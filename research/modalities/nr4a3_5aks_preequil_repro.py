#!/usr/bin/env python3
"""RUNG 5a-KS — reproduce the pre-equilibration failure on CPU, and prove the fix, for $0.

WHY THIS EXISTS. The first 5a-KS smoke leg (unit `5aks_d0_to_d__ternary_nr4a3_r0_dt4.0fs_wu1.0_5aks_smoke`,
2026-07-26) cleared the CUDA probe, the repo pull and staging — the pre-seeded stage cache HIT — and then
died with `{"status":"failed","phase":"preequil","rc":1}`. The hypothesis is that a co-fold-derived
`complex.pdb` reaches OpenMM with **no hydrogens and no terminal OXT**, so `ForceField.createSystem` fails
template matching; that is the same wall the CRYSTAL stager hit on 2026-07-17 and fixed with PDBFixer
(`ternary_pdb_stage._hydrogenate_pdb`), which this rung's stager did not call.

**A plausible story is a hypothesis, not a diagnosis**, so this runs the ONE observation that discriminates:
the same `ternary_preequil` invocation, in the same parity image, against two `complex.pdb` files differing
only in hydrogenation.

    ARM A (unfixed)  — hydrogens stripped back out. MUST fail, and fail the way the leg did.
    ARM B (fixed)    — the staged tree as `nr4a3_5aks_stage` now writes it. MUST get past the system build.

If ARM A passes, the hypothesis is WRONG and the real cause is still unfound — that outcome is reported
loudly rather than smoothed over, because it would mean re-renting on a cause nobody has actually identified.

Runs on a free CPU runner (`OPENMM_PLATFORM=CPU`, a 2 ps `PREEQUIL_SMOKE`), never on a rented GPU: the
failure is in system CONSTRUCTION, which is pure CPU, so paying a 4090 to reproduce it would be the exact
anti-pattern the repo's CPU-prime rule exists to kill.
"""
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

LEG = "5aks_d0_to_d__ternary_nr4a3"


def count_atoms(pdb):
    """(n_atoms, n_hydrogens) from the PDB element column — cols 77-78, right-justified."""
    n = h = 0
    with open(pdb) as fh:
        for line in fh:
            if line.startswith(("ATOM", "HETATM")):
                n += 1
                if line[76:78].strip().upper() == "H":
                    h += 1
    return n, h


def strip_hydrogens(src, dst):
    """The state the failing leg actually ran in: every hydrogen removed."""
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    with open(src) as fin, open(dst, "w") as fout:
        for line in fin:
            if line.startswith(("ATOM", "HETATM")) and line[76:78].strip().upper() == "H":
                continue
            fout.write(line)


def run_preequil(input_dir, output_dir, label):
    """One arm. Returns (rc, tail_of_output). Never raises — a failing arm IS the measurement."""
    env = dict(os.environ)
    env.update({
        "LEG_ID": LEG, "SEED": "0", "CHARGE_METHOD": "nagl",
        "PREEQUIL_SMOKE": "1", "PREEQUIL_NS": "0.002", "PREEQUIL_EXACT_FF": "1",
        "OPENMM_PLATFORM": "CPU", "OPENMM_REQUIRE_CUDA": "0",
        "INPUT_DIR": input_dir, "OUTPUT_DIR": output_dir,
    })
    print(f"\n=========== {label} : INPUT_DIR={input_dir}", flush=True)
    p = subprocess.run([sys.executable, os.path.join(HERE, "ternary_preequil.py")],
                       env=env, capture_output=True, text=True)
    out = (p.stdout or "") + (p.stderr or "")
    for line in out.splitlines()[-30:]:
        print("   " + line, flush=True)
    print(f"=========== {label} rc={p.returncode}", flush=True)
    return p.returncode, out


def main():
    staged = os.environ.get("STAGED_DIR", "/tmp/5aks_in")
    scratch = os.environ.get("REPRO_SCRATCH", "/tmp/5aks_repro")
    fixed_pdb = os.path.join(staged, LEG, "complex.pdb")
    if not os.path.isfile(fixed_pdb):
        raise SystemExit(f"[repro] no staged complex.pdb at {fixed_pdb} — run nr4a3_5aks_stage first")

    n, h = count_atoms(fixed_pdb)
    print(f"[repro] FIXED complex.pdb: {n} atoms, {h} hydrogens", flush=True)

    arm_a = os.path.join(scratch, "armA")
    shutil.rmtree(arm_a, ignore_errors=True)
    os.makedirs(os.path.join(arm_a, LEG), exist_ok=True)
    strip_hydrogens(fixed_pdb, os.path.join(arm_a, LEG, "complex.pdb"))
    shutil.copy(os.path.join(staged, LEG, "ligands.sdf"), os.path.join(arm_a, LEG, "ligands.sdf"))
    na, ha = count_atoms(os.path.join(arm_a, LEG, "complex.pdb"))
    print(f"[repro] UNFIXED complex.pdb: {na} atoms, {ha} hydrogens", flush=True)
    if h == 0:
        raise SystemExit("[repro] the staged pdb has NO hydrogens — the stager's PDBFixer step did not run, "
                         "so there is nothing to compare and the fix is not in this image's code")

    rc_a, out_a = run_preequil(arm_a, os.path.join(scratch, "outA"), "ARM A (UNFIXED — expected to FAIL)")
    rc_b, out_b = run_preequil(staged, os.path.join(scratch, "outB"), "ARM B (FIXED — expected to PASS)")

    # The discriminating observation, stated as a verdict rather than left for a reader to infer.
    template_error = ("No template found" in out_a) or ("template" in out_a.lower() and rc_a != 0)
    print("\n================ VERDICT ================", flush=True)
    print(f"  ARM A (no hydrogens) rc={rc_a}   ARM B (hydrogenated) rc={rc_b}", flush=True)
    if rc_a != 0 and rc_b == 0:
        print("  CONFIRMED: hydrogenation is the cause. The unfixed complex fails and the fixed one does not,"
              "\n  with nothing else differing between the two runs.", flush=True)
        print(f"  ARM A failed on a force-field TEMPLATE error: {template_error}", flush=True)
        return 0
    if rc_a == 0:
        print("  ⚠ HYPOTHESIS REFUTED: the UNFIXED complex pre-equilibrates fine, so missing hydrogens are "
              "NOT\n  what killed the leg. Do NOT re-rent — the real cause is still unidentified.", flush=True)
        return 1
    print("  ⚠ FIX INSUFFICIENT: both arms fail, so hydrogenation was necessary-or-irrelevant but is not "
          "sufficient.\n  ARM B's tail above is the next thing to read. Do NOT re-rent.", flush=True)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
