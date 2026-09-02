---
id: DOC-SPRINT-S47-RED-GPU-LANES
title: "S47-RED-GPU-LANES — $0 is at risk; the twelve reds are two defects, neither introduced by cfdc0a58b, and one of them is a `set -e` bug that has silently stopped every ternary launch since 2026-08-06"
level: L3
kind: memo
status: live
date: 2026-09-02
audience: [autonomous research agents, maintainers]
purpose: >
  Establish, from the run logs rather than the run summaries, (1) whether any of the twelve red runs on
  cfdc0a58b left a GPU billing, and (2) whether the merge caused the red. Names the mechanism behind the
  same-workflow green/red split, fixes the half that is a code defect, and hands the driver the half that
  is a decision.
scope: >
  The 29 workflow runs whose head_sha is cfdc0a58b7d872e1f1b12eed5f615d92bee9428a, plus the three earlier
  dispatch waves on e0834faf4 and 4f54ac80b used as the control. Reads Vast account state from the
  committed account-level census and the merged in-flight board. Touches one workflow file, adds one
  guard test, and this memo. No git write command was run; no workflow was dispatched, re-run or cancelled.
last_verified: 2026-09-02
---

# S47 — the twelve red GPU lanes on `cfdc0a58b`

**Item:** `AUT-S47-e71cf460` · **`origin/main` read this session:** `cfdc0a58b7d872e1f1b12eed5f615d92bee9428a`
(local `HEAD` at `b4cf28c6b`, a sibling seat's tree). **Owned paths:** this memo,
`.github/workflows/gpu-ternary-fep-vast.yml`,
`research/modalities/tests/test_a_workflow_never_reads_dollar_question_after_a_bare_semicolon.py`.
**No git write command was run.** **Started/Finished (UTC):** 2026-09-02T08:33Z / 2026-09-02T08:41Z.

## ★ MONEY AT RISK: $0. NOTHING IS RENTED, ON EITHER PROVIDER.

The account-level census — `GET /instances/`, which is the account view a per-mode board structurally
cannot give — was taken **inside the last failing wave** and reads:

```json
{ "utc": "2026-09-02T08:28:14Z", "n_instances": 0, "instances": [] }
```
`research/modalities/ternary-vast-account-census.json` @ `origin/main`

Corroborated independently by `fleet_armed.py` inside the STEP-1 tick's own log
(`"n_instances": 0, "age_s": 2001, "census_utc": "2026-09-02T07:55:18Z"`), and by
`research/modalities/inflight-board-all.md`, whose every lane reads `NO HOST`:
ternary `IN-FLIGHT BOARD: no GPU legs.`, STEP-1 `0 of 19 unit(s) landed`, NR-V04 `0 of 16 … HELD`.

⛔ **And the direction of the ternary defect is the opposite of the dangerous one: it PREVENTS spend.**
Every one of the three red ternary jobs died *before* its `gh workflow run` line. Nothing was rented
because nothing was ever dispatched. **This is not a reason to relax — see FINDING 3, which is the
$22.68 the fix releases.**

---

## The per-lane table

Twelve reds, three workflows, one sha. `wave` = one of the three ~8-minute dispatch waves that landed
on this tip (08:11, 08:19, 08:28 UTC).

| workflow (job) | green / red on this sha | failing step | the error line, quoted | rented? | $ at risk |
|---|---|---|---|---|---|
| Ternary FEP — `market_gate` | 0 / 3 | *Price 4 legs, and LAUNCH them the moment the board clears* | `##[error]Process completed with exit code 10.` (after `"outcome": "dispatched"`, `"reason": "board cleared both ceilings; dispatching task=edge-reps"`) | **no** — shell died before `gh workflow run` | **$0** |
| Ternary FEP — `triangle_gate` | 0 / 3 | *Price the triangle, and LAUNCH it the moment the board clears* | `[market-gate] ⛔ HOLD — neither tier clears. bid: over the $/ns drift line (the buy line) at 1.933x basis.` then `##[error]Process completed with exit code 10.` | **no** — and it had already refused to buy | **$0** |
| Ternary FEP — `gate_5aks` | 0 / 3 | *Price RUNG 5a-KS, and LAUNCH it the moment the board clears* | `[market-gate] ✅ CLEAR — bid tier clears at 1.686x basis` then `##[error]Process completed with exit code 10.` | **no** — same abort point | **$0** |
| Ternary FEP — non-gate dispatches (`reps_diag`, $0 forensic) | 5 / 0 | — | — | no | $0 |
| STEP 1 fan-out (`tick`) | 0 / 3 | step 8, *Collect — assemble the map, reconcile realised spend, reap dead hosts* | `##[error][s1f] REFUSING to overwrite step1-fanout-map.json: committed n_complete=18, this tick read n_complete=0.` → `exit code 2` | **no** — a read of S3, no placement attempted | **$0** |
| GCP L4 replicate (`gpu-fanout-rep-gcp`) | 3 / 0 | — | — | **no** — `gcp-s1f-rep-OPERATOR-HOLD.json` is present in the tree, so `feed_decision` returns `action=hold`, and the lane "BUYS NOTHING, whoever dispatches it" | $0 (and free-trial ledger regardless) |
| ENDPOINT-MD control (`selectivity-control-vast`) | 3 / 0 | — | — | no | $0 |
| Fusion CPU extras | 3 / 0 | — | — | no (CPU) | $0 |
| Cross-lane staleness watch | 2 / 0 | — | — | no | $0 |
| `tests (modalities)` | 1 / 0 | — | — | no | $0 |

**Reds: 3 gates x 3 waves = 9 ternary, + 3 STEP-1 ticks = 12.** Two distinct defects, not twelve.
(14 ternary dispatches landed on this sha in all: 9 red gates, 5 green `reps_diag`.)

---

## ⛔ FINDING 1 — THE SAME-NAME GREEN/RED SPLIT IS NOT MATRIX LEGS, NOT RE-RUNS, AND NOT SPOT PREEMPTION. IT IS FOUR SEPARATE DISPATCHES OF ONE WORKFLOW, THREE OF WHICH SHARE A BUG THE FOURTH DOES NOT.

Every one of the 29 runs carries `"event": "workflow_dispatch"` and `"run_attempt": 1`. Nothing here was
re-run, and no run has a matrix. The ternary workflow is dispatched **four or five times within five seconds**, by
`github-actions[bot]`, per wave — `run_number` 25621–25625 on this sha, marching consecutively from
25600 on `e0834faf4`. A poller fires one dispatch per *task*, and the tasks resolve to different jobs:

```
run 33608837680  job_id 100179124261  job_name market_gate     conclusion failure
run 33608840135  job_id 100179144087  job_name triangle_gate   conclusion failure
run 33608842910  job_id 100179159176  job_name gate_5aks       conclusion failure
run 33608834577  job_id 100178997494  job_name reps_diag       conclusion success   <- every gate job SKIPPED
```

★ **The split is exactly the three gate jobs against everything else, and those three are exactly the
three call sites in the file that capture `$?` after a bare `;`.** The green dispatches resolve to
`task=reps-diag`, whose run shows `market_gate`, `triangle_gate` and `gate_5aks` all `skipped` — it
never reaches the offending line. ⚠ Its own step 4, *"FIRST — what does the ACCOUNT hold?"*, is what
wrote the 08:28:14Z census quoted at the top of this memo, which is why the $0 reading is contemporaneous
with the failures rather than after them. ⛔ "Flaky" is refuted by construction: the partition is
deterministic and reproduces on every wave, on four different commits.

---

## ⛔ FINDING 2 — THE MECHANISM IS `set -e` EATING `fleet_armed`'s IDLE CODE, AND IT DEADLOCKS: THE GATE ABORTS PRECISELY WHEN THE ACCOUNT IS EMPTY, WHICH IS WHEN IT MOST NEEDS TO BUY.

The step runs under `set -eo pipefail` and contained, at `gpu-ternary-fep-vast.yml:1214` (and 442, 1063):

```bash
python3 research/modalities/fleet_armed.py 5aks-market > /tmp/armed-5aks-market.json 2>&1; _ARMED=$?
if [ "$_ARMED" -eq 10 ]; then
  echo "[gate] IDLE — nothing to supervise; this snapshot is not committed."
```

`fleet_armed.py` returns **10** for IDLE — the ordinary "the account holds zero instances" case. Under
`-e` that non-zero status aborts the shell **before `_ARMED` is ever assigned**, and the step exits *with*
that status.

★ **THE DISCRIMINATING OBSERVATION, which separates "the `if` ran" from "the shell died at the command":**
the log prints **neither branch**. No `[gate] IDLE`, no `::warning::fleet_armed exited …`, and not the
unconditional `echo "5aks-gate exit=$RC …"` that follows the whole block. One of those three must appear
if `_ARMED` was ever assigned. The last line before `##[error]` is the *preceding* step's ledger JSON.

Reproduced rather than argued, this session:

```
--- BROKEN FORM (as at gpu-ternary-fep-vast.yml:1214) ---
outer rc=10                       <- prints nothing at all, exits 10
=== FIXED FORM ===
[gate] IDLE
5aks-gate exit=0
  fixed-form subshell exit=0
```

⛔ **THE DEADLOCK.** Zero instances → `fleet_armed` returns 10 → the step aborts → the `gh workflow run`
that would have rented four hosts never fires → the account stays at zero instances → next tick, same.
**The gate is broken on exactly the input it exists to handle**, which is why this survived: on any tick
where the fleet was non-empty, `fleet_armed` returned 0 and the step passed.

⚠ **AND IT TURNS A DELIBERATE GREEN STATE RED.** The same file, twelve lines below the abort, says
*"A HOLD IS A NORMAL, GREEN, VISIBLE STATE — never a red build."* `triangle_gate` correctly held on price
at 1.933× basis and still went red, because the abort happens upstream of that `exit 0`.

⚠⚠ **THE RULE WAS ALREADY WRITTEN DOWN, IN A SIBLING WORKFLOW, AND MEASURED BY NOTHING.**
`step1-fanout-autoscale.yml:347` carries it verbatim:

> `# ⚠ `rc=0; cmd || rc=$?` AND NOT `cmd; rc=$?` — GitHub runs this with `bash -e {0}`, so a bare`
> `# non-zero exit aborts the step BEFORE `$?` is ever read, and the output would never be written.`

That step got it right. Two more sites in `gpu-ternary-fep-vast.yml` itself (lines 2150, 2185) also got it
right, with `|| armed_rc=$?`. **Three sites written in one commit got it wrong, next to five siblings that
were correct.** This is the one-of-a-pair defect class, at three-of-eight.

### Introduced 2026-08-06, twenty-seven days before the merge

```
git log -S'2>&1; _ARMED=$?' -- .github/workflows/gpu-ternary-fep-vast.yml
e948f9240 2026-08-06 Gate the last three market snapshots — and leave the in-flight board alone, deliberately
```

★ The commit subject names its own blast radius: the **three** snapshots it gated are the three broken
sites, and the in-flight board it "left alone" is the pair that still works.

**Verdict: OURS-AND-FIXABLE. Fixed this session** — all three sites now `_ARMED=0` + `|| _ARMED=$?`,
matching the sibling's idiom, with its warning copied to each site. YAML re-parses (27 jobs,
`market_gate`/`triangle_gate`/`gate_5aks` all present).

**Guard added:** `research/modalities/tests/test_a_workflow_never_reads_dollar_question_after_a_bare_semicolon.py`
scans every `.github/workflows/*.yml` for a `$?` capture after a bare `;`, skipping comment lines so the
sibling's warning is documentation rather than a violation. **Mutation-tested on a COPY under
`/tmp/.../scratchpad/sprint/mut`, never the live tree (CLAUDE.md §6): 3 mutations introduced, 3 caught** —
reverting one gate, reverting all three, and reverting the correct sibling in the other file, proving the
guard is not scoped to the file it was written for. It carries its own can-it-fail self-test.

---

## ⛔ FINDING 3 — THE FIX RELEASES TWO REAL LAUNCHES, PROJECTED $22.68 COMBINED, ON THE NEXT ~8-MINUTE TICK. THE DRIVER MUST KNOW THIS BEFORE COMMITTING IT.

Both cleared gates had already decided to buy and were stopped only by the abort. Their own logged numbers:

| gate | verdict | `mean_usd_per_ns` | `ratio_vs_basis` | `projected_usd` | would dispatch |
|---|---|---|---|---|---|
| `market_gate` | ✅ CLEAR | 0.004827 | 1.415 | **10.35** | `task=edge-reps` |
| `gate_5aks` | ✅ CLEAR | 0.005751 | 1.686 | **12.33** | `task=5aks` (4 legs) |
| `triangle_gate` | ⛔ HOLD | — | 1.933 | 17.23 (on-demand) | nothing |

Board depth on both clears: `offers_returned 74 → qualifying 74 → priceable 39 → needed 4 → used_for_mean 4`
— a wide board, so this is a price reading and not the filter diagnosis wearing a price label. Both sit
under the gate's own `gate_max_ratio_vs_basis: 1.9166094031192507`; `triangle_gate` at 1.933 is over it and
refused, which is the drift line working. ⛔ **No $/hr or $/ns figure in this memo is typed from memory —
every one is quoted from the gate's own run log; `research/compute/pricing.md` owns the cost evidence.**

★ This is the machine working as designed: the gate *is* the authorization, both legs are under $50, and
5a-KS's `n = 2 seeds per arm` is recorded in the workflow as *"trimcrae go, STRATEGY Open decision 11"*.
⚠ **It is flagged anyway because committing a one-character fix and causing a rental eight minutes later
is the kind of consequence that should not arrive unannounced.** This seat is barred from renting and
from git writes, so the fix sits in the working tree for the driver.

---

## ⛔ FINDING 4 — THE STEP-1 FAN-OUT RED IS A GUARD DOING ITS JOB, DELIBERATELY, SINCE 2026-08-27. IT IS NOT A CRASH AND IT IS NOT FIXABLE HERE.

```
##[error][s1f] REFUSING to overwrite step1-fanout-map.json: committed n_complete=18,
               this tick read n_complete=0. See step1-fanout-map-regression-alarm.json.
##[error]Process completed with exit code 2.
```

`_write_map_guarded` landed 2026-08-27 in `4a198168f` ("CYC-0022: stop a live tick from silently
regressing a banked GPU result"). `step1-fanout-map.json`'s own `_incident_2026-08-27_silent_regression`
field records why, and states the open question verbatim:

> *"whether the S3 objects are permanently gone or recoverable is still unestablished and needs someone
> with working bucket credentials to check `s3://sagemaker-us-east-2-646605541856/nr4a3-step1-fanout/results/`
> directly"*

The guard fails the job **loudly on purpose**, "instead of repeating this silently every ~7 minutes", to
protect the committed record of **$73.79** of already-realised GPU spend from being overwritten with zeros.

⚠ **Two consequences the driver should weigh, neither of which is "turn the guard off".**
(1) It has been red every ~8 minutes for six days; that is alarm fatigue, and it is the reason twelve reds
on a fresh merge look alarming when eleven of them are old news. (2) `##[error]` names
`step1-fanout-map-regression-alarm.json`, and **that file does not exist anywhere in the repository or in
any branch's history** (`git log --all -- <path>` returns nothing) — the collect aborts before writing it,
so the message points a reader at evidence they cannot open. That is a small, real, $0 fix and it is
*outside this seat's touch list* (`research/modalities/congeneric_fanout_vast.py`).

**Verdict: NOT-THIS-COMMIT'S / OURS-AND-NEEDS-A-DECISION.** The decision is the S3 read, which needs
credentials this sandbox does not have.

---

## ★ FINDING 5 — NEITHER DEFECT IS `cfdc0a58b`'s, AND THE CONTROL WAS FREE

The dispatch poller fires every ~8 minutes regardless of what merged, so earlier waves landed on earlier
tips and are a control that cost nothing to read. The pattern — **three red ternary gates + one green
ternary dispatch + one red STEP-1 tick per wave** — reproduces identically:

| sha | wave (UTC) | ternary run_numbers | pattern |
|---|---|---|---|
| `e0834faf4` | 07:46 | 25600–25603 | 3 red gates, 1 green, STEP-1 red |
| `e0834faf4` | 07:54 | 25604–25608 | 3 red gates, 1 green, STEP-1 red |
| `4f54ac80b` | 08:03 | 25609–25612 | 3 red gates, 1 green, STEP-1 red |
| `cfdc0a58b` | 08:11 / 08:19 / 08:28 | 25613–25625 | 3 red gates, 1 green, STEP-1 red ×3 |

⛔ **`cfdc0a58b` is "regenerate the archive manifest and the deposit-drift block against the merged tree"
— a manifest regeneration. Its diff cannot reach a bash separator in a workflow written 2026-08-06 or an
S3 object listing.** The red count *attributed* to a sha is an artifact of how many poller waves happened
to land on that tip while it was HEAD: this one was HEAD for three waves, so it collected 12 reds where
`e0834faf4` collected 8.

★ **The merge did fix something:** `tests (modalities)` was **red** on `e65145215` and `e52beb7c3` and is
**green** on `e0834faf4` and `cfdc0a58b`.

---

## Verdicts

| lane | verdict | action |
|---|---|---|
| Ternary `market_gate` / `triangle_gate` / `gate_5aks` | **OURS-AND-FIXABLE** | **Fixed this session** + guard, mutation-tested 3/3. Driver commits; see FINDING 3 before doing so. |
| STEP 1 fan-out `tick` | **NOT-THIS-COMMIT'S / OURS-AND-NEEDS-A-DECISION** | Needs an S3 read of `nr4a3-step1-fanout/results/` with working credentials. Separately, a $0 fix to write the alarm artifact the error names. |
| GCP L4, ENDPOINT-MD, Fusion CPU, staleness watch, tests | **green** | none |
| The 12-red count itself | **INFRASTRUCTURE-AND-EXPECTED** | A poller that dispatches every 8 min attributes reds to whichever sha is HEAD. Reading a sha's red count as that sha's fault is a category error the control above refutes. |

## What was NOT done, and why

- ⛔ No workflow dispatched, re-run or cancelled; nothing rented; no git write command run. Seat constraints.
- ⛔ `congeneric_fanout_vast.py`'s missing-alarm-artifact fix left alone — outside the touch list.
- ⛔ The three gates' fix is in the working tree only.

## UNMEASURED: 2

1. **Whether the ternary gates have been red *continuously* since 2026-08-06.** The defect fires only on
   the `fleet_armed` IDLE path, so it is red exactly while the Vast account is empty; the introduction date
   is measured (`e948f9240`) and the empty-account state is measured (census, 08:28:14Z), but the interval
   between them was not enumerated. Costs one paginated Actions listing, $0.
2. **Live GCP VM state.** The GCP lane is green and under an operator hold that buys nothing, and the
   trial credit is a separate ledger — but `gcp-gpu-facts.md` §6 records that **GCE VMs do not self-delete**,
   so "the lane bought nothing today" is not a reading of "no VM is up". This sandbox has no GCP credentials.
   The zombie test is quota usage ≥ 1, via `gcp-quota-check.yml`. **Not free — it needs a dispatch, which
   this seat is barred from.**

Everything else in this memo has a quoted log line, a committed artifact, or a reproduction behind it.
