---
id: DOC-SPRINT-S49-BLOCKER-LEVERAGE
title: "The blocker-leverage term has no defect; its cap governs 80.5% of routes and nothing measured it"
level: L3
kind: memo
status: live
purpose: "Record that the dispatched defect did not exist, that the term is correct on its own terms, and that the load-bearing thing was an uncapped-vs-capped cap read by one line and asserted by no test — plus the tempting fix that was refused on measurement."
scope: "One scoring term and its cap. No scorer arithmetic was changed and no score moved; what shipped is a test and prose. Says nothing about whether the weight itself is right."
audience: [autonomous research agents, maintainers]
date: 2026-09-02
last_verified: 2026-09-02
---

# S49 — `_blocker_leverage`: no defect, and a cap that governed a queue with nothing measuring it

**Seat:** `SPRINT-2026-09-01/S49-BLOCKER-LEVERAGE`, 2026-09-02, tree at `b4cf28c6b`.
**Verdict: the dispatch premise was false, the term is correct on its own terms, and the tempting
correction was measured and REFUSED.** What was actually wrong is one level down: the constant that
makes the term safe was read by one line and asserted by nothing.

---

## 1 · The filed row does not exist

The dispatch said the defect was "filed on the ledger but never applied". It is not filed anywhere.
Searching `research/autonomy/research-ledger.json` over every `what` text, on the working tree **and**
on `origin/main`, returns exactly two rows containing the word *leverage* — `AUT-PD-076` (the queue
head is dominated by closed rows, via `prerequisite_of` inheritance) and `AUT-019` (a route's
`best_next_action` that happens to use the phrase "highest-leverage"). Neither is about this term.
Every other occurrence of the string `blocker_leverage` in that file — 77 of them — is the term's own
value inside a derived row's `score_inputs`.

The driver reached the same finding independently mid-seat and sent the correction. ⚠ **Both halves
of that are the finding to keep**: a recollection produced a defect report, and the only reason it
cost one seat rather than an edit to a governed scorer is that the seat contract makes step 1 *find
the row*. CLAUDE.md §7 — never write an identifier from recollection — has a sibling this is
evidence for: **never write a defect from recollection either.**

## 2 · What the term computes, and what it should

```python
def _blocker_leverage(routes: list[dict]) -> dict[str, int]:
    """How many OTHER routes share at least one blocker with this one."""
    by_blocker: dict[str, set[str]] = {}
    for route in routes:
        for blocker in route.get("blockers_inherited") or []:
            by_blocker.setdefault(blocker, set()).add(route["id"])
    leverage: dict[str, int] = {}
    for route in routes:
        peers: set[str] = set()
        for blocker in route.get("blockers_inherited") or []:
            peers |= by_blocker.get(blocker, set())
        peers.discard(route["id"])
        leverage[route["id"]] = len(peers)
    return leverage
```
`priority.py:296-309`. Applied at `:345` as `lever = min(leverage.get(route["id"], 0), cap)`, summed
at `:352` as `terms["blocker_leverage"]["weight"] * lever`, and echoed into `score_inputs`. The
consumer re-derives it identically: `admissibility.py:253-256` refuses a non-number and adds
`terms["blocker_leverage"]["weight"] * lever` to the reproduced total.

**Against the declared contract it is correct.** `priority-weights.json` says the term *reads*
"count of OTHER routes sharing at least one blocker with this route (capped by
`blocker_leverage_cap`)", and that is line-for-line what the code does: peers are a set (two shared
blockers do not double-count one peer), self is discarded, the count is capped, the cap is read from
the weights file and never typed. **No arithmetic defect. Nothing to fix here.**

## 3 · The cap is the whole term, and it was unmeasured

| | measured on the committed graph, 2026-09-02 |
|---|---|
| raw leverage across 77 routes | `0` (12 routes) … **48** (4 routes); 13 routes at 37, 11 at 40 |
| widest blocker | `BLK-NO-EMC-DATA`, inherited by **38 of 77** routes |
| capped distribution at `cap = 6` | `{0: 12, 2: 2, 4: 1, 6: 62}` |
| routes at the ceiling | **62 of 77 (80.5 %)** |

So the term is a near-binary flag worth `0` or `24.0`, not the graded count its rationale describes.
⛔ **`priority-weights.json`'s own `why` — "Per-route weight is small because the count does the
work" — describes the UNCAPPED term.** Under the cap the count does not do the work; the flag does.

**And the cap is load-bearing rather than cosmetic.** Re-running `build_ledger()` on a scratch copy
with the cap raised to 10⁶:

| variant | rows whose score changes | rows moving > 5 places | top 20 |
|---|---|---|---|
| **D · uncapped** | 76 | **295 of 361** | inverted |
| **B · weight 0 (term removed)** | 80 | 254 | wholly different |
| **C · live/takeable peers only** | **18** | 32 | **byte-identical** |

Uncapped, `AUT-053` goes **#268 → #30** (50.0 → 218.0) and `AUT-012` **#261 → #28**: the queue
inverts toward whichever route inherits the most widely-shared blocker, which is the opposite of a
priority. ⛔ **`grep -rn "blocker_leverage_cap" --include=*.py .` returned ONE hit** — `priority.py:318`,
the line that reads it — **and no test anywhere asserted anything about it.** That is the
`subagent_width` shape CLAUDE.md §1 records verbatim: a constant governing a real behaviour with
nothing measuring it, so compliance was luck.

## 4 · The obvious correction, measured and refused

The one defensible-sounding change is to count only peers that could actually move — the weights
file's own justification is *"retiring a widely-inherited blocker moves many routes at once"*, and a
dead peer will not move. The peer sets are genuinely padded: of the 38 routes carrying
`BLK-NO-EMC-DATA` only **15 are live** and 21 takeable; of the 14 carrying `BLK-NOT-FUSION-SELECTIVE`
only **1 is live** and 3 carry `work_state: dead`.

**Measured, that correction is inert where decisions are made and pointed the wrong way where it is
not.** Restricting peers to live *and* takeable routes changes the score of **18 of 361 rows**; every
one is a **demotion**; every one already sits at **#250–#316 of 361**; the **top 20 is byte-identical**
to baseline, as is every row above #250. And among the demoted is `AUT-019` (34.0 → 10.0, #304 → #316)
— a `blocked_without_evidence_becomes_a_check` re-test row, i.e. a row whose *entire content* is
retiring a blocker, which is the single row class this term exists to promote.

⛔ **A change that moves no decision and demotes the row class the term was written for is not a
correction.** It is refused, and the refusal is now pinned by a test rather than left to the next
session's judgement.

## 5 · What changed

| path | change | scores moved |
|---|---|---|
| `research/autonomy/tests/test_the_leverage_cap_is_load_bearing.py` | **new**, 6 tests, 0.08 s | none |
| `research/autonomy/priority-weights.json` | prose only: `reads` names the field and the unfiltered peer set; `why` retains its refuted sentence under rule 1.2 beside the measurement; **new `_blocker_leverage_cap_why`** giving the bare integer the rationale every other saturating constant in the file already carries | **none** |
| `research/autonomy/amendments.jsonl` | two declarations (both paths are `amendment_guard.GOVERNED`) | — |

**Proven, not asserted:** `build_ledger()` run twice on a scratch copy — once with the edited weights
file, once with `HEAD`'s — returns byte-identical `(id, score)` sequences for **all 361 rows**, and
all **29** numeric/boolean values in the file are unchanged. `amendment_guard.py --check-log`:
`250 record(s), OK`.

## 6 · Mutation table

Every mutation applied to a **copy** of `priority.py` under the seat scratchpad; the live file was
never edited-and-restored (CLAUDE.md §6, the 13 inverted claims).

| # | mutation | result |
|---|---|---|
| — | baseline, unmutated | 6 passed |
| M1 | `min(…, cap)` → `leverage.get(…)` (cap dropped) | **CAUGHT** |
| M2 | `cap = weights[...]` → `cap = 10**6` (read, then neutered) | **CAUGHT** |
| M3 | peer set restricted to live/takeable routes | **CAUGHT** |
| M4 | `peers.discard(route["id"])` removed (self counted) | **CAUGHT** |
| M5 | `len(peers)` → `len(blockers_inherited)` (counts blockers, not peers) | **CAUGHT** |
| M6 | the term dropped from the weighted sum | **CAUGHT** |
| M7 | `min` → `max` | **CAUGHT** |
| M8 | `cap + 1` (off-by-one) | **CAUGHT** |
| — | restored, unmutated | 6 passed |

**8 mutations, 8 caught, 0 survivors.**

⚠ **THE FIRST MUTATION RUN WAS INVALID AND IS REPORTED RATHER THAN DROPPED.** Its restore step left
the unmutated file failing its own test — `cap=1 should clamp RT-B7H3 to 1, got 48`, which is M7's
`max(48, 1)` answer produced by a file `diff` said was identical to the original. The cause is not a
guess: `min` and `max` are the same byte length, so the restored file matched M7's `.pyc` on
**both** halves of CPython's mtime-and-size invalidation and the stale bytecode was served. Re-run
with `python3 -B` and a purged `__pycache__`, every result above is from a fresh compile.
★ **A mutation harness that rewrites one file in a tight loop must disable bytecode caching**, or a
same-length mutation can silently contaminate the run after it — including reporting a mutation
"caught" by the *previous* mutation's code.

## 7 · Self-serving check

⛔ **Neither edit moves a single score**, proven by the 361-row comparison in §5. No row is promoted,
none demoted, and in particular no row this sprint filed (`AUT-082/085/088/089/090/092/093/094-e71cf460*`)
moves by one place. **The other half of the rule:** no bar blocked this seat — it took no ledger item,
its subject was assigned, and its work was gated by no score. (The 61-row lease the driver briefly
opened under this seat's name came from the same bad search and was reverted; none of those rows is
this seat's.)

★ **And the self-serving edit here was the one refused.** A seat dispatched to fix a scorer has an
obvious incentive to find something to fix; the change available was §4's, and it would have been
defensible-sounding, inert, and wrong in the direction that matters. **Reporting "no defect" is the
result.**

## 8 · For the driver

- **No ledger row to close.** There is no `_blocker_leverage` row. **File one row** if this is worth
  a record: *`blocker_leverage_cap` was read by one line and asserted by no test; now pinned by
  `test_the_leverage_cap_is_load_bearing.py` (8/8 mutations caught). No scorer arithmetic changed.*
  `kind: process_defect`, `state: done`, `serves.route: RT-AUTONOMY`, `cost_class: free`.
- **Not mine, seen while running the suite, reported rather than touched:**
  `systems/tests/test_autonomy_priority.py::test_no_dollar_figure_is_ever_written_into_the_ledger`
  is **RED on the working tree** — the ledger now carries `$10.35 $12.33 $22.68 $73.79`, restated
  prices inside `what` text (the GPU-lane rows, around ledger lines 11238–11262). **None of the four
  is present at `HEAD`**, so this arrived with this sprint's ledger writes and it will red the commit.
  CLAUDE.md §1: point at the rung via `cost_points_at`, never restate the figure.
- **Also not mine:** `research/autonomy/tests`' `conftest` tracked-tree guard fired mid-run on
  `research/autonomy/ledger_schema.py` — another seat (S51, `reference_problems()`) was writing that
  file while the suite ran. Left untouched; it is that seat's evidence, not a test leak.
