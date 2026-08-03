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


class TestTheCvRgRestatement(unittest.TestCase):
    """`cv_rg_nm` restates a CV whose one home (`nr4a3_mdpocket._cv_rg_series`) is mdtraj-based and cannot
    read a PDB. A second definition of a selection criterion is a liability unless it is pinned to the
    first, so this recomputes the ENTIRE committed release_rep0 series from the committed frame PDBs and
    requires agreement with that lane's own recorded `cv_rg_nm`."""

    ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        "..", "..", "results", "nr4a3-pocket-reharmonize", "release_rep0")

    def test_it_reproduces_the_committed_rep0_series_frame_for_frame(self):
        import glob
        import json
        import re
        summ = os.path.join(self.ROOT, "pocket_analysis_summary.json")
        if not os.path.exists(summ):
            self.skipTest("committed reharmonize rep0 frames absent from this checkout")
        with open(summ) as fh:
            recorded = {s["frame"]: s["cv_rg_nm"]
                        for s in json.load(fh)["druggability_timeseries"]["series"]}
        lining, _, _ = sc.map_lining(list(range(1, 255)))
        n = 0
        for path in sorted(glob.glob(os.path.join(self.ROOT, "fp_*", "frame.pdb"))):
            idx = int(re.search(r"fp_(\d+)_", path).group(1))
            self.assertAlmostEqual(sc.cv_rg_nm(sc.ca_by_resseq(path), lining), recorded[idx], places=4,
                                   msg=f"rep0 frame {idx}: the two CV definitions disagree")
            n += 1
        self.assertEqual(n, 25)

    def test_none_when_the_lining_cannot_be_placed(self):
        self.assertIsNone(sc.cv_rg_nm({1: (0.0, 0.0, 0.0)}, [1, 2, 3]))

    def test_units_are_nanometres(self):
        """10 A of spread must read as ~1 nm, not 10. The repo has already paid for one nm/A mix
        (residue_map.py's docstring records it)."""
        ca = {1: (10.0, 0.0, 0.0), 2: (-10.0, 0.0, 0.0), 3: (0.0, 10.0, 0.0), 4: (0.0, -10.0, 0.0)}
        self.assertAlmostEqual(sc.cv_rg_nm(ca, [1, 2, 3, 4]), 1.0, places=4)


class TestSiteIdentityDescriptors(unittest.TestCase):
    """The (A) half of the site-choice question: WHAT each accepted cavity is.

    These are descriptive, and the tests exist to keep them descriptive — nothing here may become an
    acceptance criterion, because the matcher's thresholds were frozen 2026-07-11 and re-tuning them
    after seeing a verdict is the outcome-selection defect this audit is about."""

    def test_volume_parsing_is_per_pocket_and_tolerates_missing(self):
        text = ("Pocket 1 :\n\tScore : 0.3\n\tDruggability Score : 0.259\n\tVolume : 512.34\n"
                "Pocket 2 :\n\tDruggability Score : 0.667\n")
        vols = sc.parse_pocket_volumes(text)
        self.assertAlmostEqual(vols[1], 512.34)
        self.assertNotIn(2, vols)
        self.assertEqual(sc.parse_pocket_volumes(""), {})
        self.assertEqual(sc.parse_pocket_volumes(None), {})

    def test_volume_score_is_not_mistaken_for_volume(self):
        """MEASURED FAILURE, 2026-08-03: a substring test on 'Volume' returned fpocket's 0-10 `Volume
        Score` and the artifact printed two cavities at '4.909' and '4.833 Å³'. A cavity is hundreds of
        Å³; a number that cannot be a volume was one step from being quoted as one."""
        text = ("Pocket 1 :\n\tVolume Score : 4.909\n\tVolume : 512.34\n"
                "Pocket 2 :\n\tVolume : 301.5\n\tVolume Score : 4.833\n")
        vols = sc.parse_pocket_volumes(text)
        self.assertAlmostEqual(vols[1], 512.34)
        self.assertAlmostEqual(vols[2], 301.5)

    def test_labels_carry_uniprot_numbering_derived_from_lbd_first(self):
        """resSeq 34 in a structure renumbered from 373 is UniProt 406 — the first Pocket-5 lining
        residue. Typing the offset is what this asserts against."""
        labels = sc.label_residues([34, 162], {34: "LEU", 162: "PHE"})
        self.assertEqual(labels, ["LEU406", "PHE534"])

    def test_unknown_residue_is_labelled_not_dropped(self):
        self.assertEqual(sc.label_residues([34], {}), ["UNK406"])

    def test_contrast_reports_set_arithmetic_for_the_accepted_pair(self):
        pockets = [{"pocket": 1, "residues": [1, 2, 3, 4], "druggability": 0.259},
                   {"pocket": 2, "residues": [3, 4, 5, 6], "druggability": 0.667}]
        out = sc.site_choice_contrast(pockets, [1, 2, 3], {1: (0.0, 0.0, 0.0), 2: (3.0, 4.0, 0.0)})
        self.assertEqual(out["n_accepted"], 2)
        p = out["pairs"][0]
        self.assertEqual(p["n_shared"], 2)
        self.assertEqual(p["shared_residues"], [3, 4])
        self.assertEqual(p["only_in_first"], [1, 2])
        self.assertEqual(p["only_in_second"], [5, 6])
        self.assertEqual(p["centroid_separation_ang"], 5.0)
        self.assertEqual(p["reference_lining_in_first_only"], [1, 2])
        self.assertEqual(p["reference_lining_in_both"], [3])

    def test_relationship_labels_are_the_three_stated_cases(self):
        near = sc.site_choice_contrast(
            [{"pocket": 1, "residues": [1, 2, 3], "druggability": 0.1},
             {"pocket": 2, "residues": [1, 2, 3, 4], "druggability": 0.9}], [1], {})
        self.assertEqual(near["pairs"][0]["relationship"], "SAME_CAVITY_RESEGMENTED")
        mid = sc.site_choice_contrast(
            [{"pocket": 1, "residues": [1, 2, 3, 4, 5], "druggability": 0.1},
             {"pocket": 2, "residues": [5, 6, 7, 8, 9], "druggability": 0.9}], [1], {})
        self.assertEqual(mid["pairs"][0]["relationship"], "OVERLAPPING_SUBPOCKETS")
        far = sc.site_choice_contrast(
            [{"pocket": 1, "residues": [1, 2], "druggability": 0.1},
             {"pocket": 2, "residues": [8, 9], "druggability": 0.9}], [1], {})
        self.assertEqual(far["pairs"][0]["relationship"], "DISJOINT_CAVITIES")

    def test_contrast_of_a_single_accepted_cavity_has_no_pairs(self):
        out = sc.site_choice_contrast([{"pocket": 1, "residues": [1], "druggability": 0.1}], [1], {})
        self.assertEqual(out["n_accepted"], 1)
        self.assertEqual(out["pairs"], [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
