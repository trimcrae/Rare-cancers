#!/usr/bin/env python3
"""RUNG 5a-KS — the HEAVY shakeout: co-fold CIF -> staged leg inputs -> both alchemical endpoints.

WHY THIS FILE EXISTS SEPARATELY FROM `test_5aks_stage.py`. That one is pure — no gemmi, no RDKit — and is
the contract. This one exercises the code that has to interpret a real structure file, which is where every
defect in this rung actually lived. It needs gemmi + RDKit, so it runs inside `triskit23/ternary-fep`: the
same image the FEP legs run in, which is the whole point (analysing or staging with a different RDKit than
the one that will run the leg is a silent protocol deviation).

IT BUILDS ITS OWN INPUT rather than committing a Boltz output. A co-fold CIF is ~1 MB of predicted
coordinates and would be a large binary artifact whose only job is to have the right SHAPE; the shape is
what the stager parses, so the test synthesises it — two polymer chains plus the construct as a non-polymer
residue, written by gemmi exactly as a structure file is written. The ligand's coordinates come from an
RDKit embedding of the COMMITTED d0 SMILES, so the chemistry under test is the design's, not a fixture's.

EVERY CHECK HERE CORRESPONDS TO A DEFECT THIS SHAKEOUT ACTUALLY FOUND (2026-07-26):
  1. the co-fold lookup matched the CRBN+lenalidomide CONTROL for the NR4A3 leg (sorted, `control` < `protac`)
  2. `remove_ligands_and_waters()` empties the ligand chain but does not delete it, so the chain census read
     3 chains and the "a ternary needs exactly 2" guard rejected good input
  3. RDKit assigns chirality FROM 3D, so the pose resolved the glutarimide centre the design leaves open and
     canonical-SMILES equality rejected a chemically correct ligand — in the stager AND in the engine
  4. changing an aromatic C to N with its explicit H still attached makes a pyrrole-type N-H, not pyridine:
     every candidate site failed to kekulize until the hydrogens came off
"""
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..")))
sys.path.insert(0, HERE)

from _skip_guard import skip_module    # noqa: E402

try:
    import gemmi
    from rdkit import Chem
    from rdkit.Chem import AllChem
    from rdkit import RDLogger
except ImportError as e:                                    # pragma: no cover - env probe
    # NOT a bare sys.exit(0): raised at module scope it aborts pytest COLLECTION and the whole
    # modalities suite reports "no tests ran". gemmi is absent from tests.yml, so this path is live.
    skip_module(f"needs gemmi + RDKit (run inside triskit23/ternary-fep): {e}")

RDLogger.DisableLog("rdApp.*")

import nr4a3_5aks_cofold as K      # noqa: E402
import nr4a3_5aks_stage as S       # noqa: E402
import nr4a3_ternary_fep as FEP    # noqa: E402
import ternary_coop_prep as PREP   # noqa: E402

fails = []


def check(cond, msg):
    print(("  ok   " if cond else "  FAIL ") + msg)
    if not cond:
        fails.append(msg)


PAIR = K.load_pair()
D0, D = K.endpoint_smiles(PAIR)


def _ligand_conformer():
    m = Chem.AddHs(Chem.MolFromSmiles(D0))
    if AllChem.EmbedMolecule(m, randomSeed=3) != 0:
        raise SystemExit("could not embed the committed d0 SMILES")
    AllChem.MMFFOptimizeMolecule(m)
    return Chem.RemoveHs(m)


LIG = _ligand_conformer()


def write_cofold(path, n_target_res=12, ligand_is_hetatm=True, with_target=True, ligand=None):
    """A structure file shaped like a Boltz-2 co-fold: CRBN chain, target chain, one non-polymer residue."""
    st = gemmi.Structure()
    st.spacegroup_hm = "P 1"
    st.cell = gemmi.UnitCell(1, 1, 1, 90, 90, 90)
    mod = gemmi.Model("1")

    def polymer(cid, n, x0):
        ch = gemmi.Chain(cid)
        for i in range(n):
            r = gemmi.Residue()
            r.name, r.seqid, r.het_flag = "ALA", gemmi.SeqId(i + 1, " "), "A"
            for an, dx in (("N", 0.0), ("CA", 1.5), ("C", 2.4), ("O", 3.0), ("CB", 1.6)):
                a = gemmi.Atom()
                a.name, a.element, a.occ = an, gemmi.Element(an[0]), 1.0
                a.pos = gemmi.Position(x0 + i * 3.8 + dx, dx, 0.0)
                r.add_atom(a)
            ch.add_residue(r)
        return ch

    mod.add_chain(polymer("B", 40, -200.0))                 # stands in for CRBN
    if with_target:
        mod.add_chain(polymer("A", n_target_res, 100.0))    # stands in for the NR4A LBD
    mol = ligand if ligand is not None else LIG
    conf = mol.GetConformer()
    lch = gemmi.Chain("C")
    lr = gemmi.Residue()
    lr.name, lr.seqid = "LIG", gemmi.SeqId(1, " ")
    lr.het_flag = "H" if ligand_is_hetatm else "A"
    for i, at in enumerate(mol.GetAtoms()):
        p = conf.GetAtomPosition(i)
        a = gemmi.Atom()
        a.name, a.element, a.occ = f"{at.GetSymbol()}{i + 1}", gemmi.Element(at.GetSymbol()), 1.0
        a.pos = gemmi.Position(p.x, p.y, p.z)
        lr.add_atom(a)
    lch.add_residue(lr)
    mod.add_chain(lch)
    st.add_model(mod)
    st.setup_entities()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    st.make_mmcif_document().write_file(path)
    return path


def build_cofold_dir(**kw):
    root = tempfile.mkdtemp()
    pred = os.path.join(root, "boltz_results_x", "predictions", "y")
    for sp in ("NR4A3", "NR4A1"):
        write_cofold(os.path.join(pred, K.cofold_cif_stem(sp) + "_model_0.cif"), **kw)
    return root


print("== a co-fold set stages both legs, and the CONTROL sitting beside it is not picked up")
root = build_cofold_dir()
# nr4a3_ternary.py leaves `nr4a3-ternary-control` — CRBN + lenalidomide, NO NR4A3 — in the same tree.
write_cofold(os.path.join(root, "boltz_results_x", "predictions", "y",
                          "nr4a3-ternary-control_model_0.cif"), with_target=False)
out = os.path.join(root, "staged")
res = S.stage_from_cofold(root, out)
check(not res["missing"] and len(res["staged"]) == 2,
      f"both legs staged from real structure files: {res['missing']}")
check(all(os.path.basename(s["cif"]).startswith(K.cofold_cif_stem(s["leg"].split("_")[-1]))
          for s in res["staged"]),
      "each leg took its OWN species' ternary co-fold, not the single-chain control beside it")
for s in res["staged"]:
    check(len(s["chains"]) == 2, f"{s['leg']}: complex.pdb carries exactly the two polymer chains")
check(res["ligand_stereo_smiles_shared"] is not None,
      "both legs resolved the construct's unspecified stereocentre the SAME way")

print("== the staged files are what the engine mounts")
for leg_id in sorted(K.LEG_MAP):
    d = os.path.join(out, leg_id)
    check(os.path.isfile(os.path.join(d, "complex.pdb")), f"{leg_id}/complex.pdb exists")
    check(os.path.isfile(os.path.join(d, "ligands.sdf")), f"{leg_id}/ligands.sdf exists")
    man = json.load(open(os.path.join(d, "staging_manifest.json")))
    check(man["source"] == "boltz2_cofold" and man["limitation"],
          f"{leg_id} records that it started from a PREDICTION, with the limitation stated")
    names = [b.lstrip("\n").split("\n")[0] for b in open(os.path.join(d, "ligands.sdf")).read().split("$$$$")
             if b.strip()]
    check(names == [K.ENDPOINT_A, K.ENDPOINT_B],
          f"{leg_id}: the SDF records carry the two names the engine looks up ({names})")
    pdb = open(os.path.join(d, "complex.pdb")).read()
    check(not any(l.startswith("HETATM") for l in pdb.splitlines()),
          f"{leg_id}: the ligand is NOT in complex.pdb — the engine adds it from the SDF")

print("== THE POINT OF THE RUNG: the two endpoints differ by exactly one atom and nothing else")
for leg_id in sorted(K.LEG_MAP):
    leg, env = FEP.leg_spec(leg_id)
    m = PREP._morph_endpoints(leg, resolve_smiles=True)
    a, b, sa, sb = m["endpoint_a"], m["endpoint_b"], m["smiles_a"], m["smiles_b"]
    FEP.CRYSTAL_SMILES = sa
    sdf = os.path.join(out, leg_id, "ligands.sdf")
    molA = FEP._endpoint_pose(sdf, a, sa, sa, Chem)
    molB = FEP._endpoint_pose(sdf, b, sb, sa, Chem)
    hA, hB = Chem.RemoveHs(Chem.Mol(molA)), Chem.RemoveHs(Chem.Mol(molB))
    check(hA.GetNumAtoms() == hB.GetNumAtoms() == Chem.MolFromSmiles(D0).GetNumHeavyAtoms(),
          f"{leg_id}: both endpoints have the design's heavy-atom count")
    elems = [(i, x.GetSymbol(), y.GetSymbol()) for i, (x, y) in enumerate(zip(hA.GetAtoms(), hB.GetAtoms()))
             if x.GetSymbol() != y.GetSymbol()]
    check(elems == [(elems[0][0], "C", "N")] if elems else False,
          f"{leg_id}: exactly ONE element change, C->N — the aza-scan and nothing else ({elems})")
    pA = hA.GetConformer().GetPositions()
    pB = hB.GetConformer().GetPositions()
    worst = max(abs(float(x)) for row in (pA - pB) for x in row)
    # Both endpoints MUST come from the same pose. Any coordinate difference is a structural perturbation
    # the alchemical transformation would have to absorb on top of the aza-scan, and it would land in S.
    check(worst == 0.0, f"{leg_id}: the endpoints' heavy-atom coordinates are IDENTICAL (max diff {worst})")

print("== the other Boltz writer convention (ligand chain flagged ATOM, not HETATM) also stages")
r2 = build_cofold_dir(ligand_is_hetatm=False)
o2 = os.path.join(r2, "staged")
res2 = S.stage_from_cofold(r2, o2)
check(len(res2["staged"]) == 2 and not res2["missing"],
      f"het_flag is a hint, not the authority — staging does not depend on it: {res2['missing']}")

print("== refusals: nothing is fabricated, and each refusal names the real cause")
r3 = build_cofold_dir(with_target=False)
res3 = S.stage_from_cofold(r3, os.path.join(r3, "staged"))
check(not res3["staged"] and all("needs exactly 2" in m["reason"] for m in res3["missing"]),
      "a co-fold missing the target chain is refused — a one-chain 'ternary' would give S ~ 0 by construction")

wrong = Chem.AddHs(Chem.MolFromSmiles("c1ccccc1C(=O)NCCOCCOCCNC(=O)c1ccccc1"))
AllChem.EmbedMolecule(wrong, randomSeed=1)
r4 = build_cofold_dir(ligand=Chem.RemoveHs(wrong))
res4 = S.stage_from_cofold(r4, os.path.join(r4, "staged"))
check(not res4["staged"] and all("did not match" in m["reason"] or "matched the committed" in m["reason"]
                                 for m in res4["missing"]),
      "a co-fold whose ligand is NOT the committed construct is refused, never templated into one")

print("== a stereocentre the design SPECIFIES cannot be silently inverted")
inv = Chem.MolFromSmiles(D0.replace("[C@@H]", "[C@H]"))
inv = Chem.AddHs(inv)
AllChem.EmbedMolecule(inv, randomSeed=5)
_sdf, why, _info = S._ligand_sdf_from_cif(
    write_cofold(os.path.join(tempfile.mkdtemp(), "p", K.cofold_cif_stem("NR4A3") + "_model_0.cif"),
                 ligand=Chem.RemoveHs(inv)), D0)
check(_sdf is None and "stereocentre" in (why or ""),
      f"an inverted alpha-carbon is caught even though the glutarimide centre is allowed to float ({why})")

print()
if fails:
    print(f"FAILED {len(fails)}: {fails}")
    sys.exit(1)
print("all 5a-KS pose/staging shakeout tests passed")
