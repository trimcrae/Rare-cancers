"""The sentences that lost their census witness — the honest 'now uncovered' list."""
import json,os,sys
sys.path.insert(0, os.path.join(os.getcwd(),"research","manuscripts"))
import claim_coverage as cc
before=json.load(open(sys.argv[1]))  # BEFORE-sole-witness-breakdown.json
out={}
for key in sorted(before):
    rows=cc.census(key)
    now={r["sentence"] for r in rows if r["covered"]}
    lost=[]
    for w,v in before[key].items():
        pass
    out[key]=None
# recompute directly: run the census now and list uncovered sentences that WERE sole-witnessed
print("use probe_lost2")
