from typing import Callable, Optional
from dataclasses import dataclass
import numpy as np
from doctr.io import DocumentFile
from doctr.models import ocr_predictor

@dataclass
class OCRResult:
    text: str
    confidence: float
    source: str

def doctr_ocr(image, doctr_predictor, clean_license_plate: Callable[[str], str], log_result: Optional[Callable[[str], None]] = None) -> OCRResult:
    if not doctr_predictor:
        return OCRResult('', 0.0, 'doctr')
    try:
        # Doctr expects a numpy array
        doc = DocumentFile.from_images(np.array(image))
        result = doctr_predictor(doc)
        json_output = result.export()

        words = [word for page in json_output['pages'] for block in page['blocks'] for line in block['lines'] for word in line['words']]

        if not words:
            return OCRResult('', 0.0, 'doctr')

        # Find the word with the highest confidence
        best_word = max(words, key=lambda w: w['confidence'])
        text = best_word['value']
        conf = best_word['confidence']

        debug_msg = f"Doctr candidate: '{text}' (conf: {conf})"
        print(debug_msg)
        if log_result:
            log_result(debug_msg)

        cleaned = clean_license_plate(text)
        debug_cleaned = f"Doctr cleaned: '{cleaned}'"
        print(debug_cleaned)
        if log_result:
            log_result(debug_cleaned)

        if cleaned:
            return OCRResult(cleaned, conf, 'doctr')

        return OCRResult('', 0.0, 'doctr')
    except Exception as e:
        error_msg = f"Doctr error: {e}"
        print(error_msg)
        if log_result:
            log_result(error_msg)
        return OCRResult('', 0.0, 'doctr')
