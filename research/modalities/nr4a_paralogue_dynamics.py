#!/usr/bin/env python3
"""DOES THE CATEGORICAL CASE SURVIVE PARALOGUE DYNAMICS? — matched NR4A1 / NR4A2 / NR4A3 conformer ensembles.

THE QUESTION THIS ANSWERS, AND WHY IT IS THE ONE LEFT OPEN
----------------------------------------------------------
Tier 2 passed on the CATEGORICAL axis: NR4A3 carries reactive residues that BOTH paralogues lack, so the
paralogues are structurally *incapable* rather than merely disfavoured. That matters because the MARGINAL
(induced-interface) axis needs ~2.0 kcal/mol against a best-case resolvable difference of 1.12 kcal/mol — a
confirmation tool at its limit, not a discovery tool.

Two things were established on the NR4A3 side (`nr4a3_handle_ensemble.py`): C397's exposure is robust over 100
real NR4A3 conformers (RSA median 0.416; reaches the <=12-atom gate in 96 % of unbiased frames), and the
chemistry axis is ONE residue deep (C420 and C559 reach the gate in 0/75 frames).

**The untested assumption was on the PARALOGUE side.** Uniqueness is a SEQUENCE fact and is not in doubt. What
had never been tested is whether paralogue DYNAMICS open a COMPENSATING site:

  (1) does NR4A1 or NR4A2 present, in a populated conformer, some OTHER nucleophile within tether range of the
      same linker paths — a cysteine ELSEWHERE IN THE FOLD, not merely at the aligned position? A degrader
      does not care which cysteine it labels. If a paralogue cysteine sits inside the same reach envelope,
      the covalent bond CAN form on the paralogue and "structurally incapable" is false.
  (2) does a paralogue expose lysines inside the modelled E2~Ub transfer zone that make term (b)
      non-discriminating?

Everything to date compared ONE static opened conformer per paralogue. This module compares DISTRIBUTIONS.

WHAT IS DELIBERATELY DIFFERENT FROM THE COMMITTED RUN — and why each difference is the conservative direction
-------------------------------------------------------------------------------------------------------------
* **ALL cysteines, not the three NR4A3-unique ones.** `nr4a3_basin_search.run_arm_pose` evaluates term (a) on
  `unique_cysteines` only; the conserved set is summarised at the 20-atom SAMPLING CEILING, never at the
  12-atom gate. So "all 7 term-(a) basins reach C397 and only C397" is a statement about {C397, C420, C559}.
  NR4A3's conserved cysteines (C496, C506, C536, C594) have direct paralogue homologues (NR4A1 C465/C475/
  C505/C566), so a conserved NR4A3 cysteine inside the gate would be a NON-DISCRIMINATING electrophile target
  and no marginal statistic in the committed run would show it. Here every cysteine with an SG is scored.
* **Each species uses its OWN homologous cryptic pocket** (NR4A3's Pocket-5 lining mapped by the same BLOSUM62
  Needleman-Wunsch aligner `nr4a3_metad` uses for the paralogue CV), its own pocket centroid, and its own
  exit-vector pose ensemble at identical parameters. Transplanting NR4A3's anchors onto a paralogue would
  measure the wrong thing.
* **Term (b) uses ONE set of E3 placements** sampled on the NR4A3 reference frame and evaluated against every
  species' conformers superposed into that frame — the atlas's matched standard. A difference between species
  therefore cannot be an artefact of three independent searches finding different corners of orientation space.
* **Transfer-zone coverage is computed EXACTLY, not by Monte Carlo.** The committed `transfer_zone` draws
  `n_e2_samples` points uniformly in a ball of radius `mobility_A` about the observed catalytic-cysteine
  anchor and asks which lysines fall within `lysine_transfer_A`. For a lysine at distance r from the anchor
  that per-sample probability is the sphere-sphere lens volume over the ball volume — a closed form. Using it
  removes the MC noise that would otherwise dominate a per-conformer comparison, and `--validate-coverage`
  checks it against the committed sampler.

HONEST SCOPE. Design prep, not validation. Reach and exposure are NECESSARY, not sufficient: nothing here
tests thiol pKa, nucleophilicity, adduct stability or electrophile promiscuity. The envelope is an
E3-INDEPENDENT UPPER BOUND, which is the conservative direction for THIS question — a paralogue cysteine that
is closed in the envelope is closed for every recruiter, while one that is open has not been shown reachable
by any real recruiter. No efficacy, safety, therapeutic-window or clinical claim is made or implied.

Usage
    python nr4a_paralogue_dynamics.py --mode static      # the three matched opened models ($0, seconds)
    python nr4a_paralogue_dynamics.py --mode all         # + every MD ensemble found under --ensemble-root
    python nr4a_paralogue_dynamics.py --validate-coverage
"""
from __future__ import annotations

import argparse
import json
import math
import os
import random
import statistics as st
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)

import basin_geom as G                      # noqa: E402
import nr4a_differential_atlas as ATLAS     # noqa: E402
import nr4a3_basin_search as B              # noqa: E402

SPECIES = ("NR4A3", "NR4A1", "NR4A2")
STATIC_MODEL = {sp: os.path.join(REPO, "results", "nr4a3-matrix", f"{sp.lower()}-opened.pdb") for sp in SPECIES}
SEQ_CACHE = os.path.join(HERE, "nr4a-sequences-cache.json")
UNIQUE_JSON = os.path.join(HERE, "nr4a-paralogue-unique-residues.json")
NATIVE_REGISTRY = os.path.join(HERE, "nr4a3-e3-arm-registry-native.json")
OUT = os.path.join(HERE, "nr4a-paralogue-dynamics.json")

# MD ensembles. NR4A3's already exists (the reharmonize run); the paralogue ones are written by the Vast
# metad+release lane into results/nr4a{1,2}-pocket-ensemble/{metad,release_rep0,release_rep1,release_rep2}.
ENSEMBLE_ROOT = {
    "NR4A3": os.path.join(REPO, "results", "nr4a3-pocket-reharmonize"),
    "NR4A1": os.path.join(REPO, "results", "nr4a1-pocket-ensemble"),
    "NR4A2": os.path.join(REPO, "results", "nr4a2-pocket-ensemble"),
}
# (subdir, biased?) — identical layout per species so the comparison is structural, not by convention.
SUBSETS = (("metad", True), ("release_rep0", False), ("release_rep1", False), ("release_rep2", False))

# Matched to nr4a3_handle_ensemble.py so the NR4A3 numbers here reproduce the committed ones.
N_POSES = 12
N_MC = 12000
SEED = 20260725

# The three NR4A3 cysteines the program's categorical chemistry axis is built on (UniProt numbering). Kept as
# a literal so the verdict cannot silently change if the Tier-0 artifact is regenerated; the inventory block
# re-derives the same set from the alignment and any disagreement is visible in the output.
NR4A3_UNIQUE_CYS = {397, 420, 559}
EXPOSED_RSA = 0.25          # the standard relative-SASA cutoff, same as nr4a_differential_atlas.EXPOSED_RSA
# Linker lengths the matched test is read at. 12 is the design GATE and where the verdict is quoted; the
# longer ones are reported because a matched placement reaches an NR4A3-unique cysteine in only ~0.2 % of
# placements, so the 12-atom cell alone is thin — if the species contrast holds across the profile, the gate
# reading is corroborated rather than isolated.
LENGTHS = (12, 14, 16, 20)


# ---------------------------------------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------------------------------------
def quantiles(xs):
    """PURE. n / min / p10 / median / p90 / max / mean / sd of a list. {} when empty."""
    if not xs:
        return {}
    s = sorted(float(x) for x in xs)
    n = len(s)

    def q(f):
        if n == 1:
            return s[0]
        i = f * (n - 1)
        lo = int(math.floor(i))
        hi = min(lo + 1, n - 1)
        return s[lo] + (s[hi] - s[lo]) * (i - lo)

    return {"n": n, "min": round(s[0], 4), "p10": round(q(0.10), 4), "median": round(q(0.50), 4),
            "p90": round(q(0.90), 4), "max": round(s[-1], 4), "mean": round(sum(s) / n, 4),
            "sd": round(st.pstdev(s), 4) if n > 1 else 0.0}


def wilson95(k, n):
    """PURE. Wilson 95 % interval for a binomial proportion — the repo's standard
    (systems/POLICY-evidence.md §2.2). A
    fraction over 75 frames without an interval invites over-reading; this is the interval."""
    if n <= 0:
        return None
    z = 1.959963985
    p = k / n
    d = 1.0 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(max(0.0, p * (1 - p) / n + z * z / (4 * n * n))) / d
    return [round(max(0.0, c - h), 4), round(min(1.0, c + h), 4)]


def lens_volume(R, d, r):
    """PURE. Volume of the intersection of two spheres, radii R and d, centre separation r. Standard closed
    form; the two degenerate branches are the containment cases."""
    if r >= R + d:
        return 0.0
    if r <= abs(R - d):
        rr = min(R, d)
        return 4.0 / 3.0 * math.pi * rr ** 3
    return (math.pi * (R + d - r) ** 2
            * (r * r + 2 * r * d - 3 * d * d + 2 * r * R + 6 * d * R - 3 * R * R) / (12.0 * r))


def coverage_probability(r, mobility_A, transfer_d_A, n_e2_samples):
    """PURE. Probability the committed `transfer_zone` sampler marks a lysine at distance `r` from the
    observed transfer anchor as COVERED.

    The sampler draws `n_e2_samples` E2 positions uniformly in the ball of radius `mobility_A` about the
    anchor (`rr = mob * U**(1/3)` with a uniform direction — exactly uniform in the ball volume) and marks the
    lysine covered if ANY sample is within `transfer_d_A`. Per sample that is the lens volume over the ball
    volume; over the draw it is 1 - (1-p)^n. Exact, so a per-conformer comparison is not swamped by MC noise.
    """
    if mobility_A <= 0.0:
        return 1.0 if r <= transfer_d_A else 0.0
    ball = 4.0 / 3.0 * math.pi * mobility_A ** 3
    p = lens_volume(mobility_A, transfer_d_A, r) / ball
    p = min(1.0, max(0.0, p))
    return 1.0 - (1.0 - p) ** n_e2_samples


def species_offset(model, species, seqs):
    """local residue id -> UniProt residue number, DERIVED from the model's own sequence rather than
    hardcoded. Raises if the construct is not found in the full-length sequence — a silent wrong offset would
    mislabel every residue in the report."""
    full = seqs[species] if isinstance(seqs[species], str) else seqs[species].get("sequence")
    probe = model["seq"][:40]
    i = full.find(probe)
    if i < 0:
        raise SystemExit(f"  ABORT: {species} model sequence not found in the cached UniProt sequence")
    if full.find(probe, i + 1) >= 0:
        raise SystemExit(f"  ABORT: {species} construct prefix is not unique in the UniProt sequence")
    return (i + 1) - model["ids"][0]


def align_map(mobile, ref):
    """mobile local resid -> ref local resid, by the same BLOSUM62 Needleman-Wunsch the atlas and the metad
    CV mapping use. PURE apart from the aligner."""
    aln = ATLAS.nw_align(mobile["seq"], ref["seq"])
    out = {}
    for i, j in aln:
        if i is not None and j is not None:
            out[mobile["ids"][i]] = ref["ids"][j]
    return out


_CONSTRUCT_CACHE = {}


def construct_frame(model, species, seqs, ref, ref_pocket_local):
    """(local→UniProt offset, homologous-pocket local ids) for THIS model's own construct, cached by sequence.

    ⚠ WHY THIS IS PER-MODEL AND NOT PER-SPECIES. The static `nr4a1-opened.pdb` covers UniProt 348-598, but the
    MD construct is trimmed by `nr4a3_metad._resolve_target`, which maps the NR4A3 LBD window onto the
    paralogue BY ALIGNMENT and can land on a different first residue — and mdtraj then renumbers the exported
    frames from 1 regardless. Deriving the offset once from the static model and applying it to MD frames
    would therefore shift every residue label by the difference, silently: C465 would be reported as some
    other number, the homologous pocket would be the wrong ten residues, and nothing would raise. Both are
    re-derived from each model's own sequence instead, and the result is cached on the sequence so the cost is
    one alignment per distinct construct rather than one per frame."""
    key = (species, model["seq"])
    hit = _CONSTRUCT_CACHE.get(key)
    if hit is not None:
        return hit
    off = species_offset(model, species, seqs)
    if species == "NR4A3":
        pocket = [r for r in ref_pocket_local if r in model["aa_of"]]
        missing = [r for r in ref_pocket_local if r not in model["aa_of"]]
    else:
        pocket, missing = homologous_pocket(model, ref, ref_pocket_local)
    val = (off, pocket, missing)
    _CONSTRUCT_CACHE[key] = val
    if len(_CONSTRUCT_CACHE) <= 12:
        print(f"[pdyn] construct {species}: {len(model['residues'])} residues, local->UniProt +{off}, "
              f"homologous pocket {len(pocket)}/{len(ref_pocket_local)} "
              f"(UniProt {[r + off for r in pocket]})", flush=True)
    return val


def homologous_pocket(model, ref, ref_pocket_local):
    """The paralogue's own local ids for NR4A3's Pocket-5 lining. Same construction `nr4a3_metad._resolve_target`
    uses to put the metadynamics CV on the HOMOLOGOUS pocket, so the ensemble and the analysis agree."""
    m2r = align_map(model, ref)
    r2m = {v: k for k, v in m2r.items()}
    got = [r2m[r] for r in ref_pocket_local if r in r2m]
    return got, [r for r in ref_pocket_local if r not in r2m]


# ---------------------------------------------------------------------------------------------------------
# TERM (a): every cysteine, every conformer
# ---------------------------------------------------------------------------------------------------------
def cysteines_of(model, offset, ref, ref_aa_of):
    """Every cysteine with an SG, labelled with its UniProt number AND the NR4A3 residue it aligns to — so a
    paralogue cysteine at a position where NR4A3 has none is visible as such rather than as a bare number."""
    m2r = align_map(model, ref) if model is not ref else {rid: rid for rid, _ in model["residues"]}
    out = []
    for rid, aa in model["residues"]:
        if aa != "C":
            continue
        xyz = B.atom_xyz(model, rid, "SG")
        if xyz is None:
            continue
        r3 = m2r.get(rid)
        out.append({
            "local_resid": rid, "uniprot_resid": rid + offset, "xyz": xyz,
            "label": f"C{rid + offset}",
            "nr4a3_aligned_local": r3,
            "nr4a3_aligned": (f"{ref_aa_of.get(r3)}{r3 + B.UNIPROT_OFFSET}" if r3 is not None else None),
            "nr4a3_has_cys_here": (ref_aa_of.get(r3) == "C") if r3 is not None else False,
        })
    return out


def analyse_conformer_terma(path, species, seqs, ref, ref_aa_of, ref_pocket_local, seed,
                            n_poses=N_POSES, n_mc=N_MC):
    """One conformer: RSA of every Cys and Lys, plus the E3-INDEPENDENT term-(a) reach envelope over ALL
    cysteines, recomputed on THIS conformer with its own pocket centroid and its own exit-vector poses.

    The residue numbering and the homologous pocket are derived from THIS model's own sequence — an MD
    construct can be trimmed differently from the static opened model, and mdtraj renumbers exports from 1."""
    model = B.load_paralogue(path)                 # heavy atoms only — every criterion here is heavy-atom
    residues, atoms = ATLAS.parse_pdb(path)        # with H, matching the committed Shrake-Rupley RSA exactly
    rsa = ATLAS.residue_rsa(residues, ATLAS.shrake_rupley(atoms))

    offset, pocket_local, _missing = construct_frame(model, species, seqs, ref, ref_pocket_local)
    side = []
    for rid in pocket_local:
        for a in model["atoms_by_res"].get(rid, []):
            if a["name"] not in B.BACKBONE:
                side.append((a["x"], a["y"], a["z"]))
    centroid = G.centroid(side)
    field = G.SquaredDistanceField(model["heavy_xyz"], cell=0.9, clamp=8.0)

    rng = random.Random(seed)
    poses = B.build_pose_ensemble(model, {"pocket_centroid": centroid}, field, n_poses, rng)
    cys = cysteines_of(model, offset, ref, ref_aa_of)
    env = B.term_a_feasibility_envelope(poses, cys, field, rng, n_mc=n_mc) if (poses and cys) else None

    rec = {"frame": os.path.basename(os.path.dirname(path)) or os.path.basename(path),
           "n_poses": len(poses), "pocket_centroid": [round(c, 3) for c in centroid], "cys": {}, "lys": {}}
    for c in cys:
        lab = c["label"]
        row = {"rsa": round(rsa.get(c["local_resid"], 0.0), 4),
               "dist_to_pocket_centroid_A": round(G.dist(c["xyz"], centroid), 2),
               "nr4a3_aligned": c["nr4a3_aligned"], "nr4a3_has_cys_here": c["nr4a3_has_cys_here"]}
        if env:
            # the envelope keys on C<uniprot_resid>, which is exactly `label`
            e = env["per_cysteine"].get(lab)
            if e:
                row["shortest_linker_atoms"] = e["shortest_linker_with_any_feasible_anchor"]
                row["min_exit_anchor_to_SG_A"] = e["dist_exit_anchor_to_SG_A"]["min"]
                row["frac_anchor_space_at_gate_12"] = \
                    e["by_linker_atoms"][B.PARAMS["linker_gate_atoms"]]["mean_fraction_of_anchor_space"]
        rec["cys"][lab] = row
    for rid, aa in model["residues"]:
        if aa != "K":
            continue
        rec["lys"][f"K{rid + offset}"] = {"rsa": round(rsa.get(rid, 0.0), 4), "local_resid": rid}
    return rec


# ---------------------------------------------------------------------------------------------------------
# TERM (b): one matched placement set, every species' conformers
# ---------------------------------------------------------------------------------------------------------
def sample_transfer_anchors(ref_model, registry_path, n_samples, n_poses, seed, arms_wanted=None):
    """Sample E3 placements on the NR4A3 reference EXACTLY as the committed search does and keep only what
    term (b) consumes: the transformed observed E2 catalytic-cysteine anchor. One set, reused for every
    species and conformer — that is what makes the comparison matched."""
    reg = json.load(open(registry_path))
    e2 = reg.get("e2_geometry") or {}
    params = dict(B.PARAMS)
    cal = (e2.get("substrate_lysine_calibration") or {})
    if cal.get("nearest_lysine_to_catalytic_cys_A"):
        params["lysine_transfer_A"] = cal["nearest_lysine_to_catalytic_cys_A"]
    if e2.get("measured"):
        params["ring_to_e2_cys_A"] = e2["ring_to_catalytic_cys_A"]

    u = json.load(open(UNIQUE_JSON))
    pocket_local = [x - B.UNIPROT_OFFSET for x in u["cryptic_pocket_uniprot"]]
    side = []
    for rid in pocket_local:
        for a in ref_model["atoms_by_res"].get(rid, []):
            if a["name"] not in B.BACKBONE:
                side.append((a["x"], a["y"], a["z"]))
    centroid = G.centroid(side)
    field = G.SquaredDistanceField(ref_model["heavy_xyz"], cell=0.9, clamp=8.0)
    rng = random.Random(seed)
    poses = B.build_pose_ensemble(ref_model, {"pocket_centroid": centroid}, field, n_poses, rng)

    anchors, per_arm = [], {}
    for aid, rec in reg.get("arms", {}).items():
        if rec.get("status") != "OK":
            continue
        if arms_wanted and aid not in arms_wanted:
            continue
        arm = B.load_arm_from_registry(rec)
        if not arm.get("tanchor"):
            continue
        n_acc = 0
        for pose in poses:
            pls, _stats = B.sample_placements(arm, pose, field, rng, n_samples, params)
            for pl in pls:
                if pl.get("tanchor"):
                    # a_t (the warhead exit-vector anchor) and a_e (the E3 ligand exit atom) are the two
                    # foci of the linker path, so keeping them makes the SAME placement usable for the
                    # matched term-(a) test as well as for term (b) — one placement set, both terms.
                    anchors.append({"arm": aid, "pose": pose["pose_id"], "xyz": pl["tanchor"],
                                    "a_t": tuple(pose["anchor_xyz"]), "a_e": pl["anchor_e3"]})
                    n_acc += 1
        per_arm[aid] = {"recruiter": arm["recruiter"], "n_accepted_with_transfer_anchor": n_acc,
                        "tanchor_source": arm["tanchor_source"]}
    return anchors, per_arm, params, poses


def species_cysteines_in_ref_frame(path, ref_model, offset, ref_aa_of, pocket_local=None,
                                   ref_pocket_centroid=None):
    """A conformer's cysteine SG positions in the NR4A3 REFERENCE frame, plus each residue's RSA and post-fit
    deviation. This is what makes the MATCHED term-(a) test possible: the paralogue is placed in the same frame
    the E3 placements were sampled in, so the SAME construct geometry can be asked of both molecules."""
    model = B.load_paralogue(path)
    fitted = B.superpose_paralogue(model, ref_model)
    residues, atoms = ATLAS.parse_pdb(path)
    rsa = ATLAS.residue_rsa(residues, ATLAS.shrake_rupley(atoms))
    m2r = align_map(model, ref_model)
    out = []
    for rid, aa in fitted["residues"]:
        if aa != "C":
            continue
        for a in fitted["atoms_by_res"].get(rid, []):
            if a["name"] == "SG":
                dev = fitted.get("deviation_by_res", {}).get(rid)
                r3 = m2r.get(rid)
                out.append({"local_resid": rid, "uniprot_resid": rid + offset,
                            "label": f"C{rid + offset}", "xyz": (a["x"], a["y"], a["z"]),
                            "rsa": round(rsa.get(rid, 0.0), 4),
                            "nr4a3_aligned": (f"{ref_aa_of.get(r3)}{r3 + B.UNIPROT_OFFSET}"
                                              if r3 is not None else None),
                            "nr4a3_has_cys_here": (ref_aa_of.get(r3) == "C") if r3 is not None else False,
                            "fit_deviation_A": (round(dev, 2) if dev is not None else None),
                            "position_reliable": (dev is not None and dev <= 4.0)})
                break
    sup = dict(fitted["superposition"])
    # ★ THE ASSUMPTION THE MATCHED TEST RESTS ON, MEASURED RATHER THAN ASSERTED. The matched test holds the
    # warhead exit-vector anchors fixed at the NR4A3 reference pocket and asks whether the SAME construct
    # reaches a paralogue cysteine. That is only meaningful if the paralogue's HOMOLOGOUS pocket actually
    # lands there after superposition. A large offset would mean the warhead is not where the test pretends
    # it is, and the comparison would be measuring the superposition rather than the chemistry — so it is
    # measured per frame instead of taken on faith.
    if pocket_local and ref_pocket_centroid is not None:
        side = []
        for rid in pocket_local:
            for a in fitted["atoms_by_res"].get(rid, []):
                if a["name"] not in B.BACKBONE:
                    side.append((a["x"], a["y"], a["z"]))
        if side:
            sup["homologous_pocket_centroid_offset_A"] = round(
                G.dist(G.centroid(side), ref_pocket_centroid), 2)
    return out, sup


def matched_reach_hits_multi(anchors, cysteines, lengths, params=None, min_rsa=0.0):
    """`matched_reach_hits` at SEVERAL linker lengths in one pass, because the 12-atom gate alone has poor
    statistical power for this particular question.

    The design gate is 12 atoms and that is where the verdict is READ, but a matched placement reaches an
    NR4A3-unique cysteine in only ~0.2 % of placements, so a verdict computed at 12 alone rests on a handful of
    events. The same geometry at 14/16/20 atoms is far better sampled, and if the paralogue/NR4A3 contrast
    behaves the same way across the whole profile, the 12-atom reading is corroborated rather than isolated.
    Reporting the profile is also this repo's standing practice for the gate, so the choice stays visible.

    Returns {length: (hits_list, per_cysteine_counts)}. Distances are computed once and compared against each
    length's budget, so the extra lengths are nearly free."""
    params = params or B.PARAMS
    cys = [c for c in cysteines if c["rsa"] >= min_rsa]
    budgets = {n: G.contour_length_from_atoms(n, params["linker_rise_per_atom_A"])
               + 2.0 * params["electrophile_arm_A"] for n in lengths}
    big = max(budgets.values()) if budgets else 0.0
    # bytearray, not a list of ints: at 2M samples per (arm x pose) the placement set is ~23k, and 226
    # conformers x 3 species x 4 lengths x 2 variants of a Python list would be ~700 MB of pointers on a
    # runner that also has to hold the trajectory analysis. A bytearray is one byte per placement.
    out = {n: (bytearray(len(anchors)), {c["label"]: 0 for c in cys}) for n in lengths}
    cache = {}
    for i, pl in enumerate(anchors):
        row = cache.get(pl["pose"])
        if row is None:
            row = [G.dist(pl["a_t"], c["xyz"]) for c in cys]
            cache[pl["pose"]] = row
        ae = pl["a_e"]
        for j, c in enumerate(cys):
            if row[j] > big:
                continue
            s = row[j] + G.dist(ae, c["xyz"])
            if s > big:
                continue
            for n in lengths:
                if s <= budgets[n]:
                    hits, per = out[n]
                    hits[i] = 1
                    per[c["label"]] += 1
    return out


def matched_reach_hits(anchors, cysteines, gate_atoms=None, params=None, min_rsa=0.0):
    """THE DECISIVE TEST. For each E3 placement, does the SAME linker path — same warhead exit anchor, same E3
    anchor, same length budget — put a pendant electrophile on ANY of this conformer's cysteines?

    The E3-independent envelope asks the weaker question ("could SOME construct reach it"), which is the right
    upper bound for ruling a site OUT but over-counts when ruling one IN. This asks the design question: at a
    placement where the degrader labels NR4A3, is a paralogue cysteine also inside the budget?

    `min_rsa` optionally requires the cysteine to be solvent-exposed as well as reachable — a buried thiol is
    not attackable, and the committed NR4A3 argument itself leans on C397's RSA. Returns a per-placement 0/1
    list plus per-cysteine counts. Identical prolate-spheroid criterion to
    `nr4a3_basin_search.electrophile_reach`, so this is the committed rule, not a new one."""
    params = params or B.PARAMS
    gate = gate_atoms or params["linker_gate_atoms"]
    budget = G.contour_length_from_atoms(gate, params["linker_rise_per_atom_A"]) \
        + 2.0 * params["electrophile_arm_A"]
    cys = [c for c in cysteines if c["rsa"] >= min_rsa]
    hits = bytearray(len(anchors))
    per_cys = {c["label"]: 0 for c in cys}
    # |SG - a_t| depends only on the POSE, so cache it per (pose, cysteine) instead of recomputing per placement
    cache = {}
    for i, pl in enumerate(anchors):
        key = pl["pose"]
        row = cache.get(key)
        if row is None:
            row = [G.dist(pl["a_t"], c["xyz"]) for c in cys]
            cache[key] = row
        ae = pl["a_e"]
        any_hit = 0
        for j, c in enumerate(cys):
            if row[j] > budget:
                continue
            if row[j] + G.dist(ae, c["xyz"]) <= budget:
                per_cys[c["label"]] += 1
                any_hit = 1
        hits[i] = any_hit
    return hits, per_cys


def species_lysines_in_ref_frame(path, ref_model, offset, model=None, fitted=None):
    """A conformer's lysine NZ positions in the NR4A3 REFERENCE frame, each carrying its own post-fit
    deviation, so a claim about a lysine sitting in a badly-superposed loop is visibly untrustworthy. NR4A3's
    own MD frames go through the identical superposition, which is what keeps the contrast matched."""
    model = model or B.load_paralogue(path)
    fitted = fitted or B.superpose_paralogue(model, ref_model)
    residues, atoms = ATLAS.parse_pdb(path)
    rsa = ATLAS.residue_rsa(residues, ATLAS.shrake_rupley(atoms))
    out = []
    for rid, aa in fitted["residues"]:
        if aa != "K":
            continue
        for a in fitted["atoms_by_res"].get(rid, []):
            if a["name"] == "NZ":
                dev = fitted.get("deviation_by_res", {}).get(rid)
                out.append({"local_resid": rid, "uniprot_resid": rid + offset,
                            "label": f"K{rid + offset}", "xyz": (a["x"], a["y"], a["z"]),
                            "rsa": round(rsa.get(rid, 0.0), 4),
                            "fit_deviation_A": (round(dev, 2) if dev is not None else None),
                            "position_reliable": (dev is not None and dev <= 4.0)})
                break
    return out, fitted["superposition"]


def coverage_over_anchors(anchors, lysines, params, exposed_rsa=0.25):
    """Expected term-(b) coverage of ONE conformer over the matched placement set.

    Returns the mean over placements of P(zone covers >= 1 lysine) — the union probability, computed exactly
    per lysine and combined assuming the E2 draws are independent across lysines, which is the same
    independence the sampler realises. Also returns the per-lysine mean coverage so a single dominant lysine
    is visible rather than hidden inside a union."""
    mob = params.get("observed_anchor_mobility_A", 0.0)
    d = params["lysine_transfer_A"]
    n_e2 = params["n_e2_samples"]
    per_lys = {k["label"]: 0.0 for k in lysines}
    per_lys_exposed = {k["label"]: 0.0 for k in lysines}
    any_sum = 0.0
    any_exposed_sum = 0.0
    n = 0
    for a in anchors:
        ax, ay, az = a["xyz"]
        miss = 1.0
        miss_exp = 1.0
        for k in lysines:
            kx, ky, kz = k["xyz"]
            r = math.sqrt((ax - kx) ** 2 + (ay - ky) ** 2 + (az - kz) ** 2)
            p = coverage_probability(r, mob, d, n_e2)
            if p > 0.0:
                per_lys[k["label"]] += p
                miss *= (1.0 - p)
                if k["rsa"] >= exposed_rsa:
                    per_lys_exposed[k["label"]] += p
                    miss_exp *= (1.0 - p)
        any_sum += 1.0 - miss
        any_exposed_sum += 1.0 - miss_exp
        n += 1
    if not n:
        return None
    return {
        "n_placements": n,
        "P_zone_covers_any_lysine": round(any_sum / n, 5),
        "P_zone_covers_any_EXPOSED_lysine": round(any_exposed_sum / n, 5),
        "per_lysine_mean_coverage": {k: round(v / n, 5) for k, v in sorted(per_lys.items(), key=lambda kv: -kv[1])
                                     if v / n >= 1e-5},
    }


def _pool_per_cys(rows):
    """{cysteine label -> [per-frame matched hit fraction]} across a set of frame records. PURE."""
    out = {}
    for r in rows:
        for k, v in (r.get("matched_term_a", {}).get("per_cysteine") or {}).items():
            out.setdefault(k, []).append(v)
    return out


def categorical_verdict(anchors, joint):
    """THE NUMBER THE LANE EXISTS TO PRODUCE.

    The categorical claim is that at a placement where the degrader's electrophile reaches an NR4A3-unique
    cysteine, NO paralogue cysteine is reachable — so the covalent step cannot occur on the paralogue at all.
    This turns that into a probability, per placement, over the conformer ensembles:

        f3(pl)  = fraction of NR4A3 conformers in which a UNIQUE NR4A3 cysteine is at the gate at pl
        fP(pl)  = fraction of that paralogue's conformers in which ANY of its cysteines is at the gate at pl

        P(categorical | labelled)  = mean_pl [ f3 * (1-f1) * (1-f2) ] / mean_pl [ f3 ]
        P(collision  | labelled)  = 1 - the above

    The three trajectories are independent molecules, so multiplying their per-placement frequencies is the
    exact pairing rather than an approximation of one. Both the reach-only and the reach-AND-exposed readings
    are reported: a buried thiol is not attackable, so requiring RSA >= 0.25 is the design-relevant filter,
    while reach-only is the conservative upper bound on the paralogue's opportunity.

    Reported separately for the UNBIASED release ensembles (a population estimate), the BIASED metadynamics
    ensembles (an adversarial upper bound on how far each pocket opens), and the STATIC opened models (what
    the committed comparison actually had)."""
    npl = len(anchors)
    scopes = {
        "static_opened_model": lambda e: e["ensemble"] == "static_opened_model",
        "unbiased_release": lambda e: e["ensemble"].startswith("release_rep"),
        "metad_biased": lambda e: e["ensemble"] == "metad",
    }
    out = {}
    for scope, keep in scopes.items():
        sel = {sp: [e for e in joint[sp] if keep(e)] for sp in SPECIES}
        if not sel["NR4A3"] or not npl:
            continue
        row = {"n_frames": {sp: len(sel[sp]) for sp in SPECIES}, "n_placements": npl}
        # ⚠ REFUSE TO REPORT A VERDICT AGAINST AN EMPTY PARALOGUE SET. With no paralogue conformers in a
        # scope, `bare` is 1 by construction and the arithmetic returns P(collide) = 0 — a PASS produced by
        # measuring nothing, which is the single failure mode this repo keeps paying for. Before the matched
        # NR4A1/NR4A2 ensembles exist, the `unbiased_release` and `metad_biased` scopes have exactly that
        # shape, so they are marked and nulled rather than quietly reported as a clean categorical result.
        missing = [sp for sp in ("NR4A1", "NR4A2") if not sel[sp]]
        if missing:
            row["VERDICT_NOT_EVALUABLE"] = (
                f"no conformers for {missing} in this scope — every collision probability below would be 0 "
                f"by construction, not by measurement. Run the matched paralogue ensembles first.")
            out[scope] = row
            continue
        by_len = {}
        for n in LENGTHS:
            cell = {}
            for tag, key3, keyP in (("", "unique_any", "any"), ("_EXPOSED", "unique_exposed", "exposed")):
                num = den = collide = 0.0
                n_events = 0
                for i in range(npl):
                    f3 = sum(e[key3][n][i] for e in sel["NR4A3"]) / len(sel["NR4A3"])
                    if f3 == 0.0:
                        continue
                    n_events += 1
                    bare = 1.0
                    for sp in ("NR4A1", "NR4A2"):
                        if sel[sp]:
                            fp = sum(e[keyP][n][i] for e in sel[sp]) / len(sel[sp])
                            bare *= (1.0 - fp)
                    den += f3
                    num += f3 * bare
                    collide += f3 * (1.0 - bare)
                cell[f"P_categorical_given_nr4a3{tag}"] = round(num / den, 5) if den else None
                cell[f"P_paralogue_also_labelled_given_nr4a3{tag}"] = round(collide / den, 5) if den else None
                cell[f"mean_P_nr4a3_unique{tag}"] = round(den / npl, 6)
                cell[f"n_placements_with_any_nr4a3_hit{tag}"] = n_events
            for sp in SPECIES:
                if sel[sp]:
                    cell[f"mean_P_any_cysteine_{sp}"] = round(
                        sum(sum(e["any"][n]) for e in sel[sp]) / (len(sel[sp]) * npl), 6)
                    cell[f"mean_P_any_EXPOSED_cysteine_{sp}"] = round(
                        sum(sum(e["exposed"][n]) for e in sel[sp]) / (len(sel[sp]) * npl), 6)
            by_len[n] = cell
        row["by_linker_atoms"] = by_len
        gate = B.PARAMS["linker_gate_atoms"]
        row.update({k: v for k, v in by_len[gate].items()})
        row["P_paralogue_also_labelled_given_nr4a3"] = by_len[gate]["P_paralogue_also_labelled_given_nr4a3"]
        row["P_paralogue_also_labelled_given_nr4a3_EXPOSED"] = \
            by_len[gate]["P_paralogue_also_labelled_given_nr4a3_EXPOSED"]
        out[scope] = row
    return {
        "_what": "P(no paralogue cysteine is reachable | the same construct reaches an NR4A3-unique "
                 "cysteine), over one matched placement set and the conformer ensembles.",
        "_reading": "A value near 1 means the categorical chemistry axis SURVIVES dynamics: where the "
                    "degrader labels NR4A3 it cannot label a paralogue. A value materially below 1 is the "
                    "failure mode this lane was built to find — the paralogue is not structurally incapable, "
                    "it merely lacks a cysteine at the ALIGNED position while carrying one elsewhere that "
                    "the same linker path reaches.",
        "_limits": ["Reachability and exposure are necessary, not sufficient — no thiol pKa, "
                    "nucleophilicity, adduct stability or promiscuity is modelled.",
                    "Conformational independence across species is exact here (three independent "
                    "trajectories), but each species' own conformers are correlated within a replica, so "
                    "the effective n is smaller than the frame count.",
                    "The placement set is sampled on the NR4A3 reference frame; paralogue conformers are "
                    "superposed into it, carrying the core-fit residual reported per frame."],
        "gate_atoms": B.PARAMS["linker_gate_atoms"],
        "exposed_rsa_cutoff": EXPOSED_RSA,
        "nr4a3_unique_cysteines": sorted(NR4A3_UNIQUE_CYS),
        "by_scope": out,
    }


# ---------------------------------------------------------------------------------------------------------
# validation of the analytic coverage against the committed sampler
# ---------------------------------------------------------------------------------------------------------
def validate_coverage(n_trials=4000, seed=7):
    """The analytic coverage must reproduce `nr4a3_basin_search.transfer_zone`'s Monte-Carlo answer, or the
    speed-up is a silent protocol deviation. Compares over a range of anchor-to-lysine distances."""
    rng = random.Random(seed)
    params = dict(B.PARAMS)
    mob = params["observed_anchor_mobility_A"]
    d = 17.09
    n_e2 = params["n_e2_samples"]
    rows = []
    for r in (0.0, 5.0, 10.0, 14.0, 17.0, 20.0, 22.0, 24.0, 25.0, 26.0, 30.0):
        hit = 0
        for _ in range(n_trials):
            covered = False
            for _ in range(n_e2):
                v = G.random_unit_vector(rng)
                rr = mob * (rng.random() ** (1.0 / 3.0))
                e2 = (v[0] * rr, v[1] * rr, v[2] * rr)
                if (e2[0] - r) ** 2 + e2[1] ** 2 + e2[2] ** 2 <= d * d:
                    covered = True
                    break
            hit += covered
        mc = hit / n_trials
        an = coverage_probability(r, mob, d, n_e2)
        rows.append({"r_A": r, "monte_carlo": round(mc, 4), "analytic": round(an, 4),
                     "abs_diff": round(abs(mc - an), 4)})
    worst = max(rows, key=lambda x: x["abs_diff"])
    return {"_what": "analytic coverage_probability() vs the committed transfer_zone Monte-Carlo sampler",
            "mobility_A": mob, "transfer_d_A": d, "n_e2_samples": n_e2, "n_trials": n_trials,
            "rows": rows, "max_abs_diff": worst["abs_diff"],
            "passes": worst["abs_diff"] <= 0.03}


# ---------------------------------------------------------------------------------------------------------
# ensembles
# ---------------------------------------------------------------------------------------------------------
def frame_paths(species, subdir):
    d = os.path.join(ENSEMBLE_ROOT[species], subdir)
    if not os.path.isdir(d):
        return []
    out = []
    for name in sorted(os.listdir(d)):
        p = os.path.join(d, name, "frame.pdb")
        if os.path.exists(p):
            out.append((name, p))
    return out


def ensemble_census():
    """How many conformers each species actually contributes, per subset — computed BEFORE any analysis.

    ⚠ THE SILENT-EMPTY HOLE THIS CLOSES. `frame_paths` returns [] for a directory that does not exist, and
    both term drivers gate on `if fps:`. So a species with no ensemble is not an error — it is simply absent
    from `ensembles`, leaving `pooled_unbiased: null` in a JSON that is otherwise complete. Read downstream,
    "no frames" and "no reachable cysteine in any frame" are indistinguishable, and they are opposite answers
    to this lane's question. The census makes the distinction a first-class, committed field, and `main`
    refuses to run the ensembles mode when a species has zero frames unless the override is explicit.
    """
    by_species = {}
    for sp in SPECIES:
        per = {sub: len(frame_paths(sp, sub)) for sub, _ in SUBSETS}
        by_species[sp] = {
            "root": os.path.relpath(ENSEMBLE_ROOT[sp], REPO),
            "root_exists": os.path.isdir(ENSEMBLE_ROOT[sp]),
            "by_subset": per,
            "n_frames_total": sum(per.values()),
            "n_frames_unbiased": sum(v for k, v in per.items() if k.startswith("release_rep")),
        }
    return {
        "_what": "conformers available per species per subset, counted before any analysis ran",
        "_why": "distinguishes 'no frames' from 'no reachable cysteine in any frame' — opposite answers that "
                "an absent ensemble would otherwise render identically in this artifact.",
        "by_species": by_species,
        "species_with_no_frames": [sp for sp, c in by_species.items() if c["n_frames_total"] == 0],
    }


def summarise_terma(rows, gate=None):
    gate = gate or B.PARAMS["linker_gate_atoms"]
    labels = sorted({lab for r in rows for lab in r["cys"]})
    out = {}
    for lab in labels:
        cells = [r["cys"][lab] for r in rows if lab in r["cys"]]
        ls = [c.get("shortest_linker_atoms") for c in cells]
        opened = [x for x in ls if x is not None]
        n_gate = sum(1 for x in opened if x <= gate)
        out[lab] = {
            "n_frames": len(cells),
            "nr4a3_aligned": cells[0].get("nr4a3_aligned"),
            "nr4a3_has_cys_here": cells[0].get("nr4a3_has_cys_here"),
            "rsa": quantiles([c["rsa"] for c in cells]),
            "dist_to_pocket_centroid_A": quantiles([c["dist_to_pocket_centroid_A"] for c in cells]),
            "n_frames_open_at_or_below_gate": n_gate,
            "frac_frames_open_at_or_below_gate": round(n_gate / len(cells), 4) if cells else None,
            "frac_frames_open_at_or_below_gate_wilson95": wilson95(n_gate, len(cells)),
            "n_frames_never_open_within_20": len(ls) - len(opened),
            "shortest_linker_atoms": quantiles(opened),
            "min_exit_anchor_to_SG_A": quantiles([c["min_exit_anchor_to_SG_A"] for c in cells
                                                  if c.get("min_exit_anchor_to_SG_A") is not None]),
        }
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--mode", choices=["static", "ensembles", "all"], default="all")
    ap.add_argument("--terma", action="store_true", help="run only term (a)")
    ap.add_argument("--termb", action="store_true", help="run only term (b)")
    ap.add_argument("--samples", type=int, default=120000, help="rigid-body samples per (arm x pose) for term (b)")
    ap.add_argument("--n-poses", type=int, default=N_POSES)
    ap.add_argument("--n-mc", type=int, default=N_MC)
    ap.add_argument("--seed", type=int, default=SEED)
    ap.add_argument("--registry", default=NATIVE_REGISTRY)
    ap.add_argument("--limit", type=int, default=0, help="debug: cap frames per ensemble")
    ap.add_argument("--validate-coverage", action="store_true")
    ap.add_argument("--out", default=OUT)
    ap.add_argument("--allow-missing-ensembles", action="store_true",
                    help="proceed even when a species contributes ZERO conformers (see ensemble_census)")
    args = ap.parse_args(argv)
    do_a = args.terma or not args.termb
    do_b = args.termb or not args.terma

    t0 = time.time()
    census = ensemble_census()
    for sp, c in census["by_species"].items():
        print(f"[pdyn] ensemble census {sp}: {c['n_frames_total']} frames "
              f"({', '.join(f'{k}={v}' for k, v in c['by_subset'].items())})", flush=True)
    if args.mode in ("ensembles", "all") and census["species_with_no_frames"] and not args.allow_missing_ensembles:
        raise SystemExit(
            "[pdyn] REFUSING TO RUN — no conformers for " + ", ".join(census["species_with_no_frames"]) + ".\n"
            "  This lane's whole question is whether paralogue DYNAMICS open a compensating site. Running\n"
            "  --mode " + args.mode + " over an empty ensemble directory does not answer it: `frame_paths`\n"
            "  returns [] for a missing directory and the ensembles branch skips it, so the artifact would\n"
            "  come out full, green and STATIC-ONLY while carrying the dynamics label. Expected layout:\n"
            "  " + "\n  ".join(f"{sp}: {os.path.relpath(ENSEMBLE_ROOT[sp], REPO)}/<{'|'.join(s for s, _ in SUBSETS)}>/*/frame.pdb"
                               for sp in census["species_with_no_frames"]) + "\n"
            "  Run `nr4a_paralogue_md_ops.py collect` first, or pass --allow-missing-ensembles to override.")
    seqs = json.load(open(SEQ_CACHE))
    ref = B.load_paralogue(STATIC_MODEL["NR4A3"])
    ref_aa_of = ref["aa_of"]
    u = json.load(open(UNIQUE_JSON))
    ref_pocket_local = [x - B.UNIPROT_OFFSET for x in u["cryptic_pocket_uniprot"]]

    offsets, pocket_local_by_species, pocket_map_note = {}, {}, {}
    for sp in SPECIES:
        m = B.load_paralogue(STATIC_MODEL[sp])
        offsets[sp] = species_offset(m, sp, seqs)
        if sp == "NR4A3":
            pocket_local_by_species[sp] = list(ref_pocket_local)
            pocket_map_note[sp] = {"n_mapped": len(ref_pocket_local), "unmapped_nr4a3_local": []}
        else:
            got, missing = homologous_pocket(m, ref, ref_pocket_local)
            pocket_local_by_species[sp] = got
            pocket_map_note[sp] = {"n_mapped": len(got), "unmapped_nr4a3_local": missing,
                                   "uniprot": [r + offsets[sp] for r in got]}
        print(f"[pdyn] {sp}: local->UniProt offset {offsets[sp]}, homologous pocket "
              f"{pocket_map_note[sp]['n_mapped']}/{len(ref_pocket_local)} residues", flush=True)

    res = {
        "_title": "Does the CATEGORICAL case survive paralogue DYNAMICS? — matched NR4A1/NR4A2/NR4A3 ensembles",
        "_status": "DESIGN PRIORITISATION. Nothing here is a claim about binding, reactivity, degradation, "
                   "efficacy or safety.",
        "_question": [
            "(1) Does a paralogue present, in a populated conformer, ANY cysteine within tether range of the "
            "same linker paths — not only at the aligned position? A degrader does not care which cysteine "
            "it labels, so a cysteine elsewhere in the fold that becomes reachable is a compensating site.",
            "(2) Does a paralogue expose lysines inside the modelled E2~Ub transfer zone that make term (b) "
            "non-discriminating?",
        ],
        "_method": {
            "term_a": "E3-INDEPENDENT reach envelope (nr4a3_basin_search.term_a_feasibility_envelope), "
                      "recomputed per conformer on its OWN homologous cryptic pocket and its OWN "
                      "exit-vector pose ensemble at identical parameters, over EVERY cysteine with an SG.",
            "term_b": "ONE matched set of E3 placements sampled on the NR4A3 reference frame; every "
                      "conformer of every species superposed into that frame; coverage of the observed "
                      "E2 catalytic-cysteine transfer zone computed EXACTLY (sphere-sphere lens).",
            "rsa": "Identical Shrake-Rupley / Tien max-ASA routine that produced the committed single-frame "
                   "numbers.",
            "alignment": "BLOSUM62 Needleman-Wunsch, the same aligner nr4a3_metad uses to put the "
                         "metadynamics CV on the HOMOLOGOUS paralogue pocket.",
        },
        "_limits": [
            "Reach and exposure are NECESSARY, not sufficient: thiol pKa, nucleophilicity, adduct stability "
            "and electrophile promiscuity are untested here and untestable without chemoproteomics.",
            "The term-(a) envelope is an E3-INDEPENDENT UPPER BOUND. For THIS question that is the "
            "conservative direction — a paralogue cysteine closed in the envelope is closed for every "
            "recruiter — but a paralogue cysteine that is OPEN has not been shown reachable by a real one.",
            "Metadynamics frames are BIASED along the pocket-opening CV and are never pooled with the "
            "unbiased release frames; they are reported separately as an adversarial upper bound on how far "
            "each species' pocket can open.",
            "Every conformer is LBD-only, as every model in this program is.",
            "Superposition into the NR4A3 frame carries a real core-fit residual; per-lysine post-fit "
            "deviations are reported and NR4A3's own frames go through the identical superposition.",
        ],
        "parameters": {"n_poses": args.n_poses, "n_mc": args.n_mc, "seed": args.seed,
                       "term_b_samples_per_arm_pose": args.samples,
                       "linker_gate_atoms": B.PARAMS["linker_gate_atoms"],
                       "linker_report_atoms": B.PARAMS["linker_report_atoms"],
                       "electrophile_arm_A": B.PARAMS["electrophile_arm_A"]},
        "construct": {sp: {"local_to_uniprot_offset": offsets[sp],
                           "homologous_pocket": pocket_map_note[sp]} for sp in SPECIES},
    }

    if args.validate_coverage:
        res["coverage_validation"] = validate_coverage()
        print(f"[pdyn] coverage validation: max|MC-analytic| = "
              f"{res['coverage_validation']['max_abs_diff']} "
              f"({'PASS' if res['coverage_validation']['passes'] else 'FAIL'})", flush=True)

    # ---------------- inventory: which cysteines each species has, and where NR4A3 has none -------------
    inv = {}
    for sp in SPECIES:
        m = B.load_paralogue(STATIC_MODEL[sp])
        cys = cysteines_of(m, offsets[sp], ref, ref_aa_of)
        inv[sp] = [{"label": c["label"], "nr4a3_aligned": c["nr4a3_aligned"],
                    "nr4a3_has_cys_here": c["nr4a3_has_cys_here"]} for c in cys]
    res["ensemble_census"] = census
    res["cysteine_inventory"] = {
        "_reading": "A paralogue cysteine whose `nr4a3_has_cys_here` is false is a site NR4A3 does NOT have "
                    "— the reciprocal of the program's own categorical handle, and the exact failure mode "
                    "this lane exists to test. Sequence-level fact; whether it is REACHABLE is the "
                    "distribution below.",
        "by_species": inv,
    }

    # ---------------- term (a) -----------------------------------------------------------------------
    if do_a:
        res["term_a"] = {"_what": "reach of EVERY cysteine, per species, as a distribution over conformers",
                         "by_species": {}}
        for sp in SPECIES:
            ens = {}
            todo = []
            if args.mode in ("static", "all"):
                todo.append(("static_opened_model", [("static", STATIC_MODEL[sp])], False))
            if args.mode in ("ensembles", "all"):
                for sub, biased in SUBSETS:
                    fps = frame_paths(sp, sub)
                    if args.limit:
                        fps = fps[: args.limit]
                    if fps:
                        todo.append((sub, fps, biased))
            for name, fps, biased in todo:
                rows = []
                for i, (fid, path) in enumerate(fps):
                    rows.append(analyse_conformer_terma(path, sp, seqs, ref, ref_aa_of,
                                                        ref_pocket_local, args.seed + i,
                                                        n_poses=args.n_poses, n_mc=args.n_mc))
                    if (i % 10) == 0 or i == len(fps) - 1:
                        print(f"[pdyn][a] {sp} {name} {i + 1}/{len(fps)} {fid}: "
                              + " ".join(f"{k}(L={v.get('shortest_linker_atoms')})"
                                         for k, v in rows[-1]["cys"].items()), flush=True)
                ens[name] = {"biased": biased, "n_frames": len(rows),
                             "summary": summarise_terma(rows), "frames": rows}
            # pooled UNBIASED view — the one that is a population estimate
            unb = [n for n in ens if n.startswith("release_rep")]
            pooled = None
            if unb:
                allrows = [f for n in unb for f in ens[n]["frames"]]
                pooled = {"_what": "the unbiased release replicas pooled; metadynamics is excluded because "
                                   "it is biased along the pocket CV",
                          "n_replicas": len(unb), "n_frames": len(allrows),
                          "summary": summarise_terma(allrows)}
            res["term_a"]["by_species"][sp] = {"ensembles": ens, "pooled_unbiased": pooled}

    # ---------------- term (b) -----------------------------------------------------------------------
    if do_b:
        print(f"[pdyn][b] sampling matched E3 placements ({args.samples} x {args.n_poses} poses x arms)...",
              flush=True)
        anchors, per_arm, params_b, _poses = sample_transfer_anchors(
            ref, args.registry, args.samples, args.n_poses, args.seed)
        _side = []
        for _rid in ref_pocket_local:
            for _a in ref["atoms_by_res"].get(_rid, []):
                if _a["name"] not in B.BACKBONE:
                    _side.append((_a["x"], _a["y"], _a["z"]))
        ref_pocket_centroid = G.centroid(_side)
        print(f"[pdyn][b] {len(anchors)} accepted placements carry an observed transfer anchor: {per_arm}",
              flush=True)
        res["term_b"] = {
            "_what": "expected coverage of the observed E2~Ub transfer zone by each species' lysines, over "
                     "ONE matched placement set, as a distribution over conformers",
            "transfer_geometry": {"lysine_transfer_A": params_b["lysine_transfer_A"],
                                  "observed_anchor_mobility_A": params_b.get("observed_anchor_mobility_A"),
                                  "n_e2_samples": params_b["n_e2_samples"],
                                  "_source": "measured nearest substrate lysine in 9UUM (17.09 A); the "
                                             "repo's former 10 A assumption was ~7 A too strict"},
            "placements": {"n_total": len(anchors), "by_arm": per_arm,
                           "registry": os.path.basename(args.registry)},
            "by_species": {},
        }
        if not anchors:
            print("[pdyn][b] WARNING: no accepted placements — term (b) skipped", flush=True)
        # per-placement 0/1 hit vectors, accumulated per species so the CATEGORICAL joint statistic can be
        # computed exactly under conformational independence (the three molecules' trajectories ARE
        # independent, so this is not an approximation of the pairing — it is the pairing)
        joint = {sp: [] for sp in SPECIES}
        for sp in SPECIES:
            ens = {}
            todo = []
            if args.mode in ("static", "all"):
                todo.append(("static_opened_model", [("static", STATIC_MODEL[sp])], False))
            if args.mode in ("ensembles", "all"):
                for sub, biased in SUBSETS:
                    fps = frame_paths(sp, sub)
                    if args.limit:
                        fps = fps[: args.limit]
                    if fps:
                        todo.append((sub, fps, biased))
            for name, fps, biased in todo:
                rows = []
                for i, (fid, path) in enumerate(fps):
                    _m = B.load_paralogue(path)
                    off_i, pocket_i, _miss = construct_frame(_m, sp, seqs, ref, ref_pocket_local)
                    lys, sup = species_lysines_in_ref_frame(path, ref, off_i, model=_m)
                    cov = coverage_over_anchors(anchors, lys, params_b) if anchors else None
                    # --- MATCHED term (a) on the SAME placements, in the SAME frame -------------------
                    cys_rf, sup2 = species_cysteines_in_ref_frame(
                        path, ref, off_i, ref_aa_of,
                        pocket_local=pocket_i, ref_pocket_centroid=ref_pocket_centroid)
                    m_all = matched_reach_hits_multi(anchors, cys_rf, LENGTHS, params=params_b)
                    m_exp_all = matched_reach_hits_multi(anchors, cys_rf, LENGTHS, params=params_b,
                                                         min_rsa=EXPOSED_RSA)
                    npl = max(1, len(anchors))
                    gate = B.PARAMS["linker_gate_atoms"]
                    matched = {
                        "P_any_cysteine_at_gate": round(sum(m_all[gate][0]) / npl, 5),
                        "P_any_EXPOSED_cysteine_at_gate": round(sum(m_exp_all[gate][0]) / npl, 5),
                        "P_any_cysteine_by_linker_atoms": {n: round(sum(m_all[n][0]) / npl, 5)
                                                           for n in LENGTHS},
                        "P_any_EXPOSED_cysteine_by_linker_atoms": {n: round(sum(m_exp_all[n][0]) / npl, 5)
                                                                   for n in LENGTHS},
                        "per_cysteine": {k: round(v / npl, 5) for k, v in
                                         sorted(m_all[gate][1].items(), key=lambda kv: -kv[1]) if v},
                        "per_cysteine_at_20": {k: round(v / npl, 5) for k, v in
                                               sorted(m_all[20][1].items(), key=lambda kv: -kv[1]) if v},
                    }
                    entry = {"any": {n: m_all[n][0] for n in LENGTHS},
                             "exposed": {n: m_exp_all[n][0] for n in LENGTHS},
                             "ensemble": name, "biased": biased, "frame": fid}
                    if sp == "NR4A3":
                        uc = [c for c in cys_rf if c["uniprot_resid"] in NR4A3_UNIQUE_CYS]
                        u_all = matched_reach_hits_multi(anchors, uc, LENGTHS, params=params_b)
                        u_exp = matched_reach_hits_multi(anchors, uc, LENGTHS, params=params_b,
                                                         min_rsa=EXPOSED_RSA)
                        matched["P_unique_cysteine_at_gate"] = round(sum(u_all[gate][0]) / npl, 5)
                        matched["P_unique_EXPOSED_cysteine_at_gate"] = round(sum(u_exp[gate][0]) / npl, 5)
                        matched["P_unique_cysteine_by_linker_atoms"] = {n: round(sum(u_all[n][0]) / npl, 5)
                                                                        for n in LENGTHS}
                        entry["unique_any"] = {n: u_all[n][0] for n in LENGTHS}
                        entry["unique_exposed"] = {n: u_exp[n][0] for n in LENGTHS}
                    joint[sp].append(entry)
                    rows.append({"frame": fid, "n_lysines": len(lys),
                                 "n_exposed_lysines": sum(1 for k in lys if k["rsa"] >= 0.25),
                                 "n_cysteines": len(cys_rf),
                                 "superposition_core_rmsd_A": sup["core_rmsd_A"],
                                 "superposition_core_fraction": sup["core_fraction"],
                                 "homologous_pocket_centroid_offset_A":
                                     sup2.get("homologous_pocket_centroid_offset_A"),
                                 "coverage": cov,
                                 "matched_term_a": matched,
                                 "unreliably_placed_covered": sorted(
                                     k["label"] for k in lys
                                     if not k["position_reliable"] and cov
                                     and cov["per_lysine_mean_coverage"].get(k["label"], 0) > 0.01)})
                    if (i % 10) == 0 or i == len(fps) - 1:
                        print(f"[pdyn][b] {sp} {name} {i + 1}/{len(fps)} {fid}: "
                              f"P(lys any)={cov['P_zone_covers_any_lysine'] if cov else None} "
                              f"P(cys@gate)={matched['P_any_cysteine_at_gate']} "
                              f"P(exposed cys@gate)={matched['P_any_EXPOSED_cysteine_at_gate']}",
                              flush=True)
                per_lys_pool = {}
                for r in rows:
                    for k, v in ((r["coverage"] or {}).get("per_lysine_mean_coverage") or {}).items():
                        per_lys_pool.setdefault(k, []).append(v)
                ens[name] = {
                    "biased": biased, "n_frames": len(rows),
                    "P_zone_covers_any_lysine": quantiles(
                        [r["coverage"]["P_zone_covers_any_lysine"] for r in rows if r["coverage"]]),
                    "P_zone_covers_any_EXPOSED_lysine": quantiles(
                        [r["coverage"]["P_zone_covers_any_EXPOSED_lysine"] for r in rows if r["coverage"]]),
                    "per_lysine": {k: quantiles(v) for k, v in
                                   sorted(per_lys_pool.items(), key=lambda kv: -sum(kv[1]))},
                    "superposition_core_rmsd_A": quantiles([r["superposition_core_rmsd_A"] for r in rows]),
                    "homologous_pocket_centroid_offset_A": quantiles(
                        [r["homologous_pocket_centroid_offset_A"] for r in rows
                         if r.get("homologous_pocket_centroid_offset_A") is not None]),
                    "matched_term_a": {
                        "P_any_cysteine_at_gate": quantiles(
                            [r["matched_term_a"]["P_any_cysteine_at_gate"] for r in rows]),
                        "P_any_EXPOSED_cysteine_at_gate": quantiles(
                            [r["matched_term_a"]["P_any_EXPOSED_cysteine_at_gate"] for r in rows]),
                        "P_unique_cysteine_at_gate": quantiles(
                            [r["matched_term_a"]["P_unique_cysteine_at_gate"] for r in rows
                             if "P_unique_cysteine_at_gate" in r["matched_term_a"]]),
                        "per_cysteine": {k: quantiles(v) for k, v in sorted(
                            _pool_per_cys(rows).items(), key=lambda kv: -sum(kv[1]))},
                    },
                    "frames": rows,
                }
            unb = [n for n in ens if n.startswith("release_rep")]
            pooled = None
            if unb:
                allrows = [f for n in unb for f in ens[n]["frames"]]
                pooled = {"n_replicas": len(unb), "n_frames": len(allrows),
                          "P_zone_covers_any_lysine": quantiles(
                              [r["coverage"]["P_zone_covers_any_lysine"] for r in allrows if r["coverage"]]),
                          "P_zone_covers_any_EXPOSED_lysine": quantiles(
                              [r["coverage"]["P_zone_covers_any_EXPOSED_lysine"] for r in allrows
                               if r["coverage"]])}
            res["term_b"]["by_species"][sp] = {"ensembles": ens, "pooled_unbiased": pooled}

        # ------------- THE CATEGORICAL VERDICT --------------------------------------------------------
        res["categorical_verdict"] = categorical_verdict(anchors, joint)
        cv = res["categorical_verdict"]
        for scope, d in cv["by_scope"].items():
            if d.get("VERDICT_NOT_EVALUABLE"):
                print(f"[pdyn][V] {scope}: NOT EVALUABLE — {d['VERDICT_NOT_EVALUABLE']}", flush=True)
                continue
            print(f"[pdyn][V] {scope}: P(paralogue Cys also at gate | NR4A3 unique Cys at gate) = "
                  f"{d['P_paralogue_also_labelled_given_nr4a3']} "
                  f"(exposed-only {d['P_paralogue_also_labelled_given_nr4a3_EXPOSED']})", flush=True)

    res["runtime_s"] = round(time.time() - t0, 1)
    with open(args.out, "w") as fh:
        json.dump(res, fh, indent=1)
    print(f"[pdyn] wrote {args.out} in {res['runtime_s']} s", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
