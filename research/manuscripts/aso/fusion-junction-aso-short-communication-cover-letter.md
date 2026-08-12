---
id: DOC-FUSION-JUNCTION-ASO-COVER-LETTER
title: "Cover letter — junction-spanning gapmers against NR4A3 fusions in EMC"
level: L3
kind: memo
status: live
canonical_for: []
purpose: >
  Hold the ready-to-send cover letter accompanying fusion-junction-aso-short-communication.md to
  Cancer Gene Therapy, with the fit statement, the scope disclosure, the preprint note and the
  integrity declarations a journal expects at submission.
scope: >
  The cover letter only. It is a submission document, not a scientific record; every result it
  refers to lives in the manuscript, its tables and their artifacts.
audience: [maintainers, external reviewers, collaborators]
related: [DOC-FUSION-JUNCTION-ASO-SUBMISSION, DOC-ASO-SUBMISSION-PLAN]
date: 2026-08-12
last_verified: 2026-08-12
---

# Cover letter

*Ready to send except for three items only the author can supply. Before submitting: fill the
bracketed date; register an ORCID iD and add it to the manuscript title page; mint the archive DOI
and replace both placeholders in the manuscript. Confirm the editor addressee on the journal's
current masthead.*

⛔ *And confirm the FULL fee schedule first, not only the article processing charge. Nucleic Acid
Therapeutics was the better scientific fit and was rejected as a venue after its guidelines were
read: it offers a free subscription route and still levies mandatory page charges of $90 per page.
Cancer Gene Therapy's open-access page has been read and establishes that open access is the
optional paid upgrade, so the subscription route carries no APC — but its author-guideline and
submission pages returned HTTP 404 on every attempt, so its page, colour and over-length charges
are UNREAD. The $0 constraint is binding, so that page must be loaded in an ordinary browser before
this letter is sent. See fusion-junction-aso-submission-plan.md §1b.*

---

**To:** The Editor-in-Chief, *Cancer Gene Therapy*

**From:** Tristan D. McRae, independent researcher, unaffiliated — trimcrae@gmail.com

**Date:** [DATE]

**Re:** Submission of a Short Communication — *"In-silico design and predicted specificity limits of junction-spanning gapmers against NR4A3 fusions in extraskeletal myxoid chondrosarcoma"*

Dear Editor,

I submit the manuscript above for consideration as a Short Communication in *Cancer Gene Therapy*.
Extraskeletal myxoid chondrosarcoma is an ultra-rare sarcoma defined by rearrangement of *NR4A3* to
a variable 5′ partner. Its chimeric mRNA carries a breakpoint seam absent from every normal
transcript, which is the disease's one tumour-exclusive feature at the RNA level, and no
junction-directed oligonucleotide has been reported against any NR4A3 fusion. The manuscript grades
every donor-exon by acceptor-exon pair across all five reported partners, tiles junction-spanning
gapmers over each frame-compatible seam, and screens them by two independent methods.

The fit with the journal is that this is a nucleic-acid therapeutic design study in a
fusion-driven cancer, reported at the point where computation stops being able to answer the
question. Three findings stand. Junction-spanning, parent-sparing designs exist at every one of the
38 frame-compatible junctions, and four carry no detectable off-target on either screen, so neither
sequence availability nor transcriptome load is what constrains this modality here. One 16-mer spans
the seams of three partners at once through a measured ten-base donor identity, which would change
the deployable artefact for an ultra-rare disease from bespoke oligonucleotides to a stock reagent —
except that the only exon-resolved *TAF15* breakpoints published fall at a different exon, so the
manuscript reports that result as a statement about sequence architecture and explicitly not as a
claim that one reagent serves three patient groups. And the partner offering that breadth is not the
partner offering the best predicted specificity.

The honest principal limitation is the one the manuscript makes its conclusion. The limiting step is
discrimination between the fusion and the two parent transcripts that supply the oligonucleotide's
own halves, at the catalytic gap; the two available literature bounds on single-mismatch RNase-H1
discrimination span one- to five-fold, the pessimistic bound is the one measured at the length used
here, and no further sequence analysis narrows that interval. A measurement does. The manuscript
therefore names the experiment, its required controls and its decision threshold rather than
claiming the design problem is solved.

A methodological correction is disclosed in the Results rather than left to the archive, because it
changed reported numbers. `blastn` searches both strands, and a transcript carrying the reverse
complement of the target window cannot be hybridised by an antisense oligonucleotide; such hits were
being counted as cleavage risks. Across the sixteen screens in which orientation is filtered, 47% of
apparent gap-spanning risks are on the minus strand, and the proportion runs from 4% to 100% between
junctions, so the filter reorders the junctions rather than rescaling them. Eight further screens
are reported as upper bounds and marked as such, four of them because they record the aligned strand
on every hit and were classified before the filter consulted it.

The study is entirely computational. It uses public transcript models and public sequence databases
only, involved no wet-laboratory work, no human participants, no identifiable data and no
patient-level records, and required no ethics approval. No oligonucleotide described has been
synthesised. Nothing in the manuscript asserts efficacy, potency, safety, a therapeutic window,
delivery to a tumour, or clinical readiness for any sequence.

I intend to deposit the manuscript as a preprint on bioRxiv, consistent with the journal's preprint
policy, and will link the preprint to the published version. I am the sole author, an unaffiliated
independent researcher with no institutional address. Analysis code, the screening pipelines and
drafting were carried out with substantial AI assistance under my direction, which is disclosed in
the manuscript; no AI tool is an author, every quantitative statement is produced by code in the
released archive, and I take full responsibility for the content.

The work is original, has not been published, and is not under consideration elsewhere. I received
no funding and have no financial competing interests. I declare one non-financial interest: I am a
survivor of extraskeletal myxoid chondrosarcoma, the disease this work addresses.

Should it help the editors, appropriate reviewer expertise would include antisense oligonucleotide
design and RNase-H1 mechanism, fusion-transcript-directed therapeutics, and sarcoma molecular
pathology.

Thank you for considering this manuscript.

Yours sincerely,

Tristan D. McRae
Independent Researcher
trimcrae@gmail.com
