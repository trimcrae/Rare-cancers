"""Synthetic receipts exercise publication failures, not actual paper approvals."""
import copy
import hashlib
import json
from pathlib import Path
import sys
from types import SimpleNamespace

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "research" / "autonomy"))
import editorial_readability as ER


DOC = "research/manuscripts/example.md"
SI = "research/manuscripts/example-si.md"
RECEIPT = "research/autonomy/readability-reviews/PUB-EXAMPLE.json"
REPORT = "research/autonomy/readability-reviews/reports/example.md"


def digest(data):
    return hashlib.sha256(data).hexdigest()


@pytest.fixture
def evidence():
    files = {DOC: b"# Abstract\n\nWe compared two groups. The small study does not establish treatment benefit.\n",
             SI: b"The supplementary methods retain uncertainty and negative results.\n",
             REPORT: b"Synthetic test review. The reader understands the comparison and its limitations.\n"}
    files[ER.INVENTORY] = json.dumps({"schema": "emc-editorial-prose-inventory/1",
                                    "papers": {"PUB-EXAMPLE": [DOC, SI]}}).encode()
    receipt = {
        "schema": ER.SCHEMA, "paper_id": "PUB-EXAMPLE",
        "review_kind": "independent_llm_editorial", "reviewed_at": "2026-09-12T11:30:00Z",
        "reviewer": {"agent_id": "synthetic-reader", "model": "synthetic-test-model",
                     "execution_evidence": "Synthetic fixture only; no real review occurred."},
        "writer_ids": ["synthetic-writer"], "decision": "pass", "unresolved_blockers": [],
        "checks": {key: True for key in ER.CHECKS},
        "reader_explanation": {key: "Synthetic reader explanation." for key in ER.EXPLANATIONS},
        "report": {"path": REPORT, "sha256": digest(files[REPORT])},
        "artifacts": [{"path": path, "sha256": digest(files[path]),
                       "sections_reviewed": ["All reader-facing sections in synthetic fixture"]}
                      for path in (DOC, SI)]}
    return files, receipt


def evaluate(evidence, change=None, missing=None):
    files, receipt = copy.deepcopy(evidence)
    if change:
        change(files, receipt)
    files[RECEIPT] = json.dumps(receipt).encode()
    if missing:
        del files[missing]

    def read_at(path):
        if path not in files:
            raise FileNotFoundError(path)
        return files[path]

    return ER.verify_review("PUB-EXAMPLE", DOC, files[DOC], read_at)


def test_complete_bound_review_accepts_unchanged_artifacts(evidence):
    assert evaluate(evidence)[0]


@pytest.mark.parametrize("missing", [RECEIPT, REPORT, SI, ER.INVENTORY])
def test_missing_evidence_never_becomes_a_readability_pass(evidence, missing):
    assert not evaluate(evidence, missing=missing)[0]


@pytest.mark.parametrize("path", [DOC, SI, REPORT])
def test_changed_prose_or_report_invalidates_the_receipt(evidence, path):
    def change(files, _):
        files[path] += b" A new sentence changes the reviewed content.\n"
    assert not evaluate(evidence, change)[0]


def test_a_writer_cannot_sign_off_their_own_clarity(evidence):
    def change(_, receipt):
        receipt["reviewer"]["agent_id"] = "synthetic-writer"
    assert not evaluate(evidence, change)[0]


@pytest.mark.parametrize("field,value", [
    ("review_kind", "automated_readability_score"),
    ("paper_id", "PUB-ANOTHER"), ("decision", "needs_repair"),
    ("unresolved_blockers", ["A crucial limitation was removed."]),
    ("reviewed_at", "2026-09-12T11:30:00"),
])
def test_a_metric_wrong_paper_or_incomplete_review_cannot_pass(evidence, field, value):
    assert not evaluate(evidence, lambda _, r: r.update({field: value}))[0]


@pytest.mark.parametrize("key", ER.CHECKS)
def test_every_actual_editorial_check_is_required(evidence, key):
    def change(_, receipt):
        receipt["checks"][key] = False
    assert not evaluate(evidence, change)[0]


def test_missing_reader_explanation_cannot_be_replaced_by_a_score(evidence):
    def change(_, receipt):
        receipt["reader_explanation"]["main_limitations"] = " "
        receipt["flesch_kincaid"] = 5
    assert not evaluate(evidence, change)[0]


def test_review_of_only_the_supplement_does_not_cover_the_manuscript(evidence):
    def change(_, receipt):
        receipt["artifacts"] = receipt["artifacts"][1:]
    assert not evaluate(evidence, change)[0]


def test_omitting_the_supplement_from_the_receipt_cannot_approve_it(evidence):
    def change(files, receipt):
        receipt["artifacts"] = receipt["artifacts"][:1]
        files[SI] += b" Unreviewed supplemental claims."
    assert not evaluate(evidence, change)[0]


@pytest.mark.parametrize("required", [[], [SI], [DOC, SI, SI]])
def test_unknown_incomplete_or_duplicate_authoritative_inventory_fails(evidence, required):
    def change(files, _):
        files[ER.INVENTORY] = json.dumps({"schema": "emc-editorial-prose-inventory/1",
                                        "papers": {"PUB-EXAMPLE": required}}).encode()
    assert not evaluate(evidence, change)[0]


def test_unrelated_new_bytes_do_not_invalidate_an_unchanged_review(evidence):
    assert evaluate(evidence, lambda files, _: files.update({"unrelated.txt": b"new"}))[0]


def test_publication_clause_requires_review_from_the_requested_revision(evidence, monkeypatch, tmp_path):
    import publish_bar as bar
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[2] / "research" / "manuscripts"))
    files, receipt = evidence
    pinned = dict(files)
    pinned[RECEIPT] = json.dumps(receipt).encode()
    monkeypatch.setattr(bar, "REPO", tmp_path)
    monkeypatch.setattr(bar, "_endpoint", lambda _: {"document": {"file": DOC}})
    calls = []

    def git_show(argv, **kwargs):
        calls.append(argv)
        assert argv[:2] == ["git", "show"]
        assert argv[2].startswith("candidate:")
        path = argv[2].split(":", 1)[1]
        return SimpleNamespace(returncode=0 if path in pinned else 1,
                               stdout=pinned.get(path, b""))

    monkeypatch.setattr(bar.subprocess, "run", git_show)
    result = bar.clause_7_readable_enough_to_review("PUB-EXAMPLE", "candidate")
    assert result["ok"], result
    del pinned[RECEIPT]
    # A plausible review in the working tree cannot approve an older unreviewed candidate.
    working = tmp_path / RECEIPT
    working.parent.mkdir(parents=True)
    working.write_text(json.dumps(receipt), encoding="utf-8")
    assert not bar.clause_7_readable_enough_to_review("PUB-EXAMPLE", "candidate")["ok"]
    assert calls
