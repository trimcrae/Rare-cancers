#!/usr/bin/env python3
"""Do the independent methods that placed denovo_401 in NR4A3 AGREE with each other? ($0 CPU)

★★ WHY THIS EXISTS. Everything downstream of the lead — the ternary, the selectivity argument, the ABFE
work — is anchored to ONE predicted pose of `denovo_401` in the NR4A3 ligand-binding domain. There is no
experimental answer for that pose and there will not be one without a wet lab. In the absence of a truth,
the only evidence available is **CONVERGENCE of methods that fail differently**: if a smina dock into a
metadynamics-opened AF2 frame and a smina dock into an experimental apo NMR conformer land the ligand in
the same place in the same orientation, that agreement is weak but real evidence; if they do not, the
"the pose" language everywhere downstream is describing something that does not exist.

⛔ WHAT AGREEMENT DOES AND DOES NOT LICENSE.
  · Convergence is **NOT** correctness. Two runs of the same scoring function on two conformers of the
    same protein share every systematic error the function has. They can agree and both be wrong.
  · Divergence, however, is nearly conclusive in the other direction: methods that disagree cannot all be
    right, so a wide spread **retires** the singular "the predicted pose" and replaces it with an ensemble
    whose width has to be carried into everything built on it.
  · So this module reports a SPREAD, never a representative pose, and never a verdict of the form
    "the pose is correct". The known-answer half of the question lives in `apo_pose_recovery.py`.

★ CORRESPONDENCE IS CHEMICAL, NEVER BY PROXIMITY. Two copies of denovo_401 are matched atom-to-atom
through the molecular GRAPH (RDKit `rdMolAlign.CalcRMS`, which enumerates the molecule's automorphisms and
takes the minimum), not by nearest neighbour. The reason is documented at length in
`selcal_cofold_decompose.py`: a distance-based correspondence reports a small deviation for a molecule
that is flipped end-for-end or sitting in the wrong pocket, which is exactly the failure being tested for.
denovo_401 carries a mono-substituted phenyl (2-fold flip) and a gem-dimethyl (methyl swap), so a
symmetry-blind RMSD would also over-report deviation for poses that are chemically identical.

★ AND THE COMPARISON IS IN A COMMON RECEPTOR FRAME. Each pose was produced in its own receptor's
coordinate frame — different metadynamics frames, different NMR models — so the ligand coordinates are not
comparable as deposited. Every receptor is first mapped onto **UniProt Q92570 numbering** (the repo's own
`residue_map.resolve_positions`, the same kernel the docking pipeline uses to place its box) and then
superposed onto a common reference by Ca Kabsch (`nr4a3_8xtt_benchmark.kabsch_transform`, the repo's own
superposition, so "superposed" means here what it means in the 8XTT benchmark). Two fits are reported:
  · **global** — every Ca in common. Answers "is it the same site on the domain?"
  · **pocket-local** — Ca of the Pocket-5 lining residues only (`nr4a3_8xtt_benchmark.POCKET5`, a
    receptor-derived definition that predates and is independent of any pose). Answers "is it the same
    pose in the pocket?", without letting distant-loop motion of a flexible LBD inflate the number.
  A global fit alone is the wrong instrument here and would flatter nothing: it is the pocket-local
  number that a medicinal chemist would read.

⚠ AN INPUT WE COULD NOT READ IS **UNREAD, NOT ABSENT.** Every pose the program is known to hold is listed
in `SOURCES` whether or not its file is reachable, and a source whose coordinates cannot be loaded is
emitted in `refusals` with the evidence (the path tried, and what the filesystem said). A convergence
number computed over the subset that happened to be on disk, with the rest silently dropped, would be a
measurement of which files survived an S3 lifecycle rule.

Output: pose-convergence-401.json. No GPU, no network, no rental.
"""
from __future__ import annotations

import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(HERE, "pose-convergence-401.json")

#: The carried lead. One home for the identity: the SMILES is read from the module that owns the pose it
#: was scored in, so a silent divergence between "the lead here" and "the lead there" is impossible.
LIGAND_LABEL = "denovo_401"

#: Receptor heavy-atom / ligand heavy-atom separation counted as a contact. Not a fresh number: it is the
#: default of `nr4a3_warhead.handle_contacts`, the pipeline's OWN contact distance, read from that
#: function's signature so the two can never drift apart.
def contact_a():
    import inspect
    import nr4a3_warhead as wh
    return float(inspect.signature(wh.handle_contacts).parameters["cutoff"].default)


#: Directory of extra pose files fetched from object storage by CI (8XTT re-dock legs live only in S3).
#: Absent locally, which is why every source states where it expects to find itself.
EXTRA_DIR = os.environ.get("EXTRA_POSE_DIR", os.path.join(HERE, "_pose_convergence_inputs"))


# ==================================================================================================
# THE CENSUS — every denovo_401-in-NR4A3 pose this program is known to hold.
# ==================================================================================================
# A source is listed whether or not it is readable, and carries TWO labels that must not be conflated:
#   `kind`                 — the pose-GENERATION method. The whole premise of a convergence argument is
#                            that the methods fail differently, so two rows with the same `kind` are one
#                            method run twice however different their receptors are.
#   `receptor_provenance`  — where the receptor conformation came from (a metadynamics frame of an AF2
#                            prediction, or a deposited apo NMR model). A real and useful axis — an
#                            experimental receptor removes the AF2 model as a shared failure — but it is
#                            NOT method orthogonality and is reported separately so it cannot be read as
#                            such.
# ⚠ Every source in this census is the SAME `kind`. That is itself the finding of Deliverable A: this
# program has only ever placed denovo_401 with one pose-generation method, so there is no cross-method
# convergence to measure, only cross-conformer reproducibility.

def _r(*parts):
    return os.path.join(REPO, *parts)


def _x(*parts):
    return os.path.join(EXTRA_DIR, *parts)


SOURCES = [
    {
        "id": "dock/metad-opened/v2",
        "kind": "smina dock, top pose (nr4a3_warhead.dock_into)",
        "receptor_provenance": "metadynamics-OPENED AF2 prediction",
        "receptor": _r("results", "nr4a3-denovo", "-matrix-v2", "nr4a3-opened.pdb"),
        "poses": _r("results", "nr4a3-denovo", "-matrix-v2", "docked_nr4a3.sdf"),
        "numbering": "renumbered-from-373",
        "provenance": "nr4a3_matrix.py de-novo funnel run, S3 prefix nr4a3-denovo-matrix-v2, archived to "
                      "git by archive_results.py. This is the frame the published selectivity matrix was "
                      "scored in.",
    },
    {
        "id": "dock/metad-opened/v2-statematch",
        "kind": "smina dock, top pose (nr4a3_warhead.dock_into)",
        "receptor_provenance": "metadynamics-OPENED AF2 prediction",
        "receptor": _r("results", "nr4a3-denovo", "-matrix-v2-statematch", "nr4a3-opened.pdb"),
        "poses": _r("results", "nr4a3-denovo", "-matrix-v2-statematch", "docked_nr4a3.sdf"),
        "numbering": "renumbered-from-373",
        "provenance": "nr4a3_matrix.py state-matched run (a DIFFERENT opened conformer extracted from the "
                      "metadynamics trajectory), S3 prefix nr4a3-denovo-matrix-v2-statematch.",
    },
    # ---- the four experimental-geometry legs. S3-only: results/nr4a3-8xtt-redock/MANIFEST.json records
    # them as action="scratch", i.e. they were never mirrored into git. CI fetches them into EXTRA_DIR.
    {
        "id": "dock/8XTT-model2",
        "kind": "smina dock, top pose (nr4a3_warhead.dock_into)",
        "receptor_provenance": "EXPERIMENTAL apo NMR conformer (8XTT model 2)",
        "receptor": _x("8xtt_model2_nr4a3.pdb"),
        "poses": _x("docked_nr4a3_m2.sdf"),
        "numbering": "8XTT-author",
        "provenance": "nr4a3_8xtt_redock.py, S3 nr4a3-8xtt-redock/redock_work/. Scored -34.21 kcal/mol "
                      "MM-GBSA in nr4a3-8xtt-redock-denovo401.json (model 2).",
    },
    {
        "id": "dock/8XTT-model8",
        "kind": "smina dock, top pose (nr4a3_warhead.dock_into)",
        "receptor_provenance": "EXPERIMENTAL apo NMR conformer (8XTT model 8)",
        "receptor": _x("8xtt_model8_nr4a3.pdb"),
        "poses": _x("docked_nr4a3_m8.sdf"),
        "numbering": "8XTT-author",
        "provenance": "nr4a3_8xtt_redock.py, S3 nr4a3-8xtt-redock/redock_work/.",
    },
    {
        "id": "dock/8XTT-model20",
        "kind": "smina dock, top pose (nr4a3_warhead.dock_into)",
        "receptor_provenance": "EXPERIMENTAL apo NMR conformer (8XTT model 20)",
        "receptor": _x("8xtt_model20_nr4a3.pdb"),
        "poses": _x("docked_nr4a3_m20.sdf"),
        "numbering": "8XTT-author",
        "provenance": "nr4a3_8xtt_redock.py, S3 nr4a3-8xtt-redock/redock_work/.",
    },
    {
        "id": "dock/8XTT-model6",
        "kind": "smina dock, top pose (nr4a3_warhead.dock_into)",
        "receptor_provenance": "EXPERIMENTAL apo NMR conformer (8XTT model 6)",
        "receptor": _x("8xtt_model6_nr4a3.pdb"),
        "poses": _x("docked_nr4a3_m6.sdf"),
        "numbering": "8XTT-author",
        "provenance": "nr4a3_8xtt_redock.py, S3 nr4a3-8xtt-redock/redock_work/.",
    },
]

#: Pose sources the program does NOT hold, recorded so the census cannot be mistaken for exhaustive.
#: A named absence is a finding; an unnamed one is an omission.
KNOWN_ABSENT = [
    {
        "id": "cofold/binary-Boltz2",
        "why": "nr4a3-binary-cofold-result.json carries CONFIDENCE SCORES ONLY (ligand_iptm, "
               "protein_ligand_pair_iptm, complex_iplddt) and no coordinates. The predicted structure was "
               "never committed, so the co-fold cannot enter a geometric comparison from this repo. Its "
               "own numbers already say the placement is low-confidence (protein_ligand_pair_iptm 0.233 "
               "for NR4A3), which is a reason to want it in this comparison, not a reason to skip it.",
    },
    {
        "id": "dock/original-nr4a3-matrix",
        "why": "results/PROVENANCE.md records S3 prefix `nr4a3-matrix` (the ORIGINAL docking-matrix poses "
               "behind denovo_401's selection) as LOST to the bucket lifecycle rule. The archived "
               "results/nr4a3-matrix/ holds the 13-compound repurposing library, NOT denovo_401.",
    },
]


# ==================================================================================================
# PURE GEOMETRY — no rdkit, no network. Unit-tested in tests/test_pose_convergence_401.py.
# ==================================================================================================

def parse_receptor(pdb_path):
    """{resseq: {"resname": str, "ca": (x,y,z), "heavy": [(x,y,z), ...]}} for the protein chain.

    Reads ATOM records only (HETATM is solvent/ion here and never part of the receptor frame), keeps the
    FIRST chain encountered so a multi-chain file cannot silently mix two copies, and drops hydrogens by
    element/name so "heavy atom" means the same thing on a file that has them and one that does not."""
    out = {}
    order = []
    chain = None
    for line in open(pdb_path, errors="replace"):
        if not line.startswith("ATOM"):
            if line.startswith("ENDMDL"):
                break                     # an NMR file: first model only, never an average of models
            continue
        cid = line[21]
        if chain is None:
            chain = cid
        elif cid != chain:
            continue
        name = line[12:16].strip()
        elem = (line[76:78].strip() or name[:1]).upper()
        if elem == "H" or name.startswith("H"):
            continue
        try:
            resseq = int(line[22:26])
        except ValueError:
            continue
        xyz = (float(line[30:38]), float(line[38:46]), float(line[46:54]))
        rec = out.get(resseq)
        if rec is None:
            rec = out[resseq] = {"resname": line[17:20].strip(), "ca": None, "heavy": []}
            order.append(resseq)
        rec["heavy"].append(xyz)
        if name == "CA":
            rec["ca"] = xyz
    return out, order


AA3 = {"ALA": "A", "ARG": "R", "ASN": "N", "ASP": "D", "CYS": "C", "GLN": "Q", "GLU": "E", "GLY": "G",
       "HIS": "H", "ILE": "I", "LEU": "L", "LYS": "K", "MET": "M", "PHE": "F", "PRO": "P", "SER": "S",
       "THR": "T", "TRP": "W", "TYR": "Y", "VAL": "V", "HID": "H", "HIE": "H", "HIP": "H", "CYX": "C"}


def to_uniprot(residues, order, numbering, lbd_first=None):
    """Re-key a receptor's residues into UniProt Q92570 numbering, or (None, why).

    Two schemes appear in this program and BOTH are handled by the repo's own kernel rather than by an
    offset typed here:
      · `renumbered-from-373` — the metadynamics/MD receptors, trimmed contiguously from the LBD start and
        renumbered from 1. `residue_map.resolve_positions` is the one home of that convention.
      · `8XTT-author`         — the deposited NMR entry's own author numbering, which is NOT the UniProt
        numbering and is mapped by sequence, never by arithmetic (`nr4a3_8xtt_benchmark.map_uniprot_to_pdb`
        against the AF2 reference), because a deposit is free to number its construct however it likes.
    """
    import nr4a3_matrix as mx
    import residue_map as rm
    lbd_first = mx.LBD_FIRST_NR4A3 if lbd_first is None else lbd_first
    if numbering == "renumbered-from-373":
        span = list(range(lbd_first, lbd_first + len(order)))
        pos, how = rm.resolve_positions(order, span, lbd_first)
        if not pos:
            return None, "residue_map resolved no positions (%s)" % how
        return {span[i]: residues[order[i]] for i in pos if i < len(span)}, how
    if numbering == "8XTT-author":
        mapped, how = _map_8xtt(residues, order)
        return mapped, how
    return None, "unknown numbering scheme %r" % numbering


def _map_8xtt(residues, order):
    """UniProt->author map for a deposited 8XTT model, via the repo's own alignment (needs biopython)."""
    import nr4a3_8xtt_benchmark as bm
    ref = os.environ.get("AF2_REFERENCE_PDB", "")
    if not ref or not os.path.exists(ref):
        for cand in (os.path.join(EXTRA_DIR, "AF-Q92570.pdb"),
                     os.path.join(REPO, "results", "nr4a3-metad-r2", "ckpt", "AF-Q92570.pdb")):
            if os.path.exists(cand):
                ref = cand
                break
    if not ref or not os.path.exists(ref):
        return None, "no AF-Q92570 reference on disk — UniProt<->8XTT map needs it (set AF2_REFERENCE_PDB)"
    try:
        _ca, af2_resnums, af2_seq = bm.af2_lbd_ca(ref)
        pdb_seq = "".join(AA3.get(residues[r]["resname"], "X") for r in order)
        uni_to_auth, ident = bm.map_uniprot_to_pdb(af2_seq, af2_resnums, pdb_seq, list(order))
    except Exception as e:                                   # noqa: BLE001 — a refusal, with its reason
        return None, "8XTT alignment failed: %s: %s" % (type(e).__name__, e)
    if not uni_to_auth:
        return None, "8XTT alignment produced an empty map"
    return ({u: residues[a] for u, a in uni_to_auth.items() if a in residues},
            "sequence-aligned to AF-Q92570 (identity %.3f)" % ident)


def superpose(mobile_u, ref_u, fit_residues):
    """Rigid transform putting `mobile_u` on `ref_u` over the Ca of `fit_residues` present in both.

    Returns (R, t, n_fit, fit_rmsd) or raises. Kernel is the repo's own quaternion Kabsch."""
    import nr4a3_8xtt_benchmark as bm
    common = sorted(r for r in fit_residues
                    if r in mobile_u and r in ref_u
                    and mobile_u[r]["ca"] is not None and ref_u[r]["ca"] is not None)
    if len(common) < 3:
        raise ValueError("only %d common Ca to superpose on (need >= 3)" % len(common))
    mob = [mobile_u[r]["ca"] for r in common]
    tgt = [ref_u[r]["ca"] for r in common]
    R, t = bm.kabsch_transform(mob, tgt)
    return R, t, len(common), bm.rmsd(bm.apply_transform(mob, R, t), tgt)


def apply_to_points(points, R, t):
    import nr4a3_8xtt_benchmark as bm
    return bm.apply_transform([tuple(p) for p in points], R, t)


def centroid(points):
    n = float(len(points))
    return tuple(sum(p[i] for p in points) / n for i in range(3))


def contacts(ligand_xyz, residues_u, cutoff):
    """{uniprot_resnum} whose receptor heavy atoms come within `cutoff` of any ligand heavy atom."""
    c2 = cutoff * cutoff
    hit = set()
    for r, rec in residues_u.items():
        for (ax, ay, az) in rec["heavy"]:
            for (bx, by, bz) in ligand_xyz:
                if (ax - bx) ** 2 + (ay - by) ** 2 + (az - bz) ** 2 <= c2:
                    hit.add(r)
                    break
            else:
                continue
            break
    return hit


def jaccard(a, b):
    if not a and not b:
        return None
    u = len(a | b)
    return round(len(a & b) / u, 4) if u else None


def spread(values):
    """min / median / max / mean of a list, or None-filled if empty. NEVER a single 'representative'."""
    vals = sorted(v for v in values if v is not None)
    if not vals:
        return {"n": 0, "min": None, "median": None, "max": None, "mean": None}
    n = len(vals)
    med = vals[n // 2] if n % 2 else 0.5 * (vals[n // 2 - 1] + vals[n // 2])
    return {"n": n, "min": round(vals[0], 3), "median": round(med, 3), "max": round(vals[-1], 3),
            "mean": round(sum(vals) / n, 3)}


# ==================================================================================================
# LIGAND CORRESPONDENCE — chemical, symmetry-aware.
# ==================================================================================================

def load_pose(sdf_path, label=LIGAND_LABEL):
    """The single molecule named `label` from a (multi-molecule) SDF, or (None, why)."""
    from rdkit import Chem
    if not os.path.exists(sdf_path):
        return None, "file not present: %s" % sdf_path
    try:
        supp = Chem.SDMolSupplier(sdf_path, removeHs=True, sanitize=True)
        for m in supp:
            if m is None:
                continue
            if m.GetProp("_Name").strip() == label:
                return m, None
    except Exception as e:                                   # noqa: BLE001
        return None, "%s: %s" % (type(e).__name__, e)
    return None, "no molecule named %r in %s" % (label, os.path.basename(sdf_path))


def transformed_copy(mol, R, t):
    """A copy of `mol` with its conformer rigidly moved by (R, t)."""
    from rdkit import Chem
    from rdkit.Geometry import Point3D
    out = Chem.Mol(mol)
    conf = out.GetConformer()
    pts = [(conf.GetAtomPosition(i).x, conf.GetAtomPosition(i).y, conf.GetAtomPosition(i).z)
           for i in range(out.GetNumAtoms())]
    for i, (x, y, z) in enumerate(apply_to_points(pts, R, t)):
        conf.SetAtomPosition(i, Point3D(x, y, z))
    return out


def symmetry_rmsd(mol_a, mol_b):
    """Symmetry-corrected heavy-atom RMSD **without re-aligning** the two molecules, or (None, why).

    `rdMolAlign.CalcRMS` is the right primitive and `GetBestRMS` is the wrong one: GetBestRMS would
    superpose the two ligands onto each other first, which throws away the very thing being measured
    (their placement in a common receptor frame) and would report ~0 for two poses in different pockets.
    Verified, not assumed — `tests/test_pose_convergence_401.py` translates a copy by a known 10 A and
    requires CalcRMS to return 10.0 while GetBestRMS returns 0.0."""
    from rdkit.Chem import rdMolAlign
    try:
        return round(float(rdMolAlign.CalcRMS(mol_a, mol_b)), 3), None
    except Exception as e:                                   # noqa: BLE001
        return None, "%s: %s" % (type(e).__name__, e)


def internal_conformer_rmsd(mol_a, mol_b):
    """How much of a disagreement is the ligand's OWN shape rather than where it was put, or (None, why).

    `GetBestRMS` superposes the two ligand copies onto each other and is therefore blind to placement —
    which makes it useless as the headline number and exactly right as the DECOMPOSITION of one:
      · internal ~= 0 with a large in-frame RMSD  -> the same conformer, placed differently (a flip, a
        translation along the channel, a different sub-site). The docking SEARCH disagreed.
      · internal comparable to the in-frame RMSD  -> the two runs did not even converge on the same
        molecular shape, so conformer generation is in play as well as placement.
    Reported for both, so a reader is never asked to take the split on trust."""
    from rdkit import Chem
    from rdkit.Chem import rdMolAlign
    try:
        return round(float(rdMolAlign.GetBestRMS(Chem.Mol(mol_a), Chem.Mol(mol_b))), 3), None
    except Exception as e:                                   # noqa: BLE001
        return None, "%s: %s" % (type(e).__name__, e)


def pose_score(mol):
    """The docking score smina wrote onto the pose, when present. Not re-derived here."""
    for prop in ("minimizedAffinity", "CNNaffinity", "affinity"):
        if mol.HasProp(prop):
            try:
                return float(mol.GetProp(prop))
            except ValueError:
                return None
    return None


def scale_reference(mol, n_random=200, seed=20260802):
    """What does an RMSD of N Angstrom MEAN for this molecule? Three reference scales, measured.

    A bare "7.0 A" is uninterpretable without knowing how big the molecule is, and picking a verbal label
    for it would be exactly the tuning the known-answer module forbids. So the artifact carries the scales
    a reader can calibrate against, all computed from the pose itself:
      · `length_A`          — the largest heavy-atom separation in the molecule. An RMSD approaching this
                              means the two poses share little more than a neighbourhood.
      · `flip_rmsd_A`       — the pose against a 180 deg rotation of itself ABOUT ITS OWN CENTROID. The
                              canonical "right place, backwards" failure; nothing has moved, only turned.
      · `random_reorient_A` — mean RMSD against uniformly random reorientations in place. The ceiling for
                              "same location, orientation carries no information".
    ⛔ None of these is a threshold and none gates anything."""
    import math as _m
    import random
    from rdkit.Chem import rdMolAlign
    pts = heavy_coords(mol)
    length = max(_m.dist(a, b) for a in pts for b in pts) if len(pts) > 1 else 0.0
    c = centroid(pts)

    def _rotated(R):
        t = tuple(c[i] - sum(R[i][j] * c[j] for j in range(3)) for i in range(3))
        return transformed_copy(mol, R, t)

    flip = rdMolAlign.CalcRMS(_rotated([[-1, 0, 0], [0, -1, 0], [0, 0, 1]]), mol)
    rng = random.Random(seed)
    vals = []
    for _ in range(n_random):
        u1, u2, u3 = rng.random(), rng.random(), rng.random()
        x, y, z, w = (_m.sqrt(1 - u1) * _m.sin(2 * _m.pi * u2), _m.sqrt(1 - u1) * _m.cos(2 * _m.pi * u2),
                      _m.sqrt(u1) * _m.sin(2 * _m.pi * u3), _m.sqrt(u1) * _m.cos(2 * _m.pi * u3))
        R = [[1 - 2 * (y * y + z * z), 2 * (x * y - w * z), 2 * (x * z + w * y)],
             [2 * (x * y + w * z), 1 - 2 * (x * x + z * z), 2 * (y * z - w * x)],
             [2 * (x * z - w * y), 2 * (y * z + w * x), 1 - 2 * (x * x + y * y)]]
        vals.append(float(rdMolAlign.CalcRMS(_rotated(R), mol)))
    return {"length_A": round(length, 2), "flip_rmsd_A": round(float(flip), 2),
            "random_reorient_mean_A": round(sum(vals) / len(vals), 2) if vals else None,
            "n_random": len(vals),
            "_note": "reference scales for reading the RMSD spread; none of these is a threshold"}


def heavy_coords(mol):
    conf = mol.GetConformer()
    return [(conf.GetAtomPosition(i).x, conf.GetAtomPosition(i).y, conf.GetAtomPosition(i).z)
            for i, a in enumerate(mol.GetAtoms()) if a.GetAtomicNum() > 1]


# ==================================================================================================
# THE MEASUREMENT
# ==================================================================================================

def load_source(src):
    """(record, refusal). A source is only usable when BOTH its receptor and its pose load."""
    rec_path, sdf_path = src["receptor"], src["poses"]
    if not os.path.exists(rec_path):
        return None, {"id": src["id"], "stage": "receptor", "path": rec_path,
                      "evidence": "os.path.exists -> False", "kind": src["kind"],
                      "provenance": src["provenance"]}
    residues, order = parse_receptor(rec_path)
    if not residues:
        return None, {"id": src["id"], "stage": "receptor", "path": rec_path,
                      "evidence": "parsed 0 protein residues from the file", "kind": src["kind"]}
    mapped, how = to_uniprot(residues, order, src["numbering"])
    if mapped is None:
        return None, {"id": src["id"], "stage": "numbering", "path": rec_path, "evidence": how,
                      "kind": src["kind"]}
    mol, why = load_pose(sdf_path)
    if mol is None:
        return None, {"id": src["id"], "stage": "pose", "path": sdf_path, "evidence": why,
                      "kind": src["kind"], "provenance": src["provenance"]}
    return {"id": src["id"], "kind": src["kind"], "provenance": src["provenance"],
            "receptor_provenance": src.get("receptor_provenance"),
            "receptor": os.path.relpath(rec_path, REPO) if rec_path.startswith(REPO) else rec_path,
            "poses": os.path.relpath(sdf_path, REPO) if sdf_path.startswith(REPO) else sdf_path,
            "n_residues_mapped": len(mapped), "numbering_resolved_by": how,
            "docking_score_kcalmol": pose_score(mol),
            "residues": mapped, "mol": mol,
            "smiles": _canonical(mol)}, None


def _canonical(mol):
    from rdkit import Chem
    try:
        return Chem.MolToSmiles(Chem.RemoveHs(mol))
    except Exception:                                        # noqa: BLE001
        return None


def measure(sources=None):
    """The full convergence readout. Returns the artifact dict."""
    import nr4a3_8xtt_benchmark as bm
    sources = SOURCES if sources is None else sources
    cutoff = contact_a()
    loaded, refusals = [], []
    for src in sources:
        rec, ref = load_source(src)
        (loaded if rec else refusals).append(rec or ref)

    doc = {
        "_question": "Do the independent methods that placed denovo_401 in the NR4A3 LBD agree with each "
                     "other? Convergence is not correctness; divergence is close to conclusive.",
        "_ligand": LIGAND_LABEL,
        "_contact_A": cutoff,
        "_fits": {"global": "every Ca in common between the two receptors, in UniProt Q92570 numbering",
                  "pocket": "Ca of nr4a3_8xtt_benchmark.POCKET5 only — a receptor-derived, pose-independent "
                            "definition of the orthosteric site"},
        "sources_considered": [{"id": s["id"], "kind": s["kind"],
                                "receptor_provenance": s.get("receptor_provenance")} for s in sources],
        "known_absent": KNOWN_ABSENT,
        "refusals": refusals,
        "usable": [{k: v for k, v in r.items() if k not in ("residues", "mol")} for r in loaded],
        "n_usable": len(loaded),
    }
    if len(loaded) < 2:
        doc["_status"] = "INSUFFICIENT — a convergence measurement needs at least two readable poses"
        doc["verdict"] = {
            "convergence_measurable": False,
            "sentence": "Only %d of %d known denovo_401-in-NR4A3 pose sources could be read, so the "
                        "program cannot currently demonstrate that ANY two independent methods agree on "
                        "the pose everything downstream is anchored to. That is a statement about the "
                        "evidence, not about the pose." % (len(loaded), len(sources)),
        }
        return doc

    # one chemical identity check before any geometry: two different molecules would make every RMSD below
    # meaningless, and the failure would look like disagreement rather than like a bookkeeping error.
    smis = {r["smiles"] for r in loaded}
    doc["_ligand_identity"] = {"canonical_smiles": sorted(s for s in smis if s),
                               "all_sources_same_molecule": len(smis) == 1}
    if len(smis) != 1:
        doc["_status"] = "ABORT — the sources do not all hold the same molecule"
        return doc

    doc["scale_reference"] = scale_reference(loaded[0]["mol"])
    ref_src = loaded[0]
    pairs = []
    for i in range(len(loaded)):
        for j in range(i + 1, len(loaded)):
            pairs.append(_compare(loaded[i], loaded[j], cutoff, bm))
    doc["reference_frame"] = ref_src["id"]
    doc["pairs"] = pairs

    for fit in ("global", "pocket"):
        doc.setdefault("spread", {})[fit] = {
            "receptor_fit_rmsd_A": spread([p[fit]["receptor_fit_rmsd_A"] for p in pairs]),
            "ligand_rmsd_A": spread([p[fit]["ligand_rmsd_A"] for p in pairs]),
            "ligand_centroid_distance_A": spread([p[fit]["ligand_centroid_distance_A"] for p in pairs]),
        }
    doc["spread"]["contact_jaccard"] = spread([p["contact_jaccard"] for p in pairs])
    scores = [r.get("docking_score_kcalmol") for r in loaded if r.get("docking_score_kcalmol") is not None]
    doc["score_cannot_tell_these_poses_apart"] = {
        "docking_score_spread_kcalmol": spread(scores),
        "pairwise_score_delta_kcalmol": spread([p.get("score_delta_kcalmol") for p in pairs]),
        "pairwise_ligand_rmsd_A": spread([p["pocket"].get("ligand_rmsd_A") for p in pairs]),
        "_reads": "the scoring function's own separation between these poses, beside how far apart they "
                  "actually are. A wide geometric spread under a narrow score spread means the score is "
                  "not the thing that chose among them — which is what 'the top pose' silently assumes.",
        "_caveat": "smina scores from different receptor conformers are not strictly comparable; this is "
                   "reported as the separation the pipeline itself had available, not as an affinity.",
    }
    doc["verdict"] = _verdict(doc, pairs, len(loaded), len(sources))
    doc["_status"] = "ok"
    return doc


def _compare(a, b, cutoff, bm):
    """One ordered pair: put b's receptor on a's, move b's ligand with it, then measure."""
    import nr4a3_8xtt_benchmark as bmod
    sa, sb = a.get("docking_score_kcalmol"), b.get("docking_score_kcalmol")
    out = {"a": a["id"], "b": b["id"],
           "score_delta_kcalmol": (round(abs(sa - sb), 3) if sa is not None and sb is not None else None),
           "independent_receptor": a["receptor"] != b["receptor"],
           "same_method_kind": a["kind"] == b["kind"],
           "same_receptor_provenance": (a.get("receptor_provenance") or "").split("(")[0]
                                       == (b.get("receptor_provenance") or "").split("(")[0]}
    all_res = sorted(set(a["residues"]) & set(b["residues"]))
    lig_a = heavy_coords(a["mol"])
    cen_a = centroid(lig_a)
    for fit, fit_set in (("global", all_res), ("pocket", [r for r in bmod.POCKET5 if r in set(all_res)])):
        rec = {"n_fit_residues": len(fit_set)}
        try:
            R, t, n_fit, fit_rmsd = superpose(b["residues"], a["residues"], fit_set)
        except Exception as e:                               # noqa: BLE001
            rec.update({"error": "%s: %s" % (type(e).__name__, e), "receptor_fit_rmsd_A": None,
                        "ligand_rmsd_A": None, "ligand_centroid_distance_A": None})
            out[fit] = rec
            continue
        moved = transformed_copy(b["mol"], R, t)
        lig_b = heavy_coords(moved)
        lrms, why = symmetry_rmsd(moved, a["mol"])
        cen_b = centroid(lig_b)
        rec.update({
            "n_fit_used": n_fit,
            "receptor_fit_rmsd_A": round(fit_rmsd, 3),
            "ligand_rmsd_A": lrms,
            "ligand_rmsd_error": why,
            "ligand_centroid_distance_A": round(math.dist(cen_a, cen_b), 3),
        })
        if fit == "pocket":
            out["contact_a"] = sorted(contacts(lig_a, a["residues"], cutoff))
            out["contact_b"] = sorted(contacts(lig_b, a["residues"], cutoff))
            out["contact_jaccard"] = jaccard(set(out["contact_a"]), set(out["contact_b"]))
            out["_contacts_note"] = ("both contact sets are read against the SAME receptor (a's), because "
                                     "reading each pose against its own receptor would confound pose "
                                     "disagreement with conformer difference")
            icr, iwhy = internal_conformer_rmsd(a["mol"], b["mol"])
            out["internal_conformer_rmsd_A"] = icr
            out["internal_conformer_rmsd_error"] = iwhy
            out["disagreement_is"] = _decompose(rec.get("ligand_rmsd_A"), icr,
                                                rec.get("ligand_centroid_distance_A"),
                                                out["contact_jaccard"])
        out[fit] = rec
    return out


def _decompose(in_frame_rmsd, internal_rmsd, centroid_d, contact_j):
    """Describe WHICH kind of disagreement two poses have — with the numbers, not a category.

    Deliberately not a classifier. A centroid separation of a couple of Angstrom does not cleanly mean
    "different sub-site" or "same sub-site", and a label asserting either would be doing interpretation the
    measurement cannot support. The sentence carries the three numbers a reader needs to judge it."""
    if in_frame_rmsd is None:
        return None
    if in_frame_rmsd <= SAME_POSE_A:
        return ("agree: %.2f A, inside the field's %.1f A redocking-success boundary"
                % (in_frame_rmsd, SAME_POSE_A))
    bits = ["%.2f A apart in the common frame" % in_frame_rmsd]
    if centroid_d is not None:
        bits.append("centroids %.2f A apart" % centroid_d)
    if contact_j is not None:
        bits.append("%.0f%% of contacted residues shared" % (100 * contact_j))
    if internal_rmsd is not None and in_frame_rmsd:
        frac = internal_rmsd / in_frame_rmsd
        bits.append("internal conformer difference %.2f A = %.0f%% of the total, so the disagreement is "
                    "%s" % (internal_rmsd, 100 * frac,
                            "dominated by PLACEMENT" if frac < 0.5 else "conformer as well as placement"))
    return "; ".join(bits)


#: Bands used to describe a pairwise ligand RMSD. NOT a pass/fail gate — this module has no known answer to
#: pass or fail against, and inventing one would be exactly the tuning the known-answer module forbids.
#: 2.0 A is the field's redocking-success boundary and is used here only as a shared vocabulary so the
#: spread can be described in words a reader already calibrates against.
SAME_POSE_A = 2.0
SAME_SITE_A = 4.0


def _verdict(artifact, pairs, n_usable, n_total):
    ok = [p for p in pairs if p["pocket"].get("ligand_rmsd_A") is not None]
    vals = [p["pocket"]["ligand_rmsd_A"] for p in ok]
    s = spread(vals)
    if not vals:
        return {"convergence_measurable": False,
                "sentence": "No pair produced a ligand RMSD — see per-pair errors."}
    n_same_pose = sum(1 for v in vals if v <= SAME_POSE_A)
    n_same_site = sum(1 for v in vals if v <= SAME_SITE_A)
    # ⚠ THE DISTINCTION THAT DECIDES WHAT THE NUMBER MEANS. Two runs of the SAME method on two conformers
    # measure reproducibility; only a pair whose `kind` differs is the orthogonal-methods evidence this
    # module was built to look for. Counting them together would let a within-method number be read as
    # cross-method agreement.
    cross = [p for p in ok if not p["same_method_kind"]]
    within = [p for p in ok if p["same_method_kind"]]
    xprov = [p for p in ok if not p.get("same_receptor_provenance")]
    wprov = [p for p in ok if p.get("same_receptor_provenance")]
    doc = {
        "convergence_measurable": True,
        "n_usable_sources": n_usable,
        "n_sources_known": n_total,
        "n_pairs": len(vals),
        "n_pairs_independent_receptors": sum(1 for p in ok if p["independent_receptor"]),
        "n_pairs_cross_method": len(cross),
        "n_pairs_within_method": len(within),
        "pocket_fit_ligand_rmsd_spread_A": s,
        "within_method_spread_A": spread([p["pocket"]["ligand_rmsd_A"] for p in within]),
        "cross_method_spread_A": spread([p["pocket"]["ligand_rmsd_A"] for p in cross]),
        "n_pairs_cross_receptor_provenance": len(xprov),
        "cross_provenance_spread_A": spread([p["pocket"]["ligand_rmsd_A"] for p in xprov]),
        "within_provenance_spread_A": spread([p["pocket"]["ligand_rmsd_A"] for p in wprov]),
        "n_pairs_within_%.1fA" % SAME_POSE_A: n_same_pose,
        "n_pairs_within_%.1fA" % SAME_SITE_A: n_same_site,
    }
    ref = artifact.get("scale_reference") or {}
    doc["sentence"] = (
        "Across %d readable pose source(s) of %d known, %d pairwise comparison(s) give a pocket-superposed, "
        "symmetry-corrected ligand RMSD spanning %s-%s A (median %s). %d/%d pairs agree to within %.1f A "
        "and %d/%d to within %.1f A. For scale, the molecule is %s A long, turning it end-for-end in place "
        "costs %s A, and a uniformly random reorientation in place averages %s A. Convergence is not "
        "correctness; this spread bounds how singular 'the predicted pose' is entitled to be."
        % (n_usable, n_total, len(vals), s["min"], s["max"], s["median"],
           n_same_pose, len(vals), SAME_POSE_A, n_same_site, len(vals), SAME_SITE_A,
           ref.get("length_A"), ref.get("flip_rmsd_A"), ref.get("random_reorient_mean_A")))
    recfit = [(p["pocket"]["receptor_fit_rmsd_A"], p["pocket"]["ligand_rmsd_A"]) for p in ok
              if p["pocket"].get("receptor_fit_rmsd_A") is not None]
    tight = [l for r, l in recfit if r <= 1.0]
    doc["receptor_agreement_does_not_predict_ligand_agreement"] = {
        "n_pairs_with_pocket_fit_within_1.0A": len(tight),
        "their_ligand_rmsd_spread_A": spread(tight),
        "_note": "pairs whose POCKETS superpose to within 1 A — i.e. essentially the same receptor "
                 "geometry. Their ligand spread is the part of the disagreement that cannot be blamed on "
                 "the receptors being different conformers.",
    }
    if not cross:
        doc["cross_method_evidence"] = (
            "NONE — AND THAT IS A FINDING, NOT A GAP IN THIS ANALYSIS. Every pose this program holds of "
            "denovo_401 in NR4A3 was generated by the SAME method (smina, top pose). What varies across "
            "the census is the RECEPTOR CONFORMATION, not the method, so %d of the %d pairs cross the "
            "prediction/experiment line and none of them cross a method line. The convergence argument "
            "that would license a singular 'the predicted pose' — independent methods failing differently "
            "and agreeing anyway — cannot be made from what exists, because the second method has never "
            "been run." % (len(xprov), len(ok)))
    return doc


def main():
    doc = measure()
    with open(OUT, "w") as fh:
        json.dump(doc, fh, indent=2)
    print(json.dumps({k: doc[k] for k in ("_status", "n_usable", "verdict", "spread") if k in doc},
                     indent=2))
    print("[pose-convergence] wrote %s" % OUT)
    if doc.get("refusals"):
        print("[pose-convergence] %d refusal(s):" % len(doc["refusals"]))
        for r in doc["refusals"]:
            print("   - %s (%s): %s" % (r["id"], r["stage"], r["evidence"]))


if __name__ == "__main__":
    main()
