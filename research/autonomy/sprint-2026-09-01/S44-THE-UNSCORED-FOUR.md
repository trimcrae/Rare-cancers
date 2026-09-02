---
id: DOC-SPRINT-S44-THE-UNSCORED-FOUR
title: "S44-THE-UNSCORED-FOUR — a hand-typed `score: 0.0` is the one value the ranker can never improve, and it is now the sprint's default filing"
level: L3
kind: memo
status: live
date: 2026-09-02
audience: [autonomous research agents, maintainers]
purpose: >
  Root-cause why rows filed by this sprint's seats come out of priority.py at 0.0, decide between
  "the scorer is broken" and "the filer is sloppy", and settle what the 176 RT-AUTONOMY rows are
  actually scored on. Proposes an unapplied fix; edits no governed file and no ledger row.
scope: >
  research/autonomy/{priority.py, admissibility.py, priority-weights.json, continuity.py,
  research-ledger.json} at HEAD b4cf28c6be8f464fc25e0cee06f6be50eb181138. Every score below is
  reproduced by running the real priority.py against a COPY of the ledger; nothing in the live tree
  was mutated.
last_verified: 2026-09-02
---

# S44 — the unscored four are seven, and none of them is unscored

**Item:** the four `score: 0.0` / no-`score_inputs` rows named in this seat's dispatch.
**Owned paths:** this file, and scratch under the session scratchpad. Nothing else was written.
**Baseline:** `git rev-parse HEAD` = `b4cf28c6be8f464fc25e0cee06f6be50eb181138`. `priority.py`,
`admissibility.py` and `priority-weights.json` are byte-identical to HEAD (`git diff --stat HEAD --`
empty for all three), so the mechanism below is the committed one.
⚠ **`research-ledger.json` is NOT** — the driver is writing it (`+109/-16` against HEAD). Row counts
are given for both trees and labelled.

## ⭐ THE ANSWER, FIRST

**`0.0` was typed by the filer, and typing any number is what permanently forecloses the one pass that
could have computed a real one.** `apply_route_inheritance` — the pass added by AUT-PD-143 precisely to
give a hand-filed row a defensible score — reads

    research/autonomy/priority.py:1068    if entry.get("score") is not None:
    research/autonomy/priority.py:1069        continue

so it touches a row **only while that row's score is `None`**. A row filed `0.0` is scored, so the pass
skips it on this run and on every future run, for ever. Nothing else in the file can create a base score
for a hand-filed row: the eight graph terms are computed in one place only,
`build_entries` (`priority.py:368-375`), and `build_entries` derives rows **from `systems/graph`**, never
from a filed row.

⛔ **THE CORRECTION TO THE DISPATCH, AND IT MATTERS BECAUSE THIS REPOSITORY HAS PAID FOR THE DISTINCTION.**
The four rows do not carry `"score_inputs": null`. They carry **no `score_inputs` key at all** —
`'score_inputs' in row` is `False` at HEAD and after `--write`. `priority.py:465-490` treats explicit-null
and absent as different things on purpose (AUT-PD-152 was an explicit null; this is not that bug).
`score_inputs` is absent because the only pass that would have written one, `apply_age_factor`, hit its
own `if not f and not prev: continue` (`priority.py:808`) — these rows were filed **today**, so
`age_factor` returns `0.0` at `priority.py:642` (`if days <= 0`).

★ **So there is no branch anywhere that "skips" these rows. Every pass ran on them and each correctly did
nothing.** The number is the filer's.

## ⛔ THE POPULATION IS SEVEN AND GROWING, AND THREE OF THEM DO NAME A REAL ROUTE

Open rows scoring exactly `0.0`, working tree, `state ∉ {done, abandoned, superseded, dropped, closed,
parked}`:

| id | filed_by | `serves.route` | `_score_basis`? | route in `systems/graph/routes.json`? |
|---|---|---|---|---|
| `AUT-082-e71cf460` | S39-ATLAS-ADJUDICATION | `null` | yes | — |
| `AUT-083-e71cf460` | S39-ATLAS-ADJUDICATION | `null` | yes | — |
| `AUT-084-e71cf460` | S40-COVERAGE-INFLATION | `null` | yes | — |
| `AUT-085-e71cf460` | DRIVER-SUBAGENT-DISCRIMINATOR | `null` | **NO** | — |
| `AUT-086-e71cf460` | S41-BLOCKED-ROUTE-AUDIT | `RT-PARTNER-STRAT` | **NO** | **yes** |
| `AUT-087-e71cf460` | S41-BLOCKED-ROUTE-AUDIT | `RT-CARFILZOMIB` | **NO** | **yes** |
| `AUT-088-e71cf460` | S41-BLOCKED-ROUTE-AUDIT | `RT-ENDPOINT-CHOICE` | **NO** | **yes** |

**At HEAD the same query returns three** (`AUT-082/083/084`); the working tree has seven. **Every row this
sprint has filed is in this table** — the population is 100 % of the sprint's filings and it grew by four
in the hours between HEAD and this read.

⛔ **The last three kill the `serves.route: null` reading outright, on live data, with no mutation
needed.** They name routes the graph really contains, and they still score `0.0`. Four of the seven also
carry **no `_score_basis`**, which the ledger's own `_role` states is mandatory: *"AN ENTRY A SESSION ADDS
MUST CARRY A `score` AND A `_score_basis`"*.

## ★ THE CONTROLLED EXPERIMENT

Run on a copy of the repository (`research/`, `systems/`, `scripts/`), with the real
`priority.py --write`; the ledger was re-copied from the live tree before every arm, so each arm changes
exactly one thing against the same baseline. ⛔ No `git worktree`, no write to the live tree.

| arm | one thing changed | score after `--write` |
|---|---|---|
| A0 | nothing (baseline) | `AUT-082` **0.0**, `AUT-PD-116` **131.6** |
| **B** | **id shape**: `AUT-PD-116` → `AUT-PD-116-e71cf460` | **131.6 — unchanged** |
| **C** | **age**: `AUT-082.last_evidence_utc` `2026-09-02` → `2026-08-28` | **0.0 → 4.3**, `score_inputs {age_factor: 0.3571, age_factor_as_of: 2026-09-02}` |
| **D** | **route**: `AUT-082.serves.route` `null` → `RT-MTAP-PRMT5`, score left `0.0` | **0.0 — unchanged** |
| E | `score` key removed, route `null` | `None` (unrankable residue) |
| **F** | **`score` key removed + route `RT-MTAP-PRMT5`** | **187.0**, `_score_inherited_from_route: RT-MTAP-PRMT5` |
| G | `score: null` + route `RT-MTAP-PRMT5` | 187.0 (identical to F — absent and null agree here) |
| H | `kind` `fetch` → `proposal` | 0.0 — unchanged |
| **I** | **the three routed rows filed with `score: None` instead of `0.0`** | `AUT-086` **109.3**, `AUT-087` **50.0**, `AUT-088` **47.0** |

**B and D are the discriminating pair.** B changes the id shape on a row that scores well and moves
nothing: **the discriminated id (`PREFIX-ORDINAL-DISCRIMINATOR`) is innocent** — `merge()` parses it
through `ids.parse_entry_id` (`priority.py:894-897`), the one-line fix its own comment describes as
already made. D gives a zero row a real route and moves nothing: **the null route is not the cause
either.** The only thing that moves the number is removing the typed score (E→F→I).

**I is the cost, in points, on live rows:** `109.3 / 50.0 / 47.0` were available to S41's three rows and
were thrown away by typing `0.0`. Those are the routes' own floors, read by `route_score_floor` off the
graph's derived siblings (`priority.py:964`); reproduced independently:
`P.route_score_floor(E)` → `RT-PARTNER-STRAT 109.3`, `RT-CARFILZOMIB 50.0`, `RT-ENDPOINT-CHOICE 47.0`.

## ⛔ ARE NEWLY-FILED ROWS INVISIBLE TO THE RANKER? — NO BY CONSTRUCTION, YES IN PRACTICE

**No** as a property of newness: nothing keys on `filed_by`, on the id shape, on `kind` (arm H), on
`_derived`, or on the filing date beyond the age term, which is legitimately `0` on day one and worth
`12.0 × factor` thereafter (`priority-weights.json` `terms.age.weight = 12.0`, saturating at
`age_saturates_days.value = 14.0`).

**Yes** as an outcome, and it is measurable rather than rhetorical:

- Working tree, open rows: the seven sit at **ranks 156–162 of 165**. Only three open rows score lower
  (`AUT-079 -40.6`, `AUT-027 -79.1`, `AUT-PROP-026 -2591.4`), and all three are negative because a
  *penalty* was charged, i.e. the ranker judged them. `0.0` is not a judgement.
- `continuity.py --check` sorts the ready list by `priority.score_rank` (`continuity.py:201`). Four of
  the seven are ready, at **ready-ranks 123, 124, 125 and 126 of 126**. The printer's default is
  `--limit 10` (`continuity.py:402`), so **the driver's own "READY TO RUN" view never prints them**;
  reaching them needs `--limit 130`.
- **They are invisible to both instruments built to find unrankable rows.** `n_unscored` counts
  `score is None` (`priority.py:1547`) and `n_unscored_open` the same (`:1548`); `health.py`'s
  `scores_are_reachable` counts the same population. `n_unscored_open` reads **0** at HEAD and **0** in
  the working tree *while these seven rows exist*. A row nothing can rank is exactly what those counters
  exist to surface, and `0.0` is the one value that is unrankable and uncounted at the same time.

## ⛔⛔ THE MECHANISM BEHIND THE MECHANISM: TWO RULES SHIPPED THE SAME DAY THAT CONTRADICT EACH OTHER

- `apply_route_inheritance` — **AUT-PD-143**, `e0c100475`, **2026-08-29** — scores a hand-filed row
  **only if its `score` is `None`**.
- `refuse_population_growth` (R5) — **AUT-PD-145**, `ee17c39a2`, **2026-08-29** — refuses to admit an
  appended row **whose `score` is `None`**.

Measured directly, `A.refuse_inadmissible_write(before=<committed>, after=<committed + one row>)`:

| appended row | R5 |
|---|---|
| no `score`, route `null` | **`refused_unscored_new`** |
| no `score`, route `RT-PARTNER-STRAT` | **`refused_unscored_new`** |
| `score: 0.0`, route `null` | **admitted** |
| `score: 0.0`, route `RT-PARTNER-STRAT` | **admitted** |

★ **R5 refuses the exact shape AUT-PD-143 built the inheritance pass to rescue, and admits the one shape
the pass can never repair.** And the ratchet is now welded shut at the bottom:
`test_the_population_is_empty_and_stays_empty` asserts `n_unscored_open == 0` on the committed ledger and
says *"do NOT raise a ceiling to admit it"*. A seat with no defensible number has one admissible move —
type one — and `0.0` is what an honest filer types when they will not invent a figure. **Three of the four
routeless rows say so in their own `_score_basis`** (`AUT-082`: *"RANKS LOW HONESTLY, and the low score is
the reading"*). They were being careful. The rules rewarded care with a permanent zero.

⚠ **THE ONE PATH THAT ALREADY WORKS, AND IT IS WHY R5 IS NOT A WALL.** R5 reads its baseline off the file
on disk (`admissibility.py:624-637`) and runs *after* priority's passes. So a seat that edits the ledger
with the `score` key **absent** and then runs `priority.py --write` **before committing** gets the row
scored by inheritance first and admitted second — measured: appending a routed row with no `score` and
re-scoring exits `0` with the row at **109.3**, and `n_unscored_open` stays `0`. **The working filing
procedure exists today and needs no code change.**

## ★ WHICH READING THE EVIDENCE SUPPORTS — AND IT SPLITS ON THE ROUTE

Both readings in the dispatch are half right, and the split is derived from each row's own fields:

- **`AUT-086/087/088` — THE FILER.** A real route, a real floor, `109.3 / 50.0 / 47.0` on the table, and a
  typed `0.0` threw it away. No scorer change is warranted or would help: arm D proves the scorer declines
  to overwrite a filed number, which is the correct behaviour (`apply_route_inheritance`'s own docstring:
  *"ASSIGNED ONCE, NEVER RE-DERIVED"* — re-deriving is the AUT-PD-063 ratchet). **Recoverable at $0.**
- **`AUT-082/083/084/085` — NEITHER, AND THIS IS THE HONEST RESIDUE.** They serve no route, so no floor
  exists (arm E: score stays `None`), and the graph holds nothing to rank them by. Under today's rules
  there is **no admissible filing for a routeless row that has no defensible number**: `None` is refused
  by R5 and reddens `test_the_population_is_empty_and_stays_empty`; `0.0` is admitted and invisible.
  `0.0` is therefore correct-by-design in the narrow sense that nothing better can be derived — and wrong
  in that it is **recorded as a judgement instead of as an absence**, which is the failure CLAUDE.md §4
  names: *"a row reading UNKNOWN... is an unanswered question wearing the costume of a status"*, inverted
  into a status wearing the costume of an answer.

⛔ **"The scorer is broken" is refused.** Every branch behaved as written and each is defended in its own
docstring by a measured incident. The defect is at the **boundary** — a filing contract written before the
inheritance pass existed, never updated when it landed.

## ⛔ RT-AUTONOMY: 176 ROWS, AND THE ROUTE HALF OF THEIR SCORE IS VESTIGIAL

Read at HEAD, not recalled: `systems/graph/routes.json` holds **77** routes. Ledger `serves.route` values
absent from it: **`RT-AUTONOMY` 176 rows, `RT-LOOP` 1, `RT-DEGRADER-TERNARY` 1** — 178 of 349, over half.

Of the 176: **0 are `_derived`**, 155 carry a number, 21 carry none (all closed — the open population is
0). Under `admissibility.verdict`, **all 155 grade `unaccounted`** — *"a hand-filed number nothing can
re-derive"* — and **0 grade `admitted`**. Whole ledger for contrast: `admitted 77` (exactly the derived
rows), `unaccounted 251`, `unscored 23`, `refused_stale_input 1`.

**What those 176 are actually scored on:** a number a session TYPED, plus whatever the delta passes have
since added. Their `score_inputs` contents, counted:

| `score_inputs` keys | rows |
|---|---|
| absent / not a dict | 58 |
| `age_factor`, `age_factor_as_of` | 77 |
| `fruitless_attempts` only | 10 |
| `age_factor`, `age_factor_as_of`, `fruitless_attempts` | 9 |
| `age_factor` only | 8 |
| `age_factor`, `fruitless_attempts` | 6 |
| `{}` | 4 |
| other flag combinations | 4 |

Every key present is a **delta or a flag** — age, fruitless attempts, blocked-on-human,
blocked-with-evidence. **Not one of the eight graph terms** (`DERIVED_TERMS` =
`live, patient_path_scaled, pursue_now, tier_one, endpoint_reachable, blocker_leverage, cost_class,
blocked_on_human`) appears in complete form on any of the 176: `_has_full_block` is false for every one of
them, which is why all 155 scored rows grade `unaccounted` rather than `admitted`. The closest is a
single row carrying `live`, `cost_class` and `blocked_on_human` beside its flags — a partial echo, still
not a derivation.

★ **PLAINLY: the route half is vestigial, not real.** `serves.route` on a hand-filed row is read in
exactly three places — `merge()`'s `by_route` id-donation map, which is filtered to `_derived` rows
(`priority.py:879-880`); `route_score_floor`, which is filtered to `_derived` rows (`priority.py:983-985`);
and `_table` / `--explain`, which display it. RT-AUTONOMY has **no derived row**, so it can never acquire
a floor and `apply_route_inheritance` can never fire on any of its 176 rows. **The string contributes zero
points.** It is a grouping label. `route_score_floor`'s own docstring already says so
(*"RT-AUTONOMY is not a route in systems/graph, so its rows can never inherit"*), and S21-UNSCORED called
it "cause 1" for 59 of the 68 rows it settled — **by typing scores**, which is how `n_unscored_open`
reached 0 and how the `0.0` habit was normalised.
⛔ **Inventing the route is still refused** and this memo adds nothing to `routes.json`. What the number
would mean if it were added is untested and stays **UNMEASURED**.

## ★ THE RECOMMENDED FIX — THREE PARTS, NONE APPLIED HERE

**1. `research/autonomy/research-ledger.json` — the driver, now, $0, no code change.** Delete the typed
`"score": 0.0` from `AUT-086/087/088` and re-run `python3 research/autonomy/priority.py --write` in the
same edit. Measured outcome: **109.3 / 50.0 / 47.0**, each with `_score_inherited_from_route` and a
generated `_score_basis`; `n_unscored_open` stays `0`; the write is admitted. Also add the missing
`_score_basis` to `AUT-085`, which the ledger's `_role` requires and which no gate currently checks.
⚠ **This is a ledger write and therefore the driver's, not a seat's.**

**2. `research/autonomy/priority.py` — the filing contract, as a docstring/`_role` amendment (governed;
propose, do not apply).** The ledger's `_role` still reads *"MUST CARRY A `score`"*, which is the sentence
that produced all seven rows. It should read: **a filed row naming a route the graph contains SHOULD OMIT
`score` and be re-scored by `priority.py --write` before commit — the ranker will derive the route floor;
type a number only when no route applies, and never type `0.0`.** This is prose, it changes no arithmetic,
and it is the whole of parts 1 and 3's prevention.

**3. `research/autonomy/admissibility.py` — R5's fourth door (governed; propose, do not apply, needs an
amendment record and mutation tests).** `refuse_population_growth` closes three doors into the unrankable
population and misses the one that is now being used every time. Proposed clause, refusing on **append
only**, so nothing committed is disturbed:

> an appended OPEN row whose `score` is exactly `0.0`, whose `score_inputs` carries no derived block, and
> which carries no `_score_inherited_from_route`, is refused: `0.0` ranks below every row the ranker has
> ever judged and is counted by neither `n_unscored_open` nor `scores_are_reachable`. **Remedy:** omit the
> `score` key and re-run `priority.py --write` — if the row names a graph route it will be scored from
> that route's floor; if it names none, say in `_score_basis` why no route applies and type a number that
> is not zero.

⛔ **What this clause must NOT become:** a rule against the value `0.0` as such. A derived row is free to
compute to zero; the refusal is scoped to an **appended, open, hand-filed** row with **no derivation
behind it**, which is the shape measured here. ⚠ And it does not fix `AUT-082/083/084/085` — a routeless
row with no defensible number still has no good filing, and that residue is named rather than papered
over.

**Rejected alternative — teach `apply_route_inheritance` to overwrite a `0.0`.** It is the smaller diff
and it is wrong. The pass's `score is not None` guard is load-bearing: overwriting a filed number
re-derives a base that the flag-guarded penalty passes have already charged against, which is the
AUT-PD-063 double-application ratchet the guard exists to prevent, and it would silently overrule a filer
who typed `0.0` **deliberately**. ⚠ Special-casing "zero means unset" makes the ledger's most common
number ambiguous — the precise ambiguity `score_rank` (`priority.py:547-566`) was written to end, after
`continuity.ready` had sorted an absent score *as if it were zero* and the two files disagreed about the
queue.

**Also rejected — add `RT-AUTONOMY` to `systems/graph/routes.json`.** It would resolve 176 numbers by
inventing the thing they point at.

## UNMEASURED

- Whether the seven rows' `what` text is worth more than rank 156 — **not assessed**; this seat measured
  the arithmetic, not the work. Part 1's recovery raises three of them on the route's evidence, not on any
  judgement made here.
- Whether R5's proposed fourth door would refuse any historical write. **Untested against history** —
  it is scoped to appends, but the mutation tests the governed path requires are not written here.
- Whether a `serves.publication` floor (the analogue of `route_score_floor` for `AUT-082`, which serves
  `PUB-BIOMARKER-DEP` and no route) is derivable. **Not attempted.** It is the only idea found that would
  give the four routeless rows a real number, and it is a design change, not a fix.
- `RT-LOOP` (1 row, scored) and `RT-DEGRADER-TERNARY` (1 row, scored) are the same vestigial shape as
  RT-AUTONOMY and were **not** individually adjudicated.

## Reproduction

Scratch tree and probes (a full copy of `research/`, `systems/`, `scripts/`; the live tree was never
mutated):
`…/scratchpad/sprint/scoreprobe/{probe.py,probe2.py}` — arms A0–I and the R5 append matrix.
Each arm re-copies `research/autonomy/research-ledger.json` from the live tree, changes one field, runs
`python3 research/autonomy/priority.py --write` inside the copy, and reads the row back.
