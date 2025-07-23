import threading
import time
from dataclasses import dataclass
from typing import Dict, Tuple, Optional, List
import tkinter as tk
from tkinter import messagebox
import numpy as np
from PIL import Image, ImageTk

# OCR imports (to be handled with error catching)
try:
    import keras_ocr
except ImportError:
    keras_ocr = None
try:
    from doctr.models import ocr_predictor
except ImportError:
    ocr_predictor = None
try:
    import easyocr
except ImportError:
    easyocr = None
try:
    from paddleocr import PaddleOCR
except ImportError:
    PaddleOCR = None

import cv2
import pyautogui
# Import state filter
from state_filters import is_state_name_or_abbreviation
from easyocr_engine import easyocr_ocr, OCRResult
from paddleocr_engine import paddleocr_ocr
from doctr_engine import doctr_ocr
from kerasocr_engine import kerasocr_ocr

# Configuration
CONFIGURATION = {
    'confidence_threshold': 0.6,
    'agreement_threshold': 0.75,
    'scan_interval': 2.0,
    'max_plate_length': 10,
    'min_plate_length': 3,
    'ocr_timeout': 5.0,
    'retry_attempts': 3,
    'image_resize_height': 50
}

@dataclass
class OCRResult:
    text: str
    confidence: float
    source: str

class LicensePlateRecognizer:
    def __init__(self, config: Dict):
        self.ocr_engines = {}
        self.confidence_threshold = config['confidence_threshold']
        self.agreement_threshold = config['agreement_threshold']
        if keras_ocr:
            self.kerasocr_pipeline = keras_ocr.pipeline.Pipeline()
            self.ocr_engines['keras_ocr'] = lambda img: kerasocr_ocr(img, self.kerasocr_pipeline, self.clean_license_plate, getattr(self, 'log_result', None))
        else:
            self.kerasocr_pipeline = None
        if ocr_predictor:
            self.doctr_predictor = ocr_predictor(pretrained=True)
            self.ocr_engines['doctr'] = lambda img: doctr_ocr(img, self.doctr_predictor, self.clean_license_plate, getattr(self, 'log_result', None))
        else:
            self.doctr_predictor = None
        if easyocr:
            self.easyocr_reader = easyocr.Reader(['en'])
            self.ocr_engines['easyocr'] = lambda img: easyocr_ocr(img, self.easyocr_reader, self.clean_license_plate, getattr(self, 'log_result', None))
        else:
            self.easyocr_reader = None
        if PaddleOCR:
            self.paddleocr_reader = PaddleOCR(use_textline_orientation=True, lang='en')
            self.ocr_engines['paddleocr'] = lambda img: paddleocr_ocr(img, self.paddleocr_reader, self.clean_license_plate, getattr(self, 'log_result', None))
        else:
            self.paddleocr_reader = None

    def preprocess_image(self, image):
        # Convert to grayscale
        img = np.array(image)
        if len(img.shape) == 3:
            img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        # Gaussian blur
        img = cv2.GaussianBlur(img, (5, 5), 0)
        # OTSU threshold
        _, img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        # Morphological closing
        kernel = np.ones((3, 3), np.uint8)
        img = cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel)
        # Resize if height < 50
        h = img.shape[0]
        if h < CONFIGURATION['image_resize_height']:
            scale = CONFIGURATION['image_resize_height'] / h
            img = cv2.resize(img, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
        return Image.fromarray(img)

    def clean_license_plate(self, text) -> str:
        text = ''.join(filter(str.isalnum, text.upper()))
        # Filter out state names/abbreviations
        if is_state_name_or_abbreviation(text):
            return ''
        # Only accept likely license plate numbers (alphanumeric, length 3-10)
        if CONFIGURATION['min_plate_length'] <= len(text) <= CONFIGURATION['max_plate_length']:
            return text
        return ''

    def get_consensus_result(self, results: List[OCRResult]):
        filtered = [r for r in results if r.confidence > 0.1]
        groups = {}
        for r in filtered:
            clean = self.clean_license_plate(r.text)
            if clean:
                groups.setdefault(clean, []).append(r)
        total = len(filtered)
        for text, group in groups.items():
            agreement = len(group) / max(1, total)
            avg_conf = sum(r.confidence for r in group) / len(group)
            if agreement >= self.agreement_threshold and avg_conf >= self.confidence_threshold:
                return text, avg_conf, False
        # No strong consensus
        if groups:
            # Return most common
            text, group = max(groups.items(), key=lambda x: len(x[1]))
            avg_conf = sum(r.confidence for r in group) / len(group)
            return text, avg_conf, True
        return '', 0.0, True

    def recognize_license_plate(self, image):
        # Prepare different image formats for each engine
        processed = self.preprocess_image(image)
        np_image = np.array(image)
        results = []
        for name, engine in self.ocr_engines.items():
            try:
                if name == 'keras_ocr':
                    # keras-ocr expects a color image (numpy array, RGB)
                    result = engine(image)
                elif name == 'paddleocr':
                    # paddleocr expects a numpy array (BGR)
                    bgr_img = cv2.cvtColor(np_image, cv2.COLOR_RGB2BGR) if len(np_image.shape) == 3 else np_image
                    result = engine(bgr_img)
                elif name == 'doctr':
                    # doctr expects a numpy array (RGB)
                    result = engine(np_image)
                elif name == 'easyocr':
                    # easyocr works well with preprocessed PIL image
                    result = engine(processed)
                else:
                    result = engine(processed)
                debug_raw = f"OCR ({name}): '{result.text}' (conf: {result.confidence})"
                print(debug_raw)
                if hasattr(self, 'log_result'):
                    self.log_result(debug_raw)
                cleaned = self.clean_license_plate(result.text)
                debug_cleaned = f"Cleaned ({name}): '{cleaned}'"
                print(debug_cleaned)
                if hasattr(self, 'log_result'):
                    self.log_result(debug_cleaned)
                results.append(result)
            except Exception as e:
                error_msg = f"OCR ({name}) error: {e}"
                print(error_msg)
                if hasattr(self, 'log_result'):
                    self.log_result(error_msg)
                results.append(OCRResult('', 0.0, name))
        return self.get_consensus_result(results)

class ScreenAutomation:
    def __init__(self):
        self.target_field = None
        self.field_template = None

    def capture_screen_region(self, region):
        # region: (left, top, width, height)
        img = pyautogui.screenshot(region=region)
        return img

    def find_text_field(self, template):
        # Not implemented: would use template matching
        return (450, 300)  # Dummy value

    def click_and_type(self, text, position):
        pyautogui.click(position[0], position[1])
        pyautogui.typewrite(text)

class LicensePlateApp:
    def __init__(self, root):
        self.recognizer = LicensePlateRecognizer(CONFIGURATION)
        self.screen_automation = ScreenAutomation()
        self.running = False
        self.gui_components = {}
        self.setup_gui(root)
        self.recognition_thread = None
        self.target_field = (450, 300)

    def setup_gui(self, root):
        root.title('License Plate Recognition System')
        frame = tk.Frame(root)
        frame.pack(padx=10, pady=10)
        self.gui_components['start_btn'] = tk.Button(frame, text='Start Recognition', command=self.start_recognition)
        self.gui_components['start_btn'].grid(row=0, column=0)
        self.gui_components['stop_btn'] = tk.Button(frame, text='Stop', command=self.stop_recognition)
        self.gui_components['stop_btn'].grid(row=0, column=1)
        self.gui_components['set_field_btn'] = tk.Button(frame, text='Set Target Field', command=self.set_target_field)
        self.gui_components['set_field_btn'].grid(row=0, column=2)
        self.gui_components['set_region_btn'] = tk.Button(frame, text='Set Scan Region', command=self.set_scan_region)
        self.gui_components['set_region_btn'].grid(row=0, column=3)
        self.gui_components['status'] = tk.Label(frame, text='Status: Ready')
        self.gui_components['status'].grid(row=1, column=0, columnspan=4)
        self.gui_components['results'] = tk.Text(frame, height=10, width=50)
        self.gui_components['results'].grid(row=2, column=0, columnspan=4)
        self.gui_components['interval_label'] = tk.Label(frame, text='Scan Interval:')
        self.gui_components['interval_label'].grid(row=3, column=0)
        self.gui_components['interval_entry'] = tk.Entry(frame, width=5)
        self.gui_components['interval_entry'].insert(0, str(CONFIGURATION['scan_interval']))
        self.gui_components['interval_entry'].grid(row=3, column=1)
        self.gui_components['interval_unit'] = tk.Label(frame, text='seconds')
        self.gui_components['interval_unit'].grid(row=3, column=2)

    def set_target_field(self):
        def capture_click():
            try:
                # Minimize the window
                self.gui_components['start_btn'].master.master.iconify()
                messagebox.showinfo('Set Target Field', 'Move your mouse to the target field and left-click to set its position.')
                # Wait for mouse click
                import pyautogui
                pos = None
                while pos is None:
                    if pyautogui.mouseDown(button='left'):
                        pos = pyautogui.position()
                        break
                # Restore the window
                self.gui_components['start_btn'].master.master.deiconify()
                self.target_field = (pos.x, pos.y)
                self.log_result(f"Target field set at {self.target_field}")
            except pyautogui.FailSafeException:
                self.gui_components['start_btn'].master.master.deiconify()
                messagebox.showwarning('Operation Cancelled', 'Mouse moved to a screen corner. Target field selection cancelled for your safety.')
                self.log_result('Target field selection cancelled due to PyAutoGUI fail-safe.')
        threading.Thread(target=capture_click, daemon=True).start()

    def set_scan_region(self):
        def region_selector():
            import tkinter as tk
            import threading
            # Minimize main window
            self.gui_components['start_btn'].master.master.iconify()
            # Create transparent overlay
            overlay = tk.Tk()
            overlay.attributes('-fullscreen', True)
            overlay.attributes('-alpha', 0.3)
            overlay.attributes('-topmost', True)
            overlay.config(cursor="crosshair")
            canvas = tk.Canvas(overlay, bg='black')
            canvas.pack(fill=tk.BOTH, expand=True)
            start = [0, 0]
            rect = [None]
            region = [None]
            def on_mouse_down(event):
                start[0], start[1] = event.x, event.y
                rect[0] = canvas.create_rectangle(event.x, event.y, event.x, event.y, outline='red', width=2)
            def on_mouse_move(event):
                if rect[0] is not None:
                    canvas.coords(rect[0], start[0], start[1], event.x, event.y)
            def on_mouse_up(event):
                x0, y0 = start[0], start[1]
                x1, y1 = event.x, event.y
                left, top = min(x0, x1), min(y0, y1)
                width, height = abs(x1 - x0), abs(y1 - y0)
                region[0] = (left, top, width, height)
                overlay.destroy()
                self.gui_components['start_btn'].master.master.deiconify()
                self.scan_region = region[0]
                self.log_result(f"Scan region set to: {self.scan_region}")
            canvas.bind('<ButtonPress-1>', on_mouse_down)
            canvas.bind('<B1-Motion>', on_mouse_move)
            canvas.bind('<ButtonRelease-1>', on_mouse_up)
            overlay.mainloop()
        threading.Thread(target=region_selector, daemon=True).start()

    def start_recognition(self):
        if not self.running:
            self.running = True
            self.gui_components['status'].config(text='Status: Running')
            self.recognition_thread = threading.Thread(target=self.recognition_loop, daemon=True)
            self.recognition_thread.start()

    def stop_recognition(self):
        self.running = False
        self.gui_components['status'].config(text='Status: Stopped')

    def recognition_loop(self):
        while self.running:
            # Use user-selected region if available, else default
            region = getattr(self, 'scan_region', (100, 100, 200, 60))
            img = self.screen_automation.capture_screen_region(region)
            text, conf, alert = self.recognizer.recognize_license_plate(img)
            now = time.strftime('%H:%M:%S')
            if text:
                self.log_result(f"{now} - Detected: {text} (Conf: {conf:.2f})")
                if not alert:
                    self.screen_automation.click_and_type(text, self.target_field)
                    self.log_result(f"{now} - Auto-inserted: {text}")
                else:
                    self.log_result(f"{now} - Manual confirmation needed")
                    self.show_alert(text, conf)
            time.sleep(float(self.gui_components['interval_entry'].get()))

    def show_alert(self, text, confidence):
        result = messagebox.askyesno('Uncertain Recognition', f'Detected plate: {text}\nConfidence: {confidence:.2f}\n\nInsert this text?')
        if result:
            self.screen_automation.click_and_type(text, self.target_field)
            self.log_result(f"{time.strftime('%H:%M:%S')} - User accepted: {text}")
        else:
            self.log_result(f"{time.strftime('%H:%M:%S')} - User rejected: {text}")

    def log_result(self, message):
        self.gui_components['results'].insert(tk.END, message + '\n')
        self.gui_components['results'].see(tk.END)

if __name__ == '__main__':
    root = tk.Tk()
    app = LicensePlateApp(root)
    root.mainloop()