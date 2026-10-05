import json,pathlib,hashlib
p=pathlib.Path(__file__).resolve().parent
b=json.loads((p/"SOURCE-BINDINGS.json").read_text())
checks=[]
for row in b["bindings"]:
 if "sha256" in row:
  q=pathlib.Path(row["path"]);checks.append(hashlib.sha256(q.read_bytes()).hexdigest()==row["sha256"])
a=json.loads((p/"ELIGIBILITY-AND-COVERAGE.json").read_text())
checks.append(a["all_screen_rows"]=={"USZ20-EMC1":40,"NCC-EMC1-C1_screen":221,"NCC-EMC1-C1_selected_IC50":24})
checks.append(a["selected_validation"]["models"]==["USZ20-EMC1","USZ22-EMC2"])
checks.append(json.loads((p/"DECISION.json").read_text())["numerical_stage"] is False)
assert all(checks),checks
print(json.dumps({"checks":len(checks),"all_pass":True,"outcome_fields_inspected":False}))
