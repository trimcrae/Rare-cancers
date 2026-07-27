"""THE THREE ANCHORS ARE DERIVED FROM THEIR OWN BLOCKS, AND THEY DO NOT MOVE.

WHY THIS FILE EXISTS. `vast_cost_model.MEASURED_NS_PER_DAY_84K` anchors every `$/ns` in the repo, the ladder
basis, the drift line, the fan-out gate and the relaunch gate. Until now its three numbers were TYPED, with
their per-block evidence living only in a comment. CLAUDE.md rule 1.1 says a total is DERIVED, never typed —
so `throughput-bench-provenance.json` carries the blocks and this file recomputes the means from them.

Two independent things are pinned, and they fail for different reasons:
  1. the constants equal the mean of their recorded blocks (evidence and table agree);
  2. the constants and `REFERENCE_NS_PER_H` are BIT-IDENTICAL to the values every downstream figure was
     computed against (nobody "improves" an anchor without a deliberate, appendixed correction).
"""
import json
import os
import sys
import unittest

_HERE = os.path.dirname(os.path.abspath(__file__))
_MOD = os.path.abspath(os.path.join(_HERE, ".."))
sys.path.insert(0, _MOD)

import gpu_md_bench as bench  # noqa: E402
import vast_bench_sweep as sweep  # noqa: E402
import vast_cost_model as vcm  # noqa: E402

PROV = json.load(open(os.path.join(_MOD, "throughput-bench-provenance.json")))

# The values every $/ns, every ladder figure and every drift ratio in the repo was computed against.
# Changing one means an appendix line AND research/manuscripts/pinned-figures.json in the SAME commit.
PINNED = {"RTX4090": 755.36, "RTX4080": 703.51, "RTX3090": 359.36}
PINNED_REFERENCE_NS_PER_H = 755.36 / 24.0


class TestAnchorsAreBitIdentical(unittest.TestCase):
    def test_each_anchor_is_exactly_what_the_repo_was_priced_against(self):
        for card, ns in PINNED.items():
            self.assertIn(card, vcm.MEASURED_NS_PER_DAY_84K, f"{card} vanished from the table")
            self.assertEqual(vcm.MEASURED_NS_PER_DAY_84K[card], ns,
                             f"{card} moved — every $/ns in the repo and the ladder basis rest on it")

    def test_the_reference_card_and_its_rate_are_unchanged(self):
        self.assertEqual(vcm.REFERENCE_CARD, "RTX4090")
        self.assertEqual(vcm.REFERENCE_NS_PER_H, PINNED_REFERENCE_NS_PER_H)

    def test_a_new_card_may_be_added_without_touching_the_anchors(self):
        """The lane's whole purpose is to GROW this table, so growth must not be what this test forbids."""
        self.assertGreaterEqual(len(vcm.MEASURED_NS_PER_DAY_84K), len(PINNED))


class TestEveryEntryIsDerivedFromRecordedBlocks(unittest.TestCase):
    def setUp(self):
        self.records = {r["card"]: r for r in PROV["records"]}

    def test_every_table_entry_has_a_provenance_record(self):
        missing = sorted(set(vcm.MEASURED_NS_PER_DAY_84K) - set(self.records))
        self.assertEqual(missing, [], f"no evidence recorded for {missing} — a throughput without its "
                                      f"provenance is indistinguishable from a fabricated one")

    def test_every_entry_equals_the_mean_of_its_own_blocks(self):
        for card, ns in vcm.MEASURED_NS_PER_DAY_84K.items():
            blocks = self.records[card]["blocks_ns_per_day"]
            mean, _sd, _cv = bench.block_stats(blocks)
            self.assertAlmostEqual(round(mean, 2), ns, places=2,
                                   msg=f"{card}: table says {ns}, its blocks say {mean:.2f}")

    def test_the_recorded_cv_matches_the_blocks(self):
        for card, rec in self.records.items():
            _m, _sd, cv = bench.block_stats(rec["blocks_ns_per_day"])
            self.assertAlmostEqual(cv, rec["cv"], places=3, msg=f"{card}: CV disagrees with its blocks")

    def test_every_record_is_the_same_protocol(self):
        """The scientific content of the table: one quantity, not three that happen to share units."""
        for card, rec in self.records.items():
            self.assertEqual(rec["atoms"], PROV["protocol"]["particles"], card)
            self.assertEqual(rec["dt_fs"], PROV["protocol"]["timestep_fs"], card)
            self.assertEqual(rec["platform"], PROV["protocol"]["platform"], card)
            self.assertEqual(rec["blocks"], PROV["protocol"]["timed_blocks"], card)

    def test_every_record_passes_the_stability_gate_it_was_kept_under(self):
        for card, rec in self.records.items():
            self.assertLessEqual(rec["cv"], sweep.MAX_CV,
                                 f"{card} would not survive the gate new cards must pass")

    def test_the_4090_to_3090_ratio_is_2_10_not_the_withdrawn_2_42(self):
        """A figure derived from 2.42x is stale, and this is the cheapest place to catch its return."""
        r = vcm.MEASURED_NS_PER_DAY_84K["RTX4090"] / vcm.MEASURED_NS_PER_DAY_84K["RTX3090"]
        self.assertAlmostEqual(r, 2.102, places=2)


if __name__ == "__main__":
    unittest.main()
