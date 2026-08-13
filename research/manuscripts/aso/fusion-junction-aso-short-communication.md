---
id: DOC-FUSION-JUNCTION-ASO-SUBMISSION
title: "Junction-spanning gapmers across NR4A3 fusion partners in extraskeletal myxoid chondrosarcoma"
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

# In-silico design and predicted specificity limits of junction-spanning gapmers against NR4A3 fusions in extraskeletal myxoid chondrosarcoma

**Author.** Tristan D. McRae

*Independent researcher, unaffiliated.* Correspondence: trimcrae@gmail.com
ORCID: [to be inserted]

**Running title.** Junction gapmers across NR4A3 fusions

**Keywords.** antisense oligonucleotide; gapmer; RNase H1; fusion transcript; NR4A3; extraskeletal
myxoid chondrosarcoma; sarcoma

---

## Abstract

**Background.** Extraskeletal myxoid chondrosarcoma is an ultra-rare sarcoma defined by
rearrangement of *NR4A3* to a variable 5′ partner. Its chimeric mRNA carries a breakpoint seam
absent from every normal transcript — its one tumour-exclusive RNA feature. No junction-directed
oligonucleotide has been reported against any NR4A3 fusion.

**Methods.** Chimeras were built at the mRNA level from canonical Ensembl models, acceptor exon
retained whole; every donor-exon × acceptor-exon pair across five partners was graded.
Junction-spanning 16-mer 5-6-5 LNA/DNA/LNA gapmers were tiled over each frame-compatible seam, then
screened against all six parent transcripts, against RefSeq RNA by gap-resolved BLAST, and
exhaustively for ≤1 mismatch over 186,185 transcripts.

**Results.** Of 231 graded pairs, 38 are frame-compatible, and all 38 yield a gapmer matching no
parent perfectly. All 38 were screened with alignment orientation filtered, because a nucleotide
alignment search reports both strands and a reverse-complement match cannot hybridise. Such matches are 44% of
apparent gap-spanning risks (738 of 1,677), ranging 0–100% between junctions, so filtering reorders
junctions rather than rescaling them. Nine designs at six junctions then carry no
hybridisable near-match at all, no exact or single-mismatch match among 186,185 transcripts, and zero
residual cleavage load under both literature discrimination bounds. One 16-mer spans the *EWSR1*
exon 12, *TAF15* exon 11 and *FUS* exon 10 seams through ten identical donor bases — a sequence
property, not a clinical one: published exon-resolved *TAF15::NR4A3* breakpoints are exon 6.

**Conclusions.** Neither designability nor transcriptome load limits junction gapmers here. The
limiting step is discrimination between the fusion and its parent transcripts at the catalytic gap,
set by enzymology and chemistry, which no computation here resolves.

---

## 1 · Introduction

EMC is defined in the large majority of cases by an in-frame fusion of *EWSR1* to the orphan nuclear
receptor *NR4A3*,<sup>1</sup><!--PMID:8634690--> with *TAF15* accounting for a substantial minority
and *TCF12* and *TFG* reported rarely.<sup>2</sup><!--PMID:32572850--> *FUS::NR4A3* is reported in
a recent series that identified it by sequencing in two of five variant EMCs.<sup>3</sup><!--PMID:41755350--> Next-generation sequencing of EMC finds
few recurrent secondary mutations beyond the fusion,<sup>4</sup><!--PMID:28423517--> so it is to a
first approximation the single clonal driver. In every junction type described, the predicted
product joins the amino-terminal transactivation domain of the FET-family partner to essentially the
entire NR4A3 protein, including its nuclear-receptor DNA-binding domain.<sup>1</sup><!--PMID:8634690-->

That driver is currently untargeted. Surgery with clear margins is the backbone of localised
disease, and for advanced disease no agent is approved specifically for EMC. The largest
EMC-specific prospective study, a single-arm phase 2 of pazopanib in centrally confirmed
*NR4A3*-translocated disease, returned four objective responses in 22 evaluable patients with a
median progression-free survival of 19 months (95% CI 11–27),<sup>5</sup><!--PMID:31331701--> and
first-line anthracycline-based chemotherapy returned four responses in ten evaluable patients in a
molecularly confirmed retrospective series.<sup>6</sup><!--PMID:24345066--> The population a
fusion-directed agent would address is, by contrast, close to the whole disease: across 58
molecularly confirmed cases, 79% carried *EWSR1::NR4A3*, 16% *TAF15::NR4A3* and 3%
*TCF12::NR4A3*.<sup>7</sup><!--PMID:36948401-->

Protein-directed approaches to this fusion face a structural problem. The *NR4A3* ligand-binding
domain is retained near-intact in the chimera and is identical in sequence to wild-type NR4A3, so a
ligand that engages it cannot distinguish fusion from wild type. That matters because NR4A3 has
tumour-suppressive roles of its own: combined *NR4A1*/*NR4A3* loss causes acute myeloid leukaemia in
mice,<sup>8</sup><!--PMID:17515897--> and NR4A3's roles in cancer are context-dependent, tumour-suppressive in some
tissues and tumour-promoting in others.<sup>9</sup><!--PMID:33106376--> Either way, wild-type NR4A3 is not a protein a
therapy should silence indiscriminately. The chimeric mRNA
does not share this problem. Its breakpoint seam is a contiguous sequence absent from both parent
transcripts, so discrimination can in principle be enforced by base-pairing rather than by protein
conformation.

Targeting a fusion breakpoint with an oligonucleotide is not new; the approach has a continuous
lineage from
1991,<sup>10</sup><!--PMID:1794439--> including RNase-H-dependent antisense at a sarcoma fusion breakpoint in
1997,<sup>11</sup><!--PMID:9049825--> the general fusion-exclusivity rationale stated as a principle in 2005,<sup>12</sup><!--PMID:16083345-->
parental sparing demonstrated in at least four fusions,<sup>13–16</sup><!--PMID:33241214,36265509,21846246,23052253--> a bi-shRNA lipoplex directed
at the *EWSR1::FLI1* junction taken to preclinical justification,<sup>17</sup><!--PMID:27166877--> and a GalNAc-conjugated
junction siRNA in fibrolamellar hepatocellular carcinoma that passed the delivery gate in a rare
fusion-driven cancer.<sup>18</sup><!--PMID:37980543--> The contribution here is therefore not the modality but the indication. Across 5,153
unique records retrieved from Europe PMC, four mention *EWSR1::NR4A3* at title or abstract level;
these resolve to three papers, of which one concerns EMC and none is an oligonucleotide study. The count
of junction-directed oligonucleotide work against any NR4A3 fusion is zero.

Two questions follow that the field has not asked of this disease. First, the design lane has
addressed only *EWSR1*, while the partner varies — and partner identity is not clinically inert:
every reported objective response to an antiangiogenic tyrosine-kinase inhibitor in advanced EMC has
occurred in a non-*TAF15* patient, though the *TAF15* arm comprises three to five patients with zero
events and its Wilson upper bound remains compatible with equal response.<sup>5,19</sup><!--PMID:31331701,24703573--> Second,
whether a junction oligonucleotide must be bespoke per patient, or whether one sequence can serve
more than one fusion, determines whether the deployable artefact for an ultra-rare disease is a stock
reagent or a panel.

## 2 · Materials and methods

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

**Design.** Junction-spanning 16-mer gapmers were tiled in a 5-6-5 LNA/DNA/LNA architecture, retaining
only registers in which the seam falls inside the six-nucleotide DNA gap, since RNase-H1 cleaves
within the DNA:RNA duplex of the gap. Discrimination is set by the junction-unique bases inside
the gap, not by identity across the whole oligonucleotide, so designs were ranked by a gap-level
margin: the number of junction-unique bases inside the gap on the shorter side. Each candidate was
tested against all six parent transcripts, not only the two parents of its own fusion, because the
FET-family donors (FUS, EWSR1 and TAF15) are paralogues with similar low-complexity amino-termini.

**Specificity screening.** Two independent screens were applied. A gap-resolved screen queried each
target window against human RefSeq RNA (blastn-short, low-complexity filter off, ≥14/16 identity) and
classified each near-match by whether the six-nucleotide gap was fully base-paired. An exhaustive
seed-and-extend scan then searched 186,185 transcripts (GRCh38.p14) for exact and ≤1-mismatch matches;
this arm is complete for substitutions by construction and does not detect insertions or deletions.
The BLAST arm did not parse alignment orientation. `blastn` searches both strands, and a transcript
carrying the reverse complement of the target window cannot be hybridised by an antisense
oligonucleotide, so it is not a liability at all — yet such hits passed the identity filter and,
where they spanned the catalytic gap, were recorded as cleavage risks. The defect surfaced as a
contradiction between the two screens: at one junction a design returns five perfect 16/16 BLAST
matches to a transcript that the exhaustive ≤1-mismatch scan, which searches the sense orientation
only, reports as absent. Both cannot be true. Orientation is parsed and filtered in all 38 junction
screens, the 183 designs they hold, and therefore in every cleanliness statement made here; the only
two screens in the released set that are not filtered are modelled control seams built in amino-acid
rather than transcript coordinates, which carry no junction and support no claim. Whether a given screen belongs to the filtered group is
decided by auditing its per-hit labels rather than by the presence of a strand field, because a
screen can record the aligned strand on every hit and still have been classified before the filter
consulted it, which is indistinguishable from a sound screen unless the labels are read.
Target-site accessibility was estimated as mean unpaired probability over a truncated 180-nucleotide
local fold, and spans 0.160 to 0.707 across all 190 designs at real exon junctions (median 0.477).
It is released with the artefacts and is not used to rank anything here. A truncated
local fold is an equilibrium proxy that can over-estimate accessibility, the quantity is a weak
correlate of potency at best, and no measurement in this work bears on potency — so ordering
candidates by it would import a ranking the evidence does not support.

**Discrimination model.** The binary assumption that any mismatch inside the gap abolishes cleavage
is not supported by the primary literature and is not used for any claim of cleanliness. Measured
discrimination for an unmodified RNase-H-active oligonucleotide is approximately
five-fold,<sup>20</sup><!--PMID:23963702--> and at 16-mer length one study reports no efficient discrimination at
all.<sup>21</sup><!--PMID:7567450--> Both measurements are against a single-nucleotide substitution rather than a fusion
seam, and the pessimistic one used unmodified antisense DNA; they are applied here as the closest
available bounds. Every gap-resolved screen was therefore re-scored under both bounds as a graded
residual cleavage load, holding the hit set fixed so that only the scoring changed: all 38 junction
screens and 39 of the 40 screens released in total, the single exception being one coverage-only
control screen that records no gap-mismatch depth and so cannot be graded at all. The re-score counts
only hybridisable hits where it can — that is, where the retained hit list is complete, so every
hit's strand is known. Two distinct bounds follow, and they run in opposite directions. Where a hit
list is truncated the strand of the remainder is unrecoverable, so that design keeps a strand-blind
count, which over-counts liability because it includes matches no antisense oligonucleotide can
hybridise: an upper bound. The same truncation also means fewer hits are recorded than the search
returned, so the count of hits is itself right-censored: a lower bound on how many exist. Each design
records which bounds apply to it.

**Duplex thermodynamics and conventional design rules.** Because a base count is a proxy for
discrimination and a free energy is the field's standard instrument for it, each design was also
scored thermodynamically. A junction gapmer is a perfect complement of the fusion across all 16
positions, while a parent transcript can pair only the half of the oligonucleotide it contributes,
so the comparison is the full 16-mer duplex against the donor-side and acceptor-side runs alone.
Nearest-neighbour enthalpies and entropies for a DNA:RNA hybrid were taken from Sugimoto and
colleagues,<sup>22</sup><!--PMID:7545436--> read from a package that cites that source rather than
entered by hand, and ΔG°37 computed at 250 nM strand concentration. The keying of the table was
validated by reproducing an independent implementation's melting temperature over the design set,
which agreed exactly; a reversed strand convention yields plausible-looking energies and is the
failure this check excludes. These designs carry LNA wings and the table is for an unmodified
hybrid, so what is computed is the duplex the DNA backbone would form. LNA raises affinity on the
fusion and parent duplexes alike, compressing their difference, so the discrimination reported here
is an upper bound rather than an estimate. Separately, every design was audited against four
conventional antisense design rules (GC within 40–60%, no G-quadruplex motif, no homopolymer run of
four, and no CpG dinucleotide), not to grade the designs, but to ask whether conventional triage and
the gap-level margin would select the same molecules.

**Availability.** All code, graded artefacts and per-design tables are released under a single
archived version, deposited from the public repository at
`github.com/trimcrae/Rare-cancers` [ARCHIVE DOI]. Every result reported here is re-derived from the
committed artefacts in that archive without network access or credentials: the tables, the junction
atlas, the locus collapse, the chance baseline and the graded re-scores under both discrimination
bounds each recompute from files the archive contains. Regenerating the specificity screens from
scratch is not offline, because the gap-resolved arm queries NCBI BLAST and the exhaustive arm
downloads the GRCh38.p14 RefSeq RNA set. No reported number requires it, because each screen's hit set is
archived and the re-scores hold that hit set fixed.

## 3 · Results

### 3.1 · Frame compatibility as the bound on junction space

Grading all 231 donor-exon × acceptor-exon pairs across the five partners returns 38 frame-compatible
junctions (Table 1, Figure 1). The refusals are structural: *NR4A3* exon 2 carries no
coding sequence and is refused in every pair, and exon 4 places the acceptor outside the plausible
resumption range in every pair, so all variance sits in the exon-3 column. Within that column,
frame compatibility reduces to a single arithmetic condition — a donor coding phase of 1 — which is
necessary and sufficient across all 231 rows.

Among these, *EWSR1* exon 12 joined to *NR4A3* exon 3 is the junction reported most often — type 1
in 10 of the 15 *EWSR1*-rearranged tumours of an 18-case series<sup>23</sup><!--PMID:12378528--> — so
designs at this seam correspond to the largest documented patient group.

Every one of the 38 frame-compatible junctions yields at least one junction-spanning gapmer that is
not a perfect complement of any of the six parent transcripts, at GC contents largely inside the
conventional design band (25.0–75.0% across partners). Finding candidate sequences is therefore not
the constraint on this modality in this disease.

### 3.2 · Cross-partner coverage by a single oligonucleotide

Nine designs span the seam of more than one junction exactly, and all nine draw from *EWSR1*, *TAF15*
and *FUS* (Figure 2). Five cover the same three-partner set, differing only in register across the
seam. The best by gap-level margin is 5′-GGGCATATCATCAAAC-3′ (43.8% GC, gap-level margin 3), which
divides eight donor and eight acceptor bases at the seam of *EWSR1* exon 12, *TAF15* exon 11 and
*FUS* exon 10 joined to *NR4A3* exon 3, and occurs in none of the six wild-type parent transcripts.
The basis is sequence identity: the three donors are identical over the ten bases immediately 5′ of
their breakpoints, diverging at the eleventh. Ten exceeds the donor-side length of all five designs, which is
what makes the coverage arithmetically possible.

In one respect the published data contradict the clinical reading of this result. The only
exon-resolved *TAF15::NR4A3* breakpoints reported in EMC are exon 6: the primary report of
the variant fusion places the breakpoint at *TAF15* exon 6,<sup>24</sup><!--PMID:10537274--> and in a
series of 18 EMCs all three *TAF15*-rearranged tumours carried exon 6 joined to *NR4A3* exon
3<sup>23</sup><!--PMID:12378528--> — not exon 11. The exon-6 seam shares a single donor base with the exon-11 seam, so this oligonucleotide cannot
engage the *TAF15* junction that patients are reported to carry. That junction is itself
frame-compatible and yields five fusion-specific designs (43.8–50.0% GC), all five screened and
orientation-filtered — and every one of them retains a hybridisable gap-spanning near-match, four
loci at best and seven for the design its gap-level margin ranks first, six of those seven annotated
only as predicted gene models (Table 2). Two of the five nonetheless return no exact and no
single-mismatch match on the exhaustive scan. So the one *TAF15* seam with a published breakpoint is
designable and is not among the cleaner junctions, while the seam the multi-partner result rests on
has no reported patient. For *FUS* no exon-resolved EMC breakpoint has been published at all.
The three-partner result is therefore a statement about FET-family sequence architecture and a
hypothesis about junctions not yet observed; it is not a claim that one reagent serves three patient
groups. Testing it requires breakpoint sequencing of archival *TAF15*- and *FUS*-positive cases.

The same paralogy that permits this coverage is a specificity liability, which is why every
candidate was screened against all six parent transcripts.

### 3.3 · The non-FET partners: coverage and specificity

*TCF12* and *TFG* are the partners in this panel that are not FET-family proteins, and neither
appears in any of the nine multi-partner sets: all nine draw only on *EWSR1*, *TAF15* and *FUS*.
*TCF12* reaches multi-partner coverage only under a relaxed criterion that tolerates mismatches in
the oligonucleotide wings. Partner membership was never a criterion in the ranking; both were included because both are
reported EMC partners. The check had little power to fail: any non-homologous donor would be excluded, so it does not
separate FET paralogy from incidental exon homology. The stronger evidence for paralogy is that four
additional two-partner sets are also FET-only.

Specificity does not sort by partner. Taking at each junction the lowest count any of its designs
achieves after the orientation filter — which is not the convention of Table 2, where each row
reports the design with the highest gap-level margin, so a junction's best design and its
representative design need not be the same one — every one of the five partners has at least one
junction whose best design carries no hybridisable gap-spanning near-match: three of eight at both
*TCF12* and *FUS*, two of eight at *EWSR1*, one of eight at *TAF15* and one of six at *TFG*. The
minima therefore separate junctions rather than partners, and which exon a fusion breaks at matters
more for specificity than which gene it breaks into.

This reverses what the same analysis showed over a partial corpus, and the reversal is a lesson
about coverage rather than about biology. When 16 of the 38 junctions had been screened with
orientation filtered, the designs with no hybridisable near-match were all at *TCF12*, and that
looked like a partner effect worth reporting: breadth at the FET partners, specificity at *TCF12*.
Screening the remaining 22 dissolved it. Nothing about *TCF12* changed; the comparison had simply
been drawn against partners whose junctions were mostly unscreened, and an absence of clean designs
among junctions nobody had screened is not evidence that clean designs are absent there.

### 3.4 · Strand orientation reorders the junctions

All 38 frame-compatible junctions were screened with orientation parsed and filtered, 183 designs
across them. Twenty-two were screened or re-screened for this purpose, and the reason for the
re-screening is worth stating because the records it replaced are indistinguishable from sound ones
unless their labels are examined: some predate the parsing of alignment strand altogether, while
others record the strand on every hit and were classified before the filter consulted it, so their
counts ignored a field their own records carried. Neither group could be repaired after the fact,
because only the top 15 hits of a list up to 50 long are retained and the strand of the remainder is
not recoverable, so each was screened again rather than corrected. Counts here therefore differ from
any earlier version of this analysis. A nucleotide alignment search reports both strands, so a
proportion of the returned near-matches lie on the strand opposite the target window. A transcript
carrying the reverse complement of that window cannot be hybridised by an antisense oligonucleotide:
there is no duplex, therefore no RNase-H1 substrate and nothing to cleave. Such a match is not a
weak liability but no liability at all, and it must be removed before any count means anything.

Across the filtered corpus, 44% of the apparent gap-spanning risks are minus-strand (738 of
1,677). The proportion is not uniform: it runs from 0% at *TFG* exon 4, where no apparent risk is
minus-strand, to 100% at both *EWSR1* exon 1 and *TCF12* exon 7, where every one is. That variance is the substantive point. A
uniform inflation would rescale every junction and leave their ordering intact, whereas this filter
reorders them — *EWSR1* exons 7 and 13 return 55 and 57 apparent gap-spanning hits respectively, and
after filtering they stand at 6 and 53.

### 3.5 · Nine designs survive the filter with no hybridisable near-match

After filtering, nine designs at six junctions carry no hybridisable near-match at all
(Table 3), spanning four of the five partners: three at *EWSR1* exon 1
(5′-GGGCATATCCGTGGAC-3′, 5′-GGCATATCCGTGGACG-3′, 5′-GCATATCCGTGGACGC-3′), one at *FUS* exon 8
(5′-AGGGCATATCGGAGTC-3′), one at *TAF15* exon 1 (5′-GGGCATATCCGACATG-3′), and four at *TCF12* —
5′-GGGCATATCTCTATAA-3′ at exon 17, 5′-CAGGGCATATCTTGCA-3′ at exon 9, and
5′-GGCATATCAAGCGCTG-3′ and 5′-GCATATCAAGCGCTGC-3′ at exon 7. The exhaustive scan agrees
independently: each returns no exact and no single-mismatch match anywhere in 186,185 transcripts.
The two arms fail in different ways — one is a heuristic alignment search over both strands, the
other an exhaustive substitution scan over the sense orientation only — so their agreement is not a
restatement.

The graded re-score agrees, with one instructive exception. Scoring every retained hit by the
residual cleavage a gap-internal mismatch is predicted to permit, under the optimistic five-fold
bound and under the pessimistic bound at which a 16-mer discriminates not at all, returns a residual
load of zero for all nine of these designs — and for one further design, at *FUS* exon 11, which is
not counted as clean here. That design returns 21 near-matches of which only 15 are retained, and
all 15 are minus-strand; the graded score therefore sees nothing hybridisable to score, while the
cleanliness criterion refuses it because the six unretained hits are unknown. The graded model has no
censoring guard, so it can award a zero the hit list does not support, and the stricter count is the
one reported. That is the arithmetic
consequence of their having no hybridisable hit to score rather than an independent measurement, but
it is the point at which the discrimination model the Discussion rests on is applied to the
candidates themselves, and under the harsher of the two bounds they survive it.

That agreement is also what corroborates the orientation call itself. Three designs return perfect
16/16 BLAST matches while the sense-only exhaustive scan reports no exact match. Both results can
only be correct if every one of those BLAST hits is on the minus strand, and every one is.

### 3.6 · What chance predicts, and the two bounds that remain

A chance argument bounds how surprising a low count should be, and it points the other way from the
reading these numbers first invite. There are 1,129 16-mers within two substitutions of any given 16-mer, so an arbitrary
transcriptome position matches at ≥14/16 with probability 2.6 × 10⁻⁷; over an assumed RefSeq RNA
span of 3 × 10⁸–8 × 10⁸ nucleotides (assumed, because the screens record transcripts scanned rather
than nucleotides, and both bands here inherit that range) that predicts 79–210 near-matches for any
16-mer whatever. The BLAST arm cannot test this: its hit list is capped at 50, which lies below the
null's lower bound of 79, so any
design must return fewer whatever the transcriptome contains. The exhaustive arm can test it, being
complete for substitutions by construction, and it comes in marginally low: a median of 3 observed
against 3.4–9.1 predicted at the ≤1-mismatch threshold, which sits just below the band rather than
comfortably under it. Where an instrument complete by construction disagrees with the
null, the null is over-predicting, as an independent-uniform-base model will against real transcript
sequence; the size of that over-prediction is small here and should not be read as more. It separates "more than chance" from "at chance" and supports nothing finer.

Two bounds remain on these counts and neither is corrected for. The BLAST arm returns at most 50
hits per query, and 35 of the 183 filtered designs reach that cap; a further 101 exceed the 15 hits
retained per design, so 136 in all carry right-censored counts. The nine clean designs are not among
them, returning zero to eight raw hits each.
Separately, BLAST is a heuristic and its sensitivity at ≥14/16 is unquantified here, so "no
hybridisable near-match" is a statement about what this search found. The ≤1-mismatch result carries no such
sensitivity qualification, being exhaustive for substitutions by construction, which is why it is the
arm the cleanliness claim rests on; it remains blind to insertions and deletions, to the minus
strand, and to pre-mRNA.

### 3.7 · Near-match counts overstate the number of loci

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
only as predicted `XR_` models. One locus, no curated transcript, from a raw count of nine. The same
design returns no exact match and a single ≤1-mismatch match on the exhaustive scan.

### 3.8 · Duplex thermodynamics and conventional design rules

Scored as free energies, every one of the 190 fusion-specific designs favours the fusion duplex over
the best duplex either parent can form, by 4.8 to 13.1 kcal/mol with a median of 9.6. The denominator
here is 190 rather than the 183 of the specificity screens because a free energy needs only a
sequence, whereas a screen needs a BLAST query that returned: seven of the 190 failed at the remote
service — three on a poll timeout and four on a dropped connection — and so are scored here and not
screened there. The 190 records are 176 distinct molecules, because nine of the 16-mers meet more than
one partner's seam and are recorded once per seam. The reason every design favours the fusion is
structural rather than subtle: a parent pairs roughly half the oligonucleotide, and half a duplex is
much the weaker one. That is worth stating precisely because it separates two things a base count
conflates. Discrimination at the level of *binding* is not marginal here and is not what constrains
the modality; what remains unresolved is discrimination at the level of *catalysis*, where RNase-H1
requires a paired DNA gap and where the literature bounds span one- to five-fold. The thermodynamic
result therefore narrows the paper's central uncertainty rather than relieving it.

The two rankings agree in direction. Grouping designs by the gap-level margin the Methods define,
mean ΔΔG°37 rises monotonically with it, from 8.3 kcal/mol at margin 1 to 9.9 at margin 2 and 10.7
at margin 3, so the base count and the free energy order the candidates the same way. Since the margin
is computed from junction-unique bases and the free energy from stacking parameters, that agreement
is corroboration rather than restatement.

Conventional design rules select differently, and against the paper's own candidates. Of the 190
designs, 106 satisfy all four rules; the rules bind at different rates, with every design free of a
G-quadruplex motif but 13 carrying a homopolymer run of four, 43 a CpG dinucleotide and 58
falling outside the 40–60% GC window. The failures overlap, so they do not sum to the 84 designs
that fail at least one.
The disagreement is sharpest exactly where it matters most. Of the nine designs with no hybridisable
near-match (Table 3), exactly one satisfies all four rules. Seven contain a CpG dinucleotide, the
canonical TLR9 immunostimulatory motif and something routinely designed out of therapeutic
oligonucleotides, and four fall outside the 40–60% GC window — the three *EWSR1* exon-1 designs above
it at 62.5% and 5′-GGGCATATCTCTATAA-3′ below it at 37.5%. Only 5′-CAGGGCATATCTTGCA-3′ at *TCF12*
exon 9 passes every rule, and the multi-partner candidate 5′-GGGCATATCATCAAAC-3′, which is not among
the nine, also passes all four. So the two filters do not merely disagree at the margin: the cleanest
designs this work found are, with one exception, molecules conventional triage would reject. Neither
filter dominates the other, and both are reported here rather than composed into a single score,
because composing them would hide precisely this tension.

## 4 · Discussion

Three findings stand, the second conditionally. Junction-spanning, parent-sparing designs exist at
every frame-compatible NR4A3 fusion junction, and nine of them, at six junctions across four
partners, carry no hybridisable near-match on
the alignment screen and no single-mismatch match on the exhaustive one, so neither sequence availability nor transcriptome load is what constrains this
modality here. One 16-mer spans three partners' seams at once through a ten-base donor
identity, which would change the deployable artefact for an ultra-rare disease from *n* bespoke
oligonucleotides to a stock reagent — if patients carrying *TAF15* and *FUS* fusions prove to break at
those exons, which the only exon-resolved *TAF15* data published say they do not. And specificity does not
sort by partner: with all 38 junctions screened, every one of the five partners has a junction whose
best design carries no hybridisable gap-spanning near-match, so it is the exon a fusion breaks at,
not the gene it breaks into, that predicts a clean design.

The limiting step is discrimination, and it is not computable. The two available bounds on
single-mismatch RNase-H1 discrimination span one- to five-fold, and the pessimistic bound is the one
measured at the length used here.<sup>21</sup><!--PMID:7567450--> This is a separate question from
off-target load, and it is not improved by the designs that carry none: an oligonucleotide with no
transcriptome match still has to distinguish the fusion from the two parent transcripts that supply
its own two halves, and under the pessimistic bound a 16-mer does not discriminate a single mismatch
at all. Free-energy calculation does not narrow it either, and locating why is the useful part: every
design discriminates amply at the level of duplex formation, so what is unresolved is specifically
the catalytic step, not the binding one. No amount of further sequence analysis narrows that
interval; a measurement does. The field's own
answer to poor single-base discrimination has been positional chemical modification of the gap rather
than length,<sup>20</sup><!--PMID:23963702--> and that is the design direction this result points to. A steric-block
mechanism, which does not require gap-level discrimination, is a second alternative this work does not
evaluate.

Delivery remains unsolved for a tumour, and separates into three routes with different
requirements. A characterised EMC-enriched surface antigen is a prerequisite of
the systemic receptor-targeted route only; local and inhaled administration require none. EMC's
distant spread is lung-dominant, at 35–45% of patients and a median of approximately 28 months to
metastasis,<sup>25</sup><!--PMID:41055792--> and inhaled oligonucleotides have reached patients in non-oncology
indications, including an inhaled antisense oligonucleotide in phase 1<sup>26</sup><!--PMID:39500647--> — a
splice-switching oligonucleotide rather than an RNase-H1-active gapmer, so it establishes the route
and not the mechanism used here — and an inhaled
siRNA in phase 2b–3.<sup>27</sup><!--PMID:40028836--> Those agents target airway epithelium or parenchyma, which is the
compartment inhalation naturally reaches; a hypocellular, matrix-rich parenchymal sarcoma nodule is
not, and no retrieved record concerns a solid-tumour target. The route is therefore established in humans but not for
this compartment.

The experiment that would resolve the central uncertainty is routine and has been published in an
analogous disease: fusion-specific antisense oligonucleotides against *NAB2::STAT6* in solitary
fibrous tumour, evaluated against CRISPR-engineered isogenic fusion-positive and fusion-negative
cells, reduced fusion expression by 58% and proliferation by 22% in vitro.<sup>28</sup><!--PMID:37370737--> Applied here,
5′-GGGCATATCATCAAAC-3′ remains the single highest-information reagent, because one synthesis tests
both the mechanism and the multi-partner prediction; its predicted load — five gap-spanning
near-matches at one uncharacterised locus and a single ≤1-mismatch transcriptome match (§3.7) —
should travel with it. If the object is instead the cleanest available test of the mechanism alone,
5′-GGGCATATCTCTATAA-3′ at *TCF12* exon 17 carries no hybridisable near-match on either screen
(Table 3), at the
cost of addressing a partner reported in a few per cent of patients.

Transferability depends on how that experiment is set up. The breakpoint of the cell line or patient sample must be established
at nucleotide resolution by RNA sequencing before any oligonucleotide is ordered: every design here
is specific to one exon pair, and none is valid for an unverified junction. A positive
control gapmer against an abundant housekeeping transcript in the same cells is required to separate
failed delivery from failed discrimination: a knockdown assay alone cannot distinguish them, and
discrimination is the failure mode this work predicts. The decision threshold should be fixed before
the experiment. The informative readout is fusion knockdown measured against wild-type *NR4A3*
knockdown in the same well; a selectivity below the approximately five-fold bound cited above would
falsify the gap-margin ranking on which every candidate here is ordered.

**Limitations.** The cleanliness claim is bounded by what each screen can see. BLAST is heuristic and
its sensitivity at the ≥14/16 threshold is unquantified here, so "no hybridisable near-match" is a
property of this search rather than of the transcriptome; the exhaustive ≤1-mismatch scan carries no
such qualification and is the arm the claim rests on. Counts that reached the 50-hit cap are
right-censored lower bounds — 35 of the 183 filtered designs, none of them among the nine clean ones.
Only 47 of those 183 have hit lists complete enough to be assessed for cleanliness at all, so nine
clean designs is a floor over that subset and not a total. All 38 frame-compatible junctions are screened
with the orientation filter applied, so no junction here carries an unfiltered count. The chance null is crude:
it assumes independent uniform bases, where real transcript sequence is composition-skewed and
repetitive, so it separates "more than chance" from "at chance" and nothing finer. Which exon pair a
given patient carries is not decidable from exon structure, so the multi-partner result is
conditional on *TAF15* and *FUS* breakpoints falling at the homologous exons — a clinical fact not
established here — and *TCF12::NR4A3* fusions are reported in
patients<sup>29,30</sup><!--PMID:11156374,12598313--> but not at the exon resolution these designs
require. The thermodynamic calculation models an unmodified DNA:RNA hybrid, while these designs carry LNA wings; LNA raises affinity on the fusion and parent duplexes alike, which compresses their difference, so the reported discrimination is an upper bound rather than an estimate, and it speaks to duplex formation rather than to cleavage. Finally, both screens search mature transcript sequence only. RNase-H1 is active in the
nucleus and gapmers are known to engage pre-mRNA, so intronic and intron–exon-spanning sites are a
class of liability that neither the RefSeq RNA search nor the transcript-level exhaustive scan can
see; the counts reported here therefore bound the mature-transcript compartment only. That gap is
closable by a genomic screen and is not closed here.

## Tables

Tables 1 to 3 are in `fusion-junction-aso-submission-tables.md`, generated from the released
artefacts so that a cell and its source cannot diverge.

## Figure legends

**Figure 1. Frame compatibility across the NR4A3 fusion junction space.** All 231 donor-exon ×
acceptor-exon pairs across *EWSR1*, *TAF15*, *TCF12*, *FUS* and *TFG*, graded against the frame
condition.
Rows are donor exons grouped by partner; columns are *NR4A3* acceptor exons. Two acceptor columns
are refused in every pair for structural reasons — exon 2 carries no coding sequence and exon 4
falls outside the plausible resumption range — so the 38 frame-compatible junctions lie in a single
column. Frame compatibility is an arithmetic property of exon structure and is not a claim about
which junctions patients carry.

**Figure 2. One 16-mer spans three partners' breakpoints.** The seam windows of *EWSR1* exon
12, *TAF15* exon 11 and *FUS* exon 10 joined to *NR4A3* exon 3, aligned at the breakpoint. Blue,
donor exon; green, acceptor exon; red and boxed, positions at which the three donors differ. Those
positions are boxed as well as coloured, because that distinction is the one a reader most needs and
red against green carries no information in greyscale or to a red-green colour-blind reader. The shaded box is
the target window of 5′-GGGCATATCATCAAAC-3′, with the 5-6-5 gapmer architecture below it. The three
donors are identical over the ten nucleotides before the breakpoint, which is what makes one
oligonucleotide junction-spanning at all three seams — and is the same identity that makes the
parent transcripts hard to discriminate from, so the gap-level margin of three is shown alongside.
Coverage is predicted from sequence and has not been measured.

**Figure 3. Transcriptome load per design against chance expectation.** Each bar is one distinct
oligonucleotide's count of exact plus ≤1-mismatch matches over 186,185 transcripts, ranked. The 190
design records at real exon junctions collapse to 176 molecules, because nine of the 16-mers are
junction-spanning at more than one partner's seam at once — five at three seams and four at two — and
each of those is one physical oligonucleotide, plotted once rather than repeatedly (marked). The band
is the number of such matches expected for an arbitrary 16-mer under an independent-uniform-base null
(3.4–9.1); 125 of the 176 fall at or below its upper bound and 51 exceed it. A further ten designs, from two
modelled breakpoints whose seams were not built from a spliced transcript model, are not plotted;
four of those ten exceed the band, at 16 to 95 matches and 75.0 to 81.2% GC. Because this scan is
exhaustive for
substitutions, the fact that observed load runs below the band is evidence that the null
over-predicts against real transcript sequence rather than that the search is incomplete. The band
separates "more than chance" from "at chance" and is not a significance test; the counts are
predictions from sequence search, not measured off-target activity.

## Declarations

**Data and code availability.** [ARCHIVE DOI], deposited from `github.com/trimcrae/Rare-cancers`.
A manifest listing every archived file with its SHA-256 travels with the deposit. Artifacts include the graded junction
atlas, per-junction design panels, both specificity screens per junction, the graded re-scores under
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

*The 30 numbered entries are listed in `fusion-junction-aso-submission-references.md`, generated
from retrieved bibliographic records. Each superscript above carries its PubMed identifier in a
non-rendering comment, and the numbering is assigned from those identifiers by order of first
citation, so a superscript and its reference cannot drift apart.*
