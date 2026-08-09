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
  L3 supplementary. Two public archival expression series and one public sarcoma-line CRISPR panel.
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
- ⚠ **No proliferation-matched control exists.** Falsifier F7 in the main text names this, and it is
  the single most likely way both readings are artefacts of a difference in cellularity or growth
  fraction rather than of the biology claimed.

## S6 · Every figure and what it is drawn from

| figure | drawn from | the honest reading |
|---|---|---|
| 1 — readings, per tumour | `emc-expression-panels.json` → `gene_reads[*].per_sample` | every tumour is visible; medians are bars |
| 2 — the locus gene by gene | same | ⛔ **closed route 2** — MTAP flat, CDKN2A carrying the signal and reversing across platforms |
| 3 — dependency qualifier | `depmap-sarcoma-dependency.json` | ⛔ argues **against** the proliferation reading |
| 4 — comparator classes | `emc-expression-panels.json` | ⭐ exposes the FET-fusion comparator a pooled arm hides |

Provenance hashes for all four are stamped in
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
   and an architecture, not a DNA-binding domain or a target repertoire.
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
- `research/literature/mtap-prmt5-emc-citations.json` — the citation anchor; every identifier in the
  main text appears there, read from a retrieval rather than recalled
