"""
Debug script to print OCR model cache directories and check for model file existence.
Run this script to see which directories are being used by each OCR engine and whether the expected model files are present.
"""
import os
import sys

# Keras-OCR
try:
    import keras_ocr
    keras_home = os.environ.get('KERAS_HOME', os.path.expanduser('~/.keras-ocr'))
    print(f"[keras-ocr] Model cache dir: {keras_home}")
    for root, dirs, files in os.walk(keras_home):
        for f in files:
            print(f"[keras-ocr] Found: {os.path.join(root, f)}")
except ImportError:
    print("[keras-ocr] Not installed")

# PaddleOCR
try:
    from paddleocr import PaddleOCR
    paddle_home = os.environ.get('PADDLEOCR_HOME', os.path.expanduser('~/.paddleocr'))
    print(f"[PaddleOCR] Model cache dir: {paddle_home}")
    for root, dirs, files in os.walk(paddle_home):
        for f in files:
            print(f"[PaddleOCR] Found: {os.path.join(root, f)}")
except ImportError:
    print("[PaddleOCR] Not installed")

# EasyOCR
try:
    import easyocr
    easyocr_home = os.path.expanduser('~/.EasyOCR/model')
    print(f"[EasyOCR] Model cache dir: {easyocr_home}")
    for root, dirs, files in os.walk(easyocr_home):
        for f in files:
            print(f"[EasyOCR] Found: {os.path.join(root, f)}")
except ImportError:
    print("[EasyOCR] Not installed")

# DocTR
try:
    from doctr.models import ocr_predictor
    doctr_home = os.environ.get('DOCTR_CACHE_DIR', os.path.expanduser('~/.cache/doctr'))
    print(f"[DocTR] Model cache dir: {doctr_home}")
    for root, dirs, files in os.walk(doctr_home):
        for f in files:
            print(f"[DocTR] Found: {os.path.join(root, f)}")
except ImportError:
    print("[DocTR] Not installed")

# Tesseract (no model cache, uses system install)
try:
    import pytesseract
    print(f"[Tesseract] pytesseract version: {pytesseract.get_tesseract_version()}")
    print("[Tesseract] Uses system tesseract, no model cache directory.")
except ImportError:
    print("[Tesseract] Not installed")

print("\nDone. If you see the expected model files above, the OCR engine should not re-download them. If not, check permissions and environment variables.")
