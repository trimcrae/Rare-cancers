---
id: DOC-OPUS-CAMPAIGN-PORTFOLIO-THRESHOLD-CALIB-1-FINDING
title: "THRESHOLD-CALIB-1 — the class I threshold cannot be calibrated on held data: the cached predictor calls and the IEDB validated arms are disjoint, and the missing 1,125 calls are enumerated"
level: L4
kind: investigation-finding
status: live
date: 2026-09-09
last_verified: 2026-09-09
---

# THRESHOLD-CALIB-1 — a decisive negative, with the exact missing predictor-call set

Writes confined to this directory. Nothing added, committed or pushed; `scripts/preflight.sh` not
run; no manuscript, graph entry, producer, guard, gate, pin or test touched; no subagents; no GPU,
no paid API, no install, no re-scoring, no network fetch attempted; cost $0. No `grep -r`. Inputs
read in place and never copied; retained output 216 KiB.

⛔ **No immunogenicity, presentation, tolerance, efficacy, safety, selectivity, therapeutic-window
or clinical-readiness claim is made or implied, in either direction.** A predicted percentile or
IC50 is a number returned by a program; it is not a presented epitope. "Discrimination" below is a
property of an instrument on labelled records, and nothing else.

⛔ **HLA-C stayed excluded.** Route B8 is closed. The 34-allele panel carries no HLA-C locus
(asserted in code); the 100 arm-F and 383 arm-N HLA-C pairs were counted and dropped, never
relabelled or substituted, and no HLA-C data was acquired.

Settled inputs taken as given and not reopened: validated set **n = 15**; the correct Wilson figure
is **34**, not 37; EPITOPE-BENCHMARK-3's pin correction accepted.

## 1 · The question

`emc-vaccine-development-path.md` §6.1 step 1 says the class I acceptance threshold must be
defended or recorded as undefendable, and PUB-VACCINE-PATH established that the reading was never
taken. The arm-F collector has since succeeded — `iedb-validated-epitope-cache.json` now holds 988
arm-F and 965 arm-N validated records. So:

> **On the peptide/allele set where the repository's cached predictor calls and the IEDB validated
> arms overlap, what is the discrimination of the repository's class I threshold — and if that set
> is empty, exactly which predictor calls are missing?**

## 2 · Merit

The cut is load-bearing for the whole antigen-directed route: the manuscript's coverage reads 0% at
0.2 and 30.4% at 0.5, and all four presenting-allele calls sit inside a 0.0844-percentile-unit
window. A route graded "low coverage" on an unvalidated convention is graded on the instrument, not
the biology. The contribution here is non-trivial and does not need a specimen: either the threshold
gets a measured sensitivity/specificity on validated records, or the *reason* it cannot is pinned to
an exact, purchasable list of predictor calls rather than to a generic "not measured". Patient
relevance is indirect and honest — it decides whether a route is dismissed on a convention.

## 3 · The exact evidence gap, distinguished from prior work

PUB-VACCINE-PATH left arm F at **n = 0** (a collector defect) and computed sample-size arithmetic,
not discrimination. VACCINE-PATH-2, EPITOPE-BENCHMARK, -2 and -3 settled the *literature census*
(n = 15) and the *Wilson figure* (34) — a count of validated epitopes, never a scored one.
**Nobody has yet asked whether the predictor calls the repository actually holds name any validated
record at all.** That is the gap, and it is answerable entirely offline from two committed files.

Inputs, re-hashed at use inside the run (`provenance` block of the artifact):

| file | bytes | sha256 (16) |
|---|---|---|
| `research/modalities/iedb-validated-epitope-cache.json` | 433,695 | `122009e5615fb3f0…` |
| `research/modalities/epitope-allele-matrix-mhcnuggets.json` | 588,303 | `e9a248b28d77cbd6…` |
| `research/modalities/epitope-allele-matrix.json` (MHCflurry, secondary) | 1,517 | `24da5269b71a2d2b…` |

## 4 · The step taken, and the result

`threshold_calibration.py` → `threshold-calibration.json`.

### 4.1 ⚠ The two sets are disjoint. The discrimination is UNDEFINED, not chance and not zero.

| | arm F (fusion-junction) | arm N (non-fusion) | cached calls |
|---|---|---|---|
| records / calls | 988 | 965 | 5,916 |
| distinct peptides | 549 | 675 | 174 |
| distinct pairs on the 34-allele panel | 652 | 473 | 5,916 |
| HLA-C pairs excluded (B8 closed) | 100 | 383 | 0 (no HLA-C on panel) |
| **peptides shared with the cached calls** | **0** | **0** | — |
| **(peptide, allele) pairs shared** | **0** | **0** | — |

Alleles overlap almost completely (33 of 34 in each arm); **peptides do not overlap at all.** The
cached matrix scores only the 174 EMC junction-window peptides. Not one experimentally validated
IEDB peptide carries a cached call, so the threshold has **never been scored on a single validated
record**. With `n_positive = 0` the instrument returns `auroc = null`, `sensitivity = null`,
`specificity = null` — recorded as **undefined**, and explicitly not as chance and not as zero.

### 4.2 The zero is not a match-rule artifact, and no intersection was manufactured

Matching is exact on (peptide, allele) after whitespace/case normalisation only; no rule was
loosened, no substring or partial-allele matching was used. Both sets are plain uppercase 8–11mers
on the same allele nomenclature. As an independent probe, the **minimum edit distance between any
cached peptide and any validated peptide is 4** (`AAVEWFDD` vs `AALFFFDID`) — the peptide sets are
genuinely disjoint, not misformatted.

### 4.3 A second, independent obstacle: the scales do not match either

Even a non-empty overlap would not have calibrated the manuscript's cut. The load-bearing threshold
is a **MHCflurry presentation percentile of 0.5**; the only full per-call matrix in the tree is on
the **MHCnuggets IC50 (nM)** scale, and `epitope-allele-matrix.json` retains only the 5 passing
calls, not the 174 × 34 percentile matrix. This is recorded in the artifact rather than papered
over: the two predictors are never merged.

### 4.4 The check that had to be able to fail — and does

The instrument was validated on **synthetic, seeded, biologically meaningless** labels, existing
only to show it can separate and can be destroyed:

* rank AUROC equals its O(n·m) definition, ties included, over 40 random draws — **PASS**
* synthetic positive control: **AUROC 0.9939**, sensitivity 0.9900, specificity 0.9100 — **PASS**
* label-shuffled null, 2,000 shuffles: mean **0.49835**, 95% band **[0.44122, 0.55505]** →
  **AT CHANCE** — **PASS**
* the same chance criterion, with the shuffle *removed* (`checks/02-`, a mutation test): mean
  0.99390 → **NOT AT CHANCE**. The criterion is not inert; it can fail — **PASS**
* the empty real overlap returns undefined, and its null reports "fewer than two label classes; a
  null cannot be drawn" rather than 0.5 — **PASS**

Had the shuffled null not come out at chance, the reported result would have been that the
instrument is wrong. It did come out at chance, so the reported result is §4.1.

### 4.5 The deliverable: the exact missing predictor-call set

**1,125 predictor calls**, enumerated pair by pair in the artifact
(`missing_predictor_call_set.arm_F_pairs`, `.arm_N_pairs`):

* **arm F — 652 calls** (fusion-junction validated records × panel alleles): the only arm §B1
  permits to settle the cut.
* **arm N — 473 calls** (non-fusion validated records): the comparator §B1 refuses, listed so the
  refused calibration is costed too, never to be quoted as the calibration.
* Restricted to the 34-allele panel, HLA-C excluded, lengths 8–11 only.
* Required on **both** predictors and never merged: MHCnuggets IC50 to extend the cached matrix,
  and — for the cut the manuscript actually uses — the MHCflurry presentation percentile whose full
  matrix is not retained.
* **Positives alone are not enough.** A decoy/negative set under a preregistered rule is still
  required; without negatives, specificity and AUROC stay undefined however many positives get
  scored. Arm D of the original run is the existing decoy machinery to reuse.

Blocked here because MHCnuggets is not installed, its weights are a large download, and this lane is
forbidden to install or re-score. No network fetch was attempted.

## 5 · Artifact · validation · provenance · limitations · stop condition

* **Artifact.** `threshold-calibration.json` (98 KB), `threshold_calibration.py`,
  `mutation_test.py`, `check_artifact_integrity.py`, `checks/` — 3 attempts, all preserved, all
  exit 0.
* **Validation / baseline.** The instrument passes a definitional self-test, a synthetic positive
  control, a 2,000-run label-shuffled null at chance, and a mutation test proving the chance
  criterion can fail. `checks/03-` re-verifies the artifact: counts consistent, every allele on
  panel, no HLA-C, every peptide an 8–11mer, pairs unique, no discrimination reported anywhere, and
  all three provenance hashes still current against the inputs in place.
* **Provenance.** The three files in §3, hashed inside the run at the moment of use.
  `research/modalities/vaccine-threshold-calibration.json` (run 2026-09-01T20:31:04Z) for the
  conventional cut of 0.5 and the arm definitions; `vaccine_threshold_calibration.py` @ HEAD for the
  arm-F/arm-N inclusion rule. Nothing external was ingested.
* **Limitations.** ⛔ No claim about any peptide, tumour or patient. The disjointness is a statement
  about two committed files as they stand today, not about what a re-run would find. Arm F's records
  are validated on **other fusions in other diseases**, so even once scored they bound the
  instrument, not EMC biology. The circularity the original run flagged still holds — MHCflurry is
  trained on IEDB, so any future sensitivity on these records is an **upper bound**. The synthetic
  control validates the instrument only; it carries no biological content and must never be quoted
  as a result. The 1,125-call figure is the *minimum* positive-side cost; the negative set is extra
  and unpriced here.
* **Stop condition.** Stopped at the no-install / no-re-scoring fence, with the blocker converted
  from "unmeasured" into an exact enumerated purchase order. This lane does not dispatch CI, does
  not commit, and does not edit any tracked file.

## 6 · Next credible independent work (not done here, not authorised here)

1. Score the enumerated 652 arm-F pairs on the CPU runner that already reaches PyPI — MHCnuggets
   install plus weights is the whole dependency, and the pair list is committed here so no fetch of
   IEDB is repeated.
2. Retain the **full** MHCflurry percentile matrix, not only its passing calls, or the manuscript's
   own 0.5 cut can never be calibrated on the same scale it is applied on.
3. Preregister the decoy rule before scoring, and read the result against PUB-VACCINE-PATH §4(c)
   sample sizes (93 epitopes at sensitivity 0.5 for a ±0.10 CI), not against `min_n = 30`.
