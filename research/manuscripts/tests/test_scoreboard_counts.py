"""⛔ THE SCOREBOARD HEADLINE MUST BE COUNTED FROM ITS OWN TABLE, NOT TYPED BESIDE IT.

★ WHY THIS EXISTS (2026-08-06, found by a verification read of the roadmap, not by CI).
`nr4a3-program-map.md`'s scoreboard is the first thing every session reads. Its headline said:

    As of 2026-08-02 3:30 AM ET · 7 gates passed · 4 failed · … · 4 deliverables done and 1 PARTIAL

Three things were wrong at once, and they are one failure — a total that was typed rather than derived,
which is exactly what CLAUDE.md rule 1.1 forbids for costs and had never been applied to counts:

  (a) the gate table showed only THREE failed rows, because the SMARCA2/4 gate had a section heading of
      its own and no row in the table §0.7 calls "the one home for every gate's verdict sentence";
  (b) the deliverables table has four rows — three DONE and one PARTIAL — never four done;
  (c) three further gates landed 2026-08-03 (`5b-T` NO-GO, `R3` GATE_A_FAIL, `R14-a` self-control FAIL),
      each recorded elsewhere on the page and none of them on the board.

Net: the scoreboard understated the program's failure record by four while reading as current. A headline
that undercounts failures is the single most dangerous kind of drift in this repository, because the
board exists to stop a session steering by a rosier picture than the evidence supports.

⚠ THIS TEST DELIBERATELY DOES NOT CHECK THE DATE OR THE SPEND. Those have their own homes and their own
checks; adding them here would make one test fail for four unrelated reasons and get skipped.
"""
from __future__ import annotations

import os
import re

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))          # research/manuscripts/tests
MANUSCRIPTS = os.path.dirname(HERE)                        # research/manuscripts
MAP = os.path.join(MANUSCRIPTS, "nr4a3-program-map.md")

GATE_HEADER = "| # | gate | status |"
DELIV_HEADER = "| deliverable | status |"


def _rows(lines, header):
    """The data rows of the markdown table whose header row starts with `header`."""
    start = next(i for i, l in enumerate(lines) if l.startswith(header))
    out = []
    for l in lines[start + 2:]:          # +2 skips the header and the |---|---| separator
        if not l.startswith("|"):
            break
        out.append([c.strip() for c in l.strip("|").split("|")])
    return out


def _bucket(status):
    """PASSED / FAILED / OTHER for one status cell.

    ⚠ ORDER MATTERS: "GATE FAILED, AS PRE-REGISTERED" contains neither word cleanly, and a naive
    `"PASSED" in s or "FAILED" in s` double-counts. Failure is checked FIRST so a row that says both
    (e.g. "PASSED — … it CLEARS" vs "GATE FAILED") lands on the honest side.
    """
    if "FAILED" in status or "NO-GO" in status:
        return "FAILED"
    if "PASSED" in status:
        return "PASSED"
    return "OTHER"


@pytest.fixture(scope="module")
def lines():
    with open(MAP, encoding="utf-8") as fh:
        return fh.read().split("\n")


@pytest.fixture(scope="module")
def headline(lines):
    """The whole headline, JOINED.

    ⚠ It wraps across several source lines and the gate counts and the deliverable counts sit on
    different ones — reading only the first line finds the gates and silently misses the deliverables,
    which is how the first draft of this test passed one half and errored on the other. Collect from the
    `**As of` line to the blank line that ends the paragraph.
    """
    for i, l in enumerate(lines):
        if l.startswith("**As of ") and "gates passed" in l:
            block = []
            for m in lines[i:]:
                if not m.strip():
                    break
                block.append(m)
            return " ".join(block)
    pytest.fail("the scoreboard headline (`**As of … gates passed …`) is gone — if it moved, move this test")


def test_the_headline_gate_counts_are_the_table_s_counts(lines, headline):
    """passed/failed in the headline == passed/failed rows in the gate table."""
    rows = _rows(lines, GATE_HEADER)
    assert rows, "the gate table has no rows"
    got = {"PASSED": 0, "FAILED": 0, "OTHER": 0}
    for r in rows:
        got[_bucket(r[2])] += 1

    m = re.search(r"(\d+)\s+gates? passed\s*·\s*(\d+)\s+failed", headline)
    assert m, f"cannot parse the gate counts out of the headline:\n{headline}"
    said_pass, said_fail = int(m.group(1)), int(m.group(2))

    assert (said_pass, said_fail) == (got["PASSED"], got["FAILED"]), (
        f"the scoreboard headline says {said_pass} passed / {said_fail} failed, but its own table has "
        f"{got['PASSED']} passed / {got['FAILED']} failed ({got['OTHER']} neither).\n"
        f"⛔ A gate recorded ONLY in a section heading is a gate this board cannot show. If you added a "
        f"heading, add the row — do not adjust the headline to match a table that is missing one."
    )


def test_the_headline_deliverable_counts_are_the_table_s_counts(lines, headline):
    """done/PARTIAL in the headline == DONE/PARTIAL rows in the deliverables table."""
    rows = _rows(lines, DELIV_HEADER)
    assert rows, "the deliverables table has no rows"
    done = sum(1 for r in rows if "DONE" in r[1] and "PARTIAL" not in r[1])
    partial = sum(1 for r in rows if "PARTIAL" in r[1])

    m = re.search(r"(\d+)\s+deliverables? done and\s+(\d+)\s+PARTIAL", headline)
    assert m, f"cannot parse the deliverable counts out of the headline:\n{headline}"
    said_done, said_partial = int(m.group(1)), int(m.group(2))

    assert (said_done, said_partial) == (done, partial), (
        f"the scoreboard headline says {said_done} done / {said_partial} PARTIAL, but its own table has "
        f"{done} done / {partial} PARTIAL over {len(rows)} row(s)."
    )


def test_every_gate_row_states_a_gradeable_verdict(lines):
    """⭐ THE GUARD AGAINST FIXING THIS BY GOING VAGUE.

    Both tests above compare a headline to a bucketing, so both could be satisfied by rewording every
    status into something that buckets as OTHER. That would make the board unreadable while green. A row
    may legitimately be neither passed nor failed — `RUNG 4` RAN AND ANSWERED `DISCORDANT`, and the fan-out
    was DELIVERED BUT NOT GRADED — so this asserts a ceiling, not zero.
    """
    rows = _rows(lines, GATE_HEADER)
    other = [r for r in rows if _bucket(r[2]) == "OTHER"]
    assert len(other) <= 3, (
        f"{len(other)} of {len(rows)} gate rows state neither a pass nor a failure:\n  "
        + "\n  ".join(f"{r[0]} — {r[2][:80]}" for r in other)
        + "\n⛔ A scoreboard whose rows mostly say something ungradeable is not a scoreboard."
    )
