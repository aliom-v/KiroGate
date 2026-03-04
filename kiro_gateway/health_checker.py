# -*- coding: utf-8 -*-

"""
KiroGate Token 健康检查器。

后台任务，定期检查所有活跃 Token 的有效性。
"""

import asyncio
from typing import Optional

import httpx
from loguru import logger

from kiro_gateway.config import settings
from kiro_gateway.database import user_db
from kiro_gateway.auth import KiroAuthManager


class TokenHealthChecker:
    """Token 健康检查后台任务。"""

    def __init__(self):
        self._running = False
        self._task: Optional[asyncio.Task] = None
        self._check_interval = settings.token_health_check_interval

    async def start(self) -> None:
        """Start the health check background task."""
        if self._running:
            logger.warning("Token health checker is already running")
            return

        self._running = True
        self._task = asyncio.create_task(self._run_loop())
        logger.info(f"Token health checker started (interval: {self._check_interval}s)")

    async def stop(self) -> None:
        """Stop the health check background task."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None
        logger.info("Token health checker stopped")

    async def _run_loop(self) -> None:
        """Main health check loop."""
        while self._running:
            try:
                await asyncio.sleep(self._check_interval)
                await self.check_all_tokens()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health check loop error: {e}")
                await asyncio.sleep(60)  # Wait before retry

    async def check_all_tokens(self) -> dict:
        """
        Check all active tokens.

        Returns:
            Summary of check results
        """
        tokens = user_db.get_all_active_tokens()
        if not tokens:
            logger.debug("No active tokens to check")
            return {"checked": 0, "valid": 0, "invalid": 0}

        logger.info(f"Starting health check for {len(tokens)} tokens")

        valid_count = 0
        invalid_count = 0
        transient_fail_count = 0

        for token in tokens:
            try:
                result = await self.check_token(token.id)
                if result["is_valid"]:
                    valid_count += 1
                else:
                    if result["should_mark_invalid"]:
                        invalid_count += 1
                        user_db.set_token_status(token.id, "invalid")
                        logger.warning(f"Token {token.id} marked as invalid: {result['error']}")
                    else:
                        transient_fail_count += 1
                        logger.warning(
                            f"Token {token.id} health check transient failure, keep active: {result['error']}"
                        )
            except Exception as e:
                logger.error(f"Failed to check token {token.id}: {e}")
                transient_fail_count += 1

            # Small delay between checks to avoid rate limiting
            await asyncio.sleep(1)

        logger.info(
            f"Health check complete: {valid_count} valid, {invalid_count} invalid, "
            f"{transient_fail_count} transient_failed"
        )
        return {
            "checked": len(tokens),
            "valid": valid_count,
            "invalid": invalid_count,
            "transient_failed": transient_fail_count,
        }

    @staticmethod
    def _should_mark_invalid(error: Exception | str) -> bool:
        """
        Determine whether a failed health check indicates a permanent credential issue.

        Only permanent auth/credential failures should deactivate tokens.
        Transient failures (network/rate limit/5xx) keep token active.
        """
        if isinstance(error, httpx.HTTPStatusError):
            status = error.response.status_code if error.response else None
            if status in (400, 401, 403):
                return True
            return False

        text = str(error).lower()
        permanent_markers = (
            "bad credentials",
            "invalid_grant",
            "unauthorized",
            "forbidden",
            "client id is not set",
            "client secret is not set",
            "refresh token is not set",
            "响应中没有 accesstoken",
        )
        return any(marker in text for marker in permanent_markers)

    async def check_token(self, token_id: int) -> dict:
        """
        Check a single token's validity.

        Args:
            token_id: Token ID to check

        Returns:
            dict:
                - is_valid: bool
                - should_mark_invalid: bool
                - error: str | None
        """
        # Get full credentials (supports IDC mode)
        credentials = user_db.get_token_credentials(token_id)
        if not credentials or not credentials.get("refresh_token"):
            err = "Failed to load token credentials"
            user_db.record_health_check(token_id, False, err)
            return {
                "is_valid": False,
                "should_mark_invalid": True,
                "error": err,
            }

        # Try to get access token
        try:
            manager = KiroAuthManager(
                refresh_token=credentials["refresh_token"],
                client_id=credentials.get("client_id"),
                client_secret=credentials.get("client_secret"),
                region=settings.region,
                profile_arn=settings.profile_arn
            )
            access_token = await manager.get_access_token()

            if access_token:
                user_db.record_health_check(token_id, True)
                return {
                    "is_valid": True,
                    "should_mark_invalid": False,
                    "error": None,
                }

            err = "No access token returned"
            user_db.record_health_check(token_id, False, err)
            return {
                "is_valid": False,
                "should_mark_invalid": True,
                "error": err,
            }

        except Exception as e:
            error_msg = str(e)[:200]  # Truncate long error messages
            user_db.record_health_check(token_id, False, error_msg)
            return {
                "is_valid": False,
                "should_mark_invalid": self._should_mark_invalid(e),
                "error": error_msg,
            }


# Global health checker instance
health_checker = TokenHealthChecker()
