from models import OCRResult

class PaddleOCREngine:
    def recognize(self, image):
        try:
            from paddleocr import PaddleOCR
            from utils.state_filters import is_state_name_or_abbreviation
            from utils.validation import clean_license_plate
            ocr = PaddleOCR(use_angle_cls=True, lang='en', show_log=False)
            results = ocr.ocr(image, cls=True)
            if results and results[0]:
                best_result = max(results[0], key=lambda x: x[1][1])
                text = best_result[1][0].upper().replace(' ', '')
                confidence = best_result[1][1]
                cleaned = clean_license_plate(text)
                if cleaned and not is_state_name_or_abbreviation(cleaned):
                    return OCRResult(cleaned, confidence, 'paddleocr')
                else:
                    return OCRResult('', 0, 'paddleocr')
            else:
                return OCRResult('', 0, 'paddleocr')
        except ImportError:
            return OCRResult('', 0, 'paddleocr')
        except Exception:
            return OCRResult('', 0, 'paddleocr')

# Function wrapper for compatibility with main app
def paddleocr_ocr(image, reader, clean_func, _=None):
    engine = PaddleOCREngine()
    return engine.recognize(image)
