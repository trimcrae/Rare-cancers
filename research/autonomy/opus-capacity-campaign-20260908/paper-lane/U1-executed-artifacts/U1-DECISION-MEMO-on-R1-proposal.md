# U1 — independent review of R1's proposed ATR reconstruction

Worker U1, EMC capacity campaign, paper lane. Amendment of 2026-09-08T11:40:04Z (commit `5436eb43`).
Independent of R1's author. Read-only; nothing shared written; no git write; nothing deleted.
Companion deliverable, whose figure evidence feeds item 1: `U1-FIGURE1-PANEL-MAP.md` in this lane.

Reviewed: `PROPOSED-emc-atr-collaborator-package.md`, its `.diff`, and `DECISION-MEMO.md` in
`research/autonomy/opus-capacity-campaign-20260908/paper-lane/R1-executed-artifacts/`.

**Bottom line.** R1's fifteen mechanical corrections are almost entirely well-founded; I found no
arithmetic error in them, and the figure I opened independently corroborates the central one. The
memo's real weaknesses are elsewhere: **two of R1's eight "unresolved" items were resolvable from
committed inputs R1 did not open**, and R1's proposal creates **four cross-reference traps** where a
result would be attributed to a figure that does not show it. R1's own most important structural
judgement — declining to rewrite the predictions table — is correct and should be upheld.

---

## 1 · R1's substantive changes against the named committed inputs

Inputs read: `research/modalities/emc-fet-frame-and-composition.json`,
`research/modalities/tests/test_emc_fet_frame_and_composition.py`,
`research/manuscripts/dependency/emc-atr-collaborator-package-changelog.md`, and
`research/modalities/emc_fet_frame_and_composition.py` (line 355 only). Plus my own pixel reading of
`emc-fusion-frame-fig1.png`.

| # | verdict | committed line or field |
|---|---|---|
| M1 · 176 -> 177 nt spanned (1 EWSR1 + 176 NR4A3 = 174 e2 + 2 e3) | **SUPPORTED** | `type2_seam.nucleotides_spanned_by_the_extra_residues: 177`, `.nr4a3_5utr_nt_retained_total: 176`, `.nr4a3_5utr_nt_from_exon_2: 174`, `.nr4a3_5utr_nt_from_exon_3: 2`, `.ewsr1_nucleotides_donated_across_the_seam: 1`; test lines 37-40 (`span == extra_residues*3`; `nr4a3_5utr_nt_retained_total % 3 != 0`) and 47-49. **Independently corroborated by the figure** (below). |
| M2 · drop "two commonest … bracketing"; type 1 commonest, type 2 a minority; ATF1 as a span | **PARTLY SUPPORTED** | `counted_fusion_type_frequencies.series` and `recruitment_axis_rows.atf1_comparator_span` support the substance. **Precision nit:** R1's "counted once across three counted series" is loose — only **two** of the three series type EWSR1 subtypes at all. Sjögren's committed quotation is *"EWS-TEC (five cases…), TAF2N-TEC (four cases), and TCF12-TEC (one case)"* — it counts partners, not types. R1's other formulation, "commonest **in every series that types its cases**", is exact and should be used in both places. |
| M3 · §3.3 full seam arithmetic, AAG/K265, no stop, ORF 949 aa | **SUPPORTED** | `type2_seam.first_extra_residue_is_a_hybrid_codon` = `{AAG, K, 265}`, `.internal_stop_codon_in_the_extension: false`, `.chimeric_orf_length_aa: 949`, `.nr4a3_moiety_complete: true`; tests 53-59 (incl. `264 + 59 + 626` reconciliation). |
| M4 · "model in general use" -> this programme's own earlier model, ref 3 precedent | **PARTLY SUPPORTED** | Changelog supports the reframing. The "25-residue cryptic-exon extension" attributed to reference 3 is **not** in any of the four named inputs; it rests on the committed §3.1 quotation, which I did not open. Verify before applying. |
| M5 · Table 1 `reported rank` -> `counted frequency` | **PARTLY SUPPORTED** | Types and counts come from `series` quotations (Panagopoulos type 1 = 10, type 5 = 2; Okamoto type 1 = 11, type 2 = 1, TAF15 = 3 of 15 fusion-positive; Sjögren TAF15 4 of 10). **The denominator 15 for Panagopoulos is not in the JSON quotation** — that quotation states "10 tumors" with no denominator. It is supplied by changelog line 96 ("type 1 in 10 of 15 EWS-positive cases"). Cite the changelog, not the artifact, for that denominator. |
| M6 · Table 4 rebuilt; status column split; e7 row and RGG(1) anchor restored; span stated | **SUPPORTED** | `recruitment_axis_rows` carries exactly the needed structure: `source_anchors`, `reported_breakpoints_of_measured_fusions`, `atf1_comparator_span`, `_why_a_span`, `firmly_measured_fractions`; test line 91 pins the span. Changelog line 98 specifies the same substance. |
| M7 · remove "bracket" / "interpolate between points already measured"; "byte-identical" -> "identical in sequence" | **SUPPORTED** | Changelog line 98 names both phrases as superseded. |
| M8 · 14 residues of margin -> 13, convention stated | **SUPPORTED** | `composition.taf15_zero_rg_margin`: `residues_of_headroom_below_the_ceiling: 13`, `distance_to_the_first_rg_position: 14`, `rg_free_ceiling: 174`, `taf15_first_rg_position: 175`, `retained_at_taf15_exon_6: 161`, and `_two_conventions_that_differ_by_one`. R1 states the convention explicitly, which is the whole point of that field. Correct. |
| M9 · Table 5 -> symmetric sweep, 0.439 vs 0.400, margin 0.039, "separates" not "decisive" | **SUPPORTED** | `composition.symmetric_prefix_sweep.lowest_fet_prefix_value: 0.439` (EWSR1), `.tcf12_best_prefix_value: 0.4`, `.gap: 0.039`, `.any_tcf12_prefix_reaches_the_lowest_fet_prefix: false`; test lines 77-86 (`0 < gap < 0.10`, shared grid). The artifact's own `_what` concedes the published test was asymmetric — R1's downgrade of the grade is the honest reading. |
| M10 · §3.5 closing claim restated, overstatement disclosed | **SUPPORTED** | Same field's `_reading`. |
| M11-12 · P1 wording; P3 margin 14 -> 13 | **SUPPORTED** | Changelog; `taf15_zero_rg_margin`. |
| M13 · "the source" -> "reference 1" / "Gracilla and colleagues", 7 occurrences | **SUPPORTED** | Changelog. Mechanical; count not independently verified. |
| M14 · §3.2 gains the frame rule + phase-1 donor set 1,4,7,9,10,12,13,15 | **SUPPORTED** | `frame_rule._the_rule`, `.phase_1_donor_exons`, `.rule_holds_for_every_ewsr1_donor: true`, `.taf15_exon_6.donor_end_phase: 1`; tests 63-70 (equivalence over every donor exon) and 73-74 (`_cross_check_against_committed_audit.disagreements == []`, 27 audit rows). This is the best-evidenced item in the set. |
| M15 · references 9, 10 added carrying only artifact-held fields | **PARTLY SUPPORTED — and see §3, U6** | `series` entries hold `pmid`, `authors`, `title`, `quotation` and nothing else, so R1's restraint is correct **for the artifact**. But the missing fields for **Sjögren** are committed elsewhere in this repository (§3). R1's restraint was right; its "no committed input exists" reasoning was wrong for one of the two. |

### The figure evidence, applied to item 1

From the pixels (full method and quotations in `U1-FIGURE1-PANEL-MAP.md`):

- **M1 is confirmed by a second, independent artefact.** Panel C renders `NR4A3 exon 2, 174 nt,
  untranslated in NR4A3`, `2 nt of exon 3`, `one nucleotide donated by EWSR1`, and
  `59 codons, 177 nt, no internal stop codon`, plus `EWSR1 exon 7, coding through nt 793` and
  `residues 265 to 323 of the chimeric protein, read in the EWSR1 frame`. 1 + 174 + 2 = 177 = 59x3.
  **The figure renders 177; it never prints 176.** R1's 177-vs-176 distinction is exactly right and
  is not a conflict — they are the total insert and the NR4A3-supplied part.
- **M6 and M9's axis numbers are confirmed.** Panel B renders
  `0.000 to 0.267; the breakpoint of the measured construct is not stated`, the two firm anchors at
  0.000 and 1.000, and the one-domain add-back as a hatched full-width band labelled
  `position on this axis not determinable`. Panel A's `EWSR1(1-431), 8 of 30 RG`,
  `EWSR1(1-348), 8 of 30 RG` and `EWSR1(1-472), 11 of 30 RG` reconcile with the triangles at 0.267
  and 0.367.
- **Four of R1's results have no figure support at all** — a coverage mismatch, not a numeric one:
  1. **The frame rule as a rule.** Panel C shows one instance (the type-2 junction). The
     congruent-to-1-mod-3 statement is not rendered.
  2. **The phase-1 donor set** (1, 4, 7, 9, 10, 12, 13, 15). No exon-phase panel exists; no exon
     number from the set appears except 7.
  3. **The symmetric sweep.** Neither `0.439` nor `0.400` nor `0.039` is rendered. **TCF12 does not
     appear anywhere in the figure, in any panel.** Panel B's axis is retained-RG fraction, a
     different quantity.
  4. **The 13-residue TAF15 margin.** Panel A renders `TAF15(1-161), 0 of 31 RG` but not 174, 175
     or 13, and draws no headroom bracket.

  **Consequence for integration: any sentence citing Figure 1 for those four is unsupported.** This
  is the concrete trap R1 could not see, having not opened the images.

---

## 2 · R1's seven decisions

| # | R1's recommendation | my verdict | why |
|---|---|---|---|
| **D1 · Retitle** | yes | **SOUND in direction, PREMATURE as an act** | Changelog lines 148-160 register both former titles as superseded and say the replacement "names the result rather than the proposal" — but **never state the string**. I confirmed this directly. Also creates a dependency R1 correctly names: `systems/views/L3-publications.md` and `emc-atr-vulnerability-assessment.md` quote title 2 and go stale; the changelog names the fix (`systems_check.py --write-views`). Retitle only together with that regeneration, and only once a human supplies the string. |
| **D2 · Delete Appendix A** | yes | **SOUND, conditional on one check** | The basis — the changelog's own header saying it *is* the former Appendix A and "Nothing was dropped in the move" — is a self-report by the destination document. Cheap to verify by diffing the appendix against the changelog before deleting. Not a reason to defer, but do the check; deletion is irreversible in the reader's copy. |
| **D3 · Insert Figure 1, cut to six tables** | yes in principle; not done | **SOUND, and now unblocked** | Changelog line 107 specifies exactly this: "One three-panel figure and six main-text tables, with the gene-model table and the wild-type-control table moved to supplementary material". The figure is three panels, as specified. A caption and panel map are supplied in `U1-FIGURE1-PANEL-MAP.md`. **Two constraints:** (a) the four cross-references in §1 above must not be made; (b) Panel A's dashed boxes and internal ticks are **unlabelled and the figure has no key**, so the caption must state what they are or a key must be added — I will not assert RGG-domain boundaries the figure does not print. |
| **D4 · Reduce P1-P5 to three** | yes; explicitly not applied | **R1's restraint is CORRECT and should be upheld; the application is PREMATURE** | The table is preregistration-shaped and `CLAUDE.md` §1 preserves preregistrations. R1's *criticism* is sound and worth recording — P4's falsifier as written duplicates P2's, and P1 as an equivalence cannot be falsified by a null. But that is grounds for an **amendment record**, not a silent replacement. The dependency R1 names is real and I confirmed it: `rgg_dose_calibration_and_predictions.registered_predictions` exists at `research/modalities/emc-fet-construct-designs.json:1621` and must move with any change. Decision belongs to a human, with `research/autonomy/amendments.jsonl` describing the tradeoff. |
| **D5 · Move the scope blockquote into Limitations** | yes, unchanged wording | **SOUND — lowest risk in the set** | Position-only change, every sentence retained. Safe to apply with the mechanical tier. |
| **D6 · Renumber into a Discussion** | defer until D3/D4 settle | **SOUND — the deferral is the right call** | The changelog cites §4.1-§4.4 and §2.3, section numbers that do not exist in the committed manuscript. Applying cross-references before the structure exists produces dangling pointers. Agree without reservation. |
| **D7 · Add §2.3 and §4.1 (+ Table S3)** | yes as content; not drafted | **SOUND as content, PREMATURE as application** | Undrafted, and §2.3 carries a committed constraint R1 correctly surfaced: changelog line 106 records a **⛔ "Declined as written"** — `junction-aso-designs-e7n3.json` is *not* an independent RefSeq cross-check of the 2-nt figure, because its `_transcript_source` is `committed_cache` for both genes, i.e. the same Ensembl cache. §2.3 must therefore state the absence of an independent annotation source as a limitation, not claim a cross-check. Any drafting that forgets this reintroduces the exact error the changelog declined. |

---

## 3 · R1's eight unresolved items — genuinely unresolvable, or a missed input?

| # | R1's claim | verdict |
|---|---|---|
| **U1 · the new title** | no input exists | **GENUINELY UNRESOLVABLE.** Confirmed at changelog 148-160: the replacement title is referred to but never written. Requires the author. |
| **U2 · Figure 1 caption and panels** | needs a reading of the PNG | **RESOLVED — R1 MISSED AN AVAILABLE INPUT.** The input was committed and readable the whole time; R1's own memo §1 says "Their panel content was not opened or read in this lane". Delivered in `U1-FIGURE1-PANEL-MAP.md`, together with four unsupported cross-references only a pixel reading could expose. |
| **U3 · §4.1 procedure + Supplementary Table S3** | prose missing; artifact "exists but the table was not built in this lane" | **SPLIT — PARTLY RESOLVABLE.** The prose is genuinely unresolvable. But **Table S3 is a data-assembly task against a committed input**, `research/modalities/emc-fet-construct-designs.json` (73,415 B, committed) — R1 states this itself and declines on **scope**, not on evidence. Reclassify: not "missing input", but "in-scope work not done". Buildable by whoever the coordinator tasks, without network. |
| **U4 · §2.3 exon-numbering correspondence** | prose missing | **GENUINELY UNRESOLVABLE as prose.** But note the *constraint* is committed (changelog 106, above), so a drafter is not starting blind. |
| **U5 · the ORCID** | cannot be invented | **GENUINELY UNRESOLVABLE.** Correct, and correctly refused. Requires the author. |
| **U6 · bibliographic fields for refs 9 and 10** | "Missing input: a retrieval record for PMID 11679947 and PMID 12598313" | **SPLIT — R1 MISSED AN AVAILABLE INPUT for one of the two.** **Sjögren 2003 (PMID 12598313) is fully recorded in committed repository files:** `research/autonomy/hardening-state/PUB-FUSION-PARTNER.json` line 88 carries *"PMID 12598313, PMC1868116, doi 10.1016/S0002-9440(10)63875-8 - verified real: Am J Pathol 2003;162(3):781-92"*, and the same fields appear in `research/autonomy/review-seats/PUB-FUSION-PARTNER-…-seat-citations-and-instruments.json` and `research/literature/tcf12-nr4a3-breakpoint-primary-sources.json`. Journal, year, volume and pages are therefore available **without network**. **Okamoto 2001 (PMID 11679947) remains unresolved:** the PMID appears in `research/literature/lane-probe-metabolism-strategy.json`, `research/modalities/hemcss-label-priorart.json`, `nr4a3-nuccore-sweep-inputs.json` and `emc_fet_frame_and_composition.py:355`, but I found **no committed record carrying its journal, volume or pages**. Reference 10 can be completed; reference 9 must stay marked. ⚠ Whoever applies this must confirm the Sjögren fields are the same paper the artifact's `series` entry quotes (same PMID, same author list, same 5/4/1 counts — they match on my reading) before writing them. |
| **U7 · the cover letter** | outside this contract's file | **NOT AN EVIDENCE GAP — a scope boundary.** Resolvable by widening scope to that file. The two corrections it needs (the rank claim and the 176-nt sentence) are already settled by M1 and M2/M5. Should be scheduled, not listed as unknown. |
| **U8 · the later-same-day block corrects uncommitted text** | first-revision draft missing | **GENUINELY UNRESOLVABLE within bounds** (source recovery is barred). R1's framing — **the ATR package has two missing revision passes, not one, and the second cannot be reached without the first** — is the most consequential finding in its memo and I endorse it. Only end states are known for four of five rows in that block, so those cannot be applied as find-and-replace. |

**Score: of eight, one fully resolved (U2), two partly resolvable (U3 data half, U6 Sjögren half),
one misclassified as unknown when it is a scope item (U7), four genuinely unresolvable (U1, U4, U5,
U8).**

---

## 4 · Unsupported claims, dependencies, and a recommended coherent scope

### Concrete unsupported claims to fix before or during integration

1. **Any cross-reference from the frame rule, the phase-1 donor set, the symmetric sweep
   (0.439/0.400/0.039), or the 13-residue TAF15 margin to Figure 1.** The figure shows none of them
   (§1). This is the highest-value catch in this review.
2. **"Type 2 … counted once across three counted series"** (M2). Only two of the three series type
   EWSR1 subtypes. Use "commonest in every series that types its cases" and say plainly that Sjögren
   counts partners, not types.
3. **The Panagopoulos denominator "10 of 15"** (M5) is sourced from the changelog, not from the
   artifact quotation, which gives no denominator. Attribute it correctly.
4. **Reference 3's "25-residue cryptic-exon extension"** (M4) is unverified against the four named
   inputs. Check the committed §3.1 quotation before it goes in.
5. **Reference 9 (Okamoto)** must remain explicitly marked incomplete. **Reference 10 (Sjögren) must
   stop being marked incomplete** — the fields exist (§3, U6).
6. **Anything describing `PROPOSED-emc-atr-collaborator-package.md` as the recovered 2026-08-10
   revision.** R1 says this itself, unusually clearly, in its §0; it must survive into whatever the
   coordinator writes. It is a reconstruction, not a recovery.

### Remaining dependencies

- `systems/views/L3-publications.md` and `research/manuscripts/dependency/emc-atr-vulnerability-assessment.md`
  quote the superseded title; the changelog names `python3 systems/systems_check.py --write-views` as
  the regeneration step. Binds to D1.
- `emc-fet-construct-designs.json:1621` `registered_predictions` must move with any change to P1-P5.
  Binds to D4.
- The cover letter (U7) inherits M1 and M2/M5 and is currently unscheduled.
- D6 depends on D3 and D4; D7's §2.3 depends on the changelog-106 constraint.
- U8 blocks the whole later-same-day block regardless of anything above.

### RECOMMENDED COHERENT SCOPE — a recommendation, not an application

**Tier 1 — apply together now.** Evidence-settled, no structural dependency, each traceable to a
committed field or the changelog: **M1, M3, M6, M7, M8, M9, M10, M11-12, M13, M14**, plus **M2 and
M5 with the two attribution fixes above**, plus **D5** (move the scope blockquote). This tier is
internally coherent: it corrects numbers and register without touching structure, and every item
survives independent checking. It is also the tier the committed test file already pins.

**Tier 2 — apply with Tier 1 only if the coordinator accepts a caption.** **D3** (insert Figure 1,
move the gene-model and wild-type-control tables to supplementary), using the caption and panel map
in `U1-FIGURE1-PANEL-MAP.md`, **and only with the four unsupported cross-references withheld** and a
decision taken on labelling Panel A's dashed boxes. Also in this tier: **M15/U6 completing reference
10 from the committed Sjögren record** while reference 9 stays marked. **D2** may join Tier 2 after
the one-line appendix/changelog diff check.

**Tier 3 — must wait, and why.** **D1** (no title string exists, and it drags two stale views);
**D4** (preregistration — needs a human decision and an `amendments.jsonl` entry, not an edit);
**D6** (dangling pointers until D3 and D4 settle); **D7** (undrafted, and §2.3 carries a declined
cross-check that must not be reintroduced); **U3's prose half**; **U5** (author); **U7** (schedule as
a scope extension, not an unknown); **U8** (blocked by a missing first revision, and source recovery
is barred).

**One task worth commissioning separately:** build Supplementary Table S3 from the committed
`emc-fet-construct-designs.json`. It is bounded, needs no network, and converts half of U3 from
"unresolved" into "done".

---

## 5 · What I did NOT do, and what remains UNKNOWN

Not done: no figure regenerated, no science rerun, no gate rerun, no `scripts/preflight.sh`, no
network, no source recovery, no history hunt, no census, no whole-paper review, no publication
clearance, no shared manuscript/artifact/registry/reference-list edit, no git write, no deletion, no
held-scope continuation. I did **not** apply anything — this is a recommendation. I did not re-read
any image already read. No content-policy refusal occurred.

UNKNOWN: whether M13's "7 occurrences" is the true count (not verified); whether reference 3 states a
25-residue extension (M4); whether Appendix A's content is genuinely duplicated in the changelog
(D2); whether the committed §3.1/§4 prose already contains the four Figure 1 cross-reference traps —
**a targeted grep of the manuscript for "Figure 1" is the single cheapest next check** and I did not
run it; Okamoto 2001's journal/volume/pages; the new title; the ORCID; the first-revision draft.

No EMC efficacy, safety, selectivity or clinical-readiness claim is made or implied. Every EMC
position discussed is computed, not measured. There is no wet lab.
