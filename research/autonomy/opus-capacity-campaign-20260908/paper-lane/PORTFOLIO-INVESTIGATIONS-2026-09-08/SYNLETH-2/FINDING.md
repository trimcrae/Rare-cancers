---
id: DOC-SYNLETH-2-FINDING-20260909
title: "SYNLETH-2 — the unrecorded rest-arm denominator does not put the pan-essential-trap screen in doubt"
level: L4
kind: investigation-finding
status: live
date: 2026-09-09
last_verified: 2026-09-09
lane: SYNLETH-2
campaign: OPUS-CAPACITY-CAMPAIGN-20260908
parent: PUB-SYNLETH
siblings_read: [PUB-SYNLETH, DEP-THRESHOLD, PUB-MTAP-PRMT5, PUB-BIOMARKER-DEP, BIOMARKER-DEP-2]
concurrent: [BIOMARKER-DEP-3]
---

# SYNLETH-2

⛔ No wet lab, no EMC observation, no DepMap EMC line. Nothing here is an efficacy, safety,
therapeutic-selectivity, therapeutic-window or clinical-readiness claim, and none may be read out of
it. `selectivity` and `rest_frac_dependent` are **screen statistics on a public CRISPR panel**, not
therapeutic properties. No network, no producer re-run, no GPU, no paid API, no publication act, no
outreach, no `git add/commit/push`, no `preflight.sh`, no subagent. Every write is inside this
directory; no shared file was touched and no diff was needed.

## 1 · The question

BIOMARKER-DEP-2 established that this panel's rest-arm denominator is recorded nowhere and that
**1126** denominators are consistent with the published fractions, concluding that **no confidence
interval can be placed on any `rest_frac_dependent`** — including the **0.915** that carries
PUB-SYNLETH's EWSR1 pan-essential-trap finding.

PUB-SYNLETH's actual product for this program is not the number 0.915. It is a **reading rule**:
never read `selectivity` in this panel without `rest_frac_dependent` beside it, because the largest
selectivity in the panel (EWSR1, +0.373) belongs to a near-universal essentiality, not to a window.
DEP-THRESHOLD then *applied* that rule as a screen and flagged 22 of 64 genes at
`rest_frac_dependent ≥ 0.80`.

**So, on the synthetic-lethality side: does the unrecorded denominator actually put the trap
screen's verdicts in doubt — or is the screen decidable without it?**

## 2 · Merit rationale

Patient relevance is the indirect but real one both parents named. In a disease at under one case
per million per year there is no EMC line in this panel, so which therapeutic classes stay on the
board is decided by transferred dependency evidence, and the trap screen is the filter that decides
which of this panel's apparent "selective" hits are real candidates and which are common
essentialities in disguise. If that filter is undecidable, every route this panel grades — the
BH3 guardians, the proteasome axis, PRMT5/MAT2A, the BET/CDK panel — is being graded by an
instrument nobody can read. The contribution is non-trivial and general: **a summary-only screen
whose denominator was thrown away can still be a decidable screen**, and the condition under which
that is true is a checkable quantity rather than an opinion. The evidence is fully attainable — it
is arithmetic on a committed artifact, offline.

⛔ This is not a paper-shaped claim and I propose none. PUB-SYNLETH's target document is an internal
memo and §4 of it already decided that. This is a correction to a retained internal result.

## 3 · The exact evidence gap, and the boundary I drew against BIOMARKER-DEP-3

The gap is **not** the missing per-line `CRISPRGeneEffect` matrix. That is the parents' open gap, it
needs egress the proxy refuses, it is outside worker authority, and **no fetch was attempted here.**

The gap addressed is this: BIOMARKER-DEP-2's conclusion is stated over *quantities* — "no interval
can be placed on any `rest_frac_dependent`" — and was never carried through to the *decision* those
quantities exist to serve. A quantity can be interval-indeterminate while the binary verdict that
consumes it is fully determined, and nobody had checked which regime this screen is in.

**Boundary against BIOMARKER-DEP-3 (running concurrently on the denominator from the biomarker
side).** I produce **no per-quantity bound table** and make no attempt to recover or narrow the
denominator itself. I take the denominator set as an adversary and ask only whether the
**synthetic-lethality-side decision** — trap / clear, per gene — changes anywhere inside it. My
output is a verdict per gene and a breakdown point, not intervals per gene. If BIOMARKER-DEP-3
narrows the admissible set, my result only strengthens; it never conflicts, because I evaluate at
the worst case.

## 4 · Re-derivation of every prior number relied on — before building on it

`checks/01`, exit 0; artifact `denominator-envelope.json` §A–§B.

**Everything reproduces, digit for digit. No discrepancy found.**

* **67** gene records carrying the sarcoma/rest split over **64** unique genes; the three duplicated
  records are **EWSR1, FLI1, NR4A3** (BIOMARKER-DEP-2's correction ✓, not the NR4A paralogues).
* `n_sarcoma` = **91** on every record, the only value present; `sarcoma_frac_dependent × 91`
  integral on all 67.
* Record field names, all seven and no more: `gene`, `n_sarcoma`, `rest_frac_dependent`,
  `rest_mean`, `sarcoma_frac_dependent`, `sarcoma_mean`, `selectivity`. **No dispersion field**
  (DEP-THRESHOLD ✓, BIOMARKER-DEP-2 ✓).
* **EWSR1 selectivity +0.373, `rest_frac_dependent` 0.915, `sarcoma_frac_dependent` 0.967**
  (PUB-SYNLETH ✓).
* Trap set at ≥ 0.80: **23 records / 22 unique genes**; at ≥ 0.20: **30 / 29** (DEP-THRESHOLD's
  22 and 29, and BIOMARKER-DEP-2's 23/30 vs 22/29 reconciliation, both ✓).
* **The admissible denominator set reproduces exactly**, under a rule I stated and derived
  independently (`n` admissible iff every one of the 21 distinct reported `rest_frac_dependent`
  values is `round(k/n, 3)` for some integer `k ∈ [0,n]`, `n ≤ n_models_total = 2105`):
  **1126 admissible values, min 943, max 2105, 37 excluded inside the range** — the same
  **1126 / 943 / 2105** BIOMARKER-DEP-2 reports.

Nothing established by a prior lane is re-run or contradicted: EWSR1 stays a pan-essential trap, the
FET-class transfer stays falsified, the threshold sweep stays non-computable, and the denominator
stays unrecorded.

## 5 · The step taken, and the result

**A denominator-envelope decision test on the trap screen.** `denominator_envelope.py` (§C–§E) and
`breakdown_denominator.py`.

**(a) An interval *can* be placed — it is just conservative, and the price is bounded.** The 95 %
binomial interval half-width at fixed `p̂` is strictly decreasing in `n`, so the **union** of the
intervals over all 1126 admissible denominators is **exactly the interval evaluated at n_min = 943**
— verified numerically over the whole admissible set, monotone and union-equality both true at
p = 0.915, 0.854, 0.800 and 0.696. That envelope is at most **√(2105/943) = 1.4941** times wider
than the unknown true interval (measured inflation 1.4927–1.4961). So the honest statement is
narrower than "no interval can be placed": **the unrecorded denominator costs a factor of at most
1.494 in interval width; it does not prevent an interval.** For EWSR1's 0.915 that is Wilson
**[0.8955, 0.9312]** at the worst case against **[0.9023, 0.9262]** at the best.

**(b) And the trap screen is fully decided at the worst case — 0 fragile genes.** Evaluating every
record at n_min = 943, widening the point value by the ±5e-4 the 3-dp rounding permits, under
**both** Wilson and exact Clopper–Pearson:

| screen | TRAP_CERTAIN | CLEAR_CERTAIN | FRAGILE |
|---|---|---|---|
| `rest_frac_dependent ≥ 0.80` (the trap screen) | **23** | **44** | **0** |
| `rest_frac_dependent ≥ 0.20` (secondary) | 29 | 36 | **2** (BAK1 0.187, EGFR 0.205) |

**Every one of DEP-THRESHOLD's 23 trap records, and every one of the 44 it cleared, is decided the
same way at every admissible denominator.** EWSR1 is `TRAP_CERTAIN`: even at n = 943 its lower bound
is 0.8955, clear of the 0.80 cut. **The screen that PUB-SYNLETH installed and DEP-THRESHOLD applied
is not in doubt, and needs no interval to be read.**

**(c) How much denominator ignorance it absorbs — independent of my admissibility rule.**
`checks/02`: scanning `n` downward, the ≥ 0.80 screen stays fully decided for **every n > 438**;
the first gene to go fragile is **SMARCB1** (0.839) at n = 438. That is **2.15× below the smallest
denominator the artifact permits**, so the verdict does not rest on my derivation of the admissible
set. The ≥ 0.20 screen is the opposite case and I report it as a negative: BAK1 and EGFR straddle
that cut at **every** n up to and including 2105, so those two are undecidable *for being near the
cut*, not for want of a denominator — recovering the denominator would not fix them.

**(d) The descriptive/inferential split, which is what the denominator gap really is.** The reported
fraction is pinned to **±0.0005 by the 3-dp rounding alone, whatever the denominator.** So the
*descriptive* reading — "0.915 of the screened non-sarcoma lines scored below −0.5" — is
denominator-free and always was. The denominator is needed only to *generalise* from the screened
lines to a population. **BIOMARKER-DEP-2's finding is exactly right as an inferential statement and
should be read as one**; it does not impeach any descriptive use of these fractions, and the trap
screen is a descriptive use.

## 6 · Artifact · validation · provenance · limitations · stop condition

* **Artifact** — `denominator_envelope.py` + `denominator-envelope.json` (§A re-derivation, §B
  admissible set, §C envelope, §D per-gene decision stability, §E descriptive/inferential split);
  `breakdown_denominator.py` + `breakdown-denominator.json`. `checks/01`–`02` hold every execution
  attempt with command, stdout, stderr and real exit code. Both attempts exited 0; there were no
  failed attempts to preserve.
* **Validation / baseline** — baseline is the committed artifact's own fields and the three sibling
  lanes' published numbers, all re-derived here before use (§4) and all reproducing. The envelope
  claim is not asserted from theory alone: monotonicity and union-equality are checked numerically
  across all 1126 admissible denominators at four values of p. The decision verdict is computed
  under **two independent interval methods** (Wilson and exact Clopper–Pearson) and they agree on
  all 67 records at both cuts. The rule-independence of the verdict is checked separately by the
  downward scan (§5c).
* **Provenance** — `research/modalities/depmap-sarcoma-dependency.json`, DepMap public release 24Q4
  (figshare), `CRISPRGeneEffect.csv` + `Model.csv` per its own `data_source`; read-only, opened but
  never written. Statistic definitions read from `research/modalities/depmap_sarcoma_dependency.py`.
  Sibling FINDINGs read for constraint and re-derivation targets, not reused as evidence.
* **Limitations** — ⛔ No EMC observation of any kind; no efficacy, safety, therapeutic-selectivity,
  therapeutic-window or clinical claim. **These are nominal sampling intervals.** DepMap's
  non-sarcoma arm is a convenience cohort, not an iid draw from a defined population, so their
  coverage is not guaranteed by the design — the envelope bounds the *arithmetic* consequence of the
  missing denominator, not the panel's representativeness, which no computation here can address.
  The admissible set depends on my stated rule and on `n ≤ 2105`; §5c is the defence, not a proof
  that 943 is the true floor. The ±5e-4 widening covers the rounding of the point value only.
  The screen tested is `rest_frac_dependent` at a **fixed −0.5 gene-effect cut**; DEP-THRESHOLD
  already showed no other cut is computable from this artifact, and nothing here changes that.
  Nothing here re-opens the dilution/power question or the BRD9 prior.
* **Stop condition — reached.** The question was whether the trap screen is decidable without the
  denominator. It is, at every admissible denominator and 2.15× below the smallest one, under two
  interval methods, with zero fragile genes at the operative cut. **Do not spend further cycles on
  this**: the answer is stable and cannot be improved by more analysis of the same summaries. If
  BIOMARKER-DEP-3 narrows the admissible set, this result is unaffected by construction.

## 7 · Honest outcome and the next credible step

**A bounded positive, and a correction that narrows a sibling's wording rather than overturning it.**
BIOMARKER-DEP-2's inferential finding stands unchanged and is confirmed here down to the last digit
(1126 / 943 / 2105). What is added is that it does **not** propagate to the synthetic-lethality-side
decision it appeared to threaten: PUB-SYNLETH's headline EWSR1 trap verdict and DEP-THRESHOLD's
whole 23-record trap set survive the worst admissible denominator with room to spare, so the
reading rule those lanes installed remains usable exactly as written. The one honest negative is
the secondary ≥ 0.20 screen, where BAK1 and EGFR are undecidable at every denominator.

The next credible independent step is unchanged and remains outside this lane's authority: the
per-line `CRISPRGeneEffect` matrix, which would replace both this envelope and BIOMARKER-DEP-2's
retained-dispersion amendment with the actual distribution. It needs network egress.

## 8 · Shared files

**None changed, and none needed to change.** This lane's result is a property of the existing
artifact, not a defect in it, so no diff was prepared. If an owner wants the result recorded where
readers of the panel will meet it, the natural home is a sentence beside DEP-THRESHOLD's trap table
noting that the 23-record trap set is denominator-robust; that is another lane's document and I did
not draft it.
