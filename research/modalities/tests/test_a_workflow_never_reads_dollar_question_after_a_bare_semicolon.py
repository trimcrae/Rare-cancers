"""A workflow step must not capture `$?` after a bare `;` — `set -e` eats it first.

★ WHY THIS GUARD EXISTS, AND WHY IT IS NOT A STYLE RULE.

GitHub runs every `run:` block under `bash -e {0}`, and several of this repository's steps add
`set -eo pipefail` on top. Under `-e` a failing simple command aborts the shell IMMEDIATELY, so in

    cmd > out 2>&1; RC=$?          # ⛔ RC is never assigned; the step dies with cmd's status
    RC=0; cmd > out 2>&1 || RC=$?  # ✅ the `||` makes cmd a tested command, and -e stands down

the first form never reaches the assignment.

⛔ THE MEASURED INCIDENT (2026-09-02, S47). Three jobs in `gpu-ternary-fep-vast.yml` — `market_gate`,
`triangle_gate` and `gate_5aks` — used the bare form to read `fleet_armed.py`, whose IDLE exit code is
**10**: the ordinary "the account holds zero instances" case. So the gate priced the board, printed
`[market-gate] ✅ CLEAR`, recorded `outcome: dispatched` in the ledger, and then the shell DIED at
`fleet_armed` — before the `gh workflow run` that was the entire point of the job. Zero instances made
the gate abort, and an aborted gate rents nothing, which keeps the account at zero instances: a
self-perpetuating stall that ran red every ~8 minutes across at least four commits.

⚠ AND THE RULE WAS ALREADY WRITTEN DOWN AND MEASURED BY NOTHING. `step1-fanout-autoscale.yml`'s
`armed` step carries the warning verbatim — "`rc=0; cmd || rc=$?` AND NOT `cmd; rc=$?`" — and got it
right, while three siblings in another file got it wrong. A comment binds only the reader who opens
that file. This test binds every workflow.

⚠ The step1 form fails SAFE (an unwritten output reads empty, which its consumers treat as ARMED);
the ternary form fails LOUD and stops the launch. Both are the same defect, so both are refused here
rather than only the expensive one.
"""

import pathlib
import re

WORKFLOWS = pathlib.Path(__file__).resolve().parents[3] / ".github" / "workflows"

#: A capture of `$?` whose preceding separator is `;` (or a line start), rather than `||`.
#: `|| VAR=$?` and `|| true` are the correct forms and must not match.
BARE_CAPTURE = re.compile(r";\s*_?[A-Za-z_][A-Za-z0-9_]*=\$\?")


def _offending_lines(text):
    out = []
    for n, line in enumerate(text.splitlines(), 1):
        stripped = line.lstrip()
        # A YAML/# comment quoting the anti-pattern to warn about it is the documentation this
        # guard enforces, not a violation of it.
        if stripped.startswith("#"):
            continue
        if BARE_CAPTURE.search(line):
            out.append((n, line.strip()))
    return out


def test_no_workflow_captures_dollar_question_after_a_bare_semicolon():
    assert WORKFLOWS.is_dir(), f"workflow directory not found: {WORKFLOWS}"
    bad = {}
    for wf in sorted(WORKFLOWS.glob("*.yml")) + sorted(WORKFLOWS.glob("*.yaml")):
        hits = _offending_lines(wf.read_text(encoding="utf-8"))
        if hits:
            bad[wf.name] = hits
    assert not bad, (
        "A workflow captures `$?` after a bare `;`. Under `bash -e` the shell dies before the "
        "assignment, so the exit code is never read and the step aborts with it. Use "
        "`VAR=0` then `cmd || VAR=$?`.\n"
        + "\n".join(
            f"  {name}:{n}: {line}" for name, hits in bad.items() for n, line in hits
        )
    )


def test_the_detector_actually_fires_on_the_shape_it_is_meant_to_catch():
    """A guard that cannot fail is not a guard (this repository has shipped two of those)."""
    assert _offending_lines("          cmd > /tmp/x 2>&1; _ARMED=$?")
    assert _offending_lines("          python3 a.py; rc=$?")
    # …and stands down on the correct idiom, and on a comment describing the bug.
    assert not _offending_lines("          cmd > /tmp/x 2>&1 || _ARMED=$?")
    assert not _offending_lines("          rc=0\n          python3 a.py || rc=$?")
    assert not _offending_lines("          # ⚠ `rc=0; cmd || rc=$?` AND NOT `cmd; rc=$?` — bash -e")
