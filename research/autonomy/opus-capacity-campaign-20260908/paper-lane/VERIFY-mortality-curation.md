---
id: DOC-OPUS-CAMPAIGN-VERIFY-MORTALITY-CURATION
title: "Independent verification — the two mortality curation documents against the artifact"
level: L4
kind: memo
status: live
purpose: >
  Re-derive every count, percentage, row attribution and category total in
  CURATION-mortality-disease-membership.md and CURATION-mortality-attribution-and-overlap.md
  directly from the classified artifact, the retention probe and the retained abstracts, and
  report each claim as CONFIRMED, REFUTED or UNVERIFIABLE.
scope: >
  L4. Verification evidence only. Nothing was edited, committed, pushed, fetched or re-run.
  The mortality manuscript stays parked; no efficacy, safety, selectivity or readiness claim is made.
audience: [maintainers, external reviewers, autonomous research agents]
date: 2026-09-08
last_verified: 2026-09-08
---

# Verification result

**Claims checked: 50. CONFIRMED: 45. REFUTED: 3. UNVERIFIABLE: 2.**

⭐ **Both documents are arithmetically sound.** Every total closes against the 18 rows and the
50 documented-death instances; every percentage the documents themselves compute names its own
denominator; the claimed defect at row 13 / PMID 22569967 is real and is supported by the retained
words of the source; neither document treats summed patient instances as distinct records or unique
people; and neither asserts overlap or independence that the sources cannot establish.

The three refutations are **presentational bookkeeping slips inside otherwise correct sections**.
None of them changes a tally, a category total or a disposition. They are listed first so they are
not lost in the confirmations.

## The three REFUTED claims

**R1 · Membership doc, "What the sources DO support", line 309 — "A related but distinct defect is
present in three rows (4, 5, 8, and also 12)".** The parenthesis enumerates **four** rows.
**True value: 4 rows** (4, 5, 8, 12), across **3 records** (35665108, 23115670, 35775709), carrying
**8 documented-death instances**. The very next clause ("The disease is right in rows 4, 5 and 8")
shows the intended split, and the attribution doc's own source-type table independently gives
`cases collected from earlier publications | 35665108, 23115670, 35775709 | 8`. The word "three"
is the error; the substance elsewhere is right.

**R2 · Attribution doc, coverage check — "17 carry the coded observations above (including the five
non-death examples the classification already records)".** The **17** is correct; the parenthetical
is not. Recomputed from `review/title-eligible-retained-sentences.json` (34 papers) against the
classified artifact: the coded 17 are the **14 papers carrying documented deaths + 23213584 +
21941486 + 40885991**. Of the five `not_a_patient_death_examples`, only **40885991** is inside the
17; the other four (27418251, 24345066, 26125202, 35494187) fall in the **other 17** — where the
document itself correctly lists them. The document therefore counts those four on both sides of its
own partition in prose while its two lists remain disjoint and exact.
**True value: the coded 17 = 14 death-carrying records + 2 no-death rows + 1 registry.**

**R3 · Attribution doc, internal coding of the disease-entity instance.** The summary reads
"**3** instances name one … **1** instance names a **disease entity** and no event … The remaining
**46** are **UNKNOWN**" — arithmetically exact (50 − 3 − 1 = 46). But record entry **C4 · PMID
32963861** codes that same instance at record level as "**Terminal event: UNKNOWN** — a **named
disease entity**". So the per-record codings yield **47** UNKNOWN and the summary yields 46, because
the summary breaks the entity out of UNKNOWN and C4 leaves it inside. **The 50 still closes either
way**, and the entity/event distinction — the thing the field exists to protect — is preserved in
both places. It is a labelling inconsistency, not a lost or double-counted instance.

## UNVERIFIABLE (2)

**U-A · Membership doc, "Row 13 is the only instance of that exact defect among the 18 rows".** True
for the 16 rows whose membership the retained context settles. It cannot be established for **row 12
(35775709)**, whose own disposition in the same document is "⛔ membership **UNRESOLVED** … the
referenced table is not retained". A row whose population is not retained cannot be shown to lack a
second disease group. The claim is already qualified as "a statement about the retained context of
these 18 rows", which softens but does not remove this.

**U-B · Membership doc, Verification section — `lint_claims.py` exit 0 / 0 ERROR 4 WARN and
`lint_consistency.py` exit 0 / 0 ERROR across 29 targets.** Not re-run: the task fence forbids
producer and test execution. ⚠ The *internal* account of the 4 WARNs is self-consistent — the two
quoted phrases "13 patients with pathologically proven EMC" and "59 patients with confirmed EMC"
each occur exactly **twice** in the file (table cell plus per-row section), giving 4 hits, and both
are verbatim source wording from the 25177237 and 32612944 abstracts as claimed.

## 1 · Does the arithmetic close, and is every denominator the one it names?

**CONFIRMED.** Independently recomputed from `emc-terminal-events-classified.json`.

| quantity | re-derived | documents' use |
|---|---|---|
| rows in `individual_events` | **18** | both docs audit 18 |
| rows with `death_status != documented_death` | **2** (index 7 = 23213584, index 17 = 21941486) | both exclude exactly these |
| summed `n_patients` over documented rows | **50** | both use 50 |
| distinct PMIDs among documented rows | **14** | attribution doc's "14 records" |
| `mechanism_tier` totals | stated 4 / broad 18 / no-cause 27 / ambiguous 1 = 50 | consistent |
| `stated_type` within the stated tier | **3 named_terminal_event, 1 named_disease_entity** | see §3 |
| label totals | unstated 27, emc_progressive 8, ambiguous 1, remainder **14** → 14/50 = **28.0 %** | the hold's figures reproduce exactly |

Closures checked in the documents themselves:
- Membership doc partition **13 + 1 + 1 + 1 + 2 = 18** — CONFIRMED; the five lists are disjoint and
  cover rows 0–17 exactly once (13-row list contains 13 distinct rows: 0,1,2,3,4,5,6,9,10,11,14,15,16).
- Attribution doc **19 coded entries** (A1–A3, B1–B4, C1–C7, D1–D3, E1–E2) sum to **50** documented
  instances plus 2 no-death rows — CONFIRMED.
- Attribution table **11+1+1+2+2+1+2+2+28 = 50** — CONFIRMED; every per-category record list sums to
  its own cell (e.g. EMC-attributed 11 = 1+1+7+1+1; UNKNOWN 28 = 1+2+2+3+20).
- Source-type table **4+1+15+20+2+8 = 50** over **14** records — CONFIRMED (single-institution 15 =
  1+3+7+4; collected-from-literature 8 = 3+2+3).
- Overlap **8 SECONDARY + 42 UNKNOWN = 50** — CONFIRMED.
- Coverage **17 + 17 = 34** — CONFIRMED, and the enumerated "other 17" list matches the zip's
  title-eligible set exactly, PMID for PMID.

**Percentages.** The only percentages the documents compute are **40 % (20/50)** for 32612944's
block, stated twice and each time with its denominator named ("of the corpus's instances", "of the
total") — CONFIRMED. Every other percentage in either document is quoted verbatim from a source
(38.5 / 46.2 / 53.8 % of 13 in 36326382; 68.8 / 21.9 / 6.3 / 3.1 % of 128 in 40885991) and each is
internally correct against its own stated denominator — CONFIRMED. ⭐ Neither document restates the
hold's 28.0 %, and neither computes a mechanism share.

## 2 · The claimed defect at row 13 / PMID 22569967

**CONFIRMED — real, and correctly evidenced.**

Indexing first: the membership doc states "row numbers are the artifact's own array indices" and
uses **0-based** indices, so row 13 = `individual_events[13]` = PMID 22569967 (the 14th element).
That is the row it names.

The row as retained in the artifact:

> `"pmid": "22569967", "sentence_indices": [0, 1], "n_patients": 2, "label": "mechanism_unstated",`
> `"death_status": "documented_death", "mechanism_tier": "no_cause_or_mechanism_stated",`
> `"quote": "Two patients died of disease 8 months after the initial diagnosis."`

`emc-mortality-probe.json → terminal_events[34]` (PMID 22569967, *Virchows Arch* 2012, "NR4A3
rearrangement reliably distinguishes between the clinicopathologically overlapping entities
myoepithelial carcinoma of soft tissue and cellular extraskeletal myxoid chondrosarcoma") holds
exactly three sentences, and I read all three:

- `sentences[0]`: "Five patients were alive without evidence of disease, two were alive with disease
  and two died 8 months after the initial diagnosis. cEMCs were from three males and two females
  with an age range of 37–82 years (mean, 57 years); they presented in extremities, shoulder and
  paravertebral/cervical."
- `sentences[1]` — **the classified quote, verbatim**: "Two patients died of disease 8 months after
  the initial diagnosis."
- `sentences[2]` — **the cellular-EMC group's own statement**: "No patient died of the disease so far."

The membership doc quotes `sentences[2]` word for word, and its disposing evidence checks out: the
retained primary abstract (`rt-lung-mets-probe.json → queries.emc_topic_lung_mets.top[4].abstract`,
byte-identical copy at `queries.emc_topic_series_outcomes.top[17].abstract`) compares **ten MECs with
five cEMCs**; for MEC, "Follow-up, available for nine patients … Five patients were alive without
evidence of disease, two were alive with disease and two died 8 months after the initial diagnosis";
for cEMC, "Follow-up, available for four patients … **All patients were alive**, two with recurrences
and/or metastases and two without evidence of disease". 5 + 2 + 2 = 9 followed MEC patients, exactly
as the doc's table cell states.

⭐ So the two deaths sit inside the **myoepithelial-carcinoma** description, immediately before the
cEMC group is introduced, and the paper says of the cEMC group that no patient died. `sentences[1]`
is a body restatement that carries no group label — the doc's phrase "the extracted death sentence
had lost its disease-group attribution" is an accurate description of what the artifact holds.
⚠ Strictly, the group assignment of `sentences[1]` is an inference from the identical "8 months"
figure and the abstract's paragraph order rather than a group label on that sentence itself; the
document says so in effect by resting the finding on the abstract, and the negative statement at
`sentences[2]` closes it from the other side.

⚠ Cross-document consistency: the attribution doc deliberately does **not** decide this ("U10 …
Deliberately not coded in this lane"), recording only that the source type is a two-entity
comparison. The two documents do not contradict each other; one lane decides membership, the other
abstains and says so.

## 3 · "Only 3 named terminal events" vs the hold's "14 carrying a mechanism label"

**CONFIRMED, and no conflation is present.** This was the most likely defect and it is not there.

- `stated_type` recomputed over the artifact: **3 `named_terminal_event`** (35910216 pulmonary
  failure; 41799218 respiratory failure; 35775709's 9.5-year cerebral-haemorrhage split member) and
  **1 `named_disease_entity`** (32963861 colon cancer). The attribution doc reports exactly 3 and 1,
  attributed to exactly those PMIDs.
- The hold's **14** is a different quantity in a different unit: documented-death **instances**
  carrying a stored legacy mechanism label, i.e. 50 − 27 unstated − 8 emc-progressive − 1 ambiguous
  = 14, and 14/50 = 28.0 %. Reproduced exactly.
- The two are not merged anywhere. The attribution doc opens its coding section with "⚠ These are
  **my** coding definitions … They are not the package's legacy `label`, and they are not the
  package's `mechanism_tier`", and it never states or implies that only 3 rows carry a mechanism
  label. Neither document mentions 14 labels, 28.0 %, or any mechanism share at all.
- ⚠ **One collision hazard, correct as written.** The attribution doc's source-type table is headed
  "over the **14 records** carrying documented deaths" — 14 **publications**, which coincides
  numerically with the hold's 14 **instances** carrying a label. Both 14s are correct in their own
  unit and the doc names its unit each time, but a reader moving between the hold and this table
  will meet the same number meaning two different things. Worth a word of disambiguation if either
  document is ever quoted alongside the hold.

## 4 · Are summed patient instances silently treated as distinct records or unique patients?

**CONFIRMED — no. Both documents state the correct unit and hold to it.**

- Attribution doc: "Units are **reported patient instances**, as the retained rows define them",
  and in its supported list "⛔ The summed instances are therefore **not** established as distinct
  people." Its overlap grading exists precisely to carry that: 8 SECONDARY, 42 UNKNOWN.
- Membership doc: its summary is explicitly "Counted over the 18 preserved rows, and stated as **row
  dispositions** rather than as a tally of anything", and it says outright that the retained material
  "does **not** support a single validated EMC death count". Its "13 rows / 1 row / 1 row / 1 row /
  2 rows" figures are row counts, never presented as death counts, and each row's `n` is carried in
  the adjacent table column.
- No sentence in either document converts 50 instances into 50 patients, 50 records, or 50 deaths of
  distinct people. ⭐ This is the specific failure the hold warns about and neither document commits it.

Per-row instance counts were checked against `n_patients` one by one; all 18 agree, including the
multi-patient rows (35665108 n=2, 23115670 n=2, 35251555 n=2 and n=2, 35775709 n=3, 22569967 n=2,
25177237 n=3, 36326382 n=7, 32612944 n=20).

## 5 · Does either document assert overlap or independence the sources cannot establish?

**CONFIRMED — no. The hedging is correct in every instance I could test, and in places stronger
than required.**

- P1 (23115670 ↔ 35665108) is graded **SUSPECTED** and closed with "⛔ Retained material cannot
  decide it" — CONFIRMED as the right grade; the membership doc independently calls the same overlap
  "UNKNOWN and plausibly substantial".
- P2: I re-ran the document's own uniqueness check. Searching every retained sentence of all 162
  probe records for "cerebral hemorrhage", "9.5 year", "hepatic metastasis", "skin metastasis" and
  "congestive heart" returns **only** 35775709 sentence 0 — CONFIRMED. And the document draws the
  correct conclusion from it: "That is an absence of evidence for overlap, not evidence of
  independence."
- P3 (32612944 ↔ 41055792): the quoted review sentence is verbatim at `terminal_events[1].
  sentences[4]`, and 41055792 carries no classified death row — CONFIRMED, nothing double-counted.
- P4 (exclusion of 23115670's index patient as B1's patient): both discriminating facts are in the
  retained abstracts — total resection with no residual tumour and improvement at six months (2012)
  against partial resection and death at 36 months (2022) — CONFIRMED. It is an inference, but a
  discriminating one, and it is presented as an excluded candidate rather than as established
  uniqueness.
- D1's within-paper arithmetic (15 evaluated, "At last follow-up, 11 patients were alive", leaving
  4 = 2 + 2) is verbatim in the 35251555 abstract — CONFIRMED — and both documents label it
  "consistent with"/"not proof" and "**neither quotation states it**".
- Neither document anywhere claims that two reports describe different patients, that the 50
  instances are unique, or that any series is independent of any other.
- The registry rows (40885991) are recorded as **known internal overlap** and excluded from pooling
  in both documents, matching the artifact's own note — CONFIRMED.

## Source-binding spot checks (all passed)

- **All 18 classified quotes match their probe sentence verbatim**, at the exact index the membership
  doc's per-row pointers name: te[57].s0, te[16].s0, te[2].s0, te[18].s1, te[9].s1, te[9].s0,
  te[6].s0, te[26].s0, te[24].s0, te[12].s1, te[7].s3, te[7].s4, te[8].s0, te[34].s1, te[28].s2,
  te[5].s2, te[15].s1, te[27].s1. Every pointer in the document is correct.
- **Input hashes in the attribution doc's table are correct**: `emc-terminal-events-classified.json`
  21,732 B sha256 `94c48d42b65ed031…` and `emc-mortality-probe.json` 597,912 B sha256
  `386cd0c9376229d9…` both reproduce.
- **"primary abstracts for 11 of the cited papers"** — CONFIRMED: 11 of the 16 PMIDs in
  `individual_events` have a retained non-null abstract (12 including the registry 40885991). The
  five without are 35910216, 41799218, 28638563, 23213584 (no record) and 36097623 (record present,
  `abstract` null) — exactly the membership doc's "rows 0, 2, 3 and 7" plus its separate note that
  row 6's abstract field is null. ⚠ Checked against `rt-lung-mets-probe.json`; "anywhere in this
  repository" was not exhaustively re-swept.
- **Curation notes on deliberately excluded groups** all check out verbatim in the probe: 41799218
  sentence 2 (4 of 11 thrombectomy patients, a non-EMC table) and 36326382 sentence 5 (Enzinger and
  Shiraki, 4 of 34, another publication). ⚠ Both documents quote 41799218 sentence 2 from mid-sentence,
  dropping its leading citation fragment "11 , 39 , 40 )"; the retained words are unaltered.
- **P5's five within-record collapses** were re-read against the probe and all five are correct:
  35910216 s0/s1 one patient; 35251555 s3/s7 the same two ("two others died from concurrent
  malignancies within the first few months after diagnosis"); 25177237 seven sentences and three
  deaths, concordant with s0 "Among 13 patients, 3 died"; 36326382 s0/s2 the same seven; 41799218's
  own patient distinct from its table.
- **Non-contributing rows**: the membership doc's account of `aggregate_cause_splits` (3 overlapping
  40885991 strata), `prognostic_findings` (1) and `not_a_patient_death_examples` (5, with the right
  reason attached to each PMID) matches the artifact exactly.

## Fences observed

No manuscript, artifact, producer or curation document was edited. Nothing was committed or pushed.
No network call, no source fetch, no producer run, no test suite; the two lint results in the
membership doc were left unverified rather than re-run. Only this file was created.

⛔ Nothing here bears on EMC efficacy, safety, selectivity or clinical readiness, and nothing here
reopens the parked mortality manuscript or supplies a replacement tally for it.
