---
id: DOC-PUB-MATRIX-ADDRESS-COMPARTMENT-DATASET-REQUIREMENTS
title: "Admission criteria for a dataset that could carry a compartment statement in EMC"
level: L4
kind: benchmark-definition
status: draft
date: 2026-09-09
last_verified: 2026-09-09
---

# What a dataset must supply before an EMC compartment claim is admissible

This is a **pre-specified admission test**, written so that a future dataset can be judged
against it without re-arguing the question. It defines only *admissibility of the instrument*.
Passing it licenses asking a compartment question; it licenses **no** claim about delivery,
accessibility, efficacy, selectivity or therapeutic window, none of which is obtainable from
expression data of any kind.

A candidate dataset is **ADMISSIBLE for a compartment statement in EMC** only if all of C1–C4 hold.

**C1 · Marker readability.** At least 8 of 11 endothelial and at least 7 of 10 immune markers in
`compartment_readability_census.py`'s pre-specified panels are measurable, *and* the dataset
states its own gene-coverage universe (whole-instrument versus retained extract), so that an
absent marker can be attributed.

**C2 · Value kind that admits a fraction.** Values are on an absolute or count scale within a
sample (single-channel intensity, or per-gene counts with library size recoverable). A two-colour
log-ratio against a reference pool is **inadmissible for a fraction by construction** — the
quantity is a ratio to an unrelated pool, and no mixture model recovers a proportion from it.
`GSE4303`/GPL3290 fails here on its own recorded `value_kind`.

**C3 · A comparison whose null is calibrated, or no comparison at all.** If a compartment score
is contrasted between EMC and a comparator arm, the contrast must be calibrated against random
gene panels of the same size drawn from the same universe. This condition exists because it has
already failed once on the committed arrays: random 14-gene panels fired the frozen arm-to-arm
rule for 0.2950 (E1) and 0.2075 (E2) of draws against a nominal 0.05, which is why the
endothelial and fibro/ECM findings on that substrate are withdrawn
(`COMMON-BRIEF.md`, measured 2026-09-08T04:38Z). A dataset that cannot supply this calibration
may still be described, but supports no arm contrast.

**C4 · Compartment resolution, or an explicit deconvolution reference.** Either the assay resolves
compartments physically (single-cell, single-nucleus, or spatial transcriptomics; or quantified
immunohistochemistry / microvessel density on the same tissue), or a matched reference signature
matrix is named and its provenance given. Bulk transcript with no reference cannot separate
"more vessel" from "more transcript per vessel".

**Nothing currently held in this repository passes.** Measured coverage, per instrument, is in
`compartment-readability-census.json`; the reasoning is in `FINDING.md`.

⛔ Even a dataset passing C1–C4 would establish **composition**, not **accessibility**. Vessel
transcript is not perfusion; matrix transcript is not matrix mass; neither is a measurement of
what any agent can reach. Accessibility in this disease is a tissue measurement — imaging,
interstitial pressure, or a labelled-agent distribution study — and no expression dataset
substitutes for it.
