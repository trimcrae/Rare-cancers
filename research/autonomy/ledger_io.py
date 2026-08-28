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


def write_ledger(path: "str | os.PathLike", data: dict) -> None:
    """Write `data` to `path` as `research-ledger.json`'s one canonical serialization.

    ⛔ NOT `json.dump(data, fh, indent=2)` — that call's `ensure_ascii` defaults to `True` and
    escapes every non-ASCII character. This function exists so no caller can make that mistake by
    typing the parameters out again.
    """
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(dumps_ledger(data))
