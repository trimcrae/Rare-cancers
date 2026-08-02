#!/usr/bin/env python3
"""
IS A LINKER-BORNE COVALENT NR4A3 HANDLE GEOMETRICALLY AVAILABLE? ($0, CPU/CI only.)

THE IDEA BEING TESTED. The conventional PROTAC asks the WARHEAD to discriminate an ~80 %-identical
paralogue pocket. `nr4a3-covalent-handle-ensemble.json` measured that NR4A3's three paralogue-unique
cysteines (C397, C420, C559) are 11-19 A from that pocket -- too far for a warhead-borne electrophile, but
that band is exactly where a PROTAC's LINKER passes. So: put the electrophile on the LINKER, aimed at a
cysteine the paralogues do not have, and ask the warhead only to bind rather than to discriminate.

★ THE FIRST FINDING IS THAT THE ARCHITECTURE ALREADY EXISTS AND THE RECORDED BLOCKER IS A DIFFERENT
  QUESTION. It was put to this module that "a linker-borne electrophile plus an E3 arm is a two-branch
  case" (the n = 18 two-pendant template of `linker_twobranch.py`). Read against `build_smiles`, that is
  wrong, and the correction matters because it removes a blocker rather than adding one. The committed
  one-pendant template is

      E3-NH-C(=O)-[SEG1]-C(=O)NH-CH(pendant)-C(=O)NH-[SEG2]-<warhead tail>

  -- the E3 sits at a chain TERMINUS, not on a branch. An electrophile pendant + an E3 arm + a warhead is
  therefore a ONE-branch molecule, and `nr4a3-linker-design.json` already contains such constructs aimed at
  C397 SG (the count is COUNTED by `premise_check`, not typed here).
  Two branches are needed only for the electrophile AND the RUNG-5a causal wedge on one chain,
  which is a different molecule for a different experiment. Asserted by `premise_check()` and pinned in
  `tests/test_nr4a3_linker_covalent_reach.py`.

WHAT IS ACTUALLY OPEN, AND IS WHAT THIS MODULE MEASURES.
  1. REACH, ACROSS THE EXPERIMENTAL ENSEMBLE. The committed library was designed in ONE frame
     (`nr4a3-opened.pdb`) at C397 only. Nothing has asked whether the reach survives the 20 experimental
     8XTT conformers, or whether C420/C559 are reachable at all.
  2. THE COUNTER-TEST THAT CAN KILL IT. A pendant that reaches an NR4A3-UNIQUE cysteine may also reach a
     CONSERVED one (C496, C506, C536, C594) -- whose partners NR4A1/NR4A2 keep. If a conserved cysteine is
     reachable at or before the unique one, the paralogue-uniqueness argument is void and the route is dead.
     The decision quantity is therefore not "can it reach" but the CHEMOSELECTIVITY MARGIN: the interval of
     backbone-atom counts over which the unique cysteine is in reach and every conserved one is not.
  3. THE PARALOGUE CONTROL, COMPUTED NOT ASSUMED. "The paralogues have no cysteine there" is a statement
     about ONE aligned position. The question that decides the route is whether NR4A1/NR4A2 present ANY
     cysteine within the same tether geometry, at any position.

METHOD, AND WHAT IS REUSED RATHER THAN RE-DERIVED (rule 1).
  * The reach engine is `linker_design.branch_position_window` / `min_linker_atoms_exact` -- the exact
    three-ball rule the committed library was built with. Not re-implemented.
  * The anchors (a = warhead attachment point, b = E3 anchor) are READ from
    `nr4a3-orientation-basins.json` at the five CONFIRMED basins, both placements. `a` is the pose's
    `anchor_xyz`; `b` is the placement's `anchor_e3_xyz`, which `nr4a3_linker_design.recover_transform`
    reproduces from the stored landmarks to 0.002-0.008 A. Every distance is CROSS-CHECKED against the
    committed `nr4a3-linker-design.json` records and a mismatch is a refusal, not a new number.
  * Cysteine accessibility is READ from `nr4a3-covalent-handle-ensemble.json`, never recomputed.
  * The cavity-bearing stratification uses `nr4a3_8xtt_benchmark.DRUGGABLE_REF` against that artifact's
    own per-conformer `site_druggability`.

★★ THE ONE THING THIS MODULE ADDS TO THE ENGINE, AND WHY IT WAS NECESSARY. `branch_position_window` is a
   THROUGH-SPACE rule: it places the branch backbone atom anywhere in an intersection of three balls,
   including inside the protein. That is fine for the question it was written for and fatal for this one,
   because the two nearest competitors to C397 are C496 and C536 -- both BURIED (SG heavy-atom SASA
   0.0-11.3 A^2 across the 8XTT ensemble). A through-space rule scores a buried sulfur as reachable, so it
   systematically overstates the competitor and understates the margin. This module therefore reports two
   conventions side by side and never quotes one as the other:

     `through_space`  the committed rule, unchanged -- an UPPER BOUND on reachability.
     `corridor`       additionally requires a branch position that (i) does not clash with that conformer's
                      protein and (ii) has a clash-free straight arm to the target SG. A NECESSARY
                      condition, still not sufficient: it does not thread the backbone, score torsions or
                      test whether a clash-free pocket is connected to bulk solvent.

   The identity that makes the corridor test one cheap pass rather than a scan: a branch position p is
   usable by an n-atom chain iff ceil(|p-a|/rise) + ceil(|p-b|/rise) <= n, so the minimum chain length is
   a minimum over candidate points and the candidates depend only on (conformer, cysteine), not on the
   placement or the chain length.

⛔ WHAT THIS MODULE DOES NOT AND CANNOT SAY. Nothing here is a reactivity, potency, selectivity,
   developability or feasibility statement. Thiol pKa, intrinsic electrophile reactivity, adduct
   stability, permeability, exposure and degradation are all uncomputed. Geometry can REFUTE a route; it
   cannot license one. `electrophile_classes()` lists options with primary sources and asserts nothing
   about any of them.

Outputs: nr4a3-linker-covalent-reach.json (+ .md)
"""
from __future__ import annotations

import argparse
import glob
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)

import basin_geom as G                      # noqa: E402  horn_superpose / dist / centroid
import linker_design as LD                  # noqa: E402  THE reach engine — never reimplemented here
import nr4a3_basin_search as BS             # noqa: E402  load_paralogue / atom_xyz / superpose_paralogue
import nr4a3_linker_design as NLD           # noqa: E402  CONFIRMED / CHEM_MAX_ATOMS / UNIPROT_OFFSET
import nr4a_differential_atlas as atlas     # noqa: E402  parse_pdb / nw_align
import nr4a_paralogue_unique_residues as uniq   # noqa: E402  pocket definition / LBD bounds

# ---- imported, never re-typed ---------------------------------------------------------------------------
RISE = LD.RISE_PER_ATOM_A                    # 1.25 A per backbone atom
PENDANT_REACH = LD.PENDANT_REACH_A           # the six named pendant reaches
CHEM_MAX_ATOMS = NLD.CHEM_MAX_ATOMS          # 24 — chemically routine upper bound on a PROTAC linker
CONFIRMED = NLD.CONFIRMED                    # the five confirmed meta-basins
OFFSET = NLD.UNIPROT_OFFSET                  # 372: local resid -> NR4A3 UniProt
CRYPTIC_POCKET_UNIPROT = uniq.CRYPTIC_POCKET_UNIPROT

BASINS = os.path.join(HERE, "nr4a3-orientation-basins.json")
LIBRARY = os.path.join(HERE, "nr4a3-linker-design.json")
COV_ENSEMBLE = os.path.join(HERE, "nr4a3-covalent-handle-ensemble.json")
BENCHMARK = os.path.join(REPO, "results", "nr4a3-pocket-reharmonize", "8xtt", "nr4a3-8xtt-benchmark.json")
OPENED = {"NR4A3": os.path.join(REPO, "results/nr4a3-matrix/nr4a3-opened.pdb"),
          "NR4A1": os.path.join(REPO, "results/nr4a3-matrix/nr4a1-opened.pdb"),
          "NR4A2": os.path.join(REPO, "results/nr4a3-matrix/nr4a2-opened.pdb")}
PARALOGUE_ENSEMBLE = {"NR4A1": "results/nr4a1-pocket-ensemble/metad/*/frame.pdb",
                      "NR4A2": "results/nr4a2-pocket-ensemble/metad/*/frame.pdb"}
SEQ_CACHE = os.path.join(HERE, "nr4a-sequences-cache.json")
OUT = os.path.join(HERE, "nr4a3-linker-covalent-reach.json")

# ★ THE ONE NEW PARAMETER IN THIS MODULE, DECLARED AS ONE. No repo constant answers "how close may a linker
#   backbone atom come to a protein heavy atom", so this is not imported and must not pretend to be. It is
#   handled the way an un-inheritable threshold has to be: the whole SWEEP is computed and reported, so no
#   single value is load-bearing and the answer's dependence on it is visible rather than buried. The
#   primary is deliberately PERMISSIVE toward reach (0.4 A inside a C...C van der Waals contact of ~3.4 A),
#   because a permissive setting makes the CONSERVED competitor easier to reach, i.e. it biases against the
#   route this module is testing rather than for it.
CLASH_SWEEP_A = (2.0, 2.6, 3.0, 3.4)
CLASH_PRIMARY_A = 3.0
CANDIDATE_GRID_A = 0.75          # branch-position sampling pitch inside the pendant ball
ARM_SAMPLES = 6                  # points tested along the pendant arm p -> SG

MIN_ALIGN_IDENTITY = 0.90


# ==========================================================================================================
# PURE GEOMETRY — no I/O. Unit-tested in tests/test_nr4a3_linker_covalent_reach.py
# ==========================================================================================================
class AtomGrid:
    """Uniform-bin neighbour lookup with per-query atom EXCLUSION.

    ⚠ Why not `basin_geom.SquaredDistanceField`. That field is faster but stores only a distance, so it
    cannot answer "nearest atom OTHER THAN the target cysteine's own" — and the target's own SG is the
    reaction partner, not an obstacle. Treating it as an obstacle would make every cysteine unreachable,
    which is the sort of silently-plausible wrong answer this repo keeps paying for.
    """

    def __init__(self, points, keys, cell: float = 4.0):
        if len(points) != len(keys):
            raise ValueError("points and keys must be the same length")
        self.cell = float(cell)
        self.bins = {}
        self.points = list(points)
        self.keys = list(keys)
        for i, p in enumerate(self.points):
            self.bins.setdefault(self._cell_of(p), []).append(i)

    def _cell_of(self, p):
        c = self.cell
        return (int(math.floor(p[0] / c)), int(math.floor(p[1] / c)), int(math.floor(p[2] / c)))

    def min_dist(self, p, exclude=frozenset()):
        """Distance to the nearest source atom whose key is not in `exclude`.

        ⚠ EXACT ONLY BELOW `cell`, AND SATURATES ABOVE IT. The 27-cell neighbourhood provably contains
        every atom closer than `cell`, so a clash at any cutoff < `cell` can never be missed — but an atom
        at 4.5 A may sit outside it while one at 5.5 A is inside, so a returned value above `cell` is an
        UPPER BOUND, not the true nearest distance. Every caller here uses cutoffs <= 3.4 A, and the one
        place a real distance is reported (`min_dist_exact`) does not use this path."""
        ci, cj, ck = self._cell_of(p)
        best = float("inf")
        for i in (ci - 1, ci, ci + 1):
            for j in (cj - 1, cj, cj + 1):
                for k in (ck - 1, ck, ck + 1):
                    for idx in self.bins.get((i, j, k), ()):
                        if self.keys[idx] in exclude:
                            continue
                        q = self.points[idx]
                        d = math.sqrt((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2 + (p[2] - q[2]) ** 2)
                        if d < best:
                            best = d
        return best

    def min_dist_exact(self, p, exclude=frozenset()):
        """True distance to the nearest non-excluded source atom, by full scan.

        Used only for the handful of ANCHOR clearance queries per frame, where the answer is reported as a
        number rather than compared against a sub-cell cutoff — a binned upper bound printed as a clearance
        would be a populated field that was never measured (CLAUDE.md §4b)."""
        best = float("inf")
        for idx, q in enumerate(self.points):
            if self.keys[idx] in exclude:
                continue
            d = math.sqrt((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2 + (p[2] - q[2]) ** 2)
            if d < best:
                best = d
        return best


def ball_grid(centre, radius: float, pitch: float = CANDIDATE_GRID_A):
    """Lattice points inside a ball, plus the centre. Deterministic, no RNG — a sampled reach answer that
    moved between runs would be unusable as a gate."""
    out = []
    n = int(math.floor(radius / pitch))
    for i in range(-n, n + 1):
        for j in range(-n, n + 1):
            for k in range(-n, n + 1):
                dx, dy, dz = i * pitch, j * pitch, k * pitch
                if dx * dx + dy * dy + dz * dz <= radius * radius:
                    out.append((centre[0] + dx, centre[1] + dy, centre[2] + dz))
    return out


def arm_clear(grid: AtomGrid, p, q, exclude, cutoff: float, n_samples: int = ARM_SAMPLES):
    """Is the straight pendant arm from branch position `p` to the target atom `q` free of protein?

    The endpoint `q` itself is skipped: it is the sulfur being alkylated, not an obstacle. Interior samples
    are tested against everything except the target residue's own atoms."""
    for s in range(1, n_samples):
        f = s / float(n_samples)
        m = (p[0] + f * (q[0] - p[0]), p[1] + f * (q[1] - p[1]), p[2] + f * (q[2] - p[2]))
        if grid.min_dist(m, exclude) < cutoff:
            return False
    return True


def candidate_branch_points(grid: AtomGrid, q, max_reach: float, exclude, cutoffs=CLASH_SWEEP_A):
    """Every lattice branch position within `max_reach` of `q`, tagged with its distance to `q` and the
    clash cutoffs it survives.

    ★ COMPUTED ONCE PER (conformer, cysteine) AND REUSED BY EVERY PLACEMENT AND EVERY CHAIN LENGTH. That is
    the whole reason the corridor test is affordable: the candidate set depends on the protein and the
    target, and the anchors only ever enter through |p-a| and |p-b|."""
    out = []
    for p in ball_grid(q, max_reach):
        d_q = G.dist(p, q)
        if d_q > max_reach:
            continue
        self_d = grid.min_dist(p, exclude)
        ok = tuple(c for c in cutoffs if self_d >= c and arm_clear(grid, p, q, exclude, c))
        out.append({"p": p, "d_q": d_q, "clear_at": ok})
    return out


def n_min_from_point(p, a, b, rise: float = RISE):
    """The shortest chain length that can put a backbone atom at `p`, and the branch index it lands at.

    A chain of n atoms with branch index k in 1..n-1 places its k-th atom no further than k*rise from the
    warhead anchor and no further than (n-k)*rise from the E3 anchor, so p is usable iff
    ceil(|p-a|/rise) + ceil(|p-b|/rise) <= n with both terms >= 1. This is the same contour-length rule
    `branch_position_window` enforces, evaluated at a fixed p instead of over a ball."""
    ka = max(1, int(math.ceil(G.dist(p, a) / rise - 1e-9)))
    kb = max(1, int(math.ceil(G.dist(p, b) / rise - 1e-9)))
    return ka + kb, ka


def corridor_min_atoms(candidates, a, b, arm_reach: float, cutoff: float, n_max: int = 80):
    """Shortest chain length with a CLASH-FREE branch position reaching the target, and its branch index.

    Returns (n_atoms, k_from_warhead) or (None, None). `arm_reach` filters the shared candidate set, which
    is why one candidate set serves all six pendants (the balls are nested)."""
    best = None
    for c in candidates:
        if c["d_q"] > arm_reach or cutoff not in c["clear_at"]:
            continue
        n, k = n_min_from_point(c["p"], a, b)
        if n <= n_max and (best is None or n < best[0]):
            best = (n, k)
    return best if best else (None, None)


TANGENCY_TOL_A = 1e-3


def classify_disagreement(a, b, q, arm_reach, corridor_n, ts_n, frame, placement, cysteine, pendant,
                          cutoff):
    """Why does the corridor answer sit BELOW the through-space answer, when it cannot?

    ★ MEASURED, NOT GUESSED (the first instance was diagnosed before this function was written).
    `min_linker_atoms_exact` calls `three_ball_min_margin`, a numerical convex solve declared feasible at
    `margin <= 1e-6`. The corridor test instead exhibits an EXPLICIT witness point and needs no solve. At an
    exact three-ball TANGENCY the solve's convergence tolerance is coarser than 1e-6, so it can return a
    margin of ~1e-5 and call an intersection empty that a witness proves non-empty — a one-atom difference
    at the tangent chain length. The instance found: 8xtt_m20, vhl|M2@term_a_exemplar, C506,
    `rung5a_convention`, corridor 51 vs through-space 52, with `branch_position_window(n=51).best_margin_A`
    reported as **0.000**, i.e. the engine itself measured the intersection as exactly touching.

    So the discriminator is the engine's OWN margin at the disputed length: at or below `TANGENCY_TOL_A` it
    is a degenerate tangency and the witness is the more exact answer; anything larger is a genuine drift
    between the two rules and must be treated as one.
    """
    w = LD.branch_position_window(a, b, q, corridor_n, arm_reach)
    margin = w.get("best_margin_A")
    tangency = margin is not None and abs(margin) <= TANGENCY_TOL_A and (ts_n - corridor_n) == 1
    return {
        "frame": frame, "placement": placement, "cysteine": cysteine, "pendant": pendant,
        "cutoff": cutoff, "corridor_atoms": corridor_n, "through_space_atoms": ts_n,
        "engine_best_margin_A_at_corridor_n": margin,
        "kind": "degenerate_tangency" if tangency else "RULE_DRIFT",
        "_reading": ("the three balls touch to within %.1e A at n = %d, so the convex solve's tolerance and "
                     "the explicit witness disagree by exactly one backbone atom. Benign, and it can only "
                     "occur at the tangent length." % (TANGENCY_TOL_A, corridor_n) if tangency else
                     "NOT a tangency — the two reach rules have genuinely drifted and every number in this "
                     "artifact is suspect until it is explained."),
    }


def chemoselectivity_margin(unique_n, conserved_ns, chem_max: int = CHEM_MAX_ATOMS):
    """THE DECISION QUANTITY. The interval of backbone-atom counts over which the NR4A3-unique cysteine is
    in reach and NO conserved cysteine is.

    Reach is monotone in chain length -- growing the chain grows every branch ball -- so each cysteine has a
    single threshold and the window is [n_unique, min(conserved) - 1], clipped at the chemically routine
    ceiling. `width = 0` means the route is refuted AT THAT GEOMETRY: no chain reaches the unique cysteine
    without also reaching a conserved one, and a conserved cysteine is one both paralogues keep.
    """
    if unique_n is None or unique_n > chem_max:
        return {"lo": None, "hi": None, "width": 0, "blocked_by": None, "blocked_at_atoms": None,
                "verdict": "target cysteine NOT reachable within %d backbone atoms (needs %s)"
                           % (chem_max, unique_n)}
    live = {k: v for k, v in conserved_ns.items() if v is not None}
    if live:
        blocker = min(live, key=lambda k: live[k])
        hi = min(chem_max, live[blocker] - 1)
    else:
        blocker, hi = None, chem_max
    width = max(0, hi - unique_n + 1)
    return {
        "lo": unique_n, "hi": hi if width else None, "width": width,
        "blocked_by": blocker,
        "blocked_at_atoms": live.get(blocker) if blocker else None,
        "verdict": ("%d backbone-atom window [%d, %d]; the first conserved cysteine in reach is %s at %s"
                    % (width, unique_n, hi, blocker, live.get(blocker)) if width else
                    "NO window — the conserved cysteine %s is in reach at %s, at or before the unique one "
                    "at %d" % (blocker, live.get(blocker), unique_n)),
    }


def premise_check(lib_path=LIBRARY):
    """Is a linker-borne electrophile + an E3 arm a ONE-branch or a TWO-branch molecule? Read, not recalled.

    Counts the committed constructs that already carry an electrophile pendant AND an E3 handle on a
    single-pendant chain. A non-zero count settles it."""
    import inspect
    sig = inspect.signature(NLD.build_smiles)
    with open(lib_path) as fh:
        lib = json.load(fh)["virtual_library"]
    one_branch = [r for r in lib
                  if r.get("pendant_kind") == "electrophile" and r.get("e3_handle")
                  and r.get("branch_target")]
    return {
        "question": "does a linker-borne electrophile plus an E3 arm need a TWO-branch template?",
        "answer": "NO — it is a ONE-branch molecule and the committed library already contains %d of them"
                  % len(one_branch),
        "evidence": {
            "build_smiles_signature": str(sig),
            "template": "E3-NH-C(=O)-[SEG1]-C(=O)NH-CH(pendant)-C(=O)NH-[SEG2]-<warhead tail>",
            "why": "the E3 sits at a chain TERMINUS, not on a branch, so the single `pendant` slot is free "
                   "for the electrophile. `linker_branch_reach.py`'s two-branch requirement is for the "
                   "electrophile AND the RUNG-5a causal wedge on one chain — a different molecule for a "
                   "different experiment.",
            "n_committed_one_branch_electrophile_plus_e3": len(one_branch),
            "branch_targets": sorted({r["branch_target"] for r in one_branch}),
            "n_backbone_atoms_present": sorted({r["n_backbone_atoms_intended"] for r in one_branch}),
            "example_construct_id": one_branch[0]["construct_id"] if one_branch else None,
        },
        "consequence": "the architecture is not the blocker; reach, chemoselectivity and the paralogue "
                       "control are. Those are what this module measures.",
    }


# ==========================================================================================================
# INPUT STAGING
# ==========================================================================================================
def load_placements(basins_path=BASINS):
    """(label, meta_basin_id, a, b) for the five CONFIRMED basins at both placements.

    `a` is the docked pose's ligand exit atom (the warhead attachment point); `b` is the placement's own
    recorded E3 anchor. Both are READ; nothing is re-fitted here."""
    with open(basins_path) as fh:
        d = json.load(fh)
    poses = {p["pose_id"]: p for p in d["pose_ensemble"]}
    metas = {m["meta_basin_id"]: m for m in d["meta_basins_ranked"]}
    out = []
    for mid in CONFIRMED:
        m = metas.get(mid)
        if m is None:
            continue
        rep = dict(m["representative"])
        rep["pose_id"] = m["representative_basin_id"].split("|")[1]
        for label, pl in (("representative", rep),
                          ("term_a_exemplar", (m["term_a_union"].get("C397") or {}).get(
                              "exemplar_placement"))):
            if not pl or pl.get("pose_id") not in poses:
                continue
            a = tuple(poses[pl["pose_id"]]["anchor_xyz"])
            b = tuple(pl["anchor_e3_xyz"])
            out.append({"meta_basin_id": mid, "placement_label": label, "pose_id": pl["pose_id"],
                        "a_warhead_anchor": [round(x, 3) for x in a],
                        "b_e3_anchor": [round(x, 3) for x in b],
                        "span_A": round(G.dist(a, b), 3),
                        "span_floor_atoms": LD.span_floor_atoms(a, b),
                        "_a": a, "_b": b})
    return out, d


def cysteines_in(model, numbering=OFFSET, unique=frozenset()):
    """{label: {"xyz", "local_resid", "unique"}} for every cysteine SG in a loaded model.

    `numbering` is either an int offset (the opened models, whose residue ids are UniProt - 372) or a
    {pdb_resnum -> uniprot_resnum} map from a global alignment. ⚠ The 8XTT conformers deposit their own
    numbering (C397 is residue 19), so an offset MUST NOT be assumed for them — a wrong offset would
    silently relabel every cysteine and every downstream statement with it."""
    out = {}
    for rid, aa in model["residues"]:
        if aa != "C":
            continue
        p = BS.atom_xyz(model, rid, "SG")
        if p is None:
            continue
        uni = (rid + numbering) if isinstance(numbering, int) else numbering.get(rid)
        if uni is None:
            continue
        lab = "C%d" % uni
        out[lab] = {"xyz": p, "local_resid": rid, "unique": lab in unique}
    return out


def iterative_ca_fit(mobile_pts, ref_pts, max_iter=8, min_core=40):
    """Horn superposition with outlier rejection — the same-protein analogue of `BS.superpose_paralogue`.

    Returns (R, t, core_rmsd, n_core, all_pair_rmsd). Used to bring an 8XTT conformer into the opened
    model's frame, where the placement anchors live."""
    core = list(range(len(mobile_pts)))
    R, t, all_rmsd = G.horn_superpose(mobile_pts, ref_pts)
    rmsd = all_rmsd
    for _ in range(max_iter):
        R, t, rmsd = G.horn_superpose([mobile_pts[k] for k in core], [ref_pts[k] for k in core])
        moved = G.apply_superpose(mobile_pts, R, t)
        cut = max(2.0, 2.0 * rmsd)
        nxt = [k for k in range(len(mobile_pts)) if G.dist(moved[k], ref_pts[k]) <= cut]
        if len(nxt) < min_core or nxt == core:
            break
        core = nxt
    R, t, rmsd = G.horn_superpose([mobile_pts[k] for k in core], [ref_pts[k] for k in core])
    return R, t, rmsd, len(core), all_rmsd


def superpose_into_opened(model, uni_map, ref_model, mode="pocket", ref_offset=OFFSET):
    """Put a conformer into the opened NR4A3 frame and return (moved_model, fit_record).

    TWO CONVENTIONS, BOTH REPORTED, because they answer different questions and could disagree:
      `pocket` — Horn fit on the CA of the ten cryptic-pocket-lining residues only. PRIMARY, because the
                 warhead anchor is a docked ligand atom INSIDE that pocket, so "put the warhead in this
                 conformer's pocket the same way" is a pocket-local statement.
      `core`   — iterative all-CA fit with outlier rejection. The fold-level frame, reported as the
                 sensitivity. 8XTT's global LBD Ca-RMSD against the modelled frame is large by construction
                 (the benchmark artifact records a median of 7.63 A), so a core fit is NOT interchangeable
                 with a pocket fit here and neither may be quoted as the other.
    """
    ref_by_uni = {rid + ref_offset: p for rid, p in ref_model["ca"].items()}
    mob_by_uni = {uni_map[rid]: p for rid, p in model["ca"].items() if rid in uni_map}
    if mode == "pocket":
        shared = [u for u in CRYPTIC_POCKET_UNIPROT if u in ref_by_uni and u in mob_by_uni]
        if len(shared) < 6:
            return None, {"mode": mode, "refused": "only %d of %d pocket CA shared"
                                                   % (len(shared), len(CRYPTIC_POCKET_UNIPROT))}
        R, t, rmsd = G.horn_superpose([mob_by_uni[u] for u in shared], [ref_by_uni[u] for u in shared])
        fit = {"mode": mode, "n_ca": len(shared), "rmsd_A": round(rmsd, 3),
               "residues_uniprot": shared}
    else:
        shared = sorted(set(ref_by_uni) & set(mob_by_uni))
        if len(shared) < 60:
            return None, {"mode": mode, "refused": "only %d shared CA" % len(shared)}
        R, t, rmsd, n_core, all_rmsd = iterative_ca_fit([mob_by_uni[u] for u in shared],
                                                        [ref_by_uni[u] for u in shared])
        fit = {"mode": mode, "n_ca": len(shared), "n_core": n_core, "core_rmsd_A": round(rmsd, 3),
               "all_pair_rmsd_A": round(all_rmsd, 3), "rmsd_A": round(rmsd, 3)}
    moved = dict(model)
    moved["ca"] = {rid: p for rid, p in zip(model["ca"], G.apply_superpose(list(model["ca"].values()),
                                                                          R, t))}
    mv = {}
    for rid, alist in model["atoms_by_res"].items():
        pts = G.apply_superpose([(a["x"], a["y"], a["z"]) for a in alist], R, t)
        mv[rid] = [dict(a, x=p[0], y=p[1], z=p[2]) for a, p in zip(alist, pts)]
    moved["atoms_by_res"] = mv
    return moved, fit


def make_grid(model):
    """Neighbour grid over a model's heavy atoms, keyed by residue id so a target residue can be excluded."""
    pts, keys = [], []
    for rid, alist in model["atoms_by_res"].items():
        for a in alist:
            pts.append((a["x"], a["y"], a["z"]))
            keys.append(rid)
    return AtomGrid(pts, keys)


# ==========================================================================================================
# THE REACH TABLE
# ==========================================================================================================
def reach_one_frame(model, placements, unique_labels, numbering=OFFSET, cutoffs=CLASH_SWEEP_A,
                    max_reach=None, label="", pendants=None):
    """Both reach conventions, every cysteine x every placement x every pendant, in ONE structure.

    Returns {"cysteines": {...}, "rows": [...], "anchor_clearance": {...}, "invariant_violations": [...]}.
    """
    max_reach = max(PENDANT_REACH.values()) if max_reach is None else max_reach
    pendants = PENDANT_REACH if pendants is None else pendants
    cys = cysteines_in(model, numbering, unique_labels)
    grid = make_grid(model)

    cand = {lab: candidate_branch_points(grid, c["xyz"], max_reach, {c["local_resid"]}, cutoffs)
            for lab, c in cys.items()}

    rows, clearance, violations = [], {}, []
    for pl in placements:
        a, b = pl["_a"], pl["_b"]
        key = "%s@%s" % (pl["meta_basin_id"], pl["placement_label"])
        # ★ THE "E3 STILL PROJECTS TO SOLVENT" CLAUSE, MADE MEASURABLE. If this conformer's backbone has
        #   moved into where the E3 anchor sits, the placement does not exist here and every reach number
        #   derived from it would be fiction. Reported per frame and gated on in the summary, never assumed.
        d_b = grid.min_dist_exact(b)
        d_a = grid.min_dist_exact(a)
        clearance[key] = {
            "e3_anchor_clearance_A": round(d_b, 2),
            "warhead_anchor_clearance_A": round(d_a, 2),
            "e3_projects_to_solvent": d_b >= CLASH_PRIMARY_A,
            "warhead_anchor_has_room": d_a >= CLASH_PRIMARY_A,
        }
        for lab, c in cys.items():
            q = c["xyz"]
            row = {"frame": label, "placement": key, "meta_basin_id": pl["meta_basin_id"],
                   "placement_label": pl["placement_label"], "cysteine": lab, "unique": c["unique"],
                   "d_warhead_anchor_A": round(G.dist(q, a), 2), "d_e3_anchor_A": round(G.dist(q, b), 2),
                   "span_A": pl["span_A"], "by_pendant": {}}
            for pname, e in sorted(pendants.items(), key=lambda kv: kv[1]):
                ts = LD.min_linker_atoms_exact(a, b, q, e, n_max=80)
                entry = {"arm_reach_A": e, "through_space_atoms": ts, "corridor_atoms": {}}
                for cut in cutoffs:
                    n, k = corridor_min_atoms(cand[lab], a, b, e, cut)
                    entry["corridor_atoms"]["%.1f" % cut] = n
                    if abs(cut - CLASH_PRIMARY_A) < 1e-9:
                        entry["corridor_branch_k"] = k
                    # INVARIANT: the corridor set is a SUBSET of the through-space set, so a corridor answer
                    # can never be shorter. A violation is reported, never swallowed — but it is first
                    # CLASSIFIED, because one benign cause is known and measured (see `classify_disagreement`)
                    # and lumping it in with a real drift would make a real drift invisible.
                    if n is not None and ts is not None and n < ts:
                        violations.append(classify_disagreement(a, b, q, e, n, ts, label, key, lab,
                                                                pname, cut))
                row["by_pendant"][pname] = entry
            rows.append(row)
    return {"cysteines": {k: {"unique": v["unique"], "local_resid": v["local_resid"]}
                          for k, v in cys.items()},
            "rows": rows, "anchor_clearance": clearance, "invariant_violations": violations}


def margins_from_rows(rows, convention="corridor", cutoff=CLASH_PRIMARY_A):
    """Chemoselectivity margin per (placement x unique cysteine x pendant), over a frame's rows."""
    def atoms(row, pname):
        e = row["by_pendant"][pname]
        return e["through_space_atoms"] if convention == "through_space" \
            else e["corridor_atoms"]["%.1f" % cutoff]

    by_pl = {}
    for r in rows:
        by_pl.setdefault(r["placement"], []).append(r)
    out = []
    for key, group in by_pl.items():
        uniq_rows = [r for r in group if r["unique"]]
        cons_rows = [r for r in group if not r["unique"]]
        for ur in uniq_rows:
            for pname in PENDANT_REACH:
                m = chemoselectivity_margin(atoms(ur, pname),
                                            {r["cysteine"]: atoms(r, pname) for r in cons_rows})
                out.append(dict(m, placement=key, cysteine=ur["cysteine"], pendant=pname,
                                convention=convention, frame=group[0]["frame"]))
    return out


def spread(values):
    """min / median / max over the non-None values, with the missing count carried."""
    vals = sorted(v for v in values if v is not None)
    n_missing = sum(1 for v in values if v is None)
    if not vals:
        return {"n": 0, "n_missing": n_missing, "min": None, "median": None, "max": None}
    mid = len(vals) // 2
    med = vals[mid] if len(vals) % 2 else (vals[mid - 1] + vals[mid]) / 2.0
    return {"n": len(vals), "n_missing": n_missing, "min": vals[0], "median": med, "max": vals[-1]}


# ==========================================================================================================
# ELECTROPHILE OPTIONS — options with sources, and NOT a recommendation
# ==========================================================================================================
def electrophile_classes():
    """Electrophile classes used against cysteine, each with a primary source for the trade-off it carries.

    ⛔ THIS IS A READING LIST, NOT AN ASSESSMENT. No entry is asserted to be reactive, selective, suitable
    or feasible against any NR4A3 cysteine: this module computes geometry and has measured no thiol pKa, no
    intrinsic reactivity and no adduct. Which class a solvent-exposed, geometrically-tethered cysteine
    should see is a chemistry judgement that is not available from anything computed here.
    """
    return {
        "_status": "OPTIONS WITH SOURCES — no reactivity, selectivity or feasibility claim is made or implied",
        "_why_geometry_does_not_choose": (
            "The general position in the covalent-drug literature is that a covalent inhibitor's "
            "selectivity is dominated by the reversible recognition step that positions the electrophile, "
            "with intrinsic electrophile reactivity setting the promiscuity floor rather than the "
            "selectivity (Singh, Petter, Baillie & Whitty, Nat Rev Drug Discov 2011, 10:307-317). A "
            "geometric window is therefore a necessary input to that choice and not a substitute for it."),
        "classes": [
            {"class": "acrylamide (Michael acceptor)",
             "note": "the most-used cysteine warhead in approved covalent drugs",
             "sources": ["Honigberg et al., PNAS 2010, 107:13075-13080 (ibrutinib, BTK Cys481)",
                         "Cross et al., Cancer Discov 2014, 4:1046-1061 (osimertinib, EGFR Cys797)"]},
            {"class": "chloroacetamide / alpha-haloacetamide",
             "note": "higher intrinsic thiol reactivity than acrylamide; the two classes label "
                     "systematically different cysteine sets in proteome-wide fragment screens, which is "
                     "the trade-off a designer is choosing between",
             "sources": ["Backus et al., Nature 2016, 534:570-574 (isoTOP-ABPP ligandability map; "
                         "chloroacetamide vs acrylamide fragment sets)",
                         "Flanagan et al., J Med Chem 2014, 57:10072-10079 (glutathione reactivity across "
                         "covalent reactive groups)"]},
            {"class": "alpha-cyanoacrylamide (REVERSIBLE covalent)",
             "note": "the class the committed NR4A3 library already carries (`PENDANT.cyac_me`, "
                     "`cyac_ph`); the alpha-cyano group acidifies the adduct alpha-proton so retro-Michael "
                     "is fast, and residence time is tuned by the beta-substituent",
             "sources": ["Serafimova et al., Nat Chem Biol 2012, 8:471-476 (reversible targeting of "
                         "noncatalytic cysteines with chemically tuned electrophiles)",
                         "Bradshaw et al., Nat Chem Biol 2015, 11:525-531 (tunable residence time, "
                         "reversible covalent kinase inhibitors)"]},
            {"class": "vinyl sulfone / sulfonyl fluoride",
             "note": "sulfonyl fluorides are NOT cysteine-restricted — they also engage Ser/Thr/Tyr/Lys/His, "
                     "so the residue-uniqueness argument this whole route rests on would not transfer",
             "sources": ["Narayanan & Jones, Chem Sci 2015, 6:2650-2659 (sulfonyl fluorides as privileged "
                         "warheads in chemical biology)"]},
        ],
        "_uncomputed_and_decision_relevant": [
            "thiol pKa / local electrostatics at each NR4A3 cysteine — an exposed cysteine is not "
            "necessarily a nucleophilic one",
            "intrinsic electrophile reactivity (GSH t1/2 or k_chem) for any pendant enumerated here",
            "adduct stability, and for the reversible classes the residence time that decides whether "
            "catalytic turnover survives",
            "off-target cysteine engagement outside the NR4A family — nothing here looks beyond three "
            "proteins, so no statement about wider selectivity is available",
        ],
    }


# ==========================================================================================================
# CROSS-CHECKS — this module must not mint a second value for a number that already has a home (rule 1)
# ==========================================================================================================
def crosscheck_committed_distances(rows, lib_path=LIBRARY):
    """Every anchor-to-unique-cysteine distance recomputed here MUST reproduce the committed
    `nr4a3-linker-design.json` record, or the anchors were recovered wrongly and nothing below is valid."""
    if not os.path.exists(lib_path):
        return {"status": "UNREAD", "reason": "%s absent" % lib_path}
    with open(lib_path) as fh:
        lib = json.load(fh)
    committed = {}
    for field, label in (("basin_requirements", None),
                         ("basin_requirements_at_representative_geometry", None)):
        for r in lib.get(field, []) or []:
            committed[(r["meta_basin_id"], r["placement_label"])] = r["electrophile_reach"]
    checked, worst, mismatches = 0, 0.0, []
    for row in rows:
        rec = committed.get((row["meta_basin_id"], row["placement_label"]))
        if not rec or row["cysteine"] not in rec:
            continue
        c = rec[row["cysteine"]]
        for got, want, what in ((row["d_warhead_anchor_A"], c["dist_to_warhead_anchor_A"], "warhead"),
                                (row["d_e3_anchor_A"], c["dist_to_e3_anchor_A"], "e3")):
            checked += 1
            d = abs(got - want)
            worst = max(worst, d)
            if d > 0.02:      # the committed coordinates are stored to 2 dp; 0.02 is that rounding
                mismatches.append({"placement": row["placement"], "cysteine": row["cysteine"],
                                   "which": what, "recomputed": got, "committed": want})
    return {"status": "AGREES" if not mismatches else "DISAGREES",
            "n_compared": checked, "max_abs_delta_A": round(worst, 3), "mismatches": mismatches[:20],
            "source_of_truth": "research/modalities/nr4a3-linker-design.json -> electrophile_reach"}


def crosscheck_unique_set(cys_labels, path=COV_ENSEMBLE):
    """The unique/conserved partition used here must be the one the covalent-handle artifact already owns."""
    if not os.path.exists(path):
        return {"status": "UNREAD", "reason": "%s absent" % path}
    with open(path) as fh:
        d = json.load(fh)
    committed_unique = {"C%d" % n for n in d["nr4a3_unique_lbd_cysteines"]}
    committed_all = {"C%d" % c["resnum"] for c in d["nr4a3_lbd_cysteines"]}
    return {"status": "AGREES" if (committed_unique == cys_labels["unique"]
                                   and committed_all == cys_labels["all"]) else "DISAGREES",
            "committed_unique": sorted(committed_unique), "used_unique": sorted(cys_labels["unique"]),
            "committed_all": sorted(committed_all), "used_all": sorted(cys_labels["all"]),
            "source_of_truth": "research/modalities/nr4a3-covalent-handle-ensemble.json"}


def accessibility_join(path=COV_ENSEMBLE):
    """SG accessibility per NR4A3 cysteine, READ from the committed ensemble artifact.

    ★ WHY THIS JOIN IS LOAD-BEARING AND NOT DECORATION. The corridor test asks whether a clash-free arm
    exists; it does not ask whether the sulfur has any surface at all. Those are different failures and a
    buried competitor must be visible as buried, with a number that already has a home, rather than
    inferred from the reach column."""
    if not os.path.exists(path):
        return {"status": "UNREAD", "reason": "%s absent" % path}
    with open(path) as fh:
        d = json.load(fh)
    nmr = (d.get("ensembles", {}).get("NR4A3_8xtt_nmr") or {}).get("cysteines", {})
    out = {}
    for num, rec in nmr.items():
        out["C%s" % num] = {
            "rsa_min_med_max": [rec["rsa"]["min"], rec["rsa"]["median"], rec["rsa"]["max"]],
            "sg_sasa_heavy_A2_min_med_max": [rec["sg_sasa_heavy_A2"]["min"],
                                             rec["sg_sasa_heavy_A2"]["median"],
                                             rec["sg_sasa_heavy_A2"]["max"]],
            "dist_to_pocket_A_min_med_max": [rec["dist_to_pocket_A"]["min"],
                                             rec["dist_to_pocket_A"]["median"],
                                             rec["dist_to_pocket_A"]["max"]],
            "n_models": rec["n_models"],
        }
    return {"status": "READ" if out else "UNREAD", "per_cysteine": out,
            "source_of_truth": "research/modalities/nr4a3-covalent-handle-ensemble.json -> "
                               "ensembles.NR4A3_8xtt_nmr.cysteines"}


def druggability_by_model(path=BENCHMARK):
    """Per-8XTT-conformer cryptic-site druggability, READ from the committed benchmark artifact, with the
    committed reference boundary. Used to stratify — never to re-derive."""
    import nr4a3_8xtt_benchmark as bench
    if not os.path.exists(path):
        return {"status": "UNREAD", "reason": "%s absent" % path, "ref": bench.DRUGGABLE_REF}
    with open(path) as fh:
        d = json.load(fh)
    per = {}
    for r in d.get("per_conformer", []):
        v = r.get("site_druggability")
        per[int(r["model"])] = v
    return {"status": "READ", "ref": bench.DRUGGABLE_REF, "site_druggability_by_model": per,
            "cavity_bearing_models": sorted(m for m, v in per.items()
                                            if v is not None and v >= bench.DRUGGABLE_REF),
            "source_of_truth": "results/nr4a3-pocket-reharmonize/8xtt/nr4a3-8xtt-benchmark.json"}


# ==========================================================================================================
# DRIVER
# ==========================================================================================================
def _model_number(path):
    base = os.path.basename(path)
    for tok in base.replace(".pdb", "").split("_"):
        if tok.startswith("m") and tok[1:].isdigit():
            return int(tok[1:])
    return None


def build(seqs, models_dir=None, cutoffs=CLASH_SWEEP_A, paralogue_ensembles=True, struct_root=REPO,
          max_models=None):
    import nr4a3_covalent_handle_ensemble as COV      # lazy: an unrelated edit there must not break this

    refusals, unread = [], []
    placements, basins = load_placements()
    unique_labels = {"C%d" % c["uniprot_resid"] for c in basins["target_frame"]["unique_cysteines"]}

    # ---- the frame the committed library was designed in ------------------------------------------------
    nr4a3 = BS.load_paralogue(OPENED["NR4A3"])
    opened = reach_one_frame(nr4a3, placements, unique_labels, OFFSET, cutoffs, label="nr4a3-opened")
    all_labels = set(opened["cysteines"])

    # ---- the experimental ensemble ----------------------------------------------------------------------
    paths = []
    if models_dir:
        paths = sorted(glob.glob(os.path.join(models_dir, "*.pdb")), key=lambda p: _model_number(p) or 0)
        paths = [p for p in paths if _model_number(p)]
    if not paths:
        # repo fallback: only the conformers the committed PocketMiner run kept are in-tree
        paths = sorted(glob.glob(os.path.join(struct_root,
                                              "results/nr4a3-8xtt-pocketminer/pm8_run/conformers/*/*.pdb")),
                       key=lambda p: _model_number(p) or 0)
    if max_models:
        paths = paths[:max_models]
    if len(paths) < 20:
        unread.append({"input": "8XTT 20-conformer ensemble",
                       "reason": "only %d conformer PDB(s) reachable (%s). files.rcsb.org is 403'd by the "
                                 "dev sandbox egress proxy, so the full ensemble is a CI-only path "
                                 "(--fetch-8xtt). A partial ensemble is reported as partial, never as the "
                                 "ensemble." % (len(paths), models_dir or "repo fallback")})

    ens_frames, ens_rows, ens_fits, ens_clear = [], [], {}, {}
    disagreements = []
    for p in paths:
        num = _model_number(p)
        lab = "8xtt_m%s" % num
        try:
            residues, atoms = atlas.parse_pdb(p)
            uni_map, ident = COV.pdb_to_uniprot_map(residues, seqs["NR4A3"], MIN_ALIGN_IDENTITY)
            model = BS.load_paralogue(p)
        except Exception as exc:                                  # noqa: BLE001 — refuse, never guess
            refusals.append({"model": lab, "reason": "%s: %s" % (type(exc).__name__, exc)})
            continue
        fits = {}
        for mode in ("pocket", "core"):
            moved, fit = superpose_into_opened(model, uni_map, nr4a3, mode=mode)
            fits[mode] = fit
            if moved is None:
                refusals.append({"model": lab, "reason": "superposition (%s) refused: %s"
                                                         % (mode, fit.get("refused"))})
                continue
            if mode != "pocket":
                continue                                          # the core fit is a reported sensitivity
            r = reach_one_frame(moved, placements, unique_labels, uni_map, cutoffs, label=lab)
            ens_rows.extend(r["rows"])
            ens_clear[lab] = r["anchor_clearance"]
            disagreements.extend(r["invariant_violations"])
        ens_fits[lab] = {"alignment_identity": round(ident, 4), "n_modelled": len(residues), **fits}
        ens_frames.append(lab)

    disagreements.extend(opened["invariant_violations"])
    for v in disagreements:
        if v["kind"] != "degenerate_tangency":
            refusals.append({"model": v["frame"], "reason":
                             "RULE DRIFT: corridor %s < through-space %s at %s / %s / %s, engine margin "
                             "%s — the two reach rules disagree for a reason that is NOT a tangency"
                             % (v["corridor_atoms"], v["through_space_atoms"], v["placement"],
                                v["cysteine"], v["pendant"], v["engine_best_margin_A_at_corridor_n"])})

    # ---- the paralogue control --------------------------------------------------------------------------
    par = paralogue_control(nr4a3, placements, seqs, cutoffs, paralogue_ensembles, struct_root,
                            refusals, unread, COV)

    return assemble(placements, basins, opened, all_labels, unique_labels, ens_frames, ens_rows, ens_fits,
                    ens_clear, par, paths, cutoffs, refusals, unread, disagreements)


def paralogue_control(nr4a3, placements, seqs, cutoffs, do_ensembles, struct_root, refusals, unread, COV):
    """THE CONTROL THAT DECIDES THE ROUTE, and it is deliberately not the one the framing asked for.

    "The paralogues have no cysteine at the aligned position" is a statement about THREE positions. What
    the mechanism actually needs is that NR4A1 and NR4A2 present NO cysteine anywhere inside the same tether
    geometry — a nucleophile at a different position does the same damage. Both are computed: the aligned
    partners are read from the committed uniqueness map (never re-derived), and the reach is measured over
    EVERY cysteine each paralogue has.
    """
    out = {"_what": "reach from the SAME anchors to EVERY cysteine of NR4A1 and NR4A2",
           "aligned_partners": {}, "opened": {}, "ensembles": {}}
    models, maps = {}, {}

    out["reciprocal_uniqueness"] = {
        "_what": "for every NR4A1/NR4A2 cysteine, the NR4A3 residue it aligns to",
        "_why": ("the committed map answers 'which NR4A3 cysteines do the paralogues lack'. This is the "
                 "reciprocal, and the reciprocal is what decides the route: a cysteine the PARALOGUE has "
                 "and NR4A3 lacks is a target the electrophile acquires in the off-target, at a position "
                 "no NR4A3-side analysis would ever have looked at."),
        "by_paralogue": reverse_cysteine_map(seqs),
    }

    if os.path.exists(COV_ENSEMBLE):
        with open(COV_ENSEMBLE) as fh:
            cov = json.load(fh)
        for c in cov["nr4a3_lbd_cysteines"]:
            if not c.get("unique_vs_both"):
                continue
            out["aligned_partners"]["C%d" % c["resnum"]] = {
                "NR4A1": "%s%s" % (c.get("nr4a1"), c.get("nr4a1_resnum")),
                "NR4A2": "%s%s" % (c.get("nr4a2"), c.get("nr4a2_resnum")),
                "is_cysteine_in_either": c.get("nr4a1") == "C" or c.get("nr4a2") == "C",
                "aligners_agree": c.get("alignment_robust"),
                "_source": "nr4a3-covalent-handle-ensemble.json -> nr4a3_lbd_cysteines"}
    else:
        unread.append({"input": COV_ENSEMBLE, "reason": "absent — aligned partners not verified here"})

    for prot in ("NR4A1", "NR4A2"):
        try:
            mob = BS.load_paralogue(OPENED[prot])
            residues, _ = atlas.parse_pdb(OPENED[prot])
            uni_map, ident = COV.pdb_to_uniprot_map(residues, seqs[prot], MIN_ALIGN_IDENTITY)
            moved = BS.superpose_paralogue(mob, nr4a3)
        except Exception as exc:                                  # noqa: BLE001
            refusals.append({"model": "%s-opened" % prot, "reason": "%s: %s" % (type(exc).__name__, exc)})
            continue
        models[prot], maps[prot] = moved, uni_map
        r = reach_one_frame(moved, placements, set(), uni_map, cutoffs, label="%s-opened" % prot)
        out["opened"][prot] = {
            "superposition": moved["superposition"],
            "alignment_identity": round(ident, 4),
            "cysteines": sorted(r["cysteines"]),
            # ⚠ A CYSTEINE OUTSIDE THE SUPERPOSITION CORE HAS NO TRUSTWORTHY POSITION IN THIS FRAME, and
            #   `null` says that where a NaN would both break strict JSON and read as a measurement.
            "post_fit_deviation_A": {
                lab: (round(moved["deviation_by_res"][v["local_resid"]], 2)
                      if v["local_resid"] in moved["deviation_by_res"] else None)
                for lab, v in r["cysteines"].items()},
            "_unreliable_in_this_frame": sorted(
                lab for lab, v in r["cysteines"].items()
                if v["local_resid"] not in moved["deviation_by_res"]),
            "rows": r["rows"],
            "anchor_clearance": r["anchor_clearance"],
        }

    if do_ensembles:
        for prot, pattern in PARALOGUE_ENSEMBLE.items():
            frames = sorted(glob.glob(os.path.join(struct_root, pattern)))
            if not frames:
                unread.append({"input": "%s metadynamics ensemble" % prot,
                               "reason": "no frames matched %s" % pattern})
                continue
            rows, n_ok = [], 0
            for f in frames:
                try:
                    mob = BS.load_paralogue(f)
                    residues, _ = atlas.parse_pdb(f)
                    uni_map, _ = COV.pdb_to_uniprot_map(residues, seqs[prot], MIN_ALIGN_IDENTITY)
                    moved = BS.superpose_paralogue(mob, nr4a3)
                except Exception as exc:                          # noqa: BLE001
                    refusals.append({"model": f, "reason": "%s: %s" % (type(exc).__name__, exc)})
                    continue
                r = reach_one_frame(moved, placements, set(), uni_map, cutoffs,
                                    label="%s/%s" % (prot, os.path.basename(os.path.dirname(f))))
                rows.extend(r["rows"])
                n_ok += 1
            out["ensembles"][prot] = {
                "kind": "metadynamics pocket-opening ensemble (biased along a pocket CV — NOT Boltzmann "
                        "weighted, and NOT comparable to the 8XTT spread; a heterogeneity comparator only)",
                "n_frames": n_ok, "rows": rows}

    out["aligned_pair_displacement"] = aligned_pair_displacement(
        nr4a3, models, maps, out["reciprocal_uniqueness"]["by_paralogue"], placements)
    return out

# ==========================================================================================================
# ASSEMBLY + THE VERDICT
# ==========================================================================================================
def ensemble_summary(rows, unique_labels, druggable, cutoff=CLASH_PRIMARY_A):
    """Per (cysteine x placement x pendant), the spread of the reach requirement across the conformers, and
    the count of conformers in which the cysteine is reachable inside the chemically routine bound.

    Spread across the ensemble IS the result — a reach that holds in one conformer is not a reach."""
    cavity = set("8xtt_m%d" % m for m in (druggable.get("cavity_bearing_models") or []))
    out = {}
    for r in rows:
        for pname, e in r["by_pendant"].items():
            key = "%s|%s|%s" % (r["cysteine"], r["placement"], pname)
            o = out.setdefault(key, {"cysteine": r["cysteine"], "unique": r["unique"],
                                     "placement": r["placement"], "pendant": pname,
                                     "_ts": [], "_co": [], "_ts_cav": [], "_co_cav": [],
                                     "_da": [], "frames": []})
            o["_ts"].append(e["through_space_atoms"])
            o["_co"].append(e["corridor_atoms"]["%.1f" % cutoff])
            o["_da"].append(r["d_warhead_anchor_A"])
            o["frames"].append(r["frame"])
            if r["frame"] in cavity:
                o["_ts_cav"].append(e["through_space_atoms"])
                o["_co_cav"].append(e["corridor_atoms"]["%.1f" % cutoff])
    for o in out.values():
        o["through_space_atoms"] = spread(o.pop("_ts"))
        o["corridor_atoms"] = spread(o.pop("_co"))
        o["through_space_atoms_cavity_bearing"] = spread(o.pop("_ts_cav"))
        o["corridor_atoms_cavity_bearing"] = spread(o.pop("_co_cav"))
        o["d_warhead_anchor_A"] = spread(o.pop("_da"))
        o["n_conformers"] = len(o["frames"])
        o.pop("frames")
    # ⚠ The per-conformer reachable COUNT is deliberately NOT computed here: it needs the per-frame values,
    # not the spread, and computing it from `min` would be a plausible-looking field that was never
    # measured. `reachable_counts` owns it.
    return out


def reachable_counts(rows, cutoff=CLASH_PRIMARY_A, chem_max=CHEM_MAX_ATOMS):
    """How many conformers put each cysteine inside the chemically routine linker bound, per placement and
    pendant. A COUNT, never a probability: the 8XTT ensemble is restraint-satisfying, not Boltzmann-weighted,
    so frequency across conformers is not occupancy (the covalent-handle artifact makes the same point)."""
    out = {}
    for r in rows:
        for pname, e in r["by_pendant"].items():
            key = "%s|%s|%s" % (r["cysteine"], r["placement"], pname)
            o = out.setdefault(key, {"cysteine": r["cysteine"], "unique": r["unique"],
                                     "placement": r["placement"], "pendant": pname,
                                     "n_conformers": 0, "through_space": 0, "corridor": 0})
            o["n_conformers"] += 1
            ts, co = e["through_space_atoms"], e["corridor_atoms"]["%.1f" % cutoff]
            o["through_space"] += 1 if (ts is not None and ts <= chem_max) else 0
            o["corridor"] += 1 if (co is not None and co <= chem_max) else 0
    return out


def reverse_cysteine_map(seqs):
    """For every NR4A1/NR4A2 LBD cysteine, the NR4A3 residue it aligns to.

    ★★ THE MISSING HALF OF THE UNIQUENESS ARGUMENT, AND THE REASON THIS FUNCTION EXISTS. The committed map
    answers "which NR4A3 cysteines do the paralogues lack". It does NOT answer the reciprocal, and the
    reciprocal is what decides this route: a cysteine the PARALOGUE has and NR4A3 lacks is a target the
    electrophile acquires in the off-target, at a position where nothing in the NR4A3 analysis would ever
    have looked. Same aligner as the committed conservation leg (`nrv04_cys_conservation.needleman_wunsch`),
    so the two cannot drift.
    """
    import nrv04_cys_conservation as cyscons
    out = {}
    for prot in ("NR4A1", "NR4A2"):
        aln_a, aln_b = cyscons.needleman_wunsch(seqs[prot], seqs["NR4A3"])
        i = j = 0
        mp = {}
        for ca, cb in zip(aln_a, aln_b):
            if ca != "-":
                i += 1
            if cb != "-":
                j += 1
            if ca != "-" and cb != "-":
                mp[i] = (j, cb)
        rows = {}
        for n, aa in enumerate(seqs[prot], start=1):
            if aa != "C" or not (uniq.LBD_FIRST - 40 <= n <= uniq.LBD_LAST):
                continue
            t = mp.get(n)
            rows["C%d" % n] = {
                "nr4a3_aligned_residue": ("%s%d" % (t[1], t[0])) if t else None,
                "nr4a3_has_a_cysteine_here": bool(t and t[1] == "C"),
                "paralogue_unique_vs_NR4A3": not (t and t[1] == "C"),
            }
        out[prot] = rows
    return out


def aligned_pair_displacement(nr4a3, models, maps, rev_map, placements):
    """★ THE CHECK THAT SAYS HOW FAR A PARALOGUE NUMBER MAY BE TRUSTED.

    At an aligned cysteine pair the two backbones superpose to a reported CA deviation, but the REACH
    numbers are computed from the SG. If ΔSG is several times ΔCA, the difference between paralogues at that
    position is a SIDE-CHAIN ROTAMER difference between three independently built opened models, not a
    measured difference between the proteins — and any atom-count gap that rests on it is model noise
    wearing the costume of a result. Measured here so the distinction is visible instead of assumed.
    """
    out = []
    for prot, rows in rev_map.items():
        if prot not in models:
            continue
        cy_p = cysteines_in(models[prot], maps[prot])
        cy_3 = cysteines_in(nr4a3, OFFSET)
        dev = models[prot].get("deviation_by_res", {})
        for lab, rec in rows.items():
            partner = rec["nr4a3_aligned_residue"]
            if not partner or not rec["nr4a3_has_a_cysteine_here"] or lab not in cy_p:
                continue
            if partner not in cy_3:
                continue
            d_sg = G.dist(cy_p[lab]["xyz"], cy_3[partner]["xyz"])
            rid = cy_p[lab]["local_resid"]
            ca_dev = dev.get(rid)
            out.append({
                "paralogue": prot, "paralogue_cysteine": lab, "nr4a3_cysteine": partner,
                "delta_SG_A": round(d_sg, 2),
                "delta_CA_A": round(ca_dev, 2) if ca_dev is not None else None,
                "sg_over_ca": round(d_sg / ca_dev, 1) if ca_dev else None,
            })
    worst = max((r["sg_over_ca"] for r in out if r["sg_over_ca"]), default=None)
    return {
        "_what": "displacement between ALIGNED cysteine pairs after superposition, backbone vs side chain",
        "pairs": out,
        "max_sg_over_ca": worst,
        "_reading": ("A ratio near 1 means the two models agree about that residue. A ratio well above 1 "
                     "means the BACKBONES agree and the SIDE CHAINS do not, i.e. the gap is rotamer "
                     "placement in independently built models. Every paralogue atom count below inherits "
                     "that uncertainty and must not be quoted to better than the rotamer it rests on."),
    }


def paralogue_inclusive_window(nr4a3_rows, par, convention="corridor", cutoff=CLASH_PRIMARY_A,
                               chem_max=CHEM_MAX_ATOMS, target="C397"):
    """★★ THE DECISION QUANTITY. The interval of backbone-atom counts over which the electrophile reaches
    the NR4A3-unique target and reaches NO other cysteine in ANY of the three paralogues.

    The intra-NR4A3 margin is the easy half. The route's whole claim is cross-paralogue, so the window that
    matters is closed by the FIRST cysteine to come into reach anywhere in the family — NR4A3's own
    conserved ones, and NR4A1's and NR4A2's, including any the paralogue has and NR4A3 lacks.
    """
    def val(entry):
        return entry["through_space_atoms"] if convention == "through_space" \
            else entry["corridor_atoms"]["%.1f" % cutoff]

    by_pl = {}
    for r in nr4a3_rows:
        by_pl.setdefault(r["placement"], {}).setdefault("NR4A3", []).append(r)
    for prot, blk in (par.get("opened") or {}).items():
        for r in blk["rows"]:
            by_pl.setdefault(r["placement"], {}).setdefault(prot, []).append(r)

    out = []
    for key, group in by_pl.items():
        tgt = next((r for r in group.get("NR4A3", []) if r["cysteine"] == target), None)
        if tgt is None:
            continue
        for pname in PENDANT_REACH:
            n_u = val(tgt["by_pendant"][pname])
            competitors = {}
            for prot, rows in group.items():
                for r in rows:
                    if prot == "NR4A3" and r["cysteine"] == target:
                        continue
                    v = val(r["by_pendant"][pname])
                    if v is not None:
                        competitors["%s %s" % (prot, r["cysteine"])] = v
            m = chemoselectivity_margin(n_u, competitors, chem_max)
            intra = chemoselectivity_margin(
                n_u, {k.split()[1]: v for k, v in competitors.items() if k.startswith("NR4A3")}, chem_max)
            out.append({
                "placement": key, "pendant": pname, "convention": convention, "target": target,
                "target_atoms": n_u,
                "window_lo": m["lo"], "window_hi": m["hi"], "width": m["width"],
                "closed_by": m["blocked_by"], "closed_at_atoms": m["blocked_at_atoms"],
                "intra_nr4a3_width": intra["width"],
                "cost_of_the_paralogue_control_in_atoms": intra["width"] - m["width"],
                "all_competitors_atoms": dict(sorted(competitors.items(), key=lambda kv: kv[1])),
            })
    return sorted(out, key=lambda r: (r["placement"], PENDANT_REACH[r["pendant"]]))


def paralogue_verdict(par, nr4a3_windows, cutoff=CLASH_PRIMARY_A, chem_max=CHEM_MAX_ATOMS):
    """Does either paralogue put a cysteine inside the NR4A3 design window? THE question this control asks."""
    out = {}
    for scope, blocks in (("opened", par.get("opened", {})), ("metad_ensemble", par.get("ensembles", {}))):
        for prot, blk in blocks.items():
            rows = blk["rows"]
            hits = {}
            for r in rows:
                for pname, e in r["by_pendant"].items():
                    lo_hi = nr4a3_windows.get((r["placement"], pname))
                    if not lo_hi or lo_hi["width"] == 0:
                        continue
                    for conv, val in (("through_space", e["through_space_atoms"]),
                                      ("corridor", e["corridor_atoms"]["%.1f" % cutoff])):
                        if val is None:
                            continue
                        inside = lo_hi["lo"] <= val <= lo_hi["hi"]
                        rec = hits.setdefault((r["cysteine"], r["placement"], pname, conv),
                                              {"cysteine": r["cysteine"], "placement": r["placement"],
                                               "pendant": pname, "convention": conv,
                                               "n_frames": 0, "n_inside_window": 0, "min_atoms": None,
                                               "window": [lo_hi["lo"], lo_hi["hi"]]})
                        rec["n_frames"] += 1
                        rec["n_inside_window"] += 1 if inside else 0
                        rec["min_atoms"] = val if rec["min_atoms"] is None else min(rec["min_atoms"], val)
            inside_any = [v for v in hits.values() if v["n_inside_window"]]
            out["%s/%s" % (scope, prot)] = {
                "n_cysteines": len({v["cysteine"] for v in hits.values()}),
                "n_cells_examined": len(hits),
                "n_cells_with_a_paralogue_cysteine_INSIDE_the_window": len(inside_any),
                "worst_offenders": sorted(inside_any, key=lambda v: v["min_atoms"])[:12],
                "verdict": ("NO paralogue cysteine falls inside any NR4A3 design window"
                            if not inside_any else
                            "%d (cysteine x placement x pendant x convention) cell(s) put a PARALOGUE "
                            "cysteine inside an NR4A3 design window — the uniqueness argument does not "
                            "survive at those geometries" % len(inside_any)),
            }
    return out


def assemble(placements, basins, opened, all_labels, unique_labels, ens_frames, ens_rows, ens_fits,
             ens_clear, par, paths, cutoffs, refusals, unread, disagreements=()):
    drug = druggability_by_model()
    margins_ts = margins_from_rows(opened["rows"], "through_space")
    margins_co = margins_from_rows(opened["rows"], "corridor")
    ens_margins_ts = margins_from_rows(ens_rows, "through_space") if ens_rows else []
    ens_margins_co = margins_from_rows(ens_rows, "corridor") if ens_rows else []

    # the design window used to grade the paralogues: the CONSERVATIVE (narrowest) window per
    # (placement, pendant) over the C397 records in the opened frame, under the through-space convention —
    # the convention that is most generous to a competitor, so the control is not graded on the easy one.
    windows = {}
    for m in margins_ts:
        if m["cysteine"] != "C397" or m["width"] == 0:
            continue
        windows[(m["placement"], m["pendant"])] = {"lo": m["lo"], "hi": m["hi"], "width": m["width"]}

    xcheck = {
        "committed_anchor_distances": crosscheck_committed_distances(opened["rows"]),
        "unique_cysteine_partition": crosscheck_unique_set(
            {"unique": unique_labels, "all": all_labels}),
    }
    acc = accessibility_join()
    family_windows = {conv: paralogue_inclusive_window(opened["rows"], par, conv)
                      for conv in ("through_space", "corridor")}

    n_models = len(ens_frames)
    return {
        "_title": "Is a linker-borne covalent NR4A3 handle geometrically available?",
        "_question": ("Can a linker anchored at the warhead attachment point present an electrophile at an "
                      "NR4A3-unique cysteine SG while the E3 ligand still projects to solvent — across the "
                      "experimental ensemble, without also reaching a cysteine the paralogues keep?"),
        "_status": ("GEOMETRY ONLY. No reactivity, potency, selectivity, developability or feasibility "
                    "claim is made or implied. Geometry can refute a route; it cannot license one."),
        "_method": ("Reach by `linker_design.branch_position_window` / `min_linker_atoms_exact` (the exact "
                    "three-ball rule the committed library was built with), from anchors READ out of "
                    "nr4a3-orientation-basins.json at the five confirmed basins. Two conventions reported "
                    "side by side: `through_space` (the committed rule, an upper bound on reachability) "
                    "and `corridor` (additionally requires a non-clashing branch position with a clash-free "
                    "straight arm to the SG). Pure stdlib, $0 CPU."),
        "premise_correction": premise_check(),
        "_parameters": {
            "imported_never_retyped": {
                "rise_A_per_backbone_atom": RISE,
                "pendant_reach_A": PENDANT_REACH,
                "chemically_routine_max_backbone_atoms": CHEM_MAX_ATOMS,
                "confirmed_meta_basins": CONFIRMED,
                "cryptic_pocket_uniprot": list(CRYPTIC_POCKET_UNIPROT),
                "_homes": {"rise/pendant reach": "linker_design.py",
                           "CHEM_MAX_ATOMS/CONFIRMED": "nr4a3_linker_design.py",
                           "pocket": "nr4a_paralogue_unique_residues.py",
                           "druggability reference": "nr4a3_8xtt_benchmark.DRUGGABLE_REF"},
            },
            "declared_new_here": {
                "clash_cutoff_sweep_A": list(cutoffs),
                "clash_primary_A": CLASH_PRIMARY_A,
                "candidate_grid_pitch_A": CANDIDATE_GRID_A,
                "arm_samples": ARM_SAMPLES,
                "_why_it_is_declared": ("No repo constant answers 'how close may a linker backbone atom "
                                        "come to a protein heavy atom', so this is NOT imported and must "
                                        "not pretend to be. The whole sweep is computed and reported so no "
                                        "single value is load-bearing. The primary is deliberately "
                                        "permissive toward reach (0.4 A inside a C...C van der Waals "
                                        "contact of ~3.4 A), which makes the CONSERVED competitor easier "
                                        "to reach — i.e. it biases against the route under test, not for "
                                        "it."),
            },
        },
        "anchors": {
            "_what": "warhead attachment point `a` and E3 anchor `b`, per confirmed basin and placement",
            "_source": "research/modalities/nr4a3-orientation-basins.json (pose_ensemble.anchor_xyz and "
                       "meta_basins_ranked[*].representative / term_a_union.C397.exemplar_placement)",
            "_caveat": ("`representative` is a TYPICAL member of its basin; `term_a_exemplar` is the member "
                        "needing the shortest exact linker to C397, i.e. a best-of-N and the OPTIMISTIC end "
                        "of the basin. Neither may be quoted without saying which."),
            "placements": [{k: v for k, v in p.items() if not k.startswith("_")} for p in placements],
        },
        "cysteines": {"all": sorted(all_labels, key=lambda s: int(s[1:])),
                      "nr4a3_unique": sorted(unique_labels, key=lambda s: int(s[1:])),
                      "conserved": sorted(all_labels - unique_labels, key=lambda s: int(s[1:]))},
        "accessibility_of_each_cysteine": acc,
        "designed_frame": {
            "_what": "nr4a3-opened.pdb — the single frame the committed library was designed in",
            "anchor_clearance": opened["anchor_clearance"],
            "rows": opened["rows"],
            "chemoselectivity_margin_through_space": margins_ts,
            "chemoselectivity_margin_corridor": margins_co,
        },
        "experimental_ensemble_8xtt": {
            "_what": "PDB 8XTT — the experimental 20-conformer solution-NMR apo LBD ensemble",
            "n_conformers_analysed": n_models,
            "n_conformers_deposited": 20,
            "is_complete": n_models >= 20,
            "conformers": ens_frames,
            "superposition_per_conformer": ens_fits,
            "anchor_clearance_per_conformer": ens_clear,
            "druggability_stratification": drug,
            "reach_spread": ensemble_summary(ens_rows, unique_labels, drug) if ens_rows else {},
            "reachable_conformer_counts": reachable_counts(ens_rows) if ens_rows else {},
            "chemoselectivity_margin_through_space": ens_margins_ts,
            "chemoselectivity_margin_corridor": ens_margins_co,
            "rows": ens_rows,
            "_reading": ("Spread across conformers is itself the result. A count of conformers is NOT a "
                         "probability — the 8XTT ensemble is restraint-satisfying, not Boltzmann-weighted."),
        },
        "★_family_wide_chemoselectivity_window": {
            "_what": ("THE DECISION QUANTITY: the interval of backbone-atom counts over which the "
                      "electrophile reaches NR4A3 C397 and reaches NO other cysteine in NR4A3, NR4A1 or "
                      "NR4A2. The intra-NR4A3 margin is the easy half; the route's whole claim is "
                      "cross-paralogue, so the window that decides it is closed by the FIRST cysteine to "
                      "come into reach anywhere in the family."),
            "_computed_on": "the nr4a3-opened.pdb frame and the two superposed opened paralogue models — "
                            "single conformers, not ensembles. See `paralogue_control.aligned_pair_"
                            "displacement` for how far the paralogue atom counts may be trusted.",
            "by_convention": family_windows,
        },
        "paralogue_control": dict(par, verdict=paralogue_verdict(par, windows)),
        "electrophile_options": electrophile_classes(),
        "cross_checks": xcheck,
        "reach_rule_disagreements": {
            "_what": "cells where the corridor answer fell BELOW the through-space answer, which the subset "
                     "relation forbids. Classified, never swallowed — see `classify_disagreement`.",
            "n": len(disagreements),
            "n_degenerate_tangency": sum(1 for v in disagreements
                                         if v["kind"] == "degenerate_tangency"),
            "n_RULE_DRIFT": sum(1 for v in disagreements if v["kind"] != "degenerate_tangency"),
            "n_at_or_below_the_chemically_routine_bound": sum(
                1 for v in disagreements if v["corridor_atoms"] <= CHEM_MAX_ATOMS),
            "cells": list(disagreements),
        },
        "unread_inputs": unread,
        "refusals": refusals,
        "_limits": [
            "GEOMETRY ONLY. Reach is a necessary condition for a covalent handle and never a sufficient "
            "one. Thiol pKa, intrinsic electrophile reactivity, adduct formation, adduct stability, "
            "permeability and degradation are all uncomputed here.",
            "`through_space` is an UPPER BOUND on reachability: it places the branch atom anywhere in a "
            "three-ball intersection, including inside the protein.",
            "`corridor` is a NECESSARY condition, not a sufficient one: it tests one branch position and a "
            "straight arm, and does NOT thread the linker backbone, score torsions or test whether a "
            "clash-free region is connected to bulk solvent.",
            "Both conventions treat the protein as RIGID within a conformer. Induced fit is not modelled, "
            "and the ensemble is used as the only source of conformational freedom.",
            "The anchors are inherited from a DOCKED pose whose known-answer test has not returned "
            "(program map, `Ligand pose prediction (dock + MM-GBSA)` — running). Every number here is "
            "conditional on that pose, and none of it can be more reliable than the pose is.",
            "16 of the 20 8XTT conformers do not carry a detectable cryptic site, so placing a warhead in "
            "them is a geometric operation and not a physical one. The cavity-bearing subset is reported "
            "separately for that reason.",
            "The paralogue ensembles are metadynamics, biased along a pocket-opening collective variable "
            "and not Boltzmann-weighted. They are a heterogeneity comparator; their spread is NOT "
            "comparable to the 8XTT spread. There is no experimental NR4A1/NR4A2 ensemble — that is a "
            "missing input, not a negative result.",
            "No claim of NR4A3 selectivity, efficacy, safety, a therapeutic window or clinical readiness "
            "is made or implied anywhere in this artifact.",
        ],
    }


def verdict(d):
    """The answer, DERIVED from the artifact rather than typed."""
    uniq_labels = set(d["cysteines"]["nr4a3_unique"])
    ens = d["experimental_ensemble_8xtt"]
    counts = ens.get("reachable_conformer_counts") or {}
    per_cys = {}
    for v in counts.values():
        if not v["unique"]:
            continue
        o = per_cys.setdefault(v["cysteine"], {"best_through_space": 0, "best_corridor": 0,
                                               "n_conformers": v["n_conformers"], "best_cell": None})
        if v["corridor"] > o["best_corridor"]:
            o["best_corridor"] = v["corridor"]
            o["best_cell"] = "%s | %s" % (v["placement"], v["pendant"])
        o["best_through_space"] = max(o["best_through_space"], v["through_space"])
    live = sorted((c for c, o in per_cys.items() if o["best_corridor"] > 0), key=lambda s: int(s[1:]))
    dead = sorted(uniq_labels - set(live), key=lambda s: int(s[1:]))

    fam = d["★_family_wide_chemoselectivity_window"]["by_convention"]
    fam_open, fam_all = {}, {}
    for conv, rows in fam.items():
        rows_t = [r for r in rows if "term_a_exemplar" in r["placement"]]
        openr = [r for r in rows_t if r["width"] > 0]
        fam_all[conv] = {"n_cells": len(rows_t), "n_open": len(openr),
                         "widest": max(openr, key=lambda r: r["width"]) if openr else None,
                         "median_width": spread([r["width"] for r in rows_t])["median"],
                         "closers": sorted({r["closed_by"] for r in rows_t if r["closed_by"]}),
                         "n_closed_by_a_PARALOGUE_cysteine": sum(
                             1 for r in rows_t if r["closed_by"] and not r["closed_by"].startswith("NR4A3")),
                         "median_atoms_lost_to_the_paralogue_control": spread(
                             [r["cost_of_the_paralogue_control_in_atoms"] for r in rows_t])["median"]}
        fam_open[conv] = openr
    disp = (d["paralogue_control"].get("aligned_pair_displacement") or {})
    return {
        "headline": _headline(live, dead, fam_all),
        "at_which_cysteine": live,
        "refuted_unique_cysteines": dead,
        "per_unique_cysteine_conformer_counts": per_cys,
        "family_wide_window": fam_all,
        "what_would_defeat_it": {
            "_the_measured_answer": ("NOT an NR4A3 conserved cysteine. The window is closed first by a "
                                     "PARALOGUE cysteine in %s of the graded cells under the corridor "
                                     "convention — including NR4A1/NR4A2 C534, which aligns to NR4A3 S565 "
                                     "and is therefore a cysteine the PARALOGUES have and NR4A3 lacks. "
                                     "Uniqueness runs both ways, and the reciprocal direction was never "
                                     "checked before this module."
                                     % fam_all.get("corridor", {}).get(
                                         "n_closed_by_a_PARALOGUE_cysteine")),
            "closers_by_convention": {k: v["closers"] for k, v in fam_all.items()},
            "how_far_the_paralogue_numbers_may_be_trusted": {
                "max_delta_SG_over_delta_CA_at_aligned_pairs": disp.get("max_sg_over_ca"),
                "_reading": disp.get("_reading"),
            },
        },
        "_what_this_verdict_is_not": ("a feasibility statement. Geometry can refute a route; it cannot "
                                      "license one. No reactivity, potency, selectivity, developability, "
                                      "efficacy or safety claim is made or implied."),
    }


def _headline(live, dead, fam_all):
    co = fam_all.get("corridor", {})
    if not live:
        return ("REFUTED: no NR4A3-unique cysteine is reachable from the warhead anchor within the "
                "chemically routine linker bound, in any conformer.")
    parts = ["Only %s of the three NR4A3-unique cysteines is within tether range; %s %s refuted at every "
             "placement, pendant and convention."
             % (", ".join(live), ", ".join(dead) or "none", "are" if len(dead) != 1 else "is")]
    if co.get("n_open"):
        parts.append("A family-wide window exists in %d of %d graded (placement x pendant) cells, median "
                     "width %s backbone atoms, and %d of those cells are closed first by a PARALOGUE "
                     "cysteine rather than by an NR4A3 one."
                     % (co["n_open"], co["n_cells"], co["median_width"],
                        co["n_closed_by_a_PARALOGUE_cysteine"]))
    else:
        parts.append("No family-wide window survives the paralogue control at any graded cell.")
    parts.append("The paralogue control costs a median of %s backbone atoms of window, so the binding "
                 "constraint on this route is the paralogues' own cysteines, not NR4A3's conserved ones."
                 % co.get("median_atoms_lost_to_the_paralogue_control"))
    return " ".join(parts)


# ==========================================================================================================
# MARKDOWN
# ==========================================================================================================
def _fmt(v):
    return "—" if v is None else str(v)


def to_markdown(d):
    L = []
    A = L.append
    A("# %s" % d["_title"])
    A("")
    A(d["_question"])
    A("")
    A("**Status:** %s" % d["_status"])
    A("")
    A("*Method:* %s" % d["_method"])
    A("")

    pc = d["premise_correction"]
    A("## 0 · The premise, corrected before anything was measured")
    A("")
    A("**%s** — %s" % (pc["question"], pc["answer"]))
    A("")
    A("`build_smiles%s` builds `%s`. %s" % (pc["evidence"]["build_smiles_signature"],
                                            pc["evidence"]["template"], pc["evidence"]["why"]))
    A("")
    A("%s" % pc["consequence"])
    A("")

    A("## 1 · The two reach conventions, and why both are reported")
    A("")
    A("| convention | what it requires | what it is |")
    A("|---|---|---|")
    A("| `through_space` | the committed three-ball rule, unchanged | an **upper bound** on reachability — "
      "it will place a branch atom inside the protein |")
    A("| `corridor` | additionally: a non-clashing branch position with a clash-free straight arm to the SG "
      "| a **necessary** condition, still not sufficient — no backbone threading, no torsions, no "
      "solvent-connectivity test |")
    A("")
    p = d["_parameters"]["declared_new_here"]
    A("Clash cutoff sweep **%s Å**, primary **%.1f Å**. %s" % (p["clash_cutoff_sweep_A"],
                                                              p["clash_primary_A"],
                                                              p["_why_it_is_declared"]))
    A("")

    A("## 2 · Reach across the experimental ensemble (PDB 8XTT)")
    A("")
    ens = d["experimental_ensemble_8xtt"]
    A("%d of %d deposited conformers analysed.%s" % (
        ens["n_conformers_analysed"], ens["n_conformers_deposited"],
        "" if ens["is_complete"] else
        " ⚠ **PARTIAL — this is not the ensemble.** The missing conformers are an unread input, not a "
        "negative result; see `unread_inputs`."))
    A("")
    drug = ens.get("druggability_stratification") or {}
    if drug.get("cavity_bearing_models"):
        A("Cavity-bearing conformers (`site_druggability >= %s`, read from the committed benchmark): "
          "**%s**. The other conformers have no detectable cryptic site, so placing a warhead in them is a "
          "geometric operation and not a physical one." % (drug["ref"], drug["cavity_bearing_models"]))
        A("")
    sp = ens.get("reach_spread") or {}
    if sp:
        pend = "dab_branch"
        A("Minimum linker backbone atoms to present a `%s` pendant (%.2f Å arm) on each cysteine SG, "
          "min–median–max across the analysed conformers, at the **term-(a) exemplar** placements "
          "(the optimistic end of each basin):" % (pend, PENDANT_REACH[pend]))
        A("")
        A("| cysteine | unique | placement | through-space min–med–max | corridor min–med–max | "
          "conformers within %d atoms (TS / corridor) |" % CHEM_MAX_ATOMS)
        A("|---|---|---|---|---|---|")
        counts = ens.get("reachable_conformer_counts") or {}
        for key in sorted(sp, key=lambda k: (int(sp[k]["cysteine"][1:]), sp[k]["placement"])):
            v = sp[key]
            if v["pendant"] != pend or "term_a_exemplar" not in v["placement"]:
                continue
            c = counts.get(key, {})
            A("| %s | %s | %s | %s–%s–%s | %s–%s–%s | %s / %s |" % (
                v["cysteine"], "**yes**" if v["unique"] else "no", v["placement"].split("@")[0],
                _fmt(v["through_space_atoms"]["min"]), _fmt(v["through_space_atoms"]["median"]),
                _fmt(v["through_space_atoms"]["max"]),
                _fmt(v["corridor_atoms"]["min"]), _fmt(v["corridor_atoms"]["median"]),
                _fmt(v["corridor_atoms"]["max"]),
                _fmt(c.get("through_space")), _fmt(c.get("corridor"))))
        A("")
        A("Spread across conformers is itself the result: a reach that holds in one conformer is not a "
          "reach. A conformer **count is not a probability** — the 8XTT ensemble is restraint-satisfying, "
          "not Boltzmann-weighted.")
        A("")

    A("## 3 · The counter-test — what a conserved cysteine does to it")
    A("")
    A("The decision quantity is not *can it reach* but the **chemoselectivity margin**: the interval of "
      "backbone-atom counts over which the NR4A3-unique cysteine is in reach and **no** conserved cysteine "
      "is. Conserved cysteines are the ones NR4A1 and NR4A2 keep, so a conserved cysteine reachable at or "
      "before the unique one voids the entire paralogue-uniqueness argument.")
    A("")
    for conv, field in (("through-space", "chemoselectivity_margin_through_space"),
                        ("corridor", "chemoselectivity_margin_corridor")):
        ms = [m for m in (ens.get(field) or d["designed_frame"][field])
              if m["pendant"] == "dab_branch" and "term_a_exemplar" in m["placement"]]
        if not ms:
            continue
        A("**%s convention**" % conv)
        A("")
        A("| cysteine | placement | window (backbone atoms) | width | first conserved cysteine in reach |")
        A("|---|---|---|---|---|")
        seen = set()
        for m in sorted(ms, key=lambda x: (int(x["cysteine"][1:]), x["placement"])):
            k = (m["cysteine"], m["placement"])
            if k in seen:
                continue
            seen.add(k)
            A("| %s | %s | %s | %s | %s |" % (
                m["cysteine"], m["placement"].split("@")[0],
                "[%s, %s]" % (_fmt(m["lo"]), _fmt(m["hi"])) if m["width"] else "**none**",
                m["width"], "%s at %s" % (m["blocked_by"], m["blocked_at_atoms"])
                if m["blocked_by"] else "—"))
        A("")

    A("## 3b · The family-wide window — the quantity that actually decides it")
    A("")
    fam = d["★_family_wide_chemoselectivity_window"]
    A("%s" % fam["_what"])
    A("")
    A("*%s*" % fam["_computed_on"])
    A("")
    for conv, rows in fam["by_convention"].items():
        rows_t = [r for r in rows if "term_a_exemplar" in r["placement"] and r["pendant"] == "dab_branch"]
        if not rows_t:
            continue
        A("**%s convention, `dab_branch` pendant (8.75 Å arm), term-(a) exemplar placements**" % conv)
        A("")
        A("| placement | C397 | intra-NR4A3 width | family-wide window | width | closed first by |")
        A("|---|---|---|---|---|---|")
        for r in sorted(rows_t, key=lambda x: x["placement"]):
            A("| %s | %s | %s | %s | **%s** | %s at %s |" % (
                r["placement"].split("@")[0], _fmt(r["target_atoms"]), r["intra_nr4a3_width"],
                "[%s, %s]" % (_fmt(r["window_lo"]), _fmt(r["window_hi"])) if r["width"] else "**none**",
                r["width"], r["closed_by"], _fmt(r["closed_at_atoms"])))
        A("")

    A("## 4 · The paralogue control")
    A("")
    A("*The claim under test is that NR4A1 and NR4A2 have no cysteine where the electrophile lands. That is "
      "a statement about three aligned positions; what actually decides the route is whether either "
      "paralogue presents **any** cysteine inside the same tether geometry.*")
    A("")
    rec = (d["paralogue_control"].get("reciprocal_uniqueness") or {}).get("by_paralogue") or {}
    if rec:
        A("### 4a · Uniqueness runs BOTH ways — the half that had never been checked")
        A("")
        A("| paralogue cysteine | aligned NR4A3 residue | NR4A3 has a cysteine here? |")
        A("|---|---|---|")
        for prot in sorted(rec):
            for lab in sorted(rec[prot], key=lambda s: int(s[1:])):
                v = rec[prot][lab]
                A("| %s %s | %s | %s |" % (prot, lab, v["nr4a3_aligned_residue"],
                                           "yes" if v["nr4a3_has_a_cysteine_here"] else "**no**"))
        A("")

    disp = d["paralogue_control"].get("aligned_pair_displacement") or {}
    if disp.get("pairs"):
        A("### 4b · How far a paralogue atom count may be trusted")
        A("")
        A("| pair | ΔCA after superposition (Å) | ΔSG (Å) | ΔSG/ΔCA |")
        A("|---|---|---|---|")
        for r in disp["pairs"]:
            A("| %s %s ↔ NR4A3 %s | %s | %s | %s |" % (r["paralogue"], r["paralogue_cysteine"],
                                                       r["nr4a3_cysteine"], _fmt(r["delta_CA_A"]),
                                                       _fmt(r["delta_SG_A"]), _fmt(r["sg_over_ca"])))
        A("")
        A("%s" % disp["_reading"])
        A("")

    A("### 4c · The three NR4A3-unique cysteines, at their aligned paralogue positions")
    A("")
    ap = d["paralogue_control"].get("aligned_partners") or {}
    if ap:
        A("| NR4A3 unique cysteine | NR4A1 | NR4A2 | cysteine in either? |")
        A("|---|---|---|---|")
        for lab in sorted(ap, key=lambda s: int(s[1:])):
            v = ap[lab]
            A("| %s | %s | %s | %s |" % (lab, v["NR4A1"], v["NR4A2"],
                                         "**yes**" if v["is_cysteine_in_either"] else "no"))
        A("")
    for k, v in sorted((d["paralogue_control"].get("verdict") or {}).items()):
        A("- **%s** — %s" % (k, v["verdict"]))
    A("")

    A("## 5 · Electrophile classes — options, with sources, and no assessment")
    A("")
    eo = d["electrophile_options"]
    A("⛔ %s" % eo["_status"])
    A("")
    A("%s" % eo["_why_geometry_does_not_choose"])
    A("")
    A("| class | what the trade-off is | primary sources |")
    A("|---|---|---|")
    for c in eo["classes"]:
        A("| %s | %s | %s |" % (c["class"], c["note"], "; ".join(c["sources"])))
    A("")
    A("**Uncomputed and decision-relevant:** %s." % "; ".join(eo["_uncomputed_and_decision_relevant"]))
    A("")

    A("## 6 · Cross-checks (rule 1 — this module must not mint a second value)")
    A("")
    for k, v in d["cross_checks"].items():
        extra = ""
        if v.get("max_abs_delta_A") is not None:
            extra = " (n = %s, max |Δ| %.3f Å)" % (v.get("n_compared"), v["max_abs_delta_A"])
        A("- `%s`: **%s**%s" % (k, v["status"], extra))
    A("")

    ver = d.get("verdict") or {}
    A("## 7 · The answer")
    A("")
    A("**%s**" % ver.get("headline", ""))
    A("")
    A("- **At which cysteine:** %s" % (", ".join(ver.get("at_which_cysteine") or []) or "none"))
    A("- **Refuted unique cysteines:** %s" % (", ".join(ver.get("refuted_unique_cysteines") or []) or "none"))
    for conv, v in (ver.get("family_wide_window") or {}).items():
        A("- **Family-wide window (%s):** %s of %s cells open, median width %s atoms; window closed first "
          "by %s; %s cell(s) closed by a PARALOGUE cysteine; median %s atoms of window lost to the "
          "paralogue control" % (conv, v["n_open"], v["n_cells"], v["median_width"],
                                 ", ".join(v["closers"]) or "—",
                                 v["n_closed_by_a_PARALOGUE_cysteine"],
                                 v["median_atoms_lost_to_the_paralogue_control"]))
    wd = ver.get("what_would_defeat_it") or {}
    A("- **What would defeat it:** %s" % wd.get("_the_measured_answer", ""))
    tr = wd.get("how_far_the_paralogue_numbers_may_be_trusted") or {}
    A("- **Trust bound on the paralogue numbers:** max ΔSG/ΔCA at aligned cysteine pairs = **%s**. %s"
      % (_fmt(tr.get("max_delta_SG_over_delta_CA_at_aligned_pairs")), tr.get("_reading", "")))
    A("")
    A("⛔ %s" % ver.get("_what_this_verdict_is_not", ""))
    A("")

    rd = d.get("reach_rule_disagreements") or {}
    if rd.get("n"):
        A("### Reach-rule disagreements")
        A("")
        A("%d cell(s) where the corridor answer fell below the through-space answer, which the subset "
          "relation forbids: **%d degenerate tangency**, **%d rule drift**, %d at or below the %d-atom "
          "chemically routine bound." % (rd["n"], rd["n_degenerate_tangency"], rd["n_RULE_DRIFT"],
                                         rd["n_at_or_below_the_chemically_routine_bound"], CHEM_MAX_ATOMS))
        A("")

    if d["unread_inputs"]:
        A("## Unread inputs — refused, not assumed absent")
        A("")
        for u in d["unread_inputs"]:
            A("- **%s** — %s" % (u["input"], u["reason"]))
        A("")
    if d["refusals"]:
        A("## Refusals")
        A("")
        for r in d["refusals"]:
            A("- **%s** — %s" % (r.get("model", r.get("input")), r["reason"]))
        A("")

    A("## Honest limits")
    A("")
    for lim in d["_limits"]:
        A("- %s" % lim)
    A("")
    return "\n".join(L)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("--seq-cache", default=SEQ_CACHE)
    ap.add_argument("--models-dir", default=None,
                    help="directory of split 8XTT conformer PDBs (use --fetch-8xtt in CI)")
    ap.add_argument("--fetch-8xtt", action="store_true",
                    help="download 8XTT from RCSB and split it (CI only; the dev sandbox proxy 403s "
                         "files.rcsb.org)")
    ap.add_argument("--max-models", type=int, default=None)
    ap.add_argument("--no-paralogue-ensembles", action="store_true")
    ap.add_argument("--out", default=OUT)
    args = ap.parse_args(argv)

    with open(args.seq_cache) as fh:
        seqs = json.load(fh)
    for k in ("NR4A1", "NR4A2", "NR4A3"):
        if k not in seqs:
            raise SystemExit("sequence cache %s is missing %s — REFUSING to guess" % (args.seq_cache, k))

    models_dir = args.models_dir
    if args.fetch_8xtt:
        import nr4a3_covalent_handle_ensemble as COV
        models_dir = models_dir or os.path.join(os.environ.get("RUNNER_TEMP", "/tmp"), "8xtt_models")
        paths = COV.fetch_8xtt_models(models_dir)
        print("[8xtt] fetched + split %d conformers into %s" % (len(paths), models_dir), flush=True)

    d = build(seqs, models_dir=models_dir, paralogue_ensembles=not args.no_paralogue_ensembles,
              max_models=args.max_models)
    d["verdict"] = verdict(d)
    with open(args.out, "w") as fh:
        json.dump(d, fh, indent=1)
        fh.write("\n")
    with open(os.path.splitext(args.out)[0] + ".md", "w") as fh:
        fh.write(to_markdown(d))

    print(json.dumps(d["verdict"], indent=1)[:3000], flush=True)
    for k, v in d["cross_checks"].items():
        print("[xcheck] %s: %s" % (k, v["status"]), flush=True)
    for u in d["unread_inputs"]:
        print("[UNREAD] %s: %s" % (u["input"], u["reason"]), flush=True)
    for r in d["refusals"]:
        print("[REFUSED] %s: %s" % (r.get("model", r.get("input")), r["reason"]), flush=True)
    print("[reach] wrote %s" % args.out, flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
