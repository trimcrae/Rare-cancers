# EMC Open Target & Drug Atlas

> **Project 1 of the EMC research-strategy shortlist** (see the strategy brief that
> seeded this workstream). A version-controlled, machine-readable evidence system that
> answers one question:
>
> **Which genes, pathways, drugs and combinations have _independent_ support in EMC, in
> _which fusion subtype_, at what _evidence level_, and with what _feasible validation
> experiment_?**

Extraskeletal myxoid chondrosarcoma (EMC) is an ultra-rare NR4A3-rearranged soft-tissue
sarcoma. The published evidence is fragmented across a few dozen historical expression
profiles, three modern patient-derived models, two non-overlapping drug screens, small
clinical treatment cohorts, and incomplete fusion-partner annotation, with no standard way
to compare drug activity, achievable exposure, target engagement and clinical evidence.
This atlas integrates those fragments into one reproducible resource so that every
downstream experiment starts from the same evidence base.

**No wet lab is available** to this project. Every artifact here is either (1) a
reproducible in-silico analysis or (2) a structured synthesis of primary-source evidence
built to be handed to a wet-lab collaborator. Nothing here is a treatment recommendation.

## Contents

| File | What it is | Deliverable in the strategy |
|---|---|---|
| `citations.json` | Shared citation map; every claim carries a `verified` flag + PMID/PMCID/DOI/NCT | provenance backbone |
| `samples.json` | Source of truth for the EMC sample/model registry | `emc_sample_manifest.tsv` |
| `drug_screens.json` | Reconstructed USZ (40-drug) & NCC (221-drug) screens + compound→target→exposure | compound–target–exposure table |
| `claims.json` | Atomic evidence claims, each with a source locator + EMC-specific-vs-extrapolated flag | `emc_claims_with_provenance` |
| `evidence_score.json` | Per-target/per-drug evidence components, ranked shortlist, validation panel | ranked reports + 12-compound/6-combination panel |
| `METHODS.md` | Manuscript-quality methods | methods document |
| `build.mjs` | One-command build: validates provenance, emits the `dist/` TSVs | reproducibility |
| `dist/*.tsv` | Generated, human-readable deliverables (do not hand-edit) | machine-readable outputs |

Run `node research/atlas/build.mjs` to validate the JSON sources and regenerate `dist/`.

## Integration with existing repo assets (not duplicated — referenced)

This atlas is the *integrating layer*; it does not re-derive analyses that already exist:

- **DepMap dependency / expression** — `research/modalities/depmap-insilico-findings.md`,
  `depmap-sarcoma-dependency.json`, `depmap-target-expression.json`
  (FLI1-in-Ewing fusion-addiction analogy; NR4A family dispensability in dividing cells;
  B7-H3 / PRAME surface & antigen reads). Folded in as the "genetic perturbation" and
  "surface/antigen" evidence axes.
- **Biology & safety evidence base** — `research/manuscripts/nr4a3-emc-biology-evidence.md`
  (four-pillar fusion-oncoprotein prior; gnomAD LoF constraint; paralogue redundancy).
- **Repurposing candidates** — `research/hypotheses/candidates.json`,
  `target-drug-matrix.json` (DGIdb approved-drug map), `txgnn-emc-predictions.json`.
- **Fusion-junction antigen / HLA** — `research/modalities/fusion_neoantigen.py`,
  `hla_coverage.py` and outputs (the computational core of strategy Project 4, run in
  parallel).

The atlas gives these a single, provenance-checked home and a comparable evidence score.

## Non-negotiable rules (from the strategy brief's master instructions + repo AGENTS.md)

1. Every claim is an evidence object with a precise source locator.
2. EMC-specific evidence is tagged distinctly from evidence extrapolated from another cancer.
3. `EWSR1::NR4A3` and `TAF15::NR4A3` are **never** pooled without also being reported
   separately.
4. RNA over-expression is **never** treated as proof of dependency or of cell-surface
   protein.
5. One drug's activity is **never** treated as proof of its nominal target.
6. In-vitro potency is compared against clinically achievable free exposure before ranking.
7. Negative and contradictory evidence is reported alongside positive evidence.
8. No high-capacity model is trained on the tiny EMC-specific dataset.

## Status

See `STATUS.md` for the live build log and what is verified vs pending verification.
