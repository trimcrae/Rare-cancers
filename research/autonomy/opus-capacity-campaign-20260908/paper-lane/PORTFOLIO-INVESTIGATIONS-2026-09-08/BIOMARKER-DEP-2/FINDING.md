---
id: DOC-BIOMARKER-DEP-2-FINDING-20260909
title: "BIOMARKER-DEP-2 — the producer amendment both dependency lanes named, written and proved to apply without moving a published number"
level: L4
kind: investigation-finding
status: live
date: 2026-09-09
last_verified: 2026-09-09
lane: BIOMARKER-DEP-2
campaign: OPUS-CAPACITY-CAMPAIGN-20260908
parent: PUB-BIOMARKER-DEP
siblings_read: [DEP-THRESHOLD, SURFACE-2, PUB-SYNLETH, PUB-MTAP-PRMT5]
---

# BIOMARKER-DEP-2

⛔ **No wet lab, no EMC observation, no DepMap EMC line.** Nothing here is an efficacy, safety,
selectivity, therapeutic-window or clinical-readiness claim, and none may be read out of it. No
network, no GPU, no paid API, no publication act, no outreach. Every write is inside this directory;
the one shared-file change is an **unapplied** diff.

## 1 · The question

PUB-BIOMARKER-DEP and DEP-THRESHOLD converged on one defect and both stopped at it: the DepMap
transfer panel's producer keeps, per gene, a mean and a single dependent fraction at a hard-coded
−0.5 cut, and discards the per-line distribution — so the statistic the two dependency papers argue
from cannot be checked at any other threshold, and no interval can be put on it. DEP-THRESHOLD named
the fix in prose (`stats()` should retain dispersion) and explicitly **did not** write it:
"proposed, NOT applied … prepared no diff."

**So: can that amendment actually be written and shown safe — i.e. does it add the retained
distribution without moving a single already-published number, and how much of the threshold
indeterminacy does it actually remove?**

## 2 · Merit rationale

Patient relevance is the same indirect but real one both parents named: in a disease under one case
per million per year, which therapeutic classes stay on the board is decided by transferred
dependency evidence, and this one artifact grades every route in the portfolio that touches DepMap.
The contribution is non-trivial and it is *instrument*, not conclusion: retaining the distribution
makes every future threshold question answerable from the committed artifact **without a re-fetch**,
which matters precisely because the re-fetch is the thing this sandbox cannot do. Attainable: the
amendment is 40 lines and its safety is decidable offline. The failure mode a bare recommendation
leaves open — an owner applies it and silently perturbs published values — is the thing actually
closed here.

## 3 · The exact evidence gap, and what distinguishes it

The gap is **not** the missing `CRISPRGeneEffect` matrix. That is the parents' gap, it needs network
egress, the proxy refuses it, and it stays open and untouched here (no fetch was attempted; the only
egress-adjacent command run was an offline `pip` probe, preserved as `checks/02`, exit 1 — pandas is
not installed, so the producer cannot be executed end to end in this sandbox).

The gap addressed here is downstream of that and independent of it: **the named producer change had
no diff, no applicability proof and no backward-compatibility evidence.** Distinct from every sibling
— SURFACE-2 (a different artifact, screen never fired), DEP-THRESHOLD (proved the sweep uncomputable;
proposed the fix), PUB-SYNLETH (EWSR1 pan-essential trap), PUB-MTAP-PRMT5 (FET-class transfer
falsified). None of them wrote a line of the producer. Nothing here re-opens or contradicts any of
them.

## 4 · Re-derivation of every prior number relied on — BEFORE building on it

Artifact `prior-number-rederivation.json`; producer `rederive_prior_numbers.py`; `checks/01`, exit 0.

**Reproduced exactly.** 67 gene records carrying the sarcoma/rest split over **64 unique genes**;
`n_sarcoma` = 91 on every record; **91 is the unique denominator under 100 consistent with all 67
rounded sarcoma fractions**, and 176 is excluded — a strictly stronger form of the parent's
integrality finding. Pan-essential trap **23 records / 22 unique genes** at `rest_frac ≥ 0.80` and
**30 / 29** at ≥ 0.20 — the 64/22/29 vs 67/23/30 pair both siblings report, reconciled below.
EWSR1 selectivity **+0.373**, `rest_frac_dependent` **0.915** (PUB-SYNLETH ✓). BRD9 synovial n=5,
mean −0.13, frac 0.2 → **1 of 5**; Wilson 95 % **0.036–0.624**; shift vs the +0.105 sarcoma mean
**0.235**; subtype mean **0.37** on the non-dependent side of the cut. Exact-Fisher power
**0.9925** at n=5/p₁=0.8 and **0.9094** at p₁=0.6; **minimum n for 80 % power = 3**. MCL1
0.835/0.696 and BCL2L1 0.758/0.854 ✓. The gene records carry exactly seven field names, none of them
a dispersion field ✓.

**Two corrections, reported digit for digit.**

1. **The 67 vs 64 difference is not what the dispatch brief says.** It is not "the three NR4A
   paralogue records". The three duplicated records are **NR4A3, EWSR1 and FLI1**, each appearing
   once under `/context_genes` and once under `/fusion_addiction_proxy` — machine-located, paths in
   the artifact. Both counts remain correct under their own scope, exactly as the brief states; only
   the attribution of *which* three differs. Nothing in either lane's conclusions depends on it.
2. **PUB-BIOMARKER-DEP's Fisher `p = 0.084` does not reproduce as stated.** Against the *sarcoma*
   background (1/5 vs 2/91) the one-sided exact value is **0.1497**. It reproduces only against the
   *non-sarcoma* arm, and only under an assumption about that arm's size that **the artifact does
   not record**: across the full set of denominators the artifact permits, it spans **0.0867 (n=943)
   to 0.0847 (n=2105)**. So ~0.084 is a fair number with an unstated input, not a wrong one. Its
   direction — the control does not come out at 0.99 power — is unaffected, so this lane's step was
   not blocked by it. **But it is itself evidence for the amendment**: the rest arm's denominator is
   recorded nowhere, and 1126 different values of it are consistent with the published fractions, so
   **no confidence interval can be placed on any `rest_frac_dependent` in the panel** — including
   the 0.915 that carries PUB-SYNLETH's headline and the 0.696 / 0.854 that DEP-THRESHOLD showed are
   the decisive quantities for §2.5. Neither parent named this.

## 5 · The step taken

**An unapplied unified diff against `research/modalities/depmap_sarcoma_dependency.py`, plus an
executable proof that it is safe.**

`producer-dispersion-retention.diff` adds, and changes nothing else:

* to `stats()` — `n_rest`, and per arm `*_sd`, `*_min`, `*_q25`, `*_median`, `*_q75`, `*_max`,
  `n_dependent_*`, appended after the seven existing fields;
* to `subtype_mean()` — `n_dependent`, `sd_gene_effect`, and the five-number summary, so the panel's
  own self-validation blocks (the only biomarker-defined contrasts it holds, and the ones at n=5)
  stop resting on one fraction at one cut.

The retention mirrors the in-repo precedent the sibling identified: `nr4a_paralogue_comparison`
already keeps `median_gene_effect`, `min_gene_effect` and `n_dependent_lines`, and is the only block
supporting more than one exact threshold point.

## 6 · Artifact · validation · provenance · limitations · stop condition

**Artifact.** `producer-dispersion-retention.diff` (unapplied), `amendment-validation.json`,
`verify_amendment.py`, `prior-number-rederivation.json`, `rederive_prior_numbers.py`.

**Validation / baseline.** Baseline = the committed producer's own output fields.

* `git apply --check --verbose` — **exit 0**, `checks/03`. Patched copy byte-compiles.
* **Q1 backward compatibility — PASS, 0 mismatches in 200 trials** across four distribution shapes
  (pan-essential, null, selective, bimodal). The **real committed source text** of `stats()` is
  extracted from the file and from the patched copy and executed under a minimal duck-typed
  Series/Frame shim (pandas is absent), on identical input. All seven published fields —
  `gene`, `sarcoma_mean`, `rest_mean`, `selectivity`, `sarcoma_frac_dependent`,
  `rest_frac_dependent`, `n_sarcoma` — are **identical in value and in key order**.
* **Q2 new-field correctness — PASS, 0 mismatches in 200 trials**: every one of the 15 added fields
  equals an independent pure-Python recomputation.
* **Q3 payoff — quantified, and partly negative.** Distribution-free bound width on P(X < t), 200
  synthetic 91-line arms, both bounds asserted to contain the truth:

  | t | width from committed fields | width from retained five-number summary | width from the amendment (intersection) |
  |---|---|---|---|
  | −2.00 | 0.549 | 0.261 | **0.261** (54/200 exactly determined) |
  | −1.00 | 0.780 | 0.272 | **0.272** |
  | −0.75 | 0.727 | 0.272 | **0.272** |
  | −0.25 | 0.209 | 0.261 | **0.209** |
  |  0.00 | 0.209 | 0.261 | **0.209** |

  **Honest reading:** the five-number summary is a large gain at the deep cuts where the
  common-essential arguments live (−1.0: 0.78 → 0.27) and is *worse than the existing mean+fraction
  bound alone* at shallow cuts near the mean. Because the amendment **retains the old fields as
  well**, the bound a reader actually gets is the intersection, which is never worse than either —
  that is the last column. The amendment does not make any off-cut fraction exactly recoverable in
  general (0 of 200 at t = −1.0); it narrows it. Only the per-line matrix would make it exact.

**Provenance.** `research/modalities/depmap_sarcoma_dependency.py` and
`research/modalities/depmap-sarcoma-dependency.json` (DepMap public 24Q4, figshare,
`CRISPRGeneEffect.csv` + `Model.csv`, per the artifact's own `data_source`), both read-only. Sibling
FINDINGs read for constraint, not reused as evidence. Every execution attempt is under `checks/`
with its real exit code, **including the two failures**: `checks/02` (pip, exit 1),
`checks/04` (harness, wrong repo path depth, exit 1) and `checks/05` (**exit 1 — the harness caught a
genuine bug in my own bound derivation**: with n = 91 and values rounded to 3 dp, the naive quartile
bound excluded a true value of 0.5055 from [0.25, 0.50]; the fix absorbs both the ±5e-4 rounding and
the 1/n order-statistic slack, which is why the widths above are 0.261–0.272 rather than 0.25).

**Limitations.** ⛔ No EMC observation; no clinical, efficacy, safety, selectivity or
therapeutic-window claim, and the amendment creates no new scientific claim of any kind — it retains
numbers already computed and thrown away. **The diff is UNAPPLIED and no shared file was touched**;
applying it is an owner decision. The producer was **not run** and the committed JSON is **not
regenerated**, so no field added here exists in any artifact yet — running it needs network and
pandas, neither available. Validation is on **synthetic** input under a shim implementing the pandas
methods the functions call; it tests the committed code text and the amendment's arithmetic, **not
pandas itself**, and not the surrounding `main()`. Q3's widths are for one Gaussian family at n = 91
and do not generalise as measured values. The five-number bound is conservative by construction.

**Stop condition — reached.** The question was whether the named amendment can be written and shown
safe. It can: it applies at exit 0 and provably moves no published number, while narrowing the
deep-cut indeterminacy by roughly a factor of three. **Do not iterate further on this diff.** The
next credible step is not more analysis of these summaries — DEP-THRESHOLD already showed there is
nothing left to sweep — it is the owner deciding whether to apply the diff and re-run the producer on
the standing networked CI route, which this lane may not commit, push or dispatch.

## 7 · Reconciliation with `portfolio-2026-09-05/recommendation.md`

Read and reconciled. Its dependency-family prospects are no longer open as written: the
biomarker-to-dependency transfer question is **answered and closed** by PUB-BIOMARKER-DEP (zero
models in common between the biomarker and dependency axes), the threshold-robustness prospect is
**refuted as computable** by DEP-THRESHOLD, the FET-class transfer is **falsified** by
PUB-MTAP-PRMT5 (t = −0.16, p 0.873), and the vital-tissue screen has **never fired** (SURFACE-2:
45 leaves, 0 non-null). What survives across all four is a single shared instrument defect in one
producer — which is why this lane went to the producer rather than to a new prospect.
