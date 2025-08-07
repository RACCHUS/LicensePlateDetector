
import sys
import threading
import time
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QLabel, QTextEdit, QVBoxLayout, QHBoxLayout, QStatusBar

# Import backend recognizer
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from license_plate_app import LicensePlateRecognizer, CONFIGURATION



class LicensePlateMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('License Plate Recognition System (PyQt)')
        self.setGeometry(100, 100, 600, 400)
        self._init_ui()
        self.recognition_running = False
        self.recognizer = LicensePlateRecognizer(CONFIGURATION)
        try:
            from license_plate_app import ScreenAutomation
            self.screen_automation = ScreenAutomation()
        except Exception:
            self.screen_automation = None
        self.recognition_thread = None
        self.scan_region = (100, 100, 200, 60)  # Default region

    def _init_ui(self):
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)

        # Layouts

        import sys
        import os
        from PyQt5.QtWidgets import QApplication
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from license_plate_app import LicensePlateRecognizer, CONFIGURATION, ScreenAutomation
        from main_window import LicensePlateMainWindow

        if __name__ == '__main__':
            app = QApplication(sys.argv)
            recognizer = LicensePlateRecognizer(CONFIGURATION)
            screen_automation = ScreenAutomation()
            window = LicensePlateMainWindow(recognizer, screen_automation)
            window.show()
            sys.exit(app.exec_())
        # Results text area
