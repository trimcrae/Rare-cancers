#!/usr/bin/env python3
"""A missing PAE must not satisfy the 'confident relative placement' half of a co-fold call.

WHY. report_cofold.analyse() decided the call with

    coupled = inter_pae is not None and inter_pae < PAE_COUPLED
    folds_together = ordered_iface and (coupled if inter_pae is not None else True)

`coupled` is ALREADY False when inter_pae is None, so the trailing conditional did exactly one thing: flip the
unmeasured case from fail to pass. With no usable PAE matrix the call then rested on the contact patch alone — and
the verdict string went on to say "ordered contact patch + confident relative placement", naming as observed the
criterion that was never measured. A co-fold call is what sends an interface on to fpocket, so this is the
expensive direction to be wrong in.

Found by sweeping for the shape behind audit §L.6 — a default or coercion that makes "not measured"
indistinguishable from "measured and fine" — after fixing four instances of it in the ternary FEP lane. This one
was in a different lane and had NO test coverage at all.

The decision was pulled out of analyse() into the pure cofold_call() so it can be exercised without gemmi.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

import report_cofold as rc


def test_ordered_patch_with_NO_pae_is_NOT_ASSESSED_not_a_cofold():
    """The regression. Ordered patch + missing PAE used to return True and claim confident placement."""
    folds, verdict = rc.cofold_call(True, None)
    assert folds is None, (
        "with no PAE the placement half cannot be assessed, so the call must be None, got %r. True here is a "
        "co-fold claim resting on one of its two stated criteria." % (folds,))
    assert "NOT ASSESSED" in verdict, verdict
    assert "confident relative placement" not in verdict, (
        "the verdict must not name the criterion that was never measured — that phrasing is what made the old "
        "behaviour actively misleading rather than merely permissive: %r" % verdict)


def test_the_not_assessed_verdict_still_reports_what_WAS_measured():
    """NOT_ASSESSED must not throw away the ordered-patch observation — it is necessary, just not sufficient."""
    ordered, _ = rc.cofold_call(True, None)
    v_ordered = rc.cofold_call(True, None)[1]
    v_unordered = rc.cofold_call(False, None)[1]
    assert "IS ordered" in v_ordered and "necessary but not sufficient" in v_ordered, v_ordered
    assert "small or low-confidence" in v_unordered, v_unordered
    assert v_ordered != v_unordered, "the two unmeasured cases are not the same finding"


def test_a_genuine_cofold_still_passes():
    """The over-tightening guard: both criteria measured and met must still be a positive call."""
    folds, verdict = rc.cofold_call(True, rc.PAE_COUPLED - 1.0)
    assert folds is True, "ordered patch + confident placement is a co-fold; this change must not block it"
    assert "COMPOSITE INTERFACE PREDICTED" in verdict and "fpocket" in verdict, verdict


def test_measured_but_high_pae_is_a_real_negative():
    folds, verdict = rc.cofold_call(True, rc.PAE_COUPLED + 5.0)
    assert folds is False, "a measured, high PAE is a MEASURED negative — distinct from unmeasured"
    assert "NO CO-FOLD" in verdict and "high" in verdict, verdict


def test_disordered_patch_with_good_pae_is_a_real_negative():
    folds, verdict = rc.cofold_call(False, rc.PAE_COUPLED - 1.0)
    assert folds is False
    assert "NO CO-FOLD" in verdict
    assert "PAE" not in verdict or "high" not in verdict, (
        "the PAE was fine here, so the verdict must not blame it: %r" % verdict)


def test_the_three_states_are_mutually_distinguishable():
    got = {rc.cofold_call(True, None)[0], rc.cofold_call(True, 1.0)[0], rc.cofold_call(True, 99.0)[0]}
    assert got == {None, True, False}, (
        "NOT_ASSESSED / co-fold / no-co-fold must be three distinct values, got %r. Collapsing any two is the "
        "defect this file exists for." % (got,))


def test_boundary_is_exclusive_as_documented():
    """PAE_COUPLED's comment says 'below this', so exactly at the cutoff is NOT coupled."""
    assert rc.cofold_call(True, rc.PAE_COUPLED)[0] is False
    assert rc.cofold_call(True, rc.PAE_COUPLED - 0.01)[0] is True


def test_analyse_uses_the_shared_helper_rather_than_its_own_copy():
    """Pins the CALL SITE. Leaving the old inline expression in analyse() would leave every test above green
    while the real code path kept defaulting a missing PAE to True — the same call-site gap that let a
    frame-B swap pass eight tests in test_contact_moiety_pose_rmsd.py."""
    import inspect
    src = inspect.getsource(rc.analyse)
    assert "cofold_call(" in src, "analyse() must delegate to cofold_call(), not re-implement the decision"
    assert "if inter_pae is not None else True" not in src, (
        "the old default-to-True expression is still in analyse()")
    assert "folds_together = ordered_iface and" not in src, (
        "analyse() still computes the call itself; the rule must have exactly one home")


def test_no_conditional_in_the_module_defaults_to_True():
    """AST, not grep: the defect shape is `<x> if <measured> else True` — a ternary whose ELSE branch is the
    literal True, i.e. 'when we could not measure it, call it satisfied'.

    A text search was the obvious way to write this and it was wrong in both directions: it fired on the
    expression quoted inside cofold_call's own docstring (a false positive that cost this test a red run), and it
    would miss any reformatting across lines. Walking the tree checks the code and only the code.
    """
    import ast
    tree = ast.parse(open(rc.__file__).read())
    bad = [n for n in ast.walk(tree)
           if isinstance(n, ast.IfExp) and isinstance(n.orelse, ast.Constant) and n.orelse.value is True]
    assert not bad, (
        "found %d conditional(s) defaulting to True at line(s) %r — an unmeasured criterion must never arrive "
        "pre-satisfied" % (len(bad), [n.lineno for n in bad]))


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
