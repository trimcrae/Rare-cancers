#!/usr/bin/env python3
"""Offline tests for `nr4a3_fusion_targets_figures.py`.

matplotlib is not installed in every checkout, so the drawing itself is skipped where it is absent.
What is ALWAYS tested is the part that can silently lie: the artifact lookups behind the cells, and
the staleness stamp. Two of those lookups were wrong on the first run and produced a figure that
looked finished -- an evidence-class chart with four empty bars, and a convergence matrix whose two
array columns both read "not computed". Neither raised anything; both had to be caught by eye.
"""
import json
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.dirname(HERE)
sys.path.insert(0, MOD)

import nr4a3_fusion_targets_figures as F  # noqa: E402

mpl = pytest.importorskip if False else None


@pytest.fixture(scope="module")
def art():
    return {name: F._load(p) for name, p in
            (("tgt", F.TARGETS), ("robust", F.ROBUST), ("seq3", F.SEQ3),
             ("motif", F.MOTIF), ("conf", F.CONF))}


def test_every_cell_of_the_convergence_matrix_resolves_to_a_real_statistic(art):
    """The bug that shipped a finished-looking figure: a lookup that misses renders as
    'not computed', which is indistinguishable from a contrast that genuinely cannot be run."""
    cells = F._cells(art["tgt"], art["robust"], art["seq3"], art["motif"], art["conf"])
    assert set(cells) == set(F.GENES)
    for g, row in cells.items():
        assert len(row) == 5, g
        for txt, state in row:
            assert state in ("supported", "weak", "absent", "circular"), (g, txt)
        # None of these five instruments is genuinely uncomputable for any class-A gene.
        assert not [t for t, s in row if s == "absent"], f"{g}: {row}"


def test_the_array_columns_carry_the_q_values_the_manuscript_reports(art):
    cells = F._cells(art["tgt"], art["robust"], art["seq3"], art["motif"], art["conf"])
    assert "0.000438" in cells["ENO3"][0][0]        # GPL6244 BH q
    assert "0.000625" in cells["ENO3"][1][0]        # GPL3290 BH q
    assert "0.097" in cells["PPARG"][0][0]


def test_the_circular_PPARG_cell_is_marked_and_not_coloured_as_support(art):
    """GSE4303 IS the cohort the 'high PPARG in most EMCs' claim was published from.

    Colouring that cell as independent support would let the figure make a claim the manuscript
    explicitly refuses for the equivalent gene SET."""
    cells = F._cells(art["tgt"], art["robust"], art["seq3"], art["motif"], art["conf"])
    txt, state = cells["PPARG"][1]
    assert state == "circular"
    assert "circular" in txt.lower()
    assert cells["ENO3"][1][1] == "supported", "only PPARG/GPL3290 is the circular cell"


def test_the_NBRE_column_reads_the_composition_matched_null_not_the_raw_count(art):
    cells = F._cells(art["tgt"], art["robust"], art["seq3"], art["motif"], art["conf"])
    eno = cells["ENO3"][4][0]
    assert "4 exact sites" in eno and "p=" in eno
    assert cells["ENO3"][4][1] == "supported"
    assert cells["SEMA3C"][4][1] == "weak", "SEMA3C carries no exact NBRE"


def test_the_3seq_column_uses_the_percentile_calibration_not_the_bare_ratio(art):
    cells = F._cells(art["tgt"], art["robust"], art["seq3"], art["motif"], art["conf"])
    for g in F.GENES:
        txt, _ = cells[g][3]
        assert "ᵗʰ" in txt, f"{g} 3SEQ cell shows no percentile: {txt}"


def test_the_evidence_class_figure_refuses_to_draw_if_it_disagrees_with_the_artifact(art):
    """Pinned because the first version silently drew four empty bars.

    The generator now cross-checks its own tally against `counts_by_class` and exits rather than
    emitting a catalogue figure that omits rows."""
    plt = pytest.importorskip("matplotlib.pyplot")
    import matplotlib
    matplotlib.use("Agg")
    fig = F.fig_classes(plt, art["tgt"])
    assert fig is not None
    plt.close(fig)

    counts = art["tgt"]["evidence_table"]["counts_by_class"]
    assert counts["fusion_dna_binding"] == 3
    bad = json.loads(json.dumps(art["tgt"]))
    bad["evidence_table"]["counts_by_class"]["fusion_dna_binding"] = 99
    with pytest.raises(SystemExit) as e:
        F.fig_classes(plt, bad)
    assert "counts" in str(e.value)


def test_the_provenance_stamp_matches_the_committed_artifacts():
    """`--check` is the only staleness signal that exists: nothing in CI redraws these figures."""
    if not os.path.exists(F.STAMP):
        pytest.skip("figures not built in this checkout")
    stamp = F._load(F.STAMP)
    assert stamp["sources"] == F._fingerprint(), (
        "the committed figures were drawn from different artifacts than the ones on disk; "
        "re-run nr4a3_fusion_targets_figures.py")
    for f in stamp["figures"]:
        assert os.path.exists(os.path.join(F.FIGDIR, f)), f


def test_check_mode_reports_ok_on_a_clean_tree():
    if not os.path.exists(F.STAMP):
        pytest.skip("figures not built in this checkout")
    assert F.check() == 0
