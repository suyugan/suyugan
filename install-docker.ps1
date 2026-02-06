# Install Docker Desktop - Simplified
$ErrorAction = "SilentlyContinue"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Docker Desktop Installer" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 搜索下载目录
$downloadsPath = "$env:USERPROFILE\Downloads"
Write-Host "Checking downloads: $downloadsPath" -ForegroundColor Yellow

# 查找并运行安装文件
Get-ChildItem $downloadsPath -Filter "Docker*.exe" -ErrorAction SilentlyContinue | ForEach-Object {
    Write-Host "Found: $($_.Name)" -ForegroundColor White
    
    $process = Start-Process -FilePath $_.FullName -WindowStyle Normal -Wait
    
    if ($process.ExitCode -eq 0) {
        Write-Host "  Success: ExitCode 0" -ForegroundColor Green
    } else {
        Write-Host "  Failed: ExitCode $($process.ExitCode)" -ForegroundColor Red
    }
    
    Start-Sleep -Seconds 2
}

Write-Host ""
Write-Host "Done!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查Docker Desktop
$dockerProcess = Get-Process | Where-Object {$_.ProcessName -like "*Docker Desktop*"} | Where-Object {$_.ProcessName -notlike "*Backend*"}

if ($dockerProcess) {
    Write-Host "Docker Desktop is running!" -ForegroundColor Green
    Write-Host "Ready to deploy video analysis system!" -ForegroundColor Cyan
} else {
    Write-Host "Docker Desktop not found" -ForegroundColor Yellow
}
