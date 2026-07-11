# Reproducibility

> **Reviewer must-fix #3.** The "one command" only rebuilds the atlas *outputs* from committed source
> files; the upstream analyses run in separate, pinned workflows. This file documents both layers, the
> source/database versions + retrieval dates, seeds, and a clean-environment reproduction test.

## Two layers

**Layer 1 — atlas rebuild (deterministic, local).**
`node research/atlas/build.mjs` validates provenance and regenerates `research/atlas/dist/*.tsv` from the
committed JSON sources. No third-party dependencies (Node ≥18). Same inputs → identical outputs.
*Clean-environment test:* in a fresh checkout at the release commit, run the command and confirm `git
diff --exit-code research/atlas/dist` is clean.

**Layer 2 — upstream analyses (CI, internet-dependent, NOT re-run by Layer 1).**
Run via `.github/workflows/atlas-data.yml` on GitHub-hosted `ubuntu-latest`. Each writes to
`research/atlas/_generated/`. They are internet-dependent (public databases) and are **not**
bit-for-bit reproducible in general (upstream data can change), so outputs are pinned to the retrieval
dates and source versions below.

| Analysis | Script | Source + version | Retrieved | Environment | Determinism |
|---|---|---|---|---|---|
| Expression reprocessing | `expression_reprocess.py` | GEO GSE24369 (GPL6244), GSE4303; series matrices + GPL SOFT | 2026-07-11 | Python 3.11, stdlib only | Deterministic given fixed GEO files (rank-based; no RNG) |
| Full-text verification | `fulltext_verify.py` | EuropePMC REST | 2026-07-11 | Python 3.11, stdlib only | Deterministic given fixed records |
| Panel dependency | `panel_dependency.py` | DepMap **24Q4** (Figshare CRISPRGeneEffect.csv + Model.csv) | 2026-07-11 | Python 3.11 + `pandas` | Deterministic given the pinned release |
| Junction antigen MHC-I | `antigen_expand.py` | UniProt Q01844/Q92804/Q92570; MHCflurry 2.0 `models_class1_presentation` | 2026-07-11 | Python 3.11 + `mhcflurry` | Deterministic (no sampling); modeled breakpoints flagged |
| Junction antigen MHC-II | `antigen_mhcii.py` | same UniProt; MHCnuggets (class II) | 2026-07-11 | **Python 3.10 + tensorflow 2.10 + numpy 1.23.5** (isolated venv; MHCnuggets breaks on modern-Keras `lr` and numpy-2 ABI) | Deterministic (no sampling) |
| Panel exposure | `panel_exposure.py` | DailyMed SPL (FDA labels) | 2026-07-11 | Python 3.11, stdlib only | Verbatim quotes; deterministic given fixed labels |

**Random seeds:** none of the above uses stochastic sampling (rank statistics, deterministic predictors,
verbatim extraction), so no seeds are required. If a future analysis adds sampling, record the seed here.

## Dependency pinning (to add before the DOI)
- The stdlib scripts need only the stated Python minor version.
- For `pandas` / `mhcflurry` / `mhcnuggets`, capture exact versions with a lockfile (e.g. `pip freeze >
  research/atlas/requirements-lock-<analysis>.txt` inside each CI env) and include the lockfiles in the
  deposit. *(Self-doable: I can add a CI step that emits these lockfiles.)*

## Input hashes (to add at release)
Record a SHA-256 for each committed input the atlas depends on (the JSON sources and `_generated/*`) in
`MANIFEST.txt` (see `DEPOSIT.md`), tied to the exact release commit, so a third party can confirm they
are evaluating the same inputs.

## Honest limits
- Upstream public databases (GEO, DepMap, EuropePMC, DailyMed, UniProt) can change; exact reproduction
  requires the pinned versions/dates above, not merely re-running the workflow "today".
- GSE4303 was NOT usably reprocessed (legacy custom two-colour arrays, no standard symbol column);
  the expression signal rests on GSE24369 (n=6 EMC).
