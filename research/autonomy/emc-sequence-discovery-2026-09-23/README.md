---
id: DOC-EMC-SEQUENCE-DISCOVERY-CLOSEOUT-20260924
title: EMC public-sequence discovery campaign closeout
level: L3
kind: memo
status: historical
purpose: Preserve the no-go decision, evidence and recovery procedure for a shelved campaign.
scope: Public EMC sequence-discovery pilot conducted September 23-24, 2026.
audience: [maintainers, autonomous research agents]
date: 2026-09-24
last_verified: 2026-09-24
---

# EMC public-sequence discovery: shelved

**No paper-worthy finding was established. Stop this campaign with the currently accessible data and validation resources.** The user requested documentation, integration and shelving on September 24, 2026. Do not resume collectors, BLAST polling, agent launches or automatic follow-up from historical instructions in this archive.

This is a decision about this public-sequence mining route, not proof that undiscovered EMC transcripts do not exist or a conclusion about the broader EMC research program. Additional agents cannot supply the missing independent specimens or biological validation. The three requested worker starts produced no results; this packet is coordinator-executed research and does not evaluate parallel-agent performance.

## Result and evidence

The screen examined **132,380,492 read records**, retaining **5,497 bait-matching records**, from three runs representing **two deposited cell models**. SRR3380704 was partial (27,100,816 records); SRR3380705 (51,389,642) and SRR33903995 (53,890,034) completed both mate files with source MD5 verification. The two V1-34 runs share a sample/experiment. Counts are not independent molecules, patients or a clinical cohort. The initial USZ pilot prefix is not counted twice.

- Established EWSR1–NR4A3 fusion joins were recovered. USZ supplied 102 qualifying canonical-junction records from 88 fragment IDs; the other V1-34 run supplied 12 records from 11 fragments. Its alternative-exon entry supplied two records from two fragments; the 72-nt exon was already known.
- H05, a 70-nt within-exon repeat, had two mates from one original fragment. Its exact seam did not recur in the completed other V1-34 run or USZ retained reads. Biological authenticity remains unresolved; technical artifact is plausible, not proven.
- Other apparent splice events were already represented in normal-background GTEx calls. Several mismatches/indels had catalogued variant explanations. These observations establish neither genotype nor somatic origin.
- H11, an exploratory shifted fusion acceptor, remains one high-quality exact read from one fragment. A known normal acceptor does not establish prior observation of that fusion join. Novelty, authenticity and utility remain unresolved.

The [preserved final decision](DECISION.md) gives candidate dispositions, coverage limits and reopening conditions. Its September 23 title is historical; the evidence closeout and shelving occurred September 24. Repository frontmatter was added to the readable copy; the original remains byte-for-byte inside the archive. File references in that decision resolve under the extracted packet's `round2/` directory, not beside this README. Its statement that the packet had not changed the repository describes its pre-integration state.

One H05 genomic BLAST request (`B8ZK595Y014`) was still WAITING at the last recorded observation, September 24 at 02:55:41 UTC. This is a historical pending result, not a negative result or a running local job. It is not being monitored. All local collectors and final analyses had exited at scientific closeout. No manuscript or clinical registry change follows from this result.

## Preserved packet and offline reproduction

`evidence-packet.tar.gz` preserves all original files, including contracts, amendments, source receipts, retained reads and qualities, scripts, candidate dispositions, negative results and historical checkpoints. `archive-manifest.json` records its hash and size; `closing-manifest.json` is the original per-file hash manifest, also present inside the archive. Original absolute paths and launch instructions are historical provenance. No full raw FASTQ files were retained; an offline audit cannot independently repeat their source-stream MD5 calculation.

From this directory, using Python 3.12 or later:

```text
python -X utf8 verify_archive.py
python -X utf8 verify_archive.py --extract PATH_TO_NEW_EMPTY_DIRECTORY
python -X utf8 PATH_TO_NEW_EMPTY_DIRECTORY/round2/audit_completion.py
```

The verifier checks the archive hash, exact member set and every original file hash before extraction. The audit reconciles retained evidence and quantitative claims without network access; it writes a fresh audit receipt only in the extracted copy. Allow approximately 20 MiB for extraction and keep at least 10 GiB free. Do not run archived collectors or supervisors. The source packet remains at its original location, recorded in `archive-manifest.json`.

Authoritative extracted files are `round2/DECISION.md`, `round2/completion-audit.json`, `round2/usz-final-analysis.json` and `round2/v1-replication-final-analysis.json`. The explicitly invalid `usz-final-analysis-premature-snapshot.json` is retained solely for provenance. Five earlier USZ outputs are losslessly compressed under `round2/snapshots/`; their recovery hashes are checked by the audit. Earlier checkpoint instructions are superseded by this closeout.

The packet also demonstrates overlap double-counting and synthetic FASTQ quality-line matching in a legacy scanner. These known-answer failures are useful engineering evidence; they do not correct historical counts automatically, establish a new publishable method or mean the repository scanner was patched here.

## Shelving and reopening

`status.json` records the shelving decision and disables automatic resumption for this campaign. It is a closeout record, not a scheduler registration. No shared queue or global research coordinator ownership is changed. Reopening requires a new explicit user instruction, ideally accompanied by new confirmed EMC sequence data, independent-library/long-read support for a specific candidate, or a collaborator able to validate a compelling hypothesis. Repeating this search with more agents alone does not address the observed constraint.

See `validation.json` for actual integration checks. This archive is not a publication candidate and makes no clinical efficacy, safety or therapeutic-window claim.
