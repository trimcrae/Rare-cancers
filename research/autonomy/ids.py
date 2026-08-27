#!/usr/bin/env python3
"""THE ONE PLACE THAT MINTS AN ID IN THIS LOOP (AUT-PROP-013).

⛔⛔ NOTHING ALLOCATED AN ID OF ANY KIND HERE, AND THE SAME COLLISION FIRED THREE TIMES.
Every session computed the next id as `max(committed) + 1` over the same committed state, so
concurrency was outside the derivation BY CONSTRUCTION. Measured 2026-08-27:

  1. Two sessions ~50 s apart both derived `CYC-0016` from the same receipts directory. Both would
     have written `receipts/CYC-0016.json`; the second would have SILENTLY OVERWRITTEN the first.
     Caught only because the two claims raced on one push window.
  2. The same hour, the same two sessions both filed ledger entries numbered `AUT-PROP-009` and
     `AUT-PROP-010` — four entirely different items under two ids. Caught only by a rebase conflict.
  3. ⛔ AND THE THIRD KILLS THE COMFORTABLE READING THAT THIS IS A RACE: `AUT-PD-012` was used twice
     by two entirely different process defects, filed by SEQUENTIAL cycles. The derivation collides
     on its own. It sat on origin/main unnoticed because nothing validated id uniqueness.

⭐ THE FIX HAS TWO HALVES AND THEY DO DIFFERENT JOBS.

  `next_receipt()` — ALLOCATION THAT CANNOT COLLIDE. The item's own finding: *"an id that cannot
  collide beats a rule about who yields, because the yielding session must first NOTICE, and a
  session that pushes cleanly never does."* The ad-hoc tiebreak actually used that day (claimed
  first, landed second, renumber yourself) is not a mechanism — it required a human to see the
  conflict. So a receipt's id carries a discriminator taken from the SESSION, which is an identity
  the session already has and never has to agree with anybody about. Two sessions deriving the same
  ordinal now produce two different ids and two different files: both survive, both are readable,
  and the ordinal still sorts the record for a human.

  `duplicate_ids()` — THE ASSERTION, which is the cheap half and the one that would have caught all
  three instances at the commit that created them. It is wired into `priority.py` and into
  `research/autonomy/tests`, which preflight gate 15 and tests.yml both run.

⚠ WHAT THIS DELIBERATELY DOES NOT DO: renumber history. Receipts already on the trunk keep their
bare `CYC-NNNN` ids — a receipt is immutable committed history, `receipt_schema.cycle_number()`
parses both shapes, and rewriting them to look collision-proof would be a fiction about what the
record actually was.
"""

from __future__ import annotations

import os
import re
from collections import Counter

RECEIPT_ID = re.compile(r"^CYC-(\d+)(?:-([0-9a-z]{4,16}))?$")

#: How much of the session id goes into a receipt id. Eight hex characters of a UUID is the same
#: discriminator length git uses for a short sha, and for the same reason: long enough that a
#: collision is not a thing that happens, short enough to read aloud.
DISCRIMINATOR_LEN = 8


def discriminator(session_id: str) -> str:
    """The session's contribution to an id it must not have to negotiate.

    ⛔ TAKEN FROM THE SESSION, NEVER FROM A CLOCK OR A COUNTER. A timestamp collides when two
    sessions start in the same second and a counter is the very derivation that failed; the session
    id is the one value a session holds that no other session can hold.
    """
    cleaned = re.sub(r"[^0-9a-zA-Z]", "", session_id or "").lower()
    if not cleaned:
        raise ValueError(
            "a receipt id needs the session id and none was given. ⛔ Do NOT fall back to a clock or "
            "a counter here: both are the derivation this module exists to replace, and a fallback "
            "that silently produces a collidable id is worse than a loud failure.")
    return cleaned[:DISCRIMINATOR_LEN]


def receipt_ordinals(receipt_dir: str) -> list[int]:
    """Every cycle ordinal already on disk, both the bare and the discriminated shape."""
    out = []
    if not os.path.isdir(receipt_dir):
        return out
    for name in os.listdir(receipt_dir):
        if not name.endswith(".json"):
            continue
        m = re.match(r"^CYC-(\d+)", name[:-5])
        if m:
            out.append(int(m.group(1)))
    return out


def next_receipt(receipt_dir: str, session_id: str) -> tuple[str, str]:
    """`(cycle_id, path)` for this session's next receipt. Two sessions can call this against
    identical committed state and cannot be handed the same path.

    ⚠ The ORDINAL may still be shared — that is the point, and it is why the ordinal alone was never
    an identity. Two concurrent cycles are both the twenty-fourth cycle anybody had committed when
    they started; what the record needs is for both to survive saying so.
    """
    n = max(receipt_ordinals(receipt_dir), default=-1) + 1
    cycle_id = f"CYC-{n:04d}-{discriminator(session_id)}"
    return cycle_id, os.path.join(receipt_dir, f"{cycle_id}.json")


def write_receipt(receipt_dir: str, session_id: str, payload: dict) -> str:
    """Write one receipt and return its path. It cannot overwrite another.

    ⛔ MODE `x`, AND THE FIRST DRAFT OF THIS MODULE GOT IT WRONG IN A WAY WORTH RECORDING. That draft
    put an `os.path.exists` guard inside `next_receipt()` — and the guard was UNREACHABLE, because
    the ordinal is `max(existing) + 1` and so the returned path can never already exist. Its test
    failed with DID NOT RAISE, which is the only reason anybody noticed: a guard nobody can trigger
    is a guard that measures nothing, and this repository has now paid for that shape three times in
    one day (`subagent_width`, `research/autonomy/tests`, and here).
    ⭐ The guarantee belongs at the WRITE, where a caller can genuinely hand over a path that exists.
    `x` makes the filesystem refuse it rather than this module promising to.
    """
    path = os.path.join(receipt_dir, f"{next_receipt(receipt_dir, session_id)[0]}.json")
    import json as _json
    with open(path, "x", encoding="utf-8") as fh:
        fh.write(_json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
    return path


def next_entry_id(prefix: str, entries: list[dict]) -> str:
    """The next ledger id under `prefix`, derived over the WHOLE ledger rather than by eye.

    ⚠ THIS ONE IS HONESTLY STILL max+1, AND SAYS SO. Ledger entries merge through git, so a
    concurrent filing surfaces as a rebase conflict or is caught by `duplicate_ids()` at the commit —
    which is what the item asks for and what caught nothing before. The value here is that the
    derivation is written down ONCE instead of being re-eyeballed by every session, which is how
    `AUT-PD-012` was issued twice by two SEQUENTIAL cycles.
    """
    pat = re.compile(rf"^{re.escape(prefix)}-?(\d+)$")
    used = [int(m.group(1)) for m in
            (pat.match(str(e.get("id", ""))) for e in entries or []) if m]
    width = 3
    return f"{prefix}-{max(used, default=0) + 1:0{width}d}"


def duplicate_ids(entries: list[dict]) -> dict[str, int]:
    """`{id: count}` for every id used more than once. Empty is the only acceptable answer.

    ⛔ THE ASSERTION THAT WOULD HAVE CAUGHT ALL THREE INSTANCES AT THE COMMIT THAT CREATED THEM, and
    it is four lines. `AUT-PD-012` sat duplicated on origin/main because a duplicate id is invisible
    until a human or a rebase trips over it: nothing reads a ledger looking for one.
    """
    counts = Counter(str(e.get("id")) for e in entries or [] if e.get("id"))
    return {k: v for k, v in counts.items() if v > 1}
