from typing import Callable, Optional
from dataclasses import dataclass
import numpy as np
import keras_ocr

@dataclass
class OCRResult:
    text: str
    confidence: float
    source: str

def kerasocr_ocr(image, kerasocr_pipeline, clean_license_plate: Callable[[str], str], log_result: Optional[Callable[[str], None]] = None) -> OCRResult:
    if not kerasocr_pipeline:
        return OCRResult('', 0.0, 'keras-ocr')
    try:
        from state_filters import is_state_name_or_abbreviation
        # Keras-OCR expects a list of numpy arrays
        images = [np.array(image)]
        prediction_groups = kerasocr_pipeline.recognize(images)

        # We only sent one image, so we only care about the first group
        if not prediction_groups:
            return OCRResult('', 0.0, 'keras-ocr')

        predictions = prediction_groups[0]

        if not predictions:
            return OCRResult('', 0.0, 'keras-ocr')

        candidates = []
        for pred in predictions:
            text = pred[0]
            conf = 0.9  # Placeholder confidence
            debug_msg = f"Keras-OCR candidate: '{text}' (conf: {conf})"
            print(debug_msg)
            if log_result:
                log_result(debug_msg)
            cleaned = clean_license_plate(text)
            debug_cleaned = f"Keras-OCR cleaned: '{cleaned}'"
            print(debug_cleaned)
            if log_result:
                log_result(debug_cleaned)
            # Filter out state names/abbreviations and empty results
            if cleaned and not is_state_name_or_abbreviation(cleaned):
                candidates.append((cleaned, conf))

        if candidates:
            # If two candidates, try joining them (for split plates like 'GHT' + '8670')
            if len(candidates) == 2:
                joined = candidates[0][0] + candidates[1][0]
                joined_conf = min(candidates[0][1], candidates[1][1])
                debug_msg = f"Keras-OCR joined candidate: '{joined}' (conf: {joined_conf})"
                print(debug_msg)
                if log_result:
                    log_result(debug_msg)
                cleaned = clean_license_plate(joined)
                debug_cleaned = f"Keras-OCR joined cleaned: '{cleaned}'"
                print(debug_cleaned)
                if log_result:
                    log_result(debug_cleaned)
                if cleaned:
                    return OCRResult(cleaned, joined_conf, 'keras-ocr')
            # Otherwise, select the candidate with the longest cleaned text
            best = max(candidates, key=lambda x: len(x[0]))
            return OCRResult(best[0], best[1], 'keras-ocr')

        warn_msg = "Keras-OCR: No valid license plate candidates found."
        print(warn_msg)
        if log_result:
            log_result(warn_msg)
        return OCRResult('', 0.0, 'keras-ocr')
    except Exception as e:
        error_msg = f"Keras-OCR error: {e}"
        print(error_msg)
        if log_result:
            log_result(error_msg)
        return OCRResult('', 0.0, 'keras-ocr')
