# -*- coding: utf-8 -*-

"""
KiroGate 用户管理模块。

处理用户会话、OAuth2 认证和用户相关操作。
"""

import secrets
from typing import Optional, Tuple

import httpx
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from loguru import logger

from kiro_gateway.config import (
    settings,
    OAUTH_AUTHORIZATION_URL,
    OAUTH_TOKEN_URL,
    OAUTH_USER_URL,
    GITHUB_AUTHORIZATION_URL,
    GITHUB_TOKEN_URL,
    GITHUB_USER_URL,
)
from kiro_gateway.database import user_db, User


class UserSessionManager:
    """用户会话管理器。"""

    def __init__(self):
        self._serializer = URLSafeTimedSerializer(settings.user_session_secret)
        self._oauth_states: dict[str, int] = {}  # state -> timestamp

    def create_session(self, user_id: int) -> str:
        """Create a signed session token for user."""
        return self._serializer.dumps({"user_id": user_id})

    def verify_session(self, token: str) -> Optional[int]:
        """
        Verify session token and return user_id if valid.

        Returns:
            user_id if valid, None otherwise
        """
        if not token:
            return None
        try:
            data = self._serializer.loads(token, max_age=settings.user_session_max_age)
            return data.get("user_id")
        except (BadSignature, SignatureExpired):
            return None

    def create_oauth_state(self) -> str:
        """Create a random state for OAuth2 CSRF protection."""
        import time
        state = secrets.token_urlsafe(32)
        self._oauth_states[state] = int(time.time())
        # Clean old states (> 10 minutes)
        cutoff = int(time.time()) - 600
        self._oauth_states = {k: v for k, v in self._oauth_states.items() if v > cutoff}
        return state

    def verify_oauth_state(self, state: str) -> bool:
        """Verify OAuth2 state parameter."""
        if state in self._oauth_states:
            del self._oauth_states[state]
            return True
        return False


class OAuth2Client:
    """LinuxDo OAuth2 客户端。"""

    def __init__(self):
        self.client_id = settings.oauth_client_id
        self.client_secret = settings.oauth_client_secret
        self.redirect_uri = settings.oauth_redirect_uri

    @property
    def is_configured(self) -> bool:
        """Check if OAuth2 is properly configured."""
        return bool(self.client_id and self.client_secret)

    def get_authorization_url(self, state: str) -> str:
        """Get OAuth2 authorization URL."""
        params = {
            "client_id": self.client_id,
            "response_type": "code",
            "redirect_uri": self.redirect_uri,
            "state": state,
        }
        query = "&".join(f"{k}={v}" for k, v in params.items())
        return f"{OAUTH_AUTHORIZATION_URL}?{query}"

    async def exchange_code(self, code: str) -> Optional[dict]:
        """
        Exchange authorization code for access token.

        Returns:
            Token response dict or None on failure
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    OAUTH_TOKEN_URL,
                    data={
                        "grant_type": "authorization_code",
                        "code": code,
                        "redirect_uri": self.redirect_uri,
                    },
                    auth=(self.client_id, self.client_secret),
                    headers={"Accept": "application/json"},
                    timeout=30.0,
                )
                if response.status_code == 200:
                    return response.json()
                logger.error(f"OAuth2 token exchange failed: {response.status_code} - {response.text}")
            except Exception as e:
                logger.error(f"OAuth2 token exchange error: {e}")
        return None

    async def get_user_info(self, access_token: str) -> Optional[dict]:
        """
        Get user info from LinuxDo API.

        Returns:
            User info dict or None on failure
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    OAUTH_USER_URL,
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Accept": "application/json",
                    },
                    timeout=30.0,
                )
                if response.status_code == 200:
                    return response.json()
                logger.error(f"OAuth2 user info failed: {response.status_code} - {response.text}")
            except Exception as e:
                logger.error(f"OAuth2 user info error: {e}")
        return None


class GitHubOAuth2Client:
    """GitHub OAuth2 客户端。"""

    def __init__(self):
        self.client_id = settings.github_client_id
        self.client_secret = settings.github_client_secret
        self.redirect_uri = settings.github_redirect_uri

    @property
    def is_configured(self) -> bool:
        """Check if GitHub OAuth2 is properly configured."""
        return bool(self.client_id and self.client_secret)

    def get_authorization_url(self, state: str) -> str:
        """Get GitHub OAuth2 authorization URL."""
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": "read:user user:email",
            "state": state,
        }
        query = "&".join(f"{k}={v}" for k, v in params.items())
        return f"{GITHUB_AUTHORIZATION_URL}?{query}"

    async def exchange_code(self, code: str) -> Optional[dict]:
        """
        Exchange authorization code for access token.

        Returns:
            Token response dict or None on failure
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    GITHUB_TOKEN_URL,
                    data={
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "code": code,
                        "redirect_uri": self.redirect_uri,
                    },
                    headers={"Accept": "application/json"},
                    timeout=30.0,
                )
                if response.status_code == 200:
                    return response.json()
                logger.error(f"GitHub OAuth2 token exchange failed: {response.status_code} - {response.text}")
            except Exception as e:
                logger.error(f"GitHub OAuth2 token exchange error: {e}")
        return None

    async def get_user_info(self, access_token: str) -> Optional[dict]:
        """
        Get user info from GitHub API.

        Returns:
            User info dict or None on failure
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    GITHUB_USER_URL,
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Accept": "application/vnd.github.v3+json",
                        "User-Agent": "KiroGate",
                    },
                    timeout=30.0,
                )
                if response.status_code == 200:
                    return response.json()
                logger.error(f"GitHub user info failed: {response.status_code} - {response.text}")
            except Exception as e:
                logger.error(f"GitHub user info error: {e}")
        return None


class UserManager:
    """用户管理器，整合会话、OAuth2 和数据库操作。"""

    def __init__(self):
        self.session = UserSessionManager()
        self.oauth = OAuth2Client()
        self.github = GitHubOAuth2Client()

    async def oauth_login(self, code: str) -> Tuple[Optional[User], Optional[str]]:
        """
        Complete OAuth2 login flow.

        Args:
            code: Authorization code from OAuth2 callback

        Returns:
            (User, session_token) on success, (None, error_message) on failure
        """
        # Exchange code for token
        token_data = await self.oauth.exchange_code(code)
        if not token_data:
            return None, "授权码交换失败"

        access_token = token_data.get("access_token")
        if not access_token:
            return None, "响应中缺少访问令牌"

        # Get user info
        user_info = await self.oauth.get_user_info(access_token)
        if not user_info:
            return None, "获取用户信息失败"

        # Extract user data
        linuxdo_id = str(user_info.get("id", ""))
        username = user_info.get("username", "") or user_info.get("name", "")
        avatar_url = user_info.get("avatar_url") or user_info.get("avatar_template", "")
        trust_level = user_info.get("trust_level", 0)

        if not linuxdo_id:
            return None, "用户信息无效：缺少 ID"

        # Check if user exists
        user = user_db.get_user_by_linuxdo(linuxdo_id)
        if user:
            # Update last login
            user_db.update_last_login(user.id)
            # Check if banned
            if user.is_banned:
                return None, "用户已被封禁"
        else:
            # Create new user
            user = user_db.create_user(
                linuxdo_id=linuxdo_id,
                username=username,
                avatar_url=avatar_url,
                trust_level=trust_level
            )
            logger.info(f"New user registered: {username} (LinuxDo ID: {linuxdo_id})")

        # Create session
        session_token = self.session.create_session(user.id)
        return user, session_token

    async def github_login(self, code: str) -> Tuple[Optional[User], Optional[str]]:
        """
        Complete GitHub OAuth2 login flow.

        Args:
            code: Authorization code from GitHub OAuth2 callback

        Returns:
            (User, session_token) on success, (None, error_message) on failure
        """
        # Exchange code for token
        token_data = await self.github.exchange_code(code)
        if not token_data:
            return None, "授权码交换失败"

        access_token = token_data.get("access_token")
        if not access_token:
            return None, "响应中缺少访问令牌"

        # Get user info
        user_info = await self.github.get_user_info(access_token)
        if not user_info:
            return None, "获取用户信息失败"

        # Extract user data
        github_id = str(user_info.get("id", ""))
        username = user_info.get("login", "") or user_info.get("name", "")
        avatar_url = user_info.get("avatar_url", "")

        if not github_id:
            return None, "用户信息无效：缺少 ID"

        # Check if user exists by GitHub ID
        user = user_db.get_user_by_github(github_id)
        if user:
            # Update last login
            user_db.update_last_login(user.id)
            # Check if banned
            if user.is_banned:
                return None, "用户已被封禁"
        else:
            # Create new user with GitHub ID
            user = user_db.create_user(
                github_id=github_id,
                username=username,
                avatar_url=avatar_url,
                trust_level=0
            )
            logger.info(f"New user registered via GitHub: {username} (GitHub ID: {github_id})")

        # Create session
        session_token = self.session.create_session(user.id)
        return user, session_token

    def get_current_user(self, session_token: str) -> Optional[User]:
        """Get current user from session token."""
        user_id = self.session.verify_session(session_token)
        if not user_id:
            return None
        user = user_db.get_user(user_id)
        if user and user.is_banned:
            return None
        return user

    def logout(self, session_token: str) -> bool:
        """Logout user (session invalidation is handled by cookie deletion)."""
        return True


# Global user manager instance
user_manager = UserManager()
