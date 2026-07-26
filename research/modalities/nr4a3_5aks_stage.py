#!/usr/bin/env python3
"""RUNG 5a-KS — turn the two co-folded ternaries into the FEP engine's per-leg inputs.

THE CONTRACT. `nr4a3_ternary_fep.py` mounts, per leg, `<leg_id>/complex.pdb` (the protein) and
`<leg_id>/ligands.sdf` (the two morph endpoints, posed). This module produces exactly that for

    5aks_d0_to_d__ternary_nr4a3      CRBN + NR4A3-LBD + construct
    5aks_d0_to_d__ternary_nr4a1      CRBN + NR4A1-LBD + construct

WHY THIS IS NOT `ternary_fep_stage`. That module stages the FROZEN pilot bundle, whose E3 machinery is
VHL + Elongin B + Elongin C — three chains this rung does not have. 5a-KS recruits **CRBN**, a single chain.
Its `E3_ROLES` is a module constant, its manifest is built from `expand_pilot_legs()`, and `load_pilot_legs`
fails closed on any drift from the preregistered leg-id list, so pointing it at these legs would either break
that guard or silently enlarge a preregistered experiment. Separate rung, separate stager.

⚠ AND ITS LIGAND EXTRACTOR IS A STUB. `ternary_fep_stage._extract_ligand_sdf` is `return None` with a
SHAKEOUT-PENDING note — the ternary staging path in this repo has never produced a `ligands.sdf` from a
co-fold. So there was nothing to reuse and this implements it: gemmi splits polymer from non-polymer, RDKit
reads the ligand's heavy-atom coordinates and takes bond orders from the **committed d0 SMILES** via
`AssignBondOrdersFromTemplate`. That template step is what makes a coordinate-only ligand into a chemically
valid SDF, and using the design's own SMILES is what keeps the simulated molecule tied to the design.

BOTH ENDPOINTS COME FROM ONE POSE. `ligands.sdf` is the co-fold pose written twice, retitled `d0` and `d` —
the engine's pose repair re-imposes each endpoint's bond orders and stereo from SMILES and OpenFE's hybrid
topology handles the one-atom perturbation. Two independent co-folds would introduce a pose difference between
the endpoints that the alchemical transformation would have to absorb, contaminating `S` with something that
is not the physical question.

SHAKEOUT STATUS: the pure planner below is unit-tested and is the contract. `stage_from_cofold` needs gemmi +
RDKit + real Boltz output, so it runs on a CI runner, never in the dev sandbox — and it FABRICATES NOTHING: a
missing co-fold, a missing ligand, or a template mismatch is reported and staged as nothing.
"""
import argparse
import glob
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import nr4a3_5aks_cofold as K     # noqa: E402  (the pair, the leg ids, the leg map — one home)

E3_ROLE = "CRBN"


def required_inputs_for_leg(lid):
    """The exact input contract for one 5a-KS leg. Pure."""
    spec = K.LEG_MAP.get(lid)
    if not spec:
        raise SystemExit(f"[5aks-stage] {lid} is not a 5a-KS leg — refusing to guess its chain roles")
    return {
        "leg_id": lid,
        "environment": spec["environment"],
        "needs_complex_pdb": True,
        "chain_roles": [E3_ROLE, spec["target"]],
        "ligand_endpoints": [K.ENDPOINT_A, K.ENDPOINT_B],
        "source_cofold_species": spec["target"],
        "source_cofold_cif_stem": K.cofold_cif_stem(spec["target"]),
    }


def staging_manifest(design_path=None):
    """Every leg's required inputs, plus the co-folds that must exist to supply them. Pure."""
    mp = K.load_pair(design_path) if design_path else K.load_pair()
    legs = [required_inputs_for_leg(lid) for lid in sorted(K.LEG_MAP)]
    return {
        "legs": legs,
        "source_cofolds": sorted({l["source_cofold_species"] for l in legs}),
        "endpoint_smiles": {K.ENDPOINT_A: mp["d0"]["smiles"], K.ENDPOINT_B: mp["d"]["smiles"]},
        "contract": ("engine mounts <prefix>/<leg_id>/complex.pdb (chain_roles) + <leg_id>/ligands.sdf "
                     "(the ONE co-fold pose written twice, retitled d0 and d). Ternary only: the binary and "
                     "solvent legs cancel algebraically in S — see nr4a3_5aks_reduce."),
    }


def retitle_sdf(sdf_text, name):
    """Set each SDF record's title line to `name`, so OpenFE resolves the pose by `_Name`."""
    out = []
    for blk in sdf_text.split("$$$$"):
        if not blk.strip():
            continue
        lines = blk.lstrip("\n").split("\n")
        lines[0] = name
        out.append("\n".join(lines) + "$$$$\n")
    return "".join(out)


_SOLVENT_NAMES = {"HOH", "WAT", "DOD", "SO4", "PO4", "GOL", "EDO", "NA", "CL", "MG", "ZN", "K", "CA"}

# The 20 standard residues + the nucleic-acid set, so a polymer residue can be recognised by NAME when the
# file's own annotation is missing. Boltz-2 writes its ligand chain with `group_PDB = HETATM` in some versions
# and `ATOM` in others, and `setup_entities()` re-derives subchains from CONNECTIVITY rather than from the
# input's flags — so `het_flag == "H"` is a HINT here, never the authority.
_POLYMER_NAMES = {
    "ALA", "ARG", "ASN", "ASP", "CYS", "GLN", "GLU", "GLY", "HIS", "ILE", "LEU", "LYS", "MET", "PHE",
    "PRO", "SER", "THR", "TRP", "TYR", "VAL", "MSE", "SEC", "PYL", "UNK",
    "A", "C", "G", "U", "T", "DA", "DC", "DG", "DT", "DU", "N",
}


def _candidate_ligand_residues(st):
    """Every residue in the model that could be the co-folded construct, best guess first.

    THREE INDEPENDENT CRITERIA, DELIBERATELY OR-ed. This function is the shakeout risk in the whole rung: it
    is the one place that has to interpret a file format nobody here had produced yet, and each criterion
    alone has a way of being wrong on real Boltz-2 output:
      * `het_flag == "H"` — depends on the writer setting `group_PDB = HETATM`, which is a convention, not a
        guarantee, and is re-derived by `setup_entities()`.
      * subchain/entity type — only populated once entities are set up, and only correctly when the CIF
        carries the entity block Boltz may or may not write.
      * residue NAME not in the standard polymer set — always available, and the construct is a `LIG`-class
        residue in every writer.
    Taking the union and then RANKING by heavy-atom count means a wrong criterion costs nothing, while a
    missing one would have cost a whole rented co-fold. The caller still refuses anything that does not
    template-match, so a wrong pick cannot become a wrong dG.
    """
    cands = []
    for chain in st[0]:
        for res in chain:
            name = (res.name or "").strip().upper()
            if name in _SOLVENT_NAMES:
                continue
            het = res.het_flag == "H"
            try:
                nonpoly = str(res.subchain or "") != "" and not res.is_amino_acid() and not res.is_nucleic_acid()
            except Exception:  # noqa: BLE001
                nonpoly = False
            unnamed = name not in _POLYMER_NAMES
            if not (het or nonpoly or unnamed):
                continue
            heavy = sum(1 for a in res if a.element.name != "H")
            if heavy < 6:          # ions, buffer fragments, a stray modified residue
                continue
            cands.append((heavy, chain.name, name, res))
    cands.sort(key=lambda t: -t[0])
    return cands


def _residue_pdb_block(res):
    """A minimal single-residue PDB block of the heavy atoms, for RDKit's proximity bonding."""
    lines = []
    for i, a in enumerate(res):
        if a.element.name == "H":
            continue
        el = a.element.name.upper()
        # The element column is what RDKit types the atom from; the atom NAME is only a label. Both are
        # right-justified per the PDB spec, and a left-justified two-letter element (`CL` in cols 77-78 vs
        # 78-79) is read as carbon — a silent, whole-molecule mis-typing.
        lines.append("HETATM%5d %-4s %3s %s%4d    %8.3f%8.3f%8.3f  1.00  0.00          %2s" % (
            i + 1, (a.name or el)[:4], "LIG", "X", 1, a.pos.x, a.pos.y, a.pos.z, el))
    return "\n".join(lines) + "\nEND\n"


def _no_stereo(Chem, mol):
    """A stereochemistry-free copy, for comparing CONSTITUTION alone."""
    m = Chem.RemoveHs(Chem.Mol(mol))
    Chem.RemoveStereochemistry(m)
    return m


def _ligand_sdf_from_cif(cif_path, template_smiles):
    """Heavy-atom coordinates from the co-fold's non-polymer chain + bond orders from the design's SMILES.

    Returns (sdf_text, reason_or_None, info). `sdf_text` is None whenever the ligand could not be resolved,
    and `reason` says why. Never returns a molecule it could not template-match: a silently mis-bonded ligand
    would run, converge, and give a wrong dG.
    """
    try:
        import gemmi
        from rdkit import Chem
        from rdkit.Chem import AllChem
    except Exception as e:  # noqa: BLE001
        return None, f"gemmi/rdkit unavailable (run on a CI runner): {e}", {}
    try:
        st = gemmi.read_structure(cif_path)
        st.setup_entities()
    except Exception as e:  # noqa: BLE001
        return None, f"co-fold parse failed: {e}", {}
    if not len(st) or not len(st[0]):
        return None, "the co-fold CIF has no model/chains", {}

    template = Chem.MolFromSmiles(template_smiles)
    if template is None:
        return None, "the design's d0 SMILES did not parse as a template", {}
    want_heavy = template.GetNumHeavyAtoms()

    cands = _candidate_ligand_residues(st)
    if not cands:
        return None, ("no non-polymer residue in the co-fold CIF — the construct did not co-fold. Residues "
                      f"present: {sorted({r.name for ch in st[0] for r in ch})!r:.300}"), {}

    tried = []
    for heavy, chain_name, res_name, res in cands:
        raw = Chem.MolFromPDBBlock(_residue_pdb_block(res), removeHs=True, sanitize=False)
        if raw is None:
            tried.append(f"{chain_name}/{res_name}({heavy} heavy): RDKit could not read the coordinates")
            continue
        # `sanitize=False` keeps a partly-broken block readable, but it also leaves RING INFO uninitialised —
        # and `AssignBondOrdersFromTemplate` runs a substructure match, which needs it. Without this the
        # template step raises `RingInfo not initialized` and the whole co-fold looks like a chemistry
        # mismatch when it is really an un-perceived molecule.
        try:
            Chem.SanitizeMol(raw, sanitizeOps=Chem.SanitizeFlags.SANITIZE_SYMMRINGS
                             | Chem.SanitizeFlags.SANITIZE_SETCONJUGATION
                             | Chem.SanitizeFlags.SANITIZE_SETHYBRIDIZATION,
                             catchErrors=True)
        except Exception:  # noqa: BLE001
            Chem.FastFindRings(raw)
        try:
            mol = AllChem.AssignBondOrdersFromTemplate(template, raw)
        except Exception as e:  # noqa: BLE001
            tried.append(f"{chain_name}/{res_name}({heavy} heavy vs template {want_heavy}): {e}")
            continue
        # BELT AND BRACES: a template match that succeeded still has to describe the design's molecule.
        # `AssignBondOrdersFromTemplate` matches the template INTO the pose, so a pose carrying extra atoms
        # could in principle match on a substructure.
        #
        # ⚠ BUT THE COMPARISON IS NOT PLAIN SMILES EQUALITY, AND THE FIRST VERSION THAT TRIED IT REJECTED A
        # PERFECTLY GOOD LIGAND. Found on the pre-spend shakeout: RDKit's PDB reader assigns chiral tags
        # FROM THE 3D COORDINATES, so the extracted pose comes back with EVERY stereocentre specified —
        # including the glutarimide C-H, which the design's SMILES deliberately leaves unspecified (it is
        # the thalidomide-class centre that epimerises, and the whole IMiD field draws it unassigned). The
        # pose therefore read `N([C@H]3CCC(=O)NC3=O)` against the design's `N(C3CCC(=O)NC3=O)` and the two
        # canonical strings differed on a molecule that is chemically identical.
        # So the check is split into the two questions that actually matter:
        #   (1) CONSTITUTION must be identical — same atoms, same bonds. Stereo-stripped SMILES equality.
        #   (2) Every stereocentre the DESIGN specifies must be reproduced. A chirality-aware substructure
        #       match does exactly this: an unspecified template centre matches either configuration, a
        #       specified one must agree. So a flipped alpha-carbon is still caught, and a resolved
        #       glutarimide is not mistaken for one.
        # What the pose resolved is then RECORDED rather than discarded — see `stage_from_cofold`, which
        # refuses to stage the two species' legs with DIFFERENT resolutions of it.
        try:
            flat_got = Chem.MolToSmiles(_no_stereo(Chem, mol))
            flat_ref = Chem.MolToSmiles(_no_stereo(Chem, template))
            stereo_got = Chem.MolToSmiles(Chem.RemoveHs(Chem.Mol(mol)))
        except Exception as e:  # noqa: BLE001
            return None, f"could not canonicalise the templated ligand: {e}", {}
        if flat_got != flat_ref:
            tried.append(f"{chain_name}/{res_name}: templated to a DIFFERENT molecule "
                         f"({flat_got} != {flat_ref})")
            continue
        if not mol.HasSubstructMatch(template, useChirality=True):
            tried.append(f"{chain_name}/{res_name}: right constitution but a stereocentre the design "
                         f"SPECIFIES is inverted in the co-folded pose ({stereo_got})")
            continue
        mol.SetProp("_Name", "5aks_cofold_pose")
        return Chem.MolToMolBlock(mol) + "$$$$\n", None, {"stereo_smiles": stereo_got,
                                                          "chain": chain_name, "residue": res_name}

    return None, ("no residue in the co-fold matched the committed d0 SMILES "
                  f"({want_heavy} heavy atoms). Refusing to stage a mis-bonded ligand. Tried: {tried}"), {}


def _write_protein_pdb(cif_path, out_pdb):
    """Write the co-fold's POLYMER chains (CRBN + the target LBD) to a PDB, dropping the ligand.

    Returns (chain_names, residues_per_chain). The residue counts are not decoration: they are how a reader
    tells a two-chain ternary from a one-chain control WITHOUT trusting the file name, and the CRBN chain
    (~442 aa) and the NR4A LBD (254 aa by `nr4a3_ternary.LBD_LEN`) are unmistakable by size.
    """
    import gemmi
    st = gemmi.read_structure(cif_path)
    st.setup_entities()
    st.remove_ligands_and_waters()
    st.remove_hydrogens()
    # ⚠ `remove_ligands_and_waters` EMPTIES the ligand chain, it does not DELETE it. Caught on the pre-spend
    # shakeout: the written PDB was correct, but the chain census came back `['A','B','C']` with C at 0
    # residues, so the "a ternary leg must have exactly 2 chains" guard rejected a perfectly good co-fold.
    # A guard that fires on good input is not a safe guard — it teaches you to loosen it.
    st.remove_empty_chains()
    st.setup_entities()
    counts = {ch.name: sum(1 for _ in ch) for ch in st[0] if sum(1 for _ in ch)}
    # `write_pdb` needs the chains to be addressable by a single-character id; Boltz uses A/B, but a longer
    # id from another writer would silently truncate into a collision.
    long_ids = [c for c in counts if len(c) > 1]
    if long_ids:
        raise ValueError(f"co-fold chain ids {long_ids} do not fit the PDB single-character chain column")
    st.write_pdb(out_pdb)
    return sorted(counts), counts


def find_cofold_cif(cofold_dir, species):
    """The co-fold CIF for one species, matched on the driver's OWN prediction stem. Pure-ish (globs disk).

    Boltz writes `<out>/boltz_results_<stem>/predictions/<stem>/<stem>_model_<k>.cif`. We take model 0 — the
    top-ranked prediction — and REFUSE if more than one distinct stem matches, because at that point the
    right structure is a guess.
    """
    stem = K.cofold_cif_stem(species)
    pats = [os.path.join(cofold_dir, "**", f"{stem}_model_0.cif"),
            os.path.join(cofold_dir, "**", f"{stem}*model_0.cif"),
            os.path.join(cofold_dir, "**", f"{stem}*.cif")]
    for p in pats:
        hits = sorted(set(glob.glob(p, recursive=True)))
        if len(hits) == 1:
            return hits[0], None
        if len(hits) > 1:
            return hits[0], f"{len(hits)} CIFs matched {p!r}; took {os.path.basename(hits[0])}"
    return None, None


def stage_from_cofold(cofold_dir, out_dir, design_path=None):
    """Assemble both legs' inputs from the co-fold outputs on disk. Fabricates nothing."""
    man = staging_manifest(design_path)
    d0_smiles = man["endpoint_smiles"][K.ENDPOINT_A]
    staged, missing = [], []
    for leg in man["legs"]:
        sp = leg["source_cofold_species"]
        cif, note = find_cofold_cif(cofold_dir, sp)
        if not cif:
            missing.append({"leg": leg["leg_id"],
                            "reason": f"no co-fold CIF named {K.cofold_cif_stem(sp)}*.cif for {sp} under "
                                      f"{cofold_dir}"})
            continue
        sdf, why, lig_info = _ligand_sdf_from_cif(cif, d0_smiles)
        if sdf is None:
            missing.append({"leg": leg["leg_id"], "cif": cif, "reason": why})
            continue
        # Built in a scratch dir and MOVED in only once every check passes. A half-populated `<leg>/` is worse
        # than an absent one: `run_ternary_leg.sh` skips staging when `complex.pdb` exists, so a leg dir
        # holding a protein and no ligands.sdf would be treated as staged and fail deep inside the engine.
        tmp = os.path.join(out_dir, f".staging_{leg['leg_id']}")
        os.makedirs(tmp, exist_ok=True)
        try:
            chains, counts = _write_protein_pdb(cif, os.path.join(tmp, "complex.pdb"))
        except Exception as e:  # noqa: BLE001
            shutil.rmtree(tmp, ignore_errors=True)
            missing.append({"leg": leg["leg_id"], "cif": cif, "reason": f"protein write failed: {e}"})
            continue
        leg_out = tmp
        # ⚠ A TERNARY LEG WITH ONE CHAIN IS A BINARY LEG THAT NOBODY LABELLED. `S` is a paralogue difference,
        # so a complex.pdb missing the target LBD would give two legs that differ in nothing and an S of ~0
        # that looks exactly like the preregistered null. Refuse here, where it is free.
        if len(chains) != len(leg["chain_roles"]):
            shutil.rmtree(tmp, ignore_errors=True)
            missing.append({"leg": leg["leg_id"], "cif": cif,
                            "reason": f"co-fold has {len(chains)} polymer chain(s) {chains} with residue "
                                      f"counts {counts}; this ternary leg needs exactly "
                                      f"{len(leg['chain_roles'])} ({leg['chain_roles']}). A one-chain "
                                      f"'ternary' leg is a binary leg and S would be ~0 by construction."})
            continue
        with open(os.path.join(leg_out, "ligands.sdf"), "w") as fh:
            fh.write(retitle_sdf(sdf, K.ENDPOINT_A) + retitle_sdf(sdf, K.ENDPOINT_B))
        # The engine reads `staging_manifest.json` for starting-model provenance and the reviewer's item-4
        # record. Writing our own means a 5a-KS leg reports where it came from instead of reporting `null`
        # because the file it looks for belongs to the crystal stager.
        rec = {"leg_id": leg["leg_id"], "source": "boltz2_cofold", "cofold_cif": os.path.basename(cif),
               "chains": chains, "residues_per_chain": counts, "expected_roles": leg["chain_roles"],
               "starting_model": 0, "n_relaxed_models": None,
               "endpoint_names": leg["ligand_endpoints"],
               "one_pose_two_endpoints": True,
               "limitation": ("the starting structure is a Boltz-2 PREDICTION of the ternary complex, not a "
                              "crystal structure; every result is conditional on that pose"),
               "cif_note": note, "ligand": lig_info}
        with open(os.path.join(leg_out, "staging_manifest.json"), "w") as fh:
            json.dump(rec, fh, indent=1)
        final = os.path.join(out_dir, leg["leg_id"])
        shutil.rmtree(final, ignore_errors=True)
        os.replace(tmp, final)
        staged.append({"leg": leg["leg_id"], "cif": cif, "chains": chains, "residues_per_chain": counts,
                       "expected_roles": leg["chain_roles"], "note": note,
                       "ligand_stereo_smiles": lig_info.get("stereo_smiles")})

    # ★ THE TWO LEGS MUST CARRY THE SAME MOLECULE, STEREOCHEMISTRY INCLUDED — AND NOTHING ELSE CHECKS THIS.
    # `S = dG_tern(NR4A3) - dG_tern(NR4A1)` is a difference of two legs, so anything that differs between
    # them other than the paralogue lands inside S and is indistinguishable from the signal. The design
    # leaves the glutarimide stereocentre unspecified (the thalidomide-class centre), which means Boltz
    # resolves it independently in each species' co-fold and can perfectly well resolve it BOTH WAYS. That
    # would make S a difference of two diastereomers in two different proteins, reported as a paralogue
    # wedge effect. It is free to catch here and invisible afterwards, so it refuses rather than warns.
    stereo = {s_["leg"]: s_.get("ligand_stereo_smiles") for s_ in staged}
    distinct = {v for v in stereo.values() if v}
    if len(staged) > 1 and len(distinct) > 1:
        for s_ in staged:
            shutil.rmtree(os.path.join(out_dir, s_["leg"]), ignore_errors=True)
        return {"staged": [], "out_dir": out_dir, "missing": [{
            "leg": "ALL", "reason": (
                "the two species' co-folds resolved the construct's UNSPECIFIED stereocentre differently, so "
                "S would be a difference of two diastereomers rather than of two paralogues. Per-leg: "
                f"{stereo}. Re-fold, or pin the centre in the design before staging.")}]}

    return {"staged": staged, "missing": missing, "out_dir": out_dir,
            "ligand_stereo_smiles_shared": (sorted(distinct)[0] if len(distinct) == 1 else None)}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--manifest", action="store_true", help="print the pure staging manifest and exit")
    ap.add_argument("--cofold-dir", default=os.environ.get("COFOLD_DIR", ""))
    ap.add_argument("--out-dir", default=os.environ.get("OUTPUT_DIR", "5aks_fep_inputs"))
    args = ap.parse_args(argv)
    if args.manifest or not args.cofold_dir:
        print(json.dumps(staging_manifest(), indent=1))
        return 0
    res = stage_from_cofold(args.cofold_dir, args.out_dir)
    print(json.dumps(res, indent=1))
    if res["missing"]:
        raise SystemExit(f"[5aks-stage] {len(res['missing'])} leg(s) NOT staged — nothing was fabricated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
