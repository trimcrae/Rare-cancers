---
id: DOC-PUB-ASO-NAT-CANDIDATE-PACKAGE-2026-09-04
title: ASO NAT candidate package
kind: memo
status: live
date: 2026-09-04
last_verified: 2026-09-04
purpose: Preserve a shortened, rendered ASO candidate for author review.
scope: Candidate source and layout verification; not submission or release authority.
audience: [maintainers, external reviewers]
---

# ASO NAT candidate — unsubmitted, 4 September 2026

This bundle contains an actual condensed revision of the ASO article, isolated from the
canonical paper and Qeios v2. It is an author-review candidate, not a publication receipt,
approval to submit, or a newly deposited archive. No manuscript has been submitted externally.

The main text falls from **3,803 to 2,241 words** (41.1% shorter); the abstract is **200 words**,
with **24 references, two tables and one figure**. Counts use the repository's existing
`submission_metrics.measure` with the companion tables and references. The title, six printed
16-mer sequences and citation PMID set are preserved. References, tables, figure and ordering CSV
preserve their canonical source content. The candidate references have a separate document ID;
copied files can retain the source worktree's line endings. Source and candidate hashes and
comparisons after normalizing line endings are recorded in `verification.json`.

## Read or rebuild

- [Revised manuscript](manuscript.md)
- [Six-page PDF](candidate.pdf)
- [Assembled HTML](candidate.html)
- [Verification record](verification.json)
- [Build wrapper](build_candidate.py)

Run `python research/release-candidates/PUB-ASO/2026-09-04/build_candidate.py` from a checkout
with Python, `pypdf` and Chromium. `--html-only` assembles HTML without launching a browser;
`--chrome PATH` selects an executable. The wrapper uses the existing journal renderer and its
unchanged Letter page geometry: 9.8-point text, line-height 1.125, 4.2-mm column gap and
35/21.5/25/21.5-mm margins. It adapts browser discovery and local file URLs for Windows.

**The candidate PDF renders to six pages**, compared with seven for the canonical journal
preview. After the initial blocked launch, the coordinator ran the local Chromium build,
rendered all six pages with Poppler at 120 dpi, and visually checked them. Text checks confirmed
all six manuscript 16-mers, the exact-hit identifier and the AI disclosure in the PDF; all six
build-input hashes match. The figure, tables, references, page numbers and margins render without
observed clipping or overlap. See `verification.json` and `candidate.build-stamp.json`.
This preview does not determine the journal's eventual production page count. Neither the build
stamp nor this document is a publication-readiness verdict.

## Scientific changes and checks

| Change | Evidence and result |
|---|---|
| Disclose the exact genomic hit | [Genome search output](../../../modalities/aso-genome-offtarget.json) records one exact 16-base hit for GGGCATATCATCAAAC, intronic in annotated lncRNA ENSG00000304430, and none for GGGCATATCTTGTGTG. Aggregate hybridisable full-gap counts remain 156 and 135. The candidate explicitly says transcription and cleavage are unmeasured. |
| Clarify scope in the abstract | [Retrieved framework record](../../../manuscripts/aso/lit-targets-aso-instruments.json) describes complementarity prediction plus transcriptomics in step one. The candidate consistently claims only its in-silico half; no transcriptomics or later framework step is represented as completed. |
| Name the variance referent | [Existing power calculation](../../../manuscripts/aso_falsification_power.py) models the natural logarithm of the selectivity ratio. The candidate states that explicitly, retaining the assumed, unmeasured SD and existing power/voidness values. |
| Condense repeated caveats | Parent/precursor overlap, alignment censoring, mismatch ceilings, duplex versus gap length, unmeasured cleavage and uncertain model junctions are each retained where needed. No analyses, candidate rankings or therapeutic claims are added. |
| Make contributions explicit | A separate Author Contributions heading credits project conception and direction to T.D.M.; the AI disclosure identifies Claude's existing role and GPT-6-Astra's revision and repository checks. This candidate still requires author review. |

The exact-hit artifact uses **zero-based inclusive** coordinates. Its start/end
176354948/176354963 correspond to **GRCh38 chr3:176354949–176354964, plus strand, one-based
inclusive**. The manuscript omits coordinates to avoid mixing conventions; it retains the gene
identifier and annotated compartment. The convention was checked against the genome scanner's
zero-origin FASTA offsets and GTF conversion in
[aso_genome_offtarget.py](../../../modalities/aso_genome_offtarget.py).

The numeric comparison preserved the following substantive results from the canonical article:

- Panel size 190 across 38 junctions; mature-parent liability 87, longest with NR4A3 for 61,
  own-parent pairing for 85; precursor class 19 and union 93.
- Alignment results: seven searches absent, 183 returned and 47 assessable; energy results:
  eight fully paired 16-base off-target duplexes, 45 within 2 kcal/mol, reagent separations
  3.2 and 3.0 kcal/mol.
- Named reagent parent duplexes eight/nine bases; longer-geometry counts 87/88/87 and
  panels 190/266/342; within-junction cut ladder 35/5, 31/3, 23/2, 9/0 and 6/0.
- Null 40.6% versus panel 45.8%; coverage 68.4%, range 39.9%–82.8%, third-junction 79.0%;
  scramble rates 10.0%/3.9%; nine of 176 distinct sequences matching multiple junctions.
- Selectivity threshold 5.0, assumed log-ratio SD 0.35, power approximately 30%/80% for
  three/six replicates at true selectivity 3; void SD approximately 0.65/1.53/2.25.

The source comparison is a focused revision check by the revising agent, not an independent
review. Underlying analyses were not rerun in full. Scientific interpretation remains limited
to computational predictions. No wet-lab potency, safety, cleavage or delivery result exists.

## Prior readiness evidence and remaining work

The source checkout was `c309b6f6e42ab6adb684c995dc9af2b6caa08fe5`. Its
[round-34 hostile-referee record](../../../autonomy/review-seats/PUB-ASO-3d5c709b69bc32a00a7776bf47303771d17d87f5-seat-hostile-referee.json)
reported no blockers and re-derived the headline results. Its actual
[full preflight log](../../../autonomy/preflight-logs/3d5c709b69bc32a00a7776bf47303771d17d87f5.log)
shows 8,212, 1,851 and 1,515 tests passed across the three suites, with 48, 3 and 1 skipped,
respectively; recorded test times total 497.16 seconds. That is historical evidence for the
source revision, not a test receipt for this candidate. Stale review tasks or `converged: false`
do not create a new scientific defect in unchanged content.

The [publication ledger](../../../../systems/graph/publications.json) records Qeios v2
[10.32388/VL3LJR.2](https://doi.org/10.32388/VL3LJR.2). Its prior read-back evidence was inspected;
direct Qeios retrieval was unavailable in this audit. That version and its files remain intact.

The [NAT author instructions](https://journals.sagepub.com/author-instructions/NAT), retrieved
4 September 2026, set Original Paper limits of 4,000 main words, 200 abstract words and five
display items. They permit preprints and charge $90 per typeset page; six pages would be $540
before any separately requested print colour. The recorded author budget is $600. The publisher's
production page count and final charge require confirmation, regardless of this preview.

The coordinator also read the rendered candidate and checked the genomic-hit disclosure against
the source artifact. The revising agent's power rerun and preserved numerical results were
reviewed; this is a focused revision check, not a fresh six-seat round or a full analysis rerun.

Finish this candidate with author review and confirmation of declarations, reconciliation of the
accepted source, corrected ordering record and immutable archive, and generation of the required
Word/anonymous upload variants from that accepted source. Required release checks remain to be
run against the final accepted package. The current archive DOI identifies existing analyses, not this candidate
revision. Exclude historical extended-report SI from the NAT upload set unless intentionally
reworked into a journal-specific supplement. The Zurich model-junction reply and actual future
bench preregistration are not prerequisites for publishing this computational proposal; the
sequence-before-order requirement remains in the manuscript.
