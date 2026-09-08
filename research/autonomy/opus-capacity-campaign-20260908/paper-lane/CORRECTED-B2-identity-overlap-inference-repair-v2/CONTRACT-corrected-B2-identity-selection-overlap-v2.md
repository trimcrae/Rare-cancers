---
id: DOC-OPUS-CAMPAIGN-CORRECTED-B2-IDENTITY-SELECTION-OVERLAP-V2
title: "Corrected contract B2 — identity / selection / overlap, inference strength repaired"
level: L4
kind: contract
status: live
version: v2
sibling_of: research/autonomy/opus-capacity-campaign-20260908/paper-lane/CORRECTED-B-identity-selection-overlap/
supersedes: nothing
relation_to_v1: >
  New explicitly versioned sibling. Every byte of the v1 component — its contract, schema,
  data-sufficiency statement, builder, checks and all 12 artifacts — is untouched and its
  historical claims stand as the record of what v1 actually asserted (check V1, check V12).
  This contract repairs the INFERENCE STRENGTH of v1's identity and relation labels; it repairs
  no data, re-runs no job and re-computes no quantity from source.
audience: [maintainers, external reviewers, autonomous research agents]
date: 2026-09-08
last_verified: 2026-09-08
---

# Corrected contract B2 — the encoding/semantics repair

⛔ **This contract states no response rate, no unique-patient total, no capacity bound, no control
comparison and no clinical comparison.** The endpoint manuscript stays **parked**; it was neither
read nor edited. Nothing here was committed or pushed. No source query was made, job 2 was not
re-run, and no leaf analysis was re-run.

## 1 · The defect being repaired

v1 ran one comparison: for each cohort key with more than one observation, are the competing
records **identical on every preserved identity field**? The answer was no, everywhere — 0 of 4,464
sets identical.

v1 then wrote two sentences that the comparison does not support. Both are **WITHDRAWN as v2
statements** and are quoted here only as the v1 text they replace:

> *(v1, WITHDRAWN)* "Genuinely duplicate encodings do not occur in this cache."

> *(v1, WITHDRAWN)* "every one of them is **a distinct outcome, time point or population** rather
> than a re-encoding of the same measurement."

**Different preserved strings establish NON-IDENTICAL ENCODINGS. They do not establish that any
pair is a genuinely distinct clinical measurement or population.** A record entered twice in
different words differs on preserved fields and is still one record. The v1 sentences convert an
encoding comparison into a semantic conclusion, and that is the overclaim.

The v1 rows themselves — the identity fields, the competing observation sets, the counts — are
correct and are kept. Only the reading of them changes.

## 2 · What v2 asserts instead

| quantity | v2 statement |
|---|---|
| cohort keys | 8,740, unchanged and in the same order (check V3) |
| competing sets (>1 observation) | 4,464, unchanged |
| identical on every preserved field | 0 — `IDENTICAL_ON_ALL_PRESERVED_FIELDS` |
| non-identical encodings | 4,464 — `NON_IDENTICAL_ENCODING_ON_PRESERVED_FIELDS` |
| semantically resolved | **0.** All 4,464 carry `UNRESOLVED__SEMANTIC_CORRESPONDENCE_NOT_ESTABLISHED` (check V4) |
| separated by free-text-derived fields only | **1,744** — `distinction_basis = TEXT_DERIVED_ONLY` |
| separated with at least one structured field (paramType, denominator value, outcome-measure type, denominator state) | 2,720 |

⚠ **Semantic duplication and overlap are left explicitly UNRESOLVED wherever correspondence has
not been established** — which is everywhere in this component. The 1,744 text-only cases are
flagged, not resolved and not merged.

⛔ **No normalisation** of unit order, signs, case, spacing or misspellings is performed anywhere,
and ⛔ **no preferred endpoint, criteria version, time point, population or selection rule** is
introduced. `selection_status` remains `NOT_SELECTED_BY_DESIGN` on all 8,740 rows.

The corrected labels are carried in `artifacts/RELATED-SETS-encoding-vs-semantics-v2.tsv`, in
`SCHEMA-v2.json`, and in `DATA-SUFFICIENCY-v2.md` — the three places where v1 actually carried the
old ones.

## 3 · Parent / component relations at their real evidence strength

v1 emitted 47 parent→component relations and labelled every one `POOLED_PARENT_WITH_COMPONENTS`,
inferred from a pooled-word regex over the normalised group title. ⛔ **A name is not evidence that
a parent and its components are the same people.** The 47 relations are preserved row for row, with
v1's parent, component and denominator columns carried verbatim (check V7), and re-labelled:

| relation_status | rows | what the evidence is |
|---|---|---|
| `SOURCE_STATED_PARENT_COMPONENT_RELATION__COMPONENTS_NAMED_IN_RECORD` | **11** | an exact record field enumerates the components or states the pooling arithmetic — e.g. `results_group_title` "Total (Equals AM Plus PM Dose) Sunitinib Malate"; `results_group_description` "Cohort A and Cohort B combined" |
| `SOURCE_DESCRIBED_SUPERSET_LANGUAGE__COMPONENTS_NOT_NAMED` | **10** | the field uses all-participants/superset language but names no component group |
| `CANDIDATE_PARENT_COMPONENT_RELATION__NAME_PATTERN_ONLY` | **26** | the only basis is the pooled-sounding title |

Every row records **the field that carries the evidence** (`relation_evidence_field`), its
**verbatim text** (`relation_evidence_text`), and an explicit `same_patients_claim`. For the 26
name-only rows that claim reads **NOT ESTABLISHED**.

v1's operative safeguard is **kept unchanged**: `component_sum` exists only to expose double
counting against the parent, and parent and components are **never added together**. What is
withdrawn is the assertion that they *are the same people* on name evidence alone.

## 4 · Denominators and metadata states — wording made exact

**"Denominator usability" means a positive reported Participants denominator at THIS component's
scope.** It is **not** a statement of eligibility, of analysis-population membership, or of fitness
for any downstream estimand. A row marked usable here may be unusable for any actual analysis.

**Source non-collection and an absent `reportingStatus` field remain two separate metadata
states** and are never collapsed into each other or into a missing value:

| state | v1 output carried forward | meaning |
|---|---|---|
| explicit non-collection / termination statement | 639 observations | the record says data were not collected, not analysed, or the study terminated — preserved verbatim |
| `reporting_status_state = ABSENT_FIELD` | 15 observations in 10 trials | the record carries no `reportingStatus` field — a metadata gap, not evidence that data are absent |
| `REPORTED_ZERO` denominator | 1,282 observations, 287 trials | a source fact, never a divisor, never an observed zero-response cohort |

These counts are **v1 outputs carried forward**, not re-derived here.

## 5 · The excess categories, reconciled

The v1 table listed `WITHIN_MEASURE_SUM_EXCEEDS_ENROLLMENT` = 70 with "…and that measure contains a
pooled/total group" = 35 **indented beneath it**, and the v1 prose then said "only **106** trials
exceed enrollment, 35 of them…". The 35 is not a subset of the 70, and 70 and 106 are two different
quantities. As the schema actually defines them:

| category | trials | exclusivity |
|---|---|---|
| exact label `WITHIN_MEASURE_SUM_EXCEEDS_ENROLLMENT` | **70** | disjoint |
| exact label `…__POOLED_LABEL_IN_MEASURE` | **35** | disjoint |
| exact label `SINGLE_COHORT_EXCEEDS_ENROLLMENT__…` (NCT00756509, 41 vs 34) | **1** | disjoint |
| membership view: any within-measure excess | **106** | **non-exclusive** — the union of the three above |
| `NO_CONFLICT_DETECTED` | 2,536 | disjoint |

⛔ **No total is manufactured.** 106 is stated as a membership view, not as a fourth category, and
the three exact labels are the partition (check V8).

⚠ The single-cohort trial's measure holds **exactly one group**, so its "within-measure sum" *is*
that one cohort — not an additional summation phenomenon inside the 106. The 41-vs-34 conflict
stands as recorded; no field is declared wrong and nothing is clipped.

## 6 · The negative control

`negative_control.py` builds one synthetic record entered **twice with harmless wording
differences** — capitalisation, an abbreviated month unit, a hyphen, "patients" vs "participants",
a misspelled criteria token — with the same paramType, the same Participants denominator and the
same reported value. Three assertions, real exit code (check V9, exit 0):

* **NC1** v1's rule reports **no** duplicate-encoding candidate for it. Under v1's sentence this
  pair would be called "a distinct outcome, time point or population". **The control exposes the
  overclaim.**
* **NC2** v2 labels it `NON_IDENTICAL_ENCODING_ON_PRESERVED_FIELDS`, `TEXT_DERIVED_ONLY`,
  semantics `UNRESOLVED` — a statement about encodings only.
* **NC3** ⛔ **Neither rule merges, normalises or rewrites a clinical record.** Both observations
  survive byte-identical, and the contrasting genuinely-different pair is left unresolved too, so
  the v2 label cannot be used to merge anything.

The control is entirely synthetic. No source record is read, written or altered by it.

⚠ The control's **first run failed** (`evidence/negative-control-attempt-01.{out,err}`, exit 1):
a pure case difference in `unitOfMeasure` was being counted as a *structured* distinction. The fix
was to classify `unitOfMeasure` as the free-text string it is — a **classification** change, not a
normalisation. Both the failing and the passing attempt are preserved.

## 7 · Checks — real exit codes

```
$ python3 relabel_v2.py      ; echo RELABEL_EXIT=$?          -> RELABEL_EXIT=0
$ python3 negative_control.py; echo NEGATIVE_CONTROL_EXIT=$? -> NEGATIVE_CONTROL_EXIT=0
$ python3 checks_v2.py       ; echo CHECKS_EXIT=$?           -> CHECKS_EXIT=0   (12/12)
```

Every attempt is preserved in its own file under `evidence/`; no failure was overwritten. A check
that cannot run is a FAIL and the process exits 1.

## 8 · What this contract does NOT do

1. It re-runs **no** job 2, **no** leaf analysis, and makes **no** source query. It reads only v1's
   emitted artifacts.
2. It changes **no** v1 byte and withdraws **no** v1 row — only v1's readings of them.
3. It introduces **no** preferred endpoint, no selection rule and no normalisation.
4. It merges **no** clinical record and resolves **no** semantic duplication or overlap.
5. It emits **no** rate, unique-patient total, capacity bound or control analysis (check V10).
6. It makes **no** manuscript change. The endpoint paper stays parked.

## 9 · Artifacts

| file | rows | note |
|---|---|---|
| `artifacts/RELATED-SETS-encoding-vs-semantics-v2.tsv` | 8,740 | corrected encoding/semantic labels, v1 states carried alongside |
| `artifacts/GROUP-RELATIONS-candidate-parent-component-v2.tsv` | 47 | relation status, evidence field, verbatim evidence text |
| `artifacts/ENROLLMENT-EXCESS-CATEGORIES-v2.tsv` | 5 | the disjoint partition and the membership view |
| `artifacts/CHANGE-MAP-v1-to-v2.tsv` | 14 | every changed statement and label, with its v1 and v2 location |
| `artifacts/NEGATIVE-CONTROL-wording-only-duplicate.json` | — | fixture, both rules' output, three assertions |
| `artifacts/RELABEL-SUMMARY-v2.json`, `artifacts/CHECKS-v2.json` | — | census and machine-readable checks |
| `evidence/` | — | every run attempt, stdout/stderr/exit, and the v1 baseline hashes |
