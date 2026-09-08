---
id: DOC-EMC-ATR-COLLABORATOR-PACKAGE
title: "Transcript-level models of the NR4A3 fusions of extraskeletal myxoid chondrosarcoma, and five pre-specified predictions for a DNA double-strand break recruitment assay"
level: L3
kind: manuscript
status: live
canonical_for:
  - the reported transcript-level junctions of the NR4A3 fusions of extraskeletal myxoid chondrosarcoma
  - the transcript-level open reading frames those junctions produce, and their in-frame self-checks
  - the placement of EMC's fusions on the published retained-RGG recruitment axis
  - the computed classification of TCF12 as a non-FET 5' partner
  - the five pre-specified DSB-recruitment predictions and their falsifiers
purpose: >-
  Compile the reported NR4A3-fusion junctions of extraskeletal myxoid chondrosarcoma from primary
  sources, translate them at the transcript level, place them on a published recruitment axis,
  classify the one non-FET 5' partner, and specify in advance the predictions, constructs, controls
  and falsifiers a group already running the assay would need to test them.
scope: >-
  Sequence-level analysis of reported fusion junctions and a pre-specified prediction set. No
  experiment was performed, no reagent was made, and no patient, cell or animal was studied.
audience: [external reviewers, collaborators, maintainers, autonomous research agents]
date: 2026-08-09
last_verified: 2026-08-09
related: [DOC-EMC-ATR-VULNERABILITY-ASSESSMENT]
---

# Transcript-level models of the NR4A3 fusions of extraskeletal myxoid chondrosarcoma, and five pre-specified predictions for a DNA double-strand break recruitment assay

**Tristan D. McRae**

*Independent researcher, unaffiliated.* Correspondence: trimcrae@gmail.com
ORCID: [ORCID TO BE SUPPLIED BY THE AUTHOR BEFORE SUBMISSION]

Running title: NR4A3 fusion models and DSB predictions

*A sequence-analysis report with a pre-specified prediction set. No experiment was performed and no
reagent was made. Every sequence below is computed from public reference transcripts, and every
breakpoint is quoted from a primary source. Analyses and drafting were carried out with AI
assistance (section 2.5).*

<!-- EDITORIAL, NOT FOR SUBMISSION.

PUBLISHABLE OBJECT. A short computational research article whose Discussion is a pre-specified,
falsifiable prediction set. The three obvious alternatives were weighed and rejected:

  (a) REGISTERED REPORT, Stage 1. Rejected on eligibility, not on fit. Stage 1 review ends in
      in-principle acceptance, which publisher guidelines define as a commitment that the AUTHORS
      then conduct the study exactly as approved and submit Stage 2. This programme has no
      laboratory, no institutional affiliation and no engaged collaborator, so it cannot enter that
      commitment, and a Stage 1 submission from an author who cannot run the protocol misrepresents
      the contract the format exists to create. The pre-commitment the format supplies is obtained
      here instead by a dated preprint carrying the prediction table and by the committed artifact
      that produced it.
  (b) STUDY PROTOCOL ARTICLE. Same eligibility failure plus a fee failure. Protocol article types
      describe a study that is funded, approved and under way, and typically require a recruitment
      status and an ethics decision; and the main venues carrying the type are fully gold open
      access, which the $0 constraint excludes.
  (c) HYPOTHESIS / PERSPECTIVE PIECE. Rejected on fit. The content is four computed results with
      auditable self-checks, and a Perspective type at the chosen venue asks for a juxtaposition of
      established lines of reasoning rather than for new computation. Filing it as a Perspective
      would detach the ask from the evidence that makes it worth taking.
  (d) RESOURCE / CALL FOR COLLABORATION. No peer-reviewed article type of that name exists at any
      venue with a $0 route that was found.

VENUE. Genes, Chromosomes and Cancer (Wiley), Research Article, with the preprint on bioRxiv.
Rationale: it is the field's standard home for fusion-gene analysis in sarcoma, and the reported
EMC junction literature this paper compiles sits in that literature.

FEE ROUTE: THE $0 SUBSCRIPTION ROUTE IS NOW VERIFIED AT PRIMARY SOURCE (2026-08-10). The publisher
policy pages were retrieved from a GitHub Actions runner rather than from this sandbox, because the
per-journal pages return HTTP 403 to both. Full record with verbatim quotations, URLs and HTTP
statuses: research/literature/venue-fee-routes-2026-08-10.json.
Wiley states on its own author pages that under open access "the author pays an Article Publication
Charge", that hybrid open access is selected by the corresponding author AFTER acceptance, and that a
subscription article requires only a Copyright Transfer or Exclusive License Agreement. The journal
is recorded as not open access and not in DOAJ. Declining the optional open-access selection is the
$0 route.
STILL NOT VERIFIED, and stated as such: the per-journal author-guideline pages return 403 from CI as
well, so the word, abstract and display-item limits written into this manuscript remain
search-derived. Those affect FORMAT, which an editor returns, not COST, which is billed. And the
APC figure itself comes from a bibliographic database rather than the publisher page; it is not the
number the decision rests on, since the charge is being declined.
ARTICLE-TYPE SPECIFICS ALSO UNVERIFIED for the same reason. Search snippets of the journal's
guidelines report an abstract of at most 250 words, structured or unstructured, and a Short
Communication limit of 2,500 words with 25 references and six display items. This manuscript is
built to the tighter of those: the abstract is 227 words as a single paragraph; the main text
(sections 1-7, excluding abstract, tables, references and appendix) is 2,722 words, or 3,467 words
with the seven tables counted in; and there are 7 display items and 8 references. Confirm the real
limits before submission and cut section 5 first if a shorter type is chosen. These counts drift
whenever the text is edited and were measured rather than remembered.

TITLE. The frontmatter `title` now matches the H1. systems_check.py reads that field back out of
this file to render systems/views/L3-publications.md, so the committed view is stale until someone
runs `python3 systems/systems_check.py --write-views`. That regeneration is required in any case:
three sibling manuscripts were retitled in the same window and the view is stale on their rows too.

GRAPH ANCHORS. RESOLVED 2026-08-09. INS-CONSTRUCT-DESIGNS and INS-FUSION-COFOLD in
systems/graph/instruments.json carried owner.anchor = "#72-the-four-constructs--all-four-are-in-frame-4--4",
which was section 7.2 of the previous draft. Both now point at "#32-gene-models-and-open-reading-frames",
verified to resolve with systems_check.anchor_resolves before being written. Views regenerated;
systems_check reports 0 ERROR.

REFERENCES. Retrieved 2026-08-09 from Europe PMC and recorded in
research/literature/remaining-reference-metadata-2026-08-09.json. All eight entries are complete and
every one is cited in the text.

REFERENCE 7 WAS A CONFERENCE ABSTRACT AND IS NOW THE PEER-REVIEWED PAPER. It previously read
"PMC2395470" with no author list or title, because Europe PMC returns an empty author string and a
title of only "Biology" for that record. Reading the full text showed why: PMC2395470 is the whole
CTOS 2001 abstract supplement (Sarcoma 2001;5(Suppl 1):S37-43), and "Biology" is one of its section
headings, so the record describes a supplement rather than an article. The counted series quoted in
section 3.1 comes from abstract 035 within it, by Panagopoulos and colleagues. That work was
subsequently published in full as Genes Chromosomes Cancer 2002;35(4):340-352 (PMID 12378528),
reporting the same 18 cases and the same counts verbatim: 15 EWS/CHN cases, type 1 in 10 tumours,
type 5 in two. The reference is now the peer-reviewed paper, which is the correct source when it
exists and reports the same data.

NOVELTY CLAIM. Section 1 cites the 2026-08-09 prior-art screen for zero indexed EMC records on ATR
or replication stress, with the title-and-abstract caveat in the running text rather than in a
footnote. Reviewers of a pre-committed format scrutinise a "nobody has done this" claim closely, so
the claim is written as "no indexed report" and never as "no report".

AUTHOR BLOCK matches the block the author confirmed in nr4a3-degrader-paper.md and
response-endpoint-indolent-tumours.md. No ORCID is given because the repository carries none.
-->

> **Declarations.** Ethics approval and consent were not required and were not sought: this study
> analyses public reference sequences and published exon-level breakpoint statements, and involves
> no human participant, no identifiable data, no patient-level record, no animal and no laboratory
> work. **Funding:** none. **Competing interests:** none. **Author contributions:** Tristan D. McRae
> is the sole author and is responsible, in CRediT terms, for conceptualization, methodology,
> software, formal analysis, investigation, data curation, visualization, writing of the original
> draft, and writing of the review and editing. **Data and code:** section 7.

> **Scope of the claims.** This is a sequence-analysis report. It asserts no efficacy, potency,
> dose, safety, therapeutic window or clinical readiness for any agent in any disease, and makes no
> treatment recommendation. The replication-stress vulnerability that motivates the assay is
> inherited from the FET fusion class and has never been measured on an NR4A3 fusion; that
> inheritance is the limit of what is claimed here, and no result below is EMC-specific. Every
> construct is a computed design for verification against a sequenced breakpoint before any reagent
> is ordered.

## Abstract

Extraskeletal myxoid chondrosarcoma (EMC) is a translocation sarcoma driven by an NR4A3 fusion,
usually with the FET-family gene EWSR1. A recent report describes FET fusion oncoproteins as
disrupting physiologic DNA repair, using accumulation of a GFP-tagged fusion protein at
laser-induced double-strand break stripes as the readout, and reports that recruitment kinetics
track the dose of RGG-rich sequence retained from the FET partner. EMC is the untested fourth
transcription-factor-partner class in that argument. Here the reported EMC junctions are compiled
from primary sources, translated at the transcript rather than the coding-sequence level, and
placed on that published dose axis. Four sourced junctions, EWSR1 exon 12 to NR4A3 exon 3, EWSR1
exon 7 to NR4A3 exon 2, EWSR1 exon 13 to NR4A3 exon 3 and TAF15 exon 6 to NR4A3 exon 3, all yield
in-frame open reading frames retaining the complete NR4A3 moiety. The exon 7 to exon 2 junction
carries 176 nucleotides of NR4A3 5' untranslated sequence in the EWSR1 reading frame, encoding 59
residues that the protein-level model in general use does not contain. Retained EWSR1 RG dipeptide
counts place the two commonest EMC fusions at 0 of 30 and 8 of 30, bracketing the two fusions in
which the mechanism has been measured. TCF12, the 5' partner in a minority of EMC, falls outside
the FET compositional range at every prefix length. Five predictions with explicit falsifiers, four
constructs and four wild-type controls are specified in advance.

---

## 1. Introduction

EMC is an ultra-rare sarcoma defined by rearrangement of NR4A3. The commonest 5' partner is EWSR1,
a member of the FET family alongside TAF15 and FUS; a minority of cases carry TAF15, FUS or the
non-FET partner TCF12. A 2025 comprehensive review states that no clinically validated agent
directly targets NR4A3, and reports the systemic options as an anthracycline backbone with a low
objective response rate and pazopanib at an objective response rate of 18 per cent with a median
progression-free survival of 19 months (NCT02066285) [2]. The driver itself is untreated, so a
candidate vulnerability that does not require the driver to be drugged is worth the cost of
establishing.

A peer-reviewed report in *Cancer Research* proposes a shared lesion across FET fusion sarcomas: the chimeric protein retains
the FET N-terminal low-complexity region and loses most of the C-terminal RGG-rich repeats, and
that loss changes its behaviour at DNA double-strand breaks [1]. The readout is accumulation of a
GFP-tagged protein at a laser-induced stripe. The report also builds an internal dose series,
reintroducing one or three RGG-rich domains into EWSR1-FLI1 and into EWSR1-ATF1, and finds earlier
recruitment and higher overall recruitment as the dose rises.

Three transcription-factor-partner classes were examined in that work. EMC is a fourth, and no
NR4A3 fusion has been placed in the assay. The unit of work in that assay is a GFP-tagged open
reading frame, so adding EMC requires new plasmids rather than a new instrument or a new analysis;
what is missing is the sequence, the placement and the criteria.

A prior-art screen supports that reading of the record. A Europe PMC sweep of 322 EMC-linked
records, of which 238 were retrieved as full text, was screened for ATR and replication stress and
returned no hits
([`emc-prior-art-2026-08-09.json`](../../literature/emc-prior-art-2026-08-09.json)). The screen
matched titles and abstracts rather than full text, so that zero establishes only that nothing is
indexed on the pairing, and not that no such experiment has been done: a result inside a
supplementary table of a larger FET-fusion paper would be invisible to it.

This report supplies those three things. It compiles the reported EMC junctions from primary
sources, computes the protein each produces, places EMC on the published dose axis, classifies the
one non-FET partner, and fixes five predictions with their falsifiers before any experiment.

---

## 2. Methods

### 2.1 Gene models and junction arithmetic

A reported fusion is an mRNA exon junction rather than a protein junction. Constructs are therefore
assembled at the cDNA level, taking 5' partner cDNA from the transcript start through the end of
the named exon, joining 3' partner cDNA from the start of its named exon, and translating from the
5' partner's own start codon.

The distinction changes an answer here. NR4A3 transcript exons 1 and 2 are entirely non-coding and
exon 3 carries both 5' untranslated sequence and the start codon. A coding-sequence splice discards
that untranslated segment; a transcript-level splice translates it in the 5' partner's frame, which
is the only way to establish whether a reported junction is in frame at all.

Canonical Ensembl transcripts were used throughout. Each gene model carries four assertions:
exon lengths sum to the cDNA, coding nucleotides sum to the coding sequence, the cDNA slice at the
5' untranslated boundary equals the coding sequence, and the coding sequence translates to the
reference protein. Each construct carries three further self-checks: the reading frame opens with
the 5' partner's N-terminus, it ends with the 3' partner's C-terminus, and both hold together. A
construct failing them is reported as failing, and its sequence is withheld.

### 2.2 The retained-RG axis

The axis is retained RG dipeptides of the 5' FET partner as a fraction of that partner's wild-type
total. It is threshold-free: an RG dipeptide either falls inside the retained segment or it does
not. It is not a count of RGG domains, which depend on a box definition: the source names three
RGG-rich domains in EWSR1 while the operational box-finder used here merges them into two on the
same sequence. The underlying RG count requires no such definition, and box counts are reported as
context only.

### 2.3 TCF12 comparison

Three independent tests, plus one sweep that removes a dependency on an unpinned breakpoint. Test
one is the N-terminal [S,Y,G,Q] fraction over a 250-residue window, the FET prion-like signature,
for TCF12 against all three FET proteins. Test two is RG dipeptide content, whole-protein and
N-terminal, with the operational box count. Test three is N-terminal sequence identity by
Needleman-Wunsch alignment, with the three FET-versus-FET pairs computed by the identical call as
the positive control, since a single identity value in isolation carries no scale. The sweep
computes the [S,Y,G,Q] fraction of every TCF12 N-terminal prefix from 50 residues to full length in
10-residue steps, so the conclusion does not rest on one assumed junction.

### 2.4 Tag orientation

Tag orientation was left open. The source is internally inconsistent, its methods writing
EWSR1-FLI1-GFP and its Fig. 5 legend writing GFP-EWSR1-FLI1, and a tag can itself perturb an
intrinsically disordered region. The artifact therefore emits the untagged reading frame, and EMC
constructs should be built in whichever orientation the recipient laboratory's existing
EWSR1-FLI1 construct uses.

### 2.5 Reproduction

```
python3 research/modalities/emc_fet_construct_designs.py --check
```

That command re-derives every figure below offline from the committed input cache
([`emc-construct-inputs.json`](../../modalities/emc-construct-inputs.json)) and prints `REPRODUCES`.
The producer emits no output if the inputs have drifted.

Retrieval, computation and drafting were carried out with substantial assistance from an AI coding
agent operating on a version-controlled repository under the author's direction. The agent is not an
author and cannot be one, and the author takes responsibility for the content. The agent's output
did influence the substance of this report rather than its wording alone: the transcript-level
reading frames, the recruitment-axis placement and the TCF12 classification are all computed
results, and the pre-specified predictions follow from them. The author verified each by an
independent route. Every breakpoint is quoted from a primary source and checked against the cited
record, every sequence figure is re-derivable by the command above, and every prose identifier is
checked against a tracked fetch product by an automated linter. Those controls address the
characteristic failure mode of the method, which is a fluent citation to a paper that does not
exist.

---

## 3. Results

### 3.1 Reported junctions

**Table 1.** Reported junctions, in transcript exon numbering, with the source of each.

| fusion | junction | reported rank | sources |
|---|---|---|---|
| EWSR1::NR4A3 type 1 | EWSR1 e12 to NR4A3 e3 | commonest | [4,5,6]; expressed as "E-N, corresponding to EWSR1 (exons 1-12)-NR4A3 (exons 3-8)" [3] |
| EWSR1::NR4A3 type 2 | EWSR1 e7 to NR4A3 e2 | second | [4,6] |
| EWSR1::NR4A3 type 5 | EWSR1 e13 to NR4A3 e3 | minority | [5,7] |
| TAF15::NR4A3 | TAF15 e6 to NR4A3 e3 | the only reported coding junction | [4,5,7]; expressed as "T-N*, corresponding to the commonest TAF15 (exons 1-6)-NR4A3 (exons 3-8) fusion" [3] |

The two commonest types are quoted verbatim from a primary source: "The most common fusion
transcript contains exon 12 of EWSR1 fused to exon 3 of NR4A3 (type 1), whereas exon 7 of EWSR1 is
fused to exon 2 of NR4A3 in the type 2 fusion transcript" [4]. They are corroborated independently
by RT-PCR primer design, an EWSR1 exon 12 forward primer paired with an NR4A3 exon 3 reverse for
type 1 and an EWSR1 exon 7 forward paired with an NR4A3 exon 2 reverse for type 2 [6], and by a
counted series in which 10 of 15 tumours carried exon 12 to exon 3 and 2 of 15 carried type 5 [7].
The TAF15 junction is reported as exclusive: "exon 6 of TAF15 is fused exclusively to exon 3 of
NR4A3" [4], and "always" in a second source [5].

Three reported variants are not modelled, and the reasons differ. A rarer TAF15::NR4A3 isoform
splices into a cryptic exon in NR4A3 intron 2, "thus encoding 25 additional amino acids prior to
the NR4A3 ATG" [3]; the cryptic exon's sequence is in no source held here, so building it would
mean inventing 75 nucleotides, and the same source reports the two isoforms as "essentially
indistinguishable" for colony formation. FUS::NR4A3 has no exon-level breakpoint statement in the
sources retrieved. TCF12::NR4A3 is reported only at genomic resolution, "the breakpoint affects the
region of intron 5" [5], and TCF12 has several alternatively spliced isoforms. Absence of a
construct is a statement about the sourcing rather than about the fusion.

### 3.2 Gene models and open reading frames

All four gene-model assertions pass on all five transcripts.

**Table 2.** Reference gene models, from the UniProt and Ensembl records retrieved into the input cache [8].

| gene | transcript | protein | transcript / coding exons | Ensembl matches UniProt |
|---|---|---|---|---|
| EWSR1 | ENST00000397938 | 656 aa | 17 / 17 | yes |
| TAF15 | canonical | 592 aa | 16 / 16 | yes |
| FUS | canonical | 526 aa | 15 / 15 | yes |
| NR4A3 | ENST00000395097 | 626 aa | 8 / 6, exons 1-2 non-coding | yes |
| TCF12 | canonical | 706 aa | 21 / 19 | no; UniProt Q99081 is 682 aa |

The TCF12 length mismatch is not reconciled here. The two databases select different
canonical isoforms, so a TCF12 residue number taken from the literature requires conversion before
comparison with anything here. It does not reach the classification in section 3.5, whose decisive
tests are compositional and are computed over every prefix.

**Table 3.** The four constructs. A slash marks the junction in the seam sequence. Extra junction
residues are those encoded across the seam by neither partner's own reading frame.

| construct | 5' retained | seam | extra residues | ORF | NR4A3 moiety |
|---|---|---|---|---|---|
| type 1, EWSR1 e12 to NR4A3 e3 | EWSR1(1-431) | TAKAAVEWFD / DMPCVQAQYS | 1 | 1058 aa | complete: AF-1, C4 zinc finger, LBD, C166 |
| type 2, EWSR1 e7 to NR4A3 e2 | EWSR1(1-264) | SQQSSSYGQQ / KPTAEEGSPA | 59 | 949 aa | complete: AF-1, C4 zinc finger, LBD, C166 |
| type 5, EWSR1 e13 to NR4A3 e3 | EWSR1(1-472) | GRGMPPPLRG / DMPCVQAQYS | 1 | 1099 aa | complete: AF-1, C4 zinc finger, LBD, C166 |
| TAF15 e6 to NR4A3 e3 | TAF15(1-161) | QRENYSHHTQ / DMPCVQAQYS | 1 | 788 aa | complete: AF-1, C4 zinc finger, LBD, C166 |

All four are in frame. Each splits a codon across the junction, which is why the frame was computed
at the nucleotide level rather than inferred from residue arithmetic.

### 3.3 A 59-residue insertion in the type-2 fusion

The named 3' exon of the type-2 junction, NR4A3 exon 2, is entirely non-coding, so the fusion mRNA
carries 176 nucleotides of NR4A3 5' untranslated sequence downstream of the EWSR1 cut. Read in the
EWSR1 frame that segment contains no stop codon and encodes 59 residues lying between EWSR1(1-264)
and NR4A3's own methionine. The type-2 fusion protein predicted by the canonical transcripts is
therefore not EWSR1(1-264)::NR4A3(1-626), the protein-level model in general use and the one this
programme itself used until this analysis.

The weight of that statement is bounded. It is what the canonical transcripts predict for the
reported exon junction, a computed consequence rather than an observed protein, and it requires
checking against a sequenced junction before any reagent is ordered. A 59-residue difference
nonetheless changes what a construct built from the published model contains.

### 3.4 Placement on the retained-RG axis

**Table 4.** EMC fusions and the measured comparators on one axis. Fractions are of the 5' partner's
wild-type RG total.

| construct | 5' partner retained | RG kept | fraction | status |
|---|---|---|---|---|
| EWSR1-FLI1, the study's reference fusion | EWSR1(1-264) | 0 / 30 | 0.000 | measured |
| EWSR1::NR4A3 type 2 | EWSR1(1-264) | 0 / 30 | 0.000 | predicted (P1) |
| TAF15::NR4A3 | TAF15(1-161) | 0 / 31 | 0.000 | predicted (P3) |
| EWSR1::ATF1 e8, commonest clear-cell type | EWSR1(1-324) | 7 / 30 | 0.233 | measured, phenotype present |
| EWSR1::ATF1 e10 | EWSR1(1-348) | 8 / 30 | 0.267 | measured |
| EWSR1::NR4A3 type 1, commonest EMC | EWSR1(1-431) | 8 / 30 | 0.267 | predicted (P2) |
| EWSR1::NR4A3 type 5 | EWSR1(1-472) | 11 / 30 | 0.367 | predicted |
| EWSR1-RGG(3)-FLI1 and native EWSR1 | full length | 30 / 30 | 1.000 | measured |

EMC's two main fusion types bracket the two fusions in which the mechanism was measured. Type 2
sits where EWSR1-FLI1 sits, at zero, on a retained segment reported as byte-identical over the
shared prefix. Type 1 sits at 0.267 against 0.233 for the commonest reported clear-cell type and
0.267 for the exon 10 type. Neither EMC type extrapolates beyond the published series; both
interpolate between points already measured.

Two readings are excluded. Retaining some RG content does not predict absence of the phenotype: the
commonest clear-cell type retains seven RG dipeptides and the mechanism was measured in that
disease regardless, so the axis is a comparison and not a threshold. The placement of
TAF15::NR4A3 was also open until this computation. TAF15's sourced exon 6 junction retains 161 residues
and TAF15's first RG dipeptide falls at residue 175, so the junction lies inside the strict zero-RG
window with 14 residues of margin, where the earlier sweep could report only a range of 100 to 170.

### 3.5 TCF12 outside the FET compositional range

Roughly 3 to 4 per cent of EMC carries TCF12::NR4A3, and TCF12 is not a FET-family gene. The class
argument therefore predicts that these cases do not carry the lesion, which is a prediction
testable inside one disease on one slide.

**Table 5.** TCF12 against the three FET proteins.

| test | the three FET proteins | TCF12 | separation |
|---|---|---|---|
| N-terminal 250-aa [S,Y,G,Q] fraction | EWSR1 0.540, TAF15 0.620, FUS 0.804 | 0.368 | decisive |
| best [S,Y,G,Q] over every prefix, 50 aa to full length, 66 prefixes | as above | 0.400, at residues 1-160 | decisive; no TCF12 prefix reaches the lowest FET value |
| RG dipeptides, whole protein | 30, 31, 24 | 7 | clear |
| RGG boxes, operational definition | 2, 1, 2 | 0 | clear |
| N-terminal identity, Needleman-Wunsch | FET versus FET 26.1 to 35.7 per cent | TCF12 versus FET 16.8 to 20.5 per cent | separates, modestly |

TCF12 is classified as non-FET on the compositional tests. The identity result carries the
qualification: 20.5 per cent against a FET-versus-FET floor of 26.1 per cent is a real gap but a
modest one, which follows from the FET N-termini being low-complexity and only 26 to 36 per cent
identical to each other. TCF12 has no RGG box, roughly a quarter of the RG content, and no
N-terminal prefix of any length reaching the FET compositional range, which makes the
classification robust to the unpinned TCF12 breakpoint.

---

## 4. Pre-specified predictions

**Table 6.** Predictions fixed before any experiment, each with the observation that falsifies it.
P1 to P4 are held in `emc-fet-construct-designs.json` under
`rgg_dose_calibration_and_predictions.registered_predictions`; P5 is held in the same file under
`tcf12_negative_control.registered_prediction`.

| id | prediction | falsified by |
|---|---|---|
| P1 | EWSR1::NR4A3 type 2 is recruited to laser-induced breaks with kinetics indistinguishable from EWSR1-FLI1. Basis: 0 of 30 RG retained, on a segment byte-identical to the reference construct's | no accumulation at the stripe, or kinetics matching native EWSR1 rather than the fusion reference |
| P2 | EWSR1::NR4A3 type 1, the commonest EMC fusion, is recruited earlier than type 2 and closest to the commonest clear-cell EWSR1::ATF1 type. Basis: 8 of 30 against 7 of 30 | type 1 recruiting no earlier than type 2, which would place the variable elsewhere; or type 1 not recruited at all |
| P3 | TAF15::NR4A3 is recruited, at the zero end of the axis. Basis: TAF15(1-161) retains 0 of 31, with 14 residues of margin to TAF15's first RG at 175 | kinetics indistinguishable from native TAF15 |
| P4 | The type-1 and type-2 pair reproduces the RGG dose-dependence with no add-back construct, being two naturally occurring points on one axis in one disease with one 3' partner | the pair showing no kinetic difference, which would bound the dose-dependence to engineered constructs |
| P5 | TCF12::NR4A3 is not recruited, behaving like the source's full-length FLI1 control, which "showed no accumulation at laser-induced DSBs" [1] | recruitment of TCF12::NR4A3 |

P5 is the arm capable of falsifying the class argument. Four outcomes are distinguishable. TCF12::NR4A3
not recruited while EWSR1::NR4A3 is recruited leaves the prediction standing and demonstrates FET
specificity within one disease, which no experiment in the source performs. Both recruited places
the driver in something the two chimeras share that is not the FET low-complexity region, the
obvious candidate being the NR4A3 moiety, which is why GFP-NR4A3 alone is a required control in the
same run; that outcome refutes the class argument for EMC and the structural mechanism as stated.
TCF12::NR4A3 recruited while EWSR1::NR4A3 is not inverts the structural argument. Neither recruited
indicates that EMC does not inherit the lesion by this readout, a negative result that would spare
other groups the experiment.

Four things are explicitly not predicted. Retained RGG content is one input to recruitment kinetics
rather than the only one; the source's own data show a second variable, EWSR1::ATF1 recruiting like
EWSR1-FLI1 but with "differences in departure timing", and recruitment depending "at least in part"
on native EWSR1, which these constructs do not control. No effect size is predicted: the axis is
ordinal, earlier or later and more or less, because the source reports it that way, and no slope is
available to quote. Nothing downstream is predicted; the predictions concern recruitment kinetics
only and say nothing about ATM signalling, ATR dependency, drug sensitivity, efficacy, safety,
dosing or any clinical question. And the 3' partner is a nuclear receptor with its own DNA-binding
domain: the source showed that a DNA-binding-domain mutation did not change EWSR1-FLI1's
localisation, but that was measured on an ETS domain rather than a C4 zinc finger, which is why
GFP-NR4A3 alone is included as a control.

---

## 5. Constructs and controls

The assay's unit of work is a GFP-tagged open reading frame. From its methods: "U2OS cells
expressing EWSR1-GFP, EWSR1-FLI1-GFP, EWSR1-ATF1-GFP, EWSR1-WT1-GFP or the various mutant forms of
the fusion oncoproteins were seeded in 8-well Lab Tek II Chamber Slides ... Cells were treated with
1 microgram/ml Hoechst 33342 ... for 30 minutes prior to micro-irradiation ... 5-pixel wide stripes
were drawn in every cell nucleus ... and irradiated with a 405nm diode laser (40mW). Images were
acquired pre-irradiation and at 1-minute intervals post-laser damage for 15 minutes" [1]. Adding
EMC to that panel requires plasmids and nothing else.

Four wild-type controls anchor both ends of the recruitment axis for EMC's own partner genes,
without which a delayed curve cannot be told from a poorly expressed construct.

**Table 7.** Wild-type controls and their predictions. Full-length sequences are in the artifact
under `wild_type_controls`.

| control | role | prediction |
|---|---|---|
| GFP-EWSR1, full length | fast-recruitment anchor, already held by any laboratory running the assay | rapid recruitment, as published. Failure to reproduce it makes nothing else in the run interpretable |
| GFP-TAF15, full length | wild-type anchor for the TAF15::NR4A3 arm | rapid recruitment, as TAF15 carries its own C-terminal RGG region. Not previously reported in this assay, so a prediction rather than a reproduction |
| GFP-NR4A3, full length | partner-alone control, the EMC analogue of the source's GFP-FLI1 control | no accumulation. Recruitment of NR4A3 alone would remove the attribution of the fusion's recruitment to the FET moiety |
| GFP-TCF12, full length | partner-alone anchor for the P5 arm | no accumulation, TCF12 being non-FET by section 3.5 |

No TCF12::NR4A3 construct is emitted, for the reason in section 3.1. A laboratory holding a
TCF12::NR4A3 case should sequence the junction; failing that, the arm runs with full-length
GFP-TCF12, which tests the same question the control exists for, whether a non-FET N-terminus
reaches a double-strand break at all.

---

## 6. Limitations

1. **These are computed designs rather than validated reagents.** Nothing here has been synthesised,
   expressed or sequenced. Every junction requires verification against a sequenced breakpoint
   before any order is placed.
2. **This analysis inherits a documented failure mode of its own method.** An earlier committed
   artifact in this programme, built from a stated Ensembl methodology, indexed a coding-exon offset
   table with transcript exon numbers; the label "NR4A3 exon 3" resolved to transcript exon 5, and
   all seven junctions it emitted silently deleted NR4A3's AF-1 domain and the first zinc finger of
   its C4 DNA-binding domain. That error survived review and was caught by re-derivation. Every
   boundary above therefore carries its provenance and every construct carries self-checks.
3. **Canonical Ensembl transcripts only.** A tumour may use a different transcript or a different
   breakpoint, in which case the exon-to-residue map changes and so does the protein.
4. **The predictions concern recruitment kinetics and nothing else.** They make no claim about ATM
   signalling, ATR dependency or drug sensitivity, and no claim about efficacy, safety,
   tolerability, dosing, patient selection or clinical readiness.
5. **Retained RGG content is one input among several**, and the constructs do not control native
   EWSR1, which the source shows contributes.
6. **FUS::NR4A3 and TCF12::NR4A3 have no sourced transcript-level junction here**, which bounds the
   sourcing rather than the fusions.
7. **The class inheritance is the whole of the transfer argument.** The replication-stress
   vulnerability was measured on other FET fusions in other diseases; no NR4A3 fusion has been
   tested for it, and no computation in this report changes that.
8. **No laboratory work is proposed by the author.** This programme has no laboratory. The
   deliverable is the design, the prediction and the criteria.

---

## 7. Data and code availability

| item | location |
|---|---|
| Producer | [`emc_fet_construct_designs.py`](../../modalities/emc_fet_construct_designs.py) |
| Computed artifact, the home of every figure above | [`emc-fet-construct-designs.json`](../../modalities/emc-fet-construct-designs.json) |
| Offline input cache the artifact re-derives from | [`emc-construct-inputs.json`](../../modalities/emc-construct-inputs.json) |
| NR4A3 exon audit | [`nr4a3-exon-audit.json`](../../modalities/nr4a3-exon-audit.json) |
| RG and RGG-box definitions, and the breakpoint sweep | [`emc_fet_idr_census.py`](../../modalities/emc_fet_idr_census.py), [`emc-fet-idr-census.json`](../../modalities/emc-fet-idr-census.json) |
| Companion assessment of the class-inheritance argument | [`emc-atr-vulnerability-assessment.md`](./emc-atr-vulnerability-assessment.md) |
| Prior-art screen, with its retrieval record and its stated limits | [`emc-prior-art-2026-08-09.json`](../../literature/emc-prior-art-2026-08-09.json) |
| Separate pre-registered protocol for the drug-response half of the same question, which this report does not address | [`emc-atri-prereg.md`](../../modalities/emc-atri-prereg.md) |

The artifact was produced by GitHub Actions run 30857647907 on `depmap-dependency.yml` in the
public repository, and `--check` re-derives it offline. Any figure above that disagrees with the
artifact is an error in this document.

The analysis runs on a standard processor and requires no specialised hardware, licensed software or paid service, so it can be reproduced at no cost.

---

## 8. References

1. Gracilla DE, Menon S, Breese MR, Lin YP, Dela Cruz FS, Feinberg TY, et al. FET Fusion Oncoproteins Disrupt Physiologic DNA Repair and Create a Targetable Opportunity for ATR Inhibitor Therapy. *Cancer Research* 2026;86:2660-2677. PMID 41811428. PMC13223543. doi 10.1158/0008-5472.can-25-2166.
2. Remiszewski P, Falkowski S, Szumera-Ciećkiewicz A, Spałek MJ, Rutkowski P, Czarnecka AM. From pathogenesis to the patient's bedside: a comprehensive review of extraskeletal myxoid chondrosarcoma. *J Cancer Res Clin Oncol* 2025;151(11):283. PMID 41055792. PMC12504171. doi 10.1007/s00432-025-06316-5.
3. Brenca M, Stacchiotti S, Fassetta K, Sbaraglia M, Janjusevic M, Racanelli D, et al. NR4A3 fusion proteins trigger an axon guidance switch that marks the difference between EWSR1 and TAF15 translocated extraskeletal myxoid chondrosarcomas. *J Pathol* 2019;249(1):90-101. PMID 31020999. PMC6766969. doi 10.1002/path.5284.
4. Nishio J, Iwasaki H, Nabeshima K, Naito M. Cytogenetics and molecular genetics of myxoid soft-tissue sarcomas. *Genet Res Int* 2011;2011:497148. PMID 22567356. PMC3335514. doi 10.4061/2011/497148. Source of the verbatim type 1 and type 2 exon-level definitions and of the TAF15 exclusivity statement quoted in section 3.1.
5. Cerrone M, Cantile M, Collina F, Marra L, Liguori G, Franco R, et al. Molecular strategies for detecting chromosomal translocations in soft tissue tumors (review). *Int J Mol Med* 2014;33(6):1379-1391. PMID 24714847. PMC4055444. doi 10.3892/ijmm.2014.1726. Source of the type 5 definition, the second TAF15 exclusivity statement, and the TCF12 genomic-only intron 5 breakpoint quoted in section 3.1.
6. Agaram NP, Zhang L, Sung YS, Singer S, Antonescu CR. Extraskeletal myxoid chondrosarcoma with non-EWSR1-NR4A3 variant fusions correlate with rhabdoid phenotype and high-grade morphology. *Hum Pathol* 2014;45(5):1084-1091. PMID 24746215. PMC4015728. doi 10.1016/j.humpath.2014.01.007.
7. Panagopoulos I, Mertens F, Isaksson M, Domanski HA, Brosjö O, Heim S, et al. Molecular genetic characterization of the EWS/CHN and RBP56/CHN fusion genes in extraskeletal myxoid chondrosarcoma. *Genes Chromosomes Cancer* 2002;35(4):340-352. PMID 12378528. doi 10.1002/gcc.10127. Counted series: of the 15 EWS/NR4A3 cases, 10 carried exon 12 to exon 3 (type 1) and 2 carried exon 13 to exon 3 (type 5).
8. UniProt and Ensembl reference records for EWSR1 (ENST00000397938), NR4A3 (ENST00000395097), TAF15, FUS and TCF12 (UniProt Q99081), as retrieved into the input cache in section 7.

---

## Appendix A. Superseded and corrected values

Per [CLAUDE.md](../../../CLAUDE.md) rule 1.2, a corrected value is registered rather than dropped, and
the live text above carries only the current value.

| superseded | current | where it lived | why it changed |
|---|---|---|---|
| **"EMC's canonical fusion is EWSR1 exon 7 :: NR4A3 exon 3, i.e. `EWSR1(1–264)`."** Used by [`emc_fet_idr_census.py`](../../modalities/emc_fet_idr_census.py) (`emc_canonical_EWSR1_NR4A3`), by [`emc-post-degrader-options.md`](../program/emc-post-degrader-options.md) route 1, and by [`target-route-options.md` §1.3](../program/target-route-options.md) | The primary literature reports **EWSR1 e12 :: NR4A3 e3 (type 1, commonest)** and **EWSR1 e7 :: NR4A3 e2 (type 2)**; §3.1 | those three files, and §2.2 of this document before this revision | Superseded 2026-08-03. The combination "e7 :: e3" pairs the 5′ side of one reported type with the 3′ side of another and is not itself a reported type. ⚠ The census row remains **valid arithmetic for a 264-residue EWSR1 cut** and remains the right comparator for EWSR1::FLI1 type 1 — what changed is the label "canonical", which now belongs to the exon-12 cut. Retained here because the old figure (`0 of 30 RG`) is quoted in live text elsewhere. ⛔ **AND THE CENSUS KEY ITSELF IS NOW RETIRED (2026-09-02, `AUT-PD-208`):** `emc_fet_idr_census.py` no longer writes `emc_canonical_EWSR1_NR4A3`. It writes `emc_EWSR1_NR4A3_reported_types`, a map over reported types 1, 2 and 5 read from this document's own sourced junction registry, and it computes the RGG comparison **per type** rather than as one flag — so the census and Table 4 below now carry the same three fusions. |
| **The type-2 fusion protein modelled as `EWSR1(1–264)::NR4A3(1–626)`** — [`fusion_cofold.py`](../../modalities/fusion_cofold.py)'s `EWS_CUT = 264` with *"NR4A3 resumed at res 2"* | `EWSR1(1–264) :: [59 UTR-encoded residues] :: NR4A3(1–626)`; §3.3 | `fusion_cofold.py`, and any construct built from the protein-level model | The named 3′ exon of the type-2 junction is entirely non-coding, so 176 nt of NR4A3 5′-UTR sit downstream of the EWSR1 cut and, read in EWSR1's frame, encode 59 residues with no intervening stop. ⚠ A computed consequence of the canonical transcripts for the reported junction, not an observed protein |
| **"NR4A3 exon 3"** as resolved by a coding-exon offset table indexed with transcript exon numbers, which returned transcript exon 5 | Transcript-level exon numbering throughout, with four gene-model assertions and three per-construct self-checks; §2.1, §3.2 | a committed artifact, corrected at [`target-route-options.md` §1.3](../program/target-route-options.md) | The off-by-two deleted NR4A3's AF-1 domain and the first zinc finger of its C4 DNA-binding domain from all seven emitted junctions, modelling a chimera that could not do what the real fusion is reported to do. ✅ **NOT superseded by anything in this revision:** both reported EMC types retain NR4A3 from its own first coding exon, so AF-1, the C4 zinc finger and the LBD are present under either type |
| **"One home for the machine-readable versions: `rgg_dose_calibration_and_predictions.registered_predictions`",** applied to all five predictions P1–P5 | P1–P4 are in `registered_predictions`; **P5 is in `tcf12_negative_control.registered_prediction`**; Table 6 | §3.3 of this document before this revision | The pointer was wrong for P5. `registered_predictions` holds four entries and has never held P5, so a reader following the pointer for the one prediction that can falsify the hypothesis would have found nothing |
| **"Three independent tests"** heading a list of **four** items in the TCF12 section | Three independent tests plus one breakpoint-independent sweep; §2.3, §3.5 | §4.1 of this document before this revision | The artifact's own verdict field describes three tests with the FET-vs-FET pairs as the positive control for the third, and records the prefix sweep separately as `test_4_breakpoint_independent_sweep`. The count in the prose disagreed with the count in the list beneath it |
| **The document's framing as an unpublished collaborator package** — *"What this is: everything a group that already runs the FET-fusion DSB-recruitment assay would otherwise have to derive… What it is not: a request to be convinced by an argument"* | A short computational research article for *Genes, Chromosomes and Cancer* with the preprint on bioRxiv, whose Discussion is the pre-specified prediction set | the whole document before this revision | An ask reaches a laboratory only through the published record (CLAUDE.md §5), and the package's four computed results carry a paper on their own. ⚠ **Registered Report Stage 1 was the closer fit on FORMAT and was rejected on ELIGIBILITY:** in-principle acceptance is a commitment that the submitting authors then run the approved protocol, and this programme has no laboratory, no affiliation and no engaged collaborator, so it cannot enter that commitment. The pre-commitment is supplied instead by the dated preprint and the committed artifact |
| **The repository-register presentation** — glyph-led warning blocks, bold on load-bearing clauses, sentence-shaped headings, running commentary on the document's own honesty (183 bold runs at 42.4/1000 words and 65 em-dashes at 15.1/1000) | Journal register: 0 findings from [`lint_style.py`](../lint_style.py) | the whole document before this revision | That register is correct in a repository document, where the reader is a maintainer being stopped from repeating a specific mistake, and wrong in a submission text, where prose asserting its own honesty reads as advocacy (CLAUDE.md §7, gate 5). No claim, figure or caveat was dropped in the conversion; the superseded presentation is recorded here because the earlier text is quoted elsewhere |

| **Reference 1 cited as a bioRxiv preprint** — *"FET fusion oncoproteins disrupt physiologic DNA repair and create a targetable opportunity for ATR inhibitor therapy. bioRxiv 2023. PMID 37205599. doi 10.1101/2023.04.30.538578"* | The peer-reviewed version: Gracilla DE, Menon S, Breese MR, Lin YP, Dela Cruz FS, Feinberg TY, et al. *Cancer Research* 2026;86:2660-2677. PMID 41811428. PMC13223543. doi 10.1158/0008-5472.can-25-2166 | §8 reference 1, and §1 where the source was introduced as "a recent report" | A DOI-keyed retrieval on 2026-08-09 returned the published version ([`citation-corrections-2026-08-09.json`](../../literature/citation-corrections-2026-08-09.json)). The first-author order differs between the two versions, Menon S on the preprint and Gracilla DE on the published paper, so the author string above is the published one. ⚠ **Nothing measured changes and the transfer argument is unchanged:** the replication-stress vulnerability is still inherited from the FET fusion class and still untested on an NR4A3 fusion (§6 item 7). The apparent disagreement between two committed artifacts about the preprint's identifier was adjudicated later the same day and both were reporting correctly for their own dates. On 2026-08-07 the query `EXT_ID:37205599 AND SRC:MED` returned `hitCount: 1` for that preprint under PMID 37205599 and PMC10187251, recorded verbatim in [`atr-hrd-sarcoma-series-inputs.json`](../../modalities/atr-hrd-sarcoma-series-inputs.json); on 2026-08-09 the identical query returned nothing, while the same query form resolved a control identifier normally. The identifier stopped resolving between the two dates. Nothing in the citing prose was fabricated, and no claim that this identifier names nothing may be repeated. The citation above is the published version, which is correct on every reading |

**Superseded document title.** *"The EMC arm, pre-built — a collaborator package for the FET / ATM /
ATR laser-microirradiation assay"*, carried in both the frontmatter and the H1 until this revision
and quoted as this endpoint's title in
[`systems/views/L3-publications.md`](../../../systems/views/L3-publications.md) and in
[`emc-atr-vulnerability-assessment.md`](./emc-atr-vulnerability-assessment.md). Replaced by the
title above, which names what the paper measures rather than who it is addressed to. ⚠ The
generated view is stale until `python3 systems/systems_check.py --write-views` is run, and two
`owner.anchor` fields in [`systems/graph/instruments.json`](../../../systems/graph/instruments.json)
(`INS-CONSTRUCT-DESIGNS`, `INS-FUSION-COFOLD`) still point at the retired §7.2 anchor and must be
repointed to `#32-gene-models-and-open-reading-frames`.
