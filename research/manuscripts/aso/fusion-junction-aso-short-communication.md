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
rearrangement of *NR4A3* to a variable 5′ partner. Its chimeric mRNA carries a breakpoint seam absent
from every normal transcript, its one tumour-exclusive RNA feature; a structured search retrieved no
junction-directed oligonucleotide against any NR4A3 fusion.

**Methods.** Chimeras were built at the mRNA level from canonical Ensembl models, acceptor exon
retained whole, and every donor-exon × acceptor-exon pair across five partners graded.
Junction-spanning 16-mer 5-6-5 LNA/DNA/LNA gapmers were tiled over each frame-compatible seam and
screened against all six parent transcripts, against RefSeq RNA by gap-resolved BLAST, exhaustively
for ≤1 mismatch over 186,185 transcripts, and — because RNase-H1 acts in the nucleus — unspliced and
against all of GRCh38 in both orientations. Two longer geometries, 5-8-5 and 5-10-5 at the
same wing, were tiled and screened over those seams.

**Results.** Of 231 graded pairs, 38 are frame-compatible, all yielding a gapmer matching no
parent perfectly. All 38 were screened with alignment orientation filtered. Nine designs at six
junctions carry no hybridisable near-match among non-parent transcripts and no single-mismatch
match among 186,185 transcripts; that search is capped: re-screening ten times deeper leaves three. The parents are a liability no transcript screen reaches: 19 of 190 designs pair the catalytic
gap in parent pre-mRNA, 87 of 190 pair it in mature parent transcript inside a duplex of at least ten
base pairs, 61 of those against wild-type *NR4A3*, and an exhaustive GRCh38 scan finds such a site in
a parent gene or *NR4A* paralogue for 20 of 176. Three designs survive every screen, two at any parent-duplex
threshold, but at junctions no patient is reported to carry. Ranking within each junction returns a
usable design at both junctions with a published exon-resolved breakpoint, about 95% of confirmed
cases, and none at three where every design pairs a parent. One 16-mer spans three partners' seams
through ten identical donor bases, a sequence property, not a clinical one. A longer gap does not escape the parents: inside it the junction-unique bases and those a wild-type
parent pairs are complements summing to the gap, so across 798 designs at three geometries each
nucleotide of margin gained costs one of contiguous parent duplex. There a 5-10-5
design sheds all 123 of the 16-mer's gap-spanning transcript risks and lengthens the parent's run
from 3 to 5 nucleotides.

**Conclusions.** Designability does not limit junction gapmers here, but clean designs are far
scarcer than a capped search suggests, and it is the parents, not the transcriptome,
that consume them. The limiting step is fusion-versus-parent discrimination at the
catalytic gap, set by enzymology and chemistry, which no computation here resolves; gap length cannot
relieve it, the nucleotide that sharpens the fusion margin being the one that lengthens the parent
duplex.

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
seam. No claim is made that a short gap improves
fusion-versus-parent discrimination: one series that shortened a 5-10-5 gapmer to 5-6-5 reported
lower off-target knockdown but also lower on-target activity and lower allele
selectivity.<sup>22</sup><!--PMID:39126066--> Because that trade is the modality's central one, two
longer geometries were tiled over the same seams by the same rule and carried through the same
screens: 5-8-5 and 5-10-5, with the wing held at five nucleotides so that only the catalytic gap
changed. Holding the wing fixed is what makes the geometries comparable, since LNA affinity then
enters every parent duplex identically; §3.10 reports the comparison. Discrimination is set by the junction-unique bases inside
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

**Expression of the off-target loci.** No screen above says whether a matched gene is transcribed
where the drug goes. For the two junctions with a published exon-resolved breakpoint, the gene loci
their deeper screens return at the gap-paired class were read against GTEx v8 median TPM in two
blocks reported separately and never combined: liver and both kidney compartments, the organs a
systemically dosed phosphorothioate gapmer distributes to, and six soft-tissue types standing in for
the compartment EMC arises in, no atlas containing the tumour itself. NCBI Gene supplied locus
identity, so a locus with no reading is attributed rather than left blank; the Human Protein Atlas
was read as a transport check only, its consensus incorporating GTEx rather than confirming it
independently.

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
screens, and 39 of the 93 screens released in total, the exceptions being one coverage-only
control screen that records no gap-mismatch depth and so cannot be graded at all, and the 53 deeper
re-screens, which are released ungraded. The re-score counts
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
orientation-filtered — and every one of them retains a hybridisable gap-spanning near-match. At the
tenfold deeper ceiling, where every hit list is complete, those recount to three gene loci at best
and five for the design its gap-level margin ranks first, three of those five annotated only as
predicted gene models (Table 4). Two of the five nonetheless return no exact and no
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
other exon. That junction is frame-compatible and designable, and its best-margin design retains 17
gap-spanning near-matches at the deeper ceiling, every one of them a variant of a single curated
locus, *PIK3CG* (Table 4). None of the four *TCF12* designs with no hybridisable near-match is at that
exon. So for *TCF12* as for *TAF15*, the seam a patient is reported to carry is designable and is
not among the clean ones, while the clean seams have no reported patient — an inference from a
residue count against this transcript model, not an exon reported as such.

### 3.4 · Strand orientation reorders the junctions

All 38 frame-compatible junctions were screened with orientation parsed and filtered, 183 designs
across them.

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

Every junction was then re-screened at a tenfold deeper alignment ceiling, with retention raised
to match it so that every hit list is complete — 38 junctions and 187 design records, none truncated
— and the result withdraws most of the set above. The 187 are the panel's 190 less three that failed
at the remote service on this pass, two at *FUS* exon 5 and one at *TFG* exon 2; each had already
returned 23, 41 and 31 near-matches at the default depth, so none was a candidate and no count below
depends on them. Only
three of the nine still carry no hybridisable near-match: 5′-AGGGCATATCGGAGTC-3′ at *FUS* exon 8,
5′-GGGCATATCCGACATG-3′ at *TAF15* exon 1 and 5′-GGCATATCAAGCGCTG-3′ at *TCF12* exon 7, each of which
returned the same count at both depths. The other six did not. The three *EWSR1* exon-1 designs had
returned no near-match at all at the default ceiling and return 27, 29 and 84; 5′-GGGCATATCTCTATAA-3′
at *TCF12* exon 17 goes from 8 to 118, and 5′-CAGGGCATATCTTGCA-3′ at *TCF12* exon 9 from 7 to 67.
Three of the six carry hits that span the catalytic gap and so are cleavage risks rather than merely
hybridisable: 64 for 5′-GCATATCCGTGGACGC-3′, 14 for 5′-GGGCATATCTCTATAA-3′ and 11 for
5′-CAGGGCATATCTTGCA-3′. A count of zero at the default ceiling was not a count of zero, which is the
sharpest form of the bound §3.6 sets out.

The deeper pass also decided what the default one could not. Seven of the 190 designs had failed at
the remote service and carried no count at all; all seven returned at the deeper ceiling, six of them
dirty and one — 5′-GGGCATATCAAGCGCT-3′ at *TCF12* exon 7 — with three near-matches and none
hybridisable. So the set of designs with a complete hit list and no hybridisable near-match is four
at this depth rather than three: a design the shallower pass never screened joins the three that
survived it. The deeper counts are reported as their own
measurement and no figure quoted above is restated from them.

The orientation call is corroborated independently of any of this. Ten designs return perfect
16/16 BLAST matches while the sense-only exhaustive scan reports no exact match. Both results can
only be correct if every one of those BLAST hits is on the minus strand, and every one is.

### 3.6 · Chance expectation and the two censoring bounds

A chance argument bounds how surprising a low count should be, and it points the other way from the
reading these numbers first invite. There are 1,129 16-mers within two substitutions of any given 16-mer, so an arbitrary
transcriptome position matches at ≥14/16 with probability 2.6 × 10⁻⁷. The span that probability
multiplies is measured rather than assumed: the exhaustive scan counts 718,571,139 nucleotides across
its 186,185 transcripts, so the prediction is 189 near-matches for any 16-mer whatever on one strand,
a single figure rather than the range an assumed span would give. The BLAST arm cannot test this: its
hit list is capped at 50, far below 189 on one strand and 378 on the two the search covers, so any
design must return fewer whatever the transcriptome contains. The exhaustive arm can test it, being
complete for substitutions by construction, and it comes in at chance rather than below it. At the
≤1-mismatch threshold the same span predicts 8.2 per design, against an observed mean of 9.2 over the
176 distinct oligonucleotides, a ratio of 1.12, while the median is 3. Real transcript sequence
therefore produces a long right tail an independent-uniform-base
model cannot, reaching 100 matches, rather than a uniform shift away from the expectation.

Two bounds remain on these counts and neither is corrected for. The BLAST arm returns at most 50
hits per query, and 35 of the 183 filtered designs reach that cap; a further 101 exceed the 15 hits
retained per design, so 136 in all carry right-censored counts. The nine clean designs return zero to
eight raw hits each, and that is not a measurement either. Re-screening at a tenfold deeper ceiling
raised the count of 164 of the 180 designs screened at both depths, and 129 of those had not
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
inflation of 2.25 transcript records per locus and a maximum of 11.0 — that is, a typical near-match count
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

Re-screened at the tenfold deeper ceiling, that design returns 189 near-matches, 141 of them
hybridisable and gap-spanning, and 123 with the catalytic gap perfectly paired. Both effects above
apply at that depth and neither weakens. All 123 sit at 14 of 16 identity, the loosest match the
screen admits; they recount to six gene loci, of which *ANKS1B* and *ZNF667* supply 104 between
them; 82 of the 123 are `XM_`/`XR_` predicted models; and no parent transcript is among them. Depth
therefore raises the raw count roughly twentyfold and the distinct gap-spanning locus count from one
to six.

### 3.8 · Two parent liability classes outside the transcript screens

RNase-H1 is active in the nucleus and gapmers engage pre-mRNA, so a screen over mature transcripts
cannot see intronic or intron–exon-spanning sites. That omission is not neutral in its direction: a
junction gapmer's two halves are both exonic, and in a parent pre-mRNA an exon is followed by an
intron rather than by the next exon, so parent pre-mRNA is precisely where a design's donor half sits
beside sequence no mature screen has compared it against. A mature-only screen therefore returns a
low count partly by construction.

Of 190 designs, 53 have a
near-match somewhere in parent pre-mRNA and 19 carry one that is hybridisable, pairs the catalytic gap
in full, and touches intronic sequence, the last condition being what makes it invisible to both
transcript screens rather than a re-count of something already reported.

The step from 53 to 19 is a threshold rather than a measurement, and the class it removes is the one
the Methods decline to dismiss. Forty designs carry a hybridisable parent pre-mRNA site; the 19
counted here are those pairing the catalytic gap in full, and the remaining 21 pair all of it but
one or two positions — 26 of their 28 sites are a single gap mismatch short, and five are in
*NR4A3* itself. Under the bounds this work adopts a single mismatch inside the gap does not abolish
cleavage, so those 21 are not a null result; they are excluded because a graded count over this
compartment would need a discrimination model the literature does not supply for a parent duplex.
The same condition governs the mature-parent screen below, which considers only windows pairing the
whole gap. Every count in this section should be read as the fully-paired class and not as the whole
parent liability.

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
are against wild-type *NR4A3*, the transcript this modality must spare, with a 62nd pairing *NR4A3*
at eleven base pairs but another parent at twelve, so that it is attributed elsewhere. It falls steeply with the
gap-level margin, from 50 of 76 designs at margin 1 through 29 of 76 at margin 2 to 8 of 38 at margin
3, which is what the margin's definition predicts: at margin 1 a parent needs one lucky base to pair
the whole gap and at margin 3 it needs three. Five of the nine designs of §3.5 carry such
a duplex, at 11 or 12 base pairs — including 5′-CAGGGCATATCTTGCA-3′, against wild-type *NR4A3*
itself. The margin is a predictor of
parent engagement rather than a guarantee against it, because it counts bases unique to the fusion at
the seam without asking whether a parent carries them elsewhere.

Composing this with the deeper re-screen of §3.5 leaves three candidates in the whole panel, and
they are not equally secure. 5′-AGGGCATATCGGAGTC-3′ at *FUS* exon 8 and 5′-GGGCATATCCGACATG-3′ at
*TAF15* exon 1 carry no
hybridisable near-match at ten times the default search depth, no single-mismatch match on the
exhaustive scan, no pre-mRNA site and no mature-parent duplex. Neither depends on the
ten-base-pair threshold, because no window of any parent pairs their catalytic gap at any length, so
their longest run is zero rather than merely short. 5′-GGGCATATCAAGCGCT-3′ at *TCF12* exon 7 passes
the same screens but not in the same way: its longest parent run is eight base pairs against
wild-type *NR4A3*, below the threshold rather than absent, so it is a candidate at the stated cut and
not at a stricter one. The fourth design with a clean deep screen,
5′-GGCATATCAAGCGCTG-3′ at the same junction, is excluded by an eleven-base-pair *NR4A3* duplex.
That is the honest size of the
candidate set, and no junction among them has a published patient breakpoint — the exon-resolved *TAF15*
breakpoints reported in EMC are exon 6, and for *FUS* and *TCF12* exon 7 none has been published at all.
Selecting within each junction rather than across the panel changes what is available, not what is
clean: Table 4 applies the same criteria at all 38, where 35 have a design that clears the parent
screen and *TAF15* exon 14, *TCF12* exon 3 and *TFG* exon 2 have none. Both junctions with a
published exon-resolved breakpoint have one at the top gap-level margin, with longest parent runs of
eight and nine base pairs.

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
Twenty of 176 do. No candidate above is among them, and the two secure at any parent-duplex
threshold carry a load well below chance — 0.33 and 0.24 of expectation at ≤2 mismatches, and 0.06
and 0.04 for gap-paired sites, ranking 26th and 13th of 176. That is the strongest statement this work can
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

### 3.10 · Gap length trades junction specificity against parent-duplex competence

The panel above is one geometry. Tiling the same seams at 5-8-5 and 5-10-5, wing fixed at five
nucleotides, resolves what a longer catalytic gap buys and what it costs (Table 5).

The two are the same nucleotide. Inside the gap, the junction-unique bases on the shorter side and
the bases one wild-type parent pairs on the longer side are complements: they sum to the gap. That
holds for every design in all three panels rather than on average, so no design can gain a nucleotide
of gap-level margin without handing RNase-H1 one more nucleotide of contiguous wild-type-parent
duplex. Lengthening the gap makes the enzyme more competent against the fusion and against the parent
transcript together, and no choice of register avoids it.

Both directions are large. The best available gap-level margin rises from 3 to 4 to 5 and the
junction-spanning registers per seam from five to seven to nine. At the *EWSR1* exon 12 / *TAF15*
exon 11 / *FUS* exon 10 seam the design carrying that margin sheds its transcriptome load completely:
123 hybridisable gap-spanning cleavage risks at six gene loci become 3 at one locus and then none.
Over the six seams screened at every geometry, designs carrying no gap-spanning risk rise from 8 of
30 to 28 of 42 to 54 of 54, and the most such risk loci on any one design falls from seven to two to
none. Against that, the contiguous DNA a wild-type parent pairs at the same seam rises from 3 to 4 to
5 nucleotides and the most stable parent duplex from −7.77 to −8.66 to −10.25 kcal/mol. The corpus
shows the same trade: designs whose parent pairs at least five nucleotides of contiguous gap DNA, the
shorter of the two reported minima for RNase-H1, rise from 76 of 190 to 228 of 266 to 342 of 342, and
the median most stable parent duplex falls from −8.66 to −14.58 kcal/mol. At 5-10-5 that count is
every design, and necessarily so, since the smaller half of a gap of ten cannot be under five; at
5-6-5, 114 of 190 designs keep the parent below it.

Part of the fall in near-matches is guaranteed by the instrument rather than measured. At a fixed
budget of two mismatches, every locus a longer design can reach is also reached by each of its own
shorter sub-windows, so the reachable set can only shrink as the design lengthens, and two mismatches
is a fractionally stricter test at 20 nucleotides than at 16. Only the size of the fall and which
designs reach zero are measurements. The parent-side quantities carry no such qualification, being
computed from the seam rather than from a search.

Two liabilities the transcript screens do not reach move the favourable way: a mature parent can pair
the whole gap for 181 of 190 designs at 5-6-5 but 87 of 342 at 5-10-5, and designs pairing the gap in
parent pre-mRNA fall from 19 of 190 to 9 of 342. Nor is the effect confined to the longest geometry,
since 5′-CAGGGCATATCAAGCGCT-3′ at *TCF12* exon 7 returns no near-match at all where the 16-mer
surviving at that seam returns three.

### 3.11 · Off-target loci in the exposure organs and the tumour compartment

The screens establish that a design matches a gene, not that the gene is transcribed where the drug
goes. Read against reference expression data, the two reagents' gap-paired loci separate, in the
direction opposite to the sizes of their loads (Table 6). The *EWSR1* exon 12 reagent's six loci carry 123 of
the panel's 278 transcript records, and none of the four measurable ones reaches the upper cut in
liver or either kidney compartment; *ANKS1B* supplies 67 of them and sits below the lower cut in all
three, peaking instead in brain at 24.9 TPM. The *TAF15* exon 6 reagent returns five loci, of which
*NRP1* reaches 6.6 to 17.8 TPM across all three exposure tissues and is the only one all five of that
seam's tiling registers return, on five transcript records, so robustness to register and record
count order it differently. The tumour-compartment proxy orders them differently again, *LAMA4*
carrying the panel's highest value there at 268.6 TPM in cultured fibroblasts.

## 4 · Discussion

Designability is not the constraint: junction-spanning designs exist at every frame-compatible NR4A3
fusion junction, though at three of them every design pairs a wild-type parent through the catalytic
gap. Specificity does not
sort by partner — with all 38 junctions screened, every one of the five partners has a junction whose
best design carries no hybridisable gap-spanning near-match, so it is the exon a fusion breaks at,
not the gene it breaks into, that predicts a clean design.

Clean designs are much scarcer than the default search depth implies, and two independent findings
converge on that. Of the nine designs with no hybridisable near-match at that depth, six lose the
property at ten times it, three of them having reported no near-match at all before; and five form an
eleven- or twelve-base-pair duplex with a mature wild-type parent that pairs the whole catalytic gap,
one of them with *NR4A3* itself, where no screen filtering on global identity can see it. Three designs
survive every screen applied here, two of them at any parent-duplex threshold, and that is the honest
size of the candidate set, taken at
the deeper ceiling now applied to all 38 junctions and 187 design records with no hit list
truncated. Those counts are reported as their own
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
here. Gap length is not a third, for a reason that is arithmetic rather than empirical: in every design of
all three panels the margin a longer gap wins and the contiguous parent duplex it concedes are the
same nucleotides (§3.10). A longer gap buys a markedly quieter transcriptome, and buys it by making
RNase-H1 more competent against the parent as well as against the fusion, which is the same limit
reached from the other side rather than a way around it. The field's own
answer to poor single-base discrimination has been positional chemical modification of the gap rather
than length,<sup>26</sup><!--PMID:23963702--> and that is the design direction this result points to,
now for a demonstrated reason rather than by analogy. A steric-block
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
cells, reduced fusion expression by 58% and proliferation by 22% in vitro.<sup>35</sup><!--PMID:37370737--> Applied here, the
reagents to synthesise are the best available at the two junctions with a published exon-resolved
breakpoint (Table 4): 5′-GGGCATATCATCAAAC-3′ at *EWSR1* exon 12 and 5′-GGGCATATCTTGTGTG-3′ at
*TAF15* exon 6, together about 95% of molecularly confirmed cases. Both hold the top gap-level
margin of 3 and neither pairs a parent through the catalytic gap at the ten-base-pair threshold,
although the *TAF15* reagent's longest parent run is nine; the first
also tests, against a synthetic target only, the multi-partner prediction. Two risks attach, in this
order. The first is architectural and the Methods disclose it: a six-nucleotide gap supports
noteworthy but incomplete RNase-H1 activity where seven to ten are reported as
optimal,<sup>24</sup><!--PMID:24981949--> so weak knockdown is at least as likely to be the gap as
the sequence. That risk is now addressable by a named second reagent rather than by a caveat.
5′-AGGGCATATCATCAAACC-3′ is the 5-8-5 design at the same *EWSR1* exon 12 seam: it spans the same
three partners' breakpoints, sits inside the reported activity optimum, holds a gap-level margin of 4
where the 16-mer holds 3, and carries 3 hybridisable gap-spanning near-matches at one gene locus
against the 16-mer's 123 at six (§3.10, Table 5). Synthesised alongside it, at one extra
oligonucleotide and one extra well per condition, it separates the two explanations a weak result
would otherwise confound: a 5-8-5 arm that knocks down where the 5-6-5 arm does not attributes the
failure to gap length rather than to sequence. What it does not buy is parental sparing, since the
same two nucleotides lengthen each parent's contiguous duplex from 3 to 4 nucleotides of gap DNA and
from −7.77 to −8.66 kcal/mol. Both arms therefore need the fusion-negative comparator below. The second risk is transcriptome load, which differs sharply between
them: the *EWSR1* reagent carries the heaviest disclosed load of any design considered here,
123 gap-paired hybridisable near-matches at the deeper ceiling, recounting to six gene loci, all at
the screen's loosest admitted identity and none on a parent transcript (§3.7), against 8 such
near-matches at five loci for the *TAF15* reagent. The parent compartments qualify that, and in a
way the transcript screens cannot show. The *EWSR1* reagent carries a hybridisable
intron–exon-spanning near-match in wild-type *TAF15* pre-mRNA at two mismatches, one of them inside
the catalytic gap, returned independently by the pre-mRNA and the genome-wide arms; it falls outside
every parent count reported here because those require the gap to be paired in full, and by the
bounds adopted above a single gap mismatch does not abolish cleavage. It is the multi-partner
result's own cost rather than an incidental hit: the ten donor bases shared across *EWSR1*, *TAF15*
and *FUS* that let one oligonucleotide span three seams are the bases that place it against
wild-type *TAF15*. The *TAF15* exon-6 reagent carries no hybridisable pre-mRNA site at all, which is
a second respect in which the two separate on something other than count. That load should
travel with the reagent, and it is a liability to disclose and to control for rather than a
disqualification, because on the exhaustive genome scan the same design falls below chance in both
directions that matter, at 0.69 times the expected number of near-matches at two mismatches and
0.62 times the expected number of gap-paired ones. Expression reads those two loads differently from
their sizes (§3.11): none of the *EWSR1* reagent's four measurable loci is expressed at the upper cut
in the organs a systemic dose reaches, while the *TAF15* reagent's five include *NRP1*, which is, in
all three. That does not reverse the ranking, since no screen here establishes that a two-mismatch duplex
engages any of them, and it is not a statement about safety. It is the first evidence separating the
two reagents on anything but count, and it points the load question at the shorter list rather than
the longer. The three designs that survive every screen are
mechanism controls rather than candidates: 5′-AGGGCATATCGGAGTC-3′ at *FUS* exon 8,
5′-GGGCATATCCGACATG-3′ at *TAF15* exon 1 and
5′-GGGCATATCAAGCGCT-3′ at *TCF12* exon 7, tiered as §3.8 describes. The *TAF15* exon-1 design is
contradicted by the exon-6 breakpoints reported in EMC, while for *FUS* and *TCF12* no exon-resolved
EMC breakpoint has been published at all. 5′-GGGCATATCTCTATAA-3′ at *TCF12* exon
17, which an earlier draft of this work put forward for that role, is not among them: at ten times
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
lost the property at ten times the default search depth, and that censoring is corpus-wide across
all 38 junctions re-screened at that depth (§3.6), so the default-depth figures throughout should be
read as lower bounds rather than as
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
cohort carried no identified partner.<sup>9</sup><!--PMID:36948401--> Every screened count outside
§3.10 is for one architecture, a 16-mer 5-6-5, and §3.10's comparison carries bounds of its own. The
exhaustive GRCh38 scan is unavailable at 18 and 20 nucleotides by construction rather than merely
unrun, since the scanner is a packed bitmap over the code space of a 16-mer and a longer window needs
a different data structure; the nesting argument bounds a longer design's genome liability by that of
its own sub-windows, but no such scan has been run, so that bound is an available next step and not a
result. No RNase-H1 assay distinguishes these geometries here, so which gap is preferable is not decided by
this work. The
thermodynamic calculation models an unmodified DNA:RNA hybrid and speaks to duplex formation rather
than to cleavage. Every parent count reported here requires the catalytic gap to be paired in full, which is the
binary rule the Methods decline to apply to cleavage, used as an inclusion criterion because no
retrieved measurement grades a partly-paired parent duplex; the class it excludes is 21 designs at
the pre-mRNA arm and is stated in §3.8 rather than left to the artefacts. All five screens address
hybridisation-dependent liability only; the
sequence-independent class of a phosphorothioate LNA gapmer, protein binding and the
target-independent hepatotoxicity of this chemistry, is not a function of any feature graded here.
The expression reading carries bounds of its own. Seven of the 23 loci returned no reading: three are
attributable to what the locus is, a brain-associated long non-coding RNA host, an antisense
transcript and a readthrough, while four remain uncharacterised and carry 11 of the panel's 278
records, so for those the exposure question is unanswered rather than answered negatively. No
expression figure is a predicted cleavage event, and the step from a gene being expressed in liver to
that oligonucleotide being a problem needs an argument no screen here supplies (Table 6). Reference
bulk medians describe normal tissue in a population, not a dosed patient's organ.
The genome scan removes the six-transcript bound the parent screens carried, at the cost of two of
its own: `hybridisable` is measured against an annotation, so a site in unannotated transcription is
reported as intergenic and not counted, and a screen against one assembly says nothing about a
patient's private variation. An earlier genome-wide attempt against a mixed public corpus returned
nothing interpretable and is released with the artefacts; it could not have done otherwise, having
no defined nucleotide span to form a null against. Every exhaustive arm inherits the
substitution-only bound: all are complete for mismatches by construction and blind to insertions and deletions.

## Tables

Tables 1 to 6 are in `fusion-junction-aso-submission-tables.md`, generated from the released
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
each of those is one physical oligonucleotide, plotted once rather than repeatedly (marked). The line
is the number of such matches expected for an arbitrary 16-mer under an independent-uniform-base
null, 8.2, computed against the scan's measured 718,571,139-nucleotide span;
118 of the 176 fall at or below it and 58 exceed it. Ten further designs from
modelled breakpoints not built from a spliced transcript model are excluded, and are released with
the artefacts. It is an expected count: the observed mean is 9.2, a ratio of 1.12, while the
median is 3, so real transcript sequence produces a long right tail the null cannot
rather than a uniform shift away from it. The line
separates "more than chance" from "at chance" and is not a significance test; the counts are
predictions from sequence search, not measured off-target activity.

## Declarations

**Data and code availability.** [ARCHIVE DOI], deposited from `github.com/trimcrae/Rare-cancers`.
A manifest listing every archived file with its SHA-256 travels with the deposit. Artefacts include the graded junction
atlas, per-junction design panels, all five screens, the per-junction reagent table behind Table 4,
the graded re-scores under
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
