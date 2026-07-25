#!/usr/bin/env python3
"""CI-side operations for the LANE-13 paralogue MD ensembles: status, reap, collect, stop.

WHY THE STATUS BOARD IS A PROGRESS CHECK, NOT A LIVENESS PING. A rented Vast box can sit up with a dead
container or an idle GPU and look perfectly healthy — that failure mode has bitten this repo three times on the
ternary lane. So `status` reports, per leg, the PHASE marker, its AGE, and the tail of the host log, and it
reports the biased-ns counter the job writes, so two consecutive polls can be compared for ADVANCE. An instance
being up is never reported as progress.

WHY THE REAP LIVES HERE AND NOT ON THE HOST. `VAST_API_KEY` is never forwarded to a community host (it can
spend the account's credit). The host stops its own GPU billing key-free by exiting its container; only CI,
which holds the key, can DESTROY the exited instance. So teardown is two-layer by design and this is the
control-plane half.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tarfile
import tempfile
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gpu_backend import _vast_request  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
LABEL_PREFIX = "nr4a-pdyn"
RESULT_PREFIX = os.environ.get("PDYN_RESULT_PREFIX", "nr4a-paralogue-ensemble")
DEFAULT_BUCKET = "sagemaker-us-east-2-646605541856"
# Anti-idle backstop. A leg that has been up this long without a result is destroyed regardless of what it
# claims to be doing: 60 ns metad + 3 x 5 ns release is ~5-6 h on a 4090 and ~11-12 h on a 3090, so 14 h is
# comfortably past any legitimate single-host run and a preempted leg resumes from its checkpoint anyway.
BACKSTOP_H = float(os.environ.get("PDYN_BACKSTOP_H", "14"))


def bucket():
    return os.environ.get("VAST_CKPT_BUCKET") or DEFAULT_BUCKET


def leg_names(targets):
    return [f"{LABEL_PREFIX}-{t.strip().lower()}" for t in targets.split(",") if t.strip()]


def _s3():
    import boto3
    return boto3.client("s3")


def _get(s3, key):
    try:
        return s3.get_object(Bucket=bucket(), Key=key)["Body"].read().decode(errors="replace")
    except Exception:  # noqa: BLE001
        return None


def _exists(s3, key):
    try:
        s3.head_object(Bucket=bucket(), Key=key)
        return True
    except Exception:  # noqa: BLE001
        return False


def instances():
    key = os.environ.get("VAST_API_KEY")
    if not key:
        print("[ops] no VAST_API_KEY — instance half of the board skipped")
        return []
    try:
        insts = _vast_request("GET", "/instances/", key).get("instances", [])
    except Exception as e:  # noqa: BLE001
        print(f"[ops] instance list FAILED ({e}) — refusing to act on instances this pass")
        return None
    return [i for i in insts if (i.get("label") or "").startswith(LABEL_PREFIX)]


def result_key(name):
    target = name.rsplit("-", 1)[-1]
    return f"{RESULT_PREFIX}/{name}/{target}-pocket-ensemble.tar.gz"


def status(targets):
    s3 = _s3()
    print(f"[ops] bucket={bucket()} prefix={RESULT_PREFIX}")
    for name in leg_names(targets):
        base = f"{RESULT_PREFIX}/{name}"
        print(f"\n=== {name}")
        done = _exists(s3, result_key(name))
        print(f"  deliverable in S3: {'YES' if done else 'no'}")
        ph = _get(s3, f"{base}/phase.json")
        if ph:
            try:
                d = json.loads(ph)
                age = None
                try:
                    age = (time.time() - time.mktime(time.strptime(d["utc"], "%Y-%m-%dT%H:%M:%SZ"))
                           + time.timezone) / 60.0
                except Exception:  # noqa: BLE001
                    pass
                print(f"  phase: {d.get('phase')} {d.get('extra')}  "
                      f"(written {d.get('utc')}, {f'{age:.0f} min ago' if age is not None else 'age unknown'})")
            except Exception:  # noqa: BLE001
                print(f"  phase: (unparseable) {ph[:200]}")
        else:
            print("  phase: (none yet)")
        log = _get(s3, f"{base}/run.log")
        if log:
            lines = [ln for ln in log.strip().splitlines() if ln.strip()][-15:]
            for ln in lines:
                print(f"    | {ln[:170]}")
        else:
            print("    | (no run.log yet)")
    insts = instances()
    print("\n=== Vast instances")
    if insts is None:
        return 0
    if not insts:
        print("  (none up)")
    for i in insts:
        up_h = (time.time() - float(i.get("start_date") or time.time())) / 3600.0
        print(f"  {i.get('id')} {i.get('label')} intended={i.get('intended_status')} "
              f"actual={i.get('actual_status')} gpu={i.get('gpu_name')} "
              f"dph={i.get('dph_total')} up={up_h:.2f} h "
              f"gpu_util={i.get('gpu_util')} status_msg={str(i.get('status_msg'))[:80]}")
    return 0


def reap(targets, force=False):
    """Destroy instances whose deliverable is already in S3, whose state is terminal, or which are past the
    anti-idle backstop. Refuses to act if the instance list could not be read."""
    insts = instances()
    if insts is None:
        return 1
    key = os.environ.get("VAST_API_KEY")
    s3 = _s3()
    done_names = {n for n in leg_names(targets) if _exists(s3, result_key(n))}
    for i in insts:
        label = i.get("label") or ""
        iid = i.get("id")
        up_h = (time.time() - float(i.get("start_date") or time.time())) / 3600.0
        actual = i.get("actual_status")
        why = None
        if force:
            why = "force"
        elif label in done_names:
            why = "deliverable already in S3"
        elif actual in ("exited", "stopped") and up_h > 0.25:
            why = f"terminal state {actual}"
        elif up_h > BACKSTOP_H:
            why = f"past the {BACKSTOP_H:.0f} h anti-idle backstop"
        if not why:
            print(f"[ops] keep {iid} {label} (actual={actual}, up {up_h:.2f} h)")
            continue
        print(f"[ops] DESTROY {iid} {label}: {why}")
        try:
            _vast_request("DELETE", f"/instances/{iid}/", key)
        except Exception as e:  # noqa: BLE001
            print(f"[ops]   destroy {iid} failed: {e}")
    return 0


def collect(targets):
    """Pull each finished ensemble tarball and unpack it into results/nr4a{1,2}-pocket-ensemble/, which is the
    layout nr4a_paralogue_dynamics.py reads and the same one the committed NR4A3 ensemble uses."""
    s3 = _s3()
    got = []
    for name in leg_names(targets):
        target = name.rsplit("-", 1)[-1]
        k = result_key(name)
        if not _exists(s3, k):
            print(f"[ops] {name}: no deliverable yet at s3://{bucket()}/{k}")
            continue
        dest = os.path.join(REPO, "results", f"{target}-pocket-ensemble")
        os.makedirs(dest, exist_ok=True)
        with tempfile.TemporaryDirectory() as td:
            tgz = os.path.join(td, "e.tar.gz")
            subprocess.run(["aws", "s3", "cp", f"s3://{bucket()}/{k}", tgz, "--only-show-errors"], check=True)
            with tarfile.open(tgz) as tf:
                # the tarball holds frames/<ensemble>/fp_*/frame.pdb + release_summary.json
                tf.extractall(td)
            src = os.path.join(td, "frames")
            n = 0
            for ens in sorted(os.listdir(src)) if os.path.isdir(src) else []:
                sd = os.path.join(src, ens)
                dd = os.path.join(dest, ens)
                os.makedirs(dd, exist_ok=True)
                for fr in sorted(os.listdir(sd)):
                    os.makedirs(os.path.join(dd, fr), exist_ok=True)
                    fp = os.path.join(sd, fr, "frame.pdb")
                    if os.path.exists(fp):
                        with open(fp, "rb") as a, open(os.path.join(dd, fr, "frame.pdb"), "wb") as b:
                            b.write(a.read())
                        n += 1
            rs = os.path.join(td, "release_summary.json")
            if os.path.exists(rs):
                with open(rs) as a, open(os.path.join(dest, "release_summary.json"), "w") as b:
                    b.write(a.read())
            print(f"[ops] {name}: unpacked {n} frame PDBs into {os.path.relpath(dest, REPO)}")
            got.append({"target": target, "n_frames": n})
    print(json.dumps({"collected": got}, indent=1))
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("action", choices=["status", "reap", "collect", "stop"])
    ap.add_argument("--targets", default="NR4A1,NR4A2")
    a = ap.parse_args()
    if a.action == "status":
        return status(a.targets)
    if a.action == "reap":
        return reap(a.targets)
    if a.action == "stop":
        return reap(a.targets, force=True)
    return collect(a.targets)


if __name__ == "__main__":
    raise SystemExit(main())
