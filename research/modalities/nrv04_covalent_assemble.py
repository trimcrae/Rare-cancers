#!/usr/bin/env python3
"""
NR-V04 covalent feasibility panel — structural assembler (prereg §7 build gate).

Turns a Boltz-2 co-fold prediction (NR4A1+VHL+NR-V04 / +celastrol / +epimer) into the per-leg inputs the MD
driver mounts: <leg_id>/complex.pdb (protein, chain-surgeried for the leg's environment) + <leg_id>/ligand.sdf
(the co-fold ligand POSE with correct bond orders).

The load-bearing (previously-stubbed) piece is the ligand extraction: a co-fold CIF carries the ligand's atoms +
coordinates but not reliable bond orders, so we perceive connectivity from the coordinates and then assign the
bond orders from the KNOWN frozen SMILES (nrv04_ligands) via RDKit's AssignBondOrdersFromTemplate. This is the
standard, non-fabricating way to recover a chemically-correct posed ligand — every atom stays at its co-fold
coordinate; only the bond orders come from the template. The connectivity+template kernel is unit-tested offline
by round-tripping celastrol; the gemmi CIF read runs on a CI/CPU runner.
"""
from __future__ import annotations


def ligand_mol_from_coords(elements, coords, template_smiles):
    """Build a chemically-correct, POSED RDKit mol from co-fold heavy-atom coordinates + the known SMILES.

    We do NOT trust distance-perceived bond orders (they add spurious bonds and corrupt the valence). Instead we
    build the exact molecule FROM THE TEMPLATE (correct topology + implicit H) and transfer the co-fold
    coordinates onto it via a heavy-atom GRAPH MATCH between the template and a connectivity-only coord mol. The
    result's chemistry is exactly the template's; every heavy atom sits at its co-fold coordinate. Hs are added
    with coordinates. Raises if the template graph doesn't match the co-fold atom graph."""
    from rdkit import Chem
    from rdkit.Chem import AllChem, rdDetermineBonds
    from rdkit.Geometry import Point3D

    rw = Chem.RWMol()
    for el in elements:
        rw.AddAtom(Chem.Atom(el))
    coord_mol = rw.GetMol()
    cc = Chem.Conformer(coord_mol.GetNumAtoms())
    for i, (x, y, z) in enumerate(coords):
        cc.SetAtomPosition(i, Point3D(float(x), float(y), float(z)))
    coord_mol.AddConformer(cc, assignId=True)
    rdDetermineBonds.DetermineConnectivity(coord_mol)     # connectivity ONLY, to enable the graph match

    template = Chem.RemoveHs(Chem.MolFromSmiles(template_smiles))
    if template.GetNumAtoms() != coord_mol.GetNumAtoms():
        raise ValueError(f"template heavy atoms {template.GetNumAtoms()} != co-fold heavy atoms {coord_mol.GetNumAtoms()}")
    # match on the bond-order-agnostic SKELETON (element + connectivity), so aromatic/double template bonds vs
    # the all-single perceived coord bonds don't block the correspondence.
    sk_t, sk_c = _skeleton(template), _skeleton(coord_mol)
    match = sk_c.GetSubstructMatch(sk_t)                  # template atom i -> coord atom match[i]
    if not match or len(match) != template.GetNumAtoms():
        raise ValueError("template<->co-fold heavy-atom graph match failed (bad pose connectivity?)")

    posed = Chem.Mol(template)                            # topology = template (no spurious bonds)
    conf = Chem.Conformer(posed.GetNumAtoms())
    for ti, ci in enumerate(match):
        p = cc.GetAtomPosition(ci)
        conf.SetAtomPosition(ti, p)
    posed.RemoveAllConformers()
    posed.AddConformer(conf, assignId=True)
    posed = Chem.AddHs(posed, addCoords=True)
    Chem.SanitizeMol(posed)
    return posed


def _skeleton(mol):
    """A bond-order/aromaticity-agnostic copy (all single bonds, no implicit-H valence): element + connectivity
    only, for a graph match that ignores how bonds are drawn."""
    from rdkit import Chem
    em = Chem.RWMol()
    for a in mol.GetAtoms():
        na = Chem.Atom(a.GetAtomicNum()); na.SetNoImplicit(True); em.AddAtom(na)
    for b in mol.GetBonds():
        em.AddBond(b.GetBeginAtomIdx(), b.GetEndAtomIdx(), Chem.BondType.SINGLE)
    return em.GetMol()


def extract_ligand_from_cif(cif_path, template_smiles, out_sdf):
    """Pull the non-polymer ligand's heavy atoms + coords from a co-fold CIF (gemmi) and write a bond-order-correct
    posed SDF via the template kernel. Returns the ligand atom count. CI/CPU (needs gemmi + rdkit)."""
    import gemmi
    from rdkit import Chem

    st = gemmi.read_structure(cif_path)
    elements, coords = [], []
    for chain in st[0]:
        for res in chain:
            if res.is_amino_acid() or res.is_nucleic_acid() or res.name in ("HOH", "WAT"):
                continue
            for atom in res:                              # ligand heavy atoms only
                if atom.element.name != "H":
                    elements.append(atom.element.name)
                    coords.append((atom.pos.x, atom.pos.y, atom.pos.z))
    if not elements:
        raise SystemExit(f"[assemble] no ligand (non-polymer) atoms in {cif_path}")
    mol = ligand_mol_from_coords(elements, coords, template_smiles)
    w = Chem.SDWriter(out_sdf); w.write(mol); w.close()
    return len(elements)


def write_complex_pdb(cif_path, keep_chains, out_pdb):
    """Write only the kept PROTEIN chains (drop ligand/waters/ions; drop the target for a binary leg) CIF->PDB."""
    import gemmi
    st = gemmi.read_structure(cif_path)
    st.setup_entities()
    model = st[0]
    for name in [ch.name for ch in model]:
        if keep_chains and name not in keep_chains:
            model.remove_chain(name)
    st.remove_ligands_and_waters()
    st.remove_empty_chains()
    if not any(True for ch in st[0] for _ in ch):
        raise SystemExit(f"[assemble] no protein residues left after chain surgery keep={keep_chains}")
    st.write_pdb(out_pdb)


def assemble_leg(cif_path, leg, template_smiles, out_dir, keep_chains=None):
    """Produce <out_dir>/<leg.leg_id>/{complex.pdb, ligand.sdf} for one panel leg. `leg` is a
    nrv04_covalent_panel.Leg; binary legs drop the target chain via keep_chains."""
    import os
    leg_out = os.path.join(out_dir, leg.leg_id)
    os.makedirs(leg_out, exist_ok=True)
    n = extract_ligand_from_cif(cif_path, template_smiles, os.path.join(leg_out, "ligand.sdf"))
    write_complex_pdb(cif_path, keep_chains, os.path.join(leg_out, "complex.pdb"))
    return {"leg": leg.leg_id, "ligand_atoms": n, "out": leg_out}
