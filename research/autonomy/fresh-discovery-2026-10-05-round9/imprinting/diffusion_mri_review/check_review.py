#!/usr/bin/env python3
"""Validate public source bindings and blinded row-label identity, not ADC outcomes."""
from pathlib import Path
import hashlib
import json
import re
import shutil
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parent
NS = {"s": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}


def run():
    bindings = json.loads((ROOT / "INPUT-BINDINGS.json").read_text())
    for row in bindings["inputs"]:
        path = Path(row["runtime_path"])
        assert path.stat().st_size == row["bytes"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == row["sha256"]
    schema = json.loads((ROOT / "S1-SCHEMA-IDENTITY-GATE.json").read_text())
    path = ROOT / "raw-cache" / "PMC5510859-S1-primary.xlsx"
    assert hashlib.sha256(path.read_bytes()).hexdigest() == schema["S1_sha256"]
    with zipfile.ZipFile(path) as archive:
        strings = ["".join(x.itertext()) for x in
                   ET.fromstring(archive.read("xl/sharedStrings.xml")).findall("s:si", NS)]
        assert not any(re.search(r"chondrosar|histolog|diagnos|liposar|myxofibro", s, re.I)
                       for s in strings)
        sheet = ET.fromstring(archive.read("xl/worksheets/sheet1.xml"))
        records = []
        for row in sheet.findall("s:sheetData/s:row", NS):
            # Read only string cells in columns A (identifier) and B (binary label).
            cells = {re.sub(r"\d", "", c.get("r", "")): c
                     for c in row.findall("s:c", NS)
                     if re.sub(r"\d", "", c.get("r", "")) in {"A", "B"}}
            def label(column):
                cell = cells.get(column)
                if cell is None or cell.get("t") != "s":
                    return None
                return strings[int(cell.findtext("s:v", "", NS))]
            identifier = label("A")
            if identifier and re.fullmatch(r"A(?:[1-9]|[1-3][0-9]|40)", identifier):
                records.append((identifier, label("B")))
    expected = [(r["id"], r["label"]) for r in schema["all40_identity_rows"]]
    assert records == expected and len(set(i for i, _ in records)) == 40
    assert sum(x == "benign" for _, x in records) == 23
    assert sum(x == "malignant" for _, x in records) == 17
    tree = ET.parse(ROOT / "raw-cache" / "PMC5510859.xml")
    body = " ".join("".join(tree.find("body").itertext()).split())
    assert not re.search(r"(?<![A-Za-z0-9])A(?:[1-9]|[1-3][0-9]|40)(?![0-9A-Za-z])", body)
    assert "extraskeletal myxoid chondrosarcomas (n = 2)" in body
    assert "mean ADC value has limited ability" in body
    original_plan = ROOT / "PLAN.json"
    assert hashlib.sha256(original_plan.read_bytes()).hexdigest() == "f36bad6d30bce24cf73f3bbb8219c2f901e765bf09163e8fc18a2be186aa09b4"
    raw_bytes = sum(p.stat().st_size for p in (ROOT / "raw-cache").rglob("*") if p.is_file())
    free = shutil.disk_usage(ROOT).free
    assert raw_bytes < 64 * 1024**2 and free >= 10 * 1024**3
    return {"status": "PASS", "input_hashes_checked": len(bindings["inputs"]),
            "identity_rows_checked": 40, "binary_label_counts": {"benign": 23, "malignant": 17},
            "EMC_linked_feature_rows": None, "numeric_ADC_or_texture_cells_read": False,
            "case_histology_inferred": False, "original_prevalue_plan_unchanged": True,
            "retained_new_raw_bytes": raw_bytes, "free_bytes": free,
            "scope": "Identity/schema, short prior-art/method facts and raw bindings only; no subtype error rate or diagnostic-performance validation."}


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
