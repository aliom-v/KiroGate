# -*- coding: utf-8 -*-

"""
KiroGate Token 健康检查器。

后台任务，定期检查所有活跃 Token 的有效性。
"""

import asyncio
from typing import Optional

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
        Check all active and invalid tokens.

        Returns:
            Summary of check results
        """
        # Check both active and invalid tokens so previously-failed tokens can recover
        active_tokens = user_db.get_all_active_tokens()
        invalid_tokens_dict = user_db.get_all_tokens_with_users(status="invalid")
        invalid_tokens = [t for t in invalid_tokens_dict] if invalid_tokens_dict else []
        
        # Convert dict to token-like objects for invalid tokens
        class InvalidToken:
            def __init__(self, d):
                self.id = d.get("id")
                self.status = "invalid"
        invalid_tokens = [InvalidToken(t) for t in invalid_tokens]
        
        tokens = active_tokens + invalid_tokens
        if not tokens:
            logger.debug("No tokens to check")
            return {"checked": 0, "valid": 0, "invalid": 0}

        logger.info(f"Starting health check for {len(tokens)} tokens")

        valid_count = 0
        invalid_count = 0

        for token in tokens:
            try:
                is_valid = await self.check_token(token.id)
                if is_valid:
                    valid_count += 1
                    if token.status != "active":
                        user_db.set_token_status(token.id, "active")
                        logger.info(f"Token {token.id} recovered, marked as active")
                else:
                    invalid_count += 1
                    if token.status != "invalid":
                        user_db.set_token_status(token.id, "invalid")
                        logger.warning(f"Token {token.id} marked as invalid")
            except Exception as e:
                logger.error(f"Failed to check token {token.id}: {e}")
                invalid_count += 1

            # Small delay between checks to avoid rate limiting
            await asyncio.sleep(1)

        logger.info(f"Health check complete: {valid_count} valid, {invalid_count} invalid")
        return {
            "checked": len(tokens),
            "valid": valid_count,
            "invalid": invalid_count
        }
        """
        Check all active and invalid tokens.

        Returns:
            Summary of check results
        """
        # Check both active and invalid tokens so previously-failed tokens can recover
        tokens = user_db.get_all_active_tokens() + user_db.get_tokens_by_status("invalid")
        if not tokens:
            logger.debug("No tokens to check")
            return {"checked": 0, "valid": 0, "invalid": 0}

        logger.info(f"Starting health check for {len(tokens)} tokens")

        valid_count = 0
        invalid_count = 0

        for token in tokens:
            try:
                is_valid = await self.check_token(token.id)
                if is_valid:
                    valid_count += 1
                    if token.status != "active":
                        user_db.set_token_status(token.id, "active")
                        logger.info(f"Token {token.id} recovered, marked as active")
                else:
                    invalid_count += 1
                    if token.status != "invalid":
                        user_db.set_token_status(token.id, "invalid")
                        logger.warning(f"Token {token.id} marked as invalid")
            except Exception as e:
                logger.error(f"Failed to check token {token.id}: {e}")
                invalid_count += 1

            # Small delay between checks to avoid rate limiting
            await asyncio.sleep(1)

        logger.info(f"Health check complete: {valid_count} valid, {invalid_count} invalid")
        return {
            "checked": len(tokens),
            "valid": valid_count,
            "invalid": invalid_count
        }

    async def check_token(self, token_id: int) -> bool:
        """
        Check a single token's validity.

        Args:
            token_id: Token ID to check

        Returns:
            True if token is valid, False otherwise
        """
        # Get full token credentials (including client_id/client_secret for IDC tokens)
        creds = user_db.get_token_credentials(token_id)
        if not creds or not creds.get("refresh_token"):
            user_db.record_health_check(token_id, False, "Failed to get token credentials")
            return False

        refresh_token = creds["refresh_token"]
        client_id = creds.get("client_id")
        client_secret = creds.get("client_secret")

        # Try to get access token
        try:
            manager = KiroAuthManager(
                refresh_token=refresh_token,
                region=settings.region,
                profile_arn=settings.profile_arn,
                client_id=client_id,
                client_secret=client_secret
            )
            access_token = await manager.get_access_token()

            if access_token:
                user_db.record_health_check(token_id, True)
                return True
            else:
                user_db.record_health_check(token_id, False, "No access token returned")
                return False

        except Exception as e:
            error_msg = str(e)[:200]  # Truncate long error messages
            user_db.record_health_check(token_id, False, error_msg)
            return False
        """
        Check a single token's validity.

        Args:
            token_id: Token ID to check

        Returns:
            True if token is valid, False otherwise
        """
        # Get decrypted token
        refresh_token = user_db.get_decrypted_token(token_id)
        if not refresh_token:
            user_db.record_health_check(token_id, False, "Failed to decrypt token")
            return False

        # Try to get access token
        try:
            manager = KiroAuthManager(
                refresh_token=refresh_token,
                region=settings.region,
                profile_arn=settings.profile_arn
            )
            access_token = await manager.get_access_token()

            if access_token:
                user_db.record_health_check(token_id, True)
                return True
            else:
                user_db.record_health_check(token_id, False, "No access token returned")
                return False

        except Exception as e:
            error_msg = str(e)[:200]  # Truncate long error messages
            user_db.record_health_check(token_id, False, error_msg)
            return False


# Global health checker instance
health_checker = TokenHealthChecker()
