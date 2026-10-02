#!/usr/bin/env python3
"""Offline CI verdict behavior; synthetic API responses, real production poll.

The pinned original is loaded from Git for one exact false-green witness. All
poll calls replace API reads and time; no provider or GitHub HTTP call is made.
These are operational checks, not scientific tests or publication evidence.
"""
from __future__ import annotations

import contextlib
import hashlib
import io
from pathlib import Path
import subprocess
import sys
import types
import unittest
from unittest import mock

AUTONOMY = Path(__file__).resolve().parents[1]
REPO = AUTONOMY.parents[1]
sys.path.insert(0, str(AUTONOMY))
import await_ci  # noqa: E402

BASE = "184e6aff659180492f4df94ed46a222849ab1b7c"
SOURCE = "research/autonomy/await_ci.py"
ORIGINAL_BLOB = "121bb8798debff50e207a14e50aa5aae162f3d0e"
SHA = "1" * 40


def run(conclusion="success", status="completed"):
    return {"name": "synthetic offline workflow", "status": status,
            "conclusion": conclusion, "head_sha": SHA}


def observe(module, responses, *, require=1, deadline=2, quiet=False):
    """A deterministic finite clock and API replacement, never a live poll."""
    calls = []
    sleeps = []
    clock = [0]
    replies = list(responses)

    def fake_get(url, token, timeout=25):
        calls.append((url, token, timeout))
        # Repeat the last response for deadline/minimum-count controls.
        return replies[min(len(calls) - 1, len(replies) - 1)]

    def sleep(seconds):
        sleeps.append(seconds)
        clock[0] += seconds

    fake_time = types.SimpleNamespace(monotonic=lambda: clock[0], sleep=sleep)
    output = io.StringIO()
    with mock.patch.object(module, "_get", fake_get), \
            mock.patch.object(module, "time", fake_time), \
            contextlib.redirect_stdout(output):
        code = module.poll("fixture/repo", SHA, deadline, 1, None,
                           require=require, quiet=quiet)
    return code, output.getvalue(), calls, sleeps


class TerminalVerdictTests(unittest.TestCase):
    def checked(self, runs, expected, *, quiet=False):
        code, output, calls, sleeps = observe(
            await_ci, [{"workflow_runs": runs}], quiet=quiet)
        self.assertEqual(code, expected, output)
        self.assertEqual(len(calls), 1, output)
        self.assertEqual(sleeps, [])
        self.assertEqual("CI decided GREEN" in output, expected == 0, output)
        return output

    def test_exact_original_cancelled_false_green_witness(self):
        # Retained scenario family: test_exact_original_cancelled_false_green_witness
        raw = subprocess.check_output(["git", "show", f"{BASE}:{SOURCE}"], cwd=REPO)
        blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
        self.assertEqual(blob, ORIGINAL_BLOB)
        baseline = types.ModuleType("baseline_await_ci")
        baseline.__file__ = str(AUTONOMY / "await_ci.py")
        exec(compile(raw, f"{BASE}:{SOURCE}", "exec"), baseline.__dict__)
        code, output, calls, sleeps = observe(
            baseline, [{"workflow_runs": [run("cancelled")]}])
        self.assertEqual(code, 0, output)
        self.assertIn("CI decided GREEN", output)
        self.assertIn("not evidence of green", output)
        self.assertEqual(len(calls), 1)
        self.assertEqual(sleeps, [])
        print(f"PINNED_BASELINE_FALSE_GREEN base={BASE} blob={blob} "
              "conclusion=cancelled exit=0; mocked API/time, no HTTP")

    def test_positive_and_terminal_single_inventory_verdicts(self):
        # Retained scenario family: test_current_success_and_neutral_controls
        for conclusions in (["success"], ["neutral"], ["success", "neutral"]):
            with self.subTest(conclusions=conclusions):
                self.checked([run(c) for c in conclusions], 0)

        # Retained scenario family: test_terminal_no_verdict_is_unknown
        for conclusion in ("cancelled", "skipped", "new_unknown_conclusion", ""):
            with self.subTest(conclusion=conclusion):
                output = self.checked([run(conclusion)], 2)
                self.assertIn("UNKNOWN", output)

        # Retained scenario family: test_multiple_cancelled_and_skipped_runs_are_unknown
        for conclusions in (["cancelled", "cancelled"], ["skipped", "skipped"],
                            ["cancelled", "skipped"]):
            with self.subTest(conclusions=conclusions):
                self.checked([run(c) for c in conclusions], 2)

        # Retained scenario family: test_quiet_still_reports_terminal_unknown
        output = self.checked([run("cancelled")], 2, quiet=True)
        self.assertIn("UNKNOWN", output)
        self.assertNotIn("still going", output)

    def test_positive_runs_cannot_hide_terminal_nonverdicts(self):
        # Retained scenario family: test_success_does_not_hide_a_terminal_no_verdict
        for conclusion in ("cancelled", "skipped", "new_unknown_conclusion", ""):
            for reverse in (False, True):
                with self.subTest(conclusion=conclusion, reverse=reverse):
                    runs = [run("success"), run(conclusion)]
                    self.checked(list(reversed(runs)) if reverse else runs, 2)

        # Retained scenario family: test_neutral_does_not_hide_cancelled_or_skipped
        for conclusion in ("cancelled", "skipped"):
            with self.subTest(conclusion=conclusion):
                self.checked([run("neutral"), run(conclusion)], 2)

    def test_red_precedence_is_preserved(self):
        # Retained scenario family: test_red_precedence_is_preserved
        for conclusion in sorted(await_ci.RED):
            for other in (None, "cancelled", "success"):
                with self.subTest(conclusion=conclusion, other=other):
                    runs = [run(conclusion)]
                    if other is not None:
                        runs.append(run(other))
                    output = self.checked(runs, 1)
                    self.assertIn("RED", output)

    def test_pending_or_missing_inventory_has_no_green_verdict(self):
        # Retained scenario family: test_unfinished_statuses_and_null_conclusion_wait_then_timeout
        cases = [(status, "success") for status in
                 ("queued", "in_progress", "waiting", "requested", "pending")]
        cases.append(("completed", None))
        for status, conclusion in cases:
            with self.subTest(status=status, conclusion=conclusion):
                code, output, calls, sleeps = observe(
                    await_ci, [{"workflow_runs": [run(conclusion, status)]}])
                self.assertEqual(code, 2, output)
                self.assertGreater(len(calls), 1)
                self.assertTrue(sleeps)
                self.assertNotIn("CI decided GREEN", output)

        # Retained scenario family: test_empty_or_missing_inventory_is_not_green
        for response in ({"workflow_runs": []}, {}):
            with self.subTest(response=response):
                code, output, calls, sleeps = observe(await_ci, [response])
                self.assertEqual(code, 2, output)
                self.assertGreater(len(calls), 1)
                self.assertTrue(sleeps)
                self.assertNotIn("CI decided GREEN", output)

    def test_waiting_ends_with_the_observed_terminal_verdict(self):
        # Retained scenario family: test_waiting_can_then_reach_a_measured_success
        replies = [{"workflow_runs": []},
                   {"workflow_runs": [run(None, "in_progress")]},
                   {"workflow_runs": [run("success")]}]
        code, output, calls, sleeps = observe(await_ci, replies, deadline=4)
        self.assertEqual(code, 0, output)
        self.assertEqual(len(calls), 3)
        self.assertEqual(sleeps, [1, 1])

        # Retained scenario family: test_terminal_unknown_after_wait_is_not_green
        code, output, calls, sleeps = observe(
            await_ci, [{"workflow_runs": [run(None, "in_progress")]},
                       {"workflow_runs": [run("cancelled")]}])
        self.assertEqual(code, 2, output)
        self.assertEqual(len(calls), 2)
        self.assertEqual(sleeps, [1])
        self.assertIn("UNKNOWN", output)
        self.assertNotIn("CI decided GREEN", output)

    def test_minimum_inventory_count_remains_enforced(self):
        # Retained scenario family: test_minimum_inventory_count_remains_enforced
        code, output, calls, sleeps = observe(
            await_ci, [{"workflow_runs": [run("success")]}], require=2)
        self.assertEqual(code, 2, output)
        self.assertGreater(len(calls), 1)
        self.assertTrue(sleeps)
        self.assertNotIn("CI decided GREEN", output)
        code, output, calls, sleeps = observe(
            await_ci, [{"workflow_runs": [run("success"), run("neutral")]}], require=2)
        self.assertEqual(code, 0, output)
        self.assertEqual(len(calls), 1)
        self.assertEqual(sleeps, [])

    def test_mixed_pending_and_red_keeps_existing_waiting_behavior(self):
        # Retained scenario family: test_mixed_pending_and_red_keeps_existing_waiting_behavior
        code, output, calls, sleeps = observe(
            await_ci, [{"workflow_runs": [run("failure"), run(None, "in_progress")]}])
        self.assertEqual(code, 2, output)
        self.assertGreater(len(calls), 1)
        self.assertTrue(sleeps)
        self.assertNotIn("CI decided GREEN", output)



if __name__ == "__main__":
    unittest.main(verbosity=2)
