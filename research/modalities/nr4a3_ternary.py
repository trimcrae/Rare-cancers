#!/usr/bin/env python3
"""
NR4A–PROTAC–E3 ternary-complex modelling (degrader GPU experiment #3 — degradation geometry).

WHY. A degrader's *degradation* selectivity is set by the ternary complex, not by warhead binding alone
(paper §2.7 / caveat 5): a non-selective binder can degrade selectively (productive ternary on only one
paralogue) and a selective binder can fail to degrade. So the highest-value degradation experiment is to
fold **NR4A-LBD + E3 substrate receptor (CRBN) + PROTAC** for each paralogue and ask whether the recruited
complex presents a solvent-exposed lysine near the E3 in a geometry compatible with ubiquitin transfer.
This is the red-team **F18** mitigation: the CRBN+lenalidomide control (below) is an in-distribution sanity
check; the NR4A-specific ternary predictions here are the actual, previously-un-run result.

WHAT (2026-07-01, extended from NR4A3-only to the whole family for the degradation-selectivity read):
  (1) CONTROL (known answer): CRBN + lenalidomide — the imide should seat in CRBN's tri-Trp pocket
      (W380/W386/W400). If Boltz can't recover that, we don't trust the NR4A ternaries.
  (2) TERNARY, per paralogue: **NR4A{3,1,2}-LBD + CRBN + PROTAC**, with the PROTAC SMILES taken from
      $PROTAC_SMILES / --protac-smiles. Running all three lets us compare degradation geometry across the
      family (does the productive, Lys-near-CRBN geometry form for NR4A3 but *not* NR4A1/NR4A2?), which is
      the ternary contribution to paralogue selectivity §2.7 calls the highest-value un-run experiment.

LBD definition: the NR4A ligand-binding domain is the C-terminal domain; NR4A3's repo range (373-626) is
exactly its **last 254 residues**, so we define each paralogue's LBD the same principled way (last 254
residues; NR4A3 kept explicit at 373-626 for exact reproducibility) — no alignment/dependency needed.

Inference needs a GPU (Boltz/torch); prepared to run as-is and skips gracefully in CI. Tool is Boltz-2.

Outputs (written incrementally into $OUTPUT_DIR so a timeout still uploads completed targets — the
checkpoint/continuous-upload standing rule): the Boltz input YAMLs, per-target Boltz predictions under
<OUTPUT_DIR>/, and nr4a3-ternary-prep.json (what was assembled / status), updated after each target.
"""
import argparse
import json
import os
import sys
import urllib.parse
import urllib.request

import nr4a3_structure as ns  # reuse fetch_pdb (AFDB resolve + download)

HERE = os.path.dirname(__file__)
OUT_DIR = os.environ.get("OUTPUT_DIR", os.path.join(HERE, "boltz_out"))
CRBN = "Q96SW2"
# (accession, lbd_first, lbd_last) — None/None = take the C-terminal 254 residues (matches NR4A3 373-626).
NR4A_TARGETS = {
    "NR4A3": ("Q92570", 373, 626),
    "NR4A1": ("P22736", None, None),
    "NR4A2": ("P43354", None, None),
}
LBD_LEN = 254  # NR4A3 373..626 inclusive == 254 residues; the family LBD is this C-terminal domain.

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


def lbd_seq(acc, lo, hi):
    """LBD one-letter sequence: explicit [lo,hi] if given, else the C-terminal LBD_LEN residues."""
    if lo is not None and hi is not None:
        return fetch_seq(acc, lo, hi)
    full = fetch_seq(acc)
    return full[-LBD_LEN:]


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
        lines += ["  - protein:", f"      id: {cid}", f"      sequence: {seq}"]
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
    # --no_kernels: pure-PyTorch triangle path. boltz>=2 HARD-CRASHES on this A10G container when the
    # accelerated cuEquivariance/Triton kernels' CUDA ops fail to import (2026-07-01); --no_kernels avoids
    # the whole dependency chain — slower, but it runs.
    cmd = ["boltz", "predict", yaml_path, "--use_msa_server", "--out_dir", out_dir, "--no_kernels"]
    print("  running:", " ".join(cmd), file=sys.stderr)
    return subprocess.run(cmd).returncode


def _write_prep(out):
    os.makedirs(OUT_DIR, exist_ok=True)
    json.dump(out, open(os.path.join(OUT_DIR, "nr4a3-ternary-prep.json"), "w"), indent=2)
    # also keep a copy next to the code (back-compat with the old reporter path)
    json.dump(out, open(os.path.join(HERE, "nr4a3-ternary-prep.json"), "w"), indent=2)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="store_true", help="run Boltz inference (needs GPU); else prep only")
    ap.add_argument("--e3-ligand", default="lenalidomide", help="ChEMBL name for the E3 ligand control")
    ap.add_argument("--protac-smiles", default=os.environ.get("PROTAC_SMILES", ""),
                    help="PROTAC SMILES for the real NR4A ternaries (none until a warhead exists)")
    ap.add_argument("--binary-smiles", default=os.environ.get("BINARY_SMILES", ""),
                    help="warhead SMILES for BINARY co-folding: NR4A{3,1,2}-LBD + warhead (AF3-class independent "
                         "cross-check of the docked pose + cross-paralogue confidence; NOT the ternary)")
    ap.add_argument("--control", action="store_true", help="no-op; keeps the SageMaker arg list non-empty")
    args = ap.parse_args()

    os.makedirs(OUT_DIR, exist_ok=True)
    out = {"_note": "NR4A–PROTAC–E3 ternary modelling (Boltz-2). Control = CRBN + E3 ligand (known "
                    "answer); ternaries = NR4A{3,1,2}-LBD + CRBN + PROTAC. Degradation-geometry read = an "
                    "exposed NR4A Lys near CRBN (ubiquitin reach). Inference needs GPU.",
           "lbd_definition": f"C-terminal {LBD_LEN} residues (NR4A3 == 373-626)",
           "targets": {}, "status": {}}

    # sequences
    try:
        crbn = fetch_seq(CRBN)
        out["crbn_len"] = len(crbn)
        for name, (acc, lo, hi) in NR4A_TARGETS.items():
            seq = lbd_seq(acc, lo, hi)
            out["targets"][name] = {"accession": acc, "lbd_len": len(seq)}
    except Exception as e:  # noqa
        out["status"]["sequences"] = f"error: {e}"
        _write_prep(out)
        print(f"sequence fetch failed: {e}", file=sys.stderr)
        return
    _write_prep(out)

    # (1) positive control: CRBN + E3 ligand (known to bind the tri-Trp pocket)
    try:
        e3_smiles, e3_id = fetch_ligand_smiles(args.e3_ligand)
        ctrl = boltz_yaml([("A", crbn)], e3_smiles)
        open(os.path.join(OUT_DIR, "nr4a3-ternary-control.yaml"), "w").write(ctrl)
        open(os.path.join(HERE, "nr4a3-ternary-control.yaml"), "w").write(ctrl)
        out["control"] = {"complex": f"CRBN + {args.e3_ligand}", "ligand_chembl": e3_id,
                          "expected": "imide seats in CRBN tri-Trp pocket (W380/W386/W400 region)"}
    except Exception as e:  # noqa
        out["status"]["control"] = f"error: {e}"
    _write_prep(out)

    # (2) real ternaries: NR4A{3,1,2}-LBD + CRBN + PROTAC (one YAML per paralogue)
    if args.protac_smiles:
        for name, (acc, lo, hi) in NR4A_TARGETS.items():
            seq = lbd_seq(acc, lo, hi)
            tern = boltz_yaml([("A", seq), ("B", crbn)], args.protac_smiles)
            stem = f"{name.lower()}-ternary-protac.yaml"
            open(os.path.join(OUT_DIR, stem), "w").write(tern)
            open(os.path.join(HERE, stem), "w").write(tern)
            out["targets"][name]["yaml"] = stem
        out["ternary"] = {"complex": "NR4A{3,1,2}-LBD + CRBN + PROTAC", "protac_smiles": args.protac_smiles,
                          "scoring": "exposed NR4A Lys near CRBN within ubiquitin reach; compare across paralogues"}
    else:
        out["ternary"] = {"status": "TEMPLATE — supply --protac-smiles / $PROTAC_SMILES once a selective "
                          "NR4A warhead is designed"}
    _write_prep(out)

    # (3) BINARY co-folding (AF3-class): NR4A{3,1,2}-LBD + warhead alone, per paralogue. Independent
    # complex-prediction cross-check of the docked pose + a cross-paralogue confidence read (does Boltz seat
    # the warhead in NR4A3 with higher confidence than NR4A1/2?). Cryptic-pocket caveat lives in the paper.
    if args.binary_smiles:
        for name, (acc, lo, hi) in NR4A_TARGETS.items():
            seq = lbd_seq(acc, lo, hi)
            b = boltz_yaml([("A", seq)], args.binary_smiles)
            stem = f"{name.lower()}-binary.yaml"
            open(os.path.join(OUT_DIR, stem), "w").write(b)
            open(os.path.join(HERE, stem), "w").write(b)
            out["targets"][name]["binary_yaml"] = stem
        out["binary"] = {"complex": "NR4A{3,1,2}-LBD + warhead (no E3)", "binary_smiles": args.binary_smiles,
                         "scoring": "compare ligand-pocket iptm/plddt/PAE + pose vs docked across paralogues; "
                                    "CAVEAT: cryptic pocket + de-novo ligand is the hardest co-folding regime — "
                                    "a low/closed-pocket prediction is informative, high confidence read skeptically"}
        _write_prep(out)

    if args.run:
        # control first (cheap, validates the pipeline), then each paralogue ternary; upload incrementally.
        ctrl_yaml = os.path.join(OUT_DIR, "nr4a3-ternary-control.yaml")
        if os.path.exists(ctrl_yaml):
            out["status"]["control_run"] = run_boltz(ctrl_yaml, OUT_DIR)
            _write_prep(out)
        if args.protac_smiles:
            for name in NR4A_TARGETS:
                yml = os.path.join(OUT_DIR, f"{name.lower()}-ternary-protac.yaml")
                if os.path.exists(yml):
                    out["status"][f"{name}_run"] = run_boltz(yml, OUT_DIR)
                    _write_prep(out)
        if args.binary_smiles:
            for name in NR4A_TARGETS:
                yml = os.path.join(OUT_DIR, f"{name.lower()}-binary.yaml")
                if os.path.exists(yml):
                    out["status"][f"{name}_binary_run"] = run_boltz(yml, OUT_DIR)
                    _write_prep(out)

    print(json.dumps({k: out.get(k) for k in
                      ("crbn_len", "targets", "control", "ternary", "status")}, indent=2))

    # Fail loud: any Boltz run that returned non-zero must exit non-zero (prep JSON already uploaded, so
    # partials survive). None = skipped (no GPU / not installed) → not a failure.
    if args.run:
        rcs = [v for k, v in out["status"].items() if k.endswith("_run")]
        failed = [rc for rc in rcs if rc not in (0, None)]
        if failed:
            sys.exit(f"Boltz inference FAILED (return codes {failed}); see traceback above.")


if __name__ == "__main__":
    main()
