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
