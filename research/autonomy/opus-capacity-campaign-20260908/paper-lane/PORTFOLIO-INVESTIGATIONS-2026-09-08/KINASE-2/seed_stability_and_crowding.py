#!/usr/bin/env python3
"""Two robustness checks on the KINASE-2 label-permutation null.

1. SEED STABILITY. The prereg fixed seed 20260909 / 2000 permutations. If the permuted
   concordance rate moved with the seed, the headline gap would be a sampling accident.
   Re-runs the primary frame under four further seeds and 500-permutation runs.

2. CROWDING. A small joint p under the LABEL-permutation null only says "a real
   EMC-vs-comparator contrast exists here". The question a lead gene has to answer is
   "does this gene stand out among genes". This prints, for each lead, how many genes on
   the array are expected to be at least as concordant and at least as strong -- the
   gene-resampling rate scaled to each platform's own frame size.

Reads only; prints; writes nothing.
"""
import json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import label_permutation_null as M

d = json.load(open(M.SRC))
prim = sorted(set(d["background_reads"][M.P1]["z"]) & set(d["background_reads"][M.P2]["z"]))

print("== 1. seed stability, primary frame, 500 permutations each ==")
M.N_PERM = 500
for s in (20260909, 1, 42, 987654321, 20260908):
    rep, _, _ = M.frame_report("primary", d, prim, "background", np.random.default_rng(s))
    l = rep["label_permutation_null"]; g = rep["gene_resampling_null"]
    print("  seed %-10d permuted concordance mean %.4f sd %.4f max %.4f | observed %.4f | p %s"
          % (s, l["concordance_rate_mean"], l["concordance_rate_sd"],
             l["concordance_rate_max_over_permutations"], g["concordance_rate"],
             l["p_observed_concordance_vs_permutation"]))

print("\n== 2. crowding: how many genes are as concordant and as strong as each lead ==")
gw1 = d["platforms"][M.P1]["genome_wide_null"]; gw2 = d["platforms"][M.P2]["genome_wide_null"]
print("  genome_wide_null keys:", sorted(k for k in gw1 if not k.startswith("placed")))
frame1 = gw1["n_symbols_scored"]
frame2 = gw2["n_symbols_scored"]
print("  per-platform scored frame sizes:", frame1, frame2)
art = json.load(open(M.OUT))
smaller = min(frame1, frame2)
for g, rec in sorted(art["leads"].items(),
                     key=lambda kv: (kv[1].get("placement_primary_frame") or
                                     {"joint_p_gene_resampling": 9})["joint_p_gene_resampling"]):
    p = rec.get("placement_primary_frame")
    if not p:
        print("  %-7s not readable on both platforms" % g); continue
    print("  %-7s joint p(gene-resampling) %.4f -> approx %5d of the %d genes readable on the "
          "smaller platform are at least this concordant and this strong"
          % (g, p["joint_p_gene_resampling"],
             round(p["joint_p_gene_resampling"] * smaller), smaller))
