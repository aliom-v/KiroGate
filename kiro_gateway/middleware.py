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
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from loguru import logger


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
            logger.info(
                f"Request started: {request.method} {request.url.path} "
                f"(query: {request.url.query})"
            )

            try:
                response = await call_next(request)

                # Calculate processing time
                process_time = time.time() - start_time

                # Add response headers
                response.headers["X-Request-ID"] = request_id
                response.headers["X-Process-Time"] = str(round(process_time, 4))

                logger.info(
                    f"Request completed: {request.method} {request.url.path} "
                    f"status={response.status_code} time={process_time:.4f}s"
                )

                return response

            except Exception as e:
                process_time = time.time() - start_time
                logger.error(
                    f"Request failed: {request.method} {request.url.path} "
                    f"error={str(e)} time={process_time:.4f}s"
                )
                raise


class MetricsMiddleware(BaseHTTPMiddleware):
    """
    Metrics collection middleware.

    Collects basic request metrics and sends to Prometheus collector:
    - Total request count (by endpoint, status code, model)
    - Response time
    - Active connection count
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

            return response

        except Exception as e:
            process_time = time.time() - start_time
            metrics.inc_request(endpoint, 500, model)
            metrics.inc_error(type(e).__name__)
            metrics.observe_latency(endpoint, process_time)
            raise

        finally:
            # Decrement active connections
            metrics.dec_active_connections()


# Global metrics middleware instance
metrics_middleware = MetricsMiddleware