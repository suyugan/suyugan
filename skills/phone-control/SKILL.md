---
name: phone-control
description: 远程控制苏总的安卓手机（moto g54）。用于：点外卖、打开App、截屏查看、模拟点击等操作。当用户说"帮我点外卖"、"打开美团/微信/淘宝"、"看看手机屏幕"、"手机截图"时触发此技能。
---

# 手机远程控制

通过ADB无线调试控制苏总的 moto g54 手机。

## 连接信息

手机IP固定为 `192.168.41.203`，但端口会变。连接前先检查 TOOLS.md 中的端口配置。

## 常用命令

### 检查连接状态
```bash
adb devices
```

### 重新连接（如果掉线）
```bash
adb connect 192.168.41.203:<端口>
```
如果连接失败，需要用户提供新的配对码和端口重新配对。

### 截图
```bash
adb -s 192.168.41.203:<端口> shell screencap -p /sdcard/screen.png
adb -s 192.168.41.203:<端口> pull /sdcard/screen.png phone_screen.png
```

### 打开App
```bash
# 美团
adb -s 192.168.41.203:<端口> shell am start -n com.sankuai.meituan/com.meituan.android.pt.homepage.activity.MainActivity

# 微信
adb -s 192.168.41.203:<端口> shell am start -n com.tencent.mm/.ui.LauncherUI

# 淘宝
adb -s 192.168.41.203:<端口> shell am start -n com.taobao.taobao/com.taobao.tao.TBMainActivity

# 抖音
adb -s 192.168.41.203:<端口> shell am start -n com.ss.android.ugc.aweme/.main.MainActivity
```

### 模拟点击
```bash
adb -s 192.168.41.203:<端口> shell input tap <x> <y>
```
屏幕分辨率：1080x2400

### 模拟滑动
```bash
adb -s 192.168.41.203:<端口> shell input swipe <x1> <y1> <x2> <y2> <duration_ms>
```

### 输入文字
```bash
adb -s 192.168.41.203:<端口> shell input text "hello"
```
注意：中文需要用ADBKeyboard或剪贴板方式

### 按键
```bash
# 返回
adb -s 192.168.41.203:<端口> shell input keyevent 4
# Home
adb -s 192.168.41.203:<端口> shell input keyevent 3
# 最近任务
adb -s 192.168.41.203:<端口> shell input keyevent 187
```

## 工作流程

1. **先检查连接**：运行 `adb devices` 确认手机在线
2. **如果离线**：尝试重新连接，失败则让用户提供新端口
3. **截图确认**：每次操作后截图，确认界面状态
4. **根据截图操作**：分析截图内容，计算点击坐标

## 点外卖流程

1. 打开美团
2. 截图确认进入首页
3. 点击「外卖」图标（约坐标 80, 290）
4. 进入外卖页面后，根据用户需求操作

## 注意事项

- 端口会变，每次操作前确认连接
- 操作间隔留1-2秒等待页面加载
- 复杂操作需要多次截图确认
- 如果连续失败，让用户检查手机无线调试是否开启
- **视频/动画播放时不能用uiautomator dump**（UI无法idle），改用坐标直接tap
- **⚠️ adb screencap的图片分辨率可能与设备不同**（如900x2000 vs 1080x2400），点击坐标需乘以缩放比例（1080/图片宽度）
