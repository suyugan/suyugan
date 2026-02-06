# Discord Bot Tester - 直接通过 Discord API 测试
# 这个脚本会帮你测试 bot 是否可以接收消息

$clientId = "1468278297195708520"
$botName = "dasx"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Discord Bot 测试助手" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Bot 信息:" -ForegroundColor Yellow
Write-Host "  名称: $botName" -ForegroundColor White
Write-Host "  ID: $clientId" -ForegroundColor White
Write-Host "  状态: 已登录 OpenClaw" -ForegroundColor Green
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  为什么看不到 bot？" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "可能的原因:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Bot 没有真正加入服务器" -ForegroundColor White
Write-Host "   解决: 重新使用邀请链接" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Bot 被服务器权限隐藏" -ForegroundColor White
Write-Host "   解决: 检查服务器设置" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Discord 缓存问题" -ForegroundColor White
Write-Host "   解决: 刷新页面或重启 Discord" -ForegroundColor Gray
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  重新邀请 bot 到服务器" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$oauthUrl = "https://discord.com/oauth2/authorize?client_id=$clientId&permissions=274878025984&scope=bot+applications.commands"
Write-Host "1. 点击下面的链接:" -ForegroundColor Yellow
Write-Host ""
Write-Host $oauthUrl -ForegroundColor Green
Write-Host ""
Write-Host "2. 选择你的服务器" -ForegroundColor Yellow
Write-Host "3. 点击 '授权'" -ForegroundColor Yellow
Write-Host "4. 等待 bot 出现在成员列表" -ForegroundColor Yellow
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  测试 bot" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Bot 添加到服务器后:" -ForegroundColor Yellow
Write-Host ""
Write-Host "【方法 1】服务器频道测试" -ForegroundColor White
Write-Host "  在频道输入: @dasx 你好" -ForegroundColor Gray
Write-Host ""
Write-Host "【方法 2】私聊测试" -ForegroundColor White
Write-Host "  1. 在成员列表找到 dasx" -ForegroundColor Gray
Write-Host "  2. 右键点击 -> 发送消息" -ForegroundColor Gray
Write-Host "  3. 发送: 你好" -ForegroundColor Gray
Write-Host ""
Write-Host "【方法 3】直接发送 DM" -ForegroundColor White
Write-Host "  在浏览器打开: https://discord.com/channels/@me/DM-ID" -ForegroundColor Gray
Write-Host "  (需要 bot 用户 ID)" -ForegroundColor Gray
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  立即测试？" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$test = Read-Host "是否打开邀请链接? (y/n)"
if ($test -eq 'y' -or $test -eq 'Y') {
    Start-Process $oauthUrl
    Write-Host ""
    Write-Host "✓ 已在浏览器打开邀请链接" -ForegroundColor Green
    Write-Host ""
}

Write-Host "完成! 按 Ctrl+C 退出" -ForegroundColor Yellow
