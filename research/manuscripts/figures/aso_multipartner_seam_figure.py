#!/usr/bin/env python3
"""Figure — why one 16-mer spans three partners' junctions, and why two of the three are not
a patient's junction.

THE RESULT THIS HAS TO MAKE LEGIBLE. A single gapmer, 5'-GGGCATATCATCAAAC-3', is junction-spanning
and fusion-specific at EWSR1::NR4A3, TAF15::NR4A3 and FUS::NR4A3 at once. Stated as a sentence that
sounds like a coincidence. Drawn, the mechanism is visible in one line: the three donors' last ten
nucleotides before the breakpoint are identical, because EWSR1, TAF15 and FUS are FET-family
paralogues with similar low-complexity amino-termini, and the acceptor side is the same NR4A3 exon
in all three. The oligonucleotide's 16-nt window lies entirely inside that identity.

⛔⛔ THE LETTERS DRAWN ARE THE TARGET mRNA, NOT THE REAGENT, AND THE PANEL USED TO LEAVE THAT TO
INFERENCE (figure-integrity and order-safety review, 2026-08-19). `target = revcomp(OLIGO)`, so the
shaded window reads 5'-GTTTGATGATATGCCC-3' while the reagent is 5'-GGGCATATCATCAAAC-3'. Neither the
panel nor the caption said the rows were mRNA. A reader who transcribes the sixteen shaded letters
orders the SENSE strand of the target: a different molecule with no antisense activity, in a
document whose every other display item repeats a chemistry-and-orientation note. Every sequence row
is now labelled as target mRNA, the reagent is named beside the architecture with the relationship
between them stated, and the legend says it a third time.

⛔ AND THE TITLE ASSERTED WHAT THE CAPTION WITHDREW. It read "One 16-mer spans three partners'
breakpoints" while the caption said two of those three are carried by no reported patient — the
exon-resolved TAF15 breakpoints in this disease are at exon 6 rather than exon 11, and no
exon-resolved FUS breakpoint has been published at all. A title a caption withdraws is a title most
readers will keep, so the withdrawal is now IN the title and each row carries its own clinical tier,
read from `aso-per-junction-table.json` rather than restated here.

⚠ THE SAME PANEL MUST SHOW THE LIABILITY, NOT ONLY THE ASSET. The identity that lets one reagent
cover three fusions is the identity that makes the parent transcripts hard to discriminate from, and
a figure showing only the coverage would be selling the result. The divergent positions are marked,
the gap-level margin is printed, and the caption line says both things.

⛔ SEQUENCES ARE READ FROM `nr4a3-fusion-junction-atlas.json`, never typed. The seam strings, the
donor/acceptor split and the shared donor run all come from the artifact; this script aligns and
draws them, and it asserts the identity it claims rather than assuming it (see `_shared_prefix`).

Dependency-free SVG. No matplotlib, no network.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
from aso_figure_text import check_type_sizes, number_word, text_width, wrap  # noqa: E402

MOD = os.path.join(HERE, "..", "..", "modalities")
SRC = os.path.join(MOD, "nr4a3-fusion-junction-atlas.json")
#: The clinical tier of each junction, joined rather than restated. `aso_per_junction_table` owns
#: the whitelist of exon-resolved patient breakpoints; this figure must not carry a second copy.
TIERS = os.path.join(MOD, "aso-per-junction-table.json")
OUT = os.path.join(HERE, "aso-multipartner-seam.svg")

OLIGO = "GGGCATATCATCAAAC"          # the multi-partner lead reagent, looked up in the artifact
CW = 17                              # per-base cell width
W, T, L = 880, 84, 150

#: ⛔ 11 px IS THE PRINTED FLOOR AT THIS CANVAS. A 2026-08-19 review measured this figure's
#: architecture labels at 5.56 pt in the built PDF, because they were set at 9.5 px and the
#: renderers scale an 880-px canvas by about 0.198 mm/px. `check_type_sizes` turns that into a gate.
FS_TITLE, FS_SUB = 15, 12
FS_LABEL, FS_BASE, FS_TAG = 11.5, 13, 11.5
FS_ARCH, FS_NOTE, FS_MARK = 12, 11.5, 11.5

#: Tier token -> the words drawn beside a row. ⛔ A TOKEN WITH NO GLOSS RAISES rather than drawing an
#: empty tag: a new tier must be given words deliberately, not rendered as blank space beside a
#: sequence a reader is deciding whether to build.
TIER_WORDS = {
    "published_exon_resolved_breakpoint": "reported in patients at this exon",
    "partner_published_this_exon_not_reported": "partner reported, this exon not",
    "no_published_exon_resolved_breakpoint": "no exon-resolved report at all",
}
TIER_IS_REPORTED = "published_exon_resolved_breakpoint"


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def revcomp(s):
    return s.translate(str.maketrans("ACGTacgt", "TGCAtgca"))[::-1]


def _shared_prefix(seqs):
    """Length of the common SUFFIX of the donor halves — asserted, not assumed."""
    n = 0
    while all(len(s) > n and s[-(n + 1)] == seqs[0][-(n + 1)] for s in seqs):
        n += 1
    return n


def _tiers():
    with open(TIERS, encoding="utf-8") as fh:
        return {row["junction_label"]: row["clinical_tier"] for row in json.load(fh)["junctions"]}


def main(argv=None):
    d = json.load(open(SRC))
    entry = d["isoform_coverage"]["multi_partner_exact"][OLIGO]
    labels = [entry["designed_for"]] + list(entry["also_covers"])
    seams = {p["junction_label"]: p["seam_mRNA"] for p in d["panels"]}
    tiers = _tiers()
    for lab in labels:
        if lab not in tiers:
            raise SystemExit(f"{lab} has no clinical tier in {os.path.basename(TIERS)}")
        if tiers[lab] not in TIER_WORDS:
            raise SystemExit(f"{lab} carries tier {tiers[lab]!r}, which has no gloss in TIER_WORDS")
    n_reported = sum(1 for lab in labels if tiers[lab] == TIER_IS_REPORTED)

    donors, acceptors = [], []
    for lab in labels:
        dn, ac = seams[lab].split("|")
        donors.append(dn)
        acceptors.append(ac)

    shared = _shared_prefix(donors)
    assert all(a == acceptors[0] for a in acceptors), "acceptor halves differ; the figure's premise"
    target = revcomp(OLIGO)
    split = entry["seam_split_per_junction"][labels[0]]
    d_bases, a_bases = split["donor_bases"], split["acceptor_bases"]
    assert target == donors[0][-d_bases:] + acceptors[0][:a_bases], (
        "the oligonucleotide's target window is not the seam window the artifact records")

    #: The count of columns at which the donors actually differ — DERIVED, because the legend used
    #: to say "positions" (plural) over exactly one such column.
    n_divergent = sum(1 for c in range(len(donors[0]) - shared)
                      if any(donors[k][c] != donors[0][c] for k in range(len(donors))))
    divergent_words = ("the one position at which the three donors differ" if n_divergent == 1
                       else f"the {n_divergent} positions at which the three donors differ")

    ncols = len(donors[0]) + len(acceptors[0])
    tag_x = L + ncols * CW + 14
    tag_w = W - 32 - tag_x
    for lab in labels:
        wide = text_width(f"{lab.split('_')[0]} · {TIER_WORDS[tiers[lab]]}", FS_TAG)
        if wide > tag_w:
            raise SystemExit(f"the clinical tag for {lab} needs {wide:.0f} px and the gutter is "
                             f"{tag_w:.0f} px; widen the canvas or shorten TIER_WORDS")

    title = (f"One 16-mer spans three partners’ breakpoints — and only "
             f"{number_word(n_reported)} of the {number_word(len(labels))} is a junction any "
             f"patient is reported to carry")
    subtitle = (f"The three FET-family donors are identical over the {number_word(shared)} "
                f"nucleotides before the breakpoint, and the acceptor exon is the same in all "
                f"three. Every row is "
                f"TARGET mRNA, sense; the reagent is the reverse complement of the shaded window.")
    title_lines = wrap(title, FS_TITLE, W - 64)
    sub_lines = wrap(subtitle, FS_SUB, W - 64)

    y_title = 26
    y_sub = y_title + len(title_lines) * (FS_TITLE + 5) - 4
    top = y_sub + len(sub_lines) * (FS_SUB + 4) + 30      # first sequence row's baseline

    notes = [
        (f"Blue, donor exon; green, NR4A3 acceptor exon; boxed and red, {divergent_words}. "
         f"Shaded box, the window this reagent targets."),
        (f"Every sequence row above is the TARGET mRNA read 5′ to 3′, not the oligonucleotide. "
         f"The reagent is 5′-{OLIGO}-3′, the reverse complement of the shaded window "
         f"(5′-{target}-3′). Transcribing the shaded letters orders the sense strand, which is a "
         f"different molecule with no antisense activity."),
        (f"The same paralogy that lets one reagent cover three fusions is why these designs are "
         f"hard to discriminate from the parent transcripts: this reagent’s gap-level margin is "
         f"{number_word(entry['gap_specificity_margin'])} junction-unique bases inside the "
         f"{number_word(d['oligo_geometry']['gap'])}-nucleotide catalytic gap, the window "
         f"RNase-H1 cleaves. "
         f"Coverage is predicted from sequence and has not been measured."),
        #: ⛔ THE PANEL NAMES A SEQUENCE AND CARRIED NO HANDLING NOTE (figure-integrity and safety
        #: screens, 2026-08-19). Every table caption carries the chemistry-and-canonical-file note;
        #: this figure prints the lead reagent and three raw target windows and carried none, while
        #: being one of the most extractable elements in the document.
        ("Research use only, not for administration. The bases alone, ordered as unmodified DNA, "
         "are a different molecule; order from fusion-junction-aso-sequences.csv."),
    ]
    note_lines = [line for note in notes for line in wrap(note, FS_NOTE, W - 64)]

    gy = top + len(labels) * 30 + 26                      # the architecture bar
    y_notes = gy + 62
    H = int(y_notes + len(note_lines) * (FS_NOTE + 4) + 12)
    seam_x = L + len(donors[0]) * CW

    check_type_sizes(W, H, {
        "sequence rows": FS_BASE, "junction labels": FS_LABEL, "clinical tags": FS_TAG,
        "architecture labels": FS_ARCH, "notes": FS_NOTE, "markers": FS_MARK,
        "subtitle": FS_SUB, "title": FS_TITLE,
    })

    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
         f'viewBox="0 0 {W} {H}" font-family="Helvetica,Arial,sans-serif">',
         f'<rect width="{W}" height="{H}" fill="#ffffff"/>']
    for i, line in enumerate(title_lines):
        p.append(f'<text x="32" y="{y_title + i * (FS_TITLE + 5)}" font-size="{FS_TITLE}" '
                 f'fill="#111" font-weight="600">{esc(line)}</text>')
    for i, line in enumerate(sub_lines):
        p.append(f'<text x="32" y="{y_sub + i * (FS_SUB + 4)}" font-size="{FS_SUB}" fill="#555">'
                 f'{esc(line)}</text>')

    # what the rows ARE, said once above them and once per row below
    p.append(f'<text x="32" y="{top - 26}" font-size="{FS_MARK}" fill="#111" font-weight="600">'
             f'target mRNA (sense, 5′ to 3′)</text>')

    # the target window, shaded behind the sequence rows
    win_x0 = seam_x - d_bases * CW
    p.append(f'<rect x="{win_x0}" y="{top - 16}" width="{(d_bases + a_bases) * CW}" '
             f'height="{len(labels) * 30 + 8}" fill="#fff8e1" stroke="#f9a825" stroke-width="0.9"/>')

    for r, lab in enumerate(labels):
        y = top + r * 30
        gene = lab.split("_")[0]
        p.append(f'<text x="{L - 12}" y="{y}" font-size="{FS_LABEL}" fill="#111" text-anchor="end">'
                 f'{esc(lab.replace("__", "::").replace("_", " "))}</text>')
        row = donors[r] + acceptors[r]
        for c, base in enumerate(row):
            in_donor = c < len(donors[r])
            divergent = in_donor and c < len(donors[r]) - shared and any(
                donors[k][c] != base for k in range(len(donors)))
            fill = "#c62828" if divergent else ("#1565c0" if in_donor else "#2e7d32")
            weight = "700" if divergent else "400"
            # ⛔ COLOUR IS NOT THE ONLY CHANNEL, BECAUSE FOR TWO CLASSES OF READER IT CARRIES
            # NOTHING (2026-08-13). The three roles were encoded as blue donor / green acceptor /
            # red divergent, and the pair the reader most needs to separate — the green acceptor
            # bases and the red divergent ones — sit at almost the same relative luminance (0.18
            # against 0.15). That is the textbook red/green confusion for deuteranopia and
            # protanopia, about 8% of male readers, AND it collapses to the same grey when a
            # journal prints in black and white or a reader photocopies the page. Bold weight was
            # the only non-colour cue and 13px bold monospace is not a cue anyone reliably sees.
            # ⚠ A BOX, NOT A DIFFERENT PALETTE. Re-hueing would fix the colour-blind case and not
            # the greyscale one; a drawn rectangle is legible under both, and under neither does it
            # depend on the reader distinguishing anything at all.
            if divergent:
                p.append(f'<rect x="{L + c * CW + 0.6:.1f}" y="{y - 11}" '
                         f'width="{CW - 1.2:.1f}" height="14" rx="2" '
                         f'fill="none" stroke="#c62828" stroke-width="1.1"/>')
            p.append(f'<text x="{L + c * CW + CW / 2:.1f}" y="{y}" font-size="{FS_BASE}" '
                     f'fill="{fill}" font-family="monospace" font-weight="{weight}" '
                     f'text-anchor="middle">{esc(base)}</text>')
        #: ⛔ THE CLINICAL TIER IS WORDS, NOT A COLOUR. Two of the three seams drawn here are
        #: carried by no reported patient, and a figure lifted out of the paper has to say so on
        #: the row rather than in a caption a reader may not have. Text is the channel that
        #: survives greyscale, photocopying and colour-blindness alike.
        reported = tiers[lab] == TIER_IS_REPORTED
        p.append(f'<text x="{tag_x}" y="{y}" font-size="{FS_TAG}" '
                 f'fill="{"#2e7d32" if reported else "#b71c1c"}">'
                 f'{esc(gene)} · {esc(TIER_WORDS[tiers[lab]])}</text>')

    # seam marker
    p.append(f'<line x1="{seam_x}" y1="{top - 20}" x2="{seam_x}" y2="{top + len(labels) * 30 - 6}" '
             f'stroke="#111" stroke-width="1.4"/>')
    p.append(f'<text x="{seam_x}" y="{top - 26}" font-size="{FS_MARK}" fill="#111" '
             f'text-anchor="middle" font-weight="600">breakpoint</text>')

    # the gapmer architecture under the window
    geom = d["oligo_geometry"]
    wing, gap = geom["wing"], geom["gap"]
    segs = [("LNA wing", wing, "#90a4ae"), ("DNA gap", gap, "#ef6c00"),
            ("LNA wing", wing, "#90a4ae")]
    sx = win_x0
    for name, ln, col in segs:
        #: ⛔ THE LABEL HAS TO FIT THE SEGMENT IT NAMES. "DNA gap (RNase-H1)" at a legible size does
        #: not fit six cells, and the previous fix for that was to set it at 9.5 px — which printed
        #: at 5.56 pt. The enzyme moved to the note; the bar carries the name that fits.
        if text_width(name, FS_ARCH) > ln * CW:
            raise SystemExit(f"architecture label {name!r} needs "
                             f"{text_width(name, FS_ARCH):.0f} px and its segment is {ln * CW} px")
        p.append(f'<rect x="{sx}" y="{gy}" width="{ln * CW}" height="18" fill="{col}" '
                 f'opacity="0.85" stroke="#ffffff"/>')
        p.append(f'<text x="{sx + ln * CW / 2:.1f}" y="{gy + 13}" font-size="{FS_ARCH}" '
                 f'fill="#ffffff" text-anchor="middle">{esc(name)}</text>')
        sx += ln * CW
    p.append(f'<text x="{win_x0}" y="{gy + 36}" font-size="{FS_ARCH}" fill="#333">'
             f'reagent 5′-{esc(OLIGO)}-3′ (antisense), {esc(d_bases)} donor and {esc(a_bases)} '
             f'acceptor bases either side of the seam</text>')

    # ⛔ THE CAPTION DESCRIBED A CUE THE FIGURE NO LONGER USED (2026-08-13). It read "red and bold"
    # after the boxes above were added precisely BECAUSE bold weight is not a cue a reader reliably
    # sees — so the figure's own legend sent a greyscale or colour-blind reader looking for the one
    # distinction it had been redrawn to stop relying on. A figure that describes itself wrongly is
    # worse than one that describes itself thinly, because the reader trusts the legend.
    for i, line in enumerate(note_lines):
        p.append(f'<text x="32" y="{y_notes + i * (FS_NOTE + 4)}" font-size="{FS_NOTE}" '
                 f'fill="#666">{esc(line)}</text>')
    p.append('</svg>')

    with open(OUT, "w") as fh:
        fh.write("\n".join(p) + "\n")
    print(f"wrote {OUT}  {W} x {H} px (shared donor run {shared} nt: {donors[0][-shared:]}; "
          f"{n_divergent} divergent column(s); gap margin {entry['gap_specificity_margin']}; "
          f"reported at {n_reported} of {len(labels)} seams)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
