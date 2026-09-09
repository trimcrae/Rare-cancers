---
id: DOC-PORTFOLIO-REPURPOSING2-CITED-REFERENCE-SWEEP
title: "Sweep of the repurposing manuscript's own cited references for unread EMC patient-level facts"
level: L4
kind: evidence-table
status: live
date: 2026-09-09
last_verified: 2026-09-09
---

# Cited-reference sweep — the same class of miss, elsewhere

**Attribution.** Every cited fact below was retrieved **according to PubMed / PubMed Central**, via
the PubMed MCP server, on **2026-09-09 00:05–00:13 UTC**. ⛔ No direct HTTP fetch was attempted;
clinicaltrials.gov, GEO, IEDB and api.github.com are proxy-refused in this environment and were not
touched. Raw calls and results are in `checks/`.

## 1 · What was swept, and why these references

The cabozantinib miss had a specific shape: **a patient-level EMC fact sitting inside a paper the
manuscript already cites, while the manuscript's prose describes that paper only at class or
unselected-sarcoma level.** The sweep targeted every cited reference that could carry that shape —
each reference that reports on EMC patients, or on a trial or cohort that could have contained them.

| Ref | Article | PMC full text retrieved? | Swept for |
|---|---|---|---|
| [1] | Remiszewski 2025, comprehensive EMC review | **yes**, PMC12504171 | agent-level EMC patient facts; support for the sunitinib attribution |
| [4] | Masunaga 2025, RT and chemo in EMC, 171 patients | **yes**, PMC12398172 | per-agent exposures in an EMC registry cohort |
| [5] | Davis 2017, NGS of EMC | **yes**, PMC5400622 | treatment histories of the sequenced EMC patients |
| [6] | Urbini 2018, actionable *KIT* mutation in EMC | **yes**, PMC6073125 | what the index patient actually received |
| [13] | Bangerter 2023, two ex-vivo EMC models | **yes**, PMC9813045 | donor patients' systemic treatment |
| [21] | Maki 2005, bortezomib phase II in sarcoma | **no — no PMCID exists** | whether an EMC patient was enrolled |
| [22] | Boklan 2025, carfilzomib phase I | **yes**, PMC12428389 | whether an EMC patient was enrolled |
| [19] | O'Sullivan Coyne 2022, cabozantinib phase II | (read by PUB-REPURPOSING, 2026-09-08) | the known hit; not re-fetched |

Not swept, with reason: [3], [10], [11], [15], [16], [17], [18], [20] carry no EMC patient cohort
([17] is a melanoma trial, [10]/[20] are databases); [2], [8], [9], [12], [14] have no PMC full text
reachable by this route or are pathology/preclinical series — **their sweep is unfinished, not clear**.

## 2 · Hits

⛔ **Every row is a statement about what has been GIVEN to patients and about novelty. No row is an
efficacy, safety or therapeutic-window claim, and none may be read as one.**

### H1 — pioglitazone has already been given to an EMC patient. ⭐ CHANGES A CLAIM.

| | |
|---|---|
| **Cited reference** | **[5]** Davis EJ, et al. *Next generation sequencing of extraskeletal myxoid chondrosarcoma.* Oncotarget 2017. PMC5400622, PMID 28423517. [DOI](https://doi.org/10.18632/oncotarget.15568) |
| **How the manuscript's prose uses it** | §1.1, line 163: *"Clinical next-generation sequencing of advanced EMC characteristically reveals no recurrent, directly actionable driver mutation beyond the defining fusion [5]."* — a **genomic** statement only. [5] is cited nowhere for treatment. |
| **The cited fact, verbatim** | *"In our EMC cohort, one patient with diabetes mellitus was treated with an antidiabetic agent, pioglitazone, a thiazolidinedione that is a potent and selective agonist for PPAR-gamma. The patient had stable metastatic EMC for 13 months before unequivocal progression. The contribution of pioglitazone to disease control is unknown."* |
| **The claim it falsifies** | Table 1 (line 323) places the PPARγ row in **"In vivo, animal EMC model / Novel (untried)"**; Table 2 (line 339) grades *"Zaltoprofen, and by extension pioglitazone (PPARγ, lineage)"* novelty **"Yes"**; Table 3 (line 366) calls the pioglitazone route **"untried"**. Pioglitazone is not untried in EMC. It has been taken by an EMC patient, and the manuscript's own reference [5] says so. |
| **What it does NOT establish** | ⛔ Nothing about whether pioglitazone works. n=1, given incidentally for diabetes, no response assessment, contribution explicitly unknown to the reporting authors, and the patient progressed. It narrows **novelty**, not evidence. |
| **Same shape as the cabozantinib miss?** | **Yes, exactly.** Patient-level EMC drug exposure, inside an already-cited paper, while the prose cites that paper only for a non-treatment fact. |

### H2 — the [6] *KIT* patient never received imatinib, and did receive sunitinib. ⭐ CHANGES A CLAIM.

| | |
|---|---|
| **Cited reference** | **[6]** Urbini M, et al. *Identification of an actionable mutation of KIT in a case of extraskeletal myxoid chondrosarcoma.* Int J Mol Sci 2018. PMC6073125, PMID 29937513. [DOI](https://doi.org/10.3390/ijms19071855) |
| **How the manuscript's prose uses it** | §1.1, line 163: *"An **imatinib-sensitive** activating *KIT* mutation is rare, reported in **1 of 20 EMCs** in one series [6]…"* — a **prevalence** statement, with an inherited sensitivity adjective. |
| **The cited fact, verbatim** | *"The EMC patient with a [KIT] exon 11 mutation described here **never received imatinib**. Thus, the therapeutic role of this agent in this case is still to be defined. Interestingly the same patient had been **treated with sunitinib with a prolonged response**."* And: *"…cannot explain the EMC sensitivity to sunitinib, although it is an actionable mutation in the individual case in which it has been identified."* |
| **The claim it changes** | The adjective *"imatinib-sensitive"* is not supported for this case by the source it cites. [6] says the opposite is unknown: the patient was never given imatinib. Sensitivity is inferred from the mutation class (its behaviour in GIST), which the manuscript should say. Separately, an EMC patient-level **sunitinib** exposure with a prolonged response sits in this reference and is not reflected anywhere in the manuscript's evidence tables. |
| **What it does NOT establish** | ⛔ It does not show imatinib fails, and it does not weaken the *KIT*-mutant hypothesis. It shows the manuscript characterises a cited case more strongly than its source does. |

### H3 — the sunitinib attribution points at a reference that does not appear to carry it. ⚠ CHANGES A CITATION, NOT A CONCLUSION.

| | |
|---|---|
| **Citing sentence** | Table 2, line 338: *"Clinical at class level: pazopanib and **sunitinib** are the active class in EMC **[1]**; these specific agents are untested extensions"* |
| **What was found** | The retrieved PMC full text and abstract of **[1]** (Remiszewski 2025, PMC12504171) contain **zero** occurrences of "sunitinib". ⚠ **Caveat, load-bearing:** that extraction demonstrably drops table contents and italic-marked gene tokens (it renders *"Table**provides a summary of relevant clinical trials related to EMC"* with the table absent). Sunitinib may well sit in that dropped clinical-trials table. **This is a flag, not a refutation.** |
| **Where the claim IS supported inside the same reference list** | **[4]**: *"The first data came from a retrospective study of sunitinib, which reported six (60%) partial responses and a median progression-free survival of 8.5 months in 10 NR4A3-positive EMCs"*. **[5]**: *"Of 10 patients treated, 8 patients who showed clinical benefit (6 partial responses, 2 stable disease > 3-6+ months) harbored the [EWSR1-NR4A3] translocation"*. **[6]**: *"we reported the therapeutic activity of sunitinib in a cohort of 10 EMC patients with 6 partial responses, 2 stable disease, and 2 showed progression."* |
| **Verdict** | The sunitinib claim is **true and supported three times over inside the manuscript's own reference list** — but probably not by the reference it points at. A citation fix, not a science fix. **No diff is proposed here**, because settling it requires reading [1]'s trial table, which this route cannot return. |

### H4 — reference [22] is now read at full text; a stated "unread" is partly resolved. ⭐ CHANGES A CLAIM.

| | |
|---|---|
| **Citing sentences** | §4.1, lines 498–500: *"Both are read here at **abstract level only**: no full text was retrieved for either…"*; lines 513–515: *"whether either trial enrolled an EMC patient remains **unread**"*. |
| **What was found** | **[22]** (Boklan 2025, PMC12428389, [DOI](https://doi.org/10.3390/cancers17172924)) full text retrieved. *"A total of 42 patients were screened, and 38 were treated (stratum A, 14; stratum B, 24)"*; *"Of the twenty-four patients enrolled in stratum B, fifteen (63%) had a diagnosis of sarcoma"*; *"Eleven patients in stratum B (48%) had OS"*; one synovial sarcoma; responses in germ cell tumour, NHL, hepatoblastoma; SD in rhabdomyosarcoma, teratoma and two osteosarcomas. **No occurrence of "extraskeletal", "myxoid", "chondrosarcoma" or "EMC" anywhere in the retrieved text.** ⚠ The per-histology enrolment table is not carried in the retrievable full text, so this is a reading of the narrative, not of the diagnosis table. |
| **Effect** | The manuscript's "abstract level only / unread" statement is now **stale for [22]** and must be narrowed to [21]. The substantive conclusion is unchanged and slightly strengthened: no EMC-specific result, and no EMC patient named. |

### H5 — reference [21] genuinely cannot be read by this route. ✅ NO CHANGE; the manuscript is right.

**[21]** Maki 2005 (PMID 15739208, [DOI](https://doi.org/10.1002/cncr.20968)) has **no PMCID**. Its
MeSH indexing goes no finer than "Sarcoma" / "Soft Tissue Neoplasms". Whether it enrolled an EMC
patient stays unread, and the manuscript's statement to that effect is accurate and should be kept.

### H6 — pazopanib denominator: 22 vs 23. ⚠ MINOR, ATTRIBUTION ONLY.

The manuscript (§1.1) reports *"4 of 22 evaluable patients"* and attributes the figures to *"the 2025
comprehensive review"* = **[1]**. **[1]** says *"26 patients, 23 of whom met modified intention-to-treat
criteria… Four patients (18% …)"*. **[4]** says *"four of the 22 evaluable patients had a partial
response"*. So the manuscript's **22** is supported inside its reference list — by **[4]**, not by the
reference it names. A pointer fix at most; no number in the manuscript is wrong.

## 3 · Adjacent EMC patient-level records found, which falsify nothing

Recorded so a later lane does not have to re-find them. ⛔ None is a candidate agent; ⛔ none supports
any efficacy claim.

| Record | Source | Why it is not a hit |
|---|---|---|
| Interferon-alpha-2b, one metastatic EMC patient, durable response with disease control 16 months | [1], citing Rubinger et al. | Interferon is not among the 14 candidates |
| 4 EMC patients received pazopanib, 2 trabectedin, 1 eribulin, plus anthracycline regimens, in a 171-patient national registry | [4] | pazopanib/trabectedin are already the established comparators, not candidates |
| Trabectedin: stable disease >1 year in metastatic EMC in a randomised phase III of translocation-associated sarcoma | [4] | not a candidate |
| Sunitinib retrospective series, 10 EMC patients, 6 PR / 2 SD / 2 PD, the 2 progressors carrying the variant fusion | [4], [5], [6] | sunitinib is named as the established active class, not as a candidate |
| Donors of both ex-vivo EMC models received surgery, radiotherapy and cryoablation only — no systemic candidate agent | [13] | confirms the models are treatment-naive for the candidate agents |
| The two best-performing targeted agents in the very screen the carfilzomib candidate rests on are **PU-H71 (HSP90)** and **HDM201 (MDM2/MDM4)** | [13] | not a patient-level fact, so out of this sweep's scope — but neither agent appears anywhere in the 14-candidate menu, which is a **candidate-generation** question worth its own bounded check |

## 4 · The routing lesson, stated concretely

Two of the four claim-changing hits (H1, H2) came from references the manuscript cites **for a
non-treatment fact** — a genomics statement and a prevalence fraction. The cabozantinib miss came
from a reference cited for a **class-level** fact. In all three cases the manuscript's prose reads a
cited paper at one level of description and never asks what else that paper says about EMC patients.

That is a mechanical, checkable gap, and it is not fixed by another literature search: **the papers
were already in the reference list.** The durable fix is the index PUB-REPURPOSING already proposed —
a cross-paper table of *EMC patient-level agent exposures*, one row per (agent, source, n, what the
source actually says) — populated by reading each cited EMC paper once for that one question. This
sweep is the first eight rows of it.
