"""Boundaries of the local runner; all child processes are local test programs."""
import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from unittest import mock

SOURCE = Path(__file__).resolve().parents[1] / "research_run.py"
SPEC = importlib.util.spec_from_file_location("research_run", SOURCE)
R = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(R)


class RunnerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)

    def repo(self):
        repo = self.directory / "repo"
        repo.mkdir()
        R.git(repo, "init", "-q")
        R.git(repo, "config", "user.email", "runner-test@example.invalid")
        R.git(repo, "config", "user.name", "Runner Test")
        path = repo / R.PROTOCOL
        path.parent.mkdir(parents=True)
        path.write_text("Complete only the assigned task.\n", encoding="utf-8")
        (repo / ".gitignore").write_text(".cache/\n", encoding="utf-8")
        R.git(repo, "add", R.PROTOCOL, ".gitignore")
        R.git(repo, "-c", "core.hooksPath=", "commit", "-qm", "fixture")
        return repo

    def test_api_environment_is_refused_without_echoing_value(self):
        for variable in R.API_ENV:
            with self.subTest(variable=variable), self.assertRaises(R.Refused) as error:
                R.subscription_environment({variable: "secret-that-must-not-leak"})
            self.assertNotIn("secret-that-must-not-leak", str(error.exception))

    def test_auth_requires_positive_chatgpt_status(self):
        for stdout, code, accepted in (("Logged in using ChatGPT", 0, True),
                                       ("Logged in using an API key", 0, False),
                                       ("unknown", 0, False), ("ChatGPT", 1, False)):
            result = subprocess.CompletedProcess([], code, stdout, "")
            with mock.patch.object(R.subprocess, "run", return_value=result):
                if accepted:
                    R.probe_auth("codex", {})
                else:
                    with self.assertRaises(R.Refused):
                        R.probe_auth("codex", {})

    def test_plan_is_read_only_and_does_not_probe_auth(self):
        repo = self.repo()
        with mock.patch.object(R, "probe_auth", side_effect=AssertionError("auth called")), \
                mock.patch.object(R, "run_process", side_effect=AssertionError("worker called")), \
                contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(R.main(["--repo", str(repo), "--plan"]), 0)
        self.assertFalse((repo / ".cache").exists())

    def test_launch_requires_cutover_before_auth_or_worktree(self):
        repo = self.repo()
        with mock.patch.object(R.shutil, "which", return_value="codex.exe"), \
                mock.patch.object(R, "probe_auth", side_effect=AssertionError("auth called")), \
                contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(R.main(["--repo", str(repo)]), 2)
        self.assertFalse((repo / ".cache").exists())

    def test_common_lock_is_shared_across_real_git_worktrees(self):
        repo = self.repo()
        worktree = self.directory / "sibling"
        R.git(repo, "worktree", "add", "--detach", str(worktree), "HEAD")
        self.assertEqual(R.repository(repo)[1], R.repository(worktree)[1])

    def test_os_lock_excludes_second_process_and_releases(self):
        lock = self.directory / "coordinator.lock"
        program = ("import importlib.util,sys; "
                   "s=importlib.util.spec_from_file_location('runner',sys.argv[1]); "
                   "m=importlib.util.module_from_spec(s); s.loader.exec_module(m); "
                   "m.LocalLock(sys.argv[2]).__enter__()")
        command = [sys.executable, "-c", program, str(SOURCE), str(lock)]
        with R.LocalLock(lock):
            denied = subprocess.run(command, capture_output=True, timeout=10)
            self.assertNotEqual(denied.returncode, 0)
            self.assertIn(b"coordinator lock", denied.stderr)
        allowed = subprocess.run(command, capture_output=True, timeout=10)
        self.assertEqual(allowed.returncode, 0, allowed.stderr)

    def test_timeout_stops_descendants(self):
        heartbeat = self.directory / "heartbeat.txt"
        child = self.directory / "child.py"
        child.write_text("import sys,time\nfrom pathlib import Path\np=Path(sys.argv[1])\n"
                         "while True:\n with p.open('a') as f:f.write('pulse\\n')\n time.sleep(.04)\n")
        program = ("import subprocess,sys,time; "
                   "subprocess.Popen([sys.executable,sys.argv[1],sys.argv[2]]); time.sleep(30)")
        with self.assertRaises(subprocess.TimeoutExpired):
            R.run_process([sys.executable, "-c", program, str(child), str(heartbeat)], "",
                          self.directory, self.directory / "out", self.directory / "err",
                          1.5, dict(os.environ))
        self.assertTrue(heartbeat.exists(), "Descendant did not start; test did not exercise containment")
        before = heartbeat.read_bytes()
        time.sleep(.2)
        self.assertEqual(heartbeat.read_bytes(), before, "Descendant survived parent timeout")

    def test_command_pins_subscription_model_sandbox_and_session(self):
        command = R.command_for("codex", Path("work"), Path("schema"), Path("out"), R.DEFAULTS, "my-id")
        self.assertIn(R.MODEL, command)
        self.assertIn('--ignore-user-config', command)
        self.assertIn('forced_login_method="chatgpt"', command)
        self.assertIn('features.multi_agent=false', command)
        self.assertIn("workspace-write", command)
        self.assertEqual(command[-3:], ["resume", "my-id", "-"])
        self.assertNotIn("--last", command)
        with mock.patch.object(R.os, "name", "nt"):
            windows_command = R.command_for("codex", "work", "schema", "out", R.DEFAULTS,
                                            read_only=True)
        self.assertIn('windows.sandbox="elevated"', windows_command)
        self.assertEqual(windows_command[windows_command.index("--sandbox") + 1], "read-only")
        self.assertIn('approval_policy="never"', windows_command)
        self.assertIn('--ignore-user-config', windows_command)

    def fake_launch(self, statuses, config=None, read_only=False):
        repo = self.repo()
        cache = R.repository(repo)[1]
        fake = self.directory / "fake_worker.py"
        fake.write_text("import json,sys\nfrom pathlib import Path\n"
                        "sys.stdin.read()\n"
                        "outcome={'status':sys.argv[2],'summary':'fixture','artifacts':[],"
                        "'checks':[],'blockers':[] if sys.argv[2]=='completed' else ['fixture blocker']}\n"
                        "Path(sys.argv[1]).write_text(json.dumps(outcome))\n"
                        "print(json.dumps({'type':'thread.started','thread_id':'explicit-fixture-id'}))\n"
                        "print(json.dumps({'type':'turn.completed','usage':{'input_tokens':1}}))\n")
        sessions = []

        def command(codex, worktree, schema, outcome, settings, session=None, read_only=False):
            sessions.append(session)
            return [sys.executable, str(fake), str(outcome), statuses[len(sessions) - 1]]

        with mock.patch.object(R, "probe_auth"), mock.patch.object(R, "command_for", side_effect=command):
            path, receipt = R.launch(repo, cache, "fixture", config or R.DEFAULTS,
                                     "Create a fixture.", "paper:PUB-ASO", dict(os.environ), read_only)
        self.assertEqual(json.loads(path.read_text())["status"], receipt["status"])
        self.assertEqual(R.git(repo, "status", "--porcelain", "--untracked-files=no"), "")
        self.assertEqual(len((cache / "runs.jsonl").read_text().splitlines()), 1)
        return receipt, sessions

    def test_bounded_success_retains_worktree_and_receipt(self):
        receipt, _ = self.fake_launch(["completed"])
        self.assertEqual(receipt["status"], "completed")
        self.assertTrue(Path(receipt["worktree"]).is_dir())
        self.assertEqual(receipt["rounds"][0]["usage"], [{"input_tokens": 1}])

    def test_dispatch_budget_stops_incomplete_task_without_claiming_readiness(self):
        receipt, sessions = self.fake_launch(["needs_revision"],
                                             {**R.DEFAULTS, "max_rounds": 2, "max_dispatches": 1})
        self.assertEqual(receipt["status"], "budget_exhausted")
        self.assertEqual(len(sessions), 1)

    def test_one_repair_resumes_only_explicit_session(self):
        receipt, sessions = self.fake_launch(["needs_revision", "completed"],
                                             {**R.DEFAULTS, "max_rounds": 2, "max_dispatches": 2})
        self.assertEqual(receipt["status"], "completed")
        self.assertEqual(sessions, [None, "explicit-fixture-id"])

    def test_read_only_audit_is_bounded_and_does_not_claim_cutover(self):
        receipt, sessions = self.fake_launch(["needs_revision"],
                                             {**R.DEFAULTS, "max_rounds": 2, "max_dispatches": 2}, True)
        self.assertFalse(receipt["legacy_and_remote_writers_stopped_acknowledged"])
        self.assertEqual(receipt["mode"], "read-only")
        self.assertEqual(len(sessions), 1)
        command = R.command_for("codex", Path("work"), Path("schema"), Path("out"), R.DEFAULTS,
                                read_only=True)
        self.assertEqual(command[command.index("--sandbox") + 1], "read-only")

    def test_completed_with_blockers_is_rejected(self):
        path = self.directory / "outcome.json"
        path.write_text(json.dumps({"status": "completed", "summary": "test", "artifacts": [],
                                    "checks": [], "blockers": ["unresolved"]}))
        with self.assertRaises(R.Refused):
            R.read_outcome(path)

    def test_limits_cannot_be_unbounded_or_wrong_types(self):
        for key, value in (("max_rounds", 3), ("max_dispatches", 0),
                           ("timeout_seconds", True), ("timeout_seconds", 7201)):
            path = self.directory / "config.json"
            path.write_text(json.dumps({key: value}))
            with self.subTest(key=key, value=value), self.assertRaises(R.Refused):
                R.settings(path)


if __name__ == "__main__":
    unittest.main()
