
import threading
import time
from utils.state_filters import is_state_name_or_abbreviation
from .notifier import Notifier
from .logger import log_info, log_error
from PyQt5.QtCore import QObject, pyqtSignal


from utils.chrome_messaging import send_plate_to_chrome

class RecognitionController(QObject):
    result_signal = pyqtSignal(str)
    error_signal = pyqtSignal(str)
    status_signal = pyqtSignal(str)

    """Handles the recognition thread and logic for license plate detection."""
    def __init__(self, main_widget):
        super().__init__()
        self.main_widget = main_widget
        self._thread = None
        self.running = False

    def start(self):
        if not self.running:
            self.running = True
            self._thread = threading.Thread(target=self._loop, daemon=True)
            self._thread.start()

    def stop(self):
        self.running = False

    def _loop(self):
        while self.running:
            try:
                if self.main_widget.screen_automation:
                    img = self.main_widget.screen_automation.capture_screen_region(self.main_widget.scan_region)
                    text, conf, alert = self.main_widget.recognizer.recognize_license_plate(img)
                    now = time.strftime('%H:%M:%S')
                    detected_state = None
                    if text and is_state_name_or_abbreviation(text):
                        detected_state = text
                    if text:
                        state_info = f" | State: {detected_state}" if detected_state else ""
                        self.result_signal.emit(f"{now} - Detected: {text} (Conf: {conf:.2f}){state_info}")
                        # Send recognized plate to Chrome extension
                        send_plate_to_chrome(text)
                        if not alert and self.main_widget.target_field:
                            self.main_widget.screen_automation.click_and_type(text, self.main_widget.target_field)
                            self.result_signal.emit(f"{now} - Auto-inserted: {text}")
                        elif alert:
                            self.result_signal.emit(f"{now} - Manual confirmation needed")
                            self.status_signal.emit(f"Manual confirmation needed for: {text}")
                    else:
                        self.result_signal.emit(f"{now} - No plate detected.")
                else:
                    self.error_signal.emit("ScreenAutomation not available.")
            except Exception as e:
                self.error_signal.emit(f"Recognition error: {e}")
            try:
                interval = float(self.main_widget.interval_entry.text())
                if interval < 0.1:
                    interval = 0.1
            except Exception:
                interval = 2.0
            time.sleep(interval)
