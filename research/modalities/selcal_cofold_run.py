#!/usr/bin/env python3
"""ENDPOINT-MD SENSITIVITY CONTROL — the co-fold entry point that runs ON the rented host.

One Vast host produces every structural input the panel needs: both arms x 6 diffusion seeds = 12 Boltz-2
predictions of the SAME ternary (target bromodomain + VHL + Elongin B + Elongin C + the reference PROTAC),
differing only in the paralogue sequence and the seed.

★ WHY BOTH ARMS RUN ON ONE HOST AND IN ONE PROCESS. Protocol matching is the scientific content of this panel:
if the arms were co-folded by different Boltz versions, on different hardware, or from separately-resolved
sequences, a difference in E1 could come from the pipeline rather than from the paralogue. One process, one
pinned `boltz==` spec, one fetch of the E3 sequences shared by both arms — so the ONLY thing that differs is
the target chain.

⛔ CHECKPOINT + CONTINUOUS UPLOAD, PER UNIT (CLAUDE.md §6). A completed `(system, seed)` is never recomputed:
its output directory is checked first, so a preempted host that is re-dispatched resumes at prediction N+1
instead of redoing 1..N. The launcher's pipeline runs a background `s3 sync` beside this, so each prediction
is durable the moment it is written rather than at the end of the job.
"""
from __future__ import annotations

import glob
import json
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import selcal_panel as SP  # noqa: E402
import selcal_stage as ST  # noqa: E402

SYSTEMS = (("smarca2", "SMARCA2"), ("smarca4", "SMARCA4"))


def _systems():
    """Which arms THIS host produces. Scoped by `$SELCAL_SYSTEMS` so the two arms can run on two hosts.

    ★ WHY THEY FAN OUT (CLAUDE.md §6's litmus test): *"is there a result this shard could return that would
    make me NOT run the rest?"* For the two ARMS the answer is NO — a sensitivity control needs both, and one
    arm's co-folds say nothing about whether to buy the other's. Parallel costs the same GPU-dollars as
    serial, so serialising them would be pure wall-clock for zero decision value. (This is NOT the same
    question as the MD ladder's smoke -> one real leg -> fleet, where the answer IS yes and the rungs stay
    serial.)"""
    want = [w.strip() for w in (os.environ.get("SELCAL_SYSTEMS") or "").split(",") if w.strip()]
    return [(sysname, gene) for sysname, gene in SYSTEMS if not want or sysname in want]


def _seeds():
    raw = os.environ.get("SELCAL_SEEDS") or ",".join(str(s) for s in SP.COFOLD_MODEL_SEEDS)
    return [int(s) for s in raw.replace(" ", "").split(",") if s]


def _have_gpu():
    try:
        import torch
        return torch.cuda.is_available()
    except Exception:  # noqa: BLE001
        return False


# =============================================================================================================
# ★★ THE CCD CACHE — a TRUNCATED download used as if it were complete, and nothing checked
# =============================================================================================================
# MEASURED 2026-08-01, and it cost the whole smarca4 arm. Every one of its six seeds died in ~7 s inside
# Boltz's own loader:
#
#     File "…/boltz/main.py", line 766, in process_inputs; ccd = load_canonicals(mol_dir)
#     File "…/boltz/data/mol.py", line 36, in load_molecules; raise ValueError(msg)
#     ValueError: CCD component CYS not found!
#     [selcal-cofold] 0/6 predictions succeeded in 0.7 min
#
# ⛔ CYS IS A CANONICAL AMINO ACID. A `mols/` directory missing cysteine is not an exotic-ligand problem — it
# is an INCOMPLETE DOWNLOAD BEING TREATED AS READY. It fits everything else this lane has measured: four hosts
# died between 4 and 14 min, three of them while Boltz pulled its ~3 GB of CCD data and weights. smarca2's
# host finished that pull and produced all six models; smarca4's did not, and nothing looked before inference
# started. The arm burned a rental, returned `rc=1` in 42 seconds, and was silent as to why.
#
# ★ THE CHECK IS BOLTZ'S OWN PREDICATE, NOT A LIST RE-TYPED HERE (CLAUDE.md rule 1). `load_canonicals` is
# exactly what failed, so it is exactly what is called — a re-spelled set of required tokens could drift from
# the one the loader actually demands and would then certify a cache that still dies.
def ccd_cache_integrity(cache_dir):
    """(ok, detail): will Boltz's canonical-component load succeed against this cache?

    PURE apart from reading the filesystem. `ok=False` on an unreadable/absent Boltz is deliberate: not being
    able to ASK is an absent reading, not a clean cache, and the expensive failure mode here is certifying a
    short cache rather than re-pulling one that was fine."""
    mol_dir = os.path.join(str(cache_dir), "mols")
    detail = {"cache_dir": str(cache_dir), "mol_dir": mol_dir, "mol_dir_exists": os.path.isdir(mol_dir),
              "n_pkl_present": len(glob.glob(os.path.join(mol_dir, "*.pkl")))}
    # ★★ COLD IS NOT TRUNCATED, AND CONFLATING THEM WOULD BREAK THE VERY FIRST RUN. A cache with no `mols/`
    # at all has simply never been populated — Boltz fetches it lazily on the first `predict`, which is the
    # normal cold path and must be allowed. The measured failure is the OTHER one: a directory that EXISTS
    # and is SHORT, which Boltz will never repair because it only downloads what it thinks is absent. Only
    # `truncated` may refuse a run; `cold` proceeds and is re-verified after the first prediction.
    try:
        from boltz.data.mol import load_canonicals
    except Exception as e:  # noqa: BLE001
        detail["state"] = "unverifiable"
        detail["why"] = ("cannot import boltz.data.mol.load_canonicals (%s: %s) — the requirement is UNKNOWN, "
                         "which is an absent reading, not a clean cache" % (type(e).__name__, e))
        return False, detail
    if not os.path.isdir(mol_dir) or not detail["n_pkl_present"]:
        detail["state"] = "cold"
        detail["why"] = "no populated mols/ directory — nothing has been downloaded yet (the normal cold path)"
        return False, detail
    try:
        mols = load_canonicals(mol_dir)
    except Exception as e:  # noqa: BLE001 — this IS the failure being pre-empted
        detail["state"] = "truncated"
        detail["why"] = "%s: %s" % (type(e).__name__, e)
        detail["missing_examples"] = _missing_canonicals(mol_dir)[:12]
        return False, detail
    detail["state"] = "ok"
    detail["n_canonicals_loaded"] = len(mols)
    detail["why"] = ""
    return True, detail


#: How many `mols/*.pkl` a COMPLETE Boltz-2 CCD download contains. MEASURED, not chosen: the one host that
#: completed the fetch reported `n_pkl_present: 45227` after its repair, recorded in
#: research/modalities/selcal-cofold-census.json — which is that number's one home; this is a named reference
#: to it, and `tests/test_selcal_launch.py` fails if the two drift apart.
#: ⚠ IT IS A FLOOR, NOT AN EQUALITY. The CCD only grows upstream, so a later release legitimately carries more
#: components; what is diagnostic is a directory that is SHORT, which is the measured failure.
#: ⚠ AND IT IS A BUILD-TIME ASSERTION ONLY. The RUNTIME verdict stays `load_canonicals` — Boltz's own
#: predicate, the one that actually failed — because a re-spelled requirement can drift from the one the
#: loader demands and would then certify a cache that still dies (CLAUDE.md rule 1).
CCD_MIN_COMPONENTS = 45227

#: The two checkpoints `download_boltz2` fetches beside the CCD. Named here so the bake can prove they landed
#: whole rather than as the 0-byte stubs a killed transfer leaves.
CCD_CHECKPOINTS = ("boltz2_conf.ckpt", "boltz2_aff.ckpt")


def verify_baked_cache(cache_dir, min_components=None):
    """BUILD-TIME gate: return 0 only if this cache is one a rented GPU can predict from. Non-zero FAILS the
    docker build, which is the entire point — a short bake must never become an image.

    ★ WHY THIS RUNS IN THE BAKE AND NOT ONLY ON THE HOST. The host-side `preflight_ccd` already refuses a
    truncated cache, but it refuses it on a machine that is already billing, after a pull, a clone and a
    restore. Verifying the same bytes once on a free runner turns that into a build that simply does not
    publish. The checks are deliberately the same predicate plus two things the runtime verdict does not
    assert: a completeness FLOOR, and CYS by name — the component whose absence killed six seeds at ~7 s each
    on 2026-08-01."""
    floor = CCD_MIN_COMPONENTS if min_components is None else int(min_components)
    ok, detail = ccd_cache_integrity(cache_dir)
    print("[bake-verify] %s" % json.dumps(detail), flush=True)
    problems = []
    if not ok:
        problems.append("Boltz's own load_canonicals refuses this cache: %s (state=%s)"
                        % (detail.get("why"), detail.get("state")))
    n = int(detail.get("n_pkl_present") or 0)
    if n < floor:
        problems.append("mols/ holds %d component(s), below the measured floor of %d — this download is SHORT, "
                        "which is exactly the state that reaches inference and dies at ~7 s per seed"
                        % (n, floor))
    # CYS BY NAME, through the exact call that raised. `load_canonicals` covers it, but naming it makes the
    # assertion legible next to the incident it exists for, and survives a future change to what "canonical"
    # means upstream.
    mol_dir = os.path.join(str(cache_dir), "mols")
    try:
        from boltz.data.mol import load_molecules
        load_molecules(mol_dir, ["CYS"])
        print("[bake-verify] CYS resolves through boltz.data.mol.load_molecules", flush=True)
    except Exception as e:  # noqa: BLE001 — this IS the measured failure, reproduced as a build gate
        problems.append("CYS does not resolve (%s: %s) — a canonical amino acid missing from mols/ is an "
                        "INCOMPLETE DOWNLOAD, not an exotic-ligand problem" % (type(e).__name__, e))
    for ck in CCD_CHECKPOINTS:
        p = os.path.join(str(cache_dir), ck)
        sz = os.path.getsize(p) if os.path.exists(p) else 0
        print("[bake-verify] %s: %s byte(s)" % (ck, sz), flush=True)
        if sz < 1_000_000:
            problems.append("%s is %d byte(s) — absent or a stub left by a killed transfer" % (ck, sz))
    if problems:
        for p in problems:
            print("[bake-verify] ⛔ %s" % p, flush=True)
        print("[bake-verify] ⛔ REFUSING TO PUBLISH THIS IMAGE. A short cache that ships is a rental that dies "
              "at 7 seconds; a failed build costs nothing.", flush=True)
        return 1
    print("[bake-verify] ✅ cache complete: %d components (floor %d), CYS resolves, both checkpoints present."
          % (n, floor), flush=True)
    return 0


def _missing_canonicals(mol_dir):
    """Which canonical components are absent — for the READOUT only. The verdict is `load_canonicals`."""
    try:
        from boltz.data import const
        tokens = list(getattr(const, "canonical_tokens", []) or [])
    except Exception:  # noqa: BLE001
        return []
    return [t for t in tokens if not os.path.exists(os.path.join(mol_dir, "%s.pkl" % t))]


def _boltz_download(cache_dir):
    """Ask Boltz to (re)fetch its own cache. Best-effort across versions: the downloader has been renamed
    between releases, so several names are tried and the VERDICT is always the integrity check afterwards,
    never the return of this function."""
    import importlib
    for mod, fn in (("boltz.main", "download_boltz2"), ("boltz.main", "download_boltz1"),
                    ("boltz.main", "download")):
        try:
            f = getattr(importlib.import_module(mod), fn)
        except Exception:  # noqa: BLE001
            continue
        try:
            from pathlib import Path
            f(Path(cache_dir))
            print("[selcal-cofold] CCD/weights re-fetch via %s.%s returned" % (mod, fn), flush=True)
            return True
        except Exception as e:  # noqa: BLE001
            print("[selcal-cofold] %s.%s raised %s: %s" % (mod, fn, type(e).__name__, e), flush=True)
    print("[selcal-cofold] no usable Boltz downloader entry point — the purged cache will be re-pulled by "
          "the first `boltz predict` instead", flush=True)
    return False


def repair_ccd_cache(cache_dir):
    """Purge a SHORT `mols/` and re-pull. Returns (ok, detail_after).

    ⛔ THE PURGE IS THE POINT. Boltz only downloads what it thinks is absent, so a directory that exists but
    is short is never repaired by asking again — it stays short forever, which is why the smarca4 host failed
    identically on its restart at 11:22 AM ET as on its first attempt."""
    import shutil
    mol_dir = os.path.join(str(cache_dir), "mols")
    if os.path.isdir(mol_dir):
        print("[selcal-cofold] purging the SHORT CCD cache at %s — a partial cache is never repaired by "
              "asking again, only by re-pulling" % mol_dir, flush=True)
        shutil.rmtree(mol_dir, ignore_errors=True)
    _boltz_download(cache_dir)
    return ccd_cache_integrity(cache_dir)


def _s3_sync(src, dst, extra=()):
    cmd = ["aws", "s3", "sync", src, dst, "--only-show-errors", *extra]
    try:
        return subprocess.run(cmd).returncode == 0
    except Exception as e:  # noqa: BLE001
        print("[selcal-cofold] s3 sync %s -> %s unavailable (%s)" % (src, dst, type(e).__name__), flush=True)
        return False


def preflight_ccd(cache_dir, cache_s3=None):
    """Restore the cache from S3, VERIFY it, repair it if short, and re-bank it once healthy.

    ⚠ THE UPLOAD IS GATED ON THE CHECK PASSING, AND THAT ORDER IS THE WHOLE SAFETY ARGUMENT. A shared cache
    populated from a truncated local one would poison every future host of this lane — turning a one-host
    accident into a permanent property of the prefix. So: restore -> verify -> (repair -> verify) -> only
    then upload. A restored cache is never trusted on the strength of having been restored.

    Raises SystemExit when the cache is still short after a repair: six seeds failing at 7 s each, silently,
    is strictly worse than one loud refusal before the first prediction.

    ★★ THE LOCAL CACHE IS CHECKED FIRST, AND A GOOD ONE SHORT-CIRCUITS THE RESTORE. Since the lane runs a
    BAKED image (`triskit23/selcalcofold`), the ~3 GB is already a verified layer on disk, and syncing S3 over
    it would re-download the whole thing whenever the banked objects happen to be newer than the image's file
    mtimes — `aws s3 sync` compares mtime, so the "cache" silently becomes a 3 GB transfer on a billing host,
    which is the cost this image exists to remove. Skipping the restore does NOT weaken the safety argument
    below: nothing is banked here, and the thing that decides is still `ccd_cache_integrity`."""
    ok, detail = ccd_cache_integrity(cache_dir)
    if ok:
        detail["source"] = "already complete before any restore (the baked image layer)"
        print("[selcal-cofold] CCD preflight: the cache at %s ALREADY verifies (%s components) — no S3 "
              "restore, no ~3 GB pull. %s" % (cache_dir, detail.get("n_pkl_present"), json.dumps(detail)),
              flush=True)
        return detail
    if cache_s3:
        print("[selcal-cofold] restoring the Boltz cache from %s (~3 GB — this is the step that killed three "
              "of four hosts when it was a cold download)" % cache_s3, flush=True)
        _s3_sync(cache_s3, str(cache_dir))
    ok, detail = ccd_cache_integrity(cache_dir)
    print("[selcal-cofold] CCD preflight: ok=%s %s" % (ok, json.dumps(detail)), flush=True)
    if not ok:
        print("[selcal-cofold] the CCD cache is %r — %s. Repairing BEFORE inference rather than discovering "
              "it inside Boltz's loader once per seed." % (detail.get("state"), detail.get("why")), flush=True)
        ok, detail = repair_ccd_cache(cache_dir)
        print("[selcal-cofold] CCD after repair: ok=%s %s" % (ok, json.dumps(detail)), flush=True)
    if not ok and detail.get("state") == "truncated":
        # ⛔ THE ONLY STATE THAT REFUSES A RUN, and it is the one that was MEASURED. Boltz only downloads what
        # it thinks is absent, so a short directory that survived a purge and re-pull will not fix itself:
        # every prediction dies in ~7 s inside load_canonicals and the arm returns rc=1 with no models and no
        # explanation. Six silent failures are strictly worse than one loud refusal.
        raise SystemExit("[selcal-cofold] ⛔ REFUSING TO RUN: the Boltz CCD cache is still TRUNCATED after a "
                         "purge and re-pull (%s). A partial cache must be a re-pull, never a run."
                         % detail.get("why"))
    if not ok:
        # `cold` (never populated) and `unverifiable` (boltz not importable here) both PROCEED: the cold path
        # is how a first-ever run legitimately begins — Boltz fetches lazily inside `predict` — and refusing
        # it would mean this guard could never bootstrap its own cache. The per-seed re-check below is what
        # catches a lazy fetch that lands short, so proceeding costs one seed, not six.
        print("[selcal-cofold] ⚠ proceeding with a %r cache: Boltz will fetch it lazily on the first "
              "prediction, and the per-seed re-check catches a short landing. This is NOT the measured "
              "failure mode, which is a directory that exists and is short." % detail.get("state"), flush=True)
    if ok and cache_s3:
        # ⚠ GATED ON `ok`, WHICH IS THE WHOLE SAFETY ARGUMENT. Banking a cold or truncated cache would poison
        # every future host of this lane, turning a one-host accident into a permanent property of the prefix.
        # Banked EARLY when it IS good: a host that then dies during inference still leaves its verified cache
        # for its successor — the same reasoning as the MSA restore.
        print("[selcal-cofold] cache VERIFIED — banking it to %s so the next host restores instead of "
              "re-pulling ~3 GB" % cache_s3, flush=True)
        _s3_sync(str(cache_dir), cache_s3)
    return detail


def bank_ccd_if_verified(cache_dir, cache_s3=None):
    """Re-verify and bank after the run — the cold path's cache only exists once Boltz has fetched it.

    Same gate as the preflight's: a cache is uploaded because it VERIFIED, never because it is present."""
    if not cache_s3:
        return None
    ok, detail = ccd_cache_integrity(cache_dir)
    if ok:
        print("[selcal-cofold] post-run cache verified — banking to %s" % cache_s3, flush=True)
        _s3_sync(str(cache_dir), cache_s3)
    else:
        print("[selcal-cofold] post-run cache is %r — NOT banking it. A shared cache is populated from a "
              "verified local one or not at all." % detail.get("state"), flush=True)
    return detail


def main():
    out_dir = os.environ.get("OUTPUT_DIR") or "/tmp/selcal_cofold_out"
    inputs_dir = os.environ.get("SELCAL_INPUTS_DIR") or os.path.join(out_dir, "inputs")
    os.makedirs(out_dir, exist_ok=True)

    # The inputs are BUILT ON CI AND DOWNLOADED, not resolved here. Two reasons, both about the meter: a
    # UniProt or AlphaFold-DB hiccup would otherwise fail a job that is already billing, and the chain
    # CONTRACT the assembler verifies against has to exist in S3 anyway. If they are genuinely absent, build
    # them rather than dying — but say so, because it means the CI step did not run.
    manifest_path = os.path.join(inputs_dir, "cofold-inputs.json")
    if not os.path.exists(manifest_path):
        print("[selcal-cofold] WARN %s absent — the CI staging step did not run. Building the inputs here; "
              "this costs a network round trip on a billing host." % manifest_path, flush=True)
        ST.build_cofold_inputs(inputs_dir)
    with open(manifest_path) as fh:
        manifest = json.load(fh)
    print("[selcal-cofold] ligand %s (%s) | %s" % (manifest["ligand"]["name"], manifest["ligand"]["ccd"],
                                                   {k: v["construct"]["n_residues"]
                                                    for k, v in manifest["arms"].items()}), flush=True)

    if not _have_gpu():
        raise SystemExit("[selcal-cofold] no CUDA GPU visible — refusing to run Boltz on CPU. This is a "
                         "rented GPU host; a CPU fallback would bill for hours and produce nothing usable.")

    boltz_spec = os.environ.get("BOLTZ_SPEC", "boltz")
    # ⛔ AN EXPLICIT CACHE DIR, so the thing that is checked, repaired and banked is provably the thing Boltz
    # reads. With the default `~/.boltz` the cache location depends on `$HOME` inside the container, and a
    # check that verified a different directory would be worse than no check.
    cache_dir = os.environ.get("BOLTZ_CACHE") or os.path.expanduser("~/.boltz")
    os.makedirs(cache_dir, exist_ok=True)
    ccd_detail = preflight_ccd(cache_dir, os.environ.get("BOLTZ_CACHE_S3"))

    results, t0 = [], time.time()
    repaired_once = False
    for system, gene in _systems():
        yml = os.path.join(inputs_dir, "%s.yaml" % system)
        if not os.path.exists(yml):
            raise SystemExit("[selcal-cofold] missing input %s" % yml)
        for seed in _seeds():
            sdir = os.path.join(out_dir, system, "seed_%d" % seed)
            os.makedirs(sdir, exist_ok=True)
            if glob.glob(os.path.join(sdir, "**", "*.cif"), recursive=True):
                print("[selcal-cofold] %s seed %d: CIF already present -> resume-skip" % (system, seed),
                      flush=True)
                results.append({"system": system, "gene": gene, "seed": seed, "rc": "resumed"})
                continue
            cmd = ["boltz", "predict", yml, "--use_msa_server", "--out_dir", sdir, "--no_kernels",
                   "--cache", cache_dir, "--seed", str(seed)]
            print("[selcal-cofold] %s seed %d: %s" % (system, seed, " ".join(cmd)), flush=True)
            t = time.time()
            rc = subprocess.run(cmd).returncode
            n_cif = len(glob.glob(os.path.join(sdir, "**", "*.cif"), recursive=True))
            # ★ A FAILURE RE-CHECKS THE CACHE ONCE. The preflight proves the cache was whole before the run;
            # this catches it going short DURING one (an evicted or part-written file), which is the same
            # fault an hour later and would otherwise take the remaining seeds down with it at ~7 s each.
            if rc != 0 and not n_cif and not repaired_once:
                ok, det = ccd_cache_integrity(cache_dir)
                if not ok:
                    print("[selcal-cofold] ⛔ the cache went SHORT mid-run (%s) — repairing and retrying this "
                          "seed once" % det.get("why"), flush=True)
                    repaired_once = True
                    ok, det = repair_ccd_cache(cache_dir)
                    if ok:
                        rc = subprocess.run(cmd).returncode
                        n_cif = len(glob.glob(os.path.join(sdir, "**", "*.cif"), recursive=True))
            print("[selcal-cofold] %s seed %d -> rc=%s, %d CIF(s), %.1f s (elapsed %.1f min)"
                  % (system, seed, rc, n_cif, time.time() - t, (time.time() - t0) / 60.0), flush=True)
            results.append({"system": system, "gene": gene, "seed": seed, "rc": rc, "n_cif": n_cif,
                            "wall_s": round(time.time() - t, 1)})
            # ⚠ A FAILED PREDICTION DOES NOT ABORT THE BATCH, and it does not pass either. The panel needs
            # 6 models per arm; losing one to a transient MSA-server failure should not throw away the other
            # eleven, and the census (`--mode cofold_collect`) is what decides whether the set is complete.
    prov = {"_what": "Boltz-2 co-folds for the endpoint-MD sensitivity control: one ligand, both real "
                     "paralogue sequences, identical protocol, %d diffusion seeds per arm." % len(_seeds()),
            "boltz_spec": boltz_spec, "git_branch": os.environ.get("GIT_BRANCH"),
            "ccd_cache": ccd_detail, "ccd_cache_repaired_mid_run": repaired_once,
            "seeds": _seeds(), "ligand": manifest["ligand"],
            "arms": {k: v["construct"] for k, v in manifest["arms"].items()},
            "chain_contract": manifest["chain_contract"],
            "results": results, "wall_min": round((time.time() - t0) / 60.0, 1)}
    # ⚠ PER-ARM FILENAME. Both arms' hosts sync into the SAME `$RESULT_S3`, so a single
    # `cofold-provenance.json` is a file the two of them overwrite in turn — leaving the panel with a
    # provenance record for whichever host happened to finish last and none at all for the other.
    # The cold path's cache only exists once Boltz has fetched it, so the bank happens here too — gated on the
    # same verification, never on mere presence.
    bank_ccd_if_verified(cache_dir, os.environ.get("BOLTZ_CACHE_S3"))
    _tag = "-".join(s for s, _g in _systems()) or "all"
    with open(os.path.join(out_dir, "cofold-provenance-%s.json" % _tag), "w") as fh:
        json.dump(prov, fh, indent=2)
    ok = sum(1 for r in results if r.get("rc") in (0, "resumed"))
    print("[selcal-cofold] %d/%d predictions succeeded in %.1f min"
          % (ok, len(results), (time.time() - t0) / 60.0), flush=True)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
