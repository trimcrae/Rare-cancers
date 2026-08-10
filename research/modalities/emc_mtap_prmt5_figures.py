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
#: added 2026-08-10. Figure 4 drew only the samples the panel's arms contain, so a deposited class
#: the sample classifier had no pattern for was invisible in a figure whose whole subject is the
#: comparison BETWEEN classes. `emc-prmt5-multiplicity.json` carries per-sample z for exactly those
#: samples, beside the record of why they were excluded.
MULTI = os.path.join(HERE, "emc-prmt5-multiplicity.json")
#: added 2026-08-10 with the rebuilt figure 2. `emc-mtap-locus-persample.json` carries the
#: per-tumour 9p21 reading and the MTAP/CDKN2A conjunction that discriminates a co-deletion from a
#: low MTAP transcript with an intact locus, which is the manuscript's central negative and which
#: no group statistic can display.
LOCUS_PS = os.path.join(HERE, "emc-mtap-locus-persample.json")
SOURCES = (PANEL, DEPMAP, GRADING, MOTIF, MULTI, LOCUS_PS)

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
MARK = {"emc": {"marker": "o", "fill": True}, "comp": {"marker": "s", "fill": False},
        # a filled triangle for pooled normal tissue: a third shape, so the class survives
        # greyscale beside the open squares of the comparator tumours.
        "normal": {"marker": "^", "fill": True}}


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
    # ⛔ "EVERY TUMOUR" WAS FALSE AND THE FIGURE IS WHERE A READER MEETS IT FIRST (2026-08-10).
    # GSE24369 deposits 40 tumours and this figure draws the 35 in the panel's arms; the five
    # solitary fibrous tumours the classifier had no pattern for appear only in figure 4. The same
    # defect was registered and corrected for figure 4 in the previous revision and was not carried
    # across to the figure making the stronger claim.
    fig.suptitle("Every tumour in the analysed arms, on both platforms. Bars are medians.",
                 fontsize=fs(9), color=C_INK)
    fig.text(0.5, 0.005,
             "The two platforms are not on a shared axis: one is single-channel intensity, the other a "
             "two-colour log-ratio.\nA gene with no probe is marked unreadable, which reflects the "
             "instrument rather than the absence of expression.\nFive deposited solitary fibrous "
             "tumours are not in the analysed arms and are drawn in figure 4.",
             ha="center", fontsize=fs(6.6), color=C_MUTE)
    fig.tight_layout(rect=(0, 0.05, 1, 0.955))
    return fig


def fig_locus_genewise(plt, panel, locus_ps):
    """2 — the locus per tumour, and the MTAP/CDKN2A conjunction that decides the 9p21 question.

    ⛔ THIS FIGURE USED TO BE FIGURE 1'S RIGHT COLUMN WITH A DIFFERENT CAPTION. Both panels called
    `_gene_panel(..., LOCUS, ...)` on the same panel object for the same two platforms, so the two
    figures were identical point for point and only the title differed. It was rebuilt rather than
    deleted, because the manuscript's central negative is a PER-SAMPLE argument that no group
    statistic and no per-gene summary can display: five EMC tumours on GPL3290 sit below every
    comparator for MTAP, and the question that decides whether they carry a 9p21 homozygous
    deletion is what CDKN2A does in those same five. The right panel is the only place a reader
    can see that it does the opposite of co-deletion.
    """
    if not locus_ps:
        return None
    rec = (locus_ps.get("per_platform") or {}).get(P3290)
    if not rec:
        return None
    fig, axes = plt.subplots(1, 2, figsize=page(7.4, 3.4),
                             gridspec_kw={"width_ratios": [1.35, 1.0]})

    # left — the three genes per tumour on the platform where all three are readable
    _gene_panel(axes[0], panel, LOCUS, "GPL6244, per tumour", P6244, "GPL6244, intensity")
    axes[0].plot([], [], "o", color=C_EMC, mec="white", mew=0.6, label="EMC tumour")
    axes[0].plot([], [], "s", mfc="none", mec=C_COMP, mew=1.25, label="comparator sarcoma")
    axes[0].legend(fontsize=fs(6.6), frameon=False, loc="lower left", handletextpad=0.5)

    # right — MTAP against CDKN2A, per tumour, on the platform with the low MTAP tail
    mt = rec["locus_genes"]["MTAP"]["per_sample"]
    cd = {r["gsm"]: r for r in rec["locus_genes"]["CDKN2A"]["per_sample"]}
    cand = {c["gsm"] for c in rec["mtap_low_candidates"]["candidates"]}
    floor = rec["mtap_low_candidates"]["lowest_comparator_MTAP_array_percentile"] * 100
    ax = axes[1]
    ax.axvline(floor, color="#9aa7b4", lw=0.9, ls=":", zorder=1)
    ax.axhline(25, color="#9aa7b4", lw=0.9, ls=":", zorder=1)
    for r in mt:
        c = cd.get(r["gsm"])
        if not c:
            continue
        x, y = r["array_percentile"] * 100, c["array_percentile"] * 100
        if r["class"] == "EMC":
            ax.plot(x, y, "o", ms=5.4 if r["gsm"] in cand else 4.6, color=C_EMC,
                    mec="white", mew=0.6, zorder=4)
        else:
            ax.plot(x, y, "s", ms=4.4, mfc="none", mec=C_COMP, mew=1.25, zorder=3)
    ax.set_xlim(-3, 100)
    ax.set_ylim(0, 100)
    ax.set_xlabel("MTAP, percentile of its own array", fontsize=fs(7.0))
    ax.set_ylabel("CDKN2A, percentile of its own array", fontsize=fs(7.0))
    ax.set_title("GPL3290, per tumour", fontsize=fs(8.2), color=C_INK, pad=5)
    ax.tick_params(labelsize=fs(6.9))
    ax.text(floor + 2, 97, "lowest comparator\nfor MTAP", fontsize=fs(6.2), color=C_MUTE,
            va="top", ha="left")
    ax.text(5, 20, "a co-deleted tumour\nwould fall in here", fontsize=fs(6.2), color=C_MUTE,
            va="top", ha="left", style="italic")
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)

    fig.suptitle("The 9p21 locus read per tumour", fontsize=fs(9), color=C_INK)
    fig.text(0.5, 0.005,
             "Filled circles are EMC tumours, open squares comparator sarcomas; bars in the left "
             "panel are medians, while the manuscript table reports differences of\nmeans, so the "
             "two need not agree in direction for a gene as flat as MTAP. Right: a homozygous 9p21 "
             "deletion removes MTAP and CDKN2A together, so a\ndeleted tumour would fall in the "
             "lower-left quadrant. Five EMC tumours sit below every comparator for MTAP and all "
             "five carry CDKN2A above their\narray median, which is the opposite of the "
             "co-deletion pattern. No tumour on either platform falls in that quadrant.",
             ha="center", fontsize=fs(6.2), color=C_MUTE)
    fig.tight_layout(rect=(0, 0.115, 1, 0.925))
    return fig


def _wilson(k, n, z=1.96):
    """Wilson score interval. A bar at 94.5% of 91 lines is not a point estimate and the figure
    should not draw it as one."""
    if not n:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    h = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5)
    return ((c - h) / d, (c + h) / d)


def fig_dependency(plt, dep):
    """3 — ⛔ THE FIGURE THAT ARGUES AGAINST THE PAPER'S OWN PROLIFERATION READING.

    ⛔ IT USED TO DRAW ONLY THE SARCOMA FRACTIONS WHILE ITS CAPTION MADE THE LOAD-BEARING POINT
    WITH THE NON-SARCOMA NUMBER, WHICH NO BAR CARRIED (2026-08-10). The comparison the section
    actually rests on is sarcoma against everything else — 94.5% versus 94.1% for PRMT5 — so both
    are drawn. The old title, "PRMT5 and MAT2A are pan-essential across sarcoma lines", also
    over-stated against the manuscript's own text, which uses MAT2A's selectivity of −0.285 as the
    contrast that makes PRMT5's +0.013 look like nothing; if MAT2A were pan-essential in the same
    sense that contrast would have no force. And the x-axis ran to 120% for a quantity bounded at
    100.
    """
    rows = {}
    for grp in dep["genes_by_group"].values():
        for r in grp:
            if r["gene"] in ("PRMT5", "MAT2A", "MTAP"):
                rows[r["gene"]] = r
    if not rows:
        return None
    order = [g for g in ("PRMT5", "MAT2A", "MTAP") if g in rows]
    fig, ax = plt.subplots(figsize=page(6.6, 3.4))
    ypos = list(range(len(order)))
    for i, g in enumerate(order):
        r = rows[g]
        n_s = r.get("n_sarcoma") or 0
        n_r = r.get("n_rest") or 0
        for j, (key, n, col, hatch, lab) in enumerate((
                ("sarcoma_frac_dependent", n_s, C_EMC, "", "sarcoma lines"),
                ("rest_frac_dependent", n_r, C_COMP, "///", "non-sarcoma lines"))):
            f = r.get(key)
            if f is None:
                continue
            y = i + (0.19 if j == 0 else -0.19)
            ax.barh(y, f * 100, color="white", edgecolor=col, hatch=hatch, height=0.32,
                    linewidth=1.0, zorder=2,
                    label=lab if i == 0 else None)
            lo, hi = _wilson(round(f * n), n)
            ax.plot([lo * 100, hi * 100], [y, y], "-", color=C_INK, lw=1.0, zorder=3)
            if hi * 100 > 70:
                ax.text(lo * 100 - 2, y, f"{f * 100:.1f}%", va="center", ha="right",
                        fontsize=fs(7.0), color=C_INK, zorder=5)
            else:
                ax.text(hi * 100 + 2, y, f"{f * 100:.1f}%", va="center", ha="left",
                        fontsize=fs(7.0), color=C_INK, zorder=5)
    ax.set_yticks(ypos)
    ax.set_yticklabels([f"{g}\n(gene effect {rows[g]['sarcoma_mean']:+.2f} in sarcoma)"
                        for g in order], fontsize=fs(7.0))
    ax.legend(fontsize=fs(6.8), frameon=False, loc="upper right")
    ax.set_xlim(0, 100)
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
    ax.set_xlabel(f"% of lines in which the gene is a dependency, with Wilson 95% intervals "
                  f"({n_screened or '?'} screened sarcoma lines)", fontsize=fs(7.2))
    ax.set_title("Dependency inside and outside sarcoma", fontsize=fs(8.6), color=C_INK)
    ax.tick_params(labelsize=fs(7.0))
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    fig.text(0.5, 0.005,
             "PRMT5 and MAT2A are dependencies in almost every sarcoma line and in almost every "
             "non-sarcoma line, so growth inhibition on silencing\nthem is expected and the panel "
             "supports no statement of tissue selectivity; only an effect on fusion-driven "
             "transcription would be specific\nto this disease. MTAP is not a dependency in either "
             "group, which is the profile of a biomarker rather than a target. No EMC line is "
             "present\nin this panel, so every value is inferred from other sarcomas.",
             ha="center", fontsize=fs(6.5), color=C_MUTE)
    fig.tight_layout(rect=(0, 0.135, 1, 1))
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


#: ⛔ ONE BUCKET NAME IS A SUBSTRING ARTEFACT AND THE FIGURE MUST NOT REPEAT IT (2026-08-10). The
#: six samples the classifier buckets `fibrosarcoma` are annotated `Myxofibrosarcoma` in GEO; the
#: bucket matches on the substring. Myxofibrosarcoma is a different entity, so the axis carries what
#: the deposit says the samples are. The bucket name stays in the artifact, which is a record of
#: what the classifier did.
CLASS_LABEL = {"fibrosarcoma": "myxofibrosarcoma",
               "desmoid_fibromatosis": "desmoid fibromatosis",
               "solitary_fibrous_tumour": "solitary fibrous tumour",
               "pooled_skeletal_muscle_RNA": "pooled normal muscle"}
NOT_A_COMPARATOR = "pooled_skeletal_muscle_RNA"


def _class_ax(ax, rows, title, ylab, n_genes=1):
    order = sorted(rows, key=lambda k: -st.median(rows[k]))
    for i, k in enumerate(order):
        col = C_EMC if k == "EMC" else C_ABSENT if k == NOT_A_COMPARATOR else C_COMP
        # ⛔ SHAPE, NOT HUE, FOR THE CLASS THE PAPER MOST NEEDS A READER TO SEE (2026-08-10). The
        # generator's own rule is that shape and fill carry the series so the figure survives
        # greyscale printing, and it was obeyed for EMC against comparator and broken for pooled
        # normal muscle, which was an open square in gold beside open squares in slate. In
        # greyscale the normal-tissue column became indistinguishable from a tumour comparator —
        # and it is the column that reads ABOVE EMC on PRMT5, which is the plainest statement in
        # the figure of what a within-array z does not show.
        series = ("emc" if k == "EMC" else "normal" if k == NOT_A_COMPARATOR else "comp")
        _dots(ax, i, rows[k], col, jitter=0.17, series=series)
        ax.plot([i - 0.26, i + 0.26], [st.median(rows[k])] * 2,
                ":" if k == NOT_A_COMPARATOR else "-", color=col, lw=2.2, zorder=4)
    ax.set_xticks(range(len(order)))
    # ⛔ THE AXIS REPORTED GENE-BY-SAMPLE COUNTS AS `n` (2026-08-10). In the pooled panel `rows[k]`
    # holds four genes times the class's samples, so the axis read "EMC (n=24)" for six tumours in
    # a paper whose entire evidence base is sixteen. The caption disclosed the pooling and never
    # said the n was not a tumour count. The label now states the tumour count and the gene
    # multiplier separately.
    def _lab(k):
        name = CLASS_LABEL.get(k, k)
        n_tum = len(rows[k]) // n_genes
        return f"{name}\n{n_tum} tumours" + (f" x {n_genes} genes" if n_genes > 1 else "")
    ax.set_xticklabels([_lab(k) for k in order],
                       fontsize=fs(6.4), rotation=28, ha="right", rotation_mode="anchor")
    ax.set_ylabel(ylab, fontsize=fs(7.0))
    ax.set_title(title, fontsize=fs(8.2), color=C_INK, pad=5)
    ax.tick_params(labelsize=fs(6.8))
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    return order


def _excluded_class_z(multi, genes):
    """The deposited samples the panel's arms leave out, keyed by class, from the exclusion record."""
    rows = {}
    if not multi:
        return rows
    rec = ((multi.get("per_platform") or {}).get(P6244) or {}).get("excluded_sample_z") or {}
    for s in (rec.get("samples") or {}).values():
        for g in genes:
            v = (s.get("z_vs_array") or {}).get(g)
            if v is not None:
                rows.setdefault(s["class"], []).append(v)
    return rows


def fig_classes(plt, panel, multi):
    """4 — pooled group vs the single gene, because the GROUP DILUTES THE SIGNAL rather than making it.

    ⭐ THIS PANEL PAIR IS THE FINDING, AND IT WAS NOT THE ONE THE FIGURE WAS BUILT FOR. Pooled across
    the four methylosome genes EMC does not come top — the group does not separate this disease at
    all. PRMT5 alone, which is the gene route 1 actually depends on, is highest of the tumour
    classes. The three other members are flat or lower in EMC and dilute it.
    ⚠ Which is figure 2's lesson running the other way: there a group INVENTED a signal its key gene
    did not have; here a group HID one its key gene does have. Neither is visible without the cut.

    ⛔ AND IT USED TO DRAW FOUR CLASSES WHERE THE DEPOSIT HAS SIX (2026-08-10). The panel artifact
    carries per-sample values only for the samples in an arm, so five solitary fibrous tumours the
    sample classifier had no pattern for, and two pooled skeletal-muscle references excluded by
    design, were absent from a figure whose entire subject is the comparison between classes. Both
    are drawn now, from `emc-prmt5-multiplicity.json`, with the normal-tissue column marked as not a
    comparator — and it reads HIGHER than EMC on PRMT5, which is a caveat about what a within-array
    z can show and belongs in the figure rather than in a footnote.
    """
    pooled = _class_z(panel, METHYLOSOME, P6244)
    single = _class_z(panel, ("PRMT5",), P6244)
    if not pooled or not single:
        return None
    for tgt, genes in ((pooled, METHYLOSOME), (single, ("PRMT5",))):
        for k, v in _excluded_class_z(multi, genes).items():
            tgt.setdefault(k, []).extend(v)
    fig, axes = plt.subplots(1, 2, figsize=page(9.6, 4.3))
    _class_ax(axes[0], pooled, "Methylosome pooled: EMC does not come top", "z vs array",
              n_genes=len(METHYLOSOME))
    _class_ax(axes[1], single, "PRMT5 alone: EMC has the highest class median", "z vs array")
    axes[1].plot([], [], "o", color=C_EMC, mec="white", mew=0.6, label="EMC tumour")
    axes[1].plot([], [], "s", mfc="none", mec=C_COMP, mew=1.25, label="comparator")
    axes[1].plot([], [], "^", color=C_ABSENT, mec="white", mew=0.6, label="normal tissue")
    axes[1].legend(fontsize=fs(6.4), frameon=False, loc="lower left", handletextpad=0.5)
    fig.suptitle("GSE24369 / GPL6244 - every deposited class separately", fontsize=fs(9),
                 color=C_INK)
    fig.text(0.5, 0.005,
             "LGFMS carries FUS::CREB3L2 and is therefore a within-class control for a FET-fusion "
             "sarcoma. Solitary fibrous tumour is drawn because it is\ndeposited in this series; it "
             "is not in the comparator arm, because the sample classifier carried no pattern for "
             "it. The two pooled skeletal-muscle\nreferences are normal tissue, are drawn as "
             "triangles, are not a comparator, and read above EMC on PRMT5. Pooled, EMC ranks "
             "third of five, below\ndesmoid fibromatosis and solitary fibrous tumour. On PRMT5 "
             "alone EMC has the highest class median, and 9 of 34 comparator tumours read at or "
             "above\nthe lowest EMC tumour. Left-panel points are gene-by-sample values pooled "
             "across four genes, so they are not independent observations and no test\nis run on "
             "them.",
             ha="center", fontsize=fs(6.2), color=C_MUTE)
    fig.tight_layout(rect=(0, 0.185, 1, 0.94))
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
    # ⛔ EVERY REPORTED JUNCTION, NOT THE CLEANEST ONE (2026-08-10). This loop used to skip any
    # comparator whose label says "reported type", which dropped two of the three reported
    # EWSR1::ATF1 junctions — and the dropped pair is exactly what makes the comparison honest:
    # one of them retains four sites like the commonest type, and the other retains none. A figure
    # that plots the single cleanest of three available comparisons is the failure this whole
    # paper is written against.
    for c in motif["measured_comparator_fusions_on_the_same_ruler"]:
        raw = (c["comparator"] or "")
        name = raw.split("—")[0].strip()
        exon = raw.split("—")[-1].strip() if "—" in raw else ""
        if "reported type" in name:
            name = name.replace("(clear cell, reported type)", "(clear cell, further reported)")
        rows.append((f"{name} {exon}".strip(), c["five_prime_residues_retained"],
                     c["five_prime_motif_sites_retained"]["GRG"], False))

    # ⛔ THE PLATEAU IS THE FINDING NOW, AND IT WEAKENS THE PAPER'S OWN EARLIER ARGUMENT
    # (2026-08-10). Four of the eleven sites sit inside twenty residues and the fifth is 143
    # residues later, so every breakpoint across that gap keeps exactly four. A figure that draws
    # two fusions with the same four ticks and does not draw the gap invites a reader to see a
    # correspondence between two diseases where there is only a step function. The band is shaded
    # and labelled with its width.
    plateau = (sites[3] + 1, sites[4] - 1)

    fig, ax = plt.subplots(figsize=page(7.4, 0.52 * len(rows) + 2.9))
    y0 = len(rows) + 0.6
    ax.axvspan(plateau[0], plateau[1], color="#eef1f4", zorder=0)
    ax.plot([1, length], [y0, y0], "-", color="#c9d2da", lw=7, solid_capstyle="butt", zorder=1)
    for b in boxes:
        ax.plot([b["start"], b["end"]], [y0, y0], "-", color="#8fa5b8", lw=7,
                solid_capstyle="butt", zorder=2)
    for p in sites:
        ax.plot(p, y0, "|", color=C_INK, ms=13, mew=1.6, zorder=4)
    ax.text(1, y0 + 0.52, f"EWSR1, {length} aa - {len(sites)} GRG sites (ticks), first at "
                          f"{sites[0]}; RGG-rich regions shaded darker",
            fontsize=fs(7.0), color=C_INK, va="bottom")
    ax.text(150, y0 - 0.55, "no GRG site in residues 1-300\n(the segment every fusion retains)",
            fontsize=fs(6.6), color=C_MUTE, ha="center", va="top", style="italic")

    # ⛔ SHAPE AND FILL PATTERN, NOT HUE (2026-08-10). EMC fusions were red bars and comparators
    # slate bars, with the GRG ticks drawn in red on both; printed greyscale the two series
    # collapsed together and the ticks vanished from the EMC rows, which carry the whole content of
    # the section. EMC rows are now solid and comparator rows hatched, and the ticks are drawn in
    # ink against both.
    for i, (name, cut, kept, is_emc) in enumerate(rows):
        y = len(rows) - 1 - i
        col = C_EMC if is_emc else C_MUTE
        ax.barh(y, cut - 1, left=1, height=0.34, color=col if is_emc else "white",
                edgecolor=col, hatch="" if is_emc else "////", linewidth=1.0, zorder=2)
        ax.plot([cut, length], [y, y], "-", color="#e4e9ee", lw=4.5, solid_capstyle="butt",
                zorder=1)
        for p in sites:
            if p <= cut:
                ax.plot(p, y, "|", color=C_INK, ms=10, mew=1.5, zorder=4)
        ax.text(length + 12, y, f"{kept} kept", fontsize=fs(7.0), va="center", color=C_INK)
        ax.text(-14, y, name, fontsize=fs(7.0), ha="right", va="center",
                color=C_INK if is_emc else C_MUTE)
    ax.text(-14, y0, "wild type", fontsize=fs(7.0), ha="right", va="center", color=C_INK)

    span = plateau[1] - plateau[0] + 1
    ax.text((plateau[0] + plateau[1]) / 2, -0.95,
            f"any breakpoint in residues {plateau[0]}-{plateau[1]} keeps exactly 4 sites\n"
            f"({span} residues, {span / length:.0%} of the protein)",
            fontsize=fs(6.5), color=C_INK, ha="center", va="top")

    ax.set_xlim(-8, length + 78)
    ax.set_ylim(-3.1, y0 + 1.5)
    ax.set_yticks([])
    ax.set_xticks([1, 100, 200, 300, 400, 500, 600, length])
    ax.tick_params(labelsize=fs(6.9))
    ax.set_xlabel("EWSR1 residue", fontsize=fs(7.4))
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.text(-14, -2.15,
            "Solid bars are EMC fusions, hatched bars comparator fusions. EWSR1::FLI1 retains no "
            "sites and PRMT5 inhibition is nonetheless\nfusion-dependent there, so the motif is not "
            "required and this figure is not a response predictor.",
            fontsize=fs(6.5), color=C_INK, ha="left", va="top")
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
    multi = _load(MULTI) if os.path.exists(MULTI) else None
    locus_ps = _load(LOCUS_PS) if os.path.exists(LOCUS_PS) else None
    figs = {
        "mtap-prmt5-fig1-readings": fig_readings(plt, panel),
        "mtap-prmt5-fig2-locus-genewise": fig_locus_genewise(plt, panel, locus_ps),
        "mtap-prmt5-fig3-dependency-qualifier": fig_dependency(plt, dep),
        "mtap-prmt5-fig4-comparator-classes": fig_classes(plt, panel, multi),
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
        json.dump({"_what": "content hashes of every artifact these figures were drawn from AND of "
                            "every image file written",
                   "_why": "a reader cannot otherwise tell a stale figure from a current one; "
                           "--check compares both sides",
                   "_regenerate": "python3 research/modalities/emc_mtap_prmt5_figures.py",
                   "sources": _fingerprint(),
                   "images": _image_fingerprint(written),
                   "figures": sorted(written)}, fh, indent=1, sort_keys=True)
        fh.write("\n")
    return written


def _image_fingerprint(names):
    """⛔ THE STAMP FINGERPRINTED THE ARTIFACTS AND NEVER THE IMAGES (2026-08-10), while the SI
    said `--check` made a stale figure detectable and the tool printed "N files match". Nothing was
    ever computed from a `.png` or `.pdf`, so a figure edited by hand, or left over from an earlier
    run of the generator against the same artifact, passed. Hashing the images is what makes the
    sentence true."""
    out = {}
    for n in sorted(names):
        # ⚠ PNG ONLY. Matplotlib writes a creation timestamp into every PDF, so two runs of the
        # same code on the same artifacts produce different PDF bytes and a hash of one would fail
        # on every regeneration. The Agg PNG writer is deterministic, which is what makes this
        # check worth having.
        if not n.endswith(".png"):
            continue
        p = os.path.join(FIGDIR, n)
        if os.path.exists(p):
            with open(p, "rb") as fh:
                out[n] = hashlib.sha256(fh.read()).hexdigest()[:16]
    return out


def check():
    if not os.path.exists(STAMP):
        print("mtap-prmt5 figures --check: no provenance stamp; run the generator")
        return 1
    stamp = _load(STAMP)
    stamped = stamp.get("sources", {})
    now = _fingerprint()
    bad = [f"artifact {k}: stamped {stamped[k]}, now {now.get(k)}"
           for k in stamped if stamped[k] != now.get(k)]
    stamped_img = stamp.get("images", {})
    now_img = _image_fingerprint(stamp.get("figures", []))
    bad += [f"image {k}: stamped {stamped_img[k]}, now {now_img.get(k, 'absent')}"
            for k in stamped_img if stamped_img[k] != now_img.get(k)]
    if not stamped_img:
        bad.append("the stamp carries no image hashes; re-run the generator")
    for b in bad:
        print(f"mtap-prmt5 figures --check: DRIFT {b}")
    if bad:
        print("Re-run: python3 research/modalities/emc_mtap_prmt5_figures.py")
        return 1
    # ⚠ PDFs embed a creation timestamp, so they are listed and not hashed: two runs of the same
    # code on the same artifacts produce different bytes. Only the PNGs are compared.
    print(f"mtap-prmt5 figures --check: OK — {len(stamped)} artifacts and {len(stamped_img)} "
          f"image file(s) match their stamped hashes")
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
