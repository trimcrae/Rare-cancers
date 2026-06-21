# Manuscript figures

Auto-generated, data-driven figures for `repurposing-hypotheses.md`. Regenerate after the
catalogue changes:

```
node research/manuscripts/figures/make-figures.mjs
```

- **candidate-landscape.svg** (Figure 1) — the 14 existing-drug candidates as horizontal bars,
  length = priority score (0–18), colour = evidence tier (T3→T0), ★ = patient-page-eligible.
  Generated directly from `research/hypotheses/candidates.json`, so it cannot drift from the data.

These are **draft** figures for the working manuscript; final figures should be produced to the
target journal's style by the human authors. Do not hand-edit the SVG — change the data or
`make-figures.mjs` and regenerate.
