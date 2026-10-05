#!/usr/bin/env python3
"""Verify immutable source bindings and compact identity/assay records only."""
import hashlib
import json
from pathlib import Path
import sys
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parent
errors = []
bindings = json.loads((ROOT / "SOURCE-BINDINGS.json").read_text())["inputs"]
for item in bindings:
    p = Path(item["path"])
    if not p.is_file():
        errors.append("cache unavailable: " + str(p))
        continue
    data = p.read_bytes()
    if len(data) != item["bytes"] or hashlib.sha256(data).hexdigest() != item["sha256"]:
        errors.append("source changed: " + str(p))
roster = json.loads((ROOT / "IDENTITY-ONLY-OBSERVATIONS-CORRECTED.json").read_text())
groups = roster["all_displayed_sample_labels_by_coarse_histology"]
labels = [s for rows in groups.values() for s in rows]
assert len(labels) == len(set(labels)) == 45
assert {k: len(v) for k, v in groups.items()} == {"DDLPS":14,"WDLPS":7,"LMS":6,"SFT":4,"GIST":2,"Others":12}
assert "hSC09" in groups["WDLPS"] and "hSC09" not in groups["DDLPS"]
assert len(roster["Others_unresolved"]) == 10
assert set(roster["Others_unresolved"] + roster["Others_resolved_non_EMC"]) == set(groups["Others"])
assert roster["endpoint_fields_inspected"] is False
xml = next(Path(x["path"]) for x in bindings if x["path"].endswith("/qpop2025.xml"))
source = ET.parse(xml).getroot()
sections = {s.attrib.get("id"): s for s in source.iter("sec")}
schema = " ".join(" ".join(p.itertext()) for sid in ["Sec12","Sec13","Sec14","Sec15","Sec16"] for p in sections[sid].findall("p"))
for text in ["technical duplicates", "technical quadruplicates", "CellTiter-Glo", "48", "155", "third passage"]:
    assert text in schema
pages = next(Path(x["path"]) for x in bindings if x["path"].endswith("qpop2025-supp-text.txt"))
page_texts = [p for p in pages.read_text().split("\f") if p.strip()]
assert len(page_texts) == 8
assert all(s in page_texts[7] for s in ["LPS141","FU-DDLS-1","MLS402","T778"])
record = {"source_bindings_checked":len(bindings),"errors":errors,"sample_labels":45,"coarse_Others":12,"explicit_later_non_EMC":2,"unresolved_Others":10,"nonempty_supplement_pages":8,"raw_response_or_rank_or_protein_values_used":False,"scope":"Source bytes, procedure schema and compact identity record assertions only; manual masked-image observations are not automatically reclassified by this script."}
(ROOT / "VALIDATION.json").write_text(json.dumps(record, indent=2)+"\n")
print(json.dumps(record))
sys.exit(bool(errors))
