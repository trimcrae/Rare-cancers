#!/usr/bin/env python3
"""METAD-CONVERGENCE-1: is the pocket-opening free energy resolved beyond replica noise?

Reads the three committed metadynamics analysis packages IN PLACE (no copies), re-hashes
every input at use, computes the within-replica half-block error and the between-replica
spread of the opening free-energy difference, and states a resolution floor.

The between-replica comparison is run BLIND: replica labels are replaced by pseudonyms
under a recorded seeded permutation, every quantity is computed from the pseudonymous set,
and the mapping is applied only after the spread and floor are fixed.

A free-energy difference computed here is a property of a simulation ensemble. It is not
evidence of druggability, selectivity, efficacy or a therapeutic window.
"""
import json, hashlib, random, statistics, sys, os, datetime

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "..", ".."))
REPLICAS = ["r1", "r2", "r3"]
WALL = (0.45, 2.2)          # lower_wall / upper_wall from metad_params
BOUNDARY = 0.9              # boundary_rg_nm from the published recrossing analysis
BLOCKS = ["10.0", "20.0", "30.0", "30.2"]
SEED = 20260908
CEIL_TOL = 1e-6

def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()

def load(r):
    base = os.path.join(ROOT, "results", f"nr4a3-metad-analysis-{r}")
    paths = {k: os.path.join(base, v) for k, v in {
        "fes_blocks": "fes_blocks.json",
        "fes2d_rg_gate": "fes2d_rg_gate.json",
        "metad_analysis_summary": "metad_analysis_summary.json",
        "MANIFEST": "MANIFEST.json"}.items()}
    hashes = {k: {"path": os.path.relpath(v, ROOT), "sha256": sha256(v),
                  "bytes": os.path.getsize(v)} for k, v in paths.items()}
    blocks = json.load(open(paths["fes_blocks"]))
    summ = json.load(open(paths["metad_analysis_summary"]))
    return blocks, summ, hashes

def profile(block):
    """Grid points inside the wall region, with unsampled ceiling points flagged."""
    reg = [(x, f) for x, f in block if WALL[0] <= x <= WALL[1]]
    ceil = max(f for _, f in reg)
    return [(x, f, abs(f - ceil) <= CEIL_TOL * max(1.0, abs(ceil))) for x, f in reg], ceil

def dF_open(block):
    """F(open basin) - F(closed basin), minima taken over SAMPLED grid points only.

    Returns (dF, status). status 'measured' when both sides carry sampled points;
    'open_unsampled' when the open side is entirely at the unsampled ceiling, in which
    case dF is a LOWER BOUND, not an estimate."""
    reg, ceil = profile(block)
    closed = [f for x, f, unsamp in reg if x <= BOUNDARY and not unsamp]
    openn = [f for x, f, unsamp in reg if x > BOUNDARY and not unsamp]
    if not closed:
        return None, "closed_unsampled"
    if not openn:
        openn_all = [f for x, f, _ in reg if x > BOUNDARY]
        return min(openn_all) - min(closed), "open_unsampled"
    return min(openn) - min(closed), "measured"

def sampled_extent(block):
    reg, _ = profile(block)
    xs = [x for x, f, unsamp in reg if not unsamp]
    return [min(xs), max(xs)] if xs else None

# ---------------------------------------------------------------- load + hash
raw = {}
for r in REPLICAS:
    blocks, summ, hashes = load(r)
    raw[r] = {"blocks": blocks, "summary": summ, "inputs": hashes}

# ---------------------------------------------------------------- BLIND
rng = random.Random(SEED)
pseudo = ["A", "B", "C"]
order = REPLICAS[:]
rng.shuffle(order)
mapping = dict(zip(pseudo, order))          # pseudonym -> real, withheld until unblinding
blind = {p: raw[mapping[p]] for p in pseudo}

per = {}
for p in pseudo:
    b = blind[p]["blocks"]
    s = blind[p]["summary"]
    dfs = {}
    for k in BLOCKS:
        v, st = dF_open(b[k])
        dfs[k] = {"dF_kJ_mol": None if v is None else round(v, 3), "status": st,
                  "sampled_rg_extent_nm": sampled_extent(b[k])}
    final = dfs["30.2"]
    half = dfs["20.0"]
    # within-replica half-block error: |dF(first ~2/3 block) - dF(full)|
    if final["dF_kJ_mol"] is None or half["dF_kJ_mol"] is None:
        hb = None
    else:
        hb = round(abs(final["dF_kJ_mol"] - half["dF_kJ_mol"]), 3)
    published = s["convergence"]["final_block_to_block_max_dF_kJ"]
    per[p] = {"per_block": dfs,
              "final_dF_kJ_mol": final["dF_kJ_mol"],
              "final_status": final["status"],
              "within_replica_half_block_error_kJ_mol": hb,
              "published_per_replica_error_kJ_mol": published,
              "half_block_bounds_published": (hb is not None and hb >= published)}

finals = [per[p]["final_dF_kJ_mol"] for p in pseudo]
spread = {
    "values_kJ_mol": finals,
    "mean_kJ_mol": round(statistics.mean(finals), 3),
    "sd_kJ_mol": round(statistics.stdev(finals), 3),
    "range_kJ_mol": round(max(finals) - min(finals), 3),
    "half_range_kJ_mol": round((max(finals) - min(finals)) / 2.0, 3),
}
within_max = max(v for v in (per[p]["within_replica_half_block_error_kJ_mol"] for p in pseudo)
                 if v is not None)
signal = abs(spread["mean_kJ_mol"])
floor = max(spread["range_kJ_mol"], within_max)
resolved = signal > floor

blinded_record = {"pseudonyms": pseudo, "per_pseudonym": per, "between_replica_spread": spread,
                  "max_within_replica_half_block_error_kJ_mol": within_max,
                  "signal_kJ_mol": round(signal, 3),
                  "resolution_floor_kJ_mol": round(floor, 3),
                  "resolved": resolved}

# ---------------------------------------------------------------- UNBLIND
unblinded = {mapping[p]: per[p] for p in pseudo}

checks = [
    {"name": "half_block_error_bounds_published_per_replica_error",
     "statement": "For every replica the within-replica half-block error must be >= the "
                  "published final block-to-block max |dF|; a smaller value would mean the "
                  "published error understates the block-level uncertainty of dF_open.",
     "per_replica": {r: {"half_block_kJ_mol": v["within_replica_half_block_error_kJ_mol"],
                         "published_kJ_mol": v["published_per_replica_error_kJ_mol"],
                         "pass": v["half_block_bounds_published"]}
                     for r, v in unblinded.items()},
     "pass": all(v["half_block_bounds_published"] for v in unblinded.values())},
    {"name": "between_replica_comparison_run_blind",
     "statement": "Replica labels were permuted under a recorded seed before any spread or "
                  "floor was computed; the mapping was applied only afterwards.",
     "seed": SEED, "permutation_pseudonym_to_replica": mapping, "pass": True},
    {"name": "signal_exceeds_resolution_floor",
     "statement": "The mean opening free-energy difference must exceed the resolution floor "
                  "(the larger of the between-replica range and the worst within-replica "
                  "half-block error) for the difference to be resolved beyond replica noise.",
     "signal_kJ_mol": round(signal, 3), "floor_kJ_mol": round(floor, 3), "pass": bool(resolved)},
]

out = {
    "id": "METAD-CONVERGENCE-1",
    "generated_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
    "question": "Is the pocket-opening free energy resolved beyond replica noise across the "
                "three committed NR4A3-LBD metadynamics replicas?",
    "definition": {
        "observable": "dF_open = min F over sampled Rg > 0.9 nm  minus  min F over sampled "
                      "Rg <= 0.9 nm, within the metadynamics wall region [0.45, 2.2] nm.",
        "boundary_rg_nm": BOUNDARY, "wall_region_rg_nm": list(WALL),
        "unsampled_handling": "Grid points sitting at the per-block ceiling value are treated as "
                              "UNSAMPLED and excluded from basin minima. Where the whole open "
                              "side is unsampled, dF_open is a lower bound, flagged as such.",
        "within_replica_error": "|dF_open(20.0 ns block) - dF_open(30.2 ns block)| — the "
                                "half-block estimate.",
        "resolution_floor": "max(between-replica range of dF_open, worst within-replica "
                            "half-block error).",
    },
    "inputs": {r: raw[r]["inputs"] for r in REPLICAS},
    "blinding": {"seed": SEED, "pseudonym_to_replica": mapping,
                 "blinded_record": blinded_record},
    "per_replica": unblinded,
    "between_replica_spread": spread,
    "max_within_replica_half_block_error_kJ_mol": within_max,
    "signal_kJ_mol": round(signal, 3),
    "resolution_floor_kJ_mol": round(floor, 3),
    "resolved_beyond_replica_noise": bool(resolved),
    "checks": checks,
    "scope_limit": "A free-energy difference computed here is a property of this simulation "
                   "ensemble only. It is NOT evidence of druggability, selectivity, efficacy, "
                   "safety or a therapeutic window, and no such claim is made.",
}

dest = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                    "metad-cross-replica-convergence.json")
with open(dest, "w") as f:
    json.dump(out, f, indent=2)
    f.write("\n")

print(json.dumps({"per_replica_final_dF_kJ_mol":
                  {r: v["final_dF_kJ_mol"] for r, v in unblinded.items()},
                  "final_status": {r: v["final_status"] for r, v in unblinded.items()},
                  "sampled_rg_extent_nm":
                  {r: v["per_block"]["30.2"]["sampled_rg_extent_nm"] for r, v in unblinded.items()},
                  "between_replica_spread": spread,
                  "max_within_replica_half_block_error_kJ_mol": within_max,
                  "signal_kJ_mol": round(signal, 3),
                  "resolution_floor_kJ_mol": round(floor, 3),
                  "resolved_beyond_replica_noise": bool(resolved),
                  "checks": [{"name": c["name"], "pass": c["pass"]} for c in checks]},
                 indent=2))
print("wrote", dest)
sys.exit(0)
