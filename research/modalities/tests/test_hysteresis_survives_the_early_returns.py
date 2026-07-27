#!/usr/bin/env python3
"""A MEASURED criterion must not be dropped by a guard belonging to a DIFFERENT criterion.

WHY THIS FILE EXISTS (2026-07-27, the day the first fwd/rev hysteresis in this program was measured).
`calib_hi_to_lo__ternary_vhl` finished in both directions: dG_fwd = +47.470131055401, dG_rev = -47.79473620121289,
so |dG_fwd + dG_rev| = 0.32460514581189415 kcal/mol against the preregistered ceiling of 1.0 — the preregistered
criterion, measurable for the first time. `mode=reduce` computed it (it is in `morph_summaries` and in
`leg_algebra_audit`) and then the verdict annotation reported:

    fwd/rev hysteresis: NOT MEASURED (no reverse leg reduced)

TWO INDEPENDENT DEFECTS produced that sentence, and either alone was sufficient:

  1 · `calibration_decision()` computed the hysteresis only AFTER the Welch-Satterthwaite CI succeeded. With one
      replicate per environment `_welch_satterthwaite` returns None and the function returned early with
      {decision, reason, n_ternary, n_binary} and nothing about the hysteresis at all. But the two criteria have
      DIFFERENT data requirements: |mean(fwd) + mean(rev)| needs one replicate per DIRECTION and no replicate
      spread whatever, so it is measurable in exactly the case where the CI is not. A replicate-count guard
      silently suppressed a criterion that does not depend on replicate count.

  2 · the workflow annotation read `dec.get('hysteresis_ok')` — a key the reducer emitted under NO code path (it
      emitted `checks.hysteresis_resolved`). `.get()` on a key that does not exist yields None, and None was
      mapped to the string "NOT MEASURED". So the annotation was hardwired to that sentence regardless of what
      had been measured, and `quiet = (verdict == 'PASS' and hy is True)` could never be True — a genuine PASS
      would have been annotated as an ERROR claiming its preregistered criterion had not passed.

This is the lane's signature defect (§B/§L.6 of ternary-lane-guard-audit-2026-07-25.md) reached two new ways: not
by a coercion (`or 0.0`, `bool(None)`) but by a CONTROL-FLOW PATH that never computes the value, and by a READER
naming a field the producer does not have. Both render as the same None, which is a legal "not measured" value.
It is the mirror of report_cofold.py in §L.6a — there an unmeasured criterion was named as observed; here an
observed one is named as unmeasured.

WHAT IS PINNED, in both directions, because the cheap way to "fix" either is to make absent look fine:
  * every return path of calibration_decision carries hysteresis_kcal / hysteresis_ok / hysteresis_measured
  * an absent rev leg still yields None + measured=False, and NEVER 0.0, False-as-a-value, or a passing True
  * a measured-and-passing hysteresis is reported as passing even when the gate is INDETERMINATE for replicates
  * a measured-and-FAILING hysteresis is reported as failing on the same early-return path
  * every return path of calibration_gate carries diagnostics_ok AND diagnostics_state, so MEASURED_FAILURE and
    NOT_VERIFIED never collapse onto an absent key
  * the 1.0 ceiling is READ FROM THE PREREG JSON, not typed here or in the reducer

Pure stdlib against the real functions — no MD, no numpy, runs in the dev sandbox.
"""

import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

import ternary_fep_reduce as red

# the real r0 numbers, so this test fails if the reduction of the actual landed legs would be misreported
DG_FWD = 47.470131055401
DG_REV = -47.79473620121289
HYS_R0 = abs(DG_FWD + DG_REV)          # 0.32460514581189415


def _agg(env, mean, hysteresis, n=1):
    return {"leg_id": "calib_hi_to_lo__%s" % env, "environment": env, "mean_dg_morph_kcal": mean,
            "replicate_sd_kcal": (0.3 if n > 1 else None), "n_replicas": n,
            "ci95_half_width_kcal": (0.4 if n > 1 else None),
            "hysteresis_kcal": hysteresis, "dg_values": [mean] * n}


def _r0_pair(hysteresis=HYS_R0, n=1):
    """The r0 cycle exactly as it stands: ternary has a rev partner, binary does not, one seed each."""
    return _agg("ternary", DG_FWD, hysteresis, n), _agg("binary", 48.00457067327676, None, n)


# ------------------------------------------------------------------ hysteresis_fields: the tri-state itself
def test_absent_rev_leg_is_none_and_never_zero():
    f = red.hysteresis_fields(_agg("ternary", DG_FWD, None), _agg("binary", 48.0, None))
    assert f["hysteresis_kcal"] is None, "absent must not be a number; 0.0 reads as perfect antisymmetry"
    assert f["hysteresis_ok"] is None, "absent must not be True (a pass) or False (a measured failure)"
    assert f["hysteresis_measured"] is False


def test_measured_zero_is_distinguishable_from_absent():
    """A cycle that really closes perfectly must still be reportable as MEASURED."""
    f = red.hysteresis_fields(_agg("ternary", DG_FWD, 0.0), _agg("binary", 48.0, None))
    assert f["hysteresis_kcal"] == 0.0 and f["hysteresis_ok"] is True and f["hysteresis_measured"] is True


def test_worst_leg_wins_so_a_bad_leg_cannot_hide_behind_a_good_one():
    f = red.hysteresis_fields(_agg("ternary", DG_FWD, 0.2), _agg("binary", 48.0, 1.7))
    assert f["hysteresis_kcal"] == 1.7 and f["hysteresis_ok"] is False


def test_ceiling_is_read_from_the_prereg_not_typed_in_the_reducer():
    prereg = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                                         "nr4a3-ternary-coop-prereg.json")))
    frozen = prereg["retrospective_bar"]["technical_convergence"]["cycle_closure_or_hysteresis_kcal_max"]
    assert red.hysteresis_max_kcal() == float(frozen)
    assert red.AUDIT_ANTISYM_MAX_KCAL == float(frozen), (
        "the condition-8 antisymmetry audit and the calibration hysteresis criterion are the SAME frozen "
        "ceiling; two typed copies of 1.0 is how they drift apart")
    # and it really is read, not coincidentally equal: move the ceiling in a copy of the prereg and it follows.
    with tempfile.TemporaryDirectory() as d:
        prereg["retrospective_bar"]["technical_convergence"]["cycle_closure_or_hysteresis_kcal_max"] = 0.25
        p = os.path.join(d, "prereg.json")
        json.dump(prereg, open(p, "w"))
        assert red.hysteresis_max_kcal(p) == 0.25


# ------------------------------------------------------- calibration_decision: EVERY return path carries them
_HYS_KEYS = ("hysteresis_kcal", "hysteresis_ok", "hysteresis_measured", "hysteresis_max_kcal")


def test_n1_early_return_still_reports_the_measured_hysteresis():
    """THE ACTUAL 2026-07-27 CASE. Fails on the pre-fix reducer, which returned no hysteresis key here."""
    tern, bina = _r0_pair()
    dec = red.calibration_decision(tern, bina, 0.944)
    assert dec["decision"] == "INDETERMINATE" and "replicate" in dec["reason"]
    for k in _HYS_KEYS:
        assert k in dec, ("%s missing from the n<2 early return — the replicate guard belongs to the CI "
                          "criterion, not to the hysteresis one" % k)
    assert dec["hysteresis_measured"] is True
    assert dec["hysteresis_ok"] is True
    assert abs(dec["hysteresis_kcal"] - HYS_R0) < 1e-12


def test_n1_early_return_reports_a_measured_FAILURE_as_a_failure():
    """The other direction: the early return must not launder a bad hysteresis into silence either."""
    tern, bina = _r0_pair(hysteresis=1.6)
    dec = red.calibration_decision(tern, bina, 0.944)
    assert dec["hysteresis_ok"] is False and dec["hysteresis_measured"] is True
    assert dec["hysteresis_kcal"] == 1.6


def test_n1_early_return_with_no_rev_leg_is_still_NOT_MEASURED():
    tern, bina = _r0_pair(hysteresis=None)
    dec = red.calibration_decision(tern, bina, 0.944)
    assert dec["hysteresis_ok"] is None and dec["hysteresis_measured"] is False
    assert dec["hysteresis_kcal"] is None


def test_missing_environment_leg_return_carries_the_fields_too():
    dec = red.calibration_decision(None, None, 0.944)
    for k in _HYS_KEYS:
        assert k in dec
    assert dec["hysteresis_ok"] is None and dec["hysteresis_measured"] is False


def test_full_path_carries_them_and_agrees_with_its_own_checks_table():
    tern, bina = _r0_pair(n=3)
    dec = red.calibration_decision(tern, bina, 0.944)
    for k in _HYS_KEYS:
        assert k in dec
    assert dec["hysteresis_ok"] is dec["checks"]["hysteresis_resolved"], (
        "the top-level field and the checks table must be ONE computation with two labels; if they can "
        "disagree there are two homes for the criterion")
    assert dec["hysteresis_measured"] is dec["checks"]["hysteresis_measured"]


# ------------------------------------------------- calibration_gate: the tri-state survives ITS early return
def test_gate_n1_early_return_keeps_the_diagnostics_tristate():
    """`_diagnostics_ok()` is evaluated at the CALL SITE and handed in, so the answer is known by the time this
    return fires — and it was discarded. `.get('diagnostics_ok')` then yielded None, printing NOT_VERIFIED for
    what was a MEASURED FAILURE (both r0 convergence reports carry technical_failure=true)."""
    for ok, state in ((True, "CLEAN"), (False, "MEASURED_FAILURE"), (None, "NOT_VERIFIED")):
        g = red.calibration_gate([-0.534439617875762], 0.944, diagnostics_ok=ok)
        assert g["decision"] == "INDETERMINATE" and g["n_replicates"] == 1
        assert "diagnostics_ok" in g and "diagnostics_state" in g, (
            "an ABSENT key is not an acceptable substitute for the third state — .get() renders absence as "
            "None, i.e. as NOT_VERIFIED, which is one of the three states it is supposed to distinguish")
        assert g["diagnostics_ok"] is ok
        assert g["diagnostics_state"] == state


def test_gate_multi_replicate_path_reports_the_same_tristate():
    for ok, state in ((True, "CLEAN"), (False, "MEASURED_FAILURE"), (None, "NOT_VERIFIED")):
        g = red.calibration_gate([0.9, 1.0, 1.1], 0.944, diagnostics_ok=ok)
        assert g["diagnostics_ok"] is ok and g["diagnostics_state"] == state


def test_measured_failure_never_renders_as_not_verified_on_any_path():
    """One assertion for the whole bug class: across every replicate count the gate handles, False must never
    come back as None and must never come back as an absent key."""
    for reps in ([], [-0.534], [0.9, 1.0], [0.9, 1.0, 1.1, 1.2, 1.3]):
        g = red.calibration_gate(reps, 0.944, diagnostics_ok=False)
        assert g.get("diagnostics_ok", "ABSENT") is False, "reps=%r" % (reps,)
        assert g.get("diagnostics_state") == "MEASURED_FAILURE", "reps=%r" % (reps,)


if __name__ == "__main__":
    mod = sys.modules[__name__]
    fns = [v for k, v in sorted(vars(mod).items()) if k.startswith("test_") and callable(v)]
    for fn in fns:
        fn()
    print("OK — %d checks" % len(fns))
