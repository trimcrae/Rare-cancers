---
id: DOC-PORTFOLIO-INVESTIGATION-PUB-IPD-SURVIVAL-2026-09-08
title: "PUB-IPD-SURVIVAL — decision-level reconstruction uncertainty on the one real figure, validated against held-out printed numbers-at-risk"
level: L4
kind: investigation
status: complete
date: 2026-09-09
last_verified: 2026-09-09
---

# PUB-IPD-SURVIVAL — what actually moves the decision, measured on the real figure

⛔ Nothing here is medical advice, and nothing here asserts efficacy, safety, selectivity or
clinical readiness for any therapy. Every number is a re-expression of one already-published
figure. No patient, no follow-up and no cohort is created here. There is no wet lab.

## 1 · The question

For the only real Kaplan–Meier figure this programme has reconstructed (stacchiotti2013 Fig. 2,
EMC, anthracycline PFS), **which source of reconstruction uncertainty is large enough to change a
decision-level number, and does external ground truth the reconstruction never saw confirm the
branch the programme selected?** Concretely: the same figure yields median PFS **5.0 months** or
**8.0 months** depending on one discrete reporting ambiguity — whether the printed first
numbers-at-risk row (`10 at t=2`) is a pre- or post-event count. Pixel accuracy cannot settle that.
What can, and how fragile is the automatic discriminator?

## 2 · Paper-level merit

The programme's live claim is a negative about reporting practice, with a method attached. A
methods claim about reconstructing published figures needs to say **which uncertainty matters**,
not only how large error is. This lane's result is directly usable by anyone digitizing a rare
disease figure: it separates *continuous reading error*, which turns out not to move the
decision-level estimate here, from a *discrete reporting ambiguity*, which moves median PFS by a
factor of 1.6 — and it shows the repository's own admissibility floor does not reliably arbitrate
between them. It also supplies the first check in this programme that tests the **reading** of a
real figure against real published numbers other than the single caption median.

## 3 · The exact evidence gap, and how this differs from completed work

Named inputs: `research/modalities/km-figure-readings.json` (`recipes[0]`, `readings[0]`),
`research/modalities/emc_ipd_survival.py` (`reconstruct`, `assess_quality`, `kaplan_meier`,
`MAX_KM_DEVIATION = 0.05`), `research/modalities/km-digitization-error.json` (envelope figures
only, quoted not re-derived).

* **R1-risk-table-sensitivity** (78f268caf → 1dd53f562) swept risk-table density × extent on
  **synthetic renders**. Not touched, not re-run, not extended, not re-graded. **S4/S5** likewise
  synthetic; `DECISION-synthetic-line-and-S6.md` closed that line NO-GO precisely because synthetic
  ease bounds nothing about real figures.
* **S6/S7** went looking for an external figure–truth pair: **0 MATCHED**, and the one decisive
  candidate (PMC8891938) is `EGRESS_BLOCKED`. That route is unavailable, and I did not retry it,
  proxy it, or seek a substitute.
* The gap nobody closed: `km-digitization-error.json` itself names the missing check —
  *"the reading needs its own evidence — an independent re-digitization, or the paper's own printed
  medians **and n-at-risk** reproduced from the reconstructed cohort."* The median half was done.
  **The n-at-risk half was never done**, and it is available at zero cost and zero new sources: the
  printed risk rows can be **held out one at a time** and predicted back. That is real published
  ground truth, from inside the figure the programme already committed — not a synthetic render,
  and not the blocked external pair.

## 4 · The bounded step taken

`decision_margin_real_figure.py` — two experiments on the real reading only.

**E1 · margin sensitivity of the branch discriminator.** A systematic additive offset δ applied to
every read survival value (the failure mode the reading's own diagnostics call out: an axis offset
moves all points together), δ ∈ [−0.030, +0.030] in 0.0005 steps plus the two measured envelope
values, 123 offsets × 2 risk-table branches = 246 reconstructions.

**E2 · held-out printed numbers-at-risk.** Each printed risk row after the anchor (t = 4, 6, 8, 10)
is withheld, the curve reconstructed without it, and the withheld count predicted from the
reconstructed cohort. The comparison value is a number the paper printed and that reconstruction
never saw.

## 5 · Results

**E2 — the reading survives its first real external check.** Held-out printed vs predicted
numbers-at-risk: t=4 → 7 vs 7 (Δ0); t=6 → 5 vs 4 (Δ−1); t=8 → 1 vs 2 (Δ+1); t=10 → 0 vs 0 (Δ0).
**Maximum error one patient in eleven**, and **median PFS and 6-month PFS rate were identical
(7.98 months, 0.511) in all four hold-outs**. Decision-level output does not depend on any single
printed row. (t=10 is a near-trivial row — the curve ends there — and is reported as such.)

**E1 — continuous reading error does not move the decision-level number; the admissibility floor
does not track reading error.**

* Median PFS was **7.98 months in all 123 offsets** of the anchored branch, i.e. unchanged out to
  ±0.030 in survival — roughly 19× the reading's own pixel-uncertainty bound (0.0016) and 8.6× the
  worst off-step error the synthetic control ever measured (0.0035).
* The **event count is not** robust: (events, censored) took (8,3), (9,2) and (10,1) across the
  same offsets — ±1 event in an 11-patient cohort.
* **The floor's margin is 0.0046.** The correct branch — the one reproducing the caption's printed
  median — becomes **inadmissible at δ = +0.005**, only 3.1× the pixel bound and 1.4× the worst
  measured off-step error. The floor's error here is one of **false refusal**, not false admission:
  the wrong (printed-table) branch was **never** admissible anywhere in the scan (minimum deviation
  0.0604 > 0.05).
* **Admissibility is non-monotone in reading error.** Beyond δ ≥ +0.019 the reconstruction absorbs
  the offset by dropping an event (9 → 8), the deviation falls back to ~0.031, and the curve
  **passes the floor again with a cohort whose event count is wrong**; symmetrically at δ ≤ −0.025
  (9 → 10 events). This is the repository's known metric-blindness finding — previously shown on
  synthetic renders — reproduced **on the real figure** and quantified as an exact re-admission
  threshold.

**Decision-level summary.** For this figure the uncertainty that could change a decision is not the
pixels. It is the discrete question of what the first printed risk row means: median PFS 5.0 vs 8.0
months. Pixel accuracy cannot resolve it, the admissibility floor resolves it only with a 0.0046
margin and non-monotonically, and what actually resolved it is external printed ground truth — a
caption median plus (now) four held-out risk counts. **Most published figures print neither.**

## 6 · Artifact · validation · provenance · limitations · stop condition

* **Artifact.** `decision-margin-real-figure.json` (62 KB, full per-offset and per-hold-out
  records), `decision_margin_real_figure.py`, `summarize.py`, `checks/01-decision-margin/`,
  `checks/02-summarize/` (command, stdout, stderr, exit_code — both exit 0; no attempt failed and
  none is omitted).
* **Validation / baseline.** Baseline is the committed reconstruction in `km-figure-readings.json`,
  reproduced exactly by this script (anchored: n=11, 9 events, 2 censored, deviation 0.0454,
  median 7.984996; printed: n=10, deviation 0.0903, inadmissible) — so the harness is verified
  against the repository's own committed output before any perturbation. E2 is validation against
  data external to the computation.
* **Provenance.** Coordinates were not typed here: every one is loaded from
  `km-figure-readings.json`, which names the committed image and reader. Repo HEAD at run
  `b6baa1b7cf919a352dc0f61d0bf0c2ab354ae2b4`; run 2026-09-09 ~00:0x UTC; 13 GiB free at start;
  no repository file outside this directory was written, no git operation run, no network call, no
  GPU, no paid API, no subagent.
* **Limitations.** One figure, one endpoint, one 11-patient series — nothing here generalises to
  another figure without being re-run on it. The four hold-outs are not independent replicates: the
  digitized curve and the remaining rows are shared, so they bound *self-consistency with printed
  counts*, not reading accuracy in general. E1 models a **systematic** survival offset only; time
  offsets shift the median rigidly by ≤0.008 months (the reading's own bound) and were reasoned,
  not scanned. `MAX_KM_DEVIATION`, the digitizer and every gate were left untouched. No pooling, no
  new dataset, no reporting requirement, no journal recommendation and **no clinical claim** follows
  from any of this.
* **Stop condition (met).** Both experiments produced a durable graded result on real inputs with
  the baseline reproduced. Reached; stopped.

## 7 · Next credible independent work (not done here)

1. **Unapplied, proposed to the owner, not written:** record in `km-figure-readings.json` that the
   anchored reading now has a **second** external check — four held-out printed risk counts, max
   error 1 — alongside the caption median. That is a shared-file edit and is deliberately left as a
   proposal.
2. The false-refusal margin (0.0046) and the non-monotone re-admission at δ ≈ +0.019 are properties
   of `MAX_KM_DEVIATION` as a *sole* discriminator. The honest successor is not a new floor value —
   it is to state in the manuscript that admissibility must be reported **with** an external check,
   and that a figure lacking one cannot have its branch chosen automatically.
3. The blocked dependency is unchanged: a real figure whose patient-level truth is also published
   (S6/S7). Nothing here substitutes for it and nothing here reopens the blocked route.
