---
id: DOC-ATLAS-SPECIMEN-PROVENANCE-20260906
title: Named EMC specimen chain remains unresolved after case-record recovery
kind: memo
status: live
purpose: Decide whether the named legacy EMC specimens establish independent atlas validation.
scope: Panagopoulos 2002, Mitelman 9736 cases 3/5/4/7, 2017 EMC cases 46–51, and their possible GSE24369 and GSE4303 relationships; no expression analysis.
audience: [maintainers, autonomous research agents]
date: 2026-09-06
last_verified: 2026-09-06
---

**C12 remains unresolved.** The new recovery adds individual Mitelman case records and, crucially, their field definitions. It does not recover primary recruitment documentation, an EMC1–EMC6 crosswalk, or evidence establishing patient separation from GSE4303. No independent validation cohort is certified, and reference compatibility (C3) is unchanged.

The [previously recovered primary Table S1](https://api.figshare.com/v2/articles/22466361) explicitly links its EMC cases 46, 47, 48 and 49 to Panagopoulos/Mitelman 9736 cases 3, 5, 4 and 7. The newly downloaded case records corroborate the linked age/sex fields. The linkage comes from the Published column, not demographic matching.

| 2017 case | Explicit 2002 case link | Primary S1 age/sex, site | New curated fields |
|---|---|---|---|
| 46 | 3 | 71/M, buttock | Sweden; tumor biopsy |
| 47 | 5 | 35/F, knee | Sweden; tumor biopsy |
| 48 | 4 | 40/M, groin | Sweden; tumor biopsy |
| 49 | 7 | 48/F, groin | Sweden; tumor biopsy; investigations 1 and 2 |
| 50 | No Published entry | 76/M, upper arm | No new case linkage |
| 51 | No Published entry | Unknown | No new case linkage |

The four case records are **secondary curated evidence**. Mitelman's own [Country definition](https://mitelmandatabase.isb-cgc.org/help) permits a corresponding-author-residence fallback when the publication does not state case origin. The saved records do not distinguish fallback from documented origin. Thus even their Sweden codes do **not** establish Swedish recruitment. The Tissue field concerns material used for cytogenetic investigation; it does not identify the later expression-array aliquot. “Unselected” is a classification about unusual karyotypes, not proof of consecutive clinical recruitment. Exact case records are saved as `mitelman-case3.html`, `mitelman-case5.html`, `mitelman-case4.html`, and `mitelman-case7*.html`.

Case 7 has two investigations in the database. Its [field definition](https://mitelmandatabase.isb-cgc.org/help) allows either consecutive investigations or a metastatic lesion at another location. The 2017 Published cell specifies Case 7 without an investigation number. Neither the lesion nor the relevant array aliquot can be selected from these records. These are not two patients, and no additional validation sample is created by the second record.

Comparison with the existing [GSE4303 author clinical table](https://tma.im/tma_portal/emc/figures/table1.htm) supplies no explicit STT-to-2017 or STT-to-2002 key. Different ages or sites cannot exclude later lesions or reporting differences, and similar attributes cannot establish identity. The inherited STT3696/table versus STT3714/GEO mismatch, STT2528(2) ambiguity, and unverified within-GSE4303 patient uniqueness remain. The six 2017 EMC controls reuse the published 2011 expression data; their order must not be assumed to equal EMC1–EMC6. Missing Published entries for cases 50–51 do not establish new specimens.

The previous retrieval log and web outputs were inspected before requests. Distinct routes covered the current Lund Research Portal linked by its prior record, OpenAlex article locations, Europe PMC full-text links, a targeted institutional-repository search, and the exact ResearchGate 2002 article record. They exposed metadata or abstract, not the Panagopoulos methods. A distinct ResearchGate route for the 2011 paper exposed a publisher preview of the first page, without recruitment methods. Existing failed publisher URLs were not retried. Searches were restricted to the named articles and dataset; incidental results were not followed. This access outcome does not establish that full text or a crosswalk is absent elsewhere.

The bounded named-source recovery stops here. Remaining evidence needs are primary recruitment/sample records for all six EMC controls, a reliable link from EMC1–EMC6 to cases 46–51 (including Case 7's lesion), and GSE4303 procurement/patient provenance sufficient to assess sharing. Country/lab labels cannot substitute. The evidence has not changed enough to justify another scientific experiment at this checkpoint; no expression analysis or automatic repeat recovery is selected.

`retrievals.json` preserves 13 exact HTTP response bodies with URLs, UTC request times, byte counts and SHA-256. `web-01.json` through `web-05.json` are serialized web-tool extractions, not publisher bytes; exact web retrieval instants were not instrumented. `input-manifest.json` pins eight inherited dependencies. `case-evidence.json` gives precise claim locators and unknowns. The read-only `check_sources.py` passed 44 source/link/definition checks; this is a worker verification, not independent scientific review. The coordinator owns the settled integration preflight; no commit or publication gate ran here. No downloads, computations, background jobs or nested workers remain running.
