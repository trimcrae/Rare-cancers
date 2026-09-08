# C1 — next question stated IN FULL before dispatch

Recorded `date -u` **Tue Sep 8 07:24 UTC 2026**. Same session, sole parent collector, `claude-opus-5` medium,
saved subscription, no overage, deadline 2026-09-09T02:37:19Z. Stated before dispatch as required; nothing is
dispatched on this until the five elements below are on record.

## Why this is a scientific question and not another inventory

I applied the test to this one myself rather than inheriting a rank. **B1 failed because a readability
adjudication has no dependent conclusion — nothing changes whichever way each row lands.** This candidate has
one: a load-bearing denominator is measurably wrong, and **whether the paper's quantitative conclusion survives
the correction is currently UNKNOWN**. That is the difference, and it is the whole justification.

## (a) Exact scientific question

**Does the compartment-B upper band on treating host comorbidity in EMC survive correcting its own denominator
— and by how much does it move?**

`research/manuscripts/emc-host-factor-model.json` sets `competing_share_of_deaths_used = 0.394`, sourced to
*"within-series (Meis-Kindblom 1999) — the only pairing measured on the same patients."* The paper's own
Appendix A.1 states verbatim *"Competing share, 39.4 per cent superseded by 21.7 per cent"*, and its Results
table carries the adopted `21.7 %` (163 patients, 18 disease / 5 other-cause deaths), corroborated
independently at 23.0 % by relative survival. **Parent-verified all three lines directly.** So the model runs on
the superseded estimator, **high by 39.4/21.7 = 1.82×**, and its source sentence is now false —
`direct_cause_split` *is* a same-patient pairing and *is* what the paper adopted.

**Why it matters:** this is the portfolio's only route whose intervention already exists and is already
approved, and the competing-mortality share bounds the entire antitumour argument. A band inflated 1.82× either
collapses to something unremarkable or survives — and nobody knows which.

## (b) Actual reachable evidence, with access limits

Committed, $0, no network: `emc-host-factor-model.json`, `emc-host-factor-inputs.json`,
`emc-mortality-decomposition.json`, `emc-terminal-events.json`, `emc-mortality-mechanisms-paper.md`, and the
model's generator. **Limits, stated:** the model's own `factors_not_entered` (type-2 diabetes/metformin,
hypertension) need a **network retrieval outside worker authority** and stay out; host-factor prevalence in a
real EMC cohort is blocked on `BLK-NO-EMC-DATA` and is unobtainable here. Neither limit blocks the
recomputation, because both are inputs the model already excludes.

## (c) Contribution and novelty uncertainty — stated honestly

Contribution: **it determines whether a recorded defect is material or cosmetic**, which no committed artifact
currently answers. **Novelty: this is NOT a new paper and none is claimed** — it is the consequence of a
correction inside a `drafted` endpoint. Whether the corrected band is *scientifically interesting* is
**UNKNOWN until computed**, and if it turns out to change nothing, that is the result and it is reported as
such. Per the standing instruction, a drafted endpoint does not prove every useful scientific correction is
closed — but neither does this become a paper by being useful.

## (d) Distinction from named prior no-gos

Not the parked synthetic figure-validation family (no digitization, reconstruction, sweep, point-count
successor or figure route). Not S6/S7 (no source hunt, no network, no PMC). Not B1 (a dependent conclusion
exists). Not P1–P6: the endpoint is `PUB-MORTALITY-MECHANISM`, and AUT-064's "ANSWERED — no" names
`PUB-CARE-DELIVERY`, a different endpoint. Not lane 2 (no expression data, no arm comparison, no panel score).
Not a record or consumer census — it recomputes a scientific quantity. Touches no `CLOSED-WORK.md` denied
source, no GSE4303/GSE28866, no PMID 22592656, no W25/GSE243553, no NR4A Perspective, no P6 manuscript.

## (e) Finite acceptance and stop

**Acceptance:** the compartment-B figures recomputed with the share taken from `direct_cause_split`, each
reported beside its current value and its ratio, in a **report with durable raw output** — plus an explicit
statement of whether the paper's stated conclusion survives.
**Stop, whichever comes first:** (i) acceptance; (ii) a committed record shows the within-series estimator was
chosen **deliberately** — then this is a documentation defect, the branch stops there and that is the result;
(iii) the recomputation cannot be done without an input the model excludes; (iv) ~40 tool calls / ~40 minutes.
**Hard stops:** no manuscript edit, no graph edit, no `systems/graph/` write, no re-derivation of the
decomposition, no re-retrieval of effect sizes, no writing of a paper. The child produces a **report and raw
artifacts only**; every repository write, including any eventual correction, remains an **owner act**.

## Bounds

Read-only with respect to the checkout; all execution in scratch, durable artifacts to
`/tmp/claude-0/c1-retained/` **outside** the checkout, hash-verified **before** any cleanup and not deleted;
parent alone collects. ≥10 GiB free. No network, no paid API, no GPU, no publication, no external contact.
Model verified from the child transcript after launch.

---

# ⛔ SCOPE APPENDED 2026-09-08 07:28 UTC — two overstatements in (a) corrected, originals not rewritten

The contract text above is **preserved unchanged**. Two claims in element (a) overreach and are scoped here.

1. **"The competing-mortality share bounds the entire antitumour argument" — withdrawn.** It does not. The
   quantity is a **cohort death fraction** — what share of deaths in a retrospective series were attributed to
   causes other than the tumour. It is **not population mortality risk**, **not a causal treatment effect**, and
   **not a bound on the portfolio's antitumour argument**.
2. **"The portfolio's only route whose intervention already exists and is approved" — scoped.** That is a
   statement about *regulatory availability of a drug class*, never a claim that treating host comorbidity
   helps anyone with this disease.

**Binding on the run and its report:** recomputing this number **establishes no clinical benefit**, no efficacy,
safety, selectivity, therapeutic window or readiness, and no bound on any antitumour claim. It is arithmetic
over a committed model's inputs. **The corrected band, whatever it is, is a model output — not a treatment
effect and not a patient-facing quantity.**

## Provenance requirement added before execution

**Verify the source estimator's provenance BEFORE treating the discrepancy as a defect.** Use
`direct_cause_split`'s **stored value, or its exact numerator and denominator**, from the committed artifact.
**Do not derive a fresh value from the displayed, rounded "21.7 per cent"** — a rounded display is not the
input. If the stored value and the displayed one disagree, that disagreement is itself the result.

**Hold every other model assumption fixed.** Change the competing-share input and nothing else; report the
actual changed outputs and state, for each stated model conclusion, whether it changes and **why**.

**A documented deliberate-estimator stop is an admissible RESULT**, not a reason to run another variant. If a
committed record shows the within-series estimator was chosen on purpose, the branch ends there — no second
configuration, no sensitivity sweep, no alternative share.
