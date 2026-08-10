#!/usr/bin/env python3
"""Figures for the EMC PRMT5/MTAP preprint.

WHY THESE FOUR, AND WHY PER-SAMPLE DOTS DOMINATE. The manuscript rests on 6 and 10 tumours. At that
size a group mean and a t-statistic hide the one thing a reader most needs in order to judge the
claim — whether a single tumour carries the contrast. Every panel that can show the tumours shows
them.

  1  the two readings      per-sample dots for the methylosome and for the MTAP locus, both
                           platforms, on separate axes because the two platforms measure different
                           quantities (single-channel intensity vs two-colour log-ratio) and a shared
                           axis would invent comparability.
  2  the locus, gene by    MTAP, CDKN2A, CDKN2B separately. The paper's own caveat is that CDKN2A is
     gene                  lost by mechanisms leaving MTAP intact, so the group score is ambiguous by
                           construction. That caveat is invisible in a group bar and obvious here.
  3  ⛔ the dependency     PRMT5 and MAT2A against the sarcoma-line CRISPR panel. This figure ARGUES
     qualifier            AGAINST the paper's own proliferation reading and is included for that
                           reason: both are dependencies in almost every line, so a growth effect is
                           close to expected and only a transcriptional effect would be specific.
  4  the comparator        the methylosome in EMC against EACH comparator class, not a pooled arm.
     classes               A pooled arm hides that one comparator is itself a FET-fusion sarcoma.

RULES THE DRAWING ENFORCES
  * The two platforms never share an axis. Their value kinds differ and the panel artifact says so.
  * A gene with no probe is drawn as an explicit UNREADABLE marker, never as zero and never omitted.
    An absent reading is not a reading of absence.
  * No panel is scaled by an effect size that is not comparable to its neighbours.
  * Every number is read from a committed artifact. Nothing is computed here that the artifacts do
    not already carry, except the per-class medians, which are a re-cut of committed per-sample z.
  * ⛔ No axis, label or caption asserts efficacy, safety, a therapeutic window or clinical readiness.

USAGE
    python3 emc_mtap_prmt5_figures.py          # PNG (300 dpi) + PDF per figure, plus a provenance stamp
    python3 emc_mtap_prmt5_figures.py --check  # stdlib-only staleness check, draws nothing
"""

import argparse
import hashlib
import json
import os
import statistics as st
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FIGDIR = os.path.normpath(os.path.join(HERE, "..", "manuscripts", "figures"))
STAMP = os.path.join(FIGDIR, "mtap-prmt5-figure-provenance.json")

PANEL = os.path.join(HERE, "emc-expression-panels.json")
DEPMAP = os.path.join(HERE, "depmap-sarcoma-dependency.json")
GRADING = os.path.join(HERE, "census-route-expression-grading.json")
MOTIF = os.path.join(HERE, "emc-prmt5-substrate-motif-map.json")
SOURCES = (PANEL, DEPMAP, GRADING, MOTIF)

P6244 = "GSE24369_series_matrix.txt.gz"
P3290 = "GSE4303-GPL3290_series_matrix.txt.gz"
PLATS = ((P6244, "GSE24369 / GPL6244", "single-channel intensity"),
         (P3290, "GSE4303 / GPL3290", "two-colour log-ratio"))

METHYLOSOME = ("PRMT5", "WDR77", "RIOK1", "CLNS1A")
LOCUS = ("MTAP", "CDKN2A", "CDKN2B")
SALVAGE = ("MAT2A", "AHCY", "MTR", "ADI1")

C_EMC = "#b5385a"
C_COMP = "#6b7d8f"
C_INK = "#1f2a33"
C_MUTE = "#6b7d8f"
C_ABSENT = "#c8b06a"


def _load(p):
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def _fingerprint():
    out = {}
    for p in SOURCES:
        if os.path.exists(p):
            with open(p, "rb") as fh:
                out[os.path.basename(p)] = hashlib.sha256(fh.read()).hexdigest()[:16]
    return out


#: ⛔ AUTHOR AT THE FINAL PRINTED SIZE, AND FLOOR THE TYPE (2026-08-10). These figures were drawn on
#: canvases up to 9.6 in wide with 6.4 pt type. A journal scales a figure to its page width, so a
#: 9.4 in figure on a 7.5 in page is multiplied by 0.80 and that 6.4 pt type prints at 5.1 pt —
#: under the ~7 pt minimum these journals state, and genuinely hard to read. Matplotlib font sizes
#: are absolute points, so narrowing the canvas raises type size relative to the plot rather than
#: shrinking it with the canvas: authoring at the page width means what is drawn is what prints.
PAGE_W_IN = 7.4          # a full double-column page, with margin to spare
MIN_PT = 7.0


def fs(pt):
    """Font size floored at the smallest type a journal will accept."""
    return max(MIN_PT, pt)


def page(w, h):
    """Clamp a figure to the page width, preserving aspect."""
    if w <= PAGE_W_IN:
        return (w, h)
    return (PAGE_W_IN, h * PAGE_W_IN / w)


def _samples(panel, gene, plat):
    """(emc_z, comparator_z, readable). ⚠ A sample with no value is DROPPED, never zero-filled."""
    v = (panel["gene_reads"].get(gene) or {}).get(plat)
    if not isinstance(v, dict) or not v.get("readable"):
        return [], [], False
    emc, comp = [], []
    for s in v["per_sample"]:
        z = s.get("z_vs_array")
        if z is None:
            continue
        (emc if s["class"] == "EMC" else comp).append(z)
    return emc, comp, True


#: ⛔ SHAPE AND FILL CARRY THE SERIES, NOT HUE (2026-08-10). The two series were both filled circles
#: separated only by colour, and their luminances are 97 and 122 of 255 — about a tenth of the range
#: apart. Printed greyscale, or read by a colour-blind reviewer, the figure lost its only distinction.
#: Wiley journals can also levy a colour charge, and the $0 route this programme requires means a
#: figure must survive being printed in greyscale. Now EMC is a filled circle and the comparator an
#: OPEN square, so the colour is decoration and the shape is the data.
MARK = {"emc": {"marker": "o", "fill": True}, "comp": {"marker": "s", "fill": False}}


def _dots(ax, x, vals, colour, jitter=0.085, series="emc"):
    """Deterministic spread — no RNG, because a figure must redraw identically."""
    n = len(vals)
    m = MARK[series]
    for i, v in enumerate(sorted(vals)):
        off = 0.0 if n == 1 else (i / (n - 1) - 0.5) * 2 * jitter
        if m["fill"]:
            ax.plot(x + off, v, m["marker"], ms=4.6, color=colour,
                    mec="white", mew=0.6, zorder=3)
        else:
            ax.plot(x + off, v, m["marker"], ms=4.4, mfc="none", mec=colour, mew=1.25, zorder=3)


def _gene_panel(ax, panel, genes, title, plat, label):
    ax.axhline(0, color="#c9d2da", lw=0.9, zorder=1)
    for i, g in enumerate(genes):
        emc, comp, ok = _samples(panel, g, plat)
        if not ok:
            ax.text(i, 0, "no probe\n(unreadable)", ha="center", va="center", fontsize=fs(6.4),
                    color=C_ABSENT, style="italic", zorder=4)
            continue
        _dots(ax, i - 0.17, comp, C_COMP, series="comp")
        _dots(ax, i + 0.17, emc, C_EMC, series="emc")
        if emc:
            ax.plot([i + 0.03, i + 0.31], [st.median(emc)] * 2, "-", color=C_EMC, lw=1.9, zorder=4)
        if comp:
            ax.plot([i - 0.31, i - 0.03], [st.median(comp)] * 2, "--", color=C_COMP,
                    lw=1.9, zorder=4)
    ax.set_xticks(range(len(genes)))
    ax.set_xticklabels(genes, fontsize=fs(7.4))
    ax.set_title(title, fontsize=fs(8.2), color=C_INK, pad=5)
    ax.set_ylabel(f"z vs this array's own\nprobe distribution\n({label})", fontsize=fs(6.9))
    ax.tick_params(labelsize=fs(6.9))
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)


def fig_readings(plt, panel):
    """1 — the two readings, per tumour, platforms never sharing an axis."""
    fig, axes = plt.subplots(2, 2, figsize=page(9.4, 6.4))
    for r, (plat, pname, kind) in enumerate(PLATS):
        _gene_panel(axes[r][0], panel, METHYLOSOME, f"PRMT5 methylosome — {pname}", plat, kind)
        _gene_panel(axes[r][1], panel, LOCUS, f"MTAP / CDKN2A / CDKN2B locus — {pname}", plat, kind)
    axes[0][0].plot([], [], "o", color=C_EMC, mec="white", mew=0.6, label="EMC tumour")
    axes[0][0].plot([], [], "s", mfc="none", mec=C_COMP, mew=1.25, label="comparator sarcoma")
    axes[0][0].legend(fontsize=fs(6.6), frameon=False, loc="lower right", handletextpad=0.5)
    fig.suptitle("Every tumour, on both platforms. Bars are medians.", fontsize=fs(9), color=C_INK)
    fig.text(0.5, 0.005,
             "NOTE  The two platforms are NOT on a shared axis: one is single-channel intensity and one "
             "is a two-colour log-ratio.\nA gene with no probe is marked unreadable — that is an "
             "instrument statement, never evidence of absence.",
             ha="center", fontsize=fs(6.6), color=C_MUTE)
    fig.tight_layout(rect=(0, 0.035, 1, 0.955))
    return fig


def fig_locus_genewise(plt, panel):
    """2 — the locus gene by gene, because the paper's own caveat lives between these three genes."""
    fig, axes = plt.subplots(1, 2, figsize=page(8.6, 3.5))
    for c, (plat, pname, kind) in enumerate(PLATS):
        _gene_panel(axes[c], panel, LOCUS, pname, plat, kind)
    fig.suptitle("The locus is three genes, and they are not interchangeable", fontsize=fs(9), color=C_INK)
    fig.text(0.5, 0.005,
             "NOTE  CDKN2A is lost by mechanisms that leave MTAP intact, so a LOCUS score is ambiguous by "
             "construction — the group\ncannot distinguish co-deletion from CDKN2A-only loss. Only "
             "MTAP protein can, which is why the manuscript's decisive\ntest for this route is a "
             "stain and not this figure.",
             ha="center", fontsize=fs(6.6), color=C_MUTE)
    fig.tight_layout(rect=(0, 0.06, 1, 0.93))
    return fig


def fig_dependency(plt, dep):
    """3 — ⛔ THE FIGURE THAT ARGUES AGAINST THE PAPER'S OWN PROLIFERATION READING."""
    rows = {}
    for grp in dep["genes_by_group"].values():
        for r in grp:
            if r["gene"] in ("PRMT5", "MAT2A", "MTAP"):
                rows[r["gene"]] = r
    if not rows:
        return None
    order = [g for g in ("PRMT5", "MAT2A", "MTAP") if g in rows]
    fig, ax = plt.subplots(figsize=page(6.4, 3.3))
    fr = [rows[g]["sarcoma_frac_dependent"] * 100 for g in order]
    bars = ax.barh(order, fr, color=[C_EMC if f > 50 else C_COMP for f in fr], height=0.5)
    for g, b, f in zip(order, bars, fr):
        ax.text(b.get_width() + 1.6, b.get_y() + b.get_height() / 2,
                f"{f:.1f}%   (mean gene effect {rows[g]['sarcoma_mean']:+.2f})",
                va="center", fontsize=fs(7.2), color=C_INK)
    ax.set_xlim(0, 128)
    # ⛔ THE DENOMINATOR IS THE SCREENED COUNT, NOT THE MODEL COUNT (2026-08-10). This label read
    # `n_sarcoma_models`, which is 176 — the number of sarcoma models in the release — while the
    # percentages plotted above it are computed over the 91 that actually carry CRISPR gene-effect
    # data. The manuscript had already caught that exact error, corrected it in four places
    # including the abstract, and registered it in its appendix; the FIGURE still carried the
    # superseded number, so the paper contradicted its own correction in the one place a reader
    # looks first. Found by rendering the figure and reading the axis.
    # `n_sarcoma` sits on every per-gene row under `genes_by_group`, never at the top level, so it
    # is read from the rows and asserted unanimous rather than taken from the first one found.
    _ns = {r["n_sarcoma"] for grp in dep.get("genes_by_group", {}).values() for r in grp
           if isinstance(r, dict) and r.get("n_sarcoma")}
    assert len(_ns) == 1, f"screened-count disagreement across rows: {sorted(_ns)}"
    n_screened = _ns.pop()
    ax.set_xlabel(f"% of {n_screened or '?'} screened sarcoma cell lines in which the gene is a "
                  f"dependency", fontsize=fs(7.4))
    ax.set_title("This QUALIFIES the route rather than supporting it", fontsize=fs(8.6), color=C_INK)
    ax.tick_params(labelsize=fs(7.6))
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    fig.text(0.5, 0.005,
             "PRMT5 and MAT2A are dependencies in almost every sarcoma line, so a GROWTH effect on "
             "silencing them is close to expected\nand is not specific to this disease. Only an "
             "effect on FUSION-DRIVEN TRANSCRIPTION would be. MTAP is not a dependency, exactly as a\n"
             "biomarker rather than a target should read.  NO EMC LINE EXISTS IN THIS PANEL - every "
             "value is a transfer from other sarcomas.",
             ha="center", fontsize=fs(6.5), color=C_MUTE)
    fig.tight_layout(rect=(0, 0.11, 1, 1))
    return fig


def _class_z(panel, genes, plat):
    rows = {}
    for g in genes:
        v = (panel["gene_reads"].get(g) or {}).get(plat)
        if not isinstance(v, dict) or not v.get("readable"):
            continue
        for s in v["per_sample"]:
            z = s.get("z_vs_array")
            if z is not None:
                rows.setdefault(s["class"], []).append(z)
    return rows


def _class_ax(ax, rows, title, ylab):
    order = sorted(rows, key=lambda k: -st.median(rows[k]))
    for i, k in enumerate(order):
        col = C_EMC if k == "EMC" else C_COMP
        _dots(ax, i, rows[k], col, jitter=0.17)
        ax.plot([i - 0.26, i + 0.26], [st.median(rows[k])] * 2, "-", color=col, lw=2.2, zorder=4)
    ax.set_xticks(range(len(order)))
    ax.set_xticklabels([f"{k}\n(n={len(rows[k])})" for k in order], fontsize=fs(6.6))
    ax.set_ylabel(ylab, fontsize=fs(7.0))
    ax.set_title(title, fontsize=fs(8.2), color=C_INK, pad=5)
    ax.tick_params(labelsize=fs(6.8))
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    return order


def fig_classes(plt, panel):
    """4 — pooled group vs the single gene, because the GROUP DILUTES THE SIGNAL rather than making it.

    ⭐ THIS PANEL PAIR IS THE FINDING, AND IT WAS NOT THE ONE THE FIGURE WAS BUILT FOR. Pooled across
    the four methylosome genes EMC ranks SECOND, below desmoid fibromatosis — the group does not
    separate this disease at all. PRMT5 alone, which is the gene route 1 actually depends on, is
    clearly highest. The three other members are flat or lower in EMC and dilute it.
    ⚠ Which is figure 2's lesson running the other way: there a group INVENTED a signal its key gene
    did not have; here a group HID one its key gene does have. Neither is visible without the cut.
    """
    pooled = _class_z(panel, METHYLOSOME, P6244)
    single = _class_z(panel, ("PRMT5",), P6244)
    if not pooled or not single:
        return None
    fig, axes = plt.subplots(1, 2, figsize=page(9.6, 3.7))
    _class_ax(axes[0], pooled, "Methylosome POOLED (4 genes) - EMC ranks second",
              "z vs array, 4 genes pooled")
    _class_ax(axes[1], single, "PRMT5 ALONE - EMC is highest", "z vs array, PRMT5")
    fig.suptitle("GSE24369 / GPL6244 - each comparator class separately", fontsize=fs(9), color=C_INK)
    fig.text(0.5, 0.005,
             "NOTE  LGFMS is FUS::CREB3L2 - a FET-fusion sarcoma, and therefore a control for 'this is "
             "just what a fusion sarcoma looks like'.\nPooled, EMC does not separate from desmoid "
             "fibromatosis; PRMT5 alone does. Route 1 depends on PRMT5, not on the group.\n"
             "Left-panel points are gene-by-sample values pooled across four genes, so they are not "
             "independent observations and no test is run on them.",
             ha="center", fontsize=fs(6.4), color=C_MUTE)
    fig.tight_layout(rect=(0, 0.115, 1, 0.93))
    return fig


def fig_motif_map(plt, motif):
    """⭐ FIGURE 5 — where PRMT5's motif sits in EWSR1, and where each fusion cuts.

    The only panel in this set that is not an expression reading. It is drawn because the sentence
    it replaces — "the fusion keeps the half without the motif, except for the part that depends on
    the breakpoint" — is unreadable as prose and obvious as a ruler.

    ⛔ THE FIGURE MUST CARRY ITS OWN REFUTATION. EWSR1::FLI1 cuts at 264 and keeps no site, and
    that is the fusion in which a PRMT5 requirement was actually shown to be fusion-dependent. It is
    plotted alongside the others, in the same style, with that fact in the caption strip — a version
    of this figure showing only the EMC and clear cell breakpoints would read as a response
    predictor, which is exactly what it is not.
    """
    if not motif:
        return None
    wt = motif["wild_type_proteins"]["EWSR1"]
    sites = wt["positions"]["GRG"]
    length = wt["length_aa"]
    boxes = (motif["⭐_the_headline"].get("rgg_boxes_from_the_census") or [])

    rows = []
    for f in motif["fusion_constructs"]:
        if f["five_prime_partner"] != "EWSR1":
            continue
        rows.append((f["label"].split("—")[0].strip().replace("EWSR1::NR4A3", "EWSR1::NR4A3"),
                     f["last_five_prime_residue_retained"],
                     f["five_prime_motif_sites_retained"]["GRG"], True))
    for c in motif["measured_comparator_fusions_on_the_same_ruler"]:
        name = (c["comparator"] or "").split("—")[0].strip()
        if "reported type" in name:
            continue
        rows.append((name, c["five_prime_residues_retained"],
                     c["five_prime_motif_sites_retained"]["GRG"], False))

    fig, ax = plt.subplots(figsize=page(7.6, 0.52 * len(rows) + 2.5))
    # the protein, drawn once at the top
    y0 = len(rows) + 0.6
    ax.plot([1, length], [y0, y0], "-", color="#c9d2da", lw=7, solid_capstyle="butt", zorder=1)
    for b in boxes:
        ax.plot([b["start"], b["end"]], [y0, y0], "-", color="#8fa5b8", lw=7,
                solid_capstyle="butt", zorder=2)
    for p in sites:
        ax.plot(p, y0, "|", color=C_EMC, ms=13, mew=1.5, zorder=4)
    ax.text(1, y0 + 0.52, f"EWSR1, {length} aa — {len(sites)} GRG sites (red), first at "
                          f"{sites[0]}; RGG-rich regions shaded",
            fontsize=fs(7.0), color=C_INK, va="bottom")
    ax.text(150, y0 - 0.55, "no GRG site in residues 1-300\n(the segment every fusion retains)",
            fontsize=fs(6.6), color=C_MUTE, ha="center", va="top", style="italic")

    for i, (name, cut, kept, is_emc) in enumerate(rows):
        y = len(rows) - 1 - i
        col = C_EMC if is_emc else C_MUTE
        ax.plot([1, cut], [y, y], "-", color=col, lw=4.5, alpha=0.85,
                solid_capstyle="butt", zorder=2)
        ax.plot([cut, length], [y, y], "-", color="#e4e9ee", lw=4.5, solid_capstyle="butt",
                zorder=1)
        for p in sites:
            if p <= cut:
                ax.plot(p, y, "|", color="#7a1f34", ms=10, mew=1.4, zorder=4)
        ax.text(length + 12, y, f"{kept} kept", fontsize=fs(7.0), va="center", color=C_INK)
        ax.text(-14, y, name, fontsize=fs(7.0), ha="right", va="center",
                color=C_INK if is_emc else C_MUTE)
    ax.text(-14, y0, "wild type", fontsize=fs(7.0), ha="right", va="center", color=C_INK)

    ax.set_xlim(-8, length + 78)
    ax.set_ylim(-2.4, y0 + 1.5)
    ax.set_yticks([])
    ax.set_xticks([1, 100, 200, 300, 400, 500, 600, length])
    ax.tick_params(labelsize=fs(6.9))
    ax.set_xlabel("EWSR1 residue", fontsize=fs(7.4))
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.text(-14, -1.75,
            "NOTE: EWSR1::FLI1 keeps 0 sites and PRMT5 inhibition is still fusion-dependent there.\n"
            "The motif is NOT required, and this figure is not a response predictor.",
            fontsize=fs(6.5), color="#7a1f34", ha="left", va="top")
    fig.tight_layout()
    return fig


def build():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.family": "DejaVu Sans", "figure.facecolor": "white",
                         "axes.facecolor": "white", "savefig.facecolor": "white",
                         "axes.edgecolor": "#9aa7b4", "text.color": C_INK,
                         "axes.labelcolor": C_INK, "xtick.color": C_MUTE, "ytick.color": C_MUTE})
    panel, dep = _load(PANEL), _load(DEPMAP)
    motif = _load(MOTIF) if os.path.exists(MOTIF) else None
    figs = {
        "mtap-prmt5-fig1-readings": fig_readings(plt, panel),
        "mtap-prmt5-fig2-locus-genewise": fig_locus_genewise(plt, panel),
        "mtap-prmt5-fig3-dependency-qualifier": fig_dependency(plt, dep),
        "mtap-prmt5-fig4-comparator-classes": fig_classes(plt, panel),
        "mtap-prmt5-fig5-motif-map": fig_motif_map(plt, motif),
    }
    os.makedirs(FIGDIR, exist_ok=True)
    written = []
    for name, fig in figs.items():
        if fig is None:
            print(f"  skipped (inputs absent): {name}", file=sys.stderr)
            continue
        for ext in ("png", "pdf"):
            p = os.path.join(FIGDIR, f"{name}.{ext}")
            fig.savefig(p, dpi=300 if ext == "png" else None, bbox_inches="tight")
            written.append(os.path.basename(p))
        plt.close(fig)
    with open(STAMP, "w", encoding="utf-8") as fh:
        json.dump({"_what": "content hashes of every artifact these figures were drawn from",
                   "_why": "a reader cannot otherwise tell a stale figure from a current one; "
                           "--check compares these against the artifacts",
                   "_regenerate": "python3 research/modalities/emc_mtap_prmt5_figures.py",
                   "sources": _fingerprint(), "figures": sorted(written)}, fh, indent=1,
                  sort_keys=True)
        fh.write("\n")
    return written


def check():
    if not os.path.exists(STAMP):
        print("mtap-prmt5 figures --check: no provenance stamp; run the generator")
        return 1
    stamped = _load(STAMP).get("sources", {})
    now = _fingerprint()
    bad = [k for k in stamped if stamped[k] != now.get(k)]
    for k in bad:
        print(f"mtap-prmt5 figures --check: DRIFT {k}: stamped {stamped[k]}, now {now.get(k)}")
    if bad:
        print("Re-run: python3 research/modalities/emc_mtap_prmt5_figures.py")
        return 1
    print(f"mtap-prmt5 figures --check: OK — {len(_load(STAMP).get('figures', []))} files match "
          f"{len(stamped)} committed artifacts")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args(argv)
    if args.check:
        return check()
    for f in build():
        print(f"  wrote {f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
