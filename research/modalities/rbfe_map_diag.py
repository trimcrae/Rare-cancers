#!/usr/bin/env python3
"""Root-cause the degenerate RBFE atom map (2026-07-14 forensic: the congeneric pilot's solvent leg reported
n_mapped_atoms=1 for the zaienne_cmpd19 5-Br -> cw_ev_5nh2 5-NH2 edge, whose MCS is ~13 atoms — a map that small
alchemically transforms nearly the whole molecule, so ΔG_morph and thus ΔΔG are invalid). This isolates WHERE the
map collapses WITHOUT a GPU or the (slow) openfe conda solve: it pulls the real docked SDF from S3 and, with rdkit
only, (1) resolves each ligand's docked record via the engine's own _sdf_mol, (2) runs the engine's _repair_pose,
(3) reports heavy-atom counts before/after repair, and (4) runs rdFMCS between the two repaired mols to show the
true common-atom count. If the repaired mols are sane and rdFMCS is ~13, the collapse is in the openfe/LOMAP layer
(escalate to a mode=smoke); if repair mangles a mol (atom count crashes / fragments), the bug is pose-repair. Pure
rdkit + boto3 -> runs free on a CI runner. Reuses nr4a3_rbfe._sdf_mol/_repair_pose so we test the ACTUAL code path.
"""
import os
import sys
import tempfile

import boto3
from rdkit import Chem
from rdkit.Chem import rdFMCS

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nr4a3_rbfe as R  # noqa: E402  (reuse the real _sdf_mol / _repair_pose)
import rbfe_edges as rb  # noqa: E402

EDGE = (os.environ.get("MAP_LIGAND_A", "zaienne_cmpd19"), os.environ.get("MAP_LIGAND_B", "cw_ev_5nh2"))
# candidate S3 prefixes that may hold docked_<r>.sdf (the RBFE receptor input). Search broadly; first hit wins.
# NB: `os.environ.get(x, default)` returns "" when the CI passes an EMPTY input (the var IS set) — so `or` the
# default, don't rely on the get() fallback (that empty-string override is what made the first run search []).
CANDIDATE_PREFIXES = [p.strip() for p in ((os.environ.get("MAP_PREFIXES") or "").strip() or
    "nr4a3-congeneric-dock/congeneric-poses2-ckpt,nr4a3-congeneric-dock,nr4a3-leadopt-species,"
    "nr4a3-congeneric-dock/congeneric-pilot-ckpt").split(",") if p.strip()]


def _find_sdf(s3, bucket):
    for pfx in CANDIDATE_PREFIXES:
        for page in s3.get_paginator("list_objects_v2").paginate(Bucket=bucket, Prefix=pfx):
            for o in page.get("Contents", []):
                if o["Key"].endswith("docked_nr4a3.sdf"):
                    return o["Key"]
    # not under the candidates — bucket-wide fallback: report ALL docked*.sdf keys so we learn the real location.
    print(f"[mapdiag] no docked_nr4a3.sdf under {CANDIDATE_PREFIXES}; scanning the whole bucket for docked*.sdf ...")
    hits = []
    for page in s3.get_paginator("list_objects_v2").paginate(Bucket=bucket):
        for o in page.get("Contents", []):
            k = o["Key"]
            if k.endswith(".sdf") and "docked" in k.lower():
                hits.append(k)
    for k in hits[:60]:
        print(f"[mapdiag]   found: {k}")
    return next((k for k in hits if k.endswith("docked_nr4a3.sdf")), hits[0] if hits else None)


def main() -> int:
    import sagemaker
    s3 = boto3.client("s3")
    bucket = sagemaker.Session().default_bucket()
    key = _find_sdf(s3, bucket)
    if not key:
        print(f"[mapdiag] no docked_nr4a3.sdf under {CANDIDATE_PREFIXES} in s3://{bucket}/ — set MAP_PREFIXES")
        return 1
    tmp = os.path.join(tempfile.gettempdir(), "docked_nr4a3.sdf")
    s3.download_file(bucket, key, tmp)
    print(f"[mapdiag] docked SDF: s3://{bucket}/{key}")
    all_names = [m.GetProp("_Name") for m in Chem.SDMolSupplier(tmp, removeHs=False)
                 if m is not None and m.HasProp("_Name")]
    print(f"[mapdiag] SDF records ({len(all_names)}): {all_names[:20]}")

    repaired = {}
    for lig in EDGE:
        smi = rb.SMILES.get(lig)
        print(f"\n[mapdiag] === {lig}  expected_SMILES={smi}")
        try:
            raw = R._sdf_mol(tmp, lig, smi, Chem)
        except SystemExit as e:
            print(f"[mapdiag]   _sdf_mol ABORT: {e}")
            return 2
        rawH = Chem.RemoveHs(Chem.Mol(raw)).GetNumHeavyAtoms()
        fixed = R._repair_pose(raw, smi, Chem)
        fixedH = Chem.RemoveHs(Chem.Mol(fixed)).GetNumHeavyAtoms()
        frags = Chem.GetMolFrags(Chem.RemoveHs(Chem.Mol(fixed)))
        print(f"[mapdiag]   record heavy atoms raw={rawH} -> repaired={fixedH}; fragments after repair={len(frags)}")
        print(f"[mapdiag]   repaired canonical SMILES: {Chem.MolToSmiles(Chem.RemoveHs(Chem.Mol(fixed)))}")
        if len(frags) > 1:
            print(f"[mapdiag]   *** repaired mol is FRAGMENTED ({len(frags)} pieces) — pose-repair is the bug ***")
        repaired[lig] = Chem.RemoveHs(Chem.Mol(fixed))

    a, b = repaired[EDGE[0]], repaired[EDGE[1]]
    for label, kw in (("strict(ring)", dict(completeRingsOnly=True, ringMatchesRingOnly=True)),
                      ("loose", dict())):
        m = rdFMCS.FindMCS([a, b], timeout=30, **kw)
        print(f"\n[mapdiag] rdFMCS {label}: common_atoms={m.numAtoms} common_bonds={m.numBonds} "
              f"canceled={m.canceled}\n           smarts={m.smartsString}")
    print(f"\n[mapdiag] READ: heavy atoms {a.GetNumHeavyAtoms()}/{b.GetNumHeavyAtoms()}; a healthy congeneric edge "
          f"should share ~{min(a.GetNumHeavyAtoms(), b.GetNumHeavyAtoms()) - 1} atoms. If rdFMCS is large but the "
          f"leg logged n_mapped=1, the collapse is in openfe/LOMAP (escalate to mode=smoke with these ligands); if "
          f"rdFMCS is tiny or a mol fragmented, pose-repair/_sdf_mol is the bug.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
