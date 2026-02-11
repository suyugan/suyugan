@echo off
set DEVICE=192.168.41.203:39075
set OUTDIR=C:\Users\Administrator\.openclaw\workspace\wc_captures

for /L %%i in (2,1,30) do (
    adb -s %DEVICE% shell input swipe 540 1600 540 800 300
    ping -n 2 127.0.0.1 >nul
    if %%i LSS 10 (
        adb -s %DEVICE% shell screencap -p /sdcard/wc_cap0%%i.png
        adb -s %DEVICE% pull /sdcard/wc_cap0%%i.png %OUTDIR%\wc_0%%i.png
    ) else (
        adb -s %DEVICE% shell screencap -p /sdcard/wc_cap%%i.png
        adb -s %DEVICE% pull /sdcard/wc_cap%%i.png %OUTDIR%\wc_%%i.png
    )
)
echo DONE
