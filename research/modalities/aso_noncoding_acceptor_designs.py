#!/usr/bin/env python3
"""Gapmer designs at the NR4A3 exon-2 acceptor — the junctions the coding-acceptor filter excludes.

⛔ WHY THIS EXISTS. Every one of the 38 junctions in the manuscript's panel joins a donor exon to
NR4A3 exon **3**. The EWSR1 *type 2* transcript does not: it joins EWSR1 exon 7 to NR4A3 exon **2**,
and it is recurrent rather than anecdotal — defined as the type 2 transcript in a review
(PMID 22567356), sequenced as one of five cases in a whole-transcriptome cohort (PMID 29937513), and
sequenced again in an independent patient (PMID 35488288). The panel cannot express it, because the
atlas grades every exon-2 acceptor NON_CODING_ACCEPTOR: NR4A3 exon 2 lies upstream of the start
codon, so the chimera it makes is not the fusion protein.

⭐⭐ AND SINCE 2026-08-15 A THIRD KIND OF ENTRY SITS HERE: A SEAM WHOSE ACCEPTOR EXON INDEX IS
ITSELF THE OPEN QUESTION. The two identity-clean patient-derived EMC cell models in existence —
USZ20-EMC1 (CVCL_C6MX) and USZ22-EMC2 (CVCL_C6MY), PMID 36316541 / PMC9813045 — are both reported
fusing to "exon 2 from NR4A3", from a FoundationOne®HEME report with no sequenced exon-exon
boundary, no transcript accession and no junction sequence. That label admits two readings and this
module CANNOT decide between them (the full statement is on each entry's
`⚠_read_this_before_using_the_sequence`, which is the one home for it). ⛔ THE POINT OF ADDING THEM
IS NOT THAT THE LITERAL READING WON. It is that designing at BOTH acceptors retires the ambiguity as
a blocker: the exon-3 seams are already in the manuscript panel and already screened, so once the
exon-2 seams exist each model has a reagent under EITHER reading, and nothing downstream has to wait
on an exon index nobody has sequenced. That is a different justification from the other entries here
and it is written down as one rather than blended into them.

⭐ AND SINCE 2026-08-15 A SECOND KIND OF EXCLUSION SITS IN THE SAME LANE: A PARTNER GENE THE ATLAS
DOES NOT MODEL AT ALL. PMID 36103645 reports an EMC fused at "PGR (exon2) to the 5′ untranslated
region (UTR) of NR4A3 (exon2)" — progesterone receptor, a 5' partner outside the five this
repository holds transcript models for, in a tumour that was EWSR1 FISH-negative. So that patient
was invisible to the panel TWICE OVER: once at the acceptor (exon 2, non-coding) and once at the
donor (a gene with no committed transcript). ⚠ It is ONE reported EMC patient and it is in NEITHER
of the two partner cohorts this repository counts against — `hormone-partner-lane.json` owns the
zero-of-84 reading, `aso_coverage_ladder.py` owns the coverage consequence, and neither is restated
here. A junction can be worth designing at and add no measurable coverage; those are two different
statements and this module makes only the first.

★ THAT IS A PROTEIN-LEVEL EXCLUSION, AND THIS IS AN RNA-LEVEL MODALITY. An RNase-H1 gapmer cleaves
a transcript. Whether the chimeric ORF survives decides what PROTEIN the tumour makes; it does not
decide whether the transcript exists, whether it is tumour-specific, or whether it can be cut. For a
degrader or a neoantigen the filter is right. For a gapmer it removes a patient population.

⛔ AND THIS DOES NOT DELETE THE GUARD IT ROUTES AROUND — read `junction_aso.build_parents_and_fusion`,
which raises on a non-coding acceptor and calls it "Defect 1, and it is what produced the retracted
seam". That guard is not about biology. It caught a COORDINATE defect: code sliding onto a
neighbouring exon and silently designing against a seam no patient has. Two different things wear
the same grade —
    (a) a coordinate slip onto exon 2 when exon 3 was meant  → still a defect, still must raise;
    (b) a patient whose transcript genuinely joins exon 2    → a target, and the guard cannot tell
        (a) from (b) because it only ever sees the exon index.
So this module does not relax the guard. It names its junctions EXPLICITLY, from published patient
reports, and asserts that each one it emits is one of those — a whitelist, not a bypass. A junction
nobody has sequenced cannot get in here either.

WHAT THIS IS NOT.
  · Not an efficacy claim, and not a claim that any sequence below is active. These are design
    proposals: sequence arithmetic and a parent-exclusion screen, nothing more.
  · ⛔ NOT UNIFORMLY SCREENED — AND THIS SENTENCE NO LONGER SAYS "NOT SCREENED", BECAUSE THAT
    STOPPED BEING TRUE AND A STALE DISCLAIMER IS ITS OWN DEFECT. The five deep screens the panel's
    other junctions went through are transcript BLAST, pre-mRNA, genome, mature-parent gap pairing
    and locus collapse. ⚠ THE PER-JUNCTION STATE IS NOT WRITTEN HERE. It is emitted per design in
    the artifact's `⚠_offtarget_screens_run` field, which names what ran and what did not, and that
    field is the one home for it — because a docstring cannot know which screens landed after it
    was written, and this paragraph has now proved that twice.
    ⚠ SUPERSEDED, RETAINED: "As of 2026-08-15 EWSR1_e7__NR4A3_e2 has all five and PGR_e2__NR4A3_e2
    does not." Both junctions have all five. The PGR alignment arm landed in commit b977ef616 and
    the committed artifact was not regenerated, so the JSON kept saying "still INCOMPLETE at
    PGR_e2__NR4A3_e2" while its own generator, run against the screened table, said COMPLETE at
    both. Read the field rather than this paragraph — and regenerate the artifact when a screen
    lands, because a derived sentence is only as fresh as its last build.
    ⛔ WHAT DOES NOT CHANGE: a design here is comparable with a panel design only on the screens
    BOTH have been through, and the expression arm is separate from all five.
    ⚠ The docstring and the artifact disagreed for part of 2026-08-15 — the prose still said
    "have NOT been run" while the JSON already said the five were complete at the exon-2 seam. A
    disclaimer that overstates caution reads as harmless and is not: it is the same class of defect
    as a stale "screened", a claim about another artifact's state made without reading it.
    ⛔ CORRECTED 2026-08-15: this list read "transcript, pre-mRNA, genome, tissue expression, locus
    collapse". Tissue expression is an EXPOSURE arm and not one of the five — the manuscript's §3.5
    says "All five screens address hybridisation-dependent liability only" and reports the
    expression result separately, as "the expression reading". The same wrong list also stood in
    aso_taf15_intron2_designs.py, and between them they had the integration board counting EWSR1
    e13 and TCF12 e5 at four of five when neither was ever short a screen. One set, named two ways,
    in two committed files — CLAUDE.md rule 1.
  · Not a coverage claim. What these junctions would add is priced in
    research/manuscripts/aso_coverage_ladder.py, which prices them at zero design availability
    precisely because this file did not exist when it was written.
  · Not a statement that the type 2 chimera is oncogenic, or that it makes any protein at all. The
    reading frame question is real and unresolved; it is simply not the gapmer's question.
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "aso-noncoding-acceptor-designs.json")
sys.path.insert(0, HERE)

import junction_aso as ja  # noqa: E402
import aso_screen_sets as ass  # noqa: E402


#: ⭐⭐ THE WILD-TYPE-ALLELE SCAN, BORROWED RATHER THAN REIMPLEMENTED (added 2026-08-15).
#:
#: ⛔ WHY IT BELONGS AT THIS SEAM AND NOT ONLY AT THE CRYPTIC-EXON ONE. The acceptor half of every
#: design in this module is NR4A3 exon-2 5'UTR sequence, and in the patient's UN-REARRANGED NR4A3
#: allele that same sequence sits immediately 3' of intron 1. So a design whose 6-nt catalytic gap
#: falls mostly on acceptor bases can form a fully gap-paired, RNase-H1-competent duplex on the
#: wild-type allele, across the intron-1/exon-2 boundary — in a compartment the spliced-cDNA parent
#: screen in `design(parents=...)` STRUCTURALLY CANNOT SEE, because a mature NR4A3 transcript has
#: exon 1 there instead of intron 1. Measured at the sibling cryptic-exon seam: all five designs
#: cleared the parent screen and the genome screen then found one of them cleaving wild-type NR4A3.
#: A 5/5 parent-screen pass is therefore not evidence either way, here or there.
#:
#: ⛔ AND IT IS THE SAME FUNCTION, NOT A SECOND ONE. `aso_taf15_intron2_designs.wildtype_nr4a3_liability`
#: is already validated against a known positive; a private copy here would be a second definition
#: of "cleavage-competent on wild-type NR4A3" and the two would disagree the first time either was
#: edited. Its `cryptic` argument is the anchor for a cryptic-exon-relative offset and is passed
#: None here, which is the only difference.
import aso_taf15_intron2_designs as _wt  # noqa: E402

#: ⛔⛔ RETRACTED — SEAMS THIS MODULE ONCE WHITELISTED AND MUST NEVER REACH AGAIN.
#:
#: A whitelist that only ever grows cannot express "we looked, and the seam is not there". Deleting
#: an entry silently would leave the next reader free to re-add it from the same case report, which
#: is exactly how a withdrawn seam comes back. So a withdrawal is RECORDED here with the observation
#: that settled it, `_assert_no_retracted_junction_is_whitelisted()` fails the import if the tuple
#: ever reappears above, and `retraction_for()` gives the guard a NAMED refusal instead of the
#: generic "nobody sequenced this" one — a reader who opts in at a retracted seam gets the verdict,
#: not a puzzle.
RETRACTED_PUBLISHED_BREAKPOINTS = {
    ("EWSR1", 11, "NR4A3", 3): {
        "retracted_utc": "2026-08-15",
        "verdict": "NOT A DISTINCT JUNCTION — the vendor's 'ex11' is not this repository's EWSR1 "
                   "exon 11. Best-evidenced reading: the canonical EWSR1 exon 12 :: NR4A3 exon 3 "
                   "type-1 junction, which the manuscript panel already carries and has screened.",
        "the_claim_that_was_withdrawn":
            "PMID 36636521 (PMC9831112), vulvar EMC case report, writes the fusion verbatim as "
            "'EWSR1 (ex11)-NR4A3 (CHN,ex3)'. That string was read as a distinct EWSR1 exon-11 donor "
            "and given designs in this module on 2026-08-15. It is the ONLY source for that donor "
            "exon in 295 retrieved papers.",
        #: ⛔⛔ WHAT THE WITHDRAWAL RESTS ON, AND WHAT IT DOES NOT. READ THIS BEFORE THE EVIDENCE
        #: LISTS BELOW, because the two are easy to swap and only one of them can carry the verdict.
        "⛔_basis_of_the_withdrawal": (
            "THE EXON-NUMBERING RECONCILIATION, AND NOTHING ELSE. The junction is withdrawn because "
            "the vendor's 'ex11' has been reconciled against the reference exon index and resolves "
            "to our EWSR1 exon 12 — the canonical type-1 junction the manuscript panel already "
            "carries and has already screened. That reconciliation is established by the measured "
            "anchors in `evidence_our_exon_index_IS_the_reference_index`, each of which pins our "
            "index to a named accession or to an external, independently measured breakpoint map. "
            "⚠ IT DOES **NOT** REST ON THE `OUT_OF_FRAME` GRADE. That grade was only ever GROUNDS "
            "FOR SUSPICION — a reason to go and check the exon assignment, which is exactly what was "
            "then done. Treating the frame grade as the basis would be inverting the argument: a "
            "frame reading can tell you an assignment looks wrong, it cannot tell you what the right "
            "assignment is, and it is the numbering work that names exon 12. The frame material is "
            "kept below as corroboration and is labelled as such."),
        #: ⭐ FIVE ANCHORS, EACH MEASURED, NOT ONE OF THEM AN OPINION (the list below carries six
        #: entries: the fifth anchor is stated in two, its numbering half and its selection half).
        #: ⚠ A COUNT TYPED BESIDE A LIST IS A COUNT THAT DRIFTS — this comment said FOUR while the
        #: list held six, because the DSRCT anchor was added after the comment was written. Read the
        #: list, not this number. Together they close the
        #: question the retracted entry left open ("a commercial panel's exon index need not match
        #: the RefSeq/Ensembl model this repository uses") in the direction the entry did not expect:
        #: our index is NOT the odd one out, so the ONE-OFF cannot be resolved in our favour by
        #: renumbering us.
        "evidence_our_exon_index_IS_the_reference_index": [
            "PMID 22567356 (PMC3371325) states its EMC RT-PCR primers against a NAMED ACCESSION: "
            "'primers targeting EWSR1 (exon 7: TCCTACAGCCAAGCTCCAAGTC and exon 11: "
            "GACTCTAGATGATCTGGCAGAC, RefSeq: NM_005243.3) … and NR4A3 (exon 3: "
            "CCTGGAGGGGAAGGGCTATATTGGG, RefSeq: NM_006981.3)'. Located against this repository's "
            "committed transcript models (junction_aso.transcript_model, TRANSCRIPT_SOURCE=cache): "
            "the exon-7 primer lands at EWSR1 cDNA 804-825 = transcript exon 7; the exon-11 primer "
            "at 1184-1205 = transcript exon 11; the NR4A3 exon-3 primer (reverse) at 715-739 = "
            "transcript exon 3. THREE independent primers, three exact landings — RefSeq NM_005243.3 "
            "/ NM_006981.3 exon numbering IS ours.",
            "PMID 31020999 (PMC6766969) builds the type-1 construct as 'E-N, corresponding to EWSR1 "
            "(exons 1-12)-NR4A3 (exons 3-8)' and names the acceptor transcript ENST00000395097.6 — "
            "the SAME NR4A3 transcript this repository models. Our NR4A3 model has 8 transcript "
            "exons of which 3-8 are the whole CDS (nr4a3-exon-audit.json), so 'exons 3-8' matches "
            "exon for exon.",
            "EWSR1 has NO non-coding first exon to hide a one-off in: nr4a3-exon-audit.json records "
            "EWSR1 ENST00000397938 with n_transcript_exons=17, n_coding_exons=17 and "
            "first_transcript_exon_is_coding=true. Transcript rank and coding index are the same "
            "number for every EWSR1 exon, so the classic source of a coding-vs-transcript offset "
            "does not exist on the donor side. (NR4A3 is the gene that HAS one — exons 1-2 carry no "
            "CDS — and that offset is already graded in the same file.)",
            "junction_aso.EWSR1_KEEP_AA = 264 is the EWS-FLI1 breakpoint residue, and our exon 7 "
            "ends at cumulative coding nt 793 = residue 264. The field's other EWSR1 landmark lands "
            "on our index too.",
            "★ THE STRONGEST ANCHOR, AND IT TESTS THE PHASE TABLE AND THE NUMBERING AT ONCE. "
            "PMC10344636 maps DSRCT genomic breakpoints and finds them in 'EWSR1 introns 7, 9, and "
            "10', with NONE in intron 8 despite intron 8 being much the largest of the four ('2.8 kb "
            "versus 1.5 kb, 0.5 kb, and 0.4 kb'). It gives the reason: 'a fusion of EWSR1 exon 8 to "
            "WT1 exon 8 would produce a frameshifted transcript … the resulting transcripts would "
            "fail to produce a functional EWSR1-WT1 protein capable of binding to DNA and driving "
            "oncogenesis'. Read against our committed EWSR1 model, cumulative coding nt mod 3 is "
            "e7 793→1, e8 974→2, e9 1012→1, e10 1045→1: the three OBSERVED donors share one phase "
            "and the one ABSENT donor is the odd one out — reproduced exactly. A numbering shift of "
            "even one exon would scramble that partition, so this checks our index and our frame "
            "arithmetic against an external, measured breakpoint map. It also settles the DNA-vs-RNA "
            "convention the case report's assay forces on us: the same paper equates a genomic break "
            "in 'intron 7, 9, or 10' with a spliced donor of 'exon 7, 9, or 10' — intron N ↔ donor "
            "exon N, one index, no offset.",
            "⭐ AND IT IS WHY AN OUT-OF-FRAME DONOR EXON IS NOT MERELY UNATTESTED BUT NOT EXPECTED. "
            "The DSRCT map is direct evidence that frame SELECTS which EWSR1 exon appears as a "
            "breakpoint in patients, even where the genomic opportunity is largest. Our EWSR1 e11 is "
            "phase 0 against an NR4A3 exon-3 acceptor that retains 2 nt of 5'UTR, i.e. exactly the "
            "'exon 8' case; the EMC donors actually reported, e12 and e13, are both phase 1.",
        ],
        #: ⚠ CORROBORATION, NOT THE BASIS — see `⛔_basis_of_the_withdrawal`. This is the material
        #: that made the exon assignment WORTH CHECKING. It is retained because a suspicion that
        #: turned out to be justified is part of how the finding was reached, and deleting it would
        #: make the numbering work look like it came from nowhere. It is NOT what the verdict stands
        #: on, and it could not be: OUT_OF_FRAME says an assignment looks wrong, never which
        #: assignment is right.
        "corroboration_only_the_seam_as_written_cannot_be_the_EMC_driver": [
            "nr4a3-fusion-junction-atlas.json grades EWSR1_e11__NR4A3_e3 OUT_OF_FRAME "
            "(frame_sum_mod3 = 2). EWSR1 cumulative coding nt through exon 11 is 1164 and NR4A3 "
            "transcript exon 3 retains 2 nt of 5'UTR ahead of its ATG, so the chimeric ORF opened at "
            "EWSR1's own start codon reads NR4A3 out of register — no NR4A3 DNA-binding domain, so "
            "not the fusion transcription factor that defines EMC. The tumour in the report is a "
            "bona fide EMC on histology, IHC and course.",
            "PMID 29937513, the only retrieved series that resolves every case to an exon pair by "
            "sequencing: 'All fusions retained the coding frame for creating a chimeric protein, "
            "with the exception of sample #1, in which EWSR1 fuses with exon2 of NR4A3, an exon "
            "upstream of the start codon.' The one described exception is a 5'UTR acceptor, which "
            "leaves NR4A3's own ORF intact — NOT a frameshifted coding-exon acceptor.",
            "In-frame EWSR1 donors to NR4A3 exon 3 in our atlas: e1, e4, e7, e9, e10, e12, e13, e15. "
            "Out of frame: e2, e3, e5, e6, e8, e11, e14, e16, e17. The two in-frame exons adjacent "
            "to 11 are e10 and e12.",
        ],
        "why_exon_12_rather_than_exon_10": [
            "lit-targets-aso-breakpoint-census.json junction_census: EWSR1_e12__NR4A3_e3 is 'type 1' "
            "at k=13 of n=20 pooled sequenced EWSR1 EMC (PMID 12378528 + PMID 29937513) — the single "
            "commonest junction in the disease. EWSR1 exon 10 is reported as an EMC donor by NO "
            "source in the 295-paper corpus.",
            "PMID 32612944 (PMC7308468), a clinical qRT-PCR panel, targets exactly "
            "'EWSR1(ex7)/NR4A3(ex2), EWSR1(ex12)/NR4A3(ex3), EWSR1(ex13)/NR4A3(ex3), and "
            "TAF15(ex6)/NR4A3(ex3)' — the same '(exN)' rendering as the case report, and exon 11 is "
            "not among the junctions a diagnostic laboratory thought worth detecting.",
        ],
        #: ⭐ A SECOND, INDEPENDENT ROUTE REACHED THE SAME PLACE. Recorded with its provenance
        #: attached rather than absorbed into the counts above, because it was not measured here.
        "independent_confirmation_from_the_corpus_sweeps": {
            "finding": "No report of an EWSR1 exon-11 breakpoint in EMC exists anywhere in the "
                       "swept literature apart from PMID 36636521 itself. The only other exon-11 "
                       "mention is a PRIMER POSITION in a Methods table (PMC3371325's EMC RT-PCR "
                       "forward primer, which sits 28 nt upstream of the exon 11/12 boundary and is "
                       "there to amplify ACROSS the exon-12 and exon-13 breakpoints) — a primer "
                       "location is not a breakpoint, and it was correctly left unconverted rather "
                       "than filed as a junction. Two independent routes, numbering and retrieval, "
                       "now agree the junction was never real.",
            "⚠_provenance": "The two-sweep total (~1,030 papers) was REPORTED BY THE MAIN THREAD, "
                            "not measured in this task, and is recorded here as an attribution "
                            "rather than as a count this module verified. What WAS checked here: "
                            "the 295-paper EMC breakpoint census and the 124-paper F1CDx corpus "
                            "(fetch-literature run 31886456405), in which the string 'EWSR1 … exon "
                            "11' occurs in exactly three papers — PMID 36636521 itself, PMC3371325's "
                            "primer table, and PMC10855420, which is an EWSR1::BEND2 fusion in a "
                            "different tumour type and not an NR4A3 acceptor at all.",
        },
        #: ⚠ THE HONEST RESIDUAL. Stated because a retraction that overstates its own certainty is
        #: the same failure as the claim it replaces.
        "⚠_what_this_does_NOT_establish": (
            "FOUNDATIONONE CDX'S OWN TRANSCRIPT MODEL WAS NOT READ. It is not in this repository, "
            "not in the case report, and a targeted Europe PMC sweep dispatched to find a second "
            "F1CDx-reported EWSR1 fusion to calibrate it against (fetch-literature runs 31886265088 "
            "failed on a control bug of mine, 31886373463 returned 0 on a bad field qualifier, "
            "31886456405 SUCCEEDED and published 124 papers to literature-cache under "
            "literature/f1cdx-fusion-exon-nomenclature/) returned NO second F1CDx fusion call "
            "carrying an exon number — the retrieved corpus contains exactly one such string and it "
            "is this case's own. So the MECHANISM of the one-off is not demonstrated, only its "
            "direction. Recorded as a real gap, not smoothed over. "
            "⚠ The residual reading is that the vendor index is correct and the assay reported a "
            "GENOMIC break in EWSR1 intron 11 whose spliced product nobody observed — F1CDx is a "
            "DNA-only panel (PMC12320126: 'F1CDx, NCC Onco-panel, and F1LCDx are DNA panels'; "
            "PMC12488741: 'FoundationOne®CDx (DNA)'; PMC12775561: 'a conventional DNA-only test "
            "(FoundationOne CDx)'), and the report calls it 'cancer genome profiling' with no "
            "transcript accession, no coordinate, no RNA confirmation and no fusion-type number. "
            "That reading is WEAKER than it looks, because PMC10344636 shows intron N and donor exon "
            "N are the same index and that an out-of-frame donor exon is selected AGAINST as a "
            "breakpoint — so an intron-11 break would have to yield the frameshifted product that "
            "map finds patients do not carry. But it is not excluded, and under it the mRNA seam is "
            "simply unobserved, so there is still nothing for a gapmer to be designed against. "
            "Both readings withdraw the junction; they differ only in what replaces it."),
        "what_would_reopen_it": (
            "A nucleotide-resolution RNA-level breakpoint — RNA-seq, RT-PCR across the seam, or a "
            "vendor report quoting a transcript accession — placing a patient's spliced junction at "
            "EWSR1 exon 11 as numbered in NM_005243.3 / ENST00000397938. Nothing less: the four "
            "anchors above are what a contrary claim has to displace."),
        "one_home_for_the_evidence":
            "research/manuscripts/aso/lit-targets-aso-breakpoint-census.json",
    },
}

#: ⛔⛔ THE ONE HOME FOR THE USZ ACCEPTOR AMBIGUITY — shared verbatim by both USZ entries below.
#:
#: It is a CONSTANT and not two paragraphs because it is ONE fact about ONE report: two cell models,
#: one paper, one FoundationOne®HEME pipeline, one shared acceptor label. Written out twice it would
#: drift the first time either entry was edited, which is rule 1 exactly. ⚠ AND IT IS NOT A FOOTNOTE
#: TO THE SEQUENCES — it is the reason the sequences exist, so it travels into every artifact built
#: from this dict through `⚠_read_this_before_using_the_sequence`.
_USZ_ACCEPTOR_AMBIGUITY = (
    "FIVE THINGS A READER MUST HOLD AT ONCE, AND THE SEQUENCE ARITHMETIC RESOLVES NONE OF THEM. "
    "(1) THE ACCEPTOR EXON INDEX IS NOT SETTLED AND THIS ENTRY DOES NOT SETTLE IT. The only "
    "statement of these two junctions anywhere is a FoundationOne®HEME report label quoted in a "
    "figure legend: 'exon 2 from NR4A3'. There is NO sequenced exon-exon boundary, NO transcript "
    "accession and NO junction sequence behind it. Two readings survive. READING A (literal): the "
    "acceptor really is NR4A3 transcript exon 2 — not an absurd reading, because NR4A3 exon 2 is a "
    "genuine sequence-confirmed EMC acceptor, which is what the EWSR1 e7 :: NR4A3 e2 type 2 "
    "transcript in this same dict is. READING B (breakpoint-flanking label): the number names the "
    "last exon 5' of the break the assay called, while the spliced transcript still joins the donor "
    "to NR4A3 exon 3 — the junction the manuscript panel already carries and has already screened. "
    "⛔ THIS REPOSITORY HAS ALREADY RETRACTED A SEAM FOR EXACTLY THIS CLASS OF ERROR: "
    "EWSR1_e11__NR4A3_e3, withdrawn 2026-08-15, a vendor exon label read as a reference exon index "
    "(see RETRACTED_PUBLISHED_BREAKPOINTS above). "
    "(2) THE MEASUREMENT THAT WAS TAKEN, AND WHAT IT DID AND DID NOT REMOVE. Every NR4A3 transcript "
    "model that could have made 'exon 2' the coding acceptor was checked, and none does: the three "
    "curated RefSeq transcripts NM_006981.4, NM_173199.4 and NM_173200.3 all share non-coding exon "
    "1 and non-coding exon 2 and all three begin their CDS in exon 3 (UCSC ncbiRefSeqCurated, hg38, "
    "chr9), and this repository's own committed model agrees exon for exon "
    "(nr4a3-exon-audit.json, ENST00000395097: transcript exons 1 and 2 is_coding=false, exon 3 "
    "carries first_protein_residue=1). SO NO PUBLISHED NR4A3 NUMBERING MAKES THE CODING ACCEPTOR "
    "'EXON 2'. That removes the simplest form of reading B — an alternative transcript's numbering "
    "— and it does NOT remove reading B, because a breakpoint-flanking label is not a transcript-"
    "exon label at all. ⚠ One difference from the retracted case is real and is recorded without "
    "being leaned on: F1CDx is a DNA-only panel, whereas the FoundationOne®HEME run here extracted "
    "DNA AND RNA and the paper reports the rearrangement 'confirmed on the RNA level'. That makes "
    "reading A more available than it was at the retracted seam; it still produces no accession and "
    "no boundary, so it does not decide the numbering. "
    "(3) WHY THE SEAM IS DESIGNED ANYWAY — AND IT IS NOT THAT READING A WON. Designing at BOTH "
    "acceptors is what retires the ambiguity AS A BLOCKER. The exon-3 seam for each of these two "
    "donors is already in the manuscript's 38-junction panel and already through all five deep "
    "screens; adding the exon-2 seam means each model has a reagent under EITHER reading, so no "
    "downstream step has to wait on an exon index nobody has sequenced. The ambiguity is carried, "
    "not resolved by assertion, and it stays open until (4)'s condition is met. "
    "(4) NO PUBLISHED PATIENT COUNT, AND EXACTLY ZERO COVERAGE MOVEMENT. Neither junction has a "
    "reported prevalence anywhere. Neither donor-acceptor pair is in the 58-case cohort every "
    "coverage rung in `aso_coverage_ladder.py` is computed against, so a reagent here moves the "
    "ladder by zero — not by a little, by zero — exactly as recorded for PGR above. What it changes "
    "is which MODELS are testable at all, which is a different statement from coverage and must "
    "never be added to a coverage percentage. Under a panel stocked FOR TESTING rather than for "
    "population coverage, an absent patient count is not an argument against these seams: these are "
    "the junctions of the only two patient-derived EMC models that are both fusion-annotated and "
    "free of an identity flag (STR-matched to their native tumours, DNA-methylation class EMC at "
    "0.99, no Cellosaurus problematic-line record). "
    "(5) NUCLEOTIDE-RESOLUTION CONFIRMATION IN TEST MATERIAL IS A PRECONDITION, NOT A NICETY — the "
    "same requirement §5.4 of the manuscript already places on the exon-3 reagents, and here it is "
    "load-bearing rather than routine, because it is also the observation that would decide between "
    "readings A and B. One RT-PCR/Sanger read across either model's junction settles it.")

#: ⛔ THE WHITELIST. A junction gets designs here ONLY if a published report places a patient's
#: breakpoint at it. This is what keeps the module from being a bypass of the coding-acceptor guard:
#: it cannot reach a seam nobody has sequenced, which is the failure that guard exists to stop.
PUBLISHED_NONCODING_ACCEPTOR_JUNCTIONS = {
    ("PGR", 2, "NR4A3", 2): {
        "transcript_type": "no type number reported — a novel 5' partner",
        "excluded_from_the_panel_by": "NON_CODING_ACCEPTOR",
        "evidence": [
            "PMID 36103645 (PMC9489176), JCO Precis Oncol 2022 — 'The results of next-generation "
            "sequencing revealed gene fusion of progesterone receptor, PGR (exon2) to the 5′ "
            "untranslated region (UTR) of NR4A3 (exon2)'",
            "Same report, on why a canonical-partner assay would have missed it: 'Fluorescent in "
            "situ hybridization was negative for EWSR1 rearrangement.'",
            "Same report, on the assay that found it: 'RNA sequencing was performed using a "
            "lab-developed, exome-capture RNA-sequence protocol.' — and 'To our knowledge, this "
            "fusion would have not been captured by existing commercial vendors which use "
            "panel-based approaches that do not include PGR or N4A3.'",
            "⛔ ONE EMC CASE, AND A NEAR-MISS THAT MUST NOT BE COUNTED AS A SECOND. Two corpus "
            "sweeps totalling ~1,030 papers returned PMC12730577 as a further PGR::NR4A3 source; "
            "it is UTERINE EPITHELIOID LEIOMYOSARCOMA, not EMC, and it does not corroborate this "
            "junction in this disease. The case report itself already says the same thing about "
            "the same partner in the same other disease: 'Previously, Chiang et al reported four "
            "cases of uterine epithelioid leiomyosarcoma also with a PGR-NR4A3 fusion. However, "
            "the clinical implications of anti-estrogen treatment were not mentioned.' So "
            "n_independent_sources stays at ONE, for EMC.",
            "⚠ CONTEXT — PGR IS NOT THE ONLY MINOR NR4A3 PARTNER, AND IT IS THE ONLY "
            "EXON-RESOLVED ONE. The same sweeps found PRRC1 (one EMC case, conference abstract, "
            "no exon reported, so no seam can be built) and GREB1 (UTROSCT, not EMC). A partner "
            "with no exon is not designable and is not a gap in this module; it is a gap in the "
            "literature.",
        ],
        "n_independent_sources": 1,
        "⚠_read_this_before_using_the_sequence": (
            "FOUR THINGS A READER MUST HOLD AT ONCE, AND NONE OF THEM IS RESOLVED BY THE SEQUENCE "
            "ARITHMETIC BELOW. (1) ONE PATIENT, AND ZERO MEASURABLE COVERAGE. This is a single "
            "case report. PGR appears in ZERO of the 84 partner-genotyped EMC cases this "
            "repository cites — `hormone-partner-lane.json` owns that count and its Wilson "
            "interval — and it is NOT a partner of the 58-case cohort "
            "(`aso_reagent_coverage.PARTNER_COHORT`: 46 EWSR1, 9 TAF15, 2 TCF12, 1 with no "
            "identified partner) that every coverage rung in `aso_coverage_ladder.py` is computed "
            "against. A reagent at this seam therefore moves the ladder by EXACTLY ZERO — not by a "
            "small amount, by zero — because the denominator contains no case it could engage. "
            "What it changes is which patients are REACHABLE AT ALL, and that is a different "
            "statement from coverage, must be written as one, and must never be added to a "
            "coverage percentage. (2) VENDOR "
            "EXON NUMBERING. The report states no transcript accession, so 'PGR (exon2)' is an "
            "exon index against an unstated model; this module builds it against the Ensembl "
            "CANONICAL PGR transcript, and if the report's model differs the donor cut moves. "
            "Same unresolved problem as the EWSR1 ex11 row above, and it is the reason "
            "nucleotide-resolution confirmation in test material is a precondition, not a nicety. "
            "(3) A PARENT THAT IS EXPRESSED IN NORMAL TISSUE. PGR is a hormone receptor; the "
            "parent-exclusion screen below runs against wild-type PGR transcript for that reason, "
            "and the tissue-expression screen is the one that matters most at this seam. (4) THE "
            "PATIENT BENEFIT IN THAT PAPER CAME FROM TAMOXIFEN, NOT FROM ANYTHING LIKE THIS. The "
            "report's own result is 'She began targeted therapy with tamoxifen, a selective "
            "estrogen receptor modulator. Since initiation of tamoxifen was over 5 years ago, she "
            "has had ongoing decrease in size of her pulmonary nodules and no evidence of disease "
            "progression'. That is a hormonal route acting on the ESTROGEN-DRIVEN expression of "
            "the PGR promoter the fusion imports; it is not a junction-directed mechanism, and "
            "nothing here competes with it, improves on it or is supported by it."),
        "one_home_for_the_evidence":
            "research/manuscripts/aso/lit-targets-aso-breakpoint-census.json",
    },
    ("EWSR1", 7, "NR4A3", 2): {
        "transcript_type": "EWSR1::NR4A3 type 2",
        "excluded_from_the_panel_by": "NON_CODING_ACCEPTOR",
        "evidence": [
            "PMID 22567356 — 'exon 7 of EWSR1 is fused to exon 2 of NR4A3 in the type 2 fusion "
            "transcript'",
            "PMID 29937513 — whole-transcriptome sequencing; 'exon13/exon3 and exon7/exon2 were "
            "detected respectively in samples #4 and #1', one of five EMC cases",
            "PMID 35488288 — independent case report; 'An EWSR1 exon 7-NR4A3 exon 2 fusion was "
            "subsequently identified'",
        ],
        "n_independent_sources": 3,
        "one_home_for_the_evidence":
            "research/manuscripts/aso/lit-targets-aso-breakpoint-census.json",
    },
    ("EWSR1", 13, "NR4A3", 2): {
        "transcript_type": (
            "no type number reported — a FoundationOne®HEME exon label in a cell-model "
            "establishment paper, not a sequenced junction"),
        "excluded_from_the_panel_by": "NON_CODING_ACCEPTOR",
        "model_it_makes_testable": "USZ20-EMC1 (RRID:CVCL_C6MX), under reading A of its acceptor",
        "evidence": [
            "PMID 36316541 (PMC9813045), Hum Cell 36:446-455 (2023), Figure 4 legend — 'The "
            "rearrangement and fusion partner was confirmed by NGS using the FoundationOne®HEME "
            "assay. For USZ20-EMC1; EWSR1 was confirmed as fusion partner having exon 13 for EWSR1 "
            "on chr22 and exon 2 from NR4A3 on chr9 involved (B).'",
            "Same report, on the material the call was made in — this is a PATIENT's breakpoint and "
            "not only a cell line's: 'For USZ20-EMC1, an EWSR1-NR4A3 rearrangement and, for "
            "USZ22-EMC2, a TAF15-NR4A3 rearrangement in the native tumor tissue and the "
            "corresponding cell model was confirmed on the RNA level (Fig. b, d).'",
            "Same report, Methods, on the assay: 'FoundationOne®HEME assay is a next generation "
            "sequencing (NGS) assay that uses a hybrid capture methodology and detects base "
            "substitutions, insertions, deletions, and copy number (CN) alterations in up to 406 "
            "genes and gene rearrangements in up to 265 genes, tumor mutation burden and "
            "microsatellite instability using the previously described methods. DNA and RNA was "
            "extracted using the Maxwell® Tissue DNA Purification Kit (Promega AS1030).'",
            "Cellosaurus curation of the same PubMed record, not an independent observation — 'CC "
            "Sequence variation: Gene fusion; HGNC; HGNC:3508; EWSR1 + HGNC; HGNC:7982; NR4A3; "
            "Name(s)=EWSR1-NR4A3; Note=EWSR1 exon 13 fused to NR4A3 exon 2 (PubMed=36316541).' "
            "(ID USZ20-EMC1 / AC CVCL_C6MX)",
            "⛔ ONE REPORT, ONE ASSAY, AND THE CELLOSAURUS ROW IS NOT A SECOND SOURCE — it cites "
            "PubMed=36316541, which is this same paper. n_independent_sources is therefore ONE.",
        ],
        "n_independent_sources": 1,
        "⚠_read_this_before_using_the_sequence": _USZ_ACCEPTOR_AMBIGUITY,
        "one_home_for_the_evidence":
            "research/modalities/emc-model-junction-evidence.json",
    },
    ("TAF15", 6, "NR4A3", 2): {
        "transcript_type": (
            "no type number reported — a FoundationOne®HEME exon label in a cell-model "
            "establishment paper, not a sequenced junction"),
        "excluded_from_the_panel_by": "NON_CODING_ACCEPTOR",
        "model_it_makes_testable": "USZ22-EMC2 (RRID:CVCL_C6MY), under reading A of its acceptor",
        "evidence": [
            "PMID 36316541 (PMC9813045), Hum Cell 36:446-455 (2023), Figure 4 legend — 'For "
            "USZ22-EMC2; TAF15 was confirmed as fusion partner having exon 6 for TAF15 on chr17 "
            "and exon 2 from NR4A3 on chr9 involved (D).'",
            "Same report, on the material the call was made in — this is a PATIENT's breakpoint and "
            "not only a cell line's: 'For USZ20-EMC1, an EWSR1-NR4A3 rearrangement and, for "
            "USZ22-EMC2, a TAF15-NR4A3 rearrangement in the native tumor tissue and the "
            "corresponding cell model was confirmed on the RNA level (Fig. b, d).'",
            "Cellosaurus curation of the same PubMed record, not an independent observation — 'CC "
            "Sequence variation: Gene fusion; HGNC; HGNC:7982; NR4A3 + HGNC; HGNC:11547; TAF15; "
            "Name(s)=TAF15-NR4A3; Note=TAF15 exon 6 fused to NR4A3 exon 2 (PubMed=36316541).' "
            "(ID USZ22-EMC2 / AC CVCL_C6MY)",
            "⚠ THE DONOR HALF IS THE ONE HALF NOBODY DISPUTES, AND IT IS THE COMMONEST TAF15 DONOR "
            "IN THE DISEASE: PMID 31020999 (PMC6766969) builds 'T-N*, corresponding to the "
            "commonest TAF15 (exons 1-6)-NR4A3 (exons 3-8) fusion'. The disagreement between that "
            "construct and this report is at the ACCEPTOR only — which is the whole of the "
            "ambiguity below.",
            "⛔ ONE REPORT, ONE ASSAY, AND THE CELLOSAURUS ROW IS NOT A SECOND SOURCE — it cites "
            "PubMed=36316541, which is this same paper. n_independent_sources is therefore ONE.",
        ],
        "n_independent_sources": 1,
        "⚠_read_this_before_using_the_sequence": _USZ_ACCEPTOR_AMBIGUITY,
        "one_home_for_the_evidence":
            "research/modalities/emc-model-junction-evidence.json",
    },
}


def _assert_no_retracted_junction_is_whitelisted():
    """A retracted seam must not be re-addable by editing one dict and not the other.

    ⛔ RUNS AT IMPORT, not in a test, because the failure it catches is a seam being DESIGNED — and
    by the time a test notices, the artifact with the sequences in it has already been written and
    could already have been quoted. The two dicts must stay disjoint; if they ever overlap, the
    module refuses to load rather than emitting designs at a junction this repository has withdrawn.
    """
    clash = sorted(set(RETRACTED_PUBLISHED_BREAKPOINTS) & set(PUBLISHED_NONCODING_ACCEPTOR_JUNCTIONS))
    if clash:
        raise RuntimeError(
            f"{clash} appear(s) in BOTH the published-breakpoint whitelist and "
            "RETRACTED_PUBLISHED_BREAKPOINTS. A retracted seam cannot be re-whitelisted by adding it "
            "back; read the retraction record's `what_would_reopen_it` and satisfy it, or remove the "
            "retraction with the evidence that overturns it. Refusing to load.")


_assert_no_retracted_junction_is_whitelisted()


def retraction_for(donor_sym, d_end, acceptor_sym, a_start):
    """The retraction record for a seam this repository has withdrawn, or None.

    ⭐ WHY THE GUARD CALLS THIS INSTEAD OF JUST SAYING "not on the whitelist". Those two states look
    identical to `published_breakpoint_waiver` and are completely different to a reader: one means
    "nobody has sequenced this", the other means "we looked, here is what we found, here is what
    would reopen it". Collapsing them would send the next session back to the same case report to
    re-derive the same answer — which is the specific waste a recorded retraction exists to prevent.
    """
    return RETRACTED_PUBLISHED_BREAKPOINTS.get((donor_sym, d_end, acceptor_sym, a_start))


#: Every partner transcript the parent-exclusion screen runs against. ⚠ WIDER THAN THE FUSION'S OWN
#: TWO PARENTS ON PURPOSE — the FET donors are paralogues with similar low-complexity N-termini, so
#: a design against one partner's junction can be a perfect complement of another's wild-type
#: transcript. `junction_aso.design` documents this; the point is to inherit it, not restate it.
#: ⭐ PGR ADDED 2026-08-15 WITH THE PGR::NR4A3 SEAM, AND IT IS THE MOST IMPORTANT ENTRY IN THIS
#: TUPLE. Wild-type PGR is a hormone-receptor transcript expressed in normal breast, uterus and
#: ovary — a design against the PGR::NR4A3 seam whose donor half perfectly complements wild-type PGR
#: would engage a gene the patient runs in healthy tissue. Every design in every junction of this
#: module is now screened against it, which makes the test strictly stricter everywhere, not only at
#: the new seam.
PARENT_SYMBOLS = ("EWSR1", "TAF15", "TCF12", "FUS", "TFG", "PGR", "NR4A3")


def _parents():
    out = {}
    for sym in PARENT_SYMBOLS:
        try:
            out[sym] = ja.transcript_model(sym)["cdna"]
        except Exception as exc:                                  # noqa: BLE001
            # ⚠ A PARENT WE COULD NOT LOAD IS NOT A PARENT WE CLEARED. Recorded and surfaced on
            # every design, never silently dropped — a specificity screen that quietly ran against
            # five transcripts while claiming six is the exact shape of a false clean.
            out[sym] = None
            print(f"  ⚠ parent {sym} unavailable: {exc}", file=sys.stderr)
    return out


#: ⛔ WHICH SCREENS HAVE RUN IS READ, NEVER ASSERTED (2026-08-15). This module used to state
#: "⛔ NOT SCREENED FOR OFF-TARGET LOAD … the five deep screens … have NOT been run" as a CONSTANT.
#: That was true the day it was written and stopped being true the day the screen lane learned to
#: run at a whitelisted seam — and a stale "unscreened" is not a harmless conservatism: it is the
#: same class of defect as a stale "screened", a claim about another artifact's state made without
#: reading it. So the status is derived from the screened table itself, and it says NONE only when
#: the table is absent or the junction is not in it, which is the honest reading of "no screen ran".
_SCREENED_TABLE = os.path.join(
    HERE, "noncoding-acceptor", "aso-noncoding-acceptor-screened-table.json")


def _screened_table():
    try:
        with open(_SCREENED_TABLE, encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return None


def _screens_run_on(label):
    """The screens that ran at THIS junction, named, or an explicit NONE."""
    art = _screened_table()
    if not art:
        return ("NONE — no screened table is committed; see _what_this_is_not. This is a screen "
                "that did not run, not a screen that found nothing.")
    if label not in {j.get("junction_label") for j in art.get("junctions") or []}:
        return (f"NONE at this junction — {os.path.basename(_SCREENED_TABLE)} exists but carries no "
                f"row for it. Absent from a table is an absent reading, not a clean one.")
    row = next(j for j in art["junctions"] if j.get("junction_label") == label)
    ran = sorted(k for k, v in (art.get("screens") or {}).items() if v.get("ran"))
    out = sorted(k for k, v in (art.get("screens") or {}).items() if not v.get("ran"))
    # ⛔ THE LANE-WIDE SCREEN LIST IS NOT THIS JUNCTION'S STATE. The alignment screen is dispatched
    # PER JUNCTION, so "the lane's alignment screen ran" can be true while this seam has no rows at
    # all — a sibling's success reported as this one's coverage. `screens_complete` is the per-row
    # flag the table sets, and it is what decides the sentence.
    if not row.get("screens_complete"):
        return (f"INCOMPLETE at this junction. Lane-wide: ran {', '.join(ran) or 'none'}; NOT run "
                f"{', '.join(out) or 'none'} — but this seam's own alignment screen has NOT run, so "
                f"its transcriptome-load fields are null and listed in the table's "
                f"`⛔_unmeasured_fields`. Unmeasured is not clean.")
    return (f"ran: {', '.join(ran) or 'none'}; NOT run: {', '.join(out) or 'none'}. Per-design "
            f"counts are in noncoding-acceptor/{os.path.basename(_SCREENED_TABLE)}, which is the "
            "one home for them; they are not restated here.")


def _off_target_screening_status():
    """The `_what_this_is_not` line about off-target load, derived from the screened table."""
    art = _screened_table()
    if not art:
        return ("⛔ NOT SCREENED FOR OFF-TARGET LOAD. The five deep screens every other junction in "
                "the panel went through have NOT been run on these designs — they need BLAST and "
                "network. These counts are therefore NOT comparable with the panel's, and a design "
                "here is not shown to be as clean as, or cleaner than, any screened design.")
    ran, total = art.get("n_screens_that_ran"), len(art.get("screens") or {})
    js = art.get("junctions") or []
    complete = sorted(j["junction_label"] for j in js if j.get("screens_complete"))
    partial = sorted(j["junction_label"] for j in js if not j.get("screens_complete"))
    return (f"⛔ OFF-TARGET SCREENING IS PER JUNCTION, NOT PER LANE. Lane-wide {ran} of {total} "
            f"screens have run; COMPLETE at {', '.join(complete) or 'no junction'}; still "
            f"INCOMPLETE at {', '.join(partial) or 'no junction'}. A junction whose alignment "
            f"screen has not run carries null transcriptome-load fields, and null is unmeasured — "
            f"never clean, and never comparable with a panel design that went through all five. "
            f"The per-design counts live in "
            f"noncoding-acceptor/{os.path.basename(_SCREENED_TABLE)} and are not restated here.")


def _wild_type_register_table(junction_designs):
    """WHY a design cleaves wild-type NR4A3, computed rather than argued.

    ⭐ THE DISCRIMINATING OBSERVATION, AND IT REFUTES THE OBVIOUS RULE. Every design here spans
    [donor exon 3' end]|[NR4A3 exon 2]. The patient's UN-REARRANGED allele presents the same acceptor
    behind a different left half: [NR4A3 intron 1 3' end]|[NR4A3 exon 2]. So for each design this
    places its target window on the wild-type boundary IN THE SAME REGISTER it occupies on the
    fusion, and counts mismatches — total, and inside the catalytic gap.

    ⛔ "LOW GAP MARGIN DECIDES" IS FALSE AT THIS SEAM, AND THE TABLE IS HOW YOU SEE IT. At
    EWSR1 e13 :: NR4A3 e2 the condemned designs are the two with <=2 DONOR bases in the gap — while
    the margin-1 design with 5 donor bases in the gap is clean. What decides is how much of the
    catalytic gap is acceptor sequence the wild-type allele also has, not the symmetric margin. And
    the liability is DONOR-SPECIFIC, not a property of the exon-2 acceptor: the same arithmetic over
    TAF15 exon 6 finds 3-7 mismatches in every register, because TAF15's 3' end does not resemble
    NR4A3 intron 1's, whereas EWSR1 exon 13's does.
    """
    if not os.path.exists(_wt.PREMRNA_CACHE):
        return {"_status": "NOT RUN — the committed pre-mRNA cache is absent. ABSENT, NOT CLEAN."}
    with open(_wt.PREMRNA_CACHE, encoding="utf-8") as fh:
        pre = json.load(fh)["genes"]["NR4A3"]["sequence"].upper()
    nr4a3 = ja.transcript_model("NR4A3")
    e1, e2 = nr4a3["exon_lens"][0], nr4a3["exon_lens"][1]
    exon2 = nr4a3["cdna"][e1:e1 + e2]
    if pre.count(exon2) != 1:
        return {"_status": "NOT RUN — NR4A3 exon 2 is not a unique substring of the committed "
                           "unspliced sequence, so the boundary offset would be ambiguous."}
    k = pre.find(exon2)
    gap_lo, gap_hi = ja.WING, ja.OLIGO_LEN - ja.WING - 1
    rows = {}
    for label, left, fusion, oligos in junction_designs:
        per = []
        for o in oligos:
            t = o["target_mRNA_5to3"]
            n_donor = len(left) - fusion.index(t)
            w = pre[k - n_donor:k - n_donor + ja.OLIGO_LEN]
            mm = [i for i, (x, y) in enumerate(zip(t, w)) if x != y]
            gap_mm = [i for i in mm if gap_lo <= i <= gap_hi]
            per.append({
                "antisense_5to3": o["antisense_5to3"],
                "gap_bases_donor_side": o["gap_bases_from_EWSR1"],
                "gap_bases_acceptor_side": o["gap_bases_from_NR4A3"],
                "fusion_target_window": t,
                "wild_type_window_same_register": w,
                "n_mismatches_vs_wild_type": len(mm),
                "mismatch_positions": mm,
                "n_gap_mismatches": len(gap_mm),
                "reading": ("⛔ cleavage-competent on the un-rearranged allele: <=2 mismatches over "
                            "the 16-mer and none in the catalytic gap"
                            if len(mm) <= 2 and not gap_mm else
                            f"no site at this register: {len(mm)} mismatches, above the <=2 ceiling "
                            "matched to the BLAST arm's >=14/16 identity" if len(mm) > 2 else
                            f"gap not fully paired ({len(gap_mm)} gap mismatch(es))"),
            })
        rows[label] = per
    return {
        "_method": (f"each design's target window placed on the wild-type NR4A3 intron-1/exon-2 "
                    f"boundary in the SAME register it occupies on its fusion; catalytic gap is "
                    f"positions {gap_lo}..{gap_hi} of the {ja.OLIGO_LEN}-mer"),
        "wild_type_boundary_unspliced_offset_0based": k,
        "wild_type_boundary_context": f"{pre[k - 8:k]}|{pre[k:k + 10]}",
        # ⛔ THIS RULE TRAVELS IN THE ARTIFACT, NOT ONLY IN THE SOURCE. It generalises to every
        # future seam at this acceptor and the margin heuristic it replaces does not, so a reader
        # holding only the JSON has to be able to see it.
        "⛔_THE_RULE_THIS_REFUTES": (
            "'LOW GAP SPECIFICITY MARGIN DECIDES' IS FALSE AT AN NR4A3 EXON-2 ACCEPTOR. That "
            "heuristic was generalised from the TAF15 intron-2 cryptic-exon seam, where the one "
            "condemned design also happened to be the lowest-margin one. Here it breaks: at "
            "EWSR1 e13 :: NR4A3 e2 the two condemned designs are those with <=2 DONOR bases inside "
            "the catalytic gap, while the margin-1 design carrying 5 donor bases in the gap is "
            "clean. WHAT DECIDES IS HOW MUCH OF THE CATALYTIC GAP IS ACCEPTOR SEQUENCE THE "
            "WILD-TYPE ALLELE ALSO CARRIES — the donor bases are the only part of the gap the "
            "un-rearranged allele does not have, so they are what the discrimination rests on. "
            "Gap specificity margin is symmetric and therefore cannot express this; the donor-side "
            "gap count can."),
        "⛔_AND_IT_IS_DONOR_SPECIFIC_NOT_A_PROPERTY_OF_THE_ACCEPTOR": (
            "The liability is not a hazard of the exon-2 acceptor as such. It exists because THIS "
            "donor's 3' end resembles NR4A3 intron 1's 3' end: both terminate in the AG that a 3' "
            "splice site must end in, and the identity extends further upstream. The identical "
            "arithmetic over TAF15 exon 6 finds 3-7 mismatches in every register and condemns "
            "nothing. So the question to ask at any new seam here is 'how much does this donor's "
            "3' end look like NR4A3 intron 1's?', measured per-donor in "
            "emc-model-junction-evidence.json -> nr4a3_wild_type_acceptor_context, and never "
            "assumed from the acceptor."),
        "⚠_scope": ("ONE register at ONE boundary — it explains the scan's verdicts, it does not "
                    "replace them. The exhaustive scan over the whole NR4A3 unspliced sequence is "
                    "the measurement; this is the mechanism behind it. Both are corroborated "
                    "independently by the exhaustive GRCh38 screen, which finds the same two "
                    "designs cleaving NR4A3 at chr9:99825651 and chr9:99825652."),
        "per_junction": rows,
    }


def _wild_type_allele_liability(designs, parents):
    """Does any design here cleave the patient's own un-rearranged NR4A3? MEASURED, locally, $0.

    ⛔ AND ITS CONTROL IS A FIXED KNOWN POSITIVE, NEVER "THE OTHER WHITELIST ENTRY". That mistake has
    already been made once in this repository and is recorded at
    `aso_taf15_intron2_designs._known_positive_control`: a control that scanned whichever junction
    was NOT being built reported itself silent while the real liability sat in the same file. The
    control used here is that module's own — TAF15 e6 :: NR4A3 intron-2 cryptic exon, design
    TGATGAGGGCCTTGTG, which the GENOME screen measured forming a gap-paired hybridisable duplex on
    chr9 in wild-type NR4A3. It is a fixed case with a known answer and it is external to every
    junction in this file, so it cannot be made vacuous by anything this module does.
    ⛔ IF THE CONTROL DOES NOT FIRE, NO 'CLEAN' VERDICT BELOW MAY BE RELIED ON.
    """
    try:
        _seam_rec, cryptic = _wt.load_seam_record()
        control = _wt._known_positive_control(cryptic, parents)
    except Exception as exc:                                          # noqa: BLE001
        control = {"_status": f"control could not be built: {exc}", "passed": None}
    scan = _wt.wildtype_nr4a3_liability(sorted(designs), None)
    per = scan.get("per_design") or {}
    hits = sorted(a for a, v in per.items()
                  if v["⛔_n_cleavage_competent_sites_in_wild_type_NR4A3"])
    return {
        "⛔_the_question": (
            "does this reagent form an RNase-H1-competent duplex on the patient's own UN-REARRANGED "
            "NR4A3 allele? The acceptor half of every design here is NR4A3 exon-2 5'UTR sequence, "
            "which in the wild-type allele sits immediately 3' of intron 1 — a compartment the "
            "spliced-cDNA parent screen cannot see, because a mature transcript has exon 1 there."),
        "⛔_a_clean_parent_screen_is_not_an_answer": (
            "every design in this module clears the parent exclusion, and that screen searches "
            "MATURE cDNA only. At the sibling cryptic-exon seam all five designs cleared it and one "
            "was then measured cleaving wild-type NR4A3."),
        "positive_control": control,
        "n_designs_scanned": len(per),
        "n_designs_cleaving_wild_type_NR4A3": len(hits),
        "designs_cleaving_wild_type_NR4A3": hits,
        "scan": scan,
    }


def build():
    geom = ass.MANUSCRIPT_GEOMETRY
    assert (ja.OLIGO_LEN, ja.WING) == (geom.oligo_len, geom.wing), (
        f"geometry drift: junction_aso is at {ja.OLIGO_LEN}-mer/wing {ja.WING}, the manuscript "
        f"panel is at {geom.oligo_len}/{geom.wing}. Designs emitted at a different geometry cannot "
        "be compared with the panel's, so this refuses rather than quietly emitting them.")

    parents = _parents()
    unavailable = sorted(s for s, v in parents.items() if not v)
    screened_against = sorted(s for s, v in parents.items() if v)
    nr4a3 = ja.transcript_model("NR4A3")

    junctions, unbuildable, register_inputs = [], [], []
    for (d_sym, d_end, a_sym, a_start), meta in PUBLISHED_NONCODING_ACCEPTOR_JUNCTIONS.items():
        label = f"{d_sym}_e{d_end}__{a_sym}_e{a_start}"
        # ⚠ A JUNCTION WHOSE TRANSCRIPT MODEL IS NOT ON DISK IS AN ABSENT READING, NOT AN ABSENT
        # JUNCTION — and it must not take the whole artifact down with it either. Before this, one
        # whitelisted partner missing from the committed cache (PGR, which needs its own CI fetch)
        # raised out of the loop, so the module could not be run in the sandbox AT ALL and the other
        # seams' designs could not be regenerated. Recorded by name, surfaced at the top level, and
        # never silently dropped: `_parents()` already applies exactly this rule to a parent it could
        # not load, and a donor deserves it more, not less.
        try:
            donor = ja.transcript_model(d_sym)
            acceptor = nr4a3 if a_sym == "NR4A3" else ja.transcript_model(a_sym)
        except Exception as exc:                                       # noqa: BLE001
            unbuildable.append({
                "junction_label": label,
                "why": f"transcript model unavailable here: {exc}",
                "⚠": ("NOT a finding about this junction. The seam was not graded, no design was "
                      "emitted, and nothing about it is cleared or refused — the model simply could "
                      "not be read in this environment. Re-run where it can be."),
                "evidence": list(meta["evidence"]),
            })
            print(f"  ⚠ {label} not buildable here: {exc}", file=sys.stderr)
            continue
        j = ja.mrna_junction_generic(donor, acceptor, d_end, a_start)

        # The two readings that make this junction the case it is, asserted rather than assumed.
        assert j["junction_label"] == f"{d_sym}_e{d_end}__{a_sym}_e{a_start}", j["junction_label"]
        # ⛔ THE JUNCTION MUST ACTUALLY BE ONE THE PANEL EXCLUDES, and for the reason claimed.
        # Without this a seam that the ordinary panel already screens could be emitted here too,
        # and the same sequence would appear in two lanes under two different levels of evidence —
        # the screened one and the unscreened one — which is exactly how an unscreened design gets
        # quoted as though it had been screened.
        grade = meta["excluded_from_the_panel_by"]
        if grade == "NON_CODING_ACCEPTOR":
            assert not j["nr4a3_acceptor_exon_is_coding"], (
                f"{j['junction_label']} has a CODING acceptor, so NON_CODING_ACCEPTOR is the wrong "
                "exclusion reason for it. Refusing to emit on a misstated grade.")
        elif grade == "OUT_OF_FRAME":
            assert not j["in_frame"], (
                f"{j['junction_label']} IS in frame, so OUT_OF_FRAME is the wrong exclusion reason "
                "for it — and an in-frame coding-acceptor junction belongs in the ordinary panel. "
                "Refusing to emit it in this lane.")
        else:
            raise AssertionError(f"unknown exclusion grade {grade!r} for {j['junction_label']}")

        oligos = ja.design(j["_left"], j["_right"], j["_fusion"],
                           parents={k: v for k, v in parents.items() if v})
        clean = [o for o in oligos if o["fusion_specific"]]
        register_inputs.append((j["junction_label"], j["_left"], j["_fusion"], oligos))
        junctions.append({
            "junction_label": j["junction_label"],
            "transcript_type": meta["transcript_type"],
            "n_independent_sources": meta["n_independent_sources"],
            "excluded_from_the_panel_by": meta["excluded_from_the_panel_by"],
            # ⚠ PRESENT ONLY WHERE THE WHITELIST NAMES ONE, AND `None` OTHERWISE RATHER THAN OMITTED:
            # a reader comparing two junction blocks must be able to see that one seam is tied to a
            # named, obtainable laboratory model and the other is not, without having to notice the
            # absence of a key.
            "model_it_makes_testable": meta.get("model_it_makes_testable"),
            "⚠_read_this_before_using_the_sequence":
                meta.get("⚠_read_this_before_using_the_sequence"),
            "evidence": meta["evidence"],
            "one_home_for_the_evidence": meta["one_home_for_the_evidence"],
            "junction_context_mRNA": j["junction_context_mRNA"],
            "acceptor_exon_is_coding": j["nr4a3_acceptor_exon_is_coding"],
            "acceptor_5utr_nt_retained": j["nr4a3_acceptor_exon_5utr_nt_retained"],
            "in_frame_at_the_mRNA_level": j["in_frame"],
            "_frame_note": (
                "reported because it is a reading, not because it gates anything here. An RNase-H "
                "gapmer cleaves the transcript; the frame decides what protein the tumour makes."),
            "n_designs_spanning_the_seam": len(oligos),
            "n_clearing_the_parent_exclusion": len(clean),
            "parents_screened": screened_against,
            "parents_unavailable": unavailable,
            "designs": [{
                "antisense_5to3": o["antisense_5to3"],
                "target_mRNA_5to3": o["target_mRNA_5to3"],
                "architecture": o["architecture"],
                "gap_specificity_margin": o["gap_specificity_margin"],
                "gap_bases_donor_side": o["gap_bases_from_EWSR1"],
                "gap_bases_acceptor_side": o["gap_bases_from_NR4A3"],
                "gc_percent": o["gc_percent"],
                "has_G4_motif": o["has_G4_motif"],
                "clears_parent_exclusion": o["fusion_specific"],
                "exact_parent_hits": o["exact_parent_hits"],
                "⚠_offtarget_screens_run": _screens_run_on(j["junction_label"]),
            } for o in oligos[:8]],
            "best_by_gap_specificity_margin": (clean[0]["antisense_5to3"] if clean else None),
        })

    # ── the wild-type-allele scan, over every design in the lane, with ONE fixed control ────────
    # ⛔ RUN AFTER THE LOOP AND ANNOTATED BACK IN, so the control is built once and every junction is
    # graded by the same invocation. `best_by_gap_specificity_margin` is then RE-DERIVED to exclude
    # any design the scan condemns: a "best" that cleaves the patient's own NR4A3 is not a best, and
    # leaving the old value beside a ⛔ verdict is exactly how a condemned sequence gets quoted.
    wt = _wild_type_allele_liability(
        [d["antisense_5to3"] for j in junctions for d in j["designs"]], parents)
    wt["⭐_why_these_and_not_the_others"] = _wild_type_register_table(register_inputs)
    condemned = set(wt["designs_cleaving_wild_type_NR4A3"])
    per_design_scan = (wt["scan"].get("per_design") or {})
    for jrec in junctions:
        for d in jrec["designs"]:
            v = per_design_scan.get(d["antisense_5to3"]) or {}
            d["⛔_cleaves_wild_type_NR4A3"] = d["antisense_5to3"] in condemned
            d["wild_type_NR4A3_verdict"] = v.get(
                "verdict", "NOT SCANNED — absent, not clean")
            d["wild_type_NR4A3_n_cleavage_competent_sites"] = v.get(
                "⛔_n_cleavage_competent_sites_in_wild_type_NR4A3")
        hit = sorted(d["antisense_5to3"] for d in jrec["designs"]
                     if d["⛔_cleaves_wild_type_NR4A3"])
        jrec["n_designs_cleaving_wild_type_NR4A3"] = len(hit)
        jrec["designs_cleaving_wild_type_NR4A3"] = hit
        usable = [d for d in jrec["designs"]
                  if d["clears_parent_exclusion"] and not d["⛔_cleaves_wild_type_NR4A3"]]
        jrec["n_clearing_parent_exclusion_AND_the_wild_type_allele"] = len(usable)
        jrec["best_by_gap_specificity_margin"] = (
            usable[0]["antisense_5to3"] if usable else None)
        jrec["_how_best_is_chosen"] = (
            "highest gap_specificity_margin among designs that clear the parent exclusion AND carry "
            "no cleavage-competent site in wild-type NR4A3. ⛔ It is NOT a recommendation: the three "
            "screens that need NCBI or the genome have their own state, reported per design in "
            "`⚠_offtarget_screens_run`.")

    return {
        "_what": ("Junction-spanning gapmer designs at NR4A3 exon-2 acceptor seams — the published "
                  "EMC breakpoints the manuscript's panel excludes by a protein-coding filter."),
        "_why": ("The EWSR1 type 2 transcript joins EWSR1 exon 7 to NR4A3 exon 2 and is reported in "
                 "at least two sequenced patients across two series. Every junction in the panel "
                 "uses NR4A3 exon 3, so no reagent in it can engage those tumours. The exclusion is "
                 "a frame/coding grade, which is the right filter for a fusion protein and the "
                 "wrong one for an RNase-H mechanism. The PGR e2 :: NR4A3 e2 seam is excluded by "
                 "the same acceptor grade AND by a second, independent gap: PGR is not one of the "
                 "five 5' partners the atlas models, so no design lane could reach that patient "
                 "even with the acceptor filter lifted. ⭐ AND THE TWO USZ SEAMS ARE HERE FOR A "
                 "THIRD REASON AGAIN: EWSR1 e13 :: NR4A3 e2 and TAF15 e6 :: NR4A3 e2 are the "
                 "junctions the two identity-clean patient-derived EMC cell models are reported to "
                 "carry, under the LITERAL reading of an acceptor exon label that has two readings "
                 "and no sequenced boundary. Designing at both acceptors — the exon-3 seams are "
                 "already in the manuscript panel and already screened — is what stops that "
                 "unresolved exon index from blocking anything: under either reading each model "
                 "then has a reagent. The ambiguity itself is carried on every junction's "
                 "`⚠_read_this_before_using_the_sequence`, not resolved here."),
        "_what_this_is_not": [
            "Not an efficacy claim and not a claim of activity. Sequence arithmetic and a "
            "parent-exclusion screen only. Nothing here has been synthesised or tested.",
            _off_target_screening_status(),
            "Not a relaxation of the coding-acceptor guard in junction_aso. That guard catches a "
            "coordinate slip and still raises; this module reaches its seams through an explicit "
            "published-breakpoint whitelist, so it cannot design at a junction nobody sequenced.",
            "Not a claim that the type 2 chimera makes a protein, or that it is oncogenic. Real "
            "questions, and not the gapmer's questions.",
        ],
        "_cost": "$0 — CPU only, committed transcript caches, no network, no GPU, no rental.",
        "geometry": {"oligo_len": ja.OLIGO_LEN, "wing": ja.WING, "gap": ja.GAP,
                     "architecture": f"{ja.WING}-{ja.GAP}-{ja.WING} (LNA-DNA-LNA)",
                     "_same_as": "aso_screen_sets.MANUSCRIPT_GEOMETRY, asserted at build time"},
        "transcript_source": ja.transcript_source_provenance(),
        "n_junctions": len(junctions),
        "junctions": junctions,
        "⭐_wild_type_NR4A3_cleavage_liability": wt,
        "n_junctions_not_buildable_in_this_environment": len(unbuildable),
        "junctions_not_buildable_in_this_environment": unbuildable,
        #: ⛔ WITHDRAWN SEAMS TRAVEL WITH THE ARTIFACT, not only with the source. A reader holding
        #: only this JSON must be able to see that a junction was removed and why — otherwise the
        #: retraction is invisible to exactly the audience that consumed the designs.
        "retracted_junctions": [
            {"junction_label": f"{d}_e{de}__{a}_e{ae}", **rec}
            for (d, de, a, ae), rec in RETRACTED_PUBLISHED_BREAKPOINTS.items()
        ],
        "what_would_make_these_usable": [
            "Run the five deep screens at these seams — the same aso-offtarget CI path the other "
            "38 junctions used. CPU and network only; no GPU, no rental.",
            "Confirm the acceptor at nucleotide resolution in any test material, exactly as §5.4 of "
            "the manuscript already requires for the exon-3 reagents.",
        ],
    }


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    art = build()
    new = json.dumps(art, indent=1, sort_keys=False, ensure_ascii=False) + "\n"
    if "--check" in argv:
        cur = open(OUT, encoding="utf-8").read() if os.path.exists(OUT) else ""
        if cur != new:
            print("aso-noncoding-acceptor-designs.json is stale; re-run without --check",
                  file=sys.stderr)
            return 1
        print("non-coding-acceptor designs artifact is current")
        return 0
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(new)
    print(f"wrote {os.path.basename(OUT)}", file=sys.stderr)
    for j in art["junctions"]:
        print(f"  {j['junction_label']}  ({j['transcript_type']}, "
              f"{j['n_independent_sources']} independent sources)", file=sys.stderr)
        print(f"    seam {j['junction_context_mRNA']}   "
              f"{j['n_clearing_the_parent_exclusion']}/{j['n_designs_spanning_the_seam']} "
              "designs clear the parent exclusion", file=sys.stderr)
        for o in j["designs"][:5]:
            print(f"      {o['antisense_5to3']}  margin={o['gap_specificity_margin']}  "
                  f"GC={o['gc_percent']}%  "
                  f"{'clean' if o['clears_parent_exclusion'] else 'HITS ' + ','.join(o['exact_parent_hits'])}",
                  file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
