---
id: DOC-BIOMARKER-DEP-3-FINDING-20260909
title: "BIOMARKER-DEP-3 — the rest arm re-derived: what the missing denominator does and does not cost, quantity by quantity"
level: L4
kind: investigation-finding
status: live
date: 2026-09-09
last_verified: 2026-09-09
lane: BIOMARKER-DEP-3
campaign: OPUS-CAPACITY-CAMPAIGN-20260908
parents: [PUB-BIOMARKER-DEP, BIOMARKER-DEP-2]
siblings_read: [DEP-THRESHOLD, PUB-SYNLETH]
---

# BIOMARKER-DEP-3

⛔ **No wet lab. No EMC observation. Nothing here is an efficacy, safety, selectivity,
therapeutic-window or clinical-readiness claim, and none may be read out of it.** No network, no
GPU, no paid API, no publication, no outreach. The `CRISPRGeneEffect` per-line fetch — the parents'
open gap — was **not attempted**; it is outside worker authority. Every write is inside this
directory; both shared-file changes are **unapplied** diffs.

## 1 · The question

BIOMARKER-DEP-2 reported two things about the DepMap transfer panel's **rest (non-sarcoma) arm**:
that PUB-BIOMARKER-DEP's `p = 0.084` does not reproduce as stated, and that the arm's denominator is
recorded nowhere while **1126** values are consistent with the published fractions. **Do both claims
survive independent re-derivation from the underlying artifact — and if so, which published
quantities in this paper family still carry uncertainty that can be bounded, and which are bare
point estimates?**

## 2 · Merit rationale

Patient relevance is the parents' indirect but real one: in a disease under one case per million per
year, which therapeutic classes stay on the board is decided by transferred dependency evidence, and
`depmap-sarcoma-dependency.json` grades every route in this portfolio that touches DepMap. The
contribution is non-trivial and it is **instrument**, not conclusion: nobody has yet said, per
quantity, which numbers this family prints are descriptions and which are estimates. Attainable —
every figure below is arithmetic on committed values, no fetch and no spend.

## 3 · The evidence gap

Not the missing per-line matrix. The gap here is that a defect named in one sentence by a sibling was
never (a) independently checked, or (b) propagated to the quantities it actually threatens. Both
parents named `rest_frac_dependent` as suspect; neither said what could still be claimed about it.

## 4 · Re-derivation — BOTH prior claims, before relying on either

Producer `rest_arm_audit.py`, artifact `rest-arm-audit.json`, `checks/03`, exit 0. Sole scientific
input `research/modalities/depmap-sarcoma-dependency.json`, read-only. Fisher is exact by full
hypergeometric enumeration; the two-sided implementation is cross-checked against
`scipy.stats.fisher_exact` and agrees to 6 dp.

### 4.1 · Claim (b) — the 1126 admissible denominators: **REPRODUCES EXACTLY**

Searching every integer in [2, 2105], the denominators consistent with **all 67 rounded
`rest_frac_dependent` values simultaneously** number **1126**, spanning **943 to 2105** — identical
to BIOMARKER-DEP-2, by an independently written admissibility test. 37 of the 1163 integers in that
range are excluded. The denominator is recorded nowhere in the panel artifact. ⭑ **New:** both
candidate denominators are admissible — the producer's `2105 − 91 = 2014` **and** the
panel-implied `1178 − 91 = 1087` (1178 is the `nr4a_paralogue_comparison` block's own `n_lines`).

### 4.2 · Claim (a) — the `p = 0.084` statement: **reproduces, with TWO corrections to how it was described**

| route | table | exact two-sided p |
|---|---|---|
| **A** producer's own route, `n_rest = n_models_total − n_sarcoma = 2105 − 91 = 2014` | [[1, 4], [34, 1980]] | **0.083803** → **0.0838**, the value stored in `transfer-calibration.json`, printed as 0.084 |
| **B** against the **sarcoma** arm (1/5 vs 2/91) | [[1, 4], [2, 89]] | **0.149741** |
| **C** envelope over all 1126 admissible rest denominators | — | **min 0.083170, max 0.088644** |
| **D** panel-implied `n_rest = 1178 − 91 = 1087` | [[1, 4], [18, 1069]] | **0.084170** |

One-sided (greater) equals two-sided to 6 dp on every one of these tables, so the sibling's
one-sided implementation and the producer's two-sided `scipy` call do not disagree.

**Correction 1 — the assumption is not "unrecorded", it is recorded in the producer.**
BIOMARKER-DEP-2 wrote that the p reproduces "only under an assumption about that arm's size that
**the artifact does not record**". The assumption is written explicitly in
`PUB-BIOMARKER-DEP/transfer_calibration.py` lines 125–129, which build the rest row as
`round(rest_frac_dependent × (n_models_total − n_pan))`. It is absent from the panel JSON, from
`transfer-calibration.json` and from the prose — which is the real defect, and is what the diff
fixes — but "recorded nowhere" is too strong by one file.

**Correction 2 — 0.0867 to 0.0847 is not the span.** BIOMARKER-DEP-2 reported the range as
"**0.0867 (n = 943) to 0.0847 (n = 2105)**". Both endpoint values are right (0.086680 and 0.084734
here), but **p is not monotone in n**: the true envelope over the 1126 admissible denominators is
**[0.083170, 0.088644]**, wider at both ends. **321** of the 1126 admissible denominators round to
0.084.

**So the published figure is defensible and the honest fix is restatement, not withdrawal.** The
0.084 is arithmetically exact on the route its own producer took, and the reading it supports —
"the control does not come out at 0.99 power" — is unchanged across the whole 0.0832–0.0886
envelope, and unchanged again at the more plausible `n_rest = 1087`. What was wrong is the
*description*: the comparison arm was not named, and the denominator assumption was not stated
anywhere a reader of the finding or the JSON could see it.

## 5 · The per-quantity supportability table

**Sampling model, stated once.** DepMap's screened lines are a convenience panel, not a random
sample of any population. So there are two distinct readings and they must not be conflated:

* **descriptive** — "of the lines the panel screened, this fraction fell below −0.5". Assumption-
  free. The only uncertainty is the 3-dp rounding, ±0.0005, and it does **not** depend on N.
* **inferential** — a CI, an SE or a test. Requires N, and requires an i.i.d. binomial model that
  this panel does not license. The "CI envelope" column below is the union of exact
  Clopper–Pearson intervals over the admissible N; it is a **conditional** bound — valid only if one
  grants the binomial model — and is reported so the cost of the missing N is visible, not as an
  endorsement of that model.

### 5.1 · Quantities that depend on the rest arm

Artifact for rows 1–6: `research/modalities/depmap-sarcoma-dependency.json`.

| # | quantity | published | key | interval placeable? | tightest bound placeable |
|---|---|---|---|---|---|
| 1 | EWSR1 `rest_frac_dependent` — **PUB-SYNLETH's headline** | **0.915** | `fusion_addiction_proxy/EWSR1_overall.rest_frac_dependent` | descriptive yes; inferential **no** | descriptive **[0.9145, 0.9155]**; implied dependent count **863–1926**; conditional CI envelope **[0.8955, 0.9322]** |
| 2 | MCL1 `rest_frac_dependent` — **decisive for §2.5** | **0.696** | `genes_by_group/Apoptotic guardians (BH3)/MCL1.rest_frac_dependent` | descriptive yes; inferential **no** | **[0.6955, 0.6965]**; count **656–1465**; conditional CI **[0.6652, 0.7249]** |
| 3 | BCL2L1 `rest_frac_dependent` — **decisive for §2.5** | **0.854** | `genes_by_group/Apoptotic guardians (BH3)/BCL2L1.rest_frac_dependent` | descriptive yes; inferential **no** | **[0.8535, 0.8545]**; count **805–1798**; conditional CI **[0.8295, 0.8756]** |
| 4 | BRD9 `rest_frac_dependent` — the Fisher background | **0.017** | `genes_by_group/ncBAF (primary hypothesis)/BRD9.rest_frac_dependent` | descriptive yes; inferential **no** | **[0.0165, 0.0175]**; count **16–36**; conditional CI **[0.0097, 0.0274]** |
| 5 | FLI1 `rest_frac_dependent` | **0.019** | `fusion_addiction_proxy/FLI1_overall.rest_frac_dependent` | descriptive yes; inferential **no** | **[0.0185, 0.0195]**; count **18–40**; conditional CI **[0.0114, 0.0300]** |
| 6 | NR4A3 `rest_frac_dependent` — the H1 safety prior | **0.000** | `fusion_addiction_proxy/NR4A3_overall.rest_frac_dependent` | descriptive yes; inferential **no** | count is **exactly 0** at every admissible N; conditional one-sided CI **[0, 0.0039]** |
| 7 | every `rest_mean` (61 genes; e.g. EWSR1 **−0.835**, MCL1 **−0.787**, BCL2L1 **−1.076**) | see artifact | `<group>/<gene>.rest_mean` | **no, under any reading** | **none.** No SD, no quantiles, no per-line values **and** no N: neither an SE nor a distribution-free bound exists. ⭑ **A bare point estimate with no placeable uncertainty at all.** |
| 8 | every `selectivity` = `rest_mean − sarcoma_mean` (e.g. EWSR1 **+0.373**, FLI1 **+0.242**) | see artifact | `<group>/<gene>.selectivity` | **no, under any reading** | **none.** Double blocker: no dispersion on *either* arm, and no N on the rest arm. ⭑ **Bare point estimate.** |
| 9 | Fisher p, BRD9-in-synovial vs the rest arm | **0.084** (stored 0.0838) | `PUB-BIOMARKER-DEP/transfer-calibration.json → stated_positive_controls[0].fisher_p_vs_rest_panel`; prose at `PUB-BIOMARKER-DEP/FINDING.md:65` | **bracketable** | **[0.083170, 0.088644]** over all 1126 admissible N; 0.084170 at the panel-implied N = 1087 |

**The ones that are point estimates with no placeable uncertainty at all: rows 7 and 8 — every
`rest_mean` and every `selectivity` in the panel, 61 genes each.** Rows 1–6 are pinned to ±0.0005 as
*descriptions of the screened panel* and carry no defensible interval as *estimates*; row 9 is the
only rest-arm quantity that can be bracketed end to end from held data.

### 5.2 · Quantities that do NOT depend on the rest arm — still supportable as printed

`n_sarcoma` = **91** on every record (and 91 is the unique denominator under 100 consistent with all
67 rounded sarcoma fractions); every `sarcoma_frac_dependent`; the pan-essential trap counts
**23 records / 22 genes** at `rest_frac ≥ 0.80` and **30 / 29** at ≥ 0.20 (threshold comparisons on
recorded numbers, denominator-free); **67 records over 64 genes**; BRD9-in-synovial **1 of 5**,
Wilson **0.036–0.624**; the exact power figures **0.9925** (n = 5, p₁ = 0.8) and **0.9094**
(p₁ = 0.6) and **min n = 3**, all computed against the *sarcoma* background; and the sarcoma-arm
Fisher **0.1497**. None of these moves with N.

## 6 · The diffs — UNAPPLIED

### 6.1 · `fisher-p-denominator-restatement.diff` — the primary fix. `git apply --check` **exit 0** (`checks/05`)

Three files under `PUB-BIOMARKER-DEP/`, so that the number is not left live anywhere it is printed:

1. `FINDING.md` finding 3 — names the comparison (**against the rest arm, not the sarcoma arm**),
   states the assumed denominator and its arithmetic, prints the sarcoma-arm value **0.1497** so the
   two cannot be confused, and gives the 1126-denominator envelope **[0.0832, 0.0886]** and the
   panel-implied **0.0842**.
2. `transfer_calibration.py` — emits `fisher_comparison`, `fisher_n_rest_assumed` (2014) and
   `fisher_n_rest_provenance` beside the p-value, so the assumption travels with the number.
3. `transfer-calibration.json` — the same three keys, at the value the patched producer emits.

**Withdrawal was considered and rejected**: the figure is arithmetically exact on its own route and
its direction is stable across every admissible denominator, so restatement is the honest fix.

### 6.2 · `biomarker-dep-2-span-correction.diff` — the sibling's two mis-descriptions. `git apply --check` **exit 0** (`checks/07`)

`BIOMARKER-DEP-2/FINDING.md` §4.2 plus the matching `_comment` strings in
`rederive_prior_numbers.py` and `prior-number-rederivation.json`: the assumption **is** recorded in
the producer, and 0.0867–0.0847 are endpoints, not the span. **No numeric value in that lane's
artifact is changed** — its two stored p-values are correct at the denominators they name.

### 6.3 · Every site where this figure is live — complete census

| file:line | text | in a diff? |
|---|---|---|
| `.../PUB-BIOMARKER-DEP/FINDING.md:65` | "Fisher *p* = 0.084 against the non-sarcoma background" | ✅ 6.1 |
| `.../PUB-BIOMARKER-DEP/transfer-calibration.json` → `stated_positive_controls[0].fisher_p_vs_rest_panel` | `0.0838` | ✅ 6.1 (value kept, provenance added) |
| `.../PUB-BIOMARKER-DEP/transfer_calibration.py:125–129` | the computation | ✅ 6.1 |
| `.../BIOMARKER-DEP-2/FINDING.md:84` | "does not reproduce as stated … 0.0867 … 0.0847" | ✅ 6.2 |
| `.../BIOMARKER-DEP-2/rederive_prior_numbers.py:87` and `prior-number-rederivation.json:146` | the `_comment` | ✅ 6.2 |

⭐ **The figure never reached a manuscript.** Grepped across `research/manuscripts/`,
`research/manuscripts/pinned-figures.json`, `systems/` and the campaign tree: **no manuscript, no
pinned figure and no generated artifact prints this Fisher p.** `PUB-BIOMARKER-DEP/FINDING.md` §4.5
already says "**No manuscript edit was made and none is proposed here**". The two other `0.084`
hits in dependency manuscripts are unrelated quantities — `emc-dnapk-nr4a3-lane-assessment.md:258`
(a Δ-distribution mean) and `emc-atr-vulnerability-assessment.md:579` (a MYC-targets contrast) —
and the second `0.084` inside `PUB-BIOMARKER-DEP/FINDING.md:73` is the Gaussian-reconstructed BRD9
fraction, a different number that coincidentally rounds the same; **neither is touched.**

## 7 · Artifact · validation · provenance · limitations · stop condition

**Artifact.** `rest-arm-audit.json`, producer `rest_arm_audit.py`, and the two unapplied diffs.

**Validation / baseline.** Baseline is the committed panel and the two sibling lanes' own reported
numbers. (i) Claim (b) reproduces exactly — 1126, [943, 2105] — by an independently written test.
(ii) Claim (a) reproduces on route A and is corrected in two named respects. (iii) The two-sided
Fisher implementation agrees with `scipy.stats.fisher_exact` to 6 dp on the route-A table.
(iv) `checks/04`, exit 0: the **patched** producer was executed and its output compared to the
committed `transfer-calibration.json` — with only the three added keys stripped, the regenerated
artifact is **identical**, so the diff moves **no published value**. (v) Both diffs `git apply
--check` at **exit 0**.

**Provenance.** `research/modalities/depmap-sarcoma-dependency.json` (DepMap public 24Q4, figshare,
`CRISPRGeneEffect.csv` + `Model.csv`, per its own `data_source`), read-only. Sibling artifacts read
only to quote the claims under test. **No shared file was modified**: all edits were made on copies
in the session scratchpad and the diffs generated from them; `git status` shows this lane's
directory and nothing else of mine.

**Every execution attempt is under `checks/` with its real exit code, including the three failures:**
`01` (redirect paths resolved under the lane directory, exit 1), `02` (the direct binomial-tail
Clopper–Pearson overflowed at n ≈ 2000 — `OverflowError: int too large to convert to float` — exit
1; replaced by the beta-quantile identity), `06` (`git apply --check` run from the scratchpad rather
than the repository root, exit 1).

**Limitations.** ⛔ No EMC observation; no efficacy, safety, selectivity, therapeutic-window or
clinical-readiness claim, and no new scientific claim of any kind — every number here re-describes
values already committed. The conditional CI envelopes in §5.1 assume an i.i.d. binomial model this
panel does not license and are reported as a cost accounting, not as intervals anyone should quote.
The descriptive ±0.0005 brackets are statements about the **screened panel**, not about any
population of tumours or patients. Which of 2014 and 1087 is the true rest denominator is **not**
settled here and cannot be settled without the per-line matrix. The admissibility search is bounded
at 2105 because no rest arm can exceed the release's model count; denominators above that are not
excluded by argument, only by that bound. The producer was not re-run against fresh DepMap data.

**Stop condition — reached.** Both prior claims were re-derived (one exact, one correct-with-two-
corrections), the per-quantity audit is complete, and both diffs apply at exit 0. **Do not iterate
further on this p-value.** The next credible step is unchanged and is not this lane's to take: the
owner applies (or declines) the diffs, and the per-line `CRISPRGeneEffect` fetch on the standing
networked route replaces every conditional bound in §5.1 with a real distribution — which would
also settle 2014 versus 1087 in one pass.
