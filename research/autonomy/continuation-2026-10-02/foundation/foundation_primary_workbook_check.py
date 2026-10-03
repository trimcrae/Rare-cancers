"""Independent primary-XLS check of Foundation identity recovery.

Run in the approved cloud environment with xlrd installed. Does not import the
original extraction helper or the correction prototype. stdout is one JSON receipt.
Default is offline; --fetch-primary explicitly permits one bounded public GET.
"""
import argparse
from collections import Counter
import csv
import hashlib
import io
import json
from pathlib import Path
import sys
import urllib.request
import zipfile

WB_SHA = "88c1a0bab7509ffe3bcff955b89f3d60ddb58a68311cd4c56ca4b0c78506b475"
MAP_SHA = "341f64562039230c581aefb7f03d7da4769969a79290217962216f3d7e567a5e"
EXPORT_SHA = "d9fc3fc8073104c3f364825972921f271b5e8793eefcf71331c3cff7d3882701"
CORRECTED_SHA = "2c910856e5e483c3774af5d0192b6118536f368aade8f05960bb123014a20184"
PRIMARY_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC9200814/supplementaryFiles"
MEMBER = "41467_2022_30496_MOESM2_ESM.xls"
PREFIX = "sarcoma_msk_2022-"
VARIANT_SHEET = "variants_table_final_for_supple"
CLINICAL_SHEET = "samples_table_final_for_supplem"
VARIANT_HEADERS = [
    "de-identified ID", "gene", "partner_gene", "alteration_type", "cds_effect",
    "protein_effect", "copy_number", "fraction_reads", "Chromosome", "position",
    "refSeq_SV", "altSeq_SV", "transcript_SV"
]
CLINICAL_HEADERS = [
    "de-identified ID", "initial_diagnosis", "final_diagnosis", "tissue",
    "age [0-89]", "gender", "msi_status", "mutation_load_per_mb",
    "percent_genome_loh", "computational_tumor_purity"
]
EXPORT_HEADERS = [
    "Sample_Id", "SV_Status", "Site1_Hugo_Symbol", "Site2_Hugo_Symbol", "NCBI_Build"
]
CAP = 20 * 1024 * 1024


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def pinned(data, expected, label):
    require(digest(data) == expected, label + " SHA256 mismatch")
    return data


def bounded_file(path):
    require(path.stat().st_size <= CAP, "Input exceeds 20MiB")
    return path.read_bytes()


def workbook_bytes(args):
    if args.workbook:
        raw = bounded_file(args.workbook)
        receipt = {"transport": "local_workbook"}
    else:
        if args.archive:
            archive = bounded_file(args.archive)
            receipt = {"transport": "local_archive"}
        else:
            request = urllib.request.Request(
                PRIMARY_URL, headers={"User-Agent": "EMC-primary-identity-verification/1"}
            )
            # No alternative authenticated source, access bypass, or fallback.
            with urllib.request.urlopen(request, timeout=90) as response:
                require(response.status == 200, "Unexpected primary HTTP status")
                archive = response.read(CAP + 1)
                receipt = {"transport": "public_HTTPS", "url": PRIMARY_URL,
                           "final_url": response.url, "http_status": response.status}
            require(len(archive) <= CAP, "Primary archive exceeds 20MiB")
        receipt.update(archive_sha256=digest(archive), archive_bytes=len(archive))
        with zipfile.ZipFile(io.BytesIO(archive)) as z:
            matches = [i for i in z.infolist() if Path(i.filename).name == MEMBER]
            require(len(matches) == 1, "Missing or duplicate primary workbook member")
            info = matches[0]
            require(info.file_size == 4812800, "Unexpected uncompressed workbook size")
            raw = z.read(info)
            receipt["archive_member"] = info.filename
    require(len(raw) == 4812800, "Unexpected workbook byte count")
    pinned(raw, WB_SHA, "Primary workbook")
    require(raw[:8] == bytes.fromhex("d0cf11e0a1b11ae1"), "Expected legacy XLS OLE signature")
    receipt.update(workbook_bytes=len(raw), workbook_sha256=digest(raw))
    return raw, receipt


def source_id(value):
    # xlrd represents BIFF numeric cells as floats; do not round fractions.
    if isinstance(value, float):
        require(value.is_integer(), "Non-integral primary source ID")
        value = str(int(value))
    elif isinstance(value, int) and not isinstance(value, bool):
        value = str(value)
    else:
        value = str(value).strip()
    require(value.isascii() and value.isdigit() and value == str(int(value)),
            "Noncanonical primary source ID")
    require(1 <= int(value) <= 7494, "Primary ID outside study range")
    return value


def mapped_gene(value):
    # Reproduce only the published mapping's documented representation.
    # Numeric BIFF cell values remain strings such as 44621.0, not gene aliases.
    text = str(value).strip()
    return "" if text.upper() in ("", "NA", "N/A", "NAN") else text


def tsv(raw):
    reader = csv.DictReader(io.StringIO(raw.decode("utf-8"), newline=""), delimiter="\t")
    require(reader.fieldnames == EXPORT_HEADERS, "Unexpected export columns")
    rows = list(reader)
    require(all(set(r) == set(EXPORT_HEADERS) and None not in r.values() for r in rows),
            "Malformed TSV record")
    return rows


def check(args):
    import xlrd
    wb, transport = workbook_bytes(args)
    mapping_bytes = pinned(bounded_file(args.mapping), MAP_SHA, "Mapping")
    export_bytes = pinned(bounded_file(args.export), EXPORT_SHA, "Original export")
    corrected_bytes = pinned(bounded_file(args.corrected), CORRECTED_SHA, "Corrected export")
    # Only concrete records are accessed; no derived summary or perEMC fields.
    mapping = json.loads(mapping_bytes)["result"]["REmapping"]["mapping"]
    original, corrected = tsv(export_bytes), tsv(corrected_bytes)
    book = xlrd.open_workbook(file_contents=wb, on_demand=True)
    try:
        variants = book.sheet_by_name(VARIANT_SHEET)
        clinical = book.sheet_by_name(CLINICAL_SHEET)
        require(variants.nrows == 28547 and clinical.nrows == 7495,
                "Pinned workbook physical dimensions differ")
        require(variants.row_values(0) == VARIANT_HEADERS, "Variant headers differ")
        require(clinical.row_values(0) == CLINICAL_HEADERS, "Clinical headers differ")
        all_clinical_ids = []
        emc_ids = set()
        for index in range(1, clinical.nrows):
            row = clinical.row_values(index)
            sid = source_id(row[0])
            all_clinical_ids.append(sid)
            if str(row[2]).strip().casefold() == "extraskeletal myxoid chondrosarcoma":
                emc_ids.add(sid)
        require(len(all_clinical_ids) == len(set(all_clinical_ids)) == 7494,
                "Duplicate or incomplete clinical IDs")
        clinical_id_set = set(all_clinical_ids)
        events = []
        numeric_gene_cells = []
        for index in range(1, variants.nrows):
            values = variants.row_values(index)
            if values[3] != "RE":
                continue
            ordinal = len(events) + 1
            sid = source_id(values[0])
            require(sid in clinical_id_set, "Variant ID absent from primary clinical sheet")
            raw_pair = values[1:3]
            pair = [mapped_gene(v) for v in raw_pair]
            events.append({
                "REordinal": ordinal, "sourceExcelRow": index + 1,
                "sourceID": sid, "sourceGenePair": pair
            })
            for position, value in enumerate(raw_pair):
                if isinstance(value, (int, float)) and not isinstance(value, bool):
                    numeric_gene_cells.append({
                        "REordinal": ordinal, "sourceExcelRow": index + 1,
                        "gene_slot": position + 1, "raw_numeric_value": value,
                        "mapping_representation": pair[position]
                    })
        require(len(events) == len(mapping) == len(original) == len(corrected) == 3771,
                "Incomplete event coverage")
        differences = []
        source_counts = Counter()
        id_discordances = 0
        missing_tokens = 0
        selected_events = []
        for primary, mapped, old, new in zip(events, mapping, original, corrected):
            ordinal = primary["REordinal"]
            for key in ("REordinal", "sourceExcelRow", "sourceID", "sourceGenePair"):
                require(primary[key] == mapped[key], "Primary/mapping mismatch at ordinal " + str(ordinal) + " field " + key)
            require(old["Sample_Id"] == mapped["exportSampleID"] == PREFIX + str(ordinal + 3),
                    "Original export mapping mismatch")
            require(new["Sample_Id"] == PREFIX + primary["sourceID"],
                    "Corrected sample ID disagrees with PRIMARY workbook")
            require(all(old[k] == new[k] for k in EXPORT_HEADERS if k != "Sample_Id"),
                    "Non-ID export field changed")
            export_pair = [old["Site1_Hugo_Symbol"], old["Site2_Hugo_Symbol"]]
            normalized_export = [mapped_gene(v) for v in export_pair]
            require(normalized_export == mapped["exportGenePair"], "Mapping/export gene pair mismatch")
            missing_tokens += sum(v == "N/A" for v in export_pair)
            if primary["sourceGenePair"] != normalized_export:
                differences.append({
                    **primary, "exportGenePairLiteral": export_pair
                })
            source_counts[primary["sourceID"]] += 1
            id_discordances += old["Sample_Id"] != PREFIX + primary["sourceID"]
            if old["Sample_Id"].removeprefix(PREFIX) in emc_ids:
                selected_events.append(primary)
        corrected_counts = Counter(r["Sample_Id"].removeprefix(PREFIX) for r in corrected)
        require(source_counts == corrected_counts, "PRIMARY sample-event multiplicities changed")
        require(source_counts["49"] == 1 and source_counts["245"] == 2, "Sentinel events differ")
        primary_emc_events = [e for e in events if e["sourceID"] in emc_ids]
        return {
            "schema": "foundation-primary-workbook-independent-check/1",
            "status": "passed",
            "reader": {"package": "xlrd", "version": xlrd.__version__},
            "primary_source": transport,
            "input_hashes": {"mapping": MAP_SHA, "original_export": EXPORT_SHA,
                             "corrected_export": CORRECTED_SHA},
            "source_sheet": VARIANT_SHEET,
            "physical_variant_rows": variants.nrows,
            "primary_clinical_profiles": len(all_clinical_ids),
            "rearrangement_events": len(events),
            "direct_primary_fields_checked": ["REordinal", "sourceExcelRow", "sourceID", "sourceGenePair"],
            "direct_primary_mapping_matches": len(events),
            "direct_primary_corrected_ID_matches": len(events),
            "non_ID_export_fields_unchanged": True,
            "direct_primary_multiplicities_preserved": True,
            "distinct_primary_event_source_IDs": len(source_counts),
            "original_ID_discordances": id_discordances,
            "gene_pair_agreements_after_explicit_missing_token_convention": len(events) - len(differences),
            "literal_gene_pair_differences": differences,
            "numeric_primary_gene_cells": numeric_gene_cells,
            "N_A_export_tokens": missing_tokens,
            "primary_EMC_join": {
                "source_profiles": len(emc_ids), "source_events": len(primary_emc_events),
                "export_selected_events": len(selected_events),
                "selected_originating_in_EMC": sum(e["sourceID"] in emc_ids for e in selected_events),
                "source_profiles_outside_export_suffix_range": sum(not 4 <= int(s) <= 3774 for s in emc_ids)
            },
            "sentinel_primary_events": [e for e in events if e["sourceID"] in ("49", "245")],
            "limits": [
                "Independent extraction/code path; same xlrd reader family as historical extraction.",
                "Explicit empty/NA/N/A/NAN and whitespace comparison convention; no gene-alias equivalence assumed.",
                "No source diagnosis, somatic origin, biological function or portal deployment validation.",
                "No new primary assay measurements."
            ]
        }
    finally:
        book.release_resources()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    src = parser.add_mutually_exclusive_group(required=True)
    src.add_argument("--workbook", type=Path)
    src.add_argument("--archive", type=Path)
    src.add_argument("--fetch-primary", action="store_true")
    parser.add_argument("--mapping", required=True, type=Path)
    parser.add_argument("--export", required=True, type=Path)
    parser.add_argument("--corrected", required=True, type=Path)
    args = parser.parse_args()
    try:
        receipt = check(args)
    except Exception as error:
        print(json.dumps({"schema": "foundation-primary-workbook-independent-check/1",
                          "status": "failed", "error_type": type(error).__name__,
                          "message": str(error)}, allow_nan=False))
        raise SystemExit(1)
    print(json.dumps(receipt, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
