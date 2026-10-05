"""Check explicitly exported bytes; this is not scientific reproduction."""
from pathlib import Path
import hashlib
import json


def main():
    root = Path(__file__).resolve().parent
    manifest = json.loads((root / "PORTABLE-EXPORT.json").read_text())
    total = 0
    for row in manifest["files"]:
        target = (root / row["path"]).resolve()
        if not target.is_relative_to(root):
            raise ValueError("Export path escapes checkpoint")
        body = target.read_bytes()
        if len(body) != row["bytes"]:
            raise ValueError("Size mismatch: " + row["path"])
        if hashlib.sha256(body).hexdigest() != row["sha256"]:
            raise ValueError("Hash mismatch: " + row["path"])
        total += len(body)
    print(json.dumps({"files_verified": len(manifest["files"]),
                      "bytes_verified": total,
                      "scope": "Declared analytical export integrity only; "
                               "no recovery of ignored originals, scientific "
                               "replication or source-coverage completion implied."}))


if __name__ == "__main__":
    main()
