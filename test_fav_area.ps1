# Test Favorite Coordinate Area
# Function: Test coordinates around the favorite button

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Favorite Area Test" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Test coordinates around known position
$testCoords = @(
    @{Name="CenterRight"; X=950; Y=1292},
    @{Name="RightShift"; X=1000; Y=1292},
    @{Name="RightShift2"; X=1050; Y=1292},
    @{Name="RightShift3"; X=1100; Y=1292},
    @{Name="DownShift"; X=842; Y=1350},
    @{Name="DownShift2"; X=842; Y=1400}
)

Write-Host "Testing coordinates..." -ForegroundColor Yellow
Write-Host ""

for ($i = 0; $i -lt $testCoords.Count; $i++) {
    $coord = $testCoords[$i]
    Write-Host "[$($i+1)/$($testCoords.Count)] Testing $($coord.Name) - ($($coord.X), $($coord.Y))" -ForegroundColor Yellow
    
    adb shell input tap $coord.X $coord.Y
    Start-Sleep -Milliseconds 500
    Start-Sleep -Milliseconds 500
    
    adb shell screencap -p "/sdcard/area_test_$($i+1).png"
    Start-Sleep -Milliseconds 200
}

Write-Host ""
Write-Host "Downloading screenshots..." -ForegroundColor Cyan
for ($i = 1; $i -le $testCoords.Count; $i++) {
    adb pull "/sdcard/area_test_$($i).png" ".\area_test_$($i).png" 2>$null
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Test Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Check area_test_*.png" -ForegroundColor White
Write-Host "Look for star icon turning gray" -ForegroundColor Yellow
Write-Host "(Means favorite button was clicked)" -ForegroundColor Gray
Write-Host ""
