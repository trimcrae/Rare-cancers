"""Administrative bindings cannot silently change reviewed content or identity."""
import hashlib
import json
from pathlib import Path
import sys
import pytest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import systems_check as sc


def sidecar_path(doc):
    path = doc.parent / "systems" / "document-metadata" / (doc.name + ".json")
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def fixture_binding(tmp_path, monkeypatch):
    monkeypatch.setattr(sc, "REPO", str(tmp_path))
    text = "---\nid: DOC-FROZEN\ntitle: Frozen title\nkind: manuscript\nstatus: draft\n---\nOriginal science.\n"
    doc = tmp_path / "paper.md"
    doc.write_bytes(text.encode())
    binding = {"schema": "emc-document-metadata/1", "document": "paper.md",
               "sha256": hashlib.sha256(doc.read_bytes()).hexdigest(),
               "administrative": {"level": "L3", "status": "live",
                                  "audience": ["reviewers"], "last_verified": "2026-09-10"}}
    return text, doc, binding


@pytest.mark.parametrize("defect", [None, "missing", "hash", "path", "title", "malformed", "field"])
def test_binding_requires_exact_source_and_restricted_fields(tmp_path, monkeypatch, defect):
    text, doc, binding = fixture_binding(tmp_path, monkeypatch)
    if defect == "hash":
        doc.write_bytes((text + "Changed science").encode())
    if defect == "path":
        binding["document"] = "another.md"
    if defect == "title":
        binding["administrative"]["title"] = "Substituted title"
    if defect == "field":
        del binding["administrative"]["audience"]
    if defect != "missing":
        sidecar_path(doc).write_text(
            "{" if defect == "malformed" else json.dumps(binding), encoding="utf-8")
    fields, error = sc._effective_frontmatter(text, "paper.md")
    if defect is None:
        assert error is None and fields["level"] == "L3"
        assert fields["title"] == "Frozen title" and fields["id"] == "DOC-FROZEN"
        assert doc.read_bytes() == text.encode()
    elif defect == "missing":
        assert error is None and fields.get("level") != "L3"
    else:
        assert fields is None and error


def test_binding_cannot_repair_invalid_source_yaml(tmp_path, monkeypatch):
    text, doc, binding = fixture_binding(tmp_path, monkeypatch)
    broken = text.replace("Frozen title", "Unquoted: title")
    doc.write_text(broken, encoding="utf-8")
    binding["sha256"] = hashlib.sha256(doc.read_bytes()).hexdigest()
    sidecar_path(doc).write_text(json.dumps(binding), encoding="utf-8")
    assert sc._effective_frontmatter(broken, "paper.md")[1]


@pytest.mark.parametrize("key,value", [
    ("level", ["L3"]), ("status", {"value": "live"}), ("last_verified", 20260910),
    ("audience", "reviewers"), ("audience", []), ("audience", [1]), ("audience", [" "]),
])
def test_wrong_administrative_types_return_structured_error(tmp_path, monkeypatch, key, value):
    text, doc, binding = fixture_binding(tmp_path, monkeypatch)
    binding["administrative"][key] = value
    sidecar_path(doc).write_text(json.dumps(binding), encoding="utf-8")
    fields, error = sc._effective_frontmatter(text, "paper.md")
    assert fields is None
    assert error.startswith("invalid administrative metadata binding:")
