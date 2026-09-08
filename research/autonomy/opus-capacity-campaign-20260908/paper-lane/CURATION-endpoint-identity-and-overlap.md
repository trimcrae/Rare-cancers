---
id: DOC-OPUS-CAMPAIGN-CURATION-ENDPOINT-IDENTITY
title: "Source validation — study / group / outcome / assessment identity, repeated time points and cohort overlap"
level: L4
kind: curation
status: live
purpose: >
  Independently establish, from the delivered ClinicalTrials.gov cache alone, which keys the source
  records actually carry, at which level a unit can be counted, which records repeat the same cohort,
  and where cohorts overlap. Produce a deterministic, pre-registered selection rule with every
  exclusion and tie recorded.
scope: >
  L4 source-validation evidence. It repairs no manuscript, reinstates no efficacy, cause-fraction or
  capacity claim, proposes no rate, and authorises no publication act. The response-endpoint
  manuscript remains parked; nothing here is an input to it until root adjudicates.
audience: [maintainers, external reviewers, autonomous research agents]
date: 2026-09-08
last_verified: 2026-09-08
---

# JOB 2 — identity, repeated assessments and overlap

⛔ This document produces **source-validation evidence only**. No efficacy, cause-fraction or
capacity claim is stated or reinstated. The endpoint manuscript stays parked and was not read,
edited or recomputed.

## Inputs — exactly the delivered bytes, nothing acquired

| item | value |
|---|---|
| cache directory | `…/scratchpad/ctg-cache-216bd1b5/` (session scratchpad) |
| cache revision | `216bd1b5fb25a56b90ef3cc2373e1fe68322708f` |
| payloads read | 12 (`ctg_*.txt`) + `_manifest.json`, `SHA256-MANIFEST.txt` |
| network activity in this job | **none** — no ClinicalTrials.gov request, no retry, no second copy, no synthetic record |
| parse | each payload is a 5-line header (`SOURCE URL`, `FINAL URL`, `HTTP`, `CONTENT-TYPE`) then `=`×70 then the API JSON body |

**Sharding: not used, deliberately.** The whole cache is 6,414 study records and parses in one
process in a few seconds, so volume did not merit a split; and because duplicate NCTs must stay
co-located for identity and overlap to be judgeable, a split would have had to be by hash of NCT id
anyway. One pass over one shared cache copy is the safe form of the same thing. Cross-shard
reconciliation is therefore not applicable — all duplicates were resolved in a single key space.

## 1 · Keys the source actually carries

| level | key that actually identifies it | stable? |
|---|---|---|
| study | `protocolSection.identificationModule.nctId` | **yes** — the only stable study identifier present |
| protocol arm | `armsInterventionsModule.armGroups[].label` (free text, no id) | text only; **no id**, and mostly not joinable to results (see §4) |
| outcome measure | position in `resultsSection.outcomeMeasuresModule.outcomeMeasures[]` + `type` + `title` + `timeFrame` | positional; **no registry-assigned id** |
| results group ("arm" as reported) | `groups[].id` (`OG000`…) **scoped to one outcome measure**, plus `groups[].title` | **id is NOT study-stable** (see §4) |
| assessment / population qualifier | free text inside `title`, `description`, `populationDescription` (ITT, per-protocol, confirmed, unconfirmed, investigator, independent/central) | **no coded field exists** |
| denominator | `denoms[].counts[]`, keyed by `groupId`, **per outcome measure** | per-measure, not per-cohort |
| measurement cell | `classes[].categories[].measurements[]` | per outcome measure |

## 2 · Unit counts at each actual level

Every count below is at the level named, on the canonical de-duplicated record set (§3).

| level | count | what one unit actually means |
|---|---|---|
| payload study records returned | **6,414** | one API row in one query file; **not** a trial — 329 trials appear more than once |
| distinct trials (`nctId`) | **6,081** | one registered study |
| trials carrying a results section | **4,235** | a study with posted outcome measures |
| protocol arm groups | **10,441** | a registered arm label; **not** a results group |
| outcome measures (all endpoints) | **46,493** | one posted measure of one endpoint at one time frame |
| outcome-measure group entries `(trial, measure, group)` | **133,623** | one cohort **as reported inside one measure** — repeats across measures |
| measurement cells | **467,069** | one number in one category for one group |
| response-titled outcome measures | **5,551** in **2,672** trials | a measure whose title names a response endpoint |
| response `(trial, measure, group)` rows | **16,101** candidate rows | **the number that must never be summed** — the same cohort recurs here up to 17 times |
| distinct response cohorts `(trial, normalised group title)` | **8,747** (8,728 after the POSTED filter) | one named reported cohort in one trial |
| trials contributing a selected response cohort | **2,632** | one trial |

⚠ **None of these is a count of unique patients**, and none of them is a count of independent trial
arms. Summing the 8,728 selected denominators gives **464,808 participant-slots**, which is an upper
bound with known internal double counting (§5), not a cohort size.

## 3 · Duplicate records — established, not assumed

- 329 NCT ids appear in more than one payload (325 in two, **4 in three**); 0 appear twice inside a
  single payload.
- Of those, **175 are byte-identical** across copies and **154 differ** — and every one of the 154
  differs **only by field set**, because the two accrual queries request fewer fields than the BOR
  and placebo queries. **No duplicate pair carries conflicting content.**
- Era files inside a query family are **disjoint** (0 intra-family duplicate NCTs in each of the
  three families), so the duplication is entirely **cross-query**, not cross-era.
- Overlap between the three query families, on the trials that reached the selection:
  **357** also appear in the placebo family, **98** in the accrual family, **10** in all three.
- Canonicalisation (rule R0): keep the copy with the most populated fields, ties by payload name
  ascending. Because the differences are field-set only, this is lossless.

⚠ Two payloads are **truncated by the API page size and were treated as incomplete**:
`ctg_accrual_completed_onc_phase2` returned 1,000 of `totalCount` 16,035, and
`ctg_accrual_terminated_onc` 1,000 of 2,027. Any statement about the accrual families is a statement
about the returned 1,000, not about the registry.

## 4 · Identity failures the source imposes

**(a) The results group id is not a study-level cohort key.** In **1,425 of 4,235** result-bearing
trials, one `groups[].id` (e.g. `OG000`) maps to **more than one group title** across that trial's
outcome measures. Ids are scoped to a single outcome measure. Any join on id across measures is
wrong; identity across measures must go by title.

**(b) Results groups mostly cannot be resolved to registered arms.** Only **4,227 of 17,124**
distinct results-group titles match a protocol `armGroups[].label` exactly (24.7%). Group counts also
disagree with arm counts: of the trials having both, **2,303** have exactly `#arms` groups in every
measure, **900** have at least one measure with **more** groups than arms, and **1,282** at least one
with **fewer**. So a reported cohort is not, in general, a registered arm.

**(c) Population, confirmation and assessment are unstructured.** There is no coded ITT / per-protocol,
confirmed / unconfirmed, or investigator / central field anywhere in the payloads; those distinctions
exist only as free text. Across the 16,101 response rows the fixed regexes flag ITT 4,691, per-protocol
or evaluable 3,829, confirmed 4,351, unconfirmed 505, independent/central 2,053, investigator 5,004.
These are **text flags, not source fields**, and unflagged does not mean absent.

**(d) Denominators are per-measure, not per-cohort.** **9,859 of 17,195** `(trial, group title)`
cohorts carry **more than one distinct** reported `Participants` denominator across that trial's
outcome measures. There is no single "the denominator" for a cohort in this source.

## 5 · Repeated assessments and cohort overlap — what was established, and how

**Repeated measurement of the same cohort (established by key collision).**
**4,461 of 8,728** selected cohorts had **more than one** candidate response measure (max **17**).
For **1,795** cohorts the candidates spanned **more than one distinct `timeFrame`** — the same named
cohort measured at different time points. For **1,246** cohorts the candidates gave **different
denominators**. Within cohorts, 568 carry both a central and an investigator measure, 750 both an
ITT-flagged and a non-ITT-flagged measure, and 76 both a confirmed and an unconfirmed measure. This
independently reproduces the *structure* root recorded as F2, from the raw records.

**Overlap between cohorts of the same trial (established against registered enrollment).**
After selecting exactly one measure per cohort, the selected denominators were summed per trial and
compared with `designModule.enrollmentInfo.count`:

| result | trials |
|---|---|
| summed cohort denominators **exceed** registered enrollment → overlap proven | **180** |
| summed denominators equal enrollment | 1,136 |
| summed denominators below enrollment | 1,316 |

Excess over registered enrollment totals **22,578 participant-slots**. Worked examples, both from
the source rows: `NCT01572038` reports cohorts `Age >65 Years` (230), `Age ≤65 Years` (968) **and**
`Docetaxel` (657), `Paclitaxel` (481), `Nab-Paclitaxel` (53), `Pertuzumab + Trastuzumab + Taxane`
(1,198) — two different partitions of the same 1,436 enrolled patients. `NCT01621490` reports 22
cohorts summing to 680 against 170 enrolled, including an explicit `Total` (140) alongside dose and
sub-population cohorts. **Cohorts of one trial are not disjoint patient groups.**

**Pooled-label cohorts.** 61 selected cohorts carry a pooled label (`Total`, `Overall`, `All
participants`, `All patients`, `Combined`). They are **flagged, not dropped**, because they are
supersets of other cohorts in the same trial and must never be counted alongside them.

**Time point inside the cohort name.** 25 selected cohorts in 7 trials embed a time point in the
group title itself (`W2`, `W4`, `Week 8`, …), so for those the source does not separate cohort
identity from assessment time at all.

## 6 · The deterministic selection rule

The rule was written and hashed **before it was applied**, from record structure only — key
stability, field presence, title vocabulary, denominator placement. No numerator, percentage, rate or
effect was inspected while it was written, and the rule was not revised after seeing any result.

- Frozen text: `CURATION-endpoint-identity-and-overlap-artifacts/RULE-PREREGISTERED.md`,
  sha256 `4545e83ef39df80aaf3548d71e9f3320596feec0e195c5c118172b3d55ed9df4`, 4,378 B.
- Unit: **one reported response measurement per `(nctId, normalised results-group title)`**.
- R0 canonicalise duplicate NCT copies → R1 candidate measures (fixed response regex,
  `reportingStatus == POSTED`, group present, `Participants` denominator present) → R2 ladder:
  **(a)** type PRIMARY > SECONDARY > OTHER_PRE_SPECIFIED > POST_HOC → **(b)** ITT/FAS > unflagged >
  per-protocol/evaluable → **(c)** confirmed > unflagged > unconfirmed → **(d)** central/independent
  > unflagged > investigator → **(e)** largest reported `Participants` denominator → **(f)** smallest
  outcome-measure index. Steps (e) and (f) are recorded as ties.

**Result: 8,728 selected measurements across 2,632 trials.**
Selected by type: 2,787 PRIMARY, 5,908 SECONDARY, 26 OTHER_PRE_SPECIFIED, 7 POST_HOC.
Selected flags: 2,433 ITT, 2,088 per-protocol/evaluable, 2,756 confirmed, 214 unconfirmed,
1,176 central, 2,347 investigator.

**Ties — all 2,001 recorded** in `TIES.tsv` with the step that resolved them and how many candidates
were still competing: 411 reached step (e) (largest denominator), **1,590 reached step (f)** and were
decided by registration order alone. Resolution: 6,842 cohorts settled within steps (a)–(d), 296 at
(e), 1,590 at (f). ⚠ The 1,590 step-(f) cohorts are cohorts the source's own metadata **cannot**
discriminate — the tie-break there is an arbitrary but reproducible convention, not evidence.

**Exclusions — all 3,530 recorded** in `EXCLUSIONS.tsv`: 1,846 trials with no results outcome
measures; 1,563 trials with results but no response-titled measure; 121 response measures with
`reportingStatus != POSTED`. **Zero** posted response measures lacked a `Participants` denominator,
and zero used a non-`Participants` unit — consistent with root's note that every frozen row carries
unit `Participants`.

## 7 · What the sources cannot identify — return this, do not substitute a number

1. **The intended unit of analysis of the parked manuscript cannot be recovered from these records.**
   The source supports *trial* and *reported cohort*. It does **not** support "independent arm": 75%
   of results groups do not match a registered arm label, group ids are not study-stable, and one
   trial's cohorts routinely overlap (180 trials prove it arithmetically). If the analysis needs
   independent arms, **this cache cannot supply them**.
2. **Unique patients cannot be counted at any level.** Denominators are per-measure, repeat across
   measures, and overlap within trials. 464,808 is a sum of participant-slots, not people.
3. **ITT vs per-protocol, confirmed vs unconfirmed, central vs investigator are text inferences**,
   not source fields; absence of a flag is not evidence of absence.
4. **1,590 cohorts have no metadata basis for choosing among their candidate measures** — recorded as
   ties, not resolved by evidence.
5. **The two accrual payloads are truncated** (1,000 of 16,035 and 1,000 of 2,027); no accrual-family
   statement generalises beyond the returned rows.
6. **Neither 552 nor 465 nor 138 was adopted as a target.** None was used as an input, a check or a
   goal; the counts above stand on the raw records alone.

## Artifacts

| file | rows | bytes |
|---|---|---|
| `CURATION-endpoint-identity-and-overlap-artifacts/RULE-PREREGISTERED.md` | — | 4,378 |
| `…/SELECTED-cohort-response-measurements.tsv` | 8,728 + header | 2,920,651 |
| `…/TIES.tsv` | 2,001 + header | 154,814 |
| `…/EXCLUSIONS.tsv` | 3,530 + header | 141,008 |
| `…/OVERLAP-enrollment-check.tsv` | 2,632 + header | 83,363 |

Nothing was committed or pushed. No file outside the `CURATION-endpoint-identity-and-overlap`
prefix was created or modified.
