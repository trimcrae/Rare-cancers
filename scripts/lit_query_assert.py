#!/usr/bin/env python3
"""Assert that the Europe PMC `query` path of fetch-literature.yml ACTUALLY SEARCHED.

Why this exists (CLAUDE.md §6): that query path was DECORATIVE until 2026-08-05 — the workflow
header claimed the search, `scripts/fetch-paper.mjs` implemented it, and the workflow never invoked
it, so a dispatch carrying a query searched for nothing and reported SUCCESS. It was wired up on
2026-08-05, and a wiring that is described rather than asserted is a hope, not a property
(same shape as the `fleet_armed` CENSUS_LANE string defect).

So this runs AFTER the search step and turns three silent-success modes into hard failures:

  1. `_index.json` absent           -> the search step did not run at all.
  2. `_index.json` empty            -> the query matched nothing; a corpus of zero records must never
                                       be published under a slug that claims a subject.
  3. EXPECT_PMIDS not all present   -> the known-positive control did not come back. This is the one
                                       that discriminates "the search ran" from "the search ran and
                                       returned the real corpus": a caller names a PMID it KNOWS the
                                       query must match, and the run fails if the API answered with
                                       something else.

It also prints a readable digest of what came back, so the Actions log itself is evidence of the
retrieval rather than a "success" with nothing behind it.

Environment:
  LIT_EXPECT_PMIDS   comma/space separated PMIDs that MUST appear in the result set (optional)
  LIT_MIN_RECORDS    minimum record count, default 1
  LIT_CACHE          cache dir, default .cache/literature
"""
import json
import os
import sys

CACHE = os.environ.get("LIT_CACHE", os.path.join(".cache", "literature"))
INDEX = os.path.join(CACHE, "_index.json")


def fail(msg: str) -> int:
    print(f"::error::{msg}")
    return 1


def main() -> int:
    if not os.path.exists(INDEX):
        return fail(
            f"{INDEX} does not exist. The Europe PMC search step did not produce an index, so this "
            "run searched for NOTHING. That is the exact failure this check exists to catch — do not "
            "publish, and do not read the run's green tick as a retrieval."
        )
    with open(INDEX, "r", encoding="utf-8") as fh:
        index = json.load(fh)
    if not isinstance(index, list):
        return fail(f"{INDEX}: expected a JSON list of records, got {type(index).__name__}")

    min_records = int(os.environ.get("LIT_MIN_RECORDS", "1") or 1)
    n = len(index)
    n_oa = sum(1 for r in index if r.get("fullTextFile"))
    n_abs = sum(1 for r in index if r.get("abstract"))
    print(f"Europe PMC returned {n} record(s): {n_oa} with full text on disk, {n_abs} with abstracts.")

    # A digest, oldest-first, so the log is readable evidence of WHAT was retrieved.
    for r in sorted(index, key=lambda r: (str(r.get("year") or ""), str(r.get("pmid") or "")))[:60]:
        flag = "FT" if r.get("fullTextFile") else ("ab" if r.get("abstract") else "  ")
        print(f"  [{flag}] {r.get('year')}  pmid={r.get('pmid') or '-':<10} "
              f"{r.get('pmcid') or '-':<12} {str(r.get('title') or '')[:110]}")
    if n > 60:
        print(f"  ... and {n - 60} more (see _index.json)")

    if n < min_records:
        return fail(
            f"Europe PMC returned {n} record(s), below the required minimum of {min_records}. "
            "A query that matches nothing is not a successful retrieval."
        )

    raw = os.environ.get("LIT_EXPECT_PMIDS", "").replace(",", " ").split()
    if raw:
        have = {str(r.get("pmid")) for r in index if r.get("pmid")}
        missing = [p for p in raw if p not in have]
        print(f"Known-positive control PMIDs required: {raw}; missing: {missing or 'none'}")
        if missing:
            return fail(
                f"Known-positive control FAILED: PMID(s) {missing} were not in the {n} record(s) "
                "Europe PMC returned for this query. Either the query is wrong or the search path is "
                "not doing what it says. Do not trust this corpus."
            )
        print("Known-positive control PASSED — the query path returned the record it was told to find.")
    else:
        print("::warning::No LIT_EXPECT_PMIDS given, so this run proves the search RAN but not that "
              "it returned the right corpus. Pass a known-positive PMID when the answer matters.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
