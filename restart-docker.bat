@echo off
title Restart Docker Desktop
echo Restarting Docker Desktop...
echo.

echo Stopping Docker Desktop...
taskkill /F /IM com.docker.backend.exe /T 2>nul
taskkill /F /IM docker-sandbox.exe /T 2>nul
taskkill /F /IM com.docker.build.exe /T 2>nul
taskkill /F /IM docker.exe /T 2>nul

timeout /t 3 /nobreak > nul

echo Starting Docker Desktop...
start "" "C:\Program Files\Docker\Docker\Docker Desktop.exe"

echo.
echo Waiting for Docker Desktop to be ready...
echo This may take 2-5 minutes...
echo.

timeout /t 30 /nobreak > nul

echo Checking Docker status...
docker ps >nul
if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo Docker Desktop is running!
    echo ========================================
    echo.
    echo Tell me: "Docker Desktop 已启动"
    echo I will deploy the video analysis system!
) else (
    echo.
    echo ========================================
    echo Docker Desktop not ready yet
    echo ========================================
    echo.
    echo Please wait 2-3 more minutes
    echo Then tell me: "Docker Desktop 已启动"
)

echo.
pause
