# 一键启动视频分析系统
# 使用方法：直接输入"启动"即可

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  视频分析系统 - 一键启动" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 工作目录
$workDir = "C:\Users\Administrator\.openclaw\video-analysis"
$volumeDir = "C:\Users\Administrator\.openclaw\video-analysis\data"

Write-Host "[1/5] 检查Docker Desktop..." -ForegroundColor Yellow

# 检查Docker是否运行
$dockerProcess = Get-Process docker -ErrorAction SilentlyContinue

if (-not $dockerProcess) {
    Write-Host "Docker Desktop 未运行，正在启动..." -ForegroundColor Yellow
    
    # 启动Docker Desktop
    Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe" -WindowStyle Hidden
    
    # 等待Docker启动
    Start-Sleep -Seconds 5
}

Write-Host "✓ Docker Desktop 已运行" -ForegroundColor Green
Write-Host ""

# 创建工作目录
if (-not (Test-Path $workDir)) {
    New-Item -ItemType Directory -Force -Path $workDir | Out-Null
    New-Item -ItemType Directory -Force -Path $volumeDir | Out-Null
    Write-Host "✓ 工作目录已创建" -ForegroundColor Green
}

Write-Host ""
Write-Host "[2/5] 拉取Docker镜像..." -ForegroundColor Yellow
docker pull evil0ctal/douyin_tiktok_download_api

Write-Host ""
Write-Host "[3/5] 启动API容器..." -ForegroundColor Yellow

# 停止旧容器
$oldContainer = docker ps --filter "name=douyin-api" --format "{{.ID}}"
if ($oldContainer) {
    docker stop $oldContainer
    docker rm $oldContainer
    Write-Host "✓ 旧容器已更新" -ForegroundColor Green
}

# 启动新容器
docker run -d `
  --name douyin-api `
  -p 18810:80 `
  -v "${volumeDir}:/app/data" `
  --restart unless-stopped `
  evil0ctal/douyin_tiktok_download_api

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  启动完成！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "🎯 后续步骤：" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. 配置Cookie（必需）" -ForegroundColor Yellow
Write-Host "   打开浏览器访问抖音" -ForegroundColor Gray
Write-Host "   登录后按F12获取Cookie" -ForegroundColor Gray
Write-Host "   粘贴到这个文件:" -ForegroundColor Gray
Write-Host "   $volumeDir\douyin_web\config.yaml" -ForegroundColor White
Write-Host ""
Write-Host "2. 测试API" -ForegroundColor Yellow
Write-Host "   在浏览器打开: http://localhost:18810/docs" -ForegroundColor Gray
Write-Host ""
Write-Host "以后只需输入: 启动" -ForegroundColor Green
Write-Host "我会自动完成所有步骤！" -ForegroundColor Cyan
Write-Host ""
