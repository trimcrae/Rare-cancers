---
id: DOC-FUSION-JUNCTION-ASO-NAT-CANDIDATE-2026-09-04
title: "NR4A3 fusion-junction antisense gapmers for extraskeletal myxoid chondrosarcoma: reagents, test articles and a pre-registrable knockdown experiment"
level: L3
kind: manuscript
status: live
purpose: >
  A tightened NAT candidate for author review, derived from the current journal article.
  It preserves the scientific results and sources and has not been submitted or deposited.
scope: >
  Computational design and specificity screening only; no laboratory validation,
  efficacy, safety, delivery or clinical readiness is established.
audience: [external reviewers, collaborators, maintainers]
date: 2026-09-04
last_verified: 2026-09-04
related: [DOC-FUSION-JUNCTION-ASO-JOURNAL]
---

# *NR4A3* fusion-junction antisense gapmers for extraskeletal myxoid chondrosarcoma: reagents, test articles and a pre-registrable knockdown experiment

**Author.** Tristan D. McRae

*Independent researcher, unaffiliated.* Correspondence: trimcrae@gmail.com
ORCID: [0000-0002-1823-1451](https://orcid.org/0000-0002-1823-1451)

**Running title.** NR4A3 junction gapmers for EMC

---

## Abstract

Extraskeletal myxoid chondrosarcoma (EMC) is an ultra-rare sarcoma usually defined by an
in-frame *NR4A3* fusion. That junction is in no normal transcript, so an antisense
gapmer could in principle cleave it, sparing its parents; none is reported for any
*NR4A3* fusion in the literature retrieved. This computational work performs the in-silico half of step one of an off-target
framework; every sequence named is a research reagent not for administration. It names what a laboratory needs: two reagents at the most-reported
breakpoints, 5′-GGGCATATCATCAAAC-3′ at *EWSR1* exon 12 and 5′-GGGCATATCTTGTGTG-3′ at
*TAF15* exon 6, both to *NR4A3* exon 3, longest wild-type parent gap duplexes eight and nine base
pairs; two screened controls; a pre-registrable selectivity threshold. Both come from a panel of 190 junction-spanning 16-mers tiled 5-6-5 across 38 in-frame junctions: 87 let a mature wild-type
parent pair their whole catalytic gap over ten or more contiguous base pairs, and for 61 the longest is wild-type *NR4A3*. Ten is a convention, not a measurement: exon-terminus chimeras meet the same screen
at 40.6% against the panel's 45.8%. Five test articles are named; the two fusion-positive EMC cell
models are reported at an *NR4A3* exon-2 acceptor, not this panel's. The design procedure is released.

## Keywords

**Keywords.** antisense oligonucleotide; gapmer; RNase-H1; fusion transcript; NR4A3; extraskeletal
myxoid chondrosarcoma; off-target screening

---

## Introduction

Most EMC carries an in-frame *EWSR1*::*NR4A3* fusion;<sup>1</sup><!--PMID:8634690-->
*TAF15* is a substantial minority partner and *TCF12* and *TFG* are rare.<sup>2</sup><!--PMID:32572850-->
*FUS*, reported in two of five variant cases in a recent series,<sup>3</sup><!--PMID:41755350-->
supplies eight modelled junctions here. Conventional cytotoxic chemotherapy has limited
activity,<sup>4</sup><!--PMID:41055792--> though responses occur.<sup>5</sup><!--PMID:24345066-->
Disease control exceeded response with a trialled tyrosine-kinase inhibitor: this interpretation
uses the review's response categories,<sup>4</sup><!--PMID:41055792--> not a figure stated in the
trial report.<sup>6</sup><!--PMID:31331701-->

A fusion-junction gapmer could recruit RNase-H1 to cleave tumour RNA while sparing the normal
parents. Junction-directed nucleic-acid agents have been reported against at least six fusion
oncogenes: two as antisense oligonucleotides and the remainder as RNA-interference agents,
including one expressed from a lentiviral vector.<sup>7,8,9,10,11,12</sup><!--PMID:1794439,9049825,33241214,21846246,23052253,37980543-->
None against an *NR4A3* fusion was found in the literature retrieved.

Each parent supplies roughly half the junction sequence. Such matches often fall outside a
conventional off-target search's mismatch budget but may pair the catalytic gap. We therefore
screen that pairing directly. RNase-H1's reported minimum DNA gap is six nucleotides, with seven
to ten the working range.<sup>13</sup><!--PMID:24981949--> Our criterion instead concerns a
ten-base-pair contiguous duplex through the whole six-nucleotide gap. Ten is an adopted hybridisation
criterion, not a measured cleavage threshold or a gap-length requirement. We also adopt, without
establishing, the premises that incomplete overall pairing can permit cleavage and that wing
mismatches are less protective than gap mismatches. Of the five steps in a 2025 industry off-target
framework,<sup>14</sup><!--PMID:39912803--> this work performs only the in-silico half of step one;
transcriptomics is not performed. The Discussion proposes a parent-selectivity measurement related
to step three.

## Materials and Methods

All analyses use public data; no laboratory work was performed. Complete parameters, per-design
tables and claim bounds are archived. Canonical transcripts of five partners and *NR4A3* were
obtained from Ensembl.<sup>15</sup><!--PMID:39656687--> We tiled 16-mers in 5-6-5
β-D-oxy-locked-nucleic-acid/DNA/β-D-oxy-locked-nucleic-acid geometry,<sup>13</sup><!--PMID:24981949-->
giving five registers per junction with the breakpoint inside the DNA gap. Six is the cited minimum,
not the preferred gap length; the genome-wide arm is available only for 16-mers. Gap-level margin
counts junction-unique gap bases on the shorter side of the breakpoint.

Five screens examine human RefSeq RNA alignments; an exhaustive transcript substitution search
within one mismatch; unspliced parents; the longest contiguous duplex through the gap in six mature
wild-type parents; and unambiguous GRCh38, including mitochondrial sequence. This adopted scope
covers mature, precursor, exon-exon, non-coding and mitochondrial sequence. A near-match pairs at
least 14 of 16 positions. Parent liability requires a contiguous run of at least ten base pairs
pairing the whole gap. Ten identically screened null ensembles comprise four shuffles, two
base-frequency draws (uniform or composition-matched), and four real-parent chimeras, two joined
at exon termini.

Alignments were re-scored by nearest-neighbour stability of the longest contiguous paired run;
only energy separations are reported. Melting-temperature calculations assume unmodified DNA:RNA
at 250 nM strand,<sup>16</sup><!--PMID:7545436--> not locked phosphorothioate chemistry. Accordingly,
we report no absolute melting temperature for the proposed reagents. Table 1 gives the
unmodified-hybrid model's fusion-versus-parent difference. LNA and phosphorothioate effects
are unmodelled; this difference is not a validated bound for the modified chemistry.

## Results

### The reagents

We select the highest-margin designs at the two most-prevalent junctions with published
exon-resolved breakpoints: 5′-GGGCATATCATCAAAC-3′ for *EWSR1* exon 12 and
5′-GGGCATATCTTGTGTG-3′ for *TAF15* exon 6, both to *NR4A3* exon 3 (Table 1).
Exon indices count from the transcript 5′ end, including non-coding exons; coding-exon numbering
can select a different reagent. Both have gap-level margin three.

Their longest wild-type duplexes pairing the whole gap are eight and nine base pairs,
respectively, both against *TFG*. Thus both are liable at an eight-base-pair cut, the *TAF15*
reagent remains liable at nine, and neither is liable at ten. Both also pair part of the gap at
the wild-type *NR4A3* exon-2/exon-3 seam; these unmeasured partial duplexes are not counted.
A one-base register shift can reverse the verdict: 5′-AGGGCATATCTTGTGT-3′, adjacent to the
*TAF15* reagent, pairs 11 base pairs of wild-type *NR4A3* through the whole gap and cannot
substitute for it.

At a deeper-than-default search ceiling, the *EWSR1* and *TAF15* reagents have 123 and eight
gap-paired sense-strand transcript near-matches, but six and five gene loci. Most of the 123 are
predicted transcript models. The *EWSR1* reagent also matches wild-type *TAF15* precursor RNA
across an intron-exon boundary with two mismatches, one in the gap. Ten shared donor bases let
this reagent span *EWSR1*, *TAF15* and *FUS* breakpoints (Figure 1). The *TAF15* reagent has no
sense-strand precursor site.

Aggregate genome-wide loads are similar: 156 and 135 hybridisable gap-paired sites. The *EWSR1*
reagent has one exact 16-base genomic match, intronic in annotated lncRNA ENSG00000304430; the
*TAF15* reagent has none. These are sequence predictions, not measured activity. Much genomic
sequence is untranscribed; transcription and cleavage at these sites are unmeasured.

Both reagents are phosphorothioate throughout, with five contiguous β-D-oxy-locked residues per
wing, exceeding the two to four taken here as usual. Their high affinity may permit more
mismatches than the near-match screens' two-mismatch ceiling. Both begin with a locked 5′-GGG
tract. Increased sequence-dependent hepatotoxicity with high affinity is an adopted, untested
premise here, not a retrieved finding. Neither reagent's potency or safety is established.

Combining the breakpoint distribution of an 18-case series<sup>17</sup><!--PMID:12378528-->
with a 58-case cohort<sup>18</sup><!--PMID:36948401--> assigns 68.4% of molecularly confirmed cases
to these two junctions. This is modelled coverage, not patient screening. Its 39.9%–82.8% range
is not a confidence interval: two of four inputs are fixed, no nominal level is assigned, and
the calculation transfers a breakpoint distribution between cohorts collected 21 years apart.
The *TAF15* arm uses three of three reported breakpoints, an upper bound. Adding the top-margin
*EWSR1* exon-13/*NR4A3* exon-3 design, 5′-GGGCATATCTCCACGG-3′, would raise modelled coverage
to 79.0%; selection names only the first two junctions by reported prevalence.

### Selection from a panel of 190 designs

Across 38 in-frame junctions of five partners, 87 of 190 designs let a mature wild-type parent
pair the whole gap over at least ten contiguous base pairs. The longest duplex is with *NR4A3*
for 61; 85 pair one of their own two parents. Only seven of the 87 reach the conventional
14-of-16 near-match threshold, and parent records are excluded by name from that screen.
Nineteen designs have sense-strand precursor near-matches pairing the whole gap. The mature-parent
and precursor union is 93 designs, not their sum. Gap mismatches score zero, so these counts
bound the fully paired class, not all parent liability.

Alignment-screen cleanliness has additional bounds: seven searches never returned and censoring
leaves only 47 of 183 returned searches assessable. A clean count is a floor over that subset;
most default-clean designs fail a deeper search. Parent, precursor and genome screens cover all
190 without failures or censoring.

Energy re-scoring finds eight designs with fully paired 16-base off-target duplexes and 45 with
a duplex within 2 kcal/mol of the intended target. Neither named reagent is in these classes;
their nearest separations are 3.2 and 3.0 kcal/mol. These are upper bounds because the
longest-run calculation ignores pairing on either side of a mismatch.

Longer gaps retain parent liability: counts are 87, 88 and 87 in panels of 190, 266 and 342,
respectively, reducing rates from 45.8% to 33.1% and 25.4% without removing the problem.
At 5-10-5, whole-gap pairing itself requires ten base pairs; shorter runs potentially compatible
with the reported seven-to-ten working range are missed, making 25.4% a floor.

Three designs clear every screen at the ten-base-pair cut. Two have no full-gap parent duplex
at any length; the third pairs wild-type *NR4A3* over eight bases. None targets a reported patient
junction, so these are mechanism controls. Within-junction selection instead finds a parent-clear
design for 35 of 38 junctions and all five with published exon-resolved breakpoints. At cuts of
nine, eight, seven and six base pairs, those counts become 31/3, 23/2, 9/0 and 6/0
(all junctions/published junctions). These cuts measure whole duplexes, not DNA gap length;
the named *TAF15* junction loses its best design at nine.

Exon-terminus chimeras meet the parent-liability criterion at 40.6%, versus 45.8% for the panel.
The strongest null falls inside the panel's 95% interval at cuts seven through thirteen except
eleven; the excess changes sign four times across cuts six through thirteen. Both panel and
chimeras contain mostly junctions unreported in patients. The comparison therefore does not
resolve a disease-specific excess over the liability generated by joining these genes' exon termini.

### Test articles

Five test articles offer complementary routes. The panel joins donors to *NR4A3* exon 3, its
first coding exon, whereas two patient-derived cell models are reported at exon 2. No annotated
*NR4A3* transcript has exon 2 as its first coding exon, so annotation does not reconcile them.
The original protein-fusion filter excluded acceptors upstream of the initiation codon; that
filter is inappropriate for RNase-H1 gapmers, which cleave RNA independently of reading frame.
An *EWSR1* exon-7/*NR4A3* exon-2 fusion was sequenced in one of five *EWSR1*-rearranged tumours
in a transcriptome series,<sup>19</sup><!--PMID:29937513--> and a *PGR*::*NR4A3* case joins
exon 2 to the *NR4A3* 5′ untranslated region.<sup>20</sup><!--PMID:36103645--> All retrieved
exon-resolved acceptors are exon 2, exon 3 or a cryptic exon in intron 2;<sup>21</sup><!--PMID:31020999-->
none is downstream of exon 3, where no patient-grounded designs are made.

Three engineered constructs come from a functional study reporting their exon spans.<sup>21</sup><!--PMID:31020999-->
Two, E-N and T-N*, carry exactly the named reagents' junctions. Rebuilding them offers a direct
test of junction-selective knockdown, but heterologous complementary-DNA overexpression cannot
establish activity at an endogenous locus.

The two patient-derived, identity-clean models are USZ20-EMC1 (RRID:CVCL_C6MX) and USZ22-EMC2
(RRID:CVCL_C6MY), the only fusion-positive EMC cell source identified here.<sup>22</sup><!--PMID:36316541-->
They are available on request, with no repository deposit and reported doubling times of five
to six days. Their reported junctions join *EWSR1* exon 13 and *TAF15* exon 6 to *NR4A3*
exon 2. The report supplies no sequenced boundary, transcript accession or junction sequence;
whether this denotes a non-coding acceptor or unsupported numbering cannot be determined.
An earlier version of this work was withdrawn after this class of indexing error.

A first-coding-exon acceptor is more parsimonious for the defining chimeric transcription
factor.<sup>1,21</sup><!--PMID:8634690,31020999--> A non-coding exon-2 acceptor would instead
retain the *NR4A3* initiation codon under the donor promoter. On the former interpretation,
USZ22-EMC2 matches the named *TAF15* reagent and USZ20-EMC1 matches the third, exon-13 design.
This remains inference. The builder emits exon-2 acceptors only for published patient seams
or user-supplied sequencing checked against its transcript models.

Alternative exon-2 reagents are 5′-AGTGGGCTCTCCACGG-3′ (*EWSR1* exon 13) and
5′-AGTGGGCTCTTGTGTG-3′ (*TAF15* exon 6), both at top margin and below the ten-base-pair
criterion. Their longest full-gap parent duplexes are eight bases with *EWSR1* and nine with
*NR4A3*, respectively. The latter directly involves the acceptor used in the selectivity ratio.
Reagents cannot be exchanged between acceptors.

Establish the test article's breakpoint at nucleotide resolution by RNA sequencing before
ordering: only nine of 176 distinct panel sequences match multiple junctions. Routine
break-apart *NR4A3* fluorescence in situ hybridisation detects rearrangement regardless of
partner,<sup>4</sup><!--PMID:41055792--> not the nucleotide seam.

### Controls for the knockdown experiment

Table 2 gives a dinucleotide-preserving scramble of each reagent, screened against mature
parents. Among such scrambles, 10.0% pair a parent's whole gap over at least ten bases and
3.9% have the longest duplex with *NR4A3*. Passing this screen is necessary for these controls;
it does not establish inertness.

## Discussion

### The falsification experiment

We propose isogenic fusion-positive/fusion-negative comparisons, as used for *NAB2::STAT6*
in solitary fibrous tumour,<sup>23</sup><!--PMID:37370737--> with the screened controls.
Knockdown alone cannot distinguish the relevant failure modes.

Selectivity is wild-type *NR4A3* knockdown IC50 divided by fusion knockdown IC50, from matched
dose responses in the same wells. This ratio and its threshold of 5.0 are adopted conventions,
not specified by framework step three.<sup>14</sup><!--PMID:39912803--> With an assumed replicate
standard deviation of 0.35 for the natural-log selectivity ratio, six independent biological
replicates give about 80% power to falsify true selectivity of 3; three give about 30%.
Variance is unmeasured.

Above a realised standard deviation of approximately 0.65 at three replicates, 1.53 at six or
2.25 at ten, no observed ratio at least one can place a two-sided 95% interval's upper limit
below 5. Such a test can fail only with an anti-selective result and is treated as void.
A normal-approximation interval would change these figures. Apply the gate to the upper
confidence bound on a pilot's standard deviation: at or above the threshold for the proposed
replicate count, increase replication or do not test. An acceptor-only ratio cannot exclude
other parent liabilities; measure *TFG* alongside *NR4A3*, given its eight- and nine-base
full-gap duplexes with the named reagents.

### Interpretation and limits

Every modelled in-frame junction is designable; discrimination remains unproven. A design's own
parents pair at most 13 bases across mature and precursor compartments, whereas eight off-target
duplexes pair all 16, five in curated records. This is no liability ranking: the parent screen
reads six transcripts and the energy screen excludes parents. Mature-parent liability requires
a ten-base full-gap duplex; precursor liability requires a full-gap near-match within two
mismatches. These are distinct, overlapping classes.

The archive additionally screens the patient's unrearranged *NR4A3* allele. Its two-mismatch
ceiling gives a lower bound. No selected design fails, but two other registers at the *EWSR1*
exon-13/*NR4A3* exon-2 seam do, reinforcing the register hazard.

Four cited junction-specificity reports tested synthesised molecules;<sup>9,10,11,24</sup><!--PMID:33241214,21846246,23052253,36265509-->
we did not survey design pipelines and claim no priority for pre-synthesis screening.
Whether sparing wild-type *NR4A3* justifies a specificity cost remains unsettled: reported
paralogue redundancy and dosage effects point in opposite directions.

All five screens predict hybridisation, not duplex formation or cleavage. Junction-directed
oligonucleotides are established; the new application here is the indication. No potency,
therapeutic window or safety has been measured, and systemic delivery to solid tumours remains
unresolved. All named test articles require cell culture; none establishes clinical readiness.

## Acknowledgments

No person other than the author contributed to this work.

## Author Contributions

T.D.M. conceived and directed the project and is responsible for its content. AI assistance
with analysis and manuscript preparation is disclosed below.

## Statements and Declarations

**Research use only, and not for administration to any person or animal.** Every sequence is
an unsynthesised, untested laboratory reagent. Order only from `fusion-junction-aso-sequences.csv`,
which specifies sequence, locked residues and backbone, after RNA sequencing establishes the
test article's breakpoint at nucleotide resolution.

**Ethical considerations.** Not applicable; no human subjects, human material or animals were
involved, and no ethics approval was required.

**Consent to participate.** Not applicable; no participants were enrolled.

**Consent for publication.** Not applicable; no individual-level data are reported.

**Declaration of conflicting interest.** No competing financial interests exist. The author
holds no patent, patent application, equity or consultancy relating to any sequence or method
described here. One non-financial interest is declared: the author is a survivor of extraskeletal
myxoid chondrosarcoma, the disease this work addresses.

**Funding statement.** No external funding; self-funded by the author.

**Use of artificial intelligence.** Claude (Anthropic) assisted with analysis code, screens,
literature retrieval and checking, and manuscript drafting and review. GPT-6-Astra (OpenAI)
assisted with this revision and checks against repository artefacts. Bibliographic records
were retrieved from PubMed, Europe PMC or Crossref rather than generated, and citations were
checked against those records. The author directed the work and is responsible for its content.

**Data availability.** Code, per-design tables and screen parameters for the preceding analysis
are archived at [doi:10.5281/zenodo.22229096](https://doi.org/10.5281/zenodo.22229096).
This revision does not claim that the archived files contain its corrected interpretations.
The accompanying sequence record (Supplementary File 1) and revision note (Supplementary File 2)
correct the melting-temperature interpretation and qualify cell-model correspondence;
sequence rows and numerical model outputs are unchanged.
An earlier analysis mislocated the acceptor through coding-versus-transcript exon indexing
and was withdrawn in full. Rebuilt, verified panels and the correction record are archived.

## References
## Tables

Tables 1 and 2 are in `fusion-junction-aso-journal-tables.md`, generated from the canonical
sequence file and its screened-control source.

## Figure legends

**Figure 1. One 16-mer spans three partners' breakpoints; only one is reported in patients.**
Breakpoint-aligned windows join *EWSR1* exon 12, *TAF15* exon 11 and *FUS* exon 10 to *NR4A3*
exon 3, with reporting status for each row. The *TAF15* exon-11 row differs from Table 1's
exon-6 reagent: it is an additional breakpoint spanned by the *EWSR1* reagent, not a selected reagent.
