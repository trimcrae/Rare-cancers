import json,os,sys
sys.path.insert(0, os.path.join(os.getcwd(),"research","manuscripts"))
import claim_coverage as cc, claim_ablation as ca
key="research/manuscripts/endpoint/response-endpoint-indolent-tumours.md"
needles=["whether its 282 patients overlap","placed 100 patients on active surveillance",
         "A pooled analysis of three prospective observational"]
rows=cc.census(key)
out=[]
for r in rows:
    if any(n in r["sentence"] for n in needles):
        v=ca.ablate(key,r)
        out.append({"sentence":r["sentence"][:150],"covered":r["covered"],"read_by":r["read_by"],
                    "status":v["status"],"red":v["red"],"quantity_kind":v.get("quantity_kind"),
                    "reason":v.get("reason",""),"cached":v.get("cached",False),
                    "baseline":v.get("baseline")})
print(json.dumps(out,indent=1,default=str))
