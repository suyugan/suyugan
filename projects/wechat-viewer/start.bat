@echo off
chcp 65001 >nul
echo ========================================
echo   微信群聊截图展示系统
echo ========================================
echo.

cd /d "%~dp0"

:: 检查 node_modules
if not exist "node_modules" (
    echo 📦 首次运行，正在安装依赖...
    call npm install
    echo.
)

echo 🚀 启动服务器...
echo 📍 访问地址: http://localhost:3000
echo.
echo 按 Ctrl+C 可停止服务
echo ========================================
echo.

node server.js
pause
