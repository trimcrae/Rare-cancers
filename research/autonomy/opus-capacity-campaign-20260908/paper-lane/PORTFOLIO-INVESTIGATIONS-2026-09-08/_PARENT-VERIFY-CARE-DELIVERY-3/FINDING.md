---
id: DOC-PORTFOLIO-INVESTIGATION-CARE-DELIVERY-3-2026-09-09
title: "The three trial series read: two are examined and print the fields nowhere by design, one was retrieved incompletely and stays UNKNOWN"
level: L4
kind: investigation
status: live
date: 2026-09-09
last_verified: 2026-09-09
---

# CARE-DELIVERY-3 — closing the residue CARE-DELIVERY-2 left, and refusing to close the part that cannot be

> ⛔ Nothing here is medical advice and nothing here asserts efficacy, safety, selectivity, a
> therapeutic window or clinical readiness. No patient was studied; no wet-lab work exists. Nothing
> here claims that specialist-centre care, referral or excision planning changes any EMC outcome.

**Source attribution.** According to PubMed, the three full texts below were retrieved from PubMed
Central through the PubMed MCP server on 2026-09-09.
martinbroto2020immunosarc1 — [DOI 10.1136/jitc-2020-001561](https://doi.org/10.1136/jitc-2020-001561).
stacchiotti2013anthracycline — [DOI 10.1186/2045-3329-3-16](https://doi.org/10.1186/2045-3329-3-16).
morioka2016trabectedin — [DOI 10.1186/s12885-016-2511-y](https://doi.org/10.1186/s12885-016-2511-y).
Carried through from CARE-DELIVERY-2 without re-reading:
bishop2019 — [DOI 10.1097/COC.0000000000000590](https://doi.org/10.1097/COC.0000000000000590);
drilon2008 — [DOI 10.1002/cncr.23978](https://doi.org/10.1002/cncr.23978).

## 1 · The question

CARE-DELIVERY-2 refuted `treatment_setting.recorded_in_any_reachable_series: false` and confirmed
`unplanned_excision.recorded_in_any_reachable_series: false` at four examined series, leaving three
systemic-therapy trial series UNKNOWN for both fields. **Do those three close the residue, and if
they do not print the fields, is that a curation gap or an absence by design?**

## 2 · Merit

Unchanged from the two parent lanes, minus one thing they could not settle. An absence claim over an
unexamined set tells the next session not to look; a *residue* over an unexamined set tells it to
look again, forever, at three papers where the answer may be structural. Settling which of the two
it is costs three retrievals and permanently retires the question — or, in the one case where the
retrieval was incomplete, says exactly why it cannot be retired yet.

## 3 · What was retrieved, per series — the part that decides everything else

The three retrievals **did not return the same thing**, and this is the finding that shapes the rest.
CARE-DELIVERY-2 could carry one global caveat because both of its retrievals came back
narrative-only. This lane cannot.

| series | PMCID | what came back | what did not | usable as an *absence*? |
|---|---|---|---|---|
| **martinbroto2020immunosarc1** | PMC7674086 | abstract, full narrative, **Tables 1–3 in full**, **all three figure legends** | the supplementary appendix; figure images | **YES** — Table 1 is the baseline-characteristics table |
| **stacchiotti2013anthracycline** | PMC3879193 | abstract, full narrative, **Tables 1–3 in full incl. the per-patient Table 2, all 11 rows and its footnote**, figure legends | figure **images** (Fig. 2 is the KM PFS curve, so any risk row under it) | **YES** — the most complete of the three |
| **morioka2016trabectedin** | PMC4946242 | abstract and narrative **only** | ⚠ **ALL tables, ALL figures, ALL legends** | **NO** |

For morioka2016trabectedin the in-text pointers arrive stripped to bare punctuation — *"Clinical
information of these subjects is presented in Table."*, *"(Table, Fig.)"*, *"are shown in Figs.and."*
— the same signature CARE-DELIVERY-2 recorded for bishop2019 and drilon2008.

> ⛔ **The dropped table is exactly the one that matters.** "Clinical information of these subjects"
> is where primary site, stage, prior treatment and any prior-surgery field for these five subjects
> would live. **This lane therefore asserts no absence for morioka2016trabectedin for any element
> that could live in it.** That is not caution for its own sake: the repository's own receipt
> `research/autonomy/receipts/CYC-0028-moriokat.json` records that this paper's Table 2 was read from
> the PDF page raster and carries per-subject PFS/OS with censoring flags. A "not printed" verdict
> drawn from its narrative alone would have been **demonstrably wrong**.

## 4 · Element by element, verbatim

### martinbroto2020immunosarc1 — IMMUNOSARC phase Ib/II, STS cohort, n = 68 (16 Ib + 52 II)

| element | verdict | what the paper says |
|---|---|---|
| **surgical margin** | EXAMINED, NOT PRINTED | Table 1 returned in full and prints **resectability, not margin**: *"Resectable at diagnosis, n (%): Resectable 10 (63) / 38 (73); Unresectable 6 (37) / 14 (27)"*. No margin status, no R0/R1/R2, no definition anywhere in abstract, narrative or Tables 1–3. |
| **follow-up** | REPORTED | *"At a median follow-up of 17 months (4–26), 37 of 49 (76%) per-protocol evaluable patients experienced progression"*. ⚠ Whole trial; time zero is enrolment on a second-line protocol. |
| **treatment setting** | **REPORTED — cohort-level constant** | Methods: *"enrolled in eight centers in Spain and Italy with expertise in sarcoma care. Central pathology review was mandatory before accrual."* Table 1 carries **no** per-patient centre, centre-volume or referral column. |
| **unplanned excision** | **EXAMINED, NOT PRINTED — and absent BY DESIGN** | The words *unplanned*, *inadvertent*, *whoops* appear nowhere. What Table 1 records of prior treatment is **systemic**: *"Median previous lines (range) 1.5 (0–5) / 1 (0–4)"*, *"Previous antiangiogenic lines"*. Eligibility is advanced STS progressing within 6 months; **the quality of a prior local excision is not a variable this protocol collects.** ⛔ Not a claim about the supplementary appendix, which was not returned. |
| **numbers at risk** | EXAMINED, NOT PRINTED | All three legends returned; **none is a KM curve** — Fig. 1 CONSORT, Fig. 2 waterfall, Fig. 3 per-patient swimmer plot. Matches the repository's own screen: *"NOT A PAIR - no KM curve exists"*. ⛔ No curve digitised; the closed KM/IPD pilot is not reopened. |

### stacchiotti2013anthracycline — Italian Rare Cancer Network, n = 11, **all EMC, all NR4A3-confirmed**

| element | verdict | what the paper says |
|---|---|---|
| **surgical margin** | EXAMINED, NOT PRINTED | Table 2 returned in full — columns are *Patient ID · Gender · Age · Diagnosis · NR4A3 · Site of primary tumor · Staging at time of initial diagnosis · Site of relapse at the time of chemotherapy · RECIST · PFS*. **No margin column.** The only resection-quality wording, *"macroscopic complete surgery"*, describes the **post-chemotherapy** resection of 3 patients, on no margin scale. |
| **follow-up** | REPORTED | *"At a median follow-up of 30 months, the estimated OS at 10-year was 50%"*. ⚠ n = 11, time zero is the start of chemotherapy for advanced disease. |
| **treatment setting** | **REPORTED — cohort-level constant** | *"treated … at Fondazione IRCCS Istituto Nazionale Tumori, Milano and those included in the data-base of the Italian Rare Cancer Network, registered by other Italian institutions"*. ⚠ Two strata are **named** — but Table 2 has no institution column, so **no patient is attributable to either**. |
| **unplanned excision** | **EXAMINED, NOT PRINTED — a visible omission, closer to a reporting choice** | Table 2 runs straight from *"Staging at time of initial diagnosis"* to *"Site of relapse at the time of chemotherapy"*. The primary operation that each of the **7 patients staged "localized disease"** must have had is **never described** — not its margin, not its planning, not where it happened. ⛔ An absence in the paper only; nothing is claimed about its source records. |
| **primary site** | **REPORTED, per patient** | Table 2: thigh 5, leg 3, buttock 1, arm 1, sacrum 1 = **11**. Cross-checks against the abstract's own *"lower limb/other = 9/2"*. |
| **stage at diagnosis** | **REPORTED, per patient** | Table 2: localized disease **7**, local + lung **4** = 11. |
| **numbers at risk** | **unchanged from v2, and this lane did not see it** | Fig. 2 is the KM PFS curve; only its legend (*"Median PFS 8 months"*) came through. The v2 REPORTED status rests on `emc-km-admissibility-2026-08-27.json`, which examined the figure. This lane neither confirms nor disturbs it. |

### morioka2016trabectedin — trabectedin phase 2 sub-analysis, n = 5 (**2 EMC + 3 mesenchymal chondrosarcoma**)

| element | verdict | why |
|---|---|---|
| **follow-up** | REPORTED | *"Median follow-up time of the randomized phase 2 study was 22.7 months"*. ⚠ **The whole 73-subject study**, not the 5-subject subset and not the 2 EMC subjects. |
| **time-to-event** | REPORTED | *"median PFS … 12.5 months (95 % CI: 7.4–not reached)"*; OS 26.4 months (10.4–26.4). ⚠ **Mixes 2 EMC with 3 MCS** — a different disease. |
| margin · margin definition · stage · primary site · treatment setting · **unplanned excision** · Cox | **STILL NOT_EXAMINED — UNKNOWN, not absent** | Tables not returned. See §3. |

Its only surgical sentence, Discussion: *"The basic treatment of EMCS is wide resection"* — a general
statement about the disease, naming no margin and counting nothing.

## 5 · The verdict on the two absence claims

**`treatment_setting` — UNCHANGED. Still FALSE.** One refuting series (bishop2019) was already
enough; three more were read and none reports the field per patient either. What changes is scope
and shape:

> **Examined set 4 → 6.** Of the six series now examined, **five hold the setting constant or omit
> it and exactly one (bishop2019) resolves it per patient.** A constant exposure cannot be an
> exposure, so no amount of further curation of the other five can answer the referral question.

**`unplanned_excision` — CONFIRMED AT SIX EXAMINED SERIES, not four.** Still a claim about the
examined set, never about every reachable series. No new proxy was found; bishop2019's 14/41 outside
excisions carrying the margin at referral remains the best available, and is still only a proxy.

> ⭐ **And the reason for the absence differs by series type — this is the new content.**
> In **martinbroto2020immunosarc1** it is **design-inherent**, shown against the paper's complete
> Table 1 rather than inferred from silence: a second-line systemic-therapy trial in advanced disease
> collects prior *systemic* exposure, not the quality of a prior local excision. **Further curation
> of trial reports of this shape will not produce the field.**
> In **stacchiotti2013anthracycline** it is closer to a **reporting choice**: a retrospective series
> whose per-patient table skips the primary surgical episode entirely.

**Still UNKNOWN for both fields:** `morioka2016trabectedin` (tables not returned), plus the eleven
candidate series never retrieved. Neither claim is a statement about them.

## 6 · A second finding the reading forced, which is not about field coverage

The trial series are not a source of poolable EMC values, for a reason **independent** of coverage:
**their denominators are not EMC.**

* `martinbroto2020immunosarc1` — n = 68 is the whole all-histology STS trial. Table 1 prints
  *"Extraskeletal myxoid chondrosarcoma 0 [Ib] 4 (7) [II]"* — **four EMC patients**. The only
  EMC-specific statement in the paper is *"partial response in patients diagnosed with … extraskeletal
  myxoid chondrosarcoma (n=1)"*.
* `morioka2016trabectedin` — n = 5, of which **2 have EMC**.
* `stacchiotti2013anthracycline` — n = 11, **entirely EMC**, the only pure EMC denominator of the three.

> ⛔ **Consequence, recorded as a caveat and not as an edit:** every element newly marked REPORTED for
> the first two is a **mixed-histology** value and must not enter an EMC element pool. The matrix's
> `candidate_patients_sum` of 1,133 is a weighting device over candidate series; this reading shows it
> also over-counts EMC patients for a **second, independent reason** beyond the series overlap already
> recorded. **No count was altered** — the caveat is added so no later session reads 1,133 as an EMC
> patient count.

## 7 · What changes for `emc-surgical-quality.json` beyond CARE-DELIVERY-2

**Little, and that is the honest answer.** Precisely:

1. `series_examined_for_this_field` on **both** fields: four → **six** (morioka deliberately excluded).
2. `treatment_setting.what_would_answer_it`: the five-hold-it-constant / one-resolves-it structure,
   with each of the five quoted.
3. `unplanned_excision`: the **design-inherent vs reporting-choice** distinction, and the statement
   that no better proxy was found.
4. `⛔_scope`: the global "tables were not read" caveat becomes **per series**, because it is no
   longer true globally.

**Unchanged:** both verdicts. The margin element — **still four series REPORTED, three poolable on
the R0/R1/R2 scale** — because *no trial series prints a margin at all*. `counts.series` (2) and
`counts.operated_patients_with_a_margin_recorded` (196) untouched; no count, distribution or measured
value added, removed or altered anywhere in the diff.

## 8 · Artifact · validation · provenance · limitations · stop condition

**Artifacts.**
`care-delivery-element-coverage-v3.json` — v2 with the three trial rows replaced by the actual
reading, each row carrying a new **`retrieval_completeness`** field, plus the re-decided audit
(`absence_claim_denominator_audit_v3`, with v2's preserved beside it) and the EMC-denominator
caveat. Generated by `build_v3.py`; **20 status changes**, all on the three trial rows, all listed
in `_status_changes_made_by_v3`.
`PROPOSED-UNAPPLIED-emc-surgical-quality-scope.diff` — **UNAPPLIED**, written against the **current
unpatched tree**, superseding and subsuming CARE-DELIVERY-2's diff (do not apply that one first).

**Validation.** `validate_v3.py`, **131/131 pass, exit 0** (`checks/05-validate-v3/`). It asserts,
among others: v2 and PUB-CARE-DELIVERY and `emc-surgical-quality.json` are untouched
(`git status` empty) and the recorded v2 input hash matches disk; the matrix still spans 17 series
summing to 1,133; every element's three buckets partition all 17 series and all 1,133 patients;
exactly 20 status changes, all on the three read series, none moving backward; bishop2019 and
drilon2008 rows carried through byte-identical; **morioka has zero `EXAMINED_NOT_PRINTED` cells and
moved only the two elements printed in its narrative**; the two table-complete series name a read
section on every not-printed cell; the counted-cell arithmetic holds (5+3+1+1+1 = 11, 7+4 = 11); the
margin REPORTED sets and the margin-scale split are **unchanged from v2**; both audit examined sets
are the six, with morioka in the residue; and no pooled rate, digitisation or clinical claim appears.
The diff is verified separately (`checks/06-dryrun-diff/`): `git apply --check` returns **0**, the
patched file parses as JSON, its `counts` block and `series` array are identical to the current tree,
and **no removed line carries a numeric value** (the only numerics on added lines are bishop2019's
quoted counts carried through from v2).

**Provenance.** Repo `/home/user/Rare-cancers`, branch `claude/confident-bardeen-ji76cd`, working
directory read concurrently — no copy, no worktree. Inputs: CARE-DELIVERY-2's v2 matrix (read, never
written) and three PMC full texts. Retrieval was **PubMed MCP only**; no direct HTTP fetch was made
to any host (that route is proxy-refused here: CONNECT 403 / curl exit 56), and no denied source was
reopened, reworded, model-switched or proxied around. Writes confined to this lane's directory
(`checks/07-no-shared-state-written/`). No `git add`, `commit`, `push`, `preflight`, subagent, GPU,
paid API or publication.

**Limitations.** (1) **Retrieval completeness is per series and is the binding limit** — see §3 and
the `retrieval_completeness` field; `morioka2016trabectedin` was read narrative-only and every
element that could live in its dropped table stays UNKNOWN. (2) `martinbroto2020immunosarc1`'s
**supplementary appendix was not returned**; its absence verdicts are not claims about it.
(3) Figure **images** were returned for none of the three; the numbers-at-risk row was not examined
by this lane for any of them, and `stacchiotti2013anthracycline`'s v2 REPORTED status rests entirely
on the earlier admissibility artifact. (4) The term scans in `checks/` are a **reading** of the
returned text, not an automated grep — the MCP response was deliberately not hand-transcribed to
disk, since a hand-copied primary source could silently drop a passage and manufacture a false
absence; short passages quoted are verbatim. (5) Two of the three series have **non-EMC
denominators** (§6). (6) The other 11 candidate series remain NOT_EXAMINED. (7) `masunaga2025` and
`chiusole2020` are still trusted from `emc-surgical-quality.json` and were not re-read. (8) The
element list is what these artifacts support, not a validated reporting checklist.

**Stop condition — reached.** The named residue was these three series. Two are now examined and
retire the question for good; the third is retrieved as far as this route allows and is recorded as
UNKNOWN with the exact reason. **This lane stops.** The only credible next step for morioka
2016trabectedin is a route that returns its tables — which this lane does not have and did not
attempt to manufacture.

**Honest outcome.** One absence claim's examined set doubled from its original two to six, with the
absence now shown against complete baseline tables rather than narrative silence, and with the reason
for it distinguished between design and reporting choice. One series' residue **not** closed, and
said so. Nothing new for the margin element. ⛔ This does **not** make `PUB-CARE-DELIVERY` writable —
that endpoint's publish decision is recorded "no" and `BLK-NO-FIELD-ATTENTION-MEASUREMENT` is
unresolved, and neither is touched or reopened here — and it does **not** touch the user-rejected
EMC-classification project, the retired patient-facing site, or the closed KM/IPD pilot. No clinical
claim is made.
