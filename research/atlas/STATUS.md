# EMC Atlas — STATUS (single dated snapshot)

**Snapshot date:** 2026-07-11 (ET). **Release commit:** _not yet tagged — see release blockers._
Historical development notes are in `CHANGELOG.md`. This file is the one authoritative current-state view.

## What this is
A versioned, curated synthesis of *identified public* EMC evidence (NR4A3-rearranged EMC) with a
judgment-based triage heuristic. **Not** a systematic review; **nothing validated in EMC**; **no EMC line
exists in DepMap** (all dependency reads are non-EMC surrogates).

## Contents (current)
- Sources/citations: 32 (see verification-tier breakdown below).
- Claims: 23 atomic claims (each references graded sources; carries its own confidence).
- Scored entities: 10 therapeutic axes/nodes (triage heuristic, not probabilities).
- CI analyses folded in: GEO expression reprocessing (GSE24369), EuropePMC full-text verification,
  DepMap panel dependency, junction antigen MHC-I/II, FDA-label pharmacology.
- Docs: README, METHODS, REPRODUCIBILITY, DEPOSIT, collaborator-brief, antiangiogenic-mechanism,
  lineage-antigen-program, overview-plain-language; outreach (operational, excluded from any deposit).

## Verification tiers (sources) — NOT aggregated as one "verified" count
Run `node research/atlas/build.mjs` for the live per-tier breakdown. Tiers: `primary_full_text`,
`primary_abstract`, `regulatory_label` (FDA labels), `computational_or_resource` (in-repo CI analyses +
named databases/methods), `secondary_source_unconfirmed` (e.g. the **USZ single-agent compound
identities** — asserted secondarily, not confirmed from the primary paper), `unresolved_pending`
(e.g. GSE4303, not usably reprocessed).

## Key limitations (current)
- USZ screen compound identities are **secondary-source/unconfirmed** (Bangerter full text not OA);
  awaiting author/full-text confirmation (Email 1 to Dr. Pauli).
- Proposed validation panel is **not exposure-matched / not ready-to-run** — concentration ranges need
  final pharmacology + primary-source review; `panel-exposure.json` holds verbatim label quotes only.
- DepMap results are **non-EMC surrogates**; causal conclusions (mechanism, "markers not addictions",
  BH3-mimetic choice) are softened to surrogate/hypothesis language.
- Antigen results are **predicted binding only** (no processing/presentation/immunogenicity demonstrated).
- Fusion-subtype antiangiogenic difference is a **possible association requiring prospective validation**.
- Evidence score weights are **author judgments, not calibrated probabilities**.

## Release blockers (must clear before minting a DOI)
1. Source-author accuracy corrections folded in (esp. Pauli / USZ compound identities).
2. Real ORCID added to `CITATION.cff` + `.zenodo.json` (no placeholder); version + date + exact commit filled.
3. **Curated** deposit assembled per `DEPOSIT.md` (whole repo NOT deposited; outreach/strategy/site/scratchpad excluded).
4. Independent review complete + green `build.mjs` on the exact tagged commit; **PR #3 not merged/released while unreviewed**.

## Unresolved / open (no wet lab; not release-blocking)
- GSE4303 clone-ID→symbol crosswalk (legacy two-colour arrays) — or drop as superseded by GSE24369.
- A completed compound-by-compound pharmacology table (active conc vs total/unbound exposure, units, QC).
- Dependency lockfiles + `MANIFEST.txt` (SHA-256) for the deposit (self-doable in CI).
