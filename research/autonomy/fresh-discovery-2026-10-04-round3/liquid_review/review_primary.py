"""Independent read-only extraction of liquid-biomarker primary observations.

No pooled sensitivity, biological inference or reclassification is computed.
The source worker owns the source files; this script writes only its own review.
"""
from pathlib import Path
import hashlib
import json
import re
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parent
SOURCE = Path("C:/Users/mcrae/.codex/worktrees/emc-fresh-20261004-microenvironment/research/autonomy/fresh-discovery-2026-10-04-round3/liquid_biomarker")
FILES = ["eastley2018.xml", "localized2020.xml", "structural2020.xml", "heinhuis2020.xml"]
out = []
terms = re.compile(r"extraskeletal|extra-skeletal|ExMC|Soft Tissue Chondrosarcoma|VWDE|MEAF6", re.I)
for name in FILES:
    path = SOURCE/name
    tree = ET.parse(path)
    record = {"path": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "rows": []}
    for table in tree.iter("table-wrap"):
        for row in table.iter("tr"):
            cells = [" ".join("".join(c.itertext()).split()) for c in row if c.tag in ["th", "td"]]
            if terms.search(" ".join(cells)):
                record["rows"].append({"table_id": table.get("id"), "cells": cells})
    out.append(record)

ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
for name in ["supp-Supplementary Methods and Tables IJMS final revision.docx", "supp-Supplementary figures IJMS final revision.docx"]:
    path = SOURCE/name
    xml = ET.fromstring(zipfile.ZipFile(path).read("word/document.xml"))
    rows = []
    for table in xml.findall(".//w:tbl", ns):
        for row in table.findall("w:tr", ns):
            cells = [" ".join(t.text or "" for t in cell.findall(".//w:t", ns)) for cell in row.findall("w:tc", ns)]
            if terms.search(" ".join(cells)):
                rows.append(cells)
    paragraphs = ["".join(t.text or "" for t in p.findall(".//w:t", ns)) for p in xml.findall(".//w:p", ns)]
    out.append({"path": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "rows": rows,
                "assay_or_control_paragraphs": [p for p in paragraphs if any(t in p.lower() for t in ["ddpcr", "figure s 5", "figure s 6", "sensitivity", "control", "template dna"])],
                "note": "VWDE-specific detection-limit estimate/dilution series not found in supplied methods or figure captions. Positive-control examples are patients6/22, not patient3."})
(ROOT/"independent-primary-extraction.json").write_text(json.dumps(out, indent=2), encoding="utf8")
print(json.dumps({"sources": len(out), "matched_rows": sum(len(r['rows']) for r in out)}))
