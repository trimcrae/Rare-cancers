---
id: DOC-EMC-SURFACE-TARGET-LANDSCAPE-COVER-LETTER
title: "Cover letter — transferability of a lineage-surrogate surface-antigen ranking"
level: L3
kind: memo
status: live
canonical_for: []
purpose: >
  Hold the ready-to-send cover letter accompanying emc-surface-target-landscape.md to Genes,
  Chromosomes and Cancer, with the fit statement, the scope disclosure, the preprint note and the
  integrity declarations a journal expects at submission.
scope: >
  The cover letter only. It is a submission document, not a scientific record; every result it
  refers to lives in the manuscript, its supplementary file and their artifacts.
audience: [maintainers, external reviewers, collaborators]
related: [DOC-EMC-SURFACE-TARGET-LANDSCAPE]
date: 2026-08-10
last_verified: 2026-08-10
---

# Cover letter

*Ready to send. Before submitting: fill the bracketed date, confirm the editor addressee on the
journal's current masthead, choose the standard subscription publication route so no article
processing charge is incurred, and submit the figure in greyscale so no colour charge applies.*

*Venue changed 2026-08-10 from the British Journal of Cancer, together with the manuscript's
reframing. The reasoning and the superseded venue framing are recorded in the manuscript's editorial
comment block; the zero-cost publication route is verified at primary source for both journals in
`research/literature/venue-fee-routes-2026-08-10.json`.*

---

**To:** The Editor-in-Chief, *Genes, Chromosomes and Cancer*

**From:** Tristan D. McRae, independent researcher, unaffiliated — trimcrae@gmail.com

**Date:** [DATE]

**Re:** Submission of a research article — *"How far a lineage-surrogate surface-antigen ranking transfers to the tumour it was built for: extraskeletal myxoid chondrosarcoma as a worked case"*

Dear Editor,

I submit the manuscript above for consideration in *Genes, Chromosomes and Cancer*.

Surface-antigen target lists for rare tumours are routinely built without the tumour. When a disease
has no public expression data, candidate antigens are ranked in a lineage surrogate — usually cell
lines from related entities — and that ranking becomes the shortlist for reagent development. The
step that would grade the method is almost never taken: measuring the same antigens in the disease's
own tissue. This manuscript takes that step for one disease and reports how large the disagreement
is.

The worked case is extraskeletal myxoid chondrosarcoma, a sarcoma driven by the nuclear
*EWSR1::NR4A3* fusion. A 2,826-gene surfaceome was ranked across a translocation-sarcoma cell-line
class and filtered by a normal-tissue prior, and the resulting priorities were then tested in three
EMC tumour-tissue cohorts under a stated alpha with Benjamini-Hochberg correction applied within each
platform. Eighteen of 47 actionable antigens were selective in the surrogate; 13 had a tumour-tissue
reading, none was concordantly elevated on both arrays, and every significant movement among them ran
opposite to the direction the surrogate predicted. The ranking's rejections fared no better: the
antigen ranked lowest of all 47 is one of only three genes on the whole board concordantly elevated
in the disease's tissue. The result is therefore a non-transfer in both directions rather than a
target list, and the manuscript states the effect size the design can resolve so that "not elevated"
is not read as "absent".

The fit with the journal is that this is a cross-platform expression analysis of a rare
translocation-driven sarcoma whose readership will recognise why one of its cohorts needed an
expressed-sequence-tag accession bridge before it could be read at all, and why an
EMC-versus-dermatofibrosarcoma contrast is not an EMC-versus-normal one. The generalisable claim is
about a method the field uses routinely for rare entities, not about one disease.

The study is entirely computational. It analyses public gene-expression deposits and public
annotation resources only, involved no wet-laboratory work, no human participants, no identifiable
data and no patient-level records, and required no ethics approval. Nothing in it asserts that any
antigen is a validated target in this disease, that any agent is safe or effective in it, that a
therapeutic window exists, or that any route is ready for clinical use.

Two things belong in an editor's hands before review. First, the principal limitation: every quantity
reported is transcript abundance, while every address discussed is a protein or glycan question, so a
high reading is a reason to stain rather than an antigen call; and the tumour cohorts are small
archival bulk deposits on decade-old platforms, at n = 6, n = 10 and n = 4, with the normal-tissue
exposure axis resting on medians of four libraries against six visceral organ types. Second, the
manuscript carries a version-history register in its supplementary file. It records, among other
corrections, that a cell line this programme had treated as its one real EMC line is documented as
not carrying the fusion; that an earlier internal criterion thresholding |t| at 2 was more permissive
than a 95% interval and every count derived from it has been re-derived; and that an earlier figure
was withdrawn because it plotted a marker at a coordinate no analysis had computed. Every one of
those was found and fixed before submission rather than after, and the register is offered as part of
the material rather than hidden in it.

I intend to deposit the manuscript as a preprint on bioRxiv, consistent with the journal's preprint
policy, and will link the preprint to the published version. I am the sole author, an unaffiliated
independent researcher with no institutional address; no ORCID accompanies this submission because I
hold none. Analysis code, data processing and drafting were carried out with substantial AI
assistance under my direction, which is disclosed in the manuscript; no AI tool is an author, and I
take full responsibility for the content.

The work is original, has not been published, and is not under consideration elsewhere. I have no
competing interests and received no funding.

Should it help the editors, appropriate reviewer expertise would include tumour-antigen and
cell-surface target discovery, sarcoma translational biology, and cross-platform expression analysis
in small archival cohorts.

Thank you for considering this manuscript.

Yours sincerely,

Tristan D. McRae
Independent Researcher
trimcrae@gmail.com
