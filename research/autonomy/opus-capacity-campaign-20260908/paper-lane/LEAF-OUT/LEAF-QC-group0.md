# LEAF QC — group0: do the step-`f` registration-order ties have a recoverable metadata basis?

Leaf worker, question C, group 0. 121 assigned NCTs (`LEAF-ASSIGNMENTS/QC-group0.txt`).
Scope: only the step-`f` ("smallest outcome index") rows of
`CURATION-endpoint-identity-and-overlap-artifacts/TIES.tsv` for those NCTs.
Nothing outside my group was read or reasoned about.

## Provenance and integrity

- Cache: `/tmp/claude-0/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/scratchpad/ctg-cache-216bd1b5/`
- `sha256sum -c SHA256-MANIFEST.txt` → all 13 files `OK`, **exit code 0**.
- No network request was made. No producer, gate, test suite or manuscript was run. No tracked file was
  edited. The two files in `LEAF-OUT/` are the only things written.
- The preregistered rule was **not** modified and the global selection was **not** re-run. Steps a–e were
  replicated read-only for the sole purpose of reconstructing which measures were still competing at step `f`.

## Coverage

| | count |
|---|---|
| NCTs assigned | 121 |
| NCTs with ≥1 step-`f` tie row | 121 |
| step-`f` tie rows assigned | 333 |
| step-`f` tie rows reached and adjudicated | **333 (100%)** |
| rows left `UNRESOLVED` | **0** |

**Replication fidelity.** For all 333 rows my independent reconstruction (R0 canonicalisation, R1
candidate filter, ladder a–e) reached step `f` with a competing-set size *identical* to Job 2's
`candidates_still_competing` — 0 mismatches. Competing-set sizes: 2 candidates in 292 rows, 3 in 35, 4 in 6.
One normalisation detail had to be inferred: Job 2's group-title normalisation strips trailing
`.`/`,`/`;`/`:`/`!`/`?` but **not** brackets or parentheses (recovered from `NCT00493636` group
`a (sorafenib + gemcitabine or capecitabine)` and `NCT00906698` group `afatinib 20mg with vinorelbine i.v`).
With any other strip set some group keys do not join and the reconstruction fails; with this one, all 333 join.

## Headline result — Job 2's global claim does not hold for this group

**333 / 333 = 100% `BASIS_EXISTS`. 0 `NO_BASIS`. 0 `UNRESOLVED`.**

Every step-`f` tie in group 0 has at least one record field, never consulted by the ladder, on which the
competing measures differ. Field-level census over the 333 rows (a row counts once per field that differs
among its still-competing measures):

| field the ladder never compared | rows where competitors differ |
|---|---|
| `title` | 333 (100%) |
| `description` | 327 |
| `timeFrame` | 167 (161 substantively; 6 differ only in punctuation/case) |
| `populationDescription` | 116 |
| assessment criteria token (RECIST/IWG/Cheson/mRECIST/…) | 100 |
| `paramType` / `unitOfMeasure` | 72 |
| `type` (PRIMARY/SECONDARY/…) | 0 — as expected, step `a` already equalises this |

The ladder does read `title`, `description` and `populationDescription`, but **only** through six fixed
flag regexes (ITT/PP/confirmed/unconfirmed/central/investigator). It never compares the *endpoint the title
names*, the *timeframe*, the *assessment criteria* or the *reporting unit*. That is the gap.

## Classification of the 333 ties

Each row is assigned the single most decision-relevant basis (precedence: endpoint concept → timeframe →
assessment criteria → population → other substantive title difference → unit-only).

| basis tier | rows | what actually distinguishes the competitors |
|---|---|---|
| `A_DIFFERENT_ENDPOINT` | **159** | The competitors are *different endpoints*: ORR vs DCR (85), ORR vs CBR (63), ORR vs DCR vs CBR (11). |
| `B_TIMEFRAME` | 104 | Same endpoint concept, different `timeFrame` text. |
| `E_TITLE_SUBSTANTIVE` | 32 | Title names a different response construct outside the DCR/CBR lexicon (non-progression rate, complete-response rate, clinical-benefit response rate, Part I vs Part II analyses). |
| `D_POPULATION` | 26 | Same endpoint and timeframe, different `populationDescription`. |
| `C_ASSESSMENT_CRITERIA` | 10 | Different criteria token (e.g. RECIST vs modified RECIST). |
| `F_UNIT_DUPLICATE` | 2 | Same measurement reported twice, count vs percentage. |

The dominant finding is tier A + E = **191 of 333 rows (57%)** in which registration order is being used to
choose between *materially different endpoints*, not between two encodings of one endpoint.

### Worked examples (exact source pointers)

- `NCT00537095`, group `zd6474`, payload `ctg_placebo_onc_1999_2009.txt`, competing om **1** and **2**.
  om1 `"Disease Control Rate at 6 Months"`, `timeFrame` `"6 months after randomization"`, description
  `"...complete response + partial response + stable disease \> 24 weeks according to RECIST criteria"`.
  om2 `"Objective Response Rate"`, `timeFrame` `"46.7 months"`, description `"...defined as complete or
  partial response according to RECIST criteria"`. Step `f` selects **om1 (DCR)**.
- `NCT00753675`, groups `arm a vandetanib 300 mg` / `arm b` / `arm c`, payload `ctg_placebo_onc_1999_2009.txt`,
  competing om **1** (`"Objective Tumor Response Rate (CR+PR),"`) and om **2** (`"Disease Control Rate
  (CR+PR+SD)"`). Identical `timeFrame` `"up to 1032 days"` and `populationDescription` `"ITT"`; the
  distinguishing field is the title/description endpoint definition. Step `f` selects om1 (ORR) — correct
  here by luck of ordering, not by rule.
- `NCT01491672`, four groups, payload `ctg_results_bor_2010_2013.txt`, competing om **3**
  (`"Clinical Benefit Rate (CBR)"`, `"…CR or PR or stable disease… RECIST 1.0"`) and om **4**
  (`"Objective Response Rate (ORR)"`, `"…CR or PR… RECIST 1.0"`). Identical `timeFrame` `"20 months"`,
  identical `populationDescription` `"The FAS was used…"`. Step `f` selects **om3 (CBR)**.
- `NCT00473590`, groups `bort + p` / `bort + bv`, payload from the results-BOR set, competing om **0**
  (`"Number of Participants With an Overall Response"`, `unitOfMeasure` `participants`) and om **1**
  (`"Percentage of Participants With an Overall Response"`, `unitOfMeasure` `Percentage of Participants`).
  Same timeframe and population — a genuine unit-duplicate (tier F); registration order is harmless here.

## Question 3 — would the basis change the selection?

There is **no preregistered direction** for any of these fields, so I do not assert a new rule. I report the
one direction that is unambiguous from the rule's own stated intent — R1's regex is a *response-rate*
filter, and DCR/CBR/non-progression rate are pulled in only as collateral matches:

- **Under an endpoint-concept preference for the ORR-family measure over DCR / CBR / non-progression rate,
  15 of 333 rows (4.5%) change their selected measure.** These are listed with the exact replacement index
  in the TSV (`would_change_selection` = `yes`, `would_change_to_om`):
  `NCT00243074` om3→4; `NCT00324155` (2 groups) om1→4; `NCT00447057` (2 groups) om1→2;
  `NCT00537095` (2 groups) om1→2; `NCT00883779` (2 groups) om5→6; `NCT01491672` (4 groups) om3→4;
  `NCT01512745` (2 groups) om2→3.
- **176 rows: `no`** — the smallest-index measure already *is* the ORR-family measure, so under that same
  preference the selection is unchanged. The tie is still not metadata-free; it is merely benign.
- **142 rows: `indeterminate`** — the distinguishing field is `timeFrame`, `populationDescription`,
  assessment criteria or reporting unit, for which no direction is preregistered and none can be derived
  from the record without a policy decision that belongs to the parent. Basis exists; consequence is open.

## Honest limits

- Tier assignment and the field-difference census are **mechanical** (exact string comparison of record
  fields, plus fixed lexicons for endpoint concept and criteria tokens). They are re-derivable from the
  cache. The *interpretation* of a differing `timeFrame` is not mechanical: 161 rows have substantively
  different timeframe text, but some of those pairs are plausibly two phrasings of the same observation
  window (e.g. `NCT00095199`, `NCT00077857`). I therefore claim only that the field differs, not that the
  two measures observe different windows.
- Nine rows in tier A select DCR and four select CBR as the *smallest-index* measure; the remaining tier-A
  rows select an ORR-family measure. That split is the source of the 15-row change count above (plus two
  tier-E non-progression-rate rows).
- Because Job 2's selection code is not in the packet, steps a–e were re-implemented from
  `RULE-PREREGISTERED.md`. The exact match of all 333 competing-set sizes is the evidence that the
  re-implementation is faithful; it is not proof of byte-identical behaviour.
- Nothing here is a statement about efficacy, safety, selectivity, therapeutic window or clinical readiness,
  and nothing here corrects a manuscript. The endpoint manuscript remains parked.
- This result covers **group 0 only**. It refutes Job 2's claim *as a global claim* (a global claim fails on
  one counterexample, and there are 333), but the per-group rates for groups 1–3 are not mine to state.

## Files

- `LEAF-OUT/LEAF-QC-group0.tsv` — 333 rows, one per step-`f` tie: NCT, group key, competing outcome-measure
  indices, index selected by step `f`, classification, basis tier, distinguishing fields, would-change verdict
  and replacement index, a metadata summary of every competing measure, and the source payload file.
