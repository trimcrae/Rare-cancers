"""Verify imported checkpoint bytes and formats, without source retrieval/reanalysis.

The integration manifest records hashes checked against each frozen writer tree.
This portable check needs only committed files, not the workers or their raw caches.
"""
import hashlib
import json
from pathlib import Path


def main():
    packet = Path(__file__).resolve().parent
    root = packet.parents[2]
    manifest = json.loads((packet / "INTEGRATION-VERIFICATION.json").read_text())
    failures = []
    for row in manifest["copied_files"]:
        path = root / row["path"]
        if not path.is_file():
            failures.append({"path": row["path"], "failure": "missing committed export"})
            continue
        data = path.read_bytes()
        actual = hashlib.sha256(data).hexdigest()
        if actual != row.get("export_sha256", row["source_sha256"]):
            failures.append({"path": row["path"], "failure": "source/export hash mismatch"})
        if row.get("scientific_body_sha256"):
            body = data.split(b"\n---\n", 1)[1]
            if hashlib.sha256(body).hexdigest() != row["scientific_body_sha256"]:
                failures.append({"path": row["path"], "failure": "scientific body changed"})
        if path.suffix == ".json":
            json.loads(data.decode("utf-8-sig"))
        elif path.suffix == ".py":
            compile(data, str(path), "exec")
    bindings_checked = 0
    for row in manifest.get("review_bindings", []):
        if row["disposition"] != "committed-export":
            continue
        path = root / row["path"]
        actual = hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None
        if actual != row["sha256"]:
            failures.append({"path": row["path"], "failure": "review input binding mismatch"})
        bindings_checked += 1
    print(json.dumps({"imported_files_checked": len(manifest["copied_files"]),
                      "committed_review_bindings_checked": bindings_checked,
                      "failures": failures,
                      "scope": "Frozen export identity, committed review input hashes, JSON parsing and Python syntax; no scientific rerun or cache recovery."}, indent=2))
    return bool(failures)


if __name__ == "__main__":
    raise SystemExit(main())
