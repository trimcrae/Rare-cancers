"""For the four affected documents: sentences covered BEFORE (from the HEAD clone) and not now."""
import json,os,sys
sys.path.insert(0, os.path.join(os.getcwd(),"research","manuscripts"))
import claim_coverage as cc
prev=json.load(open(sys.argv[1]))   # {doc: {sentence: [witnesses]}} captured at HEAD
out={}
for key,sents in prev.items():
    rows={r["sentence"]: r for r in cc.census(key)}
    lost=[]
    for s,ws in sents.items():
        r=rows.get(s)
        if r is None:
            lost.append({"sentence":s[:240],"was_read_by":ws,"now":"SENTENCE NOT FOUND (document edited since)"})
        elif not r["covered"]:
            lost.append({"sentence":s[:240],"was_read_by":ws,"has_number":r["has_number"],"now":"UNCOVERED"})
    if lost: out[key]=lost
print(json.dumps(out,indent=1))
