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


def test_a_v_prefixed_version_is_normalised_before_it_reaches_the_api(monkeypatch, tmp_path):
    """⛔ MEASURED: `--version v1.4` returned HTTP 422 from /api/get-review, because the API wants
    'X.Y' while the platform LABELS its versions 'v1.4' — and this file's own usage examples wrote
    the `v` form. A caller reading either writes the one that fails."""
    seen = {}
    monkeypatch.setattr(aixiv_review, "_request",
                        lambda path, **k: seen.update(k.get("data") and
                                                      json.loads(k["data"]) or {}) or
                        {"review_list": [], "code": 0})
    aixiv_review.main(["fetch", "--aixiv-id", "x", "--version", "v1.4", "--out", str(tmp_path)])
    assert seen["version"] == "1.4", f"the API was sent {seen['version']!r}"


def test_the_filename_keeps_the_form_the_caller_used():
    """The normalisation is at the request boundary only — a human matching an artifact against the
    aiXiv page is looking at the labelled form."""
    assert aixiv_review._api_version("v1.4") == "1.4"
    assert aixiv_review._api_version("1.4") == "1.4"
    assert aixiv_review._api_version("v1.9.3") == "1.9.3"


def test_a_version_that_only_looks_v_prefixed_is_left_alone():
    """`velocity-2` is not a version with a `v` prefix, and stripping it would corrupt the request."""
    assert aixiv_review._api_version("velocity-2") == "velocity-2"


def test_status_reports_a_failed_review_lookup_rather_than_counting_it_as_zero(monkeypatch, capsys):
    """⛔ THE WHOLE POINT OF `status` IS THAT AN EMPTY READING HAS SEVERAL CAUSES.

    A lookup that ERRORS and a lookup that returns no reviews are different facts, and collapsing
    the first into `reviews=0` would rebuild the ambiguity this command exists to resolve — in the
    one place a reader would trust it.
    """
    def _req(path, **k):
        if path.startswith("/api/submissions/public"):
            return [{"aixiv_id": "x", "version": "1.4", "status": "Under Review"}] \
                if "skip=0" in path else []
        raise aixiv_review.AixivError("HTTP 503: upstream unavailable")

    monkeypatch.setattr(aixiv_review, "_request", _req)
    aixiv_review.main(["status", "--aixiv-id", "x"])
    out = capsys.readouterr().out
    assert "LOOKUP FAILED" in out
    assert "reviews=0" not in out


def test_status_says_absent_from_the_listing_is_not_absent_from_aixiv(monkeypatch, capsys):
    """A paper can be missing from the PUBLIC listing without being missing from the platform."""
    monkeypatch.setattr(aixiv_review, "_request", lambda path, **k: [])
    aixiv_review.main(["status", "--aixiv-id", "nope"])
    out = capsys.readouterr().out
    assert "NOT IN THE PUBLIC LISTING" in out
    assert "not the same as absent from aiXiv" in out


def test_status_counts_reviews_per_version(monkeypatch, capsys):
    monkeypatch.setenv("AIXIV_TOKEN", "t")
    def _req(path, **k):
        if path.startswith("/api/submissions/public"):
            return ([{"aixiv_id": "x", "version": "1.3", "status": "Reviewed"},
                     {"aixiv_id": "x", "version": "1.4", "status": "Under Review"},
                     {"aixiv_id": "other", "version": "1.0", "status": "Reviewed"}]
                    if "skip=0" in path else [])
        if path.startswith("/api/get_pending-review-submissions"):
            return [{"aixiv_id": "x", "version": "1.4", "status": "Under Review"}]
        body = json.loads(k["data"])
        return {"review_list": [{"id": 1}] if body["version"] == "1.3" else []}

    monkeypatch.setattr(aixiv_review, "_request", _req)
    aixiv_review.main(["status", "--aixiv-id", "x"])
    out = capsys.readouterr().out
    assert "v1.3" in out and "reviews=1" in out
    assert "v1.4" in out and "reviews=0" in out
    assert "QUEUED v1.4" in out, "the pending queue is what distinguishes queued from never-enqueued"
    assert "other" not in out, "a different paper's row leaked into the report"


def test_status_says_plainly_when_nothing_is_queued(monkeypatch, capsys):
    """⛔ THE FINDING THAT ENDS A WAIT. A version in neither list was never enqueued, and waiting
    longer produces nothing — so this has to be stated, not left for a reader to infer from silence."""
    monkeypatch.setenv("AIXIV_TOKEN", "t")
    def _req(path, **k):
        if path.startswith("/api/submissions/public"):
            return [{"aixiv_id": "x", "version": "1.3", "status": "official review completed"}] \
                if "skip=0" in path else []
        if path.startswith("/api/get_pending-review-submissions"):
            return []
        return {"review_list": []}

    monkeypatch.setattr(aixiv_review, "_request", _req)
    aixiv_review.main(["status", "--aixiv-id", "x"])
    out = capsys.readouterr().out
    assert "NOTHING FOR THIS ID IS QUEUED" in out
    assert "waiting longer will not produce one" in out


def test_an_unreadable_pending_queue_is_an_absent_reading_not_a_verdict(monkeypatch, capsys):
    """⛔ If the queue cannot be read, 'not queued' has NOT been established. Saying otherwise would
    end a wait on the strength of a failed request."""
    monkeypatch.setenv("AIXIV_TOKEN", "t")
    def _req(path, **k):
        if path.startswith("/api/submissions/public"):
            return [{"aixiv_id": "x", "version": "1.3", "status": "done"}] if "skip=0" in path else []
        if path.startswith("/api/get_pending-review-submissions"):
            raise aixiv_review.AixivError("HTTP 500")
        return {"review_list": []}

    monkeypatch.setattr(aixiv_review, "_request", _req)
    aixiv_review.main(["status", "--aixiv-id", "x"])
    out = capsys.readouterr().out
    assert "PENDING QUEUE UNREADABLE" in out
    assert "NOTHING FOR THIS ID IS QUEUED" not in out


def test_the_pending_queue_sends_the_token_in_the_query_string_and_never_logs_it(monkeypatch, capsys):
    """⛔ MEASURED: this endpoint alone wants `?token=`, not a bearer header (HTTP 422 otherwise).

    ⚠ AND THE TOKEN MUST NOT REACH THE LOG. This repository's Actions logs are world-readable, so
    the second assertion is not hygiene — it is the difference between a diagnostic and a leaked
    credential.
    """
    monkeypatch.setenv("AIXIV_TOKEN", "s3cret-token")
    seen = {}

    def _req(path, **k):
        if path.startswith("/api/submissions/public"):
            return [{"aixiv_id": "x", "version": "1.3", "status": "done"}] if "skip=0" in path else []
        if path.startswith("/api/get_pending-review-submissions"):
            seen["path"] = path
            return []
        return {"review_list": []}

    monkeypatch.setattr(aixiv_review, "_request", _req)
    aixiv_review.main(["status", "--aixiv-id", "x"])
    assert "token=s3cret-token" in seen["path"], "the token did not reach the query string"
    assert "s3cret-token" not in capsys.readouterr().out, "the token was printed to a public log"


def test_status_without_a_token_declines_to_claim_nothing_is_queued(monkeypatch, capsys):
    """No credential means the queue was NOT read, which is not the same as reading it empty."""
    monkeypatch.delenv("AIXIV_TOKEN", raising=False)
    def _req(path, **k):
        if path.startswith("/api/submissions/public"):
            return [{"aixiv_id": "x", "version": "1.3", "status": "done"}] if "skip=0" in path else []
        return {"review_list": []}

    monkeypatch.setattr(aixiv_review, "_request", _req)
    aixiv_review.main(["status", "--aixiv-id", "x"])
    out = capsys.readouterr().out
    assert "PENDING QUEUE NOT CHECKED" in out
    assert "NOTHING FOR THIS ID IS QUEUED" not in out


def test_a_credential_in_a_query_string_is_redacted_before_it_reaches_an_exception(monkeypatch):
    """⛔ THE REAL LEAK, AND THE PREVIOUS TEST OF IT WAS AGREEING WITH ITSELF.

    `get_pending-review-submissions` takes its token as a query parameter and `_request`
    interpolated the whole path into its error text, so a 401 printed a live credential into a
    world-readable Actions log. GitHub's masking rendered it `***`; masking is a backstop, not a
    control. This exercises the REAL error path rather than a mock that raises without one.
    """
    import urllib.error

    def _boom(req, *a, **k):
        raise urllib.error.HTTPError(req.full_url, 401, "Unauthorized", {},
                                     __import__("io").BytesIO(b'{"detail":"Invalid token"}'))

    monkeypatch.setattr(aixiv_review.urllib.request, "urlopen", _boom)
    with pytest.raises(aixiv_review.AixivError) as e:
        aixiv_review._request("/api/get_pending-review-submissions?token=s3cret-token",
                              method="GET")
    assert "s3cret-token" not in str(e.value), "the token reached the exception text"
    assert "<redacted>" in str(e.value)
    assert "Invalid token" in str(e.value), "the server's own message must survive redaction"


def test_redaction_leaves_ordinary_paths_alone():
    """A redactor that mangles every path makes every diagnostic worse."""
    assert aixiv_review._redact("/api/get-review") == "/api/get-review"
    assert aixiv_review._redact("/api/submissions/public?skip=0&limit=100") == (
        "/api/submissions/public?skip=0&limit=100")
