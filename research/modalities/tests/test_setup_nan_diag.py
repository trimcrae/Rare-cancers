"""The pre-MD (`sampler.setup()`) NaN diagnostic: pair classification + the BLOCK/RETRY verdict.

WHY THESE TESTS EXIST (2026-07-27). Step 1 fan-out unit
`e_zaienne_cmpd19__cw_bio_primary_amide__neutral__neutral` lost its complex leg to
`openmm.OpenMMException: Particle coordinate is NaN` raised inside `LocalEnergyMinimizer` during
`sampler.setup()` — i.e. before any MD. The decision it forces is binary and expensive in both
directions: BLOCK the unit (stop renting a fresh host every tick, forever) or RETRY it (a block
would retire a viable edge on a wrong diagnosis). The leg's own `[clash-diag:initial]` block could
not decide it, and worse, two of its statements were wrong in ways that pointed AWAY from a
diagnosis:

  * four ligand pairs at 1.375-1.399 A — aromatic C-C BOND lengths — were reported as `non-bonded`,
    because `_bonded_pairs` read only `HarmonicBondForce` and OpenFE's hybrid topology puts the
    alchemically-transforming bonds in a `CustomBondForce`;
  * a pair at **d=0.000 A** was labelled `EXCLUDED-hybrid(benign)` on the strength of a zeroed
    `NonbondedForce` exception alone, while nothing had checked whether the alchemical
    `CustomNonbondedForce` terms still couple it — and r=0 in those is exactly where a softcore
    expression goes non-finite.

The classification logic and the verdict are therefore pure functions, pinned here. The
OpenMM-touching parts (`_bonded_pairs`, `_custom_nb_exclusions`, `_force_energy_probe`) are
exercised on the leg itself; what must never regress silently is the RULE.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import rbfe_spot_driver as drv  # noqa: E402


# ---- _pair_verdict ----------------------------------------------------------------------------
def test_pair_absent_from_exceptions_is_force_bearing():
    fb, label = drv._pair_verdict(10, 20, exc={}, n_custom_nb=2, custom_excl=set())
    assert fb is True
    assert label == "FORCE-BEARING(real clash)"


def test_pair_with_nonzero_exception_is_force_bearing():
    exc = {(10, 20): (0.5, 0.0)}
    fb, label = drv._pair_verdict(20, 10, exc=exc, n_custom_nb=0, custom_excl=set())
    assert fb is True
    assert label.startswith("exception(")


def test_zeroed_exception_with_no_custom_forces_keeps_the_old_two_way_answer():
    # A plain, non-alchemical system has no CustomNonbondedForce; behaviour must be unchanged.
    exc = {(10, 20): (0.0, 0.0)}
    fb, label = drv._pair_verdict(10, 20, exc=exc, n_custom_nb=0, custom_excl=set())
    assert fb is False
    assert label == "EXCLUDED-hybrid(benign)"


def test_zeroed_exception_still_seen_by_a_custom_force_is_force_bearing():
    # THE DEFECT THIS PINS: the 0.000 A pair was called benign without consulting these.
    exc = {(4052, 4054): (0.0, 0.0)}
    fb, label = drv._pair_verdict(4052, 4054, exc=exc, n_custom_nb=3, custom_excl=set())
    assert fb is True
    assert "CustomNonbondedForce" in label
    assert "3 custom nonbonded force(s)" in label


def test_zeroed_exception_excluded_everywhere_is_benign():
    exc = {(4052, 4054): (0.0, 0.0)}
    fb, label = drv._pair_verdict(4054, 4052, exc=exc, n_custom_nb=3, custom_excl={(4052, 4054)})
    assert fb is False
    assert label == "EXCLUDED-everywhere(benign)"


def test_pair_verdict_is_order_independent():
    exc = {(7, 9): (0.0, 0.0)}
    assert drv._pair_verdict(7, 9, exc, 2, {(7, 9)}) == drv._pair_verdict(9, 7, exc, 2, {(7, 9)})


# ---- energy_probe_verdict ---------------------------------------------------------------------
def _row(force, e):
    return {"group": 0, "force": force, "energy_kj_mol": e, "finite": math.isfinite(e)}


def test_non_finite_force_term_says_BLOCK():
    rows = [_row("NonbondedForce", -1.2e6), _row("CustomNonbondedForce", float("inf"))]
    v = drv.energy_probe_verdict(rows, float("inf"))
    assert "DETERMINISTIC" in v
    assert "BLOCK the unit, do not retry" in v
    assert "CustomNonbondedForce" in v


def test_nan_force_term_is_caught_as_well_as_inf():
    rows = [_row("CustomBondForce", float("nan"))]
    assert "BLOCK the unit" in drv.energy_probe_verdict(rows, float("nan"))


def test_all_finite_says_RETRY():
    rows = [_row("HarmonicBondForce", 1234.5), _row("NonbondedForce", -987654.0)]
    v = drv.energy_probe_verdict(rows, -986419.5)
    assert "RETRY candidate" in v
    assert "BLOCK" not in v
    assert "987654" in v            # the max |E| is quoted, so the reading is auditable


def test_finite_groups_but_non_finite_total_still_says_BLOCK():
    rows = [_row("NonbondedForce", 1e308), _row("CustomNonbondedForce", 1e308)]
    assert "BLOCK the unit, do not retry" in drv.energy_probe_verdict(rows, float("inf"))


def test_empty_probe_is_INCONCLUSIVE_and_never_a_retry_licence():
    # A probe that measured nothing must not read as "everything was fine" — that is the exact
    # shape (a guard reporting success while measuring nothing) this repo keeps paying for.
    v = drv.energy_probe_verdict([], 0.0)
    assert "INCONCLUSIVE" in v
    assert "RETRY candidate" not in v
    assert "BLOCK" not in v


# ---- the probe is an evidence hook, never a recovery path -------------------------------------
def test_force_energy_probe_is_non_fatal_without_openmm():
    logs = []
    # `system`/`positions` are deliberately nonsense: the probe must swallow its own failure and
    # return an empty row list rather than converting a diagnosis into a second outage.
    assert drv._force_energy_probe(object(), object(), logs.append, "unit-test") == []
    assert any("force-diag:unit-test" in m for m in logs)


def test_setup_nan_handler_calls_the_probe_and_reraises():
    """The `except` around `_get_sampler` must DIAGNOSE and then RE-RAISE — a swallowed setup NaN
    would turn a hard failure into a silent one, and the leg has produced nothing to keep."""
    src = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                            "rbfe_spot_driver.py")).read()
    block = src.split("THE SETUP MINIMISER CAN NaN TOO", 1)[1].split("_set_caches", 1)[0]
    assert '_clash_report(positions, system, log, "setup_nan")' in block
    assert '_force_energy_probe(system, positions, log, "setup_nan")' in block
    assert "\n        raise\n" in block


def test_hmrdiag_energy_probe_is_opt_in_and_non_fatal():
    """The free CPU reproduction runs the SAME probe from `nr4a3_rbfe`'s HMRDIAG exit, under
    RBFE_ENERGY_PROBE=1. It must be opt-in (so the timestep scan is unchanged) and must never be
    able to break the build it is diagnosing."""
    src = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                            "nr4a3_rbfe.py")).read()
    assert 'os.environ.get("RBFE_ENERGY_PROBE") == "1"' in src
    blk = src.split('RBFE_ENERGY_PROBE', 1)[1].split("RBFE_HMRDIAG_ONLY=1 -> exiting", 1)[0]
    assert "_drv._force_energy_probe(system, positions" in blk
    assert "energy_probe_verdict" in blk
    assert "except Exception as _pe" in blk
