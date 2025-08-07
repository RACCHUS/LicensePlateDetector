
from PyQt5.QtWidgets import QDialog, QApplication
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QPainter, QPen, QColor

class RegionSelectorDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Select Scan Region')
        self.selected_region = None
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setWindowState(Qt.WindowFullScreen)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.start_pos = None
        self.end_pos = None
        self.drawing = False
        self.setCursor(Qt.CrossCursor)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.start_pos = event.pos()
            self.end_pos = event.pos()
            self.drawing = True
            self.update()

    def mouseMoveEvent(self, event):
        if self.drawing:
            self.end_pos = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.drawing:
            self.end_pos = event.pos()
            self.drawing = False
            self.update()
            rect = self.get_rect()
            if rect.width() > 10 and rect.height() > 10:
                self.selected_region = (rect.x(), rect.y(), rect.width(), rect.height())
                self.accept()
            else:
                self.selected_region = None
                self.reject()

    def paintEvent(self, event):
        if self.start_pos and self.end_pos:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setPen(QPen(QColor(255, 0, 0, 200), 2, Qt.SolidLine))
            painter.setBrush(QColor(255, 0, 0, 50))
            rect = self.get_rect()
            painter.drawRect(rect)

    def get_rect(self):
        if not self.start_pos or not self.end_pos:
            return QRect()
        x1, y1 = self.start_pos.x(), self.start_pos.y()
        x2, y2 = self.end_pos.x(), self.end_pos.y()
        left, top = min(x1, x2), min(y1, y2)
        width, height = abs(x2 - x1), abs(y2 - y1)
        return QRect(left, top, width, height)
