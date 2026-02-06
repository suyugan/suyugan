# Docker Desktop Force Cleanup Script
# 彻底清理Docker相关文件和注册表

$ErrorAction = "SilentlyContinue"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Docker Desktop 彻底清理" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[1/6] 停止所有Docker进程..." -ForegroundColor Yellow
Get-Process | Where-Object {$_.ProcessName -like "*docker*"} | Stop-Process -Force
Write-Host "  已完成" -ForegroundColor Green

Write-Host "[2/6] 停止Docker服务..." -ForegroundColor Yellow
net stop com.docker.backend 2>$null
net stop com.docker.service 2>$null
Write-Host "  已完成" -ForegroundColor Green

Write-Host "[3/6] 删除Docker安装目录..." -ForegroundColor Yellow
Remove-Item -Path "C:\Program Files\Docker" -Recurse -Force
Remove-Item -Path "$env:LOCALAPPDATA\Docker" -Recurse -Force
Remove-Item -Path "$env:APPDATA\Docker" -Recurse -Force
Remove-Item -Path "$env:USERPROFILE\.docker" -Recurse -Force
Write-Host "  已完成" -ForegroundColor Green

Write-Host "[4/6] 清理注册表..." -ForegroundColor Yellow
reg delete "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Docker Desktop" /f 2>$null
reg delete "HKCU\Software\Docker Inc." /f 2>$null
reg delete "HKLM\SOFTWARE\Docker Inc." /f 2>$null
Write-Host "  已完成" -ForegroundColor Green

Write-Host "[5/6] 删除快捷方式..." -ForegroundColor Yellow
Remove-Item -Path "$env:PUBLIC\Desktop\Docker Desktop.lnk" -Force
Remove-Item -Path "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Docker Desktop.lnk" -Force
Write-Host "  已完成" -ForegroundColor Green

Write-Host "[6/6] 验证清理结果..." -ForegroundColor Yellow
$dockerExists = Test-Path "C:\Program Files\Docker"
if (-not $dockerExists) {
    Write-Host "  Docker Desktop 已完全卸载!" -ForegroundColor Green
} else {
    Write-Host "  某些文件可能需要手动删除" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  清理完成！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "下一步：" -ForegroundColor Yellow
Write-Host "1. 重启计算机（推荐）" -ForegroundColor Gray
Write-Host "2. 下载 Docker Desktop：" -ForegroundColor Gray
Write-Host "   https://www.docker.com/products/docker-desktop/" -ForegroundColor Cyan
Write-Host "3. 重新安装" -ForegroundColor Gray
Write-Host ""
Write-Host "安装完成后告诉我：'Docker Desktop 已安装'" -ForegroundColor Cyan
Write-Host "我会立即帮你部署视频分析系统！" -ForegroundColor Green
Write-Host ""
