"""Paired synthetic expectations frozen before the historical-context repair."""
import unittest
from companion_v2 import classify_context

class HistoricalRepairTests(unittest.TestCase):
    def test_population_and_comparator_history_is_not_assessment_history(self):
        for text in (
            "Response assessed using RECIST1.1 in previously treated patients.",
            "Response assessed using RECIST 1.1 in previously treated patients.",
            "Previously treated patients have response assessed using RECIST 1.1.",
            "Response assessed using RECIST 1.1 against historical controls.",
            "Response assessed using RECIST 1.1 in formerly treated patients.",
        ):
            with self.subTest(text=text):
                result = classify_context({"description": text})
                self.assertEqual((result["status"], result["familyName"], result["criteriaVersion"]),
                                 ("assigned", "RECIST", "1.1"))
                self.assertFalse(any(m["historicalContext"] for m in result["mentions"]))

    def test_assessment_and_earlier_study_history_still_abstains(self):
        for text in (
            "Response was previously assessed using RECIST 1.1.",
            "Response was historically assessed using RECIST 1.0.",
            "Response was formerly evaluated using RECIST 1.0.",
            "Earlier studies using RECIST 1.0 assessed response.",
            "Prior studies assessed response using RECIST 1.0.",
            "Historical assessment using RECIST 1.0 is described.",
        ):
            with self.subTest(text=text):
                result = classify_context({"description": text})
                self.assertEqual(result["status"], "ambiguous")
                self.assertIsNone(result["familyName"])
                self.assertTrue(any(m["historicalContext"] for m in result["mentions"]))

if __name__ == "__main__":
    unittest.main()

