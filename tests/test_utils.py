import unittest
import numpy as np
from utils.image_processing import preprocess_image
from utils.validation import clean_license_plate, get_consensus_result
from models import OCRResult

class TestUtils(unittest.TestCase):
    def test_preprocess_image(self):
        # Create a dummy image (white rectangle)
        img = np.ones((30, 100, 3), dtype=np.uint8) * 255
        processed = preprocess_image(img)
        self.assertIsNotNone(processed)
        self.assertEqual(processed.shape[0], 50)  # Should be resized to height 50

    def test_clean_license_plate(self):
        self.assertEqual(clean_license_plate('abc-123'), 'ABC123')
        self.assertEqual(clean_license_plate('A B C 1 2 3'), 'ABC123')
        self.assertEqual(clean_license_plate('!@#'), '')
        self.assertEqual(clean_license_plate('AB'), '')  # Too short
        self.assertEqual(clean_license_plate('ABCDEFGHIJK'), '')  # Too long

    def test_get_consensus_result(self):
        results = [
            OCRResult('ABC123', 0.9, 'tesseract'),
            OCRResult('ABC123', 0.8, 'easyocr'),
            OCRResult('XYZ999', 0.7, 'paddleocr'),
        ]
        text, conf, alert = get_consensus_result(results, 3, 0.75, 0.6)
        self.assertEqual(text, 'ABC123')
        self.assertFalse(alert)
        results = [
            OCRResult('ABC123', 0.5, 'tesseract'),
            OCRResult('XYZ999', 0.5, 'easyocr'),
            OCRResult('XYZ999', 0.5, 'paddleocr'),
        ]
        text, conf, alert = get_consensus_result(results, 3, 0.75, 0.6)
        self.assertTrue(alert)

if __name__ == '__main__':
    unittest.main()
