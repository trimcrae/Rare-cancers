#!/usr/bin/env python3
"""
Figure 5 (contrast panel) — denovo_401's decoy-null result is receptor-frame-dependent (§2.6).

The load-bearing honesty panel of the de-novo result: the lead `denovo_401` is scored against a
*same-tier multi-snapshot decoy null* (38 non-NR4A marketed drugs pushed through the identical
dock -> multi-snapshot MM-GBSA funnel) in TWO receptor frames. In the unbiased "release" frame the
molecule was designed against, denovo_401's margin (+12.83 +/- 2.98) sits above the entire decoy
null (95th +6.69, max +7.10) -> it clears. In the biased metad-opened frame it was NOT designed
against, the decoy null balloons (95th +17.70, max +24.74; random drugs like diphenhydramine +24.74,
lidocaine +22.08 score "selective") and denovo_401 (+7.44 +/- 4.18) does NOT clear (~84th percentile).

The panel makes the frame-dependence unmissable: the claim is a de-noised *foothold* in the design
frame, not a frame-invariant specificity result. Values are transcribed from the manuscript's §2.6
contrast table (each a committed SageMaker MM-GBSA run). No values are estimated here.
Output: nr4a3-frame-decoynull.png (+ .pdf).
"""
import os

# --- committed data: manuscript §2.6 receptor-frame contrast table ---
# frame label, decoy-null 95th pct, decoy-null max, denovo_401 margin, denovo_401 SD, clears?
FRAMES = [
    ("unbiased release\n(design frame)", 6.69, 7.10, 12.83, 2.98, True),
    ("biased metad-opened\n(not the design frame)", 17.70, 24.74, 7.44, 4.18, False),
]

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    INK = "#1a1a2e"
    MUTED = "#8a8f98"
    NULL_FILL = "#eceef1"     # decoy-null band fill
    NULL_EDGE = "#8a8f98"     # 95th percentile line
    CLEARS = "#2f6fed"        # denovo_401 clears the null (blue)
    FAILS = "#d97706"         # denovo_401 fails the null (amber)

    out = os.path.join(HERE, "nr4a3-frame-decoynull.png")
    ys = [1.0, 0.0]  # release on top

    fig, ax = plt.subplots(figsize=(8.2, 4.6), dpi=200)

    ax.axvline(0, color=MUTED, lw=1.0, zorder=1)

    for (label, p95, dmax, margin, sd, clears), y in zip(FRAMES, ys):
        colour = CLEARS if clears else FAILS
        # decoy-null band: 0 -> 95th percentile shaded, with max-decoy whisker to dmax
        ax.barh(y, p95, height=0.30, left=0.0, color=NULL_FILL, edgecolor=NULL_EDGE,
                linewidth=1.1, zorder=2)
        ax.plot([p95, dmax], [y, y], color=NULL_EDGE, lw=1.1, ls=":", zorder=2)
        ax.plot([dmax, dmax], [y - 0.08, y + 0.08], color=NULL_EDGE, lw=1.1, zorder=2)
        ax.text(p95 / 2.0, y + 0.22, "decoy null (n=38): 0→95th %ile", fontsize=7.2,
                color=MUTED, ha="center", va="bottom")
        ax.text(dmax, y + 0.15, f"max decoy +{dmax:.2f}", fontsize=6.8, color=MUTED,
                ha="center", va="bottom")
        # denovo_401 point +/- SD
        ax.errorbar([margin], [y], xerr=[sd], fmt="D", color=colour, ms=10, capsize=5,
                    elinewidth=1.9, zorder=6, markeredgecolor="white", markeredgewidth=1.2)
        verdict = "clears the entire null" if clears else "does NOT clear (~84th %ile)"
        ax.text(margin, y - 0.19, f"denovo_401  +{margin:.2f} ± {sd:.2f}",
                fontsize=8.6, color=colour, ha="center", va="top", fontweight="bold")
        ax.text(margin, y - 0.32, verdict, fontsize=7.6, color=colour, ha="center",
                va="top", style="italic")
        # frame label at left
        ax.text(-1.2, y, label, fontsize=9.0, color=INK, ha="right", va="center")

    ax.set_yticks([])
    ax.set_xlim(-12, 28)
    ax.set_ylim(-0.62, 1.62)
    ax.set_xlabel("NR4A3-selectivity margin  ΔΔG  (kcal/mol; NR4A3 favoured →)",
                  fontsize=10, color=INK)
    ax.set_title("denovo_401's decoy-null result is receptor-frame-dependent (§2.6)",
                 fontsize=11.5, color=INK, pad=12)
    ax.grid(True, axis="x", color="#e7e8ec", lw=0.8, zorder=0)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(MUTED)
    ax.tick_params(colors=MUTED, labelsize=9)

    ax.text(0.0, -0.16, "Grey band = decoy null (38 non-NR4A marketed drugs, same dock→multi-snapshot MM-GBSA "
            "funnel), 0→95th %ile; dotted whisker → max decoy. Diamond = denovo_401 ± SD.\nValues from "
            "manuscript §2.6 (committed MM-GBSA runs). The null controls the scoring step, not the generative "
            "step; single-trajectory GB-implicit, not FEP — read direction/robustness, not affinity.",
            transform=ax.transAxes, ha="left", va="top", fontsize=6.9, color=MUTED)
    fig.tight_layout()
    fig.savefig(out, bbox_inches="tight")
    fig.savefig(out.replace(".png", ".pdf"), bbox_inches="tight")
    print("wrote", out)


if __name__ == "__main__":
    main()
