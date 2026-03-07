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

from fastapi import FastAPI, Request
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
from kiro_gateway.exceptions import validation_exception_handler, http_exception_handler
from kiro_gateway.middleware import RequestTrackingMiddleware, MetricsMiddleware, SiteGuardMiddleware
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


# --- 启动 Banner ---
def _print_startup_banner():
    """打印启动成功后的 ASCII art logo 和项目信息。"""
    banner = """
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║     _  ___           ____       _                             ║
║    | |/ (_)_ __ ___/ ___| __ _| |_ ___                       ║
║    | ' /| | '__/ _ \\ |  _ / _` | __/ _ \\                      ║
║    | . \\| | | | (_) | |_| | (_| | ||  __/                     ║
║    |_|\\_\\_|_|  \\___/ \\____|\\__,_|\\__\\___|                     ║
║                                                               ║
║                  OpenAI & Anthropic Gateway                   ║
║                       Version 2.1.0                           ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
"""

    # 使用普通 print，因为这是美化输出，不需要记录到日志文件
    print(banner)

    # 输出项目地址信息
    logger.info("=" * 60)
    logger.info("🚀 KiroGate 启动成功!")
    logger.info("=" * 60)
    logger.info("📍 项目地址:")
    logger.info(f"   • 本地访问: http://127.0.0.1:8000")
    logger.info(f"   • 网络访问: http://0.0.0.0:8000")
    logger.info("📖 API 文档:")
    logger.info(f"   • Swagger UI: http://127.0.0.1:8000/docs")
    logger.info(f"   • Admin 面板: http://127.0.0.1:8000/admin")
    logger.info("=" * 60)


# --- 配置验证 ---
def validate_configuration() -> None:
    """
    验证所需配置是否存在。

    支持两种认证模式：
    1. 简单模式：需要配置 REFRESH_TOKEN 或 KIRO_CREDS_FILE
    2. 组合模式：只需配置 PROXY_API_KEY，REFRESH_TOKEN 由用户在请求中传递

    Raises:
        SystemExit: 如果缺少关键配置（PROXY_API_KEY）
    """
    errors = []

    # PROXY_API_KEY 是必须的
    if not settings.proxy_api_key:
        errors.append(
            "PROXY_API_KEY is required!\n"
            "\n"
            "Set PROXY_API_KEY in environment variable or .env file.\n"
            "This is the password used to authenticate API requests."
        )

    # 检查凭证配置
    has_refresh_token = bool(settings.refresh_token)
    has_creds_file = bool(settings.kiro_creds_file)

    # 检查凭证文件是否实际存在（URL 跳过本地路径检查）
    if settings.kiro_creds_file:
        is_url = settings.kiro_creds_file.startswith(('http://', 'https://'))
        if not is_url:
            creds_path = Path(settings.kiro_creds_file).expanduser()
            if not creds_path.exists():
                has_creds_file = False
                logger.warning(f"KIRO_CREDS_FILE not found: {settings.kiro_creds_file}")

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

    # 记录配置模式
    config_source = "environment variables" if not Path(".env").exists() else ".env file"

    if has_refresh_token or has_creds_file:
        # 简单模式：服务器配置了 REFRESH_TOKEN
        if settings.kiro_creds_file:
            if settings.kiro_creds_file.startswith(('http://', 'https://')):
                logger.info(f"Using credentials from URL: {settings.kiro_creds_file} (via {config_source})")
            else:
                logger.info(f"Using credentials file: {settings.kiro_creds_file} (via {config_source})")
        elif settings.refresh_token:
            logger.info(f"Using refresh token (via {config_source})")
        logger.info("Auth mode: Simple mode (server-configured REFRESH_TOKEN) + Multi-tenant mode supported")
    else:
        # 仅组合模式：用户在请求中传递 REFRESH_TOKEN
        logger.info("No REFRESH_TOKEN configured - running in multi-tenant only mode")
        logger.info("Auth mode: Multi-tenant only (users must provide PROXY_API_KEY:REFRESH_TOKEN)")
        logger.info("Tip: Configure REFRESH_TOKEN to enable simple mode authentication")


# 运行配置验证
validate_configuration()


# --- 生命周期管理器 ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    管理应用程序生命周期。

    创建并初始化：
    - KiroAuthManager 用于 token 管理（简单模式）
    - ModelInfoCache 用于模型缓存
    - 启动后台任务
    """
    logger.info("Starting application... Creating state managers.")

    # 确保 debug_logs 目录存在
    debug_dir = Path(settings.debug_dir)
    debug_dir.mkdir(parents=True, exist_ok=True)

    # 检查是否配置了全局凭证
    has_global_credentials = bool(settings.refresh_token) or bool(settings.kiro_creds_file)

    # 创建全局 AuthManager（简单模式使用）
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

    # 仅在有全局凭证时启动后台刷新和初始填充
    if has_global_credentials:
        # 启动后台刷新任务
        await model_cache.start_background_refresh()

        # 初始填充缓存
        if model_cache.is_empty():
            logger.info("Performing initial model cache population...")
            await model_cache.refresh()
    else:
        logger.warning("No global credentials configured - model cache refresh disabled")
        logger.warning("Simple mode authentication will not work, only multi-tenant mode available")

    logger.info("Application startup complete.")

    # 显示启动 banner
    _print_startup_banner()

    # Start token health checker (for user token pool)
    from kiro_gateway.health_checker import health_checker
    await health_checker.start()

    yield

    logger.info("Shutting down application...")

    # Stop health checker
    await health_checker.stop()

    # 停止后台任务
    if has_global_credentials:
        await model_cache.stop_background_refresh()

    # 关闭全局 HTTP 客户端
    await close_global_http_client()

    logger.info("Application shutdown complete.")


# --- FastAPI 应用 ---
app = FastAPI(
    title=APP_TITLE,
    description=APP_DESCRIPTION,
    version=APP_VERSION,
    lifespan=lifespan,
    docs_url=None,  # 禁用默认的 /docs，使用自定义页面
    redoc_url=None  # 禁用默认的 /redoc
)

# 添加中间件（顺序很重要：最后添加的最先执行）
app.add_middleware(RequestTrackingMiddleware)
app.add_middleware(MetricsMiddleware)
app.add_middleware(SiteGuardMiddleware)

# 设置速率限制器
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_handler)

# 注册验证错误处理器
app.add_exception_handler(RequestValidationError, validation_exception_handler)

# 注册 HTTPException 处理器 (OpenAI 兼容错误格式)
from fastapi import HTTPException as _HTTPException
app.add_exception_handler(_HTTPException, http_exception_handler)


# 404 页面处理器
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """Handle 404 errors with a custom page."""
    from fastapi.responses import HTMLResponse
    from kiro_gateway.pages import render_404_page
    return HTMLResponse(content=render_404_page(), status_code=404)


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
