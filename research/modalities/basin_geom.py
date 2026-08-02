#!/usr/bin/env python3
"""
Pure geometry + polymer-statistics kernels for the RUNG-5a mechanism-first orientation-basin search.

WHY A SEPARATE MODULE (TESTING.md rule 3). Every load-bearing decision the basin search makes is a *geometric
set-membership* question — "does this basin place an electrophile within tethering distance of C397?", "does the
modelled E2~Ub transfer zone cover K572 and no paralogue lysine?" — and nr4a3-program-map.md's Tier-2 asymmetry says
exactly those are the questions cheap scoring answers RELIABLY, unlike a ~1 kcal/mol energy difference. So the
geometry must be right, and "right" here means unit-tested against closed-form answers, not eyeballed on a
picture. This module therefore holds the kernels with NO I/O, NO numpy, NO structure parsing: rotations,
superposition, an occupancy distance field, the linker-reach spheroid, the worm-like-chain end-to-end density,
and leader clustering. The driver (`nr4a3_basin_search.py`) imports these, so the tested code IS the run code.

Pure stdlib on purpose: the dev sandbox has no numpy/scipy/rdkit, and this whole rung is a $0 CPU step.

THE FOUR KERNELS THAT CARRY SCIENTIFIC WEIGHT, and why each is written the way it is:

1. `linker_visit_sum` / `linker_can_visit` — a linker of contour length L tethered at anchors a (target exit
   vector) and b (E3 ligand exit vector) can route its backbone through point p only if
   |p-a| + |p-b| <= L. That is an EXACT necessary condition (the chain's arclength through p is at least the
   straight-line distance to each anchor) and it is the defining inequality of the prolate spheroid with foci
   a, b. With a pendant electrophile arm of reach e mounted on the linker, the reachable condition becomes
   |q-a| + |q-b| <= L + 2e for the nucleophile at q (relaxing p to anywhere in the ball of radius e about q
   lowers the focal sum by at most 2e). We report the DETOUR = (|q-a| + |q-b|) - |a-b|: the extra contour length
   the linker must spend to visit the nucleophile, which is the quantity a chemist actually pays for.

2. `SquaredDistanceField` — a clamped nearest-atom distance grid. Used because the search evaluates ~10^5-10^6
   rigid-body placements and a per-placement neighbour search would be the whole run time. Built by stamping
   each source atom into the cells within `clamp` of it, keeping the running minimum; queried by trilinear-free
   nearest-cell lookup. The grid is CONSERVATIVE for clash detection by construction (see `min_dist`): the
   returned value is the true distance to the nearest source atom from the CELL CENTRE, so a query point may sit
   up to half a cell diagonal from that centre; the class exposes `cell_slack` and the caller must subtract it
   before declaring "no clash". Never assume the tool's convention — derive it (TESTING.md rule 1).

3. `wlc_end_to_end_density` — Thirumalai-Ha mean-field worm-like-chain radial density. This is the
   ACCESSIBILITY half of nr4a3-program-map.md load-bearing piece 4 (`P(B_k | d, s)` kept separate from the orientation's
   plausibility): a basin whose anchor-anchor span sits in the tail of a candidate linker's end-to-end
   distribution is one the linker rarely reaches, however good the interface looks. A Gaussian chain is wrong
   here — real degrader linkers are 3-16 backbone atoms, far from the Gaussian limit, and the Gaussian assigns
   non-zero weight beyond the contour length, which is unphysical exactly where the answer matters.

4. `horn_superpose` — Horn's unit-quaternion superposition, via Jacobi diagonalisation of the 4x4 key matrix.
   Chosen over Kabsch because it needs no SVD, so it is ~80 lines of stdlib and exactly testable. Used to put
   NR4A1/NR4A2 into the NR4A3 frame so ONE sampled transform set is evaluated against all three paralogues —
   which is what makes the comparison MATCHED (the atlas's requirement) rather than three separate searches.
"""
from __future__ import annotations

import math
import random
from array import array

# ---------------------------------------------------------------------------------------------------------
# Vector primitives (tuples of 3 floats)
# ---------------------------------------------------------------------------------------------------------


def sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def add(a, b):
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def scale(a, s):
    return (a[0] * s, a[1] * s, a[2] * s)


def dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def norm(a):
    return math.sqrt(a[0] * a[0] + a[1] * a[1] + a[2] * a[2])


def unit(a):
    n = norm(a)
    if n == 0.0:
        raise ValueError("cannot normalise a zero vector")
    return (a[0] / n, a[1] / n, a[2] / n)


def dist(a, b):
    return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 + (a[2] - b[2]) ** 2)


def dist2(a, b):
    return (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 + (a[2] - b[2]) ** 2


def centroid(points):
    n = len(points)
    if n == 0:
        raise ValueError("centroid of an empty point set")
    sx = sy = sz = 0.0
    for p in points:
        sx += p[0]; sy += p[1]; sz += p[2]
    return (sx / n, sy / n, sz / n)


# ---------------------------------------------------------------------------------------------------------
# Rotations
# ---------------------------------------------------------------------------------------------------------


def quat_to_matrix(q):
    """Unit quaternion (w, x, y, z) -> 3x3 rotation matrix as a tuple of 3 row-tuples."""
    w, x, y, z = q
    n = math.sqrt(w * w + x * x + y * y + z * z)
    if n == 0.0:
        raise ValueError("zero quaternion")
    w, x, y, z = w / n, x / n, y / n, z / n
    return (
        (1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)),
        (2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)),
        (2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)),
    )


def matvec(R, v):
    return (
        R[0][0] * v[0] + R[0][1] * v[1] + R[0][2] * v[2],
        R[1][0] * v[0] + R[1][1] * v[1] + R[1][2] * v[2],
        R[2][0] * v[0] + R[2][1] * v[1] + R[2][2] * v[2],
    )


def random_quaternion(rng: random.Random):
    """Uniform on SO(3) — four independent standard normals, normalised (Marsaglia / Shoemake equivalent).

    A uniform quaternion on S^3 maps to Haar-uniform rotations; sampling Euler angles uniformly does NOT, and
    the bias would concentrate sampled E3 orientations near the poles, which is exactly the kind of silent
    sampling artefact that would make a 'basin' an artefact of the sampler.
    """
    while True:
        q = (rng.gauss(0.0, 1.0), rng.gauss(0.0, 1.0), rng.gauss(0.0, 1.0), rng.gauss(0.0, 1.0))
        n = math.sqrt(sum(c * c for c in q))
        if n > 1e-9:
            return (q[0] / n, q[1] / n, q[2] / n, q[3] / n)


def random_unit_vector(rng: random.Random):
    """Uniform on the sphere (same reason as above: Gaussian trick, not uniform-in-angle)."""
    while True:
        v = (rng.gauss(0.0, 1.0), rng.gauss(0.0, 1.0), rng.gauss(0.0, 1.0))
        n = math.sqrt(v[0] ** 2 + v[1] ** 2 + v[2] ** 2)
        if n > 1e-9:
            return (v[0] / n, v[1] / n, v[2] / n)


def transform_points(points, R, pivot, target_pivot):
    """Rotate `points` about `pivot` by R, then translate so `pivot` lands on `target_pivot`.

    This is the parameterisation the search uses: the E3's ligand exit-vector atom is the pivot, it is placed
    at a sampled position inside the linker-reach shell, and the E3 body is then rotated about it. Six DOF,
    both of them constrained by the physical tether rather than sampled blind over all of SE(3).
    """
    out = []
    for p in points:
        v = (p[0] - pivot[0], p[1] - pivot[1], p[2] - pivot[2])
        rv = matvec(R, v)
        out.append((rv[0] + target_pivot[0], rv[1] + target_pivot[1], rv[2] + target_pivot[2]))
    return out


# ---------------------------------------------------------------------------------------------------------
# Horn quaternion superposition (no SVD)
# ---------------------------------------------------------------------------------------------------------


def _jacobi_eigen_sym4(A, iters: int = 100):
    """Jacobi eigen-decomposition of a symmetric 4x4. Returns (eigenvalues, eigenvectors-as-columns)."""
    n = 4
    a = [row[:] for row in A]
    v = [[1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]
    for _ in range(iters):
        off = 0.0
        for i in range(n):
            for j in range(i + 1, n):
                off += a[i][j] * a[i][j]
        if off < 1e-22:
            break
        for p in range(n):
            for q in range(p + 1, n):
                if abs(a[p][q]) < 1e-18:
                    continue
                theta = (a[q][q] - a[p][p]) / (2.0 * a[p][q])
                t = (1.0 if theta >= 0 else -1.0) / (abs(theta) + math.sqrt(theta * theta + 1.0))
                c = 1.0 / math.sqrt(t * t + 1.0)
                s = t * c
                for k in range(n):
                    akp, akq = a[k][p], a[k][q]
                    a[k][p] = c * akp - s * akq
                    a[k][q] = s * akp + c * akq
                for k in range(n):
                    apk, aqk = a[p][k], a[q][k]
                    a[p][k] = c * apk - s * aqk
                    a[q][k] = s * apk + c * aqk
                for k in range(n):
                    vkp, vkq = v[k][p], v[k][q]
                    v[k][p] = c * vkp - s * vkq
                    v[k][q] = s * vkp + c * vkq
    return [a[i][i] for i in range(n)], v


def horn_superpose(mobile, ref):
    """Optimal rigid superposition of `mobile` onto `ref` (paired, equal length). Returns (R, t, rmsd) with
    the convention  x' = R @ (x - centroid(mobile)) + centroid(ref)  — i.e. apply via `apply_superpose`."""
    if len(mobile) != len(ref):
        raise ValueError("horn_superpose needs paired point sets of equal length")
    if len(mobile) < 3:
        raise ValueError("horn_superpose needs >= 3 points")
    cm, cr = centroid(mobile), centroid(ref)
    Sxx = Sxy = Sxz = Syx = Syy = Syz = Szx = Szy = Szz = 0.0
    for m, r in zip(mobile, ref):
        mx, my, mz = m[0] - cm[0], m[1] - cm[1], m[2] - cm[2]
        rx, ry, rz = r[0] - cr[0], r[1] - cr[1], r[2] - cr[2]
        Sxx += mx * rx; Sxy += mx * ry; Sxz += mx * rz
        Syx += my * rx; Syy += my * ry; Syz += my * rz
        Szx += mz * rx; Szy += mz * ry; Szz += mz * rz
    N = [
        [Sxx + Syy + Szz, Syz - Szy,        Szx - Sxz,        Sxy - Syx],
        [Syz - Szy,       Sxx - Syy - Szz,  Sxy + Syx,        Szx + Sxz],
        [Szx - Sxz,       Sxy + Syx,       -Sxx + Syy - Szz,  Syz + Szy],
        [Sxy - Syx,       Szx + Sxz,        Syz + Szy,       -Sxx - Syy + Szz],
    ]
    vals, vecs = _jacobi_eigen_sym4(N)
    k = max(range(4), key=lambda i: vals[i])
    q = (vecs[0][k], vecs[1][k], vecs[2][k], vecs[3][k])
    R = quat_to_matrix(q)
    ss = 0.0
    for m, r in zip(mobile, ref):
        v = matvec(R, (m[0] - cm[0], m[1] - cm[1], m[2] - cm[2]))
        ss += (v[0] + cr[0] - r[0]) ** 2 + (v[1] + cr[1] - r[1]) ** 2 + (v[2] + cr[2] - r[2]) ** 2
    return R, (cm, cr), math.sqrt(ss / len(mobile))


def apply_superpose(points, R, t):
    """Apply the (R, (cm, cr)) returned by horn_superpose."""
    cm, cr = t
    out = []
    for p in points:
        v = matvec(R, (p[0] - cm[0], p[1] - cm[1], p[2] - cm[2]))
        out.append((v[0] + cr[0], v[1] + cr[1], v[2] + cr[2]))
    return out


# ---------------------------------------------------------------------------------------------------------
# Clamped nearest-atom distance field
# ---------------------------------------------------------------------------------------------------------


class SquaredDistanceField:
    """Grid of distance-to-nearest-source-atom, clamped at `clamp` A.

    CONVENTION, derived not assumed (TESTING.md rule 1): `min_dist(p)` returns the exact distance from the
    CENTRE OF THE CELL CONTAINING p to the nearest source atom. A query point sits at most `cell_slack` =
    (sqrt(3)/2) * cell from that centre, so the true distance obeys
        min_dist(p) - cell_slack  <=  true  <=  min_dist(p) + cell_slack.
    Callers doing clash rejection must use the LOWER bound (`min_dist(p) - cell_slack`) so the field can never
    silently pass a real overlap; `is_clash` does this for you.
    """

    def __init__(self, points, cell: float = 1.0, clamp: float = 8.0, margin: float = 2.0):
        if not points:
            raise ValueError("SquaredDistanceField needs at least one source point")
        self.cell = float(cell)
        self.clamp = float(clamp)
        self.cell_slack = math.sqrt(3.0) / 2.0 * self.cell
        pad = clamp + margin
        xs = [p[0] for p in points]; ys = [p[1] for p in points]; zs = [p[2] for p in points]
        self.ox, self.oy, self.oz = min(xs) - pad, min(ys) - pad, min(zs) - pad
        self.nx = int((max(xs) + pad - self.ox) / self.cell) + 2
        self.ny = int((max(ys) + pad - self.oy) / self.cell) + 2
        self.nz = int((max(zs) + pad - self.oz) / self.cell) + 2
        big = self.clamp
        self.grid = array("f", [big]) * (self.nx * self.ny * self.nz)
        r_cells = int(math.ceil(self.clamp / self.cell))
        nyz = self.ny * self.nz
        for (px, py, pz) in points:
            ci = int((px - self.ox) / self.cell)
            cj = int((py - self.oy) / self.cell)
            ck = int((pz - self.oz) / self.cell)
            for i in range(max(0, ci - r_cells), min(self.nx, ci + r_cells + 1)):
                cx = self.ox + (i + 0.5) * self.cell
                dx2 = (cx - px) ** 2
                if dx2 > self.clamp * self.clamp:
                    continue
                base_i = i * nyz
                for j in range(max(0, cj - r_cells), min(self.ny, cj + r_cells + 1)):
                    cy = self.oy + (j + 0.5) * self.cell
                    dxy2 = dx2 + (cy - py) ** 2
                    if dxy2 > self.clamp * self.clamp:
                        continue
                    base_ij = base_i + j * self.nz
                    kmax_off = math.sqrt(self.clamp * self.clamp - dxy2)
                    k0 = max(0, int((pz - kmax_off - self.oz) / self.cell))
                    k1 = min(self.nz - 1, int((pz + kmax_off - self.oz) / self.cell) + 1)
                    for k in range(k0, k1 + 1):
                        cz = self.oz + (k + 0.5) * self.cell
                        d = math.sqrt(dxy2 + (cz - pz) ** 2)
                        if d < self.clamp:
                            idx = base_ij + k
                            if d < self.grid[idx]:
                                self.grid[idx] = d

    def min_dist(self, p):
        i = int((p[0] - self.ox) / self.cell)
        if i < 0 or i >= self.nx:
            return self.clamp
        j = int((p[1] - self.oy) / self.cell)
        if j < 0 or j >= self.ny:
            return self.clamp
        k = int((p[2] - self.oz) / self.cell)
        if k < 0 or k >= self.nz:
            return self.clamp
        return self.grid[(i * self.ny + j) * self.nz + k]

    def is_clash(self, p, cutoff: float) -> bool:
        """True if p is CERTAINLY closer than `cutoff` to a source atom (uses the conservative lower bound)."""
        return (self.min_dist(p) - self.cell_slack) < cutoff

    def is_contact(self, p, lo: float, hi: float) -> bool:
        d = self.min_dist(p)
        return lo <= d <= hi


# ---------------------------------------------------------------------------------------------------------
# Linker reach — the prolate-spheroid criterion
# ---------------------------------------------------------------------------------------------------------


def linker_visit_sum(anchor_a, anchor_b, target_point):
    """|q-a| + |q-b| — the minimum contour length a chain tethered at a and b must have to route through q."""
    return dist(target_point, anchor_a) + dist(target_point, anchor_b)


def linker_detour(anchor_a, anchor_b, target_point):
    """Extra contour length, over the straight anchor-anchor span, needed to visit `target_point`.
    Zero iff the point lies on the a-b segment. This is the chemically meaningful cost of the detour."""
    return linker_visit_sum(anchor_a, anchor_b, target_point) - dist(anchor_a, anchor_b)


def linker_can_visit(anchor_a, anchor_b, target_point, contour_length, arm_reach: float = 0.0) -> bool:
    """⚠ A RELAXATION — NECESSARY BUT NOT SUFFICIENT. Do NOT use it to decide reach; use
    `linker_design.min_linker_atoms_exact` / `pendant_contactable`.

    The criterion is: there is p with |p - q| <= arm_reach and |p-a| + |p-b| <= L. Minimising the focal sum
    over the ball of radius `arm_reach` about q lowers it by at most 2*arm_reach, which gives the inequality
    below — an outer bound on the feasible set, not the feasible set.

    ★ THE LOOPHOLE, AND WHY IT COST A PUBLISHED NUMBER (2026-07-25). Since |q-a| + |q-b| >= |a-b|, a
    nucleophile ON the anchor-anchor segment reduces this to `span <= L + 2*arm_reach` — i.e. the pendant is
    credited with shortening the SPAN. It cannot: the pendant hangs off the backbone and the backbone must
    still connect a to b, so L >= |a-b| whatever the arm. RUNG 5a's term-(a) numbers were computed with this
    rule and are therefore LOWER BOUNDS, understated by up to 2*arm_reach (~5 backbone atoms at the 3.0 A gate
    arm). Kept, tested and named as the relaxation it is, so the two rules can be compared rather than
    conflated — `nr4a3_basin_search.electrophile_reach` now reports both.
    """
    return linker_visit_sum(anchor_a, anchor_b, target_point) <= contour_length + 2.0 * arm_reach


def contour_length_from_atoms(n_backbone_atoms: int, per_atom: float = 1.25) -> float:
    """Contour length of a linker with `n_backbone_atoms` chain atoms.

    1.25 A/atom is the projected rise per backbone atom of an all-anti sp3 chain (1.53 A bond at the 109.5 deg
    tetrahedral angle projects to 1.53*sin(54.75 deg) = 1.25 A). It is a MODEL parameter, stated here rather
    than buried, and the driver reports results across a linker-length range rather than at one value.
    """
    if n_backbone_atoms < 0:
        raise ValueError("n_backbone_atoms must be >= 0")
    return n_backbone_atoms * per_atom


# ---------------------------------------------------------------------------------------------------------
# Worm-like-chain end-to-end density (the ACCESSIBILITY half of load-bearing piece 4)
# ---------------------------------------------------------------------------------------------------------


def wlc_end_to_end_density(r: float, contour_length: float, persistence_length: float = 4.0) -> float:
    """Thirumalai-Ha mean-field radial density for a worm-like chain, evaluated at end-to-end distance r.

    P(r) ∝ 4*pi*r^2 * (1 - x^2)^(-9/2) * exp( -3t / (4(1 - x^2)) ),   x = r/L,  t = 3L/(2*l_p)

    Returned UNNORMALISED (the driver normalises numerically over [0, L] with `wlc_normalisation`), because the
    normaliser depends on L and is shared across every basin evaluated for the same candidate linker.

    Chosen over a Gaussian chain deliberately: degrader linkers are 3-16 backbone atoms, nowhere near the
    Gaussian limit, and a Gaussian puts finite probability beyond the contour length — unphysical precisely
    where the accessibility question bites (a basin whose span exceeds the linker cannot be reached at all).
    """
    if contour_length <= 0.0:
        raise ValueError("contour_length must be > 0")
    if persistence_length <= 0.0:
        raise ValueError("persistence_length must be > 0")
    if r < 0.0 or r >= contour_length:
        return 0.0
    x = r / contour_length
    t = 3.0 * contour_length / (2.0 * persistence_length)
    one_minus = 1.0 - x * x
    expo = -3.0 * t / (4.0 * one_minus)
    if expo < -700.0:
        return 0.0
    return 4.0 * math.pi * r * r * one_minus ** (-4.5) * math.exp(expo)


def wlc_normalisation(contour_length: float, persistence_length: float = 4.0, n_bins: int = 400) -> float:
    """Numerical integral of `wlc_end_to_end_density` over [0, L] (midpoint rule)."""
    h = contour_length / n_bins
    s = 0.0
    for i in range(n_bins):
        s += wlc_end_to_end_density((i + 0.5) * h, contour_length, persistence_length)
    return s * h


def wlc_pdf(r: float, contour_length: float, persistence_length: float = 4.0, norm_const=None) -> float:
    z = wlc_normalisation(contour_length, persistence_length) if norm_const is None else norm_const
    if z <= 0.0:
        return 0.0
    return wlc_end_to_end_density(r, contour_length, persistence_length) / z


# ---------------------------------------------------------------------------------------------------------
# Leader clustering on landmark RMSD
# ---------------------------------------------------------------------------------------------------------


def landmark_rmsd(a_points, b_points) -> float:
    """Positional RMSD between two landmark sets ALREADY in a common frame (no re-superposition).

    Re-superposing would be wrong here: two E3 placements related by a large rotation about the target are
    physically different basins even though the E3's internal structure is identical, and superposition would
    call them the same. The whole point is to cluster PLACEMENTS, not conformations.
    """
    if len(a_points) != len(b_points):
        raise ValueError("landmark sets must be the same length")
    s = 0.0
    for a, b in zip(a_points, b_points):
        s += dist2(a, b)
    return math.sqrt(s / len(a_points))


def farthest_point_sample(points, k: int, seed_index: int = 0):
    """Indices of k maximally-spread points (greedy farthest-point). Used to pick E3 landmark atoms and the
    cheap clash pre-screen set, so both cover the body instead of clumping in one domain."""
    if k <= 0:
        return []
    n = len(points)
    if k >= n:
        return list(range(n))
    chosen = [seed_index % n]
    d = [dist2(p, points[chosen[0]]) for p in points]
    while len(chosen) < k:
        nxt = max(range(n), key=lambda i: d[i])
        chosen.append(nxt)
        for i in range(n):
            dd = dist2(points[i], points[nxt])
            if dd < d[i]:
                d[i] = dd
    return chosen


def jaccard_distance(a: set, b: set) -> float:
    """1 - |a n b| / |a u b|. Two empty sets are identical (distance 0)."""
    if not a and not b:
        return 0.0
    u = len(a | b)
    return 1.0 - (len(a & b) / u if u else 0.0)


def leader_cluster_by(items, descriptor_of, distance, threshold: float, key=None):
    """Leader clustering under an ARBITRARY descriptor distance.

    Exists because clustering rigid-body placements on landmark RMSD was measured to be the wrong resolution
    for this problem: with an E3 of ~18 A radius, an 8 A landmark RMSD corresponds to a ~25 deg rotation, and
    only 0.09 % of accepted placement PAIRS fall inside that — so every 'basin' came out a singleton. It was
    not a bug; the accepted set is genuinely spread over orientation space at that resolution, and closing the
    gap by sampling would need ~10^7-10^8 placements per arm.

    The fix is to cluster on the descriptor the SCORED TERMS actually depend on — which target-surface patch
    the E3 occupies, i.e. the interface fingerprint — under `jaccard_distance`. Rotation of the E3 about the
    tether that leaves the interface unchanged should not split a basin; it is a real degree of freedom the
    complex explores, and the right way to report it is as a FREQUENCY within the basin (in what fraction of
    the basin's placements does the transfer zone cover a unique lysine?), not as a forest of singletons.
    """
    ordered = sorted(items, key=key, reverse=True) if key is not None else list(items)
    clusters, leaders = [], []
    for it in ordered:
        d = descriptor_of(it)
        for ci, ld in enumerate(leaders):
            if distance(d, ld) <= threshold:
                clusters[ci].append(it)
                break
        else:
            clusters.append([it])
            leaders.append(d)
    return clusters


def leader_cluster(items, landmarks_of, cutoff: float, key=None):
    """Greedy leader clustering: process items best-first, assign each to the first cluster whose LEADER is
    within `cutoff` landmark-RMSD, else open a new cluster.

    Deterministic given the sort order, O(n * n_clusters), and — unlike k-means — it never invents a cluster
    centre that no sampled placement actually occupies. Returns a list of clusters, each a list of items.
    """
    ordered = sorted(items, key=key, reverse=True) if key is not None else list(items)
    clusters = []
    leaders = []
    for it in ordered:
        lm = landmarks_of(it)
        placed = False
        for ci, leader_lm in enumerate(leaders):
            if landmark_rmsd(lm, leader_lm) <= cutoff:
                clusters[ci].append(it)
                placed = True
                break
        if not placed:
            clusters.append([it])
            leaders.append(lm)
    return clusters


# ---------------------------------------------------------------------------------------------------------
# Spherical-cap sampling (the E2~Ub swing about the RING)
# ---------------------------------------------------------------------------------------------------------


def sample_spherical_cap(rng: random.Random, axis, half_angle_deg: float):
    """Uniform unit vector inside the cap of half-angle `half_angle_deg` about `axis`.

    Uniform in AREA (cos(theta) uniform on [cos(alpha), 1]), not uniform in theta — sampling theta uniformly
    would over-weight the cap's pole, which for the E2~Ub swing would silently bias every transfer zone toward
    one point instead of covering the arc the RING-E2 module actually sweeps.
    """
    a = unit(axis)
    alpha = math.radians(half_angle_deg)
    cos_t = 1.0 - rng.random() * (1.0 - math.cos(alpha))
    sin_t = math.sqrt(max(0.0, 1.0 - cos_t * cos_t))
    phi = rng.random() * 2.0 * math.pi
    # orthonormal frame around a
    tmp = (1.0, 0.0, 0.0) if abs(a[0]) < 0.9 else (0.0, 1.0, 0.0)
    u = unit(cross(a, tmp))
    v = cross(a, u)
    return (
        a[0] * cos_t + (u[0] * math.cos(phi) + v[0] * math.sin(phi)) * sin_t,
        a[1] * cos_t + (u[1] * math.cos(phi) + v[1] * math.sin(phi)) * sin_t,
        a[2] * cos_t + (u[2] * math.cos(phi) + v[2] * math.sin(phi)) * sin_t,
    )
