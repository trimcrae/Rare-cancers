#!/usr/bin/env python3
"""
DEPRECATED (2026-07-22) — superseded by in-process NAGL charging (md_settings.CHARGE_METHOD="nagl").
This script existed to amortize the ~40-min AM1-BCC/sqm charge of the 166-atom recruiter across legs. But sqm
on that molecule turned out to be intractable (>85 min, never converged), so the panel switched to NAGL — a
deterministic ML AM1-BCC surrogate that charges it in seconds, in-process, with no cache. Kept only for
reference / a future am1bcc revisit; NOT on the critical path. See md_settings.py "ligand partial charges".

Pre-compute AM1-BCC charges for every UNIQUE panel ligand ONCE (free CPU/CI) and cache the resulting GAFF
templates to S3, so NO GPU leg ever pays for sqm.

WHY THIS EXISTS (2026-07-22, root-caused from build_smoke #2): every covalent-panel leg was spending ~40 min of
single-core AM1-BCC (antechamber/sqm) charging the 166-atom NR-V04 recruiter before MD even starts. On the CI
smoke that blew the 40-min job timeout; on a rented GPU box it would be ~40 min of GPU-IDLE billing PER LEG
(~12 GPU-h wasted across the 18-unit fan-out) plus a real timeout/flakiness risk. openmmforcefields keys its
charged-template cache on the ligand's connectivity-only isomeric SMILES, so charging each distinct ligand ONCE
here and shipping the cache lets every leg's SystemGenerator(cache=...) hit instantly.

The panel has 3 distinct small molecules (nrv04, nrv04_epimer, celastrol). The driver loads each leg's ligand
from an assembled co-fold SDF, but that SDF is built from `Chem.MolFromSmiles(LIGANDS[name])` + AddHs — the exact
same molecular graph + protonation as build_sdf(name) here — so a cache charged from build_sdf keys identically
and hits in the driver (verified by nrv04_covalent_assemble.ligand_mol_from_coords: topology == the template).

Consistency: the FF strings come from md_settings (the single source of truth). The env that builds this cache,
the env baked into the Vast image, and the driver's env are the SAME conda-packed env, so the cache keys match.

Checkpointing (trimcrae standing rule): the shared cache is uploaded to S3 AFTER each ligand, and any existing
cache is downloaded first, so a timeout/re-dispatch resumes instead of recharging. Free CPU; generous timeout.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def _charge_one(name, cache_path):
    """Charge one ligand (by panel name) into the shared openmmforcefields cache at cache_path. If it is already
    cached (resumed download), this is instant; otherwise it runs AM1-BCC once and writes the template."""
    import md_settings as MD
    from openff.toolkit import Molecule
    from openmm import app
    from openmmforcefields.generators import GAFFTemplateGenerator
    from nrv04_ligands import build_sdf

    sdf = os.path.join("/tmp", f"ffcache_{name}.sdf")
    build_sdf(name, sdf)                                  # MolFromSmiles(LIGANDS[name]) + AddHs -> same graph as driver
    lig = Molecule.from_file(sdf)
    if isinstance(lig, list):
        lig = lig[0]
    gen = GAFFTemplateGenerator(molecules=[lig], forcefield=MD.SMALL_MOLECULE_FORCEFIELD, cache=cache_path)
    # Trigger template generation (= the AM1-BCC charge) by having an OpenMM ForceField resolve the ligand-only
    # topology through the generator. NoCutoff (the default) needs no periodic box. This writes to cache_path in
    # the SAME format SystemGenerator(cache=...) reads back.
    ff = app.ForceField(*MD.PROTEIN_FORCEFIELDS)
    ff.registerTemplateGenerator(gen.generator)
    ff.createSystem(lig.to_topology().to_openmm())
    print(f"[ffcache] charged {name} ({lig.n_atoms} atoms) -> {cache_path}", flush=True)
    return lig.n_atoms


def main():
    import boto3
    from nrv04_covalent_panel import PANEL

    bucket = os.environ["VAST_CKPT_BUCKET"]
    key = os.environ.get("NRV04_FFCACHE_S3", "nrv04-ffcache/ffcache.json")
    cache_path = os.environ.get("NRV04_FFCACHE", "/tmp/nrv04_ffcache.json")

    s3 = boto3.client("s3")
    try:                                                 # resume from a prior (possibly partial) cache
        s3.download_file(bucket, key, cache_path)
        print(f"[ffcache] resumed from s3://{bucket}/{key}", flush=True)
    except Exception as e:                               # noqa: BLE001 — first run: no cache yet
        print(f"[ffcache] no prior cache ({e.__class__.__name__}); starting fresh", flush=True)

    unique = sorted({lg.ligand for lg in PANEL})
    print(f"[ffcache] {len(unique)} distinct ligands to ensure cached: {unique}", flush=True)
    stats = {}
    for name in unique:
        stats[name] = _charge_one(name, cache_path)
        s3.upload_file(cache_path, bucket, key)          # checkpoint after EACH ligand
        print(f"[ffcache] uploaded s3://{bucket}/{key} after {name}", flush=True)

    print(f"FFCACHE DONE -> s3://{bucket}/{key}  atoms={stats}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
