#!/usr/bin/env python3
"""Hash the current NAT upload set and create a portable local handoff ZIP.

This verifies build hashes, not scientific acceptance or permission to submit.
Run only after artifact verification; rerunning refreshes the inventory.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import zipfile

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
SUB = HERE / "submission"
ROLES = {
    "manuscript.docx": "Main manuscript; use unless anonymous review is requested",
    "manuscript-anonymized.docx": "Alternative main manuscript for anonymous review",
    "title-page.docx": "Title page and author declarations",
    "figure-1.eps": "Figure 1; vector artwork",
    "figure-legends.docx": "Figure legends",
    "fusion-junction-aso-sequences.csv": "Supplementary File 1",
    "anonymous/fusion-junction-aso-sequences.csv": "Alternative Supplementary File 1 for anonymous review; identifiers removed from comments only",
    "supplementary-file-2.pdf": "Supplementary File 2",
    "supplementary-file-2-anonymized.pdf": "Alternative Supplementary File 2 for anonymous review",
    "cover-letter.md": "Cover letter body for portal text; omit repository front matter",
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_hashes():
    checked = 0
    stamps = [
        (SUB / "word-build-stamp.json", "sources", REPO),
        (SUB / "revision-note-build-stamp.json", "files", HERE),
        (HERE / "data-build-stamp.json", "files", REPO),
        (HERE / "candidate.build-stamp.json", "built_from", REPO / "research/manuscripts"),
    ]
    for file, field, base in stamps:
        for name, expected in json.loads(file.read_text(encoding="utf-8"))[field].items():
            if sha(base / name) != expected:
                raise ValueError(f"Stale build input: {name}")
            checked += 1
    word = json.loads((SUB / "word-build-stamp.json").read_text(encoding="utf-8"))
    for name, result in word["outputs"].items():
        assert sha(SUB / name) == result["sha256"], name
        assert result["complete_body_text_matches"], name
        checked += 1
    assert (SUB / "fusion-junction-aso-sequences.csv").read_bytes() == (HERE / "fusion-junction-aso-sequences.csv").read_bytes()
    assert sha(SUB / "figure-1.eps") == sha(REPO / "research/manuscripts/figures/submission/aso-multipartner-seam.eps")
    return checked + 2


def anonymous_csv():
    source = (SUB / "fusion-junction-aso-sequences.csv").read_text(encoding="utf-8")
    text, n = re.subn(r"(?m)^#   Author:.*?^#   DOI above\.$",
                      "# Author and archive identifiers are omitted for anonymous review.\n"
                      "# The unblinded submission identifies the historical archive and correction.",
                      source, count=1, flags=re.S)
    assert n == 1
    assert [x for x in source.splitlines() if not x.startswith("#")] == [x for x in text.splitlines() if not x.startswith("#")]
    assert not re.search(r"tristan|mcrae|orcid|qeios|zenodo|gmail", text, re.I)
    target = SUB / "anonymous/fusion-junction-aso-sequences.csv"
    target.parent.mkdir(exist_ok=True)
    target.write_text(text, encoding="utf-8", newline="\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--zip", type=Path, help="Optional output ZIP outside this source bundle")
    args = parser.parse_args()
    anonymous_csv()
    checks = check_hashes()
    files = [{"path": (SUB / name).relative_to(REPO).as_posix(), "sha256": sha(SUB / name),
              "bytes": (SUB / name).stat().st_size, "upload_role": role} for name, role in ROLES.items()]
    record = {"schema": "pub-aso-nat-upload-inventory/2", "path_basis": "repository root",
              "hash_algorithm": "SHA256 over raw file bytes", "resource": "paper:PUB-ASO",
              "status": "Prepared upload set; final status and checks are in verification.json",
              "manuscript_sha256": sha(HERE / "manuscript.md"), "build_hash_checks": checks,
              "files": files, "variant_rule": "Use one main manuscript and one Supplementary File 2 variant, according to the portal review mode.",
              "publication_authority": "No journal submission has been made or authorized by this inventory."}
    (SUB / "upload-manifest.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8", newline="\n")
    if args.zip:
        if args.zip.resolve().is_relative_to(HERE):
            raise ValueError("ZIP must be outside source bundle to avoid recursive inclusion")
        selected = [p for p in HERE.rglob("*") if p.is_file() and "__pycache__" not in p.parts]
        # Preserve the exact repository layout needed to reproduce the explanatory correction.
        selected += [REPO / "research/manuscripts/aso" / n for n in
                     ("fusion-junction-aso-sequences.csv", "fusion-junction-aso-journal-tables.md")]
        args.zip.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(args.zip, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
            for path in sorted(selected):
                info = zipfile.ZipInfo(path.relative_to(REPO).as_posix(), (2026, 9, 4, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                z.writestr(info, path.read_bytes())
        with zipfile.ZipFile(args.zip) as z:
            assert z.testzip() is None
            for path in selected:
                assert z.read(path.relative_to(REPO).as_posix()) == path.read_bytes()
        print(json.dumps({"zip": str(args.zip), "sha256": sha(args.zip), "files": len(selected)}))
    print(json.dumps({"upload_files": len(files), "build_hash_checks": checks}))


if __name__ == "__main__":
    main()
