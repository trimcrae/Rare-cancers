---
id: DOC-PORTFOLIO-EXPOSURE-INDEX-2-FINDING
title: "EXPOSURE-INDEX-2 — resolving EXPOSURE-INDEX's UNKNOWN EMC denominators through the admitted PubMed/PMC route, and naming what blocks the rest"
level: L4
kind: evidence-index
status: live
date: 2026-09-09
last_verified: 2026-09-09
---

# EXPOSURE-INDEX-2 — FINDING

Lane: `…/PORTFOLIO-INVESTIGATIONS-2026-09-08/EXPOSURE-INDEX-2/`. Writes confined to this directory.

⛔ **This is a provenance index, not evidence synthesis.** Nothing here asserts or implies efficacy,
safety, selectivity, a therapeutic window, prognosis or any treatment recommendation, and nothing here
is patient-specific advice. No wet lab. Counting who has been counted is not a statement about what
happened to them. No patient datum, citation or count was invented; every figure below is copied
verbatim from a returned PubMed/PMC record and is quoted with its locator.

According to PubMed. Records used, with DOIs:
[10.1002/cncr.23978](https://doi.org/10.1002/cncr.23978) ·
[10.3389/fonc.2020.00828](https://doi.org/10.3389/fonc.2020.00828) ·
[10.1097/COC.0000000000000590](https://doi.org/10.1097/COC.0000000000000590) ·
[10.1186/s13018-025-06245-6](https://doi.org/10.1186/s13018-025-06245-6) ·
[10.3390/cancers17172924](https://doi.org/10.3390/cancers17172924) ·
[10.18632/oncotarget.15568](https://doi.org/10.18632/oncotarget.15568) ·
[10.1007/s00432-025-06316-5](https://doi.org/10.1007/s00432-025-06316-5) ·
[10.1002/cncr.20968](https://doi.org/10.1002/cncr.20968) ·
[10.1097/CCO.0b013e32812143d9](https://doi.org/10.1097/CCO.0b013e32812143d9)

## 1 · Question

**Of the 19 rows where EXPOSURE-INDEX recorded `n_emc_status: UNKNOWN`, how many resolve through the
admitted PubMed/PMC route — and for the rest, what exactly is the blocker?**

EXPOSURE-INDEX deliberately performed no retrieval, so its UNKNOWNs conflate three different things:
a figure nobody looked for, a figure that is not in PMC, and a figure that is in the paper but not in
what PMC returns. Separating those is the whole of this lane's contribution.

## 2 · Merit

*Patient relevance.* An UNKNOWN denominator is not a stable state — it is either a real limit of the
published record or a gap this program never tried to close. The portfolio's manuscripts cite these
series; if 14 of 28 EMC denominators are unread purely because nobody made a call, every downstream
statement about how much evidence exists is understated in an unknown direction.

*Non-trivial contribution.* EXPOSURE-INDEX's own §9 named "resolving `overlap_unknown`" as the highest-
yield next step and correctly declined it. This lane takes the *other* axis — the denominator, not the
independence relation — which is resolvable by the admitted route and does not touch the stop condition.

*Attainable.* Five MCP calls. No HTTP, no download, no paywall, no cost.

## 3 · Step 1 — the index's own tallies re-derive (`checks/01`, exit 0)

Independently recomputed from EXPOSURE-INDEX's committed JSON
(sha256 `1e165294acc4715b992e5134a6eaa507a775edda179f666d97160d3c606184f8`):

| | expected | got |
|---|---|---|
| rows | 28 | **28** |
| `retrieval_completeness` unread / partial / complete | 18 / 7 / 3 | **18 / 7 / 3** |
| `overlap_unknown = true` | 24 | **24** |
| `n_emc_status = UNKNOWN` | 19 | **19** |

**Reproduces exactly.** The instruction's stop-and-report branch is not taken.

## 4 · Step 2 — resolution through the admitted route

Five `mcp__PubMed__*` calls, nine rows touched, every call preserved under `checks/`.
**No HTTP request, no publisher site, no paywall.** Routes B1/B2/B4/B8/B9 untouched; R1–R4 not restarted.

### 4.1 Resolved — 5 rows, each with a verbatim quote and locator

| row | n_emc | verbatim source of the number |
|---|---|---|
| `drilon2008` | **86** | *"Of the 86 evaluable patients, 57 were men and 29 were women…"* — PMC2779719, Results |
| `chiusole2020` | **59** | *"A total of 59 patients were identified, 37 were male (62.7%)…"* — PMC7308468, Results |
| `bishop2019` | **41** | *"We identified 41 consecutive patients with localized, non-metastatic histologically confirmed EMC…"* — PMC7771031, Methods |
| `masunaga2025` | **171** | *"…the remaining 171 patients were retrospectively analyzed."* — PMC12398172, Methods |
| `davis2017` | **6** | *"Six patients with EMC were enrolled on MI-ONCOSEQ."* — PMC5400622, Results |

`n_emc_status: UNKNOWN` **19 → 14**. `reported` **9 → 14**.

### 4.2 ⭐ A fourth headline-is-not-EMC-n instance — of a **different kind**

`drilon2008` prints **87** in its abstract (*"the clinical behavior and treatment responses of 87
patients with EMC … were examined"*) and **86** in its body, three separate times. The index's headline
87 is the curated repository value and tracks the abstract; the body's evaluable EMC n is 86.

⚠ **This is not the same shape as the three EXPOSURE-INDEX found.** Those (martinbroto 68→4, morioka
5→2, osullivanCoyne 55→3) are mixed-histology cohorts with an EMC subgroup. This is an **intra-paper
abstract-vs-body discrepancy in an EMC-only cohort**. The row says so in words so nobody reads it as
the mixed-histology shape. `headline_n_is_not_emc_n: True` count **3 → 4**, with the distinction recorded.

### 4.3 Still UNKNOWN — 14 rows, each with its reason. **This is a correct result, not a failure.**

| reason | rows | what was actually established |
|---|---|---|
| `identity_not_established_no_admitted_call_attributable` | **10** | The index and `emc-ipd-survival.json` carry **no PMID, PMCID, DOI, title, journal, author or year** for these rows — only an internal `source_id`. Every PubMed tool requires one of those as input. **No call was made** (`checks/07`). |
| `no_pmc_record_abstract_only` | 2 | `maki2005bortezomib`, `chow2007` — retrieved by `get_article_metadata`; abstract + MeSH returned, no body, no PMCID exists. |
| `tables_stripped_from_returned_body` | 2 | `boklan2025carfilzomib`, `remiszewski2025` — full text returned, tables not returned as cell content. |

**"Not in the abstract" was never treated as "not in the paper."** All four abstract-only and
table-stripped rows stay UNKNOWN and explicitly **not zero**.

### 4.4 ⭐ The dominant blocker is not a paywall — it is a missing identifier

**Ten of the fourteen surviving UNKNOWNs are blocked on an identifier this repository never recorded**,
not on PMC coverage and not on a publisher. `emc-ipd-survival.json`'s `candidate_sources` carry
`source_id`, `n`, `endpoint_hint`, `why_candidate`, reachability notes and `overlap_risk` — and no
citation of any kind. The only way into the admitted route would be to guess which published paper
`ussc2022` or `japan2003` denotes from its prose description and attribute a retrieved count to that
guess. **A count typed against an inferred identity is a count typed from memory. No such call was made.**

The cheap fix is not retrieval: record a PMID or DOI per `candidate_source`. This lane does not edit
that shared file and prepared no diff, because the change is a data-entry task for its owner, not a
correction this lane can supply from evidence it holds.

### 4.5 Refusals upheld, not overturned

* `chow2007` — EXPOSURE-INDEX recorded 0, its own verifier **refused it** (`checks/02`, exit 1), and it
  was corrected to UNKNOWN. This lane reached the same wall by direct retrieval and **did not step over
  it**. Upheld by test.
* `maki2005bortezomib` — the protected row. Abstract prints no enrolment total and no per-histology
  table; the only denominator is *"21 evaluable patients … on Arm B"*, and Arm B is defined as *"other
  types of soft tissue sarcomas"* — the stratum an EMC patient would fall into. Finest MeSH: `Sarcoma`.
  **UNKNOWN, never zero.** Upheld by test.
* `boklan2025carfilzomib` — measured on the returned body: `Table` = 0, `histolog` = 0, `myxoid` = 0,
  `chondro` = 0 occurrences. The accrual sentence's table reference resolves to an empty `()`. The
  portfolio's clearest unread-not-absent row, now **independently re-reached rather than inherited**.
* `higuchi2023zaltoprofen` remains the index's **only** zero, and still a measured one.

## 5 · Artifact

`emc-patient-exposure-index-v2.json` — 28 rows, EXPOSURE-INDEX's schema preserved. Every original field
of every row is carried through unchanged **except** on the five resolved rows, where the prior value is
recorded inside a new additive `resolution_2026_09_09` block. **Every one of the 19 formerly-UNKNOWN
rows carries that block**, including the ten with no call, which record why no call was possible.

**No `overlap_unknown` flag was changed on any row.** Resolving a denominator answers *who was counted
in one series*; it says nothing about whether two series counted the same patient.

## 6 · Validation — `checks/11`, exit **0**

`verify_resolved_index.py` reads only the emitted JSON, EXPOSURE-INDEX's source, and LOCOREGIONAL-2's
ledger. It enforces the inherited invariants (28 rows, three-valued completeness, `overlap_unknown` on
every row and still 24 true, every reported n names a source, no zero without a measured-zero
justification, no total-shaped key), this lane's own (every surviving UNKNOWN carries an admitted reason
code; every resolved row carries quote **and** locator; the four refusals upheld), and the control.

**The control reproduces from this index's rows:** bishop2019 33+8 = 41 patients / 1+4 = 5 events;
masunaga2025 24+110 = 134 / 2+14 = 16. **175 patients, 21 local recurrences — matches LOCOREGIONAL-2.** ✅

### ⭐ Two preserved failures, and what the second one caught

* `checks/09`, exit **1** — the verifier assumed the ledger stored flat `n`/`events`; it stores
  `arm_sizes`/`arm_events`. Field-name defect, fixed in `checks/10`.
* `checks/10`, exit **1** — **a real conflation in my own invariant.** I had asserted that both control
  rows carry `overlap_unknown: false`. They do not: `masunaga2025` is false, but **`bishop2019` carries
  `overlap_unknown: true`** (*"⚠ US institution, may overlap ussc2022"*). The sanctioned sum is therefore
  **not** licensed by the row-level flag. It is licensed by a **pairwise, contrast-scoped ruling** in a
  named source file, which in its own words applies *"FOR THIS CONTRAST"* only and states that bishop2019
  *"must still NEVER be summed into any total that also contains ussc2022, remiszewski2025, seer270_2022
  or uMich2023."* The verifier now tests that licence — including that all four named-forbidden rows are
  absent from the sum — instead of the flag. `checks/11`, exit 0.

  This matters beyond a fixed test: **a row-level `overlap_unknown: true` does not forbid every use of
  that row, and a pairwise licence does not clear the row's flag.** Conflating the two in either
  direction is how a stop condition gets quietly widened or quietly bypassed.

### The control's inputs are now primary-verified, not only curated

EXPOSURE-INDEX limitation 5 recorded that bishop2019's arm split was *"inherited transcription, NOT
re-verified against the paper in this lane."* It is now verified against the primary:

* *"The majority of patients (n=33, 80%) received combined modality local therapy with both surgery and
  RT, whereas 8 patients received surgery alone (20%)."* → 33 + 8
* *"There were 5 patients (12%) with local relapse… Four of those patients underwent surgery alone."*
  and *"…compared to the one patient who received CMT"* → 4 + 1

For masunaga2025 the 134 denominator, the 16 events and the 24-patient RT arm are verified
(*"the remaining 134 patients were included. Local recurrence occurred in 16 patients (11.9%)"*;
*"Of the 24 patients who received (neo)adjuvant radiotherapy…"*). **The 2/14 event split by arm was not
printed in the returned body and remains inherited from LOCOREGIONAL-2** — the row says so.

## 7 · Provenance

* **Route:** PubMed/PMC MCP tools only. Five calls: `get_full_text_article` ×4 (PMC2779719;
  PMC7308468 + PMC7771031; PMC12398172 + PMC12428389; PMC5400622 + PMC12504171) and
  `get_article_metadata` ×1 (PMID 15739208, 17545802). No HTTP, no download, no publisher site.
* Two calls returned payloads over the inline cap and were persisted by the harness; both retrievals
  **succeeded**, the persisted paths are recorded in `checks/04` and `checks/05`, and every quote was
  extracted verbatim from those files.
* Read-only inputs: EXPOSURE-INDEX's index (sha256 recorded), `research/modalities/emc-ipd-survival.json`,
  `../LOCOREGIONAL-2/rt-local-control-contrast-ledger-k2.json`, `../REPURPOSING-2/CITED-REFERENCE-SWEEP.md`,
  `../REPURPOSING-3/FIVE-REFERENCE-TABLE.md`, `../CARE-DELIVERY-3/`, `../SHARED-CONTRACT.md`.
* Nothing outside this lane was written. Nothing staged, committed or pushed; `scripts/preflight.sh` not
  run; no subagent spawned; the clinical registry not edited and no shared file modified.

## 8 · Limitations

1. **A resolved denominator is still one series' denominator.** It is not a portfolio count and cannot
   become one. See §9.
2. **`complete` still means narrative-plus-all-tables** and still excludes supplementary appendices and
   figure images. Only `chiusole2020` was upgraded to it; the other four resolved rows are `partial`
   because PMC returned their narrative but not their table cells.
3. **The ten identity-blocked rows are unknown to *this program*, not unknown to the literature.** Each
   is a real published paper a human can look up. The blocker is a missing field in a repository file.
4. **`remiszewski2025`'s four tables were not returned**, so "review with no original cohort" is what the
   returned text shows, not a demonstrated absence. Held to the same rule as `chow2007`.
5. **masunaga2025's 2/14 arm-event split remains inherited**, not primary-verified (§6).
6. `drilon2008`'s 87-vs-86 is recorded as a discrepancy in the source paper. This lane takes the body's
   86 as the EMC n and **does not adjudicate** which figure the paper's authors intended.
7. The index still cannot detect overlap it was not told about, and this lane resolved none.

## 9 · ⛔ Stop condition — inherited, absolute, and reached

**Stop at the index.** No pooling. No portfolio total. **No denominator arithmetic across any row
carrying `overlap_unknown`** — not as an aside, not as a range, not as an approximate upper bound.
24 of 28 rows carry it, and this lane changed none of them.

⚠ **Resolving five denominators makes the temptation worse and the answer no different.** There are now
**14 known EMC denominators sitting in one file**, and they still must not be added: the series overlap
in at least three named clusters (Milan; US institutional/SEER; Japanese registry/trial), and at least
two denominators are not EMC cohorts at all. Knowing *who was counted in each series* is not knowing
*whether two series counted the same person* — and only the second licenses a sum.

The only addition performed anywhere in this artifact is the two-row LOCOREGIONAL-2 control, under the
pairwise contrast-scoped licence dissected in §6. The file refuses total-shaped keys by test.

**The distinct-EMC-patient count on which this portfolio's cited evidence rests remains UNKNOWN**, and
this index now says why with one more level of precision than before: 24 rows whose independence is
unestablished, 14 whose EMC denominator is still unread — **ten of those for want of a citation, two for
want of a PMC record, two because PMC returned the paper without its tables.**

## 10 · Next credible independent step (not taken here)

Add a PMID or DOI to each `candidate_source` in `research/modalities/emc-ipd-survival.json`. That single
data-entry change would open ten of the fourteen surviving UNKNOWNs to the admitted route at zero cost.
It is the owner's edit to make; this lane neither made it nor prepared a diff, because the identifiers
are not evidence this lane holds.

## 11 · Files

* `emc-patient-exposure-index-v2.json` — the artifact.
* `build_resolved_index.py`, `verify_resolved_index.py`.
* `checks/01-rederive-index-tallies` (0) · `02` (0) · `03` (0) · `04` (0) · `05` (0) · `06` (0) ·
  `07-no-admitted-route-ten-unidentified-rows` (0, a preserved **non**-attempt) ·
  `08-build-resolved-index` (0) · `09-verify-resolved-index` (**1**, preserved) ·
  `10-verify-resolved-index-rerun` (**1**, preserved — the licence conflation) ·
  `11-verify-resolved-index-final` (0).
