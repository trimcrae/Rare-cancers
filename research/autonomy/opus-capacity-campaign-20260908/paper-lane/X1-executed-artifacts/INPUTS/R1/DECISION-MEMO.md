# Decision memo — a PROPOSED partial revision of the EMC ATR collaborator package

R1 lane, 2026-09-08. Baseline `cc23cd1dfe175aa0f82a3042fa11bfac0aa1f6f5`.
Nothing shared was written. This lane is `/tmp/claude-0/r1-lane/`.

## 0 · What this is, stated plainly

**This is a PROPOSED reconstruction, not a recovered original.** No file, blob or draft containing
the 2026-08-10 revision was found or is claimed to exist. Every sentence in
`PROPOSED-emc-atr-collaborator-package.md` was written now, in this lane, by applying a committed
input to the committed pre-revision text. Where the changelog records a "current" wording, it was
used as a **specification of what the sentence must say**, never quoted as if it were the revision's
prose. The PROPOSED file therefore does not reproduce the revision and must not be described as it.

## 1 · What the committed side-products actually establish

**`research/modalities/emc-fet-frame-and-composition.json`, `type2_seam`** — quoted:

    "ewsr1_coding_nt_through_exon_7": 793,   "ewsr1_whole_codons": 264,
    "ewsr1_nucleotides_donated_across_the_seam": 1,
    "nr4a3_5utr_nt_retained_total": 176,
    "nr4a3_5utr_nt_from_exon_2": 174,  "nr4a3_5utr_nt_from_exon_3": 2,
    "nucleotides_spanned_by_the_extra_residues": 177,
    "_the_arithmetic": "1 nt donated by EWSR1 + 176 nt of NR4A3 5'UTR = 177 nt = 59 codons",
    "extra_residues": 59, "internal_stop_codon_in_the_extension": false,
    "chimeric_orf_length_aa": 949, "nr4a3_moiety_complete": true,
    "first_extra_residue_is_a_hybrid_codon": {"codon":"AAG","residue":"K","position_in_the_chimeric_protein":265}

**`research/modalities/tests/test_emc_fet_frame_and_composition.py:32`** — it exists; quoted:

    def test_the_extension_spans_a_whole_number_of_codons(art):
        """The defect this module was written for: 176 nt cannot encode 59 residues."""
        ...
        assert span % 3 == 0, "an extension spanning a non-multiple of three is an arithmetic error"

**`frame_rule._the_rule`** — quoted: *"A 5' partner exon joined to NR4A3 exon 2 or exon 3 is in
frame if and only if the donor exon ends one nucleotide into a codon … Both acceptors give the same
register, because NR4A3 exon 2 is 174 nt, a multiple of three."* `phase_1_donor_exons` =
`[1, 4, 7, 9, 10, 12, 13, 15]`, independently reproduced here from the per-exon `donor_end_phase`
values in the same artifact.

**`composition.symmetric_prefix_sweep`** — `lowest_fet_prefix_value: 0.439` (EWSR1, residues 1-560),
TCF12 best 0.400; and its own `_what`: *"The published version of this test swept TCF12 alone and
compared its best value against the FET proteins at one fixed 250-aa window, which is asymmetric and
overstates the separation."*

**`counted_fusion_type_frequencies`** — three counted series with verbatim quotations
(Panagopoulos PMID 12378528, Okamoto PMID 11679947, Sjögren PMID 12598313), plus
`genomic_breakpoint_mapping`: *"In CHN, 12 breakpoints were found in intron 2 and only two in
intron 1."* Its `_why` states the defect directly: *"The rank appears to have been inferred from the
type NUMBER."*

**`recruitment_axis_rows`** — the four reference-1 anchors (with `EWSR1-RGG(1)-FLI1` at
`rg_retained: null`, *"the source does not identify which RGG-rich domain was reintroduced"*), the
four reported breakpoints of measured diseases, and `atf1_comparator_span: [0.0, 0.267]`.

**`taf15_zero_rg_margin`** — the two conventions that differ by one; the artifact uses the RG-free
ceiling (174) minus the retained length (161) = **13**.

**The changelog** carries, for many items, the exact *substance* of the corrected sentence.

**The figure files** `emc-fusion-frame-fig1.png/.pdf` exist (360,656 B and 83,262 B, dated
2026-09-04). **Their panel content was not opened or read in this lane**, so no caption is drafted.

## 2 · Resolved against committed evidence — the mechanical corrections drafted

Each is in `PROPOSED-emc-atr-collaborator-package.diff`. Each is traceable to a committed input.

| # | correction | committed source |
|---|---|---|
| M1 | Abstract: "carries 176 nucleotides … encoding 59 residues" -> 177 nt spanned = 1 EWSR1 + 176 NR4A3 (174 exon 2 + 2 exon 3) | `type2_seam`; test line 32 |
| M2 | Abstract: "the two commonest EMC fusions … bracketing" removed; type 1 commonest, type 2 a minority variant counted once; ATF1 stated as a span | `counted_fusion_type_frequencies`; `recruitment_axis_rows.atf1_comparator_span` |
| M3 | §3.3 rewritten with the full seam arithmetic, the hybrid AAG/K265 codon, no internal stop, ORF 949 aa | `type2_seam` |
| M4 | §3.3 "the protein-level model in general use" -> this programme's own earlier model, with reference 3's 25-residue cryptic-exon extension named as precedent | changelog; reference 3 quotation already in the committed §3.1 |
| M5 | Table 1 `reported rank` -> `counted frequency`, with the actual counts (10/15 and 11/15 type 1; type 2 1/15 and absent from [7]; type 5 2/15; TAF15 3/15 and 4/10) | `counted_fusion_type_frequencies` |
| M6 | Table 4 rebuilt: status column separates "measured in reference 1" from "a reported breakpoint of a disease in which the mechanism was measured"; the EWSR1::ATF1 e7 row and the RGG(1) anchor restored; ATF1 span 0.000-0.267 stated | `recruitment_axis_rows` |
| M7 | §3.4 ¶2: "bracket" and "interpolate between points already measured" removed; "byte-identical" -> "identical in sequence" | `recruitment_axis_rows`; changelog |
| M8 | §3.4: 14 residues of margin -> 13, with the convention stated | `taf15_zero_rg_margin` |
| M9 | Table 5 sweep row -> symmetric sweep, FET lowest 0.439 vs TCF12 best 0.400, margin 0.039, graded "separates" not "decisive"; fixed-window row keeps its grade | `composition.symmetric_prefix_sweep` |
| M10 | §3.5 closing claim restated against the lowest FET prefix value, with the overstatement disclosed | same |
| M11-12 | P1 "byte-identical" -> "identical in sequence"; P3 margin 14 -> 13 | changelog; `taf15_zero_rg_margin` |
| M13 | Register sweep: "the source" -> "reference 1"/"Gracilla and colleagues" (7 occurrences); | changelog |
| M14 | §3.2 gains the frame rule as one rule over all donor/acceptor pairs, with the complete phase-1 donor set 1, 4, 7, 9, 10, 12, 13, 15 | `frame_rule` |
| M15 | References 9 and 10 added, carrying **only** the fields the artifact holds (authors, title, PMID, counts) | `counted_fusion_type_frequencies.series` |

**The arithmetic question was decided on the evidence, not assumed.** 176 is not a multiple of
three; 177 is, and 177/3 = 59. The artifact and the test agree. **The committed manuscript is wrong
and the response's "177" is correct.** The committed manuscript says "176 nucleotides" twice; the
proposed file says 177 nucleotides spanned and 176 supplied by NR4A3, which are both true and are
not the same quantity — that distinction is what the original sentence collapsed.

## 3 · Scientific and structural DECISIONS a human must take — NOT done here

None of these is in the diff. Each is a judgement, with my recommendation and its basis.

**D1 · Retitle.** Recommend yes, to a title naming the result rather than the proposal. Basis: the
changelog registers both former titles as superseded and says the replacement "names the result
rather than the proposal". **But the changelog does not state the new title**, so the exact wording
is a human choice (see U1). Consequence if taken: `systems/views/L3-publications.md` and
`emc-atr-vulnerability-assessment.md` quote the old title and go stale.

**D2 · Delete Appendix A.** Recommend yes. Basis: the changelog's header states it *is* the former
Appendix A and that "Nothing was dropped in the move" — the content is already committed elsewhere,
so deleting it loses nothing and removes ~40% of main-text length plus four references to this
repository's own house-rules file from a submission file. Left in the proposed file because
deleting 27 lines of the shared paper's content is a version decision, not a correction.

**D3 · Insert Figure 1 and cut to six tables.** Recommend yes in principle. Basis: the figure files
are committed; the changelog specifies one three-panel figure with the gene-model table (Table 2)
and the wild-type-control table (Table 7) moved to supplementary. **I did not do it**, because the
caption must describe what the panels actually show and I did not open the images (U2).

**D4 · Reduce P1-P5 to three predictions.** Recommend yes. Basis: the changelog's reasoning is
checkable against the committed manuscript and is correct — P4's falsifier as written *is* P2's
falsifier ("the pair showing no kinetic difference" vs "type 1 recruiting no earlier than type 2"),
so the set counts one experiment twice; and P1 as written is an equivalence ("kinetics
indistinguishable from EWSR1-FLI1"), which a null result cannot falsify and an underpowered
experiment satisfies. **Not applied**: dropping and re-deriving a pre-specified prediction set is a
scientific act on a preregistration-shaped table, and the repository's own rule is that
preregistrations are preserved. A human must decide whether this is a correction or a new
registration, and the machine-readable
`rgg_dose_calibration_and_predictions.registered_predictions` must move with it.

**D5 · Move the "Scope of the claims" blockquote into Limitations.** Recommend yes, unchanged in
wording. Basis: the changelog states every sentence is retained and only the position changes.
Low-risk but still a structural edit to a shared file.

**D6 · Renumber into a Discussion (§4.1 procedure, §4.2 axis, §4.3 comparator, §4.4 Limitations).**
Recommend deferring until D3 and D4 are settled. Basis: the changelog's later-same-day entry cites
§4.1-§4.4 and §2.3, section numbers **that do not exist in the committed manuscript**, so the
revision restructured the paper. Applying cross-references before the structure is fixed produces
dangling pointers.

**D7 · Add §2.3 (exon-numbering correspondence) and §4.1 (the six-step construct procedure with
Supplementary Table S3).** Recommend yes as content. Basis: the changelog names the inputs and even
the initiator positions (EWSR1 cDNA nucleotide 70, TAF15 87). **Not drafted**: these are new
sections whose wording no committed input fixes (U3, U4).

## 4 · UNRESOLVED — with the exact missing input for each

- **U1 · The new title.** The changelog registers both former titles as superseded but never states
  the replacement. *Missing input: the title string.* Nothing in the tree carries it.
- **U2 · The Figure 1 caption and panel assignments.** The changelog refers to "Figure 1B" (the
  axis) and "Figure 1C" (the seam) and to "one scope clause … in the Figure 1 caption naming type 2
  as the only reported junction at the exon 2 acceptor", but no caption text is committed and panel
  A is never named. *Missing input: the caption, or a reading of
  `research/manuscripts/figures/emc-fusion-frame-fig1.png` to establish what each panel shows.*
- **U3 · The §4.1 six-step procedure.** The six steps are listed by gist in the changelog
  ("establish the junction, assemble the transcript, translate once from the 5' partner's initiator,
  predict from the donor phase, verify against the expected open reading frame, and grade a junction
  absent from Table 3") but no prose exists. *Missing input: the drafted procedure, and
  Supplementary Table S3's per-junction cut coordinates, assembled cDNA length and ORF.* The source
  artifact `emc-fet-construct-designs.json` exists but the table was not built in this lane.
- **U4 · §2.3, the exon-numbering correspondence.** *Missing input: the drafted section, and the
  widened limitation 3 text naming the missing second annotation source.*
- **U5 · The ORCID.** Line 32 still reads `[ORCID TO BE SUPPLIED BY THE AUTHOR BEFORE SUBMISSION]`
  and the manuscript's own editorial block says "No ORCID is given because the repository carries
  none." *Missing input: an ORCID iD from the author.* It cannot be invented and was not changed.
- **U6 · Bibliographic fields for the two added references.** The artifact holds authors, title and
  PMID for Okamoto 2001 and Sjögren 2003 but no journal, year, volume or pages. Those fields are
  **left explicitly marked in the proposed reference list rather than written.** *Missing input: a
  retrieval record for PMID 11679947 and PMID 12598313.* No network was used.
- **U7 · The cover letter.** The changelog records corrections to cover-letter ¶3 (the rank claim
  and the 176-nt sentence). The cover letter was not opened or edited in this lane; it is outside
  the file this contract names.
- **U8 · The whole later-same-day changelog block corrects text that is not committed anywhere.**
  Its "before this revision" column quotes sentences from the **first** revision — e.g. the Abstract
  sentence *"The insertion belongs to the acceptor, so any fusion using NR4A3 exon 2 carries it…"* —
  which do not appear in the committed manuscript. Those items therefore cannot be applied as
  find-and-replace against the committed baseline at all; only their end states are known.
  *Missing input: the first-revision draft.* Four of the five superseded rows in that block are in
  this category. This is a finding, not a failure: **the ATR package has TWO missing revision
  passes, not one**, and the second cannot be reached without the first.

## 5 · Coverage, honestly

The blocker records 41 items. This lane's diff carries **15 mechanical corrections** covering the
items a committed artifact settles, plus **7 decisions** and **8 unresolved entries**. It does not
cover 41 items and does not claim to. Roughly: the numeric and register corrections are done, the
structural revision is prepared as decisions, and the two new sections plus the figure caption
remain unwritten for want of committed inputs.

## 6 · What was NOT done

No shared path was written, copied, moved or restored. No git write. No gate rerun, no
`scripts/preflight.sh`, no network, no source retrieval, no history hunt, no census, no whole-paper
re-review. The figure images were not opened. The cover letter, the registry, the views and every
clinical artifact were untouched. No EMC efficacy, safety, selectivity or clinical-readiness claim
is made anywhere in the proposed text; there is no wet lab. No content-policy refusal occurred.

## 7 · Retained paths

    /tmp/claude-0/r1-lane/BASELINE-emc-atr-collaborator-package.md   (git show HEAD, unmodified)
    /tmp/claude-0/r1-lane/PROPOSED-emc-atr-collaborator-package.md   (the proposed candidate)
    /tmp/claude-0/r1-lane/PROPOSED-emc-atr-collaborator-package.diff (232-line unified diff)
    /tmp/claude-0/r1-lane/build_candidate.py                         (the edits, replayable)
    /tmp/claude-0/r1-lane/DECISION-MEMO.md                           (this file)
