#!/usr/bin/env python3
"""
Coverage-vs-number-of-alleles curve for a public EWSR1::NR4A3 fusion-neoantigen vaccine.

Answers "how many HLA alleles must a public vaccine present the junction on to cover X% of
patients?" — globally and per region. This is the design curve behind the headline coverage
number: the earlier analysis used only the few alleles that happened to win best-binder per
peptide; here we scan a broad common-allele panel and build the greedy coverage curve.

Phases (each guarded so the script degrades gracefully):
  A. PREDICT (needs MHCflurry; CI only): run MHCflurry-2.0 over the junction-spanning
     peptides (read from fusion-breakpoint-neoantigens.json) for a broad HLA-A/-B panel;
     record every (peptide, allele) strong binder. Cache to epitope-allele-matrix.json.
     If MHCflurry is absent, reuse the cached matrix.
  B. CURVE (pure Python; runs anywhere): the set a vaccine "targets" is the alleles that
     present >=1 strong junction binder. Coverage of a set = 1 - prod(1-af)^2 (>=1 presenting
     allele; IEDB formula). Under this model the greedy marginal gain ranks identically to
     allele frequency, so the optimal curve is the presenting alleles added in descending
     AFND frequency. Built globally and per UN M49 sub-region (frequencies + region map
     reuse hla_coverage.py, i.e. the AFND mirror + ISO 3166).
  C. CHART (needs matplotlib; CI only): render coverage-curve.png (global + regional).

Outputs: epitope-allele-matrix.json, coverage-curve.json, coverage-curve.png
"""

import json
import os
import sys

import hla_coverage as hc  # reuse AFND fetch/pooling + region resolver (same dir)

HERE = os.path.dirname(__file__)
BREAKPOINTS = os.path.join(HERE, "fusion-breakpoint-neoantigens.json")
MATRIX = os.path.join(HERE, "epitope-allele-matrix.json")
CURVE = os.path.join(HERE, "coverage-curve.json")
CHART = os.path.join(HERE, "coverage-curve.png")

# Broad common-allele panel (HLA-A/-B), spanning global diversity (≈ IEDB reference breadth).
PANEL = [
    "HLA-A*01:01", "HLA-A*02:01", "HLA-A*02:03", "HLA-A*02:06", "HLA-A*03:01",
    "HLA-A*11:01", "HLA-A*23:01", "HLA-A*24:02", "HLA-A*26:01", "HLA-A*30:01",
    "HLA-A*30:02", "HLA-A*31:01", "HLA-A*32:01", "HLA-A*33:01", "HLA-A*68:01",
    "HLA-A*68:02",
    "HLA-B*07:02", "HLA-B*08:01", "HLA-B*13:02", "HLA-B*14:02", "HLA-B*15:01",
    "HLA-B*18:01", "HLA-B*27:05", "HLA-B*35:01", "HLA-B*38:01", "HLA-B*40:01",
    "HLA-B*40:02", "HLA-B*44:02", "HLA-B*44:03", "HLA-B*46:01", "HLA-B*51:01",
    "HLA-B*53:01", "HLA-B*57:01", "HLA-B*58:01",
]
LENGTHS = [8, 9, 10, 11]
RANK_STRONG = 0.5


def predict_matrix():
    """Phase A: MHCflurry strong binders over the panel. Returns matrix dict or None."""
    try:
        from mhcflurry import Class1PresentationPredictor
    except ImportError:
        return None
    bp = json.load(open(BREAKPOINTS))
    peps = sorted({p for jn in bp.get("junctions", []) for p in jn.get("novel_peptides", [])
                   if len(p) in LENGTHS})
    if not peps:
        return None
    predictor = Class1PresentationPredictor.load()
    df = predictor.predict(peptides=peps, alleles={a: [a] for a in PANEL}, verbose=0)
    rank_col = ("presentation_percentile" if "presentation_percentile" in df.columns
                else "affinity_percentile")
    rows = []
    for _, r in df.iterrows():
        rank = float(r[rank_col])
        if rank <= RANK_STRONG:
            rows.append({"peptide": r["peptide"], "allele": str(r["best_allele"]),
                         "percentile": round(rank, 4)})
    matrix = {"_note": "Strong MHC-I binders (presentation_percentile<=0.5) of EWSR1::NR4A3 "
                       "junction peptides across a broad HLA-A/-B panel (MHCflurry-2.0).",
              "panel": PANEL, "rank_column": rank_col, "n_peptides": len(peps),
              "strong_binders": rows,
              "presenting_alleles": sorted({x["allele"] for x in rows})}
    json.dump(matrix, open(MATRIX, "w"), indent=2)
    return matrix


def greedy_curve(presenting, af_of):
    """Presenting alleles sorted by af desc; cumulative coverage 1-prod(1-af)^2."""
    alleles = [a for a in presenting if af_of(a) is not None]
    alleles.sort(key=lambda a: af_of(a), reverse=True)
    curve, prod = [], 1.0
    for n, a in enumerate(alleles, 1):
        prod *= (1 - af_of(a)) ** 2
        curve.append({"n_alleles": n, "allele_added": a, "af": round(af_of(a), 4),
                      "cumulative_coverage": round(1 - prod, 4)})
    return curve


def alleles_to_reach(curve, targets=(0.5, 0.8, 0.9, 0.95)):
    out = {}
    for t in targets:
        hit = next((c["n_alleles"] for c in curve if c["cumulative_coverage"] >= t), None)
        out[f"{int(t*100)}pct"] = hit
    return out


def main():
    matrix = predict_matrix()
    if matrix is None:
        if not os.path.exists(MATRIX):
            print("  MHCflurry absent and no cached matrix; cannot build curve", file=sys.stderr)
            json.dump({"_status": "no matrix"}, open(CURVE, "w"), indent=2)
            return
        matrix = json.load(open(MATRIX))
        print("  reusing cached epitope-allele-matrix.json", file=sys.stderr)

    presenting = matrix["presenting_alleles"]
    print(f"  {len(presenting)} of {len(matrix.get('panel', PANEL))} panel alleles present a "
          f"strong junction binder", file=sys.stderr)

    # AFND frequencies + per-region accumulators for the presenting alleles (reuse hla_coverage)
    resolve = hc.build_region_resolver(hc.fetch(hc.ISO_JSON_URL))
    ginfo, racc, source_ok, _ = hc.load_afnd(presenting, resolve)
    if not source_ok:
        json.dump({"_status": "AFND unavailable"}, open(CURVE, "w"), indent=2)
        return

    def gaf(a):
        info = ginfo.get(a) or {}
        return info.get("allele_frequency")

    global_curve = greedy_curve(presenting, gaf)

    regions = {}
    for region, alleles in racc.items():
        def raf(a, _al=alleles):
            acc = _al.get(a.replace("HLA-", ""))
            return (acc["copies"] / acc["twoN"]) if (acc and acc["twoN"]) else None
        rc = greedy_curve(presenting, raf)
        if rc:
            regions[region] = {"curve": rc, "max_coverage": rc[-1]["cumulative_coverage"],
                               "alleles_to_reach": alleles_to_reach(rc)}
    regions = dict(sorted(regions.items(),
                          key=lambda kv: -kv[1]["max_coverage"]))

    out = {
        "_note": "Coverage vs number of HLA-A/-B alleles presented, for a public EWSR1::NR4A3 "
                 "junction vaccine. Presenting alleles (>=1 strong MHCflurry binder) added in "
                 "descending AFND frequency (= greedy-optimal under 1-prod(1-af)^2). Class I "
                 "only; CD4/class-II handled separately. Sources as in hla-coverage.json.",
        "panel_size": len(matrix.get("panel", PANEL)),
        "n_presenting_alleles": len(presenting),
        "presenting_alleles": presenting,
        "global_curve": global_curve,
        "global_max_coverage": global_curve[-1]["cumulative_coverage"] if global_curve else None,
        "global_alleles_to_reach": alleles_to_reach(global_curve),
        "regions": regions,
    }
    json.dump(out, open(CURVE, "w"), indent=2)
    print("wrote", CURVE, file=sys.stderr)
    print(json.dumps({"global_max": out["global_max_coverage"],
                      "global_alleles_to_reach": out["global_alleles_to_reach"],
                      "n_presenting": len(presenting)}, indent=2))
    render_chart(out)


def render_chart(out):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("  matplotlib absent; skipping chart", file=sys.stderr)
        return
    fig, ax = plt.subplots(figsize=(8, 5))
    g = out["global_curve"]
    ax.plot([c["n_alleles"] for c in g], [c["cumulative_coverage"] * 100 for c in g],
            color="black", lw=2.5, marker="o", ms=4, label="Global", zorder=5)
    # a few representative regions (extremes + large samples)
    show = ["Northern Europe", "Eastern Asia", "Sub-Saharan Africa",
            "Latin America and the Caribbean"]
    for region in show:
        rc = out["regions"].get(region)
        if not rc:
            continue
        c = rc["curve"]
        ax.plot([x["n_alleles"] for x in c], [x["cumulative_coverage"] * 100 for x in c],
                lw=1.5, marker=".", ms=3, alpha=0.85, label=region)
    ax.axhline(90, ls="--", c="gray", lw=1)
    ax.set_xlabel("Number of HLA-A/-B alleles presented by the vaccine")
    ax.set_ylabel("Population coverage (% with ≥1 presenting allele)")
    ax.set_title("EWSR1::NR4A3 public fusion-neoantigen: coverage vs. alleles targeted")
    ax.set_ylim(0, 100)
    ax.legend(fontsize=8, loc="lower right")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(CHART, dpi=130)
    print("wrote", CHART, file=sys.stderr)


if __name__ == "__main__":
    main()
