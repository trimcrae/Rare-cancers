---
id: DOC-PORTFOLIO-INVESTIGATION-EXPR-HYPOXIA-1-2026-09-09
title: "EXPR-HYPOXIA-1 — a frozen 16-gene HIF-target score attenuates the two-platform EMC expression contrast further and beyond the generic label-matched baseline; the composition-adjusted residual does not survive it"
level: L4
kind: investigation
status: live
date: 2026-09-09
last_verified: 2026-09-09
lane: EXPR-HYPOXIA-1
continues: EXPR-COMPOSITION
assessed_baseline_from: ASSESS-EXPR-COMPOSITION
campaign: OPUS-CAPACITY-CAMPAIGN-20260908
---

# EXPR-HYPOXIA-1 — is the residual EMC expression contrast a hypoxia programme?

Writes confined to this directory. No `git add`/`commit`/`push`, no `preflight.sh`, no subagent,
no worktree, no repo copy, no network, no GPU, no paid API, no shared-file edit. Repository read in
place; lane footprint **1 MB**; free disk 9196 MB at finish (9522 MB before the run, 3954 MB at
lane start — no large write was made and no scratch was left).

## 1 · Question

DISCOVERY-2 proposal 3, executed as specified: **is the residual EMC cross-platform expression
contrast that survives EXPR-COMPOSITION's tumour/stroma adjustment a hypoxia programme?**

## 2 · Merit

KINASE-2's 65.2 % two-platform direction concordance is what the expression arm leans on when it
says a gene is "higher in EMC on both platforms". EXPR-COMPOSITION showed a frozen 20-marker
tumour/stroma score removes about half the excess, and ASSESS-EXPR-COMPOSITION showed about half of
*that* is generic covariate shrinkage, leaving a composition-specific share nearer 0.27. What
remained was a residual nobody had characterised. Naming a second, mechanistically distinct
per-sample programme that explains it — or failing to, cleanly — tells the arm's owners how much of
the contrast is tumour-microenvironmental state rather than lineage biology. Attainable at $0 from
data already committed.

## 3 · Evidence gap this closes, and what distinguishes it from prior work

EXPR-COMPOSITION adjusted for **one** covariate (cell-type marker abundance) and explicitly left the
residual uncharacterised; its nulls randomise the label or the score, never a *second real
per-sample programme*. The missing input was a hypoxia covariate measurable on the same samples.
`research/modalities/emc-hypoxia-null-background.json` — untouched by every lane so far — carries,
for both series, per-sample `array_percentile` for 118 named confound genes including a full
HIF-target/glycolysis panel, **and** a seeded (`_sample_seed` 20260807) random background universe
that excludes those 118 names by construction. That is a purpose-built null universe for exactly
this control, and no lane had opened it.

## 4 · Step taken

A rank-based partial-association re-analysis of exactly EXPR-COMPOSITION's two frames, with the
hypoxia gene list, the value channel, the **missingness rule**, the control design and the stop
condition frozen in `PREREGISTRATION.md` (sha256 `39827cc8…`, pinned in the script and stamped into
the artifact) **before any statistic was read**. The only earlier reads were input hashes and the
JSON key structure (`checks/01`, `checks/02` — neither contains an association of any kind).

* **Hypoxia score `H`** = per-sample mean `array_percentile` over the frozen HIF-target /
  glycolytic-effector set. **Reported separately, not scored:** the oxygen-sensing regulators
  (`HIF1A, EPAS1, ARNT, VHL, HIF1AN, EGLN1/2` — mRNA is a poor hypoxia readout) and a **vascular
  score `V`** (13 endothelial/angiogenic genes).
* **Missingness, decided before computing.** ASSESS-EXPR-COMPOSITION showed a NaN-skipping score has
  a sample-dependent marker set on GPL3290. **This lane does not NaN-skip.** A gene enters a score
  only if it is present on *every* labelled sample of *both* platforms — complete-case **gene**
  selection, so the score is one fixed definition on both platforms. **16 of 22** hypoxia genes
  survive; the 6 dropped are named in the artifact (`CA9`, `HK2`, `SLC16A1`, `SLC2A3` missing on one
  GPL3290 sample each; `PKM`, `SLC16A3` not measured on GPL3290 at all). 10 of 13 vascular genes
  survive. **The loss of `CA9` and `SLC16A3`, the two most hypoxia-specific members, is a real
  weakening of the score and is stated as such.**
* Statistics are EXPR-COMPOSITION's: Spearman gene–label association, first-order rank partial
  correlation for one covariate, **second-order** for the two-covariate `C + H`.

### Ordering, honoured

1. **The gate ran first and gated everything** (`checks/04` stdout, lines 1–7). Using
   EXPR-COMPOSITION's own committed machinery on the same input, **6/6 comparisons, 0 mismatches,
   to 1e-9**: primary 434 genes, 0.6521 → **0.5668**; secondary 413 genes, 0.6368 → **0.5981**.
   The script exits **3** and computes no hypoxia statistic on any mismatch.
2. Then the covariates, under the frozen missingness rule; fewer than 8 surviving genes exits **4**.
3. Then the seeded-random-background control and the generic baseline, before any reading was formed.
4. Then `H`, `V` and `C + H` on both frames. **Stop.**

## 5 · ⭐ Result — this is **not** a null

**`H` is associated with the EMC label in the same direction on both platforms, and the EMC arms
score HIGHER on it** (Spearman(`H`, EMC) **+0.413** GPL6244, **+0.840** GPL3290; arm means 0.876 vs
0.824 and 0.533 vs 0.256). The composition score ran the other way (−0.578 / −0.504), and `H`
correlates **negatively** with `C` (−0.396 / −0.615): a sample high on the marker score is low on
the HIF-target score. The vascular score `V` tracks `C`, not `H` (−0.518 / −0.224).

| primary frame, 434 genes paired across all six variants | rate | change | attenuation of the excess over 0.5 |
|---|---|---|---|
| unadjusted | 0.6567 | — | — |
| composition `C` | 0.5691 | −0.088 | 0.56 |
| **hypoxia `H`** | **0.5184** | **−0.138** | **0.88** |
| vascular `V` | 0.6336 | −0.023 | 0.15 |
| **`C` + `H` (two-covariate)** | **0.4885** | −0.168 | **1.07** |
| `C` + `V` | 0.5829 | −0.074 | 0.47 |

Secondary frame (413 genes): unadjusted 0.6368; `C` 0.5956 (0.30); **`H` 0.5182 (0.87)**; `V` 0.6174
(0.14); **`C`+`H` 0.5133 (0.90)**. **Both frames agree.**

**The seeded random background does not reproduce it.** 300 shams, each the mean `array_percentile`
of 16 background genes per platform drawn from the file's seeded universe (which excludes all 118
named genes) through identical machinery: mean adjusted rate **0.6166** (sd 0.0285, min 0.5276) —
i.e. a **small generic drop of 0.040** from 0.6567, nothing like `H`'s 0.138, and **0 of 300**
shams reach `H`.

**`H` beats the generic label-matched baseline, which is the test that matters.** Following
ASSESS-EXPR-COMPOSITION's decomposition — adjusted rate regressed on the covariate's own mean
|Spearman(cov, label)|; slope −0.131, r = −0.70 — the generic prediction at `H`'s label correlation
(0.627) is **0.5758**, against an observed **0.5184**: `H` beats generic by **0.057**. In matched
bands: **0 of 14** (±0.05, one-sided p = 0.067), **0 of 28** (±0.10, p = 0.034), **0 of 47** (±0.15,
p = 0.021). *Internal consistency check on the same regression*: at `C`'s label correlation it
predicts **0.587** for the composition score, against ASSESS-EXPR-COMPOSITION's independently
derived **0.6077** — same conclusion, different route, and the difference is disclosed below.

**Abundance-matched sensitivity control** (`checks/05`) — the important one, because glycolytic
genes are high-abundance while uniform shams are mid-range, so a mean of high-percentile genes could
track an array's dynamic range rather than hypoxia. 300 shams matched gene-by-gene on mean
`array_percentile` (sham mean abundance 0.631 vs `H`'s 0.833/0.429): sham mean 0.6134, **1 of 300**
reaches `H`; generic prediction 0.5732 vs observed 0.5184; matched bands **1/17 (p = 0.111)**,
1/41 (p = 0.048), 1/65 (p = 0.030). **The claim survives but weakens: at the tightest matched band
it is no longer significant at 0.05.** That band has 17 members, so p cannot go below 0.056.

### Reading, stated at the strength the evidence supports

A frozen HIF-target/glycolysis score, measured per sample on the same two series, **removes ~0.88 of
the excess concordance on the primary frame and ~0.87 on the secondary — more than the
tumour/stroma score removes, and more than any of 300 seeded-background shams matched on label
correlation.** Jointly with `C` it drives the primary-frame rate to 0.4885, i.e. **to and slightly
past chance**: on these data the composition-adjusted residual does **not** survive further
adjustment for `H`. That is a positive-association outcome under the preregistration's §8, not a
null. **It licenses no biological conclusion.** The `C + H` figure crossing below 0.5 is itself a
warning that two correlated covariates on 6 and 10 EMC samples over-adjust; the honest statement is
"nothing distinguishable from chance remains", not "hypoxia explains EMC".

## 6 · Artifact · validation · provenance · limitations · stop condition

**Artifact.** `hypoxia-residual-attribution.json` (12 KB) — the gate record; the covariate
definitions with every dropped gene and its reason; label associations and arm means for `H`, `V`,
`C`; per-frame rates and attenuations for all six variants; the seeded-random-background control
with its generic label-matched baseline and matched bands; and the abundance-matched control.
**Generators.** `hypoxia_residual_attribution.py`, `abundance_matched_sham.py`, `inspect_inputs.py`,
`inspect2.py`. **Prereg.** `PREREGISTRATION.md`, sha256 `39827cc8…`, verified by the script at run
time (mismatch exits 5).

**Validation.** (1) The gate, 6/6 to 1e-9, run first, hard exit 3 — `checks/04`. (2) The seeded
random background does not attenuate materially (0/300 reach `H`). (3) The generic label-matched
baseline, ASSESS-EXPR-COMPOSITION's own falsifier, applied to `H`. (4) The abundance-matched sham,
which the brief did not require and which is the strongest available alternative explanation.
(5) Two independent frames, two different data paths into the same series, same answer.
(6) Cross-lane consistency: my sham regression reproduces ASSESS's generic prediction for `C` to
0.02 by an independent implementation and a different covariate pool.

**Preserved failed attempt.** `checks/03` (**exit 1**, `TypeError` in `np.polyfit`) — the first full
run passed the gate and produced every frame statistic, then died in the control because shams were
filtered for complete-case *after* drawing, so **0 of 300** draws survived on GPL3290. Its stdout,
stderr and exit code are kept unedited; `checks/04` is the rerun after pre-filtering the universe.
No statistic was changed to make it pass.

**Provenance.** `research/modalities/emc-hypoxia-null-background.json`, 7,975,969 B, sha256
`e6b583e5…`, committed `14a3f172` 2026-09-04, `_generated_utc` 2026-08-07, read read-only.
`research/modalities/emc-expression-panels.json`, 13,254,759 B, **re-hashed at use**: sha256
`59bccb55…` — **byte-identical to the version EXPR-COMPOSITION recorded**, so despite the
2026-09-08 23:23 working-tree mtime the *content* read here is the same version that produced
0.6521 → 0.5668, and `git status` was clean for it. EXPR-COMPOSITION's artifact and its module read
read-only. Runtime 5.3 s + 6 s, single core, stdlib + numpy.

**Limitations — these bound the result hard.**
- **`H` is not a measured oxygen tension.** It is 16 transcripts in undeconvolved bulk archival
  tissue. Every glycolytic member is also a proliferation, MYC, PI3K/AKT and mitochondrial-content
  readout; `PGK1`, `ENO1`, `ALDOA`, `GPI`, `TPI1` are as much "glycolytic rate" as "hypoxia". The
  two most hypoxia-*specific* members, `CA9` and `SLC16A3`, are exactly the ones the missingness
  rule dropped. **"Hypoxia programme" here means the frozen §2 score and nothing more.**
- **The abundance-matched control is the honest ceiling on the claim**: at the tightest matched band
  1 of 17 shams reaches `H` (p = 0.111). The claim is significant at the ±0.10 and ±0.15 bands and
  not at ±0.05, and 17 members cannot give p < 0.056. More draws is the obvious strengthening and
  was not run.
- **`H` and `C` are not independent** (r = −0.40 / −0.61) and both correlate strongly with the
  label. A second-order partial correlation with n = 16 on GPL3290 and two label-tracking covariates
  is unstable and over-adjusts by construction; the `C + H` rate falling *below* 0.5 is direct
  evidence of that, not evidence of anti-concordance.
- **Confound and covariate are not separable, even in principle.** Hypoxia, necrosis, cellularity,
  proliferation and comparator diagnosis mix co-vary in these blocks. `H` may be a proxy for the
  comparator mix (LGFMS / desmoid / fibrosarcoma / DFSP / GIST) rather than for tumour oxygenation;
  nothing here distinguishes those.
- **Platform asymmetry.** GPL3290 is a two-colour log-ratio platform; `array_percentile` is
  comparable across platforms by construction but is a *within-array rank*, not a level. The
  complete-case filter cut the GPL3290 sham universe from 3,971 to **2,316** genes, so shams there
  are drawn from the better-measured half of the array — a bias whose direction is not established.
- The unadjusted baseline in §5's table (0.6567) differs from the gated 0.6521 by **2 genes of 434**
  whose near-zero rank correlation falls the other side of zero under the residualisation
  arithmetic. Every row of that table uses one implementation, so its comparisons are like with
  like, but attenuations are reported to 2 significant figures for exactly this reason.
- **No label-permutation p is reported for `H`.** The lane stopped at its declared stop condition;
  the covariate-sham control was the preregistered inferential comparison.
- Small arms (6 and 10 EMC), no multiple-testing correction, no deconvolution, no third series, no
  protein, no oxygen measurement, no drug response.
- ⛔ **Nothing here establishes efficacy, safety, selectivity, a therapeutic window, target
  attribution or clinical readiness for any agent in any disease, and nothing here is advice about
  a patient.** The attenuation is **an association in owned expression data and nothing more.**

**Stop condition (preregistered §9).** Stop when `H`, `V`, `C + H` and the seeded-background control
are computed on the primary and secondary frames. **Met.** No third frame, no new series, no
per-gene lead re-ranking, no downstream text.

## 7 · What this owes EXPR-COMPOSITION and KINASE-2 (not applied — shared files)

EXPR-COMPOSITION §8 item 1 asked for further covariate sensitivity; this supplies a *different*
programme instead, and the answer is that the composition-adjusted residual it reported does not
survive a frozen HIF-target score on either frame. Any prose citing either the 65.2 % concordance or
the surviving composition-adjusted residual as evidence of a coherent EMC *biological* contrast
should carry that qualification. **No shared file is edited and no diff is proposed**; the
downstream text belongs to the owners of `EXPR-COMPOSITION/FINDING.md`, `KINASE-2/FINDING.md` and
the `PUB-KINASE-LEADS` endpoint.

## 8 · Next credible independent work (not done, not authorised here)

1. **Extend the abundance-matched sham to ~3,000 draws** — the single cheapest strengthening; the
   ±0.05 band is the binding constraint and it currently holds 17 members.
2. A **stratified** rather than covariate-adjusted contrast over the `H` overlap region between
   arms, which would show whether the `C + H` result is an extrapolation artefact.
3. A hypoxia score restricted to the **specific** members (`CA9`, `SLC16A3`, `EGLN3`, `PDK1`) on
   GPL6244 alone, where they are complete, as a specificity probe against the glycolysis/
   proliferation reading.
4. A **third series**, which still does more for this arm than any further reanalysis of these two.
