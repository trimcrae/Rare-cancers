#!/usr/bin/env python3
"""Finite public-input CLI replay; standard library, CPU only, no raw-data logs."""
import datetime, hashlib, json, os, subprocess, sys, urllib.request
from pathlib import Path
ROOT = Path(__file__).resolve().parents[4]
CAMPAIGN = Path(__file__).resolve().parents[1]
OUTPUTS = ROOT / "campaign-output"
MAX_BYTES = 64 * 1024 * 1024
SOURCES = json.loads(r'''[["trimcrae/Rare-cancers","af7211708205b5189d8c537c1ce2a23aa4bea076","research/literature/emc-census-2026-09-12/sources/clinicaltrials-discovery.json","research/literature/emc-census-2026-09-12/sources/clinicaltrials-discovery.json","b19b851de5da13f768856045da77d95c4ffd7c96","f45b8eb11625e2f2049c43086032951dfaf955bc63683b78dfdba8d87999bb9d"],["trimcrae/Rare-cancers","af7211708205b5189d8c537c1ce2a23aa4bea076","research/literature/emc-census-2026-09-12/sources/clinicaltrials-fulltext-discovery.json","research/literature/emc-census-2026-09-12/sources/clinicaltrials-fulltext-discovery.json","3593b82b00a4f2f87dcaff10b5239df789db3a61","b1beb99dcc3a9a5ad006ed810ebb2fec68a56d222bc12987b5acf954a46f11bc"],["mskcc/ImmunoSarc","b71c3373bc182f9c647a6f7bc1fbd641d24db917","Figures/data/PatientSourceData.txt","campaign-inputs/PatientSourceData.txt","8e65abf4208c2e6d9b96d8271752bfde4c85f443","ce4d01664c7ebba86b13356f36b84c398e4d57c9ef00637ecf1955139a837bdd"],["mskcc/ImmunoSarc","b71c3373bc182f9c647a6f7bc1fbd641d24db917","Figures/data/SampleSourceData.txt","campaign-inputs/SampleSourceData.txt","c3d9ee850299eb8930788468c87754b58d5a67f8","66d1f6bf39becc76f82d194ef2bf7b1784689c6d01177a319c717e208427e625"],["trimcrae/Rare-cancers","af7211708205b5189d8c537c1ce2a23aa4bea076","research/manuscripts/endpoint/endpoint-corpus-inputs.json","campaign-inputs/endpoint-corpus-inputs.json","d66060ca0acea0bb70fbb0e478ca5a3a5a8c4309",null],["trimcrae/Rare-cancers","af7211708205b5189d8c537c1ce2a23aa4bea076","research/manuscripts/endpoint/endpoint-corpus.json","campaign-inputs/endpoint-corpus.json","343922742f88f63a1803dba26904c45369c73d07",null],["trimcrae/Rare-cancers","af7211708205b5189d8c537c1ce2a23aa4bea076","research/manuscripts/endpoint/orr-dcr-reread.json","campaign-inputs/orr-dcr-reread.json","79c82a02cf5ce8534154896db140c9b67e88a892",null],["trimcrae/Rare-cancers","216bd1b5fb25a56b90ef3cc2373e1fe68322708f","literature/xdisease-ctg-results/ctg_results_bor_2022_2026.txt","campaign-inputs/ctg_results_bor_2022_2026.txt","f125b25e71104dc7db4f3134c3632406e88a9033",null],["qtran1/MeQTrack_app","578bb615e0e89858ffb02cbe1da87680c74a01ba","reference/GSE140686_sarcoma_methylation_labels.csv","campaign-inputs/GSE140686_sarcoma_methylation_labels.csv","3dd8b13a4c30d7ef06e5a933633a3e0da670efc1","c3b102c078a1035f4589952ea8b50ff3a8fbbb63ed8edd425aed2ea343119a19"]]''')
ANALYSES = json.loads(r'''[{"name":"registry-search","script":"registry_search.mjs","script_blob":"041309b0454d6a3b1c73d5b56109722c10a3622a","result":"registry-search.json","result_blob":"c544111c2bed5a184b990863ed051a70f2f35df8","args":[]},{"name":"immunosarc-availability","script":"immunosarc_availability.mjs","script_blob":"822909ebcafbad34c8360a19530f66b4e2d13b98","result":"immunosarc-availability.json","result_blob":"20b6fe121dfa6f6decf1ae64dc5ffeef274328d5","args":["campaign-inputs/PatientSourceData.txt","campaign-inputs/SampleSourceData.txt"]},{"name":"registry-units","script":"registry_units.mjs","script_blob":"f07fb3e23d1c74cffb6b036580bbb2d94251fcbc","result":"registry-units.json","result_blob":"a58af61cbfbd5852dce2fc4859e920b8814ae81b","args":["campaign-inputs/endpoint-corpus-inputs.json","campaign-inputs/endpoint-corpus.json","campaign-inputs/orr-dcr-reread.json","campaign-inputs/ctg_results_bor_2022_2026.txt"]},{"name":"methylation-feasibility","script":"methylation_feasibility.mjs","script_blob":"7a36bd70d1aad9c5086d7d70f0a8fac7fb22441e","result":"methylation-feasibility.json","result_blob":"9df3a88abadfac4638cfb9d1f6cb86773fee61c9","args":["campaign-inputs/GSE140686_sarcoma_methylation_labels.csv"]},{"name":"partner-intervals","script":"partner_intervals.mjs","script_blob":"db7aeabed04cba1ed64b3f5c5c464cc778593552","result":"partner-intervals.json","result_blob":"d15c16f20c2eecb65b5ada8e15e2b1dad33b08ad","args":[]},{"name":"hla-availability","script":"hla_availability.mjs","script_blob":"0952ae310144b90a50e9fa20d71cfd5422bb2da3","result":"hla-availability.json","result_blob":"7464e2e93ccdc21b73a8870dcd1b6313ccc49de4","args":["campaign-output/public-source-retrieval.json"]}]''')

def digest(data):
    return hashlib.sha256(data).hexdigest()

def blob(data):
    return hashlib.sha1(("blob " + str(len(data)) + "\0").encode("ascii") + data).hexdigest()

def verify(data, expected, sha256=None):
    if blob(data) != expected:
        raise ValueError("Git blob mismatch: " + expected)
    if sha256 and digest(data) != sha256:
        raise ValueError("SHA256 mismatch: " + sha256)

def fetch(spec):
    repo, revision, source, local, expected, sha256 = spec
    url = "https://raw.githubusercontent.com/" + repo + "/" + revision + "/" + source
    request = urllib.request.Request(url, headers={"User-Agent": "EMC-public-data-replay/1"})
    with urllib.request.urlopen(request, timeout=90) as response:
        length = response.headers.get("Content-Length")
        if length and int(length) > MAX_BYTES:
            raise ValueError("Source exceeds limit: " + source)
        parts, size = [], 0
        while True:
            chunk = response.read(min(1024 * 1024, MAX_BYTES + 1 - size))
            if not chunk:
                break
            parts.append(chunk)
            size += len(chunk)
            if size > MAX_BYTES:
                raise ValueError("Source exceeds limit: " + source)
    data = b"".join(parts)
    verify(data, expected, sha256)
    destination = ROOT / local
    destination.resolve().relative_to(ROOT)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(data)
    return {"repository": repo, "revision": revision, "path": source,
            "bytes": len(data), "git_blob": blob(data), "sha256": digest(data),
            "pinned_hash_verified": True}

def reject_constant(value):
    raise ValueError("Invalid JSON constant: " + value)

def parse(data):
    return json.loads(data, parse_constant=reject_constant)

def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False).encode("utf-8")

def replay(spec):
    script = CAMPAIGN / "analysis" / spec["script"]
    saved = CAMPAIGN / "results" / spec["result"]
    script_bytes, saved_bytes = script.read_bytes(), saved.read_bytes()
    verify(script_bytes, spec["script_blob"])
    verify(saved_bytes, spec["result_blob"])
    result = subprocess.run(["node", str(script), *[str(ROOT / arg) for arg in spec["args"]]],
                            cwd=ROOT, capture_output=True, timeout=120, check=False)
    if result.returncode:
        raise RuntimeError(spec["name"] + ": " + result.stderr.decode("utf-8", errors="replace")[:800])
    actual, expected = parse(result.stdout), parse(saved_bytes)
    excluded = []
    if spec["name"] == "methylation-feasibility":
        expected.pop("primaryReconciliation")
        excluded = ["primaryReconciliation"]
    actual_json = canonical(actual)
    if actual_json != canonical(expected):
        raise ValueError(spec["name"] + " differs from saved semantic JSON")
    (OUTPUTS / ("replayed-" + spec["name"] + ".json")).write_bytes(result.stdout)
    return {"analysis": spec["name"], "status": "pass",
            "script": str(script.relative_to(ROOT)), "script_git_blob": spec["script_blob"],
            "script_sha256": digest(script_bytes), "saved_result": str(saved.relative_to(ROOT)),
            "saved_result_git_blob": spec["result_blob"], "saved_result_sha256": digest(saved_bytes),
            "stdout_sha256": digest(result.stdout), "canonical_json_sha256": digest(actual_json),
            "semantic_json_equal": True, "excluded_saved_fields": excluded}

def main():
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    receipt = {"schema": "emc-bounded-cli-replay/1",
               "timestamp_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
               "checkout_commit": os.environ.get("GITHUB_SHA"),
               "workflow_run_id": os.environ.get("GITHUB_RUN_ID"),
               "python_version": sys.version.split()[0],
               "limits": {"file_bytes": MAX_BYTES, "network_seconds": 90, "node_seconds": 120},
               "scope": "Six Node CLI wrappers; not repository preflight or publication gates",
               "sources": [], "analyses": [], "status": "running"}
    exit_code = 0
    try:
        version = subprocess.run(["node", "--version"], cwd=ROOT, capture_output=True, timeout=10, check=True)
        receipt["node_version"] = version.stdout.decode("utf-8").strip()
        for source in SOURCES:
            receipt["sources"].append(fetch(source))
        hla = OUTPUTS / "public-source-retrieval.json"
        data = hla.read_bytes()
        receipt["hla_projection_input"] = {"path": str(hla.relative_to(ROOT)),
                                          "bytes": len(data), "sha256": digest(data),
                                          "provenance": "Public retrieval producer; HLA CLI verifies full-source hashes"}
        for analysis in ANALYSES:
            receipt["analyses"].append(replay(analysis))
        receipt["status"] = "pass"
        receipt["analyses_passed"] = len(receipt["analyses"])
        receipt["not_replayed"] = ["Separate primary methylation workbook reconciliation",
                                  "Raw-array QC/classifier fitting/CNV/spatial/proteomics analyses",
                                  "Repository preflight and publication gates"]
    except Exception as error:
        receipt.update(status="fail", error_type=type(error).__name__, error=str(error)[:1200])
        exit_code = 1
    (OUTPUTS / "replay-results.json").write_text(json.dumps(receipt, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")
    print("EMC_REPLAY_RESULT_BEGIN")
    print(json.dumps(receipt, separators=(",", ":"), ensure_ascii=False, allow_nan=False))
    print("EMC_REPLAY_RESULT_END")
    return exit_code

if __name__ == "__main__":
    sys.exit(main())
