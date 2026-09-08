# Lane probe: compares the plotted geometry of HEAD vs modified script. Writes nothing to the repo.
import importlib.util, json, os, itertools
LOCAL="/home/user/Rare-cancers/research/modalities"
def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
def geom(m):
    scan=json.load(open(os.path.join(LOCAL,"emc-surfaceome-scan.json")))
    win=json.load(open(os.path.join(LOCAL,"emc-surface-normal-window.json")))
    act=scan.get("actionable_antigens",{})
    pts=[];ne=[]
    for g in m.SHOW:
        w=win["antigens"].get(g,{})
        if not w or w.get("_status"): continue
        tier=m.WINDOW_TIER.get(w.get("window"),1)
        s=act.get(g,{}); enr=s.get("enrichment_vs_rest")
        if enr is None: ne.append((g,tier)); continue
        pts.append((g,enr,tier,bool(s.get("selectivity_significant"))))
    return pts,ne
head=load("/tmp/claude-0/l1-lane/pre/HEAD_emc_surface_figure.py","head")
new=load("/home/user/Rare-cancers/research/modalities/emc_surface_figure.py","new")
ph,nh=geom(head); pn,nn=geom(new)
print("SHOW identical:", head.SHOW==new.SHOW)
print("LABEL identical:", head.LABEL==new.LABEL)
print("WINDOW_TIER identical:", head.WINDOW_TIER==new.WINDOW_TIER, "TIER_LABEL identical:", head.TIER_LABEL==new.TIER_LABEL)
print("evaluated points (gene, x=enrichment_vs_rest, tier, significant) identical:", ph==pn)
print("NOT EVALUATED band identical:", nh==nn, nh)
for r in pn: print("  point", r)
print("\ndeterministic jitter (decoration only):")
J={g:0.12*(new.SHOW.index(g)%5-2) for g,_,_,_ in pn}
for g,x,t,s in pn: print(f"  {g:9s} tier={t} jitter={J[g]:+.2f} y={t+J[g]:+.2f} x={x}")
print("\nsame-tier marker separation (data coords; xlim span 6.831, ylim span 4.4):")
worst=None
for a,b in itertools.combinations(pn,2):
    if a[2]!=b[2]: continue
    dx=abs(a[1]-b[1]); dy=abs((a[2]+J[a[0]])-(b[2]+J[b[0]]))
    flag="COLLISION" if (dx<0.25 and dy<0.10) else ""
    if dx<0.6 or dy<0.13: print(f"  {a[0]:9s} vs {b[0]:9s} dx={dx:.3f} dy={dy:.3f} {flag}")
