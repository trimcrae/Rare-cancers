---
id: DOC-LEE-SEQUENCE-ASSAY-20260906
title: Lee fusion guide and qPCR assay audit
level: —
kind: memo
status: live
date: 2026-09-06
last_verified: 2026-09-06
purpose: Record the bounded sequence and assay findings from published fusion-siRNA experiments.
scope: Two reported fusion systems and 31 designs; exact reference and primer mapping with unchanged published outcome extraction.
audience: [maintainers, autonomous research agents]
---

# Lee sequence and qPCR audit — 2026-09-06

B4N #15 remains a credible reported counterexample to assuming measured-parent sparing solely from junction crossing and absence of a full-length parental match. This bounded audit eliminates an exact-sequence fusion-amplification explanation for the named BRD4 qPCR pair. It does not experimentally establish assay specificity, mechanism, or a causal direct effect on BRD4. SS outcomes remain unverified for full-parent/assay specificity because primary-source SS18/SSX1 reference versions could not be established.

## Verified sequence result

The visually inspected [main Fig.2](https://www.e-crt.org/upload/thumbnails/crt-2022-910f2.jpg) gives `CTCTGACAGCGAAGACTCCGAAACAG|CATCTGCATTGCCGGGACCGGATATGAG`. The left flank uniquely matches BRD4 NM_058243.2 positions2355–2380; the right flank uniquely matches NUTM1 NM_001284292.2 positions483–510. Those coordinates agree with annotated BRD4 exon11 end2380 and NUTM1 exon3 start483. Reconstructed fusion is BRD4 positions1–2380 + NUTM1 positions483–4109. It is a reference-based reconstruction, not a recovered full-length cell-line transcript.

All15 B4N sense cores uniquely match this reconstruction and cross the junction, with left/right contributions3/16 for #1 through17/2 for #15. Every reported antisense core equals the reverse complement of its sense core. Neither 19nt core string has a full exact match in either corresponding parental transcript, using article versions and S3 versions. This is four specified transcript records, not transcriptome/genome-wide specificity and not a near-match assessment. The guide antisense binds the plus-orientation sense target; searching the antisense string in the plus reference is an additional opposite-orientation string audit, not a second demonstrated binding orientation.

S6A displays `CCAGCAGAGGCCTTATGGATATGACCAG|ATCATGCCCAAGAAGCCAGCAGAGGAAGGAAA`. All16 SS cores uniquely match and cross this displayed local junction, with left/right contributions2/17 through17/2. The article XML and all retained supplementary searchable text specify SS18 exon10/SSX1 exon6 but do not identify their transcript version accessions. The named SS primer sequences were recovered from S3; full transcript mapping and predicted SS amplicons are null/unverified. A bounded NCBI search identified alternative/current records, but these do not establish which references the authors used and were not substituted as verified experimental references.

## Assay audit

S3 lists BRD4 NM_058243.3 and NUTM1 NM_001284292.1, whereas article results name BRD4 NM_058243.2 and NUTM1 NM_001284292.2. All four actual version records were retrieved; this discrepancy remains visible. B4N primer results agree across those versions.

| S3 pair | Predicted exact parent amplicon | Predicted exact reconstructed fusion amplicon |
|---|---|---|
| Wild BRD4 | BRD4 .2 and .3:4910–5023,114bp | None; neither primer exact site exists |
| Wild NUTM1 | NUTM1 .1 and .2:429–573,145bp | None; forward site is upstream of retained NUTM1 segment |
| BRD4-NUTM1 | None in all four parent records | 2359–2423,65bp |
| Wild SS18 / SS18-SSX1 | Unverified | Unverified |

Wild BRD4 forward primer starts4910 and reverse-primer reverse complement starts5002 in both BRD4 records. Both sites are downstream of retained BRD4 end2380. This supports intended wild-parent discrimination by exact in-silico PCR. No mismatch-tolerant PCR, thermodynamic amplification model, melt curve, efficiency, amplicon sequencing or empirical specificity validation was performed. Therefore “cannot amplify the fusion” is justified only for the exact-primer model on this reconstructed sequence, not as an experimental impossibility.

## Frozen outcomes and interpretation

B4N #15 has sense `CGAAGACTCCGAAACAGCA`, fusion coordinates2364–2382,17 BRD4 nt and2 NUTM1 nt. The previously frozen S5 parent plotted mean is0.347368 with reading range0.326316–0.368421; fusion mean0.073684 with reading range0.052632–0.094737. These are plotted relative-expression scale values, not asserted Ct-derived fold changes or percent knockdown. No values were redigitized from the newly retrieved figure. All93 existing endpoint rows were joined exactly:31 fusion means,31 measured-parent rows (30 means plus censored SS#4),31 unmeasured second-parent placeholders.

The result supports retaining B4N#15 as an apparent parent-loss example under the bounded sequence/assay checks. It does not establish direct guide-mediated parental targeting, statistical significance, clinical selectivity, both-parent sparing, ASO performance or direct EMC validation. Ct transformation is unspecified, triplicate biological/technical identity unresolved, and source SD differs from digitization reading uncertainty. SS#4 remains right-censored at the source plot ceiling; HS-SY-II/HY-SY-II is a retained source naming inconsistency. Neither second parent has a screen outcome. This is an enabling rank2 external-fusion checkpoint, not a standalone paper.

## Reproduction and provenance

Run `python research/autonomy/lee-sequence-assay-2026-09-06/analyze.py`, then `python research/autonomy/lee-sequence-assay-2026-09-06/verify.py` from this worktree using the bundled Python runtime. No network is required for reproduction. `verify.py` checks all nine inherited source/member hashes, retrieved source hashes, primer transcription, exon boundaries,31 designs/93 endpoint coverage and byte-identical regeneration of six outputs. Both commands passed. No whole-repository preflight or publication checks ran in this sparse worker, and no commit/push/PR was made. A development assertion initially assumed62 outcome rows, then was corrected to93 after observing the31 explicit absent-second-parent rows; no source row was removed or altered.

All coordinates are1-based inclusive; sequences are DNA alphabet for matching and5-prime to3-prime. The printed RNA 3-prime tt overhangs are excluded from19nt cores. `primer-mappings.json` contains forward sites, reverse-complement sites, amplicon sequences and lengths. `design-mappings-and-outcomes.json` contains all designs and unchanged outcome fields. `checks.json` pins frozen input hashes. `retrievals.json` records source URLs, UTC retrieval times, bytes and SHA256, including one429 response and its successful finite retry. PMC browser retrieval encountered a challenge and journal article browser retrieval403; direct primary figure and NCBI sequence retrieval succeeded. RefSeq annotation dates may postdate publication even on named sequence versions; they are not presented as historical annotation snapshots.

Next decision: independently verify the B4N reference reconstruction, S3 assay identity and exact primer coordinates, plus the unchanged B4N#15 outcome join; then integrate this limited result. Keep all16 SS full-reference/assay rows unverified until a source identifying the actual versions or full experimental fusion sequence is available. No further search, model fitting or interpretation is necessary for this checkpoint. Worker computation is complete and nothing remains running.
