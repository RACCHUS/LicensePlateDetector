
from PyQt5.QtWidgets import QMainWindow, QStatusBar, QAction, QFileDialog, QMessageBox
from PyQt5.QtGui import QIcon
from .main_widget import MainWidget
import os


class LicensePlateMainWindow(QMainWindow):
    def __init__(self, recognizer, screen_automation):
        super().__init__()
        self.setWindowTitle('License Plate Recognition System (PyQt)')
        self.setGeometry(100, 100, 600, 400)
        self.main_widget = MainWidget(recognizer, screen_automation)
        self.setCentralWidget(self.main_widget)
        self.setStatusBar(QStatusBar())

        # Dark mode state
        self.dark_mode = True
        self._apply_dark_mode()

        # Menu for toggling dark mode
        menubar = self.menuBar()
        view_menu = menubar.addMenu('View')
        self.toggle_dark_action = QAction('Toggle Dark Mode', self)
        self.toggle_dark_action.setCheckable(True)
        self.toggle_dark_action.setChecked(True)
        self.toggle_dark_action.triggered.connect(self.toggle_dark_mode)
        view_menu.addAction(self.toggle_dark_action)

    def _apply_dark_mode(self):
        qss_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'style_dark.qss')
        try:
            with open(qss_path, 'r') as f:
                self.setStyleSheet(f.read())
        except Exception:
            pass

    def _apply_light_mode(self):
        self.setStyleSheet("")

    def toggle_dark_mode(self):
        self.dark_mode = not self.dark_mode
        if self.dark_mode:
            self._apply_dark_mode()
        else:
            self._apply_light_mode()
        self.toggle_dark_action.setChecked(self.dark_mode)
