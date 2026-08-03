#!/usr/bin/env python3
"""Tests for the accepted-candidate dump (2026-08-03).

The artifact exists so that "which accepted cavity is the site?" becomes arithmetic on a committed file
instead of another fpocket run. That is only safe if two things hold, and both are asserted here:

  1. `frozen_winner` reproduces `pocket_tracking.match_pocket`'s ordering EXACTLY. If it drifts, every
     downstream reading of the artifact silently describes a rule nobody adopted.
  2. The reference site this module builds is the SAME site `paralogue_pocket_contrast` builds. A dump of
     "accepted cavities" against a different reference is not a sensitivity, it is a second experiment.
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import paralogue_pocket_contrast as PPC       # noqa: E402
import pocket_accepted_candidates as P        # noqa: E402
import pocket_tracking as pt                  # noqa: E402


def _rec(pocket, drug, jac, frac, cdist, n=10):
    return {"pocket": pocket, "druggability": drug, "jaccard": jac, "frac_recovered": frac,
            "centroid_dist_ang": cdist, "n_overlap": int(round(frac * 10)), "n_lining_residues": n}


class TestFrozenWinnerMatchesTheMatcher(unittest.TestCase):
    def _agree(self, cands, ref_lining, ca):
        hit = pt.match_pocket(cands, {"lining_residues": ref_lining, "centroid": (0.0, 0.0, 0.0)},
                              ca_by_resnum=ca, **pt.match_params())
        accepted = []
        for c in cands:
            m = pt.match_metrics(c["residues"], ref_lining)
            cen = pt.pocket_centroid(c["residues"], ca)
            cd = None if cen is None else round(sum(v * v for v in cen) ** 0.5, 3)
            if pt.accept_candidate(m, cd, **pt.match_params()):
                accepted.append({"pocket": c["pocket_number"], "druggability": c["druggability"],
                                 "jaccard": round(m["jaccard"], 4),
                                 "frac_recovered": round(m["frac_recovered"], 4),
                                 "centroid_dist_ang": cd, "n_overlap": m["n_overlap"],
                                 "n_lining_residues": len(c["residues"])})
        mine = P.frozen_winner(accepted)
        self.assertEqual(None if hit is None else hit["pocket_number"],
                         None if mine is None else mine["pocket"])

    def test_agrees_on_the_generation_frame_shape(self):
        """The real shape: a better-MATCHING low-druggability cavity against a worse-matching high one.
        This is precisely the case the rule decides and the one a re-implementation would get wrong."""
        ca = {i: (float(i), 0.0, 0.0) for i in range(1, 21)}
        cands = [{"pocket_number": 1, "residues": [1, 2, 3, 4, 5, 6, 7, 8], "druggability": 0.259},
                 {"pocket_number": 2, "residues": [5, 6, 7, 8, 9, 10], "druggability": 0.667}]
        self._agree(cands, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10], ca)

    def test_agrees_when_nothing_is_accepted(self):
        ca = {i: (float(i) * 40.0, 0.0, 0.0) for i in range(1, 21)}
        cands = [{"pocket_number": 7, "residues": [19, 20], "druggability": 0.9}]
        self._agree(cands, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10], ca)

    def test_agrees_on_a_single_accepted_cavity(self):
        ca = {i: (float(i) * 0.1, 0.0, 0.0) for i in range(1, 21)}
        cands = [{"pocket_number": 3, "residues": [1, 2, 3, 4, 5], "druggability": 0.4}]
        self._agree(cands, [1, 2, 3, 4, 5], ca)


class TestMostDruggableIsLabelledNotUsed(unittest.TestCase):
    def test_it_is_a_different_answer_from_the_frozen_one_on_the_generation_frame(self):
        acc = [_rec(1, 0.259, 0.6154, 0.8, 3.478), _rec(2, 0.667, 0.375, 0.6, 7.562)]
        self.assertEqual(P.frozen_winner(acc)["pocket"], 1)
        self.assertEqual(P.most_druggable(acc)["pocket"], 2)

    def test_both_are_none_on_an_empty_accepted_list(self):
        self.assertIsNone(P.frozen_winner([]))
        self.assertIsNone(P.most_druggable([]))


class TestSummaryCountsBothRulesSideBySide(unittest.TestCase):
    def test_counts_and_the_difference_column(self):
        frames = [
            {"species": "NR4A3", "ensemble": "release_rep0",
             "accepted": [_rec(1, 0.259, 0.6154, 0.8, 3.478), _rec(2, 0.667, 0.375, 0.6, 7.562)]},
            {"species": "NR4A3", "ensemble": "release_rep0",
             "accepted": [_rec(1, 0.90, 0.6, 0.8, 2.0)]},
            {"species": "NR4A3", "ensemble": "release_rep0", "accepted": []},
        ]
        row = P.summarise(frames)[0]
        self.assertEqual(row["n_frames"], 3)
        self.assertEqual(row["n_matched"], 2)
        self.assertEqual(row["n_multi_accept"], 1)
        self.assertEqual(row["n_ge_dstar_frozen"], 1)              # only the 0.90 frame
        self.assertEqual(row["n_ge_dstar_if_most_druggable"], 2)   # the 0.667 frame joins
        self.assertEqual(row["n_frames_where_the_two_rules_differ"], 1)

    def test_an_unmatched_frame_is_not_a_failed_frame_in_either_column(self):
        row = P.summarise([{"species": "X", "ensemble": "e", "accepted": []}])[0]
        self.assertEqual(row["n_matched"], 0)
        self.assertEqual(row["n_ge_dstar_frozen"], 0)
        self.assertEqual(row["n_ge_dstar_if_most_druggable"], 0)


class TestTheReferenceSiteIsTheSameOne(unittest.TestCase):
    def test_the_three_sources_are_the_contrast_modules_own_constants(self):
        for attr in ("SEQ_CACHE", "STATIC_MODEL", "UNIQUE_JSON"):
            self.assertTrue(hasattr(PPC.PD, attr), f"paralogue_pocket_contrast.PD lost {attr}")
        self.assertTrue(hasattr(PPC.B, "UNIPROT_OFFSET"))

    def test_the_mapped_lining_is_the_prespecified_pocket5_set(self):
        """10 residues, and the SAME ones the R3 Gate-A score mapped onto the generation receptor."""
        _seqs, _ref, pocket_local = P.reference_context()
        self.assertEqual(sorted(pocket_local), [34, 35, 38, 39, 40, 109, 112, 113, 159, 162])
        self.assertEqual(len(pocket_local), len(pt.POCKET5_LINING))

    def test_frame_walk_is_the_contrasts_own(self):
        self.assertEqual(len(PPC.frame_paths("NR4A3", "release_rep0")), 25)


if __name__ == "__main__":
    unittest.main(verbosity=2)
