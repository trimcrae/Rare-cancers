---
id: DOC-EMC-SEQUENCE-DISCOVERY-DECISION-20260924
title: EMC sequence-discovery final decision
level: L3
kind: historical
status: historical
purpose: Preserve the campaign decision and its evidence limitations at scientific closeout.
scope: Public EMC sequence discovery with the data and validation resources available September 24, 2026.
audience: [maintainers, autonomous research agents]
date: 2026-09-24
last_verified: 2026-09-24
---

# EMC sequence-discovery decision — September 23, 2026

**Decision: stop this open-ended sequence-mining campaign with the currently accessible data and validation resources. No paper-worthy finding was established.** This is a research-priority judgment based on the evidence below, not proof that no undiscovered EMC transcript exists or that all EMC research is fruitless. More parallel agents are unlikely to solve the observed shortage of independent, well-characterized samples and validation.

The three run-specific screens examined **132,380,492 read records** and retained 5,497 bait matches. Four mate files were completed and their full source MD5s verified; the two original V1-34 mate files remain partial. Repeated examination of the initial USZ pilot prefix is not added to this total. These are records from two deposited cell models, not millions of independent molecules or a clinical cohort.

| Run | Material | Records examined | Completion |
|---|---|---:|---|
| SRR3380704 | V1-34, first run | 27,100,816 | Partial prefixes; transport failures; no full-file checksum verification |
| SRR3380705 | V1-34, other run from the same sample/experiment | 51,389,642 | Both files complete, expected source MD5s verified |
| SRR33903995 | USZ-23_EMC3 | 53,890,034 | Both files complete, expected source MD5s verified |

## What would justify a paper

The original question was whether accessible EMC data contain recurrent transcript features missed by existing annotations or target designs. A useful result needs a nontrivial new observation, credible evidence separating it from known human sequences and technical artifacts, and a coherent biological or methodological contribution. A pile of unexplained short reads does not meet that standard. Neither do repeated database annotations, two mates from one fragment, or multiple run accessions from one sample.

## Evidence already settled

- **Known fusion recovered.** The complete USZ-23_EMC3 dataset contains 53,890,034 read records, with both source MD5s verified. The strict exact-read junction check finds 102 qualifying reads, 88 fragment IDs and 22 oriented starts across the established EWSR1–NR4A3 join. Those counts are not unique original molecules. See `usz-final-analysis.json`.
- **Both published fusion entry joins recovered.** The completed V1-34 replication has 12 qualifying canonical-junction records from 11 fragment IDs and two qualifying alternative-exon-entry records from two fragment IDs. The 72-nt exon already occurs in the repository's evidence and normal RefSeq NM_173200.3. This confirms the publisher's processed report; it is not a new exon discovery. No qualifying read phases the alternative entry to the proposed downstream continuation.
- **Variants, not novel events.** Full-read explanations include catalogued rs3837280, rs753648433, rs202143889 and rs1180697223. A recurrent UTR mismatch corresponds to rs141819687. These checks do not establish a genotype, somatic origin or clinical consequence. Some short-indel groups remain unassigned; they have one oriented read interval, and one catalogue lookup failed.
- **Apparent novel splice already observed outside this model.** The H06 upstream junction is called in 101 GTEx samples, with 113 junction reads. The USZ evidence is four read IDs but one distinct oriented sequence. GTEx samples are not necessarily distinct donors, and its calls are not functional isoform validation. See `H06-upstream-splice-disposition.json`.
- **H05 repeat did not recur in the replication screen.** Two mates from one original V1-34 fragment support a 70-nt within-exon repeat. They agree over 84 nt and have adequate junction-flank quality. Its exact seam is absent from both the completed other V1-34 run and the completed USZ retained reads. It is not phased to EWSR1, and RT/library artifacts remain plausible. Zero recovered matches is a result of this targeted screen, not proof of biological absence. See `v1-replication-final-analysis.json` and `H05-read-verification.json`.
- **Other provisional joins do not rescue the campaign.** Three additional large repeat-like joins each have one fragment. A further splice-like join is already called in 1,019 GTEx samples (1,779 junction reads). An exploratory EWSR1 fusion model using an NR4A3 acceptor 42 nt downstream has one high-quality exact read from one fragment. The acceptor is known in GTEx, but that does not establish prior observation of this particular fusion join. Its novelty and biological authenticity remain unresolved, and it lacks replication or demonstrated utility. See `all-runs-exact-event-recurrence.json`, `v1-alternative-exon-splice-disposition.json` and `H11-shifted-fusion-acceptor.json`.

## Why more agents may not solve the current constraint

The [Anthropic report](https://www.anthropic.com/news/claude-discovers-novel-enzyme-system) describes searching a large, diverse collection of reverse transcriptases, followed by laboratory experiments. Here, the usable confirmed whole-transcriptome material located for this pilot consists of two deposited EMC models, with two sequencing runs from one of them. Broader searches returned controlled-access data, targeted expression assays, other chondrosarcoma types, and incompletely identified samples. More model calls do not create independent specimens, long-read phasing or laboratory validation.

The broader search returned 518 experiment summaries. Selected relevant hits received additional source review, including 61 experiment records from six further studies. This is not an exhaustive census or proof that no other public EMC data exist. See `expanded-dataset-disposition.json` and `remaining-candidate-study-disposition.json`.

## Useful work retained, and its limits

The packet preserves record-aware streaming, known-answer checks, accession provenance, exact read/quality evidence, normal-reference comparisons, and negative candidate dispositions. It also demonstrates two defects in a legacy scanner: overlap double-counting and matching synthetic quality-line text. These defects do not supply a correction factor for historical counts and are not by themselves a publishable new method.

The human RefSeq RNA comparison examined a verified source containing 186,185 transcripts; bait filtering retained 51 references while preserving possible exact full-read matches within that FASTA. The remote 16-query RNA BLAST also completed: all query identities/lengths and 556 HSP query segments were checked, including three exact MEOX2 matches already explained by the local comparison. These methods are not whole-genome alignment, exhaustive variant calling, or evidence that all unresolved reads are artifacts. The final run's 135 unresolved bait-screen records received a further bounded local-alignment pass. Partial matches remain partial explanations.

## Decision limits and what would change it

The decision does not require resolving every single-fragment anomaly. None currently combines nontrivial novelty, convincing independent support and a useful biological conclusion. Normal-reference novelty alone would not turn an unreplicated observation into a paper.

One genomic BLAST request for the original H05 mates was still waiting at its last observation; its missing result is not used as evidence against the candidate. Whether it finds an alternative genomic match or leaves the repeat unexplained cannot supply the missing independent support. Its latest actual status is recorded in `blast-status-latest.json`.

Reopening would be justified by a new confirmed EMC cohort with accessible sequence data, independent-library or long-read support for a specific candidate, or a laboratory collaborator able to test a compelling hypothesis. Repeating the same search with more agents, without such a change, is not justified by this pilot.

All raw collectors and the final analysis processes have exited. The three requested worker starts produced no results and still appeared as `pending_init` in the last platform listing; no successful parallel-agent work or performance comparison is claimed. This was coordinator-executed research. No manuscript, clinical registry, shared repository queue, correspondence or publication has been changed by this packet. The final source and completion checks are recorded in `completion-audit.json` and the packet's closing manifest.
