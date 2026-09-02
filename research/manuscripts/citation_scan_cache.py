#!/usr/bin/env python3
"""Do not re-extract identifiers from a file whose bytes have not changed.

⛔⛔ THE MEASUREMENT. Gate 12 is 39.3 s of a 131.8 s commit loop — 30 % — and profiling it on
2026-09-02 put 48.2 s of a 54.7 s instrumented run inside `_scan`:

    re.findall over the scanned text     24.1 s   47,681 calls
    _redact_failed_fetches               17.0 s   13,028,986 recursive calls
    json.loads / json.dumps               5.7 s    4,253 blobs each way

★ AND ALL OF IT IS A PURE FUNCTION OF THE FILE'S BYTES. `_scan` reads a tracked file, parses it if
it is JSON, blanks the failed-fetch records, dumps it back to text and runs every pattern over the
result. Nothing else enters: no clock, no environment, no other file. So the same bytes give the
same identifiers, every time, and the corpus is ~4,250 committed fetch products of which a commit
typically touches none.

★★ WHAT IS IN THE KEY, AND WHY THAT IS THE WHOLE SAFETY ARGUMENT. Two things: the file's own
sha256, and the sha256 of `lint_citations.py` — which is where `PATTERNS`, `TRAILING`, the redaction
and the bare-key corpus rule all live. Widen a pattern, add a kind, change what counts as a failed
fetch, and every entry is a miss. ⛔ THE SCANNER'S SOURCE IS NOT OPTIONAL IN THAT KEY: a cache keyed
on file bytes alone would answer a NEW question with an OLD scan the first time anyone tightened the
gate, and a citation gate that quietly kept answering the previous version of itself is worse than a
slow one.

⛔ IT IS NOT TRACKED AND IT IS NOT COMMITTED. The file lives under the system temp directory, keyed
by repository path, so it cannot be staged by accident, cannot go stale in the index, and cannot
turn a pytest run into a tracked-tree failure (AUT-PD-186). A fresh container pays the full 39 s
once and then pays ~2 s; CI pays it once per job, which is the correct place for it to be paid,
because CI is not the commit loop.

⚠ AND IT CANNOT TURN AN UNANCHORED IDENTIFIER INTO AN ANCHORED ONE. It caches WHICH identifiers a
file contains, not whether any citation is legitimate; the gate's own comparison of prose against
anchors runs in full, every time, on the identifiers this returns. An unreadable or malformed cache
is a total miss and the scan re-runs.
"""

from __future__ import annotations

import hashlib
import json
import os
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SCHEMA = "emc-citation-scan-cache/1"

#: ⛔ KEYED BY REPOSITORY PATH so two worktrees on one box do not share a file, and living outside
#: the tree so it can never be committed, never be staged by `git add -A`, and never be the thing a
#: tracked-tree guard trips on.
CACHE = os.path.join(tempfile.gettempdir(),
                     "emc-citation-scan-%s.json"
                     % hashlib.sha256(ROOT.encode()).hexdigest()[:12])


def scanner_digest():
    """sha256 of the module that defines what a scan MEANS. A change here misses every entry."""
    with open(os.path.join(HERE, "lint_citations.py"), "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def key_for(rel, blob, scanner):
    """The content key for one file, or None when it cannot be built (a miss)."""
    if scanner is None:
        return None
    acc = hashlib.sha256()
    acc.update(rel.encode("utf-8") + b"\0")
    acc.update(scanner.encode("ascii") + b"\0")
    acc.update(hashlib.sha256(blob).digest())
    return acc.hexdigest()


def load():
    try:
        with open(CACHE, encoding="utf-8") as fh:
            doc = json.load(fh)
    except (OSError, ValueError):
        return {}
    if not isinstance(doc, dict) or doc.get("_schema") != SCHEMA:
        return {}
    entries = doc.get("entries")
    return entries if isinstance(entries, dict) else {}


def save(entries):
    """Best effort. A cache that cannot be written must not fail the gate it accelerates."""
    doc = {"_schema": SCHEMA,
           "_role": "Identifiers found per file by lint_citations._scan, keyed on the file's sha256 "
                    "AND the scanner's own source. Untracked, disposable, rebuilt on a miss.",
           "entries": entries}
    try:
        tmp = CACHE + ".tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(doc, fh, ensure_ascii=False)
        os.replace(tmp, CACHE)
        return True
    except OSError:
        return False


def lookup(entries, key):
    """The recorded {kind: [identifier, ...]} for `key`, or None. Malformed is a MISS."""
    if key is None:
        return None
    got = entries.get(key)
    if not isinstance(got, dict):
        return None
    for kind, idents in got.items():
        if not isinstance(kind, str) or not isinstance(idents, list):
            return None
        if any(not isinstance(i, str) for i in idents):
            return None
    return got


def record(entries, key, per_kind):
    if key is not None:
        entries[key] = {k: sorted(v) for k, v in per_kind.items() if v}
    return entries
