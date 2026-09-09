import json,hashlib,os
def sha(p):
    b=open(p,'rb').read(); return hashlib.sha256(b).hexdigest(), len(b), json.loads(b)
def flat(o,p=""):
    if isinstance(o,dict):
        for k,v in o.items(): yield from flat(v,p+"."+k)
    elif isinstance(o,list):
        for i,v in enumerate(o): yield from flat(v,p+"[%d]"%i)
    else: yield p,o
targets={
 "research/modalities/antitarget-selfcontrol.json":["recover","panel_readable","n_"],
 "research/modalities/r3-generation-frame-harmonized.json":["verdict","0.259","dstar","score"],
 "research/modalities/nr4a3-5bt-gate.json":["verdict","sentence","arm"],
 "research/modalities/nr4a3-5bt-signature.json":["sentence_replicated","model","contact"],
 "research/modalities/r5-cross-method-cavity-attribution.json":["cavity","grade","separation","9.85"],
 "research/modalities/pose-second-method.json":["status","R2b","404","align","pair"],
}
for p,keys in targets.items():
    if not os.path.exists(p):
        print("MISSING",p); continue
    h,n,d=sha(p); print("=== %s sha=%s bytes=%d"%(p,h,n))
    for k,v in flat(d):
        s=repr(v)
        if any(t.lower() in (k+s).lower() for t in keys):
            print("  ",k,"=",s[:170])
# decoy
dp="results/nr4a3-decoy/-mmgbsa/nr4a3-mmgbsa.json"
print("=== decoy path exists:",os.path.exists(dp))
if os.path.exists(dp):
    h,n,d=sha(dp); print(h,n)
