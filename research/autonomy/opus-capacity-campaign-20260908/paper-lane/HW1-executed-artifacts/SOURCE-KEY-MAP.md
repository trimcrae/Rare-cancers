# SOURCE-KEY-MAP — every number in `AFTER-block.md`

Two artifacts only, both read at HEAD `d775c80f8e64bc64b67e8c2fb46edeaa2cca2911`:
`H` = `research/modalities/hla-coverage.json`, `C` = `research/modalities/coverage-curve.json`.
Percentages are the leaf × 100 rendered to two decimals; no other transformation is applied.
Rows marked **RETAINED / NOT RE-VERIFIED** are numbers carried over verbatim from the existing
manuscript whose source lies outside these two artifacts — they were not checked in this pass.

## A. Prose numbers (Abstract, §2, §3.1, §3.2, §3.3, §4)

| Printed value | Artifact | Exact key path |
|---|---|---|
| `8.51%` | H | `global.coverage_e7e3_public` |
| `8.26–8.76%` | H | `global.coverage_e7e3_public_95ci` |
| `27.37%` | H | `global.coverage_any_strong_binder_allele` |
| `26.63–28.14%` | H | `global.coverage_any_strong_binder_allele_95ci` |
| `6.49%` | H | `global.coverage_cd4_classii` |
| `6.30–6.70%` | H | `global.coverage_cd4_classii_95ci` |
| `1.78%` (no interval printed) | H | `global.coverage_cd8_and_cd4_combined` (no `_95ci` key exists) |
| `B*15:01`, "one allele" | H | `global.e7e3_public_epitope_alleles` (length 1) |
| `A*01:01, B*07:02, B*15:01`, "three alleles" | H | `global.all_strong_binder_alleles` (length 3) |
| `DRB1*14:01`, "exactly one" | H | `global.class_ii_cd4_helper_alleles` (length 1) |
| "exactly **four** alleles — three class I and one class II" | H | `global.allele_frequencies` (4 keys) |
| `23-allele class-II panel` | H | `_class_ii_note` (states "23-allele class-II panel" and enumerates them) |
| `P(>=1 class-I allele) x P(>=1 class-II allele)` | H | `_class_ii_note` (verbatim) |
| af / Wilson / carrier / coverage formula statements | H | `_method` (verbatim) |
| AFND mirror URL and status | H | `_source_urls.allele_frequencies`, `_source_status` |
| ISO 3166 / UN M49 mapping source | H | `_source_urls.region_mapping`, `_region_mapping.scheme` |
| `0` unassigned populations | H | `_region_mapping.unassigned_populations` |
| `0` unassigned individuals | H | `_region_mapping.unassigned_individuals` |
| "16 UN M49 sub-regions" | H | `regions` (16 keys) |
| `QYSQQSSSYGQQ\|NMPCVQAQYSPS` | H | `⛔_class_ii_provenance.class_ii_junction_context` |
| `SQQSSSYGQQ\|NMPCVQAQYSP` | H | `⛔_class_ii_provenance.corrected_junction_context` |
| `matches_corrected_seam: true` | H | `⛔_class_ii_provenance.matches_corrected_seam` |
| `60.43%` / `55.93–64.95%` (Northern Europe, any-strong) | H | `regions["Northern Europe"].coverage_any_strong_binder_allele{,_95ci}` |
| `1.37%` / `0.54–3.49%` (Melanesia, any-strong) | H | `regions["Melanesia"].coverage_any_strong_binder_allele{,_95ci}` |
| Micronesia class-I `UNKNOWN` | H | `regions["Micronesia"].coverage_any_strong_binder_allele` = `null`; `.coverage_e7e3_public` = `null`; all three `allele_frequencies` entries `null` |
| `15.40%` / `14.66–16.17%` (Eastern Asia, e7::e3) | H | `regions["Eastern Asia"].coverage_e7e3_public{,_95ci}` |
| `0.76%` / `0.26–2.19%` (Northern Africa, e7::e3) | H | `regions["Northern Africa"].coverage_e7e3_public{,_95ci}` |
| Polynesia e7::e3 `UNKNOWN` | H | `regions["Polynesia"].coverage_e7e3_public` = `null` |
| `1.95%` / `0.34–10.41%` (Polynesia, any-strong, one allele) | H | `regions["Polynesia"].coverage_any_strong_binder_allele{,_95ci}`, `.coverage_all_alleles_used` = `["B*07:02"]` |
| Melanesia "two-allele figure" | H | `regions["Melanesia"].coverage_all_alleles_used` (length 2) |
| `9.84%` (Eastern Asia CD4) | H | `regions["Eastern Asia"].coverage_cd4_classii` |
| `2.46%` (Northern Africa CD4) | H | `regions["Northern Africa"].coverage_cd4_classii` |
| `14.33%` (Australia and New Zealand CD4) | H | `regions["Australia and New Zealand"].coverage_cd4_classii` |
| `129` / `2` (Micronesia) | H | `regions["Micronesia"].max_total_individuals`, `.max_n_populations` |
| `450` / `9` (Polynesia) | H | `regions["Polynesia"].max_total_individuals`, `.max_n_populations` |
| `702` / `8` (Australia and New Zealand) | H | `regions["Australia and New Zealand"].max_total_individuals`, `.max_n_populations` |
| `1,269` / `19` (Melanesia) | H | `regions["Melanesia"].max_total_individuals`, `.max_n_populations` |
| `17,277` / `113` (Latin America and the Caribbean) | H | `regions["Latin America and the Caribbean"].max_total_individuals`, `.max_n_populations` |
| `34` (panel size) | C | `panel_size` |
| `4` (presenting alleles) | C | `n_presenting_alleles` |
| `A*01:01, A*30:02, B*07:02, B*15:01` | C | `presenting_alleles` |
| `6.41%` / `12.41%` (step 1) | C | `global_curve[0].af`, `global_curve[0].cumulative_coverage` |
| `4.80%` / `20.62%` (step 2) | C | `global_curve[1].af`, `global_curve[1].cumulative_coverage` |
| `4.35%` / `27.37%` (step 3) | C | `global_curve[2].af`, `global_curve[2].cumulative_coverage` |
| `2.11%` / `30.40%` (step 4) | C | `global_curve[3].af`, `global_curve[3].cumulative_coverage` |
| `30.40%` (`global_max_coverage`) | C | `global_max_coverage` |
| all four global thresholds `null` | C | `global_alleles_to_reach.{50pct,80pct,90pct,95pct}` |
| `2` (Northern Europe alleles to 50%) | C | `regions["Northern Europe"].alleles_to_reach.50pct` |
| `61.10%` (Northern Europe max) | C | `regions["Northern Europe"].max_coverage` |
| `42.28%` (Western Europe max) | C | `regions["Western Europe"].max_coverage` |
| "no region reaches 80/90/95%" | C | `regions[*].alleles_to_reach.{80pct,90pct,95pct}` all `null` (15 regions) |

## B. RETAINED / NOT RE-VERIFIED (source outside the two artifacts; carried over verbatim)

| Printed value | Where | Status |
|---|---|---|
| `0.495` best cavity druggability (§1) | pre-existing §1 text, sourced to `novel-modalities.md` §2 | RETAINED, not re-verified in this pass |
| `27 aa`, `15 aa`, `2` CD8 epitopes, `1` CD4 helper, peptide sequences (§3.4) | pre-existing §3.4 text, sourced to `vaccine-construct.json` | RETAINED, explicitly flagged in §3.4 as NOT re-verified; allele identities B*15:01 / DRB1*14:01 *are* consistent with H |
| `2026-08-07` (transcript-model rebuild date) | supersession record | RETAINED from the manuscript's own banner, now in `HISTORY-superseded.md` |

## C. Table cells — §3.1 global per-allele table and §3.2 regional table

Auto-generated one row per printed cell.

| Printed value | Artifact | Exact key path |
|---|---|---|
| `6.41%` | H | `global.allele_frequencies["HLA-A*01:01"].allele_frequency` |
| `6.22–6.60%` | H | `global.allele_frequencies["HLA-A*01:01"].af_95ci` |
| `12.40%` | H | `global.allele_frequencies["HLA-A*01:01"].carrier_frequency` |
| `210` | H | `global.allele_frequencies["HLA-A*01:01"].n_populations` |
| `32,777` | H | `global.allele_frequencies["HLA-A*01:01"].total_individuals` |
| `4.80%` | H | `global.allele_frequencies["HLA-B*07:02"].allele_frequency` |
| `4.64–4.98%` | H | `global.allele_frequencies["HLA-B*07:02"].af_95ci` |
| `9.38%` | H | `global.allele_frequencies["HLA-B*07:02"].carrier_frequency` |
| `175` | H | `global.allele_frequencies["HLA-B*07:02"].n_populations` |
| `30,647` | H | `global.allele_frequencies["HLA-B*07:02"].total_individuals` |
| `4.35%` | H | `global.allele_frequencies["HLA-B*15:01"].allele_frequency` |
| `4.22–4.48%` | H | `global.allele_frequencies["HLA-B*15:01"].af_95ci` |
| `8.50%` | H | `global.allele_frequencies["HLA-B*15:01"].carrier_frequency` |
| `265` | H | `global.allele_frequencies["HLA-B*15:01"].n_populations` |
| `45,574` | H | `global.allele_frequencies["HLA-B*15:01"].total_individuals` |
| `3.30%` | H | `global.allele_frequencies["DRB1*14:01"].allele_frequency` |
| `3.20–3.41%` | H | `global.allele_frequencies["DRB1*14:01"].af_95ci` |
| `6.50%` | H | `global.allele_frequencies["DRB1*14:01"].carrier_frequency` |
| `365` | H | `global.allele_frequencies["DRB1*14:01"].n_populations` |
| `53,005` | H | `global.allele_frequencies["DRB1*14:01"].total_individuals` |
| `UNKNOWN (null leaf)` | H | `regions["Micronesia"].coverage_e7e3_public` |
| `— (null leaf)` | H | `regions["Micronesia"].coverage_e7e3_public_95ci` |
| `UNKNOWN (null leaf)` | H | `regions["Micronesia"].coverage_any_strong_binder_allele` |
| `— (null leaf)` | H | `regions["Micronesia"].coverage_any_strong_binder_allele_95ci` |
| `6.86%` | H | `regions["Micronesia"].coverage_cd4_classii` |
| `3.67–12.58%` | H | `regions["Micronesia"].coverage_cd4_classii_95ci` |
| `none` | H | `regions["Micronesia"].coverage_all_alleles_used` |
| `129` | H | `regions["Micronesia"].max_total_individuals` |
| `2` | H | `regions["Micronesia"].max_n_populations` |
| `16.11%` | H | `regions["Northern Europe"].coverage_e7e3_public` |
| `13.83–18.71%` | H | `regions["Northern Europe"].coverage_e7e3_public_95ci` |
| `60.43%` | H | `regions["Northern Europe"].coverage_any_strong_binder_allele` |
| `55.93–64.95%` | H | `regions["Northern Europe"].coverage_any_strong_binder_allele_95ci` |
| `4.10%` | H | `regions["Northern Europe"].coverage_cd4_classii` |
| `3.23–5.17%` | H | `regions["Northern Europe"].coverage_cd4_classii_95ci` |
| `A\*01:01, B\*07:02, B\*15:01` | H | `regions["Northern Europe"].coverage_all_alleles_used` |
| `1,598` | H | `regions["Northern Europe"].max_total_individuals` |
| `9` | H | `regions["Northern Europe"].max_n_populations` |
| `8.24%` | H | `regions["Western Europe"].coverage_e7e3_public` |
| `7.32–9.27%` | H | `regions["Western Europe"].coverage_e7e3_public_95ci` |
| `41.57%` | H | `regions["Western Europe"].coverage_any_strong_binder_allele` |
| `38.99–44.28%` | H | `regions["Western Europe"].coverage_any_strong_binder_allele_95ci` |
| `6.86%` | H | `regions["Western Europe"].coverage_cd4_classii` |
| `6.12–7.67%` | H | `regions["Western Europe"].coverage_cd4_classii_95ci` |
| `A\*01:01, B\*07:02, B\*15:01` | H | `regions["Western Europe"].coverage_all_alleles_used` |
| `4,045` | H | `regions["Western Europe"].max_total_individuals` |
| `11` | H | `regions["Western Europe"].max_n_populations` |
| `7.09%` | H | `regions["Eastern Europe"].coverage_e7e3_public` |
| `5.64–8.91%` | H | `regions["Eastern Europe"].coverage_e7e3_public_95ci` |
| `37.03%` | H | `regions["Eastern Europe"].coverage_any_strong_binder_allele` |
| `32.39–42.15%` | H | `regions["Eastern Europe"].coverage_any_strong_binder_allele_95ci` |
| `8.28%` | H | `regions["Eastern Europe"].coverage_cd4_classii` |
| `7.28–9.43%` | H | `regions["Eastern Europe"].coverage_cd4_classii_95ci` |
| `A\*01:01, B\*07:02, B\*15:01` | H | `regions["Eastern Europe"].coverage_all_alleles_used` |
| `2,456` | H | `regions["Eastern Europe"].max_total_individuals` |
| `32` | H | `regions["Eastern Europe"].max_n_populations` |
| `5.95%` | H | `regions["Southern Europe"].coverage_e7e3_public` |
| `5.11–6.92%` | H | `regions["Southern Europe"].coverage_e7e3_public_95ci` |
| `32.12%` | H | `regions["Southern Europe"].coverage_any_strong_binder_allele` |
| `29.32–35.12%` | H | `regions["Southern Europe"].coverage_any_strong_binder_allele_95ci` |
| `6.34%` | H | `regions["Southern Europe"].coverage_cd4_classii` |
| `5.75–6.97%` | H | `regions["Southern Europe"].coverage_cd4_classii_95ci` |
| `A\*01:01, B\*07:02, B\*15:01` | H | `regions["Southern Europe"].coverage_all_alleles_used` |
| `5,982` | H | `regions["Southern Europe"].max_total_individuals` |
| `36` | H | `regions["Southern Europe"].max_n_populations` |
| `7.96%` | H | `regions["Northern America"].coverage_e7e3_public` |
| `7.22–8.76%` | H | `regions["Northern America"].coverage_e7e3_public_95ci` |
| `31.60%` | H | `regions["Northern America"].coverage_any_strong_binder_allele` |
| `29.59–33.72%` | H | `regions["Northern America"].coverage_any_strong_binder_allele_95ci` |
| `4.94%` | H | `regions["Northern America"].coverage_cd4_classii` |
| `4.37–5.58%` | H | `regions["Northern America"].coverage_cd4_classii_95ci` |
| `A\*01:01, B\*07:02, B\*15:01` | H | `regions["Northern America"].coverage_all_alleles_used` |
| `5,478` | H | `regions["Northern America"].max_total_individuals` |
| `23` | H | `regions["Northern America"].max_n_populations` |
| `2.60%` | H | `regions["Western Asia"].coverage_e7e3_public` |
| `1.69–3.98%` | H | `regions["Western Asia"].coverage_e7e3_public_95ci` |
| `27.83%` | H | `regions["Western Asia"].coverage_any_strong_binder_allele` |
| `23.46–33.06%` | H | `regions["Western Asia"].coverage_any_strong_binder_allele_95ci` |
| `6.20%` | H | `regions["Western Asia"].coverage_cd4_classii` |
| `5.33–7.19%` | H | `regions["Western Asia"].coverage_cd4_classii_95ci` |
| `A\*01:01, B\*07:02, B\*15:01` | H | `regions["Western Asia"].coverage_all_alleles_used` |
| `2,543` | H | `regions["Western Asia"].max_total_individuals` |
| `23` | H | `regions["Western Asia"].max_n_populations` |
| `3.98%` | H | `regions["Southern Asia"].coverage_e7e3_public` |
| `3.08–5.11%` | H | `regions["Southern Asia"].coverage_e7e3_public_95ci` |
| `25.11%` | H | `regions["Southern Asia"].coverage_any_strong_binder_allele` |
| `22.21–28.43%` | H | `regions["Southern Asia"].coverage_any_strong_binder_allele_95ci` |
| `6.65%` | H | `regions["Southern Asia"].coverage_cd4_classii` |
| `5.89–7.49%` | H | `regions["Southern Asia"].coverage_cd4_classii_95ci` |
| `A\*01:01, B\*07:02, B\*15:01` | H | `regions["Southern Asia"].coverage_all_alleles_used` |
| `3,580` | H | `regions["Southern Asia"].max_total_individuals` |
| `26` | H | `regions["Southern Asia"].max_n_populations` |
| `4.98%` | H | `regions["Australia and New Zealand"].coverage_e7e3_public` |
| `3.33–7.36%` | H | `regions["Australia and New Zealand"].coverage_e7e3_public_95ci` |
| `23.88%` | H | `regions["Australia and New Zealand"].coverage_any_strong_binder_allele` |
| `18.93–29.96%` | H | `regions["Australia and New Zealand"].coverage_any_strong_binder_allele_95ci` |
| `14.33%` | H | `regions["Australia and New Zealand"].coverage_cd4_classii` |
| `11.88–17.19%` | H | `regions["Australia and New Zealand"].coverage_cd4_classii_95ci` |
| `A\*01:01, B\*07:02, B\*15:01` | H | `regions["Australia and New Zealand"].coverage_all_alleles_used` |
| `702` | H | `regions["Australia and New Zealand"].max_total_individuals` |
| `8` | H | `regions["Australia and New Zealand"].max_n_populations` |
| `0.76%` | H | `regions["Northern Africa"].coverage_e7e3_public` |
| `0.26–2.19%` | H | `regions["Northern Africa"].coverage_e7e3_public_95ci` |
| `21.20%` | H | `regions["Northern Africa"].coverage_any_strong_binder_allele` |
| `16.34–27.84%` | H | `regions["Northern Africa"].coverage_any_strong_binder_allele_95ci` |
| `2.46%` | H | `regions["Northern Africa"].coverage_cd4_classii` |
| `1.79–3.35%` | H | `regions["Northern Africa"].coverage_cd4_classii_95ci` |
| `A\*01:01, B\*07:02, B\*15:01` | H | `regions["Northern Africa"].coverage_all_alleles_used` |
| `1,537` | H | `regions["Northern Africa"].max_total_individuals` |
| `15` | H | `regions["Northern Africa"].max_n_populations` |
| `7.84%` | H | `regions["Latin America and the Caribbean"].coverage_e7e3_public` |
| `7.46–8.24%` | H | `regions["Latin America and the Caribbean"].coverage_e7e3_public_95ci` |
| `21.09%` | H | `regions["Latin America and the Caribbean"].coverage_any_strong_binder_allele` |
| `19.33–23.00%` | H | `regions["Latin America and the Caribbean"].coverage_any_strong_binder_allele_95ci` |
| `3.17%` | H | `regions["Latin America and the Caribbean"].coverage_cd4_classii` |
| `2.80–3.61%` | H | `regions["Latin America and the Caribbean"].coverage_cd4_classii_95ci` |
| `A\*01:01, B\*07:02, B\*15:01` | H | `regions["Latin America and the Caribbean"].coverage_all_alleles_used` |
| `17,277` | H | `regions["Latin America and the Caribbean"].max_total_individuals` |
| `113` | H | `regions["Latin America and the Caribbean"].max_n_populations` |
| `2.01%` | H | `regions["Sub-Saharan Africa"].coverage_e7e3_public` |
| `1.43–2.82%` | H | `regions["Sub-Saharan Africa"].coverage_e7e3_public_95ci` |
| `20.39%` | H | `regions["Sub-Saharan Africa"].coverage_any_strong_binder_allele` |
| `18.08–23.02%` | H | `regions["Sub-Saharan Africa"].coverage_any_strong_binder_allele_95ci` |
| `2.27%` | H | `regions["Sub-Saharan Africa"].coverage_cd4_classii` |
| `1.65–3.08%` | H | `regions["Sub-Saharan Africa"].coverage_cd4_classii_95ci` |
| `A\*01:01, B\*07:02, B\*15:01` | H | `regions["Sub-Saharan Africa"].coverage_all_alleles_used` |
| `3,066` | H | `regions["Sub-Saharan Africa"].max_total_individuals` |
| `27` | H | `regions["Sub-Saharan Africa"].max_n_populations` |
| `15.40%` | H | `regions["Eastern Asia"].coverage_e7e3_public` |
| `14.66–16.17%` | H | `regions["Eastern Asia"].coverage_e7e3_public_95ci` |
| `19.96%` | H | `regions["Eastern Asia"].coverage_any_strong_binder_allele` |
| `18.63–21.37%` | H | `regions["Eastern Asia"].coverage_any_strong_binder_allele_95ci` |
| `9.84%` | H | `regions["Eastern Asia"].coverage_cd4_classii` |
| `9.33–10.39%` | H | `regions["Eastern Asia"].coverage_cd4_classii_95ci` |
| `A\*01:01, B\*07:02, B\*15:01` | H | `regions["Eastern Asia"].coverage_all_alleles_used` |
| `11,585` | H | `regions["Eastern Asia"].max_total_individuals` |
| `68` | H | `regions["Eastern Asia"].max_n_populations` |
| `3.67%` | H | `regions["South-eastern Asia"].coverage_e7e3_public` |
| `3.02–4.45%` | H | `regions["South-eastern Asia"].coverage_e7e3_public_95ci` |
| `14.04%` | H | `regions["South-eastern Asia"].coverage_any_strong_binder_allele` |
| `12.09–16.29%` | H | `regions["South-eastern Asia"].coverage_any_strong_binder_allele_95ci` |
| `5.87%` | H | `regions["South-eastern Asia"].coverage_cd4_classii` |
| `5.15–6.68%` | H | `regions["South-eastern Asia"].coverage_cd4_classii_95ci` |
| `A\*01:01, B\*07:02, B\*15:01` | H | `regions["South-eastern Asia"].coverage_all_alleles_used` |
| `3,556` | H | `regions["South-eastern Asia"].max_total_individuals` |
| `29` | H | `regions["South-eastern Asia"].max_n_populations` |
| `UNKNOWN (null leaf)` | H | `regions["Polynesia"].coverage_e7e3_public` |
| `— (null leaf)` | H | `regions["Polynesia"].coverage_e7e3_public_95ci` |
| `1.95%` | H | `regions["Polynesia"].coverage_any_strong_binder_allele` |
| `0.34–10.41%` | H | `regions["Polynesia"].coverage_any_strong_binder_allele_95ci` |
| `6.76%` | H | `regions["Polynesia"].coverage_cd4_classii` |
| `4.82–9.46%` | H | `regions["Polynesia"].coverage_cd4_classii_95ci` |
| `B\*07:02` | H | `regions["Polynesia"].coverage_all_alleles_used` |
| `450` | H | `regions["Polynesia"].max_total_individuals` |
| `9` | H | `regions["Polynesia"].max_n_populations` |
| `0.86%` | H | `regions["Melanesia"].coverage_e7e3_public` |
| `0.36–2.01%` | H | `regions["Melanesia"].coverage_e7e3_public_95ci` |
| `1.37%` | H | `regions["Melanesia"].coverage_any_strong_binder_allele` |
| `0.54–3.49%` | H | `regions["Melanesia"].coverage_any_strong_binder_allele_95ci` |
| `7.26%` | H | `regions["Melanesia"].coverage_cd4_classii` |
| `5.99–8.82%` | H | `regions["Melanesia"].coverage_cd4_classii_95ci` |
| `B\*07:02, B\*15:01` | H | `regions["Melanesia"].coverage_all_alleles_used` |
| `1,269` | H | `regions["Melanesia"].max_total_individuals` |
| `19` | H | `regions["Melanesia"].max_n_populations` |
