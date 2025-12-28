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
| **用户系统** | 支持 LinuxDo/GitHub OAuth2 登录 |
| **Token 捐献** | 用户可捐献 Token 共享使用 |
| **API Key 生成** | 生成 sk-xxx 格式的 API Key |
| **Admin 管理后台** | 用户管理、Token 池管理、IP 黑名单等 |
| **中文日志系统** | 完整的中文日志输出，含时间戳和用户信息 |
| **数据持久化** | 支持 Docker 卷和 Fly.io 持久卷 |
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

# 方式二: 直接运行（简单模式）
docker build -t kirogate .
docker run -d -p 8000:8000 \
  -e PROXY_API_KEY="your-password" \
  -e REFRESH_TOKEN="your-kiro-refresh-token" \
  --name kirogate kirogate

# 方式三: 组合模式（推荐 - 无需配置 REFRESH_TOKEN）
docker build -t kirogate .
docker run -d -p 8000:8000 \
  -e PROXY_API_KEY="your-password" \
  --name kirogate kirogate
# 用户在请求中传递 PROXY_API_KEY:REFRESH_TOKEN

# 查看日志
docker logs -f kirogate
```

### Fly.io 部署

```bash
# 1. 安装 Fly CLI
curl -L https://fly.io/install.sh | sh

# 2. 登录
fly auth login

# 3. 创建应用（首次）
fly apps create kirogate

# 4. 创建持久卷（重要！确保数据不丢失）
fly volumes create kirogate_data --region nrt --size 1

# 5. 设置 Secrets（环境变量）
fly secrets set PROXY_API_KEY="your-password"
fly secrets set ADMIN_PASSWORD="your-admin-password"
fly secrets set ADMIN_SECRET_KEY="your-random-secret"
# 可选：OAuth2 配置
fly secrets set OAUTH_CLIENT_ID="..."
fly secrets set OAUTH_CLIENT_SECRET="..."

# 6. 部署
fly deploy

# 7. 查看状态
fly status
fly logs
```

### 数据持久化

**⚠️ 重要**: 用户数据（数据库）需要持久化存储，否则每次部署会丢失数据。

#### Docker Compose（已配置）

`docker-compose.yml` 默认使用 Docker 命名卷：

```yaml
volumes:
  - kirogate_data:/app/data   # 用户数据库持久化
```

**注意事项：**
- ✅ `docker-compose down` — 保留数据
- ❌ `docker-compose down -v` — 删除数据卷（数据丢失）

#### Fly.io（需手动创建卷）

`fly.toml` 已配置挂载点，但需要先创建卷：

```bash
# 查看现有卷
fly volumes list

# 创建卷（如果不存在）
fly volumes create kirogate_data --region nrt --size 1
```

#### 手动 Docker 运行

```bash
docker run -d -p 8000:8000 \
  -v kirogate_data:/app/data \  # 关键：挂载数据卷
  -e PROXY_API_KEY="your-password" \
  --name kirogate kirogate
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
# 必填：代理服务器密码（用于验证客户端请求）
PROXY_API_KEY="my-super-secret-password-123"

# 可选：全局 REFRESH_TOKEN（仅简单模式需要）
# 如果使用组合模式（PROXY_API_KEY:REFRESH_TOKEN），可以不配置此项
REFRESH_TOKEN="你的kiro_refresh_token"

# 可选：其他配置
PROFILE_ARN="arn:aws:codewhisperer:us-east-1:..."
KIRO_REGION="us-east-1"
```

**配置说明：**
- **简单模式**：必须配置 `REFRESH_TOKEN` 环境变量
- **组合模式**：无需配置 `REFRESH_TOKEN`，用户在请求中直接传递

### 超时配置

对于 `claude-opus-4-5` 等响应较慢的模型，可以调整超时设置：

```env
# 首个 token 超时（秒）- 等待模型开始响应的时间
# 对于 Opus 等慢模型，建议 60-120 秒
FIRST_TOKEN_TIMEOUT="60"

# 首个 token 超时重试次数
FIRST_TOKEN_MAX_RETRIES="5"

# 流式读取超时（秒）- 读取流中每个 chunk 的最大等待时间
# 对于 Opus 等慢模型，建议 120-300 秒
STREAM_READ_TIMEOUT="120"

# 非流式请求超时（秒）- 等待完整响应的最大时间
# 对于复杂请求，建议 300-600 秒
NON_STREAM_TIMEOUT="600"
```

### 获取 Refresh Token

#### 推荐方式：使用 Kiro Account Manager ✨

使用 [Kiro Account Manager](https://github.com/chaogei/Kiro-account-manager) 可以轻松管理和获取 Refresh Token，无需手动抓包。

#### 手动方式：抓包获取

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

支持两种认证模式，每种模式都兼容 OpenAI 和 Anthropic 格式：

#### 模式 1: 简单模式（使用服务器配置的 REFRESH_TOKEN）

| API 格式 | 请求头 | 格式 |
|---------|--------|------|
| OpenAI | `Authorization` | `Bearer {PROXY_API_KEY}` |
| Anthropic | `x-api-key` | `{PROXY_API_KEY}` |

#### 模式 2: 组合模式（用户自带 REFRESH_TOKEN）✨ 推荐

| API 格式 | 请求头 | 格式 |
|---------|--------|------|
| OpenAI | `Authorization` | `Bearer {PROXY_API_KEY}:{REFRESH_TOKEN}` |
| Anthropic | `x-api-key` | `{PROXY_API_KEY}:{REFRESH_TOKEN}` |

**核心优势：**
- 🚀 **无需配置环境变量**：REFRESH_TOKEN 直接在请求中传递，服务器无需配置 `REFRESH_TOKEN` 环境变量
- 👥 **多租户支持**：每个用户使用自己的 REFRESH_TOKEN，多用户共享同一网关实例
- 🔒 **安全隔离**：每个用户的认证信息独立管理，互不影响
- ⚡ **缓存优化**：认证信息自动缓存（Python/Deno: 最多100个用户），提升性能

**优先级说明：**
- ✅ **优先使用组合模式**：如果 API Key 包含冒号 `:`，自动识别为 `PROXY_API_KEY:REFRESH_TOKEN` 格式
- ✅ **回退到简单模式**：如果不包含冒号，使用服务器配置的全局 REFRESH_TOKEN

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
<summary>🔹 cURL 请求（简单模式）</summary>

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
<summary>🔹 cURL 请求（组合模式 - 推荐）</summary>

```bash
curl http://localhost:8000/v1/chat/completions \
  -H "Authorization: Bearer my-proxy-key:eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claude-sonnet-4-5",
    "messages": [{"role": "user", "content": "你好！"}],
    "stream": true
  }'
```

</details>

<details>
<summary>🐍 Python OpenAI SDK（简单模式）</summary>

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
<summary>🐍 Python OpenAI SDK（组合模式 - 推荐）</summary>

```python
from openai import OpenAI

# 组合模式：PROXY_API_KEY:REFRESH_TOKEN
client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="my-proxy-key:eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
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
<summary>🤖 Claude Code CLI（简单模式）</summary>

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
<summary>🤖 Claude Code CLI（组合模式 - 推荐）</summary>

配置 Claude Code CLI 使用你的网关（多租户模式）:

```bash
# 设置环境变量（组合格式）
export ANTHROPIC_BASE_URL="http://localhost:8000"
export ANTHROPIC_API_KEY="my-proxy-key:eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# 或者在 Claude Code 设置中配置
claude config set --global apiBaseUrl "http://localhost:8000"
claude config set --global apiKey "my-proxy-key:eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**优势：**
- ✅ 无需在服务器配置 REFRESH_TOKEN
- ✅ 每个用户使用自己的 REFRESH_TOKEN
- ✅ 支持多用户共享同一个网关实例

</details>

<details>
<summary>🐍 Anthropic Python SDK（简单模式）</summary>

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
<summary>🐍 Anthropic Python SDK（组合模式 - 推荐）</summary>

```python
from anthropic import Anthropic

# 组合模式：PROXY_API_KEY:REFRESH_TOKEN
client = Anthropic(
    base_url="http://localhost:8000",
    api_key="my-proxy-key:eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
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
<summary>🔹 Anthropic cURL 请求（简单模式）</summary>

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

<details>
<summary>🔹 Anthropic cURL 请求（组合模式 - 推荐）</summary>

```bash
curl http://localhost:8000/v1/messages \
  -H "x-api-key: my-proxy-key:eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
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
│   ├── routes.py              # FastAPI 路由
│   ├── pages.py               # HTML 页面渲染
│   ├── database.py            # 用户系统数据库
│   ├── user_manager.py        # 用户管理和 OAuth2
│   ├── token_allocator.py     # Token 智能分配
│   └── health_checker.py      # Token 健康检查
│
├── data/                      # 数据目录（自动创建）
│   └── users.db               # 用户数据库
│
├── tests/                     # 测试
│   ├── unit/                  # 单元测试
│   └── integration/           # 集成测试
│
└── debug_logs/                # 调试日志（启用时生成）
```

---

## 🛡️ Admin 管理后台

KiroGate 提供了一个隐藏的管理后台，用于监控和管理服务。

### 访问方式

```
/admin/login  → 登录页面
/admin        → 管理面板（需登录）
/admin/logout → 退出登录
```

> **注意**: Admin 页面不会显示在导航菜单和 Swagger 文档中。

### 功能列表

| 功能 | 说明 |
|------|------|
| 📊 **概览面板** | 站点状态、Token 状态、总请求数、成功率、平均延迟 |
| 👥 **用户管理** | 查看所有用户、搜索/排序/分页、封禁/解封用户 |
| 🎁 **Token 池管理** | 管理捐献的 Token、切换可见性、查看成功率 |
| 🌐 **IP 统计** | 请求来源 IP、请求次数、最后访问时间 |
| 🚫 **黑名单管理** | 封禁/解封 IP 地址 |
| 🔑 **缓存管理** | 查看和清理缓存的用户 Token |
| ⚙️ **系统控制** | 站点开关、刷新 Token、清除缓存 |

### 配置

在 `.env` 文件中配置：

```env
# 管理员密码（请在生产环境中设置强密码！）
ADMIN_PASSWORD="your-secure-password"

# Session 签名密钥（请使用随机字符串）
ADMIN_SECRET_KEY="your-random-secret-key"

# Session 有效期（秒），默认 24 小时
ADMIN_SESSION_MAX_AGE=86400
```

### Docker 部署

```bash
docker run -d -p 8000:8000 \
  -e PROXY_API_KEY="your-password" \
  -e ADMIN_PASSWORD="your-admin-password" \
  -e ADMIN_SECRET_KEY="your-random-secret" \
  -v kirogate_data:/app/data \
  --name kirogate kirogate
```

---

## 👥 用户系统

KiroGate 支持用户注册登录，用户可以捐献 Token 并生成自己的 API Key。

### 登录方式

支持两种 OAuth2 登录方式：

| 提供商 | 配置 | 获取地址 |
|--------|------|----------|
| **LinuxDo** | `OAUTH_CLIENT_ID`, `OAUTH_CLIENT_SECRET` | https://connect.linux.do |
| **GitHub** | `GITHUB_CLIENT_ID`, `GITHUB_CLIENT_SECRET` | https://github.com/settings/developers |

### 功能说明

| 功能 | 说明 |
|------|------|
| 🔐 **多方式登录** | 支持 LinuxDo 和 GitHub OAuth2 登录 |
| 🎁 **Token 捐献** | 用户可捐献 Refresh Token，选择公开或私有 |
| 🔑 **API Key 生成** | 生成 `sk-xxx` 格式的 API Key |
| 📊 **使用统计** | 查看 Token 成功率和使用次数 |
| 🌐 **公开 Token 池** | 公开的 Token 供所有用户共享使用 |

### 配置示例

```env
# LinuxDo OAuth2
OAUTH_CLIENT_ID="your-linuxdo-client-id"
OAUTH_CLIENT_SECRET="your-linuxdo-client-secret"
OAUTH_REDIRECT_URI="https://your-domain.com/oauth2/callback"

# GitHub OAuth2
GITHUB_CLIENT_ID="your-github-client-id"
GITHUB_CLIENT_SECRET="your-github-client-secret"
GITHUB_REDIRECT_URI="https://your-domain.com/oauth2/github/callback"

# 用户系统安全配置
USER_SESSION_SECRET="your-random-secret-key"
TOKEN_ENCRYPT_KEY="your-32-byte-encrypt-key-here!!"
```

### 用户端点

| 端点 | 说明 |
|------|------|
| `/login` | 登录选择页面 |
| `/user` | 用户中心（Token 管理、API Key 管理） |
| `/tokens` | 公开 Token 池 |
| `/oauth2/logout` | 退出登录 |

### 使用 API Key

用户生成的 `sk-xxx` 格式 API Key 可直接用于 API 调用：

```bash
# OpenAI 格式
curl http://localhost:8000/v1/chat/completions \
  -H "Authorization: Bearer sk-your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"model": "claude-sonnet-4-5", "messages": [{"role": "user", "content": "你好"}]}'

# Anthropic 格式
curl http://localhost:8000/v1/messages \
  -H "x-api-key: sk-your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"model": "claude-sonnet-4-5", "max_tokens": 1024, "messages": [{"role": "user", "content": "你好"}]}'
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
