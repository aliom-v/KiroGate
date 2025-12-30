# 用户端接入功能

本文档汇总 KiroGate 的用户端接入方式、入口与相关功能，便于统一对外说明与排查问题。

## 登录与注册

### 登录方式

- 邮箱 + 密码登录
- LinuxDo OAuth2 登录
- GitHub OAuth2 登录

### 注册方式

- 邮箱 + 密码注册

### 审核机制

- 默认需要管理员审核通过才可登录
- 管理端可关闭“注册审核”开关，关闭后新注册可直接登录
- 审核状态：
  - pending：待审核
  - approved：已通过
  - rejected：已拒绝

### 自用模式影响

- 自用模式开启时，禁止新注册
- 自用模式开启时，已注册用户仍可登录

## 用户中心功能

### Token 管理

- 添加 Refresh Token
- 支持公开/私有可见性
- 查看 Token 状态与使用情况

### API Key 管理

- 生成 `sk-xxx` 格式 API Key
- 启用/禁用 API Key
- 删除 API Key

### 公开 Token 池

- 浏览公开 Token 池
- 根据筛选/排序查看公开 Token

## 相关入口

### 页面入口

- `/login`：登录/注册页面
- `/user`：用户中心
- `/tokens`：公开 Token 池
- `/oauth2/logout`：退出登录

### 表单与认证接口

- `POST /auth/login`：邮箱登录
- `POST /auth/register`：邮箱注册
- `GET /oauth2/login`：LinuxDo OAuth2 登录入口
- `GET /oauth2/callback`：LinuxDo OAuth2 回调
- `GET /oauth2/github/login`：GitHub OAuth2 登录入口
- `GET /oauth2/github/callback`：GitHub OAuth2 回调

## 访问控制与拦截逻辑

- 被封禁用户无法登录
- 待审核/已拒绝用户无法登录
- 自用模式下禁止新注册

## 账号数据说明

- 用户邮箱为唯一标识之一（email 唯一）
- 密码使用 PBKDF2 进行安全存储
- 登录会写入最近登录时间

