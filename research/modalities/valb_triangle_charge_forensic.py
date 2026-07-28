#!/usr/bin/env python3
# =============================================================================================================
# WHY TWO CLOSURE-TRIANGLE LEGS DIED WHILE THEIR SIBLINGS RAN — read from the two SDFs themselves
# =============================================================================================================
# THE OBSERVATION (measured 2026-07-27, `task=collect` run 30317810456, 8:37 PM ET). Four triangle legs were
# rented at 7:51 PM ET. Both `calib_lo_to_lo2` legs — the ternary AND the binary arm, two different hosts, two
# different GPU classes — died at 7:59 PM ET with the SAME exception, eight minutes in:
#
#   nr4a3_ternary_fep.py:474  ligA = openfe.SmallMoleculeComponent.from_rdkit(molA)
#   gufe/components/explicitmoleculecomponent.py:137  _check_partial_charges
#   ValueError: Incorrect number of partial charges: 109  were provided for 110 atoms
#
# while `calib_hi_to_lo2__ternary` (46055595) reached warmup/64 on the same lane, same mode, same timestep.
#
# ⛔ THE PART THAT MAKES THIS WORTH A FILE RATHER THAN A COMMIT MESSAGE. The $0 ATOM-MAP GATE calls
# `_build_components` — the exact function that raised — and it PASSED at 7:51 PM ET ("every leg's atom map
# measured complete at the production budget", run 30315113060). A gate cannot be green on the same call that
# kills the host eight minutes later unless the gate and the host are reading DIFFERENT BYTES. They are:
#
#   the gate reads   <STAGE_CACHE>/<leg>/ligands.sdf   — written on CPU by the prime task
#   the host reads   <PE_CACHE>/<leg>/ligands.sdf      — `run_ternary_leg.sh` step 2 copies the RELAXED
#                                                        ligands.sdf over the staged one before the engine runs
#
# So this reads BOTH SDFs for BOTH the dead legs and the live ones, reports the `atom.dprop.PartialCharge`
# property on every record beside that record's atom count, and then runs the production `_build_components`
# against each — which turns "the gate passed and the host died" into a measured difference between two files.
#
# It also dumps the FULL `run.log` each unit uploaded to S3 (`collect` prints a filtered head plus a 5-line
# tail, which is what hid the traceback behind an innocuous `committed=none/0`).
#
# $0: reads only. It never rents, never nudges, never destroys.
# =============================================================================================================
from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# The gufe property name is not a guess: gufe's `_check_partial_charges` reads exactly this key, and the
# error text this file exists to explain is that method's f-string. One name, one home.
CHARGE_PROP = "atom.dprop.PartialCharge"


# ---------------------------------------------------------------------------------- part A: S3, stdlib+boto3
def _s3():
    import boto3
    return boto3.client("s3")


def _split(uri):
    rest = uri[len("s3://"):]
    b, _, k = rest.partition("/")
    return b, k


def dump_logs(mode, tail=0):
    """Print each unit's FULL uploaded run.log (or its last `tail` lines). $0, read-only."""
    import ternary_vast_launch as tv
    s3 = _s3()
    out = []
    for leg, seed, direction in tv.units_for(mode):
        dt, wdt = tv.resolve_timesteps(mode)
        uid = tv.unit_id(leg, seed, direction, dt, wdt, mode)
        b, k = _split(tv.result_prefix_for(tv.DEFAULT_BUCKET, uid))
        rec = {"unit": uid, "log_bytes": None, "status": None}
        for name in ("run.log", "leg.json"):
            try:
                o = s3.get_object(Bucket=b, Key=f"{k}/{name}")
                body = o["Body"].read().decode("utf-8", "replace")
            except Exception as e:  # noqa: BLE001
                print(f"[forensic] {uid}: no {name} ({type(e).__name__})", flush=True)
                continue
            if name == "leg.json":
                try:
                    rec["status"] = json.loads(body).get("status")
                except Exception:  # noqa: BLE001
                    pass
                continue
            rec["log_bytes"] = len(body)
            lines = body.splitlines()
            keep = lines[-tail:] if tail else lines
            print(f"\n========== run.log {uid} ({len(lines)} lines, mtime "
                  f"{o['LastModified'].isoformat()}) ==========", flush=True)
            for ln in keep:
                print("  | " + ln, flush=True)
            # The one line that says whether a leg that DID start is using charges the protocol never
            # assigned. A crash is loud; this is the silent twin and it is the reason to read every log.
            hits = [ln for ln in lines if "partial charge" in ln.lower() or CHARGE_PROP in ln]
            rec["charge_mentions"] = hits
            if hits:
                print(f"  >> CHARGE MENTIONS in {uid}:", flush=True)
                for h in hits:
                    print("     ! " + h, flush=True)
        out.append(rec)
    return out


TREES = ("stage", "asrun")


def fetch_caches(mode, dest):
    """Assemble, side by side, the tree the GATE grades and the tree the HOST actually runs.

    `dest/stage/<leg>/`  = the stage cache alone — what the $0 atom-map gate has been reading.
    `dest/asrun/<leg>/`  = the stage cache with the PRE-EQUIL cache overlaid on top, which is byte-for-byte
                           what `run_ternary_leg.sh` step 2 hands the engine.

    The two tars have DIFFERENT layouts and the onstart script unpacks them differently: the stage tar holds
    `<leg>/...` and extracts at the tree root; the pre-equil tar holds `complex.pdb` + `ligands.sdf` at ITS
    root and extracts INTO the leg directory. Mirroring that exactly is the whole point — a forensic that
    assembled the inputs its own way would be evidence about itself.
    """
    import shutil
    import tarfile
    import ternary_vast_launch as tv
    s3 = _s3()
    found = {}
    for leg, seed, direction in tv.units_for(mode):
        spec = tv.build_jobspec(leg, seed=seed, direction=direction, mode=mode)
        env = getattr(spec, "env", None) or {}
        entry = {}
        stage_root = os.path.join(dest, "stage")
        os.makedirs(stage_root, exist_ok=True)
        tar = os.path.join(dest, f"stage_{leg}.tar")
        b, k = _split(env["STAGE_CACHE"])
        try:
            s3.download_file(b, k, tar)
            with tarfile.open(tar) as tf:
                tf.extractall(stage_root)
            entry["stage"] = os.path.join(stage_root, leg, "ligands.sdf")
            print(f"[forensic] {leg} stage: HIT {env['STAGE_CACHE']}", flush=True)
        except Exception as e:  # noqa: BLE001
            print(f"[forensic] {leg} stage: MISS ({type(e).__name__}) {env['STAGE_CACHE']}", flush=True)
            entry["stage"] = None

        asrun_leg = os.path.join(dest, "asrun", leg)
        os.makedirs(asrun_leg, exist_ok=True)
        if entry.get("stage") and os.path.exists(os.path.dirname(entry["stage"])):
            shutil.copytree(os.path.dirname(entry["stage"]), asrun_leg, dirs_exist_ok=True)
        petar = os.path.join(dest, f"pe_{leg}.tar")
        b, k = _split(env["PE_CACHE"])
        try:
            s3.download_file(b, k, petar)
            with tarfile.open(petar) as tf:
                tf.extractall(asrun_leg)                       # complex.pdb + ligands.sdf OVER the staged ones
            entry["asrun"] = os.path.join(asrun_leg, "ligands.sdf")
            entry["pe_cache"] = "HIT"
            print(f"[forensic] {leg} preequil: HIT {env['PE_CACHE']} — overlaid, this is what the host ran",
                  flush=True)
        except Exception as e:  # noqa: BLE001
            entry["asrun"] = os.path.join(asrun_leg, "ligands.sdf")
            entry["pe_cache"] = "MISS(%s)" % type(e).__name__
            print(f"[forensic] {leg} preequil: MISS {env['PE_CACHE']} — the host relaxed on its own and "
                  f"the SDF it built is not retrievable; `asrun` here equals `stage`", flush=True)
        found[leg] = entry
    return found


# ------------------------------------------------------------- part B: inside the parity image (rdkit+openfe)
def audit_sdf(path):
    """Per-record atom count vs the length of any inherited partial-charge array. This IS the discriminator."""
    from rdkit import Chem
    recs = []
    for i, m in enumerate(Chem.SDMolSupplier(path, removeHs=False)):
        if m is None:
            recs.append({"record": i, "parse": "FAILED"})
            continue
        n_ch = None
        if m.HasProp(CHARGE_PROP):
            n_ch = len(m.GetProp(CHARGE_PROP).split())
        recs.append({"record": i, "name": m.GetProp("_Name") if m.HasProp("_Name") else None,
                     "n_atoms": m.GetNumAtoms(), "n_partial_charges": n_ch,
                     "mismatch": (n_ch is not None and n_ch != m.GetNumAtoms())})
    return recs


def build_from(input_dir, leg_id):
    """Run the production `_build_components` against `input_dir` exactly as the host does. Returns a verdict."""
    os.environ["INPUT_DIR"] = input_dir
    os.environ.setdefault("RBFE_LOMAP_TIME_S", "300")
    import openfe
    from rdkit import Chem
    import nr4a3_ternary_fep as tf
    tf.IN = input_dir
    leg = tf.leg_spec(leg_id)[0]
    endpoints = tf._morph_endpoints(leg)
    try:
        ligA, ligB, _ = tf._build_components(openfe, Chem, leg, "solvent", endpoints)
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "error": "%s: %s" % (type(e).__name__, e)}
    # A build that SUCCEEDS is not automatically clean: if the inherited array happened to be the right
    # LENGTH, gufe accepts it and the leg runs on charges the protocol never assigned.
    got = {}
    for nm, lig in (("A", ligA), ("B", ligB)):
        rd = lig.to_rdkit()
        got[nm] = {"n_atoms": rd.GetNumAtoms(),
                   "carries_partial_charges": rd.HasProp(CHARGE_PROP)}
    return {"ok": True, **got}


def main(argv=None):
    ap = argparse.ArgumentParser(description="$0 forensic: why two closure-triangle legs died at from_rdkit")
    ap.add_argument("--mode", default="triangle")
    ap.add_argument("--logs", action="store_true", help="dump every unit's full uploaded run.log (S3)")
    ap.add_argument("--fetch-caches", metavar="DIR", default=None,
                    help="download+extract the stage AND pre-equil caches side by side under DIR (S3)")
    ap.add_argument("--audit", metavar="DIR", default=None,
                    help="audit the two extracted trees under DIR (needs the parity image)")
    ap.add_argument("--out", default=None)
    a = ap.parse_args(argv)

    report = {"_what": "closure-triangle from_rdkit death: the gate's SDF vs the host's SDF",
              "_why": "the atom-map gate reads the STAGE cache; run_ternary_leg.sh step 2 overwrites "
                      "ligands.sdf with the PRE-EQUIL one before the engine runs, so the gate is "
                      "structurally blind to anything pre-equilibration introduces.",
              "mode": a.mode, "charge_prop": CHARGE_PROP}

    if a.logs:
        report["logs"] = dump_logs(a.mode)
    if a.fetch_caches:
        report["caches"] = fetch_caches(a.mode, a.fetch_caches)
    if a.audit:
        import ternary_vast_launch as tv
        legs = sorted({leg for leg, _s, _d in tv.units_for(a.mode)})
        per = {}
        for leg in legs:
            entry = {}
            for which in TREES:
                root = os.path.join(a.audit, which)
                sdf = os.path.join(root, leg, "ligands.sdf")
                if not os.path.exists(sdf):
                    entry[which] = {"present": False}
                    continue
                entry[which] = {"present": True, "records": audit_sdf(sdf),
                                "build": build_from(root, leg)}
                print("[forensic] %-32s %-8s records=%s build=%s"
                      % (leg, which, json.dumps(entry[which]["records"]),
                         json.dumps(entry[which]["build"])), flush=True)
            per[leg] = entry
        report["audit"] = per

    if a.out:
        with open(a.out, "w") as fh:
            json.dump(report, fh, indent=2)
            fh.write("\n")
    print("\n[forensic] done.", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
