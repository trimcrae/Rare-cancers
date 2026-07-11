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

## 2026-07-11 — v0.3 CI data pipeline: GEO reprocessed + primary full-text verified

Ran the atlas-data.yml workflow (GitHub Actions — the dev sandbox proxy blocks GEO/PMC). Results
folded in with provenance.

**Expression reprocessing (`expression_reprocess.py`):**
- **GSE24369 / GPL6244 (6 EMC vs 36 sarcoma, 23,072 genes): a real reproduction of known EMC biology.**
  Rank-based AUC=P(EMC>other): **NMB 1.00 (rank 11)**, **CHRNA6 1.00 (rank 26)**, SOX9 0.92, **RET 0.86**,
  NR4A3 0.82, PPARG 0.75 — all EMC-up. Leave-one-out top-50 Jaccard 0.64 (n=6). → claim C018;
  GSE24369 citation flipped to **verified**. A strategy success criterion (recover known EMC features) met.
- **GSE4303**: 7 legacy custom two-colour platforms (GPL3290 has 10 EMC vs 6 other) but NONE expose a
  standard probe→symbol column → 0 genes annotatable. Honest limitation; GSE4303 stays unverified.

**Primary full-text verification (`fulltext_verify.py`, EuropePMC):**
- **Iwata 2025 (NCC)** — primary abstract NAMES brigatinib/panobinostat/romidepsin + 221 drugs + EWSR1::NR4A3
  → NCC screen hits upgraded to VERIFIED_primary_abstract.
- **Sunitinib (Stacchiotti 2014)** — primary abstract EXPLICITLY states responders expressed EWSR1::NR4A3,
  refractory carried TAF15::NR4A3 → claim C019; the EWSR1-vs-TAF15 antiangiogenic biomarker is now
  primary-confirmed (AXIS-antiangiogenic fusion_subtype_coverage 2→3, composite 18→19).
- **Pazopanib** 18% (95% CI 1-36); **anthracycline** 4/11 PR (40%); **Masunaga registry** margin HR 4.76
  (95% CI 1.72-13.15) — all upgraded to primary-abstract confirmed with exact numbers.
- **Bangerter (USZ)** — the EuropePMC abstract is GENERIC (no compound names); **HDM201 stays uncorroborated**
  and carfilzomib/PU-H71 stay snippet-level (Human Cell not OA). Recorded honestly.

**Infra lessons (folded into CLAUDE.md rule):** egress-proxy 403 → route via a CI runner. Debugging cost
three iterations: (1) OOM from decompressing GSE24369's GPL SOFT whole → stream it; a cancelled job skips
the always() commit → per-unit checkpoint-commits; (2) divide-by-zero lost the dataset → isolate signature +
diagnostics; (3) 0 genes annotated → parse Affymetrix gene_assignment columns + per-file platform id.

## 2026-07-11 — v0.4 four-workstream expansion (A/B/C/D)

- **A (collaborator brief):** `collaborator-brief.md` — 2-page package (proteostasis-chromatin program +
  EWSR1-vs-TAF15 antiangiogenic biomarker + what-we-bring/ask + honest limits) for wet-lab recruitment.
- **B (panel dependency, CI):** `panel_dependency.py` → DepMap 24Q4 dependency of the 12-compound panel's
  target genes (91 sarcoma lines). **Key honest reframes (claim C020):** proteasome/XPO1/HDAC3 PAN-ESSENTIAL
  (window = pharmacology, not genetic selectivity); ALL TKI kinases non-essential (antiangiogenic mechanism
  is non-tumor-autonomous; ALK GE −0.05 kills brigatinib=ALK); **BCL2 non-essential — BCL-xL/MCL1 are the
  real apoptotic nodes, so venetoclax may be the wrong BH3-mimetic.** Folded into 4 scored entities +
  validation panel. Self-validated (NR4A3 non-essential, BRD9 synovial-selective).
- **D (antiangiogenic mechanism):** `antiangiogenic-mechanism.md` — kinome-level TKI target-set comparison
  (which inhibited-kinase set matches EWSR1-responders; brigatinib as a built-in negative control; selective
  RET inhibitor as the clean RET test) + a response-linked common data model / CRF with growth-rate-adjusted
  endpoints.
- **C (antigen TAF15):** DONE — `antigen_expand.py` runs BOTH junctions through MHC-I (claim C021).
  TAF15::NR4A3: 1 strong / 7 sub-500nM of 34 novel peptides; EWSR1: 2 strong / 3 sub-500nM. **Both modest**
  -> neither common junction is a strong shared class-I target (redirects to lineage antigens). Axis
  fusion_subtype_coverage 1→2. MHC-II deferred (MHCnuggets TF-pin clash; tool exists for a follow-up).

## Open next steps (all no-wet-lab, mostly free/cheap)
0. **DONE this session:** GSE24369 reprocessed (verified); primary full-text pass; panel DepMap dependency (C020); brief (A); antiangiogenic mechanism+CRF (D); TAF15 junction antigen (C, C021).
1. **MHC-II help epitopes** for both junctions (patient_cd4_epitopes.py / MHCnuggets, isolated venv) — the one antigen piece deferred this session.
2. **Exposure numbers:** populate cited unbound-Cmax for the 12 panel compounds (the window is now shown to be pharmacology-limited, so this matters most for proteostasis).
3. **GSE4303** needs a bespoke clone-ID→symbol crosswalk (custom two-colour GPLs); or drop as superseded.
4. **Lineage-antigen screen** (B7-H3/PRAME/CHRNA6 in EMC tissue/immunopeptidomics) — the redirect target from the modest junction yield; needs collaborator tissue. (raw CEL → QC → EMC-vs-sarcoma + EWSR1-vs-TAF15 signatures,
   leave-one-sample-out, rank-based meta-analysis). Flips the 2 unverified GEO citations to verified.
2. **Full-text re-confirmation pass** when PMC access is available: IC50 numbers, HDM201 status,
   per-model synergy wording, NCC-EMC1-C1 fusion, unbound-Cmax exposure numbers.
3. **Fold in the fusion-junction antigen computation** (strategy Project 4) as a parallel axis —
   the repo already has `fusion_neoantigen.py` / `hla_coverage.py` outputs to register.
4. **Populate `achievable_free_exposure`** with cited unbound-Cmax values for the 12 panel compounds.
