---
id: DOC-PORTFOLIO-INVESTIGATION-PUB-MTAP-PRMT5
title: "PUB-MTAP-PRMT5 portfolio investigation — does the PRMT5 reading track FET-fusion driver status? A prespecified within-series test"
level: L4
kind: investigation-finding
status: live
date: 2026-09-08
last_verified: 2026-09-08
lane: PUB-MTAP-PRMT5
repo_commit: 41cf1e61f161fa52304cc0002421e4a80e9de927
---

# PUB-MTAP-PRMT5 — the fusion-class transfer, tested inside the series that supplies the reading

## 1. The question

**Does the elevated *PRMT5* transcript reading in EMC track FET-fusion driver status, as the
fusion-class transfer premise requires — or does it not?** The comparator arm of the powered series
(GSE24369 / GPL6244) is 17/29 low-grade fibromyxoid sarcoma, **itself a FET-fusion sarcoma**
(FUS::CREB3L2). If PRMT5 elevation were a property of FET-fusion-driven transcription, that class
should read like EMC rather than like the rest of the arm. This is directly falsifiable inside data
already committed to this repository.

## 2. Paper-level merit

The manuscript's one surviving rationale is a **transfer**: PRMT5 supports fusion-driven
transcription in other EWSR1-fusion sarcomas, therefore it may matter in EWSR1::NR4A3 EMC. The
transcript reading (§3.5, *t* = 6.24) is offered as the EMC-side evidence consistent with that
transfer. Whether that reading is *class-linked* or *EMC-linked* changes what the transfer argument
can claim, and it is answerable with no new data, no network and no cost. Patient relevance is the
paper's own: EMC has no targeted agent, and the two proposed experiments are chosen on the strength
of this rationale. A test that sharpens or breaks the class link changes which experiment is worth
asking a model holder to run.

## 3. The exact evidence gap, and what makes it different from completed work

`§3.4` of the manuscript uses LGFMS as a "FET-fusion control on whether the reading is simply what a
fusion sarcoma looks like", but reports it only as a **pooled four-gene methylosome median per
comparator class** in Figure 4 (EMC +1.30 against +1.05, +1.04, +0.94). What has **not** been
computed anywhere in the package:

* the ***PRMT5*-alone* contrast of **EMC against the FET-fusion comparator class specifically**;
* the ***PRMT5* contrast between the FET comparator and the non-FET comparators** — the contrast that
  actually tests whether fusion status carries the elevation;
* the manuscript's headline contrast **recomputed with the FET class removed**, which shows how much
  of *t* = 6.24 is EMC-versus-a-fusion-sarcoma.

Inputs are exactly those the paper already owns: per-sample `z_vs_array` values in
`research/modalities/emc-expression-panels.json`, `gene_reads[GENE][GSE24369_series_matrix.txt.gz]`.
This is **not** the R2 simulation, the R3 cohort, or a re-fetch of any blocked source; it introduces
no new cohort and manufactures no independent validation. It is a within-series decomposition of a
contrast the paper already reports. It is also unrelated to the three recorded publication-readiness
blockers (the `lint_consistency` DOI-substring failure, publisher-level confirmation of the JBC
counterpart, Appendix A's `[2]`/`[3]` attribution), none of which is touched here.

## 4. The step taken

A prespecified script, `fet_class_transfer_test.py`, recomputing Welch *t* with exact permutation
(complete enumeration where C(n,k) ≤ 300,000, otherwise a fixed-seed Monte-Carlo permutation with its
standard error) for four contrasts per gene, on ten prespecified genes: *PRMT5*; the rest of the
methylosome and salvage axis (*MAT2A*, *WDR77*); the locus (*MTAP*, *CDKN2A*); PRMT-family
specificity controls (*PRMT1*, *CARM1*, *PRMT3*); and the two instrument controls the paper already
uses (*NR4A3*, *ENO3*).

Interpretations were fixed before execution:

| outcome | reading |
|---|---|
| LGFMS reads like EMC, both above non-FET | the elevation is a FET-fusion-class feature; EMC-specific claims weaken, the class transfer gains expression-level support |
| LGFMS reads like non-FET, EMC above both | fusion status carries **no** PRMT5 elevation; the reading is EMC-associated and supplies **no** class-level support to the transfer |
| EMC does not separate from LGFMS | the headline contrast is carried by the non-fusion comparators and the reading is what a fusion sarcoma looks like |

### Result — the second branch, unambiguously

*PRMT5*, GPL6244, mean *z* against each array's own probe distribution:

| class | driver | n | mean *z* |
|---|---|---:|---:|
| EMC | EWSR1::NR4A3 | 6 | **+1.290** |
| LGFMS | FUS::CREB3L2 (FET) | 17 | +1.024 |
| desmoid fibromatosis | non-fusion (*CTNNB1*) | 6 | +1.052 |
| fibrosarcoma | non-fusion | 6 | +1.011 |

| contrast | *t* | Δ mean *z* (95% CI) | permutation *p* |
|---|---:|---|---|
| EMC vs all comparators (the manuscript's) | +6.236 | +0.263 | 0.000142 (paper; > enumeration cap here) |
| **EMC vs the FET comparator** | **+5.979** | +0.266 (0.177 to 0.355) | **5.9 × 10⁻⁵**, exact, 100,947 labelings |
| **FET comparator vs non-FET** | **−0.160** | **−0.008 (−0.101 to +0.086)** | **0.873**, MC, 200,000 draws, SE 0.00075 |
| EMC vs non-FET only (FET class removed) | +4.876 | +0.259 (0.135 to 0.383) | 0.0014, exact, 18,564 labelings |

**On this platform, FET-fusion driver status carries no *PRMT5* elevation at all** (Δ = −0.008 SD,
CI excluding anything above +0.09 SD), while EMC separates from the FET-fusion class as strongly as
from the non-fusion classes. The headline *t* = 6.24 is therefore **not** diluted by the fusion
comparator and is **not** explained by it: 59% of that comparator arm is a fusion sarcoma that reads
like the non-fusion ones.

Supporting reads, same run:

* **Instrument controls behave.** *NR4A3* (+0.72 EMC vs −0.12 LGFMS, *t* = 5.08, exact *p* = 6.9 × 10⁻⁵)
  and *ENO3* (+0.46 vs −0.34, *t* = 3.60, *p* = 0.0017) separate EMC from the FET comparator, as the
  disease-defining transcript and its published fusion target should.
* **The null is not array insensitivity.** *PRMT1* is genuinely higher in LGFMS than in the non-FET
  classes (*t* = +5.83, MC *p* = 1 × 10⁻⁵) and *CARM1* genuinely lower (*t* = −5.92): the FET/non-FET
  split carries real, detectable structure in the PRMT family. *PRMT5* has none of it.
* **The locus reading survives this cut unchanged.** *MTAP* is flat against the FET class
  (*t* = 0.22, *p* = 0.83) and against non-FET (*t* = 0.92), and is **not lower in EMC than in any
  class** (+0.587 vs +0.571, +0.490, +0.473). *CDKN2A* is lower in EMC than in every class, including
  LGFMS (*t* = −5.99, *p* = 2 × 10⁻⁵). Independent within-series confirmation that the locus signal is
  *CDKN2A*, not *MTAP*.
* **Scale.** All four classes sit near *z* ≈ +1.0 for *PRMT5*. The EMC increment is 0.26 SD **on top
  of a class-wide elevation**, which quantifies the paper's own §4.4 caveat that "higher than other
  sarcomas" and "a sarcoma-wide feature" are not exclusive.

### What this does to the manuscript's argument — stated as a bounded correction, not a repair

The result **does not refute** the fusion-class transfer, and it **does not support it either**. It
removes one specific thing the paper could otherwise be read as claiming: that the transcript reading
is evidence of a fusion-driven mechanism. It is not. The reading is EMC-associated and orthogonal to
FET status in the only series able to test it. Symmetrically, it **strengthens** the specificity half
of §3.4 — EMC separates from a bona fide fusion sarcoma, so the reading is not "what a fusion sarcoma
looks like" — and it leaves falsifier **F8** (specificity must rest on fusion-driven transcription,
not growth) exactly where the paper puts it: only a functional experiment can settle it.

**No manuscript edit is proposed or made here.** The paper is under a closed contract with three
recorded blockers; this is an independent finding delivered to its owner.

## 5. Artifact · validation · provenance · limitations · stop condition

**Artifact.** `fet-class-transfer-test.json` (sha256 `83a4076e…`), produced by
`fet_class_transfer_test.py` (sha256 `4a62c9b4…`), both in this directory. Executions in
`checks/01-…` and `checks/02-…` with command, stdout, stderr and exit code (both exit 0).

**Validation / baseline.** The recomputed **EMC-vs-all-comparators** *t* for *PRMT5* is **+6.236**
against the manuscript's **+6.24**, for *MAT2A* +4.132 against +4.13, *WDR77* +2.82 against +2.82,
*MTAP* +0.685 against +0.69, *CDKN2A* −5.398 against −5.40, *NR4A3* +4.662 against +4.66 and *ENO3*
+3.607 against +3.61 — seven independent reproductions of published values through a separate code
path, which is the baseline that makes the new contrasts readable. Exact permutation is complete
enumeration, so those *p* values carry no sampling error; the one Monte-Carlo value reports its seed,
draw count and standard error.

**Provenance.** Sole input `research/modalities/emc-expression-panels.json` at repo commit
`41cf1e61f161fa52304cc0002421e4a80e9de927`; per-sample `z_vs_array` and `class` fields only. GEO
series GSE24369, platform GPL6244. No network access, no new retrieval, no paid resource, no GPU.
Class-to-driver assignments (LGFMS = FUS::CREB3L2; desmoid = *CTNNB1*; fibrosarcoma = non-fusion) are
the manuscript's own (§2.1, §3.4) and were not re-derived here.

**Limitations — load-bearing.**
1. **The FET comparator is FUS-driven, not EWSR1-driven.** This falsifies "FET-family fusion status
   predicts *PRMT5* elevation". It does **not** test "EWSR1-fusion status predicts it", because
   GSE24369 contains no other EWSR1-fusion class. A weaker premise than the manuscript's remains
   untested by this design.
2. Six EMC tumours; the LGFMS arm is 17. Small samples, one series, a decade-old array.
3. GPL3290 cannot run this test at all: its comparators are DFSP (COL1A1::PDGFB) and GIST (*KIT*),
   neither FET. The platform disagreement recorded in §3.6 is therefore untouched here.
4. No multiplicity correction across the ten genes or four contrasts; these are decompositions of one
   reported contrast, and the family-wise result in §3.5 (adjusted *p* = 0.21) still governs how
   strong the *PRMT5* reading may be called. **Nothing here makes the transcript contrast significant.**
5. Transcript abundance is not dependency and not copy number. No efficacy, safety, selectivity or
   therapeutic-window claim follows from any of it.
6. Prespecification is honest but partial: class labels and arm sizes were inspected before the
   script was written; the *z* values and every statistic reported were not.

**Stop condition — reached.** The question was binary and is answered on the only series that can
answer it. This lane stops here. It does **not** proceed to a third series (GSE28866, GSE43632,
GSE80126 have no symbol-mapped platform and would require a blocked GEO fetch), and it does not
re-open any closed route.

## 6. The credible next independent work, and the real missing dependency

* **Missing dependency, not resolvable computationally:** no EMC line exists in any public dependency
  dataset, and DepMap's raw per-line matrices are not held locally (only the reduced summaries in
  `research/modalities/depmap-sarcoma-dependency.json`). The per-line test that would matter —
  *PRMT5* Chronos effect in Ewing/FET-fusion lines against other sarcoma lines, and stratified by
  *MTAP* status — **cannot be run in this sandbox** and is recorded as unavailable, not as null.
  It needs the raw `CRISPRGeneEffect.csv`, `Model.csv` and an *MTAP* copy-number table on a runner
  with network, which is outside this lane's fences.
* **The one experiment this result sharpens:** the two-construct comparison of §4.2 (type 1, four
  retained GRG sites, against type 2, none) is now the *only* proposed test whose outcome could tie
  PRMT5 to the fusion in EMC, because the transcript route to that link is closed by this finding.
