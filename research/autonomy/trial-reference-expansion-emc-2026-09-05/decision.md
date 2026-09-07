---
id: DOC-TRIAL-REFERENCE-EXPANSION-EMC-20260905
title: Frozen expansion frame and EMC first-reader checkpoint
kind: memo
status: live
date: 2026-09-05
last_verified: 2026-09-05
purpose: Hand off a source-grounded EMC reference expansion for independent verification.
scope: Frozen registry disease and cohort scope; no individual eligibility or retrieval-performance claim.
audience: [maintainers, autonomous research agents]
---

The full expansion frame remains **149 diagnosis–trial pairs** (58 EMC, 39 DSRCT, 52 SS; 124 distinct trials). This checkpoint preserves the 25 integrated adjudicated overlaps exactly, retains the 24 outside-frame reference pairs separately, and supplies first-reader judgments for all 50 previously unjudged EMC pairs. The remaining 74 pairs (29 DSRCT, 45 SS) remain explicitly unjudged in `unfinished-pairs.json`. The benchmark is not complete or EMC-only.

`contract.json`, `label-protocol.json`, `full-frame.json`, the original-overlap objects, `unjudged-frame.json` and `work-order.json` were frozen before displaying new criteria. The order is ascending SHA256 of UTF-8 `20260905|EMC-expansion|NCTID`, with NCT ID as tie-breaker; it is a work order, not a prevalence sample. `frame-freeze-receipt.json` anchors those bytes. `source-packet.json` retains all 549 copies of the 124 required registry records, their compressed and decoded page hashes, JSON pointers and original page receipts. Duplicate records matched exactly; no source version was silently preferred over a differing copy.

The first reader read saved eligibility, descriptions, conditions, arms/cohorts, design/purpose/phases and snapshot status in the frozen order. Truncated displays were reread as detailed in `reading-log.json`. `judgments-*.json` are the preserved authored rationales. `assemble.py` adds verified excerpts, raw-source pointers/hashes and complete module evidence without inferring labels. Its first attempt caught one incorrect condition-array index before writing labels; `source-corrections.json` records the correction while retaining the original note. `first-reader-labels.json` and its inputs are frozen by `label-freeze-receipt.json`.

Review should preserve the substantive distinctions: explicit EMC inclusion versus named exclusions; diagnostic surveillance versus antitumor treatment; unrelated acronym hits versus express cancer exclusions; Ewing/DSRCT histology restrictions versus matching fusion classes; and additional biomarkers versus histologic scope. NCT01659203 has an unexplained “Other types of sarcomas” exclusion. NCT05597917 requires unestablished CD13 positivity and leaves EMC versus generic chondrosarcoma exclusion unresolved. NCT06548672 has a non-exhaustive solid-tumor list with unclear CDH3-expression requirements. NCT07469774 requires sponsor approval for unlisted escalation histologies. NCT04901702 has broad non-Ewing cohorts and a separately gated HR/DSB-alteration cohort. None is an uncomplicated patient-eligibility positive.

`validate.py` reproduced all 6,182 corpus metadata records from 24 query manifests, verified 112 saved pages and all source copies, reconciled the full frame and preserved overlaps, and checked 92 exact excerpts. It also reproduces the assembled artifacts. This is mechanical provenance/coverage validation, **not independent semantic verification**. Run it read-only from the repository root with bundled Python and `-B -X utf8`; add `--manifest` to verify the final exact-byte inventory. Do not rerun `freeze.py` or `finalize.py` to replace existing output: they deliberately refuse overwrites. `assemble.py` is read-only by default; its explicit `--write` path also refuses overwrites.

The next distinct work is separate independent source verification/adjudication of these 50 labels and a fresh comparator round for the 74 remaining pairs. No ranking, fitting, retrieval evaluation, manuscript rewriting, clinical-registry edits, commits, publication or normal integration preflight occurred here. No process remains running. Timing, the initialization app-message wait and actual permission limitations are recorded in `run-record.json`. This bounded checkpoint is not an independently verified preprint or a completed 149-pair benchmark.
