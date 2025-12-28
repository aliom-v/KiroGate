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
HTTP 客户端管理器。

全局 HTTP 客户端连接池管理，提高性能。
支持自适应超时，针对慢模型（如 Opus）自动调整。
"""

import asyncio
from typing import Optional

import httpx
from fastapi import HTTPException
from loguru import logger

from kiro_gateway.auth import KiroAuthManager
from kiro_gateway.config import settings, get_adaptive_timeout
from kiro_gateway.utils import get_kiro_headers


class GlobalHTTPClientManager:
    """
    Global HTTP client manager.

    Maintains a global connection pool to avoid creating new clients for each request.
    Timeout is configured per-request, not at client level.
    """

    def __init__(self):
        """Initialize global client manager."""
        self._client: Optional[httpx.AsyncClient] = None
        self._lock = asyncio.Lock()

    async def get_client(self) -> httpx.AsyncClient:
        """
        Get or create HTTP client.

        Note: Timeout should be set per-request, not here, since the client is reused.

        Returns:
            HTTP client instance
        """
        async with self._lock:
            if self._client is None or self._client.is_closed:
                limits = httpx.Limits(
                    max_connections=100,
                    max_keepalive_connections=20,
                    keepalive_expiry=60.0  # Increased from 30.0 for long-running connections
                )

                self._client = httpx.AsyncClient(
                    timeout=None,  # Timeout set per-request
                    follow_redirects=True,
                    limits=limits,
                    http2=False
                )
                logger.debug("Created new global HTTP client with connection pool")

            return self._client

    async def close(self) -> None:
        """Close global HTTP client."""
        async with self._lock:
            if self._client and not self._client.is_closed:
                await self._client.aclose()
                logger.debug("Closed global HTTP client")


# Global manager instance
global_http_client_manager = GlobalHTTPClientManager()


class KiroHttpClient:
    """
    Kiro API HTTP client with retry logic.

    Uses global connection pool for better performance.
    Automatically handles various error types:
    - 403: Auto-refresh token and retry
    - 429: Exponential backoff retry
    - 5xx: Exponential backoff retry
    - Timeout: Exponential backoff retry
    """

    def __init__(self, auth_manager: KiroAuthManager):
        """
        Initialize HTTP client.

        Args:
            auth_manager: Authentication manager
        """
        self.auth_manager = auth_manager
        self.client = None  # Will use global client

    async def _get_client(self) -> httpx.AsyncClient:
        """
        Get HTTP client (uses global connection pool).

        Returns:
            HTTP client instance
        """
        return await global_http_client_manager.get_client()

    async def close(self) -> None:
        """
        Close client (does not actually close global client).

        Kept for backward compatibility.
        """
        pass

    async def request_with_retry(
        self,
        method: str,
        url: str,
        json_data: dict,
        stream: bool = False,
        first_token_timeout: float = None,
        model: str = None
    ) -> httpx.Response:
        """
        Execute HTTP request with retry logic.

        Automatically handles various error types:
        - 403: Refresh token and retry
        - 429: Exponential backoff retry
        - 5xx: Exponential backoff retry
        - Timeout: Exponential backoff retry

        Args:
            method: HTTP method
            url: Request URL
            json_data: JSON request body
            stream: Whether to use streaming response
            first_token_timeout: First token timeout (streaming only)
            model: Model name (for adaptive timeout)

        Returns:
            HTTP response

        Raises:
            HTTPException: After retry failure
        """
        # 从 json_data 中提取模型名称（如果未提供）
        if model is None:
            model = json_data.get("modelId", "") if json_data else ""

        if stream:
            # 流式请求：使用较长的连接超时，实际读取超时在 streaming.py 中控制
            base_timeout = first_token_timeout or settings.first_token_timeout
            timeout = get_adaptive_timeout(model, base_timeout)
            max_retries = settings.first_token_max_retries
        else:
            # 非流式请求：使用配置的超时时间（默认 600 秒）
            base_timeout = settings.non_stream_timeout
            timeout = get_adaptive_timeout(model, base_timeout)
            max_retries = settings.max_retries

        client = await self._get_client()
        last_error = None

        for attempt in range(max_retries):
            try:
                token = await self.auth_manager.get_access_token()
                headers = self._get_headers(token)

                # Set timeout per-request
                request_timeout = httpx.Timeout(timeout)

                if stream:
                    req = client.build_request(
                        method, url, json=json_data, headers=headers, timeout=request_timeout
                    )
                    response = await client.send(req, stream=True)
                else:
                    response = await client.request(
                        method, url, json=json_data, headers=headers, timeout=request_timeout
                    )

                if response.status_code == 200:
                    return response

                # 403 - Token expired, refresh and retry
                if response.status_code == 403:
                    logger.warning(f"Received 403, refreshing token (attempt {attempt + 1}/{max_retries})")
                    await self.auth_manager.force_refresh()
                    continue

                # 429 - Rate limited, wait and retry
                if response.status_code == 429:
                    delay = settings.base_retry_delay * (2 ** attempt)
                    logger.warning(f"Received 429, waiting {delay}s (attempt {attempt + 1}/{max_retries})")
                    await asyncio.sleep(delay)
                    continue

                # 5xx - Server error, wait and retry
                if 500 <= response.status_code < 600:
                    delay = settings.base_retry_delay * (2 ** attempt)
                    logger.warning(f"Received {response.status_code}, waiting {delay}s (attempt {attempt + 1}/{max_retries})")
                    await asyncio.sleep(delay)
                    continue

                # Other errors, return directly
                return response

            except httpx.TimeoutException as e:
                last_error = e
                if stream:
                    logger.warning(f"First token timeout after {timeout}s for model {model} (attempt {attempt + 1}/{max_retries})")
                else:
                    delay = settings.base_retry_delay * (2 ** attempt)
                    logger.warning(f"Timeout after {timeout}s for model {model}, waiting {delay}s (attempt {attempt + 1}/{max_retries})")
                    await asyncio.sleep(delay)

            except httpx.RequestError as e:
                last_error = e
                delay = settings.base_retry_delay * (2 ** attempt)
                logger.warning(f"Request error: {e}, waiting {delay}s (attempt {attempt + 1}/{max_retries})")
                await asyncio.sleep(delay)

        # All retries failed
        if stream:
            raise HTTPException(
                status_code=504,
                detail=f"模型在 {max_retries} 次尝试后仍未在 {timeout}s 内响应，请稍后再试。"
            )
        else:
            raise HTTPException(
                status_code=502,
                detail=f"在 {max_retries} 次尝试后仍未完成请求: {last_error}"
            )

    def _get_headers(self, token: str) -> dict:
        """
        Build request headers.

        Args:
            token: Access token

        Returns:
            Headers dictionary
        """
        return get_kiro_headers(self.auth_manager, token)

    async def __aenter__(self) -> "KiroHttpClient":
        """Support async context manager."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit context without closing global client."""
        pass


async def close_global_http_client():
    """Close global HTTP client (called on app shutdown)."""
    await global_http_client_manager.close()
