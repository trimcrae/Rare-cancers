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
check([l["ligand_endpoints"] for l in man["legs"]] == [[K.ENDPOINT_A, K.ENDPOINT_B]] * 2,
      "each leg declares exactly the two endpoint names the engine will look up")
check(man["source_cofolds"] == ["NR4A1", "NR4A3"],
      "one co-fold per species — not one per endpoint, which would put a pose difference inside S")
check(len(man["legs"]) == len(man["source_cofolds"]),
      "legs and co-folds are 1:1: two co-folds, two legs, no binary or solvent leg")

print("== the SMILES come from the design, and both endpoints are carried")
real = K.load_pair()
check(man["endpoint_smiles"][K.ENDPOINT_A] == real["d0"]["smiles"]
      and man["endpoint_smiles"][K.ENDPOINT_B] == real["d"]["smiles"],
      "the manifest's endpoint SMILES are the committed design's, not a copy")
src = open(os.path.join(HERE, "..", "nr4a3_5aks_stage.py")).read()
check(real["d"]["smiles"] not in src and real["d0"]["smiles"] not in src,
      "no molecule is hand-typed in the stager either")

print("== retitle_sdf writes the pose twice under the two endpoint names")
sdf = "SOMENAME\n  fake\n\n  0  0\nM  END\n$$$$\n"
both = S.retitle_sdf(sdf, K.ENDPOINT_A) + S.retitle_sdf(sdf, K.ENDPOINT_B)
check(both.count("$$$$") == 2, "two records out")
check(both.split("\n")[0] == K.ENDPOINT_A and f"\n{K.ENDPOINT_B}\n" in both,
      "titled with the two endpoint names")
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

print("== the co-fold lookup cannot pick up the CRBN+lenalidomide CONTROL")
# THE BUG THIS PINS, found on the first shakeout pass: the lookup was `*nr4a3*model_0.cif`, and
# `nr4a3_ternary.py` writes its positive control as `nr4a3-ternary-control` — a SINGLE-CHAIN CRBN complex
# with no NR4A3 in it. Sorted, `control` precedes `protac`, so the NR4A3 leg would have been staged from a
# structure containing neither the target nor the construct.
cd = tempfile.mkdtemp()
os.makedirs(os.path.join(cd, "boltz_results_x", "predictions", "y"), exist_ok=True)
for stem in ("nr4a3-ternary-control", "nr4a3-ternary-protac", "nr4a1-ternary-protac"):
    open(os.path.join(cd, "boltz_results_x", "predictions", "y", f"{stem}_model_0.cif"), "w").write("x")
hit3, _n3 = S.find_cofold_cif(cd, "NR4A3")
hit1, _n1 = S.find_cofold_cif(cd, "NR4A1")
check(hit3 and os.path.basename(hit3) == "nr4a3-ternary-protac_model_0.cif",
      "NR4A3 resolves to its TERNARY co-fold, not to the CRBN+lenalidomide control sitting beside it")
check(hit1 and os.path.basename(hit1) == "nr4a1-ternary-protac_model_0.cif",
      "NR4A1 resolves to its own co-fold and is not shadowed by NR4A3's")
check(S.find_cofold_cif(tempfile.mkdtemp(), "NR4A3")[0] is None,
      "an empty directory resolves to nothing rather than to whatever is nearby")

print("== the engine can actually resolve these legs, end to end, with no GPU")
import nr4a3_ternary_fep as FEP            # noqa: E402
import ternary_coop_prep as PREP           # noqa: E402
for lid in sorted(K.LEG_MAP):
    leg, env = FEP.leg_spec(lid)
    check(env == "ternary", f"{lid} resolves to a TERNARY leg in the engine")
    m = PREP._morph_endpoints(leg, resolve_smiles=True)
    check(m["endpoint_a"] == K.ENDPOINT_A and m["endpoint_b"] == K.ENDPOINT_B,
          f"{lid}'s morph string parses back to the two SDF record names the stager writes")
    check(m["smiles_a"] == real["d0"]["smiles"] and m["smiles_b"] == real["d"]["smiles"],
          f"{lid}'s endpoint SMILES resolve from the committed design, not from a copy in the engine")
# The whole reason the leg map is separate: resolving 5a-KS must not have disturbed the frozen bundle.
import ternary_coop as TCOOP               # noqa: E402
check(len(TCOOP.load_pilot_legs()) == 4,
      "the frozen pilot bundle still loads unchanged after the engine learned these legs")

print()
if fails:
    print(f"FAILED {len(fails)}: {fails}")
    sys.exit(1)
print("all 5a-KS staging tests passed")
