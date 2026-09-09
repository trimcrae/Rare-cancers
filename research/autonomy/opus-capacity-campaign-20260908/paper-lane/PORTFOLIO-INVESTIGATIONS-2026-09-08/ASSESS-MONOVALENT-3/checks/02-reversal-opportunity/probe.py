"""Is 'all 24 disagreements go the same way' informative, or partly structural?

Under an NR4A2-only substitution the window is [target, min(all competitors)-1].
A cell can only OPEN if its committed blocker is an NR4A2 cysteine (an NR4A1/NR4A3 blocker,
or an unreachable target, is untouched by this substitution -> opening is IMPOSSIBLE by
construction). A cell can CLOSE whenever any NR4A2 competitor comes in nearer.
So: count the opportunities on each side, per cutoff, and measure whether the experimental
NR4A2 reach is systematically nearer than the modelled one (the collapsed-apo bias the lane
itself names as limitation 1). Read-only on MONOVALENT-3's artifact."""
import json, statistics
A = ("/home/user/Rare-cancers/research/autonomy/opus-capacity-campaign-20260908/paper-lane/"
     "PORTFOLIO-INVESTIGATIONS-2026-09-08/MONOVALENT-3/cutoff-sweep-closure.json")
d = json.load(open(A))
cells = d["per_cell"]
cuts = ["%.1f" % c for c in d["_cutoffs_A"]]
NF = 10
print("cell-frame decisions per cutoff: %d cells x %d frames = %d\n" % (len(cells), NF, len(cells)*NF))
tot_close_opp = tot_open_opp = 0
for k in cuts:
    n_open = n_closed = 0
    closed_by_nr4a2 = closed_by_other = closed_by_none = 0
    for c in cells:
        cm = c["by_cutoff"][k]["committed_modelled"]
        if cm["open"]:
            n_open += 1
        else:
            n_closed += 1
            cb = cm["closed_by"]
            if cb is None: closed_by_none += 1
            elif cb.startswith("NR4A2"): closed_by_nr4a2 += 1
            else: closed_by_other += 1
    close_opp = n_open * NF
    open_opp = closed_by_nr4a2 * NF
    tot_close_opp += close_opp; tot_open_opp += open_opp
    diffs = d["open_closed_set_vs_committed_per_cutoff"][k]["n_cell_frame_open_closed_differences"]
    print("%s A: committed open %2d / closed %2d  (closed by NR4A2 %2d, by NR4A1/NR4A3 %2d, target-unreachable %2d)"
          % (k, n_open, n_closed, closed_by_nr4a2, closed_by_other, closed_by_none))
    print("        cell-frame chances to CLOSE an open cell : %3d   observed closings: %d" % (close_opp, diffs))
    print("        cell-frame chances to OPEN a closed cell : %3d   observed openings: 0" % open_opp)
print("\nTOTAL over the grid: closing opportunities %d, opening opportunities %d"
      % (tot_close_opp, tot_open_opp))
print("If opening opportunities were 0, 'never the reverse' would be a tautology.\n")

# how far from opening are the NR4A2-blocked closed cells?  width-to-open margin proxy:
# committed width 0 with an NR4A2 blocker; report widths seen experimentally there.
print("Closed-cell behaviour where opening IS structurally possible (NR4A2 blocker):")
n = 0
for c in cells:
    for k in cuts:
        b = c["by_cutoff"][k]
        cm = b["committed_modelled"]
        if cm["open"] or (cm["closed_by"] or "").startswith("NR4A2") is False:
            continue
        ws = b["experimental"]["widths_seen"]
        n += 1
        if n <= 12:
            print("  %-46s %s A  committed w=%d blocker=%s at %s | exp widths %s"
                  % (c["placement"]+"|"+c["pendant"], k, cm["width"], cm["closed_by"],
                     cm["closed_at_atoms"], ws))
print("  ... %d such cell-cutoff situations in total\n" % n)

# systematic direction of the experimental NR4A2 reach vs modelled (C534, the reported competitor)
print("Experimental minus committed NR4A2 C534 corridor atoms (negative = experimental reaches NEARER):")
for k in cuts:
    ds = []
    for c in cells:
        b = c["by_cutoff"][k]
        cm = b["committed_modelled"]["nr4a2_c534_atoms"]
        if cm is None: continue
        for lab, v in b["experimental"]["by_frame"].items():
            if v["nr4a2_c534_atoms"] is not None:
                ds.append(v["nr4a2_c534_atoms"] - cm)
    if ds:
        neg = sum(1 for x in ds if x < 0); pos = sum(1 for x in ds if x > 0)
        print("  %s A: n=%4d  mean %+.2f  median %+.1f  nearer(neg) %d  farther(pos) %d  equal %d"
              % (k, len(ds), statistics.mean(ds), statistics.median(ds), neg, pos, len(ds)-neg-pos))
