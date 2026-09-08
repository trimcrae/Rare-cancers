# Independent re-derivation of Job 1's endpoint measurement/denominator arithmetic

Role: independent re-deriver. I did not write the target and did not read its producing scripts
before computing; I wrote my own replay of `research/manuscripts/endpoint_corpus.py` against the
delivered cache and compared afterwards. Read-only throughout: nothing edited, committed, pushed
or fetched; no producer, gate, preflight or test suite was run; no second copy of the cache was
made. Scope: global arithmetic and the two named exhibits only — no per-NCT adjudication.
The response-endpoint manuscript is parked; nothing here proposes a correction to it and nothing
here asserts anything about efficacy, safety or clinical readiness.

Date: 2026-09-08.

## Verdicts

| # | Claim | Verdict | My independently recomputed value |
|---|---|---|---|
| 0 | Cache integrity | **CONFIRMED** | `sha256sum -c SHA256-MANIFEST.txt` → 13/13 `OK`, **exit 0** |
| 1 | 552 rows over 138 distinct NCTs | **CONFIRMED** | 552 rows, 138 distinct NCTs; per-shard counts match |
| 2 | 552/552 source measures carry a participant `denoms`; producer reads none of it | **CONFIRMED** | 552/552 have exactly one `Participants` denominator for their group; 0 occurrences of `denoms` in the producer; `n = sum(cells.values())` at line 209 |
| 3 | 299 `<` denominator, 0 `>`, 253 `=` | **CONFIRMED** | 299 / 0 / 253 (median shortfall 3, max 112) |
| 4 | 548/552 all-category class sums equal the denominator | **CONFIRMED** | 548; the 4 exceptions are exactly the four named |
| 5 | 10 cross-class, 51 within-class, 22 value-changing overwrites | **CONFIRMED** | 10 / 51 / 22 (+491 none = 552); the 10 are exactly the 10 named |
| 6a | Exhibit A, NCT00654238 | **CONFIRMED** | every digit matches the record |
| 6b | Exhibit B, NCT01790503 | **CONFIRMED on all numbers**; two wording imprecisions, no numeric effect | 8 classes, 26 vs 53, `CR+PR` overwrites `CR` |
| 7 | The overwrite passes the build assertion because the assertion checks the sum of the same cells | **CONFIRMED** | `orr_dcr_reread.py:152` asserts `CR+PR+SD+PD == evaluable_n`, and `evaluable_n` *is* that sum |

No claim was refuted. No claim was unverifiable.

## Method

`/tmp/.../scratchpad/verify/replay.py` re-reads the 12 delivered payloads directly from the cache
directory (the header line before the `=`×30 rule is stripped, as the producer's `_payload` does),
in the producer's order (5 BOR eras, then 5 placebo eras), reimplements the four category regexes,
the float/`is_integer` test, the four-cell requirement, the `n <= 0` refusal and the
`(nct, om title, group title, n)` de-duplication, and records for every emitted row the full
(class index, class title, category title, value) provenance of each stored cell rather than only
the sum.

Fidelity: my 552 replayed rows are positionally identical to the committed
`research/manuscripts/endpoint/endpoint-corpus-inputs.json` on
`(nct_id, outcome_measure_title, arm_title, evaluable_n, cells)` — **0 mismatches**. So the
arithmetic below is about the rows the paper actually used.

Independent row-level cross-check of the seven shard TSVs: for all 552 rows, `cells_CR/PR/SD/PD`,
`reported_denominator_participants`, `all_categories_in_contributing_classes_sum` and
`sum_minus_reported_denominator` — **0 mismatches** against my replay. The shard files therefore
agree with the source, not merely with each other.

## Claim 1 — 552 rows, 138 NCTs — CONFIRMED

My replay: **552 rows**, **138 distinct NCTs**. Per-shard, mine vs the published table and vs the
actual TSV line counts and byte sizes:

| shard | my replay | published / TSV rows | TSV bytes |
|---|---|---|---|
| `ctg_results_bor_1999_2009` | 49 | 49 | 31,043 |
| `ctg_results_bor_2010_2013` | 81 | 81 | 55,374 |
| `ctg_results_bor_2014_2017` | 283 | 283 | 221,163 |
| `ctg_results_bor_2018_2021` | 130 | 130 | 85,431 |
| `ctg_results_bor_2022_2026` | 3 | 3 | 2,097 |
| `ctg_placebo_onc_2010_2013` | 4 | 4 | 3,415 |
| `ctg_placebo_onc_2014_2017` | 2 | 2 | 1,544 |
| total | **552** | **552** | **400,067** |

The TSVs carry 30 columns and 552 data rows over 138 distinct NCTs. `summary.json` matches on every
field I recomputed.

## Claim 2 — the denominator exists and the producer does not read it — CONFIRMED

Source half: for each of the 552 rows I looked up
`outcomeMeasures[i].denoms[units == "Participants"].counts[groupId]`. **552/552 rows have exactly one
such entry** — 0 rows missing it, 0 rows with more than one. (Also verified incidentally, matching
the document: all 552 have `unitOfMeasure = Participants` and `paramType = COUNT_OF_PARTICIPANTS`,
0 rows have an empty `timeFrame`, and 451 carry a `populationDescription`.)

Code half, by line in `research/manuscripts/endpoint_corpus.py`:

- `grep -c denoms research/manuscripts/endpoint_corpus.py` → **0**. The producer never touches the
  block. (The word "denominator" appears only in prose and in an unrelated disposition counter,
  `group_block_zero_denominator`, line 211.)
- Line **209**: `n = sum(cells.values())`.
- Line **231**: `"evaluable_n": n` — the stored field is that sum, with no other source.
- `_cells_for_groups`, lines 130–151, reads only `om["classes"][…]["categories"][…]["measurements"]`.
  Line **133** `for cl in om.get("classes") or []` and line **150** `per[gid][label] = int(f)` are the
  unguarded assignment the overwrite claim rests on: no key-collision check exists, so the last
  writer wins across categories and across classes alike.

Both halves of the claim hold as stated.

## Claim 3 — 299 / 0 / 253 — CONFIRMED

Comparing each row's `evaluable_n` to its own reported participant denominator:

- `evaluable_n <` reported denominator: **299**
- `evaluable_n >` reported denominator: **0**
- `evaluable_n =` reported denominator: **253**
- 299 + 0 + 253 = 552.

Median shortfall over the 299: **3**. Maximum shortfall: **112**. Both match the document.

## Claim 4 — 548/552, and the 4 that do not — CONFIRMED

Summing *all* integer categories for the row's group across the classes that contributed a stored
cell: **548** rows equal the reported denominator exactly. The **4** that do not are exactly the four
the document names, with the same numbers:

| NCT | group | all-category class sum | reported denominator |
|---|---|---|---|
| NCT01790503 | OG000 | 197 | 53 |
| NCT02150967 | OG000 | 118 | 59 |
| NCT02440464 | OG000 | 42 | 21 |
| NCT02440464 | OG001 | 44 | 22 |

Each is a multiple-of-the-denominator case: overlapping subgroup classes or repeated timepoint
classes, i.e. the same participants counted once per class, as the document says.

## Claim 5 — 10 / 51 / 22 — CONFIRMED

Definitions I used (chosen before reading the document's, and which reproduce its partition):

- **cross_class** — some stored label received assignments from two or more distinct class indices;
- **within_class** — not cross_class, but some stored label received two or more assignments (two
  category titles inside one class both matched the same regex);
- **none** — every stored label was assigned exactly once;
- **conflicting** — some stored label received two or more *distinct* values.

Counts: cross_class **10**, within_class **51**, none **491** (sum 552); conflicting **22**. All four
match `summary.json` and the document.

The 10 cross-class rows are exactly the 10 named in §5.2, and each is classified `unsupported` and
conflicting:

| NCT | group | om index | evaluable_n | reported denominator |
|---|---|---|---|---|
| NCT00654238 | OG000 | 0 | 1 | 55 |
| NCT01790503 | OG000 | 6 | 26 | 53 |
| NCT02150967 | OG000 | 11 | 55 | 59 |
| NCT02440464 | OG000 | 3 | 5 | 21 |
| NCT02440464 | OG001 | 3 | 3 | 22 |
| NCT02440464 | OG000 | 4 | 2 | 21 |
| NCT02440464 | OG001 | 4 | 2 | 22 |
| NCT02212015 | OG000 | 7 | 7 | 26 |
| NCT02212015 | OG000 | 8 | 12 | 26 |
| NCT04208958 | OG000 | 3 | 19 | 54 |

All ten of the §5.2 pairs (55 vs 59; 5 vs 21, 3 vs 22, 2 vs 21, 2 vs 22; 7 vs 26, 12 vs 26; 19 vs 54)
are reproduced. Since all 10 cross-class rows are conflicting, the remaining 12 of the 22
value-changing overwrites are within-class.

## Claim 6a — Exhibit A, NCT00654238 — CONFIRMED, every digit

`ctg_results_bor_1999_2009.txt`, `outcomeMeasures[0]`, title "To Determine the Efficacy (Best
Response) of BAY 43-9006 (Objective Response Rate and Stable Disease) in Patients With Metastatic
Thyroid Carcinoma.", group `OG000` "Sorafenib". Reported denominator, verbatim from `denoms`:
`Participants / OG000 = "55"`. Four classes, in this order:

| category (source title) | Differentiated | Poorly Differenitated | Medullary | Anaplastic | stored |
|---|---|---|---|---|---|
| Complete Response | 0 | 0 | 0 | 0 | **0** |
| Partial response | **16** | **2** | **1** | 0 | **0** |
| Stable Disease | **22** | **1** | **2** | 0 | **0** |
| Progressive Disease | 1 | 1 | 0 | 1 | **1** |
| Not Evaluable for Response | 5 | 2 | 0 | 1 | (dropped) |

PR 16/2/1/0 and SD 22/1/2/0 are exactly as claimed. Stored row is `{"CR":0,"PR":0,"SD":0,"PD":1}`
with `evaluable_n = 1` — the last class (Anaplastic) alone, since every label is overwritten in class
order. Class totals 44 + 6 + 3 + 2 = **55**, equal to the reported denominator, so this row is one of
the 548 in claim 4 and one of the 10 in claim 5. The characterisation "19 responses in 55 patients
enters as 0 responses in 1 patient" is arithmetically right (16+2+1 = 19 PR across strata; no CR).

## Claim 6b — Exhibit B, NCT01790503 — numbers CONFIRMED; two wording imprecisions

`ctg_results_bor_2010_2013.txt`, `outcomeMeasures[6]`, "Summary of Best Overall Response by Subgroups
in the Modified Intent-To-Treat Population on the Recommended Phase 2 Dose", group `OG000`
("Combined 800 mg, 5 Days/Week"). Confirmed exactly:

- **8 classes**, and they are the overlapping subgroups named: age 18–64 / 65+, complete / partial
  resection, KPS 70–89 / 90–100, MGMT methylated / unmethylated.
- Reported denominator `Participants / OG000 = "53"`; stored `evaluable_n` = **26**. **26 vs 53**
  confirmed.
- The within-class collision is real: each class lists `Complete response (CR)`, then
  `Partial response (PR)`, then **`CR+PR`**. `CR+PR` matches the `CR` regex and, being later in the
  class, overwrites the complete-response cell. Stored cells are
  `{"CR":3,"PR":2,"SD":12,"PD":9}` — the `3` is class 7's `CR+PR`, not its `CR` (which is 1).
- All-category sum over the 8 classes = **197** vs 53, the claim-4 exception.

Two imprecisions in the prose, neither of which changes a number and neither of which I count as a
refutation:

1. "stored row is the last subgroup (MGMT unmethylated)" is not exact. MGMT-unmethylated's own four
   cells are CR 1, PR 2, SD 12, PD 9, which sum to **24**, not 26. The stored row is the last
   subgroup **with `CR` replaced by that subgroup's `CR+PR`** — a within-class overwrite on top of
   the cross-class one. Sum 3+2+12+9 = 26 as stated. (Exhibit A's parallel phrasing, "the Anaplastic
   stratum alone", *is* exact, because that class had no colliding title.)
2. The regex is written as `^CR\b`. The producer's actual pattern is
   `^\s*(complete response|complete remission|CR)\b`, whose `CR` branch does match `CR+PR`
   (`\b` sits between `R` and `+`). The mechanism is as described; the quoted pattern is a shorthand.

## Claim 7 — the build assertion cannot catch this — CONFIRMED

The manuscript assertion is `research/manuscripts/endpoint/response-endpoint-indolent-tumours.md`
§2.3 (line 161): "Both this identity and the requirement that the four categories sum to the
denominator are asserted for every row, so an arm whose categories came from different denominators
fails the build rather than entering the distribution."

Its implementation is `research/manuscripts/orr_dcr_reread.py`, `rows_from_corpus`, lines 141–152,
which runs over every `C2_arms` row:

```
n = a["evaluable_n"]                                     # line 145
assert dc_ev - orr_ev == sd_ev                           # line 151
assert orr_ev + sd_ev + c["PD"] == n                     # line 152
```

The reasoning in the document holds, and it holds for a stronger reason than "the same cells":

- `evaluable_n` is *defined* as `sum(cells.values())` (`endpoint_corpus.py:209`), so line 152 reduces
  to `CR+PR+SD+PD == CR+PR+SD+PD`. It is a tautology for any row the producer emitted and can fail
  for none of the 552 — it is not a denominator check at all, because no denominator external to the
  cells ever enters it.
- Line 151 is likewise an algebraic identity: `dc_ev - orr_ev` is `(CR+PR+SD) - (CR+PR)`, which is
  `sd_ev` by construction.
- I confirmed both exhibits pass: NCT00654238 gives `0+0+0+1 == 1`; NCT01790503 gives
  `3+2+12+9 == 26`. Both are cells drawn from different source classes, i.e. exactly the
  "different denominators" case the prose says the build refuses, and both pass.

One qualification, so the finding is not overstated: the assertion is not dead code in the
literal sense. `research/manuscripts/tests/test_endpoint_logic.py:170`
(`test_cells_that_do_not_sum_to_the_denominator_fail_the_build`) shows it firing on a hand-constructed
row with `evaluable_n: 99`. It would catch a hand-edited or externally supplied corpus. What it
cannot do is catch anything in the producer's own output, which is the population the manuscript
sentence is about.

## Attempts to break the result that did not succeed

- Re-derived every count from the raw payloads rather than from any Job 1 script or intermediate.
- Checked the shard TSVs row-by-row against my replay (552/552 exact on cells, denominator, class
  total and signed difference) rather than trusting `summary.json`.
- Checked whether any row has zero or multiple `Participants` denominator entries, which would make
  "the reported denominator" ambiguous: none does.
- Checked the direction of every mismatch: no row's cells exceed the reported denominator, so no
  count is inflated; the defect is one-directional.
- Checked that the three overwrite categories partition the 552 rows exactly (10 + 51 + 491).
- Checked the file sizes and column count published in §6 against the files on disk: all match.

## Bounds of this check

I verified arithmetic and two exhibits. I did **not** adjudicate individual rows for whether a
given trial's row is scientifically usable, did not examine over-enrolment trials, and did not
assess Job 1's `valid` / `ambiguous` / `unsupported` labelling as a *rule* — I only confirmed the
label tallies (233 / 19 / 300) are what the shard files contain and are consistent with the
denominator and overwrite facts I recomputed. Arm identity, repeated assessment and overlap are
other jobs' questions and were not touched.
