"""Audit the remaining load-bearing numbers in MONOVALENT-3's FINDING.md against its own JSON."""
import json, collections
A = ("/home/user/Rare-cancers/research/autonomy/opus-capacity-campaign-20260908/paper-lane/"
     "PORTFOLIO-INVESTIGATIONS-2026-09-08/MONOVALENT-3/cutoff-sweep-closure.json")
d = json.load(open(A)); cuts = ["%.1f" % c for c in d["_cutoffs_A"]]
t = d["tally_per_cutoff"]
print("claim: open-cell count 40,42,37,42 ->", [t[k]["n_open_committed"] for k in cuts])
print("claim: exp open ranges 37-38/41-42/37/42 ->", {k: t[k]["experimental_n_open_range"] for k in cuts})
print("claim: set identical in every frame ->",
      {k: t[k]["open_closed_set_identical_to_committed_in_every_frame"] for k in cuts})
print("claim: committed tally per cutoff ->", {k: t[k]["committed_modelled_tally"] for k in cuts})
print("claim: exp C534 closer-count range 15-36 ->",
      "grid", (min(t[k]["experimental_nr4a2_c534_closer_count_range"][0] for k in cuts),
               max(t[k]["experimental_nr4a2_c534_closer_count_range"][1] for k in cuts)),
      "per cutoff", {k: t[k]["experimental_nr4a2_c534_closer_count_range"] for k in cuts})
f = d["flips"]
print("claim: 7 of 60 cells flip along the cutoff axis ->",
      f["n_cells_whose_open_closed_decision_flips_along_the_cutoff_axis"])
comm_only = [c for c, fl in f["cells_with_an_open_closed_flip"] if fl["committed_open_closed_flips_at"]]
print("   of which the committed model itself flips:", len(comm_only), comm_only)
print("   cells flipping only under experimental geometry:",
      [c for c, fl in f["cells_with_an_open_closed_flip"] if not fl["committed_open_closed_flips_at"]])
# C551
c551 = collections.Counter()
for c in d["per_cell"]:
    for k in cuts:
        for lab, v in c["by_cutoff"][k]["experimental"]["by_frame"].items():
            if v["closed_by"] == "NR4A1 C551":
                c551[(c["placement"]+"|"+c["pendant"], k)] += 1
print("claim: NR4A1 C551 closer in one experimental cell at 3.4 A ->", dict(c551))
# gate/control blocks
print("gate_b:", d["gate_b_primary_cutoff_tally"]["passed"],
      "control field mismatches:", d["control_recomputed_primary_cells_vs_committed"]["n_field_mismatches"],
      "n_cells:", d["control_recomputed_primary_cells_vs_committed"]["n_cells"])
print("invariant violations per frame:",
      {k: v["invariant_violations"] for k, v in d["frames"].items()})
print("alignment identities:", {k: v["alignment_identity"] for k, v in d["frames"].items()})
print("core rmsd range:", min(v["superposition"]["core_rmsd_A"] for v in d["frames"].values()),
      max(v["superposition"]["core_rmsd_A"] for v in d["frames"].values()))
