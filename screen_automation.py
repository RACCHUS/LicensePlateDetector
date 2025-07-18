import pyautogui
from typing import Tuple, Optional
import cv2
import numpy as np

class ScreenAutomation:
    def __init__(self):
        self.target_field: Optional[Tuple[int, int]] = None
        self.field_template: Optional[np.ndarray] = None

    def capture_screen_region(self, region: Tuple[int, int, int, int]) -> np.ndarray:
        screenshot = pyautogui.screenshot(region=region)
        return cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

    def find_text_field(self, template: np.ndarray) -> Optional[Tuple[int, int]]:
        screenshot = pyautogui.screenshot()
        screen_image = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        result = cv2.matchTemplate(screen_image, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        if max_val > 0.8:
            self.target_field = (max_loc[0] + template.shape[1] // 2, max_loc[1] + template.shape[0] // 2)
            return self.target_field
        return None

    def click_and_type(self, text: str, position: Tuple[int, int]):
        pyautogui.click(position)
        pyautogui.hotkey('ctrl', 'a')
        pyautogui.press('delete')
        pyautogui.write(text, interval=0.1)
