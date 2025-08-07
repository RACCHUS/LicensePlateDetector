import tkinter as tk
from tkinter import messagebox
import threading
import time
import numpy as np
from models import OCRResult
from ocr.tesseract_engine import TesseractEngine
from ocr.easyocr_engine import EasyOCREngine
from ocr.paddleocr_engine import PaddleOCREngine
from automation.screen import ScreenAutomation


class LicensePlateApp:
    def __init__(self):
        self.recognizer = None  # To be set up with new modular recognizer
        self.screen_automation = ScreenAutomation()
        self.running = False
        self.root = tk.Tk()
        self.root.title("License Plate Recognition System")
        self.root.geometry("600x400")
        self.status_var = tk.StringVar(value="Ready")
        self.setup_gui()

    def set_target_field(self):
        def capture_click():
            try:
                self.status_var.set('Click on the target field...')
                self.root.iconify()
                messagebox.showinfo('Set Target Field', 'Move your mouse to the target field and left-click to set its position.')
                import pyautogui
                pos = None
                while pos is None:
                    if pyautogui.mouseDown(button='left'):
                        pos = pyautogui.position()
                        break
                self.root.deiconify()
                self.status_var.set(f'Target field set at {pos}')
                self.log_result(f'Target field set at {pos}')
                self.screen_automation.target_field = (pos.x, pos.y)
            except Exception as e:
                self.root.deiconify()
                self.status_var.set('Target field selection cancelled')
                self.log_result(f'Target field selection cancelled: {e}')
        threading.Thread(target=capture_click, daemon=True).start()

    def setup_gui(self):
        control_frame = tk.Frame(self.root)
        control_frame.pack(pady=10)
        self.start_button = tk.Button(control_frame, text="Start Recognition", command=self.start_recognition, bg='green', fg='white')
        self.start_button.pack(side=tk.LEFT, padx=5)
        self.stop_button = tk.Button(control_frame, text="Stop", command=self.stop_recognition, bg='red', fg='white')
        self.stop_button.pack(side=tk.LEFT, padx=5)
        self.calibrate_button = tk.Button(control_frame, text="Set Target Field", command=self.set_target_field, bg='blue', fg='white')
        self.calibrate_button.pack(side=tk.LEFT, padx=5)
        status_label = tk.Label(self.root, textvariable=self.status_var, font=('Arial', 12))
        status_label.pack(pady=5)
        results_frame = tk.Frame(self.root)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        tk.Label(results_frame, text="Recognition Results:", font=('Arial', 10, 'bold')).pack(anchor=tk.W)
        self.results_text = tk.Text(results_frame, height=15, width=70)
        self.results_text.pack(fill=tk.BOTH, expand=True)
        config_frame = tk.Frame(self.root)
        config_frame.pack(pady=5)
        tk.Label(config_frame, text="Scan Interval (seconds):").pack(side=tk.LEFT)
        self.interval_var = tk.StringVar(value="2")
        interval_entry = tk.Entry(config_frame, textvariable=self.interval_var, width=5)
        interval_entry.pack(side=tk.LEFT, padx=5)


    def start_recognition(self):
        if not self.running:
            self.running = True
            self.status_var.set("Running")
            self.log_result("Recognition started.")
            threading.Thread(target=self.recognition_loop, daemon=True).start()

    def stop_recognition(self):
        self.running = False
        self.status_var.set("Stopped")
        self.log_result("Recognition stopped.")

    def recognition_loop(self):
        while self.running:
            # Simulate recognition result
            now = time.strftime('%H:%M:%S')
            self.log_result(f"{now} - Dummy recognition result: ABC1234 (Conf: 0.95)")
            time.sleep(float(self.interval_var.get()))

    def log_result(self, message):
        self.results_text.insert(tk.END, message + '\n')
        self.results_text.see(tk.END)
