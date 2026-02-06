# 测试抖音收藏坐标
# 功能：点击收藏按钮并截图验证

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  抖音收藏坐标测试" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 截取点击前的屏幕
Write-Host "[1/3] 截取点击前的屏幕..." -ForegroundColor Yellow
adb shell screencap -p /sdcard/before_tap.png
Write-Host "✓ 已保存: before_tap.png" -ForegroundColor Green

# 点击收藏坐标
Write-Host "[2/3] 点击收藏按钮 (1010, 1550)..." -ForegroundColor Yellow
adb shell input tap 1010 1550
Start-Sleep -Milliseconds 500
Write-Host "✓ 已点击" -ForegroundColor Green

# 等待抖音反应
Start-Sleep -Milliseconds 1000

# 截取点击后的屏幕
Write-Host "[3/3] 截取点击后的屏幕..." -ForegroundColor Yellow
adb shell screencap -p /sdcard/after_tap.png
Write-Host "✓ 已保存: after_tap.png" -ForegroundColor Green

# 下载截图
Write-Host ""
Write-Host "下载截图到电脑..." -ForegroundColor Yellow
adb pull /sdcard/before_tap.png .\before_tap.png
adb pull /sdcard/after_tap.png .\after_tap.png

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  测试完成！" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "请检查 before_tap.png 和 after_tap.png" -ForegroundColor White
Write-Host ""
Write-Host "对比两张截图，看收藏图标是否发生变化" -ForegroundColor Yellow
Write-Host "- 变白了 = 点击成功" -ForegroundColor Green
Write-Host "- 没变化 = 坐标错误" -ForegroundColor Red
Write-Host ""
