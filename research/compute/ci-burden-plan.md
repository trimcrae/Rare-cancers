---
id: DOC-CI-BURDEN-PLAN
title: The CI burden — what it actually is, what was fixed, and the rule that keeps it fixed
level: —
kind: runbook
status: live
canonical_for: [ci-run-rate-measurement, supervision-arming-rule]
purpose: >-
  Measure what the repository's ~185 workflow runs/hour are actually made of, record the root cause of the
  self-sustaining supervision loop found on 2026-08-25, and carry the ordered plan for the rest. Owns the
  standing rule that arming gates a DISPATCH, not only a commit.
scope: >-
  GitHub Actions run rate, workflow triggers and the supervision fan-out. Does NOT own prices
  (research/compute/pricing.md) or the commit-gate tiers (CLAUDE.md section 6 and the repo-gates skill).
audience: [maintainers, autonomous research agents]
date: 2026-08-25
last_verified: 2026-08-25
---

# The CI burden — what it actually is, what was fixed, and the rule that keeps it fixed

**Measured 2026-08-25.** Trigger: *"this repo is groaning under the weight of unnecessary CI jobs that run
constantly, take several minutes, and block progress."* This file is the measurement and the ordered plan.
Prices live in [pricing.md](./pricing.md); commit-gate rules live in `repo-gates`. Nothing here restates either.

---

## 0 · THE HEADLINE, AND WHY THE OBVIOUS SUSPECT WAS INNOCENT

**The burden is not the test suite. It is a supervision fleet re-dispatching itself over an empty account.**

| reading | value | how measured |
|---|---|---|
| workflow files | 173 | `ls .github/workflows` |
| lifetime workflow runs | **40,000** | Actions API `total_count`, all runs |
| repo-wide run rate | **~185 runs/hour** | 30 runs over a 9.4-min window; spot reading, see §1 |
| `tests.yml` share of that | **2.3 runs/hour** | 60 runs / 26.0 h |
| Vast instances being supervised | **0** | `ternary-vast-account-census.json`, `n_instances: 0` |

⛔ **`tests.yml` IS NOT THE PROBLEM AND MUST NOT BE "OPTIMISED".** It is 60 runs in 26 h at a median of
**621 s** (p90 835 s, max 1293 s) and it is already the most carefully tuned workflow in the repo: two
independent jobs since 2026-08-24, `-n 4 --dist loadfile` for a measured 1.94x, `cancel-in-progress` off
`main` only. Its critical path is the suite, and CLAUDE.md §6 records the measurement that refused to scope
it (a validated selector still left a 132.5 s floor of 176.1 s). **Every further "saving" available here is
either negligible or buys back a guard.** Two were examined and REFUSED on evidence — see §4.

---

## 1 · THE MEASUREMENT

Per-workflow rates from `run_number` deltas over multi-hour windows (2026-08-25, ET evening):

| workflow | runs | window | **runs/hour** | nominal cron | conclusion of last 30 |
|---|---:|---:|---:|---|---|
| `gpu-ternary-fep-vast` | 30 | 49.3 min | **35.3** | `17 * * * *` (1/h) | heavily red |
| `lane-staleness-watch` | 30 | 114.7 min | **15.2** | `23 * * * *` (1/h) | ~27 % `cancelled` |
| `account-orphan-alarm` | 30 | 139.3 min | **12.5** | `41 * * * *` (1/h) | green |
| `step1-fanout-autoscale` | 30 | 158.7 min | **11.0** | `*/20` (3/h) | **30 of 30 FAILED** |
| **subtotal, 4 of ~14 crons** | | | **73.9** | | |

★ **THE CADENCE IS NOT THE CRON, AND THE GAP IS THE FINDING.** Every row above runs 4–35x its nominal
schedule. The excess is `workflow_dispatch` by `github-actions[bot]` — workflows dispatching each other.
Five runs of `gpu-ternary-fep-vast` were created **within 5 seconds** (22728–22732 at 23:00:46–23:00:51).

⚠ **The 185/hour repo-wide figure is a 9.4-minute spot reading, not a sustained measurement.** It
cross-checks to within ~20 % of the multi-hour rows (`gpu-ternary-fep-vast` reads 44.7/h in that window
against 35.3/h sustained), so *"on the order of 150–190/hour"* is the honest statement. **~4,000+ runs/day.**

### What was RULED OUT, with the observation that did it

- **Bot commits re-triggering `tests.yml`.** 64 of 79 commits to `main` in 26 h are cron watchdog commits.
  **None triggered `tests.yml`** — 8 `main` runs, all merges or human work. GitHub's `GITHUB_TOKEN`
  loop-prevention holds. *Hypothesis dead; do not re-raise it.*
- **Stale branch-scoped `push` triggers.** ~30 workflows carry `push:` scoped to feature branches. **All 11
  referenced branches still exist** (239 branches on origin). They are dormant and path-filtered, and they
  cost nothing. *Not the burden.*

---

## 2 · ROOT CAUSE — A SELF-SUSTAINING ALARM LOOP, 19 DAYS OLD

`step1-fanout-autoscale` failed **30 of its last 30 runs**. The mechanism, from the run's own logs:

1. The `tick` job correctly reads the account and reports
   `{"armed": false, "why": "the account holds ZERO instances and the census is fresh — there is nothing to
   supervise, so a heartbeat about it carries no information"}`, so `publish_artifacts.sh` **deliberately
   withholds** the heartbeat commit. This is `fleet_armed.py`, landed 2026-08-06, and it is correct.
2. `_generated_utc` on `step1-fanout-progress.json` therefore stops moving.
3. `fleet_supervision_alarm.py` reads that timestamp — **its only input** — finds it **27,391 min (19 days)**
   stale, and returns `FAILING`: *"the tick ran and measured nothing… The tick's CODE is broken."*
4. The alarm exits non-zero, **emails trimcrae**, and six `needs: tick` + `if: always()` jobs re-dispatch the
   supervision chain regardless. Five of those six do nothing but dispatch another workflow.

⛔ **THE FILE DOCUMENTS BOTH HALVES OF THE COLLISION WITHOUT NOTICING THEY CONTRADICT.** In
`step1-fanout-autoscale.yml`, two lines apart:

> `# ⚠ NO PUBLISH_IF_CHANGED — THIS IS THE LANE'S HEARTBEAT. The timestamp is the only input to the`
> `# supervision alarm's staleness verdict… a tick whose artifacts were all absent published no heartbeat`
> `# at all, and so read as a tick that never ran.`
> `# ⛔ HEARTBEAT, NOT A RESULT — publishes only while there is something to supervise (trimcrae 2026-08-06…)`

The idle-suppression re-armed the exact landmine the comment above it was written to disarm.

★ **THE DISCRIMINATING OBSERVATION.** The frozen artifact is stamped **2026-08-06T22:31:27Z** — the day
idle-suppression landed. Not a coincidence to be argued about: the cause is dated.

⛔ **The alarm was not reporting an outage. It WAS the outage.** ~11 red runs/hour, each emailing, each
re-dispatching, for 19 days, over a fleet of zero — against trimcrae's 2026-07-31 *"You're emailing me way
too much."*

### Why it survived

`fleet_armed.py` gates **whether a lane COMMITS a non-event**. Nine workflows and `publish_artifacts.sh`
consult it. **`fleet_supervision_alarm.py` — the one module that judges whether the tick is broken — never
did**, and neither did the `if: always()` fan-out. Arming reached the *publish* decision and never reached
the *dispatch* decision.

---

## 3 · WHAT WAS FIXED (this commit)

Both changes are **fail-armed**: they can only take effect on a *fresh account-level reading of zero hosts*,
and reproduce today's behaviour exactly under any doubt. Neither gates the tick, the work, or any teardown.

1. **`fleet_supervision_alarm.py`** now asks `fleet_armed.state()` before drawing a staleness verdict and
   returns a new `QUIET-NOTHING-TO-SUPERVISE` (ok) when there is nothing to supervise. An unreadable or
   missing `fleet_armed` leaves `armed=None` and the module behaves as before.
2. **`step1-fanout-autoscale.yml`** publishes the arming state as a `tick` job output, and the **five
   dispatcher jobs** (`cross-lane-staleness-watch`, `resurrect-supervisor`, `resurrect-lane-watch`,
   `account-orphan-alarm`, `account-reaper`) now carry
   `if: ${{ always() && needs.tick.outputs.armed != 'false' }}`.
   `supervision-alarm` is deliberately **left ungated** so the lane still reports every tick.

⚠ **`!= 'false'`, NEVER `== 'true'`** — a missing, empty or unexpected output re-dispatches as it does today.

### Verification actually run (not asserted)

- On the real frozen artifact + real census: `STALE-CAUSE-UNKNOWN`/red → `QUIET-NOTHING-TO-SUPERVISE`/green.
- **Mutation-tested**, six single-site mutations of the census, each of which must revert to armed:
  a host appears · census 5 days stale · `n_instances` absent · `utc` absent · `n_instances` not an int ·
  `fleet_armed` import fails. **All six returned armed / not-ok.** The gate opens only on a fresh zero.
- The `armed` shell step was proven under `bash -e` at exits 10 / 0 / 1 / 127 → `false / true / true / true`.
  ⛔ Its first draft used `cmd; rc=$?`, which under GitHub's `bash -e` aborts before `$?` is read. It would
  have failed *safe* and *silent* — which is how it would have survived. Use `rc=0; cmd || rc=$?`.

### Proven in CI — run 32910036091, dispatched on this branch

`step1-fanout-autoscale` dispatched with `ref=claude/ci-job-optimization-9l1kac`. **All five dispatcher jobs
reported `conclusion: skipped`** — `resurrect-supervisor`, `account-reaper`, `cross-lane-staleness-watch`,
`account-orphan-alarm`, `resurrect-lane-watch` — while `supervision-alarm` still ran, as designed.
**Five downstream dispatches per tick became zero, on a real runner.**

⛔ **AND THE ALARM HALF IS STRUCTURALLY UNTESTABLE FROM A BRANCH — A FINDING, NOT A FAULT.** In the same run
`supervision-alarm` still went red, and the cause is one line in its own job:

```yaml
      - uses: actions/checkout@v4
        with:
          ref: ${{ github.event.inputs.fleet_branch || 'main' }}
```

**That job hard-checks-out `main` and therefore ran `main`'s unpatched `fleet_supervision_alarm.py`.** The
five job-level `if:` conditions were honoured because GitHub evaluates those from the *dispatched ref's*
workflow file; the Python did not, because the job fetches its own source from elsewhere. This is the same
ref-confusion the tick already shouts a `::notice::` about. So the alarm half rests on the local evidence
above (89 existing tests green, six mutations, real artifact red→green) **and lands only on merge.**

⛔ **NOTHING IN §3 IS IN EFFECT YET. The crons run from `main`; this work is on a feature branch.** Merging is
trimcrae's call — the session that produced this was scoped to its own branch and must not push to `main`.

**Expected effect once merged: the ~74 runs/hour in §1 collapse toward the crons' nominal rate while the
account is empty, and restore in full the moment a host is rented.** ⚠ Still a prediction — re-read the
rates 24 h after the merge and record them here.

---

## 4 · EXAMINED AND DELIBERATELY NOT CHANGED

⛔ **Both were candidate savings that the evidence refused. Do not re-propose them without new data.**

- **Dropping `pull_request:` from `tests.yml`** to kill duplicate runs. 13 PR runs in the sample, but only 7
  had a `push` sibling — **6 had none**, because `pull_request` builds the *merge commit*, a SHA that is
  never pushed. Dropping it loses CI on the merge result. The 7 true duplicates run in parallel on a public
  repo where minutes are free, so they cost **almost no wall clock**. Not worth the coverage.
- **`pip` caching in `tests.yml`.** Install is 20–23 s in each of two *parallel* jobs, against a 621 s
  critical path — **~3 %**, for a new moving part and a cache-key to keep correct. Not worth it.

---

## 5 · THE STANDING RULE

> ★★ **ARMING GATES THE DISPATCH, NOT ONLY THE COMMIT.** A supervision lane may run on its cron. It may not
> *dispatch another workflow* while `fleet_armed` says there is nothing to supervise. Proof-of-life for a
> watchman guarding nothing is worth nothing — and a watchman that wakes four more watchmen is how 14 crons
> became ~185 runs/hour.

⛔ **AND A RED SUPERVISION LANE IS A CLAIM ABOUT THE FLEET, NOT FURNITURE.** 30 consecutive red runs naming a
false cause is worse than no alarm: it is alarm fatigue with a plausible story attached. **If a supervision
workflow is red, either the fleet is in trouble or the alarm is — and both are work, today.**

---

## 6 · THE REST OF THE PLAN, ORDERED

Each row states its own evidence gate. **Nothing below is done; §3 is what is done.**

| # | action | why now | cost | risk |
|---|---|---|---|---|
| 1 | **Re-measure the four rates in §1 after 24 h** and write them into this file | §3's effect is a prediction, and CLAUDE.md §4 forbids leaving it one | $0, one API read | none |
| 2 | Apply the §5 rule to the remaining REAL dispatchers: `account-orphan-alarm` (already verdict-gated), `vast-watchdog`, `gpu-ternary-fep-gcp` | same defect, same fix, three more files | $0 | low — same fail-armed pattern |
| 3 | **`step1-fanout-supervisor.yml` — 13 dispatches, NO cron, NO `fleet_armed` reference.** The largest dispatcher in the repo and the least gated | it is the loop `resurrect-supervisor` starts; §3 holds its *start*, not its *body* | $0 | **medium — read it before touching it**; it owns fleet cadence |
| 4 | `gpu-ternary-fep-vast` at **35.3 runs/h** against a 1/h cron, 7 dispatches, 18 `fleet_armed` refs | already the most arming-aware file, yet the fastest-firing — the refs gate commits, not dispatches | $0 | medium |
| 5 | Audit the four `*/15` and one `*/10` crons (`vast-watchdog`, `ternary-vast-watchdog`, `ternary-leg-watchdog`, `fep-monitor-cron`, `gpu-fanout-rep-gcp`) for an arming gate | 5 workflows × 4–6/h is a floor that never drops while idle | $0 | low |
| 6 | **The tick's step 11 (`congeneric_fanout_vast.py`) is still red** — a SEPARATE cause this change does not touch | §3 stops the red PROPAGATING, it does not make the tick green; a permanently-red lane still violates §5's second rule | $0 to diagnose | low |
| 7 | Decide the retention question: **40,000 runs** makes the Actions UI and the API unusable for diagnosis | every reading in §1 needed `run_number` arithmetic because listing is unusable | $0 | **trimcrae's call — deleting run history is irreversible** |

⚠ **CORRECTION to the §1 dispatch census, made while scoping row 2.** `lane-staleness-watch` was counted as a
dispatcher on a `grep` hit. It is **not** one: line 281 is a `print(f"gh workflow run …")` inside a Python
heredoc — it *recommends* a command to a human, it does not issue one. Its **15.2 runs/hour are entirely
inbound**, from `step1-fanout-autoscale`'s `cross-lane-staleness-watch` job — which §3 has now gated. So that
row is expected to fall out with the §3 fix and needs no edit of its own. **A `grep` for `gh workflow run`
counts strings, not dispatches; read the line before believing the count.**

⛔ **Row 7 is the only one that is not self-doable** (CLAUDE.md §2: irreversible). Rows 1–6 are $0 and ready.

---

## 6b · SECOND PASS — EXECUTED 2026-08-25, on trimcrae's instruction

★ **THE STEER THAT CHANGED THE DESIGN** (trimcrae, 2026-08-25): *"we haven't used vast in a month and don't
need to be driving things on it at all, let alone every two minutes."*

⭐ **CORROBORATED, AND THE NUMBER IS BETTER THAN THE CLAIM.** The clone was SHALLOW (81 commits), which made a
first scan meaningless; after `git fetch --deepen=3000` there are **886 account-census commits reachable,
back to 2026-08-05, and NOT ONE carries a non-zero `n_instances`.** 20 days of continuous zero. The history
does not reach a full month, so *"a month"* is the operator's reading and *"≥ 20 days"* is the repo's.
⚠ **A shallow clone silently truncates every `git log` measurement** — check `git rev-parse
--is-shallow-repository` before quoting one. It nearly cost this file a fabricated figure.

### Done

| what | file | effect |
|---|---|---|
| Arming gate on the redundant fan-out dispatch | `vast-watchdog.yml` | its own header calls the dispatch *"redundancy, not a repair"*; it no longer re-dispatches the autoscale tick over an empty account |
| Cadence cut, `*/15` → hourly | `vast-watchdog`, `ternary-vast-watchdog`, `ternary-leg-watchdog`, `fep-monitor-cron` | 4/h → 1/h each, on **distinct minutes** (8, 14, 26, 32) so they do not thunder together |
| Cadence cut, `*/20` → hourly | `step1-fanout-autoscale` | 3/h → 1/h (minute 38) |
| Cadence cut, `*/10` → hourly | `gpu-fanout-rep-gcp` | 6/h → 1/h (minute 44) — and this lane is on a recorded **operator hold**, so it was polling 6×/h to re-read its own pause |

⛔ **CADENCE CUT, NOT DISABLED, AND THAT IS DELIBERATE.** An hourly watchdog is still a watchdog; a disabled
one is not. The launch lanes were checked and **do NOT dispatch their watchdogs** — the `grep` hits that
suggested they did are COMMENTS referencing the watchdog, not `gh workflow run` calls. So the cron is the
only thing that would notice a host, and it keeps firing.

### Refused in this pass — and this one matters

⛔ **DO NOT PUT AN ARMING GATE ON `gpu-ternary-fep-vast`'S SEVEN DISPATCHES.** It is the fastest-firing
workflow in the repo (35.3 runs/h) and the obvious next target, and gating it would be **wrong**: those
dispatches are **market gates that exist to BUY** — *"price the legs and self-dispatch the launch the moment
the board clears."* `fleet_armed` answers *"is there anything to SUPERVISE?"*, and on an empty account it
says no. Gating a buyer on a supervision predicate would mean the lane could never place a host again.
★ **The rule in §5 governs supervision fan-out. A market gate is not supervision.** Its 18 existing
`fleet_armed` references correctly gate *commits*, not dispatches, and should stay that way.

### Row 6 diagnosed — the still-red tick is NOT a bug

`congeneric_fanout_vast.py` exits 2 from exactly one place:

```python
if price_blocks_every_unit and held_h >= MARKET_HOLD_ESCALATE_H:   # 6 h
    _lprint("[s1f] ESCALATED — price has been the BINDING constraint for {held_h} h ... trimcrae's call now.")
```

⭐ **The tick is red because the escalated market hold is doing its job.** All 19 step-1 fan-out units have
been unplaceable on price for ~19 days, and the alarm says so, in those words: **"trimcrae's call now."**
⛔ **So this must NOT be "fixed", and silencing it would be the exact failure §5 names.** It is a correct,
unanswered question, and the answer is a program decision, not a patch: **release the fan-out, or stand the
lane down.** Given the steer at the top of this section, standing it down is the likely call — but it is
trimcrae's, and it is now the only Vast item left open.

---

## 7 · THE TEST FOR ANY WORKFLOW THAT SURVIVES

A workflow earns its wall clock only if it can answer all four. **A row that fails any one is a candidate for
deletion, not for tuning.**

1. **Who reads its output, and when did they last act on it?** (`tests.yml`: every commit. A supervision lane
   over an empty account: nobody, for 19 days.)
2. **Can it fire when there is nothing to observe?** If yes it needs an arming gate — §5.
3. **Does it dispatch anything?** If yes, its true cost is its own runs times its fan-out, not its own runs.
4. **What does its red mean?** If red is routine, it is not a gate — it is noise wearing a gate's costume.
