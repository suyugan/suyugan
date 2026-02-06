#!/usr/bin/env python3
"""
Phone Control Script - Control Android phone via ADB
Usage: python phone.py <command> [args]

Commands:
  status          Check connection status
  connect <port>  Connect to phone
  screen          Take screenshot
  tap <x> <y>     Tap at coordinates
  swipe <x1> <y1> <x2> <y2>  Swipe
  back            Back key
  home            Home key
  app <name>      Open app (meituan/wechat/taobao/douyin)
"""

import subprocess
import sys
import os

PHONE_IP = "192.168.41.203"
WORKSPACE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# App package mappings
APPS = {
    "meituan": "com.sankuai.meituan/com.meituan.android.pt.homepage.activity.MainActivity",
    "wechat": "com.tencent.mm/.ui.LauncherUI",
    "taobao": "com.taobao.taobao/com.taobao.tao.TBMainActivity",
    "douyin": "com.ss.android.ugc.aweme/.main.MainActivity",
}

def run_adb(cmd, device=None):
    """Run ADB command"""
    full_cmd = ["adb"]
    if device:
        full_cmd.extend(["-s", device])
    full_cmd.extend(cmd)
    result = subprocess.run(full_cmd, capture_output=True, text=True)
    return result.stdout + result.stderr, result.returncode

def get_device():
    """Get connected device"""
    output, _ = run_adb(["devices"])
    lines = output.strip().split('\n')[1:]
    for line in lines:
        if PHONE_IP in line and 'device' in line:
            return line.split()[0]
    return None

def status():
    """Check connection status"""
    device = get_device()
    if device:
        print(f"[OK] Phone connected: {device}")
        return True
    else:
        print("[FAIL] Phone not connected")
        return False

def connect(port):
    """Connect to phone"""
    target = f"{PHONE_IP}:{port}"
    output, code = run_adb(["connect", target])
    print(output)
    return code == 0 and "connected" in output

def screen():
    """Take screenshot"""
    device = get_device()
    if not device:
        print("[FAIL] Phone not connected")
        return False
    
    # Screenshot on phone
    run_adb(["shell", "screencap", "-p", "/sdcard/screen.png"], device)
    # Pull to local
    output_path = os.path.join(WORKSPACE, "phone_screen.png")
    output, code = run_adb(["pull", "/sdcard/screen.png", output_path], device)
    if code == 0:
        print(f"[OK] Screenshot saved: {output_path}")
        return True
    else:
        print(f"[FAIL] Screenshot failed: {output}")
        return False

def tap(x, y):
    """Tap at coordinates"""
    device = get_device()
    if not device:
        print("[FAIL] Phone not connected")
        return False
    run_adb(["shell", "input", "tap", str(x), str(y)], device)
    print(f"[OK] Tap ({x}, {y})")
    return True

def swipe(x1, y1, x2, y2, duration=300):
    """Swipe"""
    device = get_device()
    if not device:
        print("[FAIL] Phone not connected")
        return False
    run_adb(["shell", "input", "swipe", str(x1), str(y1), str(x2), str(y2), str(duration)], device)
    print(f"[OK] Swipe ({x1},{y1}) -> ({x2},{y2})")
    return True

def back():
    """Back key"""
    device = get_device()
    if not device:
        print("[FAIL] Phone not connected")
        return False
    run_adb(["shell", "input", "keyevent", "4"], device)
    print("[OK] Back")
    return True

def home():
    """Home key"""
    device = get_device()
    if not device:
        print("[FAIL] Phone not connected")
        return False
    run_adb(["shell", "input", "keyevent", "3"], device)
    print("[OK] Home")
    return True

def open_app(name):
    """Open app"""
    device = get_device()
    if not device:
        print("[FAIL] Phone not connected")
        return False
    
    if name not in APPS:
        print(f"[FAIL] Unknown app: {name}")
        print(f"Supported: {', '.join(APPS.keys())}")
        return False
    
    activity = APPS[name]
    run_adb(["shell", "am", "start", "-n", activity], device)
    print(f"[OK] Opened {name}")
    return True

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    
    cmd = sys.argv[1]
    
    if cmd == "status":
        status()
    elif cmd == "connect" and len(sys.argv) >= 3:
        connect(sys.argv[2])
    elif cmd == "screen":
        screen()
    elif cmd == "tap" and len(sys.argv) >= 4:
        tap(int(sys.argv[2]), int(sys.argv[3]))
    elif cmd == "swipe" and len(sys.argv) >= 6:
        duration = int(sys.argv[6]) if len(sys.argv) >= 7 else 300
        swipe(int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]), duration)
    elif cmd == "back":
        back()
    elif cmd == "home":
        home()
    elif cmd == "app" and len(sys.argv) >= 3:
        open_app(sys.argv[2])
    else:
        print(__doc__)

if __name__ == "__main__":
    main()
