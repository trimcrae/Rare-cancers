#!/usr/bin/env python3
"""Export the prior-art retrieval evidence behind the manuscript's first-in-kind claim. ($0, offline.)

⛔ WHY THIS EXISTS. The Introduction states: "Across 5,153 unique records retrieved from Europe PMC,
four mention EWSR1::NR4A3 at title or abstract level; these resolve to three papers, of which one
concerns EMC and none is an oligonucleotide study." That is the paper's ONLY first-in-kind claim, and
a first-in-kind claim is the one a reviewer is most entitled to check, because it is a statement
about an absence and absences are where search methodology hides.

⛔⛔ THE EVIDENCE FOR IT WAS NOT IN THE DEPOSIT. The two retrieved corpora live on the
`literature-cache` branch — 4,252 records under `aso-priorart-fusiononco` and 1,133 under
`aso-priorart-junction` — and the archive manifest is built from THIS branch, so a depositor
following the manifest would have shipped the audited summary and none of the rows it summarises.
The manifest's own `gaps` block said so, which is the block doing its job; this module is the
closing of it rather than another note about it.

★ WHAT IS EXPORTED AND WHAT IS NOT. The identifiers, the per-corpus counts, their overlap and the
union — not the full texts, which run to thousands of files and are not what the claim rests on. The
claim is arithmetic over a set of identifiers: how many unique records were searched. That set is
small enough to travel and is exactly what lets a reader re-run the count.

✅ THE ARITHMETIC IS RE-DERIVED HERE, NOT COPIED FROM THE PAPER. 4,252 + 1,133 = 5,385 raw records,
232 of them in both corpora, so 5,153 unique. If that ever stops equalling the number in the
Introduction this module's own check fails, which is the point — a first-in-kind claim that drifts
from its evidence is worse than one never made.

⚠ WHAT THIS DOES NOT ESTABLISH. That a search returned no oligonucleotide study against any NR4A3
fusion is a statement about THIS query over THIS corpus at THIS date. It is not proof that no such
work exists; a paper indexed under different terms, or not indexed at all, would not appear. The
manuscript should be read as claiming the search found none, which is what it says.

    python3 research/manuscripts/aso_priorart_evidence.py
    python3 research/manuscripts/aso_priorart_evidence.py --check
"""
from __future__ import annotations

import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(HERE, "aso", "fusion-junction-aso-priorart-evidence.json")

CORPORA = {
    "aso-priorart-fusiononco": "literature/aso-priorart-fusiononco/_index.json",
    "aso-priorart-junction": "literature/aso-priorart-junction/_index.json",
}
BRANCH = "origin/literature-cache"

#: The number the Introduction prints. Named once so the check below can fail loudly.
CLAIMED_UNIQUE = 5153


def _read(path):
    """A corpus index from the fetch branch, or None. `git show`, no network."""
    r = subprocess.run(["git", "show", f"{BRANCH}:{path}"], cwd=REPO,
                       capture_output=True, text=True, timeout=120)
    if r.returncode != 0:
        return None
    try:
        d = json.loads(r.stdout)
    except Exception:  # noqa: BLE001
        return None
    return d if isinstance(d, list) else (d.get("records") or list(d.values()))


def build():
    per, missing = {}, []
    for name, path in CORPORA.items():
        recs = _read(path)
        if recs is None:
            missing.append(path)
            continue
        ids = set()
        for r in recs:
            if not isinstance(r, dict):
                continue
            k = str(r.get("pmid") or r.get("id") or r.get("pmcid") or "").strip()
            if k:
                ids.add(k)
        per[name] = {"n_records": len(recs), "n_identified": len(ids), "identifiers": sorted(ids)}
    if missing:
        print(f"REFUSED: {BRANCH} does not carry {missing}. Fetch it first: "
              f"git fetch origin literature-cache:refs/remotes/origin/literature-cache",
              file=sys.stderr)
        return None

    sets = {k: set(v["identifiers"]) for k, v in per.items()}
    names = sorted(sets)
    union = set().union(*sets.values())
    overlap = set.intersection(*sets.values()) if len(sets) > 1 else set()

    return {
        "_what": ("The retrieval evidence behind the manuscript's first-in-kind statement: which "
                  "Europe PMC corpora were searched, how many unique records they hold, and every "
                  "identifier, so the count can be re-derived rather than taken on trust."),
        "_why": ("The claim is the one a reviewer is most entitled to check, and its evidence lived "
                 "on a branch the deposit is not built from. Exported so it travels with the "
                 "archive."),
        "⚠_what_this_does_not_establish": (
            "That a search returned no oligonucleotide study against any NR4A3 fusion is a "
            "statement about this query, over this corpus, at this date. It is not proof that no "
            "such work exists: a paper indexed under other terms, or not indexed, would not "
            "appear. The manuscript claims the search found none, which is what it says."),
        "_source_branch": BRANCH,
        "_corpora": {k: CORPORA[k] for k in names},
        "counts": {
            "per_corpus": {k: {"n_records": per[k]["n_records"],
                               "n_identified": per[k]["n_identified"]} for k in names},
            "raw_sum": sum(per[k]["n_identified"] for k in names),
            "in_both_corpora": len(overlap),
            "unique_records": len(union),
            "claimed_in_manuscript": CLAIMED_UNIQUE,
            "agrees_with_manuscript": len(union) == CLAIMED_UNIQUE,
            "_arithmetic": (f"{' + '.join(str(per[k]['n_identified']) for k in names)} = "
                            f"{sum(per[k]['n_identified'] for k in names)} raw, minus "
                            f"{len(overlap)} present in both, gives {len(union)} unique."),
        },
        "identifiers_in_both_corpora": sorted(overlap),
        "unique_identifiers": sorted(union),
    }


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    art = build()
    if art is None:
        return 2
    if not art["counts"]["agrees_with_manuscript"]:
        print(f"⛔ the corpora now hold {art['counts']['unique_records']} unique records against "
              f"the manuscript's {CLAIMED_UNIQUE}. Fix whichever is wrong; do not adjust this "
              f"constant to match.", file=sys.stderr)
    new = json.dumps(art, indent=1) + "\n"
    if "--check" in argv:
        cur = open(OUT).read() if os.path.exists(OUT) else ""
        if cur != new:
            print("prior-art evidence artifact is stale", file=sys.stderr)
            return 1
        print("prior-art evidence is current")
        return 0
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(new)
    c = art["counts"]
    print(f"wrote {os.path.basename(OUT)}: {c['_arithmetic']} "
          f"agrees_with_manuscript={c['agrees_with_manuscript']}", file=sys.stderr)
    return 0 if art["counts"]["agrees_with_manuscript"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
