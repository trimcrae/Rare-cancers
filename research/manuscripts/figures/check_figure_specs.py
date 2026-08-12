#!/usr/bin/env python3
"""Check every figure against the resolution and format specs journals ask for.

⛔ THIS STARTED LIFE AS A FIXER AND THE FIX WAS IMPOSSIBLE. matplotlib writes 299.9994 dpi for
`savefig(dpi=300)`, which looked like a rounding bug worth stamping to exactly 300. It is not a bug
and it cannot be stamped: the PNG `pHYs` chunk stores resolution as an INTEGER number of pixels per
METRE, and 300 dpi is 11811.02 ppm, which rounds to 11811 and reads back as 299.9994. 300 dpi is
not representable in a PNG header. Every 300-dpi PNG ever written reads this way, so no submission
portal can reject on it, and re-saving the file changes nothing. Caught by verifying the output of
the "fix" instead of trusting that it worked.

⚠ THE HONEST BAR IS THEREFORE 299 dpi, not 300 — anything at or above that was authored at 300.
What this does check is the thing that actually varies and actually matters:

  * a figure genuinely authored below 300 dpi, which must be REGENERATED and never relabelled,
    since raising the header without re-rendering claims detail that was never measured;
  * a missing vector companion (PDF or EPS), which journals prefer to raster for line art;
  * a physical width outside what a journal page can take.

    python3 research/manuscripts/figures/check_figure_specs.py
"""
import glob
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
MIN_DPI = 299.0            # see the docstring: 300 dpi reads as 299.9994 and cannot read higher
MAX_WIDTH_IN = 7.5         # a full double-column page at most journals
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))


def main():
    problems = []
    rows = []
    for path in sorted(glob.glob(os.path.join(HERE, "*.png"))):
        name = os.path.basename(path)
        im = Image.open(path)
        dpi = im.info.get("dpi") or (0, 0)
        w_in = im.size[0] / dpi[0] if dpi[0] else None
        vector = any(os.path.exists(path[:-4] + ext) for ext in (".pdf", ".eps", ".svg"))
        flags = []
        if dpi[0] < MIN_DPI:
            flags.append(f"{dpi[0]:.0f} dpi — REGENERATE at 300, do not relabel")
        if not vector:
            flags.append("no vector companion")
        if w_in and w_in > MAX_WIDTH_IN:
            flags.append(f"{w_in:.1f} in wide — wider than a {MAX_WIDTH_IN} in page")
        rows.append((name, dpi[0], w_in, vector, flags))
        if flags:
            problems.append((name, flags))
        print(f"{name:44s} {dpi[0]:7.1f} dpi  {('%.1f in' % w_in) if w_in else '   ?':>8s}  "
              f"{'vector' if vector else '   —':>6s}  {'; '.join(flags) or 'ok'}")

    print(f"\ncheck_figure_specs: {len(problems)} figure(s) with findings, {len(rows)} checked")
    return 0


if __name__ == "__main__":
    sys.exit(main())
