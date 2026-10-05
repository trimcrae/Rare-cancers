from pathlib import Path
import json,hashlib
p=Path(__file__).resolve().parent
checks=[]
for r in json.loads((p/"PRIOR-SOURCE-BINDINGS.json").read_text())["bindings"]:
 checks.append(hashlib.sha256(Path(r["path"]).read_bytes()).hexdigest()==r["sha256"])
b=json.loads((p/"ALL23-BIOSAMPLE-BRIDGE-AUDIT.json").read_text());s=json.loads((p/"SRA-OUTWARD-LINK-AUDIT.json").read_text());checks.extend([len(b["rows"])==23,s["source_packages"]==23,set(b["attribute_schema_counts"])=={"isolate","age","biomaterial_provider","sex","tissue"},len(s["unique_outward_links"])==2])
for r in json.loads((p/"FINAL-SOURCE-AND-VALUE-REVIEW.json").read_text())["owner_exact_bindings"]:
 checks.append(hashlib.sha256(Path(r["path"]).read_bytes()).hexdigest()==r["sha256"])
assert all(checks),checks
print(json.dumps({"checks":len(checks),"all_pass":True,"new_requests":0,"new_raw_bytes":0,"new_RNA_outcomes":False}))
