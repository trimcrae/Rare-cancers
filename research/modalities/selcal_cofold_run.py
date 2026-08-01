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


def _seeds():
    raw = os.environ.get("SELCAL_SEEDS") or ",".join(str(s) for s in SP.COFOLD_MODEL_SEEDS)
    return [int(s) for s in raw.replace(" ", "").split(",") if s]


def _have_gpu():
    try:
        import torch
        return torch.cuda.is_available()
    except Exception:  # noqa: BLE001
        return False


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
    results, t0 = [], time.time()
    for system, gene in SYSTEMS:
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
                   "--seed", str(seed)]
            print("[selcal-cofold] %s seed %d: %s" % (system, seed, " ".join(cmd)), flush=True)
            t = time.time()
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
            "seeds": _seeds(), "ligand": manifest["ligand"],
            "arms": {k: v["construct"] for k, v in manifest["arms"].items()},
            "chain_contract": manifest["chain_contract"],
            "results": results, "wall_min": round((time.time() - t0) / 60.0, 1)}
    with open(os.path.join(out_dir, "cofold-provenance.json"), "w") as fh:
        json.dump(prov, fh, indent=2)
    ok = sum(1 for r in results if r.get("rc") in (0, "resumed"))
    print("[selcal-cofold] %d/%d predictions succeeded in %.1f min"
          % (ok, len(results), (time.time() - t0) / 60.0), flush=True)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
