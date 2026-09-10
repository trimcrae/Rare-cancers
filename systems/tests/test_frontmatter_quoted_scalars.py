"""Quoted YAML scalars retain document identity and status semantics."""
from pathlib import Path
import sys
import pytest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import systems_check as sc

@pytest.mark.parametrize("quote", ["'", chr(34)])
@pytest.mark.parametrize("status", ["live", "immutable", "not-a-valid-status"])
def test_quoted_document_scalars_match_plain_values(quote, status):
    plain = "---\nid: DOC-QUOTED-PROBE\nstatus: " + status + "\n---\n"
    quoted = "---\nid: " + quote + "DOC-QUOTED-PROBE" + quote + "\nstatus: " + quote + status + quote + "\n---\n"
    assert sc._frontmatter(quoted) == sc._frontmatter(plain)
    assert sc._frontmatter(quoted)["status"] == status

@pytest.mark.parametrize("quoted_id", ['"DOC-DUPLICATE"', "'DOC-DUPLICATE'"])
def test_quoted_id_cannot_hide_duplicate_document(monkeypatch, quoted_id):
    docs = [("live.md", "---\nid: DOC-DUPLICATE\n---\n"),
            ("archive/old.md", "---\nid: " + quoted_id + "\n---\n")]
    monkeypatch.setattr(sc, "_walk_md", lambda skip: iter(docs))
    findings = sc.Findings()
    sc.check_doc_ids({}, findings)
    assert len(findings.errors) == 1
    assert "[D6]" in findings.errors[0]
    assert "live.md" in findings.errors[0] and "archive/old.md" in findings.errors[0]

def test_scalar_escapes_are_decoded_without_changing_unquoted_fields():
    text = "---\nid: DOC-ESCAPE\ntitle: 'It''s quoted'\naudience: [author, reviewers]\n---\n"
    fields = sc._frontmatter(text)
    assert fields["title"] == "It's quoted"
    assert fields["audience"] == "[author, reviewers]"
