"""Byte-for-value comparison of the reproduced census against the committed one."""
import json, os, sys
REPO="/home/user/Rare-cancers"
A=json.load(open(os.path.join(REPO,"research/modalities/km-risk-row-detection.json")))
B=json.load(open("census-reproduced-2026-09-09.json"))
diffs=[]
def walk(p,a,b):
    if type(a)!=type(b):
        diffs.append({"path":p,"committed":a,"reproduced":b,"kind":"type"}); return
    if isinstance(a,dict):
        for k in sorted(set(a)|set(b)):
            if k in ("cache_branch","cache_path","cache_commit","page_rasters","_generated_by"):
                continue
            if k not in a or k not in b:
                diffs.append({"path":f"{p}.{k}","committed":a.get(k,"<absent>"),"reproduced":b.get(k,"<absent>"),"kind":"key"})
            else: walk(f"{p}.{k}",a[k],b[k])
    elif isinstance(a,list):
        if len(a)!=len(b):
            diffs.append({"path":p,"committed":f"len {len(a)}","reproduced":f"len {len(b)}","kind":"length"}); return
        for i,(x,y) in enumerate(zip(a,b)): walk(f"{p}[{i}]",x,y)
    else:
        if a!=b: diffs.append({"path":p,"committed":a,"reproduced":b,"kind":"value"})
for key in ("sources","_totals","control","method"):
    walk(key,A.get(key),B.get(key))
verdict_paths=[d for d in diffs if d["path"].endswith("verdict")]
OUT={"_what":"Independent re-execution of km_risk_row_detect.py on the ORIGINAL input PDFs, "
             "recovered from the local git object store, compared field by field with the "
             "committed measurement.",
     "_not_medical_advice":"Nothing here is medical advice and nothing asserts efficacy, safety, "
                           "selectivity or clinical readiness.",
     "committed_totals":A["_totals"],"reproduced_totals":B["_totals"],
     "n_field_differences":len(diffs),
     "n_verdict_differences":len(verdict_paths),
     "verdict_differences":verdict_paths,
     "all_differences":diffs[:200],
     "summary":("THE COMMITTED CENSUS REPRODUCES EXACTLY FROM ITS ORIGINAL INPUTS"
                if not diffs else f"{len(diffs)} field difference(s)")}
json.dump(OUT,sys.stdout,indent=1,ensure_ascii=False); print()
