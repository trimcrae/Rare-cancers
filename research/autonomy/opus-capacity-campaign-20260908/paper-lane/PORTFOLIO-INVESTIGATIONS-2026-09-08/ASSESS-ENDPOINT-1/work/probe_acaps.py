import json
E="/home/user/Rare-cancers/research/manuscripts/endpoint/"
c=json.load(open(E+"endpoint-corpus.json"))
prov=c["C5_retrieval_provenance"]
print("C5 top-level sections:", list(prov.keys()))
print()
print("ACCRUAL provenance:", json.dumps(prov.get("accrual"), indent=1)[:3000])
print()
for k,v in prov.items():
    if k not in ("arms","accrual"): print("OTHER", k, json.dumps(v)[:600])
print()
print("### does 2027 / 16035 appear in endpoint-corpus.json or -inputs.json?")
for f in ("endpoint-corpus.json","endpoint-corpus-inputs.json"):
    s=open(E+f).read()
    print(f, "2027:", s.count("2027"), " 16035:", s.count("16035"))
    import re
    for pat in ("2027","16035"):
        for m in re.finditer(r'.{140}'+pat+r'.{140}', s):
            print("   ", pat, "::", m.group(0).replace("\n"," ")[:290]); break
