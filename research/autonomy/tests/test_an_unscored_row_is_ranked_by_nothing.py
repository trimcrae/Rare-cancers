#!/usr/bin/env python3
"""A ledger row with no `score` is ordered by NOTHING, and nothing said so (AUT-PD-050).

⛔⛔ THE DEFECT, MEASURED ON THE COMMITTED LEDGER BEFORE ANY CODE WAS CHANGED (2026-08-28).
`research-ledger.json` carried 260 rows, of which **97 had no `score` at all** — every one of them
hand-filed; not one derived row was unscored. `build_ledger` sorts with
`-(score if score is not None else -1e9)`, so those 97 occupied ranks 164-260 CONTIGUOUSLY, pinned to
the bottom by construction, ordered among themselves by id string. Two rows tied at the same
`age_factor` of 0.1429 landed at positions 3 and 90 of that block. 80 of the 97 were OPEN, and 75 of
the 98 rows `continuity.ready()` offered a session were unscored.

⭐ THE ANTI-STARVATION TERM RAN ON THEM AND MOVED NOTHING, WHICH IS THE WHOLE FAILURE. `apply_age_factor`
guards its arithmetic with `if isinstance(e.get("score"), (int, float))`, so for 17 of those rows it
computed a real age factor, WROTE IT into `score_inputs` — and could not apply it. The term added by
AUT-PD-048 explicitly to rescue starved rows is dead code against the only starving class in the
queue, and the row advertised an input its score did not contain.

⛔ AND THE POPULATION ONLY GROWS. Every commit of `research-ledger.json` in the observable trunk
history (32 commits, 17:26-20:34 on 2026-08-28) was read back with `git show`:

    total 236 -> 260   unscored 73 -> 97   unscored_open 64 -> 80

**24 rows were filed in that window and 24 of 24 carry no score. Zero pre-existing unscored rows
ever acquired one.** So an unscored row is not an oversight on a few old entries; it is what filing
a row DOES, and nothing in the loop reduces the count.

★★ THE POLICY WAS ALREADY DECIDED — THIS SUITE ENFORCES IT RATHER THAN INVENTING ONE.
`test_priority_ranks_the_hand_filed_entries_too.py` states the invariant in as many words: *"a
hand-filed entry is HAND-SCORED, not unscorable. It carries a `score` its filer typed and a
`_score_basis` in prose."* And the alternative — having the scorer derive one — is refused by
`admissibility.py`, which grades a hand-filed number `unaccounted` precisely so a fabricated
derivation cannot masquerade as a computed one ("an entry with a full set of zeroed inputs looks
computed, and the arithmetic printed beside it would be arithmetic nobody did"). Defaulting these
rows to zero is refused for the third reason the item itself gives: it would make the starvation
SILENT rather than visible.

⚠ WHY IT WAS NEVER ENFORCED: `admissibility.UNSCORED` existed, was documented, and was returned by
`verdict()` — and a repo-wide grep for it found hits in NO file but its own. Nothing counted it,
no test asserted on it, and `admissibility.py --report`'s own closing sentence explained `admitted`
and `unaccounted` and omitted the largest bucket. The same shape as `subagent_width` governing
nothing for a fortnight, and as `research/autonomy/tests` itself being run by nothing.

WHAT EACH TEST HOLDS DOWN
  1-3  the two views that print a score survive a row that has none, and the sibling field on the
       same statement (`serves.route`, missing from 9 committed rows) survives with it.
  4    neither view prints a NUMBER for a row that has none. `continuity.py` printed `[   0.0]`.
  5    the two rankers order a missing score the SAME way — they did not.
  6    the generator counts the population into the artifact.
  7    NOT LANDED HERE — see DEFERRED below. The ratchet belongs to a follow-up row.

⛔⛔ DEFERRED, AND SEQUENCING IS THE ONLY REASON (AUT-PD-050, seat s6, 2026-08-28).
The suite as first written on branch `s1-aut-pd-050-unscored-rows` @ d082c01a78 carried an eighth
and ninth test — `test_the_open_unscored_population_does_not_grow`, a ratchet pinned at
`MAX_UNSCORED_OPEN = 80`, and `test_the_ratchet_is_not_vacuous`, the guard that stops that ceiling
being raised to fit. **They are correct and they are not weakened here; they are not landed here.**
Neither has ever been on the trunk, so nothing on `main` loses a guard by their absence, and the
pair must land TOGETHER and VERBATIM from that commit — a ratchet without its vacuity guard is the
self-serving version of the same change.

★ WHY NOT NOW, MEASURED RATHER THAN ARGUED. The ceiling was pinned at 80 against the population
`s1` measured at 20:34 UTC. Re-measured by reading back all 248 commits of `research-ledger.json`
in the observable trunk history: the open unscored population was **82 at 22:03 UTC on the same
day**, i.e. the ratchet is ALREADY red on the tree it would be merged into, and the net filing rate
over the preceding 2.8 hours was **+10 rows, about 3.6 an hour**. Landing it would turn `main` red
on arrival, for whichever session files a row next, on a gate that session did not cause and whose
remedy is not in its prompt — and `research-loop` §1 makes a red trunk stop every cycle. That is a
loop-wide outage bought to enforce a rule no filer has been told about.

★★ THE ENTRY CONDITION, so this is a deferral and not a quiet burial. The ratchet lands when BOTH
hold, and it is pinned at the count measured in the same commit:
  (1) **The filing path supplies the remedy, and it already has one home.**
      `ledger_io.write_ledger` is the single serialization every writer of `research-ledger.json`
      passes through, and it ALREADY runs an admission gate there — `admissibility.check_write`,
      which refuses a score change nothing can account for. An appended row with no `score` and no
      `prerequisite_of` belongs to the same gate, refused at the write with the remedy in the
      message. Until the filer is told at the moment of filing, a ratchet only punishes a
      downstream session for an upstream omission, which is the blast radius that deferred it.
  (2) **The population is flat or falling**, read the way it was read here: open-unscored is not
      higher at the end of a ≥2-hour window of trunk commits than at its start. It rose 64 at
      17:26 UTC to 82 at 22:12 UTC on 2026-08-28 — +18 across 4h46m over 47 ledger commits, whose
      steps were 8 falls of exactly one row against rises of up to five: the population does not
      merely trend up, it has no mechanism that removes more than one row at a time. A ratchet
      pinned today is a ratchet red tomorrow.
⛔ NEITHER CONDITION IS "raise the number". Raising `MAX_UNSCORED_OPEN` to create headroom is the
edit `test_the_ratchet_is_not_vacuous` exists to catch, and deferring the test does not license
making by omission the change the test refuses.
"""

from __future__ import annotations

import io
import json
import os
import sys
from contextlib import redirect_stdout

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
AUTONOMY = os.path.dirname(HERE)
sys.path.insert(0, AUTONOMY)

import admissibility as A  # noqa: E402
import continuity  # noqa: E402
import priority  # noqa: E402

LEDGER = os.path.join(AUTONOMY, "research-ledger.json")



def _committed():
    with open(LEDGER, encoding="utf-8") as fh:
        return json.load(fh)


def _unscored_open(entries):
    return [e["id"] for e in entries
            if e.get("score") is None
            and (e.get("state") or "queued") not in priority.CLOSED_STATES]


# 1 -------------------------------------------------------------------------------------------
def test_the_ranked_table_survives_a_row_with_no_score():
    """⛔ THE EXACT CRASH: `python3 research/autonomy/priority.py --limit 300` raised
    `TypeError: unsupported format string passed to NoneType.__format__` at `entry['score']:>7.1f`.

    ⚠ A CONSTRUCTED LEDGER, NOT THE COMMITTED ONE, because the committed ledger is the thing this
    suite's ratchet is trying to empty — a test that needs an unscored row to exist would go green
    for the wrong reason on the day the defect is finally cleared."""
    entries = [
        {"id": "AUT-X-001", "kind": "proposal", "cost_class": "free",
         "serves": {"route": "RT-X"}, "what": "a row nobody scored"},              # no `score` key
        {"id": "AUT-X-002", "score": None, "kind": "fix", "cost_class": "free",
         "serves": {"route": "RT-X"}, "what": "a row scored explicitly null"},     # the other shape
        {"id": "AUT-X-003", "score": 12.5, "kind": "fix", "cost_class": "free",
         "serves": {"route": "RT-X"}, "what": "a row that IS scored"},
    ]
    table = priority._table(entries, limit=10)  # must not raise
    assert "a row that IS scored" in table, "the fix blanked out a scored sibling"
    assert "a row nobody scored" in table and "a row scored explicitly null" in table, (
        "an unscored row must still appear in the table — the whole defect is that these rows are "
        "invisible, and rendering them as nothing would be the same failure in a new place")


# 2 -------------------------------------------------------------------------------------------
def test_the_ranked_table_survives_the_sibling_field_on_the_same_statement():
    """⚠ THE ONE-OF-A-PAIR CLASS (`paper-hardening` §8b.2). The crashing statement carried THREE
    bare indexes — `entry['score']`, `entry['kind']`/`entry['cost_class']`, `entry['serves']['route']`
    — and 9 committed rows carry no `serves.route`. Fixing the score alone would have made those 9
    the next crash, discovered by the next reader rather than by this suite."""
    entries = [{"id": "AUT-X-004", "what": "no score, no route, no kind, no cost_class"}]
    table = priority._table(entries, limit=10)  # must not raise KeyError or TypeError
    assert "no score, no route" in table


# 3 -------------------------------------------------------------------------------------------
def test_the_ready_list_survives_a_row_with_no_score(monkeypatch):
    """⛔ MEASURED: `python3 research/autonomy/continuity.py --limit 30` died with the identical
    `TypeError` at ready-rank 29, while the default `--limit 10` never reached it. The view a session
    uses to look PAST the top ten — i.e. to look at the starved rows — was the one that crashed.

    ⚠ AND THE LIMIT IN THAT SENTENCE IS A DATED READING, NOT A PROPERTY (re-measured by seat s6 five
    hours later, on the pre-fix tree): `--limit 30` had by then stopped reaching an unscored row and
    exited 0, because the ready population had grown past 30 SCORED rows — the crash reproduces at
    `--limit 300`. The threshold moves with the queue and the defect does not, which is why this
    test constructs its rows instead of asserting on a limit."""
    rows = [
        {"id": "AUT-X-005", "score": 50.0, "what": "scored"},
        {"id": "AUT-X-006", "score": None, "what": "explicitly null"},
        {"id": "AUT-X-007", "what": "no key at all"},
    ]
    monkeypatch.setattr(continuity, "ready", lambda me=None: rows)
    monkeypatch.setattr(continuity, "blocked", lambda me=None: [])
    buf = io.StringIO()
    with redirect_stdout(buf):
        continuity.main(["--limit", "10"])  # must not raise
    out = buf.getvalue()
    assert "AUT-X-006" in out and "AUT-X-007" in out


# 4 -------------------------------------------------------------------------------------------
@pytest.mark.parametrize("row", [
    {"id": "AUT-X-008", "kind": "fix", "cost_class": "free", "serves": {"route": "RT-X"},
     "what": "no key"},
    {"id": "AUT-X-009", "score": None, "kind": "fix", "cost_class": "free",
     "serves": {"route": "RT-X"}, "what": "explicit null"},
])
def test_no_view_prints_a_number_for_a_row_that_has_none(row, monkeypatch):
    """⛔⛔ CLAUDE.md §4: a populated field is not a measured one. `continuity.py` printed
    `[   0.0]` for the 91 rows that omit the key — a confident, computed-looking zero, in the list
    the driver reads to choose what to work on, for a row nobody had scored at all. A real 0.0 and
    an absent score must not render alike, and two committed rows DO score exactly 0.0."""
    table = priority._table([row], limit=5)
    assert priority.NO_SCORE in table
    assert "0.0" not in table.split(row["what"])[0], (
        "the table printed a numeric score for a row that has none")

    monkeypatch.setattr(continuity, "ready", lambda me=None: [row])
    monkeypatch.setattr(continuity, "blocked", lambda me=None: [])
    buf = io.StringIO()
    with redirect_stdout(buf):
        continuity.main(["--limit", "5"])
    line = [ln for ln in buf.getvalue().splitlines() if row["id"] in ln][0]
    assert priority.NO_SCORE in line and "0.0" not in line, line


# 5 -------------------------------------------------------------------------------------------
def test_both_rankers_order_a_missing_score_the_same_way():
    """⛔ THEY DID NOT, AND THE FIX IS A SHARED FUNCTION RATHER THAN TWO COPIES THAT AGREE.
    `build_ledger` sorted unscored rows at `-1e9`; `continuity.ready` sorted them at `or 0`, i.e.
    ABOVE any negatively-scored row and identical to a real 0.0. Both now call
    `priority.score_rank`, so the two cannot drift apart again — a test that wrote the key out a
    third time would assert its own copy, which is the agreement-in-prose failure this repository
    keeps paying for (AUT-PD-013's fan-out key, AUT-PROP-013's ids, AUT-PD-037's serialization)."""
    import copy
    from unittest import mock

    rows = [
        {"id": "AUT-X-010", "score": -40.0, "serves": {"route": "RT-B"}, "what": "penalised"},
        {"id": "AUT-X-011", "serves": {"route": "RT-C"}, "what": "unscored"},
        {"id": "AUT-X-012", "score": 0.0, "serves": {"route": "RT-A"}, "what": "a real zero"},
    ]
    expected = ["AUT-X-012", "AUT-X-010", "AUT-X-011"]

    ranker = sorted(copy.deepcopy(rows),
                    key=lambda e: (priority.score_rank(e),
                                   str(e.get("serves", {}).get("route") or e["id"])))
    assert [e["id"] for e in ranker] == expected

    with mock.patch.object(continuity, "_entries", return_value=copy.deepcopy(rows)), \
            mock.patch.object(continuity, "_why_not_ready", return_value=None), \
            mock.patch.object(continuity.handoff, "terminal_ids", return_value=set()):
        got = [e["id"] for e in continuity.ready()]
    assert got == expected, f"the ready list ranks a missing score differently from the ranker: {got}"


def test_the_shared_ordering_is_actually_shared_by_both_call_sites():
    """⚠ THE WIRING, ASSERTED. A shared function nobody calls is the `subagent_width` shape: correct,
    documented, and governing nothing. Mutation-tested by reverting either call site to its own
    lambda, which this test catches and the ordering test above does NOT (two hand-written copies
    that happen to agree still produce the expected order)."""
    for path in ("priority.py", "continuity.py"):
        src = open(os.path.join(AUTONOMY, path), encoding="utf-8").read()
        assert "score_rank(e)" in src, f"{path} no longer orders through priority.score_rank"
    assert priority.score_rank({"id": "x"}) == 1e9, "an unscored row must sort last"
    assert priority.score_rank({"id": "x", "score": None}) == 1e9, "both spellings of 'no score'"
    assert priority.score_rank({"id": "x", "score": 0.0}) == 0.0, "a real zero is not 'no score'"
    assert priority.score_rank({"id": "x", "score": -5}) == 5.0


# 6 -------------------------------------------------------------------------------------------
def test_the_generated_ledger_counts_its_own_unscored_rows():
    """⛔ `admissibility.UNSCORED` was a grade nothing counted anywhere a reader looks. The count is
    now DERIVED into the artifact beside `n_by_kind` and `n_clamped`, never typed."""
    led = priority.build_ledger()
    assert "n_unscored" in led and "n_unscored_open" in led
    entries = led["entries"]
    assert led["n_unscored"] == sum(1 for e in entries if e.get("score") is None)
    assert led["n_unscored_open"] == len(_unscored_open(entries))
    assert led["n_unscored_open"] <= led["n_unscored"]
    assert "`score`" in led["_role"] and "_score_basis" in led["_role"], (
        "the ledger's own `_role` must state the requirement a filer is meant to meet — it is the "
        "one text every session reading this file actually opens")


def test_the_closed_state_scope_is_one_fact_shared_by_both_readers():
    """One fact, one place: `apply_age_factor` refuses to age these states and `n_unscored_open`
    refuses to count them, so the two must read the same constant, and `admissibility` must agree."""
    assert priority.CLOSED_STATES == ("done", "abandoned", "superseded")
    assert A.CLOSED_STATES == set(priority.CLOSED_STATES)


def test_the_scoring_audit_explains_the_grade_it_reports():
    """⛔ `admissibility.py --report` printed `{"admitted": 77, "unaccounted": 86, "unscored": 97}`
    and a closing sentence that explained the first two and omitted the third — the LARGEST bucket
    left as a number with no reading. An absent reading is not a reading of absence (CLAUDE.md §4),
    and a grade nobody explains is how `UNSCORED` sat in this module for a week, returned by
    `verdict()` and referenced by no other file in the repository."""
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = A.main(["--report"])
    out = buf.getvalue()
    assert rc == 0
    for grade in (A.ADMITTED, A.UNACCOUNTED, A.UNSCORED):
        assert f"`{grade}`" in out, f"the report never explains what `{grade}` means"
    assert "_score_basis" in out and "prerequisite_of" in out, (
        "the report names a population it does not tell the reader how to clear")


