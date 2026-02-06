# 飞书桥接服务启动脚本 (Windows PowerShell)
# 使用前请修改飞书相关配置

# ===== 飞书配置（需要你填写）=====
$env:FEISHU_APP_ID = "cli_xxxxxx"           # 飞书App ID
$env:FEISHU_APP_SECRET = "xxxxxx"           # 飞书App Secret  
$env:FEISHU_VERIFICATION_TOKEN = "xxxxxx"   # 飞书验证Token

# ===== OpenClaw配置（已配置好）=====
$env:OPENCLAW_HOOK_TOKEN = "feishu-bridge-2026"
$env:OPENCLAW_WEBHOOK_URL = "http://127.0.0.1:18789/hooks/agent"
$env:PORT = "8066"

# ===== 启动 =====
Write-Host "启动飞书桥接服务..." -ForegroundColor Green
Write-Host "OpenClaw Webhook: $env:OPENCLAW_WEBHOOK_URL" -ForegroundColor Cyan
Write-Host "飞书回调地址: http://你的公网IP:$env:PORT/webhook" -ForegroundColor Yellow
Write-Host ""
python feishu_bridge.py
