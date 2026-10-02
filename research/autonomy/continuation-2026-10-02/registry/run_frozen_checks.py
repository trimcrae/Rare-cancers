"""Run pinned conformance checks against existing inputs/ files."""
from pathlib import Path
import json
from registry_literal_extractor import load_verified
from conformance_checks import synthetic_checks, real_checks

manifest = json.loads(Path("sources.json").read_text())
fixtures = json.loads(Path("cases.json").read_text())
completed = set()
assert synthetic_checks() == 7
for source in manifest["sources"]:
    raw = Path("inputs", source["name"]).read_bytes()
    assert len(raw) == source["bytes"]
    document, receipt = load_verified(raw, source["sha256"], source)
    completed.update(real_checks(document, receipt, fixtures))
assert completed == {case["id"] for case in fixtures["cases"]}
print(json.dumps({"syntheticChecks": 7, "frozenCaseIds": sorted(completed)}))
