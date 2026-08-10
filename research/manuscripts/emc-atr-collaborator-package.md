---
id: DOC-EMC-ATR-COLLABORATOR-PACKAGE
title: "Untranslated NR4A3 sequence encodes a 59-residue insertion in the EWSR1 exon 7 to NR4A3 exon 2 fusion of extraskeletal myxoid chondrosarcoma, and a donor-exon phase rule for the reported junctions"
level: L3
kind: manuscript
status: live
canonical_for:
  - the reported transcript-level junctions of the NR4A3 fusions of extraskeletal myxoid chondrosarcoma
  - the counted frequency of each reported EMC fusion type, and the sources those counts come from
  - the donor-exon phase rule governing the reading frame of an EWSR1::NR4A3 junction
  - the 59-residue insertion the NR4A3 exon 2 acceptor contributes, at nucleotide resolution
  - the transcript-level open reading frames those junctions produce, and their in-frame self-checks
  - the placement of EMC's fusions on the published retained-RGG recruitment axis
  - the computed classification of TCF12 as a non-FET 5' partner
  - the pre-specified DSB-recruitment predictions and their falsifiers
purpose: >-
  Establish the reading frame of every reported NR4A3-fusion junction of extraskeletal myxoid
  chondrosarcoma from public reference transcripts, state the rule that governs it, report the
  59-residue insertion the exon 2 acceptor contributes at nucleotide resolution, and set out the
  consequences for construct design and for a published double-strand-break recruitment assay.
scope: >-
  Sequence-level analysis of reported fusion junctions, with a pre-specified prediction set in the
  Discussion. No experiment was performed, no reagent was made, and no patient, cell or animal was
  studied.
audience: [external reviewers, collaborators, maintainers, autonomous research agents]
date: 2026-08-10
last_verified: 2026-08-10
related: [DOC-EMC-ATR-COLLABORATOR-PACKAGE-CHANGELOG, DOC-EMC-ATR-VULNERABILITY-ASSESSMENT]
---

# Untranslated NR4A3 sequence encodes a 59-residue insertion in the EWSR1 exon 7 to NR4A3 exon 2 fusion of extraskeletal myxoid chondrosarcoma, and a donor-exon phase rule for the reported junctions

**Tristan D. McRae**

*Independent researcher, unaffiliated.* Correspondence: trimcrae@gmail.com

Running title: Reading frames of the EMC NR4A3 fusions

*A sequence-analysis report. No experiment was performed and no reagent was made. Every sequence
below is computed from public reference transcripts, and every breakpoint is quoted from a primary
source. Analyses and drafting were carried out with AI assistance (section 2.6).*

**Keywords:** extraskeletal myxoid chondrosarcoma; NR4A3; EWSR1; TAF15; fusion transcript; reading
frame; 5' untranslated region; construct design

<!-- EDITORIAL, NOT FOR SUBMISSION. Strip this block from the produced submission file and confirm
its absence there rather than here.

PUBLISHABLE OBJECT. A short computational research article whose Results are sequence and whose
Discussion draws the consequences, one of which is a pre-specified prediction set for an assay
another group already runs. That ordering was reversed until this revision: the previous title
announced the prediction set, the Discussion was replaced by it, and the one novel sequence result
sat in a subsection with no display item. Alternatives weighed and rejected:

  (a) REGISTERED REPORT, Stage 1. Rejected on eligibility, not on fit. Stage 1 review ends in
      in-principle acceptance, which publisher guidelines define as a commitment that the AUTHORS
      then conduct the study exactly as approved and submit Stage 2. This programme has no
      laboratory, no institutional affiliation and no engaged collaborator, so it cannot enter that
      commitment. The pre-commitment the format supplies is obtained here instead by a dated
      preprint carrying the prediction table and by the committed artifact that produced it.
  (b) STUDY PROTOCOL ARTICLE. Same eligibility failure plus a fee failure: protocol article types
      describe a study that is funded, approved and under way, and the main venues carrying the type
      are fully gold open access, which the $0 constraint excludes.
  (c) HYPOTHESIS / PERSPECTIVE PIECE. Rejected on fit. The content is computed results with
      auditable self-checks; a Perspective at the chosen venue asks for a juxtaposition of
      established lines of reasoning rather than for new computation.
  (d) RESOURCE / CALL FOR COLLABORATION. No peer-reviewed article type of that name exists at any
      venue with a $0 route that was found.

VENUE. Genes, Chromosomes and Cancer (Wiley), Research Article, with the preprint on bioRxiv.
Rationale: it is the field's standard home for fusion-gene analysis in sarcoma, and reference 7,
the counted series this paper leans on hardest, was published in it.

FEE ROUTE: THE $0 SUBSCRIPTION ROUTE IS VERIFIED AT PRIMARY SOURCE (2026-08-10). The publisher
policy pages were retrieved from a GitHub Actions runner rather than from this sandbox, because the
per-journal pages return HTTP 403 to both. Full record with verbatim quotations, URLs and HTTP
statuses: research/literature/venue-fee-routes-2026-08-10.json. Wiley states on its own author
pages that under open access "the author pays an Article Publication Charge", that hybrid open
access is selected by the corresponding author AFTER acceptance, and that a subscription article
requires only a Copyright Transfer or Exclusive License Agreement. The journal is recorded as not
open access and not in DOAJ. Declining the optional open-access selection is the $0 route.

STILL NOT VERIFIED, and stated as such: the per-journal author-guideline pages return 403 from CI as
well, so the word, abstract and display-item limits remain search-derived. Those affect FORMAT,
which an editor returns, not COST, which is billed.

COUNTS. Measured by research/manuscripts/submission_metrics.py, whose counting rule is stated in
its own docstring: main text runs from the first substantive heading to the last heading before the
declarations block, excluding frontmatter, this comment, fenced blocks, the abstract, table bodies,
references and supplementary material. The measured values are printed by that tool and are not
restated here, because a hand-carried count in this block was stale at every previous reading.
Display items after this revision: one figure and six tables in the main text, with the gene-model
table and the wild-type-control table moved to supplementary material.

APPENDIX. The superseded-value register that stood here as Appendix A has moved to
research/manuscripts/emc-atr-collaborator-package-changelog.md. It was roughly forty per cent of the
main text, it was entirely repository bookkeeping, and it would have gone to an editor inside the
same file. Nothing was dropped in the move, and this revision's own corrections were added to it.

GRAPH ANCHORS. INS-CONSTRUCT-DESIGNS and INS-FUSION-COFOLD in systems/graph/instruments.json point
at a section of this file. Their anchor was repointed in the same commit as this restructure and
verified with systems_check.anchor_resolves before being written.

REFERENCES. Retrieved 2026-08-09 from Europe PMC and recorded in
research/literature/remaining-reference-metadata-2026-08-09.json; references 9 and 10 were added in
this revision from research/manuscripts/lit-targets-aso-verify.json, where their abstracts are
committed verbatim. All ten entries are complete and every one is cited in the text.

AUTHOR BLOCK matches the block the author confirmed in nr4a3-degrader-paper.md and
response-endpoint-indolent-tumours.md. No ORCID line is carried because the repository holds none;
the cover letter states the same.
-->

> **Declarations.** Ethics approval and consent were not required and were not sought: this study
> analyses public reference sequences and published exon-level breakpoint statements, and involves
> no human participant, no identifiable data, no patient-level record, no animal and no laboratory
> work. **Funding:** none. **Competing interests:** none. **Author contributions:** Tristan D. McRae
> is the sole author and is responsible, in CRediT terms, for conceptualization, methodology,
> software, formal analysis, investigation, data curation, visualization, writing of the original
> draft, and writing of the review and editing. **Data and code:** section 5.

## Abstract

Extraskeletal myxoid chondrosarcoma (EMC) is a translocation sarcoma driven by an NR4A3 fusion,
usually with the FET-family gene EWSR1. Because NR4A3 transcript exons 1 and 2 are non-coding, a
reported EMC junction is an mRNA junction whose product cannot be obtained by splicing coding
sequences. Here every reported EMC junction was translated from canonical reference transcripts at
the transcript level. One rule governs the outcome: a junction is in frame if and only if the 5'
donor exon ends one nucleotide into a codon, and both NR4A3 acceptors give the same register because
exon 2 is 174 nucleotides. The rule was checked against an independent audit of 27
donor and acceptor pairs and predicts which unreported junctions would be in frame. Its consequence
at the exon 2 acceptor is a 59-residue insertion: EWSR1 coding sequence ends at nucleotide 793, and
that single unused base with 176
nucleotides of NR4A3 5' untranslated sequence, 174 from exon 2 and 2 from exon 3, completes 59
codons with no intervening stop before NR4A3's own initiator. The insertion belongs to the acceptor,
so any fusion using NR4A3 exon 2 carries it, and a construct built from a protein-level model does
not. Retained EWSR1 RG dipeptide counts place the reported EMC fusions between 0 and 11 of 30,
within the range of a published recruitment series whose own comparator spans 0.000 to 0.267. TCF12
falls outside the FET compositional range at every prefix length. Three predictions with explicit
falsifiers are specified in advance.

---

## 1. Introduction

EMC is an ultra-rare sarcoma defined by rearrangement of NR4A3. The commonest 5' partner is EWSR1, a
member of the FET family alongside TAF15 and FUS; a minority of cases carry TAF15, FUS or the
non-FET partner TCF12. A 2025 comprehensive review states that no clinically validated agent
directly targets NR4A3, and reports the systemic options as an anthracycline backbone with a low
objective response rate and pazopanib at an objective response rate of 18 per cent with a median
progression-free survival of 19 months, from the trial registered as NCT02066285 [2].

Work on this disease therefore runs through its fusion protein, and a fusion protein is built from a
reported junction. That step is less mechanical than it looks. NR4A3 transcript exons 1 and 2 carry
no coding sequence and exon 3 carries both 5' untranslated sequence and the initiator codon, so a
reported junction such as EWSR1 exon 7 to NR4A3 exon 2 names an mRNA event whose protein product
cannot be recovered by joining two coding sequences. It has to be translated from the spliced
transcript. Whether the junction is in frame at all is decided by nucleotides that a coding-sequence
model discards.

This report establishes that arithmetic for every EMC junction with a sourced exon-level breakpoint.
It reports the rule that governs the reading frame, the insertion the rule produces at one acceptor,
the four resulting open reading frames with their self-checks, and a compositional classification of
the one non-FET partner. It then draws two consequences: what a laboratory building an EMC fusion
construct should build, and where EMC's fusions fall on a recruitment axis published for other FET
fusions [1].

That axis is the reason the retained composition is measured here at all. A peer-reviewed report in
*Cancer Research* proposes a shared lesion across FET fusion sarcomas: the chimeric protein retains
the FET N-terminal low-complexity region and loses most of the C-terminal RGG-rich repeats, and that
loss changes its behaviour at DNA double-strand breaks [1]. The readout is accumulation of a
GFP-tagged protein at a laser-induced stripe. Gracilla and colleagues also build an internal dose
series, reintroducing one or three RGG-rich domains into EWSR1-FLI1 and into EWSR1-ATF1, and find
earlier recruitment and higher overall recruitment as the dose rises. Three transcription-factor
partner classes were examined; EMC is a fourth, and no NR4A3 fusion has been placed in the assay.

A prior-art screen supports that reading of the record, with limits that bound it on three sides. A
Europe PMC sweep of 322 EMC-linked records, of which 238 were retrieved as full text, was screened
for ATR and replication stress and returned no hits
([`emc-prior-art-2026-08-09.json`](../literature/emc-prior-art-2026-08-09.json)). First, the screen
matched titles and abstracts rather than full text, so a result inside a supplementary table would
be invisible to it. Second, it carried no positive control, the artifact recording that no
confident control identifier existed for a prior-art query, so a zero from this screen cannot be
distinguished from a zero from a screen that does not work. Third, and separately from both, the
corpus is anchored on the disease name, so a FET-fusion paper that included an NR4A3 construct
without naming EMC would never enter the 322 records and could not be missed by the matching step at
all. A measured instance of that retrieval failure is recorded in the companion assessment, where a
relevant series was not disease-titled and was found only by widening the query. The claim is that
nothing is indexed on the pairing, and never that no such experiment has been done.

Two negative findings from that companion assessment bear on whether the recruitment experiment is
worth a laboratory's time. EMC tumours show no proliferation-independent DNA-damage-response
signature on two independent series totalling 16 tumours, and ATR-inhibitor sensitivity does not track the mechanism across cell-line panels, with
one of four pre-registered tests passing and the load-bearing predictor, ATM-signalling expression,
returning a correlation of minus 0.090, the wrong sign. Both concern transcriptional and
pharmacogenomic surrogates while the predictions below concern recruitment kinetics, and neither
refutes the hypothesis; an expression matrix cannot measure a recruitment event. They do bound it.

---

## 2. Materials and methods

### 2.1 Reference transcripts and their provenance

Canonical Ensembl transcripts were used throughout, retrieved through the Ensembl REST endpoint
`https://rest.ensembl.org` on 2026-08-09 and cached
([`emc-construct-inputs.json`](../modalities/emc-construct-inputs.json)). The transcript and
translation identifiers are given in Supplementary Table S1. The cache records the retrieval
timestamp and the endpoint and does not record the Ensembl release or the genome assembly, and the
identifiers it returned carry no version suffix; that gap is stated rather than filled, since a
release number written from recollection would not be a retrieved fact. Reproduction of the analysis
from the cache is exact and is verified by the command in section 2.6; reproduction of the cache
itself would need a release number the cache does not hold. UniProt sequences for the same five
genes and for FLI1 and ATF1 were cached alongside, and every Ensembl translation was compared
against its UniProt entry.

Each gene model carries four assertions: exon lengths sum to the cDNA, coding nucleotides sum to the
coding sequence, the cDNA slice at the 5' untranslated boundary equals the coding sequence, and the
coding sequence translates to the reference protein. All four pass on all five transcripts.

### 2.2 Junction arithmetic and numbering conventions

A reported fusion is an mRNA exon junction rather than a protein junction. Constructs are therefore
assembled at the cDNA level, taking 5' partner cDNA from the transcript start through the end of the
named exon, joining 3' partner cDNA from the start of its named exon, and translating from the 5'
partner's own start codon. A coding-sequence splice discards the acceptor's untranslated segment; a
transcript-level splice translates it in the 5' partner's frame, which is the only way to establish
whether a reported junction is in frame at all.

Two conventions are fixed here because both differ by one from a convention a reader may bring.
Residue counts for a retained 5' segment are fully encoded residues only, so the EWSR1 exon 8
breakpoint is written EWSR1(1-324); the clear-cell sarcoma literature conventionally writes
EWSR1(1-325) for the same breakpoint, counting the hybrid residue whose codon is completed across
the seam. Margins to an RG-free ceiling are reported as the number of further residues that could be
retained without touching an RG dipeptide, so a segment of 161 residues against a first RG at
residue 175 has 13 residues of margin, not the 14 that the distance to the RG position would give.

Each construct carries three further self-checks: the reading frame opens with the 5' partner's
N-terminus, it ends with the 3' partner's C-terminus, and both hold together. A construct failing
them is reported as failing, and its sequence is withheld.

### 2.3 Correspondence between the breakpoint literature and transcript exon ranks

Every result below depends on the breakpoint literature's "NR4A3 exon 2" and "NR4A3 exon 3" being
transcript exon ranks 2 and 3 of ENST00000395097. The correspondence is established from the primary
sources rather than assumed, in two independent ways.

Panagopoulos and colleagues mapped genomic breakpoints in 14 cases and report that in NR4A3 "12
breakpoints were found in intron 2 and only two in intron 1" [7]. A genomic break in intron 2 yields
a transcript whose first NR4A3 exon is exon 3; a break in intron 1 yields one whose first NR4A3 exon
is exon 2. The two acceptors named in the transcript literature are therefore the exons flanking the
first two introns, which is what the transcript model gives. Independently, Brenca and colleagues
describe a rarer TAF15::NR4A3 isoform splicing into a cryptic exon within NR4A3 intron 2, "thus
encoding 25 additional amino acids prior to the NR4A3 ATG" [3], which places intron 2 immediately
upstream of the initiator codon in the field's numbering and matches a transcript in which exon 3
carries the initiator.

A second module in the same repository, written for antisense-oligonucleotide design rather than for
protein modelling, recomputes the same junction and reports the same 2-nucleotide 5' untranslated
segment ahead of the NR4A3 initiator
([`junction-aso-designs-e7n3.json`](../modalities/junction-aso-designs-e7n3.json)). That is a check
on the code path and not on the annotation, since both modules read the same cached transcript; an
independent annotation source has not been consulted, and the limitation is stated in section 4.4.

### 2.4 The retained-RG axis

The axis is retained RG dipeptides of the 5' FET partner as a fraction of that partner's wild-type
total. It is threshold-free: an RG dipeptide either falls inside the retained segment or it does
not. It is not a count of RGG domains, which depend on a box definition; reference 1 names three
RGG-rich domains in EWSR1 while the operational box-finder used here merges them into two on the
same sequence. The underlying RG count requires no such definition, and box counts are reported as
context only.

### 2.5 Compositional comparison of TCF12

Three tests, plus one sweep that removes a dependency on an unpinned breakpoint. Test one is the
N-terminal [S,Y,G,Q] fraction over a 250-residue window, the FET prion-like signature, for TCF12
against all three FET proteins and against three non-FET fusion partners as background. Test two is
RG dipeptide content, whole-protein and N-terminal, with the operational box count. Test three is
N-terminal sequence identity by Needleman-Wunsch alignment, with the three FET-versus-FET pairs
computed by the identical call as the positive control, since a single identity value in isolation
carries no scale. The sweep computes the [S,Y,G,Q] fraction of every N-terminal prefix from 50
residues to full length in 10-residue steps, on the same grid for all four proteins, so that neither
the conclusion nor the margin rests on one assumed junction or on an asymmetric comparison.

### 2.6 Reproduction, and the use of an AI assistant

```
python3 research/modalities/emc_fet_construct_designs.py --check
python3 research/modalities/emc_fet_frame_and_composition.py --check
python3 research/manuscripts/figures/emc_fusion_frame_figure.py --check
```

The first command re-derives every construct below offline from the committed input cache and prints
`REPRODUCES`. The second re-derives the frame rule, the seam arithmetic, the symmetric sweep, the
background panel and the counted frequency table, and prints the same. The third compares the
figure's provenance stamp against the artifacts it was drawn from, so a number changed without a
redraw is detected. The producers emit no output if the inputs have drifted.

Retrieval, computation and drafting were carried out with substantial assistance from an AI coding
agent operating on a version-controlled repository under the author's direction. The agent is not an
author and cannot be one, and the author takes responsibility for the content. The agent's output
influenced the substance of this report rather than its wording alone: the reading frames, the frame
rule, the recruitment-axis placement and the TCF12 classification are all computed results. The
author verified each by an independent route. Every breakpoint is quoted from a primary source and
checked against the cited record, every sequence figure is re-derivable by the commands above, and
every prose identifier is checked against a tracked fetch product by an automated linter. Those
controls address the characteristic failure mode of the method, which is a fluent citation to a
paper that does not exist.

---

## 3. Results

### 3.1 Reported junctions and their counted frequencies

**Table 1.** Reported EMC fusion junctions in transcript exon numbering, with every counted series
this analysis holds. Counts are given per series and are not pooled: the reports come from
overlapping centres and the abstracts as retrieved do not establish that the cases are
non-overlapping.

| fusion | junction | Panagopoulos, 18 tumours [7] | Okamoto, 15 fusion-positive of 18 [9] | Sjogren, 10 tumours [10] | junction sources |
|---|---|---|---|---|---|
| EWSR1::NR4A3 type 1 | EWSR1 e12 to NR4A3 e3 | 10 of 15 EWS-positive | 11 | EWSR1 partner in 5 | [4,5,6]; "E-N, corresponding to EWSR1 (exons 1-12)-NR4A3 (exons 3-8)" [3] |
| EWSR1::NR4A3 type 2 | EWSR1 e7 to NR4A3 e2 | not among the counted types | 1 | not reported | [4,6] |
| EWSR1::NR4A3 type 5 | EWSR1 e13 to NR4A3 e3 | 2 of 15 EWS-positive, named the second commonest | not reported | not reported | [5,7] |
| TAF15::NR4A3 | TAF15 e6 to NR4A3 e3 | 3 of 18 | 3 | 4 of 10 | [4,5,7]; "T-N*, corresponding to the commonest TAF15 (exons 1-6)-NR4A3 (exons 3-8) fusion" [3] |
| TCF12::NR4A3 | genomic intron 5 only | not reported | not reported | 1 of 10 | [5,10] |

The exon-level definitions of types 1 and 2 are quoted verbatim from a primary source: "The most
common fusion transcript contains exon 12 of EWSR1 fused to exon 3 of NR4A3 (type 1), whereas exon 7
of EWSR1 is fused to exon 2 of NR4A3 in the type 2 fusion transcript" [4]. That sentence names type
2 and does not rank it. Both junctions are corroborated independently by RT-PCR primer design, an
EWSR1 exon 12 forward primer paired with an NR4A3 exon 3 reverse for type 1 and an EWSR1 exon 7
forward paired with an NR4A3 exon 2 reverse for type 2 [6], which establishes that the junction is
assayed rather than how often it is found. The TAF15 junction is reported as exclusive: "exon 6 of
TAF15 is fused exclusively to exon 3 of NR4A3" [4], and "always" in a second source [5].

On the counted evidence, type 1 is the commonest transcript in every series that types its cases,
and type 2 is a minority variant: one case in Okamoto's 15, and absent from the types counted in
Panagopoulos's 15 EWS-positive cases, whose stated second commonest transcript is type 5 [7]. The
same series maps only 2 genomic breakpoints of 14 to NR4A3 intron 1, the break that produces an exon
2 acceptor, and only one EWSR1 break of 14 to intron 7 [7]. TAF15::NR4A3 is counted in 3, 3 and 4
cases across the three series, so among the fusions that retain no RG dipeptide it is the more
frequently counted one.

Three reported variants are not modelled, and the reasons differ. The rarer TAF15::NR4A3 isoform
using the intron 2 cryptic exon [3] has no sequence in any source held here, so building it would
mean inventing 75 nucleotides, and the same source reports the two isoforms as "essentially
indistinguishable" for colony formation. FUS::NR4A3 has no exon-level breakpoint statement in the
sources retrieved. TCF12::NR4A3 is reported only at genomic resolution, "the breakpoint affects the
region of intron 5" [5], and TCF12 has several alternatively spliced isoforms. Absence of a
construct is a statement about the sourcing rather than about the fusion.

### 3.2 A donor-exon phase rule

**Table 2.** Reading frame of every junction between an EWSR1 donor exon and either NR4A3 acceptor,
over the exon range that brackets all reported breakpoints. Phase is the cumulative EWSR1 coding
nucleotide count modulo 3, that is how far into a codon the donor exon ends. Full table over all
seventeen EWSR1 coding exons, and the 27-row cross-check, in
[`junction-mrna-frame-audit.json`](../modalities/junction-mrna-frame-audit.json) and
[`emc-fet-frame-and-composition.json`](../modalities/emc-fet-frame-and-composition.json).

| EWSR1 donor exon | cumulative coding nt | phase | last whole residue | to NR4A3 exon 2 | to NR4A3 exon 3 |
|---|---|---|---|---|---|
| 6 | 581 | 2 | 193 | out of frame | out of frame |
| 7 | 793 | 1 | 264 | in frame | in frame |
| 8 | 974 | 2 | 324 | out of frame | out of frame |
| 9 | 1012 | 1 | 337 | in frame | in frame |
| 10 | 1045 | 1 | 348 | in frame | in frame |
| 11 | 1164 | 0 | 388 | out of frame | out of frame |
| 12 | 1294 | 1 | 431 | in frame | in frame |
| 13 | 1417 | 1 | 472 | in frame | in frame |
| 14 | 1580 | 2 | 526 | out of frame | out of frame |

One rule accounts for the whole table. NR4A3 exon 3 contributes exactly 2 nucleotides of 5'
untranslated sequence ahead of its initiator, so a donor exon ending one nucleotide into a codon
completes that codon across the seam and resumes in register: one plus two is three. A junction is
in frame if and only if the donor exon ends at phase 1. Joining at exon 2 instead adds NR4A3 exon 2
entire, and exon 2 is 174 nucleotides, a multiple of three, so both acceptors give the same
register. The rule was checked against every one of the seventeen EWSR1 coding exons and against an
independently written audit of 27 donor and acceptor pairs, with no disagreement on any row in
scope, and it holds for TAF15 as well: TAF15 exon 6 ends at 484 coding nucleotides, phase 1, 161
whole residues.

The rule is predictive rather than descriptive. Of the nine EWSR1 exons in the range above, five are
phase 1, so an EWSR1::NR4A3 fusion breaking in introns 7, 9, 10, 12 or 13 would be in frame at
either acceptor and one breaking in introns 6, 8, 11 or 14 would not. All four reported EMC
junctions fall in the first set, and so do the reported EWSR1::ATF1 exon 10 breakpoint and the
EWSR1::FLI1 type 1 breakpoint at exon 7. The EWSR1::ATF1 exon 8 breakpoint is phase 2 and would be
out of frame with either NR4A3 acceptor, which says nothing about the ATF1 fusion itself, whose own
acceptor sets a different register.

### 3.3 A 59-residue insertion at the exon 2 acceptor

The named 3' exon of the type-2 junction, NR4A3 exon 2, is entirely non-coding, so the fusion mRNA
carries 176 nucleotides of NR4A3 5' untranslated sequence downstream of the EWSR1 cut, of which 174
come from exon 2 and 2 from exon 3 ahead of the initiator codon. Those 176 nucleotides are not
themselves a whole number of codons. EWSR1 coding sequence runs through exon 7 to nucleotide 793,
which is 264 complete codons and one base left over, and that single base completes the first codon
across the seam. The 59 residues therefore span 177 nucleotides: 1 donated by EWSR1 and 176 supplied
by NR4A3. Figure 1C draws the seam at this resolution.

The first of the 59 is a hybrid codon, AAG, one nucleotide from EWSR1 and two from NR4A3, encoding
lysine at position 265 of the chimeric protein. The remaining 58 are encoded entirely by NR4A3
sequence read in a frame NR4A3 itself does not use. The segment contains no stop codon and
translates to

```
KPTAEEGSPASPGPEPGPLAVPGSTAGASPRRTSAPPTLSASAGETPSPTIQRARYPPD
```

lying between EWSR1(1-264) and NR4A3's own methionine, which becomes residue 324 of a 949-residue
open reading frame retaining the complete NR4A3 moiety.

The insertion is a property of the acceptor, not of type 2. Any 5' partner exon joined to NR4A3 exon
2 retains the same 176 nucleotides; what the type-2 breakpoint fixes is the frame they are read in.
By the rule in section 3.2, a phase-1 donor joined to exon 2 always yields these 59 residues, and a
donor of any other phase yields no protein of this shape at all.

Two statements bound the weight of this. It is what the canonical transcripts predict for a reported
exon junction, a computed consequence rather than an observed protein, and it requires checking
against a sequenced junction before any reagent is ordered. And the mechanism has a precedent in the
same gene: Brenca and colleagues report a TAF15::NR4A3 variant splicing through a cryptic intron 2
exon and "thus encoding 25 additional amino acids prior to the NR4A3 ATG" [3]. What is new here is
the specific junction, its 59 residues and their sequence, not the possibility that NR4A3 fusions
carry N-terminal additions.

A construct built from a protein-level model of this junction is 59 residues shorter than the
reported junction predicts. The model this analysis itself used before the present work was
EWSR1(1-264)::NR4A3(1-626); no external source for a field-wide protein model of the type-2 fusion
was found, so the documented instance is the present analysis's own, recorded in the changelog
cited in section 5.

### 3.4 The four reported junctions and their products

**Table 3.** Open reading frames of the four sourced junctions. A slash marks the junction in the
seam sequence. Extra junction residues are those encoded across the seam by neither partner's own
reading frame; for type 2 the value is 59, of which one is the hybrid codon of section 3.3 and 58
are NR4A3 sequence in a non-native frame, so it is not a 59-residue hybrid seam.

| construct | 5' retained | seam | extra residues | ORF | NR4A3 moiety |
|---|---|---|---|---|---|
| type 1, EWSR1 e12 to NR4A3 e3 | EWSR1(1-431) | TAKAAVEWFD / DMPCVQAQYS | 1 | 1058 aa | complete: AF-1, C4 zinc finger, LBD, C166 |
| type 2, EWSR1 e7 to NR4A3 e2 | EWSR1(1-264) | SQQSSSYGQQ / KPTAEEGSPA | 59 | 949 aa | complete: AF-1, C4 zinc finger, LBD, C166 |
| type 5, EWSR1 e13 to NR4A3 e3 | EWSR1(1-472) | GRGMPPPLRG / DMPCVQAQYS | 1 | 1099 aa | complete: AF-1, C4 zinc finger, LBD, C166 |
| TAF15 e6 to NR4A3 e3 | TAF15(1-161) | QRENYSHHTQ / DMPCVQAQYS | 1 | 788 aa | complete: AF-1, C4 zinc finger, LBD, C166 |

All four are in frame, as the rule requires, and each splits a codon across the junction. The three
exon 3 junctions gain a single hybrid residue; the exon 2 junction gains 59. Every construct retains
NR4A3 from residue 1, so AF-1, the C4 zinc finger whose first cysteine is residue 292, the
ligand-binding domain from residue 373 and C166 are present in all four. Figure 1A draws the
retained 5' segments on one ruler.

Supplementary Table S1 gives the gene models and the Ensembl-to-UniProt comparison. One mismatch is
carried rather than reconciled: the two databases select different canonical TCF12 isoforms, 706
residues against 682, so a TCF12 residue number taken from the literature requires conversion before
comparison with anything here. It does not reach the classification in section 3.5, whose decisive
tests are compositional and are computed over every prefix on both sequences.

### 3.5 TCF12 outside the FET compositional range

A minority of EMC carries TCF12::NR4A3, counted in 1 of 10 tumours in the one series in Table 1 that
reports it, and TCF12 is not a FET-family gene. The class argument of reference 1 therefore predicts
that these cases do not carry the lesion, which is a prediction testable inside one disease. TCF12 is presented here as a designed negative control
rather than as a discovery.

**Table 4.** TCF12 against the three FET proteins. Test numbers follow section 2.5; the RG row and
the RGG-box row are two readouts of test two.

| test | the three FET proteins | TCF12 | separation |
|---|---|---|---|
| 1. N-terminal 250-aa [S,Y,G,Q] fraction | EWSR1 0.540, TAF15 0.620, FUS 0.804 | 0.368 | decisive |
| 1b. same window, non-FET background | ATF1 0.324, NR4A3 0.264, FLI1 0.248 | 0.368 | TCF12 sits with the non-FET partners |
| 4. best [S,Y,G,Q] over every prefix, symmetric | lowest FET prefix 0.439, EWSR1 residues 1-560 | best 0.400, at residues 1-160 | separates by 0.039; no TCF12 prefix reaches any FET prefix |
| 2. RG dipeptides, whole protein | 30, 31, 24 | 7 | clear |
| 2b. RGG boxes, operational definition | 2, 1, 2 | 0 | clear |
| 3. N-terminal identity, Needleman-Wunsch | FET versus FET 26.1 to 35.7 per cent | TCF12 versus FET 16.8 to 20.5 per cent | separates, modestly |

TCF12 is classified as non-FET on the compositional tests. Two rows carry qualifications. The
identity result is a real gap and a modest one, 20.5 per cent against a FET-versus-FET floor of 26.1
per cent, which follows from the FET N-termini being low-complexity and only 26 to 36 per cent
identical to each other. The prefix sweep is reported symmetrically here: sweeping all four proteins
over the same grid gives a lowest FET value of 0.439 against TCF12's best of 0.400, so the ordering
survives with a margin of 0.039 rather than the 0.140 that comparing the same swept best against the
fixed 250-residue window would give. The 250-residue row is the decisive one, and the background row shows why
0.368 is not merely a low number: the three non-FET fusion partners in the same cache sit at 0.248
to 0.368, and the three FET proteins at 0.540 to 0.804, with no overlap. Seven proteins is a
comparison panel and not a proteome background, and no null distribution is claimed. TCF12 has no
RGG box, roughly a quarter of the RG content, and no N-terminal prefix of any length reaching the
FET compositional range, which makes the classification robust to the unpinned TCF12 breakpoint.

![Figure 1. Fusion architecture, the retained-RG axis, and the type-2 seam. Panel A draws EWSR1, TAF15 and NR4A3 to scale with every RG dipeptide as a tick and the operational RGG boxes bracketed, then each reported fusion's retained 5' segment on the same ruler. Panel B draws the retained-RG axis with the two firmly measured points as filled circles, the one-domain add-back construct as an unplaceable band, the EWSR1::ATF1 comparator as a span from 0.000 to 0.267, and the EMC placements as open triangles. Panel C draws the type-2 seam at nucleotide resolution with the 59 codons and the translated residues.](./figures/emc-fusion-frame-fig1.png)

**Figure 1.** Fusion architecture, the recruitment axis, and the type-2 seam. (A) EWSR1, TAF15 and
NR4A3 drawn to scale in residues; each vertical tick is one RG dipeptide at its measured position,
dashed brackets are the operational RGG boxes of section 2.4, and the NR4A3 bar carries C166, the C4
zinc finger from residue 292 and the ligand-binding domain from residue 373. Below the dashed rule,
the retained 5' segment of each reported junction on the same scale, with the two comparator fusions
of reference 1. (B) The retained-RG axis. Filled circles are the only two positions reference 1
measured that can be placed on this axis; the hatched band is its one-domain add-back construct,
whose reintroduced domain is not identified in reference 1 and whose position is therefore not
determinable; the bar spans the three reported EWSR1::ATF1 breakpoints, because reference 1 does not
state which its construct used. Open triangles are computed placements, not measurements. (C) The
type-2 seam. EWSR1 coding sequence ends one nucleotide into a codon at nucleotide 793; that base and
176 nucleotides of NR4A3 5' untranslated sequence complete 59 codons before NR4A3's own initiator.
No panel supports any claim about recruitment, activity, efficacy or safety: panel A is sequence
composition, panel B places computed points beside published measurements without asserting that
they behave alike, and panel C is exon arithmetic.

---

## 4. Discussion

### 4.1 Consequences for construct design

The practical consequence of section 3.3 falls on anyone building an EMC fusion construct. A
laboratory that takes the type-2 junction from the literature and expresses EWSR1(1-264) joined to
NR4A3(1-626) builds a protein 59 residues shorter than the canonical transcripts predict for that
junction. Whether the difference matters functionally is not addressed here and cannot be settled by
sequence: the 59 residues are proline-rich and serine-rich with no recognisable domain, and no
structural, binding or activity claim is made about them. What can be said is that two different
proteins are being called the same fusion, and that the difference is decidable by sequencing the
patient junction and translating the transcript rather than the coding sequences.

The frame rule of section 3.2 has a second consequence, for junctions not yet reported. A new EMC
breakpoint can be graded before any construct is made: a donor exon at phase 1 gives an in-frame
product at either acceptor, and a donor at any other phase does not. That grading is what the
27-row audit supplies, and it is the reason the four reported junctions are presented here as
instances rather than as four separate results.

### 4.2 Placement on the published retained-RG axis

**Table 5.** EMC fusions and the comparators of reference 1 on one axis. Fractions are of the 5'
partner's wild-type RG total. The status column separates what reference 1 measured from what is a
reported breakpoint of a disease in which it measured something.

| construct | 5' partner retained | RG kept | fraction | status |
|---|---|---|---|---|
| EWSR1-FLI1, the study's reference fusion | EWSR1(1-264) | 0 / 30 | 0.000 | measured in reference 1 |
| EWSR1-RGG(1)-FLI1, one domain restored | not specified | not determinable | not determinable | measured in reference 1; the reintroduced RGG domain is not identified there, so it cannot be placed on this axis |
| EWSR1-RGG(3)-FLI1 and native EWSR1 | full length | 30 / 30 | 1.000 | measured in reference 1 |
| EWSR1::ATF1, EWSR1 exon 7 | EWSR1(1-264) | 0 / 30 | 0.000 | a reported breakpoint of a disease in which the mechanism was measured |
| EWSR1::ATF1, EWSR1 exon 8, commonest clear-cell type | EWSR1(1-324) | 7 / 30 | 0.233 | a reported breakpoint of a disease in which the mechanism was measured |
| EWSR1::ATF1, EWSR1 exon 10 | EWSR1(1-348) | 8 / 30 | 0.267 | a reported breakpoint of a disease in which the mechanism was measured |
| EWSR1::NR4A3 type 2 | EWSR1(1-264) | 0 / 30 | 0.000 | computed here |
| TAF15::NR4A3 | TAF15(1-161) | 0 / 31 | 0.000 | computed here |
| EWSR1::NR4A3 type 1, commonest EMC | EWSR1(1-431) | 8 / 30 | 0.267 | computed here |
| EWSR1::NR4A3 type 5 | EWSR1(1-472) | 11 / 30 | 0.367 | computed here |

Reference 1 built one EWSR1-ATF1 construct and the retrieved text does not state its EWSR1
breakpoint, so the ATF1 comparator is a span from 0.000 to 0.267 rather than a point. The census
module used here records the same limit in a checkable field, writing its control rule as "any
type", not "all types", "because a fusion's breakpoint varies between patients and this repo has no
exon audit fixing which type the source's constructs used". With the add-back construct at
one domain unplaceable as well, the firmly measured positions on this axis are 0.000 and 1.000.
Every EMC fusion falls between them, which is a weaker statement than interpolation between measured
points and is the statement the data supports. Figure 1B draws the axis this way.

Two readings are excluded. Retaining some RG content does not predict absence of the phenotype: at
least one reported clear-cell breakpoint retains seven RG dipeptides and the mechanism was measured
in that disease regardless, so the axis is a comparison and not a threshold. The placement of
TAF15::NR4A3 was open until this computation: TAF15's sourced exon 6 junction retains 161 residues
and TAF15's first RG dipeptide falls at residue 175, so the junction lies inside the strict zero-RG
window with 13 residues of margin by the convention of section 2.2, where an earlier sweep could
report only a range of 100 to 170.

The zero-RG end of the axis in EMC is occupied principally by TAF15::NR4A3 rather than by
EWSR1::NR4A3 type 2. Section 3.1 counts type 2 once across three series and TAF15::NR4A3 ten times,
so a laboratory choosing one zero-RG EMC construct has a reason to choose the TAF15 fusion, even
though type 2 is the one whose retained EWSR1 segment is identical in sequence to the reference
fusion's over the shared prefix.

### 4.3 Predictions for the recruitment assay

The unit of work in the assay of reference 1 is a GFP-tagged open reading frame, so adding EMC
requires plasmids rather than a new instrument or a new analysis. From its methods, the operative
parameters are U2OS cells expressing GFP-tagged fusion or wild-type proteins, seeded in eight-well
chambered slides, sensitised with 1 microgram per millilitre Hoechst 33342 for 30 minutes,
micro-irradiated along 5-pixel stripes with a 405 nm diode laser at 40 mW, and imaged before
irradiation and at one-minute intervals for 15 minutes afterwards [1].

**Table 6.** Three independent predictions fixed before any experiment, each with the observation
that falsifies it. The producing artifact
[`emc-fet-construct-designs.json`](../modalities/emc-fet-construct-designs.json) holds an earlier
five-prediction form under `rgg_dose_calibration_and_predictions.registered_predictions` and
`tcf12_negative_control.registered_prediction`; the reduction to the three below, and the reason for
each change, are recorded in the version history cited in section 5.

| id | prediction | falsified by |
|---|---|---|
| P1 | The two EMC fusions retaining no RG dipeptide, type 2 and TAF15::NR4A3, are recruited to laser-induced breaks, and both rank later than native EWSR1 and with the EWSR1-FLI1 reference fusion rather than with native protein. Basis: 0 of 30 and 0 of 31 retained, type 2 on a segment identical in sequence to the reference construct's, TAF15 with 13 residues of margin to its first RG at 175 | either fusion showing no accumulation at the stripe; or either ranking with native EWSR1 rather than with the reference fusion |
| P2 | EWSR1::NR4A3 type 1 is recruited earlier than type 2, the two being naturally occurring points on one axis in one disease with one 3' partner. Basis: 8 of 30 against 0 of 30 | type 1 recruiting no earlier than type 2, which would place the variable elsewhere; or type 1 not recruited at all |
| P3 | TCF12::NR4A3 is not recruited, behaving like the full-length FLI1 control of reference 1, which "showed no accumulation at laser-induced DSBs" [1]. No TCF12::NR4A3 construct is supplied with this prediction, for the reason in section 3.1; the substitute is full-length GFP-TCF12, a wild-type protein rather than a chimera, so as stated the arm tests whether a non-FET N-terminus reaches a break at all | recruitment of TCF12::NR4A3, or of full-length TCF12 |

P1 is stated as a rank prediction rather than as an equivalence. An equivalence claim of the form
"kinetics indistinguishable from EWSR1-FLI1" cannot be falsified by a null result and is satisfied
automatically by an underpowered experiment, and no equivalence margin can be quoted, because the
axis of reference 1 is ordinal and no slope is available. P2 absorbs what an earlier version of this
set stated as a separate prediction about the type-1 and type-2 pair reproducing the dose
dependence; that was the same experiment with the same falsifier and is a corollary rather than a
prediction.

P3 is the arm capable of falsifying the class argument, and it is the arm this analysis cannot
equip. Four outcomes are distinguishable. TCF12::NR4A3 not recruited while EWSR1::NR4A3 is recruited
leaves the prediction standing and demonstrates FET specificity within one disease, which no
experiment in reference 1 performs. Both recruited places the driver in something the two chimeras
share that is not the FET low-complexity region, the obvious candidate being the NR4A3 moiety, which
is why GFP-NR4A3 alone is a required control in the same run; that outcome refutes the class
argument for EMC and the structural mechanism as stated. TCF12::NR4A3 recruited while EWSR1::NR4A3
is not inverts the structural argument. Neither recruited indicates that EMC does not inherit the
lesion by this readout.

Four things are not predicted. Retained RGG content is one input to recruitment kinetics rather than
the only one; reference 1's own data show a second variable, EWSR1::ATF1 recruiting like EWSR1-FLI1
but with "differences in departure timing", and recruitment depending "at least in part" on native
EWSR1, which these constructs do not control. No effect size is predicted: the axis is ordinal
because reference 1 reports it that way. Nothing downstream is predicted; the predictions concern
recruitment kinetics only and say nothing about ATM signalling, ATR dependency, drug sensitivity,
efficacy, safety, dosing or any clinical question. And no proximity between type 1 and the
commonest clear-cell type is predicted, although both retain eight RG dipeptides: at a cut of 348
residues and a cut of 431 residues the retained set is the same eight dipeptides, at positions 300
to 330, differing only by 83 residues of RG-free sequence, so this axis cannot distinguish the two
even in principle.

An analysis plan follows from the imaging cadence above and is fixed here rather than left to the
executing laboratory. Endpoint: stripe-to-nucleoplasm fluorescence intensity ratio, background
subtracted, normalised to the same nucleus before irradiation, reported as a time course over the 15
one-minute frames, with time to half-maximal enrichment as the summary statistic. Expression
normalisation: whole-nucleus GFP intensity before irradiation recorded for every nucleus and used to
exclude the lowest and highest deciles, without which a delayed curve cannot be told from a poorly
expressed construct. Replication: at least 20 nuclei per construct
per experiment and at least 3 independent experiments, with error bars as the standard deviation
across independent experiments rather than across nuclei. Comparison: each EMC construct against
GFP-EWSR1 and against the EWSR1-FLI1 reference fusion run in the same session, since the predictions
are ranks within a run and not absolute values. Supplementary Table S2 gives the four wild-type
controls that anchor the axis for EMC's own partner genes.

### 4.4 Limitations

This is a sequence-analysis report. It asserts no efficacy, potency, dose, safety, therapeutic
window or clinical readiness for any agent in any disease, and makes no treatment recommendation.
The replication-stress vulnerability that motivates the assay is inherited from the FET fusion class
and has never been measured on an NR4A3 fusion; that inheritance is the limit of what is claimed
about the vulnerability, and no recruitment property reported here has been measured on an EMC
fusion. Every construct is a computed design for verification against a sequenced breakpoint before
any reagent is ordered.

1. **These are computed designs rather than validated reagents.** Nothing here has been synthesised,
   expressed or sequenced.
2. **This analysis inherits a documented failure mode of its own method.** An earlier committed
   artifact of the present author, built from a stated Ensembl methodology, indexed a coding-exon
   offset table with transcript exon numbers; the label "NR4A3 exon 3" resolved to transcript exon
   5, and all seven junctions it emitted silently deleted NR4A3's AF-1 domain and the first zinc
   finger of its C4 DNA-binding domain. That error survived review and was caught by re-derivation.
   Every boundary above therefore carries its provenance and every construct carries self-checks.
3. **Canonical Ensembl transcripts only, from one annotation source.** A tumour may use a different
   transcript or a different breakpoint, in which case the exon-to-residue map changes and so does
   the protein. Section 2.3 establishes the correspondence between the literature's exon numbering
   and the transcript ranks used here from two primary sources, but no second annotation database
   was consulted; a RefSeq re-derivation of the same exon boundaries would be an independent check
   and has not been run.
4. **The predictions concern recruitment kinetics and nothing else.** They make no claim about ATM
   signalling, ATR dependency or drug sensitivity, and no claim about efficacy, safety,
   tolerability, dosing, patient selection or clinical readiness.
5. **Retained RGG content is one input among several**, and the constructs do not control native
   EWSR1, which reference 1 shows contributes.
6. **FUS::NR4A3 and TCF12::NR4A3 have no sourced transcript-level junction here**, which bounds the
   sourcing rather than the fusions, and leaves P3 without its own construct.
7. **The class inheritance is the whole of the transfer argument.** The replication-stress
   vulnerability was measured on other FET fusions in other diseases, and the companion findings in
   section 1 bound it further on the transcriptional and pharmacogenomic side.
8. **The counted frequencies are three small series and are not pooled.** They total 46 tumours, all
   typed by RT-PCR on material from overlapping decades and centres, and none was assembled to
   estimate a fusion-type frequency.
9. **No laboratory work is proposed by the author.** The present author has no laboratory, so the
   predictions of section 4.3 are offered as pre-specification rather than as an intended study.

---

## 5. Data and code availability

| item | location |
|---|---|
| Construct producer | [`emc_fet_construct_designs.py`](../modalities/emc_fet_construct_designs.py) |
| Computed construct artifact | [`emc-fet-construct-designs.json`](../modalities/emc-fet-construct-designs.json) |
| Frame rule, seam arithmetic, symmetric sweep, background panel, counted frequencies | [`emc_fet_frame_and_composition.py`](../modalities/emc_fet_frame_and_composition.py), [`emc-fet-frame-and-composition.json`](../modalities/emc-fet-frame-and-composition.json) |
| Frame audit across 27 donor and acceptor pairs | [`junction-mrna-frame-audit.json`](../modalities/junction-mrna-frame-audit.json) |
| Second module recomputing the same seam | [`junction-aso-designs-e7n3.json`](../modalities/junction-aso-designs-e7n3.json) |
| Offline input cache every artifact re-derives from | [`emc-construct-inputs.json`](../modalities/emc-construct-inputs.json) |
| NR4A3 exon audit | [`nr4a3-exon-audit.json`](../modalities/nr4a3-exon-audit.json) |
| RG and RGG-box definitions, and the breakpoint sweep | [`emc_fet_idr_census.py`](../modalities/emc_fet_idr_census.py), [`emc-fet-idr-census.json`](../modalities/emc-fet-idr-census.json) |
| Figure generator and provenance stamp | [`emc_fusion_frame_figure.py`](./figures/emc_fusion_frame_figure.py), [`emc-atr-figure-provenance.json`](./figures/emc-atr-figure-provenance.json) |
| Retrieval record holding the counted series verbatim | [`lit-targets-aso-verify.json`](./lit-targets-aso-verify.json) |
| Prior-art screen, with its retrieval record and its stated limits | [`emc-prior-art-2026-08-09.json`](../literature/emc-prior-art-2026-08-09.json) |
| Companion assessment of the class-inheritance argument | [`emc-atr-vulnerability-assessment.md`](./emc-atr-vulnerability-assessment.md) |
| Separate pre-registered protocol for the drug-response half of the same question | [`emc-atri-prereg.md`](../modalities/emc-atri-prereg.md) |
| Version history, including every superseded value this analysis has corrected | [`emc-atr-collaborator-package-changelog.md`](./emc-atr-collaborator-package-changelog.md) |

Any value above that disagrees with the artifact it cites is an error in this document. Three known
disagreements are recorded rather than left for a reader to find, all dated 2026-08-10 and all
concerning provenance rather than any computed value. The construct artifact and the census cite
reference 1 as its bioRxiv preprint rather than the published version corrected in the changelog.
The type 5 and TAF15 breakpoint sources in the construct artifact still cite the conference abstract
that reference 7 replaced. And the census carries a field named `emc_canonical_EWSR1_NR4A3`
describing an EWSR1 exon 7 to NR4A3 exon 3 junction, which is not a reported type; its arithmetic is
valid for a 264-residue EWSR1 cut and is the right comparator for EWSR1::FLI1 type 1, and only the
name is wrong.

The construct artifact was produced by GitHub Actions run 30857647907 on `depmap-dependency.yml` in
the public repository, and every producer re-derives offline. The analysis runs on a standard
processor and requires no specialised hardware, licensed software or paid service, so it can be
reproduced at no cost.

---

## 6. References

1. Gracilla DE, Menon S, Breese MR, Lin YP, Dela Cruz FS, Feinberg TY, et al. FET Fusion Oncoproteins Disrupt Physiologic DNA Repair and Create a Targetable Opportunity for ATR Inhibitor Therapy. *Cancer Research* 2026;86:2660-2677. PMID 41811428. PMC13223543. doi 10.1158/0008-5472.can-25-2166.
2. Remiszewski P, Falkowski S, Szumera-Ciećkiewicz A, Spałek MJ, Rutkowski P, Czarnecka AM. From pathogenesis to the patient's bedside: a comprehensive review of extraskeletal myxoid chondrosarcoma. *J Cancer Res Clin Oncol* 2025;151(11):283. PMID 41055792. PMC12504171. doi 10.1007/s00432-025-06316-5.
3. Brenca M, Stacchiotti S, Fassetta K, Sbaraglia M, Janjusevic M, Racanelli D, et al. NR4A3 fusion proteins trigger an axon guidance switch that marks the difference between EWSR1 and TAF15 translocated extraskeletal myxoid chondrosarcomas. *J Pathol* 2019;249(1):90-101. PMID 31020999. PMC6766969. doi 10.1002/path.5284.
4. Nishio J, Iwasaki H, Nabeshima K, Naito M. Cytogenetics and molecular genetics of myxoid soft-tissue sarcomas. *Genet Res Int* 2011;2011:497148. PMID 22567356. PMC3335514. doi 10.4061/2011/497148. Source of the verbatim type 1 and type 2 exon-level definitions and of the TAF15 exclusivity statement quoted in section 3.1.
5. Cerrone M, Cantile M, Collina F, Marra L, Liguori G, Franco R, et al. Molecular strategies for detecting chromosomal translocations in soft tissue tumors (review). *Int J Mol Med* 2014;33(6):1379-1391. PMID 24714847. PMC4055444. doi 10.3892/ijmm.2014.1726. Source of the type 5 definition, the second TAF15 exclusivity statement, and the TCF12 genomic-only intron 5 breakpoint quoted in section 3.1.
6. Agaram NP, Zhang L, Sung YS, Singer S, Antonescu CR. Extraskeletal myxoid chondrosarcoma with non-EWSR1-NR4A3 variant fusions correlate with rhabdoid phenotype and high-grade morphology. *Hum Pathol* 2014;45(5):1084-1091. PMID 24746215. PMC4015728. doi 10.1016/j.humpath.2014.01.007.
7. Panagopoulos I, Mertens F, Isaksson M, Domanski HA, Brosjö O, Heim S, et al. Molecular genetic characterization of the EWS/CHN and RBP56/CHN fusion genes in extraskeletal myxoid chondrosarcoma. *Genes Chromosomes Cancer* 2002;35(4):340-352. PMID 12378528. doi 10.1002/gcc.10127. Counted series and genomic breakpoint mapping quoted in sections 2.3 and 3.1.
8. UniProt and Ensembl reference records for EWSR1 (ENST00000397938), NR4A3 (ENST00000395097), TAF15 (ENST00000605844), FUS (ENST00000254108) and TCF12 (ENST00000333725, UniProt Q99081), as retrieved into the input cache in section 5.
9. Okamoto S, Hisaoka M, Ishida T, Imamura T, Kanda H, Shimajiri S, Hashimoto H. Extraskeletal myxoid chondrosarcoma: a clinicopathologic, immunohistochemical, and molecular analysis of 18 cases. *Human Pathology* 2001. PMID 11679947. doi 10.1053/hupa.2001.28226. Counted series quoted in section 3.1. Volume and page numbers were not returned by the retrieval that resolved this record and are therefore not given.
10. Sjögren H, Meis-Kindblom JM, Orndal C, Bergh P, Ptaszynski K, Aman P, et al. Studies on the molecular pathogenesis of extraskeletal myxoid chondrosarcoma-cytogenetic, molecular genetic, and cDNA microarray analyses. *The American Journal of Pathology* 2003;162(3):781-792. PMID 12598313. PMC1868116. doi 10.1016/s0002-9440(10)63875-8. Counted series quoted in section 3.1.

---

## Supplementary material

**Supplementary Table S1.** Reference gene models, from the UniProt and Ensembl records retrieved
into the input cache [8]. Identifiers are as returned by the endpoint in section 2.1 and carry no
version suffix; the Ensembl release and genome assembly were not recorded at retrieval.

| gene | transcript | translation | protein | transcript / coding exons | Ensembl matches UniProt |
|---|---|---|---|---|---|
| EWSR1 | ENST00000397938 | ENSP00000381031 | 656 aa | 17 / 17 | yes |
| TAF15 | ENST00000605844 | ENSP00000474096 | 592 aa | 16 / 16 | yes |
| FUS | ENST00000254108 | ENSP00000254108 | 526 aa | 15 / 15 | yes |
| NR4A3 | ENST00000395097 | ENSP00000378531 | 626 aa | 8 / 6, exons 1-2 non-coding | yes |
| TCF12 | ENST00000333725 | ENSP00000331057 | 706 aa | 21 / 19 | no; UniProt Q99081 is 682 aa |

**Supplementary Table S2.** Wild-type controls for the recruitment assay and their predictions.
Full-length sequences are in the construct artifact under `wild_type_controls`.

| control | role | prediction |
|---|---|---|
| GFP-EWSR1, full length | fast-recruitment anchor, already held by any laboratory running the assay | rapid recruitment, as published. Failure to reproduce it makes nothing else in the run interpretable |
| GFP-TAF15, full length | wild-type anchor for the TAF15::NR4A3 arm | rapid recruitment, as TAF15 carries its own C-terminal RGG region. Not previously reported in this assay, so a prediction rather than a reproduction |
| GFP-NR4A3, full length | partner-alone control, the EMC analogue of the GFP-FLI1 control in reference 1 | no accumulation. NR4A3 carries 2 RG dipeptides against EWSR1's 30 and has no RGG box, so it is a weak candidate for PAR-dependent recruitment; accumulation would remove the attribution of the fusion's recruitment to the FET moiety |
| GFP-TCF12, full length | partner-alone anchor for the P3 arm | no accumulation, TCF12 being non-FET by section 3.5 |

Tag orientation was left open in all constructs. Reference 1 is internally inconsistent, its methods
writing EWSR1-FLI1-GFP and its Fig. 5 legend writing GFP-EWSR1-FLI1, and a tag can itself perturb an
intrinsically disordered region. The artifact therefore emits the untagged reading frame, and EMC
constructs should be built in whichever orientation the recipient laboratory's existing EWSR1-FLI1
construct uses.
