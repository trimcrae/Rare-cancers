"""Check portable analytical bytes; this is not scientific reproduction."""
import argparse
import hashlib
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[3])
    parser.add_argument("--manifest", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    manifest = args.manifest or Path(__file__).with_name("PORTABLE-EXPORT.json")
    packet = json.loads(manifest.read_text())
    errors, seen, total = [], set(), 0
    for row in packet["files"]:
        relative = Path(row["path"])
        path = (root / relative).resolve()
        if relative.is_absolute() or not path.is_relative_to(root) or str(relative) in seen:
            errors.append({"path": str(relative), "error": "unsafe or duplicate path"})
            continue
        seen.add(str(relative))
        try:
            data = path.read_bytes()
            if len(data) != row["bytes"] or hashlib.sha256(data).hexdigest() != row["sha256"]:
                errors.append({"path": str(relative), "error": "byte identity differs"})
            if relative.suffix == ".json":
                json.loads(data)
            if relative.suffix == ".py":
                compile(data, str(relative), "exec")
            total += len(data)
        except (OSError, ValueError, SyntaxError) as exc:
            errors.append({"path": str(relative), "error": str(exc)})
    print(json.dumps({"files_checked": len(seen), "bytes": total, "errors": errors,
                      "scope": "Declared export byte equality, JSON parsing and Python syntax only; no raw-source recovery or scientific reproduction."}, indent=2))
    raise SystemExit(bool(errors))


if __name__ == "__main__":
    main()
