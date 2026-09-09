import json, os, sys, numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "EXPR-COMPOSITION"))
import composition_adjusted_contrast as m
d = json.load(open(m.SRC))
bad = 0
for pkey, tag, want in ((m.P1, "GPL6244", 35), (m.P2, "GPL3290", 16)):
    plat = d["platforms"][pkey]
    cols = list(plat["EMC_gsms"]) + list(plat["comparator_gsms"])
    print("%s labelled samples: %d (prereg claims %d)" % (tag, len(cols), want))
    if len(cols) != want: bad += 1
    for sym in m.MARKERS + m.EXCLUDED:
        rec = d["gene_reads"].get(sym, {}).get(pkey)
        if rec is None or not rec.get("readable"):
            print("  MISSING/unreadable:", sym); bad += 1; continue
        per = {r["gsm"]: r.get("z_vs_array") for r in rec["per_sample"]}
        miss = [g for g in cols if per.get(g) is None]
        if miss:
            print("  %s: %d of %d samples lack z_vs_array" % (sym, len(miss), len(cols))); bad += 1
print("markers checked: %d per platform" % len(m.MARKERS + m.EXCLUDED))
print("PREREG SEC.2 PRESENCE CLAIM: %s" % ("HOLDS - all 22 readable with complete per-sample z_vs_array on both platforms" if bad == 0 else "FAILS (%d problems)" % bad))
