# -*- coding: utf-8 -*-

# KiroGate
# Based on kiro-openai-gateway by Jwadow (https://github.com/Jwadow/kiro-openai-gateway)
# Original Copyright (C) 2025 Jwadow
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

"""
Request tracking middleware.

Adds unique ID to each request for log correlation and debugging.
"""

import time
import uuid
from datetime import datetime
from typing import Callable, Optional

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from loguru import logger


def get_timestamp() -> str:
    """获取格式化的时间戳。"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_user_info(request: Request) -> str:
    """从请求中提取用户信息。"""
    try:
        if hasattr(request.state, "username"):
            return request.state.username
        if hasattr(request.state, "api_key_id"):
            return f"API Key #{request.state.api_key_id}"
        if hasattr(request.state, "donated_token_id"):
            return f"Token #{request.state.donated_token_id}"
    except Exception:
        pass
    return "匿名"


def get_client_ip(request: Request) -> str:
    """Extract client IP from request, supporting X-Forwarded-For."""
    x_forwarded_for = request.headers.get("X-Forwarded-For")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


class RequestTrackingMiddleware(BaseHTTPMiddleware):
    """
    Request tracking middleware.

    For each request:
    - Generates unique request ID
    - Records request start and end time
    - Calculates request processing time
    - Adds request ID context to logs
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request and add tracking info.

        Args:
            request: HTTP request
            call_next: Next middleware or route handler

        Returns:
            HTTP response
        """
        # Get from header or generate new request ID
        request_id = request.headers.get("X-Request-ID")
        if not request_id:
            request_id = str(uuid.uuid4())

        # Record request start time
        start_time = time.time()

        # Add request ID to request state
        request.state.request_id = request_id

        # Use loguru context to bind request ID
        with logger.contextualize(request_id=request_id):
            client_ip = get_client_ip(request)
            logger.info(
                f"[{get_timestamp()}] [IP: {client_ip}] 请求开始: {request.method} {request.url.path}"
                + (f" 参数: {request.url.query}" if request.url.query else "")
            )

            try:
                response = await call_next(request)

                # Calculate processing time
                process_time = time.time() - start_time
                user_info = get_user_info(request)

                # Add response headers
                response.headers["X-Request-ID"] = request_id
                response.headers["X-Process-Time"] = str(round(process_time, 4))

                status_text = "成功" if 200 <= response.status_code < 400 else "失败"
                logger.info(
                    f"[{get_timestamp()}] [用户: {user_info}] [IP: {client_ip}] "
                    f"请求{status_text}: {request.method} {request.url.path} "
                    f"状态码={response.status_code} 耗时={process_time:.4f}秒"
                )

                return response

            except Exception as e:
                process_time = time.time() - start_time
                user_info = get_user_info(request)
                logger.error(
                    f"[{get_timestamp()}] [用户: {user_info}] [IP: {client_ip}] "
                    f"请求异常: {request.method} {request.url.path} "
                    f"错误={str(e)} 耗时={process_time:.4f}秒"
                )
                raise


class MetricsMiddleware(BaseHTTPMiddleware):
    """
    Metrics collection middleware.

    Collects basic request metrics and sends to Prometheus collector:
    - Total request count (by endpoint, status code, model)
    - Response time
    - Active connection count
    - API Key and Token usage tracking
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Collect request metrics.

        Args:
            request: HTTP request
            call_next: Next middleware or route handler

        Returns:
            HTTP response
        """
        from kiro_gateway.metrics import metrics

        start_time = time.time()
        endpoint = request.url.path
        model = "unknown"

        # Record client IP
        metrics.record_ip(get_client_ip(request))

        # Increment active connections
        metrics.inc_active_connections()

        try:
            response = await call_next(request)

            # Calculate processing time
            process_time = time.time() - start_time

            # Try to get model name from request state
            if hasattr(request.state, "model"):
                model = request.state.model

            # Record metrics
            metrics.inc_request(endpoint, response.status_code, model)
            metrics.observe_latency(endpoint, process_time)

            # Track API key and token usage for sk-xxx keys
            is_success = 200 <= response.status_code < 400
            self._track_token_usage(request, is_success)

            return response

        except Exception as e:
            process_time = time.time() - start_time
            metrics.inc_request(endpoint, 500, model)
            metrics.inc_error(type(e).__name__)
            metrics.observe_latency(endpoint, process_time)

            # Track failed request
            self._track_token_usage(request, success=False)
            raise

        finally:
            # Decrement active connections
            metrics.dec_active_connections()

    def _track_token_usage(self, request: Request, success: bool) -> None:
        """Track usage for sk-xxx API keys."""
        try:
            # Check if request used a user API key
            if hasattr(request.state, "donated_token_id"):
                from kiro_gateway.database import user_db
                from kiro_gateway.token_allocator import token_allocator

                token_id = request.state.donated_token_id
                api_key_id = getattr(request.state, "api_key_id", None)

                # Record token usage
                token_allocator.record_usage(token_id, success)

                # Record API key usage
                if api_key_id:
                    user_db.record_api_key_usage(api_key_id)

        except Exception as e:
            logger.debug(f"[{get_timestamp()}] Token 使用追踪失败: {e}")


class SiteGuardMiddleware(BaseHTTPMiddleware):
    """Check site status and IP blacklist."""

    MAINTENANCE_HTML = '''<!DOCTYPE html>
<html lang="zh">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>维护中 - KiroGate</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
      font-family: system-ui, -apple-system, sans-serif;
      color: #e2e8f0;
    }
    .container {
      text-align: center;
      padding: 2rem;
      max-width: 500px;
    }
    .icon { font-size: 5rem; margin-bottom: 1.5rem; }
    h1 { font-size: 2rem; margin-bottom: 1rem; color: #f59e0b; }
    p { color: #94a3b8; line-height: 1.6; margin-bottom: 1.5rem; }
    .status {
      display: inline-block;
      padding: 0.5rem 1rem;
      background: rgba(245, 158, 11, 0.2);
      border: 1px solid #f59e0b;
      border-radius: 9999px;
      font-size: 0.875rem;
      color: #f59e0b;
    }
  </style>
</head>
<body>
  <div class="container">
    <div class="icon">🔧</div>
    <h1>服务维护中</h1>
    <p>KiroGate 服务正在进行维护，请稍后再试。<br>给您带来的不便，敬请谅解。</p>
    <div class="status">预计很快恢复</div>
  </div>
</body>
</html>'''

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Check site status and IP blacklist.

        Args:
            request: HTTP request
            call_next: Next middleware or route handler

        Returns:
            HTTP response
        """
        from kiro_gateway.metrics import metrics
        from starlette.responses import HTMLResponse

        path = request.url.path

        # Allow admin, auth and static routes
        exempt_prefixes = ("/admin", "/login", "/oauth", "/user", "/static", "/docs", "/openapi.json")
        if any(path.startswith(p) for p in exempt_prefixes):
            return await call_next(request)

        # Check site status
        if not metrics.is_site_enabled():
            # Check if API request
            accept = request.headers.get("accept", "")
            is_api = (
                request.url.path.startswith("/v1/") or
                request.url.path.startswith("/api/") or
                "application/json" in accept
            )
            if is_api:
                return JSONResponse(
                    status_code=503,
                    content={"error": "Service temporarily unavailable"}
                )
            # Return HTML maintenance page
            return HTMLResponse(
                content=self.MAINTENANCE_HTML,
                status_code=503
            )

        # Check IP blacklist
        client_ip = get_client_ip(request)
        if metrics.is_ip_banned(client_ip):
            return JSONResponse(
                status_code=403,
                content={"error": "Access denied"}
            )

        return await call_next(request)


# Global metrics middleware instance
metrics_middleware = MetricsMiddleware