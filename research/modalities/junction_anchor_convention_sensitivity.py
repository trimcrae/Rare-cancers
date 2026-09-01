#!/usr/bin/env python3
"""
How much of §B3's near-self null rests on the anchor convention, and exactly which position it
turns on.

⛔ WHY THIS EXISTS. `junction-selfsimilarity.json` reports that ZERO of the 11 predicted class I
junction binders has a near-self proteome neighbour whose differences are confined to anchor
positions — the worst case, because a peptide that differs from self only where the groove grips it
presents a near-identical surface to a T-cell receptor, and central tolerance would have deleted the
repertoire that sees it. That artifact states the null and, in the same file, states the caveat that
qualifies it:

    "Anchors taken as P2 and the C-terminus for every length, which is the general class I rule and
     not an allele-specific motif. HLA-A*01:01 reads P3 as a primary anchor; rows for peptides
     called on it are marked and should be read with that caveat."

A null computed under ONE convention is a statement about that convention until somebody measures
how far it travels. This module measures that, and it needs no new data: the mismatch POSITIONS are
already in the committed artifact, so the question "under which anchor sets would this hit have been
anchor-only?" is answerable exactly and exhaustively.

★ THE CONSTRUCTION, WHICH IS WHY THE ANSWER IS EXHAUSTIVE RATHER THAN A SAMPLE OF CONVENTIONS.
A hit is anchor-only under an anchor set A exactly when its mismatch positions are a SUBSET of A.
So the mismatch position set IS the minimal anchor set that would flip that hit — there is no
smaller one, and every superset of it also flips the hit. Reporting the minimal set per hit
therefore answers the question for EVERY convention anyone might bring, including ones this
repository has no source for, without enumerating them.

The named conventions below are then just readable labels over that lattice. Two are sourced from
the input artifact's own caveat; two are explicitly UNSOURCED sensitivity variants, and are marked
as such in the output so that no reader can mistake a variant for a motif read out of a database.

⛔ WHAT THIS IS NOT.
  - Not a safety result, and not a claim that any peptide is or is not immunogenic. Every input is a
    BINDING PREDICTION plus a sequence-distance search. Sequence distance is not receptor distance.
  - Not a determination of which anchor convention is correct for these alleles. This repository
    holds no allele-specific motif source, so where an allele's true anchor set is not known here
    the output says UNKNOWN rather than guessing. Deciding it needs a motif source (an allele-
    specific binding-motif dataset), which is a separate networked fetch nobody has run.
  - Not a new search. It re-reads one committed artifact and adds no proteome hit to it.

Inputs:  junction-selfsimilarity.json  (committed; generated 2026-08-23 by junction_selfsimilarity.py)
         novelty-seam-test.json       (committed; the acceptor gene's collision alphabet and stems),
                                      used only to test whether the flipped hits sit where the seam
                                      mechanism predicts — a corroboration, not an input to any count.
Output:  junction-anchor-convention-sensitivity.json
Cost:    $0 — pure local recomputation over committed artifacts. No network, no predictor, no GPU.
"""

import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SELFSIM = os.path.join(HERE, "junction-selfsimilarity.json")
SEAMTEST = os.path.join(HERE, "novelty-seam-test.json")
OUT = os.path.join(HERE, "junction-anchor-convention-sensitivity.json")


def load(path, what):
    if not os.path.exists(path):
        raise SystemExit(
            f"{what} is missing at {path}. It is committed, so regenerate it rather than writing "
            "an artifact that reports a sensitivity analysis over inputs nothing produced."
        )
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def mismatch_positions(query, self_peptide):
    """Recompute mismatch positions from the two sequences, 1-based from the N-terminus.

    ⛔ RECOMPUTED, NOT READ. The artifact records `mismatch_positions`, and this module derives them
    again from the peptide strings instead of trusting the field. That makes the input's own
    bookkeeping falsifiable here: a disagreement is reported as a defect rather than propagated.
    """
    if len(query) != len(self_peptide):
        return None
    return [i + 1 for i, (a, b) in enumerate(zip(query, self_peptide)) if a != b]


def anchor_set(length, positions_from_n, c_terminal_offsets):
    """Resolve a convention to concrete 1-based positions for a peptide of this length.

    `positions_from_n` are counted from the N-terminus (P1, P2, P3...). `c_terminal_offsets` are
    counted back from the C-terminus, 0 meaning the C-terminal residue itself (PΩ). Keeping the two
    apart is what lets one convention apply to 8-, 9-, 10- and 11-mers without a per-length table.
    """
    resolved = {p for p in positions_from_n if 1 <= p <= length}
    resolved |= {length - off for off in c_terminal_offsets if 1 <= length - off <= length}
    return resolved


# Two conventions SOURCED from the input artifact's own `⚠_anchor_convention` field, and two
# UNSOURCED variants included only to locate the position the null turns on. The `sourced` flag
# travels into the output on every row.
CONVENTIONS = [
    {
        "id": "P2_and_C_terminus",
        "positions_from_n": [2],
        "c_terminal_offsets": [0],
        "sourced": True,
        "source": "junction-selfsimilarity.json → ⚠_anchor_convention (the convention that artifact "
                  "states it used: 'P2 and the C-terminus for every length, which is the general "
                  "class I rule and not an allele-specific motif')",
        "role": "REPRODUCTION — this run must return the input artifact's own per-hit verdicts. A "
                "disagreement means one of the two files is wrong and is reported, not smoothed.",
    },
    {
        "id": "P2_P3_and_C_terminus",
        "positions_from_n": [2, 3],
        "c_terminal_offsets": [0],
        "sourced": True,
        "source": "junction-selfsimilarity.json → ⚠_anchor_convention, second clause: 'HLA-A*01:01 "
                  "reads P3 as a primary anchor'. Applied here to every peptide rather than only to "
                  "A*01:01 rows, which is the conservative direction: it can only ADD anchor-only "
                  "hits, never remove one.",
        "role": "SENSITIVITY — the widest set the input artifact itself names.",
    },
    {
        "id": "P1_P2_and_C_terminus",
        "positions_from_n": [1, 2],
        "c_terminal_offsets": [0],
        "sourced": False,
        "source": "UNSOURCED VARIANT. No allele-specific motif source in this repository says P1 is "
                  "an anchor for these alleles. Included solely to locate which position the null "
                  "turns on. A count under this row is NOT a claim that P1 is an anchor.",
        "role": "SENSITIVITY — unsourced.",
    },
    {
        "id": "P1_P2_P3_and_C_terminus",
        "positions_from_n": [1, 2, 3],
        "c_terminal_offsets": [0],
        "sourced": False,
        "source": "UNSOURCED VARIANT, as above, widened by the P3 clause. The most permissive set "
                  "considered; it is an upper bound on how many hits any convention over these "
                  "positions could call anchor-only.",
        "role": "SENSITIVITY — unsourced, upper bound.",
    },
]


def seam_corroboration(flipped, seamtest):
    """Do the flipped hits sit where the seam mechanism says they must, or somewhere else?

    ⛔ A CROSS-CHECK, NOT A COUNT. Nothing in the convention scoring depends on this block. It exists
    because "the differences are N-terminal" would otherwise be an observation with no mechanism, and
    an observation with no mechanism is the kind that does not transfer to another locus.

    novelty-seam-test.json holds the acceptor gene's COLLISION ALPHABET — the residues that, placed
    immediately 5' of a given acceptor STEM, reconstruct a normal isoform boundary. If a flipped
    hit's differences really are the seam, then the residues the query SHARES with its self
    neighbour, read from just after the last mismatch, must be exactly such a stem, or a collision
    residue followed by one. That is a string test over committed data with no free parameters.
    """
    alphabet = set(seamtest.get("collision_alphabet", []))
    stems = set()
    for residue, stem_list in (seamtest.get("stems_each_alphabet_residue_precedes") or {}).items():
        for s in stem_list:
            stems.add(s)
            stems.add(residue + s)
    rows = []
    for f in flipped:
        last = max(f["mismatch_positions"])
        shared_suffix = f["query"][last:]
        matches = shared_suffix in stems or (
            len(shared_suffix) > 1 and shared_suffix[0] in alphabet and shared_suffix[1:] in stems
        )
        rows.append({
            "query": f["query"],
            "self_peptide": f["self_peptide"],
            "accession": f["accession"],
            "mismatch_positions": f["mismatch_positions"],
            "shared_suffix_after_the_last_mismatch": shared_suffix,
            "suffix_is_an_acceptor_isoform_stem": matches,
        })
    return {
        "_what": "Whether each hit that the P1 convention flips is a seam-proximal peptide differing "
                 "from an acceptor-gene isoform at the seam, as novelty-seam-test.json's mechanism "
                 "predicts, rather than an unrelated coincidence of position.",
        "_source": "novelty-seam-test.json → collision_alphabet, stems_each_alphabet_residue_precedes",
        "collision_alphabet": sorted(alphabet),
        "n_flipped_hits": len(rows),
        "n_whose_shared_suffix_is_an_acceptor_isoform_stem": sum(
            1 for r in rows if r["suffix_is_an_acceptor_isoform_stem"]),
        "rows": rows,
    }


def main():
    selfsim = load(SELFSIM, "junction-selfsimilarity.json")
    seamtest = load(SEAMTEST, "novelty-seam-test.json")

    hits = []
    disagreements = []
    for q in selfsim["queries"]:
        query = q["peptide"]
        for h in q["hits"]:
            recomputed = mismatch_positions(query, h["self_peptide"])
            recorded = h.get("mismatch_positions")
            if recomputed is None:
                disagreements.append({
                    "query": query, "self_peptide": h["self_peptide"],
                    "defect": "length mismatch — a Hamming hit must be equal-length",
                })
                continue
            if recorded is not None and sorted(recorded) != recomputed:
                disagreements.append({
                    "query": query, "self_peptide": h["self_peptide"],
                    "recorded_mismatch_positions": recorded,
                    "recomputed_mismatch_positions": recomputed,
                    "defect": "the artifact's recorded mismatch positions do not match the sequences",
                })
            hits.append({
                "query": query,
                "length": len(query),
                "alleles_called_on": [b["allele"] for b in q.get("predicted_binders", [])],
                "self_peptide": h["self_peptide"],
                "accession": h["accession"],
                "protein": h["protein"],
                "n_mismatches": len(recomputed),
                "mismatch_positions": recomputed,
                # The lattice statement: this IS the minimal anchor set that would flip this hit.
                "minimal_anchor_set_that_would_call_this_anchor_only": recomputed,
                "minimal_set_in_c_terminal_terms": [
                    (f"P{p}" if p < len(query) else "P_omega") for p in recomputed
                ],
                "exact_self": len(recomputed) == 0,
                "artifact_all_mismatches_at_anchors": h.get("all_mismatches_at_anchors"),
            })

    scored = [h for h in hits if not h["exact_self"]]
    exact_self = [h for h in hits if h["exact_self"]]

    per_convention = []
    for conv in CONVENTIONS:
        flagged = []
        for h in scored:
            aset = anchor_set(h["length"], conv["positions_from_n"], conv["c_terminal_offsets"])
            if set(h["mismatch_positions"]) <= aset:
                flagged.append({
                    "query": h["query"], "self_peptide": h["self_peptide"],
                    "accession": h["accession"], "protein": h["protein"],
                    "mismatch_positions": h["mismatch_positions"],
                    "alleles_called_on": h["alleles_called_on"],
                })
        per_convention.append({
            "id": conv["id"],
            "anchor_positions": {
                "from_n_terminus": conv["positions_from_n"],
                "from_c_terminus_offsets": conv["c_terminal_offsets"],
            },
            "sourced": conv["sourced"],
            "source": conv["source"],
            "role": conv["role"],
            "n_hits_anchor_only": len(flagged),
            "n_queries_with_an_anchor_only_hit": len({f["query"] for f in flagged}),
            "queries_with_an_anchor_only_hit": sorted({f["query"] for f in flagged}),
            "anchor_only_hits": flagged,
        })

    # Reproduction check against the input artifact's own verdicts, under its own convention.
    baseline = next(c for c in per_convention if c["id"] == "P2_and_C_terminus")
    artifact_flagged = sorted({h["query"] for h in scored if h["artifact_all_mismatches_at_anchors"]})
    reproduction = {
        "this_run_under_the_artifacts_own_convention": baseline["queries_with_an_anchor_only_hit"],
        "the_artifacts_own_per_hit_verdicts": artifact_flagged,
        "agree": baseline["queries_with_an_anchor_only_hit"] == artifact_flagged,
        "artifact_headline_n_anchor_only_near_self_total": selfsim.get(
            "n_anchor_only_near_self_total"),
        "this_run_n_hits_anchor_only_under_that_convention": baseline["n_hits_anchor_only"],
    }

    # Which positions the null actually turns on: the union of the minimal sets of every hit that
    # is NOT anchor-only under the sourced baseline but IS under some considered variant.
    baseline_set = {(f["query"], f["self_peptide"]) for f in baseline["anchor_only_hits"]}
    turns_on = {}
    for conv in per_convention:
        if conv["id"] == "P2_and_C_terminus":
            continue
        for f in conv["anchor_only_hits"]:
            if (f["query"], f["self_peptide"]) in baseline_set:
                continue
            for p in f["mismatch_positions"]:
                turns_on.setdefault(str(p), 0)
                turns_on[str(p)] += 1
    added_positions = sorted(
        set(turns_on) - {str(p) for p in baseline["anchor_positions"]["from_n_terminus"]},
        key=int,
    )

    out = {
        "_what": "Sensitivity of §B3's near-self anchor-only null to the anchor convention, computed "
                 "exhaustively by recording the MINIMAL anchor set that would flip each hit.",
        "_why": "junction-selfsimilarity.json states the null and, in the same file, states that its "
                "anchor assignment is a general class I rule rather than an allele-specific motif. "
                "This measures how far the null travels across conventions instead of leaving the "
                "caveat unquantified.",
        "⛔_what_this_is_not": (
            "NOT a safety, immunogenicity or presentation result — every upstream input is a binding "
            "PREDICTION plus a sequence-distance search, and sequence distance is not T-cell-receptor "
            "distance. NOT a determination of the correct anchor convention for any allele: this "
            "repository holds no allele-specific motif source, so the true anchor set for each allele "
            "below is UNKNOWN here. NOT a new proteome search — one committed artifact is re-read and "
            "no hit is added to it."
        ),
        "_method": "for each recorded near-self hit, mismatch positions are RECOMPUTED from the two "
                   "peptide strings and cross-checked against the artifact's own field; a hit is "
                   "anchor-only under an anchor set A iff its mismatch positions are a subset of A, "
                   "so the mismatch position set is the minimal such A and every superset also "
                   "flips it. Named conventions are labels over that lattice, each carrying whether "
                   "it is sourced.",
        "_input": {
            "file": "junction-selfsimilarity.json",
            "generated_utc": selfsim.get("generated_utc"),
            "n_queries": selfsim.get("n_queries"),
            "max_mismatches": selfsim.get("max_mismatches"),
            "proteome": selfsim.get("_proteome"),
            "anchor_convention_declared_by_the_input": selfsim.get("⚠_anchor_convention"),
        },
        "_cost": "$0 — local recomputation over a committed artifact; no network, no predictor, no GPU.",
        "n_hit_records": len(hits),
        "n_scored_hits": len(scored),
        "n_exact_self_hits_excluded_from_scoring": len(exact_self),
        "⚠_exact_self_is_worse_than_anchor_only": (
            "An exact-self hit has no mismatches at all, so it is a strictly worse case than any "
            "anchor-only hit and is excluded from the convention scoring rather than counted as a "
            "clean negative. These are the §B5 withdrawals, not a finding of this module."
        ),
        "exact_self_hits": exact_self,
        "input_bookkeeping_disagreements": disagreements,
        "conventions": per_convention,
        "reproduction_of_the_input_artifacts_verdicts": reproduction,
        "the_null_turns_on_these_positions": {
            "positions_not_in_the_sourced_baseline_whose_inclusion_flips_at_least_one_hit":
                added_positions,
            "n_hits_each_such_position_participates_in": turns_on,
            "⚠_reading": "A position listed here is one whose anchor status decides the headline. "
                         "Its true status for the alleles involved is UNKNOWN in this repository.",
            "⚠_how_to_read_this_against_the_manuscript": (
                "§B3 of emc-vaccine-development-path.md does not merely adopt a convention: it gives "
                "a structural reason, that positions 1 and 5 'face outward or into the groove's "
                "middle rather than serving as the primary anchors at position 2 and the "
                "C-terminus'. That argument concerns PRIMARY anchors. It neither asserts nor "
                "excludes a secondary-anchor role at P1, and a secondary anchor is still a residue "
                "the T cell does not read. So this module does not show the manuscript is wrong. It "
                "shows the headline null is worth exactly the strength of the P1 premise, and that "
                "if P1 acts as an anchor for these alleles then six of the eleven binders fall into "
                "the configuration §B3 itself names as the worst case — 'an identical TCR-facing "
                "surface distinguished only by residues the T cell cannot see'."
            ),
        },
        "⛔_read_this_before_quoting_the_result_in_either_direction": (
            "Two live documents in this repository state OPPOSITE answers to which configuration "
            "deletes the repertoire, and this result speaks directly to that question. "
            "emc-vaccine-development-path.md §B3 calls anchor-only the worst case — 'an identical "
            "TCR-facing surface distinguished only by residues the T cell cannot see'. "
            "shared-vs-individualized-neoantigen-evidence.md, falsifier 3, instead says the route is "
            "in trouble if 'the seam residues fall at T-cell-receptor contact positions rather than "
            "anchors'. They cannot both be the failing configuration. This module does not "
            "adjudicate it: it reports WHERE the differences fall, exhaustively and per convention, "
            "and the direction that reading implies for the route depends on a reconciliation that "
            "has not happened. Do not quote this artifact as support for or against the route until "
            "it has."
        ),
        "alleles_whose_anchor_sets_are_unknown_here": sorted({
            a for h in scored for a in h["alleles_called_on"]
        }),
        "seam_mechanism_cross_check": seam_corroboration(
            max(per_convention, key=lambda c: c["n_hits_anchor_only"])["anchor_only_hits"],
            seamtest,
        ),
        "accessions_of_the_flipped_hits": sorted({
            f["accession"]
            for c in per_convention for f in c["anchor_only_hits"]
        }),
        "hits": hits,
    }

    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    print(f"wrote {OUT}")
    for c in per_convention:
        mark = "sourced" if c["sourced"] else "UNSOURCED"
        print(f"  {c['id']:<26} [{mark}]  hits={c['n_hits_anchor_only']}  "
              f"queries={c['n_queries_with_an_anchor_only_hit']}")
    print(f"  reproduction agrees with the input artifact: {reproduction['agree']}")
    print(f"  disagreements in input bookkeeping: {len(disagreements)}")
    print(f"  the null turns on positions: {added_positions}")


if __name__ == "__main__":
    main()
