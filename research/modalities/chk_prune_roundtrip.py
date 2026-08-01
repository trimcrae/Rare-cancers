#!/usr/bin/env python3
"""RUNG 1 — CAN A PRUNED `.chk` STILL BE RESUMED FROM? The experiment that decides the incremental-commit
design in `commit-payload-design.md`. Offline, CPU-only, no rental, $0.

★★ THE QUESTION. The design doc measured the O(n²): the openmmtools **checkpoint** file accumulates one
full-coordinate frame per checkpoint interval and every commit re-uploads all of them. **A resume reads only
the LAST frame.** Everything earlier is re-sent forever and never read. So: keep only the last frame.

The load-bearing unknown is whether openmmtools still RESUMES, because its checkpoint reader indexes frames by
`iteration // checkpoint_interval` — a naive "keep one frame" file puts the newest data at index 0 while the
reader looks for it at index 25.

★ THE DESIGN UNDER TEST — PRESERVE THE INDEX, DROP THE BYTES. netCDF-4 is HDF5, and HDF5 allocates storage
per CHUNK, on write. So a pruned file can keep the SAME `iteration` dimension length and materialise ONLY the
final frame's slice: every earlier index stays unwritten, costs nothing, and the reader's arithmetic is
untouched. That is the hypothesis, and it is not obvious — `netCDF4` might materialise fill chunks, the
variable might be contiguous rather than chunked, or `read_last_iteration` might key off the dimension length
rather than the data.

WHAT IS MEASURED, IN THREE PARTS — deliberately separated, because they fail for different reasons:

  A. STORAGE MECHANISM, at the real 5a-KS shape (12 replicas × 147,788 atoms × 3). Does an unwritten chunk
     cost bytes? Includes its own negative control (a CONTIGUOUS layout, where it must NOT save).
  B. RESUME SEMANTICS, on a real 3-replica openmmtools run: prune → `LocalCommitStore.commit` →
     `restore_latest` → `from_storage` → **keep running** → prune → commit → restore → run again. A pruned
     CHAIN, not a single hop, because the steady state is every generation pruned.
  C. NEGATIVE CONTROL on B. The naive prune (last frame rewritten at index 0) must be REJECTED. If the
     harness cannot tell a broken prune from a good one, part B proves nothing and the verdict says so.

⛔ WHAT THIS DELIBERATELY DOES NOT DO. It never touches a live reporter file — everything happens on copies in
a temp dir, exactly where `commit()` already snapshots. It rents nothing. It changes no commit path, and it
does not relax `validate_reporter_pair` or `effective_interval` by a single line: the pruned file has to
satisfy them AS THEY STAND, or the answer is no.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import tempfile
import time
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

# The real 5a-KS checkpoint shape, from `commit-payload-design.md` §1 (its one home). Used only to size the
# storage probe so the mechanism is measured at the scale it has to work at, not at toy scale.
REAL_N_REPLICAS = 12
REAL_N_ATOMS = 147_788


# ★ THE PRUNE ITSELF LIVES IN `chk_prune`, NOT HERE (rule 1: one fact, one home). This module is the
# EXPERIMENT that licenses it; the commit path imports the same functions, so what was proven and what
# runs can never drift apart.
from chk_prune import (  # noqa: E402
    _chunk_for, _copy_scalar, _is_vlen, _itemsize, chk_frame_report, inspect_header, prune_to_last_frame,
)


def empty_prune(src_chk, dst_chk):
    """⚠ NEGATIVE CONTROL #2 — the structure with NO frame at all: every dimension and variable preserved,
    nothing per-iteration written.

    Unambiguous by construction, unlike the index-0 control (which degenerates into the CORRECT prune
    whenever the source happens to hold a single frame). Whatever the reader does with the index, there is
    no data anywhere, so an acceptance here means the validator is reading fill and calling it coordinates."""
    import netCDF4
    with netCDF4.Dataset(str(src_chk), "r") as src, \
            netCDF4.Dataset(str(dst_chk), "w", format="NETCDF4") as dst:
        for name in src.ncattrs():
            dst.setncattr(name, src.getncattr(name))
        for dname, dim in src.dimensions.items():
            dst.createDimension(dname, None if dim.isunlimited() else len(dim))
        for vname, var in src.variables.items():
            nv = dst.createVariable(vname, var.datatype, var.dimensions)
            for a in var.ncattrs():
                if a != "_FillValue":
                    nv.setncattr(a, var.getncattr(a))
            if var.dimensions and var.dimensions[0] == "iteration":
                continue                          # <-- the point: no frame is ever written
            if var.shape:
                nv[...] = var[...]
            else:
                _copy_scalar(var, nv)


def naive_prune(src_chk, dst_chk):
    """⚠ NEGATIVE CONTROL #1 — the obvious-but-wrong prune: a single-frame file with the newest data at
    index 0.

    This is what "just keep the last checkpoint" produces if you do not think about the reader's
    `iteration // checkpoint_interval` arithmetic. It MUST be rejected by `validate_reporter_pair`.

    ⚠ IT IS NOT A VALID CONTROL ON A SINGLE-FRAME SOURCE. If the source holds exactly one frame at index 0,
    "write the last frame at index 0" IS the correct file, and an acceptance proves nothing either way. The
    caller must check `source_frames` before drawing any conclusion — which is why `empty_prune` exists."""
    import netCDF4

    rep = chk_frame_report(src_chk)
    keep = rep["frames_with_data"][-1]
    with netCDF4.Dataset(str(src_chk), "r") as src, \
            netCDF4.Dataset(str(dst_chk), "w", format="NETCDF4") as dst:
        for name in src.ncattrs():
            dst.setncattr(name, src.getncattr(name))
        for dname, dim in src.dimensions.items():
            dst.createDimension(dname, None if dim.isunlimited() else len(dim))
        for vname, var in src.variables.items():
            nv = dst.createVariable(vname, var.datatype, var.dimensions)
            for a in var.ncattrs():
                if a != "_FillValue":
                    nv.setncattr(a, var.getncattr(a))
            if var.dimensions and var.dimensions[0] == "iteration":
                nv[0] = var[keep]                 # <-- the bug under control: newest data at index 0
            elif var.shape:
                nv[...] = var[...]
            else:
                _copy_scalar(var, nv)
    return keep


# ------------------------------------------------------------------------------------------------
# PART A — storage mechanism at the real shape
# ------------------------------------------------------------------------------------------------
def storage_probe(n_frames=6, n_replicas=REAL_N_REPLICAS, n_atoms=REAL_N_ATOMS, workdir=None):
    """Does an UNWRITTEN chunk cost bytes? Measured at the real 5a-KS checkpoint shape, three layouts.

    Carries its own negative control: a CONTIGUOUS variable must NOT save anything, because HDF5 allocates
    contiguous storage up front. If the "saving" showed up there too, it would be an artefact of the
    measurement rather than the mechanism."""
    import netCDF4
    import numpy as np

    tmp = Path(workdir or tempfile.mkdtemp(prefix="chkprobe-"))
    tmp.mkdir(parents=True, exist_ok=True)
    frame = np.random.random_sample((n_replicas, n_atoms, 3)).astype("f4")  # incompressible: conservative
    out = {"n_frames": n_frames, "n_replicas": n_replicas, "n_atoms": n_atoms,
           "bytes_per_frame_raw": int(frame.nbytes)}

    def _write(path, unlimited, per_iter_chunk, frames_to_write):
        with netCDF4.Dataset(str(path), "w", format="NETCDF4") as ds:
            ds.createDimension("iteration", None if unlimited else n_frames)
            ds.createDimension("replica", n_replicas)
            ds.createDimension("atom", n_atoms)
            ds.createDimension("spatial", 3)
            kw = {}
            if per_iter_chunk:
                kw["chunksizes"] = _chunk_for((n_frames, n_replicas, n_atoms, 3), 4)
            v = ds.createVariable("positions", "f4",
                                  ("iteration", "replica", "atom", "spatial"), **kw)
            for i in frames_to_write:
                v[i] = frame
        return os.path.getsize(path)

    allf = list(range(n_frames))
    last = [n_frames - 1]
    t0 = time.time()
    out["all_frames_unlimited"] = _write(tmp / "a_all.nc", True, True, allf)
    out["one_frame_unlimited_chunked"] = _write(tmp / "b_one.nc", True, True, last)
    # NEGATIVE CONTROL: fixed dimension + no chunking request -> netCDF4 stores contiguously
    out["all_frames_contiguous"] = _write(tmp / "c_all.nc", False, False, allf)
    out["one_frame_contiguous"] = _write(tmp / "d_one.nc", False, False, last)
    out["probe_seconds"] = round(time.time() - t0, 1)

    out["shrink_chunked_x"] = round(out["all_frames_unlimited"] / out["one_frame_unlimited_chunked"], 2)
    out["shrink_contiguous_x"] = round(out["all_frames_contiguous"] / out["one_frame_contiguous"], 2)
    out["checks"] = {
        # the mechanism: with per-iteration chunks, dropping n-1 of n frames must save close to n×
        "chunked_saves_about_n_x": out["shrink_chunked_x"] >= 0.7 * n_frames,
        # the control: contiguous storage must NOT save — otherwise the saving is a measurement artefact
        "contiguous_does_NOT_save": out["shrink_contiguous_x"] < 1.2,
    }
    for p in tmp.glob("*.nc"):
        p.unlink()
    return out


# ------------------------------------------------------------------------------------------------
# PART B/C — resume semantics on a real openmmtools run
# ------------------------------------------------------------------------------------------------
def _pruned_copy(chk_path, dest_dir):
    """A pruned copy of `chk_path` under the SAME basename in `dest_dir` — exactly the shape `commit()`
    would produce with the prune wired into its temp-dir snapshot.

    SNAPSHOT FIRST, then prune the snapshot. Reading the live reporter file directly would be a second HDF5
    handle on a file the sampler still owns, and it is also not what the design does: `commit()` copies to a
    temp dir precisely so that a bug here can only produce a bad UPLOAD, never a corrupt running leg."""
    chk_path, dest_dir = Path(chk_path), Path(dest_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=str(dest_dir)) as td:
        snap = Path(td) / chk_path.name
        shutil.copy2(chk_path, snap)
        dst = dest_dir / chk_path.name
        kept = prune_to_last_frame(snap, dst)
    return dst, kept


def resume_semantics(ci=2, target=8, extend_by=2, workdir=None):
    """The real experiment. Build a genuine 3-replica multistate run, prune, commit through the REAL
    `LocalCommitStore.commit`, restore through the REAL `restore_latest`, resume with `from_storage`, then
    keep running and do it a SECOND time — a pruned chain, which is the steady state being proposed."""
    import numpy as np
    from openmm import unit
    from openmmtools.multistate import MultiStateReporter, ReplicaExchangeSampler
    import rbfe_spot_checkpoint as spot
    import rbfe_spot_checkpoint_test as fixture

    def _positions(sampler):
        return [np.array(s.positions.value_in_unit_system(unit.md_unit_system))
                for s in sampler._sampler_states]

    work = Path(workdir or tempfile.mkdtemp(prefix="chkprune-"))
    work.mkdir(parents=True, exist_ok=True)
    out = {"checkpoint_interval": ci, "target": target}
    thermo, sstate, move = fixture._mk_env()

    wnc, wchk = work / "warmup.nc", work / "warmup.chk"
    smp = ReplicaExchangeSampler(mcmc_moves=move, number_of_iterations=target + extend_by)
    smp.create(thermodynamic_states=thermo, sampler_states=sstate,
               storage=fixture._reporter(wnc, ci, wchk.name))
    smp.minimize(max_iterations=5)
    rep = smp._reporter
    spot.run_to_target(smp, rep, target, ci, lambda it: None, log=lambda *a, **k: None)
    out["iteration_reached"] = spot._sampler_iteration(smp)

    # in-memory state at the kill, for a coarse "did we get coordinates or garbage" check. It is NOT the
    # strict comparator: the checkpoint stores float32 while these are float64, so a bit-exact comparison
    # against them would fail for a reason that has nothing to do with pruning. The strict comparator is the
    # UNPRUNED RESUME below, which carries the identical rounding.
    live_pos = _positions(smp)
    truth_idx = np.asarray(smp._replica_thermodynamic_states, dtype=int).tolist()
    del smp, rep                                   # <-- the spot kill

    out["before"] = chk_frame_report(wchk)

    # ---- C. NEGATIVE CONTROLS first: does the harness have any power at all? --------------------
    # Two separate questions per control, kept separate because they had DIFFERENT answers:
    #   (i)  does `validate_reporter_pair` REJECT the broken checkpoint?
    #   (ii) if it were accepted, what would a resume off it actually hand back?
    # (ii) is what says how dangerous an accepted bad prune is; (i) is whether the commit path's safety net
    # would catch it. Both are recorded for BOTH controls — recording (ii) for only one of them is how the
    # zeros-not-fill mechanism stayed hidden for two runs.
    def _control(tag, builder, note):
        cd = work / tag
        cd.mkdir()
        shutil.copy2(wnc, cd / wnc.name)
        builder(wchk, cd / wchk.name)
        out[f"{tag}_report"] = chk_frame_report(cd / wchk.name)
        try:
            spot.validate_reporter_pair(cd / wnc.name, cd / wchk.name, target, ci)
            out[f"{tag}_rejected"] = False
            out[f"{tag}_note"] = note
        except Exception as e:  # noqa: BLE001 — this is the expected path
            out[f"{tag}_rejected"] = True
            out[f"{tag}_error"] = f"{type(e).__name__}: {e}"
        try:
            crep = MultiStateReporter(str(cd / wnc.name), open_mode="r+", checkpoint_storage=wchk.name)
            try:
                out[f"{tag}_last_iteration_checkpoint"] = int(crep.read_last_iteration(last_checkpoint=True))
                cst = crep.read_sampler_states(iteration=target)
                cpos = [np.ma.asarray(spot._positions_array(s)) for s in (cst or [])]
                if cpos:
                    dat = [np.ma.getdata(x) for x in cpos]
                    out[f"{tag}_frame_max_abs_nm"] = float(max(float(np.max(np.abs(x))) for x in dat))
                    out[f"{tag}_frame_all_zero"] = bool(all(not np.any(x) for x in dat))
                    out[f"{tag}_frame_is_masked"] = bool(any(np.ma.getmaskarray(x).any() for x in cpos))
                    out[f"{tag}_frame_is_unusable"] = bool(any(spot.positions_are_unusable(x) for x in cpos))
                else:
                    out[f"{tag}_frame_max_abs_nm"] = None
            finally:
                crep.close()
        except Exception as e:  # noqa: BLE001
            out[f"{tag}_resume_probe_error"] = f"{type(e).__name__}: {e}"

    _control("naive", naive_prune,
             "\u26a0 the index-0 prune VALIDATED \u2014 the reader was handed something it accepted for a "
             "frame that is not at the index it asked for")
    _control("empty", empty_prune,
             "\u26a0 a checkpoint with NO frame anywhere VALIDATED \u2014 the validator is accepting "
             "whatever the reader returns for a missing frame")

    # ---- B. the real round-trip, through the real store -----------------------------------------
    p_chk, kept = _pruned_copy(wchk, work / "pruned")
    out["kept_frame_index"] = kept
    out["after"] = chk_frame_report(p_chk)
    out["shrink_x"] = round(out["before"]["bytes"] / out["after"]["bytes"], 2) if out["after"]["bytes"] else None

    # TWO stores, each holding exactly ONE generation. Separate, so a restore cannot silently pick the
    # unpruned copy and report a pass that never touched a pruned byte — and so the two resumes differ in
    # NOTHING except the prune, which is what makes the coordinate comparison below decisive.
    store = spot.LocalCommitStore(work / "commits-pruned")
    ref_store = spot.LocalCommitStore(work / "commits-unpruned")
    try:
        ref_store.commit("warmup", target, wnc, wchk, ci)
        out["baseline_commit_ok"] = True
    except Exception as e:  # noqa: BLE001
        out.update({"baseline_commit_ok": False, "baseline_error": f"{type(e).__name__}: {e}"})
        return out
    try:
        out["commit_manifest"] = store.commit("warmup", target, wnc, p_chk, ci)
        out["pruned_commit_ok"] = True
    except Exception as e:  # noqa: BLE001
        out.update({"pruned_commit_ok": False, "commit_error": f"{type(e).__name__}: {e}"})
        return out
    out["committed_chk_bytes"] = {"unpruned": out["before"]["bytes"], "pruned": out["after"]["bytes"]}

    # the reference resume: same pipeline, unpruned bytes
    wsr = work / "resume-ref"
    wsr.mkdir()
    ref = ref_store.restore_latest(["warmup"], wsr, ci)
    if ref:
        rrep = MultiStateReporter(str(ref[2]), open_mode="r+", checkpoint_storage=ref[3].name)
        rsmp = ReplicaExchangeSampler.from_storage(rrep)
        ref_pos = _positions(rsmp)
        out["reference_resume_iteration"] = spot._sampler_iteration(rsmp)
        del rsmp, rrep
    else:
        ref_pos = None
        out["reference_resume_iteration"] = None

    ws = work / "resume1"
    ws.mkdir()
    got = store.restore_latest(["warmup"], ws, ci)
    out["restore_ok"] = got is not None
    if not got:
        return out
    _phase, it_restored, r_nc, r_chk = got
    out["restored_iteration"] = int(it_restored)
    out["restored_chk_bytes"] = os.path.getsize(r_chk)
    out["restored_chk_report"] = chk_frame_report(r_chk)
    out["interval_readback"] = spot.read_checkpoint_interval(r_nc, r_chk)
    out["effective_interval"] = spot.effective_interval(out["commit_manifest"], r_nc, r_chk, fallback=None)

    rep2 = MultiStateReporter(str(r_nc), open_mode="r+", checkpoint_storage=r_chk.name)
    smp2 = ReplicaExchangeSampler.from_storage(rep2)
    out["from_storage_iteration"] = spot._sampler_iteration(smp2)
    got_pos = _positions(smp2)
    out["n_replicas"] = len(got_pos)
    # STRICT: pruned resume vs unpruned resume, bit for bit. Anything but 0.0 means the prune changed what
    # comes back — including the fill-value failure mode, which would be enormous rather than subtle.
    out["max_delta_vs_unpruned_resume_nm"] = (
        float(max(np.abs(a - b).max() for a, b in zip(ref_pos, got_pos)))
        if ref_pos is not None and len(ref_pos) == len(got_pos) else None)
    # COARSE: against the live pre-kill state, which differs only by the checkpoint's float32 rounding.
    out["max_delta_vs_live_state_nm"] = (
        float(max(np.abs(a - b).max() for a, b in zip(live_pos, got_pos)))
        if len(got_pos) == len(live_pos) else None)
    out["replica_state_indices_match"] = (
        np.asarray(smp2._replica_thermodynamic_states, dtype=int).tolist() == truth_idx)

    # ---- keep running from the pruned resume, then prune+commit+restore AGAIN (a pruned CHAIN) ----
    def _commit_pruned(it):
        pd = work / f"pruned-{it}"
        pp, _ = _pruned_copy(r_chk, pd)
        store.commit("warmup", it, r_nc, pp, ci)

    try:
        spot.run_to_target(smp2, rep2, target + extend_by, ci, _commit_pruned, log=lambda *a, **k: None)
        out["extended_to"] = spot._sampler_iteration(smp2)
        out["ran_on_from_pruned"] = out["extended_to"] == target + extend_by
    except Exception as e:  # noqa: BLE001
        out.update({"ran_on_from_pruned": False, "extend_error": f"{type(e).__name__}: {e}"})
    del smp2, rep2

    ws2 = work / "resume2"
    ws2.mkdir()
    got2 = store.restore_latest(["warmup"], ws2, ci)
    out["chain_restore_ok"] = got2 is not None and got2[1] == target + extend_by
    if got2:
        out["chain_restored_iteration"] = int(got2[1])
        out["chain_chk_report"] = chk_frame_report(got2[3])
        rep3 = MultiStateReporter(str(got2[2]), open_mode="r+", checkpoint_storage=got2[3].name)
        smp3 = ReplicaExchangeSampler.from_storage(rep3)
        out["chain_from_storage_iteration"] = spot._sampler_iteration(smp3)
        del smp3, rep3

    # ---- does the pruned pair still REJECT a wrong iteration? ------------------------------------
    try:
        spot.validate_reporter_pair(r_nc, r_chk, target - ci, ci)
        out["still_rejects_a_wrong_iteration"] = False
    except Exception:  # noqa: BLE001 — expected
        out["still_rejects_a_wrong_iteration"] = True
    return out


# ------------------------------------------------------------------------------------------------
# PART D — the same prune against a REAL committed 5a-KS pair
# ------------------------------------------------------------------------------------------------
# Part B runs a genuine openmmtools sampler, but a 3-replica implicit-solvent alanine dipeptide is not the
# file the fix has to survive. The real `.chk` is 12 replicas × 147,788 atoms and may carry variables the toy
# does not. This part prunes an ACTUAL committed generation and re-validates it — no sampler, no GPU, $0 —
# so the fresh leg is not the first time the prune meets the real layout.
def pair_targets(listing_lines, uri_prefix, phase="warmup", limit=1, exclude=("_smoke",)):
    """Pick committed generations to prune-test from an `aws s3 ls --recursive`-style key listing.

    LAYOUT-AGNOSTIC, deliberately: it looks for `COMMITTED.json` (the commit point) and lets the manifest
    supply the filenames, the iteration and the interval, rather than constructing a path. A guessed path
    that misses returns "no pairs", which is indistinguishable from "there are none" — the failure mode the
    census workflow already paid for. Pure stdlib, so it is unit-tested without an object store."""
    import re
    pat = re.compile(r"(?P<root>.*/)%s/iter-(?P<it>\d+)/(?P<gen>[0-9a-f]+)/COMMITTED\.json$" % re.escape(phase))
    found = []
    for raw in listing_lines:
        key = raw.split()[-1].strip() if raw.strip() else ""
        m = pat.match(key)
        if not m or any(x in key for x in exclude):
            continue
        root = m.group("root").rstrip("/")
        found.append({"iteration": int(m.group("it")), "generation": m.group("gen"),
                      "label": root.rsplit("/", 1)[-1],
                      "dir_uri": uri_prefix.rstrip("/") + "/" + key.rsplit("/", 1)[0],
                      "manifest_key": key})
    # newest iteration per leg, then the newest few overall — one real pair is enough to answer the question
    best = {}
    for f in found:
        cur = best.get(f["label"])
        if cur is None or f["iteration"] > cur["iteration"]:
            best[f["label"]] = f
    return sorted(best.values(), key=lambda f: -f["iteration"])[:max(1, int(limit))]


def real_pair_probe(gen_dir):
    """Prune a REAL committed generation (a directory holding COMMITTED.json + the pair) and re-validate.

    Reads every parameter from the manifest, so it cannot be run against the wrong iteration or interval by
    a typo in a workflow input."""
    import rbfe_spot_checkpoint as spot
    gen_dir = Path(gen_dir)
    man = json.loads((gen_dir / "COMMITTED.json").read_text())
    nc = gen_dir / man["analysis_name"]
    chk = gen_dir / man["checkpoint_name"]
    it = int(man["iteration"])
    ci = int(man.get("checkpoint_interval") or 0) or spot.read_checkpoint_interval(nc, chk)
    out = {"dir": str(gen_dir), "phase": man.get("phase"), "iteration": it, "interval": ci,
           "analysis_name": nc.name, "checkpoint_name": chk.name}
    try:
        spot.validate_reporter_pair(nc, chk, it, ci)
        out["baseline_validates"] = True
    except Exception as e:  # noqa: BLE001
        out.update({"baseline_validates": False, "baseline_error": f"{type(e).__name__}: {e}",
                    "note": "the UNPRUNED real pair does not validate, so nothing about pruning follows"})
        return out
    out["before"] = chk_frame_report(chk)
    # ⚠ THE PRUNED PAIR GETS ITS OWN DIRECTORY, WITH A COPY OF THE `.nc`. `validate_reporter_pair` opens the
    # reporter as `MultiStateReporter(nc, checkpoint_storage=chk.name)` — a NAME, resolved next to the `.nc`.
    # Pruning into a sibling directory would therefore have validated the UNPRUNED checkpoint sitting beside
    # the original `.nc` and reported a pass that never touched a pruned byte.
    tmp = Path(tempfile.mkdtemp(prefix="realprune-", dir=str(gen_dir.parent)))
    p_nc, p_chk = tmp / nc.name, tmp / chk.name
    shutil.copy2(nc, p_nc)
    t0 = time.time()
    try:
        out["kept_frame_index"] = prune_to_last_frame(chk, p_chk)
    except Exception as e:  # noqa: BLE001
        out.update({"prune_ok": False, "prune_error": f"{type(e).__name__}: {e}"})
        return out
    out["prune_ok"] = True
    out["prune_seconds"] = round(time.time() - t0, 1)
    out["after"] = chk_frame_report(p_chk)
    out["shrink_x"] = round(out["before"]["bytes"] / out["after"]["bytes"], 2) if out["after"]["bytes"] else None
    try:
        spot.validate_reporter_pair(p_nc, p_chk, it, ci)
        out["pruned_validates"] = True
    except Exception as e:  # noqa: BLE001
        out.update({"pruned_validates": False, "pruned_error": f"{type(e).__name__}: {e}"})
    out["interval_readback"] = spot.read_checkpoint_interval(p_nc, p_chk)
    try:
        spot.validate_reporter_pair(p_nc, p_chk, max(0, it - ci), ci)
        out["still_rejects_a_wrong_iteration"] = False
    except Exception:  # noqa: BLE001 — expected
        out["still_rejects_a_wrong_iteration"] = True
    out["checks"] = {
        "real_pruned_pair_validates": bool(out.get("pruned_validates")),
        "real_index_preserved": out["after"]["iteration_dim"] == out["before"]["iteration_dim"],
        "real_only_one_frame_materialised": len(out["after"]["frames_with_data"]) == 1,
        "real_interval_survives": out.get("interval_readback") == ci,
        "real_still_rejects_a_wrong_iteration": bool(out.get("still_rejects_a_wrong_iteration")),
        "real_actually_smaller": bool(out.get("shrink_x") and out["shrink_x"] > 1.5),
    }
    shutil.rmtree(tmp, ignore_errors=True)
    return out


# ------------------------------------------------------------------------------------------------
# verdict
# ------------------------------------------------------------------------------------------------
def resume_checks(b):
    """The named conditions part B has to meet. Pure — testable without netCDF4 or openmmtools."""
    before, after = b.get("before") or {}, b.get("after") or {}
    restored = b.get("restored_chk_report") or {}
    ci = b.get("checkpoint_interval")
    # A toy checkpoint (3 replicas × 22 atoms) is almost entirely netCDF header, so a file-size ratio on it
    # measures the header rather than the prune. Where frames do not dominate, this part only has to show
    # the prune does not GROW the file; the shrink claim is carried by the storage probe and the real pair,
    # both of which are frame-dominated by construction.
    frac = before.get("payload_fraction")
    header_dominated = frac is not None and frac < 0.5
    shrink = b.get("shrink_x") or 0.0
    # ⚠ CONTROL #1 IS ONLY MEANINGFUL ON A MULTI-FRAME SOURCE. "Write the last frame at index 0" IS the
    # correct file when the source holds one frame at index 0, so on such a source an acceptance is not
    # evidence of a blind validator — it is evidence of a degenerate control. Control #2 (no frame at all)
    # has no such degeneracy, which is why the gating check is an OR over the two.
    n_src = len(before.get("frames_with_data") or [])
    naive_is_meaningful = n_src > 1
    controls = [bool(b.get("empty_rejected"))]
    if naive_is_meaningful:
        controls.append(bool(b.get("naive_rejected")))
    return {
        # the harness has power at all
        "a_BROKEN_checkpoint_is_REJECTED": all(controls) and bool(controls),
        # the index arithmetic the reader depends on is untouched
        "iteration_dim_preserved": (after.get("iteration_dim") is not None
                                    and after.get("iteration_dim") == before.get("iteration_dim")),
        "kept_the_LAST_frame": (after.get("frames_with_data") == (before.get("frames_with_data") or [None])[-1:]),
        "only_one_frame_materialised": len(after.get("frames_with_data") or []) == 1,
        # the prune is not a no-op (see `header_dominated` above for why the bar moves)
        "actually_smaller": bool(shrink >= 1.0 if header_dominated else shrink > 1.5),
        # the real commit path accepted it, unmodified
        "real_commit_accepted_it": bool(b.get("pruned_commit_ok")),
        "real_restore_returned_it": bool(b.get("restore_ok")),
        # we resumed from the PRUNED bytes, not from some unpruned copy
        "restored_the_pruned_file": (restored.get("frames_with_data") is not None
                                     and len(restored["frames_with_data"]) == 1),
        "resumed_at_the_right_iteration": b.get("from_storage_iteration") == b.get("target"),
        "did_NOT_reset_to_zero": bool(b.get("from_storage_iteration")),
        # the coordinates came back, not fill values: identical to an UNPRUNED resume of the same run
        "coordinates_identical_to_unpruned_resume": (
            b.get("max_delta_vs_unpruned_resume_nm") is not None
            and b["max_delta_vs_unpruned_resume_nm"] == 0.0),
        "coordinates_are_the_real_state": (b.get("max_delta_vs_live_state_nm") is not None
                                           and b["max_delta_vs_live_state_nm"] < 1e-3),
        "replica_state_indices_match": bool(b.get("replica_state_indices_match")),
        # the interval still reads back, so `effective_interval` stays honest
        "interval_survives": (b.get("interval_readback") == ci and b.get("effective_interval") == ci),
        # a pruned resume can keep running, and the NEXT generation prunes too
        "ran_on_from_a_pruned_resume": bool(b.get("ran_on_from_pruned")),
        "pruned_CHAIN_restores": bool(b.get("chain_restore_ok")),
        "chain_resumed_at_the_right_iteration": (
            b.get("chain_from_storage_iteration") == b.get("chain_restored_iteration")),
        # validation still discriminates
        "still_rejects_a_wrong_iteration": bool(b.get("still_rejects_a_wrong_iteration")),
    }


def verdict(doc):
    """One sentence, and it starts with the word the exit code keys off.

    ⚠ AN ABSENT PART IS NAMED, NEVER ASSUMED PASSED (§4). Part D (the real committed pair) is optional
    because it needs object-store access; when it did not run, the verdict SAYS the real layout is untested
    rather than quietly reading as full coverage."""
    a = (doc.get("storage") or {}).get("checks") or {}
    b = doc.get("resume_checks") or {}
    real = doc.get("real_pairs") or []
    if not b:
        return "INCONCLUSIVE — the resume experiment did not run to a verdict; see `resume`."
    if not b.get("a_BROKEN_checkpoint_is_REJECTED"):
        return ("INCONCLUSIVE — a deliberately-broken checkpoint PASSED validation, so the harness cannot "
                "tell a broken prune from a good one and no conclusion may be drawn from the rest. See "
                "`resume.naive_*` and `resume.empty_*`.")
    rc = {}
    for r in real:
        for k, v in (r.get("checks") or {}).items():
            rc[k] = rc.get(k, True) and bool(v)
    bad = sorted(k for k, v in list(b.items()) + list(a.items()) + list(rc.items()) if not v)
    if bad:
        return ("PRUNING IS NOT SAFE — failed: %s. Fall back to the `.chk` every k commits option (pure "
                "scheduling, no format risk) rather than pushing on the format." % ", ".join(bad))
    scope = ("also verified on %d REAL committed 5a-KS pair(s) (shrink %s)"
             % (len(real), ", ".join(str(r.get("shrink_x")) + "x" for r in real))) if real else \
            ("NOT yet run against a real committed pair — the real 12-replica layout is untested")
    return ("PRUNING IS SAFE — a single-frame `.chk` keeps the reader's index, returns bit-identical "
            "coordinates, is accepted by the UNMODIFIED commit/restore path, resumes at the right iteration, "
            "runs on, and chains. Storage shrinks %sx at the real shape; the test pair shrank %sx; %s."
            % ((doc.get("storage") or {}).get("shrink_chunked_x"),
               (doc.get("resume") or {}).get("shrink_x"), scope))


def run_all(ci=2, target=8, extend_by=2, skip_storage=False, workdir=None, real_dirs=()):
    doc = {"generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    if not skip_storage:
        doc["storage"] = storage_probe(workdir=workdir)
    b = resume_semantics(ci=ci, target=target, extend_by=extend_by, workdir=workdir)
    doc["resume"] = b
    doc["resume_checks"] = resume_checks(b)
    if real_dirs:
        doc["real_pairs"] = [real_pair_probe(d) for d in real_dirs]
    doc["verdict"] = verdict(doc)
    return doc


def _main(argv=None):
    ap = argparse.ArgumentParser(description=(__doc__ or "").split("\n")[0])
    ap.add_argument("--interval", type=int, default=2)
    ap.add_argument("--target", type=int, default=8)
    ap.add_argument("--extend-by", type=int, default=2)
    ap.add_argument("--skip-storage", action="store_true",
                    help="skip part A (the real-shape storage probe writes ~130 MB four times)")
    ap.add_argument("--real-dir", action="append", default=[],
                    help="a directory holding COMMITTED.json + the committed pair; prunes and re-validates it")
    ap.add_argument("--pair-targets", default=None,
                    help="MODE: read an `aws s3 ls --recursive` listing from this file and print pair "
                         "targets as TSV (label<TAB>iteration<TAB>dir_uri). Pure stdlib; runs anywhere.")
    ap.add_argument("--uri-prefix", default="")
    ap.add_argument("--phase", default="warmup")
    ap.add_argument("--limit", type=int, default=1)
    ap.add_argument("--inspect", default=None,
                    help="MODE: print a netCDF file's dimensions + variable inventory and exit (instant)")
    ap.add_argument("--out", default=None)
    a = ap.parse_args(argv)

    if a.inspect:
        print(json.dumps(inspect_header(a.inspect), indent=1, default=str))
        return 0

    if a.pair_targets:
        with open(a.pair_targets) as fh:
            tgts = pair_targets(fh.readlines(), a.uri_prefix, phase=a.phase, limit=a.limit)
        for t in tgts:
            print("%s\t%d\t%s" % (t["label"], t["iteration"], t["dir_uri"]))
        return 0 if tgts else 0     # no targets is not an error — it is a reported absence

    doc = run_all(ci=a.interval, target=a.target, extend_by=a.extend_by, skip_storage=a.skip_storage,
                  real_dirs=a.real_dir)
    print(json.dumps(doc, indent=1, default=str), flush=True)
    # ★ A COMPACT TAIL, because the artifact is not reachable from the dev sandbox (the egress proxy 403s
    # GitHub's artifact blob host) and the full JSON is ~1400 log lines. Everything needed to diagnose a
    # failure has to be inside the last screen of the log.
    r = doc.get("resume") or {}
    print("\n=== SOURCE + CONTROLS ===", flush=True)
    for lbl, key in (("source .chk", "before"), ("good prune", "after"),
                     ("control#1 index-0", "naive_report"), ("control#2 no-frame", "empty_report")):
        rep = r.get(key) or {}
        print("  %-20s dim=%s frames=%s bytes=%s payload_frac=%s"
              % (lbl, rep.get("iteration_dim"), rep.get("frames_with_data"), rep.get("bytes"),
                 rep.get("payload_fraction")), flush=True)
    for tag in ("naive", "empty"):
        for suffix in ("rejected", "error", "note", "last_iteration_checkpoint", "frame_max_abs_nm",
                       "frame_all_zero", "frame_is_masked", "frame_is_unusable", "resume_probe_error"):
            k = f"{tag}_{suffix}"
            if k in r:
                print("  %-34s %s" % (k, str(r[k])[:200]), flush=True)
    print("\n=== CHECKS ===", flush=True)
    for k, v in sorted((doc.get("resume_checks") or {}).items()):
        print("  [%s] %s" % ("PASS" if v else "FAIL", k), flush=True)
    for k, v in sorted(((doc.get("storage") or {}).get("checks") or {}).items()):
        print("  [%s] storage: %s" % ("PASS" if v else "FAIL", k), flush=True)
    for r in doc.get("real_pairs") or []:
        for k, v in sorted((r.get("checks") or {}).items()):
            print("  [%s] %s: %s" % ("PASS" if v else "FAIL", r.get("dir", "?").rsplit("/", 3)[-1], k),
                  flush=True)
    print("\n=== VERDICT ===\n" + doc["verdict"], flush=True)
    if a.out:
        Path(a.out).parent.mkdir(parents=True, exist_ok=True)
        Path(a.out).write_text(json.dumps(doc, indent=1, default=str))
    return 0 if doc["verdict"].startswith("PRUNING IS SAFE") else 1


if __name__ == "__main__":
    raise SystemExit(_main())
