#!/usr/bin/env python3
"""
Figure 3 — Per-receptor multi-snapshot MM-GBSA binding ΔG for the lead `denovo_401` (§2.6).

Grouped bars of the mean binding ΔG against NR4A3 vs the paralogues NR4A1 and NR4A2, in the two receptor
frames the paper reports: the unbiased *release* (design) frame and the biased *metad-opened* frame. NR4A3 is
the most-favoured receptor in BOTH frames (the selectivity direction is robust), but the NR4A3-vs-NR4A1 margin
is larger in the release frame (+14.75) than in the metad-opened frame (+7.44) — i.e. the direction is
frame-robust while the magnitude is frame-dependent (§2.6).

Data are transcribed from the manuscript §2.6: the release-frame values are the independent-reproduction run
28518978321 (all three ΔG reported: NR4A3 −37.50 / NR4A1 −22.75 / NR4A2 −20.43; margin +14.75 ± 4.82), the
metad-opened values are runs 28473682532/28480041030 (NR4A3 −32.37 / NR4A1 −24.93 / NR4A2 −22.80; margin
+7.44 ± 4.18). No values are estimated. Output: nr4a3-selectivity-dG.png (+ .pdf).
"""
import os

# --- committed data: manuscript §2.6 (per-receptor multi-snapshot MM-GBSA ΔG, kcal/mol) ---
FRAMES = [
    ("release / design frame",
     {"NR4A3": -37.50, "NR4A1": -22.75, "NR4A2": -20.43}, 14.75, 4.82),
    ("metad-opened frame",
     {"NR4A3": -32.37, "NR4A1": -24.93, "NR4A2": -22.80}, 7.44, 4.18),
]
RECEPTORS = ["NR4A3", "NR4A1", "NR4A2"]

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    INK = "#1a1a2e"
    MUTED = "#8a8f98"
    COLORS = {"NR4A3": "#2f6fed", "NR4A1": "#d97706", "NR4A2": "#9333ea"}

    out = os.path.join(HERE, "nr4a3-selectivity-dG.png")
    fig, ax = plt.subplots(figsize=(7.0, 4.6), dpi=200)

    group_w = 0.62
    bw = group_w / len(RECEPTORS)
    centers = [0, 1.15]

    for gi, (glabel, dG, margin, sd) in enumerate(FRAMES):
        x0 = centers[gi] - group_w / 2 + bw / 2
        for ri, rec in enumerate(RECEPTORS):
            x = x0 + ri * bw
            val = dG[rec]
            ax.bar(x, val, width=bw * 0.9, color=COLORS[rec], zorder=3,
                   label=(rec if gi == 0 else None))
            ax.text(x, val - 0.7, f"{val:.1f}", ha="center", va="top", fontsize=8.2, color=INK)
        # selectivity margin annotation (NR4A1 − NR4A3), bracket above NR4A3 & NR4A1 bars
        xn3 = x0
        xn1 = x0 + bw
        top = 2.0
        ax.annotate("", xy=(xn3, top), xytext=(xn1, top),
                    arrowprops=dict(arrowstyle="<->", color=MUTED, lw=1.1))
        ax.text((xn3 + xn1) / 2, top + 1.0, f"ΔΔG(NR4A3−NR4A1)\n= +{margin:.1f} ± {sd:.1f}",
                ha="center", va="bottom", fontsize=8.0, color=INK)

    ax.axhline(0, color=MUTED, lw=1.0)
    ax.set_xticks(centers)
    ax.set_xticklabels([f[0] for f in FRAMES], fontsize=9.4, color=INK)
    ax.set_ylabel("multi-snapshot MM-GBSA binding ΔG (kcal/mol)\n← tighter / more favoured", fontsize=9.5, color=INK)
    ax.set_xlim(-0.55, 1.75)
    ax.set_ylim(-44, 12)
    ax.set_title("`denovo_401` binds NR4A3 most tightly in both receptor frames\n"
                 "(selectivity direction robust; margin frame-dependent — §2.6)",
                 fontsize=10.6, color=INK, pad=10)
    ax.grid(True, axis="y", color="#e7e8ec", lw=0.8, zorder=0)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(MUTED)
    ax.tick_params(colors=MUTED, labelsize=9)
    ax.legend(loc="lower right", frameon=False, fontsize=9, ncol=1)

    footnote = ("Values from manuscript §2.6 (committed MM-GBSA runs: release 28518978321,\n"
                "metad 28473682532/28480041030). Single-trajectory GB-implicit MD, not FEP;\n"
                "magnitudes inflated (no entropy/ensemble) — read ΔΔG direction, not Kd.")
    ax.text(0.0, -0.135, footnote, transform=ax.transAxes, ha="left", va="top",
            fontsize=7.0, color=MUTED)
    fig.tight_layout()
    fig.savefig(out, bbox_inches="tight")
    fig.savefig(out.replace(".png", ".pdf"), bbox_inches="tight")
    print("wrote", out)


if __name__ == "__main__":
    main()
