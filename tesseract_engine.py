from typing import Callable, Optional
from dataclasses import dataclass

@dataclass
class OCRResult:
    text: str
    confidence: float
    source: str

def tesseract_ocr(image, pytesseract, clean_license_plate: Callable[[str], str], log_result: Optional[Callable[[str], None]] = None) -> OCRResult:
    if not pytesseract:
        return OCRResult('', 0.0, 'tesseract')
    try:
        text = pytesseract.image_to_string(image, config='--psm 7')
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        candidates = []
        for idx, line in enumerate(lines):
            debug_msg = f"Tesseract candidate: '{line}'"
            print(debug_msg)
            if log_result:
                log_result(debug_msg)
            cleaned = clean_license_plate(line)
            debug_cleaned = f"Tesseract cleaned: '{cleaned}'"
            print(debug_cleaned)
            if log_result:
                log_result(debug_cleaned)
            if cleaned:
                return OCRResult(cleaned, 0.8, 'tesseract')
            candidates.append(line)
        if len(candidates) == 2:
            joined = candidates[0] + candidates[1]
            debug_msg = f"Tesseract joined candidate: '{joined}'"
            print(debug_msg)
            if log_result:
                log_result(debug_msg)
            cleaned = clean_license_plate(joined)
            debug_cleaned = f"Tesseract joined cleaned: '{cleaned}'"
            print(debug_cleaned)
            if log_result:
                log_result(debug_cleaned)
            if cleaned:
                return OCRResult(cleaned, 0.8, 'tesseract')
        return OCRResult('', 0.0, 'tesseract')
    except Exception as e:
        error_msg = f"Tesseract error: {e}"
        print(error_msg)
        if log_result:
            log_result(error_msg)
        return OCRResult('', 0.0, 'tesseract') 