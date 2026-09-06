---
id: DOC-ATLAS-HOFVANDER-RESULT-20260906
title: Frozen tissue RNA checkpoint results
level: cross-cutting
kind: memo
status: live
canonical_for: []
purpose: Report every prespecified gene and contrary sensitivity from the completed frozen analysis.
scope: Single-cohort tissue RNA prioritization and separate shared-histology array replication.
audience: [autonomous research agents, external reviewers]
date: "2026-09-06"
last_verified: "2026-09-06"
related: [DOC-ATLAS-HOFVANDER-VALIDATION-20260906]
---

CSPG4 is the only one of11 address genes meeting the frozen Hofvander tissue-validation allocation rule. Its all9-EMC equal-histology probability of superiority is0.89454 and its year-matched summary is0.81111. The result is materially year-sensitive: deleting2019 lowers the matched summary to0.43333, while the marginal summary remains0.83333. This supports a **qualified tissue-validation rationale**, not a batch-robust or universally EMC-specific enrichment claim. CHRNA6 has A=1 across the three primary contrasts, but was a separate prior-supported control and does not count as address-panel success.

The primary shared-histology LGFMS anchor agrees for CSPG4: original array A=1.000 (6 EMC biopsies versus17 LGFMS), Hofvander marginal A=0.96581 (9 versus13), and matched A=0.93333 (3 supported EMC). Array LGFMS direction survives every single-biopsy deletion. Separately, CSPG4 array A=1 versus MFS, SFT and desmoid; Hofvander marginal/matched estimates are0.85370/0.85714,0.87879/0.62500 and1/1 respectively. These are named comparator results, not a cross-cohort composite or proof of universally independent recruitment.

## Full fixed panel

Higher A means higher EMC ranks;0.5 means neutral pair ordering including half ties. Hof summaries weight MLPS,LGFMS,synovial equally. Marginal uses9 EMC; matched uses3 EMC per contrast, union4. Intervals are pointwise2000-resample bootstrap percentiles, conditional on observed year strata; singleton strata stay fixed and can yield misleadingly narrow/degenerate intervals. They are not simultaneous confidence claims, clinical intervals or statistical discovery thresholds. Full precision is retained in CSV/JSON. L1CAM rounds to0.699 here and remains below the frozen0.70 benchmark; no rounding was used in the rule.

| Gene | Hof marginal A [conditional95%] | Hof matched A [conditional95%] | LGFMS array / Hof / matched | Frozen rule |
|---|---|---|---|---|
| CD276 | 0.266 [0.174,0.361] | 0.271 [0.111,0.438] | 0.324 / 0.026 / 0.048 | False |
| SSTR2 | 0.569 [0.413,0.729] | 0.734 [0.401,0.978] | 0.471 / 0.761 / 0.810 | False |
| PRAME | 0.216 [0.170,0.260] | 0.254 [0.190,0.333] | 0.686 / 0.641 / 0.762 | False |
| FAP | 0.344 [0.190,0.510] | 0.279 [0.000,0.581] | 0.549 / 0.051 / 0.095 | False |
| CD248 | 0.122 [0.027,0.222] | 0.016 [0.000,0.063] | 0.304 / 0.214 / 0.048 | False |
| CSPG4 | 0.895 [0.866,0.918] | 0.811 [0.753,0.861] | 1.000 / 0.966 / 0.933 | True |
| MSLN | 0.680 [0.591,0.780] | 0.590 [0.343,0.817] | 0.294 / 0.927 / 0.786 | False |
| L1CAM | 0.699 [0.624,0.772] | 0.616 [0.429,0.808] | 0.765 / 0.902 / 0.857 | False |
| GPC3 | 0.291 [0.209,0.375] | 0.313 [0.238,0.367] | 0.480 / 0.761 / 0.905 | False |
| ALPP | 0.533 [0.450,0.617] | 0.497 [0.450,0.533] | 0.637 / 0.611 / 0.500 | False |
| CDH17 | 0.445 [0.356,0.535] | 0.431 [0.269,0.620] | 0.098 / 0.303 / 0.281 | False |
| CHRNA6 | 1.000 [1.000,1.000] | 1.000 [1.000,1.000] | 1.000 / 1.000 / 1.000 | context_not_applied |

## Contrary evidence and sensitivity

CSPG4 is not higher than DFSP on the marginal comparison (A=0.46667); this context was not part of the pass rule and is retained. The DFSP matched contrast is only1 EMC versus3 comparators. CSPG4's leave-one-EMC-out equal-histology ranges are0.88136–0.94035 marginal and0.71667–0.94444 matched; leave-one-histology-out ranges0.85891–0.94896 and0.75000–0.88333. Comparator-patient deletion ranges are0.88905–0.89976 and0.80317–0.83333. Year deletion ranges are0.83333–0.94618 and0.43333–0.94444, exposing the2019 dependence. Revised-diagnosis sensitivity gives0.89475 marginal and0.81111 matched, but partly expression-informed revisions cannot supersede original labels.

All10 other address genes fail the original broad allocation rule. PRAME and L1CAM are positive against LGFMS in both cohorts yet weak/reversed against other primary Hofvander histologies. MSLN, SSTR2, GPC3 and FAP have opposed array-versus-Hofvander LGFMS directions. CD276, CD248 and CDH17 remain negative against LGFMS in both cohorts. ALPP has positive marginal LGFMS directions but exactly neutral matched A=0.5. These directions narrow the biological question rather than being dropped as inconvenient targets. Complete primary/context directions, all individual year cells, all deletions and all48 shared-histology contrasts are provided in the tables below and original JSON.

## Separate normal-expression context; no change to frozen analysis

The new12-gene [HPA source roster](../atlas-normal-context-2026-09-06/fixed-panel-normal-context-roster.json) is joined by the fixed symbols for interpretation only. Its original XML entries are version25; current HPA methods/download pages describe25.1/Ensembl109. Exact response hashes and retrieval provenance remain in that source packet; this is not a tumor/normal matched comparison. HPA consensus tissue RNA takes maxima across HPA/GTEx sources and grouped sub-tissues, not an independent cohort average. No nTPM/TPM safety ratio, normal-sparing label or membrane-accessibility verdict is computed.

| Gene | Normal tissue IHC reliability | Missing/discordant context retained |
|---|---|---|
| [CD276](https://v25.proteinatlas.org/ENSG00000103855) | enhanced | Broad normal cytoplasmic/membranous IHC versus vesicle ICC/IF. |
| [SSTR2](https://v25.proteinatlas.org/ENSG00000180616) | uncertain | Brain context; uncertain IHC and intracellular ICC/IF. |
| [PRAME](https://v25.proteinatlas.org/ENSG00000185686) | enhanced | Testis-associated evidence; nucleoplasm/membrane tags do not establish intact surface accessibility or EMC peptide-HLA presentation. |
| [FAP](https://v25.proteinatlas.org/ENSG00000078098) | uncertain | Uncertain IHC; missing ICC/IF is not absent membrane protein; stromal source unresolved. |
| [CD248](https://v25.proteinatlas.org/ENSG00000174807) | enhanced | Normal cell-type/membrane annotations do not identify the EMC compartment. |
| [CSPG4](https://v25.proteinatlas.org/ENSG00000173546) | approved | Broad cytoplasmic normal IHC; membrane ICC/IF does not establish normal sparing or EMC accessibility. |
| [MSLN](https://v25.proteinatlas.org/ENSG00000102854) | enhanced | Normal epithelial staining; mesothelial surfaces are not comprehensively surveyed. |
| [L1CAM](https://v25.proteinatlas.org/ENSG00000198910) | enhanced | CNS/PNS and renal-tubule normal context retained. |
| [GPC3](https://v25.proteinatlas.org/ENSG00000147257) | missing | No normal tissue-IHC summary/cell rows; placenta RNA and membrane ICC/IF are not adult protein-absence evidence. |
| [ALPP](https://v25.proteinatlas.org/ENSG00000163283) | enhanced | Placental/cervical RNA and trophoblast IHC; antibody multi-gene cross-reactivity retained. |
| [CDH17](https://v25.proteinatlas.org/ENSG00000079112) | enhanced | Gastrointestinal epithelial protein and differing intracellular/junction tags retained. |
| [CHRNA6](https://v25.proteinatlas.org/ENSG00000147434) | missing | Retinal RNA enrichment; no tissue-IHC rows/ICC summary, not evidence of absent normal neural protein. |

The previously independently verified [GSE28866 sample/organ report](../atlas-sample-organ-2026-09-06/report.md) is historical evidence under a different, cancer-selected3SEQ peak estimand. CSPG4's positive medians coexist with an individual normal-colon record exceeding the lowest EMC library value. CHRNA6 is nonuniform in those peak records despite the present array/TPM direction. Those four EMC library records are not four newly established independent patients. No unchanged3SEQ analysis was rerun, no peak-scale quantity pooled with the present ranks, and no result from normal context altered panel membership or the frozen rule.

## Sources, reproducibility and scope

Primary sources are [Hofvander2026](https://pmc.ncbi.nlm.nih.gov/articles/PMC13133608/), its [author data v1.0.1](https://github.com/JakobHofvander/Transcriptomic_subgroups_in_soft_tissue_tumors_correlate_with_morphologic_subtype_genomic_features/tree/v1.0.1), [GSE24369](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE24369), and [GPL6244](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GPL6244). Exact original source hashes, sample/lesion decisions and unique probes are frozen in metadata-manifest.json and replication-manifest.json. All42 array samples were parsed from original SOFT values at full released precision; MFS and SFT source-label corrections were frozen before outcomes. Array biopsies have unknown lesion stage and no universal patient crosswalk. Two pooled skeletal muscle RNAs are descriptive only, not evidence of normal-organ safety. GSE4303 was not treated as abundance replication.

Both authorized processes completed once with exit0. Raw logs, command times/elapsed, exact authorization and execution states are preserved in analyze-run.log,analyze-command.json,replication-run.log,replication-command.json and each output directory. There were no empirical errors, repairs, reruns or tuning. Initial arithmetic fixtures and replication parser/rank fixtures passed before outcomes. summarize.py reads completed outputs only; original analyze.py and replication.py remain unchanged. An independent reader separately parsed original sources and reported zero discrepancies across8,448 Hofvander values,504 array values,2,436 estimate/deletion blocks and266,772 scalar comparisons. This verifies arithmetic and the frozen gate, not biological independence or localization; no manuscript-ready or publication claim is made. No process remains running.

Useful next interpretation is CSPG4 tissue protein/localization assessment in relevant EMC material with explicit batch and DFSP context, alongside CHRNA6 as a separate established-context signal. Bulk RNA cannot distinguish malignant-cell expression from stroma/immune composition, prove normal sparing, demonstrate a therapeutic window or establish efficacy. Source convenience sampling and partial overlap evidence further limit generalization.

Files: all12-gene-effects.csv (compact effects/conditional intervals); all-hofvander-contrasts.csv (all60 initial gene×histology effects); all-year-cells.csv (unsupported and singleton cells retained); all-primary-deletions.csv (every deletion summary); all-shared-histology-replication.csv (all48 cohort comparisons and deletion ranges). results/ and replication-results/ preserve full patient values/placements and individual sensitivities. No candidate or unfavorable comparison was removed.
