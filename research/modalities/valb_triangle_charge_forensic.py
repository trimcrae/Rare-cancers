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
import re
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


def _signature(body):
    """The last exception line of a run.log, plus the frame that raised it. PURE, stdlib only.

    A traceback's LAST `Type: message` line is the exception that ended the process; the frame above it is
    where it came from. Together they are a stable key to group dozens of attempts by, which is what turns a
    pile of logs into a before/after comparison.
    """
    lines = body.splitlines()
    exc = None
    frame = None
    for i, ln in enumerate(lines):
        s = ln.strip()
        if s.startswith("File \"") and ", line " in s:
            frame_candidate = s
        else:
            frame_candidate = None
        if frame_candidate:
            _last_frame = frame_candidate
        # An exception line is unindented `Something(Error|Exception|Exit): message` at the end of a block.
        if s and not ln.startswith(" ") and ":" in s:
            head = s.split(":", 1)[0]
            if head.endswith(("Error", "Exception", "Exit")) or head in ("SystemExit", "KeyboardInterrupt"):
                exc = s
                # the innermost frame is the LAST `File "..."` before this line
                for back in range(i - 1, max(-1, i - 60), -1):
                    b = lines[back].strip()
                    if b.startswith("File \"") and ", line " in b:
                        frame = b
                        break
    return exc, frame


def dump_attempts(mode, per_unit=None, full=0, grep=None):
    """Every ARCHIVED attempt of every unit of `mode`: its date, its exception, and the frame that raised it.

    ★ WHY THIS IS THE MEASUREMENT AND A SINGLE LOG IS NOT (2026-07-29). Two of these units have 35 and 49
    archived attempts — every one a separately rented host that died. `strip_foreign_partial_charges` landed
    mid-way through that series, so the archive spans BOTH sides of the fix. Grouping the attempts by
    (exception, frame) and by date therefore answers, from data the hosts themselves wrote, the one question a
    single traceback cannot: did the failure signature CHANGE when the fix landed, or has it been the same
    thing throughout? A signature that changes proves the fix ran and moved the failure; one that does not
    proves the fix never reached this path.

    `full` prints the last N lines of the newest log per distinct signature, so the traceback itself is in the
    record and nobody has to re-fetch it. $0, read-only.
    """
    import ternary_vast_launch as tv
    s3 = _s3()
    out = []
    for leg, seed, direction in tv.units_for(mode):
        dt, wdt = tv.resolve_timesteps(mode)
        uid = tv.unit_id(leg, seed, direction, dt, wdt, mode)
        if per_unit and per_unit not in uid:
            continue
        b, k = _split(tv.result_prefix_for(tv.DEFAULT_BUCKET, uid))
        keys = []
        for page in s3.get_paginator("list_objects_v2").paginate(Bucket=b, Prefix=f"{k}/attempts/"):
            keys.extend(page.get("Contents", []) or [])
        keys.sort(key=lambda o: o["LastModified"])
        rec = {"unit": uid, "n_attempts": len(keys), "by_signature": {}, "attempts": []}
        print(f"\n########## {uid}: {len(keys)} archived attempts ##########", flush=True)
        samples = {}
        for o in keys:
            try:
                body = s3.get_object(Bucket=b, Key=o["Key"])["Body"].read().decode("utf-8", "replace")
            except Exception as e:  # noqa: BLE001
                print(f"  [attempts] unreadable {o['Key']}: {type(e).__name__}", flush=True)
                continue
            exc, frame = _signature(body)
            sig = f"{exc} @@ {frame}"
            when = o["LastModified"].isoformat()
            rec["attempts"].append({"key": o["Key"].rsplit("/", 1)[-1], "utc": when,
                                    "bytes": o["Size"], "exception": exc, "frame": frame})
            g = rec["by_signature"].setdefault(sig, {"n": 0, "first_utc": when, "last_utc": when})
            g["n"] += 1
            g["last_utc"] = when
            samples.setdefault(sig, (o["Key"], body))
            samples[sig] = (o["Key"], body)          # keep the NEWEST example of each signature
            # ★ THE ATTEMPT THAT SUCCEEDED IS NOT THE ONE WITH A TRACEBACK — it is the big one with none, and
            # it is only ever in the ARCHIVE (a later re-dispatch of a done unit exits on the idempotency
            # check and overwrites the live run.log with a two-line stub). Grepping every archived attempt is
            # the only way to read what a COMPLETED leg actually did.
            if grep:
                hits = [l for l in body.splitlines() if re.search(grep, l)]
                if hits:
                    print(f"  [grep] {o['Key'].rsplit('/', 1)[-1]} ({when}, {o['Size']} B)", flush=True)
                    for h in hits[:40]:
                        print("     > " + h[:220], flush=True)
        for sig, g in sorted(rec["by_signature"].items(), key=lambda kv: kv[1]["first_utc"]):
            print(f"  [sig] n={g['n']:<3} {g['first_utc']} .. {g['last_utc']}  {sig}", flush=True)
        if full:
            for sig, (key, body) in samples.items():
                print(f"\n  ---- newest example of {sig}\n  ---- {key}", flush=True)
                for ln in body.splitlines()[-full:]:
                    print("  | " + ln, flush=True)
        out.append(rec)
    return out


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


def charge_census(modes, dest):
    """For EVERY unit of every mode: what charges does the SDF the host actually read carry, at BOTH levels?

    ★ WHY PER-UNIT AND NOT PER-LEG. `PE_CACHE` is keyed by (leg, mode, seed), so the SAME leg has a DIFFERENT
    relaxed SDF per mode and per seed — `calib_hi_to_lo2__ternary_vhl` has one cache for `triangle_smoke` (which
    finished clean) and another for `triangle` (which died). A per-leg census cannot see that difference, and
    that difference is the experiment.

    ★ WHY THE MTIME. A cache written before a fix still carries what the fix removes. The object's
    LastModified is the only thing that says which side of a code change a cached artefact was born on.

    Needs boto3 + rdkit only. $0, read-only.
    """
    import tarfile
    import ternary_vast_launch as tv
    s3 = _s3()
    os.makedirs(dest, exist_ok=True)
    rows = []
    for mode in modes:
        for leg, seed, direction in tv.units_for(mode):
            spec = tv.build_jobspec(leg, seed=seed, direction=direction, mode=mode)
            env = getattr(spec, "env", None) or {}
            dt, wdt = tv.resolve_timesteps(mode)
            uid = tv.unit_id(leg, seed, direction, dt, wdt, mode)
            row = {"unit": uid, "mode": mode, "leg": leg, "seed": seed,
                   "arm": ("ternary" if "ternary" in leg else "binary" if "binary" in leg else "solvent")}
            for which, uri, member in (("stage", env.get("STAGE_CACHE"), os.path.join(leg, "ligands.sdf")),
                                       ("preequil", env.get("PE_CACHE"), "ligands.sdf")):
                info = {"uri": uri}
                root = os.path.join(dest, uid, which)
                os.makedirs(root, exist_ok=True)
                tar = os.path.join(dest, f"{uid}_{which}.tar")
                try:
                    b, k = _split(uri)
                    head = s3.head_object(Bucket=b, Key=k)
                    info["mtime"] = head["LastModified"].isoformat()
                    info["bytes"] = head["ContentLength"]
                    s3.download_file(b, k, tar)
                    with tarfile.open(tar) as tf:
                        tf.extractall(root)
                except Exception as e:  # noqa: BLE001
                    info["cache"] = "MISS(%s)" % type(e).__name__
                    row[which] = info
                    continue
                sdf = os.path.join(root, member)
                info["cache"] = "HIT"
                info["records"] = audit_sdf(sdf) if os.path.exists(sdf) else "NO ligands.sdf IN TAR"
                row[which] = info
            rows.append(row)
            print("[census] " + json.dumps(row), flush=True)
    return rows


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
    """Per-record atom count vs the inherited partial charges — at BOTH levels RDKit carries them.

    ⚠ THE MOLECULE-LEVEL PROPERTY IS ONLY HALF THE STORY (measured 2026-07-28). RDKit's SD parser expands a
    `atom.dprop.<name>` tag into a PER-ATOM property on every atom (`processPropertyLists`, on by default), so
    one SD tag becomes N atom properties, and `mol.ClearProp(CHARGE_PROP)` removes the tag while leaving all N
    of them in place. Reporting only the molecule-level tag therefore says "clean" about a file that is not,
    which is exactly what the first version of this forensic did. One name, one home for the per-atom key:
    `nr4a3_rbfe.PER_ATOM_CHARGE_PROP`.
    """
    from rdkit import Chem
    import nr4a3_rbfe as rbfe
    recs = []
    for i, m in enumerate(Chem.SDMolSupplier(path, removeHs=False)):
        if m is None:
            recs.append({"record": i, "parse": "FAILED"})
            continue
        n_ch = None
        if m.HasProp(CHARGE_PROP):
            n_ch = len(m.GetProp(CHARGE_PROP).split())
        n_atom_ch = sum(1 for a in m.GetAtoms() if a.HasProp(rbfe.PER_ATOM_CHARGE_PROP))
        recs.append({"record": i, "name": m.GetProp("_Name") if m.HasProp("_Name") else None,
                     "n_atoms": m.GetNumAtoms(), "n_partial_charges": n_ch,
                     "n_atoms_carrying_per_atom_charge": n_atom_ch,
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
    #
    # ⚠ AND `HasProp(CHARGE_PROP)` IS NOT THE TEST (2026-07-29). That is the molecule-level array, and this
    # audit reported `carries_partial_charges: 0` for legs that were dying — because the charges that killed
    # them were the PER-ATOM ones, which is the level OpenFF reads. So this now (a) censuses both levels and
    # (b) makes the call that actually raised: `to_openff()`, reached in production from `proto.create` ->
    # `_validate_smcs`. An audit that stops short of the failing call cannot clear a fix.
    import nr4a3_rbfe as rbfe
    got = {}
    for nm, lig in (("A", ligA), ("B", ligB)):
        rd = lig.to_rdkit()
        n_arr, n_atom, n_tot = rbfe.foreign_charge_census(rd)
        rec = {"n_atoms": n_tot, "mol_level_partial_charges": n_arr,
               "atoms_carrying_per_atom_charge": n_atom}
        try:
            off = lig.to_openff()
            pc = getattr(off, "partial_charges", None)
            rec["to_openff"] = "OK"
            # None here is the CORRECT outcome: the protocol assigns its own charges downstream.
            rec["openff_partial_charges_is_none"] = pc is None
        except Exception as e:  # noqa: BLE001
            rec["to_openff"] = "%s: %s" % (type(e).__name__, e)
        got[nm] = rec
    return {"ok": True, **got}


def silent_case_probe(input_dir, leg_id):
    """Does an inherited array of the RIGHT LENGTH actually reach OpenFF as this molecule's charges?

    ⛔ THE QUESTION THIS ANSWERS IS NOT COSMETIC, and it must be MEASURED rather than reasoned about
    (CLAUDE.md §4). The crash only happens when the inherited array is the wrong length. When it is the
    right length — which is exactly the case for `calib_hi_to_lo2__ternary`, the one triangle leg that was
    still billing — gufe raises nothing at all. Whether that leg is scientifically usable then depends on a
    single fact: does the charge survive into `SmallMoleculeComponent.to_openff().partial_charges`, from
    which OpenFE prefers it over generating its own? If it does, that leg ran a charge model
    `_protocol()` never selected, and ΔΔG_coop = ternary − binary stops cancelling the charge model.

    So this deliberately bypasses the strip and reports the raw truth from the SDF record itself.
    """
    from rdkit import Chem
    import openfe
    sdf = os.path.join(input_dir, leg_id, "ligands.sdf")
    out = []
    for i, m in enumerate(Chem.SDMolSupplier(sdf, removeHs=False)):
        if m is None:
            continue
        rec = {"record": i, "n_atoms": m.GetNumAtoms(),
               "n_partial_charges": len(m.GetProp(CHARGE_PROP).split()) if m.HasProp(CHARGE_PROP) else None}
        try:
            comp = openfe.SmallMoleculeComponent.from_rdkit(m)
            off = comp.to_openff()
            pc = getattr(off, "partial_charges", None)
            rec["gufe_accepted"] = True
            rec["openff_partial_charges_is_none"] = pc is None
            if pc is not None:
                rec["first_three"] = [float(x.m) if hasattr(x, "m") else float(x) for x in list(pc)[:3]]
        except Exception as e:  # noqa: BLE001
            rec["gufe_accepted"] = False
            rec["error"] = "%s: %s" % (type(e).__name__, e)
        out.append(rec)
        print("[forensic] SILENT-CASE %-32s %s" % (leg_id, json.dumps(rec)), flush=True)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="$0 forensic: why two closure-triangle legs died at from_rdkit")
    # COMMA-SEPARATED, because the discriminating comparison is ACROSS lanes. The closure triangle and the
    # valB_mini replicates die the same way and their binary arms do not; a forensic that can only see one
    # mode at a time cannot put the two side by side, and the contrast is the evidence.
    ap.add_argument("--mode", default="triangle")
    ap.add_argument("--logs", action="store_true", help="dump every unit's full uploaded run.log (S3)")
    ap.add_argument("--attempts", action="store_true",
                    help="group EVERY archived attempt of every unit by (exception, raising frame) and date "
                         "— the before/after test across a code change. $0, read-only.")
    ap.add_argument("--attempts-full", type=int, default=0, metavar="N",
                    help="with --attempts, also print the last N lines of the newest log per signature")
    ap.add_argument("--attempts-grep", default=None, metavar="REGEX",
                    help="with --attempts, print every archived attempt's lines matching REGEX. This is how "
                         "you read a leg that SUCCEEDED: its log is in the archive, never in run.log.")
    ap.add_argument("--charge-census", metavar="DIR", default=None,
                    help="per-UNIT (mode,leg,seed) census of BOTH charge levels in the stage cache and the "
                         "pre-equil cache the host actually ran, with each cache object's mtime. rdkit+boto3 "
                         "only — no openfe, so it runs on a bare runner in ~2 min.")
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

    modes = [m for m in (a.mode or "").split(",") if m.strip()]

    if a.logs:
        report["logs"] = [rec for m in modes for rec in dump_logs(m)]
    if a.attempts:
        report["attempts"] = [rec for m in modes
                              for rec in dump_attempts(m, full=a.attempts_full, grep=a.attempts_grep)]
    if a.charge_census:
        report["charge_census"] = charge_census(modes, a.charge_census)
    if a.fetch_caches:
        report["caches"] = fetch_caches(modes[0], a.fetch_caches)
    if a.audit:
        import ternary_vast_launch as tv
        legs = sorted({leg for leg, _s, _d in tv.units_for(modes[0])})
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
                if which == "asrun":
                    entry[which]["silent_case"] = silent_case_probe(root, leg)
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
