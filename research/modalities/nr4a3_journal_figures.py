#!/usr/bin/env python3
"""
Journal-grade composite figures for the NR4A3-degrader manuscript (nr4a3-degrader-paper.md).

Renders the six MAIN figures as multi-panel composites in one consistent house style, from committed data
in research/modalities/. Output: nr4a3-fig1.png ... nr4a3-fig6.png (+ .pdf), 300 dpi.

  Fig 1  Calibrated druggability (bar) + independent PocketMiner cross-check (per-residue).           §2.1
  Fig 2  Metadynamics F(Rg) landscape + unbiased release-run druggability.                            §2.2
  Fig 3  Selectivity handles: pocket-facing fraction + paralogue-divergence asymmetry.                §2.3
  Fig 4  Family-wide, state-matched selectivity fingerprint (heatmap of committed candidates).        §2.4
  Fig 5  De-novo funnel: multi-snapshot de-noising + frame-dependent decoy null + lead structure.     §2.5-2.6
  Fig 6  The programmable NR4A axis: census flip (selective vs pan) + the designed pan lead.           §3

Palette validated colorblind-safe (light/print) via the dataviz skill validator:
  NR4A3 #0072B2, NR4A1 #D55E00, NR4A2 #CC79A7 (worst-adjacent CVD ΔE ~70).
Every panel states its evidentiary weight in the caption of the manuscript, not on the axes.
"""
import json
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))

# ---- house style -------------------------------------------------------------
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["DejaVu Sans", "Arial", "Helvetica"],
    "font.size": 9.0,
    "axes.titlesize": 10.5,
    "axes.labelsize": 9.5,
    "xtick.labelsize": 8.5,
    "ytick.labelsize": 8.5,
    "axes.linewidth": 0.8,
    "axes.edgecolor": "#3a3f4a",
    "xtick.color": "#3a3f4a",
    "ytick.color": "#3a3f4a",
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "savefig.facecolor": "white",
    "savefig.dpi": 300,
})

INK = "#1a1a2e"
MUTED = "#8a8f98"
GRIDC = "#e7e8ec"
BLUE = "#0072B2"      # NR4A3 / primary
VERM = "#D55E00"      # NR4A1
PURP = "#CC79A7"      # NR4A2
GREEN = "#0f9d58"     # status: druggable / pass
AMBER = "#b45309"     # caution
PARA = {"NR4A3": BLUE, "NR4A1": VERM, "NR4A2": PURP}
PARA_ORDER = ["NR4A3", "NR4A1", "NR4A2"]


def panel_label(ax, letter, dx=-0.11, dy=1.04):
    ax.text(dx, dy, letter, transform=ax.transAxes, fontsize=13, fontweight="bold",
            va="top", ha="left", color=INK)


def tidy(ax, grid_axis="y"):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    if grid_axis:
        ax.grid(True, axis=grid_axis, color=GRIDC, lw=0.8, zorder=0)
    ax.set_axisbelow(True)


def save(fig, name):
    png = os.path.join(HERE, f"{name}.png")
    fig.savefig(png, bbox_inches="tight")
    fig.savefig(os.path.join(HERE, f"{name}.pdf"), bbox_inches="tight")
    plt.close(fig)
    print(f"wrote {name}.png / .pdf")


# =============================================================================
# Fig 1 — calibrated druggability + PocketMiner
# =============================================================================
def fig1():
    fig, (axL, axR) = plt.subplots(1, 2, figsize=(9.4, 4.0),
                                   gridspec_kw={"width_ratios": [1.05, 1.25]})

    # (a) calibration bar
    names = ["PPARγ\n(rosi)", "ERα\n(E2)", "Nurr1\nholo", "Nur77\nholo", "NR4A3\nstatic", "NR4A3\nopened"]
    vals = [0.599, 0.586, 0.677, 0.529, 0.495, 0.931]
    kinds = ["bound", "bound", "bound", "bound", "static", "opened"]
    colors = {"bound": "#c7d9f0", "static": VERM, "opened": BLUE}
    bars = []
    for i, (v, k) in enumerate(zip(vals, kinds)):
        b = axL.bar(i, v, width=0.72, color=colors[k], edgecolor=INK, lw=0.7, zorder=3,
                    hatch=("////" if k == "opened" else None))
        bars.append(b)
        axL.text(i, v + 0.018, f"{v:.3f}", ha="center", va="bottom", fontsize=8.0, color=INK)
    axL.axhspan(0.53, 0.68, color=GREEN, alpha=0.10, zorder=1)
    axL.axhline(0.53, color=GREEN, lw=1.4, ls="--", zorder=2)
    axL.text(5.62, 0.53, "D* = 0.53\n(drug-bound floor)", ha="left", va="center",
             fontsize=7.4, color=GREEN)
    axL.set_xticks(range(len(names)))
    axL.set_xticklabels(names, fontsize=7.8)
    axL.set_ylabel("fpocket druggability")
    axL.set_xlim(-0.6, 7.4)
    axL.set_ylim(0, 1.0)
    axL.set_title("Orthosteric pocket is borderline — calibrated", color=INK, pad=8)
    tidy(axL, "y")
    leg = [Patch(fc="#c7d9f0", ec=INK, lw=0.7, label="drug-bound NR (static)"),
           Patch(fc=VERM, ec=INK, lw=0.7, label="NR4A3 static (0.495)"),
           Patch(fc=BLUE, ec=INK, lw=0.7, hatch="////", label="NR4A3 opened (biased-MD peak)")]
    axL.legend(handles=leg, loc="upper left", fontsize=7.0, frameon=False,
               bbox_to_anchor=(0.0, 1.0), handlelength=1.3)

    # (b) PocketMiner per-residue
    pm = json.load(open(os.path.join(HERE, "nr4a3-pocketminer-result.json")))
    scores = pm["pocket5_scores"]
    handles = set(str(h) for h in pm["pocket5_handles"])
    resids = sorted(scores, key=lambda r: int(r))
    yv = [scores[r] for r in resids]
    xc = np.arange(len(resids))
    bar_colors = [BLUE if r in handles else "#b9c0cc" for r in resids]
    axR.bar(xc, yv, width=0.74, color=bar_colors, edgecolor=INK, lw=0.6, zorder=3)
    bg = pm["overlap"]["lbd_mean_score"]
    axR.axhline(bg, color=MUTED, lw=1.3, ls=":", zorder=2)
    axR.text(len(resids) - 0.4, bg - 0.045, f"LBD background {bg:.2f}", ha="right", va="top",
             fontsize=7.4, color=MUTED)
    axR.axhline(0.5, color=AMBER, lw=1.0, ls="--", zorder=2, alpha=0.7)
    axR.text(0.1, 0.51, "0.5", fontsize=7.0, color=AMBER, va="bottom")
    axR.set_xticks(xc)
    axR.set_xticklabels(resids, fontsize=8.0)
    axR.set_xlabel("Pocket-5 residue (Q92570)")
    axR.set_ylabel("PocketMiner cryptic-pocket propensity")
    axR.set_ylim(0, 1.0)
    enr = pm["overlap"]["enrichment_pocket5_over_lbd"]
    axR.set_title(f"Independent cross-check: {enr:.2f}× enriched over LBD", color=INK, pad=8)
    tidy(axR, "y")
    axR.legend(handles=[Patch(fc=BLUE, ec=INK, lw=0.6, label="selectivity handle"),
                        Patch(fc="#b9c0cc", ec=INK, lw=0.6, label="other Pocket-5 residue")],
               loc="upper right", fontsize=7.0, frameon=False)

    panel_label(axL, "a")
    panel_label(axR, "b")
    fig.tight_layout(w_pad=2.6)
    save(fig, "nr4a3-fig1")


# =============================================================================
# Fig 2 — metad F(Rg) + release run
# =============================================================================
def fig2():
    import report_metad as rm
    KJ = 4.184
    fig, (axL, axR) = plt.subplots(1, 2, figsize=(9.4, 4.0),
                                   gridspec_kw={"width_ratios": [1.35, 1.0]})

    # (a) F(Rg)
    pts = rm.parse_fes(os.path.join(HERE, "metad-fes-60ns.dat"))
    fmin = min(f for _r, f in pts)
    rg = np.array([p[0] for p in pts])
    fk = np.array([(p[1] - fmin) / KJ for p in pts])
    m = (rg >= 0.60) & (rg <= 1.12)
    axL.plot(rg[m], fk[m], color=BLUE, lw=2.2, zorder=3)
    # basin minimum
    i0 = int(np.argmin(fk))
    axL.scatter([rg[i0]], [fk[i0]], s=36, color=INK, zorder=5)
    axL.annotate(f"closed basin\n(Rg {rg[i0]:.2f} nm)", (rg[i0], fk[i0]),
                 xytext=(rg[i0] + 0.03, fk[i0] + 4.5), fontsize=7.8, color=INK,
                 arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8))
    # druggable release frame ~0.737
    dr = 0.737
    idr = int(np.argmin(np.abs(rg - dr)))
    axL.scatter([rg[idr]], [fk[idr]], s=40, color=GREEN, zorder=5, marker="D")
    axL.annotate(f"druggable release frame\n(Rg ≈ 0.74, ~0.6 kcal/mol)", (rg[idr], fk[idr]),
                 xytext=(rg[idr] + 0.05, fk[idr] + 8), fontsize=7.8, color=GREEN,
                 arrowprops=dict(arrowstyle="-", color=GREEN, lw=0.8))
    # frontier
    ifr = int(np.argmin(np.abs(rg - 1.06)))
    axL.annotate(f"open frontier\n~{fk[ifr]:.0f} kcal/mol", (rg[ifr], fk[ifr]),
                 xytext=(rg[ifr] - 0.02, fk[ifr] - 1), fontsize=7.8, color=MUTED, ha="right", va="top")
    axL.set_xlabel("Pocket-5 radius of gyration, Rg (nm)")
    axL.set_ylabel("free energy F(Rg) (kcal/mol)")
    axL.set_title("Single breathing basin (60 ns; no separate opened minimum)", color=INK, pad=8)
    tidy(axL, "y")

    # (b) release-run druggability summary
    metrics = ["frac ≥ D*\n(0.53)", "frac ≥ 0.5", "mean", "max", "static\nAF2"]
    mv = [0.20, 0.24, 0.262, 0.842, 0.495]
    mc = [GREEN, GREEN, BLUE, BLUE, MUTED]
    xb = np.arange(len(metrics))
    axR.bar(xb, mv, width=0.66, color=mc, edgecolor=INK, lw=0.6, zorder=3)
    for x, v in zip(xb, mv):
        axR.text(x, v + 0.012, f"{v:.2f}" if v < 1 else f"{v}", ha="center", va="bottom",
                 fontsize=8.0, color=INK)
    axR.axhline(0.53, color=GREEN, ls="--", lw=1.1, alpha=0.6, zorder=2)
    axR.set_xticks(xb)
    axR.set_xticklabels(metrics, fontsize=7.6)
    axR.set_ylabel("fpocket druggability (unbiased frames)")
    axR.set_ylim(0, 1.0)
    axR.set_title("Unbiased release run: metastable (3/3), druggable ~24 %", color=INK, pad=8)
    tidy(axR, "y")

    panel_label(axL, "a")
    panel_label(axR, "b")
    fig.tight_layout(w_pad=2.6)
    save(fig, "nr4a3-fig2")


# =============================================================================
# Fig 3 — selectivity handles
# =============================================================================
def fig3():
    fig, (axL, axR) = plt.subplots(1, 2, figsize=(9.4, 3.9),
                                   gridspec_kw={"width_ratios": [1.3, 0.95]})

    # (a) handle-facing fraction in druggable frames
    # engageable five are >=0.875 (paper §2.2); the two splay-out at exact stated values
    handles = ["L406", "T410", "I484", "I531", "L534", "T407", "R412"]
    facing = [0.875, 0.875, 0.875, 0.875, 0.875, 0.00, 0.25]
    is_eng = [True, True, True, True, True, False, False]
    xh = np.arange(len(handles))
    for x, v, e in zip(xh, facing, is_eng):
        axL.bar(x, v, width=0.66, color=(BLUE if e else "#c9ccd3"), edgecolor=INK, lw=0.6, zorder=3)
        lbl = "≥0.875" if e else f"{v:.2f}"
        axL.text(x, v + 0.02, lbl, ha="center", va="bottom", fontsize=7.6, color=INK)
    axL.set_xticks(xh)
    axL.set_xticklabels(handles, fontsize=8.4)
    axL.set_ylabel("pocket-facing fraction (druggable frames)")
    axL.set_ylim(0, 1.05)
    axL.set_title("5 of 7 divergent handles stay engageable (mean 5.0/7)", color=INK, pad=8)
    tidy(axL, "y")
    axL.legend(handles=[Patch(fc=BLUE, ec=INK, lw=0.6, label="engageable (pocket-facing)"),
                        Patch(fc="#c9ccd3", ec=INK, lw=0.6, label="splays outward")],
               loc="center right", fontsize=7.2, frameon=False)

    # (b) divergence asymmetry vs each paralogue
    cats = ["vs NR4A1", "vs NR4A2"]
    div_all = [7, 6]        # of 7 handles
    div_eng = [5, 4]        # of 5 engageable
    xg = np.arange(len(cats))
    w = 0.36
    axR.bar(xg - w/2, div_all, width=w, color="#b9c0cc", edgecolor=INK, lw=0.6, zorder=3, label="all handles (of 7)")
    axR.bar(xg + w/2, div_eng, width=w, color=BLUE, edgecolor=INK, lw=0.6, zorder=3, label="engageable (of 5)")
    for x, v in zip(xg - w/2, div_all):
        axR.text(x, v + 0.08, str(v), ha="center", va="bottom", fontsize=8.2, color=INK)
    for x, v in zip(xg + w/2, div_eng):
        axR.text(x, v + 0.08, str(v), ha="center", va="bottom", fontsize=8.2, color=INK)
    axR.set_xticks(xg)
    axR.set_xticklabels(cats, fontsize=8.6)
    axR.set_ylabel("divergent handles")
    axR.set_ylim(0, 8)
    axR.set_title("Asymmetric window\n(I531 shared with NR4A2)", color=INK, pad=8)
    tidy(axR, "y")
    axR.legend(loc="upper right", fontsize=7.2, frameon=False)

    panel_label(axL, "a")
    panel_label(axR, "b")
    fig.tight_layout(w_pad=2.6)
    save(fig, "nr4a3-fig3")


# =============================================================================
# Fig 4 — family-wide state-matched selectivity fingerprint (heatmap)
# =============================================================================
def fig4():
    def clean_label(lbl):
        lbl = lbl.replace("NR4A3-active:", "")
        if "xxxx" in lbl.lower():
            return "ChEMBL active (equipotent)"
        if lbl.startswith("CHEMBL"):
            return "ChEMBL " + lbl[6:]
        return lbl

    pr = json.load(open(os.path.join(HERE, "nr4a3-pan-readout.json")))
    rows = []  # (label, dG dict, cell)
    for m in pr["repurposed_library_pan_cell"]["members"]:
        rows.append((clean_label(m["label"]), m["dG"], "pan"))
    for m in pr["denovo_pan_cell"].get("members", []):
        if isinstance(m, dict) and "dG" in m:
            rows.append((clean_label(m["label"]), m["dG"], "pan"))
    for m in pr["pan_designed_campaign"].get("pan_leads", []):
        rows.append((clean_label(m["label"]), m["dG"], "pan"))
    # de-dup by label
    seen, uniq = set(), []
    for r in rows:
        if r[0] not in seen:
            seen.add(r[0]); uniq.append(r)
    labels = [r[0] for r in uniq]
    mat = np.array([[r[1][p] for p in PARA_ORDER] for r in uniq])

    fig, ax = plt.subplots(figsize=(6.2, 0.5 * len(labels) + 2.0))
    im = ax.imshow(mat, cmap="Blues_r", aspect="auto", vmin=mat.min(), vmax=mat.max())
    ax.set_xticks(range(3)); ax.set_xticklabels(PARA_ORDER, fontsize=9)
    ax.set_yticks(range(len(labels))); ax.set_yticklabels(labels, fontsize=8.2)
    for i in range(len(labels)):
        for j in range(3):
            ax.text(j, i, f"{mat[i, j]:.2f}", ha="center", va="center", fontsize=7.8,
                    color=("white" if mat[i, j] < (mat.min() + mat.max()) / 2 else INK))
    # color the target column tick
    ax.get_xticklabels()[0].set_color(BLUE)
    ax.get_xticklabels()[0].set_fontweight("bold")
    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label("docking ΔG (kcal/mol)  — more negative = tighter", fontsize=8.0)
    ax.set_title("State-matched selectivity fingerprint\n(candidates × opened NR4A pockets; docking-tier priors)",
                 color=INK, fontsize=10, pad=10)
    ax.set_xlabel("opened paralogue pocket")
    fig.tight_layout()
    save(fig, "nr4a3-fig4")


# =============================================================================
# Fig 5 — de-novo: de-noising + frame-decoy null + lead structure
# =============================================================================
def fig5():
    fig = plt.figure(figsize=(10.4, 8.0))
    gs = fig.add_gridspec(2, 2, height_ratios=[1.0, 1.02], width_ratios=[1.18, 1.0],
                          hspace=0.40, wspace=0.30)
    ax_a = fig.add_subplot(gs[0, 0]); ax_b = fig.add_subplot(gs[0, 1])
    ax_c = fig.add_subplot(gs[1, 0]); ax_d = fig.add_subplot(gs[1, 1])

    # (a) multi-snapshot de-noising
    ROWS = [
        ("denovo_393", 18.34, -2.95, 3.65, "collapses"),
        ("denovo_780", 14.66, 2.07, 6.36, "noise"),
        ("denovo_924*", -19.41, -25.20, 4.55, "neg. control"),
        ("denovo_111", 15.70, 14.60, 4.10, "withdrawn"),
        ("denovo_401", 13.92, 12.83, 2.98, "holds"),
    ]
    for y, (name, single, mean, sd, tag) in enumerate(ROWS):
        ax_a.plot([single, mean], [y, y], color=MUTED, lw=1.3, alpha=0.7, zorder=2)
        ax_a.scatter([single], [y], s=30, facecolor="white", edgecolor=MUTED, lw=1.2, zorder=3)
        hue = GREEN if tag == "holds" else (VERM if tag in ("collapses", "withdrawn") else MUTED)
        ax_a.errorbar([mean], [y], xerr=[sd], fmt="o", color=hue, ms=7, capsize=3.5, lw=1.4, zorder=4)
    ax_a.axvline(0, color=INK, lw=0.9, zorder=1)
    ax_a.axvline(6.69, color=AMBER, lw=1.1, ls="--", zorder=1)
    ax_a.text(7.4, 3.45, "multi-snapshot\ndecoy 95th (+6.69)", fontsize=6.9, color=AMBER, va="center", ha="left")
    ax_a.set_yticks(range(len(ROWS)))
    ax_a.set_yticklabels([r[0] for r in ROWS], fontsize=8.0)
    ax_a.set_xlabel("NR4A3-selectivity margin (kcal/mol)")
    ax_a.set_title("Multi-snapshot de-noising", color=INK, pad=8)
    ax_a.legend(handles=[plt.Line2D([], [], marker="o", ls="", mfc="white", mec=MUTED, label="single-snapshot"),
                         plt.Line2D([], [], marker="o", ls="", color=INK, label="multi-snapshot ± SD")],
                loc="lower right", fontsize=6.8, frameon=False)
    tidy(ax_a, "x")

    # (b) frame-dependence of decoy null
    FR = [("release\n(design frame)", 6.69, 7.10, 12.83, 2.98, GREEN, "clears"),
          ("metad-opened\n(off-design)", 17.70, 24.74, 7.44, 4.18, VERM, "fails")]
    for y, (name, p95, mx, margin, sd, col, tag) in enumerate(FR):
        yy = len(FR) - 1 - y
        ax_b.barh(yy, mx, height=0.5, color="#e9ecf2", edgecolor=MUTED, lw=0.7, zorder=2)
        ax_b.barh(yy, p95, height=0.5, color="#cfd6e4", edgecolor=MUTED, lw=0.7, zorder=3)
        ax_b.errorbar([margin], [yy], xerr=[sd], fmt="D", color=col, ms=9, capsize=4, lw=1.5, zorder=5)
        ax_b.text(margin + sd + 0.7, yy, f"denovo_401\n{margin:+.1f} ({tag})", ha="left", va="center",
                  fontsize=7.0, color=col)
    ax_b.set_yticks(range(len(FR)))
    ax_b.set_yticklabels([f[0] for f in reversed(FR)], fontsize=8.0)
    ax_b.set_xlabel("NR4A3-selectivity margin (kcal/mol)")
    ax_b.set_title("Decoy null is receptor-frame-dependent", color=INK, pad=8)
    ax_b.legend(handles=[Patch(fc="#cfd6e4", ec=MUTED, label="decoy null 95th pct"),
                         Patch(fc="#e9ecf2", ec=MUTED, label="decoy null max")],
                loc="lower right", fontsize=6.8, frameon=False)
    tidy(ax_b, "x")

    # (c) lead structure (RDKit)
    _draw_molecule(ax_c, "COC[C@H](c1ccccc1)[C@@H]1CC[C@H](CC(C)(C)[C@@H](C)O)C1",
                   "denovo_401  (MW 304, QED 0.80, SA 3.87)")

    # (d) docked pose in the metad-opened NR4A3 pocket (committed PyMOL render, whitespace-trimmed)
    _draw_pose(ax_d, "nr4a3-pose.png",
               "denovo_401 docked in the opened NR4A3 LBD\n(orange = warhead; grey = pocket residues)")

    panel_label(ax_a, "a"); panel_label(ax_b, "b")
    panel_label(ax_c, "c", dx=-0.05); panel_label(ax_d, "d", dx=-0.05)
    save(fig, "nr4a3-fig5")


def _draw_pose(ax, fname, title):
    try:
        from PIL import Image, ImageChops
        im = Image.open(os.path.join(HERE, fname)).convert("RGB")
        bg = Image.new("RGB", im.size, (255, 255, 255))
        bbox = ImageChops.difference(im, bg).getbbox()
        if bbox:
            pad = 12
            bbox = (max(0, bbox[0] - pad), max(0, bbox[1] - pad),
                    min(im.width, bbox[2] + pad), min(im.height, bbox[3] + pad))
            im = im.crop(bbox)
        ax.imshow(np.asarray(im))
    except Exception as e:  # pragma: no cover
        ax.text(0.5, 0.5, f"[pose]\n{e}", ha="center", va="center", fontsize=8)
    ax.set_title(title, color=INK, fontsize=9.2, pad=8)
    ax.axis("off")


def _draw_molecule(ax, smiles, title):
    try:
        from rdkit import Chem
        from rdkit.Chem.Draw import rdMolDraw2D
        mol = Chem.MolFromSmiles(smiles)
        from rdkit.Chem import AllChem
        AllChem.Compute2DCoords(mol)
        d = rdMolDraw2D.MolDraw2DCairo(520, 460)
        opts = d.drawOptions()
        opts.bondLineWidth = 2
        opts.clearBackground = True
        rdMolDraw2D.PrepareAndDrawMolecule(d, mol)
        d.FinishDrawing()
        png = os.path.join(HERE, "_lead_tmp.png")
        with open(png, "wb") as fh:
            fh.write(d.GetDrawingText())
        import matplotlib.image as mpimg
        ax.imshow(mpimg.imread(png))
        os.remove(png)
    except Exception as e:  # pragma: no cover
        ax.text(0.5, 0.5, f"[structure]\n{e}", ha="center", va="center", fontsize=8)
    ax.set_title(title, color=INK, fontsize=9.2, pad=8)
    ax.axis("off")


# =============================================================================
# Fig 6 — programmable axis: census flip + designed pan lead
# =============================================================================
def fig6():
    pr = json.load(open(os.path.join(HERE, "nr4a3-pan-readout.json")))
    census = pr["pan_designed_campaign"]["cell_census"]
    fig, (axL, axR) = plt.subplots(1, 2, figsize=(9.6, 4.0),
                                   gridspec_kw={"width_ratios": [1.15, 1.0]})

    # (a) census: selective-run by-catch vs conserved-core-designed
    cells = ["NR4A3-\nselective", "pan-NR4A", "none/\nother"]
    selective_run = [3, 2, 6]     # selective campaign: 3 selective (denovo_15/94/57), pan by-catch 2, rest
    conserved_run = [census.get("nr4a3-selective", 0), census.get("pan-NR4A", 0),
                     census.get("none", 0) + census.get("NR4A1+NR4A2", 0)]
    xg = np.arange(len(cells)); w = 0.38
    axL.bar(xg - w/2, selective_run, width=w, color="#b9c0cc", edgecolor=INK, lw=0.6, zorder=3,
            label="ranked on divergent handles")
    axL.bar(xg + w/2, conserved_run, width=w, color=BLUE, edgecolor=INK, lw=0.6, zorder=3,
            label="ranked on conserved core")
    for x, v in zip(xg - w/2, selective_run):
        axL.text(x, v + 0.06, str(v), ha="center", va="bottom", fontsize=8.4, color=INK)
    for x, v in zip(xg + w/2, conserved_run):
        axL.text(x, v + 0.06, str(v), ha="center", va="bottom", fontsize=8.4, color=INK)
    axL.set_xticks(xg); axL.set_xticklabels(cells, fontsize=8.2)
    axL.set_ylabel("docked candidates in cell")
    axL.set_title("Re-ranking the SAME framework flips the census", color=INK, pad=8)
    tidy(axL, "y")
    axL.legend(loc="upper center", fontsize=7.2, frameon=False)

    # (b) designed pan lead denovo_9: balanced tri-engagement
    d9 = None
    for m in pr["pan_designed_campaign"]["pan_leads"]:
        if m["label"] == "denovo_9":
            d9 = m; break
    dg = d9["dG"]
    xb = np.arange(3)
    axR.bar(xb, [dg[p] for p in PARA_ORDER], width=0.6,
            color=[PARA[p] for p in PARA_ORDER], edgecolor=INK, lw=0.7, zorder=3)
    for x, p in zip(xb, PARA_ORDER):
        axR.text(x, dg[p] * 0.5, f"{dg[p]:.2f}", ha="center", va="center", fontsize=9.2,
                 fontweight="bold", color="white")
    axR.set_xticks(xb); axR.set_xticklabels(PARA_ORDER, fontsize=9)
    axR.set_ylabel("docking ΔG (kcal/mol)")
    axR.set_ylim(min(dg.values()) - 1.0, 0)
    axR.set_title("Designed pan lead denovo_9\n(balanced within 0.4 kcal/mol)", color=INK, pad=8)
    tidy(axR, "y")
    axR.text(0.5, -0.22, "selective pole: denovo_401 (FEP ΔΔG −4.8 / −5.0 kcal/mol vs NR4A1 / NR4A2)",
             transform=axR.transAxes, ha="center", va="top", fontsize=7.2, color=MUTED)

    panel_label(axL, "a"); panel_label(axR, "b")
    fig.tight_layout(w_pad=2.6)
    save(fig, "nr4a3-fig6")


# =============================================================================
# Supplementary figures (S1, S3, S4, S5). S2 = committed molecular pose render.
# =============================================================================
def figS1():
    FRAMES = [("release /\ndesign frame", {"NR4A3": -37.50, "NR4A1": -22.75, "NR4A2": -20.43}, 14.75),
              ("metad-opened\nframe", {"NR4A3": -32.37, "NR4A1": -24.93, "NR4A2": -22.80}, 7.44)]
    fig, ax = plt.subplots(figsize=(6.6, 4.4))
    centers = np.arange(len(FRAMES)) * 1.5
    bw = 0.32
    for gi, (name, dg, margin) in enumerate(FRAMES):
        for ri, rec in enumerate(PARA_ORDER):
            x = centers[gi] + (ri - 1) * bw
            ax.bar(x, dg[rec], width=bw * 0.92, color=PARA[rec], edgecolor=INK, lw=0.6, zorder=3,
                   label=rec if gi == 0 else None)
            ax.text(x, dg[rec] * 0.5, f"{dg[rec]:.1f}", ha="center", va="center", fontsize=7.8,
                    fontweight="bold", color="white")
        ax.text(centers[gi], -40.5, f"NR4A3 margin +{margin:.2f}", ha="center", va="center",
                fontsize=8.2, color=INK, fontweight="bold")
    ax.axhline(0, color=INK, lw=0.9)
    ax.set_xticks(centers)
    ax.set_xticklabels([f[0] for f in FRAMES], fontsize=8.6)
    ax.set_ylabel("multi-snapshot MM-GBSA ΔG (kcal/mol)")
    ax.set_ylim(-43, 2)
    ax.set_title("denovo_401: NR4A3-favoured in both frames\n(direction frame-robust; magnitude frame-dependent)",
                 color=INK, fontsize=10, pad=10)
    ax.legend(loc="upper right", fontsize=8, frameon=False, ncol=3)
    tidy(ax, "y")
    fig.tight_layout()
    save(fig, "nr4a3-figS1")


def figS3():
    ROWS = [("orthosteric cryptic pocket\n(warhead contacts)", 10, 70, 60),
            ("predicted NR4A3–CRBN\nternary interface", 33, 24, 18),
            ("LBD-wide pocket census", 148, 45, 28),
            ("non-orthosteric remainder\n(surface / PPI proxy)", 138, 43, None)]
    fig, ax = plt.subplots(figsize=(7.2, 3.8))
    y = np.arange(len(ROWS))[::-1]
    h = 0.34
    for yy, (name, n, d1, d2) in zip(y, ROWS):
        ax.barh(yy + h/2, d1, height=h, color="#b9c0cc", edgecolor=INK, lw=0.6, zorder=3,
                label="vs ≥1 paralogue" if yy == y[0] else None)
        ax.text(d1 + 1, yy + h/2, f"{d1}%", va="center", fontsize=7.8, color=INK)
        if d2 is not None:
            ax.barh(yy - h/2, d2, height=h, color=BLUE, edgecolor=INK, lw=0.6, zorder=3,
                    label="vs both paralogues" if yy == y[0] else None)
            ax.text(d2 + 1, yy - h/2, f"{d2}%", va="center", fontsize=7.8, color=INK)
    ax.set_yticks(y)
    ax.set_yticklabels([f"{r[0]}  (n = {r[1]})" for r in ROWS], fontsize=8.0)
    ax.set_xlabel("paralogue-divergent residues (%)")
    ax.set_xlim(0, 85)
    ax.set_title("The orthosteric pocket is the most paralogue-divergent LBD zone", color=INK, fontsize=10, pad=8)
    ax.legend(loc="lower right", fontsize=7.6, frameon=False)
    tidy(ax, "x")
    fig.tight_layout()
    save(fig, "nr4a3-figS2")


def figS4():
    d = json.load(open(os.path.join(HERE, "nr4a-superfamily-selectivity.json")))
    controls = {c["gene"] for c in d["controls_paralogues"]}
    flagged = {f["gene"] for f in d["flagged_liabilities"]}
    fig, ax = plt.subplots(figsize=(6.8, 4.6))
    disp = {"NR3C2": "MR (NR3C2)", "AR": "AR"}
    label_off = {"NR4A2": (7, 6), "NR4A1": (7, -12), "NR3C2": (8, 4), "AR": (8, -12), "PGR": (8, 2)}
    for r in d["ranking"]:
        g, ov, pid = r["gene"], r["overall_identity"], r["pocket_identity"]
        if g in controls:
            col, mk, sz, z = BLUE, "o", 70, 5
        elif g in flagged:
            col, mk, sz, z = AMBER, "D", 66, 5
        else:
            col, mk, sz, z = "#c2c7d0", "o", 34, 3
        ax.scatter(ov, pid, s=sz, marker=mk, color=col, edgecolor=INK, lw=0.6, zorder=z)
        if ov >= 0.30 and (g in controls or g in flagged or g == "PGR"):
            dx, dy = label_off.get(g, (6, 6))
            ax.annotate(disp.get(g, g), (ov, pid), textcoords="offset points", xytext=(dx, dy),
                        fontsize=7.8, color=INK, fontweight=("bold" if g in flagged else "normal"))
    ax.axvline(0.30, color=MUTED, ls="--", lw=1.1, zorder=1)
    ax.text(0.305, 0.02, "confidence gate\n(overall id ≥ 0.30)", fontsize=7.2, color=MUTED, va="bottom")
    ax.set_xlabel("overall NR4A3-LBD alignment identity (mapping confidence)")
    ax.set_ylabel("warhead-pocket residue identity (of 10)")
    ax.set_title("Superfamily pocket-liability screen (47 human NRs)\nonly paralogues + MR/AR clear the gate",
                 color=INK, fontsize=10, pad=8)
    ax.legend(handles=[plt.Line2D([], [], marker="o", ls="", color=BLUE, mec=INK, label="paralogue control"),
                       plt.Line2D([], [], marker="D", ls="", color=AMBER, mec=INK, label="flagged (MR / AR)"),
                       plt.Line2D([], [], marker="o", ls="", color="#c2c7d0", mec=INK, label="other NR")],
              loc="upper right", fontsize=7.4, frameon=False)
    tidy(ax, None)
    ax.grid(True, color=GRIDC, lw=0.8, zorder=0)
    fig.tight_layout()
    save(fig, "nr4a3-figS3")


def figS5():
    d = json.load(open(os.path.join(HERE, "nr4a-safety-genetics.json")))
    loeuf = {g: d["gnomad_lof_constraint"]["genes"][g]["loeuf"] for g in ("NR4A1", "NR4A2", "NR4A3")}
    depmap = {"NR4A1": -0.115, "NR4A2": -0.05, "NR4A3": 0.023}
    fig, ax = plt.subplots(figsize=(6.4, 4.6))
    off = {"NR4A1": (9, 8), "NR4A2": (10, -6), "NR4A3": (10, 9)}
    for g in ("NR4A1", "NR4A2", "NR4A3"):
        ax.scatter(depmap[g], loeuf[g], s=90, color=PARA[g], edgecolor=INK, lw=0.8, zorder=5)
        ax.annotate(g, (depmap[g], loeuf[g]), textcoords="offset points", xytext=off[g],
                    fontsize=8.6, color=INK, fontweight="bold")
    ax.axvline(-0.5, color=MUTED, ls="--", lw=1.0)
    ax.text(-0.49, 0.05, "DepMap dependency\n(< −0.5)", fontsize=7.0, color=MUTED, va="bottom")
    ax.axhline(0.35, color=AMBER, ls="--", lw=1.1)
    ax.text(0.05, 0.33, "gnomAD LoF-intolerant (LOEUF < 0.35)", fontsize=7.2, color=AMBER, va="top", ha="right")
    ax.set_xlabel("DepMap CRISPR gene effect (proliferative essentiality)")
    ax.set_ylabel("gnomAD LOEUF (germline LoF constraint)")
    ax.set_xlim(-0.6, 0.15)
    ax.set_ylim(0, 0.85)
    ax.set_title("‘Dispensable ⇒ safe’ is invalid: NR4A3/NR4A2 are LoF-constrained\ndespite being dispensable for proliferation",
                 color=INK, fontsize=9.6, pad=8)
    tidy(ax, None)
    ax.grid(True, color=GRIDC, lw=0.8, zorder=0)
    fig.tight_layout()
    save(fig, "nr4a3-figS4")


FIGS = {"1": fig1, "2": fig2, "3": fig3, "4": fig4, "5": fig5, "6": fig6,
        "S1": figS1, "S2": figS3, "S3": figS4, "S4": figS5}

if __name__ == "__main__":
    which = sys.argv[1:] or list(FIGS)
    for k in which:
        FIGS[k]()
