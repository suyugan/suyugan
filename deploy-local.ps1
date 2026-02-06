# Windows本地部署视频分析API
# 通过Docker在Windows电脑上运行抖音分析API

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Windows本地部署" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查Docker
Write-Host "[1/4] 检查Docker..." -ForegroundColor Yellow
$dockerRunning = Get-Process docker -ErrorAction SilentlyContinue

if (-not $dockerRunning) {
    Write-Host "X Docker Desktop未运行，请先启动Docker Desktop！" -ForegroundColor Red
    Write-Host ""
    exit 1
}

Write-Host "OK Docker运行中" -ForegroundColor Green
Write-Host ""

# 目录
$workDir = "C:\Users\Administrator\.openclaw\video-analysis"
$volumeDir = "C:\Users\Administrator\.openclaw\video-analysis\data"

Write-Host "[2/4] 创建目录..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path $workDir | Out-Null
New-Item -ItemType Directory -Force -Path $volumeDir | Out-Null

Write-Host "[3/4] 拉取镜像..." -ForegroundColor Yellow
docker pull evil0ctal/douyin_tiktok_download_api

Write-Host "[4/4] 停止旧容器..." -ForegroundColor Yellow
$oldContainer = docker ps --filter "name=douyin-api" -q --format "{{.ID}}"
if ($oldContainer) {
    docker stop $oldContainer
    docker rm $oldContainer
}

Write-Host "[5/4] 启动容器..." -ForegroundColor Yellow
docker run -d --name douyin-api -p 18810:80 -v "${volumeDir}:/app/data" --restart unless-stopped evil0ctal/douyin_tiktok_download_api

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  完成！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "下一步:" -ForegroundColor White
Write-Host "1. 配置Cookie" -ForegroundColor Yellow
Write-Host "   打开: $volumeDir\douyin_web\config.yaml" -ForegroundColor Gray
Write-Host "2. 重启容器" -ForegroundColor Yellow
Write-Host "   docker restart douyin-api" -ForegroundColor Gray
Write-Host "3. 测试" -ForegroundColor Yellow
Write-Host "   打开: http://localhost:18810/docs" -ForegroundColor Gray
Write-Host ""
