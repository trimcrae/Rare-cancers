#!/usr/bin/env python3
"""
CANONICAL MD hyperparameters — the SINGLE SOURCE OF TRUTH every MD/FEP lane is measured against.

WHY THIS FILE EXISTS (2026-07-22): the covalent endpoint-MD lane was silently running a 2 fs timestep with NO
hydrogen-mass repartitioning while the ValB/RBFE (OpenFE) lane ran 4 fs + 3.0 amu HMR — an inconsistency that
only surfaced by manual inspection and would have made the two lanes' MD non-comparable. Physics
hyperparameters MUST be defined ONCE and imported everywhere, so every test uses the same integration +
force-field settings and drift between lanes is structurally impossible.

These values match OpenFE's production defaults (what the RBFE lane runs). **Changing a value here changes ALL
lanes that import it, at once — that is the point.** Any lane that needs to deviate must do so EXPLICITLY and say
why in its own code, next to the override.

SCOPE OF WHAT SHARING THESE BUYS (be precise — do NOT overclaim a validation link):
  - This is ENGINE HYGIENE, not validation transfer. Sharing the integrator/FF means the MD lanes use the same
    simulation engine so nothing is *gratuitously* incomparable and there are no unexplained knobs to defend.
  - It does NOT mean the covalent endpoint-MD lane "inherits" ValB's validation. ValB (the known-answer ternary
    RBFE edge) validates ONE thing — the *free-energy / cooperativity* method — and its only hard dependent that
    MUST be physics-identical is the NR4A prospective RBFE matrix (calibration -> application). The covalent
    endpoint-MD panel computes NO free energies (it reports geometric interface readouts R1-R4), so ValB does not
    validate it; its validity rests on its OWN biological known-answer control (NR-V04 degrades NR4A1, spares
    NR4A2/3). The covalent panel keeps 4 fs purely as the shared-engine default, not as evidence borrowed from ValB.

Consumers (import from here, do NOT re-specify):
  - nrv04_covalent_md.py            (covalent/noncovalent endpoint MD)  — MIGRATED
  - nr4a3_md.py / nr4a3_md_release.py (unbiased/pocket + metad release) — DOCUMENTED DEVIATION (distinct apo
        cryptic-pocket experiment at 310 K / 2 fs / no HMR; NOT in the comparison chain — see the explicit
        deviation note next to each integrator). Parked/complete; a re-run would adopt these canonical values.
  - nr4a3_rbfe.py / rbfe_spot_driver.py (OpenFE alchemical)            — sets OpenFE Settings objects, not raw
        OpenMM; it cannot import openmm_integrator(), but its timestep/H-mass/FF MUST equal the constants below
        (asserted by tests/test_md_settings.py::test_rbfe_matches_canonical).

Pure-constant module: the constants have no dependencies; the OpenMM builder helpers import openmm lazily so a
CPU/CI context can read the constants without the MD stack installed.
"""
from __future__ import annotations

# ---- integration (matches OpenFE production defaults) -----------------------------------------------------
TIMESTEP_FS = 4.0                 # 4 fs, made stable by HMR + all-X-H (HBonds) constraints
HYDROGEN_MASS_AMU = 3.0           # H-mass repartition (OpenFE default)
CONSTRAINTS = "HBonds"            # constrain every X-H bond
RIGID_WATER = True
TEMPERATURE_K = 300.0
FRICTION_PER_PS = 1.0             # LangevinMiddle collision rate

# ---- nonbonded / force field ------------------------------------------------------------------------------
NONBONDED_CUTOFF_NM = 0.9
PROTEIN_FORCEFIELDS = ("amber14-all.xml", "amber14/tip3p.xml")
SMALL_MOLECULE_FORCEFIELD = "gaff-2.11"
WATER_MODEL = "tip3p"

# ---- solvation --------------------------------------------------------------------------------------------
SOLVENT_PADDING_NM = 1.0
IONIC_STRENGTH_M = 0.15

# ---- sampling lengths (endpoint MD) -----------------------------------------------------------------------
EQUIL_NS = 1.0
PROD_NS = 5.0
FRAME_STRIDE_PS = 10.0

# ---- derived ----------------------------------------------------------------------------------------------
TIMESTEP_PS = TIMESTEP_FS / 1000.0
TIMESTEP_NS = TIMESTEP_FS / 1e6


def openmm_integrator(seed=None):
    """The canonical LangevinMiddle integrator. Lazy openmm import so the constants stay dependency-free."""
    from openmm import LangevinMiddleIntegrator, unit
    integ = LangevinMiddleIntegrator(TEMPERATURE_K * unit.kelvin,
                                     FRICTION_PER_PS / unit.picosecond,
                                     TIMESTEP_PS * unit.picoseconds)
    if seed is not None:
        integ.setRandomNumberSeed(int(seed))
    return integ


def systemgenerator_forcefield_kwargs():
    """Canonical OpenMM createSystem kwargs (constraints + HMR + cutoff), shared by every endpoint-MD leg."""
    from openmm import app, unit
    return {"constraints": app.HBonds, "rigidWater": RIGID_WATER,
            "hydrogenMass": HYDROGEN_MASS_AMU * unit.amu,
            "nonbondedCutoff": NONBONDED_CUTOFF_NM * unit.nanometer}


def frame_stride_steps():
    """Frames every FRAME_STRIDE_PS, expressed in integration steps (timestep-independent)."""
    return max(1, int(round(FRAME_STRIDE_PS / TIMESTEP_PS)))


def summary():
    """A dict of the canonical settings — stamp it into every result JSON so each run RECORDS the exact
    hyperparameters it used (audit trail; makes any future drift visible in the outputs themselves)."""
    return {
        "timestep_fs": TIMESTEP_FS, "hydrogen_mass_amu": HYDROGEN_MASS_AMU, "constraints": CONSTRAINTS,
        "rigid_water": RIGID_WATER, "temperature_K": TEMPERATURE_K, "friction_per_ps": FRICTION_PER_PS,
        "nonbonded_cutoff_nm": NONBONDED_CUTOFF_NM, "protein_forcefields": list(PROTEIN_FORCEFIELDS),
        "small_molecule_forcefield": SMALL_MOLECULE_FORCEFIELD, "water_model": WATER_MODEL,
        "solvent_padding_nm": SOLVENT_PADDING_NM, "ionic_strength_M": IONIC_STRENGTH_M,
        "equil_ns": EQUIL_NS, "prod_ns": PROD_NS, "frame_stride_ps": FRAME_STRIDE_PS,
        "_source": "md_settings.py (canonical single source of truth)",
    }
