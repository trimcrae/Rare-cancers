---
id: DOC-OPUS-CAMPAIGN-FP-PINNED-FIGURES-UNBOUND
title: "FP's central magnitude is unbound again — three pins point at a key path that no longer exists"
level: L4
kind: finding
status: live
date: 2026-09-08
last_verified: 2026-09-08
---

# FP's central magnitude is unbound again

**Diagnosis only. Nothing was fixed, and nothing should be fixed without adjudication** — repointing
a pin or editing a pinned quantity is substantive, and the FP guards are explicitly unadmitted for
rewrite. This converts an observation the FP author left as narrative into bound evidence.

## The reading, with real commands and measured exits

| # | command | exit | result |
|---|---|---|---|
| 01 | `python3 research/manuscripts/emc_fusion_partner_pooling.py --check` | **0** | the producer's own check is clean |
| 02 | `python3 research/manuscripts/lint_consistency.py` | **1** | `lint_consistency: 3 ERROR across 29 target file(s)` |

Run 02's three errors are exactly these:

```
ERROR [A-key-missing] fusion_partner_dod_fisher_p:
  cannot read key 'analyses.B_outcome_by_partner.disease_specific_death.fisher_exact_two_sided_p'
ERROR [A-key-missing] fusion_partner_dod_taf15_percent:
  cannot read key 'analyses.B_outcome_by_partner.disease_specific_death.taf15_arm.percent'
ERROR [A-key-missing] fusion_partner_dod_comparator_percent:
  cannot read key 'analyses.B_outcome_by_partner.disease_specific_death.comparator_arm.percent'
```

Resolved directly against the current artifact: **all three paths are MISSING.**
`analyses.B_outcome_by_partner` no longer contains `disease_specific_death` at all — its keys are
now `question`, `what_changed_2026_09_08`, `does_not_touch_the_response_question`,
`cohorts_identified`, `cohorts_pooled`, `pooled_cohorts`, `cohorts_excluded`, `⚠_roster_scope`,
`source_verified_recorded_outcomes`, `separate_descriptive_context_not_pooled`,
`what_is_not_established`.

**But the prose still states the figures.** Each pin's `context` regex still matches **exactly once**
in `emc-fusion-partner-stratification.md`: `7/15 = 46.7 %` and `6/58 = 10.3 %`.

## Why this matters more than a lint error

Pin `fusion_partner_dod_fisher_p` exists **because this exact failure already happened once**. Its
own description records it:

> *"⛔ THE PAPER'S HEADLINE STATISTIC, AND IT WAS UNBOUND. Found 2026-08-26 by two independent blind
> seats: §4.8's Limitations guarded a p = 0.0672 that appears NOWHERE else in the document — the
> retired Agaram-only value — while the live headline p = 0.0034 carried no caveat at all. Nothing
> cross-checked this paper's prose against its artifact: pinned-figures had no entry for it, and the
> generator's `--check` closes only the generator↔artifact loop."*

**The same failure mode has returned by a different route.** In August the guard was absent; today
the guard exists but **points at nothing**, so the paper's central magnitude — the TAF15-versus-
comparator gap, 46.7 % versus 10.3 % — is once again asserted in prose with **no artifact binding**.
And the producer's own `--check` exits 0, exactly as that description warned it would: it closes the
generator↔artifact loop and cannot see a dangling pin.

## What I did NOT do, and why

⛔ I did **not** repoint the three pins at a surviving key. That would restore a green lint while
leaving open whether the quantity still exists at all.
⛔ I did **not** edit or remove the prose figures, and I did **not** touch
`pinned-figures.json` — changing a pinned quantity is a recorded, substantive act, not a lint fix.
⛔ I did **not** re-run the FP producer, regenerate anything, or rewrite the FP guards (unadmitted).
⛔ **No value was changed to make a check pass**, and the `lint_consistency` failure is left standing.

## The three dispositions, for adjudication

1. **The analysis was legitimately restructured and the figures are retired** → the prose figures
   must go too, and the three pins retire with them.
2. **The analysis was legitimately restructured and the figures survive elsewhere** → the pins are
   repointed to the surviving path, and the equality of the values is demonstrated, not assumed.
3. **The quantity was lost in the restructure** → this is a substantive regression in the FP paper,
   not a bookkeeping problem, and the paper's central magnitude currently has no artifact behind it.

I cannot choose between these without deciding a scientific question that is not mine, and the
distinction is exactly what the blind seats caught last time. **Recorded, bound, and left open.**

---

## ⭐ ADDENDUM, 2026-09-08 — disposition 3 is now the live reading

The FP direct correction (author work, verified by me) did **not** touch the pins, and its
current-field work makes the diagnosis sharper. The three pins name a **pooled** disease-specific-
death node, and the current field now states there is **no pool**: *"no seven-death pool"* in
`emc-fusion-partner-pooling.json`, and *"one series in the main event analysis"* in the manuscript —
both verified live.

So the missing key is **not a stale path awaiting a re-point**. It is the **absence of the pooled
quantity** the prose figures `7/15 = 46.7 %` and `6/58 = 10.3 %` were bound to. That rules
disposition 2 out on the current evidence and makes **disposition 3** — the quantity did not survive
the restructure — the live reading.

⛔ Still not settled here, and still not acted on. What those two printed figures now denote is a
scientific question, `pinned-figures.json` remains untouched, and `lint_consistency` still exits 1
with the same three errors.

---

## ⛔ CORRECTION, 2026-09-09 — my central claim here was WRONG

**"The paper's central magnitude is asserted in prose with no artifact binding" is false, and the
error was mine.** I matched each pin's `context` regex against the manuscript, found one hit each,
and read those hits as live assertions. **I never checked what surrounded them.** They sit inside a
dated withdrawal:

```
402  ⛔ **The two-cohort pooled prognostic magnitude previously reported in this section is withdrawn.**
403  ⚠ *Superseded, retained: "Pooled over 73 patients, disease-specific death is 7/15 = 46.7 % (95 % CI
404  24.8–69.9) with TAF15::NR4A3 against 6/58 = 10.3 % (95 % CI 4.8–20.8) — a 36.3-point gap, post-hoc
405  Fisher p = 0.0034."*  Every figure in that sentence depended on cells transcribed from Huang 2023's
     Table 1, and no [...]
```

**The prose does not assert those figures. It withdraws them and retains the old sentence as a
quotation** — the same dated-supersession convention this campaign uses everywhere, including in my
own records. A regex cannot tell an assertion from its withdrawal, and I drew a conclusion the
method could not support.

### What this changes

* The three pins point at a removed key **because the quantity was deliberately withdrawn**, not
  because a live claim lost its binding. That is coherent bookkeeping lag, **not the August
  failure mode recurring** — and my framing of it as "the same failure, by a different route" is
  withdrawn with it.
* Of the three dispositions I recorded, **disposition 1** — the figures are retired and the pins
  retire with them — is the reading the evidence actually supports. My earlier addendum naming
  disposition 3 the live reading is superseded by this one.
* ⛔ **Do not repoint the pins.** The old nodes are *pooled* quantities over 73 patients; the current
  result is Agaram-only. Root's separate bounded mechanical comparison is distinguishing the two.
  Pointing a retired pooled node at a different cohort's values and keeping its name would
  manufacture continuity that does not exist.

### What still stands

The mechanical facts are unaffected and were measured, not inferred: the three paths **do not
resolve** in the current artifact; `emc_fusion_partner_pooling.py --check` exits **0** while
`lint_consistency.py` exits **1** with three `[A-key-missing]` errors; and the producer's own check
closes only the generator↔artifact loop, so it cannot see a dangling pin. Those remain **unresolved
maintenance evidence, not waived tests**, and guard maintenance remains **unadmitted**.

I did not repoint, restore or edit any pin, and `pinned-figures.json` is still untouched.
