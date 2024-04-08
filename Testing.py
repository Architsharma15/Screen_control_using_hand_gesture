import pyautogui
import time
# Disable the fail-safe feature
pyautogui.FAILSAFE = False
# Small delay before PyAutoGUI starts
time.sleep(2)
# Move the mouse to several locations on the screen
pyautogui.moveTo(100, 100, duration=1)
pyautogui.moveTo(200, 100, duration=1)
pyautogui.moveTo(200, 200, duration=1)
pyautogui.moveTo(100, 200, duration=1)