#!/usr/bin/env python3
"""THE ONE PLACE THAT SERIALIZES `research-ledger.json` (AUT-PD-037).

⛔⛔ THE LEDGER HAD NO ENFORCED SERIALIZATION, SO EVERY WRITER INVENTED ONE. Measured 2026-08-27:
a driver's hand-writes used `json.dumps(d, indent=1)`; the file's own documented "generator",
`priority.py:591-593`, wrote `json.dump(ledger, fh, indent=2)` — `ensure_ascii` DEFAULTS TO TRUE,
so that call escapes every ⛔ ⭐ ⚠ ★ and em-dash in the file as `\\uXXXX`. Neither matched what was
actually on `origin/main`. The mismatch turns every cross-session edit into a whole-file diff: one
real incident produced a rebase conflict spanning lines 2-9340 for what was semantically a five-row
delta against a one-row delta.

⭐ THE CANONICAL FORMAT, READ FROM WHAT WAS ALREADY COMMITTED (never invented): `indent=2`,
`ensure_ascii=False`, one trailing newline. Verified byte-for-byte on 2026-08-28 —
`json.dumps(data, indent=2, ensure_ascii=False) + "\\n"` reproduced the committed file exactly, so
this module pins the convention most writers had already converged on by hand, not a fresh
preference.

⭐ THIS IS THE FIX ITSELF, NOT A DOCSTRING ABOUT ONE. A comment saying "use indent=2" is exactly the
class of agreement-in-prose this repository keeps paying for (AUT-PD-013's fan-out key,
AUT-PROP-013's ids, the reader/writer key mismatch) — nothing enforced it and nothing could. Every
writer of `research-ledger.json` must import `write_ledger` from here instead of calling
`json.dump`/`json.dumps` directly; `research/autonomy/tests/test_the_ledger_has_one_serialization.py`
round-trips the committed file through it and fails if the parameters ever drift again, and fails
if a writer stops calling this module at all.
"""

from __future__ import annotations

import json
import os
import sys
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

#: The exact parameters, pinned once. Nothing downstream should ever type `indent=` or
#: `ensure_ascii=` again for this file — import `write_ledger` (or `dumps_ledger`, for a caller
#: that needs the text without touching disk) and call it.
INDENT = 2
ENSURE_ASCII = False


def dumps_ledger(data: dict) -> str:
    """The canonical ledger TEXT — `json.dumps` at the pinned parameters, plus one trailing
    newline. Split out from `write_ledger` so a caller that wants the bytes without writing them
    (a test, a diff preview) shares the identical serialization rather than reconstructing it."""
    return json.dumps(data, indent=INDENT, ensure_ascii=ENSURE_ASCII) + "\n"


def write_ledger(path: "str | os.PathLike", data: dict, check: bool = True) -> None:
    """Write `data` to `path` as `research-ledger.json`'s one canonical serialization.

    ⛔ NOT `json.dump(data, fh, indent=2)` — that call's `ensure_ascii` defaults to `True` and
    escapes every non-ASCII character. This function exists so no caller can make that mistake by
    typing the parameters out again.

    ⛔⛔ AND IT IS ALSO THE ADMISSION GATE FOR THE LOOP'S OWN SCORING EVIDENCE (AUT-PROP-036).
    `research/autonomy/admissibility.py` names, in advance and in code, the observable signature of
    a score change nothing can account for; this is the one place every writer of the ledger already
    has to pass through, so it is where the predicate is CHECKED rather than merely documented —
    before the evidence is allowed to change a row's score, state or `what`. It raises
    `admissibility.InadmissibleWrite`; it never writes a partial file.

    ⛔⛔ AND IT IS THE FIELD-NAME GATE TOO (AUT-PD-030). Every reader of this file keys off exact
    field names and nothing held a whitelist, so a one-edit misspelling was indistinguishable from a
    new field. Measured on a scratch copy of the committed ledger, 2026-09-01: a row carrying
    `require_trimcrae: true` — ONE deletion from `requires_trimcrae` — was offered by
    `continuity.ready()`, was NOT flagged by `continuity.unclassified_outward()`, and drew no
    complaint from `prepush_ledger_guard.py`, on the one field CLAUDE.md §3 exists to protect.
    `ledger_schema.check_write` is that gate, HERE for the same reason `admissibility` is: this is
    the one place a programmatic writer cannot get past. It raises `ledger_schema.SchemaViolation`;
    it never writes a partial file.
    ⚠ IT IS NOT THE WHOLE GATE, AND SAYING SO MATTERS: most ledger rows are hand-authored JSON that
    never comes through this function at all. `tests/test_a_near_miss_field_name_cannot_enter_the_ledger.py`
    runs the same schema over the COMMITTED file, and that test directory is in the default preflight
    tier — so a hand edit is caught at the commit and a programmatic write is caught here.

    ⚠ `check=False` EXISTS FOR TESTS AND FOR NOTHING ELSE, AND IT IS NOT A WAY PAST A REFUSAL. A
    real writer whose score change is refused records why on the row (`_score_correction`) or
    re-derives the number; a test that is deliberately constructing an inadmissible ledger in order
    to assert the gate fires needs to be able to lay one down on disk first.
    """
    if check:
        # Imported here, not at module scope: `admissibility` reaches `priority` for the age term,
        # and `priority` imports this module — a top-level import would close the cycle.
        import admissibility  # noqa: PLC0415

        import ledger_schema  # noqa: PLC0415

        # ⛔⛔ DERIVE THE HEADER TOTALS BEFORE CHECKING THEM. They are counts of the rows in this
        # very document, so a writer that appended a row and did not separately run
        # `priority.py --write` left the file's own summary describing a ledger that no longer
        # existed — and that is not a hypothetical tidiness point: across the eight committed
        # PREFLIGHT_FULL logs, ledger bookkeeping is what failed the PUBLICATION gate in three of
        # them, twice on 2026-09-02 alone, each costing a full re-run of a nine-minute gate. The
        # modalities suite, 72 % of every one of those runs, failed in none of them.
        # ★ CLAUDE.md §1: "a total is DERIVED, never typed — regenerate it." This is the one place
        # every programmatic writer already passes through, so it is where the regeneration
        # belongs. `header_problems` keeps guarding hand-authored edits, which never come here.
        corrected = ledger_schema.derive_headers(data)
        if corrected:
            print("ledger_io: re-derived header total(s) %s from the rows" % ", ".join(corrected),
                  file=sys.stderr)
        admissibility.check_write(os.fspath(path), data)
        ledger_schema.check_write(os.fspath(path), data)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(dumps_ledger(data))
