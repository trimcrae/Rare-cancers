import pathlib,json,hashlib,collections
p=pathlib.Path(__file__).resolve().parent
checks=[]
for r in json.loads((p/"REUSED-INPUT-BINDINGS.json").read_text())["bindings"]:
 checks.append(hashlib.sha256(pathlib.Path(r["path"]).read_bytes()).hexdigest()==r["sha256"])
a=json.loads((p/"AUTHOR-METADATA-ELIGIBILITY.json").read_text())["rows"]
checks.extend([len(a)==13,all(r["Driver"]=="Fusion" for r in a),all(r["Grade"]=="NA" for r in a)])
s=json.loads((p/"HOFVANDER-PRIMARY-ELIGIBILITY.json").read_text())["rows"]
checks.extend([len(s)==13,all(r["Fusiong"]=="Yes" for r in s),all(r["Graded"]=="NA" for r in s),collections.Counter(r["Sex"] for r in s)=={"M":9,"F":2,"NA":2}])
f=json.loads((p/"COMPLETE-FAMILY-SCOPE-AMENDMENT.json").read_text());checks.extend([len(f["primary_family"])==6,len(f["fixed_context_family"])==6,len(set(f["full_family"]))==12])
checks.append(json.loads((p/"DECISION.json").read_text())["numerical_stage"] is False)
assert all(checks),checks
print(json.dumps({"checks":len(checks),"all_pass":True,"new_gene_values":False,"new_raw_bytes":0}))
