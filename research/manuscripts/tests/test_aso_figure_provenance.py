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

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
CHECKER = os.path.join(REPO, "research", "manuscripts", "figures", "aso_figure_provenance.py")


def test_the_aso_figures_are_drawn_from_the_current_artifacts():
    # ⛔ WAS A SKIP UNTIL 2026-08-17, AND A SKIP HERE IS A FAIL-QUIET. `aso_figure_provenance.py` is
    # TRACKED, so it cannot be legitimately absent: the only ways to reach that branch are a broken
    # checkout or someone deleting the checker — and in the second case both guards in this file
    # would go green-by-skipping while the property they exist to hold silently stopped being
    # checked. That is the exact shape this repository has shipped twice (a gate obeying an input
    # nothing supplied; a guard that no-opped into the previous behaviour). An assertion turns a
    # missing checker into a red build, which is the only reading that is not a lie.
    assert os.path.exists(CHECKER), (
        f"{CHECKER} is missing. It is a tracked file, so this is a deleted or broken checkout, not "
        "a configuration this test may skip — the ASO figures' provenance is unchecked right now.")
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
    # ⛔ WAS A SKIP UNTIL 2026-08-17, AND A SKIP HERE IS A FAIL-QUIET. `aso_figure_provenance.py` is
    # TRACKED, so it cannot be legitimately absent: the only ways to reach that branch are a broken
    # checkout or someone deleting the checker — and in the second case both guards in this file
    # would go green-by-skipping while the property they exist to hold silently stopped being
    # checked. That is the exact shape this repository has shipped twice (a gate obeying an input
    # nothing supplied; a guard that no-opped into the previous behaviour). An assertion turns a
    # missing checker into a red build, which is the only reading that is not a lie.
    assert os.path.exists(CHECKER), (
        f"{CHECKER} is missing. It is a tracked file, so this is a deleted or broken checkout, not "
        "a configuration this test may skip — the ASO figures' provenance is unchecked right now.")
    sys.path.insert(0, os.path.dirname(CHECKER))
    import aso_figure_provenance as prov  # noqa: PLC0415

    figs = os.path.join(os.path.dirname(CHECKER))
    drawn = {f[:-4] for f in os.listdir(figs) if f.startswith("aso-") and f.endswith(".svg")}
    assert drawn, "no ASO figure SVGs found; the glob or the directory moved"
    assert drawn <= set(prov.FIGURES), (
        f"ASO figures with no provenance entry: {sorted(drawn - set(prov.FIGURES))}")
