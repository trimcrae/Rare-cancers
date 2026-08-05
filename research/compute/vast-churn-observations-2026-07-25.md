---
id: DOC-VAST-CHURN-OBSERVATIONS-2026-07-25
title: Vast churn, 2026-07-25 — three cost-model priors the 5a-KS benchmark run contradicts
level: —
kind: runbook
status: live
canonical_for: []
purpose: See the document body; purpose was not stated separately when frontmatter was backfilled.
scope: Scope not separately declared. Inferred kind `runbook` from its location under research/compute/.
audience: [maintainers, autonomous research agents]
date: 2026-08-05
last_verified: unverified
_backfilled: true
---
# Vast churn, 2026-07-25 — three cost-model priors the 5a-KS benchmark run contradicts

*Companion: [vast-placement-facts.md](./vast-placement-facts.md) covers why a rental does or does not
**happen** — our own filters, board width, the tier — and carries a later, larger host-lifetime measurement
(208 rentals) than the one night below.*

**Status: OBSERVATIONS, not a re-derivation.** One night, one lane, ~12–20 legs. Suggestive, not
decisive. Nothing here is a reason to change the bid yet; it is a reason to stop treating three
numbers as settled, and it names the measurement that would settle them.

## What was observed

The 5a-KS known-answer benchmark (qualified 2026-07-25) ran ~12–20 legs on Vast overnight. It
completed, but the wall clock was set by host churn rather than by compute — 1.1 GPU-h/leg of work
took ~12 h of elapsed time.

1. **~half of all rentals never got a GPU.** They returned
   `{"success": false, "error": "resources_unavailable", "msg": "...state change queued."}` — the
   machine advertised a slot and could not schedule it. At least 8 distinct machines
   (53989, 11892, 142143, 53947, 9427, 143878, 117843, 144626, 137041 …) did this.
2. **Legs died mid-run repeatedly.** The Y29F apo legs died three separate times, at 12/16, 8/16 and
   2/16 windows. They finished only because completed λ windows restore from S3.
3. **Dead legs stayed dead until a human relaunched them.** Unattended, two legs sat with no host for
   203 and 276 minutes.

## Which priors this bears on

| prior (`vast_cost_model.py`) | stated basis | what this run suggests |
|---|---|---|
| **F5** — "essentially none [of 445 offers] were rented… there is nobody there to outbid" | counting **offers** | The inference from *offer listed* to *GPU free* does not hold: ~50% of **rental attempts** were refused. F5 may still be true in aggregate, but it is not evidence for the step it is used for. |
| `DEFAULT_HAZARD_PER_H = 0.10` | prior, flagged as such | Looks **2.5–4× low**. ~15–20 running hours should give ~1–2 preemptions; we saw materially more. |
| `DEFAULT_DOWNTIME_H = 0.25` | "re-dispatch to one of ~148 substitutes" | Assumes an **automatic** re-dispatch loop that does not exist in this lane. Real downtime was 20–40 min attended, **3–4.5 h unattended**. |

## Why this matters even if the bid is right

The model minimises `C(b) = b·W/(1 − λR)` and concludes a margin is not worth buying **partly because
preemption is cheap** — small λ times small R. Both of those inputs are contradicted above, so the
conclusion is downstream of two numbers this run disputes. **The bid may well still be correct; the
justification needs re-deriving against measured λ and R.**

## What is NOT contradicted

- **Margin does not buy acquisition priority.** Tested directly on 2026-07-25: a stuck leg's bid was
  raised 26% to its value ceiling and the instance stayed queued exactly as before. This is
  independent support for the "staleness tick, not priority premium" design.
- **Retention is untested in either direction.** Whether a higher bid holds a *running* leg was never
  measured. Do not assume tonight's acquisition result transfers to it.
- **$/ns offer selection.** Unaffected by any of this, and it demonstrably worked — it put the first
  pilot leg on a $0.044/h 3090 at $0.00295/ns against a 4090 alternative at $0.00473/ns.

## The measurement that would settle it

`vast_cost_model` already ships `fit_lambda_ref` and `LaunchRecord` and says plainly that λ is "a
PRIOR, not a measurement… because launches have never recorded time-to-preemption." That is still
true. The fix is to log, per rental: `machine_id`, `min_bid`, `bid`, rental time, first-running time,
death time, and cause (`resources_unavailable` vs died-while-running). An MLE over exponential
survival, censored at completion, then replaces both priors with numbers.

A matched A/B — floor+tick versus 1.5× floor, same leg, time-to-death recorded — would separately
answer the retention question the acquisition test could not.
