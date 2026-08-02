"""The $0 precheck's gate must be unfoolable in the two directions that would cost real money.

Direction 1: an instrument that could not be read must NEVER render as "no reference exists". That is
the absent-reading-vs-reading-of-absence error CLAUDE.md section 4 names, and here it would turn a
transport failure into a scientific STOP.

Direction 2: a measured value that is smaller than the engine's own accuracy band must NEVER render as
PROCEED. That is STRATEGY Open decision 7, and here it would buy a run that cannot tell a right answer
from a wrong one.
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pmx_mutation_reference as pmr  # noqa: E402


HEADER = ("#Pdb;Mutation(s)_PDB;Protein 1;Protein 2;Affinity_mut (M);Affinity_wt (M);Temperature")


def _csv(*rows):
    return "\n".join([HEADER] + list(rows)) + "\n"


# ------------------------------------------------------------------ the SKEMPI instrument
def test_empty_table_is_a_load_failure_not_a_finding():
    scan = pmr.skempi_scan("")
    assert scan["loaded"] is False
    assert any("LOAD FAILURE" in e for e in scan["errors"])
    # and the verdict built on it must not be a scientific negative
    v = pmr.verdict(scan, [])
    assert v["decision"] == "UNDETERMINED"
    assert "ABSENT READING" in v["sentence"]


def test_pdb_and_name_scans_are_independent_routes_to_the_same_row():
    text = _csv("6HAX_A_B;QA98L;SMARCA2 bromodomain;VHL;1E-6;1E-7;298",
                "9XYZ_A_B;LA10A;SMARCA4 bromodomain;Elongin C;1E-6;1E-7;298",
                "1ABC_A_B;YA29A;Lysozyme;Antibody;1E-6;1E-7;298")
    scan = pmr.skempi_scan(text)
    assert scan["loaded"] is True
    assert scan["n_pdb_hits"] == 1                      # only 6HAX is in CANDIDATE_PDBS
    assert scan["n_name_hits_paired"] == 1              # SMARCA4 vs Elongin C: both arms, other deposit
    assert scan["n_name_leads"] == 0
    # ddG is RECOMPUTED from the Kd pair, never read off a cell
    assert scan["pdb_hits"][0]["ddg_kcal"] == pytest.approx(1.363, abs=0.01)
    # the unrelated complex is in no bucket at all
    assert all("Lysozyme" not in str(r.get("protein_1"))
               for r in scan["name_hits_paired"] + scan["name_leads"])


def test_a_single_substring_match_is_a_LEAD_and_can_never_satisfy_the_gate():
    """The regression that this whole three-bucket split exists for.

    The first version of the gate pooled every name match and returned PROCEED off a 2.048 kcal/mol
    record that a promiscuous substring had matched somewhere else in the database. A bromodomain is
    not THIS bromodomain, and a populated field is not a measured one (CLAUDE.md section 4b).
    """
    # a big, real, entirely off-interface effect: BRD4 against a histone, not against the E3
    scan = pmr.skempi_scan(_csv("8ABC_A_B;YA29A;Bromodomain-containing protein 4;Histone H4;1E-2;1E-7;298"))
    assert scan["n_pdb_hits"] == 0
    assert scan["n_name_hits_paired"] == 0
    assert scan["n_name_leads"] == 1
    assert scan["name_leads"][0]["ddg_kcal"] > 5.0      # a large measured number, and irrelevant
    v = pmr.verdict(scan, [{"tag": "q", "query": "q", "error": None, "records": []}])
    assert v["decision"] == "STOP_NO_REFERENCE"
    assert v["gates"]["G1_measured_primary_source"]["met"] is False
    assert v["gates"]["G1_measured_primary_source"]["skempi_offinterface_name_leads"] == 1
    # and the lead is still SURFACED, because discovery is its job
    assert scan["name_lead_complexes"]


def test_unparseable_affinity_is_recorded_not_dropped():
    scan = pmr.skempi_scan(_csv("6HAX_A_B;QA98L;SMARCA2;VHL;n.d.;1E-7;298"))
    hit = scan["pdb_hits"][0]
    assert hit["ddg_kcal"] is None
    assert "ddg_unavailable_because" in hit
    # a row we could not turn into a number does not satisfy G1
    v = pmr.verdict(scan, [{"tag": "t", "query": "q", "error": None, "records": []}])
    assert v["gates"]["G1_measured_primary_source"]["met"] is False


# ------------------------------------------------------------------ the Europe PMC instrument
def test_a_span_needs_BOTH_a_mutation_and_a_quantity():
    assert pmr.mutational_spans("The Q1469L mutant bound with a Kd of 12 nM in SPR experiments here.")
    # a mutation with no measurement is a construct, not a value
    assert not pmr.mutational_spans("We generated the Q1469L mutant and crystallised the complex.")
    # a measurement with no mutation is a wild-type affinity
    assert not pmr.mutational_spans("The wild-type protein bound with a Kd of 12 nM by SPR analysis.")


def test_failed_queries_are_named_and_do_not_count_as_negatives():
    epmc = [{"tag": "Q1", "query": "q", "error": "URLError: timed out", "records": []}]
    scan = pmr.skempi_scan(_csv("1ABC_A_B;YA29A;Lysozyme;Antibody;1E-6;1E-7;298"))
    v = pmr.verdict(scan, epmc)
    assert v["decision"] == "UNDETERMINED"
    assert v["epmc_queries_that_failed"] == ["Q1"]


# ------------------------------------------------------------------ Open decision 7's band gate
def _clean_epmc():
    return [{"tag": "Q1", "query": "q", "error": None, "records": []}]


def test_no_measured_reference_stops_the_spend():
    scan = pmr.skempi_scan(_csv("1ABC_A_B;YA29A;Lysozyme;Antibody;1E-6;1E-7;298"))
    v = pmr.verdict(scan, _clean_epmc())
    assert v["decision"] == "STOP_NO_REFERENCE"
    assert "SPEND NOTHING" in v["sentence"]


def test_a_signal_inside_the_band_is_refused_even_though_it_is_real():
    # 1E-6/1E-7 at 298 K is ~1.36 kcal/mol -- a REAL measured value, and still inside the engine's
    # 1.5 kcal/mol qualification tolerance. Decision 7 refuses it.
    scan = pmr.skempi_scan(_csv("6HAX_A_B;QA98L;SMARCA2;VHL;1E-6;1E-7;298"))
    v = pmr.verdict(scan, _clean_epmc())
    assert v["decision"] == "STOP_BAND"
    assert v["gates"]["G1_measured_primary_source"]["met"] is True
    assert v["gates"]["G2_signal_exceeds_band"]["met"] is False


def test_a_signal_outside_the_band_proceeds():
    scan = pmr.skempi_scan(_csv("6HAX_A_B;QA98L;SMARCA2;VHL;1E-4;1E-7;298"))   # ~4.1 kcal/mol
    v = pmr.verdict(scan, _clean_epmc())
    assert v["decision"] == "PROCEED"
    assert v["gates"]["G2_signal_exceeds_band"]["met"] is True


# ------------------------------------------------------------------ the band itself, and the caveat
def test_the_band_is_read_from_the_committed_benchmark_not_typed():
    band = pmr.engine_band()
    assert band["_source"] == "protfep-benchmark-result.json"
    assert band["qualification_tolerance_kcal"] == pytest.approx(1.5)
    # both ends of the effect-size-dependent scatter, which is the whole reason decision 7 bites
    assert band["near_null_replicate_sd_kcal"] == pytest.approx(0.175, abs=0.01)
    assert band["hot_spot_replicate_sd_kcal"] == pytest.approx(1.077, abs=0.01)


def test_a_missing_benchmark_artifact_falls_back_and_says_so():
    band = pmr.engine_band(path="/nonexistent/protfep-benchmark-result.json")
    assert "fallback" in band["_source"]


def test_the_caveat_travels_with_every_verdict():
    v = pmr.verdict(pmr.skempi_scan(""), [])
    assert "NOT demonstrated to resolve a paralogue-scale difference" in \
        v["caveat_that_must_travel_with_any_result"]
    # and it is the same sentence wherever it is read from -- one home
    assert v["caveat_that_must_travel_with_any_result"] == pmr.caveat()


def test_offline_run_never_emits_a_scientific_verdict():
    doc = pmr.run(out_path=None, offline=True)
    assert doc["verdict"]["decision"] == "UNDETERMINED"
