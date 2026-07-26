#!/usr/bin/env python3
"""HOST-SIDE driver for a matched NR4A paralogue conformer ensemble (metadynamics -> unbiased release ->
frame export -> S3), resume-safe on a preemptible Vast host.

WHY A DRIVER AND NOT A BASH PIPELINE. Three things here are easy to get silently wrong in shell and are the
difference between a resumable leg and a lost one:

  1. **`nr4a3_metad.NS` is the segment length to ADD, not a target.** A naive re-dispatch with `NS=60` on a
     checkpoint that already holds 60 ns runs a SECOND 60 ns. The remaining work is computed here from the
     manifest AND from the trajectory's own frame count (an interrupted segment advances HILLS and the DCD but
     never writes the manifest, so the manifest alone under-reports and would re-run work already done).
  2. **Continuous upload, at two cadences.** The repo's standing rule is that a job whose runtime you are
     estimating must upload checkpoints AS THEY ARE WRITTEN — a default end-of-job upload loses everything on a
     preemption. The restart set (checkpoint/state/HILLS/COLVAR/manifest) is small and syncs every 2 min; the
     trajectory is hundreds of MB and syncs every 10 min, because S3 has no append and each sync re-uploads the
     whole growing file.
  3. **The phases are separately resumable.** metad and release keep their own checkpoint directories, so a
     preemption during release never re-runs metad.

Everything scientific lives in `nr4a3_metad.py` (unchanged, the SAME module that produced the NR4A3 ensemble)
and `nr4a_paralogue_release.py`. This file only sequences them and moves bytes.
"""
from __future__ import annotations

import argparse
import json
import os
import struct
import subprocess
import sys
import threading
import time

HERE = os.path.dirname(os.path.abspath(__file__))

CKPT = os.environ.get("CKPT_DIR", "/work/ckpt")
CHECKPOINT_URI = os.environ.get("CHECKPOINT_URI", "")
RESULT_S3 = os.environ.get("RESULT_S3", "")
FRAME_PS = 50.0     # DCDReporter interval in nr4a3_metad / nr4a_paralogue_release: 25000 steps x 2 fs


def sh(cmd, **kw):
    print(f"[job] $ {' '.join(cmd)}", flush=True)
    return subprocess.run(cmd, **kw)


def mark(phase, extra=None):
    print(f"[job] PHASE {phase} {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())} {extra or ''}", flush=True)
    if RESULT_S3:
        body = json.dumps({"phase": phase, "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                           "extra": extra})
        p = subprocess.run(["aws", "s3", "cp", "-", f"{RESULT_S3}/phase.json"],
                           input=body.encode(), capture_output=True)
        if p.returncode:
            print(f"[job] phase upload failed: {p.stderr.decode()[:300]}", flush=True)


def dcd_n_frames(path):
    """Frame count from a DCD header, without loading the trajectory. OpenMM's DCDFile rewrites this field on
    every write, so it is the cheapest honest measure of how far an INTERRUPTED segment actually got.

    Returns 0 for a missing/short/unparseable file — the caller then falls back to the manifest, which is the
    conservative direction (it may re-run work, never skip it)."""
    try:
        if not os.path.exists(path) or os.path.getsize(path) < 16:
            return 0
        with open(path, "rb") as fh:
            head = fh.read(16)
        if head[4:8] != b"CORD":
            return 0
        # little-endian first; if it looks absurd try big-endian (DCD is endian-ambiguous by design)
        n = struct.unpack("<i", head[8:12])[0]
        if n < 0 or n > 10 ** 7:
            n = struct.unpack(">i", head[8:12])[0]
        return max(0, n)
    except Exception as e:  # noqa: BLE001
        print(f"[job] dcd_n_frames({path}) failed: {e}", flush=True)
        return 0


def metad_done_ns(metad_dir):
    """Biased ns already accumulated: the larger of the manifest's cumulative_ns and the trajectory's own
    frame count x 50 ps. PURE apart from the two file reads."""
    man = 0.0
    p = os.path.join(metad_dir, "metad_manifest.json")
    if os.path.exists(p):
        try:
            man = float(json.load(open(p)).get("cumulative_ns", 0.0))
        except Exception:  # noqa: BLE001
            man = 0.0
    frames = dcd_n_frames(os.path.join(metad_dir, "nr4a3-lbd-metad.dcd"))
    return max(man, frames * FRAME_PS / 1000.0)


def release_done_ns(rel_dir, n_rep):
    """Unbiased ns completed across the release replicas, from each replica's own progress marker."""
    tot = 0.0
    for r in range(n_rep):
        p = os.path.join(rel_dir, f"release_rep{r}.progress.json")
        if os.path.exists(p):
            try:
                tot += float(json.load(open(p)).get("ns_done", 0.0))
            except Exception:  # noqa: BLE001
                pass
    return tot


class Heartbeat(threading.Thread):
    """Publish LIVE progress every `period_s`, not just at phase boundaries.

    WHY THIS IS NOT COSMETIC. A metadynamics segment is 20 ns and takes over an hour, so a phase marker
    written only at segment boundaries would leave the progress signature UNCHANGED for that whole hour — and
    the watch's stall detector, which fires after 6 unchanged ticks (18 min), would raise a false STALL on a
    perfectly healthy leg. Worse, the opposite error is the one this repo actually keeps paying for: a marker
    that never changes is indistinguishable from a dead container. So the heartbeat reads the metadynamics
    trajectory's own frame count (cheap: a 16-byte header read, no trajectory load) and the release replicas'
    progress markers, and publishes real ns.
    """

    def __init__(self, metad_dir, rel_dir, n_rep, phase_getter, period_s=120):
        super().__init__(daemon=True)
        self.metad_dir, self.rel_dir, self.n_rep = metad_dir, rel_dir, n_rep
        self.phase_getter, self.period_s = phase_getter, period_s
        self.stop = threading.Event()

    def run(self):
        while not self.stop.wait(self.period_s):
            try:
                ph = self.phase_getter()
                extra = {"live": True}
                if ph == "metad":
                    extra["done_ns"] = round(metad_done_ns(self.metad_dir), 3)
                elif ph == "release":
                    extra["done_ns"] = round(release_done_ns(self.rel_dir, self.n_rep), 3)
                mark(ph, extra)
            except Exception as e:  # noqa: BLE001 — a heartbeat must never kill the science
                print(f"[hb] {e}", flush=True)


class Syncer(threading.Thread):
    """Continuous upload at two cadences. Daemon so it can never hold the process open."""

    def __init__(self, local, uri, small_s=120, full_s=600):
        super().__init__(daemon=True)
        self.local, self.uri, self.small_s, self.full_s = local, uri, small_s, full_s
        self.stop = threading.Event()
        self.last_full = 0.0

    def _sync(self, full):
        cmd = ["aws", "s3", "sync", self.local, self.uri, "--only-show-errors"]
        if not full:
            cmd += ["--exclude", "*.dcd"]
        r = subprocess.run(cmd, capture_output=True)
        if r.returncode:
            print(f"[sync] {'full' if full else 'small'} failed: {r.stderr.decode()[:300]}", flush=True)

    def run(self):
        if not self.uri:
            return
        while not self.stop.wait(self.small_s):
            full = (time.time() - self.last_full) >= self.full_s
            self._sync(full)
            if full:
                self.last_full = time.time()

    def final(self):
        self.stop.set()
        if self.uri:
            self._sync(True)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--target", default=os.environ.get("TARGET", "NR4A1"))
    ap.add_argument("--metad-ns", type=float, default=float(os.environ.get("METAD_NS", "60")))
    ap.add_argument("--release-ns", type=float, default=float(os.environ.get("RELEASE_NS", "5")))
    ap.add_argument("--n-rep", type=int, default=int(os.environ.get("N_REP", "3")))
    ap.add_argument("--target-rg", default=os.environ.get("TARGET_RG", "0.717"))
    ap.add_argument("--n-export", default=os.environ.get("N_EXPORT", "25"))
    ap.add_argument("--seed", default=os.environ.get("SEED", "1"))
    ap.add_argument("--segment-ns", type=float, default=float(os.environ.get("SEGMENT_NS", "20")),
                    help="max biased ns per metad subprocess call; several segments per job is fine and "
                         "bounds how much a crashed segment can cost")
    args = ap.parse_args(argv)

    metad_dir = os.path.join(CKPT, "metad")
    rel_dir = os.path.join(CKPT, "release")
    os.makedirs(metad_dir, exist_ok=True)
    os.makedirs(rel_dir, exist_ok=True)

    # ---- resume: pull whatever a previous attempt left in the object store ---------------------------
    if CHECKPOINT_URI and os.environ.get("RESUME", "1") == "1":
        mark("resume_download")
        sh(["aws", "s3", "sync", CHECKPOINT_URI, CKPT, "--only-show-errors"])
        print(f"[job] resumed {sum(len(f) for _, _, f in os.walk(CKPT))} file(s) into {CKPT}", flush=True)

    syncer = Syncer(CKPT, CHECKPOINT_URI)
    syncer.start()
    phase = {"now": "start"}
    hb = Heartbeat(metad_dir, rel_dir, args.n_rep, lambda: phase["now"])
    hb.start()
    env0 = dict(os.environ)
    env0.pop("PYTHONPATH", None)          # never let a base-image site-packages shadow the conda env
    env0["TARGET"] = args.target

    try:
        # ---- phase 1: well-tempered metadynamics on the HOMOLOGOUS cryptic pocket --------------------
        while True:
            done = metad_done_ns(metad_dir)
            todo = args.metad_ns - done
            phase["now"] = "metad"
            mark("metad", {"done_ns": round(done, 2), "target_ns": args.metad_ns})
            if todo <= 0.05:
                print(f"[job] metad already at {done:.2f}/{args.metad_ns} ns — skipping", flush=True)
                break
            seg = min(args.segment_ns, todo)
            env = dict(env0)
            env.update({"NS": f"{seg:.3f}", "SEED": str(args.seed), "OUTPUT_DIR": metad_dir})
            r = sh([sys.executable, os.path.join(HERE, "nr4a3_metad.py")], env=env)
            if r.returncode != 0:
                mark("metad_failed", {"rc": r.returncode, "done_ns": round(metad_done_ns(metad_dir), 2)})
                return r.returncode
            if metad_done_ns(metad_dir) <= done + 1e-6:
                mark("metad_stalled", {"done_ns": round(done, 2)})
                return 3                          # no progress: fail loudly rather than spin on the meter
        syncer._sync(True)

        # ---- phase 2: unbiased release replicas + frame export ---------------------------------------
        phase["now"] = "release"
        mark("release", {"done_ns": round(release_done_ns(rel_dir, args.n_rep), 3),
                         "target_ns": args.release_ns * args.n_rep})
        env = dict(env0)
        env.update({"NS": str(args.release_ns), "N_REP": str(args.n_rep),
                    "TARGET_RG": str(args.target_rg), "N_EXPORT": str(args.n_export),
                    "INPUT_DIR": metad_dir, "OUTPUT_DIR": rel_dir, "RESUME_DIR": rel_dir,
                    "RUN_TAG": "release"})
        r = sh([sys.executable, os.path.join(HERE, "nr4a_paralogue_release.py")], env=env)
        if r.returncode != 0:
            mark("release_failed", {"rc": r.returncode})
            return r.returncode

        # ---- phase 3: package + upload the deliverable ----------------------------------------------
        phase["now"] = "package"
        mark("package")
        frames = os.path.join(rel_dir, "frames")
        tgz = os.path.join(CKPT, f"{args.target.lower()}-pocket-ensemble.tar.gz")
        sh(["tar", "czf", tgz, "-C", rel_dir, "frames", "release_summary.json"])
        if RESULT_S3:
            sh(["aws", "s3", "cp", tgz, f"{RESULT_S3}/{os.path.basename(tgz)}", "--only-show-errors"])
            sh(["aws", "s3", "cp", os.path.join(rel_dir, "release_summary.json"),
                f"{RESULT_S3}/release_summary.json", "--only-show-errors"])
            traj = os.path.join(rel_dir, "traj")
            if os.path.isdir(traj):
                sh(["aws", "s3", "sync", traj, f"{RESULT_S3}/traj", "--only-show-errors"])
        n_frames = sum(1 for _r, _d, f in os.walk(frames) for x in f if x == "frame.pdb")
        mark("done", {"n_frame_pdbs": n_frames, "tarball": os.path.basename(tgz)})
        print(f"[job] DONE — {n_frames} frame PDBs exported for {args.target}", flush=True)
        return 0
    finally:
        hb.stop.set()
        syncer.final()


if __name__ == "__main__":
    raise SystemExit(main())
