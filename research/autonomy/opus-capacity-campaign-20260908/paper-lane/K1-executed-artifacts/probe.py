import importlib.util, json, os
spec = importlib.util.spec_from_file_location("emcfig", "/home/user/Rare-cancers/research/modalities/emc_surface_figure.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
LOCAL="/home/user/Rare-cancers/research/modalities"
def _local(url):
    with open(os.path.join(LOCAL, url.rsplit("/",1)[-1])) as f: return json.load(f)
scan=_local("emc-surfaceome-scan.json"); win=_local("emc-surface-normal-window.json")
act=scan.get("actionable_antigens",{})
for g in m.SHOW:
    w=win["antigens"].get(g,{})
    if not w or w.get("_status"): print(g,"SKIPPED",w.get("_status")); continue
    s=act.get(g,{}); enr=s.get("enrichment_vs_rest")
    print(g, "tier=",m.WINDOW_TIER.get(w.get("window"),1), "enr=",enr, "sig=",s.get("selectivity_significant"), "jit=",0.12*(hash(g)%5-2))
