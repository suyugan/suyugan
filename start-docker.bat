@echo off
echo ========================================
echo Starting Docker Desktop
echo ========================================
echo.

echo Method 1: Program Files
start "" "C:\Program Files\Docker\Docker\Docker Desktop.exe"

echo Method 2: Local AppData
start "" "%LOCALAPPDATA%\Docker\Docker Desktop.exe"

echo Method 3: Search PATH
for %%f in (docker.exe) do (
    start "" %%f
    goto :found
)
:found
echo.
echo ========================================
echo Docker Desktop should be starting...
echo ========================================
echo.
echo After it starts:
echo 1. Configure Cookie in:
echo    C:\Users\Administrator\.openclaw\video-analysis\data\douyin_web\config.yaml
echo.
echo 2. Test API:
echo    http://localhost:18810/docs
echo.
pause
