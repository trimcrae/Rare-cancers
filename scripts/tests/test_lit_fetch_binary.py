#!/usr/bin/env python3
"""A binary payload must never reach the UTF-8 text writer. ($0, pure stdlib)

⛔ THE DEFECT THIS PINS, measured 2026-08-23 on a real fetch. `lit_fetch_urls.py` already had a
binary path, added after a JPEG was destroyed by `data.decode("utf-8", errors="replace")` — but it
listed images, tar and zip and NOT Office documents. So three Supplemental Digital Content tables
from a CORR paper, served by links.lww.com as
`application/vnd.openxmlformats-officedocument.wordprocessingml.document`, went down the TEXT path.

⚠ WHY IT IS A TEST AND NOT A COMMENT. The failure is SILENT and it forges a success. The run
reported green, the manifest recorded `chars: 21826` / `chars: 24799` / `chars: 22163` and no
`binary_path`, and a session reading the manifest sees three retrieved documents. What is on disk
is mojibake that `zipfile` refuses with "Bad magic number for central directory". A destroyed file
that reports a five-figure character count is worse than a missing one, because nothing in the
record contradicts it — the same shape as the image incident and as the ClinicalTrials.gov module
loss that `test_lit_fetch_structured.py` pins.

The fix is a WIDER SNIFF rather than a longer content-type list, and that is the property asserted
here: a caller must be protected by the BYTES even when the server declares something else, because
the content type is exactly what cannot be trusted.
"""
import io
import os
import sys
import zipfile

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import lit_fetch_urls as L  # noqa: E402

DOCX_CT = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
XLSX_CT = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
OLE2 = b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1" + b"\x00" * 200


def _ooxml_bytes(body=b"<w:document>Myxoid 87</w:document>"):
    """A real, openable OOXML container — the thing the fetcher must preserve byte-for-byte."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr("word/document.xml", body)
    return buf.getvalue()


class _Resp:
    """The parts of an http.client.HTTPResponse that `fetch()` actually touches."""

    def __init__(self, data, ctype, url):
        self._data, self._url = data, url
        self.status = 200
        self.headers = {"Content-Type": ctype}

    def read(self):
        return self._data

    def geturl(self):
        return self._url

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


@pytest.fixture
def served(monkeypatch, tmp_path):
    """Drive `fetch()` off chosen bytes + content type, writing into a temp OUT."""
    monkeypatch.setattr(L, "OUT", str(tmp_path))
    os.makedirs(str(tmp_path), exist_ok=True)

    def _serve(data, ctype, url="https://example.org/x"):
        monkeypatch.setattr(
            L.urllib.request, "urlopen",
            lambda req, timeout=None: _Resp(data, ctype, url))
        return L.fetch("target", url)

    return _serve


@pytest.mark.parametrize("ctype,ext", [(DOCX_CT, "docx"), (XLSX_CT, "xlsx"),
                                       ("application/msword", "doc"),
                                       ("application/vnd.ms-excel", "xls")])
def test_an_office_document_is_written_as_bytes_not_decoded_text(served, tmp_path, ctype, ext):
    payload = _ooxml_bytes()
    rec = served(payload, ctype)
    assert rec.get("binary_path"), f"{ctype} took the text path — the 2026-08-23 defect"
    assert rec.get("chars") == 0, "a binary payload must not report a character count"
    assert rec.get("bytes") == len(payload)
    on_disk = (tmp_path / rec["binary_path"]).read_bytes()
    assert on_disk == payload, "the bytes were altered on the way to disk"
    # ⚠ THE EXTENSION IS PINNED SEPARATELY FROM THE BYTES, AND ON PURPOSE. Mutation-tested
    # 2026-08-23: deleting the docx content-type mapping leaves every byte assertion GREEN,
    # because the ZIP magic sniff still catches the file — it just lands as `target.zip`. The
    # bytes are safe and the NAME is what a future session reads, so the name gets its own
    # assertion rather than riding on the guard that happens to overlap it.
    assert rec["binary_path"].endswith("." + ext), (
        f"{ctype} was saved as {rec['binary_path']!r}, not .{ext}")


def test_the_saved_container_still_opens(served, tmp_path):
    """⛔ THE REAL TEST OF 'NOT CORRUPTED' IS THAT A READER CAN OPEN IT. Byte equality is checked
    above; this asserts the consequence that actually mattered — the three SDC tables could not be
    opened at all."""
    payload = _ooxml_bytes(b"<w:document>Extraskeletal myxoid chondrosarcoma 404</w:document>")
    rec = served(payload, DOCX_CT)
    with zipfile.ZipFile(tmp_path / rec["binary_path"]) as z:
        assert b"404" in z.read("word/document.xml")


def test_the_bytes_win_when_the_server_declares_something_else(served, tmp_path):
    """⚠ THE CONTENT TYPE IS THE UNTRUSTWORTHY HALF. The module's own comment records
    pmc.ncbi.nlm.nih.gov answering a .jpg request with text/html (a captcha), which is why the
    declared type is consulted first. The converse must also hold: a ZIP container declared as
    plain text is still a ZIP, and decoding it destroys it."""
    payload = _ooxml_bytes()
    rec = served(payload, "text/plain")
    assert rec.get("binary_path"), "the PK\\x03\\x04 magic did not trigger the binary path"
    assert (tmp_path / rec["binary_path"]).read_bytes() == payload


def test_a_legacy_ole2_document_is_also_bytes(served, tmp_path):
    rec = served(OLE2, "application/octet-stream")
    assert rec.get("binary_path")
    assert (tmp_path / rec["binary_path"]).read_bytes() == OLE2


def test_real_text_is_still_written_as_text(served, tmp_path):
    """The sniff must not swallow the ordinary case. A regression here would send every fetched
    page down the binary path and quietly end the corpus."""
    rec = served(b"<html><body>Myxoid chondrosarcoma</body></html>", "text/html")
    assert "binary_path" not in rec
    assert rec.get("chars", 0) > 0


def test_json_is_still_written_as_text(served, tmp_path):
    rec = served(b'{"hitCount": 31}', "application/json")
    assert "binary_path" not in rec
    assert rec.get("chars", 0) > 0
