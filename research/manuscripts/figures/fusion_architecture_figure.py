#!/usr/bin/env python3
"""
Figure 1 — EWSR1::NR4A3 fusion domain architecture (the structural basis of "undruggable but
degradable"). Dependency-free SVG from the committed AF2/fpocket assessment
(nr4a3-structure-assessment.json): disordered EWSR1 transactivation domain :: ordered NR4A3
DBD/hinge/LBD, with the fpocket Pocket-5 (the degrader warhead handle) marked.
"""
import json
import os

HERE = os.path.dirname(__file__)
OUT = os.path.join(HERE, "fusion-architecture.svg")
ASSESS = os.path.join(HERE, "..", "..", "modalities", "nr4a3-structure-assessment.json")

# fusion segments: (label, length_aa, ordered?, fill, accent, sublabel)
SEGMENTS = [
    ("EWSR1 SYGQ-rich prion-like / transactivation", 264, False, "#fdecdc", "#e8830c",
     "intrinsically disordered (pLDDT 38.8)"),
    ("NR4A3 DBD", 77, True, "#e8f0fe", "#1565c0", "Zn fingers (pLDDT 76)"),
    ("hinge", 35, True, "#eef2f7", "#7a8aa0", ""),
    ("NR4A3 ligand-binding domain", 254, True, "#e6f4ea", "#2e7d32", "ordered (pLDDT 85)"),
]
# fpocket Pocket-5 within the LBD (NR4A3 residues 406-534; LBD starts at 373)
POCKET_IN_LBD = (406 - 373, 534 - 373)   # offset within the 254-aa LBD segment
POCKET_DRUG = 0.495

W = 980
PAD = 28
TRACK_Y = 150
TRACK_H = 46
SCALE = (W - 2 * PAD) / sum(s[1] for s in SEGMENTS)


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def main():
    drug = POCKET_DRUG
    try:
        d = json.load(open(ASSESS))
        drug = d["NR4A3"]["fpocket"]["top_pocket_locale"]["druggability"]
    except Exception:
        pass

    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="320" '
         f'font-family="Helvetica,Arial,sans-serif" viewBox="0 0 {W} 320">',
         f'<rect width="{W}" height="320" fill="white"/>',
         f'<text x="{PAD}" y="40" font-size="19" font-weight="700">EWSR1::NR4A3 — a disordered '
         f'transactivation domain fused to an ordered NR4A3 LBD</text>',
         f'<text x="{PAD}" y="64" font-size="13" fill="#555">No druggable functional pocket '
         f'(best fpocket druggability {drug}, sub-threshold) — but the ordered LBD is retained, '
         f'giving a degrader a structural handle.</text>']

    x = PAD
    for label, length, ordered, fill, accent, sub in SEGMENTS:
        w = length * SCALE
        # disordered drawn with a wavy/dashed top to signal flexibility
        dash = '' if ordered else ' stroke-dasharray="5 3"'
        p.append(f'<rect x="{x:.1f}" y="{TRACK_Y}" width="{w:.1f}" height="{TRACK_H}" rx="5" '
                 f'fill="{fill}" stroke="{accent}" stroke-width="1.5"{dash}/>')
        # label (alternate above/below to avoid crowding)
        p.append(f'<text x="{x + w/2:.1f}" y="{TRACK_Y - 12}" font-size="11.5" font-weight="700" '
                 f'fill="#222" text-anchor="middle">{esc(label)}</text>')
        if sub:
            p.append(f'<text x="{x + w/2:.1f}" y="{TRACK_Y + TRACK_H + 18}" font-size="10" '
                     f'fill="#666" text-anchor="middle">{esc(sub)}</text>')
        # pocket marker inside the LBD
        if label.startswith("NR4A3 ligand"):
            px = x + POCKET_IN_LBD[0] * SCALE
            pw = (POCKET_IN_LBD[1] - POCKET_IN_LBD[0]) * SCALE
            p.append(f'<rect x="{px:.1f}" y="{TRACK_Y+8}" width="{pw:.1f}" height="{TRACK_H-16}" '
                     f'rx="3" fill="none" stroke="#c62828" stroke-width="2"/>')
            p.append(f'<text x="{px + pw/2:.1f}" y="{TRACK_Y + TRACK_H + 34}" font-size="9.5" '
                     f'fill="#c62828" text-anchor="middle">fpocket Pocket-5 (warhead handle)</text>')
        x += w

    # junction marker between EWSR1 and NR4A3
    jx = PAD + SEGMENTS[0][1] * SCALE
    p.append(f'<line x1="{jx:.1f}" y1="{TRACK_Y-4}" x2="{jx:.1f}" y2="{TRACK_Y+TRACK_H+4}" '
             f'stroke="#000" stroke-width="1.5"/>')
    p.append(f'<text x="{jx:.1f}" y="{TRACK_Y+TRACK_H+52}" font-size="10" font-weight="700" '
             f'text-anchor="middle">fusion junction</text>')

    # N/C termini
    p.append(f'<text x="{PAD}" y="{TRACK_Y-30}" font-size="11" fill="#999">N</text>')
    p.append(f'<text x="{W-PAD}" y="{TRACK_Y-30}" font-size="11" fill="#999" text-anchor="end">C</text>')
    p.append(f'<text x="{PAD}" y="300" font-size="9.5" fill="#999">Source: '
             f'nr4a3-structure-assessment.json (AlphaFold2/AFDB + fpocket). Lengths approximate; '
             f'dashed = intrinsically disordered.</text>')
    p.append('</svg>')
    open(OUT, "w").write("\n".join(p) + "\n")
    print("wrote", OUT)


if __name__ == "__main__":
    main()
