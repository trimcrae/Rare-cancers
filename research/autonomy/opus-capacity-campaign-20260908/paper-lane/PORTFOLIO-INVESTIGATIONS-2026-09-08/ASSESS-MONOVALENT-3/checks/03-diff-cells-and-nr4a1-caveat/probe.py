"""(a) Verify the 24 disagreements, the four cells and the 'committed window is width 1' claim.
   (b) Verify the NR4A1 un-error-barred caveat is carried in the JSON, and check whether it is
       attached to the per-cell / per-tally NR4A1 readings or only at the top level."""
import json, collections
A = ("/home/user/Rare-cancers/research/autonomy/opus-capacity-campaign-20260908/paper-lane/"
     "PORTFOLIO-INVESTIGATIONS-2026-09-08/MONOVALENT-3/cutoff-sweep-closure.json")
d = json.load(open(A))
cuts = ["%.1f" % c for c in d["_cutoffs_A"]]
cmap = {c["placement"]+"|"+c["pendant"]: c for c in d["per_cell"]}

print("== (a) the disagreements ==")
tot = 0; cellset = collections.Counter(); widths = collections.Counter()
for k in cuts:
    blk = d["open_closed_set_vs_committed_per_cutoff"][k]
    n = blk["n_cell_frame_open_closed_differences"]
    listed = blk["differences"]
    tot += n
    print("%s A: %d differences, %d listed in JSON (truncated at 60)" % (k, n, len(listed)))
    for x in listed:
        cellset[(x["cell"], k)] += 1
        cw = cmap[x["cell"]]["by_cutoff"][k]["committed_modelled"]["width"]
        widths[cw] += 1
        assert x["committed_open"] and not x["experimental_open"], x
print("total differences over the grid: %d" % tot)
print("all differences are committed-open -> experimental-closed: True (asserted above)")
print("committed width of the disagreeing cells (count by width):", dict(widths))
print("distinct (cell, cutoff) situations:", len(cellset))
for (cell, k), n in sorted(cellset.items()):
    cm = cmap[cell]["by_cutoff"][k]["committed_modelled"]
    print("   %-46s %s A  committed width=%d closed_by=%s  frames disagreeing=%d/10"
          % (cell, k, cm["width"], cm["closed_by"], n))
print("distinct cells involved:", sorted({c for c, _ in cellset}))

print("\n== (b) NR4A1 caveat in the JSON ==")
print("top-level _nr4a1_caveat present:", "_nr4a1_caveat" in d)
print("_limits mentioning NR4A1:", sum(1 for l in d["_limits"] if "NR4A1" in l))
print("_scope mentions NR4A1 unchanged:", "NR4A1" in d["_scope"])
# per-cell / per-tally NR4A1 readings, and whether any carry their own flag
n_nr4a1_cells = 0; flagged = 0
for c in d["per_cell"]:
    for k in cuts:
        b = c["by_cutoff"][k]
        if (b["committed_modelled"]["closed_by"] or "").startswith("NR4A1"):
            n_nr4a1_cells += 1
            if any("nr4a1" in kk.lower() or "error" in kk.lower() for kk in b["committed_modelled"]):
                flagged += 1
        for lab, v in b["experimental"]["by_frame"].items():
            if (v["closed_by"] or "").startswith("NR4A1"):
                n_nr4a1_cells += 1
                if any("nr4a1" in kk.lower() or "error" in kk.lower() for kk in v):
                    flagged += 1
print("cell-level readings whose closer is an NR4A1 cysteine: %d; of those carrying a local "
      "un-error-barred flag: %d" % (n_nr4a1_cells, flagged))
tal = d["tally_per_cutoff"]
print("tally keys naming NR4A1 per cutoff:",
      {k: {kk: vv for kk, vv in tal[k]["committed_modelled_tally"].items() if "NR4A1" in kk} for k in cuts})
print("any local flag inside tally_per_cutoff:",
      any("nr4a1" in kk.lower() for k in cuts for kk in tal[k]))
# NR4A1 closer classes seen anywhere experimentally
cl = collections.Counter()
for c in d["per_cell"]:
    for k in cuts:
        for lab, v in c["by_cutoff"][k]["experimental"]["by_frame"].items():
            if (v["closed_by"] or "").startswith("NR4A1"):
                cl[(v["closed_by"], k)] += 1
print("experimental NR4A1 closer classes (residue, cutoff) -> cell-frame count:", dict(cl))
