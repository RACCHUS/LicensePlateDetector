from dataclasses import dataclass

@dataclass
class OCRResult:
    text: str
    confidence: float
    source: str
