---
id: DOC-PORTFOLIO-INVESTIGATION-PUB-SURFACE-TARGETS
title: "PUB-SURFACE-TARGETS lane — is the EMC surface-antigen exposure axis an artifact of pooling a six-organ, 37%-fetal normal panel?"
level: L4
kind: investigation
status: live
date: 2026-09-09
last_verified: 2026-09-09
---

# PUB-SURFACE-TARGETS — portfolio investigation

Branch `claude/confident-bardeen-ji76cd`. Written under the campaign shared contract. **Nothing
outside this directory was edited.** No commit, no push, no preflight, no subagent.

## 1 · The question

**Does the paper's only quantitative on-target/off-tumour reading survive resolution of its normal
arm?** Concretely: when the GSE28866 normal arm is read *by organ* and *adult-only*, and summarised
by the **worst normal organ** rather than by a pooled median over 27 libraries, does the standing of
the named candidates (ALCAM's demotion, CSPG4's hold, the BGN/CD44/VCAN rises) change — and which
normal compartments does that panel never observe at all?

This is a normal-tissue **comparator** question, not another pass over the atlas and not a residual
correction.

## 2 · Paper-level merit

On-target off-tumour exposure is the gate that ends surface-target programmes; it is the one axis on
which this manuscript demotes its own lead antigen. The demotion currently rests on one number pair —
ALCAM 0.578 in EMC against 0.631 in "normal" (`emc_over_normal` 0.9165, 33.1st percentile of the
deposit-wide ratio distribution). **Exposure is a worst-organ property, not a median property:** an
antigen that is absent in five organs and high in one has a bad window and a benign median. A pooled
median across a panel that mixes organs and ages cannot express that, in either direction — so the
demotion is currently as unfalsified as the promotion it replaced. Resolving it is a
prioritisation-of-what-to-stain statement, attainable from one already-read public deposit, and
reusable by any rare-tumour surface-target programme.

## 3 · The exact evidence gap, and what makes it new

Measured here, from the two committed artifacts, and recorded in `exposure-coverage.json`:

| Fact | Value |
|---|---|
| Normal libraries in the only quantitative normal arm (GSE28866) | **27** |
| Of those, **fetal** | **10 (37.0 %)** — 3 bowel, 3 kidney, 4 lung |
| Distinct organ types | **6** (breast, lung, colon, bowel, kidney, uterus) |
| Organ types with **adult** libraries | 5 — and uterus has **n = 1** |
| Committed summary statistic | **one pooled median over all 27 libraries per gene** |
| Per-organ values present anywhere in this checkout | **no** |
| Tissues the paper's own heuristic flags as vital | **21** |
| Of those, with **any** quantitative normal observation | **4** (colon, kidney, lung, small intestine — the last only via *fetal* bowel) |
| With any **adult** quantitative observation | **3** (colon, kidney, lung) — **19 %** of the flagged list |
| Vital tissues with **no** observation | **17**: heart, cerebral cortex, brain, cerebellum, hippocampus, amygdala, basal ganglia, spinal cord, nerve, liver, pancreas, duodenum, stomach, bone marrow, skeletal muscle, smooth muscle, cardiac |
| HPA antigen records carrying a quantitative tissue nTPM | **0 of 46** (blood nTPM: 0 of 46) |
| Candidate genes with **any** quantitative normal observation | **19 of 52**; the other 32 are categorical label only |

**Distinct from completed and held work.** The R1–R8 residual batch and the sixteen-panel erratum are
corrections to what was computed; the B4 surfaceome-membership route concerns set *definition*. None
of them touches the composition or the summary statistic of the normal arm. The atlas asks
*EMC vs comparator sarcoma* (lineage); this asks *EMC vs which normal organ, in adults* (exposure) —
the deposit's own note already separates those two axes and warns they must not be read as each
other. No prior artifact in this tree resolves the normal arm below the pooled median.

## 4 · The bounded step taken, and the honest outcome

**Outcome: a bounded partial no-go with a quantified gap and a ready analysis.** Two access routes to
per-organ normal values were probed and both are closed from this sandbox; both attempts are
preserved in `checks/`.

* `checks/01-fetch-probe` — the GSE28866 peak matrix (~13 MB, the file CI has read before):
  **CONNECT tunnel failed, 403**, curl exit **56**.
* `checks/02-snaptron-probe` — Snaptron `gtexv2` (an *independent* adult normal reference this
  repository already uses, and which would cover heart, nerve, brain and skin): **CONNECT 403**,
  exit **56**. `checks/03-proxy-status` records the proxy state behind both.

Neither is a denied or closed source; both are ordinary public endpoints unreachable from this
container, and the contract forbids this lane from committing or pushing, which is what a CI-runner
route would require. So the step was taken where it could be:

1. **`exposure_coverage.py` → `exposure-coverage.json`** (ran, exit 0) — a coverage census over the
   two committed artifacts that converts "no clean normal-tissue window is established" into the
   exact table in §3. It counts *evidence*, never expression.
2. **`perorgan_normal_reanalysis.py`** — the prespecified per-organ / adult-only / worst-organ
   re-reading, written before any real value could be seen, with its reduction order taken from the
   committed producer, its low-n rule fixed (uterus, n = 1, excluded from the primary maximum and
   reported in a sensitivity arm), and **no test defined** (n_EMC = 4; sqrt-compressed scores).
   Its logic is validated offline: `--selftest` builds a fixture gene that is safe on the pooled
   median (EMC/pooled = 10.0) and dangerous in one adult organ (EMC/worst-adult-organ = 0.2), and
   **7 of 7 assertions pass, exit 0** (`checks/05-perorgan-selftest`). The missing dependency is now
   a file, not a design.

**Incidental, unapplied.** In `research/modalities/emc-surface-normal-window.json`, ALCAM carries
`rna_blood_cell_specificity: "Immune cell enhanced"` with `immune_or_circulating: false` and
`window: RESTRICTED`. That is a heuristic-flag question about a committed artifact, outside this
lane's scope; it is recorded here, **not** edited and **not** graded.

## 5 · Artifact · validation · provenance · limitations · stop condition

* **Artifact** — `exposure-coverage.json` (computed), `exposure_coverage.py`,
  `perorgan_normal_reanalysis.py` (prespecified, fixture-validated), `checks/01`–`05`.
* **Validation / baseline** — the coverage census is a recount of committed records and was checked
  against the deposit's own `grouping` block (27 = 17 adult + 10 fetal reconciles with the series
  description). The re-analysis carries a synthetic positive control whose correct answer is known by
  construction and is the *opposite* of the pooled reading; all 7 assertions pass.
* **Provenance** — `research/modalities/emc-surface-normal-window.json`,
  `research/modalities/gse28866-tumour-vs-normal.json`,
  `research/modalities/gse28866_tumour_vs_normal.py` (reduction order), `systems/graph/publications.json`
  (PUB-SURFACE-TARGETS), `systems/graph/artifacts.json` (ART-EMC-EXPRESSION-PANELS). Every number in
  §3 is emitted by `exposure_coverage.py` from those files; none is retyped by hand.
* **Limitations** — transcript only; no protein, surface localisation, receptor density, selectivity,
  safety or therapeutic-window claim is made or supported. The census counts evidence, not
  expression, and a tissue counted "observed" is observed only inside a pooled median.
  `ORGAN_TO_VITAL` is a literal six-label map. The re-analysis has **not** been run on real data and
  therefore **no candidate's standing is changed by this lane**.
* **Stop condition** — stop when either (a) the GSE28866 peak matrix is available locally, at which
  point `--peaks` produces the per-organ table in one run; or (b) an authorised owner declines the
  fetch, in which case the coverage table in §3 stands as the honest statement of the exposure axis'
  reach. **Do not** substitute a reused cohort, a proxy source, or a categorical label for the
  per-organ values.

## 6 · Next credible independent work, in order

1. **One unauthenticated public GET** of `GSE28866_36048_normalized_peaks_cancer_and_normal.txt.gz`
   (a file this repository's CI has already read once) → the per-organ table, immediately.
2. **An independent adult normal reference** covering the 17 unobserved vital tissues — Snaptron
   `gtexv2`, already used by this repository and already recorded as reachable from CI. That is the
   only route by which heart, nerve, brain, liver, marrow and adult soft tissue enter the exposure
   axis at all, and it is a genuinely independent instrument rather than a re-read of the same arm.
3. Only then: any statement about whether ALCAM's demotion or CSPG4's hold survives.
