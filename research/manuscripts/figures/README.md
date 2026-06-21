# Manuscript figures

Auto-generated, data-driven figures for `repurposing-hypotheses.md`. Regenerate after the
catalogue changes:

```
node research/manuscripts/figures/make-figures.mjs
```

- **candidate-landscape.svg** (Figure 1) — the 14 existing-drug candidates as horizontal bars,
  length = priority score (0–18), colour = evidence tier (T3→T0), ★ = patient-page-eligible.
  Generated directly from `research/hypotheses/candidates.json`, so it cannot drift from the data.
- **stress-test.svg** (Figure 3) — strip plot of where our 31 candidate drugs rank (percentile)
  in TxGNN's indication ranking for EMC vs chondrosarcoma vs soft-tissue sarcoma; the leads
  cluster low across all three (medians 21 / 17.7 / 17.4), refuting an EMC-sparsity explanation.
  Generated from `research/hypotheses/txgnn-relatives-comparison.json` (skipped if that file is
  absent).
- **triangulation.svg** (Figure 2) — schematic of the three-method design: curation + enumeration
  converge into the scored catalogue; TxGNN diverges and is reported as a limitation (not
  promoted); the catalogue feeds the manuscript and, only at T3 + clinician review, the patient
  page (the firewall). Static schematic (layout in `make-figures.mjs`).

These are **draft** figures for the working manuscript; final figures should be produced to the
target journal's style by the human authors. Do not hand-edit the SVG — change the data or
`make-figures.mjs` and regenerate.
