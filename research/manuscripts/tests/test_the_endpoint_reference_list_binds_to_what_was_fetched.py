#!/usr/bin/env python3
"""Every PMID and DOI in the endpoint manuscript's reference list, bound to the fetch that returned it.

⛔⛔ FOUND BY AUT-PD-132, WHICH IS THE POINT OF THAT ROW. Recovering the sentences the ablation
harness could not previously locate turned 22 untestable sentences into testable ones; 19 came back
RED and three BLIND. One of the three was this:

    "PMID 27714541. doi 10.1007/s10549-016-4001-y."

Perturbing 27714541 -> 27714547, and every digit of the DOI, turned NO guard red. The identifiers in
this manuscript's reference list were checked by nothing.

★ THE ONE-OF-A-PAIR SHAPE AGAIN, AND THIS REPOSITORY KEEPS FINDING IT. The ASO journal article has
`test_journal_references_match_the_prose.py`; the endpoint manuscript had no equivalent, so the same
class of identifier was guarded in one paper and unguarded in the other.

⚠ AND CLAUDE.md §7 IS EXPLICIT ABOUT WHY THIS ONE MATTERS: claim STRENGTH is orthogonal to citation
PROVENANCE. `lint_claims` reads every one of these lines and has nothing to say about them — a
hedged sentence on a wrong PMID passes it. A drifted identifier points a reader at a different paper,
and it is the one error class this repository can commit without contradicting itself anywhere.

⭐ BOUND TO THE FETCH RECORDS, NOT TO A TYPED LIST. The endpoint artifacts carry
`_identifiers_returned_by_these_fetches` and `records` keyed by PMID — what a real API call returned.
Binding to those means the guard cannot be satisfied by copying the manuscript's own text.
"""

from __future__ import annotations

import glob
import io
import json
import os
import re

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MANUSCRIPTS = os.path.dirname(HERE)
DOC = os.path.join(MANUSCRIPTS, "endpoint", "response-endpoint-indolent-tumours.md")
ARTIFACTS = os.path.join(MANUSCRIPTS, "endpoint", "*.json")

#: `21. Author A, Author B, et al. Title. 2016. PMID 27714541. doi 10.1007/s10549-016-4001-y.`
_REF = re.compile(r"^\d+\. .*?PMID (\d+)\.(?: doi (\S+?)\.)?$", re.M)
_PMID_KEY = re.compile(r"\d{7,8}")


def _index():
    """Every PMID any endpoint artifact records, with the DOI that artifact holds for it.

    ⛔ WALKED, NOT PATHED. The artifacts disagree about shape — one keys records by PMID under
    `records`, another under `_identifiers_returned_by_these_fetches`, a third nests them one level
    deeper — and a guard pinned to today's paths would go quietly green the first time a generator
    moved a key. What is invariant is the SHAPE OF A RECORD: a PMID-looking key, or a `pmid` field.
    """
    out: dict[str, set[str]] = {}
    def walk(node, source):
        if isinstance(node, dict):
            for k, v in node.items():
                if isinstance(v, dict):
                    pmid = k if _PMID_KEY.fullmatch(str(k)) else str(v.get("pmid", ""))
                    if _PMID_KEY.fullmatch(pmid):
                        doi = v.get("doi")
                        out.setdefault(pmid, set())
                        if doi:
                            out[pmid].add(str(doi).lower().rstrip("."))
                walk(v, source)
        elif isinstance(node, list):
            for v in node:
                walk(v, source)
    for path in sorted(glob.glob(ARTIFACTS)):
        try:
            walk(json.load(io.open(path, encoding="utf-8")), os.path.basename(path))
        except (ValueError, OSError):
            continue
    return out


def _references():
    return _REF.findall(io.open(DOC, encoding="utf-8").read())


def test_the_reference_list_is_actually_being_read():
    """⛔ THE POSITIVE CONTROL. A regex that silently matches nothing is how a guard passes over an
    empty set — the failure mode this repository has hit in `_locate`, in `claim_coverage`, and in
    the ablation baseline. 21 references today; the floor is deliberately loose so adding one is not
    a failure, and zero is."""
    refs = _references()
    assert len(refs) >= 20, f"only {len(refs)} reference lines parsed out of the endpoint manuscript"


def test_the_index_is_built_from_real_fetch_records():
    idx = _index()
    assert len(idx) >= 18, f"only {len(idx)} PMIDs found across the endpoint artifacts"


@pytest.mark.parametrize("pmid,doi", _references())
def test_every_cited_identifier_is_one_an_artifact_recorded(pmid, doi):
    idx = _index()
    assert pmid in idx, (
        f"PMID {pmid} appears in the endpoint manuscript's reference list and in NO endpoint "
        f"artifact. Either the fetch that justifies it was never recorded, or a digit drifted — and "
        f"CLAUDE.md §7 forbids writing an identifier from recollection.")
    recorded = idx[pmid]
    if doi and recorded:
        assert doi.lower().rstrip(".") in recorded, (
            f"the reference list gives PMID {pmid} the DOI {doi}, but the artifact that recorded "
            f"that fetch holds {sorted(recorded)}. One of the two drifted.")
