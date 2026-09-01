---
id: DOC-SPRINT-S32-EMCDATA
title: "S32-EMCDATA — BLK-NO-EMC-DATA re-tested route by route: the blocker is right and sixteen routes cite it wrongly"
level: L3
kind: memo
status: live
date: 2026-09-01
audience: [autonomous research agents, maintainers]
purpose: "The findings record of sprint seat S32-EMCDATA — what it measured, what it changed, and what it could not do. Written before the seat returned, so a seat that dies costs its own work and nothing else."
scope: "One seat of the 2026-09-01 sprint, bounded by the owned-paths list in its own prompt. It reports; it does not decide what lands."
last_verified: 2026-09-01
---

# S32-EMCDATA — BLK-NO-EMC-DATA, re-tested one required_validation entry at a time

**Item(s):** `AUT-PD-116` (and, refuted in part, its summary in `S21-UNSCORED.md`)
**Owned paths:** `research/modalities/emc-blk-no-emc-data-route-retest.json` (new),
`research/autonomy/sprint-2026-09-01/S32-EMCDATA.md`
**Baseline:** `git rev-parse HEAD` = `b6397c5666efbf7d6755dfaedabc6a4bef24a8ee`
**Started/Finished (UTC):** 2026-09-01T19:54Z / 2026-09-01T20:4xZ

## Verdict

**PARTIAL** — all sixteen entries are adjudicated individually and **`BLK-NO-EMC-DATA` should come off
every one of them, while none of the sixteen is promoted, re-graded or made ready**; but the finding
that matters is that **the blocker was never wrong and the summary that sent me here was wrong in
both directions at once** — it under-reports what the repository already knows (six of the sixteen
were graded against the artifact three weeks ago) and over-reports what the artifact can answer
(three of the six it names as answered are answered by nothing in it).

---

## ⭐ THE FINDING, FIRST

### 1 · The blocker's own text never claimed expression data was missing

`BLK-NO-EMC-DATA` lives in **`systems/graph/blockers.json`**. Verbatim:

> **name:** *"EMC is nearly absent from public functional-genomics data (one DepMap line, n = 1, no
> CRISPR data)"*
> **statement_about:** *"data availability — the repo-wide rate-limiter, not any one route"*
> **retired_by_action:** *"What WOULD retire it is an EMC dependency or drug-response screen (a second
> EMC line in DepMap, a CRISPR screen, or an ex-vivo panel), none of which exists"*

The same field then **refuses two retirements it was offered**, on exactly this ground — the fourth
SRA cohort (*"a tumour expression panel is not a dependency screen, so nothing here touches it"*) and
the 2026-08-24 methylation cohort (*"a methylation reference set is not a dependency screen"*).

**So the blocker is one of the most carefully scoped records in the graph, and sixteen routes attached
an expression-or-tissue-read requirement to it anyway.** The defect is entirely in the routes.

⛔ **Nothing in this seat's work retires or weakens `BLK-NO-EMC-DATA`.** No EMC dependency screen,
CRISPR screen or ex-vivo drug-response panel has appeared. `RT-SYNLETH-DEP` — *"An EMC-specific
dependency screen"* — carries it correctly and is **outside** the sixteen, which is the boundary
working.

### 2 · This exact correction has already been performed once, and its shape is the instruction

`BLK-NO-CURATED-CLINICAL-DATA`'s own `retired_by_action` records it verbatim:

> *"Six routes across ST-LOCOREGIONAL and ST-STRATEGY inherited BLK-NO-EMC-DATA, whose own record
> scopes it to FUNCTIONAL-GENOMICS data (one DepMap line, no CRISPR). None of the six needs a
> dependency screen, so all six lost it. Only FOUR gained this one. … RT-SCHEDULING AND
> RT-TRIAL-REACH GAINED NOTHING AND ARE NOW UNBLOCKED OUTRIGHT."*

⭐ **That is the answer to "don't replace one string with another": the last time this was done the
correction was deliberately non-uniform, two routes ended up with no blocker at all, and one was left
showing a visible disagreement for its grade owner rather than papered over.** The sixteen below
follow the same shape.

### 3 · ⛔ REFUTED IN PART — six of the sixteen were graded against the artifact three weeks ago

`AUT-PD-116` says *"not one of them cites ART-EMC-EXPRESSION-PANELS."* **Literally true at HEAD** —
grepping each route record for the id returns zero. **Substantively false for six of them.**

`research/modalities/census-route-expression-grading.json` — registered as **`ART-CENSUS-ROUTE-GRADING`**,
whose `source_artifact` field is `research/modalities/emc-expression-panels.json` — grades sixteen
routes against that artifact, and **six of them are in this population**: `RT-MTAP-PRMT5`,
`RT-TXN-CDK`, `RT-MATRIX-SYNTHESIS`, `RT-MATRIX-ADDRESS`, `RT-IMMUNOCYTOKINE`, `RT-HYPOXIA-PRODRUG`.
Each cites it in `supporting_evidence`, and **for four of them the grade changed as a result**
(*"Premise NOT supported AS STATED"*, *"NOT SUPPORTED ON CAPACITY"*, *"PARTLY READ"*, *"GRADE
WITHDRAWN"*). A further five — `RT-SSTR2`, `RT-B7H3`, `RT-FAP-RLT`, `RT-CART-SURFACE`, `RT-TCRT-CTA` —
have their EMC-tissue readings written up in the live submission text
`research/manuscripts/surface-targets/emc-surface-target-landscape.md`.

**The row measured citation of an ID and reported blindness to a READING.** The stale layer is the
route JSON, not the repository's knowledge.

### 4 · ⛔⛔ AND THE ARTIFACT ANSWERS *LESS* THAN THE SUMMARY IMPLIES — THIS IS THE HALF THAT COULD HAVE DONE HARM

S21 names six routes the artifact "already answers". **Three of those six it does not answer at all,
and the artifact says so in its own words.**

| route | what the entry asks for | what the artifact holds | why it cannot reach it |
|---|---|---|---|
| `RT-JUNCTION-NEOANTIGEN` | *"Measured presentation on EMC tissue"* | the antigen-presentation **machinery** transcripts | **no peptide-HLA quantity exists anywhere in the file** |
| `RT-FUSION-OUTPUT` | *"Fusion-type-stratified EMC expression data"* | EWSR1 and TAF15 **gene abundance** | **neither series carries a partner label** — `sample_annotations_verbatim` contains `EWSR1`, `TAF15` and `fusion` **zero times, in both files** |
| `RT-MTAP-PRMT5` | *"A gene-level copy-number read of the locus"* | a transcript **triage** | `reads.read_9_MTAP_PRMT5.what_it_cannot_settle`: *"⛔ A TRANSCRIPT IS NOT A COPY NUMBER … expression can TRIAGE this question but cannot answer it"* |

`AUT-PD-116`'s own body **does** warn about the last two and says *"ADJUDICATE PER ROUTE AND DO NOT
BATCH THIS."* Its headline sentence does not carry the warning, and **S21 propagated the headline.**
A reader who took the summary would have unblocked three routes on data that cannot reach them —
the same error, in the same direction, as the `RT-PRAME-IMMTAC` precedent the row itself records.

⛔ **So the registrations that read *"keep registered; re-runs automatically when EMC expression data
lands"* are NOT all discharged.** `RT-CART-SURFACE`'s search has genuinely run (§5). `RT-TCRT-CTA`'s
series has genuinely landed — and cannot read three of the antigens it was wanted for.
`RT-FAP-RLT`'s expression half is genuinely taken. The other three are still waiting, on instruments
this program does not have.

### 5 · ⛔ The one place the dangerous direction is live: `RT-CART-SURFACE`

Its `next` says *"the antigen search re-runs automatically when EMC expression data lands."* **It
landed and the search ran.** Of 100 genes on `read_8_SURFACE_ANTIGEN.cross_platform_board`, exactly
five are `CONCORDANT_UP_ON_BOTH` — ALCAM, BGN, CD44, GPC1, VCAN — and of those **only ALCAM carries a
`RESTRICTED` normal-tissue window prior** in `emc-surface-normal-window.json`. A binder ladder for it
is already committed (`alcam-precedent.json`: an anti-CD166 ADC has reached patients).

**That is exactly the shape of a route somebody would unblock, and it must not be.** The route's own
owning manuscript demotes the candidate on the exposure axis: *"Its EMC median in the sequencing
cohort, 0.578, sits below the normal-organ median of 0.631"*, and *"the single antigen elevated on
both arrays is ALCAM, which no candidate route names."* Unblocking a CAR-T route on a transcript
contrast in n = 6 and n = 10 archival tumours, against an antigen its own exposure axis puts below
normal organs, is the `RT-PRAME-IMMTAC` error repeated. **`readiness.missing: ["a selective surface
antigen"] stays true and is not edited.** What changes is only that a completed search stops being
recorded as a standing promise.

---

## What I measured

Every reading below is a `$0` read of a committed artifact at `HEAD`; nothing was fetched and nothing
was run on CI or GPU.

**The population, reproduced rather than inherited.** `AUT-PD-116` names sixteen routes and
enumerates six. Applying the row's own stated recipe to `git show HEAD:systems/graph/routes.json` —
`required_validation` entries with `feasible_today: false` and `BLK-NO-EMC-DATA`, filtered to those
whose text names an expression or tissue read — returns **exactly sixteen**, and the same sixteen
against the working tree. (Twenty-three routes carry such an entry before the text filter; forty-four
of the seventy-seven routes reference the blocker somewhere.) One route, `RT-TRABECTEDIN`, differs
between `HEAD` and the working tree because a concurrent seat is correcting its clinical record; that
edit does not touch `required_validation[0]`, so the verdict holds on both.

**The instrument is licensed.** `reads.control` — ENO3 clearly higher in EMC on **both** platforms,
which is the artifact's own stated precondition for quoting anything below it. NR4A3 higher on
GPL6244.

**The environment reads that bound one proposal.** In this sandbox: no `Rscript`; `methylprep`,
`pandas` and `GEOparse` all absent (`numpy` and `scipy` present). `grep -rn` over the whole repository
returns **zero** hits for any copy-number-from-methylation method.

**The full per-entry adjudication — sixteen entries, sixteen verdicts, each with its evidence
address, the next action it permits, the claim that action would support, and its residual blocker —
is the deliverable and lives in
[`research/modalities/emc-blk-no-emc-data-route-retest.json`](../../modalities/emc-blk-no-emc-data-route-retest.json).**
It carries addresses, not re-typed figures: `emc-expression-panels.json` owns every number.

### The tally

| verdict | n | routes |
|---|---|---|
| **UNBLOCKED** — requirement satisfied as written | 3 | `RT-TCRT-CTA`, `RT-MATRIX-SYNTHESIS`, `RT-HYPOXIA-PRODRUG` |
| **PARTIAL** — one disjunct or axis taken; entry must be split | 5 | `RT-SSTR2`, `RT-B7H3`, `RT-CART-SURFACE`, `RT-FAP-RLT`, `RT-IMMUNOCYTOKINE` |
| **STILL BLOCKED, WRONG BLOCKER** | 8 | `RT-TRABECTEDIN`, `RT-JUNCTION-NEOANTIGEN`, `RT-SYNPROMOTER`, `RT-FUSION-OUTPUT`, `RT-TXN-CDK`, `RT-MTAP-PRMT5`, `RT-MATRIX-ADDRESS`, `RT-VACCINE-COMBINATION` |
| **STILL BLOCKED, BLOCKER CORRECT** | **0** | — by construction: the population was selected for naming an expression or tissue read, and this blocker is about functional-genomics data |

⛔ **Zero grade changes, zero readiness promotions, zero status changes.** Three of the sixteen
already had their grade moved by this reading three weeks ago; the rest keep theirs.

⚠ **44 of the 77 routes reference this blocker somewhere. Sixteen are adjudicated here; the other 28
were not tested by this seat and their attribution is UNKNOWN, not endorsed.**

### Three defects found on the way that are not `AUT-PD-116`

1. **A requirement string is copied onto a route it does not describe.** `RT-MATRIX-SYNTHESIS`,
   `RT-IMMUNOCYTOKINE` and `RT-HYPOXIA-PRODRUG` all carry the identical
   *"A measurement of the matrix compartment in EMC tissue"*. **The hypoxia route's premise is
   hypoxia**, and its real reading (`read_5_HYPOXIA`, audited by `emc-hypoxia-confounds.json`, grade
   withdrawn by `emc-hypoxia-reading.md` §5) is a different quantity entirely.
2. **Two committed files address a read by an id that has not existed since 2026-08-07.**
   `alcam-precedent.json -> the_emc_reading_this_rests_on.address` and `cd248_precedent.py:392` both
   point at `reads.read_7_SURFACE_ANTIGEN`. The surface read is `read_8`; `read_7` is `read_7_RET`.
   `research/modalities/tests/test_emc_expression_panels.py:243-245` records the rename and the
   collision that caused it. Both pointers are dangling and nothing checks them.
3. **A sibling manuscript asserts an absence its neighbour measures.**
   `research/manuscripts/surface-targets/fap-rlt-2026-regrade.md` carries a **2026-08-29** re-read and
   still states *"EMC-specific evidence: … still none REPORTED"*, explicitly defending
   `missing: ["any measurement in EMC"]` as *"the explicit test this re-grade had to pass"* — while
   `emc-surface-target-landscape.md`, in the same directory, reports the FAP EMC-tissue read on both
   platforms. ⛔ **The memo's substantive finding survives and must not be softened:** no FAP
   **protein**, IHC or imaging value in EMC has been reported, and the n = 1 EMC case inside
   PMID 38964294's 133-case cohort has unreported scores, so even a fully successful extraction ask
   leaves the protein gap open — **`CYC-0074` already ruled exactly that on 2026-08-29**, and this
   seat does not reverse it. **What is wrong is only that the words are now ambiguous between protein
   and transcript, and one reading of them is false.** Scoping them to protein/imaging preserves
   `CYC-0074`'s ruling verbatim and leaves the route's negative intact and slightly stronger.

### ⭐ One live lead, raised rather than taken

`RT-MTAP-PRMT5`'s own grader named the decisive next observation on 2026-08-09:
*"the cheapest decisive next observation is a copy-number or methylation read of the locus, not
another expression series."* **Fifteen days later a candidate source was committed and nothing
connects them:** `emc-data-level-sweep.json -> arms.pan_sarcoma_methylation_deposit` records **12 EMC
cases** in GSE140686, joined on an identifier both the deposit and the paper declare, with **24 IDATs,
every one HEAD-probed and reachable**, 9 on GPL13534 and 3 on GPL21145.

⛔ **Three bars, stated at full strength:**
- **Feasibility is UNKNOWN**, not assumed — see the environment reads above. Nothing in this
  repository has ever derived copy number from a methylation array.
- **trimcrae ruled on 2026-08-24** (`new-evidence-routes.md` §5.6) that this cohort is **not a
  priority paper**, and separately **refused a broad "methylation landscape of EMC" paper on the
  merits** at n = 12. **This proposal is neither** — it is a targeted 9p21 read serving a different
  route's stated requirement — but it is close enough to that call that it goes to the driver, not
  into a route record.
- n = 12; ten of the twelve are the classifier's own training set; two platforms; FFPE.

---

## What I changed

- **`research/modalities/emc-blk-no-emc-data-route-retest.json` — NEW.** The per-entry adjudication:
  the blocker's verbatim text and scope, the refutation above, and sixteen route blocks each carrying
  the entry's verbatim requirement, its JSON path, a verdict on the four-value scale, the evidence
  address, the next action, the claim that action supports, the claim it explicitly does **not**
  support, and the residual blocker. No figure is re-typed; every number stays in
  `emc-expression-panels.json`.
- **`research/autonomy/sprint-2026-09-01/S32-EMCDATA.md` — this file.**
- **Nothing else.** `systems/graph/routes.json` is held by two other seats and was read from `HEAD`
  only.

### `systems/graph/blockers.json` — owned, deliberately not edited

The blocker's own record is **the thing that is correct**, and editing it would force
`python3 systems/systems_check.py --write-views`, which regenerates `systems/views/registers/blockers.md`
**and every other view**, overwriting four view files another seat is currently holding
(`L1-st-repurposing.md`, `L2-rt-trabectedin.md`, `L3-publications.md`, `readiness.md`). Editing it
without regenerating turns the systems gate red for the whole wave. **The proposed edit, for the
driver to apply with a single regeneration on a settled tree**, is one append to `retired_by_action`,
in the same voice as the two refusals already there:

> ⚠ **AND THE EMC EXPRESSION PANELS DO NOT RETIRE IT EITHER, recorded here for the same reason as the
> two leads above.** `research/modalities/emc-expression-panels.json` reads 479 genes on EMC tumour
> tissue across two array series and is graded against sixteen routes in
> `research/modalities/census-route-expression-grading.json`. That is tumour PROFILING; this blocker
> is about FUNCTIONAL-GENOMICS data, so it moves this blocker not at all. ⛔ **What it DOES do is
> expose sixteen routes that cite this blocker for an expression or tissue read it never covered** —
> adjudicated one entry at a time in
> `research/modalities/emc-blk-no-emc-data-route-retest.json`, following the non-uniform correction
> `BLK-NO-CURATED-CLINICAL-DATA` records for six earlier routes.

`evidence` should gain `research/modalities/emc-blk-no-emc-data-route-retest.json`.

---

## What I could not do, and what it is actually waiting on

- **The sixteen route edits.** `systems/graph/routes.json` is held by two concurrent seats
  (a trabectedin correction and an HLA one). Every change is written per route in the artifact with
  its JSON path. **Waiting on: the driver sequencing three writers on one file.** Not on evidence.
- **The blocker edit.** Waiting on a settled tree for one `--write-views` pass. Not on evidence.
- **`RT-IMMUNOCYTOKINE`'s isoform question.** Whether the fourth cohort's whole-transcriptome
  TempO-Seq panel resolves the oncofetal fibronectin/tenascin domains is a **probe-manifest lookup,
  not an experiment**. I did not run it — it needs a fetch, and the seat brief says spend nothing and
  the manifest is not on disk. **Waiting on: one $0 CI fetch.**
- **`RT-TCRT-CTA`'s CTA coverage question.** Same cohort, same manifest, same single fetch: whether
  CTAG1B, MAGEA3 and SSX2 are in its gene space would decide the route's re-grade.
- **The MTAP copy-number read.** Waiting on a decision (above), then a feasibility check. Not on data.

---

## Ledger rows the driver should write

| `what` (abbreviated — full text in the artifact) | `kind` | `state` | `serves.route` |
|---|---|---|---|
| **Apply the sixteen per-entry corrections in `emc-blk-no-emc-data-route-retest.json` to `systems/graph/routes.json`**: drop `BLK-NO-EMC-DATA` from all sixteen entries, split the five PARTIAL entries, re-attribute eight to `BLK-NO-WET-LAB` / `BLK-NO-CURATED-CLINICAL-DATA`, and replace four `readiness.missing` strings a committed artifact refutes (`RT-SSTR2` *"any expression measurement in EMC"*, `RT-B7H3` *"a tissue-level measurement"*, `RT-FAP-RLT` *"any measurement in EMC"*, `RT-TCRT-CTA` *"a real EMC expression series"*). ⛔ Zero grade, readiness or status changes; `RT-CART-SURFACE`'s `missing` stays. | `process_defect` | `queued` | `null` |
| **Append the scope note to `BLK-NO-EMC-DATA.retired_by_action` and add the retest artifact to its `evidence`**, then one `systems_check.py --write-views` on a settled tree. Text drafted in `S32-EMCDATA.md`. | `process_defect` | `queued` | `null` |
| **`AUT-PD-116` is REFUTED IN PART and should be closed with the correction rather than re-run**: six of its sixteen were already graded against the artifact via `ART-CENSUS-ROUTE-GRADING`, and three of the six it names as answered are not answered by it (presentation, fusion-type stratification, copy number). | `process_defect` | `queued` | `null` |
| **`RT-HYPOXIA-PRODRUG.required_validation[1]` is a copied string** — *"A measurement of the matrix compartment in EMC tissue"*, identical on three routes, and this route's premise is hypoxia. Delete or replace with the requirement `emc-hypoxia-reading.md` §5 already states. | `process_defect` | `queued` | `RT-HYPOXIA-PRODRUG` |
| **Two committed files address a read id retired 2026-08-07**: `alcam-precedent.json -> the_emc_reading_this_rests_on.address` and `cd248_precedent.py:392` both point at `reads.read_7_SURFACE_ANTIGEN`; the read is `read_8` and `read_7` is `read_7_RET`. Nothing checks artifact-internal addresses. | `process_defect` | `queued` | `null` |
| **Scope `fap-rlt-2026-regrade.md`'s absence claim to protein/imaging.** Its 2026-08-29 re-read says *"EMC-specific evidence: … still none REPORTED"* while its sibling manuscript reports the FAP EMC-tissue transcript read on both platforms. ⛔ The protein gap is REAL, `CYC-0074`'s ruling that a successful extraction would leave it open STANDS, and only the scope of the words changes — the route's negative gets stronger, not weaker. | `process_defect` | `queued` | `RT-FAP-RLT` |
| **One $0 CI fetch answers two routes**: does PRJNA1357027's whole-transcriptome TempO-Seq panel manifest cover (a) the oncofetal FN/TNC spliced domains (`RT-IMMUNOCYTOKINE`'s own stated next action) and (b) CTAG1B / MAGEA3 / SSX2, unreadable on both arrays (`RT-TCRT-CTA`)? | `fetch` | `queued` | `RT-IMMUNOCYTOKINE` |
| **`RT-CART-SURFACE`'s antigen search has RUN and its `next` still records it as a standing promise.** Replace with the board result: 5 of 100 concordantly up, only ALCAM restricted on the normal prior, and ALCAM demoted by its own manuscript's exposure axis. ⛔ `readiness.missing` stays true. | `process_defect` | `queued` | `RT-CART-SURFACE` |
| **DECISION FOR TRIMCRAE — a targeted 9p21 copy-number read from the GSE140686 IDATs.** `RT-MTAP-PRMT5`'s own grader named a copy-number or methylation read of the locus as the decisive next observation; 12 EMC cases with 24 reachable IDATs were committed 15 days later. ⚠ Adjacent to the settled 2026-08-24 call that this cohort is not a priority paper, and feasibility here is UNKNOWN (no Rscript, no methylprep, no prior art in-repo). | `proposal` | `queued` | `RT-MTAP-PRMT5` |

---

## Gates

Scoped to my change (charter §6 — the wave is mid-flight, so no `preflight.sh`):

- `python3 -c "json.load(...)"` on the new artifact — **valid**, 16 route blocks.
- `python3 research/manuscripts/lint_consistency.py` — see the run report below.

⚠ **I wrote no guard, so charter §7 does not apply.** I ran no `git` write command of any kind.
