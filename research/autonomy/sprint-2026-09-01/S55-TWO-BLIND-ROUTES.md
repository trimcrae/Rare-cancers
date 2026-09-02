---
id: DOC-SPRINT-S55-TWO-BLIND-ROUTES
title: "S55-TWO-BLIND-ROUTES — the negative's MEASUREMENT survives and its INFERENCE does not; the chaperone reading is category (d) by the route's own taxonomy and is not a promotion; and RT-MDM2's timing.rationale asserts the non-existence of a $0 open-access observation"
level: L3
kind: memo
status: live
date: 2026-09-02
audience: [autonomous research agents, maintainers]
purpose: >
  Verify S52-BLOCKER-PRECISION §4.2 against the primary source rather than inheriting it; establish the
  TP53 status question for RT-MDM2 or record it as UNKNOWN; state what each of RT-MDM2 and RT-CHAPERONE
  should be graded and why; and verify the S39 citation defect on both halves — the absence in the cited
  document AND what the primary source says.
scope: >
  Read-only over systems/graph/{routes,evidence,blockers}.json, research/literature/, research/modalities/
  and the literature-cache branch. Writes exactly two files: this memo and S55-proposed-route-evidence.json.
  Baseline HEAD b4cf28c6be8f464fc25e0cee06f6be50eb181138; literature-cache 0eac3e3aaa5b3e02c258611588e20162a7996515.
  No git write command was run. Measures nothing new; every reading is a $0 read of a committed file or a
  cached primary text.
last_verified: 2026-09-02
---

# S55 — two routes that never read their own compound, and what that is worth

**Seat:** acting on `S52-BLOCKER-PRECISION.md` §4.2, which is **verified here against the primary source,
not inherited.** S52's central factual claims all hold. **Two of its judgements do not**, and one of its
supporting dismissals is wrong. Both corrections are in §3 and §4.

**Owned paths, and the only two files written:**
`research/autonomy/sprint-2026-09-01/S55-TWO-BLIND-ROUTES.md` (this file) and
`research/autonomy/sprint-2026-09-01/S55-proposed-route-evidence.json`.
⛔ `systems/graph/*.json` was **read only** — another seat is auditing that tree and S41's patch is
pending on `routes.json`. `research/autonomy/research-ledger.json` was read (grep) and not written.
`S39-ATLAS-ADJUDICATION.md` and `S52-BLOCKER-PRECISION.md` are other seats' files and were not edited.

---

## ⭐ THE ANSWER UP FRONT

**★★ `RT-MDM2`'s "report the negative" does NOT survive — and the reason is narrower and more useful
than "the negative is wrong".** The expression measurement the negative rests on is untouched by
everything below; not one number in it is contested. What fails is an **unstated second step**: that low
p53 transcriptional output implies an MDM2/MDM4 antagonist is inactive in this disease. That step was
never tested, and two readings now bear against it. This is the **"reached without reading a relevant
source"** case, sharpened to the *inference* rather than the *measurement*.

**⛔⛔ AND THE ROUTE'S `timing.rationale` ASSERTS THE NON-EXISTENCE OF THE EXACT OBSERVATION IT NAMES AS
DECISIVE.** `systems/graph/routes.json:6062` reads *"Only a sequence-level TP53 call would reopen it, and
none is available."* A sequence-level variant list for **two fusion-confirmed EMC models** is a **$0
open-access fetch** — Bangerter Supplementary Table 1, PDF 89 KB, under `doi 10.1007/s13577-022-00818-x`,
CC BY. ★ **This is the same failure shape S52 corrected in `BLK-NO-EMC-DATA.retired_by_action` — a
sentence declaring absent a thing this repository has cached — in the same paper, on the same day, at a
second site.** That is a pattern, not a coincidence, and §6 says what it implies.

**★ `RT-CHAPERONE` gains a citation and NOT a promotion, and S52 overstates the gain.** S52 §4.2 calls a
direct EMC observation *"a different and better kind of evidence"* than the Ewing class transfer. Right
about the **disease**, wrong about the **kind**: the route's own clientship artifact already defines this
exact category and grades it **"ABUNDANT, AND IT IS THE WEAKEST CATEGORY"** (§4). Grade `◐ PARTLY
SUPPORTED` stands, unchanged, and the correct `strength` on the new citation is `class_inherited`.

**★ TP53 is UNKNOWN and stays UNKNOWN.** Verified independently: `TP53` and `p53` appear **zero** times in
the cached full text. §2.3 states exactly what the $0 fetch could and could not settle, because that
distinction is where an honest UNKNOWN gets quietly converted into a wild-type call.

**★ The S39 citation defect is REAL on both halves.** §5. Verified, not inherited.

**⚠ UNMEASURED: 6.** Enumerated in §7. Nothing in this memo rests on any of them.

---

## 1 · WHAT THE PRIMARY SOURCE ACTUALLY SAYS

Read from `git show origin/literature-cache:literature/bangerter-2023-emc-exvivo/PMC9813045.txt`
(29 246 bytes, 77 lines). ⚠ The containing directory is named `bangerter-2023-emc-exvivo/` but is a
**shared cache bucket** holding 90 unrelated files (FEP/alchemy method texts among them); the paper is the
one file `PMC9813045.txt`. Identifiers below are read from `systems/graph/evidence.json`
(`EV-BANGERTER-2023`) and from the blob, never from recollection.

### 1.1 The design, verbatim

| question | answer |
|---|---|
| what | *"A medium throughput drug screen using 40 drugs was conducted with USZ20-EMC1 at passage 5"* (`:37`) — 23 targeted agents + 17 chemotherapies, acoustic dispensing, 3-log 6-dose curves **from 33 pmol/l to 200 μmol/l**, 6-day CellTiter-Glo, AUC endpoint |
| on how many models | **Screen: n = 1** (USZ20-EMC1). Validation of **three compounds only** — carfilzomib, doxorubicin, venetoclax — in triplicate 6-point dose-response in **both** models at passages 8–10, top dose **10 µM** |
| models | USZ20-EMC1 (`EWSR1-NR4A3`, amputation specimen, 54 y) and USZ22-EMC2 (`TAF15-NR4A3`, diagnostic biopsy, 68 y); DKFZ sarcoma-classifier methylation score **0.99** for both; NR4A3 break-apart FISH confirmed |
| replicates in the SCREEN | **not stated.** The validation is explicitly *"in triplicates"*; the screen is not |
| normal-cell comparator | **none anywhere in the paper** |

⚠ **An internal discrepancy S52 did not surface:** Methods say the screen ran *"with USZ20-EMC1 at
passage 5"* (`:37`); Results say *"we subjected sarco-spheres at p6 from USZ20-EMC1"* (`:48`). Immaterial
to every conclusion here, recorded because a future session quoting one figure should know the other
exists.

### 1.2 ⛔ THE FORM OF THE OUTCOME — S52 IS RIGHT, AND THIS IS THE CAP

Verbatim (`:48`):

> *"Drug sensitivities were classified as (i) none, (ii) low to moderate and (iii) good to high."*

**The paper computes AUC and IC50 and prints neither in the text for any compound.** So there is no
number any route can rank, threshold, or compare against a class prior — for the five named compounds
included. S52's characterisation is exact and the cap it implies is the most important sentence in this
memo.

**★ AND THE CONCENTRATION AXIS IS MISSING WITH IT, WHICH NEITHER S52 NOR ITS LEDGER ROW STATES.** The
screen's dose range tops at **200 μmol/l**. With only an ordinal band printed, a *"good sensitivity"* call
**cannot be placed on a concentration axis at all** — it is not distinguishable from activity at a
concentration far above any achievable exposure. ⚠ The authors' own validation step used a top dose of
**10 µM**, twenty-fold lower. That gap is the single sharpest limit on both routes below.

### 1.3 The five named compounds and their bands, verbatim

> *"From the 17 tested chemotherapeutic drugs, carfilzomib, a proteosome inhibitor was the only compound
> that showed high sensitivity, followed by doxorubicin with good sensitivity."* (`:48`)

> *"PU-H71 (HSP90) and HDM201 (MDM2/MDM4) performed best from the compounds tested and showed good
> sensitivity while the cells had a moderate sensitivity to venetoclax."* (`:48`)

⛔ **READ THE NEXT SENTENCE, WHICH S52 OMITS AND WHICH SETS THE BASELINE THE WORD "BEST" IS AGAINST:**

> *"In general there was none to only moderate sensitivity for the most screened targeted therapeutics
> tested in USZ20-EMC1"* (`:48`), and in the Discussion: *"Drug screening identified limited sensitivities
> to most chemotherapeutic and targeted agents as kind of expected based on current clinical knowledge."*
> (`:50`)

★ **So "performed best from the compounds tested" is a RELATIVE RANK INSIDE A PANEL THE AUTHORS THEMSELVES
CALL LIMITED**, and PU-H71/HDM201 sit at **"good"**, not at the top of the top band — carfilzomib is *"the
only compound that showed high sensitivity"*. A route quoting "best-performing" without that baseline
inherits an overclaim the paper does not make.

### 1.4 ⛔⛔ THE FINDING S52 DOES NOT MAKE, AND IT IS THE DECISIVE ONE

**PU-H71 AND HDM201 WERE NEVER VALIDATED.** Verbatim (`:48`): *"Screening results of higher relevance were
validated and reproduced for calfilzomib, doxorubicin, and venetoclax"* [sic]. Neither PU-H71 nor HDM201
is reproduced by any second experiment in the paper.

**And the paper contains an internal calibration of how much an unvalidated screen band is worth.** Of the
three bands that WERE tested against dose-response in the same models:

| compound | screen band | validation outcome, verbatim (`:48`) | held? |
|---|---|---|---|
| carfilzomib | *"the only compound that showed high sensitivity"* | *"high sensitivity to carfilzomib"* | yes |
| doxorubicin | *"good sensitivity"* | *"good to moderate sensitivity to doxorubicin"* | yes, with slippage |
| **venetoclax** | *"moderate sensitivity"* | **"there was no response to venetoclax as a monotherapy in the validation"** | **NO — collapsed** |

★★ **One of three screen bands did not survive its own authors' validation, in these exact models, in
this exact paper.** PU-H71 and HDM201 sit one band above the one that collapsed and have not been tested.
⛔ **That is the calibration any use of their bands must carry**, and it is a limit derived from the
source itself rather than a generic hedge.

### 1.5 The copy-number reading, verbatim — and what it is NOT

> *"The copy number profiles exhibited gains mainly in chromosome 1, where the MDM4 locus is located, and
> in chromosome 8, where MYC is located for USZ20-EMC1."* (`:45`)

⛔ **This is a BROAD CHROMOSOME-1 GAIN THAT THE AUTHORS ANNOTATE FOR THE MDM4 LOCUS. It is not a focal
MDM4 amplification call**, carries **no copy-number value**, and the same paragraph reports *"there was a
rather flat CNV plot for both models"* (`:45`). ⚠ S52 §4.2 writes *"An MDM4 gain is a selecting feature
for this drug class"*, which reads as a focal lesion call and is a step past the sentence. The honest
statement is: *the screened model carries a chromosome-1 gain that the authors annotate for the MDM4
locus, on an otherwise near-diploid flat genome.*

⭐ **It does land on the right model.** The gain is reported for **USZ20-EMC1** — the same and only model
the 40-drug screen ran on. That co-location is real and is the one thing that makes the HDM201 band worth
citing at all rather than merely noting.

---

## 2 · TP53 — THE ANSWER IS **UNKNOWN**, AND HERE IS EXACTLY HOW FAR THE $0 FETCH COULD MOVE IT

### 2.1 Verified independently

```
grep -c -i "TP53" PMC9813045.txt  ->  0
grep -c -i "p53"  PMC9813045.txt  ->  0
```

**S52's claim holds exactly.** Neither string occurs anywhere in the 29 246-byte cached full text.

### 2.2 What the body text DOES say about variants, and why it is not an answer

> *"Tumor and sarco-spheres for both samples showed low tumor mutational burden (TMB) (< 5 mut/MB) and a
> stable microsatellite status (MS-stable). For USZ20-EMC1 on the DNA level multiple genomic short-variant
> mutations were detected that have been classified as **variants of unknown significance (VUS)**.
> USZ22-EMC2 harbors two additional likely pathogenic mutations in **MLL3** and **KDM5C** beside a
> **FANCA** alteration that has been classified as a VUS."* (`:45`)

⚠ **There is a tempting inference here and it must be refused.** All of USZ20-EMC1's called short variants
are VUS, and a pathogenic *TP53* lesion would not be classed a VUS — so the passage is *consistent with*
no pathogenic *TP53* call in the screened model. ⛔ **That is not an answer.** It requires two unverified
conditionals: that *TP53* is on the FoundationOne®HEME panel, and that it was adequately covered. The
paper states only *"up to 406 genes"* (`:36`) and lists none of them. **The panel's gene list is not in
the accessible record.** ★ **An absent reading is not a reading of absence** — CLAUDE.md §4. **UNKNOWN.**

### 2.3 ⭐ THE DISCRIMINATING OBSERVATION EXISTS, IS $0, AND ITS CEILING MUST TRAVEL WITH IT

> *"Details about these alterations are listed in the Supplementary Table 1."* (`:45`)
> *"Supplementary file1 (PDF 89 KB)"*, linked under `10.1007/s13577-022-00818-x`, CC BY open access (`:54`)

⛔ **SCOPE IT HONESTLY BEFORE ANYONE FETCHES IT.** Supplementary Table 1 is described as the list of
alterations **DETECTED** — not the panel's gene list. So it can establish *"no TP53 alteration was
detected on a hybrid-capture panel of up to 406 genes"* and **cannot by itself establish wild-type
TP53**. That is still strictly more than the current UNKNOWN, and it costs nothing.

⛔⛔ **AND THE ROUTE SAYS IT DOES NOT EXIST.** `systems/graph/routes.json:6062`,
`RT-MDM2.timing.rationale`, verbatim: *"Only a sequence-level TP53 call would reopen it, and none is
available."* Also `readiness.missing[0]`: *"a direct TP53 sequence call, which no available EMC dataset
supplies"*. **Both are false as written**, at a paper this repository has cited, resolved three
identifiers for, and cached in full since 2026-08-05.

★ **This is the second instance of the identical failure in one day, in the same paper.** S52 found
`BLK-NO-EMC-DATA.retired_by_action` asserting *"an ex-vivo panel … none of which exists"* about a panel in
the cache. This is a second sentence declaring absent a second thing in the same cached paper. §6.

---

## 3 · `RT-MDM2` — WHAT THE GRADE SHOULD BECOME

### 3.1 The current record, verbatim

- `grade.value` (`routes.json`, `RT-MDM2`): *"⛔ NOT SUPPORTED (2026-08-09). The class needs a p53 axis
  that is intact AND LIVE. The p53 transcriptional output group reads LOWER in EMC on BOTH platforms and
  the axis genes themselves are flat — quiet rather than live. ⚠ The quiet-genome argument that raised
  this route predicted the opposite."*
- `next.best_next_action` (`:6069`): *"Report the negative; the quiet-genome inference did not survive its
  own test."*
- `supporting_evidence`: one entry, `ART-CENSUS-ROUTE-GRADING`.
- `remaining_unknowns[0]`: *"Whether TP53 is wild-type, which this reading does not establish either way
  — most inactivating lesions are missense and leave transcript intact."*
- `evidence: []` — **empty.**

### 3.2 ★★ THE DISTINCTION THE BRIEF ASKED FOR, AND IT IS THE WHOLE FINDING

⛔ **THE NEGATIVE IS NOT WRONG. ITS WARRANT IS.** Nothing here contests one number in
`ART-CENSUS-ROUTE-GRADING`. The p53 transcriptional output group reads lower in EMC on both platforms;
that measurement stands at full original strength and keeps its original wording.

**The negative has two steps and only the first was measured:**

| step | status |
|---|---|
| 1 · p53 transcriptional output reads LOW in EMC on both platforms | **MEASURED. Stands.** |
| 2 · therefore an MDM2/MDM4 antagonist is inactive in this disease | **NEVER TESTED, and two readings now bear against it.** |

**Reading A — direct, in this disease, weak.** HDM201 is called one of the two best-performing targeted
agents in an ex-vivo EMC model (§1.3), in the model carrying the chromosome-1 gain the authors annotate
for the MDM4 locus (§1.5). ⛔ Ordinal band, n = 1, **unvalidated**, no AUC, no comparator, no concentration
anchor, no clinical exposure. **A signal to look further and nothing more.**

**Reading B — indirect, a depositor's claim, NOT evidence.**
`research/modalities/emc-cohort-search-inputs.json:317-326`, GEO series **GSE315379**, *"Epigenetic
regulation of p53 represents a targetable dependency in synovial sarcoma"*, 18 samples, taxon **Mus
musculus**, `pubmed: null`. Its summary reports MDM2 dependency in synovial sarcoma lines, that *"Very few
synovial sarcomas in humans demonstrate TP53 mutation or loss"*, that *"Transcriptome analysis revealed
minimal change in p53 target gene expression, suggesting that expression of the fusion alone was
sufficient to impact these"*, and that HDM201 *"was modestly successful at slowing tumor growth, alone"*.
★ **That is the same inferential pattern this route graded on — a fusion-driven sarcoma with quiet p53
transcriptional output — and in it the quiet output coexists with reported MDM2 dependency and HDM201
activity.** ⛔ **It is a claim, not a measurement, and it is not proposed as evidence**: the artifact
carries its own flag, verbatim, *"title and summary are the depositors' CLAIM, not a measurement"*, and it
is mouse, a different disease, and unpublished at the record. **It cannot carry a grade. It can say the
inferential step is not safe.**

⚠ **CORRECTION TO S52.** `S52-BLOCKER-PRECISION.md:288` states HDM201 *"appears elsewhere in the
repository only as unrelated GEO sample titles ('HDM201 rep1/2/3')"*. Those titles
(`emc-cohort-search-inputs.json:2271/2276/2291`) are the **treatment arm of this very series**, and the
series summary at `:326` is substantive and on-topic. **The dismissal is wrong.** The S52 conclusion it
supported — that the S39 pointer has no home — is unaffected and still holds (§5).

### 3.3 ⭐ THE PROPOSED GRADE

**From** `⛔ NOT SUPPORTED` **to** `⛔ NOT SUPPORTED ON EXPRESSION · ◐ UNRESOLVED ON PHARMACOLOGY`.

⛔ **THE ROUTE DOES NOT BECOME SUPPORTED, AND NOTHING HERE ARGUES THAT IT SHOULD.** n = 1, ordinal,
unvalidated, TP53 UNKNOWN, no concentration anchor, and the class's stated dose-limiting haematological
toxicity liability recorded in the route's own `rationale` is untouched. What changes is that a terminal
negative becomes an open question with **a named $0 action under it**.

**`next.best_next_action` should be replaced.** Its current text is wrong about the cheapest remaining
observation. The replacement: fetch Bangerter Supplementary Table 1 and record whether a TP53 alteration
was **detected** in either model (§2.3 ceiling attached), then re-state the negative knowing what the
pharmacologic reading actually is.

**`timing.rationale` should be corrected under rule 1.2**, retaining the superseded clause. Drafted in
`S55-proposed-route-evidence.json`.

⚠ **`timing.recommendation` (`monitor`) and `state.status` (`parked`) need not move.** What moves is that
`monitor` acquires a concrete free action instead of a wait on `TECH-EMC-EXPRESSION-DATA`.

---

## 4 · `RT-CHAPERONE` — A CITATION, NOT A PROMOTION, AND S52 OVERSTATES THE GAIN

### 4.1 The blindness is real and is a scoping miss, not a fabrication

`research/literature/fet-fusion-chaperone-clientship-2026-08-27.json`, string counts at baseline HEAD:

| string | count |
|---|---|
| `Bangerter` · `USZ20` · `USZ22` · `EMC1` · `9813045` · `36316541` · `ex vivo` | **0 each** |
| `PU-H71` | **8** — all Ewing sarcoma or non-FET contexts |

S52's claim verified exactly. ⚠ **And the cause is legible in the artifact rather than mysterious:** its
recorded query is Ewing-scoped, verbatim (`:251`) *"(\"Ewing sarcoma\"[TIAB]) AND (geldanamycin OR
\"17-AAG\" OR \"17-DMAG\" OR ganetespib OR tanespimycin OR \"PU-H71\" OR \"HSP90 inhibitor\")"*. **A sweep
scoped to another disease cannot find this disease's paper.** That is a process finding worth more than the miss.

### 4.2 ⛔⛔ THE CORRECTION TO S52, AND IT INVERTS THE FRAMING

S52 §4.2 argues the addition *"changes … that the dependence-without-binding half acquires a direct EMC
observation in place of a Ewing transfer"* — a *"different and better kind of evidence"*.

**Right about the DISEASE. Wrong about the KIND.** This route's own artifact already defines the category
and grades it. `fet-fusion-chaperone-clientship-2026-08-27.json:18`, key
`d_fusion_driven_line_sensitive_to_an_HSP90_inhibitor`, verbatim:

> *"ABUNDANT, AND IT IS THE WEAKEST CATEGORY. Ewing and myxoid liposarcoma lines and xenografts are
> sensitive to 17-AAG, 17-DMAG, ganetespib, PU-H71 and an HSP90 C-terminal-domain inhibitor. **Sensitivity
> of a fusion-driven line is not clientship of the fusion** — in the one Ewing paper that actually assayed
> physical HSP90 interaction (PMID 18676850), the clients named are AKT, KIT and IGF1R, and the fusion is
> not among them."*

★★ **Bangerter's PU-H71 result IS category (d).** Moving a category-(d) observation from Ewing to EMC
**does not change its category**, and by the route's own written standard category (d) cannot reach the
route's premise, which is a **binding** question.

⚠ **AND ON RIGOUR IT IS THE WEAKER OF THE TWO, WHICH IS THE OPPOSITE OF S52'S ORDERING.** The Ewing
PU-H71 item in that same artifact carries an immunoblot/RPPA readout of fusion-protein depletion —
verbatim (`:67`): *"Exposure to PU-H71 resulted in depletion of critical proteins including AKT, pERK,
RAF-1, c-MYC, c-KIT, IGF1R, hTERT and **EWS-FLI1** in Ewing cell lines"* — a mechanistic readout adjacent to the
clientship question. **Bangerter carries an unvalidated ordinal viability band on n = 1 with no protein
readout at all.** On disease it is nearer; on premise it is further.

### 4.3 ⭐ THE PROPOSED GRADE

**`◐ PARTLY SUPPORTED` stands, unchanged.** The addition is one `supporting_evidence` entry at
`strength: class_inherited` — ⛔ **deliberately not `direct`**, because it is direct on disease and
indirect on premise, and the premise is what the route is graded against. Grading it `direct` would let a
viability band stand in for a binding measurement.

**`next.best_next_action` should NOT change.** It is the IntAct/BioGRID `IM-22301` fetch (PMID 25036637 as
recorded in the route), which addresses the binding premise. That is still the right next action and this
reading does not displace it.

**One `remaining_unknowns` entry is added**: the PU-H71 AUC rank is in Fig. 2b and is unread — ⚠ **and is
not obtainable**, since the matrix is not deposited. A standing UNKNOWN, not a queued fetch.

---

## 5 · THE S39 CITATION DEFECT — REAL ON BOTH HALVES

`research/autonomy/sprint-2026-09-01/S39-ATLAS-ADJUDICATION.md:166`, verbatim, a row in the table
*"evidence_score.json `what_the_atlas_already_rejected_or_downgraded` (8 entries) -> ALL EIGHT ARE ON
MAIN"*:

> `| MDM2/MDM4 — HDM201 not a USZ hit | `repurposing-hypotheses-review.md` (identities resolved via CI full text) |`

**Half one — the absence in the cited document. VERIFIED.**
`research/manuscripts/repurposing/repurposing-hypotheses-review.md`, 8 657 bytes, 126 lines:

```
grep -c -i "hdm201" -> 0
grep -c -i "mdm"    -> 0
grep -c -i "usz"    -> 0
```

The document is an internal review of `repurposing-hypotheses.md` draft v0.2 — its section headings are
*Overall judgement*, *Strengths*, *Major issues*, *Minor issues*, *TxGNN result — stress-tested*,
*Accuracy items verified in this pass*, *Required human actions before submission*. **It says nothing
about HDM201, MDM2, MDM4 or the USZ models.** The pointer resolves to a real file that does not contain
the claim.

**Half two — what the primary source says. VERIFIED, AND IT IS THE OPPOSITE.** §1.3: *"PU-H71 (HSP90) and
HDM201 (MDM2/MDM4) performed best from the compounds tested and showed good sensitivity"* — in USZ20-EMC1,
which is a USZ model. **"HDM201 not a USZ hit" is contradicted by the only source that could settle it,
and that source is in this repository's own literature cache.**

⛔ **This is a third axis beyond CLAUDE.md §7's provenance/strength orthogonality.** The identifier
resolves (provenance intact), the claim is flatly stated rather than over-hedged (strength is not the
issue), and what fails is that **the cited document does not support the claim**. `lint_citations` cannot
see this — it checks that identifiers resolve, not that documents contain what they are said to contain.

⚠ **AND IT WAS LOAD-BEARING**: the row sits in the table S39 uses to argue all eight atlas rejections are
already represented on `main`, which supports its verdict that nothing needs recovering from the atlas.
**The verdict may well still be right** — that adjudication rested on many readings, seven of which are
not touched here — but one support does not hold.

★ **The fix is a correction under rule 1.2, not a deletion**: strike the assertion, record what the
primary source says, and re-state whether the atlas verdict survives without it. ⛔ **Not done here.**
`S39-ATLAS-ADJUDICATION.md` is another seat's file and this seat did not open it for writing.

⚠ **One thing this memo cannot settle:** whether the error originated in S39's transcription or in the
atlas's own `evidence_score.json`. S39 records the atlas files were *"read from the branch, not
recovered"*, so the atlas source was not checked here. **UNMEASURED (§7).** It matters for the fix's
wording and not for its necessity.

---

## 6 · ★★ THE PATTERN UNDERNEATH ALL THREE, WHICH IS BIGGER THAN THE THREE

Three sentences, one repository, one paper:

| where | the sentence | what it declares absent | what is actually in the cache |
|---|---|---|---|
| `blockers.json`, `BLK-NO-EMC-DATA` (corrected by S52 today) | *"an ex-vivo panel … none of which exists"* | an ex-vivo EMC drug panel | `EV-BANGERTER-2023` |
| `routes.json:6062`, `RT-MDM2.timing.rationale` | *"Only a sequence-level TP53 call would reopen it, and none is available"* | a TP53 sequence call for an EMC model | Bangerter Suppl. Table 1, CC BY, 89 KB |
| `routes.json`, `RT-MDM2.readiness.missing[0]` | *"a direct TP53 sequence call, which no available EMC dataset supplies"* | same | same |

⛔ **THE FAILING CLASS IS "A CLAIM OF NON-EXISTENCE, WRITTEN FROM WHAT THE AUTHOR HAD LOADED RATHER THAN
FROM A SEARCH."** Every one is grammatical, hedged in form, in the right register, and passes every gate
this repository owns. **Nothing computes on any of them** — they are prose fields — so the entire blast
radius is on the reader, and in this repository the reader is the next session, which inherits each as a
fact and stops looking.

★ **The mechanically checkable version of this defect is cheap and does not exist yet.** Every one of
these sentences asserts the non-existence of a class of thing; every one is falsified by a committed
`EV-*` record or a cached blob. A guard that flags a non-existence claim in a graph prose field against
the committed evidence collection would have caught all three. ⚠ Filed as a row, not built here — this
seat owns two files and neither is a test. **S52 §7 already proposed the narrow version of this for
`BLK-NO-EMC-DATA`; the finding here is that it is a repository-wide class rather than one blocker's
problem.**

---

## 7 · ⚠ UNMEASURED — 6, AND NOTHING ABOVE RESTS ON ANY OF THEM

1. **The AUC/IC50 matrix for all 40 compounds.** Fig. 2a/b only; not deposited. ⛔ **Not obtainable** —
   data availability is *"available from the corresponding author on reasonable request"*, an offer to a
   person and not a fetchable dataset.
2. **35 of 40 compound identities.** Same reason.
3. **TP53 status in either model.** UNKNOWN. Supplementary Table 1 is a $0 fetch and would move it partway
   (§2.3), and was not fetched by this seat.
4. **Whether TP53 is on the FoundationOne®HEME panel and adequately covered.** The paper says *"up to 406
   genes"* and lists none. Not asserted from recollection anywhere above.
5. **Whether the S39 error originated in S39's transcription or in the atlas's own `evidence_score.json`**
   (§5). The atlas source was not read.
6. **Whether GSE315379 has since been published.** `pubmed: null` in the record read; no live check was
   run. ⚠ CLAUDE.md §4: a remembered reading would understate, so this stays UNKNOWN rather than being
   filled in.

---

## 8 · What I wrote, and what I did not touch

**Written — two files, both new:**
- `research/autonomy/sprint-2026-09-01/S55-TWO-BLIND-ROUTES.md` (this file)
- `research/autonomy/sprint-2026-09-01/S55-proposed-route-evidence.json` — the proposed patch, **not
  applied**, with per-route justification and the ceiling attached to every proposed citation.

**Not touched:** `systems/**` (read-only; two seats in that tree, S41's patch pending on `routes.json`),
`research/manuscripts/**` (grepped, not opened for writing),
`research/autonomy/research-ledger.json` (grepped; the driver writes it),
`S39-ATLAS-ADJUDICATION.md` and `S52-BLOCKER-PRECISION.md` (other seats' files).

**Git:** read-only throughout — `git show`, `git ls-tree`, `git rev-parse`, `git log`. ⛔ **No git write
command was run.**

**Gates:** `./scripts/preflight.sh` was **not** run by this seat — it is the driver's to run once, with
the whole sprint's tree settled (CLAUDE.md §6).

---

## 9 · Ledger rows the driver should write

| what | kind | state | serves |
|---|---|---|---|
| **`RT-MDM2.timing.rationale` and `readiness.missing[0]` both assert that no sequence-level TP53 call is available for an EMC model, while Bangerter Supplementary Table 1 (PDF 89 KB, `doi 10.1007/s13577-022-00818-x`, CC BY) is a $0 open-access fetch.** Correct both under rule 1.2 and fetch the table, recording that it lists alterations DETECTED and so cannot alone establish wild-type. Patch drafted in `S55-proposed-route-evidence.json`. | `fetch` | `queued` | `RT-MDM2` |
| **`RT-MDM2`'s `next.best_next_action` = "report the negative" is wrong about the cheapest remaining observation.** Apply the proposed grade split (`NOT SUPPORTED ON EXPRESSION · UNRESOLVED ON PHARMACOLOGY`) and the two `supporting_evidence` entries. ⛔ Not a promotion: the expression measurement stands at full strength and the route does not become supported. | `process_defect` | `queued` | `RT-MDM2` |
| **`RT-CHAPERONE` should cite `EV-BANGERTER-2023` at `strength: class_inherited`, not `direct`.** Its own clientship artifact grades this evidence category *"ABUNDANT, AND IT IS THE WEAKEST CATEGORY"*; ⛔ S52 §4.2's "different and better kind of evidence" framing should not be carried forward. No grade change, no `next` change. | `process_defect` | `queued` | `RT-CHAPERONE` |
| **A literature sweep scoped to another disease missed this disease's own paper.** `fet-fusion-chaperone-clientship-2026-08-27.json`'s recorded query is `"Ewing sarcoma"[TIAB]`-anchored, which is why PU-H71-in-EMC was invisible to it. Consider a standing rule that any compound-scoped sweep runs the compound name unanchored by disease at least once. | `process_defect` | `queued` | — |
| **`S39-ATLAS-ADJUDICATION.md:166` cites a document that does not contain the claim, and the primary source says the opposite** (§5, both halves verified). Correct under rule 1.2, and check whether the error is S39's transcription or the atlas's own `evidence_score.json`. ⚠ `lint_citations` cannot see this class: the identifier resolves and the strength is fine; the SUPPORT is absent. | `process_defect` | `queued` | — |
| **A guard for non-existence claims in graph prose fields.** §6: three sentences in two files declared absent things sitting in this repository's own cache, all of them gate-clean. Assert that no prose field in `systems/graph/**` claims the non-existence of a class of thing that a committed `EV-*` record or a cached blob satisfies. ⚠ Generalises S52 §7's `BLK-NO-EMC-DATA`-scoped proposal to the repository. | `process_defect` | `queued` | — |
| ⚠ **Correction to `S52-BLOCKER-PRECISION.md:288`** — HDM201 does NOT appear elsewhere in the repository "only as unrelated GEO sample titles". `emc-cohort-search-inputs.json:326` (GSE315379) is a substantive, on-topic HDM201 record in a fusion-driven sarcoma. S52's conclusion is unaffected; the supporting dismissal is wrong. | `process_defect` | `queued` | — |
