"""⛔ A DEPOSIT THAT OMITS THE PAPER IT IS CITED BY IS AN EMPTY PROMISE.

The condensed journal submission's Data and code availability points a NAT editor at a Zenodo
archive. Until 2026-08-22 that archive did not contain the journal article. It contained the
article's TABLES, its REFERENCES and its GENERATOR — and not the article, not either of its two
built PDFs, not either build stamp.

⛔ THE CAUSE IS THE SHAPE, NOT THE OVERSIGHT. `deposited_documents`' glob read
`fusion-junction-aso-research-article*`, written on 2026-08-19, one day before the condensed paper
was registered as a second paper in `build_submission_pdf.PAPERS`. Nobody omitted it: a list that
was complete for one paper became silently incomplete for two, which is the same failure this
repository has now found in a staleness map, an abstract guard, a title guard, a text-layer guard
and a packet's companion resolver.

★ SO THE QUESTION IS ASKED OF THE BUILDER, NOT OF A LIST. `build_submission_pdf.PAPERS` is what
decides which papers exist and what each one renders. Every manuscript it knows about, and every
PDF and build stamp it writes, has to be inside the archive the papers cite — and a paper added
tomorrow is covered the day it is registered, with nothing for anyone to remember.
"""
from __future__ import annotations

import importlib.util
import json
import os

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MANUSCRIPTS = os.path.abspath(os.path.join(HERE, ".."))
REPO = os.path.abspath(os.path.join(MANUSCRIPTS, "..", ".."))
MANIFEST = os.path.join(MANUSCRIPTS, "aso", "fusion-junction-aso-archive-manifest.json")


def _builder():
    path = os.path.join(MANUSCRIPTS, "build_submission_pdf.py")
    if not os.path.exists(path):
        pytest.fail("build_submission_pdf.py is missing; nothing defines which papers exist")
    spec = importlib.util.spec_from_file_location("_build_submission_pdf_for_test", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _archived():
    if not os.path.exists(MANIFEST):
        pytest.fail("the archive manifest is missing; the deposit's contents are unknown")
    files = json.load(open(MANIFEST, encoding="utf-8"))["files"]
    return set(files) if isinstance(files, dict) else {f["path"] for f in files}


def _deposition_doi():
    return json.load(open(MANIFEST, encoding="utf-8")).get("deposition_doi") or ""


def _cites_this_archive(paper):
    """Does this paper send its readers to THIS deposit?

    ⚠ SCOPE IS DERIVED FROM THE PAPERS, NOT ASSUMED. This manifest is the ASO deposit; the vaccine
    paper is built by the same builder and belongs to no archive of its own yet, so demanding it
    here would be a guard inventing a promise nobody made. The right question is which papers'
    availability statements point AT this DOI — those are the ones that must be inside it.
    """
    doi = _deposition_doi()
    if not doi:
        return False
    rel = paper.get("manuscript")
    if not rel:
        return False
    path = os.path.join(MANUSCRIPTS, rel)
    if not os.path.exists(path):
        return False
    key = doi.split("zenodo.")[-1] if "zenodo." in doi else doi
    return key in open(path, encoding="utf-8").read()


def test_every_paper_that_cites_this_archive_is_inside_it():
    """⛔ THE MANUSCRIPT, ITS BUILT PDFs AND THEIR STAMPS — for every paper that cites the deposit."""
    mod = _builder()
    archived = _archived()
    missing = []
    citing = [(n, p) for n, p in sorted(getattr(mod, "PAPERS", {}).items())
              if _cites_this_archive(p)]
    assert citing, (
        "no registered paper cites this archive's DOI, so this guard is checking nothing — either "
        "the manifest's `deposition_doi` moved or the availability statements did")
    for name, paper in citing:
        wanted = set()
        for key in ("manuscript", "supplementary", "tables", "references"):
            rel = paper.get(key)
            if rel:
                wanted.add(f"research/manuscripts/{rel}")
        out = paper.get("out")
        if out:
            stem = f"research/manuscripts/{out}".rsplit(".pdf", 1)[0]
            for suffix in (".pdf", ".build-stamp.json",
                           "-manuscript.pdf", "-manuscript.build-stamp.json"):
                candidate = stem + suffix
                # only require what actually exists on disk — an unbuilt format is a different
                # finding, and the staleness guards own it
                if os.path.exists(os.path.join(REPO, candidate)):
                    wanted.add(candidate)
        for rel in sorted(wanted - archived):
            missing.append(f"{name}: {rel}")
    assert not missing, (
        "the deposit does not contain a document of a paper the builder builds, and the papers' own "
        "Data and code availability statements point readers at that deposit:\n  "
        + "\n  ".join(missing)
        + "\n\nWiden the globs in aso_archive_manifest.py's promise table — do not add one literal "
          "path, because a literal list is what produced this hole twice.")
