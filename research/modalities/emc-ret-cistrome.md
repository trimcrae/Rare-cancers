---
id: DOC-EMC-RET-CISTROME
title: Is RET a direct transcriptional target of NR4A3? — measured occupancy, not a motif string
level: L3
kind: memo
status: live
canonical_for: ["the 2026-08-07 NR4A ChIP-seq retrieval, the RET-locus intersection and its paralogue read"]
purpose: >
  Take the step emc-ret-lane.md §2d ranked above everything else in the RET lane and could not
  reach: pull every public NR4A1/NR4A2/NR4A3 ChIP-seq peak set reachable at $0, characterise each
  before using it, and intersect it with the RET locus on a stated genome build — with the
  paralogue-overlap read that comes free and that this repository has only ever argued from domain
  sequence identity.
scope: >
  L3. Grades ONE question inside ONE lane. It does not re-grade any route, it does not move
  emc-ret-lane.md §3 (the activation bar), and every roadmap or graph change it implies is emitted
  as a routed map-edits file rather than applied.
audience: [maintainers, autonomous research agents, external reviewers]
date: 2026-08-07
last_verified: 2026-08-07
---

# Is *RET* a direct transcriptional target of NR4A3? — measured occupancy, not a motif string

> ⛔ **NOTHING HERE ASSERTS EFFICACY, SAFETY, SELECTIVITY, A THERAPEUTIC WINDOW OR CLINICAL
> READINESS FOR EMC, AND NOTHING HERE RECOMMENDS GIVING ANY AGENT TO ANY PATIENT.** No EMC patient
> has received a selective RET inhibitor. Every biological statement carries a PMID, a PMCID or a
> named database accession.

## 0 · What this is, and what it is not

[`emc-ret-lane.md`](./emc-ret-lane.md) §2d established two things and could act on neither:

1. **⛔ No `EWSR1::NR4A3` cistrome exists.** Against 792 Europe PMC records (461 full texts), the
   only chromatin experiments on *any* NR4A3 fusion are single-locus: the SEMA3C ChAP-qPCR
   (**PMID 31020999** / PMC6766969) and the ENO3 EMSA/ChIP (**PMID 26310886**, on `TFG::NR4A3`).
   Nothing genome-wide has ever been done on the object this whole programme is about.
2. **⭐ Wild-type NR4A3 ChIP-seq does exist**, and one dataset is human and carries **all three
   paralogues in the same cells** (**PMID 36482877** / PMC10108054).

So the question this memo asks is the strongest form the target-gene question can take at $0, and
it is a **strictly weaker question than the one the lane wants**:

| the lane wants | this instrument delivers |
|---|---|
| does **EWSR1::NR4A3** occupy *RET* **in an EMC tumour**? | does **wild-type NR4A1/2/3** occupy *RET* **in the cell types anyone has ChIP'd**? |

**A peak is a PRIOR, and a strong one** — measured occupancy, in real chromatin, by the protein
whose DNA-binding domain the fusion retains intact. **It is never a demonstration.** PMID 31020999
*measured* that the EWSR1 and TAF15 chimeras differ from each other in DNA binding at a validated
NBRE target, so a wild-type reading cannot be transferred to the chimera by assumption.

**And NO peak is WEAK evidence**, because the locus may simply be closed in the cells assayed.
⛔ An absent reading is not a reading of absence (CLAUDE.md §4).

### Why this is not the motif scan, and why both exist

[`emc_ret_target_scan.py`](./emc_ret_target_scan.py) asks whether *RET*'s regulatory window carries
an **NBRE octamer** more often than a composition-matched null. That is a *sequence* question.
`AAAGGTCA` is an 8-mer, so it occurs about once per 33 kb of random sequence and **a motif scan
cannot tell a bound element from an unbound one**. A ChIP peak already has. The two modules are
**siblings that answer different questions and are allowed to disagree**; neither supersedes the
other, and this one does not touch `emc-ret-target-scan.json`.

---

## 1 · ⛔ The genome build, which is a result and not a footnote

**This lane has already been burned twice by a coordinate convention that produced a
plausible-looking artifact** — the NR4A3 exon-numbering hazard and the 2-nt acceptor 5′UTR, both in
[`junction-mrna-frame-audit.json`](./junction-mrna-frame-audit.json). The genome analogue is worse:
***RET* is on chr10, where GRCh37 and GRCh38 differ by a large constant.** A build mix-up does not
raise. It silently reports another locus, and the artifact reads perfectly.

Four guards, **asserted rather than described**, all in
[`emc_ret_cistrome.py`](./emc_ret_cistrome.py) and exercised by `--selftest` **before one byte is
fetched**:

1. **Nothing is lifted over.** Each build's *RET* span is fetched from that build's own service
   (`rest.ensembl.org` for GRCh38, `grch37.rest.ensembl.org` for GRCh37).
2. **Two independent sources per build** — Ensembl and NCBI Gene — and the artifact records the
   **disagreement** rather than asserting agreement. NCBI's chromosome accession *version* is
   self-describing about the assembly (`NC_000010.11` is GRCh38's chr10, `.10` is GRCh37's), so the
   build is read off the data rather than assumed.
3. **A cross-build intersection RAISES.** `intersect_locus` refuses rather than correcting; a
   `ValueError` is a stack trace, and a silently-shifted window is a publication.
4. **BED is 0-based half-open; Ensembl and NCBI Gene are 1-based inclusive.** One converter,
   `ens_to_bed`, tested including the 1-bp case, the round trip and the adjacency case
   (`[0,10)` and `[10,20)` **do not** overlap).

And the same discipline applies to a peak file with no build inside it: a GEO supplementary
`.narrowPeak` carries no assembly, so the build is **read from the series' own
`!Sample_data_processing` record**, and a series that does not name one unambiguously has its peak
files **retrieved, recorded and not intersected**.

<!-- RESULTS-BUILD -->

---

## 2 · What was retrieved, and how each dataset was characterised before use

**Seven routes, all attempted, every one recorded with its HTTP status.** CLAUDE.md §6 requires a
series to be characterised before anything is built on it, and CLAUDE.md §4 requires
*"we did not look"* and *"we looked and it is not there"* to stay different facts — so a 404 is a
**reading** in `part_1_datasets._retrieval_attempts`, never a silent skip.

| route | what it is | why it is here |
|---|---|---|
| **ChIP-Atlas** `experimentList.tab` → per-SRX `bed05` | every public ChIP-seq, uniformly reprocessed with MACS2 at a fixed threshold (Oki et al., *EMBO Reports* 2018, **PMID 30413482**) | uniform reprocessing means the peak sets are comparable ACROSS experiments, which is what a paralogue overlap needs |
| ChIP-Atlas per-antigen **target-gene tables** | strongest peak within *N* kb of each gene's TSS, per experiment | a purpose-built answer to this exact question — kept as **corroboration**, never as the headline, because it uses somebody else's TSS definition and distance cut |
| **GEO** DataSets, six overlapping queries | series-level records + supplementary peak files | a query returning nothing is indistinguishable from a dataset not existing, so more than one is run |
| **NCBI ELink** (PubMed → gds / sra / bioproject) | the paper→dataset link table | ⭐ the canonical route for *"the accession is not in the article text"*, and the one [`emc-ret-lane.md`](./emc-ret-lane.md) §2d did not take — it searched PMC10108054's **rendering** and found none, which is a reading about the rendering |
| **Europe PMC** `resultType=core` + `supplementaryFiles` | curated database cross-references and the publisher supplement bundle | neither is in the rendered body text; the cDC2 study's supplements are Wiley-hosted |
| **EBI BioStudies / ArrayExpress** | the archive a European deposition would use | *"not in GEO"* and *"not deposited"* are different facts |
| **ReMap 2022** and **ENCODE** | two more uniformly-reprocessed human TF catalogues | breadth, and each is one request |
| **NGDC GSA** `CRA032324` / `CRA032321` | the Schwann-cell NR4A3 ChIP-seq named verbatim in PMC13099357 | ⚠ GSA archives **raw reads**. Alignment + peak calling from FASTQ is not a $0 CPU-runner operation, and that is recorded as an **instrument limit**, never as an absence of data |

<!-- RESULTS-DATASETS -->

---

## 3 · The intersection at *RET*

<!-- RESULTS-INTERSECTION -->

---

## 4 · The paralogue overlap

<!-- RESULTS-PARALOGUE -->

---

## 5 · The expression cross-read

**Three instrument classes, deliberately, because concordance across classes is an argument and
one instrument is a number.** All three run at $0 on the same two EMC tumour series
(`emc_expression_panels.py`, `read_7_RET`):

| class | what it asks | what it cannot answer |
|---|---|---|
| **occupancy** (§3, this memo) | is an NR4A protein *sitting* at the RET locus? | whether anything happens as a result |
| **membership** — ChEA / ENCODE+ChEA / TRRUST NR4A3 target sets | has anyone's experiment already called RET an NR4A3 target? | it is a citation, not a measurement made here |
| **perturbation** — TF_Perturbations `NR4A3 KD_DOWN` / `OE_UP`, with `KD_UP` as the directional **control** | does RET *move* when NR4A3 is perturbed? | direction, not directness — an indirect effect moves genes too |
| **abundance** — RET, the GDNF-family ligands, the GFRα co-receptors | is RET high in EMC, and is there a ligand at all? | ⛔ **activation**, and cellular origin |

⛔ **The abundance arm is the one most likely to be over-read, so it is fenced here.**
[`emc-ret-lane.md` §3](./emc-ret-lane.md) is the one home of the finding that RET in EMC has never
been given the measurement that decided MET in clear cell sarcoma — a **blinded 32-case tissue
microarray** in which MET protein was present in **82 %** and phospho-MET Tyr1234–35 in **4 %**
(**PMID 34885165** / PMC8657105). Abundance and activation came apart by a factor of twenty in the
disease this lane uses as its comparator. **No transcript read can close that gap, and this one
does not move that finding.** It also cannot separate tumour RET from stromal or entrapped
peripheral-nerve RET: EMC is hypocellular and matrix-rich (PMC6766969), RET is a nerve-lineage
receptor, and these are **bulk** arrays.

⭐ **The perturbation arm is the interesting one**, because it is the cheap shadow of the
experiment the ENO3 precedent actually needed: **PMID 26310886** established ENO3 with EMSA *and*
ChIP *and* **luciferase** — occupancy plus a functional readout. Occupancy alone has never been
enough in this lane's own precedent.

<!-- RESULTS-EXPRESSION -->

---

## 6 · The verdict, at its true strength

<!-- RESULTS-VERDICT -->

---

## 7 · Files

| file | what it is |
|---|---|
| [`emc_ret_cistrome.py`](./emc_ret_cistrome.py) | the instrument: catalogue discovery, characterisation, build reconciliation, interval algebra, intersection, paralogue overlap. `--fetch` / `--check` / `--selftest` |
| [`emc-ret-cistrome.json`](./emc-ret-cistrome.json) | the derived artifact |
| [`emc-ret-cistrome-inputs.json`](./emc-ret-cistrome-inputs.json) | the inputs cache — every peak set, every locus, and every network attempt with its HTTP status |
| [`tests/test_emc_ret_cistrome.py`](./tests/test_emc_ret_cistrome.py) | the guards: interval algebra, the cross-build refusal, no-reading-⇒-no-verdict, and that a null without a recovered positive control renders as UNINTERPRETABLE rather than as a negative |
| [`emc_expression_panels.py`](./emc_expression_panels.py) | `read_7_RET` — the abundance half, in the same two EMC tumour series |
| [`emc-ret-cistrome-map-edits.json`](./emc-ret-cistrome-map-edits.json) | the routed roadmap/graph proposal. **Not applied** |
