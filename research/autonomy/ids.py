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

⛔⛔ AND FOR TWO DAYS THE FIX WAS APPLIED TO ONE HALF OF A PAIR (AUT-PD-171, closed 2026-09-01).
`next_receipt()` carried the discriminator; `next_entry_id()` — the next allocator in this file,
32 lines below it — stayed `max(committed) + 1` and said so. It collided FIVE MEASURED TIMES on 2026-08-29 across three
sessions — AUT-PD-169, then 176, then 177/178, then 178 again, then 179 — and the compounding is the
part that is not obvious: the window is not the derivation instant, it is the WHOLE GATE. A row is
allocated when it is WRITTEN and validated when it is PUSHED, ~13.5 minutes apart against a trunk
that moves every 2-5 minutes, so one cycle was renumbered TWICE for one $0 finding, across five
files and a commit message each time. `next_entry_id()` now takes the same discriminator, from the
same place, and two sessions can both be the Nth filing without sharing a name.

⚠ WHAT THIS DELIBERATELY DOES NOT DO: renumber history. Receipts already on the trunk keep their
bare `CYC-NNNN` ids — a receipt is immutable committed history, `receipt_schema.cycle_number()`
parses both shapes, and rewriting them to look collision-proof would be a fiction about what the
record actually was.
"""

from __future__ import annotations

import os
import pathlib
import re
import sys
from collections import Counter

# ⚠ sys.path, not a package import: this directory is a flat set of scripts run as `python3
# research/autonomy/<name>.py`, and `priority.py` and `session_cap.py` already reach their
# neighbours exactly this way. It makes the import work under `spec_from_file_location` too, which
# is how `systems/tests` loads modules from here.
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import envread  # noqa: E402

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


#: The harness variable that names the session this process IS. ⛔ SPELLED ONCE, HERE, and it is
#: the same variable `session_cap.session_id()` reads: a name agreed in prose between two readers is
#: not agreed at all (AUT-PD-013).
SESSION_ENV = "CLAUDE_CODE_SESSION_ID"

#: The shape of a ledger entry id, bare (`AUT-PD-169`) or discriminated (`AUT-PD-169-6b009680`).
#: ⛔ ONE REGEX FOR THE ALLOCATOR AND EVERY READER, because the receipt half of this module has
#: already paid for the alternative: `session_reaper` carried its own `^CYC-\d+\.json$` and went
#: blind to every discriminated receipt the moment one existed.
#: ⚠ A PREFIX MAY ITSELF CONTAIN HYPHENS — `AUT`, `AUT-PD`, `AUT-PROP`, `AUT-BIX` are all live on
#: the committed ledger — so the prefix is lazy and the ordinal is the first all-digit segment. The
#: separator stays optional to match the derivation this replaces, which accepted `AUT169` too.
ENTRY_ID = re.compile(
    r"^(?P<prefix>[A-Za-z][A-Za-z-]*?)-?(?P<ordinal>\d+)"
    r"(?:-(?P<discriminator>[0-9a-z]{4,16}))?$")


def parse_entry_id(entry_id: str) -> tuple[str, int, str | None] | None:
    """`(prefix, ordinal, discriminator | None)` for a ledger id, or `None` if it is not one.

    ⭐ THE READER'S HALF OF THE SHAPE CHANGE, AND IT IS NOT DECORATION. `priority.merge()` derives
    its own `AUT-NNN` ids from `int(id.rsplit("-", 1)[-1])`, which reads a discriminator as the
    ordinal and throws — caught by a bare `except ValueError: pass`, so the row silently stops
    contributing to the used-ordinal set. That file is not this seat's to edit; this function is
    what its one-line fix should call.
    """
    m = ENTRY_ID.match(str(entry_id or ""))
    if not m:
        return None
    return m.group("prefix"), int(m.group("ordinal")), m.group("discriminator")


def session_discriminator(session_id: str | None = None) -> str:
    """`discriminator()` for a session given explicitly, or for the session this process IS.

    ⛔ AN ABSENT SESSION IS A LOUD FAILURE, NEVER A BARE ID. `discriminator()` already refuses a
    clock and a counter for this reason; an allocator that quietly drops the discriminator when it
    cannot find a session hands back a collidable id while looking like it solved the problem, which
    is worse than raising, because the collision then surfaces ~13.5 minutes later as somebody
    else's blocked push.
    ⚠ AND THE READ IS THREE-VALUED (`envread`, AUT-PROP-034): **unset** — no harness variable, the
    case a sandbox or a bare `python3 -c` hits — is a different fault from **exported empty**, which
    is a harness that set it to nothing, and the caller who has to fix it needs to know which.
    """
    if session_id is not None:
        return discriminator(session_id)
    r = envread.read(SESSION_ENV, default=None,
                     what="the session that owns the ledger row being allocated")
    if not r.value:
        raise ValueError(
            f"cannot allocate a ledger id: {r.detail} ⛔ Pass `session_id=` explicitly, or export "
            f"{SESSION_ENV}. This does NOT fall back to a bare `max+1` id: that derivation put "
            "concurrency outside itself by construction and collided five measured times on "
            "2026-08-29 (AUT-PD-171).")
    return discriminator(r.value)


def next_entry_id(prefix: str, entries: list[dict], session_id: str | None = None) -> str:
    """The next ledger id under `prefix`, carrying this session's discriminator so that two
    concurrent filings cannot be handed one name.

    ⚠ SUPERSEDED, RETAINED (CLAUDE.md rule 1.2). This docstring used to read *"THIS ONE IS HONESTLY
    STILL max+1, AND SAYS SO. Ledger entries merge through git, so a concurrent filing surfaces as a
    rebase conflict or is caught by `duplicate_ids()` at the commit — which is what the item asks
    for."* Both sentences were true and the conclusion was wrong: a rebase conflict and a refused
    push are how the loser LEARNS, not how the collision is avoided, and the loser is whoever pushes
    second, which nobody knows until the push. Measured cost, five occurrences on 2026-08-29: one
    cycle renumbered the same two rows twice, across five files and a commit message each time, and
    re-ran a ~13.5-minute gate after each — because an id appears in ledger cross-references, module
    docstrings, refusal messages, test assertions and amendment declarations.

    ⭐ THE ORDINAL IS STILL SHARED, AND THAT IS THE POINT — the same trade `next_receipt()` makes.
    Two cycles that read the same committed ledger ARE both the 204th filing anybody had committed
    when they started; what the record needs is for both to survive saying so, not for one to be
    renamed into a lie about its place. What must never be shared is the NAME.

    ⛔ THE ORDINAL COUNTS DISCRIMINATED IDS TOO, and this is the one-of-a-pair defect this fix could
    trivially have shipped: widening the mint without widening the scan freezes the ordinal at the
    last bare id forever, so every later session — INCLUDING THIS ONE, on its second row — reuses
    it. `test_ids_cannot_collide` pins both halves.
    """
    disc = session_discriminator(session_id)
    used = []
    for e in entries or []:
        parsed = parse_entry_id(str(e.get("id", "")))
        if parsed and parsed[0] == prefix:
            used.append(parsed[1])
    width = 3
    return f"{prefix}-{max(used, default=0) + 1:0{width}d}-{disc}"


def duplicate_ids(entries: list[dict]) -> dict[str, int]:
    """`{id: count}` for every id used more than once. Empty is the only acceptable answer.

    ⛔ THE ASSERTION THAT WOULD HAVE CAUGHT ALL THREE INSTANCES AT THE COMMIT THAT CREATED THEM, and
    it is four lines. `AUT-PD-012` sat duplicated on origin/main because a duplicate id is invisible
    until a human or a rebase trips over it: nothing reads a ledger looking for one.
    """
    counts = Counter(str(e.get("id")) for e in entries or [] if e.get("id"))
    return {k: v for k, v in counts.items() if v > 1}
