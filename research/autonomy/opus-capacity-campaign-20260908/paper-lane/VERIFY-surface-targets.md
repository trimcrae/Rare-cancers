# Independent verification — surface-target landscape working-tree diff

**Verifier:** independent reviewer. Did not write either manuscript file. Read-only pass: no manuscript
or artifact was edited, nothing was staged, committed or pushed, no producer, figure build, gate or
test suite was run, and no network request of any kind was made.

**Target:** the uncommitted changes to
`/home/user/Rare-cancers/research/manuscripts/surface-targets/emc-surface-target-landscape.md` and
`/home/user/Rare-cancers/research/manuscripts/surface-targets/emc-surface-target-landscape-si.md`,
against HEAD `593e8dece`.

## Headline

| | count |
|---|---|
| Load-bearing claims added or changed by the diff and checked | **34** |
| CONFIRMED | **21** |
| REFUTED | **9** |
| UNVERIFIABLE | **4** |

Plus three separate findings that are not per-claim verdicts: a conflict with a committed sibling
document (F1), two sentences that assert target properties no artifact establishes (F2, F3), and the
`git checkout` question, answered at the end.

**The single most important result of this pass:** a committed artifact,
`research/modalities/emc-tissue-read-statistics.json`, is named nowhere in either document and
contradicts several of the counts the manuscript prints and the diff's own Appendix A6 claims to have
re-verified. Two of the diff's edits make that conflict *worse* rather than better. Details at R5–R7.

---

## CONFIRMED (21)

Each row states the artifact path, the key path I actually read, and the value.

| # | Claim (diff-added/changed) | Artifact, key path, value |
|---|---|---|
| C1 | ORCID `0000-0002-1823-1451` in both author blocks; editorial note says the author supplied it | `.zenodo.json:10` `creators[0].orcid = "0000-0002-1823-1451"`; also `deploy/release-doi.md:53` (CITATION.cff and .zenodo.json both carry it). ISO 7064 MOD 11-2 check digit recomputes to `1`, matching. **CONFIRMED** |
| C2 | Results: "selectivity was significant for nine of the evaluated classic antigens: CDH11, KIT, CD248, FGFR1, NCAM1, GPC2, PTK7, MCAM and EPHB4" | `research/modalities/emc-surfaceome-scan.json` → `actionable_antigens.<gene>.selectivity_significant` is `true` for all nine. q values: CDH11/KIT/CD248/FGFR1/NCAM1/GPC2 = 0.0, PTK7 = 0.0002, MCAM = 0.0032, EPHB4 = 0.0003. Non-selective as stated: CD276 q = 1.0, EGFR q = 1.0, FAP q = 0.1555. **CONFIRMED** for the nine named, scoped to Table 1's "classic antigens". ⚠ Scope caveat: the artifact records **18** selectivity-significant rows among 47 `actionable_antigens` (adds ALK, DLL3, ENPP1, FGFR4, PDGFRA, PDGFRB, ROR1, SLC34A2, STEAP1). The Abstract's bare "Nine evaluated antigens were selective" is not the artifact's count of selective antigens — see F1 |
| C4 | "Table 3 reads eight of the nine in tissue; CD248 … is in Table 4" | Manuscript Table 3 lists FGFR1, PTK7, CDH11, MCAM, KIT, NCAM1, EPHB4, GPC2 (8) plus EGFR and CD276 marked not selective; CD248 appears in Table 4. **CONFIRMED** |
| C5 | Methods/S2: class defined by substring match, terms "ewing, synovial, myxoid, alveolar, desmoplastic small round, clear cell sarcoma, extraskeletal"; six subtypes returned incl. alveolar rhabdomyosarcoma; no DSRCT line matched; n = 76; 45 with expression | `emc-surfaceome-scan.json` → `class_definition.translocation_sarcoma_subtypes` = exactly those seven strings; `class_definition.class_oncotree_subtypes_present` = `['Alveolar Rhabdomyosarcoma','Alveolar Soft Part Sarcoma','Clear Cell Sarcoma','Ewing Sarcoma','Extraskeletal Myxoid Chondrosarcoma','Synovial Sarcoma']` (six, no DSRCT); `class_definition.n_class_lines = 76`; every per-gene row carries `n_class = 45`. **CONFIRMED** — this is a real improvement: the previous text named DSRCT as a class member and omitted alveolar rhabdomyosarcoma |
| C6 | Methods: "Five limits of this instrument were computed" (was four) | `research/modalities/surfaceome-instrument-limits.json` → `limits` keys = `L1_no_stromal_compartment`, `L2_stromal_floor_demonstrated`, `L3_glycan_unrankable`, `L4_cspg4_coverage_gap`, `L5_no_emc_fap_observation`. **CONFIRMED** |
| C7 | SI Note S1 L2: LRRC15 mean 0.14 / frac 0.0; FAP 1.37 / 0.16; CD248 3.01 / 0.44 / q = 0.0; PDGFRB 2.14 / 0.24 / q = 0.0001; the narrowed limit | `surfaceome-instrument-limits.json` → `limits.L2_stromal_floor_demonstrated.genes` and `.counter_reading_that_narrows_the_limit` carry exactly those four gene blocks and the narrowing note nearly verbatim. Cross-checks against `emc-surfaceome-scan.json.actionable_antigens` agree on every value. **CONFIRMED** |
| C9 | DLL3 is RESTRICTED and selectivity-significant at q = 0.0079 on +0.29 log2TPM, 11 % of class lines expressing; "the one antigen in the artifacts that is both selective and restricted" | `research/modalities/emc-surface-normal-window.json` → `antigens.DLL3.window = "RESTRICTED"`; `emc-surfaceome-scan.json` → `actionable_antigens.DLL3` = `{selectivity_q: 0.0079, enrichment_vs_rest: 0.29, class_frac_expressed: 0.11, selectivity_significant: true}`. I computed the full intersection myself: significant set (18) ∩ RESTRICTED set (ALCAM, ALPP, B4GALNT1, CTAG1B, DLL3, GPC3, MAGEA4, PRAME) = **{DLL3}** exactly. **CONFIRMED**, uniqueness included |
| C10 | Table 1 LRRC15 verdict changed from "not scored in this filter" to ENHANCED_BROAD; new SI Table S2 row | `emc-surface-normal-window.json` → `antigens.LRRC15` = `{rna_tissue_specificity: "Tissue enhanced", rna_tissue_distribution: "Detected in many", rna_blood_cell_specificity: "Not detected in immune cells", window: "ENHANCED_BROAD"}` — matches the new Table S2 row field for field. **CONFIRMED**; the old cell was wrong |
| C11 | "Two classic antigens carry a restricted prior: B4GALNT1 … and ALCAM" | Of Table 1's 18 rows, only `B4GALNT1` and `ALCAM` carry `window = "RESTRICTED"` in `emc-surface-normal-window.json`. (The artifact's other RESTRICTED entries — ALPP, CTAG1B, MAGEA4, PRAME, GPC3, DLL3 — are not Table 1 rows.) ALCAM enrichment −1.45, `selectivity_significant: false`. **CONFIRMED** |
| C13 | CSPG4 sequencing median 8.730 is "roughly five times the next-largest row in that panel (CD248, 1.767)", 3.31× normal, 2.51× other-sarcoma | `research/modalities/aso-delivery-antigen.json` → `per_antigen.CSPG4.exposure_axis…emc_median = 8.729579519`, `normal_median = 2.636317921`, `ratio = 3.3113`; `…3SEQ_vs_32_other_sarcoma_libraries.ratio = 2.5053`. I sorted all 12 `per_antigen` EMC medians: CSPG4 8.730, then CD248 1.767, then RET 0.637. 8.7296 / 1.767 = **4.94**. **CONFIRMED** — and the superseded "an order of magnitude" was indeed overstated by ~2× |
| C14 | CSPG4 Δ = +0.885 (t = 7.42) on GPL6244, Δ = −0.189 (t = −0.40) on GPL3290 | `research/modalities/emc-expression-panels.json` → `reads.read_8_SURFACE_ANTIGEN.cross_platform_board.per_gene.CSPG4.per_platform`: GPL6244 `delta 0.8852, t 7.419, df 7.7`; GPL3290 `delta -0.1893, t -0.403, df 10.1`. **CONFIRMED** |
| C15 | CSPG4's normal-tissue prior is "tissue-enhanced, that is detected broadly with a peak and not restricted" (main + SI), replacing "the broad-liability list" | `emc-surface-normal-window.json` → `antigens.CSPG4.window = "ENHANCED_BROAD"`, `rna_tissue_specificity = "Tissue enhanced"`, `rna_tissue_distribution = "Detected in many"`; `aso-delivery-antigen.json` → `per_antigen.CSPG4…hpa_normal_tissue_prior.state = "BROAD_WITH_A_PEAK"`. **CONFIRMED**; the old wording named the wrong verdict tier |
| C16 | Table S6: CD248 row (2 peaks, 1.767 / 2.107 / 2.715) moved to rank 2 | `aso-delivery-antigen.json` → `per_antigen.CD248…emc_median 1.766684664, normal_median 2.1068718245, n_peaks 2`; other-sarcoma median follows from `ratio 0.6507`. The row was previously mis-sorted between MSLN (0.257) and PRAME (0.102). **CONFIRMED** |
| C17 | MKI67 flat on GPL6244 (Δ +0.129, t 0.53, df 8.7) and not flat on GPL3290 (Δ +1.236, t 2.30, df 5.5); the control's expectation was written for GSE24369 only | `emc-expression-panels.json` → `reads.control.gene_readability.MKI67`: GPL6244 `delta_a_minus_b 0.129, t 0.528, df 8.7`; GPL3290 `delta_a_minus_b 1.2358, t 2.301, df 5.5`. `reads.control.expected.MKI67` = "approximately FLAT **in GSE24369**". **CONFIRMED**, and the SI's superseded "not reported" cell was indeed wrong |
| C18 | Route-named panel: Δ −0.0935 (t −1.66, 11/11) on GPL6244, Δ +0.599 (t 2.91, 8/11) on GPL3290; the three missing are CD248, CD276 and SSTR2 | `emc-expression-panels.json` → `…panels.surface_antigen.groups.route_named_addresses.per_platform`: GPL6244 `{t -1.655, delta -0.0935, n_genes_readable 11}`; GPL3290 `{t 2.905, delta 0.5985, n_genes_readable 8, genes_not_readable ["CD248","CD276","SSTR2"]}`. **CONFIRMED** |
| C19 | Table S3: four new panel rows — ofCS carriers (18), sarcoma cell-surface addresses (30), alkaline-phosphatase family (4), HLA-presented intracellular (10) — and "All nine panels" | `emc-expression-panels.json` → `…panels.surface_antigen.groups` has exactly **9** groups; `genes_requested` for `ofcs_carrier_proteoglycans` (18), `sarcoma_cell_surface_addresses` (30), `alkaline_phosphatase_family` (4) and `hla_presented_intracellular_antigens_NOT_surface` (10) match the printed lists **gene for gene and in order**. `provenance` confirms the repo-curated framing. **CONFIRMED** |
| C20a | SI Table S2 preamble: the artifact "classifies 46 antigens in total" | `emc-surface-normal-window.json` → `len(antigens) = 46`, `_drift_vs_previous_artifact.n_now = 46`. **CONFIRMED** (minor: ALPPL2 is a row with no `window` — a not-found record — so 45 carry a verdict) |
| C21 | Reference preamble: entries 4, 5, 6, 13, 16, 17, 18 come from `remaining-reference-metadata-2026-08-09.json`; the remaining eleven from `submission-reference-metadata-2026-08-09.json` | All seven PMIDs (35974707, 34340159, 25613900, 30373828, 10537274, 12378528, 28076709) are in `research/literature/remaining-reference-metadata-2026-08-09.json.records`; all eleven others (41055792, 36563884, 41323055, 15920699, 26310886, 28341109, 26961907, 36316541, 40580361, 34966741, 34413129) are in `submission-reference-metadata-2026-08-09.json`. 7 + 11 = 18 = the reference count. **CONFIRMED** |
| C22 | Appendix A5: the seven entries were "re-checked field by field against that record … and each matched" | I re-checked all seven myself against `remaining-reference-metadata-2026-08-09.json.records`. Journal, year, volume, issue, pages and first-six author order match in every case, including the two edge cases: ref 5 has `issue: ""` and prints `2021;99:102260`; ref 16 has `doi: null` and prints no DOI. **CONFIRMED** |
| C23 | Limitations: "Every reference below now carries bibliographic detail taken from a committed retrieval record … none is marked as unretrieved" | No "not yet retrieved" marker survives in the reference list; every printed identifier resolves in one of the three named records (ref 15's Cellosaurus entry via its primary-source PMID 34413129, present in the submission record). **CONFIRMED** |
| C24 | Methods pointer corrected from "Supplementary Tables S1 to S8" to "S1 to S7"; "Supplementary Methods S1 to S6" | The SI has Supplementary Methods S1–S6, Tables S1–S7 and Notes S1–S5. **CONFIRMED** |
| C32 | Discussion negative: "the stromal panel is lower in EMC on both platforms" | `emc-expression-panels.json` → `…groups.stromal_and_matrix_antigens.per_platform`: GPL6244 `delta -0.3281, t -1.89`; GPL3290 `delta -0.4668, t -1.801`. Direction **CONFIRMED**. ⚠ Both |t| < 2, i.e. *flat* under this paper's own board convention, so presenting it in the Discussion as one of three "negatives with a named basis" states it more firmly than the numbers support |
| C36 | Ethics/AI-use rewrites (main Declarations, preprint-deposit box, new SI declarations block) | Non-quantitative. The new wording — no approval sought, no exemption determination requested, no "not required" determination invented, original collection is the depositing studies' matter, named model providers, no LLM as author — asserts less than the text it replaces. **CONFIRMED as an honest narrowing**, no number involved |

---

## REFUTED (9)

### R1 (C3) — the Abstract now contradicts itself: "Nine … " then "none of the eight"

The diff changed the Abstract's first Results sentence to "**Nine** evaluated antigens were selective"
but left the third sentence reading "In tumour tissue, **none of the eight** was concordantly elevated
on both arrays". Results and Conclusion were both updated to nine. As it stands "the eight" has no
antecedent in the Abstract. **True value: nine** (Results §"Every antigen the surrogate called selective
… None of the nine"; Conclusion "none of the nine surrogate-selective antigens"). One-word fix, but it
is exactly the main-text/abstract disagreement this pass was asked to look for, and it was *introduced*
by this diff.

### R2 (C12) — "CSPG4 was not among the antigens the filter saw" is false against the filter's artifact

Main text, Results, changed line: *"CSPG4 was not among the antigens the filter saw, so its absence from
the intersection is a property of the evaluated set."* The filter is defined two sentences earlier as
the normal-tissue prior.

- **True value:** `emc-surface-normal-window.json` → `antigens.CSPG4.window = "ENHANCED_BROAD"`. The
  filter saw CSPG4 and classified it. `_drift_vs_previous_artifact.newly_added_this_run` names CSPG4
  explicitly.
- The manuscript's own **Table 1** prints CSPG4 with normal-tissue verdict ENHANCED_BROAD, and the SI's
  **Table S2** carries a CSPG4 row. So the sentence contradicts two tables in its own submission.
- What *is* true is the narrower statement: CSPG4 has no per-gene row in the **selectivity scan**
  (`emc-surfaceome-scan.json` — I confirmed `actionable_antigens` has no CSPG4 key), which is why it
  cannot enter a selective∩restricted intersection.
- Note the same stale premise in SI Note S1 L4 ("no row in the normal-tissue prior artifact of that
  stage") and in `surfaceome-instrument-limits.json` → `limits.L4_cspg4_coverage_gap.in_emc_surface_normal_window = false`.
  That artifact field is **stale** relative to the current normal-window artifact. The manuscript
  inherited a stale field instead of reading the artifact it names.

### R3 (C20b) — Table S2's new caption overclaims and contradicts its own next sentence

New caption: *"Normal-tissue classification for **every antigen this paper names**, plus the four
controls."* The next sentence says *"the rows below are **the subset** cited in the main text and this
document."* Both cannot hold.

**True value:** Table S2 has 26 antigen rows. Antigens the paper names in Tables 4/5 and the Results
that are classified in `emc-surface-normal-window.json` but absent from Table S2 include **CD44**
(BROAD_LIABILITY), **VCAN** (VITAL_OR_IMMUNE_LIABILITY), **GPC1** (ENHANCED_BROAD), **MSLN**
(ENHANCED_BROAD), **L1CAM** (ENHANCED_BROAD), **CDH17** (VITAL_OR_IMMUNE_LIABILITY), **PDGFRB**
(BROAD_LIABILITY). The "subset" half of the caption is correct; the "every antigen this paper names"
half is not. (All 26 rows that *are* printed match the artifact field for field — I checked all four
columns of every row programmatically; zero mismatches, controls included.)

### R4 (C25) — the DLL3 cross-reference points at the wrong section

Main text line 282: *"DLL3 … is RESTRICTED and selectivity-significant at q = 0.0079 … **(Note S3)**."*

**True value:** SI **Note S3** is "CSPG4, held open". The DLL3 material the diff added lives in
Supplementary **Methods** S3 ("Normal-tissue prior and its classification semantics"). The SI numbers
Methods and Notes in parallel S-series, so "Note S3" resolves to the wrong section. (Line 397's
"(Note S3)" for the CSPG4 explanations *is* correct.)

### R5 (C26) — "No reprocessing or sensitivity analysis was run" is false; the diff strengthened it

Methods, changed line: the previous text read *"No reprocessing or sensitivity analysis was run **here**,
so the mismatch is disclosed rather than excluded."* The diff **deleted "here"**, turning a scoped
statement into an unscoped one. SI Note S3 already carried the unscoped version: *"no sensitivity
analysis recomputing the GPL3290 contrasts against the three dermatofibrosarcoma protuberans arrays
alone was run, **here or elsewhere in this study**."*

**True value:** `research/modalities/emc-tissue-read-statistics.json` (committed, clean at HEAD) contains
a top-level key `sensitivity_reference_matched_GPL3290_DFSP_only`, whose `_what` reads: *"GPL3290 with
the three GIST arrays dropped, leaving a comparator arm processed like the EMC arm: mRNA against a CRH
reference on both sides."* It carries per-gene Δ, t, df, exact p, 95 % CI and BH q. The CSPG4 row is
`{delta: -0.5179, t: -1.839, df: 9.8, p: 0.096426, ci: [-1.1473, 0.1115], n_emc: 10, n_comparator: 3,
q: 0.182427, significant: false}`. The same file also carries
`sensitivity_GPL6244_with_solitary_fibrous_tumour` and `normal_skeletal_muscle_anchor`. The exact
analysis both documents say was never run **was run and is deposited**, and it is the analysis the
CSPG4 discussion turns on.

### R6 (C27) — "No multiple-testing correction is applied" is false

Three places assert this: main text line 244 ("No multiple-testing correction is applied anywhere in the
tissue read"), the diff-condensed Limitations line 498 ("No multiple-testing correction is applied"), and
SI line 449.

**True value:** `emc-tissue-read-statistics.json._correction` = *"Benjamini-Hochberg within platform,
across every gene on the board that produced a contrast on that platform."* Its `_why` states: *"Every
count in the manuscript is derived from this file rather than from a |t| threshold."* Its `_verified_against`
is `emc-expression-panels.json`, which it reproduces before writing.

### R7 (C28) — "exactly five are concordantly elevated" and the whole ALCAM headline

Main text: *"Across the 100 genes on the cross-platform board, exactly five are concordantly elevated in
EMC … VCAN, BGN, CD44, GPC1 and ALCAM (Table 5)"*, plus the Abstract ("ALCAM rose on both arrays"),
Results ("The single antigen elevated on both arrays is ALCAM"), the diff-changed Discussion (*"ALCAM is
higher in EMC than in other sarcomas in all three cohorts"*, "a demoted but intact marker") and the
Conclusion ("the one antigen that is elevated on both, ALCAM").

**True value:** `emc-tissue-read-statistics.json.cross_platform_state_corrected.by_state` gives
`CONCORDANT_UP_ON_BOTH = ['BGN', 'CD44', 'VCAN']` — **three, not five**. ALCAM and GPC1 are both
`MOVED_ON_ONE_FLAT_ON_THE_OTHER`. The driver: `primary.GPL3290.ALCAM = {delta 0.7535, t 2.214, df 8.5,
p 0.055956, ci [-0.024, 1.531], q 0.161652, significant: false}` — the 95 % interval crosses zero. Also
under correction: EGFR is `MOVED_ON_ONE_FLAT_ON_THE_OTHER`, not "concordant down on both"; CDH11 is
`MOVED_ON_ONE_FLAT_ON_THE_OTHER`, not "discordant, opposite signs".
The diff's added hedge — *"an uncorrected transcript-level reading in 6, 10 and 4 tumours"* — is honest
about the method but does not rescue "in all three cohorts" or "intact marker" once the correction the
repository has already computed is applied.

### R8 (C31) — "B7-H3 … is not elevated in EMC on either instrument" contradicts the paper's own Table 4

Discussion, changed line: *"B7-H3 is not elevated in EMC on either instrument and reads lower than
comparator sarcomas on the one platform that reads it."*

**True value:** Table 4's own sequencing columns for CD276 read **1.30× vs 27 normal organs** and
**1.42× vs 32 other sarcomas** (`aso-delivery-antigen.json` → `per_antigen.CD276`, and
`gse28866-tumour-vs-normal.json`). The sequencing cohort *is* one of the tissue instrument's three
cohorts and it reads CD276 above the other-sarcoma median. "The one platform that reads it" is true
only of the two arrays. Separately, the GPL6244 contrast the sentence rests on is
`primary.GPL6244.CD276 = {delta -0.249, t -2.549, p 0.034108, q 0.087575, significant: false}` — not
significant under the repository's own correction.

### R9 (C33) — "carry no EMC-tissue array contrast elsewhere in this repository's artifacts"

Results, changed line: *"Six of them, ALCAM, CD248, CD276, FAP, PRAME and SSTR2, carry no EMC-tissue
array contrast elsewhere in this repository's artifacts."*

**True value:** `emc-tissue-read-statistics.json.primary.GPL6244` carries a full EMC-vs-comparator array
contrast for **all six** — e.g. `ALCAM {delta 1.0907, t 7.008, p 1.2e-05, q 0.000373, significant: true}`,
`SSTR2 {delta -0.0424, p 0.707208, q 0.790409}` — and `primary.GPL3290` carries ALCAM, FAP and PRAME.
`research/modalities/surface-address-sensitivity.json` and
`research/modalities/emc-fourth-cohort-route-readout.json` also carry array readouts for these symbols.
(The replaced claim — "gained their first EMC-tissue array contrast in this work" — was a priority claim
and was rightly withdrawn; the replacement is a *different* claim that is also false, just less
consequentially.)

---

## UNVERIFIABLE (4)

| # | Claim | Why |
|---|---|---|
| U1 (C8) | Methods: *"the scan holds no disease observation of FAP, **for both of the preceding reasons**"* | `surfaceome-instrument-limits.json.limits.L5_no_emc_fap_observation` gives two reasons: `reason_1_compartment` (no CAF compartment, per L1) and `reason_2_identity` (the only subtype-annotated line is ACH-001519, whose EMC identity is retracted). The **identity** reason is not one of the sentences preceding this one in that paragraph — the preceding ones are the stromal floor, the glycan, and the CSPG4 coverage gap. As written the pointer does not resolve to the artifact's two reasons |
| U2 (C29) | Appendix A6: *"Every printed quantity in the main text and the Supplementary Information was re-read against the artifact it names, and the main text and Supplementary Information were compared wherever both state the same fact."* | Cannot be confirmed and is contradicted in practice: R1 is a main-text/abstract disagreement the diff created, and R5–R7 are printed quantities whose governing artifact (`emc-tissue-read-statistics.json`) is named nowhere in either document. The claim is a process assertion with no artifact behind it |
| U3 (F2) | Results: *"B7-H3 protein **can be tumour-restricted** despite broad transcript expression"* | No citation and no artifact. The diff removed the clause that at least gestured at a basis ("which is the basis of its clinical traction") and kept the tumour-restriction assertion itself. This is precisely a "target is tumour-restricted" claim with nothing checkable behind it; nothing in this repository measures B7-H3 protein |
| U4 | Results: *"Six of them … carry no EMC-tissue array contrast **elsewhere in this repository's artifacts**"* — the scope of the negative | Even setting aside R9, an exhaustive negative over "this repository's artifacts" is not verifiable by the reader from any named source. A claim of this shape needs either a named enumeration or removal |

---

## Other findings

### F1 — conflict with a committed sibling document in the same directory

`research/manuscripts/surface-targets/emc-surface-target-landscape-review-response-2026-08-10.md`
(committed, clean at HEAD) states, under "What changed, at a glance":

> "Under alpha 0.05 with within-platform correction the concordantly elevated set falls from five to
> three (VCAN, BGN, CD44); ALCAM and GPC1 do not survive … The selective set is redefined as every
> actionable antigen with BH *q* < 0.05, which is **18** rather than eight … Two sensitivity analyses
> and one normal soft-tissue anchor, all runnable from committed data, were added."

and, under Major point 2, that *"the surrogate's negatives transferred and its positives did not"* was
removed from the abstract, Results, Discussion and cover letter as contradicted by Table 5.

None of that is in the working-tree manuscript. It still prints five concordant genes, still carries the
asymmetry sentence in both the Abstract's Conclusions and the Results, and Tables 3–4 carry no q or CI.
This diff moves the selective count from eight to **nine**, which conflicts with the sibling's **18**.
I cannot tell from the tree whether the response document describes work that was reverted, or work that
was written up but never applied — but the parent should resolve that before committing, because the two
documents cannot both be published as they stand. (Both files are the outputs of a *simulated* internal
review; neither is a journal document, and the review file says so in a banner.)

### F2 / F3 — fence check on efficacy, safety, selectivity margin, window and readiness

I read every added and changed line for such claims. Both documents are, on the whole, unusually
disciplined here: the diff's changes to the Scope box, the SSTR2 paragraph ("the gate is unchanged …
no quantity here measures either") and the AI/ethics declarations all *reduce* the strength of the
claims. Two residues to flag:

- **F2** = U3 above: "B7-H3 protein can be tumour-restricted" — a tumour-restriction property asserted
  of a protein with no measurement and no citation.
- **F3**: Discussion, changed line — *"an antigen elevated against other sarcomas but not against normal
  visceral organs, which is ALCAM's exact profile, remains a candidate lineage marker worth testing and
  **is a poor address for any modality that acts wherever the antigen is**."* The first half was
  correctly softened by this diff (from "is a usable diagnostic or lineage marker"). The second half is
  still a modality-suitability verdict derived from transcript abundance in 6, 10 and 4 tumours. It is
  reasoning rather than a measurement, and it reads as a conclusion; it should be marked as an
  inference, not a finding. No sentence in the diff asserts efficacy, safety, a selectivity margin, a
  therapeutic window or clinical readiness outright.

---

## The `git checkout --` question: was anything lost?

**No. Nothing was lost.**

The lane reported running `git checkout -- research/manuscripts/neoantigen/emc-vaccine-development-path.md`
and destroying a sibling's in-flight edits. I checked commit `414e661c9` ("Vaccine path: two miscounts
fixed, unsupported proteome counts withdrawn"):

- `git merge-base --is-ancestor 414e661c9 HEAD` → **true**. The commit is in the history HEAD points at.
- All three changes it describes are present in that commit's patch **and** in the current working-tree
  file (which `git status` reports clean):
  1. **8 → 6 alleles** — line 285 now reads "peptide-allele calls across **6** alleles". Present in the
     patch at `@@ -282,10 +282,10 @@`.
  2. **"four" → "five" below 0.2755** — line 288 now reads "**five** of the ten fall below 0.2755".
     Present in the same hunk.
  3. **Withdrawal of the unreviewed-proteome counts** — the B5 rewrite (127,090 / 12 of 170 / none a
     binder, withdrawn against `junction-proteome-novelty.json` `trembl_included: false`), the §8
     exception, the Declarations amendment and the **new Appendix D** are all present, at lines 870 and
     1596–1606.

The commit also carries the Ethics rewrite and the aixiv-metadata regeneration it describes. Whatever
the working tree held at the moment of the checkout, the sibling's three changes were already committed,
so the checkout restored the file *to* that work rather than discarding it. There is no recovery action
to take on this file. (I did not audit whether some *fourth*, uncommitted edit existed; I can only state
that the three changes named in the report are in committed history and in the tree.)

---

## Recommendation

Do not commit as-is. R1 (one word) and R4 (one cross-reference) are trivial. R2, R3, R8 and R9 are
single-sentence corrections against artifacts I have named and quoted above.

R5, R6 and R7 are not editorial: they mean the manuscript prints headline counts that a committed
artifact in this repository already corrects, while asserting in four places that no such correction
exists. Together with F1 — a committed sibling document asserting that this exact revision was already
applied — that is the thing to settle before anything here is committed or submitted, and it is bigger
than the diff under review.
