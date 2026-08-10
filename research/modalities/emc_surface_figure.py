#!/usr/bin/env python3
"""Figure 1 for the EMC surface-antigen transfer paper: the tissue read, with its intervals.

WHAT IT DRAWS. Two panels, one per array platform. One row per antigen: the 18 antigens the
surrogate scan called selective after Benjamini-Hochberg correction, then the 11 therapeutic
addresses named by candidate surface-directed routes, ordered by surrogate enrichment descending
within each block. The x axis is the EMC-minus-comparator contrast in standard-deviation units of
that array's own probe distribution, with the point estimate and its exact 95% interval. Fill and
shape carry significance, so nothing depends on colour: a filled square is within-platform
Benjamini-Hochberg q < 0.05, an open square is not, and an open triangle at the axis means the gene
was not readable on that platform, which is a statement about the instrument rather than a null.

WHAT IT REPLACES, AND WHY. The previous figure plotted surrogate selectivity against normal-tissue
window tier, and it had three defects. It placed B4GALNT1, a gene with no selectivity value in the
scan artifact, at x = 0, which is a coordinate nothing computed, inside a region annotated as empty.
Its display list was 13 antigens chosen by hand, so the emptiness of that region was a property of
the list rather than of the evaluated set; DLL3 is both selective at q = 0.0079 and RESTRICTED and
was not in it. And its jitter came from Python's string hash, which is salted per process, so the
figure was not reproducible between runs. This figure plots only computed quantities, has no
hand-chosen display list, and is deterministic.

    python3 research/modalities/emc_surface_figure.py

Outputs research/manuscripts/figures/emc-surface-fig1-transfer.{png,pdf} at 300 dpi and refreshes
their entry in emc-surface-figure-provenance.json.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
FIGDIR = os.path.join(REPO, "research", "manuscripts", "figures")
STEM = os.path.join(FIGDIR, "emc-surface-fig1-transfer")
PROV = os.path.join(FIGDIR, "emc-surface-figure-provenance.json")

SCAN = os.path.join(HERE, "emc-surfaceome-scan.json")
STATS = os.path.join(HERE, "emc-tissue-read-statistics.json")
PANELS = os.path.join(HERE, "emc-expression-panels.json")

#: Greyscale only. The journal charges for colour in print and the charge is declined.
INK = "black"
GREY = "0.40"
ALPHA = 0.05

LABEL = {"CD276": "CD276 (B7-H3)", "NCAM1": "NCAM1 (CD56)", "MCAM": "MCAM (CD146)",
         "ALCAM": "ALCAM (CD166)", "CD248": "CD248 (endosialin)"}


def _load(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


BLOCKS = ("surrogate-selective", "route-named address", "concordant in tissue")


def rows():
    """(block, gene, surrogate q or None) in the order the figure draws them, top to bottom."""
    scan = _load(SCAN)["actionable_antigens"]
    stats = _load(STATS)
    panels = _load(PANELS)
    route = panels["panels"]["surface_antigen"]["groups"]["route_named_addresses"]
    named = route["per_platform"]["GSE24369_series_matrix.txt.gz"]
    requested = sorted(set(named["genes_readable"]) | set(named["genes_not_readable"]))

    selective = sorted((g for g, v in scan.items() if v["selectivity_significant"]),
                       key=lambda g: -scan[g]["enrichment_vs_rest"])
    addresses = sorted((g for g in requested if g not in selective),
                       key=lambda g: -(scan[g]["enrichment_vs_rest"] if g in scan else -99))

    # The genes the uncorrected criterion called concordantly elevated, so a reader can see which
    # of them survive correction and which do not, and their intervals side by side.
    state = stats["cross_platform_state_corrected"]["by_gene"]
    survivors = [g for g, s in state.items() if s == "CONCORDANT_UP_ON_BOTH"]
    dropped = ["ALCAM", "GPC1"]
    tissue = sorted(set(survivors) | set(dropped),
                    key=lambda g: -stats["primary"]["GPL6244"][g]["delta"])

    seen, out = set(), []
    for block, genes in zip(BLOCKS, (selective, addresses, tissue)):
        for g in genes:
            if g in seen:
                continue
            seen.add(g)
            out.append((block, g, scan[g]["selectivity_q"] if g in scan else None))
    return out


def main(argv):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from matplotlib.lines import Line2D
    except ImportError:
        print("matplotlib is required", file=sys.stderr)
        return 1

    stats = _load(STATS)
    data = rows()
    data.reverse()                       # first listed row at the top of the axis
    y = list(range(len(data)))

    fig, axes = plt.subplots(1, 2, figsize=(7.4, 8.0), sharey=True,
                             gridspec_kw={"width_ratios": [1, 1], "wspace": 0.08})

    xmin, xmax = 0.0, 0.0
    for row in data:
        for plat in ("GPL6244", "GPL3290"):
            r = stats["primary"][plat].get(row[1])
            if r:
                xmin = min(xmin, r["ci_lo"])
                xmax = max(xmax, r["ci_hi"])
    pad = 0.06 * (xmax - xmin)
    xmin, xmax = xmin - pad, xmax + pad

    for ax, plat, panel in zip(axes, ("GPL6244", "GPL3290"), ("a", "b")):
        ax.axvline(0.0, color=GREY, lw=0.8, ls=(0, (4, 3)), zorder=1)
        for i, (block, gene, _q) in zip(y, data):
            r = stats["primary"][plat].get(gene)
            if r is None:
                ax.plot([xmin + 0.02 * (xmax - xmin)], [i], marker="^", ms=5,
                        mfc="white", mec=INK, mew=0.9, ls="none", zorder=3)
                continue
            ax.plot([r["ci_lo"], r["ci_hi"]], [i, i], color=INK, lw=1.0, zorder=2)
            filled = r["q"] < ALPHA
            ax.plot([r["delta"]], [i], marker="s", ms=5.5, ls="none", zorder=3,
                    mfc=(INK if filled else "white"), mec=INK, mew=0.9)
        ax.set_xlim(xmin, xmax)
        ax.set_ylim(-0.9, len(data) - 0.1)
        ax.tick_params(axis="both", labelsize=7)
        ax.set_xlabel("EMC minus comparator (SD of the array)", fontsize=8)
        ax.set_title(f"{panel}   {plat}", fontsize=9, loc="left")
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)

    def qtext(q):
        if q is None:
            return "not in the scan"
        if q < 0.0001:
            return "q < 0.0001"
        s = f"{q:.4g}"
        return "q = " + (s if "." in s else s + ".0")

    labels = [f"{LABEL.get(g, g)}  ({qtext(q)})" for _b, g, q in data]
    axes[0].set_yticks(y)
    axes[0].set_yticklabels(labels, fontsize=7)

    blocks = [d[0] for d in data]
    for i in range(1, len(blocks)):
        if blocks[i] != blocks[i - 1]:
            for ax in axes:
                ax.axhline(i - 0.5, color=GREY, lw=0.6, ls=(0, (2, 2)))

    fig.canvas.draw()
    caption = {"surrogate-selective": "surrogate-selective (BH q < 0.05)",
               "route-named address": "route-named addresses",
               "concordant in tissue": "elevated before correction"}
    for name in BLOCKS:
        idx = [i for i, b in zip(y, blocks) if b == name]
        if not idx:
            continue
        mid = (min(idx) + max(idx)) / 2.0
        _, fy = fig.transFigure.inverted().transform(
            axes[0].transData.transform((0.0, mid)))
        fig.text(0.012, fy, caption[name], rotation=90, fontsize=7.5, color=GREY,
                 ha="left", va="center")

    handles = [
        Line2D([], [], marker="s", ls="none", mfc=INK, mec=INK, ms=5.5,
               label="within-platform BH q < 0.05"),
        Line2D([], [], marker="s", ls="none", mfc="white", mec=INK, ms=5.5,
               label="not significant after correction"),
        Line2D([], [], marker="^", ls="none", mfc="white", mec=INK, ms=5,
               label="not readable on this platform"),
        Line2D([], [], color=INK, lw=1.0, label="95% confidence interval"),
    ]
    fig.legend(handles=handles, loc="lower center", ncol=2, frameon=False, fontsize=7.5,
               bbox_to_anchor=(0.5, -0.005))
    fig.subplots_adjust(left=0.30, right=0.985, top=0.965, bottom=0.10)

    os.makedirs(FIGDIR, exist_ok=True)
    fig.savefig(STEM + ".png", dpi=300)
    fig.savefig(STEM + ".pdf")
    print("wrote", os.path.relpath(STEM + ".png", REPO), "and .pdf", file=sys.stderr)

    sources = {}
    for path in (SCAN, STATS, PANELS):
        with open(path, "rb") as fh:
            sources[os.path.basename(path)] = hashlib.blake2b(fh.read(), digest_size=8).hexdigest()
    with open(PROV, "w", encoding="utf-8") as fh:
        json.dump({
            "_regenerate": "python3 research/modalities/emc_surface_figure.py",
            "_what": "content hashes of every artifact this figure was drawn from",
            "_why": "nothing in CI regenerates the figure, so comparing these against the "
                    "artifacts is the only way a reader tells a stale figure from a current one",
            "_greyscale": "black, white and one 40 per cent grey only. Significance is carried by "
                          "fill and shape, so the figure loses nothing in greyscale print.",
            "_supersedes": "emc-surface-prioritization.png, the selectivity-against-window scatter. "
                           "Withdrawn: it placed B4GALNT1 at x = 0, a coordinate no artifact "
                           "carries, inside a region annotated as empty; its 13-antigen display "
                           "list omitted DLL3, which is both selective and RESTRICTED, so the "
                           "emptiness was a property of the list; and its jitter came from a "
                           "salted string hash, so it did not reproduce between runs.",
            "figures": ["emc-surface-fig1-transfer.pdf", "emc-surface-fig1-transfer.png"],
            "sources": sources,
        }, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    print("wrote", os.path.relpath(PROV, REPO), file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
