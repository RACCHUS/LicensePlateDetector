import unittest
import numpy as np
from license_plate_recognizer import LicensePlateRecognizer, OCRResult

class TestLicensePlateRecognizer(unittest.TestCase):

    def setUp(self):
        self.recognizer = LicensePlateRecognizer()

    def test_clean_license_plate(self):
        self.assertEqual(self.recognizer.clean_license_plate("Abc-123"), "ABC123")
        self.assertEqual(self.recognizer.clean_license_plate("XYZ 789"), "XYZ789")
        self.assertEqual(self.recognizer.clean_license_plate("12"), "")
        self.assertEqual(self.recognizer.clean_license_plate("12345678901"), "")
        self.assertEqual(self.recognizer.clean_license_plate(""), "")

    def test_get_consensus_result(self):
        # Test case 1: Strong consensus
        results1 = [
            OCRResult(text="ABC123", confidence=0.9, source='tesseract'),
            OCRResult(text="ABC123", confidence=0.8, source='easyocr'),
            OCRResult(text="ABC123", confidence=0.85, source='paddleocr')
        ]
        text, confidence, alert_flag = self.recognizer.get_consensus_result(results1)
        self.assertEqual(text, "ABC123")
        self.assertAlmostEqual(confidence, 0.85)
        self.assertFalse(alert_flag)

        # Test case 2: No consensus
        results2 = [
            OCRResult(text="ABC123", confidence=0.9, source='tesseract'),
            OCRResult(text="XYZ789", confidence=0.8, source='easyocr'),
            OCRResult(text="DEF456", confidence=0.85, source='paddleocr')
        ]
        text, confidence, alert_flag = self.recognizer.get_consensus_result(results2)
        self.assertTrue(alert_flag)

        # Test case 3: Low confidence
        results3 = [
            OCRResult(text="ABC123", confidence=0.4, source='tesseract'),
            OCRResult(text="ABC123", confidence=0.5, source='easyocr'),
            OCRResult(text="ABC123", confidence=0.3, source='paddleocr')
        ]
        text, confidence, alert_flag = self.recognizer.get_consensus_result(results3)
        self.assertTrue(alert_flag)

        # Test case 4: Partial consensus
        results4 = [
            OCRResult(text="ABC123", confidence=0.9, source='tesseract'),
            OCRResult(text="ABC123", confidence=0.8, source='easyocr'),
            OCRResult(text="XYZ789", confidence=0.85, source='paddleocr')
        ]
        text, confidence, alert_flag = self.recognizer.get_consensus_result(results4)
        self.assertTrue(alert_flag)
        self.assertEqual(text, "ABC123")

if __name__ == '__main__':
    unittest.main()
