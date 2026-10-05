#!/usr/bin/env python3
"""Replay source hashes and one gzip header, never a gene/count row."""
import argparse
import collections
import datetime
import hashlib
import json
from pathlib import Path
import shutil
import zlib


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def first_line_only(data):
    decoder = zlib.decompressobj(31)
    line = bytearray()
    consumed = 0
    while True:
        if decoder.unconsumed_tail:
            char = decoder.decompress(decoder.unconsumed_tail, 1)
        elif consumed < len(data):
            char = decoder.decompress(data[consumed:consumed + 1], 1)
            consumed += 1
        else:
            raise AssertionError("No first newline in the retained prefix")
        if char:
            if char == b"\n":
                return line.decode(), consumed, len(line) + 1
            line.extend(char)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--owner-root", type=Path, default=Path(
        "/workspace/emc-r6-single_cell/research/autonomy/"
        "fresh-discovery-2026-10-05-round9/rna_processing/"
        "model_population_processed_source_gate"))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    here = Path(__file__).resolve().parent
    owner = args.owner_root
    expected = {
        "raw/GSE221532-series-brief.txt":
            "e89ee7c1963beee4ccb6e448b912e5d723797068ec5e9c08b9ba42da2b146286",
        "raw/processed-counts-compressed-prefix.bin":
            "25330ed15c106b70cdaf6ddd37eaaf8968ccefc8134f07c1ca27ffc1ad38d35e",
        "raw/GSE221532-BioSample-ten.xml":
            "02497ef08e1ba182af7687eb4ce7871d4aec08d2b1b0abb51ebae61b24ad6316",
        "raw/GSE299349-series-brief.txt":
            "94891546aa3a4185b16819c7e75c505604f5b9b0c011971bb0d3b0337a2d1ca0",
    }
    for name, expected_sha in expected.items():
        assert sha(owner / name) == expected_sha, name
    assert sha(owner / "MANIFEST.json") == (
        "2c1cc275290bc1211301e73e1afae4b616d57f558e7c4385b97ae8ba6fc901c1")
    assert sha(owner / "SCIENCE-FREEZE.json") == (
        "9d570216071207566863f05d0a341c49af0166f96bc87efacbec72f1df2ea814")
    manifest = json.loads((owner / "MANIFEST.json").read_text())
    for item in manifest["files"]:
        path = owner / item["path"]
        assert path.stat().st_size == item["bytes"], item["path"]
        assert sha(path) == item["sha256"], item["path"]
    gsm = json.loads((here / "GSE221532-EXACT-GSM-VERSUS-SERIES-FIELD-REVIEW.json").read_text())
    gsm_source = Path(gsm["source"]["path"])
    assert sha(gsm_source) == gsm["source"]["sha256"]
    assert len(gsm["observations"]) == 10
    assert gsm["source_series_fields"] == 0
    header, compressed_consumed, output_bytes = first_line_only(
        (owner / "raw/processed-counts-compressed-prefix.bin").read_bytes())
    fields = [field.rstrip("\r") for field in header.split("\t")]
    assert fields[0] == "" and len(fields) == 11
    labels = fields[1:]
    duplicates = {key: value for key, value in collections.Counter(labels).items() if value > 1}
    titles = [row["Sample_title"][0] for row in gsm["observations"]]
    assert duplicates == {"NMFH-1": 2}
    assert set(titles) - set(labels) == {"USZ-20_REA1"}
    assert compressed_consumed == 164 and output_bytes == 99
    series = json.loads((here / "SERIES-AVAILABILITY-CORRECTION-REVIEW.json").read_text())
    assert set(series["selected_fields"]["Series_sample_id"]) == {
        row["sample_id"] for row in gsm["observations"]}
    result = {
        "utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "status": "PASS",
        "owner_frozen_exports": len(manifest["files"]),
        "owner_frozen_export_bytes": manifest["total_bytes"],
        "new_owner_original_hashes": len(expected),
        "reused_GSM_original_hashes": 1,
        "GSM_conditions": 10,
        "series_membership_conditions": 10,
        "processed_columns": 10,
        "distinct_aliases": len(set(labels)),
        "duplicates": duplicates,
        "missing_GSM_title": "USZ-20_REA1",
        "compressed_bytes_consumed_for_header": compressed_consumed,
        "decompressed_bytes_including_newline": output_bytes,
        "gene_count_rows_decompressed_by_replay": 0,
        "new_requests_or_outcomes": 0,
        "new_original_bytes_reviewer": 0,
        "free_bytes": shutil.disk_usage(here).free,
        "scope": "Source/field/header integrity only; no full matrix hash, normalized RNA result, scientific-value proof or publication clearance.",
    }
    if args.output:
        args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
