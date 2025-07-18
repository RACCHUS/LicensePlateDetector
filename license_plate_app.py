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
    import pytesseract
except ImportError:
    pytesseract = None
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
        if pytesseract:
            self.ocr_engines['tesseract'] = self.tesseract_ocr
        if easyocr:
            self.ocr_engines['easyocr'] = self.easyocr_ocr
        if PaddleOCR:
            self.ocr_engines['paddleocr'] = self.paddleocr_ocr
        self.easyocr_reader = easyocr.Reader(['en']) if easyocr else None
        self.paddleocr_reader = PaddleOCR(use_angle_cls=True, lang='en') if PaddleOCR else None

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

    def tesseract_ocr(self, image) -> OCRResult:
        if not pytesseract:
            return OCRResult('', 0.0, 'tesseract')
        try:
            text = pytesseract.image_to_string(image, config='--psm 7')
            conf = 0.8  # Tesseract does not always provide confidence
            return OCRResult(text, conf, 'tesseract')
        except Exception:
            return OCRResult('', 0.0, 'tesseract')

    def easyocr_ocr(self, image) -> OCRResult:
        if not self.easyocr_reader:
            return OCRResult('', 0.0, 'easyocr')
        try:
            result = self.easyocr_reader.readtext(np.array(image))
            if result:
                text, conf = result[0][1], float(result[0][2])
                return OCRResult(text, conf, 'easyocr')
            else:
                return OCRResult('', 0.0, 'easyocr')
        except Exception:
            return OCRResult('', 0.0, 'easyocr')

    def paddleocr_ocr(self, image) -> OCRResult:
        if not self.paddleocr_reader:
            return OCRResult('', 0.0, 'paddleocr')
        try:
            result = self.paddleocr_reader.ocr(np.array(image))
            if result and result[0]:
                text, conf = result[0][0][1][0], float(result[0][0][1][1])
                return OCRResult(text, conf, 'paddleocr')
            else:
                return OCRResult('', 0.0, 'paddleocr')
        except Exception:
            return OCRResult('', 0.0, 'paddleocr')

    def clean_license_plate(self, text) -> str:
        text = ''.join(filter(str.isalnum, text.upper()))
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
        processed = self.preprocess_image(image)
        results = []
        for name, engine in self.ocr_engines.items():
            try:
                result = engine(processed)
                results.append(result)
            except Exception:
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
        self.gui_components['status'] = tk.Label(frame, text='Status: Ready')
        self.gui_components['status'].grid(row=1, column=0, columnspan=3)
        self.gui_components['results'] = tk.Text(frame, height=10, width=50)
        self.gui_components['results'].grid(row=2, column=0, columnspan=3)
        self.gui_components['interval_label'] = tk.Label(frame, text='Scan Interval:')
        self.gui_components['interval_label'].grid(row=3, column=0)
        self.gui_components['interval_entry'] = tk.Entry(frame, width=5)
        self.gui_components['interval_entry'].insert(0, str(CONFIGURATION['scan_interval']))
        self.gui_components['interval_entry'].grid(row=3, column=1)
        self.gui_components['interval_unit'] = tk.Label(frame, text='seconds')
        self.gui_components['interval_unit'].grid(row=3, column=2)

    def set_target_field(self):
        # Dummy: set to fixed position
        self.target_field = (450, 300)
        self.log_result(f"Target field set at {self.target_field}")

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
            # Dummy region for screen capture
            region = (100, 100, 200, 60)
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