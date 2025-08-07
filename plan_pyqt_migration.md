# License Plate Detector - PyQt Migration & Modernization Plan

## Purpose
This plan outlines the steps to migrate the License Plate Detector application from Tkinter to PyQt (or PySide), modernize the UI, and ensure a robust, maintainable, and user-friendly experience.

---

## 1. Migration Goals
- Replace Tkinter GUI with a PyQt-based interface
- Preserve and reuse backend logic (OCR, automation, validation)
- Improve UI/UX with modern widgets, layouts, and styling
- Prepare for future features (state reporting, logging, settings, etc.)

---

## 2. Migration Steps

### Phase 1: Preparation
- [x] Review current GUI features and workflows
- [x] List all Tkinter-dependent code and UI logic
- [x] Identify reusable backend modules (OCR, automation, models, utils)
- [x] Add PyQt5 to requirements.txt

#### Tkinter-dependent code:
- All GUI logic is in `license_plate_app.py` (class `LicensePlateApp` and its methods)
- GUI setup, event handling, and widgets (buttons, labels, text fields, dialogs) are all Tkinter-based


#### Reusable backend modules:
- OCR logic: `ocr/` directory (all engine files)
- Recognizer logic: `recognizer/` package (main recognizer, config, automation)
- Models: `models.py`
- Utilities: `utils/` directory (image processing, validation, state filters)
- Automation: `automation/` directory



### Phase 2: PyQt Project Setup (Complete)
- [x] Modular structure: `qt_app.py` (entry), `main_window.py` (window), `main_widget.py` (UI/logic), `region_selector_dialog.py`, `notifier.py`, `settings_manager.py`, `logger.py`
- [x] All main UI buttons (Start, Stop, Set Target Field, Set Scan Region) have event handlers and log actions
- [x] Recognition loop is integrated and logs results
- [x] Interactive region selection dialog for scan region
- [x] Settings persistence for scan region
- [x] Centralized logging to file and UI
- [x] User feedback and error dialogs via Notifier utility

---

### Phase 3: Feature Parity Migration (Complete)
- [x] All Tkinter GUI features ported to PyQt:
    - Start/Stop recognition
    - Set target field (with overlay click capture)
    - Set scan region (with interactive selection)
    - Display status and results
    - Interval configuration
- [x] PyQt signals/slots connected to backend logic
- [x] Automation and OCR features work with the new UI (auto-insert, manual confirmation on low confidence)



- [x] Improve layout and styling (QSS, icons, responsive design)
- [x] Add dark mode (default) with toggleable light/dark mode in the UI
- [x] Add state reporting to results display
- [x] Add error dialogs, confirmations, and user feedback
- [x] Prepare for future features (logging, settings, etc.)

### Phase 5: Testing & Documentation
- [x] Test all features for parity and stability
- [x] Update README and user documentation
- [x] Remove obsolete Tkinter code after successful migration

---

## 3. Risks & Considerations
- PyQt has a steeper learning curve than Tkinter
- Users must install PyQt5/PySide2 (not in stdlib)
- Some platform-specific issues may arise (test on Windows, macOS, Linux)
- Refactoring may introduce temporary instability
- **Automation Limitation:** Automatic text insertion via simulated mouse/keyboard input (PyAutoGUI) will always interfere with user activity. True non-interference is only possible if the target application supports direct API or plugin integration.

---

## 4. References
- [PyQt5 Documentation](https://doc.qt.io/qtforpython/)
- [PySide2 Documentation](https://doc.qt.io/qtforpython/)
- [Qt Designer](https://build-system.fman.io/qt-designer-download) (for drag-and-drop UI design)

---

## 5. Next Steps
- [x] Approve this plan
- [x] Complete all migration and cleanup steps
- [ ] Final review and polish as needed

---

*This plan is a living document. Update as migration progresses.*
