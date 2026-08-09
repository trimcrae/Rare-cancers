#!/usr/bin/env python3
"""Where PRMT5's measured substrate motif sits in EMC's fusion protein — and which half keeps it.

⭐ THE QUESTION THIS ANSWERS. The EMC PRMT5 manuscript's weakest stated point is that its transfer
from another EWSR1-fusion sarcoma is an ASSUMPTION. One half of that assumption is checkable for
nothing: PRMT5 has a MEASURED sequence preference, EMC's fusion protein has a committed sequence,
and nobody in this repository had asked whether the retained half of the fusion contains the motif
at all.

⭐ THE MOTIF IS `GRG`, AND IT IS RETRIEVED RATHER THAN RECALLED. Musiani et al. (PMID 30940768,
Sci Signal 2019) profiled arginine methylation genome-wide after selective PRMT5 inhibition,
validated targets by in vitro methylation, and report "the preference of the enzyme to methylate
arginine sandwiched between two neighboring glycines (a Gly-Arg-Gly, or 'GRG,' sequence)". A
mapping experiment in the same family (PMID 31267554 / PMC6669924) narrows it further in one
substrate: of three DDX5 truncations, only the fragment carrying the C-terminal RGG/RG motif was
methylated by PRMT5, and mutating five arginines inside that motif abolished it.

⚠ SO `GRG` IS THE MOTIF, AND THIS REPOSITORY HAD ONLY EVER COUNTED `RG`. The two are not the same
string. `emc-fet-idr-census.json` and `emc-fet-construct-designs.json` count RG DIPEPTIDES, on a
threshold-free criterion chosen for a DIFFERENT mechanism (FET → ATM suppression → DSB
recruitment). This module counts both, side by side, so the substitution is visible rather than
assumed — and it re-derives the RG totals and checks them against the committed ones, so a
disagreement in the shared half is caught instead of being quietly averaged over.

⛔ WHAT THIS IS NOT, AND THE LIMIT IS SEVERE. A motif is a place a methyltransferase CAN act. It is
not evidence that any FET fusion protein is methylated, that PRMT5 is the enzyme that does it, or
that methylation of the fusion has any consequence in this disease. No experiment here touches an
EMC cell. This is a sequence argument and nothing more.

⛔ AND THE MOTIF IS NOT A NECESSARY CONDITION — the one measurement that speaks to it says so.
EWSR1::FLI1 (Ewing, type 1) retains ZERO RG dipeptides of EWSR1's 30, and PRMT5 inhibition
nonetheless reduces Ewing cell viability in an EWSR1::FLI1-DEPENDENT manner (PMID 40823091 /
PMC12354397). Whatever PRMT5 is doing in a FET-fusion sarcoma, it does not require the fusion
protein to carry the motif. Any prediction stratified on retained motif count must therefore be
offered as falsifiable and never as expected.

$0 — reads committed artifacts, stdlib only, no network.
"""
from __future__ import annotations

import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
DESIGNS = os.path.join(HERE, "emc-fet-construct-designs.json")
CENSUS = os.path.join(HERE, "emc-fet-idr-census.json")
OUT = os.path.join(HERE, "emc-prmt5-substrate-motif-map.json")

#: The motif PRMT5 was MEASURED to prefer, and the dipeptide this repository has been counting in
#: its place. Both are reported for every sequence so the substitution never has to be trusted.
MOTIFS = {
    "GRG": "PRMT5's measured preference — arginine flanked by glycine on both sides "
           "(PMID 30940768). This is the motif the manuscript's claim should rest on.",
    "RG": "the dipeptide `emc-fet-idr-census.json` counts, on a criterion adopted for the "
          "FET→ATM→DSB-recruitment mechanism, NOT for methylation. Reported so the two axes can "
          "be compared rather than conflated.",
}


def _positions(seq, motif):
    """1-based positions of every occurrence, overlapping included.

    ⚠ OVERLAPPING ON PURPOSE. `GRGRG` contains two GRG sites and two methylatable arginines; a
    non-overlapping scan would report one and silently halve a poly-RG tract, which is exactly the
    kind of region this module exists to measure."""
    out, i = [], seq.find(motif)
    while i != -1:
        out.append(i + 1)
        i = seq.find(motif, i + 1)
    return out


def _profile(seq):
    return {m: _positions(seq, m) for m in MOTIFS}


def _summarise(seq, name):
    prof = _profile(seq)
    return {
        "protein": name,
        "length_aa": len(seq),
        "motif_counts": {m: len(p) for m, p in prof.items()},
        "first_occurrence_residue": {m: (p[0] if p else None) for m, p in prof.items()},
        "last_occurrence_residue": {m: (p[-1] if p else None) for m, p in prof.items()},
        "positions": {m: p for m, p in prof.items()},
        "⚠_a_zero_here_is_a_measurement": "This sequence was read and the motif is absent from it. "
                                          "That is a reading of absence, not an absent reading — "
                                          "the sequence is committed and its length is printed.",
    }


def _retained(prof_positions, last_residue):
    """How many wild-type sites of each motif fall inside residues 1..last_residue."""
    return {m: sum(1 for p in pos if p <= last_residue) for m, pos in prof_positions.items()}


def build():
    with open(DESIGNS, encoding="utf-8") as fh:
        des = json.load(fh)
    with open(CENSUS, encoding="utf-8") as fh:
        cen = json.load(fh)

    wt_seq, wt = {}, {}
    for c in des["wild_type_controls"]["controls"]:
        # "GFP-EWSR1 (full length)" -> EWSR1
        name = c["construct"].split("-", 1)[1].split(" ")[0]
        wt_seq[name] = c["protein_sequence"]
        rec = _summarise(c["protein_sequence"], name)
        rec["committed_rg_dipeptides_total"] = c.get("rg_dipeptides_total")
        rec["rg_self_check"] = (
            "✅ re-derived count matches the committed one"
            if rec["motif_counts"]["RG"] == c.get("rg_dipeptides_total") else
            f"⛔ DISAGREES — re-derived {rec['motif_counts']['RG']}, committed "
            f"{c.get('rg_dipeptides_total')}. One of the two counters is wrong; do not quote "
            f"either until this is resolved.")
        wt[name] = rec

    fusions = []
    for c in des["constructs"]:
        five = "TAF15" if c["id"].startswith("TAF15") else "EWSR1"
        jr = c.get("junction_in_residue_numbering") or {}
        # ⚠ `five_prime_residues_fully_encoded`, NOT the seam index. Every one of these junctions
        # splits a codon, so the seam residue is a hybrid encoded by both partners and belongs to
        # neither; counting it as retained 5' sequence would be a one-residue lie in the direction
        # that flatters the motif count. The conservative boundary is the last FULLY encoded
        # residue, and a motif spanning the seam is not a wild-type 5' site in any case.
        last = jr.get("five_prime_residues_fully_encoded")
        rec = {
            "id": c["id"],
            "label": c["label"],
            "reported_rank": c.get("reported_rank"),
            "five_prime_partner": five,
            "last_five_prime_residue_retained": last,
            "junction_in_residue_numbering": jr,
        }
        if last:
            keep = _retained(wt[five]["positions"], last)
            rec["five_prime_motif_sites_retained"] = keep
            rec["five_prime_motif_sites_in_wildtype"] = wt[five]["motif_counts"]
            rec["fraction_of_five_prime_wildtype_retained"] = {
                m: (round(keep[m] / wt[five]["motif_counts"][m], 3)
                    if wt[five]["motif_counts"][m] else None) for m in MOTIFS}
        # ⭐ THE WHOLE PROTEIN, NOT JUST THE RETAINED 5' HALF. A methyltransferase sees the fusion,
        # and the 3' partner contributes its own sites; counting only the FET half would understate
        # the substrate the enzyme actually meets.
        rec["whole_fusion_protein"] = {
            "length_aa": c.get("protein_length_aa"),
            "motif_counts": {m: len(_positions(c["protein_sequence"], m)) for m in MOTIFS},
        }
        fusions.append(rec)

    # ⭐ THE FUSIONS THE MECHANISM WAS MEASURED IN, ON THE SAME RULER. This is the whole point of
    # the file: a transfer between diseases is only as good as the comparison it rests on, and
    # until now that comparison had never been made on PRMT5's own motif. Their breakpoints are
    # already sourced in the designs artifact; only the motif arithmetic is new here.
    comparators = []
    for c in ((des.get("rgg_dose_calibration_and_predictions") or {})
              .get("measured_comparator_fusions") or []):
        last = c.get("ewsr1_residues_retained")
        if not last:
            continue
        keep = _retained(wt["EWSR1"]["positions"], last)
        comparators.append({
            "comparator": c.get("comparator"),
            "_role": c.get("_role"),
            "breakpoint_provenance": c.get("breakpoint_provenance"),
            "five_prime_residues_retained": last,
            "five_prime_motif_sites_retained": keep,
            "fraction_of_five_prime_wildtype_retained": {
                m: (round(keep[m] / wt["EWSR1"]["motif_counts"][m], 3)
                    if wt["EWSR1"]["motif_counts"][m] else None) for m in MOTIFS},
            "committed_rg_dipeptides_retained": c.get("rg_dipeptides_retained"),
            "rg_self_check": ("✅ matches the committed count"
                              if keep["RG"] == c.get("rg_dipeptides_retained") else
                              f"⛔ DISAGREES — re-derived {keep['RG']}, committed "
                              f"{c.get('rg_dipeptides_retained')}"),
        })

    ewsr1 = wt["EWSR1"]
    ceiling = (cen.get("wild_type_annotation") or {}).get("EWSR1", {})
    return {
        "_title": "PRMT5's measured substrate motif (GRG) mapped onto EMC's fusion protein, and "
                  "onto the fusions the mechanism has actually been measured in.",
        "_generated_by": "research/modalities/emc_prmt5_substrate_motif_map.py",
        "_sources": {
            "sequences_and_junctions": "research/modalities/emc-fet-construct-designs.json "
                                       "(wild_type_controls.controls[*].protein_sequence, "
                                       "constructs[*].junction_in_residue_numbering)",
            "rgg_boxes_and_ceiling": "research/modalities/emc-fet-idr-census.json "
                                     "(wild_type_annotation)",
            "the_motif": "PMID 30940768 (Musiani et al., Sci Signal 2019) — PRMT5 prefers arginine "
                         "sandwiched between two glycines (GRG). Retrieved 2026-08-09 via "
                         "fetch-literature.yml, slug prmt5-substrate-motif.",
        },
        "_this_computes_nothing_about_efficacy": "⛔ Nothing here asserts efficacy, safety, a "
            "therapeutic window or clinical readiness for any agent in any disease. It locates a "
            "sequence motif in a protein sequence.",
        "motifs": MOTIFS,
        "wild_type_proteins": wt,
        "⭐_the_headline": {
            "question": "Which half of EWSR1 carries PRMT5's motif, and does the fusion keep it?",
            "ewsr1_length_aa": ewsr1["length_aa"],
            "first_GRG_residue": ewsr1["first_occurrence_residue"]["GRG"],
            "first_RG_residue": ewsr1["first_occurrence_residue"]["RG"],
            "rgg_free_ceiling_from_the_census": ceiling.get("rgg_free_ceiling"),
            "rgg_boxes_from_the_census": ceiling.get("rgg_boxes"),
            "_reading": "⭐ NO GRG SITE LIES IN EWSR1's FIRST 300 RESIDUES. That segment — the "
                        "SYGQ-rich transactivation region every EWSR1 fusion retains — carries "
                        "none of the 11 sites; all of them lie beyond residue 300, in the two "
                        "RGG-rich regions the fusion truncates. How many survive is decided by "
                        "the breakpoint, and it differs between EMC transcript types.",
            "⚠_do_not_write_this_as_c_terminal_half": "Residue 301 of 656 is at 46% of the "
                "protein, so 'the C-terminal half' is false by ~27 residues and a test in "
                "tests/test_emc_prmt5_substrate_motif_map.py rejects that wording. The accurate "
                "statement is the narrower one above, and it is not weaker: what matters is that "
                "the RETAINED segment carries no site, not where the midpoint falls.",
        },
        "fusion_constructs": fusions,
        "measured_comparator_fusions_on_the_same_ruler": comparators,
        "⛔_the_limits": [
            "A MOTIF IS NOT A METHYLATION EVENT. Nothing here shows any FET fusion protein is "
            "methylated, that PRMT5 is the enzyme, or that it matters in this disease.",
            "THE MOTIF IS NOT NECESSARY. EWSR1::FLI1 (Ewing, type 1) retains none of EWSR1's RG "
            "dipeptides, and PRMT5 inhibition still reduces Ewing viability in an EWSR1::FLI1-"
            "dependent manner (PMID 40823091). So a fusion retaining zero sites is NOT predicted "
            "to be unresponsive, and any motif-stratified prediction is falsifiable rather than "
            "expected.",
            "PRMT5 HAS MANY SUBSTRATES THAT ARE NOT THE FUSION — Sm proteins, histones, and "
            "R-loop-resolution factors among them (PMID 31267554) — and its route into a fusion "
            "sarcoma may run through none of the fusion's own sequence.",
            "GRG IS A PREFERENCE, NOT A RULE. PRMT5 methylates arginines outside GRG, and a GRG "
            "site is not necessarily methylated. Counting sites bounds opportunity, not activity.",
            "BREAKPOINT FREQUENCIES ARE REPORTED, NOT MEASURED HERE. Which EMC transcript type a "
            "given patient carries is a fact about that patient, and this repository has no EMC "
            "cohort of its own to weight the types by.",
        ],
    }


def main():
    res = build()
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(res, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    print(f"wrote {os.path.relpath(OUT, os.path.dirname(HERE))}")
    h = res["⭐_the_headline"]
    print(f"  EWSR1 {h['ewsr1_length_aa']} aa — first GRG at {h['first_GRG_residue']}, "
          f"first RG at {h['first_RG_residue']}")
    for n, w in res["wild_type_proteins"].items():
        print(f"  WT {n:6} GRG={w['motif_counts']['GRG']:3} RG={w['motif_counts']['RG']:3}  "
              f"{w['rg_self_check'][:52]}")
    for f in res["fusion_constructs"]:
        k = f.get("five_prime_motif_sites_retained") or {}
        w = f["whole_fusion_protein"]["motif_counts"]
        print(f"  {f['id']:20} 5'kept GRG={k.get('GRG')} RG={k.get('RG')}  "
              f"| whole fusion GRG={w['GRG']} RG={w['RG']}")
    for c in res["measured_comparator_fusions_on_the_same_ruler"]:
        k = c["five_prime_motif_sites_retained"]
        print(f"  [measured] {c['comparator'][:46]:48} res={c['five_prime_residues_retained']:4} "
              f"GRG={k['GRG']:2} RG={k['RG']:2}  {c['rg_self_check'][:30]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
