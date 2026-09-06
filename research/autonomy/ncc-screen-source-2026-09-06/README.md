---
id: DOC-NCC-SCREEN-SOURCE-20260906
title: Recovered complete reported NCC EMC drug screen
kind: memo
status: live
date: 2026-09-06
last_verified: 2026-09-06
purpose: Preserve newly recovered measured EMC drug-response inputs and their actual limitations.
scope: Original source workbooks and independently reproduced extraction; no new treatment claim.
audience: [maintainers, autonomous research agents]
---

# Recovered source result

The [NCC-EMC1-C1 paper](https://link.springer.com/article/10.1007/s13577-025-01250-7)
links four supplementary workbooks. The initial source screen missed the supplementary
section. The coordinator's full-page recheck located those links; three downloaded files
are genuine workbooks containing the drug catalogue, complete reported screen and IC50 table.
The generic email asking for these missing public measurements was withdrawn before sending.

The worker's spreadsheet-library extraction and coordinator's independent standard-library
ZIP/XML extraction agree: 221 unique CAS identifiers, all with source viability (%) and SD;
the catalogue matches exactly; all 24 IC50 entries (nM) map to screen entries. This repairs
the input-access gap. It is not an independently validated new paper.

These are measurements of one patient-derived cell model. Preserve values outside 0–100%
as reported; do not clamp, call them clinical resistance, or interpret 221 drugs as 221
biological replicates. The SD definition, number/type of replicates, concentration and
duration, control/normalization and dose-response fitting need source Methods verification.
Table4 names24 agents and the FigureS2 description names21; a possible explanation is not
a verified reconciliation. No cross-study pooling or treatment inference is authorized by
this source recovery alone.

Original bytes and exact URLs are under sources/ and source-provenance.json. Run
`python verify_sources.py` to reproduce screen.csv, ic50.csv and coordinator-verification.json.
The coordinator check is actual independent extraction and arithmetic, not full publication
verification. worker-inspection.json retains the separate reader's result.

Next: inspect the primary Methods and the independent Zurich EMC response sources, establish
assay/model/drug overlap before any prespecified cross-study comparison, and request only
remaining specific source gaps under standing correspondence authority. Pending replies do
not suspend independent research.
