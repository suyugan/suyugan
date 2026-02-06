# Windows Local Deployment for Video Analysis API
# Deploy Douyin/TikTok analysis API locally via Docker

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Windows Local Deployment" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check Docker Desktop
Write-Host "[1/4] Checking Docker Desktop..." -ForegroundColor Yellow
$dockerRunning = Get-Process docker -ErrorAction SilentlyContinue

if (-not $dockerRunning) {
    Write-Host "Error: Docker Desktop not running" -ForegroundColor Red
    Write-Host "Please start Docker Desktop first!" -ForegroundColor Yellow
    exit 1
}

Write-Host "Docker Desktop is running" -ForegroundColor Green
Write-Host ""

# Work directory
$workDir = "C:\Users\Administrator\.openclaw\video-analysis"
$volumeDir = "C:\Users\Administrator\.openclaw\video-analysis\data"

Write-Host "[2/4] Creating directories..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path $workDir | Out-Null
New-Item -ItemType Directory -Force -Path $volumeDir | Out-Null

Write-Host "Work directory: $workDir" -ForegroundColor White
Write-Host "Data volume: $volumeDir" -ForegroundColor White
Write-Host ""

# Pull Docker image
Write-Host "[3/4] Pulling Docker image..." -ForegroundColor Yellow
Write-Host "Image: evil0ctal/douyin_tiktok_download_api" -ForegroundColor White
Write-Host ""

docker pull evil0ctal/douyin_tiktok_download_api

Write-Host ""
Write-Host "[4/4] Checking old containers..." -ForegroundColor Yellow

# Stop and remove old container
$oldContainer = docker ps --filter "name=douyin-api" --format "{{.ID}}"
if ($oldContainer) {
    Write-Host "Stopping old container..." -ForegroundColor Gray
    docker stop $oldContainer
    docker rm $oldContainer
    Write-Host "Old container removed" -ForegroundColor Green
}

Write-Host ""
Write-Host "[5/4] Starting new container..." -ForegroundColor Yellow
Write-Host ""

# Start container
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
Write-Host "Next Steps:" -ForegroundColor White
Write-Host "1. Configure Cookie (CRITICAL)" -ForegroundColor Yellow
Write-Host "   - Open: C:\Users\Administrator\.openclaw\video-analysis\data\douyin_web\config.yaml" -ForegroundColor Gray
Write-Host "   - Replace Cookie: line with your Douyin cookie" -ForegroundColor Gray
Write-Host "2. Restart container" -ForegroundColor Yellow
Write-Host "   docker restart douyin-api" -ForegroundColor Gray
Write-Host "3. Test API" -ForegroundColor Yellow
Write-Host "   - Open browser: http://localhost:18810/docs" -ForegroundColor Gray
Write-Host ""
Write-Host "Get Douyin Cookie:" -ForegroundColor Cyan
Write-Host "1. Open https://www.douyin.com in browser" -ForegroundColor White
Write-Host "2. Login to your Douyin account" -ForegroundColor White
Write-Host "3. Press F12" -ForegroundColor White
Write-Host "4. Application -> Cookies" -ForegroundColor White
Write-Host "5. Copy all Cookie values" -ForegroundColor White
Write-Host "6. Paste into config.yaml Cookie line" -ForegroundColor White
Write-Host ""
