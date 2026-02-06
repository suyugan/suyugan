@echo off
echo ========================================
echo   芝麻组队工具 - 启动脚本
echo ========================================
echo.

echo [1] 前端 - 本地开发 (http://localhost:3000)
echo [2] 后端 - 本地开发 (http://localhost:5001)
echo [3] Docker - 完整部署 (http://localhost:3000)
echo [4] 全部启动 - 前端+后端
echo [5] 退出
echo.

set /p choice=请选择启动方式:

if "%choice%"=="1" (
    echo.
    echo 启动前端开发服务器...
    cd frontend
    npm run dev
) else if "%choice%"=="2" (
    echo.
    echo 启动后端服务器...
    cd backend
    npm run dev
) else if "%choice%"=="3" (
    echo.
    echo 启动 Docker 容器...
    docker-compose up -d
    echo.
    echo 访问地址: http://localhost:3000
) else if "%choice%"=="4" (
    echo.
    echo 同时启动前端和后端...
    start "前端" cmd /k "cd frontend && npm run dev"
    start "后端" cmd /k "cd backend && npm run dev"
    echo.
    echo 前端: http://localhost:3000
    echo 后端: http://localhost:5001
) else if "%choice%"=="5" (
    echo.
    echo 退出...
    exit
) else (
    echo.
    echo 无效的选择，请重新运行脚本
    pause
)
