#!/usr/bin/env python3
"""WHAT A REVIEW ACTUALLY READ, ADDRESSED BY CONTENT RATHER THAN BY COMMIT.

⛔⛔ THE MEASUREMENT THAT FORCED THIS. On 2026-09-02 one session spent a night getting PUB-ASO to
`publish_bar` 7/7 and did not get there. Counted from its own logs: **46 gate runs, 8 green, ~12
hours of validation wall clock** — against **118 insertions and 12 deletions across three manuscript
files**. Roughly a hundred lines of editing, twelve hours of re-checking.

★★ THE STRUCTURAL CAUSE, AND IT IS ONE LINE OF `publish_bar`: clauses 1, 2 and 6 compared
`record["reviewed_commit"] != sha`. So ANY commit invalidated a clean round, including commits that
touched nothing the review had read. Measured that night: the journal article's sha256 was
**byte-identical** (`afd60b9e…`) at pins `7ae3cb518` and `4ae4e9929`; five blind seats had read
exactly those bytes; clause 1 failed anyway because the SHA moved. Five seats and a seventy-minute
publication run were then spent re-establishing a fact that had not changed.

⛔ AND THE SHA IS NOT MERELY TOO STRICT — IT IS ALSO TOO LOOSE, which is why this is a re-anchoring
rather than a relaxation. A commit sha says WHEN a review happened, not WHAT it covered: a seat that
read one file and a seat that read forty record the same sha. Two properties, both wanted, neither
supplied:

    too strict  the sha changes when nothing the review read changed  -> a clean round is thrown away
    too loose   the sha does not say which files were read            -> the record cannot be audited

A digest over the reviewed SET has both: it cannot change unless something reviewed changed, and it
cannot be produced without naming exactly what went into it.

★ THE SET IS DERIVED, NEVER TYPED. `deliverable_set` reads the publication's own `document` out of
`systems/graph/publications.json` and adds the files built from it — the ones whose names extend its
stem, which is how this repository already names a manuscript's renderings. Every path is listed in
the record, so a reader can check the set as well as the digest. ⚠ A set that had to be hand-listed
would rot the moment a deliverable was added, and rot silently, which is the failure this module
exists to end rather than to relocate.

⚠ WHAT THIS DOES NOT DO, AND MUST NOT. It does not decide whether a review was good, how many seats
it fielded, or whether the paper is right. It answers exactly one question — *is this record about
the bytes in front of me?* — and it answers it more precisely than the sha did.

Usage:
    python3 research/autonomy/deliverable_digest.py --paper PUB-ASO
    python3 research/autonomy/deliverable_digest.py --paper PUB-ASO --sha <commit>   # as of a commit
    python3 research/autonomy/deliverable_digest.py --paper PUB-ASO --json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
PUBLICATIONS = os.path.join(ROOT, "systems", "graph", "publications.json")

#: ⛔ THE ONE PLACE THE SET'S SHAPE IS DECIDED. A deliverable is the publication's own document, or a
#: file whose name extends that document's stem — `…-journal-article.md` gives `…-journal-article.pdf`,
#: `…-journal-article-manuscript.docx`, `…-journal-article.build-stamp.json` and so on. That is the
#: naming convention this repository already builds renderings under, so the rule reads the
#: convention rather than a list somebody has to remember to update.
#: ⚠ IT IS DELIBERATELY NOT "every file the archive deposits". The deposit is 515 paths including
#: screens, atlases and generators; a review does not read those and claiming it did would be the
#: overstatement this module exists to prevent. The deposit's currency is clause-independent and
#: already has its own instrument (`aso_deposit_drift.py`).
def _publication(pub_id, at=None):
    raw = _read(os.path.relpath(PUBLICATIONS, ROOT), at)
    if raw is None:
        return None
    doc = json.loads(raw)
    rows = doc if isinstance(doc, list) else (doc.get("publications") or list(doc.values()))
    for row in rows:
        if isinstance(row, dict) and row.get("id") == pub_id:
            return row
    return None


def _read(rel, at=None):
    """File bytes now, or as of a commit. `None` when it does not exist there."""
    if at:
        rel = rel.replace("\\", "/")  # Git object paths use '/', including on Windows.
        r = subprocess.run(["git", "-C", ROOT, "show", "%s:%s" % (at, rel)],
                           capture_output=True)
        return r.stdout if r.returncode == 0 else None
    path = os.path.join(ROOT, rel)
    if not os.path.exists(path):
        return None
    with open(path, "rb") as fh:
        return fh.read()


def _listing(directory, at=None):
    if at:
        directory = directory.replace("\\", "/")
        r = subprocess.run(["git", "-C", ROOT, "ls-tree", "--name-only", "%s:%s" % (at, directory)],
                           capture_output=True, text=True)
        return [] if r.returncode else [n for n in r.stdout.split("\n") if n]
    d = os.path.join(ROOT, directory)
    return sorted(os.listdir(d)) if os.path.isdir(d) else []


def deliverable_set(pub_id, at=None):
    """Sorted repo-relative paths that make up the paper as a reader receives it."""
    pub = _publication(pub_id, at)
    if not pub:
        return None
    doc = ((pub.get("document") or {}).get("file"))
    if not doc:
        return None
    directory, base = os.path.split(doc)
    stem = base.rsplit(".", 1)[0]
    out = {doc}
    for name in _listing(directory, at):
        if name.startswith(stem) and name != base:
            out.add(os.path.join(directory, name).replace(os.sep, "/"))
    return sorted(out)


def deliverable_digest(pub_id, at=None):
    """`(digest, [(path, sha256)])` over the set, or `(None, None)` when it cannot be built.

    ⛔ THE PATH IS HASHED WITH THE CONTENT. Hashing contents alone would let a file be RENAMED with
    no change of digest, and a renamed deliverable is a different deliverable to the reader who
    followed a link to it.
    ⛔ AND A MISSING FILE IS NOT AN EMPTY ONE. If any member of the set cannot be read at `at`, this
    returns None rather than a digest over a partial set — a digest that silently covers less than it
    names is exactly the too-loose failure the sha had.
    """
    paths = deliverable_set(pub_id, at)
    if not paths:
        return None, None
    rows = []
    for rel in paths:
        blob = _read(rel, at)
        if blob is None:
            return None, None
        rows.append((rel, hashlib.sha256(blob).hexdigest()))
    acc = hashlib.sha256()
    for rel, digest in rows:
        acc.update(rel.encode("utf-8") + b"\0" + digest.encode("ascii") + b"\n")
    return acc.hexdigest(), rows


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--paper", required=True)
    ap.add_argument("--sha", default=None, help="as of a commit rather than the working tree")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    digest, rows = deliverable_digest(a.paper, a.sha)
    if digest is None:
        print("::error::no deliverable set for %s%s — the publication has no `document.file`, or a "
              "member of its set is absent there. A digest is not emitted over a partial set."
              % (a.paper, " at %s" % a.sha[:12] if a.sha else ""), file=sys.stderr)
        return 1
    if a.json:
        print(json.dumps({"paper": a.paper, "at": a.sha, "digest": digest,
                          "files": [{"path": p, "sha256": h} for p, h in rows]}, indent=2))
        return 0
    print("%s  %s" % (digest[:16], a.paper))
    for p, h in rows:
        print("  %s  %s" % (h[:12], p))
    print("\n%d file(s). This is what a review of %s covers; the commit sha says when, not what."
          % (len(rows), a.paper))
    return 0


if __name__ == "__main__":
    sys.exit(main())
