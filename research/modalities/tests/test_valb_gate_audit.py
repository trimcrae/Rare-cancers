"""Locks the properties the applied admits-zero defect fix is JUSTIFIED BY, so they cannot silently regress.

The fix (commit 3f11cbf5) was applied in place, after an unfavourable result, on three claims: that it is
strictly stricter, that it changes no recorded verdict, and that it excludes the null. Those claims are the
entire reason it counts as a defect fix rather than a post-hoc retune — so they belong in the test suite, not
only in a commit message and an audit document. A future edit that makes the gate more permissive anywhere
should turn this file red.

Fast by construction (a coarse deterministic grid, no Monte Carlo). The full audit with its 20,468-point scan
and 40,000-trial Monte Carlo lives in valb_gate_audit.py and is run on demand.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import ternary_fep_reduce as red  # noqa: E402

TARGET = 0.944
R0 = -0.534
RANK = {"FAIL": 0, "INDETERMINATE": 1, "BORDERLINE": 2, "PASS": 3}


def _v(vals, extended=False, anti_null=None):
    return red.calibration_gate(list(vals), TARGET, extended=extended, anti_null=anti_null)["decision"]


def test_the_superseded_rule_really_did_admit_the_null():
    """If this ever stops being true, the premise of the whole fix is gone and it should be reconsidered."""
    assert _v([0.05] * 5, extended=True, anti_null=False) == "PASS"
    assert _v([0.02, 0.08, -0.01, 0.11, 0.05], extended=True, anti_null=False) == "PASS"


def test_the_corrected_rule_rejects_the_null():
    assert _v([0.05] * 5, extended=True) != "PASS"
    assert _v([0.02, 0.08, -0.01, 0.11, 0.05], extended=True) != "PASS"


def test_the_corrected_rule_still_passes_an_accurate_precise_method():
    """Stricter must not mean unpassable — a method sitting on the target with a tight spread must PASS, or the
    fix would have replaced one broken gate with another."""
    assert _v([0.90, 0.94, 0.98, 0.92, 0.96], extended=True) == "PASS"


def test_monotone_strictness_over_a_grid():
    """The corrected verdict may never rank ABOVE the superseded one. A single counterexample would make the
    amendment a retune rather than a defect fix."""
    worse = []
    for i in range(-100, 201):
        m = i * 0.02
        for sd in (0.0, 0.1, 0.25, 0.5, 0.75, 0.9, 1.0, 1.2):
            for n, vals in ((3, [m - sd, m, m + sd]),
                            (5, [m - sd * 2 ** 0.5, m, m, m, m + sd * 2 ** 0.5])):
                for ext in (False, True):
                    if RANK[_v(vals, ext, True)] > RANK[_v(vals, ext, False)]:
                        worse.append((n, ext, round(m, 3), sd))
    assert not worse, "corrected rule is MORE permissive at %d points, e.g. %s" % (len(worse), worse[:3])


def test_the_fix_does_not_rescue_the_failing_r0_result():
    """THE INTEGRITY TEST. Conditioned on the real r0, no replicate set may pass under the corrected rule that
    did not already pass under the superseded one — and in fact none passes at all."""
    passes_new = passes_old = 0
    g = [x * 0.25 for x in range(-16, 33)]
    for r1 in g:
        for r2 in g:
            if _v([R0, r1, r2]) == "PASS":
                passes_new += 1
            if _v([R0, r1, r2], anti_null=False) == "PASS":
                passes_old += 1
            for r3 in (0.0, 0.944, 2.0):
                for r4 in (0.0, 0.944, 2.0):
                    if _v([R0, r1, r2, r3, r4], extended=True) == "PASS":
                        passes_new += 1
                    if _v([R0, r1, r2, r3, r4], extended=True, anti_null=False) == "PASS":
                        passes_old += 1
    assert passes_new == 0, "the corrected rule passes %d r0-anchored sets — it rescues the failing result" % passes_new
    assert passes_old > 0, ("the superseded rule must pass SOME r0-anchored set, else this test cannot "
                            "discriminate the fix from a no-op")


def test_r0_alone_is_indeterminate_under_both_rules():
    """'changes no recorded verdict' — the only verdict on record is r0's."""
    assert red.calibration_gate([R0], TARGET)["decision"] == "INDETERMINATE"
    assert red.calibration_gate([R0], TARGET, anti_null=False)["decision"] == "INDETERMINATE"


def test_the_audit_switch_is_off_the_production_path():
    """anti_null defaults to the corrected rule and the metrics record which rule ran, so a report can never be
    ambiguous about which gate produced it."""
    assert red.GATE_ANTI_NULL_ENABLED is True
    assert red.calibration_gate([0.9, 0.95, 1.0], TARGET)["anti_null_rule_applied"] is True
    assert red.calibration_gate([0.9, 0.95, 1.0], TARGET, anti_null=False)["anti_null_rule_applied"] is False


def test_the_accept_band_is_still_wider_than_the_signal():
    """Not a regression guard — a RECORDED FACT, so that nobody reads the defect fix as having made the gate
    informative. A method reading double the true cooperativity change still passes."""
    assert _v([1.90, 1.94, 1.98, 1.92, 1.96], extended=True) == "PASS"
    assert _v([0.50, 0.52, 0.48, 0.51, 0.49], extended=True) == "PASS"
