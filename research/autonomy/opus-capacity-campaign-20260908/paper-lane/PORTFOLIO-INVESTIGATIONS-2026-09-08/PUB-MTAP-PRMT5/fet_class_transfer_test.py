#!/usr/bin/env python3
"""FET-fusion-class transfer test for the PRMT5 reading in EMC.

Prespecified before execution (see FINDING.md). Reads only committed per-sample
z-scores from research/modalities/emc-expression-panels.json. No network, no new data.

Question: the EMC-vs-comparator PRMT5 contrast reported in the manuscript is computed
against an arm that is 17/29 low-grade fibromyxoid sarcoma (LGFMS, FUS::CREB3L2) — itself
a FET-fusion sarcoma. If PRMT5 elevation were a property of FET-fusion-driven
transcription (the transfer premise), LGFMS should read like EMC, not like the arm.
"""
import json, math, sys
from itertools import combinations
from pathlib import Path

REPO = Path(__file__).resolve().parents[6]
SRC = REPO / "research/modalities/emc-expression-panels.json"
SERIES = "GSE24369_series_matrix.txt.gz"          # GPL6244, the powered platform
FET_COMPARATOR = "LGFMS"                          # FUS::CREB3L2
NONFET = ("desmoid_fibromatosis", "fibrosarcoma")
GENES = ["PRMT5", "MAT2A", "WDR77", "MTAP", "CDKN2A", "PRMT1", "CARM1", "PRMT3",
         "NR4A3", "ENO3"]
EXACT_MAX = 300000        # enumerate exactly below this many labelings

def welch_t(a, b):
    na, nb = len(a), len(b)
    if na < 2 or nb < 2: return None
    ma, mb = sum(a)/na, sum(b)/nb
    va = sum((x-ma)**2 for x in a)/(na-1)
    vb = sum((x-mb)**2 for x in b)/(nb-1)
    den = math.sqrt(va/na + vb/nb)
    if den == 0: return None
    return (ma-mb)/den

def exact_p(a, b):
    """Two-sided exact permutation p for the labelling, or None if too large."""
    pool = list(a)+list(b); n, k = len(pool), len(a)
    total = math.comb(n, k)
    if total > EXACT_MAX: return None, total
    obs = abs(welch_t(a, b)); hits = 0
    idx = range(n)
    for c in combinations(idx, k):
        s = set(c)
        t = welch_t([pool[i] for i in c], [pool[i] for i in idx if i not in s])
        if t is not None and abs(t) >= obs - 1e-12: hits += 1
    return hits/total, total

def main():
    panels = json.loads(SRC.read_text())["gene_reads"]
    out = {"_what": "Prespecified FET-fusion-class transfer test of the PRMT5 transcript reading",
           "source_artifact": str(SRC.relative_to(REPO)),
           "series": SERIES, "platform": "GPL6244",
           "fet_comparator": FET_COMPARATOR, "nonfet_comparators": list(NONFET),
           "genes": {}}
    for g in GENES:
        rec = panels.get(g, {}).get(SERIES)
        if not rec or not rec.get("readable"):
            out["genes"][g] = {"readable": False}; continue
        by = {}
        for s in rec["per_sample"]:
            by.setdefault(s["class"], []).append(s["z_vs_array"])
        emc = by.get("EMC", []); fet = by.get(FET_COMPARATOR, [])
        nonfet = [z for c in NONFET for z in by.get(c, [])]
        allcomp = fet + nonfet
        res = {"readable": True,
               "n": {k: len(v) for k, v in sorted(by.items())},
               "mean_z": {k: round(sum(v)/len(v), 4) for k, v in sorted(by.items())}}
        def contrast(name, a, b):
            t = welch_t(a, b)
            p, tot = exact_p(a, b) if t is not None else (None, None)
            res[name] = {"t": None if t is None else round(t, 3),
                         "delta_mean_z": round(sum(a)/len(a)-sum(b)/len(b), 4) if a and b else None,
                         "n_a": len(a), "n_b": len(b),
                         "exact_two_sided_p": None if p is None else round(p, 6),
                         "labelings": tot}
        contrast("emc_vs_all_comparators", emc, allcomp)      # the manuscript's contrast
        contrast("emc_vs_fet_comparator", emc, fet)           # E1
        contrast("fet_comparator_vs_nonfet", fet, nonfet)     # E2
        contrast("emc_vs_nonfet", emc, nonfet)                # E3 leave-FET-out
        out["genes"][g] = res
    print(json.dumps(out, indent=2))

if __name__ == "__main__":
    sys.exit(main())
