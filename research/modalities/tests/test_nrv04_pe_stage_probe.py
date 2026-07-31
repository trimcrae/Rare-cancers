#!/usr/bin/env python3
"""The stage probe measures the PRODUCTION build path, and its boundary is the physical one.

Context: the inter-chain-distance gate this replaced was refuted by its own first run
(nrv04_cofold_audit.CLASH_MIN_INTERCHAIN_A). The lesson pinned here is that the replacement must not be a
re-implementation of the builder — a probe that rebuilds the stages itself can drift from the real pipeline
and then answer confidently about something nobody runs.
"""
import inspect
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

import nrv04_pe_stage_probe as probe  # noqa: E402


def test_the_probe_hooks_the_real_builder_rather_than_reimplementing_it():
    import nrv04_covalent_md as md
    assert "stage_probe" in inspect.signature(md.build_system).parameters
    src = inspect.getsource(md.build_system)
    # The three stages the diagnosis turns on, in the production builder itself.
    for stage in ("protein_after_pdbfixer", "protein_plus_ligand", "solvated"):
        assert stage in src, f"{stage} is not probed in the real build path"
    assert "build_system(" in inspect.getsource(probe.probe_unit)


def test_the_probe_is_inert_for_a_real_leg():
    """Every production leg passes stage_probe=None, so this costs nothing and cannot change a result."""
    import nrv04_covalent_md as md
    assert inspect.signature(md.build_system).parameters["stage_probe"].default is None
    src = inspect.getsource(md.build_system)
    assert src.count("if stage_probe:") == 3, "each stage must be guarded, so None does no work"


def test_the_boundary_is_zero_and_agrees_with_the_quarantine():
    """Both use the physical boundary, not a tuned cut — a MINIMISED solvated system is always negative."""
    import nrv04_vast_launch as vl
    assert probe.NONPHYSICAL_PE_KJ == 0.0
    assert vl._NONPHYSICAL_PE_KJ == probe.NONPHYSICAL_PE_KJ, (
        "the quarantine and the probe must not disagree about what counts as non-physical")


#: The measured stage energies, 2026-07-31 4:20 PM ET. Held here so the classifier is exercised against the
#: real observation rather than invented numbers — an invariance claim about made-up data proves nothing.
_MEASURED_SUBJECT = {"system": "nr4a3", "seed": 3, "stages": [
    {"stage": "protein_after_pdbfixer", "n_atoms": 10914, "pe_kj_per_mol": 2.109005036357692e+15},
    {"stage": "protein_plus_ligand", "n_atoms": 11080, "pe_kj_per_mol": 2.109005036360151e+15},
    {"stage": "solvated", "n_atoms": 316243, "pe_kj_per_mol": 2.108844375741770e+15}]}
_MEASURED_CONTROL = {"system": "nr4a3", "seed": 1, "stages": [
    {"stage": "protein_after_pdbfixer", "n_atoms": 10914, "pe_kj_per_mol": 2.522674e+05},
    {"stage": "protein_plus_ligand", "n_atoms": 11080, "pe_kj_per_mol": 2.606874e+05},
    {"stage": "solvated", "n_atoms": 329820, "pe_kj_per_mol": -3.740431e+06}]}


def test_no_per_stage_physical_verdict_survives_anywhere():
    """⛔ THE ZERO BOUNDARY CALLED THE HEALTHY CONTROL BROKEN, and that must not come back.

    `PE <= 0` is meaningful only for a MINIMISED SOLVATED system. No probe stage is minimised and two are not
    solvated, so the control's perfectly ordinary +2.5e5 at `protein_after_pdbfixer` was reported as the
    stage where its energy 'first goes non-physical'. Same class of error as reporting `solvated` off two
    stages that had RAISED: a summary line that contradicted the table above it.
    """
    src = inspect.getsource(probe.probe_unit)
    assert '"physical"' not in src, "a probe stage records a MEASUREMENT, not a verdict"
    assert "NONPHYSICAL_PE_KJ" not in src, "the post-minimisation boundary must not be applied to a stage"
    assert not hasattr(probe, "first_nonphysical_stage")


def test_the_verdict_is_comparative_and_names_the_measured_stage():
    got = probe.compare_to_control(_MEASURED_SUBJECT, _MEASURED_CONTROL)
    assert got["first_divergent_stage"] == "protein_after_pdbfixer", (
        "the energy is already 1e15 before the ligand exists and before one water is placed")
    rows = {r["stage"]: r for r in got["stages"]}
    assert round(rows["protein_after_pdbfixer"]["decades_above_control"], 1) == 9.9
    # Ligand placement and solvation are EXONERATED: they do not introduce the divergence, they inherit it.
    assert rows["protein_plus_ligand"]["status"] == "DIVERGENT"
    assert rows["solvated"]["status"] == "DIVERGENT"
    assert rows["solvated"]["sign_flip"] is True, "control goes negative on solvation; the subject does not"
    # ★ THE READING THAT DECIDES THE LANE: the divergence is in the earliest thing built, so it is the INPUT.
    assert "property of the INPUT, not of the build" in got["verdict"], got["verdict"]


def test_the_verdict_is_invariant_across_the_threshold():
    """★★ WHAT MAKES THIS A SEPARATOR AND NOT THE RETIRED GEOMETRY CUT.

    The 1.5 A inter-chain gate was refuted because ground truth straddled it. Here the separation is ~10
    decades, so the answer does not move across four orders of magnitude of the threshold's own value. If a
    future observation ever makes the verdict threshold-sensitive, this fails and the measure needs the same
    scrutiny the geometry one got — rather than a quiet re-tune.
    """
    answers = {probe.compare_to_control(_MEASURED_SUBJECT, _MEASURED_CONTROL,
                                        decades=float(d))["first_divergent_stage"]
               for d in range(1, 9)}
    assert answers == {"protein_after_pdbfixer"}, answers
    assert 1.0 < probe.DIVERGENCE_DECADES < 9.0


def test_a_stage_missing_from_either_side_is_unknown_not_a_verdict():
    """CLAUDE.md §4b — an absent reading is not a reading of absence, in the classifier too."""
    subj = {"system": "x", "seed": 1, "stages": [
        {"stage": "protein_after_pdbfixer", "pe_kj_per_mol": None, "error": "boom"},
        {"stage": "solvated", "pe_kj_per_mol": 1e15}]}
    ctl = {"system": "x", "seed": 2, "stages": [{"stage": "solvated", "pe_kj_per_mol": -4e6}]}
    got = probe.compare_to_control(subj, ctl)
    rows = {r["stage"]: r for r in got["stages"]}
    assert rows["protein_after_pdbfixer"]["decades_above_control"] is None
    assert rows["protein_after_pdbfixer"]["status"].startswith("unknown")
    # An unreadable EARLIER stage must not let a later one claim to be where divergence STARTED.
    assert got["first_divergent_stage"] == "solvated"
    assert "an EARLIER origin is not excluded" in got["verdict"], got["verdict"]
    assert "every stage BEFORE it is consistent" not in got["verdict"]
    assert probe.compare_to_control({"stages": []}, ctl)["verdict"].startswith("NO COMPARISON POSSIBLE")


def test_the_default_units_pair_the_failing_input_with_a_working_control():
    """A probe run on the broken input alone cannot say which stage is ABNORMAL."""
    import argparse
    ap = argparse.ArgumentParser()
    src = inspect.getsource(probe.main)
    assert "nr4a3:3,nr4a3:1" in src, "the failing seed and its working sibling must both be the default"
    del ap, argparse


def test_a_stage_that_cannot_be_priced_records_no_energy_and_says_why():
    src = inspect.getsource(probe.probe_unit)
    assert '"pe_kj_per_mol": None' in src, "an unreadable stage must never carry a fabricated energy"
    assert '"error":' in src, "and it must say what stopped it"


def test_pre_solvation_stages_are_priced_without_a_cutoff():
    """The probe's own first run measured NOTHING before solvation, and that is not a result.

    `sysgen.create_system` applies the production PME + 0.9 nm cutoff, which needs a periodic box at least
    twice the cutoff. An unsolvated topology has none, so both pre-solvation stages raised
    "cutoff distance cannot be greater than half the periodic box size" for the FAILING unit and the CONTROL
    alike — making `first_nonphysical_stage=solvated` an artifact of unmeasurability, not evidence about
    solvation. CLAUDE.md §4b: an absent reading is not a reading of absence.
    """
    src = inspect.getsource(probe.single_point_kj)
    assert "NoCutoff" in src
    assert 'periodic=(name == "solvated")' in inspect.getsource(probe.probe_unit), (
        "only the solvated stage may be priced periodically")


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-v"]))
