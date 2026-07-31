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
    """Both use the physical boundary, not a tuned cut — a minimised solvated system is always negative."""
    import nrv04_vast_launch as vl
    assert probe.NONPHYSICAL_PE_KJ == 0.0
    assert vl._NONPHYSICAL_PE_KJ == probe.NONPHYSICAL_PE_KJ, (
        "the quarantine and the probe must not disagree about what counts as non-physical")


def test_the_default_units_pair_the_failing_input_with_a_working_control():
    """A probe run on the broken input alone cannot say which stage is ABNORMAL."""
    import argparse
    ap = argparse.ArgumentParser()
    src = inspect.getsource(probe.main)
    assert "nr4a3:3,nr4a3:1" in src, "the failing seed and its working sibling must both be the default"
    del ap, argparse


def test_a_stage_that_cannot_be_priced_is_unknown_not_physical():
    src = inspect.getsource(probe.probe_unit)
    assert '"physical": None' in src, "an unreadable stage must never be recorded as physical"


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
