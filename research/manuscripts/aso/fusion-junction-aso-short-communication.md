---
id: DOC-FUSION-JUNCTION-ASO-SUBMISSION
title: "Design and predicted specificity limits of junction-spanning gapmers against NR4A3 fusions in extraskeletal myxoid chondrosarcoma"
level: L3
kind: manuscript
status: live
canonical_for:
  - the submitted form of the fusion-junction ASO work
purpose: >
  The submission manuscript for PUB-ASO, going first to bioRxiv as a preprint — free, verified at
  primary source, and compatible with every journal still under consideration. The journal venue is
  OPEN: Cancer Gene Therapy was eliminated once its own guide to authors was read, because it levies
  a mandatory £145/$238 per typeset page on the subscription route. See
  fusion-junction-aso-submission-plan.md §1c and fusion-junction-aso-preprint-checklist.md. Its
  provenance archive, including every superseded value and the full correction
  history, is fusion-junction-aso-working-record.md; the numbers themselves live in the artifacts
  under research/modalities/ and are not duplicated here.
scope: >
  Computational design and specificity screening only. No wet-lab experiment was performed, and
  nothing here asserts efficacy, potency, safety, a therapeutic window, delivery to a tumour, or
  clinical readiness for any sequence.
audience: [external reviewers, collaborators, maintainers]
date: 2026-08-13
last_verified: 2026-08-13
---

# Design and predicted specificity limits of junction-spanning gapmers against *NR4A3* fusions in extraskeletal myxoid chondrosarcoma

**Author.** Tristan D. McRae

*Independent researcher, unaffiliated.* Correspondence: trimcrae@gmail.com
ORCID: [to be inserted]

**Running title.** Junction gapmers across NR4A3 fusions

**Keywords.** antisense oligonucleotide; gapmer; RNase-H1; fusion transcript; NR4A3; extraskeletal
myxoid chondrosarcoma

---

## Abstract

**Background.** Extraskeletal myxoid chondrosarcoma is an ultra-rare sarcoma defined by
rearrangement of *NR4A3* to a variable 5′ partner. Its chimeric mRNA carries a breakpoint seam
absent from every normal transcript — its one tumour-exclusive RNA feature. A structured literature
search retrieved no junction-directed oligonucleotide against any NR4A3 fusion.

**Methods.** Chimeras were built at the mRNA level from canonical Ensembl models, acceptor exon
retained whole; every donor-exon × acceptor-exon pair across five partners was graded.
Junction-spanning 16-mer 5-6-5 LNA/DNA/LNA gapmers were tiled over each frame-compatible seam, then
screened against all six parent transcripts, against RefSeq RNA by gap-resolved BLAST, exhaustively
for ≤1 mismatch over 186,185 transcripts, and — because RNase-H1 acts in the nucleus — exhaustively
against those transcripts unspliced and against every position of GRCh38 in both orientations.

**Results.** Of 231 graded pairs, 38 are frame-compatible, and all 38 yield a gapmer matching no
parent perfectly. All 38 were screened with alignment orientation filtered, since a
reverse-complement match cannot hybridise; the filter reorders junctions rather than rescaling them. Nine designs at six junctions then carry no
hybridisable near-match among non-parent transcripts and no single-mismatch match among
186,185 transcripts. That search is capped, and re-screening those six junctions ten times deeper
leaves three standing: three designs that had returned no near-match at all return 27, 29 and 84, and
three carry gap-spanning cleavage risks, 64 at worst. The parents are a separate liability no
transcript screen reaches: 19 of 190 designs pair the catalytic gap in parent pre-mRNA, nine across
the wild-type *NR4A3* intron-2/exon-3 boundary, and 87 of 190 pair it in mature parent transcript
inside a duplex of at least ten base pairs, 61 of those against wild-type *NR4A3*. An exhaustive scan
of all 3.10 × 10⁹ nucleotides of GRCh38 in both orientations finds 20 of 176 designs with a
gap-paired, strand-agreeing site in a parent gene or an *NR4A* paralogue. Two designs
survive every screen, at junctions no patient is reported to carry. One 16-mer spans the *EWSR1*
exon 12, *TAF15* exon 11 and *FUS* exon 10 seams through ten identical donor bases — a sequence
property, not a clinical one: published exon-resolved *TAF15::NR4A3* breakpoints are exon 6.

**Conclusions.** Designability does not limit junction gapmers here, but clean designs are far
scarcer than a capped search suggests, and it is the parent transcripts rather than the transcriptome
that consume them. The limiting step is discrimination between the fusion and its parents at the
catalytic gap, set by enzymology and chemistry, which no computation here resolves.

---

## 1 · Introduction

EMC is defined in the large majority of cases by an in-frame fusion of *EWSR1* to the orphan nuclear
receptor *NR4A3*,<sup>1</sup><!--PMID:8634690--> with *TAF15* accounting for a substantial minority
and *TCF12* and *TFG* reported rarely.<sup>2</sup><!--PMID:32572850--> *FUS::NR4A3* is reported in
a recent series that identified it by sequencing in two of five variant EMCs.<sup>3</sup><!--PMID:41755350--> Next-generation sequencing of six EMCs finds
few recurrent secondary mutations beyond the fusion,<sup>4</sup><!--PMID:28423517--> so it is to a
first approximation the single clonal driver. In every junction type described, the predicted
product joins the amino-terminal transactivation domain of the partner to essentially the
entire NR4A3 protein, including its nuclear-receptor DNA-binding domain.<sup>1,5</sup><!--PMID:8634690,11156374-->

That driver is currently untargeted. Surgery with clear margins is the backbone of localised
disease, and for advanced disease no agent is approved specifically for EMC.<sup>6</sup><!--PMID:41055792--> The largest
EMC-specific prospective study, a single-arm phase 2 of pazopanib in centrally confirmed
*NR4A3*-translocated disease, returned four objective responses in 22 evaluable patients with a
median progression-free survival of 19 months (95% CI 11–27),<sup>7</sup><!--PMID:31331701--> and
first-line anthracycline-based chemotherapy returned four responses in ten evaluable patients in a
molecularly confirmed retrospective series.<sup>8</sup><!--PMID:24345066--> The population a
fusion-directed agent would address is close to the whole disease: across 58
molecularly confirmed cases, 79% carried *EWSR1::NR4A3*, 16% *TAF15::NR4A3* and 3%
*TCF12::NR4A3*.<sup>9</sup><!--PMID:36948401-->

Protein-directed approaches to this fusion face a structural problem. The *NR4A3* ligand-binding
domain is retained near-intact in the chimera and is identical in sequence to wild-type NR4A3, so a
ligand that engages it cannot distinguish fusion from wild type. That matters because NR4A3 can be
tumour-suppressive: combined *NR4A1*/*NR4A3* loss causes acute myeloid leukaemia in
mice,<sup>10</sup><!--PMID:17515897--> and NR4A3's roles in cancer are context-dependent, tumour-suppressive in some
tissues and tumour-promoting in others.<sup>11</sup><!--PMID:33106376--> Either way, wild-type NR4A3 is not a protein a
therapy should silence indiscriminately. The chimeric mRNA
does not share this problem. Its breakpoint seam is a contiguous sequence absent from both parent
transcripts, so discrimination can in principle be enforced by base-pairing rather than by protein
conformation.

Targeting a fusion breakpoint with an oligonucleotide is not new; the approach has a continuous
lineage from
1991,<sup>12</sup><!--PMID:1794439--> including RNase-H-dependent antisense at a sarcoma fusion breakpoint in
1997,<sup>13</sup><!--PMID:9049825--> the general fusion-exclusivity rationale stated as a principle in 2005,<sup>14</sup><!--PMID:16083345-->
parental sparing demonstrated in at least four fusions,<sup>15–18</sup><!--PMID:33241214,36265509,21846246,23052253--> a bi-shRNA lipoplex directed
at the *EWSR1::FLI1* junction taken to preclinical justification,<sup>19</sup><!--PMID:27166877--> and a GalNAc-conjugated
junction siRNA in fibrolamellar hepatocellular carcinoma that passed the delivery gate in a rare
fusion-driven cancer.<sup>20</sup><!--PMID:37980543--> The contribution here is therefore not the modality but the indication. Across 5,153
unique records retrieved from Europe PMC, four mention *EWSR1::NR4A3* at title or abstract level,
resolving to three papers, none an oligonucleotide study.

Two questions follow that the field has not asked of this disease. First, prior design work has
addressed only *EWSR1*, while the partner varies — and partner identity is not clinically inert:
every reported objective response to an antiangiogenic tyrosine-kinase inhibitor in advanced EMC has
occurred in a non-*TAF15* patient, though the *TAF15* arm comprises three to five patients with zero
events and its Wilson upper bound remains compatible with equal response.<sup>7,21</sup><!--PMID:31331701,24703573--> Second,
whether a junction oligonucleotide must be bespoke per patient, or whether one sequence can serve
more than one fusion, determines whether the deployable artefact for an ultra-rare disease is a stock
reagent or a panel.

## 2 · Methods

**Transcript models.** Canonical transcripts for *EWSR1* (ENST00000397938), *TAF15*
(ENST00000605844), *TCF12* (ENST00000333725), *FUS* (ENST00000254108), *TFG* (ENST00000240851) and
*NR4A3* (ENST00000395097) were obtained from Ensembl. Each model was self-checked before use: exon
lengths must sum to the spliced cDNA, the CDS must occur exactly once within it, and translation of
the CDS must reproduce the annotated protein. Per-exon coding content was additionally cross-checked
against an independent exon audit for *EWSR1* and *NR4A3*; for the other four partners that audit
does not exist, and the
weaker check is recorded per gene in the released artefacts.

**Chimera construction.** Chimeras were built at the mRNA level, not by concatenating coding
sequences: a fusion transcript retains the acceptor exon whole, so *NR4A3* exon-3 bases 5′ of its own
initiation codon are physically present in the transcript and are the bases an oligonucleotide meets
immediately 3′ of the seam. Let *U* be the number of retained untranslated acceptor-exon nucleotides, measured here as 2.
The chimeric open reading frame is then in frame when (donor coding nucleotides + *U*) mod 3 = 0. Every declared exon pair was graded by this rule before any design was emitted, and a
panel was emitted only for a pair graded frame-compatible.

**Design.** Junction-spanning 16-mer gapmers were tiled in a 5-6-5 LNA/DNA/LNA architecture on a
phosphorothioate backbone, the chemistry the design rules below assume, retaining
only registers in which the seam falls inside the six-nucleotide DNA gap, since RNase-H1 cleaves
within the DNA:RNA duplex of the gap and needs a minimum run of contiguous DNA to do so. Reported
minima for that run are five to six nucleotides,<sup>22,23</sup><!--PMID:39126066,41614678--> and for
LNA/DNA/LNA gapmers specifically a six-nucleotide gap gives noteworthy but incomplete activity, with
seven to ten reported as optimal.<sup>24</sup><!--PMID:24981949--> A six-nucleotide gap therefore sits
at the short end of the usable range and below the reported optimum. It was retained because it
admits exactly five junction-spanning registers per
seam, which is the whole design space explored here. No claim is made that a short gap improves
fusion-versus-parent discrimination: one series that shortened a 5-10-5 gapmer to 5-6-5 reported
lower off-target knockdown but also lower on-target activity and lower allele
selectivity.<sup>22</sup><!--PMID:39126066--> Discrimination is set by the junction-unique bases inside
the gap, not by identity across the whole oligonucleotide, so designs were ranked by a gap-level
margin: the number of junction-unique bases inside the gap on the shorter side. Each candidate was
tested against all six parent transcripts, not only the two parents of its own fusion, because the
FET-family donors (FUS, EWSR1 and TAF15) are paralogues with similar low-complexity amino-termini.

**Specificity screening.** Five screens were applied, over four compartments. A gap-resolved screen queried each
target window against human RefSeq RNA (blastn-short, low-complexity filter off, ≥14/16 identity) and
classified each near-match by whether the six-nucleotide gap was fully base-paired. Records of the
six parent genes were counted separately and are excluded from every near-match count reported here,
since each parent pairs one wing by construction and would otherwise dominate the list; the parents
are assessed instead by the gap-level margin and by the fourth screen below. An exhaustive
seed-and-extend scan then searched 186,185 transcripts (GRCh38.p14) for exact and ≤1-mismatch matches;
this arm is complete for substitutions by construction and does not detect insertions or deletions.
The BLAST arm did not parse alignment orientation. `blastn` searches both strands, and a transcript
carrying the reverse complement of the target window cannot be hybridised by an antisense
oligonucleotide, so it is not a liability at all — yet such hits passed the identity filter and,
where they spanned the catalytic gap, were recorded as cleavage risks. Orientation is parsed and filtered in all 38 junction
screens, the 183 designs they hold, and therefore in every cleanliness statement made here; the only
two screens in the released set that are not filtered are modelled control seams built in amino-acid
rather than transcript coordinates, which carry no junction and support no claim.

Both of those screens search mature transcript sequence, so a third was added over the nuclear
compartment they cannot reach. Unspliced sequence and exon coordinates for all six parent transcripts were
retrieved from Ensembl, and every design's target window was scanned against that sequence in both
orientations at the same ≤2-mismatch threshold the alignment screen admits, which keeps the two arms
comparable: a stricter threshold here would return a cleaner pre-mRNA result for that reason alone.
This arm is exhaustive for substitutions by construction, seeded on three blocks of the 16-mer so a
hit within the threshold must match one block exactly, and each hit is classified as wholly intronic,
wholly exonic, or spanning an intron–exon boundary, since only the exonic class could have been
visible to a transcript screen. Pre-mRNA is transcribed in transcript orientation, so the same
orientation rule applies: a forward match is hybridisable and a reverse-complement match is not.
Target-site accessibility was estimated as mean unpaired probability over a local fold of up to 180
nucleotides, and spans 0.160 to 0.707 across all 190 designs at real exon junctions (median 0.477).
It is released with the artefacts and is not used to rank anything here.

A fourth screen addresses the parent transcripts the alignment screen excludes, in the compartment
the pre-mRNA arm cannot reach. Mature parent transcripts were spliced from the same Ensembl records,
and every design's target window was compared to every 16-nucleotide window of all six in the
forward orientation only. A window counts only if all six gap positions are paired; its size is the
longest contiguous run of perfect pairing containing the whole gap, which is the duplex RNase-H1
would see. Runs shorter than ten base pairs are not treated as plausible substrates — a stated
threshold, not a measured one, so every design's longest run is released. Ten is the strict end of
the seven to ten hybridised nucleotides reported as the minimum for RNase-H1 to engage a
heteroduplex through its hybrid-binding domain and cleave,<sup>25</sup><!--PMID:35664704--> so the
count it produces is a floor: at seven the same screen returns 175 of 190 rather than 87.

**Discrimination model.** The binary assumption that any mismatch inside the gap abolishes cleavage
is not supported by the primary literature and is not used for any claim of cleanliness. The field's
general figure for single-nucleotide discrimination by a gapmer carrying no positional modification
in its gap is approximately five-fold,<sup>26</sup><!--PMID:23963702--> and at 16-mer length one study reports no efficient discrimination at
all.<sup>27</sup><!--PMID:7567450--> Both are measured against a single-nucleotide substitution rather than a fusion
seam, and the pessimistic one used unmodified antisense DNA; they are used here as bounds for
unmodified chemistry, not as a property of this architecture. Gapmer-specific work points the same
way and is the reason the bounds are not narrowed: across more than 120 gapmers spanning five
single-nucleotide changes, only two or three achieved preferential cleavage of the mutant allele in
cells,<sup>28</sup><!--PMID:28970564--> and where allele selectivity is achieved it is engineered by
modifying a gap position to block cleavage of the near-match rather than obtained from the mismatch
itself.<sup>29</sup><!--PMID:42327837--> Every gap-resolved screen was therefore re-scored under both bounds as a graded
residual cleavage load, holding the hit set fixed so that only the scoring changed: all 38 junction
screens and 39 of the 45 screens released in total, the exceptions being one coverage-only
control screen that records no gap-mismatch depth and so cannot be graded at all, and the five deeper
re-screens of §3.6, which are released ungraded. The re-score counts
only hybridisable hits where it can — that is, where the retained hit list is complete, so every
hit's strand is known. Two distinct bounds follow, and they run in opposite directions. Where a hit
list is truncated the strand of the remainder is unrecoverable, so some designs keep a strand-blind
count, which over-counts liability because it includes matches no antisense oligonucleotide can
hybridise: an upper bound. Screens produced before the orientation fix carry that count for every
truncated design; later screens carry an already-filtered one. The same truncation also means fewer
hits are recorded than the search returned, so the count of hits is itself right-censored: a lower
bound on how many exist. Each design records which bounds apply to it.

**Duplex thermodynamics and conventional design rules.** Because a base count is a proxy for
discrimination and a free energy is the field's standard instrument for it, each design was also
scored thermodynamically. A junction gapmer is a perfect complement of the fusion across all 16
positions, while a parent transcript can pair only the half of the oligonucleotide it contributes,
so the comparison is the full 16-mer duplex against the donor-side and acceptor-side runs alone.
Nearest-neighbour enthalpies and entropies for a DNA:RNA hybrid were taken from Sugimoto and
colleagues,<sup>30</sup><!--PMID:7545436--> and ΔG°37 computed as ΔH° − TΔS°; the 250 nM strand concentration enters only the
melting temperature used to check the arithmetic against an independent implementation, which agreed
exactly. That check verifies the summation, not the choice of strand, which is fixed by the table's
documented convention that the sequence supplied is the RNA one. These designs carry LNA wings and the table is for an unmodified
hybrid, so what is computed is the duplex the DNA backbone would form. Because the seam lies inside
the gap, each parent pairs exactly one of the two five-nucleotide LNA wings while the fusion pairs
both, so LNA should widen this margin rather than narrow it and the value reported is a conservative
floor. That direction follows from the architecture and was not computed: no LNA parameters were
applied. Separately, every design was audited against four
conventional antisense design rules (GC within 40–60%, no G-quadruplex motif, no homopolymer run of
four, and no CpG dinucleotide), not to grade the designs, but to ask whether conventional triage and
the gap-level margin would select the same molecules.

**Availability.** All code, graded artefacts and per-design tables are released under a single
archived version, deposited from the public repository at
`github.com/trimcrae/Rare-cancers` [ARCHIVE DOI]. Every result reported here is re-derived from the
committed artefacts in that archive without network access or credentials. Regenerating the specificity screens from
scratch is not offline, because the gap-resolved arm queries NCBI BLAST and the exhaustive arm
downloads the GRCh38.p14 RefSeq RNA set. No reported number requires it, because each screen's hit set is
archived and the re-scores hold that hit set fixed. The pre-mRNA and mature-parent screens are fully
offline against the archive: the retrieved unspliced sequence and exon coordinates travel with it.

## 3 · Results

### 3.1 · Frame compatibility as the bound on junction space

Grading all 231 donor-exon × acceptor-exon pairs across the five partners returns 38 frame-compatible
junctions (Table 1, Figure 1). The refusals are structural: *NR4A3* exon 2 carries no
coding sequence and is refused in every pair, and an exon-4 acceptor would delete the *NR4A3*
DNA-binding domain that every reported EMC chimera retains, so all variance sits in the exon-3 column. Within that column,
frame compatibility reduces to a single arithmetic condition — a donor coding phase of 1 — which is
necessary and sufficient across its 77 rows, and necessary but not sufficient across all 231.

Among these, *EWSR1* exon 12 joined to *NR4A3* exon 3 is the junction reported most often — type 1
in 10 of the 15 *EWSR1*-rearranged tumours of an 18-case series<sup>31</sup><!--PMID:12378528--> — so
designs at this seam correspond to the largest documented patient group.

No design at any of the 38 junctions is a perfect complement of any of the six parent transcripts, a
test that excluded none of the 190 because a seam-spanning window cannot occur intact in a parent. GC
runs 25.0–75.0% across partners, with 132 of the 190 inside the conventional 40–60% band. Finding
candidate sequences is therefore not the constraint on this modality in this disease.

### 3.2 · Cross-partner coverage by a single oligonucleotide

Nine designs span the seam of more than one junction exactly, and all nine draw from *EWSR1*, *TAF15*
and *FUS* (Figure 2). Five cover the same three-partner set, differing only in register across the
seam. The best by gap-level margin is 5′-GGGCATATCATCAAAC-3′ (43.8% GC, gap-level margin 3), which
divides eight donor and eight acceptor bases at the seam of *EWSR1* exon 12, *TAF15* exon 11 and
*FUS* exon 10 joined to *NR4A3* exon 3, and occurs in none of the six wild-type parent transcripts.
The basis is sequence identity: the three donors are identical over the ten bases immediately 5′ of
their breakpoints, diverging at the eleventh. No design draws more than ten donor bases, which is
what makes the coverage arithmetically possible.

In one respect the published data contradict the clinical reading of this result. The only
exon-resolved *TAF15::NR4A3* breakpoints reported in EMC are exon 6: the primary report of
the variant fusion places the breakpoint at *TAF15* exon 6,<sup>32</sup><!--PMID:10537274--> and in a
series of 18 EMCs all three *TAF15*-rearranged tumours carried exon 6 joined to *NR4A3* exon
3<sup>31</sup><!--PMID:12378528--> — not exon 11. The exon-6 seam shares a single donor base with the exon-11 seam, so this oligonucleotide cannot
engage the *TAF15* junction that patients are reported to carry. That junction is itself
frame-compatible and yields five fusion-specific designs (43.8–50.0% GC), all five screened and
orientation-filtered — and every one of them retains a hybridisable gap-spanning near-match, four
loci at best and seven for the design its gap-level margin ranks first, five of those seven annotated
only as predicted gene models (Table 2). Two of the five nonetheless return no exact and no
single-mismatch match on the exhaustive scan. So the one *TAF15* seam with a published breakpoint is
designable and is not among the cleaner junctions, while the seam the multi-partner result rests on
has no reported patient. For *FUS* no exon-resolved EMC breakpoint has been published at all.
The three-partner result is therefore a statement about FET-family sequence architecture and a
hypothesis about junctions not yet observed; it is not a claim that one reagent serves three patient
groups. Testing it requires breakpoint sequencing of archival *TAF15*- and *FUS*-positive cases.

### 3.3 · The non-FET partners: coverage and specificity

*TCF12* and *TFG* are the partners in this panel that are not FET-family proteins, and neither
appears in any of the nine multi-partner sets: all nine draw only on *EWSR1*, *TAF15* and *FUS*.
*TCF12* reaches multi-partner coverage only under a relaxed criterion that tolerates mismatches in
the oligonucleotide wings. The check had little power to fail: any non-homologous donor would be excluded, so it does not
separate FET paralogy from incidental exon homology. The stronger evidence for paralogy is that four
additional two-partner sets are also FET-only.

Specificity does not sort by partner. Taking at each junction the lowest count any of its designs
achieves after the orientation filter, every one of the five partners has at least one
junction whose best design carries no hybridisable gap-spanning near-match: three of eight at both
*TCF12* and *FUS*, two of eight at *EWSR1*, one of eight at *TAF15* and one of six at *TFG*. The
minima therefore separate junctions rather than partners, and which exon a fusion breaks at matters
more for specificity than which gene it breaks into.

The same tension the *TAF15* result carries applies to *TCF12*, and in the same direction. The one
published *TCF12::NR4A3* breakpoint reports a chimera retaining the first 108 TCF12
residues,<sup>5</sup><!--PMID:11156374--> which in this transcript model is *TCF12* exon 5 and no
other exon. That junction is frame-compatible and designable, and it carries the highest
gap-spanning near-match load in the panel: 17 loci for its best-margin design, 12 of them predicted
gene models (Table 2). None of the four *TCF12* designs with no hybridisable near-match is at that
exon. So for *TCF12* as for *TAF15*, the seam a patient is reported to carry is designable and
dirty, while the clean seams have no reported patient — an inference from a residue count against
this transcript model, not an exon reported as such.

### 3.4 · Strand orientation reorders the junctions

All 38 frame-compatible junctions were screened with orientation parsed and filtered, 183 designs
across them, twenty-two of them screened or re-screened after alignment strand was parsed.

Across the retained hit lists, 44% of apparent gap-spanning risks are minus-strand (738 of
1,677). The proportion is not uniform: it runs from 0% at *TFG* exon 4, where no apparent risk is
minus-strand, to 100% at both *EWSR1* exon 1 and *TCF12* exon 7, where every one is. A
uniform inflation would rescale every junction and leave their ordering intact, whereas this filter
reorders them — *EWSR1* exons 7 and 13 return 55 and 57 apparent gap-spanning hits respectively, and
after filtering they stand at 6 and 53.

### 3.5 · Designs with no hybridisable near-match, at two search depths

After filtering, nine designs at six junctions carry no hybridisable near-match among non-parent
transcripts (Table 3), spanning four of the five partners: three at *EWSR1* exon 1
(5′-GGGCATATCCGTGGAC-3′, 5′-GGCATATCCGTGGACG-3′, 5′-GCATATCCGTGGACGC-3′), one at *FUS* exon 8
(5′-AGGGCATATCGGAGTC-3′), one at *TAF15* exon 1 (5′-GGGCATATCCGACATG-3′), and four at *TCF12* —
5′-GGGCATATCTCTATAA-3′ at exon 17, 5′-CAGGGCATATCTTGCA-3′ at exon 9, and
5′-GGCATATCAAGCGCTG-3′ and 5′-GCATATCAAGCGCTGC-3′ at exon 7. The exhaustive scan agrees
independently: each returns no exact and no single-mismatch match anywhere in 186,185 transcripts.
The two arms fail in different ways — one is a heuristic alignment search over both strands, the
other an exhaustive substitution scan over the sense orientation only — so their agreement is not a
restatement. A third screen, over the compartment neither of those two can reach, does not overturn
them either: none of the nine has a hybridisable site in parent pre-mRNA (§3.8).

The graded re-score agrees, with one instructive exception. Scoring every retained hit by the
residual cleavage a gap-internal mismatch is predicted to permit, under both literature bounds,
returns a residual
load of zero for all nine — and for one further design, at *FUS* exon 11, which is
not counted as clean here. That design returns 21 near-matches of which only 15 are retained, and
all 15 are minus-strand; the graded score therefore sees nothing hybridisable to score, while the
cleanliness criterion refuses it because the six unretained hits are unknown. The graded model has no
censoring guard, so it can award a zero the hit list does not support, and the stricter count is the
one reported. A zero for the nine is arithmetic rather than an independent measurement: it follows
from their having no hybridisable hit to score.

All six junctions were then re-screened at a tenfold deeper alignment ceiling, with retention raised
to match it so that every hit list is complete, and the result withdraws most of the set above. Only
three of the nine still carry no hybridisable near-match: 5′-AGGGCATATCGGAGTC-3′ at *FUS* exon 8,
5′-GGGCATATCCGACATG-3′ at *TAF15* exon 1 and 5′-GGCATATCAAGCGCTG-3′ at *TCF12* exon 7, each of which
returned the same count at both depths. The other six did not. The three *EWSR1* exon-1 designs had
returned no near-match at all at the default ceiling and return 27, 29 and 84; 5′-GGGCATATCTCTATAA-3′
at *TCF12* exon 17 goes from 8 to 118, and 5′-CAGGGCATATCTTGCA-3′ at *TCF12* exon 9 from 7 to 67.
Three of the six carry hits that span the catalytic gap and so are cleavage risks rather than merely
hybridisable: 64 for 5′-GCATATCCGTGGACGC-3′, 14 for 5′-GGGCATATCTCTATAA-3′ and 11 for
5′-CAGGGCATATCTTGCA-3′. A count of zero at the default ceiling was not a count of zero, which is the
sharpest form of the bound §3.6 sets out. The deeper counts are reported here as their own
measurement and no figure quoted above is restated from them.

The orientation call is corroborated independently of any of this. Ten designs return perfect
16/16 BLAST matches while the sense-only exhaustive scan reports no exact match. Both results can
only be correct if every one of those BLAST hits is on the minus strand, and every one is.

### 3.6 · Chance expectation and the two censoring bounds

A chance argument bounds how surprising a low count should be, and it points the other way from the
reading these numbers first invite. There are 1,129 16-mers within two substitutions of any given 16-mer, so an arbitrary
transcriptome position matches at ≥14/16 with probability 2.6 × 10⁻⁷; over an assumed RefSeq RNA
span of 3 × 10⁸–8 × 10⁸ nucleotides (assumed, because the screens record transcripts scanned rather
than nucleotides) that predicts 79–210 near-matches for any 16-mer whatever, on one strand. The BLAST arm cannot test this: its hit list is capped at 50, below
the null's lower bound of 79 for one strand and 158 for the two the search covers, so any
design must return fewer whatever the transcriptome contains. The exhaustive arm can test it, being
complete for substitutions by construction, and it comes in at chance rather than below it. The band
is an expected count, and the observed mean over the 176 distinct oligonucleotides is 9.2 against
3.4–9.1 predicted; the median is 3, which is what the low end of the band predicts for a count of
this kind. Real transcript sequence therefore produces a long right tail an independent-uniform-base
model cannot, reaching 100 matches, rather than a uniform shift below the band.

Two bounds remain on these counts and neither is corrected for. The BLAST arm returns at most 50
hits per query, and 35 of the 183 filtered designs reach that cap; a further 101 exceed the 15 hits
retained per design, so 136 in all carry right-censored counts. The nine clean designs return zero to
eight raw hits each, and that is not a measurement either. Re-screening
23 designs at a tenfold deeper ceiling raised every one of their counts, and 20 of the 23 had not
approached the 50-hit cap: one reporting 9 near-matches returned 34, one reporting 10 returned 110,
and one reporting 15, a count the pipeline treats as a complete list, returned 204. Every
alignment count taken at the default ceiling is therefore a lower bound whether or not it reached
the cap. Reaching the cap is not what censors a count, and a count of zero is not exempt: §3.5
reports three designs that returned no near-match at this depth and 27, 29 and 84 at ten times it.

Retention is a second and separate bound, and the restriction it imposes was tested rather than
assumed. Seven design-and-junction records in the filtered corpus have no hybridisable hit among
those retained and a raw count above the retention depth, so retention alone withholds a verdict on
them. Re-screening their five junctions at a tenfold deeper ceiling, with retention raised to match
it, decided six of
the seven, and every one of the six is not clean. The counts they had been reporting were severely
censored: 21 raw near-matches became 161 with 5 hybridisable, 23 became 68 with 48, 27 became 65 with
5, 35 became 78 with 10, and 47 became 196 with 119, the last at both junctions that sequence spans.
The seventh re-screen did not return and that record remains undecided. Relaxing the censoring
restriction would therefore have promoted at least six records that a deeper look shows carry
hybridisable near-matches, one of them 119 of them, and the nine are unchanged by the test.

### 3.7 · Transcript records versus gene loci

These are counts of transcript records, not of genes, and the distinction cuts in the candidate's
favour. RefSeq carries one accession per annotated variant, so a match to a
constitutive exon of a multi-variant gene is counted once per variant. Recounting every screened hit
list per gene locus, over the 44 designs of the 38 junction screens whose lists are neither truncated
nor missing a locus recount, gives a median
inflation of 2.20 transcript records per locus and a maximum of 11.0 — that is, a typical near-match count
overstates the number of distinct genes involved by rather more than twofold. The distinction also
separates observed from predicted sequence: RefSeq `NM_`/`NR_` records are curated, whereas
`XM_`/`XR_` are computationally predicted gene models, so a design whose load sits entirely in the
predicted namespace carries a different kind of liability from one that matches curated transcripts.
For the multi-partner candidate 5′-GGGCATATCATCAAAC-3′ both effects apply and compound with the
orientation filter. Of its nine near-matches, six are hybridisable and five of those are
gap-spanning — and all five are variants of a single uncharacterised locus, LOC105374140, annotated
only as predicted `XR_` models. One gap-spanning locus from a raw count of nine, but not one clean of
curated sequence: the sixth hybridisable near-match is *H2AP* (NM_012274), whose single mismatch
falls inside the catalytic gap and which the pessimistic bound therefore counts in full. The same
design returns no exact match and a single ≤1-mismatch match on the exhaustive scan.

### 3.8 · Two parent liability classes outside the transcript screens

RNase-H1 is active in the nucleus and gapmers engage pre-mRNA, so a screen over mature transcripts
cannot see intronic or intron–exon-spanning sites. That omission is not neutral in its direction: a
junction gapmer's two halves are both exonic, and in a parent pre-mRNA an exon is followed by an
intron rather than by the next exon, so parent pre-mRNA is precisely where a design's donor half sits
beside sequence no mature screen has compared it against. A mature-only screen therefore returns a
low count partly by construction.

Unspliced sequence for all six parent transcripts was retrieved and every design's target window
scanned against it exhaustively at the same ≤2-mismatch threshold the alignment screen uses, both
orientations, with the same gap resolution and the same orientation filter. Of 190 designs, 53 have a
near-match somewhere in parent pre-mRNA and 19 carry one that is hybridisable, pairs the catalytic gap
in full, and touches intronic sequence, the last condition being what makes it invisible to both
transcript screens rather than a re-count of something already reported.

Those 19 sites fall into two classes that do not mix, and only one of them is mechanistically
interesting. Nine are intron–exon-spanning and every one is in *NR4A3*, at the same place: six or
seven nucleotides into intron 2, spanning the boundary into exon 3. That follows from the design problem. A junction gapmer's acceptor half is the 5′ end of
*NR4A3* exon 3, and the wild-type *NR4A3* transcript reaches that same exon across its own splice
junction — so a design whose donor half also matches the 3′ end of intron 2 within the mismatch budget
pairs across the real splice site. It is a route to wild-type *NR4A3* engagement that does not pass
through the fusion at all, in the compartment where RNase-H1 is active, and it is the discrimination
question this paper is about. The other ten are wholly intronic and every one is in *TCF12*, which
contributes 365,096 of the 517,157 intronic nucleotides searched: 71% of the search space for 100% of
that class, which is what sequence volume alone predicts and should not be read as anything about
*TCF12*.

The liability tracks the tiling register, of which the gap-level margin is a function: of the designs
at margin 1, 12 of 76 carry a pre-mRNA site; at margin 2, 7 of 76; at margin 3, none of 38, and eight
of the nine *NR4A3* boundary sites are at the shortest donor-side register, which needs the fewest
intronic bases to match. None of the nine designs with no hybridisable near-match on either transcript
screen carries one.

The second class is in mature parent transcript, and it is larger. The alignment screen excludes
parent records by design and filters at ≥14/16 identity, the exhaustive scan admits ≤1 mismatch, and
the pre-mRNA arm searches unspliced sequence and so cannot reach a mature exon–exon junction — so a
parent duplex of 11 or 12 contiguous base pairs that pairs the whole catalytic gap is invisible to
all three while being what RNase-H1 requires. Comparing every design's target window to every window
of all six mature parents, 87 of 190 designs have one of at least ten base pairs, and 61 of those 87
are against wild-type *NR4A3* — the transcript this modality must spare, with a 62nd pairing *NR4A3*
at eleven base pairs but another parent at twelve, so that it is attributed elsewhere. It falls steeply with the
gap-level margin, from 50 of 76 designs at margin 1 through 29 of 76 at margin 2 to 8 of 38 at margin
3, which is what the margin's definition predicts: at margin 1 a parent needs one lucky base to pair
the whole gap and at margin 3 it needs three. Five of the nine designs of §3.5 carry such
a duplex, at 11 or 12 base pairs — including 5′-CAGGGCATATCTTGCA-3′, against wild-type *NR4A3*
itself. The margin is a predictor of
parent engagement rather than a guarantee against it, because it counts bases unique to the fusion at
the seam without asking whether a parent carries them elsewhere.

Composing this with the deeper re-screen of §3.5 leaves two candidates in the whole panel:
5′-AGGGCATATCGGAGTC-3′ at *FUS* exon 8 and 5′-GGGCATATCCGACATG-3′ at *TAF15* exon 1, which carry no
hybridisable near-match at ten times the default search depth, no single-mismatch match on the
exhaustive scan, no pre-mRNA site and no mature-parent duplex. Neither depends on the ten-base-pair
threshold: no window of any parent pairs their catalytic gap at any length, so their longest run is
zero rather than merely short. That is the honest size of the
candidate set, and neither junction has a published patient breakpoint — the exon-resolved *TAF15*
breakpoints reported in EMC are exon 6, and for *FUS* none has been published at all.

Both classes were bounded the same way — exhaustive over six parent transcripts and silent about
every other gene — so a fifth screen removed that bound. Every distinct target window and its
reverse complement was tested against every position of GRCh38 in both orientations at the same
≤2-mismatch threshold, exhaustively: 2,948,609,696 windows scanned over a measured 3.10 × 10⁹
nucleotides, with no seed, no word size and therefore no search sensitivity to quantify.

A raw genome-wide count is not a result at this threshold. Chance alone predicts of order 10³
near-matches per 16-mer over a genome for any 16-mer whatever, so the informative readings are
stratified. Exact 16/16 matches are the class where chance expectation is of order one: 1.37 expected
per design against 236 observed across 176 windows, which is at chance. Load relative to that
expectation separates designs where a total cannot — the median design sits at 0.98 of its
expectation and 14 of 176 exceed twice it. And the repeat split, free from a soft-masked reference,
shows 52.5% of hits fully repeat-masked against a genome that is 51.4% masked, so the load is not
repeat-driven.

The decisive reading is a lookup rather than a count: does any design have a gap-paired,
strand-agreeing site in *NR4A3*, in a parent gene, or in an *NR4A* paralogue anywhere in the genome?
Twenty of 176 do. Neither of the two designs that survive every other screen is among them, and both
carry a load well below chance — 0.33 and 0.24 of expectation at ≤2 mismatches, and 0.06 and 0.04
for gap-paired sites, ranking 26th and 13th of 176. That is the strongest statement this work can
make about them, and it is a statement about predicted hybridisation and not about cleavage.

### 3.9 · Duplex thermodynamics and conventional design rules

Scored as free energies, every one of the 190 fusion-specific designs favours the fusion duplex over
the best duplex either parent can form, by 4.8 to 13.1 kcal/mol with a median of 9.6. The denominator
here is 190 rather than the 183 of the specificity screens because a free energy needs only a
sequence, whereas a screen needs a BLAST query that returned, and seven of the 190 failed at the
remote service. The 190 records are 176 distinct molecules, because nine of the 16-mers meet more than
one partner's seam and are recorded once per seam. Every design favours the fusion because a parent
pairs roughly half the oligonucleotide, and half a duplex is much the weaker one. That separates two
things a base count conflates. Discrimination at the level of *binding* is not marginal here and is not what constrains
the modality; what remains unresolved is discrimination at the level of *catalysis*, where RNase-H1
requires a paired DNA gap and where the literature bounds span one- to five-fold. The thermodynamic
result therefore narrows the paper's central uncertainty rather than relieving it.

The two rankings agree in direction. Grouping designs by the gap-level margin the Methods define,
mean ΔΔG°37 rises monotonically with it, from 8.3 kcal/mol at margin 1 to 9.9 at margin 2 and 10.7
at margin 3. That agreement is arithmetic rather than corroboration: the longest run either parent
can pair is exactly 11 minus the gap-level margin for all 190 designs, so the free energy is ordering
the same quantity in kilocalories. What it adds is the size of the difference, not an independent
ranking, and the same caution applies to the margin's agreement with the parent screens of §3.8.

Conventional design rules select differently, and against the paper's own candidates. Of the 190
designs, 106 satisfy all four rules; the rules bind at different rates, with every design free of a
G-quadruplex motif but 13 carrying a homopolymer run of four, 43 a CpG dinucleotide and 58
falling outside the 40–60% GC window. The failures overlap, so they do not sum to the 84 designs
that fail at least one.
The disagreement is sharpest exactly where it matters most. Of the nine designs with no hybridisable
near-match (Table 3), exactly one satisfies all four rules. Seven contain a CpG dinucleotide, the
canonical TLR9 immunostimulatory motif, which in practice is neutralised by 5-methylcytosine
substitution rather than by changing the sequence; four fall outside the 40–60% GC window — the three *EWSR1* exon-1 designs above
it at 62.5% and 5′-GGGCATATCTCTATAA-3′ below it at 37.5%. Only 5′-CAGGGCATATCTTGCA-3′ at *TCF12*
exon 9 passes every rule, and the multi-partner candidate 5′-GGGCATATCATCAAAC-3′, which is not among
the nine, also passes all four. So the two filters disagree where it matters: the cleanest
designs this work found are, with one exception, molecules conventional triage would flag, in six of
the seven cases for a CpG a base substitution removes. Both are reported rather than composed into a
single score.

## 4 · Discussion

Designability is not the constraint: junction-spanning designs exist at every frame-compatible NR4A3
fusion junction, and specificity does not
sort by partner — with all 38 junctions screened, every one of the five partners has a junction whose
best design carries no hybridisable gap-spanning near-match, so it is the exon a fusion breaks at,
not the gene it breaks into, that predicts a clean design.

Clean designs are much scarcer than the default search depth implies, and two independent findings
converge on that. Of the nine designs with no hybridisable near-match at that depth, six lose the
property at ten times it, three of them having reported no near-match at all before; and five form an
eleven- or twelve-base-pair duplex with a mature wild-type parent that pairs the whole catalytic gap,
one of them with *NR4A3* itself, where no screen filtering on global identity can see it. Two designs
survive every screen applied here — at *FUS* exon 8 and *TAF15* exon 1, neither a junction any patient
is reported to carry. That is the honest size of the candidate set, and it is a floor rather than a
total until the same depth is applied everywhere — which it now has been, for all 38 junctions
and 187 design records, with no hit list truncated. Those counts are reported as their own
measurement and are not folded into the default-depth figures above.

The limiting step is discrimination between the fusion and its parents, and it is not resolved here.
Both cited bounds are measured against a single substitution in an otherwise fully paired duplex, so
neither transfers to a parent that leaves half the oligonucleotide unpaired and the catalytic gap
only partly so: they bound the near-match case, and no retrieved measurement bounds the parent case.
The two parent compartments of §3.8 sharpen that rather than softening it. For nine designs the
route to wild-type *NR4A3* is not a gap-level discrimination problem at all: they pair the catalytic
gap in full across the wild-type intron-2/exon-3 boundary, at two mismatches that both fall in the
LNA wing, and the compartment in which that duplex would form is the nuclear one
RNase-H1 occupies. For 87 the same is true in mature parent sequence. The general point is that a
fusion-junction design's most plausible wild-type liability is its own parent, reached either across
a splice junction or in the mature transcript, and both are invisible to a screen that ranks
candidates by global identity. Free-energy calculation does not narrow the interval either: every
design discriminates amply at the level of duplex formation, so what is unresolved is specifically
the catalytic step, not the binding one. Two things could narrow that interval and no further
sequence analysis is either of them: a measurement, or a physics-based estimate of cleavage geometry
on the RNase-H1·heteroduplex complex, for which experimental structures exist. Neither is attempted
here. The field's own
answer to poor single-base discrimination has been positional chemical modification of the gap rather
than length,<sup>26</sup><!--PMID:23963702--> and that is the design direction this result points to. A steric-block
mechanism, which does not require gap-level discrimination, is a second alternative this work does not
evaluate.

Delivery remains unsolved for a tumour, and separates into three routes with different
requirements. A characterised EMC-enriched surface antigen is a prerequisite of
the systemic receptor-targeted route only; local and inhaled administration require none. EMC's
distant spread is lung-dominant, at 35–45% of patients and a median of approximately 28 months to
metastasis,<sup>6</sup><!--PMID:41055792--> and inhaled oligonucleotides have reached human dosing in non-oncology
indications, including an inhaled antisense oligonucleotide dosed in healthy volunteers in phase 1<sup>33</sup><!--PMID:39500647--> — a
splice-switching oligonucleotide rather than an RNase-H1-active gapmer, so it establishes the route
and not the mechanism used here — and an inhaled
siRNA in phase 2b–3 in patients.<sup>34</sup><!--PMID:40028836--> Those agents target airway epithelium or parenchyma, which is the
compartment inhalation naturally reaches; a hypocellular, matrix-rich parenchymal sarcoma nodule is
not. Inhaled delivery to lung tumours is an active preclinical field — 68 records in the retrieval
corpus behind this section — but only two of those carry clinical-stage language and neither is a
trial, so the route is established in humans and not for this target.

The experiment that would resolve the central uncertainty is routine and has been published in an
analogous disease: fusion-specific antisense oligonucleotides against *NAB2::STAT6* in solitary
fibrous tumour, evaluated against CRISPR-engineered isogenic fusion-positive and fusion-negative
cells, reduced fusion expression by 58% and proliferation by 22% in vitro.<sup>35</sup><!--PMID:37370737--> Applied here,
5′-GGGCATATCATCAAAC-3′ remains the single highest-information reagent, because one synthesis tests
the mechanism at the most commonly reported junction and, against a synthetic target only, the
multi-partner prediction; its predicted load — five gap-spanning
near-matches at one uncharacterised locus, a sixth hybridisable near-match on curated *H2AP*, and a
single ≤1-mismatch transcriptome match (§3.7) —
should travel with it, and it has not been re-screened at the deeper ceiling. If the object is
instead the cleanest available test of the mechanism alone, the candidates are
5′-AGGGCATATCGGAGTC-3′ at *FUS* exon 8 and 5′-GGGCATATCCGACATG-3′ at *TAF15* exon 1, the two designs
that survive every screen including the deeper one, at the
cost of addressing junctions no patient is reported to carry. 5′-GGGCATATCTCTATAA-3′ at *TCF12* exon
17, which an earlier draft of this work put forward for that role, is not a candidate: at ten times
the default search depth it carries 101 hybridisable near-matches, 14 of them spanning the catalytic
gap.

Transferability depends on how that experiment is set up. The breakpoint of the cell line or patient sample must be established
at nucleotide resolution by RNA sequencing before any oligonucleotide is ordered: every design here
is specific to one exon pair, and none is valid for an unverified junction. Three controls are
required, and a knockdown assay alone distinguishes none of them: a positive
control gapmer against an abundant housekeeping transcript in the same cells, to separate
failed delivery from failed discrimination; a scrambled gapmer of matched chemistry, to separate
sequence-specific cleavage from the non-specific toxicity of this chemistry; and a fusion-negative
isogenic comparator, since wild-type *NR4A3* may be too weakly expressed in an EMC line for the
selectivity readout to be defined at all. The decision threshold should be fixed before
the experiment. The informative readout is fusion knockdown measured against wild-type *NR4A3*
knockdown in the same well; a selectivity below the approximately five-fold bound cited above would
falsify the gap-margin ranking on which every candidate here is ordered.

**Limitations.** The cleanliness claim is bounded by what each screen can see, and the deeper
re-screen shows how tight that bound is. The alignment screen
returned hit lists for 183 filtered designs. Only 47 of those 183 are short enough to be assessed for
cleanliness at all, so nine
clean designs is a floor over that subset and not a total. It is also an over-count: six of the nine
lost the property at ten times the default search depth. Across all 38 junctions re-screened at
that depth, 141 of 157 comparable designs return a higher count and 125 of those had not reached the
50-hit cap, so the default-depth figures throughout should be read as lower bounds rather than as
counts. BLAST is also heuristic and its sensitivity at the ≥14/16 threshold is unquantified
here, so "no hybridisable near-match" is a property of this search rather than of the transcriptome;
the exhaustive ≤1-mismatch scan carries no such qualification and is the arm the claim rests on. All 38 frame-compatible junctions are screened
with the orientation filter applied, so no junction here carries an unfiltered count. The chance null is crude:
it assumes independent uniform bases, where real transcript sequence is composition-skewed and
repetitive, so it separates "more than chance" from "at chance" and nothing finer. Which exon pair a
given patient carries is not decidable from exon structure, so the multi-partner result is
conditional on *TAF15* and *FUS* breakpoints falling at the homologous exons — a clinical fact not
established here — and the *TCF12* exon assignment of §3.3 is inferred from a reported residue count
against this transcript model rather than reported as an exon. The five partners modelled here are
not the full catalogue: *ACTB*<sup>3</sup><!--PMID:41755350--> and others are reported, and 2% of one
cohort carried no identified partner.<sup>9</sup><!--PMID:36948401--> One architecture was tiled, a
16-mer 5-6-5, so nothing here bounds what a longer catalytic gap would achieve at the same seams. The
thermodynamic calculation models an unmodified DNA:RNA hybrid and speaks to duplex formation rather
than to cleavage. All five screens address hybridisation-dependent liability only; the
sequence-independent class of a phosphorothioate LNA gapmer, protein binding and the
target-independent hepatotoxicity of this chemistry, is not a function of any feature graded here.
The genome scan removes the six-transcript bound the parent screens carried, at the cost of two of
its own: `hybridisable` is measured against an annotation, so a site in unannotated transcription is
reported as intergenic and not counted, and a screen against one assembly says nothing about a
patient's private variation. An earlier genome-wide attempt against a mixed public corpus returned
nothing interpretable and is released with the artefacts; it could not have done otherwise, having
no defined nucleotide span to form a null against. Every exhaustive arm inherits the
substitution-only bound: all are complete for mismatches by construction and blind to insertions and deletions.

## Tables

Tables 1 to 3 are in `fusion-junction-aso-submission-tables.md`, generated from the released
artefacts so that a cell and its source cannot diverge.

## Figure legends

**Figure 1. Frame compatibility across the NR4A3 fusion junction space.** All 231 donor-exon ×
acceptor-exon pairs across *EWSR1*, *TAF15*, *TCF12*, *FUS* and *TFG*, graded against the frame
condition.
Rows are donor exons grouped by partner; columns are *NR4A3* acceptor exons. Two acceptor columns
are refused in every pair for structural reasons, so the 38 frame-compatible junctions lie in a
single column.

**Figure 2. One 16-mer spans three partners' breakpoints.** The seam windows of *EWSR1* exon
12, *TAF15* exon 11 and *FUS* exon 10 joined to *NR4A3* exon 3, aligned at the breakpoint. Blue,
donor exon; green, acceptor exon; positions at which the three donors differ are boxed as well as
coloured, for greyscale and colour-blind readers. The shaded box is
the target window of 5′-GGGCATATCATCAAAC-3′, with the 5-6-5 gapmer architecture below it and its
gap-level margin of three alongside. The three
donors are identical over the ten nucleotides before the breakpoint, which is what makes one
oligonucleotide junction-spanning at all three seams.
Coverage is predicted from sequence and has not been measured.

**Figure 3. Transcriptome load per design against chance expectation.** Each bar is one distinct
oligonucleotide's count of exact plus ≤1-mismatch matches over 186,185 transcripts, ranked. The 190
design records at real exon junctions collapse to 176 molecules, because nine of the 16-mers are
junction-spanning at more than one partner's seam at once — five at three seams and four at two — and
each of those is one physical oligonucleotide, plotted once rather than repeatedly (marked). The band
is the number of such matches expected for an arbitrary 16-mer under an independent-uniform-base null
(3.4–9.1); 125 of the 176 fall at or below its upper bound and 51 exceed it. Ten further designs from
modelled breakpoints not built from a spliced transcript model are excluded, and are released with
the artefacts. The band is an expected count: the observed mean is 9.2, at its upper end, while the
median is 3 at its lower end, so real transcript sequence produces a long right tail the null cannot
rather than a uniform shift away from it. The band
separates "more than chance" from "at chance" and is not a significance test; the counts are
predictions from sequence search, not measured off-target activity.

## Declarations

**Data and code availability.** [ARCHIVE DOI], deposited from `github.com/trimcrae/Rare-cancers`.
A manifest listing every archived file with its SHA-256 travels with the deposit. Artefacts include the graded junction
atlas, per-junction design panels, all five screens, the graded re-scores under
both discrimination bounds, and the retrieval records for every literature claim.

**Provenance and corrections.** An earlier version of these analyses placed the acceptor seam
incorrectly through a coding-versus-transcript exon indexing error and was withdrawn in full; all
panels were rebuilt and verified against two independent transcript acquisitions. The complete
correction record, including every superseded value, is released with the archive.

**Competing interests.** The author declares no financial competing interests: he holds no
position, equity, consultancy or patent relating to any gene, sequence or agent named here, and no
oligonucleotide described in this manuscript has been synthesised, licensed or offered for sale. One
non-financial interest is declared: the author is a survivor of extraskeletal myxoid chondrosarcoma,
the disease this work addresses.

**Funding.** This work received no external funding and was self-funded by the author. No grant,
institution, company or charity supported it, and no funder had any role in the design of the
analyses, the interpretation of the results, or the decision to publish.

**Ethics.** No human subjects, human material or animals were involved. All clinical figures are
taken from published aggregate data and are cited.

**Use of AI tools.** A large language model (Claude, Anthropic) was used throughout this work: to
write the analysis code, to run the graded design and screening pipelines, to draft and revise this
manuscript, and to conduct internal critical review of earlier drafts. Every quantitative statement
here is produced by code in the released archive and is reproducible from it; no numerical result
was generated by a language model directly. Every literature identifier was checked against a
retrieved bibliographic record, and identifiers that could not be so anchored were removed rather
than retained. The author takes full responsibility for the content, including for the correctness
of the code and for the interpretation of the results.

## References

*The numbered entries are listed in `fusion-junction-aso-submission-references.md`, generated
from retrieved bibliographic records. Each superscript above carries its PubMed identifier in a
non-rendering comment, and the numbering is assigned from those identifiers by order of first
citation, so a superscript and its reference cannot drift apart.*
