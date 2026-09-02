---
id: DOC-EMC-ATR-COLLABORATOR-PACKAGE-CHANGELOG
title: "Changelog and superseded-value register for the EMC NR4A3 fusion reading-frame manuscript"
level: L3
kind: register
status: live
canonical_for:
  - every superseded value, framing and title the EMC NR4A3 fusion reading-frame manuscript has corrected
purpose: >-
  Hold the superseded-value register for emc-atr-collaborator-package.md, so a corrected number stays
  quotable and findable without the bookkeeping travelling to a journal editor inside the submission
  file.
scope: >-
  Version history and corrections for one manuscript and its cover letter. It reports no new result
  and asserts nothing about any disease or agent.
audience: [maintainers, external reviewers]
related: [DOC-EMC-ATR-COLLABORATOR-PACKAGE]
date: 2026-08-10
last_verified: 2026-08-10
---

# Changelog and superseded-value register

**What this is.** Per [CLAUDE.md](../../../CLAUDE.md) rule 1.2 a corrected value is registered rather
than dropped, and the live text carries only the current value. This file is the register for
[`emc-atr-collaborator-package.md`](./emc-atr-collaborator-package.md) and its cover letter.

**Why it is not an appendix of the manuscript.** It stood as Appendix A of the manuscript until
2026-08-10, where it was roughly forty per cent of the main-text length, named this repository's own
house-rules file four times, cited this repository's own style linter as a result, and would have
gone to a journal editor inside the submission file. Nothing was dropped in the move. The manuscript
points here from its data-and-code section.

---

## 2026-08-10, later the same day — the construct-building procedure, and a present-tense sweep

Two things were done in one pass. **A numbered procedure was added** to §4.1, with
**Supplementary Table S3** carrying the per-junction assembly coordinates: the manuscript had
established that a construct spliced from coding sequences is wrong and had stated the remedy in a
single clause ("decidable by sequencing the patient junction and translating the transcript rather
than the coding sequences"), which is correct and unusable. **And every present-tense claim about
what other laboratories do was re-read**, after the same defect had been found and removed from this
file earlier the same day. Three sentences overstated and are registered below.

⭐ **The sweep also found the opposite of what it went looking for, and it is the stronger finding.**
The premise under test was that no published EMC fusion construct exists, which would have made the
59-residue result a correction nobody had yet earned. That premise is FALSE in this repository's own
committed record: [`emc-fet-construct-designs.json`](../../modalities/emc-fet-construct-designs.json)
labels reference 3 (PMID 31020999 / PMC6766969) as **"an EXPRESSED construct with this
architecture"** for two of the four junctions, quoting *"E-N, corresponding to EWSR1 (exons
1-12)-NR4A3 (exons 3-8)"* and *"T-N\*, corresponding to the commonest TAF15 (exons 1-6)-NR4A3 (exons
3-8) fusion"*, and records that the same source compares T-N and T-N\* for colony formation;
[`emc-ret-cistrome.json`](../../modalities/emc-ret-cistrome.json) records the same source measuring
NBRE binding **"RETAINED by the EWSR1-NR4A3 chimera and IMPAIRED by TAF15-NR4A3"**. Both named
constructs use the **exon 3** acceptor, where the difference this paper reports is one residue, and
no source retrieved reports a construct at the **exon 2** acceptor. §4.1 now says exactly that, which
is a better sentence than an implication that the error is widespread.

| superseded | current | where it lived | why it changed |
|---|---|---|---|
| **"The practical consequence of section 3.3 falls on anyone building an EMC fusion construct."** | **"falls on a construct assembled at the exon 2 acceptor"**, with the one-residue case at the exon 3 acceptor named in the same paragraph; §4.1 | §4.1 ¶1 of the manuscript before this revision | The 59-residue insertion belongs to the exon 2 acceptor, which one of the four reported junctions uses, and that one is counted **once across three series** (§3.1). As written the sentence put a minority-variant consequence on every EMC construct |
| **"two different proteins are being called the same fusion"** | **"the same junction name would then denote two different proteins"** | §4.1 ¶1 of the manuscript before this revision | A present progressive asserting an ongoing practice. No source retrieved establishes that any laboratory has built a type-2 construct, and the two sources that DO report expressed EMC fusion constructs both use the exon 3 acceptor |
| **"fast-recruitment anchor, already held by any laboratory running the assay"** | **"fast-recruitment anchor; reference 1 measured native EWSR1 in the same assay"**; Supplementary Table S2 | the GFP-EWSR1 row of Supplementary Table S2 before this revision | A present-tense claim about other laboratories' reagent stocks, the same defect corrected in §4.3 earlier the same day. What reference 1 supports is that it measured native EWSR1, which Table 5 already records |
| **"in whichever orientation the recipient laboratory's existing EWSR1-FLI1 construct uses"** | **"in whichever orientation the EWSR1-FLI1 comparator of section 4.3 is built in"**; supplementary tag-orientation note | the tag-orientation paragraph before this revision | Presupposes that the recipient laboratory already holds an EWSR1-FLI1 construct. §4.3 requires that comparator to be run in the same session regardless, so the orientation rule does not need the presupposition |
| **"The insertion belongs to the acceptor, so any fusion using NR4A3 exon 2 carries it, and a construct built from a protein-level model does not."** | **"The insertion belongs to the acceptor: among the four reported junctions only the minority type 2 uses it, and the other three gain one hybrid residue. A procedure for assembling and verifying either construct is given."**; Abstract | Abstract of the manuscript before this revision | The Abstract stated the insertion's scope in terms of the acceptor and never said how many reported junctions use that acceptor, so a reader skimming it could carry away a 59-residue insertion in the commonest EMC fusion. ⚠ Paid for inside the 250-word limit by six words trimmed elsewhere in the same paragraph; measured at **247 words** by [`submission_metrics.py`](../submission_metrics.py) |

**Additions rather than corrections.** §4.1's six-step procedure (establish the junction, assemble
the transcript, translate once from the 5' partner's initiator, predict from the donor phase, verify
against the expected open reading frame, and grade a junction absent from Table 3);
**Supplementary Table S3**, holding the cut coordinates, assembled cDNA length and open reading
frame for each reported junction, from
[`emc-fet-construct-designs.json`](../../modalities/emc-fet-construct-designs.json); a **5' untranslated
length** column in Supplementary Table S1, from
[`emc-construct-inputs.json`](../../modalities/emc-construct-inputs.json), which is where the
procedure's initiator positions (EWSR1 cDNA nucleotide 70, TAF15 87) come from; the **complete
phase-1 donor set** across all seventeen EWSR1 coding exons (1, 4, 7, 9, 10, 12, 13, 15), from
`frame_rule.phase_1_donor_exons` in
[`emc-fet-frame-and-composition.json`](../../modalities/emc-fet-frame-and-composition.json), which the
manuscript previously gave only over exons 6 to 14; and one scope clause each in §3.3 and the
Figure 1 caption naming type 2 as the only reported junction at the exon 2 acceptor.

⛔ **Two inputs the procedure needs are named as absent rather than filled**, and §4.1 says so: the
cryptic exon of reference 3's rarer TAF15::NR4A3 isoform has no sequence in any source retrieved,
and neither FUS::NR4A3 nor TCF12::NR4A3 has a transcript-level breakpoint statement to build from.

---

## 2026-08-10 — revision in response to a simulated internal review

Review: [`emc-atr-collaborator-package-peer-review-2026-08-10.md`](./emc-atr-collaborator-package-peer-review-2026-08-10.md).
Point-by-point response: [`emc-atr-collaborator-package-review-response-2026-08-10.md`](./emc-atr-collaborator-package-review-response-2026-08-10.md).

| superseded | current | where it lived | why it changed |
|---|---|---|---|
| **"Retained EWSR1 RG dipeptide counts place the two commonest EMC fusions at 0 of 30 and 8 of 30, bracketing the two fusions in which the mechanism has been measured."** With it, Table 1's `reported rank` of **"second"** for EWSR1::NR4A3 type 2, and P4's basis in the type-1 and type-2 pair | Type 1 is the commonest reported type in every series that types its cases; **type 2 is a minority variant, counted once across three series**, and **TAF15::NR4A3 is the more frequently counted zero-RG EMC fusion**; §3.1, Table 1, §4.2 | Abstract sentence 6, Table 1, §3.4 ¶2 and P4 of the manuscript before this revision, and ¶3 of the cover letter | Neither source cited for the rank makes a frequency claim: reference 4's quotation is a definition of the two types and reference 6's is an RT-PCR primer design. The rank appears to have been inferred from the type NUMBER. Three counted series held in [`lit-targets-aso-verify.json`](../aso/lit-targets-aso-verify.json) say otherwise — Panagopoulos type 1 in 10 of 15 EWS-positive cases with type 5 named second commonest and type 2 not among the counted types [7], Okamoto type 1 in 11, type 2 in 1 and TAF15 in 3 of 15 fusion-positive cases [9], Sjögren EWSR1 in 5, TAF15 in 4 and TCF12 in 1 of 10 [10] — as does the genomic mapping, 2 of 14 breakpoints in NR4A3 intron 1 and 1 of 14 in EWSR1 intron 7 [7]. ⚠ The RG arithmetic is unchanged: 0 of 30 for a 264-residue cut and 8 of 30 for a 431-residue cut are both still correct |
| **"carries 176 nucleotides of NR4A3 5' untranslated sequence in the EWSR1 reading frame, encoding 59 residues"**, and **"The named 3' exon of the type-2 junction, NR4A3 exon 2, is entirely non-coding, so the fusion mRNA carries 176 nucleotides"** | The 59 residues span **177 nt: 1 donated by EWSR1 across the seam and 176 supplied by NR4A3**, of which **174 come from exon 2 and 2 from exon 3**; §3.3, Figure 1C | Abstract sentence 5, §3.3 sentences 1 and 2, Table 3's note and Appendix A row 2 of the manuscript before this revision, and ¶3 of the cover letter | 176 is not a multiple of three. EWSR1 coding sequence runs through exon 7 to nucleotide 793, which is 264 complete codons and one base over, and that base completes the first codon of the extension. ⚠ Every computed value is unchanged and was re-verified: the segment carries no stop codon, the first residue is the hybrid codon AAG encoding lysine at position 265, the remaining 58 are NR4A3 sequence in a non-native frame, and the open reading frame is 949 aa. Pinned by `tests/test_emc_fet_frame_and_composition.py::test_the_extension_spans_a_whole_number_of_codons` |
| **Table 4's `status` column marking EWSR1::ATF1 at EWSR1 exon 8 and at exon 10 both as "measured"**, with the EWSR1::ATF1 exon 7 row and the EWSR1-RGG(1)-FLI1 anchor absent from the table, and the claims that EMC's two main types **"bracket"** the measured fusions and that both **"interpolate between points already measured"** | A status column separating **"measured in reference 1"** from **"a reported breakpoint of a disease in which the mechanism was measured"**; both dropped rows restored; the ATF1 comparator stated as a **span from 0.000 to 0.267**; the firmly measured positions stated as **0.000 and 1.000**; Table 5, §4.2, Figure 1B | Table 4, §3.4 ¶2-3 and P2 of the manuscript before this revision | Reference 1 built one EWSR1-ATF1 construct, so at most one of the two rows could describe it, and the retrieved text does not state its breakpoint. [`emc_fet_idr_census.py`](../../modalities/emc_fet_idr_census.py) says so in a field a reader can check, writing its control rule as "any type", not "all types", "because a fusion's breakpoint varies between patients and this repo has no exon audit fixing which type the source's constructs used". The RGG(1) anchor's retained RG count is `null` in the artifact because the source does not identify which domain it restored. ⚠ Restoring the exon 7 row is not purely damaging: an ATF1 breakpoint at 0 of 30 in a disease where the phenotype was observed is a second measured-disease point at zero |
| **Five predictions P1 to P5**, with **P1 stated as an equivalence** ("kinetics indistinguishable from EWSR1-FLI1"), **P3's falsifier omitting no-accumulation**, **P2 bundling a proximity claim** to the commonest clear-cell type, and **P4** as a prediction in its own right | **Three predictions.** P1 is a rank prediction over both zero-RG EMC fusions; P2 is the type-1 against type-2 comparison, with the old P4 folded in as a corollary and the proximity claim moved to the explicit non-predictions; P3 is the TCF12 arm and states where it is made that no chimeric construct is supplied; Table 6, §4.3 | §4 and Table 6 of the manuscript before this revision | P4's falsifier was P2's falsifier, so the set counted one experiment twice. An equivalence claim cannot be falsified by a null result and is satisfied by an underpowered experiment, and no equivalence margin can be quoted from an ordinal axis. At cuts of 348 and 431 residues the retained RG set is the same eight dipeptides at positions 300 to 330, so the axis cannot distinguish type 1 from the ATF1 exon 10 breakpoint even in principle |
| **Table 5's sweep row graded "decisive"** on TCF12's best prefix value of 0.400 against the FET proteins at a single fixed 250-residue window | The **symmetric sweep**: all four proteins on the same grid gives a lowest FET prefix value of **0.439** (EWSR1, residues 1-560) against TCF12's best of 0.400, a margin of **0.039**; the row is graded as separating rather than decisive, and the fixed-window row keeps its grade; Table 4 | Table 5 row 2 of the manuscript before this revision | The published comparison gave TCF12 every prefix and the FET proteins one window, which is asymmetric and overstates the separation. ⚠ The conclusion survives: no TCF12 prefix of any length reaches the lowest value any FET prefix takes. One home for the arithmetic: [`emc-fet-frame-and-composition.json`](../../modalities/emc-fet-frame-and-composition.json) → `composition.symmetric_prefix_sweep` |
| **"the strict zero-RG window with 14 residues of margin"** for TAF15 exon 6 | **13 residues of margin**, the number of further residues that could be retained without touching an RG dipeptide, with the convention stated in §2.2; §4.2 and P1 | §3.4 and P3 of the manuscript before this revision | The census computes margin as the RG-free ceiling (174) minus the retained length (161). Fourteen is the distance to the first RG position at 175; thirteen is the headroom. Both are defensible and the artifact uses the second, so the manuscript now uses the second |
| **"byte-identical over the shared prefix"** | **"identical in sequence"**; §4.2 | §3.4 ¶2 of the manuscript before this revision | Repository register in a submission text |
| **"the source"** used as a noun for reference 1, and **"this programme"** | **"reference 1"** or **"Gracilla and colleagues"**, and **"the present analysis"** | throughout the manuscript before this revision | Internal shorthand in a submission text |
| **The four in-frame junctions reported as four checked examples** | **One rule**: a junction is in frame if and only if the donor exon ends one nucleotide into a codon, both NR4A3 acceptors giving the same register because exon 2 is 174 nt; §3.2, Table 2 | §3.2's closing paragraph of the manuscript before this revision | Not a correction: an addition. The rule was already computed across 27 donor and acceptor pairs in [`junction-mrna-frame-audit.json`](../../modalities/junction-mrna-frame-audit.json), which the manuscript did not cite |
| **"the protein-level model in general use"**, unsourced | A statement of what is actually documented, which is this programme's own earlier model, plus reference 3's 25-residue cryptic-exon extension as precedent for the mechanism; §3.3 | §3.3 and the Abstract of the manuscript before this revision | No source was ever cited for what the field's protein model is. The honest scope of the novelty is the specific junction and its sequence, not the possibility of an N-terminal addition, which reference 3 already describes in the same gene |
| **The exon-numbering correspondence left unstated**, with limitation 3 covering only "a tumour may use a different transcript" | §2.3, establishing the correspondence from reference 7's genomic mapping and reference 3's cryptic exon, with limitation 3 widened to name the missing second annotation source | §2.1 and §6 item 3 of the manuscript before this revision | Everything in the manuscript depends on the literature's NR4A3 exon 2 and exon 3 being transcript exon ranks 2 and 3, and limitation 2 already discloses that this programme was once bitten by an exon-indexing error of the same family. ⛔ **Declined as written:** the review offered [`junction-aso-designs-e7n3.json`](../../modalities/junction-aso-designs-e7n3.json) as a RefSeq-derived independent cross-check of the 2-nucleotide figure. It is not one. That artifact's `_breakpoint_model` names the RefSeq mRNAs `NM_005243` and `NM_006981` as a label inherited from its module's default mode, but its `mode` is `real_exon_junction_mRNA` and its `_transcript_source` records `committed_cache` for both genes — the same Ensembl cache. It is cited for what it is, a second code path reaching the same seam, and the absence of an independent annotation check is now a stated limitation |
| **Seven tables and no figure**, with the 59-residue result carrying no display item | **One three-panel figure and six main-text tables**, with the gene-model table and the wild-type-control table moved to supplementary material; Figure 1 | the manuscript before this revision | Seven tables and no figure is the wrong display mix for a paper about protein architecture, and it is a large part of why the novel result read as buried |
| **Appendix A, the superseded-value register, inside the manuscript** | This file | the manuscript before this revision | See the header above |
| **The "Scope of the claims" blockquote standing above the Abstract** | The opening paragraph of §4.4, Limitations, with every sentence intact | the manuscript before this revision | The content is correct and none of it was lost. In its former position, prose pre-emptively declaring its own restraint reads as advocacy; in Limitations the same sentences read as rigour |

**Declined, with reasons.**

1. **Cite the primary pazopanib trial report alongside or instead of the 2025 review.** No committed
   retrieval record in this repository holds a primary trial report for NCT02066285, and writing a
   citation from recollection is the exact failure mode
   [`lint_citations.py`](../lint_citations.py) exists for. The review citation is retained and the
   trial registration is named in the running text, so a reader can reach the primary report.
2. **Give the full versioned transcript and translation accessions and the Ensembl release and
   genome assembly.** The unversioned accessions are now given for all five genes, and the retrieval
   date and endpoint are stated. The cache records neither a release number nor an assembly and the
   identifiers it returned carry no version suffix, so supplying either would be invention. The gap
   is stated in §2.1 as the review permits.
3. **Regenerate the construct artifact and the census so they cite the published version of
   reference 1.** Not done in this revision: the artifacts were produced by a workflow run whose
   inputs are pinned, and regenerating them to change a citation string would replace a dated
   measurement with an undated one. The three known artifact-to-manuscript disagreements are instead
   recorded in the manuscript's data-and-code section, dated, with the statement that each concerns
   provenance and none concerns a computed value.

---

## 2026-08-09 and earlier

Carried forward from the manuscript's former Appendix A without alteration.

| superseded | current | where it lived | why it changed |
|---|---|---|---|
| **"EMC's canonical fusion is EWSR1 exon 7 :: NR4A3 exon 3, i.e. `EWSR1(1–264)`."** Used by [`emc_fet_idr_census.py`](../../modalities/emc_fet_idr_census.py) (`emc_canonical_EWSR1_NR4A3`), by [`emc-post-degrader-options.md`](../program/emc-post-degrader-options.md) route 1, and by [`target-route-options.md` §1.3](../program/target-route-options.md) | The primary literature reports **EWSR1 e12 :: NR4A3 e3 (type 1, commonest)** and **EWSR1 e7 :: NR4A3 e2 (type 2)** | those three files, and §2.2 of the manuscript before its 2026-08-09 revision | Superseded 2026-08-03. The combination "e7 :: e3" pairs the 5′ side of one reported type with the 3′ side of another and is not itself a reported type. ⚠ The census row remains **valid arithmetic for a 264-residue EWSR1 cut** and remains the right comparator for EWSR1::FLI1 type 1 — what changed is the label "canonical", which now belongs to the exon-12 cut. Retained here because the old figure (`0 of 30 RG`) is quoted in live text elsewhere |
| **The type-2 fusion protein modelled as `EWSR1(1–264)::NR4A3(1–626)`** — [`fusion_cofold.py`](../../modalities/fusion_cofold.py)'s `EWS_CUT = 264` with *"NR4A3 resumed at res 2"* | `EWSR1(1–264) :: [59 UTR-encoded residues] :: NR4A3(1–626)` | `fusion_cofold.py`, and any construct built from the protein-level model | The named 3′ exon of the type-2 junction is entirely non-coding, so 176 nt of NR4A3 5′-UTR sit downstream of the EWSR1 cut and, with the base EWSR1 donates across the seam, encode 59 residues with no intervening stop. ⚠ A computed consequence of the canonical transcripts for the reported junction, not an observed protein |
| **"NR4A3 exon 3"** as resolved by a coding-exon offset table indexed with transcript exon numbers, which returned transcript exon 5 | Transcript-level exon numbering throughout, with four gene-model assertions and three per-construct self-checks | a committed artifact, corrected at [`target-route-options.md` §1.3](../program/target-route-options.md) | The off-by-two deleted NR4A3's AF-1 domain and the first zinc finger of its C4 DNA-binding domain from all seven emitted junctions, modelling a chimera that could not do what the real fusion is reported to do. ✅ **NOT superseded by anything since:** both reported EMC types retain NR4A3 from its own first coding exon, so AF-1, the C4 zinc finger and the LBD are present under either type |
| **"One home for the machine-readable versions: `rgg_dose_calibration_and_predictions.registered_predictions`",** applied to all five predictions P1–P5 | The pointer names both fields, `registered_predictions` and `tcf12_negative_control.registered_prediction` | §3.3 of the manuscript before its 2026-08-09 revision | The pointer was wrong for the one prediction that can falsify the hypothesis, so a reader following it would have found nothing |
| **"Three independent tests"** heading a list of **four** items in the TCF12 section | Three tests plus one breakpoint-independent sweep, with the table rows labelled by test number | §4.1 of the manuscript before its 2026-08-09 revision | The artifact's own verdict field describes three tests with the FET-vs-FET pairs as the positive control for the third, and records the prefix sweep separately as `test_4_breakpoint_independent_sweep`. The count in the prose disagreed with the count in the list beneath it |
| **The document's framing as an unpublished collaborator package** — *"What this is: everything a group that already runs the FET-fusion DSB-recruitment assay would otherwise have to derive… What it is not: a request to be convinced by an argument"* | A computational research article for *Genes, Chromosomes and Cancer* with the preprint on bioRxiv | the whole document before its 2026-08-09 revision | An ask reaches a laboratory only through the published record (CLAUDE.md §5), and the computed results carry a paper on their own. ⚠ **Registered Report Stage 1 was the closer fit on FORMAT and was rejected on ELIGIBILITY:** in-principle acceptance is a commitment that the submitting authors then run the approved protocol, and this programme has no laboratory, no affiliation and no engaged collaborator |
| **The repository-register presentation** — glyph-led warning blocks, bold on load-bearing clauses, sentence-shaped headings, running commentary on the document's own honesty (183 bold runs at 42.4/1000 words and 65 em-dashes at 15.1/1000) | Journal register: 0 findings from [`lint_style.py`](../lint_style.py) | the whole document before its 2026-08-09 revision | That register is correct in a repository document, where the reader is a maintainer being stopped from repeating a specific mistake, and wrong in a submission text, where prose asserting its own honesty reads as advocacy (CLAUDE.md §7, gate 5). No claim, figure or caveat was dropped in the conversion |
| **Reference 7 cited as the conference abstract `PMC2395470`,** with no author list and a title of only "Biology" | Panagopoulos I, Mertens F, Isaksson M, Domanski HA, Brosjö O, Heim S, et al. *Genes Chromosomes Cancer* 2002;35(4):340-352. PMID 12378528 | the reference list before the 2026-08-09 revision | Reading the full text showed why the record was empty: `PMC2395470` is the whole CTOS 2001 abstract supplement (Sarcoma 2001;5(Suppl 1):S37-43), and "Biology" is one of its section headings, so the record describes a supplement rather than an article. The counted series comes from abstract 035 within it, by Panagopoulos and colleagues, subsequently published in full with the same 18 cases and the same counts verbatim. The peer-reviewed paper is the correct source when it exists and reports the same data. ⚠ The counts themselves are unchanged and are the ones quoted in §3.1 of the manuscript |
| **Reference 1 cited as a bioRxiv preprint** — *"FET fusion oncoproteins disrupt physiologic DNA repair and create a targetable opportunity for ATR inhibitor therapy. bioRxiv 2023. PMID 37205599. doi 10.1101/2023.04.30.538578"* | The peer-reviewed version: Gracilla DE, Menon S, Breese MR, Lin YP, Dela Cruz FS, Feinberg TY, et al. *Cancer Research* 2026;86:2660-2677. PMID 41811428. PMC13223543. doi 10.1158/0008-5472.can-25-2166 | the reference list, and §1 where the source was introduced as "a recent report" | A DOI-keyed retrieval on 2026-08-09 returned the published version ([`citation-corrections-2026-08-09.json`](../../literature/citation-corrections-2026-08-09.json)). The first-author order differs between the two versions, Menon S on the preprint and Gracilla DE on the published paper, so the author string above is the published one. ⚠ **Nothing measured changes and the transfer argument is unchanged.** The apparent disagreement between two committed artifacts about the preprint's identifier was adjudicated the same day and both were reporting correctly for their own dates: on 2026-08-07 the query `EXT_ID:37205599 AND SRC:MED` returned `hitCount: 1` for that preprint under PMID 37205599 and PMC10187251, recorded verbatim in [`atr-hrd-sarcoma-series-inputs.json`](../../modalities/atr-hrd-sarcoma-series-inputs.json); on 2026-08-09 the identical query returned nothing while the same query form resolved a control identifier normally. Nothing in the citing prose was fabricated, and no claim that this identifier names nothing may be repeated |

**Superseded document titles.**

1. *"The EMC arm, pre-built — a collaborator package for the FET / ATM / ATR laser-microirradiation
   assay"*, carried until 2026-08-09.
2. *"Transcript-level models of the NR4A3 fusions of extraskeletal myxoid chondrosarcoma, and five
   pre-specified predictions for a DNA double-strand break recruitment assay"*, carried from
   2026-08-09 until 2026-08-10, and quoted as this endpoint's title in
   [`systems/views/L3-publications.md`](../../../systems/views/L3-publications.md) and in
   [`emc-atr-vulnerability-assessment.md`](./emc-atr-vulnerability-assessment.md).

Both are replaced by the title the manuscript now carries, which names the result rather than the
proposal. ⚠ The generated view is stale until `python3 systems/systems_check.py --write-views` is
run.
