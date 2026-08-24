#!/usr/bin/env python3
"""Deposit the CONDENSED article as a preprint record of its own, and RESERVE its DOI.

⛔⛔ WHY THIS IS A SEPARATE RECORD AND NOT A NEW VERSION OF THE ARCHIVE (trimcrae asked directly,
2026-08-23: "this is essentially version 2 of the longer preprint we already submitted, do we want
it to share a DOI to link them together?"). The answer is no, and the reason is what a Zenodo
version actually MEANS.

  · `10.5281/zenodo.22028916` IS NOT THE LONGER PREPRINT. It is the ARCHIVE — `upload_type:
    dataset`, titled "Code and artefacts for: …" — which happens to CONTAIN both manuscripts as
    files. Making a paper a new version of it would replace an artefact archive with a paper.
  · A VERSION MEANS SUPERSESSION, AND THE CONCEPT DOI FOLLOWS THE NEWEST ONE. `zenodo_deposit.py`'s
    own header says it: "A concept DOI MOVES … The paper must cite a FROZEN version." So a reader
    following the record without a version suffix would land on a 6-page paper where the archive
    should be, and the archive's own page would read "newer version available" pointing at a
    manuscript that does not supersede it.
  · AND THE CONDENSED ARTICLE DOES NOT SUPERSEDE THE EXTENDED REPORT. Both papers say the opposite:
    the condensed one cites the extended report for every screen's parameters and the complete
    bounds on each claim. "Version 2" asserts the longer one is obsolete, which is the one thing
    this pair must not say.
  · A JOURNAL ASKS FOR A PREPRINT DOI. Nucleic Acid Therapeutics: "Please enter the preprint DOI in
    the designated field." Handing them a version of a dataset record invites exactly the confusion
    the field exists to avoid.

★ THE LINK IS `related_identifiers`, WHICH IS THE MECHANISM FOR "these two things are related"
— as opposed to a shared DOI, which is the mechanism for "these two things are the same thing at
different times". This record therefore points at the archive DOI and at the git tree.
⚠ RELATION VOCABULARY, STATED HONESTLY: `isDerivedFrom` is used because this repository has
WATCHED THE LIVE API ACCEPT IT (zenodo_deposit.py uses it and its deposits succeed). A more precise
DataCite term may exist — `isSupplementedBy` is the obvious candidate — but developers.zenodo.org is
blocked at this sandbox's egress proxy and zenodo.org does not answer here either, so switching to
one would be writing a vocabulary term from recollection, which CLAUDE.md §7 forbids. Confirm the
term on a runner before changing it.

★ EVERY FIELD IS READ OUT OF THE MANUSCRIPT, NOT TYPED HERE. Title, abstract, keywords and the
author block come from the built document, for the same reason `aso_sequence_manifest.py` reads
them: a carrier that states them from memory is a second home that drifts. A missing field is a
hard failure, never a default.

⛔ THIS SCRIPT NEVER PUBLISHES. Same rule as the archive deposit: publishing is irreversible, and
the click stays human.

    python3 scripts/zenodo_preprint.py --build-only          # verify + assemble, no network
    ZENODO_TOKEN=... python3 scripts/zenodo_preprint.py --sandbox
    ZENODO_TOKEN=... python3 scripts/zenodo_preprint.py
"""
from __future__ import annotations

import argparse
import io
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from zenodo_deposit import CREATOR, REPO_URL, api, sha256  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANUSCRIPTS = os.path.join(REPO, "research", "manuscripts")

PAPER = {
    "manuscript": "aso/fusion-junction-aso-journal-article.md",
    #: The typeset build is what a reader wants from a preprint DOI. The submission-format PDF and
    #: the Word file are what a JOURNAL wants, and they travel in the archive rather than here: a
    #: preprint record carrying three renderings of one paper invites someone to cite the wrong one.
    "pdf": "aso/fusion-junction-aso-journal-article.pdf",
    "state": "aso/deposit-state.json",
    #: ⛔ NOT a licence chosen here. CC-BY-4.0 matches the archive record this paper is derived from;
    #: if the author wants a different one it is changed on Zenodo before publishing, which is the
    #: last moment it is still free to change.
    "license": "cc-by-4.0",
}


def _read(rel, what):
    path = os.path.join(MANUSCRIPTS, rel)
    if not os.path.exists(path):
        raise SystemExit(f"{rel} is missing, and {what} cannot be read from anywhere else.")
    return io.open(path, encoding="utf-8").read()


def _one(pattern, text, what, flags=re.M):
    m = re.search(pattern, text, flags)
    if not m:
        raise SystemExit(
            f"{what} could not be read out of {PAPER['manuscript']} — this script does not state it "
            "from memory, so it stops here. Either the manuscript was reworded and this pattern "
            "must follow it, or the field was dropped.")
    return " ".join(m.group(1).split())


def metadata():
    """Everything Zenodo needs, read out of the manuscript and the deposit state."""
    text = _read(PAPER["manuscript"], "the paper's own metadata")
    flat = " ".join(text.split())

    title = _one(r"^#\s+(.+)$", text, "the title")
    title = re.sub(r"[*_`]", "", title)

    #: The abstract runs from its heading to the next one. `submission_metrics.py` measures the same
    #: span, so the length Zenodo shows is the length that was graded against the venue's cap.
    abstract = _one(r"^##\s*Abstract\s*$\n(.+?)(?=^##\s)", text, "the abstract", re.M | re.S)

    #: ⛔ READ FROM THE SOURCE, NOT THE FLATTENED TEXT, AND THE FIRST VERSION DID THE OPPOSITE.
    #: `(.+?)(?=\s*$|\n\n)` against text whose newlines have been collapsed has no `\n\n` to stop
    #: at and `\s*$` matches at the end of the string, so the lazy quantifier swallowed the entire
    #: paper: 35 "keywords", the first seven real and the rest the whole of §1 onward. It was caught
    #: by `--build-only` PRINTING the values rather than by any assertion, which is the argument for
    #: a dry run that shows its work. The keyword block is a PARAGRAPH — every line up to a blank
    #: one — which is what `build_submission_pdf.label_paragraph` already matches for the same field.
    block = _one(r"\*\*Keywords\.\*\*([^\n]*(?:\n(?!\s*\n)[^\n]*)*)", text, "the keywords")
    keywords = [k.strip() for k in block.split(";") if k.strip()]
    if len(keywords) < 4:
        raise SystemExit(
            f"only {len(keywords)} keyword(s) were read. Nucleic Acid Therapeutics requires a "
            "minimum of 4, and a preprint record with fewer is a worse landing page than the "
            "paper deserves.")
    #: ⚠ AND A CEILING, BECAUSE THE FAILURE THAT ACTUALLY HAPPENED WAS OVER-MATCHING. A floor alone
    #: passes a runaway match with flying colours — 35 is comfortably more than 4. Neither bound is
    #: a style rule; both exist to make a broken read impossible to mistake for a wide one.
    runaway = [k for k in keywords if len(k) > 80]
    if len(keywords) > 15 or runaway:
        raise SystemExit(
            f"read {len(keywords)} keyword(s)"
            + (f", {len(runaway)} of them over 80 characters" if runaway else "")
            + ". That is a pattern that has escaped its paragraph, not a long keyword list. "
              "Fix the pattern; do not widen the bound.")

    state = json.loads(_read(PAPER["state"], "which archive DOI this paper cites"))
    archive_doi = (state.get("pending") or state.get("published", {})).get("doi")
    if not archive_doi:
        raise SystemExit("deposit-state.json names no archive DOI, so this record cannot point at "
                         "the artefacts the paper's Data availability statement promises.")

    #: ⛔ THE PAPER MUST ALREADY CITE THIS DOI. If it does not, the preprint would go up promising
    #: an archive it never names, which is the defect the reserve-then-rebuild ordering exists to
    #: prevent — one document over.
    if archive_doi not in flat:
        raise SystemExit(
            f"the manuscript does not cite {archive_doi}, which deposit-state.json says is the "
            "archive it belongs to. Rebuild the paper against the current DOI before depositing.")

    return {
        "upload_type": "publication",
        "publication_type": "preprint",
        "title": title,
        "creators": [CREATOR],
        "description": _description(abstract, archive_doi),
        "keywords": keywords,
        "license": PAPER["license"],
        "prereserve_doi": True,
        "related_identifiers": [
            {"relation": "isDerivedFrom", "scheme": "doi", "identifier": archive_doi},
            {"relation": "isDerivedFrom", "scheme": "url", "identifier": REPO_URL},
        ],
        "notes": ("Built by scripts/zenodo_preprint.py from the manuscript itself. Not published by "
                  "that script: publishing is irreversible and is a human step."),
    }


def _description(abstract, archive_doi):
    """The abstract, plus the one thing a landing page must say that the abstract does not."""
    return (
        f"<p>{abstract}</p>"
        "<p><strong>Research use only, and not for administration to any person or animal.</strong> "
        "This work is entirely computational. No sequence described has been synthesised or tested, "
        "and nothing here asserts efficacy, potency, safety, a therapeutic window, delivery to a "
        "tumour, or clinical readiness.</p>"
        f'<p>Code, graded artefacts and per-design tables are archived separately under '
        f'<a href="https://doi.org/{archive_doi}">{archive_doi}</a>, which also carries the extended '
        "report of this work — every screen's parameters and the complete bounds on each claim. "
        "This paper is the condensed account; it does not supersede that one.</p>")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--sandbox", action="store_true",
                    help="rehearse against sandbox.zenodo.org; mints nothing real")
    ap.add_argument("--build-only", action="store_true",
                    help="read and validate the metadata, then stop; no network, no token")
    args = ap.parse_args(argv)

    meta = metadata()
    pdf = os.path.join(MANUSCRIPTS, PAPER["pdf"])
    if not os.path.exists(pdf):
        raise SystemExit(f"{PAPER['pdf']} is not built. Run build_submission_pdf.py --paper "
                         "aso-journal first; a preprint record with no paper in it is worse than "
                         "no record.")
    print(f"preprint deposition for {os.path.basename(PAPER['manuscript'])}")
    print(f"  title      : {meta['title']}")
    print(f"  abstract   : {len(meta['description'])} chars of HTML "
          f"({len(re.sub(r'<[^>]+>', ' ', meta['description']).split())} words incl. the notices)")
    print(f"  keywords   : {len(meta['keywords'])} — {'; '.join(meta['keywords'])}")
    print(f"  related    : {[r['identifier'] for r in meta['related_identifiers']]}")
    print(f"  file       : {PAPER['pdf']} ({os.path.getsize(pdf) // 1024} KB, "
          f"sha256 {sha256(pdf)[:16]}…)")
    if args.build_only:
        print("  --build-only: nothing was sent.")
        return 0

    token = os.environ.get("ZENODO_TOKEN")
    if not token:
        raise SystemExit("ZENODO_TOKEN is not set. Create a personal access token at "
                         "zenodo.org/account/settings/applications/tokens/new/ with the "
                         "deposit:write and deposit:actions scopes.")
    base = "https://sandbox.zenodo.org/api" if args.sandbox else "https://zenodo.org/api"
    print(f"  target     : {base}" + ("  (REHEARSAL — mints nothing real)" if args.sandbox else ""))

    #: ⛔ A RE-RUN MUST UPDATE THE DRAFT, NOT MINT A SECOND DOI — the defect zenodo_deposit.py
    #: recorded the expensive way. The state file is the only record of which draft this is.
    state_path = os.path.join(MANUSCRIPTS, PAPER["state"])
    state = json.loads(io.open(state_path, encoding="utf-8").read())
    declared = (state.get("preprint") or {}).get("doi")
    existing = re.search(r"zenodo\.(\d+)$", declared) if declared else None
    if existing:
        dep_id = int(existing.group(1))
        api(base, token, "GET", f"/deposit/depositions/{dep_id}")
        print(f"  updating existing preprint draft {dep_id} ({declared}) — not creating a second one")
        for old in api(base, token, "GET", f"/deposit/depositions/{dep_id}").get("files", []):
            api(base, token, "DELETE", f"/deposit/depositions/{dep_id}/files/{old['id']}")
    else:
        dep_id = api(base, token, "POST", "/deposit/depositions", payload={})["id"]
        print(f"  created preprint draft {dep_id}")

    dep = api(base, token, "PUT", f"/deposit/depositions/{dep_id}", payload={"metadata": meta})
    doi = dep["metadata"].get("prereserve_doi", {}).get("doi")
    with open(pdf, "rb") as fh:
        api(base, token, "PUT", f"{dep['links']['bucket']}/{os.path.basename(pdf)}",
            raw=fh.read(), ctype="application/octet-stream")
    print(f"  uploaded {os.path.basename(pdf)}")

    print("\n" + "=" * 72)
    print(f"DRAFT preprint deposition {dep_id} ready. NOTHING IS PUBLISHED.")
    print(f"  reserved DOI : {doi}")
    print(f"  edit it at   : https://zenodo.org/deposit/{dep_id}")
    print("=" * 72 + "\n")
    print("Two steps remain and neither is this script's to take:")
    print("  * Publish the ARCHIVE draft first. This paper's Data availability cites it, and a")
    print("    preprint freezes whatever it carries — including a DOI that resolves to nothing.")
    print("  * Then publish this deposition by hand. Irreversible.")
    print(f"  * Then record the DOI under `preprint` in {PAPER['state']}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
