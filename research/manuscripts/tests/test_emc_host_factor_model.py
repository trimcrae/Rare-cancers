"""Tests for the two-compartment host-factor model.

The model exists to keep one distinction from collapsing: a host factor acts on EMC
deaths and on ordinary deaths through completely different evidence, and only the second
is well supported. Every test here defends that separation, because collapsing it is what
turns "treating obesity is worth something to an EMC patient" -- which is defensible --
into "a GLP-1 agonist is a cancer drug", which is not.
"""

from __future__ import annotations

import importlib.util
import pathlib

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[3]
MODULE = ROOT / "research/manuscripts/emc_host_factor_model.py"


def _load():
    spec = importlib.util.spec_from_file_location("emc_host_factor_model", MODULE)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


M = _load()


def _factor(**kw):
    base = {
        "id": "HF-OBESITY", "factor": "obesity", "intervention": "GLP-1 receptor agonist",
        "prevalence_in_cohort": 0.40,
        "prevalence_basis": "general population, imported -- no EMC series records it",
        "biases": ["reverse_causation", "obesity_paradox"],
        "evidence": [],
    }
    base.update(kw)
    return base


def _ev(compartment, lo, hi, pmid="12345678", status="retrieved"):
    return {"compartment": compartment, "relative_risk_reduction_lo": lo,
            "relative_risk_reduction_hi": hi, "pmid": pmid, "status": status,
            "measured_in": "adults with obesity and cardiovascular disease",
            "endpoint": "all-cause mortality"}


# ---------------------------------------------------------------------------
# The asymmetry -- the model's central claim
# ---------------------------------------------------------------------------
def test_compartment_a_can_always_be_zero_and_compartment_b_cannot():
    """⛔ The floor for an EMC-specific effect must be ZERO, because no EMC evidence
    exists. A non-zero floor would assert that obesity worsens the sarcoma."""
    assert M.COMPARTMENT_TRANSFER["A"][0] == 0.0
    assert M.COMPARTMENT_TRANSFER["B"][0] > 0.0


def test_compartment_a_is_capped_far_below_compartment_b():
    """The same paper supports a statement about ordinary death far better than one about
    cancer death. If these ceilings ever converged, the model would be letting
    compartment-B evidence license a compartment-A claim."""
    assert M.COMPARTMENT_TRANSFER["A"][1] < M.COMPARTMENT_TRANSFER["B"][0]


def test_compartment_b_transfer_is_not_one_because_the_cohort_is_selected():
    """An EMC cohort reached and survived a sarcoma diagnosis, so it is fitter than the
    population the effect was measured in. A multiplier of 1.0 would ignore that."""
    assert M.COMPARTMENT_TRANSFER["B"][1] <= 1.0
    assert M.COMPARTMENT_TRANSFER["B"][0] < 1.0


def test_a_factor_with_no_compartment_a_evidence_claims_nothing_there():
    row = _factor(evidence=[_ev("B", 0.10, 0.20)])
    out = M.model_factor(row, competing_share=0.394)
    assert out["compartments"]["A"]["status"] == "NO_EVIDENCE"
    assert out["compartments"]["A"]["relative_risk_reduction_range"] == [0.0, 0.0]
    assert out["compartments"]["B"]["status"] == "MODELLED"


def test_the_two_compartment_shares_sum_to_all_deaths():
    out = M.model_factor(_factor(), competing_share=0.394)
    a = out["compartments"]["A"]["share_of_all_deaths"]
    b = out["compartments"]["B"]["share_of_all_deaths"]
    assert a + b == pytest.approx(1.0)
    assert b == pytest.approx(0.394)


# ---------------------------------------------------------------------------
# The arithmetic
# ---------------------------------------------------------------------------
def test_the_exposed_patient_band_is_bounded_by_the_compartment_share():
    """A host factor acting only on non-EMC death cannot avert more than the non-EMC
    share of deaths, however good the drug is. This is the honest ceiling."""
    row = _factor(evidence=[_ev("B", 1.0, 1.0)])          # a perfect intervention
    out = M.model_factor(row, competing_share=0.394)
    hi = out["compartments"]["B"]["exposed_patient_share_of_deaths_averted_range"][1]
    assert hi <= 0.394 + 1e-9


def test_the_cohort_band_is_smaller_than_the_exposed_patient_band():
    """Only the exposed fraction can benefit, so a population figure must be the smaller
    of the two. Quoting the exposed-patient number as a population effect is the obvious
    way to overstate this."""
    row = _factor(prevalence_in_cohort=0.40, evidence=[_ev("B", 0.10, 0.20)])
    out = M.model_factor(row, competing_share=0.394)
    b = out["compartments"]["B"]
    assert b["cohort_share_of_deaths_averted_range"][1] < b["exposed_patient_share_of_deaths_averted_range"][1]


def test_prevalence_scales_the_cohort_effect_linearly():
    lo = M.model_factor(_factor(prevalence_in_cohort=0.20, evidence=[_ev("B", 0.1, 0.2)]), 0.4)
    hi = M.model_factor(_factor(prevalence_in_cohort=0.40, evidence=[_ev("B", 0.1, 0.2)]), 0.4)
    a = lo["compartments"]["B"]["cohort_share_of_deaths_averted_range"][1]
    b = hi["compartments"]["B"]["cohort_share_of_deaths_averted_range"][1]
    assert b == pytest.approx(2 * a, rel=1e-6)


# ---------------------------------------------------------------------------
# Bias discipline
# ---------------------------------------------------------------------------
def test_a_row_declaring_no_biases_is_flagged_as_unanalysed():
    """⚠ Silence about bias must not read as absence of bias. This is the row most likely
    to be quoted and least likely to be right."""
    out = M.model_factor(_factor(biases=[]), competing_share=0.394)
    assert "bias_declaration_missing" in out
    assert "not been analysed" in out["bias_declaration_missing"]


def test_declared_biases_are_carried_with_their_explanation():
    out = M.model_factor(_factor(biases=["reverse_causation"]), competing_share=0.394)
    names = [b["bias"] for b in out["biases_that_apply"]]
    assert "reverse_causation" in names
    assert "weight loss" in out["biases_that_apply"][0]["why_it_matters"]


def test_the_registry_names_the_bias_that_would_reverse_the_sign():
    """The obesity paradox is the specific failure that would make this analysis
    recommend weight gain to cancer patients. It must be nameable."""
    assert "obesity_paradox" in M.BIASES
    assert "reverse_causation" in M.BIASES
    assert "opposite" in M.BIASES["obesity_paradox"]


def test_every_bias_carries_a_usable_explanation():
    for name, text in M.BIASES.items():
        assert len(text) > 40, name


# ---------------------------------------------------------------------------
# The anchor gate
# ---------------------------------------------------------------------------
def _probe(pmids):
    return {"queries": {"q": {"hits": [{"pmid": p} for p in pmids]}}}


def test_an_unanchored_pmid_refuses_the_model():
    spec = {"factors": [_factor(evidence=[_ev("B", 0.1, 0.2, pmid="99999999")])]}
    problems = M.check_anchors(spec, _probe(["12345678"]))
    assert len(problems) == 1
    assert "recollection" in problems[0]


def test_an_anchored_pmid_passes():
    spec = {"factors": [_factor(evidence=[_ev("B", 0.1, 0.2, pmid="12345678")])]}
    assert M.check_anchors(spec, _probe(["12345678"])) == []


def test_an_unretrieved_evidence_row_anchors_nothing():
    ev = _ev("A", 0.0, 0.0, pmid=None, status="unretrieved")
    assert M.check_anchors({"factors": [_factor(evidence=[ev])]}, _probe([])) == []


# ---------------------------------------------------------------------------
# An association is not an intervention effect (AUT-220, 2026-09-04)
# ---------------------------------------------------------------------------
def _assoc(compartment, lo, hi, pmid="12345678"):
    return {"compartment": compartment, "status": "association_only", "pmid": pmid,
            "hazard_ratio_lo": lo, "hazard_ratio_hi": hi,
            "measured_in": "sarcoma patients, CT-defined sarcopenia", "endpoint": "overall survival"}


def test_an_association_only_row_claims_nothing_but_keeps_the_estimate_visible():
    out = M.model_factor(_factor(evidence=[_assoc("A", 1.09, 3.34)]), 0.4)
    a = out["compartments"]["A"]
    assert a["status"] == "ASSOCIATION_ONLY"
    assert a["association_hazard_ratio_range"] == [1.09, 3.34]
    assert a["relative_risk_reduction_range"] == [0.0, 0.0]
    assert a["cohort_share_of_deaths_averted_range"] == [0.0, 0.0]
    assert a["exposed_patient_share_of_deaths_averted_range"] == [0.0, 0.0]


def test_a_corroborating_row_outside_both_compartments_is_anchored_but_never_modelled():
    ev = [_ev("B", 0.05, 0.21, pmid="11111111"),
          {"compartment": "B_corroborating", "status": "retrieved", "pmid": "22222222",
           "note": "class-level pairwise reduction reported without a hazard ratio"}]
    out = M.model_factor(_factor(evidence=ev), 0.4)
    assert out["compartments"]["B"]["pmid"] == "11111111"
    assert set(out["compartments"]) == {"A", "B"}
    probe = {"queries": {"q": {"hits": [{"pmid": "11111111"}]}}}
    problems = M.check_anchors({"factors": [_factor(evidence=ev)]}, probe)
    assert any("22222222" in p for p in problems), "a corroborating PMID must still be anchor-checked"


def test_an_endpoint_caveat_is_carried_onto_the_modelled_row():
    out = M.model_factor(_factor(endpoint_caveat="cardiovascular death only", evidence=[_ev("B", 0.05, 0.29)]), 0.4)
    assert out["endpoint_caveat"] == "cardiovascular death only"
