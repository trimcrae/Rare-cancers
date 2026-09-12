"""Verify evidence of an independent LLM prose review, not a readability score.

The LLM judges clarity. This module verifies that its recorded review covers the
outgoing bytes, preserves scientific meaning, and has no unresolved blockers.
It cannot establish that a reviewer was honest or that a paper is good science.
"""
from __future__ import annotations

from datetime import datetime
import hashlib
import json
from pathlib import PurePosixPath
import re


SCHEMA = "emc-llm-readability-review/1"
INVENTORY = "research/autonomy/editorial-prose-inventory.json"
EXPLANATIONS = ("question", "approach", "main_finding", "main_limitations", "next_step")
CHECKS = ("reader_facing_text_reviewed", "abstract_understandable", "terms_explained",
          "narrative_followable", "scientific_meaning_preserved", "limitations_preserved")


def _text(value):
    return isinstance(value, str) and bool(value.strip())


def _path(value):
    if not _text(value) or "\\" in value or ":" in value:
        return False
    path = PurePosixPath(value)
    return not path.is_absolute() and ".." not in path.parts and str(path) == value


def _digest(value):
    return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None


def verify_review(paper_id, document, document_bytes, read_at):
    """Return (accepted, explanation); read_at reads bytes at one pinned revision.

    Receipt and report must be committed alongside the candidate. Review reuse is
    by artifact hashes, so unrelated commits do not require another LLM pass.
    """
    if not isinstance(paper_id, str) or not re.fullmatch(r"[A-Z0-9-]+", paper_id):
        return False, "Invalid paper identifier for editorial review."
    receipt_path = f"research/autonomy/readability-reviews/{paper_id}.json"
    try:
        inventory = json.loads(read_at(INVENTORY).decode("utf-8-sig"))
        if not isinstance(inventory, dict) or inventory.get("schema") != "emc-editorial-prose-inventory/1":
            return False, "Missing or unsupported authoritative editorial prose inventory."
        required = inventory.get("papers", {}).get(paper_id)
        if (not isinstance(required, list) or not required or
                not all(_path(path) for path in required) or len(set(required)) != len(required)):
            return False, "The paper needs a complete authoritative outgoing prose inventory."
        if document not in required:
            return False, "The registered manuscript differs from the editorial prose inventory."
        receipt = json.loads(read_at(receipt_path).decode("utf-8-sig"))
        if not isinstance(receipt, dict) or receipt.get("schema") != SCHEMA:
            return False, "Missing or unsupported LLM readability review schema."
        if receipt.get("paper_id") != paper_id:
            return False, "LLM readability review belongs to another paper."
        if receipt.get("review_kind") != "independent_llm_editorial":
            return False, "An independent LLM editorial review is required; metrics/layout are insufficient."
        reviewer = receipt.get("reviewer")
        writers = receipt.get("writer_ids")
        if not isinstance(reviewer, dict) or not all(_text(reviewer.get(k)) for k in
                ("agent_id", "model", "execution_evidence")):
            return False, "Reviewer identity, model description and actual execution evidence are required."
        if not isinstance(writers, list) or not writers or not all(_text(x) for x in writers):
            return False, "Identify the writers whose prose was independently reviewed."
        if reviewer["agent_id"].strip() in {x.strip() for x in writers}:
            return False, "The writer cannot supply their own independent clarity signoff."
        when = datetime.fromisoformat(receipt.get("reviewed_at", "").replace("Z", "+00:00"))
        if when.tzinfo is None:
            return False, "The editorial review timestamp needs a timezone."
        if receipt.get("decision") != "pass" or receipt.get("unresolved_blockers") != []:
            return False, "The LLM review has not passed or has unresolved readability/content blockers."
        checks = receipt.get("checks")
        if not isinstance(checks, dict) or any(checks.get(k) is not True for k in CHECKS):
            return False, "The actual prose and scientific-meaning preservation checks are incomplete."
        explanation = receipt.get("reader_explanation")
        if not isinstance(explanation, dict) or not all(_text(explanation.get(k)) for k in EXPLANATIONS):
            return False, "The LLM must explain the question, approach, finding, limitations and next step."
        report = receipt.get("report")
        if not isinstance(report, dict) or not _path(report.get("path")) or not _digest(report.get("sha256")):
            return False, "A bound editorial report is required."
        report_bytes = read_at(report["path"])
        if not report_bytes.strip() or hashlib.sha256(report_bytes).hexdigest() != report["sha256"]:
            return False, "The editorial report is absent, empty or differs from the reviewed report."
        artifacts = receipt.get("artifacts")
        if not isinstance(artifacts, list) or not artifacts:
            return False, "The LLM review names no outgoing prose artifacts."
        seen = set()
        for item in artifacts:
            if not isinstance(item, dict) or not _path(item.get("path")) or not _digest(item.get("sha256")):
                return False, "An editorial artifact path or hash is invalid."
            path = item["path"]
            if path in seen:
                return False, "Duplicate artifact in LLM readability review."
            seen.add(path)
            sections = item.get("sections_reviewed")
            if not isinstance(sections, list) or not sections or not all(_text(x) for x in sections):
                return False, f"Record the actual prose sections reviewed in {path}."
            data = document_bytes if path == document else read_at(path)
            if hashlib.sha256(data).hexdigest() != item["sha256"]:
                return False, f"LLM readability review is stale for {path}; review the changed prose."
        if document not in seen:
            return False, "The LLM review does not cover the outgoing manuscript."
        missing = set(required) - seen
        if missing:
            return False, "The LLM review omits required outgoing prose: " + ", ".join(sorted(missing))
        return True, (f"Independent LLM editorial review by {reviewer['agent_id']} covers "
                      f"{len(seen)} unchanged prose artifact(s); report {report['path']}. "
                      "Clarity is the recorded reader judgment, not a numeric score or scientific validation.")
    except (OSError, ValueError, TypeError, KeyError, AttributeError, UnicodeError) as exc:
        return False, f"LLM readability evidence unavailable or malformed at the candidate revision ({type(exc).__name__}): {receipt_path}"
