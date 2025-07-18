# LicensePlateDetector

Using OCRs to detect and input license plates.

## Setup

1. Install Python 3.8+.
2. Install Tesseract OCR (system package, e.g. `sudo apt install tesseract-ocr`).
3. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the application:
```bash
python license_plate_app.py
```

## Features
- Multi-engine OCR (Tesseract, EasyOCR, PaddleOCR)
- Consensus-based validation
- Automated screen capture and text insertion
- Tkinter GUI for control and alerts

## Notes
- All processing is local; no data is sent to the cloud.
- No persistent storage; all data is session-based.
