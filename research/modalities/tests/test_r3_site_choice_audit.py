#!/usr/bin/env python3
"""Tests for the R3 site-choice audit (2026-08-03).

This artifact answers two questions that decide whether the program's most load-bearing structure stands.
The tests pin the things that would be dangerous to get wrong quietly:

  * the selector is CALLED, not re-implemented — a re-implementation that drifted would report a
    "would-be receptor" nobody's code would actually choose;
  * "qualifies" means clears D* ON THE MAPPED SITE, never "has a druggable cavity somewhere";
  * an absent input renders as NOT MEASURED, never as a small consequence;
  * the identity cross-check can actually FAIL — a comparison that always says "identical" proves nothing.
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pocket_tracking as pt          # noqa: E402
import r3_site_choice_audit as A      # noqa: E402
import release_frame_select as rfs    # noqa: E402


def _rec(rep, frame, rg, drug):
    return {"rep": rep, "frame": frame, "rg": rg, "druggability": drug}


class TestQualifying(unittest.TestCase):
    def test_only_frames_at_or_above_d_star(self):
        recs = [_rec(0, 1, 0.737, 0.53), _rec(0, 2, 0.737, 0.5299), _rec(0, 3, 0.74, 0.9)]
        got = {r["frame"] for r in A.qualifying(recs)}
        self.assertEqual(got, {1, 3})

    def test_ranked_by_closeness_to_target_rg_then_druggability(self):
        recs = [_rec(0, 1, 0.800, 0.99), _rec(0, 2, 0.7371, 0.60), _rec(0, 3, 0.7371, 0.80)]
        order = [r["frame"] for r in A.qualifying(recs)]
        self.assertEqual(order, [3, 2, 1])

    def test_rg_offset_is_recorded_so_the_ranking_is_checkable(self):
        r = A.qualifying([_rec(0, 1, 0.7612, 0.9)])[0]
        self.assertAlmostEqual(r["rg_offset"], 0.0242, places=4)


class TestPerReplica(unittest.TestCase):
    def test_counts_are_derived_per_replica(self):
        recs = [_rec(0, 1, 0.7, 0.9), _rec(0, 2, 0.7, 0.1), _rec(2, 3, 0.7, 0.9)]
        rows = {r["rep"]: r for r in A.per_replica(recs)}
        self.assertEqual((rows[0]["n"], rows[0]["n_ge_dstar"]), (2, 1))
        self.assertEqual((rows[2]["n"], rows[2]["n_ge_dstar"]), (1, 1))


class TestSelectorIsCalledNotReimplemented(unittest.TestCase):
    def test_it_returns_what_release_frame_select_returns(self):
        recs = [_rec(0, 29, 0.7363, 0.598), _rec(0, 95, 0.7612, 0.259), _rec(0, 99, 0.7376, 0.621)]
        mine = A.selector_choice(recs)
        theirs = rfs.select_receptor_ensemble(recs, d_star=pt.D_STAR, target_rg=A.TARGET_RG, n_alt=3)
        self.assertEqual(mine["primary"]["frame"], theirs["primary"]["frame"])
        self.assertEqual(mine["n_druggable"], theirs["n_druggable"])

    def test_the_generation_frame_is_not_selectable_at_its_measured_rg(self):
        """The point of (B), stated as an assertion: at Rg 0.7612 and druggability 0.259 the frame fails
        the D* filter outright, so no ordering could return it."""
        recs = [_rec(0, 29, 0.7363, 0.598), _rec(0, 95, 0.7612, 0.259), _rec(0, 99, 0.7376, 0.621)]
        self.assertNotEqual(A.selector_choice(recs)["primary"]["frame"], 95)

    def test_an_empty_pool_returns_a_reason_not_a_crash(self):
        out = A.selector_choice([])
        self.assertIsNone(out["primary"])
        self.assertTrue(out["reason"])


class TestSeriesRecordsUseTheMatchedSite(unittest.TestCase):
    def test_rows_without_a_score_or_an_rg_are_dropped_not_defaulted(self):
        summ = {0: {"druggability_timeseries": {"series": [
            {"frame": 1, "orthosteric_druggability": 0.5, "cv_rg_nm": 0.73, "match": {"n_overlap": 8}},
            {"frame": 2, "orthosteric_druggability": None, "cv_rg_nm": 0.73},
            {"frame": 3, "orthosteric_druggability": 0.9, "cv_rg_nm": None},
        ]}}}
        recs = A.series_records(summ)
        self.assertEqual([r["frame"] for r in recs], [1])
        self.assertIsNotNone(recs[0]["match"])

    def test_the_committed_series_carries_a_match_block_on_every_scored_frame(self):
        """This is what makes 'clears on the mapped site' a true statement rather than a hopeful one."""
        recs = A.series_records(A.load_reharmonize_summaries())
        if not recs:
            self.skipTest("committed reharmonize summaries absent from this checkout")
        self.assertEqual(len(recs), 75)
        self.assertTrue(all(r["match"] and r["match"].get("n_overlap") is not None for r in recs))


class TestIdentityCrossCheckCanFail(unittest.TestCase):
    def test_a_real_difference_is_reported(self):
        a = {"n_candidate_pockets": 15, "n_accepted_by_gate": 2, "verdict": {"verdict": "X"}}
        b = {"n_candidate_pockets": 14, "n_accepted_by_gate": 2, "verdict": {"verdict": "X"}}
        out = A.identical_reading(a, b)
        self.assertTrue(out["comparable"])
        self.assertFalse(out["identical"])
        self.assertIn("n_candidate_pockets", out["differences"])

    def test_a_missing_side_is_not_identical_it_is_incomparable(self):
        out = A.identical_reading(None, {"n_candidate_pockets": 1})
        self.assertFalse(out["comparable"])
        self.assertNotIn("identical", out)


class TestUnmeasuredNeverRendersAsSmall(unittest.TestCase):
    def test_absent_dump_is_none_not_zero(self):
        self.assertIsNone(A.ensemble_consequence(None))
        self.assertIsNone(A.ensemble_consequence({"summary": []}))

    def test_present_dump_totals_both_rules(self):
        dump = {"d_star": 0.53, "match_params": {}, "summary": [
            {"species": "NR4A3", "ensemble": "release_rep0", "n_frames": 25, "n_matched": 25,
             "n_multi_accept": 9, "n_ge_dstar_frozen": 14, "n_ge_dstar_if_most_druggable": 19,
             "n_frames_where_the_two_rules_differ": 7},
            {"species": "NR4A1", "ensemble": "release_rep0", "n_frames": 25, "n_matched": 25,
             "n_multi_accept": 1, "n_ge_dstar_frozen": 1, "n_ge_dstar_if_most_druggable": 2,
             "n_frames_where_the_two_rules_differ": 1}]}
        out = A.ensemble_consequence(dump)
        self.assertEqual(out["totals"]["n_ge_dstar_frozen"], 14)      # NR4A3 only — species-scoped
        self.assertEqual(out["totals"]["n_ge_dstar_if_most_druggable"], 19)


class TestSelectivityConsequence(unittest.TestCase):
    """A rule choice reprices the paralogue contrast, and that must be visible before anyone chooses."""

    DUMP = {"summary": [
        {"species": "NR4A3", "ensemble": "release_rep0", "n_frames": 10,
         "n_ge_dstar_frozen": 6, "n_ge_dstar_if_most_druggable": 8},
        {"species": "NR4A3", "ensemble": "metad", "n_frames": 10,
         "n_ge_dstar_frozen": 10, "n_ge_dstar_if_most_druggable": 10},
        {"species": "NR4A1", "ensemble": "release_rep0", "n_frames": 10,
         "n_ge_dstar_frozen": 2, "n_ge_dstar_if_most_druggable": 5},
    ]}

    def test_the_biased_metad_subset_is_excluded_like_the_contrast_does(self):
        out = A.selectivity_under_each_rule(self.DUMP)
        rows = {r["species"]: r for r in out["rows"]}
        self.assertEqual(rows["NR4A3"]["n_frames"], 10)          # metad row not pooled in
        self.assertEqual(rows["NR4A3"]["n_ge_dstar_frozen"], 6)

    def test_margins_are_reported_under_both_rules_and_the_change_is_signed(self):
        m = A.selectivity_under_each_rule(self.DUMP)["nr4a3_margin_vs_paralogue"]["NR4A1"]
        self.assertAlmostEqual(m["margin_frozen"], 0.4, places=4)          # 0.6 - 0.2
        self.assertAlmostEqual(m["margin_if_most_druggable"], 0.3, places=4)  # 0.8 - 0.5
        self.assertAlmostEqual(m["margin_change"], -0.1, places=4)

    def test_it_refuses_to_report_one_rule_alone(self):
        for r in A.selectivity_under_each_rule(self.DUMP)["rows"]:
            self.assertIn("frac_frozen", r)
            self.assertIn("frac_if_most_druggable", r)

    def test_absent_dump_is_none(self):
        self.assertIsNone(A.selectivity_under_each_rule(None))

    def test_the_real_dump_reproduces_the_committed_contrast_frozen_counts(self):
        """⭑ The dump is only trustworthy if its FROZEN column reproduces C04, which was computed
        independently, in a different process, from the same frames."""
        dump = A.load_json(A.ACCEPTED)
        contrast = A.load_json(A.CONTRAST)
        if not dump or not contrast:
            self.skipTest("dump or contrast absent from this checkout")
        c = {(r["species"], r["ensemble"]): r["n_ge_dstar"] for r in contrast["rows"]}
        n = 0
        for r in dump["summary"]:
            key = (r["species"], r["ensemble"])
            if key in c:
                self.assertEqual(r["n_ge_dstar_frozen"], c[key], f"{key} disagrees with C04")
                n += 1
        self.assertEqual(n, 12)


class TestVerdictUnder(unittest.TestCase):
    def test_the_two_accepted_cavities_give_opposite_verdicts(self):
        self.assertEqual(A.verdict_under(0.259), "GATE_A_FAIL_BELOW_DSTAR")
        self.assertEqual(A.verdict_under(0.667), "GATE_A_PASS")

    def test_exactly_d_star_passes(self):
        self.assertEqual(A.verdict_under(pt.D_STAR), "GATE_A_PASS")


class TestTheRealArtifactHoldsTogether(unittest.TestCase):
    def test_build_reports_44_of_75_on_the_mapped_site(self):
        rec = A.build()
        b = rec["question_B_what_a_qualifying_frame_would_be"]
        if b["n_frames_scored"] == 0:
            self.skipTest("committed reharmonize summaries absent from this checkout")
        self.assertEqual(b["n_frames_scored"], 75)
        self.assertEqual(b["n_qualifying"], 44)

    def test_the_generation_frames_own_row_is_the_failing_one(self):
        rec = A.build()
        row = rec["question_B_what_a_qualifying_frame_would_be"]["generation_frame_row"]
        if row is None:
            self.skipTest("committed reharmonize summaries absent from this checkout")
        self.assertLess(row["druggability"], pt.D_STAR)


if __name__ == "__main__":
    unittest.main(verbosity=2)
