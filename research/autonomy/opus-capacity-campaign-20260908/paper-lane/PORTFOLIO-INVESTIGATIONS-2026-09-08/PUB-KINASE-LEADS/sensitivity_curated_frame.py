#!/usr/bin/env python3
"""Sensitivity: the same concordance statistic on a SECOND, deliberately biased frame.

The primary null (two_platform_concordance_null.py) uses the 431 genes drawn into BOTH
random background samples. This script repeats it on the intersection of the two
`placed_wanted_genes` sets -- i.e. this repository's CURATED panel genes, which are
enriched for genes somebody already believed were interesting. If the headline
"direction agreement is uninformative" result held only on the random frame it would be
a sampling artefact; if it holds on both, it is a property of the two series.
Reads only; prints, writes nothing.
"""
import json, os
REPO = "/home/user/Rare-cancers"
d = json.load(open(os.path.join(REPO, "research/modalities/emc-expression-panels.json")))
P1 = "GSE24369_series_matrix.txt.gz"; P2 = "GSE4303-GPL3290_series_matrix.txt.gz"
a = d["platforms"][P1]["genome_wide_null"]["placed_wanted_genes"]
b = d["platforms"][P2]["genome_wide_null"]["placed_wanted_genes"]
shared = sorted(set(a) & set(b))
rows = [(s, a[s]["t"], b[s]["t"]) for s in shared]
conc = [r for r in rows if (r[1] > 0) == (r[2] > 0)]
print("curated frame n =", len(rows), "concordant =", len(conc),
      "frac = %.4f" % (len(conc) / len(rows)))
mins = sorted(min(abs(r[1]), abs(r[2])) for r in conc)
def q(p): return round(mins[min(len(mins)-1, int(p*len(mins)))], 3)
print("min|t| among concordant curated genes: p50=%s p75=%s p90=%s p95=%s p99=%s max=%s"
      % (q(.5), q(.75), q(.9), q(.95), q(.99), round(mins[-1], 3)))
for g in ["RET", "NDRG1", "GFRA2", "NR4A3", "EGFR"]:
    if g in a and g in b:
        m = min(abs(a[g]["t"]), abs(b[g]["t"]))
        k = sum(1 for x in mins if x >= m)
        print("%-6s min|t|=%.3f  curated-frame joint p=%.4f" % (g, m, k/len(rows)))
