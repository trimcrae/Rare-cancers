#!/usr/bin/env python3
"""Unit tests for RUNG 5a-KS co-fold staging — pure planner only (no network, no GPU, no Boltz).

The load-bearing check is `pair_is_matched`. `S = ddG_coop(d0->d | NR4A3) - ddG_coop(d0->d | NR4A1)` is a
DOUBLE difference, so if `d` and `d0` were ever the same molecule — or differed by more than the preregistered
aza-scan — `S` would come back ~0 and read as a clean null on the marginal wedge. That is the single most
expensive way this rung could fail, because a null is ALREADY the honestly-recorded expectation, so nothing
downstream would look wrong. The check runs before any GPU time and refuses rather than warns.
"""
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..")))

import nr4a3_5aks_cofold as K     # noqa: E402

fails = []


def check(cond, msg):
    if cond:
        print(f"  ok   {msg}")
    else:
        print(f"  FAIL {msg}")
        fails.append(msg)


PHENYL = "CC(=O)N[C@@H](Cc7ccccc7)C(=O)N"
PYRIDYL = "CC(=O)N[C@@H](Cc7cccnc7)C(=O)N"


def mp(d0=PHENYL, d=PYRIDYL, **over):
    out = {"d0": {"smiles": d0}, "d": {"smiles": d},
           "wedge_target_residue": {"uniprot_resid": 407}, "test": "S = ..."}
    out.update(over)
    return out


print("== the matched pair must be the one-atom aza-scan, checked BEFORE any GPU time")
ok, why = K.pair_is_matched(mp())
check(ok and "index" in why, "a genuine phenyl -> 3-pyridyl pair passes and reports where the atom changed")

ok, why = K.pair_is_matched(mp(d=PHENYL))
check(not ok and "identical" in why,
      "identical endpoints are REFUSED — S would be 0 by construction and read as a clean null")

ok, why = K.pair_is_matched(mp(d="CC(=O)N[C@@H](Cc7cccnc7)C(=O)NC"))
check(not ok and "length" in why, "a length change is refused — that is not a one-atom substitution")

ok, why = K.pair_is_matched(mp(d0="CC(=O)N[C@@H](Cc7ccccc7)C(=O)NC",
                               d="CC(=O)N[C@@H](Cc7cccnc7)C(=O)NN"))
check(not ok and "2 positions" in why, "two substitutions are refused — the pair is no longer matched")

ok, why = K.pair_is_matched(mp(d0="CC(=O)N[C@@H](Cc7ccccc7)C(=O)NC",
                               d="CC(=O)N[C@@H](Cc7ccccc7)C(=O)NO"))
check(not ok and "'C' -> 'O'" in why,
      "a one-character change that is NOT aromatic C -> N is refused, and the message names what it saw")

print("== the real committed pair passes")
real = K.load_pair()
ok, why = K.pair_is_matched(real)
check(ok, f"the pair RUNG 5b actually committed is a one-atom aza-scan ({why})")

print("== the planner's contract")
plan = K.cofold_plan(real)
check([p["species"] for p in plan] == ["NR4A3", "NR4A1"],
      "exactly NR4A3 and NR4A1 are planned — NR4A2 is what a discriminating result earns, not a prepaid leg")
check(all(p["cofold_ligand_smiles"] == real["d0"]["smiles"] for p in plan),
      "d0 is the molecule co-folded; both endpoints are later staged from that ONE pose")
check(all(p["perturbed_endpoint_smiles"] == real["d"]["smiles"] for p in plan),
      "d rides along on the plan, so the simulated endpoints stay tied to the committed design")
check(len({p["leg_id"] for p in plan}) == len(plan), "leg ids are distinct")
check(all(p["environment"] == "ternary" for p in plan),
      "ternary only — the binary and solvent legs cancel in the double difference (wedge is 9.0 A off the E3)")


print("== the leg ids must be classified TERNARY by the real FEP engine")
# The trap: nr4a3_ternary_fep._environment_of falls back to `"ternary" if "__ternary" in leg_id else "binary"`
# for any id not in the FROZEN PILOT_LEG_MAP. A single-underscore id (5aks_ternary_nr4a3 — which is what this
# planner emitted first) classifies as BINARY, so the engine would drop the target chain and S would be a
# difference of two binary legs with no paralogue in them. A binary leg converges perfectly well, so nothing
# downstream would look wrong.
import nr4a3_ternary_fep as ENG          # noqa: E402
import ternary_coop as TCOOP             # noqa: E402

for p_ in plan:
    check(ENG._environment_of(p_["leg_id"]) == "ternary",
          f"the engine classifies {p_['leg_id']} as ternary, not binary")
check(ENG._environment_of("5aks_ternary_nr4a3") == "binary",
      "...and the single-underscore form this planner first emitted really would have been read as BINARY")
check(len({ENG._morph_key(p_["leg_id"]) for p_ in plan}) == 1,
      "both species' legs share ONE morph key, as the repo's binary/ternary arms of a pair do")

print("== 5a-KS legs must NOT be added to the frozen pilot bundle")
check(all(lid not in TCOOP.PILOT_LEG_MAP for lid in K.LEG_MAP),
      "no 5a-KS leg appears in ternary_coop.PILOT_LEG_MAP — that map is the PREREGISTERED pilot, and "
      "load_pilot_legs fails closed on drift, so extending it would either break the guard or silently "
      "enlarge a preregistered experiment")
TCOOP.load_pilot_legs()      # must still agree with the frozen manifest
check(True, "load_pilot_legs still agrees with the frozen manifest after this module is imported")
check(all(K.LEG_MAP[lid]["target"] in K.SPECIES and K.LEG_MAP[lid]["environment"] == "ternary"
          for lid in K.LEG_MAP), "each 5a-KS leg records its target species and the ternary environment")

print("== a partial or absent design is refused, never guessed around")
for bad, want in ((  {"matched_pair_for_rung_5a_ks": {}},                       "no `matched_pair"),
                  (  {},                                                        "no `matched_pair"),
                  (  {"matched_pair_for_rung_5a_ks": {"d": {"smiles": "C"}}},    "missing")):
    td = tempfile.mkdtemp()
    p = os.path.join(td, "design.json")
    json.dump(bad, open(p, "w"))
    try:
        K.load_pair(p)
        check(False, f"a design lacking the pair must raise ({want})")
    except SystemExit as e:
        check(want in str(e), f"a design lacking the pair raises and says why ({want})")

td = tempfile.mkdtemp()
p = os.path.join(td, "design.json")
json.dump({"matched_pair_for_rung_5a_ks": {"d": {}, "d0": {"smiles": "C"},
                                           "wedge_target_residue": {}, "test": "x"}}, open(p, "w"))
try:
    K.load_pair(p)
    check(False, "an endpoint with no SMILES must raise")
except SystemExit as e:
    check("no SMILES" in str(e), "an endpoint carrying no SMILES is refused rather than invented")

print("== no molecule is hand-typed in the module")
src = open(os.path.join(HERE, "..", "nr4a3_5aks_cofold.py")).read()
check(real["d"]["smiles"] not in src and real["d0"]["smiles"] not in src,
      "neither endpoint's SMILES appears in the source — a second copy is how a design and the thing "
      "actually simulated drift apart")

print()
if fails:
    print(f"FAILED {len(fails)}: {fails}")
    sys.exit(1)
print("all 5a-KS co-fold staging tests passed")
