---
id: DOC-PORTFOLIO-REPURPOSING3-FIVE-REFERENCE-TABLE
title: "REPURPOSING-3 — the five unread cited references, read for what they contain"
level: L4
kind: evidence
status: live
date: 2026-09-09
last_verified: 2026-09-09
---

# The five unread cited references, per reference

Manuscript: `research/manuscripts/repurposing/repurposing-hypotheses.md`, committed at
`b729216089989343bc8eb5d538bb815ab9e413a0`, unmodified by this lane.
Source: PubMed and PubMed Central, via the PubMed MCP server, 2026-09-09 (checks `01`–`06`).
According to PubMed. DOI links are given per row.

## 1 · Retrieval completeness — established first, because every absence claim below is bounded by it

Two independent retrieval modes were run before any reading, so that "not found" could be
distinguished from "not looked at":

* `convert_article_ids` on all five PMIDs (check `01`) — a `pmcid` field came back for **one**.
* `find_related_articles link_type="pubmed_pmc"` on all five PMIDs (check `04`) — the PMC link
  database returned **one** link, `10054153`, across all five inputs.

The two modes agree. **References [2], [8], [9] and [14] have no PubMed Central record at all.**
This is a stronger limitation than the one the two prior lanes recorded: it is not that the
extraction drops table contents, it is that **no body text of any kind is retrievable** for those
four — no Methods, no Results, no Discussion, no tables, no figures, no supplementary material.
For **[12]** a PMC record exists (`PMC10054153`) and returns an **empty `full_text` string**, twice,
under both the `PMC`-prefixed and the bare-numeric id form (checks `02`, `03`).

**Consequence, stated once and applying to every row below.** Everything read here is the PubMed
abstract, plus keywords, MeSH terms and article types. Any EMC patient-level fact that lives in a
table, a figure, a case listing or a supplementary file of these five papers **would not have been
seen**. That is exactly how reference [19]'s three EMC patients hid, and it is unresolved here by
the permitted route. No absence claim below is wider than "not in the abstract".

## 2 · Per reference

| Ref | Article | Sections actually read | Retrieval completeness | EMC patient-level content found (enrolment / treatment / response / outcome) | What is NOT reported in what was read | Changes a manuscript claim? |
|---|---|---|---|---|---|---|
| **[2]** | Huang SC et al., *Mod Pathol* 2023;36(7):100161. PMID 36948401. [DOI](https://doi.org/10.1016/j.modpat.2023.100161) | Title; **abstract in full**; keywords; MeSH; article types | **Abstract only.** No PMC record by either mode. Body, all tables, all figures **unread**. | **Enrolment:** *"fluorescence in situ hybridization was performed to confirm 58 EMCs, with 48 available for pan-Trk immunostaining and KIT sequencing."* **Treatment + outcome:** *"Size >10 cm, moderate-to-severe nuclear pleomorphism, metastasis at presentation, TAF15::NR4A3 fusion, and **the administration of chemotherapy** portended shorter univariate disease-specific survival, whereas only size >10 cm (P = .004) and metastasis at presentation (P = .032) remained prognostically independent."* Also: *"Moderate-to-strong immunoreactivities of pan-Trk, CD117, and INSM1 were present in 35.4%, 52.6%, and 54.6% of EMCs"*; *"KIT p. E554K mutation was detected in 2/48 cases"*; *"RES showed upregulation of NTRK2/3, KIT, and INSM1"*; *"pathogenic KIT mutation rarely occurred."* | Which regimens; how many of the 58 received systemic therapy; any response assessment; **any statement that KIT p.E554K is imatinib-sensitive** — the word imatinib does not appear. No targeted agent named. | **YES**, two ways — see §3, E1 and E2. Also **independently corroborates** REPURPOSING-2's H2. |
| **[8]** | Giner F et al., *Virchows Arch* 2023;482(2):407-417. PMID 36376703. [DOI](https://doi.org/10.1007/s00428-022-03453-x) | Title; **abstract in full**; keywords; MeSH; article types | **Abstract only.** No PMC record by either mode. The per-case clinicopathological table — the place treatment given would be recorded in a 31-case series with follow-up — is **unread**. | **Enrolment:** *"We studied 31 cases confirmed as EMC. Clinical and follow-up data were recorded."* **Treatment:** exactly one modality is named — surgery, via *"Positive surgical margins together with atypical histology and expression of p53 and Ki67 correlated with worse clinical prognosis."* **Marker denominators:** *"IHC positivity (focal or diffuse) was present for CDK4 (100%), STAT-6 (90%), CD117 (84%), HNK-1 (81%), SATB2 (68%), and S-100 (58%)."* | **No systemic agent, no drug name, no chemotherapy, no radiotherapy, no response assessment anywhere in the abstract.** MeSH carries no drug term; "Margins of Excision" is the only treatment term. ⚠ This is an absence **in the abstract of a paper whose per-patient table was not retrievable**, not a demonstrated absence of systemic treatment in the cohort. | **YES**, on a precision point — see §3, E2/E3. Not on treatment. |
| **[9]** | Chow WA, *Curr Opin Oncol* 2007;19(4):371-6. PMID 17545802. [DOI](https://doi.org/10.1097/CCO.0b013e32812143d9) | Title; **abstract in full**; MeSH; article types (Review) | **Abstract only.** No PMC record by either mode. | The **only** EMC-specific sentence in the abstract is molecular: *"extraskeletal myxoid chondrosarcoma is a unique entity defined by the presence of a fusion gene between the orphan nuclear receptor, CHN/NOR1, and a promiscuous partner, most commonly EWSR1."* Parent-histology treatment content: *"Translational research has validated platelet-derived growth factor receptor, estrogen signaling, matrix metalloproteinase-1, histone deacetylase, methylthioadenosine phosphorylase, and vascular endothelial growth factor-A as potential therapeutic targets"*; *"Bisphosphonates may also possess important antitumoral effects"*; *"the benefit of chemotherapy for dedifferentiated chondrosarcomas remains questionable."* | **No EMC patient, no EMC treatment, no EMC outcome** in the abstract. As a 2007 narrative review its body would carry no primary EMC patient data of its own in any case. | **NO.** The manuscript's six-target list at §1.2 matches the source's validated-target sentence **exactly**, all six. Bisphosphonates are flagged in §4 as a no-diff observation. |
| **[12]** | Higuchi T et al., *Cell Cycle* 2023;22(8):939-950. PMID 36636023, **PMC10054153**. [DOI](https://doi.org/10.1080/15384101.2023.2166195) | Title; **abstract in full**; the returned `full_text` field, which was the **empty string** | **Abstract only, despite a PMC record existing.** `full_text: ""` reproducibly, in two id forms. Methods, results, the animal-model section and every table **unread**. | **No human patient of any kind.** Preclinical throughout. In vitro: *"human extraskeletal chondrosarcoma **H-EMC-SS** cells"* — the line is named. In vivo: *"Zaltoprofen treatment inhibited tumor growth, induced tumor cell apoptosis, and was well tolerated in **a mouse model of extraskeletal myxoid chondrosarcoma**"* — **no line is named for the animal work.** | Which line the mouse model used; any dose, any n, any tumour measurement; the trailing gene names in *"PPARγ-activating factors, such as,, and,"* — the extractor dropped them, visibly. | **YES**, but only on the recorded *reason* the paper is unread — see §3, E4/E5. The manuscript's substantive statement (mouse-model line **unknown**, not stated in either direction) is **confirmed correct** and stays. |
| **[14]** | Iwata S et al., *Hum Cell* 2025;38(4):122. PMID 40580361. [DOI](https://doi.org/10.1007/s13577-025-01250-7) | Title; **abstract in full**; keywords; MeSH; article types | **Abstract only.** No PMC record by either mode. All IC50 values, the drug roster and the donor patient's clinical record are in tables/figures and are **unread**. | **One EMC patient, as a tissue donor:** *"We successfully developed the NCC-EMC1-C1 cell line using surgically resected tumor tissue from a patient with EMC."* No age, sex, site, stage, prior treatment or outcome for that patient. Screen result verbatim: *"High-throughput screening of 221 anticancer drugs using NCC-EMC1-C1 identified three candidates, **brigatinib, panobinostat, and romidepsin**, that demonstrated low IC values."* | Any treatment given to the donor patient; any response; any IC50 number; the other 218 compounds. | **NO.** The manuscript's §3.1 Table 2 and §4 tranche rows already carry all three agents and attribute them to a 221-drug screen in a patient-derived EMC line [14]. Read against the abstract, **that is accurate.** |

## 3 · Adjacent record found by reading [12] for what it contains

**Not one of the five, and not cited by the manuscript.** [12] is preclinical, so the question
"has zaltoprofen ever been given to a human with this tumour" is unanswerable from [12] itself.
PubMed holds exactly **two** records for zaltoprofen in chondrosarcoma or sarcoma (check `06`); the
other is by the same Kanazawa group:

> Higuchi T, Takeuchi A, Munesue S, Yamamoto N, Hayashi K, Kimura H, et al. *Cancer Med.*
> 2018;7(5):1944-1954. PMID 29573200, PMC5943440.
> [DOI](https://doi.org/10.1002/cam4.1438) — article type **Case Reports**.
> *"Moreover, we showed a case of a patient with cervical chondrosarcoma (grade 2), who was treated
> with zaltoprofen and has been free from disease progression for more than 2 years.
> Histopathological findings revealed enhanced expression of PPARγ and reduced expression of MMP2
> after administration of zaltoprofen."*

⛔ **Scope, stated exactly.** That patient had a **grade 2 cervical chondrosarcoma**. **This is not
an EMC patient.** It does **not** falsify "untried in EMC". It bounds the claim at
**parent-histology** level only — the same bound the manuscript already applies to itself for the
proteasome class ("untried in EMC; the class is not untried in sarcoma") and, via [9], for histone
deacetylase. **No efficacy, safety, selectivity or therapeutic-window conclusion is drawn from an
uncontrolled n=1 report, in either histology.** Its in-vitro lines were SW1353 and OUMS27, both
conventional chondrosarcoma, not EMC.
