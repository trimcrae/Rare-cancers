---
id: DOC-CSPG4-PRIMARY-TISSUE-EVIDENCE-2026-09-06
title: CSPG4 primary tissue evidence and bounded subtype-table recovery
kind: memo
status: live
purpose: Record verified primary cohort scope and the exact unresolved EMC tissue-evidence gap.
scope: CSPG4/NG2/HMW-MAA protein or spatial RNA evidence in EMC; recovery of two named primary subtype tables.
audience: [maintainers, autonomous research agents]
date: 2026-09-06
last_verified: 2026-09-06
---

No primary EMC-specific CSPG4 protein or spatial/cell-specific RNA measurement was verified in the bounded search. Both requested subtype tables remain uninspected after the recovery below. This is an unresolved gap, not evidence that no EMC measurement exists.

The saved `evidence.json` contains six primary-source findings, exact short excerpts independently confirmed against the saved sources, inspection boundaries and hashes. `access-log.json` records every durable recovery request, UTC time, final URL, HTTP status, bytes and SHA-256; `.response` files are original response bodies. HTTP 200 alone is not successful source recovery.

## Inspected cohort scope

- [Leuci 2020](https://pmc.ncbi.nlm.nih.gov/articles/PMC7710537/): disclosed RNA cohort has 251 TCGA samples: LMS 99, DDLPS 58, UPS/MFH/high-grade spindle-cell 50, MFS 25, MPNST 9, synovial 10. Measured flow-cytometry cohort has patient-derived UPS 3, GIST 5, liposarcoma 4, LMS 2, MPNST 1, plus HT1080 fibrosarcoma. No EMC in either disclosed cohort. The RNA specimens are not a 251-case protein cohort.
- [Cattaruzza 2013](https://pmc.ncbi.nlm.nih.gov/articles/PMC3656611/): main Results and Figure 1 identify MFH-like pleomorphic sarcoma, LMS, liposarcoma variants, fibrosarcoma and synovial sarcoma. These are the inspected named categories, not independently verified exhaustive Table S1 counts. Immunolabeling localizes NG2 to neoplastic cells and neovascular pericytes; Figure 2 also identifies pericyte staining in NG2-negative tumor-cell xenografts. This supports possible perivascular contributions in other sarcomas, but establishes neither malignant nor stromal origin of the EMC bulk signal. It does not support labeling all sarcoma CSPG4 stromal contamination.
- [Boudin 2022](https://pmc.ncbi.nlm.nih.gov/articles/PMC9552405/): 1,378 pooled bulk-RNA samples; Table 1 groups 177 as other. Separate RNA/protein correlation uses 343 cancer cell lines, four sarcoma lines. Neither establishes EMC tissue protein; other-category subtype completeness is unverified.
- [Geldres 2014](https://pmc.ncbi.nlm.nih.gov/articles/PMC3944408/): inspected Results distinguish sarcoma expression-database findings from IHC in other tumor classes. No verified EMC protein measurement.
- [Nota 2022](https://pmc.ncbi.nlm.nih.gov/articles/PMC9468862/): primary patient-selection paragraph defines 76 cases, comprising 52 conventional and 24 dedifferentiated bone chondrosarcomas. These are not EMC. Do not replace selected-cohort counts with different evaluable-staining denominators or a review's summary.
- [Benassi 2009](https://pubmed.ncbi.nlm.nih.gov/18634019/): abstract inspected, also recovered in Europe PMC core JSON. High-grade STS RNA and nonuniform in situ protein are described; the primary subtype table was not recovered. Review-derived subtype counts were not promoted to primary verification.

## Exact source recovery and stop

Cattaruzza's saved primary HTML contains the PMC supplement PDF/index links and the Oxford supplementary landing link. Direct PDF and index requests each returned 200 but 1,817-byte HTML download proof-of-work pages, not the supplement. No challenge was solved or bypassed. The observed Oxford supplementary link returned 403 (93 bytes). Europe PMC's supplementaryFiles API returned 200 XML (164 bytes) explicitly reporting that PMC3656611 is not open access; it supplied no asset. NCBI OA endpoint attempts returned 404, also supplying no asset. The actual Table S1 remains uninspected; no complete cohort count or EMC absence is inferred.

Benassi's Wiley landing page returned 403 (5,519 bytes). OpenAlex metadata listed only the DOI and PubMed locations, both non-OA with null PDF URL; this is discovery metadata, not an independent exhaustive repository census. Europe PMC core metadata identifies a subscription-required DOI route. Crossref exposed two publisher links: the PDF route returned 403 (5,531 bytes), and the TDM route returned 400 with an empty body. No credentials, payment or author contact was used. Targeted exact-title/DOI repository search yielded no usable primary copy. The primary subtype table remains uninspected.

These specific alternatives satisfy the bounded recovery stop. Uninspected tables are not negative expression results. The narrow remaining documentary action is authorized access to those exact tables; the scientific measurement gap is independent diagnosis-confirmed EMC tissue with separate malignant-cell membrane and perivascular scoring.

## Contribution and execution

The coordinator independently verified that the original GSE28866 CSPG4 peak46886 coding NM_001897 row already had the MLS_EMC_ annotation. This memo does not recompute that observation. No first discovery of EMC-linked CSPG4 RNA is claimed. Existing evidence can inform tissue-validation design and qualify sample/normal-stratum interpretation; it does not establish a tumor-cell target, therapeutic window, efficacy, or paper readiness.

Base revision: 7305b159b97d3345f6d2e3fb2fa718b0b2d35ec1. Worker: /root/cspg4_evidence, assigned medium effort; independent runtime model identifier unavailable. Actual runtime permits full filesystem access with approval policy never. Writes remained in the reserved evidence directory. Validation checked JSON parseability, all saved-response SHA-256 values, and exact short excerpts against saved primary bodies. No expression analyses, scientific tests, commits, preflight, nested agents, shared queue changes, outreach or paid services. No process remains running.
