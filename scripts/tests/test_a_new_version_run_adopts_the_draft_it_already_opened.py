"""⛔⛔ A CORRECTION MUST BE RESUMABLE: A SECOND RUN ADOPTS THE DRAFT THE FIRST ONE OPENED.

⚠ WHY THIS EXISTS, AND IT IS MEASURED IN TWO REAL LOGS RATHER THAN REASONED FROM THE API DOCS.
`POST /deposit/depositions/{id}/actions/newversion` is not idempotent, and Zenodo will not open a
second version while one is open:

  · run 33498033370 — the POST on published record 22182180 SUCCEEDED, and the `GET
    .../deposit/depositions/22229096` that immediately followed returned 504. The draft existed from
    that moment on; the script did not survive to use it, so its inherited files were never cleared
    and its reserved DOI was never read.
  · run 33498227279 — the retry POSTed newversion again and Zenodo answered
    `400 files.enabled: "Please remove all files first."` — how it declines to open a second
    version. Nothing in that wording says "a draft is already open", so it reads as a defect in the
    archive rather than a run that needs resuming.

★ THE FIX IS TO READ, NOT TO RETRY: the published record's own `links.latest_draft` names the open
draft. A mutation must never be repeated (see
`test_zenodo_api_retries_reads_and_never_mutations.py`), so the recovery for a half-finished
correction cannot be another POST — it has to be a GET of state Zenodo already holds.

⛔ AND THE REFUSALS ARE HALF THE FILE. Adopting whatever a link points at is how a corrected archive
would get uploaded over a version a reader may already cite, so a draft that comes back `submitted`,
or that is the published record itself, stops the run instead.
"""
import json
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(REPO, "scripts"))

import zenodo_deposit as Z  # noqa: E402

PUBLISHED = 22182180
DRAFT = 22229096

MANIFEST = {
    "git_revision": "0" * 40,
    "deposition_doi": f"10.5281/zenodo.{PUBLISHED}",
    "files": [],
    "gaps": {},
}


def _draft(dep_id=DRAFT, submitted=False):
    return {
        "id": dep_id,
        "submitted": submitted,
        "files": [{"id": "inherited-1"}, {"id": "inherited-2"}],
        "links": {"bucket": "https://zenodo.org/api/files/bucket", "html": "https://zenodo.org/x"},
        "metadata": {"prereserve_doi": {"doi": f"10.5281/zenodo.{dep_id}"}},
    }


def _run(monkeypatch, tmp_path, published_links, draft=None, argv=None):
    """Drive main() with every real side effect replaced. Returns (calls, exit_or_exc)."""
    calls = []
    draft = draft if draft is not None else _draft()

    seen_published = []

    def fake_api(base, token, method, path, payload=None, raw=None, **kw):
        calls.append((method, path))
        # ⚠ ORDER, NOT PATH-MATCHING. The first GET is the run resolving the published record from
        # the manifest's DOI; every GET after it is the run reading the draft. Keying on the id in
        # the path instead made the self-link case indistinguishable — the adopted deposition's
        # path CONTAINS the published id there, so the fake handed back a `submitted` record and
        # the earlier refusal fired, hiding whether the self-link guard exists at all. Found by
        # mutation: deleting that guard left this file green.
        if method == "GET" and str(PUBLISHED) in path and not seen_published:
            seen_published.append(path)
            return {"id": PUBLISHED, "submitted": True, "links": published_links, "files": []}
        if method == "POST" and path.endswith("actions/newversion"):
            return {"links": {"latest_draft": f"/deposit/depositions/{DRAFT}"}}
        if method == "GET":
            return draft
        if method == "PUT":
            return draft
        return draft

    monkeypatch.setattr(Z, "api", fake_api)
    monkeypatch.setattr(Z, "load_manifest", lambda rel: dict(MANIFEST))
    monkeypatch.setattr(Z, "verify", lambda manifest: None)
    monkeypatch.setattr(Z, "sha256", lambda p: "d" * 64)
    # The record's prose is built from the real manifest's contents and has its own guards
    # (test_the_deposit_does_not_restate_a_count_the_paper_owns, and the delimiter suite). This
    # file is about WHICH deposition the run writes to, so the description is stubbed rather than
    # half-faked — a stub says "not measured here"; a fake manifest would say "measured", wrongly.
    monkeypatch.setattr(Z, "description", lambda *a, **k: "<p>stub</p>")
    zip_path = tmp_path / "emc-aso-archive.zip"

    def fake_build_zip(manifest, rel, out):
        with open(out, "wb") as fh:
            fh.write(b"PK\x03\x04")

    monkeypatch.setattr(Z, "build_zip", fake_build_zip)
    monkeypatch.setenv("ZENODO_TOKEN", "t")
    argv = argv or ["--paper", "aso", "--new-version", "--out-dir", str(tmp_path)]
    try:
        return calls, Z.main(argv)
    except SystemExit as exc:
        return calls, exc


def test_an_open_draft_is_adopted_and_newversion_is_never_posted(monkeypatch, tmp_path):
    """The whole point: the run that resumes must not ask Zenodo for a second version."""
    calls, out = _run(monkeypatch, tmp_path,
                      {"latest_draft": f"/deposit/depositions/{DRAFT}"})
    assert out == 0, out
    posts = [p for m, p in calls if m == "POST"]
    assert not any(p.endswith("actions/newversion") for p in posts), \
        f"a draft was already open and the run asked for another version anyway: {posts}"


def test_the_adopted_draft_gets_its_inherited_files_cleared(monkeypatch, tmp_path):
    """⛔ The step the 504 skipped. A new version inherits the old one's files, so a run that
    adopts a draft and does not clear them ships a UNION of two archives."""
    calls, out = _run(monkeypatch, tmp_path,
                      {"latest_draft": f"/deposit/depositions/{DRAFT}"})
    assert out == 0
    deletes = [p for m, p in calls if m == "DELETE"]
    assert len(deletes) == 2, f"inherited files were not cleared: {deletes}"
    assert all(f"depositions/{DRAFT}/files/" in p for p in deletes)


def test_with_no_open_draft_it_still_opens_one(monkeypatch, tmp_path):
    """⚠ The adopt path must not disable the ordinary correction. A published record with no
    `latest_draft` is the first correction of that record, and it still needs the POST."""
    calls, out = _run(monkeypatch, tmp_path, {})
    assert out == 0
    assert any(m == "POST" and p.endswith("actions/newversion") for m, p in calls), \
        "no draft was open, so the run had to open one and did not"


def test_a_published_target_is_refused(monkeypatch, tmp_path):
    """⛔ The dangerous adoption. If the link resolves to something Zenodo calls submitted, this
    run would replace the files of a version a reader may already cite."""
    calls, out = _run(monkeypatch, tmp_path,
                      {"latest_draft": f"/deposit/depositions/{DRAFT}"},
                      draft=_draft(submitted=True))
    assert isinstance(out, SystemExit), "a submitted target was accepted as a draft"
    assert "PUBLISHED" in str(out)
    assert not any(m in ("PUT", "DELETE") for m, _ in calls), \
        "it refused only AFTER writing, which is not a refusal"


def test_a_self_referential_link_is_refused(monkeypatch, tmp_path):
    """A link that points back at the published record leaves nothing to write to."""
    calls, out = _run(monkeypatch, tmp_path,
                      {"latest_draft": f"/deposit/depositions/{PUBLISHED}"},
                      draft=_draft(dep_id=PUBLISHED))
    assert isinstance(out, SystemExit), "the record adopted itself as its own new version"
    assert not any(m in ("PUT", "DELETE") for m, _ in calls)


def test_the_reserved_doi_is_read_from_the_response(monkeypatch, tmp_path, capsys):
    """⛔ CLAUDE.md §7 — never write an identifier from recollection. The DOI the manuscript will
    cite comes out of Zenodo's own answer, not from the deposition number, even though all three
    prior versions happened to match that way."""
    draft = _draft()
    draft["metadata"]["prereserve_doi"]["doi"] = "10.5281/zenodo.99999999"
    calls, out = _run(monkeypatch, tmp_path,
                      {"latest_draft": f"/deposit/depositions/{DRAFT}"}, draft=draft)
    assert out == 0
    assert "10.5281/zenodo.99999999" in capsys.readouterr().out
