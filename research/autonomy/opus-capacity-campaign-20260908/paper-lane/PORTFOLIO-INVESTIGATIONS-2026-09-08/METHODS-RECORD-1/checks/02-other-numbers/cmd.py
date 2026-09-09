import json,hashlib
def L(p):
    b=open(p,'rb').read(); return json.loads(b), hashlib.sha256(b).hexdigest()
def flat(o,p=""):
    if isinstance(o,dict):
        for k,v in o.items():
            yield from flat(v,p+"."+k)
    elif isinstance(o,list):
        for i,v in enumerate(o): yield from flat(v,p+"[%d]"%i)
    else: yield p,o

print("=== 5aKS")
d,h=L("research/modalities/nr4a3-5aks-reduction.json"); print("sha",h)
for k,v in flat(d): print(k,"=",repr(v)[:160])

print("=== valb-failure-propagation (selected)")
d,h=L("research/modalities/valb-failure-propagation.json"); print("sha",h)
for k,v in flat(d):
    s=repr(v)
    if any(t in k.lower() for t in ("sign","error","replicate","power","calib","abs")) or (isinstance(v,(int,float)) and not isinstance(v,bool)):
        print(k,"=",s[:200])

print("=== valb-triangle-reduction (numeric)")
d,h=L("research/modalities/valb-triangle-reduction.json"); print("sha",h)
for k,v in flat(d):
    if isinstance(v,(int,float)) and not isinstance(v,bool): print(k,"=",v)
    elif isinstance(v,str) and ("NONE QUOTED" in v or "R_" in v): print(k,"=",v[:160])
