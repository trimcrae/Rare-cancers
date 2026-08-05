#!/usr/bin/env python3
"""KEEPING ONLY THE LAST CHECKPOINT FRAME — the one home of the prune, its arithmetic and its switch.

★★ WHY. `commit-payload-design.md` measured the O(n²): the openmmtools CHECKPOINT accumulates one
full-coordinate frame per checkpoint interval (~49 MiB at the 5a-KS shape) and every commit re-uploads all
of them — 1231.1 MiB per commit by the end of a 1600-iteration warmup, 15.6 GiB across the warmup. **A
resume reads only the LAST frame.** Everything earlier is re-sent forever and never read.

★ THE MECHANISM — PRESERVE THE INDEX, DROP THE BYTES. netCDF-4 is HDF5, and HDF5 allocates storage per
CHUNK, on write. So a pruned file keeps the SAME `iteration` dimension length and materialises only the
final frame's slice: every earlier index stays unwritten, costs nothing, and openmmtools'
`iteration // checkpoint_interval` arithmetic is untouched.

★★ PROVEN BEFORE IT WAS WIRED (GH run 30676071569, $0, no rental). `chk_prune_roundtrip.py` is the
experiment and its verdict is the licence for this module: a pruned pair keeps the reader's index, returns
BIT-IDENTICAL coordinates to an unpruned resume of the same run, is accepted by the UNMODIFIED
commit/restore path, resumes at the right iteration, runs on, and chains — plus 25.88× on a REAL committed
5a-KS pair (1231.1 → 47.6 MiB in ~4 s) and 6.0× at the real shape against a contiguous control at 1.0×.

⛔ IT NEVER TOUCHES A LIVE REPORTER FILE. `prune_snapshot` operates on `commit()`'s temp-dir snapshot, so
the worst a bug here can do is produce a bad UPLOAD — and it validates the pruned file before adopting it,
falling back to the unpruned snapshot if anything at all goes wrong. An optimisation must never be able to
cost a commit.
"""
from __future__ import annotations

import os
import re
import shutil
import tempfile
from pathlib import Path

# ★ DEFAULT OFF. The switch is opt-in so that legs already in flight are provably unaffected by a change
# landed mid-run: nothing prunes until a dispatch explicitly asks for it, which is what makes "new legs
# only" a fact about the code rather than a promise about sequencing.
PRUNE_ENV = "RBFE_PRUNE_CHK"


def prune_enabled(env=None) -> bool:
    """Read at CALL time, never cached at import — so a test or a single dispatch can flip it without the
    value having been frozen by whatever imported this module first."""
    env = os.environ if env is None else env
    return str(env.get(PRUNE_ENV, "")).strip() in ("1", "true", "TRUE", "yes")


# ------------------------------------------------------------------------------------------------
# netCDF variable helpers
#
# ⚠ `netCDF4` IS NOT UNIFORM ACROSS VARIABLE KINDS, and an openmmtools checkpoint contains both kinds.
# For a numeric variable `var.dtype` is a numpy dtype; for a VLEN string variable it is the Python TYPE
# `str`, which has no `.itemsize`, cannot be compressed, and rejects a `chunksizes` request. The first run
# of this experiment (GH 30674942072) died on exactly that, four lines into the prune. These three helpers
# are the one home of that asymmetry.
# ------------------------------------------------------------------------------------------------
def _is_vlen(var):
    dt = getattr(var, "dtype", None)
    return dt is str or dt is bytes or str(dt) in ("str", "<class 'str'>")


#: `[byteorder]kind<bytes>` — numpy's own dtype notation, and the only part of it this needs.
_DTYPE_STR = re.compile(r"^[<>=|]?[a-zA-Z](\d+)$")


def _itemsize(dtype, default=8):
    """Bytes per element, tolerating the non-numpy dtypes netCDF4 returns for VLEN variables.

    ⚠ THE `except Exception` BELOW ALSO CATCHES `ImportError`, WHICH IS NOT WHAT IT WAS WRITTEN FOR.
    It exists for the VLEN `str`/`bytes` case, where size is not fixed and a bound is all the caller
    needs. But where numpy is absent entirely it returned `default` for EVERY dtype, so `"f4"` reported
    8 bytes — and `test_itemsize_survives_a_dtype_that_is_not_a_numpy_dtype` asserts 4. Inert in
    production (netCDF4 requires numpy, so the numpy branch always wins) and wrong everywhere else,
    which is the combination that survives unnoticed: this one did, behind a preflight step that was
    aborting at collection and reporting zero failures.

    So the string form is parsed directly when numpy cannot answer. `default` still covers what it was
    always for — a VLEN type, or a dtype in no recognisable notation.
    """
    try:
        import numpy as np
        return max(1, int(np.dtype(dtype).itemsize))
    except Exception:  # noqa: BLE001 — VLEN str/bytes, or no numpy at all
        m = _DTYPE_STR.match(dtype) if isinstance(dtype, str) else None
        return max(1, int(m.group(1))) if m else default


def _chunking(var):
    try:
        return var.chunking()
    except Exception:  # noqa: BLE001
        return None


def _filters(var):
    try:
        return var.filters() or {}
    except Exception:  # noqa: BLE001
        return {}


def inspect_header(path):
    """Dimensions + variable inventory ONLY — no frame scan, so it is instant even on a 1.2 GiB checkpoint.

    Exists because the first run of this experiment died on a variable kind nobody had enumerated, and died
    before writing any artifact. A header dump costs nothing and is printed BEFORE the experiment, so a crash
    still leaves the evidence needed to diagnose it."""
    import netCDF4
    out = {"path": str(path), "bytes": os.path.getsize(path)}
    with netCDF4.Dataset(str(path), "r") as ds:
        out["global_attrs"] = {a: str(ds.getncattr(a))[:120] for a in ds.ncattrs()}
        out["dimensions"] = {n: {"len": len(d), "unlimited": d.isunlimited()} for n, d in ds.dimensions.items()}
        out["variables"] = {n: {"dims": list(v.dimensions), "dtype": str(v.dtype), "vlen": _is_vlen(v),
                                "shape": list(v.shape), "chunking": str(_chunking(v)),
                                "filters": {k: x for k, x in _filters(v).items() if x not in (False, 0, None)}}
                            for n, v in ds.variables.items()}
        out["groups"] = sorted(ds.groups)
    return out


def _copy_scalar(src_var, dst_var):
    """A 0-d netCDF variable. `assignValue`/`getValue` is the documented route, but it is not defined for
    every datatype, so the indexed form is kept as a fallback rather than letting the whole prune die on a
    one-element variable."""
    try:
        dst_var.assignValue(src_var.getValue())
    except Exception:  # noqa: BLE001
        dst_var[...] = src_var[...]


# ------------------------------------------------------------------------------------------------
# the frame census
# ------------------------------------------------------------------------------------------------
def chk_frame_report(chk_path):
    """What a checkpoint file physically contains: the `iteration` dimension length, and which frames hold
    REAL data rather than fill.

    The distinction is the whole point — a pruned file must report the SAME number of iterations (so the
    reader's index arithmetic is unchanged) while only ONE of them is materialised."""
    import netCDF4
    import numpy as np
    out = {"path": str(chk_path), "bytes": os.path.getsize(chk_path)}
    with netCDF4.Dataset(str(chk_path), "r") as ds:
        out["iteration_dim"] = len(ds.dimensions["iteration"]) if "iteration" in ds.dimensions else None
        v = ds.variables.get("positions")
        out["positions_shape"] = None if v is None else list(v.shape)
        out["positions_chunking"] = None if v is None else str(_chunking(v))
        out["positions_filters"] = None if v is None else {k: val for k, val in (_filters(v) or {}).items()
                                                           if val not in (False, 0, None)}
        # the full variable inventory, because the first run of this experiment died on a variable nobody had
        # looked at (an openmmtools VLEN `str`, whose `dtype` is the Python TYPE and has no `.itemsize`).
        out["variables"] = {n: {"dims": list(vv.dimensions), "dtype": str(vv.dtype),
                                "vlen": _is_vlen(vv), "shape": list(vv.shape)}
                            for n, vv in ds.variables.items()}
        written = []
        if v is not None:
            for i in range(v.shape[0]):
                arr = v[i]
                mask = getattr(arr, "mask", None)
                if mask is not None and bool(np.all(mask)):
                    continue                      # entirely fill -> never written
                if int(np.ma.count(arr)) == 0:
                    continue
                written.append(i)
        out["frames_with_data"] = written
        # IS A BYTE-SHRINK EVEN MEASURABLE ON THIS FILE? A 22-atom toy checkpoint is mostly netCDF header,
        # so a file-size ratio there measures the header, not the prune. Recording the payload fraction lets
        # the checks apply a shrink threshold only where frames actually dominate — rather than either
        # failing a good prune on a toy or waiving the check with no stated reason.
        if v is not None and out["positions_shape"] and len(out["positions_shape"]) > 1:
            per_frame = _itemsize(v.dtype)
            for n in out["positions_shape"][1:]:
                per_frame *= int(n)
            out["positions_frame_bytes"] = int(per_frame)
            out["payload_fraction"] = round(per_frame * max(1, len(written)) / max(1, out["bytes"]), 4)
    return out


def _chunk_for(shape, itemsize, src_chunking=None, budget_bytes=8 << 20):
    """Chunk shape that puts ONE iteration per chunk — the mechanism by which an unwritten frame costs
    nothing — while keeping any single chunk under `budget_bytes`.

    Pure, so it is testable without netCDF4. Prefers the source's own chunking (only overriding dim 0) so the
    pruned file stays as close to what openmmtools wrote as the design allows."""
    if not shape:
        return None
    if isinstance(src_chunking, (list, tuple)) and len(src_chunking) == len(shape):
        cand = [1] + [max(1, int(x)) for x in src_chunking[1:]]
    else:
        cand = [1] + [max(1, int(x)) for x in shape[1:]]
    # shrink from the LEFT of the trailing dims until the chunk fits the budget; the trailing dims are the
    # contiguous ones (atom, spatial), so splitting the replica axis first keeps reads sequential.
    i = 1
    while i < len(cand):
        n = itemsize
        for c in cand:
            n *= c
        if n <= budget_bytes:
            break
        cand[i] = 1
        i += 1
    return tuple(cand)


# ------------------------------------------------------------------------------------------------
# the prune, and its negative control
# ------------------------------------------------------------------------------------------------
def prune_to_last_frame(src_chk, dst_chk, keep_index=None):
    """Copy `src_chk` to `dst_chk` keeping the SAME dimensions and attributes but materialising only
    `keep_index`'s slice of every iteration-dimensioned variable.

    Never mutates the source. `keep_index` defaults to the last frame that actually holds data."""
    import netCDF4

    rep = chk_frame_report(src_chk)
    if not rep["frames_with_data"]:
        raise RuntimeError(f"{src_chk} holds no written checkpoint frame — nothing to prune to")
    keep = rep["frames_with_data"][-1] if keep_index is None else int(keep_index)

    with netCDF4.Dataset(str(src_chk), "r") as src, \
            netCDF4.Dataset(str(dst_chk), "w", format="NETCDF4") as dst:

        def _copy(s, d):
            for name in s.ncattrs():
                d.setncattr(name, s.getncattr(name))
            for dname, dim in s.dimensions.items():
                if dname not in d.dimensions:
                    # `iteration` MUST stay unlimited: a resume appends new frames to it.
                    d.createDimension(dname, None if dim.isunlimited() else len(dim))
            for vname, var in s.variables.items():
                per_iter = bool(var.dimensions) and var.dimensions[0] == "iteration"
                vlen = _is_vlen(var)
                kw = {}
                # VLEN variables take neither chunking nor compression — and they are metadata, kilobytes at
                # most, so there is nothing to save on them anyway.
                if per_iter and var.ndim >= 1 and not vlen:
                    ch = _chunking(var)
                    kw["chunksizes"] = _chunk_for(var.shape, _itemsize(var.dtype),
                                                  ch if isinstance(ch, (list, tuple)) else None)
                    # preserve the source's compression so the byte comparison isolates the PRUNE and is not
                    # confounded by newly-applied compression.
                    f = _filters(var)
                    if f.get("zlib"):
                        kw.update(zlib=True, complevel=int(f.get("complevel", 4) or 4),
                                  shuffle=bool(f.get("shuffle", False)))
                fv = getattr(var, "_FillValue", None)
                if fv is not None and not vlen:
                    kw["fill_value"] = fv
                try:
                    nv = d.createVariable(vname, var.datatype, var.dimensions, **kw)
                except Exception:  # noqa: BLE001 — a layout request the library refused; correctness first
                    nv = d.createVariable(vname, var.datatype, var.dimensions)
                for a in var.ncattrs():
                    if a != "_FillValue":
                        nv.setncattr(a, var.getncattr(a))
                if per_iter:
                    if keep < var.shape[0]:
                        nv[keep] = var[keep]      # ONLY the kept frame is materialised
                elif var.shape:
                    nv[...] = var[...]            # not per-iteration: copy whole
                else:
                    _copy_scalar(var, nv)
            for gname, grp in s.groups.items():
                _copy(grp, d.createGroup(gname))

        _copy(src, dst)
    return keep



def prune_snapshot(snap_chk, snap_nc=None, expected_iteration=None, checkpoint_interval=None, log=print):
    """Prune `snap_chk` IN PLACE (it is a snapshot, never a live reporter file). Returns a dict describing
    what happened; never raises.

    ⚠ FAIL-SAFE BY CONSTRUCTION, and that is not politeness — a commit is the only thing standing between a
    preemption and lost GPU hours, so an optimisation that can fail a commit is worse than no optimisation.
    The pruned file is written beside the snapshot and VALIDATED before it replaces it; on any failure the
    unpruned snapshot is kept and the commit proceeds exactly as before, with a line in the log."""
    snap_chk = Path(snap_chk)
    out = {"pruned": False, "before_bytes": None, "after_bytes": None}
    try:
        out["before_bytes"] = snap_chk.stat().st_size
        tmp = snap_chk.parent / ("prune-" + snap_chk.name)
        out["kept_frame_index"] = prune_to_last_frame(snap_chk, tmp)
        # PROVE IT BEFORE ADOPTING IT. The same validator the commit will run, on the pruned bytes, while
        # the untouched original is still on disk to fall back to.
        if snap_nc is not None and expected_iteration is not None:
            import rbfe_spot_checkpoint as _spot
            probe = snap_chk.parent / ("probe-" + Path(snap_nc).name)
            shutil.copy2(snap_nc, probe)
            try:
                # both live in `snap_chk.parent`, which is what makes the reporter's by-NAME checkpoint
                # lookup resolve to the PRUNED file rather than the untouched original.
                _spot.validate_reporter_pair(probe, tmp, int(expected_iteration),
                                             int(checkpoint_interval or 0))
            finally:
                probe.unlink(missing_ok=True)
        out["after_bytes"] = tmp.stat().st_size
        os.replace(tmp, snap_chk)
        out["pruned"] = True
        out["shrink_x"] = (round(out["before_bytes"] / out["after_bytes"], 2)
                           if out["after_bytes"] else None)
        log("[prune] .chk %.1f MiB -> %.1f MiB (%sx), frame %s kept"
            % (out["before_bytes"] / 1048576.0, out["after_bytes"] / 1048576.0,
               out["shrink_x"], out.get("kept_frame_index")))
    except Exception as e:  # noqa: BLE001 — an optimisation may never cost a commit
        out["error"] = f"{type(e).__name__}: {e}"
        log("[prune] SKIPPED, committing the unpruned checkpoint: %s" % out["error"])
        try:
            (snap_chk.parent / ("prune-" + snap_chk.name)).unlink(missing_ok=True)
        except Exception:  # noqa: BLE001
            pass
    return out
