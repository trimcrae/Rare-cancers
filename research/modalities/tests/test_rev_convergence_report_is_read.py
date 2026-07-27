#!/usr/bin/env python3
"""The REVERSE leg's convergence report must actually gate something.

WHY. mode=converge became direction-keyed so a rev run would stop overwriting the forward cycle's report — it now
writes ternary_convergence_rev.json. But `_diagnostics_ok()` opened only ternary_convergence.json, so the new file
was produced and read by NOBODY. That is not a cosmetic gap:

  * the rev leg exists for exactly one purpose — the preregistered hysteresis |dG_fwd + dG_rev| <= 1.0
  * a rev leg whose ligand left its pocket, or whose MBAR overlap collapsed, yields a number that is not a
    measurement of path error at all
  * so a SMALL hysteresis computed off a broken rev leg reads as a CLEAN CYCLE

and the ligand-departure failure this lane actually hit was found BY this very convergence analysis, on the binary
arm. Running its own output past the gate unread was a live hole, not a hypothetical one.

WHAT IS PINNED. Both directions again, since the cheap "fix" is to require the rev report unconditionally and
thereby wedge every forward-only cycle at NOT_VERIFIED forever:
  * a MEASURED rev failure -> False (FAIL), even with a spotless fwd report
  * a rev leg present but its report missing -> None (BORDERLINE), never True
  * NO rev leg at all -> the rev report is NOT required, and a clean fwd report still returns True
  * the reported metric keeps all three states apart

Pure stdlib + tmpdir; no MD, no numpy.
"""

import json
import os
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

import ternary_fep_reduce as red


def _report(technical_failure=False, complete=True):
    return {"legs": [{"leg_id": "calib_hi_to_lo__ternary_vhl", "technical_failure": technical_failure,
                      "diagnostics_complete": complete}]}


class _Sandbox:
    """Point the module's CKPT/IN at a scratch dir and control which reports / rev leg files exist."""

    def __enter__(self):
        self.d = tempfile.mkdtemp(prefix="revconv-")
        self._saved = (red.CKPT, red.IN)
        red.CKPT = red.IN = self.d
        return self

    def __exit__(self, *exc):
        red.CKPT, red.IN = self._saved
        shutil.rmtree(self.d, ignore_errors=True)
        return False

    def write(self, direction, **kw):
        p = os.path.join(self.d, red.convergence_report_name(direction))
        json.dump(_report(**kw), open(p, "w"))

    def add_rev_leg(self, leg="calib_hi_to_lo__ternary_vhl", seed=0):
        """A leg_<id>_rev_r<seed>.json is what _rev_leg_present() looks for."""
        p = os.path.join(self.d, "leg_%s_rev_r%d.json" % (leg, seed))
        json.dump({"leg_id": leg, "seed": seed, "direction": "rev", "dg_morph_kcal": 47.1}, open(p, "w"))


def test_report_names_are_direction_keyed():
    assert red.convergence_report_name("fwd") == "ternary_convergence.json"
    assert red.convergence_report_name("rev") == "ternary_convergence_rev.json"
    assert red.convergence_report_name("fwd") != red.convergence_report_name("rev"), (
        "if these collide, a rev converge run destroys the forward cycle's report — which is what happened")


def test_a_MEASURED_rev_failure_fails_even_with_a_spotless_fwd_report():
    with _Sandbox() as s:
        s.write("fwd", technical_failure=False, complete=True)
        s.write("rev", technical_failure=True, complete=True)
        s.add_rev_leg()
        assert red._diagnostics_ok() is False, (
            "a measured technical failure on the rev leg must FAIL — the hysteresis is computed from that leg, so "
            "a clean fwd report does not redeem it")


def test_a_rev_leg_with_NO_report_is_NOT_VERIFIED_not_a_pass():
    with _Sandbox() as s:
        s.write("fwd", technical_failure=False, complete=True)
        s.add_rev_leg()                      # rev leg ran; nobody analysed it
        assert red._diagnostics_ok() is None, (
            "a rev leg whose convergence was never computed must route to BORDERLINE, not PASS — this is the exact "
            "'success on no measurement' shape the fwd path was already fixed for")


def test_an_incomplete_rev_report_is_NOT_VERIFIED():
    with _Sandbox() as s:
        s.write("fwd", technical_failure=False, complete=True)
        s.write("rev", technical_failure=False, complete=False)
        s.add_rev_leg()
        assert red._diagnostics_ok() is None


def test_with_NO_rev_leg_the_rev_report_is_not_required():
    """The over-tightening guard. Most cycles are forward-only; demanding a rev report from them would pin every
    one of them at NOT_VERIFIED, which is just a different way of reporting the wrong thing."""
    with _Sandbox() as s:
        s.write("fwd", technical_failure=False, complete=True)
        assert red._rev_leg_present() is False
        assert red._diagnostics_ok() is True, (
            "a clean forward-only cycle must still pass; requiring an inapplicable rev report is not stricter, "
            "it is wrong")


def test_both_clean_passes():
    with _Sandbox() as s:
        s.write("fwd", technical_failure=False, complete=True)
        s.write("rev", technical_failure=False, complete=True)
        s.add_rev_leg()
        assert red._diagnostics_ok() is True


def test_a_fwd_failure_still_fails_when_rev_is_clean():
    with _Sandbox() as s:
        s.write("fwd", technical_failure=True, complete=True)
        s.write("rev", technical_failure=False, complete=True)
        s.add_rev_leg()
        assert red._diagnostics_ok() is False, "the pre-existing forward behaviour must be untouched"


def test_absent_fwd_report_is_still_not_a_pass():
    with _Sandbox():
        assert red._diagnostics_ok() is None, "the 2026-07-25 fix must survive the refactor"


def test_unparseable_report_is_NOT_VERIFIED():
    with _Sandbox() as s:
        open(os.path.join(s.d, red.convergence_report_name("fwd")), "w").write("{ this is not json")
        assert red._convergence_verdict("fwd") is None, "a corrupt report is unverified, never clean"


# ---- the reported metric must keep the three states apart ----

TARGET = 2.4


def _state(diagnostics_ok):
    g = red.calibration_gate([2.35, 2.40, 2.45], TARGET, diagnostics_ok=diagnostics_ok)
    return g["diagnostics_ok"], g["diagnostics_state"], g["decision"]


def test_reported_metric_distinguishes_measured_failure_from_never_verified():
    """bool(None) is False, so both collapsed onto a reported `false` and only the prose reason carried which."""
    ok_true, st_true, dec_true = _state(True)
    ok_false, st_false, dec_false = _state(False)
    ok_none, st_none, dec_none = _state(None)

    assert (ok_true, st_true) == (True, "CLEAN")
    assert (ok_false, st_false) == (False, "MEASURED_FAILURE")
    assert (ok_none, st_none) == (None, "NOT_VERIFIED"), (
        "an unverified diagnostic must not serialise as the same value as a measured failure, got %r/%r"
        % (ok_none, st_none))
    assert ok_false != ok_none, "the whole point: these two must be machine-distinguishable in the record"
    # and the decisions they drive must stay as they were
    assert dec_true == "PASS" and dec_false == "FAIL" and dec_none == "BORDERLINE", (
        "decision routing must be unchanged by the reporting fix: %r/%r/%r" % (dec_true, dec_false, dec_none))


def test_json_serialisable_so_the_verdict_still_writes():
    g = red.calibration_gate([2.35, 2.40, 2.45], TARGET, diagnostics_ok=None)
    json.dumps(g)          # None -> null; a non-serialisable sentinel would break the reducer's output
    assert '"diagnostics_ok": null' in json.dumps(g, indent=1).replace("\n", " ") or g["diagnostics_ok"] is None


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
