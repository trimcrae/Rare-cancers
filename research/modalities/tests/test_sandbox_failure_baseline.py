"""The sandbox failure baseline must exist, be well-formed, and actually be READ by preflight.

⛔ WHY THIS FILE EXISTS (2026-08-08). scripts/preflight.sh used to tolerate a COUNT of sandbox test
failures and assert they were "all dep-related" without checking. A genuine regression took the count
from 48 to 49, fitted under the baseline of 50, and the gate printed PREFLIGHT OK; that tree was
pushed and turned `main` red. The fix replaced the count with a LIST — sandbox-failure-baseline.txt —
so anything absent from it fails the build by name.

⚠ A LIST IS ONLY A FIX WHILE SOMETHING READS IT. This repository has already been bitten by exactly
that: fleet_armed.CENSUS_LANE was documented in three places and wired to a name no caller passed, so
the design read as safe while the artifact it protected was the one being dropped
(tests/test_fleet_armed.py::test_the_exempt_census_lane_is_actually_used_by_the_census_writer). A
baseline file that preflight stopped consulting would fail in the same shape and with no symptom —
the gate would go green, as it did before, and nobody would know the list had been orphaned. So the
wiring is ASSERTED here rather than described in a comment.
"""

from __future__ import annotations

import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))          # research/modalities/tests
# ⚠ THREE levels up, not two. The first version of this line stopped at `research/` and every path
# built from it missed — the same off-by-one-directory bug CLAUDE.md §6 records for the committed
# census lookup, which fail-quiet made symptomless there. Here the tests below went red immediately,
# which is the whole reason they resolve real paths instead of monkeypatching the seam.
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
BASELINE = os.path.join(HERE, "sandbox-failure-baseline.txt")
PREFLIGHT = os.path.join(ROOT, "scripts", "preflight.sh")
REL = "research/modalities/tests/sandbox-failure-baseline.txt"


def _entries() -> list[str]:
    with open(BASELINE, encoding="utf-8") as fh:
        return [ln.strip() for ln in fh
                if ln.strip() and not ln.lstrip().startswith("#")]


def test_the_baseline_file_exists_and_is_not_empty():
    assert os.path.exists(BASELINE), f"{REL} is missing; preflight fails closed without it"
    assert _entries(), "an empty baseline would tolerate nothing and is probably a truncation bug"


def test_every_entry_is_a_well_formed_test_id():
    """`path::test_name`, pointing at a file that exists. A typo'd entry silently tolerates nothing —
    the real failure it was meant to cover then reads as NEW and the build goes red for the wrong
    reason, which is the confusing direction rather than the dangerous one, but still wrong."""
    bad = []
    for e in _entries():
        if "::" not in e:
            bad.append((e, "no '::' separator"))
            continue
        path = e.split("::", 1)[0]
        if not path.startswith("research/modalities/tests/"):
            bad.append((e, "path is outside the modalities test tree"))
        elif not os.path.exists(os.path.join(ROOT, path)):
            bad.append((e, "test file does not exist"))
    assert not bad, f"malformed baseline entries: {bad[:5]}"


def test_entries_are_unique_and_sorted():
    """Unsorted or duplicated entries make the diff against a fresh run unreadable, which is how a
    list quietly degrades back into the count it replaced."""
    e = _entries()
    assert len(e) == len(set(e)), f"duplicate entries: {sorted({x for x in e if e.count(x) > 1})}"
    assert e == sorted(e), "baseline is not sorted; regenerate with the command in its header"


def test_preflight_actually_reads_the_baseline():
    """⛔ THE LOAD-BEARING ONE. Asserts the wiring, not the intent.

    If preflight stops referencing this path, the gate reverts to trusting a bare count and the
    incident above recurs with no symptom — a green line from a check that measures less than it
    claims. Naming the file in a comment would not be enough; it has to be read.
    """
    with open(PREFLIGHT, encoding="utf-8") as fh:
        src = fh.read()
    assert REL in src, (
        f"scripts/preflight.sh no longer mentions {REL}. If the gate has been rewritten, this test "
        f"must be updated deliberately — do not delete it to go green.")
    # And it must be consumed, not merely named in prose: the path is assigned and then diffed.
    assert re.search(r'base=\S*sandbox-failure-baseline\.txt', src), \
        "the baseline path appears in preflight but is not assigned to the variable the gate diffs"
    assert "comm -23" in src, \
        "preflight names the baseline but no longer diffs against it; the list is orphaned"


def test_the_gate_fails_closed_when_the_baseline_is_absent():
    """A missing list must go RED, never fall back to a count. Read from the source rather than
    executed, because running preflight here would take ~20 minutes."""
    with open(PREFLIGHT, encoding="utf-8") as fh:
        src = fh.read()
    assert re.search(r'if \[ ! -f "\$base" \]; then', src), \
        "preflight no longer checks that the baseline exists before relying on it"
