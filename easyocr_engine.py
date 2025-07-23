from typing import Callable, Optional
from dataclasses import dataclass
import numpy as np

@dataclass
class OCRResult:
    text: str
    confidence: float
    source: str

def easyocr_ocr(image, easyocr_reader, clean_license_plate: Callable[[str], str], log_result: Optional[Callable[[str], None]] = None) -> OCRResult:
    if not easyocr_reader:
        return OCRResult('', 0.0, 'easyocr')
    try:
        result = easyocr_reader.readtext(np.array(image))
        candidates = []
        for r in result:
            text, conf = r[1], float(r[2])
            debug_msg = f"EasyOCR candidate: '{text}' (conf: {conf})"
            print(debug_msg)
            if log_result:
                log_result(debug_msg)
            cleaned = clean_license_plate(text)
            debug_cleaned = f"EasyOCR cleaned: '{cleaned}'"
            print(debug_cleaned)
            if log_result:
                log_result(debug_cleaned)
            if cleaned:
                return OCRResult(cleaned, conf, 'easyocr')
            candidates.append((text, conf))
        if len(candidates) == 2:
            joined = candidates[0][0] + candidates[1][0]
            joined_conf = min(candidates[0][1], candidates[1][1])
            debug_msg = f"EasyOCR joined candidate: '{joined}' (conf: {joined_conf})"
            print(debug_msg)
            if log_result:
                log_result(debug_msg)
            cleaned = clean_license_plate(joined)
            debug_cleaned = f"EasyOCR joined cleaned: '{cleaned}'"
            print(debug_cleaned)
            if log_result:
                log_result(debug_cleaned)
            if cleaned:
                return OCRResult(cleaned, joined_conf, 'easyocr')
        return OCRResult('', 0.0, 'easyocr')
    except Exception as e:
        error_msg = f"EasyOCR error: {e}"
        print(error_msg)
        if log_result:
            log_result(error_msg)
        return OCRResult('', 0.0, 'easyocr') 