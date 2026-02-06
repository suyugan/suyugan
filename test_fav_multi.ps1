# Test Douyin Favorite Multi-Coordinates
# Test different positions to find correct favorite button

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Favorite Coordinate Multi-Test" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Test positions list (based on 1080x2400)
$positions = @(
    @{Name="Pos1-Original"; X=1000; Y=1550},
    @{Name="Pos2-Adjusted"; X=842; Y=1292},
    @{Name="Pos3-Right"; X=1100; Y=1292},
    @{Name="Pos4-FarRight"; X=1200; Y=1292},
    @{Name="Pos5-Bottom"; X=842; Y=1600}
)

for ($i = 0; $i -lt $positions.Count; $i++) {
    $pos = $positions[$i]
    Write-Host "[$($i+1)/5] Testing $($pos.Name) - ($($pos.X), $($pos.Y))" -ForegroundColor Yellow
    
    # Tap
    adb shell input tap $pos.X $pos.Y
    Start-Sleep -Milliseconds 300
    
    # Screenshot
    adb shell screencap -p "/sdcard/fav_test_$($i+1).png"
    Start-Sleep -Milliseconds 500
}

# Download all screenshots
Write-Host ""
Write-Host "Downloading screenshots..." -ForegroundColor Cyan
for ($i = 1; $i -le $positions.Count; $i++) {
    adb pull "/sdcard/fav_test_$($i).png" ".\fav_test_$($i).png" 2>$null
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Compare 5 screenshots:" -ForegroundColor White
Write-Host "- Which one has a white star = correct position" -ForegroundColor Green
Write-Host "- Tell me the number (1-5)" -ForegroundColor Yellow
Write-Host ""
