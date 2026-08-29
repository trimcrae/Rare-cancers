#!/usr/bin/env python3
"""Verify the citation-debt ledger: did captured evidence reach the artifacts it is owed to?

⛔ WHAT THIS EXISTS FOR (2026-08-28). The repository had two automated layers that FIND
literature — method-watch.yml's weekly digest and method-watch-triggers.yml's reopening scan —
and a third, write_pending_signals(), that routes a hit into systems/graph/technologies.json for
grading. Nothing routed a hit into the ARTIFACT WHOSE CLAIM IT BEARS ON. So PMID 42570981, an
off-the-shelf peptide vaccine spanning the EWSR1-FLI1 breakpoint, sat captured, triaged and
cited-in-two-manuscripts for four days while research/modalities/vaccine-construct.json — the
file that proposes exactly that design class — said nothing about it. Every gate was green
throughout, because no gate could ask the question.

⛔ IT VERIFIES, IT DOES NOT WRITE. A `discharged` row is not believed: the PMID or DOI must
literally appear in the destination, so a row cannot keep claiming a discharge that a later edit
deleted. Nothing here inserts a citation into anything — see `_what_it_does_NOT_do` in the
ledger. Unread evidence entering a manuscript automatically would be a worse failure than the
one this module fixes.

⚠ AND `open` IS NOT FREE. An open row must name `blocked_on`. A status with no reason behind it
is CLAUDE.md §4's "unanswered question wearing the costume of a status", and this checker's whole
value is that it refuses to render one.

Usage:
  python3 scripts/citation_debt.py            # print the board
  python3 scripts/citation_debt.py --check    # exit non-zero on any violation (the gate)
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
LEDGER = os.path.join(ROOT, "research", "literature", "citation-debt.json")
TRIGGERS = os.path.join(ROOT, "research", "method-watch-triggers.json")

VALID = {"open", "discharged", "declined"}


def _read(path):
    """Return a destination's text, or None if it is not a readable text file.

    ⚠ BINARY DESTINATIONS ARE A REAL CASE, NOT A DEFENSIVE BRANCH: a manuscript's PDF sits
    beside its .md and somebody will eventually list one. A path that cannot be read as text
    is reported as an ERROR rather than silently passing, because "we could not look" and
    "the citation is there" must never render alike.
    """
    try:
        with open(path, encoding="utf-8") as fh:
            return fh.read()
    except (OSError, UnicodeDecodeError):
        return None


def check(verbose=True):
    with open(LEDGER, encoding="utf-8") as fh:
        led = json.load(fh)

    errors, open_rows = [], []
    trigger_ids = set()
    if os.path.exists(TRIGGERS):
        with open(TRIGGERS, encoding="utf-8") as fh:
            trigger_ids = {t["id"] for t in json.load(fh).get("triggers", [])}

    for row in led.get("rows", []):
        rid = row.get("id", "<no id>")
        pmid, doi = row.get("pmid", ""), row.get("doi", "")
        if not pmid and not doi:
            errors.append(f"{rid}: neither pmid nor doi — nothing to look for")
            continue

        # The trigger pointer joins this ledger to the one home for the search queries.
        # A dangling one means a graded hit would name a trigger nobody can find.
        trg = row.get("trigger")
        if trg and trigger_ids and trg not in trigger_ids:
            errors.append(f"{rid}: trigger {trg} is not in {os.path.relpath(TRIGGERS, ROOT)}")

        home = row.get("record_home")
        if home and not os.path.exists(os.path.join(ROOT, home)):
            errors.append(f"{rid}: record_home does not exist: {home}")

        for dest in row.get("owed_to", []):
            path, status = dest.get("path", ""), dest.get("status", "")
            where = f"{rid} -> {path}"
            if status not in VALID:
                errors.append(f"{where}: status {status!r} is not one of {sorted(VALID)}")
                continue
            abspath = os.path.join(ROOT, path)
            if not os.path.exists(abspath):
                errors.append(f"{where}: destination does not exist")
                continue

            text = _read(abspath)
            if text is None:
                errors.append(f"{where}: destination is not readable as text, so this row's "
                              f"status cannot be verified either way")
                continue
            present = (pmid and pmid in text) or (doi and doi in text)

            if status == "discharged" and not present:
                errors.append(f"{where}: marked DISCHARGED but neither PMID {pmid} nor DOI {doi} "
                              f"appears in the file. Either the citation was removed by a later "
                              f"edit, or the row was wrong when written.")
            elif status == "open":
                if present:
                    errors.append(f"{where}: marked OPEN but the identifier is already in the "
                                  f"file. Flip it to `discharged` with a date; a stale OPEN row "
                                  f"is how a board stops being read.")
                elif not dest.get("blocked_on"):
                    errors.append(f"{where}: OPEN with no `blocked_on`. Name what it is waiting "
                                  f"on, or decide it (`discharged` / `declined`).")
                else:
                    open_rows.append((where, dest.get("blocked_on")))
            elif status == "declined" and not dest.get("reason"):
                errors.append(f"{where}: DECLINED with no `reason`. 'We looked and it is not "
                              f"owed' and 'nobody looked' must not render alike.")

    if verbose:
        n_dest = sum(len(r.get("owed_to", [])) for r in led.get("rows", []))
        print(f"citation debt: {len(led.get('rows', []))} record(s), {n_dest} destination(s)")
        for where, why in open_rows:
            print(f"   OPEN  {where}\n         waiting on: {why}")
        for e in errors:
            print(f"   ERROR {e}")
        if not errors and not open_rows:
            print("   every declared destination is decided and every discharge verified")

    return errors


def main():
    errors = check(verbose=True)
    if "--check" in sys.argv:
        if errors:
            print(f"citation_debt --check: {len(errors)} ERROR", file=sys.stderr)
            return 1
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
