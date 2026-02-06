@echo off
title Uninstall Docker Desktop
echo ========================================
echo Uninstalling Docker Desktop...
echo ========================================
echo.

echo Method 1: Running uninstaller
echo.

set UNINSTALLER=%PROGRAMFILES%\Docker\Docker\Docker Desktop.exe
if exist "%UNINSTALLER%" (
    echo Found uninstaller at: %UNINSTALLER%
    echo Starting uninstallation...
    "%UNINSTALLER%" /uninstall
    goto :end
)

echo Error: Uninstaller not found
echo.
echo Please uninstall manually:
echo 1. Control Panel ^> Programs and Features
echo 2. Find Docker Desktop
echo 3. Right click ^> Uninstall
echo.

:end
echo.
echo ========================================
echo Uninstallation process completed
echo ========================================
echo.
pause
