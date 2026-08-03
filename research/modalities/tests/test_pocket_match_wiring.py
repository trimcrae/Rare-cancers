#!/usr/bin/env python3
"""The guard behind the `POCKET_MATCH` fix (2026-08-03).

`pocket_tracking.match_mode()` defaults to LEGACY — the retired, outcome-selected site rule. A lane that
sets nothing therefore produces a manifest that looks complete and carries a number no reader can
attribute to a rule. That already happened on the single most load-bearing structure in the program: the
generation receptor's manifest recorded **0.667** under LEGACY where the harmonized rule scores the same
PDB at **0.259**, below D* (`r3-generation-frame-harmonized.json`).

These tests exist so the fix cannot rot. They assert:
  * the WIRING is real end to end, not just present in the workflow YAML (the entry script must forward it
    into the child process, which is exactly where a `env:` block alone would fail);
  * the RUNTIME guard refuses a silent legacy run and still permits a deliberate one;
  * the census of still-unwired lanes is pinned EXACTLY, so fixing one or gaining one both go red.
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import nr4a3_release_druggable as rd     # noqa: E402
import pocket_match_wiring as pmw        # noqa: E402
import pocket_tracking as pt             # noqa: E402


class TestTheDefaultIsStillTheHazard(unittest.TestCase):
    def test_match_mode_still_defaults_to_legacy(self):
        """If this ever flips, the whole guard is unnecessary — and pretending otherwise while it is
        still LEGACY is what let five lanes stay silent."""
        self.assertEqual(pt.match_mode({}), pt.LEGACY)
        self.assertEqual(pt.match_mode({"POCKET_MATCH": "harmonized"}), pt.HARMONIZED)


class TestRuntimeGuard(unittest.TestCase):
    def test_legacy_without_an_explicit_opt_in_is_refused(self):
        ok, msg = rd.check_site_rule(pt.LEGACY, "")
        self.assertFalse(ok)
        self.assertIn("RETIRED", msg)
        self.assertIn("ALLOW_LEGACY_POCKET_MATCH", msg)

    def test_legacy_stays_reachable_when_said_out_loud(self):
        """Reproducing the 2026-06-29 manifest is a legitimate thing to want; a guard that made it
        impossible would just get deleted."""
        ok, msg = rd.check_site_rule(pt.LEGACY, "1")
        self.assertTrue(ok)
        self.assertIn("RETIRED", msg)
        self.assertIn("do NOT use this number", msg)

    def test_harmonized_passes_and_says_it_is_score_independent(self):
        ok, msg = rd.check_site_rule(pt.HARMONIZED, "")
        self.assertTrue(ok)
        self.assertIn("score-independent", msg)


class TestWiringIsEndToEnd(unittest.TestCase):
    def test_the_step0_lane_is_wired_at_every_hop(self):
        """The workflow, the submitter and the SageMaker entry must ALL carry it. The bug this replaces
        would have survived a check that looked only at the workflow file."""
        st = pmw.lane_status("release-druggable-aws.yml", pmw.LANES["release-druggable-aws.yml"])
        self.assertEqual(st["missing_files"], [])
        self.assertTrue(st["workflow_sets_pocket_match"])
        self.assertTrue(st["chain_complete"], st["chain_forwards_pocket_match"])
        self.assertTrue(st["wired"])

    def test_every_required_lane_is_wired(self):
        c = pmw.census()
        for lane in pmw.WIRED_REQUIRED:
            self.assertIn(lane, c["wired"], f"{lane} lost its {pmw.MATCH_ENV} wiring")

    def test_no_lane_file_is_missing(self):
        """An absent reading is not a reading of absence: a renamed workflow must fail loudly rather than
        quietly drop out of the census."""
        for row in pmw.census()["rows"]:
            self.assertEqual(row["missing_files"], [], f"{row['lane']} references files that do not exist")


class TestTheOpenDefectIsPinnedNotHidden(unittest.TestCase):
    def test_the_unwired_set_is_exactly_the_recorded_one(self):
        """⛔ NOT an exemption list. Pinned EXACTLY so that fixing one of these, or a sixth appearing,
        both turn red and force a deliberate edit instead of a silent baseline bump."""
        self.assertEqual(tuple(pmw.census()["unwired"]), tuple(sorted(pmw.KNOWN_UNWIRED)))

    def test_every_lane_states_why_its_rule_matters(self):
        """A census row with no consequence attached is how a real defect reads as bookkeeping."""
        for row in pmw.census()["rows"]:
            self.assertTrue(row["why_it_matters"].strip())


class TestCensusIsPureAndReadable(unittest.TestCase):
    def test_census_is_computed_from_the_reader_not_remembered(self):
        fake = {"x.yml": {"driver": "d.py", "chain": ["c.py"], "why_it_matters": "w"}}
        c = pmw.census(fake, reader=lambda p: "POCKET_MATCH: harmonized")
        self.assertEqual(c["wired"], ["x.yml"])
        c2 = pmw.census(fake, reader=lambda p: "nothing here")
        self.assertEqual(c2["unwired"], ["x.yml"])

    def test_a_workflow_that_sets_it_but_a_chain_that_drops_it_is_UNWIRED(self):
        """The precise shape of the original bug's near-miss fix."""
        fake = {"x.yml": {"driver": "d.py", "chain": ["c.py"], "why_it_matters": "w"}}
        reader = lambda p: ("POCKET_MATCH: harmonized" if p.endswith("x.yml") else "no forwarding")  # noqa: E731
        self.assertEqual(pmw.census(fake, reader=reader)["unwired"], ["x.yml"])

    def test_format_names_every_unwired_lane(self):
        c = pmw.census()
        text = pmw.format_census(c)
        for lane in c["unwired"]:
            self.assertIn(lane, text)


if __name__ == "__main__":
    unittest.main(verbosity=2)
