#!/usr/bin/env python3
"""
Prioritisation figure for the EMC surface-target preprint.

Renders the paper's central, honest result in one plot: candidate surface antigens placed by
cross-cancer SELECTIVITY (x, from emc-surfaceome-scan.json) against NORMAL-TISSUE WINDOW tier
(y, from emc-surface-normal-window.json). A usable target would sit top-right (selective AND
tumour-restricted); the figure shows that quadrant is unpopulated for the antigens the selectivity
filter actually evaluated — B7-H3 is not selective, the selective ones carry window liabilities.

Antigens with NO selectivity value in the scan output (not evaluated) are NOT drawn on the
selectivity axis. They are drawn in a separate, hatched "NOT EVALUATED" side band that has no
selectivity scale at all, so that a missing value can never be read as a measured selectivity of
zero. In the current artifacts those antigens are B4GALNT1 (GD2 synthase) and SSTR2.

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
    # An antigen with no enrichment_vs_rest was NOT evaluated by the selectivity filter. It has no
    # selectivity value, so it is never placed on the selectivity axis (a marker at x=0 would assert
    # a measured selectivity of zero). Such antigens go to the separate NOT EVALUATED band instead.
    wants = {g: win["antigens"].get(g, {}) for g in SHOW}

    pts = []      # antigens WITH a measured selectivity value: (gene, x, tier, significant)
    not_eval = []  # antigens WITHOUT one: (gene, tier)
    for g in SHOW:
        w = wants[g]
        if not w or w.get("_status"):
            continue
        tier = WINDOW_TIER.get(w.get("window"), 1)
        s = act.get(g, {})
        enr = s.get("enrichment_vs_rest")
        sig = s.get("selectivity_significant")
        if enr is None:
            not_eval.append((g, tier))
            continue
        pts.append((g, enr, tier, bool(sig)))

    fig, (ax, axn) = plt.subplots(1, 2, figsize=(11.5, 6.4), sharey=True,
                                  gridspec_kw={"width_ratios": [5, 1.5], "wspace": 0.05})
    # shade the "target-worthy" region: significant selectivity (x>0) AND restricted (tier 3)
    ax.add_patch(Rectangle((0.0, 2.5), 4.0, 1.0, color="#2ca02c", alpha=0.08))
    ax.text(2.0, 3.35, "target-worthy\n(selective & restricted)\nno EVALUATED antigen here",
            ha="center", va="top", fontsize=9, color="#2ca02c")

    for g, x, tier, sig in pts:
        jitter = 0.12 * (hash(g) % 5 - 2)
        color = "#d62728" if tier <= 0 else ("#ff7f0e" if tier == 1 else
                                             ("#1f77b4" if tier == 2 else "#2ca02c"))
        marker = "o" if sig else "x"
        ax.scatter(x, tier + jitter, s=90, c=color, marker=marker,
                   edgecolors="k", linewidths=0.5, zorder=3)
        ax.annotate(LABEL.get(g, g), (x, tier + jitter), fontsize=8, xytext=(5, 3),
                    textcoords="offset points")

    ax.axvline(0, color="gray", lw=0.8, ls=":")
    # Pin the selectivity axis to the limits it had before the not-evaluated antigens were moved
    # off it, so that every evaluated antigen keeps exactly the position it had.
    ax.set_xlim(-2.5205, 4.3105)
    ax.set_yticks([0, 1, 2, 3])
    ax.set_yticklabels([TIER_LABEL[i] for i in [0, 1, 2, 3]], fontsize=8)
    ax.set_ylim(-0.6, 3.8)
    ax.set_xlabel("Cross-cancer selectivity  (enrichment vs non-sarcoma lineages, log2TPM)\n"
                  "● = BH-significant   ✕ = not significant", fontsize=9)
    fig.suptitle("EMC surface-antigen prioritisation (surrogate): selectivity vs normal-tissue window\n"
                 "the selective-and-restricted quadrant is unpopulated for the antigens the "
                 "selectivity filter evaluated;\nantigens with no selectivity value are not on the "
                 "axis at all — see the NOT EVALUATED band at right",
                 fontsize=10)
    ax.grid(axis="x", alpha=0.25)

    # --- separate band: antigens with NO selectivity value (not evaluated) -------------------
    # This band carries no selectivity scale. Nothing in it is at, near, or comparable to x = 0.
    axn.set_facecolor("#f0f0f0")
    for sp in ("top", "right", "bottom"):
        axn.spines[sp].set_visible(False)
    axn.spines["left"].set_linestyle((0, (4, 3)))
    axn.spines["left"].set_color("gray")
    axn.set_xlim(0, 1)
    axn.set_xticks([])
    axn.add_patch(Rectangle((0, -0.6), 1.0, 4.4, facecolor="none", edgecolor="gray",
                            hatch="///", alpha=0.35, lw=0))
    axn.tick_params(axis="y", length=0)
    axn.text(0.5, 3.72, "NOT EVALUATED\nno selectivity value\n(not a measured zero)", ha="center",
             va="top", fontsize=8.5, color="dimgray", fontweight="bold")
    for i, (g, tier) in enumerate(not_eval):
        y = tier + 0.12 * (i % 3 - 1)
        axn.scatter(0.5, y, s=90, facecolors="none", edgecolors="dimgray",
                    marker="s", linewidths=1.2, zorder=3)
        axn.annotate(LABEL.get(g, g), (0.5, y), fontsize=8, color="dimgray", ha="center",
                     xytext=(0, -16), textcoords="offset points")
    if not not_eval:
        axn.text(0.5, 1.6, "none", ha="center", fontsize=8, color="dimgray")

    fig.tight_layout(rect=(0, 0, 1, 0.88))
    fig.savefig(OUT, dpi=140)
    print("wrote", OUT, file=sys.stderr)


if __name__ == "__main__":
    main()
