"""`_download` must have a REAL wall clock, not just a socket timeout.

Run 30853818120: the DepMap step ran 15 min against a normal 17-26 s and only ended because a
re-dispatch cancelled it. Cause: `timeout=` on `urlopen` is a PER-SOCKET-OPERATION timeout, so a
peer that dribbles one byte inside every window never trips it, and the 4-attempt retry loop
multiplied the stall instead of ending it.

The reproduction below is the diagnostic that proved it (CLAUDE.md §4 — a real controlled
reproduction, not a "probably"). Note it also pins the SECOND bug found while fixing the first:
`HTTPResponse.read(n)` blocks until it has all n bytes, so a deadline checked around `r.read(1<<20)`
is never reached while the peer dribbles — the first version of the fix still hung. `read1()` is
what makes the wall clock run.
"""

import http.server
import socketserver
import threading
import time

import pytest

import depmap_sarcoma_dependency as dep


class _Dribble(http.server.BaseHTTPRequestHandler):
    """Announces a huge body, then sends one byte every 100 ms forever. Never idle, never done."""

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Length", "100000000")
        self.end_headers()
        try:
            while True:
                self.wfile.write(b"x")
                self.wfile.flush()
                time.sleep(0.1)
        except Exception:  # noqa: BLE001  (client hung up — that is the pass condition)
            pass

    def log_message(self, *a):
        pass


class _Fast(http.server.BaseHTTPRequestHandler):
    BODY = b"col_a,col_b\n" + b"1,2\n" * 20000

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Length", str(len(self.BODY)))
        self.end_headers()
        self.wfile.write(self.BODY)

    def log_message(self, *a):
        pass


@pytest.fixture
def serve():
    servers = []

    def _start(handler):
        srv = socketserver.TCPServer(("127.0.0.1", 0), handler)
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        servers.append(srv)
        return f"http://127.0.0.1:{srv.server_address[1]}/file.csv"

    yield _start
    for s in servers:
        s.shutdown()


def test_a_dribbling_peer_is_abandoned_at_the_total_deadline(serve):
    url = serve(_Dribble)
    t0 = time.monotonic()
    with pytest.raises(RuntimeError):
        dep._download(url, timeout=1, total_deadline=3)
    elapsed = time.monotonic() - t0
    # without the wall clock this never returns; with it, the whole retry loop is bounded.
    assert elapsed < 10, f"retry loop was not bounded: {elapsed:.1f}s"


def test_total_deadline_defaults_to_twice_the_per_attempt_timeout(serve):
    url = serve(_Dribble)
    t0 = time.monotonic()
    with pytest.raises(RuntimeError):
        dep._download(url, timeout=1)
    assert time.monotonic() - t0 < 10


def test_a_normal_transfer_is_untouched_and_byte_exact(serve):
    path = dep._download(serve(_Fast), timeout=30)
    with open(path, "rb") as fh:
        assert fh.read() == _Fast.BODY
