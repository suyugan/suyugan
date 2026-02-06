# Auto Deploy Video Analysis
# Auto-start Docker Desktop and deploy API

$ErrorAction = "SilentlyContinue"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Auto Deployment" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check Docker Desktop
Write-Host "[1/8] Checking Docker Desktop..." -ForegroundColor Yellow

$dockerTask = Get-Process | Where-Object {$_.ProcessName -like "*docker*" -and $_.ProcessName -notlike "*Docker Desktop*"}

if ($dockerTask) {
    Write-Host "  Docker Desktop is running" -ForegroundColor Green
    $dockerRunning = $true
} else {
    Write-Host "  Docker Desktop not running, starting..." -ForegroundColor Yellow
    
    # Try multiple paths
    $paths = @(
        "C:\Program Files\Docker\Docker\Docker Desktop.exe",
        "$env:LOCALAPPDATA\Docker\Docker Desktop.exe",
        "$env:APPDATA\Docker\Docker Desktop.exe"
    )
    
    foreach ($path in $paths) {
        if (Test-Path $path) {
            Write-Host "  Trying: $path" -ForegroundColor Gray
            Start-Process -FilePath $path -WindowStyle Hidden -ErrorAction $ErrorAction
            Start-Sleep -Seconds 2
            
            $dockerTask = Get-Process | Where-Object {$_.ProcessName -like "*docker*" -and $_.ProcessName -notlike "*Docker Desktop*"}
            if ($dockerTask) {
                Write-Host "  Started!" -ForegroundColor Green
                $dockerRunning = $true
                break
            }
        }
    }
    
    if (-not $dockerRunning) {
        Write-Host ""
        Write-Host "  Could not auto-start Docker Desktop" -ForegroundColor Red
        Write-Host "  Please start it manually" -ForegroundColor Yellow
        exit 1
    }
}

# Create work directories
Write-Host ""
Write-Host "[2/8] Creating directories..." -ForegroundColor Yellow

$workDir = "C:\Users\Administrator\.openclaw\video-analysis"
$volumeDir = "C:\Users\Administrator\.openclaw\video-analysis\data"

if (-not (Test-Path $workDir)) {
    New-Item -ItemType Directory -Force -Path $workDir | Out-Null
}
if (-not (Test-Path $volumeDir)) {
    New-Item -ItemType Directory -Force -Path $volumeDir | Out-Null
}

Write-Host "  Work: $workDir" -ForegroundColor White
Write-Host "  Data: $volumeDir" -ForegroundColor White

Write-Host ""
Write-Host "[3/8] Pulling Docker image..." -ForegroundColor Yellow
Write-Host "  Image: evil0ctal/douyin_tiktok_download_api" -ForegroundColor White

docker pull evil0ctal/douyin_tiktok_download_api

Write-Host ""
Write-Host "[4/8] Checking old containers..." -ForegroundColor Yellow

$oldContainer = docker ps --filter "name=douyin-api" --format "{{.ID}}" 2>$null

if ($oldContainer) {
    Write-Host "  Stopping old container..." -ForegroundColor Gray
    docker stop $oldContainer
    docker rm $oldContainer
    Write-Host "  Removed" -ForegroundColor Green
}

Write-Host ""
Write-Host "[5/8] Starting API container..." -ForegroundColor Yellow

docker run -d `
  --name douyin-api `
  -p 18810:80 `
  -v "${volumeDir}:/app/data" `
  --restart unless-stopped `
  evil0ctal/douyin_tiktok_download_api

Write-Host ""
Write-Host "  Started!" -ForegroundColor Green

Write-Host ""
Write-Host "[6/8] Waiting for API ready..." -ForegroundColor Yellow

$ready = $false
$attempts = 0
$maxAttempts = 18

while (-not $ready -and $attempts -lt $maxAttempts) {
    $attempts++
    Start-Sleep -Seconds 2
    
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:18810/docs" -TimeoutSeconds 5 -UseBasicParsing
        if ($response.StatusCode -eq 200) {
            Write-Host ""
            Write-Host "  API is ready!" -ForegroundColor Green
            $ready = $true
        }
    } catch {
        # Continue trying
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Deployment Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "1. Configure Cookie" -ForegroundColor Yellow
Write-Host "   - Open: https://www.douyin.com" -ForegroundColor Gray
Write-Host "   - Login, press F12, copy cookies" -ForegroundColor Gray
Write-Host "   - Paste into: ${volumeDir}\douyin_web\config.yaml" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Restart container" -ForegroundColor Yellow
Write-Host "   docker restart douyin-api" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Test full flow" -ForegroundColor Yellow
Write-Host "   - Open: http://localhost:18810/docs" -ForegroundColor Gray
Write-Host "   - Send: analysis [video link]" -ForegroundColor Gray
Write-Host ""
