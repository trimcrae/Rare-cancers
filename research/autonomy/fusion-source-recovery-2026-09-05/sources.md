---
id: DOC-FUSION-SOURCE-RECOVERY-PROVENANCE-20260905
title: Retrieval and inspection provenance
kind: memo
status: live
date: 2026-09-05
last_verified: 2026-09-05
purpose: Separate original source bytes from extracted representations and recovery failures.
scope: Four named primary sources and one local XLS reader dependency.
audience: [maintainers, autonomous research agents]
---

`retrieval-log.jsonl` records direct requests, timestamps, duration, URL, status and SHA256. Original Varley and Clerc XML hashes match the earlier source manifest. `output-manifest.json` identifies all preserved bytes, including archive members and derived views. Source retention is evidence provenance, not a redistribution license.

Oxford: both the exact prior PDF URL and canonical landing URL returned403 through the web tool; the direct download also returned403 after local network permission was granted. Title/DOI searches found the same ORA item. No alternate primary copy was recovered. No challenge, authentication or access restriction was bypassed.

Varley: Europe PMC supplied original XML and a ZIP containing article figures and the XLS. The XLS has `Supp. Table 1` (123rows,7columns) and `Supp. Figure 1` (18rows,1column plus an embedded PNG). All cells are preserved in JSON. xlrd2.0.2 was downloaded from official PyPI with its SHA256 checked against PyPI metadata, and imported directly from its wheel without modifying the environment. The reader wheel is a dependency, not scientific evidence. The embedded PNG was recovered from concatenated BIFF drawing/continuation records, validated by Pillow and visually inspected. An initial naive PNG carve failed because BIFF continuation headers interrupted it; that invalid derivative was removed after successful reconstruction. Main Figure4 JPEG was visually inspected; manual mean-line estimates use wide reading intervals and no invented statistical error bars.

Clerc: the Europe PMC supplementary ZIP timed out twice (one interrupted run continued briefly, causing a duplicate attempt). Direct publisher links exposed in the article recovered Table2 XLSX, supplementary PDF and main PDF. The original files are preserved. Table2 was read without editing via openpyxl. Main PDF p3/Fig1 and supplementary PDF p8/FigS2 were rendered using Poppler and visually inspected; text of the entire supplementary PDF was searched. Table2 row53 is the junction siRNA; row52 is the CTSD-body control; rows3-4 contain canonical CTSD and fusion primer pairs. Tables1/3 concern event lists and ChIP datasets according to the inspected supplement legends, so they were not pursued as oligonucleotide outcomes. Fig1G does not print a replicate count or quantitative error definition. Standard helicase transfection methods are not silently assigned as exact junction cotransfection conditions.

Ohba: the web tool exposed full publisher text at the existing DOI/full URL. `sources/ohba-web-representation.json` preserves that tool representation, which is not original HTTP content and must not be cited as a raw publisher-byte archive. Direct urllib requests returned403. Figure1A image and experimental sequences remain uninspected; no exact sequence is inferred from the article's exon prose. The Results opening paragraphs distinguish ABL-body designs from prior junction-specific designs in Figure1B.

Local network socket failures occurred before the permission change. The first download approval was granted; the second action was interrupted while an already-started process continued to completion. The user then explicitly enabled full access and instructed no further individual approvals. No escalation was requested afterward. `run-record.json` preserves the timing uncertainty and duplicate retrieval rather than attributing all wall time to science.
