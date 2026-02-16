import time
import pyautogui
import subprocess

# Wait for file dialog
time.sleep(3)

# Use SendKeys via PowerShell for reliability with CJK paths
# Type the path directly using keyboard
file_path = r"D:\video-analysis\output\银针试毒v4\v5\final_v9.mp4"

# Use Win32 to find and interact with the Open dialog
import ctypes
from ctypes import wintypes

user32 = ctypes.windll.user32
FindWindow = user32.FindWindowW
FindWindowEx = user32.FindWindowExW
SendMessage = user32.SendMessageW

WM_SETTEXT = 0x000C
BM_CLICK = 0x00F5

# Find the Open dialog (common dialog class #32770)
hwnd = FindWindow('#32770', None)
print(f"Dialog hwnd: {hwnd}")

if hwnd:
    # Find the ComboBoxEx32 (filename field) 
    combo = FindWindowEx(hwnd, 0, 'ComboBoxEx32', None)
    print(f"ComboBoxEx32: {combo}")
    if combo:
        edit = FindWindowEx(combo, 0, 'ComboBox', None)
        if edit:
            edit2 = FindWindowEx(edit, 0, 'Edit', None)
            if edit2:
                SendMessage(edit2, WM_SETTEXT, 0, file_path)
                print(f"Set text in Edit: {edit2}")
    
    # Find and click the Open button
    btn = FindWindowEx(hwnd, 0, 'Button', '打开(&O)')
    if not btn:
        btn = FindWindowEx(hwnd, 0, 'Button', 'Open')
    if not btn:
        btn = FindWindowEx(hwnd, 0, 'Button', '&Open')
    print(f"Open button: {btn}")
    if btn:
        SendMessage(btn, BM_CLICK, 0, 0)
        print("Clicked Open button")
else:
    print("No dialog found, trying pyautogui fallback")
    pyautogui.typewrite(r"D:\video-analysis\output", interval=0.02)
    time.sleep(0.3)
    pyautogui.press('enter')
