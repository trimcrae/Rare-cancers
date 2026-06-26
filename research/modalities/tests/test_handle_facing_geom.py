"""Tests for handle_facing_geom — the pure geometry behind the NR4A3 Gate-2 handle-facing check.

These prove the "pocket-facing" decision and the aggregation/verdict logic are correct without mdtraj,
fpocket, numpy, or any trajectory (TESTING.md #3: the SageMaker job runs this tested code)."""
import handle_facing_geom as hf

HANDLES = [406, 407, 410, 412, 484, 531, 534]


def test_centroid():
    assert hf.centroid([(0, 0, 0), (2, 0, 0), (4, 0, 0)]) == (2.0, 0.0, 0.0)
    assert hf.centroid([]) is None


def test_inward_side_chain_faces_pocket():
    # cavity at origin; CA out at x=2; side chain at x=1 points back toward the cavity -> facing in
    r = hf.facing(ca=(2, 0, 0), sidechain_pts=[(1, 0, 0)], cavity_center=(0, 0, 0))
    assert r["facing"] is True
    assert r["cos"] == 1.0
    assert r["depth"] > 0          # side chain sits deeper toward the cavity than the backbone


def test_outward_side_chain_splays_away():
    # side chain at x=3 points away from the cavity at origin -> not facing (splayed artifact)
    r = hf.facing(ca=(2, 0, 0), sidechain_pts=[(3, 0, 0)], cavity_center=(0, 0, 0))
    assert r["facing"] is False
    assert r["cos"] == -1.0
    assert r["depth"] < 0


def test_perpendicular_is_not_facing():
    # exactly 90 deg (cos == 0) counts as not pocket-facing (strict cos > 0)
    r = hf.facing(ca=(2, 0, 0), sidechain_pts=[(2, 1, 0)], cavity_center=(0, 0, 0))
    assert r["cos"] == 0.0
    assert r["facing"] is False


def test_glycine_or_degenerate_is_undecidable():
    assert hf.facing(ca=(2, 0, 0), sidechain_pts=[], cavity_center=(0, 0, 0)) is None        # no side chain
    assert hf.facing(ca=(2, 0, 0), sidechain_pts=[(2, 0, 0)], cavity_center=(0, 0, 0)) is None  # sc == ca
    assert hf.facing(ca=None, sidechain_pts=[(1, 0, 0)], cavity_center=(0, 0, 0)) is None
    assert hf.facing(ca=(2, 0, 0), sidechain_pts=[(1, 0, 0)], cavity_center=None) is None


def _frame(fi, drug, facing_map):
    return {"frame": fi, "druggability": drug, "facing": {h: facing_map.get(h) for h in HANDLES}}


def test_summarize_confirms_when_druggable_frames_keep_handles():
    # 3 druggable frames, all 7 handles facing; 1 non-druggable frame ignored for the subset
    all_in = {h: True for h in HANDLES}
    frames = [_frame(0, 0.9, all_in), _frame(1, 0.8, all_in), _frame(2, 0.6, all_in),
              _frame(3, 0.2, {h: False for h in HANDLES})]
    s = hf.summarize(frames, HANDLES, d_star=0.53, min_handles_facing=4)
    assert s["n_druggable_frames"] == 3
    assert s["confirmed"] is True
    assert s["verdict"].startswith("CONFIRMED")
    assert s["frac_druggable_frames_keeping_handles"] == 1.0
    assert s["per_handle"][406]["frac_facing_druggable"] == 1.0


def test_summarize_not_confirmed_when_handles_splay_in_druggable_frames():
    # druggable frames but only 2 of 7 handles facing (< min 4) -> not confirmed
    two_in = {406: True, 407: True}   # rest False
    for h in HANDLES[2:]:
        two_in[h] = False
    frames = [_frame(0, 0.9, two_in), _frame(1, 0.7, two_in)]
    s = hf.summarize(frames, HANDLES, d_star=0.53, min_handles_facing=4)
    assert s["n_druggable_frames"] == 2
    assert s["confirmed"] is False
    assert s["verdict"].startswith("NOT CONFIRMED")
    assert s["frac_druggable_frames_keeping_handles"] == 0.0


def test_summarize_inconclusive_without_druggable_frames():
    # no frame reaches D* (e.g. fpocket unavailable -> druggability None) -> INCONCLUSIVE, but the
    # geometric-only per-handle frac_facing_all is still reported
    frames = [_frame(0, None, {h: True for h in HANDLES}),
              _frame(1, None, {h: True for h in HANDLES})]
    s = hf.summarize(frames, HANDLES, d_star=0.53, min_handles_facing=4)
    assert s["n_druggable_frames"] == 0
    assert s["confirmed"] is False
    assert s["verdict"].startswith("INCONCLUSIVE")
    assert s["per_handle"][406]["frac_facing_all"] == 1.0
    assert s["per_handle"][406]["frac_facing_druggable"] is None
