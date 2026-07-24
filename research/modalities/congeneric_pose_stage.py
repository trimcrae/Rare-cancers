#!/usr/bin/env python3
"""
STEP 1 FAN-OUT — common-mode pose staging for the cmpd19 congeneric series (RDKit; free CPU, no GPU).

WHY THIS EXISTS. RBFE's whole cost advantage rests on the COMMON-MODE assumption: both endpoints of an edge
occupy the SAME binding mode, so the shared scaffold cancels. The map enforces that chemically (every edge is
a single-site swap off a shared indole core), but it also has to hold GEOMETRICALLY — the two poses handed to
OpenFE must have their shared scaffold superimposed, or LOMAP's distance filter rejects an otherwise-valid
topological map (the 2026-07-14 n_mapped=1 root cause) and the morph is not physical.

Independently re-docking each of the 17 analogues would NOT give that: smina would place each one in its own
local optimum, and a 0.5-1.5 A core displacement between two analogues is both invisible to a docking score
and fatal to the morph. So this module does the thing the common-mode assumption actually asks for: it takes
the ONE experimentally-motivated anchor pose (cmpd19, docked into the frozen nr4a3_design Pocket-5 box —
`nr4a3-congeneric-dock-result.json`, smina, run 29175736795) and builds every analogue by MCS-CORE-CONSTRAINED
EMBEDDING onto it, so all 17 share the anchor's core coordinates EXACTLY and differ only in the substituent.

WHAT THIS IS NOT. This is INPUT STAGING, not evidence. It does not establish that cmpd19 binds in this pose
(there is no solved NR4A3 cocrystal — only functional target engagement), it does not score anything, and it
does not make any analogue's pose "correct". It propagates ONE hypothesis consistently, which is exactly what
makes the resulting ddG values conditional-on-that-hypothesis and mutually comparable.

QC, and what a failure means. Each staged pose is checked for (a) a large enough shared core, (b) core
coordinates that really did land on the anchor's, and (c) no hard steric clash with the receptor. A pose that
fails (a) or (b) is a BROKEN morph -> the unit is refused. A pose that fails (c) is reported as
`needs_pose_revalidation` rather than silently accepted: a clashing substituent means the analogue cannot
occupy the anchor's mode without receptor relaxation, which is a real (and interesting) result about the
5-position exit-vector hypothesis, not a staging bug to paper over.

Runs free on a CI runner (`pip install rdkit`) and uploads the staged tree to S3 for the Vast fan-out.
Usage:  python congeneric_pose_stage.py            # stage + QC (+ upload if S3_BUCKET/OUT_PREFIX set)
        STAGE_DRY=1 python congeneric_pose_stage.py  # stage + QC to a local dir, no S3 write
"""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from congeneric_fanout import PRIMARY_RECEPTOR, default_units, smiles_registry  # noqa: E402

ANCHOR = "zaienne_cmpd19"

# The congeneric DOCKING output the pilot consumed (nr4a3-opened.pdb + _pose_<lig>.sdf per endpoint).
DOCK_PREFIX = os.environ.get("DOCK_PREFIX", "nr4a3-congeneric-dock/congeneric-poses2-ckpt")
OUT_PREFIX = os.environ.get("OUT_PREFIX", "nr4a3-step1-fanout/stage")
BUCKET = os.environ.get("S3_BUCKET", os.environ.get("VAST_CKPT_BUCKET", ""))

# QC thresholds. The core floor is deliberately generous: the 3-position bioisosteres (tetrazole,
# acylsulfonamide) legitimately replace the ester, so their shared core is the 5-substituted indole alone.
MIN_CORE_ATOMS = int(os.environ.get("STAGE_MIN_CORE_ATOMS", "8"))
MAX_CORE_RMSD_A = float(os.environ.get("STAGE_MAX_CORE_RMSD", "0.35"))
CLASH_CUTOFF_A = float(os.environ.get("STAGE_CLASH_CUTOFF", "2.0"))


def _rdkit():
    from rdkit import Chem, RDLogger
    from rdkit.Chem import AllChem, rdFMCS, rdMolAlign
    RDLogger.DisableLog("rdApp.warning")
    return Chem, AllChem, rdFMCS, rdMolAlign


def read_anchor_pose(sdf_path, smiles):
    """Load the docked anchor pose and re-impose bond orders from its known SMILES.

    Docked SDFs come back with perceived valences that can leave radical electrons (which later kills the
    OpenFF charge step); the same repair `nr4a3_rbfe._repair_pose` applies is done here so the template the
    whole series is built on is clean. Heavy-atom coordinates are untouched."""
    Chem, AllChem, _, _ = _rdkit()
    mols = [m for m in Chem.SDMolSupplier(sdf_path, removeHs=False, sanitize=False) if m is not None]
    if not mols:
        raise SystemExit(f"[stage] no molecule in anchor pose SDF {sdf_path}")
    raw = mols[0]
    tmpl = Chem.MolFromSmiles(smiles)
    if tmpl is None:
        raise SystemExit(f"[stage] unparseable anchor SMILES {smiles!r}")
    heavy = Chem.RemoveHs(raw, sanitize=False)
    Chem.SanitizeMol(heavy, Chem.SanitizeFlags.SANITIZE_ALL ^ Chem.SanitizeFlags.SANITIZE_KEKULIZE)
    fixed = AllChem.AssignBondOrdersFromTemplate(tmpl, heavy)
    fixed = Chem.AddHs(fixed, addCoords=True)
    Chem.SanitizeMol(fixed)
    fixed.SetProp("_Name", ANCHOR)
    return fixed


def core_match(mol, anchor, rdFMCS, Chem):
    """Map the analogue's shared-core atoms onto the anchor's, as (anchor_idx, mol_idx) pairs.

    Deliberately NOT RDKit's ConstrainedEmbed-with-a-fragment idiom: carving an RWMol core out of the anchor
    produces a fragment whose perceived valences/aromaticity often fail to substructure-match the analogue,
    which fails silently as "no core". Matching the MCS SMARTS against BOTH molecules and driving the embed
    from an explicit coordinate map is robust to that. Ring-complete/ring-only MCS keeps the indole intact
    instead of letting the match wander into a partial ring."""
    a_heavy = Chem.RemoveHs(Chem.Mol(anchor))
    m_heavy = Chem.RemoveHs(Chem.Mol(mol))
    mcs = rdFMCS.FindMCS([a_heavy, m_heavy], completeRingsOnly=True, ringMatchesRingOnly=True, timeout=60)
    if mcs.numAtoms < MIN_CORE_ATOMS:
        return None, mcs.numAtoms
    patt = Chem.MolFromSmarts(mcs.smartsString)
    if patt is None:
        return None, mcs.numAtoms
    a_match, m_match = anchor.GetSubstructMatch(patt), mol.GetSubstructMatch(patt)
    if not a_match or not m_match or len(a_match) != len(m_match):
        return None, mcs.numAtoms
    return list(zip(a_match, m_match)), mcs.numAtoms


def build_pose(node_id, smiles, anchor, seed=0xC19):
    """Build one analogue's pose: embed it with the shared core PINNED to the anchor's coordinates, MMFF-relax
    only the grown substituent, then snap the core exactly onto the anchor. Returns (mol, qc)."""
    Chem, AllChem, rdFMCS, rdMolAlign = _rdkit()
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise SystemExit(f"[stage] unparseable SMILES for {node_id}: {smiles!r}")
    mol = Chem.AddHs(mol)
    pairs, n_mcs = core_match(mol, anchor, rdFMCS, Chem)
    if pairs is None:
        return None, {"node": node_id, "status": "NO_CORE", "mcs_atoms": n_mcs,
                      "reason": f"MCS with the anchor is {n_mcs} atoms (< {MIN_CORE_ATOMS}) or did not match "
                                f"both molecules; the common-mode assumption does not hold for this analogue"}
    aconf = anchor.GetConformer()
    coord_map = {mi: aconf.GetAtomPosition(ai) for ai, mi in pairs}
    cid = -1
    for attempt, kwargs in enumerate(({}, {"useRandomCoords": True}, {"useRandomCoords": True, "maxAttempts": 200})):
        cid = AllChem.EmbedMolecule(mol, coordMap=coord_map, randomSeed=seed + attempt,
                                    useBasicKnowledge=True, **kwargs)
        if cid >= 0:
            break
    if cid < 0:
        return None, {"node": node_id, "status": "EMBED_FAILED", "mcs_atoms": n_mcs,
                      "reason": "RDKit could not embed a 3D conformer with the core pinned to the anchor"}

    m_core = [mi for _ai, mi in pairs]
    try:
        ff = AllChem.MMFFGetMoleculeForceField(mol, AllChem.MMFFGetMoleculeProperties(mol))
        if ff is not None:
            for idx in m_core:
                ff.MMFFAddPositionConstraint(idx, 0.0, 1.0e3)
            ff.Minimize(maxIts=500)
    except Exception as e:  # noqa: BLE001 — relaxation is a nicety; the pinned embed is load-bearing
        print(f"[stage] {node_id}: MMFF relax skipped ({e})", flush=True)

    # rigid-body snap: removes any residual core drift the embed/relax left, without touching internal geometry
    rdMolAlign.AlignMol(mol, anchor, atomMap=[(mi, ai) for ai, mi in pairs])
    core_rmsd = _core_rmsd(mol, anchor, pairs)
    mol.SetProp("_Name", node_id)
    qc = {"node": node_id, "status": "ok", "mcs_atoms": n_mcs, "core_atoms": len(pairs),
          "core_rmsd_A": round(core_rmsd, 3), "n_heavy": Chem.RemoveHs(mol).GetNumAtoms()}
    if core_rmsd > MAX_CORE_RMSD_A:
        qc["status"] = "CORE_DRIFT"
        qc["reason"] = (f"core RMSD {core_rmsd:.2f} A > {MAX_CORE_RMSD_A} A — the shared scaffold did not land "
                        "on the anchor's, so the morph would not be common-mode")
    return mol, qc


def _core_rmsd(mol, anchor, pairs):
    """RMSD between the analogue's core atoms and the anchor atoms they were pinned to."""
    conf, aconf = mol.GetConformer(), anchor.GetConformer()
    tot = 0.0
    for ai, mi in pairs:
        p, q = conf.GetAtomPosition(mi), aconf.GetAtomPosition(ai)
        tot += (p.x - q.x) ** 2 + (p.y - q.y) ** 2 + (p.z - q.z) ** 2
    return (tot / max(1, len(pairs))) ** 0.5


def receptor_heavy_coords(pdb_path):
    """Heavy-atom coordinates of the receptor, straight out of the PDB (stdlib parse — no structure library
    needed for a clash count)."""
    xyz = []
    with open(pdb_path) as f:
        for line in f:
            if not line.startswith(("ATOM", "HETATM")):
                continue
            name = line[12:16].strip()
            if name.startswith("H") or line[76:78].strip() == "H":
                continue
            try:
                xyz.append((float(line[30:38]), float(line[38:46]), float(line[46:54])))
            except ValueError:
                continue
    return xyz


def clash_count(mol, rec_xyz, cutoff=CLASH_CUTOFF_A):
    """Number of ligand-heavy / receptor-heavy pairs closer than `cutoff`, and the closest contact."""
    from rdkit import Chem
    heavy = Chem.RemoveHs(Chem.Mol(mol))
    conf = heavy.GetConformer()
    lig = [(conf.GetAtomPosition(i).x, conf.GetAtomPosition(i).y, conf.GetAtomPosition(i).z)
           for i in range(heavy.GetNumAtoms())]
    c2, n, closest = cutoff * cutoff, 0, 1e9
    for lx, ly, lz in lig:
        for rx, ry, rz in rec_xyz:
            d2 = (lx - rx) ** 2 + (ly - ry) ** 2 + (lz - rz) ** 2
            if d2 < closest:
                closest = d2
            if d2 < c2:
                n += 1
    return n, round(closest ** 0.5, 2)


def stage(anchor_sdf, receptor_pdb, out_dir, receptor=PRIMARY_RECEPTOR):
    """Build the full docked SDF for every node the fan-out needs + a QC report. Returns (sdf_path, report)."""
    from rdkit import Chem

    smiles = smiles_registry()
    units = default_units()
    needed = sorted({u["ligand_a"] for u in units} | {u["ligand_b"] for u in units})
    anchor = read_anchor_pose(anchor_sdf, smiles[ANCHOR])
    rec = receptor_heavy_coords(receptor_pdb)
    print(f"[stage] anchor pose loaded ({anchor.GetNumAtoms()} atoms incl. H); receptor {len(rec)} heavy atoms; "
          f"{len(needed)} nodes to stage", flush=True)

    os.makedirs(os.path.join(out_dir, "ligand"), exist_ok=True)
    os.makedirs(os.path.join(out_dir, "receptor"), exist_ok=True)
    sdf_path = os.path.join(out_dir, "ligand", f"docked_{receptor}.sdf")

    poses, report = {}, []
    for node in needed:
        if node == ANCHOR:
            mol, qc = anchor, {"node": ANCHOR, "status": "ok", "source": "smina docked pose (run 29175736795)",
                               "core_atoms": Chem.RemoveHs(anchor).GetNumAtoms(), "core_rmsd_A": 0.0}
        else:
            mol, qc = build_pose(node, smiles[node], anchor)
        if mol is not None:
            nclash, closest = clash_count(mol, rec)
            qc["receptor_clashes_lt_%.1fA" % CLASH_CUTOFF_A] = nclash
            qc["closest_receptor_contact_A"] = closest
            if nclash:
                qc["needs_pose_revalidation"] = True
                qc["revalidation_reason"] = (f"{nclash} heavy-atom contacts < {CLASH_CUTOFF_A} A with the rigid "
                                             "receptor: this substituent cannot occupy the anchor mode without "
                                             "receptor relaxation — a finding about the exit-vector hypothesis, "
                                             "reported, not hidden")
            poses[node] = mol
        report.append(qc)
        print(f"[stage] {node:28s} {qc['status']:12s} core={qc.get('core_atoms')} "
              f"rmsd={qc.get('core_rmsd_A')} clashes={qc.get('receptor_clashes_lt_%.1fA' % CLASH_CUTOFF_A)}",
              flush=True)

    w = Chem.SDWriter(sdf_path)
    for node in needed:
        if node in poses:
            w.write(poses[node])
    w.close()

    with open(receptor_pdb) as src, open(os.path.join(out_dir, "receptor", f"{receptor}-opened.pdb"), "w") as dst:
        dst.write(src.read())

    names = [m.GetProp("_Name") for m in Chem.SDMolSupplier(sdf_path, sanitize=False) if m is not None]
    missing = [n for n in needed if n not in names]
    summary = {
        "_what": "common-mode pose staging for the step1 congeneric RBFE fan-out — INPUT STAGING ONLY, not "
                 "evidence of binding, affinity or selectivity",
        "_method": "MCS-core-constrained embedding onto the ONE docked cmpd19 anchor pose (smina, frozen "
                   "nr4a3_design Pocket-5 box, run 29175736795), then MMFF relaxation of the grown substituent "
                   "with the shared core pinned. All analogues share the anchor's core coordinates exactly.",
        "_limitation": "cmpd19 has no solved NR4A3 cocrystal; the anchor pose is a HYPOTHESIS. Every downstream "
                       "ddG is conditional on it. Consistent propagation makes the ddG values mutually "
                       "comparable; it does not make the pose right.",
        "receptor": receptor, "n_requested": len(needed), "n_staged": len(names),
        "missing": missing, "sdf": os.path.basename(sdf_path), "qc": report,
        "thresholds": {"min_core_atoms": MIN_CORE_ATOMS, "max_core_rmsd_A": MAX_CORE_RMSD_A,
                       "clash_cutoff_A": CLASH_CUTOFF_A},
    }
    with open(os.path.join(out_dir, "stage_qc.json"), "w") as f:
        json.dump(summary, f, indent=2)
    return sdf_path, summary


def _pull_dock_inputs(bucket, prefix, work):
    """Fetch the anchor pose + receptor PDB out of the congeneric docking output in S3."""
    import boto3
    s3 = boto3.client("s3")
    keys, tok = [], None
    while True:
        kw = {"Bucket": bucket, "Prefix": prefix.rstrip("/") + "/"}
        if tok:
            kw["ContinuationToken"] = tok
        r = s3.list_objects_v2(**kw)
        keys += [o["Key"] for o in r.get("Contents", [])]
        if not r.get("IsTruncated"):
            break
        tok = r["NextContinuationToken"]
    pdb_key = next((k for k in keys if k.endswith(f"{PRIMARY_RECEPTOR}-opened.pdb")),
                   next((k for k in keys if k.endswith("-opened.pdb")), None))
    pose_key = next((k for k in keys if k.endswith(f"_pose_{ANCHOR}.sdf")), None)
    if not (pdb_key and pose_key):
        print("[stage] KEYS:", *keys, sep="\n  ")
        raise SystemExit(f"[stage] missing docking inputs under s3://{bucket}/{prefix}/ "
                         f"(receptor={pdb_key}, anchor_pose={pose_key})")
    os.makedirs(work, exist_ok=True)
    pdb, sdf = os.path.join(work, "receptor.pdb"), os.path.join(work, "anchor.sdf")
    s3.download_file(bucket, pdb_key, pdb)
    s3.download_file(bucket, pose_key, sdf)
    print(f"[stage] pulled {pdb_key} + {pose_key}", flush=True)
    return sdf, pdb


def _push(bucket, prefix, out_dir):
    import boto3
    s3 = boto3.client("s3")
    n = 0
    for root, _, files in os.walk(out_dir):
        for fn in files:
            p = os.path.join(root, fn)
            key = f"{prefix.strip('/')}/{os.path.relpath(p, out_dir)}"
            s3.upload_file(p, bucket, key)
            print(f"[stage] uploaded s3://{bucket}/{key}", flush=True)
            n += 1
    return n


def main():
    work = os.environ.get("STAGE_WORK", "/tmp/step1_stage")
    out_dir = os.path.join(work, "out")
    anchor_sdf = os.environ.get("ANCHOR_SDF")
    receptor_pdb = os.environ.get("RECEPTOR_PDB")
    if not (anchor_sdf and receptor_pdb):
        if not BUCKET:
            raise SystemExit("[stage] need ANCHOR_SDF+RECEPTOR_PDB, or S3_BUCKET/VAST_CKPT_BUCKET to pull them")
        anchor_sdf, receptor_pdb = _pull_dock_inputs(BUCKET, DOCK_PREFIX, work)

    sdf_path, summary = stage(anchor_sdf, receptor_pdb, out_dir)
    bad = [q for q in summary["qc"] if q["status"] != "ok"]
    reval = [q["node"] for q in summary["qc"] if q.get("needs_pose_revalidation")]
    print(f"\n[stage] staged {summary['n_staged']}/{summary['n_requested']} -> {sdf_path}")
    print(f"[stage] failed QC: {[q['node'] for q in bad] or 'none'}")
    print(f"[stage] clash -> needs_pose_revalidation: {reval or 'none'}")

    if os.environ.get("STAGE_DRY") == "1":
        print("[stage] STAGE_DRY=1 — not uploading")
    elif BUCKET:
        _push(BUCKET, OUT_PREFIX, out_dir)
    else:
        print("[stage] no bucket configured — local only")

    if bad:
        raise SystemExit(f"[stage] {len(bad)} node(s) failed staging QC — refusing to hand a broken morph to "
                         f"the fan-out: {json.dumps(bad, indent=2)}")
    print("[stage] OK")


if __name__ == "__main__":
    main()
