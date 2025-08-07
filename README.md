
# License Plate Detector (Modular Refactor)

## Overview
This project is a modular, professional Python application for license plate detection and recognition. It is designed for maintainability, scalability, and easy extension with new OCR engines or features.

## Features
- Modular codebase: OCR engines, GUI, automation, utilities, and data models are separated for clarity and maintainability.
- Tkinter-based GUI for user interaction and results display.
- Multiple OCR engine support (Tesseract, EasyOCR, PaddleOCR, and more planned).
- Utilities for image preprocessing, plate cleaning, and consensus logic.
- Automation for screen capture and text field interaction.
- Unit tests for core utilities.

## Project Structure
```
LicensePlateDetectorJules/
├── main.py                # Entry point
├── requirements.txt
├── README.md
├── plan_refactor_structure.md
├── ocr/                   # OCR engine modules
├── gui/                   # GUI logic and widgets
├── automation/            # Screen automation
├── utils/                 # Image processing and validation
├── models.py              # Data models
└── tests/                 # Unit tests
```

## Models & OCR Engines
> **Note:** The number and type of OCR models required for this application is not yet finalized. The project is designed to support multiple engines (Tesseract, EasyOCR, PaddleOCR, Keras-OCR, DocTR, etc.), but the optimal combination and configuration may change as development continues.

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
python main.py
```

## Testing
Run unit tests with:
```
python -m unittest discover tests
```

## Contributing
- Please open issues or pull requests for bugs, improvements, or new OCR engine integrations.
- The codebase is structured for easy extension and testing.

## License
MIT License
