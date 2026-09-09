import json, os
d = json.load(open(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))), "cutoff-sweep-closure.json")))
want = {"vhl|M3@term_a_exemplar|dab_branch", "vhl|M4@term_a_exemplar|dab_branch",
        "vhl|M3@term_a_exemplar|dap_branch", "vhl|M14@term_a_exemplar|aryl_direct"}
for c in d["per_cell"]:
    lab = "%s|%s" % (c["placement"], c["pendant"])
    if lab not in want:
        continue
    print("==", lab)
    for k in ("2.0", "2.6", "3.0", "3.4"):
        b = c["by_cutoff"][k]
        cm = b["committed_modelled"]
        ex = b["experimental"]
        print("  %s A target_atoms=%s | committed closed_by=%s width=%s | exp closers=%s widths=%s c534=%s"
              % (k, b["target_atoms"], cm["closed_by"], cm["width"],
                 ex["closers_seen"], ex["widths_seen"],
                 [ex["nr4a2_c534_atoms"]["min"], ex["nr4a2_c534_atoms"]["max"]]))
print()
print("artifact size bytes:", os.path.getsize(os.path.join(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))), "cutoff-sweep-closure.json")))
print("invariant violations per frame:",
      {k: len(v["invariant_violations"]) for k, v in d["frames"].items()})
