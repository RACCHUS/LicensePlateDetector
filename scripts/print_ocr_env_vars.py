"""
Script to print and verify the environment variables used for OCR model cache directories.
Run this script to see the current values and check if they are set as expected.
"""
import os

env_vars = {
    'KERAS_HOME': os.environ.get('KERAS_HOME'),
    'PADDLEOCR_HOME': os.environ.get('PADDLEOCR_HOME'),
    'DOCTR_CACHE_DIR': os.environ.get('DOCTR_CACHE_DIR'),
}

for var, value in env_vars.items():
    if value:
        print(f"{var} is set to: {value}")
    else:
        print(f"{var} is NOT set (using library default)")

print("\nTo set an environment variable for this session:")
print("  set KERAS_HOME=C:\\path\\to\\keras-ocr-cache")
print("  set PADDLEOCR_HOME=C:\\path\\to\\paddleocr-cache")
print("  set DOCTR_CACHE_DIR=C:\\path\\to\\doctr-cache")
print("\nSet these before running your Python app if you want to override the default cache locations.")
