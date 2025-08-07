import pyautogui
import cv2
import numpy as np
import time

class ScreenAutomation:
    def __init__(self):
        self.target_field = None
        self.field_template = None

    def capture_screen_region(self, region=None):
        """Capture screen or specific region"""
        if region:
            return pyautogui.screenshot(region=region)
        return pyautogui.screenshot()

    def find_text_field(self, template_image=None):
        """Find text input field on screen"""
        if template_image:
            # Use template matching
            screenshot = np.array(pyautogui.screenshot())
            template = np.array(template_image)
            result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            if max_val > 0.8:  # Good match
                return max_loc
        # Fallback: look for cursor or active field
        return pyautogui.position()  # Return current mouse position

    def click_and_type(self, text, position=None):
        """Click on position and type text"""
        if position:
            pyautogui.click(position)
        # Clear existing text
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.1)
        # Type new text
        pyautogui.typewrite(text)
