---
id: DOC-EMC-SURFACE-TARGET-LANDSCAPE
title: "Surface-antigen prioritisation in extraskeletal myxoid chondrosarcoma: a lineage-surrogate ranking tested against three tumour-tissue cohorts"
level: L3
kind: manuscript
status: live
canonical_for:
  - the surface-antigen prioritisation for EMC and what EMC tumour tissue says about it
  - the grade of RT-B7H3
purpose: >
  Submission text for PUB-SURFACE-TARGETS, prepared to British Journal of Cancer Article format with a
  bioRxiv preprint as the free open copy. Reports a two-stage in-silico study: a lineage-surrogate
  surfaceome ranking with a normal-tissue prior, and the test of that ranking in three EMC
  tumour-tissue cohorts. Supplementary material is in emc-surface-target-landscape-si.md.
scope: >
  Public expression data only. Transcript abundance, never protein; never surface localisation,
  receptor density, selectivity, safety, a therapeutic window or clinical readiness. None of those
  quantities is computed in this document or in any artifact it cites.
audience: [external reviewers, collaborators, maintainers, autonomous research agents]
date: 2026-08-09
last_verified: 2026-08-09
related: [DOC-EMC-SURFACE-TARGET-LANDSCAPE-SI]
---

# Surface-antigen prioritisation in extraskeletal myxoid chondrosarcoma: a lineage-surrogate ranking tested against three tumour-tissue cohorts

**Tristan D. McRae**

*Independent researcher, unaffiliated.* Correspondence: trimcrae@gmail.com
ORCID: [ORCID TO BE SUPPLIED BY THE AUTHOR BEFORE SUBMISSION]

Running title: Surface-antigen priorities in EMC

<!-- EDITORIAL, NOT FOR SUBMISSION.
VENUE: British Journal of Cancer (Springer Nature), article type Article, with a bioRxiv preprint as
the free open copy. An accepted paper may be published by the traditional subscription route at no
charge to the author; gold open access is an optional paid upgrade. That is the zero-cost route this
programme requires.
SUPERSEDED, RETAINED: this note previously quoted the upgrade as "3,580 EUR / 4,480 USD / 3,060 GBP",
taken from a web-search snippet. A bibliographic database reports USD 4,690. The figure is not the
one any decision here rests on, since the charge is declined, but the discrepancy is the measurable
reason the search-snippet method was replaced. Neither number is publisher-page verified.
FEE ROUTE: THE $0 SUBSCRIPTION ROUTE IS NOW VERIFIED AT PRIMARY SOURCE (2026-08-10). The publisher
policy pages were retrieved from a GitHub Actions runner rather than from this sandbox, because the
per-journal pages return HTTP 403 to both. Full record with verbatim quotations, URLs and HTTP
statuses: research/literature/venue-fee-routes-2026-08-10.json.
The journal's own open-access page states that gold open access requires an article processing charge,
and that authors choosing "the standard subscription publication route" need only complete the
standard Licence to Publish form. The journal is recorded as not open access and not in DOAJ.
THE COLOUR CHARGE IS CONFIRMED at the journal's own guide to authors, verbatim: "There is a charge if
authors choose to publish their figures in colour in the print publication (which includes the online
PDF). Colour charges will not apply to authors who choose to pay an article processing charge to make
their paper Open Access." It is an author CHOICE, so the $0 route holds provided figures are
submitted greyscale.
STILL NOT VERIFIED, and stated as such: the per-journal author-guideline pages return 403 from CI as
well, so the word, abstract and display-item limits written into this manuscript remain
search-derived. Those affect FORMAT, which an editor returns, not COST, which is billed. And the
APC figure itself comes from a bibliographic database rather than the publisher page; it is not the
number the decision rests on, since the charge is being declined.
AUTHOR BLOCK matches the author block already committed in nr4a3-degrader-paper.md and
response-endpoint-indolent-tumours.md. No ORCID is given because the repository carries none, and
only the author can supply one; the sibling submission texts carry the same statement.
COMMENT TERMINATOR ADDED 2026-08-10. This editorial block opened at "<!-- EDITORIAL" and was never
closed, so every renderer treated the whole manuscript from that line down as an HTML comment, and
submission_metrics.py's comment strip, which requires the closing token, silently did nothing. The
terminator below ends the block where the sibling manuscripts end theirs, immediately before the
preprint-deposit declarations.
-->

> **Declarations for preprint deposit.** Ethics approval and consent were not required and were not
> sought. This study analyses public gene-expression deposits and public annotation resources only. It
> involves no human participants, no identifiable data, no patient-level record and no laboratory work.
> **Funding:** none. **Competing interests:** none. **Data and code:** see Declarations.

> **Scope of the claims.** Every quantity reported here is transcript abundance. No protein
> measurement, no surface-localisation measurement and no receptor-density measurement appears in this
> paper or in any artifact it cites. Nothing here asserts that any antigen is a validated target in
> extraskeletal myxoid chondrosarcoma, that any agent is safe or effective in it, that any therapeutic
> window exists, or that any route is ready for clinical use.

## Abstract

**Background.** Extraskeletal myxoid chondrosarcoma (EMC) is a rare sarcoma driven by the *EWSR1::NR4A3*
fusion, a nuclear transcription factor. Cell-surface antigens offer a delivery axis gated differently
from driver-directed routes, but EMC surface-antigen expression has not been systematically mapped, so
prioritisation has run on lineage surrogates.

**Methods.** A 2,826-gene human surfaceome was ranked across a translocation-sarcoma DepMap class
(n = 76 lines) by a rank-based, Benjamini-Hochberg-corrected selectivity test, then filtered by a Human
Protein Atlas normal-tissue prior. Those priorities were then tested in three EMC tumour-tissue cohorts:
GSE24369 (6 EMC versus 29 sarcomas), GSE4303 on GPL3290 (10 versus 6) and GSE28866 (4 EMC, 27
normal-organ and 32 sarcoma libraries).

**Results.** Eight antigens were selective in the surrogate and B7-H3/CD276 was not (q = 1.0); the
normal-tissue prior left no evaluated antigen both selective and restricted. In tumour tissue, none of
the eight was concordantly elevated on both arrays and two were concordantly lower. None of eleven
therapeutic addresses named by candidate routes was concordantly elevated. ALCAM rose on both arrays yet
sat below the normal-organ median.

**Conclusions.** Surrogate-derived surface priorities did not transfer to EMC tissue: the surrogate's
negatives transferred and its positives did not.

## Keywords

Extraskeletal myxoid chondrosarcoma; EWSR1::NR4A3; surfaceome; tumour antigen; on-target off-tumour
exposure; sarcoma; ALCAM; CSPG4; surrogate validity.

## Background

Extraskeletal myxoid chondrosarcoma is a rare soft-tissue sarcoma defined by a translocation fusing the
5' region of *EWSR1*, less often *TAF15* or another FET gene, to the orphan nuclear receptor *NR4A3*,
producing a chimeric transcription factor on a genome with few recurrent secondary mutations [16,17]. A 2025
comprehensive review of the disease states that no clinically validated agent directly targets NR4A3
[1]. Immunohistochemical series support a neuroendocrine phenotype, with INSM1 a diagnostically useful
marker [2].

Because the driver is nuclear, driver-directed therapy confronts a druggability or
oligonucleotide-delivery gate. Cell-surface antigens enable modalities that move the problem elsewhere:
antibody-drug conjugates, T-cell engagers, chimeric antigen receptor cell products and radioligand
therapy. That axis carries its own gates, and it gives up the fusion-level specificity that a
nucleic-acid route uniquely offers, since every surface antigen considered below is a generic
lineage antigen with no mechanistic link to the fusion.

Surface-antigen prioritisation for EMC has had to run on surrogates because the disease was taken to be
absent from usable public expression data. A prior-art screen run for this work supports the underlying
gap. A Europe PMC retrieval of 322 EMC-linked records, 238 of them with full text, was hand-screened for
surfaceome, surface antigen, cell-surface protein, chimeric antigen receptor, radioligand,
antibody-drug conjugate and immunotherapy terms. It returned three EMC-specific records, none of which
is a systematic surface-antigen map: a radiotherapy case report [3], a single case describing an
immunosuppressive tumour microenvironment in EMC with pleural metastases [4], and a multidisciplinary
review of uncommon soft-tissue sarcomas [5]. That screen matched titles and abstracts, not full text, so
it establishes that nothing is indexed on those pairings rather than that no such work exists; a
surface-antigen analysis inside a supplementary table of a larger sarcoma paper would be invisible to
it.

That assumption is tested here. Three EMC tumour-tissue cohorts are readable at no cost, two of them
only after a probe-to-symbol accession bridge was built. The study therefore has two stages: a
surrogate-based prioritisation, and the test of that prioritisation against the disease it was built
for. Surrogate-based target lists are routinely built for rare tumours, and the outcome when the
tumour itself is measured is rarely reported.

## Methods

All analyses are computational, use public data, run in continuous integration at no compute cost, and
commit their outputs. No laboratory work was performed. Full parameters, controls and per-gene tables
are in Supplementary Methods S1 to S6 and Supplementary Tables S1 to S8.

### Surfaceome definition

UniProt-reviewed human proteins carrying a plasma-membrane location (SL-0039) together with a
transmembrane (KW-0812) or GPI-anchor (KW-0336) topology were unioned with a curated seed of 47
actionable surface antigens, so that established targets were always evaluated. An established
machine-learning surfaceome resource exists [13]; it was not used, because the annotation-derived
construction above is reproducible from public identifiers alone and its membership rule can be
stated in one sentence, and the two sets are not interchangeable. The committed run used
2,820 UniProt genes plus the seed, of which 41 were already in the UniProt set, giving 2,826 unique
genes, 2,692 of which were present in the DepMap expression matrix and were scanned. The seed is a
small and largely redundant minority, so the set is largely but not strictly unbiased. The scanned gene
list itself was not recorded, which is why the coverage gap described in Results is undecidable rather
than resolvable.

### Expression and selectivity in the surrogate class

DepMap OmicsExpression values, log2(TPM+1). A translocation-sarcoma class was defined by OncotreeSubtype
(Ewing, synovial, alveolar, desmoplastic small round cell, clear-cell, plus the single line annotated
*Extraskeletal Myxoid Chondrosarcoma*; n = 76) as a lineage-generic surrogate. That line, ACH-001519, is
recorded by Cellosaurus as not harbouring an *EWSR1* fusion [15], so it is treated as one of 45 class
members carrying expression data and not as EMC evidence; the record and its consequences are in
Appendix A.
For each surface gene the scan reports expression, an effect size against non-sarcoma lineages, and a
rank-based one-sided Mann-Whitney *p* that the class exceeds the rest, Benjamini-Hochberg corrected.
This is cross-cancer selectivity, a descriptor of distinguishability from other tumour lineages, and not
a tumour-versus-normal contrast; it mechanically favours mesenchymal antigens because the DepMap panel
is epithelial-dominated.

Four limits of this instrument were computed (Supplementary Note S1). The scanned
population is tumour-cell monoculture, so it contains no stromal or fibroblast compartment. An antigen
carried only by stroma reads at the floor, demonstrated by LRRC15, an established sarcoma
cancer-associated-fibroblast antigen with a clinical antibody-drug conjugate programme behind it, at
`frac_expressed` 0.0. A glycan such as oncofetal chondroitin sulfate is the product of a biosynthetic
pathway rather than of one gene [14], and so cannot be ranked.
And CSPG4 has no per-gene row in any committed artifact of this instrument.

### Normal-tissue prior

Each antigen was queried against the Human Protein Atlas [6] for RNA tissue specificity, tissue
distribution, per-tissue nTPM, blood-cell specificity and subcellular location, and given a verdict with
Human Protein Atlas semantics. Only tissue-enriched or group-enriched antigens with a restricted
distribution, no vital-tissue signal and no strong immune or circulating signal were classed RESTRICTED.
Tissue-enhanced antigens, detected broadly with a peak, were classed ENHANCED_BROAD. Low tissue
specificity, or a detected-in-all distribution, gave BROAD_LIABILITY. Expression in a vital tissue, or a
confined blood signal, overrode all others as VITAL_OR_IMMUNE_LIABILITY. Controls behaved as specified:
DLL3 and GPC3 returned RESTRICTED, B2M returned BROAD, and the hard control CD3E returned a vital or
immune liability. Human Protein Atlas RNA is bulk normal tissue and a prior, not a safety statement.

### EMC tumour-tissue cohorts

Three deposits were read (Table 2). GSE24369, on GPL6244, carries 6 EMC against 29 comparator sarcomas
(17 low-grade fibromyxoid sarcoma, 6 desmoid fibromatosis, 6 fibrosarcoma) and supplies a lineage axis.
GSE4303 on GPL3290 carries 10 EMC against 6 comparators (3 dermatofibrosarcoma protuberans, 3
gastrointestinal stromal tumour) and supplies a second lineage axis with different comparators; the
cohort was first published by Subramanian and colleagues [7]. GSE28866, a 3'-end sequencing deposit,
carries 4 EMC libraries, 27 normal-organ libraries (bowel, breast, colon, kidney, lung, uterus) and 32
non-EMC sarcoma libraries, and supplies both a lineage axis and the on-target off-tumour exposure axis.

The two axes are different questions and are not collapsed. The 27 normal libraries are visceral organs
containing almost no soft tissue, so a gene high in EMC against that panel is not thereby shown to be
EMC-specific rather than mesenchymal-lineage-specific; and a gene high against other sarcomas says
nothing about normal-organ exposure. Read densities from 3'-end sequencing are not array intensities and
are never pooled with them. Array figures are Δ, the EMC mean z minus the comparator mean z in standard
deviation units of that array's own probe distribution, with Welch *t* and degrees of freedom.
Sequencing figures are ratios of medians of per-peak medians and carry no test.

### Cross-platform state and readability

GPL3290 probes carry expressed-sequence-tag accessions only, so a gene can be unreadable there purely
because its accession did not resolve through the curated dictionary, UniGene archive and live-query
bridge. Every gene therefore carries a cross-platform state: CONCORDANT_UP_ON_BOTH,
CONCORDANT_DOWN_ON_BOTH, DISCORDANT_OPPOSITE_SIGNS, MOVED_ON_ONE_FLAT_ON_THE_OTHER, FLAT_ON_BOTH,
READABLE_ON_ONE_PLATFORM_ONLY or NOT_READABLE_ON_EITHER_PLATFORM. The last two describe the
instrument rather than the biology. CD248, CD276 and SSTR2 are unreadable on GPL3290, and no
statement below treats unreadability as evidence about their expression. A curated panel is
scored only above a floor of 3 readable genes and 0.5 coverage; panels below the floor emit no score.

### Controls and multiple testing

Three genes with known answers were read on the same platforms before any antigen. *NR4A3* must rise,
because its over-expression defines the disease; *ENO3*, a reported direct transactivation target of an
NR4A3 fusion [8], must rise; *MKI67* must be approximately flat, because EMC is slow-cycling and a large
proliferation difference would indicate a contrast driven by cellularity. Results are in Supplementary
Table S4. No multiple-testing correction is applied anywhere in the tissue read. The reads were
specified before the tables were parsed, and each is reported with its *t* and degrees of freedom so
that a reader can apply their own correction. A threshold on |*t*| in a verdict string is a readability
aid rather than a test.

### Use of large language models

Analysis code, data processing and manuscript drafting were carried out with substantial assistance
from a large language model under the author's direction. The author designed the study, specified
every read and threshold in advance, and verified each reported value against the committed
artifact that produced it. No large language model is an author, and none is accountable for the
work. Every number in this manuscript is reproducible offline from the artifacts named in the data
availability statement, without any language model.

## Results

### Stage-1 selectivity and the normal-tissue prior

In the surrogate class, selectivity was significant for CDH11, KIT, FGFR1, NCAM1, GPC2, PTK7, MCAM and
EPHB4, and was absent for B7-H3/CD276 at q = 1.0, for EGFR and for FAP (Table 1). Two cautions apply to
the whole column. The contrast is cross-cancer, which the epithelial-dominated DepMap panel biases
toward mesenchymal antigens, so CDH11 at +3.18 log2TPM is largely a statement that carcinomas do not
express it. And transcript magnitude to two decimal places conveys false precision about surface-protein
density; the values are coarse tiers.

B7-H3, the field's default surface target for sarcoma, is not significantly selective in these data.
B7-H3 protein can be tumour-restricted despite broad transcript expression, which is the basis of its
clinical traction, so this is a selectivity-of-transcript caveat rather than a claim about protein; it
removes the transcriptomic rationale for treating B7-H3 as the obvious first choice.

FAP and CD248 need a further caution. Both are stromal antigens, and the surrogate instrument has no
stromal compartment, with LRRC15 reading at zero expressed fraction in it. A verdict on FAP from this
instrument is a statement about tumour cells in culture rather than about FAP in an EMC tumour.

The normal-tissue prior is the decisive filter, and among the classic protein antigens it evaluated no
antigen was both selective and restricted (Figure 1). Each candidate fails for an identifiable reason.
NCAM1/CD56 sits on natural killer cells and neural tissue, carrying a fratricide risk for cell products
and a circulating compartment; the CD56 antibody-drug conjugate lorvotuzumab mertansine was clinically
developed and discontinued [9,10]. CDH11 is broadly expressed in normal fibroblasts, synovium and bone,
and its high cross-cancer enrichment is the mesenchymal-versus-epithelial artefact described above.
B7-H3, EGFR and FAP are non-selective or broad; FGFR1, MCAM and EPHB4 carry liabilities on this prior.
The one restricted prior among the classic antigens belongs to B4GALNT1, the GD2 synthase, and whether
EMC expresses GD2 is not measured by anything in this study. The intersection was computed over the
antigens the filter saw, and CSPG4 was not among them, so the empty intersection is a property of the
evaluated set.

### Surrogate priorities in EMC tumour tissue

Every antigen the surrogate called selective now has a reading in EMC tumour tissue. None of the eight is
concordantly higher in EMC than in comparator sarcomas on both arrays, and two are concordantly lower
(Table 3). The two antigens the surrogate called non-selective read the same way in tissue: EGFR is
concordantly down on both arrays, and CD276 is lower in EMC on the one platform that reads it. The
surrogate's negatives transferred and its positives did not.

Three qualifications apply to Table 3. It does not refute the surrogate, which asked a different
question, in monoculture, and answered it correctly. It is not corrected for multiple testing. And a
flat or single-platform row does not demonstrate that an antigen is absent.

### Route-named therapeutic addresses

Eleven genes make up the panel of therapeutic addresses named by candidate surface-directed routes for
this disease, assembled from the addresses those routes name plus two coverage corrections, and none of
the eleven is concordantly elevated in EMC tumour tissue (Table 4). CD248 and CD276 read lower on the one
platform that reads them, FAP and PRAME are flat on both, SSTR2 is flat, and the remainder are
discordant or single-platform. Six of these genes gained their first EMC-tissue array contrast in this
work: ALCAM, CD248, CD276, FAP, PRAME and SSTR2.

The single antigen elevated on both arrays is ALCAM, which no candidate route names, and the exposure
axis demotes it. Its EMC median in the sequencing cohort, 0.578, sits below the normal-organ median of
0.631 while remaining above the other-sarcoma median of 0.377. The lineage reading survives and the
exposure reading does not, and for any surface-directed modality the exposure axis decides whether an
address is usable at all. ALCAM as an EMC-versus-sarcoma marker is unaffected; what weakens is ALCAM
as a therapeutic address. The reading rests on one cohort, n = 4, at transcript level, on two
peaks, and is not a safety statement. The two normal-tissue instruments in this study disagree about
ALCAM: the Human Protein Atlas prior classes it RESTRICTED (tissue enriched, detected in many, immune-cell
enhanced), while the sequencing normal arm places its EMC median below the normal-organ median. Neither
instrument measures protein, and the disagreement is not resolved here.

Four rows warrant individual comment. CD248 inverts: it is the surrogate's only selectivity-significant
antigen in this set, at 2.29 log2TPM enrichment with q = 0.0, and in EMC tissue it is lower than
comparator sarcomas on the one platform that reads it and below normal organs in the sequencing cohort.
CD276 points the same way in tissue as in the surrogate, sitting at the 79th array percentile while
reading lower than comparators, which is the profile of an antigen that is expressed and
non-discriminating rather than absent. FAP is flat, and the comparator arm is why that matters: GSE24369
compares EMC with desmoid fibromatosis and fibrosarcoma, fibroblastic lesions in which FAP is expected
to be high, and EMC itself sits at the 88th array percentile, so this is not a reading that EMC lacks
FAP. It indicates instead that a FAP-directed route cannot claim EMC as a selectively FAP-rich
indication among soft-tissue tumours; the whole 13-gene stromal and matrix panel is lower in EMC on both platforms
(Δ = −0.328, *t* = −1.89; Δ = −0.467, *t* = −1.80). PRAME reads at the floor of every readable cohort:
30th array percentile on GPL6244 with Δ near zero, 11th percentile of log-ratios on GPL3290 where its
nominally positive Δ is flat at |*t*| = 1.43, and a sequencing EMC median of 0.102 against an
other-sarcoma median of 0.194, on a single peak.

The precondition for the two human-leukocyte-antigen-directed routes points the wrong way. The
12-gene antigen-presentation panel reads lower in EMC than in comparator sarcomas on GPL6244
(Δ = −0.216, *t* = −2.90, 12 of 12 readable) and on GPL3290 (Δ = −0.228, *t* = −0.84, 11 of 12). The
second is not significant on any reading, and the panel is a precondition rather than a target, but a
T-cell-receptor-directed route needs class-I presentation.

The panel-level score for the route-named addresses disagrees between platforms and is reported as such:
lower in EMC on GPL6244 (Δ = −0.0935, *t* = −1.66, 11 of 11 readable) and higher on GPL3290 (Δ = +0.599,
*t* = 2.91, 8 of 11). The three genes missing from the GPL3290 score are CD248, CD276 and SSTR2, three of
the four that read down or flat on GPL6244, so the two panel scores are not computed over the same set
and the disagreement is partly a coverage artefact. The per-gene table is therefore the interpretable
presentation and the panel scores are not.

### SSTR2 and the GD2 proxy

EMC's reported neuroendocrine differentiation motivated two candidate targets absent from previous EMC
surface discussions: SSTR2, the target of approved somatostatin-receptor radioligand therapy [18], and GD2, a
surface glycolipid with mature cell-product and antibody platforms. Both now have EMC-tissue readings,
and the readings are unsupportive without being decisive.

On GPL6244, SSTR2 sits at the 60th percentile of the array's own probe distribution with Δ = −0.042
(*t* = −0.40) against comparator sarcomas, so it is present, mid-distribution and indistinguishable from
the comparators. It is not readable on GPL3290, and the somatostatin-receptor family panel could not be
scored there at all, with 1 of 5 genes readable against a coverage floor of 0.50, so the artifact emits
no score. On GPL6244 the family panel is flat (Δ = −0.008, *t* = −0.20). In the sequencing cohort EMC
sits at 1.54 times the normal-organ median and 1.37 times the other-sarcoma median, on two peaks and
n = 4.

The GD2 proxy B4GALNT1 is flat on GPL6244 (Δ = −0.069, *t* = −1.00, 49th array percentile) and not
readable on GPL3290, and the whole five-gene glycan-synthase panel is lower in EMC on both platforms
(Δ = −0.147, *t* = −4.96; Δ = −1.050, *t* = −3.44). GD2 is a glycolipid and B4GALNT1 is a synthase, so
this is a proxy for a proxy and cannot exclude the antigen.

These readings change the prior without changing the gate. The hypothesis was that EMC's reported
neuroendocrine phenotype might extend to SSTR2 surface expression at a level worth imaging, and the
first EMC transcript readings show no elevation over other soft-tissue tumours and no striking
absolute signal. The gate is unchanged: a peptide-receptor radioligand route depends on absolute
receptor protein density and on the tumour-to-normal uptake ratio, and no quantity in this study
measures either. A single somatostatin-receptor
positron-emission-tomography scan, or an SSTR2 immunohistochemical stain on archival EMC, remains the
cheap decisive measurement, and these readings lower the prior for it rather than removing the reason to
perform it.

### CSPG4, a gene outside the stage-1 scan

CSPG4 has no per-gene row in any committed artifact of the surrogate instrument, and whether it was ever
scanned is undecidable because the artifact stores gene counts rather than the gene list. Its absence
from the empty selective-and-restricted intersection is therefore a measured coverage gap rather than a
rejection. It matters because CSPG4 is one of the two carrier proteoglycans named by the founding
oncofetal-chondroitin-sulfate work, and the surfaceome seed held only the other one, CD44.

In EMC tissue CSPG4 is the largest absolute row in the sequencing deposit, with an EMC median of 8.730,
an order of magnitude above every other row in that panel, 3.31 times the normal-organ median and 2.51
times the other-sarcoma median. It moves strongly on GPL6244 (Δ = +0.885, *t* = 7.42) and not at all on
GPL3290 (Δ = −0.189, *t* = −0.40). The classifier records this as movement on one platform with
flatness on the other rather than as opposite signs, because the GPL3290 value is negative in sign but
flat in magnitude. The row does not replicate and is also not contradicted. Two candidate explanations
are live and neither is settled here: the GPL3290 comparator arm is n = 6 with an unusually high CSPG4
mean, and dermatofibrosarcoma protuberans is a dermal fibroblastic tumour while CSPG4 is a well-known
melanocytic and pericytic antigen, so a high comparator arm would flatten the contrast for reasons about
the comparator rather than about EMC. The sequencing row rests on one peak and n = 4, and the Human
Protein Atlas already places CSPG4 on the broad-liability list, so its normal-tissue behaviour beyond
those six organs is unaddressed. CSPG4 is therefore held open.

### Genes concordantly elevated on both arrays

Across the 100 genes on the cross-platform board, exactly five are concordantly elevated on both arrays:
VCAN, BGN, CD44, GPC1 and ALCAM (Table 5). Four of the five are matrix or proteoglycan genes, and ALCAM
is the only classical single-pass cell-surface adhesion molecule among them.

Three considerations weaken that reading. The background is saturated: VCAN's EMC samples sit
at the 99.7th and 97.5th array percentiles against comparators at the 97.8th and 91.2nd, so the
separation is small on top of a signal that is high everywhere, and a matrix proteoglycan being abundant
in a myxoid tumour is expected rather than discriminating. These are largely secreted or
matrix-associated products rather than cell-surface addresses, so a versican or biglycan transcript is a
statement about what the tumour deposits rather than about what a binder would find on a cell. And bulk
archival tissue cannot deconvolve compartments, so a matrix or stromal signal may report the
compartment's presence rather than the tumour cell's.

The two instruments invert on the three genes where they can be compared, and the disagreement is not
resolved here. CD248 is the surrogate's only selectivity-significant antigen in this set and is lower in
EMC tissue; ALCAM was scored and rejected by the surrogate and is higher in EMC tissue on both arrays;
CD44 is the surrogate's most strongly negative row here and is higher in EMC tissue on both arrays. Four
explanations are live and nothing in either artifact discriminates them. The two instruments ask
different questions, sarcoma-versus-other-cancer against EMC-versus-other-sarcoma, so opposite answers
are not inconsistent. They read different populations, since the surrogate contains no
verified *EWSR1::NR4A3* line and so holds no EMC observation. They read different compartments, since
monoculture is tumour cells only while bulk tissue adds stroma, vasculature, immune infiltrate and
matrix. And they use different measurements, RNA-sequencing transcripts per million in cultured lines
against array intensity in archival tissue on two decade-old platforms. A single-cell or spatial EMC
dataset would discriminate the compartment explanation directly, and none is in hand.

### Instrument controls

The tissue instrument reproduced its known answers (Supplementary Table S4). *NR4A3* rose in EMC on
GPL6244 (Δ = +0.741, *t* = 4.66, 76th array percentile), and in the sequencing cohort its median across
the 32 non-EMC sarcoma libraries was 0.000 against 0.216 in EMC; it emits no contrast on GPL3290, where
only 2 comparator samples carry a value against a floor of 3. *ENO3* rose on both arrays (Δ = +0.808,
*t* = 3.61; Δ = +3.811, *t* = 13.22). *MKI67* was flat (Δ = +0.129, *t* = 0.53). On the exposure axis,
four antigens with no reason to be present in a soft-tissue sarcoma read lower in EMC than in normal
tissue: GPC3 at 0.09 times, MSLN at 0.27 times, L1CAM at 0.33 times and CDH17 at 0.91 times. A working
control licenses reading the other rows and is not evidence for any of them.

## Discussion

In-silico surface-target discovery for this disease does not deliver a clean target, and when its
output is checked against the disease's own tissue the leads largely do not reproduce. The
contribution is therefore an estimate of how far a lineage-surrogate surface ranking transfers to the
disease it was built for, rather than a target list; here the negatives transferred and the
positives did not. That asymmetry has a testable mechanism: a cross-lineage selectivity test measures
mesenchymal rather than epithelial character, which is a property EMC shares with every comparator in
the tissue cohorts, so it cannot discriminate within them. The caution applies to every surrogate-based
rare-tumour target list, not only to this one.

Three outputs survive as usable. First, a set of negatives with a named basis: B7-H3 is not a
differentially expressed EMC address on either instrument; the stromal panel is lower in EMC than in
comparator sarcomas on both platforms; PRAME reads at the floor of every readable cohort. Second, a
demoted but intact marker: ALCAM separates EMC from other sarcomas across three cohorts and three
platform families, which is a marker-grade result even though the same data removes its case as a
therapeutic address. Third, a held-open lead with a stated defect: CSPG4, which the original search never
evaluated.

A surrogate ranking plus a normal-tissue prior did not suffice to prioritise scarce validation effort
for this rare tumour, and the check that showed as much required no new data.

The modality axis carries its own gates. The abundant myxoid and chondroid extracellular matrix is a
diffusion and binding-site barrier to antibodies, adoptive cells and radioligands, and adult sarcoma has a poor record for cell products and engagers in cold,
immune-excluded tumours; a single reported EMC case describes exactly such an immunosuppressive
microenvironment [4]. The genes concordantly elevated in EMC tissue are largely the matrix itself, so the
compartment that most complicates delivery is also the compartment carrying most of the differential
signal. One modality-specific consequence follows from the exposure axis: an antigen elevated against
other sarcomas but not against normal visceral organs, which is ALCAM's exact profile, is a usable
diagnostic or lineage marker and a poor address for any modality that acts wherever the antigen is.
Radioligand crossfire mitigates heterogeneous tumour uptake rather than broad normal expression; for a
normal-tissue antigen, crossfire widens the irradiated field.

### Limitations

The binding limitation of this work is no longer its comparator basis, which three EMC tissue cohorts
now replace. It is twofold. Everything measured here is transcript abundance, and every address named
above, ALCAM, CSPG4, CD248, CD276, SSTR2, FAP, PRAME and GD2, is a protein or glycan question. A
transcript says nothing about whether the protein reaches the plasma membrane, at what density, or
whether the epitope a binder needs is exposed; transcript-to-protein correlation for membrane proteins
is modest and is not measured here. A high transcript reading is a reason to stain rather than an antigen
call. And the tissue cohorts are small archival bulk deposits on decade-old platforms: n = 6, n = 10 and
n = 4, with the exposure axis resting on medians of four libraries against six visceral organ types.
None of these readings supports a population-level statement.

Several further constraints apply to every number above. Read densities from 3'-end sequencing are never
pooled with array intensities. Several genes rest on a single peak in the sequencing deposit, among them
CSPG4, FAP, GPC3, L1CAM and PRAME, and several array rows rest on a single probe. The 27 normal libraries
are a tissue panel rather than matched adjacent tissue, covering six organ types. The two lineage
cohorts have different comparator arms, so a gene can move in one and not the other because the
comparator changed rather than because EMC did, which is the worked explanation for CSPG4. GPL3290 is a
two-colour log-ratio platform, so an absolute level there means relative to the reference pool and only
the between-group contrast is interpretable. CD248, CD276, SSTR2, GPC2 and B4GALNT1 are unreadable on
GPL3290 and ALPPL2, CTAG1B, MAGEA3, NECTIN4 and SSX2 on both, and no statement above treats any of them
as low. Bulk archival tissue is not deconvolved, so a stromal or pericyte antigen can read high because
the compartment is present. Sample classification is string matching on the verbatim deposit annotation,
which is reproduced in the artifact so that a mis-bucketed sample is auditable without another run. No
multiple-testing correction is applied. On the surrogate side, no verified EMC observation enters it at
all, the surrogate is lineage-generic, the scanned gene list was never recorded, and the instrument has
no stromal compartment. Clinical-agent and EMC-biology citations marked in the reference list as not yet
retrieved must be sourced before use.

### Conclusion

This in-silico analysis does not deliver a clean EMC surface target, and when its output
is checked against the disease's own tumour tissue the leads largely do not reproduce. None of the eleven
therapeutic addresses named by candidate routes is concordantly elevated in EMC relative to comparator
sarcomas, none of the eight surrogate-selective antigens is concordantly elevated on both arrays, and the
one antigen that is elevated on both, ALCAM, shows no separation from normal visceral organ tissue on the
only cohort able to measure that. What survives is a set of negatives with a named basis, a demoted but
intact lineage marker, one held-open lead the original search never evaluated, and a caution about
surrogate-based target lists for rare tumours.

The measurement that would decide the question is EMC surface protein expression with a normal-tissue
comparison, on a cohort large enough to carry a distribution. Two groups hold patient-derived EMC models,
USZ-EMC [11] and NCC-EMC1-C1 [12], and those models remain the route to EMC data that public deposits
cannot supply. Four questions are now sharp enough to be worth a targeted panel: whether ALCAM protein is
on the EMC cell surface and at what density relative to normal visceral tissue; whether CSPG4 protein is
present; whether SSTR2 is detectable by immunohistochemistry or somatostatin-receptor imaging at all; and
whether any protein-level reason remains to keep B7-H3 on the list. A single-cell or spatial EMC dataset
would be worth more than any of these individually, because it is the one measurement that discriminates
the four explanations for the disagreement between the two instruments.

## Display items

**Table 1.** Surrogate-class selectivity and normal-tissue prior for the evaluated classic antigens.
Enrichment is class mean minus rest mean, log2(TPM+1); *q* is the Benjamini-Hochberg-corrected
one-sided Mann-Whitney value; the verdict is the Human Protein Atlas window classification.

| Antigen | Enrichment (log2TPM) | BH *q* | Selective | Normal-tissue verdict |
|---|---|---|---|---|
| CDH11 | +3.18 | ~0 | yes | ENHANCED_BROAD |
| KIT | +2.46 | ~0 | yes | VITAL_OR_IMMUNE_LIABILITY |
| CD248 | +2.29 | 0.0 | yes | VITAL_OR_IMMUNE_LIABILITY |
| FGFR1 | +1.99 | ~0 | yes | BROAD_LIABILITY |
| NCAM1/CD56 | +1.74 | ~0 | yes | VITAL_OR_IMMUNE_LIABILITY |
| GPC2 | +1.49 | ~0 | yes | ENHANCED_BROAD |
| PTK7 | +1.24 | 2e-4 | yes | VITAL_OR_IMMUNE_LIABILITY |
| MCAM/CD146 | +1.09 | 3e-3 | yes | BROAD_LIABILITY |
| EPHB4 | +1.00 | 3e-4 | yes | BROAD_LIABILITY |
| B7-H3/CD276 | +0.14 | 1.0 | no | BROAD_LIABILITY |
| FAP | +0.02 | 0.16 | no | ENHANCED_BROAD |
| LRRC15 | −0.25 | 1.0 | no | not scored in this filter |
| ERBB2 | −0.52 | 1.0 | no | BROAD_LIABILITY |
| ALCAM | −1.45 | not significant | no | RESTRICTED |
| EGFR | −2.21 | 1.0 | no | ENHANCED_BROAD |
| B4GALNT1 (GD2 synthase) | not in the scan output | not in the scan output | not evaluated | RESTRICTED |
| SSTR2 | not in the scan output | not in the scan output | not evaluated | ENHANCED_BROAD |
| CSPG4 | no per-gene row (coverage gap) | no per-gene row | not evaluated | ENHANCED_BROAD |

**Table 2.** The three EMC tumour-tissue cohorts.

| Cohort | Platform | EMC | Comparator arm | Axis supplied |
|---|---|---|---|---|
| GSE24369 | GPL6244, single-channel array | 6 | 29 sarcomas: 17 LGFMS, 6 desmoid fibromatosis, 6 fibrosarcoma | lineage |
| GSE4303 | GPL3290, two-colour cDNA, log-ratio | 10 | 6 sarcomas: 3 DFSP, 3 GIST | lineage, second comparator set |
| GSE28866 | 3'-end sequencing, read density | 4 | 27 normal-organ libraries and 32 non-EMC sarcoma libraries | exposure and lineage |

**Table 3.** Surrogate-selective antigens read in EMC tumour tissue. Δ is the EMC mean z minus the
comparator mean z in standard deviation units of that array's probe distribution, with Welch *t*.

| Antigen | Surrogate BH *q* | GPL6244 Δ (*t*) | GPL3290 Δ (*t*) | Cross-platform state |
|---|---|---|---|---|
| FGFR1 | ~0 | −0.778 (−4.54) | −1.940 (−12.19) | concordant down on both |
| PTK7 | 2e-4 | −0.524 (−3.87) | −0.658 (−4.55) | concordant down on both |
| CDH11 | ~0 | +0.318 (+2.65) | −1.181 (−3.78) | discordant, opposite signs |
| MCAM/CD146 | 3e-3 | −0.288 (−2.65) | +0.279 (+1.18) | moved on one, flat on the other |
| KIT | ~0 | +1.353 (+3.03) | +0.399 (+0.55) | moved on one, flat on the other |
| NCAM1/CD56 | ~0 | −0.268 (−1.08) | +1.028 (+1.97) | flat on both |
| EPHB4 | 3e-4 | +0.050 (+0.56) | +0.614 (+1.72) | flat on both |
| GPC2 | ~0 | −0.015 (−0.36), 31st percentile | not readable | readable on one platform only |
| EGFR (not selective) | 1.0 | −0.619 (−3.41) | −0.670 (−2.02) | concordant down on both |
| CD276 (not selective) | 1.0 | −0.249 (−2.55) | not readable | readable on one platform only |

**Table 4.** Therapeutic addresses named by candidate surface-directed routes, read in EMC tumour
tissue, with ALCAM added as the one concordantly elevated antigen that no route names. Sequencing
columns are ratios of medians and carry no test.

| Address | GPL6244 Δ (*t*), EMC percentile | GPL3290 Δ (*t*) | vs 27 normal organs | vs 32 other sarcomas | State |
|---|---|---|---|---|---|
| CD248 | −0.698 (−2.32), 59th | not readable | 0.84× | 0.65× | readable on one platform only |
| CD276/B7-H3 | −0.249 (−2.55), 79th | not readable | 1.30× | 1.42× | readable on one platform only |
| FAP | −0.265 (−0.81), 88th | −0.144 (−0.55) | 1.63× | 1.59× | flat on both |
| SSTR2 | −0.042 (−0.40), 60th | not readable | 1.54× | 1.37× | readable on one platform only |
| PRAME | −0.004 (−0.05), 30th | +0.868 (+1.43), 11th | normal median 0.000 | 0.53× | flat on both |
| CSPG4 | +0.885 (+7.42), 81st | −0.189 (−0.40) | 3.31× | 2.51× | moved on one, flat on the other |
| ALPP | −0.021 (−0.34), 32nd | +0.315 (+1.59) | not in panel | not in panel | flat on both |
| MSLN | −0.086 (−2.53), 42nd | +0.835 (+2.10) | 0.27× | 1.23× | discordant, opposite signs |
| GPC3 | −0.508 (−3.25), 28th | +0.804 (+2.15) | 0.09× | 0.48× | discordant, opposite signs |
| L1CAM | +0.096 (+0.86), 44th | +1.883 (+3.93) | 0.33× | 1.62× | moved on one, flat on the other |
| CDH17 | −0.135 (−4.67), 14th | +0.515 (+0.92) | 0.91× | 0.50× | moved on one, flat on the other |
| ALCAM (no route names it) | +1.091 (+7.01), 99th | +0.753 (+2.21) | 0.92× | 1.53× | concordant up on both |

**Table 5.** The five genes concordantly elevated in EMC on both arrays.

| Gene | GPL6244 Δ (*t*) | GPL3290 Δ (*t*) | vs 27 normal organs | vs 32 other sarcomas |
|---|---|---|---|---|
| VCAN | +0.629 (+3.94) | +1.561 (+4.76) | 3.33× | 2.01× |
| BGN | +0.400 (+4.14) | +1.733 (+3.87) | 1.91× | 2.49× |
| CD44 | +0.711 (+7.86) | +0.707 (+3.04) | 1.69× | 1.64× |
| GPC1 | +0.187 (+3.11) | +1.000 (+4.01) | not in the sequencing panel | not in the sequencing panel |
| ALCAM | +1.091 (+7.01) | +0.753 (+2.21) | 0.92× | 1.53× |

**Figure 1.** Candidate surface antigens placed by cross-cancer selectivity against normal-tissue
window tier. A usable classic antigen would sit in the selective and restricted quadrant, which is
unpopulated for the antigens the filter evaluated. Rendered by `emc_surface_figure.py` to
`emc-surface-prioritization.png`. The figure renders the surrogate stage only; the EMC-tissue axis is
presented in Tables 3 to 5.

## Declarations

**Ethics approval and consent to participate.** Not required and not sought. This study analyses public
gene-expression deposits and public annotation resources, and involves no human participants, no
identifiable data and no patient-level records.

**Consent for publication.** Not applicable.

**Data availability.** All primary data are public. Gene-expression deposits: GSE24369 (GPL6244),
GSE4303 (GPL3290) and GSE28866 (3'-end sequencing, supplementary peak table
`GSE28866_36048_normalized_peaks_cancer_and_normal.txt.gz`). Annotation and reference resources:
UniProt, DepMap, Cellosaurus and the Human Protein Atlas. Derived per-gene values, per-sample values and
verbatim deposit annotations are committed as `emc-expression-panels.json` (`reads.read_8_SURFACE_ANTIGEN`,
`reads.control`, `gene_reads`) and `gse28866-tumour-vs-normal.json` (`per_gene.values`). The surrogate
stage is committed as `emc-surfaceome-scan.json`, `emc-surface-normal-window.json` and
`surfaceome-instrument-limits.json`. The prior-art screen is committed as
`emc-prior-art-2026-08-09.json`.

**Code availability.** `emc_expression_panels.py`, `emc_surfaceome_scan.py`,
`emc_surface_normal_window.py`, `surfaceome_instrument_limits.py`, `emc_line_data_probe.py`,
`emc_gse4303_crosscheck.py` and `emc_surface_figure.py`.

**Use of artificial intelligence.** Analysis code, data processing and manuscript drafting were carried
out with substantial AI assistance under the author's direction. The author designed the study, directed
every analysis, reviewed all outputs and takes responsibility for the content.

**Author contributions.** T.M. conceived the study, directed the analyses, verified the outputs and
wrote the manuscript.

**Funding.** None.

**Competing interests.** None.

**Acknowledgements.** None.

## References

Author lists, journal titles, volumes and pages are taken from the retrieval records in
[`submission-reference-metadata-2026-08-09.json`](../../literature/submission-reference-metadata-2026-08-09.json)
and [`emc-prior-art-2026-08-09.json`](../../literature/emc-prior-art-2026-08-09.json), and where a record
lists more than six authors the first six are given.

1. Remiszewski P, Falkowski S, Szumera-Ciećkiewicz A, Spałek MJ, Rutkowski P, Czarnecka AM. From
   pathogenesis to the patient's bedside: a comprehensive review of extraskeletal myxoid
   chondrosarcoma. *J Cancer Res Clin Oncol* 2025;151(11):283. doi:10.1007/s00432-025-06316-5.
   PMID 41055792. PMC12504171.
2. Lenz J, Klubíčková N, Ptáková N, Hájková V, Grossmann P, Šteiner P, et al. Extraskeletal myxoid
   chondrosarcoma: a study of 17 cases focusing on the diagnostic utility of INSM1 expression and
   presenting rare morphological variants associated with non-EWSR1::NR4A3 fusions. *Hum Pathol*
   2023;134:19-29. doi:10.1016/j.humpath.2022.12.005. PMID 36563884.
3. Timon G, Grassi M, Tominaj C, Turazzi M, Mascherini M, De Cian F, et al. Excellent response and
   persistent local control of metastatic extraskeletal myxoid chondrosarcoma repeatedly treated with
   surgical excision or stereotactic radiotherapy alone: a case report. *Case Rep Oncol*
   2025;18(1):1488-1495. doi:10.1159/000548238. PMID 41323055. PMC12659415.
4. Ogata R, Soda H, Senju H, Fujioka M, Shimada M, Yamashita K, et al. Immunosuppressive tumor
   microenvironment in extraskeletal myxoid chondrosarcoma: a case of pleural metastases. *Thorac
   Cancer* 2022;13(19):2812-2816. doi:10.1111/1759-7714.14613. PMID 35974707. PMC9527174.
5. Martínez-Trufero J, Cruz Jurado J, Hernández-León CN, Correa R, Asencio JM, Bernabeu D, et al.
   Uncommon and peculiar soft tissue sarcomas: multidisciplinary review and practical
   recommendations. Spanish Group for Sarcoma Research (GEIS-GROUP). Part II. *Cancer Treat Rev*
   2021;99:102260. doi:10.1016/j.ctrv.2021.102260. PMID 34340159.
6. Uhlén M, Fagerberg L, Hallström BM, Lindskog C, Oksvold P, Mardinoglu A, et al. Proteomics.
   Tissue-based map of the human proteome. *Science* 2015;347(6220):1260419.
   doi:10.1126/science.1260419. PMID 25613900. The Human Protein Atlas.
7. Subramanian S, West RB, Marinelli RJ, Nielsen TO, Rubin BP, Goldblum JR, et al. The gene
   expression profile of extraskeletal myxoid chondrosarcoma. *J Pathol* 2005;206(4):433-444.
   doi:10.1002/path.1792. PMID 15920699. The originating cohort publication for GSE4303.
8. Kim AY, Lim B, Choi J, Kim J. The TFG-TEC oncoprotein induces transcriptional activation of the
   human β-enolase gene via chromatin modification of the promoter region. *Mol Carcinog*
   2016;55(10):1411-1423. doi:10.1002/mc.22384. PMID 26310886. ENO3 as a direct transactivation
   target of an NR4A3 fusion; the reported fusion in that work is TFG::NR4A3 rather than
   EWSR1::NR4A3.
9. Socinski MA, Kaye FJ, Spigel DR, Kudrik FJ, Ponce S, Ellis PM, et al. Phase 1/2 study of the
   CD56-targeting antibody-drug conjugate lorvotuzumab mertansine (IMGN901) in combination with
   carboplatin/etoposide in small-cell lung cancer patients with extensive-stage disease. *Clin Lung
   Cancer* 2017;18(1):68-76.e2. doi:10.1016/j.cllc.2016.09.002. PMID 28341109.
10. Shah MH, Lorigan P, O'Brien ME, Fossella FV, Moore KN, Bhatia S, et al. Phase I study of IMGN901,
    a CD56-targeting antibody-drug conjugate, in patients with CD56-positive solid tumors. *Invest
    New Drugs* 2016;34(3):290-299. doi:10.1007/s10637-016-0336-9. PMID 26961907. PMC4859861.
11. Bangerter JL, Harnisch KJ, Chen Y, Hagedorn C, Planas-Paz L, Pauli C. Establishment,
    characterization and functional testing of two novel ex vivo extraskeletal myxoid chondrosarcoma
    (EMC) cell models. *Hum Cell* 2023;36(1):446-455. doi:10.1007/s13577-022-00818-x. PMID 36316541.
    PMC9813045. The USZ-EMC patient-derived models.
12. Iwata S, Noguchi R, Osaki J, Adachi Y, Shiota Y, Osaki S, et al. Establishment and
    characterization of NCC-EMC1-C1: a novel patient-derived cell line of extraskeletal myxoid
    chondrosarcoma. *Hum Cell* 2025;38(4):122. doi:10.1007/s13577-025-01250-7. PMID 40580361.
13. Bausch-Fluck D, Goldmann U, Müller S, van Oostrum M, Müller M, Schubert OT, et al. The in silico
    human surfaceome. *Proc Natl Acad Sci U S A* 2018;115(46):E10988-E10997.
    doi:10.1073/pnas.1808790115. PMID 30373828. PMC6243280.
14. Wu ZY, He YQ, Wang TM, Yang DW, Li DH, Deng CM, et al. Glycogenes in oncofetal chondroitin
    sulfate biosynthesis are differently expressed and correlated with immune response in placenta and
    colorectal cancer. *Front Cell Dev Biol* 2021;9:763875. doi:10.3389/fcell.2021.763875.
    PMID 34966741. PMC8710744.
15. Cellosaurus record CVCL_1238, curated caution on the fusion status of the DepMap model annotated
    extraskeletal myxoid chondrosarcoma, citing PMID 34413129. The primary source is Gartrell J,
    Mellado-Largarde M, Clay MR, Bahrami A, Sahr NA, Sykes A, et al. SLFN11 is widely expressed in
    pediatric sarcoma and induces variable sensitization to replicative stress caused by DNA-damaging
    agents. *Mol Cancer Ther* 2021;20(11):2151-2165. doi:10.1158/1535-7163.mct-21-0089.
    PMID 34413129. PMC8571037.
16. Sjögren H, Meis-Kindblom J, Kindblom LG, Aman P, Stenman G. Fusion of the EWS-related gene TAF2N
    to TEC in extraskeletal myxoid chondrosarcoma. *Cancer Res* 1999;59(20):5064-5067. PMID 10537274.
    The primary report of the variant fusion in which the 5' partner is TAF15 (TAF2N) rather than
    EWSR1. *Entry resolved 2026-08-09; see Appendix A.*
17. Panagopoulos I, Mertens F, Isaksson M, Domanski HA, Brosjö O, Heim S, et al. Molecular genetic
    characterization of the EWS/CHN and RBP56/CHN fusion genes in extraskeletal myxoid
    chondrosarcoma. *Genes Chromosomes Cancer* 2002;35(4):340-352. doi:10.1002/gcc.10127.
    PMID 12378528.
18. Strosberg J, El-Haddad G, Wolin E, Hendifar A, Yao J, Chasen B, et al. Phase 3 trial of
    177Lu-Dotatate for midgut neuroendocrine tumors. *N Engl J Med* 2017;376(2):125-135.
    doi:10.1056/nejmoa1607427. PMID 28076709. PMC5895095. The NETTER-1 trial.

---

## Appendix A. Correction and supersession register

### Appendix A5 — Reference-list repairs (2026-08-09)

| What it said | What it says now | Why |
|---|---|---|
| Reference 16 read *"Sjögren H, et al. EWSR1/NR4A3 fusion in extraskeletal myxoid chondrosarcoma"*, with no identifier | Sjögren H, Meis-Kindblom J, Kindblom LG, Aman P, Stenman G. Fusion of the EWS-related gene TAF2N to TEC in extraskeletal myxoid chondrosarcoma. *Cancer Res* 1999;59(20):5064-5067. PMID 10537274 | The original entry described no real paper. A retrieval returned three Sjögren papers on this disease and none is an EWSR1-fusion report: PMID 10537274 is the TAF15 fusion, PMID 11156374 the TCF12 fusion, PMID 12598313 a cytogenetic and microarray study. Tracing the entry through the pre-rewrite draft showed it entered as the placeholder *"[Sjögren; Panagopoulos; whole-genome characterisation citation to verify]"* attached to the sentence defining the fusion and its variant 5' partners. The entry is now the primary report of the variant that sentence names, and the two rejected candidates are recorded here so the identification can be checked |
| References 13 to 18 appeared in the list with no citation marker anywhere in the text | Each is cited at the sentence it supports | The cut from 11,740 to 4,553 words removed the citing sentences and left the entries. Each claim was located in the current text before a marker was restored, and no marker was placed on a sentence the source does not support |
| Reference 13, the machine-learning surfaceome resource, had no place in the text at all | Cited in Methods, with an explicit statement that it was *not* used and why | The surfaceome here is built from UniProt annotation. Citing that resource at the construction step would have implied it was the source. Stating that an established alternative exists and was not used is the accurate form, and it answers a question a reviewer would otherwise ask |
| Reference 14 sat nearest a sentence calling a cited work *"founding"* | Cited instead at the statement that a glycan is a pathway product rather than a gene product | That paper is a 2021 glycogene expression study, not the founding description of the antigen. Attaching it to *"founding"* would have misattributed it |


⛔ **This appendix is the correction register required by CLAUDE.md rule 1.2. It is not part of the
5,000-word main body; it is deposited as a supplementary note and retained in the repository so that
every superseded value and every withdrawn claim stays quotable and attributable. The live text above
carries only current values.**

### Appendix A1 — Amendment 1 (2026-08-05): the cell line this manuscript called "the one real EMC line" is recorded as NOT carrying the fusion

**What the 2026-07-03 version claimed, verbatim and still quotable:** the abstract said the DepMap
translocation-sarcoma class *"— contrary to the common assumption — **also contains one genuine EMC line
(H-EMC-SS / ACH-001519)** whose surface transcriptome we report directly (n = 1, descriptive)"*; §3.1 was
headed *"The one EMC line in public data — H-EMC-SS"* and called its top surface antigens *"the most
EMC-specific in-silico signal available"*; §2.2 recorded that line's *"authentication and EWSR1::NR4A3
status flagged [to verify]"*; and the 2026-07-03 banner read *"surfaces one real EMC cell line's own
profile"*.

**What resolved it.** Three independent readouts, recorded in
[`../modalities/emc-atr-vulnerability.json`](../../modalities/emc-atr-vulnerability.json) →
`part_a_hemcss_identity` (verdict `NOT_FUSION_POSITIVE_PER_CURATED_RECORD`) and narrated in
[`emc-atr-vulnerability-assessment.md` §2](../dependency/emc-atr-vulnerability-assessment.md):

1. **Cellosaurus `CVCL_1238` carries an explicit curated caution, verbatim:** *"Caution: Does not harbor
   a gene fusion involving EWSR1 which is a hallmark of extraskeletal myxoid chondrosarcoma
   (PubMed=34413129)."*
2. **DepMap's filtered fusion caller** (`OmicsFusionFiltered.csv`, 24Q4, 1,670 models) has the model
   **present** with **2** calls, `AL158209.1--NEBL` and `VIM--RPS25`, and **neither names NR4A3, EWSR1,
   TAF15 or FUS**. ⭑ The model being *in* the file is what makes this a reading of absence rather than an
   absent reading.
3. **NR4A3 transcript, independent of the caller:** **0.941 log2(TPM+1)**, 83rd percentile of 1,673
   lines, against a panel **median of 0.214**. A fusion transcript carries the NR4A3 body under EWSR1's
   promoter and would be expected to read far higher. **Weak corroboration only.**

⚠ **What Amendment 1 does NOT claim.** Cell-line identity is settled by STR authentication against the
donor and RT-PCR for the fusion. Neither is in public data at the resolution needed and neither is
something this programme can perform. So this establishes that **the public record does not support** the
label the manuscript applied; it does **not** establish what the line is instead, that the original
characterisation was wrong, or that the line is not EMC. A line can be misidentified, can drift in
culture, or can be a genuine fusion-negative tumour of the same histology, which is a real category since
a minority of EMC carries no identified FET partner. Cellosaurus also records an STR profile of 16 markers — 15 STR
loci plus amelogenin — cross-referenced to DepMap `ACH-001519`, COSMIC-CLP `907290` and RIKEN
`RCB0508`: the line is a real,
profiled entity, and the open question is what it is rather than whether it exists.

**What was withdrawn.**

| element | status |
|---|---|
| Title's *"one cell line"*, the abstract's *"one genuine EMC line"*, the banner's *"surfaces one real EMC cell line's own profile"*, §3.1's *"the most EMC-specific in-silico signal available"*, §7's *"DepMap additionally holds H-EMC-SS"* | ⛔ **WITHDRAWN.** These read the line as EMC-and-fusion-positive, which the public record does not support |
| §3.1 **Table 1**, the line's own top surface transcripts | ⛔ **WITHDRAWN AS AN EMC READING; RETAINED AS DATA** and re-labelled a single sarcoma line of disputed identity. Its values, log2(TPM+1), were: APP 9.9, CD63 9.5, FGFR1 9.3, SLC38A2 9.0, GPRC5B 8.9, PERP 8.8, SLC3A2 8.6, CD81 8.5, CD164 8.5, DNER 8.5, BSG/CD147 8.2, RTN4 8.2, MMP14 8.1, ITGB1 7.9, PMP22 7.8, ALCAM 7.7. The list is dominated by ubiquitous membrane proteins, which is a statement about single-line expression as an instrument and holds for any line |
| §3.1's reading that DNER / RTN4 / PMP22 is *"loosely consistent with EMC's neuroendocrine/neural differentiation"* | ⛔ **WITHDRAWN.** It was a corroboration of the SSTR2/GD2 hypothesis taken from this line. The manuscript already graded it *"a suggestion, not evidence"*; it is now not even that. FGFR1's appearance there is doubly uninformative, since FGFR1 is concordantly down on both arrays in EMC tissue |
| §3.2 **selectivity** (incl. *B7-H3 is not selective, BH q = 1.0*) | ✅ **SURVIVES, RE-LABELLED.** The line is **1 of 45** class members carrying expression data. Recomputing every actionable antigen's `enrichment_vs_rest` with the line dropped moves it by **≤ 0.13 log2TPM** (largest: GPC3 0.93→0.81; CD276 0.14→0.15; CDH11 3.18→3.29), with **no sign flips**. ⚠ Honest limit: the rank-based Mann–Whitney *p* cannot be recomputed from the committed artifact, which stores summary statistics rather than per-line values, so the *q*-values are **not** re-derived — the effect-size bound is what is offered |
| §3.3 **normal-tissue window** | ✅ **UNAFFECTED.** Built entirely from Human Protein Atlas normal tissue; no cell line enters it |

⭑ **The general lesson.** The `[to verify]` flag on this line was written honestly and carried faithfully
in four places for a month. **Carrying a flag is not resolving one.** What resolved it was one free API
call that could have been made on day one. Every repository file that leaned on the line now carries its
own dated amendment, and the line's status is registered as an object (`OBJ-LINE-HEMCSS`) in
[`emc-systems-map.json`](../emc-systems-map.json) so that a future claim reading EMC biology off it fails a
checker rather than a reader.

### Appendix A2 — Amendment 2 (2026-08-07): the surrogate-basis framing is superseded

**Superseded claim, retained verbatim.** The endpoint register and §6 both stated that every negative this
manuscript reported was *"bounded by that surrogate basis rather than by an EMC tissue measurement"*, from
*"one cell line and a translocation-sarcoma comparison set"*. That limit no longer holds, because the
measurement now exists: **GSE24369 on GPL6244**, **GSE4303 on GPL3290** and **GSE28866 on 3SEQ** are read,
the third carrying **27 normal-organ libraries** and so supplying the on-target/off-tumour exposure axis
this analysis had never been able to ask for.

**Also superseded, retained verbatim.** The 2026-08-05 banner read that the analysis *"reports what an
honest in-silico surface-antigen analysis for EMC can and cannot establish from public data"* and that its
finding was that **"a rigorous selectivity test plus a hard normal-tissue-window filter leaves essentially
no classic protein surface antigen that is both tumour-selective and normal-tissue-restricted."** That
sentence is not withdrawn; it is now a statement about the **surrogate**, and the EMC-tissue results
above report what the disease's own tissue says instead.

**Superseded abstract sentence, retained verbatim.** *"The value of the work is to de-risk over-optimistic
assumptions (especially B7-H3), to expose antigen-specific liabilities, and to nominate the neuroendocrine
SSTR2/GD2 route"*, and, before Amendment 1, *"to surface the one available EMC line's profile"*.

**Superseded conclusion sentence, retained verbatim.** *"rigorous selectivity testing plus a normal-tissue
window shows the field-default B7-H3 is not selective and that the selective candidates carry specific
window liabilities, leaving a favourable-normal-tissue-window GD2 (EMC expression unknown) and a
grounded-but-unmeasured-in-EMC SSTR2/DOTATATE neuroendocrine hypothesis as the questions most worth
testing"*.

**What Amendment 2 changed, element by element.**

| element | status |
|---|---|
| The framing that the negatives are bounded by the surrogate rather than by an EMC measurement | ⛔ **SUPERSEDED.** Three EMC tumour cohorts are read; the surrogate is one instrument among several |
| The **SSTR2 / GD2 neuroendocrine hypothesis**, nominated as one of the two questions "most worth testing" | ⚠ **DOWNGRADED, not closed.** SSTR2's first EMC-tissue readings show no elevation; the somatostatin-receptor family panel could not be scored on GPL3290; the GD2 proxy B4GALNT1 is flat and its synthase panel is lower on both platforms. ⛔ None of this measures receptor protein density, so the hypothesis is weakened and **not** refuted |
| The headline that **B7-H3/CD276 is not selective** | ✅ **STRENGTHENED and re-based.** CD276 also reads lower in EMC tumour tissue than in comparator sarcomas on the one platform that can read it. ⚠ It is **not readable at all** on GPL3290, which is an instrument statement and never a low reading |
| The list of **eight significantly-selective antigens** | ⚠ **NOT REPRODUCED.** Zero of the eight are concordantly higher on both arrays; two (FGFR1, PTK7) are concordantly lower |
| The conclusion that the **selective-and-restricted intersection is empty** | ⚠ **RE-SCOPED.** It was computed over a set that did not contain CSPG4, a measured coverage gap rather than a rejection. The statement stands for the antigens the filter saw |
| The finding that **GSE4303 is unusable** | ⛔ **SUPERSEDED BY AN INSTRUMENT CHANGE, not by new data.** Superseded text, retained verbatim: *"The only usable, dedicated public EMC tumour transcriptome we could identify, GSE4303, is a seven-platform two-colour cDNA-clone microarray (three EMC samples per platform) whose values are reference-pool log-ratios and whose probes lack gene symbols; zero shortlist genes resolved. It cannot rank surface antigens."* One of its seven platforms, GPL3290, is now readable through an accession bridge; the earlier "zero shortlist genes resolved" was a property of the symbol lookup rather than of the deposit |
| The **collaboration request** | ✅ **SURVIVES, with a changed ask.** Superseded sentence, retained verbatim: *"Those models are now the ONLY route to real EMC data for this analysis"*, true on 2026-08-05 and not true once GPL3290 became readable. The decisive missing datum is now **protein and surface localisation**, plus a cohort large enough to carry a distribution |

⭑ **The general lesson.** A search that cannot see its own subject will still return a ranked list, and the
list will look like a result. Nothing in the original ranking was miscomputed and every stage-1 number is
reproducible and unretracted. What was wrong was the implicit inference from *"selective in the surrogate"*
to *"worth measuring in EMC"*. The four candidate reasons the two instruments disagree are all live, so this
amendment does not replace one instrument's authority with another's.

### Appendix A3 — Restructuring record (2026-08-09)

The manuscript was rewritten from an 11,740-word internal working document carrying two stacked amendment
blocks into a single current narrative in British Journal of Cancer Article format. Nothing measured was
withdrawn in the restructure. Material moved out of the main text is in
[`emc-surface-target-landscape-si.md`](./emc-surface-target-landscape-si.md): the full normal-tissue
classification, the instrument-limit derivations, the panel-level scores, the accession-bridge detail, the
control tables and the extended limitations. The repository-register house style (glyph warnings,
mid-sentence emphasis, running commentary on the paper's own candour) was removed from the main text as
out of register for a journal, and survives here, where the bookkeeping belongs.

⚠ **Superseded framing, retained:** the previous version presented itself as *"an instrument and its
audit"* with the demotion announced in a banner before the abstract. The demotion is unchanged; the banner
is not, because a submission text states its result in the abstract rather than warning the reader in
advance of it.

### Appendix A4 — Reference-list completion record (2026-08-09)

Eleven of the eighteen references carried an identifier and no bibliographic detail. They were completed
from
[`submission-reference-metadata-2026-08-09.json`](../../literature/submission-reference-metadata-2026-08-09.json)
and [`emc-prior-art-2026-08-09.json`](../../literature/emc-prior-art-2026-08-09.json). Two entries changed
in substance rather than merely gaining fields, and both are registered here:

⛔ **Reference 14 was attributed to the wrong first author and carried a paraphrase in place of its
title.** *Superseded, retained:* *"Wu M, et al. Chondroitin sulfate sulfation machinery. Front Cell Dev
Biol 2021."* The record for PMID 34966741 names **Wu ZY** as first author and titles the work *"Glycogenes
in oncofetal chondroitin sulfate biosynthesis are differently expressed and correlated with immune
response in placenta and colorectal cancer."* No committed source carries "Wu M" or the paraphrased
title, so both entered the prose from something the repository cannot show. This is the 2026-08-07
failure mode in its milder form: a real identifier wearing a description nobody fetched.

⚠ **Reference 11 was dated "2022/2023".** The record for PMID 36316541 gives 2023, volume 36, issue 1,
pages 446-455. The hedge is replaced by the retrieved year.

Five entries (6, 13, 16, 17, 18) are in neither retrieval and still carry their identifier alone; two
(4, 5) resolved with an author list, year, DOI and identifiers but no journal or pagination. Nothing was
written for any of the seven, because a field that is not in a retrieval is left missing.

---
*Provenance: consolidates the stage-1 surfaceome scan (BH-corrected selectivity plus the ACH-001519
profile, whose EMC label is withdrawn by Amendment 1), the normal-tissue prior (controls behaved as
specified), the EMC-line data probe, the GSE4303 cross-check (superseded by the accession bridge), the
stage-2 EMC tumour-tissue read across three cohorts and three platform families, the measured limits of
the stage-1 instrument, the 2026-08-09 prior-art screen, two red-team passes
([`emc-surface-target-redteam.md`](./emc-surface-target-redteam.md)) and the 2026-08-05 line-identity
readout. All committed CPU/CI outputs; no GPU compute and no wet-lab work. No antigen is asserted as an
EMC-validated target, and no claim of safety, selectivity, efficacy or clinical readiness is made
anywhere.*
