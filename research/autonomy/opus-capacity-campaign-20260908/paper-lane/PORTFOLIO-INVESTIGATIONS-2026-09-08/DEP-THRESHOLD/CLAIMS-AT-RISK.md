---
id: DOC-DEP-THRESHOLD-CLAIMS-AT-RISK
title: "DEP-THRESHOLD — claims at risk from the -0.5 cut and from selectivity read without its complement"
level: L4
kind: claims-audit
status: live
date: 2026-09-09
last_verified: 2026-09-09
lane: DEP-THRESHOLD
campaign: OPUS-CAPACITY-CAMPAIGN-20260908
---

# CLAIMS AT RISK

Every row names an actual sentence in a live manuscript, the retained quantity it rests on, and
this lane's verdict. Line numbers are as of 2026-09-09 on branch `claude/confident-bardeen-ji76cd`.
**No manuscript was edited.** Evidence: `threshold-sensitivity.json`, sections A–E.

Verdict vocabulary:

* **SURVIVES (threshold-invariant)** — the quantity is a difference of means; the cut does not enter
  its definition, so no cut can move it.
* **SURVIVES (one-sided monotone)** — a binary verdict that can only move in the direction that
  would strengthen it, so the published reading is safe.
* **WEAKENS** — the quantity is a margin between two fractions, unstable to a cut change in both
  directions, and section C shows the retained summaries cannot bound it usefully at any other cut.
* **UNCHECKABLE** — the sentence's truth at any cut other than −0.5 cannot be evaluated from the
  committed artifact at all.
* **NEW DEFECT** — the sentence is not wrong about its number but reads a mean shift as a window.

---

## A · `research/manuscripts/dependency/degrader-vs-synthetic-lethal.md` (PUB-SYNLETH)

| # | line(s) | the sentence | rests on | verdict |
|---|---|---|---|---|
| A1 | 156–159 | "**ncBAF is not a sarcoma dependency.** BRD9 mean gene effect in sarcoma is **+0.105** (non-essential; 2.2% of the 91 screened lines dependent) … BRD9 selectivity is −0.016, i.e. none." | `sarcoma_mean`, `selectivity` (invariant); `sarcoma_frac_dependent = 0.022` at −0.5 | **SURVIVES.** The mean and the selectivity are threshold-invariant. The 2.2% is one-sided monotone in the *protective* direction: at any **stricter** cut it can only fall (bound at t=−1.0: sarcoma_frac ∈ [0, 0.022], Δfrac ∈ [−0.017, 0.022]). A **looser** cut could raise it, but a looser cut is not what "not a dependency" needs. |
| A2 | 160–162 | "Not supported even in the closest FET-fusion analog… BRD9 is **+0.134, 0% dependent**" (Ewing, n=27) | subtype block `mean_gene_effect`, `frac_dependent` at −0.5 | **SURVIVES.** The mean is invariant and *positive* (the wrong sign for a dependency at any cut ≤ 0). 0/27 dependent can only stay 0 under a stricter cut. This remains the standing measurement, as PUB-SYNLETH found. |
| A3 | 163–165 | "**BET/CDK targets give no selectivity window.** BRD4 (−0.954), CDK7 (−1.847), CDK9 (−1.464) … selectivities −0.018, +0.085, +0.017 — pan-essential, not a therapeutic margin." | `selectivity` (invariant) **and** `rest_frac_dependent` = 0.952 / 0.999 / 0.994 | **SURVIVES, and is the correct template.** This is the only place in either paper where a selectivity is already read beside its complement. Both halves point the same way. |
| A4 | 166–172 | "NR4A3 is +0.021 in sarcoma with 0% of the 91 screened lines dependent, and its selectivity is +0.002" | invariant mean + selectivity; `frac = 0.0` | **SURVIVES**, on the same one-sided argument as A1. |
| A5 | 173–178 | "**Pipeline mechanics validated** by correct recovery of the pan-essential controls (CDK7/BRD4/CDK9, ~100% dependent everywhere)." | `sarcoma_frac_dependent`/`rest_frac_dependent` ≈ 1.0 at −0.5 | **UNCHECKABLE in the strict direction.** "~100% dependent" is monotone-safe only under a **looser** cut. At t = −1.0 the artifact bounds CDK7's sarcoma fraction only to **[0.28, 1.00]** — the pan-essentiality of the validation control cannot be re-verified at the canonical common-essential depth (−1.0) from what is retained. The verdict is not shown to be wrong; it is shown to be uncheckable off the one published cut. |
| A6 | 178–182 | "The one control that could have validated selectivity detection — BRD9 in synovial sarcoma — did not recover it (n=5, −0.130, 20% dependent, i.e. 1 line of 5). So the headline negative … should be read as a weak prior against BRD9." | subtype `frac_dependent` at −0.5, n=5 | **WEAKENS — and this is the converged defect.** The failure of this control is entirely a property of where −0.5 falls: the synovial mean of −0.13 is a −0.235 shift in the expected direction that sits 0.37 units on the non-dependent side of the cut (PUB-BIOMARKER-DEP finding 4). The binarised control is validated by nothing, and section A here shows **its value at any other cut is not computable**. The memo's hedge is right; its stated reason is not the operative one. |
| A7 | 213–219 | "**Verdict.** The DepMap transfer prior came back negative … the 'test an existing BRD9 degrader first' shortcut is therefore **no longer justified by transfer logic**." | A1 + A2 + A6 | **SURVIVES, on A2 rather than on A6.** The route re-weighting is carried by the Ewing subtype read (n=27, +0.134, 0% dependent), which is threshold-safe in the direction that matters and is a direct subtype measurement. It is **not** carried by the pan-sarcoma statistic (dilution-limited, PUB-SYNLETH) nor by the synovial control (cut-limited, A6). Same conclusion, different and narrower support. |
| A8 | 141–143, 184 | "is BRD9 / BRD4 / CDK9 / EP300 / SMARCA4 *selectively* essential …" / "**Interpretation.** The cheap transfer prior does **not** support BRD9/ncBAF (or selective BET/CDK) as an EMC vulnerability." | `selectivity` used as the operational definition of "selectively essential" | **NEW DEFECT (definitional).** `selectivity` is a shift of means and is 0.72-correlated (Spearman, n=64) with the actual dependent-fraction margin Δfrac — not 1.0. The memo never states that "selective" here means "the arm means differ", not "one arm is dependent and the other is not". EWSR1 is the proof: **largest selectivity in the whole panel (+0.373) and a margin of 0.052**, because 91.5% of non-sarcoma lines are already dependent. |
| A9 | — (absent) | EWSR1 is read in `fusion_addiction_proxy` and its selectivity is never reported in the memo. | `EWSR1_overall` | **MISSING SAFEGUARD.** The panel's single largest selectivity belongs to a gene that is a dependency in 96.7% of sarcoma **and 91.5% of everything else**. Any future reader ranking this panel by selectivity meets EWSR1 first. The memo should carry the trap warning explicitly. |

## B · `research/manuscripts/dependency/emc-biomarker-selected-classes.md` (PUB-BIOMARKER-DEP)

| # | line(s) | the sentence | rests on | verdict |
|---|---|---|---|---|
| B1 | 235–237 | "On the dependency axis, **MCL1 and BCL2L1 are dependencies in the large majority of sarcoma lines.** That is a statement about the tissue class, not about EMC, and a near-universal dependency argues against selectivity rather than for it." | `sarcoma_frac_dependent` = 0.835 (MCL1), 0.758 (BCL2L1) at −0.5 — **the only support** | **WEAKENS (uncheckable).** "Large majority" is one-sided monotone: it survives any **looser** cut and is unverifiable under a stricter one. At the canonical common-essential depth t = −1.0 the artifact bounds MCL1's sarcoma fraction only to **[0.003, 0.835]** and BCL2L1's to **[0.000, 0.758]** — i.e. "large majority" at −1.0 is consistent with the retained data but so is "almost none". The *anti-selectivity* half of the sentence is stronger than the paper claims and does not depend on the cut at all: `rest_frac_dependent` is 0.696 (MCL1) and 0.854 (BCL2L1), so both are **caught by the pan-essential trap** and BCL2L1's mean shift actually runs the *wrong* way (selectivity −0.200, Δfrac −0.096). The conclusion holds; the stated evidence for it is the weaker of the two available. |
| B2 | 134–135 | Standing rule: "a near-universal dependency is evidence *against* selectivity, not for it." | `frac_dependent` at −0.5, generically | **SURVIVES as a rule, but it is applied to the wrong arm.** As written it looks at `sarcoma_frac_dependent`. The quantity that makes a dependency "near-universal" for the purpose of a therapeutic window is **`rest_frac_dependent`** — the arm the agent would also hit. 29 of 64 gene records in the panel carry `rest_frac_dependent ≥ 0.20`; 22 carry ≥ 0.80. The rule should be restated on the complement. |
| B3 | 117–123 | "Where the question was not whether the feature is present but whether hitting the target would be selective, the sarcoma-line CRISPR dependency panel was read instead." | the panel as an instrument | **NEW DEFECT (instrument disclosure).** The paper does not state which statistic in the panel answers "would hitting the target be selective", and the two candidates disagree in rank (Spearman 0.72; EWSR1 moves rank 1 → 7, PSMB5 3 → 11, XRCC5 6 → 19, CDK7 8 → 25, WEE1 9 → 28, EP300 15 → 49). The paper should name the statistic and report it beside `rest_frac_dependent`. |
| B4 | 118–122 | "That panel contains no EMC line … Every dependency figure here is therefore a transfer from other sarcomas, and the honest bound is not a small sample but no observation in this disease at all." | — | **SURVIVES, unaffected.** Not a threshold claim. It is correct and is the strongest caveat in either paper. |
| B5 | 218–233 | The whole abundance argument of §2.5 (five guardians lower in EMC; NOXA higher on GPL3290; "the one class that stays open") | `emc-expression-panels.json`, not the CRISPR panel | **NEVER THRESHOLD-DEPENDENT.** No part of this touches `depmap-sarcoma-dependency.json`. Unaffected in either direction. |
| B6 | 241–248 | §3 "Claims not made" — no exclusion of any class, not a substitute for the named assays | — | **SURVIVES, unaffected.** |

## C · What is at risk in the artifact itself

| # | object | verdict |
|---|---|---|
| C1 | `research/modalities/depmap_sarcoma_dependency.py` `stats()` | **RETAINS NO DISPERSION.** Fields kept per gene: `gene`, `sarcoma_mean`, `rest_mean`, `selectivity`, `sarcoma_frac_dependent`, `rest_frac_dependent`, `n_sarcoma`. No SD, no quantile, no order statistic, no per-line value. Consequence: **the route-decision statistic cannot be checked at any cut other than the one it was published at**, from the artifact it was published in. |
| C2 | `self_validation._pass_criterion` | Written as "clearly more-negative `mean_gene_effect` / high `frac_dependent`". The two halves can disagree (that is exactly the BRD9-in-synovial case: mean shifts the right way, fraction does not), and the criterion does not say which governs. It was never adjudicated. |
| C3 | `nr4a_paralogue_comparison` | The **only** block in the artifact that retains order statistics (`median_gene_effect`, `min_gene_effect`), giving three exact threshold points per paralogue instead of one. It is pan-panel, so it cannot enter a selectivity sweep — but it is the existing in-repo precedent for what the other records should retain. |
