#!/usr/bin/env python3
"""The [REDUCE-VERDICT] annotation must read keys the reducer actually emits — and must SAY SO when it cannot.

WHY THIS FILE EXISTS (2026-07-27). The annotation is the whole point of §D of the guard audit: the watchdog
dispatches `mode=reduce` with no session awake, so the verdict has to arrive in one API call rather than in a log
nobody opens. It read

    hy = dec.get('hysteresis_ok')

and `ternary_fep_reduce.calibration_decision` emitted no key of that name on ANY path — it emitted
`checks.hysteresis_resolved`. `.get()` on an absent key returns None, and None was mapped to the string
"NOT MEASURED (no reverse leg reduced)". So the annotation was HARDWIRED to that sentence, and it printed it on
the day the first fwd/rev hysteresis this program has ever measured (0.3246 kcal/mol, inside the 1.0 ceiling)
was sitting two keys away in the same file. The reciprocal hazard was worse: `quiet = (verdict == 'PASS' and
hy is True)` could never be True, so a genuine PASS would have been annotated ::error with the text "GATE PASSED
BUT THE PREREGISTERED FWD/REV CRITERION DID NOT" — naming as unmeasured a criterion that had been measured and
had passed. That is report_cofold.py (§L.6a) reflected: a verdict string decoupled from its measurement.

TWO CHECKS, and the method matters because both cheap versions of this test are worthless:

  1 · PHANTOM-KEY SWEEP. The keys are **extracted from the YAML by AST** — every `g.get(...)` / `dec.get(...)`
      in the real annotation script — and each is required to be emitted by SOME path of the producer it is read
      from. A test that RETYPED the key list would prove only that the copy agrees with itself (the §L.6 lesson
      that made the workflow's filename rule an extraction), and a text `grep` for the offending expression
      false-positives on its own docstring (the §L.6a lesson that made the sweep an AST walk).

  2 · END-TO-END EXECUTION. The extracted script is EXEC'd against reducer output built by calling the real
      reducer functions, and the emitted annotation text is asserted. Reading the formatter is how the original
      defect survived review; running it is what caught it.

Pure stdlib — no MD, no numpy, no pyyaml. Runs in the dev sandbox.
"""

import ast
import io
import json
import os
import sys
import textwrap
import contextlib

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
WF = os.path.join(REPO, ".github", "workflows", "gpu-ternary-fep-gcp.yml")

import ternary_fep_reduce as red

REDUCTION_PATH_LITERAL = "'/tmp/legs/ternary_coop_reduction.json'"


def extract_heredoc(marker, path=WF):
    """The REAL lines of a heredoc body in the workflow, dedented as the YAML block scalar delivers them.

    Extraction, never transcription: a retyped copy of the script would pass every assertion below while the
    workflow ran something else entirely."""
    src = open(path).read().splitlines()
    start = next(i for i, l in enumerate(src) if l.strip().endswith("<<'%s'" % marker))
    end = next(i for i in range(start + 1, len(src)) if src[i].strip() == marker)
    return textwrap.dedent("\n".join(src[start + 1:end])) + "\n"


VERDICT_SRC = extract_heredoc("PYVERDICT")


def _gets(src, names):
    """Every `<name>.get('<key>'[, default])` in `src`, as {name: {keys}}. AST, not text: the expression appears
    inside this file's own docstring and inside the workflow's comments, and a grep fires on both."""
    out = {n: set() for n in names}
    for node in ast.walk(ast.parse(src)):
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                and node.func.attr == "get" and isinstance(node.func.value, ast.Name)
                and node.func.value.id in out and node.args
                and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str)):
            out[node.func.value.id].add(node.args[0].value)
    return out


def _agg(env, mean, hysteresis, n):
    return {"leg_id": "calib_hi_to_lo__%s" % env, "environment": env, "mean_dg_morph_kcal": mean,
            "replicate_sd_kcal": (0.3 if n > 1 else None), "n_replicas": n,
            "ci95_half_width_kcal": (0.4 if n > 1 else None),
            "hysteresis_kcal": hysteresis, "dg_values": [mean] * n}


def _producer_key_union():
    """Every key the two producers can emit, across all their branches."""
    dec, gate = set(), set()
    for n in (1, 3):
        for hys in (None, 0.3246, 1.6):
            dec |= set(red.calibration_decision(_agg("ternary", 47.47, hys, n),
                                                _agg("binary", 48.0, None, n), 0.944))
    dec |= set(red.calibration_decision(None, None, 0.944))
    for reps in ([], [-0.534], [0.9, 1.0, 1.1], [1.0, 0.9, 0.95]):
        for ok in (True, False, None):
            gate |= set(red.calibration_gate(reps, 0.944, diagnostics_ok=ok))
    return {"dec": dec, "g": gate}


def test_every_key_the_annotation_reads_is_emitted_by_its_producer():
    read = _gets(VERDICT_SRC, ("g", "dec"))
    assert read["dec"] and read["g"], "extraction found no .get() calls — the heredoc marker or shape moved"
    emitted = _producer_key_union()
    # keys the annotation attaches to the reduction root, not to a producer object
    root_only = {"valB_calibration_gate", "valB_calibration_decision"}
    for obj in ("dec", "g"):
        phantom = sorted(k for k in read[obj] - emitted[obj] if k not in root_only)
        assert not phantom, (
            "the annotation reads %r off `%s` but ternary_fep_reduce emits it on NO code path. `.get()` will "
            "return None forever and the verdict will report whatever None means — which for hysteresis_ok "
            "was the string 'NOT MEASURED'. Emitted keys: %s" % (phantom, obj, sorted(emitted[obj])))


def test_the_gate_schema_is_CONSTANT_across_replicate_counts():
    """ABSENT and null must mean different things, so absence cannot also mean "not defined on this path".

    The corrected 2026-07-27 annotation read `mean_ddG_coop=KEY ABSENT | target=KEY ABSENT | cycle_SD=KEY ABSENT`
    at n=1. Two of those are genuinely undefined with one replicate — but `target_kcal` is a frozen constant
    handed straight into the call and discarded, the same shape as the diagnostics tri-state. And rendering
    "undefined here" the same way as "the reader and producer disagree about the field name" hands back the
    ambiguity the sentinel exists to remove, when a phantom key is what started all this. So the gate emits the
    SAME key set on every path, with explicit nulls where a quantity is not defined, and KEY ABSENT is reserved
    for a schema mismatch."""
    full = set(red.calibration_gate([0.9, 1.0, 1.1], 0.944, diagnostics_ok=True))
    thin = red.calibration_gate([-0.534], 0.944, diagnostics_ok=False)
    missing = sorted(k for k in full - set(thin) if k not in ("thresholds", "authorizes", "adaptive_action",
                                                             "anti_null_checks", "anti_null_rule_applied"))
    assert not missing, "n=1 drops keys the n>=2 path emits: %s" % missing
    assert thin["target_kcal"] == 0.944, "the frozen target is an INPUT — it cannot be unknown on any path"
    for k in ("mean_ddg_coop_kcal", "cycle_sd_kcal", "abs_error_kcal"):
        assert thin[k] is None, "%s is undefined at n=1 and must say so as an explicit null, not by absence" % k


def test_the_hysteresis_and_diagnostics_keys_are_on_EVERY_producer_path():
    """Presence on *some* path is the phantom-key floor; these specific fields must never be absent, because an
    absent key and a measured-None are indistinguishable to the reader and one of the three states IS None."""
    for n in (1, 3):
        for hys in (None, 0.3246, 1.6):
            dec = red.calibration_decision(_agg("ternary", 47.47, hys, n), _agg("binary", 48.0, None, n), 0.944)
            for k in ("hysteresis_kcal", "hysteresis_ok", "hysteresis_measured", "hysteresis_max_kcal"):
                assert k in dec, "n=%s hys=%s missing %s" % (n, hys, k)
    for reps in ([], [-0.534], [0.9, 1.0, 1.1]):
        for ok in (True, False, None):
            g = red.calibration_gate(reps, 0.944, diagnostics_ok=ok)
            for k in ("diagnostics_ok", "diagnostics_state"):
                assert k in g, "reps=%r ok=%r missing %s" % (reps, ok, k)


# ------------------------------------------------------------------ end-to-end: run the real annotation script
def _run_annotation(reduction, tmpdir):
    p = os.path.join(tmpdir, "ternary_coop_reduction.json")
    json.dump(reduction, open(p, "w"))
    assert REDUCTION_PATH_LITERAL in VERDICT_SRC, (
        "the annotation's reduction path literal moved; this test would silently stop exercising it")
    src = VERDICT_SRC.replace(REDUCTION_PATH_LITERAL, repr(p))
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        exec(compile(src, "PYVERDICT", "exec"), {"__name__": "__main__"})
    return buf.getvalue()


def _reduction(dec, gate):
    return {"valB_calibration_decision": dec, "valB_calibration_gate": gate}


def _tmp():
    import tempfile
    return tempfile.TemporaryDirectory()


def test_annotation_reports_the_real_r0_hysteresis_as_measured_and_passing():
    """THE 2026-07-27 CASE END TO END. On the pre-fix pair this printed 'NOT MEASURED (no reverse leg reduced)'."""
    dec = red.calibration_decision(_agg("ternary", 47.470131055401, 0.32460514581189415, 1),
                                   _agg("binary", 48.00457067327676, None, 1), 0.944)
    gate = red.calibration_gate([-0.534439617875762], 0.944, diagnostics_ok=False)
    gate["per_replicate_ddg_coop_kcal"] = [-0.534439617875762]
    with _tmp() as d:
        out = _run_annotation(_reduction(dec, gate), d)
    assert "NOT MEASURED" not in out, "a measured hysteresis was reported as unmeasured:\n%s" % out
    assert "0.325" in out, "the measured value must appear, not just a boolean:\n%s" % out
    assert "PASS" in out
    assert "MEASURED_FAILURE" in out, (
        "diagnostics_ok=False is a MEASURED convergence failure and must not print as NOT_VERIFIED:\n%s" % out)
    assert "-0.534" in out, "the single-replicate point estimate exists and must not print only as None:\n%s" % out


def test_annotation_says_NOT_MEASURED_only_when_it_really_is():
    dec = red.calibration_decision(_agg("ternary", 47.47, None, 1), _agg("binary", 48.0, None, 1), 0.944)
    gate = red.calibration_gate([-0.534], 0.944, diagnostics_ok=None)
    with _tmp() as d:
        out = _run_annotation(_reduction(dec, gate), d)
    assert "NOT MEASURED (no reverse leg reduced)" in out
    assert "NOT_VERIFIED" in out


def test_annotation_reports_a_measured_failing_hysteresis_as_failing():
    dec = red.calibration_decision(_agg("ternary", 47.47, 1.6, 1), _agg("binary", 48.0, None, 1), 0.944)
    gate = red.calibration_gate([-0.534], 0.944, diagnostics_ok=True)
    with _tmp() as d:
        out = _run_annotation(_reduction(dec, gate), d)
    assert "FAIL" in out and "1.600" in out and "NOT MEASURED" not in out


def test_a_missing_key_is_LOUD_rather_than_a_quiet_none():
    """The general remedy on the reader side. If a future rename re-creates the phantom, the annotation must say
    the field is absent instead of silently reporting the criterion as unmeasured."""
    dec = red.calibration_decision(_agg("ternary", 47.47, 0.3, 1), _agg("binary", 48.0, None, 1), 0.944)
    dec.pop("hysteresis_ok")
    with _tmp() as d:
        out = _run_annotation(_reduction(dec, red.calibration_gate([-0.534], 0.944, diagnostics_ok=True)), d)
    assert "KEY ABSENT" in out, "a renamed/removed field must not read as 'not measured':\n%s" % out


def test_a_passing_gate_with_unmeasured_hysteresis_is_still_an_error_annotation():
    """Pre-existing invariant, re-pinned because the fix touches exactly this branch: PASS + hysteresis not
    measured must NOT go quiet."""
    dec = red.calibration_decision(_agg("ternary", 47.47, None, 3), _agg("binary", 48.0, None, 3), 0.944)
    gate = red.calibration_gate([0.9, 1.0, 0.95], 0.944, diagnostics_ok=True)
    gate["decision"] = "PASS"
    with _tmp() as d:
        out = _run_annotation(_reduction(dec, gate), d)
    assert out.startswith("::error"), out
    assert "NOT a pass of the calibration" in out


def test_a_passing_gate_with_measured_passing_hysteresis_goes_quiet():
    dec = red.calibration_decision(_agg("ternary", 47.47, 0.2, 3), _agg("binary", 48.0, 0.1, 3), 0.944)
    gate = red.calibration_gate([0.9, 1.0, 0.95], 0.944, diagnostics_ok=True)
    gate["decision"] = "PASS"
    with _tmp() as d:
        out = _run_annotation(_reduction(dec, gate), d)
    assert out.startswith("::notice"), (
        "with the gate PASSing and the preregistered fwd/rev criterion measured and passing there is nothing "
        "to shout about; if this can never happen the quiet branch is dead code:\n%s" % out)


if __name__ == "__main__":
    mod = sys.modules[__name__]
    fns = [v for k, v in sorted(vars(mod).items()) if k.startswith("test_") and callable(v)]
    for fn in fns:
        fn()
    print("OK — %d checks" % len(fns))
