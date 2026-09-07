---
id: DOC-TRIAL-COMPARATOR-EXPANSION-20260905
title: Completed comparator first reading
kind: memo
status: live
date: 2026-09-05
last_verified: 2026-09-05
purpose: Preserve the complete comparator source review pending independent adjudication.
scope: The 74 comparator pairs in the frozen 149-pair registry snapshot; first-reader scope only.
audience: [autonomous research agents, external reviewers]
---

# Completed comparator first reading

All 74 remaining comparator pairs have source-linked first-reader judgments: 29 DSRCT and
45 synovial-sarcoma pairs. The completed artifact is
[first-reader-checkpoint-0074.json](first-reader-checkpoint-0074.json). Its SHA256 is
`5fa090d56c7c370702f665f1e2477419c352728eca2443e51436ae341976443a`.
Earlier checkpoints and note batches remain immutable.

Together with the 50 new EMC judgments and 25 previously adjudicated overlaps, this completes
first-reader coverage of the frozen 149-pair current query frame. The 124 new judgments still
require independent adjudication. The other 24 previously adjudicated reference pairs outside
that current frame remain preserved in their original reference; no label is replaced here.

The coordinator read the seven saved modules for each comparator pair in its existing context
and wrote in a separate reserved worktree. This is neither a fresh-context second reading nor
independent semantic verification. Protocol and work order were frozen before the first reading.
The original source packet and archived pages, not current live registry pages, define this snapshot.

## Checks and limits

[verify_sources.py](verify_sources.py) reproduced the completed artifact, verified all seven
checkpoint prefixes and note hashes, and checked 431 record copies against 80 original compressed
source pages. It checked 216 exact excerpts and 518 saved modules against the original pages.
[source-verification.json](source-verification.json) preserves the result. Reproduce with:

```text
python -B research/autonomy/trial-reference-expansion-comparators-2026-09-05/verify_sources.py
```

These are provenance checks, not an independent determination that the labels are correct.
First-reader counts are 62 explicit diagnosis compatible, nine exclusions, two broad tumor
compatible and one insufficient evidence. They describe this selected snapshot only, not
prevalence, patient eligibility, current slots, therapeutic benefit, or retrieval performance.
Biomarker requirements, study purpose, phase/cohort restrictions and protocol uncertainty are
recorded separately. Diagnostic, surgical-device, fertility and microdose research must not be
silently counted as systemic treatment opportunities.

## Issues for the later adjudication

The second reader must make a source-only judgment before seeing these notes. After that freeze,
the adjudication must specifically reconcile the following recorded uncertainties alongside all
other disagreements:

- SS:NCT03016819 has a closed SS-specific cohort, a separately open broad pharmacokinetic cohort,
  and contradictory ASPS-only recruitment text. Its broad-scope judgment does not imply SS access.
- SS:NCT02275286 explicitly closes the historically SS-compatible cohort; remaining cohorts have
  incompatible histology lists. The exclusion label records this closure/current-scope interpretation,
  while preserving historical SS inclusion. Endpoint definitions must distinguish these concepts.
- SS:NCT07066982 names SS and broad sarcoma eligibility but contains material age, product and
  intervention-domain inconsistencies. The label records histologic scope only.
- Several cell-therapy records have HLA and antigen gates, or missing assay thresholds; no molecular
  eligibility can be inferred from an SS diagnosis. Some generic sarcoma and named SS routes have
  different explicit testing clauses.
- Master protocols and early-phase routes do not establish that a particular cohort is open.
  External protocols were not reviewed and saved recruitment dates remain as recorded.

Next: preserve this completed package through normal integration, prepare source-only comparator
inputs, independently adjudicate the 124 new pairs, then freeze the retrieval endpoints and run the
decisive evaluation. The existing 50-pair source-only EMC packet is already prepared. New independent
desktop tasks still need the user-requested Full access setting verified; this package does not
claim that the unresolved launch default has changed. No full publication gate or ultra review has
run, and no preprint-readiness claim is made.
