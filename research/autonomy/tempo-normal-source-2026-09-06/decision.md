---
id: DOC-TEMPO-NORMAL-SOURCE-20260906
title: GSE119630 supplies five-patient matched normal colon counts, but no bridge to the processed EMC assay
kind: memo
audience: [maintainers, autonomous research agents]
status: live
purpose: Resolve the specific normal-source dependency without inferring unmeasured calibration.
scope: Human GSE119630 provenance and structural inspection; no expression contrast or manuscript.
date: 2026-09-06
last_verified: 2026-09-06
---

GSE119630 repairs a real missing input: publicly downloadable, probe-resolved counts from
pathologist-designated normal colon regions in five colorectal-cancer patients. It makes a
specific **within-study normal-colon repeatability experiment** possible. It does **not yet
permit a calibrated EMC-versus-normal expression comparison**, a healthy-organ atlas, or a
therapeutic-selectivity claim. This is a source checkpoint, not an analysis result or proof
that no future bridge can be obtained.

## Primary evidence and recovery

The original NCBI GEO family SOFT and two named HUMAN count matrices were retrieved over the
public NCBI FTP site's HTTPS interface, each HTTP200. The complete Trejo2019 primary JATS
(PMID30794557; PMC6386473; DOI10.1371/journal.pone.0212031) was recovered through Europe PMC.
The directly cited assay-method paper, Yeakley2017 (PMC5444820;
DOI10.1371/journal.pone.0178302), was recovered through the same public fullTextXML interface
to clarify probe pools, attenuation, and control experiments. No Trejo supplementary-material
element is present in the recovered JATS; its methods point to these GEO processed files.
Source URLs, UTC request times, HTTP status/headers, sizes, and SHA256 are retained in
`retrieval.json` and `methods-retrieval.json`. Original bytes remain untouched.

The web renderer returned browser-check pages for GEO and PMC. No challenge was solved or
repeated; ordinary independent public archive/API delivery succeeded. No credentials, paid
access, animal count matrices, raw sequencing files, broad search, or author contact was used.
The GEO family metadata itself necessarily includes the species inventory:119 human,
15 mouse,21 rat records. Only human count matrices were downloaded or validated.

## Specimens and experimental units

Trejo Methods, `sec009`, direct paragraph3, explicitly states that a pathologist identified
normal and cancerous regions on sections of colorectal cancer. Two within-donor biological
replicates of each tissue type from each patient were separately lysed; each lysate was
assayed in three technical replicate experiments. Results and Fig3 identify five anonymized
patients. This evidence supports normal-region classification beyond the titles alone.

`ColonCancerReplicatesMaster` contains60 libraries:5 patients ×2 region types ×2 biological
samples ×3 technical replicates. The30 normal libraries represent10 separately lysed
within-patient normal-region samples from **five patients**, not30 independent patients or
10 independent donors. Their GEO accessions, original metadata, matrix columns and explicit
patient/region/biological/technical identifiers are preserved in `sample-column-mapping.json`.
Every column maps to one GEO human sample via its exact `Sample_description` field; all119
human GEO samples map exactly once across the two matrices.

These are cancer-patient matched normal regions, reasonably described as tumor-associated
normal or adjacent-normal in scope; the exact tumor-to-normal distance, independent block
identity, histological composition, donor demographics and normal-region fixation duration
are not supplied. The source does not establish healthy-donor tissue. Do not infer30
independent normal specimens or cancer-free status from the word Normal. GEO's common
cell-pellet fixation/growth protocol text appears on tissue records too; it must not be
misread as proof that normal colon received the cell-pellet fixation regimen.

The59 columns of `HumanGeneCountsMaster` are not a healthy-organ census:

| Column family | Libraries | Source-supported identity |
|---|---:|---|
| F2 |9| Colorectal/prostate adenocarcinoma and pancreatic cancer, three section replicates each (primary Fig2 results) |
| F7 |8| Prostate cancer serial sections, paraffinized/deparaffinized/H&E-treated; published Fig9, despite older GEO Fig7 titles |
| F4 |24| Archival colorectal cancer1986, hepatocellular carcinoma1993 and kidney cancers1988/1994; internal numeric tokens are not independent patient IDs |
| F6 |18| MCF7 and MDA-MB-231 breast-cancer cell-line material, fresh/fixed and stated input conditions; not normal donor tissue |

No crosswalk establishes whether separate experiments reused a donor or block. Technical
replicates, serial sections, fixation comparators, and study-specific controls cannot be
counted as new normal donors. Primary tissue/staining/cell-pellet locators are retained in
`primary-method-locators.json`; complete per-sample original metadata is preserved separately.

## Matrix and probe identity

Both files have21,111 unique probe rows, three annotation fields (`Probe_ID`, `Probe_Sequence`,
`Accession`) and60 or59 unique sample columns. All2,512,209 count fields are nonnegative
integer lexical strings, hence finite; there are no missing count fields, ragged rows,
duplicate probe IDs or duplicate headers. The gzip streams decoded successfully. Independent
CSV and delimiter parses agreed on every field. Counts were not summarized by target or
compared across groups.

The probe-ID-to-sequence/accession maps are identical between the two files, but their row
orders differ. Joining by row position would therefore be wrong. Every sequence has50
characters. One source sequence, C8ORF82_33840, contains `I`; this non-ACGT character is
preserved and flagged, without repair or an inferred chemical meaning. There are19,289
distinct source-label prefixes before the final numeric underscore suffix; these are not
19,289 independently validated HGNC genes. The article reports19,283 genes/21,111 probes.
The six-label difference is unresolved and does not change the exact probe count.

All12 frozen target labels are represented in both matrices, by13 probes:

| Target | Source probe ID(s) | Present by exact symbol in twelve-column EMC export |
|---|---|---|
| CHRNA6 | CHRNA6_15834 | yes |
| CD276 | CD276_12737 | yes |
| SSTR2 | SSTR2_27909 | yes |
| FAP | FAP_22264 | yes |
| CD248 | CD248_22272 | yes |
| CSPG4 | CSPG4_24558 | yes |
| MSLN | MSLN_15223 | yes |
| PRAME | PRAME_17621 | no |
| L1CAM | L1CAM_12063; L1CAM_3714 | no |
| GPC3 | GPC3_20438 | no |
| ALPP | ALPP_20550 | no |
| CDH17 | CDH17_23930 | no |

The exact sequences, accessions and1-based source CSV rows are in `structural-inventory.json`;
complete feature mappings are the two derived probe-annotation TSVs. This table is an
identifier-presence inventory, not an expression/detection result. No alias substitution,
probe aggregation, target ranking, or zero imputation was performed. The absence of five
labels in the EMC processed export still has an unresolved cause.

## Measurement comparison with PeerJ21497

| Requirement | GSE119630 | Existing EMC source packet | Consequence |
|---|---|---|---|
| Exact assay content/version | Human whole transcriptome21,111 probes; actual50-character sequences/accessions supplied; commercial revision number not specified | Human Whole Transcriptome2.0,22,537 probes/19,683 reported genes; released matrix only symbols | Same family does not prove identical fixed-target detector sequences or response |
| Probe versus gene units | Raw mapped probe counts; multiple probes for some labels | Processed log2CPM9,500 rows ×12 columns; article9,909 genes; duplicated symbols discarded per article | Cannot reconstruct raw gene/probe units or duplicate-removal rule from export |
| Lysis and annealing | Direct scraped FFPE; mineral oil95°C5min; protease37°C30min;2µL lysate;70→45°C then overnight | Closely corresponding documented steps | Similar preparation supports assay-family relevance, not quantitative interchangeability |
| Fixation/staining/storage | Human archive history and separate cell/rat fixation and prostate staining experiments documented; exact normal-colon regimen incomplete | Archival EMC; new/old block analyses; sample-specific covariates and analyzed-slide staining state not supplied in workbook | Other organisms/cell lines cannot establish target-specific bounds for the human normal-versus-EMC preparation difference |
| Mapping and normalization | GEO Bowtie up to2 mismatches in probe pseudo-transcriptome; bcl2fastq versions; article DESeq2 or total-read normalization depending analysis | UQ normalization then edgeR CPM; low-expression and duplicated-symbol exclusions; missing exact factors/log prior/count inputs | Existing processed values cannot simply be combined with raw counts |
| Batch effects | Technical/within-donor replicates within one study; no shared EMC material | Article describes batch correction, but workbook's correction state/method/factors unresolved | Tissue and study remain confounded; library-size normalization cannot identify gene-specific study effects |
| Attenuation | No per-probe attenuator factors or clear attenuation/back-correction status in these files/methods | No per-probe factors/status in available EMC packet | Sequence equality alone would not establish equivalent detector response |
| Reference/negative controls | Fresh/fixed breast-cancer cell material and staining comparisons; no identified shared EMC reference, no explicit no-input or synthetic spike-in library columns in the two matrices | Positive RNA-control summary QC and replicate correlation, without identified control material or released control counts | Neither source supplies a common calibration bridge or target-specific background/response estimates |

Yeakley2017 explains that competing nonfunctional detector oligos can attenuate specific
transcripts and that correction requires known target-specific factors. Its ERCC titrations,
Universal Reference RNA/Brain controls and no-input assays are separate experiments, not
evidence that either current study used or released those same materials. Human genes such
as ERCC1/ERCC2 in these matrices are endogenous labels, not synthetic ERCC spike-ins.
Published assay-family sensitivity/reproducibility and context-independence demonstrations
do not supply missing study-specific calibration constants or tolerable batch bounds.
GEO identifies NextSeq500 whereas the Trejo article says NextSeq550; preserve that metadata
discrepancy rather than assign an instrument by assumption.

## Concrete next experiment and stop

A **normal-colon replicate precision study** is technically feasible from
the recovered public input, after integration and coordinator verification: retain the frozen12-target panel
at its13 probe identities, distinguish the three technical assays of each lysate from the
two within-patient biological samples, and use five patients as the independent donor level.
The question would be whether the normal-region assay readings are repeatable within these
specimens and how variation partitions across those replication levels. No measurements,
thresholds, effects or precision estimates for that experiment were calculated here. Even
a strong result would be local assay precision, not a normal-organ reference range,
absolute transcript calibration, EMC selectivity, or protein accessibility. This is a
feasibility observation, not a recommendation to spend another cycle: allocation requires
a demonstrated connection to an EMC decision. It does not repair the cross-study bridge.

The **cross-study calibrated EMC-versus-normal comparison is no-go on current evidence**.
The next necessary bridge is exact EMC probe/aggregation and attenuation provenance plus
a common assayed reference with probe-level measurements across the relevant study/assay
conditions, or another independently justified calibration design. No such shared material
is identified in the recovered data; it cannot be manufactured by choosing housekeeping
genes, z-scoring each study, or assuming negligible batch effects. Merely obtaining an EMC
probe manifest would repair sequence mapping but would not alone identify study effects.
This dataset narrows the missing dependency and enables a bounded within-study experiment;
it does not establish an overall research impasse.

`verify_packet.py` checks original hashes, source identifiers, full finite-count structure,
column-to-GSM uniqueness, replication hierarchy and deterministic derived outputs against
the frozen manifest. The coordinator still owns independent verification and integration.
No expression contrast, pooling, model, manuscript, commit, shared-state edit, normal/full
gate or nested agent was run. All worker commands finished; no worker process remains active.

## Metadata amendment, 2026-09-06

Added the required audience frontmatter after the integration gate identified its omission.
Scientific content, source bytes, findings and analysis scope are unchanged. The original
decision, manifest and verification receipt are preserved in the corresponding original files.
