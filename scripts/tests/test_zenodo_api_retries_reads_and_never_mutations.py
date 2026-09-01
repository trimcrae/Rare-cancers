"""⛔ A TRANSIENT 504 MUST NOT KILL A DEPOSIT RUN, AND A RETRY MUST NEVER REPEAT A MUTATION.

⚠ WHY THIS EXISTS, MEASURED 2026-09-01 (AUT-PD-199). `zenodo_deposit.api` had no retry: any
`HTTPError` raised `SystemExit` on the spot. Three runs died on transient 5xx responses and the
cycle concluded "Zenodo's deposit API is down" — then a `record=verify` dispatch read the published
record in three seconds. The service was healthy throughout; the client simply could not survive one
bad response.

⛔ AND THE OTHER HALF IS THE DANGEROUS ONE. The first failure was a 504 on the GET that FOLLOWED a
successful `actions/newversion` POST, which orphaned draft 22229096 with its inherited files still
attached. Retrying that POST would have made a second orphan. So the retry is scoped to methods with
no side effect, and this file asserts BOTH halves — that reads recover, and that writes do not
repeat. A retry that helped and also double-published would be worse than no retry at all.
"""
import os
import sys
import urllib.error

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(REPO, "scripts"))

import zenodo_deposit as Z  # noqa: E402


class _Resp:
    def __init__(self, payload=b'{"ok": true}'):
        self._payload = payload

    def read(self):
        return self._payload

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


def _http_error(code):
    return urllib.error.HTTPError("https://zenodo.org/api/x", code, "boom", {},
                                  __import__("io").BytesIO(b"gateway timeout"))


def _patch(monkeypatch, outcomes):
    """`outcomes` is a list of status codes (int) or None for success. Returns the call log."""
    calls = []

    def fake_urlopen(req, timeout=None):
        calls.append(req.get_method())
        nxt = outcomes[len(calls) - 1] if len(calls) <= len(outcomes) else None
        if nxt is None:
            return _Resp()
        raise _http_error(nxt)

    monkeypatch.setattr(Z.urllib.request, "urlopen", fake_urlopen)
    return calls


@pytest.mark.parametrize("code", sorted(Z._RETRY_STATUS))
def test_a_transient_failure_on_a_read_is_retried_and_recovers(monkeypatch, code):
    """The defect this closes: one 5xx killed the run."""
    calls = _patch(monkeypatch, [code, None])
    out = Z.api("https://zenodo.org/api", "tok", "GET", "/deposit/depositions/1",
                _sleep=lambda s: None)
    assert out == {"ok": True}
    assert calls == ["GET", "GET"], "the read should have been retried exactly once"


def test_a_read_that_never_recovers_still_fails_and_says_it_was_retried(monkeypatch):
    calls = _patch(monkeypatch, [504] * 10)
    with pytest.raises(SystemExit) as exc:
        Z.api("https://zenodo.org/api", "tok", "GET", "/x", _sleep=lambda s: None)
    assert len(calls) == Z._RETRY_ATTEMPTS, "the attempt bound is not being honoured"
    assert "attempt(s)" in str(exc.value), (
        "an exhausted retry and a one-shot failure must not read alike — the message has to say "
        "which happened, or the next reader infers it from the wall clock")


@pytest.mark.parametrize("method", ["POST", "PUT", "DELETE"])
def test_a_mutation_is_never_retried(monkeypatch, method):
    """⛔ THE HALF THAT PROTECTS THE RECORD. `actions/newversion` creates a draft and
    `actions/publish` is irreversible; repeating either is worse than failing."""
    calls = _patch(monkeypatch, [504, None])
    with pytest.raises(SystemExit) as exc:
        Z.api("https://zenodo.org/api", "tok", method, "/deposit/depositions/1/actions/newversion",
              payload={}, _sleep=lambda s: None)
    assert calls == [method], f"{method} was retried; a mutation must fail on the first error"
    assert "unsafe method" in str(exc.value)


@pytest.mark.parametrize("code", [400, 401, 403, 404, 409])
def test_a_client_error_on_a_read_is_not_retried(monkeypatch, code):
    """A 4xx is the server saying 'not like that'. Repeating it is noise, and on 2026-09-01 one of
    the three 'failures' was a 400 that was Zenodo correctly refusing to open a second version."""
    calls = _patch(monkeypatch, [code, None])
    with pytest.raises(SystemExit) as exc:
        Z.api("https://zenodo.org/api", "tok", "GET", "/x", _sleep=lambda s: None)
    assert calls == ["GET"], f"{code} was retried; only transient statuses may be"
    assert "not transient" in str(exc.value)


def test_the_backoff_table_covers_every_retry_the_bound_allows():
    """A one-of-a-pair guard: raising _RETRY_ATTEMPTS without extending _RETRY_BACKOFF would
    IndexError on the last retry — at the moment of a real outage, which is the worst time."""
    assert len(Z._RETRY_BACKOFF) >= Z._RETRY_ATTEMPTS - 1
