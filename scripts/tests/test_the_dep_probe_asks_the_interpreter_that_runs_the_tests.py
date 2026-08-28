"""`preflight.sh`'s dependency banner must probe the interpreter `$PYTEST` will actually use.

⛔ THE DEFECT THIS ASSERTS AGAINST IS THIS FILE'S OWN HISTORY, THREE TIMES.
  2026-08-15  `python3 -m pytest` was chosen while pytest was a uv TOOL in its own venv, so
              `import yaml` succeeded in the shell and failed inside the tests. 36 invented failures.
  2026-08-23  the xdist probe asked `python3` while the tests ran under `$PYTEST`. The 2.9x
              parallel speedup had been off the whole time; the fix moved that probe onto `$PYTEST`.
  2026-08-28  the DEPENDENCY probe, sitting ~20 lines ABOVE the xdist one and written against the
              same incident (AUT-PD-026), was still hard-coding `python3 -c`. One-of-a-pair
              (`paper-hardening` §8b.2): a fix bound to one call site regresses at its sibling.

★ WHAT IS ASSERTED, AND WHY IT IS A TEXT CHECK. The two interpreters differ only at runtime and only
on a degraded box, so a behavioural test would pass on any healthy sandbox and assert nothing --
which is the "reports while measuring nothing" defect `preflight.sh`'s own header was written
against. The property that must hold is structural and is visible in the source: the probe's command
word is the resolved run interpreter, never the bare `python3`.

⚠ WHAT THIS DOES NOT CATCH, stated here rather than discovered later:
  * whether `_PYTEST_PYTHON` is resolved CORRECTLY -- only that the probe consults it. A wrong
    resolution is a different bug and this guard would stay green through it.
  * a fourth probe added elsewhere in the file against `python3`. It binds to this one call site,
    which is the very defect class it records; a future sibling needs its own assertion here.
  * the xdist probe, which is asserted by nothing and is currently correct by construction
    (`$PYTEST --version --version`).
"""

import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PREFLIGHT = os.path.join(ROOT, "scripts", "preflight.sh")


def _source():
    with open(PREFLIGHT, encoding="utf-8") as fh:
        return fh.read()


def test_preflight_is_readable():
    """An unreadable gate script is an unanswered question, not a pass (CLAUDE.md §4)."""
    assert os.path.isfile(PREFLIGHT), f"{PREFLIGHT} is missing"
    assert "_dep_probe=" in _source(), (
        "the dependency probe assignment `_dep_probe=` is gone from preflight.sh — this guard now "
        "asserts nothing. Re-point it at whatever replaced the probe rather than deleting it."
    )


def test_the_run_interpreter_is_resolved_from_the_pytest_branch():
    """`$PYTEST` is either `python3 -m pytest` or the uv-tool console script; the probe needs both."""
    src = _source()
    assert re.search(r'^_PYTEST_PYTHON=', src, re.M), (
        "preflight.sh no longer resolves _PYTEST_PYTHON. Without it the dependency banner can only "
        "describe the system interpreter, which is not the one the tests import from whenever "
        "$PYTEST is the uv tool venv."
    )
    assert re.search(r'if \[ "\$PYTEST" = "pytest" \]', src), (
        "_PYTEST_PYTHON is set but never branches on the console-script case, so it is a rename of "
        "`python3` rather than a resolution of the run interpreter."
    )


def test_the_dependency_probe_does_not_hard_code_python3():
    """The one that would have caught 2026-08-28. The probe's command word must be the run
    interpreter, not the bare `python3`."""
    src = _source()
    m = re.search(r'if ! _dep_probe="\$\((.*?) -c "', src, re.S)
    assert m, (
        "could not find the `_dep_probe=\"$(<interpreter> -c \"` form in preflight.sh. Either the "
        "probe was rewritten (re-point this guard) or it no longer runs a subprocess at all."
    )
    invoked = m.group(1).strip()
    assert invoked == '"$_PYTEST_PYTHON"', (
        f"the dependency probe runs `{invoked} -c`, not `\"$_PYTEST_PYTHON\" -c`. When $PYTEST is "
        f"the uv tool venv this probes an interpreter no test imports from, and its verdict — "
        f"green or red — is about the wrong environment. That is the 2026-08-15 and 2026-08-23 "
        f"incidents repeated a third time in the same file."
    )


# ---------------------------------------------------------------------------------------------
# ⛔ ONE FACT, TWO PLACES (CLAUDE.md §1). `dev-setup.sh`'s `_preflight_python` exists ONLY to mirror
# `preflight.sh`'s interpreter branch, so that the packages are installed into the interpreter the
# suites will actually run in. dev-setup says so in its own words -- "Keep the two in step: if that
# `if python3 -c "import pytest"` branch ever changes, this function changes with it" -- and a
# comment is not a check. If they drift, dev-setup provisions one interpreter, preflight runs the
# other, and every failure is manufactured. That is AUT-PD-026's mechanism in one sentence.
# ⚠ WHAT THIS DOES NOT CATCH: agreement of MEANING. Both files could adopt the same NEW wrong
# condition and stay green here. It asserts they have not silently diverged, nothing more.
DEVSETUP = os.path.join(ROOT, "scripts", "dev-setup.sh")
_SHARED_CONDITION = 'python3 -c "import pytest"'


def test_devsetup_and_preflight_choose_the_run_interpreter_by_the_same_test():
    assert os.path.isfile(DEVSETUP), f"{DEVSETUP} is missing"
    with open(DEVSETUP, encoding="utf-8") as fh:
        dev = fh.read()
    pre = _source()
    # ⛔ ANCHOR ON THE BRANCH LINE, NOT ON THE FILE. Measured 2026-08-28 by mutation M5: a first cut
    # asserted `_SHARED_CONDITION in pre`, and replacing the real `if` line left the guard GREEN
    # because the same words appear in this file's own comments about the incident. A guard whose
    # anchor is satisfied by prose describing the bug is satisfied by the bug.
    assert re.search(r'^if ' + re.escape(_SHARED_CONDITION) + r' ', pre, re.M), (
        f"preflight.sh no longer OPENS its interpreter branch with `if {_SHARED_CONDITION} `. "
        f"dev-setup.sh's `_preflight_python` mirrors that exact branch to decide WHERE to install; "
        f"change one and you must change the other, or the provisioned interpreter stops being the "
        f"running one."
    )
    assert "_preflight_python()" in dev, (
        "dev-setup.sh no longer defines `_preflight_python`, so nothing there mirrors preflight's "
        "choice and TEST_DEPS may be installed into an interpreter no test imports from."
    )
    body = dev.split("_preflight_python()", 1)[1].split("\n}", 1)[0]
    assert _SHARED_CONDITION in body, (
        f"`_preflight_python` in dev-setup.sh no longer branches on `{_SHARED_CONDITION}`, the "
        f"condition preflight.sh still uses. The two have drifted: dev-setup will provision one "
        f"interpreter and preflight will run the suites in another."
    )


# ---------------------------------------------------------------------------------------------
# ⛔ THE SECOND PROBE IN THIS FILE, AND IT FAILED FOR A DIFFERENT REASON: `set -o pipefail` PLUS
# `grep -q`. `grep -q` exits the instant it matches, the producer's stdout becomes EPIPE, the
# producer exits non-zero, and pipefail reports the whole pipeline as failed — so a SUCCESSFUL
# match reads as "not found". Measured 2026-08-28 over 60 samples of preflight's exact xdist probe:
# 34 answered "no xdist" and in all 34 it was pytest that exited non-zero (`PIPESTATUS=(1 0)`),
# grep having matched every time. Cost, from this repository's own numbers: the modalities suite is
# 968.9 s serial against 336.9 s at `-n 4`, so about half of every modalities run silently paid
# ~11 extra minutes. The rewritten form (capture once, match with `case`) measured 0/60.
#
# ★ WHY THIS IS A TEXT CHECK TOO: the defect is a RACE, so a behavioural test is exactly the thing
# that passes on a lucky run. The property that must hold is that no second process can be killed
# early — i.e. the probe is not a pipeline at all — and that is visible in the source.
#
# ⚠ WHAT THIS DOES NOT CATCH: any OTHER `... | grep -q` under pipefail elsewhere in the file. It is
# bound to this one call site, which is the defect class this whole file records; a general check
# would need to parse the script.


def test_the_xdist_probe_is_not_a_grep_q_pipeline():
    """⚠ THE ANCHOR SKIPS COMMENT LINES, AND IT HAD TO BE TAUGHT TO. The first cut of this
    assertion went red against the FIXED script, because rule 1.2 keeps the broken pipeline quoted
    verbatim in preflight.sh's `Superseded, retained:` note four lines above the fix. That is the
    same trap mutation M5 exposed in this file's other assertion: a pattern that prose describing
    the bug can satisfy is a pattern the bug can satisfy. Only executable lines count."""
    src = _source()
    assert not re.search(r'^(?!\s*#).*\$PYTEST --version --version[^\n]*\|\s*grep', src, re.M), (
        "preflight.sh detects xdist by piping `$PYTEST --version --version` into grep. Under "
        "`set -o pipefail` (line 49) `grep -q` exits on match, the producer dies of EPIPE, and the "
        "pipeline reports failure — measured 34/60 false negatives, each one silently costing the "
        "modalities suite ~11 minutes. Capture the output once and match it with `case` instead."
    )


def test_the_xdist_decision_is_made_from_a_captured_string():
    src = _source()
    assert re.search(r'^_pytest_selftest="\$\(\$PYTEST --version --version', src, re.M), (
        "preflight.sh no longer captures `$PYTEST --version --version` into a variable before "
        "deciding on xdist. Without the capture there is a second process in the decision, and a "
        "second process is what the pipefail race needs."
    )
    assert re.search(r'case "\$_pytest_selftest" in', src), (
        "the captured pytest self-report is not matched with `case`. Any form that re-runs pytest "
        "or pipes it re-opens the race this guard exists to close."
    )
