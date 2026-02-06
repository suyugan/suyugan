# Discord Bot Creation Helper
# Usage: .\create-discord-bot.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Discord Bot Creation Helper" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Open Discord Developer Portal
Write-Host "[1/4] Opening Discord Developer Portal..." -ForegroundColor Yellow
Start-Process "https://discord.com/developers/applications"
Start-Sleep -Seconds 3

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Follow these steps in your browser:" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "[Step 1] Click 'New Application' button" -ForegroundColor White
Write-Host "[Step 2] Enter app name (anything), click Create" -ForegroundColor White
Write-Host "[Step 3] Click 'Bot' in left menu, then 'Add Bot'" -ForegroundColor White
Write-Host "[Step 4] Click 'Yes, do it!'" -ForegroundColor White
Write-Host "[Step 5] Enable these options:" -ForegroundColor White
Write-Host "  [X] MESSAGE CONTENT INTENT (REQUIRED!)" -ForegroundColor Green
Write-Host "  [ ] SERVER MEMBERS INTENT (optional)" -ForegroundColor Gray
Write-Host "[Step 6] Click 'Reset Token', then copy the TOKEN" -ForegroundColor Yellow
Write-Host "[Step 7] Send the TOKEN to AI assistant" -ForegroundColor Yellow
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Need to invite bot to server?" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "[Step 8] Click 'OAuth2' -> 'URL Generator' in left menu" -ForegroundColor White
Write-Host "[Step 9] Check 'bot' and 'applications.commands'" -ForegroundColor White
Write-Host "[Step 10] Check these bot permissions:" -ForegroundColor White
Write-Host "  [X] Send Messages" -ForegroundColor Green
Write-Host "  [X] Read Messages/View Channels" -ForegroundColor Green
Write-Host "  [ ] Embed Links (optional)" -ForegroundColor Gray
Write-Host "[Step 11] Copy the URL at the bottom, open in browser" -ForegroundColor Yellow
Write-Host "[Step 12] Select server and authorize" -ForegroundColor Yellow
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Done! Send TOKEN to AI assistant" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
