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

**Authors.** [AUTHOR BLOCK TO BE COMPLETED BEFORE SUBMISSION — name, affiliation, ORCID,
corresponding address. This manuscript must not be submitted with this placeholder in place.]

**Running title.** Junction gapmers across NR4A3 fusions

**Keywords.** antisense oligonucleotide; gapmer; RNase H1; fusion transcript; NR4A3; extraskeletal
myxoid chondrosarcoma; sarcoma

---

## Abstract

**Background.** Extraskeletal myxoid chondrosarcoma (EMC) is an ultra-rare sarcoma defined by
rearrangement of *NR4A3* to a variable 5′ partner, most often *EWSR1* and in a substantial minority
*TAF15*. The chimeric mRNA carries a breakpoint seam present in no normal transcript, which makes it
the one tumour-exclusive feature of the disease at the RNA level. No junction-directed
oligonucleotide has been reported against any NR4A3 fusion.

**Methods.** We built chimeric transcripts at the mRNA level from canonical Ensembl transcript
models, retaining the acceptor exon in full, and graded every donor-exon × *NR4A3*-acceptor-exon pair
across four reported partners. Junction-spanning 16-mer 5-6-5 LNA/DNA/LNA gapmers were tiled over
each frame-compatible seam and screened against every partner transcript, then against human RefSeq
RNA by gap-resolved BLAST and against 186,185 transcripts by exhaustive ≤1-mismatch search.

**Results.** Of 207 graded exon pairs, 32 are frame-compatible, and all 32 yield at least one
junction-spanning gapmer that is not a perfect complement of any parent transcript. Designs against
*EWSR1* exon 12 joined to *NR4A3* exon 3 — the junction reported as type 1 in 10 of 18 tumours —
address the largest documented patient group. No design at any of the 12 junctions screened is free
of predicted gap-spanning near-matches, but that is a property of the threshold rather than of these
sequences: at 16-mer length, chance alone predicts 79–210 matches at ≥14/16 identity against the
human transcriptome, so no 16-mer can be free of them. Read against the applicable null, 55 of 70
designs carry off-target load at or below chance expectation, and the outliers are GC-rich and
low-complexity. Separately, one 16-mer spans the seams of *EWSR1* exon 12, *TAF15* exon 11 and *FUS*
exon 10 simultaneously through ≥10 identical donor bases; we report this as a sequence property and
not as a clinical one, because the only exon-resolved *TAF15::NR4A3* breakpoints published are exon
6, not exon 11.

**Conclusions.** Designability is not the limiting step for junction gapmers in NR4A3-rearranged
sarcoma, and neither is transcriptome load, which is at chance for most designs. The limiting step is
discrimination between the fusion and its parent transcripts at the catalytic gap, which is set by
enzymology and chemistry rather than by sequence search, and which no computation here resolves.

---

## 1 · Introduction

EMC is defined in the large majority of cases by an in-frame fusion of *EWSR1* to the orphan nuclear
receptor *NR4A3*, with *TAF15* accounting for a substantial minority and *TCF12*, *TFG* and *FUS*
reported rarely.<sup>1,2</sup> The genome is otherwise quiet, with few recurrent secondary
mutations,<sup>2</sup> so the fusion is to a first approximation the single clonal driver.

That driver is currently untargeted. Surgery with clear margins is the backbone of localised
disease, and for advanced disease no agent is approved specifically for EMC. The largest
EMC-specific prospective study, a single-arm phase 2 of pazopanib in centrally confirmed
*NR4A3*-translocated disease, returned four objective responses in 22 evaluable patients with a
median progression-free survival of 19 months (95% CI 11–27),<sup>24</sup><!--PMID:31331701--> and
first-line anthracycline-based chemotherapy returned four responses in ten evaluable patients in a
molecularly confirmed retrospective series.<sup>25</sup><!--PMID:24345066--> The population a
fusion-directed agent would address is, by contrast, close to the whole disease: across 58
molecularly confirmed cases, 79% carried *EWSR1::NR4A3*, 16% *TAF15::NR4A3* and 3%
*TCF12::NR4A3*.<sup>26</sup><!--PMID:36948401-->

Protein-directed approaches to this fusion face a structural problem. The *NR4A3* ligand-binding
domain is retained near-intact in the chimera and is identical in sequence to wild-type NR4A3, so a
ligand that engages it cannot distinguish fusion from wild type. That matters because NR4A3 has
tumour-suppressive roles of its own: combined *NR4A1*/*NR4A3* loss causes acute myeloid leukaemia in
mice,<sup>3</sup> and NR4A3 is tumour-suppressive in several tissues.<sup>4</sup> The chimeric mRNA
does not share this problem. Its breakpoint seam is a contiguous sequence absent from both parent
transcripts, so discrimination can in principle be enforced by base-pairing rather than by protein
conformation.

Targeting a fusion breakpoint with an oligonucleotide is not new. It is a continuous lineage from
1991,<sup>5</sup> including RNase-H-dependent antisense at a sarcoma fusion breakpoint in
1997,<sup>6</sup> the general fusion-exclusivity rationale stated as a principle in 2005,<sup>7</sup>
parental sparing demonstrated in at least four fusions,<sup>8–11</sup> a bi-shRNA against the
EWS/FLI1 junction taken into clinical testing,<sup>12,13</sup> and a GalNAc-conjugated
junction siRNA in fibrolamellar hepatocellular carcinoma that passed the delivery gate in a rare
fusion-driven cancer.<sup>14</sup> The contribution here is therefore not the modality. Across 5,153
unique records retrieved from Europe PMC, four mention *EWSR1::NR4A3* at title or abstract level;
those four are three papers, only one concerns EMC, and none is an oligonucleotide study. The count
of junction-directed oligonucleotide work against any NR4A3 fusion is zero.

Two questions follow that the field has not asked of this disease. First, the design lane has
addressed only *EWSR1*, while the partner varies — and partner identity is not clinically inert:
every reported objective response to an antiangiogenic tyrosine-kinase inhibitor in advanced EMC has
occurred in a non-*TAF15* patient, though the *TAF15* arm comprises three to five patients with zero
events and its Wilson upper bound remains compatible with equal response.<sup>15</sup> Second,
whether a junction oligonucleotide must be bespoke per patient, or whether one sequence can serve
more than one fusion, determines whether the deployable artifact for an ultra-rare disease is a stock
reagent or a panel.

## 2 · Materials and methods

**Transcript models.** Canonical transcripts for *EWSR1* (ENST00000397938), *TAF15*
(ENST00000605844), *TCF12* (ENST00000333725), *FUS* (ENST00000254108) and *NR4A3* (ENST00000395097)
were obtained from Ensembl. Each model was self-checked before use: exon lengths must sum to the
spliced cDNA, the CDS must occur exactly once within it, and translation of the CDS must reproduce
the annotated protein. Per-exon coding content was additionally cross-checked against an independent
exon audit for *EWSR1* and *NR4A3*; for the other three partners that audit does not exist, and the
weaker check is recorded per gene in the released artifacts.

**Chimera construction.** Chimeras were built at the mRNA level, not by concatenating coding
sequences: a fusion transcript retains the acceptor exon whole, so *NR4A3* exon-3 bases 5′ of its own
initiation codon are physically present in the transcript and are the bases an oligonucleotide meets
immediately 3′ of the seam. With *U* the number of retained untranslated acceptor-exon nucleotides
(*U* = 2, measured), the chimeric open reading frame is in frame when (donor coding nucleotides + *U*)
mod 3 = 0. Every declared exon pair was graded by this rule before any design was emitted, and a
panel was emitted only for a pair graded frame-compatible.

**Design.** Junction-spanning 16-mer gapmers were tiled in a 5-6-5 LNA/DNA/LNA architecture, retaining
only registers in which the seam falls inside the six-nucleotide DNA gap, since RNase-H1 cleaves
within the DNA:RNA duplex of the gap. Because discrimination is set by junction-unique bases inside
the gap rather than across the whole oligonucleotide, we report a gap-level margin — the number of
junction-unique bases inside the gap on the shorter side — and rank by it. Each candidate was tested
against all five partner transcripts, not only the two parents of its own fusion, because the FET
family donors are paralogues with similar low-complexity amino-termini.

**Specificity screening.** Two independent screens were applied. A gap-resolved screen queried each
target window against human RefSeq RNA (blastn-short, low-complexity filter off, ≥14/16 identity) and
classified each near-match by whether the six-nucleotide gap was fully base-paired. An exhaustive
seed-and-extend scan then searched 186,185 transcripts (GRCh38.p14) for exact and ≤1-mismatch matches;
this arm is complete for substitutions by construction and does not detect insertions or deletions.
Target-site accessibility was estimated as mean unpaired probability over a truncated 180-nucleotide
local fold, and is reported as a weak correlate rather than a potency ranking.

**Discrimination model.** The binary assumption that any mismatch inside the gap abolishes cleavage
is not supported by the primary literature and is not used for any claim of cleanliness. Measured
discrimination for an unmodified RNase-H-active oligonucleotide is approximately
five-fold,<sup>16</sup> and at 16-mer length one study reports no efficient discrimination at
all.<sup>17</sup> Every screen was therefore re-scored under both bounds as a graded residual
cleavage load, holding the hit set fixed so that only the scoring changes. Where a hit list reached
its cap, counts are right-censored and are reported as lower bounds.

**Availability.** All code, graded artifacts and per-design tables are released under a single
archived version [DATA AVAILABILITY DOI TO BE MINTED BEFORE SUBMISSION]. No result in this manuscript
requires network access or credentials to reproduce from that archive.

## 3 · Results

### 3.1 · Frame compatibility as the bound on junction space

Grading all 207 donor-exon × acceptor-exon pairs across the four partners returns 32 frame-compatible
junctions (Table 1). The refusals are structural rather than selective: *NR4A3* exon 2 carries no
coding sequence and is refused in every pair, and exon 4 places the acceptor outside the plausible
resumption range in every pair, so all variance sits in the exon-3 column. Within that column,
frame compatibility reduces to a single arithmetic condition — a donor coding phase of 1 — which is
necessary and sufficient across all 207 rows.

Every one of the 32 frame-compatible junctions yields at least one junction-spanning gapmer that is
not a perfect complement of any of the five parent transcripts, at GC contents largely inside the
conventional design band (25.0–75.0% across partners). Finding candidate sequences is therefore not
the constraint on this modality in this disease.

### 3.2 · Cross-partner coverage by a single oligonucleotide

Nine designs span the seam of more than one junction exactly, and all nine draw from *EWSR1*, *TAF15*
and *FUS* (Figure 1). Five cover the same three-partner set, differing only in register across the
seam. The best by gap-level margin is 5′-GGGCATATCATCAAAC-3′ (43.8% GC, gap-level margin 3), which
divides eight donor and eight acceptor bases at the seam of *EWSR1* exon 12, *TAF15* exon 11 and
*FUS* exon 10 joined to *NR4A3* exon 3, and occurs in none of the five wild-type parent transcripts.
The mechanism is measured: these donors are identical over at least the ten bases immediately 5′ of
their breakpoints, which is longer than the donor-side contribution of any of the five designs and is
the arithmetic requirement for the coverage to be possible.

The clinical reading of this result is weak, and in one respect the published data contradict it.
The only exon-resolved *TAF15::NR4A3* breakpoints reported in EMC are exon 6 — in both cases of
one series<sup>24</sup> and in all three fusion-positive tumours of another<sup>25</sup> — not exon
11. The exon-6 seam shares no donor sequence with the exon-11 seam, so this oligonucleotide cannot
engage the *TAF15* junction patients are actually reported to carry, and we screened *TAF15* exon 6
separately for that reason. For *FUS* no exon-resolved EMC breakpoint has been published at all.
The three-partner result is therefore a statement about FET-family sequence architecture and a
hypothesis about junctions not yet observed; it is not a claim that one reagent serves three patient
groups. Testing it requires breakpoint sequencing of archival *TAF15*- and *FUS*-positive cases.

The same paralogy that permits this coverage is a specificity liability, which is why candidates were
screened against every partner transcript rather than two. One sequence property is being read twice.

### 3.3 · The non-FET partner: coverage and specificity

*TCF12* is the one partner in this panel that is not a FET-family protein, and it appears in none of
the nine multi-partner sets; it reaches only a weaker tier in which mismatches are tolerated in the
oligonucleotide wings. Partner membership was never a criterion in the ranking, and *TCF12* was
included because it is a reported EMC partner. We note that this consistency check had little power
to fail: any non-homologous donor would be excluded, so the observation does not by itself separate
FET paralogy from incidental exon homology. The stronger evidence for paralogy is that four
additional two-partner sets are also FET-only.

On specificity the ordering inverts (Table 2). The best *TCF12* design carries one predicted
gap-spanning near-match, against a best of eight across *EWSR1*, *TAF15* and *FUS*. Four of the eight
*TCF12* junctions nonetheless score worse than the FET best, so the distributions overlap and only
the minima separate. Breadth and per-oligo specificity therefore point at different partners.

### 3.4 · Transcriptome load against a chance baseline

Twelve junctions across all four partners were screened, comprising 58 designs. Under the binary
assumption that a gap-internal mismatch abolishes cleavage, several designs score zero gap-spanning
risks; that assumption is not supported, and re-scoring the identical hit sets under both literature
bounds returns no design with zero predicted residual cleavage load.

That statement is arithmetically unavoidable and should not be read as a finding. There are 1,129
16-mers within two substitutions of any given 16-mer, so an arbitrary transcriptome position matches
at ≥14/16 with probability 2.6 × 10⁻⁷; over a human RefSeq RNA set of order 10⁸–10⁹ nucleotides that
is 79–210 expected near-matches per oligonucleotide, for any 16-mer at all. A scrambled control and a
marketed gapmer of this length would return the same. Zero is not an achievable state, so a count of
zero-clean designs is a property of the threshold and the size of the transcriptome.

The informative quantity is load relative to chance (Table 2). At the ≤1-mismatch threshold chance
predicts 3.4–9.1 hits per 16-mer; the observed median across 70 designs is 2, and **55 of 70 carry
load at or below the chance upper bound**. The outliers are the GC-rich, low-complexity designs at
the modelled reference seam, reaching 58 and 95 — a base-composition effect rather than a property of
the junction. So the defensible specificity statement is not that designs are clean, but that most
carry no more transcriptome load than an arbitrary oligonucleotide of the same length, and that the
few that carry much more are identifiable and avoidable.

Four further qualifications bound this, and the first is the most serious. The BLAST arm did not
parse alignment orientation. `blastn` searches both strands, and a transcript carrying the reverse
complement of the target window cannot be hybridised by an antisense oligonucleotide, so it is not a
liability at all — yet such hits passed the identity filter and, where they spanned the catalytic
gap, were recorded as cleavage risks. The defect was found by a contradiction between our own two
screens: at one junction a design returns five perfect 16/16 BLAST matches to a transcript that the
exhaustive ≤1-mismatch scan, which searches the sense orientation only, reports as absent. Both
cannot be true. Orientation is now parsed, but the committed screens predate the fix and cannot be
retro-corrected without re-running, so **every gap-resolved count reported here is an upper bound of
unknown tightness**, and the rank ordering inherits that uncertainty. Counts that reached the
hit-list cap are separately right-censored lower bounds. Twenty of the 32 frame-compatible junctions
are unscreened. The null above is likewise crude — it assumes independent uniform bases, where real
transcript sequence is composition-skewed and repetitive — and is used only to separate "more than
chance" from "at chance", never as a significance test.

The fourth qualification is that these are counts of transcript records rather than of genes, and it
cuts in the candidate's favour. RefSeq carries one accession per annotated variant, so a match to a
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

Three findings survive their own caveats. Junction-spanning, parent-sparing designs exist at every
frame-compatible NR4A3 fusion junction, so the obstacle is not sequence availability. One
16-mer addresses three partners' junctions at once by a measured sequence identity, which changes the
deployable artifact for an ultra-rare disease from *n* bespoke oligonucleotides to a candidate stock
reagent. And the partner offering that breadth is not the partner offering the best predicted
specificity.

The limiting step is discrimination, and it is not computable. The two available bounds on
single-mismatch RNase-H1 discrimination span one- to five-fold, and the pessimistic bound is the one
measured at the length used here.<sup>17</sup> Under either, no design in this corpus is clean. No
amount of further sequence analysis narrows that interval; a measurement does. The field's own
answer to poor single-base discrimination has been positional chemical modification of the gap rather
than length,<sup>16</sup> and that is the design direction this result points to. A steric-block
mechanism, which does not require gap-level discrimination, is a second alternative this work does not
evaluate.

Delivery remains unsolved for a tumour, and is best described as three routes with different
requirements rather than one gate. A characterised EMC-enriched surface antigen is a prerequisite of
the systemic receptor-targeted route only; local and inhaled administration require none. EMC's
distant spread is lung-dominant, at 35–45% of patients and a median of approximately 28 months to
metastasis,<sup>18</sup> and inhaled oligonucleotides have reached patients in non-oncology
indications, including an inhaled antisense oligonucleotide in phase 1<sup>19</sup> and an inhaled
siRNA in phase 2b–3.<sup>20</sup> Those agents target airway epithelium or parenchyma, which is the
compartment inhalation naturally reaches; a hypocellular, matrix-rich parenchymal sarcoma nodule is
not, and no retrieved record concerns a solid-tumour target. The route is deliverable in humans. That
is not evidence it reaches this tumour.

The experiment that would resolve the central uncertainty is routine and has been published in an
analogous disease: fusion-specific antisense oligonucleotides against *NAB2::STAT6* in solitary
fibrous tumour, evaluated against CRISPR-engineered isogenic fusion-positive and fusion-negative
cells, reduced fusion expression by 58% and proliferation by 22% in vitro.<sup>21</sup> Applied here,
5′-GGGCATATCATCAAAC-3′ is the single highest-information reagent, because one synthesis tests both
the mechanism and the multi-partner prediction; it carries eight predicted gap-spanning near-matches
at three gene loci, none of them a curated transcript, and one ≤1-mismatch transcriptome match, and
those numbers should travel with it.

Three elements make that experiment transferable, and stating them is the point of publishing
designs rather than a method. The breakpoint of the cell line or patient sample must be established
at nucleotide resolution by RNA sequencing before any oligonucleotide is ordered: every design here
is specific to one exon pair, and none is valid for an unverified junction. A transfection-competent
positive control — a gapmer against an abundant housekeeping transcript in the same cells — is
required to separate failed delivery from failed discrimination, since discrimination is the failure
mode this work predicts and the two are indistinguishable from a knockdown assay alone. And the
decision threshold should be fixed before the experiment: the informative readout is fusion
knockdown measured against wild-type *NR4A3* knockdown in the same well, and a selectivity below the
approximately five-fold bound cited above would not merely underperform, it would falsify the
gap-margin ranking on which every candidate here is ordered.

Three limits are structural. Which exon pair a given patient carries is not decidable from exon
structure, so the multi-partner result is conditional on *TAF15* and *FUS* breakpoints falling at the
homologous exons — a clinical fact not established here. *TCF12::NR4A3* fusions are reported in
patients<sup>22,23</sup> but not at the exon resolution these designs require. And both screens
search mature transcript sequence only. RNase-H1 is active in the nucleus and gapmers are known to
engage pre-mRNA, so intronic and intron–exon-spanning sites are a class of liability that neither
the RefSeq RNA search nor the transcript-level exhaustive scan can see; the counts reported here are
therefore bounds on the mature-transcript compartment rather than on the transcriptome a gapmer
actually meets. That gap is closable by a genomic screen and is not closed here.

## Declarations

**Data and code availability.** [ARCHIVE DOI TO BE MINTED.] Artifacts include the graded junction
atlas, per-junction design panels, both specificity screens per junction, the graded re-scores under
both discrimination bounds, and the retrieval records for every literature claim.

**Provenance and corrections.** An earlier version of these analyses placed the acceptor seam
incorrectly through a coding-versus-transcript exon indexing error and was withdrawn in full; all
panels were rebuilt and verified against two independent transcript acquisitions. The complete
correction record, including every superseded value, is released with the archive.

**Competing interests.** [TO BE COMPLETED.]

**Funding.** [TO BE COMPLETED.]

**Ethics.** No human subjects, human material or animals were involved. All clinical figures are
taken from published aggregate data and are cited.

**Use of AI tools.** [TO BE COMPLETED — disclose per journal policy.]

## References

*Numbered entries are generated from retrieval records and are listed in
`fusion-junction-aso-references.md`. Citation superscripts above are placeholders pending final
numbering against that list.*
