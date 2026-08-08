#!/usr/bin/env python3
"""Figure 1 for the EWSR1::NR4A3 transcriptional-output manuscript — the evidence-convergence
matrix for the three class-A direct-target genes.

WHY THIS FIGURE
---------------
The manuscript's result is not a single number; it is that several INDEPENDENT instruments, applied
to the same three genes, agree about one of them and not about the others. That shape is invisible in
the paper's tables, which are necessarily one instrument each. One matrix — genes down, instruments
across — puts the whole claim on one screen: ENO3's row is supported everywhere, SEMA3C's nowhere,
PPARG's in between.

⛔ WHAT THE FIGURE MAY NOT IMPLY, AND HOW THE DRAWING ENFORCES IT
  * The columns are NOT commensurable. A two-colour array log-ratio, a single-channel array z, a 3SEQ
    read-density ratio and a motif count are four different quantities on four different scales, and
    the manuscript is explicit that the cohorts are never pooled. So the glyph is deliberately NOT
    sized by effect magnitude — a reader cannot accidentally compare a cell's area across columns.
    Colour encodes DIRECTION and whether the instrument SUPPORTED the gene; the number printed in the
    cell is the instrument's own statistic, in its own units, labelled per column.
  * A pale cell is "this instrument did not support it", never "this gene is absent" — an absent
    reading is not a reading of absence, and the one genuinely absent contrast is drawn as a distinct
    hatched cell rather than as a weak result.
  * No cell asserts occupancy or causation. The caption says so, and the motif column's own header
    carries "sequence, not occupancy".

⛔ EVERY NUMBER IS READ FROM A COMMITTED ARTIFACT. Nothing is typed into this file — the module
refuses to draw a cell whose statistic it could not read, so a figure can never carry a number the
artifacts do not. Sources:
    nr4a3-fusion-targets.json            per-gene array deltas
    nr4a3-fusion-targets-robustness.json exact label-permutation p and BH q
    gse28866-tumour-vs-normal.json       the independent 3SEQ cohort
    emc-ret-target-scan.json             NBRE counts and their composition-matched null

USAGE
    python3 nr4a3_fusion_targets_figure.py            # write the SVG
    python3 nr4a3_fusion_targets_figure.py --check    # verify the committed SVG is current
"""

import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "manuscripts", "figures", "fusion-target-evidence-matrix.svg")

TARGETS = os.path.join(HERE, "nr4a3-fusion-targets.json")
ROBUST = os.path.join(HERE, "nr4a3-fusion-targets-robustness.json")
SEQ3 = os.path.join(HERE, "gse28866-tumour-vs-normal.json")
MOTIF = os.path.join(HERE, "emc-ret-target-scan.json")

GENES = ["ENO3", "PPARG", "SEMA3C"]
ALPHA = 0.05

# colour: supported / not-supported / not-readable. Deliberately NOT a magnitude ramp.
C_UP = "#2e7d32"        # higher in EMC and the instrument supported it
C_DIR = "#7fb98a"       # higher in EMC, DIRECTION ONLY -- the instrument carries no test
C_UP_WEAK = "#b7dfc0"   # higher in EMC, instrument did not support it
C_NULL = "#e9edf2"      # no support / count at chance
C_ABSENT = "#cfd6de"    # no contrast computable
C_TEXT = "#1b2733"
C_MUTED = "#5c6b7a"
C_RULE = "#d5dce4"


def _load(p):
    with open(p) as fh:
        return json.load(fh)


def esc(s):
    """XML-escape any text that reaches a <text> node.

    ⛔ NOT COSMETIC. The legend reads "q or p < 0.05" and `_fmt_p` emits "p<0.001", so the figure
    carried raw `<` characters into text content and was NOT well-formed XML — it parsed as broken
    and would have failed to render wherever a journal rasterises it. A figure that looks right in
    one previewer and is invalid to a parser is the worst failure mode available here, because
    nothing about it looks wrong until it is somebody else's problem.
    """
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def _fmt_p(p):
    if p is None:
        return "—"
    if p < 0.001:
        return "p<0.001"
    return "p=%.3g" % p


def collect():
    """Read every cell from the artifacts. A cell we cannot read is recorded as unreadable, never
    silently dropped and never defaulted to a neutral-looking value."""
    tg, rb, s3, mo = _load(TARGETS), _load(ROBUST), _load(SEQ3), _load(MOTIF)

    perm = {}
    for r in rb.get("rows", []):
        if r.get("computed") and r.get("kind") == "gene":
            perm[(r["name"], r["platform"])] = r

    rows = []
    for g in GENES:
        cells = []
        # --- the two array platforms: delta + exact permutation p + BH q
        for plat, series in (("GPL6244", "GSE24369_series_matrix.txt.gz"),
                             ("GPL3290", "GSE4303-GPL3290_series_matrix.txt.gz")):
            node = ((tg.get("gene_reads") or {}).get(g) or {}).get(series) or {}
            w = node.get("welch_EMC_vs_comparator") or {}
            delta = w.get("delta_a_minus_b")
            pr = perm.get((g, plat)) or {}
            p = (pr.get("label_permutation") or {}).get("p_two_sided")
            q = pr.get("bh_fdr_q_across_genes_on_this_platform")
            if delta is None:
                cells.append({"kind": "absent", "top": "no contrast", "bot": ""})
            else:
                sup = q is not None and q < ALPHA and delta > 0
                cells.append({
                    "kind": "up" if sup else ("upweak" if delta > 0 else "null"),
                    "top": "%+.2f" % delta,
                    "bot": ("q=%.3g" % q) if q is not None else _fmt_p(p),
                })
        # --- the independent 3SEQ cohort: two ratios, no test (n = 4)
        pg = ((s3.get("per_gene") or {}).get("values") or {}).get(g) or {}
        emc = pg.get("emc_median")
        for label, key in (("vs normal", "normal_median"), ("vs sarcoma", "sarcoma_median")):
            comp = pg.get(key)
            if emc is None or comp in (None, 0):
                cells.append({"kind": "absent", "top": "not readable", "bot": ""})
            else:
                ratio = emc / comp
                # ⛔ NEVER `up`. The 3SEQ arm is n = 4 with no z-score, no test and no interval, so a
                # cell that rendered like a significant array result would claim support this cohort
                # cannot give. `dir` is its own category for exactly that reason.
                cells.append({"kind": "dir" if ratio > 1 else "null",
                              "top": "%.2f×" % ratio, "bot": "direction only"})
        # --- the sequence axis: NBRE count against its composition-matched null
        p1 = mo.get("part_1_nbre_scan") or {}
        rec = (p1.get("focus_genes") or {}).get(g) or {}
        nb = (rec.get("nbre_exact") or {}).get("n")
        pn = (rec.get("shuffle_null") or {}).get("empirical_p_one_sided")
        if nb is None:
            cells.append({"kind": "absent", "top": "not scanned", "bot": ""})
        else:
            sup = pn is not None and pn < ALPHA and nb > 0
            cells.append({"kind": "up" if sup else "null",
                          "top": "%d site%s" % (nb, "" if nb == 1 else "s"),
                          "bot": _fmt_p(pn)})
        rows.append({"gene": g, "cells": cells})
    return rows


COLS = [
    ("GPL6244", "array 1 · Δ mean z"),
    ("GPL3290", "array 2 · Δ mean z"),
    ("3SEQ vs normal", "cohort 3 · ratio"),
    ("3SEQ vs sarcoma", "cohort 3 · ratio"),
    ("NBRE motif", "sequence, not occupancy"),
]

W, PAD = 1000, 30
LABEL_W = 108
TOP = 116
CELL_H, CELL_GAP = 74, 12


def render(rows):
    n = len(COLS)
    grid_w = W - 2 * PAD - LABEL_W
    cw = (grid_w - CELL_GAP * (n - 1)) / n
    h = TOP + len(rows) * (CELL_H + CELL_GAP) + 112
    o = []
    a = o.append
    a(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{int(h)}" '
      f'viewBox="0 0 {W} {int(h)}" font-family="Helvetica,Arial,sans-serif">')
    a(f'<rect width="{W}" height="{int(h)}" fill="#ffffff"/>')
    a(f'<text x="{PAD}" y="40" font-size="19" font-weight="600" fill="{C_TEXT}">'
      'Independent instruments applied to the three published EWSR1::NR4A3 direct targets</text>')
    a(f'<text x="{PAD}" y="63" font-size="13" fill="{C_MUTED}">'
      'Colour = whether that instrument supported the gene (see key). Columns are NOT comparable: '
      'each is its own quantity on its own scale.</text>')

    for i, (head, sub) in enumerate(COLS):
        x = PAD + LABEL_W + i * (cw + CELL_GAP)
        a(f'<text x="{x + cw/2:.1f}" y="{TOP - 30}" font-size="12.5" font-weight="600" '
          f'text-anchor="middle" fill="{C_TEXT}">{esc(head)}</text>')
        a(f'<text x="{x + cw/2:.1f}" y="{TOP - 14}" font-size="10.5" text-anchor="middle" '
          f'fill="{C_MUTED}">{esc(sub)}</text>')

    a(f'<line x1="{PAD}" y1="{TOP - 6}" x2="{W - PAD}" y2="{TOP - 6}" stroke="{C_RULE}"/>')

    for r, row in enumerate(rows):
        y = TOP + r * (CELL_H + CELL_GAP)
        a(f'<text x="{PAD}" y="{y + CELL_H/2 + 5:.1f}" font-size="15" font-weight="600" '
          f'font-style="italic" fill="{C_TEXT}">{esc(row["gene"])}</text>')
        for i, c in enumerate(row["cells"]):
            x = PAD + LABEL_W + i * (cw + CELL_GAP)
            fill = {"up": C_UP, "dir": C_DIR, "upweak": C_UP_WEAK,
                    "null": C_NULL, "absent": C_ABSENT}[c["kind"]]
            txt = "#ffffff" if c["kind"] in ("up", "dir") else C_TEXT
            sub = "#eef6f0" if c["kind"] in ("up", "dir") else C_MUTED
            a(f'<rect x="{x:.1f}" y="{y}" width="{cw:.1f}" height="{CELL_H}" rx="7" fill="{fill}"/>')
            if c["kind"] == "absent":
                a(f'<rect x="{x:.1f}" y="{y}" width="{cw:.1f}" height="{CELL_H}" rx="7" '
                  f'fill="none" stroke="#aab4c0" stroke-dasharray="4 3"/>')
            a(f'<text x="{x + cw/2:.1f}" y="{y + 32}" font-size="17" font-weight="600" '
              f'text-anchor="middle" fill="{txt}">{esc(c["top"])}</text>')
            if c["bot"]:
                a(f'<text x="{x + cw/2:.1f}" y="{y + 53}" font-size="11" text-anchor="middle" '
                  f'fill="{sub}">{esc(c["bot"])}</text>')

    ly = TOP + len(rows) * (CELL_H + CELL_GAP) + 22
    for i, (col, lab) in enumerate(((C_UP, "supported (q or p < 0.05)"),
                                    (C_DIR, "direction only — no test (n = 4)"),
                                    (C_UP_WEAK, "higher in EMC, not supported"),
                                    (C_NULL, "no support"))):
        lx = PAD + i * 232
        a(f'<rect x="{lx}" y="{ly - 11}" width="15" height="15" rx="3" fill="{col}"/>')
        a(f'<text x="{lx + 22}" y="{ly + 1}" font-size="11.5" fill="{C_MUTED}">{esc(lab)}</text>')
    # ⛔ Each caption line is kept under ~165 characters. At 11 px in a 940 px text area an
    # over-long line silently runs past the canvas edge -- it does not wrap, and SVG will not warn.
    for k, line in enumerate((
            'Array q-values: Benjamini–Hochberg over exact sample-label permutation p-values. The '
            '3SEQ cohort (n = 4) carries no test.',
            'The motif column is an exact-NBRE count against a dinucleotide-preserving null of the '
            'same window — sequence, never occupancy.',
            'No cell asserts that the fusion binds or drives any gene: every axis is correlative, '
            'and no NR4A3-fusion cistrome has been reported.')):
        a(f'<text x="{PAD}" y="{ly + 30 + k * 17}" font-size="11" fill="{C_MUTED}">{esc(line)}</text>')
    a('</svg>')
    return "\n".join(o) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true",
                    help="verify the committed SVG matches what the artifacts now produce")
    a = ap.parse_args(argv)
    svg = render(collect())
    if a.check:
        if not os.path.exists(OUT):
            print("no committed figure at %s" % OUT, file=sys.stderr)
            return 2
        if open(OUT).read() == svg:
            print("figure matches the committed artifacts")
            return 0
        print("⛔ the committed figure is STALE — regenerate it", file=sys.stderr)
        return 1
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as fh:
        fh.write(svg)
    print("wrote %s" % os.path.relpath(OUT, os.path.dirname(HERE)), file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
