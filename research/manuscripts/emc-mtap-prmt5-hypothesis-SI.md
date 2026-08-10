---
id: DOC-EMC-MTAP-PRMT5-SI
title: Supplementary information — PRMT5 in extraskeletal myxoid chondrosarcoma
level: L3
kind: manuscript
status: live
canonical_for: ["the methods and full tables behind the 2026-08-09 EMC PRMT5/MTAP reading"]
purpose: >
  Carry every method, every per-gene reading and every negative control behind the main text, so a
  reader can check each number against the artifact that owns it.
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

*Supplement to "The PRMT5 methylosome in extraskeletal myxoid chondrosarcoma: a fusion-class
rationale that survives, an MTAP-locus rationale that does not, and two inexpensive tests". Section
numbers of the form 3.2 refer to the main text. Nothing here asserts efficacy, safety, a therapeutic
window or clinical readiness for any agent in any disease.*

---

## S1. Data sources and their reach

| source | what it is | what it can support | what it cannot |
|---|---|---|---|
| GSE24369 / GPL6244 | 6 EMC against 29 comparator sarcomas, single-channel intensity | a within-array contrast between EMC and its comparators | absolute expression; anything about protein |
| GSE4303 / GPL3290 | 10 EMC against 6 comparators, two-colour cDNA log-ratio | the same contrast, independently | absolute levels, since every value is a ratio against a reference pool |
| DepMap sarcoma CRISPR panel, public 24Q4 release | 91 screened sarcoma cell lines, of 176 sarcoma models in the release | whether a gene is required in this tissue class | anything about EMC, since the panel contains no EMC line |

The third row is the binding limit of the whole study. No EMC cell line carrying the fusion appears
in any public dependency dataset. The one line on the curated record labelled EMC is recorded by
Cellosaurus as not harbouring an EWSR1 fusion, and it carries no CRISPR data. Every dependency figure
in the main text is therefore a transfer from other sarcomas, limited by the complete absence of an
EMC observation rather than by sample size.

## S2. Scoring rules

Per gene, each value in each sample is converted to a *z*-score against that array's own full probe
distribution, so a value is a position within that array and not a quantity comparable across
platforms. Each sample also carries its array percentile.

Per group, a score is the mean of its member genes' *z*, contrasted between EMC and the comparator
arm by Welch's *t* with Welch degrees of freedom. No multiplicity correction is applied anywhere, and
every reported *t* must be read with that in mind.

A curated group emits no score unless at least three genes are readable and coverage is at least 0.5.
A group failing that floor is reported as underpowered with no score emitted, which is an instrument
statement rather than a null result.

A gene with no probe mapping is recorded as unreadable, and its verdict states that the read could
not be taken. A missing probe is never recorded as an absence of expression.

## S3. Full per-group readings

| group | genes | GPL6244 | GPL3290 |
|---|---|---|---|
| PRMT5 methylosome | PRMT5, WDR77, RIOK1, CLNS1A | *t* = +3.11, Δ = +0.090, 4/4 readable | *t* = +3.89, Δ = +0.478, 3/4 readable |
| methionine-salvage context | MAT2A, AHCY, MTR, ADI1 | *t* = +4.26, Δ = +0.139, 4/4 | *t* = +2.07, Δ = +0.283, 4/4 |
| the locus | MTAP, CDKN2A, CDKN2B | *t* = −4.06, Δ = −0.188, 3/3 | underpowered, no score, 2/3 readable |
| PRMT family, control | PRMT1/2/3, CARM1, PRMT6/7/8/9 | *t* = +0.33, Δ = +0.013, 7/8 | *t* = +1.34, Δ = +0.126, 6/8 |
| proliferation, control | 11 cell-cycle genes | *t* = +0.44, Δ = +0.090, 11/11 | *t* = +2.91, Δ = +0.446, 11/11 |
| chondroid lineage, control | COL2A1, COL9A1, COL11A2, SOX5, SOX6 | *t* = +0.42, Δ = +0.027, 5/5 | *t* = −0.83, Δ = −0.179, 5/5 |
| Sm proteins, context only | SNRPB, SNRPD1/D3/E/G | *t* = +0.22, Δ = +0.014, 5/5 | *t* = +3.15, Δ = +0.296, 4/5 |

Δ is the EMC-minus-comparator difference in standard-deviation units of that array. The last four
rows are controls and context rather than four further hypothesis tests. The Sm row is context in the
strictest sense, because an array cannot see a methyl mark, so the abundance of PRMT5's canonical
substrates says nothing about whether PRMT5 is acting on them. The proliferation and chondroid group
scores in this table use the panel's own coverage rule and member list, while the adjustment in main
text section 3.6 uses a twelve-gene and an eight-gene score with a per-sample coverage floor, so the
two are close but not the same instrument (S11).

The locus reading gene by gene, which closed that rationale:

| gene | GPL6244 (powered) | GPL3290 | genome-wide rank of \|*t*\| |
|---|---|---|---|
| MTAP | +0.053 SD, flat, *t* = +0.69 | −0.607 SD, opposite sign | top 74% / top 26% |
| CDKN2A | −0.481 SD, *t* = −5.40 | +0.175 SD, reversed | top 3.5% / top 49% |
| CDKN2B | −0.136 SD | unreadable | top 34% / not applicable |

The group's *t* of −4.06 is accurate but is not a reading of MTAP. The therapeutic window selects on
MTAP loss, and MTAP does not move where the read is powered. A group score cannot distinguish the
two, and the gene-level reading is what closed the rationale.

## S4. The dependency prior in full

| gene | mean gene effect across the 91 screened sarcoma lines | fraction of those lines dependent |
|---|---:|---:|
| PRMT5 | −1.015 | 94.5% |
| MAT2A | −1.471 | 96.7% |
| MTAP | −0.075 | 0.0% |

This table bounds the route rather than supporting it. A gene required in almost every line of a
tissue class offers little to select on. The proliferation half of the transferred result is
therefore close to expected, and the part that could be specific to this disease is the effect on
fusion-driven transcription, which no public data measures.

The same panel says the same thing more sharply about a different route in this portfolio. Read on
2026-08-09 for the proteasome inhibitor carfilzomib, the only agent in this programme with ex-vivo
activity in patient-derived EMC models, the same 91 lines give PSMB1, PSMC1, PSMD1 and VCP at 100%
dependent and carfilzomib's own target PSMB5 at 97.8%, with selectivity against the rest of DepMap of
−0.10 to +0.17. A target required in every line of the class, and equally required outside it, offers
nothing to select on.

The group unit fails in both directions. For the locus, the group score reported a signal its
decisive gene (MTAP) did not have. For the methylosome, the group score hid a signal its decisive
gene (PRMT5) does have, since pooled across four genes EMC ranks second of four comparator classes
while PRMT5 alone is highest. Neither is visible without reading the constituent genes, so a curated
group score is treated here as a summary and not as a unit of evidence.

MTAP reading as a non-dependency is the internal positive control. A biomarker should not be a
dependency and a target should, and the panel separating them in the expected direction is weak
evidence that it is being read correctly.

## S5. Negative and internal controls

A FET-fusion comparator sits inside the comparator arm. GSE24369's comparators include low-grade
fibromyxoid sarcoma (FUS::CREB3L2), a fusion sarcoma of the same family as EMC's driver. Main text
figure 4 plots the methylosome against each comparator class separately for that reason, since a
pooled arm would hide whether the reading is simply what a FET-fusion sarcoma looks like.

The instrument-control read, covering housekeeping recovery and a marker expected high in the
comparator arm rather than in EMC, is carried in the source artifact's control block and is not
restated here.

No proliferation-matched series exists, and the in-silico substitute for one disagrees between
platforms. Main text section 3.6 adjusts PRMT5 for a twelve-gene proliferation score read on all 35
and all 16 samples. It leaves the contrast largely intact on GPL6244 (*t* 6.24 to 5.23, where the
score is flat at *t* = 0.45) and takes most of it on GPL3290 (*t* 6.67 to 2.71, where the score is
itself elevated in EMC at *t* = 3.00 and correlates with PRMT5 at *r* = 0.60). The adjustment
measures the confound without resolving it, and falsifier F7 remains the most likely way both
readings turn out to be artefacts of cellularity or growth fraction.

## S6. Figures and their sources

| figure | drawn from | reading |
|---|---|---|
| 1, readings per tumour | `emc-expression-panels.json`, `gene_reads[*].per_sample` | every tumour is visible; medians are bars |
| 2, the locus gene by gene | same | closed the MTAP rationale: MTAP flat, CDKN2A carrying the signal and reversing across platforms |
| 3, dependency qualifier | `depmap-sarcoma-dependency.json` | argues against the proliferation reading |
| 4, pooled against single gene, per class | `emc-expression-panels.json` | pooled, EMC ranks second below desmoid; PRMT5 alone separates |
| 5, the motif map | `emc-prmt5-substrate-motif-map.json` | the commonest EMC and clear cell fusions keep the same four sites, and EWSR1::FLI1, drawn beside them, keeps none |

Provenance hashes for all five are stamped in
`research/manuscripts/figures/mtap-prmt5-figure-provenance.json`, and `--check` compares them against
the artifacts, so a stale figure is detectable.

## S7. Failure modes

1. The contrasts are cellularity or proliferation artefacts. Both readings would then be real
   measurements of the wrong thing, and nothing here excludes it.
2. This failure mode has already occurred. The locus reading is a CDKN2A shadow: MTAP is flat where
   the read is powered and CDKN2A reverses on the second platform. The MTAP rationale is closed at
   transcript level, and figure 2 is where it became visible. The entry is retained rather than
   deleted because it records a failure mode that fired.
3. The clear cell sarcoma transfer does not hold. EWSR1-ATF1 and EWSR1::NR4A3 share a 5′ partner and
   an architecture, not a DNA-binding domain or a target repertoire. Two things now argue against
   this failure mode without removing it: a second EWSR1-fusion sarcoma with a fusion-dependent PRMT5
   requirement, and the finding that the commonest fusion of each disease retains the same number of
   PRMT5-motif sites (S9). Both are arguments about plausibility, neither is an observation in EMC,
   and this entry stays open until one is.
4. The methylosome elevation is generic. Elevated PRMT5 is reported across many malignancies, and
   abundance is not dependency.
5. Every reading above is at transcript level. No claim in the manuscript has been tested in a cell
   carrying this fusion, because no such cell is available to this work.

## S8. Artifacts

Every number in the main text and in this supplement resolves to one of:

- `research/modalities/emc-expression-panels.json`, the readings, and the one home of every *z*,
  percentile and group score
- `research/modalities/census-route-expression-grading.json`, the grading of this route against its
  own selection criterion
- `research/modalities/depmap-sarcoma-dependency.json`, the sarcoma-line dependency prior
- `research/modalities/emc-prmt5-route-controls.json`, the control calculations of main text
  section 3.6
- `research/modalities/emc-prmt5-substrate-motif-map.json`, the motif counts of S9 and the two
  double-entry checks against the artifacts that already held the RG numbers
- `research/modalities/emc-fet-construct-designs.json` and
  `research/modalities/emc-fet-idr-census.json`, the committed protein sequences and sourced
  breakpoints the motif map reads; neither was produced for this manuscript, which is why they can
  check it
- `research/literature/mtap-prmt5-emc-citations.json`, the citation anchor, in which every identifier
  used in the main text appears, read from a retrieval rather than recalled
- `research/literature/emc-prior-art-2026-08-09.json`, the Europe PMC prior-art screen of main text
  section 1.3, with its retrieval record and its own statement of what a title-and-abstract screen
  can and cannot show

## S9. The substrate-motif map

The motif is GRG, taken from a retrieval rather than from recollection: PRMT5's preference for
arginine flanked by glycines is reported from genome-wide methylation profiling after selective PRMT5
inhibition, with in vitro methylation used to validate the hits (main text reference 8). A mapping
experiment in a different substrate agrees, since only the DDX5 fragment carrying the C-terminal
RGG/RG motif was methylated by PRMT5 (main text reference 9).

Occurrences are counted by exact string scan on the committed protein sequences, with overlaps
included, because GRGRG is two sites and two methylatable arginines and a non-overlapping scan would
report one and silently halve a poly-RG tract. A fusion's retained 5′ sites are those at or before
`five_prime_residues_fully_encoded`, excluding the seam residue, because every one of these junctions
splits a codon and the seam residue is encoded by both partners.

GRG is computed nowhere else in this repository, so nothing can check it directly. What can be
checked is the half this module shares with two existing artifacts:

| check | result |
|---|---|
| every re-derived RG count against the count `emc-fet-idr-census.json` and `emc-fet-construct-designs.json` already hold | agrees for all four wild-type proteins and all four measured comparator fusions |
| each fusion's own RG count against its retained 5′ half plus NR4A3's contribution, which exercises the construct sequences that the check above never touches | holds for all four constructs |

The RG axis and the GRG axis are not the same quantity, and both are reported side by side. This
repository's RG counts were adopted for a different mechanism, FET protein suppression of ATM
signalling and double-strand-break recruitment, and carry no methylation meaning; one must not be
substituted for the other.

The map cannot show that any fusion is methylated, name the enzyme, or predict response. The one
disease in which a PRMT5 requirement has been shown to be fusion-dependent, Ewing sarcoma with
EWSR1::FLI1, retains zero sites. That fact is stated in the artifact's own limits and asserted by a
test, and it is why the table cannot be read as a response predictor.

## S10. The control calculations

Exact permutation. Every assignment of the observed *z* values to arms of the observed sizes is
enumerated and Welch's *t* recomputed; the two-sided *p* is the fraction with |*t*| at least the
observed. No random sampling is used anywhere in this implementation of the test, so the value is
exactly reproducible. On GPL3290 the smallest attainable *p* is 1/8,008, so the test's resolution is
the sample size.

Confound adjustment. A per-sample score is the mean *z* of the readable members of the named set;
PRMT5 is regressed on it by ordinary least squares with one covariate and an intercept, and the
EMC-versus-comparator contrast recomputed on the residuals. A contrast is called surviving if it
keeps its sign and at least 60% of its magnitude, a threshold chosen for this work rather than taken
from an established convention; the raw and adjusted values are both reported.

Coverage. The proliferation score uses twelve genes and scores all 35 and all 16 samples; the
chondroid score uses eight and scores 35 and 14. A proxy still makes a null weak evidence, since a
confound the proxy measures badly passes through the adjustment untouched, so a surviving result is
a much weaker statement than a failing one; the failure on GPL3290 is the stronger direction of the
same instrument.

Group scores for the adjustment. A per-sample score is the mean *z* of the member genes that sample
has a value for, provided it has at least 60% of them. It is a coverage-weighted mean rather than an
intersection: requiring every member gene would drop GPL3290 from 16 samples to 9, so adding genes
to the definition would have reduced the sample without that being visible in the output. The floor
stops a sample scoring off one stray gene while keeping all sixteen.

The genome-wide null. The same statistic is computed for every symbol the platform's probes map to
(18,474 and 14,402), and each gene of interest placed in that distribution. It is computed at fetch
time because that is the only point at which the full probe matrix exists. It double-enters the
panel, since the null recomputes from the raw matrix, by a separate code path, the statistic the
panel computes from reduced per-gene values, and a wanted gene's *t* must agree between them. It
does, for every gene on both platforms.

Status. The PRMT family, the fuller proliferation set, the Sm substrates, the additional chondroid
markers and the genome-wide null were added to the panel definition on 2026-08-09 and fetched the
same day; every figure in main text sections 3.5 and 3.6 is read from that fetch.

---

## Appendix S1. Corrections register

Per [CLAUDE.md](../../CLAUDE.md) rule 1.2, superseded numbers are recorded rather than silently
dropped. A retracted value stays quotable unless the record says it was retracted, and a live text
carrying a "was X, now Y" narrative leaves both in circulation. So the live text carries only the
current figure and this appendix carries the rest. It is the full register; the main text's Appendix
A carries the subset that lived in the main text.

| where | was | is | why it moved |
|---|---|---|---|
| §3, *PRMT5* EMC-minus-comparator | +0.266 and +0.744 SD | **+0.263 and +0.816 SD** | the values had drifted from `emc-expression-panels.json`, which is their one home. Checked 2026-08-09 against the committed artifact; the second differs by 0.07 SD and the reading is unchanged in direction or size class |
| §3, the statistic quoted for route 1 | the methylosome **group** *t* (3.11, 3.89) | additionally the **gene's own** *t* (6.24, 6.67) | the group score is not the unit route 1 depends on — the same error §S4 records in the other direction for the locus. The group figures are not withdrawn; they were simply the wrong ones to lead with |
| §3/§S3, the locus genes | *MTAP* −0.023 / −0.389; *CDKN2A* −0.399 / +0.173; *CDKN2B* −0.096 | **+0.053 / −0.607; −0.481 / +0.175; −0.136** | ⛔ **CAUSE NOT ESTABLISHED, AND AN EARLIER EXPLANATION HERE WAS WRONG.** *Superseded, retained: "a re-fetch ran on a NARROWER probe→symbol bridge (0.931 against 0.984), and a narrower bridge changes which probes map."* That was a story built on a coincidence. Checked against every committed version of the artifact: ***MTAP* reads +0.053 in all of them — at bridge rates 0.984, 0.931 AND 0.981**, and always on one mapped probe. Bridge width does not move this gene. The −0.023 appears in **no committed artifact at all**, so it entered the prose from a source this repository cannot show, and the live values are the ones the artifact has always carried |
| §3.1/§S4, the dependency denominator | "across 176 sarcoma cell lines" | **"across the 91 screened sarcoma cell lines"** | ⛔ a real error, in the direction that overstated the evidence base, and it was in four places including the abstract. The release lists 176 sarcoma MODELS; only **91** carry CRISPR gene-effect data, and every per-gene record in the artifact says `n_sarcoma: 91`. The percentages themselves are unchanged — they were always computed on the screened subset — but they were being attributed to a denominator almost twice its true size. Caught 2026-08-09 by a later run that added a second gene group and printed the same 91 |
| §7, the fusion-class transfer | "an assumption" | "argued rather than assumed" | a peer-reviewed fusion-dependent PRMT5 result in a second EWSR1-fusion sarcoma, and the motif match of §S9. ⚠ Still not an EMC observation |
| §S5, the proliferation control | *Superseded, retained: "No proliferation-matched control exists."* | one is now run, and it disagrees between platforms | the in-silico substitute is reported in §S5 and in main text §3.6. It is a measurement, not a resolution |
| §S11 status line | *Superseded, retained: an earlier version reported the added panel members as pending.* | they were fetched on 2026-08-09 | the re-fetch landed the same day |
| this file's own register | §S10, numbered in sequence with the method sections | Appendix S1 | `lint_style.py` exempts sections under an `Appendix` heading, because superseded-value bookkeeping is required by rule 1.2 and belongs in an appendix rather than in running text. The content is unchanged |
| both files' register | repository house style throughout: glyph warnings, bold on the load-bearing clause, sentence-shaped headings, running commentary on the paper's own honesty | journal register in the running text, with the house-style rows preserved verbatim inside this appendix | the register was correct for a maintainer and wrong for a journal reader. No measured statement was removed. The rows above are left in their original wording rather than rewritten, because a corrections register that is itself edited is no longer a record |

⭐ **AND THE THIRD ROW IS A LESSON ABOUT THIS WORK'S OWN METHOD, WHICH IS WHY IT IS NOT JUST
BOOKKEEPING.** A plausible mechanism was available — the annotation bridge narrowed on the same day
the numbers were noticed to differ — and it was written down as the cause without the one check that
could separate it from coincidence. The check was a `git log` over the artifact, it was free, and it
refutes the explanation: **four committed versions, three different bridge rates (0.984, 0.931,
0.981), and *MTAP* reads +0.053 in every one of them.** ⛔ **The −0.023 is in no committed artifact**,
so what was corrected was a stale figure in the prose rather than a value that moved.
⭐ **What survives, and is now measured rather than asserted: every figure this manuscript quotes is
stable across three independent annotation bridges** — *PRMT5* +0.2632 and *MTAP* +0.053 at all
three — which is a stronger statement about reproducibility than the one it replaces.

⚠ **The bridge itself is volatile and the values are not, which is the useful pair.** The
accession→symbol step was re-run four times on 2026-08-09 and resolved 0.984, 0.931, 0.931 and 0.981
of GPL6244's accessions — the middle two returning **zero** gene links from NCBI in ~15 minutes each,
the endpoint having briefly stopped answering and then recovered. **None of that moved a number this
manuscript quotes.** The bridge now has a committed home so a future outage cannot narrow it at all.
