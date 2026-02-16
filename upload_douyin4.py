import time
import pyautogui
import pyperclip

# Wait for file dialog to fully appear
time.sleep(4)

# The file dialog should be focused. The filename field should be active.
# Clear any existing text first
pyautogui.hotkey('ctrl', 'a')
time.sleep(0.2)

# Copy path to clipboard and paste (handles CJK characters)
file_path = r"D:\video-analysis\output\银针试毒v4\v5\final_v9.mp4"
pyperclip.copy(file_path)
time.sleep(0.2)
pyautogui.hotkey('ctrl', 'v')
time.sleep(1)

# Press Enter to confirm
pyautogui.press('enter')
time.sleep(0.5)
pyautogui.press('enter')  # Sometimes need double enter
print("Done")
