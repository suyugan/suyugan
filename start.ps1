# One-Click Start Video Analysis System
# Just type "启动" to deploy everything automatically

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Video Analysis System - One-Click Start" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$workDir = "C:\Users\Administrator\.openclaw\video-analysis"
$volumeDir = "C:\Users\Administrator\.openclaw\video-analysis\data"

Write-Host "[1/5] Checking Docker Desktop..." -ForegroundColor Yellow
$dockerProcess = Get-Process docker -ErrorAction SilentlyContinue

if (-not $dockerProcess) {
    Write-Host "Docker Desktop not running, starting..." -ForegroundColor Yellow
    Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe" -WindowStyle Hidden
    Start-Sleep -Seconds 5
}

Write-Host "Docker Desktop is running" -ForegroundColor Green
Write-Host ""

if (-not (Test-Path $workDir)) {
    Write-Host "Creating work directories..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Force -Path $workDir | Out-Null
    New-Item -ItemType Directory -Force -Path $volumeDir | Out-Null
    Write-Host "Work dirs created" -ForegroundColor Green
}

Write-Host ""
Write-Host "[2/5] Pulling Docker image..." -ForegroundColor Yellow
Write-Host "Image: evil0ctal/douyin_tiktok_download_api" -ForegroundColor White
Write-Host ""

docker pull evil0ctal/douyin_tiktok_download_api

Write-Host ""
Write-Host "[3/5] Checking old containers..." -ForegroundColor Yellow

$oldContainer = docker ps --filter "name=douyin-api" --format "{{.ID}}"
if ($oldContainer) {
    Write-Host "Stopping old container..." -ForegroundColor Gray
    docker stop $oldContainer
    docker rm $oldContainer
    Write-Host "Old container updated" -ForegroundColor Green
}

Write-Host ""
Write-Host "[4/5] Starting API container..." -ForegroundColor Yellow

docker run -d `
  --name douyin-api `
  -p 18810:80 `
  -v "${volumeDir}:/app/data" `
  --restart unless-stopped `
  evil0ctal/douyin_tiktok_download_api

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Deployment Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "1. Configure Cookie (CRITICAL)" -ForegroundColor Yellow
Write-Host "   - Open browser: https://www.douyin.com" -ForegroundColor Gray
Write-Host "   - Login and get Cookie via F12" -ForegroundColor Gray
Write-Host "   - Paste into: ${volumeDir}\douyin_web\config.yaml" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Restart container" -ForegroundColor Yellow
Write-Host "   docker restart douyin-api" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Test API" -ForegroundColor Yellow
Write-Host "   - Open browser: http://localhost:18810/docs" -ForegroundColor Gray
Write-Host ""
Write-Host "Get Douyin Cookie:" -ForegroundColor Cyan
Write-Host "1. Open https://www.douyin.com" -ForegroundColor White
Write-Host "2. Login to your account" -ForegroundColor White
Write-Host "3. Press F12 -> Application -> Cookies" -ForegroundColor White
Write-Host "4. Copy all Cookie values" -ForegroundColor White
Write-Host "5. Paste into config.yaml Cookie line" -ForegroundColor White
Write-Host ""
Write-Host "After configuration:" -ForegroundColor Green
Write-Host "Just type: 启动" -ForegroundColor Cyan
Write-Host "I will do everything automatically!" -ForegroundColor Cyan
