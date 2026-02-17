#!/usr/bin/env pwsh
<#
.SYNOPSIS
    标准化上传脚本：上传文件到腾讯云 + 修权限 + 验证链接
.USAGE
    .\upload_to_cloud.ps1 -LocalPath "D:\video-analysis\output\xxx\final.mp4" -RemotePath "/var/www/html/videos/xxx.mp4"
    .\upload_to_cloud.ps1 -LocalPath "D:\output\cover.jpg" -RemotePath "/var/www/html/images/cover.jpg"
    
    # 指定远程目录（自动用本地文件名）
    .\upload_to_cloud.ps1 -LocalPath "D:\output\demo.mp4" -RemoteDir "/var/www/html/videos/"
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$LocalPath,
    
    [string]$RemotePath,
    [string]$RemoteDir,
    
    [string]$Server = "106.55.158.137",
    [string]$User = "ubuntu",
    [string]$BaseUrl = "http://bm.weiixxin.com"
)

$ErrorActionPreference = "Stop"

# 检查本地文件
if (-not (Test-Path $LocalPath)) {
    Write-Error "本地文件不存在: $LocalPath"
    exit 1
}

$fileInfo = Get-Item $LocalPath
$fileSizeMB = [math]::Round($fileInfo.Length / 1MB, 2)
Write-Host "📦 文件: $($fileInfo.Name) ($fileSizeMB MB)" -ForegroundColor Cyan

# 确定远程路径
if (-not $RemotePath -and -not $RemoteDir) {
    Write-Error "必须指定 -RemotePath 或 -RemoteDir"
    exit 1
}

if (-not $RemotePath) {
    $RemoteDir = $RemoteDir.TrimEnd('/')
    $RemotePath = "$RemoteDir/$($fileInfo.Name)"
}

# 确保远程目录存在
$remoteDir = $RemotePath.Substring(0, $RemotePath.LastIndexOf('/'))
Write-Host "📁 远程目录: $remoteDir" -ForegroundColor Gray
ssh "${User}@${Server}" "mkdir -p '$remoteDir'"

# 上传
Write-Host "⬆️  上传中..." -ForegroundColor Yellow
scp "$LocalPath" "${User}@${Server}:${RemotePath}"
if ($LASTEXITCODE -ne 0) {
    Write-Error "上传失败！"
    exit 1
}
Write-Host "✅ 上传完成" -ForegroundColor Green

# 修权限（nginx用www-data读取）
Write-Host "🔒 修复权限..." -ForegroundColor Yellow
ssh "${User}@${Server}" "chmod 644 '$RemotePath'; sudo chown www-data:www-data '$RemotePath' 2>/dev/null || true"
Write-Host "✅ 权限已修复" -ForegroundColor Green

# 计算URL路径（去掉/var/www/html前缀）
$urlPath = $RemotePath -replace '^/var/www/html', ''
$fullUrl = "${BaseUrl}${urlPath}"

# 验证链接
Write-Host "🔍 验证链接: $fullUrl" -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri $fullUrl -Method Head -UseBasicParsing -TimeoutSec 10
    if ($response.StatusCode -eq 200) {
        $contentType = $response.Headers['Content-Type']
        $contentLength = $response.Headers['Content-Length']
        $sizeMB = if ($contentLength) { [math]::Round([long]$contentLength / 1MB, 2) } else { "unknown" }
        Write-Host "✅ 链接可用！" -ForegroundColor Green
        Write-Host "   Status: $($response.StatusCode)" -ForegroundColor Gray
        Write-Host "   Type: $contentType" -ForegroundColor Gray
        Write-Host "   Size: $sizeMB MB" -ForegroundColor Gray
    } else {
        Write-Warning "⚠️ 返回状态码: $($response.StatusCode)"
    }
} catch {
    Write-Error "❌ 链接验证失败: $_"
    Write-Host "尝试排查..." -ForegroundColor Yellow
    ssh "${User}@${Server}" "ls -la '$RemotePath'; nginx -t 2>&1; systemctl status nginx --no-pager -l | head -5"
    exit 1
}

# 输出结果
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🎉 上传成功！" -ForegroundColor Green
Write-Host "在线链接: $fullUrl" -ForegroundColor White
Write-Host "本地路径: $LocalPath" -ForegroundColor Gray
Write-Host "远程路径: $RemotePath" -ForegroundColor Gray
Write-Host "========================================" -ForegroundColor Cyan

# 返回URL供脚本调用
return $fullUrl
