#!/usr/bin/env python3
"""Pin each ASO figure to the artifact revision it was drawn from. ($0, offline.)

⛔ WHY THIS EXISTS. On 2026-08-13 Figure 3's legend was found to disagree with Figure 3. The legend
said 125 design records collapse to 114 molecules, 77 at or below the chance band and 37 above, from
six multi-seam designs; the artifact said 190 records, 176 molecules, 125 at or below, 51 above,
nine multi-seam — and the rendered SVG printed the artifact's numbers, because the drawing script
computes nothing. So the figure was right, the prose beside it was wrong, and the manuscript shipped
both for as long as nobody read them side by side.

⛔⛔ AND NOTHING COULD HAVE CAUGHT IT. `figure-provenance.json` covers the `nr4a3-fusion-targets`
set only; the three ASO figures had no provenance record at all, so there was no revision to compare
a figure against and no check that would go red when its source moved. `check_figure_specs.py` reads
dpi, format and printed width — it cannot know whether a figure is stale.

★ WHAT THIS CHECKS, AND WHAT IT CANNOT. It records the content hash of every artifact each figure
reads, so `--check` fails when an artifact has moved since the figure was last drawn. That is a
staleness detector, not a correctness one: it cannot tell whether a legend describes its figure, only
whether the figure describes the current artifact. The legend is held by
`tests/test_aso_submission_numbers.py::test_the_figure_3_legend_matches_the_series_it_describes`,
which asserts the manuscript's numbers against `figure_series` directly. The two together close the
loop the Figure 3 defect went through: artifact -> figure (this file), artifact -> legend (that test).

    python3 research/manuscripts/figures/aso_figure_provenance.py
    python3 research/manuscripts/figures/aso_figure_provenance.py --check
"""
from __future__ import annotations

import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.join(HERE, "..", "..", "modalities")
OUT = os.path.join(HERE, "aso-figure-provenance.json")

#: figure stem -> the artifacts its drawing script reads. Kept beside the scripts rather than
#: derived from them, because a script that stopped reading an artifact would silently shrink a
#: derived list and the check would pass by covering less.
FIGURES = {
    "aso-junction-space": ["nr4a3-fusion-junction-atlas.json"],
    # ⚠ THREE ATLASES, NOT ONE, AND THAT IS THE WHOLE POINT OF THE FIGURE. It draws the identity
    # across 5-6-5, 5-8-5 and 5-10-5, so a change to ANY geometry's atlas makes it stale. Listing
    # only the 16-mer here would leave the two panels that carry the argument unwatched.
    "aso-gap-length-tradeoff": [
        "nr4a3-fusion-junction-atlas.json",
        "nr4a3-fusion-junction-atlas-18mer-5-8-5.json",
        "nr4a3-fusion-junction-atlas-20mer-5-10-5.json",
    ],
    "aso-multipartner-seam": ["nr4a3-fusion-junction-atlas.json"],
    "aso-chance-baseline": ["offtarget-chance-baseline.json"],
}

#: figure stem -> the script that draws it.
#:
#: ⛔ WHY THIS IS DECLARED RATHER THAN LEFT INSIDE A PROSE RECIPE (2026-08-17). The `_regenerate`
#: line this feeds was a hand-typed string naming THREE generators, and there are four. Following it
#: redrew the junction-space, seam and chance-baseline panels, then ran this module, which re-pinned
#: the hashes of ALL FOUR — including `aso-gap-length-tradeoff`, whose SVG had not been redrawn. So
#: the one instrument that exists to distinguish a stale figure from a current one would have
#: certified a stale one as current, and gone green doing it. `scripts/regenerate_aso_chain.sh` had
#: the same three-of-four omission, from the same missing fact.
#:
#: The recipe below is now derived from this map, the chain script is asserted against it by
#: `tests/test_aso_figure_chain_is_complete.py`, and `_assert_every_figure_has_a_generator` refuses
#: to write a record at all if a fifth figure is ever added without one — because the failure mode
#: is not a missing figure, it is a hash pinned over a drawing nobody made.
GENERATORS = {
    "aso-junction-space": "aso_junction_space_figure.py",
    "aso-gap-length-tradeoff": "aso_gap_length_figure.py",
    "aso-multipartner-seam": "aso_multipartner_seam_figure.py",
    "aso-chance-baseline": "aso_chance_baseline_figure.py",
}

#: Run after every panel, in this order: the rasteriser turns whatever the drawing scripts just
#: wrote into the PDF/PNG a portal wants, and this module pins the hashes only once both have run.
FIGURE_POSTSTEPS = ("svg_to_submission_formats.py", "aso_figure_provenance.py")


def _assert_every_figure_has_a_generator():
    orphans = sorted(set(FIGURES) - set(GENERATORS))
    if orphans:
        raise SystemExit(
            "⛔ these figures have provenance pinned but no declared generator: "
            + ", ".join(orphans)
            + "\n   Pinning a hash for a figure nobody redraws is how a stale panel passes --check."
            + "\n   Add each to GENERATORS in this file, and add its step to "
              "scripts/regenerate_aso_chain.sh.")
    strays = sorted(set(GENERATORS) - set(FIGURES))
    if strays:
        raise SystemExit("⛔ GENERATORS names figures that have no provenance entry: "
                         + ", ".join(strays))
    for stem, script in sorted(GENERATORS.items()):
        if not os.path.exists(os.path.join(HERE, script)):
            raise SystemExit(f"⛔ {stem}: declared generator {script} does not exist")


def regenerate_recipe():
    """The command that actually rebuilds every figure this module pins — all of them."""
    scripts = [GENERATORS[stem] for stem in sorted(FIGURES)] + list(FIGURE_POSTSTEPS)
    return " && ".join(f"python3 research/manuscripts/figures/{s}" for s in scripts)


def _hash(path):
    """Content hash of an artifact, or None if it is absent.

    ⚠ ABSENT IS NOT ZERO. A missing artifact records `null` rather than the hash of empty bytes, so a
    later run cannot report "unchanged" about a file that was never there. An absent reading is not a
    reading of absence.
    """
    if not os.path.exists(path):
        return None
    return hashlib.sha256(open(path, "rb").read()).hexdigest()[:16]


def _sources():
    out = {}
    for names in FIGURES.values():
        for name in names:
            out[name] = _hash(os.path.join(MOD, name))
    return dict(sorted(out.items()))


def _record():
    return {
        "_what": f"content hashes of every artifact the {len(FIGURES)} ASO figures were drawn from",
        "_why": ("nothing in CI regenerates these figures, so a reader cannot otherwise tell a "
                 "stale figure from a current one. `--check` compares these hashes against the "
                 "artifacts on disk."),
        "_regenerate": regenerate_recipe(),
        "_what_this_does_not_check": ("whether a figure's LEGEND in the manuscript describes the "
                                     "figure. That is a separate failure and it happened: see this "
                                     "module's docstring and test_aso_submission_numbers.py."),
        "figures": {stem: sorted(names) for stem, names in sorted(FIGURES.items())},
        "rendered": sorted(
            f"{stem}{ext}" for stem in FIGURES for ext in (".svg", ".pdf", ".png")
            if os.path.exists(os.path.join(HERE, f"{stem}{ext}"))),
        "sources": _sources(),
    }


def main(argv):
    _assert_every_figure_has_a_generator()
    rec = _record()
    if "--check" in argv:
        if not os.path.exists(OUT):
            print(f"{os.path.basename(OUT)} is missing — run this module without --check",
                  file=sys.stderr)
            return 2
        old = json.load(open(OUT))
        drift = {k: (v, rec["sources"].get(k)) for k, v in old.get("sources", {}).items()
                 if rec["sources"].get(k) != v}
        missing = [k for k, v in rec["sources"].items() if v is None]
        for k, (was, now) in sorted(drift.items()):
            print(f"STALE  {k}: figures were drawn from {was}, artifact is now {now}",
                  file=sys.stderr)
        for k in missing:
            print(f"ABSENT {k}: an artifact a figure is drawn from is not on disk", file=sys.stderr)
        if drift or missing:
            print(f"\n{len(drift)} artifact(s) moved since the ASO figures were drawn. Redraw them:"
                  f"\n  {old.get('_regenerate') or rec['_regenerate']}", file=sys.stderr)
            return 1
        print(f"aso figure provenance: {len(rec['sources'])} artifact(s) unchanged, "
              f"{len(rec['rendered'])} rendered file(s)")
        return 0
    with open(OUT, "w") as fh:
        json.dump(rec, fh, indent=1)
        fh.write("\n")
    print(f"wrote {OUT}  ({len(rec['sources'])} source artifact(s), "
          f"{len(rec['rendered'])} rendered file(s))")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
