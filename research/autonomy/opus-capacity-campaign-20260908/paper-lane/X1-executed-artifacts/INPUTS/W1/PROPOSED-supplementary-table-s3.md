# PROPOSED Supplementary Table S3 — per-junction assembly coordinates

**Status: PROPOSED. Not applied to any manuscript or shared artifact.**

Source (single input): `research/modalities/emc-fet-construct-designs.json`  
sha256 `726aae02ae38b41c34d4398363e3581cfc9e4602d0fe9d65906a4fba79c2048b`  
size 73,415 B  
Assembled 2026-09-08T11:57:48Z by `build_table_s3.py`.

Every cell below is a verbatim copy of a recorded JSON leaf, a fixed column label, or `UNRESOLVED`. No value in this table was derived, inferred, rounded or interpolated.

Input's own status line: COMPUTED DESIGNS FOR SOMEONE ELSE TO VERIFY BEFORE ORDERING. Not validated reagents. Never synthesised, expressed, sequenced or tested by anyone. This repository has been wrong about a fusion junction before — a committed artifact built from a stated Ensembl methodology was off by two exons and silently deleted NR4A3's AF-1 and the first zinc finger of its DNA-binding domain (research/manuscripts/program/target-route-options.md §1.3). Every boundary here therefore carries its provenance, and every construct carries self-checks a reader can audit before spending a cent.

| Field | EWSR1_NR4A3_type1 | EWSR1_NR4A3_type2 | EWSR1_NR4A3_type5 | TAF15_NR4A3 |
|---|---|---|---|---|
| Junction (label) | EWSR1::NR4A3 type 1 — EWSR1 exon 12 :: NR4A3 exon 3 | EWSR1::NR4A3 type 2 — EWSR1 exon 7 :: NR4A3 exon 2 | EWSR1::NR4A3 type 5 — EWSR1 exon 13 :: NR4A3 exon 3 | TAF15::NR4A3 — TAF15 exon 6 :: NR4A3 exon 3 |
| Reported rank | the commonest reported EWSR1::NR4A3 transcript type | the second reported EWSR1::NR4A3 transcript type | a minority reported type | the only reported TAF15::NR4A3 coding junction |
| 5' transcript | ENST00000397938 | ENST00000397938 | ENST00000397938 | ENST00000605844 |
| 5' last exon retained (transcript rank) | 12 | 7 | 13 | 6 |
| 3' transcript | ENST00000395097 | ENST00000395097 | ENST00000395097 | ENST00000395097 |
| 3' first exon retained (transcript rank) | 3 | 2 | 3 | 3 |
| CUT — 5' cDNA nt retained | 1363 | 862 | 1486 | 570 |
| CUT — 5' coding nt retained | 1294 | 793 | 1417 | 484 |
| 5' UTR length (nt) | 69 | 69 | 69 | 86 |
| CUT — 3' cDNA resume offset (0-based) | 697 | 523 | 697 | 697 |
| 3' UTR nt read through | 2 | 176 | 2 | 2 |
| Assembled cDNA length (nt) | 6270 | 5943 | 6393 | 5477 |
| ORF length (nt) | 3174 | 2847 | 3297 | 2364 |
| ORF length (aa) | 1058 | 949 | 1099 | 788 |
| 5' residues fully encoded | 431 | 264 | 472 | 161 |
| Codon split across junction | yes | yes | yes | yes |
| Seam residue index (1-based) | 432 | 265 | 473 | 162 |
| Junction context (aa) | TAKAAVEWFD\|DMPCVQAQYS | SQQSSSYGQQ\|KPTAEEGSPA | GRGMPPPLRG\|DMPCVQAQYS | QRENYSHHTQ\|DMPCVQAQYS |
| Junction context (nt) | AATGGTTTGATG\|ATATGCCCTGCG | ACGGGCAGCAGA\|AGCCCACTGCGG | CACTCCGTGGAG\|ATATGCCCTGCG | ACCACACACAAG\|ATATGCCCTGCG |
| Extra junction-encoded residues | 1 | 59 | 1 | 1 |
| In frame (self-check) | yes | yes | yes | yes |
| 5' start matches partner (self-check) | yes | yes | yes | yes |
| 3' C-terminus intact (self-check) | yes | yes | yes | yes |
| CUT — genomic breakpoint coordinates | UNRESOLVED | UNRESOLVED | UNRESOLVED | UNRESOLVED |

## Reported fusions with no sourced transcript-level junction

| Fusion | Every assembly field | Recorded status |
|---|---|---|
| FUS::NR4A3 | UNRESOLVED | NO transcript-level junction sourced in this repo's literature cache |
| TCF12::NR4A3 | UNRESOLVED | GENOMIC breakpoint only — reported as TCF12 intron 5, not as an mRNA exon junction, and TCF12 has several alternatively-spliced isoforms |

## Limits, copied verbatim from the input's `_limits`

- These are computed designs. Nothing here has been synthesised, expressed or sequenced. A collaborator must verify every junction against their own case's sequenced breakpoint before ordering anything.
- Canonical Ensembl transcripts only. A patient's tumour may use a different transcript or a different breakpoint, in which case the exon→residue map changes and so does the protein.
- The predictions are about DSB-recruitment kinetics only. They say nothing about ATM signalling, ATR dependency, drug sensitivity, efficacy, safety or any clinical question, and nothing downstream may be read as if they did.
- Retained RGG content is one input to recruitment kinetics, not the only one — the source's own data show recruitment also depends in part on native EWSR1, which these constructs do not control.
- FUS::NR4A3 and TCF12::NR4A3 have no sourced transcript-level junction in this repo's literature cache, so no construct is emitted for either. That is a gap in the sourcing, not evidence that the fusions are rare or unimportant.
