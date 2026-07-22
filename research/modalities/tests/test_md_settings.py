#!/usr/bin/env python3
"""Enforce the single-source-of-truth MD hyperparameters (md_settings.py) across every lane. Pure stdlib.

These tests are the STRUCTURAL guard against the 2 fs-vs-4 fs drift that prompted md_settings.py: they pin the
canonical values (so any change is deliberate and shows up in a test diff), forbid the covalent driver from
re-hardcoding integration params, and assert the canonical values equal what the ValB/RBFE (OpenFE) lane runs.
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import md_settings as MD  # noqa: E402

_HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_canonical_values_pinned():
    # a change to any of these is a cross-lane physics change — it must be intentional (edit this test too)
    assert MD.TIMESTEP_FS == 4.0
    assert MD.HYDROGEN_MASS_AMU == 3.0
    assert MD.CONSTRAINTS == "HBonds" and MD.RIGID_WATER is True
    assert MD.TEMPERATURE_K == 300.0 and MD.FRICTION_PER_PS == 1.0
    assert MD.NONBONDED_CUTOFF_NM == 0.9
    assert MD.PROTEIN_FORCEFIELDS == ("amber14-all.xml", "amber14/tip3p.xml")
    assert MD.SMALL_MOLECULE_FORCEFIELD == "gaff-2.11" and MD.WATER_MODEL == "tip3p"
    assert MD.SOLVENT_PADDING_NM == 1.0 and MD.IONIC_STRENGTH_M == 0.15
    assert MD.EQUIL_NS == 1.0 and MD.PROD_NS == 5.0 and MD.FRAME_STRIDE_PS == 10.0


def test_derived_are_consistent():
    assert MD.TIMESTEP_PS == 0.004 and MD.TIMESTEP_NS == 4e-6
    assert MD.frame_stride_steps() == 2500          # 10 ps / 4 fs
    s = MD.summary()
    assert s["timestep_fs"] == 4.0 and s["hydrogen_mass_amu"] == 3.0 and "single source of truth" in s["_source"]


def test_rbfe_matches_canonical():
    # The ValB/RBFE lane runs OpenFE production defaults: 4 fs timestep + 3.0 amu H-mass. The canonical constants
    # MUST equal those so the endpoint-MD and alchemical lanes are directly comparable. (OpenFE sets these via its
    # own Settings objects; this test pins the shared expectation both lanes are held to.)
    OPENFE_PRODUCTION_TIMESTEP_FS = 4.0
    OPENFE_PRODUCTION_HYDROGEN_MASS_AMU = 3.0
    assert MD.TIMESTEP_FS == OPENFE_PRODUCTION_TIMESTEP_FS
    assert MD.HYDROGEN_MASS_AMU == OPENFE_PRODUCTION_HYDROGEN_MASS_AMU


def test_covalent_driver_does_not_re_hardcode_integration():
    """The covalent MD driver must SOURCE its integration/FF params from md_settings, never hardcode them — that
    per-driver hardcoding is exactly how the 2 fs drift happened."""
    src = open(os.path.join(_HERE, "nrv04_covalent_md.py")).read()
    assert "import md_settings" in src, "covalent driver must import md_settings"
    # no raw timestep literal in a LangevinMiddleIntegrator, and no hardcoded hydrogenMass
    assert not re.search(r"LangevinMiddleIntegrator\([^)]*femto|LangevinMiddleIntegrator\([^)]*0\.00\d", src), \
        "integrator must come from md_settings.openmm_integrator(), not a hardcoded timestep"
    assert "hydrogenMass" not in src, "hydrogenMass must come from md_settings.systemgenerator_forcefield_kwargs()"
