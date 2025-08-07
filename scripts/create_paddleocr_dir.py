"""
Script to create the PaddleOCR model cache directory if it does not exist.
Run this script to ensure PaddleOCR can cache its models and avoid repeated downloads.
"""
import os

paddleocr_dir = os.path.expanduser('~/.paddleocr')

if not os.path.exists(paddleocr_dir):
    os.makedirs(paddleocr_dir)
    print(f"Created directory: {paddleocr_dir}")
else:
    print(f"Directory already exists: {paddleocr_dir}")

print("Done. You can now re-run your app and PaddleOCR should use this directory for model caching.")
