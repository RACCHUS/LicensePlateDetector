def easyocr_ocr(image, reader=None, clean_license_plate=None, log_result=None):
    engine = EasyOCREngine()
    return engine.recognize(image, reader)
from models import OCRResult

class EasyOCREngine:
    def recognize(self, image, reader=None):
        try:
            import easyocr
            from utils.state_filters import is_state_name_or_abbreviation
            from utils.validation import clean_license_plate
            if reader is None:
                reader = easyocr.Reader(['en'])
            results = reader.readtext(image)
            if results:
                best_result = max(results, key=lambda x: tuple(x)[2] if len(x) > 2 else 0)
                _, text, confidence = best_result
                text = text.upper().replace(' ', '')
                cleaned = clean_license_plate(text)
                if cleaned and not is_state_name_or_abbreviation(cleaned):
                    return OCRResult(cleaned, float(confidence), 'easyocr')
                else:
                    return OCRResult('', 0, 'easyocr')
            else:
                return OCRResult('', 0, 'easyocr')
        except ImportError:
            return OCRResult('', 0, 'easyocr')
        except Exception:
            return OCRResult('', 0, 'easyocr')
