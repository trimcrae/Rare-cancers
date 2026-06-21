# Fact-check & replication log — novel-modalities.md

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
| 34 novel junction-spanning peptides | n_novel_spanning_peptides | ✓ |
| 5 binders (≤2 %ile), 2 strong (≤0.5); 3 ≤500 nM | n_predicted_binders_* | ✓ |
| Lead GQQPCVQAQY B*15:01 44.6 nM, %ile 0.07, score 0.94 | top_predictions[0] | ✓ |
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
- Breakpoint-resolved truth: 7 in-frame junctions (EWSR1 e7/9/10/11/12/13 → mostly NR4A3
  e3), 26 distinct predicted binders, **no pan-EMC epitope** (most-shared GVVRTDSLK in
  2/7, weak). Strong binders are breakpoint-specific (e.g. QQIVRTDSL/B*08:01 from the
  commonly-reported e7::e3). Honest conclusion: personalised, not off-the-shelf. ✓
- **HLA coverage — NOT fabricated.** `hla_coverage.py` attempted AFND retrieval in CI;
  AFND returns only its interactive search form (no data: n_decimals=0, no DataTable), so
  no precise coverage % is reported. Stated qualitatively instead (presenting alleles
  A*02:01/A*11:01/B*07:02/B*08:01 are among the most common worldwide). `_source_status`
  records this. ✓ (honest gap, flagged as AFND/IEDB next step)
- Treatment-precedent DOIs (CI-confirmed): KEYNOTE-942/mRNA-4157 `10.1016/S0140-6736(23)02268-7`
  (Lancet 2024); autogene cevumeran/Rojas `10.1038/s41586-023-06063-y` (Nature 2023). ✓

## Honesty boundaries (claims we deliberately do NOT make)
- No named drug/PROTAC/validated epitope as "the therapy" — would be fabrication.
- Breakpoint is modelled (flagged in every JSON `_breakpoint_model`); per-patient junction
  must be re-run. The neoantigen lead is therefore conditional on this breakpoint + HLA.
- AlphaFold "no pocket" is a hypothesis-grade prior, not experimental proof; cryptic pockets
  can exist. MHC binding ≠ immunogenicity. No EMC line exists in DepMap (screen must be run).
