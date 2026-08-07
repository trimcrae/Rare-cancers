---
id: DOC-NOVEL-MODALITIES-FACTCHECK
title: Fact-check & replication log — novel-modalities.md
level: L3
kind: manuscript
status: live
canonical_for: []
purpose: See the document body; purpose was not stated separately when frontmatter was backfilled.
scope: Scope not separately declared. Inferred kind `manuscript` from its location under research/manuscripts/.
audience: [maintainers, external reviewers, autonomous research agents]
date: 2026-08-05
last_verified: unverified
_backfilled: true
---
# Fact-check & replication log — novel-modalities.md

> **QA / FACT-CHECK LOG (not a manuscript)** for [`novel-modalities.md`](./novel-modalities.md).
> Active manuscript: [`emc-treatment-roadmap.md`](./emc-treatment-roadmap.md). Folder map: [`README.md`](./README.md).

Reviewer-grade verification trail for the computational target-assessment paper.
✓ = verified/reproduced; ⚠ = needs confirmation a hostile reviewer could demand;
✗→✓ = found wrong and fixed. Every number in the manuscript traces to a CI-produced
JSON on the `modalities-cache` branch (snapshotted into `research/modalities/`).

## Replication (deterministic; re-run via `.github/workflows/modalities-run.yml`)
- `nr4a3_structure.py` — AlphaFold (AFDB) models for Q92570/Q01844 + fpocket. Inputs are
  immutable public records; output reproduces. ✓
- `fusion_neoantigen.py` — UniProt sequences + MHCflurry-2.0. Deterministic given the
  pinned model bundle; records `_rank_column_used` + `_mhcflurry_columns` for audit. ✓
- `junction_aso.py` — RefSeq CDS (NM_005243, NM_006981) + deterministic gapmer tiling. ✓
- Publishing is `if: always()` with `continue-on-error` analyses, so a partial/failed run
  publishes whatever computed instead of silently dropping output. ✓

## Bugs caught and fixed (the important part)
- **✗→✓ Silent percentile-default → false "0 binders".** First neoantigen run reported
  0 MHC-I binders. A provenance check (`_mhcflurry_columns`) showed this MHCflurry build
  emits `presentation_percentile` + raw `affinity`, **not** `affinity_percentile`; my code
  defaulted every rank to 100. Fixed to rank on `presentation_percentile` (+ raw-affinity
  cross-check). **The real result is the opposite of the artifact:** 5 binders, 2 strong;
  lead **GQQPCVQAQY** strong on HLA-B*15:01 (44.6 nM, presentation %ile 0.07). This is the
  single most consequential catch in this paper — without it the immunotherapy section
  would have wrongly been declared dead.
- **✗→✓ AlphaFold 404.** Hard-coded `AF-{acc}-F1-model_v4.pdb` URL 404'd; switched to the
  AFDB prediction API which returns the correct `pdbUrl` (version-robust).
- **✗→✓ fpocket `volume` mis-parsed** (~5 instead of Å³, wrong field across fpocket
  versions). Dropped from output; druggability (the headline) parses unambiguously and is
  retained. Added top-pocket→domain localisation instead.

## Key numeric claims (source = CI JSON on modalities-cache)
| Claim (manuscript) | Source field | Status |
|---|---|---|
| EWSR1 SYGQ 1–264 disordered: mean pLDDT 38.8, 98.1% <50 | `…structure…json` EWSR1.regions | ✓ |
| NR4A3 AF1 1–260 disordered: 37.7, 96.5% <50 | NR4A3.regions | ✓ |
| NR4A3 LBD 373–626 folded: mean pLDDT 85.0, 9.1% <50 | NR4A3.regions | ✓ |
| NR4A3 DBD 261–337: mean pLDDT 76.1 | NR4A3.regions | ✓ |
| 33 fpocket cavities; max druggability 0.495 (sub-0.5) | NR4A3.fpocket | ✓ |
| Top pocket localises to LBD, residues 406–534 (all LBD) | top_pocket_locale | ✓ |
| 34 novel junction-spanning peptides | n_novel_spanning_peptides | ⛔ superseded — **38** at the corrected junction |
| 5 binders (≤2 %ile), 2 strong (≤0.5); 3 ≤500 nM | n_predicted_binders_* | ⛔ superseded — **3** binders, **2** strong, **3** ≤500 nM |
| Lead GQQPCVQAQY B*15:01 44.6 nM, %ile 0.07, score 0.94 | top_predictions[0] | ⛔ superseded — lead is **NMPCVQAQY** B*15:01 73.4 nM, %ile 0.374, score 0.74 |

> ⛔ **THOSE THREE ROWS ARE SUPERSEDED, RETAINED (2026-08-06), AND THE REASON MATTERS MORE THAN THE
> NUMBERS.** Each was a correct read of the field it names — which is precisely why a field-by-field
> factcheck could not catch what was wrong: the artifact was internally consistent and built on a
> chimera that could not exist. `fusion_neoantigen.py` spliced two UniProt PROTEIN sequences
> (EWSR1 1–264 :: NR4A3 from 2), and a protein-level splice cannot represent a codon split across the
> junction. EWSR1 exon 7 ends 1 nt past a codon boundary and NR4A3's acceptor exon retains 2 5′UTR nt,
> which compose into a **novel codon belonging to neither parent** (`AAT` = Asn), followed by NR4A3
> **Met1** — so the corrected seam is `…SQQSSSYGQQ-N-MPCVQAQYSP…`, two residues different, and
> `GQQPCVQAQY` does not occur in the corrected chimera at all. Regenerated from the mRNA junction on
> 2026-08-06 (MHCflurry 2.1.4, downloads release 2.2.0, recorded in the artifact's `_predictor`
> block): [`fusion-neoantigen-predictions.json`](../modalities/fusion-neoantigen-predictions.json).
> Grading and the checks that lifted the retraction:
> [`fusion-neoantigen-retraction.json`](../modalities/fusion-neoantigen-retraction.json) →
> `single_breakpoint_artifact.status == "CLEARED …"`. **A verification trail that checks values
> against fields cannot see a wrong object; only re-deriving the object can.**
| 5 fusion-specific gapmer ASOs; junction GC-rich (~75–81%) | `…aso…json` | ✓ |

## Reference DOIs (CI-resolved via Crossref in `verify-refs.yml` §4)
- ✓ Wang 2003 Nurr1 `10.1038/nature01645`; Varadi 2022 AFDB `10.1093/nar/gkab1061`;
  Le Guilloux 2009 fpocket `10.1186/1471-2105-10-168`; O'Donnell 2020 MHCflurry
  `10.1016/j.cels.2020.09.001`; Békés/Crews 2022 PROTAC `10.1038/s41573-021-00371-6`;
  Nabet 2018 dTAG `10.1038/s41589-018-0021-8`; Crooke 2021 ASO `10.1038/s41573-021-00162-z`.
- ✗→✓ "Kwon 2013" was a mislabel — the cited title belongs to **Nott 2015 Mol Cell**
  (`10.1016/j.molcel.2015.01.013`), which Crossref returned; corrected in the reference list.
- ✗→✓ Boulay 2017 *Cell* `10.1016/j.cell.2017.07.036` — first searches returned only the
  near-title AACR abstract (`10.1158/1538-7445.pedca17-pr09`); resolved by constraining
  author + journal + year (verify-refs §5), CI-confirmed container=Cell, year 2017.
- ✗→✓ Jumper 2021 AlphaFold *Nature* `10.1038/s41586-021-03819-2` — first searches
  returned same-field decoys (a Nat Methods AlphaFold paper, a 2023 assembly paper);
  resolved + CI-confirmed container=Nature, year 2021 via the author-constrained query.
  (DOIs were taken from CI Crossref output, never asserted from memory.)

## Breakpoint-resolved redo (the biggest correction)
- **✗→✓ The headline neoepitope GQQPCVQAQY was an artifact of a guessed breakpoint.**
  `fusion_neoantigen.py` used one assumed junction (EWSR1 res 264 :: NR4A3 res 2).
  `fusion_breakpoints.py` derives the *real* in-frame junctions from Ensembl exon
  structure (self-check: translate(CDS)==Ensembl protein) and runs MHCflurry across all
  7 of them. GQQPCVQAQY arises from **none** of them — it was a guess artifact. Corrected
  in abstract + §3.3. Source: `fusion-breakpoint-neoantigens.json`.
  > ⛔ **THE CONCLUSION HELD; THE EVIDENCE FOR IT DID NOT (2026-08-06) — AND THE EVIDENCE HAS
  > NOW BEEN REBUILT (2026-08-07).** `GQQPCVQAQY` really does not occur in the corrected
  > chimera, but not for the reason given here. The seven junctions cited as "the *real*
  > in-frame junctions" all resumed NR4A3 at an offset the corrected exon map does not
  > produce. ⚠ And the obvious repair was not enough: fixing the exon index still left the
  > builder concatenating **CDS to CDS**, which discards the 2 nt of 5′UTR NR4A3's acceptor
  > exon 3 carries ahead of its ATG — so the CDS rule and the transcript rule select
  > **disjoint** junction sets. `fusion_breakpoints.py` is now built on the transcript model
  > and the artifact is regenerated; its banner is withheld by an independent re-derivation,
  > not by the file having been rewritten
  > (`fusion_neoantigen_invalidation._breakpoint_panel_clearance`). **A right answer reached
  > through a wrong instrument is not a verified answer**, and the 7-junction "breakpoint-
  > resolved truth" below — its 26 binders and `GVVRTDSLK`/`QQIVRTDSL` — **stays withdrawn in
  > full and is replaced, not restored.**
- ⚠ *Superseded, retained (withdrawn 2026-08-06, replaced 2026-08-07):* "Breakpoint-resolved
  truth: 7 in-frame junctions (EWSR1 e7/9/10/11/12/13 → mostly NR4A3 e3), 26 distinct
  predicted binders, no pan-EMC epitope (most-shared GVVRTDSLK in 2/7, weak). Strong binders
  are breakpoint-specific (e.g. QQIVRTDSL/B*08:01 from the commonly-reported e7::e3)."
- **Breakpoint-resolved truth, regenerated on the TRANSCRIPT model:** 27 declared exon pairs
  graded, **5** emittable (EWSR1 e7/9/10/12/13 → NR4A3 e3) and 22 explicit refusals; **11**
  distinct predicted binders, 4 strong; **no pan-EMC epitope** (most-shared `DMPCVQAQY` in
  **4/5**, weak — shared only because those four junctions produce the same Asp seam codon).
  **Every** strong binder is breakpoint-specific and **e9/e10/e12 return none at all**. e11
  is now a refusal, not a junction. Honest conclusion unchanged: personalised, not
  off-the-shelf — and the corrected data strengthens it. Source:
  `fusion-breakpoint-neoantigens.json`. ✓
- **HLA coverage — computed from real data, not fabricated.** `hla_coverage.py` pulls
  AFND allele frequencies in CI from the MIT-licensed `slowkow/allelefrequencies` mirror
  (AFND's own site serves only its interactive form to a non-browser client). Denominator
  (2N)-weighted global pooling + Wilson 95% CIs (per systems/POLICY-evidence.md). ⛔ **RECOMPUTED
  2026-08-07 on the corrected junction set — the allele set moved, so every class-I figure moved
  with it:** e7::e3 public junction (**B*15:01 alone**) = **8.51%** (95% CI 8.26–8.76%); any
  strong-binder allele across all resolved breakpoints (A*01:01/B*07:02/B*15:01) = **27.4%**
  (26.6–28.1%). Also pooled per UN M49 sub-region (AFND population→country→region via ISO 3166):
  any-strong coverage 1.4% (Melanesia) → 60% (Northern Europe); 0 populations unassigned.
  ⚠ *Superseded, retained: e7::e3 (A*11:01 + B*08:01) = **29.7%** (29.0–30.3%); any-strong
  (A*02:01/A*11:01/B*07:02/B*08:01/B*15:01) = **58.0%** (57.1–59.0%); regional 36% (Sub-Saharan
  Africa) → 79% (Northern Europe); CD8∧CD4 both-arms **16.5%**.* Class II: DRB1 helper alleles
  (DRB1*03:01/07:01, strong binders from `patient-cd4-demo.json`) compute to **28.4%** globally,
  but ⛔ **that arm and the combined both-arms figure are WITHHELD** — `patient-cd4-demo.json` is
  still built on the retracted seam (`…IVRTDSLKGRRG`) and has not been regenerated, so the file
  would otherwise mix a corrected class-I set with an uncorrected class-II one. `hla_coverage.py`
  now measures the mismatch and records it as `⛔_class_ii_provenance`. It remains a FLOOR in any
  case, because the class-II screen tested only a 3-allele DR panel (not fabricated up). The
  global number is the headline, the regional spread an equity caveat. If a source is unreachable
  the script records `source_unavailable` rather than guessing. Sources: `hla-coverage.json`,
  `hla-coverage-emc.md`. ✓
- Treatment-precedent DOIs (CI-confirmed): KEYNOTE-942/mRNA-4157 `10.1016/S0140-6736(23)02268-7`
  (Lancet 2024); autogene cevumeran/Rojas `10.1038/s41586-023-06063-y` (Nature 2023). ✓

## Patient-ready tools (TAF15 + CD4)
- **✓ TAF15::NR4A3 covered.** `patient_neoepitopes.py --partner TAF15` reuses the generic
  Ensembl machinery; CI demo found TAF15 exon 4 :: NR4A3 e3 in-frame → 6 presented / 3
  strong (e.g. SVVRTDSLK/A*11:01 37 nM). Source: `patient-neoepitopes-taf15-demo.json`.
- **✗→✓ CD4/class-II.** `patient_cd4_epitopes.py` (MHCnuggets) first failed —
  `Argument(s) not recognized: {'lr': 0.001}` — because MHCnuggets uses the old Keras
  `lr=` optimizer arg removed in Keras≥2.11 (forced by py3.11). Fixed by pinning a
  Python 3.10 + TensorFlow 2.10 micromamba env. CI demo (EWSR1 e7::e3 vs DRB1*15:01/
  03:01/07:01): 9 binders / 4 strong (e.g. SQYSQQSSSYGQQIV/DRB1*07:01 14.5 nM). Source:
  `patient-cd4-demo.json`. Both tools degrade gracefully (emit candidate peptides) when a
  predictor is unavailable, and carry not-a-device / screen-not-proof disclaimers.

## Honesty boundaries (claims we deliberately do NOT make)
- No named drug/PROTAC/validated epitope as "the therapy" — would be fabrication.
- Breakpoint is modelled (flagged in every JSON `_breakpoint_model`); per-patient junction
  must be re-run. The neoantigen lead is therefore conditional on this breakpoint + HLA.
- AlphaFold "no pocket" is a hypothesis-grade prior, not experimental proof; cryptic pockets
  can exist. MHC binding ≠ immunogenicity. No EMC line exists in DepMap (screen must be run).
