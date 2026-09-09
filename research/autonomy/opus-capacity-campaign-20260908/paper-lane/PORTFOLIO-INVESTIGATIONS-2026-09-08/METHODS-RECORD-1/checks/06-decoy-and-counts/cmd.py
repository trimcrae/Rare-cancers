import json,os,hashlib,glob
def flat(o,p=""):
    if isinstance(o,dict):
        for k,v in o.items(): yield from flat(v,p+"."+k)
    elif isinstance(o,list):
        for i,v in enumerate(o): yield from flat(v,p+"[%d]"%i)
    else: yield p,o
print("== decoy path literal from manuscript:")
for cand in ["results/nr4a3-decoy/-mmgbsa/nr4a3-mmgbsa.json"]:
    print(cand, os.path.exists(cand))
print("glob results/nr4a3-decoy*:", glob.glob("results/nr4a3-decoy*")[:10])
print("glob **nr4a3-mmgbsa.json:", glob.glob("results/**/nr4a3-mmgbsa.json",recursive=True)[:10])
p="research/modalities/decoy-null-provenance.json"
print("== provenance",os.path.exists(p))
if os.path.exists(p):
    b=open(p,'rb').read(); print("sha",hashlib.sha256(b).hexdigest(),len(b))
    for k,v in flat(json.loads(b)):
        s=repr(v)
        if any(t in (k+s).lower() for t in ("22","38","path","reproduc","margin","constant","arm")):
            print("  ",k,"=",s[:180])
print("== antitarget recovery counts")
b=open("research/modalities/antitarget-selfcontrol.json",'rb').read()
d=json.loads(b)
for k,v in flat(d):
    if any(t in k.lower() for t in ("n_pass","n_recover","n_targets","summary")) or (isinstance(v,str) and "7 of 10" in v) or (isinstance(v,str) and "7/10" in v):
        print("  ",k,"=",repr(v)[:180])
print("== cavity attribution counts")
d=json.loads(open("research/modalities/r5-cross-method-cavity-attribution.json",'rb').read())
for k,v in flat(d):
    if any(t in k.lower() for t in ("n_","gradeable","same_cavity","different","separation","summary","verdict")):
        print("  ",k,"=",repr(v)[:180])
