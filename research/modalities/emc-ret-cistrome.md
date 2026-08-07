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

<!-- RESULTS-DATASETS -->

---

## 3 · The intersection at *RET*

<!-- RESULTS-INTERSECTION -->

---

## 4 · The paralogue overlap

<!-- RESULTS-PARALOGUE -->

---

## 5 · The expression cross-read

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
