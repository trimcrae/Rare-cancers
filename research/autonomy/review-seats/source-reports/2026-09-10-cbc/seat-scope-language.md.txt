# ASO blind scope-and-language review

Reviewed commit: `1f717f120724ad0d0442f0cf24d565871b52afb6`
Document: `research/manuscripts/aso/cbc-20260910/manuscript.md`
SHA-256: `9154a93be06ad7e34990f26e202b0c70e69c1d9b9b14b539a8da850c752e9d04`

Configuration: gpt-6-astra; reasoning effort medium, supplied task configuration rather than runtime introspection.

Verdict: **pass_with_optional_language_edits**. Central claim verdict: **supported**.

In a modeled panel of 190 NR4A3 junction gapmer designs, an adopted full-gap pairing criterion identifies substantial potential parent-transcript liabilities and threshold-sensitive prioritization, without establishing disease-specific excess, biological activity, or a therapeutic window.

The central claim is supported as a bounded computational interpretation of the presented results. Main text, highlights, graphical abstract, figure reporting-status labels, cover letter and supplementary revision note preserve the main distinctions. No demonstrated current blocker or P1 was found in this finite scope-and-language review. This verdict does not independently certify the underlying numerical computations.

## Blockers and P1 findings

None demonstrated.

## Boundary checks

- **Modeled versus confirmed junctions:** Main sections 3.2 and 4.1 distinguish mostly unreported panel junctions, five published exon-resolved junctions, engineered constructs and unresolved patient-derived model seams. Figure 1 labels the EWSR1 seam as reported and the FUS and TAF15 seams as unreported. Highlights and graphical abstract expressly say modelled.
- **Sequence pairing versus biological activity:** Abstract, sections 2, 3.1, 3.3 and 4.3, declarations, cover and graphical abstract state the adopted cutoff and absence of cleavage/potency/safety/therapeutic-window evidence. Table 1 and Supplementary File 2 limit temperature values to an unmodified DNA:RNA model.
- **Descriptive panel versus population inference:** Section 3.2 says both panel and exon-terminus controls mostly contain unreported junctions and disease-specific excess remains unresolved. Section 3.1 explicitly calls 68.4% modeled coverage and says 39.9%-82.8% is not a confidence interval, identifying transferred cohort distribution and fixed inputs.
- **Completed computation versus proposed experiments:** Section 4.2 is explicitly proposed experimental evaluation; replicate variance is assumed and unmeasured. Main abstract, declarations, cover and SI all say no laboratory work was performed.
- **Source evidence versus extrapolation:** Introduction identifies review-derived response interpretation, adopted incomplete-pairing premises and only the in-silico half of framework step one. Sections 3.1 and 4.1 label the hepatotoxicity premise and model-correspondence inference as untested. Section 4.2 calls selectivity ratio and threshold adopted conventions.

## Optional edits

- **O1 — research/manuscripts/aso/cbc-20260910/manuscript.md:23, Abstract sentence 2**: across 38 in-frame NR4A3 fusion junctions in extraskeletal myxoid chondrosarcoma. Insert modelled before in-frame to make the standalone abstract as explicit as the highlights and graphical abstract. The full article states the distinction repeatedly and the abstract already frames the work computationally; this is a clarity improvement rather than demonstrated material misrepresentation.
- **O2 — research/manuscripts/aso/cbc-20260910/manuscript.md:202, Table 2 caption (outgoing PDF p.19)**: each screened as its reagent was; that screening step makes a scramble a control. Specify screened against mature parents and describe these as candidate negative controls; retain the section 3.3 statement that screening does not establish inertness. The same caption specifies the mature-parent screen and section 3.3 states the limitation, but its opening and closing shorthand can imply broader screening or demonstrated control behavior.
- **O3 — research/release-candidates/PUB-ASO/2026-09-10-cbc/figure-1.png, bottom explanatory paragraph beginning The reagent is**: the sense strand, which is a different molecule with no antisense activity. Replace no antisense activity with does not complement the intended fusion target in the intended antisense orientation. This is an overly absolute activity statement for an untested molecule. Its purpose and context concern wrong-strand ordering, not a claimed activity experiment; the intended warning is sound.
- **O4 — research/release-candidates/PUB-ASO/2026-09-10-cbc/fusion-junction-aso-sequences.csv:43-44 and :93-98**: a DIFFERENT MOLECULE about which nothing in the paper is true; MEASURED AND UNDER THE CRITERION; shortest cut measured. Use a different molecule whose activity is not assessed here and computationally evaluated rather than measured. The CSV itself says the thermodynamic calculations use unmodified chemistry and no sequence was tested. Its historical emphatic shorthand is less accurate than the current main text, but surrounding disclaimers resolve the central activity boundary.

## Blind context

One finite independent review. No other reviewer reports, hardening records, owner QA verdicts or cross-review discussion were read or used.

These annotations were encountered inside allowed scientific/package files and were treated as provenance statements only, not independent evidence that prior review findings were resolved.

- Main section 4.1 and Data availability discuss withdrawal after exon-indexing errors.
- Main AI declaration describes prior AI assistance and checks.
- Supplementary File 2 and original-v3-revision-note.pdf describe historical corrections and archive limitations.
- Sequence CSV comments retain historical preprint date, withdrawal and manuscript-section references.
- Cover letter and version-change-summary.txt describe preservation from Qeios version 3.

## Actual checks

- Read complete pinned manuscript Markdown including abstract, references, tables and figure legend; recomputed its SHA-256 and matched the supplied digest.
- Read pinned highlights, graphical-abstract caption, version-change summary, all cover-letter/figure-legends/Supplementary File 2 DOCX paragraphs, original revision-note PDF text and graphical-abstract PDF text.
- Read all sequence CSV explanatory comments and selected named-reagent/control rows. Initial full CSV output was truncated; no claim is made to have manually reviewed all 782 rows.
- Verified every substantive DOCX paragraph of the main manuscript appears in the Markdown after normalization and in the 20-page PDF text after removing standalone page numbers. Cover-letter, highlights, figure-legends and Supplementary File 2 PDF text likewise contained all substantive DOCX paragraphs.
- Inspected Figure 1 PNG visually after verifying local bytes equal the pinned Git blob.
- Compared interpretation boundaries across the reviewed outgoing scientific surfaces; performed no new numerical screen.

## Limitations

- Scope-and-language review only; no broad literature search, independent bibliographic audit, assay validation, numerical recomputation, full CI or journal-layout certification.
- No underlying primary records were opened because no specific source-wording conflict requiring adjudication emerged in this bounded pass.
- No new renders were generated. PDF checks were text extraction; Figure 1 used the existing PNG. Graphical-abstract layout was not visually certified.
- Supplied formal MD/DOCX/PDF digest and 29-file fullfileset digest are task identity context; this seat independently recomputed only the declared main Markdown SHA-256 and the inspected figure byte equality, not the aggregate package digests.
