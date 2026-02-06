# Discord Bot Status Checker & Fixer
# Usage: .\test-discord-bot.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Discord Bot Status Checker" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check OpenClaw status
Write-Host "[1/4] Checking OpenClaw Discord channel..." -ForegroundColor Yellow
$statusResult = & openclaw channels status
Write-Host $statusResult
Write-Host ""

# Check bot token
Write-Host "[2/4] Checking bot configuration..." -ForegroundColor Yellow
$configPath = "$env:USERPROFILE\.openclaw\openclaw.json"
$config = Get-Content $configPath | ConvertFrom-Json
$discordToken = $config.channels.discord.token
$discordEnabled = $config.channels.discord.enabled

if ($discordEnabled) {
    Write-Host "  Discord: ENABLED" -ForegroundColor Green
    Write-Host "  Token: Present ($($discordToken.Substring(0, 20))...)" -ForegroundColor Green
} else {
    Write-Host "  Discord: DISABLED" -ForegroundColor Red
}
Write-Host ""

# Generate OAuth2 URL
Write-Host "[3/4] Generating OAuth2 URL..." -ForegroundColor Yellow
$clientId = "1468278297195708520"
$permissions = "274878025984"
$scope = "bot%20applications.commands"
$oauthUrl = "https://discord.com/oauth2/authorize?client_id=$clientId&permissions=$permissions&scope=$scope"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  INVITE LINK" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host $oauthUrl -ForegroundColor Yellow
Write-Host ""
Write-Host "Copy and open this link in your browser to invite the bot to your server."
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Test bot connection
Write-Host "[4/4] Testing bot connection..." -ForegroundColor Yellow
& openclaw gateway restart
Start-Sleep -Seconds 5
& openclaw channels status
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  COMPLETE" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
