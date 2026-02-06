# 创建全新 Discord Bot 的步骤（完整版）
# 我会一步步帮你完成

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  创建全新 Discord Bot" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "【步骤 1】删除旧的应用" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. 打开: https://discord.com/developers/applications" -ForegroundColor White
Write-Host "2. 找到 'dasx' 应用" -ForegroundColor White
Write-Host "3. 点击右上角齿轮图标" -ForegroundColor White
Write-Host "4. 点击 'Delete App'（删除应用）" -ForegroundColor White
Write-Host "5. 确认删除" -ForegroundColor White
Write-Host ""

Write-Host "【步骤 2】创建新的应用" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. 点击左上角 'New Application'" -ForegroundColor White
Write-Host "2. 输入应用名称: 苏煜淦AI助手" -ForegroundColor White
Write-Host "3. 点击 'Create'" -ForegroundColor White
Write-Host ""

Write-Host "【步骤 3】创建 Bot" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. 在左侧菜单点击 'Bot'" -ForegroundColor White
Write-Host "2. 点击 'Add Bot'" -ForegroundColor White
Write-Host "3. 点击 'Yes, do it!'" -ForegroundColor White
Write-Host "4. 给 bot 改名: 苏煜淦AI助手" -ForegroundColor White
Write-Host "5. 点击 'Save Changes'" -ForegroundColor White
Write-Host ""

Write-Host "【步骤 4】启用 Intents（重要！）" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. 向下滚动到 'Privileged Gateway Intents'" -ForegroundColor White
Write-Host "2. 勾选 'MESSAGE CONTENT INTENT' [必须]" -ForegroundColor Green
Write-Host "3. 勾选 'SERVER MEMBERS INTENT' [推荐]" -ForegroundColor Gray
Write-Host "4. 点击 'Save Changes'" -ForegroundColor White
Write-Host ""

Write-Host "【步骤 5】复制 Bot Token" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. 在 'TOKEN' 区域点击 'Reset Token'" -ForegroundColor White
Write-Host "2. 点击 'Yes, do it!'" -ForegroundColor White
Write-Host "3. 复制显示的 Token" -ForegroundColor White
Write-Host "4. **把 Token 发给 AI 助手**" -ForegroundColor Yellow
Write-Host ""

Write-Host "【步骤 6】生成邀请链接" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. 左侧菜单点击 'OAuth2' -> 'URL Generator'" -ForegroundColor White
Write-Host "2. 勾选 'bot' 和 'applications.commands'" -ForegroundColor White
Write-Host "3. 在 'Bot Permissions' 里勾选:" -ForegroundColor White
Write-Host "   - View Channels" -ForegroundColor Green
Write-Host "   - Send Messages" -ForegroundColor Green
Write-Host "   - Read Message History" -ForegroundColor Green
Write-Host "   - Embed Links" -ForegroundColor Green
Write-Host "   - Attach Files" -ForegroundColor Green
Write-Host "   - Add Reactions" -ForegroundColor Green
Write-Host "4. 复制页面底部的 URL" -ForegroundColor White
Write-Host "5. 在浏览器打开 URL" -ForegroundColor White
Write-Host "6. 选择你的服务器，点击 '授权'" -ForegroundColor White
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  完成后" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. 把 Bot Token 发给 AI 助手" -ForegroundColor Yellow
Write-Host "2. Bot 会出现在服务器成员列表" -ForegroundColor Yellow
Write-Host "3. 右键点击 bot -> 发送消息 -> 测试" -ForegroundColor Yellow
Write-Host ""
Write-Host "准备好了吗？开始吧！" -ForegroundColor Green
Write-Host ""
