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
KiroGate - OpenAI & Anthropic 兼容的 Kiro API 代理。

本包提供模块化架构，用于将 OpenAI/Anthropic API 请求代理到 Kiro (AWS CodeWhisperer)。

支持两种 API 格式:
    - OpenAI API: /v1/chat/completions
    - Anthropic API: /v1/messages

模块:
    - config: 配置和常量
    - models: OpenAI 和 Anthropic API 的 Pydantic 模型
    - auth: Kiro 认证管理器
    - cache: 模型元数据缓存
    - utils: 辅助工具函数
    - converters: OpenAI/Anthropic <-> Kiro 格式转换
    - parsers: AWS SSE 流解析器
    - streaming: 流式响应处理逻辑
    - http_client: 带重试逻辑的 HTTP 客户端
    - routes: FastAPI 路由
    - exceptions: 异常处理器
"""

# 版本从 config.py 导入 - 单一数据源 (Single Source of Truth)
from kiro_gateway.config import APP_VERSION as __version__

__author__ = "Based on kiro-openai-gateway by Jwadow"

# Основные компоненты для удобного импорта
from kiro_gateway.auth import KiroAuthManager
from kiro_gateway.cache import ModelInfoCache
from kiro_gateway.http_client import KiroHttpClient
from kiro_gateway.routes import router

# 配置
from kiro_gateway.config import (
    PROXY_API_KEY,
    REGION,
    MODEL_MAPPING,
    AVAILABLE_MODELS,
    APP_VERSION,
    APP_TITLE,
    APP_DESCRIPTION,
)

# Модели
from kiro_gateway.models import (
    ChatCompletionRequest,
    ChatMessage,
    OpenAIModel,
    ModelList,
    # Anthropic models
    AnthropicMessagesRequest,
    AnthropicMessage,
    AnthropicTool,
    AnthropicContentBlock,
    AnthropicMessagesResponse,
    AnthropicUsage,
)

# Конвертеры
from kiro_gateway.converters import (
    build_kiro_payload,
    extract_text_content,
    merge_adjacent_messages,
    # Anthropic converters
    convert_anthropic_to_openai_request,
    convert_anthropic_tools_to_openai,
    convert_anthropic_messages_to_openai,
)

# Парсеры
from kiro_gateway.parsers import (
    AwsEventStreamParser,
    parse_bracket_tool_calls,
)

# Streaming
from kiro_gateway.streaming import (
    stream_kiro_to_openai,
    collect_stream_response,
    # Anthropic streaming
    stream_kiro_to_anthropic,
    collect_anthropic_response,
)

# Exceptions
from kiro_gateway.exceptions import (
    validation_exception_handler,
    http_exception_handler,
    sanitize_validation_errors,
)

__all__ = [
    # Версия
    "__version__",

    # Основные классы
    "KiroAuthManager",
    "ModelInfoCache",
    "KiroHttpClient",
    "router",

    # 配置
    "PROXY_API_KEY",
    "REGION",
    "MODEL_MAPPING",
    "AVAILABLE_MODELS",
    "APP_VERSION",
    "APP_TITLE",
    "APP_DESCRIPTION",

    # OpenAI модели
    "ChatCompletionRequest",
    "ChatMessage",
    "OpenAIModel",
    "ModelList",

    # Anthropic модели
    "AnthropicMessagesRequest",
    "AnthropicMessage",
    "AnthropicTool",
    "AnthropicContentBlock",
    "AnthropicMessagesResponse",
    "AnthropicUsage",

    # Конвертеры
    "build_kiro_payload",
    "extract_text_content",
    "merge_adjacent_messages",
    "convert_anthropic_to_openai_request",
    "convert_anthropic_tools_to_openai",
    "convert_anthropic_messages_to_openai",

    # Парсеры
    "AwsEventStreamParser",
    "parse_bracket_tool_calls",

    # Streaming
    "stream_kiro_to_openai",
    "collect_stream_response",
    "stream_kiro_to_anthropic",
    "collect_anthropic_response",

    # Exceptions
    "validation_exception_handler",
    "http_exception_handler",
    "sanitize_validation_errors",
]