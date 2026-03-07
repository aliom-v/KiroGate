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
KiroBridge 异常处理器。

Содержит функции для обработки ошибок валидации и других исключений
в формате, совместимом с JSON-сериализацией.
"""

from typing import Any, List, Dict

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from loguru import logger


def sanitize_validation_errors(errors: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Преобразует ошибки валидации в JSON-сериализуемый формат.
    
    Pydantic может включать bytes объекты в поле 'input', которые
    не сериализуются в JSON. Эта функция конвертирует их в строки.
    
    Args:
        errors: Список ошибок валидации от Pydantic
    
    Returns:
        Список ошибок с bytes преобразованными в строки
    """
    sanitized = []
    for error in errors:
        sanitized_error = {}
        for key, value in error.items():
            if isinstance(value, bytes):
                # Конвертируем bytes в строку
                sanitized_error[key] = value.decode("utf-8", errors="replace")
            elif isinstance(value, (list, tuple)):
                # Рекурсивно обрабатываем списки
                sanitized_error[key] = [
                    v.decode("utf-8", errors="replace") if isinstance(v, bytes) else v
                    for v in value
                ]
            else:
                sanitized_error[key] = value
        sanitized.append(sanitized_error)
    return sanitized


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    Обработчик ошибок валидации Pydantic.
    
    Логирует детали ошибки и возвращает информативный ответ.
    Корректно обрабатывает bytes объекты в ошибках, преобразуя их в строки.
    
    For /v1/ API endpoints, returns OpenAI-compatible error format.
    
    Args:
        request: FastAPI Request объект
        exc: Исключение валидации от Pydantic
    
    Returns:
        JSONResponse с деталями ошибки и статусом 422
    """
    body = await request.body()
    body_str = body.decode("utf-8", errors="replace")
    
    # Санитизируем ошибки для JSON-сериализации
    sanitized_errors = sanitize_validation_errors(exc.errors())
    
    logger.error(f"Validation error (422): {sanitized_errors}")
    logger.error(f"Request body: {body_str[:500]}...")
    
    # For /v1/ API endpoints, return OpenAI-compatible error format
    # OpenCode (@ai-sdk/openai-compatible) and OpenClaw (openai-completions)
    # both expect {"error": {"message": "...", "type": "...", "code": ...}}
    path = request.url.path
    if path.startswith("/v1/"):
        # Build a human-readable error message from validation errors
        error_parts = []
        for err in sanitized_errors:
            loc = " -> ".join(str(l) for l in err.get("loc", []))
            msg = err.get("msg", "unknown error")
            error_parts.append(f"{loc}: {msg}" if loc else msg)
        error_message = "; ".join(error_parts) if error_parts else "Request validation failed"
        
        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "message": error_message,
                    "type": "invalid_request_error",
                    "code": "validation_error"
                }
            },
        )
    
    return JSONResponse(
        status_code=422,
        content={"detail": sanitized_errors, "body": body_str[:500]},
    )


async def http_exception_handler(request: Request, exc) -> JSONResponse:
    """
    Global HTTPException handler that returns OpenAI-compatible error format
    for /v1/ API endpoints.
    
    OpenCode (@ai-sdk/openai-compatible) and OpenClaw (openai-completions api)
    both expect error responses in the format:
    {"error": {"message": "...", "type": "...", "code": ...}}
    
    FastAPI's default HTTPException returns {"detail": "..."} which these
    SDKs cannot parse correctly.
    
    Args:
        request: FastAPI Request
        exc: HTTPException
    
    Returns:
        JSONResponse with OpenAI-compatible error format for API endpoints,
        or default format for non-API endpoints
    """
    path = request.url.path
    status_code = getattr(exc, 'status_code', 500)
    detail = getattr(exc, 'detail', 'Internal server error')
    
    if path.startswith("/v1/"):
        # Map HTTP status codes to OpenAI error types
        error_type_map = {
            400: "invalid_request_error",
            401: "authentication_error",
            403: "permission_error",
            404: "not_found_error",
            422: "invalid_request_error",
            429: "rate_limit_error",
            500: "server_error",
            502: "server_error",
            503: "server_error",
        }
        error_type = error_type_map.get(status_code, "api_error")
        
        return JSONResponse(
            status_code=status_code,
            content={
                "error": {
                    "message": str(detail),
                    "type": error_type,
                    "code": status_code
                }
            },
        )
    
    # For non-API endpoints, use default format
    return JSONResponse(
        status_code=status_code,
        content={"detail": str(detail)},
    )