#!/usr/bin/env python3
"""Tests for the R3 frame-level generation-receptor dependency audit (Gate A).

The point of pinning these is that every verdict this pair returns is load-bearing on a SUBMISSION gate,
and three of the four are REFUSALS. A refusal that silently degrades into a pass is the failure mode the
paper's own sentence warns about — *"if the generation frame does not qualify, the generation receptor ...
is affected"* — so the boundary between "named and scored", "named but pre-harmonized", and "not
recoverable" is asserted rather than assumed.
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import r3_generation_frame_audit as aud   # noqa: E402
import r3_score_generation_frame as sc    # noqa: E402


def _manifest(mode=None, confirmed=0.667):
    m = {"selection_primary_receptor": "nr4a3-release-druggable.pdb",
         "docking_primary_receptor": "nr4a3-release-druggable.pdb",
         "receptors": [{"pdb": "nr4a3-release-druggable.pdb", "role": "primary", "rep": 0,
                        "frame": 95, "selection_rg": 0.7367, "selection_druggability": 0.692,
                        "confirmed_druggability": confirmed}]}
    if mode is not None:
        m["pocket_match"] = {"mode": mode}
    return m


class TestCoverage(unittest.TestCase):
    def test_the_committed_summary_does_not_cover_the_generation_receptor(self):
        """The real artifact, not a fixture. This is the audit's central factual claim."""
        import json
        p = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                         "nr4a3-pocket-reharmonize-summary.json")
        with open(p) as fh:
            summary = json.load(fh)
        cov = aud.reharmonize_covers_generation_frame(summary)
        self.assertFalse(cov["covered"])
        self.assertEqual(cov["missing_kind"], "release_druggable")
        # and it is not merely a granularity problem: no release_druggable row exists at any granularity
        self.assertNotIn("release_druggable", cov["rows"])

    def test_a_release_druggable_row_would_count_as_coverage(self):
        cov = aud.reharmonize_covers_generation_frame({"rows": [{"ensemble": "release_druggable"}]})
        self.assertTrue(cov["covered"])


class TestPickPrimary(unittest.TestCase):
    def test_follows_selection_primary_not_docking_primary(self):
        """A promoted alternate is NOT the frame the generator saw. Following the docking pointer would
        score a structure denovo_401 was never conditioned on."""
        m = _manifest()
        m["receptors"].append({"pdb": "nr4a3-release-druggable-alt1.pdb", "role": "alt1",
                               "rep": 1, "frame": 7, "confirmed_druggability": 0.9})
        m["docking_primary_receptor"] = "nr4a3-release-druggable-alt1.pdb"
        self.assertEqual(aud.pick_primary(m)["role"], "primary")

    def test_none_when_absent(self):
        self.assertIsNone(aud.pick_primary(None))
        self.assertIsNone(aud.pick_primary({"receptors": []}))


class TestClassify(unittest.TestCase):
    def test_no_manifest_is_a_named_refusal(self):
        v = aud.classify(None, None)
        self.assertEqual(v["verdict"], "FRAME_NOT_RECOVERABLE")
        self.assertTrue(v["unblocker"])

    def test_absent_pocket_match_is_a_refusal_not_a_pass(self):
        """THE REAL CASE. The committed manifest predates the harmonized tracker, so it has no
        pocket_match block. 0.667 >= D* must NOT be read as a pass."""
        m = _manifest(mode=None, confirmed=0.667)
        v = aud.classify(m, aud.pick_primary(m))
        self.assertEqual(v["verdict"], "FRAME_NAMED_UNSCORED")
        self.assertEqual(v["frame_id"]["rep"], 0)
        self.assertEqual(v["frame_id"]["frame"], 95)

    def test_legacy_mode_is_also_a_refusal(self):
        m = _manifest(mode="legacy", confirmed=0.9)
        self.assertEqual(aud.classify(m, aud.pick_primary(m))["verdict"], "FRAME_NAMED_UNSCORED")

    def test_harmonized_pass_and_fail(self):
        m = _manifest(mode="harmonized", confirmed=0.667)
        self.assertEqual(aud.classify(m, aud.pick_primary(m))["verdict"], "DISCHARGED_PASS")
        m = _manifest(mode="harmonized", confirmed=0.40)
        v = aud.classify(m, aud.pick_primary(m))
        self.assertEqual(v["verdict"], "DISCHARGED_FAIL")
        self.assertIn("generation receptor", v["reaches"])

    def test_harmonized_with_no_matched_cavity_fails(self):
        m = _manifest(mode="harmonized", confirmed=None)
        self.assertEqual(aud.classify(m, aud.pick_primary(m))["verdict"], "DISCHARGED_FAIL")


class TestNumberingMap(unittest.TestCase):
    def test_the_generation_receptors_own_numbering(self):
        """resseq_range [1, 254] is what the manifest records. UniProt 406..534 must map onto 34..162,
        and the label must SAY which branch fired — a silent wrong offset would report 'no matched
        cavity' for a numbering reason, indistinguishable from a real D* failure."""
        lining, span, label = sc.map_lining(list(range(1, 255)))
        self.assertEqual(label, "renumbered-from-373")
        self.assertEqual(lining, [34, 35, 38, 39, 40, 109, 112, 113, 159, 162])
        self.assertEqual((min(span), max(span)), (34, 162))

    def test_uniprot_numbered_structure_is_left_alone(self):
        lining, span, label = sc.map_lining(list(range(373, 627)))
        self.assertEqual(label, "resSeq-preserved")
        self.assertEqual(lining, sc.POCKET5_LINING)
        self.assertEqual((min(span), max(span)), (406, 534))

    def test_the_mapped_lining_agrees_with_the_manifests_own_box_residues(self):
        """Independent corroboration: nr4a3_release_druggable.py wrote box_residues in the SAME
        trajectory numbering, from the same LBD_FIRST. Six of the ten lining residues appear there, and
        if the offset were wrong none would."""
        box = {34, 108, 109, 112, 113, 152, 153, 156, 157, 159, 162, 166}
        lining, _, _ = sc.map_lining(list(range(1, 255)))
        self.assertTrue(box.intersection(lining) >= {34, 109, 112, 113, 159, 162})


class TestGateAScoreClassification(unittest.TestCase):
    def test_no_match_is_distinct_from_below_dstar(self):
        a = sc.classify_score(False, None)
        b = sc.classify_score(True, 0.40)
        self.assertEqual(a["verdict"], "GATE_A_FAIL_NO_MATCH")
        self.assertEqual(b["verdict"], "GATE_A_FAIL_BELOW_DSTAR")
        self.assertNotEqual(a["reason"], b["reason"])

    def test_pass_at_and_above_dstar(self):
        self.assertEqual(sc.classify_score(True, sc.D_STAR)["verdict"], "GATE_A_PASS")
        self.assertEqual(sc.classify_score(True, 0.99)["verdict"], "GATE_A_PASS")

    def test_both_failures_say_they_reach_the_generation_receptor(self):
        for v in (sc.classify_score(False, None), sc.classify_score(True, 0.1)):
            self.assertIn("generation receptor", v["reaches"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
