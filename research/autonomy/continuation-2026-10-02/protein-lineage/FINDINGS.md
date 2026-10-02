---
id: DOC-PROTEIN-LINEAGE-FINDINGS-20261002
title: Histology and quantification support in two measured antigen comparisons
kind: memo
status: live
level: cross-cutting
purpose: Separate within-histology and between-histology contributions to previously observed pooled RNA-protein associations.
scope: Post hoc descriptive follow-up in a frozen 61-family sarcoma cohort; no model fitting or clinical validation.
audience: [maintainers, external reviewers]
date: "2026-10-02"
last_verified: "2026-10-02"
---

The new [cloud analysis](https://github.com/trimcrae/Rare-cancers/actions/runs/37029842078/job/110913618388) passed at `24ffe1f43b123d5822f318311e9e488d68850ede`. All eight synthetic arithmetic tests passed, and the four accepted pooled sample counts/correlations were reproduced as mandatory source-processing checks. The frozen [plan](PLAN.md) was committed before inspecting these new strata. No predictor was refitted and no significance test or new confidence interval was calculated.

The primary two-antigen measurement extract now permanently retains 122 family-antigen rows with RNA, original protein, expanded-matrix protein, missingness and histology. Its source matrix is the pinned published ProCan measurement file, not a protein prediction. All 24 prespecified gene-by-histology-by-support cells, including sparse/empty cells, are in results/protein-lineage-results.json. That file is 73,197 bytes, SHA256 `bfbd5bee8d88053565af54f7f0dea225cb55fed71f688cb4b6cab6f922bc0dbb`.

## Exact pooled-rank decomposition

| Antigen | Quantification support | Paired families | Pooled Spearman rho | Within-histology component | Between-histology component |
| --- | --- | ---: | ---: | ---: | ---: |
| CSPG4 | original | 33 | 0.665775 | 0.533021 | 0.132754 |
| CSPG4 | added | 18 | -0.304438 | -0.092707 | -0.211730 |
| L1CAM | original | 29 | 0.669951 | 0.501642 | 0.168309 |
| L1CAM | added | 17 | -0.482843 | -0.395833 | -0.087010 |

Ranks in this decomposition are formed within the entire gene/support subset. The two components share the same global rank-standard-deviation denominator and sum to pooled rho (largest numerical residual `2.22e-16`). They are not the local Spearman coefficients, a causal adjustment or independent evidence. Singleton strata contribute zero within-stratum covariance by construction; small strata may contribute to the identity even when a standalone correlation is undefined.

The negative added-subset rank covariances contain both within-histology and between-histology terms, with different relative contributions by gene. CSPG4 has the larger negative between-histology contribution; 12 of its 18 paired families are Ewing sarcoma. L1CAM has the larger negative within-histology contribution, but two strata with only two families each (osteosarcoma and rhabdomyosarcoma) contribute −0.147059 and −0.143382, together −0.290441 of the −0.395833 within term. These sparse terms are valid parts of the arithmetic identity, not robust within-lineage evidence. Neither negative aggregate is solely a between-histology arithmetic term. This does not show that changing a processing filter caused either association, or exclude quantification selection, measurement error or small-sample variation.

## Comparisons with supported correlations in both subsets

The inherited rule requires at least three paired families and nonconstant measurements. Exactly four of twelve gene/histology combinations meet this rule in both support subsets:

| Antigen | Histology | Original n | Original rho | Added n | Added rho |
| --- | --- | ---: | ---: | ---: | ---: |
| CSPG4 | Ewing's Sarcoma | 3 | -0.500000 | 12 | -0.181818 |
| CSPG4 | Osteosarcoma | 8 | 0.571429 | 3 | -1.000000 |
| L1CAM | Ewing's Sarcoma | 12 | 0.566434 | 6 | -0.600000 |
| L1CAM | Other Sarcomas | 6 | 0.828571 | 4 | 0.200000 |

Two show an observed sign reversal: CSPG4 osteosarcoma and L1CAM Ewing sarcoma. CSPG4 Ewing remains negative in both subsets; L1CAM other sarcomas remains positive in both. The CSPG4 added osteosarcoma coefficient is based on only three families. Most gene/histology comparisons do not have enough paired support to estimate both correlations under the fixed rule. All unsupported cells remain in the result; none was selected away.

## Meaning for the paper

This is a narrow measured-data extension of the existing sarcoma RNA-to-protein transfer report. It qualifies why expanding quantification support can alter an observed RNA-protein relationship, and distinguishes pooled covariance composition from the limited within-histology evidence. It neither identifies a molecular mechanism nor establishes a general within-lineage effect. The fixed cohort contains no independently verified EMC model. It provides no new EMC-specific protein, surface-accessibility or treatment-response finding, and does not modify the submitted CSPG4 letter.

Exact source identity, mapping and processing are described in README.md and the executable code. Independent code review preceded execution; result verification is recorded separately. Source-capture and result logs, execution revision and Python/numpy/pandas versions are retained. The complete matrix need not be downloaded again for follow-up questions answered by the new compact measurements. Stop here rather than adding genes, new cutoffs or repeated significance searches.
