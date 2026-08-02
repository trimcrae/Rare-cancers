"""Unit tests for basin_geom — the geometry kernels of the RUNG-5a mechanism-first basin search.

Every test here checks a kernel against a CLOSED-FORM or exactly-constructed answer, not against another run
of the same code. The kernels that carry scientific weight (linker reach, the distance field's clash
convention, the WLC accessibility density, matched-frame superposition) each get a correctness test AND a
failure-mode test, because nr4a3-program-map.md's Tier-2 argument rests on those geometric answers being reliable.
"""
import math
import random

import pytest

import basin_geom as G


# ------------------------------------------------------------------ vectors / rotations


def test_quat_identity_and_known_90deg_rotation():
    R = G.quat_to_matrix((1.0, 0.0, 0.0, 0.0))
    assert G.matvec(R, (1.0, 2.0, 3.0)) == pytest.approx((1.0, 2.0, 3.0))
    # 90 deg about z: (1,0,0) -> (0,1,0)
    s = math.sin(math.pi / 4), math.cos(math.pi / 4)
    Rz = G.quat_to_matrix((s[1], 0.0, 0.0, s[0]))
    out = G.matvec(Rz, (1.0, 0.0, 0.0))
    assert out[0] == pytest.approx(0.0, abs=1e-9)
    assert out[1] == pytest.approx(1.0, abs=1e-9)


def test_rotations_preserve_length_and_are_haar_uniform_in_the_mean():
    rng = random.Random(11)
    # length preservation
    for _ in range(50):
        R = G.quat_to_matrix(G.random_quaternion(rng))
        v = (1.3, -2.7, 0.4)
        assert G.norm(G.matvec(R, v)) == pytest.approx(G.norm(v), rel=1e-12)
    # a Haar-uniform rotation sends a fixed unit vector to a uniform point on the sphere -> mean ~ 0
    acc = [0.0, 0.0, 0.0]
    n = 4000
    for _ in range(n):
        R = G.quat_to_matrix(G.random_quaternion(rng))
        w = G.matvec(R, (0.0, 0.0, 1.0))
        acc = [acc[i] + w[i] for i in range(3)]
    assert G.norm(tuple(a / n for a in acc)) < 0.05


def test_transform_points_pins_the_pivot_exactly():
    """The search's whole parameterisation depends on the E3 ligand exit atom landing EXACTLY on the sampled
    anchor position — if it drifts, the linker-reach constraint it was sampled under is not the one enforced."""
    rng = random.Random(3)
    pts = [(1.0, 2.0, 3.0), (4.0, -1.0, 0.5), (0.0, 0.0, 0.0)]
    pivot = pts[0]
    tgt = (10.0, -5.0, 2.0)
    R = G.quat_to_matrix(G.random_quaternion(rng))
    out = G.transform_points(pts, R, pivot, tgt)
    assert out[0] == pytest.approx(tgt, abs=1e-9)
    # internal geometry is rigid
    assert G.dist(out[1], out[2]) == pytest.approx(G.dist(pts[1], pts[2]), rel=1e-12)


# ------------------------------------------------------------------ superposition


def test_horn_recovers_a_known_rigid_motion_to_zero_rmsd():
    rng = random.Random(7)
    ref = [(rng.uniform(-20, 20), rng.uniform(-20, 20), rng.uniform(-20, 20)) for _ in range(30)]
    Rtrue = G.quat_to_matrix(G.random_quaternion(rng))
    shift = (5.0, -3.0, 11.0)
    mobile = [G.add(G.matvec(Rtrue, p), shift) for p in ref]
    R, t, rmsd = G.horn_superpose(mobile, ref)
    assert rmsd == pytest.approx(0.0, abs=1e-6)
    back = G.apply_superpose(mobile, R, t)
    for b, r in zip(back, ref):
        assert G.dist(b, r) == pytest.approx(0.0, abs=1e-6)


def test_horn_reports_honest_rmsd_on_noisy_pairs_and_refuses_bad_input():
    rng = random.Random(5)
    ref = [(rng.uniform(-10, 10), rng.uniform(-10, 10), rng.uniform(-10, 10)) for _ in range(40)]
    mobile = [(p[0] + rng.gauss(0, 0.5), p[1] + rng.gauss(0, 0.5), p[2] + rng.gauss(0, 0.5)) for p in ref]
    _, _, rmsd = G.horn_superpose(mobile, ref)
    assert 0.2 < rmsd < 1.5           # ~sqrt(3)*0.5 = 0.87 for iid sigma=0.5 per axis
    with pytest.raises(ValueError):
        G.horn_superpose(ref[:5], ref[:6])
    with pytest.raises(ValueError):
        G.horn_superpose(ref[:2], ref[:2])


# ------------------------------------------------------------------ distance field


def test_distance_field_matches_brute_force_within_its_declared_cell_slack():
    rng = random.Random(13)
    src = [(rng.uniform(0, 20), rng.uniform(0, 20), rng.uniform(0, 20)) for _ in range(60)]
    f = G.SquaredDistanceField(src, cell=0.8, clamp=8.0)
    for _ in range(300):
        q = (rng.uniform(-2, 22), rng.uniform(-2, 22), rng.uniform(-2, 22))
        brute = min(G.dist(q, s) for s in src)
        got = f.min_dist(q)
        if brute < 6.0:                                    # inside the clamped, meaningful band
            assert abs(got - brute) <= f.cell_slack + 1e-9


def test_is_clash_is_conservative_never_passing_a_real_overlap():
    """The clash test MUST err toward rejecting. A silently-passed overlap would put an E3 inside the target
    and every downstream term computed on that placement would be meaningless."""
    rng = random.Random(17)
    src = [(rng.uniform(0, 15), rng.uniform(0, 15), rng.uniform(0, 15)) for _ in range(80)]
    f = G.SquaredDistanceField(src, cell=1.0, clamp=8.0)
    cutoff = 2.5
    missed = 0
    for _ in range(2000):
        q = (rng.uniform(-1, 16), rng.uniform(-1, 16), rng.uniform(-1, 16))
        really_clashing = min(G.dist(q, s) for s in src) < cutoff
        if really_clashing and not f.is_clash(q, cutoff):
            missed += 1
    assert missed == 0


def test_distance_field_clamps_far_away_and_refuses_empty_input():
    f = G.SquaredDistanceField([(0.0, 0.0, 0.0)], cell=1.0, clamp=5.0)
    assert f.min_dist((1000.0, 0.0, 0.0)) == pytest.approx(5.0)
    with pytest.raises(ValueError):
        G.SquaredDistanceField([], cell=1.0)


# ------------------------------------------------------------------ linker reach (term (a) kernel)


def test_linker_visit_sum_and_detour_are_exact_on_a_collinear_construction():
    a, b = (0.0, 0.0, 0.0), (10.0, 0.0, 0.0)
    on_segment = (4.0, 0.0, 0.0)
    assert G.linker_visit_sum(a, b, on_segment) == pytest.approx(10.0)
    assert G.linker_detour(a, b, on_segment) == pytest.approx(0.0)
    # 3-4-5 triangles either side: sums to 2*5 = 10 from the midpoint offset by 3... construct exactly
    off = (5.0, 12.0, 0.0)                      # 5-12-13 both sides
    assert G.linker_visit_sum(a, b, off) == pytest.approx(26.0)
    assert G.linker_detour(a, b, off) == pytest.approx(16.0)


def test_linker_can_visit_is_the_prolate_spheroid_and_the_arm_relaxes_it_by_two_e():
    a, b = (0.0, 0.0, 0.0), (10.0, 0.0, 0.0)
    q = (5.0, 12.0, 0.0)                        # focal sum 26
    assert not G.linker_can_visit(a, b, q, contour_length=25.0)
    assert G.linker_can_visit(a, b, q, contour_length=26.0)
    # a 3 A pendant arm relaxes the requirement by exactly 2*3 = 6
    assert G.linker_can_visit(a, b, q, contour_length=20.0, arm_reach=3.0)
    assert not G.linker_can_visit(a, b, q, contour_length=19.9, arm_reach=3.0)


def test_contour_length_model_and_its_refusal():
    assert G.contour_length_from_atoms(8) == pytest.approx(10.0)
    assert G.contour_length_from_atoms(0) == 0.0
    with pytest.raises(ValueError):
        G.contour_length_from_atoms(-1)


# ------------------------------------------------------------------ WLC accessibility (piece 4 kernel)


def test_wlc_density_vanishes_at_and_beyond_the_contour_length():
    """The property a Gaussian chain gets WRONG, and the reason this form was chosen: a linker cannot span
    more than its own contour length, so a basin beyond it must have exactly zero accessibility."""
    L = 12.0
    assert G.wlc_end_to_end_density(L, L) == 0.0
    assert G.wlc_end_to_end_density(L + 1.0, L) == 0.0
    assert G.wlc_end_to_end_density(0.0, L) == 0.0
    assert G.wlc_end_to_end_density(6.0, L) > 0.0


def test_wlc_pdf_integrates_to_one_and_is_stiffness_ordered():
    L = 15.0
    for lp in (2.0, 4.0, 8.0):
        z = G.wlc_normalisation(L, lp, n_bins=2000)
        h = L / 2000
        total = sum(G.wlc_pdf((i + 0.5) * h, L, lp, norm_const=z) for i in range(2000)) * h
        assert total == pytest.approx(1.0, rel=1e-3)
    # a stiffer chain puts more weight near full extension
    def tail(lp):
        z = G.wlc_normalisation(L, lp, n_bins=2000)
        h = L / 2000
        return sum(G.wlc_pdf((i + 0.5) * h, L, lp, norm_const=z) for i in range(1400, 2000)) * h
    assert tail(8.0) > tail(2.0)


def test_wlc_refuses_nonphysical_parameters():
    with pytest.raises(ValueError):
        G.wlc_end_to_end_density(1.0, 0.0)
    with pytest.raises(ValueError):
        G.wlc_end_to_end_density(1.0, 10.0, persistence_length=0.0)


# ------------------------------------------------------------------ clustering


def test_landmark_rmsd_does_not_superpose_so_rotated_placements_stay_distinct():
    """A basin is a PLACEMENT. Two placements related by a large rotation about the target must not collapse
    into one cluster just because the E3's internal structure is identical."""
    lm = [(0.0, 0.0, 0.0), (10.0, 0.0, 0.0), (0.0, 10.0, 0.0)]
    Rz = G.quat_to_matrix((math.cos(math.pi / 4), 0.0, 0.0, math.sin(math.pi / 4)))   # 90 deg
    rotated = [G.matvec(Rz, p) for p in lm]
    assert G.landmark_rmsd(lm, lm) == pytest.approx(0.0)
    assert G.landmark_rmsd(lm, rotated) > 5.0
    with pytest.raises(ValueError):
        G.landmark_rmsd(lm, lm[:2])


def test_leader_cluster_recovers_three_planted_groups_and_orders_by_key():
    groups = {"a": (0.0, 0.0, 0.0), "b": (40.0, 0.0, 0.0), "c": (0.0, 40.0, 0.0)}
    rng = random.Random(2)
    items = []
    for gname, c in groups.items():
        for i in range(10):
            jitter = [(c[0] + rng.gauss(0, 0.4), c[1] + rng.gauss(0, 0.4), c[2] + rng.gauss(0, 0.4))]
            items.append({"g": gname, "lm": jitter, "score": rng.random()})
    cl = G.leader_cluster(items, lambda it: it["lm"], cutoff=5.0, key=lambda it: it["score"])
    assert len(cl) == 3
    for c in cl:
        assert len({it["g"] for it in c}) == 1
    # best-first: each cluster's leader is its own top-scoring member
    for c in cl:
        assert c[0]["score"] == max(it["score"] for it in c)


def test_farthest_point_sample_spreads_and_degrades_gracefully():
    pts = [(0.0, 0.0, 0.0), (0.1, 0.0, 0.0), (0.2, 0.0, 0.0), (50.0, 0.0, 0.0), (0.0, 50.0, 0.0)]
    idx = G.farthest_point_sample(pts, 3)
    assert set(idx) == {0, 3, 4}
    assert G.farthest_point_sample(pts, 99) == list(range(5))
    assert G.farthest_point_sample(pts, 0) == []


# ------------------------------------------------------------------ E2 swing sampling


def test_spherical_cap_sampling_respects_the_half_angle_and_is_area_uniform():
    rng = random.Random(23)
    axis = (0.0, 0.0, 1.0)
    half = 40.0
    cosines = []
    for _ in range(5000):
        v = G.sample_spherical_cap(rng, axis, half)
        assert G.norm(v) == pytest.approx(1.0, rel=1e-9)
        c = G.dot(v, axis)
        assert c >= math.cos(math.radians(half)) - 1e-9
        cosines.append(c)
    # uniform-in-area => cos(theta) ~ Uniform[cos(alpha), 1]; mean is the midpoint
    expected = 0.5 * (1.0 + math.cos(math.radians(half)))
    assert sum(cosines) / len(cosines) == pytest.approx(expected, abs=0.02)
