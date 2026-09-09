---
id: DOC-PORTFOLIO-INVESTIGATION-CARE-DELIVERY-2-2026-09-08
title: "Reading the two series the coverage matrix left UNKNOWN: EMC treatment setting IS reported, and the absence claim that said otherwise is false"
level: L4
kind: investigation
status: live
date: 2026-09-08
last_verified: 2026-09-09
---

# CARE-DELIVERY-2 — follow-through on PUB-CARE-DELIVERY's named stop condition

> ⛔ Nothing here is medical advice and nothing here asserts efficacy, safety, selectivity, a
> therapeutic window or clinical readiness. No patient was studied; no wet-lab work exists. Nothing
> here claims that specialist-centre care changes any EMC outcome.

Source attribution: the two full texts below were retrieved **from PubMed Central through the PubMed
MCP server**. bishop2019 — [DOI 10.1097/COC.0000000000000590](https://doi.org/10.1097/COC.0000000000000590).
drilon2008 — [DOI 10.1002/cncr.23978](https://doi.org/10.1002/cncr.23978).

## 1 · The question

`research/modalities/emc-surgical-quality.json` asserts
`treatment_setting.recorded_in_any_reachable_series: false` and the same for `unplanned_excision`,
over an examined set of **two** series. Lane PUB-CARE-DELIVERY showed the quantifier was wider than
the reading and named the exact fix: read `bishop2019` (n = 41, PMC7771031) and `drilon2008`
(n = 87, PMC2779719) for **surgical margin status, follow-up duration, treatment setting and
unplanned excision**. Its route was blocked (403 at the proxy) and it stopped there.
**Are those two absence claims false, confirmed at a wider denominator, or still unknown?**

## 2 · Merit

Unchanged from the parent lane, and now sharper. What can be compared across EMC series is fixed by
what the series print, and an absence claim asserted over an unexamined set is the failure mode that
freezes a field: it tells the next session not to look. Resolving it costs two retrievals and either
removes a false blocker or hardens a real one. It also decides whether "where was the patient first
operated" is an available variable in EMC at all — the precondition for ever asking the referral
question — without needing a trial.

## 3 · The gap, and what closed it

The parent lane's residue was five reachable-but-unread series. Three
(`martinbroto2020immunosarc1`, `morioka2016trabectedin`, `stacchiotti2013anthracycline`) are
systemic-therapy trial reports of advanced disease where both fields are close to inapplicable. The
two decision-relevant ones were the retrospective operated-patient series. **The PubMed MCP route
worked**; both were retrieved on the first attempt (`checks/01-`, `checks/02-`, exit 0 each).

### ⛔ Exactly what was read, and what was not

The PMC full-text response carried **the abstract and the narrative sections only**. For bishop2019:
INTRODUCTION, MATERIAL AND METHODS (incl. *Follow-up and Statistical Analysis*), RESULTS (*Patient
and Tumor Characteristics*, *Treatment*, *Survival*, *Patterns of Disease Recurrence*, *Outcomes
After Relapse*), DISCUSSION. For drilon2008: the untitled introduction, MATERIALS AND METHODS
(*Patient Selection*, *Demographics and Statistical Methods*), RESULTS (*Clinical Features of Local
and Metastatic EMC*, *Treatment Outcomes for Localized Disease*, *Follow-up and OS*, *Chemotherapy
Outcomes*), DISCUSSION.

**Tables, figures and legends were NOT returned and were NOT read** — their in-text citations come
through stripped to bare punctuation ("Patient and tumor characteristics are listed in."). **Every
statement below that an element is not printed is scoped to those narrative sections and is not a
claim about either paper's tables.**

## 4 · Element by element, verbatim

### bishop2019 — MD Anderson, 41 consecutive localized EMC, 1990–2016

| element | verdict | what the paper says, and where |
|---|---|---|
| **surgical margin** | REPORTED | RESULTS/*Treatment*: "Final margin status was negative in 35 patients (85%) and positive/uncertain in 6 patients (15%)." ⛔ **Not** on the R0/R1/R2 scale, and no margin definition appears in the narrative text — so it raises the margin count to four series but **cannot be pooled** with the other three. |
| **follow-up** | REPORTED | RESULTS/*Survival*: "The median follow-up time from the completion of local therapy for patients alive at last follow-up was 94 months (range, 8–316 months)." Time zero is completion of local therapy, over survivors — not interchangeable with a from-diagnosis median. |
| **treatment setting** | **REPORTED, per patient** | RESULTS/*Treatment*: "Twenty-seven patients (66%) presented to MDACC with gross disease, whereas 14 patients (34%) presented after an outside excision had already been performed, of which 12 patients had a positive/uncertain margins and 2 had negative margins." Cohort setting from METHODS: "treated at the University of Texas MD Anderson Cancer Center… All diagnoses were confirmed at the time of presentation by sarcoma pathologists at MDACC… presented at a multidisciplinary tumor board." |
| **unplanned excision** | NOT PRINTED as such; strongest proxy in the literature | The words *unplanned*, *inadvertent* and *whoops* do not appear in the narrative text read, and the paper never says whether any of the 14 outside excisions was unplanned. What it does print is the 14/41 outside-excision count **with the margin found at referral**. |

### drilon2008 — MSKCC + Royal Marsden, 86/87 patients, 1975–2006

| element | verdict | what the paper says, and where |
|---|---|---|
| **surgical margin** | REPORTED, **with its definition** | METHODS: "(R0: complete resection, negative margins; R1, complete macroscopic resection, positive microscopic margins; and R2, incomplete resection)". RESULTS: "In a subset of 43 patients… 2 of 24 patients who underwent an R0 resection… 3 of 12 patients with an R1 resection and 5 of 7 with an R2 resection experienced local disease recurrence" → **R0 24 / R1 12 / R2 7 of 43**. ⚠ 43 of 73 curative-intent patients have a margin value; 30 (41 %) do not, and the paper does not say who they are. |
| **follow-up** | REPORTED | RESULTS/*Follow-up and OS*: "median follow-up time of 3.6 years (range, 0.2 years–24.6 years)". The authors flag it themselves in the DISCUSSION: "Our follow-up was relatively short compared with other series". |
| **treatment setting** | NOT PRINTED per patient — a **cohort-level constant** | Introduction: "a retrospective series of patients from 2 large referral centers"; METHODS names Memorial Sloan-Kettering and the Royal Marsden. No per-patient referral status, no first-operating-hospital field, no centre-volume variable in the narrative text. Same shape as chiusole2020: the exposure is held constant, so the series cannot answer the referral question. |
| **unplanned excision** | NOT PRINTED — a **visible omission** | METHODS: "using the date of wide local excision (WLE) as Time 0, **irrespective of previous procedures**", and DISCUSSION cites Kawaguchi on "the role of WLE despite previous procedures". Prior procedures are acknowledged twice and **counted zero times**; never defined, never called unplanned. This is an omission the paper's own analysis conditions on, not an inference from silence. |

Also recorded, not resolved: drilon2008's abstract says **87** patients while its Methods and Results
say **86**. Nothing here depends on it — the margin denominator is stated independently as 43 and the
curative-intent denominator as 73.

## 5 · The verdict on the two absence claims

**`treatment_setting.recorded_in_any_reachable_series: false` — FALSE.**
Not over-scoped; contradicted. `emc-surgical-quality.json`'s own `what_would_answer_it` asked for
"a series that reports **where each patient was first operated**". bishop2019 reports exactly that,
per patient, 27 inside the specialist centre versus 14 after an outside excision, in a series the
repository already counts as reachable and had already retrieved once for a different field.

⛔ **What this does not mean.** The exposure is a two-level in/out-of-centre split inside one
centre's referred population, with no comparator arm and no centre-volume variable. The field being
*recorded* does not make the referral question answerable, and **no association between treatment
setting and any EMC outcome is asserted here or anywhere in the revised diff.**

**`unplanned_excision.recorded_in_any_reachable_series: false` — CONFIRMED AT A WIDER DENOMINATOR
(four series, not two), and still a claim about an examined set.**
No examined series defines, names or counts an unplanned excision. But the available *proxy* has
changed: bishop2019's 14/41 outside excisions, carrying the margin at referral, is **stronger than
masunaga2025's undefined "previous surgery" field** that the artifact already rejected — anchored to
a named institution and carrying an outcome-relevant covariate. It is still a proxy: an outside
excision may have been a correctly planned resection.

**Still UNKNOWN:** `martinbroto2020immunosarc1`, `morioka2016trabectedin`,
`stacchiotti2013anthracycline` for both fields. Neither claim is a statement about them.

## 6 · What else the reading changed in the matrix

Four elements moved from a two-series base to a **four-series** base — margin distribution, primary
site, median follow-up, time-to-event median (358 of the 1,133 candidate patients, **non-additive**;
the series overlap). Margin *definition* is now printed by three. But the sharper number is this:

> **Three EMC series — masunaga2025 (156), chiusole2020 (40), drilon2008 (43) — print margin
> distributions on the same, defined R0/R1/R2 scale.** That is the largest set of EMC margin
> distributions that can actually be placed side by side, up from two. bishop2019 makes four
> *reported* and three *poolable*, because it collapses "uncertain" into positive and does not
> separate R1 from R2.

⛔ **Nothing is pooled here.** `emc-surgical-quality.json` already records that the denominator
choice moves the EMC positive-margin rate by more than the width of any interval, and all four
series carry informative missingness or a restricted cohort. No pooled rate is computed.

Two elements did **not** move: the numbers-at-risk row stays NOT_EXAMINED for both papers, because
the figures were not returned. ⛔ **The closed KM/IPD reconstruction pilot is not reopened; no curve
was digitised and nothing was re-run.**

## 7 · Artifact · validation · provenance · limitations · stop condition

**Artifacts.**
`care-delivery-element-coverage-v2.json` — the v1 matrix with the bishop2019 and drilon2008 rows
replaced by the actual reading, each element carrying its verbatim quotation, its section, and its
v1 status; recomputed element counts; the margin-scale split; and the re-decided absence-claim audit.
Generated by `update_coverage_with_read_fulltexts.py`.
`PROPOSED-UNAPPLIED-emc-surgical-quality-scope.diff` — **UNAPPLIED**, superseding the parent lane's
diff. It records the treatment_setting claim as refuted and the unplanned_excision claim as narrowed
to four examined series, and adds the bishop2019 proxy.

**Validation.** `validate_v2.py`, **78/78 pass, exit 0** (`checks/04-validate-v2/`): the v1 artifact
is untouched (`git diff` clean); the matrix spans the same 17 series with the same denominators
(patients sum 1,133); every element's three buckets partition all 17 series and all 1,133 patients;
**exactly two rows changed status** and they are the two that were read; every changed element cites
a section and carries its v1 status; the quoted arithmetic holds (35+6=41, 27+14=41, 12+2=14,
24+12+7=43); the two audit verdicts are the two decided values; the examined set is 4 and the residue
is the three trial reports; and the margin-scale split covers exactly the four REPORTED series.
The diff is verified separately (`checks/05-`): the patched file parses as JSON and
`git apply --check` returns **0**, and no `+`/`-` line touches a count or a margin value.

**Provenance.** Repo `/home/user/Rare-cancers`, branch `claude/confident-bardeen-ji76cd`, working
directory read concurrently — no copy, no worktree. Inputs: the parent lane's
`care-delivery-element-coverage.json` (read, never written) and the two PMC full texts. Retrieval was
by **PubMed MCP only**; no direct HTTP fetch was made to any host, and no denied route was reopened,
reworded or proxied around. Writes are confined to this lane's directory
(`checks/06-no-shared-state-written/`). No `git add`, `commit`, `push`, `preflight`, subagent, GPU,
paid API or publication.

**Limitations.** (1) **Narrative sections only** — tables, figures and legends were not returned and
were not read; if either paper tabulates a referral or unplanned-excision field, this lane would not
have seen it, and every not-printed verdict is scoped accordingly. (2) The term scans in `checks/01-`
and `checks/02-` are a **reading**, not an automated grep: the MCP response was deliberately not
hand-transcribed to disk, because a hand-copied 20 KB "primary source" could silently drop a passage
and manufacture a false absence. The short passages quoted were copied verbatim. (3) The other 13
series remain NOT_EXAMINED; for them every element is UNKNOWN. (4) Series denominators overlap and
are summed only to weight the accounting. (5) `EXAMINED_NOT_PRINTED` for masunaga2025 and
chiusole2020 is still trusted from `emc-surgical-quality.json`; those two texts were not re-read.
(6) The element list is what these artifacts support, not a validated reporting checklist.

**Stop condition — reached.** The parent lane's named stop condition was exactly these two
retrievals, and both are done. This lane stops. The remaining three-series residue is a low-value
read (systemic-therapy trials where the fields are near-inapplicable) and is left recorded as
UNKNOWN rather than pursued.

**Honest outcome.** One absence claim refuted on evidence, one confirmed at twice its old
denominator and still bounded, a better proxy found, and the poolable EMC margin set grown from two
series to three. ⛔ This does **not** make `PUB-CARE-DELIVERY` writable — that endpoint is held by
ledger row AUT-064's recorded publish decision ("no") and by `BLK-NO-FIELD-ATTENTION-MEASUREMENT`,
neither of which this work touches or reopens — and it does **not** touch the user-rejected
EMC-classification project. No clinical claim is made.
