"""Finite GPL3290 source annotation/channel audit; never parse expression values."""
import argparse
import collections
import datetime as dt
import gzip
import hashlib
import json
from pathlib import Path
import re
import signal
import socket
import urllib.error
import urllib.request
import urllib.robotparser

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
PLATFORM = "GPL3290"
SERIES = "GSE4303"
MATRIX = "GSE4303-GPL3290_series_matrix.txt.gz"
URL = "https://ftp.ncbi.nlm.nih.gov/geo/series/GSE4nnn/GSE4303/soft/GSE4303_family.soft.gz"
ROBOTS_URL = "https://ftp.ncbi.nlm.nih.gov/robots.txt"
UA = "EMCResearchSourceAudit/1.0"
COMPRESSED_LIMIT = 64 * 1024 * 1024
EXPANDED_LIMIT = 256 * 1024 * 1024
META_KEYS = {"!Sample_title", "!Sample_platform_id", "!Sample_channel_count",
             "!Sample_hyb_protocol", "!Sample_scan_protocol", "!Sample_data_processing",
             "!Sample_description"}
CH_FIELDS = ("source_name", "organism", "molecule", "extract_protocol", "label", "label_protocol",
             "characteristics")
for channel in (1, 2):
    META_KEYS.update(f"!Sample_{field}_ch{channel}" for field in CH_FIELDS)
SYMBOL_COLUMNS = {"gene symbol", "gene_symbol", "symbol", "genesymbol"}
DESCRIPTORS = {"CRH", "CRH-mRNA", "UHR"}
PINS = {
 "research/modalities/emc-expression-panels-inputs.json": "6a4f778a3102b970f629906cf33357e97729a9d62ce9add20df709738cf1f3a8",
 "research/modalities/emc-expression-panels.json": "123bd05a9f9f5d08a362df3bd51cdbb72c241b49712123aaf5c5ea914f336bd9",
}

class CycleDeadline(BaseException):
    pass

def sha(b):
    return hashlib.sha256(b).hexdigest()

def fail(condition, reason):
    if not condition:
        raise ValueError(reason)

def frozen_inputs():
    for p, pin in PINS.items():
        fail(sha((ROOT / p).read_bytes()) == pin, "Existing expression input changed: " + p)
    inputs = json.loads((ROOT / "research/modalities/emc-expression-panels-inputs.json").read_text())
    samples = inputs["targets"][MATRIX]["samples"]
    roster = {s["gsm"]: s["title"] for s in samples}
    readiness_path = ROOT / "research/modalities/expression-validation-readiness.json"
    readiness = json.loads(readiness_path.read_text())
    old = readiness["cohorts"]["GSE4303"]["sample_records"]
    expected = {r["sample_id"]["value"]: r["title"]["value"] for r in old}
    fail(roster == expected and len(samples) == len(roster) == 16, "Current cached roster changed")
    arms = {r["sample_id"]["value"]: r["class"]["value"] for r in old}
    fail(collections.Counter(arms.values()) == {"EMC": 10, "DFSP": 3, "GIST": 3}, "Cached arms changed")
    return roster, arms, {**PINS, "research/modalities/expression-validation-readiness.json": sha(readiness_path.read_bytes())}

def metadata_from_lines(rows):
    out = collections.defaultdict(list)
    for r in rows:
        key, value = r["text"].split(" = ", 1)
        fail(key in META_KEYS or key.startswith("#"), "Unknown retained metadata key")
        out[key].append(value)
    return dict(out)

def descriptor_groups(samples):
    grouped = collections.defaultdict(list)
    for sid, s in samples.items():
        meta = s["metadata"]
        for channel in (1, 2):
            for descriptor in meta.get(f"!Sample_source_name_ch{channel}", []):
                if descriptor in DESCRIPTORS:
                    signature = {"channel": channel, "source_name": descriptor,
                                 "molecule": meta.get(f"!Sample_molecule_ch{channel}", []),
                                 "label": meta.get(f"!Sample_label_ch{channel}", [])}
                    grouped[json.dumps(signature, sort_keys=True)].append(sid)
    return [{"descriptor_signature": json.loads(k), "sample_ids": sorted(v)}
            for k, v in sorted(grouped.items())]

def parse_family(lines, expected):
    active_platform = None
    active_sample = None
    in_platform = False
    in_sample_table = False
    header = None
    target_done = False
    target_header = None
    target_rows = 0
    target_ids = set()
    table_hash = hashlib.sha256()
    literal_rows = []
    accession_examples = []
    platform_meta = []
    all_samples = []
    samples = {}
    series_ids = []
    expanded = 0
    last_line = 0
    for number, raw in enumerate(lines, 1):
        last_line = number
        expanded += len(raw.encode("utf-8"))
        fail(expanded <= EXPANDED_LIMIT, "Expanded source exceeds limit")
        line = raw.rstrip("\r\n")
        if line.startswith("^"):
            fail(not in_platform and not in_sample_table, "Record starts inside unclosed table")
            active_platform = active_sample = None
            if line.startswith("^SERIES = "):
                series_ids.append(line.split(" = ", 1)[1])
            elif line.startswith("^PLATFORM = "):
                active_platform = line.split(" = ", 1)[1]
            elif line.startswith("^SAMPLE = "):
                active_sample = line.split(" = ", 1)[1]
                fail(active_sample not in all_samples, "Duplicate sample record")
                all_samples.append(active_sample)
                if active_sample in expected:
                    samples[active_sample] = {"record": {"line": number, "text": line},
                      "metadata_lines": [], "table_complete": False}
            continue
        if line == "!platform_table_begin":
            fail(active_platform is not None and not in_platform, "Platform table lacks record")
            fail(active_platform != PLATFORM or not target_done, "Repeated target platform table")
            in_platform = True
            header = None
            continue
        if line == "!platform_table_end":
            fail(in_platform and header is not None, "Incomplete platform table")
            in_platform = False
            if active_platform == PLATFORM:
                target_done = True
            continue
        if in_platform:
            if active_platform != PLATFORM:
                if header is None:
                    header = line.split("\t")
                continue
            fields = line.split("\t")
            if header is None:
                header = fields
                fail("ID" in header and len(header) == len(set(header)), "Missing/duplicate platform columns")
                target_header = {"line": number, "text": line}
                table_hash.update(raw.encode("utf-8"))
            else:
                fail(len(fields) == len(header), "Ragged target annotation row")
                pid = fields[header.index("ID")]
                fail(pid and pid not in target_ids, "Duplicate/empty platform probe ID")
                target_ids.add(pid)
                target_rows += 1
                table_hash.update(raw.encode("utf-8"))
                row = {"line": number, "text": line, "probe_id": pid, "fields": dict(zip(header, fields))}
                if any("CHRNA6" in re.split(r"[^A-Za-z0-9_]+", token) for token in fields):
                    literal_rows.append(row)
                if len(accession_examples) < 3:
                    accession_examples.append(row)
            continue
        if line == "!sample_table_begin":
            fail(active_sample is not None and not in_sample_table, "Sample table lacks record")
            if active_sample in samples:
                fail(not samples[active_sample]["table_complete"], "Repeated sample table")
            in_sample_table = True
            continue
        if line == "!sample_table_end":
            fail(in_sample_table, "Sample end without table")
            in_sample_table = False
            if active_sample in samples:
                samples[active_sample]["table_complete"] = True
            continue
        if in_sample_table:
            # Deliberately do not split, coerce, select or persist any expression table row.
            continue
        if active_platform == PLATFORM and line.startswith(("!Platform_", "#")):
            platform_meta.append({"line": number, "text": line})
        if active_sample in samples and " = " in line:
            key, value = line.split(" = ", 1)
            if key in META_KEYS or key.startswith("#"):
                samples[active_sample]["metadata_lines"].append({"line": number, "text": line})
    fail(series_ids == [SERIES], "Source series identity mismatch")
    fail(target_done and target_header and target_rows > 0 and not in_platform and not in_sample_table,
         "Missing/truncated GPL3290 annotation or table")
    fail(set(samples) == set(expected), "Incomplete cached source roster")
    for sid, s in samples.items():
        s["metadata"] = metadata_from_lines(s["metadata_lines"])
        fail(s["metadata"].get("!Sample_platform_id") == [PLATFORM], "Wrong cached sample platform: " + sid)
        fail(s["metadata"].get("!Sample_title") == [expected[sid]], "Source/cache title mismatch: " + sid)
        fail(s["metadata"].get("!Sample_channel_count") == ["2"], "Not explicitly two-channel: " + sid)
        fail(s["table_complete"], "Truncated cached sample table: " + sid)
        for ch in (1, 2):
            fail(s["metadata"].get(f"!Sample_source_name_ch{ch}") is not None and
                 s["metadata"].get(f"!Sample_molecule_ch{ch}") is not None,
                 "Missing declared channel metadata: " + sid)
    return {"series": SERIES, "platform": PLATFORM, "platform_record_header": f"^PLATFORM = {PLATFORM}",
      "platform_metadata_lines": platform_meta, "platform_table_header": target_header,
      "platform_table_rows": target_rows, "platform_table_sha256": table_hash.hexdigest(),
      "explicit_symbol_columns": [h for h in target_header["text"].split("\t") if h.lower() in SYMBOL_COLUMNS],
      "literal_CHRNA6_annotation_rows": literal_rows, "annotation_examples": accession_examples,
      "samples": samples, "observed_series_sample_ids": all_samples, "source_line_count": last_line,
      "expanded_bytes": expanded, "reference_descriptor_groups": descriptor_groups(samples),
      "coverage_interpretation": "Deposited annotation and literal symbol hits only; CHRNA6 assay coverage remains unestablished without an authoritative complete probe assignment.",
      "reference_interpretation": "Deposited descriptor/channel groups only; different strings do not prove different biological pools, and matching labels do not prove identical pools. Common-pool and processing compatibility remain unestablished.",
      "expression_values_parsed": False}

def check_projection(p, expected):
    fail(p["series"] == SERIES and p["platform"] == PLATFORM and
         p["platform_record_header"] == f"^PLATFORM = {PLATFORM}", "Projected source/platform identity mismatch")
    header = p["platform_table_header"]["text"].split("\t")
    fail("ID" in header and len(header) == len(set(header)), "Malformed annotation header")
    fail(p["platform_table_rows"] > 0, "Empty target annotation census")
    fail(set(p["samples"]) == set(expected), "Projected cached roster mismatch")
    for sid, s in p["samples"].items():
        fail(s["record"]["text"] == "^SAMPLE = " + sid, "Sample record/raw ID mismatch")
        fail(metadata_from_lines(s["metadata_lines"]) == s["metadata"], "Raw/parsed sample metadata mismatch")
        meta = s["metadata"]
        fail(meta.get("!Sample_platform_id") == [PLATFORM], "Wrong projected sample platform")
        fail(meta.get("!Sample_title") == [expected[sid]], "Projected source/cache title mismatch")
        fail(meta.get("!Sample_channel_count") == ["2"] and s["table_complete"], "Incomplete two-channel source")
        for ch in (1, 2):
            fail(meta.get(f"!Sample_source_name_ch{ch}") is not None and meta.get(f"!Sample_molecule_ch{ch}") is not None,
                 "Incomplete channel metadata")
    fail(p["reference_descriptor_groups"] == descriptor_groups(p["samples"]), "Descriptor groups diverge from raw channel metadata")
    fail(p["expression_values_parsed"] is False, "Expression analysis is outside this source audit")
    for row in p["literal_CHRNA6_annotation_rows"] + p["annotation_examples"]:
        fields = row["text"].split("\t")
        fail(len(fields) == len(header) and row["fields"] == dict(zip(header, fields)) and
             row["probe_id"] == fields[header.index("ID")], "Raw/parsed annotation mismatch")
    fail(p["explicit_symbol_columns"] == [h for h in header if h.lower() in SYMBOL_COLUMNS], "Symbol header classification mismatch")

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args):
        raise ValueError("Source redirect refused; no new host/path acquisition")

def request(url, target, limit):
    opener = urllib.request.build_opener(NoRedirect())
    with opener.open(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=12) as r:
        fail(r.status == 200 and r.url == url, "Unexpected source response")
        fail(int(r.headers.get("Content-Length", "0")) <= limit, "Source length exceeds limit")
        n = 0
        with target.open("xb") as f:
            while True:
                b = r.read(65536)
                if not b:
                    break
                n += len(b)
                fail(n <= limit, "Source stream exceeds limit")
                f.write(b)
        return {"requested_url": url, "final_url": r.url, "bytes": n, "sha256": sha(target.read_bytes()),
                "http_status": r.status, "last_modified": r.headers.get("Last-Modified")}

def robots(cache):
    path = cache / "robots.txt"
    try:
        r = request(ROBOTS_URL, path, 65536)
    except urllib.error.HTTPError as e:
        if e.code in (404, 410):
            return {"requested_url": ROBOTS_URL, "http_status": e.code, "decision": "allow_missing"}
        raise
    raw = path.read_text(encoding="utf-8")
    parser = urllib.robotparser.RobotFileParser()
    parser.parse(raw.splitlines())
    r["raw_utf8"] = raw
    r["decision"] = "allow" if parser.can_fetch(UA, URL) else "refuse"
    fail(r["decision"] == "allow", "Robots policy refuses source acquisition")
    return r

def validate(record, expected, arms, pins):
    fail(record["schema"] == "emc-gpl3290-coverage/1" and record["input_sha256"] == pins and
         record["cached_arm_by_gsm"] == arms, "Frozen input/arm binding mismatch")
    fail(record["source_receipt"]["requested_url"] == URL and record["source_receipt"]["final_url"] == URL,
         "Official source locator mismatch")
    r = record["robots"]
    fail(r["requested_url"] == ROBOTS_URL, "Wrong robots source origin")
    if r["http_status"] == 200:
        fail(sha(r["raw_utf8"].encode()) == r["sha256"] and len(r["raw_utf8"].encode()) == r["bytes"],
             "Robots raw hash/size mismatch")
        parser = urllib.robotparser.RobotFileParser()
        parser.parse(r["raw_utf8"].splitlines())
        fail(parser.can_fetch(UA, URL) and r["decision"] == "allow", "Robots replay refuses source")
    else:
        fail(r["http_status"] in (404, 410) and r["decision"] == "allow_missing", "Unavailable robots cannot authorize source")
    fail(record["source_receipt"]["http_status"] == 200 and record["source_receipt"]["bytes"] <= COMPRESSED_LIMIT,
         "Invalid source acquisition receipt")
    check_projection(record["projection"], expected)
    fail(record["adjudication"] == {"CHRNA6_coverage": "not_established", "common_reference_pool": "not_established",
       "processing_compatibility": "not_established", "independent_validation": "not_established",
       "expression_statistics": "not_run"}, "Unsupported coverage/compatibility/independence conclusion")

def acquire(cache, expected, arms, pins):
    cache.mkdir(parents=True, exist_ok=True)
    started = dt.datetime.now(dt.timezone.utc).isoformat()
    rb = robots(cache)
    gzpath = cache / "GSE4303_family.soft.gz"
    receipt = request(URL, gzpath, COMPRESSED_LIMIT)
    with gzip.open(gzpath, "rt", encoding="utf-8", errors="strict", newline="") as f:
        projection = parse_family(f, expected)
    receipt["started_utc"] = started
    receipt["completed_utc"] = dt.datetime.now(dt.timezone.utc).isoformat()
    out = {"schema": "emc-gpl3290-coverage/1", "ai_authorship": "Codex AI assistant; independent LLM review pending",
      "source_receipt": receipt, "robots": rb, "input_sha256": pins, "cached_arm_by_gsm": arms, "projection": projection,
      "adjudication": {"CHRNA6_coverage": "not_established", "common_reference_pool": "not_established",
       "processing_compatibility": "not_established", "independent_validation": "not_established",
       "expression_statistics": "not_run"}}
    validate(out, expected, arms, pins)
    return out

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--acquire", action="store_true")
    p.add_argument("--check")
    p.add_argument("--output")
    args = p.parse_args()
    expected, arms, pins = frozen_inputs()
    if args.acquire:
        fail(not (HERE / "evidence.json").exists(), "Evidence already committed; no source repetition")
        fail(args.output is not None, "Output path required")
        socket.setdefaulttimeout(12)
        signal.signal(signal.SIGALRM, lambda *_: (_ for _ in ()).throw(CycleDeadline("Hard 180-second source-cycle deadline")))
        signal.alarm(180)
        out = acquire(Path(args.output).parent, expected, arms, pins)
        signal.alarm(0)
        text = json.dumps(out, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
        Path(args.output).write_text(text, encoding="utf-8", newline="")
        print("SOURCE_EVIDENCE_BEGIN")
        print(text, end="")
        print("SOURCE_EVIDENCE_END")
        print(f"EVIDENCE_SHA256={sha(text.encode())} BYTES={len(text.encode())}")
    elif args.check:
        out = json.loads(Path(args.check).read_text(encoding="utf-8"))
        validate(out, expected, arms, pins)
        print(f"OFFLINE_CHECK_OK samples={len(expected)} annotation_rows={out['projection']['platform_table_rows']} no_expression_values=True")
    else:
        p.error("Choose --acquire or --check")

if __name__ == "__main__":
    main()
