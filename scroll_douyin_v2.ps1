# Auto-scroll Douyin (v2 - add favorite)
# Function: Auto scroll, like, and favorite

$r = New-Object System.Random
$count = 8

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Douyin Auto-Scroll v2" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Settings: $count videos" -ForegroundColor Yellow
Write-Host ""

# Adjusted coordinates
$likeX = 842
$likeY = 1292
$favX = 1000
$favY = 1550
$swipeX1 = 540
$swipeY1 = 1600
$swipeY2 = 600

$likedCount = 0
$favCount = 0

for ($i = 1; $i -le $count; $i++) {
    Write-Host "Video $i / $count" -ForegroundColor Cyan
    
    Start-Sleep -Seconds 2
    
    # Like (always)
    Write-Host "  -> Like (fixed)" -ForegroundColor Green
    adb shell input tap $likeX $likeY
    Start-Sleep -Milliseconds 100
    adb shell input tap $likeX $likeY
    Start-Sleep -Milliseconds 500
    $likedCount++
    
    # Favorite (always)
    Write-Host "  -> Favorite (fixed)" -ForegroundColor Yellow
    adb shell input tap $favX $favY
    Start-Sleep -Milliseconds 500
    $favCount++
    
    Start-Sleep -Seconds 2
    
    # Swipe to next
    Write-Host "  -> Swipe next" -ForegroundColor Gray
    adb shell input swipe $swipeX1 $swipeY1 $swipeX1 $swipeY2 300
    Start-Sleep -Milliseconds 500
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Done!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Stats:" -ForegroundColor Cyan
Write-Host "  Liked: $likedCount" -ForegroundColor Green
Write-Host "  Favorited: $favCount" -ForegroundColor Yellow
Write-Host ""
