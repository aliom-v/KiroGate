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
KiroGate FastAPI routes.

Contains all API endpoints:
- / and /health: Health check
- /v1/models: Model list
- /v1/chat/completions: OpenAI compatible chat completions
- /v1/messages: Anthropic compatible messages API
"""

import json
import secrets
from datetime import datetime, timezone

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request, Response, Security, Header, Form
from fastapi.responses import JSONResponse, StreamingResponse, HTMLResponse, RedirectResponse
from fastapi.security import APIKeyHeader
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from loguru import logger

from kiro_gateway.middleware import get_timestamp
from kiro_gateway.config import (
    PROXY_API_KEY,
    AVAILABLE_MODELS,
    APP_VERSION,
    RATE_LIMIT_PER_MINUTE,
)
from kiro_gateway.models import (
    OpenAIModel,
    ModelList,
    ChatCompletionRequest,
    AnthropicMessagesRequest,
)
from kiro_gateway.auth import KiroAuthManager
from kiro_gateway.auth_cache import auth_cache
from kiro_gateway.cache import ModelInfoCache
from kiro_gateway.request_handler import RequestHandler
from kiro_gateway.utils import get_kiro_headers
from kiro_gateway.config import settings
from kiro_gateway.pages import (
    render_home_page,
    render_docs_page,
    render_playground_page,
    render_deploy_page,
    render_status_page,
    render_dashboard_page,
    render_swagger_page,
)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# 预创建速率限制装饰器（避免重复创建）
_rate_limit_decorator_cache = None


def rate_limit_decorator():
    """
    Conditional rate limit decorator (cached).

    Applies rate limit when RATE_LIMIT_PER_MINUTE > 0,
    disabled when RATE_LIMIT_PER_MINUTE = 0.
    """
    global _rate_limit_decorator_cache
    if _rate_limit_decorator_cache is None:
        if RATE_LIMIT_PER_MINUTE > 0:
            _rate_limit_decorator_cache = limiter.limit(f"{RATE_LIMIT_PER_MINUTE}/minute")
        else:
            _rate_limit_decorator_cache = lambda func: func
    return _rate_limit_decorator_cache


try:
    from kiro_gateway.debug_logger import debug_logger
except ImportError:
    debug_logger = None


# --- Security scheme ---
api_key_header = APIKeyHeader(name="Authorization", auto_error=False)


def _mask_token(token: str) -> str:
    """
    Mask token for logging (show only first and last 4 chars).

    Args:
        token: Token to mask

    Returns:
        Masked token string
    """
    if len(token) <= 8:
        return "***"
    return f"{token[:4]}...{token[-4:]}"


async def _parse_auth_header(auth_header: str, request: Request = None) -> tuple[str, KiroAuthManager, int | None, int | None]:
    """
    Parse Authorization header and return proxy key, AuthManager, and optional user/key IDs.

    Supports three formats:
    1. Traditional: "Bearer {PROXY_API_KEY}" - uses global AuthManager
    2. Multi-tenant: "Bearer {PROXY_API_KEY}:{REFRESH_TOKEN}" - creates per-user AuthManager
    3. User API Key: "Bearer sk-xxx" - uses user's donated tokens

    Args:
        auth_header: Authorization header value
        request: Optional FastAPI Request for accessing app.state

    Returns:
        Tuple of (proxy_key, auth_manager, user_id, api_key_id)
        user_id and api_key_id are set when using sk-xxx format

    Raises:
        HTTPException: 401 if key is invalid or missing
    """
    if not auth_header or not auth_header.startswith("Bearer "):
        logger.warning(f"[{get_timestamp()}] 缺少或无效的 Authorization 头格式")
        raise HTTPException(status_code=401, detail="API Key 无效或缺失")

    token = auth_header[7:]  # Remove "Bearer "

    # Check if it's a user API key (sk-xxx format)
    if token.startswith("sk-"):
        from kiro_gateway.database import user_db
        from kiro_gateway.token_allocator import token_allocator, NoTokenAvailable

        result = user_db.verify_api_key(token)
        if not result:
            logger.warning(f"[{get_timestamp()}] 用户 API Key 无效: {_mask_token(token)}")
            raise HTTPException(status_code=401, detail="API Key 无效或缺失")

        user_id, api_key = result

        # Check if user is banned
        user = user_db.get_user(user_id)
        if not user or user.is_banned:
            logger.warning(f"[{get_timestamp()}] 被封禁用户尝试使用 API Key: 用户ID={user_id}")
            raise HTTPException(status_code=403, detail="用户已被封禁")

        # Get best token for this user
        try:
            donated_token, auth_manager = await token_allocator.get_best_token(user_id)
            logger.debug(f"[{get_timestamp()}] 用户 API Key 模式: 用户ID={user_id}, Token ID={donated_token.id}")

            # Store token_id in request state for usage tracking
            if request:
                request.state.donated_token_id = donated_token.id
                request.state.api_key_id = api_key.id
                request.state.user_id = user_id

            return token, auth_manager, user_id, api_key.id
        except NoTokenAvailable as e:
            logger.warning(f"[{get_timestamp()}] 用户可用 Token 不足: 用户ID={user_id}, 错误={e}")
            raise HTTPException(status_code=503, detail="该用户暂无可用的 Token")

    # Check if token contains ':' (multi-tenant format)
    if ':' in token:
        parts = token.split(':', 1)  # Split only once
        proxy_key = parts[0]
        refresh_token = parts[1]

        # Verify proxy key
        if not secrets.compare_digest(proxy_key, PROXY_API_KEY):
            logger.warning(f"[{get_timestamp()}] 多租户模式下 Proxy Key 无效: {_mask_token(proxy_key)}")
            raise HTTPException(status_code=401, detail="API Key 无效或缺失")

        # Get or create AuthManager for this refresh token
        logger.debug(f"[{get_timestamp()}] 多租户模式: 使用自定义 Refresh Token {_mask_token(refresh_token)}")
        auth_manager = await auth_cache.get_or_create(
            refresh_token=refresh_token,
            region=settings.region,
            profile_arn=settings.profile_arn
        )
        return proxy_key, auth_manager, None, None
    else:
        # Traditional mode: verify entire token as PROXY_API_KEY
        if not secrets.compare_digest(token, PROXY_API_KEY):
            logger.warning(f"[{get_timestamp()}] 传统模式下 API Key 无效")
            raise HTTPException(status_code=401, detail="API Key 无效或缺失")

        # Return None to indicate using global AuthManager
        logger.debug(f"[{get_timestamp()}] 传统模式: 使用全局 AuthManager")
        return token, None, None, None


async def verify_api_key(
    request: Request,
    auth_header: str = Security(api_key_header)
) -> KiroAuthManager:
    """
    Verify API key in Authorization header and return appropriate AuthManager.

    Supports three formats:
    1. Traditional: "Bearer {PROXY_API_KEY}" - uses global AuthManager
    2. Multi-tenant: "Bearer {PROXY_API_KEY}:{REFRESH_TOKEN}" - creates per-user AuthManager
    3. User API Key: "Bearer sk-xxx" - uses user's donated tokens

    Args:
        request: FastAPI Request for accessing app.state
        auth_header: Authorization header value

    Returns:
        KiroAuthManager instance (global or per-user)

    Raises:
        HTTPException: 401 if key is invalid or missing
    """
    proxy_key, auth_manager, user_id, api_key_id = await _parse_auth_header(auth_header, request)

    # If auth_manager is None, use global AuthManager
    if auth_manager is None:
        auth_manager = request.app.state.auth_manager

    return auth_manager


async def verify_anthropic_api_key(
    request: Request,
    x_api_key: str = Header(None, alias="x-api-key"),
    auth_header: str = Security(api_key_header)
) -> KiroAuthManager:
    """
    Verify Anthropic or OpenAI format API key and return appropriate AuthManager.

    Anthropic uses x-api-key header, but we also support
    standard Authorization: Bearer format for compatibility.

    Supports three formats:
    1. Traditional: "{PROXY_API_KEY}" - uses global AuthManager
    2. Multi-tenant: "{PROXY_API_KEY}:{REFRESH_TOKEN}" - creates per-user AuthManager
    3. User API Key: "sk-xxx" - uses user's donated tokens

    Args:
        request: FastAPI Request for accessing app.state
        x_api_key: x-api-key header value (Anthropic format)
        auth_header: Authorization header value (OpenAI format)

    Returns:
        KiroAuthManager instance (global or per-user)

    Raises:
        HTTPException: 401 if key is invalid or missing
    """
    # Try x-api-key first (Anthropic format)
    if x_api_key:
        # Check if it's a user API key (sk-xxx format)
        if x_api_key.startswith("sk-"):
            from kiro_gateway.database import user_db
            from kiro_gateway.token_allocator import token_allocator, NoTokenAvailable

            result = user_db.verify_api_key(x_api_key)
            if not result:
                logger.warning(f"[{get_timestamp()}] x-api-key 中的用户 API Key 无效: {_mask_token(x_api_key)}")
                raise HTTPException(status_code=401, detail="API Key 无效或缺失")

            user_id, api_key = result

            # Check if user is banned
            user = user_db.get_user(user_id)
            if not user or user.is_banned:
                logger.warning(f"[{get_timestamp()}] 被封禁用户尝试使用 API Key: 用户ID={user_id}")
                raise HTTPException(status_code=403, detail="用户已被封禁")

            try:
                donated_token, auth_manager = await token_allocator.get_best_token(user_id)
                logger.debug(f"[{get_timestamp()}] x-api-key 用户 API Key 模式: 用户ID={user_id}, Token ID={donated_token.id}")

                request.state.donated_token_id = donated_token.id
                request.state.api_key_id = api_key.id
                request.state.user_id = user_id

                return auth_manager
            except NoTokenAvailable as e:
                logger.warning(f"[{get_timestamp()}] 用户可用 Token 不足: 用户ID={user_id}, 错误={e}")
                raise HTTPException(status_code=503, detail="该用户暂无可用的 Token")

        # Check if x-api-key contains ':' (multi-tenant format)
        if ':' in x_api_key:
            parts = x_api_key.split(':', 1)
            proxy_key = parts[0]
            refresh_token = parts[1]

            # Verify proxy key
            if not secrets.compare_digest(proxy_key, PROXY_API_KEY):
                logger.warning(f"[{get_timestamp()}] x-api-key 多租户模式下 Proxy Key 无效: {_mask_token(proxy_key)}")
                raise HTTPException(status_code=401, detail="API Key 无效或缺失")

            # Get or create AuthManager for this refresh token
            logger.debug(f"[{get_timestamp()}] x-api-key 多租户模式: 使用自定义 Refresh Token {_mask_token(refresh_token)}")
            auth_manager = await auth_cache.get_or_create(
                refresh_token=refresh_token,
                region=settings.region,
                profile_arn=settings.profile_arn
            )
            return auth_manager
        else:
            # Traditional mode: verify entire x-api-key as PROXY_API_KEY
            if secrets.compare_digest(x_api_key, PROXY_API_KEY):
                logger.debug(f"[{get_timestamp()}] x-api-key 传统模式: 使用全局 AuthManager")
                return request.app.state.auth_manager

    # Try Authorization header (OpenAI format)
    if auth_header:
        return await verify_api_key(request, auth_header)

    logger.warning(f"[{get_timestamp()}] Anthropic 端点访问时 API Key 无效")
    raise HTTPException(status_code=401, detail="API Key 无效或缺失")


# --- Router ---
router = APIRouter()


@router.get("/", response_class=HTMLResponse, include_in_schema=False)
async def root():
    """
    Home page with dashboard.

    Returns:
        HTML home page
    """
    return HTMLResponse(content=render_home_page())


@router.get("/api", response_class=JSONResponse)
async def api_root():
    """
    API health check endpoint (JSON).

    Returns:
        Application status and version info
    """
    return {
        "status": "ok",
        "message": "Kiro API Gateway is running",
        "version": APP_VERSION
    }


@router.get("/docs", response_class=HTMLResponse, include_in_schema=False)
async def docs_page():
    """
    API documentation page.

    Returns:
        HTML documentation page
    """
    return HTMLResponse(content=render_docs_page())


@router.get("/playground", response_class=HTMLResponse, include_in_schema=False)
async def playground_page():
    """
    API playground page.

    Returns:
        HTML playground page
    """
    return HTMLResponse(content=render_playground_page())


@router.get("/deploy", response_class=HTMLResponse, include_in_schema=False)
async def deploy_page():
    """
    Deployment guide page.

    Returns:
        HTML deployment guide page
    """
    return HTMLResponse(content=render_deploy_page())


@router.get("/status", response_class=HTMLResponse, include_in_schema=False)
async def status_page(request: Request):
    """
    Status page with system health info.

    Returns:
        HTML status page
    """
    from kiro_gateway.metrics import metrics

    auth_manager: KiroAuthManager = request.app.state.auth_manager
    model_cache: ModelInfoCache = request.app.state.model_cache

    # Check if token is valid
    token_valid = False
    try:
        if auth_manager._access_token and not auth_manager.is_token_expiring_soon():
            token_valid = True
    except Exception:
        token_valid = False

    status_data = {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": APP_VERSION,
        "token_valid": token_valid,
        "cache_size": model_cache.size,
        "cache_last_update": model_cache.last_update_time
    }

    return HTMLResponse(content=render_status_page(status_data))


@router.get("/dashboard", response_class=HTMLResponse, include_in_schema=False)
async def dashboard_page():
    """
    Dashboard page with metrics and charts.

    Returns:
        HTML dashboard page
    """
    return HTMLResponse(content=render_dashboard_page())


@router.get("/swagger", response_class=HTMLResponse, include_in_schema=False)
async def swagger_page():
    """
    Swagger UI page for API documentation.

    Returns:
        HTML Swagger UI page
    """
    return HTMLResponse(content=render_swagger_page())


@router.get("/health")
async def health(request: Request):
    """
    Detailed health check.

    Returns:
        Status, timestamp, version and runtime info
    """
    from kiro_gateway.metrics import metrics

    auth_manager: KiroAuthManager = request.app.state.auth_manager
    model_cache: ModelInfoCache = request.app.state.model_cache

    # Check if token is valid
    token_valid = False
    try:
        if auth_manager._access_token and not auth_manager.is_token_expiring_soon():
            token_valid = True
    except Exception:
        token_valid = False

    # Update metrics
    metrics.set_cache_size(model_cache.size)
    metrics.set_token_valid(token_valid)

    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": APP_VERSION,
        "token_valid": token_valid,
        "cache_size": model_cache.size,
        "cache_last_update": model_cache.last_update_time
    }


@router.get("/metrics")
async def get_metrics():
    """
    Get application metrics in JSON format.

    Returns:
        Metrics data dictionary
    """
    from kiro_gateway.metrics import metrics
    return metrics.get_metrics()


@router.get("/api/metrics")
async def get_api_metrics():
    """
    Get application metrics in Deno-compatible format for dashboard.

    Returns:
        Deno-compatible metrics data dictionary
    """
    from kiro_gateway.metrics import metrics
    return metrics.get_deno_compatible_metrics()


@router.get("/metrics/prometheus")
async def get_prometheus_metrics():
    """
    Get application metrics in Prometheus format.

    Returns:
        Prometheus text format metrics
    """
    from kiro_gateway.metrics import metrics
    return Response(
        content=metrics.export_prometheus(),
        media_type="text/plain; charset=utf-8"
    )


@router.get("/v1/models", response_model=ModelList)
@rate_limit_decorator()
async def get_models(
    request: Request,
    auth_manager: KiroAuthManager = Depends(verify_api_key)
):
    """
    Return available models list.

    Uses static model list with optional dynamic updates from API.
    Results are cached to reduce API load.

    Args:
        request: FastAPI Request for accessing app.state
        auth_manager: KiroAuthManager instance (from verify_api_key)

    Returns:
        ModelList containing available models
    """
    logger.info(f"[{get_timestamp()}] 收到 /v1/models 请求")

    model_cache: ModelInfoCache = request.app.state.model_cache

    # Trigger background refresh if cache is empty or stale
    if model_cache.is_empty() or model_cache.is_stale():
        # Don't block - just trigger refresh in background
        try:
            import asyncio
            asyncio.create_task(model_cache.refresh())
        except Exception as e:
            logger.warning(f"[{get_timestamp()}] 触发模型缓存刷新失败: {e}")

    # Return static model list immediately
    openai_models = [
        OpenAIModel(
            id=model_id,
            owned_by="anthropic",
            description="Claude model via Kiro API"
        )
        for model_id in AVAILABLE_MODELS
    ]

    return ModelList(data=openai_models)


@router.post("/v1/chat/completions")
@rate_limit_decorator()
async def chat_completions(
    request: Request,
    request_data: ChatCompletionRequest,
    auth_manager: KiroAuthManager = Depends(verify_api_key)
):
    """
    Chat completions endpoint - OpenAI API compatible.

    Accepts OpenAI format requests and converts to Kiro API.
    Supports streaming and non-streaming modes.

    Args:
        request: FastAPI Request for accessing app.state
        request_data: OpenAI ChatCompletionRequest format
        auth_manager: KiroAuthManager instance (from verify_api_key)

    Returns:
        StreamingResponse for streaming mode
        JSONResponse for non-streaming mode

    Raises:
        HTTPException: On validation or API errors
    """
    logger.info(f"[{get_timestamp()}] 收到 /v1/chat/completions 请求 (模型={request_data.model}, 流式={request_data.stream})")

    # Store auth_manager and model in request state for RequestHandler and metrics
    request.state.auth_manager = auth_manager
    request.state.model = request_data.model

    return await RequestHandler.process_request(
        request,
        request_data,
        "/v1/chat/completions",
        convert_to_openai=False,
        response_format="openai"
    )


# ==================================================================================================
# Anthropic Messages API Endpoint (/v1/messages)
# ==================================================================================================

@router.post("/v1/messages")
@rate_limit_decorator()
async def anthropic_messages(
    request: Request,
    request_data: AnthropicMessagesRequest,
    auth_manager: KiroAuthManager = Depends(verify_anthropic_api_key)
):
    """
    Anthropic Messages API endpoint - Anthropic SDK compatible.

    Accepts Anthropic format requests and converts to Kiro API.
    Supports streaming and non-streaming modes.

    Args:
        request: FastAPI Request for accessing app.state
        request_data: Anthropic MessagesRequest format
        auth_manager: KiroAuthManager instance (from verify_anthropic_api_key)

    Returns:
        StreamingResponse for streaming mode
        JSONResponse for non-streaming mode

    Raises:
        HTTPException: On validation or API errors
    """
    logger.info(f"[{get_timestamp()}] 收到 /v1/messages 请求 (模型={request_data.model}, 流式={request_data.stream})")

    # Store auth_manager and model in request state for RequestHandler and metrics
    request.state.auth_manager = auth_manager
    request.state.model = request_data.model

    return await RequestHandler.process_request(
        request,
        request_data,
        "/v1/messages",
        convert_to_openai=True,
        response_format="anthropic"
    )


# --- Rate limit error handler ---
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """Handle rate limit errors."""
    return JSONResponse(
        status_code=429,
        content={
            "error": {
                "message": "Rate limit exceeded. Please try again later.",
                "type": "rate_limit_exceeded",
                "code": 429
            }
        }
    )


# ==================== Admin Routes (Hidden from Swagger) ====================

def create_admin_session() -> str:
    """Create signed admin session token."""
    from itsdangerous import URLSafeTimedSerializer
    from kiro_gateway.config import ADMIN_SECRET_KEY
    serializer = URLSafeTimedSerializer(ADMIN_SECRET_KEY)
    return serializer.dumps({"admin": True})


def verify_admin_session(token: str) -> bool:
    """Verify admin session token."""
    if not token:
        return False
    try:
        from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
        from kiro_gateway.config import ADMIN_SECRET_KEY, ADMIN_SESSION_MAX_AGE
        serializer = URLSafeTimedSerializer(ADMIN_SECRET_KEY)
        serializer.loads(token, max_age=ADMIN_SESSION_MAX_AGE)
        return True
    except Exception:
        return False


@router.get("/admin/login", response_class=HTMLResponse, include_in_schema=False)
async def admin_login_page():
    """Admin login page."""
    from kiro_gateway.pages import render_admin_login_page
    return HTMLResponse(content=render_admin_login_page())


@router.post("/admin/login", include_in_schema=False)
async def admin_login(request: Request, password: str = Form(...)):
    """Handle admin login."""
    from kiro_gateway.config import ADMIN_PASSWORD
    if password == ADMIN_PASSWORD:
        response = RedirectResponse(url="/admin", status_code=303)
        response.set_cookie(
            key="admin_session",
            value=create_admin_session(),
            httponly=True,
            max_age=86400,
            samesite="lax"
        )
        return response
    from kiro_gateway.pages import render_admin_login_page
    return HTMLResponse(content=render_admin_login_page(error="密码错误"))


@router.get("/admin/logout", include_in_schema=False)
async def admin_logout():
    """Admin logout."""
    response = RedirectResponse(url="/admin/login", status_code=303)
    response.delete_cookie(key="admin_session")
    return response


@router.get("/admin", response_class=HTMLResponse, include_in_schema=False)
async def admin_page(request: Request):
    """Admin dashboard page."""
    session = request.cookies.get("admin_session")
    if not verify_admin_session(session):
        return RedirectResponse(url="/admin/login", status_code=303)
    from kiro_gateway.pages import render_admin_page
    return HTMLResponse(content=render_admin_page())


@router.get("/admin/api/stats", include_in_schema=False)
async def admin_get_stats(request: Request):
    """Get admin statistics."""
    session = request.cookies.get("admin_session")
    if not verify_admin_session(session):
        return JSONResponse(status_code=401, content={"error": "未授权"})
    from kiro_gateway.metrics import metrics

    stats = metrics.get_admin_stats()
    # Add cached tokens count
    stats["cached_tokens"] = auth_cache.size
    # Map snake_case for frontend
    return {
        "total_requests": stats.get("totalRequests", 0),
        "success_requests": stats.get("successRequests", 0),
        "failed_requests": stats.get("failedRequests", 0),
        "active_connections": stats.get("activeConnections", 0),
        "token_valid": stats.get("tokenValid", False),
        "site_enabled": stats.get("siteEnabled", True),
        "banned_count": stats.get("bannedIPs", 0),
        "cached_tokens": stats.get("cached_tokens", 0),
        "cache_size": stats.get("cacheSize", 0),
        "avg_latency": stats.get("avgLatency", 0),
    }


@router.get("/admin/api/ip-stats", include_in_schema=False)
async def admin_get_ip_stats(request: Request):
    """Get IP statistics."""
    session = request.cookies.get("admin_session")
    if not verify_admin_session(session):
        return JSONResponse(status_code=401, content={"error": "未授权"})
    from kiro_gateway.metrics import metrics
    return metrics.get_ip_stats()


@router.get("/admin/api/blacklist", include_in_schema=False)
async def admin_get_blacklist(request: Request):
    """Get IP blacklist."""
    session = request.cookies.get("admin_session")
    if not verify_admin_session(session):
        return JSONResponse(status_code=401, content={"error": "未授权"})
    from kiro_gateway.metrics import metrics
    return metrics.get_blacklist()


@router.post("/admin/api/ban-ip", include_in_schema=False)
async def admin_ban_ip(request: Request, ip: str = Form(...), reason: str = Form("")):
    """Ban an IP address."""
    session = request.cookies.get("admin_session")
    if not verify_admin_session(session):
        return JSONResponse(status_code=401, content={"error": "未授权"})
    from kiro_gateway.metrics import metrics
    success = metrics.ban_ip(ip, reason)
    return {"success": success}


@router.post("/admin/api/unban-ip", include_in_schema=False)
async def admin_unban_ip(request: Request, ip: str = Form(...)):
    """Unban an IP address."""
    session = request.cookies.get("admin_session")
    if not verify_admin_session(session):
        return JSONResponse(status_code=401, content={"error": "未授权"})
    from kiro_gateway.metrics import metrics
    success = metrics.unban_ip(ip)
    return {"success": success}


@router.post("/admin/api/toggle-site", include_in_schema=False)
async def admin_toggle_site(request: Request, enabled: bool = Form(...)):
    """Toggle site status."""
    session = request.cookies.get("admin_session")
    if not verify_admin_session(session):
        return JSONResponse(status_code=401, content={"error": "未授权"})
    from kiro_gateway.metrics import metrics
    success = metrics.set_site_enabled(enabled)
    return {"success": success, "enabled": enabled}


@router.post("/admin/api/refresh-token", include_in_schema=False)
async def admin_refresh_token(request: Request):
    """Force refresh Kiro token."""
    session = request.cookies.get("admin_session")
    if not verify_admin_session(session):
        return JSONResponse(status_code=401, content={"error": "未授权"})
    try:
        auth_manager = getattr(request.app.state, "auth_manager", None)
        if auth_manager:
            await auth_manager.force_refresh()
            return {"success": True, "message": "Token 刷新成功"}
        return {"success": False, "message": "认证管理器不可用"}
    except Exception as e:
        logger.error(f"[{get_timestamp()}] Token 刷新失败: {e}")
        return {"success": False, "message": f"刷新失败: {str(e)}"}


@router.post("/admin/api/clear-cache", include_in_schema=False)
async def admin_clear_cache(request: Request):
    """Clear model cache."""
    session = request.cookies.get("admin_session")
    if not verify_admin_session(session):
        return JSONResponse(status_code=401, content={"error": "未授权"})
    try:
        from kiro_gateway.cache import model_cache
        await model_cache.refresh()
        return {"success": True, "message": "模型缓存已刷新"}
    except Exception as e:
        return {"success": False, "message": f"模型缓存刷新失败: {str(e)}"}


@router.get("/admin/api/tokens", include_in_schema=False)
async def admin_get_tokens(request: Request):
    """Get cached tokens list."""
    session = request.cookies.get("admin_session")
    if not verify_admin_session(session):
        return JSONResponse(status_code=401, content={"error": "未授权"})

    tokens = []
    for token, manager in auth_cache.cache.items():
        masked = f"{token[:4]}...{token[-4:]}" if len(token) > 8 else "***"
        tokens.append({
            "token_id": token[:8],  # Use first 8 chars as ID
            "masked_token": masked,
            "has_access_token": bool(manager._access_token)
        })
    return {"tokens": tokens, "count": len(tokens)}


@router.post("/admin/api/remove-token", include_in_schema=False)
async def admin_remove_token(request: Request, token_id: str = Form(...)):
    """Remove a cached token."""
    session = request.cookies.get("admin_session")
    if not verify_admin_session(session):
        return JSONResponse(status_code=401, content={"error": "未授权"})

    # Find token by ID (first 8 chars)
    for token in list(auth_cache.cache.keys()):
        if token[:8] == token_id:
            await auth_cache.remove(token)
            return {"success": True}
    return {"success": False, "message": "Token 不存在"}


@router.post("/admin/api/clear-tokens", include_in_schema=False)
async def admin_clear_tokens(request: Request):
    """Clear all cached tokens."""
    session = request.cookies.get("admin_session")
    if not verify_admin_session(session):
        return JSONResponse(status_code=401, content={"error": "未授权"})

    await auth_cache.clear()
    return {"success": True}


@router.get("/admin/api/users", include_in_schema=False)
async def admin_get_users(request: Request):
    """Get all registered users."""
    session = request.cookies.get("admin_session")
    if not verify_admin_session(session):
        return JSONResponse(status_code=401, content={"error": "未授权"})

    from kiro_gateway.database import user_db
    users = user_db.get_all_users()
    return {
        "users": [
            {
                "id": u.id,
                "linuxdo_id": u.linuxdo_id,
                "github_id": u.github_id,
                "username": u.username,
                "avatar_url": u.avatar_url,
                "trust_level": u.trust_level,
                "is_admin": u.is_admin,
                "is_banned": u.is_banned,
                "created_at": u.created_at,
                "last_login": u.last_login,
                "token_count": user_db.get_token_count(u.id)["total"],
                "api_key_count": user_db.get_api_key_count(u.id),
            }
            for u in users
        ]
    }


@router.post("/admin/api/users/ban", include_in_schema=False)
async def admin_ban_user(request: Request, user_id: int = Form(...)):
    """Ban a user."""
    session = request.cookies.get("admin_session")
    if not verify_admin_session(session):
        return JSONResponse(status_code=401, content={"error": "未授权"})

    from kiro_gateway.database import user_db
    success = user_db.set_user_banned(user_id, True)
    return {"success": success}


@router.post("/admin/api/users/unban", include_in_schema=False)
async def admin_unban_user(request: Request, user_id: int = Form(...)):
    """Unban a user."""
    session = request.cookies.get("admin_session")
    if not verify_admin_session(session):
        return JSONResponse(status_code=401, content={"error": "未授权"})

    from kiro_gateway.database import user_db
    success = user_db.set_user_banned(user_id, False)
    return {"success": success}


@router.get("/admin/api/donated-tokens", include_in_schema=False)
async def admin_get_donated_tokens(request: Request):
    """Get all donated tokens with statistics."""
    session = request.cookies.get("admin_session")
    if not verify_admin_session(session):
        return JSONResponse(status_code=401, content={"error": "未授权"})

    from kiro_gateway.database import user_db
    tokens = user_db.get_all_tokens_with_users()

    total = len(tokens)
    active = sum(1 for t in tokens if t["status"] == "active")
    public = sum(1 for t in tokens if t["visibility"] == "public")
    avg_success = sum(t["success_rate"] for t in tokens) / total if total > 0 else 0

    return {
        "total": total,
        "active": active,
        "public": public,
        "avg_success_rate": avg_success * 100,
        "tokens": tokens
    }


@router.post("/admin/api/donated-tokens/visibility", include_in_schema=False)
async def admin_toggle_token_visibility(
    request: Request,
    token_id: int = Form(...),
    visibility: str = Form(...)
):
    """Toggle token visibility."""
    session = request.cookies.get("admin_session")
    if not verify_admin_session(session):
        return JSONResponse(status_code=401, content={"error": "未授权"})

    from kiro_gateway.database import user_db
    success = user_db.set_token_visibility(token_id, visibility)
    return {"success": success}


@router.post("/admin/api/donated-tokens/delete", include_in_schema=False)
async def admin_delete_donated_token(request: Request, token_id: int = Form(...)):
    """Delete a donated token (admin override)."""
    session = request.cookies.get("admin_session")
    if not verify_admin_session(session):
        return JSONResponse(status_code=401, content={"error": "未授权"})

    from kiro_gateway.database import user_db
    success = user_db.admin_delete_token(token_id)
    return {"success": success}


# ==================== OAuth2 Routes (Hidden from Swagger) ====================

@router.get("/oauth2/login", include_in_schema=False)
async def oauth2_login():
    """Redirect to LinuxDo OAuth2 authorization."""
    from kiro_gateway.user_manager import user_manager

    if not user_manager.oauth.is_configured:
        return HTMLResponse(
            content="<h1>OAuth2 未配置</h1><p>请在 .env 中配置 OAUTH_CLIENT_ID 和 OAUTH_CLIENT_SECRET</p>",
            status_code=500
        )

    state = user_manager.session.create_oauth_state()
    auth_url = user_manager.oauth.get_authorization_url(state)

    response = RedirectResponse(url=auth_url, status_code=302)
    response.set_cookie(
        key="oauth_state",
        value=state,
        httponly=True,
        max_age=600,  # 10 minutes
        samesite="lax"
    )
    return response


@router.get("/oauth2/callback", include_in_schema=False)
async def oauth2_callback(request: Request, code: str = None, state: str = None):
    """Handle OAuth2 callback from LinuxDo."""
    from kiro_gateway.user_manager import user_manager

    # Verify state
    cookie_state = request.cookies.get("oauth_state")
    if not state or state != cookie_state:
        return HTMLResponse(content="<h1>错误</h1><p>无效的 state 参数</p>", status_code=400)

    if not code:
        return HTMLResponse(content="<h1>错误</h1><p>未收到授权码</p>", status_code=400)

    # Complete OAuth2 flow
    user, result = await user_manager.oauth_login(code)

    if not user:
        error_msg = result or "登录失败"
        return HTMLResponse(content=f"<h1>错误</h1><p>{error_msg}</p>", status_code=400)

    # Create session and redirect
    response = RedirectResponse(url="/user", status_code=303)
    response.set_cookie(
        key="user_session",
        value=result,  # session_token
        httponly=True,
        max_age=settings.user_session_max_age,
        samesite="lax"
    )
    response.delete_cookie(key="oauth_state")
    return response


@router.get("/oauth2/logout", include_in_schema=False)
async def oauth2_logout():
    """User logout."""
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie(key="user_session")
    return response


# ==================== GitHub OAuth2 Routes ====================

@router.get("/login", response_class=HTMLResponse, include_in_schema=False)
async def login_page():
    """Login selection page with multiple OAuth2 providers."""
    from kiro_gateway.pages import render_login_page
    return HTMLResponse(content=render_login_page())


@router.get("/oauth2/github/login", include_in_schema=False)
async def github_oauth2_login():
    """Redirect to GitHub OAuth2 authorization."""
    from kiro_gateway.user_manager import user_manager

    if not user_manager.github.is_configured:
        return HTMLResponse(
            content="<h1>GitHub OAuth2 未配置</h1><p>请在 .env 中配置 GITHUB_CLIENT_ID 和 GITHUB_CLIENT_SECRET</p>",
            status_code=500
        )

    state = user_manager.session.create_oauth_state()
    auth_url = user_manager.github.get_authorization_url(state)

    response = RedirectResponse(url=auth_url, status_code=302)
    response.set_cookie(
        key="github_oauth_state",
        value=state,
        httponly=True,
        max_age=600,  # 10 minutes
        samesite="lax"
    )
    return response


@router.get("/oauth2/github/callback", include_in_schema=False)
async def github_oauth2_callback(request: Request, code: str = None, state: str = None):
    """Handle OAuth2 callback from GitHub."""
    from kiro_gateway.user_manager import user_manager

    # Verify state
    cookie_state = request.cookies.get("github_oauth_state")
    if not state or state != cookie_state:
        return HTMLResponse(content="<h1>错误</h1><p>无效的 state 参数</p>", status_code=400)

    if not code:
        return HTMLResponse(content="<h1>错误</h1><p>未收到授权码</p>", status_code=400)

    # Complete GitHub OAuth2 flow
    user, result = await user_manager.github_login(code)

    if not user:
        error_msg = result or "登录失败"
        return HTMLResponse(content=f"<h1>错误</h1><p>{error_msg}</p>", status_code=400)

    # Create session and redirect
    response = RedirectResponse(url="/user", status_code=303)
    response.set_cookie(
        key="user_session",
        value=result,  # session_token
        httponly=True,
        max_age=settings.user_session_max_age,
        samesite="lax"
    )
    response.delete_cookie(key="github_oauth_state")
    return response


# ==================== User Routes (Hidden from Swagger) ====================

def get_current_user(request: Request):
    """Get current logged-in user from session."""
    from kiro_gateway.user_manager import user_manager
    session_token = request.cookies.get("user_session")
    return user_manager.get_current_user(session_token) if session_token else None


@router.get("/user", response_class=HTMLResponse, include_in_schema=False)
async def user_page(request: Request):
    """User dashboard page."""
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    from kiro_gateway.pages import render_user_page
    return HTMLResponse(content=render_user_page(user))


@router.get("/user/api/profile", include_in_schema=False)
async def user_get_profile(request: Request):
    """Get current user profile."""
    user = get_current_user(request)
    if not user:
        return JSONResponse(status_code=401, content={"error": "未登录"})
    from kiro_gateway.database import user_db
    token_counts = user_db.get_token_count(user.id)
    api_key_count = user_db.get_api_key_count(user.id)
    return {
        "id": user.id,
        "username": user.username,
        "avatar_url": user.avatar_url,
        "trust_level": user.trust_level,
        "is_admin": user.is_admin,
        "token_count": token_counts["total"],
        "public_token_count": token_counts["public"],
        "api_key_count": api_key_count,
    }


@router.get("/user/api/tokens", include_in_schema=False)
async def user_get_tokens(request: Request):
    """Get user's tokens."""
    user = get_current_user(request)
    if not user:
        return JSONResponse(status_code=401, content={"error": "未登录"})
    from kiro_gateway.database import user_db
    tokens = user_db.get_user_tokens(user.id)
    return {
        "tokens": [
            {
                "id": t.id,
                "visibility": t.visibility,
                "status": t.status,
                "success_count": t.success_count,
                "fail_count": t.fail_count,
                "success_rate": round(t.success_rate * 100, 1),
                "last_used": t.last_used,
                "created_at": t.created_at,
            }
            for t in tokens
        ]
    }


@router.get("/user/api/public-tokens", include_in_schema=False)
async def user_get_public_tokens(request: Request):
    """Get public tokens with contributor info for user page."""
    user = get_current_user(request)
    if not user:
        return JSONResponse(status_code=401, content={"error": "未登录"})
    from kiro_gateway.database import user_db
    tokens = user_db.get_public_tokens_with_users()
    avg_rate = sum(t["success_rate"] for t in tokens) / len(tokens) if tokens else 0
    return {
        "tokens": [
            {
                "id": t["id"],
                "username": t["username"],
                "status": t["status"],
                "success_rate": round(t["success_rate"] * 100, 1),
                "use_count": t["success_count"] + t["fail_count"],
                "last_used": t["last_used"],
            }
            for t in tokens
        ],
        "count": len(tokens),
        "avg_success_rate": round(avg_rate * 100, 1),
    }


@router.post("/user/api/tokens", include_in_schema=False)
async def user_donate_token(
    request: Request,
    refresh_token: str = Form(...),
    visibility: str = Form("private")
):
    """Donate a new token."""
    user = get_current_user(request)
    if not user:
        return JSONResponse(status_code=401, content={"error": "未登录"})

    if visibility not in ("public", "private"):
        return JSONResponse(status_code=400, content={"error": "可见性无效"})

    from kiro_gateway.database import user_db

    # Validate token before saving
    from kiro_gateway.auth import KiroAuthManager
    from kiro_gateway.config import settings as cfg
    try:
        temp_manager = KiroAuthManager(
            refresh_token=refresh_token,
            region=cfg.region,
            profile_arn=cfg.profile_arn
        )
        access_token = await temp_manager.get_access_token()
        if not access_token:
            return {"success": False, "message": "Token 验证失败：无法获取访问令牌"}
    except Exception as e:
        return {"success": False, "message": f"Token 验证失败：{str(e)}"}

    # Save token
    success, message = user_db.donate_token(user.id, refresh_token, visibility)
    return {"success": success, "message": message}


@router.put("/user/api/tokens/{token_id}", include_in_schema=False)
async def user_update_token(
    request: Request,
    token_id: int,
    visibility: str = Form(...)
):
    """Update token visibility."""
    user = get_current_user(request)
    if not user:
        return JSONResponse(status_code=401, content={"error": "未登录"})

    from kiro_gateway.database import user_db

    # Verify ownership
    token = user_db.get_token_by_id(token_id)
    if not token or token.user_id != user.id:
        return JSONResponse(status_code=404, content={"error": "Token 不存在"})

    success = user_db.set_token_visibility(token_id, visibility)
    return {"success": success}


@router.delete("/user/api/tokens/{token_id}", include_in_schema=False)
async def user_delete_token(request: Request, token_id: int):
    """Delete a token."""
    user = get_current_user(request)
    if not user:
        return JSONResponse(status_code=401, content={"error": "未登录"})

    from kiro_gateway.database import user_db
    success = user_db.delete_token(token_id, user.id)
    return {"success": success}


@router.get("/user/api/keys", include_in_schema=False)
async def user_get_keys(request: Request):
    """Get user's API keys."""
    user = get_current_user(request)
    if not user:
        return JSONResponse(status_code=401, content={"error": "未登录"})
    from kiro_gateway.database import user_db
    keys = user_db.get_user_api_keys(user.id)
    return {
        "keys": [
            {
                "id": k.id,
                "key_prefix": k.key_prefix,
                "name": k.name,
                "is_active": k.is_active,
                "request_count": k.request_count,
                "last_used": k.last_used,
                "created_at": k.created_at,
            }
            for k in keys
        ]
    }


@router.post("/user/api/keys", include_in_schema=False)
async def user_create_key(request: Request, name: str = Form("")):
    """Generate a new API key."""
    user = get_current_user(request)
    if not user:
        return JSONResponse(status_code=401, content={"error": "未登录"})

    from kiro_gateway.database import user_db

    # Check if user has any tokens (for info purposes only, not blocking)
    tokens = user_db.get_user_tokens(user.id)
    active_tokens = [t for t in tokens if t.status == "active"]
    has_own_tokens = len(active_tokens) > 0

    plain_key, api_key = user_db.generate_api_key(user.id, name or None)
    return {
        "success": True,
        "key": plain_key,  # Only returned once!
        "key_prefix": api_key.key_prefix,
        "id": api_key.id,
        "uses_public_pool": not has_own_tokens,
    }


@router.delete("/user/api/keys/{key_id}", include_in_schema=False)
async def user_delete_key(request: Request, key_id: int):
    """Delete an API key."""
    user = get_current_user(request)
    if not user:
        return JSONResponse(status_code=401, content={"error": "未登录"})

    from kiro_gateway.database import user_db
    success = user_db.delete_api_key(key_id, user.id)
    return {"success": success}


# ==================== Public Token Pool ====================

@router.get("/tokens", response_class=HTMLResponse, include_in_schema=False)
async def public_tokens_page(request: Request):
    """Public token pool page."""
    from kiro_gateway.pages import render_tokens_page
    user = get_current_user(request)
    return HTMLResponse(content=render_tokens_page(user))


@router.get("/api/public-tokens", include_in_schema=False)
async def get_public_tokens():
    """Get public tokens list (masked)."""
    from kiro_gateway.database import user_db
    tokens = user_db.get_public_tokens()
    return {
        "tokens": [
            {
                "id": t.id,
                "success_rate": round(t.success_rate * 100, 1),
                "last_used": t.last_used,
            }
            for t in tokens
        ],
        "count": len(tokens)
    }
