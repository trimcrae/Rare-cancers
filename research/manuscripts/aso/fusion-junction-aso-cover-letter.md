---
id: DOC-FUSION-JUNCTION-ASO-COVER-LETTER
title: "Cover letter — junction-spanning gapmers against NR4A3 fusions in EMC"
level: L3
kind: memo
status: live
canonical_for: []
purpose: >
  Hold the cover letter accompanying fusion-junction-aso-research-article.md, with the fit
  statement, the scope disclosure, the preprint note and the integrity declarations a journal
  expects at submission. The addressee is a placeholder: the venue is open, and both venues
  previously chosen were eliminated on their page charges — see
  fusion-junction-aso-submission-plan.md §1c.
scope: >
  The cover letter only. It is a submission document, not a scientific record; every result it
  refers to lives in the manuscript, its tables and their artifacts.
audience: [maintainers, external reviewers, collaborators]
related: [DOC-FUSION-JUNCTION-ASO-SUBMISSION, DOC-ASO-SUBMISSION-PLAN]
date: 2026-08-13
last_verified: 2026-08-13
---

# Cover letter

*Ready to send except for three items only the author can supply. Before submitting: fill the
bracketed date; register an ORCID iD and add it to the manuscript title page; mint the archive DOI
and replace both placeholders in the manuscript. Confirm the editor addressee on the journal's
current masthead.*

⛔ *THE VENUE IS OPEN, SO THE ADDRESSEE BELOW IS A PLACEHOLDER. Two venues have been eliminated on
their full fee schedules, not their article processing charges: Nucleic Acid Therapeutics was the
better scientific fit and levies mandatory page charges of $90 per page on its free subscription
route, and Cancer Gene Therapy's guide to authors was subsequently read at HTTP 200 and levies
£145/$238 per typeset page. Confirm the FULL fee schedule of whichever venue is chosen — page, colour,
submission and over-length charges included — from the journal's own guide to authors. See
fusion-junction-aso-submission-plan.md §1c.*
⚠ *Superseded, retained: "Cancer Gene Therapy's … author-guideline and submission pages returned
HTTP 404 on every attempt, so its page, colour and over-length charges are UNREAD." They were read
the same day this letter was drafted, and the answer disqualified the journal — so the letter was
addressed to a venue its own planning document had already ruled out.*

---

**To:** The Editor-in-Chief, *[JOURNAL — venue not yet chosen]*

**From:** Tristan D. McRae, independent researcher, unaffiliated — trimcrae@gmail.com

**Date:** [DATE]

**Re:** Submission of an Article — *"In-silico design and predicted specificity limits of junction-spanning gapmers against NR4A3 fusions in extraskeletal myxoid chondrosarcoma"*

Dear Editor,

I submit the manuscript above for consideration as an Article in *[JOURNAL]*.
Extraskeletal myxoid chondrosarcoma is an ultra-rare sarcoma defined by rearrangement of *NR4A3* to
a variable 5′ partner. Its chimeric mRNA carries a breakpoint seam absent from every normal
transcript, which is the disease's one tumour-exclusive feature at the RNA level, and no
junction-directed oligonucleotide has been reported against any NR4A3 fusion. The manuscript grades
every donor-exon by acceptor-exon pair across all five reported partners, tiles junction-spanning
gapmers over each frame-compatible seam, and screens them by five independent methods over four
compartments: mature transcript, parent pre-mRNA, mature parent transcript and the whole genome.

The fit with the journal is that this is a nucleic-acid therapeutic design study in a
fusion-driven cancer, reported at the point where computation stops being able to answer the
question. Designability is not the constraint: junction-spanning designs exist at every one of the
38 frame-compatible junctions, and specificity does not sort by partner — every
one of the five partners has a junction whose best design carries no hybridisable gap-spanning
near-match, so it is the exon a fusion breaks at rather than the gene it breaks into that predicts a
clean design. What is scarce is a design that survives every screen, and the manuscript reports two
results that make it scarcer rather than one that makes it look easy. Re-screening the nine designs
that pass the default search depth at ten times that depth withdraws six of them, three having
returned no near-match at all before and returning 27, 29 and 84. And a screen the manuscript adds
over mature parent transcript — a compartment none of the others can reach — finds that 87 of
190 designs form a duplex of at least ten base pairs pairing the whole catalytic gap against a
wild-type parent, 61 of them against *NR4A3* itself. Three designs survive everything, two of them
at any parent-duplex threshold, and all three are at junctions no patient is reported to carry, so
the manuscript presents them as mechanism controls and ranks within each junction to name the best
available reagent at the two most frequently reported junctions with a published breakpoint. One 16-mer spans
the seams of three partners at once through a measured ten-base donor identity, which would change
the deployable artefact for an ultra-rare disease from bespoke oligonucleotides to a stock reagent —
except that the only exon-resolved *TAF15* breakpoints published fall at a different exon, so the
manuscript reports that result as a statement about sequence architecture and explicitly not as a
claim that one reagent serves three patient groups.

The honest principal limitation is the one the manuscript makes its conclusion. The limiting step is
discrimination between the fusion and the two parent transcripts that supply the oligonucleotide's
own halves, at the catalytic gap. Both cited literature bounds are measured against a single
substitution in an otherwise fully paired duplex, so neither transfers to a parent that leaves half
the oligonucleotide unpaired, and no retrieved measurement bounds the parent case. The manuscript
therefore names the experiment, its required controls and its decision threshold rather than
claiming the design problem is solved.

Two methodological corrections are disclosed rather than left to the archive, because both changed
reported numbers. A nucleotide alignment search reports both strands, and a transcript
carrying the reverse
complement of the target window cannot be hybridised by an antisense oligonucleotide; such hits were
being counted as cleavage risks. All 38 junction screens are now orientation-filtered, and across
them 44% of apparent gap-spanning risks are on the minus strand, so the filter reorders the
junctions rather than rescaling them. Separately, an earlier draft of this work recommended two
reagents that the deeper re-screen withdrew; the manuscript names them as withdrawn rather than
dropping them silently.

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
