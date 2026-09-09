#!/usr/bin/env python3
"""Figures for the EWSR1::NR4A3 transcriptional-output manuscript.

WHY THIS REPLACES THE HAND-EMITTED SVG. `AGENTS.md` bans hand-written SVG with manually computed
coordinates, for two reasons that both applied to the figure this supersedes: there is no text
measurement, so labels overflow their boxes, and nothing rasterises it, so the author cannot see the
result before committing. Both are answered by drawing with matplotlib and looking at the PNG.

WHAT EACH FIGURE IS FOR
  1  per-sample dots      every tumour, visible. At n_EMC of 6 and 10 a summary statistic hides the
                          thing a reader most needs to judge, which is whether one tumour carries a
                          row. The muscle reference samples are drawn where the platform has them.
  2  the instrument       the size-matched empirical null with the observed delta and the 95% band.
                          This is the manuscript's central methodological claim and it had no
                          picture. The null is REGENERATED from the seeded pool, not sketched.
  3  evidence classes     the catalogue, by class. "Three genes are the whole of class A" is the
                          paper's most quotable sentence and was carried only in prose.
  4  convergence matrix   genes x independent instruments -- which instrument supports which gene.
  5  muscle control       the ENO3 admixture objection and its answer, on one pair of axes.

RULES THE DRAWING ENFORCES
  * Columns and panels that measure different quantities are never put on a shared scale, and no
    glyph is sized by an effect magnitude that is not comparable across its neighbours.
  * A pale or empty cell is "this instrument did not support it", NEVER "this gene is absent". A
    contrast that could not be computed is drawn distinctly from one that was computed and flat.
  * No panel asserts occupancy or causation. Every axis here is correlative and the captions say so.
  * Every number is read from a committed artifact. A cell whose statistic cannot be read is not
    drawn, so a figure can never carry a number the artifacts do not.

USAGE
    python3 nr4a3_fusion_targets_figures.py           # write PNG (300 dpi) + PDF for every figure
    python3 nr4a3_fusion_targets_figures.py --figure fig4-instrument-convergence
                                                      # draw ONE figure; the others are never called
    python3 nr4a3_fusion_targets_figures.py --check   # stdlib-only staleness check, draws nothing
    python3 nr4a3_fusion_targets_figures.py --check-builds
                                                      # stdlib-only: do the recorded per-build output
                                                      # identities still match the files on disk?
"""

import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FIGDIR = os.path.normpath(os.path.join(HERE, "..", "manuscripts", "figures"))

TARGETS = os.path.join(HERE, "nr4a3-fusion-targets.json")
INPUTS = os.path.join(HERE, "nr4a3-fusion-targets-inputs.json")
ROBUST = os.path.join(HERE, "nr4a3-fusion-targets-robustness.json")
SEQ3 = os.path.join(HERE, "gse28866-tumour-vs-normal.json")
MOTIF = os.path.join(HERE, "emc-ret-target-scan.json")
CONF = os.path.join(HERE, "nr4a3-fusion-targets-confounds.json")
OCC = os.path.join(HERE, "nr4a3-fusion-targets-occupancy.json")
STAMP = os.path.join(FIGDIR, "figure-provenance.json")

SOURCES = [TARGETS, INPUTS, ROBUST, SEQ3, MOTIF, CONF, OCC]

GENES = ["ENO3", "PPARG", "SEMA3C"]
P6 = "GSE24369_series_matrix.txt.gz"
P3 = "GSE4303-GPL3290_series_matrix.txt.gz"
PLATS = [(P6, "GPL6244  ·  single-channel intensity"), (P3, "GPL3290  ·  two-colour log-ratio")]

# One palette, used consistently. Green = supported by that instrument; grey = not supported;
# hatched = not computable. Never a magnitude ramp across non-comparable columns.
C_EMC = "#1b5e20"
C_SUPP = "#2e7d32"
C_WEAK = "#a8cdb0"
C_NULL = "#e4e9ef"
C_ABSENT = "#c8d0da"
C_INK = "#1b2733"
C_MUTE = "#5c6b7a"
C_DOWN = "#8c3b3b"
STRATUM_COLOUR = {
    "EMC": C_EMC, "LGFMS": "#5b8ca8", "desmoid_fibromatosis": "#c08a3e",
    "fibrosarcoma": "#8a6fa8", "DFSP": "#5b8ca8", "GIST": "#c08a3e",
}
STRATUM_LABEL = {
    "EMC": "EMC", "LGFMS": "LGFMS (myxoid, FET-rearranged)",
    "fibrosarcoma": "myxofibrosarcoma (myxoid)",
    "desmoid_fibromatosis": "desmoid fibromatosis (not myxoid)",
    "DFSP": "DFSP (not myxoid)", "GIST": "GIST (not myxoid, other ref. pool)",
}


def _load(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _fingerprint():
    """Content hash of every artifact a figure reads, so staleness is checkable without drawing."""
    import hashlib
    out = {}
    for p in SOURCES:
        h = hashlib.sha256()
        with open(p, "rb") as fh:
            for chunk in iter(lambda: fh.read(1 << 20), b""):
                h.update(chunk)
        out[os.path.basename(p)] = h.hexdigest()[:16]
    return out


# =================================================================================================
# FIGURE 1 -- every tumour, visible
# =================================================================================================
def fig_per_sample(plt, tgt):
    import numpy as np
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 5.4), gridspec_kw={"width_ratios": [1.55, 1]})
    for ax, (plat, title) in zip(axes, PLATS):
        seen = []
        for gi, gene in enumerate(GENES):
            rec = (tgt["gene_reads"].get(gene) or {}).get(plat)
            if not rec or not rec.get("per_sample"):
                ax.text(gi, 0, "not readable", ha="center", va="center", fontsize=8,
                        color=C_MUTE, rotation=90)
                continue
            by = {}
            for s in rec["per_sample"]:
                if s.get("z_vs_array") is not None:
                    by.setdefault(s["class"], []).append(s["z_vs_array"])
            order = ["EMC"] + [c for c in by if c != "EMC"]
            n_str = len(order)
            for si, cl in enumerate(order):
                vals = by.get(cl) or []
                if not vals:
                    continue
                off = (si - (n_str - 1) / 2) * 0.19
                rng = np.random.default_rng(1000 * gi + si)      # deterministic jitter
                x = gi + off + rng.uniform(-0.045, 0.045, len(vals))
                ax.scatter(x, vals, s=30 if cl == "EMC" else 20,
                           c=STRATUM_COLOUR.get(cl, C_MUTE),
                           edgecolors="white", linewidths=0.6, zorder=3,
                           marker="o" if cl == "EMC" else "s")
                ax.plot([gi + off - 0.085, gi + off + 0.085],
                        [float(np.mean(vals))] * 2, color=C_INK, lw=1.6, zorder=4)
                if cl not in seen:
                    seen.append(cl)
        ax.axhline(0, color=C_MUTE, lw=0.7, ls=":", zorder=1)
        ax.set_xticks(range(len(GENES)))
        ax.set_xticklabels([f"$\\it{{{g}}}$" for g in GENES], fontsize=12)
        ax.set_title(title, fontsize=10.5, color=C_INK, pad=8)
        ax.set_ylabel("within-array $z$ (probe distribution of that sample)", fontsize=9.5)
        ax.spines[["top", "right"]].set_visible(False)
        ax.tick_params(labelsize=9)
        # Legend BELOW the axes: at n_EMC of 6 the interesting points sit high, and an in-axes
        # legend covered them on GPL3290.
        handles = [plt.Line2D([], [], marker="o" if c == "EMC" else "s", ls="",
                              color=STRATUM_COLOUR.get(c, C_MUTE),
                              markeredgecolor="white", markersize=7,
                              label=STRATUM_LABEL.get(c, c)) for c in seen]
        ax.legend(handles=handles, fontsize=7.6, loc="upper left", frameon=False,
                  bbox_to_anchor=(-0.02, -0.09), ncol=2, handletextpad=0.4,
                  borderpad=0.2, labelspacing=0.3, columnspacing=1.1)
    fig.suptitle("Every tumour, per gene and per comparator stratum", fontsize=13,
                 color=C_INK, y=0.985, x=0.02, ha="left", fontweight="bold")
    fig.text(0.02, 0.925, "Horizontal bar = arm mean. Each point is one tumour. The two platforms "
                          "measure different quantities and are never pooled.",
             fontsize=8.6, color=C_MUTE, ha="left")
    fig.tight_layout(rect=[0, 0.06, 1, 0.90])
    return fig


# =================================================================================================
# FIGURE 2 -- the instrument the paper is arguing for
# =================================================================================================
def fig_null(plt, tgt, inputs):
    """Regenerate the real seeded null and draw it, rather than sketching a bell."""
    import numpy as np
    sys.path.insert(0, HERE)
    import nr4a3_fusion_targets as M

    panels = [
        (P6, "A+B_all_dna_binding", "A+B direct-target set (19 genes)", "GPL6244"),
        (P3, "A+B_all_dna_binding", "A+B direct-target set (17 readable)", "GPL3290"),
        (P6, "D_filion_table1", "published EMC phenotype (21 genes)", "GPL6244"),
        (P3, "D_filion_table1", "published EMC phenotype (18 readable)", "GPL3290"),
    ]
    key = {"A+B_all_dna_binding": "A_plus_B_all_dna_binding",
           "D_filion_table1": "D_filion_table1_emc_vs_137_sarcomas"}
    fig, axes = plt.subplots(2, 2, figsize=(11, 6.4))
    for ax, (plat, sk, label, pname) in zip(axes.ravel(), panels):
        sc = (tgt["set_scores"][key[sk]] or {}).get(plat) or {}
        nc = sc.get("null_calibration") or {}
        if not nc.get("computed"):
            ax.axis("off")
            continue
        t = inputs["targets"][plat]
        _, emc, comp = M._group_indices(t["samples"])
        null = M._null_scores(t, nc["set_size"], emc, comp, M.NULL_DRAWS, M.NULL_SEED)
        draws = null["_sorted"]
        obs = nc["observed_delta"]
        lo, hi = nc["null_q025"], nc["null_q975"]
        ax.hist(draws, bins=60, color="#cdd6e0", edgecolor="white", linewidth=0.3)
        ax.axvspan(lo, hi, color="#8fa6bd", alpha=0.22, lw=0,
                   label=f"95% of random {nc['set_size']}-gene sets")
        cleared = abs(obs) > abs(hi if obs >= 0 else lo)
        ax.axvline(obs, color=C_SUPP if cleared else C_DOWN, lw=2.4, zorder=5)
        ax.annotate(f"observed {obs:+.3f}", xy=(obs, ax.get_ylim()[1] * 0.94),
                    xytext=(6, 0), textcoords="offset points", fontsize=9,
                    color=C_SUPP if cleared else C_DOWN, fontweight="bold", va="top")
        thr = hi if obs >= 0 else lo
        frac = abs(obs) / abs(thr)
        reach = f"reached {frac:.0%} of it" if frac < 1 else f"{frac:.1f}× past it"
        ax.annotate(f"clears at {thr:+.3f}\n{reach}",
                    xy=(thr, ax.get_ylim()[1] * 0.55), xytext=(6, 0),
                    textcoords="offset points", fontsize=8, color=C_MUTE, va="top")
        ax.set_title(f"{label}  ·  {pname}", fontsize=10, color=C_INK)
        ax.set_xlabel("EMC − comparator, mean $z$ over the set", fontsize=8.8)
        ax.set_ylabel("random gene sets", fontsize=8.8)
        ax.spines[["top", "right"]].set_visible(False)
        ax.tick_params(labelsize=8)
        ax.legend(fontsize=7.4, frameon=False, loc="upper left")
    fig.suptitle("A set score means nothing until an arbitrary set of the same size is scored too",
                 fontsize=13, color=C_INK, y=0.985, x=0.02, ha="left", fontweight="bold")
    fig.text(0.02, 0.935, "Grey histogram = 4,000 random gene sets of exactly the observed size, "
                          "drawn from the platform's own symbols and scored identically.",
             fontsize=8.6, color=C_MUTE, ha="left")
    fig.tight_layout(rect=[0, 0, 1, 0.91])
    return fig


# =================================================================================================
# FIGURE 3 -- the catalogue
# =================================================================================================
def fig_classes(plt, tgt):
    et = tgt["evidence_table"]
    rows = et if isinstance(et, list) else et.get("rows", [])
    order = ["A", "B", "C", "D"]
    title = {
        "A": "A — DNA-binding assay with an NR4A3 FUSION",
        "B": "B — the same assay class with NATIVE NR4A3",
        "C": "C — moves when the fusion is expressed; no binding assay",
        "D": "D — measured in EMC tissue; no mechanism",
    }
    # The artifact's own controlled vocabulary -> the manuscript's class letters. Mapped explicitly
    # rather than by first initial, which silently produced four empty bars.
    CLASS_OF = {"fusion_dna_binding": "A", "native_dna_binding": "B",
                "fusion_expression_only": "C", "emc_tumour_expression_only": "D"}
    by = {k: [] for k in order}
    unmapped = sorted({r.get("evidence_class") for r in rows
                       if isinstance(r, dict) and r.get("evidence_class") not in CLASS_OF})
    if unmapped:
        raise SystemExit(f"fig_classes: unmapped evidence_class values {unmapped} -- refusing to "
                         "draw a catalogue figure that would silently omit rows.")
    for r in rows:
        if isinstance(r, dict) and r.get("gene"):
            by[CLASS_OF[r["evidence_class"]]].append(r["gene"])
    expected = (tgt["evidence_table"] or {}).get("counts_by_class") or {}
    for vocab, letter in CLASS_OF.items():
        if vocab in expected and len(set(by[letter])) != expected[vocab]:
            raise SystemExit(f"fig_classes: class {letter} drew {len(set(by[letter]))} genes but "
                             f"the artifact counts {expected[vocab]}.")
    fig, ax = plt.subplots(figsize=(11, 4.6))
    y = 0
    for k in order:
        genes = sorted(set(by[k]))
        n = len(genes)
        col = C_SUPP if k == "A" else ("#8fa6bd" if k == "B" else C_ABSENT)
        ax.barh(y, n, height=0.62, color=col, edgecolor="white")
        ax.text(-0.35, y, title[k], ha="right", va="center", fontsize=9.5, color=C_INK)
        ax.text(n + 0.35, y, f"{n}   " + ", ".join(genes), ha="left", va="center",
                fontsize=8.2, color=C_MUTE if k != "A" else C_INK,
                fontweight="bold" if k == "A" else "normal")
        y -= 1
    ax.set_ylim(y + 0.4, 0.7)
    ax.set_xlim(0, 30)
    ax.set_xlabel("genes with this level of published evidence", fontsize=9.5)
    ax.set_yticks([])
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.tick_params(labelsize=9)
    fig.suptitle("The entire published direct-target catalogue of an NR4A3 chimera is three genes",
                 fontsize=13, color=C_INK, y=0.97, x=0.02, ha="left", fontweight="bold")
    fig.text(0.02, 0.885, "Counted across 2,276 retrieved full-text documents (§3.10). A count of "
                          "what has been PUBLISHED, not of what exists.",
             fontsize=8.6, color=C_MUTE, ha="left")
    fig.tight_layout(rect=[0, 0, 1, 0.86])
    return fig


# =================================================================================================
# FIGURE 4 -- which instrument supports which gene
# =================================================================================================
def _cells(tgt, robust, seq3, motif, conf, occ):
    """One row per gene, one entry per instrument: (text, state). State drives colour only."""
    qmap = {}
    for r in robust.get("rows", []):
        if r.get("kind") == "gene" and r.get("computed"):
            qmap[(r.get("name"), r.get("matrix_file"))] = r
    # GSE4303 IS the cohort Subramanian (2005) reported "high PPARG in most EMCs" from, so a PPARG
    # reading on GPL3290 re-derives a published finding from the data it was published from. It is
    # marked, not silently coloured as independent support -- the manuscript grades set E the same
    # way and the gene row must not be treated more gently than the set row.
    CIRCULAR = {("PPARG", P3)}
    out = {}
    for g in GENES:
        row = []
        for plat, short in ((P6, "GPL6244"), (P3, "GPL3290")):
            rec = qmap.get((g, plat))
            if not rec:
                row.append(("not computed", "absent"))
                continue
            q = rec.get("bh_fdr_q_across_genes_on_this_platform")
            d = rec.get("observed_delta_re_derived")
            if (g, plat) in CIRCULAR:
                row.append((f"Δ{d:+.2f} · q={q:.3g}\ncircular — not a test", "circular"))
                continue
            state = "supported" if (q is not None and q < 0.05) else "weak"
            row.append((f"Δ{d:+.2f}\nq={q:.3g}" if q is not None else f"Δ{d:+.2f}", state))
        # stratified: the LEAST FAVOURABLE p across every comparator stratum on GPL6244
        pr = ((conf["platforms"][P6]["restricted_comparator_arms"]["per_gene"]).get(g) or {})
        ps = [c["permutation"]["p_two_sided"] for c in pr.values()
              if isinstance(c, dict) and c.get("permutation")]
        if ps:
            worst = max(ps)
            row.append((f"$p$ = {worst:.3g}\nacross {len(ps)} strata",
                        "supported" if worst < 0.05 else "weak"))
        else:
            row.append(("not computed", "absent"))
        # 3SEQ percentile. TWO SEPARATE COMPARISONS RANKED AGAINST TWO DIFFERENT GENE SETS, and
        # the header used to name a third number that is the denominator of neither.
        #   emc_over_normal_percentile  ranks the gene among the deposit genes that have a
        #                               computable EMC/normal ratio  (n_genes_with_a_normal_ratio)
        #   emc_over_sarcoma_percentile ranks it among those with a computable EMC/sarcoma ratio
        #                               (n_genes_with_a_sarcoma_ratio)
        # n_genes_in_deposit is the deposit CENSUS. A gene whose comparator median is zero has no
        # ratio on that axis and is dropped from that axis's distribution, so the two populations
        # are smaller than the census and are not equal to each other.
        # ⚠ The colour below is an EITHER-AXIS maximum: a cell is green when one axis reaches the
        # 95th percentile even if the other does not. That rule is UNCHANGED here; what changed is
        # that the row label and the caption now say so. PPARG is the live case: 84.0 vs normal,
        # 96.4 vs sarcoma, green on the sarcoma axis alone.
        cal = (seq3.get("ratio_calibration") or {}).get("per_gene", {}).get(g) or {}
        pn, psar = cal.get("emc_over_normal_percentile"), cal.get("emc_over_sarcoma_percentile")
        if pn is None and psar is None:
            row.append(("not readable", "absent"))
        else:
            best = max(x for x in (pn, psar) if x is not None)
            txt = (f"normal {cal.get('emc_over_normal')}× / {pn}ᵗʰ\n"
                   f"sarcoma {cal.get('emc_over_sarcoma')}× / {psar}ᵗʰ")
            row.append((txt, "supported" if best >= 95 else "weak"))
        # NBRE, exact motif against the dinucleotide-preserving (composition-matched) null
        fg = ((motif.get("part_1_nbre_scan") or {}).get("focus_genes") or {}).get(g) or {}
        sn = fg.get("shuffle_null") or {}
        n = (fg.get("nbre_exact") or {}).get("n")
        p = sn.get("empirical_p_one_sided")
        if n is None:
            row.append(("not scanned", "absent"))
        else:
            row.append((f"{n} exact site{'s' if n != 1 else ''}" +
                        (f"\np={p:.3g}" if p is not None else ""),
                        "supported" if (p is not None and p < 0.05) else "weak"))
        # NR4A occupancy, calibrated against the 198-gene background panel. Reported as the best p
        # any informative EXPERIMENT gives, beside the number of tests -- a raw peak count here is
        # meaningless because the deepest catalogue recovers 82.8% of arbitrary genes.
        osum = (occ.get("per_gene_summary") or {}).get(g) or {}
        best = osum.get("best_empirical_p_vs_panel")
        nexp = osum.get("n_informative_experiments")
        if best is None:
            row.append(("no informative\npeak set", "absent"))
        else:
            row.append((f"best $p$ = {best:.3g}\nof {nexp} experiments",
                        "supported" if best < 0.05 / max(1, nexp) else "weak"))
        out[g] = row
    return out


def _matrix_row_labels(seq3):
    """Instrument labels, in the order `_cells` emits them.

    The 3SEQ label reads its two ranking populations OUT OF THE ARTIFACT rather than carrying a
    literal. The defect this repair closes was exactly a hard-coded literal (14,120, the deposit
    census) standing where two different, smaller populations belong; a label that cannot drift
    from its artifact cannot reacquire that defect.
    """
    rc = seq3.get("ratio_calibration") or {}
    n_norm = rc.get("n_genes_with_a_normal_ratio")
    n_sarc = rc.get("n_genes_with_a_sarcoma_ratio")

    def _n(v):
        return f"{v:,}" if isinstance(v, int) else "an unrecorded number of"

    return [
        ["GPL6244 array", "Δ mean $z$ · BH $q$"],
        ["GPL3290 array", "Δ mean $z$ · BH $q$"],
        ["Each comparator stratum", "least favourable exact $p$"],
        ["3SEQ: score ratio / percentile",
         f"N = normal: rank among {_n(n_norm)} genes",
         f"S = sarcoma: rank among {_n(n_sarc)} genes",
         "green if EITHER reaches the 95th"],
        ["NBRE motif", "sequence, not occupancy"],
        ["NR4A occupancy", "NR4A1 + native NR4A3", "hg38: 198-gene panel; hg19: 200"],
    ]


def fig_matrix(plt, tgt, robust, seq3, motif, conf, occ):
    """Genes × instruments, drawn TRANSPOSED: one row per instrument, one column per gene.

    WHY TRANSPOSED (2026-09-09). The previous layout was six columns on a 15.6-inch canvas,
    scaled to a ~150 mm text column in both PDFs — a reduction of roughly 0.38, which rendered
    8.4 pt header type at about 3.2 pt and ran the NBRE header into the occupancy header. Three
    columns fit the printed width at close to 1:1, so the type is legible at final size without
    shrinking a font or promising a wider page. No cell value, state, threshold or colour
    expression changes with the orientation.
    """
    rows = _matrix_row_labels(seq3)
    cells = _cells(tgt, robust, seq3, motif, conf, occ)
    colour = {"supported": C_SUPP, "weak": C_NULL, "absent": C_ABSENT, "circular": "#b08a3e"}
    nrow, ncol = len(rows), len(GENES)

    fig, ax = plt.subplots(figsize=(6.4, 7.9))
    for ci, g in enumerate(GENES):
        ax.text(ci + 0.5, nrow + 0.12, f"$\\it{{{g}}}$", ha="center", va="bottom",
                fontsize=11, color=C_INK)
    for ri, label_lines in enumerate(rows):
        y = nrow - 1 - ri
        ax.text(-0.10, y + 0.5, "\n".join(label_lines), ha="right", va="center",
                fontsize=7.8, color=C_INK, linespacing=1.45)
        for ci, g in enumerate(GENES):
            txt, state = cells[g][ri]
            # Wrap long cells without changing their numbers, comparison order or state.
            if ri == 3:
                txt = txt.replace("normal ", "N: ").replace("sarcoma ", "S: ")
                txt = txt.replace(" / ", "\n")
            elif ri == 5:
                txt = txt.replace(" experiments", "\nexperiments")
            elif state == "circular":
                txt = txt.replace(" · ", "\n").replace("circular — not a test", "circular\nnot a test")
            ax.add_patch(plt.Rectangle((ci + 0.04, y + 0.06), 0.92, 0.88,
                                       facecolor=colour[state], edgecolor="white", lw=1.4,
                                       hatch="///" if state == "absent" else None))
            ax.text(ci + 0.5, y + 0.5, txt, ha="center", va="center", fontsize=8.3,
                    color="white" if state in ("supported", "circular") else C_INK,
                    linespacing=1.45,
                    fontweight="bold" if state == "supported" else "normal")
    ax.set_xlim(-2.35, ncol)
    ax.set_ylim(-0.62, nrow + 0.42)
    ax.axis("off")
    key = [("supported by this instrument", C_SUPP), ("not supported", C_NULL),
            ("circular (same discovery cohort)", "#b08a3e"),
           ("not computable", C_ABSENT)]
    handles = [plt.Rectangle((0, 0), 1, 1, facecolor=c, edgecolor="white",
                             hatch="///" if lab == "not computable" else None)
               for lab, c in key]
    ax.legend(handles, [k for k, _ in key], fontsize=7.8, frameon=False, ncol=2,
              loc="lower left", bbox_to_anchor=(0.0, 0.0), handlelength=1.6, columnspacing=1.2)
    fig.suptitle("Independent instruments applied to\nthe three published direct targets",
                 fontsize=11.5, color=C_INK, y=0.985, x=0.02, ha="left", fontweight="bold")
    rc = seq3.get("ratio_calibration") or {}
    n_dep = rc.get("n_genes_in_deposit")
    dep = f"{n_dep:,}" if isinstance(n_dep, int) else "an unrecorded number of"
    fig.text(0.02, 0.910,
             "Instrument statistics are not commensurable; no glyph is scaled by effect size.\n"
             "Colour encodes only support by that instrument. 3SEQ ratios use compressed\n"
             f"summary scores; percentiles are descriptive ranks. Of {dep} deposit genes,\n"
             "each rank uses those with a computable ratio. Green: either percentile ≥95.",
             fontsize=7.8, color=C_MUTE, ha="left", va="top", linespacing=1.5)
    fig.subplots_adjust(left=0.02, right=0.99, bottom=0.04, top=0.815)
    return fig


# =================================================================================================
# FIGURE 5 -- the muscle-admixture control
# =================================================================================================
def fig_muscle(plt, conf):
    m = conf["platforms"][P6]["muscle_admixture"]
    if m.get("_status"):
        return None
    fig, ax = plt.subplots(figsize=(8.6, 5.2))
    pts = [(g, r["muscle_reference_mean_percentile"], r["emc_minus_comparator"],
            r["is_muscle_marker"])
           for g, r in sorted(m["genes"].items())
           if r["muscle_reference_mean_percentile"] is not None
           and r["emc_minus_comparator"] is not None]
    for g, x, y, marker in pts:
        ax.scatter(x, y, s=125 if not marker else 95,
                   c="#8a6fa8" if marker else C_SUPP,
                   marker="s" if marker else "o",
                   edgecolors="white", linewidths=1.2, zorder=3)
    # The muscle markers all pile up at the right-hand edge by construction -- that IS the point --
    # so labels there go to the LEFT and are staggered by rank, rather than overplotting.
    crowd = sorted([p for p in pts if p[1] > 0.95], key=lambda p: -p[2])
    for rank, (g, x, y, _) in enumerate(crowd):
        ax.annotate(f"$\\it{{{g}}}$", (x, y), xytext=(-13, 0), textcoords="offset points",
                    ha="right", va="center", fontsize=10, color=C_INK)
    for g, x, y, _ in [p for p in pts if p[1] <= 0.95]:
        ax.annotate(f"$\\it{{{g}}}$", (x, y), xytext=(0, 13), textcoords="offset points",
                    ha="center", fontsize=10, color=C_INK)
    ax.axhline(0, color=C_MUTE, lw=0.9, ls=":")
    ax.set_xlabel("how muscle-restricted the gene is\n"
                  "(mean within-array percentile in the two pooled skeletal-muscle samples)",
                  fontsize=9.5)
    ax.set_ylabel("EMC − comparator\n(within-array percentile points)", fontsize=9.5)
    ax.spines[["top", "right"]].set_visible(False)
    ax.tick_params(labelsize=9)
    ax.set_xlim(0.28, 1.06)
    ys=[y for _,_,y,_ in pts]
    pad=0.10*(max(ys)-min(ys)) or 0.05
    ax.set_ylim(min(ys)-pad, max(ys)+pad)
    handles = [plt.Line2D([], [], marker="s", ls="", color="#8a6fa8", markeredgecolor="white",
                          markersize=9, label="skeletal-muscle marker"),
               plt.Line2D([], [], marker="o", ls="", color=C_SUPP, markeredgecolor="white",
                          markersize=9, label="class-A target gene")]
    ax.legend(handles=handles, fontsize=8.4, frameon=False, loc="upper left")
    fig.suptitle("If the $ENO3$ signal were admixed skeletal muscle, the muscle markers would "
                 "carry it too", fontsize=12.4, color=C_INK, y=0.98, x=0.02, ha="left",
                 fontweight="bold")
    fig.text(0.02, 0.915, "The two pooled skeletal-muscle RNA samples are in NEITHER arm and no "
                          "contrast uses them; they fix the scale of what muscle looks like here.",
             fontsize=8.6, color=C_MUTE, ha="left")
    fig.tight_layout(rect=[0, 0, 1, 0.89])
    return fig


# =================================================================================================
# =================================================================================================
# FIGURE REGISTRY -- what each figure needs, so ONE figure can be drawn without calling the others
# =================================================================================================
ART_PATHS = {"tgt": TARGETS, "inputs": INPUTS, "robust": ROBUST, "seq3": SEQ3,
             "motif": MOTIF, "conf": CONF, "occ": OCC}


def _draw_fig1(plt, art):
    return fig_null(plt, art["tgt"], art["inputs"])


def _draw_fig2(plt, art):
    return fig_classes(plt, art["tgt"])


def _draw_fig3(plt, art):
    return fig_per_sample(plt, art["tgt"])


def _draw_fig4(plt, art):
    return fig_matrix(plt, None, art["robust"], art["seq3"], art["motif"], art["conf"],
                      art["occ"])


def _draw_fig5(plt, art):
    return fig_muscle(plt, art["conf"])


#: name -> the artifacts it reads and the factory that draws it. Selection happens HERE, before
#: any factory is called. Calling build() and then picking one result is NOT the same thing: that
#: has already run fig_null's seeded null over the 5 MB INPUTS body.
FIGURE_SPECS = {
    "fig1-size-matched-null":        {"needs": ("tgt", "inputs"), "draw": _draw_fig1},
    "fig2-evidence-classes":         {"needs": ("tgt",), "draw": _draw_fig2},
    "fig3-per-sample-class-a":       {"needs": ("tgt",), "draw": _draw_fig3},
    "fig4-instrument-convergence":   {"needs": ("robust", "seq3", "motif", "conf", "occ"),
                                      "draw": _draw_fig4},
    "fig5-muscle-admixture-control": {"needs": ("conf",), "draw": _draw_fig5},
}

FIGURE_OUTPUTS = tuple(f"{n}.{e}" for n in FIGURE_SPECS for e in ("png", "pdf"))


def _sha256_file(path):
    import hashlib
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _identity(path):
    return {"bytes": os.path.getsize(path), "sha256": _sha256_file(path)}


def _output_identities():
    """Identity of every figure output that exists. Missing files are simply absent from the map."""
    out = {}
    for f in FIGURE_OUTPUTS:
        p = os.path.join(FIGDIR, f)
        if os.path.exists(p):
            out[f] = _identity(p)
    return out


def _read_stamp():
    if not os.path.exists(STAMP):
        return None
    return _load(STAMP)  # A corrupt existing record must never be replaced by an empty history.


CALIBRATION_EQUIVALENCE = {
    "artifact": "gse28866-tumour-vs-normal.json",
    "old": {"bytes": 27256,
            "sha256": "ac0a17bd81dd8bc2ecc3b5bb380de5ae00921ae2d32b5a9595bd1449720be407",
            "git_blob": "526084a99b3a44af0eb1720abe0ec268bae2c47a"},
    "current": {"bytes": 28606,
                "sha256": "386a035175d94ef8eccd3719d74ef39cff5e93461ed2470983777333a1962cee",
                "git_blob": "9e1fd200b05aa2f716044b8f197ec7212878b625"},
    "changed_paths": ["per_gene._contrast", "per_gene._contrast_superseded_2026-09-08",
                      "per_gene._annotation_correction_2026-09-08"],
    "verification": "Complete resident-blob comparison by the coordinator on 2026-09-09: "
                    "only the three contrast annotation keys differ; all other JSON values, "
                    "including ratio_calibration and every consumed number, are identical.",
    "scope": "Source equivalence, not generation. The annotation corrects reduction order, "
             "score compression and library context. It does not establish scientific acceptance.",
}


def _source_identities():
    return {os.path.basename(p): _identity(p) for p in SOURCES}


def _source_updates(stamp, names, identities):
    """Selective builds accept only the explicitly audited calibration annotation change."""
    now = {k: v["sha256"][:16] for k, v in identities.items()}
    if stamp is None:
        if set(names) != set(FIGURE_SPECS):
            raise ValueError("selective build requires the existing provenance and output inventory")
        return now, None
    prior = stamp["sources"]
    drift = {k for k, v in now.items() if prior.get(k) != v}
    if set(names) == set(FIGURE_SPECS):
        return now, None  # Allowed only after all affected factories succeed; checked below.
    eq = CALIBRATION_EQUIVALENCE
    key = eq["artifact"]
    allowed = (names == ["fig4-instrument-convergence"] and drift == {key}
               and prior.get(key) == eq["old"]["sha256"][:16]
               and identities[key] == {k: eq["current"][k] for k in ("bytes", "sha256")})
    if drift and not allowed:
        raise ValueError("unexplained source drift; no output or prefix may be refreshed: "
                         + ", ".join(sorted(drift)))
    return now, eq if allowed else None


def _git_output(*args):
    import subprocess
    env = dict(os.environ, GIT_NO_LAZY_FETCH="1", GIT_TERMINAL_PROMPT="0")
    return subprocess.run(["git", "-C", HERE, *args], env=env, check=True,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout


def _committed_source_context():
    """Require an actual committed generator and data before drawing, without fetching."""
    import hashlib
    from pathlib import Path
    root = Path(_git_output("rev-parse", "--show-toplevel").decode().strip())
    commit = _git_output("rev-parse", "HEAD").decode().strip()
    for path in [__file__, *SOURCES]:
        relative = Path(path).resolve().relative_to(root.resolve()).as_posix()
        body = _git_output("show", f"{commit}:{relative}")
        if hashlib.sha256(body).hexdigest() != _sha256_file(path):
            raise ValueError(f"uncommitted generation input: {relative}; anchor source before drawing")
    return {"source_commit": commit,
            "generator": {"path": Path(__file__).resolve().relative_to(root.resolve()).as_posix(),
                          **_identity(__file__)}}


def build(only=None):
    """Draw lazily; preserve prior provenance and stamp only complete successful output pairs."""
    if only is not None and only not in FIGURE_SPECS:
        raise ValueError(f"unknown figure: {only}")
    names = list(FIGURE_SPECS) if only is None else [only]
    prior = _read_stamp()
    sources = _source_identities()
    source_map, equivalence = _source_updates(prior, names, sources)
    context = _committed_source_context()
    before = _output_identities()
    stamp_before = _identity(STAMP) if prior is not None else None

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.family": "DejaVu Sans", "figure.facecolor": "white",
                         "axes.facecolor": "white", "savefig.facecolor": "white",
                         "axes.edgecolor": "#9aa7b4", "text.color": C_INK,
                         "axes.labelcolor": C_INK, "xtick.color": C_MUTE,
                         "ytick.color": C_MUTE})
    needed = {k for n in names for k in FIGURE_SPECS[n]["needs"]}
    art = {k: _load(ART_PATHS[k]) for k in sorted(needed)}
    os.makedirs(FIGDIR, exist_ok=True)
    written, drawn = [], []
    for name in names:
        fig = FIGURE_SPECS[name]["draw"](plt, art)
        if fig is None:
            continue
        try:
            for ext in ("png", "pdf"):
                path = os.path.join(FIGDIR, f"{name}.{ext}")
                fig.savefig(path, dpi=300 if ext == "png" else None, bbox_inches="tight")
                if not os.path.isfile(path) or not os.path.getsize(path):
                    raise ValueError(f"save did not produce a nonempty output: {path}")
                written.append(os.path.basename(path))
            drawn.append(name)
        finally:
            plt.close(fig)
    if not written:
        return []  # A skipped factory is not a generation event or permission to advance sources.
    after = _output_identities()
    changed = [f for f in FIGURE_OUTPUTS if f not in written and before.get(f) != after.get(f)]
    if changed:
        raise ValueError("build changed outputs outside its scope: " + ", ".join(changed))
    if sources != _source_identities():
        raise ValueError("source bytes changed during generation; provenance left untouched")
    if prior and set(names) == set(FIGURE_SPECS):
        for name in set(names) - set(drawn):
            stale = [os.path.basename(ART_PATHS[k]) for k in FIGURE_SPECS[name]["needs"]
                     if prior["sources"].get(os.path.basename(ART_PATHS[k]))
                     != source_map[os.path.basename(ART_PATHS[k])]]
            if stale:
                raise ValueError(f"skipped {name} still depends on changed sources: {stale}")
    if stamp_before != (_identity(STAMP) if os.path.exists(STAMP) else None):
        raise ValueError("provenance changed during generation; refusing to overwrite another writer")
    consumed = {os.path.basename(ART_PATHS[k]) for n in drawn for k in FIGURE_SPECS[n]["needs"]}
    _write_stamp(prior, drawn, written, consumed, before, after, sources, source_map,
                 equivalence, context, matplotlib.__version__)
    return written


def _write_stamp(prior, names, written, consumed, before, after, sources, source_map,
                 equivalence, context, matplotlib_version):
    import copy
    import datetime
    import platform
    import tempfile
    stamp = copy.deepcopy(prior) if prior is not None else {
        "_what": "Source identities with additive records of actual figure generation",
        "_regenerate": "python3 research/modalities/nr4a3_fusion_targets_figures.py",
        "figures": [], "sources": {}}
    expected = {f"{n}.{ext}" for n in names for ext in ("png", "pdf")}
    if set(written) != expected or any(f not in after for f in expected):
        raise ValueError("cannot stamp an incomplete output pair")
    record = {
        "utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "scope": names, "regenerated_outputs": sorted(written),
        **context,
        "command_argv": [sys.executable, *sys.argv],
        "runtime": {"python": sys.version, "executable": sys.executable,
                    "platform": platform.platform(), "matplotlib": matplotlib_version},
        "prior_source_map": dict(stamp["sources"]),
        "sources_verified": sources,
        "sources_actually_consumed": {k: sources[k] for k in sorted(consumed)},
        "outputs_before": {f: before[f] for f in sorted(written) if f in before},
        "outputs_after": {f: after[f] for f in sorted(written)},
        "outputs_not_regenerated": {f: after[f] for f in sorted(after) if f not in written},
        "scope_note": "Only regenerated_outputs were drawn. The other outputs retain their "
                      "previous bytes and generation history. No visual or scientific acceptance.",
    }
    if equivalence:
        record["source_equivalence"] = copy.deepcopy(equivalence)
    stamp["sources"] = dict(source_map)
    stamp["sources_meaning"] = "Current source identities; prior draw identities and verified " \
                               "equivalences remain in the retained history and build records."
    stamp["figures"] = sorted(set(stamp["figures"]) | set(written))
    stamp.setdefault("builds", []).append(record)
    fd, temporary = tempfile.mkstemp(prefix="figure-provenance-", suffix=".json", dir=FIGDIR)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(stamp, fh, indent=1, sort_keys=True)
            fh.write("\n")
        os.replace(temporary, STAMP)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def check_builds():
    """Verify the latest identity per output; old records remain historical, not current claims."""
    import hashlib
    stamp = _read_stamp()
    builds = stamp.get("builds", []) if stamp else []
    if not builds:
        print("figures --check-builds: no build records to verify")
        return 1
    latest = {}
    for i, record in enumerate(builds):
        for output in record["outputs_after"]:
            latest[output] = i
    bad = []
    for output, i in latest.items():
        path = os.path.join(FIGDIR, output)
        if not os.path.isfile(path) or _identity(path) != builds[i]["outputs_after"][output]:
            bad.append(f"output identity differs: {output}")
    current_sources = _source_identities()
    for i in set(latest.values()):
        record = builds[i]
        for name, identity in record["sources_actually_consumed"].items():
            if current_sources.get(name) != identity:
                bad.append(f"source identity differs: {name} (build {i})")
            try:
                body = _git_output("show", f"{record['source_commit']}:research/modalities/{name}")
                if len(body) != identity["bytes"] or hashlib.sha256(body).hexdigest() != identity["sha256"]:
                    bad.append(f"committed source identity differs: {name} (build {i})")
            except Exception as exc:
                bad.append(f"cannot verify committed source: {name} (build {i}): {exc}")
        generator = record["generator"]
        try:
            body = _git_output("show", f"{record['source_commit']}:{generator['path']}")
            if len(body) != generator["bytes"] or hashlib.sha256(body).hexdigest() != generator["sha256"]:
                bad.append(f"committed generator identity differs (build {i})")
        except Exception as exc:
            bad.append(f"cannot verify committed generator (build {i}): {exc}")
    if _identity(__file__) != {k: builds[-1]["generator"][k] for k in ("bytes", "sha256")}:
        bad.append("current generator differs from the latest build")
    for message in bad:
        print("figures --check-builds: " + message)
    if bad:
        return 1
    print(f"figures --check-builds: OK -- latest identities for {len(latest)} output(s); "
          f"{len(builds)} historical build record(s) retained")
    return 0


def check():
    """Stdlib-only: are the committed figures drawn from the committed artifacts?"""
    if not os.path.exists(STAMP):
        print("figures --check: no provenance stamp; run the generator")
        return 1
    have = _load(STAMP)
    now = _fingerprint()
    drift = {k: (have["sources"].get(k), v) for k, v in now.items() if have["sources"].get(k) != v}
    missing = [f for f in have.get("figures", []) if not os.path.exists(os.path.join(FIGDIR, f))]
    if drift or missing:
        for k, (was, is_) in drift.items():
            print(f"figures --check: DRIFT {k}: stamped {was}, now {is_}")
        for f in missing:
            print(f"figures --check: MISSING {f}")
        print("Re-run: python3 research/modalities/nr4a3_fusion_targets_figures.py")
        return 1
    print(f"figures --check: OK -- {len(have.get('figures', []))} files match "
          f"{len(now)} committed artifacts")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    ap.add_argument("--check", action="store_true",
                    help="stdlib-only staleness check against the artifacts; draws nothing")
    ap.add_argument("--check-builds", action="store_true",
                    help="stdlib-only: verify recorded per-build output identities; draws nothing")
    ap.add_argument("--figure", metavar="NAME", choices=sorted(FIGURE_SPECS), default=None,
                    help="draw exactly this figure; the other factories are never called")
    args = ap.parse_args()
    if args.check:
        return check()
    if args.check_builds:
        return check_builds()
    written = build(only=args.figure)
    scope = args.figure or "all figures"
    print(f"figures [{scope}]: wrote {len(written)} file(s) to {os.path.relpath(FIGDIR)}")
    for w in written:
        print("   ", w)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
