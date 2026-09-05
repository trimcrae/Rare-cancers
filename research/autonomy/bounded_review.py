#!/usr/bin/env python3
"""Bound review dispatch using existing hardening/seat evidence, never a ready boolean.

This decides whether to spend another review, not whether a paper may be published.
An explicit reason is inspectable evidence for the coordinator, not proof that the
named scientific error exists. publish_bar remains the acceptance decision.
"""
from __future__ import annotations

import argparse
from functools import lru_cache
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys

REPO = Path(__file__).resolve().parents[2]
MATERIAL_REASONS = {"material_error", "changed_evidence", "external_review"}


@lru_cache(maxsize=4)
def _bar(repo):
    path = repo / "research/autonomy/publish_bar.py"
    sys.path.insert(0, str(path.parent))
    spec = importlib.util.spec_from_file_location("_bounded_publish_bar", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _paths_exist(paths, repo):
    if not isinstance(paths, list) or not paths:
        return False
    for value in paths:
        if not isinstance(value, str) or not value.strip():
            return False
        path = (repo / value).resolve()
        if Path(value).is_absolute() or not path.is_relative_to(repo) or not path.is_file():
            return False
    return True


def _material_reason(request, repo):
    reason = request.get("reason")
    return (isinstance(reason, dict) and reason.get("kind") in MATERIAL_REASONS
            and isinstance(reason.get("summary"), str) and bool(reason["summary"].strip())
            and _paths_exist(reason.get("evidence"), repo))


def review_decision(paper, sha, request=None, *, repo=None):
    """Return allowed/action/reason; request is the immutable task's review_request.

    Baseline review is one batch. Further work needs a focused repair verification
    naming claims and dependencies, or an explicit evidenced material reason. A
    completed matching review is reused even if it reports maintenance findings.
    """
    repo = Path(repo or REPO).resolve()
    request = {} if request is None else request
    def result(allowed, action, reason, **extra):
        return dict(allowed=allowed, action=action, reason=reason, paper=paper, sha=sha, **extra)
    if not isinstance(request, dict):
        return result(False, "invalid_request", "review_request must be an object")
    scope = request.get("scope", "baseline")
    if scope not in {"baseline", "focused_verification", "full_review"}:
        return result(False, "invalid_request", "unknown review scope")
    if not isinstance(paper, str) or not re.fullmatch(r"PUB-[A-Za-z0-9_.-]+", paper):
        return result(False, "invalid_request", "review needs a publication id")
    if not isinstance(sha, str) or not re.fullmatch(r"[0-9a-f]{40}", sha):
        return result(False, "invalid_request", "review needs an exact frozen 40-character revision")
    try:
        bar = _bar(repo)
        hard, error = bar._read_json(bar.HARDENING_DIR / f"{paper}.json")
        history = bar._look_history(paper)
        prior = bool(history) or hard is not None
        matching = bool(hard and bar._covers(paper, hard.get("reviewed_commit"), sha))
        verdict = bar.clause_1_hardening_converged(paper, sha) if matching else None
    except Exception as exc:
        return result(False, "unverifiable", f"cannot read review evidence: {type(exc).__name__}: {exc}")
    lenses = request.get("lenses")
    if lenses is not None:
        if (not isinstance(lenses, list) or not lenses
                or not all(isinstance(lens, str) and re.fullmatch(r"[A-Za-z0-9_.-]+", lens)
                           for lens in lenses) or len(lenses) != len(set(lenses))):
            return result(False, "invalid_request", "lenses must name a nonempty unique review batch")
        batch = []
        for path in bar.SEATS_DIR.glob(f"{paper}-{sha}-seat-*.json"):
            seat, _ = bar._read_json(path)
            if seat and seat.get("review_request") == request and seat.get("reviewed_commit") == sha:
                batch.append(seat)
        if batch:
            complete = {seat.get("lens") for seat in batch if seat.get("status") == "complete"}
            if set(lenses) <= complete:
                return result(False, "budget_spent", "every lens in this frozen review batch has "
                              "reported; record the outcome and repair or resolve its findings")
            return result(True, "resume_batch", "finish only the remaining lenses of the frozen batch")
    material = _material_reason(request, repo)
    if material:
        return result(True, scope, "named material reason with inspectable evidence",
                      review_reason=request["reason"])
    if request.get("reason"):
        return result(False, "invalid_reason", "additional review needs material_error, changed_evidence, "
                      "or external_review, a summary and existing repository evidence files")
    if matching and verdict and verdict["ok"]:
        return result(False, "reuse_review", "completed review covers these deliverables; maintenance "
                      "findings do not reopen it", reviewed_commit=hard["reviewed_commit"],
                      evidence=verdict["evidence"])
    if scope == "focused_verification":
        claims = request.get("changed_claims")
        if not prior or not isinstance(claims, list) or not claims or not all(
                isinstance(c, str) and c.strip() for c in claims) or not _paths_exist(
                    request.get("depends_on"), repo):
            return result(False, "invalid_scope", "focused verification needs a prior review, "
                          "changed_claims and existing depends_on evidence files")
        # Records preserve each dispatch's request. One completed focused batch
        # cannot silently turn into another full look on the same frozen artifact.
        for path in bar.SEATS_DIR.glob(f"{paper}-*-seat-*.json"):
            seat, _ = bar._read_json(path)
            if (seat and seat.get("status") == "complete"
                    and (seat.get("review_request") or {}).get("scope") == scope
                    and bar._covers(paper, seat.get("reviewed_commit"), sha)):
                return result(False, "budget_spent", "focused verification already completed for "
                              "these deliverables; report the unresolved issue or a material reason")
        return result(True, scope, "verify the batched repair's named claims and dependencies")
    if prior:
        return result(False, "review_endpoint", "a prior review exists; batch repairs and verify the "
                      "affected claims. Another whole-paper review needs a named material reason",
                      existing_evidence=verdict)
    if (bar.HARDENING_DIR / f"{paper}.json").exists() and error:
        return result(False, "unverifiable", error)
    return result(True, "baseline", "one independent review batch for a new paper")


def task_review_decision(entry, sha=None, *, repo=None):
    """Shared adapter for legacy queue readers and the subscription runner.

    Typed legacy rows use kind=harden. Incidental mentions of past reviews or
    closes_clause metadata do not turn a tooling repair into a manuscript review.
    """
    repo = Path(repo or REPO).resolve()
    clause = entry.get("closes_clause") or {}
    serves = entry.get("serves") or {}
    request = entry.get("review_request")
    text = " ".join(str(entry.get(k) or "") for k in ("title", "item", "what", "next_act"))
    review = (request is not None or entry.get("kind") in {"harden", "review"}
              or (not entry.get("kind") and bool(re.search(
                  r"^\W*(?:run|commission|conduct)\b.{0,70}\b(?:hardening|blind (?:review|seat)|whole.paper review)",
                  text.strip(), re.I))))
    if not review:
        return {"allowed": True, "action": "not_review", "reason": "not a review dispatch"}
    paper = (entry.get("paper") or clause.get("paper") or serves.get("publication")
             or serves.get("paper"))
    resource = entry.get("resource", "")
    if not paper and isinstance(resource, str) and resource.startswith("paper:"):
        paper = resource.split(":", 1)[1]
    if not paper:
        matches = set(re.findall(r"\bPUB-[A-Z0-9]+(?:-[A-Z0-9]+)*", text))
        paper = next(iter(matches)) if len(matches) == 1 else None
    if sha is None:
        proc = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo,
                              capture_output=True, text=True, timeout=30)
        sha = proc.stdout.strip() if proc.returncode == 0 else None
    if not sha:
        return {"allowed": False, "action": "unverifiable", "reason": "cannot resolve review revision"}
    return review_decision(paper, sha, request, repo=repo)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--paper", required=True)
    parser.add_argument("--sha", required=True)
    parser.add_argument("--request", type=Path, help="JSON review_request object")
    args = parser.parse_args(argv)
    request = json.loads(args.request.read_text(encoding="utf-8")) if args.request else None
    decision = review_decision(args.paper, args.sha, request)
    print(json.dumps(decision, indent=2))
    return 0 if decision["allowed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
