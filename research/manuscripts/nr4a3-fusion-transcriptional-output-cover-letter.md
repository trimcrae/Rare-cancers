---
id: DOC-NR4A3-FUSION-TRANSCRIPTIONAL-OUTPUT-COVER-LETTER
title: "Cover letter — EWSR1::NR4A3 transcriptional-output manuscript submission"
level: L3
kind: memo
status: live
canonical_for: []
purpose: >
  Hold the ready-to-send cover letter accompanying the transcriptional-output manuscript to its
  primary target journal (Genes, Chromosomes & Cancer), with the fit statement, integrity
  declarations and preprint note a journal expects at submission.
scope: >
  The cover letter only. It is a submission document, not a scientific record; every result it
  refers to lives in the manuscript and its artifacts.
audience: [maintainers, external reviewers, collaborators]
related: [DOC-NR4A3-FUSION-TRANSCRIPTIONAL-OUTPUT]
date: 2026-08-10
last_verified: 2026-08-10
---

# Cover letter

*Ready to send. Before submitting: fill the bracketed fields, confirm the editor addressee on the
journal's current masthead, and elect the subscription (non-open-access) route at the fee step so no
article-processing charge is incurred.*

---

**To:** The Editor-in-Chief, *Genes, Chromosomes & Cancer*

**From:** Tristan D. McRae, Independent Researcher — trimcrae@gmail.com — [ORCID]

**Date:** [DATE]

**Re:** Submission of an Original Research Article — *"The published direct-target catalogue of the EWSR1::NR4A3 fusion is three genes wide, and none is separable from disease association in the available EMC expression record."*

Dear Editor,

I am pleased to submit the manuscript above for consideration as an Original Research Article in
*Genes, Chromosomes & Cancer*. Extraskeletal myxoid chondrosarcoma (EMC) is a rare translocation
sarcoma driven, in most cases, by the *EWSR1::NR4A3* fusion, and its central molecular hypothesis is
that the chimera drives an aberrant transcriptional programme. The manuscript asks what has actually
been shown about that programme, and what the available expression record leaves of it. It sits
squarely within the journal's scope of genetic and genomic analysis of neoplasia.

The first result is a catalogue. Every published claim that an NR4A3 chimera or native NR4A3
activates a named gene was assembled with the factor actually tested, the assay, the cell system and
the species recorded per claim. Across 2,276 retrieved full-text documents, the set of genes for
which any NR4A3 chimera has been shown to bind DNA is three: *SEMA3C*, *PPARG* and *ENO3*. Read back
in the three public EMC expression cohorts, none of the three is separable from disease association.
*SEMA3C* survives nothing and reverses sign depending on which sarcomas sit in the comparator arm;
*PPARG*'s strongest reading is circular, scored on the cohort from which high *PPARG* in EMC was
first published; *ENO3* survives every test, and I state plainly that it was the pre-designated
positive control and is therefore not an independent finding of this work. Two published measurements
in the primary literature also show the native-to-fusion transfer assumption failing in both
directions, which matters to anyone reasoning from the NR4A3 literature to EMC.

The second result is a mapped absence. No experiment has measured where an NR4A3 fusion binds, or
what chromatin does, in EMC material. That negative is reported as what it is, a search across GEO,
SRA, BioProject, BioSample, ArrayExpress, ENA and ChIP-Atlas with every query string deposited, and
it is stated comparatively: the field performs this experiment routinely for the sibling fusions
(EWSR1::WT1, EWSR1::ATF1, EWSR1::FLI1, FUS::DDIT3 and, twice, HEY1::NCOA2) and has never performed it
on EMC. The one genome-wide chromatin readout that carries NR4A3 fusions at all reads accessibility
in HEK293T rather than occupancy in EMC chromatin, and the manuscript says so rather than counting
it. The paper therefore names the single experiment that would settle the question rather than
gesturing at one, which is the part addressed to anyone with a laboratory.

On method, gene-set reads on a series of this shape are uninterpretable without calibration: at 10
versus 6, unrelated gene sets all come back higher in the index arm. I calibrate every set score
against random gene sets of the same size drawn from the same platform. That is the competitive
gene-set null and it is not new; the manuscript positions it against Goeman and Bühlmann, CAMERA,
ROAST, restandardization and single-sample scoring, measures that this implementation is an
independence null, and reports the correlation-inflated threshold beside the uninflated one for every
set. The one modest element I would keep is a reporting convention rather than a method: an effect
that does not clear its null is reported as a fraction of the threshold it had to reach, which turns
an uninterpretable flat result into a bounded one.

The manuscript is entirely computational and re-analyses only public, de-identified gene-expression
deposits; no new human or animal data were generated, and no ethics approval was required. All code and
derived data are openly available and the central results reproduce offline from committed code and the
public accessions alone; the repository will be archived to Zenodo with a citable DOI at submission and the DOI added to the Data and code availability section.
The manuscript reports no efficacy, selectivity, safety or clinical-readiness claim for any agent or
target, and makes none by implication.

The work is original, has not been published, and is not under consideration elsewhere. I intend to
deposit the manuscript as a preprint on bioRxiv, consistent with the journal's preprint policy, and
will link the preprint to the published version. The use of an AI research assistant in the analysis
and drafting is disclosed in the manuscript; no AI tool is an author, and I take full responsibility
for the content. I am the sole author; I have no competing interests and received no funding.

Should it help the editors, appropriate reviewer expertise would include sarcoma molecular pathology,
fusion-oncogene transcriptional biology, and cancer-genomics methodology (gene-set
calibration in small cohorts).

Thank you for considering this manuscript.

Yours sincerely,

Tristan D. McRae
Independent Researcher
trimcrae@gmail.com
