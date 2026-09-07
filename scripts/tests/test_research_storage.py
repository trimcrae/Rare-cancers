"""Storage refusal and sparse worktree isolation using real, tiny Git repositories."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import time
import unittest
from unittest import mock

SOURCE = Path(__file__).resolve().parents[1] / "research_run.py"
SPEC = importlib.util.spec_from_file_location("storage_runner", SOURCE)
R = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(R)


class StorageTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.directory = Path(temporary.name)
        self.repo = self.directory / "repo"
        self.repo.mkdir()
        R.git(self.repo, "init", "-q")
        R.git(self.repo, "config", "user.email", "storage-test@example.invalid")
        R.git(self.repo, "config", "user.name", "Storage Test")
        R.git(self.repo, "config", "core.autocrlf", "false")
        self.contents = {
            ".gitignore": b".cache/\n",
            "AGENTS.md": b"Fixture instructions.\n",
            "research/README.md": b"Ancestor file included by cone mode.\n",
            R.PROTOCOL: b"Fixture protocol.\n",
            "research/autonomy/codex-handover.json": b'{"legacy_driver":{"status":"disabled"}}',
            "research/autonomy/tests/input.txt": b"Selected test input.\n",
            "research/autonomy/other/input.txt": b"Excluded sibling directory.\n",
            "scripts/example.py": b"print('fixture')\n",
            "results/unrelated.bin": b"x" * (2 * 1024 ** 2),
        }
        for name, contents in self.contents.items():
            path = self.repo / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(contents)
        R.git(self.repo, "add", ".")
        R.git(self.repo, "-c", "core.hooksPath=", "commit", "-qm", "fixture")
        self.base = R.git(self.repo, "rev-parse", "HEAD")
        self.cache = R.repository(self.repo)[1]
        self.disk = mock.patch.object(R.shutil, "disk_usage", return_value=mock.Mock(free=100 * 1024 ** 3))
        self.disk_probe = self.disk.start()
        self.addCleanup(self.disk.stop)

    def test_sparse_checkout_matches_estimate_without_materializing_other_inputs(self):
        # Establish an independently scoped sibling before creating another tree.
        sibling = self.directory / "sibling"
        R.prepare_worktree(self.repo, sibling, self.base, ["scripts"], time.monotonic() + 30)
        sibling_scope = R.git(sibling, "sparse-checkout", "list")
        source_index = Path(R.git(self.repo, "rev-parse", "--git-path", "index"))
        if not source_index.is_absolute():
            source_index = self.repo / source_index
        index_before = source_index.read_bytes()
        worktree = self.directory / "selected"
        storage = R.checkout_storage(self.repo, self.cache, self.base, ["research/autonomy/tests"])
        actual_git = R.git

        def checked_git(repo, *args, **kwargs):
            output = actual_git(repo, *args, **kwargs)
            if worktree.exists():
                self.assertFalse((worktree / "results/unrelated.bin").exists())
            return output

        with mock.patch.object(R, "git", side_effect=checked_git):
            R.prepare_worktree(self.repo, worktree, self.base, storage["sparse_directories"],
                               time.monotonic() + 30)
        expected = {".gitignore", "AGENTS.md", "research/README.md", R.PROTOCOL,
                    "research/autonomy/codex-handover.json", "research/autonomy/tests/input.txt"}
        present = {name for name in self.contents if (worktree / name).is_file()}
        self.assertEqual(present, expected)
        self.assertEqual(storage["tracked_files"], len(expected))
        self.assertEqual(storage["estimated_checkout_bytes"],
                         sum((worktree / name).stat().st_size for name in present))
        self.assertEqual(source_index.read_bytes(), index_before)
        self.assertEqual(R.git(self.repo, "status", "--porcelain"), "")
        self.assertEqual(R.git(sibling, "status", "--porcelain"), "")
        self.assertEqual(R.git(sibling, "sparse-checkout", "list"), sibling_scope)
        self.assertTrue((sibling / "scripts/example.py").is_file())
        self.assertFalse((sibling / R.PROTOCOL).exists())

    def test_default_full_checkout_from_sparse_caller_stays_full(self):
        caller = self.directory / "sparse-caller"
        R.prepare_worktree(self.repo, caller, self.base, ["research/autonomy/tests"], time.monotonic() + 30)
        full = self.directory / "full"
        R.prepare_worktree(caller, full, self.base, [], time.monotonic() + 30)
        self.assertTrue(all((full / name).is_file() for name in self.contents))
        self.assertFalse((caller / "results/unrelated.bin").exists())
        storage = R.checkout_storage(caller, self.cache, self.base)
        self.assertEqual(storage["mode"], "full")
        self.assertEqual(storage["estimated_checkout_bytes"], sum(map(len, self.contents.values())))

    def test_low_disk_refuses_before_authentication_reservation_or_checkout(self):
        with R.Coordinator(self.repo, self.cache) as ownership:
            ownership.claim("fixture", "Synthetic repository; no running legacy driver")
        self.disk_probe.return_value.free = R.CHECKOUT_HEADROOM_BYTES
        with mock.patch.object(R, "probe_auth", side_effect=AssertionError("auth reached")), \
                mock.patch.object(R.Coordinator, "reserve", side_effect=AssertionError("reservation reached")), \
                mock.patch.object(R, "prepare_worktree", side_effect=AssertionError("checkout reached")), \
                mock.patch.object(R, "run_process", side_effect=AssertionError("worker reached")), \
                self.assertRaisesRegex(R.Refused, "10 GiB headroom"):
            R.launch(self.repo, self.cache, "unused", R.DEFAULTS, "Inspect fixture", "process:storage", {},
                     coordinator_id="fixture", task_contract={"resource": "process:storage", "kind": "maintenance"})
        self.assertEqual(R.Coordinator.read(self.cache)["resources"], {})
        self.assertFalse(any(path.is_dir() for path in self.cache.iterdir()))

    def test_plan_reports_repeated_scope_and_low_capacity_without_writing(self):
        self.disk_probe.return_value.free = 1
        output = io.StringIO()
        with contextlib.redirect_stdout(output), \
                mock.patch.object(R, "probe_auth", side_effect=AssertionError("auth reached")):
            code = R.main(["--repo", str(self.repo), "--plan", "--sparse-dir", "scripts",
                           "--sparse-dir", "research/autonomy/tests"])
        self.assertEqual(code, 0)
        storage = json.loads(output.getvalue())["storage"]
        self.assertEqual(storage["sparse_directories"], ["research/autonomy/tests", "scripts"])
        self.assertFalse(storage["capacity_available"])
        self.assertEqual(storage["required_free_bytes"],
                         storage["estimated_checkout_bytes"] + 10 * 1024 ** 3)
        self.assertFalse(self.cache.exists())

    def test_scope_rejects_traversal_absolute_untracked_and_file_paths(self):
        for name in ("../research", "/research", "C:\\repo", "research/../scripts", "research//autonomy",
                     "research\\..\\scripts", ".git", "missing", "scripts/example.py", "scripts\n", ""):
            with self.subTest(name=name), self.assertRaises(R.Refused):
                R.checkout_storage(self.repo, self.cache, self.base, [name])
        normalized = R.checkout_storage(self.repo, self.cache, self.base,
                                        ["research\\autonomy\\tests", "research/autonomy/tests/"])
        self.assertEqual(normalized["sparse_directories"], ["research/autonomy/tests"])

    def test_launch_receipt_records_scope_and_worker_reads_selected_files(self):
        def worker(command, prompt, cwd, stdout, stderr, timeout, env):
            self.assertIn('sparse checkout of these tracked input directories: ["research/autonomy/tests"]', prompt)
            self.assertIn("their absence is not evidence of absence from the repository", prompt)
            self.assertTrue((cwd / "research/autonomy/tests/input.txt").is_file())
            self.assertFalse((cwd / "results/unrelated.bin").exists())
            outcome = {"status": "completed", "summary": "Fixture inspected", "artifacts": [],
                       "checks": [], "blockers": [], "follow_up": []}
            Path(command[command.index("--output-last-message") + 1]).write_text(json.dumps(outcome))
            Path(stdout).write_text('{"type":"turn.completed","usage":{"input_tokens":1}}\n')
            Path(stderr).write_text("")
            return 0

        with mock.patch.object(R, "probe_auth"), mock.patch.object(R, "run_process", side_effect=worker):
            receipt_path, receipt = R.launch(self.repo, self.cache, "unused", R.DEFAULTS,
                                             "Inspect fixture", "process:storage", {}, read_only=True,
                                             sparse_dirs=["research/autonomy/tests"])
        self.assertEqual(receipt["status"], "completed")
        self.assertEqual(receipt["storage"]["sparse_directories"], ["research/autonomy/tests"])
        self.assertEqual(json.loads(receipt_path.read_text())["storage"], receipt["storage"])
        self.assertTrue(receipt["storage"]["capacity_available"])
        self.assertTrue(Path(receipt["worktree"]).is_dir(), "Completion must still retain output")


if __name__ == "__main__":
    unittest.main()
