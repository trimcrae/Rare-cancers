"""Unit tests for the RUNG-5b inverse-linker-design kernels.

Every test below is against a CLOSED-FORM answer, a hand-constructed case, or an identity the module must
share with `basin_geom` — never against a previously-observed output of the module itself. The two that carry
the most weight are:

  * `test_branch_window_matches_basin_geom_criterion` — the branch-position kernel must agree, in the
    continuous limit, with the exact spheroid criterion RUNG 5a's term-(a) GATE was read on. If it ever
    disagrees, the 5b library would be designed against a different feasibility rule than the gate that
    nominated the basins, and nothing downstream would announce it.
  * `test_wlc_density_matches_basin_geom` — `_wlc_density` is a deliberate duplicate of
    `basin_geom.wlc_end_to_end_density` (so this module imports nothing); the duplicate is pinned here so it
    cannot drift.
"""
import math
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import basin_geom as G          # noqa: E402
import linker_design as LD      # noqa: E402


# ---------------------------------------------------------------------------------------------------------
# three_ball_min_margin — closed-form cases
# ---------------------------------------------------------------------------------------------------------


def test_single_ball_margin_is_negative_radius():
    """One ball: the minimiser is its centre and the margin is exactly -r."""
    m, p = LD.three_ball_min_margin([(1.0, 2.0, 3.0)], [2.5])
    assert m == pytest.approx(-2.5, abs=1e-6)
    assert LD._dist(p, (1.0, 2.0, 3.0)) < 1e-5


def test_two_disjoint_balls_margin_is_half_the_gap():
    """Two equal balls at separation d > 2r: the optimum sits at the midpoint with margin d/2 - r."""
    a, b, r = (0.0, 0.0, 0.0), (10.0, 0.0, 0.0), 2.0
    m, p = LD.three_ball_min_margin([a, b], [r, r])
    assert m == pytest.approx(5.0 - r, abs=1e-4)
    assert p[0] == pytest.approx(5.0, abs=1e-3)


def test_equilateral_triangle_threshold_is_the_circumradius():
    """Three equal balls on an equilateral triangle of side s intersect iff r >= circumradius = s/sqrt(3).

    Exact, and the sharpest available test of the solver: it must return a margin that changes sign precisely
    at r = s/sqrt(3).
    """
    s = 6.0
    verts = [(0.0, 0.0, 0.0), (s, 0.0, 0.0), (s / 2.0, s * math.sqrt(3) / 2.0, 0.0)]
    circ = s / math.sqrt(3.0)
    m_at, _ = LD.three_ball_min_margin(verts, [circ] * 3)
    assert m_at == pytest.approx(0.0, abs=1e-3)
    assert LD.three_ball_min_margin(verts, [circ * 1.05] * 3)[0] < 0.0
    assert LD.three_ball_min_margin(verts, [circ * 0.95] * 3)[0] > 0.0
    assert LD.balls_intersect(verts, [circ * 1.05] * 3)
    assert not LD.balls_intersect(verts, [circ * 0.95] * 3)


def test_margin_is_monotone_in_radius():
    """Growing every ball can only make the intersection easier — a structural property of the objective."""
    c = [(0.0, 0.0, 0.0), (7.0, 1.0, 0.0), (2.0, 6.0, 1.0)]
    prev = None
    for r in (1.0, 2.0, 3.0, 4.0, 5.0):
        m, _ = LD.three_ball_min_margin(c, [r] * 3)
        if prev is not None:
            assert m < prev + 1e-9
        prev = m


def test_rejects_mismatched_inputs():
    with pytest.raises(ValueError):
        LD.three_ball_min_margin([(0, 0, 0)], [1.0, 2.0])
    with pytest.raises(ValueError):
        LD.three_ball_min_margin([], [])
    with pytest.raises(ValueError):
        LD.three_ball_min_margin([(0, 0, 0)], [-1.0])
    with pytest.raises(ValueError):        # the in-plane reduction is only a statement about 3 centres
        LD.three_ball_min_margin([(0, 0, 0)] * 4, [1.0] * 4)


def test_witness_point_always_realises_the_reported_margin():
    """The returned point must actually achieve the returned value — an argmin nobody checked is exactly the
    populated-but-unmeasured field CLAUDE.md §4b warns about."""
    cases = [
        ([(0.0, 0.0, 0.0), (9.0, 2.0, -1.0), (3.0, 8.0, 4.0)], [5.0, 6.0, 3.0]),
        ([(0.0, 0.0, 0.0), (30.0, 0.0, 0.0), (15.0, 1.0, 0.0)], [12.0, 12.0, 2.0]),
        ([(0.0, 0.0, 0.0), (4.0, 0.0, 0.0), (8.0, 0.0, 0.0)], [1.0, 1.0, 1.0]),   # collinear
    ]
    for centers, radii in cases:
        m, p = LD.three_ball_min_margin(centers, radii)
        assert LD._max_violation(p, centers, radii) == pytest.approx(m, abs=1e-9)


def test_no_false_disjoint_when_a_witness_point_exists():
    """★ REGRESSION, MEASURED 2026-08-02 — the defect that blocked the 8XTT reach artifact.

    The kernel used to solve the in-plane problem with a coarse-to-fine 3x3 pattern search. f is convex but
    NOT differentiable, its minimiser lies on the ridge where cone terms are equal, and along that ridge every
    axis-aligned stencil direction is ascent — so the search stalled ON the answer and reported the balls
    DISJOINT when they demonstrably intersect. Measured on this exact geometry: returned +0.457272 against a
    true minimum of -0.030917 (error 0.488 A, ~500x the 1e-6 feasibility tolerance), identically at
    rounds = 50/100/200/400/800, with the stencil unable to improve at any of 10 scales from 10 A to 1e-6 A.

    Downstream, `min_linker_atoms_exact` therefore over-reported the required chain length by one backbone
    atom, which surfaced as `RULE_DRIFT` cells in `nr4a3_linker_covalent_reach.py` — the lattice-witness
    corridor rule was right and this kernel was wrong.

    The test asserts the property, not the historical number: a point that satisfies every ball proves the
    intersection is non-empty, so the reported margin may not be positive.
    """
    centers = [(0.0, 0.0, 0.0),
               (10.76425666336196, -1.2010692813571033, 1.564854060957357),
               (10.344120696299626, 1.388554467469497, 23.854919207677796)]
    radii = [20.0, 38.75, 6.10]
    m, p = LD.three_ball_min_margin(centers, radii)
    assert LD._max_violation(p, centers, radii) <= 1e-9
    assert m <= 0.0, "balls with a common point must not be reported disjoint (got %+.6f)" % m
    assert LD.balls_intersect(centers, radii)
    # and the value itself, against a dense scan of the segment joining ball 1 and ball 3
    assert m == pytest.approx(-0.030917, abs=1e-4)
    # the schedule kwargs are vestigial: an exact solver cannot depend on them
    for rounds in (1, 50, 800):
        for shrink in (0.6, 0.8, 0.95):
            assert LD.three_ball_min_margin(centers, radii, rounds, shrink)[0] == pytest.approx(m, abs=1e-12)


def _thin_lens_cases():
    """The geometry family the retired pattern search got wrong, enumerated deterministically.

    Shape: the warhead ball and the pendant ball overlap in a THIN LENS (|q-a| just inside ra + e) while the
    E3 ball is large enough to contain it. The optimum is then a small region far from the centroid the search
    started at, sitting on the ridge where two cone terms are equal — where the axis stencil has no descent
    direction. This is not a contrived corner: it is what a long linker reaching a barely-accessible cysteine
    looks like, which is why it appeared in the real 8XTT table.
    """
    for R in (10.0, 15.0, 20.0, 25.0, 30.0):
        for e in (3.0, 4.5, 6.1, 7.5):
            for delta in (0.02, 0.06, 0.15, 0.4):
                for bx in (8.0, 18.0, 25.0):
                    for tilt in (0.0, 0.35, 0.9):
                        a = (0.0, 0.0, 0.0)
                        b = (bx, -1.2, 1.5)
                        d_aq = R + e - delta
                        raw = (d_aq * math.sin(tilt) * 0.4, d_aq * math.sin(tilt) * 0.1,
                               d_aq * math.cos(tilt * 0.4))
                        n = math.sqrt(sum(x * x for x in raw))
                        if n == 0.0:
                            continue
                        q = tuple(x * d_aq / n for x in raw)
                        rb = max(LD._dist(q, b) + 5.0, 20.0)
                        yield a, b, q, R, rb, e, delta


def test_thin_lens_family_is_never_reported_disjoint():
    """★ THE REGRESSION WITH TEETH. Measured 2026-08-02: the retired pattern search reported 873 of these 720+
    geometries as DISJOINT when their balls overlap by construction, with errors up to +0.61 A. A plain
    lattice-witness sweep does NOT reproduce the defect (0 catches over 6591 cells), so asserting the
    invariant alone would have been a test that could never fail — this pins the failing family itself.

    Two balls overlapping by `delta` have min margin exactly -delta/2, and the third ball contains the lens,
    so the answer is known in closed form rather than compared against a previous output.
    """
    n_cases = 0
    for a, b, q, R, rb, e, delta in _thin_lens_cases():
        n_cases += 1
        m, p = LD.three_ball_min_margin([a, b, q], [R, rb, e])
        assert m < 0.0, ("thin lens (overlap %.3f A) reported disjoint at %+.6f" % (delta, m))
        assert m == pytest.approx(-delta / 2.0, abs=1e-6)
        assert LD._max_violation(p, [a, b, q], [R, rb, e]) <= 1e-9
        assert LD.balls_intersect([a, b, q], [R, rb, e])
    assert n_cases > 500, n_cases


def test_corridor_witness_can_never_beat_the_convex_solve():
    """THE INVARIANT THE REACH TABLE GATES ON, tested directly on the kernel.

    A lattice point p with |p-a| <= k*rise, |p-b| <= (n-k)*rise and |p-q| <= e is a witness that an n-atom
    linker branching at k reaches q. `branch_position_window` must therefore call n feasible. When it did not,
    the reach table's corridor rule returned a SHORTER chain than the through-space rule — an ordering the
    subset relation makes impossible — and the artifact was refused.

    Kept alongside the family test above, which is the one that reproduces the defect: this one states the
    property the driver actually depends on.
    """
    rise = LD.RISE_PER_ATOM_A
    checked = 0
    for b in ((18.0, 3.0, -2.0), (34.0, -6.0, 5.0)):
        for gx in range(-5, 6):
            for gy in range(-5, 6):
                for gz in range(-5, 6):
                    p = (gx * 2.5, gy * 2.5, gz * 2.5)
                    for e in (3.0, 6.1):
                        q = (p[0] + e, p[1], p[2])          # |p-q| == e exactly
                        a = (0.0, 0.0, 0.0)
                        ka = max(1, int(math.ceil(LD._dist(p, a) / rise - 1e-9)))
                        kb = max(1, int(math.ceil(LD._dist(p, b) / rise - 1e-9)))
                        n = ka + kb
                        if n > 80:
                            continue
                        w = LD.branch_position_window(a, b, q, n, e)
                        assert w["n_feasible"] > 0, (
                            "witness p=%s proves n=%d k=%d reaches q, but the window says infeasible "
                            "(best_margin %s)" % (p, n, ka, w["best_margin_A"]))
                        assert LD.min_linker_atoms_exact(a, b, q, e) <= n
                        checked += 1
    assert checked > 2000, checked


# ---------------------------------------------------------------------------------------------------------
# branch_position_window
# ---------------------------------------------------------------------------------------------------------


def test_branch_window_on_a_collinear_construction():
    """Hand-constructed: a and b are 10 A apart on the x-axis, the nucleophile sits ON the segment at x=4.

    With rise 1.25 and a zero-length arm, the branch atom must reach x=4 from a (needs k*1.25 >= 4, k >= 4)
    and reach b from there (needs (n-k)*1.25 >= 6, k <= n-5). For n=10 the window is exactly k in 4..5.
    """
    a, b, q = (0.0, 0.0, 0.0), (10.0, 0.0, 0.0), (4.0, 0.0, 0.0)
    w = LD.branch_position_window(a, b, q, n_atoms=10, arm_reach=0.0)
    assert w["feasible_k"] == [4, 5]
    assert w["k_min"] == 4 and w["k_max"] == 5


def test_branch_window_empty_when_linker_too_short():
    a, b, q = (0.0, 0.0, 0.0), (10.0, 0.0, 0.0), (4.0, 0.0, 0.0)
    w = LD.branch_position_window(a, b, q, n_atoms=6, arm_reach=0.0)
    assert w["feasible_k"] == [] and w["n_feasible"] == 0


def test_branch_window_widens_with_arm_reach():
    """A longer pendant can only add branch positions, never remove them."""
    a, b, q = (0.0, 0.0, 0.0), (12.0, 0.0, 0.0), (5.0, 3.0, 0.0)
    prev = None
    for e in (0.0, 1.0, 2.0, 3.0, 5.0):
        w = LD.branch_position_window(a, b, q, n_atoms=14, arm_reach=e)
        if prev is not None:
            assert set(prev).issubset(set(w["feasible_k"]))
        prev = w["feasible_k"]


def test_relaxed_rule_reproduces_basin_geom_exactly():
    """`min_linker_atoms_relaxed` must reproduce RUNG 5a's rule bit for bit — it is the thing being compared
    against, so a drift here would silently redefine the comparison."""
    a = (0.0, 0.0, 0.0)
    rise = LD.RISE_PER_ATOM_A
    for bx in (8.0, 14.0, 20.0):
        for qx, qy in ((3.0, 4.0), (10.0, 2.0), (6.0, 9.0), (-2.0, 5.0)):
            b, q = (bx, 0.0, 0.0), (qx, qy, 0.0)
            n_rel = LD.min_linker_atoms_relaxed(a, b, q, arm_reach=3.0)
            for n in range(1, 30):
                assert (n >= n_rel) == G.linker_can_visit(
                    a, b, q, G.contour_length_from_atoms(n, rise), arm_reach=3.0), (bx, qx, qy, n)


def test_relaxed_rule_is_a_strict_lower_bound_on_the_exact_one():
    """★ THE FINDING THIS MODULE ENCODES. RUNG 5a's criterion credits the pendant arm with shortening the
    ANCHOR-TO-ANCHOR SPAN, which no pendant can do — the linker must still connect a to b. So the exact
    requirement is never shorter than the relaxed one, and on a nucleophile sitting on the segment it is
    longer by the full span the rule gave away.

    The construction is closed-form: a and b are 16 A apart, q sits ON the segment. The relaxed rule sees
    focal sum = span = 16, subtracts 2e = 6, and returns ceil(10/1.25) = 8 atoms. The truth is that the chain
    must span 16 A, needing ceil(16/1.25) = 13.
    """
    a, b, q = (0.0, 0.0, 0.0), (16.0, 0.0, 0.0), (8.0, 0.0, 0.0)
    assert LD.min_linker_atoms_relaxed(a, b, q, arm_reach=3.0) == 8
    assert LD.span_floor_atoms(a, b) == 13
    assert LD.min_linker_atoms_exact(a, b, q, arm_reach=3.0) == 13


def test_exact_is_never_below_relaxed_or_the_span_floor():
    """The two structural inequalities, over a grid of geometries. Both are provable, neither is fitted."""
    a = (0.0, 0.0, 0.0)
    for bx in (6.0, 12.0, 18.0):
        for qx, qy in ((3.0, 4.0), (10.0, 2.0), (6.0, 9.0), (-2.0, 5.0), (9.0, 0.5)):
            b, q = (bx, 0.0, 0.0), (qx, qy, 0.0)
            ex = LD.min_linker_atoms_exact(a, b, q, arm_reach=3.0)
            assert ex is not None
            assert ex >= LD.min_linker_atoms_relaxed(a, b, q, arm_reach=3.0)
            assert ex >= LD.span_floor_atoms(a, b)
            # ... and never worse than the zero-arm solution, which is always available
            assert ex <= math.ceil(LD._dist(q, a) / 1.25) + math.ceil(LD._dist(q, b) / 1.25)


def test_branch_window_shortcircuits_agree_with_the_full_solve():
    """`branch_position_window` short-circuits the convex solve on two exact conditions (pairwise-overlap
    necessity; q-inside-both-anchor-balls sufficiency). Both must give the same verdict as the solve itself,
    over a grid that exercises all three branches — otherwise the speed-up would be silently changing answers.
    """
    a = (0.0, 0.0, 0.0)
    rise = LD.RISE_PER_ATOM_A
    for bx in (6.0, 13.0, 19.0):
        for qx, qy, qz in ((3.0, 4.0, 0.0), (10.0, 2.0, 1.0), (5.0, 9.0, -2.0), (14.0, 1.0, 0.5)):
            b, q = (bx, 0.0, 0.0), (qx, qy, qz)
            for n in range(3, 24):
                got = LD.branch_position_window(a, b, q, n, arm_reach=3.0)["feasible_k"]
                want = [k for k in range(1, n)
                        if LD.three_ball_min_margin([a, b, q],
                                                    [k * rise, (n - k) * rise, 3.0])[0] <= 1e-6]
                assert got == want, (bx, qx, qy, qz, n, got, want)


def test_min_linker_atoms_for_reach_is_the_closed_form():
    a, b, q = (0.0, 0.0, 0.0), (10.0, 0.0, 0.0), (3.0, 4.0, 0.0)
    # |q-a| = 5, |q-b| = sqrt(49+16) = 8.0623 ; focal sum 13.0623; arm 3 -> need 7.0623 / 1.25 = 5.65 -> 6
    assert LD.min_linker_atoms_for_reach(a, b, q, arm_reach=3.0) == 6
    assert LD.min_linker_atoms_for_reach(a, b, q, arm_reach=0.0) == math.ceil(13.06225 / 1.25)
    assert LD.min_linker_atoms_for_reach is LD.min_linker_atoms_relaxed


def test_zero_arm_exact_requirement_is_the_two_leg_sum():
    """With no pendant, the branch atom must BE the nucleophile, so the answer is exactly the sum of the two
    legs rounded up independently — a closed form, and the tightest available check on the integer bookkeeping.
    """
    a, b, q = (0.0, 0.0, 0.0), (14.0, 0.0, 0.0), (5.0, 6.0, 0.0)
    expect = math.ceil(LD._dist(q, a) / 1.25) + math.ceil(LD._dist(q, b) / 1.25)
    assert LD.min_linker_atoms_exact(a, b, q, arm_reach=0.0) == expect


def test_exact_scan_start_is_exact_not_a_heuristic():
    """`min_linker_atoms_exact` starts its scan at max(span floor, relaxed bound) rather than at n=2, which is
    what makes it affordable inside RUNG 5a's inner loop (~10^5 calls). Both skipped bounds are provable
    necessary conditions, so the shortcut must return the IDENTICAL answer to a scan from the bottom — if it
    ever did not, the speed-up would be silently redefining the corrected gate.
    """
    def naive(a, b, q, e, n_max=40):
        for n in range(2, n_max + 1):
            if LD.branch_position_window(a, b, q, n, e)["n_feasible"] > 0:
                return n
        return None

    a = (0.0, 0.0, 0.0)
    for bx in (5.0, 11.0, 17.0, 23.0):
        for qx, qy, qz in ((3.0, 4.0, 0.0), (10.0, 2.0, 1.0), (5.0, 9.0, -2.0),
                           (bx / 2.0, 0.0, 0.0), (-4.0, 3.0, 2.0), (bx + 6.0, 0.0, 0.0)):
            for e in (0.0, 3.0, 8.75):
                b, q = (bx, 0.0, 0.0), (qx, qy, qz)
                assert LD.min_linker_atoms_exact(a, b, q, e, n_max=40) == naive(a, b, q, e), (bx, qx, qy, qz, e)


def test_pendant_reach_table_is_shared_with_the_rung5a_gate():
    """One definition, two rungs (CLAUDE.md §1). The RUNG-5a gate value must be the first entry and must be
    the SHORTEST — a sweep that let the gate sit on a longer pendant would be a tuned knob, not a sensitivity.
    """
    t = LD.PENDANT_REACH_A
    assert t["rung5a_convention"] == 3.0
    assert min(t.values()) == t["rung5a_convention"]


def test_exact_requirement_returns_none_when_out_of_range():
    a, b, q = (0.0, 0.0, 0.0), (10.0, 0.0, 0.0), (400.0, 0.0, 0.0)
    assert LD.min_linker_atoms_exact(a, b, q, arm_reach=3.0, n_max=20) is None


def test_pendant_contactable_uses_the_exact_rule():
    a, b, q = (0.0, 0.0, 0.0), (16.0, 0.0, 0.0), (8.0, 0.0, 0.0)
    assert not LD.pendant_contactable(a, b, q, n_atoms=12, arm_reach=3.0)   # relaxed rule would say yes at 8
    assert LD.pendant_contactable(a, b, q, n_atoms=13, arm_reach=3.0)


# ---------------------------------------------------------------------------------------------------------
# WLC accessibility
# ---------------------------------------------------------------------------------------------------------


def test_wlc_density_matches_basin_geom():
    """The deliberate duplicate must equal the original, bit for bit, over the whole domain."""
    for L in (5.0, 12.5, 25.0):
        for r in [i * L / 20.0 for i in range(20)]:
            assert LD._wlc_density(r, L, 4.0) == G.wlc_end_to_end_density(r, L, 4.0)


def test_wlc_window_probability_is_a_probability():
    for n in (6, 10, 16, 24):
        p = LD.wlc_window_probability(0.0, n * LD.RISE_PER_ATOM_A, n)
        assert p == pytest.approx(1.0, abs=2e-3)      # the full support integrates to 1


def test_wlc_window_probability_zero_beyond_contour():
    """A basin whose spans exceed the contour length is unreachable — exactly zero, not a small number."""
    assert LD.wlc_window_probability(20.0, 25.0, n_atoms=8) == 0.0


def test_wlc_window_probability_windows_are_additive():
    n = 14
    L = n * LD.RISE_PER_ATOM_A
    lo, mid, hi = 0.0, L * 0.4, L * 0.999999
    a = LD.wlc_window_probability(lo, mid, n)
    b = LD.wlc_window_probability(mid, hi, n)
    assert a + b == pytest.approx(1.0, abs=5e-3)


def test_wlc_best_length_has_an_interior_optimum():
    """★ THE CENSORING FIX. The quantity RUNG 5a reported (a density) was still rising at the top of its
    scan; the probability integrated over the basin's span window must instead peak INSIDE a wide range."""
    best, p, meta = LD.wlc_best_length(8.0, 14.0, range(4, 61))
    assert not meta["at_boundary"]
    assert 8 <= best <= 24
    assert p > 0.0


def test_wlc_best_length_flags_a_boundary_optimum():
    """... and when the range is too narrow to contain the optimum, it says so rather than reporting an edge
    as an answer — the precise failure mode that produced `best_linker_atoms = 19` on 188 of 192 basins."""
    best, _, meta = LD.wlc_best_length(18.0, 26.0, range(3, 21, 2))
    assert meta["at_boundary"]
    assert best == 19


def test_wlc_mode_is_grid_independent():
    """The mode must not move when the bracketing grid is refined — the defect that made `wlc_strain_kt`
    return a small bin-count-dependent number at its own mode."""
    a = LD.wlc_mode(16, n_bins=200)
    b = LD.wlc_mode(16, n_bins=1600)
    assert a == pytest.approx(b, abs=1e-6)


def test_wlc_strain_is_zero_at_the_mode_and_rises_in_the_tail():
    n = 16
    L = n * LD.RISE_PER_ATOM_A
    assert LD.wlc_strain_kt(LD.wlc_mode(n), n) == pytest.approx(0.0, abs=1e-9)
    assert LD.wlc_strain_kt(L * 0.97, n) > LD.wlc_strain_kt(L * 0.8, n) > 0.0
    assert LD.wlc_strain_kt(L * 1.01, n) == float("inf")


def test_wlc_strain_is_never_negative():
    """Structural: a relative-to-the-mode log-ratio cannot be negative. Guards the clamp."""
    for n in (6, 12, 20):
        L = n * LD.RISE_PER_ATOM_A
        for i in range(1, 60):
            assert LD.wlc_strain_kt(i * L / 60.0, n) >= 0.0


# ---------------------------------------------------------------------------------------------------------
# Exit-vector geometry
# ---------------------------------------------------------------------------------------------------------


def test_dihedral_matches_a_known_construction():
    """A textbook +90 deg torsion: p1 on +y, p2-p3 along +x, p4 on +z."""
    p1, p2, p3, p4 = (0.0, 1.0, 0.0), (0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (1.0, 0.0, 1.0)
    assert abs(abs(LD.dihedral_deg(p1, p2, p3, p4)) - 90.0) < 1e-6


def test_dihedral_is_zero_when_coplanar_and_cis():
    p1, p2, p3, p4 = (0.0, 1.0, 0.0), (0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (1.0, 1.0, 0.0)
    assert LD.dihedral_deg(p1, p2, p3, p4) == pytest.approx(0.0, abs=1e-6)


def test_exit_geometry_taut_case_costs_nothing():
    """Both exit bonds pointing straight at each other: alpha = beta = 0 and no turn to pay for."""
    g = LD.exit_vector_geometry((0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (12.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    assert g["alpha_deg"] == pytest.approx(0.0, abs=1e-6)
    assert g["beta_deg"] == pytest.approx(0.0, abs=1e-6)
    assert g["turn_detour_A"] == pytest.approx(0.0, abs=1e-6)
    assert g["turn_penalty_atoms"] == 0


def test_exit_geometry_reversed_case_costs_two_bonds_per_end():
    """Both exit bonds pointing directly AWAY: the chain leaves along the bond then has to come all the way
    back, so each end costs exactly 2*rise of extra contour. Closed form, no fitting."""
    rise = LD.RISE_PER_ATOM_A
    g = LD.exit_vector_geometry((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0), (12.0, 0.0, 0.0), (1.0, 0.0, 0.0))
    assert g["alpha_deg"] == pytest.approx(180.0, abs=1e-4)
    assert g["beta_deg"] == pytest.approx(180.0, abs=1e-4)
    assert g["turn_detour_A"] == pytest.approx(4.0 * rise, abs=1e-6)
    assert g["turn_penalty_atoms"] == 4


def test_exit_geometry_span_matches_the_anchor_distance():
    g = LD.exit_vector_geometry((1.0, 2.0, 3.0), (0.0, 1.0, 0.0), (4.0, 6.0, 3.0), (0.0, -1.0, 0.0))
    assert g["span_A"] == pytest.approx(5.0, abs=1e-6)


def test_exit_geometry_rejects_coincident_anchors():
    with pytest.raises(ValueError):
        LD.exit_vector_geometry((0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (0.0, 0.0, 0.0), (1.0, 0.0, 0.0))
