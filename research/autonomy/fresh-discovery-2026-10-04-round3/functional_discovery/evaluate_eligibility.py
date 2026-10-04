"""Evaluate source eligibility without using drug-response values to select a hypothesis.

Inputs are retained original XML/HTML and page-wise pypdf text from the original
pan-PDO supplementary PDF. The 220-row completeness assertion checks extraction.
This establishes source eligibility, not an EMC drug-response finding.
"""
from pathlib import Path
import collections
import hashlib
import json
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def write(name, value):
    (ROOT / name).write_text(json.dumps(value, indent=2, ensure_ascii=False), encoding="utf8")

pages = json.loads((ROOT / "panPDO2026-supp-pages.json").read_text(encoding="utf8"))
pattern = re.compile(r"(?:HCM-WCMC-\s*\d+-C\d+(?:-[A-Z])?|ICSBCS\d+|WCM\d+(?:_[A-Za-z0-9]+)?)")
records = []
for page in pages:
    if not 20 <= page["page1"] <= 35:
        continue
    matches = list(pattern.finditer(page["text"]))
    for i, match in enumerate(matches):
        text = page["text"][match.end():matches[i+1].start() if i+1 < len(matches) else None]
        category = re.search(r"\(([A-Z][A-Z0-9]+)\)", text)
        records.append({"source_page1": page["page1"], "id": re.sub(r"\s+", "", match.group()),
                        "oncotree_code": category.group(1) if category else None,
                        "source_row_text": text.strip()})
assert len(records) == 220, f"Expected 220 rows, extracted {len(records)}"
# The source column says Patient ID and contains repeated IDs; those rows must
# not be silently deduplicated or described as independent donors/models.
aliases = re.compile(r"extraskeletal|chondrosarcoma|myxoid|NR4A[23]|EWSR1|\bEMC(?:S)?\b|\bTEC\b|\bCHN\b", re.I)
hits = [r for r in records if aliases.search(r["source_row_text"])]
write("panPDO-all220-identity-rows.json", records)
write("panPDO-identity-evaluation.json", {
    "source": "10.1126/sciadv.adz3351 supplementary Table S3, original PDF pp20-35",
    "pdf_sha256": "8d49fbac00d16daa49302ba4b884ace5201a9597fd1563b0c64e07bc45f6775b",
    "retained_page_text_sha256": sha(ROOT / "panPDO2026-supp-pages.json"),
    "rows": len(records), "unique_source_patient_id_labels": len({r['id'] for r in records}),
    "repeated_source_patient_id_labels": {k:v for k,v in collections.Counter(r['id'] for r in records).items() if v > 1},
    "category_counts": dict(collections.Counter(r['oncotree_code'] for r in records)),
    "alias_hits": hits,
    "missing_code_rows": [r for r in records if r['oncotree_code'] is None],
    "unknown_primary_rows": [r for r in records if 'Unknown' in r['source_row_text'][:120]],
    "scope": "All established PDO rows; counts refer to models, not independent patients. No assay values tested."
})

for source in ["dst2019", "tumoroid2025", "biobank2025"]:
    tree = ET.parse(ROOT / f"{source}.xml")
    tables = []
    for t in tree.iter("table-wrap"):
        tables.append({"id": t.get("id"), "rows": [
            [" ".join("".join(c.itertext()).split()) for c in row if c.tag in ("th", "td")]
            for row in t.iter("tr")]})
    paragraphs = []
    for p in tree.iter("p"):
        txt = " ".join("".join(p.itertext()).split())
        if any(q in txt.lower() for q in ["patients", "fusion", "translocation", "tumoroid models", "histolog"]):
            paragraphs.append(txt)
    write(source + "-identity-evaluation.json", {
        "source_sha256": sha(ROOT/f"{source}.xml"), "tables": tables,
        "identity_paragraphs": paragraphs,
        "alias_hits": [t for t in paragraphs if aliases.search(t)]
    })
print(json.dumps({"panPDO_rows": len(records), "codes": dict(collections.Counter(r['oncotree_code'] for r in records)), "alias_hits": len(hits)}))
