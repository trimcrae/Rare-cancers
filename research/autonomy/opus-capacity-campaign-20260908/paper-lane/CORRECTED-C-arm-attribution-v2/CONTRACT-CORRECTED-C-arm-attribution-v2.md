---
id: DOC-OPUS-CAMPAIGN-CORRECTED-C-ARM-ATTRIBUTION-V2
title: "CORRECTED-C v2 — arm attribution with the narrative-token confirmation predicate removed"
level: L4
kind: contract
status: live
purpose: >
  Replace CORRECTED-C v1's leaf-narrative token test for confirmation with verification against the
  exact fields of the cached source record, keeping every unverifiable leaf claim as PROPOSED with
  its locator, separating label correspondence from source-confirmed arm identity, separating
  registry arm type from clinical comparator role, and preserving ambiguity instead of binding the
  first compatible arm.
scope: >
  L4. Source-validation evidence only, over the delivered immutable cache copy and the already
  delivered leaf outputs. No response rate, no unique-patient total, no control comparison, no
  clinical comparison, no manuscript repair, no publication act.
audience: [maintainers, external reviewers, autonomous research agents]
date: 2026-09-08
last_verified: 2026-09-08
related: [DOC-OPUS-CAMPAIGN-CORRECTED-C-ARM-ATTRIBUTION, DOC-OPUS-CAMPAIGN-CURATION-ARM-ATTRIBUTION]
---

# CORRECTED-C v2 — a new, explicitly versioned sibling

⛔ **The endpoint manuscript stays parked.** No response rate, no unique-patient total, no control
comparison, no clinical comparison and no manuscript revision is produced or authorised here.

## 0 · What this is, and what it does not touch

`CORRECTED-C-arm-attribution/` (v1), `CURATION-endpoint-arm-attribution-*` (Job 3) and the 16
`LEAF-OUT/` analyses are **immutable evidence of the runs that actually happened**. Not one byte of
them is edited, moved or re-graded in place; Job 3 was not re-run. **Their historical claims stand
as claims that were made** — including v1's 503 CONFIRMED rows and its checks JSON showing 13/13
PASS. This directory disagrees with 494 of those rows and says so in the change map, which is a
different thing from pretending they were never asserted.

## 1 · The defect this repairs

v1's producer, lines 107–130:

```python
CORROBORATION = ('description','interventionnames','bijection','complement','partition',
                 'enumerat','verbatim','reproduced','drug set','elimination')
...
corr = any(t in f for t in CORROBORATION)
if corr:
    return ("CONFIRMED", "LEAF_WITHIN_RECORD_RELATION")
```

`f` is a leaf's **free-text narrative**. The predicate therefore establishes **what a leaf narrative
mentioned, not that a source relation was verified**. A narrative saying *"the description is absent
and armGroups[*].interventionNames are identical, so no verbatim field supports elimination of
either arm"* contains four of the ten tokens and was promoted to CONFIRMED. **314 rows** in the v1
map carry `arm_link_evidence_code = LEAF_WITHIN_RECORD_RELATION`. They were not corroborated; they
were only *described*.

## 2 · The rules v2 applies instead

| # | rule | where |
|---|---|---|
| 1 | **No narrative is ever parsed for meaning.** The leaf's text is carried verbatim in `leaf_narrative_verbatim_not_parsed` as evidence for a human, and a producer self-check scans its own body to prove no expression tests it. | `verify_leaf_claim`, check `no_narrative_token_corroboration_predicate_remains` |
| 2 | **Confirmation comes only from equality between two exact fields of one cached record.** `SOURCE_CONFIRMED` requires a unique label identity **and** a unique description identity naming the same arm, or a unique description-field identity alone. | `source_relations`, `decide_link` |
| 3 | **Unique identical labels are preserved as `LABEL_MATCH`** with the exact field path, and never silently become a stronger clinical assignment. Where they carry a comparator type the role is `COMPARATOR_PROPOSED_BY_LABEL_MATCHED_ARM_TYPE`, with the assumption written into `registry_type_statement_assumption`. | `decide_link`, `decide_comparator` |
| 4 | **Where exact source evidence is absent the leaf's claim is retained as `PROPOSED`/UNVERIFIED with its locator** (`LEAF-OUT/<file>:line N` plus the candidate `armGroups[i].label`), never promoted and never dropped. | `decide_link` |
| 5 | **Contrary source evidence downgrades.** v1's monotonic "a leaf may only strengthen; never downgrade an exact match" is withdrawn. | `decide_link`, `decide_comparator` |
| 6 | **Ambiguity is preserved.** v1's `next((a for a in ai if …), arm)` is withdrawn: `n_candidate_arms` records the exact count and an arm binds only at 1. | `unique_or_none`, check `two_or_more_candidates_never_select_the_first` |
| 7 | **Cardinality and uniform arm type are CONDITIONAL type statements**, with the membership assumption in machine state, never an unconditional `NOT_CONTROL`. The token `NOT_CONTROL` does not occur as a state anywhere in the table. | `decide_comparator`, checks `no_unconditional_NOT_CONTROL_state_in_the_table`, `every_conditional_type_statement_names_its_assumption_in_machine_state` |
| 8 | **Clinical comparator role and registry type are distinct columns**, and the registered type is kept verbatim. EXPERIMENTAL/OTHER yields `NOT_ESTABLISHED_IN_THIS_CACHE` — absence of evidence, not evidence of absence. | `decide_comparator` |
| 9 | **Four unknowns stay four values**: zero arms, absent type, placebo-vs-type CONTESTED, and the candidate fields. | checks `zero_arms_stays_UNKNOWN_never_a_role_or_a_link`, `absent_arm_type_stays_its_own_value`, `placebo_text_vs_type_is_CONTESTED_not_resolved_to_a_side` |
| 10 | **Only case and whitespace are normalised.** Punctuation, hyphens, brackets, dosage units and spelling are not; `3.2 mg/kg` ≠ `3.2 kg/mg`. | `fold`, test T5d |

## 3 · Files

| file | what |
|---|---|
| `CORRECTED-C-arm-attribution-v2-derive.py` | the producer; 18 self-checks, exit 1 on any failure |
| `CORRECTED-C-arm-attribution-v2-map.tsv` | 552 rows, key-identical to v1 and Job 3 |
| `CORRECTED-C-arm-attribution-v2-checks.json` | the 18 check results and the state census |
| `CORRECTED-C-arm-attribution-v2-tests.py` | 16 value-based tests of the new rules |
| `CORRECTED-C-arm-attribution-v2-changemap.py` | emits the row-level change map |
| `CHANGE-MAP-v1-to-v2.tsv` / `.md` | the exact change map and the unresolved counts |
| `CORRECTED-C-arm-attribution-v2-schema.json` | column-by-column meaning of every machine value |
| `CHECKS-RUNS/RUN-0N-*/` | every check attempt, each in its own directory, including the failures |
| `SHA256-v2-artifacts.txt` | hashes of everything above |

## 4 · Runs, in the order they happened — no failure was overwritten

| run | command | exit | outcome |
|---|---|---|---|
| RUN-01 | `python3 …-v2-tests.py` | 0 | 15/15 value tests PASS |
| RUN-02 | `python3 …-v2-derive.py <map> <checks>` | **1** | `no_narrative_token_corroboration_predicate_remains` FAIL, `suspect_lines=1`: the guard's own regex literal matched itself. Diagnosed in `RUN-02/NOTE.md`; guard rewritten to assemble the token from fragments, not weakened. |
| RUN-03 | same | **1** | same check FAIL with `suspect_lines=0`: the guard's *other* literal, `"CORROBORATION" not in body`, was itself a line of `body`. Same self-match, same fix. `RUN-03/NOTE.md`. |
| RUN-04 | same | 0 | 17/17 checks PASS — **but superseded.** Reading the values, not any check, exposed a defect in v2's own `verify_leaf_claim`: it split multi-arm leaf claims on `;` only, while three of the four leaves use `\|`. Nine rows were mis-stated as CONTESTED / label-absent instead of UNRESOLVED / multi-arm. `RUN-04/NOTE.md`. |
| RUN-05 | `python3 …-v2-tests.py` | 0 | 16/16 after adding test T3d for both separators |
| RUN-06 | `python3 …-v2-derive.py <map> <checks>` | 0 | **18/18 checks PASS**; the delivered map and checks JSON |
| RUN-07 | `python3 …-v2-changemap.py` | 0 | the delivered change map |
| RUN-08 | all three, on the settled tree | 0 / 0 / 0 | 16/16 tests, 18/18 checks; the re-run reproduces the map **byte-identically** (sha256 `bd3d6085…5484` before and after) |

Every run directory holds `cmd.txt`, `stdout.txt`, `stderr.txt` and `exit.txt` with the real exit
code. No test was skipped or deselected.

## 5 · Result, stated without a quota

**58 of 552 rows are source-confirmed. 494 are not.** v1's 503 CONFIRMED and Job 3's 521/41 were
never targets, and 313 of v1's 314 narrative-token confirmations become PROPOSED. The full counts
are in `CHANGE-MAP-v1-to-v2.md` §3.

## 6 · Boundary — what was deliberately not done

- ⛔ No whole-cache audit, no whole-leaf re-audit, no re-run of Job 3, no ablation, no census
  amnesty, no broad suite, no manuscript edit.
- ⛔ **No source query and no fetch of missing back-pointers.**
  `resultsSection.participantFlowModule` and `armsInterventionsModule.interventions[].armGroupLabels`
  — the registry's own explicit join fields — are **absent from this cache by established fact**
  (0 occurrences across all 12 payloads, verified by check). Their absence is *the* reason 337 rows
  can only ever be PROPOSED here; it is recorded as UNKNOWN with a locator, not chased.
- The producer imports only `collections, csv, json, os, re, sys`; no network, HTTP or subprocess
  module (checked).
- The 552-key set, disease and phase attributions are inherited from the unconfirmed job2/job3
  chain. Key compatibility is established; correctness of the underlying selection is not.
- **Computational field agreement is not clinical validation**, and nothing here establishes any
  EMC efficacy, safety, selectivity or readiness claim.
