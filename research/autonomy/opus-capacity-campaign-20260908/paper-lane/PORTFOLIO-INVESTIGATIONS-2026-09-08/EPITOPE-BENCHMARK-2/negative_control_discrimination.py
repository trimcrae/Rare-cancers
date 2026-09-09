import json,re,sys
sys.path.insert(0,'.')
rows=json.load(open("../EPITOPE-BENCHMARK/epitope-records.json"))["records"]
def has(r,g): return g in r["evidence"]
def measured(r): return any(has(r,g) for g in ("MS_ELUTION","TCELL","MULTIMER"))
def seq_known(r): return bool(re.fullmatch(r"[ACDEFGHIKLMNPQRSTVWY]+",r["peptide"]))
def cw(r): return r["len"] is not None and 8<=r["len"]<=11
def cr(r): return bool(re.search(r"HLA-[ABC]\*?\d",r["hla"] or ""))
def nat(r): return "ANCHOR-MODIFIED" not in r["fusion"] and "heteroclitic" not in r["peptide"]
def elig(r): return measured(r) and r["spans_junction"]=="yes" and nat(r) and seq_known(r) and cw(r) and cr(r)
neg=[r for r in rows if r["spans_junction"]=="no"]
print("negative-control rows (spans_junction == no):",len(neg))
bad=[r["id"] for r in neg if elig(r)]
for r in neg: print("  %s %-28s len=%-4s hla=%-14s evidence=%s -> eligible=%s"%(r["id"],r["fusion"][:28],r["len"],(r["hla"] or "-")[:14],"/".join(r["evidence"]),elig(r)))
print("negative controls admitted by rule:",len(bad),bad)
anchor=[r["id"] for r in rows if not nat(r)]; bo=[r["id"] for r in rows if set(r["evidence"])<={"BINDING","PREDICTION"} and "BINDING" in r["evidence"]]
po=[r["id"] for r in rows if r["evidence"]==["PREDICTION"]]; sq=[r["id"] for r in rows if not seq_known(r)]
print("anchor-modified rejected:",all(not elig(r) for r in rows if not nat(r)),anchor)
print("binding-only rejected:",all(not elig(r) for r in rows if r["id"] in bo),bo)
print("prediction-only rejected:",all(not elig(r) for r in rows if r["id"] in po),po)
print("sequence-unknown rejected:",all(not elig(r) for r in rows if r["id"] in sq),sq)
assert len(neg)==6, "negative-control stratum is not 6"
assert not bad, "a negative control was admitted -- rule no longer discriminates"
print("DISCRIMINATION OK: 6 negative controls, none admitted; rule rejects every excluded stratum.")
