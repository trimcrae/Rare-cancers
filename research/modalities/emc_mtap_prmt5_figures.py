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
SOURCES = (PANEL, DEPMAP, GRADING)

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


def _dots(ax, x, vals, colour, jitter=0.085):
    """Deterministic spread — no RNG, because a figure must redraw identically."""
    n = len(vals)
    for i, v in enumerate(sorted(vals)):
        off = 0.0 if n == 1 else (i / (n - 1) - 0.5) * 2 * jitter
        ax.plot(x + off, v, "o", ms=4.6, color=colour, mec="white", mew=0.6, zorder=3)


def _gene_panel(ax, panel, genes, title, plat, label):
    ax.axhline(0, color="#c9d2da", lw=0.9, zorder=1)
    for i, g in enumerate(genes):
        emc, comp, ok = _samples(panel, g, plat)
        if not ok:
            ax.text(i, 0, "no probe\n(unreadable)", ha="center", va="center", fontsize=6.4,
                    color=C_ABSENT, style="italic", zorder=4)
            continue
        _dots(ax, i - 0.17, comp, C_COMP)
        _dots(ax, i + 0.17, emc, C_EMC)
        if emc:
            ax.plot([i + 0.03, i + 0.31], [st.median(emc)] * 2, "-", color=C_EMC, lw=1.9, zorder=4)
        if comp:
            ax.plot([i - 0.31, i - 0.03], [st.median(comp)] * 2, "-", color=C_COMP, lw=1.9, zorder=4)
    ax.set_xticks(range(len(genes)))
    ax.set_xticklabels(genes, fontsize=7.4)
    ax.set_title(title, fontsize=8.2, color=C_INK, pad=5)
    ax.set_ylabel(f"z vs this array's own\nprobe distribution\n({label})", fontsize=6.9)
    ax.tick_params(labelsize=6.9)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)


def fig_readings(plt, panel):
    """1 — the two readings, per tumour, platforms never sharing an axis."""
    fig, axes = plt.subplots(2, 2, figsize=(9.4, 6.4))
    for r, (plat, pname, kind) in enumerate(PLATS):
        _gene_panel(axes[r][0], panel, METHYLOSOME, f"PRMT5 methylosome — {pname}", plat, kind)
        _gene_panel(axes[r][1], panel, LOCUS, f"MTAP / CDKN2A / CDKN2B locus — {pname}", plat, kind)
    axes[0][0].plot([], [], "o", color=C_EMC, label="EMC tumour")
    axes[0][0].plot([], [], "o", color=C_COMP, label="comparator sarcoma")
    axes[0][0].legend(fontsize=6.6, frameon=False, loc="upper left")
    fig.suptitle("Every tumour, on both platforms. Bars are medians.", fontsize=9, color=C_INK)
    fig.text(0.5, 0.005,
             "NOTE  The two platforms are NOT on a shared axis: one is single-channel intensity and one "
             "is a two-colour log-ratio.\nA gene with no probe is marked unreadable — that is an "
             "instrument statement, never evidence of absence.",
             ha="center", fontsize=6.6, color=C_MUTE)
    fig.tight_layout(rect=(0, 0.035, 1, 0.955))
    return fig


def fig_locus_genewise(plt, panel):
    """2 — the locus gene by gene, because the paper's own caveat lives between these three genes."""
    fig, axes = plt.subplots(1, 2, figsize=(8.6, 3.5))
    for c, (plat, pname, kind) in enumerate(PLATS):
        _gene_panel(axes[c], panel, LOCUS, pname, plat, kind)
    fig.suptitle("The locus is three genes, and they are not interchangeable", fontsize=9, color=C_INK)
    fig.text(0.5, 0.005,
             "NOTE  CDKN2A is lost by mechanisms that leave MTAP intact, so a LOCUS score is ambiguous by "
             "construction — the group\ncannot distinguish co-deletion from CDKN2A-only loss. Only "
             "MTAP protein can, which is why the manuscript's decisive\ntest for this route is a "
             "stain and not this figure.",
             ha="center", fontsize=6.6, color=C_MUTE)
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
    fig, ax = plt.subplots(figsize=(6.4, 3.3))
    fr = [rows[g]["sarcoma_frac_dependent"] * 100 for g in order]
    bars = ax.barh(order, fr, color=[C_EMC if f > 50 else C_COMP for f in fr], height=0.5)
    for g, b, f in zip(order, bars, fr):
        ax.text(b.get_width() + 1.6, b.get_y() + b.get_height() / 2,
                f"{f:.1f}%   (mean gene effect {rows[g]['sarcoma_mean']:+.2f})",
                va="center", fontsize=7.2, color=C_INK)
    ax.set_xlim(0, 128)
    ax.set_xlabel(f"% of {dep.get('n_sarcoma_models', '?')} sarcoma cell lines in which the gene is a "
                  f"dependency", fontsize=7.4)
    ax.set_title("This QUALIFIES the route rather than supporting it", fontsize=8.6, color=C_INK)
    ax.tick_params(labelsize=7.6)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    fig.text(0.5, 0.005,
             "PRMT5 and MAT2A are dependencies in almost every sarcoma line, so a GROWTH effect on "
             "silencing them is close to expected\nand is not specific to this disease. Only an "
             "effect on FUSION-DRIVEN TRANSCRIPTION would be. MTAP is not a dependency, exactly as a\n"
             "biomarker rather than a target should read.  NO EMC LINE EXISTS IN THIS PANEL - every "
             "value is a transfer from other sarcomas.",
             ha="center", fontsize=6.5, color=C_MUTE)
    fig.tight_layout(rect=(0, 0.11, 1, 1))
    return fig


def fig_classes(plt, panel):
    """4 — the methylosome against EACH comparator class; a pooled arm hides a FET-fusion control."""
    rows = {}
    v = (panel["gene_reads"].get("PRMT5") or {}).get(P6244)
    if not isinstance(v, dict) or not v.get("readable"):
        return None
    for g in METHYLOSOME:
        vv = (panel["gene_reads"].get(g) or {}).get(P6244)
        if not isinstance(vv, dict) or not vv.get("readable"):
            continue
        for s in vv["per_sample"]:
            z = s.get("z_vs_array")
            if z is not None:
                rows.setdefault(s["class"], []).append(z)
    if not rows:
        return None
    order = sorted(rows, key=lambda k: -st.median(rows[k]))
    fig, ax = plt.subplots(figsize=(7.0, 3.4))
    for i, k in enumerate(order):
        col = C_EMC if k == "EMC" else C_COMP
        _dots(ax, i, rows[k], col, jitter=0.17)
        ax.plot([i - 0.24, i + 0.24], [st.median(rows[k])] * 2, "-", color=col, lw=2.1, zorder=4)
    ax.axhline(0, color="#c9d2da", lw=0.9)
    ax.set_xticks(range(len(order)))
    ax.set_xticklabels([f"{k}\n(n={len(rows[k])})" for k in order], fontsize=7.0)
    ax.set_ylabel("z vs array, methylosome genes pooled", fontsize=7.2)
    ax.set_title("The methylosome against each comparator class separately — GSE24369 / GPL6244",
                 fontsize=8.4, color=C_INK)
    ax.tick_params(labelsize=7.0)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    fig.text(0.5, 0.005,
             "NOTE  LGFMS is FUS::CREB3L2 - a FET-fusion sarcoma, and therefore a control for 'this is "
             "just what a fusion sarcoma looks like'.\nA pooled comparator arm makes that control "
             "invisible.  ⚠ Points are gene-by-sample values pooled across the four methylosome "
             "genes,\nso they are not independent observations and no test is run on them here.",
             ha="center", fontsize=6.5, color=C_MUTE)
    fig.tight_layout(rect=(0, 0.10, 1, 1))
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
    figs = {
        "mtap-prmt5-fig1-readings": fig_readings(plt, panel),
        "mtap-prmt5-fig2-locus-genewise": fig_locus_genewise(plt, panel),
        "mtap-prmt5-fig3-dependency-qualifier": fig_dependency(plt, dep),
        "mtap-prmt5-fig4-comparator-classes": fig_classes(plt, panel),
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
