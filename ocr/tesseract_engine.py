def tesseract_ocr(image, config=None, clean_license_plate=None, log_result=None):
    engine = TesseractEngine()
    return engine.recognize(image)
from models import OCRResult
import pytesseract

class TesseractEngine:
    def recognize(self, image):
        try:
            from utils.state_filters import is_state_name_or_abbreviation
            from utils.validation import clean_license_plate
            custom_config = r'--oem 3 --psm 8 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
            data = pytesseract.image_to_data(image, config=custom_config, output_type=pytesseract.Output.DICT)
            text_parts = []
            confidences = []
            for i in range(len(data['text'])):
                if int(data['conf'][i]) > 0:
                    text_parts.append(data['text'][i])
                    confidences.append(int(data['conf'][i]))
            text = ''.join(text_parts).strip()
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            cleaned = clean_license_plate(text)
            if cleaned and not is_state_name_or_abbreviation(cleaned):
                return OCRResult(cleaned, avg_confidence / 100, 'tesseract')
            else:
                return OCRResult('', 0, 'tesseract')
        except Exception:
            return OCRResult('', 0, 'tesseract')
