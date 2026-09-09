import json, sys
A=json.load(open(sys.argv[1])); B=json.load(open(sys.argv[2]))
sa,sb=A["sufficiency"],B["sufficiency"]
print("committed sufficiency:", json.dumps(sa, indent=None))
print("patched   sufficiency:", json.dumps(sb, indent=None))
keys=set(sa)|set(sb)
print("\nfield-by-field:")
for k in sorted(keys):
    same = sa.get(k,"<missing>")==sb.get(k,"<missing>")
    print("  %-52s %s   %r -> %r" % (k, "SAME" if same else "CHANGED", sa.get(k,"<missing>"), sb.get(k,"<missing>")))
def ids(d): return {k:v["ids"] for k,v in d["strata"].items()}
print("\nstrata ids identical:", ids(A)==ids(B))
print("all_records id count:", len(A["strata"]["all_records"]["ids"]), len(B["strata"]["all_records"]["ids"]))
print("all 40 ids identical :", A["strata"]["all_records"]["ids"]==B["strata"]["all_records"]["ids"])
for k in ("benchmark_eligible_detail","distinct_fusions_in_benchmark","per_allele_depth","quantitative_observations","_id","_derived_from"):
    print("%-32s identical: %s" % (k, A[k]==B[k]))
top=set(A)|set(B); print("top-level keys identical:", set(A)==set(B))
# exhaustive: every path except sufficiency.n_required["0.9"]
def flat(o,p=""):
    if isinstance(o,dict):
        for k,v in o.items(): yield from flat(v,p+"/"+str(k))
    elif isinstance(o,list):
        for i,v in enumerate(o): yield from flat(v,p+"/%d"%i)
    else: yield p,o
fa=dict(flat(A)); fb=dict(flat(B))
diffs=[k for k in set(fa)|set(fb) if fa.get(k,"<m>")!=fb.get(k,"<m>")]
print("\nEXHAUSTIVE leaf-value diff paths:", diffs)
print("leaf count:", len(fa), len(fb))
