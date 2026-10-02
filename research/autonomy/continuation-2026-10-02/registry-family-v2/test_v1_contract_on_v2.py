"""Synthetic conformance examples; no registry downloads or source-specific IDs."""
import copy
import unittest
from companion_v2 import accompany, classify_context, lexical_role


def source(labels=("CR", "PR", "SD", "PD")):
    return {"measurements": [
        {"categoryIndex": i, "measurementIndex": 0,
         "categoryLiteral": {"title": label, "note": "retain me"},
         "measurementLiteral": {"groupId": "OG000", "value": str(i+1), "spread": "literal"}}
        for i, label in enumerate(labels)],
        "denominators": {"selectedParticipantEntry": None, "outcomeEntries": [{"countLiteral": {"value": "19"}}]},
        "normalizedIntegerCells": {"CR": 1, "PR": 2, "SD": 3, "PD": 4},
        "normalizationStatus": "four-exact-integer-cells"}


def run_case(outcome, labels=("CR", "PR", "SD", "PD")):
    return accompany(["SYNTHETIC", "outcome-hash", 0, "OG000"], source(labels), outcome,
                     [{"source": "synthetic", "pointer": "/studies/0/outcomes/0/classes/0"}])


class Tests(unittest.TestCase):
    def test_absent_criteria_not_recist_by_default(self):
        r = run_case({"title": "Best overall response"})
        self.assertEqual(r["status"], "unknown")
        self.assertIsNone(r["withinFamilyFourCells"])
        self.assertIsNotNone(r["acceptedRowUnchanged"]["normalizedIntegerCells"])

    def test_suffix_only_does_not_identify_irecist(self):
        r = run_case({"title": "Best response"}, ("iCR", "iPR", "iSD", "iPD"))
        self.assertEqual(r["family"]["evidenceStatus"], "label-only-no-family-inference")
        self.assertIsNone(r["family"]["familyName"])

    def test_explicit_versionless_criteria_not_invented(self):
        f = classify_context({"description": "Response assessed using irRECIST."})
        self.assertEqual(f["status"], "assigned")
        self.assertEqual(f["familyName"], "irRECIST")
        self.assertIsNone(f["criteriaVersion"])

    def test_explicit_version_and_version_conflict(self):
        f = classify_context({"title": "BOR per RECIST v1.1"})
        self.assertEqual(f["criteriaVersion"], "1.1")
        f = classify_context({"title": "BOR per RECIST 1.1", "description": "Assessed using RECIST 1.0."})
        self.assertEqual(f["status"], "ambiguous")

    def test_conflicting_families_remain_unassigned(self):
        r = run_case({"title": "BOR per irRC", "description": "Response assessed using RECIST 1.1."})
        self.assertEqual(r["status"], "ambiguous")
        self.assertIsNone(r["family"]["familyName"])
        self.assertIsNone(r["withinFamilyFourCells"])

    def test_unprefixed_labels_with_modified_irrc(self):
        r = run_case({"title": "Best response", "description": "Based on investigator assessment using modified irRC. Responses require confirmation."})
        self.assertEqual(r["family"]["familyName"], "modified irRC")
        self.assertEqual(r["withinFamilyFourCells"], {"CR": 1, "PR": 2, "SD": 3, "PD": 4})
        self.assertIn("confirmation", r["contextLiteral"]["description"])

    def test_longest_family_name_and_source_evidence_offsets(self):
        outcome = {"title": "Best response using modified irRC-RECIST"}
        r = run_case(outcome, ("Complete response (iCR)", "Partial response (iPR)", "Stable disease (iSD)", "Progressive disease (iPD)"))
        self.assertEqual(r["family"]["familyName"], "modified irRC-RECIST")
        self.assertEqual(len(r["family"]["mentions"]), 1)
        m = r["family"]["mentions"][0]
        self.assertEqual(outcome[m["field"]][m["start"]:m["end"]], m["literal"])
        self.assertIsNotNone(r["withinFamilyFourCells"])

    def test_unconfirmed_confirmed_progression_not_collapsed(self):
        r = run_case({"title": "Best response by iRECIST"}, ("iCR", "iPR", "iSD", "iUPD", "iCPD"))
        self.assertEqual(r["separateProgressionStates"], ["CPD", "UPD"])
        self.assertIsNone(r["withinFamilyFourCells"])
        self.assertEqual([c["familyRole"] for c in r["categoryAssignments"]][-2:], ["UPD", "CPD"])
        self.assertEqual(lexical_role("Progressive disease (iPD)")["role"], "PD")

    def test_qualified_complete_response_not_erased(self):
        self.assertIsNone(lexical_role("Complete response unconfirmed"))
        self.assertIsNone(lexical_role("Complete response (iPR)"))

    def test_duplicate_aliases_stay_ambiguous(self):
        r = run_case({"title": "BOR per irRC"}, ("CR", "Complete response", "PR", "SD", "PD"))
        self.assertEqual(r["status"], "ambiguous")
        self.assertEqual(r["duplicateRoles"], ["CR"])
        self.assertIsNone(r["withinFamilyFourCells"])

    def test_immune_label_and_ordinary_context_conflict(self):
        r = run_case({"title": "BOR per RECIST 1.1"}, ("iCR", "iPR", "iSD", "iPD"))
        self.assertEqual(r["status"], "ambiguous")
        self.assertEqual(len(r["labelContextMismatchCategoryIndices"]), 4)

    def test_negated_and_bare_citation_not_positive_context(self):
        self.assertEqual(classify_context({"title": "BOR not using RECIST"})["status"], "ambiguous")
        self.assertEqual(classify_context({"description": "RECIST was not used to assess response."})["status"], "ambiguous")
        self.assertEqual(classify_context({"description": "RECIST is discussed in the bibliography."})["status"], "unknown")

    def test_source_literals_denominators_and_input_unchanged(self):
        s = source(); before = copy.deepcopy(s)
        r = accompany(["SYNTHETIC", "h", 0, "OG000"], s, {"title": "BOR per irRC"}, [])
        self.assertEqual(s, before)
        self.assertEqual(r["acceptedRowUnchanged"], before)
        self.assertEqual(r["categoryAssignments"][0]["measurementLiteral"], before["measurements"][0]["measurementLiteral"])
        self.assertFalse(r["family"]["poolingAllowed"])

    def test_missing_or_fractional_cell_never_imputed(self):
        s = source(); s["measurements"][0]["measurementLiteral"]["value"] = "1.5"
        r = accompany(["SYNTHETIC", "h", 0, "OG000"], s, {"title": "BOR per irRC"}, [])
        self.assertIsNone(r["withinFamilyFourCells"])


if __name__ == "__main__":
    unittest.main()

