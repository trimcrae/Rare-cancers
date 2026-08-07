#!/usr/bin/env python3
"""
The EWSR1::NR4A3 HYBRID INTRON as a fusion-exclusive oligonucleotide target — is the premise true?

WHY THIS EXISTS. `emc-unexplored-treatment-lanes.md` §3.5 ranks the hybrid intron #5 of the
unexplored lanes on one premise, quoted verbatim:

    "the fusion pre-mRNA has a second unique feature that is far larger: the hybrid intron,
     EWSR1 intron 7's 5' portion joined to NR4A3 intron 2's 3' portion. That sequence exists in
     no other transcript in the body. ... there are kilobases of it."

That premise is what makes the lane interesting, because the exon-junction gapmer route was
REFUTED on 2026-08-06 for the opposite reason — it has only ~20 nt of fusion-unique sequence, and
the corrected screen returned `n_oligos_no_true_cleavage_risk = 0` at BOTH graded junctions
(`junction-aso-offtarget-e7n3.json`, `junction-aso-offtarget-e12n3.json`). If the intron really
carried kilobases of fusion-exclusive target, it would attack exactly that weakness.
⚠ §3.5 attributes the failure to a "GC-rich" seam. That is the CODON-SPACE modelled breakpoint, not
the graded junctions — `composition_is_not_the_binding_constraint()` below reads the committed
panels against this repository's own favourable GC band and finds them mostly inside it, and still
zero clean. Do not repeat the GC framing as if it described the graded seams.

WHAT THIS MODULE DOES. It grades the premise instead of assuming it, in two modes:

  offline (default) — everything decidable from committed artifacts and from the repo's own
      screening code, with NO network. This is where the load-bearing result is, because the
      premise fails on an identity rather than on a measurement.
  ci      — the measured half: Ensembl genomic coordinates and the two intron sequences, the
      hybrid intron built per modelled breakpoint, its fusion-unique extent measured against BOTH
      parent loci, seam gapmers tiled by `junction_aso.design` (the same tiler, unchanged), and
      the SAME off-target screen the exon-junction panel ran. Needs the network; the dev sandbox's
      egress proxy refuses `rest.ensembl.org` (CONNECT 403, re-measured 2026-08-07), so it runs on
      a GitHub-hosted runner — `.github/workflows/aso-offtarget.yml`, input `hybrid_intron`.

⛔ THE COORDINATE CONVENTION IS THE FIRST THING THIS FILE FIXES, BECAUSE THE LANE HAS BEEN BURNED
   TWICE BY EXACTLY THIS. `junction_aso.py`'s two-defect block records both: (1) a table keyed by
   CODING exon indexed with a TRANSCRIPT exon number, which addressed NR4A3 coding exon 3 where
   transcript exon 3 was meant and produced the retracted seam; (2) a CDS-to-CDS concatenation that
   discarded the 2 nt of NR4A3 5'UTR the fusion transcript retains. So:

     "NR4A3 intron 2" HERE MEANS the intron immediately 5' of TRANSCRIPT exon 3 of ENST00000395097.
     "EWSR1 intron 7" HERE MEANS the intron immediately 3' of TRANSCRIPT exon 7 of ENST00000397938.

   NR4A3 transcript exons 1 and 2 carry no coding sequence, so transcript exon 3 IS coding exon 1;
   naming the same intron by CODING rank would give "NR4A3 intron 4" and address a different piece
   of DNA. EWSR1 transcript exon 1 is coding, so there rank == coding index and the hazard does not
   arise — which is precisely why the 2026-08-06 defect reproduced correctly on the EWSR1 side and
   was invisible for a month. `coordinate_convention()` re-derives both facts from the committed
   `emc-construct-inputs.json` + `nr4a3-exon-audit.json` and RAISES on any disagreement; it does
   not restate them from memory.

Outputs: hybrid-intron-model.json
"""

import json
import os
import sys
import time

import junction_aso as ja
import junction_aso_offtarget as jao

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "hybrid-intron-model.json")

ENS = "https://rest.ensembl.org"

# The two introns the lane names, addressed in TRANSCRIPT-exon rank (see the module header).
EWSR1_DONOR_EXON = int(os.environ.get("EWSR1_EXON_END") or 7)      # intron 3' of this exon
NR4A3_ACCEPTOR_EXON = int(os.environ.get("NR4A3_EXON_START") or 3)  # intron 5' of this exon

# Where in each intron the genomic breakpoint is MODELLED. A translocation breakpoint is the
# position of a DNA double-strand break; it is not fixed by splicing, so it is a per-patient value
# this repository does not hold. Every seam number downstream is therefore conditional on these.
BP_FRACTIONS = tuple(float(x) for x in
                     (os.environ.get("HYBRID_BP_FRACTIONS") or "0.25,0.5,0.75").split(","))


# ─────────────────────────────────────────────────────────────────────────────────────────────
# 1 · The coordinate convention, re-derived from committed artifacts (never restated)
# ─────────────────────────────────────────────────────────────────────────────────────────────
def coordinate_convention():
    """Grade the transcript-exon convention this module uses against the committed record.

    RAISES on any disagreement. Returns the graded dict that every artifact must carry, including
    the coding-rank alias that would address a DIFFERENT intron — named explicitly so a reader can
    see which of the two numbers is in use, which is the thing the 2026-08-06 defect hid.
    """
    ews = ja.transcript_model("EWSR1")
    nr4 = ja.transcript_model("NR4A3")          # _self_check_model + the exon-audit gate run here
    ews_coding = ja.coding_nt_per_exon(ews)
    nr4_coding = ja.coding_nt_per_exon(nr4)

    if nr4_coding[0] or nr4_coding[1]:
        raise RuntimeError(
            "NR4A3 transcript exons 1-2 are recorded as coding — the whole transcript-vs-coding "
            "rank hazard this module documents does not hold on this model, so the intron names "
            "in the header are wrong. Refusing to build anything on them.")
    if not nr4_coding[NR4A3_ACCEPTOR_EXON - 1]:
        raise RuntimeError(f"NR4A3 transcript exon {NR4A3_ACCEPTOR_EXON} carries no coding "
                           "sequence — this is Defect 1's shape and it is refused, not slid onto "
                           "a neighbour")
    if not ews_coding[0]:
        raise RuntimeError("EWSR1 transcript exon 1 is recorded as non-coding — then EWSR1's "
                           "transcript rank is NOT its coding rank and the donor intron name here "
                           "is wrong")

    # the coding rank of the acceptor exon: how many coding exons up to and including it
    nr4_coding_rank = sum(1 for c in nr4_coding[:NR4A3_ACCEPTOR_EXON] if c)
    return {
        "rank_space": "TRANSCRIPT exon rank (Ensembl canonical), NOT coding-exon rank",
        "EWSR1": {
            "transcript": ews["transcript"], "n_transcript_exons": ews["n_transcript_exons"],
            "donor_exon_transcript_rank": EWSR1_DONOR_EXON,
            "donor_exon_coding_rank": sum(1 for c in ews_coding[:EWSR1_DONOR_EXON] if c),
            "intron_named": f"EWSR1 intron {EWSR1_DONOR_EXON} = the intron 3' of transcript exon "
                            f"{EWSR1_DONOR_EXON}",
            "transcript_rank_equals_coding_rank": True,
            "why": "EWSR1 transcript exon 1 is coding, so the two numbering schemes coincide — "
                   "which is why the 2026-08-06 off-by-two reproduced correctly on this side",
        },
        "NR4A3": {
            "transcript": nr4["transcript"], "n_transcript_exons": nr4["n_transcript_exons"],
            "acceptor_exon_transcript_rank": NR4A3_ACCEPTOR_EXON,
            "acceptor_exon_coding_rank": nr4_coding_rank,
            "intron_named": f"NR4A3 intron {NR4A3_ACCEPTOR_EXON - 1} = the intron 5' of transcript "
                            f"exon {NR4A3_ACCEPTOR_EXON}",
            "intron_if_coding_rank_were_used_instead":
                f"NR4A3 intron {NR4A3_ACCEPTOR_EXON + 1} — a DIFFERENT piece of DNA",
            "transcript_rank_equals_coding_rank": False,
            "n_leading_non_coding_transcript_exons": next(
                (i for i, c in enumerate(nr4_coding) if c), len(nr4_coding)),
            "acceptor_exon_5utr_nt_the_fusion_retains": nr4["utr5_len"] -
                                                        ja.exon_tx_start(nr4, NR4A3_ACCEPTOR_EXON),
            "why": "NR4A3 transcript exons 1-2 carry no CDS, so transcript exon 3 is coding exon 1. "
                   "Both of this lane's retracted defects live in this two-rank gap.",
        },
        "_gate": ("junction_aso.transcript_model ran its four sequence self-checks AND the "
                  "nr4a3-exon-audit.json provenance gate on both models before this dict was "
                  "built; a disagreement raises rather than returning a graded value"),
        "_transcript_source": ja.transcript_source_provenance(),
    }


# ─────────────────────────────────────────────────────────────────────────────────────────────
# 2 · The fusion-unique budget — the number §3.5 is really claiming
# ─────────────────────────────────────────────────────────────────────────────────────────────
def unique_budget(oligo_len=None, wing=None):
    """How many oligo windows a SEAM — any seam, exonic or intronic — can make fusion-unique.

    This is arithmetic, not biology, and it is the whole argument: a junction of two sequences
    that each exist in the wild type contributes exactly `L - 1` windows that exist in neither
    parent (the windows drawing >=1 base from each side). An RNase-H gapmer additionally needs the
    seam INSIDE its central DNA gap, which leaves `GAP - 1`. Nothing about moving the seam from an
    exon boundary to an intron changes either count.

    Cross-checked against the committed exon-junction panels rather than asserted: both graded
    panels must contain exactly `GAP - 1` designs, or this function's model of the tiler is wrong.
    """
    L = oligo_len if oligo_len is not None else ja.OLIGO_LEN
    W = wing if wing is not None else ja.WING
    gap = L - 2 * W
    predicted = {"unique_windows_of_length_L": L - 1, "rnaseh_usable_windows": gap - 1}

    observed = {}
    for tag in ("e7n3", "e12n3"):
        path = os.path.join(HERE, f"junction-aso-designs-{tag}.json")
        if not os.path.exists(path):
            observed[tag] = None                      # absent reading, not a reading of absence
            continue
        with open(path) as fh:
            d = json.load(fh)
        observed[tag] = {"n_candidates": d.get("n_candidates"),
                         "n_fusion_specific": d.get("n_fusion_specific"),
                         "oligo_length": d.get("oligo_length"),
                         "architecture": d.get("architecture")}
    mismatched = [t for t, o in observed.items()
                  if o and o.get("oligo_length") == L and o.get("n_candidates") != gap - 1]
    if mismatched:
        raise RuntimeError(
            f"the committed exon-junction panels {mismatched} do not carry {gap - 1} candidates, "
            "so this module's model of junction_aso.design is wrong and its budget comparison "
            "would be meaningless")
    return {"oligo_len": L, "wing": W, "gap": gap, "architecture": f"{W}-{gap}-{W}",
            "predicted": predicted,
            "observed_in_committed_exon_junction_panels": observed,
            "_note": ("`unique_windows_of_length_L` = L-1 and `rnaseh_usable_windows` = GAP-1 for "
                      "ANY seam between two sequences that each exist in the wild type. The "
                      "hybrid intron's seam is such a seam, so its budget is identical to the "
                      "mRNA exon junction's — not 'kilobases'.")}


# ─────────────────────────────────────────────────────────────────────────────────────────────
# 3 · Why the intron's BULK is not fusion-unique, and what the existing screen does with it
# ─────────────────────────────────────────────────────────────────────────────────────────────
def wildtype_identity_audit():
    """The identity that decides the lane, plus a REAL run of the screen's own classifiers on it.

    The hybrid intron is [5' part of EWSR1 intron 7] + [3' part of NR4A3 intron 2]. Both parts are
    wild-type human DNA, transcribed as wild-type pre-mRNA in every cell expressing either gene.
    So every window that does not span the intronic breakpoint is a PERFECT, full-length match to
    a wild-type pre-mRNA — not a near-match, an identity.

    ⛔ AND THAT IS THE COMPARTMENT ARGUMENT EATING ITSELF. An intron is only a target at all
    because it exists in NUCLEAR pre-mRNA. The wild-type introns exist in the same compartment, in
    the same molecules' unspliced precursors. "It exists as pre-mRNA" and "its sequence does not
    exist in the wild type" cannot both be true of the same bases.

    What this function MEASURES rather than asserts: what the committed screen
    (`junction_aso_offtarget`) would do with such a hit. It runs the screen's real `is_parent()`
    and `classify()` on a constructed BLAST record describing a perfect 16/16 gap-spanning hit to
    the wild-type EWSR1 transcript. If `is_parent` returns True the hit is dropped BEFORE
    `n_offtarget_near_matches` is computed — so the route's fatal liability would be reported as a
    parent/intended hit and the oligo would score clean.
    """
    L, W = ja.OLIGO_LEN, ja.WING
    perfect_parent_hit = {
        "acc": "NM_005243.4",
        "defn": "Homo sapiens EWS RNA binding protein 1 (EWSR1), transcript variant 1, mRNA",
        "identity": L, "align_len": L, "q_from": 1, "q_to": L,
        "qseq": "A" * L, "midline": "|" * L,
    }
    same_hit_unnamed = dict(perfect_parent_hit, acc="XM_000000.1",
                            defn="Homo sapiens uncharacterized locus, mRNA")
    return {
        "claim_under_test": ("emc-unexplored-treatment-lanes.md §3.5: 'That sequence exists in no "
                             "other transcript in the body ... there are kilobases of it.'"),
        "verdict": "FALSE for pre-mRNA, which is the only compartment in which the target exists",
        "why": ("The hybrid intron is composed entirely of wild-type EWSR1 intron-7 and wild-type "
                "NR4A3 intron-2 nucleotides. Those bases are present, base for base, in the "
                "unspliced pre-mRNA of the wild-type alleles — including the wild-type allele in "
                "the tumour cell itself and every allele in every normal cell that transcribes "
                "either gene. Only windows spanning the intronic breakpoint are novel."),
        "true_of_the_MATURE_transcriptome": ("An intron is absent from mature mRNA, so a screen "
                                             "run against a mature-transcript database (RefSeq "
                                             "RNA — what `junction_aso_offtarget` and "
                                             "`aso_insilico` both use) cannot see the wild-type "
                                             "copy at all. That is an instrument blind spot, not "
                                             "a clean result: an absent reading is not a reading "
                                             "of absence."),
        "screen_behaviour_measured_not_asserted": {
            "_what_was_run": ("junction_aso_offtarget.is_parent() and .classify() from the "
                              "committed screen, on a constructed record describing a perfect "
                              f"{L}/{L} gap-spanning hit to wild-type EWSR1"),
            "is_parent_on_wildtype_EWSR1_hit": jao.is_parent(perfect_parent_hit),
            "classify_on_the_same_hit": jao.classify(perfect_parent_hit),
            "classify_on_the_same_alignment_if_it_were_NOT_a_parent":
                jao.classify(same_hit_unnamed),
            "is_parent_filters_it_out_of_the_offtarget_count": jao.is_parent(perfect_parent_hit),
            "consequence": ("`screen_one` computes n_offtarget_near_matches over hits with "
                            "`not is_parent(h)`. A perfect, gap-spanning, RNase-H-cleavable match "
                            "to wild-type EWSR1 is therefore EXCLUDED from the off-target count "
                            "and counted under `n_parent_or_intended_hits`. That exclusion is "
                            "CORRECT for an mRNA junction oligo, where a parent can match at most "
                            "one side of the seam and cannot be cleaved; it is WRONG for an "
                            "intron-body oligo, where the parent match is complete. Applied "
                            "unmodified, the screen would score an intron-body ASO clean while it "
                            "is a wild-type EWSR1 knockdown agent."),
        },
        "_no_screen_needed_for_this": ("This is an identity, not a measurement: a window taken "
                                       "from wild-type intronic DNA is a substring of wild-type "
                                       "intronic DNA. No BLAST result can change it, and no "
                                       "BLAST result should be quoted as if it had tested it."),
    }


def regeneration_check():
    """Is the instrument in hand the one that produced the panels this audit compares against?

    ⭐ THE COMPARISON IS ONLY WORTH ANYTHING IF IT IS. This rebuilds both committed exon-junction
    design panels from the committed transcript cache and compares them design-for-design to the
    files on disk. A drift here would mean the head-to-head is against a record this code can no
    longer reproduce — which is exactly the state the 2026-08-06 retraction was found in, where two
    artifacts agreed because one defect produced both.

    Offline and $0: `TRANSCRIPT_SOURCE=cache` is forced for the duration and restored afterwards.
    """
    saved = {k: os.environ.get(k) for k in
             ("FUSION_JUNCTION_MODE", "EWSR1_EXON_END", "NR4A3_EXON_START", "TRANSCRIPT_SOURCE")}
    # ⛔ RESTORE THE MODULE STATE THIS BORROWS, NOT JUST THE ENV. `_TX_CACHE` is included
    # deliberately: leaving it populated would make every later caller in the same process silently
    # reuse models this function fetched under ITS choice of source, which is the same
    # cross-consumer leak the env restore below exists to prevent, one layer down.
    saved_globals = (ja.EWSR1_full, ja.NR4A3_full, ja.LAST_JUNCTION, dict(ja._TX_CACHE))
    rows = {}
    try:
        os.environ["FUSION_JUNCTION_MODE"] = "real"
        os.environ["TRANSCRIPT_SOURCE"] = "cache"
        for e, n, tag in ((7, 3, "e7n3"), (12, 3, "e12n3")):
            path = os.path.join(HERE, f"junction-aso-designs-{tag}.json")
            if not os.path.exists(path):
                rows[tag] = None                      # absent reading, not a reading of absence
                continue
            os.environ["EWSR1_EXON_END"], os.environ["NR4A3_EXON_START"] = str(e), str(n)
            _, _, left, right, fusion = ja.build_parents_and_fusion()
            fresh = ja.design(left, right, fusion)
            with open(path) as fh:
                committed = json.load(fh)
            rows[tag] = {
                "n_designs_fresh": len(fresh),
                "n_designs_committed": len(committed["top_designs"]),
                "designs_identical": fresh == committed["top_designs"],
                "seam_fresh": left[-12:] + "|" + right[:12],
                "seam_committed": committed["_breakpoint_model"]["junction_context_mRNA"],
            }
    finally:
        for k, v in saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        ja.EWSR1_full, ja.NR4A3_full = saved_globals[0], saved_globals[1]
        ja.LAST_JUNCTION = saved_globals[2]
        ja._TX_CACHE.clear()
        ja._TX_CACHE.update(saved_globals[3])
    return {"_what": ("both committed exon-junction design panels rebuilt from the committed "
                      "transcript cache and compared design-for-design"),
            "panels": rows,
            "all_reproduce": all(r is None or (r["designs_identical"] and
                                               r["seam_fresh"] == r["seam_committed"])
                                 for r in rows.values())}


def mechanism_and_confidence_cost():
    """⛔ THE HONEST COMPLICATION, STATED FIRST-CLASS RATHER THAN AS A FOOTNOTE.

    A pre-mRNA intron is a NUCLEAR, TRANSIENT target. An intron-directed oligo is therefore not the
    same kind of object as the exon-junction gapmer, even when the sequence chemistry is identical,
    and the difference costs confidence in a way no screen can repay.
    """
    return {
        "target_state": ("The hybrid intron exists only in unspliced pre-mRNA. Splicing is largely "
                         "co-transcriptional, so the intron is removed on a timescale far shorter "
                         "than the mature transcript's lifetime and is present at a small fraction "
                         "of the steady-state transcript pool. The exon junction, by contrast, is "
                         "present in every copy of the mature fusion mRNA for as long as it "
                         "survives."),
        "mechanisms_available": [
            {"mechanism": "RNase-H1 gapmer against the intron",
             "is_available": True,
             "why": ("RNase-H1 is nuclear-active and gapmers do act on pre-mRNA, so this is "
                     "mechanically real rather than hypothetical."),
             "what_it_costs": ("Effect size becomes a KINETIC quantity — the oligo must engage and "
                               "direct cleavage before the intron is excised — and nothing in this "
                               "repository, in silico or otherwise, measures that rate. A screen "
                               "result that looks identical to the exon-junction panel's therefore "
                               "supports a WEAKER conclusion here than there."),
             "metrics_transfer": ("Yes, unchanged: `classify()`'s DNA-gap logic and the whole "
                                  "`n_true_cleavage_risk` family apply as written. This is why the "
                                  "seam arm can be reported with the identical metric names.")},
            {"mechanism": "steric-block SSO (fully modified, no DNA gap) at a splice element",
             "is_available": True,
             "why": ("This is what §3.5 actually proposes — branch point, polypyrimidine tract, or "
                     "a cryptic/poison exon. It is the mechanism with clinical precedent in other "
                     "diseases."),
             "what_it_costs": ("A steric blocker's liability is OCCUPANCY, not cleavage, so the "
                               "committed screen's headline metric does not merely transfer badly "
                               "— it does not apply. Reporting `n_true_cleavage_risk` for an SSO "
                               "would be a category error. It would need an occupancy/accessibility "
                               "screen this lane has not built, plus a splice-effect predictor "
                               "(SpliceAI/Pangolin/MaxEntScan), and its endpoint is mis-splicing "
                               "rather than transcript loss."),
             "metrics_transfer": "No — see above. Not substituted with a different metric here."},
        ],
        "the_compartment_argument_is_self_defeating": (
            "An intron is a target only because it exists in nuclear pre-mRNA. The wild-type EWSR1 "
            "and NR4A3 introns exist in the same compartment, in the same nucleus, including the "
            "wild-type allele of the tumour cell itself. So the perfect-match liability is "
            "CO-LOCALISED with the intended target rather than being somewhere else in the body."),
        "repo_held_evidence_for_the_pseudoexon_biology": {
            "what": ("A real TAF15::NR4A3 fusion retains a short cryptic exon located in NR4A3 "
                     "intron 2, adding 25 residues ahead of the NR4A3 ATG."),
            "source": "PMC6766969, quoted in emc_fet_construct_designs.py -> TAF15_NR4A3 -> "
                      "_reported_variant_not_modelled",
            "what_it_supports": ("The BIOLOGY of §3.5's pseudoexon idea — a cryptic exon inside "
                                 "NR4A3 intron 2 is used in at least one reported EMC fusion. This "
                                 "is the strongest support the lane has and it is real."),
            "what_it_does_not_support": ("Fusion-exclusivity. That cryptic exon's sequence is "
                                         "wild-type NR4A3 intron 2, so an SSO promoting its "
                                         "inclusion would act on wild-type NR4A3 pre-mRNA on the "
                                         "same terms. Its sequence is also not held by this "
                                         "repository — an absent reading, not a reading of "
                                         "absence."),
        },
    }


def composition_is_not_the_binding_constraint():
    """Measured from the committed panels: is the exon-junction route failing on COMPOSITION?

    ⭐ THIS IS THE ONE THAT DECIDES WHETHER THE SURVIVING SUB-QUESTION IS WORTH ANYTHING. §3.5's
    stated attraction is that the intron "directly attacks the known GC-rich-junction weakness".
    But the GC-rich seam belongs to the CODON-SPACE modelled breakpoint (the 75-81% GC junction the
    390-breakpoint scan was built to escape). The two seams the corrected 2026-08-06 regeneration
    actually graded are not GC-rich: every oligo's GC is read here out of the committed design
    panels, and the FAVORABLE band is imported from `junction_breakpoint_scan` rather than typed.

    If the graded designs already sit inside that band and STILL return
    `n_oligos_no_true_cleavage_risk = 0`, then composition is not the binding constraint and moving
    the seam to a compositionally nicer neighbourhood cannot be expected to fix it. The binding
    constraint is the LENGTH of the fusion-unique window, which the intron does not change.
    """
    import junction_breakpoint_scan as jbs
    lo, hi = jbs.GC_FAV_LO, jbs.GC_FAV_HI
    rows = {}
    for tag in ("e7n3", "e12n3"):
        dpath = os.path.join(HERE, f"junction-aso-designs-{tag}.json")
        spath = os.path.join(HERE, f"junction-aso-offtarget-{tag}.json")
        if not (os.path.exists(dpath) and os.path.exists(spath)):
            rows[tag] = None                          # absent reading, not a reading of absence
            continue
        with open(dpath) as fh:
            designs = json.load(fh)["top_designs"]
        with open(spath) as fh:
            screen = json.load(fh)
        gcs = [o["gc_percent"] for o in designs]
        rows[tag] = {
            "seam_context_mRNA": screen["breakpoint"]["junction_context_mRNA"],
            "n_designs": len(designs),
            "gc_percent_min": min(gcs), "gc_percent_max": max(gcs),
            "n_designs_inside_favorable_gc_band": sum(1 for g in gcs if lo <= g <= hi),
            "n_oligos_screened": screen.get("n_oligos_screened"),
            "n_oligos_no_true_cleavage_risk": screen.get("n_oligos_no_true_cleavage_risk"),
        }
    return {
        "favorable_gc_band": [lo, hi],
        "_band_source": "junction_breakpoint_scan.GC_FAV_LO / GC_FAV_HI (imported, not typed)",
        "graded_junctions": rows,
        "reading": ("The graded seams are not the GC-rich neighbourhood §3.5 targets — most "
                    "designs sit inside the repository's own favorable GC band — and the screen "
                    "still returned zero clean oligos at both. So the exon-junction route is not "
                    "failing on composition; it is failing because a seam only ever yields GAP-1 "
                    "windows and a 16-mer with 2 mismatches allowed has near-matches across the "
                    "transcriptome. Moving the seam into an intron does not lengthen the window."),
        "_caveat": ("This is a reading of two junctions, not of the whole breakpoint space. The "
                    "GC-rich seam §3.5 refers to is real — it belongs to the codon-space modelled "
                    "breakpoint, which is superseded as a description of the graded junctions."),
    }


def screen_applicability():
    """Assumption-by-assumption: can the committed screen be applied to an intron target as-is?

    Task-level honesty rule: if it cannot be applied without modification, say exactly why rather
    than substituting a different metric.
    """
    return [
        {"assumption": "the database contains the compartment the drug acts in",
         "holds_for_exon_junction": True, "holds_for_intron": False,
         "detail": ("refseq_rna (BLAST screen) and GCF_000001405.40 *_rna.fna.gz (aso_insilico) "
                    "are MATURE transcript sets. Neither contains introns, so an intron-directed "
                    "oligo's largest liability class — the wild-type pre-mRNA — is invisible to "
                    "both. Running them unchanged yields a low off-target count BY CONSTRUCTION."),
         "fix": "screen against a genomic/pre-mRNA database, or against the parent loci directly"},
        {"assumption": "a hit to a parent gene is benign (half-seam, not cleavable)",
         "holds_for_exon_junction": True, "holds_for_intron": False,
         "detail": ("`is_parent()` drops EWSR1/NR4A3 hits before the off-target count. For an "
                    "intron-body oligo the parent hit is a perfect full-length match across the "
                    "DNA gap, i.e. the most cleavable hit possible."),
         "fix": "the parent exclusion must be disabled for any oligo not spanning the seam"},
        {"assumption": "the target seam is shared across patients",
         "holds_for_exon_junction": True, "holds_for_intron": False,
         "detail": ("an mRNA exon junction is produced by splicing, which normalises every "
                    "intronic DNA breakpoint in the same intron pair to ONE mRNA seam — that is "
                    "why fusions are detected at the transcript level. The intronic breakpoint "
                    "itself is the position of a DNA double-strand break and is not so "
                    "normalised."),
         "fix": ("none available in silico; an intron-seam oligo is a per-patient sequence. This "
                 "repository holds NO EMC breakpoint-position distribution, so the spread is "
                 "UNMEASURED here rather than assumed to be wide.")},
        {"assumption": "the gap-resolved RNase-H classification is meaningful",
         "holds_for_exon_junction": True, "holds_for_intron": True,
         "detail": ("RNase-H1 is active in the nucleus on pre-mRNA, so `classify()`'s gap logic "
                    "transfers unchanged. This is the one assumption that survives, and it is why "
                    "the seam arm below can be screened with the identical metric set.")},
    ]


# ─────────────────────────────────────────────────────────────────────────────────────────────
# 4 · The measured half (needs the network — CI)
# ─────────────────────────────────────────────────────────────────────────────────────────────
def _exon_genomic_spans(symbol):
    """Ensembl genomic exon coordinates for the canonical transcript, in TRANSCRIPT order.

    GATE: the genomic exon lengths must reproduce, exon for exon, the committed
    `emc-construct-inputs.json` exon lengths. That is what proves the coordinate convention
    (1-based inclusive, strand-aware) before one intronic base is used — the verification against
    a committed artifact this lane's two defects both skipped.
    """
    import fusion_breakpoints as fb
    model = ja.transcript_model(symbol)                       # runs the committed-record gates
    tr = fb.get(f"{ENS}/lookup/id/{model['transcript']}?expand=1")
    strand = tr["strand"]
    exons = sorted(tr["Exon"], key=lambda e: e["start"], reverse=(strand == -1))
    lens = [e["end"] - e["start"] + 1 for e in exons]
    if lens != model["exon_lens"]:
        raise RuntimeError(
            f"{symbol}: genomic exon lengths {lens[:6]}... do not reproduce the committed "
            f"emc-construct-inputs.json exon lengths {model['exon_lens'][:6]}... — the coordinate "
            "convention is not what this module assumes, so no intron may be cut")
    return {"symbol": symbol, "transcript": model["transcript"],
            "chrom": tr["seq_region_name"], "strand": strand,
            "exons": [{"rank": i + 1, "start": e["start"], "end": e["end"]}
                      for i, e in enumerate(exons)],
            "_gate": "genomic exon lengths reproduce emc-construct-inputs.json exon-for-exon"}


def _region_seq(chrom, start, end, strand):
    import fusion_breakpoints as fb
    txt = fb.get_text(f"{ENS}/sequence/region/human/{chrom}:{start}..{end}:{strand}"
                      f"?content-type=text/plain")
    return "".join(txt.split()).upper()


def fetch_intron(symbol, upstream_exon_rank):
    """The intron immediately 3' of TRANSCRIPT exon `upstream_exon_rank`, measured.

    Self-check: a canonical U2 intron begins GT and ends AG. That check is the direct test of the
    coordinate arithmetic — an off-by-one, or a strand mistake, breaks it immediately.
    """
    g = _exon_genomic_spans(symbol)
    ex = g["exons"]
    if upstream_exon_rank >= len(ex):
        raise ValueError(f"{symbol}: no intron 3' of transcript exon {upstream_exon_rank}")
    a, b = ex[upstream_exon_rank - 1], ex[upstream_exon_rank]
    if g["strand"] == 1:
        lo, hi = a["end"] + 1, b["start"] - 1
    else:
        lo, hi = b["end"] + 1, a["start"] - 1
    seq = _region_seq(g["chrom"], lo, hi, g["strand"])
    rec = {"symbol": symbol, "transcript": g["transcript"], "chrom": g["chrom"],
           "strand": g["strand"], "intron_name": f"{symbol} intron {upstream_exon_rank} "
                                                 f"(3' of TRANSCRIPT exon {upstream_exon_rank})",
           "genomic_start": lo, "genomic_end": hi, "length_nt": len(seq),
           "donor_dinucleotide": seq[:2], "acceptor_dinucleotide": seq[-2:],
           "gc_percent": round(100 * (seq.count("G") + seq.count("C")) / len(seq), 1) if seq else 0,
           "_seq": seq}
    if (hi - lo + 1) != len(seq):
        raise RuntimeError(f"{symbol}: requested {hi - lo + 1} nt, Ensembl returned {len(seq)}")
    if rec["donor_dinucleotide"] != "GT" or rec["acceptor_dinucleotide"] != "AG":
        raise RuntimeError(
            f"{rec['intron_name']}: boundaries read {rec['donor_dinucleotide']}..."
            f"{rec['acceptor_dinucleotide']}, not GT...AG. A non-canonical intron is possible, but "
            "an off-by-one or a strand error is far likelier, and neither may be built on.")
    return rec


def gene_locus_seq(symbol):
    """The whole gene span (exons + introns) on the transcribed strand — the wild-type pre-mRNA
    sequence an intron-directed oligo would actually meet."""
    g = _exon_genomic_spans(symbol)
    starts = [e["start"] for e in g["exons"]]
    ends = [e["end"] for e in g["exons"]]
    lo, hi = min(starts), max(ends)
    return _region_seq(g["chrom"], lo, hi, g["strand"])


def build_hybrid(ews_intron, nr4_intron, frac):
    """Hybrid intron at a MODELLED breakpoint `frac` of the way into each intron.

    Returns the two halves and the joined sequence. The breakpoint position is a model input, not
    a measurement — see BP_FRACTIONS.
    """
    k = max(1, int(round(len(ews_intron["_seq"]) * frac)))
    m = max(1, int(round(len(nr4_intron["_seq"]) * (1 - frac))))
    left = ews_intron["_seq"][:k]
    right = nr4_intron["_seq"][-m:]
    return left, right, left + right


def measure_unique_extent(hybrid, parents, oligo_len=None):
    """How many L-mer windows of the hybrid intron are absent from BOTH parent loci — measured.

    `parents` is a list of wild-type gene-span sequences. The prediction from `unique_budget` is
    L-1; a larger number would mean the breakpoint fell in sequence the parent locus does not
    contain (impossible by construction) and a smaller one means repeat content makes even the
    seam windows non-unique. Reported either way.
    """
    L = oligo_len if oligo_len is not None else ja.OLIGO_LEN
    uniq = [i for i in range(len(hybrid) - L + 1)
            if all(hybrid[i:i + L] not in p for p in parents)]
    return {"oligo_len": L, "n_windows_total": len(hybrid) - L + 1,
            "n_windows_absent_from_both_parent_loci": len(uniq),
            "unique_window_span": [min(uniq), max(uniq)] if uniq else None,
            "n_windows_that_are_a_perfect_match_to_a_parent_locus":
                (len(hybrid) - L + 1) - len(uniq)}


def ci_measure():
    """The whole measured half. Raises rather than degrading — every gate above is load-bearing."""
    ews_i = fetch_intron("EWSR1", EWSR1_DONOR_EXON)
    nr4_i = fetch_intron("NR4A3", NR4A3_ACCEPTOR_EXON - 1)
    parents = [gene_locus_seq("EWSR1"), gene_locus_seq("NR4A3")]

    arms = []
    for frac in BP_FRACTIONS:
        left, right, hybrid = build_hybrid(ews_i, nr4_i, frac)
        # the SAME tiler, with the parent strings set to the wild-type LOCI (pre-mRNA), which is
        # the correct and stricter specificity test for an intronic oligo
        ja.EWSR1_full, ja.NR4A3_full = parents[0], parents[1]
        designs = ja.design(left, right, hybrid)
        arms.append({
            "modelled_breakpoint_fraction_into_EWSR1_intron": frac,
            "hybrid_intron_length_nt": len(hybrid),
            "EWSR1_side_nt": len(left), "NR4A3_side_nt": len(right),
            "seam_context": left[-12:] + "|" + right[:12],
            "seam_gc_percent_pm12": round(100 * sum(
                c in "GC" for c in (left[-12:] + right[:12])) / len(left[-12:] + right[:12]), 1),
            "unique_extent": measure_unique_extent(hybrid, parents),
            "n_seam_designs": len(designs),
            "n_fusion_specific": sum(1 for o in designs if o["fusion_specific"]),
            "designs": designs,
        })
    return {"EWSR1_intron": {k: v for k, v in ews_i.items() if not k.startswith("_")},
            "NR4A3_intron": {k: v for k, v in nr4_i.items() if not k.startswith("_")},
            "parent_locus_nt": {"EWSR1": len(parents[0]), "NR4A3": len(parents[1])},
            "modelled_breakpoint_arms": arms}


def screen_seam_designs(arms, n_oligos=None):
    """Run the COMMITTED screen, unmodified, on the seam designs — identical metric names.

    `junction_aso_offtarget.screen_one` is called as-is so every field is directly comparable to
    `junction-aso-offtarget-e7n3.json`. The two assumptions this violates for an intron target are
    enumerated in `screen_applicability()` and are re-stated in the artifact beside the numbers,
    because a metric that is comparable is not automatically a metric that is valid.
    """
    n = n_oligos if n_oligos is not None else jao.N_OLIGOS
    out = []
    for arm in arms:
        designs = [o for o in arm["designs"] if o["fusion_specific"]][:n]
        screened = []
        for i, d in enumerate(designs):
            print(f"  screening seam oligo {i+1}/{len(designs)}: {d['target_mRNA_5to3']}",
                  file=sys.stderr)
            screened.append(jao.screen_one(d))
            time.sleep(3)
        n_ok = sum(1 for r in screened if r["status"] == "screened")
        out.append({
            "modelled_breakpoint_fraction_into_EWSR1_intron":
                arm["modelled_breakpoint_fraction_into_EWSR1_intron"],
            "n_oligos_screened": len(screened),
            "n_screened_ok": n_ok,
            "n_oligos_no_true_cleavage_risk": sum(
                1 for r in screened
                if r.get("status") == "screened" and r.get("n_true_cleavage_risk", 1) == 0),
            "oligos": screened,
        })
    return out


# ─────────────────────────────────────────────────────────────────────────────────────────────
def head_to_head(budget, measured, composition=None):
    """The like-for-like row the deliverable is judged on. `measured` is None until CI has run."""
    row = {
        "_axis": "fusion-unique target available to an RNase-H gapmer, per patient",
        "exon_junction_mRNA": {
            "unique_windows": budget["predicted"]["unique_windows_of_length_L"],
            "rnaseh_usable_windows": budget["predicted"]["rnaseh_usable_windows"],
            "observed_designs_e7n3": (budget["observed_in_committed_exon_junction_panels"]
                                      .get("e7n3") or {}).get("n_candidates"),
            "observed_designs_e12n3": (budget["observed_in_committed_exon_junction_panels"]
                                       .get("e12n3") or {}).get("n_candidates"),
            "shared_across_patients_with_the_same_exon_pair": True,
            "screen_result": ("n_oligos_no_true_cleavage_risk = 0 and "
                              "n_candidates_zero_offtarget = 0 at BOTH graded junctions "
                              "(junction-aso-offtarget-e7n3.json, -e12n3.json, "
                              "aso-insilico-evaluation-e7n3.json, -e12n3.json)"),
        },
        "hybrid_intron": {
            "claimed_by_lane_memo": "kilobases",
            "unique_windows": budget["predicted"]["unique_windows_of_length_L"],
            "rnaseh_usable_windows": budget["predicted"]["rnaseh_usable_windows"],
            "observed_designs": (measured or {}).get("n_seam_designs_per_arm"),
            "shared_across_patients_with_the_same_exon_pair": False,
            "why_not_kilobases": ("every window not spanning the intronic breakpoint is a perfect "
                                  "match to wild-type EWSR1 or NR4A3 pre-mRNA — the identity in "
                                  "`wildtype_identity_audit`"),
            "screen_result": ((measured or {}).get("screen_summary")
                              or "UNMEASURED — needs the CI fetch (see _what_is_unmeasured)"),
        },
        "verdict": ("The hybrid intron does NOT clear the bar the exon junction failed, and it "
                    "does not change the bar. Its fusion-unique budget is the SAME L-1 windows "
                    "(GAP-1 usable), not kilobases; the surplus it appeared to offer is wild-type "
                    "pre-mRNA of a ubiquitously expressed gene; and unlike the mRNA seam, the "
                    "intronic seam is not shared between patients, so an oligo against it is a "
                    "per-patient sequence rather than a drug for the disease."),
        "what_would_change_it": ("One sub-question survives and it is narrow: an intronic seam "
                                 "sits in different sequence composition from an exonic one, and "
                                 "§3.5's stated attraction is that this attacks a 'GC-rich' seam. "
                                 "`mode=ci` measures it. ⚠ But the prior is poor and it is "
                                 "MEASURED, not assumed — see "
                                 "`composition_is_not_the_binding_constraint`: the two graded "
                                 "junctions are already mostly inside this repository's own "
                                 "favorable GC band and still returned zero clean oligos, so "
                                 "composition is not what is failing. Nothing measurable here can "
                                 "restore the 'kilobases' premise or the cross-patient property."),
    }
    if composition is not None:
        row["composition_prior"] = {
            "favorable_gc_band": composition["favorable_gc_band"],
            "graded_junctions": {k: (None if v is None else
                                     {kk: v[kk] for kk in
                                      ("gc_percent_min", "gc_percent_max",
                                       "n_designs_inside_favorable_gc_band",
                                       "n_oligos_no_true_cleavage_risk")})
                                 for k, v in composition["graded_junctions"].items()},
        }
    return row


def main():
    mode = (os.environ.get("HYBRID_INTRON_MODE") or
            ("ci" if "--ci" in sys.argv else "offline")).strip().lower()
    conv = coordinate_convention()
    budget = unique_budget()
    identity = wildtype_identity_audit()
    applic = screen_applicability()
    composition = composition_is_not_the_binding_constraint()

    measured, screens, unmeasured = None, None, []
    if mode == "ci":
        measured = ci_measure()
        if os.environ.get("HYBRID_SKIP_BLAST") != "1":
            screens = screen_seam_designs(measured["modelled_breakpoint_arms"])
        else:
            unmeasured.append("BLAST seam screen skipped by HYBRID_SKIP_BLAST=1")
        for arm in measured["modelled_breakpoint_arms"]:
            arm["designs"] = arm["designs"][:12]
    else:
        unmeasured = [
            "EWSR1 intron 7 and NR4A3 intron 2 lengths, GC and GT..AG boundaries",
            "the hybrid intron's measured fusion-unique extent against both parent loci",
            "the intronic seam's composition and its five gapmer windows",
            "the BLAST gap-resolved off-target screen on those windows "
            "(n_oligos_no_true_cleavage_risk), i.e. the exon-junction panel's headline metric",
        ]

    result = {
        "_title": "The EWSR1::NR4A3 hybrid intron as a fusion-exclusive ASO target — premise audit",
        "_cost": "$0 — CPU only, no GPU and no rental." + (
            " Inputs: live Ensembl reads on a GitHub-hosted runner + NCBI BLAST URL API."
            if mode == "ci" else
            " Inputs: committed artifacts only (emc-construct-inputs.json, nr4a3-exon-audit.json,"
            " the committed junction panels) and the repo's own screening code. No network call."),
        "_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "mode": mode,
        "_limits": [
            "Sequence arithmetic and composition only. No potency, no knockdown, no delivery, no "
            "tolerability, and no efficacy, safety, therapeutic-window or clinical claim is made "
            "or implied. An ASO design is a sequence proposal, never a therapeutic claim.",
            "Canonical transcripts only, and one modelled genomic breakpoint per arm. The real "
            "per-patient breakpoint is not held by this repository and is not decided here.",
            "Predicted specificity, never validated specificity.",
        ],
        "coordinate_convention": conv,
        "regeneration_check": regeneration_check(),
        "fusion_unique_budget": budget,
        "wildtype_identity_audit": identity,
        "mechanism_and_confidence_cost": mechanism_and_confidence_cost(),
        "composition_is_not_the_binding_constraint": composition,
        "screen_applicability": applic,
        "measured": measured,
        "seam_screens": screens,
        "head_to_head": head_to_head(budget, None if not measured else {
            "n_seam_designs_per_arm": [a["n_seam_designs"]
                                       for a in measured["modelled_breakpoint_arms"]],
            "screen_summary": None if not screens else
            [{"bp_fraction": s["modelled_breakpoint_fraction_into_EWSR1_intron"],
              "n_oligos_screened": s["n_oligos_screened"],
              "n_oligos_no_true_cleavage_risk": s["n_oligos_no_true_cleavage_risk"]}
             for s in screens],
        }, composition),
        "_what_is_unmeasured": unmeasured,
    }
    with open(OUT, "w") as fh:
        json.dump(result, fh, indent=2)
    print("wrote", OUT, file=sys.stderr)
    print(json.dumps({k: v for k, v in result.items()
                      if k not in ("measured", "seam_screens", "wildtype_identity_audit",
                                   "screen_applicability")}, indent=2))


if __name__ == "__main__":
    main()
