# Docker Desktop 自动安装运行脚本
# 功能：自动查找、下载、运行 Docker Desktop 安装程序

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Docker Desktop 自动安装" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 搜索下载目录
$downloadsPath = "$env:USERPROFILE\Downloads"
Write-Host "[1/5] 检查下载目录..." -ForegroundColor Yellow
Write-Host "  目录: $downloadsPath" -ForegroundColor White
Write-Host ""

# 查找 Docker Desktop 安装文件
$files = Get-ChildItem $downloadsPath -Filter "Docker*.exe" -ErrorAction SilentlyContinue

if ($files.Count -eq 0) {
    Write-Host "  未找到 Docker Desktop 安装文件" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "请手动操作：" -ForegroundColor White
    Write-Host "  1. 浏览器应该已打开下载页面" -ForegroundColor Gray
    Write-Host "  2. 查看下载文件夹（$downloadsPath）" -ForegroundColor Gray
    Write-Host "  3. 找到 Docker Desktop 安装包后，运行安装程序" -ForegroundColor Gray
    Write-Host ""
    exit 1
}

Write-Host ""
Write-Host "✓ 找到 $($files.Count) 个安装文件" -ForegroundColor Green
Write-Host ""

foreach ($file in $files) {
    Write-Host "  文件: $($file.Name)" -ForegroundColor White
    Write-Host "  大小: $([math]::Round($file.Length / 1MB, 2))" -ForegroundColor Gray
    
    # 运行安装
    Write-Host "  正在安装..." -ForegroundColor Yellow
    $process = Start-Process -FilePath $file.FullName -WindowStyle Normal -Wait
    
    if ($process.ExitCode -eq 0) {
        Write-Host "  ✓ 安装成功！" -ForegroundColor Green
    } else {
        Write-Host "  ✗ 安装失败（错误码: $($process.ExitCode））" -ForegroundColor Red
    }
    
    Start-Sleep -Seconds 2
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  安装完成！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查 Docker Desktop 是否运行
Write-Host "[2/2] 检查 Docker Desktop..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

$dockerProcess = Get-Process | Where-Object {$_.ProcessName -like "*Docker Desktop*"} | Where-Object {$_.ProcessName -notlike "*Backend*"}

if ($dockerProcess) {
    Write-Host ""
    Write-Host "✓ Docker Desktop 已运行" -ForegroundColor Green
    Write-Host ""
    Write-Host "现在可以继续部署视频分析系统！" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "下一步：" -ForegroundColor Yellow
    Write-Host "  配置 Cookie 到：C:\Users\Administrator\.openclaw\video-analysis\data\douyin_web\config.yaml" -ForegroundColor Gray
    Write-Host "  发送: deploy" 到我" -ForegroundColor Gray
} else {
    Write-Host ""
    Write-Host "✗ Docker Desktop 未运行" -ForegroundColor Red
    Write-Host ""
    Write-Host "可能原因：" -ForegroundColor Yellow
    Write-Host "  1. 安装还在进行" -ForegroundColor Gray
    Write-Host "  2. 安装未完成" -ForegroundColor Gray
    Write-Host "  3. 需要手动启动 Docker Desktop" -ForegroundColor Gray
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  脚本执行完成！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
