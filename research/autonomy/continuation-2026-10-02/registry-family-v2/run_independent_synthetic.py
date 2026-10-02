"""Execute separately frozen synthetic assertions; no clinical source inputs."""
import argparse, copy, hashlib, importlib.util, json
from pathlib import Path
p=argparse.ArgumentParser()
p.add_argument("--code",type=Path,required=True);p.add_argument("--oracle",type=Path,required=True);p.add_argument("--out",type=Path,required=True)
a=p.parse_args();spec=importlib.util.spec_from_file_location("candidate",a.code);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
oracle=json.loads(a.oracle.read_bytes());checks=[]
for case in oracle["cases"]:
    original=copy.deepcopy(case["outcome"]);arg=copy.deepcopy(original)
    prediction=m.classify_context(arg)
    ok=arg==original and all(prediction.get(k)==v for k,v in case.get("expected",{}).items())
    if case.get("notAssigned"):ok=ok and prediction["status"]!="assigned"
    checks.append({"id":case["id"],"passed":ok,"expected":case.get("expected"),"notAssigned":case.get("notAssigned",False),"prediction":prediction})
result={"scope":"Independent synthetic behavioral cases only; no medical accuracy claim","oracleSHA256":hashlib.sha256(a.oracle.read_bytes()).hexdigest(),"codeSHA256":hashlib.sha256(a.code.read_bytes()).hexdigest(),"passed":sum(x["passed"] for x in checks),"total":len(checks),"checks":checks}
a.out.write_text(json.dumps(result,indent=2)+"\n");print(json.dumps({"passed":result["passed"],"total":result["total"]}))
raise SystemExit(0 if all(x["passed"] for x in checks) else 1)
