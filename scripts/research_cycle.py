#!/usr/bin/env python3
"""Plan bounded work and preserve verified outcomes using the existing research runner.

Task contracts refine existing ledger routes; they are not a second queue, lock,
scientific acceptance bar, or publication authority. Selection scores are explicit
coordinator judgements. Actual outcomes, not scores, measure progress.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import uuid

import research_run as runner

CONTRACTS = "research/autonomy/cycle-tasks.json"
HISTORY = "research/autonomy/cycle-outcomes"


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def within(root, relative):
    path = (root / relative).resolve()
    if not path.is_relative_to(root.resolve()) or Path(relative).is_absolute():
        raise runner.Refused(f"Path is outside the repository: {relative}")
    return path


def fingerprint(root, task):
    inputs = {p: digest(within(root, p)) for p in task["inputs"]}
    for path, value in inputs.items():
        committed = subprocess.run(["git", "show", f"HEAD:{path}"], cwd=root, capture_output=True)
        if committed.returncode or hashlib.sha256(committed.stdout).hexdigest() != value:
            raise runner.Refused(f"Input is uncommitted or differs from HEAD: {path}")
    # Changing a priority judgement or effort estimate does not create new science.
    identity = {k: task.get(k) for k in ("id", "resource", "question", "instructions", "outputs", "stop_condition")}
    encoded = json.dumps({"task": identity, "inputs": inputs}, sort_keys=True).encode()
    return hashlib.sha256(encoded).hexdigest(), inputs


def history(root):
    return [read(p) for p in sorted((root / HISTORY).glob("*/cycle.json"))]


def plan(root, tasks, previous, ledger):
    rows = {r["id"]: r for r in ledger["entries"]}
    decisions = []
    recent = sorted(previous, key=lambda r: r.get("finished_utc", ""))[-3:]
    for task in tasks:
        item = {"task_id": task["id"], "resource": task["resource"], "eligible": False}
        decisions.append(item)
        missing = [p for p in task["inputs"] if not within(root, p).is_file()]
        if missing:
            item["reason"] = "Missing evidence inputs: " + ", ".join(missing)
            continue
        fp, inputs = fingerprint(root, task)
        item.update(fingerprint=fp, input_sha256=inputs)
        linked = task["ledger_ids"]
        if not linked or any(i not in rows for i in linked):
            item["reason"] = "Task must refer to existing ledger entries"
            continue
        if any(rows[i].get("owner") for i in linked):
            item["reason"] = "Linked ledger work has an owner"
            continue
        if task.get("external_blocker"):
            item["reason"] = task["external_blocker"]
            continue
        matching = [p for p in previous if p.get("fingerprint") == fp]
        if matching:
            latest = max(matching, key=lambda p: p.get("finished_utc", ""))
            item["prior_run_id"] = latest["run_id"]
            item["reason"] = "Matching completed or attempted work; changed evidence or an explicit revised contract is required"
            if latest["status"] == "verified":
                changed = [p for p, h in latest["artifact_sha256"].items()
                           if not within(root, p).is_file() or digest(within(root, p)) != h]
                item["reason"] = ("Preserved output changed: reconcile before dispatch" if changed
                                  else "Reuse matching verified output")
            continue
        if task["kind"] == "maintenance":
            friction = task.get("observed_friction", {})
            if not friction.get("evidence") or not friction.get("measurement"):
                item["reason"] = "Maintenance needs measured friction and evidence"
                continue
            if not within(root, friction["evidence"]).is_file():
                item["reason"] = "Maintenance evidence is missing"
                continue
            if any(p.get("kind") == "maintenance" for p in recent):
                item["reason"] = "One maintenance cycle per four outcomes; advance science or stop"
                continue
        assessment = task["assessment"]
        names = ("clinical_relevance", "answerability", "validation", "information_gain")
        if any(type(assessment[n]["rating"]) is not int or not 0 <= assessment[n]["rating"] <= 3
               or not assessment[n]["basis"] for n in names):
            raise runner.Refused("Each selection rating needs a 0–3 judgement and evidence basis")
        effort = task["effort_minutes"]
        if type(effort) is not int or effort <= 0 or effort > 30:
            raise runner.Refused("A cycle contract must fit the existing 30-minute run limit")
        item.update(eligible=True, score=round(sum(assessment[n]["rating"] for n in names) / effort, 4),
                    reason="Eligible bounded question; score is a planning judgement, not scientific evidence")
    eligible = [d for d in decisions if d["eligible"]]
    # Science takes precedence over independent maintenance when both can proceed.
    kinds = {t["id"]: t["kind"] for t in tasks}
    eligible.sort(key=lambda d: (kinds[d["task_id"]] == "maintenance", -d["score"], d["task_id"]))
    selected = eligible[0] if eligible else None
    return {"schema": "emc-research-cycle-plan/1", "created_utc": runner.utc_now(),
            "base_commit": runner.git(root, "rev-parse", "HEAD"), "selected": selected,
            "decisions": decisions, "duplicate_candidates_suppressed": sum("prior_run_id" in d for d in decisions),
            "dispatches": 0, "selection_is_scientific_evidence": False}


def prompt(task):
    return (f"Bounded computational question: {task['question']}\n\n"
            f"Stop condition: {task['stop_condition']}\n\n"
            f"Inputs: {json.dumps(task['inputs'])}\n"
            f"Allowed changed files: {json.dumps(task['outputs'])}\n\n"
            + task["instructions"] + "\n\n"
            "Do not edit acceptance rules, shared queue/status, publication records or manuscripts. "
            "Preserve negative and unreadable results. Use only committed inputs and local CPU. "
            "Return actual commands/checks and outputs. Completion concerns this bounded question only.")


def write_plan(root, destination):
    contracts = read(root / CONTRACTS)
    result = plan(root, contracts["tasks"], history(root), read(root / "research/autonomy/research-ledger.json"))
    destination.mkdir(parents=True, exist_ok=True)
    if result["selected"]:
        task = next(t for t in contracts["tasks"] if t["id"] == result["selected"]["task_id"])
        result["contract"] = task
        task_text = prompt(task)
        result["task_sha256"] = hashlib.sha256(task_text.encode()).hexdigest()
        (destination / "task.txt").write_text(task_text, encoding="utf-8")
        runner.write_json(destination / "contract.json", {**task, "cycle_plan": {
            "base_commit": result["base_commit"], "fingerprint": result["selected"]["fingerprint"],
            "task_sha256": result["task_sha256"]}})
    else:
        for name in ("task.txt", "contract.json"):
            (destination / name).unlink(missing_ok=True)
    runner.write_json(destination / "plan.json", result)
    return result


def require_current_plan(root, contract, task_text):
    """Recheck registered cycle work inside the runner lock, before spending a dispatch.

    Generic manual/review contracts keep their existing interface. Registered cycle
    ids also require a plan binding, so old unbound copies cannot bypass this check.
    """
    path = root / CONTRACTS
    tasks = read(path)["tasks"] if path.is_file() else []
    current = next((t for t in tasks if t["id"] == contract.get("id")), None)
    binding = contract.get("cycle_plan")
    if current is None and "cycle_plan" not in contract:
        return
    if current is None:
        raise runner.Refused("Cycle contract is no longer registered; create a current plan")
    if task_text != prompt(current):
        raise runner.Refused("Cycle task text differs from the planned prompt; create a current plan")
    if {k: v for k, v in contract.items() if k != "cycle_plan"} != current:
        raise runner.Refused("Cycle contract changed since planning; create a current plan")
    result = plan(root, [current], history(root), read(root / "research/autonomy/research-ledger.json"))
    if not result["selected"]:
        raise runner.Refused(result["decisions"][0]["reason"])
    expected = {"base_commit": result["base_commit"],
                "fingerprint": result["selected"]["fingerprint"],
                "task_sha256": hashlib.sha256(task_text.encode()).hexdigest()}
    if binding != expected:
        raise runner.Refused("Cycle plan is missing or its base/inputs changed; create a current plan")


def worker_integrity_issues(worktree, inputs, outputs, base):
    if not worktree.is_dir():
        return ["Worker worktree is absent; input and output integrity could not be checked"]
    issues = []
    try:
        if any(not within(worktree, p).is_file() or digest(within(worktree, p)) != h
               for p, h in inputs.items()):
            issues.append("Worker inputs differ from the selected committed evidence")
        paths = runner.git(worktree, "diff", "--name-only", base).splitlines()
        paths += runner.git(worktree, "ls-files", "--others", "--exclude-standard").splitlines()
        if set(paths) - set(outputs):
            issues.append("Worker changed files outside its bounded contract")
    except (runner.Refused, OSError) as exc:
        issues.append(str(exc))
    return issues


def collect(root, cache, owner, plan_path, receipt_path, verification_path):
    # The existing runner lock remains the only local state arbiter.
    from local_ownership import Coordinator
    with Coordinator(root, cache) as ownership:
        ownership.require(owner)
        selection, receipt, verification = read(plan_path), read(receipt_path), read(verification_path)
        task = selection["contract"]
        selected = selection["selected"]
        if not re.fullmatch(r"[A-Za-z0-9-]+", receipt["run_id"]):
            raise runner.Refused("Invalid run identifier")
        fp, inputs = fingerprint(root, task)
        if fp != selected["fingerprint"] or receipt["base_commit"] != selection["base_commit"]:
            raise runner.Refused("Selected input/base changed; reconcile the preserved run before recording")
        if receipt["resource"] != task["resource"] or receipt["task_sha256"] != selection["task_sha256"]:
            raise runner.Refused("Receipt does not belong to the selected contract")
        worktree = Path(receipt["worktree"])
        issues = worker_integrity_issues(worktree, inputs, task["outputs"], receipt["base_commit"])
        if verification.get("run_id") != receipt["run_id"]:
            raise runner.Refused("Coordinator verification names a different run")
        checks = verification.get("checks", [])
        check_logs = []
        for check in checks:
            log = Path(check.get("log", ""))
            if not log.is_absolute():
                log = within(root, str(log))
            if not any(log.resolve().is_relative_to(base.resolve()) for base in (root, worktree)):
                raise runner.Refused("Check logs must be in the coordinator or worker checkout")
            if not log.is_file() or check.get("log_sha256") != digest(log):
                raise runner.Refused("Verification needs preserved, hash-matching check logs")
            check_logs.append(log)
        verified = (receipt["status"] == "completed" and bool(checks)
                    and all(type(c.get("exit_code")) is int and c["exit_code"] == 0 for c in checks))
        if verified and issues:
            raise runner.Refused("; ".join(issues))
        hashes = {}
        if verified:
            if not task["outputs"]:
                raise runner.Refused("Verified computation needs a concrete preserved output")
            for p in task["outputs"]:
                source, integrated = within(worktree, p), within(root, p)
                if not source.is_file() or not integrated.is_file() or digest(source) != digest(integrated):
                    raise runner.Refused(f"Output has not been integrated byte-for-byte: {p}")
                hashes[p] = digest(integrated)
            if verification.get("artifact_sha256") != hashes:
                raise runner.Refused("Verification hashes do not match integrated outputs")
        destination = root / HISTORY / receipt["run_id"]
        if destination.exists():
            raise runner.Refused("A durable cycle outcome already exists; do not overwrite it")
        staging = root / ".cache" / "cycle-collect" / (receipt["run_id"] + "-" + uuid.uuid4().hex)
        staging.mkdir(parents=True)
        for source, name in [(plan_path, "plan.json"), (receipt_path, "runner-receipt.json"),
                             (verification_path, "verification.json")]:
            shutil.copy2(source, staging / name)
        for number, log in enumerate(check_logs, 1):
            shutil.copy2(log, staging / f"check-{number}.log")
        rounds = receipt.get("rounds", [])
        for i, record in enumerate(rounds, 1):
            if "outcome" in record:
                runner.write_json(staging / f"outcome-{i}.json", record["outcome"])
        result = {"schema": "emc-research-cycle-outcome/1", "run_id": receipt["run_id"],
                  "task_id": task["id"], "kind": task["kind"], "resource": task["resource"],
                  "fingerprint": fp, "input_sha256": inputs, "artifact_sha256": hashes,
                  "status": "verified" if verified else "attempted",
                  "runner_status": receipt["status"], "finished_utc": runner.utc_now(),
                  "worker_integrity_issues": issues,
                  "worker_elapsed_seconds": receipt["elapsed_seconds"],
                  "time_to_verified_output_seconds": verification.get("time_to_verified_output_seconds") if verified else None,
                  "substantive_defects_found": verification.get("substantive_defects_found"),
                  "repair_induced_defects": verification.get("repair_induced_defects"),
                  "duplicate_candidates_suppressed": selection["duplicate_candidates_suppressed"],
                  "usage": [u for r in rounds for u in r.get("usage", [])],
                  "model": receipt["model"], "limits": receipt["limits"],
                  "next_action": verification["next_action"], "publication_evidence": False}
        runner.write_json(staging / "cycle.json", result)
        destination.parent.mkdir(parents=True, exist_ok=True)
        staging.replace(destination)
        return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo", default=".")
    parser.add_argument("--plan", action="store_true")
    parser.add_argument("--output", default=".cache/research-cycle")
    parser.add_argument("--collect", help="Existing runner receipt path; does not launch or integrate")
    parser.add_argument("--plan-file")
    parser.add_argument("--verification-file")
    parser.add_argument("--coordinator-id")
    args = parser.parse_args(argv)
    try:
        root, cache = runner.repository(args.repo)
        if args.collect:
            if not all((args.plan_file, args.verification_file, args.coordinator_id)):
                raise runner.Refused("Collection needs plan, independent verification and coordinator identity")
            result = collect(root, cache, args.coordinator_id, Path(args.plan_file),
                             Path(args.collect), Path(args.verification_file))
        else:
            result = write_plan(root, within(root, args.output))
        print(json.dumps(result, indent=2))
        return 0
    except (runner.Refused, KeyError, ValueError, OSError) as exc:
        print(json.dumps({"status": "refused", "reason": str(exc)}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
