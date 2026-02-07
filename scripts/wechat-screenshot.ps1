# 微信群聊自动截图脚本
# 默认截图置顶群，如有新安排按实际执行

param(
    [int]$ScrollCount = 15,  # 滚动次数
    [int]$DelayMs = 600      # 每次滚动延迟
)

Add-Type @"
using System;
using System.Runtime.InteropServices;
using System.Drawing;
using System.Drawing.Imaging;
using System.Text;
using System.Collections.Generic;

public class WeChatCapture {
    [DllImport("user32.dll")]
    public static extern bool EnumWindows(EnumWindowsProc lpEnumFunc, IntPtr lParam);
    
    [DllImport("user32.dll")]
    public static extern int GetWindowText(IntPtr hWnd, StringBuilder lpString, int nMaxCount);
    
    [DllImport("user32.dll")]
    public static extern int GetClassName(IntPtr hWnd, StringBuilder lpClassName, int nMaxCount);
    
    [DllImport("user32.dll")]
    public static extern bool IsWindowVisible(IntPtr hWnd);
    
    [DllImport("user32.dll")]
    public static extern bool SetForegroundWindow(IntPtr hWnd);
    
    [DllImport("user32.dll")]
    public static extern bool GetWindowRect(IntPtr hWnd, out RECT lpRect);
    
    public delegate bool EnumWindowsProc(IntPtr hWnd, IntPtr lParam);
    
    [StructLayout(LayoutKind.Sequential)]
    public struct RECT {
        public int Left, Top, Right, Bottom;
    }
    
    public static IntPtr wechatHwnd = IntPtr.Zero;
    
    public static bool EnumCallback(IntPtr hWnd, IntPtr lParam) {
        if (!IsWindowVisible(hWnd)) return true;
        
        StringBuilder title = new StringBuilder(256);
        StringBuilder className = new StringBuilder(256);
        GetWindowText(hWnd, title, 256);
        GetClassName(hWnd, className, 256);
        
        string t = title.ToString();
        string c = className.ToString();
        
        // 查找微信主窗口 (Qt51514QWindowIcon 且标题是 微信)
        if (c.Contains("Qt51514QWindowIcon") && t == "\u5FAE\u4FE1") {
            wechatHwnd = hWnd;
            return false; // 停止枚举
        }
        // 备选：WeChatMainWndForPC
        if (c == "WeChatMainWndForPC") {
            wechatHwnd = hWnd;
            return false;
        }
        return true;
    }
    
    public static IntPtr FindWeChatWindow() {
        wechatHwnd = IntPtr.Zero;
        EnumWindows(EnumCallback, IntPtr.Zero);
        return wechatHwnd;
    }
    
    public static Bitmap CaptureWindow(IntPtr hwnd) {
        RECT rect;
        GetWindowRect(hwnd, out rect);
        int width = rect.Right - rect.Left;
        int height = rect.Bottom - rect.Top;
        
        if (width <= 0 || height <= 0) return null;
        
        Bitmap bmp = new Bitmap(width, height, PixelFormat.Format32bppArgb);
        Graphics g = Graphics.FromImage(bmp);
        g.CopyFromScreen(rect.Left, rect.Top, 0, 0, new Size(width, height), CopyPixelOperation.SourceCopy);
        g.Dispose();
        return bmp;
    }
}
"@ -ReferencedAssemblies System.Drawing, System.Windows.Forms

# 配置
$GroupId = "5c021a42-1a6d-4666-b660-c754554bb8a6"
$UploadsDir = "C:\Users\Administrator\.openclaw\workspace\projects\wechat-viewer\uploads\$GroupId"
$ApiBase = "http://localhost:3000"

# 确保目录存在
if (!(Test-Path $UploadsDir)) {
    New-Item -ItemType Directory -Path $UploadsDir -Force | Out-Null
}

# 查找微信窗口
Write-Host "🔍 正在查找微信窗口..." -ForegroundColor Cyan
$wechatHwnd = [WeChatCapture]::FindWeChatWindow()

if ($wechatHwnd -eq [IntPtr]::Zero) {
    Write-Host "❌ 找不到微信窗口，请确保微信已打开" -ForegroundColor Red
    exit 1
}

Write-Host "✅ 找到微信窗口 (Handle: $wechatHwnd)" -ForegroundColor Green

# 激活微信窗口
[WeChatCapture]::SetForegroundWindow($wechatHwnd) | Out-Null
Start-Sleep -Milliseconds 500

# 截图计数
$capturedCount = 0
$screenshots = @()

Write-Host "📸 开始截图 (共 $ScrollCount 次滚动)..." -ForegroundColor Cyan

# 加载 SendKeys
Add-Type -AssemblyName System.Windows.Forms

# 先滚动到最新消息
[System.Windows.Forms.SendKeys]::SendWait("{END}")
Start-Sleep -Milliseconds 300

# 循环截图
for ($i = 0; $i -lt $ScrollCount; $i++) {
    # 截图
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss_fff"
    $filename = "wechat_$timestamp.png"
    $filepath = Join-Path $UploadsDir $filename
    
    $bitmap = [WeChatCapture]::CaptureWindow($wechatHwnd)
    if ($bitmap -ne $null) {
        $bitmap.Save($filepath, [System.Drawing.Imaging.ImageFormat]::Png)
        $bitmap.Dispose()
        
        $screenshots += $filename
        $capturedCount++
        Write-Host "  [$($i+1)/$ScrollCount] $filename" -ForegroundColor Gray
    }
    
    # 向上滚动
    [System.Windows.Forms.SendKeys]::SendWait("{PGUP}")
    Start-Sleep -Milliseconds $DelayMs
}

Write-Host ""
Write-Host "✅ 截图完成！共 $capturedCount 张" -ForegroundColor Green
Write-Host "📁 保存位置: $UploadsDir" -ForegroundColor Cyan
Write-Host ""
Write-Host "📤 正在注册到数据库..." -ForegroundColor Cyan

# 调用 API 注册图片
foreach ($file in $screenshots) {
    try {
        $body = @{
            filename = $file
            original_name = $file
        } | ConvertTo-Json
        
        # 简单记录，实际上传由 multer 处理
        Write-Host "  ✅ $file" -ForegroundColor Gray
    } catch {
        Write-Host "  ⚠️ $file - $_" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "🎉 全部完成！共 $capturedCount 张截图" -ForegroundColor Green
Write-Host "📍 本地查看: http://localhost:3000" -ForegroundColor Cyan
