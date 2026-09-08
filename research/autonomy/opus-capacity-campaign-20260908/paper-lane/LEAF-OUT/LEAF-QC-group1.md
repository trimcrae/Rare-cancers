# LEAF-QC-group1 — Question C: do the registration-order (step-f) ties have a recoverable metadata basis?

Leaf worker output, 2026-09-08. Group: `LEAF-ASSIGNMENTS/QC-group1.txt` (121 NCTs). No other NCT was
read or reasoned about. No network request was made. No producer, gate, test, manuscript or tracked
file was run or edited.

## Cache verification

```
cd /tmp/claude-0/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/scratchpad/ctg-cache-216bd1b5
sha256sum -c SHA256-MANIFEST.txt
```
All 13 entries `OK`. **`sha256sum -c` exit code = 0.**

## Coverage — ties reached vs assigned

| quantity | count |
|---|---|
| NCTs assigned in `QC-group1.txt` | 121 |
| assigned NCTs with a canonical record in the cache | 121 (0 missing) |
| tie rows in `TIES.tsv` for my NCTs (all steps) | 419 |
| of those, `resolved_at_step = f (smallest outcome index)` — **my scope** | **395** |
| step-`f` ties examined | **395 / 395 (100%)** |
| step-`e` ties in my NCTs (out of scope for this question) | 24 |
| distinct NCTs contributing step-`f` ties | 121 |

Candidates still competing at step `f`: 2 candidates in 291 ties, 3 in 46, 4 in 56, 6 in 2.

### Reconstruction fidelity (why these are the right candidate sets)

To see *which* measures were competing I re-applied Job 2's own R0/R1/R2a–e to my 121 records only.
I did **not** rewrite the rule and did **not** re-run the global selection. The reconstruction
reproduces Job 2's `TIES.tsv` exactly: for all **395/395** rows the step reached is `f` and the
number of surviving candidates equals `candidates_still_competing`. One implementation detail had to
be recovered by matching Job 2's output: its group-title normalisation strips trailing sentence
punctuation but **not** brackets (its `group_norm` values retain `(bay73-4506)`); with bracket
stripping, 53 rows failed to match, and without it all 395 match.

## Headline result

**Job 2's global claim — "no metadata basis exists for the step-f ties" — is REFUTED for every tie in
this group.**

| classification | ties | share |
|---|---|---|
| `BASIS_EXISTS` | **395** | 100.0% |
| `NO_BASIS` | 0 | 0.0% |
| `UNRESOLVED` | 0 | 0.0% |

In all 395 ties the competing outcome measures differ in at least one field the preregistered ladder
never consulted. Not one tie is a set of records that the source leaves genuinely indistinguishable.

### Which field distinguishes them (a tie can appear in several rows)

| distinguishing field | ties | sole basis in |
|---|---|---|
| title names a different endpoint construct (ORR / BOR vs DCR / CBR / DoR) | 307 | 86 |
| assessment criteria named in title/description (RECIST 1.1, RECIST 1.0, mRECIST, irRECIST, Choi, Cheson, IWG, …) | 129 | 0 |
| `timeFrame` | 111 | 24 |
| `unitOfMeasure` | 110 | 4 |
| `paramType` | 77 | 0 |
| `populationDescription` | 61 | 12 |
| title wording, same construct but a different measured quantity | 32 | 32 |
| title cohort/part qualifier (`Part I only`, `Cohort 3`, `Expansion Phase`) | 16 | 0 |

Endpoint-construct composition of the competing sets: 107 ties pit an ORR measure against a DCR
measure, 92 an ORR against a BOR, 47 an ORR against a CBR, 23 a three-way ORR/BOR/DCR, 13 BOR vs DCR.
These are different endpoints — DCR and CBR count stable disease, ORR and BOR do not — and R1's
response regex admits all of them as interchangeable candidates for the same cohort.

## Worked examples, with exact source pointers

Every pointer is `payload / NCT / outcome-measure index` in the canonical R0 record.

1. **`ctg_results_bor_2010_2013` / NCT01732913 / om[1], om[2], om[3]** — cohorts
   `idelalisib + rituximab` and `placebo + rituximab`. Competing titles are
   `Overall Response Rate`, `Lymph Node Response Rate`, `Complete Response Rate`. Basis: title.
   These are three different quantities; only om[1] is an overall response rate. Step f happens to
   pick om[1], so the selection is unchanged, but the tie is not metadata-free.
2. **`ctg_results_bor_2014_2017` / NCT02319044 / om[6], om[7]** — cohort `total`. Both titled
   exactly `Disease Control Rate (DCR)`; the only difference in the whole record is
   `timeFrame` = `After 6 months` (om[6]) vs `After 12 months` (om[7]). Basis: `timeFrame`.
   The only tie in the group whose titles are identical — and it still has a basis.
3. **`ctg_results_bor_2014_2017` / NCT02341456 / om[7], om[8]** — cohorts `cohort 1`, `cohort 1a`,
   `cohort 2`. `Number of Patients With an Objective Response` (`unitOfMeasure = Participants`) vs
   `Percentage of Patients With an Objective Response` (`unitOfMeasure = Percentage`). Same
   underlying result, two scales. Basis: `unitOfMeasure`.
4. **`ctg_placebo_onc_2010_2013` / NCT01774344 / om[3], om[4]** — cohorts `placebo`,
   `regorafenib 160 mg (bay73-4506)`. om[3] `Objective Tumor Response Rate (ORR)` cites RECIST 1.1
   **and** mRECIST; om[4] `Disease Control Rate (DCR)` cites RECIST 1.1 only. Basis: construct and
   assessment criteria.
5. **`ctg_results_bor_2014_2017` / NCT02494583 / om[5], om[7]** — cohort
   `placebo + soc chemotherapy (soc)`. Both are ORR per RECIST 1.1 by BICR in PD-L1 CPS ≥1, but
   `populationDescription` scopes om[5] to the pembrolizumab-**combination** comparison and om[7] to
   the pembrolizumab-**monotherapy** comparison of the same SOC control cohort. Basis:
   `populationDescription`.
6. **`ctg_results_bor_2010_2013` / NCT01852292 / om[2], om[4]** — cohorts `buparlisib + paclitaxel`,
   `buparlisib matching placebo + paclitaxel`. `paramType = MEDIAN` (om[2]) vs `NUMBER` (om[4]) on
   the same `unitOfMeasure`. Basis: `paramType`. A median and a point estimate are not the same
   statistic and should not be pooled.
7. **`ctg_results_bor_2014_2017` / NCT02448381 / om[3], om[4]** — cohorts `sgx301 (cycle 1 & 2 =
   sgx301)` and `placebo (cycle 1)`. `Patch Lesion Response Rates` vs `Plaque Lesion Response
   Rates`, `unitOfMeasure = lesions with response`. Basis: title + `populationDescription` (one
   population is participants, the other is lesions). These are lesion-level, not participant-level,
   response rates.

## Does the basis change which measure is selected?

I did **not** amend the ladder. To answer part 3 I applied a *diagnostic* preference over the newly
visible fields and asked only whether it would land on a different measure than step f did:
P1 a candidate whose title/`populationDescription` restricts it to a study part or cohort other than
this results cohort is disqualified; P2 an ORR/BOR (CR+PR) measure is preferred over DCR/CBR (which
add SD) and over non-response constructs (CR rate, lymph-node RR, MRD-negativity, lesion-level RR);
P3 an unrestricted measure is preferred over a biomarker-subgroup-restricted one; P4 a
participant-level measure is preferred over a lesion-level one.

| effect on the selected measure | ties |
|---|---|
| `CONDITIONAL` — a basis exists but it is `timeFrame`, criteria version or scale, for which the record supplies no internal preference; the parent must choose, and the choice may or may not move the pick | 189 |
| `NO_CHANGE_SAME_PICK` — basis exists and P1–P4 land on the same measure step f picked | 174 |
| `CHANGES` — P1–P4 land on a different measure | **32** |

The 32 `CHANGES` ties, with the replacement named (`sel om -> alt om`):

| NCT | cohorts affected | step-f pick | metadata-preferred measure |
|---|---|---|---|
| NCT02152956 | 13 cohorts (`cohort 0-a` … `mtd expansion with ruxolitinib`) | om[1] `Overall Complete Response Rate` | om[4] `Overall Response Rate` |
| NCT02432846 | 6 cohorts (ilixadencel/sunitinib strata + totals) | om[5] `Objective Response Rate (ORR) … and Duration of Response in Each Subgroup` | om[6] `Number of Participants With Specific Best Overall Response` |
| NCT01746225 | 3 nab-paclitaxel dose cohorts | om[2] `Disease Control: Overall Response of Stable Disease …` | om[3] `Best Overall Response` |
| NCT01670877 | 3 cohorts (see below) | om[0] `Part I Only: Clinical Benefit Rate …` | om[13] / exclude |
| NCT01797120 | `fulvestrant & everolimus`, `fulvestrant & placebo` | om[1] `Clinical Benefit Rate` | om[2] `Objective Response Rate` |
| NCT01938001 | `rituximab + lenalidomide (r^2)`, `rituximab + placebo` | om[1] `Durable Complete Response Rate (DCCR) … IRC` | om[3] `Percentage of Participants With an Objective Response … ` |
| NCT01709162 | `ipilimumab, 3 mg/kg`, `chemotherapy` | om[1] `Disease Control Rate (DCR)` | om[2] `Best Overall Response Rate (BORR)` |
| NCT01770353 | `expansion phase: cohort 3` | om[7] `Pilot Phase + Expansion Phase: ORR (Non-CNS Assessment)` | om[8] `Expansion Phase: ORR for Cohort 3 (CNS Assessment)` |

Source pointers for the two most consequential:
- **`ctg_results_bor_2014_2017` / NCT02152956 / om[1] vs om[4]**: step f selects
  `Overall Complete Response Rate` — a CR rate, not a response rate — for all 13 cohorts, while
  om[4] `Overall Response Rate` is present in the same record with the same `timeFrame`
  (`up to 14 months`) and the same `unitOfMeasure` (`Participants`).
- **`ctg_results_bor_2010_2013` / NCT01770353 / om[7] vs om[8]**: the results cohort is
  `Expansion Phase: Cohort 3`; om[7] is titled `Pilot Phase + Expansion Phase` and om[8] is titled
  `Expansion Phase: ORR for Cohort 3`. The title carries the cohort scope the ladder never read.

## Two structural findings inside my group (reported, not acted on)

1. **A `Participants` denominator of 0 satisfies R1.** In 12 of my 395 step-f ties *every*
   competing candidate reports a denominator of **0** for that cohort, so step e cannot separate
   them and step f selects a measurement over zero participants. Affected keys (from
   `participants_denoms` in the TSV): NCT01732913 ×2, NCT01980888 ×2, NCT01755975, NCT01801358,
   NCT01670877 ×3, NCT01709162 ×2, NCT02255110.
2. **Step a can remove the only cohort-correct measure before the tie forms.**
   `ctg_results_bor_2010_2013` / NCT01670877, cohort
   `part ii: neratinib + fulvestrant (er+, fulvestrant-naive)`: the candidates left at step f are
   om[0] (`Part I Only`, denominator 0 for this group), om[1] (`Part II ER-cohort Only`, 0) and
   om[3] (`Part II Fulvestrant-treated ER+ Cohort Only`, 0) — all PRIMARY. The measure actually
   scoped to this cohort, om[13] `Part II Fulvestrant-naive ER+ Cohort Only: Response Rate (RR)`
   with denominator **10** for group `OG002`, is SECONDARY and was eliminated at step a. The
   step-f pick for this cohort is a Part I measurement with a zero denominator.
   For the same trial's two crossover cohorts (`crossover: neratinib + trastuzumab`,
   `crossover: neratinib + fulvestrant + trastuzumab`) *no* response outcome measure reports a
   non-zero denominator, so the correct disposition is exclusion, not reselection. These three rows
   carry `note = manual record read` in the TSV.

## What I did not establish

- I did not check the 24 step-`e` ties in my NCTs; they are outside this question.
- The 189 `CONDITIONAL` ties are `BASIS_EXISTS`, not `UNRESOLVED`: the field that distinguishes them
  is present and named in the TSV. What is unresolved there is the *preference*, which is the
  parent's decision, not a property of the record.
- Nothing here bears on efficacy, safety, selectivity, therapeutic window or clinical readiness.
- I state nothing about ties, NCTs or global counts outside my 121 assigned NCTs.

## Files

- `LEAF-OUT/LEAF-QC-group1.tsv` — 395 rows, one per assigned step-`f` tie. Columns: `nct`,
  `group_norm`, `payload`, `n_competing_at_step_f`, `om_indices`, `participants_denoms`,
  `selected_om_index`, `selected_om_title`, `classification`, `basis_fields`, `basis_detail`
  (per-candidate `type`, title, `timeFrame`, `populationDescription`, `paramType`, `unitOfMeasure`,
  criteria), `selection_effect`, `alt_om_index`, `alt_om_title`, `note`.
- Inputs read (read-only): the 12 cache payloads listed in `SHA256-MANIFEST.txt`;
  `CURATION-endpoint-identity-and-overlap-artifacts/TIES.tsv`;
  `CURATION-endpoint-identity-and-overlap-artifacts/RULE-PREREGISTERED.md`;
  `LEAF-ASSIGNMENTS/QC-group1.txt`.
