$r = New-Object System.Random
for ($i = 1; $i -le 10; $i++) {
    Write-Host "V$i" -NoNewline
    
    # Random like (50%)
    if ($r.Next(100) -lt 50) {
        Write-Host " L" -NoNewline
        adb shell "input tap 400 800 && sleep 0.08 && input tap 400 800"
    }
    
    # Random favorite (30%)
    if ($r.Next(100) -lt 30) {
        Write-Host " F" -NoNewline
        adb shell input tap 1020 1060
    }
    
    Write-Host ""
    Start-Sleep -Milliseconds 800
    
    # Swipe to next
    adb shell input swipe 540 1500 540 500 150
    Start-Sleep -Milliseconds 1200
}
Write-Host "Done!"
