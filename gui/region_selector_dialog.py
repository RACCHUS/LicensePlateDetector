
from PyQt5.QtWidgets import QDialog, QApplication
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QPainter, QPen, QColor, QCursor

from PyQt5.QtWidgets import QDialog, QLabel, QVBoxLayout
class RegionSelectorDialog(QDialog):
    def __init__(self, screen=None):
        super().__init__(None)
        self.setWindowTitle('DEBUG: Region Selector Test Dialog')
        self.selected_region = None
        # Frameless and always-on-top
        flags = 0x00000800 | 0x00000002 | 0x00040000  # Frameless, Dialog, AlwaysOnTop
        from PyQt5.QtCore import Qt
        self.setWindowFlags(Qt.WindowFlags(flags))
        # Set translucent background attribute if available
        try:
            self.setAttribute(getattr(Qt, 'WA_TranslucentBackground', 0x00000080))
        except Exception:
            pass
        self.setStyleSheet('background-color: rgba(68, 170, 255, 120);')
        from PyQt5.QtWidgets import QPushButton, QHBoxLayout
        layout = QVBoxLayout()
        self.info_label = QLabel('Drag to select a region. Press ESC or Cancel to abort.')
        layout.addWidget(self.info_label)
        # Add cancel button
        btn_layout = QHBoxLayout()
        cancel_btn = QPushButton('Cancel')
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addStretch(1)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
        self.setLayout(layout)
        if screen is not None:
            geo = screen.geometry()
            self.setGeometry(geo.x(), geo.y(), 400, 200)

    def update_region_label(self):
        if getattr(self, 'start_pos', None) is not None and getattr(self, 'end_pos', None) is not None:
            x1, y1 = self.start_pos.x(), self.start_pos.y()
            x2, y2 = self.end_pos.x(), self.end_pos.y()
            left, top = min(x1, x2), min(y1, y2)
            width, height = abs(x2 - x1), abs(y2 - y1)
            self.info_label.setText(f'Drag to select a region. Press ESC or Cancel to abort.\nRegion: ({left}, {top}, {width}, {height})')
        else:
            self.info_label.setText('Drag to select a region. Press ESC or Cancel to abort.')

    def keyPressEvent(self, a0):
        if a0 is not None and hasattr(a0, 'key'):
            if a0.key() == 16777216:  # Qt.Key_Escape
                self.reject()
            else:
                super().keyPressEvent(a0)
        else:
            super().keyPressEvent(a0)


    def mousePressEvent(self, a0):
        if a0 is not None and hasattr(a0, 'button') and hasattr(a0, 'pos'):
            if a0.button() == 1:  # Qt.LeftButton
                self.start_pos = a0.pos()
                self.end_pos = a0.pos()
                self.drawing = True
                self.update_region_label()
                self.update()

    def mouseMoveEvent(self, a0):
        if self.drawing and a0 is not None and hasattr(a0, 'pos'):
            self.end_pos = a0.pos()
            self.update_region_label()
            self.update()

    def mouseReleaseEvent(self, a0):
        if a0 is not None and hasattr(a0, 'button') and hasattr(a0, 'pos'):
            if a0.button() == 1 and self.drawing:  # Qt.LeftButton
                self.end_pos = a0.pos()
                self.drawing = False
                self.update_region_label()
                self.update()
                rect = self.get_rect()
                if rect.width() > 10 and rect.height() > 10:
                    self.selected_region = (rect.x(), rect.y(), rect.width(), rect.height())
                    self.accept()
                else:
                    self.selected_region = None
                    self.reject()

    def paintEvent(self, a0):
        if getattr(self, 'start_pos', None) is not None and getattr(self, 'end_pos', None) is not None:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            # Qt.SolidLine is 1 in PyQt5, use int for compatibility
            painter.setPen(QPen(QColor(255, 0, 0, 200), 2, 1))
            painter.setBrush(QColor(255, 0, 0, 50))
            rect = self.get_rect()
            painter.drawRect(rect)

    def get_rect(self):
        if getattr(self, 'start_pos', None) is None or getattr(self, 'end_pos', None) is None:
            return QRect()
        x1, y1 = self.start_pos.x(), self.start_pos.y()
        x2, y2 = self.end_pos.x(), self.end_pos.y()
        left, top = min(x1, x2), min(y1, y2)
        width, height = abs(x2 - x1), abs(y2 - y1)
        return QRect(left, top, width, height)

# Remove all event handlers and paintEvent below (if present)

    # All event handlers and paintEvent are commented out for debug dialog visibility test.
