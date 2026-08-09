---
id: DOC-EMC-MTAP-PRMT5-SI
title: Supplementary information — PRMT5 in extraskeletal myxoid chondrosarcoma
level: L3
kind: manuscript
status: live
canonical_for: ["the methods and full tables behind the 2026-08-09 EMC PRMT5/MTAP reading"]
purpose: >
  Carry every method, every per-gene reading and every negative control behind the main text, so a
  reader can check each number against the artifact that owns it rather than taking the manuscript's
  word for it.
scope: >
  L3 supplementary. Two public archival expression series, one public sarcoma-line CRISPR panel, and
  a sequence analysis of committed fusion protein sequences.
  No experiment in EMC cells, no drug exposure, no patient.
audience: [maintainers, external reviewers, autonomous research agents, collaborators]
date: 2026-08-09
last_verified: 2026-08-09
related: [DOC-EMC-MTAP-PRMT5]
---

# Supplementary information

> ⛔ **Nothing here asserts efficacy, safety, a therapeutic window or clinical readiness for any agent
> in any disease.**

---

## S1 · Data sources, and what each can and cannot support

| source | what it is | what it can support | ⛔ what it cannot |
|---|---|---|---|
| GSE24369 / GPL6244 | 6 EMC vs 29 comparator sarcomas, single-channel intensity | a within-array contrast between EMC and its comparators | absolute expression; anything about protein |
| GSE4303 / GPL3290 | 10 EMC vs 6 comparators, two-colour cDNA log-ratio | the same contrast, independently | absolute levels — every value is a ratio against a reference pool |
| DepMap sarcoma CRISPR panel | 176 sarcoma cell lines | whether a gene is required in this tissue class | **anything about EMC — the panel contains no EMC line** |

⛔ **THE THIRD ROW IS THE BINDING LIMIT OF THIS ENTIRE MANUSCRIPT.** No EMC cell line carrying the
fusion appears in any public dependency dataset. The one line on the curated record labelled EMC is
recorded by Cellosaurus as not harbouring an EWSR1 fusion, and it carries no CRISPR data. So every
dependency figure in the main text is a **transfer from other sarcomas**, and the honest bound is not
a small sample — it is **no EMC observation at all**.

## S2 · Method

**Per-gene.** Each gene's value in each sample is converted to a *z*-score against that array's own
full probe distribution, so a value is a position within that array and not a quantity comparable
across platforms. Each sample also carries its array percentile.

**Per-group.** A group score is the mean of its member genes' *z*, contrasted EMC vs comparator by
Welch's *t*. Degrees of freedom are Welch's. **No multiplicity correction is applied anywhere**, and
every reported *t* must be read with that in mind.

**Coverage floor.** A curated group emits no score unless at least 3 genes are readable and coverage
is at least 0.5. ⚠ A group that fails this floor is reported as **UNDERPOWERED — NO SCORE EMITTED**,
which is an instrument statement. It is never reported as a null result.

**The rule that governs every row.** A gene with no probe mapping is `readable: false` and its verdict
says the read could not be taken. ⛔ **Nowhere does a missing probe become a statement that a gene is
not expressed.**

## S3 · Full per-group readings

| group | genes | GPL6244 | GPL3290 |
|---|---|---|---|
| PRMT5 methylosome | PRMT5, WDR77, RIOK1, CLNS1A | *t* = +3.11, Δ = +0.090, 4/4 readable | *t* = +3.89, Δ = +0.478, 3/4 readable |
| methionine-salvage context | MAT2A, AHCY, MTR, ADI1 | *t* = +4.26, Δ = +0.139, 4/4 | *t* = +2.07, Δ = +0.283, 4/4 |
| the locus | MTAP, CDKN2A, CDKN2B | *t* = −4.06, Δ = −0.188, 3/3 | ⛔ **UNDERPOWERED — no score** (2/3 readable) |

Δ is the EMC-minus-comparator difference in standard-deviation units of that array.

⛔ **THE LOCUS READING CLOSED ROUTE 2, AND THE GROUP SCORE IS WHY IT LOOKED OTHERWISE.** Powered on one
platform only — and, more decisively, gene by gene:

| gene | GPL6244 (powered) | GPL3290 |
|---|---:|---:|
| ***MTAP*** | **−0.023 SD — flat** | −0.389 |
| *CDKN2A* | **−0.399 SD** | **+0.173 — reverses** |
| *CDKN2B* | −0.096 | unreadable |

The group's *t* = −4.06 is not wrong; it is simply **not about *MTAP***. The therapeutic window selects
on *MTAP* loss, and *MTAP* does not move where the read is powered. ⚠ **No group score could have
shown this** — the gene-level cut is what closed it, which is the methodological point worth carrying
out of this manuscript.

## S4 · The dependency prior in full

| gene | mean gene effect across 176 sarcoma lines | fraction of lines dependent |
|---|---:|---:|
| PRMT5 | −1.015 | 94.5% |
| MAT2A | −1.471 | 96.7% |
| MTAP | −0.075 | 0.0% |

⛔ **READ THIS AGAINST THE ROUTE, NOT FOR IT.** A gene required in almost every line of a tissue class
offers little to select on. The proliferation half of the transferred result is therefore close to
expected, and the part that could be specific to this disease is the effect on **fusion-driven
transcription** — which no public data measures.

⚠ **AND THE GROUP UNIT IS WRONG IN BOTH DIRECTIONS, WHICH IS THIS MANUSCRIPT'S METHODOLOGICAL
FINDING.** For the locus, the group score reported a signal its decisive gene (*MTAP*) did not have.
For the methylosome, the group score hid a signal its decisive gene (*PRMT5*) does have — pooled, EMC
ranks second of four comparator classes; *PRMT5* alone is highest. **A curated group score is a
convenience, not a unit of evidence**, and neither error is visible without cutting to the gene.

⭐ **MTAP reading as a non-dependency is the internal positive control.** A biomarker should not be a
dependency; a target should. That the panel separates them in the expected direction is weak evidence
that the panel is being read correctly.

## S5 · Negative and internal controls

- **A FET-fusion comparator is inside the comparator arm.** GSE24369's comparators include LGFMS
  (FUS::CREB3L2), a fusion sarcoma of the same family as EMC's driver. Figure 4 plots the methylosome
  against each comparator class separately for that reason: a pooled arm would hide whether the
  reading is simply what a FET-fusion sarcoma looks like.
- **The instrument-control read** (housekeeping recovery, and a marker expected high in the comparator
  arm rather than in EMC) is carried in the source artifact's `control` read and is not restated here.
- ⚠ **No proliferation-MATCHED series exists, and the in-silico substitute for it is a single gene.**
  *Superseded, retained: "No proliferation-matched control exists."* One is now run — §3.3 of the
  main text adjusts *PRMT5* for a proliferation score — but that score rests on *MKI67* alone,
  because it is the only proliferation marker with a probe on the committed panel. It leaves the
  contrast largely intact on GPL6244 (*t* 6.24 → 5.51) and removes about half of it on GPL3290
  (*t* 6.67 → 3.15). ⛔ **That is a measurement, not
  a resolution**, and falsifier F7 remains the single most likely way both readings turn out to be
  artefacts of cellularity or growth fraction.

## S6 · Every figure and what it is drawn from

| figure | drawn from | the honest reading |
|---|---|---|
| 1 — readings, per tumour | `emc-expression-panels.json` → `gene_reads[*].per_sample` | every tumour is visible; medians are bars |
| 2 — the locus gene by gene | same | ⛔ **closed route 2** — MTAP flat, CDKN2A carrying the signal and reversing across platforms |
| 3 — dependency qualifier | `depmap-sarcoma-dependency.json` | ⛔ argues **against** the proliferation reading |
| 4 — pooled vs single gene, per class | `emc-expression-panels.json` | ⭐ **changed the claim**: pooled, EMC ranks second below desmoid; *PRMT5* alone separates |
| 5 — the motif map | `emc-prmt5-substrate-motif-map.json` | ⭐ the commonest EMC and clear cell fusions keep the same four sites — ⛔ and EWSR1::FLI1, drawn beside them, keeps none |

Provenance hashes for all five are stamped in
`research/manuscripts/figures/mtap-prmt5-figure-provenance.json`; `--check` compares them against the
artifacts, so a stale figure is detectable rather than merely suspected.

## S7 · What would have to be true for this manuscript to be wrong

Stated as failure modes rather than as caveats, because a caveat is easy to skim:

1. **The contrasts are cellularity or proliferation artefacts.** Both readings would then be real
   measurements of the wrong thing. Nothing here excludes it.
2. ⛔ **THIS ONE HAS ALREADY HAPPENED.** The locus reading IS a *CDKN2A* shadow: *MTAP* is flat where
   the read is powered and *CDKN2A* reverses on the second platform. Route 2 is closed at transcript
   level, and figure 2 is where it became visible — on its first render, before any of this text was
   written. It is left in this list rather than deleted because a failure mode that fired is the most
   informative entry a list like this can carry.
3. **The clear cell sarcoma transfer does not hold.** EWSR1-ATF1 and EWSR1::NR4A3 share a 5′ partner
   and an architecture, not a DNA-binding domain or a target repertoire. ⭐ **Two things now argue
   against this failure mode without removing it** — a second EWSR1-fusion sarcoma with a
   fusion-*dependent* PRMT5 requirement (PMC12354397), and the finding that the commonest fusion of
   each disease retains the same number of PRMT5-motif sites (§S9). Both are arguments about
   plausibility. **Neither is an observation in EMC**, and this entry stays open until one is.
4. **The methylosome elevation is generic.** Elevated PRMT5 is reported across many malignancies, and
   abundance is not dependency.
5. ⛔ **Everything above is transcript.** Not one claim in this manuscript has been tested in a cell
   carrying this fusion, because no such cell is available to this programme.

## S8 · Artifacts

Every number in the main text and in this SI resolves to one of:

- `research/modalities/emc-expression-panels.json` — the readings, and the one home of every *z*,
  percentile and group score
- `research/modalities/census-route-expression-grading.json` — the grading of this route against its
  own selection criterion
- `research/modalities/depmap-sarcoma-dependency.json` — the sarcoma-line dependency prior
- `research/modalities/emc-prmt5-substrate-motif-map.json` — the motif counts of §3.2, and the two
  double-entry checks against the artifacts that already held the RG numbers
- `research/modalities/emc-fet-construct-designs.json` and
  `research/modalities/emc-fet-idr-census.json` — the committed protein sequences and sourced
  breakpoints the motif map reads; **neither was produced for this manuscript**, which is why they
  can check it
- `research/literature/mtap-prmt5-emc-citations.json` — the citation anchor; every identifier in the
  main text appears there, read from a retrieval rather than recalled


## S9 · The substrate-motif map — method, and the checks that make it quotable

**The motif.** `GRG`, taken from a retrieval and not from recollection: PRMT5's preference for
arginine flanked by glycines is reported from genome-wide methylation profiling after selective PRMT5
inhibition, with in vitro methylation used to validate the hits (PMID 30940768). A mapping experiment
in a different substrate agrees — only the DDX5 fragment carrying the C-terminal RGG/RG motif was
methylated by PRMT5 (PMC6669924).

**The method.** Occurrences are counted by exact string scan on the committed protein sequences, with
**overlaps included** (`GRGRG` is two sites and two methylatable arginines; a non-overlapping scan
would report one and silently halve a poly-RG tract). A fusion's retained 5′ sites are those at or
before `five_prime_residues_fully_encoded` — **not** the seam residue, because every one of these
junctions splits a codon and the seam residue is encoded by both partners.

**Two checks, and both are the reason the new number is worth reading.** `GRG` is computed nowhere
else in this repository, so nothing can check it directly. What can be checked is the half this
module shares with two existing artifacts:

| check | result |
|---|---|
| every re-derived RG count vs the count `emc-fet-idr-census.json` / `emc-fet-construct-designs.json` already hold | ✅ agrees for all four wild-type proteins and all four measured comparator fusions |
| each fusion's own RG count vs (retained 5′ half + NR4A3's contribution) — exercises the construct **sequences**, which the check above never touches | ✅ holds for all four constructs |

⚠ **The RG axis and the GRG axis are not the same thing, and the difference is the point of
reporting both.** This repository's RG counts were adopted for a different mechanism — FET → ATM
suppression → double-strand-break recruitment — and carry no methylation meaning. Substituting one
for the other silently would be the error; they are printed side by side instead.

⛔ **What the map cannot do.** It cannot show any fusion is methylated, name the enzyme, or predict
response. And the one disease in which a PRMT5 requirement has been shown to be fusion-dependent —
Ewing, EWSR1::FLI1 — retains **zero** sites, which is stated in the artifact's own limits and
asserted by a test, because it is the fact that stops the table being read as a response predictor.

## S10 · Corrections register

⛔ **Superseded numbers are recorded, never silently dropped.** A retracted value stays quotable
unless the record says it was retracted, and a live text carrying a "was X, now Y" narrative leaves
both in circulation. So the live text carries only the current figure and this table carries the rest.

| where | was | is | why it moved |
|---|---|---|---|
| §3, *PRMT5* EMC-minus-comparator | +0.266 and +0.744 SD | **+0.263 and +0.816 SD** | the values had drifted from `emc-expression-panels.json`, which is their one home. Checked 2026-08-09 against the committed artifact; the second differs by 0.07 SD and the reading is unchanged in direction or size class |
| §3, the statistic quoted for route 1 | the methylosome **group** *t* (3.11, 3.89) | additionally the **gene's own** *t* (6.24, 6.67) | the group score is not the unit route 1 depends on — the same error §S4 records in the other direction for the locus. The group figures are not withdrawn; they were simply the wrong ones to lead with |
| §7, the fusion-class transfer | "an assumption" | "argued rather than assumed" | a peer-reviewed fusion-dependent PRMT5 result in a second EWSR1-fusion sarcoma (PMC12354397), and the motif match of §S9. ⚠ Still not an EMC observation |

## S11 · The control calculations

**Exact permutation.** Every assignment of the observed *z* values to arms of the observed sizes is
enumerated and Welch's *t* recomputed; the two-sided *p* is the fraction with |*t*| at least the
observed. **No random sampling is used anywhere in this repository's version of this test**, so the
number is reproducible to the digit rather than to a seed. ⚠ On GPL3290 the smallest attainable *p*
is 1/8,008 — the test's resolution is the sample size.

**Confound adjustment.** A per-sample score is the mean *z* of the readable members of the named set;
*PRMT5* is regressed on it (ordinary least squares, one covariate and an intercept) and the
EMC-vs-comparator contrast recomputed on the residuals. A contrast is called surviving if it keeps
its sign and at least 60% of its magnitude — **a threshold this work chose, stated so it can be
disagreed with**; the raw and adjusted values are both printed so the reader is not obliged to accept
it.

⚠ **Coverage is the limiting fact and it is not uniform.** The proliferation score rests on *MKI67*
alone on both platforms — the other eleven requested genes have no probe on the committed panel. The
chondroid score rests on three of eight (*ACAN*, *COL11A1*, *SOX9*), and on GPL3290 only nine samples
carry all three. ⛔ **A weak proxy makes a null weak evidence**: a confound it measures badly passes
through the adjustment untouched, so "survives" here is a much softer statement than "is not a
proliferation effect".

**What is still pending.** A fuller proliferation set, the PRMT family, PRMT5's canonical Sm
substrates and additional chondroid markers were added to the panel definition on 2026-08-09,
together with a genome-wide empirical null that places each gene's *t* among all symbols on its
array. Until a `mode=panels` fetch runs, those readings are **absent, not null**, and this SI reports
them as such.
