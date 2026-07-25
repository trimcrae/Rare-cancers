#!/usr/bin/env python3
"""
NR-V04 covalent feasibility panel — S3 RESULT FORENSICS (read-only).

THE QUESTION THIS ANSWERS. The panel's 18 endpoint-MD legs ran and their readouts landed, but the E3/target
chain split was positional and selected Elongin C, so R1/R2/R3 describe the wrong interface
(nrv04-cofold-chain-forensics-2026-07-24.md). The physics is not in dispute — only the analysis. So:

    can the corrected R1/R2/R3 be recomputed from what was PERSISTED, at $0, without re-running any MD?

That is decided by ONE fact: does the bucket hold per-frame all-atom coordinates (a trajectory), or only
already-reduced scalars computed against the wrong chain pair? This script settles it from the real objects —
keys, byte sizes, mtimes — not from reading the driver. Reading the driver is a hypothesis; the listing is the
diagnosis (CLAUDE.md §4).

It is strictly READ-ONLY: list_objects_v2 + get_object. It never writes to, deletes from, or launches anything.

Usage (CI, with AWS creds):
    python nrv04_result_forensics.py --bucket $VAST_CKPT_BUCKET
"""
from __future__ import annotations

import json
import os
import sys

# Extensions that could carry a MULTI-FRAME trajectory, i.e. the only thing that would make a $0 recomputation
# of R1/R2/R3 possible. Anything else in the prefix is a single frame or a derived scalar.
TRAJECTORY_SUFFIXES = (".dcd", ".xtc", ".trr", ".nc", ".netcdf", ".h5", ".hdf5", ".mdcrd", ".dtr", ".tng", ".arc")

# Single-frame / derived artifacts the driver is known to persist, and what each one is worth for a recompute.
CLASSES = {
    "leg_result": ("leg_*.json", "final per-leg readouts ONLY (R1/R2/R3 already reduced against the chain split "
                                 "that was used) — no coordinates"),
    "ckpt_state": ("ckpt_*.state.xml", "OpenMM serialized state = ONE frame (the last checkpoint); deleted by "
                                       "_rm_ckpt when a leg finishes cleanly"),
    "ckpt_json": ("ckpt_*.ckpt.json", "accumulated readout arrays — per-frame CONTACT COUNTS and interface RMSDs "
                                      "for the split in use, plus target-Lys Nz coords for that split; NOT all-atom"),
    "built_system": ("built_*.system.xml", "the OpenMM System (forces/parameters) — no trajectory"),
    "built_cif": ("built_*.solv.cif", "the solvated topology + the PRE-MINIMIZATION starting coordinates = ONE frame"),
    "built_meta": ("built_*.built.json", "build metadata (atom counts, charge method, reactive Cys)"),
    "phase": ("phase.txt", "progress marker"),
    "runlog": ("run.log", "streamed stdout"),
    "trajectory": ("|".join(TRAJECTORY_SUFFIXES), "MULTI-FRAME COORDINATES — the only artifact that would permit "
                                                  "a $0 recomputation"),
    "other": ("", "unclassified"),
}


def classify(key: str) -> str:
    base = key.rsplit("/", 1)[-1]
    low = base.lower()
    if low.endswith(TRAJECTORY_SUFFIXES):
        return "trajectory"
    if base.startswith("leg_") and base.endswith(".json"):
        return "leg_result"
    if base.startswith("ckpt_") and base.endswith(".state.xml"):
        return "ckpt_state"
    if base.startswith("ckpt_") and base.endswith(".ckpt.json"):
        return "ckpt_json"
    if base.startswith("built_") and base.endswith(".system.xml"):
        return "built_system"
    if base.startswith("built_") and base.endswith(".solv.cif"):
        return "built_cif"
    if base.startswith("built_") and base.endswith(".built.json"):
        return "built_meta"
    if base == "phase.txt":
        return "phase"
    if base.endswith(".log"):
        return "runlog"
    return "other"


def list_prefix(s3, bucket, prefix):
    """Every object under `prefix`, with size + LastModified. Paginated."""
    out, tok = [], None
    while True:
        kw = {"Bucket": bucket, "Prefix": prefix}
        if tok:
            kw["ContinuationToken"] = tok
        r = s3.list_objects_v2(**kw)
        for o in r.get("Contents", []):
            out.append({"key": o["Key"], "bytes": o["Size"],
                        "last_modified": o["LastModified"].isoformat()})
        if not r.get("IsTruncated"):
            break
        tok = r["NextContinuationToken"]
    return out


def _unit_of(key, prefix):
    rest = key[len(prefix):].lstrip("/")
    return rest.split("/")[0] if "/" in rest else "(root)"


def survey(s3, bucket, prefix):
    """Full classified inventory of one result prefix + the recompute verdict it implies."""
    prefix = prefix.rstrip("/") + "/"
    objs = list_prefix(s3, bucket, prefix)
    for o in objs:
        o["klass"] = classify(o["key"])
        o["unit"] = _unit_of(o["key"], prefix)
    by_class = {}
    for o in objs:
        c = by_class.setdefault(o["klass"], {"n": 0, "bytes": 0, "example": None})
        c["n"] += 1
        c["bytes"] += o["bytes"]
        if c["example"] is None:
            c["example"] = o["key"]
    units = sorted({o["unit"] for o in objs})
    per_unit = {}
    for u in units:
        per_unit[u] = sorted({o["klass"] for o in objs if o["unit"] == u})

    n_traj = by_class.get("trajectory", {}).get("n", 0)
    verdict = {
        "trajectory_objects_found": n_traj,
        "zero_dollar_recompute_possible": bool(n_traj),
        "why": ("multi-frame coordinate files are present, so the corrected readouts can be recomputed"
                if n_traj else
                "NO multi-frame coordinate file exists under this prefix. Every persisted object is either a "
                "SINGLE frame (built_*.solv.cif = pre-minimization start; ckpt_*.state.xml = one checkpoint "
                "frame) or a scalar ALREADY REDUCED against the chain split that was used (leg_*.json; "
                "ckpt_*.ckpt.json holds per-frame contact COUNTS and interface RMSDs, not coordinates). "
                "R1/R2/R3 for a different chain pair require per-frame all-atom positions, which were never "
                "written. Recomputation at $0 is therefore impossible; the MD must be re-run."),
    }
    return {"prefix": prefix, "n_objects": len(objs), "n_units": len(units),
            "by_class": by_class, "class_meanings": {k: v[1] for k, v in CLASSES.items()},
            "per_unit_classes": per_unit, "objects": objs, "recompute_verdict": verdict}


def read_leg_results(s3, bucket, objs):
    """Download every leg_*.json (small) and extract the fields that decide the correction."""
    legs = []
    for o in objs:
        if o["klass"] != "leg_result":
            continue
        try:
            d = json.loads(s3.get_object(Bucket=bucket, Key=o["key"])["Body"].read().decode())
        except Exception as e:  # noqa: BLE001
            legs.append({"key": o["key"], "error": str(e)})
            continue
        meta = d.get("meta") or {}
        rc = meta.get("reactive_cys") or {}
        legs.append({
            "key": o["key"], "last_modified": o["last_modified"],
            "leg_id": d.get("leg_id"), "seed": d.get("seed"), "mode": d.get("mode"),
            "covalent": d.get("covalent"), "mutation": d.get("mutation"),
            # chain_split only exists on legs run AFTER the fix; its absence is itself evidence of vintage.
            "chain_split": d.get("chain_split"),
            "reactive_cys_chain": rc.get("chain"), "reactive_cys_resid": rc.get("resid"),
            "sg_electrophile_dist_A": rc.get("sg_electrophile_dist_A"),
            "n_atoms": meta.get("n_atoms"), "n_frames": d.get("n_frames"),
            "prod_ns": d.get("prod_ns"), "equil_ns": d.get("equil_ns"),
            "timed_ns": d.get("timed_ns"), "ns_per_day": d.get("ns_per_day"),
            "blew_up": d.get("blew_up"), "blow_phase": d.get("blow_phase"),
            "R1": d.get("R1_interface"), "R2": d.get("R2_recruitment"), "R3": d.get("R3_lys"),
        })
    return sorted(legs, key=lambda x: (x.get("leg_id") or "", x.get("seed") if x.get("seed") is not None else -1))


def inspect_checkpoints(s3, bucket, objs, max_n=6):
    """For any SURVIVING ckpt_*.ckpt.json: report which arrays it carries and their LENGTHS — without dumping
    them. This is the one artifact that could conceivably help, so it is inspected rather than assumed."""
    out = []
    cks = [o for o in objs if o["klass"] == "ckpt_json"][:max_n]
    for o in cks:
        try:
            d = json.loads(s3.get_object(Bucket=bucket, Key=o["key"])["Body"].read().decode())
        except Exception as e:  # noqa: BLE001
            out.append({"key": o["key"], "error": str(e)})
            continue
        shape = {}
        for k, v in d.items():
            if isinstance(v, list):
                inner = v[0] if v else None
                shape[k] = {"len": len(v),
                            "element": ("list[%d]" % len(inner)) if isinstance(inner, list) else type(inner).__name__}
            else:
                shape[k] = v
        out.append({"key": o["key"], "bytes": o["bytes"], "last_modified": o["last_modified"], "shape": shape,
                    "carries_all_atom_positions": False,
                    "note": "per_frame_contacts = integer counts; iface_rmsds = floats; lys_frames = Nz "
                            "coordinates of the TARGET-CHAIN lysines ONLY, for whichever chain the split named. "
                            "None of these can be re-derived for a different chain pair."})
    return out


def cofold_census(s3, bucket, prefix, limit=12):
    """Chain census of the co-fold inputs (residue count per chain), to CONFIRM the E3 identity of the inputs a
    re-run would use — the 14-3-3-epsilon-for-Elongin-B defect is exactly this class of bug (verify, don't
    assume). Needs gemmi; degrades to 'gemmi unavailable' rather than failing the whole survey."""
    prefix = prefix.rstrip("/") + "/"
    objs = [o for o in list_prefix(s3, bucket, prefix) if o["key"].endswith(".cif")]
    try:
        import gemmi
    except ImportError:
        return {"prefix": prefix, "n_cifs": len(objs), "error": "gemmi unavailable",
                "cifs": [o["key"] for o in objs[:limit]]}
    from nrv04_covalent_assemble import CONTAMINANT_CHAIN_RESIDUES, E3_CHAIN_RESIDUES, NR4A_LBD_RESIDUES
    rows = []
    for o in sorted(objs, key=lambda x: x["key"])[:limit]:
        local = "/tmp/" + o["key"].replace("/", "_")
        s3.download_file(bucket, o["key"], local)
        st = gemmi.read_structure(local)
        census = []
        for ch in st[0]:
            n = sum(1 for res in ch
                    if (gemmi.find_tabulated_residue(res.name) or None)
                    and gemmi.find_tabulated_residue(res.name).is_amino_acid())
            if n:
                census.append({"chain": ch.name, "residues": n,
                               "role": (CONTAMINANT_CHAIN_RESIDUES.get(n)
                                        or E3_CHAIN_RESIDUES.get(n)
                                        or ("NR4A LBD (frozen construct)" if n == NR4A_LBD_RESIDUES else "?"))})
        contaminated = any(c["residues"] in CONTAMINANT_CHAIN_RESIDUES for c in census)
        rows.append({"key": o["key"], "last_modified": o["last_modified"], "census": census,
                     "contaminated_14_3_3": contaminated,
                     "verdict": "CONTAMINATED — 14-3-3 epsilon where Elongin B belongs" if contaminated
                                else "clean (VHL 213 / EloB 118 / EloC 112 + a 254-residue NR4A LBD)"})
        os.remove(local)
    return {"prefix": prefix, "n_cifs": len(objs), "inspected": rows}


def main(argv=None):
    import argparse
    import boto3
    ap = argparse.ArgumentParser(description="Read-only S3 forensics for the NR-V04 covalent panel.")
    ap.add_argument("--bucket", default=os.environ.get("VAST_CKPT_BUCKET", ""))
    ap.add_argument("--result-prefixes", default="nrv04-covalent-results,nrv04-covalent-results-chainfix")
    ap.add_argument("--cofold-prefixes", default="nrv04-covalent-cofold,nrv04-descriptive-v4,nrv04-descriptive-v3")
    ap.add_argument("--out", default="research/modalities/nrv04-result-forensics.json")
    args = ap.parse_args(argv)
    if not args.bucket:
        raise SystemExit("set --bucket or $VAST_CKPT_BUCKET")

    s3 = boto3.client("s3")
    doc = {"bucket": args.bucket, "question": __doc__.strip().splitlines()[3], "surveys": {}, "cofolds": {}}
    for p in [x for x in args.result_prefixes.split(",") if x]:
        sv = survey(s3, args.bucket, p)
        sv["legs"] = read_leg_results(s3, args.bucket, sv["objects"])
        sv["surviving_checkpoints"] = inspect_checkpoints(s3, args.bucket, sv["objects"])
        doc["surveys"][p] = sv
    for p in [x for x in args.cofold_prefixes.split(",") if x]:
        try:
            doc["cofolds"][p] = cofold_census(s3, args.bucket, p)
        except Exception as e:  # noqa: BLE001
            doc["cofolds"][p] = {"prefix": p, "error": f"{type(e).__name__}: {e}"}

    with open(args.out, "w") as f:
        json.dump(doc, f, indent=2)
    # Console summary — the listing is the evidence, so print the counts that decide the question.
    for p, sv in doc["surveys"].items():
        print(f"\n=== {p} : {sv['n_objects']} objects, {sv['n_units']} units ===", flush=True)
        for k, v in sorted(sv["by_class"].items()):
            print(f"    {k:14s} n={v['n']:4d}  {v['bytes']:>14,d} B   e.g. {v['example']}", flush=True)
        print(f"    VERDICT: $0 recompute possible = {sv['recompute_verdict']['zero_dollar_recompute_possible']}",
              flush=True)
        print(f"    {sv['recompute_verdict']['why']}", flush=True)
        for lg in sv["legs"]:
            print(f"    leg {str(lg.get('leg_id')):18s} s{lg.get('seed')} frames={lg.get('n_frames')} "
                  f"reactive_cys=chain {lg.get('reactive_cys_chain')}:{lg.get('reactive_cys_resid')} "
                  f"({lg.get('sg_electrophile_dist_A')} A)  split={lg.get('chain_split')}  "
                  f"R1={(lg.get('R1') or {}).get('plateau_A')}/{(lg.get('R1') or {}).get('stable')} "
                  f"R2={(lg.get('R2') or {}).get('recruited')} R3={(lg.get('R3') or {}).get('min_A')}", flush=True)
    for p, cf in doc["cofolds"].items():
        print(f"\n=== co-fold {p} ===", flush=True)
        print(json.dumps({k: v for k, v in cf.items() if k != "inspected"}, indent=2), flush=True)
        for r in cf.get("inspected", []):
            print(f"    {r['key']}  {r['verdict']}  {r['census']}", flush=True)
    print(f"\nwrote {args.out}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
