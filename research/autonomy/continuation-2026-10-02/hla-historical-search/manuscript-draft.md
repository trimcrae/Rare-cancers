---
id: "DOC-CONTINUATION-20261002-HLA-HISTORICAL-DRAFT"
title: "Historical search-space representation and donor coverage in a benign HLA atlas"
level: "L3"
kind: "manuscript"
status: "live"
canonical_for: []
purpose: "Working research draft: Historical search-space representation and donor coverage in a benign HLA atlas."
scope: "October 2 working extension of the preserved donor-coverage analysis; deposited historical canonical FASTA representation, without submission clearance."
audience: ["maintainers","external reviewers"]
date: "2026-10-02"
last_verified: "unverified"
_backfilled: "true"
---

# Historical search-space representation and donor coverage in a benign HLA atlas

## Abstract

Public immunopeptidomics supplies measured normal-tissue evidence for cancer-antigen proposals, but a database absence is interpretable only within the assay's search space and donor coverage. We reanalysed the December 2020 HLA Ligand Atlas, freezing four provisional query sequences and three HLA types from an extraskeletal myxoid chondrosarcoma (EMC) proposal. No exact sequence match appeared in the processed peptide release. A subsequent checksum-verified scan of the deposited historical canonical FASTA found none of these queries among its 20,365 target proteins; the database therefore provides no representation of these exact sequences. HLA-B*15:01 was represented by five typed donors, HLA-A*30:02 by none, and HLA-DRB1*14:01 by one. Among predictor-flagged strong binders in the B*15:01 carrier group, the union contained 7,384 peptides, including 3,550 observed in only one donor. Those singletons accounted for 22.50% of pooled peptide–donor incidences. Exact subsampling of four of five donors omitted an average 9.62% of the five-donor unique union. These percentages describe different denominators derived from the same observed breadth counts. Filtering sensitivity changed the pooled fraction to 30.12% for strong-or-weak flags and 40.52% without a binding filter. The results quantify empirical donor support; they do not establish allele restriction, normal-tissue absence, authentic fusion boundaries or population safety.

## Introduction

Cancer-antigen proposals often combine a sequence with predicted HLA binding and search normal-tissue resources to assess specificity. Published HLA-ligand measurements are valuable because tissue collection, immunoprecipitation and mass spectrometry have already been performed. An absent released-table entry can reflect absent genotypes, unsearched sequences, limited sampling, detection thresholds or biological variation. These mechanisms have different implications for tumour-specificity claims.

Marcu and colleagues' HLA Ligand Atlas includes benign specimens from 21 subjects: 14 autopsy donors and seven surgical donors. Its primary report already documents donor and tissue variation. Our narrower question is how much observed peptide coverage depends on donor inclusion when a proposed HLA type has few typed carriers, and how this changes a nondetection statement. Provisional sequences from an EMC proposal provide a frozen example.

## Methods

We retrieved donors.tsv.gz, peptides.tsv.gz, sample_hits.tsv.gz and aggregated.tsv.gz from https://hla-ligand-atlas.org/rel/2020.12/. Compressed SHA256 receipts preserve release identity. We joined peptide IDs, donor typing and positive tissue/HLA-class records. Aggregate genotype and tissue unions do not establish a restricting allele or identify every tested negative donor–tissue pair.

The frozen queries were NMPCVQAQY, QQNMPCVQAQY, SYGQQNMPCVQAQYS and the related comparison sequence DMPCVQAQY. The first two and comparison sequence occur in research/manuscripts/neoantigen/fusion-junction-neoantigen-paper.md, Git blob e493246c900f971d2776874dcfa361f4543d0366. The class-II sequence occurs in research/modalities/patient-cd4-demo.json, blob 44831834b5f39b0b0b102544ed7a6f6fb07f478b. That artifact identifies transcript-model exon ranks and context QYSQQSSSYGQQ|NMPCVQAQYSPS. Associated proposed types were B*15:01, A*30:02 and DRB1*14:01. These are provisional source-model query strings; authentic biological fusion boundaries and peptide presentation were not established. Superseded binding pipelines were not rerun.

The original exact-sequence searches examined the processed release without a new raw-spectrum search. The primary study used a Swiss-Prot protein search space and a separate cryptic-peptide analysis. We subsequently recovered the deposited canonical search FASTA, sp_21_04_2020_decoy.fasta, from PXD019643. All 483 RESULT records in the deposit README reference its FASTA identifier. The complete 27,229,450-byte stream matched the deposited checksum when computed as SHA1; SHA256 was d351fdc0add26d0a1eb6c2214ee9bf597096387c866f2d6e6ed4507a7a090dcd. We searched exact contiguous substrings within records, separating observed sp| target and DECOY_ headers and retaining sequence ambiguity/stop characters. Six synthetic tests, including an exhaustive short-pattern oracle and boundary/decoy cases, passed before the cloud scan. This establishes representation in the deposited FASTA only. It does not independently reconstruct every search run, search the separate cryptic database, or establish peptide identification, presentation or absence.

Allele-carrier groups used primary-release typing. We selected observed peptides bearing the release's strong-binding predictor flag for the target type. Flags combine predictions following pooled immunoprecipitation; they are not monoallelic experiments or restriction assignments. Primary rank cutoffs include class-I strong ≤0.5% and class-II strong ≤1%, with additional predictor criteria specified in the original report. Donor sets pooled retained positive records across tissues. Sensitivities retained four autopsy B*15:01 carriers, admitted strong-or-weak flags, or included all class-I peptides from carrier donors.

For donor d with set S_d, the holdout fraction was the number of peptides absent from all other donors divided by |S_d|. Pooled holdout used singleton IDs divided by the sum of donor-set sizes, a peptide–donor-incidence denominator. Exact rarefaction separately averaged the fraction of the unique union missing from each m-donor subset. For a peptide seen in k of n donors, its missing probability is C(n−k,m)/C(n,m). These estimands use the same observed donor-breadth counts; they are not independent validation experiments or population-confidence estimates.

We joined protein_map.tsv.gz and submitted four exact sequence queries to each public IEDB epitope, tcell and mhc endpoint. Availability statements are scoped to the processed release and exact queries executed on 1 October 2026.

## Results

The release contained 223,246 peptide IDs and 967,449 positive sample-hit rows. Retained records represented 21 donors, 29 tissue labels, 198 class-I and 220 class-II donor–tissue–class units, and 227 unique donor–tissue pairs across classes. These describe retained positive-hit units, not every attempted assay.

Five donors carried B*15:01 and contributed 56 retained class-I units. No donor carried A*30:02. Only DN08 carried the exact DRB1*14:01 label, contributing 18 retained class-II units. A third-party SDRF annotation listed DN05 and DN17 as DRB1*14:01, whereas the primary release typed both as DRB1*14:54. We preserved this discrepancy and used the primary release. Neither metadata disagreement nor binding prediction establishes functional equivalence.

No exact sequence match to the four provisional queries appeared in the processed peptide table. Twelve IEDB exact queries returned HTTP 200 empty arrays. These are scoped database results, not negative experimental binding or T-cell assays. Native-parent annotations included EHVQQFYNL mapped only to NR4A3/Q92570 and KLFLDTLPF mapped to both NR4A3 and NR4A2. Both were class-I thymus observations. Shared mapping does not establish protein origin, restricting allele or cross-reactivity; native-parent ligands do not validate a provisional candidate.

The five-carrier B*15:01 strong-flag union contained 7,384 peptides and 15,775 peptide–donor incidences. Numbers observed in one through five donors were 3,550, 1,440, 927, 771 and 696. Thus 48.08% of the unique union consisted of singletons, while pooled holdout was 3,550/15,775 = 22.50%. Individual donor fractions ranged from 2.71% to 34.69%.

Exact subsampling of one, two, three or four donors omitted an average 57.27%, 35.95%, 21.18% or 9.62% of the five-donor unique union. The four-donor result averages missing unique peptides across donor subsets; pooled holdout weights donor incidences.

| Carrier set and filter | Donors | Unique union | Singleton IDs | Peptide–donor incidences | Pooled holdout |
| --- | ---: | ---: | ---: | ---: | ---: |
| All, strong | 5 | 7,384 | 3,550 | 15,775 | 22.50% |
| All, strong or weak | 5 | 11,597 | 6,547 | 21,734 | 30.12% |
| All, unfiltered | 5 | 33,186 | 21,381 | 52,763 | 40.52% |
| Autopsy, strong | 4 | 6,675 | 3,169 | 13,312 | 23.81% |
| Autopsy, strong or weak | 4 | 10,033 | 5,726 | 17,842 | 32.09% |
| Autopsy, unfiltered | 4 | 30,332 | 20,295 | 46,380 | 43.76% |

The estimate depends on the peptide universe. Unfiltered carrier sets include ligands associated with other carried allotypes. Across 63 multi-donor allotype or heterodimer strata, pooled fractions ranged from 16.93% to 94.28%, with median 48.28%; 28 strata contained only two donors. These overlapping strata are not independent allele experiments. Tissue matching did not resolve depth imbalance: one colon pair contained 1,402 versus 39 strong-flag IDs. A one-donor DRB1*14:01 holdout equals 100% by construction and cannot assess replication.

The deposited FASTA contained 20,365 Swiss-Prot target records and 20,365 decoys, with zero occurrences of every frozen query in either group. The target count agrees with the paper, while PRIDE's project protocol describes 20,416 proteins plus contaminants. The paper reports Percolator 3.4 and the deposit protocol 3.1.1. These differences remain unresolved as per-run settings; the deposit-to-file association is not proof of identical settings in every run. The four query lengths were 9, 11, 15 and 9 residues. The 15-residue query exceeds the primary method's class-I length range of 8–12; all four lie within its class-II range of 8–25. These are length-only flags, not mass/charge observability or biological eligibility.

## Discussion

The proposed types have different empirical support in this release: five exact carriers, none and one. Donor dependence makes the observed B*15:01 union sensitive to inclusion. The exact queries are absent from the deposited canonical FASTA, so their absence from the released peptide table cannot establish a measured negative from that search space. The separate cryptic search and unverified per-run settings prevent extending this conclusion to every Atlas search.

This audit is incremental to the Atlas paper's donor-variation results. Added value lies in a frozen proposal question, typing reconciliation, direct historical FASTA representation, explicit denominators, exhaustive observed-donor rarefaction and filtering sensitivities. It is a narrow methods contribution rather than an EMC-antigen discovery or a new normal-tissue atlas. Query sequences remain provisional.

Depth, tissue composition, postmortem specimens and false discovery limit peptide-set interpretation. The primary study used local 1% FDR, with pooled global FDR of 4.5% for class I and 3.9% for class II; its separate cryptic search used 10% FDR. Calculations operate on released positive observations, without recovering undetected peptides or every attempted sample. They do not demonstrate HLA restriction, population prevalence, T-cell recognition, cytotoxicity or a therapeutic safety window.

## Sources and reproducibility

Marcu A et al. HLA Ligand Atlas: a benign reference of HLA-presented peptides to improve T-cell-based cancer immunotherapy. Journal for ImmunoTherapy of Cancer. 2021;9:e002071. DOI:10.1136/jitc-2020-002071. Primary XML:PMC8054196.

Base code: deep-analysis/normal_ligandomics.py, SHA256 19f70cd8fb6e8216a35d182e3196c26cd0f4903974c35983bf79a68877f30424; successful run 36864188085, job 110375492301. Finite follow-up: deep-analysis/normal_ligandomics_finite_followup.py, SHA256 9817e50ad24a8cce8f03ab1bb0190f3072905d5a13d56bcecee3720e3dcccafa; successful run 36874318874, job 110409809073, commit 6eaf981f90eb76ad16c675b36afda3e43db4ad77.

Durable measurements: deep-analysis/results/normal-ligandomics-actual.json; deep-analysis/results/ligandomics-donor-depth-sensitivity-actual.json; deep-analysis/results/ligandomics-query-and-source-joins-actual.json. These include compressed source receipts, exact IEDB queries and joins.

The new source metadata, README association audit and cloud scan are preserved alongside [scan_historical_fasta.py](scan_historical_fasta.py), [historical-fasta-metadata.json](historical-fasta-metadata.json), source ZIP manifests and [results](results/historical-fasta-scan.json). The new scan completed in [run37041943617](https://github.com/trimcrae/Rare-cancers/actions/runs/37041943617), revision9918aa902d96128adcc86009174645d0300f59f4. The original donor/processed-release computations were reused without repetition. A separate [source and code review](review/review.json) bound the returned hashes, counts, zero matches and limits; it did not repeat the full scan.

Independent scientific review checked actual execution, arithmetic, source restrictions and claim boundaries. This is a reviewable manuscript draft; journal acceptance and submission readiness have not been established.
