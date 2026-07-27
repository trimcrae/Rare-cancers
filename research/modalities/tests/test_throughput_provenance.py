"""EVERY TABLE ENTRY IS THE SAME STATISTIC, DERIVED FROM ITS OWN HOSTS, AND THE PINNED ONES DO NOT DRIFT.

WHY THIS FILE EXISTS. `vast_cost_model.MEASURED_NS_PER_DAY_84K` anchors every `$/ns` in the repo, the ladder
basis, the drift line, the fan-out gate and the relaunch gate. CLAUDE.md rule 1.1 says a total is DERIVED,
never typed — so `throughput-bench-provenance.json` carries each card's independent-host measurements and this
file recomputes the estimator from them.

★ AND THE ESTIMATOR ITSELF IS PINNED, which is the lesson of 2026-07-27. The original three anchors were ONE
HOST EACH and, by accident, sampled different parts of their own distributions — the RTX 4080's host sat within
0.3 % of the best of four while the RTX 4090's sat 6.7 % below the best of five. They were therefore not the
same statistic, and every card *ratio* inherited a ~7 % error nobody had chosen. **A table whose entries are
computed different ways is worse than a table with wrong numbers, because the error is invisible.**

Three independent things are pinned, and they fail for different reasons:
  1. every entry equals the MEDIAN over the hosts recorded for it (evidence and table agree);
  2. every entry is the SAME estimator, or is explicitly labelled under-sampled (no silent mixing);
  3. the current values and `REFERENCE_NS_PER_H` are bit-identical to what downstream figures were computed
     against (nobody "improves" an anchor without a deliberate, appendixed, ladder-regenerating correction).
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

# The values every $/ns, every ladder figure and every drift ratio in the repo is computed against, as of the
# 2026-07-27 re-anchoring. Changing one means: the old value into pinned-figures.json, an APPENDIX line in
# pricing.md, and a REGENERATED vast-ladder-repricing.json — all in the SAME commit.
PINNED = {
    "RTX5090": 1034.58, "RTX4090": 804.06, "RTX5080": 752.32, "RTX4080": 693.35,
    "A100PCIE": 523.82, "RTX3090TI": 481.87, "RTXPRO4000": 471.63, "RTX3090": 460.91,
    "RTX5060TI": 389.16, "RTXA4000": 246.30,
}
PINNED_REFERENCE_NS_PER_H = 804.06 / 24.0

# Cards the board could not supply 3 distinct hosts for. They may be a different statistic ONLY because they
# say so out loud; an entry that is under-sampled and SILENT is the bug.
KNOWN_UNDER_SAMPLED = {"A100PCIE", "RTX3090TI"}


class TestTheCurrentValuesAreBitIdentical(unittest.TestCase):
    def test_each_entry_is_exactly_what_the_repo_is_priced_against(self):
        for card, ns in PINNED.items():
            self.assertIn(card, vcm.MEASURED_NS_PER_DAY_84K, f"{card} vanished from the table")
            self.assertEqual(vcm.MEASURED_NS_PER_DAY_84K[card], ns,
                             f"{card} moved — every $/ns in the repo and the ladder basis rest on it")

    def test_the_reference_card_and_its_rate(self):
        self.assertEqual(vcm.REFERENCE_CARD, "RTX4090")
        self.assertEqual(vcm.REFERENCE_NS_PER_H, PINNED_REFERENCE_NS_PER_H)

    def test_reference_ns_per_h_is_derived_from_the_table_not_typed(self):
        self.assertEqual(vcm.REFERENCE_NS_PER_H,
                         vcm.MEASURED_NS_PER_DAY_84K[vcm.REFERENCE_CARD] / 24.0)

    def test_growing_the_table_is_still_allowed(self):
        """Widening is the lane's purpose, so growth must not be what this file forbids."""
        self.assertGreaterEqual(len(vcm.MEASURED_NS_PER_DAY_84K), len(PINNED))


class TestEveryEntryIsDerivedFromItsOwnHosts(unittest.TestCase):
    def setUp(self):
        self.records = {r["card"]: r for r in PROV["records"]}

    def test_every_table_entry_has_a_provenance_record(self):
        missing = sorted(set(vcm.MEASURED_NS_PER_DAY_84K) - set(self.records))
        self.assertEqual(missing, [], f"no evidence recorded for {missing} — a throughput without its "
                                      f"provenance is indistinguishable from a fabricated one")

    def test_every_entry_equals_the_median_over_its_recorded_hosts(self):
        for card, ns in vcm.MEASURED_NS_PER_DAY_84K.items():
            hosts = self.records[card]["hosts_ns_per_day"]
            self.assertEqual(sweep.median_over_hosts(hosts), ns,
                             f"{card}: table says {ns}, the median of its hosts says "
                             f"{sweep.median_over_hosts(hosts)}")

    def test_the_recorded_estimator_label_matches_the_host_count(self):
        for card, rec in self.records.items():
            _v, label, n = sweep.estimator_for(rec["hosts_ns_per_day"])
            self.assertEqual(label, rec["estimator"], card)
            self.assertEqual(n, rec["n_hosts"], card)


class TestOneEstimatorOrAnHonestLabel(unittest.TestCase):
    """The 2026-07-27 lesson: mixing estimators silently is what put a ~7 % error into every card ratio."""

    def setUp(self):
        self.records = {r["card"]: r for r in PROV["records"]}

    def test_every_properly_sampled_card_used_the_same_estimator(self):
        for card, rec in self.records.items():
            if card in KNOWN_UNDER_SAMPLED:
                continue
            self.assertEqual(rec["estimator"], f"median_of_{rec['n_hosts']}_hosts", card)
            self.assertGreaterEqual(rec["n_hosts"], sweep.MIN_HOSTS_FOR_MEDIAN, card)

    def test_an_under_sampled_card_is_LABELLED_never_silently_a_median_of_two(self):
        for card in KNOWN_UNDER_SAMPLED:
            rec = self.records[card]
            self.assertLess(rec["n_hosts"], sweep.MIN_HOSTS_FOR_MEDIAN, card)
            self.assertIn(rec["estimator"], ("single_host", f"provisional_median_of_{rec['n_hosts']}_hosts"),
                          f"{card} is under-sampled and must say so")

    def test_the_table_itself_flags_the_under_sampled_entries(self):
        """A reader of the table must see it without opening the provenance file."""
        src = open(os.path.join(_MOD, "vast_cost_model.py")).read()
        block = src[src.index("MEASURED_NS_PER_DAY_84K = {"):]
        block = block[:block.index("}")]
        for card in KNOWN_UNDER_SAMPLED:
            line = next(ln for ln in block.splitlines() if f'"{card}"' in ln)
            self.assertTrue("**" in line or "provisional" in line.lower() or "single" in line.lower(),
                            f"{card}'s line does not flag that it is under-sampled: {line}")


class TestTheHostEvidenceIsRealAndComparable(unittest.TestCase):
    def test_every_host_observation_is_the_mean_of_its_own_blocks(self):
        for o in PROV["host_observations"]:
            blocks = o.get("blocks_ns_per_day")
            if not blocks:
                continue
            mean, _sd, _cv = bench.block_stats(blocks)
            self.assertAlmostEqual(round(mean, 2), o["ns_per_day"], places=2, msg=o.get("tag"))

    def test_every_host_observation_passes_the_stability_gate(self):
        for o in PROV["host_observations"]:
            if o.get("cv") is not None:
                self.assertLessEqual(o["cv"], sweep.MAX_CV, o.get("tag"))

    def test_the_host_sets_are_the_ones_the_records_summarise(self):
        by_card = {}
        for o in PROV["host_observations"]:
            by_card.setdefault(o["card"], []).append(round(float(o["ns_per_day"]), 2))
        for r in PROV["records"]:
            self.assertEqual(sorted(by_card.get(r["card"], [])),
                             [round(x, 2) for x in r["hosts_ns_per_day"]], r["card"])


class TestTheRetiredGridIsKeptNotDropped(unittest.TestCase):
    """CLAUDE.md rule 1.2: never silently drop a superseded number. These per-block values are also the ONLY
    surviving copy — a deterministic S3 key let a re-run overwrite the raw artifacts in place."""

    def test_the_three_original_anchors_are_still_recorded(self):
        retired = {r["card"]: r for r in
                   PROV["retired_2026_07_24_single_host_md_env_grid"]["records"]}
        self.assertEqual(set(retired), {"RTX4090", "RTX4080", "RTX3090"})
        for card, old in (("RTX4090", 755.36), ("RTX4080", 703.51), ("RTX3090", 359.36)):
            mean, _sd, _cv = bench.block_stats(retired[card]["blocks_ns_per_day"])
            self.assertAlmostEqual(round(mean, 2), old, places=2)

    def test_the_retired_values_are_registered_in_pinned_figures(self):
        pf = json.load(open(os.path.join(_MOD, "..", "manuscripts", "pinned-figures.json")))
        ids = {e["id"] for e in pf["superseded"]}
        for need in ("card_rtx4090_755_36", "card_rtx4080_703_51", "card_rtx3090_359_36"):
            self.assertIn(need, ids, f"{need} must be registered so CI finds every copy")


if __name__ == "__main__":
    unittest.main()
