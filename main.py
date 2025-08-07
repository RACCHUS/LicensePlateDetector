import sys
from PyQt5.QtWidgets import QApplication
from gui.main_window import LicensePlateMainWindow
from recognizer.recognizer import LicensePlateRecognizer, CONFIGURATION, ScreenAutomation

if __name__ == "__main__":
    app = QApplication(sys.argv)
    recognizer = LicensePlateRecognizer(CONFIGURATION)
    screen_automation = ScreenAutomation()
    window = LicensePlateMainWindow(recognizer, screen_automation)
    window.show()
    sys.exit(app.exec_())
