---
id: DOC-CHECKPOINT03-PROTEIN-RUNNER
title: Frozen protein support and histology descriptive runner
level: cross-cutting
kind: memo
status: live
purpose: Specify the finite cloud implementation of the preserved protein lineage follow-up plan.
scope: Two antigens, 61 fixed families, 24 support-by-histology cells and four rank-covariance decompositions; no model fitting.
audience: [maintainers, autonomous research agents, external reviewers]
date: "2026-10-02"
last_verified: "2026-10-02"
---

PLAN.md is unchanged. This implementation passed the cloud execution at `24ffe1f43b123d5822f318311e9e488d68850ede`, run37029842078/job110913618388. All eight synthetic tests and all four accepted pooled comparisons passed. New descriptive results, unsupported cells and precise limits are in FINDINGS.md. Run from this directory with installed numpy/pandas:

```sh
python -m unittest -v test_protein_lineage.py
python protein_lineage.py --matched /tmp/protein-RNA-final-matched-measurements.json --matrix /tmp/protein8498.txt --out /tmp/protein-lineage-output
```

Stage the matched JSON from `trimcrae/Rare-cancers` at `da49c4e836533253825587f83656675dac4c913b`, path `research/autonomy/data-opportunities-2026-09-30/deep-analysis/results/protein-RNA-final-matched-measurements.json`. Its exact 2,926,326 bytes and SHA256 `46deef9526068591a76c62bda6c20fa26ca95969f666769850eb626306f63f24` are mandatory. The matrix is fetched once if absent from the supplied path, with a 94,222,540-byte cap, 30-second network inactivity timeout and exact SHA256 check. The source URL and digest are constants in the code. The process has a 295-second hard watchdog. A killed process, partial file or missing result is failure. Root should also wrap the command in a 300-second cloud timeout. Before download, free space must exceed 10 GiB plus twice the matrix size. No HDF5 input is needed.

The producer's model orientation, semicolon model-ID normalization, duplicate-model column means, accession-column means and subsequent family means are preserved. Only the two accession column sets are retained after orientation. The full TSV is parsed in cloud; this is not a local data download. The matched input hash fixes membership. All four accepted pooled n/rho checks must pass within 1e-12 before any result directory is created. Missing measurements remain null; neither imputation nor clinical interpretation is introduced.

Support status in the 122-row measurement table means original-protein present versus missing. A row contributes to the published original/added correlation only when RNA and 8498 protein are also available (`paired`). Thus `familiesWithSupportStatus` in each of the 24 cells is distinct from paired `n`. The output preserves all 61 source model/family/histology bindings, availability flags, both protein measurements and RNA, accession matches, and source hashes. Within-histology correlations use local average-tie ranks. The four covariance decompositions use ranks across each entire gene/support subset and population-weighted components; their sum reproduces the accepted pooled Spearman coefficient. Singleton strata have zero within contribution. Undefined sparse or near-constant cells remain explicit, using the original producer's n<3 or sample-SD<1e-12 rule.

The eight tests are synthetic: ties with a hand-calculated coefficient, singleton and all-singleton strata, one stratum, opposing within/between components with a hand-calculated pooled coefficient, empty/sparse inputs, constant measurements and invalid pairing. They do not constitute independent biological validation. No P values, confidence intervals, predictor refits or sign-selected strata are produced. Interpretation remains limited to the post hoc descriptive question and caveats in PLAN.md.
