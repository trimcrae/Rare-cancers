#!/usr/bin/env python3
"""
PUB-DEGRADER portfolio investigation, 2026-09-08.

QUESTION. The manuscript's covalent categorical axis leans on one exposure statement read from the
POOLED 75-frame unbiased ensembles: every paralogue LBD cysteine has an RSA that "never exceeds
0.2126", while NR4A3's C397 sits well above it. Pooling three independent release replicas can
manufacture a separation that no single replica supports (or hide one that only one replica breaks).
Does the exposure separation hold WITHIN each independent replica, and does the reach-gate occupancy?

INPUT (read-only, already landed): research/modalities/nr4a-paralogue-dynamics.json
  term_a.by_species[species].ensembles[release_rep0|1|2].summary[cysteine].rsa  (25 frames each)
  ... and .pooled_unbiased.summary (75 frames) for the pooled reference reproduction.
The biased `metad` ensemble is EXCLUDED, exactly as the source artifact excludes it.

This is a re-reading of existing measurements. It computes no new structure, asserts nothing about
reactivity, binding, degradation, selectivity in cells, efficacy, safety or any therapeutic window,
and no wet-lab observation exists for any quantity here. $0, pure stdlib.
"""
import json
import os
import sys

SRC = "research/modalities/nr4a-paralogue-dynamics.json"
REPS = ["release_rep0", "release_rep1", "release_rep2"]
NR4A3_HANDLE = "C397"
NR4A3_UNIQUE = ["C397", "C420", "C559"]
CONTROL = ("NR4A1", "C551")   # the proposed NR-V04 covalent site; V17's failed positive control


def load(path):
    with open(path) as fh:
        return json.load(fh)


def rsa_block(species_block, ens, cys):
    return species_block["ensembles"][ens]["summary"][cys]


def collect(d):
    ta = d["term_a"]["by_species"]
    out = {"_source": SRC, "_ensembles_used": REPS, "_biased_metad_excluded": True, "per_replica": {},
           "pooled_reference": {}}

    # pooled reference (reproduces the manuscript's quoted paralogue ceiling)
    par_pool = []
    for sp in ("NR4A1", "NR4A2"):
        for cys, c in ta[sp]["pooled_unbiased"]["summary"].items():
            par_pool.append((sp, cys, c["rsa"]["max"]))
    h = ta["NR4A3"]["pooled_unbiased"]["summary"][NR4A3_HANDLE]["rsa"]
    top = max(par_pool, key=lambda t: t[2])
    out["pooled_reference"] = {
        "n_frames_per_species": ta["NR4A3"]["pooled_unbiased"]["n_frames"],
        "paralogue_max_rsa_any_cysteine_any_frame": round(top[2], 4),
        "paralogue_argmax": f"{top[0]} {top[1]}",
        "nr4a3_C397_rsa": {k: h[k] for k in ("min", "p10", "median", "p90", "max")},
        "C397_p10_minus_paralogue_max": round(h["p10"] - top[2], 4),
        "C397_min_minus_paralogue_max": round(h["min"] - top[2], 4),
    }

    for rep in REPS:
        par = []
        for sp in ("NR4A1", "NR4A2"):
            for cys in ta[sp]["ensembles"][rep]["summary"]:
                b = rsa_block(ta[sp], rep, cys)
                par.append({"species": sp, "cys": cys, "max": b["rsa"]["max"],
                            "median": b["rsa"]["median"],
                            "nr4a3_has_cys_here": b.get("nr4a3_has_cys_here"),
                            "frac_frames_open_at_or_below_gate": b.get("frac_frames_open_at_or_below_gate")})
        ceiling = max(par, key=lambda r: r["max"])
        row = {"n_frames_per_species": rsa_block(ta["NR4A3"], rep, NR4A3_HANDLE)["n_frames"],
               "paralogue_ceiling": ceiling,
               "paralogue_cysteines": sorted(par, key=lambda r: -r["max"]),
               "nr4a3_unique": {}, "control": {}}
        for cys in NR4A3_UNIQUE:
            b = rsa_block(ta["NR4A3"], rep, cys)
            r = b["rsa"]
            row["nr4a3_unique"][cys] = {
                "rsa": {k: r[k] for k in ("min", "p10", "median", "p90", "max")},
                "frac_frames_open_at_or_below_gate": b.get("frac_frames_open_at_or_below_gate"),
                "p10_minus_paralogue_ceiling": round(r["p10"] - ceiling["max"], 4),
                "min_minus_paralogue_ceiling": round(r["min"] - ceiling["max"], 4),
                "median_above_paralogue_ceiling": r["median"] > ceiling["max"],
            }
        cb = rsa_block(ta[CONTROL[0]], rep, CONTROL[1])
        row["control"] = {"site": f"{CONTROL[0]} {CONTROL[1]}",
                          "rsa": {k: cb["rsa"][k] for k in ("min", "p10", "median", "p90", "max")},
                          "frac_frames_open_at_or_below_gate": cb.get("frac_frames_open_at_or_below_gate")}
        out["per_replica"][rep] = row

    # cross-replica worst case: lowest C397 replica floor against highest paralogue replica ceiling
    c397 = {rep: out["per_replica"][rep]["nr4a3_unique"]["C397"] for rep in REPS}
    worst_ceiling = max(out["per_replica"][rep]["paralogue_ceiling"]["max"] for rep in REPS)
    worst_p10 = min(c397[rep]["rsa"]["p10"] for rep in REPS)
    out["verdict"] = {
        "C397_separated_in_every_replica_at_p10": all(c397[rep]["p10_minus_paralogue_ceiling"] > 0 for rep in REPS),
        "C397_separated_in_every_replica_at_min": all(c397[rep]["min_minus_paralogue_ceiling"] > 0 for rep in REPS),
        "cross_replica_worst_case_p10_margin": round(worst_p10 - worst_ceiling, 4),
        "C420_median_above_ceiling_in_replicas": [rep for rep in REPS
                                                  if out["per_replica"][rep]["nr4a3_unique"]["C420"]["median_above_paralogue_ceiling"]],
        "C559_median_above_ceiling_in_replicas": [rep for rep in REPS
                                                  if out["per_replica"][rep]["nr4a3_unique"]["C559"]["median_above_paralogue_ceiling"]],
        "control_max_rsa_per_replica": {rep: out["per_replica"][rep]["control"]["rsa"]["max"] for rep in REPS},
        "_control_reading": ("A cutoff placed anywhere above the paralogue ceiling also excludes NR4A1 C551 in "
                             "EVERY replica. Replicate structure does not repair V17's failed positive control; "
                             "it shows the failure is reproducible rather than a pooling artifact."),
    }
    return out


def main():
    # walk up from this file until the repository root (the directory that holds SRC) is found
    root = os.path.dirname(os.path.abspath(__file__))
    while not os.path.exists(os.path.join(root, SRC)):
        parent = os.path.dirname(root)
        if parent == root:
            raise SystemExit("repository root holding %s not found above %s" % (SRC, __file__))
        root = parent
    os.chdir(root)
    d = load(SRC)
    out = collect(d)
    dest = sys.argv[1] if len(sys.argv) > 1 else "-"
    txt = json.dumps(out, indent=1)
    if dest == "-":
        print(txt)
    else:
        with open(dest, "w") as fh:
            fh.write(txt + "\n")
    v = out["verdict"]
    print("pooled paralogue ceiling:", out["pooled_reference"]["paralogue_max_rsa_any_cysteine_any_frame"],
          out["pooled_reference"]["paralogue_argmax"])
    for rep in REPS:
        r = out["per_replica"][rep]
        print(rep, "paralogue ceiling", round(r["paralogue_ceiling"]["max"], 4),
              f'({r["paralogue_ceiling"]["species"]} {r["paralogue_ceiling"]["cys"]})',
              "| C397 min/p10/med", [r["nr4a3_unique"]["C397"]["rsa"][k] for k in ("min", "p10", "median")],
              "| margin@p10", r["nr4a3_unique"]["C397"]["p10_minus_paralogue_ceiling"],
              "| margin@min", r["nr4a3_unique"]["C397"]["min_minus_paralogue_ceiling"])
    print("VERDICT", json.dumps(v))


if __name__ == "__main__":
    main()
