"""Zero-copy source/diagnostic metadata checks; never reads expression rows."""
from pathlib import Path
from io import BytesIO
import hashlib
import json
import re
import zipfile
import openpyxl

HERE = Path(__file__).resolve().parent

def digest(data):
    return hashlib.sha256(data).hexdigest()

def main():
    archive = HERE / "source-cache/ORIEN-supplementaryFiles.zip"
    assert digest(archive.read_bytes()) == "8091d6338d1173db6548eb5e9bc8c2f863379f494976e3e74c2e859e3a6e3749"
    with zipfile.ZipFile(archive) as source:
        raw = source.read("41467_2025_58678_MOESM5_ESM.xlsx")
        assert len(raw) == 49904690
        assert digest(raw) == "74c613a83117169606ccc77f93ceb5e59e3ce718223368fbbabb75776ff0c549"
        assert hashlib.md5(raw).hexdigest() == "06a6ba5264a6cf503332ffb06c2b3fa5"
        workbook = openpyxl.load_workbook(BytesIO(raw), read_only=True, data_only=True)
        expected = json.loads((HERE / "ORIEN-SHEET-HEADERS.json").read_text())
        assert len(expected) == len(workbook.sheetnames) == 4
        for sheet, header in zip(workbook, expected):
            assert sheet.title == header["sheet"]
            actual = list(next(sheet.iter_rows(min_row=1, max_row=1, values_only=True)))
            assert actual == header["first_row"]
        pdf = source.read("41467_2025_58678_MOESM1_ESM.pdf")
        assert digest(pdf) == "b364e8259fe73c5eec9ff58c765c07c6d09dcbd8a8752776af9f1ad80995d4db"
    extracted = HERE / "source-cache/ORIEN-supplement-info.txt"
    assert digest(extracted.read_bytes()) == "da81e974afcf246b1366c817713626c471f6916fe59a9bf7f6fd932bf3eae578"
    text = extracted.read_text()
    status = json.loads((HERE / "ORIEN-IDENTITY-STATUS.json").read_text())
    for table, fields in [(1, [10, 10, 8, 2, 3, 7, 0, 0]), (2, [9, 9, 7, 2, 3, 6, 0])]:
        begin = text.rfind(f"Supplementary Table {table}:")
        end = text.rfind(f"Supplementary Table {table+1}:")
        line = next(line for line in text[begin:end].splitlines() if line.startswith("Myxoid Chondrosarcoma"))
        tokens = line[len("Myxoid Chondrosarcoma"):].split()
        assert [int(value) for value in tokens[:len(fields)]] == fields
    start = text.rfind("Supplementary Table 3:")
    rows = []
    for line in text[start:].splitlines():
        match = re.search(r"\b([A-Z0-9]{10})\b\s+([A-Za-z0-9]+--[A-Za-z0-9]+).*?\b(Primary|Metastatic)\b\s+(.+)$", line)
        if match:
            rows.append({"original_diagnosis": line[:match.start()].strip(),
                         "source_avatar_key": match.group(1),
                         "diagnostic_fusion_label": match.group(2),
                         "sample_site": match.group(3),
                         "revised_histology": match.group(4).strip()})
    assert len(rows) == 14
    assert rows == status["all_14_published_diagnostic_reclassifications"]
    assert all("NR4A3" not in row["diagnostic_fusion_label"] for row in rows)
    print("Verified archive/workbook/PDF/text hashes, four metadata headers, both generic cohort condition rows and all fourteen diagnostic reclassifications. No expression values examined.")

if __name__ == "__main__":
    main()
