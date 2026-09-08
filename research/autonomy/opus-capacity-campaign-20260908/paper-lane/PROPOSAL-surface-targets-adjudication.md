# PROPOSAL — surface-target batch: what root must decide, with concrete scope

**Status: PROPOSAL. Nothing here is applied. The manuscripts are at HEAD.**
Date 2026-09-08. Parent-filed, from an independent verification of a completed lane's output.
Evidence: `VERIFY-surface-targets.md`; preserved output in `NOT-ACCEPTED-surface-targets/`.

## Why the batch was not integrated

34 load-bearing claims checked against the committed artifacts: **21 CONFIRMED, 9 REFUTED,
4 UNVERIFIABLE.** The confirmed corrections are real and well-sourced. Five refutations are not
editorial, and one of them is a claim the diff made *worse*. Committing the batch would have shipped
those five, so the parent reverted and preserved rather than partially applying its own judgement.

⛔ Per root's standing instruction, the parent has **not** silently amended any of this.

## D1 · Five substantive refutations, all against ONE committed artifact

`research/modalities/emc-tissue-read-statistics.json` is committed, is named **nowhere** in either
document, and contradicts:

1. **"No reprocessing or sensitivity analysis was run."** The artifact holds
   `sensitivity_reference_matched_GPL3290_DFSP_only` — exactly that analysis. ⚠ **The diff deleted
   the word "here", turning a scoped statement into an unscoped false one.** This is the one place
   the batch actively worsened the manuscript.
2. **"No multiple-testing correction is applied"** (three occurrences). The artifact holds
   within-platform BH q for the whole board and states "Every count in the manuscript is derived
   from this file".
3. **"Exactly five are concordantly elevated — VCAN, BGN, CD44, GPC1 and ALCAM."** Corrected states
   give **three** (BGN, CD44, VCAN). ALCAM's GPL3290 q = 0.162 with a CI crossing zero. ⚠ This
   undercuts an ALCAM headline that appears in the Abstract, Results, Discussion and Conclusion.
4. **"B7-H3 is not elevated on either instrument."** The paper's own Table 4 shows CD276 at 1.42×
   other sarcomas in the sequencing cohort.
5. **"Six carry no EMC-tissue array contrast elsewhere in this repository's artifacts."** The
   artifact carries contrasts for all six.

**Decision root must take:** whether the manuscript is corrected against
`emc-tissue-read-statistics.json`, and if so by whom. ⛔ The parent proposes no replacement number
and has computed none. This is a manuscript science change on a paper the parent does not own.

## D2 · A conflict with a committed sibling, outside the diff

`emc-surface-target-landscape-review-response-2026-08-10.md` is committed and states this revision
was **already applied** — concordant set 5→3, selective set **18** (not eight), the
"negatives transferred, positives did not" sentence removed. None of that is in the manuscript, and
the batch's own eight→nine change conflicts with the sibling's 18.

**Decision root must take:** which document is authoritative. Until that is settled, any edit to the
selective-antigen count risks shipping a third incompatible figure — the exact failure mode the
mortality death-count hold was written to prevent.

## D3 · Four editorial defects the batch introduced

Cheap and self-contained, but still the paper owner's to apply, not the parent's:
the Abstract says "Nine…" then "none of **the eight**"; "CSPG4 was not among the antigens the filter
saw" is false (CSPG4 is in `emc-surface-normal-window.json`, Table 1 and Table S2 — the true
statement is that it has no row in the *selectivity scan*); Table S2's new caption says "every
antigen this paper names" while its own next sentence says "the subset"; and the DLL3 "(Note S3)"
points at the CSPG4 note.

## D4 · Two claims with nothing behind them — flagged under the no-wet-lab rule

No sentence in the batch asserts efficacy, safety, a selectivity margin, a therapeutic window or
clinical readiness. Two residues are weaker than they read and should be scoped or withdrawn:
**"B7-H3 protein can be tumour-restricted"** carries no citation and no artifact; and **"a poor
address for any modality that acts wherever the antigen is"** is a modality-suitability verdict drawn
from transcript data alone.

## What is NOT in dispute

The verifier independently re-derived and confirmed: the nine selective antigens (each
`selectivity_significant: true`); the six-subtype class definition; L1–L5 in
`surfaceome-instrument-limits.json`; DLL3 RESTRICTED at q = 0.0079 — and computed the full
significant ∩ RESTRICTED intersection itself, finding it is exactly `{DLL3}`; LRRC15 ENHANCED_BROAD;
CSPG4 at 8.730/1.767 = 4.94, so "roughly five times" corrects a previous "order of magnitude" that
was overstated about twofold; the MKI67 GPL3290 cell that had wrongly read "not reported"; all four
new Table S3 panels gene-for-gene; and all seven reference entries field by field.

⭐ **So the batch is not worthless and should not be discarded.** The recommendation is that root
admit a bounded repair that keeps the 21 confirmed corrections, fixes D3, resolves D2 first, and
treats D1 as a separate scientific decision on a paper with a named owner.

## Fences that apply to any follow-up

⛔ No producer re-run, no figure rebuild, no source fetch, no new full CI run. ⛔ No efficacy,
safety, selectivity-margin, therapeutic-window or clinical-readiness claim. ⛔ No renumbering of the
selective set until D2 is settled.
