---
id: DOC-CSPG4-BROWSER-SOURCE-20260906
title: Normal-browser checkpoint stops at challenge and publisher access denial
kind: memo
status: live
purpose: Preserve the actual result of the single authorized normal-browser attempt at two named primary subtype tables.
scope: Cattaruzza2013 Table S1 and Benassi2009 subtype table; browser access observations only.
audience: [maintainers, autonomous research agents]
date: 2026-09-06
last_verified: 2026-09-06
---

Neither subtype table was recovered or inspected. Normal browser navigation rendered the Cattaruzza main article and the Benassi abstract landing page, but the observed supplement/PDF links ended at an actual reCAPTCHA challenge and a login/purchase access denial respectively. This closes the named browser checkpoint without resolving EMC inclusion or EMC-specific CSPG4 protein evidence. Inaccessible tables are not negative expression results.

The Cattaruzza route began at https://pmc.ncbi.nlm.nih.gov/articles/PMC3656611/ in a new hidden Codex in-app browser tab. The main article rendered, including the existing Results/Figure 1/2 caption evidence and the observed `supp_mjt010_mjt010supp.pdf` link. Clicking that link once navigated to https://pmc.ncbi.nlm.nih.gov/articles/instance/3656611/bin/supp_mjt010_mjt010supp.pdf and displayed `Checking your browser - reCAPTCHA`. The route stopped and its tab was closed. No index or Oxford alternative was attempted after this challenge.

The Benassi route began at the previously saved https://onlinelibrary.wiley.com/doi/10.1002/jor.20694. The abstract and an observed Download PDF link rendered. Clicking that link once navigated to https://onlinelibrary.wiley.com/doi/pdf/10.1002/jor.20694. The page displayed an access-denial panel offering institutional/personal login and purchase options. That route stopped, its access panel text was retained, and its tab was closed. No access option was selected.

`browser-extracts.json` retains exact text excerpts from the returned browser observations, with URLs, UTC times and precision limits. These are transparent tool-output transcriptions, not original publisher bytes, a full AX snapshot or a screenshot. A supported `content.export()` call on the accessible main article failed with `Codex in-app browser does not support command "tab_content_export"`; no artifact was produced by that call. Browser download was not attempted after either access barrier. The existing saved main-article source remains the provenance for earlier scientific findings; this checkpoint adds access evidence only. `manifest.json` records hashes of the retained artifacts and prerequisite files.

Diagnosis-confirmed EMC inclusion, denominator, specimen independence, subtype-specific malignant-cell membrane/perivascular protein scoring, normal/control comparator and associated specimen provenance remain unresolved in the exact requested tables. Main-article statements concerning other named STS categories are not EMC evidence. RNA is not protein; protein expression cannot establish safety, efficacy or a therapeutic window. No expression contrast, target ranking, manuscript or publication decision follows from this receipt.

Worker `/root/cspg4_browser`; reserved resource `paper:PUB-SURFACE-TARGETS:cspg4-browser-source`; verified base `97ed864b3275aca69a540f6973573054efb166cd`. Requested effort: medium; actual independent runtime model/effort identifier unavailable (inherited agent configuration, not relabeled as verified medium). Browser backend reported Codex In-app Browser, type iab, ID 1. Browser retrieval and cleanup finished by 2026-09-06T06:28:15.741Z, less than five minutes after prerequisite reading. No broad search, direct HTTP request, challenge solving, credentials entry, paid service, outreach, nested agent or shared-state edit. Only this reserved output directory was written. Validation: JSON parsing and artifact/prerequisite SHA-256 computation; no scientific tests, normal gate or commit (coordinator integration responsibility). Both worker-created tabs are closed; no worker process, download or browser work remains running.

Next action: coordinator verifies this frozen access receipt and records the source dependency as unresolved. No repeated browser attempt is selected by this checkpoint.
