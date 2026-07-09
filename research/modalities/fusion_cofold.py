#!/usr/bin/env python3
"""
Fusion-junction apo co-fold for EWSR1::NR4A3 EMC — does a druggable pocket form at the fused area itself?

WHY. The repo's NR4A3-LBD degrader binds a domain SHARED by the fusion and wild-type NR4A3, so it is
NR4A3-selective, NOT fusion-selective. A truly fusion-exclusive *small-molecule* target would be a pocket
that exists only in the chimera — most plausibly a COMPOSITE pocket created where the EWSR1 low-complexity
(LC) domain is juxtaposed to NR4A3, a cavity present in neither parent. This script tests, in silico,
whether the two fused halves fold TOGETHER into any such ordered interface / cavity, using the same Boltz-2
(AF3-class) predictor the degrader program used for co-folding.

HONEST PRIOR. The EWSR1 side is an intrinsically disordered prion-like LC domain (mean pLDDT 38.8; 98% of
residues < 50), and the seam is disorder(EWS-LC)::disorder(NR4A3-AF1); a folded composite pocket is
unlikely. Also, a de-novo fusion junction has NO cross-seam coevolution, so an MSA-based predictor has no
evidence for any specific inter-half packing and will default to independent domains + a floppy linker —
absence of a predicted co-fold is therefore expected and is a feasibility read, not proof no pocket can
form. This is a cheap, decisive first screen, not a claim.

CONSTRUCTS (single chimeric chain, apo — no ligand; canonical EMC breakpoint EWSR1 res 264 :: NR4A3 res 2):
  (1) seam      — EWSR1[145..264] :: NR4A3[2..260]   — the TRUE junction geometry (EWS-LC C-terminus fused
                  to NR4A3's retained, disordered AF1). Asks: does anything order AT the fused junction?
  (2) composite — EWSR1[145..264] :: NR4A3[261..626] — NR4A3's DBD+LBD folded core. The disordered AF1
                  spacer is DELIBERATELY removed so the EWS tail is given the BEST possible chance to pack
                  onto the NR4A3 fold: a generous upper-bound test for a composite EWSxNR4A3 pocket. If even
                  this does not fold together, the composite-pocket route is dead.

Controls = the parent AlphaFold models (WT EWSR1 Q01844, WT NR4A3 Q92570); no fold needed — the reporter
compares any fusion-interface cavity against parent pockets to check it is genuinely fusion-emergent.

Inference needs a GPU (Boltz/torch); runs as-is and skips gracefully in CI. Tool is Boltz-2.

Outputs (written incrementally into $OUTPUT_DIR so a timeout still uploads finished constructs — the
checkpoint/continuous-upload standing rule): per-construct Boltz apo predictions + the input YAMLs +
fusion-cofold-prep.json (constructs assembled, residue ranges, block boundary for the reporter).
"""
import argparse
import json
import os
import sys

import nr4a3_structure as ns  # reuse fetch_pdb (AFDB resolve + download)

HERE = os.path.dirname(__file__)
OUT_DIR = os.environ.get("OUTPUT_DIR", os.path.join(HERE, "cofold_out"))

EWSR1 = "Q01844"   # UniProt / AFDB — EWS RNA-binding protein 1
NR4A3 = "Q92570"   # UniProt / AFDB — NR4A3 (NOR-1)

# Canonical EMC junction: EWSR1 EAD kept to res 264 (exon-7 end) :: NR4A3 resumed at res 2 (matches the
# repo's modelled breakpoint used by fusion_neoantigen.py). Residue ranges are 1-based, inclusive.
EWS_CUT = 264            # EWSR1 breakpoint residue (end of the EAD / prion-like TAD)
EWS_SEAM_LEN = 120       # keep the C-terminal 120 aa of the EAD (seam-proximal); the distal N-terminal LC
                         #   cannot reach a junction fold and only inflates the N^2 Boltz cost
NR4A3_AF1_END = 260      # NR4A3 disordered AF1 remnant retained downstream of the seam (res 2..260)
NR4A3_CORE_START = 261   # NR4A3 folded core begins (DBD 261-337 ... LBD 373-626)
NR4A3_END = 626

THREE2ONE = {
    "ALA": "A", "ARG": "R", "ASN": "N", "ASP": "D", "CYS": "C", "GLN": "Q", "GLU": "E",
    "GLY": "G", "HIS": "H", "ILE": "I", "LEU": "L", "LYS": "K", "MET": "M", "PHE": "F",
    "PRO": "P", "SER": "S", "THR": "T", "TRP": "W", "TYR": "Y", "VAL": "V",
}


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


def boltz_yaml_apo(chains):
    """Minimal Boltz-2 YAML for an apo (ligand-free) prediction of one or more protein chains."""
    lines = ["version: 1", "sequences:"]
    for cid, seq in chains:
        lines += ["  - protein:", f"      id: {cid}", f"      sequence: {seq}"]
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
        print("  boltz not installed (pip install boltz) — GPU box only; skipping inference", file=sys.stderr)
        return None
    if not have_gpu():
        print("  no CUDA GPU detected — refusing to run Boltz on CPU (unusably slow). Dispatch "
              "gpu-cofold-aws.yml.", file=sys.stderr)
        return None
    # --no_kernels: pure-PyTorch triangle path (boltz>=2 hard-crashes on the A10G when the accelerated
    # cuEquivariance kernels fail to import — the 2026-07-01 ternary incident). Slower but runs.
    cmd = ["boltz", "predict", yaml_path, "--use_msa_server", "--out_dir", out_dir, "--no_kernels"]
    print("  running:", " ".join(cmd), file=sys.stderr)
    return subprocess.run(cmd).returncode


def _write_prep(out):
    os.makedirs(OUT_DIR, exist_ok=True)
    json.dump(out, open(os.path.join(OUT_DIR, "fusion-cofold-prep.json"), "w"), indent=2)
    json.dump(out, open(os.path.join(HERE, "fusion-cofold-prep.json"), "w"), indent=2)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="store_true", help="run Boltz inference (needs GPU); else prep only")
    ap.add_argument("--control", action="store_true", help="no-op; keeps the SageMaker arg list non-empty")
    args = ap.parse_args()

    os.makedirs(OUT_DIR, exist_ok=True)
    out = {"_note": "EWSR1::NR4A3 fusion-junction apo co-fold (Boltz-2). Tests whether the fused halves "
                    "fold together into a composite interface/pocket present in neither parent. Two "
                    "chimeric constructs; parents (WT EWSR1/NR4A3) are AFDB controls handled by the reporter.",
           "breakpoint": f"EWSR1 res {EWS_CUT} :: NR4A3 res 2 (canonical EMC)",
           "constructs": {}, "status": {}}

    try:
        ews_seam = fetch_seq(EWSR1, EWS_CUT - EWS_SEAM_LEN + 1, EWS_CUT)     # EWSR1 145..264
        nr4a3_af1 = fetch_seq(NR4A3, 2, NR4A3_AF1_END)                       # NR4A3 2..260
        nr4a3_core = fetch_seq(NR4A3, NR4A3_CORE_START, NR4A3_END)           # NR4A3 261..626
    except Exception as e:  # noqa
        out["status"]["sequences"] = f"error: {e}"
        _write_prep(out)
        sys.exit(f"sequence fetch failed: {e}")

    constructs = {
        "seam": {
            "chain": ews_seam + nr4a3_af1,
            "ews_range": [EWS_CUT - EWS_SEAM_LEN + 1, EWS_CUT], "ews_len": len(ews_seam),
            "nr4a3_range": [2, NR4A3_AF1_END], "nr4a3_len": len(nr4a3_af1),
            "block_boundary": len(ews_seam),
            "hypothesis": "true junction geometry (EWS-LC :: NR4A3 AF1); does anything order at the seam?",
        },
        "composite": {
            "chain": ews_seam + nr4a3_core,
            "ews_range": [EWS_CUT - EWS_SEAM_LEN + 1, EWS_CUT], "ews_len": len(ews_seam),
            "nr4a3_range": [NR4A3_CORE_START, NR4A3_END], "nr4a3_len": len(nr4a3_core),
            "block_boundary": len(ews_seam),
            "hypothesis": "generous upper bound (AF1 spacer removed) — best chance for an EWSxNR4A3-core "
                          "composite pocket; if this fails, the route is dead",
        },
    }
    for name, c in constructs.items():
        yml = boltz_yaml_apo([("A", c["chain"])])
        for d in (OUT_DIR, HERE):
            open(os.path.join(d, f"{name}.yaml"), "w").write(yml)
        out["constructs"][name] = {k: v for k, v in c.items() if k != "chain"}
        out["constructs"][name]["total_len"] = len(c["chain"])
    _write_prep(out)
    print(json.dumps(out["constructs"], indent=2))

    if args.run:
        for name in constructs:                       # seam first (smaller); upload incrementally
            yml = os.path.join(OUT_DIR, f"{name}.yaml")
            out["status"][f"{name}_run"] = run_boltz(yml, OUT_DIR)
            _write_prep(out)

    # Fail loud: any Boltz run that returned non-zero must exit non-zero (prep JSON already uploaded).
    if args.run:
        failed = [rc for k, rc in out["status"].items() if k.endswith("_run") and rc not in (0, None)]
        if failed:
            sys.exit(f"Boltz inference FAILED (return codes {failed}); see traceback above.")


if __name__ == "__main__":
    main()
