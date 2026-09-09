#!/usr/bin/env python3
"""Robustness of the METAD-CONVERGENCE-1 negative to the closed/open boundary.

This is NOT a search for a boundary under which the difference would be resolved: it records
the signal and the resolution floor at every boundary tried, and every one is reported.
Appends 'boundary_sensitivity' to metad-cross-replica-convergence.json.
"""
import json, os, statistics, importlib.util, sys

here = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("cc", os.path.join(here, "cross_replica_convergence.py"))

# re-import the loader pieces without re-running the writer: duplicate the small helpers
ROOT = os.path.abspath(os.path.join(here, "..", "..", "..", "..", "..", ".."))
WALL = (0.45, 2.2); CEIL_TOL = 1e-6
REPLICAS = ["r1", "r2", "r3"]

def prof(block):
    reg = [(x, f) for x, f in block if WALL[0] <= x <= WALL[1]]
    ceil = max(f for _, f in reg)
    return [(x, f, abs(f - ceil) <= CEIL_TOL * max(1.0, abs(ceil))) for x, f in reg]

def dF(block, b):
    reg = prof(block)
    closed = [f for x, f, u in reg if x <= b and not u]
    openn = [f for x, f, u in reg if x > b and not u]
    if not closed or not openn:
        return None
    return min(openn) - min(closed)

blocks = {r: json.load(open(os.path.join(ROOT, "results", f"nr4a3-metad-analysis-{r}", "fes_blocks.json")))
          for r in REPLICAS}

rows = []
for b in [0.80, 0.85, 0.90, 0.95, 1.00, 1.05]:
    finals, halves = [], []
    for r in REPLICAS:
        v = dF(blocks[r]["30.2"], b); h = dF(blocks[r]["20.0"], b)
        if v is None or h is None:
            finals = None; break
        finals.append(v); halves.append(abs(v - h))
    if finals is None:
        rows.append({"boundary_rg_nm": b, "status": "undefined_one_side_unsampled"}); continue
    rng = max(finals) - min(finals)
    floor = max(rng, max(halves))
    sig = abs(statistics.mean(finals))
    rows.append({"boundary_rg_nm": b, "status": "measured",
                 "per_replica_dF_kJ_mol": [round(v, 3) for v in finals],
                 "signal_kJ_mol": round(sig, 3),
                 "between_replica_range_kJ_mol": round(rng, 3),
                 "max_within_replica_half_block_error_kJ_mol": round(max(halves), 3),
                 "resolution_floor_kJ_mol": round(floor, 3),
                 "resolved": bool(sig > floor)})

dest = os.path.join(here, "metad-cross-replica-convergence.json")
art = json.load(open(dest))
art["boundary_sensitivity"] = {
    "purpose": "Confirms the negative is not an artifact of the 0.9 nm closed/open boundary. "
               "Every boundary tried is reported; none is selected as preferred.",
    "rows": rows,
    "resolved_at_any_boundary": any(r.get("resolved") for r in rows)}
with open(dest, "w") as f:
    json.dump(art, f, indent=2); f.write("\n")
print(json.dumps(art["boundary_sensitivity"], indent=2))
sys.exit(0)
