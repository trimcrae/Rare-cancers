#!/usr/bin/env python3
"""
Figure 4 — Safety genetics of the NR4A family: proliferative dispensability vs germline constraint (§5, H1).

The tolerability case for an NR4A3-selective degrader must not rest on the glib "dispensable ⇒ safe"
inference. This panel plots each paralogue on two orthogonal axes: DepMap CRISPR gene effect (how essential
the gene is for *proliferation*; > −0.5 = non-dependent) vs gnomAD LoF constraint LOEUF (how depleted of
loss-of-function variants the gene is in *human germline*; < 0.35 = LoF-intolerant/constrained). All three
NR4As are non-essential for proliferation (far right of the dependency line, 0/1178 lines dependent for
NR4A3), yet NR4A3 and NR4A2 are LoF-*constrained* in humans (below the LOEUF line) — the honest point that
proliferative dispensability does not equal whole-organism safety, and that NR4A2 (most constrained + CNS-
enriched) is a sparing requirement.

Data: gnomAD LOEUF/pLI read live from the committed nr4a-safety-genetics.json (gnomad_lof_constraint). DepMap
gene effect: NR4A3 +0.023 from the committed depmap-sarcoma-dependency.json (rest_mean); NR4A1 −0.115 /
NR4A2 −0.05 from the manuscript §5 (2026-07-02 direct DepMap query, n=1178). No values estimated.
Output: nr4a3-safety-genetics.png (+ .pdf).
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))

# DepMap CRISPR gene effect (mean across lines): NR4A3 from committed depmap-sarcoma-dependency.json
# rest_mean; NR4A1/NR4A2 from manuscript §5 (2026-07-02 DepMap query, n=1178). More negative = more essential.
DEPMAP_GENE_EFFECT = {"NR4A1": -0.115, "NR4A2": -0.05, "NR4A3": 0.023}
DEPENDENCY_THRESHOLD = -0.5   # DepMap: gene effect < -0.5 => "dependent"
LOEUF_THRESHOLD = 0.35        # gnomAD: LOEUF < 0.35 => LoF-intolerant / constrained


def main():
    with open(os.path.join(HERE, "nr4a-safety-genetics.json")) as fh:
        sg = json.load(fh)
    genes = sg["gnomad_lof_constraint"]["genes"]

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    INK = "#1a1a2e"
    MUTED = "#8a8f98"
    PT = "#2f6fed"
    WARN = "#b45309"   # dark amber ink for the "constrained" caution band label

    fig, ax = plt.subplots(figsize=(6.8, 4.6), dpi=200)

    # constrained (LoF-intolerant) band = below LOEUF threshold
    ax.axhspan(0, LOEUF_THRESHOLD, color="#faf1e6", zorder=0)
    ax.axhline(LOEUF_THRESHOLD, color=MUTED, lw=1.1, ls="--", zorder=1)
    ax.axvline(DEPENDENCY_THRESHOLD, color=MUTED, lw=1.1, ls="--", zorder=1)

    labelpos = {"NR4A1": (8, 8), "NR4A2": (10, -4), "NR4A3": (12, 10)}
    for g in ("NR4A1", "NR4A2", "NR4A3"):
        x = DEPMAP_GENE_EFFECT[g]
        y = genes[g]["loeuf"]
        ax.scatter([x], [y], s=90, color=PT, zorder=4, edgecolor="white", linewidth=1.3)
        intol = genes[g]["lof_intolerant"]
        tag = "LoF-constrained" if intol else "LoF-tolerant"
        dx, dy = labelpos[g]
        ax.annotate(f"{g}\n(LOEUF {y:.2f}, {tag})", (x, y), textcoords="offset points",
                    xytext=(dx, dy), fontsize=8.4, color=INK,
                    ha=("right" if dx < 0 else "left"))

    ax.text(0.4, LOEUF_THRESHOLD - 0.03, "LoF-constrained (LOEUF < 0.35): loss selected against in humans",
            transform=ax.get_yaxis_transform() if False else ax.transData,
            fontsize=7.4, color=WARN, ha="center", va="top")
    ax.text(DEPENDENCY_THRESHOLD - 0.02, 0.90, "essential\nfor\nproliferation", fontsize=7.2, color=MUTED,
            ha="right", va="center")
    ax.text(0.30, 0.90, "non-essential for proliferation →", fontsize=7.6, color=MUTED,
            ha="center", va="center")

    ax.set_xlim(-0.75, 0.42)
    ax.set_ylim(0, 0.98)
    ax.set_xlabel("DepMap CRISPR gene effect  (← more essential for proliferation)",
                  fontsize=9.5, color=INK)
    ax.set_ylabel("gnomAD LOEUF  (lower → more LoF-constrained)", fontsize=9.5, color=INK)
    ax.set_title("Non-essential in dividing cells, yet germline-constrained:\n"
                 "\"dispensable ⇒ safe\" is invalid for NR4A3/NR4A2 (§5)", fontsize=10.6, color=INK, pad=10)
    ax.grid(True, color="#e7e8ec", lw=0.8, zorder=0)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(MUTED)
    ax.tick_params(colors=MUTED, labelsize=9)

    footnote = ("LOEUF/pLI: committed nr4a-safety-genetics.json (gnomAD). DepMap: NR4A3 from\n"
                "depmap-sarcoma-dependency.json, NR4A1/2 from §5. Constraint ≠ adult drug-\n"
                "tolerability — a supporting datum, not proof.")
    ax.text(0.0, -0.155, footnote, transform=ax.transAxes, ha="left", va="top",
            fontsize=6.9, color=MUTED)
    fig.tight_layout()
    out = os.path.join(HERE, "nr4a3-safety-genetics.png")
    fig.savefig(out, bbox_inches="tight")
    fig.savefig(out.replace(".png", ".pdf"), bbox_inches="tight")
    print("wrote", out)


if __name__ == "__main__":
    main()
