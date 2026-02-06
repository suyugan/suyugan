# 飞书桥接 (Feishu Bridge)

通过 Webhook 方式接入飞书，实现双向消息。

## 架构

```
用户 → 飞书App → Webhook → OpenClaw hooks → AI处理 → 飞书API → 用户
```

## 配置步骤

### 1. 飞书开放平台配置

1. 进入 **事件与回调** → **事件订阅**
2. 配置请求地址: `http://你的服务器:18789/hooks/feishu`
3. 添加事件: `im.message.receive_v1` (接收消息)

### 2. 环境变量

```bash
export FEISHU_APP_ID="cli_xxx"
export FEISHU_APP_SECRET="xxx"
export FEISHU_VERIFICATION_TOKEN="xxx"
```

### 3. OpenClaw hooks 配置

在 `openclaw.json` 中添加:

```json
{
  "hooks": {
    "enabled": true,
    "mappings": [
      {
        "id": "feishu",
        "match": { "path": "/feishu" },
        "action": "agent",
        "transform": {
          "module": "./skills/feishu-bridge/scripts/transform.js"
        }
      }
    ]
  }
}
```

## 脚本

- `scripts/transform.js` - Webhook 事件转换
- `scripts/send.js` - 发送飞书消息
- `scripts/feishu-api.js` - 飞书 API 封装

## 使用

收到飞书消息后，AI 会自动回复。也可以手动发送:

```bash
node skills/feishu-bridge/scripts/send.js "chat_id" "消息内容"
```
