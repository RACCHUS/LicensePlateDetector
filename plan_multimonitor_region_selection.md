
# Multi-Monitor Scan Region Selection Plan

## Status & Environment
- **PyQt5 version:** 5.15.11 (Qt runtime: 5.15.2)
- **Installation checked:** Yes, confirmed with `pip install PyQt5` and version check using `from PyQt5.QtCore import QT_VERSION_STR; print(QT_VERSION_STR)`
- **Screen picker and region selector integration:** In progress, code updated to support multi-monitor selection and robust Qt attribute handling.


## 1. Screen Selection Dialog
- Created `ScreenPickerDialog` that lists all available screens using `QApplication.screens()`.
- Each entry shows the screen number and its resolution (e.g., "Screen 1: 1920x1080").
- User selects a screen and clicks "OK" (or cancels).

## 2. Update RegionSelectorDialog
- Modified `RegionSelectorDialog` to accept a `QScreen` object and set its geometry to that screen’s geometry.
- Parent is set to `None` for overlay/focus reliability.
- Qt attribute usage made robust for environments with missing enum attributes.

## 3. Integrate in MainWidget
- In `set_scan_region`, before opening the region selector, show the `ScreenPickerDialog`.
- If the user selects a screen, pass the corresponding `QScreen` to `RegionSelectorDialog`.
- If canceled, abort region selection.

## 4. Save Screen Index
- When saving the scan region, also save the screen index (so the region is always relative to the correct screen).
- Update settings structure: `{'scan_region': (x, y, w, h), 'scan_screen': screen_index}`.

## 5. Use Correct Screen for Capture
- When capturing the screen region, use the saved screen index to get the correct screen’s geometry and offset.
- Adjust region coordinates if needed (region should be relative to the selected screen, not global desktop).

## 6. User Feedback

## 7. Testing


**Recent actions:**
- User confirmed the dialog is now frameless and always-on-top, appearing above all windows and without a border.
- Next: Restore translucent (semi-transparent) overlay, then region selection (mouse capture and drawing), testing after each step.
+- User confirmed the dialog is now frameless and always-on-top, appearing above all windows and without a border.
+- User confirmed the dialog is now semi-transparent (translucent overlay works).
+- Region selection (mouse capture and drawing) restored and tested: user can now set the scan region with a translucent overlay and red rectangle.
+- Feature is now working as intended.
+

**Recommended polish/robustness improvements:**
- Add a cancel/close button or ESC key support to abort region selection. **[Done]**
- Show current region coordinates as the user drags. **[Done]**
- Highlight the selected screen in the screen picker dialog. **[Done, dark mode]**
+- Remember last used screen and region as defaults. **[Done]**
+- Handle screen configuration changes (e.g., monitor unplugged) gracefully. **[In progress]**
+- Add accessibility hints or tooltips for usability. **[In progress]**

---

- Implemented and patched screen picker and region selector dialogs for multi-monitor support.
- Hardened code for environments with missing Qt enum attributes.
- Updated `RegionSelectorDialog` to:
	- Use integer window flags for maximum compatibility (frameless, dialog, always-on-top).
	- Set a visible semi-transparent red background for debugging and user feedback.
	- Explicitly move the dialog to the top-left of the selected screen.
- User is now testing if the region selector overlay is visible and interactive on their setup.
- Temporarily replaced the region selector overlay with a normal dialog with a solid background and a label, to confirm the dialog appears on the correct screen.
- User confirmed the blue debug dialog is now visible—dialog creation and screen selection are working.
- User confirmed the dialog is now frameless and always-on-top, appearing above all windows and without a border.
- User confirmed restored translucent (semi-transparent) overlay, then region selection (mouse capture and drawing).
