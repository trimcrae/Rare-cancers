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


def build():
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

    (d_sym, d_end, a_sym, a_tag), meta = next(iter(PUBLISHED_CRYPTIC_ACCEPTOR_JUNCTIONS.items()))
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
    assert j["in_frame"], (
        "the T-N chimeric ORF does not retain the NR4A3 C-terminus, contradicting PMID 31020999's "
        "'Both T-N and T-N* encode the whole coding sequence of NR4A3'. The retrieved cryptic exon "
        "is therefore not the one the paper describes. Refusing to emit designs on it.")

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
        "_title": ("Screen-ready side atlas — the TAF15 e6 :: NR4A3-intron-2 cryptic-exon seam "
                   "ALONE, in the shape the deep off-target screens read."),
        "_read_this": (
            "⛔ NOT the manuscript panel. This file holds ONE junction, which is NOT among the 38 "
            "screened junctions in nr4a3-fusion-junction-atlas.json and whose off-target load is "
            "UNKNOWN until the five deep screens are run on it. Point a screen at this file with "
            "ATLAS_JSON=<this file>; never merge it into the panel atlas."),
        "_generated_by": os.path.basename(__file__),
        "oligo_geometry": {"length": ja.OLIGO_LEN, "wing": ja.WING, "gap": ja.GAP,
                           "architecture": f"{ja.WING}-{ja.GAP}-{ja.WING} (LNA-DNA-LNA)"},
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
        "_what": ("Junction-spanning gapmer designs at the TAF15 exon 6 :: NR4A3-intron-2 "
                  "cryptic-exon seam — the T-N isoform of TAF15::NR4A3, which the manuscript's "
                  "38-junction panel cannot express because every junction in it uses NR4A3 exon 3."),
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
            "what_would_settle_it": (
                "A TAF15::NR4A3 series that reports the acceptor per patient at nucleotide "
                "resolution. Until one exists the honest statement is: the panel covers T-N*, a "
                "second isoform exists, its prevalence among TAF15 patients is unmeasured, and a "
                "reagent for it is designed and screened so the gap is insured rather than open."),
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
    atlas, art = build()
    new = json.dumps(art, indent=1, sort_keys=False, ensure_ascii=False) + "\n"
    new_atlas = json.dumps(atlas, indent=1, sort_keys=False, ensure_ascii=False) + "\n"
    if "--check" in argv:
        stale = [p for p, want in ((OUT, new), (ATLAS_OUT, new_atlas))
                 if (open(p, encoding="utf-8").read() if os.path.exists(p) else "") != want]
        if stale:
            print(f"stale, re-run without --check: {', '.join(os.path.basename(p) for p in stale)}",
                  file=sys.stderr)
            return 1
        print("TAF15 intron-2 designs + side atlas are current")
        return 0
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(new)
    with open(ATLAS_OUT, "w", encoding="utf-8") as fh:
        fh.write(new_atlas)
    print(f"wrote {os.path.basename(OUT)} + {os.path.basename(ATLAS_OUT)}", file=sys.stderr)
    print(f"  {art['junction_label']}  ({art['transcript_type']}, "
          f"{art['n_independent_sources']} independent source)", file=sys.stderr)
    print(f"    cryptic exon {art['cryptic_exon']['length_nt']} nt "
          f"({art['cryptic_exon']['how_it_was_obtained']})", file=sys.stderr)
    print(f"    seam {art['junction_context_mRNA']}   "
          f"{art['n_clearing_the_parent_exclusion']}/{art['n_designs_spanning_the_seam']} designs "
          "clear the parent exclusion", file=sys.stderr)
    for o in art["designs"][:6]:
        print(f"      {o['antisense_5to3']}  margin={o['gap_specificity_margin']}  "
              f"GC={o['gc_percent']}%  "
              f"{'clean' if o['clears_parent_exclusion'] else 'HITS ' + ','.join(o['exact_parent_hits'])}",
              file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
