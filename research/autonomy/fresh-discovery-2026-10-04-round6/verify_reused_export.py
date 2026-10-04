"""Check cloud export identity against the unchanged R1–R5 portable inventory.

This checks bytes/availability only, not scientific replication or interpretation.
Run from any directory; emits a compact JSON result and fails on mismatched exports.
"""
import hashlib
import json
from pathlib import Path


def main():
    root = Path(__file__).resolve().parents[3]
    handoff = root / "research/autonomy/fresh-discovery-2026-10-04-handoff"
    inventory = json.loads((handoff / "PORTABLE-INVENTORY.json").read_text())["files"]
    registration = json.loads((handoff / "DOCUMENT-REGISTRATION.json").read_text())
    transformed = {r["path"]: r["export_sha256"] for r in registration["frontmatter"]}
    checked, gaps = 0, []
    for row in inventory:
        if row["disposition"] != "git_export":
            continue
        path = row.get("export_path", row["path"])
        source = root / path
        expected = row.get("export_sha256", transformed.get(path, row["sha256"]))
        actual = hashlib.sha256(source.read_bytes()).hexdigest() if source.is_file() else None
        checked += 1
        if actual != expected:
            gaps.append({"path": path, "expected_sha256": expected, "actual_sha256": actual})
    print(json.dumps({"exported_files_checked": checked, "mismatches": gaps,
                      "cache_only_files": sum(r["disposition"] != "git_export" for r in inventory),
                      "scope": "Byte identity only; no scientific reanalysis."}, indent=2))
    return bool(gaps)


if __name__ == "__main__":
    raise SystemExit(main())
