"""
Script to check and report read/write permissions for each OCR model cache directory.
Run this script to verify that your Python process can access the model files for all OCR engines.
"""
import os

def check_permissions(path):
    exists = os.path.exists(path)
    readable = os.access(path, os.R_OK)
    writable = os.access(path, os.W_OK)
    return exists, readable, writable

cache_dirs = {
    'keras-ocr': os.environ.get('KERAS_HOME', os.path.expanduser('~/.keras-ocr')),
    'paddleocr': os.environ.get('PADDLEOCR_HOME', os.path.expanduser('~/.paddleocr')),
    'easyocr': os.path.expanduser('~/.EasyOCR/model'),
    'doctr': os.environ.get('DOCTR_CACHE_DIR', os.path.expanduser('~/.cache/doctr')),
}

for name, path in cache_dirs.items():
    exists, readable, writable = check_permissions(path)
    print(f"[{name}] {path}")
    print(f"  Exists:   {exists}")
    print(f"  Readable: {readable}")
    print(f"  Writable: {writable}")
    if not exists:
        print(f"  [!] Directory does not exist!")
    print()

print("Done. If any directory is not readable or writable, fix permissions or run as the correct user.")
