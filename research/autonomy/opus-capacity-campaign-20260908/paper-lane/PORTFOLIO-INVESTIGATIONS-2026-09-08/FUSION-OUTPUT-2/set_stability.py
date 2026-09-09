#!/usr/bin/env python3
"""Cross-window stability of the two pre-registered sets. Membership only; no expression
value is read. Establishes, before the fact, that the three windows do NOT define the same
set, so one window must be pre-declared primary and the others reported as different sets."""
import itertools, json, sys
S = json.load(open(sys.argv[1]))
W = ["1000", "2000", "5000"]
out = {"status": "DESIGN ONLY", "input_sha256": S["input"]["sha256"], "sets": {}, "jaccard": {},
       "intersection_across_all_windows": {}}
for c in ("A", "B"):
    sets = {w: set(S["windows"][w][f"contrast_{c}_set"]["genes"]) for w in W}
    out["sets"][c] = {w: sorted(sets[w]) for w in W}
    out["jaccard"][c] = {f"{x}_vs_{y}": round(len(sets[x] & sets[y]) / len(sets[x] | sets[y]), 4)
                         for x, y in itertools.combinations(W, 2)}
    inter = set.intersection(*sets.values())
    out["intersection_across_all_windows"][c] = {"n": len(inter), "genes": sorted(inter),
                                                 "clears_4_gene_floor": len(inter) >= 4}
json.dump(out, sys.stdout, indent=1, sort_keys=True); print()
