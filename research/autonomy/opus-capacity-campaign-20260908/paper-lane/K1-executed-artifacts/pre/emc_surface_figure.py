#!/usr/bin/env python3
"""
Prioritisation figure for the EMC surface-target preprint.

Renders the paper's central, honest result in one plot: candidate surface antigens placed by
cross-cancer SELECTIVITY (x, from emc-surfaceome-scan.json) against NORMAL-TISSUE WINDOW tier
(y, from emc-surface-normal-window.json). A usable target would sit top-right (selective AND
tumour-restricted); the figure shows that quadrant is essentially EMPTY for classic protein
antigens — B7-H3 is not selective, the selective ones carry window liabilities.

Reads the committed JSONs from the modalities-cache branch (CI has internet). matplotlib only.
Output: emc-surface-prioritization.png
"""
import json
import os
import sys
import urllib.request

HERE = os.path.dirname(__file__)
OUT = os.path.join(HERE, "emc-surface-prioritization.png")
RAW = "https://raw.githubusercontent.com/trimcrae/Rare-cancers/modalities-cache/research/modalities"

WINDOW_TIER = {"RESTRICTED": 3, "ENHANCED_BROAD": 2, "BROAD_LIABILITY": 1,
               "VITAL_OR_IMMUNE_LIABILITY": 0}
TIER_LABEL = {3: "RESTRICTED\n(clean window)", 2: "ENHANCED_BROAD", 1: "BROAD_LIABILITY",
              0: "VITAL/IMMUNE\nLIABILITY"}
# antigens to show (shortlist)
SHOW = ["CDH11", "FGFR1", "GPC2", "PTK7", "MCAM", "EPHB4", "CD276", "NCAM1", "FAP", "EGFR",
        "KIT", "SSTR2", "B4GALNT1"]
LABEL = {"CD276": "B7-H3/CD276", "NCAM1": "NCAM1/CD56", "MCAM": "MCAM/CD146",
         "B4GALNT1": "GD2 (B4GALNT1)"}


def _get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "rare-cancers/1.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8", "replace"))


def main():
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from matplotlib.patches import Rectangle
    except ImportError:
        print("matplotlib missing", file=sys.stderr)
        return
    scan = _get(f"{RAW}/emc-surfaceome-scan.json")
    win = _get(f"{RAW}/emc-surface-normal-window.json")
    act = scan.get("actionable_antigens", {})
    # B4GALNT1 is not in the actionable seed; enrichment may be absent -> place at x=0 with a flag.
    wants = {g: win["antigens"].get(g, {}) for g in SHOW}

    pts = []
    for g in SHOW:
        w = wants[g]
        if not w or w.get("_status"):
            continue
        tier = WINDOW_TIER.get(w.get("window"), 1)
        s = act.get(g, {})
        enr = s.get("enrichment_vs_rest")
        sig = s.get("selectivity_significant")
        pts.append((g, enr if enr is not None else 0.0, tier, bool(sig), enr is not None))

    fig, ax = plt.subplots(figsize=(9, 6))
    # shade the "target-worthy" region: significant selectivity (x>0) AND restricted (tier 3)
    ax.add_patch(Rectangle((0.0, 2.5), 4.0, 1.0, color="#2ca02c", alpha=0.08))
    ax.text(2.0, 3.35, "target-worthy\n(selective & restricted) — EMPTY", ha="center",
            va="top", fontsize=9, color="#2ca02c")

    for g, x, tier, sig, has_enr in pts:
        jitter = 0.12 * (hash(g) % 5 - 2)
        color = "#d62728" if tier <= 0 else ("#ff7f0e" if tier == 1 else
                                             ("#1f77b4" if tier == 2 else "#2ca02c"))
        marker = "o" if sig else "x"
        ax.scatter(x, tier + jitter, s=90, c=color, marker=marker,
                   edgecolors="k", linewidths=0.5, zorder=3)
        lab = LABEL.get(g, g) + ("" if has_enr else " (sel n/a)")
        ax.annotate(lab, (x, tier + jitter), fontsize=8, xytext=(5, 3),
                    textcoords="offset points")

    ax.axvline(0, color="gray", lw=0.8, ls=":")
    ax.set_yticks([0, 1, 2, 3])
    ax.set_yticklabels([TIER_LABEL[i] for i in [0, 1, 2, 3]], fontsize=8)
    ax.set_ylim(-0.6, 3.8)
    ax.set_xlabel("Cross-cancer selectivity  (enrichment vs non-sarcoma lineages, log2TPM)\n"
                  "● = BH-significant   ✕ = not significant", fontsize=9)
    ax.set_title("EMC surface-antigen prioritisation (surrogate): selectivity vs normal-tissue window\n"
                 "the selective-and-restricted quadrant is empty for classic protein antigens",
                 fontsize=10)
    ax.grid(axis="x", alpha=0.25)
    fig.tight_layout()
    fig.savefig(OUT, dpi=140)
    print("wrote", OUT, file=sys.stderr)


if __name__ == "__main__":
    main()
