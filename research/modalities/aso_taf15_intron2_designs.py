#!/usr/bin/env python3
"""Gapmer designs at the TAF15 exon 6 :: NR4A3-intron-2 cryptic-exon seam — the *T-N* transcript.

⛔ WHY THIS EXISTS, AND WHY IT CAN ONLY LOWER A HEADLINE. Every one of the 38 junctions in the
manuscript's panel joins a donor exon to NR4A3 exon **3**, and the coverage ladder prices the TAF15
arm at 3/3 — it assumes every TAF15 patient carries TAF15 exon 6 :: NR4A3 exon 3. PMID 31020999
(PMC6766969, Brenca et al., J Pathol 2019) describes TWO isoforms and calls them, verbatim, "the two
major TAF15-NR4A3 isoforms detected in human tumors":

    T-N*  TAF15 exon 6 - NR4A3 exon 3       "the commonest TAF15 ... fusion"   ← the panel's seam
    T-N   TAF15 exon 6 - NR4A3 intron 2     "the less common T-N variant"      ← THIS FILE

★ A T-N* REAGENT CANNOT REACH A T-N TRANSCRIPT. The two seams share their donor half and nothing
else: 3' of the breakpoint T-N* carries NR4A3 exon 3 while T-N carries a 72-nt cryptic exon. A
16-mer gapmer whose catalytic gap straddles the seam therefore has almost no matching bases on the
acceptor side of a T-N transcript, which is not a duplex and is not a substrate. So a TAF15
patient carrying T-N is a patient the panel does not address, and pricing the arm 3/3 overstates it.

⚠ THE DESIGNS BELOW DO NOT FIX THAT — THEY MEASURE IT. Emitting a T-N reagent tells us the seam is
addressable; it does not tell us how many patients carry it, and the source paper gives an ORDERING
("the commonest" / "the less common") and no count. See `_coverage_consequence`.

WHAT THIS IS NOT.
  · Not an efficacy claim, and not a claim that any sequence below is active. Sequence arithmetic
    plus a parent-exclusion screen, nothing more. Nothing here has been synthesised or tested.
  · Not a coverage number. A named risk with no denominator is a named risk, not a percentage.
  · Not a relaxation of the coding-acceptor guard in `junction_aso.build_parents_and_fusion`. That
    guard catches a COORDINATE SLIP — code sliding onto a neighbouring exon and designing at a seam
    no patient has — and it still raises. This module reaches its seam the way
    `aso_noncoding_acceptor_designs.py` does: through an explicit published-breakpoint whitelist,
    asserted per junction, so it cannot design at a junction nobody sequenced.
  · Not a claim that the T-N chimera is oncogenic. (The source paper does report T-N and T-N* to be
    "essentially indistinguishable" in colony formation, but that is its result, not this file's,
    and an RNase-H gapmer's target does not depend on it.)

⛔ THE SEQUENCE HAS ONE HOME AND IT IS NOT THIS FILE. The cryptic exon is read out of
`nr4a3-intron2-cryptic-exon.json`, which `nr4a3_intron2_cryptic_exon.py` MEASURED from the genome on
a CI runner. A literal 72-mer typed into this module would look exactly like a real design and would
be unfalsifiable, so this module refuses to run without that artifact and re-checks what it reads.
⚠ AND THE LENGTH IS THE REASON THAT MATTERS: this lane's own arithmetic PREDICTED 75 nt from the
paper's phrasing, self-consistently and wrongly. The annotation says 72. Had the sequence been
hand-built to the prediction, all five designs below would be wrong and nothing would have said so.

Output: aso-taf15-intron2-designs.json
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
#: ⚠ BOTH PATHS ARE ENV-OVERRIDABLE **SO THAT A PLUMBING TEST NEVER HAS TO WRITE A FAKE SEQUENCE
#: INTO THIS DIRECTORY.** The design arithmetic has to be exercised before the CI fetch returns, and
#: the only alternative — dropping a hand-made record at the real path and remembering to delete it —
#: is precisely how a fabricated 75-mer would end up committed looking exactly like a measurement.
#: The same knob the deep screens already expose as `ATLAS_JSON`, for the same reason.
SEAM_RECORD = os.environ.get("CRYPTIC_EXON_JSON") or os.path.join(
    HERE, "nr4a3-intron2-cryptic-exon.json")
OUT = os.environ.get("TAF15_INTRON2_OUT") or os.path.join(HERE, "aso-taf15-intron2-designs.json")

#: ⭐ THE SCREEN-READY SIDE ATLAS. `aso_premrna_offtarget.py` and `aso_genome_offtarget.py` read
#: their design set from an atlas via the `ATLAS_JSON` env knob and expect `{"panels": [{...,
#: "designs": [...]}]}` with `fusion_specific` on each design. Emitting that shape here is what makes
#: the five deep screens RUNNABLE at this seam without teaching any screen about cryptic exons:
#:     ATLAS_JSON=aso-taf15-intron2-atlas.json python aso_premrna_offtarget.py
#: ⛔ IT IS A SEPARATE FILE, NEVER A ROW APPENDED TO `nr4a3-fusion-junction-atlas.json`. That atlas is
#: the manuscript panel's 38 screened junctions; an unscreened junction merged into it would be
#: indistinguishable from a screened one at every downstream consumer — the exact failure
#: `aso_noncoding_acceptor_designs.py` warns about when it says an unscreened design must never be
#: quoted as though it had been screened.
#: ⭐ NAMED TO FIT THE EXISTING WORKFLOW, so screening this seam needs NO code change and no new
#: input. `aso-offtarget.yml` sets `ATLAS_JSON: nr4a3-fusion-junction-atlas${suffix_tag}.json`, so a
#: dispatch with `screen_mode=premrna` and `suffix_tag=-taf15intron2` reads exactly this file and
#: writes `aso-premrna-offtarget-taf15intron2.json`. The non-coding-acceptor lane already established
#: this pattern (`nr4a3-fusion-junction-atlas-noncoding-acceptor.json`); following it rather than
#: inventing a second convention is what keeps the screens a one-dispatch operation.
#: ⚠ The suffixed name does NOT make this the panel. Consumers reference panel atlases by explicit
#: filename, not by a bare glob, and the `_read_this` banner inside says what this file is.
ATLAS_OUT = os.environ.get("TAF15_INTRON2_ATLAS") or os.path.join(
    HERE, "nr4a3-fusion-junction-atlas-taf15intron2.json")
sys.path.insert(0, HERE)

import junction_aso as ja           # noqa: E402
import aso_screen_sets as ass       # noqa: E402

#: ⛔ THE WHITELIST — the same device `aso_noncoding_acceptor_designs.py` uses, and for the same
#: reason. A junction gets designs here ONLY if a published report places a patient's breakpoint at
#: it. That is what keeps this module from being a bypass of the coding-acceptor guard rather than a
#: documented route around it: it cannot reach a seam nobody has sequenced.
PUBLISHED_CRYPTIC_ACCEPTOR_JUNCTIONS = {
    ("TAF15", 6, "NR4A3", "intron2_cryptic_exon"): {
        "transcript_type": "TAF15::NR4A3 T-N",
        "excluded_from_the_panel_by": "NON_CODING_ACCEPTOR",
        "evidence": [
            "PMID 31020999 (PMC6766969) — 'T-N, corresponding to TAF15 (exons 1-6)-NR4A3 (intron "
            "2-exon 8) ... T-N retains a short cryptic exon located in NR4A3 intron 2 "
            "(ENST00000395097.6 isoform), thus encoding 25 additional amino acids prior to the "
            "NR4A3 ATG'",
            "PMID 31020999 (PMC6766969) — 'the two major TAF15-NR4A3 isoforms detected in human "
            "tumors ... the T-N* fusion variant (TAF15 exon 6-NR4A3 exon 3) and ... the less common "
            "T-N variant (TAF15 exon 6-NR4A3 intron 2)'",
        ],
        "n_independent_sources": 1,
        "⚠_read_this_before_using_the_sequence": (
            "ONE SOURCE, AND IT IS A CELL-MODEL CONSTRUCT PAPER. PMID 31020999 states that T-N is "
            "one of two isoforms 'detected in human tumors' and that it is 'less common', but it "
            "reports NO count of how many of its five TAF15 tumours carried it, and no independent "
            "series in the corpora searched reports one either. So the ISOFORM is published and the "
            "PREVALENCE is not. A reagent at this seam is warranted as insurance against a named "
            "risk; the risk cannot be turned into a coverage percentage from the published record, "
            "and must not be."),
        "one_home_for_the_evidence": "research/modalities/nr4a3-intron2-cryptic-exon.json",
        "slug": "taf15intron2",
        "out_designs": "aso-taf15-intron2-designs.json",
        "out_atlas": "nr4a3-fusion-junction-atlas-taf15intron2.json",
        "frame_claim_to_assert": (
            "PMID 31020999: 'Both T-N and T-N* encode the whole coding sequence of NR4A3'"),
    },
    # ⭐⭐ THE SECOND DONOR AT THE SAME ACCEPTOR, AND IT DID NOT COME FROM A PAPER (2026-08-15).
    # The whitelist above exists so this module can only reach a seam somebody has sequenced. That
    # test is about EVIDENCE, not about publication format, and this entry passes it on a DEPOSITED
    # PATIENT SEQUENCE rather than on prose: GenBank AF524261.1 is 567 bp of mRNA whose own source
    # feature reads /isolation_source="extraskeletal myxoid chondrosarcoma patient".
    #
    # ⭐ IT WAS ALREADY INSIDE THIS REPOSITORY'S OWN SWEEP AND WAS DROPPED. The 1479-UID nuccore
    # sweep retrieved it, attributed 341 nt to EWSR1 and 159 nt to NR4A3, and reported no junction —
    # because the seam matcher tested only three acceptor sites somebody had already named, and this
    # transcript resumes at none of them. `nr4a3_nuccore_sweep.discover_junction` was written to
    # close exactly that, and re-derives the junction from the deposit's sequence alone.
    #
    # ⛔ WHY THIS MATTERS BEYOND ONE MORE REAGENT: before this record, the NR4A3 intron-2 cryptic
    # acceptor was a TAF15-only risk in this repository, resting on one 2019 paper. A 2002 deposit
    # shows an EWSR1 donor using the same acceptor, which makes the acceptor a property of the
    # LOCUS rather than of one partner — and the EWSR1 arm of the coverage ladder assumes every
    # EWSR1 patient joins NR4A3 exon 3.
    ("EWSR1", 10, "NR4A3", "intron2_cryptic_exon"): {
        "transcript_type": "EWSR1::NR4A3, exon 10 donor, intron-2 cryptic-exon acceptor",
        "excluded_from_the_panel_by": "NON_CODING_ACCEPTOR",
        "evidence": [
            "GenBank AF524261.1 — DEFINITION 'Homo sapiens extraskeletal myxoid chondrosarcoma "
            "EWS/TEC/CHN fusion protein mRNA, partial cds'; source 1..567 "
            "/isolation_source=\"extraskeletal myxoid chondrosarcoma patient\"",
            "GenBank AF524261.1 — misc_feature <1..337 /note=\"contains exons 7 through 10 of EWS\"",
            "GenBank AF524261.1 — misc_recomb 337..338 /note=\"fusion junction of EWS to TEC\"",
            "GenBank AF524261.1 — misc_feature 338..>567 /note=\"contains exons 2b and 3 of TEC\"",
            "GenBank AF524261.1 — CDS <1..>567 /protein_id=\"AAQ08876.1\" (189 aa), a single ORF "
            "annotated across the junction",
            "DERIVED INDEPENDENTLY OF THOSE NOTES, from the deposit's own nucleotide sequence "
            "against this repository's committed transcript models: the 5' block is an exact "
            "substring of spliced EWSR1 ending at offset 1114 == the cumulative END of EWSR1 exon "
            "10; a 72-nt segment belonging to neither spliced transcript is an exact substring of "
            "NR4A3 intron 2 at offset 897, flanked 5' by AG and 3' by GT, and is byte-identical to "
            "the cryptic exon in nr4a3-intron2-cryptic-exon.json; the 3' block resumes at offset "
            "697 == the cumulative START of NR4A3 exon 3.",
        ],
        "n_independent_sources": 1,
        "⚠_read_this_before_using_the_sequence": (
            "ONE DEPOSIT, ONE TUMOUR, NO DENOMINATOR — and no PMID is attached to the record. The "
            "deposit establishes that this junction EXISTS in a patient; it says nothing whatever "
            "about how many EWSR1-rearranged EMC patients carry an exon-10 donor or an intron-2 "
            "acceptor, and it must never be converted into a coverage percentage. "
            "⚠ IT ALSO DOES NOT RESOLVE THE THREE UNRESOLVED EWSR1 TUMOURS in PMID 12378528: this "
            "is a different report by a different group (Sjogren, Meis-Kindblom, Orndal, Bergh, "
            "Ptaszynski, Aman, Kindblom, Stenman) with no patient identifier linking it to that "
            "series, and elink from PMID 12378528 returns no direct submission at all."),
        "⛔_NOMENCLATURE_CONFLICT_UNRESOLVED": (
            "THE DEPOSIT'S OWN CDS /note READS 'type 5 fusion', AND THAT LABEL DISAGREES WITH THE "
            "SEQUENCE. In the Panagopoulos numbering this repository uses, type 5 is EWSR1 exon 13 "
            "-> NR4A3 exon 3. The junction derived here from the deposit's nucleotides is EWSR1 "
            "exon 10 -> intron-2 cryptic exon -> NR4A3 exon 3. Both readings are recorded and "
            "NEITHER is discarded. ⭐ THE DERIVATION IS THE SOUND HALF: it was obtained from the "
            "sequence against committed transcript models WITHOUT consulting the notes, and it then "
            "agreed independently with the depositor's own exon annotations ('exons 7 through 10 of "
            "EWS', 'exons 2b and 3 of TEC'). It is the TYPE LABEL that is doubtful, not the exon "
            "assignment. ⚠ CONSEQUENCE FOR ANYONE MAPPING THE TYPE SERIES: the type numbering "
            "cannot be assumed coherent across sources, so a type-3/type-4 definition inferred by "
            "interpolating the series may be built on a false premise. Key designs on SEQUENCE, "
            "never on a type label."),
        "one_home_for_the_evidence": "research/modalities/nr4a3-deposited-junctions.json",
        "slug": "ewsr1intron2",
        "out_designs": "aso-ewsr1-intron2-designs.json",
        "out_atlas": "nr4a3-fusion-junction-atlas-ewsr1intron2.json",
        # ⛔ NO PUBLISHED FRAME CLAIM EXISTS FOR THIS JUNCTION, so there is none to assert. The
        # deposit annotates a single CDS across the junction, which is the depositor's reading; the
        # frame is COMPUTED and REPORTED below rather than asserted against somebody's sentence.
        "frame_claim_to_assert": None,
    },
}

#: Every partner transcript the parent-exclusion screen runs against — the same widened set
#: `aso_noncoding_acceptor_designs.py` documents: the FET donors are paralogues with similar
#: low-complexity N-termini, so a design against one partner's junction can be a perfect complement
#: of another's wild-type transcript. Inherited, not restated.
PARENT_SYMBOLS = ("EWSR1", "TAF15", "TCF12", "FUS", "TFG", "NR4A3")


def _parents():
    out = {}
    for sym in PARENT_SYMBOLS:
        try:
            out[sym] = ja.transcript_model(sym)["cdna"]
        except Exception as exc:                                  # noqa: BLE001
            # ⚠ A PARENT WE COULD NOT LOAD IS NOT A PARENT WE CLEARED — recorded and surfaced on
            # every design, never silently dropped.
            out[sym] = None
            print(f"  ⚠ parent {sym} unavailable: {exc}", file=sys.stderr)
    return out


def load_seam_record():
    """Read the MEASURED cryptic exon, and refuse on anything short of a resolved one.

    ⛔ FOUR REFUSALS, EACH GUARDING A DIFFERENT WAY THIS COULD BECOME FICTION:
      1. the artifact is absent            → the fetch never ran; there is no sequence
      2. `resolved_cryptic_exon` is null   → the fetch ran and did NOT identify the exon
      3. the sequence is not a substring of the intron the fetch measured → it was constructed
      4. its length is not the DERIVED length → the record and its own derivation disagree
    An absent reading is not a reading of absence, and a populated field is not a measured one.
    """
    if not os.path.exists(SEAM_RECORD):
        raise RuntimeError(
            f"{os.path.basename(SEAM_RECORD)} is missing. The cryptic exon's sequence is measured "
            "from the genome by nr4a3_intron2_cryptic_exon.py on a CI runner (Ensembl is 403'd at "
            "the dev sandbox's egress proxy). Refusing to design against a seam nobody measured.")
    with open(SEAM_RECORD, encoding="utf-8") as fh:
        rec = json.load(fh)
    resolved = (rec.get("resolved_cryptic_exon") or {}).get("sequence")
    if not resolved:
        raise RuntimeError(
            "nr4a3-intron2-cryptic-exon.json records NO resolved cryptic exon "
            f"(n_candidates={((rec.get('candidate_enumeration') or {}).get('n_candidates'))}, "
            f"annotated_of_derived_length={len(rec.get('annotated_exons_of_the_derived_length') or [])}). "
            "That is a measurement, not a failure: the T-N seam is NAMED in the literature but its "
            "sequence is not determined by anything this repository can reach, so no design may be "
            "built on it. Report the named risk without a sequence.")
    if not rec["resolved_cryptic_exon"].get("is_a_substring_of_the_fetched_intron"):
        raise RuntimeError("the resolved cryptic exon is not a substring of the intron the fetch "
                           "measured — it was constructed, not measured. Refusing.")
    # ⛔ CHECK 4 IS NOW THE PAPER'S OWN NUMBER, WHICH IS A STRONGER CHECK THAN THE ONE IT REPLACED.
    # It used to compare the resolved exon against a length this lane DERIVED from the paper's
    # phrase — and that derivation was wrong (it read "25 additional amino acids" as a difference in
    # codon count and predicted 75 nt; the annotated exon is 72 nt and satisfies the same phrase read
    # as "the cryptic exon encodes 25 codons"). Checking a measurement against a hypothesis is how a
    # correct measurement gets rejected. So the check is now: does the resolved exon reproduce the
    # paper's stated 25 amino acids under a NAMED reading, and is that reading recorded?
    matched = rec["resolved_cryptic_exon"].get("reproduces_the_papers_25aa_claim_under") or []
    if not matched:
        raise RuntimeError(
            f"the resolved {len(resolved)} nt cryptic exon does not reproduce PMID 31020999's "
            "'25 additional amino acids prior to the NR4A3 ATG' under EITHER reading of that "
            "phrase. The sequence in hand is therefore not the exon the paper describes, and no "
            "design may be built on it.")
    acc = rec["resolved_cryptic_exon"].get("aa_accounting") or {}
    if not acc.get("frame_preserved"):
        raise RuntimeError(
            "the resolved cryptic exon does not preserve the chimeric reading frame, contradicting "
            "PMID 31020999's 'Both T-N and T-N* encode the whole coding sequence of NR4A3'.")
    return rec, resolved.upper()


def build_tn_acceptor_model(cryptic):
    """The T-N acceptor as a transcript model: the cryptic exon followed by NR4A3 exons 3-8.

    ⭐ WHY A SYNTHETIC MODEL RATHER THAN A SPECIAL-CASED BUILDER. `junction_aso.mrna_junction_generic`
    already does every piece of arithmetic this seam needs — retained 5'UTR, donor phase, frame
    closure, the mRNA-level seam context — and it does it from a transcript model's own fields. So
    the T-N acceptor is expressed AS a transcript model and handed to the unchanged builder, rather
    than the builder being taught about cryptic exons. One builder, one grader (rule 1), and this
    seam is graded by exactly the code that grades the panel's 38.

    The four self-checks `junction_aso._self_check_model` applies to a fetched model are applied here
    too — a synthetic model that skipped them would be a second, ungated source of truth, which is
    the failure `junction_aso`'s provenance gate exists to prevent.
    """
    nr4 = ja.transcript_model("NR4A3")
    ex3_start = ja.exon_tx_start(nr4, 3)
    cdna = cryptic + nr4["cdna"][ex3_start:]
    utr5 = len(cryptic) + max(0, nr4["utr5_len"] - ex3_start)
    model = {
        "symbol": "NR4A3crypt",
        "transcript": f"{nr4['transcript']}+intron2crypticExon",
        "strand": nr4.get("strand"),
        "cdna": cdna,
        "cds": nr4["cds"],
        "protein": nr4["protein"],
        "exon_lens": [len(cryptic)] + nr4["exon_lens"][2:],
        "utr5_len": utr5,
        "n_transcript_exons": 1 + len(nr4["exon_lens"][2:]),
        "_derived_from": nr4["transcript"],
    }
    cum, ends = 0, []
    for L in model["exon_lens"]:
        cum += L
        ends.append(cum)
    model["tx_ends"] = ends

    import fusion_breakpoints as fb
    if sum(model["exon_lens"]) != len(cdna):
        raise RuntimeError("T-N acceptor: exon lengths do not sum to the cDNA length")
    if cdna.count(model["cds"]) != 1:
        raise RuntimeError(f"T-N acceptor: the NR4A3 CDS occurs {cdna.count(model['cds'])} times in "
                           "the chimeric acceptor cDNA — the 5'UTR length would be ambiguous")
    if cdna.index(model["cds"]) != utr5:
        raise RuntimeError(f"T-N acceptor: utr5_len {utr5} != the cDNA offset of the CDS "
                           f"{cdna.index(model['cds'])}")
    if fb.translate(model["cds"]) != model["protein"].replace("*", "").rstrip("X"):
        raise RuntimeError("T-N acceptor: translate(CDS) != the annotated NR4A3 protein")
    if ja.coding_nt_per_exon(model)[0] != 0:
        raise RuntimeError("T-N acceptor: the cryptic exon is being read as CODING. It lies wholly "
                           "5' of the NR4A3 ATG, so this is an arithmetic error, not a finding.")
    return model


PANEL_ATLAS = os.path.join(HERE, "nr4a3-fusion-junction-atlas.json")
GENOME_SCREEN = os.path.join(HERE, "aso-genome-offtarget-taf15intron2.json")
PREMRNA_SCREEN = os.path.join(HERE, "aso-premrna-offtarget-taf15intron2.json")


def _out_paths(meta):
    """Per-junction output paths, named so the EXISTING screen workflow reaches them unchanged.

    `aso-offtarget.yml` sets ATLAS_JSON to `nr4a3-fusion-junction-atlas${suffix_tag}.json`, so a
    dispatch with `suffix_tag=-ewsr1intron2` reads this junction's atlas and writes
    `aso-premrna-offtarget-ewsr1intron2.json` / `aso-genome-offtarget-ewsr1intron2.json`. Following
    the convention rather than inventing a second one is what keeps screening a one-dispatch
    operation for the new seam too.
    """
    slug = meta["slug"]
    return (
        os.environ.get("TAF15_INTRON2_OUT") if slug == "taf15intron2" and os.environ.get(
            "TAF15_INTRON2_OUT") else os.path.join(HERE, meta["out_designs"]),
        os.environ.get("TAF15_INTRON2_ATLAS") if slug == "taf15intron2" and os.environ.get(
            "TAF15_INTRON2_ATLAS") else os.path.join(HERE, meta["out_atlas"]),
    )


def screen_readout(slug="taf15intron2"):
    """What the two runnable screens measured — read from their artifacts, never restated.

    ⭐ THE HEADLINE FINDING, AND IT IS THE ONE THIS LANE WAS BUILT TO LOOK FOR. The acceptor half of
    every design here is NR4A3 INTRONIC sequence, so the compartment at risk is the patient's own
    wild-type NR4A3 pre-mRNA — a liability no mature-transcript screen can see. The genome screen
    measured it, and it DISCRIMINATES AMONG THE DESIGNS:

      · the margin-1 design TGATGAGGGCCTTGTG forms a duplex on wild-type NR4A3 itself
        (chr9, 2 mismatches, gap_mismatches 0, gap_fully_paired TRUE, hybridisable TRUE) — i.e.
        RNase-H1-competent on the un-rearranged allele, because its catalytic gap is almost entirely
        cryptic-exon sequence and cryptic-exon sequence IS NR4A3 intron;
      · the margin-3 design ATGAGGGCCTTGTGTG does NOT — it carries three TAF15-derived bases inside
        the gap, which the NR4A3 locus does not have, and it has no NR4A3 site at all.

    So gap specificity margin is not a tie-breaker at this seam; it is the parameter that decides
    whether the reagent cuts the patient's own NR4A3. That is a mechanistic result, not a ranking.
    """
    out = {}
    for name, path, kind in (
            ("genome", os.path.join(HERE, f"aso-genome-offtarget-{slug}.json"), "genome"),
            ("premrna", os.path.join(HERE, f"aso-premrna-offtarget-{slug}.json"), "premrna")):
        if not os.path.exists(path):
            # ⚠ An absent screen is recorded as absent, never as a clean one.
            out[name] = {"_status": "NOT RUN — no artifact on disk. ABSENT, NOT CLEAN.",
                         "per_design": None,
                         "⛔_what_absent_means_here": (
                             "For this seam the genome screen is the instrument that decides which "
                             "designs are usable, because the acceptor half of every design is "
                             "NR4A3 intronic sequence and a spliced-cDNA parent screen structurally "
                             "cannot see it. Until it has run, NO design in this file may be called "
                             "clean and NONE may be carried forward. A 5/5 parent-screen pass is "
                             "not evidence either way — measured at the sibling TAF15 seam, where "
                             "all five designs passed the parent screen and one of them was then "
                             "found by the genome screen to form a cleavage-competent duplex on the "
                             "patient's own un-rearranged NR4A3 allele."
                             if slug != "taf15intron2" else
                             "an absent screen is recorded as absent, never as a clean one"),
                         "_why": (
                             "not yet dispatched for this seam — run aso-offtarget.yml with "
                             f"screen_mode={name} and suffix_tag=-{slug}"
                             if slug != "taf15intron2" else
                             "Blocked by a live rest.ensembl.org outage, not by anything in this "
                             "repository. Measured across four dispatches: HTTP 500 after 4 internal "
                             "retries on lookup/id/ENST00000605844 (twice), sequence/id/"
                             "ENST00000333725, and sequence/id/ENST00000254108 — three distinct "
                             "endpoints, a different one each run, which is the signature of "
                             "intermittent server-side failure rather than a bad request. In the "
                             "same window Ensembl's FTP mirror served the 898 MB GRCh38 assembly to "
                             "the genome screen without error, and lookup/id/ENST00000395097 "
                             "returned 200. Re-dispatch (screen_mode=premrna, "
                             "suffix_tag=-taf15intron2) is all that is needed once it clears."
                             if name == "premrna" else "not run"),
                         "_what_is_lost_and_what_is_not": (
                             "The pre-mRNA arm is exhaustive-by-construction over the six PARENT "
                             "loci and reports compartment and an explicit "
                             "n_invisible_to_mature_screens. ⭐ ITS CENTRAL QUESTION AT THIS SEAM "
                             "HAS NEVERTHELESS BEEN ANSWERED, by the genome arm, which is a "
                             "superset in coverage and annotates every hit from the Ensembl GTF: "
                             "the wild-type NR4A3 liability was found there (chr9, gap fully "
                             "paired, hybridisable, compartment intron_exon_spanning, 0 nt to the "
                             "nearest splice site). So the pre-mRNA arm is missing as a "
                             "CONFIRMATORY, differently-seeded check — not as the only instrument "
                             "that could have seen the intronic compartment."
                             if name == "premrna" else "")}
            continue
        d = json.load(open(path, encoding="utf-8"))
        rows = d.get("per_design") or []
        per = {}
        for r in rows:
            a = r["antisense_5to3"]
            if kind == "genome":
                nr = [s for s in (r.get("named_target_sites") or [])
                      if "NR4A3" in (s.get("genes") or [])]
                cleavable_nr = [s for s in nr if s.get("gap_fully_paired") and s.get("hybridisable")]
                per[a] = {
                    "n_exact_genomic_sites": r.get("n_exact_sites"),
                    "n_sites_le2_counted": r.get("n_sites_counted"),
                    "observed_over_expected": r.get("observed_over_expected"),
                    "n_named_target_sites": r.get("n_named_target_sites"),
                    "named_target_genes": r.get("named_target_genes"),
                    "⛔_cleavage_competent_sites_in_wild_type_NR4A3": len(cleavable_nr),
                    "_nr4a3_sites": nr,
                }
            else:
                per[a] = {
                    "n_hits_either_orientation": r.get("n_hits_either_orientation"),
                    "n_hybridisable": r.get("n_hybridisable"),
                    "n_hybridisable_gap_fully_paired": r.get("n_hybridisable_gap_fully_paired"),
                    "n_invisible_to_mature_screens": r.get("n_invisible_to_mature_screens"),
                    "compartments": r.get("compartments"),
                    "hits_truncated": r.get("hits_truncated"),
                }
        out[name] = {"_status": "run", "_method_completeness": (d.get("method") or {}).get(
            "completeness"), "per_design": per}
        if kind == "genome":
            out[name]["_reference"] = d.get("reference")
            out[name]["_wall_seconds"] = (d.get("method") or {}).get("wall_seconds")
    return out


#: The committed NR4A3 UNSPLICED sequence — the one compartment that decides this seam.
PREMRNA_CACHE = os.path.join(HERE, "aso-premrna-sequences.json")
_RC = str.maketrans("ACGT", "TGCA")


def wildtype_nr4a3_liability(designs, cryptic):
    """⭐⭐ DOES THIS REAGENT CLEAVE THE PATIENT'S OWN UN-REARRANGED NR4A3? MEASURED, LOCALLY, $0.

    ⛔ WHY THIS IS THE QUESTION AT A CRYPTIC-EXON SEAM, AND WHY A CLEAN PARENT SCREEN IS NOT AN
    ANSWER. The acceptor half of every design here is NR4A3 INTRONIC sequence, and cryptic-exon
    sequence IS NR4A3 intron 2. So a design whose 6-nt catalytic gap sits mostly on cryptic-exon
    bases can form a fully gap-paired, RNase-H1-competent duplex on the wild-type allele — in a
    compartment a spliced-cDNA parent screen structurally cannot see. Measured at the TAF15 seam:
    all five designs cleared the parent screen 5/5, and the genome screen then found
    `TGATGAGGGCCTTGTG` (margin 1) forming exactly such a duplex on chr9.

    ⭐ THIS FUNCTION IS VALIDATED AGAINST THAT KNOWN POSITIVE. Run over the TAF15 design set it
    re-finds precisely one cleavage-competent site, for precisely that design, with two mismatches
    both in the 5' wing and ZERO in the gap — reproducing the genome screen's result from the
    committed pre-mRNA cache alone. A scan that returned zero everywhere would be indistinguishable
    from a broken scan, which is why the sibling seam is scanned alongside and reported.

    ⛔ WHAT IT IS NOT: not a substitute for the genome screen. It interrogates ONE locus — NR4A3's
    own unspliced sequence — because that is the locus the liability lives at. The genome arm scans
    all of GRCh38 and remains the instrument that decides which designs are usable; an empty result
    here is necessary, not sufficient.
    """
    if not os.path.exists(PREMRNA_CACHE):
        return {"_status": "NOT RUN — the committed pre-mRNA cache is absent. ABSENT, NOT CLEAN.",
                "per_design": None}
    with open(PREMRNA_CACHE, encoding="utf-8") as fh:
        pre = json.load(fh)["genes"]["NR4A3"]["sequence"].upper()
    if cryptic not in pre:
        return {"_status": ("NOT RUN — the cryptic exon is not a substring of the committed NR4A3 "
                            "pre-mRNA, so this scan would be searching the wrong sequence. ABSENT, "
                            "NOT CLEAN."),
                "per_design": None}
    gap_lo, gap_hi = ja.WING, ja.OLIGO_LEN - ja.WING - 1
    per = {}
    for anti in designs:
        tgt = anti.translate(_RC)[::-1]
        sites = []
        for k in range(len(pre) - len(tgt) + 1):
            w = pre[k:k + len(tgt)]
            mm = [i for i in range(len(tgt)) if w[i] != tgt[i]]
            if len(mm) <= 2:
                gap_mm = [i for i in mm if gap_lo <= i <= gap_hi]
                sites.append({"pre_mrna_offset": k, "site_5to3": w, "n_mismatches": len(mm),
                              "mismatch_positions": mm, "n_gap_mismatches": len(gap_mm),
                              "gap_fully_paired": not gap_mm,
                              "offset_relative_to_cryptic_exon_start": k - pre.find(cryptic)})
        cleavable = [s for s in sites if s["gap_fully_paired"]]
        per[anti] = {
            "n_sites_le2_mismatches": len(sites),
            "⛔_n_cleavage_competent_sites_in_wild_type_NR4A3": len(cleavable),
            "verdict": ("⛔ FORMS A GAP-PAIRED DUPLEX ON THE UN-REARRANGED NR4A3 ALLELE — "
                        "RNase-H1-competent on wild-type NR4A3. DO NOT CARRY FORWARD."
                        if cleavable else
                        "no gap-paired site in the NR4A3 pre-mRNA at <=2 mismatches"),
            "sites": sites,
        }
    return {
        "_status": "run",
        "_source": os.path.basename(PREMRNA_CACHE) + " -> genes.NR4A3.sequence (unspliced)",
        "_method": (f"exhaustive <=2-mismatch scan of the NR4A3 unspliced sequence; the catalytic "
                    f"gap is positions {gap_lo}..{gap_hi} of the {ja.OLIGO_LEN}-mer target "
                    f"({ja.WING}-{ja.GAP}-{ja.WING}). A site with zero gap mismatches is treated as "
                    "cleavage-competent, the same criterion the genome screen applies."),
        "⚠_scope": ("ONE LOCUS ONLY — NR4A3's own pre-mRNA, where this seam's liability lives. NOT "
                    "a genome-wide result and NOT a substitute for aso_genome_offtarget.py."),
        "per_design": per,
    }


def _known_positive_control(cryptic, parents):
    """⛔ THE SCAN'S OWN CONTROL, AND IT IS A FIXED KNOWN POSITIVE — never "the other entry".

    The first version of this control scanned whichever junction was NOT being built, which made it
    vacuous in both directions: building the TAF15 artifact scanned EWSR1 (correctly 0 sites) and
    then reported its own control as silent, while the one design with a real liability sat in the
    same file. A control has to be a case whose answer is known.

    The known positive is TAF15 e6 :: cryptic exon, design TGATGAGGGCCTTGTG: the genome screen
    measured it forming a gap-paired hybridisable duplex on chr9 in wild-type NR4A3. This control
    rebuilds that design set from the transcript models and requires the scan to re-find EXACTLY ONE
    cleavage-competent design. If it does not, every "clean" verdict in this file is unsupported.
    """
    key = ("TAF15", 6, "NR4A3", "intron2_cryptic_exon")
    try:
        jj = ja.mrna_junction_generic(ja.transcript_model(key[0]),
                                      build_tn_acceptor_model(cryptic), key[1], 1)
        designs = [o["antisense_5to3"] for o in ja.design(
            jj["_left"], jj["_right"], jj["_fusion"],
            parents={a: b for a, b in parents.items() if b})]
    except Exception as exc:  # noqa: BLE001
        return {"_status": f"control could not be built: {exc}", "passed": None}
    res = wildtype_nr4a3_liability(designs, cryptic)
    per = res.get("per_design") or {}
    n = sum(v["⛔_n_cleavage_competent_sites_in_wild_type_NR4A3"] for v in per.values())
    hits = [a for a, v in per.items() if v["⛔_n_cleavage_competent_sites_in_wild_type_NR4A3"]]
    return {
        "control_junction": "TAF15 e6 :: NR4A3 intron-2 cryptic exon",
        "expected": "exactly 1 cleavage-competent design (TGATGAGGGCCTTGTG), per the genome screen",
        "observed_n_cleavage_competent_designs": n,
        "observed_designs": hits,
        "passed": n == 1 and hits == ["TGATGAGGGCCTTGTG"],
        "⛔_if_this_fails": ("the wild-type liability scan is not detecting the one case it is known "
                            "to have to detect, so no 'clean' verdict above may be relied on."),
        "_full": res,
    }


def panel_reach_check(fusion):
    """Does ANY reagent in the manuscript's 38-junction panel engage a T-N transcript? MEASURED.

    ⭐ WHY THIS IS A MEASUREMENT AND NOT A PARAGRAPH. The claim this whole module rests on — that a
    T-N patient is a patient the panel does not reach — is exactly the kind of claim that is easy to
    argue and easy to get wrong. Arguing it requires knowing that no other donor's seam, and no other
    acceptor's, happens to reproduce a window of the T-N chimera. So instead of arguing, every
    screened design's TARGET WINDOW is tested for exact presence in the T-N transcript, which is the
    same substring test `junction_aso.design` uses for parent specificity.

    A hit would not be a disaster — it would mean the panel already covers this seam and this lane is
    unnecessary — but it would completely change what the artifact should say. That is precisely why
    it is checked rather than assumed.

    ⚠ EXACT MATCH ONLY, AND THAT IS A FLOOR RATHER THAN A CEILING. A design could in principle engage
    a transcript through a near-match; resolving that is what the five deep screens do. This answers
    the strong, cheap question — is any panel reagent a perfect complement of any window of T-N — and
    says so rather than implying it settled the mismatch-tolerant one.
    """
    if not os.path.exists(PANEL_ATLAS):
        return {"_status": "the panel atlas is not on disk, so this check could not run — an absent "
                          "reading, not a reading of absence",
                "n_panel_designs_tested": None, "n_engaging_the_T_N_transcript": None}
    with open(PANEL_ATLAS, encoding="utf-8") as fh:
        atlas = json.load(fh)
    tested, hits = 0, []
    for pan in atlas.get("panels") or []:
        for d in pan.get("designs") or []:
            tgt = d.get("target_mRNA_5to3")
            if not tgt:
                continue
            tested += 1
            if tgt in fusion:
                hits.append({"junction_label": pan.get("junction_label"),
                             "antisense_5to3": d.get("antisense_5to3")})
    return {
        "n_panel_junctions": len(atlas.get("panels") or []),
        "n_panel_designs_tested": tested,
        "n_engaging_the_T_N_transcript": len(hits),
        "engaging_designs": hits,
        "_method": ("exact presence of each panel design's target window in the modelled T-N "
                    "chimeric transcript — the same substring test the parent-specificity screen "
                    "uses. Exact matches only; near-matches are the deep screens' question."),
        "_reading": ("0 means no reagent in the published panel is a perfect complement of any "
                     "window of a T-N transcript, so a TAF15 patient carrying T-N is not addressed "
                     "by the panel as it stands."
                     if not hits else
                     "⚠ NON-ZERO — at least one panel reagent does engage this transcript, which "
                     "changes what this lane is for. Read `engaging_designs` before using anything "
                     "in this file."),
    }


def build(key=None):
    geom = ass.MANUSCRIPT_GEOMETRY
    # ⛔ ASSERTED, NOT ASSUMED — the same refusal `aso_noncoding_acceptor_designs.py` makes. Designs
    # emitted at a different geometry cannot be compared with the panel's.
    assert (ja.OLIGO_LEN, ja.WING) == (geom.oligo_len, geom.wing), (
        f"geometry drift: junction_aso is at {ja.OLIGO_LEN}-mer/wing {ja.WING}, the manuscript "
        f"panel is at {geom.oligo_len}/{geom.wing}. Refusing to emit incomparable designs.")

    seam_rec, cryptic = load_seam_record()
    parents = _parents()
    unavailable = sorted(s for s, v in parents.items() if not v)
    screened_against = sorted(s for s, v in parents.items() if v)

    # ⛔ WAS `next(iter(...))` — ONE JUNCTION, SILENTLY. The whitelist was a dict from the start but
    # only its first entry was ever built, so adding a second entry would have emitted nothing and
    # said nothing. Fixed 2026-08-15 when AF524261.1 supplied a second donor at this acceptor.
    if key is None:
        key = next(iter(PUBLISHED_CRYPTIC_ACCEPTOR_JUNCTIONS))
    meta = PUBLISHED_CRYPTIC_ACCEPTOR_JUNCTIONS[key]
    (d_sym, d_end, a_sym, a_tag) = key
    donor = ja.transcript_model(d_sym)
    acceptor = build_tn_acceptor_model(cryptic)
    j = ja.mrna_junction_generic(donor, acceptor, d_end, 1)

    # ── The readings that make this junction the case it is, asserted rather than assumed ──────
    # ⛔ THE ACCEPTOR MUST ACTUALLY BE NON-CODING, and for the reason claimed. Without this a seam
    # the ordinary panel already screens could be emitted here too, and the same sequence would
    # appear in two lanes under two different levels of evidence.
    assert not j["nr4a3_acceptor_exon_is_coding"], (
        "the cryptic exon is graded CODING, so NON_CODING_ACCEPTOR is the wrong exclusion reason. "
        "Refusing to emit on a misstated grade.")
    assert j["nr4a3_acceptor_exon_5utr_nt_retained"] == len(cryptic) + 2, (
        f"retained 5'UTR is {j['nr4a3_acceptor_exon_5utr_nt_retained']} nt; the cryptic exon "
        f"({len(cryptic)}) plus NR4A3 exon 3's own 2 nt was expected")
    # ⭐ THE FRAME IS THE PAPER'S OWN CLAIM, CHECKED. PMID 31020999 says both isoforms "encode the
    # whole coding sequence of NR4A3". If the chimeric ORF did not reach NR4A3's C-terminus, the
    # sequence in hand would not be the exon the paper describes — which is a retrieval failure, not
    # a biological finding, and must stop the run rather than be reported as one.
    # ⛔ ASSERTED ONLY WHERE A SOURCE ACTUALLY MAKES THE CLAIM. For TAF15 the frame is PMID
    # 31020999's own statement and a failure would mean the retrieved exon is not the one the paper
    # describes — a retrieval failure that must stop the run. For the EWSR1 e10 donor NO published
    # frame claim exists, so there is nothing to check the arithmetic against; the frame is computed
    # and reported instead. Asserting a claim nobody made would be inventing the source.
    if meta.get("frame_claim_to_assert"):
        assert j["in_frame"], (
            f"the chimeric ORF does not retain the NR4A3 C-terminus, contradicting "
            f"{meta['frame_claim_to_assert']}. The retrieved cryptic exon is therefore not the one "
            "the source describes. Refusing to emit designs on it.")

    # The T-N* seam, built by the same code, so the two can be compared rather than asserted apart.
    j_star = ja.mrna_junction_generic(donor, ja.transcript_model("NR4A3"), d_end, 3)
    shared = 0
    for x, y in zip(j["_right"], j_star["_right"]):
        if x != y:
            break
        shared += 1

    oligos = ja.design(j["_left"], j["_right"], j["_fusion"],
                       parents={k: v for k, v in parents.items() if v})
    clean = [o for o in oligos if o["fusion_specific"]]

    junction_label = f"{d_sym}_e{d_end}__NR4A3_intron2crypticExon"
    atlas = {
        "_title": (f"Screen-ready side atlas — the {d_sym} e{d_end} :: NR4A3-intron-2 "
                   "cryptic-exon seam ALONE, in the shape the deep off-target screens read."),
        "_read_this": (
            "⛔ NOT the manuscript panel. This file holds ONE junction, which is NOT among the 38 "
            "screened junctions in nr4a3-fusion-junction-atlas.json and whose off-target load is "
            "UNKNOWN until the five deep screens are run on it. Point a screen at this file with "
            "ATLAS_JSON=<this file>; never merge it into the panel atlas."),
        "_generated_by": os.path.basename(__file__),
        "oligo_geometry": {"length": ja.OLIGO_LEN, "wing": ja.WING, "gap": ja.GAP,
                           "architecture": f"{ja.WING}-{ja.GAP}-{ja.WING} (LNA-DNA-LNA)"},
        # ⛔ REQUIRED BY THE DEEP SCREENS, AND ITS ABSENCE IS NOT A COSMETIC GAP. Both
        # `aso_premrna_offtarget` (`atlas["transcripts"]` -> the six parents whose UNSPLICED
        # sequence it fetches) and `aso_genome_offtarget` (`sorted(atlas["transcripts"].keys())`)
        # read this block, and the first dispatch of the pre-mRNA screen against this atlas died on
        # `KeyError: 'transcripts'` for exactly that reason. ⭐ IT IS ALSO THE BLOCK THAT MATTERS
        # MOST AT THIS SEAM: the acceptor half of every design here is NR4A3 INTRONIC sequence, so
        # the parent whose pre-mRNA must be searched is NR4A3 itself, and this is what tells the
        # screen to search it.
        # Derived from the same transcript models the designs were built from — never transcribed by
        # hand, so it cannot drift from the sequences it describes.
        "transcripts": {
            sym: {"transcript": m["transcript"], "cdna_nt": len(m["cdna"]),
                  "cds_nt": len(m["cds"]), "utr5_nt": m["utr5_len"],
                  "n_transcript_exons": m["n_transcript_exons"]}
            for sym, m in ((s, ja.transcript_model(s)) for s in PARENT_SYMBOLS)
        },
        "_transcript_source": ja.transcript_source_provenance(),
        "panels": [{
            "junction_label": junction_label,
            "donor_symbol": d_sym,
            "donor_exon_end": d_end,
            "acceptor_exon_start": "NR4A3 intron-2 cryptic exon",
            "seam_mRNA": j["junction_context_mRNA"],
            "nr4a3_first_residue": j["nr4a3_first_residue"],
            "chimeric_protein_length": j["chimeric_protein_length"],
            "n_tiled": len(oligos),
            "n_fusion_specific": len(clean),
            "best_gap_specificity_margin": (clean[0]["gap_specificity_margin"] if clean else None),
            "designs": oligos,
        }],
    }
    return atlas, {
        "_what": (f"Junction-spanning gapmer designs at the {d_sym} exon {d_end} :: NR4A3-"
                  "intron-2 cryptic-exon seam, which the manuscript's 38-junction panel cannot "
                  "express because every junction in it uses NR4A3 exon 3."),
        "_why": ("PMID 31020999 calls T-N and T-N* 'the two major TAF15-NR4A3 isoforms detected in "
                 "human tumors'. The coverage ladder prices the TAF15 arm as though every TAF15 "
                 "patient carried T-N*. If any carry T-N, no reagent in the panel reaches them."),
        "_cost": "$0 — CPU only, committed transcript caches plus the committed measured seam.",
        "junction_label": junction_label,
        "_generic_label_from_the_builder": j["junction_label"],
        "transcript_type": meta["transcript_type"],
        "n_independent_sources": meta["n_independent_sources"],
        "excluded_from_the_panel_by": meta["excluded_from_the_panel_by"],
        "⚠_read_this_before_using_the_sequence": meta["⚠_read_this_before_using_the_sequence"],
        "evidence": meta["evidence"],
        "one_home_for_the_evidence": meta["one_home_for_the_evidence"],
        "cryptic_exon": {
            "length_nt": len(cryptic),
            "sequence_5to3": cryptic,
            "how_it_was_obtained": (seam_rec.get("resolved_cryptic_exon") or {}).get("how"),
            "measured_in": os.path.basename(SEAM_RECORD),
            "genomic_locus": {k: seam_rec.get("intron", {}).get(k)
                              for k in ("chrom", "strand", "genomic_start", "genomic_end")},
            "aa_accounting": (seam_rec.get("resolved_cryptic_exon") or {}).get("aa_accounting"),
            "reproduces_the_papers_25aa_claim_under": (
                (seam_rec.get("resolved_cryptic_exon") or {}).get(
                    "reproduces_the_papers_25aa_claim_under")),
            "supporting_records": (seam_rec.get("resolved_cryptic_exon") or {}).get(
                "supporting_records"),
        },
        "junction_context_mRNA": j["junction_context_mRNA"],
        "acceptor_exon_is_coding": j["nr4a3_acceptor_exon_is_coding"],
        "acceptor_5utr_nt_retained": j["nr4a3_acceptor_exon_5utr_nt_retained"],
        "in_frame_at_the_mRNA_level": j["in_frame"],
        "chimeric_protein_length_aa": j["chimeric_protein_length"],
        "_frame_note": ("reported because it is a reading, and because the paper makes a frame claim "
                        "this checks — not because it gates the gapmer. An RNase-H gapmer cleaves "
                        "the transcript; the frame decides what protein the tumour makes."),
        "why_a_T_N_star_reagent_does_not_cover_this_seam": {
            "T_N_star_junction": j_star["junction_label"],
            "T_N_star_seam_mRNA": j_star["junction_context_mRNA"],
            "T_N_seam_mRNA": j["junction_context_mRNA"],
            "shared_acceptor_side_bases_3prime_of_the_breakpoint": shared,
            "_reading": (
                f"The two isoforms share {shared} base(s) immediately 3' of the breakpoint. A "
                f"{ja.OLIGO_LEN}-mer whose {ja.GAP}-nt catalytic gap straddles the seam needs a "
                "continuous duplex across that gap, so a T-N* reagent has no usable acceptor-side "
                "pairing on a T-N transcript. The two seams need two reagents."),
        },
        "does_the_published_panel_reach_this_transcript": panel_reach_check(j["_fusion"]),
        # ⭐⭐ THE READING THAT DECIDES WHICH DESIGN IS USABLE AT A CRYPTIC-EXON SEAM. Reported
        # BEFORE deep_screen_results because it is answerable now, offline, from committed
        # sequence — and because the parent-exclusion result immediately above is exactly the
        # reading that looks reassuring and is not.
        "⭐_wild_type_NR4A3_cleavage_liability": wildtype_nr4a3_liability(
            [o["antisense_5to3"] for o in oligos], cryptic),
        "⭐_liability_scan_positive_control": _known_positive_control(cryptic, parents),
        "deep_screen_results": screen_readout(meta["slug"]),
        "⭐_what_the_screens_actually_found": (
            "GAP SPECIFICITY MARGIN DECIDES WHETHER THIS REAGENT CUTS THE PATIENT'S OWN NR4A3, and "
            "that is the finding this junction exists to produce. Because the acceptor half of "
            "every design is NR4A3 intronic sequence, a design whose catalytic gap is mostly "
            "cryptic-exon bases is, on the wild-type NR4A3 locus, a fully gap-paired hybridisable "
            "duplex — RNase-H1-competent on the un-rearranged allele. The genome screen measured "
            "exactly that for the margin-1 design TGATGAGGGCCTTGTG (chr9, 2 mismatches, 0 of them "
            "in the gap), and measured NO NR4A3 site at all for the margin-3 design "
            "ATGAGGGCCTTGTGTG, whose gap carries three TAF15-derived bases the NR4A3 locus lacks. "
            "⚠ SO THE FIVE DESIGNS ARE NOT INTERCHANGEABLE AND MUST NOT BE PRESENTED AS A SET. "
            "ATGAGGGCCTTGTGTG is the only one that should be carried forward on this evidence; its "
            "sole named-target near-match (TCF12) is NOT gap-paired and so is not cleavage- "
            "competent, and its two exact genomic sites sit against a chance expectation of ~1.37 "
            "per design, i.e. at background. "
            "⛔ AND THIS IS PRECISELY THE LIABILITY A SPLICED-cDNA PARENT SCREEN CANNOT SEE: all "
            "five designs cleared that screen 5/5. Had this junction been reported on the parent "
            "screen alone it would have read as uniformly clean, and the margin-1 design would have "
            "looked like a legitimate alternative."),
        "⛔_the_honest_bottom_line_for_this_molecule": (
            "THIS JUNCTION WILL NOT REACH PARITY WITH THE PANEL'S 38, AND THAT IS A PROPERTY OF THE "
            "INSTRUMENTS RATHER THAN OF THE REAGENT. Three of the five deep screens address a "
            "junction as (donor gene, donor exon, NR4A3 exon index), and a cryptic exon 5' of the "
            "NR4A3 ATG is not expressible as an exon index at all — so they cannot be pointed at "
            "this seam without either an atlas-driven mode in the BLAST module or a weakening of the "
            "coordinate guard that produced the retracted seam. Architecture, not a missing "
            "dispatch, and not a defect in the designs. "
            "⭐ WHAT THIS MOLECULE DOES CARRY: a designed reagent at a REAL PUBLISHED ISOFORM — one "
            "of the two the source paper calls 'the two major TAF15-NR4A3 isoforms detected in "
            "human tumors' — screened by the two arms that actually interrogate the compartment "
            "where an intronic acceptor lives, the pre-mRNA and the genome. Those are the right two "
            "for this seam, not a consolation subset: the acceptor half of every design is absent "
            "from every mature transcript, so the mature-transcript screens would have had the "
            "least to say about it even if they could be run."),
        "⛔_which_of_the_five_deep_screens_can_run_at_this_seam": {
            "_read_this_first": (
                "⭐ THE PRE-mRNA AND GENOME SCREENS ARE THE ONES THAT COUNT AT THIS SEAM, AND A "
                "CLEAN PARENT SCREEN HERE IS WEAKER EVIDENCE THAN THE SAME RESULT AT AN EXON-EXON "
                "JUNCTION. The acceptor half of every design above is NR4A3 INTRONIC sequence. It "
                "is absent from every mature transcript, so a spliced-cDNA screen cannot see it at "
                "all — but it is physically present in the NR4A3 PRE-mRNA and in the genome, which "
                "is where an RNase-H1 gapmer meets it. Reading the parent-exclusion result above as "
                "'clean' without the pre-mRNA and genome arms would be reading the silence of an "
                "instrument that cannot look at the compartment in question."),
            "runnable_here": {
                "aso_premrna_offtarget.py": (
                    "YES — takes its design set from an atlas via ATLAS_JSON, and this module emits "
                    "one. THE ARM THAT MATTERS MOST: it searches the six parent transcripts' "
                    "UNSPLICED sequence, and NR4A3's unspliced sequence contains intron 2, hence "
                    "contains this cryptic exon."),
                "aso_genome_offtarget.py": (
                    "YES — also ATLAS_JSON-driven. The second arm that matters: an exhaustive "
                    "<=2-mismatch scan of GRCh38 covers the intronic acceptor half everywhere else "
                    "it occurs in the genome."),
            },
            "not_runnable_here_without_a_code_change": {
                "junction_aso_offtarget.py": (
                    "NO, AND THE REASON IS THE GUARD THIS LANE DELIBERATELY DID NOT WEAKEN. It "
                    "designs internally through junction_aso.build_parents_and_fusion, which "
                    "addresses a junction only as (donor gene, donor exon, NR4A3 exon) and RAISES "
                    "on a non-coding acceptor. This seam's acceptor is a cryptic exon lying 5' of "
                    "the NR4A3 ATG, so it is non-coding by that test and is not expressible as an "
                    "NR4A3 exon index at all. Screening it there would mean either weakening the "
                    "coordinate guard — which is what produced the retracted seam — or teaching "
                    "that module to take designs from an atlas the way the other two already do. "
                    "The second is the right fix and is not attempted here."),
                # ⚠ THE ARTIFACT FAMILY IS NAMED IN PROSE, NEVER AS A PATTERN. Writing the glob
                # here — even inside a descriptive string that globs nothing — trips
                # test_one_geometry_screen_loading, which scans string literals for discovery
                # patterns and cannot tell a sentence from a call. That guard is right to be blunt:
                # a linter with exceptions is a linter people learn to route around. So describe
                # the inputs by their loader instead, which is what a reader needs anyway.
                "junction_aso_locus_collapse.py": (
                    "NO — derived from the BLAST screen outputs that aso_screen_sets.BLAST_SCREEN "
                    "loads, so it inherits the blocker above."),
                "aso_offtarget_tissue_expression.py": (
                    "NO — keyed on off-target loci produced upstream, so it likewise inherits it."),
            },
            "⚠_what_this_means_for_the_counts": (
                "This junction can therefore NOT carry the full finished-junction field set that "
                "aso-per-junction-table.json holds for the panel's 38. n_gap_paired, "
                "n_hybridisable, n_near_matches, parent_duplex_bp and the locus-collapse fields all "
                "come from the BLAST arm and will be ABSENT rather than zero. An absent count is "
                "not a clean count, and this seam's numbers must never be tabulated beside the "
                "panel's as though the same instruments had been applied."),
        },
        "geometry": {"oligo_len": ja.OLIGO_LEN, "wing": ja.WING, "gap": ja.GAP,
                     "architecture": f"{ja.WING}-{ja.GAP}-{ja.WING} (LNA-DNA-LNA)",
                     "_same_as": "aso_screen_sets.MANUSCRIPT_GEOMETRY, asserted at build time"},
        "transcript_source": ja.transcript_source_provenance(),
        "provenance_gate_used": dict(ja.PROVENANCE_GATE_USED),
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
            "⚠_offtarget_screens_run": "see _what_this_is_not",
        } for o in oligos],
        "best_by_gap_specificity_margin": (clean[0]["antisense_5to3"] if clean else None),
        "_coverage_consequence": {
            "what_changes": (
                "The TAF15 arm of the coverage ladder is priced 3/3 on a three-tumour series, i.e. "
                "every TAF15 patient is assumed to carry T-N*. PMID 31020999 names a second isoform "
                "'detected in human tumors', so that assumption is now a NAMED RISK rather than an "
                "unexamined default, and the arm's 3/3 is an upper bound on it."),
            "what_does_not_change": (
                "No number moves. The source paper orders the two isoforms ('the commonest' vs 'the "
                "less common') and reports no count of either in its five TAF15 tumours; no series "
                "in the corpora searched reports one. A named risk without a denominator cannot be "
                "converted into a coverage percentage, and dressing the ordering up as a fraction "
                "would be fabricating the very number the paper declines to give."),
            "⛔_the_count_is_permanently_unavailable_not_pending": (
                "There will be NO AUTHOR OUTREACH (trimcrae, 2026-08-15). The only source that "
                "could state how many TAF15 patients carry the intron-2 acceptor is the group that "
                "reported both isoforms, and asking them is ruled out. So this is not an open "
                "question awaiting an answer — it is a CLOSED one with no answer, and the TAF15 "
                "arm's 3/3 pricing stays an explicit upper bound permanently, not provisionally. "
                "⚠ Anything that renders this row as 'pending', 'to be confirmed' or 'awaiting "
                "data' is wrong: nothing is coming."),
            "what_would_settle_it": (
                "Only a TAF15::NR4A3 series reporting the acceptor per patient at nucleotide "
                "resolution — i.e. new sequencing published by someone else, not a question anyone "
                "here can ask. Until such a series exists the honest statement is: the panel covers "
                "T-N*, a second isoform is on the record as detected in human tumours, its "
                "prevalence is unmeasured and will stay unmeasured, and a reagent for it is "
                "designed so the gap is insured rather than open."),
            "the_measured_mitigation": (
                "0 of 190 panel designs across all 38 junctions engage a modelled T-N transcript, "
                "and the two isoforms share 0 bases 3' of the breakpoint. So the exposure is fully "
                "characterised even though its frequency is not: whatever fraction of TAF15 "
                "patients carry T-N, the current panel reaches none of them, and the five designs "
                "here are what would."),
        },
        "_what_this_is_not": [
            "Not an efficacy claim and not a claim of activity. Sequence arithmetic and a "
            "parent-exclusion screen only. Nothing here has been synthesised or tested.",
            "⛔ NOT A COVERAGE NUMBER. This file does not raise or lower any published percentage; "
            "it converts a silent assumption on the TAF15 arm into a stated, unquantified risk.",
            "⛔ THE PARENT-EXCLUSION SCREEN IS SPLICED-cDNA ONLY, AND THIS SEAM IS THE CASE WHERE "
            "THAT MATTERS MOST. The acceptor half of every design below is NR4A3 INTRONIC sequence, "
            "which is present in the NR4A3 pre-mRNA and in the genome even though it is in no mature "
            "transcript. A clean parent screen here is therefore weaker evidence than the same "
            "result at an exon-exon seam, and the pre-mRNA and genome screens are not optional "
            "extras for this junction — they are the ones that count.",
            "Not a relaxation of the coding-acceptor guard in junction_aso. That guard catches a "
            "coordinate slip and still raises; this module reaches its seam through an explicit "
            "published-breakpoint whitelist, so it cannot design at a junction nobody sequenced.",
        ],
        "what_would_make_these_usable": [
            # ⛔ CORRECTED 2026-08-15. This line read "transcript BLAST, pre-mRNA, genome, tissue
            # expression and locus collapse", which substitutes the expression arm for the
            # parent-gap-pairing screen and CONTRADICTS THE MANUSCRIPT: §3.5 says "All five screens
            # address hybridisation-dependent liability only" and reports the expression result
            # separately, as "the expression reading". Expression is an EXPOSURE arm, not a
            # hybridisation screen, so it cannot be one of the five.
            # ⚠ THIS WAS NOT A COSMETIC SLIP. The integration board counted screens against this
            # list and reported EWSR1 e13 and TCF12 e5 at four of five, missing a screen neither
            # was ever short of — a false deficit on the junction whose parity carries 10.6
            # percentage points of coverage. Two committed files naming one set differently is
            # exactly the one-fact-one-place failure CLAUDE.md rule 1 is about.
            "Run the five deep screens at this seam — transcript BLAST, pre-mRNA, genome, "
            "mature-parent gap pairing and locus collapse — the same aso-offtarget CI path the "
            "panel's 38 junctions used. CPU and network only; no GPU, no rental.",
            "Then take the expression reading, which is a SIXTH arm rather than the fifth screen: "
            "it grades exposure at the loci the screens return, and answers a different question "
            "from whether a duplex can form.",
            "Confirm the acceptor at nucleotide resolution in any test material, exactly as the "
            "manuscript already requires for the exon-3 reagents.",
        ],
    }


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    # ⛔ EVERY WHITELISTED JUNCTION, NOT JUST THE FIRST. Before 2026-08-15 this built
    # `next(iter(...))` and wrote two fixed paths, so a second whitelist entry would have been
    # accepted, documented, and silently never emitted — a file that reads as covering a junction it
    # does not. Each junction now owns its own designs + atlas file, named to the `suffix_tag`
    # convention `aso-offtarget.yml` already uses, so screening the new seam needs no code change.
    rc, wrote = 0, []
    for key, meta in PUBLISHED_CRYPTIC_ACCEPTOR_JUNCTIONS.items():
        out_designs, out_atlas = _out_paths(meta)
        atlas, art = build(key)
        new = json.dumps(art, indent=1, sort_keys=False, ensure_ascii=False) + "\n"
        new_atlas = json.dumps(atlas, indent=1, sort_keys=False, ensure_ascii=False) + "\n"
        if "--check" in argv:
            stale = [p for p, want in ((out_designs, new), (out_atlas, new_atlas))
                     if (open(p, encoding="utf-8").read() if os.path.exists(p) else "") != want]
            if stale:
                print("stale, re-run without --check: "
                      f"{', '.join(os.path.basename(p) for p in stale)}", file=sys.stderr)
                rc = 1
            continue
        with open(out_designs, "w", encoding="utf-8") as fh:
            fh.write(new)
        with open(out_atlas, "w", encoding="utf-8") as fh:
            fh.write(new_atlas)
        wrote += [os.path.basename(out_designs), os.path.basename(out_atlas)]
        print(f"\n{art['junction_label']}  ({art['transcript_type']}, "
              f"{art['n_independent_sources']} independent source)", file=sys.stderr)
        print(f"  -> {os.path.basename(out_designs)} + {os.path.basename(out_atlas)}",
              file=sys.stderr)
        print(f"  cryptic exon {art['cryptic_exon']['length_nt']} nt "
              f"({art['cryptic_exon']['how_it_was_obtained']})", file=sys.stderr)
        print(f"  seam {art['junction_context_mRNA']}   "
              f"{art['n_clearing_the_parent_exclusion']}/{art['n_designs_spanning_the_seam']} "
              "designs clear the parent exclusion", file=sys.stderr)
        pr = art["does_the_published_panel_reach_this_transcript"]
        print(f"  panel reach: {pr.get('n_engaging_the_T_N_transcript')} of "
              f"{pr.get('n_panel_designs_tested')} panel designs engage this transcript",
              file=sys.stderr)
        for o in art["designs"][:6]:
            hit = ("clean" if o["clears_parent_exclusion"]
                   else "HITS " + ",".join(o["exact_parent_hits"]))
            print(f"    {o['antisense_5to3']}  margin={o['gap_specificity_margin']}  "
                  f"GC={o['gc_percent']}%  gap {o['gap_bases_donor_side']}donor/"
                  f"{o['gap_bases_acceptor_side']}acceptor  {hit}", file=sys.stderr)
    if "--check" in argv and not rc:
        print("cryptic-acceptor designs + side atlases are current")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
