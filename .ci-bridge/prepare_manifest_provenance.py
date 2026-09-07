#!/usr/bin/env python3
"""Prepare an unverified provenance-only candidate; never push or run tests.

Run ONLY in a separate, clean, detached, full-history Git worktree at the
public source commit S. The coordinator must separately authorize release CI.
All evidence lives outside this worktree except the dated correction receipt.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from datetime import datetime, timezone

EXPECTED_TREE = "98b79afe943fe7590e1d91c1a06b5b95a7b47ba9"
ORIGINAL_REVISION = "cf99d16fb773574a55ba55a3e61a2a90adeaff1a"
MANIFEST = "research/manuscripts/aso/fusion-junction-aso-archive-manifest.json"
MANIFEST_HASH = "a29906b9a3d2bba5fd9afcd262b937e33cd07f48ca44d839a8d0e194dbde0083"
GENERATOR = "research/manuscripts/aso_archive_manifest.py"
GENERATOR_HASH = "11767d142f812c536d6b887c61e94100b16912618e0f3555e157d9559e7cfa81"
DEPOSIT = "research/manuscripts/aso/deposit-state.json"
DEPOSIT_HASH = "c7a4df0c83c22e451cbf8dfc586020e06d6da01f31fa8063e3e1db73b98701ff"
ARCHIVE_DIGEST = "8710f8a2d02f926f00d09d5703e5bb51080ed1910a37f3efcd430693d3bec103"
RELEASE = "research/release-candidates/PUB-SURFACE-TARGETS/2026-09-06"
FROZEN = RELEASE + "/public-export/snapshot-independent-verification.json"
CORRECTION = RELEASE + "/public-export/aso-manifest-provenance-correction.json"
COMMIT_MESSAGE = "Regenerate development ASO manifest at verified public source"


def require(ok: bool, message: str) -> None:
    if not ok:
        raise RuntimeError(message)


def sha256(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value) -> None:
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True, type=Path)
    parser.add_argument("--source-sha", required=True)
    parser.add_argument("--source-ref", required=True,
                        help="Actual public staging refs/heads/... already resolving to S")
    parser.add_argument("--evidence-dir", required=True, type=Path)
    args = parser.parse_args()
    repo = args.repo.resolve(strict=True)
    evidence = args.evidence_dir.resolve()
    require(not evidence.is_relative_to(repo), "Evidence must be outside the source worktree")
    require(not evidence.exists(), "Evidence directory must be new; preserve previous attempts")
    require(re.fullmatch(r"[0-9a-f]{40}", args.source_sha) is not None, "S must be a full SHA")
    require(args.source_ref.startswith("refs/heads/"), "Source must be a real branch ref")
    require(not args.source_ref.startswith("refs/heads/codex/release/"),
            "S belongs on staging; this helper cannot authorize release dispatch")
    require(args.source_ref != "refs/heads/main", "Use a dedicated staging ref, not main")
    evidence.mkdir(parents=True)
    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "GIT_TERMINAL_PROMPT": "0"}
    commands = []

    def git(*parts: str, allow_failure=False) -> subprocess.CompletedProcess:
        cmd = ["git", "-C", str(repo), *parts]
        done = subprocess.run(cmd, capture_output=True, env=env)
        commands.append({"argv": cmd, "exit": done.returncode})
        if not allow_failure:
            require(done.returncode == 0,
                    f"Git failed ({done.returncode}): {' '.join(parts)}\n"
                    + done.stderr.decode("utf-8", "replace"))
        return done

    def text(*parts: str) -> str:
        return git(*parts).stdout.decode("utf-8").strip()

    def source_path(rel: str) -> Path:
        require(isinstance(rel, str) and rel and "\\" not in rel,
                "Invalid repository-relative input path")
        path = (repo / rel).resolve(strict=True)
        require(path.is_relative_to(repo), f"Input escapes worktree: {rel}")
        require(path.is_file(), f"Input is not a file: {rel}")
        return path

    def inventory(manifest) -> list:
        rows = manifest["files"]
        require(len(rows) == 516 and manifest["n_files"] == 516, "Expected all 516 inventory rows")
        require(len({row["path"] for row in rows}) == 516, "Duplicate inventory paths")
        actual = []
        for row in rows:
            path = source_path(row["path"])
            digest = sha256(path)
            require(digest == row["sha256"] and path.stat().st_size == row["bytes"],
                    f"Inventory bytes differ: {row['path']}")
            actual.append({"path": row["path"], "sha256": digest, "bytes": path.stat().st_size})
        acc = hashlib.sha256()
        for row in sorted(rows, key=lambda row: row["path"]):
            acc.update(f"{row['path']}\0{row['sha256']}\n".encode("utf-8"))
        require(acc.hexdigest() == ARCHIVE_DIGEST == manifest["archive_content_digest"],
                "Archive content digest changed")
        return actual

    def frozen_files() -> list:
        frozen = read_json(source_path(FROZEN))["outgoing"]
        require(len(frozen) == 8, "Expected exactly eight frozen outgoing artifacts")
        actual = []
        for rel, row in sorted(frozen.items()):
            path = source_path(rel)
            digest = sha256(path)
            require(digest == row["sha256"], f"Frozen output changed: {rel}")
            actual.append({"path": rel, "sha256": digest, "bytes": path.stat().st_size})
        return actual

    result = {"schema": "emc-provenance-repair-execution/1", "status": "not_started",
              "source_sha": args.source_sha, "source_ref": args.source_ref,
              "full_ci": "NOT RUN", "publication": "NOT PERFORMED"}
    try:
        require(text("rev-parse", "--show-toplevel") == str(repo), "repo must be worktree root")
        git_dir = Path(text("rev-parse", "--absolute-git-dir")).resolve()
        common = Path(text("rev-parse", "--path-format=absolute", "--git-common-dir")).resolve()
        require(git_dir != common, "Must use a separate linked Git worktree")
        require(git("symbolic-ref", "-q", "HEAD", allow_failure=True).returncode == 1,
                "Worktree HEAD must be detached; do not update any branch")
        require(text("rev-parse", "HEAD") == args.source_sha, "Checkout is not exact S")
        require(text("rev-parse", "HEAD^{tree}") == EXPECTED_TREE, "S tree is not frozen source tree")
        require(text("rev-parse", "--is-shallow-repository") == "false", "Full history is required")
        require(not text("status", "--porcelain", "--untracked-files=all"), "Source worktree is dirty")
        require(text("remote", "get-url", "origin").rstrip("/").removesuffix(".git")
                == "https://github.com/trimcrae/Rare-cancers", "Unexpected public origin")
        require(text("check-ref-format", args.source_ref) == "", "Invalid source ref")
        remote_line = text("ls-remote", "--exit-code", "origin", args.source_ref)
        require(remote_line == args.source_sha + "\t" + args.source_ref,
                "Public origin ref does not resolve exactly to S")
        tracking = "refs/remotes/origin/" + args.source_ref.removeprefix("refs/heads/")
        require(text("rev-parse", "--verify", tracking) == args.source_sha,
                "Fetch the real source staging ref before running; tracking ref must equal S")
        # Refuse active hooks instead of bypassing them or unexpectedly running tests.
        hook_path = git("config", "--get", "core.hooksPath", allow_failure=True)
        require(hook_path.returncode in (0, 1), "Could not inspect hook configuration")
        if hook_path.returncode == 0:
            hooks = Path(hook_path.stdout.decode().strip())
            if not hooks.is_absolute():
                hooks = repo / hooks
        else:
            hooks = Path(text("rev-parse", "--path-format=absolute", "--git-path", "hooks"))
        for name in ("pre-commit", "prepare-commit-msg", "commit-msg", "post-commit", "reference-transaction"):
            require(not ((hooks / name).exists() and os.access(hooks / name, os.X_OK)),
                    f"Active {name} hook: prepare runner without hooks; no bypass performed")
        require(not (repo / CORRECTION).exists(), "Correction receipt already exists")
        require(sha256(source_path(MANIFEST)) == MANIFEST_HASH, "Original manifest bytes differ")
        require(sha256(source_path(GENERATOR)) == GENERATOR_HASH, "Generator is not reviewed source")
        require(sha256(source_path(DEPOSIT)) == DEPOSIT_HASH, "Published deposit state changed")
        original = read_json(source_path(MANIFEST))
        require(original["git_revision"] == ORIGINAL_REVISION, "Original generation pin changed")
        require(original["git_tree_is_clean_apart_from_this_manifest"] is True,
                "Original manifest does not record clean committed inputs")
        inputs_before = inventory(original)
        outgoing_before = frozen_files()
        write_json(evidence / "inputs-before.json", inputs_before)
        write_json(evidence / "outgoing-before.json", outgoing_before)
        # Preserve exact bytes independently; original also remains committed at public S.
        (evidence / "original-manifest.json").write_bytes(source_path(MANIFEST).read_bytes())
        command = [sys.executable, "-B", GENERATOR]
        done = subprocess.run(command, cwd=repo, env=env, capture_output=True)
        (evidence / "generator.stdout.log").write_bytes(done.stdout)
        (evidence / "generator.stderr.log").write_bytes(done.stderr)
        require(done.returncode == 0, f"Existing generator failed: exit {done.returncode}")
        regenerated = read_json(source_path(MANIFEST))
        changed = sorted(k for k in original.keys() | regenerated.keys()
                         if original.get(k) != regenerated.get(k))
        require(changed == ["git_revision"], f"Unexpected changed manifest fields: {changed}")
        require(regenerated["git_revision"] == args.source_sha, "Generator did not name actual S")
        require(regenerated["files"] == original["files"], "Inventory rows changed")
        require(inventory(regenerated) == inputs_before, "Inventory content changed")
        require(frozen_files() == outgoing_before, "Outgoing artifacts changed")
        require(sha256(source_path(DEPOSIT)) == DEPOSIT_HASH, "Published deposit state changed")
        require(text("diff", "--name-only") == MANIFEST, "Generator changed another tracked file")
        require(not text("ls-files", "--others", "--exclude-standard"), "Generator created untracked files")
        receipt = {
            "schema": "emc-development-manifest-provenance-correction/1",
            "created_utc": datetime.now(timezone.utc).isoformat(),
            "reason": "Regenerate the moving development inventory at an actual public source commit. "
                      "The original generation event and immutable published deposit are preserved.",
            "original": {"manifest_sha256": MANIFEST_HASH, "generation_revision": ORIGINAL_REVISION,
                         "preserved_at": args.source_sha + ":" + MANIFEST,
                         "generation_record": RELEASE + "/archive-inventory-refresh.json"},
            "public_source": {"sha": args.source_sha, "tree": EXPECTED_TREE,
                              "origin": "https://github.com/trimcrae/Rare-cancers.git",
                              "ref": args.source_ref, "ls_remote": remote_line},
            "regeneration": {"command": command, "exit": done.returncode,
                             "generator_sha256": GENERATOR_HASH, "changed_fields": changed,
                             "manifest_sha256": sha256(source_path(MANIFEST)),
                             "stdout_sha256": hashlib.sha256(done.stdout).hexdigest(),
                             "stderr_sha256": hashlib.sha256(done.stderr).hexdigest()},
            "inventory": {"verified_files": 516, "rows_unchanged": True,
                          "archive_content_digest": ARCHIVE_DIGEST},
            "published_deposit_state_sha256": DEPOSIT_HASH,
            "unchanged_outgoing": outgoing_before,
            "validation_scope": "Generator and provenance/content checks only. No tests or full CI run. "
                                "The later correction commit is identified in external execution evidence.",
            "publication": "No paper or deposit publication; original private history was not exported."}
        write_json(repo / CORRECTION, receipt)
        git("add", "--", MANIFEST, CORRECTION)
        expected_paths = sorted([MANIFEST, CORRECTION])
        require(sorted(text("diff", "--cached", "--name-only").splitlines()) == expected_paths,
                "Index contains something other than the exact two authorized files")
        for rel in expected_paths:
            require(git("show", ":" + rel).stdout == source_path(rel).read_bytes(),
                    f"Index content differs from verified worktree bytes: {rel}")
        require(text("rev-parse", "HEAD") == args.source_sha, "HEAD moved before commit")
        git("commit", "-m", COMMIT_MESSAGE)
        candidate = text("rev-parse", "HEAD")
        require(text("rev-list", "--parents", "-n", "1", candidate)
                == candidate + " " + args.source_sha, "R must have exactly one parent S")
        require(sorted(text("diff-tree", "--no-commit-id", "--name-only", "-r", candidate).splitlines())
                == expected_paths, "R does not contain the exact two-file correction")
        for rel in expected_paths:
            require(git("show", candidate + ":" + rel).stdout == source_path(rel).read_bytes(),
                    f"Committed content differs from verified worktree bytes: {rel}")
        require(not text("status", "--porcelain", "--untracked-files=all"), "R checkout is dirty")
        require(inventory(read_json(source_path(MANIFEST))) == inputs_before, "Final inventory drift")
        require(frozen_files() == outgoing_before, "Final outgoing drift")
        require(sha256(source_path(DEPOSIT)) == DEPOSIT_HASH, "Final published deposit drift")
        result.update(status="prepared_unverified", candidate_sha=candidate,
                      candidate_tree=text("rev-parse", "HEAD^{tree}"), parent_sha=args.source_sha,
                      changed_paths=expected_paths, manifest_sha256=sha256(source_path(MANIFEST)),
                      correction_sha256=sha256(source_path(CORRECTION)),
                      outgoing=outgoing_before, archive_content_digest=ARCHIVE_DIGEST,
                      next="Independent candidate verification and coordinator-authorized full CI on R.")
    except Exception as exc:
        result.update(status="failed", error=str(exc),
                      recovery="No rollback or reset performed. Preserve this worktree and logs; "
                               "inspect actual state before any retry.")
    finally:
        write_json(evidence / "git-commands.json", commands)
        write_json(evidence / "result.json", result)
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "prepared_unverified" else 1


if __name__ == "__main__":
    raise SystemExit(main())
