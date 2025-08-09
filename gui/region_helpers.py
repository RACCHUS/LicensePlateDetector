from PyQt5.QtCore import QPoint
from gui.region_selector_dialog import RegionSelectorDialog
from gui.screen_picker_dialog import ScreenPickerDialog
from .notifier import Notifier
from .settings_manager import load_settings, save_settings
from typing import Any

def show_region_selector(parent, screens, last_region, last_screen_index):
    """Show dialogs to select the scan region on a chosen screen. Returns (scan_region, screen_index) or (None, None) if cancelled."""
    picker = ScreenPickerDialog(screens, parent)
    if 0 <= last_screen_index < len(screens):
        picker.list_widget.setCurrentRow(last_screen_index)
    else:
        picker.list_widget.setCurrentRow(0)
        last_screen_index = 0
    if picker.exec_() != picker.Accepted:
        Notifier.info(parent, 'Scan region selection cancelled or not implemented.')
        return None, None
    screen_index = picker.get_selected_screen_index()
    if screen_index is None or not (0 <= screen_index < len(screens)):
        Notifier.info(parent, 'Scan region selection cancelled or not implemented.')
        return None, None
    selected_screen = screens[int(screen_index)]
    region_dialog = RegionSelectorDialog(selected_screen)
    region_dialog.setGeometry(selected_screen.geometry())
    region_dialog.setWindowFlags(region_dialog.windowFlags() | region_dialog.windowFlags() | region_dialog.windowFlags().__class__.WindowStaysOnTopHint)
    try:
        region_dialog.setToolTip('Drag to select a region. ESC or Cancel to abort. Coordinates shown live.')
    except Exception:
        pass
    if last_region and int(screen_index) == int(last_screen_index):
        try:
            x, y, w, h = last_region
            region_dialog.start_pos = QPoint(x, y)
            region_dialog.end_pos = QPoint(x + w, y + h)
            region_dialog.drawing = False
            region_dialog.update_region_label()
            region_dialog.update()
        except Exception:
            pass
    if region_dialog.exec_() == region_dialog.Accepted and region_dialog.selected_region:
        return region_dialog.selected_region, int(screen_index)
    else:
        Notifier.info(parent, 'Scan region selection cancelled or not implemented.')
        return None, None
