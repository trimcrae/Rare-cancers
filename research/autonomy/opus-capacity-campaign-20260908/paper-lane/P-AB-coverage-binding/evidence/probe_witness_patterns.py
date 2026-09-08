"""Which harvested literals of a given test module are credited, and to which sentences."""
import os, sys, re, json
sys.path.insert(0, os.path.join(os.getcwd(), "research", "manuscripts"))
import claim_coverage as cc
key = sys.argv[1]; modname = sys.argv[2]
path = cc.PAPERS[key]; base = os.path.basename(path); sents = cc.sentences(path)
for h, p, w in cc._test_patterns(base):
    if w != "test:" + modname:
        continue
    if not cc.is_selective(p, sents):
        continue
    rx = re.compile(p, re.I)
    hits = [s for s in sents if rx.search(s)]
    print(json.dumps({"pattern": p, "n_hits": len(hits), "hits": [s[:180] for s in hits]}, indent=1))
