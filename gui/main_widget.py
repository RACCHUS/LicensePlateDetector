from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QTextEdit, QLineEdit, QDialog
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

import threading
import time
from .region_selector_dialog import RegionSelectorDialog
from .notifier import Notifier
from .settings_manager import load_settings, save_settings
from .logger import log_info, log_error
from utils.state_filters import is_state_name_or_abbreviation

class MainWidget(QWidget):
    def __init__(self, recognizer, screen_automation):
        super().__init__()
        self.recognizer = recognizer
        self.screen_automation = screen_automation
        self.recognition_running = False
        self.recognition_thread = None
        settings = load_settings()
        self.scan_region = tuple(settings.get('scan_region', (100, 100, 200, 60)))
        self.target_field = None
        self._init_ui()

    def _init_ui(self):
        vbox = QVBoxLayout()
        hbox = QHBoxLayout()
        self.start_btn = QPushButton(QIcon.fromTheme('media-playback-start'), 'Start Recognition')
        self.start_btn.setToolTip('Begin automatic license plate recognition')
        self.stop_btn = QPushButton(QIcon.fromTheme('media-playback-stop'), 'Stop')
        self.stop_btn.setToolTip('Stop recognition')
        self.set_field_btn = QPushButton(QIcon.fromTheme('edit-select'), 'Set Target Field')
        self.set_field_btn.setToolTip('Click to select the field where results will be inserted')
        self.set_region_btn = QPushButton(QIcon.fromTheme('view-grid'), 'Set Scan Region')
        self.set_region_btn.setToolTip('Select the screen region to scan for license plates')
        hbox.addWidget(self.start_btn)
        hbox.addWidget(self.stop_btn)
        hbox.addWidget(self.set_field_btn)
        hbox.addWidget(self.set_region_btn)
        self.status_label = QLabel('Status: Ready')
        self.status_label.setToolTip('Shows the current status of the recognition system')
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setToolTip('Recognition results and logs')
        # Interval configuration
        interval_hbox = QHBoxLayout()
        self.interval_label = QLabel('Scan Interval:')
        self.interval_label.setToolTip('How often to scan for license plates (in seconds)')
        self.interval_entry = QLineEdit()
        self.interval_entry.setFixedWidth(50)
        self.interval_entry.setText('2.0')
        self.interval_entry.setToolTip('Enter the scan interval in seconds')
        self.interval_unit = QLabel('seconds')
        interval_hbox.addWidget(self.interval_label)
        interval_hbox.addWidget(self.interval_entry)
        interval_hbox.addWidget(self.interval_unit)
        vbox.addLayout(hbox)
        vbox.addWidget(self.status_label)
        vbox.addWidget(self.results_text)
        vbox.addLayout(interval_hbox)
        self.setLayout(vbox)
        # QSS styling support
        try:
            with open('style.qss', 'r') as f:
                self.setStyleSheet(f.read())
        except Exception:
            pass  # No custom style applied if file not found
        self.start_btn.clicked.connect(self.start_recognition)
        self.stop_btn.clicked.connect(self.stop_recognition)
        self.set_field_btn.clicked.connect(self.set_target_field)
        self.set_region_btn.clicked.connect(self.set_scan_region)

    def set_target_field(self):
        # Show a transparent overlay and capture the next mouse click position
        class ClickCaptureDialog(QDialog):
            def __init__(self, parent=None):
                super().__init__(parent)
                self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint | Qt.Dialog)
                self.setWindowState(Qt.WindowFullScreen)
                self.setAttribute(Qt.WA_TranslucentBackground)
                self.setCursor(Qt.CrossCursor)
                self.clicked_pos = None
            def mousePressEvent(self, event):
                if event.button() == Qt.LeftButton:
                    self.clicked_pos = (event.globalX(), event.globalY())
                    self.accept()
        dialog = ClickCaptureDialog(self)
        Notifier.info(self, 'Click anywhere on the screen to set the target field position.')
        if dialog.exec_() == dialog.Accepted and dialog.clicked_pos:
            self.target_field = dialog.clicked_pos
            self.log_result(f'Target field set at {self.target_field}')
            Notifier.info(self, f'Target field set at {self.target_field}')
        else:
            self.log_result('Target field selection cancelled.')

    def set_scan_region(self):
        dialog = RegionSelectorDialog(self)
        if dialog.exec_() == dialog.Accepted and dialog.selected_region:
            self.scan_region = dialog.selected_region
            save_settings({'scan_region': self.scan_region})
            self.log_result(f'Scan region set to {self.scan_region}')
            Notifier.info(self, f'Scan region set to {self.scan_region}')
        else:
            self.log_result('Scan region selection cancelled or not implemented.')

    def start_recognition(self):
        if not self.recognition_running:
            self.recognition_running = True
            self.status_label.setText('Status: Running')
            self.log_result('Recognition started.')
            self.recognition_thread = threading.Thread(target=self.recognition_loop, daemon=True)
            self.recognition_thread.start()

    def recognition_loop(self):
        while self.recognition_running:
            try:
                if self.screen_automation:
                    img = self.screen_automation.capture_screen_region(self.scan_region)
                    text, conf, alert = self.recognizer.recognize_license_plate(img)
                    now = time.strftime('%H:%M:%S')
                    detected_state = None
                    if text and is_state_name_or_abbreviation(text):
                        detected_state = text
                    if text:
                        state_info = f" | State: {detected_state}" if detected_state else ""
                        self.log_result(f"{now} - Detected: {text} (Conf: {conf:.2f}){state_info}")
                        # If confident and target field set, auto-insert
                        if not alert and self.target_field:
                            self.screen_automation.click_and_type(text, self.target_field)
                            self.log_result(f"{now} - Auto-inserted: {text}")
                        elif alert:
                            self.log_result(f"{now} - Manual confirmation needed")
                            Notifier.info(self, f"Manual confirmation needed for: {text}")
                    else:
                        self.log_result(f"{now} - No plate detected.")
                else:
                    self.show_error("ScreenAutomation not available.")
            except Exception as e:
                self.show_error(f"Recognition error: {e}")
            try:
                interval = float(self.interval_entry.text())
                if interval < 0.1:
                    interval = 0.1
            except Exception:
                interval = 2.0
            time.sleep(interval)


    def show_error(self, message):
        self.log_result(f"ERROR: {message}")
        log_error(message)
        Notifier.error(self, message)

    def stop_recognition(self):
        if self.recognition_running:
            self.recognition_running = False
            self.status_label.setText('Status: Stopped')
            self.log_result('Recognition stopped.')

    def log_result(self, message):
        self.results_text.append(message)
        log_info(message)
