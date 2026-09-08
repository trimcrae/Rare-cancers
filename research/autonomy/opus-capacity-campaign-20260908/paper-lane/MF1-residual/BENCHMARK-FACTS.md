---
id: DOC-MF1-RESIDUAL-BENCHMARK-FACTS
title: "MF1 residual R3 — the retained benchmark quantities, their provenance and their uncertainty meaning"
level: L4
kind: memo
status: live
date: 2026-09-08
last_verified: 2026-09-08
---

# R3 — the benchmark identities, references and results already in the register

⛔ **These are RETAINED REGISTER VALUES. They are not newly independently verified primary experiments.**
No benchmark was rerun, no simulation or calculation was performed, no primary benchmark publication was
retrieved, and no uncertainty was recomputed. What this batch did was **copy already-registered fields
into the reader-facing display with their provenance**, because the earlier draft reported the grades
("recovered within the accepted band", "large absolute bias") without the numbers behind them.

## The table, oriented as the source actually holds it

| instrument | benchmark identity (`known_answer_test`) | reference / known answer | result as recorded | discrepancy as recorded | uncertainty type |
|---|---|---|---|---|---|
| `V5` | reproduce a known ternary cooperativity | **+0.944** kcal/mol | **−0.599** kcal/mol | absolute error **1.543**; wrong sign in all 3 replicates | ⚠ **UNKNOWN** — no uncertainty term is attached to either value in this row |
| `V6` | TYK2 `ejm_31→ejm_42` relative-FEP benchmark ΔΔG | **−0.24** | **+0.37** | absolute error **0.61**, inside its operational **≈1 kcal/mol** band | ⚠ **UNKNOWN** |
| `V7` | T4-lysozyme L99A + benzene, absolute binding free energy | **−5.2** kcal/mol (experimental) | **+1.90 ± 0.09** | under-binding by **≈ +7.1** kcal/mol | ⚠ ± quoted on the **result only**; its kind is **UNKNOWN — not established in the cited record** |
| `V8` | methane hydration free energy (FreeSolv) | **+2.0** | **+1.60 ± 0.04** | *"approximately reproduced"* | ⚠ ± quoted on the **result only**; kind **UNKNOWN** |
| `V10` | barnase–barstar Y29A interface mutation vs a published ΔΔG | **+3.4** | **+4.42 ± 1.08** | recovered a large effect | ⚠ ± quoted on the **result only**; kind **UNKNOWN** |

## Provenance, to the field and the line

Every cell above is copied from `research/modalities/instrument-census.json`, fields
`instruments[id=…].known_answer_test` and `.result`:

| instrument | `known_answer_test` at | `result` at |
|---|---|---|
| `V5` | `:69` | `:71` |
| `V6` | `:84` | `:86` |
| `V7` | `:98` | `:100` |
| `V8` | `:112` | `:114` |
| `V10` | `:140` | `:142` |

That census is **generated, never transcribed**, from `research/manuscripts/nr4a3-program-map.md` §3.1 by
`research/modalities/instrument_census.py`. `instrument_census.py --check` returned **exit 0** on
2026-09-08 (`checks/02-…`), so the committed census is in sync with its roadmap source.

## ⭐ CURRENT, 2026-09-08 — the transposition is in the DERIVED CONTRACT only

**Which record is wrong: the derived contract, not the root memo.**

The 6,819-byte root adjudication memo states the five pairs **in source order — reference first, then
result**: *V5 +0.944 versus −0.599; V6 −0.24 versus +0.37; V7 −5.2 versus +1.90; V8 +2.0 versus +1.60;
V10 +3.4 versus +4.42.* That is correct and matches the retained source.

The transposition was introduced downstream, in
`CONTRACT-MF1-R1-R5-residual-author.md` (9,259 B, sha256
`4f93302c8e335415e48ddf8b92ed0a4dab01d38306c313888233193e5d9e37e4`), **written by the integrating
parent**, whose table **swapped the "reference" and "result" column headings** while copying the
memo's values. The error is the parent's, not root's.

**What determines the orientation: the named source fields, and only those.** In
`research/modalities/instrument-census.json`, `instruments[4]` (`V5`) reads
`known_answer_test = "reproduce a known cooperativity, **+0.944** kcal/mol"` and
`result = "**−0.599** — wrong sign in all 3 replicates"`. The field names settle it directly.

⛔ **WITHDRAWN: "the arithmetic only closes that way."** That argument was invalid. **Absolute error
is symmetric** — |+0.944 − (−0.599)| and |−0.599 − (+0.944)| are both 1.543 — so it cannot
distinguish reference from result and never could. The conclusion happens to be right, but it does
not rest on that reasoning and must not be defended with it.

⛔ **WITHDRAWN: the quoted restatements.** This file previously attributed *"V5 result +0.944 vs
reference −0.599"* and *"V7 … result −5.2 vs +1.90 ± 0.09"* to the root memo and the contract as
quotations. **Neither document contains those sentences.** They were constructed to illustrate the
transposition and should never have been presented inside quotation marks as the source's own words.

⛔ **The manuscript follows the retained source and is unchanged.** The root memo and the contract
stay **immutable**. No benchmark value was altered, the five rows above stand exactly as recorded,
and the five magnitudes are identical under either orientation. No new source, benchmark or review
was used to reach this.

### ⛔ SUPERSEDED, written earlier the same day

> *"A transposition in the commissioning records, recorded rather than propagated. The root
> adjudication memo and the derived contract state these pairs with reference and result swapped for
> all five instruments — e.g. "V5 result +0.944 vs reference −0.599", "V7 … result −5.2 vs +1.90 ±
> 0.09". The retained primary source and the focused verification report both give the opposite
> orientation, and the arithmetic only closes that way … ⛔ The manuscript follows the retained
> source, not the transposed restatement. The root memo and the contract are left immutable; this
> note is the dated record of the discrepancy."*

Three faults in that passage: it blamed the **root memo**, which was correct; it rested on the
**symmetric-arithmetic** argument, which proves nothing; and it presented **invented quotations** as
the sources' own words.

## What is deliberately omitted

- ⛔ **The `V5` register phrase *"~34× the statistical uncertainty"* is NOT carried forward.** The record
  does not supply the estimand such a ratio would need, and the related SD-over-SE multiplier (`3.28`) is
  withdrawn in corrective interpretation **C5**. No substitute multiplier is adopted.
- ⛔ **No uncertainty kind is named where the record does not establish it.** A ± that the register quotes
  without saying whether it is a standard error, a replicate standard deviation or a confidence interval
  is marked **UNKNOWN**, not guessed.
- ⛔ **No primary literature identifier is asserted for `V6`, `V7`, `V8` or `V10`.** The manuscript already
  states (§11) that these benchmark known answers are cited in this repository through their retained
  benchmark records, not through primary identifiers the author retrieved.

## The E1 leg accounting — 24 / 2 / 22, and why it is not one number

`research/modalities/selectivity-sensitivity-control-prereg.md`, **AMENDMENT 1** at `:26–31`:

- **24 legs** — the frozen design.
- **2 legs excluded before execution** — one co-fold model, **SMARCA4 seed 3**, on a *measured static
  input fault*, under a clause the document states was frozen in advance.
- **22 legs admitted** — the admissible panel, which is what executed and what `selcal-verdict.json`
  records as `n_legs_admitted`.

⛔ **These are DISTINCT from the collector stage.** `selcal-verdict.json` carries `rejected_records: []`
— **zero collector rejections** — and 0 technical failures in either arm. Zero rejected records is not
evidence that nothing was excluded; it is a different stage of the same pipeline, and the earlier display
reported only that stage. ⚠ The **sampling unit of the reported statistic is the co-fold MODEL** (6 versus
5 model means), not the leg: `selcal-verdict.json` `criterion.unit_of_independence` states that per-leg E1
values are collapsed to model means before the permutation.

⚠ The claim that the excluding clause was frozen in advance is **the retained protocol's own description**
(residual R2 / corrective interpretation C13); the chronology itself is unestablished. ⛔ This entry adds
an exclusion the record already held. It makes **no new eligibility decision**, re-runs nothing, and
constructs no all-identical structure set.
