#!/usr/bin/env python3
"""HOST-SIDE driver for ONE leg of the CREBBP-vs-BRD4(1) / SGC-CBP30 selectivity ABFE, on a rented Vast box.

It is the thin layer between `nr4a3_abfe.run_shard` (the engine, unchanged) and the control plane that has to
supervise a community host it cannot log into. The engine writes per-window `window_XX.jsonl` + a per-iteration
`State.xml`; this driver adds the ONE thing a remote supervisor needs and the engine has no reason to produce:

    a durable, self-timestamping, per-unit STATUS RECORD that says how far the science has got.

★ WHY THAT RECORD IS NOT OPTIONAL, and why it is written on a TIMER rather than at the end.
CLAUDE.md §4 requires that an unproven pipeline be checked every ~3-6 min with a PROGRESS check — GPU busy,
phase advanced, **iteration count UP since last time** — not a liveness ping. From CI, "up" is only knowable if
something durable carries a monotonically increasing scalar. Without it the board can say the box is running
and cannot say whether it is working, which is exactly the shape of the three silent failures on the ternary
lane. So a background thread re-derives `iterations_done` from the engine's OWN files (never from a default —
CLAUDE.md §4b) every `PROGRESS_S` seconds and rewrites `leg_<unit>.json`; the sync loop in the onstart pipeline
pushes it to S3, and `abfe_sel_vast_launch.collect` reads it.

★ PHASES ARE NAMED FOR THE CHECK THAT USES THEM. `setup` (the solvated system is being built and
parameterised — CPU/RAM bound, minutes, GPU legitimately at 0 %), then `production` (windows sampling). A
board that cannot tell those apart reaps a healthy cold start, which `vast_idle_guard` exists to prevent.

★ WHAT IS DELIBERATELY *NOT* HERE. No MBAR combination across legs, no ΔΔG, no verdict. The reduce is a $0 CPU
step that runs in CI on the synced logs (`abfe_sel_reduce.py`) — running it on a billing host would pay GPU
rates for numpy, and running it per-leg would mean each leg reporting a number that only makes sense combined
with another leg's. A leg reports its OWN MBAR ΔG (which is free once its samples are on disk) and stops.
"""
from __future__ import annotations

import json
import os
import sys
import threading
import time
import traceback

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import nr4a3_abfe  # noqa: E402

PROGRESS_S = float(os.environ.get("ABFE_SEL_PROGRESS_S") or "60")


def _utc():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def window_progress(out_dir, n_windows):
    """(windows_done, iterations_done, per_window) read from the ENGINE'S OWN FILES. PURE-ish (reads disk).

    ⚠ `_last_logged_iter` returns the last logged index, so a window with iterations 0..n-1 answers n-1. The
    count of samples is that + 1, and a window that has logged nothing answers -1 -> 0. Getting this off by one
    would make a healthy leg look one iteration behind forever, which is the kind of drift a progress check
    cannot tolerate: the whole point is comparing this number against the last one.
    """
    per, total, done = [], 0, 0
    for w in range(int(n_windows)):
        n = nr4a3_abfe._last_logged_iter(out_dir, w) + 1
        per.append(n)
        total += n
    return done, total, per


def write_record(path, **fields):
    """Atomically rewrite the leg record. Atomic because the sync loop may upload it mid-write, and a torn
    JSON in S3 reads to `collect` as an unreadable leg — indistinguishable from a dead one."""
    doc = {"updated_utc": _utc(), **fields}
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(doc, f, indent=1)
    os.replace(tmp, path)
    return doc


class _Progress(threading.Thread):
    """Re-derive and republish the leg's progress every PROGRESS_S. Daemon: it must never hold the exit."""

    daemon = True

    def __init__(self, record_path, out_dir, base):
        super().__init__()
        self.record_path, self.out_dir, self.base = record_path, out_dir, dict(base)
        self.phase = "setup"
        self._stop = threading.Event()

    def run(self):
        while not self._stop.wait(PROGRESS_S):
            try:
                self.publish()
            except Exception as e:  # noqa: BLE001 — a monitoring aid must never kill the science
                print(f"[abfe-sel] progress publish failed: {type(e).__name__}: {e}", flush=True)

    def publish(self, **extra):
        _d, iters, per = window_progress(self.out_dir, self.base["n_windows"])
        return write_record(self.record_path, status="running", phase=self.phase,
                            iterations_done=iters, per_window_iters=per,
                            windows_done=sum(1 for n in per if n >= self.base["n_iter"]),
                            prod_iters_target=self.base["n_windows"] * self.base["n_iter"],
                            **self.base, **extra)

    def stop(self):
        self._stop.set()


def _resolve(in_dir, receptor, want_sdf=True):
    """(receptor_pdb, ligand_sdf) from the staged input directory, matched to THIS receptor.

    The staged prefix holds BOTH receptors' files (`crebbp-opened.pdb`, `docked_crebbp.sdf`,
    `brd4bd1-opened.pdb`, `docked_brd4bd1.sdf`), so a match that just took the first `.pdb` would silently run
    the wrong protein and file the answer under the right name. That is the same class of error as
    `entry_abfe._first`'s `prefer` argument, which exists for exactly this prefix shape.
    """
    files = sorted(os.listdir(in_dir)) if os.path.isdir(in_dir) else []
    pdb = next((f for f in files if f == f"{receptor}-opened.pdb"), None)
    sdf = next((f for f in files if f == f"docked_{receptor}.sdf"), None)
    if want_sdf and not sdf:
        raise FileNotFoundError(f"no docked_{receptor}.sdf in {in_dir} (saw {files})")
    return (os.path.join(in_dir, pdb) if pdb else None,
            os.path.join(in_dir, sdf) if sdf else None)


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description="one Vast leg of the CBP30 selectivity ABFE")
    ap.add_argument("--unit-id", required=True)
    ap.add_argument("--leg", choices=["complex", "solvent"], required=True)
    ap.add_argument("--receptor", default="crebbp", help="which receptor's staged files to use")
    ap.add_argument("--ligand-name", default="sgc_cbp30")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--n-iter", type=int, default=2000)
    ap.add_argument("--steps-per-iter", type=int, default=500)
    ap.add_argument("--in-dir", default=os.environ.get("INPUT_DIR") or "/tmp/abfe_in")
    ap.add_argument("--out-dir", default=None, help="default <OUTPUT_DIR>/<unit-id>")
    ap.add_argument("--platform", default="CUDA")
    a = ap.parse_args(argv)

    out_root = os.environ.get("OUTPUT_DIR") or "/tmp/abfe_out"
    out_dir = a.out_dir or os.path.join(out_root, a.unit_id)
    os.makedirs(out_dir, exist_ok=True)
    record = os.path.join(out_root, f"leg_{a.unit_id}.json")

    base = {"unit_id": a.unit_id, "leg": a.leg, "receptor": (a.receptor if a.leg == "complex" else "shared"),
            "seed": a.seed, "n_iter": a.n_iter, "steps_per_iter": a.steps_per_iter,
            "n_windows": nr4a3_abfe.n_windows(), "ligand_name": a.ligand_name,
            "started_utc": _utc(),
            # ★ WHICH CODE RAN. The host pulls a codeload TARBALL, so there is no git sha on disk and the
            # branch may have moved between dispatch and container start. Without a content hash a `failed`
            # record is ambiguous between "the fix does not work" and "this predates the fix" — the exact
            # ambiguity that cost the 5a-KS lane a paid round trip.
            "driver_sha256": _sha12(__file__), "engine_sha256": _sha12(nr4a3_abfe.__file__)}
    prog = _Progress(record, out_dir, base)
    prog.publish(phase="setup")
    prog.start()
    t0 = time.time()
    try:
        rec_pdb, lig_sdf = _resolve(a.in_dir, a.receptor, want_sdf=True)
        if a.leg == "complex" and not rec_pdb:
            raise FileNotFoundError(f"complex leg needs {a.receptor}-opened.pdb in {a.in_dir}")
        print(f"[abfe-sel] {a.unit_id}: leg={a.leg} receptor={a.receptor} sdf={lig_sdf} pdb={rec_pdb} "
              f"windows={base['n_windows']} n_iter={a.n_iter} seed={a.seed}", flush=True)
        # The phase flips to `production` the moment run_shard is entered. It is not exact — run_shard builds
        # or reloads the reference system first — but the reference build writes `reference_system.xml`, so
        # the board can distinguish the two from the artifact rather than from this label. Marking it here
        # keeps the flip on the side that under-claims: a leg is never reported as producing before it is.
        prog.publish(phase="setup")
        meta = nr4a3_abfe.run_shard(
            a.leg, lig_sdf, out_dir, receptor_pdb=(rec_pdb if a.leg == "complex" else None),
            pose_name=a.ligand_name, n_iter=a.n_iter, steps_per_iter=a.steps_per_iter,
            platform_name=a.platform, seed=a.seed, pose_index=0)
        prog.phase = "production"
        prog.stop()
        _d, iters, per = window_progress(out_dir, base["n_windows"])
        # The leg's OWN MBAR ΔG — free, the samples are already on disk, and it is what makes a finished leg
        # readable without a second job. It is a DECOUPLING ΔG, not a binding one; the ΔG_bind combination
        # and the ΔΔG are the CI reduce's business (see the module docstring).
        dg = se = None
        try:
            dg, se = nr4a3_abfe.reduce_leg(out_dir)
        except Exception as e:  # noqa: BLE001 — a leg that sampled is done even if MBAR needs a better solve
            print(f"[abfe-sel] leg MBAR did not solve here ({type(e).__name__}: {e}); the CI reduce will "
                  f"retry on the full synced logs", flush=True)
        write_record(record, status="done", phase="done", iterations_done=iters, per_window_iters=per,
                     windows_done=sum(1 for n in per if n >= a.n_iter),
                     prod_iters_target=base["n_windows"] * a.n_iter,
                     decouple_dg_kcal=dg, decouple_mbar_se_kcal=se,
                     restraint_standard_state_dg=meta.get("restraint_standard_state_dg"),
                     n_receptor_atoms=meta.get("n_receptor_atoms"), n_ligand_atoms=meta.get("n_ligand_atoms"),
                     lambda_schedule=meta.get("lambda_schedule"),
                     # ★ WALL TIME AND FRAME COUNT — the fields ONLY A REAL RUN CAN FILL (CLAUDE.md §4b).
                     # `n_iter` and `leg` come from the environment and would be present on a leg that never
                     # ran a step; these cannot be.
                     gpu_hours=round((time.time() - t0) / 3600.0, 4), **base)
        print(f"[abfe-sel] DONE {a.unit_id}: {iters} iterations, "
              f"{(time.time() - t0) / 3600.0:.2f} h, decoupling ΔG = "
              + (f"{dg:.3f} ± {se:.3f} kcal/mol" if dg is not None else "(MBAR deferred to CI)"), flush=True)
        return 0
    except Exception as e:  # noqa: BLE001 — a crash must leave a READABLE obituary, not silence
        prog.stop()
        _d, iters, per = window_progress(out_dir, base["n_windows"])
        write_record(record, status="failed", phase="failed", error=f"{type(e).__name__}: {e}",
                     traceback=traceback.format_exc(), iterations_done=iters, per_window_iters=per,
                     gpu_hours=round((time.time() - t0) / 3600.0, 4), **base)
        print(f"[abfe-sel] FAILED {a.unit_id}: {type(e).__name__}: {e}", flush=True)
        traceback.print_exc()
        return 1


def _sha12(path):
    import hashlib
    try:
        with open(path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()[:12]
    except OSError:
        return None


if __name__ == "__main__":
    raise SystemExit(main())
