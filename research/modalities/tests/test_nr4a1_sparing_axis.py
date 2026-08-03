#!/usr/bin/env python3
"""Tests for the NR4A1-sparing axis (`nr4a1_sparing_axis.py`).

⛔ THE ONE THAT MATTERS IS `test_forward_self_check_reproduces_M3`. This module's headline is a NULL result,
and a null result is indistinguishable from a broken measurement — so the guarantee that keeps the finding
honest is that the SAME code path, run with M3's forward predicate, reproduces the committed 0.923 / 0.173.
If that ever stops holding, the inverse number in the artifact is not a fact about the protein.
"""
import json
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.abspath(os.path.join(HERE, ".."))
REPO = os.path.abspath(os.path.join(MOD, "..", ".."))
sys.path.insert(0, MOD)

import nr4a1_sparing_axis as A  # noqa: E402

ART = os.path.join(MOD, "nr4a1-sparing-axis.json")


def _art():
    with open(ART) as f:
        return json.load(f)


class TestOffsetRecovery(unittest.TestCase):
    """The defect this module found in M3 is an offset bug, so the offset recovery is pinned."""

    def test_recovered_offsets_are_per_species_and_not_nr4a3s(self):
        off = _art()["steric_inverse"]["uniprot_offsets_recovered"]
        self.assertEqual(off["NR4A3"], 372)
        # The whole point: the paralogues do NOT share NR4A3's offset. If they ever do, either the models
        # changed or somebody re-introduced the M3 bug.
        self.assertNotEqual(off["NR4A1"], off["NR4A3"])
        self.assertNotEqual(off["NR4A2"], off["NR4A3"])

    def test_recovered_numbering_lands_on_the_right_residue(self):
        """A recovered offset must name the residue the model actually holds, in the real FASTA."""
        seqs = A._load("research/modalities/nr4a-sequences-cache.json")
        art = _art()
        off = art["steric_inverse"]["uniprot_offsets_recovered"]
        rows = art["steric_inverse"]["blocks"]["pocket5_matched_to_M3"]["per_position"]
        for _, rec in rows.items():
            for sp in ("NR4A1", "NR4A2", "NR4A3"):
                u = rec["uniprot"][sp]
                if u is None:
                    continue
                self.assertEqual(seqs[sp][u - 1], rec["residues"][sp],
                                 "%s %s does not carry %s" % (sp, u, rec["residues"][sp]))
        self.assertTrue(all(isinstance(v, int) for v in off.values()))


class TestForwardSelfCheck(unittest.TestCase):
    def test_forward_self_check_reproduces_M3(self):
        fsc = _art()["steric_inverse"]["⛔_forward_direction_self_check"]
        self.assertEqual(fsc["recomputed"], fsc["committed_M3"])
        self.assertTrue(fsc["reproduces_committed_M3"])

    def test_forward_self_check_agrees_with_the_live_register(self):
        """Not just with the value baked into the artifact — with selectivity-mechanism-options.json itself."""
        m3 = A._load("research/modalities/selectivity-mechanism-options.json")["measurements"]["M3"]
        fsc = _art()["steric_inverse"]["⛔_forward_direction_self_check"]
        for k in ("unique_and_both_bulkier", "conserved_or_shared"):
            self.assertEqual(fsc["recomputed"][k], m3["by_position_class"][k]["rate"])


class TestReciprocalEnumeration(unittest.TestCase):
    def test_vs_both_is_stricter_than_the_committed_pairwise_set(self):
        """The gap this module exists to close: a position NR4A1 SHARES with NR4A2 is not NR4A1-unique."""
        prior = A._load("research/modalities/nr4a-paralogue-unique-residues.json")["reciprocal_paralogue_unique"]
        shared = {(r["residue"], r["resnum"]) for r in prior["NR4A1"]} & \
                 {(r["residue"], r["resnum"]) for r in prior["NR4A2"]}
        self.assertTrue(shared, "the committed pairwise lists must overlap, or the premise is wrong")
        uniq = {u["uniprot"] for u in
                _art()["reciprocal_enumeration"]["by_species"]["NR4A1"]["unique_positions_in_lbd"]}
        for _, num in shared:
            self.assertNotIn(num, uniq, "a position shared with NR4A2 must not appear as NR4A1-unique")

    def test_nrv04_cys551_is_nr4a1_unique_the_positive_control_of_the_enumeration(self):
        """C551 is the family's one literature-anchored covalent site and is NR4A1-only. If the vs-both
        enumeration cannot recover it, the enumeration is wrong."""
        rows = _art()["reciprocal_enumeration"]["by_species"]["NR4A1"]["unique_positions_in_lbd"]
        hit = [r for r in rows if r["uniprot"] == 551]
        self.assertEqual(len(hit), 1)
        self.assertEqual(hit[0]["residue"], "C")
        self.assertEqual(hit[0]["nr4a3_aligned_resnum"], 579)
        self.assertEqual(hit[0]["nr4a3_aligned_residue"], "T")

    def test_every_reported_position_is_alignment_robust_by_construction(self):
        for sp, blk in _art()["reciprocal_enumeration"]["by_species"].items():
            for row in blk["unique_positions_in_lbd"]:
                for other, p in row["partners"].items():
                    self.assertNotEqual(p["residue"], row["residue"],
                                        "%s %s%s is not unique against %s" % (sp, row["residue"],
                                                                              row["uniprot"], other))


class TestClassAndNull(unittest.TestCase):
    def test_every_block_reports_a_null_beside_its_signal(self):
        """CLAUDE.md: a rate without its matched null is not a result. Enforced, not trusted."""
        for label, blk in _art()["steric_inverse"]["blocks"].items():
            self.assertIn("null_rate", blk, label)
            self.assertIsNotNone(blk["null_rate"], label)
            self.assertIn("signal_minus_null", blk, label)

    def test_signal_class_membership_requires_both_uniqueness_and_bulk(self):
        for blk in _art()["steric_inverse"]["blocks"].values():
            for _, rec in blk["per_position"].items():
                if rec["class"] == "nr4a1_unique_and_bulkier":
                    self.assertTrue(rec["nr4a1_categorically_unique_vs_both"])
                    self.assertTrue(rec["nr4a1_strictly_bulkier_than_both"])
                    self.assertGreater(rec["bulk_margin_heavy_atoms"]["nr4a1_over_both"], 0)

    def test_the_verdict_state_is_one_of_the_registers_four(self):
        v = _art()["verdict"]["recommended_register_state"]
        self.assertTrue(any(v.startswith(g) for g in ("✕", "⏸", "🔒", "LIVE")), v)

    def test_a_state_of_parked_names_its_reopening_trigger(self):
        art = _art()
        if art["verdict"]["recommended_register_state"].startswith("⏸"):
            self.assertTrue(art["verdict"]["what_would_reopen_it_if_parked"],
                            "§6: a ⏸ row MUST name what has to land")


class TestCitationsAreNotSecondHomes(unittest.TestCase):
    def test_therapeutic_trade_matches_its_owning_artifact(self):
        b = A._load("research/modalities/nr4a2-sparing-bound.json")
        t = _art()["therapeutic_trade"]
        hpa = b["verdict"]["gates"]["B3_tissue_overlap_measured"]
        self.assertEqual(t["what_the_profile_COSTS"]["tissue_distribution_cannot_rescue_it"]["counts"],
                         hpa["counts"])
        self.assertEqual(t["what_the_profile_BUYS"]["and_NR4A1's_own_single_null_is_the_mild_one"][
                             "n_single_gene_annotations"],
                         b["mgi"]["single_gene"]["Nr4a1"]["n_single_gene_annotations"])

    def test_relocation_control_matches_M4(self):
        m4 = A._load("research/modalities/selectivity-mechanism-options.json")["measurements"]["M4"]
        txt = _art()["controls"]["★_the_relocation_control_is_this_axis's_central_problem_not_a_footnote"]
        self.assertIn(str(m4["median_centroid_shift_A"]["NR4A1"]), txt)


class TestMapEdits(unittest.TestCase):
    def test_edits_without_an_anchor_carry_a_where_it_goes(self):
        """route_map_edits.py defers unanchored edits; an unanchored edit with no destination is useless."""
        for e in _art()["map_edits_required"]:
            if not e.get("anchor"):
                self.assertTrue(e.get("where_it_goes"), e.get("id"))

    def test_no_edit_invents_an_anchor_for_a_section_that_does_not_exist(self):
        target = os.path.join(REPO, "research", "manuscripts", "nr4a3-program-map.md")
        with open(target) as f:
            text = f.read()
        for e in _art()["map_edits_required"]:
            anchor = e.get("anchor")
            if anchor:
                self.assertGreaterEqual(text.count(anchor), 1,
                                        "anchor for %s is not present in the live map" % e.get("id"))


if __name__ == "__main__":
    unittest.main()
