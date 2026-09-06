---
id: DOC-ATLAS-SAMPLE-ORGAN-RESULTS-20260906
title: Fixed-panel GSE28866 sample and normal-organ results
kind: memo
status: live
purpose: Report empirical peak-level heterogeneity and the next defensible atlas step.
scope: Exploratory descriptive secondary reanalysis, without independent validation or clinical claims.
audience: [maintainers, autonomous research agents]
date: 2026-09-06
last_verified: 2026-09-06
---

The recovered matrix justifies further bounded atlas analysis as a record of comparator and peak heterogeneity. It does not justify a standalone independently validated atlas paper or a therapeutic target claim. Pooled summaries conceal contrary histology, individual-sample and normal-organ directions. CHRNA6 does not reproduce a uniform EMC-high pattern in these four records. CSPG4 has the broadest positive median pattern in this fixed panel, while retaining substantial comparator and normal overlap. No additional genes were selected.

This closes the previous matrix-availability barrier for GSE28866 adult-organ and sarcoma contrasts. It does not close specimen independence, protein localization or validation barriers. The previous feasibility memo remains historical; its statement that sample-aligned full matrix values were unavailable is superseded for this source only. The old reader's description of four patients is unsupported: these are four named EMC sample/library records.

Protocol and source: [exact amended pre-outcome protocol](protocol-frozen.md.txt), [preserved original bytes](protocol-original.md.txt), [full source and output hashes](provenance.json). The final protocol SHA256 is 7429a89c8b9804fa956c43818d4e7cb4841ae69926ed3beca3b9e4c32a405f8d. The coordinator read it, verified the digest and approved computation after the three documented clarifications. That was a focused methods check, not ultra review or publication approval.

The source [GEO normalized matrix](https://ftp.ncbi.nlm.nih.gov/geo/series/GSE28nnn/GSE28866/suppl/GSE28866_36048_normalized_peaks_cancer_and_normal.txt.gz) is archived here verbatim: 13,018,555 bytes; SHA256 11dae64b2d6b6e77846c3f14971fc9a313da86eb52a4b8b83df96c23eedc0ffd. [Primary methods](https://link.springer.com/article/10.1186/gb-2012-13-8-r75) describe cancer-selected peaks and sample-depth scaling followed by square-root compression. All deltas below are differences on that supplied scale, not RNA fold changes.

All 36,048 rows have 100 fields: seven annotation fields and 93 library columns. Eighteen peaks map by exact symbol tokens to eleven of the twelve fixed genes; all eighteen are strict single-symbol mappings, with no discordant nonempty symbol fields. ALPP has no attributable peak under this mapping rule; this does not establish absent expression. All 1,674 selected library values are finite. Source zeros are observed peak values, not evidence that a gene or protein is absent. The full annotation inventory retains every unassigned row.

All 93 headers map uniquely to a GEO metadata record. Exactly ESS_STT5520_rep1/rep2 and LMS_STT516_rep1/rep2 were averaged, leaving 91 STT analysis units overall. Non-EMC sarcomas comprise ESS 4, EWS 4, GIST 7, LMS 3, MLPS 6, DDLPS 3 and SS 3, total 30. Adult normals comprise breast 5, colon 3, kidney 3, lung 5, uterus 1. Fetal bowel 3, kidney 3 and lung 4 remain separate. These are library/STT counts, not verified patient counts.

Each table row is a retained source peak. The delta compares the four-EMC median with the pooled 30-sarcoma median. The next columns count positive median contrasts across seven individual sarcoma histologies and five adult organs. These counts do not weight effect sizes or establish specificity. Individual positives count the four EMC values strictly above the pooled-sarcoma median; zeros remain ties. Sensitivity changes count strict sign changes including zero among four leave-one-EMC and seven leave-one-histology pooled-sarcoma contrasts.

| Gene | Peak | Pooled sarcoma delta | Positive histologies / 7 | Positive adult organs / 5 | Individual positive / 4 | Sensitivity sign changes / 11 |
|---|---:|---:|---:|---:|---:|---:|
| CHRNA6 | 38986 | 0.023913 | 4 | 4 | 2 | 3 |
| CD276 | 19547 | 0.102257 | 6 | 5 | 4 | 0 |
| CD276 | 19548 | 0.005926 | 3 | 2 | 3 | 2 |
| CD276 | 19549 | 0.080078 | 3 | 4 | 2 | 3 |
| SSTR2 | 22547 | 0.210380 | 4 | 4 | 3 | 0 |
| SSTR2 | 22548 | 0.035775 | 3 | 4 | 3 | 2 |
| PRAME | 53327 | -0.092029 | 3 | 4 | 2 | 3 |
| FAP | 31563 | 0.230559 | 6 | 4 | 2 | 2 |
| CD248 | 42759 | -0.142709 | 2 | 5 | 1 | 0 |
| CD248 | 42760 | -1.754294 | 1 | 3 | 1 | 0 |
| CSPG4 | 46886 | 5.245156 | 7 | 5 | 4 | 0 |
| MSLN | 19943 | 0.000000 | 0 | 0 | 1 | 0 |
| MSLN | 19944 | 0.096609 | 3 | 1 | 2 | 3 |
| L1CAM | 54452 | 0.031405 | 4 | 0 | 2 | 6 |
| GPC3 | 54378 | -0.119335 | 2 | 0 | 1 | 0 |
| ALPP | no mapped peak | NA | NA | NA | NA | NA |
| CDH17 | 39248 | 0.000000 | 0 | 0 | 0 | 0 |
| CDH17 | 39249 | -0.114429 | 3 | 3 | 0 | 0 |
| CDH17 | 39250 | -0.050788 | 3 | 2 | 2 | 3 |

CHRNA6 peak 38986 has EMC values 0, 0.163592345, 0.997776998 and 0.11405081 (STT5525/5526/5527/5592). Its pooled-sarcoma delta is +0.0239129595, but only two EMC values exceed that comparator median; its median delta is negative against ESS, EWS, SS and adult kidney. Adult-pooled delta is +0.1388215775, whereas fetal-pooled delta is -0.0428913890. The combined adult/fetal pooled delta stays positive, obscuring that stage difference. CHRNA6 is the external known-marker check, not a new discovery or independently validated marker here. This limited 3SEQ peak observation is distinct from [Dulken et al. 2024 RNA chromogenic in situ hybridization evidence](https://pubmed.ncbi.nlm.nih.gov/38447752/) (PMID 38447752; DOI 10.1016/j.modpat.2024.100464): their abstract reports strong diffuse signal in 25 EMC cases and no threshold-level overexpression in 685 mimics, with limited below-threshold expression in some mimics. The discordant bulk peak does not invalidate that diagnostic tissue assay or establish whole-transcript absence.

CSPG4 peak 46886 has positive median differences for every sampled sarcoma histology and adult organ. Its lowest EMC value, STT5592 = 4.302301323, is below the LMS and MLPS medians. Adult colon STT5610 = 6.548826073 exceeds this EMC value; the minimum-EMC minus maximum-adult-colon contrast is -2.246524750. Thus even this broad median signal is not universal individual separation or tumour restriction. It is a lead for further validation, not established biological selectivity.

CD276 illustrates peak disagreement: all three peaks have positive pooled-sarcoma medians, yet their histology signs differ and adult breast is positive for peak 19547 but negative for 19548/19549. CD248 has two negative pooled-sarcoma peaks despite positive pooled-adult deltas; adult breast and uterus are negative for peak 42760. Both SSTR2 peaks are negative against adult kidney. FAP is negative against ESS and adult uterus despite positive pooled values. MSLN peak 19943 ties the sarcoma medians, while 19944 changes sign by histology and is negative against four adult organs. L1CAM is positive against the pooled sarcoma median but negative against every adult organ. GPC3 is negative against every adult organ. PRAME and CDH17 have zeros and sample/stratum differences that defeat universal EMC-high descriptions. These examples qualify the full fixed panel rather than nominate a new list.

Peak-level plots are unnecessary for this small table; all exact individual, replicate, stratum and sensitivity values remain in [results.json](results.json), [flat contrasts](contrasts.tsv), [source rows](selected-source-rows.tsv) and [column mapping](column-mapping.json). All other cancer values and original annotation fields are retained. No values from other platforms enter the calculations.

Validation: [verify.py](verify.py) independently reads the archived gzip, uses a separately implemented token matcher and Fraction arithmetic, and checks every selected source field, all replicate means, all 342 stratum contrasts and 198 deletion sensitivities, every individual difference and extremum, denominators and coverage flags. [checks.json](checks.json) records the passing results. All selected cells are complete; incomplete-case behavior was specified but is not an empirical finding. This was one analysis execution, followed by independent verification; no repeat biological search or result-driven change. [execution.json](execution.json) records actual start/end time, duration, exit codes and permissions. Total conversational time and subscription usage are unavailable. No process remains running.

To reproduce from the repository root, run the bundled Python executable on research/autonomy/atlas-sample-organ-2026-09-06/analyze.py, then verify.py and render_report.py. All use only the standard library and already archived inputs; no install or paid compute is needed. The outputs are deterministic (no timestamps inside analytic artifacts); a second generator execution was not performed because the agreed computation was a single run. No commit or repository preflight was run by this worker. Sources and generated artifacts require coordinator integration/provenance anchoring before release.

Next useful scientific step: integrate these sample/peak-qualified observations into the existing atlas evidence, and seek an authoritative specimen/patient crosswalk or genuinely compatible independent cohort before making validation claims. Additional large-scale ranking alone would not resolve the limitation. The comparison is bulk FFPE transcript signal, with a cancer-selected peak universe and only five adult organs; healthy mesenchymal lineage, many other organs and cellular composition remain unresolved. Neither complete separation within this panel nor a positive median establishes surface localization, peptide-HLA presentation, safety, efficacy or a therapeutic window. PRAME is an intracellular HLA-presented address, not a conventional surface protein.
