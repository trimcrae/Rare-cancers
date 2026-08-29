#!/usr/bin/env python3
"""Predicted coverage as a CONTINUOUS FUNCTION of the acceptance threshold, not at three points.

WHAT QUESTION THIS SETTLES. The EMC junction-vaccine paper's central claim is that its coverage
figures bound the SCREEN rather than the junction — every presenting allele rests on a single
peptide-allele call, and all of those calls sit in a narrow band just under the 0.5 presentation
percentile the field uses by convention. §2.3 could state that at three points (0.45, 0.40, 0.37)
and nowhere else, because nothing computed the function; §7 concedes the threshold "this paper does
not defend"; and an external reviewer asked for exactly this, twice (aiXiv reviews 1363 and 1364,
"Provide a Threshold-Agnostic Analysis ... coverage as a continuous function").

⛔ THE POINT IS NOT TO RAISE THE COVERAGE NUMBER. It is to show that the number IS a function of a
parameter nobody defends, and to publish that function so a reader can pick their own cut and read
off what it gives. A curve that made the route look better would be the same defect the paper exists
to name, arriving from the other side — so the curve deliberately runs ABOVE the conventional cut
too, where coverage can only rise, and the paper reports what it finds there either way.

⚠ THIS IS A DIFFERENT AXIS FROM `coverage_scan.py`. That one sweeps the NUMBER OF ALLELES at a fixed
threshold (coverage-curve.json); this one sweeps the THRESHOLD over a fixed panel. Two of the three
knobs §2.3 says the figures move with — the third, panel breadth, is bounded there and not here.

PHASES, because the two halves of the curve need different inputs:
  A. PREDICT (needs MHCflurry; CI only). The committed `epitope-allele-matrix.json` stores only
     calls at or below 0.5, so above the conventional cut it would report "no new alleles" when in
     fact nothing was ever predicted there — an absent reading dressed as a reading of absence. So
     Phase A re-runs the same predictor over the same peptides and the same panel at a LOOSE cut and
     caches every call to `epitope-allele-loose-matrix.json`.
  B. CURVE (pure Python, runs anywhere). Falls back through: the cached loose matrix, then the
     strict matrix — and each fallback DECLARES the ceiling it can speak to rather than drawing a
     half curve that looks whole.

⚠ COVERAGE IS THE PAPER'S OWN FORMULA AND THE PAPER'S OWN FREQUENCIES — `hla_coverage.coverage_with_ci`
over AFND-pooled allele frequencies, 1 - prod(1-af)^2, carrier frequency under Hardy-Weinberg with
independence across loci — imported rather than reimplemented, so this curve and the manuscript's
headline number cannot disagree by construction. Its assumptions are the manuscript's §7 and §B1 and
are not restated here.

Outputs: epitope-allele-loose-matrix.json (Phase A), coverage-threshold-curve.json (Phase B)
"""
import json
import os
import sys

import hla_coverage as hc  # AFND fetch/pooling + the coverage formula itself (same dir)

HERE = os.path.dirname(os.path.abspath(__file__))
BREAKPOINTS = os.path.join(HERE, "fusion-breakpoint-neoantigens.json")
STRICT = os.path.join(HERE, "epitope-allele-matrix.json")
LOOSE_MATRIX = os.path.join(HERE, "epitope-allele-loose-matrix.json")
OUT = os.path.join(HERE, "coverage-threshold-curve.json")

#: The conventional cut. Named as a convention, not a defended value — that is the paper's point.
CONVENTIONAL = 0.5
#: How far above the convention to look. Deliberately permissive: the question is what a reader who
#: loosened the cut would be handed, and a grid stopping at 0.5 cannot answer it.
LOOSE = 5.0
LENGTHS = [8, 9, 10, 11]


def grid(calls):
    """A regular sweep PLUS every percentile at which the function actually steps.

    ⚠ A STEP FUNCTION SAMPLED ON A REGULAR GRID IS A DIFFERENT FUNCTION. On a 0.01 grid the four
    steps here land at 0.38, 0.41 and 0.46 — none of which is where anything happens, and the
    apparent 0.41 step silently merges two. So every call's own percentile is a grid point, and so
    is a hair below it, which is what makes each step readable as the single call that causes it.
    """
    pts = {round(0.01 * i, 4) for i in range(1, 51)}            # 0.01 .. 0.50 step 0.01
    pts |= {round(0.5 + 0.05 * i, 4) for i in range(1, 31)}     # 0.55 .. 2.00 step 0.05
    pts |= {round(2.0 + 0.25 * i, 4) for i in range(1, 13)}     # 2.25 .. 5.00 step 0.25
    for c in calls:
        pts.add(round(c["percentile"], 4))
        pts.add(round(c["percentile"] - 0.0001, 4))
    return sorted(p for p in pts if p > 0)


def predict_loose():
    """Phase A. Every (peptide, allele) call at or below LOOSE. Returns matrix dict or None."""
    try:
        from mhcflurry import Class1PresentationPredictor
    except ImportError:
        return None
    bp = json.load(open(BREAKPOINTS))
    peps = sorted({p for jn in bp.get("junctions", []) for p in jn.get("novel_peptides", [])
                   if len(p) in LENGTHS})
    panel = json.load(open(STRICT))["panel"]   # the same panel §2.3 reports, not a new one
    predictor = Class1PresentationPredictor.load()
    df = predictor.predict(peptides=peps, alleles={a: [a] for a in panel}, verbose=0)
    col = ("presentation_percentile" if "presentation_percentile" in df.columns
           else "affinity_percentile")
    calls = sorted(({"peptide": r["peptide"], "allele": str(r["best_allele"]),
                     "percentile": round(float(r[col]), 4)}
                    for _, r in df.iterrows() if float(r[col]) <= LOOSE),
                   key=lambda c: (c["percentile"], c["allele"], c["peptide"]))
    return {"_note": (f"MHCflurry calls at presentation percentile <= {LOOSE} over the same "
                      f"peptides and the same panel as epitope-allele-matrix.json, which stores "
                      f"only <= {CONVENTIONAL}. Exists so the threshold curve can run ABOVE the "
                      f"conventional cut on predictions rather than on absent data."),
            "panel": panel, "rank_column": col, "n_peptides": len(peps),
            "loose_threshold": LOOSE, "calls": calls}


def load_calls():
    """(calls, ceiling, provenance). `ceiling` is the largest threshold the data can speak to."""
    m = predict_loose()
    if m is not None:
        json.dump(m, open(LOOSE_MATRIX, "w"), indent=2)
        return m["calls"], m["loose_threshold"], "MHCflurry re-run at the loose cut (this run)"
    if os.path.exists(LOOSE_MATRIX):
        m = json.load(open(LOOSE_MATRIX))
        return m["calls"], m["loose_threshold"], "cached epitope-allele-loose-matrix.json"
    # ⚠ FALL BACK AND DECLARE THE CEILING. Above the strict matrix's cut an allele's absence means
    # it was never predicted, NOT that it failed to bind; the curve stops rather than imply the one
    # from the other.
    m = json.load(open(STRICT))
    return m["strong_binders"], CONVENTIONAL, ("committed epitope-allele-matrix.json — strict cut "
                                               "only; no MHCflurry and no loose cache available")


def main():
    if not os.path.exists(STRICT):
        print("  epitope-allele-matrix.json absent; run coverage_scan.py first", file=sys.stderr)
        return 1
    panel_size = len(json.load(open(STRICT))["panel"])  # AUT-079: read, never hardcode, the size
    calls, ceiling, provenance = load_calls()

    alleles = sorted({c["allele"] for c in calls if c["percentile"] <= ceiling})
    resolve = hc.build_region_resolver(hc.fetch(hc.ISO_JSON_URL))
    freqs, _racc, source_ok, _un = hc.load_afnd(alleles, resolve)
    if not source_ok:
        print("  AFND mirror unavailable; curve NOT written rather than fabricated", file=sys.stderr)
        return 1

    rows = []
    for t in grid(calls):
        if t > ceiling:
            break
        present = sorted({c["allele"] for c in calls if c["percentile"] <= t})
        # The manuscript's own function, over the manuscript's own pooled frequencies.
        cov, ci, used = hc.coverage_with_ci({a: freqs[a] for a in present})
        rows.append({"threshold": t, "n_presenting_alleles": len(used),
                     "coverage": cov if cov is not None else 0.0,
                     "coverage_95ci": ci, "alleles": used})

    at = lambda t: next((r for r in rows if abs(r["threshold"] - t) < 1e-9), None)  # noqa: E731
    nonzero = [r for r in rows if r["n_presenting_alleles"] > 0]
    # ⭐ THE STEPS ARE THE RESULT. Coverage is a step function of the threshold and every step is
    # one peptide-allele call; listing them says how few numbers the headline figure rests on.
    steps, prev = [], []
    for r in rows:
        if r["alleles"] != prev:
            added = [a for a in r["alleles"] if a not in prev]
            steps.append({"threshold": r["threshold"], "alleles_added": added,
                          "coverage_after": r["coverage"],
                          "peptides": sorted({c["peptide"] for c in calls
                                              if c["allele"] in added
                                              and c["percentile"] <= r["threshold"]})})
            prev = r["alleles"]
    result = {
        "_what": ("Predicted class I coverage of the EWSR1::NR4A3 junction as a continuous function "
                  "of the MHCflurry presentation-percentile acceptance threshold, over the fixed "
                  f"{panel_size}-allele panel of epitope-allele-matrix.json."),
        "_why": ("The manuscript's coverage figures rest on a threshold it does not defend (§7) and "
                 "were stated at three points (§2.3). This is the function between and beyond them."),
        "⛔_what_this_is_not": (
            "Not an argument for a looser cut, and not a better coverage number. A threshold chosen "
            "to raise coverage is the defect this analysis exists to expose. Every figure here is "
            "predicted binding — a screen, not evidence of presentation, immunogenicity or benefit."),
        "_method": ("presenting alleles at threshold t = alleles with >=1 junction peptide at "
                    "presentation percentile <= t; coverage = 1 - prod(1-af)^2 over them via "
                    "hla_coverage.coverage_with_ci on AFND-pooled frequencies — the manuscript's "
                    "own formula and frequencies, imported not reimplemented, so this curve cannot "
                    "disagree with the headline number. CI propagated from per-allele Wilson bounds."),
        "_sources": [hc.AFND_CITATION, hc.ISO_CITATION],
        "⚠_the_manuscript_withdraws_these_intervals": (
            "coverage_95ci is emitted because hla_coverage computes it, and MUST NOT be quoted. "
            "§2.3 withdraws the Wilson intervals: they pool every reference population into one "
            "binomial while the same records show HLA-B*15:01 ranging 0 to 0.40 between those "
            "populations, so the single-urn model is refuted by its own input — and the interval "
            "is an order of magnitude narrower than the threshold sensitivity this curve maps."),
        "_provenance": provenance,
        "_ceiling": {
            "value": ceiling,
            "meaning": ("largest threshold this data can speak to. Above it, an allele's absence "
                        "means it was never predicted, NOT that it failed to bind."),
            "above_the_conventional_cut": ceiling > CONVENTIONAL,
        },
        "conventional_threshold": CONVENTIONAL,
        "at_conventional_threshold": at(CONVENTIONAL),
        "steps": steps,
        "lowest_threshold_with_any_presenting_allele": nonzero[0] if nonzero else None,
        "allele_frequencies": freqs,
        "curve": rows,
    }
    json.dump(result, open(OUT, "w"), indent=2)
    conv = at(CONVENTIONAL)
    top = rows[-1] if rows else None
    print(f"  threshold curve: {len(rows)} points up to {ceiling} ({provenance}); "
          f"at {CONVENTIONAL} -> {conv['coverage'] if conv else 'n/a'} on "
          f"{conv['n_presenting_alleles'] if conv else 0} alleles; "
          f"collapses to zero below {nonzero[0]['threshold'] if nonzero else 'n/a'}; "
          f"at {top['threshold'] if top else 'n/a'} -> {top['coverage'] if top else 'n/a'} on "
          f"{top['n_presenting_alleles'] if top else 0}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
