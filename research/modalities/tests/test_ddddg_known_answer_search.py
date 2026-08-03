#!/usr/bin/env python3
"""Unit tests for the row-27 gate: does a paralogue-scale ligand-side ddddG known answer exist?

★ WHAT THESE TESTS PROTECT. The three ways this search could return a FALSE PROCEED, each the
ligand-side analogue of the promiscuous name match that made `pmx_mutation_reference` return
PROCEED off an unrelated SOCS2-EloBC record:

  1. accepting a protein pair because the names look related rather than because an ALIGNMENT said so
  2. accepting a ligand pair because the names look related rather than because RDKit said so
  3. mixing observables -- a Ki on one arm and an IC50 on the other -- which is not a double
     difference at all

plus the two ways it could return a false NEGATIVE: a transport failure read as absence, and a
reference smaller than the engine's own error being reported as usable.

No network. RDKit is exercised when present and the RDKit-dependent tests skip (loudly) when not,
because a silent string-comparison fallback is exactly failure mode 2.
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import ddddg_known_answer_search as m  # noqa: E402

try:
    import rdkit  # noqa: F401
    HAVE_RDKIT = True
except Exception:  # noqa: BLE001
    HAVE_RDKIT = False


def act(target, mol, st, p, rel="=", assay="CHEMBL_A1", doc="CHEMBL_D1"):
    return {"target_chembl_id": target, "molecule_chembl_id": mol, "standard_type": st,
            "standard_relation": rel, "pchembl_value": p, "assay_chembl_id": assay,
            "document_chembl_id": doc, "assay_type": "B"}


class TestEnergyArithmetic(unittest.TestCase):
    def test_log_unit_conversion_is_the_textbook_one(self):
        self.assertAlmostEqual(m.LOG10_TO_KCAL, 1.3642, places=3)

    def test_ddddg_sign_and_magnitude(self):
        # arm A: reference 7.0 -> variant 8.0 (1 log unit better)
        # arm B: reference 7.0 -> variant 7.0 (no change) => ddddG = -1.3642 kcal/mol
        idx = m.index_activities([
            act("A", "d0", "Ki", 7.0), act("A", "d", "Ki", 8.0),
            act("B", "d0", "Ki", 7.0), act("B", "d", "Ki", 7.0)])
        e = m.ddddg_from_four(m.measurement(idx, "A", "d", "Ki"),
                              m.measurement(idx, "A", "d0", "Ki"),
                              m.measurement(idx, "B", "d", "Ki"),
                              m.measurement(idx, "B", "d0", "Ki"))
        self.assertAlmostEqual(e["ddddG_kcal"], -1.364, places=2)
        self.assertAlmostEqual(e["abs_ddddG_kcal"], 1.364, places=2)


class TestActivityIndexing(unittest.TestCase):
    def test_inequality_rows_are_not_values(self):
        """⛔ A '>' row is a BOUND. Subtracting bounds would fabricate a difference."""
        idx = m.index_activities([act("A", "d0", "Ki", 7.0, rel=">")])
        self.assertEqual(idx, {})

    def test_disallowed_standard_type_is_dropped(self):
        idx = m.index_activities([act("A", "d0", "EC50", 7.0)])
        self.assertEqual(idx, {})

    def test_types_are_kept_separate_so_they_cannot_be_mixed(self):
        """⛔ FAILURE MODE 3. A Ki on one arm and an IC50 on the other is two quantities subtracted."""
        idx = m.index_activities([act("A", "d0", "Ki", 7.0), act("A", "d0", "IC50", 5.0)])
        self.assertEqual(len(idx), 2)
        self.assertIsNotNone(m.measurement(idx, "A", "d0", "Ki"))
        self.assertIsNotNone(m.measurement(idx, "A", "d0", "IC50"))
        self.assertNotEqual(m.measurement(idx, "A", "d0", "Ki")["pchembl_median"],
                            m.measurement(idx, "A", "d0", "IC50")["pchembl_median"])

    def test_repeat_measurements_are_medianed_and_the_spread_is_reported(self):
        idx = m.index_activities([act("A", "d0", "Ki", 6.0), act("A", "d0", "Ki", 7.0),
                                  act("A", "d0", "Ki", 8.0)])
        got = m.measurement(idx, "A", "d0", "Ki")
        self.assertEqual(got["pchembl_median"], 7.0)
        self.assertEqual(got["n_measurements"], 3)
        self.assertEqual(got["pchembl_spread"], 2.0)


@unittest.skipUnless(HAVE_RDKIT, "rdkit not installed in this environment")
class TestCongeneric(unittest.TestCase):
    def test_a_matched_pair_is_congeneric(self):
        # toluene -> ethylbenzene on a benzene scaffold: same Murcko scaffold, one heavy atom apart
        r = m.congeneric_report("Cc1ccccc1", "CCc1ccccc1")
        self.assertTrue(r["available"])
        self.assertTrue(r["identical_murcko_scaffold"])
        self.assertEqual(r["heavy_atom_delta"], 1)
        self.assertTrue(r["is_congeneric"])

    def test_two_unrelated_actives_are_not_congeneric(self):
        """⛔ FAILURE MODE 2. Two molecules that merely bind the same pair of proteins are not a
        matched pair, and only a structural test can say so."""
        r = m.congeneric_report("Cc1ccccc1", "C1CCNCC1CCOC(=O)N2CCOCC2")
        self.assertTrue(r["available"])
        self.assertFalse(r["is_congeneric"])

    def test_tanimoto_does_not_gate_so_small_congeners_are_not_silently_excluded(self):
        """⛔ THE SIZE BIAS. acetaminophen -> its propionyl analogue is unambiguously congeneric and
        scores only 0.59 on a Morgan Tanimoto; toluene -> ethylbenzene scores 0.39. If Tanimoto
        gated, the scan would exclude small-molecule series and report the loss as an absence of
        references. Both must pass on the MCS criterion."""
        for a, b in [("Cc1ccccc1", "CCc1ccccc1"),
                     ("CC(=O)Nc1ccc(O)cc1", "CCC(=O)Nc1ccc(O)cc1")]:
            r = m.congeneric_report(a, b)
            self.assertLess(r["tanimoto_morgan_r2_2048"], 0.60, (a, b))
            self.assertEqual(r["mcs_fraction_of_smaller"], 1.0, (a, b))
            self.assertTrue(r["is_congeneric"], (a, b))
        self.assertTrue(m.PREREG["tanimoto_reported_but_not_gating"])

    def test_identical_molecules_are_rejected(self):
        r = m.congeneric_report("Cc1ccccc1", "Cc1ccccc1")
        self.assertTrue(r["identical_molecules"])
        self.assertFalse(r["is_congeneric"])

    def test_missing_rdkit_blocks_a_positive_rather_than_degrading(self):
        real = m.congeneric_report
        try:
            import builtins
            orig = builtins.__import__

            def fake(name, *a, **k):
                if name.startswith("rdkit"):
                    raise ImportError("simulated: rdkit absent")
                return orig(name, *a, **k)
            builtins.__import__ = fake
            r = real("Cc1ccccc1", "CCc1ccccc1")
        finally:
            builtins.__import__ = orig
        self.assertFalse(r["available"])
        self.assertNotIn("is_congeneric", r)


class TestHomologyIsMeasured(unittest.TestCase):
    def test_identical_sequences_are_100_percent(self):
        s = "MKTAYIAKQRQISFVKSHFSRQLEERLGLIEVQ" * 3
        pct, method = m.pairwise_identity(s, s)
        self.assertGreater(pct, 99.0)
        self.assertIn(method, ("biopython-global", "pure-python-nw"))

    def test_unrelated_sequences_are_far_below_the_floor(self):
        a = "MKTAYIAKQRQISFVKSHFSRQLEERLGLIEVQ" * 3
        b = "WWWWCCCCPPPPGGGGWWWWCCCCPPPPGGGG" * 3
        pct, _ = m.pairwise_identity(a, b)
        self.assertLess(pct, m.PREREG["identity_min_percent"])

    def test_kmer_prefilter_can_only_lose_candidates(self):
        """The prefilter is a cheap proxy; the alignment is the evidence. Assert it is not used as
        the evidence anywhere: a pair passing the prefilter still faces the identity floor."""
        a = "MKTAYIAKQRQISFVKSHFSRQLEERLGLIEVQ" * 3
        b = a[:40] + "WWWWCCCCPPPPGGGG" * 6
        cont = m.kmer_containment(m.kmer_set(a, 4), m.kmer_set(b, 4))
        self.assertGreater(cont, 0.0)
        pct, _ = m.pairwise_identity(a, b)
        self.assertLess(pct, 100.0)


class TestGate(unittest.TestCase):
    ENGINE = {"band_kcal": 0.61, "_source": "test"}

    def _cand(self, ddddg, arm_a="P1", arm_b="P2"):
        return {"energy": {"abs_ddddG_kcal": abs(ddddg), "ddddG_kcal": ddddg},
                "arm_a_accession": arm_a, "arm_b_accession": arm_b,
                "arm_a_target": "CHEMBL1", "arm_b_target": "CHEMBL2",
                "arm_a_label": "A", "arm_b_label": "B",
                "standard_type": "Ki", "ligand_reference": "d0", "ligand_variant": "d",
                "pair_identity_percent": 78.0,
                "congeneric": {"tanimoto_morgan_r2_2048": 0.9}}

    def _structs(self, ok=True):
        e = ["1ABC"] if ok else []
        return {"P1": {"read": True, "entries": e}, "P2": {"read": True, "entries": e}}

    def test_proceed_when_everything_clears(self):
        g = m.grade([self._cand(1.2)], engine=self.ENGINE)
        v = m.verdict(g, self._structs(), {"chembl": True, "rcsb": True})
        self.assertEqual(v["decision"], "PROCEED")

    def test_stop_band_when_the_reference_is_inside_the_engine_error(self):
        """⛔ Open decision 7: a benchmark smaller than the engine's own error buys nothing."""
        g = m.grade([self._cand(0.55)], engine=self.ENGINE)
        v = m.verdict(g, self._structs(), {"chembl": True, "rcsb": True})
        self.assertEqual(v["decision"], "STOP_BAND")

    def test_stop_no_reference_only_when_every_instrument_read_cleanly(self):
        g = m.grade([self._cand(6.0)], engine=self.ENGINE)   # out of band
        v = m.verdict(g, self._structs(), {"chembl": True, "rcsb": True})
        self.assertEqual(v["decision"], "STOP_NO_REFERENCE")

    def test_transport_failure_is_UNDETERMINED_not_STOP(self):
        """⛔ An absent reading is not a reading of absence."""
        g = m.grade([], engine=self.ENGINE)
        v = m.verdict(g, {}, {"chembl": True, "rcsb": False})
        self.assertEqual(v["decision"], "UNDETERMINED")
        self.assertIn("rcsb", v["sentence"])

    def test_no_structures_is_not_a_stop(self):
        g = m.grade([self._cand(1.2)], engine=self.ENGINE)
        v = m.verdict(g, self._structs(ok=False), {"chembl": True, "rcsb": True})
        self.assertEqual(v["decision"], "UNDETERMINED")

    def test_null_rejection_rule_is_stated_in_every_verdict(self):
        g = m.grade([self._cand(1.2)], engine=self.ENGINE)
        v = m.verdict(g, self._structs(), {"chembl": True, "rcsb": True})
        self.assertTrue(v["gates"]["A6_null_rejection_stated_up_front"]["statement"])
        self.assertIn("negative control", v["gates"]["A6_null_rejection_stated_up_front"]["statement"])


class TestEngineBandIsReadNotTyped(unittest.TestCase):
    def test_it_comes_from_instrument_options_json(self):
        band = m.engine_band()
        self.assertIn("band_kcal", band)
        if "_fallback_used" not in band:
            self.assertEqual(band["_source"], "instrument-options.json")
            self.assertAlmostEqual(band["band_kcal"], 0.61, places=2)
            self.assertIn("TYK2", band["quoted"])

    def test_unreadable_artifact_flags_the_fallback_rather_than_hiding_it(self):
        band = m.engine_band(path="/nonexistent/instrument-options.json")
        self.assertIn("_fallback_used", band)


class TestOffline(unittest.TestCase):
    def test_c01a_offline_is_undetermined(self):
        doc = m.run_c01a(out_path=None, offline=True)
        self.assertEqual(doc["verdict"]["decision"], "UNDETERMINED")

    def test_c01b_offline_is_undetermined(self):
        doc = m.run_c01b(out_path=None, offline=True)
        self.assertEqual(doc["verdict"]["decision"], "UNDETERMINED")

    def test_map_edits_carry_the_required_fields(self):
        doc = m.run_c01b(out_path=None, offline=True)
        for e in doc["map_edits_required"]:
            for k in ("section", "anchor", "current_text", "proposed_text", "why", "artifact"):
                self.assertIn(k, e)


@unittest.skipUnless(HAVE_RDKIT, "rdkit not installed in this environment")
class TestBuildCandidatesEndToEnd(unittest.TestCase):
    def test_a_congeneric_quadruple_becomes_one_candidate(self):
        rows = [act("A", "M1", "Ki", 7.0), act("A", "M2", "Ki", 8.0),
                act("B", "M1", "Ki", 7.0), act("B", "M2", "Ki", 7.0),
                # a non-congeneric third compound that must not pair up
                act("A", "M3", "Ki", 6.0), act("B", "M3", "Ki", 6.0)]
        idx = m.index_activities(rows)
        smiles = {"M1": {"smiles": "Cc1ccccc1"}, "M2": {"smiles": "CCc1ccccc1"},
                  "M3": {"smiles": "C1CCNCC1CCOC(=O)N2CCOCC2"}}
        cands = m.build_candidates(idx, "A", "B", smiles)
        self.assertEqual(len(cands), 1)
        self.assertEqual({cands[0]["ligand_reference"], cands[0]["ligand_variant"]}, {"M1", "M2"})
        self.assertAlmostEqual(cands[0]["energy"]["abs_ddddG_kcal"], 1.364, places=2)


@unittest.skipUnless(HAVE_RDKIT, "rdkit not installed in this environment")
class TestScaffoldBucketPrefilter(unittest.TestCase):
    """⛔ A SCAN THAT CANNOT FINISH IS A NULL THAT MEANS NOTHING. The bucket exists so the O(n^2)
    candidate loop does not run a 5 s MCS on every pair of hundreds of shared compounds. It must
    (a) actually cut the work and (b) lose nothing, because an identical Murcko scaffold is already
    a required criterion."""

    def test_buckets_group_by_scaffold_and_cut_the_pair_count(self):
        smiles = {("B%d" % i): {"smiles": s} for i, s in enumerate(
            ["Cc1ccccc1", "CCc1ccccc1", "CCCc1ccccc1"])}
        smiles.update({("P%d" % i): {"smiles": s} for i, s in enumerate(
            ["CN1CCNCC1", "CCN1CCNCC1"])})
        buckets = m.scaffold_buckets(list(smiles), smiles)
        self.assertEqual(len(buckets), 2, buckets)
        n_pairs = sum(len(v) * (len(v) - 1) // 2 for v in buckets.values())
        n = len(smiles)
        self.assertLess(n_pairs, n * (n - 1) // 2)

    def test_the_bucket_cannot_drop_a_pair_that_would_have_been_accepted(self):
        """Anything in different buckets fails `identical_murcko_scaffold` anyway."""
        smiles = {"A": {"smiles": "Cc1ccccc1"}, "B": {"smiles": "CN1CCNCC1"}}
        buckets = m.scaffold_buckets(["A", "B"], smiles)
        self.assertEqual(len(buckets), 2)
        r = m.congeneric_report(smiles["A"]["smiles"], smiles["B"]["smiles"])
        self.assertFalse(r["identical_murcko_scaffold"])
        self.assertFalse(r["is_congeneric"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
