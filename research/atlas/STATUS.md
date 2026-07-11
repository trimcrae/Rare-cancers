# EMC Open Target & Drug Atlas — Status

**Live build log. ET timestamps (repo rule).**

## 2026-07-11 — v0.1 scaffold + verified core (this session)

**Built (Project 1, Phase A foundation):**
- Provenance backbone (`citations.json`) — 25 sources, 23 verified, 2 pending (GEO datasets await
  reprocessing). Reused the repo's already-verified model/biology/genomics keys; added freshly
  verified clinical citations.
- Sample registry (`samples.json` → `dist/emc_sample_manifest.tsv`) — 3 modern models (with
  verified exon-level breakpoints for the two USZ models), 1 authentication-gated historical line,
  3 tumor cohorts, 1 patient trio, 2 GEO datasets. EWSR1/TAF15 kept distinct throughout.
- Atomic claims (`claims.json` → `dist/emc_claims_with_provenance.tsv`) — 15 claims, each
  EMC-specific-vs-extrapolated tagged, with contradiction links (e.g. C009 gap vs C008 analogy;
  C010 gnomAD constraint vs C007 DepMap dispensability).
- Drug-screen reconstruction (`drug_screens.json` → 2 TSVs) — 6 verified hits + 2 verified
  combinations + an explicit `did_not_survive_verification` block.
- Evidence score + ranked shortlist + 12-compound/6-combination validation panel + go/no-go
  (`evidence_score.json` → `dist/emc_evidence_score.tsv`).
- Methods (`METHODS.md`), one-command reproducible build (`build.mjs`, no deps).

**Verified this session (two background agents, cross-checked ≥2 queries each):**
- USZ screen: carfilzomib (top), doxorubicin (2nd), PU-H71/HSP90 — VERIFIED (abstract level).
  Model fusions + exon breakpoints VERIFIED.
- NCC screen: brigatinib, panobinostat, romidepsin low-IC50 hits + 221-drug count — VERIFIED.
- Clinical: pazopanib (Stacchiotti 2019, ORR 18%/mPFS 19mo, NCT02066285), sunitinib (2014, 6/10 PR),
  IMMUNOSARC II (ASCO 2025, 6-mo PFS 77%/mPFS 13.2mo, NCT03277924), ipi/nivo±cabozantinib
  (NCT05836571, EMC 1 of 4 histologies), Japanese registry (Masunaga 2025, n=171, margin→LR, RT/chemo
  null), anthracycline (Stacchiotti 2013, 4/10 PR) — all VERIFIED (search-snippet level).

**Corrections made to the seeding strategy brief (medical integrity):**
- HDM201/MDM2-MDM4 as a USZ hit → NOT corroborated; demoted to hypothesis.
- carfilzomib+doxorubicin "synergistic in one / additive in the other" → not supported; both
  effects in both models; venetoclax also in the combination panel.
- "~40-drug" USZ screen → 17 chemo + a targeted panel.

**Honest limitations:**
- All primary-literature verification is **abstract/snippet level** — the egress proxy blocked
  PubMed/PMC/Springer/EuropePMC. `verification_level` is recorded per citation.
- **No IC50 numbers** were retrievable; marked `not_reported_retrievable`.
- A notable finding: nearly all systemic-therapy evidence traces to a **single group**
  (Stacchiotti / European sarcoma network) — a real concentration limitation and the obvious
  first collaborator to approach.

## 2026-07-11 — v0.2 fold in fusion-junction antigen axis (strategy Project 4 core)

Registered the **existing** in-repo antigen computation (`fusion_neoantigen.py` /
`fusion_breakpoints.py` / `hla_coverage.py`) into the atlas — free, ready, warranted:
- Claims C016 (junction-spanning MHC-I prediction) + C017 (HLA coverage), citations mhcflurry2 /
  afnd2020 / antigenComputationRepo.
- New scored axis `AXIS-fusion-junction-antigen`.
- **Honest headline:** the common EWSR1::NR4A3 junction gives a MODEST predicted MHC-I yield
  (2 strong / 3 sub-500nM of 34 junction peptides × 10 alleles). Per the strategy, a poorly-presented
  junction is an informative negative that redirects toward fusion-induced LINEAGE antigens
  (B7-H3/PRAME axis). Prediction only — no natural presentation demonstrated.

## Open next steps (all no-wet-lab, mostly free/cheap)
1. **Reprocess GSE4303 / GSE24369** (raw CEL → QC → EMC-vs-sarcoma + EWSR1-vs-TAF15 signatures,
   leave-one-sample-out, rank-based meta-analysis). Flips the 2 unverified GEO citations to verified.
2. **Full-text re-confirmation pass** when PMC access is available: IC50 numbers, HDM201 status,
   per-model synergy wording, NCC-EMC1-C1 fusion, unbound-Cmax exposure numbers.
3. **Fold in the fusion-junction antigen computation** (strategy Project 4) as a parallel axis —
   the repo already has `fusion_neoantigen.py` / `hla_coverage.py` outputs to register.
4. **Populate `achievable_free_exposure`** with cited unbound-Cmax values for the 12 panel compounds.
