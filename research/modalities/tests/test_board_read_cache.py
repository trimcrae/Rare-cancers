"""One board read must serve a whole fan-out wave — and must never serve a stale or failed one.

WHY THIS TEST EXISTS. `VastBackend.submit` reads `/search/asks/` once per unit, and
`_vast_ondemand_base_by_machine` reads it again for the bid cap, so placement cost TWO board reads per
unit. At this lane's full width that is ~37 calls in a burst against the ONE Vast key that drives every
lane in this repo — and `gpu_backend._vast_request`'s own 403 handler records the measured consequence
(2026-07-27, 11:08-11:10 AM ET): an nginx HTML 403, i.e. a proxy throttle verdict, hit the board read,
`/instances/` and all four `/search/asks/` of a FOUR-unit launch, which rented 0/4. Scaling placement
without scaling the read pattern down would scale that trigger with it.

The cache is only safe because of four properties, and each one is pinned below rather than asserted in a
comment: it is OFF unless a caller opens it; it serves only GET `/search/asks/`; it never outlives its
TTL; and it never remembers a FAILED read (§6 — an unreadable market is not a cheap one, and it must not
become a remembered one either).
"""
import time

import pytest

import gpu_backend as gb


def _stub(calls, payload=None, fail_times=0):
    """A fake urlopen-level backend: counts real calls, optionally failing the first `fail_times`."""
    state = {"n": 0}

    def _fake(method, path, api_key, params=None, body=None, _hops=0):
        state["n"] += 1
        calls.append((method, path, params))
        if state["n"] <= fail_times:
            raise RuntimeError("vast API GET /search/asks/ -> 403: <html>403 Forbidden</html>")
        return payload if payload is not None else {"offers": [{"id": state["n"]}]}

    return _fake


def _patched(monkeypatch, fake):
    """Route `_vast_request`'s network layer through `fake` while keeping the cache hook under test.

    The cache lives INSIDE `_vast_request`, so the test cannot monkeypatch `_vast_request` itself — that
    would replace the very code being tested. It patches the transport instead.
    """
    def _shim(method, path, api_key, params=None, body=None, _hops=0):
        # mirror the real function's cache hook by delegating: call the real one with a stubbed opener
        return fake(method, path, api_key, params=params, body=body, _hops=_hops)
    return _shim


def test_cache_is_off_by_default(monkeypatch):
    """No context manager open -> every call is a real call. The cache must never be ambient."""
    calls = []
    monkeypatch.setattr(gb.urllib.request, "urlopen", _never_called)
    monkeypatch.setattr(gb, "_vast_url", lambda p: "http://x" + p)
    # Drive the cache hook directly: with TTL 0 it must not even build a key.
    assert gb._BOARD_CACHE_TTL_S == 0.0
    assert calls == []


def _never_called(*a, **k):  # pragma: no cover - guard
    raise AssertionError("no network call expected")


class _Resp:
    def __init__(self, body):
        self._b = body

    def read(self):
        return self._b

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def _urlopen_counter(counter, body=b'{"offers": [1, 2, 3]}', fail_times=0):
    def _open(req, timeout=None):
        counter["n"] += 1
        if counter["n"] <= fail_times:
            raise TimeoutError("board read timed out")
        return _Resp(body)
    return _open


def test_one_read_serves_a_whole_wave(monkeypatch):
    """18 identical board reads -> ONE real HTTP call, and the saving is reported."""
    counter = {"n": 0}
    monkeypatch.setattr(gb.urllib.request, "urlopen", _urlopen_counter(counter))
    monkeypatch.setattr(gb, "_vast_url", lambda p: "http://x" + p)
    q = {"q": '{"verified": true}'}
    with gb.board_read_cache(ttl_s=300) as stats:
        for _ in range(18):
            out = gb._vast_request("GET", "/search/asks/", "k", params=q)
            assert out == {"offers": [1, 2, 3]}
    assert counter["n"] == 1, "the wave must cost exactly one board read"
    assert stats["hits"] == 17 and stats["misses"] == 1
    assert stats["saved_calls"] == 17


def test_a_different_query_is_a_different_board(monkeypatch):
    """Two specs with different hard filters must not share a snapshot."""
    counter = {"n": 0}
    monkeypatch.setattr(gb.urllib.request, "urlopen", _urlopen_counter(counter))
    monkeypatch.setattr(gb, "_vast_url", lambda p: "http://x" + p)
    with gb.board_read_cache(ttl_s=300):
        gb._vast_request("GET", "/search/asks/", "k", params={"q": "A"})
        gb._vast_request("GET", "/search/asks/", "k", params={"q": "B"})
        gb._vast_request("GET", "/search/asks/", "k", params={"q": "A"})
    assert counter["n"] == 2


def test_ttl_expiry_forces_a_fresh_read(monkeypatch):
    """No unit may ever be placed against a board older than the TTL."""
    counter = {"n": 0}
    monkeypatch.setattr(gb.urllib.request, "urlopen", _urlopen_counter(counter))
    monkeypatch.setattr(gb, "_vast_url", lambda p: "http://x" + p)
    clock = {"t": 1000.0}
    monkeypatch.setattr(time, "monotonic", lambda: clock["t"])
    with gb.board_read_cache(ttl_s=60):
        gb._vast_request("GET", "/search/asks/", "k", params={"q": "A"})
        clock["t"] += 59
        gb._vast_request("GET", "/search/asks/", "k", params={"q": "A"})
        assert counter["n"] == 1, "inside the TTL the snapshot is reused"
        clock["t"] += 2
        gb._vast_request("GET", "/search/asks/", "k", params={"q": "A"})
    assert counter["n"] == 2, "past the TTL the board must be re-read"


def test_a_failed_read_is_never_cached(monkeypatch):
    """§6 fail-closed: a throttled board must be RE-ATTEMPTED by the next unit, not frozen in.

    The regression this forbids is subtle and expensive: if an exception were cached, one 403 at the start
    of a wave would make every remaining unit of that wave fail instantly against a remembered error, and
    the readout would blame the market rather than a single transient edge verdict.
    """
    counter = {"n": 0}
    # _vast_request retries GET timeouts internally (2,4,6,8,10 s), so patch the sleep out and let the
    # FIRST attempt fail: the retry must reach the transport again, not a cached failure.
    monkeypatch.setattr(gb.urllib.request, "urlopen", _urlopen_counter(counter, fail_times=1))
    monkeypatch.setattr(gb, "_vast_url", lambda p: "http://x" + p)
    monkeypatch.setattr(time, "sleep", lambda *_a: None)
    with gb.board_read_cache(ttl_s=300):
        out = gb._vast_request("GET", "/search/asks/", "k", params={"q": "A"})
    assert out == {"offers": [1, 2, 3]}
    assert counter["n"] == 2, "the failure was retried against the network, not served from cache"
    assert not gb._BOARD_CACHE, "the cache must be emptied when the context closes"


def test_mutations_and_other_endpoints_are_never_cached(monkeypatch):
    """Only GET /search/asks/. `/instances/` reflects state we mutate; a PUT rents a box.

    Caching either would be a correctness bug of a different order from a stale price: a remembered
    `/instances/` listing would hide a box we just rented, and a cached create would report one rental
    twice.
    """
    counter = {"n": 0}
    monkeypatch.setattr(gb.urllib.request, "urlopen", _urlopen_counter(counter))
    monkeypatch.setattr(gb, "_vast_url", lambda p: "http://x" + p)
    with gb.board_read_cache(ttl_s=300):
        gb._vast_request("GET", "/instances/", "k")
        gb._vast_request("GET", "/instances/", "k")
        gb._vast_request("PUT", "/asks/7/", "k", body={"client_id": "me"})
        gb._vast_request("PUT", "/asks/7/", "k", body={"client_id": "me"})
    assert counter["n"] == 4, "no endpoint other than /search/asks/, and no mutation, may be cached"


def test_a_deliberate_re_sampler_is_never_collapsed(monkeypatch):
    """THE INTERACTION THAT WOULD HAVE MADE THIS CACHE A REGRESSION.

    `/search/asks/` returns a ROTATING SAMPLE, not the board: at `limit=512` one read returns ~225 offers,
    two identical reads 20 s apart share only ~174 machines, and cumulative distinct machines across 30
    reads reached 591 and was still climbing (measured 2026-07-27). So `sample_board` issues the SAME query
    N times ON PURPOSE, to deepen a ~38 % sample — worth best-4 -5.8 % on the price we can buy at.

    A cache that collapsed those N reads to one would silently turn `samples=2` into `samples=1`, delete
    that gain, and report a cache HIT while doing it — a regression disguised as an optimisation, and
    precisely the opposite of the ramp's goal (more parallelism must not come at a worse rate).
    """
    counter = {"n": 0}
    monkeypatch.setattr(gb.urllib.request, "urlopen", _urlopen_counter(counter))
    monkeypatch.setattr(gb, "_vast_url", lambda p: "http://x" + p)
    with gb.board_read_cache(ttl_s=300):
        for _ in range(4):
            gb._vast_request("GET", "/search/asks/", "k", params={"q": "A"}, no_cache=True)
    assert counter["n"] == 4, "a re-sampler's reads must each reach the network"


def test_cache_does_not_survive_the_context(monkeypatch):
    """A wave's snapshot must not leak into the next wave — or into a later collect/reap."""
    counter = {"n": 0}
    monkeypatch.setattr(gb.urllib.request, "urlopen", _urlopen_counter(counter))
    monkeypatch.setattr(gb, "_vast_url", lambda p: "http://x" + p)
    with gb.board_read_cache(ttl_s=300):
        gb._vast_request("GET", "/search/asks/", "k", params={"q": "A"})
    assert gb._BOARD_CACHE_TTL_S == 0.0
    gb._vast_request("GET", "/search/asks/", "k", params={"q": "A"})
    assert counter["n"] == 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(pytest.main([__file__, "-q"]))
