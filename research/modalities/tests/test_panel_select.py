"""Tests for panel_select — the pure resolver from frozen conformer-panel RULES to concrete frame lists.
No structure/docking/S3 stack required."""
import panel_select as ps


def _frames():
    fr = []
    # unbiased release: 6 frames, druggability 0.90..0.40 (4 above D*=0.53)
    for i, d in enumerate([0.90, 0.80, 0.70, 0.60, 0.50, 0.40]):
        fr.append({"ensemble": "release_rep0", "frame_id": f"r{i}", "druggability": d, "detected": True})
    # 8XTT 20-model: 3 druggable (>=0.53), rest occluded (incl. one undetected)
    for i, d in enumerate([0.75, 0.62, 0.55]):
        fr.append({"ensemble": "8xtt_20conformers", "frame_id": f"x{i}", "druggability": d, "detected": True})
    for i in range(3, 19):
        fr.append({"ensemble": "8xtt_20conformers", "frame_id": f"x{i}", "druggability": 0.30, "detected": True})
    fr.append({"ensemble": "8xtt_20conformers", "frame_id": "x19", "druggability": None, "detected": False})
    # metad + AF2 + anti-targets
    fr.append({"ensemble": "nr4a3_metad", "frame_id": "m_hi", "druggability": 0.93, "detected": True})
    fr.append({"ensemble": "nr4a3_metad", "frame_id": "m_lo", "druggability": 0.60, "detected": True})
    fr.append({"ensemble": "af2_static", "frame_id": "af2", "druggability": 0.495, "detected": True})
    fr.append({"ensemble": "nr4a1_metad", "frame_id": "524", "druggability": 0.981, "detected": True})
    fr.append({"ensemble": "nr4a2_metad", "frame_id": "125", "druggability": 0.938, "detected": True})
    return fr


def test_design_is_top3_druggable_release_no_af2():
    p = ps.resolve_panel(_frames())
    ids = [r["frame_id"] for r in p["design"]]
    assert ids == ["r0", "r1", "r2"]                        # top-3 by druggability
    assert all(r["ensemble"].startswith("release") for r in p["design"])
    assert "af2" not in ids


def test_validation_has_druggable_8xtt_plus_heldout_release():
    p = ps.resolve_panel(_frames())
    ids = [r["frame_id"] for r in p["validation"]]
    # the 3 druggable 8XTT models...
    assert {"x0", "x1", "x2"} <= set(ids)
    # ...plus held-out druggable release (r3 is the 4th, above D*, not in design)
    assert "r3" in ids
    # design frames are NOT reused in validation
    assert not ({"r0", "r1", "r2"} & set(ids))


def test_stress_is_occluded_8xtt_plus_af2_plus_top_metad():
    p = ps.resolve_panel(_frames())
    ids = [r["frame_id"] for r in p["stress"]]
    assert "af2" in ids                                     # circularity probe
    assert "m_hi" in ids and "m_lo" not in ids              # only the TOP metad frame
    assert "x19" in ids                                     # undetected occluded
    assert "x3" in ids                                      # detected-below-D* occluded
    assert not any(f in ids for f in ("x0", "x1", "x2"))    # druggable 8XTT are validation, not stress


def test_antitargets_pass_through_metad_frames():
    p = ps.resolve_panel(_frames())
    assert [r["frame_id"] for r in p["nr4a1_antitarget"]] == ["524"]
    assert [r["frame_id"] for r in p["nr4a2_antitarget"]] == ["125"]


def test_provenance_counts_and_no_warnings_on_full_input():
    p = ps.resolve_panel(_frames())
    c = p["_provenance"]["counts"]
    assert c["design"] == 3 and c["nr4a1_antitarget"] == 1 and c["nr4a2_antitarget"] == 1
    assert p["_provenance"]["warnings"] == []


def test_empty_design_warns_when_no_druggable_release():
    fr = [{"ensemble": "release_rep0", "frame_id": "r0", "druggability": 0.40, "detected": True},
          {"ensemble": "nr4a1_metad", "frame_id": "524", "druggability": 0.9, "detected": True}]
    p = ps.resolve_panel(fr)
    assert p["design"] == []
    assert any("design set EMPTY" in w for w in p["_provenance"]["warnings"])


def test_deterministic_tie_break_by_frame_id():
    fr = [{"ensemble": "release_rep0", "frame_id": "b", "druggability": 0.7, "detected": True},
          {"ensemble": "release_rep0", "frame_id": "a", "druggability": 0.7, "detected": True},
          {"ensemble": "release_rep0", "frame_id": "c", "druggability": 0.7, "detected": True}]
    p = ps.resolve_panel(fr, n_design=2)
    assert [r["frame_id"] for r in p["design"]] == ["a", "b"]   # equal druggability -> frame_id order
