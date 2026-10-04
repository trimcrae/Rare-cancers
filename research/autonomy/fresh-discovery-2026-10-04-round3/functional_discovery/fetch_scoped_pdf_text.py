"""Retrieve public PDFs in memory, preserve SHA256 and complete page text.

No original large PDF is retained. panPDO uses the public Europe PMC supplement
archive; NCC is the public 2015 institutional annual report. Transfer limits are
distinct from retained-payload budget. Existing PDFs/text are not silently replaced.
"""
import argparse
import hashlib
import io
import json
from pathlib import Path
import shutil
import urllib.request
import zipfile
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parent
parser = argparse.ArgumentParser()
parser.add_argument("source", choices=["panPDO", "NCC"])
args = parser.parse_args()
assert shutil.disk_usage(ROOT).free >= 10 * 1024**3
if args.source == "panPDO":
    url = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC13308604/supplementaryFiles"
    cap = 30_000_000
    name = "panPDO2026-supp"
else:
    url = "https://www.ncc.go.jp/jp/ri/jimu/040/nenpou_No30_2015_02.pdf"
    cap = 45_000_000
    name = "ncc2015"
receipt = {"url": url, "retention": "page text only; original PDF and archive remain in memory"}
try:
    with urllib.request.urlopen(url, timeout=45) as response:
        raw = response.read(cap + 1)
    assert len(raw) <= cap, "Transfer exceeds bounded limit"
    receipt.update(transfer_bytes=len(raw), transfer_sha256=hashlib.sha256(raw).hexdigest())
    if args.source == "panPDO":
        archive = zipfile.ZipFile(io.BytesIO(raw))
        matches = [n for n in archive.namelist() if n.endswith("sciadv.adz3351_sm.pdf")]
        assert len(matches) == 1
        receipt["member"] = matches[0]
        raw = archive.read(matches[0])
    receipt.update(pdf_bytes=len(raw), pdf_sha256=hashlib.sha256(raw).hexdigest())
    pages = [{"page1": i+1, "text": page.extract_text()} for i, page in enumerate(PdfReader(io.BytesIO(raw)).pages)]
    payload = json.dumps(pages, indent=2, ensure_ascii=False)
    assert len(payload.encode("utf8")) < 3_000_000
    destination = ROOT / f"{name}-pages.json"
    if destination.exists():
        receipt["existing_destination_unchanged"] = True
    else:
        destination.write_text(payload, encoding="utf8")
    receipt.update(pages=len(pages), retained_text_sha256=hashlib.sha256(destination.read_bytes()).hexdigest())
except Exception as exc:
    receipt["error"] = str(exc)
(ROOT / f"{name}-script-receipt.json").write_text(json.dumps(receipt, indent=2), encoding="utf8")
print(json.dumps(receipt))
