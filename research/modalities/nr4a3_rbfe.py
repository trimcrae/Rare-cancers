#!/usr/bin/env python3
"""RBFE compute engine — denovo_401 → lo_m0_NCCO relative binding FEP via OpenFE (RelativeHybridTopologyProtocol).

Runs ONE (receptor, leg) alchemical MORPH (A→B): the complex-morph leg (protein + ligand + solvent) or the
shared solvent-morph leg (ligand + solvent). OpenFE supplies the four pieces the repo's ABFE engine lacks —
LOMAP atom-mapping, the perses hybrid topology, the relative λ schedule, and MBAR — turnkey and validated, so
we do NOT hand-roll dual-topology soft-core (the highest-risk piece; see nr4a3-degrader-next-steps.md engine
policy). No Boresch restraint / standard-state correction: both ligands share the pose, so it cancels.

Deliverable per leg: ΔG_morph(A→B) in that environment (+ uncertainty). The reducer forms
ΔΔG_bind = ΔG_complex_morph − ΔG_solvent_morph per receptor (rbfe_edges.ddg_bind), then the selectivity.

**SHAKEOUT-PENDING (standing rule): the OpenFE protocol settings + the env are first-pass; run mode=smoke on a
GPU (maps + builds the hybrid topology, no MD) then ONLY_LEGS=solvent (one real morph leg) before trusting any
number — exactly as every prior GPU pipeline here was shaken out.** Heavy deps (openfe/openmm) are imported
lazily so this file loads on a CPU box.

Env: MODE (smoke|run|reduce), RECEPTOR, LEG (complex|solvent), LIGAND_A, LIGAND_B, N_WINDOWS, N_ITER, SEED,
INPUT_DIR (mounted <r>-opened.pdb + docked_<r>.sdf), OUTPUT_DIR/CKPT_DIR.
"""
import glob
import json
import os
import sys

import rbfe_edges as rb

IN = os.environ.get("INPUT_DIR", "/opt/ml/processing/input")
CKPT = os.environ.get("CKPT_DIR", os.environ.get("OUTPUT_DIR", "/opt/ml/checkpoints"))
LIGAND_A = os.environ.get("LIGAND_A", rb.LIGAND_A)
LIGAND_B = os.environ.get("LIGAND_B", rb.LIGAND_B)
RECEPTOR = os.environ.get("RECEPTOR", "nr4a3")
LEG = os.environ.get("LEG", "complex")
N_WINDOWS = int(os.environ.get("N_WINDOWS", "12"))
N_ITER = int(os.environ.get("N_ITER", "1000"))
SEED = int(os.environ.get("SEED", "0"))


def _canon(m, rdkit_chem):
    """Canonical (stereo-aware) SMILES of a docked-pose mol, Hs stripped — for structural record matching."""
    try:
        return rdkit_chem.MolToSmiles(rdkit_chem.RemoveHs(rdkit_chem.Mol(m)))
    except Exception:  # noqa: BLE001
        return None


def _sdf_mol(sdf_path, name, expected_smiles, rdkit_chem):
    """Resolve the docked pose for ligand `name` from a multi-record docked SDF, robustly and WITHOUT ever
    silently substituting the wrong molecule (a wrong ligand A/B would invalidate the entire ΔΔG). The species
    dock tags the canonical/generated stereoisomer with a `_gen` suffix (e.g. requesting `denovo_401` must
    resolve to the record `denovo_401_gen`), and there are OTHER stereoisomers of the same base in the file, so
    we match on: (1) exact _Name, (2) _Name == name+'_gen', (3) exact stereo-canonical SMILES == expected. If
    none match, HARD-FAIL — never fall back to an arbitrary record."""
    want = None
    if expected_smiles:
        em = rdkit_chem.MolFromSmiles(expected_smiles)
        want = rdkit_chem.MolToSmiles(em) if em is not None else None
    recs = [m for m in rdkit_chem.SDMolSupplier(sdf_path, removeHs=False) if m is not None]
    for target in (name, f"{name}_gen"):
        for m in recs:
            if m.HasProp("_Name") and m.GetProp("_Name") == target:
                return m
    if want is not None:
        for m in recs:
            if _canon(m, rdkit_chem) == want:
                return m
    have = [m.GetProp("_Name") for m in recs if m.HasProp("_Name")]
    raise SystemExit(f"  ABORT: no record for {name} (tried name, {name}_gen, SMILES) in {sdf_path}; "
                     f"records present: {have[:20]}")


def _build_components(openfe, rdkit_chem):
    """Build the OpenFE ligand A/B SmallMoleculeComponents (+ receptor ProteinComponent for the complex leg),
    from the mounted docked poses. Returns (ligA, ligB, protein_or_None)."""
    # The solvent-morph leg has RECEPTOR="shared" (ligand-in-water, no protein), so its ligand structures don't
    # depend on a receptor — pull them from any real docked SDF (nr4a3). The complex leg uses its own receptor's
    # SDF. (Smoke used the nr4a3/complex defaults, so the "shared" path was first exercised by the solvent leg.)
    sdf_receptor = RECEPTOR if RECEPTOR in ("nr4a3", "nr4a1", "nr4a2") else "nr4a3"
    sdf = os.path.join(IN, "ligand", f"docked_{sdf_receptor}.sdf")
    if not os.path.exists(sdf):
        sdf = next(iter(glob.glob(os.path.join(IN, "**", f"docked_{sdf_receptor}.sdf"), recursive=True)), sdf)
    molA = _sdf_mol(sdf, LIGAND_A, rb.SMILES.get(LIGAND_A), rdkit_chem)
    molB = _sdf_mol(sdf, LIGAND_B, rb.SMILES.get(LIGAND_B), rdkit_chem)
    ligA = openfe.SmallMoleculeComponent.from_rdkit(molA)
    ligB = openfe.SmallMoleculeComponent.from_rdkit(molB)
    protein = None
    if LEG == "complex":
        pdb = os.path.join(IN, "receptor", f"{RECEPTOR}-opened.pdb")
        if not os.path.exists(pdb):
            pdb = next(iter(glob.glob(os.path.join(IN, "**", f"{RECEPTOR}-opened.pdb"), recursive=True)), pdb)
        protein = openfe.ProteinComponent.from_pdb_file(pdb)
    return ligA, ligB, protein


def _mapping(openfe, ligA, ligB):
    """LOMAP atom-map A→B (the shared scaffold maps 1:1; the ortho-acetamido is the unique region)."""
    from openfe.setup import LomapAtomMapper
    mapper = LomapAtomMapper(time=20, threed=True, element_change=False)
    mapping = next(mapper.suggest_mappings(ligA, ligB))
    return mapping


def _protocol(openfe):
    from openfe.protocols.openmm_rfe import RelativeHybridTopologyProtocol
    s = RelativeHybridTopologyProtocol.default_settings()
    # first-pass settings (SHAKEOUT-PENDING): each knob guarded independently so a version-specific attribute
    # can't block the rest of the build, and so smoke surfaces the exact offender.
    # SINGLE replicate (trimcrae 2026-07-06): relative FEP is low-variance for a congeneric pair, so one repeat
    # with MBAR/bootstrap error is the field standard for a single edge; escalate to 3 (replicate-SD) ONLY if
    # this comes back marginal. protocol_repeats=3 would silently triple GPU cost/wall and blow past MAX_RUN.
    try:
        s.protocol_repeats = 1
    except Exception as e:  # noqa: BLE001
        print(f"  [rbfe] WARN protocol_repeats ({e})", flush=True)
    # OpenFE REQUIRES n_replicas == number of lambda windows. Set the lambda-window count FIRST, then match
    # n_replicas; if the attribute differs by openfe version, leave BOTH at the internally-consistent default
    # (smoke #2 failed because n_replicas=12 didn't match the default lambda_settings.lambda_windows=11).
    try:
        s.lambda_settings.lambda_windows = N_WINDOWS
        s.simulation_settings.n_replicas = N_WINDOWS
    except Exception as e:  # noqa: BLE001
        print(f"  [rbfe] WARN could not set windows to {N_WINDOWS} ({e}); using OpenFE default", flush=True)
    # MD lengths only matter for the real run (smoke does no MD); guarded against unit-parse quirks.
    for attr, val in (("equilibration_length", "1 ns"), ("production_length", "5 ns")):
        try:
            setattr(s.simulation_settings, attr, val)
        except Exception as e:  # noqa: BLE001
            print(f"  [rbfe] WARN {attr}={val} ({e}); using default", flush=True)
    try:
        s.engine_settings.compute_platform = "CUDA"
    except Exception as e:  # noqa: BLE001
        print(f"  [rbfe] WARN compute_platform ({e})", flush=True)
    return RelativeHybridTopologyProtocol(s)


def _chemical_systems(openfe, ligA, ligB, protein):
    solvent = openfe.SolventComponent()
    if LEG == "complex":
        A = openfe.ChemicalSystem({"protein": protein, "ligand": ligA, "solvent": solvent})
        B = openfe.ChemicalSystem({"protein": protein, "ligand": ligB, "solvent": solvent})
    else:
        A = openfe.ChemicalSystem({"ligand": ligA, "solvent": solvent})
        B = openfe.ChemicalSystem({"ligand": ligB, "solvent": solvent})
    return A, B


def run_leg():
    os.makedirs(CKPT, exist_ok=True)
    import openfe
    from rdkit import Chem
    ligA, ligB, protein = _build_components(openfe, Chem)
    mapping = _mapping(openfe, ligA, ligB)
    n_mapped = len(mapping.componentA_to_componentB)
    print(f"  [rbfe] {RECEPTOR}/{LEG}: mapped {n_mapped} atoms A->B ({LIGAND_A}->{LIGAND_B})", flush=True)

    if os.environ.get("MODE") == "smoke":
        # validate env + mapping + hybrid-topology build ONLY (no MD) — the cheap shakeout.
        proto = _protocol(openfe)
        A, B = _chemical_systems(openfe, ligA, ligB, protein)
        dag = proto.create(stateA=A, stateB=B, mapping=mapping)
        json.dump({"smoke": "ok", "receptor": RECEPTOR, "leg": LEG, "n_mapped_atoms": n_mapped,
                   "n_protocol_units": len(getattr(dag, "protocol_units", []) or [])},
                  open(os.path.join(CKPT, "smoke.json"), "w"), indent=2)
        print("  [rbfe] SMOKE ok — env solves, mapping + hybrid topology build.", flush=True)
        return

    proto = _protocol(openfe)
    A, B = _chemical_systems(openfe, ligA, ligB, protein)
    dag = proto.create(stateA=A, stateB=B, mapping=mapping)
    from gufe.protocols import execute_DAG
    shared = os.path.join(CKPT, "shared")
    scratch = os.path.join(CKPT, "scratch")
    os.makedirs(shared, exist_ok=True); os.makedirs(scratch, exist_ok=True)
    dagres = execute_DAG(dag, shared_basedir=shared, scratch_basedir=scratch, keep_shared=True)
    est = proto.gather([dagres])
    dg = est.get_estimate()
    unc = est.get_uncertainty()
    out = {"receptor": RECEPTOR, "leg": LEG, "ligand_a": LIGAND_A, "ligand_b": LIGAND_B,
           "dg_morph_kcal": float(dg.to("kilocalorie_per_mole").m),
           "unc_kcal": float(unc.to("kilocalorie_per_mole").m), "n_mapped_atoms": n_mapped}
    json.dump(out, open(os.path.join(CKPT, f"leg_{RECEPTOR}_{LEG}.json"), "w"), indent=2)
    print(f"  [rbfe] LEG DONE {RECEPTOR}/{LEG}: ΔG_morph={out['dg_morph_kcal']:.2f} ± {out['unc_kcal']:.2f}",
          flush=True)


def reduce_receptor():
    """ΔΔG_bind(A→B, receptor) = ΔG_complex_morph − ΔG_solvent_morph. Reads the two legs' checkpoints (mounted)."""
    def _read(kind):
        for base in (IN, CKPT):
            for p in glob.glob(os.path.join(base, "**", f"leg_{RECEPTOR}_*.json"), recursive=True) + \
                     glob.glob(os.path.join(base, "**", "leg_*_%s.json" % kind), recursive=True):
                d = json.load(open(p))
                if d.get("leg") == kind and (kind == "solvent" or d.get("receptor") == RECEPTOR):
                    return d
        return None
    cx, sol = _read("complex"), _read("solvent")
    if not cx or not sol:
        sys.exit(f"  ABORT reduce: missing legs (complex={bool(cx)} solvent={bool(sol)})")
    ddg = rb.ddg_bind(cx["dg_morph_kcal"], sol["dg_morph_kcal"])
    out = {"receptor": RECEPTOR, "ddg_bind_kcal": round(ddg, 3),
           "dg_complex_morph": cx["dg_morph_kcal"], "dg_solvent_morph": sol["dg_morph_kcal"],
           "absolute_dg_B": round(rb.absolute_dg_B(ddg, RECEPTOR), 3),
           "note": "ΔΔG_bind(401->lo_m0_NCCO); negative = lo_m0_NCCO binds tighter. absolute_dg_B anchors on "
                   "401's preliminary ABFE (rbfe_edges.ANCHOR_401_ABFE)."}
    os.makedirs(CKPT, exist_ok=True)
    json.dump(out, open(os.path.join(CKPT, f"ddg_{RECEPTOR}.json"), "w"), indent=2)
    print(f"  [rbfe] REDUCE {RECEPTOR}: ΔΔG_bind={ddg:.2f} kcal/mol → B absolute {out['absolute_dg_B']:.2f}",
          flush=True)


def main():
    mode = os.environ.get("MODE", "smoke")
    if mode == "reduce":
        reduce_receptor()
    else:                       # smoke or run both go through run_leg (smoke short-circuits inside)
        run_leg()


if __name__ == "__main__":
    main()
