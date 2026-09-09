---
id: DOC-OPUS-CAMPAIGN-PORTFOLIO-PUB-BIOMARKER-DEP
title: "Portfolio investigation — PUB-BIOMARKER-DEP: is the biomarker-to-dependency transfer calibrated?"
level: L4
kind: investigation
status: live
date: 2026-09-08
last_verified: 2026-09-08
---

# PUB-BIOMARKER-DEP — a calibrated test of the dependency transfer

## 1 · The question

Every dependency statement in `research/manuscripts/dependency/emc-biomarker-selected-classes.md`
is a transfer from other sarcomas, because no EMC line exists in DepMap. **Is that transfer
calibrated — that is, does the committed panel recover a biomarker-defined dependency it is known to
contain, and what size of biomarker-stratified effect can it resolve?** A biomarker-selected class
claim needs the biomarker and the dependency measured in the same models; the question asks whether
this repository's instrument can carry such a claim at all, before any EMC-specific reading.

## 2 · Paper-level merit

Patient relevance is indirect but real: in a disease with well under one case per million per year,
which classes stay on the board is decided by transferred dependency evidence, and an uncalibrated
instrument keeps or kills routes for the wrong reason. The contribution is non-trivial because it is
about the instrument rather than the conclusion — it applies to every route this repository grades
on `depmap-sarcoma-dependency.json`, not only the five classes in this paper. The evidence is
attainable: the calibration below required no fetch, no compute spend and no new data.

## 3 · The exact evidence gap, and what makes it different

**Gap, established here rather than asserted:** no artifact in this repository holds a biomarker and
a dependency measured in the **same models**. `emc-expression-panels.json` holds expression in 16 EMC
tumours and no dependency and no cell line; `depmap-sarcoma-dependency.json` holds dependency in 91
screened sarcoma cell lines and no expression field, no per-line values and no EMC line. **Models in
common: zero.** The only biomarker-stratified dependency contrast committed anywhere in the
repository is BRD9 by sarcoma subtype, inside the panel's own `self_validation` and
`BRD9_by_fusion_sarcoma_subtype` blocks.

**Distinct from prior work.** The SMARCB1-in-rhabdoid control was already found mis-specified
(rhabdoid lines have *lost* SMARCB1, so non-dependence is correct biology) and BRD9-in-synovial was
already called "an inherently modest DepMap signal (n=5, −0.13)" — in
`research/manuscripts/dependency/degrader-vs-synthetic-lethal.md` and the SL1 / TD1 lane records.
Both are qualitative. **Neither adjudicated the panel's `_pass_criterion`, and neither asked whether
the failure is a power problem or a readout problem.** That question is what this lane answers, and
the answer reverses the standing qualitative reading.

## 4 · The bounded step taken

A calibration computed entirely from numbers already committed: integrality of the recorded
fractions, Wilson 95% intervals on every subtype reading, **exact Fisher power by full table
enumeration** (valid at n = 5, where a normal approximation is not), the minimum resolving n, and a
threshold-sensitivity reconstruction.

### What it found

1. **The denominator is 91, not 176.** Every `sarcoma_frac_dependent × n_sarcoma` is integral across
   all 61 genes, so all sarcoma-level fractions in the panel rest on the same **91 screened lines**
   out of the release's 176 sarcoma models. The manuscript does not state this number.
2. **Sample size is not the limitation.** Against the panel's 0.022 BRD9 background at n = 91, a
   subtype of **n = 5** has power **0.99** to detect a dependency present in 80 % of its lines, and
   0.91 at 60 %. The minimum n for 80 % power against a true rate of 0.8 is **3 lines**.
3. **The panel's own stated expected positive still does not come out.** BRD9 in synovial reads
   **1 of 5** dependent (Wilson 95 % 0.036–0.625), Fisher *p* = 0.084 against the non-sarcoma
   background. With 0.99 power against a strong subtype dependency, this is not an underpowered
   result — it excludes a *near-universal* BRD9 dependency in these 5 synovial lines while leaving
   moderate rates wide open.
4. **The readout is the limitation.** The synovial mean gene effect is −0.13 against the sarcoma
   panel's +0.105, a **−0.235 shift in the expected direction**, whose mean sits **0.37 units on the
   non-dependent side** of the −0.5 cut. The binarisation, not the n, is what discards the control.
   A single-Gaussian reconstruction of the per-line spread from the one recorded (mean, fraction)
   pair implies σ ≈ 0.44 but then over-predicts the panel's own BRD9 dependent fraction (0.084
   predicted against 0.022 recorded), so it is **not self-consistent and is reported as a bound, not
   an estimate**.
5. **The artifact keeps no dispersion.** Recorded per-gene fields are gene, n, two means, two
   fractions and selectivity — no SD, no quantiles, no per-line values. So no interval or power
   statement is possible on the continuous gene-effect scale, which is the scale finding 4 says the
   signal lives on.

### The consequence for the parked paper — offered, not applied

§2.5 argues that MCL1 and BCL2L1 being "dependencies in the large majority of sarcoma lines" is
evidence *against* selectivity. That argument is carried entirely by `frac_dependent` at the −0.5
cut, and **that binarised readout is validated by nothing**: its only stated biomarker-defined
positive control does not reproduce at 0.99 power. The claim is not shown to be wrong — the
direction of a near-universal dependency argument survives at 0.76–0.84 — but its instrument is
uncalibrated, and the paper does not say so. **No manuscript edit was made and none is proposed
here**; the park stands, and this finding neither lifts it nor adds a new claim to it.

## 5 · Artifact · validation · provenance · limitations · stop condition

* **Artifact.** `transfer-calibration.json` and its producer `transfer_calibration.py`, both in this
  directory. The producer is deterministic, reads one committed file, writes one JSON, fetches
  nothing.
* **Validation / baseline.** The baseline is the panel's own `_pass_criterion`, which was recorded
  and never adjudicated. Internal validation: the integrality check passes on 61/61 genes,
  confirming the denominator; the power computation is exact enumeration rather than an
  approximation; the Gaussian reconstruction is reported as failing its own consistency check.
* **Provenance.** Sole input `research/modalities/depmap-sarcoma-dependency.json` (DepMap public
  24Q4 CRISPRGeneEffect.csv + Model.csv, per its `data_source`). Every execution attempt, including
  the first, which failed on a repository-root path depth, is preserved under `checks/`.
* **Limitations.** ⛔ No EMC observation of any kind: this says nothing about EMC dependency,
  efficacy, safety, selectivity or clinical readiness, and asserts no such thing. The power figures
  assume independent binomial sampling and the panel's recorded background rate. The σ
  reconstruction is a bound from a single (mean, fraction) pair and is explicitly not
  self-consistent. Only the binarised readout could be calibrated at all, which is finding 5. The
  producer was not re-run and no upstream file was re-derived.
* **Stop condition — reached.** The question asked whether the transfer is calibrated. It is
  answered: powered for a strong effect, unvalidated on the readout that carries the paper's
  dependency argument, and with **zero models in common** between the biomarker and dependency axes.
  No further work here without per-line `CRISPRGeneEffect` values for the 5 synovial and 91 screened
  sarcoma lines, which would replace finding 4's reconstruction with the real distribution in one
  pass. That fetch is a networked job for the standing CI route and was **not** run: this lane may
  not commit, push or dispatch.

## 6 · Outcome

**A calibrated no-go on the matched-evidence question, with a positive methodological result.** No
matched biomarker/dependency evidence exists here for any of the five classes, and the transfer
instrument that stands in for it is well powered but unvalidated in its readout. The next credible
independent step is the per-line fetch named above; the next artifact change is a producer amendment
to retain per-line values or at least a dispersion field, which is an owner decision and is **not**
made in this lane.
