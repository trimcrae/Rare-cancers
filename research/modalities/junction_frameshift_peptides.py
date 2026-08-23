#!/usr/bin/env python3
"""What antigen, if any, do the OUT-OF-FRAME EWSR1::NR4A3 junctions supply?

WHY THIS EXISTS. `fusion_breakpoints.py` grades 27 declared exon pairs and emits peptides for the 5
that are in frame. The other 22 are graded out and then never looked at again — and an external
reviewer asked the obvious question (aiXiv 1364, W3 and suggestion 1): a frameshifted junction reads
the acceptor exon in a novel frame, so every residue after the seam is non-self until a stop codon.
In other tumours that class is the RICHEST antigen source available, not the poorest. Grading a
junction out for not producing the driver is not the same as showing it produces no antigen, and
until this script the manuscript could not tell the two apart.

⛔ WHAT THIS SCREEN IS NOT ABOUT. The 27 pairs are a COMBINATORIAL WINDOW (9 donor exons x 3 acceptor
exons), not observed breakpoints. A frameshifted EWSR1::NR4A3 cannot encode the chimeric
transcription factor that defines EMC, so a tumour carrying one is not driven by it and these
peptides are NOT offered as EMC vaccine targets. What the screen establishes is the SIZE of the
antigen supply a frameshift at this locus would provide if one were ever observed — which is a fact
about the locus, and is the question the reviewer actually asked.

WHAT IS COMPUTED, per out-of-frame junction:
  * the novel tract: translation of the chimeric ORF from the donor's own initiator codon, taken
    from the first residue not wholly donor-encoded through to the first stop. `fusion_breakpoints`
    translation already halts at a stop, so the tract is exactly what the ribosome would make.
  * every 8- to 11-mer of that tract, filtered against both parent proteins as elsewhere in this
    lane, and (in CI) MHCflurry over the same 34-allele panel at the same cut §2.3 uses.
  * ⭐ THE NMD POSITION TEST, which is what makes a short tract a finding rather than a curiosity.
    A stop codon more than 50 nt upstream of the final exon-exon junction of a transcript is the
    canonical nonsense-mediated-decay configuration. That is a POSITIONAL criterion computed from
    the transcript model here, and it is a PREDICTION about the transcript's fate, not a
    measurement of it: no decay assay is run and none is claimed.

Output: junction-frameshift-peptides.json
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MATRIX = os.path.join(HERE, "epitope-allele-matrix.json")
OUT = os.path.join(HERE, "junction-frameshift-peptides.json")

LENGTHS = [8, 9, 10, 11]
RANK_STRONG = 0.5
#: The distance upstream of the last exon-exon junction beyond which a stop is an NMD target. 50 nt
#: is the canonical rule; it is a rule of thumb in the literature, and is reported as one.
NMD_NT = 50


def novel_kmers(tract, ep, np_):
    """Every 8- to 11-mer of the tract absent from both parent proteins."""
    out = set()
    for L in LENGTHS:
        for i in range(len(tract) - L + 1):
            k = tract[i:i + L]
            if k not in ep and k not in np_:
                out.add(k)
    return sorted(out)


def nmd_reading(ja, acceptor, a_start, fusion, left_len, stop_nt):
    """Is the premature stop >NMD_NT nt upstream of the LAST exon-exon junction of the chimera?

    The chimeric transcript's junctions after the seam are the acceptor's own exon boundaries,
    shifted by the length of the retained donor part minus where the acceptor piece was cut.
    """
    shift = left_len - ja.exon_tx_start(acceptor, a_start)
    junctions = [e + shift for e in acceptor["tx_ends"][:-1] if e + shift > left_len]
    if not junctions:
        return {"last_exon_junction_nt": None, "distance_nt": None, "nmd_predicted": None,
                "⚠": "no exon-exon junction downstream of the seam; the rule does not apply"}
    last = max(junctions)
    d = last - stop_nt
    return {"last_exon_junction_nt": int(last), "stop_codon_nt": int(stop_nt),
            "distance_upstream_nt": int(d), "rule_nt": NMD_NT,
            "nmd_predicted": bool(d > NMD_NT),
            "⚠_this_is_positional_not_measured": (
                "the 50-nt rule is a positional criterion on the transcript, not an assay. No decay "
                "measurement is made here and none is claimed.")}


def main():
    sys.path.insert(0, HERE)
    import junction_aso as ja
    import fusion_breakpoints as fb

    ews = ja.transcript_model("EWSR1")
    nr4 = ja.transcript_model("NR4A3")
    ep = ews["protein"].replace("*", "").rstrip("X")
    np_ = nr4["protein"].replace("*", "").rstrip("X")
    graded = ja.graded_window(ews, nr4, keep_sequences=True)
    oof = [g for g in graded if g["grade"] == "OUT_OF_FRAME"]
    if not oof:
        print("  no OUT_OF_FRAME junctions in the declared window", file=sys.stderr)
        return 1

    rows, all_peps = [], set()
    for g in oof:
        j = ja.mrna_junction(ews, nr4, g["EWSR1_exon_end"], g["NR4A3_exon_start"])
        orf_start = ews["utr5_len"]
        prot = fb.translate(j["_fusion"][orf_start:])
        j0 = j["ewsr1_last_whole_residue"]
        tract = prot[j0:]
        peps = novel_kmers(tract, ep, np_)
        all_peps.update(peps)
        stop_nt = orf_start + 3 * len(prot)          # first nt of the stop codon, transcript coords
        rows.append({
            "junction_label": j["junction_label"],
            "grade": g["grade"], "why": g["why"],
            "chimeric_protein_length": len(prot),
            "seam_residue_index": j0,
            "novel_tract": tract,
            "novel_tract_length_aa": len(tract),
            "n_novel_peptides": len(peps),
            "novel_peptides": peps,
            "nmd": nmd_reading(ja, nr4, j["NR4A3_exon_start"], j["_fusion"], len(j["_left"]),
                               stop_nt),
        })

    # ⭐ The tracts are not independent: a frameshift into the SAME acceptor exon reads the same
    # nucleotides in the same shifted frame, so the tracts differ only where the seam codon does.
    # Reporting a total that adds them up would overstate the antigen supply several-fold.
    shared = {}
    for r in rows:
        shared.setdefault(r["novel_tract"][1:], []).append(r["junction_label"])
    convergent = {k: v for k, v in shared.items() if len(v) > 1}

    # ⛔ `binders` STAYS None UNTIL A PREDICTOR ACTUALLY RAN. An empty list would serialise as
    # "0 strong binders", which is a reading of absence produced by an absent reading — the exact
    # substitution this repository has paid for before.
    binders, predictor_note = None, "NOT SCREENED — MHCflurry absent (CI supplies it)"
    try:
        from mhcflurry import Class1PresentationPredictor
        panel = json.load(open(MATRIX))["panel"]
        pred = Class1PresentationPredictor.load()
        df = pred.predict(peptides=sorted(all_peps), alleles={a: [a] for a in panel}, verbose=0)
        col = ("presentation_percentile" if "presentation_percentile" in df.columns
               else "affinity_percentile")
        binders = sorted(({"peptide": r["peptide"], "allele": str(r["best_allele"]),
                           "percentile": round(float(r[col]), 4)}
                          for _, r in df.iterrows() if float(r[col]) <= RANK_STRONG),
                         key=lambda b: b["percentile"])
        predictor_note = (f"MHCflurry over the same {len(panel)}-allele panel at the same cut "
                          f"({RANK_STRONG}) as epitope-allele-matrix.json")
    except ImportError:
        pass

    result = {
        "_what": ("Novel peptide supply from the OUT-OF-FRAME EWSR1::NR4A3 exon pairs — the "
                  "frameshifted read-through tract of each, its 8- to 11-mers, and whether the "
                  "premature stop sits in the canonical nonsense-mediated-decay configuration."),
        "_why": ("aiXiv review 1364 asked whether the graded-out junctions could supply novel-ORF "
                 "antigen. Grading a junction out for not producing the driver does not show it "
                 "produces no antigen, and nothing here had looked."),
        "⛔_what_this_is_not": (
            "NOT a set of EMC vaccine targets. The 27 exon pairs are a combinatorial window, not "
            "observed breakpoints, and a frameshifted junction cannot encode the chimeric "
            "transcription factor that defines the disease — so a tumour carrying one is not driven "
            "by it. Predicted binding remains a screen, not presentation or immunogenicity."),
        "_method": ("chimeric mRNA per junction_aso.mrna_junction; translation from the donor's own "
                    "initiator codon, halting at the first stop; tract = first residue not wholly "
                    "donor-encoded onward; 8- to 11-mers filtered against both parent proteins; "
                    f"NMD by the {NMD_NT}-nt positional rule against the chimera's last exon-exon "
                    "junction. " + predictor_note),
        "n_out_of_frame_junctions": len(rows),
        "n_distinct_novel_peptides": len(all_peps),
        "shortest_tract_aa": min(r["novel_tract_length_aa"] for r in rows),
        "longest_tract_aa": max(r["novel_tract_length_aa"] for r in rows),
        "n_predicted_strong_binders": None if binders is None else len(binders),
        "strong_binders": binders,
        "⚠_binding_scope": (predictor_note if binders is None else
                            "screened; a count of 0 here is a measured zero"),
        "convergent_tracts": {
            "⚠_why_this_matters": (
                "junctions frameshifting into the SAME acceptor exon read the same nucleotides in "
                "the same shifted frame, so their tracts differ only at the seam codon. Summing "
                "their peptide counts would overstate the antigen supply several-fold."),
            "shared_tract_after_the_seam_residue": {k: v for k, v in convergent.items()},
        },
        "junctions": rows,
    }
    json.dump(result, open(OUT, "w"), indent=2)
    print(f"  frameshift screen: {len(rows)} out-of-frame junctions, tracts "
          f"{result['shortest_tract_aa']}-{result['longest_tract_aa']} aa, "
          f"{len(all_peps)} distinct novel peptides, "
          f"{'NOT SCREENED for binding' if binders is None else str(len(binders)) + ' strong binders'}; "
          f"NMD predicted for "
          f"{sum(1 for r in rows if r['nmd'].get('nmd_predicted'))}/{len(rows)}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
