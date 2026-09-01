---
id: DOC-SPRINT-S21-UNSCORED
title: "S21-UNSCORED — the 68 open ledger rows no cycle can be offered: census, cause, and settlement"
level: L3
kind: memo
status: live
date: 2026-09-01
audience: [autonomous research agents, maintainers]
purpose: "The findings record of sprint seat S21-UNSCORED — what it measured, what it changed, and what it could not do. Written before the seat returned, so a seat that dies costs its own work and nothing else."
scope: "One seat of the 2026-09-01 sprint, bounded by the owned-paths list in its own prompt. It reports; it does not decide what lands."
last_verified: 2026-09-01
---

# S21-UNSCORED — what the queue has been blind to for 88 hours

**Item(s):** `scores_are_reachable` / UNRANKABLE-WORK (health.py), AUT-PD-143's residue
**Owned paths:** `research/autonomy/sprint-2026-09-01/S21-UNSCORED.md`, `research/autonomy/sprint-2026-09-01/S21-UNSCORED-proposals.json`
**Census read:** `git rev-parse HEAD` = `062a48ae1c42bc71ec790d13d0565cc86be618ce` (one read; every count below is from it)
**Started/Finished (UTC):** 2026-09-01T19:2xZ / 2026-09-01T20:xxZ

## Verdict

**PARTIAL** — the 68 are enumerated and settled in a proposals file that simulates clean through the
admission gate and takes `scores_are_reachable` to **ALL-RANKABLE**; but the finding that matters is
that **the hidden population is not bookkeeping — thirteen of the 68 are portfolio work on live
treatment routes, and one of them is finished work sitting on four unmerged branches, verified still
unmerged tonight.**

---

## ⭐ THE FINDING, FIRST: what was actually in there

**It is not 68 rows of process bookkeeping.** By kind it looks like it is — 55 of 68 are
`process_defect` and 59 of 68 serve `RT-AUTONOMY` — and that appearance is exactly why nobody looked.
Reading the `what` field of all 68 gives a different answer.

### The live work, named individually (CLAUDE.md §0: this outranks every item below it)

**⛔ AUT-PD-151 — four seats' finished work is on branches nothing will merge, and I confirmed it is
STILL TRUE tonight.** This is the one row in the 68 where the harm is ongoing rather than latent.
Verified at HEAD, not inherited from the row's text — `git merge-base --is-ancestor <sha> origin/main`
returns false for all four:

| branch | sha | carries |
|---|---|---|
| `seat/s1-aut-pd-130` | `e0847032` | claim_coverage.py, a new pairing test, preflight.sh, tests.yml, the ASO archive manifest |
| `seat/s3-unscreened-endpoints` | `88ac1c7c` | lint_style.TARGETS vs systems/graph/publications.json, plus a new test — **and no row of its own on the trunk** |
| `seat/s4-aut-045` | `c8944f76` | **systems/graph/routes.json** and two generated views |
| `seat/s5-retest-blocks` | `da4247dc` | IC-3 and IC-12 prechecks, two new `research/modalities/` artifacts |

Their driver session was archived mid-landing-loop on 2026-08-28. CLAUDE.md §7 calls branch drift a
data-loss bug and says never to let a branch be the only home of an artifact. **Four days on, four
branches are exactly that, and the row saying so has been invisible to the queue the whole time.**
⚠ AUT-PD-151's own text also warns that merging `seat/s3` naively destroys a live row (an
`AUT-PD-141` closure that disagrees with the trunk) — so this is a driver merge, not a seat's.

**⛔ AUT-PD-116 — sixteen live treatment routes are blocked on a block a committed artifact already
answers.** Sixteen routes carry a `required_validation` marked `feasible_today: false` on
`BLK-NO-EMC-DATA` whose own text names an expression or tissue read, and not one cites
`ART-EMC-EXPRESSION-PANELS`. **Six name a gene that artifact already reads on EMC tumour tissue** —
RT-SSTR2 (SSTR2), RT-B7H3 (CD276), RT-FAP-RLT (FAP), RT-JUNCTION-NEOANTIGEN (HLA-A/B/C, TAF15),
RT-FUSION-OUTPUT (EWSR1, NR4A3, PPARG, SEMA3C, TAF15), RT-MTAP-PRMT5 (MAT2A, MTAP, PRMT5). This is
CLAUDE.md §0's *"blocked is a claim that needs evidence, and it is usually wrong"* applied to a fifth
of the portfolio at $0 — and the row records a precedent where the block was false **in the dangerous
direction**: RT-PRAME-IMMTAC was graded a lead on a cell-line surrogate while the EMC-tissue read its
own validation asked for had been committed four days earlier and sat at the floor of every readable
cohort.

The other eleven portfolio rows, each of which can change a route's grade, a route's status, or a
number in a published artifact:

- **AUT-PD-113** — `BLK-NO-EMC-DATA`'s `retired_by_action` is imprecise and **38 of 77 routes inherit
  it**. It says no EMC ex-vivo drug-response panel exists; EV-BANGERTER-2023 is one, committed and
  cited here.
- **AUT-PD-104** — audit every route for a status or `readiness.missing` claim a committed artifact
  refutes. Third instance in one day, and one had already **propagated out of the graph into a
  manuscript** (the neoantigen class-II figure, overstated ~4×).
- **AUT-PD-088** — three routes recorded `closed` still carry a reopening trigger (RT-SYNPROMOTER,
  RT-RXR carry `TECH-*`; RT-6MP a `TR-*`). By `systems/CONVENTIONS.md` §4.1's own words those are
  `parked`. On a rising frontier (CLAUDE.md §5) that is how a live option is lost quietly.
- **AUT-PD-098** — sweep every route grade for the defect AUT-062 found by reading ONE route: a
  transcript-abundance number described as reporting protein ACTIVITY. Claim SCOPE — invisible to
  every gate, because the sentence is grammatical, hedged, and cites a real artifact.
- **AUT-PD-111** — add a standing CLASS-LEVEL literature query beside the EMC-scoped prior-art
  screen. The scope gap it names hid a 2005 phase II trial for twenty-one years (AUT-013), and it is
  structural: a screen scoped to EMC pairings cannot return a paper mentioning neither term.
- **AUT-PD-087** — three routes recorded `ready`/`pursue_now` whose next action is a CONCLUSION.
  RT-CARFILZOMIB is still the top-scoring ready row at 172.0.
- **AUT-PD-095** — nine more not-takeable routes carrying an unmarked `feasible_today: true`
  validation. Its own triage is a text scan and says so; the previous batch was 2-of-4 mis-parked.
- **AUT-PD-103** — `TR-*` revival triggers exist only in the legacy `emc-systems-map.json`;
  `systems/graph` has no `TR-*` record and nothing validates the reference. A route's reopening
  condition the source of truth cannot see.
- **AUT-PD-083 / AUT-PD-084** — two defects **inside the released Zenodo deposit for PUB-ASO**: a
  control-oligo artifact that contradicts itself about whether its controls pass the specificity
  screen, and one number attributed to two different PMIDs. `lint_citations` cannot see the second by
  construction — both identifiers resolve; the defect is that two works are credited for one fact.
- **AUT-PROP-047** — run `claim_audit.py` on the degrader paper. Free, deterministic under a seed,
  already committed; it turns the ASO draw's 3-refutation shape into a pattern or refutes it.

**AUT-COV-001** belongs in the same conversation even though I scored it as machinery: 22 of 32
publication endpoints are read by no instrument at all, and a hardening round measurably *enlarges*
the uncovered surface (nine defects fixed, covered 46/259 → 50/271, uncovered 213 → **221**).

### What the rest is

The remaining ~51 rows are genuinely the loop's own machinery, and a large fraction of them are
instruments that are **lying rather than silent** — `session_cap.verdict()` inverted on the success
case, `continuity.py --check` with a green state unreachable by correct behaviour, a reaper whose
join can never match, `PREFLIGHT_MODALITIES=1` printing OK after running zero tests, `claim.py`
turning a one-row lease into an ungated push. Those matter, but §0 puts them behind the thirteen
above, and the tiering in the proposals file encodes exactly that.

### Two duplicate pairs, filed independently by different cycles

- **AUT-PD-115 and AUT-PD-153** are the same defect (`session_cap.blocked_handoff` returns `None`
  for both "handed off" and "never tried"; `verdict()` reads it as the latter).
- **AUT-PD-097 and AUT-PD-122** are the same defect (`ids.next_entry_id` has no session
  discriminator while `next_receipt` does).

Both are scored so they stay visible, and both are flagged for merge rather than silently dropped.

---

## What I measured

### The census, and it is one read

```
$ git rev-parse HEAD                            062a48ae1c42bc71ec790d13d0565cc86be618ce
$ TZ=America/New_York date '+%-I:%M %p ET'      3:29 PM ET
```

344 entries · 194 open · **68 open with `score: None`** — matching the ledger's own
`n_unscored_open: 68` and health.py's reading exactly. All 68 are `state: queued`. By route: 59
`RT-AUTONOMY`, 9 `null`. By kind: 55 `process_defect`, 6 `proposal`, 3 `process`, 2 `fetch`,
1 `regrade`, 1 `analysis`. Seven carry a `_score_basis` with no `score` beside it.

### Why they have no score — three causes, not two

The health message names two remedies, which implies two causes. There are **three**, and the third
is not an unscorable row at all. The split is derived from each row's own fields, not typed:
**56 / 9 / 3**.

**Cause 1 — `serves.route: RT-AUTONOMY`, which has no floor to inherit (56 rows).** `RT-AUTONOMY`
appears in **none** of the 77 routes in `systems/graph/routes.json`, so no derived row serves it —
**0 of the 176 ledger rows on that route are `_derived`** — and `priority.route_score_floor` produces
no entry for it, so `apply_route_inheritance` hits its `if floor is None: continue` and leaves the
row alone. That is deliberate, and `route_score_floor`'s own docstring says so: it is "the measured
reason this pass cannot flood the queue with the loop's own process defects."
⚠ 59 of the 68 name `RT-AUTONOMY`; three of those are counted under cause 3 below, which takes
precedence because their fix is a `state` change rather than a score.

**Cause 2 — `serves.route` is `null` (9 rows).** `AUT-COV-001`, `AUT-COV-002`, `AUT-PD-011`,
`AUT-PD-012`, `AUT-PD-039`, `AUT-PD-116`, `AUT-PD-161`, `AUT-PD-162`, `AUT-PROP-001`. These never
reach the floor lookup at all — `apply_route_inheritance` skips at `if not route`. Cause 2 is
strictly worse than cause 1: giving `RT-AUTONOMY` a graph row would not rescue them.

**Cause 3 — the row is FINISHED and was never closed out of `queued` (3 rows).** `AUT-PD-090`,
`AUT-PD-091`, `AUT-PD-118`. These are not unscorable; they should not be open. Two say in their own
text "✅ FIXED in the same merge (`e9793302e`) … filed as a CLOSED row", and `e9793302e` is an
ancestor of HEAD; the third says "⛔⛔ ANSWERED 2026-08-28 … THE PREMISE IS FALSE", and both receipts
it turns on are committed. **Inventing a score for these would be the worst outcome available** — it
puts finished work back into the ranking, which is the defect `AUT-PD-076` (also in this 68) is
separately filed about. They take a `state` change and no number.

### ⛔ And a fourth finding, about the ratchet rather than about any row

**THREE ROWS ENTERED THE POPULATION AFTER R5 WAS ALREADY LIVE, AND R5 REFUSES THEM
TODAY.** `admissibility.refuse_population_growth` (R5) landed on the trunk in `ee17c39a2` at
2026-08-29 00:49 and is supposed to make this population unable to grow. Replaying it against the
actual commits that filed each row — `before` = that commit's parent, `after` = that commit — gives
the observation that discriminates:

| row | filing commit | R5 an ancestor? | R5 replayed on that write |
|---|---|---|---|
| `AUT-PD-154` | `eab55e405` (08-29 00:51) | **no** — predates the merge | 0 refusals (correct) |
| `AUT-PD-155` | `bc4899efc` (08-29 01:59) | **yes** | **`refused_unscored_new` on AUT-PD-155** |
| `AUT-PD-161`, `AUT-PD-162` | `df529936a` (08-29 03:29) | **yes** | **`refused_unscored_new` on both** |

**Three rows landed through a write path the gate does not sit on.** R5 lives in
`admissibility.check_write`, which only runs inside `ledger_io.write_ledger`; a text edit of
`research-ledger.json` bypasses it entirely, and nothing re-runs the gate over the committed file.
The ratchet is real but it is a *write-path* ratchet, not a *repository* invariant.

### The ratchet has been holding since — the population is flat, not growing

Traced across 60 commits of `research-ledger.json` with `git show`: `n_unscored_open` has read
**68** at every commit since 2026-08-31 (and 68–69 since 2026-08-29 15:56) while the ledger grew
from 322 to 344 entries. **+22 rows, 0 net new unscored.** So this is a closed, finite, non-growing
set, and clearing it once clears it — which is what makes it worth doing tonight rather than
managing.

### What a score can honestly be here — and the option I refused

`priority-weights.json`'s eight derived terms split cleanly:

- **Readable from the row itself:** `cost_class` (all 68 are `free`), `blocked_on_human` (none carry
  `requires_trimcrae`), `blocked_with_evidence` (none carry `blocked_evidence`), `age_factor` (all 68
  carry one, with a matching `age_factor_as_of: 2026-09-01`), `fruitless_attempts`.
- **Route properties with no source:** `live`, `patient_path_scaled`, `pursue_now`, `tier_one`,
  `endpoint_reachable`. `RT-AUTONOMY` has no route record, so the graph says *nothing* about these.

**⛔ I did not write the full eight-term block, and that refusal is the main technical decision in
this seat.** Filling those five with `false` / `0.0` would produce a number R2 reproduces exactly and
`admissibility.verdict` grades `admitted` — a score that *looks computed* while asserting the graph
had said this row is not live, when the graph had said nothing. `apply_route_inheritance`'s own
docstring forbids precisely this ("⛔ IT NEVER FABRICATES `score_inputs`. A full set of zeroed inputs
would make an inherited score look computed"), and
`test_priority_ranks_the_hand_filed_entries_too` binds it. **An `admitted` grade bought that way is
worse than the `unaccounted` grade an honest typed number gets.**

So every proposal is what the repository already does 179 times: **an explicit `score` with a prose
`_score_basis`, graded `unaccounted` — reported as UNMEASURED, not as a pass.** That is the filing
contract in `research-ledger.json`'s `_role`, it is what R5's own refusal message prescribes, and it
is the form `AUT-PD-195` and `AUT-PD-196` already carry verbatim ("EXPLICIT, AND TYPED ONLY BECAUSE
IT CANNOT BE DERIVED").

### The band, and why nothing here can outrank live research

Read off the committed ledger at `062a48ae`: the **30 open scored `RT-AUTONOMY` rows span 43.6
(AUT-PD-043) to 135.8 (AUT-PD-031)**, with deciles 43.6 / 71.7 / 99.6 / 107.2 / 115.6 / 119.7 /
121.6 / 124.7 / 126.7 / 130.7. The live-research head of the queue sits at **184–201**
(RT-ASO, RT-PARTNER-STRAT hardening rows). My proposals span **66.0–135.0**, under the committed
ceiling — so **no row I score can outrank live route work**, which is the §0 property this whole
exercise has to preserve.

Three tiers, applied to the reading above:

| tier | band | rule | n |
|---|---|---|---|
| **L** | 120–135 | acts on the treatment portfolio: a route grade, a route block, a route status, a published deposit, a manuscript number, or finished route work at risk | 13 |
| **M** | 95–119 | loop machinery measurably costing the loop work right now — a broken instrument, a bypassed gate, a wrong capacity reading | 32 |
| **S** | 64–94 | latent, cosmetic, or a proposal awaiting a build decision | 20 |
| **C** | — | not scored: the work is finished and the row was never closed | 3 |

### The scores are fixed points — checked, not assumed

A typed score on these rows must be the **final** number, because `apply_age_factor`,
`apply_fruitless_attempts` and `apply_requires_trimcrae` all apply a **delta against the value
echoed in `score_inputs`**, and all 68 already carry their echoes. Verified over all 68 at HEAD: no
row carries `blocked_evidence`; none carries `requires_trimcrae`; the only two rows with a fruitless
term (`AUT-COV-001` n=0, `AUT-PD-150` n=1) already have `n == prev`. **So the next
`priority.py --write` moves none of these numbers.**

### The simulated write

Applied the proposals to an in-memory copy of the ledger (nothing written to
`research-ledger.json` — it is driver-only) and ran the real gate:

```
findings from admissibility.refuse_inadmissible_write(before, after, weights):  0
verdicts after:   admitted 77 · unaccounted 244 · unscored 23   (the 23 are CLOSED rows)
scores_are_reachable AFTER:  open=191  unrankable=0  ->  GREEN / ALL-RANKABLE
```

And against the coupled test, run with `LEDGER` pointed at the simulated file:

```
test_the_ratchet_is_not_vacuous:  RED -> "no open unscored rows at all — delete
                                          MAX_UNSCORED_OPEN and assert `not ids`"
```

That red is the test **telling the driver what to do at zero**, not a failure of the proposals. The
whole module is green at HEAD today (`12 passed in 0.18s`).

---

## What I changed

- `research/autonomy/sprint-2026-09-01/S21-UNSCORED.md` — this file.
- `research/autonomy/sprint-2026-09-01/S21-UNSCORED-proposals.json` — 68 objects, valid JSON,
  generated from a single table so the ids and numbers here and there cannot drift.

**Nothing else.** I did not touch `research-ledger.json`, `systems/graph`, `priority.py`,
`admissibility.py` or any test, and I ran no git write command.

---

## ⛔ What the driver must do IN THE SAME COMMIT

1. **Tier C rows take `state: done` and NO score** (`AUT-PD-090`, `AUT-PD-091`, `AUT-PD-118`).
   Their own text says the work is finished and I verified it: `e9793302e` is an ancestor of HEAD,
   and `CYC-0062-757d4e91.json` / `CYC-0063-757d4e91.json` are both committed under
   `research/autonomy/receipts/`. Inventing a number for a finished row is the failure mode
   `AUT-PD-076` is separately filed about.
2. **Every other row takes `score` and `_score_basis` and nothing else.** Leave `score_inputs`
   exactly as committed — see the refusal above.
3. **Fix `test_an_unscored_row_is_ranked_by_nothing.py`.** `MAX_UNSCORED_OPEN` is `69`;
   `test_the_open_unscored_population_does_not_grow` will pass at 0, and
   `test_the_ratchet_is_not_vacuous` will go **red** with the instruction to delete the constant and
   assert `not ids`. This is gate 13, in the **default** preflight tier, so it blocks the commit.
   ⚠ Deleting the constant is the honest end state the constant's own comment names ("the honest end
   state is 0, at which point this constant should be deleted and the assertion made absolute") — it
   is not weakening a bar.
4. **Regenerate the header counts** — `test_the_generated_ledger_counts_its_own_unscored_rows`
   asserts `n_unscored_open == len(_unscored_open(entries))`, so the ledger's own counters must be
   rebuilt (`priority.py --write`) rather than hand-edited.
5. **Merge the two duplicate pairs** (`AUT-PD-115`+`AUT-PD-153`, `AUT-PD-097`+`AUT-PD-122`).

---

## ⛔ Flagged, not settled by me — six rows whose CONTENT carries a decision

These are scored so they stop being invisible, but the **work** behind each needs the driver or
trimcrae, and marking them `decision-attached` in the proposals file is how that is recorded. A score
orders work; it does not authorise the decision inside it.

| row | the decision |
|---|---|
| `AUT-PD-137` | Grading `RT-AUTONOMY` differently in `advancing_live_work` changes **what the loop is allowed to call progress**. That is a program judgement, and it is the same question this seat is a symptom of. |
| `AUT-PD-074` | Wiring the `fruitless_attempts` term moves **46 scores**, and `admissibility.derived_score` must change in the same commit or every derived row goes `refused_underivable`. |
| `AUT-PD-073` | Repairing ~13 accumulated scores. ⚠ Adjacent to this seat's own subject; each repair must carry its own `_score_correction`, and it is not a batch edit. |
| `AUT-PD-076` | Either fix requires re-scoping `test_a_prerequisite_outranks_the_thing_it_unblocks` — a decision with a guard change attached, and the row says do not narrow it without mutation-testing. |
| `AUT-PROP-043` | Would make a health condition read **live per-session state no commit contains**, which every other condition avoids by design. The row says decide that explicitly first. |
| `AUT-PROP-044` | The blocking-vs-advisory classification is the driver's, and `research-loop` §1 makes it load-bearing: a `blocks` red stops a cycle. |

**And one remedy I am explicitly refusing to recommend.** The health message's second option is
*"give its route a row in `systems/graph`"*. For these rows that means **creating `RT-AUTONOMY` as a
graph route**, and it should not be done silently:

- `route_score_floor`'s docstring records `RT-AUTONOMY`'s absence as the deliberate mechanism that
  stops the loop's own process defects flooding the queue.
- `AUT-PD-137` — one of the 68 — is the finding that treating `RT-AUTONOMY` as an ordinary route is
  what blinds `advancing_live_work` to the loop auditing itself. **Adding the route row would make
  that defect worse, not better.**
- Re-serving individual rows to real routes is not a derivation either: the 77 committed route floors
  span **10.0 to 190.0**, so for a row like `AUT-PD-116` (which names six routes, floors 10.0 to
  162.0) *the choice of route would BE the score*. That is a judgement wearing a derivation's clothes.

⭐ The one place re-serving is defensible is `AUT-PD-116`, and the honest form is a **split into six
route-served rows**, one per route the artifact already answers, each then inheriting a real graph
floor with no number typed by anyone. That is a ledger write and therefore the driver's.

---

## What I could not do, and what it is actually waiting on

- **Writing the scores.** Waiting on the driver by charter rule 2 —
  `research/autonomy/research-ledger.json` is unowned this sprint. The proposals file is the
  mechanism and it is complete and valid.
- **Splitting `AUT-PD-116` into six route-served rows.** Same reason: a ledger write. Ready to apply.
- **Merging the four `seat/*` branches from `AUT-PD-151`.** A git write, forbidden to this seat, and
  it needs judgement anyway — `seat/s3` carries a ledger closure that disagrees with the trunk.
- ⛔ **Nothing here is waiting on compute, network, or trimcrae.** Every observation in this file was
  a $0 read taken tonight.

## Ledger rows the driver should write

Beyond applying the 68 settlements, one genuinely new defect fell out of the census:

- `what`: **⛔ R5 (`admissibility.refuse_population_growth`) IS A WRITE-PATH RATCHET, NOT A
  REPOSITORY INVARIANT, AND THREE ROWS WALKED PAST IT.** Measured 2026-09-01 by seat S21-UNSCORED at
  `062a48ae`, by replaying `refuse_inadmissible_write(parent, commit, weights)` over the commits that
  actually filed each row: `AUT-PD-155` (`bc4899efc`), `AUT-PD-161` and `AUT-PD-162` (`df529936a`)
  each land a `refused_unscored_new` **today**, and each was filed at a commit that already had R5
  (`ee17c39a2`, 00:49) as an ancestor. `AUT-PD-154` is the control: it predates the merge and
  replays clean. ⭐ THE MECHANISM: R5 runs only inside `ledger_io.write_ledger`; a text edit of
  `research-ledger.json` never reaches it, and nothing re-runs the gate over the **committed** file.
  ★ FIX: a preflight gate (or a test in `research/autonomy/tests`) that runs
  `refuse_inadmissible_write(origin/main's ledger, the working ledger, weights)` on every commit that
  touches the file — the same shape as the guards this repository already keeps for the ledger's ids.
  ⚠ Mutation-test it: append an unscored row to a scratch copy and confirm it goes red.
  `kind`: `process_defect` · `state`: `queued` · `serves.route`: `RT-AUTONOMY` · `cost_class`: `free`
  · proposed `score`: **120.0** (Tier L band floor: it is the guard that keeps this whole population
  from re-forming, and the population is the reason thirteen live portfolio rows were invisible for
  88 hours) · `_score_basis`: EXPLICIT, typed, not derived — same basis form as the 65 above.

---

## Would closing this clear the health row?

**Yes, and the reading afterwards is measured rather than predicted.** With the proposals applied to
an in-memory ledger, `health.py`'s condition computes:

> ✅ `scores_are_reachable` [read] **ALL-RANKABLE** — every one of **191** open row(s) carries a
> score.

(191, not 194, because the three Tier C rows close.) The condition is `advises`, so it never blocked
a cycle — its cost was entirely that 68 rows, including thirteen on live treatment routes, were
outside the ranking and outside every successor prompt.

⚠ **And it will stay green only if cause 3 is fixed.** The population has been flat for three days
because the R5 write-path ratchet is doing its job for cycles that use `ledger_io`; it did **not**
stop three rows that arrived by another path. Clearing the 68 without closing that hole means the
count starts climbing again the next time a session hand-edits the file — which is why the new ledger
row above is proposed at Tier L rather than as housekeeping.

---

## Full census — all 68, at `062a48ae`

Every row is `state: queued`. `proposed` is the number the driver writes. `conf`: `anchored` = follows
from a stated rule against a named committed sibling or a check I ran tonight; `judged` = I ordered it
by reading its text, and a different reader could defensibly move it ±10; `decision-attached` = scored
so it is visible, but the work behind it needs a driver or trimcrae decision (tabled above).

⛔ The `why unscored` column is DERIVED from each row's own `serves.route`, not typed beside it —
typing it put "RT-AUTONOMY, no floor" on two rows whose route is actually null, which is a different
cause with a different fix. Rendering it beside the route column is what caught that.


### Tier L — portfolio / treatment-facing (13)

| id | kind | route | proposed | conf | why unscored | `what`, truncated |
|---|---|---|---|---|---|---|
| `AUT-PD-116` | process_defect | *(null)* | **135.0** | judged | **cause 2** — `serves.route` null → no floor lookup at all | ⛔ SIXTEEN ROUTES CARRY A required_validation MARKED feasible_today=false ON BLK-NO-EMC-DATA WHOSE OWN TEXT NAMES AN EXPRESSION OR TISSUE READ, AND NOT ONE OF THEM CITES A |
| `AUT-PD-151` | process_defect | RT-AUTONOMY | **134.0** | anchored | cause 1 — RT-AUTONOMY, no graph route → no floor | ⛔⛔ FOUR SEATS' FINISHED WORK IS SITTING ON PUSHED BRANCHES THAT NO ROW NAMED AND NOTHING WILL MERGE. Found 2026-08-28T23:35Z (CYC-0072-2e57571a) while releasing the dead  |
| `AUT-PD-113` | process_defect | RT-AUTONOMY | **132.0** | judged | cause 1 — RT-AUTONOMY, no graph route → no floor | ⚠ `BLK-NO-EMC-DATA`'s `retired_by_action` IS IMPRECISE, AND 38 OF 77 ROUTES INHERIT IT. It says what would retire it is 'an EMC dependency or drug-response screen (… or a |
| `AUT-PD-104` | process_defect | RT-AUTONOMY | **131.0** | judged | cause 1 — RT-AUTONOMY, no graph route → no floor | ★★ AUDIT EVERY ROUTE FOR A STATUS OR `readiness.missing` CLAIM THAT A COMMITTED ARTIFACT REFUTES. THIS IS THE THIRD INSTANCE IN ONE DAY and the trend is what matters: AUT |
| `AUT-PD-088` | process_defect | RT-AUTONOMY | **129.0** | judged | cause 1 — RT-AUTONOMY, no graph route → no floor | THREE ROUTES RECORDED `closed` STILL CARRY A REOPENING TRIGGER: RT-SYNPROMOTER and RT-RXR carry TECH-* revisit_triggers, RT-6MP a TR-* revival_trigger, while systems/CONV |
| `AUT-PD-098` | process_defect | RT-AUTONOMY | **128.0** | judged | cause 1 — RT-AUTONOMY, no graph route → no floor | ★★ SWEEP EVERY ROUTE GRADE FOR THE DEFECT CLASS AUT-062 FOUND BY READING ONE ROUTE: a TRANSCRIPT-ABUNDANCE number described as reporting a protein's ACTIVITY. ⛔ NOBODY HA |
| `AUT-PD-111` | process_defect | RT-AUTONOMY | **127.0** | judged | cause 1 — RT-AUTONOMY, no graph route → no floor | ★★ ADD A STANDING CLASS-LEVEL LITERATURE QUERY BESIDE THE EMC-SCOPED PRIOR-ART SCREEN. The scope gap that hid a 2005 phase II trial for twenty-one years (AUT-013) applies |
| `AUT-PD-087` | process_defect | RT-AUTONOMY | **126.0** | judged | cause 1 — RT-AUTONOMY, no graph route → no floor | THREE ROUTE RECORDS CONTRADICT THEMSELVES IN THE OTHER DIRECTION: `ready`/`pursue_now` on a route whose next action is a CONCLUSION — RT-CARFILZOMIB ('needs no further lo |
| `AUT-PD-095` | process_defect | RT-AUTONOMY | **124.0** | judged | cause 1 — RT-AUTONOMY, no graph route → no floor | ★ MEASURE THE RESIDUE AUT-PD-086 SAMPLED, THEN GUARD IT. Measured on the corrected graph: NINE further routes with a not-takeable status carry a required_validation row r |
| `AUT-PD-103` | process_defect | RT-AUTONOMY | **123.0** | judged | cause 1 — RT-AUTONOMY, no graph route → no floor | ⛔ `TR-*` REVIVAL TRIGGERS ARE DEFINED ONLY IN THE LEGACY emc-systems-map.json: systems/graph carries NO TR-* records, and nothing validates that a route's `revival_trigge |
| `AUT-PD-083` | process_defect | RT-AUTONOMY | **122.0** | judged | cause 1 — RT-AUTONOMY, no graph route → no floor | ⛔ AN ARTIFACT IN THE ZENODO DEPOSIT CONTRADICTS ITSELF ABOUT ITS OWN CONTROLS: aso-control-oligos.json's `⛔_not_a_claim_of_inertness` field says a control 'FAILS the spec |
| `AUT-PD-084` | process_defect | RT-AUTONOMY | **121.0** | judged | cause 1 — RT-AUTONOMY, no graph route → no floor | ⛔ ONE FACT, TWO SOURCES, BOTH IN THE RELEASED DEPOSIT: aso-parent-gap-pairing.json attributes the seven-to-ten hybridised-nucleotide RNase-H1 range to PMID 35664704, whil |
| `AUT-PROP-047` | proposal | RT-AUTONOMY | **120.0** | judged | cause 1 — RT-AUTONOMY, no graph route → no floor | RUN claim_audit.py ON THE DEGRADER PAPER. One manuscript is one manuscript: the ASO draw found a 3-refutation shape in interpretation claims and zero in twenty data/liter |

### Tier M — loop machinery costing the loop work now (32)

| id | kind | route | proposed | conf | why unscored | `what`, truncated |
|---|---|---|---|---|---|---|
| `AUT-PD-076` | process_defect | RT-AUTONOMY | **119.0** | judged | cause 1 — RT-AUTONOMY, no graph route → no floor | ⛔⛔ THE RANKER'S QUEUE HEAD IS DOMINATED BY ROWS THAT ARE ALREADY CLOSED — measured 2026-08-28 by seat s63-prereqscore: 7 of the top 10 at origin/main, and 10 of 10 AFTER  |
| `AUT-PD-150` | process_defect | RT-AUTONOMY | **118.0** | judged | cause 1 — RT-AUTONOMY, no graph route → no floor | ⛔⛔ A LEASE WHOSE HOLDER'S SESSION HAS BEEN ARCHIVED IS INVISIBLE TO EVERY INSTRUMENT THE LOOP HAS, AND IT PARKS THE QUEUE FOR THE FULL 8 h LEASE. Measured 2026-08-28T23:3 |
| `AUT-PD-137` | process_defect | RT-AUTONOMY | **117.5** | decision-attached | cause 1 — RT-AUTONOMY, no graph route → no floor | ⛔⛔ `advancing_live_work` CANNOT SEE THE LOOP AUDITING ITSELF, WHICH IS THE ONE THING CLAUDE.md §0 ASKS IT TO CATCH — MEASURED 2026-08-28 (CYC-0069). The condition asks 'a |
| `AUT-PROP-050` | proposal | RT-AUTONOMY | **117.0** | judged | cause 1 — RT-AUTONOMY, no graph route → no floor | ⛔⛔ WIRE `holder_liveness.py` INTO `continuity.py`'s CAPACITY COUNT — AND IT IS FILED RATHER THAN DONE BECAUSE OF research-loop §6. AUT-PD-150 built the detector: given a  |
| `AUT-PD-060` | process_defect | RT-AUTONOMY | **116.5** | judged | cause 1 — RT-AUTONOMY, no graph route → no floor | ⛔ A REVIEW-SEAT SUBAGENT EDITED THE LIVE TRACKED TREE DURING A READ-ONLY HARDENING ROUND, AND ONLY THE 'STAGE BY PATH, NEVER -A' RULE CAUGHT IT (CLAUDE.md §6). Round 12 o |
| `AUT-PD-155` | process_defect | RT-AUTONOMY | **116.0** | anchored | cause 1 — RT-AUTONOMY, no graph route → no floor | ⛔⛔ THE COMMIT LOOP COSTS ~5x WHAT CLAUDE.md §6 SAYS IT DOES, AND GATE 13 — THE ONE ADDED AS 'A FAST, OFFLINE, PURE-LOGIC SUITE' — HAS DRIFTED 9.4x. Measured 2026-08-29 (C |
| `AUT-PD-161` | process_defect | *(null)* | **115.0** | judged | **cause 2** — `serves.route` null → no floor lookup at all | HANDOFF.PY ADVERTISES LEDGER ROWS THAT EXIST ON NO REF, BECAUSE IT READS THE WORKING TREE WHILE ITS OWN DOCSTRING PROMISES COMMITTED STATE -- AND THE FAILURE IS NOT A DAN |
| `AUT-PD-066` | process_defect | RT-AUTONOMY | **114.0** | judged | cause 1 — RT-AUTONOMY, no graph route → no floor | ⛔⛔ `claim.py` TURNS A ONE-ROW LEASE INTO AN UNGATED PUSH WHEN THE TREE IS DIRTY, AND NOTHING REFUSES IT. Measured 2026-08-28 by CYC-0053-3217966b, on itself: the driver h |
| `AUT-PD-153` | process_defect | RT-AUTONOMY | **113.0** | judged | cause 1 — RT-AUTONOMY, no graph route → no floor | ⛔⛔ `session_cap.verdict()` IS INVERTED ON THE SUCCESS CASE: A SESSION THAT HANDS OFF CORRECTLY IS TOLD **MUST NOT STOP**, AND ONE WHOSE HANDOFF FAILED IS TOLD **MAY STOP* |
| `AUT-PD-115` | process_defect | RT-AUTONOMY | **112.0** | judged | cause 1 — RT-AUTONOMY, no graph route → no floor | ⛔⛔ `session_cap.py` CANNOT TELL A SUCCESSFUL HANDOFF FROM NO HANDOFF AT ALL, AND SAYS THE WRONG ONE. Measured 2026-08-28 by CYC-0061-3217966b on its own committed receipt |
| `AUT-PD-121` | process_defect | RT-AUTONOMY | **111.0** | judged | cause 1 — RT-AUTONOMY, no graph route → no floor | ⛔ `session_id` HAS TWO READERS THAT NEED IDS FROM DIFFERENT NAMESPACES, AND THE FIX FOR ONE SILENTLY DISABLED THE OTHER. `session_reaper.py` joins the session list agains |
| `AUT-PD-122` | process_defect | RT-AUTONOMY | **110.0** | judged | cause 1 — RT-AUTONOMY, no graph route → no floor | ⛔⛔ ENTRY IDS COLLIDE THE SAME WAY RECEIPT IDS DID, AND THE FIX APPLIED TO ONE WAS NEVER APPLIED TO THE OTHER. `ids.next_entry_id` derives max+1 over committed state, so t |
| `AUT-PD-097` | process_defect | RT-AUTONOMY | **109.0** | judged | cause 1 — RT-AUTONOMY, no graph route → no floor | `research/autonomy/ids.py`'s `next_receipt()` already carries a session discriminator so two concurrent cycles can be 'both genuinely the Nth cycle' and never collide on  |
| `AUT-PD-128` | process_defect | RT-AUTONOMY | **108.5** | judged | cause 1 — RT-AUTONOMY, no graph route → no floor | ⛔ `continuity.py --check` IS STEP 12 OF THE CYCLE CONTRACT AND A CORRECTLY-HANDED-OFF CYCLE CANNOT PASS IT. Its own message names three acceptable ways to end a turn — 's |
| `AUT-COV-001` | process | *(null)* | **108.0** | judged | **cause 2** — `serves.route` null → no floor lookup at all | ⛔ 22 OF 32 PUBLICATION ENDPOINTS ARE READ BY NO INSTRUMENT AT ALL, AND EVERY CORRECTION ROUND MAKES IT WORSE. Measured 2026-08-27 by `python3 research/manuscripts/claim_c |
| `AUT-PD-136` | process_defect | RT-AUTONOMY | **107.0** | judged | cause 1 — RT-AUTONOMY, no graph route → no floor | ⛔ THE QUEUE'S TOP THREE ROWS ARE DISPOSITIONS, NOT WORK, AND THEY HAVE BEEN FOR THREE WEEKS — MEASURED 2026-08-28 (CYC-0069). AUT-025 (152.0), AUT-044 (147.0) and AUT-071 |
| `AUT-COV-002` | process | *(null)* | **106.0** | judged | **cause 2** — `serves.route` null → no floor lookup at all | ⛔ `claim_coverage.py` CREDITS A TEST MODULE'S PATTERNS TO ANY DOCUMENT WHOSE BASENAME APPEARS ANYWHERE IN THAT MODULE — A COMMENT COUNTS. Measured 2026-08-27 (CYC-0014) w |
| `AUT-PD-073` | process_defect | RT-AUTONOMY | **105.5** | decision-attached | cause 1 — RT-AUTONOMY, no graph route → no floor | ⛔ SCORE RESIDUE: ~13 hand-filed rows carry values the additive-term defect accumulated before AUT-PROP-036's fix landed (a660303). AUT-PROP-026 is off by roughly −1160 (≈ |
| `AUT-PD-074` | process_defect | RT-AUTONOMY | **105.0** | decision-attached | cause 1 — RT-AUTONOMY, no graph route → no floor | ⛔ `priority-weights.json:terms.fruitless_attempts` (weight −8.0) IS APPLIED NOWHERE IN priority.py. Measured 2026-08-28 by seat s36-admissibility: it is echoed as a hard- |
| `AUT-PD-089` | process_defect | RT-AUTONOMY | **104.0** | judged | cause 1 — RT-AUTONOMY, no graph route → no floor | `apply_age_factor` AGES PARKED ROWS, so a row nothing can take keeps climbing the ranked table — its docstring says OPEN ROWS ONLY and `parked` now belongs in that skip s |
| `AUT-PD-077` | process_defect | RT-AUTONOMY | **103.0** | judged | cause 1 — RT-AUTONOMY, no graph route → no floor | ⛔ A BLOCK KEYED ON THE PRESENCE OF TEXT CAN NEVER SELF-CLEAR. The −90 fires on ANY non-empty blocked_evidence, deliberately (a session writing state: blocked gets it reve |
| `AUT-PD-154` | process_defect | RT-AUTONOMY | **102.0** | judged | cause 1 — RT-AUTONOMY, no graph route → no floor | ⛔ STEP 11 OF THE CYCLE CONTRACT CANNOT COMPLETE IN AN AUTO-PERMISSION CCR SESSION — THE REAPER DECIDES AND THE ARCHIVE IS REFUSED. Measured 2026-08-29 (CYC-0074-5a21085f) |
| `AUT-PD-120` | process_defect | RT-AUTONOMY | **101.0** | judged | cause 1 — RT-AUTONOMY, no graph route → no floor | ⚠ A LEASE ON ONE ROW WAS READ AS OWNERSHIP OF A WHOLE RED BUILD, AND IT HELD FOR THREE CYCLES. CYC-0062 and CYC-0063 each met the same five failing manuscript guards on ` |
| `AUT-PD-092` | process_defect | RT-AUTONOMY | **100.0** | judged | cause 1 — RT-AUTONOMY, no graph route → no floor | A SEAT'S `PREFLIGHT_MODALITIES=1` ON AN UNMODIFIED WORKTREE GATES NOTHING AND SAYS OK. Measured 2026-08-28: a clean worktree at origin/main ran the flag and executed ZERO |
| `AUT-PD-085` | process_defect | RT-AUTONOMY | **99.0** | judged | cause 1 — RT-AUTONOMY, no graph route → no floor | THE MANUSCRIPTS SUITE INTERMITTENTLY REPORTS A WHOLE FILE AS ERROR UNDER xdist: 15 items of test_fusion_partner_prose_asserts_the_relations_its_artifact_computes.py error |
| `AUT-PD-012` | process_defect | *(null)* | **98.5** | judged | **cause 2** — `serves.route` null → no floor lookup at all | ⛔ THE HARNESS REPORTED 'exit code 0' FOR A BACKGROUNDED PREFLIGHT THAT FAILED. Measured 2026-08-27 (CYC-0011): `./scripts/preflight.sh > log 2>&1; echo "EXIT=$?" >> log`  |
| `AUT-PD-070` | process_defect | RT-AUTONOMY | **98.0** | judged | cause 1 — RT-AUTONOMY, no graph route → no floor | ⛔ A FOREGROUND BASH CALL THAT HITS THE HARNESS TIMEOUT LEAVES A LIVE CHILD, AND THE EXISTING HOOK CANNOT SEE IT. Measured 2026-08-28 by seat s35-outofideas, on itself: a  |
| `AUT-PD-162` | process_defect | *(null)* | **97.5** | judged | **cause 2** — `serves.route` null → no floor lookup at all | THE COMMIT LOOP IS ~4x SLOWER THAN THE TRUNK'S MEDIAN PUSH INTERVAL, SO A DRIVER THAT OBEYS THE GATING RULE IS STRUCTURALLY LIKELY TO BE OVERTAKEN -- AND THE COMMITS OVER |
| `AUT-PD-064` | process_defect | RT-AUTONOMY | **97.0** | judged | cause 1 — RT-AUTONOMY, no graph route → no floor | ⛔ GENERIC FIXED PATHS OUTSIDE THE SCRATCHPAD ROOT ARE AUT-PD-055 ONE LEVEL OUT, and seat_scratch.py --audit-root cannot see them by construction. Measured 2026-08-28 by s |
| `AUT-PD-079` | process_defect | RT-AUTONOMY | **96.0** | judged | cause 1 — RT-AUTONOMY, no graph route → no floor | ⛔ THE LINTER'S OWN RULE TABLE IS STALE, AND EVERY GATE STAYED GREEN OVER IT FOR TWELVE DAYS. Measured 2026-08-28 by seat s37-grade: research/manuscripts/lint_claims.py ha |
| `AUT-PD-011` | process_defect | *(null)* | **95.5** | judged | **cause 2** — `serves.route` null → no floor lookup at all | ⛔ A PreToolUse HOOK REGISTERED WITH A RELATIVE PATH MAKES ONE `cd` FATAL TO THE WHOLE SESSION'S Bash TOOL, AND THE RECOVERY PATH RUNS THROUGH THE BROKEN TOOL. Measured 20 |
| `AUT-PD-138` | process_defect | RT-AUTONOMY | **95.0** | judged | cause 1 — RT-AUTONOMY, no graph route → no floor | ⛔ A COMMIT THAT EDITS AN ARCHIVED MANUSCRIPT CANNOT HAVE A GREEN PREFLIGHT, AND THE GENERATOR'S OWN DOCUMENTED FIX REQUIRES MAKING THAT COMMIT ANYWAY — MEASURED 2026-08-2 |

### Tier S — latent, cosmetic, or a proposal awaiting a decision (20)

| id | kind | route | proposed | conf | why unscored | `what`, truncated |
|---|---|---|---|---|---|---|
| `AUT-BIX-001` | process_defect | RT-AUTONOMY | **94.0** | judged | cause 1 — RT-AUTONOMY, no graph route → no floor | ⭐ ENUMERATE EVERY AGENT-WRITTEN ARTIFACT THAT HAS NO MACHINE-CHECKED OUTPUT CONTRACT — this is the axis on which the model this repository RUNS is externally measured to  |
| `AUT-PD-068` | fetch | RT-AUTONOMY | **93.0** | judged | cause 1 — RT-AUTONOMY, no graph route → no floor | ⛔ THE LOOP'S CLONE IS SHALLOW, AND IT CENSORS EVERY GIT-DERIVED INSTRUMENT. Measured 2026-08-28 by seat s35-outofideas: both stuck_clock.py and the new out_of_ideas.py ar |
| `AUT-PD-065` | process_defect | RT-AUTONOMY | **92.0** | judged | cause 1 — RT-AUTONOMY, no graph route → no floor | ⛔ A SEAT-PROMPT CONVENTION THAT LIVES ONLY IN A SKILL BINDS ONLY WHEN THE SKILL IS LOADED — the same reachability gap CLAUDE.md §6 already records for research-loop §3's  |
| `AUT-PD-125` | analysis | RT-AUTONOMY | **91.0** | judged | cause 1 — RT-AUTONOMY, no graph route → no floor | ⭐ MEASURE THE BLIND SEATS' MISS RATE, WHICH IS THE ONE NUMBER THAT WOULD LET CLAUSE 1 CARRY A REAL STOPPING BOUNDARY. AUT-PROP-038 established that hardening convergence  |
| `AUT-PROP-046` | proposal | RT-AUTONOMY | **90.0** | judged | cause 1 — RT-AUTONOMY, no graph route → no floor | PROPOSAL from seat s36-admissibility: give cycle receipts ONE machine-readable field recording the ledger score the cycle acted on, so the admission predicate can adjudic |
| `AUT-PD-071` | process_defect | RT-AUTONOMY | **89.0** | judged | cause 1 — RT-AUTONOMY, no graph route → no floor | ⛔ OUTWARD-FACING ENV READ, TWO-VALUED: scripts/aixiv_review.py:64 reads BASE = os.environ.get('AIXIV_BASE', 'https://aixiv.science'). An exported-empty or wrong value dec |
| `AUT-PROP-045` | proposal | RT-AUTONOMY | **88.0** | judged | cause 1 — RT-AUTONOMY, no graph route → no floor | PROPOSAL from seat s34-healthaxes: give the cycle receipt an `escalation_raised: [<condition keys>]` field, so a future health condition can MEASURE whether the §3 escala |
| `AUT-080` | fetch | RT-AUTONOMY | **87.0** | judged | cause 1 — RT-AUTONOMY, no graph route → no floor | $0 ACTIONS JOB against export.arxiv.org/api/query to anchor the 13 arXiv identifiers AUT-PD-057 left at `unverified_at_baseline`, moving each to `verified` with a real fe |
| `AUT-BIX-002` | process | RT-AUTONOMY | **85.0** | judged | cause 1 — RT-AUTONOMY, no graph route → no floor | ⭐ GIVE THE LOOP AN EXTERNALLY-ANCHORED FAILURE VOCABULARY — adopt BixBench3's closed ten-tag failure-mode set as an optional `failure_modes` block on the cycle receipt, a |
| `AUT-PROP-044` | proposal | RT-AUTONOMY | **86.0** | decision-attached | cause 1 — RT-AUTONOMY, no graph route → no floor | PROPOSAL from seat s35-outofideas: wire out_of_ideas.route_reports() into health.py as a condition (c_routes_have_ideas) with an EXPLICIT CONDITION_ON_RED classification  |
| `AUT-PD-081` | process_defect | RT-AUTONOMY | **84.0** | judged | cause 1 — RT-AUTONOMY, no graph route → no floor | TOOLING GAP IN THE SEAT-LOG CHECKER, found by using it: research/autonomy/seat_scratch.py --verify-log should flag a log whose `EXIT=` marker is not at line start. Measur |
| `AUT-PD-039` | process_defect | *(null)* | **83.0** | judged | **cause 2** — `serves.route` null → no floor lookup at all | Fix _known_anchors()'s numbered-section regex to accept 'N.' as well as 'N ·' (or make the separator configurable per-document), verify it now extracts emc-vaccine-develo |
| `AUT-PROP-043` | proposal | RT-AUTONOMY | **82.0** | decision-attached | cause 1 — RT-AUTONOMY, no graph route → no floor | PROPOSAL from seat s55-scratchpad (AUT-PD-055), NOT BUILT because it needs a driver-level decision: add a health.py axis that reads the LIVE scratchpad root via seat_scra |
| `AUT-PD-114` | process_defect | RT-AUTONOMY | **80.0** | judged | cause 1 — RT-AUTONOMY, no graph route → no floor | ⛔ `UNCOVERED_BY_LINT_CITATIONS` STILL NAMES AUT-PD-038 AS FULLY OPEN, though that row is `done` and its fix (`_redact_failed_fetches`) is present in the code. ⚠ THE HONES |
| `AUT-PD-080` | process_defect | RT-AUTONOMY | **78.0** | judged | cause 1 — RT-AUTONOMY, no graph route → no floor | DATED-SUPERSESSION NOTE, not an inline rewrite: '110+ organisations' for GRADE endorsement is UNDERSTATED — the live reading fetched 2026-08-28 (CI run 33181002075, grade |
| `AUT-PD-072` | process_defect | RT-AUTONOMY | **76.0** | judged | cause 1 — RT-AUTONOMY, no graph route → no floor | ONE FACT, TWO PLACES: research/manuscripts/program/emc-autonomy-architecture.md §5.2's condition table has no `axis` column and no restart-intensity paragraph, while heal |
| `AUT-PROP-001` | process_defect | *(null)* | **74.0** | judged | **cause 2** — `serves.route` null → no floor lookup at all | PROPOSAL (filed, not applied): teach systems_check.check_scan_interop the `venue` trigger_kind, then re-enable scan_enabled on the three TRG-VENUE-* triggers. Not applied |
| `AUT-PD-067` | process_defect | RT-AUTONOMY | **72.0** | judged | cause 1 — RT-AUTONOMY, no graph route → no floor | ⛔ `proposal_dedup.Adjudicator.admit()` IS BUILT, CALIBRATED AND CALLED BY NOTHING — the exact 'a rule that governed nothing' shape CLAUDE.md §1 records twice (subagent_wi |
| `AUT-PD-069` | regrade | RT-AUTONOMY | **70.0** | decision-attached | cause 1 — RT-AUTONOMY, no graph route → no floor | REGRADE, blocked behind the unshallow above and filed so it is not lost: re-measure out_of_ideas.py's EMPTY_ROUNDS_TO_HUMAN=4 against real history once the clone is deep. |
| `AUT-PD-078` | process_defect | RT-AUTONOMY | **66.0** | judged | cause 1 — RT-AUTONOMY, no graph route → no floor | LATENT, CHEAP TO CLOSE: a self-referential `prerequisite_of` (a row naming itself) is not idempotent under the committed `_resolve` — it gains +bonus on every re-score, r |

### Tier C — close, do not score (3)

| id | kind | route | proposed | conf | why unscored | `what`, truncated |
|---|---|---|---|---|---|---|
| `AUT-PD-090` | process_defect | RT-AUTONOMY | `state: done` | anchored | **cause 3** — finished, never closed out of `queued` | ⛔ THE xdist PROBE IN preflight.sh WAS A pipefail/SIGPIPE RACE, AND ABOUT HALF OF EVERY MODALITIES RUN SINCE 2026-08-23 HAS SILENTLY PAID ~11 EXTRA MINUTES FOR IT. Caught  |
| `AUT-PD-091` | process_defect | RT-AUTONOMY | `state: done` | anchored | **cause 3** — finished, never closed out of `queued` | ⛔ THE DEPENDENCY BANNER PROBED A HARD-CODED `python3` WHILE THE TESTS RUN UNDER $PYTEST — a one-of-a-pair defect, and the pair is documented: the xdist probe ~20 lines be |
| `AUT-PD-118` | process_defect | RT-AUTONOMY | `state: done` | anchored | **cause 3** — finished, never closed out of `queued` | ⚠ A SUCCESSOR SESSION IS IDLE WITH NO COMMITTED RECEIPT, WHICH IS THE ONE THING session_reaper.py REFUSES TO ARCHIVE — because a cycle that died holding uncommitted work  |
