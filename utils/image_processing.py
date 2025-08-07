import cv2
import numpy as np

def preprocess_image(image):
    """Preprocess image for better OCR results"""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    kernel = np.ones((3, 3), np.uint8)
    cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    height, width = cleaned.shape
    if height < 50:
        scale_factor = 50 / height
        new_width = int(width * scale_factor)
        cleaned = cv2.resize(cleaned, (new_width, 50), interpolation=cv2.INTER_CUBIC)
    return cleaned
