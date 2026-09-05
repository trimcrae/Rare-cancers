#!/usr/bin/env python3
"""Run one bounded research task using local, subscription-authenticated Codex.

The existing OS lock serializes runners, ownership changes and local legacy
claims. Persistent coordinator/resource records retain ownership until output
is reconciled. Remote writers still require the recorded legacy-driver cutover.
Read-only audits may inspect a frozen checkout while legacy writers continue.
Receipts are operational records, never a manuscript-readiness verdict.
"""
from __future__ import annotations

import argparse
import contextlib
import ctypes
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
import time
import uuid
from datetime import datetime, timezone

MODEL = "gpt-6-astra"
PROTOCOL = "research/autonomy/OPERATING_PROTOCOL.md"
API_ENV = ("OPENAI_API_KEY", "CODEX_API_KEY", "AZURE_OPENAI_API_KEY",
           "OPENAI_BASE_URL", "OPENAI_API_BASE", "OPENAI_FEDERATION_RULE_ID",
           "CODEX_ACCESS_TOKEN")
DEFAULTS = {"timeout_seconds": 1800, "max_rounds": 1, "max_dispatches": 1,
            "reasoning_effort": "high"}
OUTCOME_SCHEMA = {
    "type": "object", "additionalProperties": False,
    "properties": {
        "status": {"type": "string", "enum": ["completed", "blocked", "needs_revision"],
                   "description": "Whether the assigned deliverable is complete, not whether later publication work is complete."},
        "summary": {"type": "string"},
        "artifacts": {"type": "array", "items": {"type": "string"}},
        "checks": {"type": "array", "items": {"type": "string"}},
        "blockers": {"type": "array", "items": {"type": "string"},
                     "description": "Unresolved issues preventing completion of this assigned task. Must be empty when status is completed."},
        "follow_up": {"type": "array", "items": {"type": "string"},
                      "description": "Work outside this task, such as later author approval, upload variants, or publication steps. These do not prevent task completion."},
    },
    "required": ["status", "summary", "artifacts", "checks", "blockers", "follow_up"],
}


# Keep sibling cycle validation available to direct Python callers as well as the CLI.
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "research/autonomy"))
from local_ownership import Coordinator, LocalLock, Refused, handover_disabled, utc_now, write_json


def git(repo, *arguments, timeout=30):
    result = subprocess.run(["git", "-c", "core.longpaths=true", *arguments],
                            cwd=repo, capture_output=True, text=True,
                            encoding="utf-8", errors="replace", timeout=timeout)
    if result.returncode:
        raise Refused(f"git {arguments[0]} failed: {result.stderr.strip()}")
    return result.stdout.strip()


def repository(repo):
    root = Path(git(repo, "rev-parse", "--show-toplevel")).resolve()
    common = Path(git(root, "rev-parse", "--path-format=absolute", "--git-common-dir")).resolve()
    return root, common.parent / ".cache" / "research-runs"


def settings(path):
    config = dict(DEFAULTS)
    if path:
        supplied = json.loads(Path(path).read_text(encoding="utf-8-sig"))
        if not isinstance(supplied, dict) or set(supplied) - set(DEFAULTS):
            raise Refused("Runner config contains unsupported fields.")
        config.update(supplied)
    return validate_settings(config)


def validate_settings(config):
    if set(config) != set(DEFAULTS):
        raise Refused("Runner config must contain the supported budget fields.")
    for key, maximum in (("timeout_seconds", 1800), ("max_rounds", 1), ("max_dispatches", 1)):
        if type(config[key]) is not int or not 1 <= config[key] <= maximum:
            raise Refused(f"{key} must be an integer from 1 to {maximum}.")
    if config["reasoning_effort"] not in ("low", "medium", "high", "xhigh", "max"):
        raise Refused("Unsupported Astra reasoning effort.")
    return config


def subscription_environment(env):
    present = [name for name in API_ENV if env.get(name)]
    if present:
        raise Refused("Subscription-only runner refuses alternate authentication/provider "
                      "environment variables: " + ", ".join(present) + ". Values were not read out.")


def probe_auth(codex, env):
    subscription_environment(env)
    result = subprocess.run([codex, "-c", 'forced_login_method="chatgpt"', "login", "status"],
                            env=env, capture_output=True, text=True,
                            encoding="utf-8", errors="replace", timeout=20)
    status = (result.stdout + result.stderr).lower()
    # Unknown/localized outputs fail closed. Never print login output: it may
    # contain a partial API key. This is an auth-status probe, not a model call.
    if result.returncode or "chatgpt" not in status or "api key" in status or "api_key" in status:
        raise Refused("Saved ChatGPT authentication could not be verified. Run codex login status "
                      "in the intended local account and sign in with ChatGPT before launching.")


class WindowsJob:
    """Kill the complete child tree when this handle closes, including on crash."""
    def __init__(self, process):
        from ctypes import wintypes

        class Basic(ctypes.Structure):
            _fields_ = [("PerProcessUserTimeLimit", ctypes.c_longlong),
                        ("PerJobUserTimeLimit", ctypes.c_longlong),
                        ("LimitFlags", wintypes.DWORD),
                        ("MinimumWorkingSetSize", ctypes.c_size_t),
                        ("MaximumWorkingSetSize", ctypes.c_size_t),
                        ("ActiveProcessLimit", wintypes.DWORD),
                        ("Affinity", ctypes.c_size_t), ("PriorityClass", wintypes.DWORD),
                        ("SchedulingClass", wintypes.DWORD)]

        class Counters(ctypes.Structure):
            _fields_ = [(name, ctypes.c_ulonglong) for name in
                        ("ReadOperationCount", "WriteOperationCount", "OtherOperationCount",
                         "ReadTransferCount", "WriteTransferCount", "OtherTransferCount")]

        class Extended(ctypes.Structure):
            _fields_ = [("BasicLimitInformation", Basic), ("IoInfo", Counters),
                        ("ProcessMemoryLimit", ctypes.c_size_t), ("JobMemoryLimit", ctypes.c_size_t),
                        ("PeakProcessMemoryUsed", ctypes.c_size_t),
                        ("PeakJobMemoryUsed", ctypes.c_size_t)]

        self.kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        self.kernel.CreateJobObjectW.argtypes = [ctypes.c_void_p, wintypes.LPCWSTR]
        self.kernel.CreateJobObjectW.restype = wintypes.HANDLE
        self.kernel.SetInformationJobObject.argtypes = [wintypes.HANDLE, ctypes.c_int,
                                                       ctypes.c_void_p, wintypes.DWORD]
        self.kernel.AssignProcessToJobObject.argtypes = [wintypes.HANDLE, wintypes.HANDLE]
        self.kernel.CloseHandle.argtypes = [wintypes.HANDLE]
        self.handle = self.kernel.CreateJobObjectW(None, None)
        limits = Extended()
        limits.BasicLimitInformation.LimitFlags = 0x2000  # JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
        if not self.handle or not self.kernel.SetInformationJobObject(
                self.handle, 9, ctypes.byref(limits), ctypes.sizeof(limits)):
            self.close()
            raise Refused("Could not create Windows child-process containment.")
        if not self.kernel.AssignProcessToJobObject(self.handle, int(process._handle)):
            self.close()
            raise Refused("Could not contain Windows child process; task was not started.")

    def close(self):
        if self.handle:
            self.kernel.CloseHandle(self.handle)
            self.handle = None


def run_process(command, prompt, cwd, stdout, stderr, timeout, env):
    """Contain descendants and drain output straight to durable files."""
    job = None
    if os.name == "nt":
        # Bootstrap waits for one byte BEFORE spawning Codex. Assign it to the
        # job first, eliminating the child-spawn-before-containment race.
        bootstrap = "import os,subprocess,sys;os.read(0,1);sys.exit(subprocess.call(sys.argv[1:]))"
        command = [sys.executable, "-c", bootstrap, *command]
    with Path(stdout).open("wb") as out, Path(stderr).open("wb") as err:
        process = subprocess.Popen(command, cwd=cwd, stdin=subprocess.PIPE,
                                   stdout=out, stderr=err, env=env,
                                   start_new_session=os.name != "nt")
        try:
            if os.name == "nt":
                job = WindowsJob(process)
            payload = ("\n" if os.name == "nt" else "") + prompt
            process.communicate(payload.encode("utf-8"), timeout=timeout)
            return process.returncode
        finally:
            if job:
                job.close()
            elif os.name != "nt":
                with contextlib.suppress(ProcessLookupError):
                    os.killpg(process.pid, signal.SIGKILL)
            elif process.poll() is None:
                # Containment setup failed while bootstrap was still waiting.
                process.kill()
            process.wait(timeout=10)


def read_outcome(path):
    result = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    if not isinstance(result, dict) or set(result) != set(OUTCOME_SCHEMA["required"]):
        raise Refused("Worker did not return the required structured outcome.")
    if result["status"] not in OUTCOME_SCHEMA["properties"]["status"]["enum"]:
        raise Refused("Worker returned an unknown outcome status.")
    if not isinstance(result["summary"], str):
        raise Refused("Worker summary must be text.")
    for field in ("artifacts", "checks", "blockers", "follow_up"):
        if not isinstance(result[field], list) or any(not isinstance(x, str) for x in result[field]):
            raise Refused(f"Worker {field} must be a list of strings.")
    if result["status"] == "completed" and result["blockers"]:
        raise Refused("Worker claimed completion while listing unresolved blockers.")
    return result


def artifact_inventory(worktree, outcome):
    """Bind claimed outputs and actual changed files to bytes retained for integration."""
    root = Path(worktree).resolve()
    paths = set(git(root, "diff", "--name-only", "HEAD").splitlines())
    paths.update(git(root, "ls-files", "--others", "--exclude-standard").splitlines())
    for name in outcome["artifacts"]:
        path = (root / name).resolve()
        if not path.is_relative_to(root) or not path.is_file():
            raise Refused(f"Worker artifact is not a retained file in its worktree: {name}")
        paths.add(path.relative_to(root).as_posix())
    result = []
    for name in sorted(paths):
        path = root / name
        if not path.resolve().is_relative_to(root):
            raise Refused(f"Output path escapes its retained worktree: {name}")
        result.append({"path": name, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()
                       if path.is_file() else None, "deleted": not path.exists()})
    return result


def event_summary(path):
    summary = {"session_id": None, "usage": [], "errors": 0}
    for line in Path(path).read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            item = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(item, dict):
            continue
        if item.get("type") == "thread.started":
            summary["session_id"] = item.get("thread_id")
        if item.get("type") == "turn.completed" and isinstance(item.get("usage"), dict):
            summary["usage"].append(item["usage"])
        if item.get("type") in ("error", "turn.failed"):
            summary["errors"] += 1
    return summary


def command_for(codex, worktree, schema, outcome, config, session_id=None, read_only=False):
    command = [codex, "exec", "--ignore-user-config", "--json", "--model", MODEL,
               "--sandbox", "read-only" if read_only else "workspace-write", "--output-schema", str(schema),
               "--output-last-message", str(outcome)]
    for setting in ('forced_login_method="chatgpt"', 'model_provider="openai"',
                    'approval_policy="never"', 'sandbox_workspace_write.network_access=false',
                    'features.multi_agent=false', 'agents.max_threads=1',
                    f'model_reasoning_effort="{config["reasoning_effort"]}"'):
        command += ["-c", setting]
    if os.name == "nt":
        # --ignore-user-config also omits the installed Windows sandbox mode.
        # Select the native elevated sandbox, without broadening file/network
        # permissions or falling back to a weaker implementation on failure.
        command += ["-c", 'windows.sandbox="elevated"']
    if session_id:
        command += ["resume", session_id, "-"]
    else:
        command += ["--cd", str(worktree), "-"]
    return command


def task_prompt(task, protocol, resource, read_only=False):
    mode = ("This is a READ-ONLY AUDIT: inspect and report; do not edit any project file."
            if read_only else "Edit only files needed for the assigned deliverable in this worktree.")
    return f"""Perform this one bounded task for resource {resource}.
{mode}
The current user authorized a subscription-first, faster research workflow.
The operating protocol below governs this run over historical workflow instructions.
Use only this worktree. Do not commit, push, merge, publish, send messages, edit shared
coordination state, rent compute, call paid APIs, or dispatch CI/other agents/processes.
Do not run another LLM client. Standard local tools and local analysis subprocesses are allowed.
No internet access from shell commands; use available read-only research tools if provided.
Stop after the concrete deliverable and relevant checks. Do not start a new paper,
self-improvement project, full-repository review, or repeated subjective scoring loop.
A completed outcome means this task is complete, never that a paper is publication-ready.
Use blockers only for unresolved issues preventing the assigned deliverable from being complete.
Put downstream work outside this assignment in follow_up, including later publication approvals
or upload preparation when those are not this task. Completed requires an empty blockers list;
a completed task can still have follow_up items. Never relabel an actual task blocker as follow_up.
Return the required structured outcome; record only checks actually performed.

OPERATING PROTOCOL:
{protocol}

TASK:
{task}
"""


def dispatch_prompt(prompt, config, read_only, number, remaining):
    context = {"model": MODEL, "reasoning_effort": config["reasoning_effort"],
               "python_executable": sys.executable,
               "timeout_seconds": config["timeout_seconds"],
               "remaining_seconds_at_dispatch": round(remaining, 3),
               "dispatch_number": number, "max_rounds": config["max_rounds"],
               "max_dispatches": config["max_dispatches"],
               "effective_dispatch_limit": 1 if read_only else min(config["max_rounds"], config["max_dispatches"]),
               "sandbox": "read-only" if read_only else "workspace-write",
               "authentication": "saved-chatgpt"}
    return ("Runner-supplied execution context:\n" + json.dumps(context) + "\n\n"
            "Use these actual configured values when reporting model, reasoning effort, and run limits. "
            "For Python commands use python_executable; a bare python command may not be on PATH. "
            "timeout_seconds is the total run budget, not measured elapsed time. "
            "remaining_seconds_at_dispatch is a dispatch-time reading, not a live clock. "
            "Do not infer other runtime metadata or subscription capacity; report unknown values as unknown.\n\n"
            + prompt)


def validate_task_contract(contract, resource):
    if (not isinstance(contract, dict) or contract.get("kind") not in ("science", "maintenance", "review")
            or contract.get("resource") != resource):
        raise Refused("Writing --task-contract requires kind science|maintenance|review and resource matching --resource.")
    if contract["kind"] == "review" and not isinstance(contract.get("review_request"), dict):
        raise Refused("Review task contracts require an explicit review_request object.")
    return contract


def launch(root, cache, codex, config, task, resource, env, read_only=False,
           coordinator_id=None, task_contract=None):
    config = validate_settings(config)
    with Coordinator(root, cache) as ownership:
        if not read_only:
            ownership.require(coordinator_id)
            handover_disabled(root)
            ownership.recover(coordinator_id)
            if resource in ownership.state["resources"]:
                raise Refused(f"Resource {resource} has unresolved retained output; resolve it before dispatch.")
        if not read_only:
            validate_task_contract(task_contract, resource)
            from research_cycle import require_current_plan
            require_current_plan(root, task_contract, task)
        if task_contract is not None:
            from bounded_review import task_review_decision
            decision = task_review_decision(task_contract, repo=root)
            if not decision["allowed"]:
                raise Refused(decision["reason"])
        protocol_path = root / PROTOCOL
        if not protocol_path.is_file():
            raise Refused(f"Required operating protocol is missing: {PROTOCOL}")
        protocol = protocol_path.read_text(encoding="utf-8-sig")
        run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:10]
        directory = cache / run_id
        directory.mkdir()
        worktree = directory / "worktree"
        base = git(root, "rev-parse", "HEAD")
        receipt = {"schema": "emc-local-research-run/1", "run_id": run_id,
                   "started_utc": utc_now(), "resource": resource, "model": MODEL,
                   "auth": "saved-chatgpt", "coordination": "one-local-clone-only",
                   "coordinator_id": coordinator_id,
                   "mode": "read-only" if read_only else "workspace-write",
                   "legacy_and_remote_writers_stopped_acknowledged": not read_only,
                   "base_commit": base, "worktree": str(worktree), "limits": config,
                   "task_sha256": hashlib.sha256(task.encode()).hexdigest(),
                   "protocol_sha256": hashlib.sha256(protocol.encode()).hexdigest(),
                   "rounds": [], "status": "starting", "automatic_publication": False}
        receipt_path = directory / "receipt.json"
        if not read_only:
            ownership.reserve(coordinator_id, resource, run_id, receipt=receipt_path)
        write_json(receipt_path, receipt)
        prompt = task_prompt(task, protocol, resource, read_only)
        (directory / "task.txt").write_text(task, encoding="utf-8")
        (directory / "protocol.md").write_text(protocol, encoding="utf-8")
        if task_contract is not None:
            write_json(directory / "task-contract.json", task_contract)
        started = time.monotonic()
        deadline = started + config["timeout_seconds"]
        try:
            probe_auth(codex, env)
            git(root, "worktree", "add", "--detach", str(worktree), base,
                timeout=max(1, deadline - time.monotonic()))
            scratch = worktree / ".cache" / "research-run"
            scratch.mkdir(parents=True)
            schema = scratch / "outcome-schema.json"
            write_json(schema, OUTCOME_SCHEMA)
            session = None
            rounds = 1 if read_only else min(config["max_rounds"], config["max_dispatches"])
            for number in range(1, rounds + 1):
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise subprocess.TimeoutExpired("research run", config["timeout_seconds"])
                outcome_path = scratch / f"outcome-{number}.json"
                stdout, stderr = directory / f"round-{number}.jsonl", directory / f"round-{number}.stderr"
                record = {"round": number, "started_utc": utc_now(), "status": "running",
                          "stdout": stdout.name, "stderr": stderr.name}
                receipt["rounds"].append(record)
                receipt["status"] = "running"
                write_json(receipt_path, receipt)
                code = run_process(command_for(codex, worktree, schema, outcome_path, config, session, read_only),
                                   dispatch_prompt(prompt, config, read_only, number, remaining),
                                   worktree, stdout, stderr, remaining, env)
                record.update(event_summary(stdout))
                record.update({"exit_code": code, "finished_utc": utc_now()})
                if code or record["errors"]:
                    record["status"] = "failed"
                    raise Refused("Codex run failed; inspect the recorded logs. No automatic retry.")
                if read_only and git(worktree, "status", "--porcelain"):
                    raise Refused("Read-only audit changed project files; inspect the retained worktree.")
                if git(worktree, "rev-parse", "HEAD") != base:
                    raise Refused("Worker changed its committed base; inspect retained work before integration.")
                outcome = read_outcome(outcome_path)
                record["artifact_inventory"] = artifact_inventory(worktree, outcome)
                record.update({"status": outcome["status"], "outcome": outcome})
                retained_outcome = directory / f"outcome-{number}.json"
                write_json(retained_outcome, outcome)
                record["outcome_sha256"] = hashlib.sha256(retained_outcome.read_bytes()).hexdigest()
                receipt["status"] = outcome["status"]
                if outcome["status"] != "needs_revision":
                    break
                session = record["session_id"] or session
                if not session:
                    raise Refused("Revision requested without an explicit resumable session ID.")
                prompt = ("Resolve only these existing blockers, then rerun affected checks. "
                          "Do not add a fresh review, act on downstream follow_up, or broaden scope. "
                          "All original task limits and outcome field meanings apply.\n"
                          + json.dumps({"summary": outcome["summary"], "blockers": outcome["blockers"]}))
            if receipt["status"] == "needs_revision":
                receipt["status"] = "budget_exhausted"
        except subprocess.TimeoutExpired:
            receipt["status"] = "timed_out"
        except KeyboardInterrupt:
            receipt["status"] = "cancelled"
        except (Refused, OSError, ValueError) as exc:
            receipt.update({"status": "failed", "error": str(exc)})
        finally:
            receipt["finished_utc"] = utc_now()
            receipt["elapsed_seconds"] = round(time.monotonic() - started, 3)
            # A crash can leave starting/running receipts; they are never read
            # as completion. Keep all worktrees for inspection; never auto-delete.
            for record in receipt["rounds"]:
                log = directory / record["stdout"]
                if log.is_file():
                    record.update(event_summary(log))
                if record["status"] == "running":
                    record["status"] = receipt["status"]
            if worktree.is_dir():
                try:
                    receipt["working_tree_status"] = git(worktree, "status", "--porcelain")
                except Refused as exc:
                    receipt["working_tree_status_error"] = str(exc)
            write_json(receipt_path, receipt)
            if not read_only:
                ownership.update_run(coordinator_id, resource, receipt)
            with (cache / "runs.jsonl").open("a", encoding="utf-8") as stream:
                stream.write(json.dumps({"run_id": run_id, "resource": resource,
                                         "status": receipt["status"], "receipt": str(receipt_path)}) + "\n")
        return receipt_path, receipt


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo", default=".")
    parser.add_argument("--config", help="Optional JSON budget settings; see codex-runner.json")
    parser.add_argument("--codex", default="codex")
    parser.add_argument("--task-file", help="UTF-8 file containing one concrete deliverable")
    parser.add_argument("--task-contract", help="Optional JSON ledger/selection contract for bounded review policy")
    parser.add_argument("--coordinator-id", help="Stable owning task identity; required for writes and ownership changes")
    parser.add_argument("--note", help="Reason/evidence for coordinator claim or handoff")
    parser.add_argument("--worker-id", help="Manual worker identity when reserving a resource")
    parser.add_argument("--worktree", help="Separate existing worktree for a manual resource writer")
    parser.add_argument("--resolution", choices=("integrated", "abandoned"))
    parser.add_argument("--evidence", help="Durable verification/reason file for resolving retained output")
    parser.add_argument("--resource", help="Stable resource name, e.g. paper:PUB-ASO or process:ci")
    parser.add_argument("--read-only", action="store_true",
                        help="One sandboxed audit of a frozen checkout; can coexist with legacy writers")
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--plan", action="store_true", help="Read-only plan; no auth check or LLM call")
    modes.add_argument("--doctor", action="store_true", help="Read-only prerequisites and auth probe")
    modes.add_argument("--coordinator-status", action="store_true")
    modes.add_argument("--claim-coordinator", action="store_true")
    modes.add_argument("--release-coordinator", action="store_true")
    modes.add_argument("--handoff-coordinator", metavar="SUCCESSOR")
    modes.add_argument("--reserve-resource", action="store_true")
    modes.add_argument("--release-resource", action="store_true")
    modes.add_argument("--recover", action="store_true")
    parser.add_argument("--ack-local-cutover", action="store_true",
                        help="Assert all legacy/remote writers are stopped; this lock is LOCAL ONLY")
    args = parser.parse_args(argv)
    try:
        config = settings(args.config)
        root, cache = repository(args.repo)
        codex = shutil.which(args.codex)
        report = {"repo": str(root), "run_directory": str(cache), "model": MODEL,
                  "limits": config, "codex_available": bool(codex),
                  "protocol_available": (root / PROTOCOL).is_file(),
                  "coordination_scope": "one-local-clone-only; not Claude or separate machines",
                  "execution_enabled": args.ack_local_cutover or args.read_only,
                  "mode": "read-only" if args.read_only else "workspace-write", "paid_api_fallback": False}
        if args.plan:
            print(json.dumps(report, indent=2))
            return 0
        if args.coordinator_status:
            print(json.dumps(Coordinator.read(cache), indent=2))
            return 0
        if any((args.claim_coordinator, args.release_coordinator, args.handoff_coordinator,
                args.reserve_resource, args.release_resource, args.recover)):
            with Coordinator(root, cache) as ownership:
                if args.claim_coordinator:
                    if not args.ack_local_cutover:
                        raise Refused("Coordinator claim requires --ack-local-cutover after draining old writers.")
                    ownership.claim(args.coordinator_id, args.note)
                elif args.handoff_coordinator:
                    ownership.handoff(args.coordinator_id, args.handoff_coordinator, args.note)
                elif args.release_coordinator:
                    ownership.release(args.coordinator_id, args.note)
                elif args.reserve_resource:
                    if not args.worktree:
                        raise Refused("Manual writer reservation requires --worktree.")
                    ownership.reserve(args.coordinator_id, args.resource, args.worker_id, args.worktree)
                elif args.release_resource:
                    if not args.evidence:
                        raise Refused("Resolving a resource requires --evidence.")
                    ownership.release_resource(args.coordinator_id, args.resource, args.resolution, args.evidence)
                else:
                    ownership.recover(args.coordinator_id)
                print(json.dumps(ownership.state, indent=2))
            return 0
        if not codex:
            raise Refused("Native Codex CLI executable not found.")
        if os.name == "nt" and Path(codex).suffix.lower() in (".cmd", ".bat"):
            raise Refused("Use --codex with the native codex.exe path on Windows.")
        if args.doctor:
            try:
                probe_auth(codex, os.environ)
                report["subscription_auth"] = "verified"
            except (Refused, subprocess.TimeoutExpired) as exc:
                report["subscription_auth"] = "unverified"
                report["detail"] = str(exc)
            print(json.dumps(report, indent=2))
            return 0 if report["subscription_auth"] == "verified" and report["protocol_available"] else 2
        if not args.ack_local_cutover and not args.read_only:
            raise Refused("Real runs require --ack-local-cutover after stopping legacy and remote "
                          "writers. This runner does not acquire claim.py's remote claim.")
        if not args.task_file or not args.resource or not re.fullmatch(r"(?:paper|process):[A-Za-z0-9_.-]+", args.resource):
            raise Refused("Supply --task-file and --resource paper:ID or process:ID.")
        task = Path(args.task_file).read_text(encoding="utf-8-sig").strip()
        if not task:
            raise Refused("Task file is empty.")
        def cancelled(*_):
            raise KeyboardInterrupt

        previous_handler = signal.signal(signal.SIGTERM, cancelled)
        try:
            receipt_path, receipt = launch(root, cache, codex, config, task, args.resource,
                                           dict(os.environ), args.read_only, args.coordinator_id,
                                           json.loads(Path(args.task_contract).read_text(encoding="utf-8-sig"))
                                           if args.task_contract else None)
        finally:
            signal.signal(signal.SIGTERM, previous_handler)
        print(json.dumps({"status": receipt["status"], "receipt": str(receipt_path),
                          "worktree": receipt["worktree"]}, indent=2))
        return 0 if receipt["status"] == "completed" else 1
    except (Refused, OSError, ValueError, subprocess.TimeoutExpired) as exc:
        print(json.dumps({"status": "refused", "reason": str(exc)}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
