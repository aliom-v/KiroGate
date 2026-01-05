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
KiroGate 配置模块。

集中管理所有配置项、常量和模型映射。
使用 Pydantic Settings 进行类型安全的环境变量加载。
"""

import re
from pathlib import Path
from typing import Dict, List, Optional

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def _get_raw_env_value(var_name: str, env_file: str = ".env") -> Optional[str]:
    """
    从 .env 文件读取原始变量值，不处理转义序列。

    这对于 Windows 路径很重要，因为反斜杠（如 D:\\Projects\\file.json）
    可能被错误地解释为转义序列（\\a -> bell, \\n -> newline 等）。

    Args:
        var_name: 环境变量名
        env_file: .env 文件路径（默认 ".env"）

    Returns:
        原始变量值，如果未找到则返回 None
    """
    env_path = Path(env_file)
    if not env_path.exists():
        return None

    try:
        content = env_path.read_text(encoding="utf-8")
        pattern = rf'^{re.escape(var_name)}=(["\']?)(.+?)\1\s*$'

        for line in content.splitlines():
            line = line.strip()
            if line.startswith("#") or not line:
                continue

            match = re.match(pattern, line)
            if match:
                return match.group(2)
    except (FileNotFoundError, PermissionError, OSError) as e:
        # File not found or permission issues are expected when env file doesn't exist
        pass
    except (re.error, ValueError) as e:
        # Regex or parsing errors - log but don't fail
        from loguru import logger
        logger.debug(f"Error parsing env file for {var_name}: {e}")

    return None


class Settings(BaseSettings):
    """
    应用程序配置类。

    使用 Pydantic Settings 进行类型安全的环境变量加载和验证。
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ==================================================================================================
    # 代理服务器设置
    # ==================================================================================================

    # 代理 API 密钥（客户端需要在 Authorization header 中传递）
    proxy_api_key: str = Field(default="changeme_proxy_secret", alias="PROXY_API_KEY")

    # ==================================================================================================
    # Kiro API 凭证
    # ==================================================================================================

    # 用于刷新 access token 的 refresh token
    refresh_token: str = Field(default="", alias="REFRESH_TOKEN")

    # AWS CodeWhisperer Profile ARN
    profile_arn: str = Field(default="", alias="PROFILE_ARN")

    # AWS 区域（默认 us-east-1）
    region: str = Field(default="us-east-1", alias="KIRO_REGION")

    # 凭证文件路径（可选，作为 .env 的替代）
    kiro_creds_file: str = Field(default="", alias="KIRO_CREDS_FILE")

    # ==================================================================================================
    # Token 设置
    # ==================================================================================================

    # Token 刷新阈值（秒）- 在过期前多久刷新
    token_refresh_threshold: int = Field(default=600)

    # ==================================================================================================
    # 重试配置
    # ==================================================================================================

    # 最大重试次数
    max_retries: int = Field(default=3, alias="MAX_RETRIES")

    # 重试基础延迟（秒）- 使用指数退避：delay * (2 ** attempt)
    base_retry_delay: float = Field(default=1.0, alias="BASE_RETRY_DELAY")

    # ==================================================================================================
    # 模型缓存设置
    # ==================================================================================================

    # 模型缓存 TTL（秒）
    model_cache_ttl: int = Field(default=3600, alias="MODEL_CACHE_TTL")

    # 默认最大输入 token 数
    default_max_input_tokens: int = Field(default=200000)

    # ==================================================================================================
    # Tool Description 处理（Kiro API 限制）
    # ==================================================================================================

    # Tool description 最大长度（字符）
    # 超过此限制的描述将被移至 system prompt
    tool_description_max_length: int = Field(default=10000, alias="TOOL_DESCRIPTION_MAX_LENGTH")

    # ==================================================================================================
    # 日志设置
    # ==================================================================================================

    # 日志级别：TRACE, DEBUG, INFO, WARNING, ERROR, CRITICAL
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    # ==================================================================================================
    # 超时设置
    # ==================================================================================================

    # 等待模型首个 token 的超时时间（秒）
    # 对于 Opus 等慢模型，建议设置为 120-180 秒
    first_token_timeout: float = Field(default=120.0, alias="FIRST_TOKEN_TIMEOUT")

    # 首个 token 超时时的最大重试次数
    first_token_max_retries: int = Field(default=3, alias="FIRST_TOKEN_MAX_RETRIES")

    # 流式读取超时（秒）- 读取流中每个 chunk 的最大等待时间
    # 对于慢模型会自动乘以倍数。建议设置为 180-300 秒
    # 这是为了处理大文档时模型可能需要更长时间生成每个 chunk
    stream_read_timeout: float = Field(default=300.0, alias="STREAM_READ_TIMEOUT")

    # 非流式请求超时（秒）- 等待完整响应的最大时间
    # 对于复杂请求，建议设置为 600-1200 秒
    non_stream_timeout: float = Field(default=900.0, alias="NON_STREAM_TIMEOUT")

    # ==================================================================================================
    # 调试设置
    # ==================================================================================================

    # 调试日志模式：off, errors, all
    debug_mode: str = Field(default="off", alias="DEBUG_MODE")

    # 调试日志目录
    debug_dir: str = Field(default="debug_logs", alias="DEBUG_DIR")

    # ==================================================================================================
    # 速率限制设置
    # ==================================================================================================

    # 速率限制：每分钟请求数（0 表示禁用）
    rate_limit_per_minute: int = Field(default=0, alias="RATE_LIMIT_PER_MINUTE")

    # ==================================================================================================
    # 慢模型配置
    # ==================================================================================================

    # 慢模型的超时倍数
    # 对于 Opus 等慢模型，超时时间会乘以这个倍数
    # 建议设置为 3.0-4.0，因为慢模型处理大文档时可能需要更长时间
    slow_model_timeout_multiplier: float = Field(default=3.0, alias="SLOW_MODEL_TIMEOUT_MULTIPLIER")

    # ==================================================================================================
    # 自动分片配置（长文档处理）
    # ==================================================================================================

    # 是否启用自动分片功能
    auto_chunking_enabled: bool = Field(default=False, alias="AUTO_CHUNKING_ENABLED")

    # 触发自动分片的阈值（字符数）
    auto_chunk_threshold: int = Field(default=150000, alias="AUTO_CHUNK_THRESHOLD")

    # 每个分片的最大字符数
    chunk_max_chars: int = Field(default=100000, alias="CHUNK_MAX_CHARS")

    # 分片重叠字符数
    chunk_overlap_chars: int = Field(default=2000, alias="CHUNK_OVERLAP_CHARS")

    # ==================================================================================================
    # Admin 管理页面配置
    # ==================================================================================================

    # Admin 登录密码
    admin_password: str = Field(default="admin123", alias="ADMIN_PASSWORD")

    # Admin Session 签名密钥（请在生产环境中更改）
    admin_secret_key: str = Field(default="kirogate_admin_secret_key_change_me", alias="ADMIN_SECRET_KEY")

    # Admin Session 有效期（秒）
    admin_session_max_age: int = Field(default=86400, alias="ADMIN_SESSION_MAX_AGE")

    # Admin Session SameSite 策略: lax/strict/none
    admin_cookie_samesite: str = Field(default="strict", alias="ADMIN_COOKIE_SAMESITE")

    # ==================================================================================================
    # Cookie & CSRF 配置
    # ==================================================================================================

    # 是否强制 secure cookie（None 表示自动按请求协议判断）
    cookie_secure: Optional[bool] = Field(default=None, alias="COOKIE_SECURE")

    # OAuth 临时 state cookie 的 SameSite 策略
    oauth_state_cookie_samesite: str = Field(default="lax", alias="OAUTH_STATE_COOKIE_SAMESITE")

    # 是否启用 CSRF 保护（仅管理/用户端接口）
    csrf_enabled: bool = Field(default=True, alias="CSRF_ENABLED")

    # ==================================================================================================
    # OAuth2 LinuxDo 配置
    # ==================================================================================================

    # OAuth2 Client ID
    oauth_client_id: str = Field(default="", alias="OAUTH_CLIENT_ID")

    # OAuth2 Client Secret
    oauth_client_secret: str = Field(default="", alias="OAUTH_CLIENT_SECRET")

    # OAuth2 Redirect URI
    oauth_redirect_uri: str = Field(default="http://localhost:8000/oauth2/callback", alias="OAUTH_REDIRECT_URI")

    # ==================================================================================================
    # OAuth2 GitHub 配置
    # ==================================================================================================

    # GitHub OAuth2 Client ID
    github_client_id: str = Field(default="", alias="GITHUB_CLIENT_ID")

    # GitHub OAuth2 Client Secret
    github_client_secret: str = Field(default="", alias="GITHUB_CLIENT_SECRET")

    # GitHub OAuth2 Redirect URI
    github_redirect_uri: str = Field(default="http://localhost:8000/oauth2/github/callback", alias="GITHUB_REDIRECT_URI")

    # ==================================================================================================
    # 用户系统配置
    # ==================================================================================================

    # 用户 Session 签名密钥
    user_session_secret: str = Field(default="kirogate_user_secret_change_me", alias="USER_SESSION_SECRET")

    # 用户 Session 有效期（秒），默认7天
    user_session_max_age: int = Field(default=604800, alias="USER_SESSION_MAX_AGE")

    # 用户 Session SameSite 策略: lax/strict/none
    user_cookie_samesite: str = Field(default="lax", alias="USER_COOKIE_SAMESITE")

    # Token 加密密钥（32字节）
    token_encrypt_key: str = Field(default="kirogate_token_encrypt_key_32b!", alias="TOKEN_ENCRYPT_KEY")

    # Token 健康检查间隔（秒）
    token_health_check_interval: int = Field(default=3600, alias="TOKEN_HEALTH_CHECK_INTERVAL")

    # Token 最低成功率阈值
    token_min_success_rate: float = Field(default=0.7, alias="TOKEN_MIN_SUCCESS_RATE")

    # 静态资源代理配置
    static_assets_proxy_enabled: bool = Field(default=True, alias="STATIC_ASSETS_PROXY_ENABLED")
    static_assets_proxy_base: str = Field(default="https://proxy.jhun.edu.kg", alias="STATIC_ASSETS_PROXY_BASE")

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """验证日志级别。"""
        valid_levels = {"TRACE", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        v = v.upper()
        if v not in valid_levels:
            return "INFO"
        return v

    @field_validator("debug_mode")
    @classmethod
    def validate_debug_mode(cls, v: str) -> str:
        """验证调试模式。"""
        valid_modes = {"off", "errors", "all"}
        v = v.lower()
        if v not in valid_modes:
            return "off"
        return v

    @field_validator("admin_cookie_samesite", "user_cookie_samesite", "oauth_state_cookie_samesite")
    @classmethod
    def validate_cookie_samesite(cls, v: str) -> str:
        """验证 SameSite 值。"""
        valid = {"lax", "strict", "none"}
        v = v.lower()
        if v not in valid:
            return "lax"
        return v

    @model_validator(mode="after")
    def validate_security_defaults(self) -> "Settings":
        """验证安全配置，警告使用默认密钥。"""
        from loguru import logger

        insecure_defaults = []

        # 检查默认密码
        if self.admin_password == "admin123":
            insecure_defaults.append("ADMIN_PASSWORD 使用默认值 'admin123'")

        # 检查默认密钥
        default_keys = {
            "admin_secret_key": "kirogate_admin_secret_key_change_me",
            "user_session_secret": "kirogate_user_secret_change_me",
            "token_encrypt_key": "kirogate_token_encrypt_key_32b!",
        }

        for key_name, default_value in default_keys.items():
            value = getattr(self, key_name)
            if value == default_value:
                insecure_defaults.append(f"{key_name.upper()} 使用默认值（不安全）")

        if insecure_defaults:
            logger.warning("=" * 60)
            logger.warning("安全警告: 检测到不安全的默认配置！")
            for issue in insecure_defaults:
                logger.warning(f"  - {issue}")
            logger.warning("请在生产环境中修改 .env 文件中的相关配置")
            logger.warning("=" * 60)

        return self


# Global settings instance
settings = Settings()

# Handle KIRO_CREDS_FILE Windows path issue
_raw_creds_file = _get_raw_env_value("KIRO_CREDS_FILE") or settings.kiro_creds_file
if _raw_creds_file:
    settings.kiro_creds_file = str(Path(_raw_creds_file))

# ==================================================================================================
# Backward-compatible exports (DEPRECATED - only kept for tests and external compatibility)
# WARNING: These constants are deprecated. Use `settings.xxx` directly in new code.
# ==================================================================================================

PROXY_API_KEY: str = settings.proxy_api_key
REFRESH_TOKEN: str = settings.refresh_token
PROFILE_ARN: str = settings.profile_arn
REGION: str = settings.region
KIRO_CREDS_FILE: str = settings.kiro_creds_file
TOKEN_REFRESH_THRESHOLD: int = settings.token_refresh_threshold
MAX_RETRIES: int = settings.max_retries
BASE_RETRY_DELAY: float = settings.base_retry_delay
MODEL_CACHE_TTL: int = settings.model_cache_ttl
DEFAULT_MAX_INPUT_TOKENS: int = settings.default_max_input_tokens
TOOL_DESCRIPTION_MAX_LENGTH: int = settings.tool_description_max_length
LOG_LEVEL: str = settings.log_level
FIRST_TOKEN_TIMEOUT: float = settings.first_token_timeout
FIRST_TOKEN_MAX_RETRIES: int = settings.first_token_max_retries
STREAM_READ_TIMEOUT: float = settings.stream_read_timeout
NON_STREAM_TIMEOUT: float = settings.non_stream_timeout
DEBUG_MODE: str = settings.debug_mode
DEBUG_DIR: str = settings.debug_dir
RATE_LIMIT_PER_MINUTE: int = settings.rate_limit_per_minute
SLOW_MODEL_TIMEOUT_MULTIPLIER: float = settings.slow_model_timeout_multiplier
AUTO_CHUNKING_ENABLED: bool = settings.auto_chunking_enabled
AUTO_CHUNK_THRESHOLD: int = settings.auto_chunk_threshold
CHUNK_MAX_CHARS: int = settings.chunk_max_chars
CHUNK_OVERLAP_CHARS: int = settings.chunk_overlap_chars
ADMIN_PASSWORD: str = settings.admin_password
ADMIN_SECRET_KEY: str = settings.admin_secret_key
ADMIN_SESSION_MAX_AGE: int = settings.admin_session_max_age

# OAuth2 & User System
OAUTH_CLIENT_ID: str = settings.oauth_client_id
OAUTH_CLIENT_SECRET: str = settings.oauth_client_secret
OAUTH_REDIRECT_URI: str = settings.oauth_redirect_uri
USER_SESSION_SECRET: str = settings.user_session_secret
USER_SESSION_MAX_AGE: int = settings.user_session_max_age
TOKEN_ENCRYPT_KEY: str = settings.token_encrypt_key
TOKEN_HEALTH_CHECK_INTERVAL: int = settings.token_health_check_interval
TOKEN_MIN_SUCCESS_RATE: float = settings.token_min_success_rate
STATIC_ASSETS_PROXY_ENABLED: bool = settings.static_assets_proxy_enabled
STATIC_ASSETS_PROXY_BASE: str = settings.static_assets_proxy_base

# OAuth2 LinuxDo endpoints
OAUTH_AUTHORIZATION_URL: str = "https://connect.linux.do/oauth2/authorize"
OAUTH_TOKEN_URL: str = "https://connect.linux.do/oauth2/token"
OAUTH_USER_URL: str = "https://connect.linux.do/api/user"

# OAuth2 GitHub configuration
GITHUB_CLIENT_ID: str = settings.github_client_id
GITHUB_CLIENT_SECRET: str = settings.github_client_secret
GITHUB_REDIRECT_URI: str = settings.github_redirect_uri

# OAuth2 GitHub endpoints
GITHUB_AUTHORIZATION_URL: str = "https://github.com/login/oauth/authorize"
GITHUB_TOKEN_URL: str = "https://github.com/login/oauth/access_token"
GITHUB_USER_URL: str = "https://api.github.com/user"

# ==================================================================================================
# Slow Model Configuration
# ==================================================================================================

# 慢模型列表 - 这些模型需要更长的超时时间
SLOW_MODELS: frozenset = frozenset({
    "claude-opus-4-5",
    "claude-opus-4-5-20251101",
    "claude-3-opus",
    "claude-3-opus-20240229",
})


# ==================================================================================================
# Kiro API URL Templates
# ==================================================================================================

KIRO_REFRESH_URL_TEMPLATE: str = "https://prod.{region}.auth.desktop.kiro.dev/refreshToken"
AWS_SSO_OIDC_URL_TEMPLATE: str = "https://oidc.{region}.amazonaws.com/token"
KIRO_API_HOST_TEMPLATE: str = "https://codewhisperer.{region}.amazonaws.com"
KIRO_Q_HOST_TEMPLATE: str = "https://q.{region}.amazonaws.com"

# ==================================================================================================
# Model Mapping
# ==================================================================================================

# External model names (OpenAI compatible) -> Kiro internal ID
MODEL_MAPPING: Dict[str, str] = {
    # Claude Opus 4.5 - Top tier model
    "claude-opus-4-5": "claude-opus-4.5",
    "claude-opus-4-5-20251101": "claude-opus-4.5",

    # Claude Haiku 4.5 - Fast model
    "claude-haiku-4-5": "claude-haiku-4.5",
    "claude-haiku-4-5-20251001": "claude-haiku-4.5",
    "claude-haiku-4.5": "claude-haiku-4.5",

    # Claude Sonnet 4.5 - Enhanced model
    "claude-sonnet-4-5": "CLAUDE_SONNET_4_5_20250929_V1_0",
    "claude-sonnet-4-5-20250929": "CLAUDE_SONNET_4_5_20250929_V1_0",

    # Claude Sonnet 4 - Balanced model
    "claude-sonnet-4": "CLAUDE_SONNET_4_20250514_V1_0",
    "claude-sonnet-4-20250514": "CLAUDE_SONNET_4_20250514_V1_0",

    # Claude 3.7 Sonnet - Legacy model
    "claude-3-7-sonnet-20250219": "CLAUDE_3_7_SONNET_20250219_V1_0",

    # Convenience aliases
    "auto": "claude-sonnet-4.5",
}

# Available models list for /v1/models endpoint
AVAILABLE_MODELS: List[str] = [
    "claude-opus-4-5",
    "claude-opus-4-5-20251101",
    "claude-haiku-4-5",
    "claude-haiku-4-5-20251001",
    "claude-sonnet-4-5",
    "claude-sonnet-4-5-20250929",
    "claude-sonnet-4",
    "claude-sonnet-4-20250514",
    "claude-3-7-sonnet-20250219",
]

# ==================================================================================================
# Version Info
# ==================================================================================================

APP_VERSION: str = "2.1.0"
APP_TITLE: str = "KiroGate"
APP_DESCRIPTION: str = "OpenAI & Anthropic compatible Kiro API gateway. Based on kiro-openai-gateway by Jwadow"


def get_kiro_refresh_url(region: str) -> str:
    """Return token refresh URL for specified region."""
    return KIRO_REFRESH_URL_TEMPLATE.format(region=region)


def get_aws_sso_oidc_url(region: str) -> str:
    """Return AWS SSO OIDC token URL for specified region."""
    return AWS_SSO_OIDC_URL_TEMPLATE.format(region=region)


def get_kiro_api_host(region: str) -> str:
    """Return API host for specified region."""
    return KIRO_API_HOST_TEMPLATE.format(region=region)


def get_kiro_q_host(region: str) -> str:
    """Return Q API host for specified region."""
    return KIRO_Q_HOST_TEMPLATE.format(region=region)


def get_internal_model_id(external_model: str) -> str:
    """
    Convert external model name to Kiro internal ID.

    Args:
        external_model: External model name (e.g. "claude-sonnet-4-5")

    Returns:
        Kiro API internal model ID

    Raises:
        ValueError: If model is not supported
    """
    if external_model in MODEL_MAPPING:
        return MODEL_MAPPING[external_model]

    # 检查是否是有效的内部模型 ID（直接传递）
    valid_internal_ids = set(MODEL_MAPPING.values())
    if external_model in valid_internal_ids:
        return external_model

    available = ", ".join(sorted(AVAILABLE_MODELS))
    raise ValueError(f"不支持的模型: {external_model}。可用模型: {available}")


def get_adaptive_timeout(model: str, base_timeout: float) -> float:
    """
    根据模型类型获取自适应超时时间。

    对于慢模型（如 Opus），自动增加超时时间。

    Args:
        model: 模型名称
        base_timeout: 基础超时时间

    Returns:
        调整后的超时时间
    """
    if not model:
        return base_timeout

    model_lower = model.lower()
    for slow_model in SLOW_MODELS:
        if slow_model.lower() in model_lower:
            return base_timeout * SLOW_MODEL_TIMEOUT_MULTIPLIER

    return base_timeout
