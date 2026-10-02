#!/usr/bin/env python3
"""Bounded cloud-only replay of three small, source-pinned reanalyses."""
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import time
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "outputs-small"
OUT_CREATED = False
REF = "da49c4e836533253825587f83656675dac4c913b"
REGISTRY_REF = "216bd1b5fb25a56b90ef3cc2373e1fe68322708f"
GIB = 1024 ** 3
OUTPUT_RESERVE = 20 * 1024 ** 2
START = time.monotonic()
DEADLINE = START + 285  # Reserve final reporting time within five minutes.
RESULT = {"schema": "small-reanalyses-replay/1", "status": "running",
          "results": {}, "downloads": [], "limitations": [
              "Frozen source replay, not clinical validation or publication clearance.",
              "Foundation mapping is derived evidence; primary workbook not re-extracted.",
              "Registry conformance cases do not re-estimate the full 552/575 corpus.",
              "Methylation uses fixed saved predictions; no new fitting or patients."
          ]}


def remaining():
    value = DEADLINE - time.monotonic()
    if value <= 0:
        raise TimeoutError("Campaign elapsed-time budget exhausted")
    return value


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(262144), b""):
            h.update(block)
    return h.hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def headroom(expected_remaining):
    remaining()
    free = shutil.disk_usage(ROOT).free
    needed = 10 * GIB + expected_remaining + OUTPUT_RESERVE
    require(free >= needed, f"Insufficient headroom: free={free}, required={needed}")


def import_file(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def download(source, destination, expected_remaining):
    """No retries; byte cap, exact size/hash, bounded read and whole-download time."""
    headroom(expected_remaining)
    cap = source["bytes"]
    require(isinstance(cap, int) and 0 < cap <= 45 * 1024 ** 2,
            "Unexpected per-source byte cap")
    require(not destination.exists(), "Refusing existing download target")
    part = destination.with_suffix(destination.suffix + ".part")
    require(not part.exists(), "Refusing existing partial download")
    until = min(DEADLINE, time.monotonic() + 45)
    request = Request(source["url"], headers={"User-Agent": "EMC-small-frozen-replay"})
    count, h = 0, hashlib.sha256()
    try:
        with urlopen(request, timeout=min(10, remaining())) as response:
            length = response.headers.get("Content-Length")
            if length is not None:
                require(int(length) <= cap, "HTTP content length exceeds cap")
            with part.open("xb") as stream:
                while True:
                    require(time.monotonic() < until, "Per-download time budget exhausted")
                    remaining()
                    block = response.read1(min(262144, cap - count + 1))
                    if not block:
                        break
                    count += len(block)
                    require(count <= cap, "Download exceeds byte cap")
                    stream.write(block)
                    h.update(block)
        require(count == cap, "Downloaded size differs from pinned source receipt")
        require(h.hexdigest() == source["sha256"], "Downloaded SHA256 mismatch")
        part.rename(destination)
    except BaseException:
        if part.exists():
            part.unlink()  # Only the exact partial file created by this download.
        raise
    receipt = {"url": source["url"], "bytes": count, "sha256": h.hexdigest(),
               "path": str(destination.relative_to(OUT))}
    RESULT["downloads"].append(receipt)
    return expected_remaining - cap


def run(command, cwd, limit=50, expect_failure=False):
    remaining()
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    completed = subprocess.run(
        command, cwd=cwd, env=env, capture_output=True, text=True,
        encoding="utf-8", timeout=min(limit, remaining()), check=False)
    if expect_failure:
        require(completed.returncode != 0, "Expected command refusal did not occur")
    elif completed.returncode != 0:
        raise RuntimeError("Command failed: " + completed.stderr[-1500:])
    return completed


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def validate_source(source, revision, prefix):
    require(source.get("revision", revision) == revision, "Wrong immutable source revision")
    require(source["url"].startswith(prefix + revision + "/"), "Unexpected source URL")
    require(len(source["sha256"]) == 64 and
            all(c in "0123456789abcdef" for c in source["sha256"]),
            "Malformed source digest")
    require(Path(source["name"]).name == source["name"], "Unsafe source filename")


def main():
    global OUT_CREATED
    foundation = ROOT / "foundation"
    registry = ROOT / "registry"
    methylation = ROOT / "methylation"
    check = read_json(foundation / "foundation_recovery_check.json")
    reg_manifest = read_json(registry / "sources.json")
    meth_manifest = read_json(methylation / "sources.json")
    require(check["evidence_ref"] == REF, "Wrong Foundation evidence revision")
    fmap = dict(check["mapping"], name="mapping.json", revision=REF)
    fexport = dict(check["export"], name="data_sv.txt",
                   revision="dca75cb3f32b82d54a6f78bf0a6323e5b975aca1")
    validate_source(fmap, REF, "https://raw.githubusercontent.com/trimcrae/Rare-cancers/")
    validate_source(fexport, fexport["revision"],
                    "https://media.githubusercontent.com/media/cBioPortal/datahub/")
    registry_sources = reg_manifest["sources"]
    methylation_sources = meth_manifest["sources"]
    require(len(registry_sources) == 2, "Expected two frozen registry sources")
    require(len(methylation_sources) == 3, "Expected three frozen methylation sources")
    for source in registry_sources:
        validate_source(source, REGISTRY_REF,
                        "https://raw.githubusercontent.com/trimcrae/Rare-cancers/")
    for source in methylation_sources:
        validate_source(source, REF,
                        "https://raw.githubusercontent.com/trimcrae/Rare-cancers/")
    sources = [fmap, fexport] + registry_sources + methylation_sources
    budget = sum(s["bytes"] for s in sources)
    require(budget < 64 * 1024 ** 2, "Unexpected total download budget")
    headroom(budget)
    require(not OUT.exists(), "outputs-small already exists; preserve prior evidence")
    OUT.mkdir()
    OUT_CREATED = True
    for name in ("foundation-inputs", "registry", "registry/inputs", "methylation-inputs"):
        (OUT / name).mkdir()
    RESULT["download_budget_bytes"] = budget

    # Foundation: actual CLI output, independent expected hash, guard negative controls.
    RESULT["stage"] = "foundation"
    budget = download(fmap, OUT / "foundation-inputs/mapping.json", budget)
    budget = download(fexport, OUT / "foundation-inputs/data_sv.txt", budget)
    module = import_file("foundation_identity_recovery", foundation / "foundation_identity_recovery.py")
    require(module.EXPORT_SHA256 == fexport["sha256"], "Export constant/receipt mismatch")
    require(module.MAPPING_SHA256 == fmap["sha256"], "Mapping constant/receipt mismatch")
    command = [sys.executable, str(foundation / "foundation_identity_recovery.py"),
               "--export", str(OUT / "foundation-inputs/data_sv.txt"),
               "--mapping", str(OUT / "foundation-inputs/mapping.json"),
               "--out-dir", str(OUT / "foundation")]
    run(command, ROOT)
    corrected = OUT / "foundation/data_sv.identity_corrected.tsv"
    receipt_path = OUT / "foundation/identity_recovery_receipt.json"
    receipt = read_json(receipt_path)
    expected = check["observed_output"]
    require(sha(corrected) == expected["sha256"] == receipt["output_sha256"],
            "Foundation corrected-output hash mismatch")
    require(corrected.stat().st_size == expected["bytes"] == receipt["output_bytes"],
            "Foundation corrected-output size mismatch")
    require(receipt["event_count"] == expected["event_count"] == 3771,
            "Foundation event count mismatch")
    export_bytes = (OUT / "foundation-inputs/data_sv.txt").read_bytes()
    mapping_bytes = (OUT / "foundation-inputs/mapping.json").read_bytes()
    negative = {}
    for label, eb, mb in [
        ("modified-export", export_bytes + b" ", mapping_bytes),
        ("truncated-mapping", export_bytes, mapping_bytes[:-1]),
        ("already-corrected-export", corrected.read_bytes(), mapping_bytes),
    ]:
        remaining()
        try:
            module.correct_bytes(eb, mb)
        except ValueError as error:
            require("Unrecognized" in str(error), "Unexpected negative-control failure")
            negative[label] = "refused-by-input-hash-guard"
        else:
            raise AssertionError("Negative control was accepted: " + label)
    receipt_hash = sha(receipt_path)
    failed = run(command, ROOT, expect_failure=True)
    require("FileExistsError" in failed.stderr, "Overwrite refusal had unexpected cause")
    require(sha(corrected) == expected["sha256"] and sha(receipt_path) == receipt_hash,
            "Overwrite control altered existing output")
    negative["existing-output-directory"] = "refused-without-changing-output"
    RESULT["results"]["foundation"] = {
        "output_sha256": sha(corrected), "receipt_sha256": receipt_hash,
        "event_count": receipt["event_count"],
        "changed_sample_id_rows": receipt["changed_sample_id_rows"],
        "negative_controls": negative, "emc_join": receipt["emc_join"]}
    write_json(OUT / "foundation/validation.json", RESULT["results"]["foundation"])

    # Exact supplied registry runner, isolated workspace; no source-folder mutation.
    RESULT["stage"] = "registry"
    for name in ("registry_literal_extractor.py", "conformance_checks.py",
                 "run_frozen_checks.py", "sources.json", "cases.json"):
        shutil.copyfile(registry / name, OUT / "registry" / name)
    for source in registry_sources:
        budget = download(source, OUT / "registry/inputs" / source["name"], budget)
    completed = run([sys.executable, str(OUT / "registry/run_frozen_checks.py")],
                    OUT / "registry")
    reg_result = json.loads(completed.stdout)
    require(reg_result["syntheticChecks"] == 7, "Registry synthetic check count mismatch")
    expected_cases = {c["id"] for c in read_json(registry / "cases.json")["cases"]}
    require(set(reg_result["frozenCaseIds"]) == expected_cases and len(expected_cases) == 4,
            "Incomplete frozen registry case coverage")
    RESULT["results"]["registry"] = reg_result
    write_json(OUT / "registry/result.json", reg_result)

    # Reaggregate existing frozen methylation outputs, no Git checkout dependency.
    RESULT["stage"] = "methylation"
    for source in methylation_sources:
        budget = download(source, OUT / "methylation-inputs" / source["name"], budget)
    completed = run([sys.executable, str(methylation / "reaggregation.py"),
                     "--source-dir", str(OUT / "methylation-inputs")], ROOT)
    meth_result = json.loads(completed.stdout)
    require(meth_result["status"] == "executed assertions passed", "Methylation status failed")
    reported = {s["path"].split("/")[-1]: s["sha256"]
                for s in meth_result["sources"].values()}
    require(reported == {s["name"]: s["sha256"] for s in methylation_sources},
            "Methylation execution-source digests differ")
    expected_meth = read_json(methylation / "receipt.json")["expected_results"]
    require(math.isclose(meth_result["transformed_total_NLL"],
                         expected_meth["transformed_total_NLL"],
                         rel_tol=0, abs_tol=1e-12), "Methylation total differs")
    write_json(OUT / "methylation-result.json", meth_result)
    RESULT["results"]["methylation"] = {
        "profiles": meth_result["profiles"], "classes": meth_result["classes"],
        "metrics": meth_result["metrics"],
        "transformed_total_NLL": meth_result["transformed_total_NLL"],
        "zero_vote_case_fraction_total_NLL": meth_result["zero_vote_case_fraction_total_NLL"],
        "three_discordant_cases_fraction_total_NLL":
            meth_result["three_discordant_cases_fraction_total_NLL"],
        "result_sha256": sha(OUT / "methylation-result.json")}
    remaining()
    RESULT["stage"], RESULT["status"] = "complete", "passed"


if __name__ == "__main__":
    sys.dont_write_bytecode = True
    exit_code = 0
    try:
        require(hasattr(signal, "setitimer"), "Cloud runner requires Unix wall-clock timer")
        def stop_at_deadline(signum, frame):
            raise TimeoutError("285-second wall-clock execution ceiling reached")
        signal.signal(signal.SIGALRM, stop_at_deadline)
        signal.setitimer(signal.ITIMER_REAL, max(0.1, DEADLINE - time.monotonic()))
        main()
    except Exception as error:
        RESULT["status"] = "failed"
        RESULT["error"] = {"type": type(error).__name__, "message": str(error)[:1500]}
        exit_code = 1
    if hasattr(signal, "setitimer"):
        signal.setitimer(signal.ITIMER_REAL, 0)
    RESULT["elapsed_seconds"] = round(time.monotonic() - START, 3)
    if OUT_CREATED and not (OUT / "summary.json").exists():
        write_json(OUT / "summary.json", RESULT)
    print("EMC_SMALL_REANALYSES_RESULT_BEGIN")
    print(json.dumps(RESULT, separators=(",", ":"), allow_nan=False))
    print("EMC_SMALL_REANALYSES_RESULT_END")
    sys.exit(exit_code)

