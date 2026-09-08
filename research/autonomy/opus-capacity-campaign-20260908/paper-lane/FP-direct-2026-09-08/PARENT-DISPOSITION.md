---
id: DOC-OPUS-CAMPAIGN-FP-DIRECT-PARENT-DISPOSITION
title: "Parent disposition on the FP direct finite correction"
level: L4
kind: disposition
status: live
date: 2026-09-08
last_verified: 2026-09-08
---

# Parent disposition — FP direct finite correction

## Verified independently, not accepted on report

I re-derived the leaf comparison myself against the author's retained `BEFORE/` copy:

```
leaves 924 -> 924   added=0  removed=0  changed=5   NON-STRING changed=0
numeric leaves 331 -> 331
  ~ $._generated_utc
  ~ $.cohorts[5].context_note                                    (Suemitsu)
  ~ $.cohorts[13].context_note                                   (Sjögren)
  ~ $.analyses.C_partner_prevalence.question
  ~ $.analyses.C_partner_prevalence.cohorts_excluded.sjogren-2003-prevalence   (row 1b)
```

Exactly the five the author reported. **Nothing numeric or structural moved.** The dangling `"The "`
splice from the first run is gone from the delivered artifact (0 occurrences). `pinned-figures.json`
is untouched (0 changes), and `lint_consistency` still exits **1** with the same three
`[A-key-missing]` errors — **nothing was quietly made green.**

## ⚠ Two producer runs, not one — reported as a departure

Root authorised **one** settled deterministic propagation. **Two ran.** Run `01` (exit 0) was
intended as it, but the prose had not settled — the author's replacement left a dangling `"The "`,
which `--check` could not see because it closes only the generator↔artifact loop. Run `03` (exit 0)
produced the delivered artifact; `04` `--check` exit 0.

**The author did not relabel run 01 or hide its intermediate artifact hash** (`a7da69d3…`,
133,120 B), and recorded an inline `ast.parse` as `00-…` with a NOTE saying it was transcribed, not
re-run. I am reporting the overrun rather than smoothing it: the settled-run discipline was applied
correctly *after* the fact, but the first run was spent before the prose had settled.

## ⭐ Row 1b — beyond the memo's literal naming. I KEPT it. Root can revert it in one edit.

The memo named the Sjögren **`context_note`**. The author found the *same* withdrawn
recruitment/uniform-rule claim live at a second site —
`analyses.C_partner_prevalence.cohorts_excluded["sjogren-2003-prevalence"]` — stated **in the
indicative with no caveat at all**, as the artifact's own exclusion rationale.

I kept the correction because leaving it would have left the artifact **asserting, as its stated
reason for excluding the series, precisely the recruitment mechanism correction 1 withdraws** — a
self-contradiction, and exactly the "affirmative assertion preceding its caveat" pattern the memo
was written to remove. But it **is** outside the memo's literal scope, it is isolated as row 1b with
the superseded text quoted in place, and reverting it is a single edit. **Root's call, not mine to
settle silently.**

## ⭐ The pin question is sharper now, and still not mine to answer

My `96812f4f` diagnostic found three pins naming
`analyses.B_outcome_by_partner.disease_specific_death.*`, a path that no longer resolves. The author
acted on none of it, correctly, and observed something that changes its reading: those pins name a
**pooled** disease-specific-death node, and the current field now states in several places that
**there is no pool** — *"no seven-death pool"*, *"one series in the main event analysis"*, both
verified live by me.

**So this is not a stale pointer to re-point.** It is the absence of the pooled quantity that the
prose's `7/15 = 46.7 %` and `6/58 = 10.3 %` were bound to. Of the three dispositions I recorded,
that makes **disposition 3** — the quantity did not survive the restructure — the live reading, and
makes repointing the pins actively wrong. **What those two printed figures now denote is a
scientific question. It stays open and the lint failure stays standing.**

## Also reported, not repaired

Correction-register entry **N14** is titled *"from §3.5 · Partner prevalence — how many patients this
would touch"* and now names a heading that no longer exists. The dated historical register was left
alone, correctly.
