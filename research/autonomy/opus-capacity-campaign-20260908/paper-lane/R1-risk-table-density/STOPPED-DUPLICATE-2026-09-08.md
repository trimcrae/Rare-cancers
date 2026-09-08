---
id: DOC-OPUS-CAMPAIGN-R1-DENSITY-STOPPED-DUPLICATE
title: "R1 risk-table density sweep — STOPPED as a duplicate of completed work"
level: L4
kind: selection-record
status: stopped
date: 2026-09-08
last_verified: 2026-09-08
---

# R1 risk-table density sweep — STOPPED, duplicate

**Selection error by the parent, caught by the launcher's reconciliation and corrected here.**

## What I selected, and why it was wrong

I launched this owner from the retained backlog's **ready** list
(`PROPOSAL-next-work-backlog.md` lines 66–146, "R1 · What a journal must print beneath a survival
figure…"). That entry was **already executed and closed** before I selected it. I did not check the
lane directory for a completed sibling before dispatching. The backlog is a **proposal document**;
it is not a live queue, and an entry in it is not evidence that the work is outstanding.

## The completed work this duplicates

| | |
|---|---|
| lane | `R1-risk-table-sensitivity/` |
| commit | `78f268caf` (2026-09-08 19:29:23 +0000) |
| result | `RESULT.md`, 12,536 B |
| original run | `RUN-01.stdout.json`, 72,838 B; `RUN-01.stderr.txt` **empty**; `RUN-01.status` |
| closure | root's dated interpretation correction at `1dd53f562`, "R1 flat band", **closed as a bounded diagnostic without paper promotion** |

**Its design strictly supersedes the one I dispatched.** The completed lane ran the **full crossing**
`R ∈ {2,3,4,5,6,8,10,13,19,25}` × `L ∈ {45, 90, 135, 168, 180}` = **50 cells**, plus a sentinel cell
and a rounding probe = **52**, with the exact-coordinate and clean-render arms kept separate and
density swept only at the clean render. My contract asked for a **6 × 5 = 30-cell** grid over the
same two axes plus the printed-vs-anchored contrast. That is the same design space, done less
completely. It is also distinct from `S4-density-extent-anchoring-EXECUTED.md`, which measured the
two axes only **marginally** — the completed R1 lane says so itself and does not re-quote S4.

## Actual execution record produced before the stop — retained, not discarded

Four runs, real commands and measured exits, in `checks/`:

| run | command | exit |
|---|---|---|
| 01-baseline-check-preedit | `python3 research/modalities/km_digitize.py --check` | 0 |
| 02-baseline-tests-preedit | `python3 -m pytest research/modalities/tests/test_km_digitize.py -q` | 0 |
| 03-reproduction-gate-prototype | `python3 …/scratchpad/gate.py` | 0 |
| 04-grid-prototype | `python3 …/scratchpad/grid.py` | 0 |

**The reproduction gate PASSED exactly**, independently reproducing the committed
`exact_coordinates_baseline` at `risk_times = [0, 24, 48, 72, 96, 120, 144, 168]`:

```
MEASURED events_delta_vs_truth: 0        COMMITTED events_delta_vs_truth: 0
MEASURED censored_delta_vs_truth: -7     COMMITTED censored_delta_vs_truth: -7
MEASURED internal_max_abs_km_deviation: 0.0009   COMMITTED: 0.0009
```

That is a genuine, if small, independent corroboration of the committed control artifact by a
process that had not seen the completed R1 lane. It is recorded as exactly that and **nothing more**
— it is not a new result, it is not promoted, and no requirement is stated from it.

**No tracked file was modified.** `km_digitize.py`, `km-digitization-error.json` and
`tests/test_km_digitize.py` are byte-unchanged; the `BEFORE/` copies here are the untouched
originals with their sizes.

## Disposition

**Stopped, not paused.** The work is done and closed; there is nothing outstanding behind this
label. Nothing here is to be extended under a reused label, and the completed lane's design is not
to be silently widened. The contract that was issued and this record are retained as the selection
history.
