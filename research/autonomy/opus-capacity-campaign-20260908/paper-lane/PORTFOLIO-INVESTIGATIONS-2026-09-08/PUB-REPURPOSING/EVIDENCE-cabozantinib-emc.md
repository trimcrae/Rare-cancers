---
id: DOC-PORTFOLIO-PUBREPURPOSING-CABOZANTINIB-EMC-EVIDENCE
title: "Per-agent EMC-scoped novelty check of the 14 repurposing candidates, and the cabozantinib falsification"
level: L4
kind: evidence-table
status: live
date: 2026-09-08
last_verified: 2026-09-08
---

# 1 · What was run

A per-agent, EMC-scoped literature check of every agent in Table 2 of
`research/manuscripts/repurposing/repurposing-hypotheses.md`, run **2026-09-08 23:59Z - 2026-09-09 00:05Z**
through the **PubMed MCP server** (a first-party tool route; no proxy HTTP egress, no denied source,
no B1/B2/B4 route touched). Four queries, each pairing the disease phrase with a block of candidate
agents, then metadata for every hit and one full text.

Source attribution: all records below are **from PubMed / PubMed Central**.

# 2 · Result table — 14 candidate rows against an EMC-scoped search

"Hits" counts records where the disease phrase and the agent/class term co-occur in indexed fields.

| Candidate row (Table 2) | EMC-scoped hits | Any record placing the agent *in EMC patients or EMC models*? | Manuscript's novelty cell | Verdict |
|---|---|---|---|---|
| Imatinib, *KIT*-mutant | (not re-queried; already graded "No, already reported") | yes, by the manuscript's own [7] | No, already reported | consistent |
| **VEGFR multikinase: regorafenib, cabozantinib, lenvatinib, nintedanib, sorafenib, axitinib, vandetanib, tivozanib** | **1** (PMID 34716194) | **YES — cabozantinib, 3 EMC patients in a phase II trial, 1 confirmed PR** | "these specific agents are untested extensions"; novelty **"Partly"** | ⛔ **FALSIFIED for cabozantinib**; unchallenged for the other seven |
| Zaltoprofen / pioglitazone (PPARγ) | 3 (36636023, 18855877, 15920699) | 36636023 is the mouse-model zaltoprofen result the manuscript already cites; the other two are expression studies | Yes | consistent — no *patient* report found |
| Carfilzomib (proteostasis) | 6 (40580361, 28360467, 24555529, 22743288, 19594492, 17545802) | none pairs a proteasome inhibitor with EMC treatment; hits are a new EMC cell line, a case report, two reviews, an IHC series and the Chow 2007 review | Untried in EMC; class not untried in sarcoma | consistent |
| Venetoclax (BCL-2) | same query as above | no EMC treatment record; the BCL-2 hit (19594492) is diagnostic IHC | Yes | consistent |
| HDAC inhibitors (romidepsin, panobinostat) | same query | none | Yes for EMC | consistent |
| Brigatinib | same query | none | Yes | consistent |
| CDK4/6 (palbociclib) | 3 (shared PPARγ query) | none pairs a CDK4/6 inhibitor with EMC | Yes | consistent |
| NTRK inhibitors (larotrectinib, entrectinib) | 3 (37477762, 34340159, 32860002) | all three are pan-TRK **immunohistochemistry / diagnostic** papers; none gives an NTRK inhibitor to an EMC patient | Yes | consistent |
| *NR4A3*-directed modulation | same query | none | Yes | consistent |
| BET / CDK7-9 | same query | none | Yes | consistent |
| mRNA vaccine + checkpoint inhibitor | same query | none | Yes | consistent |

**One of fourteen rows is falsified. Thirteen survive this check.** Survival here means only that
nothing is *indexed* on the pairing — an absence in a title/abstract-scoped search is not proof that
no such work exists, exactly as §6 of the manuscript already says.

# 3 · The falsification, at full text

O'Sullivan Coyne G, Kummar S, Hu J, Ganjoo K, Chow WA, Do KT, et al. *Clinical Activity of
Single-Agent Cabozantinib (XL184), a Multi-receptor Tyrosine Kinase Inhibitor, in Patients with
Refractory Soft-Tissue Sarcomas.* Clin Cancer Res 2022. PMID 34716194, PMC8776602,
[DOI](https://doi.org/10.1158/1078-0432.CCR-21-2480).

**This paper is already reference [19] of the repurposing manuscript.** No new source is required to
make the correction; the source was cited but its EMC content was not read into the claim.

Verbatim, from the PMC full text:

- Table 1, Diagnosis: *"Extraskeletal myxoid chondrosarcoma  3"* (of 54 evaluable, 55 enrolled).
- Results: *"Confirmed partial responses to cabozantinib were seen in 6 patients: 2 patients with
  ASPS, 2 patients with undifferentiated pleomorphic sarcoma (UPS), 1 patient with extraskeletal
  myxoid chondrosarcoma (EMC), and 1 patient with uterine leiomyosarcoma"*.
- Results: *"Patient 1010003, with an EMC … He experienced a PR after 10 cycles of therapy and
  remains on study after 99 cycles"*.
- Discussion: *"The longest response in this trial (now over 99 cycles) was observed in a patient
  with EMC."*
- Trial design: single-arm, two-stage, open-label phase II, all WHO-recognised STS subtypes, 60 mg
  daily, RECIST 1.1, multi-site. *"Neither of the primary efficacy criteria (22% ORR or 54% 6-month
  PFS) were reached."*
- Safety is reported for the whole cohort only: Table 3 caption, *"(= 54 total patients)"*.

## What this does and does not establish

- **It does** establish that cabozantinib has been given to EMC patients inside a prospective,
  multi-site clinical trial, and that the trial reports a confirmed partial response in an EMC
  patient. So cabozantinib is **not** an untested extension in EMC and is **not** a novel hypothesis.
- ⛔ **It does not** establish efficacy, safety, selectivity or clinical readiness of cabozantinib in
  EMC. Three patients in a mixed-histology trial that missed both primary endpoints is a subgroup
  observation, not an efficacy result, and this repository makes no treatment recommendation.
- ⛔ It is **not** used here to change any tier, the tier scale, the firewall admission rule, or the
  clinical registry. Its interaction with the T3 definition is flagged in FINDING.md as an input for
  the coordinator, not adjudicated.

# 4 · A second, adjacent record found on the way, NOT a falsification

PMID 32547189 (apatinib in chondrosarcoma, PMC7237692, recorded by the sibling W07c lane) reports
*"3/33 (9.1%) extraskeletal myxoid CS"* with *"one PR and two SD"* and a median duration of response
of 21.2 months. **Apatinib is not one of the manuscript's 14 candidates**, so no claim of this paper
is falsified by it. It is recorded because it is a second anti-angiogenic agent with EMC patient-level
data and it bears on the class framing of Tranche 2.
