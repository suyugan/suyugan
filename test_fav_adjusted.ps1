# Test adjusted favorite coordinate
# Function: Click favorite button and screenshot

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Adjusted Favorite Coordinate Test" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Original: (1010, 1550)" -ForegroundColor Gray
Write-Host "Adjusted: (842, 1292) [divided by 1.2]" -ForegroundColor Yellow
Write-Host ""

# Click favorite (adjusted)
Write-Host "[1/2] Clicking favorite at (842, 1292)..." -ForegroundColor Yellow
adb shell input tap 842 1292
Start-Sleep -Milliseconds 500
Write-Host "Done" -ForegroundColor Green

# Wait for reaction
Start-Sleep -Milliseconds 1000

# Screenshot
Write-Host "[2/2] Taking screenshot..." -ForegroundColor Yellow
adb shell screencap -p /sdcard/test_fav_adjusted.png
Write-Host "Saved: test_fav_adjusted.png" -ForegroundColor Green

# Download
Write-Host ""
Write-Host "Downloading..." -ForegroundColor Yellow
adb pull /sdcard/test_fav_adjusted.png .\test_fav_adjusted.png

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Complete!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Check test_fav_adjusted.png" -ForegroundColor White
Write-Host ""
Write-Host "Look for the star icon to turn white" -ForegroundColor Yellow
