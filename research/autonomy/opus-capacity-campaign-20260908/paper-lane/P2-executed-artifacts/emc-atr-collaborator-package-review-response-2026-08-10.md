---
id: DOC-EMC-ATR-COLLABORATOR-PACKAGE-REVIEW-RESPONSE
title: "Response to the simulated review of emc-atr-collaborator-package.md"
level: L3
kind: manuscript
status: live
canonical_for: []
purpose: Record what changed in the EMC NR4A3 fusion manuscript in response to each point of its simulated review, and why each declined point was declined.
scope: One manuscript's revision. It reports no new result and asserts nothing about any disease or agent.
audience: [maintainers, external reviewers]
date: 2026-08-10
last_verified: 2026-08-10
---

> **THIS RESPONDS TO A SIMULATED INTERNAL REVIEW, WRITTEN BY AN AI REVIEWER AT THE AUTHOR'S REQUEST.
> IT IS NOT CORRESPONDENCE WITH A JOURNAL.** No editor, no journal and no external reviewer has seen
> this manuscript. Nothing in this file is correspondence from *Genes, Chromosomes and Cancer*, from
> Wiley, or from any person other than the author's own tooling. Do not attach it to a submission,
> and do not describe the manuscript anywhere as "revised in response to review" on the strength of
> it.

# Response to the simulated review

**Manuscript:** [`emc-atr-collaborator-package.md`](./emc-atr-collaborator-package.md)
**Review:** [`emc-atr-collaborator-package-peer-review-2026-08-10.md`](./emc-atr-collaborator-package-peer-review-2026-08-10.md)
**Superseded values from this revision:** [`emc-atr-collaborator-package-changelog.md`](./emc-atr-collaborator-package-changelog.md)

**Summary.** Of the 47 revision-list items, 41 are applied in full, 5 are applied in part because the
committed record does not support the rest of what they ask for, and 1 is declined outright. Partial:
item 15, where the offered cross-check is cited for what it actually is; items 20 and 21, where the
accessions are supplied and the Ensembl release and assembly are not, because the cache records
neither; item 22, where the dated note is written and the artifacts are not regenerated; and item 23,
where the screen's limits are stated and its query strings are not, because the artifact does not
record them. Declined: item 45. Each is set out below.

The paper is retitled and restructured to lead with sequence; the frequency error in the
Abstract is corrected against three counted series the repository already held; Table 4's status
column and its two dropped rows are fixed; the headline arithmetic is corrected in every location
and pinned by a test; the exon-numbering correspondence is established in Methods from two primary
sources; the frame rule is stated, tabulated and cited to an audit the manuscript had never cited;
the symmetric prefix sweep is reported; and the paper's first figure was built. Three verification
notes are recorded at the end, including one place where the review's own evidence did not hold up.

---

## The editorial verdict, and the restructure

**New title.** *"Untranslated NR4A3 sequence encodes a 59-residue insertion in the EWSR1 exon 7 to
NR4A3 exon 2 fusion of extraskeletal myxoid chondrosarcoma, and a donor-exon phase rule for the
reported junctions."* This differs from the reviewer's suggested wording in one respect and the
difference is deliberate: the suggested title ended "absent from the protein model in general use",
and Major Point 5 of the same review shows that no source documents what the field's protein model
is. A title cannot assert what the body has just been told to stop asserting. The title now names
what was computed, which is the insertion and its origin.

**New structure.**

| section | content |
|---|---|
| 1 Introduction | why a reported junction is an mRNA event, the prior-art screen with its three limits, and the companion negative findings |
| 2 Materials and methods | transcript provenance; junction arithmetic and the two numbering conventions; the exon-numbering correspondence; the retained-RG axis; the TCF12 comparison; reproduction |
| 3.1 Results | reported junctions with counted frequencies per series (Table 1) |
| 3.2 Results | the donor-exon phase rule (Table 2) |
| 3.3 Results | the 59-residue insertion at nucleotide resolution (Figure 1C) |
| 3.4 Results | the four reported junctions as instances of the rule (Table 3) |
| 3.5 Results | TCF12 as a computed control (Table 4), and Figure 1 |
| 4.1 Discussion | consequences for construct design |
| 4.2 Discussion | placement on the retained-RG axis (Table 5, Figure 1B) |
| 4.3 Discussion | three predictions, their falsifiers, and an analysis plan (Table 6) |
| 4.4 Discussion | limitations, opening with the former standing scope disclaimer |
| 5, 6 | data and code; references |
| Supplementary | gene models (S1) and wild-type controls (S2) |

Display items: one figure and six main-text tables, against seven tables and no figure before.

---

## Major points

**MP1. Article type and framing. APPLIED.** Retitled and restructured as above. The prediction set is
now section 4.3 of the Discussion rather than the paper's purpose. The two sentences named as reading
like a pitch are gone: section 1's "This report supplies those three things" is replaced by a
statement of what the report establishes, and section 5's "Adding EMC to that panel requires plasmids
and nothing else" is replaced by a neutral statement of the assay's unit of work in section 4.3.

**MP2. "The two commonest EMC fusions". APPLIED IN FULL, and verified independently before applying.**
The claim was checked against the two artifacts named and against a third the review did not cite.
Neither source cited for the rank makes a frequency claim: reference 4's committed quotation defines
the two types and reference 6's is an RT-PCR primer design. Three counted series in
[`lit-targets-aso-verify.json`](../aso/lit-targets-aso-verify.json) are quoted verbatim in the new Table
1 and were extracted programmatically rather than transcribed. Panagopoulos, 18 tumours: type 1 in 10
of 15 EWSR1-positive cases, type 5 named "the second most common" at 2 cases, type 2 not among the
counted types, TAF15 in 3 of 18; and 12 of 14 genomic breaks in NR4A3 intron 2 against 2 in intron 1,
with 1 of 14 EWSR1 breaks in intron 7. Okamoto, 15 fusion-positive of 18: type 1 in 11, type 2 in 1,
TAF15 in 3. Sjogren 2003, 10 tumours: EWSR1 in 5, TAF15 in 4, TCF12 in 1. The third series is the
addition to the review's list and it strengthens the same conclusion. "The two commonest" is deleted
from the Abstract, the unsourced rank column is replaced by counted frequencies with a column per
series, section 4.2 no longer rests on type 2 being common, the old P4 is folded into P2, and section
4.2 states that TAF15::NR4A3 is the more frequently counted zero-RG EMC fusion. The series are
reported separately and not pooled, because the reports come from overlapping centres and the
abstracts as retrieved do not establish non-overlap, which this repository's pooling policy requires.

**MP3. Table 4's "measured" labels and its two dropped rows. APPLIED IN FULL.** The status column is
split into "measured in reference 1" and "a reported breakpoint of a disease in which the mechanism
was measured", with a third value "computed here" for the EMC rows. Both dropped rows are restored:
EWSR1::ATF1 at EWSR1 exon 7, retaining 0 of 30, and the one-domain add-back anchor carrying an
explicit "not determinable" because the source does not identify which RGG domain it restored. The
ATF1 comparator is stated as a span from 0.000 to 0.267, with the census module's verbatim "any type,
not all types" statement quoted in section 4.2. "Bracketing" and "interpolate between points already
measured" are both gone; the surviving statement is that the firmly measured positions on this axis
are 0.000 and 1.000 and every EMC fusion falls between them, which is weaker and is what the data
supports. P2's basis is restated as 8 of 30 against 0 of 30, a comparison internal to EMC that does
not depend on the ATF1 breakpoint at all. Figure 1B draws the same content.

**MP4. The arithmetic is one nucleotide short. APPLIED IN FULL, in five locations, and pinned.**
Recomputed from the input cache before applying: EWSR1 coding sequence through exon 7 is 793
nucleotides, 793 modulo 3 is 1, the hybrid codon is AAG encoding lysine at position 265, and 1 plus
176 is 177, which is 59 codons. The 176 is 174 nucleotides of NR4A3 exon 2 plus 2 nucleotides of
exon 3 ahead of the initiator, and the NR4A3 5' untranslated length of 699 decomposes exactly as 523
plus 174 plus 2. Corrected in the Abstract, section 3.3, the Table 3 note, the changelog and the
cover letter. The translated sequence
`KPTAEEGSPASPGPEPGPLAVPGSTAGASPRRTSAPPTLSASAGETPSPTIQRARYPPD` is now in the manuscript text, with
the statement that the first residue is a hybrid codon and the remaining 58 are NR4A3 sequence in a
frame NR4A3 does not use. The arithmetic is pinned by
`tests/test_emc_fet_frame_and_composition.py::test_the_extension_spans_a_whole_number_of_codons`,
which asserts divisibility by three rather than a remembered pair of numbers, and which fails if the
NR4A3 contribution alone is ever recorded as a whole number of codons.

**MP5. The exon-numbering correspondence. APPLIED, with item 3 declined as stated and replaced.** A
new section 2.3 establishes the correspondence from two primary sources: reference 7's genomic
mapping, where a break in NR4A3 intron 2 yields a transcript whose first NR4A3 exon is exon 3 and a
break in intron 1 yields one whose first NR4A3 exon is exon 2, and reference 3's cryptic intron 2
exon "encoding 25 additional amino acids prior to the NR4A3 ATG", which places intron 2 immediately
upstream of the initiator in the field's numbering. Limitation 3 is widened to name what is still
missing. Section 3.3 replaces "the protein-level model in general use" with a statement of what is
documented, which is this analysis's own earlier model, and cites reference 3's 25-residue extension
as precedent for the mechanism, with the novelty scoped to the specific junction and its sequence.

*Item 3 is declined as written, and this is the one place where the review's evidence did not hold
up.* The review offers `junction-aso-designs-e7n3.json` as a cross-check "built from the RefSeq mRNAs
rather than from Ensembl", making the 2-nucleotide figure an agreement between two independent
annotation sources. It is not. That artifact's `_breakpoint_model` does name `NM_005243` and
`NM_006981`, but those are labels inherited from the producing module's default codon-space mode; the
artifact's own `mode` is `real_exon_junction_mRNA` and its `_transcript_source` records
`committed_cache` for both genes, with the same `committed_cache_fetched_utc` as every other module
here. Both sides of the proposed cross-check read the same Ensembl cache, so it is a check on the
code path and not on the annotation. Publishing it as two independent annotation sources agreeing
would be a fabricated corroboration. The artifact is cited in section 2.3 for what it is, and the
absence of an independent annotation check is now limitation 3.

**MP6. One rule, not four instances. APPLIED IN FULL, and this is the largest addition.** Section 3.2
states the rule: a junction is in frame if and only if the 5' donor exon ends one nucleotide into a
codon, and both NR4A3 acceptors give the same register because exon 2 is 174 nucleotides, a multiple
of three. Table 2 gives donor exon, cumulative coding nucleotides, phase and in-frame status against
both acceptors over EWSR1 exons 6 to 14, the range that brackets every reported breakpoint. The rule
was re-derived independently from the cache rather than read out of the audit, checked against all
seventeen EWSR1 coding exons and against all 27 rows of
[`junction-mrna-frame-audit.json`](../../modalities/junction-mrna-frame-audit.json) with no
disagreement, and extended to TAF15 exon 6, which is also phase 1 at 484 coding nucleotides. The
audit is now cited in section 3.2 and in section 5. Section 3.3 states that the insertion is a
property of the exon 2 acceptor, so any 5' partner exon joined to it carries the same 176
nucleotides and what the type-2 breakpoint fixes is the frame they are read in.

**MP7. Reference transcript provenance. APPLIED, with the versioned-accession half declined for
cause.** Supplementary Table S1 now gives transcript and translation accessions for all five genes,
replacing the word "canonical" for TAF15 (ENST00000605844, ENSP00000474096), FUS (ENST00000254108,
ENSP00000254108) and TCF12 (ENST00000333725, ENSP00000331057). Section 2.1 states the retrieval date
and the REST endpoint. The Ensembl release, the genome assembly and version suffixes are **not**
supplied: the cache records none of them and the identifiers it returned carry none, so any value
here would be invention rather than provenance. Section 2.1 says so, and distinguishes reproduction
of the analysis from the cache, which is exact, from reproduction of the cache, which is not
currently possible. This is the fallback the review itself permits.

**MP8. The prediction set. APPLIED IN FULL.** Reduced to three independent predictions. P1 is a rank
prediction over both zero-RG EMC fusions rather than an equivalence claim, and its falsifier includes
no accumulation at the stripe for either, which also closes the gap the review found in the old P3.
P2 is the type-1 against type-2 comparison, with the old P4 folded in as a corollary and the reason
stated. The proximity claim to the commonest clear-cell type is moved to the explicit
non-predictions, with the reason the axis cannot support it: at cuts of 348 and 431 residues the
retained set is the same eight dipeptides at positions 300 to 330, differing only by 83 residues of
RG-free sequence, which was verified from the sequence. P3 states in the table cell where the
prediction is made that no TCF12::NR4A3 construct is supplied and that the substitute is a wild-type
protein rather than a chimera. An analysis plan is added at the end of section 4.3: endpoint,
expression normalisation, nuclei per construct, independent experiments, error-bar meaning, and the
comparison to be made.

**MP9. The novelty claim's support, and the undisclosed companion findings. APPLIED IN FULL.**
Section 1 now states three limits on the prior-art screen rather than one: the title-and-abstract
matching limit, the absence of a positive control and what that means for reading a zero, and the
distinct point that the corpus is anchored on the disease name so a FET-fusion paper not naming EMC
would fail at the retrieval step rather than the matching step, citing the companion assessment's
measured instance of exactly that. The two companion negative findings are stated in section 1: no
proliferation-independent DNA-damage-response signature in EMC tumours on two independent series
totalling 16 tumours, and ATR-inhibitor sensitivity not tracking the mechanism with one of four
pre-registered tests passing and the load-bearing predictor returning minus 0.090, the wrong sign.
Both were verified in the companion document before being restated here. The search strategy request
is met at the level the artifact supports: the corpus size, the full-text retrieval count and the
matched fields are stated, and the query strings are not, because the artifact does not record them.

**MP10. Presentation. APPLIED IN FULL.** A three-panel figure was built and is the paper's Figure 1,
generated by [`emc_fusion_frame_figure.py`](../figures/emc_fusion_frame_figure.py) from three
committed artifacts, emitted at 300 dpi with a vector companion, and greyscale-safe by construction:
no category is encoded by hue, and fills, hatching, marker shape and outline weight carry every
distinction. A provenance record stamps a content hash of each source artifact, and
`--check` compares the stamp against the artifacts on disk so a number changed without a redraw is
detected. Panel A draws EWSR1, TAF15 and NR4A3 to scale with all 30, 31 and 2 RG dipeptides as ticks
at their measured positions, the operational RGG boxes bracketed, NR4A3's C166, C4 zinc finger and
ligand-binding domain marked, and the seven retained 5' segments on the same ruler. Panel B draws the
axis as the data supports it. Panel C draws the seam at nucleotide resolution with the codon comb and
the translated sequence. The figure generator is registered in `lint_style.FIGURE_SOURCES`, so its
rendered strings are held to journal register like any other submission text. Appendix A is deleted
from the manuscript and its content moved to the changelog, with this revision's corrections added.
The editorial comment block is rewritten: its self-contradictory Short Communication limits are gone,
its hand-carried word count is replaced by a pointer to the measuring tool, and its instruction to
"cut section 5 first" is removed. The gene-model table and the wild-type-control table are moved to
supplementary material.

---

## Minor points

1. **Word counts. APPLIED.** The editorial block no longer carries a hand-typed count, which was
   stale at every previous reading; it names `submission_metrics.py` and states that tool's counting
   convention. Final measured values are in
   [`submission-metrics.json`](../submission-metrics.json).
2. **The margin convention. APPLIED.** Section 2.2 states the convention and section 4.2 and P1 use
   the artifact's value, 13 residues of headroom below the RG-free ceiling, with the distance to the
   first RG position distinguished from it.
3. **EWSR1::ATF1 residue numbers off by one from the clear-cell convention. APPLIED.** Section 2.2
   states that residue counts are fully encoded residues only and names the difference from the
   clear-cell literature's EWSR1(1-325) for the exon 8 breakpoint.
4. **"Byte-identical". APPLIED.** Replaced with "identical in sequence".
5. **"The source" and "this programme". APPLIED.** Replaced throughout with "reference 1", "Gracilla
   and colleagues" and "the present analysis".
6. **Artifacts disagreeing with the reference list. APPLIED as the dated note, regeneration
   declined.** Section 5 records all three disagreements, dated, with the statement that each
   concerns provenance and none concerns a computed value. Regenerating the artifacts is declined:
   they were produced by a workflow run whose inputs are pinned, and rewriting them to change a
   citation string would replace a dated measurement with an undated one.
7. **The 85-word methods quotation. APPLIED.** Paraphrased in section 4.3 to the operative
   parameters, cell line, dye and concentration, exposure, wavelength and power, stripe width,
   imaging cadence and duration, with the citation retained.
8. **NR4A3's own RG content. APPLIED.** Two dipeptides, recomputed here, in the GFP-NR4A3 control row
   of Supplementary Table S2 and in Figure 1A.
9. **The asymmetric sweep. APPLIED, after re-running it independently.** Sweeping all four proteins
   on the same grid gives a lowest FET prefix value of 0.439 at EWSR1 residues 1 to 560 against
   TCF12's best of 0.400, a margin of 0.039, reproducing the review's figures exactly. The row is
   graded as separating rather than decisive, the fixed-window row keeps its grade, and the
   arithmetic has a committed home in
   [`emc-fet-frame-and-composition.json`](../../modalities/emc-fet-frame-and-composition.json). A test
   asserts the margin stays inside a narrow band, so a future change to the comparison forces a
   change to the wording.
10. **A background for the composition metric. APPLIED.** A new row in Table 4 gives the same
    250-residue statistic for the three non-FET fusion partners the cache already holds: ATF1 0.324,
    NR4A3 0.264, FLI1 0.248, against TCF12's 0.368 and the FET range of 0.540 to 0.804. The panel is
    stated to be seven proteins and not a proteome background, and no null distribution is claimed.
11. **Table row-to-test correspondence. APPLIED.** Table 4's rows are labelled with their test
    numbers, and the two readouts of test two are labelled 2 and 2b.
12. **The primary pazopanib trial report. DECLINED, with the reason.** No committed retrieval record
    in this repository holds a primary trial report for NCT02066285. Writing that citation from
    recollection is the precise failure mode [`lint_citations.py`](../lint_citations.py) exists for,
    and it is the failure that already happened once in this repository. Section 1 retains the review
    citation, which does report both figures, and names the trial registration in the running text so
    a reader can reach the primary report in one step.
13. **The extra-residues footnote. APPLIED.** Table 3's caption states that the type-2 value is one
    hybrid residue plus 58 encoded by NR4A3 in a non-native frame, so it is not a 59-residue hybrid
    seam.
14. **Submission metadata. APPLIED.** The ORCID placeholder line is removed, since the repository
    holds no ORCID and a bracketed placeholder is worse than its absence; the cover letter states the
    same. A keyword list is added. The cover letter's bracketed date is filled.
15. **The standing scope disclaimer. APPLIED.** Moved intact to the opening paragraph of section 4.4,
    Limitations.

---

## Verification notes

Recorded because a response that only reports compliance is not evidence of any.

- **Everything asserted here was recomputed before it was written.** The frame rule, the seam
  arithmetic, the RG positions and retained counts at every cut, the symmetric sweep, the background
  panel and the counted frequencies were re-derived from the committed cache and the committed
  retrieval record by a new module,
  [`emc_fet_frame_and_composition.py`](../../modalities/emc_fet_frame_and_composition.py), which reads
  only committed files, makes no network call, and has a `--check` mode and nine tests.
- **The counted quotations are extracted, not transcribed.** Each is cut from the stored abstract by
  locating an anchor substring, and a test asserts that every quotation appearing in the artifact is
  a substring of the committed retrieval record, so a quotation typed from memory fails the build.
- **One of the review's own claims did not verify**, and is declined above: the RefSeq cross-check of
  Major Point 5 item 3 reads the same Ensembl cache as everything else here.
- **Two of the review's figures were reproduced exactly**, which is worth stating in the other
  direction: the symmetric sweep's 0.439 and 0.400, and the seam's 177-nucleotide span with the
  lysine hybrid codon at position 265.
- **Nothing was loosened to make a check pass.** Two graph anchors were repointed to sections that
  exist after the restructure and verified to resolve; a citation registry entry was repointed to the
  changelog, which is where the superseded conference-abstract citation now lives, and the
  corresponding changelog row was written in the same edit; and the new figure generator was added to
  the style linter's figure-source list rather than left outside it.
