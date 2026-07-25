#!/usr/bin/env python3
"""Offline unit tests for nr4a_paralogue_unique_residues (no network, no structures needed for the pure half)."""
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..")))

import nr4a_paralogue_unique_residues as pur  # noqa: E402


# A synthetic trio with a KNOWN answer, long enough that both aligners agree:
#   pos 5  : C in ref, C in both partners           -> conserved
#   pos 14 : C in ref, S / A in partners            -> unique cysteine vs both
#   pos 20 : K in ref, K in NR4A1, R in NR4A2       -> unique vs NR4A2 only
#   pos 26 : K in ref, E / E in partners            -> unique lysine vs both
_REF = "MAGTCLLGDWLAECMPQGAKLDPWTKLGVSEYA"
_P1 = "MAGTCLLGDWSAESMPQGAKLDPWTELGVSEYA"
_P2 = "MAGTCLLGDWAAEAMPQGARLDPWTELGVSEYA"
SEQS = {"NR4A3": _REF, "NR4A1": _P1, "NR4A2": _P2}


class TestClassify(unittest.TestCase):
    def setUp(self):
        self.cys = pur.classify_positions(SEQS, residue_types=("C",))
        self.lys = pur.classify_positions(SEQS, residue_types=("K",))
        self.by_num = {r["resnum"]: r for r in self.cys + self.lys}

    def test_finds_every_reference_residue_of_the_type(self):
        self.assertEqual([r["resnum"] for r in self.cys], [i for i, a in enumerate(_REF, 1) if a == "C"])
        self.assertEqual([r["resnum"] for r in self.lys], [i for i, a in enumerate(_REF, 1) if a == "K"])

    def test_conserved_cysteine_is_not_unique(self):
        self.assertFalse(self.by_num[5]["unique_vs_both"])
        self.assertEqual(self.by_num[5]["unique_vs"], [])

    def test_unique_cysteine_vs_both(self):
        r = self.by_num[14]
        self.assertTrue(r["unique_vs_both"])
        self.assertEqual(r["unique_vs"], ["NR4A1", "NR4A2"])
        self.assertEqual(r["partners"]["NR4A1"]["residue"], "S")
        self.assertEqual(r["partners"]["NR4A2"]["residue"], "A")

    def test_unique_lysine_vs_one_paralogue_only(self):
        r = self.by_num[20]
        self.assertFalse(r["unique_vs_both"])
        self.assertEqual(r["unique_vs"], ["NR4A2"])

    def test_unique_lysine_vs_both(self):
        r = self.by_num[26]
        self.assertTrue(r["unique_vs_both"])
        self.assertEqual(r["unique_vs"], ["NR4A1", "NR4A2"])

    def test_both_aligners_agree_on_this_easy_case(self):
        for r in self.cys + self.lys:
            self.assertTrue(r["alignment_robust"], f"aligners disagreed at {r['residue']}{r['resnum']}")
            self.assertEqual(r["unique_vs_both"], r["unique_vs_both_affine"])

    def test_alignment_robustness_flag_is_actually_wired(self):
        """A row must expose per-partner agreement, and the row flag must be their AND."""
        for r in self.cys + self.lys:
            agree = all(p["aligners_agree"] for p in r["partners"].values())
            self.assertEqual(r["alignment_robust"], agree)

    def test_reciprocal_direction_finds_partner_unique_residues(self):
        rec = pur.reciprocal_unique(SEQS)
        # NR4A2 has R at 20 where ref has K -> that is a ref-unique K, not a partner-unique K.
        # Build a case the other way: partner K where ref has T.
        seqs = dict(SEQS)
        seqs["NR4A1"] = _P1[:29] + "K" + _P1[30:]   # partner gains a K at 30 where ref has S
        rec = pur.reciprocal_unique(seqs)
        hits = [r for r in rec["NR4A1"] if r["resnum"] == 30]
        self.assertTrue(hits and hits[0]["residue"] == "K" and hits[0]["nr4a3_residue"] != "K")

    def test_in_lbd_flag_uses_the_modelled_construct_span(self):
        self.assertFalse(self.by_num[5]["in_lbd"])          # pos 5 < 373
        rows = pur.classify_positions({"NR4A3": "C" * 400, "NR4A1": "A" * 400, "NR4A2": "A" * 400},
                                      residue_types=("C",))
        self.assertTrue(rows[-1]["in_lbd"])                  # pos 400 is inside 373-626


class TestReach(unittest.TestCase):
    def test_reach_bands_are_monotone_and_cover_everything(self):
        self.assertEqual(pur._reach_class(1.0), "in_pocket")
        self.assertEqual(pur._reach_class(10.0), "exit_vector")
        self.assertEqual(pur._reach_class(15.0), "linker_borne")
        self.assertEqual(pur._reach_class(50.0), "distal")

    def test_bands_are_sorted(self):
        cuts = [c for c, _ in pur.REACH_BANDS]
        self.assertEqual(cuts, sorted(cuts))


class TestFusionLysines(unittest.TestCase):
    def test_counts_lysines_in_the_kept_ewsr1_segment_only(self):
        out = pur.fusion_lysine_scenarios("AAKAAKAAAK", {"keep6": 6, "keep10": 10})
        self.assertEqual(out["keep6"]["n_lysines"], 2)
        self.assertEqual(out["keep10"]["n_lysines"], 3)
        self.assertEqual(out["keep10"]["lysine_positions"], [3, 6, 10])


class TestGate(unittest.TestCase):
    def _row(self, num, exposed, reach):
        return {"resnum": num, "geometry": {"exposed": exposed, "reach_class": reach}}

    def _exposed(self, rows):
        return [r for r in rows if r["geometry"].get("exposed")]

    def test_both_axes_available(self):
        g = pur._gate([self._row(397, True, "exit_vector")], [self._row(518, True, None)], self._exposed)
        self.assertTrue(g["covalent_axis_available"])
        self.assertTrue(g["unique_lysine_axis_available"])
        self.assertIn("GO on BOTH", g["verdict"])

    def test_distal_cysteine_does_not_open_the_covalent_axis(self):
        g = pur._gate([self._row(397, True, "distal")], [self._row(518, True, None)], self._exposed)
        self.assertFalse(g["covalent_axis_available"])
        self.assertIn("PARTIAL", g["verdict"])

    def test_buried_cysteine_does_not_count(self):
        g = pur._gate([self._row(559, False, "exit_vector")], [], self._exposed)
        self.assertFalse(g["covalent_axis_available"])
        self.assertIn("NO categorical axis", g["verdict"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
