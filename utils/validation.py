import re
from models import OCRResult
from typing import List, Tuple

def clean_license_plate(text: str) -> str:
    """Clean and validate license plate text"""
    cleaned = re.sub(r'[^A-Z0-9]', '', text.upper())
    if 3 <= len(cleaned) <= 10:
        return cleaned
    return ''

def get_consensus_result(results: List[OCRResult], total_engines: int, agreement_threshold: float, confidence_threshold: float) -> Tuple[str, float, bool]:
    """Get consensus from multiple OCR results"""
    valid_results = [r for r in results if r.text and r.confidence > 0.1]
    if not valid_results:
        return '', 0, True
    cleaned_results = []
    for result in valid_results:
        cleaned = clean_license_plate(result.text)
        if cleaned:
            cleaned_results.append(OCRResult(cleaned, result.confidence, result.source))
    if not cleaned_results:
        return '', 0, True
    text_groups = {}
    for result in cleaned_results:
        if result.text not in text_groups:
            text_groups[result.text] = []
        text_groups[result.text].append(result)
    for text, group in text_groups.items():
        agreement_ratio = len(group) / total_engines
        avg_confidence = sum(r.confidence for r in group) / len(group)
        if agreement_ratio >= agreement_threshold and avg_confidence >= confidence_threshold:
            return text, avg_confidence, False
    if text_groups:
        best_group = max(text_groups.values(), key=len)
        best_text = best_group[0].text
        best_confidence = sum(r.confidence for r in best_group) / len(best_group)
        return best_text, best_confidence, True
    return '', 0, True
