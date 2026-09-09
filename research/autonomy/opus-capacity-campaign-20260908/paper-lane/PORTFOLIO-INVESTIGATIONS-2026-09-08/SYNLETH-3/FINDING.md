---
id: DOC-SYNLETH-3-FINDING-20260909
title: "SYNLETH-3 — BAK1 and EGFR are undecidable for proximity, not for rounding or denominator; nothing that would decide them exists, and nothing published depends on them"
level: L4
kind: investigation-finding
status: live
date: 2026-09-09
last_verified: 2026-09-09
lane: SYNLETH-3
campaign: OPUS-CAPACITY-CAMPAIGN-20260908
parents: [PUB-SYNLETH, SYNLETH-2]
siblings_read: [PUB-SYNLETH, SYNLETH-2, DEP-THRESHOLD, BIOMARKER-DEP-2, BIOMARKER-DEP-3]
---

# SYNLETH-3

⛔ No wet lab. No EMC observation of any kind. **Nothing here is an efficacy, safety,
therapeutic-selectivity, therapeutic-window or clinical-readiness claim, and none may be read out of
it.** `rest_frac_dependent` and `selectivity` are **screen statistics on a public CRISPR panel**, not
therapeutic properties. No network, no direct HTTP egress, **no attempt at the per-line
`CRISPRGeneEffect.csv` fetch** (the parents' open gap, outside worker authority), no producer re-run,
no GPU, no paid API, no publication, no outreach, no `git add/commit/push`, no `preflight.sh`, no
subagent. Every write is inside this directory. **No shared file was touched and no diff was needed.**

## 1 · The question

SYNLETH-2 decided the ≥ 0.80 pan-essential-trap screen completely at the worst admissible
denominator, but left one honest negative: **the secondary ≥ 0.20 screen is undecidable for BAK1
(0.187) and EGFR (0.205) at every admissible denominator up to 2105**, and recovering the denominator
would not fix it.

**So: what WOULD decide BAK1 and EGFR — and does any of it exist in this checkout?**

## 2 · Merit rationale

Patient relevance is the parents' indirect but real one. In a disease under one case per million per
year with no line in this panel, which therapeutic classes stay on the board is decided by
transferred dependency evidence, and the trap screen is the filter that separates a real candidate
from a common essentiality in disguise. A screen with two permanently unreadable rows is only a
problem if something rests on those rows — and nobody had checked either which quantity is actually
blocking them or whether anything published consumes them. The contribution is non-trivial and
general: **"undecidable" is not one condition but three with three different remedies**, and telling
them apart converts a standing open item into either a shopping list or a closed one. Fully
attainable: arithmetic on a committed artifact plus a citation census, offline, no spend.

⛔ This is not a paper-shaped claim and I propose none. This is a dependency-resolution result on a
retained internal screen.

## 3 · The evidence gap, and the boundary I drew against BIOMARKER-DEP-3

The gap is **not** the per-line `CRISPRGeneEffect` matrix. That is the parents' open gap, it needs
egress the proxy refuses, it is outside worker authority, and **no fetch was attempted.**

The gap addressed: SYNLETH-2 named two genes as undecidable and gave the reason in one clause
("too near the cut"). It never separated the three quantities that could each independently cause
that — the width of the sampling interval, the ±5e-4 of the 3-dp rounding, and the raw distance to
the cut — and so never established **what specific additional information would be sufficient**.
Those three have entirely different remedies (more lines; more decimal places; nothing), and until
they are told apart the item cannot be closed or costed.

**Boundary against BIOMARKER-DEP-3.** That lane produced a **per-quantity bound table** (its §5.1:
interval envelopes and descriptive brackets for EWSR1, MCL1, BCL2L1, BRD9, FLI1, NR4A3
`rest_frac_dependent`, every `rest_mean`, every `selectivity`, and the Fisher *p*). **I produce no
such table and re-bound none of those quantities; none of them is BAK1 or EGFR, and the two tables do
not overlap in a single row.** My unit is a **verdict**, not a quantity: for exactly two genes at
exactly one cut, I decompose the undecidability into named additive components and compute the
**critical sample size** at which each verdict would become decided. Where BIOMARKER-DEP-3 asks "how
wide is the bound on this number", I ask "what would have to be true for this binary screen row to be
readable at all". Its descriptive/inferential distinction is the frame I use and I re-derive rather
than restate it; I add no new bound to its table and propose no change to it.

## 4 · Re-derivation of SYNLETH-2's envelope result — before building on it

`checks/01`, exit 0; artifact `undecidability-anatomy.json` §A. Independent implementation
(my own admissibility test, my own record walk, my own Wilson).

**Everything reproduces, digit for digit. No discrepancy found.**

* **67** records over **64** unique genes; **49** distinct reported `rest_frac_dependent` values.
* Admissible denominators: **1126**, min **943**, max **2105**, **37** excluded inside the range —
  identical to SYNLETH-2 and to BIOMARKER-DEP-2/-3.
* Worst case n = 943, ≥ 0.80 screen: **TRAP_CERTAIN 23 · CLEAR_CERTAIN 44 · FRAGILE 0.** ✓
* Worst case n = 943, ≥ 0.20 screen: **TRAP_CERTAIN 29 · CLEAR_CERTAIN 36 · FRAGILE 2**, the two
  being **BAK1 at 0.187 and EGFR at 0.205**, matching the stored fractions exactly. ✓

The record for each: `genes_by_group/Apoptotic guardians (BH3)[5]` BAK1 `rest_frac_dependent`
**0.187**; `genes_by_group/Drug-screen hit targets[2]` EGFR **0.205**.

## 5 · WHY they are undecidable — the arithmetic

Three candidate causes, separated. A verdict at a cut is decided iff
**(rounding half-width) + (sampling half-width) < (distance to the cut)** on the relevant side.

| gene | stored | side | ① distance to cut | ② rounding half-width | ③ sampling half-width at the **largest** admissible n = 2105 |
|---|---|---|---|---|---|
| **BAK1** | 0.187 | below | **0.013000** | 0.000500 (**0.038 ×** ①) | **0.016651** (**1.28 ×** ①) |
| **EGFR** | 0.205 | above | **0.005000** | 0.000500 (**0.100 ×** ①) | **0.017238** (**3.45 ×** ①) |

**The answer is ③ against ①, and it is neither ② nor the denominator.**

* **Not the rounding.** ② is 0.0005 for both — 2.6 % of BAK1's margin and 10 % of EGFR's. Drop the
  sampling model entirely and read the fractions **descriptively** ("of the non-sarcoma lines this
  panel screened, this fraction scored below −0.5") and the rounding alone gives
  BAK1 **[0.1865, 0.1875] → CLEAR_CERTAIN** and EGFR **[0.2045, 0.2055] → TRAP_CERTAIN.**
  **Descriptively both genes are already decided, at 3 dp, with margin.** Only the *inferential*
  verdict is open. This is exactly SYNLETH-2 §5d's split, re-derived and now applied to the two rows
  it did not apply it to.
* **Not the denominator.** ③ is evaluated at **n_max = 2105**, the best case in the admissible set,
  and it still exceeds ① for both. So recovering the exact denominator — even landing on the largest
  value the artifact permits — leaves both fragile. SYNLETH-2's one-clause claim is confirmed by
  construction rather than by assertion.
* **It is proximity against sampling width, jointly.** Neither alone: 0.013 and 0.005 are not
  intrinsically small margins, and 0.0167 is not an intrinsically wide interval. The pair is the
  problem, and only their **ratio** matters.

## 6 · What WOULD decide each, quantified

`checks/01` §C, cross-checked under a second interval method in `checks/02`.

| | BAK1 (0.187) | EGFR (0.205) |
|---|---|---|
| decimal places needed for the **descriptive** verdict | **2** (already stored: 3) | **3** (already stored: 3) |
| do more decimal places decide the **inferential** verdict? | **no** | **no** |
| inferential verdict at n = 2105 with an **exact, unrounded** fraction | **FRAGILE** | **FRAGILE** |
| **critical n**, Wilson, with the 3-dp rounding carried | **3934** | **30 353** |
| **critical n**, Wilson, exact fraction | **3637** | **24 586** |
| closed form z²p(1−p)/d² | 3455.7 | 25 042.5 |
| **critical n**, exact Clopper–Pearson (stably decided from) | **3731** | **25 057** |
| × the whole 24Q4 release (2105 models) | **1.73 ×** | **11.68 ×** |

**So the shape of the answer is: no number of decimal places decides either gene, and no denominator
decides either gene. What decides them is more screened cell lines — 1.7 × the entire DepMap 24Q4
release for BAK1, and 11.7 × it for EGFR.** The two methods agree to within 3 % on both (Clopper–
Pearson is the more conservative and is the figure to quote); the closed form brackets them, and the
small gap between "first decided" and "stably decided" under CP (3612 → 3731; 24 700 → 25 057) is the
integer-count lattice, reported rather than smoothed.

EGFR is roughly **seven times harder than BAK1**, for the reason the decomposition gives: its margin
is 2.6 × smaller and the required n scales as 1/margin².

## 7 · Which of that exists in this checkout — none of it

`checks/01` §D, including a filesystem probe over the whole checkout.

| candidate | exists here? | would it decide either? |
|---|---|---|
| the stored fraction at more than 3 dp | **no** — the panel stores 3 dp and retains no count, no `n_rest`, no dispersion, no order statistic on the rest arm (DEP-THRESHOLD C1, re-checked in §4) | **no**, and it would not help if it did (§5) |
| the exact rest-arm denominator | **no** — recorded nowhere; 1126 values remain admissible | **no** — even n_max = 2105 leaves both fragile |
| the per-line `CRISPRGeneEffect` matrix | **no** — filesystem probe for any `CRISPRGeneEffect*` across the checkout returned **zero hits** | **no** — it removes the rounding term and fixes n exactly, but n is bounded by the release's own 2105 models and both critical n exceed that |
| a larger CRISPR panel (≥ 3731 / ≥ 25 057 non-sarcoma lines) | **no** | **yes — and it is the only thing that would** |

⭐ **This corrects, in the useful direction, the assumption that the per-line matrix is the remedy
here.** For the ≥ 0.80 screen and for BIOMARKER-DEP-3's bound table the matrix genuinely is the fix.
**For BAK1 and EGFR it is not.** It would confirm the descriptive verdicts that the stored 3-dp
fractions already decide, and it would leave the inferential verdicts exactly as fragile as they are
now, because the limitation is the number of lines DepMap screened, not what was retained about them.
**The correct entry for these two rows is not "blocked on a fetch" — it is "not obtainable from any
version of this dataset."** ⛔ **Accordingly I did not fetch it, did not substitute anything for it,
and relabelled nothing.**

## 8 · Does anything published depend on either classification? — No

`checks/03` (exit 1, preserved: the last of its four greps matched nothing, which is itself the
result) and `checks/04` (exit 0).

* **BAK1 is named in no manuscript in this repository at all** — `grep -rn -w BAK1
  research/manuscripts/` returns nothing. Its only appearances are gene-list membership in the
  producers (`depmap_sarcoma_dependency.py:51` BH3 group; `emc_expression_panels.py:570` effectors)
  and in expression-panel data files. **No claim of any kind rests on BAK1's dependency
  classification.**
* **EGFR's 0.205 is printed in exactly one manuscript**, as a raw table cell:
  `research/manuscripts/dependency/emc-kinase-leads-source-verification.md:361`. The prose around it
  classifies nothing against any cut. The two starred claims in that section rest on **ALK/ROS1 at
  0.000** and on **HDAC3 at 0.824 / 0.878** — the latter a ≥ 0.80 row, already **decided** by
  SYNLETH-2. The one EGFR sentence in that section (`:351`, "lower in EMC on both platforms") is an
  **expression** read from the arrays, not a dependency classification. Every other EGFR hit in
  `research/manuscripts/` is in the surface-targets papers and concerns surfaceome expression, never
  this panel.
* **No manuscript applies a ≥ 0.20 rest-arm cut anywhere.** The only manuscript sentences that read
  `rest_frac_dependent` as a classification are the two MTAP/PRMT5 review documents citing **PRMT5 at
  0.941** — a ≥ 0.80 row, `TRAP_CERTAIN`, decided.

**So the ≥ 0.20 screen's two undecidables do not matter to any published claim.** The only quantity
they move is DEP-THRESHOLD's descriptive count "29 of 64 records at ≥ 0.20" (30/29 including
duplicates), which would become 28 if EGFR's verdict flipped — and that count lives only in sibling
lane FINDINGs and BIOMARKER-DEP-3 §5.2, in no manuscript and no pinned figure. **This is a real and
reassuring result: the open item is genuinely closed rather than merely unaddressed.**

## 9 · Artifact · validation · provenance · limitations · stop condition

* **Artifact** — `undecidability_anatomy.py` + `undecidability-anatomy.json` (§A re-derivation,
  §B anatomy, §C what would decide each, §D availability); `cp_cross_check.py` + `cp-cross-check.json`
  (method independence). `checks/01`–`04` hold every execution attempt with command, stdout, stderr
  and **real** exit code. `checks/03` exits **1** and is preserved as run; the non-zero code is the
  last grep of a compound finding no match, which is the substantive answer to §8, not a failure of
  the check. `01`, `02`, `04` exit 0. There were no crashed or abandoned attempts.
* **Validation / baseline** — the baseline is SYNLETH-2's published result, re-derived here by an
  independently written implementation before anything was built on it (§4), reproducing 1126 / 943 /
  2105, 23 / 44 / 0, and both undecidable genes with their stored fractions. The critical-n result is
  computed under **two independent interval methods** (Wilson and exact Clopper–Pearson) which agree
  to within 3 %, and is bracketed by an independent closed-form normal approximation. The
  descriptive-verdict claim is checked by shrinking the rounding term to zero and re-testing. The
  availability claim for the per-line matrix is a filesystem probe over the whole checkout, not an
  assertion. The citation census is four greps over `research/manuscripts/`, `systems/`,
  `research/autonomy/` and `research/modalities/`, preserved verbatim.
* **Provenance** — `research/modalities/depmap-sarcoma-dependency.json`, DepMap public release 24Q4
  (figshare), `CRISPRGeneEffect.csv` + `Model.csv` per its own `data_source`; read-only, opened and
  never written. Statistic definitions from `research/modalities/depmap_sarcoma_dependency.py`.
  Sibling FINDINGs read for constraint and re-derivation targets, not reused as evidence.
* **Limitations** — ⛔ No EMC observation; no efficacy, safety, therapeutic-selectivity,
  therapeutic-window or clinical-readiness claim, and **the ≥ 0.20 "screen" is a dependency-score
  statistic, never a therapeutic property.** The critical n figures are **nominal binomial sample
  sizes** under an i.i.d. model DepMap's convenience panel does not license — they measure the
  arithmetic cost of the margin, not the panel's representativeness, which no computation here can
  address, so "25 057 lines would decide EGFR" is a statement about arithmetic, not a study design.
  The admissible set is inherited from my own §4 re-derivation under the same stated rule and the same
  `n ≤ 2105` bound; denominators above 2105 are excluded by that bound, not by argument. The ±5e-4
  covers the rounding of the point value only. The 0.20 cut is DEP-THRESHOLD's own secondary screen,
  not a published threshold, and nothing here validates or endorses it. §8 is a census of this
  checkout on 2026-09-09 at the paths named; a claim added later would need re-checking.
* **Stop condition — reached.** The question was what would decide BAK1 and EGFR and whether any of it
  is available. Answer: only a panel 1.7 × / 11.7 × larger than DepMap 24Q4 would, none of it exists,
  and nothing published depends on the answer. **Do not spend further cycles on these two rows**, and
  in particular **do not queue them behind the `CRISPRGeneEffect` fetch** — §7 shows that fetch would
  not decide them.

## 10 · Honest outcome and the next credible step

**A well-evidenced "nothing available", which closes the open item rather than parking it.** The
undecidability is real, it is fully explained (proximity against sampling width, not rounding and not
the denominator), the remedy is quantified (3731 and 25 057 screened non-sarcoma lines), the remedy
does not exist and is not fetchable, and — the part that makes it closeable — **no published claim in
this paper family consumes either classification.** SYNLETH-2's negative stands unaltered and is now
explained and bounded rather than merely reported.

The next credible step is **not** for these two genes: there is none, and inventing one would be
manufacturing work. It is the one both parents already named, for the quantities it actually serves —
the per-line `CRISPRGeneEffect` matrix, which would replace BIOMARKER-DEP-3's conditional bound table
and settle the 2014-vs-1087 denominator question. **It requires network egress, it is the parents'
open gap, it is outside this lane's authority, and it was not attempted.** The recommendation this
lane adds to it is one line: when that fetch happens, **do not expect it to decide BAK1 or EGFR.**

## 11 · Shared files

**None changed, and none needed to change.** This lane's result is a property of the existing
artifacts, not a defect in any of them, so no diff was prepared. If an owner wants it recorded where
readers will meet it, the natural home is one sentence beside SYNLETH-2's ≥ 0.20 row noting that its
two undecidables are proximity-limited, unfixable by the per-line matrix, and consumed by nothing;
that is another lane's document and I did not draft it.
