$r = New-Object System.Random
for ($i = 1; $i -le 8; $i++) {
    Write-Host "Video $i"
    
    # Watch for a bit
    Start-Sleep -Seconds 2
    
    # Random like (50% chance) - double tap center
    if ($r.Next(100) -lt 50) {
        Write-Host "  -> Like"
        adb shell input tap 540 900
        Start-Sleep -Milliseconds 100
        adb shell input tap 540 900
        Start-Sleep -Milliseconds 500
    }
    
    # Random favorite (30% chance) - tap star button
    if ($r.Next(100) -lt 30) {
        Write-Host "  -> Favorite"
        adb shell input tap 1000 925
        Start-Sleep -Milliseconds 500
    }
    
    # Watch more
    Start-Sleep -Seconds 2
    
    # Swipe up to next video
    adb shell input swipe 540 1600 540 600 300
    Start-Sleep -Milliseconds 500
}
Write-Host "Done!"
