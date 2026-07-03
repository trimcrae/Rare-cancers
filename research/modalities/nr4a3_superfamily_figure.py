#!/usr/bin/env python3
"""
Figure 5 — Nuclear-receptor superfamily selectivity-liability screen (§2.7, A4/D4).

Each of the 47 reviewed human nuclear receptors is scored for how many of the 10 NR4A3 warhead-pocket residues
it shares (pocket identity, y), against the overall NR4A3-LBD alignment identity that gates how much to trust
that pocket mapping (x). The confidence gate at overall identity 0.30 is decisive: only FIVE receptors clear
it — the two paralogue positive controls (NR4A2, NR4A1), the two flagged oxosteroid near-neighbours
(mineralocorticoid receptor NR3C2 and androgen receptor AR, each overlapping two selectivity *handles*), and
PGR. The many receptors at high apparent pocket identity but low overall identity (e.g. THRB/THRA/RORA) are
correctly down-weighted as distant-homology mis-registration. The honest output is a prioritised shortlist
(AR/MR need an energetic cross-binding check), not a clearance.

Data read live from the committed nr4a-superfamily-selectivity.json (ranking + controls). Pocket identity is
discrete (0.0–0.4 in 0.1 steps), so overlapping low-confidence points are given a small deterministic x/y
jitter for visibility only; the plotted (x, y) before jitter are the committed values. Output:
nr4a3-superfamily.png (+ .pdf).
"""
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
CONF_GATE = 0.30   # overall-identity confidence gate (below = low-confidence mapping)


def main():
    with open(os.path.join(HERE, "nr4a-superfamily-selectivity.json")) as fh:
        d = json.load(fh)
    controls = {c["gene"] for c in d["controls_paralogues"]}
    flagged = {f["gene"] for f in d["flagged_liabilities"]}

    rows = []
    for r in d["ranking"]:
        rows.append((r["gene"], r["overall_identity"], r["pocket_identity"]))

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D

    INK = "#1a1a2e"
    MUTED = "#8a8f98"
    C_CTRL = "#2f6fed"    # paralogue positive controls
    C_FLAG = "#d97706"    # flagged non-paralogue near-neighbours (MR/AR)
    C_OTHER = "#b8bdc7"   # background / below-confidence

    fig, ax = plt.subplots(figsize=(7.2, 4.7), dpi=200)

    # below-confidence shaded region
    ax.axvspan(0, CONF_GATE, color="#f2f3f5", zorder=0)
    ax.axvline(CONF_GATE, color=MUTED, lw=1.1, ls="--", zorder=1)
    ax.text(CONF_GATE - 0.006, 0.005, "low-confidence mapping\n(distant homology)", fontsize=7.2,
            color=MUTED, ha="right", va="bottom")
    ax.text(CONF_GATE + 0.006, 0.005, "confidence-gated →", fontsize=7.4, color=MUTED, ha="left", va="bottom")

    def cls(g):
        if g in controls:
            return C_CTRL
        if g in flagged:
            return C_FLAG
        return C_OTHER

    # deterministic tiny jitter for the crowded background points (visual only)
    def jit(i, span):
        return ((i * 2654435761) % 1000 / 1000.0 - 0.5) * span

    for i, (g, ov, pid) in enumerate(rows):
        c = cls(g)
        highlight = c != C_OTHER
        jx = 0 if highlight else jit(i, 0.012)
        jy = 0 if highlight else jit(i + 7, 0.045)
        ax.scatter([ov + jx], [pid + jy], s=(78 if highlight else 26),
                   color=c, zorder=(5 if highlight else 2),
                   edgecolor=("white" if highlight else "none"), linewidth=1.0,
                   alpha=(1.0 if highlight else 0.75))

    # direct labels for the five confidence-gated receptors
    label_off = {
        "NR4A2": (6, 6), "NR4A1": (6, -12), "NR3C2": (8, 6), "AR": (8, -12), "PGR": (8, 0),
    }
    disp = {"NR3C2": "NR3C2 / MR"}
    for g, ov, pid in rows:
        if g in controls or g in flagged or g == "PGR":
            dx, dy = label_off.get(g, (6, 6))
            name = disp.get(g, g)
            tag = " (control)" if g in controls else (" (flagged)" if g in flagged else "")
            ax.annotate(f"{name}{tag}", (ov, pid), textcoords="offset points", xytext=(dx, dy),
                        fontsize=8.2, color=INK, ha="left")

    ax.set_xlim(0.10, 0.66)
    ax.set_ylim(-0.03, 0.47)
    ax.set_xlabel("overall NR4A3-LBD alignment identity  (mapping-confidence axis)", fontsize=9.5, color=INK)
    ax.set_ylabel("warhead-pocket residue identity  (10 residues)", fontsize=9.5, color=INK)
    ax.set_title("Superfamily selectivity screen: only the paralogues, MR and AR clear the confidence gate\n"
                 "(pocket-sequence resemblance prioritises, it does not certify — §2.7)",
                 fontsize=10.4, color=INK, pad=10)
    ax.grid(True, color="#e7e8ec", lw=0.8, zorder=0)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(MUTED)
    ax.tick_params(colors=MUTED, labelsize=9)

    legend = [
        Line2D([0], [0], marker="o", color="w", markerfacecolor=C_CTRL, markersize=9,
               label="paralogue positive control (NR4A1/2)"),
        Line2D([0], [0], marker="o", color="w", markerfacecolor=C_FLAG, markersize=9,
               label="flagged non-paralogue liability (MR, AR)"),
        Line2D([0], [0], marker="o", color="w", markerfacecolor=C_OTHER, markersize=7,
               label="other human NRs (n = 43)"),
    ]
    ax.legend(handles=legend, loc="lower right", frameon=False, fontsize=8.2)

    footnote = ("Read live from committed nr4a-superfamily-selectivity.json. Necessary-not-sufficient:\n"
                "sequence resemblance to a CRYPTIC pocket prioritises an energetic follow-up (docking/FEP\n"
                "into AR/MR), it is not a selectivity clearance.")
    ax.text(0.0, -0.155, footnote, transform=ax.transAxes, ha="left", va="top", fontsize=6.9, color=MUTED)
    fig.tight_layout()
    out = os.path.join(HERE, "nr4a3-superfamily.png")
    fig.savefig(out, bbox_inches="tight")
    fig.savefig(out.replace(".png", ".pdf"), bbox_inches="tight")
    print("wrote", out)


if __name__ == "__main__":
    main()
