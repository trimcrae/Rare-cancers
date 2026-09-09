"""Baseline check: does this lane's heavy-atom recomputation of nr4a2-opened.pdb reproduce the committed
artifact's own heavy-atom columns? If it does not, nothing else in this lane is interpretable."""
import json, sys
mine = json.load(open("nr4a2-crystal-vs-model-cysteines.json"))["model"]["cysteines"]
art = json.load(open("/home/user/Rare-cancers/research/modalities/nr4a3-covalent-handle-ensemble.json"))
ref = art["opened_models"]["NR4A2"]["cysteines"]
fields = [("residue_sasa_heavy_A2", 0.01), ("rsa_heavy", 0.001), ("sg_sasa_heavy_A2", 0.01),
          ("sg_sasa_isolated_A2", 0.01)]
bad = 0
for u in ["465", "475", "505", "534", "566"]:
    for f, tol in fields:
        a, b = mine[u].get(f), ref[u].get(f)
        ok = a is not None and b is not None and abs(a - b) <= tol
        print(f"{u:>4} {f:<24} lane={a!s:<8} committed={b!s:<8} {'MATCH' if ok else 'MISMATCH'}")
        if not ok:
            bad += 1
    print(f"{u:>4} pdb_resnum lane={mine[u]['pdb_resnum']} committed={ref[u]['pdb_resnum']} "
          f"{'MATCH' if mine[u]['pdb_resnum']==ref[u]['pdb_resnum'] else 'MISMATCH'}")
    if mine[u]["pdb_resnum"] != ref[u]["pdb_resnum"]:
        bad += 1
print(f"\nmismatches: {bad}")
sys.exit(1 if bad else 0)
