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
        debug_raw = f"PaddleOCR raw result: {result}"
        print(debug_raw)
        if log_result:
            log_result(debug_raw)
        from state_filters import is_state_name_or_abbreviation
        candidates = []
        # Handle new PaddleOCR result format (list of dicts with rec_texts/rec_scores)
        if isinstance(result, list) and len(result) > 0 and isinstance(result[0], dict) and 'rec_texts' in result[0] and 'rec_scores' in result[0]:
            rec_texts = result[0]['rec_texts']
            rec_scores = result[0]['rec_scores']
            for text, conf in zip(rec_texts, rec_scores):
                debug_msg = f"PaddleOCR candidate: '{text}' (conf: {conf})"
                print(debug_msg)
                if log_result:
                    log_result(debug_msg)
                cleaned = clean_license_plate(text)
                debug_cleaned = f"PaddleOCR cleaned: '{cleaned}'"
                print(debug_cleaned)
                if log_result:
                    log_result(debug_cleaned)
                if cleaned and not is_state_name_or_abbreviation(cleaned):
                    candidates.append((cleaned, float(conf)))
        else:
            # Fallback to old format
            if not isinstance(result, list):
                result = []
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
                if cleaned and not is_state_name_or_abbreviation(cleaned):
                    candidates.append((cleaned, conf))

        if candidates:
            # If two candidates, try joining them (for split plates like 'GHT' + '8670')
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
            # Otherwise, select the candidate with the longest cleaned text
            best = max(candidates, key=lambda x: len(x[0]))
            return OCRResult(best[0], best[1], 'paddleocr')
        warn_msg = "PaddleOCR: No valid license plate candidates found."
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