import ctypes
from ctypes import wintypes
import time

user32 = ctypes.windll.user32

FindWindow = user32.FindWindowW
FindWindowEx = user32.FindWindowExW
GetClassName = user32.GetClassNameW
GetWindowText = user32.GetWindowTextW
SendMessage = user32.SendMessageW
EnumChildWindows = user32.EnumChildWindows

WM_SETTEXT = 0x000C
BM_CLICK = 0x00F5

WNDENUMPROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)

children = []

def enum_callback(hwnd, lparam):
    cls = ctypes.create_unicode_buffer(256)
    txt = ctypes.create_unicode_buffer(256)
    GetClassName(hwnd, cls, 256)
    GetWindowText(hwnd, txt, 256)
    children.append((hwnd, cls.value, txt.value))
    return True

hwnd = FindWindow('#32770', None)
print(f"Dialog: {hwnd}")

if hwnd:
    EnumChildWindows(hwnd, WNDENUMPROC(enum_callback), 0)
    for h, c, t in children:
        print(f"  hwnd={h} class={c} text='{t}'")
    
    file_path = r"D:\video-analysis\output\银针试毒v4\v5\final_v9.mp4"
    for h, c, t in children:
        if c == 'Edit':
            SendMessage(h, WM_SETTEXT, 0, file_path)
            print(f"\nSet path in Edit hwnd={h}")
            break
    
    for h, c, t in children:
        if c == 'Button' and ('打开' in t or 'Open' in t):
            time.sleep(0.3)
            SendMessage(h, BM_CLICK, 0, 0)
            print(f"Clicked: {t}")
            break
else:
    print("No dialog found")
