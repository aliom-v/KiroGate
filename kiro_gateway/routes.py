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
from fastapi import APIRouter, Depends, HTTPException, Request, Response, Security, Header
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.security import APIKeyHeader
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from loguru import logger

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
from kiro_gateway.cache import ModelInfoCache
from kiro_gateway.request_handler import RequestHandler
from kiro_gateway.utils import get_kiro_headers

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


async def verify_api_key(auth_header: str = Security(api_key_header)) -> bool:
    """
    Verify API key in Authorization header.

    Expected format: "Bearer {PROXY_API_KEY}"

    Args:
        auth_header: Authorization header value

    Returns:
        True if key is valid

    Raises:
        HTTPException: 401 if key is invalid or missing
    """
    if not auth_header or not secrets.compare_digest(auth_header, f"Bearer {PROXY_API_KEY}"):
        logger.warning("Access attempt with invalid API key.")
        raise HTTPException(status_code=401, detail="Invalid or missing API Key")
    return True


async def verify_anthropic_api_key(
    x_api_key: str = Header(None, alias="x-api-key"),
    auth_header: str = Security(api_key_header)
) -> bool:
    """
    Verify Anthropic or OpenAI format API key.

    Anthropic uses x-api-key header, but we also support
    standard Authorization: Bearer format for compatibility.

    Args:
        x_api_key: x-api-key header value (Anthropic format)
        auth_header: Authorization header value (OpenAI format)

    Returns:
        True if key is valid

    Raises:
        HTTPException: 401 if key is invalid or missing
    """
    # Check x-api-key (Anthropic format)
    if x_api_key and secrets.compare_digest(x_api_key, PROXY_API_KEY):
        return True

    # Check Authorization: Bearer (OpenAI format)
    if auth_header and secrets.compare_digest(auth_header, f"Bearer {PROXY_API_KEY}"):
        return True

    logger.warning("Access attempt with invalid API key (Anthropic endpoint).")
    raise HTTPException(status_code=401, detail="Invalid or missing API Key")


# --- Router ---
router = APIRouter()


@router.get("/")
async def root():
    """
    Health check endpoint.

    Returns:
        Application status and version info
    """
    return {
        "status": "ok",
        "message": "Kiro API Gateway is running",
        "version": APP_VERSION
    }


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


@router.get("/v1/models", response_model=ModelList, dependencies=[Depends(verify_api_key)])
@rate_limit_decorator()
async def get_models(request: Request):
    """
    Return available models list.

    Uses static model list with optional dynamic updates from API.
    Results are cached to reduce API load.

    Args:
        request: FastAPI Request for accessing app.state

    Returns:
        ModelList containing available models
    """
    logger.info("Request to /v1/models")

    model_cache: ModelInfoCache = request.app.state.model_cache

    # Trigger background refresh if cache is empty or stale
    if model_cache.is_empty() or model_cache.is_stale():
        # Don't block - just trigger refresh in background
        try:
            import asyncio
            asyncio.create_task(model_cache.refresh())
        except Exception as e:
            logger.warning(f"Failed to trigger model cache refresh: {e}")

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


@router.post("/v1/chat/completions", dependencies=[Depends(verify_api_key)])
@rate_limit_decorator()
async def chat_completions(request: Request, request_data: ChatCompletionRequest):
    """
    Chat completions endpoint - OpenAI API compatible.

    Accepts OpenAI format requests and converts to Kiro API.
    Supports streaming and non-streaming modes.

    Args:
        request: FastAPI Request for accessing app.state
        request_data: OpenAI ChatCompletionRequest format

    Returns:
        StreamingResponse for streaming mode
        JSONResponse for non-streaming mode

    Raises:
        HTTPException: On validation or API errors
    """
    logger.info(f"Request to /v1/chat/completions (model={request_data.model}, stream={request_data.stream})")

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

@router.post("/v1/messages", dependencies=[Depends(verify_anthropic_api_key)])
@rate_limit_decorator()
async def anthropic_messages(request: Request, request_data: AnthropicMessagesRequest):
    """
    Anthropic Messages API endpoint - Anthropic SDK compatible.

    Accepts Anthropic format requests and converts to Kiro API.
    Supports streaming and non-streaming modes.

    Args:
        request: FastAPI Request for accessing app.state
        request_data: Anthropic MessagesRequest format

    Returns:
        StreamingResponse for streaming mode
        JSONResponse for non-streaming mode

    Raises:
        HTTPException: On validation or API errors
    """
    logger.info(f"Request to /v1/messages (model={request_data.model}, stream={request_data.stream})")

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