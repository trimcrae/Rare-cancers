#!/usr/bin/env python3
"""
Modal wrapper to run the NR4A3 LBD cryptic-pocket MD on a CLOUD GPU (no local hardware needed).

The actual MD is `nr4a3_md.py`; this provisions a Modal GPU container, runs it, then runs mdpocket
on the trajectory to map transient pockets at Pocket-5, and persists outputs to a Modal Volume.

SETUP (one-time, by the human):
  1. Create a Modal account (modal.com) — free tier + pay-per-second GPU (~$0.60-1.10/hr for A10G).
  2. `pip install modal && modal token new`  (locally), or add MODAL_TOKEN_ID / MODAL_TOKEN_SECRET
     as GitHub secrets for the gpu-md.yml workflow.
RUN:
  modal run research/modalities/nr4a3_md_modal.py --ns 50
  (then: modal volume get nr4a3-md nr4a3-lbd-md.dcd  to retrieve the trajectory)

NOTE: this is best-effort against the Modal API and is UNTESTED from the dev sandbox (no Modal
egress). Verify the image/gpu/volume calls against current Modal docs on first run; the MD science
in nr4a3_md.py is the substance.
"""

import modal

app = modal.App("nr4a3-cryptic-pocket")

image = (
    modal.Image.micromamba()
    .micromamba_install(
        "openmm", "pdbfixer", "mdtraj", "fpocket", "git", "numpy",
        channels=["conda-forge"],
    )
    .run_commands(
        "git clone --depth 1 https://github.com/trimcrae/Rare-cancers /repo || true"
    )
)
vol = modal.Volume.from_name("nr4a3-md", create_if_missing=True)


@app.function(gpu="A10G", image=image, timeout=60 * 60 * 8, volumes={"/out": vol})
def run_md(ns: float = 50.0):
    import os
    import shutil
    import subprocess

    work = "/repo/research/modalities"
    env = os.environ.copy()
    env["NS"] = str(ns)
    print(f"[modal] running MD for {ns} ns on GPU", flush=True)
    subprocess.run(["python", "nr4a3_md.py"], cwd=work, env=env, check=False)

    for f in ("AF-Q92570.pdb", "nr4a3-lbd.pdb", "nr4a3-lbd-solvated.pdb", "nr4a3-lbd-md.dcd"):
        p = os.path.join(work, f)
        if os.path.exists(p):
            shutil.copy(p, f"/out/{f}")
            print(f"[modal] saved {f} ({os.path.getsize(p)} bytes)", flush=True)

    # transient-pocket mapping at Pocket-5 (mdpocket)
    if os.path.exists("/out/nr4a3-lbd-md.dcd") and os.path.exists("/out/nr4a3-lbd-solvated.pdb"):
        subprocess.run(
            ["mdpocket", "--trajectory_file", "/out/nr4a3-lbd-md.dcd",
             "--trajectory_format", "dcd", "-f", "/out/nr4a3-lbd-solvated.pdb",
             "-o", "/out/mdpocket"],
            cwd="/out", check=False,
        )
    vol.commit()
    return "MD + mdpocket complete; retrieve from Modal volume 'nr4a3-md'"


@app.local_entrypoint()
def main(ns: float = 50.0):
    print(run_md.remote(ns))
