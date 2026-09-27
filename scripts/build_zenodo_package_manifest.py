#!/usr/bin/env python3
"""Build the named ASO data-only inventory from a committed source revision."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess

import zenodo_deposit as Z


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--revision", required=True, help="Exact committed payload revision")
    parser.add_argument("--doi", required=True, help="Actual existing published or reserved ASO version DOI")
    args = parser.parse_args()
    if not re.fullmatch(r"[0-9a-f]{40}", args.revision):
        parser.error("--revision must be an exact 40-character commit SHA")
    if not re.fullmatch(r"10\.5281/zenodo\.\d+", args.doi):
        parser.error("--doi must identify the actual ASO version")
    paths = subprocess.check_output(["git", "-C", Z.REPO, "ls-tree", "-r", "--name-only", args.revision], text=True).splitlines()
    files = []
    for relative in sorted(p for p in paths if Z.permitted_package_path(p)):
        data = Z._git_bytes(args.revision, relative)
        files.append({"path": relative, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()})
    required = {"LICENSE", Z.PACKAGE_ROOT + "/supplementary-methods.md",
                Z.PACKAGE_ROOT + "/repository-deposit/README.md", Z.PACKAGE_ROOT + "/evidence/analyze.py"}
    if not required <= {e["path"] for e in files}:
        raise SystemExit("Commit the complete payload and reproduction README before generating its manifest")
    manifest = {
        "_schema": "emc-zenodo-package-manifest/1",
        "_what_this_is": "Versioned computational inputs, attributable sequence references, junction provenance, 40 design rows (35 source-linked and five hypothetical controls), 77 normal-parent transcript records, exact match locations, sensitivity results and reproducible analysis. These are sequence comparisons, not evidence of cleavage, potency, safety or clinical benefit. Downloaded literature is linked through the source ledger, not republished in this archive.",
        "package": Z.PACKAGE_NAME, "git_revision": args.revision,
        "conceptrecid": "22028915", "deposition_doi": args.doi,
        "inventory_limited_to_tracked_files": True, "n_files": len(files),
        "files": files, "archive_content_digest": Z.content_digest(files),
        "how_to_reproduce_offline": [
            "Extract the ZIP while preserving its repository-relative directories.",
            "Enter research/release-candidates/PUB-ASO/2026-09-26/evidence and run python analyze.py using Python 3.11 or later. No external packages or network are required.",
            "Compare SHA-256 hashes for the eleven result files with this manifest; all should reproduce exactly.",
            "Read repository-deposit/README.md and supplementary-methods.md for source classes, limitations, licensing and the optional separate read-prefix replay."
        ]}
    paper = Z.package_configuration("aso", Z.PACKAGE_NAME)
    Z.validate_package_manifest(manifest, paper)
    Z.verify(manifest)
    path = Path(Z.REPO) / paper["manifest"]
    path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"path": paper["manifest"], "files": len(files), "payload_bytes": sum(e["bytes"] for e in files),
                      "archive_content_digest": manifest["archive_content_digest"], "source_revision": args.revision}))


if __name__ == "__main__":
    main()
