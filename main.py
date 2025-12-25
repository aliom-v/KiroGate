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
KiroGate - OpenAI & Anthropic 兼容的 Kiro API 网关。

应用程序入口点。创建 FastAPI 应用并连接路由。

用法:
    uvicorn main:app --host 0.0.0.0 --port 8000
    或直接运行:
    python main.py
"""

import logging
import sys
import asyncio
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from loguru import logger
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from kiro_gateway.config import (
    APP_TITLE,
    APP_DESCRIPTION,
    APP_VERSION,
    settings,
)
from kiro_gateway.auth import KiroAuthManager
from kiro_gateway.cache import ModelInfoCache
from kiro_gateway.routes import router, limiter, rate_limit_handler
from kiro_gateway.exceptions import validation_exception_handler
from kiro_gateway.middleware import RequestTrackingMiddleware, metrics_middleware
from kiro_gateway.http_client import close_global_http_client


# --- Loguru 配置 ---
logger.remove()
logger.add(
    sys.stderr,
    level=settings.log_level,
    colorize=True,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
)


class InterceptHandler(logging.Handler):
    """
    拦截标准 logging 并重定向到 loguru。

    这允许捕获来自 uvicorn、FastAPI 和其他使用标准 logging 而非 loguru 的库的日志。
    """

    def emit(self, record: logging.LogRecord) -> None:
        # 获取对应的 loguru 级别
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # 查找调用帧以正确显示源
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def setup_logging_intercept():
    """
    配置从标准 logging 到 loguru 的拦截。

    拦截来自的日志：
    - uvicorn (access logs, error logs)
    - uvicorn.error
    - uvicorn.access
    - fastapi
    """
    # 要拦截的日志器列表
    loggers_to_intercept = [
        "uvicorn",
        "uvicorn.error",
        "uvicorn.access",
        "fastapi",
    ]

    for logger_name in loggers_to_intercept:
        logging_logger = logging.getLogger(logger_name)
        logging_logger.handlers = [InterceptHandler()]
        logging_logger.propagate = False


# 配置 uvicorn/fastapi 日志拦截
setup_logging_intercept()


# --- 配置验证 ---
def validate_configuration() -> None:
    """
    验证所需配置是否存在。

    检查：
    - .env 文件是否存在
    - 是否配置了 REFRESH_TOKEN 或 KIRO_CREDS_FILE

    Raises:
        SystemExit: 如果缺少关键配置
    """
    errors = []

    # 检查 .env 文件是否存在
    env_file = Path(".env")
    env_example = Path(".env.example")

    if not env_file.exists():
        errors.append(
            ".env file not found!\n"
            "\n"
            "To get started:\n"
            "1. Create .env or rename from .env.example:\n"
            "   cp .env.example .env\n"
            "\n"
            "2. Edit .env and configure your credentials:\n"
            "   2.1. Set you super-secret password as PROXY_API_KEY\n"
            "   2.2. Set your Kiro credentials:\n"
            "      - 1 way: KIRO_CREDS_FILE to your Kiro credentials JSON file\n"
            "      - 2 way: REFRESH_TOKEN from Kiro IDE traffic\n"
            "\n"
            "See README.md for detailed instructions."
        )
    else:
        # .env 存在，检查凭证
        has_refresh_token = bool(settings.refresh_token)
        has_creds_file = bool(settings.kiro_creds_file)

        # 检查凭证文件是否实际存在
        if settings.kiro_creds_file:
            creds_path = Path(settings.kiro_creds_file).expanduser()
            if not creds_path.exists():
                has_creds_file = False
                logger.warning(f"KIRO_CREDS_FILE not found: {settings.kiro_creds_file}")

        if not has_refresh_token and not has_creds_file:
            errors.append(
                "No Kiro credentials configured!\n"
                "\n"
                "   Configure one of the following in your .env file:\n"
                "\n"
                "Set you super-secret password as PROXY_API_KEY\n"
                "   PROXY_API_KEY=\"my-super-secret-password-123\"\n"
                "\n"
                "   Option 1 (Recommended): JSON credentials file\n"
                "      KIRO_CREDS_FILE=\"path/to/your/kiro-credentials.json\"\n"
                "\n"
                "   Option 2: Refresh token\n"
                "      REFRESH_TOKEN=\"your_refresh_token_here\"\n"
                "\n"
                "   See README.md for how to obtain credentials."
            )

    # 打印错误并退出（如果有）
    if errors:
        logger.error("")
        logger.error("=" * 60)
        logger.error("  CONFIGURATION ERROR")
        logger.error("=" * 60)
        for error in errors:
            for line in error.split('\n'):
                logger.error(f"  {line}")
        logger.error("=" * 60)
        logger.error("")
        sys.exit(1)

    # 记录成功的配置
    if settings.kiro_creds_file:
        logger.info(f"Using credentials file: {settings.kiro_creds_file}")
    elif settings.refresh_token:
        logger.info("Using refresh token from environment")


# 运行配置验证
validate_configuration()


# --- 生命周期管理器 ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    管理应用程序生命周期。

    创建并初始化：
    - KiroAuthManager 用于 token 管理
    - ModelInfoCache 用于模型缓存
    - 启动后台任务
    """
    logger.info("Starting application... Creating state managers.")

    # 创建 AuthManager
    auth_manager = KiroAuthManager(
        refresh_token=settings.refresh_token,
        profile_arn=settings.profile_arn,
        region=settings.region,
        creds_file=settings.kiro_creds_file if settings.kiro_creds_file else None
    )
    app.state.auth_manager = auth_manager

    # 创建模型缓存
    model_cache = ModelInfoCache()
    model_cache.set_auth_manager(auth_manager)
    app.state.model_cache = model_cache

    # 启动后台刷新任务
    await model_cache.start_background_refresh()

    # 初始填充缓存
    if model_cache.is_empty():
        logger.info("Performing initial model cache population...")
        await model_cache.refresh()

    logger.info("Application startup complete.")

    yield

    logger.info("Shutting down application...")

    # 停止后台任务
    await model_cache.stop_background_refresh()

    # 关闭全局 HTTP 客户端
    await close_global_http_client()

    logger.info("Application shutdown complete.")


# --- FastAPI 应用 ---
app = FastAPI(
    title=APP_TITLE,
    description=APP_DESCRIPTION,
    version=APP_VERSION,
    lifespan=lifespan
)

# 添加中间件（顺序很重要）
app.add_middleware(RequestTrackingMiddleware)
app.add_middleware(metrics_middleware)

# 设置速率限制器
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_handler)

# 注册验证错误处理器
app.add_exception_handler(RequestValidationError, validation_exception_handler)

# 包含路由
app.include_router(router)


# --- Uvicorn 日志配置 ---
# 最小配置，将 uvicorn 日志重定向到 loguru。
# 使用 InterceptHandler 拦截日志并传递给 loguru。
UVICORN_LOG_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "default": {
            "class": "main.InterceptHandler",
        },
    },
    "loggers": {
        "uvicorn": {"handlers": ["default"], "level": "INFO", "propagate": False},
        "uvicorn.error": {"handlers": ["default"], "level": "INFO", "propagate": False},
        "uvicorn.access": {"handlers": ["default"], "level": "INFO", "propagate": False},
    },
}


# --- 入口点 ---
if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Uvicorn server...")

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_config=UVICORN_LOG_CONFIG,
    )
