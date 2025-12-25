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

from pydantic import Field, field_validator
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
    except Exception:
        pass

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
    # 首个 Token 超时设置（流式重试）
    # ==================================================================================================

    # 等待模型首个 token 的超时时间（秒）
    first_token_timeout: float = Field(default=15.0, alias="FIRST_TOKEN_TIMEOUT")

    # 首个 token 超时时的最大重试次数
    first_token_max_retries: int = Field(default=3, alias="FIRST_TOKEN_MAX_RETRIES")

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
DEBUG_MODE: str = settings.debug_mode
DEBUG_DIR: str = settings.debug_dir
RATE_LIMIT_PER_MINUTE: int = settings.rate_limit_per_minute

# ==================================================================================================
# Kiro API URL Templates
# ==================================================================================================

KIRO_REFRESH_URL_TEMPLATE: str = "https://prod.{region}.auth.desktop.kiro.dev/refreshToken"
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
    """
    return MODEL_MAPPING.get(external_model, external_model)
