#!/usr/bin/env python3
"""Can a PGR::NR4A3 gapmer engage WILD-TYPE PGR — the parent a healthy woman expresses?

⛔ WHY THIS QUESTION IS DIFFERENT AT THIS SEAM AND AT NO OTHER IN THE LANE.
Every junction-spanning gapmer shares half its window with each parent by construction, and for the
five FET-family partners that is tolerable arithmetic: EWSR1, TAF15, FUS, TCF12 and TFG are
broadly-expressed housekeeping-ish transcripts whose engagement is a general specificity question,
argued in the manuscript for the whole panel. PGR is not that kind of gene. The 5' partner of the
fusion in PMID 36103645 is the PROGESTERONE RECEPTOR, a hormone receptor of normal breast, uterus
and ovary, and the reported patient was a 35-year-old woman. A design whose catalytic gap can be
paired by wild-type PGR transcript is therefore not a footnote about specificity; it is the single
most decision-relevant reading this seam has.

★ WHAT THIS MEASURES, EXACTLY.
For every design at every junction in the non-coding-acceptor atlas, every 16-nt window of every
partner's MATURE transcript is compared to the design's target window, and two things are recorded:
  (a) the number of mismatches, retained at <= 2 — the same >=14/16 threshold the BLAST arm uses, so
      the two are comparable; and
  (b) whether the hit pairs ALL SIX bases of the catalytic DNA gap, because RNase-H1 cleaves only
      across a contiguously paired gap. A wing-only match is an affinity liability; a gap-paired one
      is the class that could direct cleavage of the parent.
The gap-pairing kernel is `aso_parent_gap_pairing.longest_run_through_gap`, imported rather than
reimplemented — a second definition of "pairs the gap" is exactly the drift that module's own header
records paying for.

⚠ FORWARD ORIENTATION ONLY, AND THAT IS A STATEMENT ABOUT WHAT EXISTS, NOT A SHORTCUT. An antisense
oligonucleotide hybridises to the SENSE strand of a mature transcript; the reverse complement of a
mature mRNA is not a molecule present in the cytoplasm. `aso_parent_gap_pairing` makes the same
choice for the same reason. The genome screen is where the other orientation belongs, because there
both strands are real.

⛔ WHAT THIS IS NOT — and each line is a claim this file must never be read as making.
  · NOT the tissue-expression screen, and NOT a substitute for it. That screen asks where the
    OFF-TARGET LOCI of a BLAST search are expressed; it needs a transcriptome-wide search at this
    seam plus a GTEx fetch, both of which need the network. This file asks a narrower question it
    can answer offline and exactly: does any partner transcript, PGR included, pair a design's gap.
  · NOT an expression measurement. It does not say how much PGR any tissue makes. This repository
    holds no committed GTEx record for PGR — `aso-offtarget-tissue-expression-inputs.json` carries
    19 loci, and PGR is not among them — so the expression half of the exposure question is an
    ABSENT READING here and is named as one rather than filled in.
  · NOT a cleavage prediction, a potency claim, an efficacy claim or a safety claim. A sequence
    match at two mismatches is a sequence match. Whether such a duplex is an RNase-H1 substrate is
    an affinity question no screen in this repository answers.
  · NOT a coverage claim. PGR is in neither partner-genotyped EMC cohort this repository counts
    against; `aso_coverage_ladder.py` owns that consequence and it is zero.

Run:
    python3 research/modalities/pgr_parent_engagement.py           # $0, offline, CPU only
    python3 research/modalities/pgr_parent_engagement.py --check   # is the artifact current?
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import junction_aso as ja                       # noqa: E402  — transcript models, one home
import aso_parent_gap_pairing as pgp            # noqa: E402  — the gap-pairing kernel, one home
import aso_screen_sets as ass                   # noqa: E402  — the geometry, one home

_SUFFIX = os.environ.get("OUT_SUFFIX", "-noncoding-acceptor")
ATLAS = os.path.join(HERE, os.environ.get("ATLAS_JSON")
                     or f"nr4a3-fusion-junction-atlas{_SUFFIX}.json")
OUT = os.path.join(HERE, f"pgr-parent-engagement{_SUFFIX}.json")

#: The same <=2 mismatches over the oligo length the BLAST arm's >=14/16 threshold expresses.
MAX_MISMATCHES = 2


def _partners(atlas):
    """{symbol: mature cDNA} for every transcript the atlas actually built its seams from.

    ⚠ READ FROM THE ATLAS, NOT LISTED HERE. The atlas records which transcript it used per gene; a
    hand-kept list beside it is how a screen ends up reporting a gene it did not search, or
    searching a transcript the seam was not built from.
    """
    out = {}
    for sym, rec in atlas["transcripts"].items():
        m = ja.transcript_model(sym)
        if m["transcript"] != rec["transcript"]:
            raise RuntimeError(
                f"{sym}: the atlas was built on {rec['transcript']} but the committed cache now "
                f"holds {m['transcript']}. Refusing to screen a seam against a different "
                "transcript from the one it was designed on.")
        out[sym] = m["cdna"]
    return out


def scan_one(target, partners):
    """Every <=2-mismatch window of every partner cDNA, gap-resolved. Exhaustive, forward only."""
    L = len(target)
    hits = []
    for sym, seq in sorted(partners.items()):
        for i in range(len(seq) - L + 1):
            w = seq[i:i + L]
            mm = 0
            for k in range(L):
                if w[k] != target[k]:
                    mm += 1
                    if mm > MAX_MISMATCHES:
                        break
            if mm > MAX_MISMATCHES:
                continue
            run = pgp.longest_run_through_gap(w, target)
            hits.append({
                "gene": sym,
                "cdna_start_0based": i,
                "mismatches": mm,
                "gap_fully_paired": bool(run),
                "longest_run_bp_through_gap": run,
                # ⚠ A gap-paired hit whose contiguous duplex is shorter than the hybrid-binding
                # threshold is still recorded, with the number, rather than filtered — the threshold
                # is a STATED value (aso_parent_gap_pairing.MIN_DUPLEX_BP, anchored to PMID 35664704
                # and not measured for a 5-6-5 LNA gapmer), and filtering on a stated value hides
                # the sensitivity of the answer to it.
                "meets_stated_hybrid_length_floor": bool(run >= pgp.MIN_DUPLEX_BP),
            })
    hits.sort(key=lambda h: (h["mismatches"], -h["longest_run_bp_through_gap"], h["gene"]))
    return hits


def build():
    geom = ass.MANUSCRIPT_GEOMETRY
    if (ja.OLIGO_LEN, ja.WING) != (geom.oligo_len, geom.wing):
        raise RuntimeError(
            f"geometry drift: junction_aso is at {ja.OLIGO_LEN}-mer/wing {ja.WING}, the manuscript "
            f"panel at {geom.oligo_len}/{geom.wing}. `aso_parent_gap_pairing.GAP` is derived from "
            "the first and this artifact would be graded against the wrong six columns.")
    atlas = json.load(open(ATLAS, encoding="utf-8"))
    partners = _partners(atlas)

    junctions = []
    for pan in atlas["panels"]:
        rows = []
        for d in pan.get("designs") or []:
            if not d.get("fusion_specific"):
                continue
            hits = scan_one(d["target_mRNA_5to3"], partners)
            gap_paired = [h for h in hits if h["gap_fully_paired"]]
            rows.append({
                "antisense_5to3": d["antisense_5to3"],
                "target_mRNA_5to3": d["target_mRNA_5to3"],
                "gap_specificity_margin": d.get("gap_specificity_margin"),
                "n_partner_near_matches_le2mm": len(hits),
                "n_gap_paired": len(gap_paired),
                "n_gap_paired_meeting_the_stated_hybrid_floor":
                    sum(1 for h in gap_paired if h["meets_stated_hybrid_length_floor"]),
                "gap_paired_genes": sorted({h["gene"] for h in gap_paired}),
                "hits": hits,
            })
        junctions.append({
            "junction_label": pan["junction_label"],
            "donor_symbol": pan["donor_symbol"],
            "n_designs": len(rows),
            "n_designs_with_any_partner_near_match": sum(1 for r in rows
                                                         if r["n_partner_near_matches_le2mm"]),
            "n_designs_with_a_gap_paired_partner_hit": sum(1 for r in rows if r["n_gap_paired"]),
            "designs": rows,
        })

    pgr_rows = [r for j in junctions if j["donor_symbol"] == "PGR" for r in j["designs"]]
    pgr_hits = [h for r in pgr_rows for h in r["hits"] if h["gene"] == "PGR"]
    return {
        "_what": ("Exhaustive <=2-mismatch scan of every non-coding-acceptor design against the "
                  "MATURE transcript of every partner the atlas was built on, gap-resolved. The "
                  "question it exists for: can wild-type PGR — a hormone receptor of normal breast, "
                  "uterus and ovary — pair the catalytic gap of a PGR::NR4A3 junction gapmer?"),
        "_cost": "$0 — CPU only, committed transcript models, no network, no GPU, no rental.",
        "_what_this_is_not": [
            "NOT the tissue-expression screen and no substitute for it. That screen asks where a "
            "BLAST search's OFF-TARGET LOCI are expressed and needs both a transcriptome-wide "
            "search at this seam and a GTEx fetch — network, therefore CI.",
            "NOT an expression measurement. No TPM, no tissue, no organ. This repository holds no "
            "committed GTEx record for PGR at all, and that is an absent reading, not a low one.",
            "NOT a cleavage, potency, efficacy, safety, therapeutic-window or clinical-readiness "
            "claim. A sequence match at two mismatches is a sequence match.",
            "NOT a coverage claim. PGR is in neither partner-genotyped EMC cohort this repository "
            "counts against; the coverage consequence is zero and aso_coverage_ladder.py owns it.",
        ],
        "method": {
            "geometry": ass.MANUSCRIPT_GEOMETRY.as_dict(),
            "max_mismatches": MAX_MISMATCHES,
            "_threshold_note": ("<=2 mismatches over 16 nt is the >=14/16 identity the BLAST arm "
                                "uses, chosen so the two arms are comparable."),
            "orientation": "forward only",
            "_orientation_note": ("an antisense oligonucleotide hybridises to the SENSE strand of a "
                                  "mature transcript; the reverse complement of an mRNA is not a "
                                  "molecule present in the cell. The genome screen is where the "
                                  "other orientation is real."),
            "gap_kernel": "aso_parent_gap_pairing.longest_run_through_gap",
            "stated_hybrid_length_floor_bp": pgp.MIN_DUPLEX_BP,
            "_floor_note": ("a STATED value anchored to PMID 35664704, not a measurement for a "
                            "5-6-5 LNA gapmer — see aso_parent_gap_pairing. Hits below it are "
                            "recorded with their run length rather than filtered."),
            "atlas": os.path.basename(ATLAS),
            "partners_searched": sorted(partners),
            "partner_transcripts": {s: atlas["transcripts"][s]["transcript"] for s in partners},
            "partner_cdna_nt": {s: len(v) for s, v in sorted(partners.items())},
            "_transcript_source": ja.transcript_source_provenance(),
        },
        "headline_pgr": {
            "_question": "Does any PGR::NR4A3 design engage wild-type PGR transcript?",
            "n_designs": len(pgr_rows),
            "n_near_matches_in_wild_type_PGR_le2mm": len(pgr_hits),
            "n_gap_paired_in_wild_type_PGR": sum(1 for h in pgr_hits if h["gap_fully_paired"]),
            "longest_run_bp_through_gap_in_wild_type_PGR":
                max([h["longest_run_bp_through_gap"] for h in pgr_hits], default=0),
            "⚠_what_a_zero_here_does_and_does_not_mean": (
                "A zero says no window of the wild-type PGR MATURE transcript comes within two "
                "mismatches of a design's target window. It does NOT say the reagent is safe in "
                "breast, uterus or ovary: pre-mRNA, the rest of the transcriptome and the genome "
                "are other compartments, each with its own screen, and none of them has run at "
                "this seam."),
        },
        "n_junctions": len(junctions),
        "junctions": junctions,
    }


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    art = build()
    new = json.dumps(art, indent=1, sort_keys=False, ensure_ascii=False) + "\n"
    if "--check" in argv:
        cur = open(OUT, encoding="utf-8").read() if os.path.exists(OUT) else ""
        if cur != new:
            print(f"{os.path.basename(OUT)} is stale; re-run without --check", file=sys.stderr)
            return 1
        print("PGR parent-engagement artifact is current")
        return 0
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(new)
    print(f"wrote {os.path.basename(OUT)}", file=sys.stderr)
    h = art["headline_pgr"]
    print(f"  wild-type PGR: {h['n_near_matches_in_wild_type_PGR_le2mm']} near-matches "
          f"(<=2 mm) over {h['n_designs']} PGR::NR4A3 designs; "
          f"{h['n_gap_paired_in_wild_type_PGR']} pair the catalytic gap; longest run through the "
          f"gap {h['longest_run_bp_through_gap_in_wild_type_PGR']} bp", file=sys.stderr)
    for j in art["junctions"]:
        print(f"  {j['junction_label']}: "
              f"{j['n_designs_with_any_partner_near_match']}/{j['n_designs']} designs have any "
              f"partner near-match; {j['n_designs_with_a_gap_paired_partner_hit']} have a "
              f"gap-paired one", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
