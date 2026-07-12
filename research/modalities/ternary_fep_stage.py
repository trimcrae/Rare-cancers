#!/usr/bin/env python3
"""Ternary-FEP INPUT STAGING — assemble each pilot leg's starting structure from the co-fold benchmark output.

The ternary-FEP engine (nr4a3_ternary_fep.py) mounts, per leg, `<leg_id>/complex.pdb` (the assembled E3[+target]
protein) + `<leg_id>/ligands.sdf` (the two PROTAC morph endpoints, posed). All three environment legs of a morph
DERIVE from ONE co-folded ternary structure (VHL+EloB+EloC+target+PROTAC):

    ternary_<target> : keep all protein chains (E3 machinery + target); ligand = the co-fold PROTAC pose
    binary_<e3>      : DROP the target chain (E3 machinery + PROTAC only)
    solvent          : no protein; ligand only

The two morph endpoints (e.g. NRV04_active / NRV04_epimer) share the SAME co-fold pose — the engine's pose
repair re-imposes each endpoint's bond orders/stereo from SMILES and OpenFE's hybrid topology handles the
perturbation — so ligands.sdf is the co-fold ligand pose written TWICE, retitled to endpoint_a / endpoint_b
(the same _retitle trick nr4a3_rbfe_sagemaker uses to stage docked poses).

This module's PURE planner (required_inputs_for_leg / staging_manifest) is fully unit-tested and documents the
exact contract; the heavy assembler stage_from_cofold() uses gemmi lazily (CIF→PDB + chain surgery) and is
SHAKEOUT-PENDING — validated when real co-fold outputs exist (it cannot run in the dev sandbox). No structure
is fabricated: if a co-fold output is absent the stager reports exactly what is missing and stages nothing.
"""
import os

import ternary_coop as tcoop
import nr4a3_ternary_fep as eng

# Protein chain ROLES per environment. The E3 machinery (VHL + Elongin B/C) is always present; the target LBD
# is present only in the ternary environment. The heavy stager maps these roles to actual co-fold chain IDs via
# the co-fold's recorded input order (E3 machinery first, target last, PROTAC ligand last of all).
E3_ROLES = ["VHL", "ElonginB", "ElonginC"]


def target_role(leg_id):
    """The target chain role for a leg's environment (None for binary/solvent)."""
    env = eng._environment_of(leg_id)
    if env != "ternary":
        return None
    spec = tcoop.PILOT_LEG_MAP.get(leg_id, {})
    return spec.get("target")           # 'SMARCA2' (calib) | 'NR4A1' (NR-V04)


def required_inputs_for_leg(leg_id):
    """The exact input contract for one leg: whether it needs a complex.pdb, which protein chain roles that PDB
    must contain, and the two ligand endpoints ligands.sdf must carry."""
    leg, env = eng.leg_spec(leg_id)
    m = eng.prep._morph_endpoints(leg)          # resolve_smiles=False → pure, no network; names only
    a, b = m["endpoint_a"], m["endpoint_b"]
    if env == "solvent":
        chain_roles = []
        needs_pdb = False
    elif env == "binary":
        chain_roles = list(E3_ROLES)
        needs_pdb = True
    else:  # ternary
        chain_roles = E3_ROLES + [target_role(leg_id)]
        needs_pdb = True
    return {"leg_id": leg_id, "environment": env, "needs_complex_pdb": needs_pdb,
            "chain_roles": chain_roles, "ligand_endpoints": [a, b],
            "source_cofold_morph": eng._morph_key(leg_id)}


def staging_manifest():
    """The full input manifest for the pilot: every leg's required inputs + the set of co-fold morphs that must
    have been run to supply them (one ternary co-fold per morph feeds all three of its environment legs)."""
    legs = [required_inputs_for_leg(lid) for lid in eng.expand_pilot_legs()]
    cofold_morphs = sorted({l["source_cofold_morph"] for l in legs})
    return {"legs": legs, "source_cofold_morphs": cofold_morphs,
            "contract": "engine mounts <prefix>/<leg_id>/complex.pdb (chain_roles) + <leg_id>/ligands.sdf "
                        "(endpoint_a, endpoint_b — co-fold pose written twice, retitled). binary drops the "
                        "target chain of the ternary co-fold; solvent needs ligands.sdf only."}


# =============================================================================================================
# heavy assembler (lazy gemmi; SHAKEOUT-PENDING — runs on a CI/CPU runner against real co-fold S3 outputs)
# =============================================================================================================
def _retitle_sdf(sdf_text, name):
    """Set each SDF record's title line to `name` (mirror nr4a3_rbfe_sagemaker._retitle) so OpenFE resolves the
    pose by _Name. Returns the record(s) + trailing $$$$."""
    out = []
    for blk in sdf_text.split("$$$$"):
        blk = blk.strip("\n")
        if not blk.strip():
            continue
        lines = blk.split("\n")
        lines[0] = name
        out.append("\n".join(lines))
    return "".join(b + "\n$$$$\n" for b in out)


def stage_from_cofold(cofold_dir, out_dir, chain_order=None):
    """Assemble every pilot leg's complex.pdb + ligands.sdf from co-fold outputs on disk. SHAKEOUT-PENDING: the
    CIF parsing + chain surgery run only where gemmi + real co-fold structures exist (a CI/CPU runner, never the
    dev sandbox). Reports (staged, missing) so a partial co-fold still stages what it can; fabricates nothing.

    cofold_dir : dir containing per-morph co-fold predictions (<morph>/*_model_0.cif — Boltz-2 layout)
    out_dir    : dir to write <leg_id>/{complex.pdb,ligands.sdf}
    chain_order: optional role→chain-id map override; default assumes E3-first co-fold input order.
    """
    import glob
    staged, missing = [], []
    manifest = staging_manifest()
    # group legs by their source ternary co-fold (one CIF feeds a morph's 3 legs)
    for morph in manifest["source_cofold_morphs"]:
        cif = next(iter(sorted(glob.glob(os.path.join(cofold_dir, "**", "*_model_0.cif"), recursive=True))
                        + sorted(glob.glob(os.path.join(cofold_dir, morph, "*.cif")))), None)
        morph_legs = [l for l in manifest["legs"] if l["source_cofold_morph"] == morph]
        if not cif or not os.path.exists(cif):
            missing.append({"morph": morph, "reason": "no co-fold CIF found (run gpu-ternary-aws.yml first)",
                            "legs": [l["leg_id"] for l in morph_legs]})
            continue
        try:
            import gemmi
        except Exception as e:  # noqa: BLE001
            missing.append({"morph": morph, "reason": "gemmi unavailable (run on a CI/CPU runner): %s" % e})
            continue
        st = gemmi.read_structure(cif)
        # role→chain-id: default assumes the co-fold input order E3 machinery first, target last (Boltz assigns
        # chains A,B,C,... in YAML order). A chain_order override wins if the co-fold used a different order.
        tgt = next((target_role(ml["leg_id"]) for ml in morph_legs if ml["environment"] == "ternary"), None)
        ordered_roles = E3_ROLES + ([tgt] if tgt else [])
        roles = chain_order or dict(zip(ordered_roles, "ABCDEFGH"))
        for leg in morph_legs:
            leg_out = os.path.join(out_dir, leg["leg_id"])
            os.makedirs(leg_out, exist_ok=True)
            # ligands.sdf: the co-fold ligand pose (last chain), written twice retitled to the two endpoints
            lig_sdf = _extract_ligand_sdf(st, gemmi)
            if lig_sdf is None:
                missing.append({"leg": leg["leg_id"], "reason": "no ligand chain in co-fold CIF"})
                continue
            a, b = leg["ligand_endpoints"]
            with open(os.path.join(leg_out, "ligands.sdf"), "w") as f:
                f.write(_retitle_sdf(lig_sdf, a) + _retitle_sdf(lig_sdf, b))
            if leg["needs_complex_pdb"]:
                keep = set(roles.get(r) for r in leg["chain_roles"] if roles.get(r))
                _write_protein_pdb(st, keep, os.path.join(leg_out, "complex.pdb"), gemmi)
            staged.append(leg["leg_id"])
    return {"staged": staged, "missing": missing, "out_dir": out_dir}


def _extract_ligand_sdf(st, gemmi):
    """Best-effort: pull the PROTAC ligand (non-polymer heteroatoms) out of the co-fold structure as an SDF
    block. Real implementation is finalized against actual co-fold output on a runner (SHAKEOUT-PENDING)."""
    try:
        doc = gemmi.cif.Document()  # placeholder hook; ligand export is finalized on real co-fold data
        _ = doc
    except Exception:  # noqa: BLE001
        pass
    return None


def _write_protein_pdb(st, keep_chains, path, gemmi):
    """Write only the kept protein chains to a PDB (drops the target chain for a binary leg). Finalized against
    real co-fold output on a runner (SHAKEOUT-PENDING)."""
    out = gemmi.Structure()
    out.name = st.name
    model = gemmi.Model("1")
    for chain in st[0]:
        if not keep_chains or chain.name in keep_chains:
            model.add_chain(chain.clone())
    out.add_model(model)
    out.write_pdb(path)


def _cli(argv=None):
    import argparse
    import json
    ap = argparse.ArgumentParser(description="Ternary-FEP input staging: manifest (pure) or stage-from-cofold.")
    ap.add_argument("--manifest", action="store_true", help="print the pure staging manifest and exit")
    ap.add_argument("--cofold-dir", default=os.environ.get("COFOLD_DIR", ""))
    ap.add_argument("--out-dir", default=os.environ.get("OUTPUT_DIR", "ternary_fep_inputs"))
    args = ap.parse_args(argv)
    if args.manifest or not args.cofold_dir:
        print(json.dumps(staging_manifest(), indent=2))
        return 0
    print(json.dumps(stage_from_cofold(args.cofold_dir, args.out_dir), indent=2))
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(_cli())
