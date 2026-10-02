---
id: "DOC-CONTINUATION-2026-10-02-FOUNDATION-PRIMARY-SOURCE-AVAILABILITY"
title: "Foundation primary-source availability: bounded attempt closed"
level: "cross-cutting"
kind: "memo"
status: "live"
canonical_for: []
purpose: "Record the scoped evidence and reasoning for Foundation primary-source availability: bounded attempt closed."
scope: "October 2 continuation; limited to the named sources, computations and review scope recorded in the body. No submission clearance."
audience: ["maintainers","autonomous research agents"]
date: "2026-10-02"
last_verified: "unverified"
_backfilled: "true"
---

# Foundation primary-source availability: bounded attempt closed

Recorded 2 October 2026. The new independent primary-workbook check is
UNVERIFIED. Do not label this attempt passed or substitute the earlier
derived-mapping replay for direct primary extraction.

## Actual unsuccessful attempt

Run: https://github.com/trimcrae/Rare-cancers/actions/runs/37011070408
Job: https://github.com/trimcrae/Rare-cancers/actions/runs/37011070408/job/110850663535

The subprocess using --fetch-primary exceeded its 240-second timeout. No
passing primary-check receipt was produced. The requested source was the public
Europe PMC supplementary-files endpoint for PMC9200814. This outcome establishes
a bounded retrieval/verification failure, not an error in the underlying workbook
or proof that the primary source no longer exists.

Separately, correction replay run 37009409052/job 110845272744 passed all 3,771
records and four negative controls using the pinned derived mapping:
https://github.com/trimcrae/Rare-cancers/actions/runs/37009409052

Its corrected-export SHA256 is
2c910856e5e483c3774af5d0192b6118536f368aade8f05960bb123014a20184.
That replay validates the corrective resource against the derived mapping; it
does not complete this fresh primary-source check.

## Historical capture recovery

The scripts wrote the workbook as:
- campaign-output/foundation-original/41467_2022_30496_MOESM2_ESM.xls
- campaign-output/foundation-emc-primary/primary.xls

The inspected workflow uploaded JSON, TSV, CSV, TXT, XML and ZIP files, but
excluded XLS. The supplementary ZIP was held in memory by those scripts, not
written as an uploadable archive. Thus those successful runs did not retain the
raw workbook through their stated upload configuration. Artifact metadata alone
is not a ZIP-member listing; no raw member was independently recovered.

Actual unexpired artifact metadata:

| Run | Artifact name | Artifact ID | Compressed bytes |
|---|---|---:|---:|
| 36878758347 | emc-Foundation-primary-XLS-and-export-identifiers-36878758347 | 11170965078 | 16757 |
| 36882524218 | emc-Foundation-75-EMC-original-CNA-and-fusion-calls-36882524218 | 11172400547 | 847841 |
| 36897521385 | emc-Foundation-3771-export-ID-proof-and-75-partner-controls-36897521385 | 11180955168 | 182322 |

Workflow at the actual original primary-analysis revision:
https://github.com/trimcrae/Rare-cancers/blob/fa74fad6b9325635f712dba4911642a64a4dd6d6/.github/workflows/emc-data-deep-2026-10-01.yml

Earlier original-XLS workflow:
https://github.com/trimcrae/Rare-cancers/blob/faf65c47f0569e56d68f3247de38244dbfcb0a48/.github/workflows/emc-data-deep-2026-10-01.yml

Frozen primary extraction:
https://github.com/trimcrae/Rare-cancers/blob/da49c4e836533253825587f83656675dac4c913b/research/autonomy/data-opportunities-2026-09-30/deep-analysis/foundation_emc_workbook_analysis.py

The second artifact should contain derived all-variants.json and clinical.json
under campaign-output/foundation-emc-primary, per its script and upload policy.
Their availability is useful for recovery of derived evidence, but they do not
replace raw workbook bytes for independent re-extraction.

## Other bounded discovery

The Nature article's official indexed record identifies Supplementary Dataset 1.
Frozen primary metadata names 41467_2022_30496_MOESM2_ESM.xls as its relative
media filename. A direct Nature page fetch redirected to its identity service;
PMC returned a browser challenge. No challenge was solved or bypassed and no
speculative publisher download URL was promoted to a verified source.

The article links the official author code repository:
https://github.com/djinfmi/gounder_et_al_2022

Its inspected contents were figure-generation Markdown and rendered figure
assets, not the primary workbook. Rare-cancers code search returned no matching
committed workbook but marked results incomplete. These checks do NOT exhaust
all possible public sources or prove that no other retained capture exists.

## Exact input that reopens the check

An existing authorised capture or normally accessible public copy of:
41467_2022_30496_MOESM2_ESM.xls
Bytes: 4,812,800
SHA256: 88c1a0bab7509ffe3bcff955b89f3d60ddb58a68311cd4c56ca4b0c78506b475
Signature: d0cf11e0a1b11ae1 (legacy OLE/BIFF XLS).

Once those bytes are available, run foundation_primary_workbook_check.py with
--workbook to avoid the failed network route. Preserve the raw capture as an
explicit future artifact input, together with its source and hash receipt.
Until then, retain the timeout and mapping-derived scope in manuscript records.
No further unchanged fetch is prescribed; this bounded attempt is closed.
