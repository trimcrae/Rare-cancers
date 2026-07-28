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


def test_all_finite_energies_AND_a_finite_gradient_says_RETRY():
    rows = [_row("HarmonicBondForce", 1234.5), _row("NonbondedForce", -987654.0)]
    v = drv.energy_probe_verdict(rows, -986419.5,
                                 grad={"n_nonfinite": 0, "max_kj_mol_nm": 4.2e4, "argmax": 17})
    assert "RETRY candidate" in v
    assert "BLOCK" not in v
    assert "987654" in v            # the max |E| is quoted, so the reading is auditable


# ---- ★★ THE CORRECTION THAT COST 25 RENTALS (2026-07-28) --------------------------------------
# This block replaces `test_all_finite_says_RETRY`, which asserted that all-finite ENERGIES alone
# licence a retry. That assertion was the rule the lane followed for `cw_bio_primary_amide`, and it
# re-placed that unit 25 times across 7 distinct card/driver combinations, every attempt dying at the
# same `LocalEnergyMinimizer.minimize` call (`step1-nan-forensics.json`). The rule was not merely
# unlucky — it was measuring the wrong quantity: a minimiser descends the DERIVATIVE, and a pair of
# atoms at exactly coincident coordinates keeps every energy finite while leaving the derivative
# undefined. SUPERSEDED, retained for the record: "every force term is FINITE ... RETRY candidate,
# not a block candidate" spoken with no gradient reading attached.
def test_finite_energies_with_a_NON_FINITE_gradient_is_never_a_retry():
    rows = [_row("HarmonicBondForce", 1234.5), _row("NonbondedForce", -987654.0)]
    v = drv.energy_probe_verdict(rows, -986419.5, grad={"n_nonfinite": 2, "top": [{"atom": 4052}]})
    assert "RETRY" not in v
    assert "DETERMINISTIC" in v
    assert "Do not rent another one" in v


def test_no_gradient_reading_is_HALF_MEASURED_and_not_a_retry_licence():
    # The default call (no `grad`) is exactly the shape that produced the wrong answer, so it must no
    # longer be speakable as RETRY. "We did not ask" and "we asked and it was fine" are different states.
    v = drv.energy_probe_verdict([_row("NonbondedForce", -1.0e6)], -1.0e6)
    assert "HALF-MEASURED" in v
    assert "RETRY candidate" not in v
    assert "BLOCK" not in v


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


# ---- coordinate degeneracy: detection --------------------------------------------------------
# WHY THIS IS A SEPARATE CONCEPT FROM A CLASH, AND WHY THAT DISTINCTION IS THE WHOLE FIX. The clash
# report asks "is this pair close enough to push on each other?", classifies an excluded coincident
# pair as benign, and is RIGHT to: excluded pairs exert no direct nonbonded force. The minimiser does
# not care. It differentiates, and r = 0 has no derivative whether or not the pair is excluded.
def test_coincident_pairs_finds_an_exactly_duplicated_coordinate():
    pos = [[0.0, 0.0, 0.0], [1.0, 1.0, 1.0], [0.0, 0.0, 0.0], [2.0, 0.0, 0.0]]
    assert drv.coincident_pairs(pos) == [(0, 2)]


def test_coincident_pairs_ignores_a_close_but_distinct_contact():
    # 0.09 nm = 0.9 A is a severe steric clash and emphatically NOT this function's business: the
    # minimiser can and should resolve it. Flagging it here would silently turn a geometry guard into
    # a clash fixer that edits chemistry.
    pos = [[0.0, 0.0, 0.0], [0.09, 0.0, 0.0]]
    assert drv.coincident_pairs(pos) == []


def test_coincident_pairs_reports_each_pair_once_and_sorted():
    pos = [[0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]]
    assert drv.coincident_pairs(pos) == [(0, 1), (0, 2), (1, 2)]


# ---- coordinate degeneracy: the fix ----------------------------------------------------------
def test_dedegenerate_moves_only_the_degenerate_atom_and_by_the_stated_amount():
    import math
    pos = [[0.0, 0.0, 0.0], [1.0, 1.0, 1.0], [0.0, 0.0, 0.0]]
    out, rep = drv._dedegenerate_positions(pos, lambda _m: None, "t", nudge_nm=1e-3)
    assert rep["n_coincident_pairs"] == 1 and rep["n_moved"] == 1
    # atom 0 keeps its coordinates exactly; atom 1 was never degenerate and is untouched.
    assert list(out[0]) == [0.0, 0.0, 0.0]
    assert list(out[1]) == [1.0, 1.0, 1.0]
    d = math.dist(list(out[2]), [0.0, 0.0, 0.0])
    assert math.isclose(d, 1e-3, rel_tol=1e-9)
    assert drv.coincident_pairs(out) == []


def test_dedegenerate_is_deterministic_across_calls():
    """Two hosts handed the same system must start from the same coordinates. A random nudge would
    make a failing leg irreproducible, which is the opposite of what a spot lane needs."""
    pos = [[0.0, 0.0, 0.0], [0.0, 0.0, 0.0]]
    a, _ = drv._dedegenerate_positions([r[:] for r in pos], lambda _m: None, "t")
    b, _ = drv._dedegenerate_positions([r[:] for r in pos], lambda _m: None, "t")
    assert [list(r) for r in a] == [list(r) for r in b]


def test_dedegenerate_is_a_no_op_on_a_healthy_system():
    """Every other unit in the lane has no coincident pair, and this must be provably inert for them —
    a geometry guard that quietly perturbs healthy systems would put a silent deviation into 18 legs."""
    pos = [[0.0, 0.0, 0.0], [0.5, 0.0, 0.0], [0.0, 0.5, 0.0]]
    out, rep = drv._dedegenerate_positions([r[:] for r in pos], lambda _m: None, "t")
    assert rep["n_coincident_pairs"] == 0
    assert [list(r) for r in out] == pos


def test_the_driver_dedegenerates_BEFORE_anything_reads_the_positions():
    """Ordering is the whole property: the restraint centre, the sampler and the minimiser all read
    `positions`, so the de-degeneration has to happen ahead of all of them, not next to one of them."""
    src = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                            "rbfe_spot_driver.py")).read()
    body = src.split("def run_spot_safe(", 1)[1]
    i_fix = body.index("_dedegenerate_positions(positions")
    for later in ("add_flat_bottom_restraint", "unit._get_sampler(", "_get_integrator("):
        assert i_fix < body.index(later), f"{later} reads positions before the de-degeneration"


def test_dedegeneration_can_be_switched_off_but_defaults_ON():
    src = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                            "rbfe_spot_driver.py")).read()
    assert 'os.environ.get("RBFE_DEDEGENERATE", "1") == "1"' in src


def test_gradient_probe_returns_an_empty_dict_rather_than_a_fabricated_zero():
    # "not measured" and "measured, and fine" have opposite consequences — the first must never be
    # rendered as the second, which is why the failure return is {} and the verdict reads {} as
    # HALF-MEASURED rather than as a clean gradient.
    logs = []
    assert drv._gradient_probe(object(), logs.append, "unit-test") == {}
    assert any("grad-diag:unit-test" in m for m in logs)
