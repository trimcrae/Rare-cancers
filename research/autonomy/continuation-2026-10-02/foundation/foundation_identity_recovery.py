"""Offline identity-only recovery for the pinned Foundation rearrangement export.
No network access. Does not validate biology, somatic origin, or cBioPortal import.
"""
import argparse
import csv
import hashlib
import io
import json
from collections import Counter
from pathlib import Path

EXPORT_SHA256 = "d9fc3fc8073104c3f364825972921f271b5e8793eefcf71331c3cff7d3882701"
MAPPING_SHA256 = "341f64562039230c581aefb7f03d7da4769969a79290217962216f3d7e567a5e"
WORKBOOK_SHA256 = "88c1a0bab7509ffe3bcff955b89f3d60ddb58a68311cd4c56ca4b0c78506b475"
PREFIX = "sarcoma_msk_2022-"
COLUMNS = ["Sample_Id", "SV_Status", "Site1_Hugo_Symbol", "Site2_Hugo_Symbol", "NCBI_Build"]

def sha256(data):
    return hashlib.sha256(data).hexdigest()

def require(condition, message):
    if not condition:
        raise ValueError(message)

def correct_bytes(export_bytes, mapping_bytes):
    require(sha256(export_bytes) == EXPORT_SHA256, "Unrecognized export bytes; refusing correction")
    require(sha256(mapping_bytes) == MAPPING_SHA256, "Unrecognized mapping bytes; refusing correction")
    result = json.loads(mapping_bytes)["result"]
    require(result["workbookSHA256"] == WORKBOOK_SHA256, "Wrong source workbook")
    require(not result["errors"], "Source artifact records errors")
    # Ignore historical ordinalIDMatch/ordinalIDMatches fields: use literal records.
    mapping = result["REmapping"]["mapping"]
    require(len(mapping) == 3771, "Incomplete recovery map")
    require([m["REordinal"] for m in mapping] == list(range(1, 3772)), "Missing, duplicated, or unordered event ordinal")
    require(len({m["sourceExcelRow"] for m in mapping}) == 3771, "Duplicate source worksheet row")
    reader = csv.DictReader(io.StringIO(export_bytes.decode("utf-8"), newline=""), delimiter="\t")
    require(reader.fieldnames == COLUMNS, "Unexpected export schema")
    rows = list(reader)
    require(len(rows) == len(mapping), "Event count mismatch")
    missing_token_comparisons = 0
    corrected = []
    provenance = []
    for row, m in zip(rows, mapping):
        require(set(row) == set(COLUMNS) and None not in row.values(), "Malformed export row")
        ordinal = m["REordinal"]
        require(row["Sample_Id"] == m["exportSampleID"] == PREFIX + str(ordinal + 3), "Export ID does not match mapping")
        raw_pair = [row["Site1_Hugo_Symbol"], row["Site2_Hugo_Symbol"]]
        # Existing mapping represents TSV N/A as empty; output retains original tokens.
        comparison_pair = ["" if v == "N/A" else v for v in raw_pair]
        missing_token_comparisons += sum(v == "N/A" for v in raw_pair)
        require(comparison_pair == m["exportGenePair"], "Export gene pair does not match mapping")
        source_id = m["sourceID"]
        require(isinstance(source_id, str) and source_id.isascii() and source_id.isdigit(), "Invalid source ID")
        require(source_id == str(int(source_id)) and 1 <= int(source_id) <= 7494, "Noncanonical source ID")
        require(isinstance(m["sourceExcelRow"], int) and m["sourceExcelRow"] > 1, "Invalid source row")
        new_row = dict(row)
        new_row["Sample_Id"] = PREFIX + source_id
        corrected.append(new_row)
        provenance.append({
            "event_id": "sourceRE:" + str(ordinal),
            "source_RE_ordinal": ordinal,
            "source_excel_row": m["sourceExcelRow"],
            "source_sample_id": source_id,
            "original_export_sample_id": row["Sample_Id"],
            "corrected_sample_id": new_row["Sample_Id"],
            "source_gene_pair_literal": m["sourceGenePair"],
            "export_gene_pair_retained": raw_pair
        })
    source_counts = Counter(m["sourceID"] for m in mapping)
    corrected_counts = Counter(r["Sample_Id"].removeprefix(PREFIX) for r in corrected)
    require(source_counts == corrected_counts, "Source multiplicities were not preserved")
    require(source_counts["49"] == 1 and source_counts["245"] == 2, "Sentinel source multiplicities differ")
    for old, new in zip(rows, corrected):
        require(all(old[k] == new[k] for k in COLUMNS if k != "Sample_Id"), "Non-identity content changed")
    # perEMC is not used to generate the correction, only to quantify one join.
    emc_ids = {str(p["sourceID"]) for p in result["perEMC"]}
    require(len(emc_ids) == 75, "Unexpected EMC source ID set")
    true_emc = [m for m in mapping if m["sourceID"] in emc_ids]
    selected = [m for m in mapping if m["exportSampleID"].removeprefix(PREFIX) in emc_ids]
    retained = [m for m in selected if m["sourceID"] in emc_ids]
    require(len(true_emc) == 76, "Unexpected EMC event count")
    out = io.StringIO(newline="")
    writer = csv.DictWriter(out, fieldnames=COLUMNS, delimiter="\t", lineterminator="\n")
    writer.writeheader()
    writer.writerows(corrected)
    output_bytes = out.getvalue().encode("utf-8")
    receipt = {
        "schema": "foundation-identity-only-recovery/1",
        "input_export_sha256": EXPORT_SHA256,
        "input_mapping_sha256": MAPPING_SHA256,
        "primary_workbook_sha256": WORKBOOK_SHA256,
        "output_sha256": sha256(output_bytes),
        "output_bytes": len(output_bytes),
        "event_count": len(corrected),
        "distinct_source_ids": len(source_counts),
        "changed_sample_id_rows": sum(a["Sample_Id"] != b["Sample_Id"] for a, b in zip(rows, corrected)),
        "non_identity_fields_unchanged": True,
        "comparison_only_missing_value_convention": "TSV N/A compared with empty mapping value; raw TSV retained",
        "NA_tokens_compared_as_empty": missing_token_comparisons,
        "source_multiplicities_preserved": True,
        "sentinel_source_multiplicities": {"49": source_counts["49"], "245": source_counts["245"]},
        "emc_join": {
            "selector": "75 primary EMC source IDs with sarcoma_msk_2022- prefix",
            "source_profiles": len(emc_ids),
            "true_source_events": len(true_emc),
            "events_selected_before_correction": len(selected),
            "selected_events_originating_in_EMC": len(retained),
            "selected_events_originating_outside_EMC": len(selected) - len(retained),
            "source_profiles_outside_export_suffix_range": sum(not 4 <= int(x) <= 3774 for x in emc_ids)
        },
        "limits": [
            "Identity-only derivative; no clinical or portal deployment validation.",
            "SV_Status, NCBI_Build and export gene symbols retained without validation.",
            "SOMATIC labels do not establish somatic origin; no matched-normal validation.",
            "No evidence that a downstream publication used the affected join.",
            "Map is derived evidence tied to the hashed primary workbook, not a new workbook reanalysis."
        ],
        "events": provenance
    }
    return output_bytes, receipt

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--export", required=True, type=Path)
    parser.add_argument("--mapping", required=True, type=Path)
    parser.add_argument("--out-dir", required=True, type=Path,
                        help="Must not exist; prevents overwriting inputs or previous results")
    args = parser.parse_args()
    output, receipt = correct_bytes(args.export.read_bytes(), args.mapping.read_bytes())
    # Validate every input before creating any output. Deliberately no overwrite.
    args.out_dir.mkdir(parents=False, exist_ok=False)
    (args.out_dir / "data_sv.identity_corrected.tsv").write_bytes(output)
    (args.out_dir / "identity_recovery_receipt.json").write_text(
        json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in receipt.items() if k != "events"}, indent=2))

if __name__ == "__main__":
    main()
