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
date: 2026-08-08
last_verified: 2026-08-08
---

# Repository-internal notes for the EWSR1::NR4A3 transcriptional-output manuscript

These notes were moved out of [`nr4a3-fusion-transcriptional-output.md`](./nr4a3-fusion-transcriptional-output.md)
when it was reformatted into a clean, journal-submission-ready manuscript (2026-08-07). The manuscript
now reads as a self-contained paper; this file keeps the operational information a maintainer still
needs. Nothing here is part of the paper, and nothing here is a scientific claim.

## What the manuscript is the one home for

⚠ **Section numbers below were re-pointed on 2026-08-08**, when the manuscript was retitled and split
into a main text plus `nr4a3-fusion-transcriptional-output-SI.md`. If a pointer here disagrees with a
heading in the paper, the paper is authoritative.

⚠ **AND THE PAPER WAS REFRAMED LATER THE SAME DAY, WHICH MOVED §1.** *Superseded, retained: the
title "The direct-target catalogue of EWSR1::NR4A3 is three genes wide, and one gene survives
calibration".* The paper had been leading with its **weakest** result — *ENO3* is the pre-designated
positive control (Limitation 17), the ordering rests on cohorts of 4, 6 and 10, and no gene here is
separable from mere disease association — while the size-matched null is general, reusable beyond
this disease, and untouched by any of that. The calibration is now the stated contribution and the
gene ordering is the worked example. **§1 was reordered**: the old §1.3 (the calibration) is now
**§1.1**, the old §1.1 (disease and driver) is **§1.2**, and the old §1.2 (the gap) is **§1.3**.
**The figures were renumbered to match first mention** — the null is now **Figure 1**, the evidence
classes **Figure 2**, and the per-tumour panel **Figure 3**; 4 and 5 are unchanged. **No number in
§3 changed**, and nothing measured was withdrawn.

- The **evidence-typed catalogue** of published NR4A3 / NR4A3-fusion transcriptional targets, with
  assay, cell system, species and verbatim sentence per gene — machine-readable in
  [`nr4a3_fusion_targets.py`](../modalities/nr4a3_fusion_targets.py) → `LITERATURE_TARGETS`, tabulated
  as Supplementary Table S1.
- The **measurement that the native→fusion transfer assumption fails in both directions** (§3.2).
- The **size-matched empirical null** as the required calibration for any gene-set read on these
  platforms (§2.3), its **detectability threshold** per set (§3.9, Supplementary Table S2), and the
  three-state instrument-control grading rule (§2.4, §3.3).
- The **confound audit**: comparator composition read from the GEO sample titles, every stratum
  contrasted separately, the reference-pool-matched contrast, the provenance-filtered covariate
  adjustment and the skeletal-muscle admixture control (§3.4–§3.6, Supplementary §S5).
- The **named discriminators** between the fusion driving a gene and the gene being correlated with
  EMC (§4.3), and the **measured absence of any chromatin experiment on EMC material** — no NR4A3-fusion
  cistrome retrieved in 2,276 documents, and, measured 2026-08-08 across seven archives, zero deposits
  on EMC material under any chromatin library strategy, against sibling-fusion chromatin maps that do
  exist (§3.11). ⚠ The one genome-wide chromatin readout carrying NR4A3 fusions, GSE243553, is
  accessibility in HEK293T and is reported as such, never as a cistrome.
- The **result** of the array/3SEQ run (§3.3–§3.9) and the **PPARγ activity reading with its
  adipogenic ceiling** (Supplementary §S4).

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
- **An unsourced citation was removed, and has now been replaced by a fetched one.** A draft
  attributed the cloning of the EMC fusion to a 1995 paper with a PMID present in no committed
  source; it was written from recollection and withdrawn, and the background sentence was re-anchored
  on the GEO series record and Brenca *et al.* ⚠ *Superseded 2026-08-08:* that left §1.3's date claim
  resting on nothing, because a bare year carries no identifier and so escapes `lint_citations`
  entirely. The cloning paper was retrieved from Europe PMC (PMID 8634690, 1995, cited 139) and is
  now reference 9a. It needed a `citation-provenance-ledger.json` entry despite being a genuine fetch
  product, because `lint_citations.PATTERNS['PMID']` cannot read the `"pmid": "…"` form this
  repository's own probes write — see that entry's note.
  (recorded in the manuscript's citation-provenance note).
