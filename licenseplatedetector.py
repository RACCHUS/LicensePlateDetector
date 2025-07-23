import cv2
import numpy as np
import pytesseract
import pyautogui
import time
from PIL import Image
import tkinter as tk
from tkinter import messagebox, filedialog
import threading
from dataclasses import dataclass
from typing import List, Tuple, Optional
import re

@dataclass
class OCRResult:
    text: str
    confidence: float
    source: str

class LicensePlateRecognizer:
    def __init__(self):
        self.ocr_engines = {
            'tesseract': self.tesseract_ocr,
            'easyocr': self.easyocr_ocr,
            'paddleocr': self.paddleocr_ocr
        }
        self.confidence_threshold = 0.6
        self.agreement_threshold = 0.75
        
    def preprocess_image(self, image):
        """Preprocess image for better OCR results"""
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply gaussian blur
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Apply threshold
        _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Morphological operations to clean up
        kernel = np.ones((3, 3), np.uint8)
        cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        
        # Resize for better OCR
        height, width = cleaned.shape
        if height < 50:
            scale_factor = 50 / height
            new_width = int(width * scale_factor)
            cleaned = cv2.resize(cleaned, (new_width, 50), interpolation=cv2.INTER_CUBIC)
        
        return cleaned

    def tesseract_ocr(self, image) -> OCRResult:
        """Use Tesseract OCR for license plate recognition"""
        try:
            # Configure Tesseract for license plates
            custom_config = r'--oem 3 --psm 8 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
            
            # Get OCR result with confidence
            data = pytesseract.image_to_data(image, config=custom_config, output_type=pytesseract.Output.DICT)
            
            # Extract text and calculate average confidence
            text_parts = []
            confidences = []
            
            for i in range(len(data['text'])):
                if int(data['conf'][i]) > 0:
                    text_parts.append(data['text'][i])
                    confidences.append(int(data['conf'][i]))
            
            text = ''.join(text_parts).strip()
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            return OCRResult(text, avg_confidence / 100, 'tesseract')
        except Exception as e:
            return OCRResult('', 0, 'tesseract')

    def easyocr_ocr(self, image) -> OCRResult:
        """Use EasyOCR for license plate recognition"""
        try:
            import easyocr
            reader = easyocr.Reader(['en'])
            results = reader.readtext(image)
            
            if results:
                # Get the result with highest confidence
                best_result = max(results, key=lambda x: x[2])
                text = best_result[1].upper().replace(' ', '')
                confidence = best_result[2]
                return OCRResult(text, confidence, 'easyocr')
            else:
                return OCRResult('', 0, 'easyocr')
        except ImportError:
            return OCRResult('', 0, 'easyocr')  # EasyOCR not installed
        except Exception as e:
            return OCRResult('', 0, 'easyocr')

    def paddleocr_ocr(self, image) -> OCRResult:
        """Use PaddleOCR for license plate recognition"""
        try:
            from paddleocr import PaddleOCR
            ocr = PaddleOCR(use_angle_cls=True, lang='en', show_log=False)
            results = ocr.ocr(image, cls=True)
            
            if results and results[0]:
                # Get the result with highest confidence
                best_result = max(results[0], key=lambda x: x[1][1])
                text = best_result[1][0].upper().replace(' ', '')
                confidence = best_result[1][1]
                return OCRResult(text, confidence, 'paddleocr')
            else:
                return OCRResult('', 0, 'paddleocr')
        except ImportError:
            return OCRResult('', 0, 'paddleocr')  # PaddleOCR not installed
        except Exception as e:
            return OCRResult('', 0, 'paddleocr')

    def clean_license_plate(self, text: str) -> str:
        """Clean and validate license plate text"""
        # Remove non-alphanumeric characters
        cleaned = re.sub(r'[^A-Z0-9]', '', text.upper())
        
        # Basic validation - most plates are 6-8 characters
        if 3 <= len(cleaned) <= 10:
            return cleaned
        return ''

    def get_consensus_result(self, results: List[OCRResult]) -> Tuple[str, float, bool]:
        """Get consensus from multiple OCR results"""
        valid_results = [r for r in results if r.text and r.confidence > 0.1]
        
        if not valid_results:
            return '', 0, True  # Alert needed
        
        # Clean all results
        cleaned_results = []
        for result in valid_results:
            cleaned = self.clean_license_plate(result.text)
            if cleaned:
                cleaned_results.append(OCRResult(cleaned, result.confidence, result.source))
        
        if not cleaned_results:
            return '', 0, True  # Alert needed
        
        # Group by text
        text_groups = {}
        for result in cleaned_results:
            if result.text not in text_groups:
                text_groups[result.text] = []
            text_groups[result.text].append(result)
        
        # Find consensus
        total_engines = len(self.ocr_engines)
        for text, group in text_groups.items():
            agreement_ratio = len(group) / total_engines
            avg_confidence = sum(r.confidence for r in group) / len(group)
            
            # Strong agreement (3/3 or 3/4) and good confidence
            if agreement_ratio >= self.agreement_threshold and avg_confidence >= self.confidence_threshold:
                return text, avg_confidence, False  # No alert needed
        
        # No strong consensus or low confidence
        if text_groups:
            # Return the most common result but with alert
            best_group = max(text_groups.values(), key=len)
            best_text = best_group[0].text
            best_confidence = sum(r.confidence for r in best_group) / len(best_group)
            return best_text, best_confidence, True  # Alert needed
        
        return '', 0, True  # Alert needed

    def recognize_license_plate(self, image) -> Tuple[str, float, bool]:
        """Main recognition function"""
        preprocessed = self.preprocess_image(image)
        results = []
        
        # Run all OCR engines
        for engine_name, engine_func in self.ocr_engines.items():
            result = engine_func(preprocessed)
            results.append(result)
        
        return self.get_consensus_result(results)

class ScreenAutomation:
    def __init__(self):
        self.target_field = None
        self.field_template = None
        
    def capture_screen_region(self, region=None):
        """Capture screen or specific region"""
        if region:
            return pyautogui.screenshot(region=region)
        return pyautogui.screenshot()
    
    def find_text_field(self, template_image=None):
        """Find text input field on screen"""
        if template_image:
            # Use template matching
            screenshot = np.array(pyautogui.screenshot())
            template = np.array(template_image)
            
            result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            if max_val > 0.8:  # Good match
                return max_loc
        
        # Fallback: look for cursor or active field
        return pyautogui.position()  # Return current mouse position
    
    def click_and_type(self, text, position=None):
        """Click on position and type text"""
        if position:
            pyautogui.click(position)
        
        # Clear existing text
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.1)
        
        # Type new text
        pyautogui.typewrite(text)

class LicensePlateApp:
    def __init__(self):
        self.recognizer = LicensePlateRecognizer()
        self.screen_automation = ScreenAutomation()
        self.running = False
        
        # Create GUI
        self.root = tk.Tk()
        self.root.title("License Plate Recognition System")
        self.root.geometry("600x400")
        
        self.setup_gui()
        
    def setup_gui(self):
        """Setup the GUI interface"""
        # Control buttons
        control_frame = tk.Frame(self.root)
        control_frame.pack(pady=10)
        
        self.start_button = tk.Button(control_frame, text="Start Recognition", 
                                     command=self.start_recognition, bg='green', fg='white')
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = tk.Button(control_frame, text="Stop", 
                                    command=self.stop_recognition, bg='red', fg='white')
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        self.calibrate_button = tk.Button(control_frame, text="Set Target Field", 
                                         command=self.set_target_field, bg='blue', fg='white')
        self.calibrate_button.pack(side=tk.LEFT, padx=5)
        
        # Status display
        self.status_var = tk.StringVar(value="Ready")
        status_label = tk.Label(self.root, textvariable=self.status_var, font=('Arial', 12))
        status_label.pack(pady=5)
        
        # Results display
        results_frame = tk.Frame(self.root)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Label(results_frame, text="Recognition Results:", font=('Arial', 10, 'bold')).pack(anchor=tk.W)
        
        self.results_text = tk.Text(results_frame, height=15, width=70)
        self.results_text.pack(fill=tk.BOTH, expand=True)
        
        # Configuration
        config_frame = tk.Frame(self.root)
        config_frame.pack(pady=5)
        
        tk.Label(config_frame, text="Scan Interval (seconds):").pack(side=tk.LEFT)
        self.interval_var = tk.StringVar(value="2")
        interval_entry = tk.Entry(config_frame, textvariable=self.interval_var, width=5)
        interval_entry.pack(side=tk.LEFT, padx=5)
        
    def set_target_field(self):
        """Set the target field for text insertion"""
        messagebox.showinfo("Set Target Field", 
                           "Click OK, then click on the text field where you want to insert license plates.\n"
                           "You have 3 seconds after clicking OK.")
        
        self.root.after(3000, self.capture_target_position)
        
    def capture_target_position(self):
        """Capture the target field position"""
        self.target_position = pyautogui.position()
        self.log_result(f"Target field set at position: {self.target_position}")
        
    def start_recognition(self):
        """Start the recognition process"""
        if not hasattr(self, 'target_position'):
            messagebox.showwarning("No Target Field", "Please set a target field first!")
            return
            
        self.running = True
        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')
        self.status_var.set("Running...")
        
        # Start recognition thread
        self.recognition_thread = threading.Thread(target=self.recognition_loop)
        self.recognition_thread.daemon = True
        self.recognition_thread.start()
        
    def stop_recognition(self):
        """Stop the recognition process"""
        self.running = False
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.status_var.set("Stopped")
        
    def recognition_loop(self):
        """Main recognition loop"""
        while self.running:
            try:
                # Capture screen region (you might want to define a specific region)
                screenshot = pyautogui.screenshot()
                screenshot_np = np.array(screenshot)
                
                # Look for license plates in the screenshot
                # This is a simplified approach - you might want to add license plate detection
                # For now, we'll process the entire screenshot
                
                plate_text, confidence, needs_alert = self.recognizer.recognize_license_plate(screenshot_np)
                
                if plate_text:
                    self.log_result(f"Detected: {plate_text} (Confidence: {confidence:.2f})")
                    
                    if needs_alert:
                        self.show_alert(plate_text, confidence)
                    else:
                        # Auto-insert the text
                        self.screen_automation.click_and_type(plate_text, self.target_position)
                        self.log_result(f"Auto-inserted: {plate_text}")
                
                # Wait before next scan
                interval = float(self.interval_var.get())
                time.sleep(interval)
                
            except Exception as e:
                self.log_result(f"Error: {str(e)}")
                time.sleep(1)
                
    def show_alert(self, plate_text, confidence):
        """Show alert for uncertain results"""
        def alert_dialog():
            result = messagebox.askyesno("Uncertain Recognition", 
                                       f"Detected plate: {plate_text}\n"
                                       f"Confidence: {confidence:.2f}\n\n"
                                       f"Insert this text?")
            if result:
                self.screen_automation.click_and_type(plate_text, self.target_position)
                self.log_result(f"Manual confirmation: {plate_text}")
            else:
                self.log_result(f"Rejected: {plate_text}")
        
        self.root.after(0, alert_dialog)
        
    def log_result(self, message):
        """Log result to the GUI"""
        def update_log():
            self.results_text.insert(tk.END, f"{time.strftime('%H:%M:%S')} - {message}\n")
            self.results_text.see(tk.END)
        
        self.root.after(0, update_log)
        
    def run(self):
        """Run the application"""
        self.root.mainloop()

if __name__ == "__main__":
    app = LicensePlateApp()
    app.run()