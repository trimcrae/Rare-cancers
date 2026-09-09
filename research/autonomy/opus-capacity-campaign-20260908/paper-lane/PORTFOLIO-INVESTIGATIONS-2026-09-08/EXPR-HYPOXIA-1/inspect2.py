import json,os
REPO="/home/user/Rare-cancers"
d=json.load(open(os.path.join(REPO,"research/modalities/emc-hypoxia-null-background.json")))
print("118 confound genes:", d["_confound_genes_requested_by_name"])
for tk,t in d["targets"].items():
    print("\n=== ",tk)
    print("keys:",sorted(t.keys()))
    for k in sorted(t.keys()):
        v=t[k]
        if isinstance(v,(str,int,float,bool)) or v is None: print("  ",k,"=",repr(v)[:200])
        elif isinstance(v,list): print("  ",k,"list[%d]"%len(v),repr(v[:5])[:200])
        elif isinstance(v,dict):
            ks=list(v.keys()); print("  ",k,"dict[%d]"%len(ks),ks[:8])
    g=t["genes"]
    if isinstance(g,dict):
        k0=list(g.keys())[0]; print("  genes[%s] ="%k0, repr(g[k0])[:400])
    bp=t["background_per_sample"]
    if isinstance(bp,dict):
        k0=list(bp.keys())[0]; print("  background_per_sample[%s] ="%k0, repr(bp[k0])[:400])
