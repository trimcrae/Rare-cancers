---
id: DOC-NR4A3-FUSION-TRANSCRIPTIONAL-OUTPUT-REPO-NOTES
title: "Repository-internal notes for the EWSR1::NR4A3 transcriptional-output manuscript"
level: L3
kind: memo
status: live
canonical_for: []
purpose: >
  Hold the operational, repository-internal notes that were removed from the transcriptional-output
  manuscript when it was reformatted for journal submission — staged systems-graph records, proposed
  map-edits, cross-lane coordination, and the map of which concepts the manuscript owns — so that
  none of that maintainer-facing information is lost from the repository even though it does not
  belong in the paper an external reader sees.
scope: >
  Repository operations only. Contains no scientific result; every number and finding lives in the
  manuscript and its committed artifacts. This file is never submitted anywhere.
audience: [maintainers, autonomous research agents]
related: [DOC-NR4A3-FUSION-TRANSCRIPTIONAL-OUTPUT]
date: 2026-08-07
last_verified: 2026-08-07
---

# Repository-internal notes for the EWSR1::NR4A3 transcriptional-output manuscript

These notes were moved out of [`nr4a3-fusion-transcriptional-output.md`](./nr4a3-fusion-transcriptional-output.md)
when it was reformatted into a clean, journal-submission-ready manuscript (2026-08-07). The manuscript
now reads as a self-contained paper; this file keeps the operational information a maintainer still
needs. Nothing here is part of the paper, and nothing here is a scientific claim.

## What the manuscript is the one home for

- The **evidence-typed catalogue** of published NR4A3 / NR4A3-fusion transcriptional targets, with
  assay, cell system, species and verbatim sentence per gene — machine-readable in
  [`nr4a3_fusion_targets.py`](../modalities/nr4a3_fusion_targets.py) → `LITERATURE_TARGETS`.
- The **measurement that the native→fusion transfer assumption fails in both directions** (§3.2).
- The **size-matched empirical null** as the required calibration for any gene-set read on these
  platforms (§2.4), and the four instrument controls (§2.5).
- The **named discriminators** between the fusion driving a gene and the gene being correlated with
  EMC (§4.2), and the **measured absence of any retrieved NR4A3-fusion cistrome** in 2,276 documents
  (§3.10).
- The **result** of the array/3SEQ run (§3.3–3.7) and the **PPARγ activity reading with its
  adipogenic ceiling** (§3.9).

The PPARγ *direction* and *abundance* questions both have their one home in
[`pparg-direction-emc.md`](./pparg-direction-emc.md); the interpretation of the 3SEQ arm has its one
home in [`gse28866-tumour-vs-normal-reading.md`](./gse28866-tumour-vs-normal-reading.md).

## Proposed map-edits — DESCRIBED, NOT APPLIED

Routed as [`nr4a3-fusion-targets-map-edits.json`](./nr4a3-fusion-targets-map-edits.json) — six edits,
each `current_text` grep-verified to appear exactly once on both `origin/main` and in the working tree.
Verify with:

```
python3 research/manuscripts/verify_map_edit_anchors.py research/manuscripts/nr4a3-fusion-targets-map-edits.json
```

The six edits, in summary: (E1) re-scope `RT-PPARG-DOWNSTREAM`'s activity readout from *blocked on
data* to *blocked on one free CI dispatch*; (E2) withdraw a redundancy premise still standing in a
second field, and correct "an EMC expression read settles it either way"; (E3) give
`RT-TRABECTEDIN-PPARG` its real, narrower EMC-specific rationale with the caveat attached; (E4) add
Filion's never-cited negative result to `EV-FILION-2009`; (E5) register four new evidence items —
Brenca 2019, Kim 2016, Haller 2019 and Filion 2005/PLAGL1; (E6) narrow — not retire —
`TECH-EMC-EXPRESSION-DATA`, through which nine routes inherit `BLK-NO-EMC-DATA`.

> Note (2026-08-07): `verify_map_edit_anchors.py` previously documented a path argument and ignored
> it, always checking `three-row-audit-map-edits.json`. That defect is recorded here so a future
> session does not read a green result for the wrong file.

## Systems-graph records

A route (`RT-FUSION-OUTPUT`) and publication (`PUB-FUSION-OUTPUT`) for this work are modelled in the
systems graph (they appear in `systems/views/L3-publications.md` and `systems/views/L2-rt-fusion-output.md`).
The staged record file [`fusion-output-graph-records.json`](./fusion-output-graph-records.json) is
retained for provenance. If any field there is found to disagree with the applied graph, the applied
graph in `systems/graph/*.json` is authoritative.

## Cross-lane coordination

This module deliberately fetches **no** cistrome dataset. What it needs, stated so it can be supplied
rather than duplicated: a peak set carrying (i) the factor and construct that was ChIPped, (ii) the
genome build, and (iii) peak coordinates or nearest-gene assignments. Given those three fields, the
per-gene and per-set reads become peak-intersected in one offline pass with no new fetch.

## Corrections register (repository-internal supersessions)

Retained from the manuscript's former Appendix A; these are repository bookkeeping, removed from the
paper because an external reader does not need the supersession history.

- **"That pattern is the shape of a platform-wide offset."** Superseded 2026-08-07. Measured: the
  global offset is −0.0084 SD on GPL6244 and +0.0258 SD on GPL3290, an order of magnitude below the
  effects in question. The remedy is unchanged — the null absorbs both — but the mechanism is
  null-band **width** at n = 10 vs 6, not offset (manuscript §3.4).
- **"`emc-expression-panels.json` is not on `main`."** Superseded 2026-08-07. The artifact is on
  `main` together with its producing modules; every class-A figure quoted in the manuscript's control
  table is byte-identical between refs, so the corroboration in §3.3 is corroboration rather than a
  dependency.
- **An unsourced citation was removed.** A draft attributed the cloning of the EMC fusion to a 1995
  paper with a PMID present in no committed source; it was written from recollection and withdrawn.
  The background sentence is now anchored on the verbatim GEO series record and on Brenca *et al.*
  (recorded in the manuscript's citation-provenance note).
