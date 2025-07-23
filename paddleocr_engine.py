from typing import Callable, Optional
from dataclasses import dataclass
import numpy as np

@dataclass
class OCRResult:
    text: str
    confidence: float
    source: str

def paddleocr_ocr(image, paddleocr_reader, clean_license_plate: Callable[[str], str], log_result: Optional[Callable[[str], None]] = None) -> OCRResult:
    if not paddleocr_reader:
        return OCRResult('', 0.0, 'paddleocr')
    try:
        result = paddleocr_reader.ocr(np.array(image))
        # Log the raw result for debugging
        debug_raw = f"PaddleOCR raw result: {result}"
        print(debug_raw)
        if log_result:
            log_result(debug_raw)
        if not isinstance(result, list):
            result = []
        candidates = []
        for r in result:
            # r is typically [ [box], [text, confidence] ]
            if not (isinstance(r, list) and len(r) == 2 and isinstance(r[1], list) and len(r[1]) == 2):
                continue
            text = r[1][0]
            conf = float(r[1][1])
            debug_msg = f"PaddleOCR candidate: '{text}' (conf: {conf})"
            print(debug_msg)
            if log_result:
                log_result(debug_msg)
            cleaned = clean_license_plate(text)
            debug_cleaned = f"PaddleOCR cleaned: '{cleaned}'"
            print(debug_cleaned)
            if log_result:
                log_result(debug_cleaned)
            if cleaned:
                return OCRResult(cleaned, conf, 'paddleocr')
            candidates.append((text, conf))
        if len(candidates) == 2:
            joined = candidates[0][0] + candidates[1][0]
            joined_conf = min(candidates[0][1], candidates[1][1])
            debug_msg = f"PaddleOCR joined candidate: '{joined}' (conf: {joined_conf})"
            print(debug_msg)
            if log_result:
                log_result(debug_msg)
            cleaned = clean_license_plate(joined)
            debug_cleaned = f"PaddleOCR joined cleaned: '{cleaned}'"
            print(debug_cleaned)
            if log_result:
                log_result(debug_cleaned)
            if cleaned:
                return OCRResult(cleaned, joined_conf, 'paddleocr')
        if not candidates:
            warn_msg = "PaddleOCR: No valid candidates found in result."
            print(warn_msg)
            if log_result:
                log_result(warn_msg)
        return OCRResult('', 0.0, 'paddleocr')
    except Exception as e:
        error_msg = f"PaddleOCR error: {e}"
        print(error_msg)
        if log_result:
            log_result(error_msg)
        return OCRResult('', 0.0, 'paddleocr') 