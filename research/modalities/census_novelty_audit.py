#!/usr/bin/env python3
"""Audit every `never_searched` census row against the repository's own prose. ($0, stdlib + git)

⛔ WHY THIS EXISTS, AND IT IS A DEFECT IN THE CENSUS'S OWN DESIGN. `prior_coverage` is the census's
headline field, and the test suite checks it in ONE DIRECTION ONLY: claiming `searched_before` requires
a resolvable document, so a false POSITIVE cannot survive. Nothing checks a false NEGATIVE. A row that
says `never_searched` when the repository has in fact already worked the class passes every gate,
inflates the headline count, and -- far worse -- invites somebody to build on a "new" lead that is
already graded.

That is not hypothetical. It was found on 2026-08-09, the same day the census landed:
`MOD-HYPOXIA-PRODRUG` was filed `never_searched` while `emc-hypoxia-reading.md` (2026-08-07) had
already retrieved the class's entire clinical record, audited the EMC signal against a genome-wide
null, and ruled explicitly that the signal is "a reason to ask a question, not a reason to revisit
that class". The census had re-proposed a graded lane as an unexplored one -- the exact failure it was
built to prevent, committed by the instrument built to prevent it.

⚠ THIS SCRIPT DOES NOT DECIDE ANYTHING. It surfaces candidate collisions for a human or agent to
adjudicate, because a term match is not a coverage claim: "hypoxia" appears in files that are about
something else entirely. Every hit is a question, and the adjudication is recorded in the census row
itself, never here.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
CENSUS = os.path.join(REPO, "systems", "graph", "modalities.json")
OUT = os.path.join(HERE, "census-novelty-audit.json")

#: Files that cannot count as prior coverage: the census IS these, so matching itself is circular.
SELF = (
    "systems/graph/modalities.json",
    "systems/taxonomy/modality.md",
    "systems/views/",                       # every generated view, including the census's own
    "research/manuscripts/cancer-modality-census.md",
    "research/modalities/census_novelty_audit.py",
    "research/modalities/census-novelty-audit.json",
    "research/modalities/census_route_expression_grading.py",
    "research/modalities/census-route-expression-grading.json",
    "systems/tests/test_modality_census.py",
)

#: Words too common to discriminate. A hit on one of these is noise, not coverage.
STOP = {
    "the", "and", "for", "with", "non", "anti", "pro", "sub", "type", "cell", "cells", "acid",
    "based", "class", "agents", "agent", "therapy", "therapies", "inhibitor", "inhibitors",
    "targeted", "targeting", "directed", "delivery", "small", "molecule", "molecules", "drug",
    "drugs", "conjugate", "conjugates", "receptor", "receptors", "protein", "proteins", "tumour",
    "tumor", "cancer", "gene", "genes", "rna", "dna", "and/or", "its", "own", "beyond", "other",
    "chemotherapy", "radiotherapy", "editing", "engagers", "engager", "vaccines", "vaccine",
    "modulators", "modulation", "agonism", "agonists", "agonist", "antagonists", "antagonism",
    "inhibition", "family", "pathway", "state", "response", "regional", "local", "matrix",
}


def tracked_text_files():
    out = subprocess.run(["git", "-C", REPO, "ls-files"], capture_output=True, text=True, check=True)
    keep = []
    for rel in out.stdout.splitlines():
        if not rel.endswith((".md", ".json")):
            continue
        if any(rel == s or rel.startswith(s) for s in SELF):
            continue
        if rel.startswith("archive/"):
            continue
        keep.append(rel)
    return keep


def terms_for(row):
    """Distinctive search terms for one modality class.

    Built from the exemplar and the class name, minus stop-words. ⚠ Deliberately NOT built from the
    rationale: the rationale is where the census argues, so it names neighbouring concepts, and
    searching on those manufactures collisions with the routes it was distinguishing itself from.
    """
    src = " ".join([row.get("exemplar") or "", row["name"]])
    words = re.findall(r"[A-Za-z][A-Za-z0-9\-]{2,}", src)
    terms = []
    for w in words:
        lw = w.lower().strip("-")
        if lw in STOP or len(lw) < 4:
            continue
        if lw not in terms:
            terms.append(lw)
    return terms[:6]


def main():
    rows = json.load(open(CENSUS, encoding="utf-8"))
    files = tracked_text_files()
    blobs = {}
    for rel in files:
        try:
            with open(os.path.join(REPO, rel), encoding="utf-8", errors="ignore") as fh:
                blobs[rel] = fh.read().lower()
        except OSError:
            continue

    findings = {}
    for row in rows:
        if row["prior_coverage"] != "never_searched":
            continue
        terms = terms_for(row)
        if not terms:
            continue
        hits = {}
        for rel, text in blobs.items():
            matched = [t for t in terms if t in text]
            # ⭐ THE BAR IS TWO DISTINCT TERMS, NOT ONE. A single term match is overwhelmingly noise
            # -- "perfusion" appears in every compute document about GPU throughput. Two distinct
            # terms from the same class co-occurring in one file is a real signal worth reading.
            if len(matched) >= 2:
                hits[rel] = matched
        if hits:
            findings[row["id"]] = {
                "name": row["name"],
                "verdict": row["verdict"],
                "terms_searched": terms,
                "files_matching_two_or_more_terms": dict(sorted(
                    hits.items(), key=lambda kv: -len(kv[1]))[:8]),
                "n_files": len(hits),
                "adjudication": "UNREVIEWED — a term match is not a coverage claim",
            }

    doc = {
        "_what": "Candidate false-novelty collisions: census rows filed `never_searched` whose class "
                 "terms already co-occur in a repository document.",
        "_why": "`prior_coverage` is checkable in one direction only. Claiming a prior search requires "
                "a resolvable document, so a false POSITIVE cannot survive; nothing catches a false "
                "NEGATIVE, and one was found the day the census landed.",
        "_this_decides_nothing": "Every entry is a question for a human or agent to adjudicate. A term "
                                 "match is not coverage: the same word appears in documents about "
                                 "something else, and the census's own files are excluded because "
                                 "matching itself would be circular.",
        "_bar": "two distinct class terms co-occurring in one tracked .md or .json outside the census "
                "itself and outside archive/",
        "n_never_searched_rows": sum(1 for r in rows if r["prior_coverage"] == "never_searched"),
        "n_rows_with_a_candidate_collision": len(findings),
        "findings": dict(sorted(findings.items(), key=lambda kv: -kv[1]["n_files"])),
    }
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    print(f"{doc['n_never_searched_rows']} never_searched rows; "
          f"{doc['n_rows_with_a_candidate_collision']} carry a candidate collision")
    for rid, f in list(doc["findings"].items())[:25]:
        top = list(f["files_matching_two_or_more_terms"])[:2]
        print(f"  {rid:<28} {f['n_files']:>3} file(s)  e.g. {', '.join(os.path.basename(t) for t in top)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
