#!/usr/bin/env python3
"""Unit tests for the RUNG 5a-KS double difference — pure arithmetic, no network, no GPU.

`S` is the number this rung exists to produce, and every failure mode below yields a plausible-looking value
rather than an error, which is why they are tested rather than trusted:

  * the binary leg cancels ALGEBRAICALLY in S. Subtracting it from both arms is merely noisier; subtracting it
    from ONE arm computes a different quantity entirely and nothing downstream could tell.
  * a sign slip flips DISCRIMINATION into ANTI-SELECTIVE, and both are publishable-looking numbers.
  * a missing arm must not quietly reduce to "the other arm".
  * identity fields that are absent must read as UNRECORDED, never as agreement — the 4 fs cycle reached a
    verdict in exactly that state.
"""
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..")))

import nr4a3_5aks_reduce as R    # noqa: E402

fails = []


def check(cond, msg):
    if cond:
        print(f"  ok   {msg}")
    else:
        print(f"  FAIL {msg}")
        fails.append(msg)


def leg(species, seed=0, dg=0.0, se=0.1, **over):
    d = {"leg_id": R.leg_id(species), "seed": seed, "dg_morph_kcal": dg, "mbar_se_kcal": se,
         "protocol_hash": "h", "charge_method": "nagl", "setup_cache_version": "v1",
         "n_particles": 141968, "n_windows": 16}
    d.update(over)
    return d


def legset(*ds):
    return {(d["leg_id"], d["seed"]): d for d in ds}


print("== the sign convention is the designed direction, and it is not reversible by accident")
# NR4A3 tolerates the pyridyl better => its dG(d0->d) is LOWER => S negative => discrimination.
res = R.reduce_S(legset(leg("NR4A3", dg=1.0), leg("NR4A1", dg=2.5)))
check(res["S_kcal"] == -1.5, f"S = dG_tern(NR4A3) - dG_tern(NR4A1) = -1.5 (got {res.get('S_kcal')})")
check("S < 0" in res["sign_reading"], "the artifact states which sign means discrimination")
res_anti = R.reduce_S(legset(leg("NR4A3", dg=2.5), leg("NR4A1", dg=1.0)))
check(res_anti["S_kcal"] == 1.5, "the reversed case gives +1.5 — anti-selective, not silently absolute-valued")

print("== a binary or solvent leg must be REFUSED, not absorbed")
bin_leg = leg("NR4A3"); bin_leg["leg_id"] = f"{R.MORPH}__binary_crbn"
res = R.reduce_S(legset(leg("NR4A3", dg=1.0), leg("NR4A1", dg=2.5), bin_leg))
check(res["decision"] == "REFUSED" and "cancel ALGEBRAICALLY" in res["reason"],
      "a binary 5a-KS leg refuses the reduction and the message says why it cancels")
sol = leg("NR4A3"); sol["leg_id"] = f"{R.MORPH}__solvent"
check(R.reduce_S(legset(leg("NR4A3"), leg("NR4A1"), sol))["decision"] == "REFUSED",
      "a solvent 5a-KS leg is refused too")

print("== a missing arm does not silently become the other arm")
res = R.reduce_S(legset(leg("NR4A3", dg=1.0)))
check(res["decision"] == "INCOMPLETE" and "NR4A1" in res["reason"],
      "one arm only -> INCOMPLETE, naming the species that is missing")
check("S_kcal" not in res, "...and no S is emitted at all")

print("== error bars: replicate SD when it exists, and an explicit refusal to pretend otherwise")
res1 = R.reduce_S(legset(leg("NR4A3", dg=1.0), leg("NR4A1", dg=2.5)))
check(res1["decision"] == "COMPUTED_SINGLE_SEED" and res1["S_err_kind"].startswith("mbar_se_ONLY"),
      "one seed per arm is flagged COMPUTED_SINGLE_SEED with an MBAR-only error bar")
check(res1["_single_seed_warning"] and "replicate-SD" in res1["_single_seed_warning"],
      "...and carries the warning that the repo's standard is replicate-SD")
res3 = R.reduce_S(legset(leg("NR4A3", 0, 1.0), leg("NR4A3", 1, 1.2), leg("NR4A3", 2, 0.8),
                         leg("NR4A1", 0, 2.5), leg("NR4A1", 1, 2.3), leg("NR4A1", 2, 2.7)))
check(res3["decision"] == "COMPUTED" and res3["S_err_kind"] == "replicate_sd",
      "three seeds per arm -> COMPUTED with a replicate SD")
check(abs(res3["S_kcal"] - (1.0 - 2.5)) < 1e-9, "S uses the per-arm MEAN over seeds")
check(res3["S_err_kcal"] and res3["S_err_kcal"] > 0, "the replicate SD propagates in quadrature")
check(res3["_single_seed_warning"] is None, "no single-seed warning once replicates exist")

print("== absent provenance is a PROBLEM, never agreement")
probs = R.identity_problems(legset(leg("NR4A3", setup_cache_version=None),
                                   leg("NR4A1", setup_cache_version=None)))
check(any(p["field"] == "setup_cache_version" and p["kind"] == "UNRECORDED" for p in probs),
      "a field unrecorded on every leg reports UNRECORDED — the state the 4 fs cycle was reduced in")
probs = R.identity_problems(legset(leg("NR4A3", n_particles=141968), leg("NR4A1", n_particles=146020)))
check(any(p["field"] == "n_particles" and p["kind"] == "DISAGREES" for p in probs),
      "141,968 vs 146,020 is caught as DISAGREES — the exact incident this check exists for")
check(R.identity_problems(legset(leg("NR4A3"), leg("NR4A1"))) == [],
      "fully recorded, fully agreeing legs raise nothing")

print("== load_legs reads only this rung's legs, and tolerates junk")
td = tempfile.mkdtemp()
json.dump(leg("NR4A3", dg=1.0), open(os.path.join(td, "leg_a.json"), "w"))
json.dump({"leg_id": "calib_hi_to_lo__ternary_vhl", "seed": 0, "dg_morph_kcal": 47.6},
          open(os.path.join(td, "leg_other.json"), "w"))
open(os.path.join(td, "leg_broken.json"), "w").write("{not json")
got = R.load_legs(td)
check(len(got) == 1 and list(got)[0][0] == R.leg_id("NR4A3"),
      "another lane's leg and an unparseable file are both ignored rather than mixed in")

print("== a SMOKE record cannot silently displace the production record it shares a key with")
# The key is (leg_id, seed) and the mode lives only in unit_id, so these two collide. A smoke leg runs 12
# production iterations; its dG is meaningless by construction yet perfectly well-formed, so a silent
# overwrite yields an S that passes every other check in this module.
td2 = tempfile.mkdtemp()
prod = leg("NR4A3", dg=1.0); prod["unit_id"] = "5aks_..._5aks";       prod["mode"] = "5aks"
smoke = leg("NR4A3", dg=9.9); smoke["unit_id"] = "5aks_..._5aks_smoke"; smoke["mode"] = "5aks_smoke"
json.dump(prod, open(os.path.join(td2, "leg_a_prod.json"), "w"))
json.dump(smoke, open(os.path.join(td2, "leg_b_smoke.json"), "w"))
try:
    R.load_legs(td2)
    check(False, "two differing records for one key are REFUSED, not silently deduplicated")
except R.AmbiguousLegError as e:
    check("5aks_smoke" in str(e) and "silently overwrite" in str(e),
          "two differing records for one key are REFUSED, and the message names both")

td3 = tempfile.mkdtemp()
json.dump(prod, open(os.path.join(td3, "leg_a.json"), "w"))
json.dump(dict(prod), open(os.path.join(td3, "leg_a_copy.json"), "w"))
check(len(R.load_legs(td3)) == 1,
      "...but an identical record twice is a duplicate download, not an ambiguity")

print()
if fails:
    print(f"FAILED {len(fails)}: {fails}")
    sys.exit(1)
print("all 5a-KS reduction tests passed")
