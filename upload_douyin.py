import time
import pyautogui
import pyperclip

# Wait for file dialog to appear
time.sleep(2)

# Type file path into the file name field
file_path = r"D:\video-analysis\output\银针试毒v4\v5\final_v9.mp4"
pyperclip.copy(file_path)
pyautogui.hotkey('ctrl', 'v')
time.sleep(0.5)
pyautogui.press('enter')
print("Done - file path entered and confirmed")
