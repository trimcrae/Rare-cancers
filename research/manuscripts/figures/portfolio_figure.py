#!/usr/bin/env python3
"""
Generate the prioritized-portfolio figure for the EMC treatment roadmap paper (Figure 2).

Dependency-free: emits a self-contained SVG (renders in any browser / converts to PDF/PNG with
rsvg/inkscape). Data mirror the verified tracker (emc-treatment-strategy.md). Re-run to regenerate.
"""
import os

OUT = os.path.join(os.path.dirname(__file__), "portfolio.svg")

# evidence classes -> (fill, accent)
CLS = {
    "emc":   ("#e6f4ea", "#2e7d32"),   # EMC clinical / ex-vivo evidence
    "silico":("#e8f0fe", "#1565c0"),   # in-silico / surrogate evidence
    "hyp":   ("#fff4e5", "#e8830c"),   # mechanistic hypothesis
    "down":  ("#f1f1f1", "#9e9e9e"),   # down-weighted
}
TIERS = [
    ("Tier 1", "Actionable now — approved drugs, EMC evidence", [
        ("TKI + checkpoint inhibitor", "ImmunoSarc: an EMC partial response", "emc"),
        ("Trabectedin", "EMC responder + fusion-TF mechanism", "emc"),
        ("Carfilzomib + anthracycline", "active across 2 patient-derived EMC models", "emc"),
    ]),
    ("Tier 2", "Driver-directed, high ceiling", [
        ("NR4A3 degrader (PROTAC)", "addiction supported: FLI1/Ewing -0.93, 74%", "silico"),
    ]),
    ("Tier 3", "Surface / antigen — surrogate-supported", [
        ("B7-H3 (CD276) ADC / CAR-T", "99% of sarcoma lines express it", "silico"),
        ("PRAME (ImmTAC / CAR)", "53%; high in myxoid 7.6 / synovial 7.2", "silico"),
        ("FAP radioligand therapy", "EMC myxoid stroma; pan-sarcoma signal", "hyp"),
    ]),
    ("Tier 4", "Down-weighted with data / logic", [
        ("TCR-T / ImmTAC (NY-ESO/MAGE-A4)", "EMC is CTA-low (5-7%)", "down"),
        ("Synthetic-lethal / BRD9", "DepMap: not sarcoma-selective", "down"),
        ("Fusion-junction vaccine", "self-adjacent junction, cold tumour", "down"),
    ]),
]

W = 980
LABEL_W = 188
PAD = 22
CARD_W, CARD_H, GAP = 236, 66, 14
ROW_GAP = 18
TOP = 96


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def main():
    parts = []
    y = TOP
    row_tops = []
    for _, _, cands in TIERS:
        row_tops.append(y)
        rows = (len(cands) + 2) // 3  # up to 3 cards/row
        y += rows * CARD_H + (rows - 1) * GAP + ROW_GAP + 10
    height = y + 90

    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{height}" '
        f'font-family="Helvetica,Arial,sans-serif" viewBox="0 0 {W} {height}">')
    parts.append(f'<rect width="{W}" height="{height}" fill="white"/>')
    parts.append(f'<text x="{PAD}" y="40" font-size="22" font-weight="700">Prioritized treatment-route '
                 f'portfolio for EWSR1::NR4A3 EMC</text>')
    parts.append(f'<text x="{PAD}" y="64" font-size="13" fill="#555">Ranked by likelihood of patient '
                 f'benefit x near-term feasibility; computation-only triage (no wet lab).</text>')

    for (tname, tdesc, cands), ytop in zip(TIERS, row_tops):
        parts.append(f'<text x="{PAD}" y="{ytop+22}" font-size="15" font-weight="700">{esc(tname)}</text>')
        # wrap the descriptor under the tier name
        parts.append(f'<text x="{PAD}" y="{ytop+40}" font-size="10.5" fill="#666">'
                     f'<tspan x="{PAD}" dy="0">{esc(tdesc[:26])}</tspan>'
                     f'<tspan x="{PAD}" dy="13">{esc(tdesc[26:])}</tspan></text>')
        for i, (name, ev, cls) in enumerate(cands):
            col = i % 3
            row = i // 3
            x = LABEL_W + col * (CARD_W + GAP)
            cy = ytop + row * (CARD_H + GAP)
            fill, accent = CLS[cls]
            parts.append(f'<rect x="{x}" y="{cy}" width="{CARD_W}" height="{CARD_H}" rx="7" '
                         f'fill="{fill}" stroke="{accent}" stroke-width="1"/>')
            parts.append(f'<rect x="{x}" y="{cy}" width="5" height="{CARD_H}" rx="2" fill="{accent}"/>')
            parts.append(f'<text x="{x+14}" y="{cy+26}" font-size="12.5" font-weight="700" '
                         f'fill="#1a1a1a">{esc(name)}</text>')
            parts.append(f'<text x="{x+14}" y="{cy+46}" font-size="10.5" fill="#444">{esc(ev)}</text>')

    # legend
    ly = height - 50
    legend = [("emc", "EMC clinical/ex-vivo evidence"), ("silico", "in-silico / surrogate evidence"),
              ("hyp", "mechanistic hypothesis"), ("down", "down-weighted with data")]
    lx = PAD
    for cls, lab in legend:
        fill, accent = CLS[cls]
        parts.append(f'<rect x="{lx}" y="{ly}" width="16" height="16" rx="3" fill="{fill}" stroke="{accent}"/>')
        parts.append(f'<text x="{lx+22}" y="{ly+13}" font-size="11" fill="#333">{esc(lab)}</text>')
        lx += 30 + len(lab) * 6.4
    parts.append(f'<text x="{PAD}" y="{height-18}" font-size="9.5" fill="#999">Source: '
                 f'research/manuscripts/emc-treatment-strategy.md + depmap-insilico-findings.md. '
                 f'Nothing here is wet-lab validated.</text>')
    parts.append('</svg>')

    with open(OUT, "w") as fh:
        fh.write("\n".join(parts) + "\n")
    print("wrote", OUT)


if __name__ == "__main__":
    main()
