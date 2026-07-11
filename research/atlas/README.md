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
This atlas is a **versioned, curated synthesis of _identified public_ evidence (as of July 2026), NOT a
systematic review** and not a claim to capture everything known. It integrates those fragments so that
downstream work starts from one cited base. Scores are a **judgment-based triage heuristic**, not
calibrated probabilities or treatment recommendations. **No EMC cell line exists in DepMap — all
dependency reads are non-EMC surrogates.**

**No wet lab is available** to this project, and **nothing here has been validated in EMC**. Every
artifact is either (1) an in-silico analysis reproducible via its documented workflow or (2) a cited
synthesis built to be handed to a wet-lab collaborator. Nothing here is a treatment recommendation.

**Reproducibility (precise).** `node research/atlas/build.mjs` *deterministically rebuilds the atlas
`dist/` outputs from the committed source files and validates provenance.* The upstream analyses (GEO
reprocessing, DepMap dependency, EuropePMC full-text, MHC prediction, FDA-label PK) run in **separate,
pinned CI workflows** (`.github/workflows/atlas-data.yml`) with their own environments and retrieval
dates — see `REPRODUCIBILITY.md`. The one command does *not* re-run those upstream analyses.

## Contents

| File | What it is | Deliverable in the strategy |
|---|---|---|
| `citations.json` | Shared source/citation map; each SOURCE carries a `verified` flag + `verification_level` + PMID/PMCID/DOI/NCT (claims reference these sources) | provenance backbone |
| `samples.json` | Source of truth for the EMC sample/model registry | `emc_sample_manifest.tsv` |
| `drug_screens.json` | Reconstructed USZ (17 chemo + targeted panel) & NCC (221-compound) screens + compound→target→exposure; USZ hit identities are secondary-source/unconfirmed | compound–target table |
| `claims.json` | Atomic evidence claims, each with a source locator + EMC-specific-vs-extrapolated flag | `emc_claims_with_provenance` |
| `evidence_score.json` | Per-target/per-drug evidence components, ranked shortlist, validation panel | ranked reports + 12-compound/6-combination panel |
| `METHODS.md` | Manuscript-quality methods | methods document |
| `build.mjs` | One-command build: validates provenance, emits the `dist/` TSVs | reproducibility |
| `dist/*.tsv` | Generated, human-readable deliverables (do not hand-edit) | machine-readable outputs |
| `collaborator-brief.md` | 2-page evidence-backed package to recruit a wet-lab/clinical partner | strategy Phase B |
| `outreach.md` | Unaffiliated-researcher outreach: strategy, real recipients, send-ready emails + runbook (send needs trimcrae sign-off) | strategy Phase B |
| `overview-plain-language.md` | Non-technical explainer of the atlas for patients/foundations | outreach support |
| `antiangiogenic-mechanism.md` | Kinome-level TKI comparison + response-linked CRF/common data model | strategy Project 3 |
| `lineage-antigen-program.md` | Fusion-induced lineage-antigen program (B7-H3/PRAME/CHRNA6/NMB) | strategy Project 4 (lineage) |
| `expression_reprocess.py`, `fulltext_verify.py`, `panel_dependency.py` | CI data-fetch scripts (GEO/EuropePMC/DepMap — run via `atlas-data.yml`) | internet-gated analyses |
| `_generated/*` | Raw CI outputs (expression signature, full-text verification, panel dependency) | committed by CI |

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

## Verification tiers

Sources/claims are graded, not lumped as "verified". Tiers: **primary_full_text**, **primary_abstract**,
**regulatory_label** (FDA label PK), **computational_reproduction** (an in-repo CI analysis),
**secondary_source_unconfirmed** (asserted in reviews/search but not confirmed from the primary source —
e.g. the USZ single-agent compound identities), and **unresolved/pending**. `build.mjs` reports the
breakdown by tier rather than a single count. A `verification_level` lives on the SOURCE record; claims
reference sources and carry their own `confidence`.

## Collaboration

This is a research resource seeking a wet-lab/clinical collaborator. The experiment-level ask: run the
proposed class-vs-compound panel in EMC models (Program 1), or discuss a growth-rate-adjusted,
fusion-annotated response cohort (Program 2). Authorship follows substantive contribution (ICMJE/COPE).
Contact: Tristan McRae, independent researcher. *(Operational outreach material — recipient lists,
email drafts, tactics in `outreach.md` — is deliberately kept OUT of any citable/DOI deposit; see
`DEPOSIT.md`.)*

## Status

See `STATUS.md` for the current dated snapshot (verification-tier counts, unresolved items, release
blockers). Historical progress notes are in `CHANGELOG.md`.
