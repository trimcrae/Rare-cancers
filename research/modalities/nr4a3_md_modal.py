#!/usr/bin/env python3
"""
Modal wrapper to run the NR4A3 LBD cryptic-pocket MD on a CLOUD GPU (no local hardware).

The MD science is in `nr4a3_md.py`; this provisions a Modal GPU container, clones the latest repo
code at run time (so it always uses current `main`, not a stale cached image), runs the MD, then
mdpocket on the trajectory, and persists outputs to a Modal Volume.

SETUP (one-time, by the human):
  1. Modal account (modal.com) — free signup credit; pay-per-second GPU (A10G ~$1.1/hr).
  2. `pip install modal && modal token new`  (locally) OR add MODAL_TOKEN_ID / MODAL_TOKEN_SECRET as
     GitHub repo secrets for the gpu-md.yml workflow.
RUN (cheap validation first, then production):
  modal run research/modalities/nr4a3_md_modal.py --ns 10     # ~validation, a few $
  modal run research/modalities/nr4a3_md_modal.py --ns 150    # production, once validated
RETRIEVE:
  modal volume get nr4a3-md nr4a3-lbd-md.dcd
  modal volume get nr4a3-md mdpocket           # transient-pocket maps

NOTE: best-effort against the live Modal API (untested from the dev sandbox — no Modal egress).
If the image/gpu/volume calls need a tweak on first run, the error will be obvious; ping me.
"""

import modal

app = modal.App("nr4a3-cryptic-pocket")

image = modal.Image.micromamba().micromamba_install(
    "openmm", "pdbfixer", "mdtraj", "fpocket", "git", "numpy",
    channels=["conda-forge"],
)
vol = modal.Volume.from_name("nr4a3-md", create_if_missing=True)


@app.function(gpu="A10G", image=image, timeout=60 * 60 * 12, volumes={"/out": vol})
def run_md(ns: float = 10.0):
    import os
    import shutil
    import subprocess

    subprocess.run(["nvidia-smi"], check=False)  # confirm a GPU is attached
    subprocess.run(
        ["git", "clone", "--depth", "1", "https://github.com/trimcrae/Rare-cancers", "/tmp/repo"],
        check=True,
    )
    work = "/tmp/repo/research/modalities"
    env = os.environ.copy()
    env["NS"] = str(ns)
    print(f"[modal] running MD for {ns} ns on GPU", flush=True)
    r = subprocess.run(["python", "nr4a3_md.py"], cwd=work, env=env)

    for f in ("AF-Q92570.pdb", "nr4a3-lbd.pdb", "nr4a3-lbd-solvated.pdb", "nr4a3-lbd-md.dcd"):
        p = os.path.join(work, f)
        if os.path.exists(p):
            shutil.copy(p, f"/out/{f}")
            print(f"[modal] saved {f} ({os.path.getsize(p)} bytes)", flush=True)

    if os.path.exists("/out/nr4a3-lbd-md.dcd") and os.path.exists("/out/nr4a3-lbd-solvated.pdb"):
        subprocess.run(
            ["mdpocket", "--trajectory_file", "/out/nr4a3-lbd-md.dcd",
             "--trajectory_format", "dcd", "-f", "/out/nr4a3-lbd-solvated.pdb",
             "-o", "/out/mdpocket"],
            cwd="/out", check=False,
        )
    vol.commit()
    msg = f"MD exit={r.returncode}; outputs in Modal volume 'nr4a3-md'"
    print("[modal]", msg, flush=True)
    return msg


@app.local_entrypoint()
def main(ns: float = 10.0):
    print(run_md.remote(ns))
