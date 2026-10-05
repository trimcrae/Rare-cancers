#!/usr/bin/env python3
"""Replay source-identity and pre-overlay scope checks; never open array values."""
from pathlib import Path
import hashlib
import json
import shutil
import xml.etree.ElementTree as ET

GATE = Path(__file__).resolve().parent
ROOT = GATE.parent


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run():
    evidence = json.loads((GATE / "PRIMARY-DEFINITION-EVIDENCE.json").read_text())
    checked = []
    for source in evidence["sources"]:
        item = source["binding"]
        path = ROOT / item["path"]
        assert path.stat().st_size == item["bytes"]
        assert digest(path) == item["sha256"]
        checked.append(item)
        if source.get("quoted_fragment"):
            tree = ET.parse(path)
            text = " ".join("".join(tree.getroot().itertext()).split())
            assert source["quoted_fragment"] in text
    original = json.loads((ROOT / "COVERAGE.json").read_text())
    coverage = json.loads((GATE / "COVERAGE.json").read_text())
    assert digest(ROOT / "COVERAGE.json") == coverage["reused_complete_inventory"]["sha256"]
    for key, localkey in [("all_GSE140686_EMC", "all_GSE140686_EMC"),
                          ("all_fixed_primary_FFPE_control_inventory", "all_fixed_primary_FFPE_controls")]:
        old = {r["ID"]: r for r in original[key]}
        new = {r["ID"]: r for r in coverage[localkey]}
        assert old.keys() == new.keys()
        for identifier in old:
            for field in ["GSM", "diagnosis", "material", "manifestation", "platform", "IDAT", "slide", "supplier", "batch"]:
                assert old[identifier].get(field) == new[identifier].get(field)
    assert len(coverage["all_GSE140686_EMC"]) == 10
    assert len(coverage["all_fixed_primary_FFPE_controls"]) == 62
    assert original["Case21"] == coverage["Case21"]
    assert original["validation54"] == coverage["validation54"]
    region = json.loads((GATE / "REGION-FROZEN.json").read_text())
    assert region["plan_sha256"] == digest(GATE / "PLAN.json")
    for field in ["chosen_region", "assembly", "source_boundaries", "probe_count_whole_region"]:
        assert region[field] is None
    assert not region["fresh_probe_overlay_performed"]
    assert not region["beta_or_EMC_phenotype_values_inspected"]
    rawbytes = sum(p.stat().st_size for p in (ROOT / "sources").rglob("*") if p.is_file())
    free = shutil.disk_usage(ROOT).free
    assert rawbytes < 64 * 1024 * 1024
    assert free >= 10 * 1024**3
    return {"status": "PASS", "checked_source_bindings": checked,
            "all_reference_EMC": 10, "all_fixed_FFPE_controls": 62,
            "metadata_field_checks": 648, "Case21_and_SEF_dispositions": "unchanged",
            "fresh_array_overlay": False, "beta_values_opened": False,
            "retained_raw_bytes": rawbytes, "free_bytes": free,
            "scope": "Source identity, two short primary assay-definition fragments, full frozen metadata correspondence and no-region/no-overlay contract; not whole-region absence or biological discovery."}


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
