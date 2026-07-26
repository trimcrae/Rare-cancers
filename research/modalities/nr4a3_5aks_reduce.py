#!/usr/bin/env python3
"""RUNG 5a-KS — reduce the two ternary legs to the ligand-side double difference `S`.

THE ALGEBRA, AND WHY ONLY TWO LEGS ARE PAID FOR
-----------------------------------------------
The preregistered quantity is

    S = ddG_coop(d0 -> d | NR4A3) - ddG_coop(d0 -> d | NR4A1)

and each species' cooperativity difference is itself a difference of environments:

    ddG_coop(d0 -> d | X) = dG_ternary(X) - dG_binary

The binary leg is the ligand + E3 with **no target chain**, so it is the SAME physical leg for both species —
the construct and CRBN are identical; only the paralogue differs, and it is absent. Substituting:

    S = [dG_tern(NR4A3) - dG_bin] - [dG_tern(NR4A1) - dG_bin]
      =  dG_tern(NR4A3) - dG_tern(NR4A1)

**The binary leg cancels EXACTLY, algebraically, not approximately** — and so does the solvent leg beneath it.
That is the whole reason this rung costs two ternary legs rather than a full cycle per species. It is also a
trap: a well-meaning "completeness" pass that measures the binary leg and subtracts it from each arm computes
the same number with strictly more noise, and one that subtracts it from only ONE arm computes garbage. Hence
`refuse_non_ternary` below.

SIGN CONVENTION, STATED ONCE
----------------------------
Each leg's `dg_morph_kcal` is dG(d0 -> d) in that environment: positive means the pyridyl endpoint `d` is
DISFAVOURED relative to the phenyl control `d0`. So

    S < 0  =>  the wedge is better tolerated on NR4A3 than on NR4A1  =>  DISCRIMINATION in the designed
               direction (the T407 hydroxyl accepts the pyridyl nitrogen; NR4A1's Leu363 cannot).
    S ~ 0  =>  the marginal wedge is absent. Preregistered as the LIKELY outcome, and NOT a stop: it means the
               claim rests on the categorical axis alone, which LANE 13 has since tested against paralogue
               dynamics and found intact.
    S > 0  =>  the wedge is ANTI-selective — worse on NR4A3 than on the paralogue.

ERROR BARS
----------
`replicate_sd` over independent seeds is the repo's standard and is used whenever >= 2 seeds are present.
MBAR SE is reported alongside but never substituted for it: RUNG 2b's own reduction returned INDETERMINATE at
n = 1 for exactly this reason, and a double difference of two single-seed legs has no error bar at all.
"""
import argparse
import glob
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
MORPH = "5aks_d0_to_d"
NUMERATOR, DENOMINATOR = "NR4A3", "NR4A1"      # S = <NUMERATOR> - <DENOMINATOR>


def leg_id(species):
    return f"{MORPH}__ternary_{species.lower()}"


def load_legs(leg_dir):
    """Every `leg_5aks_*.json` in `leg_dir`, keyed by (leg_id, seed). Fabricates nothing."""
    out = {}
    for path in sorted(glob.glob(os.path.join(leg_dir, "leg_*.json"))):
        try:
            with open(path) as fh:
                d = json.load(fh)
        except Exception:  # noqa: BLE001
            continue
        if not str(d.get("leg_id", "")).startswith(MORPH):
            continue
        out[(d["leg_id"], d.get("seed", 0))] = d
    return out


def refuse_non_ternary(legs):
    """A binary or solvent 5a-KS leg must never enter `S`.

    It is not merely redundant — see the module docstring. Subtracting it from both arms adds noise for no
    information; subtracting it from one arm silently produces a number that is not `S` at all, and nothing
    downstream could tell. Both are easy mistakes for anyone 'completing the cycle', so this refuses rather
    than warns.
    """
    bad = [lid for (lid, _s) in legs if "__ternary_" not in lid]
    return bad


def identity_problems(legs):
    """Cross-leg comparability, the check `protocol_hash` cannot make.

    `S` is a difference of legs, so it is meaningless if they describe different systems. RUNG 2b's 4 fs cycle
    reached a verdict with every one of these fields UNRECORDED and the reduction correctly reporting UNKNOWN
    rather than agreement — so absent provenance is reported here as a PROBLEM, never folded in as a match.
    """
    problems = []
    for field in ("protocol_hash", "charge_method", "setup_cache_version", "n_particles", "n_windows"):
        seen, unrecorded = {}, []
        for (lid, seed), d in sorted(legs.items()):
            v = d.get(field)
            if v is None:
                unrecorded.append(f"{lid}:r{seed}")
            else:
                seen.setdefault(str(v), []).append(f"{lid}:r{seed}")
        if unrecorded:
            problems.append({"field": field, "kind": "UNRECORDED", "legs": unrecorded,
                             "why": "absent provenance is not agreement"})
        if len(seen) > 1:
            problems.append({"field": field, "kind": "DISAGREES", "values": seen,
                             "why": "the legs do not describe the same system/protocol"})
    return problems


def _mean_sd(xs):
    if not xs:
        return None, None
    m = sum(xs) / len(xs)
    if len(xs) < 2:
        return m, None
    var = sum((x - m) ** 2 for x in xs) / (len(xs) - 1)
    return m, math.sqrt(var)


def reduce_S(legs):
    """The double difference, with its error bar and its refusals. Pure — no I/O."""
    bad = refuse_non_ternary(legs)
    if bad:
        return {"decision": "REFUSED",
                "reason": f"non-ternary 5a-KS leg(s) present: {sorted(set(bad))}. The binary and solvent legs "
                          "cancel ALGEBRAICALLY in S; including one adds noise at best and computes a "
                          "different quantity at worst.",
                "legs_seen": sorted({lid for lid, _ in legs})}

    per_species = {}
    for sp in (NUMERATOR, DENOMINATOR):
        want = leg_id(sp)
        dgs = [d["dg_morph_kcal"] for (lid, _s), d in sorted(legs.items())
               if lid == want and d.get("dg_morph_kcal") is not None]
        ses = [d.get("mbar_se_kcal") for (lid, _s), d in sorted(legs.items())
               if lid == want and d.get("mbar_se_kcal") is not None]
        mean, sd = _mean_sd(dgs)
        per_species[sp] = {"leg_id": want, "n_seeds": len(dgs), "dg_morph_kcal": dgs,
                           "mean_dg_morph_kcal": mean, "replicate_sd_kcal": sd,
                           "mean_mbar_se_kcal": (sum(ses) / len(ses)) if ses else None}

    missing = [sp for sp in (NUMERATOR, DENOMINATOR) if per_species[sp]["n_seeds"] == 0]
    if missing:
        return {"decision": "INCOMPLETE", "reason": f"no completed leg for {missing}",
                "per_species": per_species}

    s_val = per_species[NUMERATOR]["mean_dg_morph_kcal"] - per_species[DENOMINATOR]["mean_dg_morph_kcal"]
    sds = [per_species[sp]["replicate_sd_kcal"] for sp in (NUMERATOR, DENOMINATOR)]
    if all(x is not None for x in sds):
        s_err, err_kind = math.sqrt(sds[0] ** 2 + sds[1] ** 2), "replicate_sd"
    else:
        ses = [per_species[sp]["mean_mbar_se_kcal"] for sp in (NUMERATOR, DENOMINATOR)]
        s_err = math.sqrt(sum(x ** 2 for x in ses)) if all(x is not None for x in ses) else None
        err_kind = "mbar_se_ONLY — not a replicate SD; the repo's standard needs >= 2 seeds per arm"

    n_min = min(per_species[sp]["n_seeds"] for sp in (NUMERATOR, DENOMINATOR))
    return {
        "decision": "COMPUTED" if n_min >= 2 else "COMPUTED_SINGLE_SEED",
        "S_kcal": round(s_val, 4),
        "S_err_kcal": round(s_err, 4) if s_err is not None else None,
        "S_err_kind": err_kind,
        "definition": "S = dG_tern(NR4A3) - dG_tern(NR4A1); the binary and solvent legs cancel algebraically",
        "sign_reading": ("S < 0 => the wedge is better tolerated on NR4A3 (discrimination in the designed "
                         "direction); S ~ 0 => the marginal wedge is absent, which is the preregistered "
                         "likely outcome and NOT a stop; S > 0 => anti-selective"),
        "per_species": per_species,
        "n_seeds_min": n_min,
        "_single_seed_warning": (None if n_min >= 2 else
                                 "one seed per arm: S has no replicate-SD error bar, and the repo's standard "
                                 "is replicate-SD over MBAR-SE. Treat as a point estimate only."),
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--legs", default=os.environ.get("CKPT_DIR", "."), help="dir holding leg_*.json")
    ap.add_argument("--out", default=os.path.join(HERE, "nr4a3-5aks-reduction.json"))
    args = ap.parse_args(argv)

    legs = load_legs(args.legs)
    print(f"[5aks-reduce] {len(legs)} matching leg record(s) in {args.legs}", flush=True)
    res = reduce_S(legs)
    res["system_identity_problems"] = identity_problems(legs) if legs else [
        {"field": "*", "kind": "NO_LEGS", "why": "nothing to check"}]
    res["_title"] = "RUNG 5a-KS — ligand-side double difference S"
    res["_status"] = ("DESIGN PRIORITISATION. No claim about binding, reactivity, degradation, efficacy or "
                      "safety follows from S.")
    with open(args.out, "w") as fh:
        json.dump(res, fh, indent=1)
        fh.write("\n")
    print(json.dumps({k: res[k] for k in ("decision", "S_kcal", "S_err_kcal", "S_err_kind") if k in res},
                     indent=1), flush=True)
    if res.get("system_identity_problems"):
        print(f"[5aks-reduce] ⚠ {len(res['system_identity_problems'])} identity problem(s) — S is a difference "
              f"of legs and protocol_hash does not cover the system", flush=True)
    print(f"[5aks-reduce] wrote {args.out}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
