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
             ("motif", F.MOTIF), ("conf", F.CONF), ("occ", F.OCC))}


def test_every_cell_of_the_convergence_matrix_resolves_to_a_real_statistic(art):
    """The bug that shipped a finished-looking figure: a lookup that misses renders as
    'not computed', which is indistinguishable from a contrast that genuinely cannot be run."""
    cells = F._cells(art["tgt"], art["robust"], art["seq3"], art["motif"], art["conf"], art["occ"])
    assert set(cells) == set(F.GENES)
    for g, row in cells.items():
        assert len(row) == 6, g
        for txt, state in row:
            assert state in ("supported", "weak", "absent", "circular"), (g, txt)
        # None of these five instruments is genuinely uncomputable for any class-A gene.
        assert not [t for t, s in row if s == "absent"], f"{g}: {row}"


def test_the_array_columns_carry_the_q_values_the_manuscript_reports(art):
    cells = F._cells(art["tgt"], art["robust"], art["seq3"], art["motif"], art["conf"], art["occ"])
    assert "0.000438" in cells["ENO3"][0][0]        # GPL6244 BH q
    assert "0.000625" in cells["ENO3"][1][0]        # GPL3290 BH q
    assert "0.097" in cells["PPARG"][0][0]


def test_the_circular_PPARG_cell_is_marked_and_not_coloured_as_support(art):
    """GSE4303 IS the cohort the 'high PPARG in most EMCs' claim was published from.

    Colouring that cell as independent support would let the figure make a claim the manuscript
    explicitly refuses for the equivalent gene SET."""
    cells = F._cells(art["tgt"], art["robust"], art["seq3"], art["motif"], art["conf"], art["occ"])
    txt, state = cells["PPARG"][1]
    assert state == "circular"
    assert "circular" in txt.lower()
    assert cells["ENO3"][1][1] == "supported", "only PPARG/GPL3290 is the circular cell"


def test_the_NBRE_column_reads_the_composition_matched_null_not_the_raw_count(art):
    cells = F._cells(art["tgt"], art["robust"], art["seq3"], art["motif"], art["conf"], art["occ"])
    eno = cells["ENO3"][4][0]
    assert "4 exact sites" in eno and "p=" in eno
    assert cells["ENO3"][4][1] == "supported"
    assert cells["SEMA3C"][4][1] == "weak", "SEMA3C carries no exact NBRE"


def test_the_occupancy_column_is_present_and_supports_no_gene(art):
    """The axis exists and it is negative for all three — the state §3.11 reports.

    If any gene ever turns green here, the abstract, §3.11 and §3.12 must be rewritten; this test
    is what makes that impossible to do by accident."""
    cells = F._cells(art["tgt"], art["robust"], art["seq3"], art["motif"], art["conf"], art["occ"])
    for g in F.GENES:
        txt, state = cells[g][5]
        assert "experiments" in txt, f"{g} occupancy cell is not reporting its test count: {txt}"
        assert state == "weak", (
            f"{g} is now supported on the occupancy axis — the manuscript must be revised, not "
            "this test")


def test_the_3seq_column_uses_the_percentile_calibration_not_the_bare_ratio(art):
    cells = F._cells(art["tgt"], art["robust"], art["seq3"], art["motif"], art["conf"], art["occ"])
    for g in F.GENES:
        txt, _ = cells[g][3]
        assert "ᵗʰ" in txt, f"{g} 3SEQ cell shows no percentile: {txt}"


class _StubPyplot:
    """Enough of `plt` to prove the REFUSAL, which happens before anything is drawn.

    ⛔⛔ WHY THIS EXISTS (2026-08-19, lane C2 audit). This test opened with
    `pytest.importorskip("matplotlib.pyplot")`, and `.github/workflows/tests.yml` has never
    installed matplotlib — so in the only environment that gates a commit it has NEVER RUN. It is
    the same defect the same audit found in the pypdf/pymupdf guards: a check reporting green for
    something nobody performed. The subject of this test is `fig_classes`'s cross-check against
    `counts_by_class`, and that cross-check raises SystemExit BEFORE the first `plt.subplots`, so
    the refusal can be — and now is — proved with no renderer at all. The rendering half is kept
    below, still behind an importorskip, and is honestly labelled as not running in CI.
    """

    class _Called(Exception):
        pass

    def subplots(self, *a, **k):
        raise _StubPyplot._Called("fig_classes reached the drawing stage")


def test_the_evidence_class_figure_refuses_to_draw_if_it_disagrees_with_the_artifact(art):
    """Pinned because the first version silently drew four empty bars.

    The generator now cross-checks its own tally against `counts_by_class` and exits rather than
    emitting a catalogue figure that omits rows.
    """
    stub = _StubPyplot()
    counts = art["tgt"]["evidence_table"]["counts_by_class"]
    assert counts["fusion_dna_binding"] == 3

    #: the CLEAN artifact must pass the cross-check and reach the drawing stage — otherwise the
    #: two refusals below would be satisfied by a function that refuses everything
    with pytest.raises(_StubPyplot._Called):
        F.fig_classes(stub, art["tgt"])

    bad = json.loads(json.dumps(art["tgt"]))
    bad["evidence_table"]["counts_by_class"]["fusion_dna_binding"] = 99
    with pytest.raises(SystemExit) as e:
        F.fig_classes(stub, bad)
    assert "counts" in str(e.value)

    #: and the second refusal in the same function — a vocabulary value with no class letter, which
    #: is what silently produced four empty bars in the first place
    unmapped = json.loads(json.dumps(art["tgt"]))
    rows = unmapped["evidence_table"]
    rows = rows if isinstance(rows, list) else rows.get("rows", [])
    assert rows, "the evidence table has no rows; the unmapped-vocabulary refusal is untestable"
    rows[0]["evidence_class"] = "a_class_the_mapping_has_never_heard_of"
    with pytest.raises(SystemExit) as e2:
        F.fig_classes(stub, unmapped)
    assert "unmapped" in str(e2.value)


def test_the_evidence_class_figure_actually_renders(art):
    """The rendering half, split out 2026-08-19 (lane C2).

    ⚠ NOT IN CI — THIS ONE GENUINELY NEEDS matplotlib AND CI DOES NOT INSTALL IT, so it does NOT run where
    commits are gated — which is why the refusal above no longer rides along with it. Keeping the
    two in one test is what let the refusal go unproven for as long as it did.
    """
    plt = pytest.importorskip("matplotlib.pyplot")
    import matplotlib  # noqa: PLC0415
    matplotlib.use("Agg")
    fig = F.fig_classes(plt, art["tgt"])
    assert fig is not None
    plt.close(fig)


def test_the_provenance_stamp_matches_the_committed_artifacts():
    """`--check` is the only staleness signal that exists: nothing in CI redraws these figures."""
    #: ⛔ NOT A SKIP (2026-08-19, lane C2 audit): `figure-provenance.json` is committed, and the
    #: docstring above already says `--check` is the ONLY staleness signal that exists.
    if not os.path.exists(F.STAMP):
        pytest.fail(f"the figure provenance stamp is missing at {F.STAMP}; it is committed, and "
                    "nothing else can tell a stale figure from a current one.")
    stamp = F._load(F.STAMP)
    assert stamp["sources"] == F._fingerprint(), (
        "the committed figures were drawn from different artifacts than the ones on disk; "
        "re-run nr4a3_fusion_targets_figures.py")
    for f in stamp["figures"]:
        assert os.path.exists(os.path.join(F.FIGDIR, f)), f


def test_check_mode_reports_ok_on_a_clean_tree():
    if not os.path.exists(F.STAMP):
        pytest.fail(f"the figure provenance stamp is missing at {F.STAMP}; it is committed, and "
                    "`--check` reporting OK on a clean tree is what this test measures.")
    assert F.check() == 0


@pytest.fixture
def isolated_build(monkeypatch, tmp_path):
    """Exercise orchestration with byte-writing doubles, never another scientific factory."""
    pytest.importorskip("matplotlib.pyplot")
    import matplotlib.pyplot as plt
    monkeypatch.setattr(plt, "close", lambda fig: None)
    monkeypatch.setattr(F, "FIGDIR", str(tmp_path))
    monkeypatch.setattr(F, "STAMP", str(tmp_path / "figure-provenance.json"))
    for name in F.FIGURE_OUTPUTS:
        (tmp_path / name).write_bytes(("original " + name).encode())
    prior = {"sources": F._fingerprint(), "figures": list(F.FIGURE_OUTPUTS),
             "_source_equivalence_2026_09_08": {"historical_draw_digest": "retain-exactly"}}
    (tmp_path / "figure-provenance.json").write_text(json.dumps(prior), encoding="utf-8")
    context = {"source_commit": "test-commit", "generator": {
        "path": "research/modalities/nr4a3_fusion_targets_figures.py", **F._identity(F.__file__)}}
    monkeypatch.setattr(F, "_committed_source_context", lambda: context)
    called = []

    class Double:
        def __init__(self, name):
            self.name = name

        def savefig(self, path, **kwargs):
            from pathlib import Path
            Path(path).write_bytes(("new " + self.name + os.path.splitext(path)[1]).encode())

    def factory(name):
        def draw(plt, art):
            called.append((name, set(art)))
            return Double(name)
        return draw

    monkeypatch.setattr(F, "FIGURE_SPECS", {
        n: {"needs": s["needs"], "draw": factory(n)} for n, s in F.FIGURE_SPECS.items()})
    return {"dir": tmp_path, "prior": prior, "called": called, "context": context, "double": Double}


def test_selective_build_is_lazy_preserves_outputs_and_history(isolated_build):
    before = F._output_identities()
    written = F.build(only="fig4-instrument-convergence")
    assert isolated_build["called"] == [("fig4-instrument-convergence", {"robust", "seq3", "motif", "conf", "occ"})]
    assert set(written) == {"fig4-instrument-convergence.png", "fig4-instrument-convergence.pdf"}
    after = F._output_identities()
    assert {f: v for f, v in after.items() if f not in written} == {f: v for f, v in before.items() if f not in written}
    stamp = F._read_stamp()
    assert stamp["_source_equivalence_2026_09_08"] == isolated_build["prior"]["_source_equivalence_2026_09_08"]
    assert set(stamp["figures"]) == set(F.FIGURE_OUTPUTS)
    record = stamp["builds"][-1]
    assert record["prior_source_map"] == isolated_build["prior"]["sources"]
    assert len(record["sources_actually_consumed"]) == 5
    assert len(record["sources_verified"]) == 7
    assert len(record["outputs_not_regenerated"]) == 8
    assert record["source_commit"] == "test-commit"
    assert all(len(v["sha256"]) == 64 for v in record["sources_actually_consumed"].values())


def test_default_build_keeps_all_five_factories(isolated_build):
    assert len(F.build()) == 10
    assert [x[0] for x in isolated_build["called"]] == list(F.FIGURE_SPECS)


@pytest.mark.parametrize("source", ["nr4a3-fusion-targets-inputs.json", "nr4a3-fusion-targets-robustness.json"])
def test_selective_build_rejects_unexplained_drift_before_drawing(isolated_build, source):
    stamp = F._read_stamp()
    stamp["sources"][source] = "0" * 16
    path = isolated_build["dir"] / "figure-provenance.json"
    path.write_text(json.dumps(stamp), encoding="utf-8")
    before = path.read_bytes(), F._output_identities()
    with pytest.raises(ValueError, match="unexplained source drift"):
        F.build(only="fig4-instrument-convergence")
    assert not isolated_build["called"]
    assert before == (path.read_bytes(), F._output_identities())


def test_exact_audited_calibration_move_is_recorded(isolated_build):
    stamp = F._read_stamp()
    eq = F.CALIBRATION_EQUIVALENCE
    stamp["sources"][eq["artifact"]] = eq["old"]["sha256"][:16]
    (isolated_build["dir"] / "figure-provenance.json").write_text(json.dumps(stamp), encoding="utf-8")
    F.build(only="fig4-instrument-convergence")
    current = F._read_stamp()
    assert current["builds"][-1]["source_equivalence"] == eq
    assert current["builds"][-1]["prior_source_map"] == stamp["sources"]
    assert current["sources"][eq["artifact"]] == eq["current"]["sha256"][:16]


def test_incomplete_pair_leaves_provenance_untouched(isolated_build, monkeypatch):
    path = isolated_build["dir"] / "figure-provenance.json"
    before = path.read_bytes()
    original = isolated_build["double"].savefig

    def fail_pdf(self, path, **kwargs):
        if path.endswith(".pdf"):
            raise OSError("synthetic second-save failure")
        return original(self, path, **kwargs)

    monkeypatch.setattr(isolated_build["double"], "savefig", fail_pdf)
    with pytest.raises(OSError, match="second-save failure"):
        F.build(only="fig4-instrument-convergence")
    assert path.read_bytes() == before
    assert F._read_stamp().get("builds") is None


def test_skipped_factory_does_not_create_generation_record(isolated_build, monkeypatch):
    path = isolated_build["dir"] / "figure-provenance.json"
    before = path.read_bytes()
    monkeypatch.setitem(F.FIGURE_SPECS["fig4-instrument-convergence"], "draw", lambda plt, art: None)
    assert F.build(only="fig4-instrument-convergence") == []
    assert path.read_bytes() == before


def test_missing_or_corrupt_provenance_is_not_replaced_by_selective_build(isolated_build):
    path = isolated_build["dir"] / "figure-provenance.json"
    path.write_text("{broken", encoding="utf-8")
    with pytest.raises(ValueError):
        F.build(only="fig4-instrument-convergence")
    assert path.read_text(encoding="utf-8") == "{broken"
    path.unlink()
    with pytest.raises(ValueError, match="requires the existing provenance"):
        F.build(only="fig4-instrument-convergence")
    assert not path.exists()


def test_repeated_build_checks_latest_output_and_source_generator_identities(isolated_build, monkeypatch):
    from pathlib import Path
    F.build(only="fig4-instrument-convergence")
    first = F._read_stamp()["builds"][0]
    original = isolated_build["double"].savefig

    def second(self, path, **kwargs):
        original(self, path, **kwargs)
        with open(path, "ab") as fh:
            fh.write(b" second build")

    monkeypatch.setattr(isolated_build["double"], "savefig", second)
    F.build(only="fig4-instrument-convergence")
    assert F._read_stamp()["builds"][0] == first

    def git_body(*args):
        name = args[-1].split("/")[-1]
        return (Path(F.HERE) / name).read_bytes()

    monkeypatch.setattr(F, "_git_output", git_body)
    assert F.check_builds() == 0
    output = isolated_build["dir"] / "fig4-instrument-convergence.png"
    original_bytes = output.read_bytes()
    output.write_bytes(b"tampered")
    assert F.check_builds() == 1
    output.write_bytes(original_bytes)
    snapshot = F._source_identities()
    real_snapshot = F._source_identities()
    snapshot[os.path.basename(F.SEQ3)]["sha256"] = "0" * 64
    monkeypatch.setattr(F, "_source_identities", lambda: snapshot)
    assert F.check_builds() == 1
    monkeypatch.setattr(F, "_source_identities", lambda: real_snapshot)
    stamp = F._read_stamp()
    stamp["builds"][-1]["generator"]["sha256"] = "0" * 64
    (isolated_build["dir"] / "figure-provenance.json").write_text(json.dumps(stamp), encoding="utf-8")
    assert F.check_builds() == 1


def test_generation_refuses_uncommitted_source(monkeypatch):
    from pathlib import Path
    root = Path(F.HERE).parents[1]

    def git_output(*args):
        if args == ("rev-parse", "--show-toplevel"):
            return str(root).encode()
        if args == ("rev-parse", "HEAD"):
            return b"test-commit"
        return b"different committed generator"

    monkeypatch.setattr(F, "_git_output", git_output)
    with pytest.raises(ValueError, match="uncommitted generation input"):
        F._committed_source_context()


def test_rank_labels_follow_distinct_artifact_populations_and_cells_keep_values(art):
    rc = art["seq3"]["ratio_calibration"]
    label = " ".join(F._matrix_row_labels(art["seq3"])[3])
    for key in ["n_genes_with_a_normal_ratio", "n_genes_with_a_sarcoma_ratio"]:
        assert f"{rc[key]:,}" in label
    cells = F._cells(art["tgt"], art["robust"], art["seq3"], art["motif"], art["conf"], art["occ"])
    for gene, expected_state in [("ENO3", "supported"), ("PPARG", "supported"), ("SEMA3C", "weak")]:
        text, state = cells[gene][3]
        normal, sarcoma = text.splitlines()
        expected = rc["per_gene"][gene]
        assert str(expected["emc_over_normal"]) in normal
        assert str(expected["emc_over_normal_percentile"]) in normal
        assert str(expected["emc_over_sarcoma"]) in sarcoma
        assert str(expected["emc_over_sarcoma_percentile"]) in sarcoma
        assert state == expected_state


def test_matrix_text_fits_cells_and_remains_legible_at_150mm(art):
    plt = pytest.importorskip("matplotlib.pyplot")
    import matplotlib
    matplotlib.use("Agg")
    fig = F.fig_matrix(plt, **art)
    try:
        fig.canvas.draw()
        renderer = fig.canvas.get_renderer()
        ax = fig.axes[0]
        assert len(ax.patches) == 18
        inset = 1.5 * fig.dpi / 72  # A real margin, not merely a centre inside the cell.
        for patch in ax.patches:
            center = (patch.get_x() + patch.get_width() / 2,
                      patch.get_y() + patch.get_height() / 2)
            texts = [text for text in ax.texts if all(abs(a-b) < 1e-8
                     for a, b in zip(text.get_position(), center))]
            assert len(texts) == 1
            tb = texts[0].get_window_extent(renderer)
            pb = patch.get_window_extent(renderer)
            assert tb.x0 >= pb.x0 + inset and tb.x1 <= pb.x1 - inset, texts[0].get_text()
            assert tb.y0 >= pb.y0 + inset and tb.y1 <= pb.y1 - inset, texts[0].get_text()
        saved_width_inches = fig.get_tightbbox(renderer).width + 0.2  # savefig default padding
        scale_at_150mm = (150 / 25.4) / saved_width_inches
        assert min(t.get_fontsize() for t in [*fig.texts, *ax.texts] if t.get_text()) * scale_at_150mm >= 7
    finally:
        plt.close(fig)
