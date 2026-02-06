@echo off
echo ========================================
echo Checking Docker Desktop and Deploying
echo ========================================
echo.

echo [1/4] Checking Docker Desktop...
tasklist | findstr /I "docker desktop" > nul
if %errorlevel% equ 0 (
    echo [2/4] Docker Desktop is running!
    goto :deploy
) else (
    echo [2/4] Docker Desktop not running
    goto :no-docker
)

:no-docker
echo.
echo Error: Docker Desktop is not running
echo.
echo Please:
echo   1. Start Docker Desktop manually first
echo   2. Or tell me to deploy using docker commands directly
echo.
echo ========================================
echo.
pause
