#!/usr/bin/env python3
"""An UNMEASURED forward/reverse hysteresis must never be reported as a measured 0.0.

WHY THIS FILE EXISTS. `ternary_fep_reduce.leg_output_record` built its record with

    "hysteresis_kcal": leg_agg["hysteresis_kcal"] or 0.0
    conv = bool(... and (leg_agg["hysteresis_kcal"] is None or leg_agg["hysteresis_kcal"] <= 1.0))

`hysteresis_kcal` is None whenever the leg has no DIRECTION=rev partner — which, until rev was unlocked, was
EVERY leg in the lane. So the first line wrote "no reverse leg ran" out as the literal value 0.0, i.e. PERFECT
A->B/B->A antisymmetry, and the second let the same absence satisfy `converged`.

The 0.0 is the damaging half, and it is damaging ACROSS module boundaries: ternary_coop_gate.evaluate() was
written to catch exactly this case — it declares hysteresis_kcal "float|null" (results_schema) and fails a leg
whose value is null, because _num(None) is None and `hyst is None` is a failure branch. Feeding it 0.0 instead of
null meant that branch could not fire, so the reviewer's cycle-closure criterion was inert for the whole lane.
calibration_decision() in the SAME module already routes an unmeasured hysteresis to INDETERMINATE, with a comment
saying so; the per-leg record contradicted it one function away.

WHAT IS PINNED, in both directions, because the cheap way to "fix" this is to loosen the gate instead:
  * null propagates as null, and ternary_coop_gate ACTUALLY FAILS on it (the cross-module end-to-end assertion)
  * a genuinely measured 0.0 -- a perfectly closing cycle -- must still be reportable and must still pass
    (`or 0.0` also silently mapped a real 0.0 onto the same value, so the two were indistinguishable)
  * a measured, in-tolerance hysteresis still yields converged=True (this is not a blanket tightening)
  * validate_result rejects converged=True alongside a null hysteresis

Pure stdlib against the real functions -- no MD, no numpy, runs in the dev sandbox.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

import ternary_coop_gate as gate
import ternary_coop_io as tio
import ternary_fep_reduce as red


def _agg(hysteresis, n=3, ci=1.0, leg="calib_hi_to_lo__ternary_vhl"):
    """A minimal aggregate_leg()-shaped dict; only the fields leg_output_record touches."""
    return {"leg_id": leg, "environment": "ternary", "mean_dg_morph_kcal": -47.28,
            "replicate_sd_kcal": 0.3, "n_replicas": n, "ci95_half_width_kcal": ci,
            "hysteresis_kcal": hysteresis, "dg_values": [-47.28] * n}


def _record(hysteresis, **kw):
    return red.leg_output_record(_agg(hysteresis, **kw), {"ddg_alch_ternary_kcal": -47.28})


def test_unmeasured_hysteresis_stays_null_in_the_record():
    rec = _record(None)
    assert rec["hysteresis_kcal"] is None, (
        "an absent rev leg must serialise as null, got %r. Writing 0.0 here claims perfect antisymmetry from a "
        "measurement that was never made." % (rec["hysteresis_kcal"],))
    assert rec["hysteresis_measured"] is False


def test_unmeasured_hysteresis_cannot_claim_converged():
    rec = _record(None)
    assert rec["converged"] is False, (
        "converged must not be True when the fwd/rev check was never run — calibration_decision() calls that "
        "same situation INDETERMINATE, and the two must not disagree")


def test_a_genuinely_measured_zero_is_still_reportable_and_still_passes():
    """The direction that guards against over-tightening: a cycle that really closes perfectly is a GOOD result."""
    rec = _record(0.0)
    assert rec["hysteresis_kcal"] == 0.0 and rec["hysteresis_measured"] is True, (
        "a measured 0.0 must survive as a measured 0.0 — `or 0.0` mapped BOTH null and a real zero onto the same "
        "output, which is why the two were indistinguishable to every downstream reader")
    assert rec["converged"] is True, "a perfectly-closing cycle with n=3 and a tight CI is converged"


def test_a_measured_in_tolerance_hysteresis_still_converges():
    assert _record(0.4)["converged"] is True, "this change must not tighten the measured-and-fine case"


def test_a_measured_out_of_tolerance_hysteresis_still_fails():
    assert _record(2.5)["converged"] is False, "a hysteresis above 1.0 kcal/mol must still fail"


def test_validate_result_rejects_converged_beside_a_null_hysteresis():
    rec = tio.mock_result_for()
    rec["hysteresis_kcal"] = None
    rec["converged"] = True
    v = tio.validate_result(rec, mode="schema")
    assert not v["ok"], "converged=True with a null hysteresis must be a schema failure"
    assert any("NOT MEASURED" in f for f in v["failures"]), v["failures"]


def test_validate_result_accepts_a_null_hysteresis_with_converged_false():
    rec = tio.mock_result_for()
    rec["hysteresis_kcal"] = None
    rec["converged"] = False
    v = tio.validate_result(rec, mode="schema")
    assert v["ok"], ("null itself is legitimate — it is the honest encoding of 'not measured'. Failing it outright "
                     "would just push a producer back to coercing 0.0. Failures: %r" % (v["failures"],))


def test_validate_result_rejects_a_negative_hysteresis():
    rec = tio.mock_result_for()
    rec["hysteresis_kcal"] = -0.4          # |dG_fwd + dG_rev| cannot be negative
    v = tio.validate_result(rec, mode="schema")
    assert not v["ok"] and any("negative" in f for f in v["failures"]), v["failures"]


def test_validate_result_rejects_a_contradictory_measured_flag():
    rec = tio.mock_result_for()
    rec["hysteresis_kcal"] = None
    rec["converged"] = False
    rec["hysteresis_measured"] = True      # claims a measurement that is not there
    v = tio.validate_result(rec, mode="schema")
    assert not v["ok"] and any("contradicts" in f for f in v["failures"]), v["failures"]


def test_END_TO_END_the_downstream_gate_actually_fails_on_the_null():
    """The whole point. Null is only worth propagating if the gate it unblinds really does fire on it.

    ternary_coop_gate.evaluate() reads hysteresis_kcal from each leg dict; _num(None) is None, and `hyst is None`
    is a failure branch. This asserts the branch fires with null and does NOT fire with the 0.0 the reducer used
    to substitute — which is the exact false pass, demonstrated across the module boundary rather than argued.
    """
    frozen = gate.load_frozen()
    thresh = frozen["retrospective_bar"]["technical_convergence"]["cycle_closure_or_hysteresis_kcal_max"]

    def leg(hysteresis):
        return {"name": "calib_hi_to_lo__ternary_vhl", "n_replicas": 3, "hysteresis_kcal": hysteresis,
                "ci95_half_width_kcal": 1.0, "n_starting_poses": 2,
                "rank_reversal_under_loo": False, "pathology": False}

    def flags_hysteresis(hysteresis):
        """Did the gate object about the HYSTERESIS specifically? (It will also object about leg coverage here —
        one leg is not the frozen manifest — so the whole verdict's ok/not-ok cannot isolate what we're testing.)"""
        res = gate.gate_technical_convergence({"legs": [leg(hysteresis)]}, frozen)
        return "hysteresis/closure" in repr(res)

    assert flags_hysteresis(None), (
        "the gate MUST flag a null hysteresis — if it does not, propagating null buys nothing and the reducer fix "
        "is cosmetic")
    assert not flags_hysteresis(0.0), (
        "a measured 0.0 must pass the gate (threshold %.2f) — and 0.0 is exactly what the reducer's `or 0.0` handed "
        "over for every leg with no reverse partner, which is why the branch above could never fire" % thresh)
    assert flags_hysteresis(thresh + 0.5), "a hysteresis above the frozen threshold must still be flagged"


# The runner stays LAST: tests defined below a `__main__` block are silently skipped, which has already happened
# twice in this directory. Add new test_* functions ABOVE this line.
if __name__ == "__main__":
    fails = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print("PASS", name)
            except AssertionError as e:
                print("FAIL", name, "\n      ", e)
                fails += 1
            except Exception as e:  # noqa: BLE001
                print("ERROR", name, "\n      ", type(e).__name__, e)
                fails += 1
    print("\n%d failure(s)" % fails)
    sys.exit(1 if fails else 0)
