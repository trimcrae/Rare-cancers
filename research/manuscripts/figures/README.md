# Manuscript figures

Auto-generated, data-driven figures for `repurposing-hypotheses.md`. Regenerate after the
catalogue changes:

```
node research/manuscripts/figures/make-figures.mjs
```

- **candidate-landscape.svg** (Figure 1) — **evidence × novelty map** (not a score ranking):
  rows = EMC-specific evidence strength (clinical → mechanistic), columns = novelty (known →
  novel). Green cells = novel + functional EMC evidence (the actionable leads); amber = evidenced
  but known (imatinib); the empty "novel × clinical" cells show the field's core gap. Generated
  from `candidates.json` (`evidenceType` × `scores.novelty`), so it cannot drift from the data.
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
