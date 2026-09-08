# C1 — next question stated IN FULL before dispatch

Recorded `date -u` **Tue Sep 8 07:24 UTC 2026**. Same session, sole parent collector, `claude-opus-5` medium,
saved subscription, no overage, deadline 2026-09-09T02:37:19Z. Stated before dispatch as required; nothing is
dispatched on this until the five elements below are on record.

## Why this is a scientific question and not another inventory

I applied the test to this one myself rather than inheriting a rank. **B1 failed because a readability
adjudication has no dependent conclusion — nothing changes whichever way each row lands.** This candidate has
one: a load-bearing denominator is measurably wrong, and **whether the paper's quantitative conclusion survives
the correction is currently UNKNOWN**. That is the difference, and it is the whole justification.

## (a) Exact scientific question

**Does the compartment-B upper band on treating host comorbidity in EMC survive correcting its own denominator
— and by how much does it move?**

`research/manuscripts/emc-host-factor-model.json` sets `competing_share_of_deaths_used = 0.394`, sourced to
*"within-series (Meis-Kindblom 1999) — the only pairing measured on the same patients."* The paper's own
Appendix A.1 states verbatim *"Competing share, 39.4 per cent superseded by 21.7 per cent"*, and its Results
table carries the adopted `21.7 %` (163 patients, 18 disease / 5 other-cause deaths), corroborated
independently at 23.0 % by relative survival. **Parent-verified all three lines directly.** So the model runs on
the superseded estimator, **high by 39.4/21.7 = 1.82×**, and its source sentence is now false —
`direct_cause_split` *is* a same-patient pairing and *is* what the paper adopted.

**Why it matters:** this is the portfolio's only route whose intervention already exists and is already
approved, and the competing-mortality share bounds the entire antitumour argument. A band inflated 1.82× either
collapses to something unremarkable or survives — and nobody knows which.

## (b) Actual reachable evidence, with access limits

Committed, $0, no network: `emc-host-factor-model.json`, `emc-host-factor-inputs.json`,
`emc-mortality-decomposition.json`, `emc-terminal-events.json`, `emc-mortality-mechanisms-paper.md`, and the
model's generator. **Limits, stated:** the model's own `factors_not_entered` (type-2 diabetes/metformin,
hypertension) need a **network retrieval outside worker authority** and stay out; host-factor prevalence in a
real EMC cohort is blocked on `BLK-NO-EMC-DATA` and is unobtainable here. Neither limit blocks the
recomputation, because both are inputs the model already excludes.

## (c) Contribution and novelty uncertainty — stated honestly

Contribution: **it determines whether a recorded defect is material or cosmetic**, which no committed artifact
currently answers. **Novelty: this is NOT a new paper and none is claimed** — it is the consequence of a
correction inside a `drafted` endpoint. Whether the corrected band is *scientifically interesting* is
**UNKNOWN until computed**, and if it turns out to change nothing, that is the result and it is reported as
such. Per the standing instruction, a drafted endpoint does not prove every useful scientific correction is
closed — but neither does this become a paper by being useful.

## (d) Distinction from named prior no-gos

Not the parked synthetic figure-validation family (no digitization, reconstruction, sweep, point-count
successor or figure route). Not S6/S7 (no source hunt, no network, no PMC). Not B1 (a dependent conclusion
exists). Not P1–P6: the endpoint is `PUB-MORTALITY-MECHANISM`, and AUT-064's "ANSWERED — no" names
`PUB-CARE-DELIVERY`, a different endpoint. Not lane 2 (no expression data, no arm comparison, no panel score).
Not a record or consumer census — it recomputes a scientific quantity. Touches no `CLOSED-WORK.md` denied
source, no GSE4303/GSE28866, no PMID 22592656, no W25/GSE243553, no NR4A Perspective, no P6 manuscript.

## (e) Finite acceptance and stop

**Acceptance:** the compartment-B figures recomputed with the share taken from `direct_cause_split`, each
reported beside its current value and its ratio, in a **report with durable raw output** — plus an explicit
statement of whether the paper's stated conclusion survives.
**Stop, whichever comes first:** (i) acceptance; (ii) a committed record shows the within-series estimator was
chosen **deliberately** — then this is a documentation defect, the branch stops there and that is the result;
(iii) the recomputation cannot be done without an input the model excludes; (iv) ~40 tool calls / ~40 minutes.
**Hard stops:** no manuscript edit, no graph edit, no `systems/graph/` write, no re-derivation of the
decomposition, no re-retrieval of effect sizes, no writing of a paper. The child produces a **report and raw
artifacts only**; every repository write, including any eventual correction, remains an **owner act**.

## Bounds

Read-only with respect to the checkout; all execution in scratch, durable artifacts to
`/tmp/claude-0/c1-retained/` **outside** the checkout, hash-verified **before** any cleanup and not deleted;
parent alone collects. ≥10 GiB free. No network, no paid API, no GPU, no publication, no external contact.
Model verified from the child transcript after launch.

---

# ⛔ SCOPE APPENDED 2026-09-08 07:28 UTC — two overstatements in (a) corrected, originals not rewritten

The contract text above is **preserved unchanged**. Two claims in element (a) overreach and are scoped here.

1. **"The competing-mortality share bounds the entire antitumour argument" — withdrawn.** It does not. The
   quantity is a **cohort death fraction** — what share of deaths in a retrospective series were attributed to
   causes other than the tumour. It is **not population mortality risk**, **not a causal treatment effect**, and
   **not a bound on the portfolio's antitumour argument**.
2. **"The portfolio's only route whose intervention already exists and is approved" — scoped.** That is a
   statement about *regulatory availability of a drug class*, never a claim that treating host comorbidity
   helps anyone with this disease.

**Binding on the run and its report:** recomputing this number **establishes no clinical benefit**, no efficacy,
safety, selectivity, therapeutic window or readiness, and no bound on any antitumour claim. It is arithmetic
over a committed model's inputs. **The corrected band, whatever it is, is a model output — not a treatment
effect and not a patient-facing quantity.**

## Provenance requirement added before execution

**Verify the source estimator's provenance BEFORE treating the discrepancy as a defect.** Use
`direct_cause_split`'s **stored value, or its exact numerator and denominator**, from the committed artifact.
**Do not derive a fresh value from the displayed, rounded "21.7 per cent"** — a rounded display is not the
input. If the stored value and the displayed one disagree, that disagreement is itself the result.

**Hold every other model assumption fixed.** Change the competing-share input and nothing else; report the
actual changed outputs and state, for each stated model conclusion, whether it changes and **why**.

**A documented deliberate-estimator stop is an admissible RESULT**, not a reason to run another variant. If a
committed record shows the within-series estimator was chosen on purpose, the branch ends there — no second
configuration, no sensitivity sweep, no alternative share.

---

# C1 EXECUTED — result collected 2026-09-08 07:36 UTC

Child `a07b78237ee438258`, observed transcript model `claude-opus-5`, 07:30:01 → 07:33:00 UTC (16 tool calls).
No repository write, no git operation, no network. Durable artifacts `sha256sum -c` **8 of 8 OK** in
`/tmp/claude-0/c1-retained/` (not deleted, and its scratch tree kept too) and again after copying into
`paper-lane/C1-executed-artifacts/`. Input hashes recorded with source paths and re-verified identical at the
end HEAD; `git diff` over the window shows **0** files changed outside the campaign directory.

## Step 1 did its job — and the discrepancy is NOT the one I described

⭐ **The stored counts and the displayed value agree.** `direct_cause_split` stores two strata —
`masunaga2025_localized` (134, 9 disease, 4 other, **30.8 %**) and `masunaga2025_metastatic` (29, 9, 1,
**10.0 %**) — whose stored numerators and denominators give **5/23 = 21.7391 %**, matching the paper's displayed
21.7 % to rounding. **No contradiction**, and the contract's requirement to use stored values rather than the
rounded display was what established it.

⭐ **The real finding is different and better:** the decomposition artifact contains **no pooled
`direct_cause_split` row at all** — **parent-verified** by walking the JSON myself (rows present: the two
strata plus `within_series` at 39.4 %; the string "163" does not occur). The `163 / 18 / 5 / 21.7 %` line exists
**only in the paper**, at `emc-mortality-mechanisms-paper.md:241`. It is a **paper-side pooling of two stored
strata that no consumer can read from the JSON** — which is a materially different defect from the one my
contract anticipated.

**Deliberate-choice stop (ii) checked and did not fire.** `emc_host_factor_model.py:244-245` selects
`within_series[0]` **unconditionally** — no branch, no config, no retention marker. Its rationale string
*"the only pairing measured on the same patients"* is **self-referential** (it occurs only in the generator and
its own output) **and false**: each `direct_cause_split` row carries `estimator = "Direct ratio of two death
counts on the same patients."` And `direct_cause_split` was already present at the very commit that generated
the model (`abc73e0e`, 2026-09-04), so the better pairing was available and not taken. The paper and the ledger
both record 39.4 % as **superseded**.

## ⛔ A second, independent defect the run surfaced — and I reproduced it myself

**The committed model cannot be regenerated from the committed inputs at this HEAD.** Running the generator
unmodified exits **1** and refuses:
`UNANCHORED EVIDENCE -- refusing to model:` HF-SMOKING PMID 42340948, HF-CV-RISK PMID 42068528, HF-SARCOPENIA
PMID 41055780 — *"is in no retrieved artifact. Either the search did not return it, or it was written from
recollection."* **I re-ran it in my own scratch copy and got the identical refusal and exit code.** The child
did **not** weaken `check_anchors` to get past it, and neither did I. Related drift it flagged:
`emc-host-factor-inputs.json` now names PMID **42340948** for HF-SMOKING while the committed output carries
**41300991**.

## The consequence, computed the only way still available

With the generator refusing, the child applied **the generator's own arithmetic, quoted from `model_factor`**,
to the committed model's stored values, changing **only** the share — and **asserted** that the committed file
reproduces under that formula at 0.394 before computing the variant (assertions passed, exit 0). One variant,
no sweep; every prevalence, RRR range, transfer multiplier, status and PMID held fixed.

Share **0.394 → 0.217391**; ratio **0.5518**, i.e. current/new **1.8124**.

| output | current | recomputed |
|---|---|---|
| competing share (B) | 0.3940 | **0.2174** |
| share of all deaths (A) | 0.6060 | **0.7826** |
| HF-OBESITY exposed band | [0.0118, 0.0827] | **[0.0065, 0.0457]** |
| HF-SMOKING exposed band | [0.0449, 0.1261] | **[0.0248, 0.0696]** |
| HF-CV-RISK exposed band | [0.0118, 0.1143] | **[0.0065, 0.0630]** |
| every compartment-A output, and HF-SARCOPENIA | [0.0, 0.0] | **[0.0, 0.0]** — unchanged |

## Answer: it survives qualitatively, and not as a number

**Changes:** the "~40 % / ~60 %" split stated in the module docstring and `_readme` (now ~22 % / ~78 %), and
the `competing_share_source` sentence, which is **false as written today**. **Contracts by 1.8124×:** every
modelled compartment-B band — largest single move, HF-CV-RISK's exposed upper bound 0.1143 → **0.0630**.
**Unchanged:** the whole-model qualitative conclusion (compartment A is pinned to `[0.0, 0.0]`, so raising its
share moves nothing), `why_two_compartments`, the endpoint caveat, and the `limits` block. **The band does not
collapse; it keeps its sign and every attached qualitative statement, and it is 0.55× what the file implies.**

## Limits, binding and restated

The quantity is a **cohort death fraction** — **not population mortality risk, not a causal treatment effect,
not a bound on any antitumour argument**. This run **establishes no clinical benefit**: no efficacy, safety,
selectivity, therapeutic window or readiness, anywhere. The corrected band is a **model output, not a treatment
effect and not a patient-facing quantity**; nothing here is advice for any individual. All four prevalences are
imported from US general-population sources because no EMC series records a host factor; a share of deaths
averted is **not** a gain in life expectancy; the 5/23 estimator rests on **5 other-cause deaths** at ~3.2 years
median follow-up, with short follow-up flattering the share and censoring under-estimating it — **two biases in
opposite directions, neither corrected**; and pooling two strata that differ 30.8 % vs 10.0 % conceals stage
dependence. `factors_not_entered` stay **out of reach without network retrieval, unknown rather than zero**.

**Four owner acts are now named and none is taken:** the generator's unconditional estimator selection; its
false `competing_share_source` sentence; the **missing pooled `direct_cause_split` row**; and the HF-SMOKING
PMID drift. No manuscript, graph or repository change was made.
