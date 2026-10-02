---
id: DOC-ASO-EXACT-MATCH-WITNESS-ANNOTATION-20261002
title: Exact-match witness annotation and coverage
kind: memo
status: live
level: cross-cutting
purpose: Identify reference genes and current transcript biotypes among saved exact-match witnesses while quantifying capped coverage.
scope: >
  Annotation of 60 saved transcript identities for 19 target designs using Ensembl
  release 116 responses collected on 2026-10-02. Verification covers the executed
  annotation join, matching transcript versions, response hashes and witness
  coverage counts; it does not establish frozen GENCODE v50 biotype labels,
  expression, cleavage, selectivity or safety.
audience: [maintainers, autonomous research agents, external reviewers]
date: "2026-10-02"
last_verified: "2026-10-02"
---

# Exact-match witness annotation, 2026-10-02

All 19 distinct exact-positive target 16-mers (17 hypothetical, 2 deposited-sequence matches) were annotated using the saved witnesses from revision `6514d5c0399453d5cbd38c3989ba632dfd336d88`. Their 128 saved design–record–window occurrences cover 128/134 (95.52%) of the independently confirmed exact-occurrence census. Fourteen designs have complete witness lists; five are capped. All 60 distinct saved transcript IDs resolved in current Ensembl release 116 with versions matching the frozen FASTA witness IDs. No full transcriptome was downloaded or rescanned.

The uncapped source-result gene lists identify 12 gene labels: CYSTM1, ENSG00000303537, ENSG00000298821, LYPD6B, MAPKAP1, RBBP8-AS1, IDE, ZNF215, EPHA7, CCDST, ANKRD11P1 and MARVELD1. These gene lists are complete for the accepted exact-match census; the saved transcript identities are not complete for capped designs.

The two deposited-sequence target matches are `TCF12_e5__NR4A3_e3:d9`, whose saved witnesses are 20 RBBP8-AS1 lncRNA records out of 22 exact occurrences, and `EWSR1_e7__NR4A3_e2:d6`, whose sole witness is the processed-pseudogene transcript ANKRD11P1-201. This classifies references; it does not establish benignity or biological activity. Four hypothetical `TFG_e2__NR4A3_e3` targets (d6–d9) each have 20 saved ZNF215 witnesses out of 21 occurrences. The two missing RBBP8-AS1 occurrences and four missing ZNF215 design-occurrences remain unassigned to transcript biotypes. They are not necessarily six distinct transcript records.

Among the 60 distinct saved transcripts, 23 are annotated protein_coding, 23 lncRNA, 7 nonsense_mediated_decay, 4 protein_coding_CDS_not_defined, 2 retained_intron, and 1 processed_pseudogene. Among the 128 saved design-occurrences these counts are 71, 26, 18, 10, 2 and 1, respectively. These are explicitly saved-list distributions, not unbiased transcriptome or full-census biotype proportions. Overlapping designs and transcript aliases recur.

The IDE matches are annotated retained_intron transcripts; CYSTM1's match is annotated nonsense_mediated_decay. Gene names alone therefore do not establish that a matched window occurs in a protein-coding transcript. Conversely, annotation as noncoding/NMD/retained-intron does not rule out transcription, accessibility or RNase-H cleavage. No expression, abundance, cleavage, safety, selectivity or clinical-risk inference is made.

Reproduce the annotation join with `annotate-witnesses.ps1` against the saved responses; `fetch-annotations.ps1` retrieves current annotations and would require a new dated receipt if rerun later. `target-annotations.tsv` is the 19-target table; `transcript-annotations.tsv` resolves all 60 saved IDs. Raw response SHA256 values and exact batch request IDs are in `api-receipts.json`. Ensembl `/info/data` returned release 116; the separate transcript lookup was collected seconds later. Matching transcript versions do not prove that all annotation labels are identical to the original GENCODE v50 release.

Sources: [frozen witness table](https://github.com/trimcrae/Rare-cancers/blob/6514d5c0399453d5cbd38c3989ba632dfd336d88/research/autonomy/continuation-2026-10-02/results/aso-exact-match-witnesses.tsv), [frozen full-result census](https://github.com/trimcrae/Rare-cancers/blob/6514d5c0399453d5cbd38c3989ba632dfd336d88/research/autonomy/continuation-2026-10-02/results/aso-transcriptome.json), [Ensembl release API](https://rest.ensembl.org/info/data?content-type=application/json), [Ensembl transcript lookup API](https://rest.ensembl.org/lookup/id/ENST00000378334?content-type=application/json). The batch lookup uses POST only as a read-only query, not an external write.
