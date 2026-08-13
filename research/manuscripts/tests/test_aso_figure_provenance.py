#!/usr/bin/env python3
"""The ASO figures must be drawn from the artifacts currently on disk.

⛔ WHY. Figure 3's legend and Figure 3 itself disagreed (2026-08-13), and nothing in this repository
could have said so: `figure-provenance.json` covers the `nr4a3-fusion-targets` set only, and the
three ASO figures had no provenance record. `aso_figure_provenance.py --check` is that record; this
test is what makes it run.

⚠ WHAT THIS DOES NOT COVER. A green check means each figure was drawn from the current artifact. It
says nothing about whether the manuscript's LEGEND describes the figure — the actual Figure 3 defect.
That direction is held by `research/modalities/tests/test_aso_submission_numbers.py::
test_the_figure_3_legend_matches_the_series_it_describes`, which reads the legend against
`figure_series`. Both directions are needed and neither substitutes for the other.
"""
import os
import subprocess
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
CHECKER = os.path.join(REPO, "research", "manuscripts", "figures", "aso_figure_provenance.py")


def test_the_aso_figures_are_drawn_from_the_current_artifacts():
    if not os.path.exists(CHECKER):
        pytest.skip("aso_figure_provenance.py is not present in this checkout")
    p = subprocess.run([sys.executable, CHECKER, "--check"], capture_output=True, text=True)
    assert p.returncode == 0, (
        "an artifact has moved since the ASO figures were drawn, so at least one figure in the "
        "submission is stale. Redraw them rather than relaxing this — a stale figure beside current "
        "prose is the exact shape of the Figure 3 defect.\n" + p.stdout + p.stderr)


def test_the_provenance_record_covers_every_aso_figure_in_the_submission():
    """A provenance record that quietly covers fewer figures than exist is worse than none.

    The manuscript has three numbered figures. If a fourth is added and not registered here, the
    check above would pass while saying nothing about it, which reads as coverage.
    """
    if not os.path.exists(CHECKER):
        pytest.skip("aso_figure_provenance.py is not present in this checkout")
    sys.path.insert(0, os.path.dirname(CHECKER))
    import aso_figure_provenance as prov  # noqa: PLC0415

    figs = os.path.join(os.path.dirname(CHECKER))
    drawn = {f[:-4] for f in os.listdir(figs) if f.startswith("aso-") and f.endswith(".svg")}
    assert drawn, "no ASO figure SVGs found; the glob or the directory moved"
    assert drawn <= set(prov.FIGURES), (
        f"ASO figures with no provenance entry: {sorted(drawn - set(prov.FIGURES))}")
