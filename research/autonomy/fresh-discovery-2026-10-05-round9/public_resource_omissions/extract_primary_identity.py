"""Compact original table metadata; no new biological outcome selection."""
from pathlib import Path
import hashlib
import json
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent
LOCK = {
    "PMC10453223.xml": "55765fdeaf04db37a02f5f485d75b96160e9acb86d71389e54ac4f32ca3b03d9",
    "PMC13179970.xml": "52225232d84d2a7e58a3ab93d864edbb4156aaa184e3d2fcb9aeb70ee8a24b97",
    "PMC12055966.xml": "0a3dd313a209c4907788564a48348cc3695c3593e0f9fe9f74599d4ea0d048a1",
}

def clean(element):
    return " ".join("".join(element.itertext()).split())

def main():
    tables = {}
    for filename, digest in LOCK.items():
        path = HERE / "source-cache" / filename
        assert hashlib.sha256(path.read_bytes()).hexdigest() == digest
        root = ET.parse(path).getroot()
        first = root.find(".//table-wrap")
        rows = []
        for row in first.findall(".//tr"):
            rows.append([clean(cell) for cell in row if cell.tag in ("td", "th")])
        tables[filename] = {"source_sha256": digest, "first_table_rows": rows}
    pilot = tables["PMC10453223.xml"]["first_table_rows"]
    cases = [r for r in pilot if r and r[0].startswith("SARC-")]
    assert len(cases) == 18
    emc = [r for r in cases if any("Extraskeletal myxoid chondrosarcoma" in v for v in r)]
    assert len(emc) == 1 and emc[0][0] == "SARC-05"
    record = {
        "source_tables": tables,
        "nanoDx2023": {
            "all_published_tumor_rows": cases,
            "author_labelled_EMC_rows": emc,
            "eligibility": "SARC-05 author-pathology EMC; molecular authentication and patient-level quantitative regional methylation source unresolved. Published classifier result is prior art.",
            "no_inference": "Classifier score and global coverage do not provide locus-level, allele-specific or IG-DMR measurements; reference.h5 reasonable-request is not public patient data.",
        },
        "clinical_classifier2026": {
            "source_scope": "40 samples from34 patients, 450K assayed. Table1 complete source-reported aggregate histopathology: US21(NOS11+UPS10), MFS11, PLS3, LMS2, MLS2, AS1.",
            "conditions": "24post-neoadjuvant-RT/16not;27fresh-frozen/13FFPE;16core-needle/24resection samples. Individual repeated-donor and final-molecular crosswalk not released in inspected main.",
            "eligibility": "No explicit EMC label in full published Table1. Generic NOS11 identity remains pending, not authenticated EMC exclusion. UPS10 and other named labels retain source-level limits. No 40-independent-donor or no-EMC-global claim.",
            "public_measurement": "IDAT files being deposited in GEO; no accession in inspected data availability statement. No new methylation values read.",
        },
        "ORIEN2025": {
            "source_scope": "1340tumor observations from1232patients,974RNA overall; primary1058/metastatic282.12generic MyxoidChondrosarcoma observations at cohort level.",
            "eligibility": "Source does not explicitly call the12 extraskeletal EMC in inspected main; no NR4A3 literal in main. Individual pathology/molecular/RNA availability/donor/condition linkage pending. No subtype transfer from generic label or numeric codes.",
            "public_supplement_scope": "Workbook descriptions identify4 aggregate mutation/differential-expression result sheets, not individual RNA/case identity; no expression values inspected.",
        },
        "interpretation": "These are source-reported published table observations, not newly discovered biology or an independent methylation classifier reanalysis. Full table metadata preserves unfavorable and inconclusive eligibility.",
    }
    (HERE / "PRIMARY-IDENTITY-OBSERVATIONS.json").write_text(json.dumps(record, indent=2) + "\n")
    print("Source hashes verified;18 original nanoDx tumor rows retained;40-sample classifier and1340-tumor ORIEN roster scope preserved.")

if __name__ == "__main__":
    main()
