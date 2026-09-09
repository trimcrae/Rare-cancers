---
id: DOC-DEP-THRESHOLD-FINDING-20260909
title: "DEP-THRESHOLD — the route-decision statistic cannot be checked from the artifact it is published in"
level: L4
kind: investigation-finding
status: live
date: 2026-09-09
last_verified: 2026-09-09
lane: DEP-THRESHOLD
campaign: OPUS-CAPACITY-CAMPAIGN-20260908
serves: [PUB-SYNLETH, PUB-BIOMARKER-DEP]
---

# DEP-THRESHOLD — how much of the panel's published structure is an artifact of the −0.5 cut

Sole input, read-only: `research/modalities/depmap-sarcoma-dependency.json` (DepMap public 24Q4)
and its producer `research/modalities/depmap_sarcoma_dependency.py`. **The producer was not
re-run. No network, no GPU, no paid compute, no new data.** The per-line `CRISPRGeneEffect`
matrix — the fix both parent lanes named — needs egress that is proxy-refused here and was
deliberately **not** attempted.

⛔ Nothing here is an EMC measurement. No DepMap line in this panel is EMC. No efficacy, safety,
selectivity or therapeutic-window claim is made or implied for either route.

## 1 · The question

Two lanes converged on one defect. PUB-BIOMARKER-DEP: sample size is *not* the limitation
(power 0.99 at n=5 for a dependency in 80% of a subtype), the **readout** is — the synovial mean of
−0.13 against the panel's +0.105 is a real −0.235 shift whose mean sits 0.37 units on the
non-dependent side of the −0.5 cut, and that cut is validated by nothing. PUB-SYNLETH: the panel's
**largest** selectivity (EWSR1, +0.373) belongs to a gene that is a dependency in 96.7% of sarcoma
**and 91.5% of everything else**. So: **how much of the panel's published structure is an artifact
of the −0.5 binarisation, and of reading selectivity without its complement?**

## 2 · The decisive result — the sweep does not exist, and that is the finding

**A threshold sweep of `frac_dependent` is not computable from this artifact.** The producer's
`stats()` retains, per gene, exactly: `gene`, `sarcoma_mean`, `rest_mean`, `selectivity`,
`sarcoma_frac_dependent`, `rest_frac_dependent`, `n_sarcoma`. **No SD, no quantile, no order
statistic, no per-line value** — machine-checked across all 64 gene records carrying the
sarcoma/rest split (`threshold-sensitivity.json` §A). A fraction at any cut other than −0.5 is a
functional of a distribution the producer discards.

Exactly which thresholds *are* computable, and from what:

| record class | exactly computable thresholds | why |
|---|---|---|
| all 64 sarcoma/rest gene records | **t = −0.5 only** | one fraction per arm at one fixed cut, plus a mean |
| every subtype block (`self_validation`, `BRD9_by_fusion_sarcoma_subtype`, `FLI1_in_ewing`) | **t = −0.5 only** | mean + one fraction + n |
| `nr4a_paralogue_comparison` (NR4A1/2/3) | **three points each**: P(X<t)=0 for t ≤ `min_gene_effect`; P(X<`median_gene_effect`)=0.5; the recorded value at −0.5 | the only block retaining order statistics — **and it is pan-panel, so it cannot enter a selectivity sweep** |

I did not manufacture a distribution to get more. Where a point value is unrecoverable, a rigorous
interval still is, so I computed the **exact distribution-free range** of P(X < t) over every
distribution on an assumed Chronos-scale support [L, U] consistent with the retained mean and the
one retained fraction (derivation in `bounds_frac()`; three supports reported so the assumption's
influence is visible). Result, at the default support [−4.0, +1.5]:

| t | Δfrac fully determined | of which exactly 0 | determined **non-zero** | undetermined | median Δfrac bound width |
|---|---|---|---|---|---|
| −2.0 … −0.75 | 5 | 5 | **0** | 59 | 0.267 |
| **−0.5 (published)** | 64 | 8 | 56 | 0 | 0.000 |
| −0.25 … +0.25 | 3 | 3 | **0** | 61 | 1.22 – 1.66 |

**At every threshold except the published one, the number of genes whose sarcoma-vs-rest dependent
fraction can be given a determined non-zero value is zero** — under all three supports. The bounds
are not merely loose; for the genes the two papers argue from they are close to vacuous:
MCL1's sarcoma fraction at t = −1.0 is bounded only to **[0.003, 0.835]**, BCL2L1's to
**[0.000, 0.758]**, and CDK7's — the pan-essential validation control — only to **[0.28, 1.00]**.

**So the published route-decision statistic cannot be checked from the artifact it is published in.**
That is the answer to the lane's question, and per the task's stop condition it is itself the
decisive result. **The producer should retain dispersion** (§6).

## 3 · What the cut can and cannot have distorted

The threshold audit splits the panel's quantities cleanly, and the split is not the one either
parent lane assumed.

**Threshold-INVARIANT, by construction — nothing to check.** `sarcoma_mean`, `rest_mean` and
`selectivity = rest_mean − sarcoma_mean` are arithmetic means over all lines in each arm; the cut
does not enter their definition. **Every gene's selectivity value, its sign, and the complete
selectivity rank order are therefore exactly stable under any threshold — trivially, not
empirically. No selectivity rank can flip.** This matters: the −0.5 cut is *not* the source of the
EWSR1 artifact. That artifact is an **interpretation** defect (reading a mean shift as a window),
not a binarisation defect. They are two different failures needing two different repairs.

**One-sided monotone — safe in exactly one direction.** P(X < t) is non-decreasing in t. So a
"pan-essential" verdict (frac ≈ 1; 18 of 64 records at frac ≥ 0.90 in sarcoma) survives any
**looser** cut and is unverifiable under a stricter one; a "not a dependency" verdict (frac ≈ 0;
31 of 64) survives any **stricter** cut and is unverifiable under a looser one. Both of the
memo's headline nulls — BRD9 at 2.2% and NR4A3 at 0% — fall in the protected direction.

**Stable in NEITHER direction — and this is where both papers argue.** Δfrac, the difference of two
fractions, is the actual dependent-fraction margin. It is monotone in neither direction, and §2
shows the retained summaries cannot bound it usefully at any other cut. Every "margin",
"selectivity window" and "large majority vs. the rest" reading in either paper is this quantity.

## 4 · The corrected reading — selectivity beside `rest_frac_dependent`

Full table in `threshold-sensitivity.json` §D and printed in `checks/03/stdout.txt`. Headlines:

* **22 of 64 gene records are caught by the EWSR1/CDK7/CDK9 pan-essential trap** (`rest_frac_dependent`
  ≥ 0.80 — a near-universal dependency *outside* sarcoma, so any selectivity is a change in the
  depth of an essentiality both arms already have, not a margin). 29 of 64 carry
  `rest_frac_dependent` ≥ 0.20. The trapped set: EWSR1, PSMB5, XRCC5, ATR, CDK7, WEE1, CDK9,
  PRMT5, XRCC6, CDK12, BRD4, HDAC3, PSMB1, VCP, CDC37, PSMD14, HSPA5, PSMC1, PSMD1, SMARCB1,
  BCL2L1, MAT2A.
* **The two statistics disagree in rank: Spearman 0.72, not 1.0** (n = 64). Reading the panel by
  selectivity rather than by margin moves **EWSR1 from rank 1 to rank 7** (selectivity +0.373,
  Δfrac 0.052), **PSMB5 3 → 11**, **XRCC5 6 → 19**, **ATR 7 → 15**, **CDK7 8 → 25**,
  **WEE1 9 → 28** (Δfrac exactly 0.000), **EP300 15 → 49** (Δfrac *negative*, −0.022).
* **The one gene that ranks top by both is FLI1** — rank 2 by selectivity (+0.242), rank 1 by
  margin (Δfrac +0.201, `rest_frac_dependent` 0.019, clear of the trap). PUB-SYNLETH's positive
  control survives the corrected reading intact and is the panel's only clean selective dependency.
* **Both BH3 guardians §2.5 argues from are trapped**: MCL1 (`rest_frac` 0.696,
  MAJORITY_ESSENTIAL_OUTSIDE_SARCOMA) and BCL2L1 (`rest_frac` 0.854, PAN_ESSENTIAL_TRAP, and its
  mean shift runs the *wrong* way at selectivity −0.200).
* **PRMT5 and MAT2A are trapped** (`rest_frac` 0.941 and 0.989) — relevant to any future
  MTAP/PRMT5 reading of this panel, though no sentence audited here rests on it.
* **BRD9 is clear of the trap** (`rest_frac` 0.017), so its null is a genuine null, not a masked
  window.

## 5 · Which claims survive — the plain statement

Full sentence-level table with line numbers in `CLAIMS-AT-RISK.md`. In summary:

**Survive, and were never threshold-dependent at all.** Everything resting on a mean or on
selectivity: the BRD9 pan-sarcoma mean (+0.105) and selectivity (−0.016); the NR4A3 null (+0.021,
+0.002); the BRD4/CDK7/CDK9 pan-essentiality verdict (the one place the memo already reads
selectivity beside `rest_frac_dependent`, and both halves agree); the entire abundance argument of
the biomarker paper's §2.5, which never touches this panel; and the "no EMC line, so this is a
transfer" caveat, which is the strongest sentence in either paper.

**Survives on a narrower support than stated.** The memo's §3 route re-weighting away from the
cheap BRD9 test. It is carried by the **Ewing subtype read (n=27, +0.134, 0% dependent)** — a
positive mean, the wrong sign for a dependency at any cut, and 0/27 that a stricter cut cannot
raise. It is **not** carried by the pan-sarcoma statistic (dilution-limited at k=5, PUB-SYNLETH)
nor by the synovial control (cut-limited, below). Same conclusion, narrower and different support.

**Weakens.** (a) The memo's synovial self-validation failure, §2b lines 178–182 — the control's
failure is a property of where −0.5 falls relative to a real −0.235 shift, and its value at any
other cut is not computable. (b) The biomarker paper's §2.5 line 235, "MCL1 and BCL2L1 are
dependencies in the large majority of sarcoma lines" — one-sided safe under a looser cut only, and
at t = −1.0 the retained data are equally consistent with "almost none". Its *conclusion* (a
near-universal dependency argues against selectivity) is in fact **stronger** than the paper claims,
because the decisive evidence is `rest_frac_dependent` (0.696, 0.854), which the sentence does not
use.

**New defects, not previously named.** (a) The memo's operational definition of "selectively
essential" is a shift of means, correlated 0.72 with the margin it is read as — stated nowhere.
(b) The biomarker paper's standing rule "a near-universal dependency is evidence against
selectivity" is applied to `sarcoma_frac_dependent` when the quantity that makes a dependency
near-universal *for a window* is `rest_frac_dependent`. (c) EWSR1's selectivity is the largest in
the panel and appears in neither paper; any reader ranking this panel by selectivity meets it first.

**Uncheckable.** The memo's "pipeline mechanics validated by ~100% dependent everywhere"
(CDK7/BRD4/CDK9). Monotone-safe only under a looser cut; at the canonical common-essential depth
t = −1.0 the artifact bounds CDK7's sarcoma fraction only to [0.28, 1.00]. Not shown wrong — shown
unverifiable off the published cut.

## 6 · Artifact · validation · provenance · limitations · stop condition

* **Artifact** — `threshold-sensitivity.json` (sections A–E) and its generator
  `threshold_sensitivity.py`, plus `CLAIMS-AT-RISK.md`. All in this directory. Deterministic; reads
  one committed file; writes one JSON; fetches nothing.
* **Validation** — three internal checks, all passing and all recorded in the artifact:
  (i) fraction integrality, 64/64 (`sarcoma_frac_dependent × n_sarcoma` integral, confirming the
  common 91-line denominator); (ii) the bound formula returns the recorded point exactly at
  t = −0.5 (64/64 determined, zero width) — a necessary condition it would fail if the derivation
  were wrong; (iii) support sensitivity — the "zero determined non-zero Δfrac off −0.5" result is
  identical under [−3, 1], [−4, 1.5] and [−6, 2], so it is not an artifact of the assumed support.
* **Provenance** — `research/modalities/depmap-sarcoma-dependency.json`, DepMap public release 24Q4
  (figshare) `CRISPRGeneEffect.csv` + `Model.csv`, per its own `data_source`. Statistic definitions
  read from `depmap_sarcoma_dependency.py` `stats()`. `checks/01`–`03` hold every execution attempt
  with command, stdout, stderr and real exit code.
* **Limitations** — ⛔ **No EMC observation of any kind**; no efficacy, safety, selectivity,
  therapeutic-window or clinical claim for either route. The BRD9 Ewing subtype read (n=27, 0%
  dependent) is a direct subtype measurement and stands unchanged. The support [L, U] is a **stated
  assumption**, not a retained field; it is reported three ways and the headline result is invariant
  to it, but the bounds themselves are not assumption-free. The bounds are worst-case over all
  consistent distributions, so they are conservative by construction — a real distribution would be
  narrower, but the artifact does not retain which one. Spearman 0.72 is computed over
  hypothesis-selected genes, not a random gene set. Nothing here re-opens the dilution/power
  question the two parent lanes already settled.
* **Stop condition — reached.** The question was how much published structure is threshold artifact.
  Answer: selectivity, none (invariant by construction); the binary verdicts, one-sided only; the
  margins both papers argue from, **unverifiable at any cut but the published one**. This cannot be
  improved by further analysis of the same summaries. **Do not spend more cycles sweeping this
  artifact** — there is nothing to sweep.

## 7 · The one producer change this implies — proposed, NOT applied

I made **no edit outside this directory** and prepared no diff to a shared file. The concrete
change the evidence supports, for the owner to decide:

`depmap_sarcoma_dependency.py` `stats()` should retain **dispersion or order statistics per arm** —
at minimum `sd`, and preferably the quartiles and `min`, exactly as the `nr4a_paralogue_comparison`
block already does for the three paralogues. That block is the in-repo precedent: it retains
`median_gene_effect` and `min_gene_effect` and consequently supports three exact threshold points
instead of one. Extending the same retention to the sarcoma/rest records would make every future
threshold question answerable from the committed artifact without a re-fetch. Adding
`n_dependent_lines` per arm (also already present in the NR4A block) would additionally make the
counts explicit rather than back-computed from rounded fractions.

The larger fix both parent lanes named — the per-line `CRISPRGeneEffect` matrix — remains the
correct one and remains out of scope here: it needs network egress, which is proxy-refused in this
sandbox, and this lane may not commit, push or dispatch.
