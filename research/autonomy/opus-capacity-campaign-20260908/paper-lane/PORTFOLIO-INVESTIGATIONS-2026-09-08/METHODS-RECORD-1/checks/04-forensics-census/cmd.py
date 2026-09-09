import json,hashlib
b=open("research/modalities/nrv04-result-forensics.json",'rb').read()
print("sha256",hashlib.sha256(b).hexdigest(),"bytes",len(b))
d=json.loads(b)
def flat(o,p=""):
    if isinstance(o,dict):
        for k,v in o.items(): yield from flat(v,p+"."+k)
    elif isinstance(o,list):
        for i,v in enumerate(o): yield from flat(v,p+"[%d]"%i)
    else: yield p,o
tot=0
for k,v in flat(d):
    if "leg_result" in k or "trajectory_objects_found" in k or "prefix" in k.lower() or ("by_class" in k and k.endswith(".n")):
        print(k,"=",repr(v)[:160])
