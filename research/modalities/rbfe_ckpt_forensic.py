#!/usr/bin/env python
"""Forensic probe for committed RBFE/ternary spot checkpoints (2026-07-21 interval-mismatch bug).

Given a local directory tree of DOWNLOADED committed generations (each generation dir holds a
COMMITTED.json manifest + its analysis .nc + checkpoint .chk), open each pair with the REAL
openmmtools MultiStateReporter and print, for the newest few:

  * the manifest's recorded iteration (+ checkpoint_interval field if present)
  * reporter.checkpoint_interval        -> the cadence BAKED into the .nc when it was created
  * read_last_iteration(last_checkpoint=False) -> analysis (.nc) last iteration
  * read_last_iteration(last_checkpoint=True)   -> resumable checkpoint (.chk) last full frame
  * raw netCDF global attrs (where checkpoint_interval physically lives) + the `iteration` dim of both
  * TORN? flag: checkpoint last != analysis last (a pair validate_reporter_pair would reject)

This DEFINITIVELY tells us which committed generations are on a 20- vs 40-grid, whether any committed
pair is itself torn, and confirms the fix's derive-from-file source (reporter.checkpoint_interval).
CPU-only, no GPU — runs on a free CI runner.

Usage:  python rbfe_ckpt_forensic.py <root_dir> [--newest N]
The workflow downloads the newest N production generations into <root_dir>/<gen-subdir>/ before this.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

MANIFEST = "COMMITTED.json"


def _raw_netcdf(path: Path) -> dict:
    out = {"exists": path.is_file(), "size": path.stat().st_size if path.is_file() else 0}
    try:
        import netCDF4
        with netCDF4.Dataset(str(path), "r") as ds:
            attrs = {}
            for a in ds.ncattrs():
                try:
                    attrs[a] = ds.getncattr(a)
                except Exception:  # noqa: BLE001
                    pass
            out["global_attrs"] = {k: (int(v) if hasattr(v, "__int__") and not isinstance(v, (bytes, str)) else str(v))
                                   for k, v in attrs.items()}
            out["iteration_dim"] = len(ds.dimensions["iteration"]) if "iteration" in ds.dimensions else None
            out["UUID"] = str(getattr(ds, "UUID", ""))
            # group-level checkpoint_interval, if openmmtools nests it
            grp_ci = {}
            for gn, g in ds.groups.items():
                if hasattr(g, "checkpoint_interval"):
                    grp_ci[gn] = int(g.checkpoint_interval)
            if grp_ci:
                out["group_checkpoint_interval"] = grp_ci
    except Exception as e:  # noqa: BLE001
        out["netcdf_error"] = repr(e)
    return out


def inspect_generation(gdir: Path) -> dict:
    man = json.loads((gdir / MANIFEST).read_text())
    nc = gdir / man["analysis_name"]
    chk = gdir / man["checkpoint_name"]
    rec = {
        "dir": str(gdir),
        "manifest_iteration": man.get("iteration"),
        "manifest_checkpoint_interval": man.get("checkpoint_interval", "<absent>"),
        "manifest_analysis_last_iteration": man.get("analysis_last_iteration"),
        "manifest_checkpoint_frames": man.get("checkpoint_frames"),
        "nc": _raw_netcdf(nc),
        "chk": _raw_netcdf(chk),
    }
    # the authoritative source the fix reads: reporter.checkpoint_interval + read_last_iteration
    try:
        from openmmtools import multistate
        rep = multistate.MultiStateReporter(str(nc), open_mode="r", checkpoint_storage=chk.name)
        try:
            rec["reporter_checkpoint_interval"] = int(getattr(rep, "checkpoint_interval", 0) or 0)
            rec["analysis_last_iteration"] = int(rep.read_last_iteration(last_checkpoint=False))
            rec["checkpoint_last_iteration"] = int(rep.read_last_iteration(last_checkpoint=True))
            rec["TORN"] = rec["analysis_last_iteration"] != rec["checkpoint_last_iteration"]
        finally:
            rep.close()
    except Exception as e:  # noqa: BLE001
        rec["reporter_error"] = repr(e)
    # also exercise the fix helper so the log confirms it agrees with the reporter
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import rbfe_spot_checkpoint as spot
        rec["derived_interval_helper"] = spot.read_checkpoint_interval(nc, chk)
    except Exception as e:  # noqa: BLE001
        rec["derived_interval_helper_error"] = repr(e)
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("root")
    ap.add_argument("--newest", type=int, default=6)
    args = ap.parse_args()
    root = Path(args.root)
    gdirs = sorted({p.parent for p in root.rglob(MANIFEST)},
                   key=lambda d: d.name, reverse=True)
    # sort by manifest iteration (newest first)
    def _it(d):
        try:
            return int(json.loads((d / MANIFEST).read_text()).get("iteration", -1))
        except Exception:  # noqa: BLE001
            return -1
    gdirs = sorted(gdirs, key=_it, reverse=True)
    print(f"[forensic] {len(gdirs)} committed generation(s) under {root}", flush=True)
    intervals = {}
    for gdir in gdirs[:args.newest]:
        rec = inspect_generation(gdir)
        print("\n" + "=" * 78, flush=True)
        print(json.dumps(rec, indent=2, default=str), flush=True)
        ci = rec.get("reporter_checkpoint_interval") or rec.get("derived_interval_helper")
        if ci:
            intervals.setdefault(ci, 0)
            intervals[ci] += 1
    print("\n" + "=" * 78, flush=True)
    print(f"[forensic] interval histogram across inspected generations: {intervals}", flush=True)
    torn = [g["manifest_iteration"] for g in (inspect_generation(d) for d in gdirs[:args.newest])
            if g.get("TORN")]
    print(f"[forensic] TORN committed generations (checkpoint != analysis): {torn or 'NONE'}", flush=True)


if __name__ == "__main__":
    main()
