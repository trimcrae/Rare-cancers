#!/usr/bin/env python3
"""Characterise the disagreements the sweep found. Read-only over this lane's own artifact."""
import json, os, collections
A = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                 "cutoff-sweep-closure.json")
d = json.load(open(A))
print("gate A passed:", d["gate_a_modelled_baseline"]["passed"],
      d["gate_a_modelled_baseline"]["n_reproduced"], "/", d["gate_a_modelled_baseline"]["n_quantities_checked"])
print("gate B passed:", d["gate_b_primary_cutoff_tally"]["passed"],
      d["gate_b_primary_cutoff_tally"]["observed"])
print()
for k in ("2.0","2.6","3.0","3.4"):
    s = d["open_closed_set_vs_committed_per_cutoff"][k]
    n = s["n_cell_frame_open_closed_differences"]
    print("cutoff %s A: %d cell-frame open/closed differences vs the committed modelled competitor" % (k, n))
    byframe = collections.Counter(x["frame"] for x in s["differences"])
    bycell = collections.Counter(x["cell"] for x in s["differences"])
    direction = collections.Counter(
        ("experimental CLOSES a cell the model opens" if x["committed_open"] and not x["experimental_open"]
         else "experimental OPENS a cell the model closes") for x in s["differences"])
    if n:
        print("   frames:", dict(byframe))
        print("   cells :", dict(bycell))
        print("   direction:", dict(direction))
print()
print("=== per-cutoff tallies ===")
for k in ("2.0","2.6","3.0","3.4"):
    t = d["tally_per_cutoff"][k]
    print(k, "A  committed:", json.dumps(t["committed_modelled_tally"], sort_keys=True),
          " n_open(committed):", t["n_open_committed"],
          " exp n_open range:", t["experimental_n_open_range"],
          " identical-set-in-every-frame:", t["open_closed_set_identical_to_committed_in_every_frame"])
    print("     per-frame n_open:", {l: v["n_open"] for l, v in t["per_experimental_frame"].items()})
    print("     per-frame C534-closer count:",
          {l: v["tally"].get("NR4A2 C534", 0) for l, v in t["per_experimental_frame"].items()})
print()
print("=== cells whose OPEN/CLOSED decision flips along the cutoff axis ===")
for cell, fl in d["flips"]["cells_with_an_open_closed_flip"]:
    print(" ", cell, "committed flips at", fl["committed_open_closed_flips_at"],
          "| experimental(any-frame) flips at", fl["experimental_open_in_any_frame_flips_at"])
print()
print("n cells whose closer identity changes along the cutoff axis:",
      d["flips"]["n_cells_whose_closer_identity_changes_along_the_cutoff_axis"])
# monotonicity check on the committed target/closure counts
print()
print("=== is the open-cell count monotone in the cutoff? ===")
print([d["tally_per_cutoff"][k]["n_open_committed"] for k in ("2.0","2.6","3.0","3.4")])
