import cv2
# import pytesseract
# import easyocr
# from paddleocr import PaddleOCR
from dataclasses import dataclass
from typing import Dict, Tuple, Optional, List
import numpy as np
import random

@dataclass
class OCRResult:
    text: str
    confidence: float
    source: str

class LicensePlateRecognizer:
    def __init__(self, confidence_threshold: float = 0.6, agreement_threshold: float = 0.75):
        self.ocr_engines: Dict[str, callable] = {
            'tesseract': self.tesseract_ocr,
            'easyocr': self.easyocr_ocr,
            'paddleocr': self.paddleocr_ocr
        }
        self.confidence_threshold = confidence_threshold
        self.agreement_threshold = agreement_threshold
        # self.easyocr_reader = easyocr.Reader(['en'])
        # self.paddleocr_reader = PaddleOCR(use_angle_cls=True, lang='en')

    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        _, thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        kernel = np.ones((3, 3), np.uint8)
        closing = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        if closing.shape[0] < 50:
            closing = cv2.resize(closing, (closing.shape[1] * 2, closing.shape[0] * 2), interpolation=cv2.INTER_CUBIC)
        return closing

    def tesseract_ocr(self, image: np.ndarray) -> OCRResult:
        # Mocked OCR
        return self.mock_ocr('tesseract')

    def easyocr_ocr(self, image: np.ndarray) -> OCRResult:
        # Mocked OCR
        return self.mock_ocr('easyocr')

    def paddleocr_ocr(self, image: np.ndarray) -> OCRResult:
        # Mocked OCR
        return self.mock_ocr('paddleocr')

    def mock_ocr(self, source: str) -> OCRResult:
        # Simulate OCR results with some randomness
        plates = ["ABC123", "XYZ789", "DEF456"]
        text = random.choice(plates)
        confidence = random.uniform(0.5, 0.95)
        if random.random() < 0.1: # 10% chance of returning a different plate
            text = random.choice([p for p in plates if p != text])
        return OCRResult(text=text, confidence=confidence, source=source)

    def clean_license_plate(self, text: str) -> str:
        clean_text = ''.join(filter(str.isalnum, text)).upper()
        if 3 <= len(clean_text) <= 10:
            return clean_text
        return ""

    def get_consensus_result(self, results: List[OCRResult]) -> Tuple[Optional[str], float, bool]:
        valid_results = [r for r in results if r.confidence > 0.1]
        if not valid_results:
            return None, 0.0, True

        cleaned_results = {r.source: self.clean_license_plate(r.text) for r in valid_results}
        text_groups = {}
        for source, text in cleaned_results.items():
            if text not in text_groups:
                text_groups[text] = []
            text_groups[text].append(source)

        for text, sources in text_groups.items():
            agreement_ratio = len(sources) / len(self.ocr_engines)
            confidences = [r.confidence for r in valid_results if r.source in sources]
            avg_confidence = sum(confidences) / len(confidences)
            if agreement_ratio >= self.agreement_threshold and avg_confidence >= self.confidence_threshold:
                return text, avg_confidence, False

        # If no strong consensus, return most common result with alert flag
        if text_groups:
            most_common_text = max(text_groups, key=lambda k: len(text_groups[k]))
            confidences = [r.confidence for r in valid_results if self.clean_license_plate(r.text) == most_common_text]
            avg_confidence = sum(confidences) / len(confidences)
            return most_common_text, avg_confidence, True

        return None, 0.0, True

    def recognize_license_plate(self, image: np.ndarray) -> Tuple[Optional[str], float, bool]:
        preprocessed_image = self.preprocess_image(image)
        results = [engine(preprocessed_image) for engine in self.ocr_engines.values()]
        return self.get_consensus_result(results)
