from PyQt5.QtWidgets import QDialog, QVBoxLayout, QListWidget, QPushButton, QHBoxLayout, QLabel
from PyQt5.QtCore import Qt

class ScreenPickerDialog(QDialog):
    def _highlight_selected(self):
        from PyQt5.QtGui import QColor, QBrush
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if item is not None:
                if i == self.list_widget.currentRow():
                    item.setBackground(QBrush(QColor(0, 0, 0)))  # black background
                    item.setForeground(QBrush(QColor(255, 255, 255)))  # white text
                else:
                    item.setBackground(QBrush(QColor(40, 40, 40)))  # dark gray background
                    item.setForeground(QBrush(QColor(255, 255, 255)))  # white text
    def __init__(self, screens, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Select Screen for Region Selection')
        self.selected_index = None
        self.screens = screens
        self._init_ui()
        try:
            self.setToolTip('Select which monitor to use for region selection. Use arrow keys or mouse, then press OK.')
            self.list_widget.setToolTip('List of available screens. Highlighted row is current selection.')
        except Exception:
            pass

    def _init_ui(self):
        vbox = QVBoxLayout()
        label = QLabel('Select the screen to use for region selection:')
        vbox.addWidget(label)
        self.list_widget = QListWidget()
        for idx, screen in enumerate(self.screens):
            geom = screen.geometry()
            desc = f"Screen {idx+1}: {geom.width()}x{geom.height()} at ({geom.x()},{geom.y()})"
            self.list_widget.addItem(desc)
        vbox.addWidget(self.list_widget)
        self.list_widget.currentRowChanged.connect(lambda _: self._highlight_selected())
        self._highlight_selected()
        hbox = QHBoxLayout()
        ok_btn = QPushButton('OK')
        cancel_btn = QPushButton('Cancel')
        ok_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        hbox.addWidget(ok_btn)
        hbox.addWidget(cancel_btn)
        vbox.addLayout(hbox)
        self.setLayout(vbox)

    def accept(self):
        row = self.list_widget.currentRow()
        if row >= 0:
            self.selected_index = row
            super().accept()
        else:
            # No selection, do nothing
            pass

    def get_selected_screen_index(self):
        return self.selected_index
