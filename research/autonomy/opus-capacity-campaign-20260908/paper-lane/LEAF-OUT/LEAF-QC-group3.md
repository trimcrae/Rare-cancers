# LEAF-QC-group3 — QUESTION C: do the registration-order ties have any recoverable basis?

Leaf worker, wave 2026-09-08 ~18:55Z. Group: `LEAF-ASSIGNMENTS/QC-group3.txt` (118 NCTs).
Scope: for my NCTs only, the tie rows in
`CURATION-endpoint-identity-and-overlap-artifacts/TIES.tsv` whose `resolved_at_step` is
`f (smallest outcome index)`. Nothing outside my 118 NCTs was examined.

## Cache verification

`sha256sum -c SHA256-MANIFEST.txt` in
`/tmp/claude-0/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/scratchpad/ctg-cache-216bd1b5/`
→ 13/13 `OK`, **exit code 0**. No network request was made. No producer, gate, build or test was run.
No tracked file was written; both outputs here are untracked.

## Coverage: ties reached vs assigned

| quantity | count |
|---|---|
| NCTs assigned | 118 |
| NCTs located in the cache after R0 canonicalisation | 118 |
| TIES.tsv rows for my NCTs (all steps) | 380 |
| of those, step `f` rows (mine to answer) | **337** |
| step `f` rows reached and candidate set re-derived | **337 (100%)** |
| step `f` rows where my re-derived competing-candidate count equals TIES.tsv `candidates_still_competing` | **337 / 337** |
| step `e` rows for my NCTs (not mine to answer) | 43 |

Method for reaching the candidates: I re-applied **the preregistered rule as written**
(`RULE-PREREGISTERED.md` R0, R1, R2 a–f) to my 118 NCTs only, purely to recover *which* outcome
measures were still competing when step `f` fired. The rule was not amended and the global
selection was not re-run. Reproduction is exact: for every one of the 337 rows the number of
candidates still competing matches the number Job 2 recorded, so the sets I inspected are the sets
Job 2's step `f` actually broke.

One normalisation detail worth recording for the parent: `TIES.tsv` group keys retain a trailing
`)` (e.g. `cohort 1: ... (dtc)`), so the "leading/trailing punctuation stripped" step in R0 did not
strip brackets. Stripping them mismatched 28 of my rows until corrected; the 337/337 figure above is
after correcting my normaliser to match Job 2's.

## Headline answer

**Job 2's global claim — "no metadata basis exists for those" — is refuted for every step-`f` tie in
my group.**

| classification | ties | share of my 337 |
|---|---|---|
| `BASIS_EXISTS` | **337** | 100% |
| `NO_BASIS` | **0** | 0% |
| `UNRESOLVED` | **0** | 0% |

Not one of my 337 registration-order ties was a tie between metadata-identical measures. In every
case the competing outcome measures differ in at least one field the ladder never consults, and in
301 of 337 they name **different response constructs entirely** (e.g. ORR vs DCR), i.e. they are not
two estimates of one quantity at all.

## What actually distinguishes the competing measures

Field-level differences among the candidates still competing at step `f` (a tie can appear in more
than one row):

| distinguishing field | ties | example |
|---|---|---|
| response **construct** named in `title`/`description` | 301 | ORR vs DCR vs CBR vs BOR distribution |
| `populationDescription` | 100 | `NCT05565391` unweighted vs IPTW-weighted analysis population |
| assessment **criteria** (RECIST version / irRECIST / iRECIST / mRECIST / IMWG / Lugano / RANO / PCWG / INRC) | 81 | `NCT03713593` RECIST 1.1 vs mRECIST |
| `timeFrame` | 75 | `NCT04014075` data cut-off 16 months vs 23 months |
| `paramType` | 31 | `NCT03697304` `NUMBER` vs `MEDIAN` (Bayesian hierarchical model) |
| `unitOfMeasure` | 27 | percentage of participants vs participants vs days |

Construct pairings across the 337 ties (constructs read off the outcome `title`, corroborated
against the `description` free text):

| competing construct set | ties |
|---|---|
| DCR vs ORR | 139 |
| CBR vs ORR | 51 |
| ORR vs ORR (same construct; separated by criteria/timeframe/population/paramType) | 33 |
| BOR distribution vs ORR | 22 |
| BOR distribution vs DCR vs ORR | 15 |
| CR rate vs ORR | 14 |
| ORR vs unqualified "response rate" | 12 |
| CBR vs CR rate | 8 |
| CBR vs DCR vs ORR | 7 |
| CBR vs CR rate vs ORR | 6 |
| BOR distribution vs DCR | 6 |
| CBR vs DCR | 5 |
| combined response rate vs CR rate | 4 |
| DCR vs ORR vs unqualified rate | 3 |
| remaining sets (each ≤2 ties): BOR/DOR/ORR, CBR/DOR/ORR, DCR vs unqualified rate, DCR only, unqualified rate only, CBR/ORR/unqualified, BOR vs progression status, time-to-response only, PSA30 vs PSA50 | 12 |

Worked examples, each re-derivable from the named payload, NCT, outcome index and group id:

- `NCT03744468`, group `phase 1 (dose escalation): surzebiclimab 2 mg + tislelizumab`, group id
  `OG000`, payload `ctg_results_bor_2018_2021`. Competing: om 8 *"Phase 1: Overall Response Rate
  (ORR)"* (description: CR or PR per RECIST v1.1) vs om 10 *"Phase 1: Disease Control Rate (DCR)"*
  (description: CR, PR **or SD** per RECIST v1.1). Same type, same denominator (1), same timeframe,
  same population text. **Basis: `title` + `description` — two different quantities.** Step `f`
  selects om 8 (ORR); correct outcome, but reached by index order, not by any rule.
- `NCT04387071`, group `treatment (cmp-001, incagn01949)`, payload `ctg_results_bor_2018_2021`.
  Competing: om 0 *"Disease Control Rate"* vs om 1 *"Objective Response Rate (CR + PR)"*. Step `f`
  selects **om 0, the DCR** — the broader construct — because it registered first.
- `NCT03713593`, group `lenvatinib + pembrolizumab`, payload `ctg_results_bor_2018_2021`. Competing:
  om 2 ORR per **RECIST 1.1** vs om 7 ORR per **mRECIST**. Same construct, same population, same
  timeframe. **Basis: assessment criteria.**
- `NCT04014075`, group `trastuzumab deruxtecan`, payload `ctg_results_bor_2018_2021`. om 0 and om 1
  carry the **identical title**; they differ only in `timeFrame` ("Up to 16 months (data cut-off)"
  vs "Up to 23 months (data cut-off)") and `populationDescription` (cut-off 09 Apr 2021 vs
  08 Nov 2021). **Basis: timeFrame / populationDescription — two data cut-offs of one analysis.**
- `NCT03697304`, groups `module a, cohort 1: gec patients` and `module c, cohort 1: gec patients`,
  payload `ctg_results_bor_2018_2021`. Competing: the observed *"Objective Response (OR)"* vs
  *"Objective Response (OR) - Bayesian Hierarchical Model"*, `paramType` `NUMBER` vs `MEDIAN`.
  **Basis: `paramType` — one is an observed proportion, the other a model-borrowed posterior.**
- `NCT05177042`, group `bavdegalutamide + abiraterone`, payload `ctg_results_bor_2022_2026`.
  Competing: om 11 *"PSA30 Response Rate"* vs om 12 *"PSA50 Response Rate"*. **Basis: threshold in
  title/description.** Neither is a RECIST tumour response.
- `NCT03582033`, groups `part a: sea-bcma 100mg`…`1600mg`, payload `ctg_results_bor_2018_2021`.
  Competing: om 29 ORR per IMWG (sCR/CR/VGPR/PR) vs om 33 the full BOR distribution per IMWG
  (adds MR, SD, PD). Identical timeframe and population text. **Basis: `title` + `description`.**

## Would a basis change which measure is selected?

The ladder has no step for construct, criteria, timeframe or paramType, so "would it change the
selection" is only answerable against a stated preference. I used the one preference implicit in the
endpoint work — prefer the narrowest response construct, ORR (CR+PR) — and report it as a
counterfactual, **not** as a rule change. That decision is the parent's.

| verdict | ties | meaning |
|---|---|---|
| `NO` | 221 | an ORR-type measure exists among the competitors and step `f` already picked it |
| `YES` | 54 | step `f` picked a **non-ORR** quantity while an ORR-type competitor was present |
| `UNDETERMINED (no ORR-type candidate)` | 27 | the competing set contains no ORR-type measure (e.g. CBR vs CR rate); which one is wanted is a scientific decision, not a record fact |
| `DEPENDS (no preregistered ordering for this field)` | 35 | same construct throughout; separated only by criteria / timeframe / population / paramType, for which the ladder states no preference |

The 54 `YES` ties fall in **16 of my 118 NCTs**: `NCT03552029`, `NCT03767335`, `NCT03790111`,
`NCT03829501`, `NCT03894540`, `NCT03901469`, `NCT04033991`, `NCT04082364`, `NCT04099888`,
`NCT04182204`, `NCT04194944`, `NCT04323436`, `NCT04387071`, `NCT04524689`, `NCT04543188`,
`NCT04607668`. The per-tie alternative measure (index and title) is in the TSV column
`alternative_if_construct_rule_added`. What the currently selected measure is, across all 337:
ORR 253, BOR distribution 33, DCR 16, unqualified response rate 15, CR rate 14, CBR 4,
time-to-response 1, PSA30 1.

## Two defects in R1 visible from my rows (reported, not fixed)

1. **R1's title regex admits outcomes that are not response rates.** `NCT05537766`, group
   `substudy a (relapsed/refractory waldenstrom macroglobulinemia): brexucabtagene autoleucel`,
   payload `ctg_results_bor_2022_2026`: both surviving candidates are om 9 *"Time to First Objective
   Response"* and om 10 *"Time to Best Objective Response"*, `unitOfMeasure` **days**, `paramType`
   `MEAN`. Two further ties (`NCT04607668`, `NCT03901469` sets) carry a *"Duration of Objective
   Response"* candidate. The basis here is the title itself (first vs best; time vs rate).
2. **30 of my 337 ties sit on a `Participants` denominator of 0** — R1 requires a `Participants`
   denom entry but not a non-zero one, so cohorts with no analysed participants still reach the
   ladder (e.g. `NCT03969420`, groups `lead-in cohort: arm 1/2` and `stage 1: arm 1/2`, whose
   `populationDescription` states "Data collection and analysis were not conducted"). Flagged in the
   TSV `notes` column.

Neither is mine to repair. Both are recorded because they change how a step-`f` tie should be read.

## Honest limits

- I answer only the **factual** question: does the record carry distinguishing metadata. I do not
  claim which measure is scientifically correct, and the `YES` column is a counterfactual under one
  stated preference, not a recommendation.
- Construct labels (ORR / DCR / CBR / CR rate / BOR distribution / unqualified rate / …) are read
  from the outcome `title` with the `description` as corroboration. Every label is recoverable from
  the `competing_titles` column; a reader who disagrees with a label can re-read the same title.
- The 33 same-construct (`ORR` vs `ORR`) ties are the ones most open to a different reading: their
  basis is criteria/timeframe/population/paramType rather than a different quantity. They are marked
  `DEPENDS` and none of them is claimed to be a wrong selection.
- 43 step-`e` rows for my NCTs were **not** examined; step `e` is outside the question.
- Nothing here is asserted about efficacy, safety, selectivity or clinical readiness.

## Output pointers

- `LEAF-OUT/LEAF-QC-group3.tsv` — one row per step-`f` tie (337 rows + header). Columns:
  `nct, group_norm, payload, results_group_id, om_type, participants_denom, n_competing,
  om_indices, constructs, assessment_criteria, classification, distinguishing_fields,
  selected_om_index, selected_title, would_change_selection, alternative_if_construct_rule_added,
  competing_titles, competing_timeframes, competing_population_descriptions, competing_paramtypes,
  competing_units, notes`. Multi-candidate fields are `;`-separated and long text fields
  ` ||| `-separated, in ascending outcome-measure index order.
- Every row's source pointer is (`payload`, `nct`, `results_group_id`, each index in `om_indices`)
  against the verified cache at commit `216bd1b5fb25a56b90ef3cc2373e1fe68322708f`.
