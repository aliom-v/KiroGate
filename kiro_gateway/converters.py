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
OpenAI <-> Kiro 格式转换器。

Содержит функции для:
- Извлечения текстового контента из различных форматов
- Объединения соседних сообщений
- Построения истории разговора для Kiro API
- Сборки полного payload для запроса
"""

import json
from typing import Any, Dict, List, Optional, Tuple

from loguru import logger

from kiro_gateway.config import get_internal_model_id, TOOL_DESCRIPTION_MAX_LENGTH
from kiro_gateway.models import (
    ChatMessage,
    ChatCompletionRequest,
    Tool,
    ToolFunction,
    AnthropicMessage,
    AnthropicMessagesRequest,
    AnthropicTool,
    AnthropicContentBlock,
)


def extract_text_content(content: Any) -> str:
    """
    Извлекает текстовый контент из различных форматов.
    
    OpenAI API поддерживает несколько форматов content:
    - Строка: "Hello, world!"
    - Список: [{"type": "text", "text": "Hello"}]
    - None: пустое сообщение
    
    Args:
        content: Контент в любом поддерживаемом формате
    
    Returns:
        Извлечённый текст или пустая строка
    
    Example:
        >>> extract_text_content("Hello")
        'Hello'
        >>> extract_text_content([{"type": "text", "text": "World"}])
        'World'
        >>> extract_text_content(None)
        ''
    """
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        text_parts = []
        for item in content:
            if isinstance(item, dict):
                if item.get("type") == "text":
                    text_parts.append(item.get("text", ""))
                elif "text" in item:
                    text_parts.append(item["text"])
            elif isinstance(item, str):
                text_parts.append(item)
        return "".join(text_parts)
    return str(content)


def merge_adjacent_messages(messages: List[ChatMessage]) -> List[ChatMessage]:
    """
    Объединяет соседние сообщения с одинаковой ролью и обрабатывает tool messages.
    
    Kiro API не принимает несколько сообщений подряд от одного role.
    Эта функция объединяет такие сообщения в одно.
    
    Tool messages (role="tool") преобразуются в user messages с tool_results.
    
    Args:
        messages: Список сообщений
    
    Returns:
        Список сообщений с объединёнными соседними сообщениями
    
    Example:
        >>> msgs = [
        ...     ChatMessage(role="user", content="Hello"),
        ...     ChatMessage(role="user", content="World")
        ... ]
        >>> merged = merge_adjacent_messages(msgs)
        >>> len(merged)
        1
        >>> merged[0].content
        'Hello\\nWorld'
    """
    if not messages:
        return []
    
    # Сначала преобразуем tool messages в user messages с tool_results
    processed = []
    pending_tool_results = []
    
    for msg in messages:
        if msg.role == "tool":
            # Собираем tool results
            tool_result = {
                "type": "tool_result",
                "tool_use_id": msg.tool_call_id or "",
                "content": extract_text_content(msg.content) or "(empty result)"
            }
            pending_tool_results.append(tool_result)
            logger.debug(f"Collected tool result for tool_call_id={msg.tool_call_id}")
        else:
            # Если есть накопленные tool results, создаём user message с ними
            if pending_tool_results:
                # Создаём user message с tool_results
                tool_results_msg = ChatMessage(
                    role="user",
                    content=pending_tool_results.copy()
                )
                processed.append(tool_results_msg)
                pending_tool_results.clear()
                logger.debug(f"Created user message with {len(tool_results_msg.content)} tool results")
            
            processed.append(msg)
    
    # Если остались tool results в конце
    if pending_tool_results:
        tool_results_msg = ChatMessage(
            role="user",
            content=pending_tool_results.copy()
        )
        processed.append(tool_results_msg)
        logger.debug(f"Created final user message with {len(pending_tool_results)} tool results")
    
    # Теперь объединяем соседние сообщения с одинаковой ролью
    merged = []
    for msg in processed:
        if not merged:
            merged.append(msg)
            continue
        
        last = merged[-1]
        if msg.role == last.role:
            # Объединяем контент
            # Если оба контента - списки, объединяем списки
            if isinstance(last.content, list) and isinstance(msg.content, list):
                last.content = last.content + msg.content
            elif isinstance(last.content, list):
                last.content = last.content + [{"type": "text", "text": extract_text_content(msg.content)}]
            elif isinstance(msg.content, list):
                last.content = [{"type": "text", "text": extract_text_content(last.content)}] + msg.content
            else:
                last_text = extract_text_content(last.content)
                current_text = extract_text_content(msg.content)
                last.content = f"{last_text}\n{current_text}"
            
            # Объединяем tool_calls для assistant сообщений
            # Критично: без этого теряются tool_calls из второго и последующих сообщений,
            # что приводит к ошибке 400 от Kiro API (toolResult без соответствующего toolUse)
            if msg.role == "assistant" and msg.tool_calls:
                if last.tool_calls is None:
                    last.tool_calls = []
                last.tool_calls = list(last.tool_calls) + list(msg.tool_calls)
                logger.debug(f"Merged tool_calls: added {len(msg.tool_calls)} tool calls, total now: {len(last.tool_calls)}")
            
            logger.debug(f"Merged adjacent messages with role {msg.role}")
        else:
            merged.append(msg)
    
    return merged


def build_kiro_history(messages: List[ChatMessage], model_id: str) -> List[Dict[str, Any]]:
    """
    Строит массив history для Kiro API из OpenAI messages.
    
    Kiro API ожидает чередование userInputMessage и assistantResponseMessage.
    Эта функция преобразует OpenAI формат в Kiro формат.
    
    Args:
        messages: Список сообщений в формате OpenAI
        model_id: Внутренний ID модели Kiro
    
    Returns:
        Список словарей для поля history в Kiro API
    
    Example:
        >>> msgs = [ChatMessage(role="user", content="Hello")]
        >>> history = build_kiro_history(msgs, "claude-sonnet-4")
        >>> history[0]["userInputMessage"]["content"]
        'Hello'
    """
    history = []
    
    for msg in messages:
        if msg.role == "user":
            content = extract_text_content(msg.content)
            
            user_input = {
                "content": content,
                "modelId": model_id,
                "origin": "AI_EDITOR",
            }
            
            # Обработка tool_results (ответы на tool calls)
            tool_results = _extract_tool_results(msg.content)
            if tool_results:
                user_input["userInputMessageContext"] = {"toolResults": tool_results}
            
            history.append({"userInputMessage": user_input})
            
        elif msg.role == "assistant":
            content = extract_text_content(msg.content)
            
            assistant_response = {"content": content}
            
            # Обработка tool_calls
            tool_uses = _extract_tool_uses(msg)
            if tool_uses:
                assistant_response["toolUses"] = tool_uses
            
            history.append({"assistantResponseMessage": assistant_response})
            
        elif msg.role == "system":
            # System prompt обрабатывается отдельно в build_kiro_payload
            pass
    
    return history


def _extract_tool_results(content: Any) -> List[Dict[str, Any]]:
    """
    Извлекает tool results из контента сообщения.
    
    Args:
        content: Контент сообщения (может быть списком)
    
    Returns:
        Список tool results в формате Kiro
    """
    tool_results = []
    
    if isinstance(content, list):
        for item in content:
            if isinstance(item, dict) and item.get("type") == "tool_result":
                tool_results.append({
                    "content": [{"text": extract_text_content(item.get("content", ""))}],
                    "status": "success",
                    "toolUseId": item.get("tool_use_id", "")
                })
    
    return tool_results


def process_tools_with_long_descriptions(
    tools: Optional[List[Tool]]
) -> Tuple[Optional[List[Tool]], str]:
    """
    Обрабатывает tools с длинными descriptions.
    
    Kiro API имеет ограничение на длину description в toolSpecification.
    Если description превышает лимит, полное описание переносится в system prompt,
    а в tool остаётся ссылка на документацию.
    
    Args:
        tools: Список инструментов из запроса OpenAI
    
    Returns:
        Tuple из:
        - Список tools с обработанными descriptions (или None если tools пуст)
        - Строка с документацией для добавления в system prompt (пустая если все descriptions короткие)
    
    Example:
        >>> tools = [Tool(type="function", function=ToolFunction(name="bash", description="Very long..."))]
        >>> processed_tools, doc = process_tools_with_long_descriptions(tools)
        >>> "## Tool: bash" in doc
        True
    """
    if not tools:
        return None, ""
    
    # Если лимит отключен (0), возвращаем tools без изменений
    if TOOL_DESCRIPTION_MAX_LENGTH <= 0:
        return tools, ""
    
    tool_documentation_parts = []
    processed_tools = []
    
    for tool in tools:
        if tool.type != "function":
            processed_tools.append(tool)
            continue
        
        description = tool.function.description or ""
        
        if len(description) <= TOOL_DESCRIPTION_MAX_LENGTH:
            # Description короткий - оставляем как есть
            processed_tools.append(tool)
        else:
            # Description слишком длинный - переносим в system prompt
            tool_name = tool.function.name
            
            logger.debug(
                f"Tool '{tool_name}' has long description ({len(description)} chars > {TOOL_DESCRIPTION_MAX_LENGTH}), "
                f"moving to system prompt"
            )
            
            # Создаём документацию для system prompt
            tool_documentation_parts.append(f"## Tool: {tool_name}\n\n{description}")
            
            # Создаём копию tool с reference description
            # Используем модель Tool для создания новой копии
            from kiro_gateway.models import ToolFunction
            
            reference_description = f"[Full documentation in system prompt under '## Tool: {tool_name}']"
            
            processed_tool = Tool(
                type=tool.type,
                function=ToolFunction(
                    name=tool.function.name,
                    description=reference_description,
                    parameters=tool.function.parameters
                )
            )
            processed_tools.append(processed_tool)
    
    # Формируем итоговую документацию
    tool_documentation = ""
    if tool_documentation_parts:
        tool_documentation = (
            "\n\n---\n"
            "# Tool Documentation\n"
            "The following tools have detailed documentation that couldn't fit in the tool definition.\n\n"
            + "\n\n---\n\n".join(tool_documentation_parts)
        )
    
    return processed_tools if processed_tools else None, tool_documentation


def _extract_tool_uses(msg: ChatMessage) -> List[Dict[str, Any]]:
    """
    Извлекает tool uses из сообщения assistant.
    
    Args:
        msg: Сообщение assistant
    
    Returns:
        Список tool uses в формате Kiro
    """
    tool_uses = []
    
    # Из поля tool_calls
    if msg.tool_calls:
        for tc in msg.tool_calls:
            if isinstance(tc, dict):
                tool_uses.append({
                    "name": tc.get("function", {}).get("name", ""),
                    "input": json.loads(tc.get("function", {}).get("arguments", "{}")),
                    "toolUseId": tc.get("id", "")
                })
    
    # Из content (если там есть tool_use)
    if isinstance(msg.content, list):
        for item in msg.content:
            if isinstance(item, dict) and item.get("type") == "tool_use":
                tool_uses.append({
                    "name": item.get("name", ""),
                    "input": item.get("input", {}),
                    "toolUseId": item.get("id", "")
                })
    
    return tool_uses


def _extract_system_and_tool_docs(
    messages: List[ChatMessage],
    tools: Optional[List[Tool]]
) -> Tuple[str, List[ChatMessage], Optional[List[Tool]]]:
    """
    提取 system prompt 和 tool 文档。

    Args:
        messages: 消息列表
        tools: 工具列表

    Returns:
        (system_prompt, non_system_messages, processed_tools)
    """
    # 处理 tools 中的长 descriptions
    processed_tools, tool_documentation = process_tools_with_long_descriptions(tools)

    # 提取 system prompt
    system_prompt = ""
    non_system_messages = []
    for msg in messages:
        if msg.role == "system":
            system_prompt += extract_text_content(msg.content) + "\n"
        else:
            non_system_messages.append(msg)
    system_prompt = system_prompt.strip()

    # 添加 tool 文档到 system prompt
    if tool_documentation:
        system_prompt = system_prompt + tool_documentation if system_prompt else tool_documentation.strip()

    return system_prompt, non_system_messages, processed_tools


def build_kiro_payload(
    request_data: ChatCompletionRequest,
    conversation_id: str,
    profile_arn: str
) -> dict:
    """
    Строит полный payload для Kiro API.
    
    Включает:
    - Полную историю сообщений
    - System prompt (добавляется к первому user сообщению)
    - Tools definitions (с обработкой длинных descriptions)
    - Текущее сообщение
    
    Если tools содержат слишком длинные descriptions, они автоматически
    переносятся в system prompt, а в tool остаётся ссылка на документацию.
    
    Args:
        request_data: Запрос в формате OpenAI
        conversation_id: Уникальный ID разговора
        profile_arn: ARN профиля AWS CodeWhisperer
    
    Returns:
        Словарь payload для POST запроса к Kiro API
    
    Raises:
        ValueError: Если нет сообщений для отправки
    """
    messages = list(request_data.messages)

    # 使用辅助函数提取 system prompt 和处理 tools（代码简化）
    system_prompt, non_system_messages, processed_tools = _extract_system_and_tool_docs(
        messages, request_data.tools
    )

    # Объединяем соседние сообщения с одинаковой ролью
    merged_messages = merge_adjacent_messages(non_system_messages)
    
    if not merged_messages:
        raise ValueError("没有可发送的消息")
    
    # Получаем внутренний ID модели
    model_id = get_internal_model_id(request_data.model)
    
    # Строим историю (все сообщения кроме последнего)
    history_messages = merged_messages[:-1] if len(merged_messages) > 1 else []
    
    # Если есть system prompt, добавляем его к первому user сообщению в истории
    if system_prompt and history_messages:
        first_msg = history_messages[0]
        if first_msg.role == "user":
            original_content = extract_text_content(first_msg.content)
            first_msg.content = f"{system_prompt}\n\n{original_content}"
    
    history = build_kiro_history(history_messages, model_id)
    
    # Текущее сообщение (последнее)
    current_message = merged_messages[-1]
    current_content = extract_text_content(current_message.content)
    
    # Если system prompt есть, но история пуста - добавляем к текущему сообщению
    if system_prompt and not history:
        current_content = f"{system_prompt}\n\n{current_content}"
    
    # Если текущее сообщение - assistant, нужно добавить его в историю
    # и создать user сообщение "Continue"
    if current_message.role == "assistant":
        history.append({
            "assistantResponseMessage": {
                "content": current_content
            }
        })
        current_content = "Continue"
    
    # Если контент пустой
    if not current_content:
        current_content = "Continue"
    
    # Строим userInputMessage
    user_input_message = {
        "content": current_content,
        "modelId": model_id,
        "origin": "AI_EDITOR",
    }
    
    # Добавляем tools и tool_results если есть
    # Используем обработанные tools (с короткими descriptions)
    user_input_context = _build_user_input_context(request_data, current_message, processed_tools)
    if user_input_context:
        user_input_message["userInputMessageContext"] = user_input_context
    
    # Собираем финальный payload
    payload = {
        "conversationState": {
            "chatTriggerType": "MANUAL",
            "conversationId": conversation_id,
            "currentMessage": {
                "userInputMessage": user_input_message
            }
        }
    }
    
    # Добавляем историю только если она не пуста
    if history:
        payload["conversationState"]["history"] = history
    
    # Добавляем profileArn
    if profile_arn:
        payload["profileArn"] = profile_arn
    
    return payload


def _build_user_input_context(
    request_data: ChatCompletionRequest,
    current_message: ChatMessage,
    processed_tools: Optional[List[Tool]] = None
) -> Dict[str, Any]:
    """
    Строит userInputMessageContext для текущего сообщения.
    
    Включает tools definitions и tool_results.
    
    Args:
        request_data: Запрос с tools
        current_message: Текущее сообщение
        processed_tools: Обработанные tools с короткими descriptions (опционально).
                        Если None, используются tools из request_data.
    
    Returns:
        Словарь с контекстом или пустой словарь
    """
    context = {}
    
    # Используем обработанные tools если переданы, иначе оригинальные
    tools_to_use = processed_tools if processed_tools is not None else request_data.tools
    
    # Добавляем tools если есть
    if tools_to_use:
        tools_list = []
        for tool in tools_to_use:
            if tool.type == "function":
                tools_list.append({
                    "toolSpecification": {
                        "name": tool.function.name,
                        "description": tool.function.description or "",
                        "inputSchema": {"json": tool.function.parameters or {}}
                    }
                })
        if tools_list:
            context["tools"] = tools_list
    
    # Обработка tool_results в текущем сообщении
    tool_results = _extract_tool_results(current_message.content)
    if tool_results:
        context["toolResults"] = tool_results

    return context


# ==================================================================================================
# Anthropic -> OpenAI Conversion Functions
# ==================================================================================================

def convert_anthropic_tools_to_openai(tools: Optional[List[AnthropicTool]]) -> Optional[List[Tool]]:
    """
    Преобразует Anthropic tools в формат OpenAI.

    Anthropic использует input_schema, OpenAI использует parameters.

    Args:
        tools: Список инструментов в формате Anthropic

    Returns:
        Список инструментов в формате OpenAI или None
    """
    if not tools:
        return None

    openai_tools = []
    for tool in tools:
        openai_tool = Tool(
            type="function",
            function=ToolFunction(
                name=tool.name,
                description=tool.description,
                parameters=tool.input_schema
            )
        )
        openai_tools.append(openai_tool)

    return openai_tools


def _extract_anthropic_system_prompt(system: Optional[Any]) -> str:
    """
    Извлекает системный промпт из Anthropic формата.

    Args:
        system: Системный промпт (строка или список блоков)

    Returns:
        Системный промпт в виде строки
    """
    if system is None:
        return ""

    if isinstance(system, str):
        return system

    if isinstance(system, list):
        text_parts = []
        for block in system:
            if isinstance(block, dict) and block.get("type") == "text":
                text_parts.append(block.get("text", ""))
        return "\n".join(text_parts)

    return str(system)


def _convert_anthropic_content_to_openai(
    content: Any,
    role: str
) -> Tuple[Optional[str], Optional[List[Dict[str, Any]]], Optional[str]]:
    """
    Преобразует Anthropic content в формат OpenAI.

    Args:
        content: Content в формате Anthropic (строка или список блоков)
        role: Роль сообщения (user или assistant)

    Returns:
        Tuple из (text_content, tool_calls, tool_call_id)
    """
    if isinstance(content, str):
        return content, None, None

    if not isinstance(content, list):
        return str(content) if content else None, None, None

    text_parts = []
    tool_calls = []
    tool_results = []

    for block in content:
        if isinstance(block, dict):
            block_type = block.get("type")

            if block_type == "text":
                text_parts.append(block.get("text", ""))

            elif block_type == "image":
                # Image content - для Kiro нужно будет обработать отдельно
                # Пока добавляем placeholder
                source = block.get("source", {})
                if source.get("type") == "base64":
                    text_parts.append(f"[Image: {source.get('media_type', 'image')}]")
                elif source.get("type") == "url":
                    text_parts.append(f"[Image URL: {source.get('url', '')}]")

            elif block_type == "tool_use":
                # Assistant's tool call
                tool_call = {
                    "id": block.get("id", ""),
                    "type": "function",
                    "function": {
                        "name": block.get("name", ""),
                        "arguments": json.dumps(block.get("input", {}))
                    }
                }
                tool_calls.append(tool_call)

            elif block_type == "tool_result":
                # User's tool result
                tool_result = {
                    "type": "tool_result",
                    "tool_use_id": block.get("tool_use_id", ""),
                    "content": _extract_tool_result_content(block.get("content")),
                    "is_error": block.get("is_error", False)
                }
                tool_results.append(tool_result)

            elif block_type == "thinking":
                # Thinking block - добавляем в текст с пометкой
                thinking_text = block.get("thinking", "")
                if thinking_text:
                    text_parts.append(f"<thinking>{thinking_text}</thinking>")

        elif isinstance(block, AnthropicContentBlock):
            # Pydantic model
            if block.type == "text":
                text_parts.append(block.text or "")
            elif block.type == "tool_use":
                tool_call = {
                    "id": block.id or "",
                    "type": "function",
                    "function": {
                        "name": block.name or "",
                        "arguments": json.dumps(block.input or {})
                    }
                }
                tool_calls.append(tool_call)
            elif block.type == "tool_result":
                tool_result = {
                    "type": "tool_result",
                    "tool_use_id": block.tool_use_id or "",
                    "content": _extract_tool_result_content(block.content),
                    "is_error": block.is_error or False
                }
                tool_results.append(tool_result)

    text_content = "\n".join(text_parts) if text_parts else None

    # Если есть tool_results, возвращаем их как content (для обработки в merge_adjacent_messages)
    if tool_results:
        return tool_results, None, None

    return text_content, tool_calls if tool_calls else None, None


def _extract_tool_result_content(content: Any) -> str:
    """
    Извлекает текстовое содержимое из tool_result.

    Args:
        content: Content tool_result (строка или список блоков)

    Returns:
        Текстовое содержимое
    """
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        text_parts = []
        for item in content:
            if isinstance(item, dict) and item.get("type") == "text":
                text_parts.append(item.get("text", ""))
            elif isinstance(item, str):
                text_parts.append(item)
        return "\n".join(text_parts)
    return str(content)


def convert_anthropic_messages_to_openai(
    messages: List[AnthropicMessage],
    system: Optional[Any] = None
) -> List[ChatMessage]:
    """
    Преобразует Anthropic messages в формат OpenAI.

    Args:
        messages: Список сообщений в формате Anthropic
        system: Системный промпт (опционально)

    Returns:
        Список сообщений в формате OpenAI
    """
    openai_messages = []

    # Добавляем системный промпт если есть
    system_prompt = _extract_anthropic_system_prompt(system)
    if system_prompt:
        openai_messages.append(ChatMessage(role="system", content=system_prompt))

    for msg in messages:
        role = msg.role
        content, tool_calls, _ = _convert_anthropic_content_to_openai(msg.content, role)

        # Если content - это tool_results, создаем user сообщение с ними
        if isinstance(content, list) and content and isinstance(content[0], dict) and content[0].get("type") == "tool_result":
            openai_messages.append(ChatMessage(
                role="user",
                content=content
            ))
        elif role == "assistant":
            openai_messages.append(ChatMessage(
                role="assistant",
                content=content or "",
                tool_calls=tool_calls
            ))
        else:
            openai_messages.append(ChatMessage(
                role="user",
                content=content or ""
            ))

    return openai_messages


def convert_anthropic_to_openai_request(
    anthropic_request: AnthropicMessagesRequest
) -> ChatCompletionRequest:
    """
    Преобразует Anthropic MessagesRequest в OpenAI ChatCompletionRequest.

    Args:
        anthropic_request: Запрос в формате Anthropic

    Returns:
        Запрос в формате OpenAI
    """
    # Конвертируем сообщения
    openai_messages = convert_anthropic_messages_to_openai(
        anthropic_request.messages,
        anthropic_request.system
    )

    # Конвертируем tools
    openai_tools = convert_anthropic_tools_to_openai(anthropic_request.tools)

    # Конвертируем tool_choice
    openai_tool_choice = None
    if anthropic_request.tool_choice:
        tc_type = anthropic_request.tool_choice.get("type")
        if tc_type == "auto":
            openai_tool_choice = "auto"
        elif tc_type == "any":
            openai_tool_choice = "required"
        elif tc_type == "tool":
            tool_name = anthropic_request.tool_choice.get("name")
            openai_tool_choice = {"type": "function", "function": {"name": tool_name}}
        elif tc_type == "none":
            openai_tool_choice = "none"

    # Конвертируем stop_sequences -> stop
    stop = anthropic_request.stop_sequences

    return ChatCompletionRequest(
        model=anthropic_request.model,
        messages=openai_messages,
        max_tokens=anthropic_request.max_tokens,
        temperature=anthropic_request.temperature,
        top_p=anthropic_request.top_p,
        stop=stop,
        tools=openai_tools,
        tool_choice=openai_tool_choice,
        stream=anthropic_request.stream
    )
