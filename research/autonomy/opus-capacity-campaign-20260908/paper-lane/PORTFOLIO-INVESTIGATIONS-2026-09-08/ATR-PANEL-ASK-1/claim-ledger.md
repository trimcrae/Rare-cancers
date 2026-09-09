---
id: DOC-ATR-PANEL-ASK-1-LEDGER
title: "PUB-ATR-PANEL-ASK claim ledger — re-derivation against committed artifacts"
level: L4
kind: evidence
status: live
date: 2026-09-09
last_verified: 2026-09-09
---

# Claim ledger — PUB-ATR-PANEL-ASK

Target: `research/manuscripts/dependency/emc-atr-collaborator-package.md`.
Every quantity below was re-derived on 2026-09-09 from committed artifacts in this checkout. No
network call, no wet lab, no GPU, no paid API. Nothing was applied to the manuscript.

Verdicts: **REPRODUCES** · **MISMATCH** · **NOT-RE-DERIVABLE-LOCALLY** (the exact missing input is named).

## Known-answer control

The harness carries three deliberate control rows so that a broken comparator reports itself:
`KAC-POS` (a true value, must REPRODUCE), `KAC-NEG` and `KACB-NEG` (values altered by one digit,
must MISMATCH) and `KAC-PATH` (a non-existent artifact path, must MISMATCH). All four behaved as
required, so a silent-pass harness is excluded. **They are the only MISMATCH rows in this ledger;
every substantive row reproduces.**

## Artifacts read

| artifact | sha256 |
|---|---|
| `emc-fet-construct-designs.json` | `726aae02ae38b41c34d4398363e3581cfc9e4602d0fe9d65906a4fba79c2048b` |
| `emc-fet-frame-and-composition.json` | `eb92812555c9239c57791af2c51dbdc0e8c2d1b7d0fac140e0f590ae43b43cb8` |
| `emc-construct-inputs.json` | `9166e09ec8e9d0bb5e3356c4334dbb2789cb26ae98d21fe6093afa2b2d23c47b` |
| `emc-fet-idr-census.json` | `72f4ba902ecc709156d1e1758663644e0e2ed9ff6fdf69925e18f1aa4f59646b` |
| `emc-prior-art-2026-08-09.json` | `3c45960a14a99ce739b7643c2f73705e3d0b8900841af1a289f9e534379d4112` |
| `emc-atr-figure-provenance.json` | `7fcff0800d18a585ba5a358abf63be5bf3333b196ae7357cd71cf1adb79209f3` |

## Part A — constructs, seam, frame rule, axis, composition, gene models

| id | section | claim | manuscript value | artifact value | verdict |
|---|---|---|---|---|---|
| `C-ORF-EWSR1::NR4A3 type 1` | 3.2/Tab2/S3 | ORF length aa, EWSR1::NR4A3 type 1 | `1058` | `1058` | **REPRODUCES** |
| `C-EXT-EWSR1::NR4A3 type 1` | 3.2/Tab2/S3 | extra junction residues, EWSR1::NR4A3 type 1 | `1` | `1` | **REPRODUCES** |
| `C-RET-EWSR1::NR4A3 type 1` | 3.2/Tab2/S3 | 5' residues fully encoded, EWSR1::NR4A3 type 1 | `431` | `431` | **REPRODUCES** |
| `C-IF-EWSR1::NR4A3 type 1` | 3.2 | in-frame self-check, EWSR1::NR4A3 type 1 | `True` | `True` | **REPRODUCES** |
| `C-ORF-EWSR1::NR4A3 type 2` | 3.2/Tab2/S3 | ORF length aa, EWSR1::NR4A3 type 2 | `949` | `949` | **REPRODUCES** |
| `C-EXT-EWSR1::NR4A3 type 2` | 3.2/Tab2/S3 | extra junction residues, EWSR1::NR4A3 type 2 | `59` | `59` | **REPRODUCES** |
| `C-RET-EWSR1::NR4A3 type 2` | 3.2/Tab2/S3 | 5' residues fully encoded, EWSR1::NR4A3 type 2 | `264` | `264` | **REPRODUCES** |
| `C-IF-EWSR1::NR4A3 type 2` | 3.2 | in-frame self-check, EWSR1::NR4A3 type 2 | `True` | `True` | **REPRODUCES** |
| `C-ORF-EWSR1::NR4A3 type 5` | 3.2/Tab2/S3 | ORF length aa, EWSR1::NR4A3 type 5 | `1099` | `1099` | **REPRODUCES** |
| `C-EXT-EWSR1::NR4A3 type 5` | 3.2/Tab2/S3 | extra junction residues, EWSR1::NR4A3 type 5 | `1` | `1` | **REPRODUCES** |
| `C-RET-EWSR1::NR4A3 type 5` | 3.2/Tab2/S3 | 5' residues fully encoded, EWSR1::NR4A3 type 5 | `472` | `472` | **REPRODUCES** |
| `C-IF-EWSR1::NR4A3 type 5` | 3.2 | in-frame self-check, EWSR1::NR4A3 type 5 | `True` | `True` | **REPRODUCES** |
| `C-ORF-TAF15::NR4A3` | 3.2/Tab2/S3 | ORF length aa, TAF15::NR4A3 | `788` | `788` | **REPRODUCES** |
| `C-EXT-TAF15::NR4A3` | 3.2/Tab2/S3 | extra junction residues, TAF15::NR4A3 | `1` | `1` | **REPRODUCES** |
| `C-RET-TAF15::NR4A3` | 3.2/Tab2/S3 | 5' residues fully encoded, TAF15::NR4A3 | `161` | `161` | **REPRODUCES** |
| `C-IF-TAF15::NR4A3` | 3.2 | in-frame self-check, TAF15::NR4A3 | `True` | `True` | **REPRODUCES** |
| `S-793` | 3.3/Fig1C | EWSR1 coding nt through exon 7 | `793` | `793` | **REPRODUCES** |
| `S-264` | 3.3/Fig1C | EWSR1 whole codons | `264` | `264` | **REPRODUCES** |
| `S-177` | 3.3/Fig1C | nt spanned by the extra residues | `177` | `177` | **REPRODUCES** |
| `S-176` | 3.3/Fig1C | NR4A3 5'UTR nt retained total | `176` | `176` | **REPRODUCES** |
| `S-174` | 3.3/Fig1C | NR4A3 5'UTR nt from exon 2 | `174` | `174` | **REPRODUCES** |
| `S-2` | 3.3/Fig1C | NR4A3 5'UTR nt from exon 3 | `2` | `2` | **REPRODUCES** |
| `S-59` | 3.3/Fig1C | extra residues | `59` | `59` | **REPRODUCES** |
| `S-58` | 3.3/Fig1C | remaining residues NR4A3 alone | `58` | `58` | **REPRODUCES** |
| `S-AAG` | 3.3/Fig1C | first extra residue codon | `AAG` | `AAG` | **REPRODUCES** |
| `S-K265` | 3.3/Fig1C | first extra residue is K at position 265 | `('K', 265)` | `('K', 265)` | **REPRODUCES** |
| `S-NOSTOP` | 3.3/Fig1C | no internal stop codon in extension | `False` | `False` | **REPRODUCES** |
| `S-949` | 3.3/Fig1C | chimeric ORF length aa | `949` | `949` | **REPRODUCES** |
| `F-PH1` | 3.2 | EWSR1 phase-1 donor exon set | `[1, 4, 7, 9, 10, 12, 13, 15]` | `[1, 4, 7, 9, 10, 12, 13, 15]` | **REPRODUCES** |
| `F-E2LEN` | 3.2 | NR4A3 exon 2 length nt | `174` | `174` | **REPRODUCES** |
| `F-ALL` | 3.2 | rule holds for every EWSR1 donor | `True` | `True` | **REPRODUCES** |
| `F-TAF484` | 3.2 | TAF15 coding nt through exon 6 | `484` | `484` | **REPRODUCES** |
| `AX-RG-EWSR1::NR4A3 type 1` | 3.4/Tab3 | retained RG / total, EWSR1::NR4A3 type 1 | `(8, 30)` | `(8, 30)` | **REPRODUCES** |
| `AX-FR-EWSR1::NR4A3 type 1` | 3.4/Tab3 | retained-RG fraction, EWSR1::NR4A3 type 1 | `0.267` | `0.267` | **REPRODUCES** |
| `AX-RG-EWSR1::NR4A3 type 2` | 3.4/Tab3 | retained RG / total, EWSR1::NR4A3 type 2 | `(0, 30)` | `(0, 30)` | **REPRODUCES** |
| `AX-FR-EWSR1::NR4A3 type 2` | 3.4/Tab3 | retained-RG fraction, EWSR1::NR4A3 type 2 | `0.0` | `0.0` | **REPRODUCES** |
| `AX-RG-EWSR1::NR4A3 type 5` | 3.4/Tab3 | retained RG / total, EWSR1::NR4A3 type 5 | `(11, 30)` | `(11, 30)` | **REPRODUCES** |
| `AX-FR-EWSR1::NR4A3 type 5` | 3.4/Tab3 | retained-RG fraction, EWSR1::NR4A3 type 5 | `0.367` | `0.367` | **REPRODUCES** |
| `AX-RG-TAF15::NR4A3` | 3.4/Tab3 | retained RG / total, TAF15::NR4A3 | `(0, 31)` | `(0, 31)` | **REPRODUCES** |
| `AX-FR-TAF15::NR4A3` | 3.4/Tab3 | retained-RG fraction, TAF15::NR4A3 | `0.0` | `0.0` | **REPRODUCES** |
| `AXR-EWSR1::FLI1 (Ewing, type 1) — EWSR1 e7` | 3.4/Tab3 | comparator RG/fraction, EWSR1::FLI1 (Ewing, type 1) — EWSR1 e7 | `(0, 0.0)` | `(0, 0.0)` | **REPRODUCES** |
| `AXR-EWSR1::ATF1 (clear cell, reported type) — EWSR1 e7` | 3.4/Tab3 | comparator RG/fraction, EWSR1::ATF1 (clear cell, reported type) — EWSR1 e7 | `(0, 0.0)` | `(0, 0.0)` | **REPRODUCES** |
| `AXR-EWSR1::ATF1 (clear cell, commonest type) — EWSR1 e8` | 3.4/Tab3 | comparator RG/fraction, EWSR1::ATF1 (clear cell, commonest type) — EWSR1 e8 | `(7, 0.233)` | `(7, 0.233)` | **REPRODUCES** |
| `AXR-EWSR1::ATF1 (clear cell, reported type) — EWSR1 e10` | 3.4/Tab3 | comparator RG/fraction, EWSR1::ATF1 (clear cell, reported type) — EWSR1 e10 | `(8, 0.267)` | `(8, 0.267)` | **REPRODUCES** |
| `AX-SPAN` | 3.4/Tab3/Fig1B | EWSR1::ATF1 comparator span | `[0.0, 0.267]` | `[0.0, 0.267]` | **REPRODUCES** |
| `AX-MEAS` | 3.4 | firmly measured fractions | `[0.0, 1.0]` | `[0.0, 1.0]` | **REPRODUCES** |
| `T-LOW` | 3.5/Tab4 | lowest FET prefix value | `0.439` | `0.439` | **REPRODUCES** |
| `T-LOWP` | 3.5/Tab4 | lowest FET prefix protein and span | `('EWSR1', [1, 560])` | `('EWSR1', [1, 560])` | **REPRODUCES** |
| `T-BEST` | 3.5/Tab4 | best TCF12 prefix value | `0.4` | `0.4` | **REPRODUCES** |
| `T-GAP` | 3.5/Tab4 | sweep gap | `0.039` | `0.039` | **REPRODUCES** |
| `T-NONE` | 3.5/Tab4 | no TCF12 prefix reaches lowest FET prefix | `False` | `False` | **REPRODUCES** |
| `T-RG` | 3.5/Tab4 | whole-protein RG: EWSR1,TAF15,FUS,TCF12 | `(30, 31, 24, 7)` | `(30, 31, 24, 7)` | **REPRODUCES** |
| `T-BSPAN` | 3.5/Tab4 | TCF12 best prefix span 1-160 | `[1, 160]` | `[1, 160]` | **REPRODUCES** |
| `M-175` | 3.4/P3 | TAF15 first RG position | `175` | `175` | **REPRODUCES** |
| `M-161` | 3.4/P3 | TAF15 retained at exon 6 | `161` | `161` | **REPRODUCES** |
| `M-14` | 3.4/P3 | distance to first RG (headroom claimed 14) | `14` | `14` | **REPRODUCES** |
| `M-174` | 3.4 | artifact rg_free_ceiling stored value 174 | `174` | `174` | **REPRODUCES** |
| `M-13` | 3.4 | artifact headroom stored value 13 | `13` | `13` | **REPRODUCES** |
| `G-TR-EWSR1` | S1 | transcript accession, EWSR1 | `ENST00000397938` | `ENST00000397938` | **REPRODUCES** |
| `G-EX-EWSR1` | S1 | transcript exon count, EWSR1 | `17` | `17` | **REPRODUCES** |
| `G-PL-EWSR1` | S1 | protein length aa, EWSR1 | `656` | `656` | **REPRODUCES** |
| `G-TR-TAF15` | S1 | transcript accession, TAF15 | `ENST00000605844` | `ENST00000605844` | **REPRODUCES** |
| `G-EX-TAF15` | S1 | transcript exon count, TAF15 | `16` | `16` | **REPRODUCES** |
| `G-PL-TAF15` | S1 | protein length aa, TAF15 | `592` | `592` | **REPRODUCES** |
| `G-TR-FUS` | S1 | transcript accession, FUS | `ENST00000254108` | `ENST00000254108` | **REPRODUCES** |
| `G-EX-FUS` | S1 | transcript exon count, FUS | `15` | `15` | **REPRODUCES** |
| `G-PL-FUS` | S1 | protein length aa, FUS | `526` | `526` | **REPRODUCES** |
| `G-TR-NR4A3` | S1 | transcript accession, NR4A3 | `ENST00000395097` | `ENST00000395097` | **REPRODUCES** |
| `G-EX-NR4A3` | S1 | transcript exon count, NR4A3 | `8` | `8` | **REPRODUCES** |
| `G-PL-NR4A3` | S1 | protein length aa, NR4A3 | `626` | `626` | **REPRODUCES** |
| `G-TR-TCF12` | S1 | transcript accession, TCF12 | `ENST00000333725` | `ENST00000333725` | **REPRODUCES** |
| `G-EX-TCF12` | S1 | transcript exon count, TCF12 | `21` | `21` | **REPRODUCES** |
| `G-PL-TCF12` | S1 | protein length aa, TCF12 | `706` | `706` | **REPRODUCES** |
| `G-UNI-TCF12` | S1 | UniProt TCF12 length 682 | `682` | `682` | **REPRODUCES** |
| `G-CACHE-DATE` | S1 | cache retrieval date 2026-08-12 | `2026-08-12` | `2026-08-12` | **REPRODUCES** |
| `KAC-POS` | control | positive control: 949 vs artifact 949 | `949` | `949` | **REPRODUCES** |
| `KAC-NEG` | control | NEGATIVE control: deliberately wrong 950 must report MISMATCH | `950` | `949` | **MISMATCH** |
| `KAC-PATH` | control | absent-path control: must report MISMATCH | `anything` | `<ABSENT:no_such_field>` | **MISMATCH** |

TOTAL 78 rows; MISMATCH 2
  MISMATCH: KAC-NEG | manuscript 950 | artifact 949
  MISMATCH: KAC-PATH | manuscript 'anything' | artifact '<ABSENT:no_such_field>'


## Part B — Table 4 detail, prior-art screen, and the not-locally-re-derivable rows

| id | section | claim | manuscript value | re-derived / missing input | verdict |
|---|---|---|---|---|---|
| `B-SYGQ` | 3.5/Tab4 | N-terminal 250-aa [S,Y,G,Q]: EWSR1,TAF15,FUS,TCF12 | `(0.54, 0.62, 0.804, 0.368)` | `(0.54, 0.62, 0.804, 0.368)` | **REPRODUCES** |
| `B-GRID` | 3.5 | grid prefix counts TCF12,EWSR1,TAF15,FUS | `(66, 61, 55, 48)` | `(66, 61, 55, 48)` | **REPRODUCES** |
| `B-IDFET` | 3.5/Tab4 | FET-vs-FET identity range | `(26.1, 35.7)` | `(26.1, 35.7)` | **REPRODUCES** |
| `B-IDTC` | 3.5/Tab4 | TCF12-vs-FET identity range | `(16.8, 20.5)` | `(16.8, 20.5)` | **REPRODUCES** |
| `B-BOX` | 3.5/Tab4 | operational RGG boxes EWSR1,TAF15,FUS,TCF12 | `(2, 1, 2, 0)` | `(2, 1, 2, 0)` | **REPRODUCES** |
| `B-RG2` | 3.5/Tab4 | whole-protein RG in the TCF12 test block | `(30, 31, 24, 7)` | `(30, 31, 24, 7)` | **REPRODUCES** |
| `KACB-NEG` | control | NEGATIVE control: boxes claimed (2,1,2,1) must MISMATCH | `(2, 1, 2, 1)` | `(2, 1, 2, 0)` | **MISMATCH** |
| `B-PA-N` | 1 | prior-art screen record count | `322` | `322` | **REPRODUCES** |
| `B-PA-FT` | 1 | prior-art full-text count | `238` | `238` | **REPRODUCES** |
| `B-PA-HIT` | 1 | prior-art ATR / replication-stress hits | `0` | `0` | **REPRODUCES** |
| `B-S3-SHA` | S3 | cited sha256 of emc-fet-construct-designs.json | `726aae02ae38b41c34d4398363e3581cfc9e4602d0fe9d65906a4fba79c2048b` | `726aae02ae38b41c34d4398363e3581cfc9e4602d0fe9d65906a4fba79c2048b` | **REPRODUCES** |
| `N-PAZO` | 1 | pazopanib ORR 18 per cent, median PFS 19 months, NCT02066285 | `18% / 19 mo` | `missing input: ref [2] (PMID 41055792) full text; no committed artifact in this repo holds the extracted trial numbers` | **NOT-RE-DERIVABLE-LOCALLY** |
| `N-REF1` | 1,3.4,5 | reference 1 measured recruitment anchors 0.000 and 1.000, and the quoted methods paragraph | `measured in ref [1]` | `missing input: ref [1] (PMID 41811428) primary data; the axis artifact stores the placement, not the recruitment measurement` | **NOT-RE-DERIVABLE-LOCALLY** |
| `N-CNT` | 3.1/Tab1 | counted series frequencies (10 tumours; 11 of 15; 3 of 15; 4 of 10; 1 of 26) | `quoted counts` | `missing input: refs [6,7,9,10] full text; frame-and-composition holds quotations for 3 series only, not the 1-of-26 TCF12 count` | **NOT-RE-DERIVABLE-LOCALLY** |
| `N-GENOMIC` | S3 | genomic breakpoint coordinates for all four junctions | `UNRESOLVED` | `missing input: a sequenced breakpoint; the input cache carries transcript/cDNA coordinates only — the manuscript states this` | **NOT-RE-DERIVABLE-LOCALLY** |
| `N-ANNOT` | 2.6/Lim3 | exon-rank-to-nucleotide correspondence verified against a second annotation source | `not claimed` | `missing input: a second, independent annotation retrieval; one offline cache only — the manuscript states this` | **NOT-RE-DERIVABLE-LOCALLY** |
| `N-TCF12FUS` | 3.1/S3 | TCF12::NR4A3 and FUS::NR4A3 transcript-level junctions | `UNRESOLVED` | `missing input: an exon-level breakpoint statement in a published source; none retrieved — the manuscript states this` | **NOT-RE-DERIVABLE-LOCALLY** |

{'REPRODUCES': 10, 'MISMATCH': 1, 'NOT-RE-DERIVABLE-LOCALLY': 6}
  MISMATCH: KACB-NEG | manuscript (2, 1, 2, 1) | artifact (2, 1, 2, 0)
