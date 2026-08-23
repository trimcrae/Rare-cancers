#!/usr/bin/env python3
"""Read the PUBLISHED Zenodo record the papers cite, and report what a reader would actually get.

⛔ WHY THIS EXISTS RATHER THAN TAKING "IT IS PUBLISHED" ON TRUST. Both manuscripts' Data
availability statements promise a DOI, and this repository's own scar tissue is a status owned by an
outside system that nobody re-read: the preprint checklist carried "⏳ Awaiting bioRxiv screening"
for three days after bioRxiv had declined the submission. The lesson recorded there is that such a
status decays silently, so it carries the date it was taken and the name of whoever can refresh it.

★ THIS IS THE ONE READING THAT SETTLES IT, AND IT IS THE READER'S OWN. Not "did somebody click
publish" but "does the identifier printed in the paper resolve, to a record holding what the paper
says it holds". The Zenodo REST API serves published records WITHOUT a token, so this needs no
secret and can run anywhere with egress. ⚠ It cannot run in the dev sandbox: zenodo.org does not
answer at the egress proxy (measured 2026-08-23, connection refused, not a 403). It runs on a
runner, which is what `deposit-zenodo.yml` dispatches it from.

⚠ WHAT IT DOES NOT DO: judge. It prints what the record says and exits non-zero only when the
record cannot be read at all or is not in a published state. Comparing file counts and digests to
this repository is `test_the_deposit_the_papers_cite_is_current.py`'s job, offline, against values
a human transcribed from this output.

    python3 scripts/zenodo_verify.py                 # the DOI deposit-state.json names
    python3 scripts/zenodo_verify.py --doi 10.5281/zenodo.22061075
"""
from __future__ import annotations

import argparse
import io
import json
import os
import re
import sys
import urllib.error
import urllib.request

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE = os.path.join(REPO, "research", "manuscripts", "aso", "deposit-state.json")


def _state_doi():
    state = json.loads(io.open(STATE, encoding="utf-8").read())
    #: The pending draft is what we are asking about while one exists; once it is published and the
    #: state has been updated, the same question is asked of the published block.
    return (state.get("pending") or state["published"])["doi"]


def fetch(doi):
    m = re.search(r"zenodo\.(\d+)$", doi)
    if not m:
        raise SystemExit(f"{doi!r} is not a Zenodo DOI this script can turn into a record id.")
    url = f"https://zenodo.org/api/records/{m.group(1)}"
    try:
        with urllib.request.urlopen(url, timeout=120) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as exc:
        #: ⛔ A 404 ON A RESERVED-BUT-UNPUBLISHED DOI IS THE EXPECTED ANSWER, NOT A FAILURE OF THIS
        #: SCRIPT, and saying so is the difference between "not published yet" and "something is
        #: wrong". A reserved DOI exists as a string and resolves to nothing until the click.
        if exc.code == 404:
            raise SystemExit(
                f"{doi} returns 404 from the public records API. That is exactly what a RESERVED "
                "but unpublished DOI does, so the most likely reading is that the draft has not "
                "been published. It is also what a wrong record id does. Check "
                f"https://doi.org/{doi} in a browser before concluding either.")
        raise SystemExit(f"Zenodo GET {url} -> {exc.code}: {exc.read().decode()[:400]}")
    except urllib.error.URLError as exc:
        raise SystemExit(f"zenodo.org could not be reached: {exc.reason}. This script needs egress; "
                         "the dev sandbox has none to zenodo.org.")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--doi", help="override the DOI read from deposit-state.json")
    args = ap.parse_args(argv)

    doi = args.doi or _state_doi()
    rec = fetch(doi)
    meta = rec.get("metadata", {})
    files = rec.get("files", [])
    print(f"record {rec.get('id')} — {doi}")
    print(f"  state        : {rec.get('state')} (submitted={rec.get('submitted')})")
    print(f"  title        : {meta.get('title')}")
    print(f"  version DOI  : {meta.get('doi') or rec.get('doi')}")
    #: ⭐ THE CONCEPT DOI IS THE ONE THAT MOVES. Printed because it is the identifier a reader gets
    #: from "all versions", and because the question of whether a paper should ever cite it has
    #: already been answered no — see scripts/zenodo_preprint.py's header.
    print(f"  concept DOI  : {rec.get('conceptdoi')}  (resolves to the NEWEST version, always)")
    print(f"  published    : {meta.get('publication_date')}")
    print(f"  type         : {meta.get('resource_type', {}).get('type')}")
    print(f"  files        : {len(files)}")
    for f in files[:5]:
        print(f"      {f.get('key')}  {f.get('size')} bytes  "
              f"{(f.get('checksum') or '')[:20]}")
    print(f"  landing page : {rec.get('links', {}).get('html')}")

    if rec.get("state") != "done" or not rec.get("submitted"):
        raise SystemExit(
            f"\nthe record exists but reports state={rec.get('state')!r}, "
            f"submitted={rec.get('submitted')!r}. A reader following the DOI does not yet get a "
            "published record.")
    print("\nPUBLISHED. The DOI both papers cite resolves to this record.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
