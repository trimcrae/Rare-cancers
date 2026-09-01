---
id: DOC-SPRINT-S9-SEATRECORD
title: "S9-SEATRECORD — the roll-up was a sixth seat, and a dead seat would have been a clean one"
level: L3
kind: process
status: live
date: 2026-09-01
audience: [autonomous research agents, maintainers]
---

# S9-SEATRECORD — the roll-up was a sixth seat, and a dead seat would have been a clean one

**Item(s):** AUT-PD-193, AUT-PROP-006
**Owned paths:** `research/autonomy/publish_bar.py`, `research/autonomy/seat_scratch.py`,
`research/autonomy/tests/test_a_round_rollup_is_not_a_sixth_seat.py`,
`research/autonomy/tests/test_a_seat_writes_its_record_before_it_looks.py`, this file
**Started/Finished (UTC):** 2026-09-01T18:35Z / 2026-09-01T19:20Z

## Verdict

**FIXED (both), with one half of AUT-PD-193 deliberately left open** — the roll-up miscount is
reproduced and closed by two added refusals plus an honest seat count, AUT-PROP-006's write-first
record is implemented in `seat_scratch.py` with the bar-side coupling that makes it safe, and the one
change that would have made a paper pass **more** easily was identified, not made, and is written up
below for a later cycle. ⚠ My own first version of the fix red on true input and a positive control
caught it within the hour — §1a, kept as a finding rather than quietly repaired.

---

## What I measured

### 1 · AUT-PD-193 reproduces, and it is worse than the row says

`publish_bar._seat_records` globs `{pub_id}-{sha}*.json`; a round's roll-up is filed as
`{pub_id}-{sha}.json`, which that glob matches with `*` empty. Reading the committed records in
`research/autonomy/review-seats/`:

```
round 20  PUB-ASO-b53290b37e71 : glob returns 6 (5 seat + 1 roll-up)  counted 4 blk / 7 P1   true 4 / 7
round 26  PUB-ASO-7a7f408258c8 : glob returns 6 (5 seat + 1 roll-up)  counted 2 blk / 10 P1  true 1 / 5
round 27  PUB-ASO-6127da1ac1a2 : glob returns 5 (5 seat + 0 roll-up)  counted 5 blk / 12 P1  true 5 / 12
round 21  PUB-ASO-a9dd5d34ce66 : glob returns 4 (4 seat + 0 roll-up)  counted 2 blk / 12 P1  true 2 / 12
```

Round 26 is the double count in the open: its roll-up's `_role` states the opposite rationale in
words — *"carries the union of their tallies, so a derivation over the seat glob counts each finding
exactly once"* — and the derivation counts each of them twice. Round 20's roll-up carries **empty**
tallies and a `_tallies_live_on_the_seat_records` field citing the round-7 PUB-FUSION-PARTNER
precedent. Only round 20's convention is correct against the code. **Four committed roll-ups carry
populated tallies**: `PUB-ASO-7a7f408258c8`, `PUB-ATR-c1bc934fec3c`,
`PUB-FUSION-PARTNER-21bc8578b11a`, `PUB-FUSION-PARTNER-34264bbeb610`.

**The count it produces versus the count it should produce**, run against the pre-change module from
`git show HEAD:research/autonomy/publish_bar.py` in a scratch clone (never the live tree), on a
fixture reproducing round 26's shape — five seats with one P1 each, a roll-up carrying the union of
five, a hardening record honestly declaring five:

```
BEFORE: FAIL — "record under-reports its own seats: it declares 0 blocker(s) and 5 P1(s),
                the seats record 0 and 10"
AFTER : FAIL — "round roll-up(s) PUB-X-…json carry their own `blockers`/`p1s` … the doubled total
                is what the under-reporting check below compares the record against …"
```

That is the reachable failure the ledger row predicts, observed rather than argued: **the honest
record is refused for under-reporting findings that exist once**, and a record that declared the
doubled ten would have passed instead.

**A further hole the row does not name, found by running it rather than reading it:** a five-seat
round could clear a **six-seat** width floor, because `len(seats)` counted the roll-up, so filing one
extra file bought a look. `PASS` before, `FAIL — 5 blind seat(s) against 6` after.

And on a clean five-seat round with an empty roll-up the passing evidence line read
`0 blockers across 6 blind seat(s)` — a printed count of looks that was wrong by one, on the line
that clears a paper.

### 1a · ⛔⛔ MY OWN FIRST VERSION RED ON TRUE INPUT, AND A POSITIVE CONTROL CAUGHT IT

Recorded rather than quietly fixed, because it is the more useful finding of the two.

The obvious form of the fix is *"exclude `{pub}-{sha}.json` from the seat set"*. **That is wrong.**
`clause_6_independent_adversarial_seat` reads **exactly** that path
(`publish_bar.py`, `_read_json(SEATS_DIR / f"{pub_id}-{sha}.json")`), so the bare filename is the
**canonical record of a round's adversarial seat**, and rounds have been filed with nothing else:

```
PUB-FUSION-PARTNER-21bc8578b11a : seat-siblings=0   tallies 4 blockers / 9 P1s
PUB-FUSION-PARTNER-69d8a6ac1c90 : seat-siblings=0   tallies 0 / 0
PUB-ASO-7a7f408258c8            : seat-siblings=5   tallies 1 / 5     <- a genuine roll-up
PUB-ATR-c1bc934fec3c            : seat-siblings=4   tallies 1 / 4     <- a genuine roll-up
PUB-FUSION-PARTNER-34264bbeb610 : seat-siblings=2   tallies 9 / 16    <- a genuine roll-up
```

The unconditional exclusion made clause 1 refuse a round whose only record **is** its seat, and
deleted that round's findings from the tally — the silent-discard failure `paper-hardening` §8.0a
warns about, committed while quoting §8.0a. It was caught within the hour by
`systems/tests/test_autonomy_publish_bar.py::test_all_six_clauses_passing_is_what_it_takes`, whose
one blind seat is filed at that path. **That is what positive controls are for**, and it is why
§8b.1 rates a gate that reds on true input worse than one that greens on false input: the first
thing anyone does to it is loosen it, and here that would have meant deleting the whole fix.

★ **So the rule is CONDITIONAL, not a flat exclusion: `{pub}-{sha}.json` is a roll-up only when
per-lens `-seat-*` records sit beside it.** Alone it is the round's one look and its tallies are the
only copy there is. Both halves are now asserted —
`test_a_bare_record_standing_alone_is_the_rounds_one_look_and_keeps_its_tallies` and
`test_a_lone_bare_records_findings_are_not_discarded` — and the near-miss is written into both
docstrings.

**The discriminator had to be the filename, and that was measured, not chosen.** Both obvious
alternatives fail on committed evidence: roll-ups routinely carry a `seat` key
(`PUB-ASO-b53290b37e71`'s reads *"five blind seats - regression, arithmetic, …"*), and the four
PUB-ATR seat files carry `lens` instead of `seat`. A third shape already exists —
`PUB-FUSION-PARTNER-69d8a6ac1c90-round4-p1-rederivation.json` is blind, matches the glob and is not
a seat — so the predicate is `startswith(f"{pub}-{sha}-seat-")` rather than a list somebody must
remember to extend (`paper-hardening` §8b.2).

### 2 · AUT-PROP-006 reproduces as a *hole in the bar*, not only a gap in the contract

The row asks that a seat's record be written **first**, so a seat that dies leaves evidence. Writing
it first creates a record that is honestly `blind: true`, honestly names the commit it is about to
read, and honestly carries empty `blockers`/`p1s` — because at that moment the seat has found
nothing. **Every filter in `_seat_records` admits it.** Measured against the pre-change module:

```
BEFORE: four seats reported + one seat that opened its record and died  ->  PASS,
        "round 9 on eeeeeeeeeeee: 0 blockers across 5 blind seat(s)"
AFTER : FAIL — "blind seat record(s) still open at eeeeeeeeeeee: PUB-X-…-seat-lens4.json"
```

So implementing AUT-PROP-006 **without** a bar-side refusal would have turned every dead seat into a
clean look, and the dead seat is the one that makes the round look widest. The two halves are only
safe together; they are implemented together and asserted in one file.

### 3 · No paper's verdict moved

Clause 1 at each paper's declaring commit, before and after:

| paper | before | after |
|---|---|---|
| PUB-ASO @ `b53290b37e71` | FAIL — 4 blockers open at round 20 | FAIL — 4 blockers open at round 20 |
| PUB-ATR @ `c1bc934fec3c` | FAIL — 7 blockers open at round 1 | FAIL — roll-up carries its own tallies |
| PUB-FUSION-PARTNER @ `9d5b4defef94` | FAIL — 9 blockers open at round 11 | FAIL — 9 blockers open at round 11 |

PUB-ATR now fails earlier and for a more precise reason; it was already failing on seven blockers.
**Nothing went from FAIL to PASS.**

### 4 · Tests, and mutation

Run against the pre-change modules (`git show HEAD:…` into a scratch clone) and then against the
live tree:

| | before the change | after |
|---|---|---|
| `test_a_round_rollup_is_not_a_sixth_seat.py` (8) | 4 failed, 3 passed, 1 skipped | 8 passed |
| `test_a_seat_writes_its_record_before_it_looks.py` (9) | 8 failed, 1 passed | 9 passed |
| **both** | **12 failed, 4 passed, 1 skipped** | **17 passed** |

The four tests passing in the "before" column are the **positive controls** — cases that must pass
both before and after, present so that a clause broken into refusing everything would not satisfy
this suite. The skip is the real-repo predicate check, whose `review-seats/` directory the scratch
clone does not carry. Both files contain a roll-up case **and** a no-roll-up case, as the item
requires, plus the lone-bare-record case §1a describes.

`systems/tests/test_autonomy_publish_bar.py` (35) and
`systems/tests/test_convergence_is_a_repeated_look_not_a_single_test.py` (5) — the existing suites
over this clause — are green on the change: **40 passed, exit 0** (log:
`<scratchpad>/S9-SEATRECORD/S9-existing-suites.log`). ⚠ The run took **249 s** for 40 pure-logic
tests; see the concurrency note below.

**Mutation test: 11 single-site mutations, 11 caught, 0 survived**, each asserted to have *landed*
(anchor found exactly once, file bytes changed) before the result was read, and each restored and
byte-compared afterwards — §8b's rule that a mutation which never lands reports exactly what a guard
that never fires reports. Harness and log:
`<scratchpad>/S9-SEATRECORD/S9-mutate.py`, `<scratchpad>/S9-SEATRECORD/S9-mutation.log`, stamped
with `seat_scratch.py --stamp`. **It ran against a clone at `<scratchpad>/S9-SEATRECORD/mut/`, never
the live tree** (charter §7; `paper-hardening` §8b.1).

Mutations: `_is_seat_file` always true · the lone-bare-record fallback dropped · the roll-up tally
refusal made unconditional · each of the two new clause-1 refusals neutralised in turn · the width
count reverted to records · `close` no longer requiring an open record · `close` re-closing a
complete record · `open` overwriting a closed record · `close` relabelling the pinned commit · the
open record written without its `status` field.

---

## What I changed

### `research/autonomy/publish_bar.py` — GOVERNED. Every change is STRICTER or EQUAL.

| # | change | direction | why that direction |
|---|---|---|---|
| 1 | new `_is_seat_file(pub_id, sha, name)` | **neutral** (a predicate; nothing calls it yet at this line) | carries the measurement and the two failed alternatives |
| 2 | the seat set at the pin is the `-seat-*` records, **falling back to every blind record when there are none** | **STRICTER or EQUAL** — smaller where both shapes exist, identical where only the bare record does | see §1a: the bare record alone IS the round's seat, and excluding it reds on true input |
| 3 | clause 1 refuses any record at the pin with `status: "open"` | **STRICTER** — added refusal | without it, AUT-PROP-006 turns a dead seat into a clean one |
| 4 | clause 1 refuses a roll-up carrying its own `blockers`/`p1s`, **only where `-seat-*` records exist beside it** | **STRICTER** — added refusal | fixes the *input*, not the meter; conditioned so a lone record's findings are never discarded |
| 5 | the width floor counts the declaring round in **seats**, not records | **STRICTER** — the declaring number falls, so the check fires more often | one extra file used to buy a look |
| 6 | the passing evidence line prints the seat count | **neutral** — reporting; nothing gates on the string | the printed count of looks was wrong by one |

**Why #4 is a refusal and not a subtraction, which is the load-bearing judgement in this seat.** The
obvious fix is to drop the roll-up from the tally sum. That is a **LOOSENING**: a roll-up is a
*synthesis*, so it can grade a blocker no single seat filed, and subtracting it would silently
discard that finding. `paper-hardening` §8.0a says exactly this about exactly this file — *"it would
silently discard findings … Fix the input, never the meter"* — and adds *"do not 'fix' this in
`publish_bar.py`"* about the neighbouring temptation. Refusing the convention loses no finding: it
says where a finding must be recorded, on a seat record, where it is counted once.

### `research/autonomy/seat_scratch.py` — FREE path (not in `amendment_guard.GOVERNED`)

New: `seat_record_path`, `open_seat_record`, `close_seat_record`, `open_seat_records`, and CLI flags
`--open-seat-record`, `--close-seat-record`, `--list-open-seat-records`, `--paper/--sha/--lens`,
`--document`, `--document-sha256`, `--findings`, `--seats-dir`. Nothing existing was changed.

- `open` writes the empty, honest `status: "open"` record at the filename `publish_bar` counts as a
  seat, **before** the seat reads anything.
- `close` merges the seat's findings and marks it `complete`. **It refuses when nothing was opened** —
  that refusal *is* the write-first rule, mechanised rather than written down. It also refuses to
  change `reviewed_commit`, `blind`, the lens or `opened_utc`, so a seat cannot relabel which commit
  it read after the fact (`paper-hardening` §3).
- `open` refuses to overwrite a **closed** record: re-opening one would erase a seat's findings with
  an empty shell, which is worse than losing them because the shell looks exactly like a seat that
  found nothing.
- `--list-open-seat-records` is the driver's read before it believes a round.

### Two new test files under `research/autonomy/tests/` — GOVERNED (`**/tests/**`)

Both are net-additive and every assertion is a refusal or a smaller count. Gate 13 runs this
directory on every commit.

---

## What I could not do, and what it is actually waiting on

### ⛔ The half of AUT-PD-193 I did **not** fix, because fixing it would loosen the bar

`_look_history` has the same glob defect: it counts each prior round's roll-up as a look. Measured:

```
_look_history("PUB-ASO"):  7a7f408258c8 -> 6 (true 5)   b53290b37e71 -> 6 (true 5)
                           f6cdb93605e3 -> 6 (true 5)   f9e5059912a5 -> 6 (true 5)
                           6127da1ac1a2 -> 5 (true 5)   a9dd5d34ce66 -> 4 (true 4)
```

so `widest = 6` for PUB-ASO. A round fielding five seats and **no** roll-up — the round-27
convention, `PUB-ASO-6127da1ac1a2` — is refused for being narrower than rounds that looked exactly
as hard. **That is a live false refusal and I left it standing.**

**Why:** correcting it lowers `widest` from 6 to 5, so the width check fires **less** often, so
PUB-ASO passes clause 1 more easily. `amendment_guard` forbids a bar being loosened by the cycle it
blocks, this sprint is blocked by this bar on several papers, and the seat contract says so
explicitly. A false refusal costs a round; a false clearance costs a paper published under a real
ORCID.

**What it is actually waiting on — and it is not trimcrae's attention.** Three routes, in the order I
would take them:

1. **Field a sixth seat.** Engineering is free (CLAUDE.md §5). A round that has to clear a
   six-look floor can clear it the honest way. This needs nobody's permission and costs one seat.
2. **A later cycle makes the symmetrical change, declared.** `amendment_guard` refuses the change
   *by the blocked cycle*, not the change. A cycle not blocked by clause 1 may symmetrise the
   comparison with a declared amendment.
3. Only if neither is taken: trimcrae. **I am not escalating it**, per CLAUDE.md §3 — there are
   actions available that resolve it without weakening a bar, so it is not his.

The deliberate asymmetry is documented in the code at the check itself, so the next reader finds the
reasoning where the oddity is, not in this file.

### ⚠ Sprint-wide: a red pytest run may not be yours, and I hit the OTHER case

The coordinator's standing warning tonight is that `tracked_tree_guard.assert_tree_unchanged` raises
in `pytest_sessionfinish` when a *different* seat edits the tree mid-run, and that it **swallows the
real failure list** while doing so — so a red report names a modified file and shows nothing about
what actually failed.

**I hit the opposite case and it is worth recording as the discriminator.** My run of
`systems/tests/test_autonomy_publish_bar.py` went red at
`test_all_six_clauses_passing_is_what_it_takes` with a named assertion at a named line and no mention
of `assert_tree_unchanged`, on a fixture entirely inside `tmp_path`. **That is a real failure and it
was mine** — §1a. The rule that separated the two was not a re-run: it was reading *what the failure
named*. A guard-induced red names a path; a real red names an assertion.

⚠ The related fact, which the AUT-PD-174 row already carries one instance of: **tonight's wall clock
is CPU contention, and that is measured rather than assumed.** `systems/tests/test_autonomy_publish_bar.py`
+ `test_convergence…` — 40 pure-logic tests, no network, no GPU — took **249 s** and **254 s** on two
separate runs, against **0.13 s** for the five-test convergence file alone and **0.31 s** for my own
17 tests. `ps` at 19:10Z showed **eight or more concurrent pytest processes** from sibling seats
(including one `pytest -n 4 --dist loadfile` fan-out) and `uptime` reported **load average 12.20**,
with no `.git/index.lock` present. So the cost is the box, not a lock and not a hang.
★ **The operational consequence for the rest of the sprint: scope every run to the files covering
your change.** A wide run is not more careful tonight, it is four minutes of somebody else's CPU —
and it is also the run most likely to collide with the tree guard and come back red for a reason
that is not yours.

### Paths I needed and do not own

- **`research/autonomy/record_bar_evidence.py`, `record_hardening()` (line ~154)** is the *same
  defect twice over*, and it is the more consequential half: it carries the identical glob
  (`SEATS_DIR.glob(f"{paper}-{sha}*.json")`) **and** the identical union
  (`blockers = [item for seat in seats for item in (seat.get("blockers") or [])]`). It is the tool
  that GENERATES the `hardening-state/<PUB>.json` record clause 1 then reads — its own `_role` says
  the file is *"GENERATED … never hand-written"* — so the doubled tally is written into the record
  before the bar ever sees it, and an OPEN record would be listed in that record's `seats`.
  **One-of-a-pair (`paper-hardening` §6): I fixed one site of a two-site defect and cannot reach the
  other.** ⚠ The two are now *consistent* — both refuse round 26's shape — so nothing is
  silently wrong today; but the generator will keep producing records the bar refuses, and the
  refusal will name the roll-up rather than the generator. Not mine this sprint.
- **`_look_history`'s prefix glob is `f"{pub_id}-*.json"`**, which for a publication id that is a
  prefix of another (`PUB-FUSION` vs `PUB-FUSION-PARTNER`) would count the longer paper's seats as
  the shorter one's. No such pair exists in `systems/graph/publications.json` today, so this is a
  latent defect, not a live one. Recorded rather than fixed: the fix is in `_look_history`, whose
  direction I have already argued is not this cycle's to move.
- **`.claude/skills/research-loop/SKILL.md`** — the cycle-contract prose for AUT-PROP-006. Exact
  wording below.
- **`research/autonomy/research-ledger.json`** — proposed rows below.
- **`research/autonomy/amendments.jsonl`** — record below.

### The four committed roll-ups that carry populated tallies

`PUB-ASO-7a7f408258c8`, `PUB-ATR-c1bc934fec3c`, `PUB-FUSION-PARTNER-21bc8578b11a`,
`PUB-FUSION-PARTNER-34264bbeb610` will now be refused by change #4 if their commit is ever the one
being posted. **I did not touch them** — they are evidence records, and rewriting evidence to fit a
count is the one thing this seat must not do. The correct repair is a *new* record at a *new* round,
following the round-20 convention; it is not a retrospective edit. Only PUB-ATR's is at a declaring
commit, and that paper already fails on seven blockers.

---

## Prose change for `.claude/skills/research-loop/SKILL.md` (driver applies — I do not own it)

In **§2 · THE CYCLE CONTRACT**, insert as a new bullet under step **6 · Do the work**:

> ⭐⭐ **A BLIND SEAT WRITES ITS RECORD AS ITS FIRST ACT, NOT ITS LAST (AUT-PROP-006).** Before the
> seat reads a line of the paper it runs
> `python3 research/autonomy/seat_scratch.py --open-seat-record --paper <PUB> --sha <PIN> --lens <lens>`,
> which writes an empty `status: open` record to `research/autonomy/review-seats/`. When it reports,
> it closes that record with `--close-seat-record … --findings <file>`; **`close` refuses if nothing
> was opened**, so the order is a mechanism rather than an instruction.
> ⚠ *Measured: CYC-0005 ran two blind seats, ACTED ON BOTH and PERSISTED NEITHER — the manuscript
> carries their fixes and `publish_bar`'s convergence clause has nothing to read. The failure is
> one-directional, which is why it is worth a step: the CHANGE survives a context loss and the
> EVIDENCE FOR IT DOES NOT.*
> ⛔ **AN OPEN RECORD REFUSES THE ROUND, AND THAT IS WHAT MAKES WRITING IT FIRST SAFE.** An open
> record is honestly blind and honestly names its commit, so `_seat_records` admits it — a seat that
> DIED would otherwise be counted as a look that found nothing, and it would be the look that made
> the round appear widest. `clause_1_hardening_converged` therefore fails on any record still open at
> the pinned commit. **The driver's read before it believes a round is
> `--list-open-seat-records --paper <PUB> --sha <PIN>`**; `paper-hardening` §7d — six killed seats
> were reported as "running" in three separate status boards, because a seat that died leaves a board
> that looks exactly like a seat that is thinking.
> ⛔ **AND THE ROUND'S ROLL-UP CARRIES NO TALLIES OF ITS OWN (AUT-PD-193).** Findings live on the
> seat records, where the bar counts each of them exactly once; the roll-up carries the narrative,
> the blindness statement and the round number, with `blockers: []` and `p1s: []`. A roll-up carrying
> the union of its seats' findings is refused by clause 1.

---

## Amendment record for the driver

⛔ I did **not** append to `amendments.jsonl` — it is a governed path this seat does not own, and a
concurrent append collides. Paste this line (one JSON object, one line):

```json
{"cycle_id": "SPRINT-2026-09-01/S9-SEATRECORD", "utc": "2026-09-01T19:20:00Z", "path": "research/autonomy/publish_bar.py", "what_changed": "AUT-PD-193 + AUT-PROP-006. Added `_is_seat_file`, which separates a round's roll-up (`{pub}-{sha}.json`) from an independent seat (`{pub}-{sha}-seat-*.json`) on the filename, because the record keys do not discriminate (roll-ups carry a `seat` key; PUB-ATR seat files carry `lens`). The seat set at a pin is now the `-seat-*` records, FALLING BACK to every blind record when there are none — because `clause_6_independent_adversarial_seat` reads `{pub}-{sha}.json` directly, so a lone bare record IS the round's seat (PUB-FUSION-PARTNER-21bc8578b11a carries 4 blockers and 9 P1s with no seat sibling). Two refusals added to clause_1_hardening_converged: (a) any record at the pin with `status: \"open\"`; (b) a roll-up carrying its own `blockers`/`p1s`, conditioned on `-seat-*` records existing beside it. The width floor now counts the declaring round in seats rather than blind records. The passing evidence line prints the seat count.", "old_value": "`_seat_records` globbed `{pub}-{sha}*.json`, which matches the roll-up with `*` empty, so the roll-up was returned as a sixth seat and its tallies were summed with the seats'. Measured on the committed records: PUB-ASO-7a7f408258c8 counted 2 blockers / 10 P1s against a true 1 / 5. On fixtures against the pre-change module: a round filing ONLY a roll-up returned PASS; a five-seat round cleared a six-seat width floor; and a round whose honest record declared 5 P1s was refused with 'record under-reports its own seats: it declares 0 blocker(s) and 5 P1(s), the seats record 0 and 10'.", "new_value": "Two added refusals and a smaller-or-equal declaring-round count. 17 new tests across two files (12 failing against the pre-change modules; the 4 that pass are positive controls and 1 skips for want of the review-seats directory in the clone). 11 single-site mutations, 11 caught, 0 survived, each asserted landed and run against a clone. The existing suites over this clause are green: systems/tests/test_autonomy_publish_bar.py (35) and test_convergence_is_a_repeated_look_not_a_single_test.py (5). Clause 1's verdict is unchanged for all three papers at their declaring commits (PUB-ASO, PUB-ATR, PUB-FUSION-PARTNER: FAIL before, FAIL after).", "why": "AUT-PD-193 and AUT-PROP-006. `independent_adversarial_seat` and `hardening_converged` are the instrument the 2026-09-01 sprint's blind seats are measured with, so it was checked before it was used.", "self_serving_check": "ANSWERED: NO, and the direction is stated per change. Every change is an ADDED REFUSAL or a SMALLER-OR-EQUAL count on the declaring side; not one removes a refusal or raises a number the bar compares against. \u26a0 The first version WAS stricter than it should have been and red on true input \u2014 it excluded the bare `{pub}-{sha}.json` unconditionally, which refuses a round whose only record is its seat and discards that round's findings. It was caught by the positive control in systems/tests/test_autonomy_publish_bar.py and is now conditioned on `-seat-*` records existing beside the bare one; that correction is a relaxation of MY OWN unshipped over-strictness back to the pre-existing behaviour, not a loosening of the bar as it stood. No paper's clause-1 verdict moved (all three FAIL before and after). ⛔ THE LOOSENING WAS IDENTIFIED AND DELIBERATELY NOT MADE: `_look_history` has the same glob defect and inflates `widest` to 6 for PUB-ASO, which falsely refuses a five-seat round that filed no roll-up (PUB-ASO-6127da1ac1a2). Correcting it lowers `widest` and makes PUB-ASO pass more easily, so this cycle — one the bar is blocking — may not make it. It is documented at the check itself, and the honest remedies available without touching the bar are named in the seat's findings file: field a sixth seat, or let an unblocked cycle symmetrise it with a declared amendment. ⚠ ALSO REFUSED: subtracting the roll-up from the tally sum, which is the obvious fix and is a loosening — a roll-up is a synthesis and can grade a blocker no single seat filed, so subtracting it would silently discard findings (`paper-hardening` §8.0a: fix the input, never the meter). The refusal loses no finding; it says where the finding must be recorded."}
```

A second line for the test files, if the driver prefers one record per governed path:

```json
{"cycle_id": "SPRINT-2026-09-01/S9-SEATRECORD", "utc": "2026-09-01T19:20:00Z", "path": "research/autonomy/tests/test_a_round_rollup_is_not_a_sixth_seat.py + research/autonomy/tests/test_a_seat_writes_its_record_before_it_looks.py", "what_changed": "Two new test files, 17 tests, covering AUT-PD-193 and AUT-PROP-006. Each carries a positive control first; each covers a round WITH a roll-up and a round WITHOUT one; one asserts `_is_seat_file` against the real committed records rather than only fixtures, so the predicate cannot be right on fixtures and wrong on evidence.", "old_value": "No test named a roll-up, and none named an unfinished seat record. `_seat_records`'s glob had no coverage of what it returns beyond the blind/commit filters.", "new_value": "17 tests. 12 fail against the pre-change modules; 4 pass (the positive controls) and 1 skips for want of the review-seats directory in the clone. 11/11 mutations caught.", "why": "AUT-PD-193, AUT-PROP-006.", "self_serving_check": "ANSWERED: NO. Net +16 tests, zero removed, zero weakened. Every assertion is a refusal the bar did not previously make or a count smaller than the one it previously used."}
```

---

## Ledger rows the driver should write

I may not edit `research-ledger.json` (charter §2).

| proposed | `kind` | `state` | `what` |
|---|---|---|---|
| **AUT-PD-193** (existing) | `process_defect` | `done` | Fixed for the tally and the declaring round's width; the `_look_history` half is deliberately left open and is re-filed below. Evidence: `research/autonomy/sprint-2026-09-01/S9-SEATRECORD.md`. |
| **AUT-PROP-006** (existing) | `process` | `done` | Implemented in `seat_scratch.py` (`--open-seat-record` / `--close-seat-record` / `--list-open-seat-records`) with the clause-1 refusal that makes it safe. ⛔ The skill prose is NOT yet applied — the driver applies the block in this file's "Prose change" section, and the row is not `done` until it is. |
| **new** | `process_defect` | `queued` | ⛔ `publish_bar._look_history` counts a round's roll-up as a look, so `widest` reads 6 for PUB-ASO where four earlier rounds fielded five seats each. A five-seat round filing no roll-up (`PUB-ASO-6127da1ac1a2`) is refused for being narrower than rounds that looked exactly as hard. **This is a LOOSENING to fix and may not be made by a cycle clause 1 is blocking** (`amendment_guard`); it needs an unblocked cycle and a declared amendment, or the round clears the old bound honestly by fielding a sixth seat. Direction and evidence: `research/autonomy/sprint-2026-09-01/S9-SEATRECORD.md`. |
| **new** | `process_defect` | `queued` | ⛔ `record_bar_evidence.py::record_hardening` carries the SAME glob AND the SAME tally union as the ones fixed in `publish_bar` — it is the tool that GENERATES the hardening-state record clause 1 reads, so a doubled tally is written before the bar sees it, and an open seat record would be listed among its `seats`. One-of-a-pair (`paper-hardening` §6): one site fixed, the sibling not reached. Free, CPU-only. The two are consistent today (both refuse), so this costs a confusing refusal rather than a wrong verdict. |
| **new** | `process_defect` | `queued` | Four committed roll-ups carry populated tallies against the round-20 convention and will now be refused by clause 1 if their commit is ever posted: `PUB-ASO-7a7f408258c8`, `PUB-ATR-c1bc934fec3c`, `PUB-FUSION-PARTNER-21bc8578b11a`, `PUB-FUSION-PARTNER-34264bbeb610`. ⛔ NOT a retrospective edit — those are evidence records. The repair is a new record at a new round following the round-20 convention. Only PUB-ATR's is at a declaring commit, and that paper already fails on seven blockers. |
| **new** | `process_defect` | `queued` | Latent: `_look_history` globs `f"{pub_id}-*.json"`, so a publication id that is a prefix of another (`PUB-FUSION` / `PUB-FUSION-PARTNER`) would count the longer paper's seats as the shorter one's. No such pair exists in `systems/graph/publications.json` today — recorded as latent, not live, and its fix lives in the same function as the loosening above. |
