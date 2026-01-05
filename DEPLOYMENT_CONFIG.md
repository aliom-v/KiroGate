# KiroGate 部署配置信息

## GitHub 仓库

### 私有开发仓库
- **仓库名**: `hj01857655/KiroGate_dev`
- **用途**: 源码开发，日常提交
- **地址**: https://github.com/hj01857655/KiroGate_dev

### 公开部署仓库
- **仓库名**: `hj01857655/KiroGate`
- **用途**: 自动部署，利用免费 Actions 额度
- **地址**: https://github.com/hj01857655/KiroGate

---

## GitHub Secrets 配置

以下 Secrets 已在两个仓库中设置：

| Secret Name | Value | 说明 |
|-------------|-------|------|
| `FLY_API_TOKEN` | `FlyV1 fm2_lJPECAAAAAAAEJufxBB+rzGO5VLC0UwvSbbAttMDwrVodHRwczovL2FwaS5mbHkuaW8vdjGUAJLOABWVaR8Lk7lodHRwczovL2FwaS5mbHkuaW8vYWFhL3YxxDz+87+pSnweUo3SCUH/EudsBuEqfjMWsx2rIx+q7wPjzZfUUyLxMauUitUCbZYXwVSPmFLLtst4aWy6vNnETgeAm+T+gWkOyCuIsX9Jp4ECCW5bRZ4TXfX2G1J3LmJfBPz4uAbUTlpYadwQCXjtQ9zVknvDGlCjKI8Q4mZkHJ1LJhmwGhD6bP13z3CA2sQguOzxSXuBG43CXaYgmKBdZRuHtmxVaF2joTmIWREgKX4=fm2_lJPETgeAm+T+gWkOyCuIsX9Jp4ECCW5bRZ4TXfX2G1J3LmJfBPz4uAbUTlpYadwQCXjtQ9zVknvDGlCjKI8Q4mZkHJ1LJhmwGhD6bP13z3CA2sQQhjZkwTjLdiYCX4nQC+K+X8O5aHR0cHM6Ly9hcGkuZmx5LmlvL2FhYS92MZgEks5pW58tzwAAAAElU71LF84AFLoCCpHOABS6AgzEEFJMOcOEQxOQJmiZYEotNVrEIP0b6ABIDLEJ/EmDi3lWBrv9/JLf0jvrnjMceNEYYD87` | Fly.io 部署凭证 |
| `PROXY_API_KEY` | `my-super-secret-password-123` | API 访问密码 |
| `ADMIN_PASSWORD` | `Kiro@2025` | 管理员密码 |
| `REFRESH_TOKEN` | `请在Kiro IDE中获取真实的REFRESH_TOKEN` | 需要你更新为真实值 |

---

## 本地环境变量 (.env)

```env
# API 配置
PROXY_API_KEY=my-super-secret-password-123
REFRESH_TOKEN=请在Kiro IDE中获取真实的REFRESH_TOKEN

# 管理员配置
ADMIN_PASSWORD=Kiro@2025
ADMIN_SECRET_KEY=your-secret-key-for-session-signing

# LinuxDo OAuth2 配置
LINUXDO_CLIENT_ID=hXYpS0rTn9EVSwG0Ya2aZGOAUftUuTy2
LINUXDO_CLIENT_SECRET=你的LinuxDo客户端密钥
LINUXDO_REDIRECT_URI=http://localhost:8000/auth/linuxdo/callback

# 数据库配置
USER_DB_FILE=data/users.db

# 服务配置
HOST=0.0.0.0
PORT=8000
DEBUG=false

# 可选配置
STATIC_ASSETS_PROXY_ENABLED=true
```

---

## Fly.io 应用配置

- **应用名**: `kirogate`
- **区域**: `nrt` (Tokyo)
- **内存**: 256MB
- **CPU**: 1 个共享 CPU
- **访问地址**: https://kirogate.fly.dev

---

## 部署流程

### 开发流程
1. 在私有仓库 `KiroGate_dev` 进行开发
2. 提交代码到私有仓库

### 部署流程
1. 将代码推送到公开仓库 `KiroGate`
2. GitHub Actions 自动触发部署
3. 部署到 Fly.io

### 推送命令
```bash
# 推送到私有仓库（开发）
git push origin main

# 推送到公开仓库（部署）
git push public main
```

---

## 重要提醒

1. **REFRESH_TOKEN** 需要从 Kiro IDE 中获取真实值
2. **LinuxDo 客户端密钥** 需要你提供
3. 公开仓库不要推送敏感信息，所有密钥都通过 GitHub Secrets 管理
4. 免费额度足够使用，不会产生费用

---

## 故障排查

### 查看部署日志
```bash
gh run list --repo hj01857655/KiroGate
gh run view [RUN_ID] --repo hj01857655/KiroGate --log
```

### 查看 Fly.io 日志
访问：https://fly.io/apps/kirogate/monitoring

### 更新 Secrets
```bash
gh secret set SECRET_NAME --body "新值" --repo hj01857655/KiroGate
```