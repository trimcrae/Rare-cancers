"""The two large-suite flags are independent, and each stage answers only to its own.

⛔ WHY THIS EXISTS. On 2026-08-26 `PREFLIGHT_MODALITIES=1` was measured to be INERT ON ITS OWN: the
modalities stage sat nested inside `if [ "$RUN_TESTS" = "1" ]`, so the flag was an AND with
`PREFLIGHT_TESTS` rather than a flag. A run with `PREFLIGHT_MODALITIES=1` and nothing else executed
zero modality tests and printed a verdict offering `PREFLIGHT_MODALITIES=1` as the remedy -- advice
to set the flag that was already set. `PREFLIGHT_FULL=1` sets both, so publication was unaffected
and nothing caught it. CLAUDE.md, the note beside `RUN_MODALITIES`, and the script's own verdict
line all documented one independent flag; only the code disagreed.

⛔ AND THE OPPOSITE ERROR IS ALSO GUARDED, because it is the one that happened FIRST. On 2026-08-12
`RUN_MODALITIES` was put on the OUTER block and silently took the manuscripts suite out with it --
a run that printed PREFLIGHT OK having executed neither suite. So this file asserts BOTH directions:
the modalities flag must reach the modalities suite alone, AND it must not drag the manuscripts
suite along.

This is a STRUCTURAL test rather than a search for a magic string. It reconstructs which `if`
conditions enclose each pytest invocation and evaluates them under each combination of the two
flags, so a future refactor that moves a stage into a different block fails here rather than in six
weeks when somebody trusts a green run.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess

import pytest

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PREFLIGHT = os.path.join(REPO, "scripts", "preflight.sh")

# The two stage-identifying invocations. Matching the pytest call itself -- not a comment, not a
# heading -- because the call is the thing whose reachability is in question.
MODALITIES_CALL = re.compile(r"\$PYTEST .*research/modalities/tests")
MANUSCRIPTS_CALL = re.compile(r"\$PYTEST .*research/manuscripts/tests")

FLAG_COND = re.compile(r'\[\s*"\$(RUN_TESTS|RUN_MODALITIES)"\s*=\s*"1"\s*\]')


def _condition(line: str):
    """Reduce an `if`/`elif` line to a predicate over (run_tests, run_modalities).

    A line that mentions neither flag constrains nothing this test reasons about, so it becomes a
    tautology -- the test is about the flag gating, not about every branch in the script.
    """
    flags = FLAG_COND.findall(line)
    if not flags:
        return lambda t, m: True
    joiner_or = "||" in line
    joiner_and = "&&" in line

    def pred(t, m, _flags=tuple(flags), _or=joiner_or, _and=joiner_and):
        vals = [t if f == "RUN_TESTS" else m for f in _flags]
        if len(vals) == 1:
            return vals[0]
        if _or and not _and:
            return any(vals)
        return all(vals)

    return pred


def _enclosing_conditions():
    """Map each stage to the list of predicates that must all hold for its call to be reached."""
    with open(PREFLIGHT, encoding="utf-8") as fh:
        lines = fh.read().split("\n")

    stack: list = []
    found: dict[str, list] = {}
    for raw in lines:
        line = raw.strip()
        if line.startswith("#"):
            continue
        # `if ...; then` opens a block; a bare `fi` closes one. The script uses this plain form
        # throughout, and `bash -n` in the gate below covers the syntax itself.
        if re.match(r"^if\s.*;\s*then$", line):
            stack.append(_condition(line))
        elif re.match(r"^(fi|fi\s+#.*)$", line):
            if stack:
                stack.pop()
        if MODALITIES_CALL.search(raw) and "modalities" not in found:
            found["modalities"] = list(stack)
        if MANUSCRIPTS_CALL.search(raw) and "manuscripts" not in found:
            found["manuscripts"] = list(stack)
    return found


@pytest.fixture(scope="module")
def gates():
    g = _enclosing_conditions()
    assert "modalities" in g, "the modalities pytest invocation was not found in preflight.sh"
    assert "manuscripts" in g, "the manuscripts pytest invocation was not found in preflight.sh"
    return g


def _reached(preds, run_tests: bool, run_modalities: bool) -> bool:
    return all(p(run_tests, run_modalities) for p in preds)


def test_the_modalities_flag_alone_reaches_the_modalities_suite(gates):
    """The defect this file was written for."""
    assert _reached(gates["modalities"], run_tests=False, run_modalities=True), (
        "PREFLIGHT_MODALITIES=1 on its own does not reach the modalities suite -- the flag is inert, "
        "which is the 2026-08-26 defect exactly")


def test_the_modalities_flag_alone_does_not_drag_in_the_manuscripts_suite(gates):
    """The 2026-08-12 defect, in the other direction."""
    assert not _reached(gates["manuscripts"], run_tests=False, run_modalities=True)


def test_the_tests_flag_alone_reaches_the_manuscripts_suite(gates):
    assert _reached(gates["manuscripts"], run_tests=True, run_modalities=False)


def test_the_tests_flag_alone_does_not_reach_the_modalities_suite(gates):
    """2026-08-25: modalities came OUT of PREFLIGHT_TESTS. That decoupling is load-bearing --
    the suite is 62 % of a 13.5-minute gate and trimcrae asked for it off."""
    assert not _reached(gates["modalities"], run_tests=True, run_modalities=False)


def test_the_default_commit_loop_reaches_neither(gates):
    assert not _reached(gates["modalities"], run_tests=False, run_modalities=False)
    assert not _reached(gates["manuscripts"], run_tests=False, run_modalities=False)


def test_both_flags_reach_both_suites(gates):
    """PREFLIGHT_FULL=1 sets both, so this is the publication path."""
    assert _reached(gates["modalities"], run_tests=True, run_modalities=True)
    assert _reached(gates["manuscripts"], run_tests=True, run_modalities=True)


def test_the_parser_would_notice_if_a_stage_moved(gates):
    """Mock the thing under test and you test the mock -- so prove the walker is load-bearing.

    If `_condition` ignored the flags, every stage would be reachable everywhere and every
    assertion above would pass vacuously. This asserts the two stages have DIFFERENT gating, which
    a tautology-only parser cannot produce.
    """
    combos = [(t, m) for t in (False, True) for m in (False, True)]
    mod = [_reached(gates["modalities"], t, m) for t, m in combos]
    man = [_reached(gates["manuscripts"], t, m) for t, m in combos]
    assert mod != man, "both stages gate identically -- the parser is not reading the conditions"
    assert any(mod) and not all(mod)
    assert any(man) and not all(man)


def test_both_flags_are_resolved_from_their_environment_variables():
    """The RUN_* variables must actually come from the documented env vars."""
    with open(PREFLIGHT, encoding="utf-8") as fh:
        src = fh.read()
    for env, var in (("PREFLIGHT_MODALITIES", "RUN_MODALITIES"),
                     ("PREFLIGHT_TESTS", "RUN_TESTS"),
                     ("PREFLIGHT_FULL", "RUN_MODALITIES"),
                     ("PREFLIGHT_FULL", "RUN_TESTS")):
        pat = re.compile(rf'\[\s*"\$\{{{env}:-0\}}"\s*=\s*"1"\s*\]\s*&&\s*{var}=1')
        assert pat.search(src), f"{env} no longer sets {var}"


def test_the_verdict_can_distinguish_a_modalities_only_run():
    """A green line must say what it measured.

    Half the inert-flag defect was that `PREFLIGHT_MODALITIES=1` fell through to the branch printing
    "NEITHER large suite ran here". With the flag working, a verdict with no modalities-only branch
    would report a run that DID execute the suite as one that executed nothing.
    """
    with open(PREFLIGHT, encoding="utf-8") as fh:
        src = fh.read()
    tail = src[src.index("_preflight_summary_reached=1"):]
    assert 'elif [ "$RUN_MODALITIES" = "1" ]; then' in tail, (
        "the verdict has no branch for a modalities-only run")
    modalities_branch = tail.index('elif [ "$RUN_MODALITIES" = "1" ]; then')
    catch_all = tail.index("\nelse\n", modalities_branch)
    assert modalities_branch < catch_all, (
        "the modalities-only branch must precede the catch-all")

    # ⛔⛔ AND THE CATCH-ALL MUST NOT NAME A SUITE AS HAVING RUN. Until 2026-09-02 this test keyed on
    # the literal sentence "NEITHER large suite ran here", which the catch-all no longer prints —
    # gate 13 became opt-in that day, so the branch now derives what ran from the flags instead of
    # asserting a fixed tier. ⚠ KEYING ON THE SENTENCE WAS THE WEAKNESS: it made the test fail on a
    # rewording and pass on any rewording that kept the words, which is the opposite of what it is
    # for. The property is what matters — a verdict printed when neither large suite ran must not
    # claim either of them.
    catch_all_body = tail[catch_all:]
    for suite in ("the manuscripts suite", "the modalities suite"):
        for line in catch_all_body.split("\n"):
            stripped = line.strip()
            if not stripped.startswith("echo") or suite not in stripped:
                continue
            assert ("RUN_TESTS" in stripped or "RUN_MODALITIES" in stripped
                    or "PREFLIGHT_TESTS=1 adds" in stripped or "PREFLIGHT_TESTS=1 " in stripped
                    or "PREFLIGHT_MODALITIES=1 " in stripped or "$_ran" in stripped), (
                "the catch-all verdict names %r on a line that is neither gated on its flag nor "
                "offering the flag as a remedy, so a run that executed nothing would report it as "
                "executed: %s" % (suite, stripped))
    assert "NO TEST SUITE THIS RUN DID NOT NAME ABOVE HAS PASSED" in catch_all_body, (
        "the catch-all no longer states that an unnamed suite has not passed. That sentence is the "
        "whole defence against a green PREFLIGHT OK being read as 'the tests pass' — the "
        "'reports while measuring nothing' defect this file exists for.")


@pytest.mark.parametrize("full,skip,code", [("1", "1", 2), ("1", "0", 0), ("0", "1", 0)])
def test_full_cannot_skip_manuscript_tests(full, skip, code):
    """Execute the actual flag check; a contradictory publication run stops before setup."""
    shell = shutil.which("bash") or shutil.which("sh")
    assert shell, "Bash is required to exercise the preflight flag contract"
    with open(PREFLIGHT, encoding="utf-8") as fh:
        src = fh.read()
    start = src.index('# A FULL run must not claim')
    end = src.index('\nfi', start) + len('\nfi')
    result = subprocess.run([shell, "-c", src[start:end]], capture_output=True, text=True,
                            env={**os.environ, "PREFLIGHT_FULL": full, "SKIP_TESTS": skip})
    assert result.returncode == code, result.stderr


@pytest.mark.parametrize("paper,rc,stamps", [("PUB-ASO", "0", False), ("", "0", True),
                                           ("", "1", False)])
def test_only_an_unscoped_green_run_certifies_the_selector(tmp_path, paper, rc, stamps):
    """Run the real summary branch with a recorder spy, without touching live evidence."""
    shell = shutil.which("bash") or shutil.which("sh")
    assert shell, "Bash is required to exercise the preflight summary contract"
    with open(PREFLIGHT, encoding="utf-8") as fh:
        src = fh.read()
    summary = src[src.index("_preflight_summary_reached=1"):]
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    (scripts / "record_selector_validation.py").write_text("# recorder stand-in\n", encoding="utf-8")
    stamp = tmp_path / "called.txt"
    # The shell function intercepts the recorder only in this subprocess. All branch selection
    # and printed banners come from the real preflight source, not a reimplementation.
    preamble = 'python3() { printf "%s\\n" "$*" >> "$STAMP_LOG"; };\n'
    result = subprocess.run([shell, "-c", preamble + summary], cwd=tmp_path,
                            capture_output=True, text=True,
                            env={**os.environ, "PREFLIGHT_FULL": "1", "PREFLIGHT_PAPER": paper,
                                 "rc": rc, "STAMP_LOG": str(stamp)})
    assert result.returncode == int(rc), result.stderr
    assert stamp.exists() is stamps
    assert ("PREFLIGHT OK (FULL:" in result.stdout) is stamps
    if paper:
        assert "PREFLIGHT OK (PAPER=PUB-ASO:" in result.stdout


@pytest.mark.parametrize("kernel,bootstrap", [("Linux", True), ("MINGW64_NT-10.0", False),
                                             ("MSYS_NT-10.0", False), ("CYGWIN_NT-10.0", False)])
def test_linux_bootstrap_is_not_run_by_a_windows_shell(tmp_path, kernel, bootstrap):
    """Exercise platform dispatch with a recording installer, not a dependency/probe fake."""
    shell = shutil.which("bash") or shutil.which("sh")
    assert shell, "Bash is required to exercise preflight's platform dispatch"
    with open(PREFLIGHT, encoding="utf-8") as fh:
        src = fh.read()
    start = src.index("# Legacy Linux bootstrap")
    block = src[start:src.index("\nesac", start) + len("\nesac")]
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    installer = scripts / "dev-setup.sh"
    installer.write_text('#!/usr/bin/env sh\nprintf "%s" "$*" > "$CALLED_LOG"\n', encoding="utf-8")
    installer.chmod(0o755)
    called = tmp_path / "called.txt"
    result = subprocess.run([shell, "-c", 'uname() { echo "$TEST_KERNEL"; };\n' + block],
                            cwd=tmp_path, capture_output=True, text=True,
                            env={**os.environ, "TEST_KERNEL": kernel, "CALLED_LOG": str(called)})
    assert result.returncode == 0, result.stderr
    assert called.exists() is bootstrap
    if bootstrap:
        assert called.read_text() == "--if-needed"
    else:
        assert "skipping Linux dev-setup" in result.stdout
