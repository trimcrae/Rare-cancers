import json, collections
d=json.load(open("/home/user/Rare-cancers/research/autonomy/opus-capacity-campaign-20260908/paper-lane/PORTFOLIO-INVESTIGATIONS-2026-09-08/ASSESS-ENDPOINT-1/work/claim-rederivation-ledger.json"))
rows=d["rows"]
c=collections.Counter((r["verdict"], r["derivation_level"]) for r in rows)
for k,v in sorted(c.items()): print(k, v)
print()
print("ledger summary block:", d["summary"])
print("REPRODUCES + RECOMPUTED =", c[("REPRODUCES","RECOMPUTED")], " <- ENDPOINT-1/FINDING.md states 72")
print("REPRODUCES + READ-BACK  =", c[("REPRODUCES","READ-BACK")])
print("total rows =", len(rows))
