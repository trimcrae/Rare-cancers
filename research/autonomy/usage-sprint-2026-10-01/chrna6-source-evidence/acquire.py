"""Recover source excerpts for CHRNA6 without running expression statistics.

One bounded GET of the public GEO family SOFT; --check is fully offline.
Existing scientific packets and their analysis rules are read only.
"""
from pathlib import Path
import argparse
import base64
import collections
import datetime
import gzip
import hashlib
import json
import math
import os
import subprocess
import urllib.request

ROOT = Path(__file__).resolve().parents[4]
PACKET = ROOT / "research/autonomy/atlas-hofvander-validation-2026-09-06"
READINESS = ROOT / "research/modalities/expression-validation-readiness.json"
URL = "https://ftp.ncbi.nlm.nih.gov/geo/series/GSE24nnn/GSE24369/soft/GSE24369_family.soft.gz"
EXPECTED_GZIP_SHA256 = "98c83c8ca23b7052cf0d4d0099a7bf1af6c3c972276038c3a633e2a5349b3c37"
SOURCE_LIMIT = 32 * 1024 * 1024
EXPANDED_LIMIT = 512 * 1024 * 1024
METADATA = {
    "!Sample_title": "title",
    "!Sample_platform_id": "platform",
    "!Sample_characteristics_ch1": "characteristics_ch1",
    "!Sample_source_name_ch1": "source_ch1",
    "!Sample_source_name_ch2": "source_ch2",
    "!Sample_data_processing": "processing",
    "#VALUE": "VALUE_definition",
}


def sha_bytes(data):
    return hashlib.sha256(data).hexdigest()


def file_sha(path):
    return sha_bytes(path.read_bytes())


def fail(condition, message):
    if not condition:
        raise ValueError(message)


def parse_family(lines, expected_samples):
    """Read a complete platform table and target per-sample rows, retaining bytes' text."""
    expected_samples = set(expected_samples)
    samples = {}
    platform = None
    platform_header = None
    annotation = []
    seen_platform_ids = set()
    platform_rows = 0
    platform_complete = False
    in_platform = False
    in_sample = False
    sample = None
    header = None
    annotation_source = None
    line_count = 0
    for line_count, raw in enumerate(lines, 1):
        line = raw.rstrip("\r\n")
        if line.startswith("^PLATFORM = "):
            fail(not in_platform and not in_sample, "unterminated table before platform")
            platform = line.split(" = ", 1)[1]
            sample = None
        elif line == "!platform_table_begin":
            fail(platform == "GPL6244" and not in_platform and not platform_complete,
                 "wrong, duplicate or nested platform table")
            in_platform = True
            platform_header = None
        elif line == "!platform_table_end":
            fail(in_platform and platform_header is not None, "platform end without header")
            in_platform = False
            platform_complete = True
        elif in_platform:
            fields = line.split("\t")
            if platform_header is None:
                platform_header = fields
                fail("ID" in fields and "gene_assignment" in fields,
                     "missing explicit original-platform gene assignment columns")
                annotation_source = {"line": line_count, "text": line}
            else:
                fail(len(fields) == len(platform_header), "ragged platform row")
                pid = fields[platform_header.index("ID")]
                fail(pid and pid not in seen_platform_ids, "duplicate or empty platform ID")
                seen_platform_ids.add(pid)
                platform_rows += 1
                assignments = fields[platform_header.index("gene_assignment")]
                symbols = []
                for assignment in assignments.split("///"):
                    parts = [x.strip() for x in assignment.split("//")]
                    if len(parts) >= 2 and parts[1] not in ("", "---"):
                        symbols.append(parts[1])
                if "CHRNA6" in symbols:
                    annotation.append({
                        "probe_id": pid,
                        "all_assigned_symbols": sorted(set(symbols)),
                        "line": line_count, "text": line,
                        "fields": dict(zip(platform_header, fields)),
                    })
        elif line.startswith("^SAMPLE = "):
            fail(not in_sample, "unterminated sample table")
            sample = line.split(" = ", 1)[1]
            fail(sample in expected_samples and sample not in samples,
                 "unknown or duplicate sample record")
            samples[sample] = {"metadata": collections.defaultdict(list),
                               "metadata_lines": [], "values": {}, "table_complete": False}
            header = None
        elif line == "!sample_table_begin":
            fail(sample is not None and not in_sample and not samples[sample]["table_complete"],
                 "missing sample or repeated sample table")
            in_sample = True
            header = None
        elif line == "!sample_table_end":
            fail(in_sample and header is not None, "sample end without header")
            in_sample = False
            samples[sample]["table_complete"] = True
        elif in_sample:
            fields = line.split("\t")
            if header is None:
                header = fields
                fail("ID_REF" in header and "VALUE" in header, "missing sample value columns")
                samples[sample]["table_header"] = {"line": line_count, "text": line}
            else:
                fail(len(fields) == len(header), "ragged sample row")
                pid = fields[header.index("ID_REF")]
                if pid in {a["probe_id"] for a in annotation}:
                    fail(pid not in samples[sample]["values"], "duplicate sample/probe measurement")
                    token = fields[header.index("VALUE")]
                    value = float(token)
                    fail(math.isfinite(value), "nonfinite CHRNA6 measurement")
                    samples[sample]["values"][pid] = {
                        "value": value, "token": token, "line": line_count, "text": line
                    }
        elif sample is not None and " = " in line:
            key, value = line.split(" = ", 1)
            if key in METADATA:
                samples[sample]["metadata"][METADATA[key]].append(value)
                samples[sample]["metadata_lines"].append({"line": line_count, "text": line})
    fail(platform_complete and not in_platform and not in_sample,
         "incomplete source tables")
    fail(annotation, "no explicit CHRNA6 annotation; coverage remains unknown")
    fail(set(samples) == expected_samples, "incomplete sample roster")
    probes = {a["probe_id"] for a in annotation}
    for sid, row in samples.items():
        fail(row["table_complete"] and set(row["values"]) == probes,
             "incomplete sample/probe measurement coverage: " + sid)
        fail(row["metadata"]["platform"] == ["GPL6244"], "wrong sample platform: " + sid)
        fail(row["metadata"]["VALUE_definition"] == ["RMA log2 signal"],
             "unknown or changed preprocessing units: " + sid)
        fail(row["metadata"]["processing"], "missing preprocessing metadata: " + sid)
        row["metadata"] = dict(row["metadata"])
    return {"platform": "GPL6244", "platform_table_rows": platform_rows,
            "platform_header": annotation_source, "CHRNA6_annotation": annotation,
            "samples": samples, "source_line_count": line_count}


def frozen_inputs():
    manifest_path = PACKET / "replication-manifest.json"
    values_path = PACKET / "replication-results/array-values.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    values = json.loads(values_path.read_text(encoding="utf-8"))["CHRNA6"]
    readiness = json.loads(READINESS.read_text(encoding="utf-8"))
    arms = {row["sample_id"]["value"]: row["arm"]["value"]
            for row in readiness["cohorts"]["GSE24369"]["sample_records"]}
    roster = {row["sample_id"]: row for row in manifest["array_samples"]}
    fail(len(roster) == len(manifest["array_samples"]) == 42, "invalid committed roster")
    fail(set(roster) == set(values) == set(arms), "cached source/sample misalignment")
    counts = dict(collections.Counter(arms.values()))
    fail(counts == {"EMC": 6, "comparator": 29, "excluded_from_cached_contrast": 7},
         "historical exclusions changed")
    fail(manifest["source_files"]["GSE24369.soft.gz"]["sha256"] == EXPECTED_GZIP_SHA256,
         "historical source pin changed")
    return manifest, values, roster, arms, {
        str(p.relative_to(ROOT)): file_sha(p) for p in (manifest_path, values_path, READINESS)
    }


def compare(projection, manifest, cached, roster):
    """Exact equality to cached values and every matching preprocessing field; no ranks."""
    annotations = projection["CHRNA6_annotation"]
    cached_probe = manifest["gene_to_probe"]["CHRNA6"]
    fail({row["probe_id"] for row in annotations} == {cached_probe},
         "CHRNA6 probe-set differs from cached single-probe assignment")
    fail(all(row["all_assigned_symbols"] == ["CHRNA6"] for row in annotations),
         "ambiguous gene assignment; do not aggregate")
    differences = []
    for sid, row in projection["samples"].items():
        if row["values"][cached_probe]["value"] != cached[sid]:
            differences.append({"sample": sid, "field": "CHRNA6_value"})
        for field in ("title", "characteristics_ch1", "source_ch1", "source_ch2",
                      "processing", "VALUE_definition"):
            got = row["metadata"].get(field, [])
            expected = roster[sid][field]
            if field == "title":
                expected = [expected]
            if got != expected:
                differences.append({"sample": sid, "field": field})
    fail(not differences, "source/cache mismatch: " + json.dumps(differences))
    return {"values_compared": len(cached), "metadata_fields_compared": len(cached) * 6,
            "mismatches": 0, "numeric_tolerance": 0,
            "method": "direct float equality and exact metadata lists; no statistical analysis"}


def download(cache):
    cache.mkdir(parents=True, exist_ok=True)
    target = cache / "GSE24369_family.soft.gz"
    req = urllib.request.Request(URL, headers={"User-Agent": "EMC-public-evidence/1.0"})
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    total = 0
    with urllib.request.urlopen(req, timeout=60) as response:
        final_url = response.geturl()
        fail(final_url.startswith("https://ftp.ncbi.nlm.nih.gov/"), "unexpected redirect host")
        with target.open("xb") as out:
            while True:
                chunk = response.read(1024 * 1024)
                if not chunk:
                    break
                total += len(chunk)
                fail(total <= SOURCE_LIMIT, "source exceeds finite size limit")
                out.write(chunk)
        receipt = {"requested_url": URL, "final_url": final_url,
                   "started_utc": started,
                   "completed_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                   "bytes": total, "sha256": file_sha(target),
                   "last_modified": response.headers.get("Last-Modified"),
                   "etag": response.headers.get("ETag")}
    fail(receipt["sha256"] == EXPECTED_GZIP_SHA256,
         "primary source bytes changed; stop before interpretation")
    return target, receipt


def bounded_lines(path):
    total = 0
    with gzip.open(path, "rt", encoding="utf-8", errors="strict", newline="") as source:
        for line in source:
            total += len(line.encode("utf-8"))
            fail(total <= EXPANDED_LIMIT, "expanded source exceeds finite size limit")
            yield line


def check_projection(projection):
    """Bind parsed fields to the retained source text without trusting redundant fields."""
    h = projection["platform_header"]["text"].split("\t")
    fail(len(h) == len(set(h)), "duplicate annotation header")
    ids = []
    for row in projection["CHRNA6_annotation"]:
        f = row["text"].split("\t")
        fail(len(f) == len(h) and dict(zip(h, f)) == row["fields"],
             "annotation text/fields disagree")
        fail(row["probe_id"] == row["fields"]["ID"], "annotation probe ID differs")
        symbols = []
        for a in row["fields"]["gene_assignment"].split("///"):
            p = [v.strip() for v in a.split("//")]
            if len(p) >= 2 and p[1] not in ("", "---"):
                symbols.append(p[1])
        fail(row["all_assigned_symbols"] == sorted(set(symbols)) and "CHRNA6" in symbols,
             "annotation symbols differ")
        ids.append(row["probe_id"])
    fail(len(ids) == len(set(ids)) and ids, "empty or duplicate projected annotation")
    for sid, row in projection["samples"].items():
        meta = collections.defaultdict(list)
        for line in row["metadata_lines"]:
            key, value = line["text"].split(" = ", 1)
            fail(key in METADATA, "unexpected projected metadata")
            meta[METADATA[key]].append(value)
        fail(dict(meta) == row["metadata"], "metadata text/fields disagree: " + sid)
        header = row["table_header"]["text"].split("\t")
        fail(len(header) == len(set(header)) and "ID_REF" in header and "VALUE" in header,
             "invalid projected value header")
        fail(set(row["values"]) == set(ids), "projected coverage differs")
        for pid, value in row["values"].items():
            fields = value["text"].split("\t")
            fail(len(fields) == len(header) and fields[header.index("ID_REF")] == pid,
                 "probe text/ID differs")
            token = fields[header.index("VALUE")]
            fail(token == value["token"] and math.isfinite(float(token))
                 and float(token) == value["value"], "value text/fields disagree")


def check(evidence_path):
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    manifest, values, roster, arms, hashes = frozen_inputs()
    fail(evidence["schema"] == "chrna6-source-evidence/1", "wrong evidence schema")
    fail(evidence["input_sha256"] == hashes, "changed committed inputs")
    fail(evidence["acquisition"]["sha256"] == EXPECTED_GZIP_SHA256, "changed primary pin")
    projection = evidence["source_projection"]
    check_projection(projection)
    fail(set(projection["samples"]) == set(roster), "changed projected sample roster")
    fail(evidence["source_comparison"] == compare(projection, manifest, values, roster),
         "changed comparison receipt")
    fail(evidence["historical_arms"] == arms, "changed exclusion/arm policy")
    fail(evidence["independence"] == "unresolved; no discovery-study specimen crosswalk",
         "unsupported independence claim")
    return {"status": "PASS", "scope": "offline committed evidence integrity, not reacquisition",
            "samples": 42, "excluded_records": 7, "sha256": file_sha(evidence_path)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--acquire", action="store_true")
    mode.add_argument("--check", type=Path)
    parser.add_argument("--cache", type=Path, default=ROOT / ".cache/chrna6-source-evidence")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.check:
        print(json.dumps(check(args.check), sort_keys=True))
        return
    fail(args.output is not None, "--acquire requires --output outside protected scientific files")
    manifest, values, roster, arms, hashes = frozen_inputs()
    ledger = json.loads((ROOT / "research/autonomy/research-ledger.json").read_text())
    owned = [{"id": row["id"], "owner": row["owner"]} for row in ledger["entries"] if row.get("owner")]
    fail(not owned, "live ledger ownership found; coordinator reconciliation required")
    path, receipt = download(args.cache)
    projection = parse_family(bounded_lines(path), roster)
    comparison = compare(projection, manifest, values, roster)
    evidence = {
        "schema": "chrna6-source-evidence/1",
        "authorship": "AI-generated source projection; exact acquired source lines retained",
        "question": "Do authoritative GPL6244 CHRNA6 annotations and all 42 GEO values/processing records match the existing source-pinned cache?",
        "stop_condition": "One finite source acquisition and exact comparison; stop on source change, gap or mismatch. No expression statistics.",
        "source_revision": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "input_sha256": hashes,
        "ownership_check": {"ledger_sha256": file_sha(ROOT / "research/autonomy/research-ledger.json"),
                            "entries": len(ledger["entries"]), "live_owners": owned},
        "acquisition": receipt,
        "source_projection": projection,
        "source_comparison": comparison,
        "historical_arms": arms,
        "independence": "unresolved; no discovery-study specimen crosswalk",
        "limitations": [
            "Deposited RMA log2 probe-set summaries, not individual physical-oligonucleotide intensities.",
            "GSM identifiers do not establish independent patients or specimens.",
            "Seven historical contrast exclusions remain excluded despite retaining their source values.",
            "No classifier, hypothesis test, CISH threshold, clinical validation or therapeutic inference.",
            "The 2026-09-05 six-input readiness audit is historical; September6 cache already supplies these values.",
            "This excerpt complements inaccessible source bundle paths; it is not a complete portable source bundle.",
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    data = (json.dumps(evidence, ensure_ascii=True, indent=2, sort_keys=True) + "\n").encode()
    args.output.write_bytes(data)
    print(json.dumps({"status": "PASS", "acquisition": receipt,
                      "comparison": comparison, "probe_ids": [a["probe_id"] for a in projection["CHRNA6_annotation"]],
                      "output_bytes": len(data), "output_sha256": sha_bytes(data)}, sort_keys=True))
    print("EVIDENCE_BASE64_BEGIN")
    encoded = base64.b64encode(data).decode("ascii")
    for offset in range(0, len(encoded), 6000):
        print(encoded[offset:offset + 6000])
    print("EVIDENCE_BASE64_END")


if __name__ == "__main__":
    main()
