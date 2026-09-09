---
id: DOC-PORTFOLIO-INVESTIGATION-SURFACE-2
title: "SURFACE-2 — is the ALCAM immune-flag inconsistency one row or a class? A derived-flag vs source-annotation audit of emc-surface-normal-window.json"
level: L4
kind: audit
status: live
date: 2026-09-09
last_verified: 2026-09-09
---

# SURFACE-2 — derived-flag consistency audit

Branch `claude/confident-bardeen-ji76cd`. Offline, committed files only. **Nothing outside this
directory was written. No value, flag, window or classification was changed anywhere.** No commit,
no push, no preflight, no subagent, no network.

## 1 · The question

PUB-SURFACE-TARGETS recorded, and deliberately did not grade, one row: in
`research/modalities/emc-surface-normal-window.json`, ALCAM carries
`rna_blood_cell_specificity: "Immune cell enhanced"` beside `immune_or_circulating: false` and
`window: RESTRICTED`. **Is that one row, or a class?** And for every candidate in that file and the
related surface-target artifacts, does each derived flag actually follow from — and is it supported
by — the free-text annotation it is supposed to summarise?

## 2 · Answer

**It is a class, and ALCAM is a member of two of them at once.** The audit found **six distinct
consistency classes over 47 audited candidates** (46 antigen rows plus one cross-artifact flag).
**Zero candidates come through with every derived flag both rule-faithful and source-supported.**

**The firm distinction the task asks for, stated once:** inside
`emc-surface-normal-window.json` there is **not a single transcription slip**. Every serialized
value is exactly what the producer's rule computes from the text beside it. Three independent
transcription checks all pass (§4). **Every hit in that file is therefore a PRODUCER error — a rule
that mis-summarises its own input — and re-running the producer would reproduce all of them
identically.** The audit's **only DATA error** (a stale value that re-derivation alone would fix)
is a single cross-artifact membership flag in a *different* file.

| Class | What is inconsistent | Rows | Kind | Changes a window? |
|---|---|---:|---|---|
| **C1** | `immune_or_circulating: false` beside `"Immune cell enhanced"` | **9** | PRODUCER | No — see §3.1 |
| **C2** | `vital_tissue: []` derived from a `rna_tissue_specific_nTPM` that is `null` | **45 / 45 scored** | PRODUCER | No — the branch never fires |
| **C3** | `window: RESTRICTED` (glossed "confined to one/few tissues") beside `"Detected in many"` | **3** | PRODUCER | No — label stands, its gloss does not |
| **C4** | `window` differs from the mapping the file's own `_note` publishes | **3** | PRODUCER | Yes vs one source field, no vs the pair |
| **C5** | `plasma_membrane_confirmed: false` on a `null` `subcellular_location` | **8** | PRODUCER | No — does not feed `classify()` |
| **C6** | `in_emc_surface_normal_window: false` for a gene that **is** in that file | **1** | **DATA** | No |

## 3 · The hits, verbatim

### 3.1 · C1 — the ALCAM class, 9 rows (PRODUCER)

**ALCAM, CD70, DLL3, EPHB4, ERBB2, GPC3, IGF1R, MSLN, PDGFRB.**

* **Source** (verbatim, from HPA, faithfully transcribed): `"rna_blood_cell_specificity": "Immune cell enhanced"`
* **Derived** (verbatim): `"immune_or_circulating": false`

The rule is `immune_flag = "enriched" in blood_spec.lower()`
(`emc_surface_normal_window.py:classify()`). `"Immune cell enhanced"` does not contain "enriched",
so the flag is `false` — **rule-faithful, and not a transcription slip**. The producer error is that
a field named `immune_or_circulating` reports **`false` for an antigen whose own annotation reports
immune-cell expression**. The flag tests *confinement* ("enriched"); its name asserts *presence*.
The code comment states the rule, but the artifact a downstream reader consumes carries only the
name and the boolean.

**Why the threshold is where it is — measured, not inferred** (`checks/04-c1-rule-sensitivity`).
Under a literal reading of the field name, all nine rows would become
`VITAL_OR_IMMUNE_LIABILITY` — **including DLL3 and GPC3, the file's own two RESTRICTED positive
controls**, breaking `self_validation`. The committed threshold is the one that keeps those controls
passing, and the code comment says so. **ALCAM's blood-cell annotation sits in the same band as
those two controls.** Of the six `restricted_window_candidates`, ALCAM is the only one that band
touches.

⛔ **Nothing here demotes ALCAM, changes its window, or removes it from any list.** The audited
defect is that `immune_or_circulating: false` is not supported by the text beside it. Whether the
"enriched"-only threshold is the right liability rule is a scientific question this audit does not
decide and has no standing to decide.

### 3.2 · C2 — the vital-tissue screen never ran, on any row (PRODUCER)

* **Source**: `"rna_tissue_specific_nTPM": null` — **null on all 46 rows**, exactly as
  PUB-SURFACE-TARGETS measured (0 of 46 carry a quantitative tissue nTPM).
* **Derived**: `"vital_tissue": []` — on **all 45 scored rows**.

`vital_hits` substring-matches the 21 `VITAL_TISSUES` labels against `json.dumps(specific_tpm)`.
When that input is `null` the match is vacuous, so `[]` is guaranteed. `classify()` never reads
`rna_tissue_distribution` on this path.

**This is the largest finding in the audit.** The file's `_note` defines
`VITAL_OR_IMMUNE_LIABILITY` as "expressed in a vital tissue **or** immune/circulating cell", and the
`vital_tissues_flagged` block advertises a 21-tissue screen. **The vital half of that verdict has
never fired for any gene in this file, because its input has never been present.** Every
`VITAL_OR_IMMUNE_LIABILITY` in the artifact was set by the immune half alone. `vital_tissue: []` is
an absent reading rendered as a negative finding — CLAUDE.md §4's "a missing measurement is unknown,
not zero", in serialized form. **No window changes**, and that is precisely the problem: no window
in the file has ever been screened against a vital tissue.

### 3.3 · C3 — RESTRICTED beside "Detected in many", 3 rows (PRODUCER)

**ALCAM, B4GALNT1, GPC3.**

* **Source**: `"rna_tissue_distribution": "Detected in many"`
* **Derived**: `"window": "RESTRICTED"`, glossed in `_note` as *"confined to one/few tissues"*

The label is correctly derived from `rna_tissue_specificity: "Tissue enriched"`. HPA's "enriched"
is an *elevation* statement (≥4x one tissue), not a *confinement* statement, and the distribution
field beside it says the transcript is detected in many tissues. **The verdict label is defensible;
the `_note`'s gloss on it is not supported by the row's own second field.** The other three
`restricted_window_candidates` — PRAME, MAGEA4, ALPP (`"Detected in some"`) and CTAG1B
(`"Detected in single"`) — are clean on this axis. So the RESTRICTED list splits **4 supported, 2
not** (ALCAM, B4GALNT1), on the distribution field alone.

**ALCAM is the only candidate that is a member of both C1 and C3.** That is the honest answer to
"one row or a class": the *classes* are real and populated, and ALCAM's original salience is that it
is the only row where two of them land together on a candidate that is currently RESTRICTED.

### 3.4 · C4 — the published legend under-determines its own rows, 3 rows (PRODUCER)

**MCAM, TNC, CD44.** Stated narrowly, because this one is weaker than the others and should not be
overstated: on these rows **two source criteria collide**.

* MCAM — **source A** `"rna_tissue_specificity": "Group enriched"` (a `_note` RESTRICTED criterion);
  **source B** `"rna_tissue_distribution": "Detected in all"` (a `_note` BROAD_LIABILITY criterion).
  **Derived**: `"window": "BROAD_LIABILITY"`.
* TNC, CD44 — `"Tissue enhanced"` (ENHANCED_BROAD criterion) with `"Detected in all"` (BROAD
  criterion) → `BROAD_LIABILITY`.

`classify()` resolves the collision distribution-first. The `_note` lists both criteria and
**states no precedence**, so the artifact's published legend cannot reproduce its own rows. This is
a legend/rule mis-summary, **not a flat contradiction**, and no standing changes: MCAM, TNC and CD44
are liability rows either way.

### 3.5 · C5 — an unperformed check serialized as a negative, 8 rows (PRODUCER)

**B4GALNT1, CDH11, EPHB4, FAP, GPC2, ROR1, ROR2, TNC.**
`"subcellular_location": null` → `"plasma_membrane_confirmed": false`, via
`bool(subcell and ...)`. The same failure shape as C2: HPA reported nothing, and the artifact says
`false` where the truth is "not checked". This field does not feed `classify()`, so **no window
changes**; it is a per-row provenance defect, and `plasma_membrane_confirmed: false` is exactly the
"populated field that is not a measured one" the producer's own docstring warns against elsewhere.

### 3.6 · C6 — the audit's only DATA error, and it is in another file (DATA)

`research/modalities/surfaceome-instrument-limits.json`,
`limits.L4_cspg4_coverage_gap`:

* **Derived** (verbatim): `"in_emc_surface_normal_window": false`
* **Source** (verbatim): `emc-surface-normal-window.json` → `antigens.CSPG4.window: "ENHANCED_BROAD"`

The producer computes this live as `"CSPG4" in json.dumps(normal_window)`
(`surfaceome_instrument_limits.py:277`). Recomputed against the committed normal-window file it is
**True** (`checks/07-c6-stale-flag`). The committed `false` predates the run that added CSPG4 —
CSPG4 is listed in that file's own `_drift_vs_previous_artifact.newly_added_this_run`. **This is a
staleness slip, not a rule defect: the rule is correct and re-running the unchanged producer fixes
it.** It does not change CSPG4's window and does not disturb the L4 coverage-gap argument, which is
about the *surfaceome scan* instrument, not about this file.

## 4 · What came through clean (the checks that found nothing)

Reported because a null result is the load-bearing half of the DATA/PRODUCER split:

* **Field duplication** — `blood_cell_specificity` vs `rna_blood_cell_specificity`: **0 mismatches / 46**.
* **`plasma_membrane_confirmed` vs its own rule** — **0 mismatches / 45 scored** (the C5 hit is the
  rule's treatment of `null`, not a mis-application of it).
* **Top-level lists vs the rows they summarise** — `restricted_window_candidates` (6),
  `liability_antigens` (35) and `broad_liability` reproduce the per-row `window` values **exactly**,
  with only the four controls excluded, as the producer intends. No membership drift.
* **The `_status` row** — ALPPL2, `"symbol mismatch — record DISCARDED, nothing scored"`, carries
  no derived flag at all. Correct behaviour: nothing to contradict.
* **The "enriched" substring test** is latent-fragile (it would fire on a hypothetical
  `"Not immune cell enriched"`), but **no such value occurs in the data**. Recorded as latent, not
  counted as a hit.

## 5 · Artifact · validation · provenance · limitations · stop condition

* **Artifact** — `WINDOW-CONSISTENCY-AUDIT.tsv` (47 rows, one per candidate, with verdict, hit
  classes and the verbatim conflicting pair), `HITS-DETAIL.tsv` (70 rows, one per hit),
  `UNAPPLIED-DIFF.patch`, `window_consistency_audit.py`, `c1_rule_sensitivity.py`, `checks/01`–`07`.
* **Validation** — both scripts are read-only and open no file for writing outside this directory;
  `git status` confirms `research/modalities/` is unmodified. Every class is stated as an executable
  predicate over committed JSON, so each hit is reproducible and falsifiable by re-running the audit
  against the file. C1's consequence and C6's staleness are each verified by independent
  recomputation of the producer's own expression. `checks/01-audit` preserves a genuine failure
  (wrong `ROOT` depth, `FileNotFoundError`, exit 1) rather than only the run that worked.
* **Provenance** — `research/modalities/emc-surface-normal-window.json` (46 antigen records) and its
  producer `research/modalities/emc_surface_normal_window.py`;
  `research/modalities/surfaceome-instrument-limits.json` and
  `surfaceome_instrument_limits.py`. Related surface-target artifacts inspected and found **out of
  this audit's class**, because their booleans derive from numbers rather than from free-text
  annotations: `surface-address-sensitivity.json` (`sign_flip`, `eligible`),
  `nr4a3-differential-surface-atlas.json` (`exposed` from SASA), `emc-surfaceome-scan.json`
  (`selectivity_significant` from q-values), `emc-expression-panels.json`, `alcam-precedent.json`
  (prose + citations; it carries no derived flag, and its
  `_why_this_does_not_contradict_the_RESTRICTED_window` block already reasons about the same gap
  from the biology side).
* **Limitations** — this is a **self-consistency audit of an artifact against its own recorded
  source text and its own producer**. It is **not** a check of HPA, not a re-derivation of any HPA
  value, and **not a protein, surface-localisation, selectivity, safety or therapeutic-window claim
  about any antigen**. It cannot say which of two colliding source fields is biologically right. The
  transcription checks verify the artifact against the producer's rule, **not** against HPA's live
  records, which are unreachable offline; a slip introduced upstream of the recorded field would not
  be visible here.
* **Stop condition** — reached. The class question is answered with a bounded, reproducible count.
  ⛔ **No candidate's standing changes on this audit's say-so, and no fix is applied.**

## 6 · The unapplied diff, and which class each hunk addresses

`UNAPPLIED-DIFF.patch` — against `research/modalities/emc_surface_normal_window.py`, the **producer**,
because five of the six classes are producer errors and editing the JSON would leave the next run to
reintroduce them. **Verified to apply cleanly** (`git apply --check`, exit 0,
`checks/06-patch-applies`) and to compile (`checks/05-generate-diff`). **It is not applied, and it
is not to be applied by this lane.**

| Hunk | Class | Change | Effect on any window |
|---|---|---|---|
| 1 | **C2** | serialize `vital_tissue_screen` beside `vital_tissue`, saying whether the screen ran | none — additive |
| 2 | **C1** | serialize `immune_cell_expression_reported` (the literal reading) and `immune_liability_rule` beside the unchanged `immune_or_circulating` | **none — the flag's value and the rule are untouched by design** |
| 3 | **C5** | `plasma_membrane_confirmed: None` instead of `false` when HPA reported no location | none — field does not feed `classify()` |
| 4 | **C3, C4** | state the branch **precedence** in `_note`, and correct its RESTRICTED gloss from "confined to one/few tissues" to an elevation statement that points the reader to `rna_tissue_distribution` | none — legend text only |

**C6 gets no diff.** It is the DATA error, and its remedy is different in kind: re-run the unchanged
`surfaceome_instrument_limits.py` so the flag re-derives to `true`. A code change there would be the
wrong repair.

⛔ **This diff deliberately changes no threshold, no rule outcome, no verdict and no list.** Whether
the C1 "enriched"-only liability threshold should move is a scientific decision for the artifact's
owner; it would flip both RESTRICTED positive controls and one candidate, and this lane neither
recommends nor makes it.

## 7 · Next credible independent work

1. **The C2 dependency is the real one**: `rna_tissue_specific_nTPM` is null on all 46 rows, so the
   vital-tissue screen has no input. Requesting HPA's per-tissue nTPM column (`rnatss` is already in
   the producer's query string, and it comes back empty) is what would make the vital half of
   `VITAL_OR_IMMUNE_LIABILITY` a real screen rather than a dead branch. That is a networked fetch and
   is out of scope here.
2. Owner decision on C1: keep the confinement threshold (and rename the flag), or widen it (and
   accept what it does to DLL3/GPC3). **Not this lane's call.**
3. Re-run `surfaceome_instrument_limits.py` to clear C6.
