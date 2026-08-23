#!/usr/bin/env python3
"""Figure — how the seam residue is made, and why an out-of-frame junction ends early.

WHY THIS FIGURE. Two of the paper's results turn on one piece of arithmetic a reader currently has
to reconstruct from prose: the seam codon is assembled from leftover donor nucleotides plus the
acceptor exon's RETAINED 5' untranslated region, and its identity is what determines whether the
Section B5 isoform collision occurs. The same picture explains the out-of-frame case, where the
shifted register runs a few residues into a premature stop. An external reviewer asked for exactly
this diagram, naming the seam index, the retained 5'UTR and the in-frame/out-of-frame difference.

⛔ NOTHING IS COMPUTED HERE. Residue indices, the seam composition, the protein seam context and the
out-of-frame tract are read from `fusion-breakpoint-neoantigens.json` and
`junction-frameshift-peptides.json`. If a value here disagrees with the manuscript, the artifacts are
the arbiter.

⚠ IT DRAWS ONE IN-FRAME JUNCTION AND ONE OUT-OF-FRAME ONE, both named. It is not a picture of "the"
junction: five in-frame junctions exist, four of which carry an aspartate seam rather than this
one's asparagine, and that difference is the whole of B5.

Dependency-free SVG, per this directory's convention. Output: vaccine-junction-schematic.svg
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.join(HERE, "..", "..", "modalities")
BP = os.path.join(MOD, "fusion-breakpoint-neoantigens.json")
FS = os.path.join(MOD, "junction-frameshift-peptides.json")
OUT = os.path.join(HERE, "vaccine-junction-schematic.svg")

W, H = 720, 300
DONOR, ACC, SEAM, NOVEL = "#4a6fa5", "#7fa650", "#c0392b", "#b8860b"


def band(x, y, w, h, fill, label, sub=None):
    g = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" fill-opacity="0.20" '
         f'stroke="{fill}" stroke-width="1.3" rx="3"/>',
         f'<text x="{x+w/2:.0f}" y="{y+h/2+4:.0f}" font-size="12" fill="#1a1a1a" '
         f'text-anchor="middle">{label}</text>']
    if sub:
        g.append(f'<text x="{x+w/2:.0f}" y="{y+h+14:.0f}" font-size="10.5" fill="#555" '
                 f'text-anchor="middle">{sub}</text>')
    return g


def main():
    bp = json.load(open(BP))
    inf = [j for j in bp["junctions"] if j["EWSR1_exon_end"] == 7][0]
    oof = json.load(open(FS))["junctions"][0]

    j0 = inf["ewsr1_last_whole_residue"]
    comp = inf["seam_codon_composition"]
    utr = inf["nr4a3_acceptor_exon_5utr_nt_retained"]
    seam_res = inf["seam_codon_residue"]
    met1 = inf.get("nr4a3_met1_is_internal_residue")

    g = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
         f'font-family="Helvetica,Arial,sans-serif">',
         f'<rect width="{W}" height="{H}" fill="#ffffff"/>']

    # ---- panel a: in frame ----
    g.append('<text x="24" y="28" font-size="13" font-weight="bold" fill="#000">'
             'a  In frame — EWSR1 exon 7 :: NR4A3 exon 3</text>')
    y0 = 44
    g += band(24, y0, 250, 40, DONOR, "EWSR1 CDS through exon 7",
              f"ends mid-codon, {inf['ewsr1_coding_phase']} nt left over")
    g += band(274, y0, 46, 40, SEAM, seam_res, "seam")
    g += band(320, y0, 62, 40, ACC, f"5'UTR", f"{utr} nt retained")
    g += band(382, y0, 314, 40, ACC, "NR4A3 exon 3 onward, own reading frame",
              f"NR4A3 Met1 becomes internal residue {met1}")
    g.append(f'<text x="297" y="{y0-6}" font-size="11" fill="{SEAM}" text-anchor="middle">'
             f'j₀ = residue {j0}</text>')
    g.append(f'<text x="24" y="{y0+78}" font-size="11.5" fill="#333">'
             f'seam codon = {comp}; protein context '
             f'{inf["junction_context_protein_seam"]}</text>')

    # ---- panel b: out of frame ----
    g.append(f'<text x="24" y="{y0+118}" font-size="13" font-weight="bold" fill="#000">'
             f'b  Out of frame — EWSR1 exon 6 :: NR4A3 exon 3</text>')
    y1 = y0 + 134
    g += band(24, y1, 250, 40, DONOR, "EWSR1 CDS through exon 6", "cut leaves a different phase")
    g += band(274, y1, 200, 40, NOVEL, f"novel tract, {oof['novel_tract_length_aa']} aa",
              oof["novel_tract"])
    g.append(f'<rect x="474" y="{y1}" width="34" height="40" fill="#444" fill-opacity="0.85" '
             f'rx="3"/>')
    g.append(f'<text x="491" y="{y1+25}" font-size="13" fill="#fff" text-anchor="middle">*</text>')
    g.append(f'<text x="491" y="{y1+56}" font-size="10.5" fill="#555" text-anchor="middle">'
             f'premature stop</text>')
    if oof["nmd"]["nmd_predicted"]:
        g.append(f'<text x="518" y="{y1+18}" font-size="11" fill="#555">'
                 f'nonsense-mediated decay</text>')
        g.append(f'<text x="518" y="{y1+32}" font-size="11" fill="#555">'
                 f'predicted: stop is {oof["nmd"]["distance_upstream_nt"]:,} nt</text>')
        g.append(f'<text x="518" y="{y1+46}" font-size="11" fill="#555">'
                 f'upstream of the last junction</text>')

    g.append(f'<text x="24" y="{H-16}" font-size="11" fill="#666">'
             f'Predicted binding is a screen. Neither panel is evidence of presentation.</text>')
    g.append("</svg>")
    open(OUT, "w").write("\n".join(g))
    print(f"wrote {OUT} (seam {seam_res} at j0={j0}; oof tract {oof['novel_tract_length_aa']} aa)")


if __name__ == "__main__":
    main()
