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
Model metadata cache.

Thread-safe storage with TTL, lazy loading and background refresh.
"""

import asyncio
import time
from typing import Any, Dict, List, Optional

import httpx
from loguru import logger

from kiro_gateway.config import MODEL_CACHE_TTL, DEFAULT_MAX_INPUT_TOKENS
from kiro_gateway.http_client import global_http_client_manager


class ModelInfoCache:
    """
    Thread-safe model metadata cache.

    Uses lazy loading - data is loaded only on first access or when cache expires.
    Supports background auto-refresh mechanism.
    """

    def __init__(self, cache_ttl: int = MODEL_CACHE_TTL):
        """
        Initialize model cache.

        Args:
            cache_ttl: Cache TTL in seconds (default from config)
        """
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._lock = asyncio.Lock()
        self._last_update: Optional[float] = None
        self._cache_ttl = cache_ttl
        self._refresh_task: Optional[asyncio.Task] = None
        self._auth_manager = None

    def set_auth_manager(self, auth_manager) -> None:
        """
        Set authentication manager (for background refresh).

        Args:
            auth_manager: Authentication manager instance
        """
        self._auth_manager = auth_manager

    async def update(self, models_data: List[Dict[str, Any]]) -> None:
        """
        Update model cache.

        Thread-safely replaces cache content with new data.

        Args:
            models_data: List of model info dictionaries.
                        Each dict should contain "modelId" key.
        """
        async with self._lock:
            logger.info(f"Updating model cache. Found {len(models_data)} models.")
            self._cache = {model["modelId"]: model for model in models_data}
            self._last_update = time.time()

    async def refresh(self) -> bool:
        """
        Refresh cache from API using global connection pool.

        Returns:
            True if refresh succeeded, False otherwise
        """
        if not self._auth_manager:
            logger.warning("No auth manager set, cannot refresh cache")
            return False

        try:
            token = await self._auth_manager.get_access_token()
            from kiro_gateway.utils import get_kiro_headers
            headers = get_kiro_headers(self._auth_manager, token)

            # Use global connection pool instead of creating new client
            client = await global_http_client_manager.get_client()
            response = await client.get(
                f"{self._auth_manager.q_host}/ListAvailableModels",
                headers=headers,
                params={
                    "origin": "AI_EDITOR",
                    "profileArn": self._auth_manager.profile_arn or ""
                },
                timeout=30.0
            )

            if response.status_code == 200:
                data = response.json()
                models_list = data.get("models", [])
                await self.update(models_list)
                logger.info(f"Successfully refreshed model cache with {len(models_list)} models")
                return True
            else:
                logger.error(f"Failed to refresh models: HTTP {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"Error refreshing model cache: {e}")
            return False

    async def start_background_refresh(self) -> None:
        """
        Start background refresh task.

        Creates a background task that periodically refreshes the cache.
        """
        if self._refresh_task and not self._refresh_task.done():
            logger.warning("Background refresh task is already running")
            return

        self._refresh_task = asyncio.create_task(self._background_refresh_loop())
        logger.info("Started background model cache refresh task")

    async def stop_background_refresh(self) -> None:
        """Stop background refresh task."""
        if self._refresh_task and not self._refresh_task.done():
            self._refresh_task.cancel()
            try:
                await self._refresh_task
            except asyncio.CancelledError:
                logger.info("Stopped background model cache refresh task")
            except Exception as e:
                logger.error(f"Error stopping refresh task: {e}")

    async def _background_refresh_loop(self) -> None:
        """
        Background refresh loop.

        Periodically refreshes cache at half the TTL interval.
        """
        refresh_interval = self._cache_ttl / 2
        logger.info(f"Background refresh will run every {refresh_interval} seconds")

        while True:
            try:
                await asyncio.sleep(refresh_interval)
                logger.debug("Running scheduled model cache refresh")
                await self.refresh()
            except asyncio.CancelledError:
                logger.info("Background refresh task cancelled")
                break
            except Exception as e:
                logger.error(f"Unexpected error in background refresh: {e}")

    def get(self, model_id: str) -> Optional[Dict[str, Any]]:
        """
        Get model info.

        Args:
            model_id: Model ID

        Returns:
            Model info dict, or None if not found
        """
        return self._cache.get(model_id)

    def get_max_input_tokens(self, model_id: str) -> int:
        """
        Get model's maxInputTokens.

        Args:
            model_id: Model ID

        Returns:
            Max input tokens or DEFAULT_MAX_INPUT_TOKENS
        """
        model = self._cache.get(model_id)
        if model and model.get("tokenLimits"):
            return model["tokenLimits"].get("maxInputTokens") or DEFAULT_MAX_INPUT_TOKENS
        return DEFAULT_MAX_INPUT_TOKENS

    def is_empty(self) -> bool:
        """
        Check if cache is empty.

        Returns:
            True if cache is empty
        """
        return not self._cache

    def is_stale(self) -> bool:
        """
        Check if cache is stale.

        Returns:
            True if cache is stale (older than cache_ttl seconds)
            or cache was never updated
        """
        if not self._last_update:
            return True
        return time.time() - self._last_update > self._cache_ttl

    def get_all_model_ids(self) -> List[str]:
        """
        Return all model IDs in cache.

        Returns:
            List of model IDs
        """
        return list(self._cache.keys())

    @property
    def size(self) -> int:
        """Number of models in cache."""
        return len(self._cache)

    @property
    def last_update_time(self) -> Optional[float]:
        """Last update timestamp (seconds) or None."""
        return self._last_update

    @property
    def is_background_refresh_running(self) -> bool:
        """Check if background refresh is running."""
        return self._refresh_task is not None and not self._refresh_task.done()