# Annotation evidence for the two deposited-sequence exact matches

Checked 2026-10-02 using small primary-resource API responses only. This is an
annotation and two-representative-sequence check, not a whole-corpus census,
normal-tissue expression analysis or off-target activity experiment.

## Starting evidence

The frozen witness table at commit
d39296bdf4114e7bf366c8a9ffeefc22e6cfb71f supplies transcript IDs, zero-based cDNA offsets
and target-oriented windows:
https://github.com/trimcrae/Rare-cancers/blob/d39296bdf4114e7bf366c8a9ffeefc22e6cfb71f/research/autonomy/continuation-2026-10-02/results/aso-exact-match-witnesses.tsv

The discovery result reports 22 RBBP8-AS1 record-window occurrences for
TCF12_e5__NR4A3_e3:d9 and one ANKRD11P1 occurrence for EWSR1_e7__NR4A3_e2:d6.
The witness TSV includes the first 20 RBBP8-AS1 records, not all 22; this review
does not infer the identities of its two omitted records.

## Directly confirmed representative annotations and sequences

| Field | RBBP8-AS1 representative | ANKRD11P1 representative |
|---|---|---|
| Frozen witness transcript | ENST00000795030.1 | ENST00000378334.3 |
| Current lookup ID/version | ENST00000795030 / 1 | ENST00000378334 / 3 |
| Display name | RBBP8-AS1-222 | ANKRD11P1-201 |
| Parent gene | ENSG00000266850 | ENSG00000234429 |
| Transcript biotype | lncRNA | processed_pseudogene |
| Annotation source | havana_tagene | havana |
| Source logic name | havana_tagene_homo_sapiens | havana_homo_sapiens |
| Spliced cDNA length | 1336 nt | 6848 nt |
| Exon count | 6 | 1 |
| Assembly / chromosome / strand | GRCh38 / 18 / minus | GRCh38 / 2 / minus |
| Reported canonical flag | 0 | 1 |
| Reported GENCODE primary flag | 0 | 1 |
| Frozen zero-based window start | 345 | 3419 |
| Corresponding one-based cDNA interval | 346–361 | 3420–3435 |
| Live cDNA substring | ATCTGATGGATATGCC | AGCAGAAGCCCACTGC |
| Agreement with frozen target | Exact, 16/16 | Exact, 16/16 |

Current lookup calls used stable IDs without version suffixes, then checked the
returned version explicitly against each frozen witness. Current cDNA sequences
were fetched independently of the GENCODE discovery FASTA and sliced at the recorded
offsets. Both returned the expected 16-mer. These are independent representative
sequence confirmations; they do not reproduce the 22/1 occurrence totals.

Lookup URLs:
- https://rest.ensembl.org/lookup/id/ENST00000795030?expand=1;content-type=application/json
- https://rest.ensembl.org/lookup/id/ENST00000378334?expand=1;content-type=application/json

cDNA URLs:
- https://rest.ensembl.org/sequence/id/ENST00000795030?type=cdna;content-type=application/json
- https://rest.ensembl.org/sequence/id/ENST00000378334?type=cdna;content-type=application/json

The documented lookup and sequence APIs are:
https://rest.ensembl.org/documentation/info/lookup
https://rest.ensembl.org/documentation/info/sequence_id

## Exon location

ANKRD11P1's sole exon is ENSE00001726407.1, chr2:81194337–81201184 on the minus
strand. Ensembl's cDNA mapping API directly maps cDNA3420–3435 to
GRCh38 chr2:81197750–81197765, minus strand, one contiguous block (gap=0).
Thus this representative window lies within the single annotated exon.
https://rest.ensembl.org/map/cdna/ENST00000378334/3420..3435?content-type=application/json

For RBBP8-AS1, the lookup response lists exon1 ENSE00004179470.1,
chr18:22872958–22873275 (318 nt), followed in transcript order by exon2
ENSE00002726011.1, chr18:22791124–22791199 (76 nt), both minus-strand.
The witness window at cDNA346–361 is therefore within exon2. Direct arithmetic
on these exon coordinates gives GRCh38 chr18:22791157–22791172, minus strand:
the first window base is 27 bases after exon2's transcript-oriented beginning.
This coordinate was derived from returned exon structure; it was NOT separately
confirmed by the mapping endpoint, which returned HTTP503 for that query.

The representative matches are therefore internal to annotated exons, rather than
requiring a splice boundary at the 16-mer in either representative. This conclusion
does not assert exon structure for every other RBBP8-AS1 isoform.

Mapping API documentation:
https://rest.ensembl.org/documentation/info/assembly_cdna

## All 20 listed RBBP8-AS1 witness models

A single expanded current lookup of ENSG00000266850 returned gene version2,
biotype lncRNA, gene source havana, and 118 transcript models. All 20 transcript IDs
listed in the frozen witness TSV were present, each at version1, each with biotype
lncRNA and source havana_tagene. They are:

ENST00000795030.1, ENST00000795022.1, ENST00000795029.1, ENST00000795080.1,
ENST00000795069.1, ENST00000795073.1, ENST00000795082.1, ENST00000795105.1,
ENST00000795102.1, ENST00000795100.1, ENST00000795091.1, ENST00000795093.1,
ENST00000795096.1, ENST00000795083.1, ENST00000795084.1, ENST00000795079.1,
ENST00000795081.1, ENST00000795077.1, ENST00000795076.1, ENST00000795114.1.

This is an annotation join for the listed IDs; only the representative
ENST00000795030.1 cDNA was independently sliced in this task.
https://rest.ensembl.org/lookup/id/ENSG00000266850?expand=1;content-type=application/json

GENCODE describes TAGENE as a manually supervised computational annotation workflow
integrating long-read-derived models. Its tag documentation defines TAGENE as
transcripts created or extended using assembled long-read RNA-seq data.
That context qualifies the havana_tagene source label; it is not locus-specific
proof of expression in a therapeutic exposure tissue or independent functional
validation of each predicted transcript.

Primary documentation:
- https://www.gencodegenes.org/pages/cls_lncrnas/
- https://www.gencodegenes.org/pages/tags.html
- https://academic.oup.com/nar/article/53/D1/D966/7905300

## Gene identities and annotation-system differences

HGNC confirms RBBP8-AS1 as approved HGNC:58091, RBBP8 antisense RNA1, locus type
RNA,long non-coding, ENSG00000266850:
https://rest.genenames.org/fetch/symbol/RBBP8-AS1
https://www.genenames.org/data/gene-symbol-report/#!/hgnc_id/HGNC:58091

NCBI Gene identifies ANKRD11P1 as GeneID100287912, ANKRD11 pseudogene1,
HGNC:54737 / ENSG00000234429, gene type pseudo and RefSeq status INFERRED:
https://www.ncbi.nlm.nih.gov/gene/100287912

NCBI's displayed GRCh38.p14 gene interval is chr2:81194139–81201179, complement.
This differs from the Ensembl transcript/exon interval above. These are different
annotation objects and sources; they must not be substituted for one another when
assigning the target's transcript coordinate. NCBI's general pseudo designation
does not replace Ensembl's specific processed_pseudogene transcript classification.

The current Ensembl lookup versions matched both selected GENCODE50 witnesses, but
the API is mutable. The Ensembl info/data version request returned HTTP503, so this
task did not establish the live API's release number. Do not equate all live API
models with a frozen release merely from access date. The discovery FASTA remains
the original counted source:
https://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_human/release_50/gencode.v50.transcripts.fa.gz
SHA256 5a320f524d73b5793518eb19b118829033713443d0f42af20a67bb31cc06cf56.

GENCODE's ALL transcript resource includes reference chromosomes, scaffolds,
patches and alternate loci. Occurrence totals count records/windows rather than
independent loci or expression observations:
https://www.gencodegenes.org/human/

## Supported wording and limits

Supported: "Two deposited-fusion-supported design sequences also occur in annotated
reference transcripts: a long-noncoding RBBP8-AS1 model and the processed-pseudogene
ANKRD11P1 model. Current Ensembl cDNA records with matching transcript versions
independently reproduce representative 16-base windows at the saved positions."

Avoid "normal-tissue off-target", "expressed harmful off-target", "protein-coding
off-target" or claims of cleavage, toxicity or safety from these annotations.
Pseudogene/noncoding status neither establishes a relevant ASO substrate in vivo
nor establishes its absence. No expression query, assay evidence or clinical-risk
estimate was generated.

The whole-corpus exact-match census and full occurrence identities remain the
coordinator's separate verification task. This document should accompany, not
replace, that receipt. No GTF, genome or transcriptome bulk file was downloaded.

