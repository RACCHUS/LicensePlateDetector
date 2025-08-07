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
        self.setup_gui()

    def setup_gui(self):
        control_frame = tk.Frame(self.root)
        control_frame.pack(pady=10)
        self.start_button = tk.Button(control_frame, text="Start Recognition", command=self.start_recognition, bg='green', fg='white')
        self.start_button.pack(side=tk.LEFT, padx=5)
        self.stop_button = tk.Button(control_frame, text="Stop", command=self.stop_recognition, bg='red', fg='white')
        self.stop_button.pack(side=tk.LEFT, padx=5)
        self.calibrate_button = tk.Button(control_frame, text="Set Target Field", command=self.set_target_field, bg='blue', fg='white')
        self.calibrate_button.pack(side=tk.LEFT, padx=5)
        self.status_var = tk.StringVar(value="Ready")
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

    # ...existing methods (set_target_field, capture_target_position, start_recognition, stop_recognition, recognition_loop, show_alert, log_result, run)...
