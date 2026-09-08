---
id: DOC-EMC-ATR-COLLABORATOR-PACKAGE-INTEGRATION-QA
title: "Integration QA note for the 2026-09-08 working revision of the EMC ATR collaborator package"
level: L3
kind: memo
status: live
canonical_for:
  - the figure-QA observations carried out of the Figure 1 caption at the 2026-09-08 integration
purpose: >-
  Hold the drawing-level observations about Figure 1 of the EMC ATR collaborator package that belong
  to the quality record rather than to a reader-facing caption, together with the denominator
  qualification attached to the section 3.5 frequency sentence.
scope: >-
  A record of observations made while integrating an already-reviewed revision. No figure was
  redrawn, no artifact was modified and no scientific result was recomputed.
audience: [maintainers, external reviewers, autonomous research agents]
date: 2026-09-08
last_verified: 2026-09-08
related: [DOC-EMC-ATR-COLLABORATOR-PACKAGE]
---

# Integration QA note — EMC ATR collaborator package, 2026-09-08 working revision

This note holds observations that were previously carried inside the Figure 1 caption of
[`emc-atr-collaborator-package.md`](./emc-atr-collaborator-package.md). They are quality-record
material about how the figure is drawn and how it may drift, not information a reader needs in
order to read the panels. Moving them changed no figure, no artifact and no result. Nothing here
was re-measured at integration; each item is recorded as it stood when it was observed.

## 1 · Legibility of the closely spaced NR4A3 ticks in Panel A

`emc_fusion_frame_figure.py` draws NR4A3 RG ticks at residues 371 and 508. An independent reading of
the rendered image reported one of them. Whether the 371 tick is occluded by the adjacent
domain-block edge at 373, or is simply not resolved at print size, was not settled. Neither
explanation is asserted. The legibility of the rendered figure at print size has not been
verified here.

## 2 · Hard-coded Panel A box spans and their source data field

The Panel A RGG-box spans are hard-coded literals in the generator. They currently match
`rgg_boxes_operational` in `emc-fet-construct-designs.json` exactly, which was checked.

The generator's `stamp()` opens each listed source file as bytes and hashes the whole file, so a
change to that data field *would* change the recorded provenance stamp. The hazard is narrower than
a stale stamp: the code carries no binding, and asserts no equality, between the data field and the
literals. A later edit to the data field followed by a redraw would produce a fresh, correct stamp
while the literals, and therefore the drawn spans, silently no longer matched the field they are
supposed to depict. Anyone editing `rgg_boxes_operational` should re-check the literals by hand.

## 3 · Denominator qualification for the section 3.5 frequency sentence

Section 3.5 now opens: "TCF12::NR4A3 was reported in one of 26 cases in one EMC series [6]." That is
the retained quotation from reference 6, and it reports no population prevalence.

The qualification the coordinator attached to it, recorded here so the manuscript need not carry it:
the pooled partner-frequency record in this repository uses partner-assigned denominators, which
are not the same as the total series sizes. The pool's Agaram denominator of 24 excludes 2 unassigned
cases, whereas the 1 of 26 quoted above uses the entire series; the Huang pool of 57 likewise differs
from that series' 58. Total-series and partner-assigned denominators are distinct and must not be
merged. The stored pooled value of 5 of 154 supports what the committed pool says; it is not a fresh
verification of source validity or of the independence of the pooled series. No new retrieval,
reference or attribution was made for this integration.
