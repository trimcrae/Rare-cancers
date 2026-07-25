#!/usr/bin/env python3
"""
NR-V04 covalent panel — CORRECTED-SPLIT t=0 analysis of the systems that actually ran ($0, read-only).

WHY THIS EXISTS. The panel's trajectories were never written (nrv04_result_forensics.py: 0 trajectory objects
in the bucket), so the corrected R1/R2/R3 cannot be recomputed and the MD must be re-run. But the driver DID
persist, for every leg, the exact solvated system it simulated — `built_<leg>_s<seed>.solv.cif`, the topology
plus coordinates of the ~466k-atom assembly. That is ONE frame, not a trajectory, so it cannot give R1's
plateau. It CAN give, for free, the t=0 value of every quantity R1/R2/R3 reduce, under BOTH chain splits:

  * does a VHL/EloBC <-> NR4A1 interface exist at all in each leg's real system, and how large is it,
  * how many NR4A1 lysine Nz atoms the corrected R3 sees versus the Elongin C lysines it actually counted,
  * and where celastrol sits in `warhead_only` relative to NR4A1's cysteines.

Those decide what the re-run can possibly show, before any of it is paid for. Every number here is measured
from a committed artifact; nothing is inferred from the driver's source.

HONEST LIMIT, stated up front: the driver takes its R1 reference frame AFTER equilibration, whereas this
snapshot is written at build time (post-solvation, post-PDBFixer, post-mutation, PRE-minimization). So these
are starting-structure values. They bound what the readouts see; they are not the readouts.

Usage (CI, AWS creds):  python nrv04_corrected_t0.py --bucket $VAST_CKPT_BUCKET
"""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Frozen cutoffs — taken from the driver so this analysis and the MD readouts mean the same thing.
# nrv04_covalent_md.interface_atom_indices(cutoff_nm=0.8) selects the interface; _contacts(cutoff_nm=0.45)
# counts them. Both operate on ALL atoms (hydrogens included), so we replicate that exactly.
IFACE_CUTOFF_NM = 0.8
CONTACT_CUTOFF_NM = 0.45

NR4A_LBD_RESIDUES = 254
E3_CHAIN_RESIDUES = {213: "VHL", 118: "ElonginB", 112: "ElonginC"}

# ⚠ The protein/non-protein test is taken VERBATIM from nrv04_covalent_md._topology_indices, which excludes
# exactly these residue names. It is NOT `gemmi.find_tabulated_residue(...).is_amino_acid()`: the small molecule
# is written as residue **UNK**, and UNK *is* a tabulated amino acid (the PDB's "unknown residue"), so the
# chemical test silently classifies the ligand chain as a 1-residue protein. On the first run of this script it
# did exactly that — sorted-last became the LIGAND chain X instead of Elongin C, and the "as-run" comparison
# reported 0 target lysines. That is the same defect class this whole lane is auditing (a classifier blind to a
# dimension the data varies along), caught here by the numbers disagreeing with the driver's own R3.
NON_PROTEIN_RESNAMES = ("HOH", "NA", "CL", "UNK", "LIG", "UNL")
LIGAND_RESNAMES = ("UNK", "LIG", "UNL")


def _is_protein_res(resname):
    return resname not in NON_PROTEIN_RESNAMES


def _is_ligand_res(resname):
    return resname in LIGAND_RESNAMES


def load_frame(cif_path):
    """Return (chains, atoms) from a solvated mmCIF snapshot.

    chains: {chain_id: {"n_res": int, "kind": "protein"|"ligand"}}
    atoms:  list of dicts (chain, resname, resid, name, element, xyz in nm) for protein + ligand atoms only —
            water and ions are ~95 % of the file and touch none of the readouts, so they are dropped on read.
    """
    import gemmi
    st = gemmi.read_structure(cif_path)
    chains, atoms = {}, []
    for ch in st[0]:
        n_prot = n_lig = 0
        for res in ch:
            prot, lig = _is_protein_res(res.name), _is_ligand_res(res.name)
            if not (prot or lig):
                continue                                        # water / ions
            n_prot += int(prot)
            n_lig += int(lig)
            for at in res:
                atoms.append({"chain": ch.name, "resname": res.name, "resid": str(res.seqid.num),
                              "name": at.name.strip(), "element": at.element.name,
                              # gemmi positions are Angstrom; the driver works in nm.
                              "xyz": (at.pos.x / 10.0, at.pos.y / 10.0, at.pos.z / 10.0)})
        if n_prot or n_lig:
            chains[ch.name] = {"n_res": n_prot + n_lig, "kind": "protein" if n_prot else "ligand"}
    return chains, atoms


def split_chains(chains):
    """The two competing splits, both computed on the same census so they can be compared directly.

    corrected — the target is the chain matching the frozen 254-residue NR4A LBD, every other protein chain
                matching a known E3 component (nrv04_covalent_assemble.identify_chains' rule).
    positional — 'the target is the LAST protein chain in sorted order' (the rule that actually ran).
    """
    prot = sorted([c for c, v in chains.items() if v["kind"] == "protein"])
    census = {c: chains[c]["n_res"] for c in prot}
    corrected_target = [c for c in prot if census[c] == NR4A_LBD_RESIDUES]
    e3_named = {c: E3_CHAIN_RESIDUES[census[c]] for c in prot if census[c] in E3_CHAIN_RESIDUES}
    positional_target = [prot[-1]] if len(prot) > 1 else []
    return {
        "protein_chains": prot, "census": census, "e3_roles": e3_named,
        "corrected": {"target": corrected_target, "e3": [c for c in prot if c not in corrected_target]},
        "positional": {"target": positional_target, "e3": [c for c in prot if c not in positional_target]},
        "splits_agree": corrected_target == positional_target,
    }


def interface_stats(atoms, e3_chains, target_chains):
    """The driver's own two-stage reduction, at t=0: select the interface at 0.8 nm, then count contacts at
    0.45 nm within that selection. Returns the numbers R1's atom set and R2's contact count are built from."""
    import numpy as np
    from scipy.spatial import cKDTree
    e3 = [a for a in atoms if a["chain"] in e3_chains]
    tg = [a for a in atoms if a["chain"] in target_chains]
    if not e3 or not tg:
        return {"e3_atoms": len(e3), "target_atoms": len(tg), "iface_e3_side": 0, "iface_target_side": 0,
                "iface_atoms": 0, "contacts_t0": 0,
                "note": "one side of the split is empty — no interface can exist"}
    E = np.array([a["xyz"] for a in e3]); T = np.array([a["xyz"] for a in tg])
    te = cKDTree(E); tt = cKDTree(T)
    pairs = te.query_ball_tree(tt, IFACE_CUTOFF_NM)
    e3_side = [i for i, p in enumerate(pairs) if p]
    tg_side = sorted({j for p in pairs for j in p})
    if not e3_side or not tg_side:
        return {"e3_atoms": len(e3), "target_atoms": len(tg), "iface_e3_side": 0, "iface_target_side": 0,
                "iface_atoms": 0, "contacts_t0": 0, "note": "the two chain groups are not in contact at 0.8 nm"}
    n_contacts = sum(len(p) for p in cKDTree(E[e3_side]).query_ball_tree(cKDTree(T[tg_side]), CONTACT_CUTOFF_NM))
    return {"e3_atoms": len(e3), "target_atoms": len(tg),
            "iface_e3_side": len(e3_side), "iface_target_side": len(tg_side),
            "iface_atoms": len(e3_side) + len(tg_side), "contacts_t0": int(n_contacts)}


def lys_stats(atoms, e3_chains, target_chains):
    """R3's inputs at t=0: the target chain's Lys Nz atoms and their distance to the E3-centroid proxy."""
    import numpy as np
    nz = np.array([a["xyz"] for a in atoms
                   if a["resname"] == "LYS" and a["name"] == "NZ" and a["chain"] in target_chains])
    e3 = np.array([a["xyz"] for a in atoms if a["chain"] in e3_chains])
    if nz.size == 0 or e3.size == 0:
        return {"n_target_lys_nz": int(nz.shape[0] if nz.size else 0), "min_A": None, "median_A": None}
    proxy = e3.mean(axis=0)
    d = np.linalg.norm(nz - proxy, axis=1) * 10.0                      # nm -> Angstrom
    return {"n_target_lys_nz": int(nz.shape[0]), "min_A": round(float(d.min()), 2),
            "median_A": round(float(np.median(d)), 2), "max_A": round(float(d.max()), 2)}


def warhead_geometry(atoms, target_chains):
    """Where the warhead actually is. For every ligand heavy atom, the nearest Cys Sg — reported BOTH globally
    (what the driver's geometric search does) and restricted to the identified target chain (what it should do).
    A large target-restricted distance means the co-fold never posed the warhead in the NR4A1 pocket, which no
    chain-split fix can repair."""
    import numpy as np
    lig = [a for a in atoms if _is_ligand_res(a["resname"]) and a["element"] != "H"]
    sg_all = [a for a in atoms if a["resname"] == "CYS" and a["name"] == "SG"]
    if not lig or not sg_all:
        return {"ligand_heavy_atoms": len(lig), "cys_sg": len(sg_all), "note": "no ligand or no cysteine"}
    L = np.array([a["xyz"] for a in lig])
    out = {"ligand_heavy_atoms": len(lig), "cys_sg_total": len(sg_all)}
    for tag, sel in (("global", sg_all),
                     ("target_chain_only", [a for a in sg_all if a["chain"] in target_chains])):
        if not sel:
            out[tag] = {"n_sg": 0, "min_A": None}
            continue
        S = np.array([a["xyz"] for a in sel])
        d = np.linalg.norm(L[:, None, :] - S[None, :, :], axis=2) * 10.0
        i, j = np.unravel_index(int(np.argmin(d)), d.shape)
        out[tag] = {"n_sg": len(sel), "min_A": round(float(d.min()), 2),
                    "cys": f"{sel[j]['chain']}:{sel[j]['resid']}", "lig_atom": lig[i]["name"]}
    return out


def target_ca_coords(cif_path, target_chain=None, n_res=NR4A_LBD_RESIDUES):
    """CA coordinates (nm) of the degradation-target chain, in residue order — the fingerprint used to identify
    WHICH co-fold a simulated system was built from. If `target_chain` is None the chain with `n_res` protein
    residues is used."""
    chains, atoms = load_frame(cif_path)
    if target_chain is None:
        cand = [c for c, v in chains.items() if v["kind"] == "protein" and v["n_res"] == n_res]
        if len(cand) != 1:
            return None, {"error": f"no unique {n_res}-residue chain; census="
                                   f"{ {c: v['n_res'] for c, v in chains.items()} }"}
        target_chain = cand[0]
    ca = [(int(a["resid"]), a["xyz"]) for a in atoms if a["name"] == "CA" and a["chain"] == target_chain]
    ca.sort()
    return [x for _, x in ca], {"chain": target_chain, "n_ca": len(ca)}


def identify_source_cofold(built_cif, candidate_cifs):
    """Which co-fold produced this simulated system?

    The census already proves the panel's chain F is 255 residues (14-3-3 epsilon) while the prefix the code
    now points at carries a 118-residue Elongin B — so the panel did NOT come from that prefix. This pins the
    positive identification instead of only the negative one: solvation translates every atom and PDBFixer adds
    hydrogens, but the heavy-atom CA geometry of the target chain is carried through unchanged, so a Kabsch RMSD
    of ~0 A against a candidate co-fold identifies the exact source model. A non-match is >> 1 A because
    independent Boltz seeds do not reproduce each other's coordinates."""
    from nrv04_covalent_md import kabsch_rmsd
    ref, meta = target_ca_coords(built_cif)
    if ref is None:
        return {"error": meta}
    rows = []
    for name, path in candidate_cifs:
        cand, cmeta = target_ca_coords(path)
        if cand is None or len(cand) != len(ref):
            rows.append({"candidate": name, "rmsd_A": None,
                         "note": f"CA count {len(cand) if cand else None} != {len(ref)}", "meta": cmeta})
            continue
        rows.append({"candidate": name, "rmsd_A": round(kabsch_rmsd(cand, ref) * 10.0, 3), "meta": cmeta})
    scored = [r for r in rows if r.get("rmsd_A") is not None]
    best = min(scored, key=lambda r: r["rmsd_A"]) if scored else None
    return {"built": meta, "candidates": rows, "best_match": best,
            "verdict": ("IDENTIFIED — CA geometry is identical to this co-fold model"
                        if best and best["rmsd_A"] < 0.05 else
                        "NO candidate matches; the source co-fold is not among those tested")}


def analyse_cif(cif_path):
    chains, atoms = load_frame(cif_path)
    sp = split_chains(chains)
    corr, pos = sp["corrected"], sp["positional"]
    res = {"chain_census": sp["census"], "e3_roles": sp["e3_roles"],
           "corrected_split": corr, "positional_split": pos, "splits_agree": sp["splits_agree"],
           "corrected": {"interface": interface_stats(atoms, corr["e3"], corr["target"]),
                         "R3_inputs": lys_stats(atoms, corr["e3"], corr["target"])},
           "positional_as_run": {"interface": interface_stats(atoms, pos["e3"], pos["target"]),
                                 "R3_inputs": lys_stats(atoms, pos["e3"], pos["target"])},
           "warhead": warhead_geometry(atoms, corr["target"])}
    return res


def main(argv=None):
    import argparse
    import boto3
    ap = argparse.ArgumentParser(description="Corrected-split t=0 analysis of the panel's persisted systems.")
    ap.add_argument("--bucket", default=os.environ.get("VAST_CKPT_BUCKET", ""))
    ap.add_argument("--prefix", default="nrv04-covalent-results")
    # Candidate source co-folds for the identity match: the prefix the launcher points at NOW, and the two
    # contaminated prefixes that predate it. `nrv04-descriptive-v3` was the workflow input's DEFAULT at the time
    # the panel ran (fusion-cpu-extras.yml @786759a9, cofold_prefix default "nrv04-descriptive-v3"), which is the
    # mechanism this match is testing.
    ap.add_argument("--cofold-candidates",
                    default="nrv04-covalent-cofold/nr4a1,nrv04-descriptive-v3/nr4a1,nrv04-shakeout/nr4a1")
    ap.add_argument("--out", default="research/modalities/nrv04-corrected-t0.json")
    args = ap.parse_args(argv)
    if not args.bucket:
        raise SystemExit("set --bucket or $VAST_CKPT_BUCKET")

    s3 = boto3.client("s3")

    def _list(prefix, suffix):
        out, tok = [], None
        while True:
            kw = {"Bucket": args.bucket, "Prefix": prefix}
            if tok:
                kw["ContinuationToken"] = tok
            r = s3.list_objects_v2(**kw)
            out += [o["Key"] for o in r.get("Contents", []) if o["Key"].endswith(suffix)]
            if not r.get("IsTruncated"):
                break
            tok = r["NextContinuationToken"]
        return out

    keys = _list(args.prefix.rstrip("/") + "/", ".solv.cif")

    # Pull one model per candidate co-fold prefix for the identity match.
    candidates = []
    for cp in [c for c in args.cofold_candidates.split(",") if c]:
        cks = sorted(_list(cp.rstrip("/") + "/", "_model_0.cif"))
        for ck in cks[:3]:                                      # a few seeds each; a wrong seed still shows >> 1 A
            local = "/tmp/cand_" + ck.replace("/", "_")
            try:
                s3.download_file(args.bucket, ck, local)
                candidates.append((ck, local))
            except Exception as e:  # noqa: BLE001
                print(f"[t0] candidate {ck} unavailable: {e}", flush=True)
    print(f"[t0] {len(candidates)} candidate co-fold models for the identity match", flush=True)

    doc = {"bucket": args.bucket, "prefix": args.prefix, "n_snapshots": len(keys),
           "cutoffs_nm": {"interface": IFACE_CUTOFF_NM, "contact": CONTACT_CUTOFF_NM},
           "limit": "build-time snapshot (pre-minimization); the driver's R1 reference is post-equilibration. "
                    "These bound what the readouts see; they are not the readouts.",
           "units": {}}
    for k in sorted(keys):
        unit = k.split("/")[-2]
        local = "/tmp/snap.cif"
        print(f"[t0] {unit} <- {k}", flush=True)
        s3.download_file(args.bucket, k, local)
        try:
            doc["units"][unit] = analyse_cif(local)
            doc["units"][unit]["source_key"] = k
            # Identify the source co-fold ONCE (the first unit) — it is the same staging path for every leg and
            # the match costs a full parse of every candidate.
            if "source_cofold" not in doc:
                doc["source_cofold"] = {"tested_on": unit, "result": identify_source_cofold(local, candidates)}
                print("[t0] SOURCE CO-FOLD: " + json.dumps(doc["source_cofold"]["result"], indent=2), flush=True)
        except Exception as e:  # noqa: BLE001
            doc["units"][unit] = {"source_key": k, "error": f"{type(e).__name__}: {e}"}
        finally:
            if os.path.exists(local):
                os.remove(local)
        print("    " + json.dumps({kk: vv for kk, vv in doc["units"][unit].items()
                                   if kk in ("chain_census", "splits_agree")}), flush=True)
        c = doc["units"][unit].get("corrected", {})
        p = doc["units"][unit].get("positional_as_run", {})
        print(f"    corrected  iface_atoms={c.get('interface', {}).get('iface_atoms')} "
              f"contacts_t0={c.get('interface', {}).get('contacts_t0')} "
              f"target_lys_nz={c.get('R3_inputs', {}).get('n_target_lys_nz')} "
              f"R3_min_A={c.get('R3_inputs', {}).get('min_A')}", flush=True)
        print(f"    as-run     iface_atoms={p.get('interface', {}).get('iface_atoms')} "
              f"contacts_t0={p.get('interface', {}).get('contacts_t0')} "
              f"target_lys_nz={p.get('R3_inputs', {}).get('n_target_lys_nz')} "
              f"R3_min_A={p.get('R3_inputs', {}).get('min_A')}", flush=True)
        print(f"    warhead    {json.dumps(doc['units'][unit].get('warhead'))}", flush=True)

    with open(args.out, "w") as f:
        json.dump(doc, f, indent=2)
    print(f"\nwrote {args.out} ({len(doc['units'])} units)", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
