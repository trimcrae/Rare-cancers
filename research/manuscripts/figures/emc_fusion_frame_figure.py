#!/usr/bin/env python3
"""
Figure 1 of emc-atr-collaborator-package.md — fusion architecture, the recruitment axis drawn as
what is known, and the type-2 seam at nucleotide resolution.

The manuscript carried seven tables and no figure, in a paper about protein architecture, and its
one novel result had no display item at all. Three panels, all from committed artifacts:

  A  EWSR1, TAF15 and NR4A3 to scale, with every RG dipeptide drawn at its measured position and
     the operational RGG boxes bracketed; then each reported fusion's retained 5' segment on the
     same ruler, so which RG ticks fall inside a retained segment is visible rather than tabulated.
  B  The retained-RG axis. The two firmly measured points are drawn as filled markers; the
     EWSR1::ATF1 comparator is drawn as a span, because the source built one construct and does not
     state its breakpoint; the middle add-back anchor is drawn as an unplaceable band, because the
     source does not identify which domain it reintroduced. The EMC constructs are computed
     placements in a distinct open style.
  C  The type-2 seam. EWSR1 coding sequence ends one nucleotide into a codon at 793; that base plus
     176 nt of NR4A3 5' untranslated sequence (174 of exon 2, 2 of exon 3) complete 59 codons before
     NR4A3's own initiator. The translated residues are printed beneath.

GREYSCALE-SAFE BY CONSTRUCTION. Nothing is distinguished by hue: fills are lightness steps, and
categories are separated by marker shape, outline weight and hatching. A journal's colour charge is
therefore avoidable without a redraw, and a photocopy carries the same information.

    python3 research/manuscripts/figures/emc_fusion_frame_figure.py
    python3 research/manuscripts/figures/emc_fusion_frame_figure.py --check   # provenance only
"""
import argparse
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
MOD = os.path.join(REPO, "research", "modalities")
STEM = os.path.join(HERE, "emc-fusion-frame-fig1")
PROVENANCE = os.path.join(HERE, "emc-atr-figure-provenance.json")

SOURCES = [
    os.path.join(MOD, "emc-construct-inputs.json"),
    os.path.join(MOD, "emc-fet-construct-designs.json"),
    os.path.join(MOD, "emc-fet-frame-and-composition.json"),
]

INK = "#111111"
MID = "#555555"
LIGHT = "#d9d9d9"
PALE = "#f0f0f0"


def load():
    inputs = json.load(open(SOURCES[0], encoding="utf-8"))
    designs = json.load(open(SOURCES[1], encoding="utf-8"))
    extra = json.load(open(SOURCES[2], encoding="utf-8"))
    return inputs, designs, extra


def stamp():
    out = {}
    for p in SOURCES:
        with open(p, "rb") as fh:
            out[os.path.basename(p)] = hashlib.sha256(fh.read()).hexdigest()[:16]
    return out


def write_provenance():
    rec = {
        "_regenerate": "python3 research/manuscripts/figures/emc_fusion_frame_figure.py",
        "_what": "content hashes of every artifact this figure was drawn from",
        "_why": "nothing in CI redraws the figure, so these hashes are the only way a reader can "
                "tell a stale figure from a current one. A number changed in an artifact and not "
                "redrawn is a stale figure, and the fix is to redraw it, never to re-stamp.",
        "_greyscale": "no category is encoded by hue; fills are lightness steps and categories are "
                      "separated by marker shape, outline weight and hatching",
        "figures": ["emc-fusion-frame-fig1.pdf", "emc-fusion-frame-fig1.png"],
        "sources": stamp(),
    }
    with open(PROVENANCE, "w", encoding="utf-8") as fh:
        json.dump(rec, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    return rec


# ── drawing ───────────────────────────────────────────────────────────────────────────────────
def draw(inputs, designs, extra):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle
    from matplotlib.gridspec import GridSpec

    rg = extra["composition"]["rg_content"]
    seam = extra["type2_seam"]
    axis = extra["recruitment_axis_rows"]

    fig = plt.figure(figsize=(7.4, 8.9))
    gs = GridSpec(3, 1, height_ratios=[3.15, 1.30, 1.60], hspace=0.50,
                  left=0.245, right=0.985, top=0.965, bottom=0.045)

    def panel_letter(ax, letter, x=-0.235):
        ax.text(x, 1.02, letter, transform=ax.transAxes, fontsize=11, fontweight="bold",
                va="bottom", ha="left")

    # -- Panel A -------------------------------------------------------------------------------
    axA = fig.add_subplot(gs[0])
    xmax = 700
    axA.set_xlim(-8, xmax)
    axA.set_ylim(-0.35, 10.5)
    axA.set_yticks([])
    axA.set_xlabel("residue", fontsize=8.4)
    axA.tick_params(axis="x", labelsize=7.6)
    for s in ("top", "right", "left"):
        axA.spines[s].set_visible(False)

    bar_h = 0.46

    def protein(y, name, length, ticks, boxes, note=None):
        axA.add_patch(Rectangle((0, y), length, bar_h, facecolor=PALE, edgecolor=INK, lw=0.9))
        for t in ticks:
            axA.plot([t, t], [y, y + bar_h], color=INK, lw=0.55, solid_capstyle="butt")
        for b0, b1 in boxes:
            axA.add_patch(Rectangle((b0, y - 0.13), b1 - b0, bar_h + 0.26, facecolor="none",
                                    edgecolor=INK, lw=1.3, linestyle=(0, (3, 1.6))))
        axA.text(-14, y + bar_h / 2, name, ha="right", va="center", fontsize=8.4, color=INK)
        if note:
            axA.text(length + 10, y + bar_h / 2, note, ha="left", va="center", fontsize=7.0,
                     color=MID)

    protein(9.62, "EWSR1", 656, rg["EWSR1"]["rg_positions"], [(300, 332), (455, 638)], "30 RG")
    protein(8.72, "TAF15", 592, rg["TAF15"]["rg_positions"], [(326, 572)], "31 RG")

    yn = 7.82
    axA.add_patch(Rectangle((0, yn), 626, bar_h, facecolor=PALE, edgecolor=INK, lw=0.9))
    zf = designs["nr4a3_landmarks_read_from_the_audit"]["c4_zinc_finger_first_cysteine"]
    lbd = designs["nr4a3_landmarks_read_from_the_audit"]["lbd_start"]
    axA.add_patch(Rectangle((zf, yn), lbd - zf, bar_h, facecolor=LIGHT, edgecolor=INK, lw=0.9))
    axA.add_patch(Rectangle((lbd, yn), 626 - lbd, bar_h, facecolor="#b0b0b0", edgecolor=INK,
                            lw=0.9))
    for t in rg["NR4A3"]["rg_positions"]:
        axA.plot([t, t], [yn, yn + bar_h], color=INK, lw=0.55)
    axA.text(-14, yn + bar_h / 2, "NR4A3", ha="right", va="center", fontsize=8.4, color=INK)
    axA.text(636, yn + bar_h / 2, "2 RG", ha="left", va="center", fontsize=7.0, color=MID)
    axA.plot([166, 166], [yn, yn + bar_h], color=INK, lw=1.6)
    axA.text(166, yn + bar_h + 0.07, "C166", ha="center", va="bottom", fontsize=6.8, color=INK)
    axA.text(146, yn - 0.10, "AF-1", ha="center", va="top", fontsize=6.8, color=MID)
    axA.text((zf + lbd) / 2, yn - 0.10, "C4 zinc finger", ha="center", va="top",
             fontsize=6.8, color=MID)
    axA.text((lbd + 626) / 2, yn - 0.10, "ligand-binding domain", ha="center", va="top",
             fontsize=6.8, color=MID)

    axA.plot([-8, xmax], [7.16, 7.16], color=MID, lw=0.6, linestyle=(0, (2, 2)))

    cuts = [
        ("EWSR1::NR4A3 type 1", "EWSR1", 431, "8 of 30 RG"),
        ("EWSR1::NR4A3 type 2", "EWSR1", 264, "0 of 30 RG"),
        ("EWSR1::NR4A3 type 5", "EWSR1", 472, "11 of 30 RG"),
        ("TAF15::NR4A3", "TAF15", 161, "0 of 31 RG"),
        ("EWSR1::ATF1, exon 8", "EWSR1", 324, "7 of 30 RG"),
        ("EWSR1::ATF1, exon 10", "EWSR1", 348, "8 of 30 RG"),
        ("EWSR1::FLI1, type 1", "EWSR1", 264, "0 of 30 RG"),
    ]
    axA.text(-14, 6.86, "retained 5' segment", ha="right", va="center", fontsize=7.2, color=MID,
             style="italic")
    y = 6.20
    for label, parent, cut, note in cuts:
        axA.add_patch(Rectangle((0, y), cut, bar_h, facecolor=PALE, edgecolor=INK, lw=0.9))
        for t in rg[parent]["rg_positions"]:
            if t <= cut:
                axA.plot([t, t], [y, y + bar_h], color=INK, lw=0.55, solid_capstyle="butt")
        axA.plot([cut, cut], [y - 0.15, y + bar_h + 0.15], color=INK, lw=1.1)
        axA.text(-14, y + bar_h / 2, label, ha="right", va="center", fontsize=7.5, color=INK)
        axA.text(cut + 10, y + bar_h / 2, f"{parent}(1-{cut}), {note}", ha="left", va="center",
                 fontsize=6.9, color=MID)
        y -= 0.88
    panel_letter(axA, "A")

    # -- Panel B -------------------------------------------------------------------------------
    axB = fig.add_subplot(gs[1])
    axB.set_xlim(-0.03, 1.04)
    axB.set_ylim(0, 1)
    axB.set_yticks([])
    axB.set_xticks([0, 0.25, 0.5, 0.75, 1.0])
    axB.tick_params(axis="x", labelsize=7.6)
    axB.set_xlabel("retained RG dipeptides, as a fraction of the 5' partner's wild-type total",
                   fontsize=8.0)
    for s in ("top", "right", "left"):
        axB.spines[s].set_visible(False)

    rows = [(0.82, "measured in\nreference 1"),
            (0.53, "reported EWSR1::ATF1\nbreakpoints"),
            (0.20, "computed here,\nEMC fusions")]
    for yr, lab in rows:
        axB.text(-0.055, yr, lab, ha="right", va="center", fontsize=7.0, color=MID,
                 linespacing=1.4)

    axB.add_patch(Rectangle((0.0, 0.745), 1.0, 0.15, facecolor="none", edgecolor=MID, lw=0.8,
                            hatch="////"))
    axB.text(0.5, 0.925, "one-domain add-back construct: position on this axis not determinable",
             ha="center", va="bottom", fontsize=6.9, color=MID)
    axB.plot([0.0, 1.0], [0.82, 0.82], marker="o", linestyle="none", markersize=6.8,
             markerfacecolor=INK, markeredgecolor=INK, zorder=5)

    lo, hi = axis["atf1_comparator_span"]
    axB.plot([lo, hi], [0.53, 0.53], color=INK, lw=2.2, solid_capstyle="butt")
    for x in (lo, 0.233, hi):
        axB.plot([x, x], [0.485, 0.575], color=INK, lw=1.5)
    axB.text(hi + 0.025, 0.53, "0.000 to 0.267; the breakpoint of the measured construct is not "
             "stated", ha="left", va="center", fontsize=6.9, color=INK)

    placed = [(0.000, "type 2 and\nTAF15::NR4A3", "left"), (0.267, "type 1", "center"),
              (0.367, "type 5", "center")]
    axB.plot([v for v, _, _ in placed], [0.20] * len(placed), marker="^", linestyle="none",
             markersize=7.2, markerfacecolor="white", markeredgecolor=INK, markeredgewidth=1.2)
    for v, lab, ha in placed:
        axB.text(v + (0.014 if ha == "left" else 0), 0.265, lab, ha=ha, va="bottom",
                 fontsize=6.9, color=INK, linespacing=1.35)
    axB.text(0.0, 0.10, "fusion reference construct", ha="left", va="top", fontsize=6.9,
             color=MID)
    axB.text(1.0, 0.10, "native EWSR1 and the three-domain add-back", ha="right", va="top",
             fontsize=6.9, color=MID)
    panel_letter(axB, "B")

    # -- Panel C -------------------------------------------------------------------------------
    axC = fig.add_subplot(gs[2])
    axC.set_xlim(-46, 252)
    axC.set_ylim(0, 1)
    axC.axis("off")

    ytop, hgt = 0.60, 0.135
    blocks = [(-42, 42, PALE, None), (0, 1, "#7a7a7a", None), (1, 174, "white", "...."),
              (175, 2, "white", "xxxx"), (177, 66, LIGHT, None)]
    for x, w, fc, hatch in blocks:
        axC.add_patch(Rectangle((x, ytop), w, hgt, facecolor=fc, edgecolor=INK, lw=0.9,
                                hatch=hatch))
    axC.text(-21, ytop + hgt + 0.045, "EWSR1 exon 7,\ncoding through nt 793", ha="center",
             va="bottom", fontsize=6.9, color=INK, linespacing=1.35)
    axC.text(88, ytop + hgt + 0.045, "NR4A3 exon 2, 174 nt,\nuntranslated in NR4A3",
             ha="center", va="bottom", fontsize=6.9, color=INK, linespacing=1.35)
    axC.text(210, ytop + hgt + 0.045, "NR4A3 coding sequence,\nfrom its own initiator",
             ha="center", va="bottom", fontsize=6.9, color=INK, linespacing=1.35)
    axC.annotate("2 nt of exon 3", xy=(176, ytop + hgt), xytext=(176, 0.985),
                 fontsize=6.9, color=INK, ha="center", va="top",
                 arrowprops=dict(arrowstyle="-", lw=0.7, color=INK))
    axC.annotate("one nucleotide donated by EWSR1", xy=(0.5, ytop), xytext=(-46, 0.375),
                 fontsize=6.9, color=INK, ha="left", va="center",
                 arrowprops=dict(arrowstyle="-", lw=0.7, color=INK))

    ycomb = 0.505
    for i in range(60):
        axC.plot([i * 3, i * 3], [ycomb, ycomb + 0.05], color=MID, lw=0.4)
    axC.plot([0, 177], [ycomb, ycomb], color=INK, lw=1.0)
    axC.plot([177, 177], [ycomb, ytop + hgt], color=INK, lw=0.7, linestyle=(0, (2, 2)))
    axC.text(120, 0.375, "59 codons, 177 nt, no internal stop codon", ha="center", va="center",
             fontsize=6.9, color=INK)

    seq = seam["extra_residue_sequence"]
    axC.text(-46, 0.235, "residues 265 to 323 of the chimeric protein, read in the EWSR1 frame:",
             ha="left", va="top", fontsize=6.9, color=INK)
    axC.text(-46, 0.155, seq[:30] + "\n" + seq[30:], ha="left", va="top", fontsize=7.8,
             color=INK, family="monospace", linespacing=1.5)
    panel_letter(axC, "C", x=-0.005)

    return fig


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true",
                    help="compare the committed provenance stamp against the artifacts on disk")
    a = ap.parse_args(argv)

    if a.check:
        if not os.path.exists(PROVENANCE):
            print("::error::no provenance record at %s" % os.path.relpath(PROVENANCE, REPO))
            return 1
        have = json.load(open(PROVENANCE, encoding="utf-8"))["sources"]
        if have != stamp():
            print("STALE — an artifact changed since the figure was drawn; redraw it")
            return 1
        print("PROVENANCE MATCHES")
        return 0

    inputs, designs, extra = load()
    fig = draw(inputs, designs, extra)
    for ext in ("png", "pdf"):
        fig.savefig(f"{STEM}.{ext}", dpi=300, facecolor="white", edgecolor="none")
    write_provenance()
    print(f"wrote {os.path.relpath(STEM, REPO)}.png, .pdf and "
          f"{os.path.relpath(PROVENANCE, REPO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
