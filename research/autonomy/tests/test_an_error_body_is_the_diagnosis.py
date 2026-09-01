#!/usr/bin/env python3
"""A failed HTTP read must carry the SERVER'S OWN account of why, not just its status code.

⛔⛔ THE NEAR MISS THIS SUITE WAS WRITTEN AGAINST, MEASURED 2026-09-01 (S24-CALIBRATION §5(d)). A
vaccine-calibration run sent 90 queries to IEDB. All 90 returned HTTP 400. The handler recorded 90
identical `HTTPError: HTTP Error 400` lines and **discarded every response body**, so the seat
diagnosed the 400s from the status code alone — an HLA name's `*` and `:` breaking a PostgREST
filter value — and rewrote a function on that reading. It was a "probably X" and it was wrong. The
next run kept the body, and the server had been saying so in its own words the entire time:

    {"message":"Unsupported request",
     "details":"Query string appears to include an offset parameter without an order parameter."}

**What caught the wrong diagnosis was not reasoning; it was four lines that keep an error body.**

★ WHY THIS IS A GUARD AND NOT A TIDINESS PREFERENCE. `urlopen` raises `HTTPError` with the body
still unread ON the exception object, and `str(HTTPError)` yields `HTTP Error 400: Bad Request` —
the REASON, never the body. So the natural, idiomatic, everywhere-in-this-repo handler
(`"%s: %s" % (type(exc).__name__, exc)`) destroys the one artifact that discriminates between the
competing hypotheses, which is precisely what CLAUDE.md §4 requires be produced. The failure is
silent in the worst direction: downstream, an error that yields an empty list is indistinguishable
from a measured absence.

⚠ WHAT THIS SUITE DOES NOT CLAIM. It covers `await_ci.py` and `gates_verdict.py` — the loop's own
two instruments — and nothing else. A census run the same day (S37-ERROR-BODIES) found **44** other
`except ...HTTPError` handlers under `research/` and `scripts/` that discard the body, of which four
carry a real false-absence risk. Those are named in that seat's findings file and are NOT guarded
here; an absent guard is not evidence of an absent defect.
"""

from __future__ import annotations

import email.message
import io
import json
import os
import sys
import urllib.error

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

import await_ci  # noqa: E402
import gates_verdict  # noqa: E402

SHA = "0" * 40

#: The IEDB body from the run that produced this suite, verbatim. Kept as the fixture because the
#: point is not "some body" — it is that THIS sentence, which named the real cause, was thrown away.
IEDB_400_BODY = json.dumps({
    "message": "Unsupported request",
    "details": "Query string appears to include an offset parameter without an order parameter. "
               "Please resubmit the query with an order parameter to ensure consistent paging. "
               "The query was not sent to the API.",
})


def http_error(code=400, reason="Bad Request", body=b"", headers=None, url="https://example/x"):
    """Build an `HTTPError` shaped exactly like the one `urlopen` raises: body unread, on the object."""
    hdrs = email.message.Message()
    for k, v in (headers or {}).items():
        hdrs.add_header(k, v)
    if isinstance(body, str):
        body = body.encode()
    return urllib.error.HTTPError(url, code, reason, hdrs, io.BytesIO(body))


# --- 1. positive controls -------------------------------------------------------------------------

def test_the_helper_exists_and_is_used_by_both_instruments():
    """If this were missing, every assertion below would fail for the wrong reason."""
    assert callable(getattr(await_ci, "describe_http_error", None))
    assert gates_verdict.await_ci is await_ci, "gates_verdict must share the helper, not copy it"


def test_a_non_http_exception_still_describes_itself():
    """⚠ A timeout carries no body and must not be made to look as though it does."""
    out = await_ci.describe_http_error(TimeoutError("timed out"))
    assert "TimeoutError" in out and "timed out" in out
    assert "body" not in out


# --- 2. the finding: the body survives -------------------------------------------------------------

def test_the_servers_own_explanation_survives_the_handler():
    """⛔ THE REGRESSION. Without this, the run that produced this suite happens again."""
    out = await_ci.describe_http_error(http_error(body=IEDB_400_BODY))
    assert "offset parameter without an order parameter" in out, (
        "the response body was discarded — this is the 2026-09-01 defect exactly")
    assert "HTTP 400" in out


def test_two_different_400s_do_not_render_identically():
    """⛔⛔ THE ONE ASSERTION A `str(exc)` IMPLEMENTATION CANNOT PASS.

    `str(HTTPError)` is `HTTP Error 400: Bad Request` for both of these. That is the whole defect:
    90 failures wearing one sentence. Same status, same reason, different causes — and a diagnostic
    that cannot separate them is not a diagnostic.
    """
    a = await_ci.describe_http_error(http_error(body=IEDB_400_BODY))
    b = await_ci.describe_http_error(http_error(body='{"message":"invalid allele filter"}'))
    assert a != b
    assert "invalid allele filter" in b


def test_an_empty_body_says_so_rather_than_going_quiet():
    """⛔ 'I did not read it' and 'there was nothing there' are opposite facts (CLAUDE.md §4).

    A describer that renders an empty body the same way it renders an unread one hands the next
    reader an absent reading dressed as a reading of absence.
    """
    out = await_ci.describe_http_error(http_error(code=502, reason="Bad Gateway", body=b""))
    assert "(empty body)" in out
    assert "HTTP 502" in out


def test_a_long_body_is_marked_truncated_and_never_silently_cut():
    """A cut explanation reads as a complete one, which is worse than no explanation."""
    out = await_ci.describe_http_error(http_error(body="x" * 5000))
    assert "TRUNCATED" in out
    assert len(out) < 1200, "the whole point of the bound is that a poll line stays one line"


def test_the_body_is_read_exactly_once_and_the_second_read_is_honest():
    """⚠ The body is a STREAM. A second describe must report an empty body, never invent one."""
    exc = http_error(body=IEDB_400_BODY)
    first = await_ci.describe_http_error(exc)
    second = await_ci.describe_http_error(exc)
    assert "offset parameter" in first
    assert "(empty body)" in second


# --- 3. a 403 is two different problems and the headers separate them -----------------------------

def test_a_rate_limited_403_names_the_reset():
    """⛔ GitHub answers 403 both for 'you may not read this' and for the legacy rate limit.

    One clears in minutes and one never clears. A handler that prints `HTTP Error 403: Forbidden`
    for both tells an operator nothing about whether waiting is a plan or a waste.
    """
    out = await_ci.describe_http_error(http_error(
        code=403, reason="Forbidden", body='{"message":"API rate limit exceeded"}',
        headers={"X-RateLimit-Remaining": "0", "X-RateLimit-Reset": "1756742400"}))
    assert "remaining=0" in out
    assert "resets" in out
    assert "rate limit exceeded" in out


def test_a_permission_403_does_not_claim_a_rate_limit():
    out = await_ci.describe_http_error(http_error(
        code=403, reason="Forbidden", body='{"message":"Resource not accessible by integration"}',
        headers={"X-RateLimit-Remaining": "4998"}))
    assert "remaining=4998" in out
    assert "resets" not in out
    assert "not accessible by integration" in out


# --- 4. await_ci: the invariant that matters most --------------------------------------------------

def _poll_with(monkeypatch, raises, capsys, deadline=600, interval=45):
    calls = {"n": 0}

    def fake_get(url, token, timeout=25):
        calls["n"] += 1
        raise raises()

    monkeypatch.setattr(await_ci, "_get", fake_get)
    monkeypatch.setattr(await_ci.time, "sleep", lambda *_: None)
    rc = await_ci.poll("o/r", SHA, deadline, interval, None)
    return rc, calls["n"], capsys.readouterr().out


def test_an_http_error_can_NEVER_make_the_poller_report_green(monkeypatch, capsys):
    """⛔⛔ THE MOST SERIOUS QUESTION ASKED OF THIS FILE, ANSWERED AS A GUARD RATHER THAN A READING.

    This poller is the instrument the loop uses to decide whether the trunk is healthy. If a
    discarded body could make it exit 0, that would be the worst instance of this defect in the
    repository. It cannot: the `except` branch has no path to `return 0`. The reading is that the
    real exposure is one rung down — UNKNOWN with the cause destroyed — and this test pins the half
    that is safe so a future edit cannot quietly move it.
    """
    for code in (400, 401, 403, 404, 422, 500, 503):
        rc, _, _ = _poll_with(monkeypatch, lambda c=code: http_error(code=c, body=b"nope"), capsys)
        assert rc == 2, f"HTTP {code} produced exit {rc} — an error must never be a verdict"


def test_the_poll_line_carries_the_body_not_just_the_exception_class(monkeypatch, capsys):
    """⛔ `API read failed (HTTPError)` was the whole line for a year. It named nothing."""
    _, _, out = _poll_with(
        monkeypatch, lambda: http_error(code=500, body=IEDB_400_BODY), capsys)
    assert "offset parameter without an order parameter" in out


def test_a_deterministic_status_is_refused_now_not_eight_polls_later(monkeypatch, capsys):
    """⛔ A 404 on `/repos/<slug>/actions/runs` means the SLUG is wrong — a real repository with no
    runs answers 200 with an empty list. Polling that eight times over six minutes and then saying
    UNKNOWN is a fake stall manufactured by the poller, which is the exact failure class this file's
    docstring says it exists to remove.
    """
    for code in sorted(await_ci.FATAL_HTTP):
        rc, n, out = _poll_with(
            monkeypatch, lambda c=code: http_error(code=c, body=b'{"message":"Not Found"}'), capsys)
        assert rc == 2
        assert n == 1, f"HTTP {code} was retried {n} times; it will not change by asking again"
        assert "will not change by asking again" in out
    assert 403 not in await_ci.FATAL_HTTP, (
        "403 is both a rate limit and a permission denial; refusing it on the first read would "
        "turn a four-minute wait into a hard failure")


def test_a_transient_status_is_still_retried(monkeypatch, capsys):
    """⚠ The mirror of the test above: the fix must not turn a hiccup into a refusal."""
    rc, n, out = _poll_with(monkeypatch, lambda: http_error(code=503, body=b"upstream"), capsys)
    assert rc == 2
    assert n == 8, f"a 503 was tried {n} times; the retry ladder is 8"
    assert "Last cause" in out and "upstream" in out


# --- 5. gates_verdict: unmeasured is honest, but it must still name the cause ----------------------

def test_the_gate_reader_writes_nothing_and_says_why(monkeypatch, tmp_path, capsys):
    """⛔ Failing closed is only half the job.

    `gates_green: unmeasured` is honest and it is also INERT — it names no action. This row had
    already sat unmeasured for 47.2 h once (see `test_main_keeps_a_per_commit_verdict`). A rate
    limit that clears in four minutes and a token that will never work again must not print the
    same sentence.
    """
    out_file = tmp_path / "gates.json"
    monkeypatch.setenv("GITHUB_REPOSITORY", "trimcrae/Rare-cancers")
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    monkeypatch.delenv("GH_TOKEN", raising=False)

    def boom(token, repo=None):
        raise http_error(code=403, reason="Forbidden",
                         body='{"message":"API rate limit exceeded for 20.1.2.3"}',
                         headers={"X-RateLimit-Remaining": "0", "X-RateLimit-Reset": "1756742400"})

    monkeypatch.setattr(gates_verdict, "fetch", boom)
    rc = gates_verdict.main(["--out", str(out_file)])

    assert rc == 0, "the tick must survive an unreadable gate — it also publishes the board"
    assert not out_file.exists(), "a guessed verdict is strictly worse than the unmeasured it replaces"
    text = capsys.readouterr().out
    assert "rate limit exceeded for 20.1.2.3" in text, "the body was discarded"
    assert "remaining=0" in text and "resets" in text
    assert "unmeasured" in text


def test_the_gate_reader_still_fails_closed_on_a_bodiless_error(monkeypatch, tmp_path, capsys):
    """⚠ The describer must not become a new way for the handler itself to fail."""
    out_file = tmp_path / "gates.json"
    monkeypatch.setenv("GITHUB_REPOSITORY", "trimcrae/Rare-cancers")
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    monkeypatch.delenv("GH_TOKEN", raising=False)
    monkeypatch.setattr(gates_verdict, "fetch",
                        lambda *_a, **_k: (_ for _ in ()).throw(urllib.error.URLError("no route")))
    assert gates_verdict.main(["--out", str(out_file)]) == 0
    assert not out_file.exists()
    assert "no route" in capsys.readouterr().out


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
