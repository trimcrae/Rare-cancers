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

### What the build check returned

| build | species | expected | returned | *RET* span (1-based) |
|---|---|---|---|---|
| **hg38** | human | GRCh38 | **GRCh38** | `chr10:43,077,026–43,130,351`, strand +, `ENSG00000165731` |
| **hg19** | human | GRCh37 | **GRCh37** | `chr10:43,572,475–43,625,799`, strand + |
| mm39 | mouse | GRCm39 | **GRCm39** | `chr6:118,128,706–118,174,769`, strand − |
| mm10 | mouse | GRCm38 | ⛔ **GRCm39** | **DISCARDED — see below** |

**`chr10` offset, hg19 − hg38, at *RET*'s start: 495,449 bp.** That is the number the whole guard
exists for: a build mix-up moves *RET* half a megabase and raises nothing.

**Two independent sources, same build, same frame:** NCBI Gene's `NC_000010.11` — a RefSeq
chromosome accession *version*, which is self-describing about the assembly — gives
`43,077,068–43,130,350` against Ensembl's `43,077,025–43,130,351` in BED coordinates. **Start
delta +43 bp, end delta −1 bp**: the two annotate transcript ends slightly differently, which is
reported rather than asserted away. A build mix-up would show a delta of order 10⁵.

⭐ **The third check is the decisive one, and it ties this memo to the other half of the lane.**
GPL6244 is the array [`emc_expression_panels.py`](./emc_expression_panels.py) reads for GSE24369.
Its platform table carries each probe's genomic range **and `RANGE_GB`** — the assembly accession
those ranges are stated against. For the loci in this panel `RANGE_GB` reads `NC_000010.10`,
`NC_000007.13`, `NC_000017.10` … — the **GRCh37** RefSeq accessions. And *RET*'s probe range falls
inside the *RET* span fetched here on **hg19 and on hg19 only**: `RET_build_is_unambiguous: true`,
`RET_consistent_with: ["hg19"]`. Containment can hold for at most one of two spans 495 kb apart,
so this is a **decisive** check rather than a corroborating one, and it means the occupancy half
and the abundance half of this lane are demonstrably in one coordinate frame instead of assumed to
be.

⚠ *Measured first, rather than claimed: the instruction that produced this module said to verify
the convention against a **committed** artifact. This repository's committed artifacts record
GPL6244's `seqname` / `RANGE_GB` / `RANGE_START` / `RANGE_STOP` **header** —
`emc-atr-vulnerability-inputs.json` and `emc-expression-panels-inputs.json` — but **not their
values**. So there is no committed genomic coordinate here to reconcile against, and saying
otherwise would have been false. The live platform table is fetched instead, and it is a stronger
check.*

### ⛔ And the guard caught the module doing the exact thing it exists to prevent

`rest.ensembl.org` serves only the **current** mouse assembly, so the `mm10` lookup came back
**GRCm39** while the build asked for GRCm38. `assembly_matches_expected` correctly went `false` —
**and the code set a note and returned the coordinates anyway.** Seven ChIP-Atlas `mm10` peak sets
were then intersected against GRCm39 loci, and **two of them reported `Ret` promoter-window
peaks**. Those two positives were a cross-build artefact, produced by the module whose entire
premise is that cross-build intersection must be impossible.

**A WARNING IS NOT A GUARD.** `intersect_locus` could not catch it, because by that point both
sides carry the same build *string*; the only place it is catchable is at the lookup, where the
returned assembly can be compared with the one requested. The coordinates are now **discarded**,
the two artefact positives are gone from the reading, and every mouse peak set reports
`no_loci_on_this_build` — an absent reading, which is the honest state. The practical consequence
is that **ChIP-Atlas's mouse peak sets are not readable through this route at all**; fixing that
needs a GRCm38 coordinate source, not a code change. Held by
`test_a_build_whose_service_returned_the_wrong_assembly_yields_NO_coordinates`.

*(Three further defects were found in the first run's own `attempts` record and fixed before the
run that produced these numbers: a `429` was being treated as "not found", so one throttled NCBI
`esummary` silently disabled the second source and the build check printed `False` when it had
merely been throttled; a 213-symbol POST that hit a transient upstream `500` took the primary
locus lookup down with the background panel, so the lookup is now chunked with the loci first; and
an arbitrary `[:40]` cut 92 ChIP-Atlas rows to 40 with no field recording it.)*

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

### What came back

**ChIP-Atlas: 845,824 experiments searched, 92 rows matching NR4A1 / NR4A2 / NR4A3.** Each SRX is
listed once per genome build, so those 92 rows are ~46 distinct experiments:

| antigen | build | n | cell types |
|---|---|---|---|
| NR4A1 | hg19 / hg38 | 26 each | Kasumi-1, MOLM-14, K-562, LoVo, MCF 10A, breast cancer cells, dendritic cells |
| NR4A2 | hg19 / hg38 | 7 each | dendritic cells, LoVo |
| NR4A3 | hg19 / hg38 | **6 each** | **dendritic cells only** |
| Nr4a1 (mouse) | mm9 / mm10 | 7 each | — |

⛔ **The single most consequential line in this table: every NR4A3 ChIP-seq experiment in existence
that ChIP-Atlas has reprocessed is in one cell type, from one study.** Peak caller MACS2 at
ChIP-Atlas's threshold `05` (q < 1e-5); QC (reads, % mapped, % duplicates, peak count) is recorded
per experiment in the artifact, and it is the peak-count column that turns out to decide
everything (§3c).

⭐ **The cDC2 accession the prior pass could not find is `GSE186199`**, and it was found twice
independently: by a regex scan of PMC10108054's `fullTextXML` (the prior pass searched the PMC
*rendering*), and by a GEO query returning GSE186197/98/99 — *"Nuclear receptor subfamily 4A
signaling as a key disease pathway of CD1c+ dendritic cell…"*. ChIP-Atlas had already reprocessed
it, which is what makes §4b's paralogue overlap computable at all. **GEO returned 37 series in
total**; the ones carrying NR4A ChIP data are listed in the artifact with their organism, sample
count and verbatim title.

⚠ **Europe PMC's curated cross-reference list returned nothing for any of the three papers**, so
the route that was expected to find the accession was not the one that did. That is recorded as a
reading about the cross-reference list, not about deposition.

✅ **PMC13099357's accessions `CRA032321` / `CRA032324` were recovered as stated** — but GSA
archives **raw reads**, so they remain unusable at $0. Instrument limit, recorded as one.

<!-- RESULTS-DATASETS -->

---

## 3 · The intersection at *RET*

> **Every number in §3 and §4 is DERIVED, not typed.** Regenerate with
> `python3 research/modalities/emc_ret_cistrome.py --report`; its one home is
> [`emc-ret-cistrome.json`](./emc-ret-cistrome.json). If this memo and that artifact disagree, the
> artifact is right and this memo is stale.

### 3a · ⭐ The finding

**Three NR4A1 peaks sit in *RET*'s first-intron regulatory region, and they reproduce across two
ChIP-seq replicates, two genome builds and two independent reprocessing pipelines.**

Offsets from *RET*'s TSS. `SRX1653203/4` are two Kasumi-1 experiments reprocessed by **ChIP-Atlas**
(MACS2, q < 1e-5); `REMAP2022_NR4A1` is **ReMap 2022**'s merged NR4A1 catalogue — a *different*
uniform-reprocessing pipeline, so it is not the same numbers arriving twice:

| peak | 1653203 hg19 | 1653204 hg19 | 1653203 hg38 | 1653204 hg38 | ReMap 2022 hg38 |
|---|---|---|---|---|---|
| 1 | +5,892…+6,005 | +5,866…+6,007 | *(not called)* | +5,864…+6,008 | +5,841…+6,036 |
| **2** | **+6,768…+7,052** | **+6,792…+7,108** | **+6,768…+7,054** | **+6,792…+7,116** | **+6,778…+7,116** |
| 3 | +14,900…+15,105 | +14,852…+15,104 | +14,891…+15,110 | +14,853…+15,108 | +14,850…+15,120 |
| MACS2 score, peak 2 | 448 | 540 | 451 | 556 | — |

⭐ **The five columns agree to within ~50 bp.** Two of them are on **GRCh37** and three on
**GRCh38** — spans 495,449 bp apart — so a coordinate-convention error could not produce this
table. That is the build guard of §1 validated by the data rather than asserted.

**Against a background panel this lane did not choose** — a fixed-seed 200-gene sample of the
1,299 symbols the repository had already committed for the ATR concept universe, so it cannot have
been picked to flatter or damage *RET*:

| peak set | peaks in set | bg genes with ≥1 promoter peak | bg genes with ≥ *RET*'s count | empirical p |
|---|---|---|---|---|
| SRX1653203 hg19 | 22,674 | 58 / 200 | **0 / 200** | **0.005** |
| SRX1653204 hg38 | 26,660 | 90 / 198 | 2 / 198 | **0.0151** |
| SRX1653204 hg19 | 26,549 | 93 / 200 | 3 / 200 | **0.0199** |
| SRX1653203 hg38 | 22,717 | 62 / 198 | 9 / 198 | 0.0503 |
| **ReMap 2022 (merged)** | **83,773** | **164 / 198** | **88 / 198** | **0.4472** |

`p = (ge+1)/(n+1)`, never `ge/n`, so it can never print a zero the panel size does not support.

⛔ **THE LAST ROW IS THE CEILING ON THE FIRST, AND IT MUST BE QUOTED WITH IT.** In ReMap's merged
catalogue the same three peaks are present — but so is a peak at 164 of 198 background genes, and
88 of them carry three or more. **In a deeply merged catalogue *RET* is occupied but entirely
unremarkable.** The enrichment (p = 0.005–0.02) is a property of the *single-experiment* peak sets,
where a peak means something because most genes do not have one. Anyone quoting `p = 0.005` without
`p = 0.4472` is quoting a selection.

⚠ **Peak 1 is not called in one of the five columns** (`SRX1653203` realigned to GRCh38),
which is why that column shows two promoter-window peaks and `p = 0.0503`. Whether that is
a threshold effect or a mapping difference is not established here.

⚠ **Peak 3 sits at the window edge.** The window is −10 kb / +15 kb and peak 3 spans ~+14.85–15.12
kb, so it is partly defined by the scope choice. Peaks 1 and 2 are not.

⚠ **These are NOT the HOXB5 element.** The window was widened, before any data, to contain
MCS+9.7 — *RET*'s one experimentally validated distal element, in the first intron, whose deletion
abolishes HOXB5 trans-activation of the *RET* promoter (**PMID 24794774**). The three peaks
*bracket* +9.7 kb rather than sitting on it. What is true is narrower and still worth saying: the
occupancy is in the same first-intron region where *RET*'s only validated distal control element
lives, not at the promoter.

### 3b · ⛔ Six things this is not, each of which would be an over-read

1. **It is NR4A1, not NR4A3 — and NR4A3 occupancy at *RET* is NOT MEASURED.** ChIP-Atlas holds
   exactly **six** NR4A3 ChIP-seq experiments, all in dendritic cells and all from one study, with
   **53–154 peaks each**, and **none of them recovers SEMA3C or ENO3**. A peak set that cannot
   detect a locus a published chromatin experiment already placed NR4A3 at cannot exclude *RET*.
   Those six nulls are recorded as **uninterpretable**, not as negatives.
2. **It is wild-type NR4A1, not the fusion.** PMID 31020999 *measured* that the EWSR1 and TAF15
   chimeras differ from each other in DNA binding at a validated NBRE target, so nothing transfers
   to `EWSR1::NR4A3` by assumption.
3. **Kasumi-1 is an AML line, not EMC.** The chromatin state at *RET* in EMC is unmeasured.
4. **⛔ THE ALTERNATIVE HYPOTHESIS IS ALSO OCCUPIED — AND IN THE DEEPEST CATALOGUE IT IS OCCUPIED
   MORE. THIS IS THE MOST IMPORTANT CAVEAT IN THE MEMO.** *KDR* carries **2** promoter-window
   peaks and **4** in the gene-body window in *every* Kasumi-1 peak set and in ReMap; *VEGFA*
   carries 1–2 in Kasumi-1 and **10 promoter-window peaks and 12 in the gene body in ReMap 2022,
   against *RET*'s 3.** §3.1's memo frames the conventional attribution of EMC's TKI activity to
   VEGFR — the originating authors' own reading (**PMID 23058004**) — as the story RET displaces.
   **Occupancy does not displace it. It occupies both, and it occupies VEGFA harder.** Anyone
   quoting the *RET* peaks without this line is quoting half a result.
5. **A 150–500× depth confound sits underneath the paralogue pattern** — see §4.
6. **Occupancy is not transactivation.** The ENO3 precedent needed **luciferase** on top of ChIP
   (**PMID 26310886**). Nothing here measures output.

### 3c · Depth, not paralogue, is what separates the peak sets

Sorted by depth, the pattern is unambiguous: **only peak sets above ~20,000 peaks recover a known
positive control at all**, and those are the only ones with a *RET* peak.

| experiment | antigen | cell type | total peaks | SEMA3C | ENO3 | *RET* promoter window |
|---|---|---|---|---|---|---|
| REMAP2022_NR4A1 | NR4A1 | merged catalogue | 83,773 | 1 | 6 | **3** |
| SRX1653204 | NR4A1 | Kasumi-1 | 26,549 / 26,660 | 1 | 2 | **3** |
| SRX1653203 | NR4A1 | Kasumi-1 | 22,674 / 22,717 | 1 | 2 | **3 / 2** |
| SRX2423525 | NR4A1 | K-562 | 6,823 / 7,958 | 0 | 1 | 0 |
| SRX5242458 | NR4A1 | MOLM-14 | 15,415 | 0 | 0 | 0 |
| … 35 further experiments | NR4A1/2/3 | dendritic cells, K-562, LoVo, MCF 10A, breast | ≤1,105 | 0 | 0 | 0 |

**So the honest count is: 3 of 40 distinct experiments carry a *RET* promoter-window peak, and only
4 of 40 recover a positive control at all.** The other 36 nulls say the experiment was too shallow
to detect a locus NR4A3 is already published as binding — they do not say *RET* is unbound.

⚠ **A peak set is not an experiment.** ChIP-Atlas reprocesses each SRX against every genome build
it supports, so 40 experiments appear as 79 peak sets. The experiment count is the one to quote;
counting peak sets would read as independent replication when it is the same reads aligned twice.

<!-- RESULTS-INTERSECTION -->

---

## 4 · The paralogue overlap

### 4a · At *RET* — the answer is NOT MEASURED, and the pattern that looks like an answer is a confound

| paralogue | peak sets scored | distinct experiments | peak-depth range | any promoter-window peak at *RET* |
|---|---|---|---|---|
| **NR4A1** | 53 | **27** | 71 – 83,773 | **yes** |
| **NR4A2** | 14 | 7 | 1 – 1,105 | no |
| **NR4A3** | 12 | **6** | **53 – 154** | no |

⛔ **This is not "NR4A1 binds *RET* and NR4A3 does not."** The positive sets have **22,674–83,773**
peaks; the deepest NR4A3 experiment anywhere has **154**. That is a **150–500× depth difference**,
on top of a cell-type difference (an AML line and a merged multi-tissue catalogue, versus primary
dendritic cells), and **no NR4A3 peak set recovers a positive control**. Two variables move with
the outcome and neither is the paralogue. **The paralogue question at *RET* is unanswered, and the
honest state is NOT MEASURED.**

⚠ *Every one of the six NR4A3 experiments comes from **one study in one cell type** (GSE186199,
cDC2s). ChIP-Atlas lists each experiment once per genome build, which is why 12 peak sets carry 6
experiments — a count that would read as replication if the distinction were not made.*

⚠ *These counts are of peak sets that were actually SCORED. A peak set that downloaded but sits on
a build whose loci were discarded (§1) contributes no reading and is excluded — counting those
inflated NR4A1 from 27 experiments to 34 in the first pass, by including the seven mm10 sets whose
coordinates had just been thrown away.*

### 4b · ⭐ But the paralogue overlap itself IS measured — and it is a repository first

The cDC2 dataset (**GSE186199**, PMID 36482877 / PMC10108054) carries **NR4A1, NR4A2 and NR4A3 in
the same primary human cells**, so the three peak sets are directly comparable to each other even
though each is shallow. Genome-wide, fraction of A's peaks overlapped by at least one of B's:

| pair | cell type | peaks A / B | fraction of A overlapped by B |
|---|---|---|---|
| NR4A1 vs NR4A2 | dendritic cells | 297 / 115 | 0.397 |
| NR4A1 vs NR4A3 | dendritic cells | 297 / 102 | 0.347 |
| **NR4A2 vs NR4A3** | dendritic cells | 115 / 102 | **0.765** |

⭐ **This is the first DIRECT empirical measurement of NR4A paralogue DNA-binding overlap anywhere
in this repository.** Every paralogue-selectivity argument the programme has made so far rests on
**domain sequence identity**; no identity calculation can produce this number. The shape is
specific and it is not what a pure-identity argument predicts: **NR4A2 and NR4A3 overlap far more
with each other (77 %) than either does with NR4A1 (35–40 %)**, in one cell type under matched
conditions.

⚠ **And it is a weak measurement, at full strength.** The peak sets are 102–297 peaks deep and
recover no positive control, so the overlap is computed over small sets that may be
noise-dominated; a deeper experiment could move all three numbers. It is one cell type, one
laboratory, wild-type receptors. It says nothing about ligand-binding-domain selectivity, which is
where this repository's degrader problem actually lives — DNA-binding overlap and pocket
selectivity are different questions.

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

⭐ **The perturbation arm was designed to be the interesting one**, because it is the cheap shadow
of the experiment the ENO3 precedent actually needed: **PMID 26310886** established ENO3 with EMSA
*and* ChIP *and* **luciferase** — occupancy plus a functional readout. Occupancy alone has never
been enough in this lane's own precedent. ⛔ **It did not resolve — see §5e**, and the reason is
itself a finding.

### 5a · The instrument reproduced its known answers first

Nothing below is quotable unless this block is. `emc_expression_panels.py` `read_7_RET`, on
GSE24369/GPL6244 (**6 EMC vs 29 comparator sarcomas**, single-channel) and GSE4303/GPL3290
(**10 EMC vs 6 comparators**, two-colour, so **relative** — only the between-group contrast is
interpretable):

| control | expected | GPL6244 | GPL3290 |
|---|---|---|---|
| **NR4A3** | UP — the disease-defining event | **+0.74 SD, t = 4.66**, 76th pct | contrast underpowered (n = 9 vs 2) |
| **ENO3** | UP — published direct target of an NR4A3 fusion (**PMID 26310886**) | **+0.81 SD, t = 3.61** | **+3.81 SD, t = 13.22**, 98th pct |
| **MKI67** | ~flat — EMC is slow-cycling | +0.13 SD, \|t\| < 2 ✓ | +1.24 SD, \|t\| 2–3 |

### 5b · ⭐ *RET* is up in EMC in BOTH series — the first time it has been read in the second one

| | GPL6244 (6 EMC vs 29) | GPL3290 (10 EMC vs 6) |
|---|---|---|
| ***RET*** | **+0.46 SD, t = 2.613**, 58th pct | **+1.11 SD, t = 4.077**, 86th pct |

**PMID 28423517** measured RET mRNA in **n = 6** by transcriptome sequencing. This adds a
**second, independent, differently-platformed cohort** (n = 10 EMC on a two-colour cDNA array) and
it agrees. The abundance half of §3.1's claim is corroborated rather than merely repeated.

### 5c · ⛔⛔ AND THE LIGAND MODULE IS THE OPPOSITE — THIS IS THE CLEAR-CELL-SARCOMA SHAPE

**PMID 34885165** closed crizotinib in clear cell sarcoma on **two** grounds, not one: MET protein
in 82 % but phospho-MET in **4 %** — *and* the **HGF ligand in only 16 %**. A receptor with no
ligand is the same failure mode as a receptor with no phosphorylation.

| gene | role | GPL6244 | GPL3290 |
|---|---|---|---|
| *GDNF* | RET ligand | flat | **−1.60 SD, \|t\| 2–3**, 25th pct |
| *NRTN* | RET ligand | flat | flat |
| *ARTN* | RET ligand | flat | flat |
| *PSPN* | RET ligand | −0.07 SD, \|t\| 2–3 | ⛔ not readable |
| ***GFRA1*** | **obligate GDNF co-receptor** | flat, 69th pct | **−1.62 SD, t = −3.63**, 23rd pct |
| ***GFRA2*** | neurturin co-receptor | **−0.96 SD, t = −4.11** | **−1.42 SD, t = −3.26** |
| *GFRA3* | co-receptor | −0.10 SD, \|t\| 2–3, 17th pct | −0.88 SD, \|t\| < 2 |
| *GFRA4* | co-receptor | flat | ⛔ not readable |

**Not one ligand or co-receptor is up in either series** (*GDNF*'s +0.03 SD on GPL6244 is flat by
the module's own \|t\| < 2 rule), **and five of the eight are down at \|t\| ≥ 2 somewhere, two of
them at \|t\| ≥ 3.**
So the reading is: **receptor up, ligand-and-co-receptor arm down or flat, in both cohorts** — the
same *shape* that decided the comparator disease, arriving from expression rather than from a
stain, and **nobody has published it for EMC**.

⛔ **What it is not, at full strength.** (a) Transcript, not protein — the CCS result was IHC on a
blinded array and this is not that measurement. (b) **Bulk tissue**: GDNF-family signalling can be
paracrine and stromal, so a low tumour-compartment transcript does not establish that no ligand
reaches the receptor. (c) RET can be activated ligand-independently, so a ligand-poor tumour is not
automatically a RET-inactive one. (d) n = 6 and n = 10, two decade-old array platforms, uncorrected
for multiple testing, one of them two-colour and therefore relative. **This does not close the RET
lane and it is not the missing measurement** — [`emc-ret-lane.md`](./emc-ret-lane.md) §3 remains
the one home of that gap. It does say the lane now has a *second* reason to want the phospho-RET /
ligand co-stain, and it names the co-stain: **GDNF and GFRA1**.

### 5d · The alternative hypothesis, in the same tumours

| gene | GPL6244 | GPL3290 |
|---|---|---|
| *VEGFA* | +0.39 SD, \|t\| < 2, 93rd pct | +0.93 SD, \|t\| 2–3 |
| *KDR* | **−0.87 SD, \|t\| 2–3** | −0.11 SD, flat |
| *PDGFRB* | **−0.75 SD, t = −4.19** | −0.59 SD, flat |
| *KIT* | **+1.35 SD, t = 3.03**, 88th pct | +0.40 SD, flat |

⚠ **Mixed, and it does not resolve the RET-versus-VEGFR question either way.** *VEGFA* is high in
both; *KDR* — the receptor an anti-angiogenic mechanism would act through — is **not** up. Read
with §3b caveat 4, where the deepest peak set occupies *VEGFA* harder than *RET*: **the two
attributions are not separated by anything measured here.**

### 5e · ⛔ The membership arm is an ABSENT READING, and that is itself informative

Eight NR4A target-set slots were requested across four instrument classes. **Seven did not
resolve**: Enrichr's ChEA, ENCODE+ChEA, TRRUST and TF-perturbation libraries contain **no NR4A3
term and no NR4A1 term at all**. The one that resolved is `nr4a2_targets_chea` — *"NR4A2 19515692
ChIP-ChIP MN9D Mouse"*, 128 genes, a **mouse** ChIP-chip — and *RET* is not in it, nor are *ENO3*,
*SEMA3C*, *VEGFA* or *KDR*.

**`member: null`, never `member: false`.** A set that was not retrieved says nothing about
membership, and the artifact records it that way. What the absence *does* corroborate is
[`emc-ret-lane.md`](./emc-ret-lane.md) §2d from a completely different direction: **there is no
curated NR4A3 target-gene set in any standard library**, because nothing genome-scale has been
published on NR4A3 to build one from. ⛔ **So the perturbation arm — "does *RET* move when NR4A3 is
perturbed?" — was not answerable, and that question remains open.**

<!-- RESULTS-EXPRESSION -->

---

## 6 · The verdict, at its true strength

### The one-paragraph answer

**Is *RET* a direct transcriptional target of the EWSR1::NR4A3 fusion? Still unknown — and for the
first time the question has measurements attached to it instead of an argument.** Three things were
measured. **(1)** The *RET* locus **is** a bindable NR4A-family site in human chromatin: three
NR4A1 peaks in *RET*'s first intron, reproducing across two Kasumi-1 replicates, **two genome
builds** and **two independent reprocessing pipelines** (ChIP-Atlas and ReMap 2022), at empirical
p = 0.005–0.02 against a background panel this lane did not choose — in **3 of 40** public
experiments, and in the only ones deep enough to recover a published NR4A3 target locus (§3).
**(2)** *RET* mRNA is **up in EMC in both readable series**, adding an independent n = 10 cohort to
the published n = 6 (§5b). **(3)** ⭐ And the reading nobody has published: **every GDNF-family
ligand is flat or down and the obligate co-receptors *GFRA1* and *GFRA2* are significantly down**,
in both cohorts — *receptor up, ligand arm down*, which is the exact shape that closed crizotinib
in clear cell sarcoma (§5c).

⛔ **Five things stop the occupancy result being more than a prior:** wrong paralogue (NR4A1),
wrong protein (wild type, not the chimera), wrong cell type (an AML line), a 200–800× depth
confound under the paralogue pattern — and **the alternative hypothesis is occupied harder**, with
*VEGFA* carrying 10 promoter-window peaks to *RET*'s 3 in the deepest catalogue. ⛔ **NR4A3
occupancy at *RET* is NOT MEASURED**: every NR4A3 ChIP-seq in existence is six dendritic-cell
experiments of 53–154 peaks, none of which detects a locus NR4A3 is already published as binding.
Absent readings, not negatives, recorded as such.

### The grade

| question | answer |
|---|---|
| **Is *RET*'s locus bindable by an NR4A protein in human chromatin?** | **Yes — measured, and reproduced across two builds and two pipelines.** NR4A1, Kasumi-1 + ReMap 2022, three first-intron peaks agreeing to ~50 bp |
| **Does NR4A3 bind *RET*?** | **NOT MEASURED.** Six NR4A3 experiments exist worldwide in ChIP-Atlas, all from one study in one cell type, 53–154 peaks, none recovering a positive control |
| **Does `EWSR1::NR4A3` bind *RET*?** | **Unanswerable from public data.** No fusion cistrome exists (`emc-ret-lane.md` §2d) |
| **Is *RET* elevated in EMC?** | **Yes, now in two independent cohorts** (§5b) — the published n = 6 plus an n = 10 series nobody had read for *RET* |
| **⭐ Is there a ligand for it?** | **Not in the transcript data, in either cohort.** All four GDNF-family ligands flat or down; *GFRA1* and *GFRA2* significantly down (§5c). ⚠ Transcript, bulk tissue, and RET can signal ligand-independently — this is a reason to stain, not a closure |
| **Does this favour the RET attribution over the VEGFR one for EMC's TKI activity?** | **No — and it slightly disfavours it.** The deepest peak set occupies *VEGFA* harder than *RET*, and in expression *VEGFA* is up while *KDR* is not. Nothing measured here separates the two |
| **Has the §3.1 falsifier fired?** | **No — and one clause moved.** Its first clause (*no NBRE at RET*) now has two instruments pointed at it; its second (*phosphorylation tracks stroma*) remains unmeasurable at $0 anywhere |
| **Does this change the activation bar?** | **No, and nothing here could.** `emc-ret-lane.md` §3 is the one home of that finding. What §5c adds is a *second* reason to want the missing stain, and a specific co-stain to run: **GDNF and GFRA1** |
| **Is it publishable?** | **Yes, and it is now a stronger paper than the negative it was going to be.** *"RET in extraskeletal myxoid chondrosarcoma: a bindable NR4A locus, an elevated receptor, and no ligand."* One sentence for the record: **the *RET* locus is a measured NR4A-family binding site in human chromatin and *RET* mRNA is elevated in both readable EMC cohorts — but no NR4A3 ChIP-seq deep enough to test the paralogue exists, the same peak sets occupy the VEGFR axis harder, and every GDNF-family ligand and co-receptor is flat or down, which is the configuration that closed the analogous MET hypothesis in clear cell sarcoma.** |
| **What it is NOT** | not evidence that `EWSR1::NR4A3` binds *RET*; not evidence of RET activation in EMC; not a selectivity, efficacy, safety, therapeutic-window or clinical-readiness claim; not a recommendation. **No EMC patient has received a selective RET inhibitor** |

### ⭐ What is now unblocked that was not

- **The cDC2 three-paralogue accession is `GSE186199`** — recovered from PMC10108054's
  `fullTextXML` (the prior pass searched the PMC *rendering* and found none) and independently
  returned by a GEO query as one of GSE186197/98/99. ChIP-Atlas had already reprocessed it, which
  is why §4b's overlap is computable at all. `emc-ret-lane.md` §2d's *"needs one prior $0
  retrieval"* is **closed**.
- **The paralogue-overlap number exists** (§4b), and it is the repository's first direct one.
- **The RET expression read exists in a second cohort**, and the ligand module has been read at
  all — for the first time in this disease.

### The ordered next steps, cheapest first

1. **$0 — a depth-matched null for the Kasumi-1 peak sets.** The background panel is not
   depth-matched, and ReMap's `p = 0.4472` shows exactly why that matters. A peak-count-matched
   permutation within the same peak set turns `p = 0.005` into something a referee cannot dismiss
   as a depth artefact. This is the single highest-value remaining $0 step.
2. **$0 — widen the catalogue sweep to CUT&RUN / CUT&Tag, GTRD and Cistrome DB.** The paralogue
   question is limited by NR4A3 peak-set depth, not by anything conceptual: one deeper NR4A3
   experiment settles §4a.
3. **$0 — a GRCm38 coordinate source**, which would make ChIP-Atlas's 14 mouse Nr4a1 experiments
   readable. They are currently unreadable through this route by construction (§1).
4. **⛔ Outside-world — the full text of Eur J Cancer 2014;50:1657-64 (PMID 24703573).** Unchanged
   from `emc-ret-lane.md` §6: still the single highest-value unread page in this lane, and
   everything the activation bar says is provisional on it. Paywalled.

<!-- RESULTS-VERDICT -->

---

## 7 · Files

| file | what it is |
|---|---|
| [`emc_ret_cistrome.py`](./emc_ret_cistrome.py) | the instrument: catalogue discovery, characterisation, build reconciliation, interval algebra, intersection, paralogue overlap. `--fetch` / `--check` / `--selftest` |
| [`emc-ret-cistrome.json`](./emc-ret-cistrome.json) | the derived artifact |
| [`emc-ret-cistrome-inputs.json`](./emc-ret-cistrome-inputs.json) | the inputs cache — every peak set, every locus, and every network attempt with its HTTP status |
| [`tests/test_emc_ret_cistrome.py`](./tests/test_emc_ret_cistrome.py) | the guards: interval algebra, the cross-build refusal, no-reading-⇒-no-verdict, and that a null without a recovered positive control renders as UNINTERPRETABLE rather than as a negative |
| [`emc_expression_panels.py`](./emc_expression_panels.py) | `read_7_RET` — the abundance half, the ligand module and the NR4A target-set membership arm, in the same two EMC tumour series |
| [`emc-expression-panels.json`](./emc-expression-panels.json) | where `read_7_RET` lands. Read `reads.control` first |
| [`emc-ret-cistrome-map-edits.json`](./emc-ret-cistrome-map-edits.json) | the routed roadmap/graph proposal. **Not applied.** Anchors re-verified 3/3 on both `origin/main` and the worktree |
| [`emc-ret-lane.md`](./emc-ret-lane.md) | the prior pass. **§3 remains the one home of the activation-bar finding and this memo does not move it** |

## 8 · Reproducing this

```
python3 research/modalities/emc_ret_cistrome.py --selftest   # 23 checks, no network
python3 -m pytest research/modalities/tests/test_emc_ret_cistrome.py -q   # 52 tests
python3 research/modalities/emc_ret_cistrome.py             # re-derive offline from the cache
python3 research/modalities/emc_ret_cistrome.py --report    # the tables in §3-§4
```

⚠ **The inputs cache is ~50 MB**, because it holds every peak of all 79 peak sets. That is not
tidy, and it is deliberate: `--check` reproduces the artifact **exactly** from it offline, and
§4b's genome-wide paralogue overlap needs whole peak sets rather than the *RET* neighbourhood. A
future slimming that keeps only the loci's chromosomes would silently change §4b's numbers, so it
should not be done without moving that computation somewhere it can be recomputed.

The fetch half runs only in CI — `emc-expression-datasets.yml`, `mode=ret-cistrome` (occupancy),
`mode=panels` (the expression read), `mode=ret-motif` (the sibling sequence scan). The dev
sandbox's egress proxy answers `403`/connection-refused to `chip-atlas.dbcls.jp`,
`remap.univ-amu.fr`, `eutils.ncbi.nlm.nih.gov`, `rest.ensembl.org` and `www.ebi.ac.uk`, which is
measured rather than assumed and is why this runs there (CLAUDE.md §6). **$0 throughout — CPU
runners only, no GPU, no rental, nothing billed.**
