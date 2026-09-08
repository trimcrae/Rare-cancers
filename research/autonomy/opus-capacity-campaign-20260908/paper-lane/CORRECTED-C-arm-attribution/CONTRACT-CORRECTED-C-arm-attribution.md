---
id: DOC-OPUS-CAMPAIGN-CORRECTED-C-ARM-ATTRIBUTION
title: "CORRECTED-C — results-group ↔ registered-arm attribution, with uncertainty preserved"
level: L4
kind: contract
status: live
purpose: >
  Deliver a NEW SIBLING arm-attribution table for the 552 included groups in which the
  results-group ↔ registered-arm link and the derived control status carry explicit, distinct,
  machine-readable states (CONFIRMED / CONFIRMED_TYPE_ONLY / CANDIDATE / CONTESTED / UNRESOLVED /
  UNKNOWN_IN_THIS_CACHE), in which label-only string similarity can never produce a confirmed link,
  and in which zero registered arms yields UNKNOWN rather than NOT_CONTROL.
scope: >
  L4. Source-validation evidence only, over the delivered immutable cache copy and the already
  delivered leaf outputs. It computes no response rate, no unique-patient total, no control
  comparison and no clinical comparison. It repairs no manuscript and authorises no publication act.
audience: [maintainers, external reviewers, autonomous research agents]
date: 2026-09-08
last_verified: 2026-09-08
related: [DOC-OPUS-CAMPAIGN-CURATION-ARM-ATTRIBUTION]
---

# CORRECTED-C — arm attribution, corrected without overwriting the record of what was run

⛔ **The endpoint manuscript stays parked.** ⛔ No response rate, no unique-patient total, no control
comparison, no clinical comparison, and no manuscript revision is produced here or authorised by this.

## 0 · What this is, and what it is not

This is a **materialisation of a corrected mapping**, not an acceptance of Job 3's logic and not an
acceptance of any individual row.

- The 16 leaf analyses and the original job1 / job2 / job3 results are **immutable evidence of their
  actual runs**. Nothing here overwrites them. `CURATION-endpoint-arm-attribution-map.tsv`,
  `CURATION-endpoint-arm-attribution-derive.py` and `CURATION-endpoint-arm-attribution.md` are
  untouched; job3 was **not re-run**, and its map is read strictly as a **prior-state index** for
  the change map below.
- ⚠ **job2 and job3 were never independently confirmed.** Neither this artifact nor any check in it
  confirms them. The 552-key set is *inherited* from that unconfirmed chain: it is reproduced here
  byte-for-byte so the two tables join, which establishes **key compatibility, not correctness of
  the underlying selection**. Job 1's and Job 2's outputs are outside this component entirely.
- The disease and phase attributions are **Job 3's and are not re-derived here**. This component
  owns **arm attribution only**.

## 1 · Inputs, and the exit code of the integrity check

| input | what it is | how used |
|---|---|---|
| `…/scratchpad/ctg-cache-216bd1b5/` (12 payloads + `_manifest.json` + `SHA256-MANIFEST.txt`) | the delivered immutable cache copy, cache revision `216bd1b5fb25a56b90ef3cc2373e1fe68322708f` | the **only** source of registry values |
| `CURATION-endpoint-arm-attribution-map.tsv` (552 rows, sha256 `1d7e8e18…97bbec`) | Job 3's map | **read-only prior state** for the change map |
| `LEAF-OUT/LEAF-QD-group{0,1,2,3}.tsv` (84 / 60 / 144 / 82 rows) | the delivered join-recovery leaves | recovery evidence, re-graded here |
| `PARENT-NOTE-zero-arm-not-control.md` | the parent's own re-derivation of the zero-arm defect | the D-ARM rule 3 correction |

**`sha256sum -c SHA256-MANIFEST.txt` → all 13 entries `OK`, exit code `0`** (run once; recorded in
`CHECKS-CORRECTED-C.md`).

⛔ **No network request of any kind was made.** No re-fetch, no retry, no second cache copy.
**`resultsSection.participantFlowModule` and `armsInterventionsModule.interventions[].armGroupLabels`
are absent from this cache and stay absent.** On ClinicalTrials.gov those two are the *explicit*
registry-asserted join fields; they were simply not requested at fetch time. Every state this
artifact writes as `*_IN_THIS_CACHE` therefore means **unknown within this cache, not globally
nonexistent**, and a stronger join for these trials may well exist upstream. That is a cache-scope
limit, not a registry limit, and it is not resolvable under the no-refetch fence.

## 2 · Deliverables

| file | what |
|---|---|
| `CORRECTED-C-arm-attribution-map.tsv` | **553 lines (552 group rows + header), 28 columns, 440,262 bytes**, sha256 `08b6f8a8a359e9789801f6a11db054a6f5531d7c58048a6047f011af707cb5f2` |
| `CORRECTED-C-arm-attribution-schema.json` | the machine-readable contract: key, enumerations, normalisation policy, column roles |
| `CORRECTED-C-arm-attribution-derive.py` | the new sibling producer (stdlib only) |
| `CORRECTED-C-arm-attribution-checks.json` | the emitted check record, 13 checks, `checks_failed: 0` |
| `CHECKS-CORRECTED-C.md` | the original check records with their real exit codes |
| this file | contract, change/disposition map, data-sufficiency statement |

## 3 · The five corrections, and the rule each one enforces

### 3.1 Label-only string similarity can never confirm a link

Job 3's matcher normalised with `re.sub(r"[^a-z0-9]+", " ", s.lower())` — which erases punctuation,
internal hyphens, brackets and unit separators — and then accepted the result as a `NORMALIZED`
match on the same footing as an exact one. It also emitted `registry_arm_label` and
`registry_arm_type` for 36 `CONTAINMENT` (substring-only) rows, so a *weak* match populated the same
columns a *confirmed* one did, even while its `control_status` said the match was weak.

Corrected policy — **only case and whitespace may be folded**:

| difference between results-group title and registry arm label | rows | new state |
|---|---|---|
| byte-identical | 137 | `CONFIRMED` |
| case and/or whitespace only (incl. spacing around punctuation, and `400 mg` ↔ `400mg`) | 52 | `CONFIRMED` |
| a punctuation insertion (`Avelumab 10 Miligram…` vs `Avelumab: 10 miligram…`) | 1 | **not confirmed** — `UNKNOWN_IN_THIS_CACHE`, `NO_LABEL_RELATION_IN_THIS_CACHE` |
| substring containment only | — | `CANDIDATE`, and **confirmed fields stay empty** |

The 52 case/whitespace rows are all 47 of Job 3's `NORMALIZED` rows that fold on case and whitespace
alone, **plus 5 rows Job 3 scored `NONE`** (`NCT03480646` `CPI-1205 400mg`/`800mg` ↔ `400 mg`/`800 mg`
×4, `NCT03451825` `Avelumab 20 mg/kg` ↔ `Avelumab 20mg/kg`). ⚠ Those five differ **by a space inside a
dose string** — the same number, the same unit, one space. That is whitespace, and it is permitted;
it is not the forbidden case, which is a changed dose or a changed unit. Exactly **one** of Job 3's 48 `NORMALIZED` rows (`NCT03451825`
`Avelumab 10 Miligram Per Kilogram (mg/kg)` ↔ `Avelumab: 10 miligram per kilogram (mg/kg)`) turns on
an inserted colon and is **refused**. A complement argument exists in that record — the sibling group
`Avelumab 20 mg/kg` takes the other arm — but it was **not adopted as confirmation**; the row keeps
its ambiguity and its original label.

⚠ **`3.2 mg/kg` and `3.2 kg/mg` are not interchangeable because their strings look similar.** That is
a dose and a unit, not a formatting variant. The producer contains no rule that could merge them.

### 3.2 Substring containment is a candidate, never a resolution

`arm_link_state = CANDIDATE` populates `candidate_registry_arm_labels`,
`candidate_registry_arm_types` and `candidate_evidence` and leaves
`confirmed_registry_arm_label` / `confirmed_registry_arm_type` **empty**. The check
`confirmed_fields_only_when_CONFIRMED` and `substring_containment_never_confirmed` both enforce this
and both `PASS` with 0 violations.

### 3.3 Zero registered arms is UNKNOWN, not NOT_CONTROL

Job 3's rule was `n_arms_registered <= 1 → NOT_CONTROL_SINGLE_ARM_TRIAL`. **6 rows across 3 NCTs**
(`NCT00389805` ×2, `NCT02825420` ×3, `NCT04539327` ×1) have **zero** registered arms and carried that
label. Absence of information is not evidence of a single arm. All 6 are now
`control_status = UNKNOWN_IN_THIS_CACHE`, basis *"zero registered arm groups in this cache: control
status is UNKNOWN, not NOT_CONTROL"*. The blast radius is exactly the 6 rows the parent note
predicted; the check `zero_arms_never_not_control` passes with 0 violations.

The neighbouring case is recorded rather than silently accepted: **19 trials register exactly one arm
yet report more than one distinct results group — 83 rows** carry
`sole_arm_multi_results_group_flag = YES`. Those rows are not forced to UNKNOWN (every registered arm
in each of those records is typed `EXPERIMENTAL`/`OTHER`, so no assignment could make the group a
control), but the flag makes the record's own contradiction of a one-arm reading visible and
queryable, and the `NOT_CONTROL_BY_ARM_SET_TYPE_INVARIANT` basis string states the residual
assumption — that the results group corresponds to *some* registered arm — in words.

### 3.4 A contradictory placebo description against an EXPERIMENTAL type stays CONTESTED

**5 rows across 3 trials** now carry `control_status = CONTESTED`; **neither field wins, and a
CONTESTED row is not counted as a comparator and not counted as NOT_CONTROL.**

| trial | group | registry type of the CONFIRMED arm | Job 3 said |
|---|---|---|---|
| `NCT01256359` | `Docetaxel and Placebo` ×3 | `EXPERIMENTAL` (byte-exact label match) | `NOT_CONTROL` |
| `NCT01859741` | `P2: Placebo + CIS or CARB` | `EXPERIMENTAL` | `CONTROL_PLACEBO_BY_GROUP_TEXT` |
| `NCT03409614` | `Part 2: Placebo + Chemotherapy` | `EXPERIMENTAL` | `CONTROL_PLACEBO_BY_GROUP_TEXT` |

Job 3 resolved the same three trials in **opposite directions** — the first to NOT_CONTROL, the other
two to a control. That inconsistency is itself the evidence that neither field should win
automatically. The trials are **not** counted among the confirmed controls in §4.

A second, weaker shape is flagged but not contested: `NCT02259582`'s
`Demcizumab/Placebo Arm (Arm 2)` names a **treatment sequence**. Its registry type is
`ACTIVE_COMPARATOR` and the row is recorded as such, with
`GROUP_TITLE_IS_A_TREATMENT_SEQUENCE_CONTAINING_A_PLACEBO_TOKEN` set so no consumer can read it as a
placebo control. `Placebo/Placebo Arm (Arm 1)` in the same trial is typed `PLACEBO_COMPARATOR` and is
the actual placebo arm; Job 3 had left both `UNKNOWN_AMBIGUOUS_SEQUENCE_LABEL`.

### 3.5 Delivered leaf recoveries are graded, not adopted wholesale

The four Q-D leaves cover exactly the **367** rows Job 3 could not strongly match
(`NONE` 328 + `CONTAINMENT` 36 + `AMBIGUOUS_MULTI` 3 = 84 + 60 + 144 + 79). Their verdicts are
re-graded here by a deterministic rule over each leaf's own stated evidence field:

| leaf evidence names… | graded | rows |
|---|---|---|
| an arm `description`, `interventionNames`, or a record-asserted bijection / partition / complement / verbatim reproduction | `CONFIRMED` (within-record relation) | 325 |
| cardinality alone (sole registered arm), or arm-set type invariance | `CONFIRMED_TYPE_ONLY` | 16 |
| a label string alone (a shared `Part` token, a tumour-type token, a dose-token removal with no corroboration) | **`CANDIDATE`** | 9 |
| a leaf join whose recovered arm label does not bind to a single registered arm in the cache | `CONFIRMED_TYPE_ONLY` (11 rows, where the arm set is type-invariant) or `CANDIDATE` (1 row) | 12 |
| the leaf's own `UNRESOLVED` (arms mutually indistinguishable) | `UNRESOLVED` | 5 |
| the leaf's own `GENUINELY_UNJOINABLE` (zero arms in this cache) | `UNKNOWN_IN_THIS_CACHE` | 7 |

⛔ A leaf recovery may **only strengthen** a link this producer had not already confirmed from the
label; it can never downgrade or overwrite a byte-exact match, and it never populates a confirmed
field without binding to a single registered arm in the cache.

## 4 · Resulting distribution, and the disposition / change map

### 4.1 Arm-link states (552 rows)

| `arm_link_state` | rows |
|---|---|
| `CONFIRMED` | 503 |
| `CONFIRMED_TYPE_ONLY` | 26 |
| `CANDIDATE` | 10 |
| `UNRESOLVED` | 5 |
| `UNKNOWN_IN_THIS_CACHE` | 8 |

### 4.2 Control status (552 rows)

| `control_status` | rows | trials |
|---|---|---|
| `NOT_CONTROL_CONFIRMED` | 454 | — |
| `NOT_CONTROL_BY_ARM_SET_TYPE_INVARIANT` | 26 | — |
| `CONTROL_ACTIVE_COMPARATOR_CONFIRMED` | 32 | 20 |
| `CONTROL_PLACEBO_CONFIRMED` | 8 | 5 |
| `CONTROL_NO_INTERVENTION_CONFIRMED` | 1 | 1 |
| `CONTROL_UNSPECIFIED_CANDIDATE_GROUP_TEXT_ONLY` | 1 | 1 |
| `CONTESTED` | 5 | 3 |
| `UNKNOWN_IN_THIS_CACHE` | 25 | 11 |

**41 rows across 25 trials have a record-confirmed control status. Of those, 9 rows across 6 trials
are placebo or no-intervention; the other 32 are treated `ACTIVE_COMPARATOR` arms, which are
comparators, not untreated controls.** 1 further row is a control *candidate* on group text alone,
5 are CONTESTED, and 25 stay UNKNOWN.

### 4.3 Change map against Job 3, by semantic class

Classes (`CONTROL_SUPPORTED` / `CONTROL_PROPOSED` / `NOT_CONTROL` / `CONTESTED` / `UNKNOWN`) exist
**for this comparison only** and are never written back onto a row.

| transition | rows | what it means |
|---|---|---|
| `UNCHANGED_CLASS` | 273 | Job 3's class survives (the machine value still changes: the vocabulary is new) |
| `UNKNOWN → NOT_CONTROL` | **245** | the delivered leaves reached the registry arm and its type reads `EXPERIMENTAL`/`OTHER` |
| `UNKNOWN → CONTROL_SUPPORTED` | 16 | the leaves reached an `ACTIVE_COMPARATOR` or `PLACEBO_COMPARATOR` arm |
| `NOT_CONTROL → UNKNOWN` | 9 | the six zero-arm rows, plus `NCT02679170` ×2 (arm confirmed but the record carries **no type field**) and the refused `NCT03451825` punctuation match |
| `NOT_CONTROL → CONTESTED` | 3 | `NCT01256359` |
| `CONTROL_PROPOSED → CONTESTED` | 2 | `NCT01859741`, `NCT03409614` |
| `CONTROL_PROPOSED → CONTROL_SUPPORTED` | 4 | a group-text claim replaced by a confirmed registry arm |

⚠ **Recovery mostly removes UNKNOWNs; it does not find comparators.** 245 of the 261 rows that left
UNKNOWN went to `NOT_CONTROL`, and only 16 to a control of any kind — of which the great majority are
active comparators. **No placebo and no no-intervention recovery was invented to increase coverage:**
the confirmed placebo/no-intervention population moved from 10 rows / 7 trials (Job 3) to 9 rows /
6 trials here, and it moved **down** because three placebo *claims* were demoted to CONTESTED and one
sequence-labelled arm was resolved to its actual registry type. Coverage of control status went up;
coverage of *controls* did not.

## 5 · Explicitly unresolved states, carried as such

| state | rows | trials | why it stays open |
|---|---|---|---|
| `UNRESOLVED` — arms mutually indistinguishable | 5 | `NCT02593786` (4), `NCT03480646` (1) | `NCT02593786` registers `Nivolumab monotherapy` and `Cohort Expansion` with **identical** descriptions and identical `interventionNames`; nothing in the record assigns cohorts A–D to either |
| `CANDIDATE` — label string only | 10 | `NCT03724890` (5), `NCT03854227` (2), `NCT03480646` (2), `NCT02566993` (1) | a shared `Part` token, a tumour-type token, or a leaf label that does not bind to one registered arm |
| `UNKNOWN_IN_THIS_CACHE` — zero arms | 6 | `NCT00389805`, `NCT02825420`, `NCT04539327` | `armsInterventionsModule` is `{}` or `armGroups` is empty **in this cache** |
| `UNKNOWN_IN_THIS_CACHE` — arm confirmed, no type | 3 | `NCT02679170` (2), `NCT04753658` (1) | the registry arm carries no `type` key in this cache |
| `UNKNOWN_IN_THIS_CACHE` — refused punctuation match | 1 | `NCT03451825` | see §3.1 |
| `UNKNOWN_IN_THIS_CACHE` — leaf found no join in this cache | 1 | `NCT02383927` `Cohort 3` | the leaf reached the record and could not join it; not a control claim in either direction |
| `CONTESTED` | 5 | `NCT01256359` (3), `NCT01859741` (1), `NCT03409614` (1) | §3.4 — neither field wins |

**31 open rows across 15 trials in total** (25 `UNKNOWN_IN_THIS_CACHE` + 5 `CONTESTED` + 1 control
candidate on group text alone).

### 5.1 Leaf equivalence claims marked UNRESOLVED rather than adopted

The Q-B leaves reported a `DUPLICATE_TITLE_VARIANT` mechanism — the same cohort written with
different punctuation, spacing, **unit order** (`3.2 mg/kg` vs `3.2 kg/mg`), or a misspelling
(`Ruxolitinib` vs `Ruxolitibin`) — across **23 NCTs**. Those are **kept as evidence**: they are real
observations about real records. They **do not license a normaliser that declares clinical
equivalence**, and no such normaliser exists in this producer.

Where a leaf asserted equivalence on string similarity alone, this component marks it **unresolved**.
Concretely: exactly **1** of those 23 NCTs (`NCT03480646`) is also among my 552 rows, and its 3
affected rows are already `CANDIDATE` (2) or `UNRESOLVED` (1) here — none of them is confirmed on a
string-variant argument. The other 22 NCTs, including the `3.2 kg/mg` exhibit `NCT03523572`, do **not
appear in these 552 rows at all** and are therefore outside this component; the equivalence assertion
about them remains **unresolved and belongs to the identity/selection/overlap owner**, not to me. I
have neither adopted nor refuted it.

## 6 · Checks actually run

13 deterministic checks, all `PASS`, `checks_failed: 0`, producer exit code `0`. Full record with
real exit codes in `CHECKS-CORRECTED-C.md`; machine record in
`CORRECTED-C-arm-attribution-checks.json`. Emitting the table is not acceptance: the checks are what
constrain it, and each one names a rule from §3 that it would catch a violation of.

⛔ These are **focused checks of the new mapping logic and of the specific prior counterexamples**.
No unchanged full source re-audit was run, no producer other than this one was executed, and Job 3
was not re-run.

## 7 · Data-sufficiency statement

**Sufficient, within the cache, for a corrected arm-attribution mapping — and only for that.**

1. **The mapping is finite and complete over its unit.** All 552 included groups carry a link state
   and a control status; the key set is identical to Job 3's and to `C2_arms` (0 only-here,
   0 only-there). No row is silently dropped and no row is invented.
2. **Arm-level control status is now determinable for 521 of 552 rows** (503 CONFIRMED +
   26 CONFIRMED_TYPE_ONLY, less the 8 confirmed-but-untyped/other residuals), against 185 strongly
   matched rows in Job 3. **31 rows across 15 trials remain CANDIDATE, CONTESTED or UNKNOWN**, and they
   are named individually in §5.
3. **It is not sufficient for any control-referenced analysis.** 41 confirmed-control rows across
   25 trials, of which only 9 rows / 6 trials are placebo or no-intervention, scattered across
   trials. A per-disease control comparison is not constructible from this, and none is attempted.
4. **It is not sufficient to settle the contested rows.** Resolving the 5 CONTESTED rows needs a
   field this cache does not carry — `participantFlowModule`, or
   `interventions[].armGroupLabels` — or a protocol document. **Unknown in this cache is not
   nonexistent**, and the refetch that could settle it is fenced off here.
5. **It does not confirm job2 or job3.** The 552-key selection, the four-cell category rules, the
   disease attribution and the phase attribution are all inherited unconfirmed, and this artifact
   makes no claim about any of them.
6. **It supports no clinical conclusion of any kind.** There is no wet lab, no response rate, no
   unique-patient total, no efficacy, safety, selectivity or readiness claim here, and this mapping
   does not become one by being joined to anything else.

**Stop condition: reached the finite corrected mapping.** Not an input insufficiency — the corrected
mapping was produced over all 552 rows; the residual 31 open rows are recorded as open states, not as
a blocked task.

## 8 · What this artifact is not

⛔ Not a re-run of Job 3 and not an overwrite of it. ⛔ Not an acceptance of Job 3's logic or of any
individual row. ⛔ Not a denominator, a unique-patient total, a response rate, a control comparison or
a clinical comparison. ⛔ Not a manuscript revision — the endpoint manuscript stays parked. ⛔ Not a
disease or phase re-attribution. ⛔ Not a claim that any gate is green. Nothing was committed, pushed
or fetched.
