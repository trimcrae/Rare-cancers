---
id: DOC-FUSION-JUNCTION-ASO-SUBMISSION
title: "Junction-spanning gapmers across NR4A3 fusion partners in extraskeletal myxoid chondrosarcoma"
level: L3
kind: manuscript
status: live
canonical_for:
  - the submitted form of the fusion-junction ASO work
purpose: >
  The submission manuscript for PUB-ASO, written as a Short Communication for Nucleic Acid
  Therapeutics. Its provenance archive, including every superseded value and the full correction
  history, is fusion-junction-aso-working-record.md; the numbers themselves live in the artifacts
  under research/modalities/ and are not duplicated here.
scope: >
  Computational design and specificity screening only. No wet-lab experiment was performed, and
  nothing here asserts efficacy, potency, safety, a therapeutic window, delivery to a tumour, or
  clinical readiness for any sequence.
audience: [external reviewers, collaborators, maintainers]
date: 2026-08-12
last_verified: 2026-08-12
---

# In-silico design and predicted specificity limits of junction-spanning gapmers against NR4A3 fusions in extraskeletal myxoid chondrosarcoma

**Author.** Tristan D. McRae

*Independent researcher, unaffiliated.* Correspondence: trimcrae@gmail.com
ORCID: [TO BE SUPPLIED — no ORCID iD exists in the project record; one is free to register and is
required by some publishers at submission.]

**Running title.** Junction gapmers across NR4A3 fusions

**Keywords.** antisense oligonucleotide; gapmer; RNase H1; fusion transcript; NR4A3; extraskeletal
myxoid chondrosarcoma; sarcoma

---

## Abstract

**Background.** Extraskeletal myxoid chondrosarcoma (EMC) is an ultra-rare sarcoma defined by
rearrangement of *NR4A3* to a variable 5′ partner, most often *EWSR1*. The chimeric mRNA carries a
breakpoint seam absent from every normal transcript, the disease's one tumour-exclusive feature at
the RNA level. No junction-directed oligonucleotide has been reported against any NR4A3 fusion.

**Methods.** Chimeric transcripts were built at the mRNA level from canonical Ensembl models,
retaining the acceptor exon in full, and every donor-exon × *NR4A3*-acceptor-exon pair was graded
across all five reported partners. Junction-spanning 16-mer 5-6-5 LNA/DNA/LNA gapmers were tiled over
each frame-compatible seam and screened against every parent transcript, then against human RefSeq
RNA by gap-resolved BLAST and against 186,185 transcripts by exhaustive ≤1-mismatch search.

**Results.** Of 231 graded exon pairs, 38 are frame-compatible, and all 38 yield at least one
junction-spanning gapmer that is not a perfect complement of any parent transcript. No design at any
of the 12 junctions screened is free of predicted gap-spanning near-matches, but that is a property
of the threshold: at 16-mer length chance alone predicts 79–210 matches at ≥14/16 identity against
the human transcriptome. Read against that null, 49 of the 60 designs at real junctions carry
off-target load at or below chance expectation. Separately, one 16-mer spans the seams of *EWSR1*
exon 12, *TAF15* exon 11 and *FUS* exon 10 at once through ten identical donor bases — a sequence
property and not a clinical one, since the only exon-resolved *TAF15::NR4A3* breakpoints published
are exon 6.

**Conclusions.** Neither designability nor transcriptome load is the limiting step for junction
gapmers in NR4A3-rearranged sarcoma. The limiting step is discrimination between the fusion and its
parent transcripts at the catalytic gap, which is set by enzymology and chemistry, and which no
computation here resolves.

---

## 1 · Introduction

EMC is defined in the large majority of cases by an in-frame fusion of *EWSR1* to the orphan nuclear
receptor *NR4A3*,<sup>1</sup><!--PMID:8634690--> with *TAF15* accounting for a substantial minority
and *TCF12* and *TFG* reported rarely,<sup>2</sup><!--PMID:32572850--> *FUS::NR4A3* is reported in
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
only, reports as absent. Both cannot be true. Orientation is now parsed, but the screens reported
here predate the fix and were not re-run, so their counts are upper bounds.
Target-site accessibility was estimated as mean unpaired probability over a truncated 180-nucleotide
local fold, and is reported only as a weak correlate.

**Discrimination model.** The binary assumption that any mismatch inside the gap abolishes cleavage
is not supported by the primary literature and is not used for any claim of cleanliness. Measured
discrimination for an unmodified RNase-H-active oligonucleotide is approximately
five-fold,<sup>20</sup><!--PMID:23963702--> and at 16-mer length one study reports no efficient discrimination at
all.<sup>21</sup><!--PMID:7567450--> Both measurements are against a single-nucleotide substitution rather than a fusion
seam, and the pessimistic one used unmodified antisense DNA; they are applied here as the closest available bounds. Every screen was therefore re-scored under both bounds as a graded residual
cleavage load, holding the hit set fixed so that only the scoring changed. Where a hit list reached
its cap, counts are right-censored and are reported as lower bounds.

**Availability.** All code, graded artefacts and per-design tables are released under a single
archived version [DATA AVAILABILITY DOI TO BE MINTED BEFORE SUBMISSION]. No result in this manuscript
requires network access or credentials to reproduce from that archive.

## 3 · Results

### 3.1 · Frame compatibility as the bound on junction space

Grading all 231 donor-exon × acceptor-exon pairs across the five partners returns 38 frame-compatible
junctions (Table 1, Figure 1). The refusals are structural: *NR4A3* exon 2 carries no
coding sequence and is refused in every pair, and exon 4 places the acceptor outside the plausible
resumption range in every pair, so all variance sits in the exon-3 column. Within that column,
frame compatibility reduces to a single arithmetic condition — a donor coding phase of 1 — which is
necessary and sufficient across all 231 rows.

Among these, *EWSR1* exon 12 joined to *NR4A3* exon 3 is the junction reported most often — type 1
in 10 of the 15 *EWSR1*-rearranged tumours of an 18-case series<sup>22</sup><!--PMID:12378528--> — so
designs against it address the largest documented patient group.

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
the variant fusion places the breakpoint at *TAF15* exon 6,<sup>23</sup><!--PMID:10537274--> and in a
series of 18 EMCs all three *TAF15*-rearranged tumours carried exon 6 joined to *NR4A3* exon
3<sup>22</sup><!--PMID:12378528--> — not exon 11. The exon-6 seam shares a single donor base with the exon-11 seam, so this oligonucleotide cannot
engage the *TAF15* junction that patients are reported to carry. That junction is itself
frame-compatible and yields five fusion-specific designs (43.8–50.0% GC), but its transcriptome
screen is not among the 12 reported here. For *FUS* no exon-resolved EMC breakpoint has been published at all.
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

On specificity the ordering inverts (Table 2). Ranking each junction by its highest-gap-margin
design, the best *TCF12* design carries two predicted gap-spanning near-matches, against a best of
eight across *EWSR1*, *TAF15* and *FUS*. Five of the eight *TCF12* junctions nonetheless score worse
than that FET best, so the distributions overlap and only the minima separate. Breadth and per-oligo specificity therefore point at different partners.

### 3.4 · Transcriptome load against a chance baseline

Twelve junctions across four of the five partners were screened, five designs at each. The gap-resolved
BLAST arm returned results for 58 of those 60; the two absences are transport failures at the remote
service, not results. Under the binary
assumption that a gap-internal mismatch abolishes cleavage, several designs score zero gap-spanning
risks; that assumption is not supported, and re-scoring the identical hit sets under both literature
bounds returns no design with zero predicted residual cleavage load.

That statement is arithmetically unavoidable. There are 1,129
16-mers within two substitutions of any given 16-mer, so an arbitrary transcriptome position matches
at ≥14/16 with probability 2.6 × 10⁻⁷; over a human RefSeq RNA set of order 10⁸–10⁹ nucleotides that
is 79–210 expected near-matches per oligonucleotide, for any 16-mer at all. A scrambled control and a
marketed gapmer of this length would return the same. Zero is not an achievable state, so a count of
zero-clean designs is a property of the threshold and the size of the transcriptome.

The informative quantity is load relative to chance (Table 2, Figure 3). The exhaustive
≤1-mismatch arm covers 70 designs: the 60 above, and ten at two modelled reference seams retained as
a base-composition control. Chance predicts 3.4–9.1 hits per 16-mer at this threshold; across
the 60 designs at real junctions the observed median is 2 and 49 carry load at or below the chance
upper bound. The two extreme values, 95 and 58, are both designs at one modelled seam and both at
81.2% GC, while the highest load at any real junction is 35. So the defensible specificity statement is not that designs are clean, but that
most carry no more transcriptome load than an arbitrary oligonucleotide of the same length, and that
the few that carry much more are predictable from base composition before synthesis.

Every gap-resolved count reported here is an upper bound of unknown tightness, because the BLAST arm
did not parse alignment orientation (Methods); counts that reached the hit-list cap are separately
right-censored lower bounds. Both are carried in Table 2 and neither is corrected for below.

### 3.5 · Near-match counts overstate the number of loci

These are counts of transcript records, not of genes, and the distinction cuts in the candidate's
favour. RefSeq carries one accession per annotated variant, so a match to a
constitutive exon of a multi-variant gene is counted once per variant. Recounting every screened hit
list per gene locus, over the 26 designs whose lists are not truncated, gives a median inflation of
2.25 transcript records per locus and a maximum of 7.0 — that is, a typical near-match count
overstates the number of distinct genes involved by rather more than twofold. The distinction also
separates observed from predicted sequence: RefSeq `NM_`/`NR_` records are curated, whereas
`XM_`/`XR_` are computationally predicted gene models, so a design whose load sits entirely in the
predicted namespace carries a different kind of liability from one that matches curated transcripts.
For the lead candidate 5′-GGGCATATCATCAAAC-3′ both effects apply and are large: its eight
gap-spanning near-matches are five variants of one uncharacterised locus, two predicted variants of
*DEPDC4* and one of *SGMS1* — three loci, and not one curated transcript among them. That is a
weaker liability than eight implies, and it is the kind of difference a count of accessions cannot
express.

## 4 · Discussion

Three findings stand, the second conditionally. Junction-spanning, parent-sparing designs exist at
every frame-compatible NR4A3 fusion junction, so the obstacle is not sequence availability. One
16-mer spans three partners' seams at once through a measured ten-base donor identity, which would
change the deployable artefact for an ultra-rare disease from *n* bespoke oligonucleotides to a stock
reagent — if patients carrying *TAF15* and *FUS* fusions prove to break at those exons, which the only
exon-resolved *TAF15* data published say they do not. And the partner offering that breadth is not
the partner offering the best predicted specificity.

The limiting step is discrimination, and it is not computable. The two available bounds on
single-mismatch RNase-H1 discrimination span one- to five-fold, and the pessimistic bound is the one
measured at the length used here.<sup>21</sup><!--PMID:7567450--> Under either, no design in this corpus is clean. No
amount of further sequence analysis narrows that interval; a measurement does. The field's own
answer to poor single-base discrimination has been positional chemical modification of the gap rather
than length,<sup>20</sup><!--PMID:23963702--> and that is the design direction this result points to. A steric-block
mechanism, which does not require gap-level discrimination, is a second alternative this work does not
evaluate.

Delivery remains unsolved for a tumour, and separates into three routes with different
requirements. A characterised EMC-enriched surface antigen is a prerequisite of
the systemic receptor-targeted route only; local and inhaled administration require none. EMC's
distant spread is lung-dominant, at 35–45% of patients and a median of approximately 28 months to
metastasis,<sup>24</sup><!--PMID:41055792--> and inhaled oligonucleotides have reached patients in non-oncology
indications, including an inhaled antisense oligonucleotide in phase 1<sup>25</sup><!--PMID:39500647--> — a
splice-switching oligonucleotide rather than an RNase-H1-active gapmer, so it establishes the route
and not the mechanism used here — and an inhaled
siRNA in phase 2b–3.<sup>26</sup><!--PMID:40028836--> Those agents target airway epithelium or parenchyma, which is the
compartment inhalation naturally reaches; a hypocellular, matrix-rich parenchymal sarcoma nodule is
not, and no retrieved record concerns a solid-tumour target. The route is therefore established in humans but not for
this compartment.

The experiment that would resolve the central uncertainty is routine and has been published in an
analogous disease: fusion-specific antisense oligonucleotides against *NAB2::STAT6* in solitary
fibrous tumour, evaluated against CRISPR-engineered isogenic fusion-positive and fusion-negative
cells, reduced fusion expression by 58% and proliferation by 22% in vitro.<sup>27</sup><!--PMID:37370737--> Applied here,
5′-GGGCATATCATCAAAC-3′ is the single highest-information reagent, because one synthesis tests both
the mechanism and the multi-partner prediction; its predicted load — eight gap-spanning near-matches at
three loci and one ≤1-mismatch transcriptome match (Table 2) — should travel with it.

Transferability depends on how that experiment is set up. The breakpoint of the cell line or patient sample must be established
at nucleotide resolution by RNA sequencing before any oligonucleotide is ordered: every design here
is specific to one exon pair, and none is valid for an unverified junction. A positive
control gapmer against an abundant housekeeping transcript in the same cells is required to separate
failed delivery from failed discrimination: a knockdown assay alone cannot distinguish them, and
discrimination is the failure mode this work predicts. The decision threshold should be fixed before
the experiment. The informative readout is fusion knockdown measured against wild-type *NR4A3*
knockdown in the same well; a selectivity below the approximately five-fold bound cited above would
falsify the gap-margin ranking on which every candidate here is ordered.

**Limitations.** Because the BLAST arm did not parse orientation, every gap-resolved count is an
upper bound of unknown tightness, and the rank ordering inherits that uncertainty; counts that
reached the hit-list cap are lower bounds in the opposite direction. Twenty-six of the 38
frame-compatible junctions are unscreened, including every *TFG* junction. The chance null is crude:
it assumes independent uniform bases, where real transcript sequence is composition-skewed and
repetitive, so it separates "more than chance" from "at chance" and nothing finer. Which exon pair a
given patient carries is not decidable from exon structure, so the multi-partner result is
conditional on *TAF15* and *FUS* breakpoints falling at the homologous exons — a clinical fact not
established here — and *TCF12::NR4A3* fusions are reported in
patients<sup>28,29</sup><!--PMID:11156374,12598313--> but not at the exon resolution these designs
require. Finally, both screens search mature transcript sequence only. RNase-H1 is active in the
nucleus and gapmers are known to engage pre-mRNA, so intronic and intron–exon-spanning sites are a
class of liability that neither the RefSeq RNA search nor the transcript-level exhaustive scan can
see; the counts reported here therefore bound the mature-transcript compartment only. That gap is
closable by a genomic screen and is not closed here.

## Tables

Tables 1 and 2 are in `fusion-junction-aso-submission-tables.md`, generated from the released
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
donor exon; green, acceptor exon; red, positions at which the three donors differ. The shaded box is
the target window of 5′-GGGCATATCATCAAAC-3′, with the 5-6-5 gapmer architecture below it. The three
donors are identical over the ten nucleotides before the breakpoint, which is what makes one
oligonucleotide junction-spanning at all three seams — and is the same identity that makes the
parent transcripts hard to discriminate from, so the gap-level margin of three is shown alongside.
Coverage is predicted from sequence and has not been measured.

**Figure 3. Transcriptome load per design against chance expectation.** Each bar is one design's
count of exact plus ≤1-mismatch matches over 186,185 transcripts, ranked. The band is the number of
such matches expected for an arbitrary 16-mer under an independent-uniform-base null (3.4–9.1);
55 of 70 designs fall at or below its upper bound, and the outliers are GC-rich, low-complexity
sequences at one modelled seam rather than a general property of junction designs. The band
separates "more than chance" from "at chance" and is not a significance test; the counts are
predictions from sequence search, not measured off-target activity.

## Declarations

**Data and code availability.** [ARCHIVE DOI TO BE MINTED.] Artifacts include the graded junction
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
than retained. The authors take full responsibility for the content, including for the correctness
of the code and for the interpretation of the results.

## References

*The 28 numbered entries are listed in `fusion-junction-aso-submission-references.md`, generated
from retrieved bibliographic records. Each superscript above carries its PubMed identifier in a
non-rendering comment, and the numbering is assigned from those identifiers by order of first
citation, so a superscript and its reference cannot drift apart.*
