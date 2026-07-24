"""Tests for the 5a-KS protein-mutation wedge engine (nr4a3_protein_fep.py).

These run on CPU with no MD stack — the engine's pure planning/arithmetic/guard layer is separated
from its perses entry points precisely so the guards are testable in CI on every push.

The two guards that matter most here are the ones that correspond to the wedge's two real blockers:
the cross-lane charge mismatch, and net-charge-changing mutations. Both are tested for REFUSAL,
because in both cases the failure mode is a plausible-looking number rather than a crash.
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import nr4a3_protein_fep as pf  # noqa: E402


# ---------------------------------------------------------------- parsing
def test_parse_basic():
    m = pf.parse_mutation("A:R412A")
    assert m["chain"] == "A"
    assert m["resid"] == 412
    assert m["wt"] == "ARG"
    assert m["mutant"] == "ALA"


def test_parse_multidigit_and_lowercase():
    m = pf.parse_mutation("B:l406a")
    assert (m["chain"], m["resid"], m["wt"], m["mutant"]) == ("B", 406, "LEU", "ALA")


@pytest.mark.parametrize("bad", ["R412A", "A:R412", "A:RXA", "A:Z412A", "A:R412Z", ":R412A", "", None, 42])
def test_parse_rejects_malformed(bad):
    with pytest.raises(pf.MutationError):
        pf.parse_mutation(bad)


def test_null_mutation_refused():
    # A wedge on a null mutation is identically zero -- it would look like a clean null result.
    with pytest.raises(pf.MutationError, match="null mutation"):
        pf.parse_mutation("A:L406L")


# ---------------------------------------------------------------- charge classification
def test_charge_conserving_hydrophobic():
    m = pf.classify_mutation("A:L406A")
    assert m["charge_change"] == 0
    assert not m["charge_changing"]
    assert m["buildable"]


def test_r412a_is_flagged_charge_changing():
    # R412 is one of the repo's own seven selectivity handles, so this is the default trap.
    m = pf.classify_mutation("A:R412A")
    assert m["charge_change"] == -1
    assert m["charge_changing"]
    assert "CHARGE-CHANGING" in m["risk"]


@pytest.mark.parametrize("spec,dq", [("A:D481A", +1), ("A:E100A", +1), ("A:K200A", -1), ("A:A100R", +1)])
def test_charge_change_signs(spec, dq):
    assert pf.classify_mutation(spec)["charge_change"] == dq


@pytest.mark.parametrize("spec", ["A:P411A", "A:L406P", "A:G100A", "A:L406G"])
def test_backbone_altering_refused(spec):
    m = pf.classify_mutation(spec)
    assert not m["buildable"]
    with pytest.raises(pf.MutationError):
        pf.plan_wedge(spec)


# ---------------------------------------------------------------- blocker 1: charge consistency
def test_charge_mismatch_hard_fails():
    # The exact split md_settings.py registers as a DOCUMENTED DEVIATION between lanes.
    with pytest.raises(pf.MutationError, match="CROSS-LANE CHARGE MISMATCH"):
        pf.assert_charge_consistency("nagl", "am1bcc")


def test_charge_consistency_passes_when_pinned():
    assert pf.assert_charge_consistency("NAGL", "nagl") == "nagl"


@pytest.mark.parametrize("t,b", [("", "nagl"), ("nagl", ""), (None, "nagl"), ("nagl", None)])
def test_unrecorded_charge_method_refused(t, b):
    with pytest.raises(pf.MutationError):
        pf.assert_charge_consistency(t, b)


def test_summarize_refuses_mismatched_legs():
    with pytest.raises(pf.MutationError, match="CROSS-LANE CHARGE MISMATCH"):
        pf.summarize_wedge([1.0, 1.2, 1.1], [0.4, 0.5, 0.3], "nagl", "am1bcc", "A:L406A")


# ---------------------------------------------------------------- blocker 2: charge-changing plans
def test_charge_changing_wedge_refused_by_default():
    with pytest.raises(pf.MutationError, match="charge-changing"):
        pf.plan_wedge("A:R412A")


def test_charge_changing_still_refused_with_none_correction():
    with pytest.raises(pf.MutationError, match="not a legitimate"):
        pf.plan_wedge("A:R412A", allow_charge_change=True, charge_correction="none")


def test_charge_changing_allowed_with_explicit_correction():
    p = pf.plan_wedge("A:R412A", allow_charge_change=True, charge_correction="coalchemical_ion")
    assert p["charge_correction"] == "coalchemical_ion"
    assert p["mutation"]["charge_changing"]


def test_unnecessary_correction_on_neutral_mutation_refused():
    with pytest.raises(pf.MutationError, match="unnecessary"):
        pf.plan_wedge("A:L406A", charge_correction="coalchemical_ion")


# ---------------------------------------------------------------- planning
def test_plan_shape():
    p = pf.plan_wedge("A:I484A", n_replicas=3)
    assert p["n_legs"] == 6
    envs = [leg["environment"] for leg in p["legs"]]
    assert envs.count("ternary") == 3 and envs.count("binary") == 3
    assert len({leg["leg_id"] for leg in p["legs"]}) == 6
    # Every leg must carry the charge method, or the wedge is unauditable after the fact.
    assert all(leg["charge_method"] for leg in p["legs"])


def test_plan_defaults_to_md_settings_charge_method():
    import md_settings
    assert pf.plan_wedge("A:I484A")["charge_method"] == md_settings.CHARGE_METHOD.lower()


def test_single_replicate_refused():
    # One leg gives no between-replicate SD.
    with pytest.raises(pf.MutationError, match="n_replicas"):
        pf.plan_wedge("A:I484A", n_replicas=1)


def test_plan_is_unvalidated():
    # The engine must advertise that it has never completed a leg.
    assert pf.plan_wedge("A:I484A")["validated"] is False


# ---------------------------------------------------------------- the cycle
def test_wedge_matches_ternary_coop_cycle():
    import ternary_coop as tcoop
    assert pf.wedge_ddg(3.0, 1.0) == tcoop.ddg_coop(3.0, 1.0)


def test_summarize_arithmetic():
    r = pf.summarize_wedge([3.0, 3.0, 3.0], [1.0, 1.0, 1.0], "nagl", "nagl", "A:L406A")
    assert r["ddg_neo_interface_kcal"] == pytest.approx(2.0)
    assert r["ddg_neo_interface_sd"] == pytest.approx(0.0)
    assert r["n_ternary"] == 3 and r["n_binary"] == 3


def test_summarize_sd_adds_in_quadrature():
    r = pf.summarize_wedge([1.0, 3.0], [10.0, 12.0], "nagl", "nagl", "A:L406A")
    # Each environment has SD sqrt(2); quadrature sum is 2.0.
    assert r["ddg_neo_interface_sd"] == pytest.approx(2.0)
    assert "between-replicate SD" in r["error_model"]


def test_summarize_requires_two_replicates():
    with pytest.raises(pf.MutationError, match=">= 2 completed replicates"):
        pf.summarize_wedge([1.0], [0.5, 0.6], "nagl", "nagl", "A:L406A")


def test_null_result_is_reported_as_killswitch_firing():
    # Wedge well inside its own error bar -- the kill-switch's whole purpose.
    r = pf.summarize_wedge([1.0, 3.0, 2.0], [1.1, 2.9, 2.1], "nagl", "nagl", "A:L406A")
    assert "KILL-SWITCH FIRING" in r["interpretation"]


def test_positive_wedge_is_conditional_not_proof():
    r = pf.summarize_wedge([5.0, 5.1, 4.9], [1.0, 1.1, 0.9], "nagl", "nagl", "A:L406A")
    assert r["ddg_neo_interface_kcal"] == pytest.approx(4.0, abs=0.1)
    assert "CONDITIONAL" in r["interpretation"]
    assert "proof" not in r["interpretation"].lower() or "not proof" in r["interpretation"].lower()


# ---------------------------------------------------------------- benchmark gate
def test_benchmark_plan_is_charge_conserving_throughout():
    # The first benchmark must not confound engine error with the charge artifact.
    bp = pf.benchmark_plan()
    assert len(bp["benchmarks"]) == len(pf.KNOWN_ANSWER_BENCHMARKS)
    for p in bp["benchmarks"]:
        assert not p["mutation"]["charge_changing"], f"{p['mutation']['spec']} is charge-changing"


def test_benchmark_plan_states_the_gate():
    bp = pf.benchmark_plan()
    assert "may not contribute a number to the manuscript" in bp["gate"]
    assert "ordering" in bp["pass_criterion"]


# ---------------------------------------------------------------- CLI
def test_cli_refuses_charge_changing_with_exit_1(capsys):
    assert pf.main(["--plan", "A:R412A"]) == 1
    assert "REFUSED" in capsys.readouterr().err


def test_cli_plans_valid_wedge(capsys):
    import json
    assert pf.main(["--plan", "A:L406A"]) == 0
    assert json.loads(capsys.readouterr().out)["n_legs"] == 6
