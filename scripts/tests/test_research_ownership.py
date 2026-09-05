"""Execution boundaries for manual, scheduled and legacy owners; no model calls."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

SOURCE = Path(__file__).resolve().parents[1] / "research_run.py"
SPEC = importlib.util.spec_from_file_location("ownership_runner", SOURCE)
R = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(R)
import claim as C


class OwnershipTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.repo = self.directory / "repo"
        self.repo.mkdir()
        R.git(self.repo, "init", "-q", "-b", "main")
        R.git(self.repo, "config", "user.email", "ownership-test@example.invalid")
        R.git(self.repo, "config", "user.name", "Ownership Test")
        autonomy = self.repo / "research/autonomy"
        autonomy.mkdir(parents=True)
        (autonomy / "OPERATING_PROTOCOL.md").write_text("Fixture protocol")
        (autonomy / "codex-handover.json").write_text(json.dumps({"legacy_driver": {"status": "disabled"}}))
        (autonomy / "research-ledger.json").write_text(json.dumps({"entries": []}))
        (self.repo / ".gitignore").write_text(".cache/\n")
        R.git(self.repo, "add", ".")
        R.git(self.repo, "-c", "core.hooksPath=", "commit", "-qm", "fixture")
        self.cache = R.repository(self.repo)[1]

    def coordinator(self, owner="first"):
        with R.Coordinator(self.repo, self.cache) as state:
            state.claim(owner, "Test driver disabled and drained")

    def test_durable_identity_cannot_be_stolen_after_os_lock_released(self):
        self.coordinator()
        with R.Coordinator(self.repo, self.cache) as state:
            with self.assertRaises(R.Refused):
                state.claim("second", "No")
            state.handoff("first", "second", "First coordinator stopped; all output retained")
        with R.Coordinator(self.repo, self.cache) as state:
            with self.assertRaises(R.Refused):
                state.require("first")
            state.require("second")
            self.assertEqual(state.state["history"][-1]["action"], "handoff_coordinator")

    def test_legacy_owner_prevents_cutover_and_cannot_be_silently_expired(self):
        path = self.repo / "research/autonomy/research-ledger.json"
        path.write_text(json.dumps({"entries": [{"id": "old", "owner": "legacy", "claimed_utc": "2000-01-01T00:00:00Z"}]}))
        with R.Coordinator(self.repo, self.cache) as state, self.assertRaisesRegex(R.Refused, "Outstanding legacy"):
            state.claim("first", "Calendar age is not release evidence")

    def test_manual_writers_need_distinct_worktrees_and_resources(self):
        self.coordinator()
        work = self.directory / "worker"
        R.git(self.repo, "worktree", "add", "--detach", str(work), "HEAD")
        with R.Coordinator(self.repo, self.cache) as state:
            with self.assertRaisesRegex(R.Refused, "separate worktree"):
                state.reserve("first", "paper:A", "writer", self.repo)
            state.reserve("first", "paper:A", "writer", work)
            with self.assertRaisesRegex(R.Refused, "remains owned"):
                state.reserve("first", "paper:A", "second", work)
            with self.assertRaisesRegex(R.Refused, "already owns this worktree"):
                state.reserve("first", "process:CI", "second", work)
            with self.assertRaisesRegex(R.Refused, "Unresolved resource"):
                state.release("first", "Cannot forget retained writer")

    def test_completed_output_blocks_duplicate_dispatch_before_authentication(self):
        self.coordinator()
        with R.Coordinator(self.repo, self.cache) as state:
            state.reserve("first", "paper:A", "completed-worker")
        with mock.patch.object(R, "probe_auth", side_effect=AssertionError("Model authentication reached")), \
                self.assertRaisesRegex(R.Refused, "unresolved retained output"):
            R.launch(self.repo, self.cache, "unused", R.DEFAULTS, "Duplicate", "paper:A", {}, coordinator_id="first")

    def test_idle_owner_rechecks_legacy_handover_before_next_dispatch(self):
        self.coordinator()
        handover = self.repo / "research/autonomy/codex-handover.json"
        handover.write_text(json.dumps({"legacy_driver": {"status": "active"}}))
        with mock.patch.object(R, "probe_auth", side_effect=AssertionError("Authentication reached")), \
                self.assertRaisesRegex(R.Refused, "does not say the legacy driver is disabled"):
            R.launch(self.repo, self.cache, "unused", R.DEFAULTS, "Test", "paper:A", {},
                     coordinator_id="first", task_contract={"resource": "paper:A", "kind": "science"})

    def test_writing_contract_is_required_and_review_refusal_precedes_dispatch(self):
        self.coordinator()
        with self.assertRaisesRegex(R.Refused, "task-contract"):
            R.launch(self.repo, self.cache, "unused", R.DEFAULTS, "Test", "paper:A", {}, coordinator_id="first")
        import bounded_review
        with mock.patch.object(bounded_review, "task_review_decision", return_value={"allowed": False, "reason": "Frozen evidence already matches"}), \
                mock.patch.object(R, "probe_auth", side_effect=AssertionError("Authentication reached")), \
                self.assertRaisesRegex(R.Refused, "Frozen evidence"):
            R.launch(self.repo, self.cache, "unused", R.DEFAULTS, "Review", "paper:A", {},
                     coordinator_id="first", task_contract={"resource": "paper:A", "kind": "science"})

    def test_contract_cannot_bypass_classification_with_arbitrary_or_mismatched_metadata(self):
        for contract in ({"x": 1}, {"kind": "science", "resource": "paper:OTHER"},
                         {"kind": "unrecognized", "resource": "paper:A"},
                         {"kind": "review", "resource": "paper:A"}):
            with self.subTest(contract=contract), self.assertRaises(R.Refused):
                R.validate_task_contract(contract, "paper:A")
        R.validate_task_contract({"kind": "review", "resource": "paper:A", "review_request": {}}, "paper:A")

    def test_authorized_authentication_failure_preserves_failed_receipt(self):
        self.coordinator()
        with mock.patch.object(R, "probe_auth", side_effect=R.Refused("Saved authentication unavailable")):
            path, receipt = R.launch(self.repo, self.cache, "unused", R.DEFAULTS, "Test", "process:test", {},
                                     coordinator_id="first", task_contract={"resource": "process:test", "kind": "maintenance"})
        self.assertEqual(receipt["status"], "failed")
        self.assertEqual(json.loads(path.read_text())["error"], "Saved authentication unavailable")
        self.assertFalse(Path(receipt["worktree"]).exists())
        self.assertEqual(R.Coordinator.read(self.cache)["resources"]["process:test"]["status"], "failed")

    def test_killed_owner_recovers_retained_output_without_redispatch(self):
        self.coordinator()
        program = self.directory / "interrupted.py"
        program.write_text(
            "import importlib.util,json,sys,time\nfrom pathlib import Path\n"
            "s=importlib.util.spec_from_file_location('runner',sys.argv[1]);r=importlib.util.module_from_spec(s);s.loader.exec_module(r)\n"
            "root,cache=r.repository(sys.argv[2])\n"
            "with r.Coordinator(root,cache) as o:\n"
            " d=cache/'interrupted';d.mkdir();p=d/'receipt.json'\n"
            " (d/'partial.txt').write_text('useful partial result')\n"
            " o.reserve('first','paper:A','crashed',receipt=p)\n"
            " r.write_json(p,{'status':'running','worktree':str(d),'rounds':[]})\n"
            " print('ready',flush=True)\n time.sleep(60)\n")
        process = subprocess.Popen([sys.executable, str(program), str(SOURCE), str(self.repo)],
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        try:
            self.assertEqual(process.stdout.readline().strip(), "ready")
            with self.assertRaisesRegex(R.Refused, "coordinator lock"):
                with R.Coordinator(self.repo, self.cache):
                    pass
            process.kill()
            process.communicate(timeout=10)
        finally:
            if process.poll() is None:
                process.kill()
                process.communicate(timeout=10)
        with R.Coordinator(self.repo, self.cache) as state:
            self.assertEqual(state.recover("first"), ["paper:A"])
            self.assertEqual(state.state["resources"]["paper:A"]["status"], "interrupted")
            with self.assertRaises(R.Refused):
                state.reserve("first", "paper:A", "duplicate")
            self.assertEqual((self.cache / "interrupted/partial.txt").read_text(), "useful partial result")
            evidence = self.directory / "resolution.md"
            evidence.write_text("Inspected retained partial result; abandon this synthetic fixture.")
            state.release_resource("first", "paper:A", "abandoned", evidence)
            self.assertEqual(state.state["history"][-1]["evidence_sha256"], R.hashlib.sha256(evidence.read_bytes()).hexdigest())
            state.reserve("first", "paper:A", "replacement")
        self.assertTrue((self.cache / "interrupted/partial.txt").exists())

    def test_corrupt_durable_state_fails_closed(self):
        self.cache.mkdir(parents=True)
        (self.cache / "coordinator.json").write_text("{interrupted write")
        with self.assertRaises(R.Refused):
            with R.Coordinator(self.repo, self.cache):
                pass
        with R.LocalLock(self.cache / "coordinator.lock"):
            pass  # Failed state read did not leak the OS lock.

    def test_artifact_inventory_binds_untracked_files_and_deletions(self):
        (self.repo / "new.txt").write_text("measured")
        (self.repo / R.PROTOCOL).unlink()
        inventory = R.artifact_inventory(self.repo, {"artifacts": ["new.txt"]})
        by_path = {row["path"]: row for row in inventory}
        self.assertTrue(by_path[R.PROTOCOL]["deleted"])
        self.assertEqual(by_path["new.txt"]["sha256"], R.hashlib.sha256(b"measured").hexdigest())
        for name in ("missing.txt", "../elsewhere.txt"):
            with self.assertRaises(R.Refused):
                R.artifact_inventory(self.repo, {"artifacts": [name]})

    def test_local_legacy_claim_is_refused_before_remote_contact(self):
        self.coordinator()
        git = C.Git(str(self.repo))
        with mock.patch.object(git, "fetch", side_effect=AssertionError("Contacted remote")):
            verdict, reason = C.claim("row", "legacy", "2026-09-05T00:00:00Z", git,
                                      str(self.repo / "research/autonomy/research-ledger.json"))
        self.assertEqual(verdict, C.SUSPENDED)
        self.assertIn("first", reason)

    def test_other_clone_reads_disabled_handover_before_claim_push(self):
        remote = self.directory / "remote.git"
        R.git(self.directory, "clone", "--bare", str(self.repo), str(remote))
        worker = self.directory / "legacy"
        R.git(self.directory, "clone", str(remote), str(worker))
        before = R.git(remote, "rev-parse", "HEAD")
        verdict, reason = C.claim("row", "legacy", "2026-09-05T00:00:00Z", C.Git(str(worker)),
                                  str(worker / "research/autonomy/research-ledger.json"))
        self.assertEqual(verdict, C.SUSPENDED)
        self.assertIn("disables the legacy driver", reason)
        self.assertEqual(R.git(remote, "rev-parse", "HEAD"), before)

    def test_legacy_claim_rechecks_cutover_after_its_next_fetch(self):
        git = mock.Mock(spec=C.Git)
        git.commits_not_on_trunk.return_value = []
        git.staged_paths.return_value = []
        with mock.patch.object(C, "legacy_handover_refusal", side_effect=[None, "Driver disabled during claim"]):
            verdict, reason = C._claim("row", "legacy", "2026-09-05T00:00:00Z", git,
                                       str(self.repo / "research/autonomy/research-ledger.json"))
        self.assertEqual(verdict, C.SUSPENDED)
        self.assertEqual(git.fetch.call_count, 2)
        git.push.assert_not_called()
        self.assertIn("during claim", reason)

    def test_two_legacy_rows_for_one_paper_cannot_be_two_writer_slots(self):
        rows = [{"id": "first", "owner": "writer", "state": "in_progress", "serves": {"publication": "PUB-ASO"}},
                {"id": "second", "owner": None, "state": "queued", "serves": {"publication": "PUB-ASO"}}]
        self.assertEqual(C.decide({"entries": rows}, "second", "different-writer")[0], C.YIELDED)
        rows[1]["serves"]["publication"] = "PUB-OTHER"
        self.assertEqual(C.decide({"entries": rows}, "second", "different-writer")[0], C.TAKEN)

    def test_withdrawal_preserves_original_newline_bytes(self):
        path = self.directory / "ledger.json"
        for original in ('{"entries": []}\n', '{"entries": []}\r\n'):
            with self.subTest(original=repr(original)):
                C.withdraw_claim(str(path), original)
                self.assertEqual(path.read_bytes(), original.encode("utf-8"))


if __name__ == "__main__":
    unittest.main()
