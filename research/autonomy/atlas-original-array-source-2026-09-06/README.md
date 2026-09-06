---
id: DOC-ATLAS-ORIGINAL-ARRAY-SOURCE-20260906
title: Original array source recovery and corrected metadata
kind: memo
status: live
date: 2026-09-06
last_verified: 2026-09-06
purpose: Preserve exact original-scale source and all sample labels.
scope: Fixed-panel source preservation and qualified interpretation.
audience: [maintainers, autonomous research agents]
---

GSE24369 contains 42 samples: six EMC biopsies, seventeen LGFMS, six myxofibrosarcomas, six desmoids, five solitary fibrous tumors and two pooled skeletal-muscle RNA records. All twelve fixed genes/control have one uniquely assigned GPL6244 transcript cluster. Source VALUE is RMA log2 signal. The old cache's generic fibrosarcoma label and dropped SFT records are not reused; original sample biopsy stage remains unestablished.

original-source-recovery.zip preserves the original source recovery packet except the byte-identical GSE24369 gzip already committed at ../atlas-primary-provenance-2026-09-06/GSE24369.soft.gz. preservation-manifest.json verifies that external duplicate and every archive member. The original source memo, annotation TSV, platform/sample evidence and extraction scripts remain unchanged inside the ZIP. GSE4303's different reference labels remain unresolved; it is excluded from tissue-abundance replication. No patient independence or normal-organ sparing is inferred from sample labels or pooled controls.
