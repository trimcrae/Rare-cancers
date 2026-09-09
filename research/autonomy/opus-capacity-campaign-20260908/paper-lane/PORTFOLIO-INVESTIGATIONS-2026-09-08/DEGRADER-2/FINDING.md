---
id: DOC-PORTFOLIO-INVESTIGATION-DEGRADER-2-20260909
title: "DEGRADER-2 — per-frame RSA: the exact frame-level overlap between NR4A3's unique cysteines and the paralogue cysteines, and a full re-derivation of the committed quantile block"
level: L4
kind: investigation-finding
status: live
date: 2026-09-09
last_verified: 2026-09-09
lane: DEGRADER-2
campaign: OPUS-CAPACITY-CAMPAIGN-20260908
predecessor: PUB-DEGRADER (first round, same campaign)
---

# DEGRADER-2 — exposure separation read per frame, not per quantile

## 1 · The question

Every exposure figure the degrader paper's covalent axis rests on — the paralogue ceiling
**RSA 0.2126**, C397's pooled p10/median, and the first round's per-replica margins — is read off
**quantile summaries** published in `nr4a-paralogue-dynamics.json`. **What is the exact frame-level
overlap** between NR4A3's unique cysteines and the paralogue cysteines in the same committed
conformers, and **do the published quantiles reproduce** when RSA is recomputed frame by frame?

## 2 · Paper-level merit

The covalent categorical axis is the one selectivity axis in this paper that does not inherit the
free-energy engine's unvalidated status, so it carries the paralogue argument. Its load-bearing
sentence is a **no-overlap** sentence ("never exceeds 0.2126"), and a no-overlap sentence is exactly
the kind that quantile summaries cannot verify: p10 and max bound a distribution, they do not count
frames. Converting a bounded statement into an exact count is cheap, it is the step the first round
named as the next credible work, and it can only sharpen or correctly qualify the claim. It also
re-derives 432 published statistics from primary conformers, which is an independent integrity check
on the artifact the manuscript quotes.

## 3 · The exact evidence gap, and how it differs from prior work

* **First round (PUB-DEGRADER) did:** split the *published quantiles* by replica and reported
  per-replica ceilings and p10 margins. Its own stated limitation (a): "the source publishes
  **quantile summaries, not per-frame RSA**, so … **no exact frame-level overlap fraction can be
  computed here**." Its section 6 named the per-frame export from the committed conformers as the
  next work and did not run it.
* **This lane does exactly that one thing** and nothing else: 225 committed `frame.pdb` conformers →
  per-frame per-cysteine RSA with the *same committed routine*. The expensive term-(a) reach
  Monte-Carlo is **not** recomputed and is untouched; the biased `metad` subset is excluded exactly
  as the source excludes it.
* **Not re-opened:** every free-energy construct, the `C7` cutoff, the chemoproteomics route
  (`STOP_NO_REFERENCE`), R1–R4, B1/B2/B4. No network read, no GPU, no docking, no structure
  prediction, no new sampling. The `portfolio-2026-09-05` recommendation's row 5 (NR4A3 degrader
  optimisation, **defer**, "no paid GPU or expanded docking campaign") **stands and is not
  circumvented**: this step buys no GPU, adds no docking, and produces no binding, degradation or
  window statement.

## 4 · The bounded step taken

`per_frame_rsa_overlap.py` (stdlib + `multiprocessing`, $0, read-only outside this directory)
imports `nr4a_differential_atlas.parse_pdb / shrake_rupley / residue_rsa` and
`nr4a_paralogue_dynamics.construct_frame / cysteines_of / quantiles` **unchanged**, walks
`results/nr4a3-pocket-reharmonize`, `results/nr4a1-pocket-ensemble`, `results/nr4a2-pocket-ensemble`
→ `release_rep{0,1,2}/*/frame.pdb` (25 frames × 3 replicas × 3 species = **225 frames**), and writes
`artifacts/per-frame-rsa-overlap.json` — every frame, every cysteine, one RSA each (225 rows,
18 species·cysteine series).

### 4a · Validation — the committed quantile block reproduces exactly

**432 statistics compared, 0 mismatches.** Every `n / min / p10 / median / p90 / max / mean / sd`
cell of `term_a.by_species[*].ensembles[release_rep*].summary[*].rsa` in
`research/modalities/nr4a-paralogue-dynamics.json` is recovered to the committed 4-dp value from the
frames. The manuscript's quoted ceiling is also confirmed **by attribution**: **0.2126** is exactly
`NR4A1 C465`'s maximum over its 75 unbiased frames, which is the residue §2.10 names. The first
round's per-replica ceilings reproduce digit for digit (**0.1737** NR4A2 C534 @ `fp_21_release_rep0`;
**0.1940** NR4A2 C534 @ `fp_0_release_rep1`; **0.2126** NR4A1 C465 @ `fp_74_release_rep2`), as do its
C551 maxima (**0.0907 / 0.1333 / 0.1201**). **Nothing in the prior chain failed to reproduce.**

### 4b · Result — the separation is now exact, and it is not "no overlap"

Paralogue reference set = **all 825** NR4A1/NR4A2 cysteine·frame observations (11 cysteines × 75
frames).

| | C397 | C420 | C559 |
|---|---|---|---|
| frames strictly above the **pooled** ceiling 0.2126 | **72 / 75 (0.96)** | 30 / 75 (0.40) | 6 / 75 (0.08) |
| exact pairwise dominance vs the 825 paralogue observations | **0.9993** | 0.9818 | 0.9563 |
| pooled RSA min / p10 / median / max | 0.1082 / 0.2981 / 0.4156 / 0.6725 | 0.0641 / 0.1021 / 0.1863 / 0.4510 | 0.0398 / 0.0772 / 0.1324 / 0.2896 |

Per replica, against **that replica's own** paralogue ceiling:

| replica | ceiling (residue) | C397 above | C420 above | C559 above |
|---|---|---|---|---|
| release_rep0 | 0.1737 (NR4A2 C534) | **23/25 (0.92)** | 23/25 (0.92) | 3/25 (0.12) |
| release_rep1 | 0.1940 (NR4A2 C534) | **25/25 (1.00)** | 4/25 (0.16) | 1/25 (0.04) |
| release_rep2 | 0.2126 (NR4A1 C465) | **25/25 (1.00)** | 7/25 (0.28) | 4/25 (0.16) |

1. **"No overlap" is falsified, with an exact count.** Three NR4A3 C397 frames sit **at or below** the
   pooled paralogue ceiling — `release_rep0/fp_41_xmzapaw0` **0.1082**, `fp_37_h9k263rg` **0.1617**,
   `fp_99_az0_ci9r` **0.1870**, all below 0.2126. The defensible statement is **96 % of C397 frames
   (72/75)** are more exposed than *any* paralogue cysteine in *any* frame, with **pairwise dominance
   0.9993** — a strong separation, but a fractional one, and all three exceptions are in one replica.
2. **The frame-level statement survives the replicate split in the direction that matters**: 0.92,
   1.00, 1.00. The worst cross-replica pairing is **C397 @ rep0 against the rep1 or rep2 ceiling:
   0.88 (22/25)**. This *replaces* the first round's quantile-derived "worst-case cross-replica p10
   margin −0.0138", which was an interpolation artefact of comparing p10 to a max; at frame level the
   worst pairing is a clean 0.88, not a sign flip. **This is a correction of a reading, not of a
   number** — the first round's −0.0138 arithmetic is reproducible from its inputs; it is the
   quantile-vs-max comparison that the exact count supersedes.
3. **C420 is confirmed replica-dependent, and more sharply than before.** Its frame fraction above
   the local ceiling is **0.92 / 0.16 / 0.28** across replicas — a ~6× spread on the same quantity.
   The first round's "single-replica effect, should not be quoted" holds at frame level. C559 never
   rises above 0.16 in any replica.
4. **The `V17` positive control fails in every frame, not merely in the median.** NR4A1 **C551**
   exceeds its own replica's paralogue ceiling in **0/25, 0/25, 0/25** frames (max 0.0907 / 0.1333 /
   0.1201). No exposure cutoff placed above the paralogue ceiling can retain the one NR4A-family
   covalent site with literature support. The failure is exhaustively reproducible, not a pooling or
   quantile accident.
5. **A quiet asymmetry the pooled read hides:** the paralogue ceiling is a *maximum over 275
   observations per replica* and rises monotonically with sampling (0.1737 → 0.1940 → 0.2126 across
   replicas), while C397's frame fraction is a bounded proportion. Any future statement of the form
   "no paralogue cysteine exceeds X" therefore **weakens with more sampling by construction**; the
   pairwise-dominance figure (0.9993) is the sampling-stable version of the same comparison and is
   the one this lane recommends quoting.

**Artifact** `artifacts/per-frame-rsa-overlap.json` (225 per-frame rows, the validation block, the
per-replica / pooled / cross-replica overlap tables, the C551 control) + the script.
**Validation / baseline** 432 published quantile statistics recomputed from primary conformers, 0
mismatches; the manuscript's 0.2126 confirmed as NR4A1 C465's exact per-residue maximum; the first
round's per-replica ceilings and C551 maxima reproduced digit for digit.
**Provenance** `results/nr4a{3-pocket-reharmonize,1-pocket-ensemble,2-pocket-ensemble}/release_rep{0,1,2}/*/frame.pdb`
(committed conformers), validated against `research/modalities/nr4a-paralogue-dynamics.json`. Same
Shrake-Rupley (n_points=96) / Tien max-ASA routine, hydrogens kept, single-chain parser — the
committed convention, unmodified.
**Limitations** (a) RSA is geometric: **nothing here bears on thiol pKa, nucleophilicity, adduct
stability, promiscuity, degradation, cellular selectivity, efficacy, safety, therapeutic window or
clinical readiness, and there is no wet lab**; (b) release ensembles are biased-CV-released MD, not
Boltzmann-weighted — frame fractions are heterogeneity statements, not populations; (c) 25 frames per
species per replica, so a 0.92 is 23/25 and its uncertainty is wide; (d) replica indices are not
physically paired across species, hence the explicit cross-replica block; (e) the `metad` subset and
the 8XTT experimental ensemble were **not** re-derived here; (f) this qualifies a *reading* and
retracts nothing — the 12-atom gate is carried by reach, not exposure.
**Stop condition** met: the exact overlap is computed and the published quantiles are reproduced.
This lane stops here. It does **not** re-open the `C7` cutoff, the chemoproteomics route, any
free-energy construct, or the deferred degrader-optimisation prospect.

## 5 · Proposed prose qualifier — UNAPPLIED, no shared file edited

For the paper owner, where §2.10 states the pooled ceiling (exact wording is the owner's):

> Read per frame rather than per quantile, C397's RSA exceeds the maximum RSA of every NR4A1/NR4A2
> cysteine in every unbiased frame in **72 of 75** frames (pairwise dominance 0.9993 against 825
> paralogue cysteine·frame observations); the three exceptions lie in `release_rep0`. Per replica the
> fraction is 0.92 / 1.00 / 1.00, and the worst cross-replica pairing is 0.88. C420 clears the same
> ceiling in 0.92 / 0.16 / 0.28 of frames and its exposure advantage should not be quoted. Because the
> paralogue ceiling is a maximum that grows with sampling, the dominance fraction rather than the
> ceiling is the sampling-stable statement.

## 6 · Compute and storage actually used

One CPU run, 4 worker processes, **2 m 45 s wall / 6 m 40 s user**, no GPU, no network, no paid API,
$0. Output written: **132 KiB** total in this lane directory (artifact 106 KiB). No repo copy, no
worktree, nothing written outside
`.../PORTFOLIO-INVESTIGATIONS-2026-09-08/DEGRADER-2/`. No `git add`/`commit`/`push`, no preflight,
no subagents.

## 7 · Next credible independent work (not started)

The remaining exposure question that data in this checkout **cannot** answer is the one already
recorded: covalent ligandability has **no known-answer reference** here
(`cys-chemoproteomics-precheck.json`, `STOP_NO_REFERENCE`, proxy-blocked tables). A dominance
fraction of 0.9993 is a geometric ranking statement and is **not** evidence of selective labelling.
The one further $0 CPU step that would add information is a per-frame RSA export of the **`metad`**
and **8XTT** subsets on the same footing, to state whether the biased and experimental ensembles put
any paralogue cysteine above C397 at frame level; it is bounded, but it is a refinement, not a
resolution of the missing reference.
