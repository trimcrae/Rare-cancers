"""Verify the immutable campaign packet; optionally extract to a new directory."""
import argparse
import hashlib
import io
import json
import shutil
import tarfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parent


def sha(data):
    return hashlib.sha256(data).hexdigest()


def verify_and_extract(destination=None):
    metadata = json.loads((ROOT / "archive-manifest.json").read_text(encoding="utf-8"))
    closing_bytes = (ROOT / "closing-manifest.json").read_bytes()
    closing = json.loads(closing_bytes)
    expected = {item["path"]: item for item in closing["files"]}
    if len(expected) != len(closing["files"]) or "closing-manifest.json" in expected:
        raise ValueError("Invalid original manifest member set")
    expected["closing-manifest.json"] = {
        "bytes": len(closing_bytes), "sha256": sha(closing_bytes)
    }
    data = (ROOT / "evidence-packet.tar.gz").read_bytes()
    if len(data) != metadata["archive_bytes"] or sha(data) != metadata["archive_sha256"]:
        raise ValueError("Archive size/hash mismatch")
    if sha(closing_bytes) != metadata["closing_manifest_sha256"]:
        raise ValueError("Original manifest hash mismatch")
    if len(expected) != metadata["member_count"]:
        raise ValueError("Member count mismatch")
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as archive:
        members = archive.getmembers()
        names = [member.name for member in members]
        if len(names) != len(set(names)) or set(names) != set(expected):
            raise ValueError("Archive member set mismatch or duplicate")
        total = 0
        for member in members:
            path = PurePosixPath(member.name)
            if (not member.isfile() or path.is_absolute() or ".." in path.parts
                    or "\\" in member.name or ":" in member.name):
                raise ValueError(f"Unsafe archive member: {member.name}")
            content = archive.extractfile(member).read()
            item = expected[member.name]
            if len(content) != item["bytes"] or sha(content) != item["sha256"]:
                raise ValueError(f"Original evidence mismatch: {member.name}")
            total += len(content)
        if total != metadata["uncompressed_bytes"]:
            raise ValueError("Uncompressed size mismatch")
        if destination is not None:
            destination = Path(destination).resolve()
            if destination.exists():
                raise ValueError("Extraction destination must not already exist")
            ancestor = destination.parent
            while not ancestor.exists():
                ancestor = ancestor.parent
            if shutil.disk_usage(ancestor).free - total < 10 * 1024**3:
                raise ValueError("Extraction would leave less than 10 GiB free")
            destination.mkdir(parents=True)
            archive.extractall(destination, members=members, filter="data")
    return {"status": "passed", "members_verified": len(expected),
            "uncompressed_bytes": total, "extracted_to": str(destination) if destination else None}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--extract", type=Path, help="New destination directory")
    arguments = parser.parse_args()
    print(json.dumps(verify_and_extract(arguments.extract), indent=2))
