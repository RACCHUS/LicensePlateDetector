import tkinter as tk
from tkinter import messagebox, simpledialog
from threading import Thread
import time
from license_plate_recognizer import LicensePlateRecognizer
from screen_automation import ScreenAutomation
import pyautogui

class LicensePlateApp:
    def __init__(self, root):
        self.root = root
        self.root.title("License Plate Recognition System")
        self.recognizer = LicensePlateRecognizer()
        self.screen_automation = ScreenAutomation()
        self.running = False
        self.setup_gui()

    def setup_gui(self):
        self.root.geometry("500x400")

        control_frame = tk.Frame(self.root)
        control_frame.pack(pady=10)

        self.start_button = tk.Button(control_frame, text="Start Recognition", command=self.start_recognition)
        self.start_button.pack(side=tk.LEFT, padx=5)

        self.stop_button = tk.Button(control_frame, text="Stop", command=self.stop_recognition, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)

        self.set_target_button = tk.Button(control_frame, text="Set Target Field", command=self.set_target_field)
        self.set_target_button.pack(side=tk.LEFT, padx=5)

        status_frame = tk.Frame(self.root)
        status_frame.pack(pady=5)

        self.status_label = tk.Label(status_frame, text="Status: Ready")
        self.status_label.pack()

        results_frame = tk.Frame(self.root)
        results_frame.pack(pady=10, fill=tk.BOTH, expand=True)

        self.results_text = tk.Text(results_frame, height=10, width=60)
        self.results_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(results_frame, command=self.results_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.results_text.config(yscrollcommand=scrollbar.set)

        scan_interval_frame = tk.Frame(self.root)
        scan_interval_frame.pack(pady=5)

        tk.Label(scan_interval_frame, text="Scan Interval:").pack(side=tk.LEFT)
        self.scan_interval_entry = tk.Entry(scan_interval_frame, width=5)
        self.scan_interval_entry.insert(0, "2")
        self.scan_interval_entry.pack(side=tk.LEFT)
        tk.Label(scan_interval_frame, text="seconds").pack(side=tk.LEFT)

    def start_recognition(self):
        if not self.screen_automation.target_field:
            messagebox.showerror("Error", "Please set the target field first.")
            return

        self.running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.set_target_button.config(state=tk.DISABLED)
        self.status_label.config(text="Status: Running")
        self.log_result("Recognition started.")

        self.recognition_thread = Thread(target=self.recognition_loop)
        self.recognition_thread.daemon = True
        self.recognition_thread.start()

    def stop_recognition(self):
        self.running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.set_target_button.config(state=tk.NORMAL)
        self.status_label.config(text="Status: Stopped")
        self.log_result("Recognition stopped.")

    def set_target_field(self):
        self.log_result("Please click on the target text field.")
        self.root.iconify()
        time.sleep(1)

        # This is a simplified way to get the click position.
        # A more robust solution would involve a proper screen listener.
        try:
            # For this example, we will just use the current mouse position
            # after a short delay, assuming the user has clicked the target field.
            # In a real application, you might use a library like 'pynput' to listen for a click.
            time.sleep(3) # Give user time to click
            x, y = pyautogui.position()
            self.screen_automation.target_field = (x, y)
            self.log_result(f"Target field set at ({x}, {y})")
        except Exception as e:
            self.log_result(f"Error setting target field: {e}")
        finally:
            self.root.deiconify()

    def recognition_loop(self):
        scan_interval = float(self.scan_interval_entry.get())
        while self.running:
            try:
                # Define a region around the target field to capture
                x, y = self.screen_automation.target_field
                region = (x - 150, y - 50, 300, 100) # Adjust as needed

                image = self.screen_automation.capture_screen_region(region)
                text, confidence, alert_flag = self.recognizer.recognize_license_plate(image)

                if text:
                    if not alert_flag:
                        self.log_result(f"Detected: {text} (Conf: {confidence:.2f}) - Auto-inserting.")
                        self.screen_automation.click_and_type(text, self.screen_automation.target_field)
                    else:
                        self.log_result(f"Detected: {text} (Conf: {confidence:.2f}) - Manual confirmation needed.")
                        self.show_alert(text, confidence)
                else:
                    self.log_result("No license plate detected.")
            except Exception as e:
                self.log_result(f"An error occurred in recognition loop: {e}")

            time.sleep(scan_interval)

    def show_alert(self, text, confidence):
        # Schedule the messagebox to be shown from the main thread
        self.root.after(0, self._show_alert_sync, text, confidence)

    def _show_alert_sync(self, text, confidence):
        response = messagebox.askyesno(
            "Uncertain Recognition",
            f"Detected plate: {text}\nConfidence: {confidence:.2f}\n\nInsert this text?"
        )
        if response:
            self.log_result(f"User approved insertion of {text}.")
            self.screen_automation.click_and_type(text, self.screen_automation.target_field)
        else:
            self.log_result(f"User rejected insertion of {text}.")

    def log_result(self, message):
        # Schedule the text widget update to be run from the main thread
        self.root.after(0, self._log_result_sync, message)

    def _log_result_sync(self, message):
        timestamp = time.strftime("%H:%M:%S")
        self.results_text.insert(tk.END, f"{timestamp} - {message}\n")
        self.results_text.see(tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = LicensePlateApp(root)
    root.mainloop()
