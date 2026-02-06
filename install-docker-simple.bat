@echo off
echo Docker Desktop Installer
echo ================================
echo.

echo Looking for Docker Desktop installer...
echo.

set DOWNLOADS_DIR=%USERPROFILE%\Downloads
set FOUND_INSTALLER=0

dir "%DOWNLOADS_DIR%\Docker*.exe" /b >nul
if %ERRORLEVEL% equ 0 (
    echo Found installer file(s)
    dir "%DOWNLOADS_DIR%\Docker*.exe" /b
    for %%f in (*.exe) (
        echo Installing: %%f
        start /wait ""%%f"
        set FOUND_INSTALLER=1
    goto :done
)

:done
echo.
if %FOUND_INSTALLER% equ 0 (
    echo ERROR: No Docker Desktop installer found
    echo Please open browser manually: https://www.docker.com/products/docker-desktop/
    goto :end
)

echo ================================
echo Installation Complete!
echo ================================
echo.
echo Next Steps:
echo 1. Wait for Docker Desktop to be ready (whale icon in system tray)
echo 2. Send: deploy
echo.
echo I will auto-deploy the video analysis system!
echo ================================

:end
echo.
pause
