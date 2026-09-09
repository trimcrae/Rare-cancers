---
id: DOC-PORTFOLIO-INVESTIGATION-FUSION-OUTPUT-2-20260909
title: "FUSION-OUTPUT-2 — what the pre-registration settles before the gated run is spent"
level: L4
kind: investigation
status: live
date: 2026-09-09
last_verified: 2026-09-09
---

# FUSION-OUTPUT-2 — follow-through lane

**Design document, not a result.** No expression value was read, no contrast was computed, no
biological conclusion is reached. Deliverable: `PRE-REGISTRATION.md` plus the frozen gene-set
artifact and its generator. The executable outcome protocol remains a **coordinator-owned frozen
gate**; this lane pre-specifies a test and neither authorises nor pre-empts it.

## 1 · The question

The completed lane `../PUB-FUSION-OUTPUT/` produced a design constraint from membership alone: at
±2 kb, 69 EWSR1::NR4A3 program genes fall to 40 after subtracting all 28 alternative-fusion programs,
but to 7 after also subtracting the other three NR4A3 fusions (4 at 1 kb, 6 at 5 kb). **Can that be
turned into a pre-registered test design — sets named, decision rules fixed, detectable effects
computed — so the constraint is settled before the gated run is spent rather than discovered
afterwards?**

## 2 · Merit

The constraint is worthless if it surfaces after the run. Pre-registration is the only artifact that
converts it into a saving: it fixes 40 genes and 7 genes, their identities and their subtractions in
advance, states what a positive, a negative and an uninterpretable outcome each look like, and
computes what either contrast could see at the cohort sizes that actually exist (6 and 10 EMC
tumours). Patient relevance is indirect but real — every therapeutic argument in EMC runs through
"the fusion's output is where the disease lives" — and the contribution is a design decision the
coordinator's frozen protocol did not have.

## 3 · What the design settles

1. **The sets are now auditable and fixed.** `fusion-program-testsets.json` names every gene at every
   window with its Ensembl id and the full list of the 32 programs containing it, keyed to the input
   file's SHA256 `b54b3eda97c0663e052cfe52ac4b8dbae3914bbffad73a905de98de8873c801b`. Counts reproduce
   the prior lane exactly (index 36/69/142; A 23/40/57; B 4/7/6).
2. **Contrast A is identifiable but only for a large effect.** It clears the manuscript's 4-gene floor
   by 36 genes and its rank statistic against 28 alternative programs can reach α = 0.05 (minimum
   *p* = 1/29 = 0.0345). But at ρ = 0.2 its minimum detectable per-gene effect is **0.61 SD units** on
   GSE24369 and **0.73** on GSE4303, rising to **0.89** with α adjusted for 28 programs.
3. **Gene count is not the binding constraint — sample count is.** Under independence the B/A MDE
   ratio at 2 kb is 2.39; at ρ = 0.2 it is **1.195**, and both contrasts collapse to *m*<sub>eff</sub>
   ≈ 3–5 effective genes. The 40-vs-7 headline overstates the power difference by roughly a factor of
   two once co-regulation is assumed. **This is the design finding the prior lane could not have.**
4. **Contrast B should not be run, stated numerically.** A rank of the EWSR1 program among the four
   NR4A3 programs has minimum one-sided *p* = **0.25** and cannot reach α = 0.05 at any effect size;
   its MDE is 0.73–0.87 per-gene SD; its window-invariant core is **3 genes**, below the manuscript's
   own 4-gene floor; and at 1 kb (exactly 4 genes) a single unreadable probe drops the set below the
   floor. Recommendation: **do not run it**; if overridden, secondary and descriptive only, never as a
   *p*-value for or against partner specificity.
5. **Cross-window agreement is not available as robustness.** Jaccard across windows is 0.25–0.50
   (A) and 0.43–0.63 (B); the three windows are different sets, so ±2 kb is pre-declared primary and
   the others are reported as different sets giving different answers.
6. **Two prerequisites are declared before any scoring.** GPL3290 coverage through the EST bridge is
   unknown offline and must clear the 0.4/4-gene floors before GSE4303 is scored; and GSE4303 is
   graded circular (§3.8), so a positive existing only there is uninterpretable by pre-declaration.

## 4 · Artifact · validation · provenance · limitations · stop condition

* **Artifacts.** `PRE-REGISTRATION.md`; `fusion-program-testsets.json` (generator `build_testsets.py`,
  stdlib only); `design-power.json` (generator `power_design.py`, scipy analytic, no data);
  `set-stability.json` (generator `set_stability.py`); `verify_prereg_tables.py`.
  `checks/01…04/` hold every execution attempt with `command.txt`, `stdout.txt`, `stderr.txt`,
  `exit_code.txt`. Four attempts, all exit 0, no failed attempt occurred and none is hidden.
* **Validation.** Set counts reproduce the completed lane's independently written script exactly.
  `verify_prereg_tables.py` machine-checks all six gene tables in the prose against the JSON and the
  quoted digest against the computed one (exit 0). Floors, scoring rule, cohorts and the MDE critical
  -value convention are the repository's own (PUB-FUSION-OUTPUT §2.3; W17c), not new thresholds.
* **Provenance.** Sole data input `outputs/common-platform-membership.tsv` from the coordinator-frozen
  packet `research/autonomy/nr4a3-program-source-2026-09-07`, read in place in the frozen corpus,
  hashed by the generator; memberships frozen before any outcome, mapping specification hashed before
  mapping. Sample counts are metadata from PUB-FUSION-OUTPUT §2.2. No network, no GPU, no spend, no
  expression matrix opened. Nothing was written outside this directory; no `git add`/commit/push, no
  preflight, no subagent.
* **Limitations, carried forward verbatim** — HEK293T, ectopic, **accessibility not occupancy**, not
  EMC material, so nothing here can make a gene fusion-driven or be cited as a cistrome; promoter
  ±2 kb only, so distal regulation is unreadable rather than absent; positive-only BEDs, so a closing
  program is invisible; ~9-fold program-depth asymmetry across the four NR4A3 fusions; absence from a
  program is an unread negative, never a measured zero. Additionally, every MDE rests on declared
  assumptions (unit per-gene z variance, a common effect across members, a single average ρ, df =
  *n*₁+*n*₂−2) that all bias the numbers **optimistically**; the true detectable effects are larger,
  not smaller. No efficacy, safety, selectivity, therapeutic-window or clinical-readiness claim.
* **Stop condition.** Stopped at the design boundary, deliberately and by instruction. The gate is
  coordinator-owned; the EMC expression matrix is not in the checkout or the frozen corpus and GEO
  egress is proxy-denied, so no contrast was runnable here even had it been authorised.

## 5 · Outcome for the paper

No manuscript prose was edited and none is proposed as applied text. Two usable outputs for the
paper's owner and the gate's owner: a frozen, auditable set definition that removes the "which genes"
question from the post-run discussion, and a numeric recommendation to drop the partner-specific
contrast — which, if accepted, saves the gated run from spending power on a comparison whose rank
statistic cannot reach significance at any effect size. Any use of either belongs to those owners.
