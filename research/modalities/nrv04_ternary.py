#!/usr/bin/env python3
"""
Retrospective NR-V04 three-paralogue ternary benchmark (Track B) — the family-matched POSITIVE CONTROL for a
paralogue-discriminating ternary workflow (gate-AI, 2026-07-11). Full spec + rationale + verdict gate:
`nrv04-ternary-benchmark.json`.

THE TEST. NR-V04 (Wang 2024) DEGRADES NR4A1 but SPARES NR4A2/NR4A3. A ternary workflow we would trust to
*discover* NR4A3 selectivity must first *recover* this KNOWN NR4A1 preference. So we co-fold, per paralogue,
NR4A{1,2,3}-LBD + VHL(+ElonginB/C) + NR-V04, over an ENSEMBLE of seeds, and ask whether the NR4A1 assembly is
favoured (interface / ternary confidence / Lys-presentation) over NR4A2/NR4A3.

Distinct from nr4a3_ternary.py (which does the CRBN degradation-geometry prediction): this is VHL, the NR-V04
PROTAC, N-seed ensembles, and the retrospective known-answer benchmark. It REUSES that module's proven helpers
(sequence fetch, Boltz YAML, `boltz predict --no_kernels`).

SINGLE-LEG-FIRST (CLAUDE.md). `--pilot` runs ONLY the cheap decision-relevant leg — the VHL+VH032 positive
control + the NR4A1 (known-degraded) ternary over a few seeds. Abort the full fleet if the control can't seat
VH032 in VHL, or NR4A1 can't form a productive, seed-persistent ternary (then the workflow can't even recover
the positive case). Only on a clean pilot do we fan out NR4A2 + NR4A3 (× seeds × linker variants).

Inference needs a GPU (Boltz-2); prepares YAMLs + skips gracefully in CI. Outputs written incrementally to
$OUTPUT_DIR (checkpoint/continuous-upload rule).
"""
import argparse
import json
import os
import sys

import nr4a3_ternary as t3   # reuse: fetch_seq, lbd_seq, boltz_yaml, run_boltz, fetch_ligand_smiles, pdb_sequence

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.environ.get("OUTPUT_DIR", os.path.join(HERE, "nrv04_ternary_out"))
SPEC = os.path.join(HERE, "nrv04-ternary-benchmark.json")

# E3 machinery — VHL and its VBC partners (VHL is only functional in the ElonginB/C complex).
VHL = "P40337"
ELONGIN_B = "P62258"
ELONGIN_C = "Q15369"
# NR4A targets + the retrospective ground truth (Wang 2024): NR4A1 degraded; NR4A2/NR4A3 spared.
TARGETS = {
    "NR4A1": {"acc": "P22736", "lo": None, "hi": None, "truth": "degraded"},
    "NR4A2": {"acc": "P43354", "lo": None, "hi": None, "truth": "spared"},
    "NR4A3": {"acc": "Q92570", "lo": 373, "hi": 626, "truth": "spared"},
}
VH032_NAME = "VH032"   # the VHL-ligand positive control (should seat in VHL's hydroxyproline pocket)


def resolve_vh032_smiles():
    """Resolve the VH032 positive-control ligand robustly. VH032 does NOT resolve by pref_name in ChEMBL
    (the 2026-07-11 pilot silently skipped the control for this reason), so try, in order:
      1. $VH032_SMILES / $NRV04_VH032_SMILES env override (authoritative if the caller sets a verified SMILES),
      2. ChEMBL by name (t3.fetch_ligand_smiles — kept for back-compat; usually misses),
      3. PubChem PUG-REST by name ('VH-032' then 'VH032') → canonical SMILES,
      4. the benchmark spec's control_ligand.smiles if present.
    Returns (smiles, source_label). Never invents a structure — raises if every route fails."""
    import urllib.parse
    import urllib.request
    for var in ("VH032_SMILES", "NRV04_VH032_SMILES"):
        if os.environ.get(var):
            return os.environ[var], "env:%s" % var
    # Prefer the VERIFIED spec SMILES (RDKit-validated, warhead cross-checked vs NR-V04) — deterministic and
    # provenance-clean — over the flaky name lookups that silently skipped the control in the first two runs.
    with open(SPEC) as f:
        spec = json.load(f)
    cl = (spec.get("control_ligand") or {}).get("smiles")
    if cl:
        return cl, "nrv04-ternary-benchmark.json:control_ligand"
    try:
        s, cid = t3.fetch_ligand_smiles(VH032_NAME)
        if s:
            return s, "chembl:%s" % cid
    except Exception:  # noqa: BLE001 — ChEMBL name miss is expected; fall through to PubChem
        pass
    for nm in ("VH-032", "VH032"):
        try:
            url = ("https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/%s/property/"
                   "CanonicalSMILES/JSON" % urllib.parse.quote(nm))
            with urllib.request.urlopen(url, timeout=60) as r:
                props = json.load(r)["PropertyTable"]["Properties"]
            if props and props[0].get("CanonicalSMILES"):
                return props[0]["CanonicalSMILES"], "pubchem:name=%s" % nm
        except Exception:  # noqa: BLE001
            continue
    raise RuntimeError("could not resolve VH032 SMILES (env/spec/ChEMBL/PubChem all missed); set $VH032_SMILES")


def load_nrv04_smiles():
    """The representative NR-V04 SMILES from the benchmark spec (celastrol + 4-PEG + VH032; flagged
    representative). Overridable via $NRV04_SMILES. Never silently invented — read from the committed spec."""
    s = os.environ.get("NRV04_SMILES")
    if s:
        return s, "env"
    with open(SPEC) as f:
        spec = json.load(f)
    return spec["nrv04"]["representative_smiles"], "nrv04-ternary-benchmark.json"


def e3_chains(with_vbc):
    """VHL (+ ElonginB/C when with_vbc) as (chain_id, sequence) tuples for the Boltz YAML."""
    chains = [("E", t3.fetch_seq(VHL))]
    if with_vbc:
        chains.append(("F", t3.fetch_seq(ELONGIN_B)))
        chains.append(("G", t3.fetch_seq(ELONGIN_C)))
    return chains


def yaml_with_seed(proteins, ligand_smiles, seed):
    """Boltz-2 YAML for a protein set + one ligand, with an explicit diffusion seed (ensemble member).
    Reuses t3.boltz_yaml then appends the seed as a top-level key Boltz honours via --seed at run time; here we
    only tag the filename by seed and pass --seed to boltz in run_ensemble (kept out of the YAML for
    compatibility)."""
    return t3.boltz_yaml(proteins, ligand_smiles)


def run_ensemble(yaml_path, out_dir, seeds):
    """Run Boltz on one system across N seeds (the ensemble). Returns {seed: returncode}. Each seed writes to
    its own subdir so the poses/confidences don't overwrite. run_boltz already uses --no_kernels."""
    import subprocess
    import shutil
    res = {}
    if not shutil.which("boltz") or not t3.have_gpu():
        print("  boltz/GPU unavailable — prep only (dispatch the GPU workflow)", file=sys.stderr)
        return {s: None for s in seeds}
    for s in seeds:
        sdir = os.path.join(out_dir, "seed_%d" % s)
        os.makedirs(sdir, exist_ok=True)
        cmd = ["boltz", "predict", yaml_path, "--use_msa_server", "--out_dir", sdir,
               "--no_kernels", "--seed", str(s)]
        print("  running:", " ".join(cmd), file=sys.stderr)
        res[s] = subprocess.run(cmd).returncode
    return res


def _write(out):
    os.makedirs(OUT_DIR, exist_ok=True)
    json.dump(out, open(os.path.join(OUT_DIR, "nrv04-ternary-prep.json"), "w"), indent=2)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="store_true", help="run Boltz inference (needs GPU); else prep YAMLs only")
    ap.add_argument("--pilot", action="store_true",
                    help="single-leg-first: only the VHL+VH032 control + the NR4A1 (known-degraded) ternary")
    ap.add_argument("--control-only", action="store_true",
                    help="run ONLY the VHL+VH032 positive control ensemble (cheap re-run to backfill a skipped control)")
    ap.add_argument("--seeds", default=os.environ.get("SEEDS", "1,2,3"),
                    help="comma-sep diffusion seeds = the ternary ENSEMBLE per system")
    ap.add_argument("--with-vbc", default=os.environ.get("WITH_VBC", "1"),
                    help="1 = include ElonginB/C with VHL (the functional VBC complex); 0 = VHL alone")
    args = ap.parse_args()
    seeds = [int(x) for x in str(args.seeds).split(",") if x.strip()]
    with_vbc = str(args.with_vbc).strip() not in ("0", "", "false", "no")

    nrv04_smiles, nrv04_src = load_nrv04_smiles()
    control_only = args.control_only
    targets = [] if control_only else (["NR4A1"] if args.pilot else list(TARGETS))
    out = {"_note": "Retrospective NR-V04 ternary benchmark (VHL). Control = VHL(+VBC)+VH032 (known answer). "
                    "Ternaries = NR4A{1,2,3}-LBD + VHL(+VBC) + NR-V04, over a seed ENSEMBLE. Ground truth: "
                    "NR4A1 degraded, NR4A2/NR4A3 spared (Wang 2024).",
           "mode": "control-only" if control_only else ("pilot" if args.pilot else "full"),
           "seeds": seeds, "with_vbc": with_vbc,
           "nrv04_smiles_source": nrv04_src, "ground_truth": {k: v["truth"] for k, v in TARGETS.items()},
           "targets": {}, "status": {}}
    os.makedirs(OUT_DIR, exist_ok=True)

    # sequences (fail loud, prep-safe)
    try:
        e3 = e3_chains(with_vbc)
        out["e3"] = {"VHL": VHL, "with_vbc": with_vbc, "chains": [c for c, _ in e3]}
    except Exception as e:  # noqa: BLE001
        out["status"]["sequences"] = "error: %s" % e
        _write(out)
        print("E3 sequence fetch failed: %s" % e, file=sys.stderr)
        return
    _write(out)

    # (1) positive control: VHL(+VBC) + VH032 — the VHL analogue of the CRBN+lenalidomide control.
    try:
        vh_smiles, vh_src = resolve_vh032_smiles()
        ctrl = t3.boltz_yaml(e3, vh_smiles)
        open(os.path.join(OUT_DIR, "control-vhl-vh032.yaml"), "w").write(ctrl)
        out["control"] = {"complex": "VHL%s + VH032" % ("+EloB/C" if with_vbc else ""),
                          "ligand_smiles": vh_smiles, "ligand_source": vh_src,
                          "expected": "hydroxyproline ligand seats in VHL's substrate pocket; if not, distrust every VHL ternary"}
    except Exception as e:  # noqa: BLE001
        out["status"]["control"] = "error: %s (set $VH032_SMILES to a verified control SMILES)" % e
    _write(out)

    # (2) ternaries: NR4A{targets}-LBD + VHL(+VBC) + NR-V04, one YAML per paralogue.
    for name in targets:
        acc, lo, hi = TARGETS[name]["acc"], TARGETS[name]["lo"], TARGETS[name]["hi"]
        seq = t3.lbd_seq(acc, lo, hi)
        proteins = [("A", seq)] + e3
        y = t3.boltz_yaml(proteins, nrv04_smiles)
        stem = "%s-nrv04-ternary.yaml" % name.lower()
        open(os.path.join(OUT_DIR, stem), "w").write(y)
        out["targets"][name] = {"accession": acc, "lbd_len": len(seq), "yaml": stem,
                                "truth": TARGETS[name]["truth"]}
    out["ternary"] = {"complex": "NR4A-LBD + VHL(+VBC) + NR-V04", "n_seeds": len(seeds),
                      "readouts": "interface area/complementarity, ligand-iPTM distribution across seeds, "
                                  "linker strain, exposed Lys near VHL (ubiquitin reach), seed persistence; "
                                  "compare NR4A1 vs NR4A2/NR4A3 (see nrv04-ternary-benchmark.json)"}
    _write(out)

    if args.run:
        cy = os.path.join(OUT_DIR, "control-vhl-vh032.yaml")
        if os.path.exists(cy):
            out["status"]["control_run"] = run_ensemble(cy, os.path.join(OUT_DIR, "control"), seeds)
            _write(out)
        for name in targets:
            yml = os.path.join(OUT_DIR, "%s-nrv04-ternary.yaml" % name.lower())
            if os.path.exists(yml):
                out["status"]["%s_run" % name] = run_ensemble(yml, os.path.join(OUT_DIR, name.lower()), seeds)
                _write(out)
    print("wrote %s (mode=%s, targets=%s, seeds=%s)" % (
        os.path.join(OUT_DIR, "nrv04-ternary-prep.json"), out["mode"], targets, seeds))


if __name__ == "__main__":
    main()
