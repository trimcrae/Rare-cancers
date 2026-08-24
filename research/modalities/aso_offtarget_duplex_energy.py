#!/usr/bin/env python3
"""Energy-based re-evaluation of the near-matches an alignment screen returns. ($0, CPU, offline)

⛔ WHY THIS EXISTS, AND IT IS SOMEBODY ELSE'S RECOMMENDATION RATHER THAN THIS PROJECT'S IDEA.
The 2025 industry recommendations on hybridisation-dependent off-target assessment (Andersson et al.,
Nucleic Acid Ther 35:16-33, PMID 39912803) prescribe a two-stage in-silico search, verbatim:

    "A practical strategy is to first run a sequence similarity search (e.g., BLAST-like search) in
     an overly sensitive configuration (suffering low specificity) and consider further evaluation
     of the remaining candidates with more complex search models like energy-based models for ASOs."

and, immediately before it, the reason the second stage is not optional:

    "Although comparably fast and computationally practical, simple alignment tools are poor at
     predicting ONT hybridization. ... Models based on thermodynamic simulation, dynamic
     programming, or nearest-neighbors can be more representative of ONT-RNA occupancy than edit
     distance."

This repository had stage one and not stage two. Every near-match behind the panel is graded on EDIT
DISTANCE — 14 of 16 positions paired, with the catalytic gap paired or not — which is the measure the
recommendations name as the weak one. ⭐ AND THE GAP WAS ALREADY WRITTEN DOWN HERE, INDEPENDENTLY:
`aso_offtarget_tissue_expression.py`'s header says the step from "this gene is expressed in liver" to
"this reagent does something in liver" "needs an affinity argument no screen in this repository has
made". This module makes that argument's first half — occupancy — and nothing beyond it.

★ WHAT IS COMPUTED, AND WHY IT IS THE HONEST FORM OF THE QUESTION. A near-match is not a duplex; it
is an alignment with mismatches in it. Nearest-neighbour parameters for INTERNAL MISMATCHES in a
DNA:RNA hybrid are not in the packaged table, and inventing them would produce numbers that look
exactly like measured ones — the failure this repository keeps paying for. So nothing is invented:
what is computed is the nearest-neighbour stability of the LONGEST CONTIGUOUS PERFECTLY PAIRED RUN
inside each alignment, from the same Sugimoto table, on the same strand convention, through the same
functions as `junction_aso_thermo.py`. Every base pair entering a sum is a real Watson-Crick pair
with a real tabulated parameter.

⚠ THAT CHOICE HAS A DIRECTION AND IT IS STATED RATHER THAN HIDDEN. Ignoring the mismatched positions
and the flanking paired stretches beyond the longest run UNDERSTATES the true duplex stability of a
near-match, because a mismatch does not annihilate the pairing either side of it. So the separation
this module reports between an off-target and the intended duplex is an UPPER bound on the
separation, not a lower one — the opposite direction from the LNA argument below, and the two must
never be quoted as if they pointed the same way.

⛔ WHAT THIS IS NOT — each line is a reading this artifact must never be given:
  · NOT a cleavage prediction. RNase-H1 needs a paired DNA gap, which is a geometric requirement no
    free energy encodes; the gap-pairing column is carried separately for exactly that reason.
  · NOT a measurement. Every value is a calculation from a published parameter table.
  · NOT a statement about the modified oligonucleotide. The table is for an unmodified DNA:RNA
    hybrid (see `⚠_lna_not_modelled`).
  · NOT a safety, efficacy, therapeutic-window or clinical-readiness claim about any sequence, and
    NOT a risk ranking: an off-target with a stable paired core has not been shown to be engaged,
    cleaved, or expressed where the reagent goes.

Usage:
  python3 research/modalities/aso_offtarget_duplex_energy.py            # write the artifact
  python3 research/modalities/aso_offtarget_duplex_energy.py --check    # reproduce it, exit 1 on drift
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import aso_screen_sets as ass  # noqa: E402  (path set above)
import junction_aso_thermo as thermo  # noqa: E402

OUT = os.path.join(HERE, "aso-offtarget-duplex-energy.json")

#: ⛔⛔ THE GEOMETRY COMES FROM THE LOADER, NOT FROM A CONSTANT AND NEVER FROM A FILENAME.
#: The first cut of this module globbed `junction-aso-offtarget-*.json`, excluded the 18-mer and
#: 20-mer screens by matching "18mer"/"20mer" IN THE NAME, and carried its own OLIGO_LEN/WING pair.
#: `tests/test_one_geometry_screen_loading.py` failed it, and correctly: that file exists because
#: exactly this shape — a filename convention used as a geometry discriminator, beside a hard-coded
#: 5-6-5 gap span — once applied the 16-mer's gap window (6, 11) to 18-mer designs and moved
#: `best_available` at the three seams the manuscript recommends. It produced a WRONG NUMBER, not a
#: crash, and a human caught it. Every screen below is now reached through `load_screens`, which
#: MEASURES each artifact's geometry from its designs and refuses to hand back a mixed bag, and the
#: catalytic-gap span is read off the ScreenSet rather than declared here.
GEOMETRY = ass.MANUSCRIPT_GEOMETRY

#: The two reagents the condensed article names for synthesis, keyed to the junction each is named
#: at. The EWSR1 e12 molecule is also tiled at TAF15 e11 and FUS e10 — one sequence spanning three
#: partners' breakpoints — so it appears three times in `designs` and must be pinned to the junction
#: the manuscript names it at, or the same reagent would be reported under three labels.
NAMED_REAGENTS = {
    "GGGCATATCATCAAAC": "EWSR1_e12__NR4A3_e3",
    "GGGCATATCTTGTGTG": "TAF15_e6__NR4A3_e3",
}

#: ⛔ ONE SCREEN PER JUNCTION, CHOSEN BY A STATED RULE OVER CONTENT RATHER THAN OVER NAMES.
#: A junction can have a base screen, a screen at a deeper search ceiling, and re-runs under
#: different parent-exclusion sets. Counting all of them would count the same molecule's hits
#: several times. The rule is: the screen returning the MOST alignment records for that junction,
#: which is the deepest reading available of it. The chosen file is named per junction in the
#: artifact so the choice is auditable rather than asserted. ⚠ The selection reads each artifact's
#: OWN record count — never its filename — which is the distinction the loader's docstring draws
#: about `select`.


def _screens_by_junction():
    """{junction_label: Screen} — the deepest screen of the manuscript geometry at each junction."""
    best = {}
    for screen in ass.load_screens(GEOMETRY, ass.BLAST_SCREEN, root=HERE):
        label = screen.junction_label
        if not label or not screen.artifact.get("oligos"):
            continue
        n = sum(len(o.get("offtargets") or []) for o in screen.artifact["oligos"])
        if label not in best or n > best[label][1]:
            best[label] = (screen, n)
    return {label: screen for label, (screen, _n) in best.items()}


def _longest_paired_run(midline):
    """(start, length) of the longest contiguous run of paired positions, 0-based into the alignment.

    A BLAST midline marks an identity with `|` and anything else with a space, so the run is exactly
    a maximal `|` block. Ties take the FIRST such run, which is arbitrary and is recorded as such:
    the LENGTH is what the metric uses, and two runs of equal length can differ in stability, so the
    artifact carries the sequence of the run it scored.
    """
    best_i = best_n = cur_i = cur_n = 0
    for i, c in enumerate(midline):
        if c == "|":
            if cur_n == 0:
                cur_i = i
            cur_n += 1
            if cur_n > best_n:
                best_i, best_n = cur_i, cur_n
        else:
            cur_n = 0
    return best_i, best_n


def _locked_positions(q_from, start, length, geometry):
    """How many β-D-oxy-locked residues the run pairs, on the geometry the screen was MEASURED at.

    Query positions are 1-based and the wings are everything outside the catalytic gap, which is
    read from `geometry` rather than declared here. This is the number that decides the DIRECTION
    of the LNA caveat, so it is counted per record rather than assumed to be smaller than the
    intended duplex's locked count.
    """
    gap_lo, gap_hi = geometry.gap_region_1based
    return sum(1 for k in range(length)
               if not gap_lo <= (q_from + start + k) <= gap_hi)


def _score(record, table, geometry):
    """The energy reading for one alignment record, or None where it cannot be taken honestly."""
    qseq, midline = record.get("qseq") or "", record.get("midline") or ""
    if len(qseq) != len(midline) or "-" in qseq:
        return None                      # a gapped alignment: the run's bases are not a clean duplex
    start, length = _longest_paired_run(midline)
    if length < 2:
        return None                      # a nearest-neighbour sum needs at least one stacked pair
    run = qseq[start:start + length]
    if any(b not in "ACGT" for b in run):
        return None
    dh, ds = thermo.duplex_enthalpy_entropy(run, table)
    if dh is None:
        return None
    q_from = int(record.get("q_from") or 1)
    return {
        "run_len": length,
        "run_seq": run,
        "run_query_from": q_from + start,
        "locked_residues_paired": _locked_positions(q_from, start, length, geometry),
        "dg37": thermo.delta_g37(dh, ds),
        "tm_c": round(thermo._tm(dh, ds), 3),
    }


def _design_row(oligo, table, geometry):
    target = oligo.get("target_mRNA_5to3") or ""
    dh, ds = thermo.duplex_enthalpy_entropy(target, table)
    if dh is None:
        return None
    dg_on = thermo.delta_g37(dh, ds)
    tm_on = round(thermo._tm(dh, ds), 3)

    scored, unscorable = [], 0
    for rec in oligo.get("offtargets") or []:
        s = _score(rec, table, geometry)
        if s is None:
            unscorable += 1
            continue
        s["risk"] = rec.get("risk")
        s["gap_mismatches"] = rec.get("gap_mismatches")
        s["acc"] = rec.get("acc")
        s["defn"] = rec.get("defn")
        s["ddg_vs_intended"] = round(s["dg37"] - dg_on, 3)
        s["dtm_vs_intended"] = round(tm_on - s["tm_c"], 3)
        scored.append(s)

    #: ⛔ THE HYBRIDISABLE SUBSET IS THE ONE THAT CAN MEAN ANYTHING. A minus-strand hit needs a
    #: transcription unit running the other way to be a duplex at all, and the screen already
    #: measured that per hit rather than assuming it. Both counts are carried so a reader can see
    #: what was set aside and why, but every headline below is over the hybridisable set.
    hyb = [s for s in scored if s["risk"] != "minus_strand_not_hybridisable"]
    gap_paired = [s for s in hyb if s["risk"] == "true_cleavage_risk"]
    worst = min(hyb, key=lambda s: s["ddg_vs_intended"], default=None)
    worst_gap = min(gap_paired, key=lambda s: s["ddg_vs_intended"], default=None)
    return {
        "antisense_5to3": oligo.get("antisense_5to3"),
        "target_mRNA_5to3": target,
        "dg37_intended_duplex": dg_on,
        "tm_intended_duplex_c": tm_on,
        "n_records": len(oligo.get("offtargets") or []),
        "n_scored": len(scored),
        "n_unscorable": unscorable,
        "n_hybridisable_scored": len(hyb),
        "n_gap_paired_scored": len(gap_paired),
        "min_ddg_any_hybridisable": worst["ddg_vs_intended"] if worst else None,
        "min_ddg_gap_paired": worst_gap["ddg_vs_intended"] if worst_gap else None,
        "max_run_len_hybridisable": max((s["run_len"] for s in hyb), default=None),
        "max_locked_paired_hybridisable": max((s["locked_residues_paired"] for s in hyb),
                                              default=None),
        "n_hybridisable_within_2_kcal": sum(1 for s in hyb if s["ddg_vs_intended"] < 2.0),
        "n_gap_paired_within_2_kcal": sum(1 for s in gap_paired if s["ddg_vs_intended"] < 2.0),
        "closest_gap_paired_record": worst_gap,
    }


def build():
    table, provenance = thermo._nn_table()
    if table is None:
        return None
    chosen = _screens_by_junction()
    junctions, designs = {}, []
    for label in sorted(chosen):
        screen = chosen[label]
        art = screen.artifact
        rows = [r for r in (_design_row(o, table, screen.geometry) for o in art["oligos"]) if r]
        for r in rows:
            r["junction"] = label
        designs.extend(rows)
        junctions[label] = {
            "screen_file": screen.name,
            "geometry": screen.geometry.architecture,
            "n_alignment_records": sum(len(o.get("offtargets") or []) for o in art["oligos"]),
            "n_designs": len(rows)}

    scored_designs = [r for r in designs if r["min_ddg_any_hybridisable"] is not None]
    gapped = [r for r in designs if r["min_ddg_gap_paired"] is not None]
    #: ⛔ A NUMBER THE MANUSCRIPT QUOTES NEEDS A KEY HERE, NOT A READER'S ARITHMETIC OVER `designs`.
    #: The condensed article states how many designs carry a fully paired off-target duplex and how
    #: close the two named reagents' nearest gap-paired near-matches come. Both were derivable from
    #: the per-design rows and neither had a home, which is the one-fact-one-place failure this
    #: repository's consistency linter exists to catch. The rounded keys are emitted because the
    #: prose quotes one decimal and a pinned figure compares strings.
    fully_paired = [r for r in gapped if r["min_ddg_gap_paired"] <= 0.0]
    named = {}
    for r in designs:
        if r["antisense_5to3"] in NAMED_REAGENTS and r["junction"] == NAMED_REAGENTS[
                r["antisense_5to3"]]:
            named[NAMED_REAGENTS[r["antisense_5to3"]]] = {
                "antisense_5to3": r["antisense_5to3"],
                "dg37_intended_duplex": r["dg37_intended_duplex"],
                "n_gap_paired_scored": r["n_gap_paired_scored"],
                "closest_gap_paired_ddg": r["min_ddg_gap_paired"],
                "closest_gap_paired_ddg_1dp": round(r["min_ddg_gap_paired"], 1),
                "n_gap_paired_within_2_kcal": r["n_gap_paired_within_2_kcal"],
                "locked_residues_paired_by_closest":
                    (r["closest_gap_paired_record"] or {}).get("locked_residues_paired"),
            }
    return {
        "_title": "Energy-based re-evaluation of alignment-screen near-matches, 16-mer 5-6-5 panel",
        "_generated_by": "research/modalities/aso_offtarget_duplex_energy.py",
        "_what": ("For every near-match an alignment screen returned, the nearest-neighbour "
                  "stability of the longest contiguous perfectly paired run inside that alignment, "
                  "against the same quantity for the intended 16/16 duplex of the same design."),
        "_why": ("The 2025 industry recommendations (PMID 39912803) prescribe following an "
                 "over-sensitive similarity search with an energy-based re-evaluation of the "
                 "candidates it returns, because edit distance predicts hybridisation poorly. This "
                 "panel had the first stage and not the second."),
        "⛔_this_is_not_a_cleavage_prediction": (
            "RNase-H1 requires a paired DNA gap, a geometric requirement no free energy encodes. "
            "The gap-pairing verdict is carried per record, from the screen that measured it, and "
            "is never merged into the energy column."),
        "⚠_the_bound_runs_one_way": (
            "Scoring only the longest perfectly paired run ignores pairing either side of a "
            "mismatch, so it UNDERSTATES a near-match's true stability and therefore OVERSTATES "
            "its separation from the intended duplex. Every ddG here is an upper bound on that "
            "separation."),
        "⚠_lna_not_modelled": (
            "The table is for an unmodified DNA:RNA hybrid. The intended duplex pairs all ten "
            "locked residues of a 5-6-5 design; `max_locked_paired_hybridisable` reports the most "
            "any near-match's scored run pairs, which is what decides whether locked chemistry "
            "would widen or narrow the separation. This premise — more locked pairs, more "
            "stabilisation — is the one junction_aso_thermo.py already runs on, and is adopted "
            "rather than measured here."),
        "⚠_and_the_two_bounds_point_opposite_ways": (
            "The run-length choice overstates the separation; unmodelled LNA understates it where "
            "the intended duplex pairs more locked residues than the near-match does. They are not "
            "a range and must not be quoted as one."),
        "method": {
            "metric": ("delta_G37 and Tm of the longest contiguous run of BLAST-identity positions "
                       "in each alignment, computed on the query (target mRNA) strand"),
            "ddg_vs_intended": "dg37(best run) - dg37(intended 16/16 duplex); positive = weaker",
            "geometry": GEOMETRY.as_dict(),
            "screen_choice_rule": ("per junction, the screen returning the most alignment records. "
                                   "Screens are reached through aso_screen_sets.load_screens, which "
                                   "measures each artifact's geometry from its own designs, so a "
                                   "screen of another geometry cannot enter this set and no "
                                   "filename is used as a discriminator."),
            "records_not_scored": ("gapped alignments, alignments whose midline and query differ in "
                                   "length, runs shorter than two bases, and runs containing a "
                                   "non-ACGT base. Counted per design as n_unscorable, never "
                                   "dropped silently."),
            "headline_subset": ("hybridisable records only — the screen measured strand agreement "
                                "per hit and minus-strand hits are excluded from every summary"),
        },
        "parameters": provenance,
        "conditions": {"strand_conc_nM": thermo.CONC_NM, "T_for_dG_K": thermo.T37},
        "junctions": junctions,
        "summary": {
            "n_junctions": len(junctions),
            "n_designs": len(designs),
            "n_alignment_records": sum(j["n_alignment_records"] for j in junctions.values()),
            "n_records_scored": sum(r["n_scored"] for r in designs),
            "n_records_unscorable": sum(r["n_unscorable"] for r in designs),
            "min_ddg_across_panel": min((r["min_ddg_any_hybridisable"] for r in scored_designs),
                                        default=None),
            "min_ddg_gap_paired_across_panel": min((r["min_ddg_gap_paired"] for r in gapped),
                                                   default=None),
            "n_designs_with_a_gap_paired_near_match_within_2_kcal":
                sum(1 for r in gapped if r["n_gap_paired_within_2_kcal"] > 0),
            "n_designs_with_any_gap_paired_near_match": len(gapped),
            "n_designs_with_a_fully_paired_offtarget_duplex": len(fully_paired),
            "⚠_fully_paired_means_the_run_covers_all_sixteen": (
                "A design counted here has a hybridisable near-match whose longest perfectly paired "
                "run is the whole 16-mer, so its ddG against the intended duplex is 0.000 by "
                "construction. Edit distance called it a near-match like any other; this is the "
                "class the energy re-evaluation exists to separate out."),
        },
        "named_reagents": named,
        "designs": designs,
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true",
                    help="rebuild and compare against the committed artifact")
    args = ap.parse_args(argv)

    d = build()
    if d is None:
        print("REFUSED: Biopython is not installed, so the nearest-neighbour table cannot be read. "
              "No artifact written — a hand-entered table would be indistinguishable from this one.",
              file=sys.stderr)
        return 1

    if args.check:
        if not os.path.exists(OUT):
            print(f"::error::{OUT} is missing", file=sys.stderr)
            return 1
        old = json.load(open(OUT, encoding="utf-8"))
        # The package version travels with the parameters and legitimately differs between machines;
        # every scientific value is compared.
        a = {k: v for k, v in old.items() if k != "parameters"}
        b = {k: v for k, v in d.items() if k != "parameters"}
        if a != b:
            print(f"::error::{os.path.basename(OUT)} is stale — re-run without --check",
                  file=sys.stderr)
            return 1
        print(f"{os.path.basename(OUT)}: current")
        return 0

    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(d, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    s = d["summary"]
    print(f"wrote {OUT}: {s['n_records_scored']} of {s['n_alignment_records']} alignment records "
          f"scored over {s['n_designs']} designs at {s['n_junctions']} junctions", file=sys.stderr)
    print(f"  closest hybridisable near-match, whole panel: ddG {s['min_ddg_across_panel']} kcal/mol",
          file=sys.stderr)
    print(f"  closest with the catalytic gap fully paired:  ddG "
          f"{s['min_ddg_gap_paired_across_panel']} kcal/mol", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
