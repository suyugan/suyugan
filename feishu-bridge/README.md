# 飞书 <-> OpenClaw 桥接服务

让飞书机器人拥有和OpenClaw一样的AI能力。

## 架构

```
飞书用户 → 飞书机器人 → 本服务(webhook) → OpenClaw → 回复 → 飞书
```

## 部署步骤

### 1. 创建飞书应用

1. 打开 [飞书开放平台](https://open.feishu.cn/app)
2. 创建企业自建应用
3. 记录 **App ID** 和 **App Secret**

### 2. 配置机器人能力

1. 在应用详情 → 添加应用能力 → 添加「机器人」
2. 配置机器人头像、名称等

### 3. 配置事件订阅

1. 应用详情 → 事件订阅
2. 请求地址: `http://你的服务器IP:8066/webhook`
3. 添加事件: `im.message.receive_v1`（接收消息）
4. 记录 **Verification Token**

### 4. 配置权限

应用详情 → 权限管理 → 开通以下权限：
- `im:message` - 获取与发送单聊、群聊消息
- `im:message:send_as_bot` - 以应用身份发送消息

### 5. 发布应用

版本管理与发布 → 创建版本 → 申请发布

### 6. 配置OpenClaw

在OpenClaw配置文件中启用webhook：

```json5
{
  hooks: {
    enabled: true,
    token: "你的hook密钥",
    path: "/hooks"
  }
}
```

### 7. 启动桥接服务

```bash
# 安装依赖
pip install flask requests

# 设置环境变量
export FEISHU_APP_ID="cli_xxxxxx"
export FEISHU_APP_SECRET="xxxxxx"
export FEISHU_VERIFICATION_TOKEN="xxxxxx"
export OPENCLAW_HOOK_TOKEN="你的hook密钥"
export OPENCLAW_WEBHOOK_URL="http://127.0.0.1:18789/hooks/agent"

# 启动
python feishu_bridge.py
```

### 8. Windows启动方式

```powershell
$env:FEISHU_APP_ID="cli_xxxxxx"
$env:FEISHU_APP_SECRET="xxxxxx"
$env:FEISHU_VERIFICATION_TOKEN="xxxxxx"
$env:OPENCLAW_HOOK_TOKEN="你的hook密钥"
$env:OPENCLAW_WEBHOOK_URL="http://127.0.0.1:18789/hooks/agent"

python feishu_bridge.py
```

## 配置文件方式（可选）

创建 `.env` 文件：

```
FEISHU_APP_ID=cli_xxxxxx
FEISHU_APP_SECRET=xxxxxx
FEISHU_VERIFICATION_TOKEN=xxxxxx
OPENCLAW_HOOK_TOKEN=你的hook密钥
OPENCLAW_WEBHOOK_URL=http://127.0.0.1:18789/hooks/agent
PORT=8066
```

然后使用 `python-dotenv` 加载。

## 公网访问

飞书需要能访问你的服务器，选择一种方式：

1. **云服务器**: 直接部署，开放8066端口
2. **内网穿透**: 使用 ngrok / frp / Cloudflare Tunnel
3. **Tailscale**: 如果飞书服务器在同一Tailnet

### 使用 ngrok

```bash
ngrok http 8066
# 获得类似 https://xxxx.ngrok.io 的地址
# 将 https://xxxx.ngrok.io/webhook 填入飞书事件订阅
```

## 测试

1. 在飞书中找到你的机器人
2. 发送消息
3. 机器人应该回复（由OpenClaw处理）

## 日志

服务会打印：
- `[收到消息]` - 收到飞书消息
- `[回复]` - 发送回复
- `[错误]` - 处理失败

## 故障排查

1. **飞书提示webhook验证失败**: 检查服务是否启动，URL是否正确
2. **收不到消息**: 检查事件订阅配置、权限是否开通
3. **回复失败**: 检查OpenClaw webhook配置、token是否正确
