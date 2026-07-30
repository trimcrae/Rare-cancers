#!/usr/bin/env python3
"""A gate that DECLINED to buy and a gate that is WAITING for a price must never print the same sentence.

★★ WHAT THIS CAUGHT (2026-07-29, 11:16 AM ET). `ternary_vast_launch --gate-for-mode` exits 4 when the failure
breaker is withholding units. The valB closure triangle's four legs went blocked on the partial-charge defect
(15, 15, 7 and 21 dead hosts each), the launcher printed `⛔ BLOCKED ON REPEATED FAILURE` with every count —
and the job annotation one line below it read:

    ::warning title=TRIANGLE MARKET HOLD::the valB closure triangle is HELD on price. … Re-checks on the next
    tick and launches itself the moment it clears.

Both halves are false, and each is false in a way that costs something real:

  * "HELD on price" names the MARKET as the cause of a stall whose cause is a code fault. CLAUDE.md §4 then
    sends the next reader to diagnose the board — the one place where there is nothing to find.
  * "launches itself the moment it clears" is the expensive half. A price hold is SELF-CLEARING: it is a true
    statement that the lane is alive and waiting on a number that moves without anyone's help, so the correct
    response is to do nothing. A breaker block is its exact opposite — nothing about the market will ever
    change it, and the remedy (fix the cause, then supersede the record) only ever happens if a human is
    told. A lane stalled forever therefore looked, in the only place an operator reads, exactly like a lane
    patiently waiting out an expensive hour.

This is CLAUDE.md §1's "a row we are paying and a row the gate refused must never render alike" seen from the
other side: there the complaint was one glyph for two meanings, here it is one sentence for two states. Same
rule — ONE GLYPH, ONE MEANING — and the same reason it is enforced in a test rather than remembered.

⚠ AND IT WAS IN **BOTH** GATES. The valB_mini gate had recorded `blocked` in its ledger since the breaker went
live, which is why the hole survived: the machine-readable artifact was right the whole time and only the
human-readable annotation lied. Fixing the triangle alone would have left the older, more frequently-run gate
carrying the identical defect — so the assertion is written over EVERY step that calls `--gate-for-mode`,
present and future, rather than over the two known bodies.

WHAT IS ASSERTED, and why it is a structural property rather than a string match. A step that can receive
exit 4 must (1) branch on it and (2) do so BEFORE the fall-through price-hold text can be reached. Ordering is
the whole property: an RC=4 branch that sits after the hold `echo` compiles, tests clean against a naive
"mentions RC=4" check, and still prints the wrong sentence — which is precisely the shape of the bug.
"""

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _skip_guard import skip_module    # noqa: E402

try:
    import yaml
except ImportError:  # pragma: no cover
    skip_module("PyYAML unavailable")

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..")
WF_DIR = os.path.join(ROOT, ".github", "workflows")

# The launcher's own exit contract. Kept here as a comment rather than imported: this test must stay readable
# by someone holding only the workflow file, and the numbers are asserted against the workflow text anyway.
#   0 = clear to rent · 1 = hold on price · 3 = nothing needs a host · 4 = withheld by the failure breaker
BREAKER_RC = "4"

# The vocabulary a PRICE hold is allowed to use, lowercased. A breaker block must not reach any of it.
PRICE_HOLD_MARKERS = ("held on price", "hold on price", "market hold")


def _acts_on_the_exit_code(body):
    """Does this step DECIDE on the gate's verdict, or merely print its board?

    ⚠ THE DISTINCTION IS REAL AND THIS TEST MUST RESPECT IT. The `launch` job opens with an ADVISORY board
    snapshot — `--mode "$MODE" --gate-for-mode --gate-out /tmp/launch-board.json || true` — whose whole
    purpose is to price the market for the receipt without changing what happens next. It discards the exit
    code by construction, prints no hold wording, and therefore cannot mis-attribute anything. Requiring it
    to branch on exit 4 would be requiring a branch with nothing on either side of it, and the first person
    to hit that would (rightly) loosen this test rather than the workflow. So: a step that captures the code
    (`|| RC=$?`) is deciding and is in scope; one that swallows it (`|| true`) is reporting and is not.
    """
    return bool(re.search(r"\|\|\s*RC=\$\?", body))


def _gate_steps():
    """(workflow file, job name, step name, run body) for every step that DECIDES on the mode gate."""
    out = []
    for fn in sorted(os.listdir(WF_DIR)):
        if not fn.endswith((".yml", ".yaml")):
            continue
        with open(os.path.join(WF_DIR, fn)) as fh:
            try:
                doc = yaml.safe_load(fh)
            except Exception:      # test_workflows_parse.py owns unparseable YAML; do not double-report it
                continue
        if not isinstance(doc, dict):
            continue
        for job_name, job in (doc.get("jobs") or {}).items():
            if not isinstance(job, dict):
                continue
            for step in job.get("steps") or []:
                if not isinstance(step, dict):
                    continue
                body = step.get("run") or ""
                if "--gate-for-mode" in body and _acts_on_the_exit_code(body):
                    out.append((fn, job_name, step.get("name") or "<unnamed>", body))
    return out


def test_the_advisory_snapshot_is_excluded_for_the_stated_reason_not_by_accident():
    """Pin the exclusion itself, so `|| true` never becomes the way a real gate escapes these assertions.

    If a DECIDING gate is ever rewritten to swallow its exit code, it drops out of `_gate_steps` silently and
    every assertion above passes vacuously for it. That would be a worse bug than the one this file exists to
    stop. So: any step that both swallows the code AND carries price-hold wording is a contradiction — it is
    claiming a market verdict it did not read — and fails here.
    """
    for fn in sorted(os.listdir(WF_DIR)):
        if not fn.endswith((".yml", ".yaml")):
            continue
        with open(os.path.join(WF_DIR, fn)) as fh:
            try:
                doc = yaml.safe_load(fh)
            except Exception:
                continue
        if not isinstance(doc, dict):
            continue
        for job_name, job in (doc.get("jobs") or {}).items():
            if not isinstance(job, dict):
                continue
            for step in job.get("steps") or []:
                if not isinstance(step, dict):
                    continue
                body = step.get("run") or ""
                if "--gate-for-mode" not in body or _acts_on_the_exit_code(body):
                    continue
                low = body.lower()
                assert not any(m in low for m in PRICE_HOLD_MARKERS), (
                    f"{fn}:{job_name}:{step.get('name')} discards the gate's exit code but still reports a "
                    f"price hold. It cannot know whether the gate held on price, on the breaker, or not at "
                    f"all — either capture the code with `|| RC=$?` or drop the hold wording."
                )


def test_there_is_at_least_one_gate_step_to_check():
    """Guard against the assertions below passing vacuously if the flag is ever renamed."""
    steps = _gate_steps()
    assert steps, "no step invoking --gate-for-mode was found; if the flag was renamed, update this test"


def test_every_gate_branches_on_the_breaker_exit_code():
    for fn, job, name, body in _gate_steps():
        assert re.search(r'"\$RC"\s*=\s*' + BREAKER_RC, body), (
            f"{fn}:{job}:{name} calls --gate-for-mode but never branches on exit {BREAKER_RC} "
            f"(withheld by the failure breaker), so a breaker block falls through to whatever the last "
            f"branch says — which is how the triangle gate came to print 'HELD on price' at four blocked units."
        )


def test_the_breaker_branch_comes_before_any_price_hold_text():
    """The ordering IS the property — see the module docstring."""
    for fn, job, name, body in _gate_steps():
        low = body.lower()
        first_hold = min([low.find(m) for m in PRICE_HOLD_MARKERS if low.find(m) != -1] or [-1])
        if first_hold == -1:
            continue                       # a gate with no price-hold wording cannot mis-attribute to one
        # The branch that ACTS on RC=4 (as opposed to the ledger row or the commit-word case statement) is
        # the one that exits; find the last RC=4 test that precedes the hold text and require it to exist.
        guards = [m.start() for m in re.finditer(r'"\$RC"\s*=\s*' + BREAKER_RC, body)]
        assert any(g < first_hold for g in guards), (
            f"{fn}:{job}:{name} tests $RC={BREAKER_RC} only AFTER its price-hold text at offset {first_hold}. "
            f"A breaker block would reach the hold wording first and be reported as a market condition."
        )


def test_the_breaker_branch_exits_rather_than_falling_through():
    for fn, job, name, body in _gate_steps():
        low = body.lower()
        if not any(m in low for m in PRICE_HOLD_MARKERS):
            continue
        # Take the text from the acting RC=4 guard to the end of its `fi`, and require an `exit` inside it.
        m = None
        # (?<!el) matters: `elif [ "$RC" = 4 ]` is the LEDGER row, which records the cause and then falls
        # through. Only a bare `if` opens a branch that can exit. Without the lookbehind the ledger
        # elif satisfies the search and the test passes on a workflow that still mis-reports.
        for cand in re.finditer(r'(?<!el)if\s*\[\s*"\$RC"\s*=\s*' + BREAKER_RC + r'\s*\]\s*;\s*then', body):
            m = cand
        assert m, (f"{fn}:{job}:{name} has no `if [ \"$RC\" = {BREAKER_RC} ]` guard — an `elif` in the ledger "
                   f"chain records the row but does not stop the fall-through to the price-hold text.")
        tail = body[m.end():]
        fi = tail.find("\nfi")
        block = tail if fi == -1 else tail[:fi]
        # `fi` may be indented; be permissive about leading whitespace rather than pinning a column.
        indented = re.search(r"\n\s*fi\b", tail)
        if indented:
            block = tail[:indented.start()]
        assert re.search(r"\bexit\s+\d", block), (
            f"{fn}:{job}:{name}'s $RC={BREAKER_RC} branch does not exit, so execution continues into the "
            f"price-hold wording and the block is reported as a market condition anyway."
        )


def test_a_breaker_block_is_recorded_under_its_own_ledger_word():
    """`blocked`, never `refused-on-price` — the artifact and the annotation must agree on the cause."""
    for fn, job, name, body in _gate_steps():
        if not re.search(r'"\$RC"\s*=\s*' + BREAKER_RC, body):
            continue
        assert "--record blocked" in body, (
            f"{fn}:{job}:{name} branches on exit {BREAKER_RC} but never files the `blocked` ledger word, so "
            f"the durable record of the stall carries a market cause it did not have."
        )
