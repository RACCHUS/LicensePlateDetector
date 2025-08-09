from PyQt5.QtWidgets import QDialog
from PyQt5.QtCore import Qt
from typing import Optional, Tuple

class ClickCaptureDialog(QDialog):
    """Transparent overlay dialog to capture a screen click position."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setWindowState(Qt.WindowState.WindowFullScreen)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        from PyQt5.QtGui import QCursor
        self.setCursor(QCursor(Qt.CursorShape.CrossCursor))
        self.clicked_pos: Optional[Tuple[int, int]] = None
    def mousePressEvent(self, a0):
        # Ensure event is a QMouseEvent (for type checkers and runtime safety)
        from PyQt5.QtGui import QMouseEvent
        event = a0
        if isinstance(event, QMouseEvent) and event.button() == Qt.MouseButton.LeftButton:
            self.clicked_pos = (event.globalX(), event.globalY())
            self.accept()
