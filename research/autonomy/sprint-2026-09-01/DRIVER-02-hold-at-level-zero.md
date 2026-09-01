---
id: DOC-SPRINT-DRIVER-02-HOLD-AT-LEVEL-ZERO
title: "DRIVER 02 hold at level zero"
level: L3
kind: incident
status: live
purpose: "A finding made by the sprint driver rather than by a seat — what was measured, the observation that discriminated, and what was handed on."
scope: "One finding, with the commands that produced it. It records what was handed to a seat; it is not that seat's report."
audience: [autonomous research agents, maintainers]
date: 2026-09-01
last_verified: 2026-09-01
---

# DRIVER-02 — an active budget hold was never consulted at backoff level 0

**Found:** 2026-09-01 ~23:30Z, by walking into it. S8-HANDOFF reported nine red tests in
`research/autonomy/tests/test_a_cadence_nobody_enforces_is_not_a_cadence.py` and said, correctly:
*"the guards are working — they are detecting exactly the loosening the charter authorised. Your
call, and it must not be closed by widening a bound."*

## Verdict

**CONFIRMED, and it is a defect in `health.py`, not in the tests.** Seven of the nine were red
because `c_budget_recovering` returned `NO-BACKOFF` before it ever read the hold. Fixed. Two remain
red and are **left red on purpose** — see below.

## The sequence, because the first two answers were both wrong

1. **First reading — "the guards are catching the sprint's own loosening."** Plausible, and what S8
   reported. If true, the honest response is to leave them red and say so.
2. **Second reading — "the state is wrong: a sprint is a governed posture, not the absence of one."**
   The driver had written `budget_hold.active: false`, which says the loop is ungoverned tonight. It
   is not: trimcrae authorised a specific, bounded, expiring posture, and `declared_posture` carries
   its four numbers. So the hold was set **active with a raised ceiling** — a hold that pins a
   ceiling rather than a floor, which is a shape this row had never been given.
   ⛔ **That was the right correction to the state and it fixed nothing: still 9 red.**
3. **The actual cause, read out of the code rather than inferred.** `c_budget_recovering`:

   ```python
   if level == 0:
       return _green(key, label, source, "NO-BACKOFF", ...)   # ← before the hold is read
   ```

   The hold is consulted fifty lines further down, under a comment that says
   **"⛔ THE HOLD MUST GOVERN THE DIALS, OR IT IS DECORATION."** At `backoff_level: 0` it was
   decoration, by construction, in the one row written to catch exactly that.

## What that means, stated plainly

A hold whose `declared_posture` the live dials **openly violated** went completely unnoticed
whenever `backoff_level` happened to be 0. The row that exists to answer *"is the governor honouring
its own hold?"* answered *"no backoff"* and stopped looking. ⚠ This is the third instance tonight of
the same family — a check that appears to measure and does not — after the depth-1 deposit guard
(DRIVER-01) and the mutation harness that scored 0/8 against unmutated code.

## The fix, and its direction

`level == 0` now splits: **no active hold → the same measured green it always was, untouched**;
**an active hold → the posture, floor and review-stamp checks all run.** The row checks MORE, never
less. Nine red tests went to two, because the code now does what those tests had always asserted it
did — which is the evidence that the tests were right and the code was wrong, rather than the other
way round.

⛔ **`health.py` is a GOVERNED path and this session had a motive**, so the direction is stated in
the code, in the amendment record, and here: no test was edited, no bound was widened, no assertion
was weakened. The live dials honour the declared posture on their own merits — cadence 4 h against a
declared ceiling of 4, width 12 against 12, items 6 against 6, cycles 2 against 2.

## The two still red, and why they stay that way

| test | why it fails | why it is not touched |
|---|---|---|
| `test_a_clean_cycle_may_not_decrement_through_the_hold_floor` | sets `backoff_level = floor - 1`. The sprint's floor is **0**, so that is **-1**, which the level validator rejects as unreadable before the floor check runs. | The only fixes are editing the test, or raising `floor_backoff_level` to 1 — which the sprint's own `backoff_level: 0` would then breach. |
| `test_without_a_hold_the_old_stuck_reading_is_unchanged` | pops the hold and expects `STUCK`, which needs a **non-zero** live `backoff_level`. The sprint's authorised posture is 0. | It cannot pass against any honest sprint state. It depends on production being mid-backoff. |

★ **Both are the same defect, and it is a real one worth a row:** the suite builds every fixture
with `copy.deepcopy(live_state())` and mutates one field, so its meaning changes whenever production
posture changes. A test that only holds while the repository happens to be in one posture is a test
that will pass for the wrong reason later.

⛔ **AND THIS CYCLE MAY NOT BE THE ONE THAT FIXES IT.** `research/autonomy/tests/**` is governed,
these two are red *because of an edit this session made*, and this session would like a green build.
That is the exact shape `amendment_guard.py` refuses — *a bar may not be changed by the cycle that
the bar just blocked* — and it does not stop being that shape because the change would also be a
genuine improvement. **A later cycle may make the identical change, declared.** The row is filed.

## Ledger rows the driver should write

- **`process_defect`, queued** — "⛔ `test_a_cadence_nobody_enforces_is_not_a_cadence.py` BUILDS EVERY
  FIXTURE FROM THE LIVE `autonomy-state.json`, so its meaning changes with production posture.
  Measured 2026-09-01: a legitimate, authorised, recorded posture change (`backoff_level: 0` under a
  ceiling-shaped hold) turned 9 of its 20 tests red; 7 were a real `health.py` defect and 2 are the
  coupling itself. Each should construct the state it is testing. ⛔ NOT takeable by a cycle whose own
  state change made them red."
- **`process_defect`, done** — the `health.py` level-0 fix above, with this file as its evidence.
