#!/usr/bin/env python
"""Spot-safe checkpoint/commit/restore for openmmtools MultiState (RBFE / any HREX) MD.

WHY THIS EXISTS
---------------
Running an OpenFE 1.12 RBFE GPU leg on AWS SageMaker managed SPOT, we found the leg
RE-EQUILIBRATES from scratch on every preemption and never converges. Root cause (proven
2026-07-15 + confirmed by an external review):
  1. OpenFE's HybridTopologyMultiStateSimulationUnit._run_simulation runs, when
     sampler._iteration == 0, `minimize()` + `equilibrate()` BEFORE production. openmmtools'
     `equilibrate()` does NOT increment _iteration and writes sampler states only ONCE at the
     end (back to iteration 0) — and that final write updates coords but NOT the
     replica<->thermodynamic-state assignments (openmmtools #759), so it isn't even a
     consistent restart frame. => a preemption anywhere in the ~1.5 h equilibration restores
     _iteration==0 and re-equilibrates. This is the dominant failure.
  2. openmmtools DOES flush NetCDF during production (write_last_iteration -> sync()), so the
     files are locally consistent at iteration boundaries. But SageMaker's checkpoint sync
     across a PAIR of live NetCDF files gives no cross-file transaction, and a naive 5-min
     timer-copy can race the writer (copy .nc, writer advances, copy .chk -> mismatched pair).

THE FIX (this module implements B + C; the A/D orchestration lives in the driver)
  * Drive the sampler in CHUNKS that end exactly on a full-checkpoint boundary (run_to_target).
  * At each boundary the writer is QUIESCENT: sync, make an immutable LOCAL copy, VALIDATE it
    (read the actual frame — not file size), then upload to VERSIONED/immutable keys and write
    a COMMIT MANIFEST LAST. An interrupted generation with no manifest is ignored on restore.
  * On startup, restore the NEWEST VALID COMMITTED snapshot before opening any reporter; never
    infer progress from YAML / mtime / size / file-existence / read_last_iteration alone.

Backends: LocalCommitStore (CPU tests, $0) and S3CommitStore (production). Identical logic.
boto3 import is lazy so the CPU path needs no AWS.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import tempfile
import time
import uuid
from pathlib import Path


# --------------------------------------------------------------------------------------------
# integrity helpers
# --------------------------------------------------------------------------------------------
def sha256_file(path: Path, block: int = 8 * 1024 * 1024) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        while True:
            b = fh.read(block)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def fsync_file(path: Path) -> None:
    with open(path, "rb") as fh:
        os.fsync(fh.fileno())


def _sampler_iteration(sampler) -> int:
    """public .iteration if present, else the private counter."""
    it = getattr(sampler, "iteration", None)
    if isinstance(it, int):
        return it
    return int(sampler._iteration)


def validate_reporter_pair(nc_path: Path, chk_path: Path, expected_iteration: int,
                           checkpoint_interval: int) -> dict:
    """Prove a (.nc, .chk) pair is a matched, resumable checkpoint AT expected_iteration by
    READING the actual frame — never by file size (HDF5/NetCDF updates in place). Returns a
    manifest dict; raises on any inconsistency."""
    import netCDF4
    from openmmtools import multistate

    if checkpoint_interval and expected_iteration % checkpoint_interval:
        raise ValueError(f"expected_iteration {expected_iteration} not a checkpoint boundary "
                         f"(interval {checkpoint_interval})")
    with netCDF4.Dataset(nc_path, "r") as anc, netCDF4.Dataset(chk_path, "r") as cnc:
        a_uuid = str(getattr(anc, "UUID", ""))
        c_uuid = str(getattr(cnc, "UUID", ""))
        if a_uuid and c_uuid and a_uuid != c_uuid:
            raise RuntimeError(f"analysis/checkpoint UUID mismatch: {a_uuid} != {c_uuid}")
        chk_frames = len(cnc.dimensions["iteration"]) if "iteration" in cnc.dimensions else -1

    rep = multistate.MultiStateReporter(str(nc_path), open_mode="r",
                                        checkpoint_storage=chk_path.name)
    try:
        ana_it = rep.read_last_iteration(last_checkpoint=False)
        res_it = rep.read_last_iteration(last_checkpoint=True)
        if res_it != expected_iteration:
            raise RuntimeError(f"resume (checkpoint) iteration {res_it} != expected "
                               f"{expected_iteration} (analysis last={ana_it})")
        # the important check: actually READ the frame, proving it exists + is consistent.
        sstates = rep.read_sampler_states(iteration=expected_iteration)
        sidx = rep.read_replica_thermodynamic_states(iteration=expected_iteration)
        rep.read_energies(iteration=expected_iteration)
        if sstates is None:
            raise RuntimeError("checkpoint sampler-state frame is missing")
        if len(sstates) != len(sidx):
            raise RuntimeError(f"replica count mismatch: {len(sstates)} states vs {len(sidx)} "
                               "state-indices (openmmtools #759 inconsistency signature)")
    finally:
        rep.close()
    return {
        "iteration": int(expected_iteration),
        "analysis_last_iteration": int(ana_it),
        "reporter_uuid": a_uuid,
        "checkpoint_frames": int(chk_frames),
        # RECORD the checkpoint cadence the pair was committed at (2026-07-21). The .chk only holds FULL
        # checkpoint frames on THIS grid, so a later resume MUST advance/commit on the SAME interval or it
        # tears the pair (analysis .nc one interval ahead of the .chk). Persisting it lets restore/resume
        # derive the single authoritative interval from the committed file instead of an env var that can
        # differ across VMs. Additive field — validate's equality semantics are unchanged.
        "checkpoint_interval": int(checkpoint_interval) if checkpoint_interval else 0,
        "analysis_size": int(nc_path.stat().st_size),
        "checkpoint_size": int(chk_path.stat().st_size),
        "analysis_sha256": sha256_file(nc_path),
        "checkpoint_sha256": sha256_file(chk_path),
        "analysis_name": nc_path.name,
        "checkpoint_name": chk_path.name,
    }


def read_checkpoint_interval(nc_path, chk_path=None):
    """Return the checkpoint cadence BAKED INTO an existing openmmtools reporter pair (the single
    physical truth for where full .chk frames live), or None if it can't be read.

    WHY THIS EXISTS (2026-07-21 root cause). openmmtools writes a full checkpoint frame to the .chk
    only every `checkpoint_interval` iterations, and that interval is fixed when the .nc is CREATED.
    Our resume path opened the reporter WITHOUT an explicit interval (so it silently inherited the
    file's, e.g. 40) but drove `run_to_target`/`commit` off the ENV interval (e.g. 20, the default
    when RBFE_PROD_CKPT_ITERS wasn't applied on a given VM). At an off-grid boundary (…540 on a
    40-grid file) the .chk's last full frame lagged the .nc by one interval → validate_reporter_pair
    raised `resume iteration 520 != expected 540`, permanently blocking re-dispatch. The fix derives
    THE interval from the committed file and uses it for the reporter, run_to_target, AND commit.

    Primary source is the openmmtools reporter property (exactly what a resume actually uses); the raw
    netCDF attribute is a version-robust fallback."""
    from pathlib import Path as _P
    nc_path = _P(nc_path)
    chk_path = _P(chk_path) if chk_path is not None else None
    # 1) authoritative: the openmmtools reporter itself (reads the persisted interval on open)
    try:
        from openmmtools import multistate
        kw = {}
        if chk_path is not None:
            kw["checkpoint_storage"] = chk_path.name
        rep = multistate.MultiStateReporter(str(nc_path), open_mode="r", **kw)
        try:
            ci = getattr(rep, "checkpoint_interval", None)
            if ci:
                return int(ci)
        finally:
            rep.close()
    except Exception:  # noqa: BLE001
        pass
    # 2) fallback: the raw netCDF attribute (openmmtools stores it on both files as a global attr)
    try:
        import netCDF4
        for p in (chk_path, nc_path):
            if p is None:
                continue
            with netCDF4.Dataset(str(p), "r") as ds:
                for attr in ("checkpoint_interval", "CheckpointInterval"):
                    if hasattr(ds, attr):
                        v = int(getattr(ds, attr))
                        if v:
                            return v
                for g in ds.groups.values():
                    if hasattr(g, "checkpoint_interval"):
                        v = int(g.checkpoint_interval)
                        if v:
                            return v
    except Exception:  # noqa: BLE001
        pass
    return None


def effective_interval(manifest, nc_path=None, chk_path=None, fallback=None):
    """The single authoritative checkpoint interval for a committed generation: the value recorded in
    its manifest if present, else derived from the file, else `fallback`. Used by restore + resume so
    the reporter, run_to_target and commit all agree on ONE interval per committed leg."""
    if manifest:
        mi = manifest.get("checkpoint_interval")
        if mi:
            return int(mi)
    got = read_checkpoint_interval(nc_path, chk_path) if nc_path is not None else None
    if got:
        return int(got)
    return fallback


# --------------------------------------------------------------------------------------------
# commit stores (versioned, immutable generations; manifest written LAST = the commit point)
# --------------------------------------------------------------------------------------------
class _BaseCommitStore:
    MANIFEST = "COMMITTED.json"

    def _gen_prefix(self, phase: str, iteration: int, generation: str) -> str:
        return f"{phase}/iter-{iteration:08d}/{generation}"

    def commit(self, phase: str, iteration: int, nc_path: Path, chk_path: Path,
               checkpoint_interval: int) -> dict:
        """Snapshot the (quiescent) pair to a temp dir, VALIDATE, then persist data objects
        first and the manifest LAST. Returns the manifest."""
        manifest = None
        with tempfile.TemporaryDirectory(dir=str(nc_path.parent)) as td:
            td = Path(td)
            snap_nc = td / nc_path.name
            snap_chk = td / chk_path.name
            shutil.copy2(nc_path, snap_nc)
            shutil.copy2(chk_path, snap_chk)
            fsync_file(snap_nc)
            fsync_file(snap_chk)
            v = validate_reporter_pair(snap_nc, snap_chk, iteration, checkpoint_interval)
            generation = uuid.uuid4().hex
            manifest = {"schema": 1, "phase": phase, "generation": generation, **v}
            self._persist(phase, iteration, generation, snap_nc, snap_chk, manifest)
        return manifest

    def _persist(self, phase, iteration, generation, snap_nc, snap_chk, manifest):
        raise NotImplementedError

    def list_committed(self, phase: str) -> list:
        """[(iteration, generation, manifest_dict)] for generations that HAVE a manifest,
        newest-iteration first then newest-generation first."""
        raise NotImplementedError

    def fetch(self, phase: str, iteration: int, generation: str, dest_dir: Path) -> tuple:
        """Download/copy the pair into dest_dir; return (nc_path, chk_path)."""
        raise NotImplementedError

    def restore_latest(self, phases, workspace: Path, checkpoint_interval: int):
        """Try phases in order; for each, newest generation first, validate the fetched pair,
        and on success move it into `workspace` (named per the manifest). Returns
        (phase, iteration, nc_path, chk_path) or None. Never trusts a generation without a
        manifest; falls back through generations on any validation failure.

        The pair is validated against ITS OWN committed interval (manifest, else the file), not the
        passed `checkpoint_interval` — that arg is only a last-resort fallback for pre-2026-07-21
        generations that recorded no interval and predate the attribute being readable. This keeps a
        VM whose env interval differs from the committed file's from spuriously rejecting (or
        mis-accepting) a valid generation at an off-env-grid boundary."""
        for phase in phases:
            for iteration, generation, man in self.list_committed(phase):
                with tempfile.TemporaryDirectory(dir=str(workspace)) as td:
                    td = Path(td)
                    try:
                        nc_p, chk_p = self.fetch(phase, iteration, generation, td)
                        ci = effective_interval(man, nc_p, chk_p, fallback=checkpoint_interval)
                        validate_reporter_pair(nc_p, chk_p, iteration, ci)
                    except Exception as e:  # noqa: BLE001
                        print(f"[restore] {phase} iter {iteration} gen {generation[:8]} "
                              f"REJECTED: {e!r}", flush=True)
                        continue
                    dst_nc = workspace / man["analysis_name"]
                    dst_chk = workspace / man["checkpoint_name"]
                    shutil.copy2(nc_p, dst_nc)
                    shutil.copy2(chk_p, dst_chk)
                    print(f"[restore] {phase} iter {iteration} gen {generation[:8]} OK (interval={ci}) -> "
                          f"{dst_nc.name}, {dst_chk.name}", flush=True)
                    return phase, iteration, dst_nc, dst_chk
        return None


class LocalCommitStore(_BaseCommitStore):
    """Filesystem-backed commit store (CPU tests, $0)."""

    def __init__(self, base: Path):
        self.base = Path(base)
        self.base.mkdir(parents=True, exist_ok=True)

    def _persist(self, phase, iteration, generation, snap_nc, snap_chk, manifest):
        gdir = self.base / self._gen_prefix(phase, iteration, generation)
        gdir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(snap_nc, gdir / snap_nc.name)
        shutil.copy2(snap_chk, gdir / snap_chk.name)
        # manifest LAST — its presence is the commit signal.
        (gdir / self.MANIFEST).write_text(json.dumps(manifest, sort_keys=True))

    def list_committed(self, phase: str) -> list:
        root = self.base / phase
        out = []
        if not root.is_dir():
            return out
        for iterdir in root.iterdir():
            if not iterdir.name.startswith("iter-"):
                continue
            it = int(iterdir.name.split("iter-")[1])
            for gdir in iterdir.iterdir():
                man = gdir / self.MANIFEST
                if man.is_file():
                    out.append((it, gdir.name, json.loads(man.read_text())))
        out.sort(key=lambda x: (x[0], x[1]), reverse=True)
        return out

    def fetch(self, phase, iteration, generation, dest_dir):
        gdir = self.base / self._gen_prefix(phase, iteration, generation)
        man = json.loads((gdir / self.MANIFEST).read_text())
        nc = dest_dir / man["analysis_name"]
        chk = dest_dir / man["checkpoint_name"]
        shutil.copy2(gdir / man["analysis_name"], nc)
        shutil.copy2(gdir / man["checkpoint_name"], chk)
        return nc, chk


class S3CommitStore(_BaseCommitStore):
    """S3-backed commit store. Uses a DISTINCT prefix from SageMaker's checkpoint_s3_uri so
    native sync is never the source of truth."""

    def __init__(self, bucket: str, base_prefix: str):
        import boto3
        self.s3 = boto3.client("s3")
        self.bucket = bucket
        self.base_prefix = base_prefix.rstrip("/")

    def _key(self, *parts) -> str:
        return "/".join([self.base_prefix, *parts])

    def _persist(self, phase, iteration, generation, snap_nc, snap_chk, manifest):
        gp = self._gen_prefix(phase, iteration, generation)
        self.s3.upload_file(str(snap_nc), self.bucket, self._key(gp, snap_nc.name),
                            ExtraArgs={"Metadata": {"sha256": manifest["analysis_sha256"],
                                                    "iteration": str(iteration), "phase": phase}})
        self.s3.upload_file(str(snap_chk), self.bucket, self._key(gp, snap_chk.name),
                            ExtraArgs={"Metadata": {"sha256": manifest["checkpoint_sha256"],
                                                    "iteration": str(iteration), "phase": phase}})
        # manifest LAST.
        self.s3.put_object(Bucket=self.bucket, Key=self._key(gp, self.MANIFEST),
                           Body=json.dumps(manifest, sort_keys=True).encode(),
                           ContentType="application/json")

    def list_committed(self, phase: str) -> list:
        out = []
        paginator = self.s3.get_paginator("list_objects_v2")
        pref = self._key(phase) + "/"
        for page in paginator.paginate(Bucket=self.bucket, Prefix=pref):
            for o in page.get("Contents", []):
                if o["Key"].endswith(self.MANIFEST):
                    body = self.s3.get_object(Bucket=self.bucket, Key=o["Key"])["Body"].read()
                    man = json.loads(body)
                    # .../<phase>/iter-XXXXXXXX/<generation>/COMMITTED.json
                    parts = o["Key"].split("/")
                    it = int(parts[-3].split("iter-")[1])
                    gen = parts[-2]
                    out.append((it, gen, man))
        out.sort(key=lambda x: (x[0], x[1]), reverse=True)
        return out

    def fetch(self, phase, iteration, generation, dest_dir):
        gp = self._gen_prefix(phase, iteration, generation)
        man = json.loads(self.s3.get_object(Bucket=self.bucket,
                                            Key=self._key(gp, self.MANIFEST))["Body"].read())
        nc = dest_dir / man["analysis_name"]
        chk = dest_dir / man["checkpoint_name"]
        self.s3.download_file(self.bucket, self._key(gp, man["analysis_name"]), str(nc))
        self.s3.download_file(self.bucket, self._key(gp, man["checkpoint_name"]), str(chk))
        return nc, chk


class GCSCommitStore(_BaseCommitStore):
    """Google Cloud Storage-backed commit store — the GCP-provider analog of S3CommitStore, so a
    spot-safe RBFE leg run on a preemptible GCE L4 checkpoints/resumes exactly like on AWS. Auth is
    keyless: google-cloud-storage uses Application Default Credentials, which on a GCE VM with the
    cloud-platform scope resolve to the attached service account (no HMAC keys). Same versioned,
    manifest-written-LAST commit contract as the S3 store."""

    def __init__(self, bucket: str, base_prefix: str):
        from google.cloud import storage  # lazy — only the GCP path needs it
        self._bucket = storage.Client().bucket(bucket)
        self.bucket_name = bucket
        self.base_prefix = base_prefix.rstrip("/")

    def _key(self, *parts) -> str:
        return "/".join([self.base_prefix, *parts])

    def _persist(self, phase, iteration, generation, snap_nc, snap_chk, manifest):
        gp = self._gen_prefix(phase, iteration, generation)
        b_nc = self._bucket.blob(self._key(gp, snap_nc.name))
        b_nc.metadata = {"sha256": manifest["analysis_sha256"], "iteration": str(iteration), "phase": phase}
        b_nc.upload_from_filename(str(snap_nc))
        b_chk = self._bucket.blob(self._key(gp, snap_chk.name))
        b_chk.metadata = {"sha256": manifest["checkpoint_sha256"], "iteration": str(iteration), "phase": phase}
        b_chk.upload_from_filename(str(snap_chk))
        # manifest LAST — its presence is the commit signal (an interrupted upload has no manifest).
        self._bucket.blob(self._key(gp, self.MANIFEST)).upload_from_string(
            json.dumps(manifest, sort_keys=True), content_type="application/json")

    def list_committed(self, phase: str) -> list:
        out = []
        pref = self._key(phase) + "/"
        for blob in self._bucket.list_blobs(prefix=pref):
            if blob.name.endswith(self.MANIFEST):
                man = json.loads(blob.download_as_bytes())
                parts = blob.name.split("/")        # .../<phase>/iter-XXXXXXXX/<generation>/COMMITTED.json
                it = int(parts[-3].split("iter-")[1])
                gen = parts[-2]
                out.append((it, gen, man))
        out.sort(key=lambda x: (x[0], x[1]), reverse=True)
        return out

    def fetch(self, phase, iteration, generation, dest_dir):
        gp = self._gen_prefix(phase, iteration, generation)
        man = json.loads(self._bucket.blob(self._key(gp, self.MANIFEST)).download_as_bytes())
        nc = dest_dir / man["analysis_name"]
        chk = dest_dir / man["checkpoint_name"]
        self._bucket.blob(self._key(gp, man["analysis_name"])).download_to_filename(str(nc))
        self._bucket.blob(self._key(gp, man["checkpoint_name"])).download_to_filename(str(chk))
        return nc, chk


# --------------------------------------------------------------------------------------------
# writer-controlled barrier: run in checkpoint-aligned chunks, commit at each boundary
# --------------------------------------------------------------------------------------------
def run_to_target(sampler, reporter, target_iteration: int, checkpoint_interval: int,
                  on_boundary, log=print) -> None:
    """Advance `sampler` to target_iteration, stopping ONLY on full-checkpoint boundaries; at
    each boundary the sampler is quiescent and `on_boundary(iteration)` is called to snapshot +
    commit. target_iteration must be a checkpoint multiple. Raises if the sampler makes no
    progress at a boundary (guards against silent stalls)."""
    if checkpoint_interval and target_iteration % checkpoint_interval:
        raise ValueError(f"target {target_iteration} not a multiple of checkpoint_interval "
                         f"{checkpoint_interval}")
    while _sampler_iteration(sampler) < target_iteration:
        cur = _sampler_iteration(sampler)
        nxt = min(((cur // checkpoint_interval) + 1) * checkpoint_interval, target_iteration)
        _t0 = time.time()
        sampler.run(n_iterations=nxt - cur)
        now = _sampler_iteration(sampler)
        # PER-ITERATION WALL TIME (the compute-feasibility number): this chunk advanced (now-cur) sampler
        # iterations across all λ-windows on this GPU. Logged every chunk so a live SSH tail reads the real
        # throughput directly, without waiting for a full run or inferring from checkpoint timestamps.
        _dn = max(now - cur, 1)
        _dt = time.time() - _t0
        log("[timing] %d iters in %.0fs = %.1fs/iter (%.2f iters/min) at iteration %d/%d"
            % (now - cur, _dt, _dt / _dn, 60.0 * _dn / _dt if _dt else 0.0, now, target_iteration))
        if now == cur:
            if getattr(sampler, "is_completed", False):
                break
            raise RuntimeError(f"sampler made no progress at iteration {cur}")
        if checkpoint_interval and now % checkpoint_interval:
            raise RuntimeError(f"stopped at non-checkpoint iteration {now}")
        reporter.sync()          # run() already synced via write_last_iteration; explicit here.
        on_boundary(now)         # writer is quiescent — safe to snapshot the pair.
        log(f"[barrier] committed checkpoint at iteration {now}/{target_iteration}")
