#!/usr/bin/env python3
"""
Geometry + polymer-statistics kernels for RUNG 5b — INVERSE LINKER DESIGN.

WHY A SEPARATE KERNEL MODULE (same reason `basin_geom.py` exists). RUNG 5b turns a nominated *region of
orientation space* into *linker requirements*, and every requirement it emits is a geometric feasibility
question with a closed-form or convex answer: "can a linker of n backbone atoms, tethered at the warhead exit
vector and the E3 ligand exit atom, carry a pendant electrophile onto C397's SG — and if so, from WHICH
backbone atom?"; "what fraction of a linker's end-to-end distribution lands inside this basin's span window?".
Those must be right, and "right" here means unit-tested against closed-form answers, not eyeballed. The driver
(`nr4a3_linker_design.py`) imports these, so the tested code IS the run code.

Pure stdlib on purpose: the dev sandbox has no numpy/scipy/rdkit and RUNG 5b is a $0 CPU step. RDKit is used
ONLY to validate the emitted SMILES and compute descriptors, and that runs on a free CI runner inside the
pre-baked `triskit23/ternary-fep` image (CLAUDE.md §6: never solve a conda env in CI).

THE FOUR KERNELS THAT CARRY SCIENTIFIC WEIGHT

1. `three_ball_min_margin` — the convex feasibility core. A pendant group mounted on the k-th backbone atom of
   an n-atom linker can touch a point q iff there exists a point p with |p-a| <= k*rise, |p-b| <= (n-k)*rise
   and |p-q| <= e. That is the intersection of three balls, i.e. the sublevel set of the CONVEX function
   f(p) = max_i(|p-c_i| - r_i); the intersection is non-empty iff min_p f(p) <= 0. Solved in CLOSED FORM by
   enumerating the finitely many points that can carry the optimum of a max of three cone functions, so the
   answer is exact and reproducible rather than seeded by a random optimiser.
   ⚠ SUPERSEDED, retained: this kernel was a "deterministic coarse-to-fine pattern search over a box that
   provably contains the minimiser", described as "converged far below any chemically meaningful tolerance".
   The box claim was true; the convergence claim was FALSE, and it is why the 8XTT reach table could not be
   committed — see the `three_ball_min_margin` docstring for the measurement that retired it.

2. `branch_position_window` — the CHEMISTRY DELIVERABLE of this rung, and the thing STRATEGY.md's RUNG 5b asks
   for by name: "the library enumerates the ELECTROPHILE POSITION ON THE LINKER as a design variable". It is
   kernel 1 evaluated over every integer branch index k, returning the contiguous window of backbone atoms
   from which the electrophile can reach the target nucleophile. **Cross-validated against `basin_geom`**: in
   the continuous limit the union over k is non-empty iff |q-a| + |q-b| <= n*rise + 2e, which is exactly
   `basin_geom.linker_can_visit`. `tests/test_linker_design.py` asserts that identity, so this kernel cannot
   silently drift from the one the RUNG-5a gate was read on.

3. `wlc_window_probability` — the CORRECTED accessibility `P(B_k | d, s)` of STRATEGY.md load-bearing piece 4.
   RUNG 5a reported accessibility as the mean WLC *density* at the basin's spans, whose argmax over linker
   length is CENSORED at the top of the scanned grid (see the module docstring note below and the lane doc);
   a probability integrated over the basin's span window is dimensionless, comparable across basins and
   linker lengths, and has a genuine interior optimum. That optimum is the design answer: the linker length
   most likely to present an end-to-end distance compatible with the basin.

4. `exit_vector_geometry` — the exit-vector angles and the dihedral about the anchor-anchor axis. A linker
   does not leave either end isotropically: it leaves the warhead along the C5 substituent bond and leaves the
   E3 ligand along its own exit bond. If those two vectors point away from each other the linker must double
   back, and contour length spent doubling back is contour length not available for the span. `alpha`/`beta`
   quantify exactly that, and `turn_penalty_atoms` converts it into the currency a chemist pays in: extra
   backbone atoms.

★ A CENSORING BUG THIS MODULE EXISTS PARTLY TO FIX. `nr4a3-orientation-basins.json` reports
`best_linker_atoms = 19` on 188 of 192 basins. 19 is the LAST point of that scan (range(3, 21, 2)), and the
mean-density profile is still rising there for spans above ~12 A — for a 20 A span the true argmax is ~53
backbone atoms, far outside the scan. So the field is a grid edge, not an optimum, and it must not be read as
"a 19-atom linker is the right length". `wlc_window_probability` replaces it. The reconciliation note already
in STRATEGY.md ("`best_linker_atoms` is the length that best supports basin accessibility") is right about the
*quantity*; what was not known when it was written is that the *reported value* is censored.
"""
from __future__ import annotations

import math

# 1.53 A C-C bond at the 109.5 deg tetrahedral angle projects to 1.53*sin(54.75 deg) = 1.25 A per backbone
# atom for an all-anti sp3 chain. Same value as `basin_geom.contour_length_from_atoms`, deliberately: the
# 5b requirements have to be quoted in the same units the 5a gate was read in.
RISE_PER_ATOM_A = 1.25


# ---------------------------------------------------------------------------------------------------------
# Convex ball-intersection feasibility
# ---------------------------------------------------------------------------------------------------------


def _dist(p, q):
    return math.sqrt((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2 + (p[2] - q[2]) ** 2)


def _max_violation(p, centers, radii):
    return max(_dist(p, c) - r for c, r in zip(centers, radii))


def three_ball_min_margin(centers, radii, rounds: int = 50, shrink: float = 0.6):
    """min over p of max_i(|p - c_i| - r_i), and the argmin. <= 0 iff the balls have a common point.

    THE REDUCTION. Reflecting a point through the plane containing the centres leaves every |p - c_i|
    unchanged, so the objective is symmetric about that plane; being convex, its value at the midpoint of a
    reflected pair — the in-plane projection — is no worse. Hence **the minimiser always lies in the plane of
    the centres**, and a 3-D search is wasted work. (For <= 2 centres the answer is closed-form directly.)

    ★★ WHY THIS IS AN ENUMERATION AND NOT A SEARCH — MEASURED, NOT PREFERRED (2026-08-02). This kernel used to
    solve the in-plane problem with a coarse-to-fine 3x3 pattern search, documented as "converged far below any
    chemically meaningful tolerance". **That was false, and it silently reported balls as disjoint when they
    provably intersect.** f is convex but NOT differentiable: its minimiser sits on the kink ridge where two or
    three cone terms are equal, and along that ridge every axis-aligned stencil direction is ascent, so a
    compass search stalls ON the answer's ridge and cannot leave it. The measurement that retired it, at
    a = (0,0,0), b = (10.764, -1.201, 1.565), q = (10.344, 1.389, 23.855), radii (20.0, 38.75, 6.10):

      * the search returned +0.457272 A — "disjoint" — while the true minimum is -0.030917, i.e. the balls DO
        intersect. Error 0.488 A, ~500x the 1e-6 feasibility tolerance the answer is compared against.
      * it is NOT a convergence budget: rounds = 50, 100, 200, 400 and 800 all return the identical value at
        the identical point.
      * at the returned point the 3x3 stencil improves at 0 of 10 scales from 10 A down to 1e-6 A, yet a
        descent direction does exist off-stencil (158.5 deg) — the definition of a stalled pattern search.
      * the returned value depended on the search SCHEDULE rather than the geometry: shrink = 0.8 gave the
        right answer where the shipped shrink = 0.6 gave the wrong one.

    Over 50,927 randomly sampled (a, b, q, k, n) cells in the range the reach table actually explores, 40 were
    reported infeasible while an explicit witness point proves they intersect. Downstream this made
    `min_linker_atoms_exact` over-report the required chain length by one backbone atom, which is what surfaced
    as the `RULE_DRIFT` cells that blocked the 8XTT reach artifact: the lattice-witness "corridor" rule was
    right and this solver was wrong. `rounds`/`shrink` are retained only so existing call sites keep working;
    the exact solver ignores them.

    THE ENUMERATION, AND WHY IT IS COMPLETE. Let A be the set of terms attaining the max at the optimum p*:
      |A| = 1, say {i} — f = g_i near p*, so p* minimises a single cone: p* = c_i.
      |A| = 2, say {i, j} — 0 in conv{grad g_i, grad g_j} forces the two unit vectors to be opposed, so p* lies
        ON the segment c_i c_j, and g_i = g_j pins it at |p*-c_i| = (d + r_i - r_j)/2 (clamped to the segment).
      |A| = 3 — all three equal some t, i.e. |p*-c_i| = r_i + t. Differencing pairs of those squared equations
        gives two equations linear in (p*, t); solving them expresses p* affinely in t, and substituting back
        into one circle equation leaves a scalar quadratic in t whose roots are the only candidates.
    Three centres, three pairs and at most two equalisation roots is at most 8 points. Every candidate is a
    real point, so evaluating f at all of them can never under-report; the optimum is always among them, so it
    can never over-report either. Collinear centres degenerate the |A| = 3 system, and are exactly the case
    where the optimum already lies on the line and is therefore a |A| <= 2 candidate, so skipping the
    degenerate solve is safe rather than approximate.
    """
    if len(centers) != len(radii):
        raise ValueError("centers and radii must be paired")
    if not centers:
        raise ValueError("need at least one ball")
    if any(r < 0 for r in radii):
        raise ValueError("radii must be >= 0")
    if len(centers) > 3:
        # The in-plane reduction is a statement about the plane of THREE points. Refusing is strictly better
        # than silently returning the wrong number for a case no caller has ever needed (CLAUDE.md §4).
        raise ValueError("three_ball_min_margin solves at most three balls; got %d" % len(centers))
    if len(centers) == 1:
        return -radii[0], tuple(centers[0])
    if len(centers) == 2:
        c0, c1 = tuple(centers[0]), tuple(centers[1])
        r0, r1 = radii
        dd = _dist(c0, c1)
        if dd == 0.0:
            return -min(r0, r1), c0
        # Along the line: f(s) = max(s - r0, d - s - r1) is minimised at s = (d + r0 - r1)/2, clamped so the
        # optimum never leaves the segment (outside it both terms only grow).
        s = min(max((dd + r0 - r1) / 2.0, 0.0), dd)
        u = tuple((c1[i] - c0[i]) / dd for i in range(3))
        p = tuple(c0[i] + s * u[i] for i in range(3))
        return _max_violation(p, centers, radii), p

    o = tuple(centers[0])
    e1 = _sub(centers[1], o)
    n1 = math.sqrt(_dot(e1, e1))
    if n1 == 0.0:
        return three_ball_min_margin(list(centers[1:]), list(radii[1:]), rounds, shrink)
    e1 = tuple(x / n1 for x in e1)
    w = _sub(centers[2], o)
    proj = _dot(w, e1)
    e2 = tuple(w[i] - proj * e1[i] for i in range(3))
    n2 = math.sqrt(_dot(e2, e2))
    collinear = n2 < 1e-12
    if collinear:                        # collinear centres: any orthogonal completes the plane
        tmp = (1.0, 0.0, 0.0) if abs(e1[0]) < 0.9 else (0.0, 1.0, 0.0)
        e2 = _cross(e1, tmp)
        n2 = math.sqrt(_dot(e2, e2))
    e2 = tuple(x / n2 for x in e2)

    flat = [(_dot(_sub(c, o), e1), _dot(_sub(c, o), e2)) for c in centers]

    def f2(x, y):
        return max(math.sqrt((x - cx) ** 2 + (y - cy) ** 2) - r
                   for (cx, cy), r in zip(flat, radii))

    cands = list(flat)                                       # |A| = 1: the centres themselves
    for i in range(3):                                       # |A| = 2: the pairwise segment optima
        for j in range(i + 1, 3):
            (xi, yi), ri = flat[i], radii[i]
            (xj, yj), rj = flat[j], radii[j]
            d = math.hypot(xj - xi, yj - yi)
            if d == 0.0:
                continue
            s = min(max((d + ri - rj) / 2.0, 0.0), d)
            cands.append((xi + s * (xj - xi) / d, yi + s * (yj - yi) / d))
    if not collinear:                                        # |A| = 3: the equalisation roots
        (x1, y1), r1 = flat[0], radii[0]
        (x2, y2), r2 = flat[1], radii[1]
        (x3, y3), r3 = flat[2], radii[2]
        a1, b1 = 2.0 * (x2 - x1), 2.0 * (y2 - y1)
        c1 = (x2 * x2 + y2 * y2) - (x1 * x1 + y1 * y1) + (r1 * r1 - r2 * r2)
        d1 = 2.0 * (r1 - r2)
        a2, b2 = 2.0 * (x3 - x1), 2.0 * (y3 - y1)
        c2 = (x3 * x3 + y3 * y3) - (x1 * x1 + y1 * y1) + (r1 * r1 - r3 * r3)
        d2 = 2.0 * (r1 - r3)
        det = a1 * b2 - a2 * b1
        if abs(det) > 1e-12:
            # p(t) = p0 + p1 * t, from the two linear difference equations
            px0, px1 = (c1 * b2 - c2 * b1) / det, (d1 * b2 - d2 * b1) / det
            py0, py1 = (a1 * c2 - a2 * c1) / det, (a1 * d2 - a2 * d1) / det
            u0, u1 = px0 - x1, px1
            v0, v1 = py0 - y1, py1
            qa = u1 * u1 + v1 * v1 - 1.0
            qb = 2.0 * (u0 * u1 + v0 * v1 - r1)
            qc = u0 * u0 + v0 * v0 - r1 * r1
            roots = []
            if abs(qa) < 1e-14:
                if abs(qb) > 1e-14:
                    roots.append(-qc / qb)
            else:
                disc = qb * qb - 4.0 * qa * qc
                if disc >= 0.0:
                    sq = math.sqrt(disc)
                    roots.extend([(-qb + sq) / (2.0 * qa), (-qb - sq) / (2.0 * qa)])
            for t in roots:
                cands.append((px0 + px1 * t, py0 + py1 * t))

    x, y = min(cands, key=lambda c: f2(c[0], c[1]))
    p = tuple(o[i] + x * e1[i] + y * e2[i] for i in range(3))
    return _max_violation(p, centers, radii), p


def balls_intersect(centers, radii, tol: float = 1e-6) -> bool:
    """True iff the given balls have a common point (within `tol`)."""
    return three_ball_min_margin(centers, radii)[0] <= tol


# ---------------------------------------------------------------------------------------------------------
# Electrophile branch position — the design variable RUNG 5b is asked to enumerate
# ---------------------------------------------------------------------------------------------------------


def branch_position_window(anchor_a, anchor_b, nucleophile, n_atoms: int, arm_reach: float,
                           rise: float = RISE_PER_ATOM_A):
    """Which backbone atoms of an n-atom linker can carry a pendant that reaches `nucleophile`?

    `anchor_a` is the warhead-side attachment point (backbone atom 0), `anchor_b` the E3-side one (backbone
    atom n). Branch index k in 1..n-1 counts backbone atoms from the WARHEAD end, which is the direction a
    chemist builds in and the direction the exit-vector handle fixes.

    `arm_reach` is the distance from the branch backbone atom to the nucleophile's reactive atom when the
    pendant is engaged — i.e. it absorbs the whole branch group (side chain + amide + Michael acceptor + the
    forming C-S bond). It is the SAME quantity `basin_geom.linker_can_visit` calls `arm_reach`, so the two
    modules can be compared directly; RUNG 5a read its gate at 3.0 A, which is conservative for every real
    pendant enumerated in the driver.

    Returns {"feasible_k": [...], "k_min", "k_max", "n_feasible", "best_k", "best_margin"} — `best_k` is the
    branch index with the most geometric slack, which is the one to design at because it is the least
    sensitive to the pose conditionality everything in this rung inherits.
    """
    if n_atoms < 2:
        return {"feasible_k": [], "k_min": None, "k_max": None, "n_feasible": 0,
                "best_k": None, "best_margin": None}
    a, b, q = tuple(anchor_a), tuple(anchor_b), tuple(nucleophile)
    da, db, dab = _dist(q, a), _dist(q, b), _dist(a, b)
    feasible, margins = [], {}
    for k in range(1, n_atoms):
        ra, rb = k * rise, (n_atoms - k) * rise
        # Closed-form short circuits, so the convex solve is only paid for the genuinely ambiguous k. Each is
        # exact, not a heuristic: NECESSARY — every pair of the three balls must itself overlap; SUFFICIENT —
        # if q is already inside both anchor balls then p = q is a witness.
        if ra + rb < dab or ra + arm_reach < da or rb + arm_reach < db:
            margins[k] = max(dab - ra - rb, da - ra - arm_reach, db - rb - arm_reach)
            continue
        if da <= ra and db <= rb:
            margins[k] = -min(ra - da, rb - db, arm_reach)
            feasible.append(k)
            continue
        m, _ = three_ball_min_margin([a, b, q], [ra, rb, arm_reach])
        margins[k] = m
        if m <= 1e-6:
            feasible.append(k)
    best_k = min(margins, key=lambda k: margins[k]) if margins else None
    return {
        "feasible_k": feasible,
        "k_min": feasible[0] if feasible else None,
        "k_max": feasible[-1] if feasible else None,
        "n_feasible": len(feasible),
        "best_k": best_k,
        "best_margin_A": round(margins[best_k], 3) if best_k is not None else None,
    }


def min_linker_atoms_relaxed(anchor_a, anchor_b, nucleophile, arm_reach: float,
                             rise: float = RISE_PER_ATOM_A) -> int:
    """The RUNG-5a criterion, reproduced exactly, and flagged for what it is: a LOWER BOUND.

        |q-a| + |q-b| <= n*rise + 2*arm_reach          (`basin_geom.linker_can_visit`)

    ★ WHY IT IS A LOWER BOUND, AND BY EXACTLY HOW MUCH. The inequality is derived from
    min over {p : |p-q| <= e} of (|p-a| + |p-b|)  >=  |q-a| + |q-b| - 2e, which is TIGHT only when the ball
    around q can be traversed in a direction that shortens the distance to *both* anchors at full rate — i.e.
    when q is collinear with, and between, a and b. Off that degenerate line the true minimum is strictly
    larger, so the true linker requirement is strictly longer.

    The sharpest way to see the size of the loophole: since |q-a| + |q-b| >= |a-b| by the triangle
    inequality, a nucleophile sitting ON the anchor-anchor segment makes the rule read `span <= n*rise + 2e`
    — i.e. it credits the pendant arm with shortening the SPAN, when in fact the linker must physically
    connect a to b and needs n*rise >= span no matter how long the pendant is. The slack is therefore bounded
    by 2*arm_reach (6.0 A, ~5 backbone atoms, at the 3.0 A arm the RUNG-5a gate was read with).

    This is NOT a claim that any published RUNG-5a number is wrong: audited over all 576
    (basin x unique cysteine) records in `nr4a3-orientation-basins.json`, **zero** have a reported
    `min_linker_atoms` below the same record's `min_linker_atoms_for_span`, so no basin's reported figure is
    internally impossible. What it does mean is that every such figure is a **lower bound on the length a
    linker actually has to be**, and RUNG 5b — which has to hand a chemist a number — must use
    `min_linker_atoms_exact` instead. Kept here, under its own name, so the two rules can be compared rather
    than conflated.
    """
    s = _dist(nucleophile, anchor_a) + _dist(nucleophile, anchor_b)
    need = max(0.0, s - 2.0 * arm_reach)
    return int(math.ceil(need / rise))


# Backwards-compatible alias: this is the name the RUNG-5a vocabulary uses.
min_linker_atoms_for_reach = min_linker_atoms_relaxed


def span_floor_atoms(anchor_a, anchor_b, rise: float = RISE_PER_ATOM_A) -> int:
    """Backbone atoms needed simply to CONNECT the two anchors. No pendant can substitute for this."""
    return int(math.ceil(_dist(anchor_a, anchor_b) / rise))


def min_linker_atoms_exact(anchor_a, anchor_b, nucleophile, arm_reach: float,
                           rise: float = RISE_PER_ATOM_A, n_max: int = 80):
    """Shortest linker that can BOTH span the anchors AND present a pendant of reach `arm_reach` on the
    nucleophile from an integer backbone position. `None` if no linker up to `n_max` can.

    Monotone in n (growing the linker grows every branch ball), so a linear scan is both correct and cheap.

    ★ WHERE THE SCAN STARTS, AND WHY IT IS NOT AN APPROXIMATION. Feasibility at n implies BOTH published
    necessary conditions, so the scan may skip every n below their maximum without changing a single answer:
      * the SPAN FLOOR. A witness p obeys |p-a| <= k*rise and |p-b| <= (n-k)*rise, so
        |a-b| <= |p-a| + |p-b| <= n*rise, i.e. n >= ceil(|a-b|/rise).
      * the RELAXED (RUNG-5a) BOUND. The same witness obeys |q-a| + |q-b| <= (|p-a| + e) + (|p-b| + e)
        <= n*rise + 2e, i.e. n >= ceil((|q-a| + |q-b| - 2e)/rise) = `min_linker_atoms_relaxed`.
    Starting at the larger of the two is therefore EXACT, not a heuristic, and it is what makes this callable
    ~10^5 times inside the RUNG-5a inner loop instead of only on a handful of exemplars.
    `tests/test_linker_design.py` pins the identity against a scan that starts at n=2.
    """
    lo = max(span_floor_atoms(anchor_a, anchor_b, rise),
             min_linker_atoms_relaxed(anchor_a, anchor_b, nucleophile, arm_reach, rise))
    for n in range(max(2, lo), n_max + 1):
        if branch_position_window(anchor_a, anchor_b, nucleophile, n, arm_reach, rise)["n_feasible"] > 0:
            return n
    return None


# ---------------------------------------------------------------------------------------------------------
# Named pendant building blocks — ONE definition, shared by RUNG 5a's reach gate and RUNG 5b's enumerator
# ---------------------------------------------------------------------------------------------------------

# `arm_reach` in Angstrom: the through-space distance from the LINKER BACKBONE atom carrying the branch to the
# target atom being touched, with the branch fully engaged (side chain + any amide + the Michael acceptor + the
# forming C-S bond). These are NAMED, commercially routine groups, so a sweep over them is a sweep over
# BUILDING BLOCKS, not over a knob — which is the only reason a sensitivity sweep is admissible under
# STRATEGY.md load-bearing piece 5 (no tunable scalar).
#
# ⚠ `rung5a_convention` (3.0 A) is the PREREGISTERED value the Tier-2 term-(a) gate is read at, and it stays
# the gate value. It is SHORTER than every real pendant below, i.e. conservative — so the longer entries are a
# labelled sensitivity, never a rescue. Moving the gate onto a longer pendant after seeing a result would be
# exactly the tuning the preregistration forbids.
PENDANT_REACH_A = {
    "rung5a_convention": 3.0,        # what the RUNG-5a gate used. Kept so the two can be compared.
    "aryl_direct": 4.0,              # a pyridyl/phenyl bonded straight to a backbone carbon
    "aryl_branch_residue": 4.5,      # the ring nitrogen of a 3-(3-pyridyl)-L-Ala side chain, measured from
                                     # the branch alpha-carbon: CA-CB (1.53) + CB-ipso (1.51) + two ring
                                     # bonds to the meta nitrogen (~2.4), through-space, between the compact
                                     # and fully extended rotamers
    "amide_direct": 5.0,             # backbone N-acylated: N-C(=O)-C(alpha)=C(beta)...S
    "dap_branch": 7.5,               # 2,3-diaminopropanoyl branch + acrylamide: 6 atoms
    "dab_branch": 8.75,              # 2,4-diaminobutanoyl branch + acrylamide: 7 atoms
}


def pendant_contactable(anchor_a, anchor_b, point, n_atoms: int, arm_reach: float,
                        rise: float = RISE_PER_ATOM_A) -> bool:
    """Can ANY backbone atom of an n-atom linker carry a pendant of reach `arm_reach` onto `point`?

    Used for the wedge-element site search: which target residues could a linker substituent touch at all?
    Uses the EXACT rule (three balls, integer branch positions), not the relaxed one, because the whole point
    of the wedge-element search is to hand back a site a chemist can actually put a group on.
    """
    return branch_position_window(anchor_a, anchor_b, point, n_atoms, arm_reach, rise)["n_feasible"] > 0


# ---------------------------------------------------------------------------------------------------------
# Worm-like-chain accessibility, as a PROBABILITY over the basin's span window
# ---------------------------------------------------------------------------------------------------------


def _wlc_density(r: float, L: float, lp: float) -> float:
    """Thirumalai-Ha mean-field radial density, unnormalised. Same functional form as
    `basin_geom.wlc_end_to_end_density` — duplicated rather than imported so this module stays importable on
    its own, and asserted equal to it in the test suite so the duplicate can never drift."""
    if L <= 0.0 or lp <= 0.0:
        raise ValueError("contour and persistence lengths must be > 0")
    if r < 0.0 or r >= L:
        return 0.0
    x = r / L
    t = 3.0 * L / (2.0 * lp)
    one_minus = 1.0 - x * x
    expo = -3.0 * t / (4.0 * one_minus)
    if expo < -700.0:
        return 0.0
    return 4.0 * math.pi * r * r * one_minus ** (-4.5) * math.exp(expo)


def wlc_window_probability(r_lo: float, r_hi: float, n_atoms: int, lp: float = 4.0,
                           rise: float = RISE_PER_ATOM_A, n_bins: int = 800) -> float:
    """P(end-to-end distance falls in [r_lo, r_hi]) for a WLC of `n_atoms` backbone atoms.

    THIS is `P(B_k | d, s)`: the probability that a candidate linker presents an end-to-end distance
    compatible with the basin, given the basin's observed span window. Unlike a density it is dimensionless,
    comparable across basins and lengths, and — the point — it has an interior optimum in `n_atoms`, so it
    answers "how long should this linker be?" instead of returning the top of whatever grid was scanned.
    """
    L = n_atoms * rise
    if r_hi <= r_lo:
        raise ValueError("r_hi must exceed r_lo")
    if r_lo >= L:
        return 0.0
    hi = min(r_hi, L * (1.0 - 1e-9))
    h_all = L / n_bins
    z = sum(_wlc_density((i + 0.5) * h_all, L, lp) for i in range(n_bins)) * h_all
    if z <= 0.0:
        return 0.0
    h = (hi - r_lo) / n_bins
    num = sum(_wlc_density(r_lo + (i + 0.5) * h, L, lp) for i in range(n_bins)) * h
    return max(0.0, min(1.0, num / z))


def wlc_strain_kt(r: float, n_atoms: int, lp: float = 4.0, rise: float = RISE_PER_ATOM_A,
                  n_bins: int = 800) -> float:
    """Conformational cost, in kT, of holding a WLC of `n_atoms` atoms at end-to-end distance `r`, relative to
    its own most probable end-to-end distance: -ln[P(r)/P(r_mode)].

    HONEST SCOPE, because this is the only energy-like number this rung emits: it is a POLYMER-STATISTICS
    estimate for an ideal semi-flexible chain with no excluded volume, no solvent, no specific torsional
    preferences and no protein. It is NOT a force-field strain energy and NOT a free energy of binding, and no
    ranking in this rung turns on a small difference in it. It is here to answer one coarse question — is this
    basin's span in the comfortable part of this linker's distribution, or in its tail? — and it is reported
    with the raw span and contour length alongside so a reader can re-derive it.
    """
    L = n_atoms * rise
    if r >= L:
        return float("inf")
    pmax = _wlc_density(wlc_mode(n_atoms, lp, rise, n_bins), L, lp)
    pr = _wlc_density(r, L, lp)
    if pr <= 0.0 or pmax <= 0.0:
        return float("inf")
    return -math.log(min(1.0, pr / pmax))


def wlc_mode(n_atoms: int, lp: float = 4.0, rise: float = RISE_PER_ATOM_A, n_bins: int = 800) -> float:
    """Most probable end-to-end distance of a WLC of `n_atoms` backbone atoms.

    Coarse grid to bracket, then golden-section on the (unimodal) density. Grid-INDEPENDENT to ~1e-9 A, which
    matters because `wlc_strain_kt` is defined relative to this point: a grid-quantised mode would make the
    strain at the mode a small non-zero number that depends on the bin count rather than on the physics.
    """
    L = n_atoms * rise
    h = L / n_bins
    grid = [(i + 0.5) * h for i in range(n_bins)]
    i = max(range(n_bins), key=lambda j: _wlc_density(grid[j], L, lp))
    lo = grid[max(0, i - 1)]
    hi = grid[min(n_bins - 1, i + 1)]
    phi = (math.sqrt(5.0) - 1.0) / 2.0
    for _ in range(200):
        c, dpt = hi - phi * (hi - lo), lo + phi * (hi - lo)
        if _wlc_density(c, L, lp) > _wlc_density(dpt, L, lp):
            hi = dpt
        else:
            lo = c
    return 0.5 * (lo + hi)


def wlc_best_length(r_lo: float, r_hi: float, n_range, lp: float = 4.0, rise: float = RISE_PER_ATOM_A):
    """argmax over `n_range` of `wlc_window_probability`. Returns (best_n, best_p, profile).

    Guards against the censoring defect that motivated this module: if the argmax sits at either end of
    `n_range` the caller is told so via `at_boundary`, so a grid edge can never again be reported as an
    optimum.
    """
    ns = list(n_range)
    prof = {n: wlc_window_probability(r_lo, r_hi, n, lp, rise) for n in ns}
    best = max(ns, key=lambda n: prof[n])
    return best, prof[best], {"profile": prof, "at_boundary": best in (ns[0], ns[-1])}


# ---------------------------------------------------------------------------------------------------------
# Exit-vector geometry
# ---------------------------------------------------------------------------------------------------------


def _unit(v):
    n = math.sqrt(v[0] ** 2 + v[1] ** 2 + v[2] ** 2)
    if n == 0.0:
        raise ValueError("cannot normalise a zero vector")
    return (v[0] / n, v[1] / n, v[2] / n)


def _sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def _dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def _cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def dihedral_deg(p1, p2, p3, p4) -> float:
    """Standard IUPAC dihedral about the p2-p3 axis, in degrees, in (-180, 180]."""
    b1, b2, b3 = _sub(p2, p1), _sub(p3, p2), _sub(p4, p3)
    n1, n2 = _cross(b1, b2), _cross(b2, b3)
    m = _cross(n1, _unit(b2))
    x, y = _dot(n1, n2), _dot(m, n2)
    return math.degrees(math.atan2(y, x))


def exit_vector_geometry(anchor_a, exit_dir_a, anchor_b, exit_dir_b, rise: float = RISE_PER_ATOM_A):
    """Angles a linker must accommodate between the two exit bonds, and the atom cost of the turn.

    `alpha` — angle between the warhead's exit direction and the vector toward the E3 anchor. 0 deg means the
    warhead's substituent bond points straight at the E3 attachment point and the linker can run taut; 180 deg
    means it points directly away and the chain must reverse.
    `beta`  — the same on the E3 side.
    `dihedral` — the torsion between the two exit bonds about the anchor-anchor axis. It is reported because
    two designs with identical alpha/beta and identical span can still differ in whether the linker sweeps
    across the target surface or out into solvent, and that is the difference between a linker that
    reinforces the basin's interface and one that fights it.

    `turn_penalty_atoms` is the honest currency: the extra contour, over the straight span, that the chain
    spends leaving each end along its own bond before it can head for the other anchor. Derived from the exact
    geometric identity that a chain leaving `a` along `u` for one bond then running straight to `b` covers
    rise + |a + rise*u - b| instead of |a - b|; summed over both ends and expressed in backbone atoms. It is a
    LOWER bound on the real cost (a one-bond model of a directional constraint that persists over several
    bonds), and it is reported as such.
    """
    a, b = tuple(anchor_a), tuple(anchor_b)
    u, v = _unit(exit_dir_a), _unit(exit_dir_b)
    ab = _sub(b, a)
    span = math.sqrt(_dot(ab, ab))
    if span == 0.0:
        raise ValueError("anchors coincide")
    alpha = math.degrees(math.acos(max(-1.0, min(1.0, _dot(u, _unit(ab))))))
    beta = math.degrees(math.acos(max(-1.0, min(1.0, _dot(v, _unit(_sub(a, b)))))))
    a1 = (a[0] + rise * u[0], a[1] + rise * u[1], a[2] + rise * u[2])
    b1 = (b[0] + rise * v[0], b[1] + rise * v[1], b[2] + rise * v[2])
    detour_a = rise + _dist(a1, b) - span
    detour_b = rise + _dist(a, b1) - span
    try:
        dih = dihedral_deg(a1, a, b, b1)
    except ValueError:
        dih = None
    return {
        "span_A": round(span, 3),
        "alpha_deg": round(alpha, 1),
        "beta_deg": round(beta, 1),
        "dihedral_deg": round(dih, 1) if dih is not None else None,
        "turn_detour_A": round(detour_a + detour_b, 3),
        "turn_penalty_atoms": int(math.ceil((detour_a + detour_b) / rise)),
        "_bound": "turn_penalty_atoms is a LOWER bound: it models the exit-bond constraint for one bond at "
                  "each end, whereas a real substituent biases several bonds.",
    }


__all__ = [
    "RISE_PER_ATOM_A", "three_ball_min_margin", "balls_intersect", "branch_position_window",
    "min_linker_atoms_relaxed", "min_linker_atoms_for_reach", "min_linker_atoms_exact", "span_floor_atoms",
    "pendant_contactable", "wlc_window_probability", "wlc_strain_kt", "wlc_mode", "wlc_best_length",
    "dihedral_deg", "exit_vector_geometry",
]
