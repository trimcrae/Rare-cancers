#!/usr/bin/env python3
"""Pin `protfep_refcheck.scan_wedge_band` — the $0 selector for the WEDGE-SIZED benchmark.

WHY THIS FILE EXISTS
--------------------
nr4a3-program-map.md's RUNG 5a-KS records that the qualified protein-mutation benchmark set BRACKETS the
wedge without covering it (a +3.4 hot spot and a ~0 near-null), and that until a wedge-sized
benchmark exists "the confirmatory line may not claim to resolve a paralogue-scale difference".
`scan_wedge_band` is the free half of closing that: it picks candidates from primary Kd data.

Every filter it applies exists because failing it yields a benchmark that LOOKS valid and is not,
so each one is tested here against a synthetic SKEMPI table with a known answer. The scanner runs
in CI against the real 30k-row database, where nothing can be asserted about the contents in
advance — which is exactly why the logic has to be pinned against a table we control.

Pure stdlib: the sandbox's egress proxy 403s SKEMPI (measured), so these tests must never fetch.
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import protfep_refcheck as rc  # noqa: E402

HEADER = ("#Pdb;Mutation(s)_PDB;Affinity_mut (M);Affinity_wt (M);Temperature;Reference")


def _row(mut, kd_mut, kd_wt=1e-9, pdb="1BRS_A_D", temp="298", ref="ref"):
    return f"{pdb};{mut};{kd_mut};{kd_wt};{temp};{ref}"


def _csv(*rows):
    return "\n".join([HEADER, *rows]) + "\n"


# A Kd ratio that lands a record at a chosen ddG, so the fixtures state their intent in kcal/mol
# rather than in Kd values a reader would have to back-substitute.
def _kd_for(ddg_kcal, kd_wt=1e-9, temperature_k=298.15):
    import math
    return kd_wt * math.exp(ddg_kcal / (rc.R_KCAL * temperature_k))


def _scan(*rows, **kw):
    kw.setdefault("chains", {"A", "D"})
    return rc.scan_wedge_band(_csv(*rows), "1BRS", **kw)


def _names(entries):
    return [e["mutation"] for e in entries]


def _rejected_reason(rep, mutation):
    for e in rep["rejected"]:
        if e.get("mutation") == mutation:
            return e["reason"]
    raise AssertionError(f"{mutation} was not rejected; candidates = {_names(rep['candidates'])}")


class TestBandFiltering:
    def test_in_band_mutation_is_a_candidate(self):
        rep = _scan(_row("YD29F", _kd_for(1.0)))
        assert _names(rep["candidates"]) == ["D:Y29F"]
        assert rep["candidates"][0]["skempi_median_ddg_kcal"] == pytest.approx(1.0, abs=0.01)

    def test_near_null_is_rejected_as_already_covered(self):
        # Below the band is the control we already have; adding it would buy nothing.
        rep = _scan(_row("YD29F", _kd_for(0.10)))
        assert "outside the wedge band" in _rejected_reason(rep, "D:Y29F")
        assert "near-null" in _rejected_reason(rep, "D:Y29F")

    def test_hot_spot_is_rejected_as_already_covered(self):
        rep = _scan(_row("YD29A", _kd_for(3.4)))
        assert "hot spot" in _rejected_reason(rep, "D:Y29A")

    def test_band_is_applied_on_MAGNITUDE_so_a_stabilising_mutation_qualifies(self):
        # A mutation that STRENGTHENS binding by 1.0 kcal/mol is just as wedge-sized as one that
        # weakens it by 1.0; the engine's job is to resolve the magnitude and get the sign right.
        rep = _scan(_row("YD29F", _kd_for(-1.0)))
        assert _names(rep["candidates"]) == ["D:Y29F"]
        assert rep["candidates"][0]["skempi_median_ddg_kcal"] < 0


class TestPhysicsFilters:
    def test_charge_changing_mutation_is_refused(self):
        # K->A removes a +1: under PME the finite-size artifact does not cancel between the two
        # differently-sized boxes, so engine error would be confounded with it.
        rep = _scan(_row("KD27A", _kd_for(1.0)))
        assert "CHARGE-CHANGING" in _rejected_reason(rep, "D:K27A")

    def test_backbone_altering_mutation_is_refused(self):
        rep = _scan(_row("YD29P", _kd_for(1.0)))
        assert "REFUSED" in _rejected_reason(rep, "D:Y29P")

    def test_unstageable_chain_is_refused_however_good_the_number(self):
        rep = _scan(_row("YZ29F", _kd_for(1.0)))
        assert "not stageable" in _rejected_reason(rep, "Z:Y29F")

    def test_no_chain_filter_admits_any_chain(self):
        rep = _scan(_row("YZ29F", _kd_for(1.0)), chains=None)
        assert _names(rep["candidates"]) == ["Z:Y29F"]


class TestReferenceQuality:
    def test_records_are_pooled_and_the_median_is_used(self):
        rep = _scan(_row("YD29F", _kd_for(0.9)),
                    _row("YD29F", _kd_for(1.0)),
                    _row("YD29F", _kd_for(1.1)))
        assert rep["candidates"][0]["n_records"] == 3
        assert rep["candidates"][0]["skempi_median_ddg_kcal"] == pytest.approx(1.0, abs=0.02)

    def test_irreproducible_reference_is_refused_even_though_its_median_is_in_band(self):
        # THE POINT OF THIS TEST: the median lands squarely in the band while the records disagree
        # by more than the band is wide. Scoring an engine against that median is scoring it against
        # noise, and the failure is invisible unless the spread is checked.
        rep = _scan(_row("YD29F", _kd_for(-0.4)),
                    _row("YD29F", _kd_for(1.0)),
                    _row("YD29F", _kd_for(2.6)))
        reason = _rejected_reason(rep, "D:Y29F")
        assert "not itself resolved at wedge scale" in reason
        assert rep["rejected"][0]["record_spread_kcal"] > rc.MAX_RECORD_SPREAD_KCAL

    def test_multi_mutant_records_are_never_pooled_into_a_single_mutation(self):
        # A double-mutant ddG is a different quantity; averaging one in would corrupt the reference.
        rep = _scan(_row("YD29F,KD27A", _kd_for(1.0)))
        assert rep["candidates"] == []
        assert not any(e.get("mutation") == "D:Y29F" for e in rep["rejected"])


class TestRankingAndContract:
    def test_more_independent_records_rank_first(self):
        rep = _scan(_row("YD29F", _kd_for(1.0)),
                    _row("YD29F", _kd_for(1.0)),
                    _row("TD42S", _kd_for(1.0)))
        assert _names(rep["candidates"])[0] == "D:Y29F"

    def test_a_tighter_reference_outranks_a_looser_one_at_equal_record_count(self):
        rep = _scan(_row("YD29F", _kd_for(0.95)), _row("YD29F", _kd_for(1.05)),
                    _row("TD42S", _kd_for(0.60)), _row("TD42S", _kd_for(1.40)))
        assert _names(rep["candidates"])[0] == "D:Y29F"

    def test_other_pdb_entries_are_not_scanned(self):
        rep = _scan(_row("YD29F", _kd_for(1.0), pdb="1AK4_A_B"))
        assert rep["candidates"] == []

    def test_an_empty_database_is_a_LOAD_FAILURE_not_a_finding(self):
        # "0 candidates" from a table that never loaded is indistinguishable from "no wedge-sized
        # mutation exists", which is a scientific claim. A failed download must not be able to
        # make it. The counts are present either way so a caller cannot read a bare 0 as a result.
        rep = _scan()
        assert rep["n_candidates"] == 0
        assert rep["errors"] and "ZERO rows" in rep["errors"][0]

    def test_a_loaded_database_with_no_qualifying_mutation_reports_no_error(self):
        # The genuine negative: rows loaded, nothing cleared the filters. This is the one case that
        # IS allowed to read as "no candidate on this complex".
        rep = _scan(_row("YD29A", _kd_for(3.4)))
        assert rep["n_candidates"] == 0
        assert rep["errors"] == []
        assert rep["n_rejected"] == 1

    def test_missing_columns_are_an_error_not_an_empty_result(self):
        # An empty result reads as "no wedge-sized mutation exists", which is a scientific claim.
        # A header rename must not be able to make that claim.
        rep = rc.scan_wedge_band("Pdb;Something\n1BRS_A_D;x\n", "1BRS")
        assert rep["errors"] and "columns not found" in rep["errors"][0]
        assert rep["candidates"] == []

    def test_scanner_never_mutates_the_benchmark_set(self):
        import protfep_bench as pb
        before = dict(pb.BENCHMARKS)
        _scan(_row("YD29F", _kd_for(1.0)))
        assert pb.BENCHMARKS == before

    def test_band_endpoints_come_from_the_module_constant(self):
        # The band is the wedge's own expected effect size (nr4a3-program-map.md RUNG 5a-KS). Pinning it here
        # means widening it to admit a candidate is a visible edit, not a quiet one.
        assert rc.WEDGE_BAND_KCAL == (0.5, 1.5)
        assert rc.MAX_RECORD_SPREAD_KCAL == pytest.approx(1.0)


class TestSharedColumnResolution:
    def test_records_for_and_scan_read_the_same_header_knowledge(self):
        # One fact, one place: both consumers resolve columns through parse_skempi, so a header
        # rename cannot fix one and silently break the other.
        text = _csv(_row("YD29F", _kd_for(1.0)))
        rows, columns, errors = rc.parse_skempi(text)
        assert not errors and rows
        hits, _, errs = rc.records_for(text, "1BRS", "D", 29, "Y", "F")
        assert not errs and len(hits) == 1
        assert rc.scan_wedge_band(text, "1BRS")["n_candidates"] == 1
