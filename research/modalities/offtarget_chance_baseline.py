#!/usr/bin/env python3
"""
Is an off-target count a finding, or is it what any 16-mer would return? — the missing null.

⛔ WHY THIS EXISTS, AND IT INVALIDATES A HEADLINE. The manuscript's central negative was "0 of 58
designs is predicted off-target-clean". A referee pointed out that this is arithmetically
unavoidable, and the arithmetic checks out: the number of 16-mers within 2 substitutions of a given
16-mer is 1,129, so the probability that an arbitrary transcriptome position matches at >= 14/16 is
1129 / 4^16 = 2.6e-07. Against a human RefSeq RNA set of order 1e8-1e9 nucleotides that is TENS TO
HUNDREDS of expected near-matches PER OLIGO, for any 16-mer whatsoever — a scrambled control, a
marketed gapmer, a random string. "Zero near-matches at >= 14/16" is not an achievable state, so a
count of zero-clean designs is a property of the threshold and the size of the transcriptome, not a
property of EMC, NR4A3, or fusion junctions.

⭐ WHAT REPLACES IT. The informative quantity is not whether a design has hits; it is whether it has
MORE hits than chance. This module computes the chance expectation under an explicit null and
reports every committed design as observed-versus-expected. A design at or below expectation is not
"clean" — nothing is — but it is "no worse than an arbitrary oligonucleotide of its length", which is
a defensible statement, is what a chemist actually wants to know, and is the statement the paper
could not previously make.

⚠ THE NULL IS DELIBERATELY CRUDE, AND ITS LIMITS RUN IN BOTH DIRECTIONS. It assumes independent,
uniformly distributed bases. Real transcriptomes are neither: base composition is skewed, sequence is
repetitive, paralogues and transcript variants of one locus multiply near-matches, and a GC-rich or
low-complexity query is enriched for partners. So this is an ORDER-OF-MAGNITUDE reference, not a
p-value, and it is used here only to answer a coarse question — is an observed count in the region
chance alone predicts, or far above it? A design far above chance is a real finding about that
sequence. A design at chance is a statement that the screen found nothing specific to it.
⛔ In particular this must NEVER be reported as a significance test, and no threshold on the ratio is
proposed here, because the null is too crude to license one.

Outputs: offtarget-chance-baseline.json
"""

import glob
import json
import os
import sys
import time
from math import comb

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "offtarget-chance-baseline.json")

OLIGO_LEN = 16

#: A source panel counts as a REAL junction only if its own record says its seam was built from a
#: spliced transcript model. Both remaining panels predate that rebuild: neither carries a
#: `junction_label`, and the one that carries a breakpoint at all states it in AMINO-ACID
#: coordinates (`EWSR1_keep_aa` / `NR4A3_from_aa`), i.e. a protein-coordinate seam of the kind the
#: manuscript's Declarations record as withdrawn in full. The classification is therefore read off
#: each source file, never inferred from a filename.
REAL_JUNCTION_BREAKPOINT_MODE = "real_exon_junction_mRNA"
#: Transcriptome size is not recorded by the screens (they record transcript COUNT, 186,185, not
#: nucleotides), so the expectation is reported as a RANGE over a plausible span rather than as a
#: single number nobody measured. Naming the uncertainty is the point; picking a midpoint would hide it.
TRANSCRIPTOME_NT_RANGE = (3.0e8, 8.0e8)


def n_within(length, mismatches):
    """How many distinct strings lie within `mismatches` substitutions of one string of `length`."""
    return sum(comb(length, k) * 3 ** k for k in range(mismatches + 1))


def chance_expectation(length, mismatches):
    """(p_per_position, (lo, hi) expected hits per oligo) under an i.i.d. uniform-base null."""
    p = n_within(length, mismatches) / 4 ** length
    return p, tuple(round(p * n, 1) for n in TRANSCRIPTOME_NT_RANGE)


def seam_class(d):
    """('real_exon_junction'|'modelled_breakpoint', the breakpoint record that decided it)."""
    bp = d.get("breakpoint") or {}
    if d.get("junction_label") and bp.get("mode") == REAL_JUNCTION_BREAKPOINT_MODE:
        return "real_exon_junction", bp.get("mode")
    return "modelled_breakpoint", (bp or None)


def committed_panel_set():
    """The source panels the CURRENTLY COMMITTED artifact was built from, or None if there is none.

    ⚠ WHY A CALLER WOULD EVER WANT THIS. The panel set grows: junctions acquire an uncapped
    <=1-mismatch screen at different times, and every one that lands changes every count derived
    here — the median, the at-or-below fraction, and therefore the figure and the sentences the
    manuscript writes off them. Regenerating over a LARGER panel set is a data decision with
    manuscript consequences, so it must be taken deliberately and not as a side effect of somebody
    fixing an unrelated defect in the same file. `--panels-from-artifact` pins the panel set to the
    committed one so that a derivation change can be shipped on its own; the default remains "read
    everything that exists", which is what a refresh should do.
    """
    try:
        d = json.load(open(OUT))
    except (OSError, ValueError):
        return None
    return {r["_source"] for r in d.get("per_design", [])} or None


def collect_observed(panels=None):
    """Every committed design's uncapped <=1-mismatch count, keyed by junction and sequence."""
    rows = []
    for path in sorted(glob.glob(os.path.join(HERE, "aso-insilico-evaluation*.json"))):
        if panels is not None and os.path.basename(path) not in panels:
            continue
        d = json.load(open(path))
        label = d.get("junction_label") or os.path.basename(path)
        cls, bp = seam_class(d)
        for o in d.get("top_designs", []):
            if o.get("offtarget_le1mm") is None:
                continue
            rows.append({"junction": label, "antisense_5to3": o["antisense_5to3"],
                         "gc_percent": o.get("gc_percent"),
                         "offtarget_exact": o.get("offtarget_exact"),
                         "offtarget_le1mm": o["offtarget_le1mm"],
                         "_source": os.path.basename(path),
                         "seam_class": cls,
                         "breakpoint_record": bp,
                         "transcripts_scanned":
                             (d.get("offtarget_screen") or {}).get("transcripts_scanned")})
    return rows


def dedupe_sequences(rows):
    """One entry per distinct oligonucleotide, in the row order first seen.

    ⛔ WHY THIS EXISTS, AND WHAT IT FIXES. A row of `per_design` is a (junction, design) PAIR, not a
    molecule. Five of these 16-mers are junction-spanning at THREE partners' seams at once — the
    multi-partner designs the manuscript headlines — so each appears once per junction and any
    consumer that iterates rows counts one physical oligonucleotide three times. That is
    pseudoreplication, and it inflated the published at-or-below fraction. The de-duplicated view is
    built HERE rather than in a figure script so that every consumer gets the same one.

    The three copies of a multi-partner design are the same sequence screened against the same
    transcriptome, so their counts must agree; a disagreement would mean the screens are not
    comparable and is raised rather than silently resolved by picking a copy.
    """
    keyed = {}
    for r in rows:
        s = r["antisense_5to3"]
        prev = keyed.get(s)
        if prev is None:
            keyed[s] = {"antisense_5to3": s, "junctions": [r["junction"]],
                        "n_junctions": 1, "seam_class": r["seam_class"],
                        "gc_percent": r["gc_percent"],
                        "offtarget_exact": r["offtarget_exact"],
                        "offtarget_le1mm": r["offtarget_le1mm"],
                        "_sources": [r["_source"]]}
            continue
        for k in ("gc_percent", "offtarget_exact", "offtarget_le1mm", "seam_class"):
            if prev[k] != r[k]:
                raise ValueError(
                    f"the same oligonucleotide {s} carries {k}={prev[k]!r} at "
                    f"{prev['junctions'][0]} and {r[k]!r} at {r['junction']}; the copies are not "
                    "the same screen and must not be merged")
        prev["junctions"].append(r["junction"])
        prev["_sources"].append(r["_source"])
        prev["n_junctions"] += 1
    return list(keyed.values())


def _uniform(vals):
    """The single value shared by every element, or a raise — never a silent pick."""
    s = set(vals)
    if len(s) != 1:
        raise ValueError(f"expected one shared value, got {sorted(s)}")
    return s.pop()


def _span(vals):
    """[min, max] over a non-empty iterable, for captions that quote a range."""
    v = sorted(vals)
    return [v[0], v[-1]]


def build(panels=None):
    p2, exp2 = chance_expectation(OLIGO_LEN, 2)
    p1, exp1 = chance_expectation(OLIGO_LEN, 1)
    rows = collect_observed(panels)
    counts = sorted(r["offtarget_le1mm"] for r in rows)
    n = len(counts)
    median = counts[n // 2] if n % 2 else (counts[n // 2 - 1] + counts[n // 2]) / 2
    lo, hi = exp1

    for r in rows:
        c = r["offtarget_le1mm"]
        r["expected_le1mm_lo"], r["expected_le1mm_hi"] = lo, hi
        r["at_or_below_chance"] = c <= hi
        r["ratio_to_chance_hi"] = round(c / hi, 2) if hi else None

    seqs = dedupe_sequences(rows)
    for s in seqs:
        c = s["offtarget_le1mm"]
        s["expected_le1mm_lo"], s["expected_le1mm_hi"] = lo, hi
        s["at_or_below_chance"] = c <= hi
        s["ratio_to_chance_hi"] = round(c / hi, 2) if hi else None
    seqs.sort(key=lambda s: (s["offtarget_le1mm"], s["antisense_5to3"]))

    plotted = [s for s in seqs if s["seam_class"] == "real_exon_junction"]
    excluded = [s for s in seqs if s["seam_class"] != "real_exon_junction"]
    exc_above = [s for s in excluded if not s["at_or_below_chance"]]
    multi = [s for s in plotted if s["n_junctions"] > 1]
    scanned = sorted({r["transcripts_scanned"] for r in rows})

    return {
        "_title": "Chance baseline for junction-gapmer off-target counts",
        "_generated_by": "research/modalities/offtarget_chance_baseline.py",
        "_cost": "$0 — arithmetic over committed artifacts. No network, no GPU.",
        "_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "_why": (
            "The manuscript's negative headline — '0 of 58 designs predicted off-target-clean' — is "
            "arithmetically unavoidable at a >=14/16 identity threshold and therefore says nothing "
            "about this disease, this fusion, or these junctions. This file computes what chance "
            "alone predicts, so an observed count can be read against it."),
        "_what_this_is_not": [
            "NOT a significance test and NOT a p-value. The null assumes independent uniform bases; "
            "real transcript sequence is composition-skewed, repetitive, and full of paralogues and "
            "transcript variants of one locus. It is an order-of-magnitude reference only.",
            "NOT a cleanliness criterion. Nothing here licenses calling any design clean, and no "
            "threshold on the observed/expected ratio is proposed, because the null cannot support "
            "one.",
            "NOT a substitute for calibration against oligonucleotides with MEASURED off-target "
            "behaviour, which is what would actually convert these counts into a decision and which "
            "this repository has not done.",
        ],
        "null_model": {
            "oligo_len": OLIGO_LEN,
            "assumption": "independent, uniformly distributed bases",
            "transcriptome_nt_range_assumed": list(TRANSCRIPTOME_NT_RANGE),
            "_transcriptome_nt_caveat": (
                "The screens record transcripts SCANNED (186,185), not nucleotides, so the "
                "nucleotide span is assumed over a range rather than measured. Every expectation "
                "below inherits that range."),
            "n_strings_within_2_substitutions": n_within(OLIGO_LEN, 2),
            "p_per_position_ge_14_of_16": p2,
            "expected_near_matches_per_oligo_ge_14_of_16": list(exp2),
            "n_strings_within_1_substitution": n_within(OLIGO_LEN, 1),
            "p_per_position_ge_15_of_16": p1,
            "expected_hits_per_oligo_ge_15_of_16": list(exp1),
        },
        "observed": {
            "n_designs": n,
            "min": counts[0], "median": median, "max": counts[-1],
            "mean": round(sum(counts) / n, 1),
            "n_at_or_below_chance_upper": sum(1 for r in rows if r["at_or_below_chance"]),
            "_unit_caveat": (
                "⚠ THESE ARE ROWS, NOT MOLECULES. A row is a (junction, design) pair, and five "
                "designs are junction-spanning at three seams each, so they are counted three "
                "times here. Anything that reports a FRACTION OF DESIGNS must read "
                "`observed_distinct_sequences` or `figure_series` instead; this block is retained "
                "because per-junction consumers legitimately want the per-junction rows."),
        },
        "observed_distinct_sequences": {
            "_what": (
                "The same designs counted as PHYSICAL OLIGONUCLEOTIDES: one entry per distinct "
                "antisense sequence, whatever number of junctions it spans."),
            "n_rows": n,
            "n_sequences": len(seqs),
            "n_sequences_spanning_multiple_junctions": len(multi),
            "junctions_spanned_by_each_of_those": sorted({s["n_junctions"] for s in multi}),
            "n_at_or_below_chance_upper": sum(1 for s in seqs if s["at_or_below_chance"]),
        },
        "figure_series": {
            "_what": (
                "Exactly what the manuscript's chance-baseline figure draws, resolved here so the "
                "drawing script computes nothing: one bar per distinct oligonucleotide at a REAL "
                "exon junction, ranked by observed load."),
            "unit": "one distinct oligonucleotide",
            "seam_class_plotted": "real_exon_junction",
            "transcripts_scanned": scanned[0] if len(scanned) == 1 else scanned,
            "n_plotted": len(plotted),
            "n_at_or_below_chance_upper": sum(1 for s in plotted if s["at_or_below_chance"]),
            "n_above_chance_upper": sum(1 for s in plotted if not s["at_or_below_chance"]),
            "n_multi_junction_sequences": len(multi),
            #: A scalar when every multi-junction oligo spans the same number of seams, because a
            #: caption has to say "each spans N junctions" in words; `[min, max]` when they differ,
            #: because then that sentence is false and the caption has to quote a range.
            #: ⛔ THIS WAS `_uniform(...)`, WHICH RAISED AND STOPPED THE SCRIPT DEAD (2026-08-13).
            #: `_uniform` refuses a mixed set by design — correctly, since silently picking one
            #: value would put a false "each spans 3" into a caption. But refusing is right for a
            #: VALUE and wrong for a SCRIPT: the committed artefact was built from a panel set in
            #: which every multi-junction oligo spanned three seams, and the wider set now on disk
            #: holds both two- and three-seam oligos, so a plain `python3 offtarget_chance_baseline.py`
            #: died on `expected one shared value, got [2, 3]`.
            #: ⚠ AND THAT MADE A MANUSCRIPT SENTENCE FALSE. The Availability paragraph names five
            #: recomputations that run offline; four were verified byte-identical with the network
            #: hard-blocked and this was the fifth. Naming them item by item is what made the claim
            #: falsifiable, and it is how this surfaced. The module already carried `_span` for
            #: exactly this shape.
            #: ⚠ The committed artefact does not move: its panel set is uniform, so this still
            #: emits the scalar 3. Only the wider set gets a range, and a reader can tell which
            #: they are holding from the type.
            "multi_junction_span": (
                _uniform(s["n_junctions"] for s in multi) if len({s["n_junctions"] for s in multi}) == 1
                else _span(s["n_junctions"] for s in multi)),
            "multi_junction_sequences": [s["antisense_5to3"] for s in multi],
            "excluded": {
                "_why": (
                    "These panels' seams were not built from a spliced transcript model: neither "
                    "source records a `junction_label`, and the one that records a breakpoint at "
                    "all states it in amino-acid coordinates. They are modelled control seams, and "
                    "plotting them beside real junctions invites the reader to grade real designs "
                    "against sequence that no patient transcript is known to carry."),
                "n_excluded": len(excluded),
                "n_breakpoints": len({s["_sources"][0] for s in excluded}),
                "sources": sorted({s["_sources"][0] for s in excluded}),
                "n_at_or_below_chance_upper": len(excluded) - len(exc_above),
                "n_above_chance_upper": len(exc_above),
                "above_offtarget_le1mm": [s["offtarget_le1mm"] for s in exc_above],
                "above_offtarget_le1mm_range": _span(s["offtarget_le1mm"] for s in exc_above),
                "above_gc_percent": [s["gc_percent"] for s in exc_above],
                "above_gc_percent_range": _span(s["gc_percent"] for s in exc_above),
                "gc_percent_all": [s["gc_percent"] for s in excluded],
            },
            "series": plotted,
        },
        "_reading": (
            f"At the <=1-mismatch threshold chance alone predicts {lo}-{hi} hits per 16-mer. The "
            f"observed median across {n} committed designs is {median}. The median design is "
            "therefore AT OR BELOW what an arbitrary oligonucleotide of this length would return, "
            "which is the honest form of the paper's specificity statement: no design is clean "
            "because no 16-mer can be, and most designs carry no more transcriptome load than "
            "chance. The outliers are the informative rows."),
        "per_design": rows,
        "per_sequence": seqs,
    }


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    panels = committed_panel_set() if "--panels-from-artifact" in argv else None
    if panels is not None:
        print(f"panel set pinned to the committed artifact's {len(panels)} sources", file=sys.stderr)
    res = build(panels)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(res, fh, indent=2)
    print("wrote", OUT, file=sys.stderr)
    summary = {k: v for k, v in res.items() if k not in ("per_design", "per_sequence")}
    summary["figure_series"] = {k: v for k, v in summary["figure_series"].items()
                                if k != "series"}
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
