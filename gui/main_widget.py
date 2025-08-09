from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QTextEdit, QLineEdit
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from typing import Optional, Tuple
from .dialogs import ClickCaptureDialog
from .region_helpers import show_region_selector

import threading
import time
from .region_selector_dialog import RegionSelectorDialog
from .screen_picker_dialog import ScreenPickerDialog
from .notifier import Notifier
from .settings_manager import load_settings, save_settings
from .logger import log_info, log_error
from utils.state_filters import is_state_name_or_abbreviation

class MainWidget(QWidget):
    def __init__(self, recognizer, screen_automation):
        """Initialize the main widget and UI."""
        super().__init__()
        self.recognizer = recognizer
        self.screen_automation = screen_automation
        settings = load_settings()
        self.scan_region: Tuple[int, int, int, int] = tuple(settings.get('scan_region', (100, 100, 200, 60)))
        self.target_field: Optional[Tuple[int, int]] = None
        self.input_mode = settings.get('input_mode', 'browser_extension')
        self._init_ui()
        self._setup_shortcuts()
        from .recognition_controller import RecognitionController
        self.recognition_controller = RecognitionController(self)
        self.recognition_controller.result_signal.connect(self.log_result)
        self.recognition_controller.error_signal.connect(self.show_error)
        self.recognition_controller.status_signal.connect(self.show_status)
        self.recognition_running = False
        # Set initial state of Set Target Field button based on input mode
        self._update_set_field_btn_state()

    def toggle_recognition_hotkey(self):
        """Toggle recognition on hotkey press."""
        # Use controller state for toggling
        if self.status_label.text() == 'Status: Running':
            self.stop_recognition()
            self.log_result('Recognition stopped by hotkey (Ctrl+Shift+L).')
        else:
            self.start_recognition()
            self.log_result('Recognition started by hotkey (Ctrl+Shift+L).')

    def _init_ui(self):
        """Set up the main UI layout and widgets."""
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

        # Input mode selector
        from PyQt5.QtWidgets import QComboBox
        self.input_mode_combo = QComboBox()
        self.input_mode_combo.addItem('Browser Extension', 'browser_extension')
        self.input_mode_combo.addItem('Keystroke Automation', 'keystroke')
        self.input_mode_combo.setCurrentIndex(0 if self.input_mode == 'browser_extension' else 1)
        self.input_mode_combo.setToolTip('Choose how to input recognized plates (browser extension is recommended)')
        self.input_mode_combo.currentIndexChanged.connect(self._on_input_mode_changed)
        vbox.addWidget(QLabel('Input Mode:'))
        vbox.addWidget(self.input_mode_combo)

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
        self._connect_signals()

    def _on_input_mode_changed(self, idx):
        mode = self.input_mode_combo.currentData()
        self.input_mode = mode
        save_settings({'input_mode': mode})
        self._update_set_field_btn_state()
        self.log_result(f"Input mode changed to: {self.input_mode_combo.currentText()}")

    def _update_set_field_btn_state(self):
        # Disable Set Target Field button in extension mode, enable in keystroke mode
        if self.input_mode == 'browser_extension':
            self.set_field_btn.setEnabled(False)
            self.set_field_btn.setToolTip('Field selection is handled by the browser extension in this mode.')
            # Visually indicate disabled state
            self.set_field_btn.setStyleSheet('background-color: #e0e0e0; color: #888; border: 1px solid #bbb;')
        else:
            self.set_field_btn.setEnabled(True)
            self.set_field_btn.setToolTip('Click to select the field where results will be inserted')
            self.set_field_btn.setStyleSheet('')  # Reset to default
    def _setup_shortcuts(self):
        """Set up global hotkeys for the widget."""
        from PyQt5.QtWidgets import QShortcut
        from PyQt5.QtGui import QKeySequence
        self.toggle_hotkey = QShortcut(QKeySequence('Ctrl+Shift+L'), self)
        self.toggle_hotkey.setAutoRepeat(False)
        self.toggle_hotkey.activated.connect(self.toggle_recognition_hotkey)

    def _connect_signals(self):
        """Connect button signals to their slots."""
        self.start_btn.clicked.connect(self.start_recognition)
        self.stop_btn.clicked.connect(self.stop_recognition)
        self.set_field_btn.clicked.connect(self.set_target_field)
        self.set_region_btn.clicked.connect(self.set_scan_region)

    def set_target_field(self):
        """Show overlay and capture the next mouse click position for the target field."""
        dialog = ClickCaptureDialog(self)
        Notifier.info(self, 'Click anywhere on the screen to set the target field position.')
        if dialog.exec_() == dialog.Accepted and dialog.clicked_pos:
            self.target_field = dialog.clicked_pos
            self.log_result(f'Target field set at {self.target_field}')
            Notifier.info(self, f'Target field set at {self.target_field}')
        else:
            self.log_result('Target field selection cancelled.')

    def set_scan_region(self):
        """Show dialogs to select the scan region on a chosen screen."""
        settings = load_settings()
        last_screen_index = settings.get('scan_screen', 0)
        last_region = settings.get('scan_region', None)
        from PyQt5.QtWidgets import QApplication
        screens = QApplication.screens()
        region, screen_index = show_region_selector(self, screens, last_region, last_screen_index)
        if region is not None and screen_index is not None:
            self.scan_region = region
            save_settings({'scan_region': self.scan_region, 'scan_screen': int(screen_index)})
            self.log_result(f'Scan region set to {self.scan_region} on screen {int(screen_index)+1}')
            Notifier.info(self, f'Scan region set to {self.scan_region} on screen {int(screen_index)+1}')
        else:
            self.log_result('Scan region selection cancelled or not implemented.')

    def start_recognition(self):
        """Start the recognition thread (via RecognitionController)."""
        if not self.recognition_running:
            self.recognition_running = True
            self.status_label.setText('Status: Running')
            self.log_result('Recognition started.')
            self.recognition_controller.start()

    # recognition_loop is now handled by RecognitionController


    def show_error(self, message: str):
        """Show an error message in the log and as a dialog."""
        self.log_result(f"ERROR: {message}")
        log_error(message)
        Notifier.error(self, message)

    def stop_recognition(self):
        """Stop the recognition thread (via RecognitionController)."""
        if self.recognition_running:
            self.recognition_running = False
            self.status_label.setText('Status: Stopped')
            self.log_result('Recognition stopped.')
            self.recognition_controller.stop()
    def show_status(self, message: str):
        Notifier.info(self, message)

    def log_result(self, message: str):
        """Append a message to the results log."""
        self.results_text.append(message)
        log_info(message)
