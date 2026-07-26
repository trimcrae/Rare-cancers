#!/usr/bin/env python3
"""Unit tests for RUNG 5a-KS input staging — pure planner + the SDF retitling, no gemmi/RDKit/network.

The heavy assembler needs real Boltz output and runs on a CI runner. What is tested here is the contract it
must satisfy and the two things that would silently corrupt `S`:

  * the chain roles. This rung recruits **CRBN**, one chain; the frozen pilot's stager hardcodes
    VHL + Elongin B + Elongin C. Staging a leg against the wrong E3 role set writes a complex.pdb missing the
    recruiter or carrying two extra chains, and the leg would still run.
  * `ligands.sdf` must be ONE pose written twice. Two poses would put a coordinate difference between the
    endpoints that the alchemical transformation absorbs — a contribution to `S` that is not the aza-scan.
"""
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..")))

import nr4a3_5aks_cofold as K    # noqa: E402
import nr4a3_5aks_stage as S     # noqa: E402

fails = []


def check(cond, msg):
    if cond:
        print(f"  ok   {msg}")
    else:
        print(f"  FAIL {msg}")
        fails.append(msg)


print("== the chain roles are CRBN + the target, NOT the frozen pilot's VHL machinery")
man = S.staging_manifest()
for leg in man["legs"]:
    check(leg["chain_roles"][0] == "CRBN",
          f"{leg['leg_id']} recruits CRBN, not VHL — the pilot stager's E3_ROLES would be wrong here")
    check(len(leg["chain_roles"]) == 2 and leg["chain_roles"][1] == leg["source_cofold_species"],
          f"{leg['leg_id']} carries exactly two chains: CRBN + its own paralogue")
    check(leg["environment"] == "ternary" and leg["needs_complex_pdb"],
          f"{leg['leg_id']} is ternary and needs a complex.pdb")

import ternary_fep_stage as PILOT    # noqa: E402
check(PILOT.E3_ROLES == ["VHL", "ElonginB", "ElonginC"],
      "the pilot stager really does hardcode the VHL machinery (which is why this rung has its own)")
check(all(set(l["chain_roles"]).isdisjoint(PILOT.E3_ROLES) for l in man["legs"]),
      "no 5a-KS leg shares a chain role with the pilot's E3 machinery")

print("== both endpoints are staged from ONE pose")
check([l["ligand_endpoints"] for l in man["legs"]] == [["d0", "d"], ["d0", "d"]],
      "each leg declares exactly the two endpoints d0 and d")
check(man["source_cofolds"] == ["NR4A1", "NR4A3"],
      "one co-fold per species — not one per endpoint, which would put a pose difference inside S")
check(len(man["legs"]) == len(man["source_cofolds"]),
      "legs and co-folds are 1:1: two co-folds, two legs, no binary or solvent leg")

print("== the SMILES come from the design, and both endpoints are carried")
real = K.load_pair()
check(man["endpoint_smiles"]["d0"] == real["d0"]["smiles"]
      and man["endpoint_smiles"]["d"] == real["d"]["smiles"],
      "the manifest's endpoint SMILES are the committed design's, not a copy")
src = open(os.path.join(HERE, "..", "nr4a3_5aks_stage.py")).read()
check(real["d"]["smiles"] not in src and real["d0"]["smiles"] not in src,
      "no molecule is hand-typed in the stager either")

print("== retitle_sdf writes the pose twice under the two endpoint names")
sdf = "SOMENAME\n  fake\n\n  0  0\nM  END\n$$$$\n"
both = S.retitle_sdf(sdf, "d0") + S.retitle_sdf(sdf, "d")
check(both.count("$$$$") == 2, "two records out")
check(both.split("\n")[0] == "d0" and "\nd\n" in both, "titled d0 and d")
check("SOMENAME" not in both, "the original title is replaced, not appended")
check(both.count("M  END") == 2, "each record keeps its molblock body — the SAME coordinates twice")

print("== a leg that is not this rung's is refused rather than guessed at")
try:
    S.required_inputs_for_leg("calib_hi_to_lo__ternary_vhl")
    check(False, "a foreign leg id must raise")
except SystemExit as e:
    check("not a 5a-KS leg" in str(e), "a foreign leg id raises rather than inventing chain roles")

print("== the heavy assembler fabricates nothing when the co-folds are absent")
td = tempfile.mkdtemp()
res = S.stage_from_cofold(td, os.path.join(td, "out"))
check(res["staged"] == [] and len(res["missing"]) == 2,
      "an empty co-fold dir stages nothing and reports both legs missing")
check(all("no co-fold CIF" in m["reason"] for m in res["missing"]),
      "...and the reason names what is absent")
check(not os.path.exists(os.path.join(td, "out", "5aks_d0_to_d__ternary_nr4a3", "ligands.sdf")),
      "no partial leg directory is left behind")

print()
if fails:
    print(f"FAILED {len(fails)}: {fails}")
    sys.exit(1)
print("all 5a-KS staging tests passed")
