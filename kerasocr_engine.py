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
        # Keras-OCR expects a list of numpy arrays
        images = [np.array(image)]
        prediction_groups = kerasocr_pipeline.recognize(images)

        # We only sent one image, so we only care about the first group
        if not prediction_groups:
            return OCRResult('', 0.0, 'keras-ocr')

        predictions = prediction_groups[0]

        if not predictions:
            return OCRResult('', 0.0, 'keras-ocr')

        # Keras-OCR does not provide confidence scores, so we'll have to use a placeholder
        # We'll take the first recognized text
        text = predictions[0][0]
        conf = 0.9 # Placeholder confidence

        debug_msg = f"Keras-OCR candidate: '{text}' (conf: {conf})"
        print(debug_msg)
        if log_result:
            log_result(debug_msg)

        cleaned = clean_license_plate(text)
        debug_cleaned = f"Keras-OCR cleaned: '{cleaned}'"
        print(debug_cleaned)
        if log_result:
            log_result(debug_cleaned)

        if cleaned:
            return OCRResult(cleaned, conf, 'keras-ocr')

        return OCRResult('', 0.0, 'keras-ocr')
    except Exception as e:
        error_msg = f"Keras-OCR error: {e}"
        print(error_msg)
        if log_result:
            log_result(error_msg)
        return OCRResult('', 0.0, 'keras-ocr')
