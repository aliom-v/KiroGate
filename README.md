<div align="center">

# KiroGate

**OpenAI & Anthropic 兼容的 Kiro IDE API 代理网关**

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)

*通过任何支持 OpenAI 或 Anthropic API 的工具使用 Claude 模型*

[功能特性](#-功能特性) • [快速开始](#-快速开始) • [配置说明](#%EF%B8%8F-配置说明) • [API 参考](#-api-参考) • [许可证](#-许可证)

</div>

---

> **致谢**: 本项目基于 [kiro-openai-gateway](https://github.com/Jwadow/kiro-openai-gateway) by [@Jwadow](https://github.com/jwadow) 开发

---

## ✨ 功能特性

| 功能 | 说明 |
|------|------|
| **OpenAI 兼容 API** | 支持任何 OpenAI 客户端开箱即用 |
| **Anthropic 兼容 API** | 支持 Claude Code CLI 和 Anthropic SDK |
| **完整消息历史** | 传递完整的对话上下文 |
| **工具调用** | 支持 OpenAI 和 Anthropic 格式的 Function Calling |
| **流式传输** | 完整的 SSE 流式传输支持 |
| **自动重试** | 遇到错误时自动重试 (403, 429, 5xx) |
| **多模型支持** | 支持多种 Claude 模型版本 |
| **智能 Token 管理** | 自动在过期前刷新凭证 |
| **模块化架构** | 易于扩展新的提供商 |

---

## 🚀 快速开始

### 环境要求

- Python 3.10+
- [Kiro IDE](https://kiro.dev/) 并已登录账号

### 安装步骤

```bash
# 克隆仓库
git clone https://github.com/aliom-v/KiroGate.git
cd KiroGate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 填写你的凭证

# 启动服务器
python main.py
```

服务器将在 `http://localhost:8000` 启动

### Docker 部署

```bash
# 方式一: 使用 docker-compose（推荐）
cp .env.example .env
# 编辑 .env 填写你的凭证
docker-compose up -d

# 方式二: 直接运行
docker build -t kirogate .
docker run -d -p 8000:8000 \
  -e PROXY_API_KEY="your-password" \
  -e REFRESH_TOKEN="your-kiro-refresh-token" \
  --name kirogate kirogate

# 查看日志
docker logs -f kirogate
```

---

## ⚙️ 配置说明

### 方式一: JSON 凭证文件（推荐）

在 `.env` 中指定凭证文件路径或远程 URL:

```env
# 本地文件
KIRO_CREDS_FILE="~/.aws/sso/cache/kiro-auth-token.json"

# 或远程 URL
KIRO_CREDS_FILE="https://example.com/kiro-credentials.json"

# 用于保护你的代理服务器的密码（自己设置一个安全的字符串）
# 连接网关时需要使用这个密码作为 api_key
PROXY_API_KEY="my-super-secret-password-123"
```

<details>
<summary>📄 JSON 文件格式</summary>

```json
{
  "accessToken": "eyJ...",
  "refreshToken": "eyJ...",
  "expiresAt": "2025-01-12T23:00:00.000Z",
  "profileArn": "arn:aws:codewhisperer:us-east-1:...",
  "region": "us-east-1"
}
```

</details>

### 方式二: 环境变量

在项目根目录创建 `.env` 文件:

```env
# 必填
REFRESH_TOKEN="你的kiro_refresh_token"

# 代理服务器密码
PROXY_API_KEY="my-super-secret-password-123"

# 可选
PROFILE_ARN="arn:aws:codewhisperer:us-east-1:..."
KIRO_REGION="us-east-1"
```

### 获取 Refresh Token

可以通过拦截 Kiro IDE 流量获取 refresh token。查找发往以下地址的请求:
- `prod.us-east-1.auth.desktop.kiro.dev/refreshToken`

---

## 📡 API 参考

### 端点列表

| 端点 | 方法 | 说明 |
|------|------|------|
| `/` | GET | 健康检查 |
| `/health` | GET | 详细健康检查 |
| `/v1/models` | GET | 获取可用模型列表 |
| `/v1/chat/completions` | POST | OpenAI 兼容的聊天补全 |
| `/v1/messages` | POST | Anthropic 兼容的消息 API |

### 认证方式

两个端点都支持两种认证方式:

| 方式 | 请求头 | 格式 |
|------|--------|------|
| OpenAI 风格 | `Authorization` | `Bearer {PROXY_API_KEY}` |
| Anthropic 风格 | `x-api-key` | `{PROXY_API_KEY}` |

### 可用模型

| 模型 | 说明 |
|------|------|
| `claude-opus-4-5` | 顶级模型 |
| `claude-opus-4-5-20251101` | 顶级模型（版本号） |
| `claude-sonnet-4-5` | 增强模型 |
| `claude-sonnet-4-5-20250929` | 增强模型（版本号） |
| `claude-sonnet-4` | 均衡模型 |
| `claude-sonnet-4-20250514` | 均衡模型（版本号） |
| `claude-haiku-4-5` | 快速模型 |
| `claude-3-7-sonnet-20250219` | 旧版模型 |

---

## 💡 使用示例

### OpenAI API 格式

<details>
<summary>🔹 cURL 请求</summary>

```bash
curl http://localhost:8000/v1/chat/completions \
  -H "Authorization: Bearer my-super-secret-password-123" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claude-sonnet-4-5",
    "messages": [{"role": "user", "content": "你好！"}],
    "stream": true
  }'
```

</details>

<details>
<summary>🐍 Python OpenAI SDK</summary>

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="my-super-secret-password-123"  # 你的 PROXY_API_KEY
)

response = client.chat.completions.create(
    model="claude-sonnet-4-5",
    messages=[
        {"role": "system", "content": "你是一个有帮助的助手。"},
        {"role": "user", "content": "你好！"}
    ],
    stream=True
)

for chunk in response:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")
```

</details>

<details>
<summary>🦜 LangChain</summary>

```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    base_url="http://localhost:8000/v1",
    api_key="my-super-secret-password-123",
    model="claude-sonnet-4-5"
)

response = llm.invoke("你好，今天怎么样？")
print(response.content)
```

</details>

### Anthropic API 格式

<details>
<summary>🤖 Claude Code CLI</summary>

配置 Claude Code CLI 使用你的网关:

```bash
# 设置环境变量
export ANTHROPIC_BASE_URL="http://localhost:8000"
export ANTHROPIC_API_KEY="my-super-secret-password-123"  # 你的 PROXY_API_KEY

# 或者在 Claude Code 设置中配置
claude config set --global apiBaseUrl "http://localhost:8000"
```

</details>

<details>
<summary>🐍 Anthropic Python SDK</summary>

```python
from anthropic import Anthropic

client = Anthropic(
    base_url="http://localhost:8000",
    api_key="my-super-secret-password-123"  # 你的 PROXY_API_KEY
)

# 非流式
message = client.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=1024,
    messages=[
        {"role": "user", "content": "你好，Claude！"}
    ]
)
print(message.content[0].text)

# 流式
with client.messages.stream(
    model="claude-sonnet-4-5",
    max_tokens=1024,
    messages=[{"role": "user", "content": "你好！"}]
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)
```

</details>

<details>
<summary>🔹 Anthropic cURL 请求</summary>

```bash
curl http://localhost:8000/v1/messages \
  -H "x-api-key: my-super-secret-password-123" \
  -H "anthropic-version: 2023-06-01" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claude-sonnet-4-5",
    "max_tokens": 1024,
    "messages": [{"role": "user", "content": "你好！"}]
  }'
```

</details>

---

## 📁 项目结构

```
kiro-bridge/
├── main.py                    # 入口点，FastAPI 应用
├── requirements.txt           # Python 依赖
├── .env.example               # 环境配置示例
│
├── kiro_gateway/              # 主包
│   ├── __init__.py            # 包导出
│   ├── config.py              # 配置和常量
│   ├── models.py              # Pydantic 模型（OpenAI & Anthropic API）
│   ├── auth.py                # KiroAuthManager - Token 管理
│   ├── cache.py               # ModelInfoCache - 模型缓存
│   ├── utils.py               # 工具函数
│   ├── converters.py          # OpenAI/Anthropic <-> Kiro 格式转换
│   ├── parsers.py             # AWS SSE 流解析器
│   ├── streaming.py           # 响应流处理逻辑
│   ├── http_client.py         # HTTP 客户端（带重试逻辑）
│   ├── debug_logger.py        # 调试日志（可选）
│   └── routes.py              # FastAPI 路由
│
├── tests/                     # 测试
│   ├── unit/                  # 单元测试
│   └── integration/           # 集成测试
│
└── debug_logs/                # 调试日志（启用时生成）
```

---

## 🔧 调试

调试日志默认**禁用**。要启用，请在 `.env` 中添加:

```env
# 调试日志模式:
# - off: 禁用（默认）
# - errors: 仅保存失败请求的日志 (4xx, 5xx) - 推荐用于排查问题
# - all: 保存所有请求的日志（每次请求覆盖）
DEBUG_MODE=errors
```

### 调试模式

| 模式 | 说明 | 使用场景 |
|------|------|----------|
| `off` | 禁用（默认） | 生产环境 |
| `errors` | 仅保存失败请求的日志 | **推荐用于排查问题** |
| `all` | 保存所有请求的日志 | 开发/调试 |

### 调试文件

启用后，请求日志保存在 `debug_logs/` 文件夹:

| 文件 | 说明 |
|------|------|
| `request_body.json` | 客户端的请求（OpenAI 格式） |
| `kiro_request_body.json` | 发送给 Kiro API 的请求 |
| `response_stream_raw.txt` | Kiro 的原始响应流 |
| `response_stream_modified.txt` | 转换后的响应流 |
| `app_logs.txt` | 应用日志 |
| `error_info.json` | 错误详情（仅错误时） |

---

## 🧪 测试

```bash
# 运行所有测试
pytest

# 仅运行单元测试
pytest tests/unit/

# 带覆盖率运行
pytest --cov=kiro_gateway
```

---

## 📜 许可证

本项目采用 **GNU Affero General Public License v3.0 (AGPL-3.0)** 许可证。

这意味着:
- ✅ 你可以使用、修改和分发本软件
- ✅ 你可以用于商业目的
- ⚠️ 分发软件时**必须公开源代码**
- ⚠️ **网络使用视为分发** — 如果你运行修改版本的服务器并让他人与其交互，必须向他们提供源代码
- ⚠️ 修改后的版本必须使用相同的许可证

查看 [LICENSE](LICENSE) 文件了解完整的许可证文本。

---

## 🙏 致谢

本项目基于 [kiro-openai-gateway](https://github.com/Jwadow/kiro-openai-gateway) 开发，感谢原作者 [@Jwadow](https://github.com/jwadow) 的贡献。

---

## ⚠️ 免责声明

本项目与 Amazon Web Services (AWS)、Anthropic 或 Kiro IDE 没有任何关联、背书或赞助关系。使用时请自行承担风险，并遵守相关 API 的服务条款。

---

<div align="center">

**[⬆ 返回顶部](#kirogate)**

</div>
