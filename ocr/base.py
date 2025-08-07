from models import OCRResult
from typing import Any

class BaseOCREngine:
    def recognize(self, image: Any) -> OCRResult:
        """Recognize text from image and return OCRResult."""
        raise NotImplementedError()
