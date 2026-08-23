"""Guards for scripts/aixiv_review.py.

⛔ THE ONE THAT MATTERS IS THE OUTWARD-FACING REFUSAL. Everything else here is ordinary argument
handling; `test_submit_refuses_without_the_explicit_acknowledgement` is the test that stops a future
session from uploading a manuscript to a third party as a side effect of running a review round.

⚠ EVERY TEST BELOW ASSERTS THAT NO NETWORK CALL HAPPENS, by making the transport itself explode.
Mocking the client's own helper would test the mock (`ci-escape-hatches`: "mock the thing under test
and you test the mock"), so the seam that is patched is `urllib.request.urlopen` — the last thing
before the socket.
"""
import importlib.util
import json
import os
import sys

import pytest

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_spec = importlib.util.spec_from_file_location(
    "aixiv_review", os.path.join(REPO, "scripts", "aixiv_review.py"))
aixiv_review = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(aixiv_review)


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    """Any real HTTP call fails the test, loudly and by name."""
    def _boom(*a, **k):
        raise AssertionError("a network call was attempted; this test must not reach aiXiv")
    monkeypatch.setattr(aixiv_review.urllib.request, "urlopen", _boom)
    monkeypatch.delenv("AIXIV_TOKEN", raising=False)


def _meta(tmp_path, **over):
    meta = {
        "title": "T", "authorship_type": "ai", "authors": ["A"],
        "corresponding_author": "a@example.org", "category": ["Q"],
        "keywords": ["k"], "license": "CC-BY-4.0", "doc_type": "paper",
    }
    meta.update(over)
    p = tmp_path / "meta.json"
    p.write_text(json.dumps(meta))
    return str(p)


def _pdf(tmp_path):
    p = tmp_path / "paper.pdf"
    p.write_bytes(b"%PDF-1.4 fake")
    return str(p)


def test_submit_refuses_without_the_explicit_acknowledgement(tmp_path, capsys):
    """The gate that keeps a review round from becoming a publication."""
    rc = aixiv_review.main([
        "submit", "--pdf", _pdf(tmp_path), "--meta", _meta(tmp_path)])
    assert rc == 1
    err = capsys.readouterr().err
    assert "refusing to submit" in err
    assert "outward-facing" in err


def test_submit_dry_run_needs_no_token_and_no_acknowledgement(tmp_path, capsys):
    rc = aixiv_review.main([
        "submit", "--pdf", _pdf(tmp_path), "--meta", _meta(tmp_path), "--dry-run"])
    assert rc == 0
    assert "DRY RUN" in capsys.readouterr().out


def test_a_dry_run_calls_both_publicity_values_a_publication(tmp_path, capsys):
    """⛔ MEASURED 2026-08-22: is_public=0 served the paper to an unauthenticated reader anyway.

    An earlier version of this test asserted the `--public 0` dry run printed "UNVERIFIED", which
    encoded the hope that the flag was access control. It is not. Both values must read as a
    publication, because both are one.
    """
    for pub in ("0", "1"):
        aixiv_review.main(["submit", "--pdf", _pdf(tmp_path), "--meta", _meta(tmp_path),
                           "--public", pub, "--dry-run"])
        out = capsys.readouterr().out
        assert "PUBLICATION" in out, f"--public {pub} must read as a publication"
        assert "non-public" not in out.lower()


@pytest.mark.parametrize("missing", sorted(aixiv_review.REQUIRED_META))
def test_every_required_field_is_checked_before_the_network(tmp_path, missing, capsys):
    """Single-site mutation per field — a validator that checks all-but-one reads as correct."""
    meta = _meta(tmp_path, **{missing: ""})
    rc = aixiv_review.main([
        "submit", "--pdf", _pdf(tmp_path), "--meta", meta, "--dry-run"])
    assert rc == 1
    assert missing in capsys.readouterr().err


def test_new_version_refuses_without_the_explicit_acknowledgement(tmp_path, capsys):
    """A revision is a publication too, and it does not withdraw what the previous version said."""
    rc = aixiv_review.main(["new-version", "--aixiv-id", "aixiv.260822.000005",
                            "--pdf", _pdf(tmp_path), "--meta", _meta(tmp_path)])
    assert rc == 1
    assert "refusing to post a new version" in capsys.readouterr().err


def test_new_version_targets_the_versions_endpoint_of_that_paper(tmp_path, capsys):
    aixiv_review.main(["new-version", "--aixiv-id", "aixiv.260822.000005",
                       "--pdf", _pdf(tmp_path), "--meta", _meta(tmp_path), "--dry-run"])
    assert "/api/agent/submit/aixiv.260822.000005/versions" in capsys.readouterr().out


def test_review_defaults_the_abs_url_from_the_id(tmp_path, capsys):
    aixiv_review.main(["review", "--aixiv-id", "aixiv.260822.000001", "--version", "v1.0",
                       "--pdf", _pdf(tmp_path), "--seed", "20260822", "--dry-run"])
    out = capsys.readouterr().out
    assert "/abs/aixiv.260822.000001" in out
    assert '"seed": "20260822"' in out


def test_missing_token_names_how_to_mint_one():
    with pytest.raises(aixiv_review.AixivError) as e:
        aixiv_review._token()
    assert "/api/agents/" in str(e.value)
    assert "ONLY ONCE" in str(e.value)


def test_no_reviews_is_reported_as_an_absent_reading_not_a_pass(monkeypatch, capsys):
    """⛔ The failure this repository keeps paying for: silence read as a clean result."""
    monkeypatch.setattr(aixiv_review, "_request", lambda *a, **k: {"review_list": [], "code": 0})
    aixiv_review.main(["fetch", "--aixiv-id", "x", "--version", "v1.0"])
    out = capsys.readouterr().out
    assert "NOT a verdict" in out


def test_every_request_carries_a_browser_user_agent(monkeypatch):
    """⛔ Cloudflare answers urllib's default signature with 403 "error code: 1010" — which reads
    as a bad token and sends the next hour into re-minting a credential that was fine."""
    seen = {}

    class _Resp:
        def read(self): return b"{}"
        def __enter__(self): return self
        def __exit__(self, *a): return False

    def _capture(req, *a, **k):
        seen["ua"] = req.get_header("User-agent")
        return _Resp()

    monkeypatch.setattr(aixiv_review.urllib.request, "urlopen", _capture)
    aixiv_review._request("/api/health", method="GET")
    assert seen["ua"] and "Mozilla/5.0" in seen["ua"]
    assert "urllib" not in seen["ua"].lower()


def test_verify_never_prints_the_response_body(monkeypatch, capsys):
    """⛔ Actions logs here are world-readable. A raw dump would publish the account's e-mail."""
    monkeypatch.setenv("AIXIV_TOKEN", "t")
    monkeypatch.setattr(aixiv_review, "_request", lambda path, **k: (
        {"has_profile": True, "email": "private@example.org", "secret_field": "leak-me"}
        if "profile" in path else
        [{"name": "hardening", "scopes": ["submit", "review"], "id": 7}]))
    aixiv_review.main(["verify"])
    out = capsys.readouterr().out
    assert "private@example.org" not in out
    assert "leak-me" not in out
    assert "VERIFY OK" in out


def test_verify_passes_when_only_the_user_profile_call_fails(monkeypatch, capsys):
    """⛔ An agent token CANNOT satisfy /api/profile/me/* — it is not a Clerk JWT. Failing the run
    on a check that cannot pass trains the reader to ignore the verdict."""
    monkeypatch.setenv("AIXIV_TOKEN", "t")

    def _req(path, **k):
        if "profile" in path:
            raise aixiv_review.AixivError("HTTP 401: Malformed JWT: cannot parse header")
        return [{"name": "Emc", "scopes": ["discuss", "reply", "review", "submit"]}]

    monkeypatch.setattr(aixiv_review, "_request", _req)
    rc = aixiv_review.main(["verify"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "VERIFY OK" in out
    assert "expected for an agent token" in out


def test_verify_fails_when_no_agent_carries_the_review_scope(monkeypatch, capsys):
    """A token that authenticates and cannot review fails LATER, on a real paper, unless caught here."""
    monkeypatch.setenv("AIXIV_TOKEN", "t")
    monkeypatch.setattr(aixiv_review, "_request", lambda path, **k: (
        {"has_profile": True} if "profile" in path else
        [{"name": "submitter", "scopes": ["submit"]}]))
    rc = aixiv_review.main(["verify"])
    out = capsys.readouterr().out
    assert rc == 1
    assert "'review' SCOPE" in out
    assert "VERIFY INCOMPLETE" in out


def test_verify_says_so_when_no_agent_exists_at_all(monkeypatch, capsys):
    monkeypatch.setenv("AIXIV_TOKEN", "t")
    monkeypatch.setattr(aixiv_review, "_request", lambda path, **k: (
        {"has_profile": True} if "profile" in path else []))
    aixiv_review.main(["verify"])
    assert "NO AGENTS REGISTERED" in capsys.readouterr().out


def test_fetch_writes_the_raw_payload_verbatim(monkeypatch, tmp_path):
    """`review_results` is typed `string`; we store what came back rather than a parse of it."""
    payload = {"review_list": [{"id": 1, "reviewer": "r", "create_time": "t",
                                "review_results": "not json at all"}], "code": 0}
    monkeypatch.setattr(aixiv_review, "_request", lambda *a, **k: payload)
    aixiv_review.main(["fetch", "--aixiv-id", "x", "--version", "v1.0", "--out", str(tmp_path)])
    written = json.loads((tmp_path / "x-v1.0-reviews.json").read_text())
    assert written == payload
