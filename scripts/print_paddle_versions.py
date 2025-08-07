"""
Script to print the installed PaddleOCR and paddlex versions.
Run this to verify which versions are installed and help debug cache path issues.
"""
try:
    import paddleocr
    print(f"PaddleOCR version: {paddleocr.__version__}")
except ImportError:
    print("PaddleOCR is not installed.")

try:
    import paddlex
    print(f"PaddleX version: {paddlex.__version__}")
except ImportError:
    print("PaddleX is not installed.")
