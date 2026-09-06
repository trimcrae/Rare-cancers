"""Read-only source integrity/excerpt check; not an exhaustive literature review."""
import hashlib
import html
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent


def normalize(text):
    return re.sub(r"\s+", " ", html.unescape(re.sub("<[^>]+>", " ", text))).strip()


def main():
    manifest = json.loads((HERE / "worker-artifact-manifest.json").read_text())
    for entry in manifest["files"]:
        data = (HERE / entry["file"]).read_bytes()
        assert len(data) == entry["bytes"]
        assert hashlib.sha256(data).hexdigest() == entry["sha256"]
    access = json.loads((HERE / "access-log.json").read_text())
    assert len(access) == 18
    for entry in access:
        data = (HERE / entry["file"]).read_bytes()
        assert len(data) == entry["bytes"]
        assert hashlib.sha256(data).hexdigest() == entry["sha256"]
    evidence = json.loads((HERE / "evidence.json").read_text())
    assert len(evidence["sources"]) == 6
    for entry in evidence["sources"]:
        data = (HERE / entry["source_file"]).read_bytes()
        assert len(data) == entry["bytes"]
        assert hashlib.sha256(data).hexdigest() == entry["sha256"]
        assert normalize(entry["observed_excerpt"]) in normalize(data.decode("utf-8"))
    for name in ("cattaruzza_supp_pmc", "cattaruzza_supp_index"):
        data = (HERE / (name + ".response")).read_bytes()
        assert not data.startswith(b"%PDF") and b"html" in data.lower()
    assert "not open access" in (HERE / "cattaruzza_epmc_supp_api.response").read_text().lower()
    print(json.dumps({"worker_files": len(manifest["files"]), "response_hashes": 18,
                      "primary_excerpts": 6, "supplement_not_recovered": True,
                      "scope": "Saved-source integrity and excerpt matching, not evidence of EMC absence"}))


if __name__ == "__main__":
    main()
