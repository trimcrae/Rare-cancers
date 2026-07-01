#!/usr/bin/env python3
"""
NR4A3–PROTAC–E3 ternary-complex modelling (degrader GPU experiment #3 — degradability geometry).

WHY NOW. The "is the fusion geometrically degradable?" question needs an AF3-class model that folds
two proteins + a small molecule together. That capability is open as of 2026-06 (AlphaFold3, Boltz-2,
Protenix — method-watch hit), so this experiment moved from "parked" to "primed." We model the
**NR4A3 LBD + E3 substrate receptor (CRBN) + PROTAC** ternary and score whether the recruited complex
presents a solvent-exposed lysine near the E3 in a geometry compatible with ubiquitin transfer.

HONEST STATUS. No selective NR4A3 warhead/PROTAC exists yet (that is degrader experiment #2). So this
script does two things:
  (1) PREP + POSITIVE CONTROL (CPU/CI, runnable now): fetch the NR4A3 LBD (AFDB Q92570, 373-626) and
      CRBN (AFDB Q96SW2) sequences and a real E3 ligand (lenalidomide, fetched from ChEMBL by name),
      assemble Boltz inputs, and build a *checkable control* — CRBN + lenalidomide — whose right
      answer is known (the imide should seat in CRBN's tri-tryptophan pocket). If Boltz can't recover
      that, we don't trust its NR4A3 ternary.
  (2) TERNARY TEMPLATE: emit the NR4A3-LBD + CRBN + PROTAC Boltz input, with the PROTAC SMILES taken
      from $PROTAC_SMILES (or --protac-smiles). Until a warhead is designed this is a template that
      completes the instant a SMILES exists — no rework.

Inference needs a GPU (Boltz/torch); like the MD it is PREPARED to run as-is and skips gracefully in
CI. Tool is Boltz-2 by default; Protenix/AF3 are documented swap-ins (keep the pipeline modular).

Outputs: nr4a3-ternary-control.yaml, nr4a3-ternary-protac.yaml (Boltz inputs) +
nr4a3-ternary-prep.json (what was assembled / status). Boltz predictions (when GPU-run) land under
boltz_out/.
"""
import argparse
import json
import os
import sys
import urllib.parse
import urllib.request

import nr4a3_structure as ns  # reuse fetch_pdb (AFDB resolve + download)

HERE = os.path.dirname(__file__)
NR4A3 = "Q92570"
CRBN = "Q96SW2"
LBD_FIRST, LBD_LAST = 373, 626

THREE2ONE = {
    "ALA": "A", "ARG": "R", "ASN": "N", "ASP": "D", "CYS": "C", "GLN": "Q", "GLU": "E",
    "GLY": "G", "HIS": "H", "ILE": "I", "LEU": "L", "LYS": "K", "MET": "M", "PHE": "F",
    "PRO": "P", "SER": "S", "THR": "T", "TRP": "W", "TYR": "Y", "VAL": "V",
}
CHEMBL = "https://www.ebi.ac.uk/chembl/api/data/molecule.json?pref_name__iexact={name}"


def pdb_sequence(pdb, lo=None, hi=None):
    """One-letter sequence from CA records, optionally restricted to resnum [lo, hi]."""
    d = {}
    with open(pdb) as fh:
        for line in fh:
            if line.startswith("ATOM") and line[12:16].strip() == "CA":
                rid = int(line[22:26])
                if (lo is None or rid >= lo) and (hi is None or rid <= hi):
                    d[rid] = THREE2ONE.get(line[17:20].strip(), "X")
    return "".join(aa for _, aa in sorted(d.items()))


def fetch_seq(acc, lo=None, hi=None):
    pdb = ns.fetch_pdb(acc, os.path.join(os.environ.get("RUNNER_TEMP", "/tmp"), f"AF-{acc}.pdb"))
    return pdb_sequence(pdb, lo, hi)


def fetch_ligand_smiles(name):
    url = CHEMBL.format(name=urllib.parse.quote(name))
    with urllib.request.urlopen(url, timeout=60) as r:
        data = json.load(r)
    for m in data.get("molecules", []):
        s = (m.get("molecule_structures") or {}).get("canonical_smiles")
        if s:
            return s, m.get("molecule_chembl_id")
    raise RuntimeError(f"no ChEMBL SMILES for {name}")


def boltz_yaml(proteins, ligand_smiles):
    """Minimal Boltz-2 YAML: list of protein chains + one ligand (SMILES)."""
    lines = ["version: 1", "sequences:"]
    for cid, seq in proteins:
        lines += [f"  - protein:", f"      id: {cid}", f"      sequence: {seq}"]
    lines += ["  - ligand:", "      id: L", f"      smiles: '{ligand_smiles}'"]
    return "\n".join(lines) + "\n"


def have_gpu():
    try:
        import torch
        return torch.cuda.is_available()
    except Exception:  # noqa
        return False


def run_boltz(yaml_path, out_dir):
    import shutil
    import subprocess
    if not shutil.which("boltz"):
        print("  boltz not installed (pip install boltz) — GPU box only; skipping inference",
              file=sys.stderr)
        return None
    if not have_gpu():
        print("  no CUDA GPU detected — refusing to run Boltz on CPU (would be unusably slow). "
              "Dispatch gpu-ternary-aws.yml.", file=sys.stderr)
        return None
    # --no_kernels: use the pure-PyTorch triangle-multiplication path instead of the cuEquivariance/Triton
    # accelerated kernels. boltz>=2 HARD-CRASHES on this A10G container when the accel kernels' CUDA ops fail
    # to import (2026-07-01: ModuleNotFoundError then ops ImportError); --no_kernels avoids the whole
    # dependency chain — slower, but it runs. Chasing the exact cuequivariance/CUDA build match is a rabbit hole.
    cmd = ["boltz", "predict", yaml_path, "--use_msa_server", "--out_dir", out_dir, "--no_kernels"]
    print("  running:", " ".join(cmd), file=sys.stderr)
    return subprocess.run(cmd).returncode


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="store_true", help="run Boltz inference (needs GPU); else prep only")
    ap.add_argument("--e3-ligand", default="lenalidomide", help="ChEMBL name for the E3 ligand control")
    ap.add_argument("--protac-smiles", default=os.environ.get("PROTAC_SMILES", ""),
                    help="PROTAC SMILES for the real NR4A3 ternary (none until a warhead exists)")
    args = ap.parse_args()

    out = {"_note": "NR4A3–PROTAC–E3 ternary modelling prep (Boltz-2). Control = CRBN + E3 ligand "
                    "(known answer); ternary = NR4A3 LBD + CRBN + PROTAC (template until a warhead "
                    "SMILES exists). Inference needs GPU.", "status": {}}
    try:
        nr4a3_lbd = fetch_seq(NR4A3, LBD_FIRST, LBD_LAST)
        crbn = fetch_seq(CRBN)
        out["nr4a3_lbd_len"] = len(nr4a3_lbd)
        out["crbn_len"] = len(crbn)
    except Exception as e:  # noqa
        out["status"]["sequences"] = f"error: {e}"
        json.dump(out, open(os.path.join(HERE, "nr4a3-ternary-prep.json"), "w"), indent=2)
        print(f"sequence fetch failed: {e}", file=sys.stderr)
        return

    # (1) positive control: CRBN + E3 ligand (known to bind the tri-Trp pocket)
    try:
        e3_smiles, e3_id = fetch_ligand_smiles(args.e3_ligand)
        ctrl = boltz_yaml([("A", crbn)], e3_smiles)
        open(os.path.join(HERE, "nr4a3-ternary-control.yaml"), "w").write(ctrl)
        out["control"] = {"complex": f"CRBN + {args.e3_ligand}", "ligand_chembl": e3_id,
                          "expected": "imide seats in CRBN tri-Trp pocket (W380/W386/W400 region)"}
    except Exception as e:  # noqa
        out["status"]["control"] = f"error: {e}"

    # (2) real ternary template: NR4A3 LBD + CRBN + PROTAC
    if args.protac_smiles:
        tern = boltz_yaml([("A", nr4a3_lbd), ("B", crbn)], args.protac_smiles)
        open(os.path.join(HERE, "nr4a3-ternary-protac.yaml"), "w").write(tern)
        out["ternary"] = {"complex": "NR4A3-LBD + CRBN + PROTAC", "protac_smiles": args.protac_smiles,
                          "scoring": "look for an exposed NR4A3 Lys near CRBN within ubiquitin reach"}
    else:
        out["ternary"] = {"status": "TEMPLATE — supply --protac-smiles / $PROTAC_SMILES once a "
                          "selective NR4A3 warhead is designed (degrader experiment #2)"}

    if args.run:
        out_dir = os.path.join(HERE, "boltz_out")
        os.makedirs(out_dir, exist_ok=True)
        ctrl_yaml = os.path.join(HERE, "nr4a3-ternary-control.yaml")
        out["status"]["control_run"] = run_boltz(ctrl_yaml, out_dir)
        tern_yaml = os.path.join(HERE, "nr4a3-ternary-protac.yaml")
        if os.path.exists(tern_yaml):
            out["status"]["ternary_run"] = run_boltz(tern_yaml, out_dir)

    json.dump(out, open(os.path.join(HERE, "nr4a3-ternary-prep.json"), "w"), indent=2)
    print(json.dumps({k: out.get(k) for k in
                      ("nr4a3_lbd_len", "crbn_len", "control", "ternary", "status")}, indent=2))

    # Fail loud: a Boltz run that returned non-zero must exit non-zero, not report false-green (the prep JSON
    # above is already written, so partials still upload). None = skipped (no GPU / not installed) → not a failure.
    if args.run:
        rcs = [out["status"].get("control_run"), out["status"].get("ternary_run")]
        failed = [rc for rc in rcs if rc not in (0, None)]
        if failed:
            sys.exit(f"Boltz inference FAILED (return codes {failed}); see traceback above.")


if __name__ == "__main__":
    main()
