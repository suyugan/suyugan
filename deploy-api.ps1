# 一键部署视频分析系统（Docker版）
# 使用方法：等 Docker Desktop 安装完成后，发送 "deploy" 即可

param(
    [string]$Command = ""
)

# 配置
$API_NAME = "douyin-api"
$API_PORT = "18810"
$DATA_DIR = "C:\Users\Administrator\.openclaw\video-analysis\data"
$VOLUME_NAME = "video-analysis-data"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  视频分析系统 - Docker版" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

if ([string]::IsNullOrEmpty($Command)) {
    Write-Host ""
    Write-Host "命令: deploy - 一键部署API" -ForegroundColor Yellow
    Write-Host "命令: check - 检查Docker状态" -ForegroundColor Yellow
    Write-Host "命令: restart - 重启API容器" -ForegroundColor Yellow
    Write-Host "命令: stop - 停止容器" -ForegroundColor Yellow
    Write-Host "命令: logs - 查看容器日志" -ForegroundColor Yellow
    Write-Host ""
    exit 1
}

# 处理命令
switch ($Command.ToLower()) {
    "deploy" {
        Deploy-System
    }
    
    "check" {
        Check-Docker
    }
    
    "restart" {
        Restart-Container
    }
    
    "stop" {
        Stop-Container
    }
    
    "logs" {
        Show-Logs
    }
    
    default {
        Write-Host "未知命令: $Command" -ForegroundColor Red
        exit 1
    }
}

function Deploy-System {
    Write-Host ""
    Write-Host "[1/5] 检查Docker..." -ForegroundColor Yellow
    
    # 检查Docker
    $dockerRunning = docker ps -ErrorAction SilentlyContinue | Out-String
    if (-not $dockerRunning) {
        Write-Host "Docker未运行，请先启动Docker Desktop！" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "  Docker运行中" -ForegroundColor Green
    
    Write-Host "[2/5] 拉取镜像..." -ForegroundColor Yellow
    docker pull evil0ctal/douyin_tiktok_download_api
    
    Write-Host "[3/5] 停止旧容器..." -ForegroundColor Yellow
    docker ps --filter "name=${API_NAME}" --format "{{.ID}}" 2>$null | ForEach-Object { docker stop $_ }
    docker ps --filter "name=${API_NAME}" --format "{{.ID}}" 2>$null | ForEach-Object { docker rm $_ }
    
    Write-Host "[4/5] 启动容器..." -ForegroundColor Yellow
    docker run -d `
        --name ${API_NAME} `
        -p ${API_PORT}:80 `
        -v ${DATA_DIR}:/app/data `
        --restart unless-stopped `
        evil0ctal/douyin_tiktok_download_api
    
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "  部署完成！" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "容器名称: ${API_NAME}" -ForegroundColor White
    Write-Host "API端口: http://localhost:${API_PORT}" -ForegroundColor White
    Write-Host "文档地址: http://localhost:${API_PORT}/docs" -ForegroundColor White
    Write-Host ""
    Write-Host "后续步骤:" -ForegroundColor Yellow
    Write-Host "1. 配置Cookie（必需）" -ForegroundColor Gray
    Write-Host "   - 打开: https://www.douyin.com" -ForegroundColor Gray
    Write-Host "   - F12获取Cookie，粘贴到: ${DATA_DIR}\douyin_web\config.yaml" -ForegroundColor Gray
    Write-Host "   - 执行: docker restart ${API_NAME}" -ForegroundColor Gray
    Write-Host ""
    Write-Host "2. 测试API" -ForegroundColor Gray
    Write-Host "   - 访问: http://localhost:${API_PORT}/docs" -ForegroundColor Gray
    Write-Host ""
    Write-Host "3. 集成到OpenClaw" -ForegroundColor Cyan
    Write-Host "   - 更新 skills\video-analysis\skill.ps1" -ForegroundColor Gray
    Write-Host "   - 配置API_URL为: http://localhost:${API_PORT}" -ForegroundColor Gray
    Write-Host ""
    Write-Host "以后只需发送: deploy 或 check 或 restart 或 logs" -ForegroundColor Green
}

function Check-Docker {
    Write-Host ""
    Write-Host "Docker状态检查" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    
    $dockerRunning = docker ps -ErrorAction SilentlyContinue | Out-String
    if (-not $dockerRunning) {
        Write-Host "Docker Desktop 未运行" -ForegroundColor Red
    Write-Host ""
        Write-Host "请先启动Docker Desktop：" -ForegroundColor Yellow
        Write-Host "1. 确认Docker Desktop已安装" -ForegroundColor Gray
        Write-Host "2. 在任务管理器找到Docker Desktop" -ForegroundColor Gray
        Write-Host "3. 启动Docker Desktop" -ForegroundColor Gray
        Write-Host "4. 等待Docker图标出现" -ForegroundColor Gray
    } else {
        Write-Host "Docker正在运行" -ForegroundColor Green
        $containers = docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
        Write-Host ""
        Write-Host $containers
    }
}

function Restart-Container {
    Write-Host ""
    Write-Host "重启API容器..." -ForegroundColor Yellow
    
    docker restart ${API_NAME}
    
    Write-Host "  完成" -ForegroundColor Green
    Write-Host "等待5秒..." -ForegroundColor Gray
    Start-Sleep -Seconds 5
    
    # 显示状态
    docker ps --filter "name=${API_NAME}" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
}

function Stop-Container {
    Write-Host ""
    Write-Host "停止容器..." -ForegroundColor Yellow
    
    docker stop ${API_NAME}
    
    Write-Host "  已停止" -ForegroundColor Green
}

function Show-Logs {
    Write-Host ""
    Write-Host "查看容器日志..." -ForegroundColor Yellow
    Write-Host "按 Ctrl+C 退出" -ForegroundColor Gray
    Write-Host ""
    
    docker logs -f --tail 50 ${API_NAME}
}
