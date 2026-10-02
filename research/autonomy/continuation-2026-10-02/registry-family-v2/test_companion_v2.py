"""Frozen synthetic behavior contract; no trial texts or IDs."""
import copy
import unittest
import companion_v2 as v2

class RepairTests(unittest.TestCase):
    def check(self, text, status, family=None, version=None, field="description"):
        outcome = {field: text}
        before = copy.deepcopy(outcome)
        r = v2.classify_context(outcome)
        self.assertEqual((r["status"], r["familyName"], r["criteriaVersion"]),
                         (status, family, version), text)
        self.assertEqual(outcome, before)
        self.assertFalse(r["poolingAllowed"])
        for m in r["mentions"]:
            self.assertEqual(text[m["start"]:m["end"]], m["literal"])
        return r

    def test_pronouns(self):
        for pronoun in ("who", "Who", "WHO"):
            self.check(f"Patients {pronoun} responded were assessed using RECIST 1.1.",
                       "assigned", "RECIST", "1.1")
        self.check("Who was assessed?", "unknown", field="title")

    def test_who_criteria(self):
        self.check("Response assessed using WHO criteria.", "assigned", "WHO")
        self.check("Response assessed using World Health Organization criteria.", "assigned", "WHO")
        self.check("WHO response criteria", "assigned", "WHO", field="title")
        self.check("Response assessed using who criteria.", "unknown")
        self.check("WHO endorsed the assessment.", "unknown")
        self.check("Response assessed using WHO criteria and RECIST 1.1.", "ambiguous")

    def test_negation_history(self):
        for text in ("Response not assessed using WHO criteria.",
                     "Response assessed using RECIST rather than WHO criteria.",
                     "RECIST was not used to assess response.",
                     "Response was historically assessed using RECIST 1.0.",
                     "Previously assessed using WHO criteria; now assessed using RECIST 1.1."):
            self.check(text, "ambiguous")
        self.check("Historical RECIST bibliography.", "unknown")
        self.check("WHO criteria are discussed in a bibliography.", "unknown")

    def test_full_names_and_iwcll(self):
        for text in ("Response assessed using Response Evaluation Criteria in Solid Tumors 1.1.",
                     "Response assessed using Response Evaluation Criteria in Solid Tumor (RECIST) v1.1.",
                     "Response Evaluation Criteria in Solid Tumours: assessed version 1.1"):
            if "assessed version" in text:
                self.check(text, "assigned", "RECIST", None)
            else:
                self.check(text, "assigned", "RECIST", "1.1")
        self.check("Response assessed using iwCLL2018.", "assigned", "iwCLL", "2018")
        self.check("Response assessed using iwCLL criteria 2018.", "assigned", "iwCLL", "2018")
        self.check("iwCLL is cited in background.", "unknown")

    def test_version_syntax_and_conflicts(self):
        for suffix in (" (version 1.1)", ") Version 1.1", " response criteria v1.1",
                       " criteria (1.1)", " v.1.1"):
            self.check("Response assessed using RECIST" + suffix + ".", "assigned", "RECIST", "1.1")
        self.check("Response assessed using Lugano response criteria (2014).", "assigned", "Lugano", "2014")
        self.check("Response assessed using RECIST at 12 months.", "assigned", "RECIST")
        self.check("Response assessed using RECIST 1.1 and RECIST 1.0.", "ambiguous")
        self.check("Response assessed using RECIST; 1.1 months follow-up.", "assigned", "RECIST")
        self.check("Response assessed using iRECIST and RECIST.", "ambiguous")

    def test_literal_and_role_scope(self):
        source = {"measurements": [{"categoryIndex": 0, "measurementIndex": 0,
                  "categoryLiteral": {"title": "not a response label"},
                  "measurementLiteral": {"value": "3.0", "extra": None}}],
                  "classTitle": "CR", "denominators": {"raw": "17"},
                  "normalizedIntegerCells": None}
        before = copy.deepcopy(source)
        outcome = {"title": "Response using RECIST criteria (1.1)", "timeFrame": "9 weeks"}
        result = v2.accompany(["SYNTHETIC", "h", 0, "g"], source, outcome, [])
        self.assertEqual(source, before)
        self.assertEqual(result["acceptedRowUnchanged"], before)
        self.assertEqual(result["categoryAssignments"][0]["measurementLiteral"], before["measurements"][0]["measurementLiteral"])
        self.assertIsNone(result["categoryAssignments"][0]["familyRole"])
        self.assertIsNone(result["withinFamilyFourCells"])
        self.assertEqual(result["contextLiteral"]["timeFrame"], "9 weeks")

if __name__ == "__main__":
    unittest.main()

