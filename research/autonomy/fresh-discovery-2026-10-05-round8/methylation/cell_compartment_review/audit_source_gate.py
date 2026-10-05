#!/usr/bin/env python3
"""Read-only source/condition audit; never load cell matrices or notebook outputs."""
import argparse
import collections
import hashlib
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET
import zipfile


def binding(path, base):
    return {"path": str(path.relative_to(base)), "bytes": path.stat().st_size,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def sheet_rows(path):
    ns = {"x": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    with zipfile.ZipFile(path) as archive:
        strings = []
        if "xl/sharedStrings.xml" in archive.namelist():
            root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
            strings = ["".join(row.itertext()) for row in root.findall("x:si", ns)]
        root = ET.fromstring(archive.read("xl/worksheets/sheet1.xml"))
        rows = []
        for row in root.findall(".//x:row", ns)[2:]:
            values = {}
            for cell in row:
                val = cell.find("x:v", ns)
                value = val.text if val is not None else "".join(cell.itertext())
                if cell.get("t") == "s":
                    value = strings[int(value)]
                values[re.sub(r"\d+", "", cell.get("r"))] = value.strip()
            rows.append({"sample": values["A"], "processing": values["B"],
                         "WGS_assay_label": values["C"], "TCR_assay_label": values["D"],
                         "pre_filter_cells": int(values["F"]),
                         "post_filter_cells": int(values["I"]),
                         "diagnosis_in_table": None})
        return rows


def run(owner, prior):
    cache = owner / ".cache"
    s1 = sheet_rows(cache / "Supplementary-Table-S1.xlsx")
    with zipfile.ZipFile(cache / "supplementaryFiles.zip") as archive:
        original_s1 = archive.read("ccr-23-2976_supplementary_table_s1_suppts1.xlsx")
        assert original_s1 == (cache / "Supplementary-Table-S1.xlsx").read_bytes()
    assert len(s1) == 9
    assert [r["sample"] for r in s1 if "single cell" in r["processing"]] == ["GS001"]
    frozen = [r for r in s1 if "single nuclei" in r["processing"]]
    assert len(frozen) == 8
    assert sum(r["post_filter_cells"] for r in frozen) == 75716
    observations = json.loads((prior / "GSM-ELIGIBILITY-OBSERVATIONS.json").read_text())
    ids = observations["by_series"]["GSE243381"]
    assert len(ids) == len(set(ids)) == 21
    receipts = {row["id"]: row for row in
                json.loads((prior / "GSM-SOURCE-RECEIPTS.json").read_text())}
    original_receipts = []
    libraries = []
    for acc in ids:
        row = observations["libraries"][acc]
        receipt = receipts[acc]
        original = prior / receipt["path"]
        assert hashlib.sha256(original.read_bytes()).hexdigest() == receipt["sha256"]
        assert row["source_sha256"] == receipt["sha256"]
        original_receipts.append({k: receipt[k] for k in ["id", "url", "path", "sha256", "bytes"]})
        assert any("Intimal" in s or "Undifferentiated" in s
                   for s in row["characteristics_ch1"])
        libraries.append({k: row[k] for k in ["accession", "source_sha256", "title",
                          "source_name_ch1", "characteristics_ch1", "library_strategy"]})
    series = []
    child_ids = []
    for name in ["GSE243380-self.txt", "GSE243377-self.txt", "GSE243379-self.txt"]:
        lines = (cache / name).read_text().splitlines()
        kept = [line for line in lines if line.startswith(("^SERIES", "!Series_relation",
                "!Series_sample_id", "!Series_title", "!Series_summary"))]
        assert "!Series_relation = SubSeries of: GSE243381" in kept
        child_ids.extend(line.split(" = ", 1)[1] for line in kept
                         if line.startswith("!Series_sample_id = "))
        series.append({"source": name, "selected_metadata": kept})
    assert len(child_ids) == len(set(child_ids)) == 21
    assert set(child_ids) == set(ids)
    tree = json.loads((cache / "github-tree.json").read_text())
    assert tree["truncated"] is False
    notebook_sources = []
    for name in ["fresh-sarc.ipynb", "quality-table.ipynb"]:
        notebook = json.loads((cache / name).read_text())
        selected = []
        for i, cell in enumerate(notebook["cells"]):
            source = "".join(cell.get("source", []))
            # Static source only; no expression values or saved notebook outputs.
            if any(alias in source for alias in ["gs001_sarc_scseq", "gs002_sarc_scseq"]):
                selected.append({"cell": i, "cell_type": cell["cell_type"], "source": source})
        notebook_sources.append({"source": name, "selected_static_cells": selected})
    alias_result = ET.fromstring((cache / "gds-fresh-labels.xml").read_bytes())
    summaries = json.loads((cache / "gds-fresh-label-summary.json").read_text())["result"]
    alias_hits = [{k: summaries[uid].get(k) for k in
                   ["accession", "title", "summary", "taxon", "entrytype", "gse"]}
                  for uid in summaries["uids"]]
    assert len(alias_hits) == int(alias_result.findtext("Count")) == 3
    assert all(row["taxon"] == "Sus scrofa domesticus" for row in alias_hits)
    sources = ["Supplementary-Table-S1.xlsx", "supplementaryFiles.zip", "GSE243380-self.txt",
               "GSE243377-self.txt", "GSE243379-self.txt", "github-README.md", "github-tree.json",
               "fresh-sarc.ipynb", "quality-table.ipynb", "gds-fresh-labels.xml",
               "gds-fresh-label-summary.json", "biosample-project.xml", "sra-project.xml"]
    return {"scope": "Independent metadata/assay/source linkage only; no gene expression outcomes",
            "owner_input_base": str(owner), "prior_input_base": str(prior),
            "owner_cache_bindings": [binding(cache / name, owner) for name in sources],
            "prior_derived_bindings": [binding(prior / name, prior) for name in
                ["GSM-ELIGIBILITY-OBSERVATIONS.json", "GSM-SOURCE-RECEIPTS.json", "COVERAGE.json"]],
            "S1_all_rows": s1, "frozen_post_filter_cell_total": 75716,
            "S1_exact_archive_extraction_verified": True,
            "named_library_count": len(ids), "named_library_metadata": libraries,
            "named_original_source_hashes_checked": 21,
            "named_original_source_receipts": original_receipts,
            "series_direction": series, "author_repo_commit": tree["sha"],
            "child_rosters_equal_named_superseries_roster": True,
            "author_repo_tree_complete": not tree["truncated"],
            "static_fresh_code": notebook_sources, "exact_alias_query_hits": alias_hits,
            "alias_query_limit": "Three piglet gut records are unrelated name collisions; no diagnosis can transfer from GS001/GS002. The indexed query and absent exact underscore aliases do not prove universal data absence.",
            "project_query_limit": "Owner queries contain PRJNA1018225 and PRJNA1018223 only; returned0 with PhraseNotFound. Index results do not authenticate absence or cover every child BioProject.",
            "disposition": "GS001 diagnosis/deposit unresolved; GS002 static code alias not an authenticated second donor. No eligible EMC compartment measurement established in this bounded source gate."}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--owner", type=Path, required=True)
    parser.add_argument("--prior", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.write_text(json.dumps(run(args.owner, args.prior), indent=2) + "\n")
