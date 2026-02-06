@echo off
title Docker Desktop Force Cleanup
echo ========================================
echo Docker Desktop Force Cleanup
echo ========================================
echo.

echo [1/6] Stopping Docker processes...
taskkill /F /IM com.docker.backend.exe /T 2>nul
taskkill /F /IM docker-sandbox.exe /T 2>nul
taskkill /F /IM docker.exe /T 2>nul
taskkill /F /IM com.docker.build.exe /T 2>nul

echo [2/6] Stopping services...
net stop com.docker.backend 2>nul
net stop com.docker.service 2>nul

echo [3/6] Removing directories...
rmdir /S /Q "C:\Program Files\Docker" 2>nul
rmdir /S /Q "%LOCALAPPDATA%\Docker" 2>nul
rmdir /S /Q "%APPDATA%\Docker" 2>nul
rmdir /S /Q "%USERPROFILE%\.docker" 2>nul

echo [4/6] Cleaning registry...
reg delete "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Docker Desktop" /f 2>nul
reg delete "HKCU\Software\Docker Inc." /f 2>nul
reg delete "HKLM\SOFTWARE\Docker Inc." /f 2>nul

echo [5/6] Removing shortcuts...
del "%PUBLIC%\Desktop\Docker Desktop.lnk" 2>nul
del "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Docker Desktop.lnk" 2>nul

echo [6/6] Verifying...
if exist "C:\Program Files\Docker" (
    echo Some files remain - may need manual cleanup
) else (
    echo Docker Desktop uninstalled successfully!
)

echo.
echo ========================================
echo Cleanup Complete!
echo ========================================
echo.
echo Next Steps:
echo 1. Restart computer (recommended)
echo 2. Download: https://www.docker.com/products/docker-desktop/
echo 3. Reinstall Docker Desktop
echo.
echo After installation, tell me:
echo "Docker Desktop installed"
echo I will deploy the video analysis system!
echo.
pause
