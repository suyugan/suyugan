@echo off
title Force Uninstall Docker Desktop
echo ========================================
echo Force Uninstall Docker Desktop
echo ========================================
echo.

echo [1/4] Stopping all Docker processes...
taskkill /F /IM com.docker.backend.exe /T 2>nul
taskkill /F /IM docker-sandbox.exe /T 2>nul
taskkill /F /IM com.docker.build.exe /T 2>nul
taskkill /F /IM Docker.Desktop.exe /T 2>nul
taskkill /F /IM docker.exe /T 2>nul

timeout /t 3 /nobreak > nul

echo [2/4] Stopping Docker Desktop services...
net stop com.docker.backend 2>nul
net stop com.docker.service 2>nul

echo [3/4] Running uninstaller...
set UNINSTALLER=%PROGRAMFILES%\Docker\Docker\Docker Desktop.exe
if exist "%UNINSTALLER%" (
    "%UNINSTALLER%" /uninstall /S
    echo Uninstaller started
) else (
    echo Uninstaller not found, removing files manually...
    rmdir /S /Q "%PROGRAMFILES%\Docker" 2>nul
    rmdir /S /Q "%LOCALAPPDATA%\Docker" 2>nul
    rmdir /S /Q "%APPDATA%\Docker" 2>nul
)

echo [4/4] Cleaning registry...
reg delete "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Docker Desktop" /f 2>nul
reg delete "HKCU\Software\Docker Inc." /f 2>nul

echo.
echo ========================================
echo Uninstallation Complete!
echo ========================================
echo.
echo Please restart your computer
echo Then reinstall Docker Desktop from:
echo https://www.docker.com/products/docker-desktop/
echo.
echo ========================================
pause
