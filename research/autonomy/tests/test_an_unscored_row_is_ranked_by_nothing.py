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
  7    the open unscored population does not GROW — the ratchet, landed 2026-08-29 on the
       follow-up row AUT-PD-145, together with its vacuity guard. See LANDED below.

⭐⭐ LANDED 2026-08-29 (AUT-PD-145, CYC-0083-381d0696), AND THE HISTORY BELOW IS KEPT RATHER
THAN DELETED, BECAUSE THE ENTRY CONDITION IS THE ONLY THING THAT MAKES THIS A DEFERRAL AND NOT
A RE-PINNING. `MAX_UNSCORED_OPEN` and `test_the_ratchet_is_not_vacuous` are now in this file,
verbatim from d082c01a78 apart from the pinned number, which is **73 — SEVEN LOWER than the 80
they were written against, not higher.** Both entry conditions were met and measured, not argued:
  (1) R5 landed on the trunk 2026-08-29 (CYC-0073-d4ccfde4): `admissibility.refuse_population_growth`
      refuses, at `ledger_io.write_ledger`, any write that puts a row INTO this population —
      appended unscored, a committed `score` removed, or a closed-and-exempt row reopened.
      Membership is grandfathered, which is why landing it was not an outage.
  (2) The population is FLAT, read the way condition (2) prescribes: `n_unscored_open` was 73 at
      every one of the 18 consecutive trunk ledger commits from 03:29:55Z to 07:47:50Z on
      2026-08-29 — 4.3 hours against a required window of 2, with no rise anywhere in it. It had
      fallen 88 -> 73 when R5 landed and has not moved since. ⚠ That series is what condition (2)
      asks for and it is the ONLY thing that licenses this pin; a flat window shorter than two
      hours, or any rise inside it, would put the pair back on the branch.
⛔ AND THE NUMBER WAS NOT CHOSEN TO FIT. 73 is the count in this very commit, so
`test_the_ratchet_is_not_vacuous` has zero slack — the strictest legal pin, not the safest one.

⛔⛔ WHY IT WAS DEFERRED IN THE FIRST PLACE, KEPT VERBATIM (AUT-PD-050, seat s6, 2026-08-28).
The suite as first written on branch `s1-aut-pd-050-unscored-rows` @ d082c01a78 carried an eighth
and ninth test — `test_the_open_unscored_population_does_not_grow`, a ratchet pinned at
`MAX_UNSCORED_OPEN = 80`, and `test_the_ratchet_is_not_vacuous`, the guard that stops that ceiling
being raised to fit. **They are correct and they were not weakened; they were not landed THEN.**
Neither had ever been on the trunk, so nothing on `main` lost a guard by their absence, and the
pair had to land TOGETHER and VERBATIM from that commit — a ratchet without its vacuity guard is
the self-serving version of the same change. They landed together, as required.

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



#: ⛔⛔ THE RATCHET, AND IT MAY ONLY EVER BE LOWERED. The count of OPEN ledger rows carrying no
#: `score`, measured on the tree this test was committed against. Closing a row lowers it; filing an
#: unscored row raises it and turns this red. **Lower it in the same commit that scores rows. Raising
#: it is weakening the bar to make a filing pass, which is the one edit `amendment_guard.py` exists
#: to refuse** — and there is no case for it, because the remedy costs one field on the row you just
#: filed. The number is NOT a target and not a budget: the honest end state is 0, at which point this
#: constant should be deleted and the assertion made absolute.
#: ⭐ LANDED 2026-08-29 BY CYC-0083-381d0696, PINNED AT THE COUNT MEASURED IN THIS COMMIT, which is
#: what AUT-PD-145 required and is 73 rather than the 80 the pair was written against. The ceiling
#: was NOT raised to fit — it was LOWERED by seven, because the population fell. See the DEFERRED
#: section of this module's docstring for the entry condition and the series that met it.
#: ⭐ LOWERED AGAIN 2026-08-29 BY CYC-0088-f7394a99, 73 -> 69, AND THE DIRECTION IS THE WHOLE POINT.
#: AUT-PD-177: three route ids in `serves.route` — `RT-ASO-JUNCTION`, `RT-FUSION-PARTNER` and
#: `RT-DEGRADER-TERNARY` — appear in NONE of the 77 routes in systems/graph/routes.json, so
#: `apply_route_inheritance` had no floor to give the rows naming them and four could never be
#: scored at all. Remapping each to the route the graph itself determines (the `primary` route for
#: the publication those rows name: RT-ASO, RT-PARTNER-STRAT, RT-DEGRADER) let all four inherit a
#: score, and the open unscored population fell 73 -> 69.
#: ⛔ THE CEILING HAD TO MOVE IN THE SAME COMMIT OR `test_the_ratchet_is_not_vacuous` GOES RED: it
#: allows at most 2 of slack, and 73 against a real 69 is 4. That coupling is deliberate and it only
#: ever forces the ceiling DOWN — a fix that shrinks the population must re-pin at the new count,
#: which is why this constant cannot drift upward by neglect. Superseded, retained: **73**, and
#: before it **80**. The honest end state is still 0.
#: ⭐⭐ 0 AS OF 2026-09-01, WHICH IS THE END STATE THE LINE ABOVE HAS BEEN NAMING SINCE THE RATCHET
#: LANDED: *"The honest end state is still 0."* The population is empty. `health.py`'s
#: `scores_are_reachable` had read UNRANKABLE-WORK for 88 hours — 68 open rows carrying no score, so
#: no cycle could be offered them and no handoff listed them. Seat S21-UNSCORED enumerated all 68,
#: settled every one, and the driver applied it: 65 scored with a prose `_score_basis`, 3 moved to
#: `done` because the work was finished and the row had simply never been closed.
#: ⛔ AND THE COUPLING THIS CONSTANT DOCUMENTS IS WHAT FORCED THE 0. The comment above is explicit
#: that a fix which shrinks the population must re-pin at the new count, and that the ceiling only
#: ever moves DOWN. 69 against a real 0 is 69 of slack against an allowance of 2, so
#: `test_the_ratchet_is_not_vacuous` would go red on exactly the commit that fixed the thing. The
#: coupling worked.
#: ★ WHAT THIS NOW MEANS, PLAINLY: any future write that appends an open row with no score turns
#: this red. That is the strictest this constant can ever be, and it is the direction the whole
#: file was built to travel. `admissibility.refuse_population_growth` refuses such a write at
#: `ledger_io.write_ledger`; this is the committed-file backstop for a write that goes around it —
#: and S21 measured that such a path exists, because a text edit bypasses `write_ledger` entirely.
#: Superseded, retained: **69**, before it **73**, before it **80**.
MAX_UNSCORED_OPEN = 0


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


# 7 -------------------------------------------------------------------------------------------
def test_the_open_unscored_population_does_not_grow():
    """⛔⛔ THE RATCHET, AND IT IS THE ONLY PART OF THIS SUITE THAT STOPS THE BLEEDING. Every one of
    the 24 rows filed in the observable trunk history joined this population; nothing has ever left
    it. A view that renders these rows and a report that counts them are both worth having and
    neither prevents the 25th.

    ★ IF THIS IS RED ON YOUR COMMIT, YOU FILED A LEDGER ROW WITH NO SCORE. The remedy is one field
    on that row — a `score` and a `_score_basis` saying why, or a `prerequisite_of` naming the row it
    unblocks, which derives one from the parent. ⛔ Do NOT raise `MAX_UNSCORED_OPEN`: that is
    weakening a bar so a filing passes, `amendment_guard.py` refuses it, and there is no version of
    this where a typed number is more expensive than the queue never seeing the work."""
    entries = _committed()["entries"]
    ids = _unscored_open(entries)
    assert len(ids) <= MAX_UNSCORED_OPEN, (
        f"{len(ids)} open ledger rows carry no `score` — up from the {MAX_UNSCORED_OPEN} this "
        f"ratchet was pinned at. A row with no score sorts below every scored row and no ranking "
        f"term can reach it, the anti-starvation age factor included, so it will never be picked. "
        f"Give the row(s) you filed a `score` and a `_score_basis`, or a `prerequisite_of`. "
        f"Newest unscored ids: {sorted(ids)[-6:]}")


def test_the_ratchet_is_not_vacuous():
    """⚠ A ceiling far above the real count asserts nothing (the vacuous-guard failure
    `paper-hardening` §8b names, and the one that let an emptied constant pass a parametrised test).
    The pin must sit ON the measured population, not above it.

    ⭐⭐ THE POPULATION REACHED ZERO ON 2026-09-01 AND THIS GUARD SAID SO ITSELF. Its own instruction
    when that happened was *"no open unscored rows at all — delete MAX_UNSCORED_OPEN and assert
    `not ids`"*, and that is what this now does. The ratchet is no longer a ceiling that may be
    approached; it is an absolute: **no open ledger row may carry no score, ever.**

    ★ `MAX_UNSCORED_OPEN` IS KEPT AT 0 RATHER THAN DELETED, deliberately, and the difference
    matters. The instruction said delete it; keeping it pinned at 0 makes the sibling ratchet above
    assert exactly the same thing, so the two tests cannot drift apart, and it leaves the
    supersession chain (80 → 73 → 69 → 0) readable at the constant a future reader will look for.
    ⛔ A deleted constant is also the easier thing to quietly reintroduce with a number on it.

    ⛔ AND THE VACUITY CHECK IS NOT RETIRED — IT IS INVERTED, WHICH IS STRICTER. It used to refuse a
    ceiling with slack. It now refuses any slack at all, because at 0 the only way to create slack
    is to raise the constant, and raising it is the edit `amendment_guard.py` exists to catch. If
    this file is ever found with `MAX_UNSCORED_OPEN > 0` again, the population grew and somebody
    re-pinned to fit — which is precisely the move this test was written to make impossible."""
    ids = _unscored_open(_committed()["entries"])
    assert not ids, (
        f"{len(ids)} open ledger row(s) carry no `score`, and the population has been EMPTY since "
        f"2026-09-01. A row with no score sorts below every scored row and no ranking term can "
        f"reach it — the anti-starvation age factor included — so it will never be picked. Give it "
        f"a `score` and a `_score_basis`, or a `prerequisite_of` naming the row it unblocks. "
        f"⛔ Do NOT raise MAX_UNSCORED_OPEN to make this pass. Ids: {sorted(ids)[:8]}")
    assert MAX_UNSCORED_OPEN == 0, (
        f"MAX_UNSCORED_OPEN is {MAX_UNSCORED_OPEN} against an EMPTY population. The only reason to "
        "raise it above 0 is to make room for an unscored row, which is the weakening this pair "
        "exists to refuse.")
