# Curated atlas deposit — what to archive for a citable DOI

> **Reviewer must-fix #1 + #14.** Zenodo's GitHub integration archives the *whole connected repository*.
> This repository also contains a shelved patient-facing site, scratchpads, broader manuscripts,
> speculative roadmaps, and operational/outreach files — which should **not** be in a scientific archive.
> So the DOI must be minted from a **curated deposit**, either (a) a **dedicated atlas repository**
> mirroring the files below, or (b) a **manual Zenodo upload** of a curated bundle. Do **not** simply
> toggle Zenodo on the full `trimcrae/Rare-cancers` repo.

## Include (the curated atlas bundle), tied to an EXACT commit

- **Atlas documents:** `research/atlas/README.md`, `METHODS.md`, `REPRODUCIBILITY.md`, this `DEPOSIT.md`,
  `overview-plain-language.md`, `collaborator-brief.md`, `antiangiogenic-mechanism.md`,
  `lineage-antigen-program.md`. (STATUS.md/CHANGELOG.md optional.)
- **Source-of-truth data:** `citations.json`, `samples.json`, `claims.json`, `drug_screens.json`,
  `evidence_score.json`.
- **Analysis/build scripts:** `build.mjs`, `expression_reprocess.py`, `fulltext_verify.py`,
  `panel_dependency.py`, `antigen_expand.py`, `antigen_mhcii.py`, `panel_exposure.py`, and a copy of the
  CI workflow `.github/workflows/atlas-data.yml`.
- **Generated outputs:** `dist/*.tsv` and `_generated/*` (with the caveat that `_generated` are CI
  products; keep them for transparency, clearly labelled as generated).
- **Reproducibility metadata:** the pinned environment description, source/database versions + retrieval
  dates, input hashes, and the checksum manifest (see below and `REPRODUCIBILITY.md`).
- **Provenance:** the exact git commit SHA, version tag, and release date.

## Redistribution note (licensing)
Only redistribute third-party material that the source license permits. Verbatim FDA-label PK quotes are
public-domain US-government text (OK). GEO/DepMap/EuropePMC values are referenced with source + retrieval
date; redistribute derived/aggregate outputs, not bulk third-party datasets, unless their terms allow it.

## Exclude (keep OUT of the scientific archive)
- `outreach.md` (recipient lists, email drafts, tactics), and any internal strategy/roadmap files.
- The scratchpad directory and any working notes.
- The shelved patient-facing site (`cancers/`, `data/`, `assets/`, `index.html`, deploy/site files).
- Unrelated cancer work and repo-operational files (CI for non-atlas jobs, etc.).

## Manifest + checksums (generate at release)
Produce a `MANIFEST.txt` listing every included file with a SHA-256 and the release commit, e.g.:

```
# from the repo root, at the tagged commit:
git rev-parse HEAD > MANIFEST.txt
echo "# curated EMC atlas deposit — files + sha256" >> MANIFEST.txt
for f in research/atlas/*.md research/atlas/*.json research/atlas/*.mjs research/atlas/*.py \
         research/atlas/dist/*.tsv research/atlas/_generated/* .github/workflows/atlas-data.yml; do
  sha256sum "$f" >> MANIFEST.txt
done
```
Include `MANIFEST.txt` in the deposit. (I can generate this file for you in CI on request — self-doable.)

## Release blockers (do not mint until all true)
1. Source-author accuracy corrections folded in (esp. Pauli / USZ compound identities).
2. Real ORCID in `CITATION.cff` + `.zenodo.json` (no placeholder); version + date + commit filled.
3. Curated bundle assembled per this file (whole-repo NOT deposited).
4. Independent review complete + green build on the exact tagged commit; PR #3 not left open unreviewed.
