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

⛔⛔ AND THE SESSION IS NOT THE ALLOCATOR (AUT-085, 2026-09-02). A SUBAGENT INHERITS ITS PARENT'S
`CLAUDE_CODE_SESSION_ID` VERBATIM, and a five-wide fan-out of seats each filing a ledger row is this
repository's standing work pattern (CLAUDE.md §1, `subagent_width`). Measured, not reasoned: the
driver read `e71cf460`, a subagent it dispatched read `e71cf460`, and two concurrent subprocesses
carrying that one session id were both handed `AUT-PD-205-e71cf460` off the committed ledger. Among
seats of one session the discriminator was a constant, so `next_entry_id` degraded to
`max(committed) + 1` — the exact derivation AUT-PD-171 was closed for removing, one level down.

⭐ SO THE DISCRIMINATOR HAS TWO HALVES, `<session>-<process>`, AND THEY ANSWER DIFFERENT QUESTIONS.
The session half says WHICH SESSION produced the row and is unchanged, so `AUT-085-e71cf460` and
`AUT-085-e71cf460-3f19c2b1` still share a greppable prefix. The process half says WHICH ALLOCATOR,
and it is taken from the kernel because the harness exports nothing that separates one seat from its
sibling — measured 2026-09-02 over the whole environment: `CLAUDE_PID` is the shared harness process
(every seat's shell is a direct child of it), `CLAUDE_CODE_MESSAGING_SOCKET` names that same pid, and
`CLAUDE_CODE_CHILD_SESSION` is the literal `1`, a flag that separates child from parent and never
child from child.

⚠ AND THE PROCESS HALF OVER-SEPARATES, WHICH IS THE SAFE DIRECTION AND IS SAID OUT LOUD. It names a
MINT, not a seat: a seat runs each of its commands in a fresh process, so two rows filed by one seat
carry two process halves. Uniqueness is preserved (that is the whole requirement); what is lost is
re-derivation — ⛔ AN ID IS MINTED ONCE AND WRITTEN DOWN, and re-running `next_entry_id` in a new
process to "check" a row's id returns a DIFFERENT name for the same row. Nothing on the trunk
re-derives (the three other mentions of `next_entry_id` are hint strings in `priority.py`,
`push_guard.py` and `prepush_ledger_guard.py`); a human doing it by hand is the hazard.

⛔⛔ AND A DISCRIMINATOR CANNOT SEPARATE A CALLER FROM ITSELF — MEASURED THE SAME HOUR, AND IT IS
THE STRONGER FINDING (AUT-086/087/088, 2026-09-02). Three ledger rows were built in ONE list
comprehension, each calling `next_entry_id("AUT", entries)`, none appended until the comprehension
finished. All three were handed `AUT-086-e71cf460`. ⛔ NO CONCURRENCY WAS INVOLVED AT ALL: the
ordinal is `max(ordinals in the list passed in) + 1`, and the list had not grown, so the second call
re-derived the first call's answer. No token of any kind fixes this — a session id, a subagent id and
a pid are all CONSTANT within one process, which is precisely what makes them useful for the other
two cases.

★★ SO THERE ARE THREE FAILURE MODES AND TWO MECHANISMS, AND NEITHER MECHANISM SUBSTITUTES FOR THE
OTHER. Writing them down in one place because each was found separately, months apart, by paying for
it:

  1. ONE PROCESS, MINTED TWICE BEFORE APPENDING   -> `_ISSUED`, an in-process record of every name
     this process has handed out. AUT-086, measured 2026-09-02.
  2. TWO CONCURRENT SEATS OF ONE SESSION          -> the PROCESS half of the discriminator.
     AUT-085, measured 2026-09-02.
  3. TWO SESSIONS ON ONE COMMITTED LEDGER         -> the SESSION half. AUT-PD-171, five measured
     occurrences 2026-08-29.

⛔ A fix for 2 and 3 that stops at the token leaves 1 open, and 1 is the only one this ledger has
actually RECORDED a duplicate for. A fix for 1 alone leaves 2 and 3 open, because `_ISSUED` dies
with the process and two processes share nothing.

⛔⛔ THE PRICE, PAID DELIBERATELY AND STATED AT FULL STRENGTH: `next_entry_id` IS NO LONGER A
FUNCTION OF ITS ARGUMENTS. It is an ALLOCATOR — every call is a new name, and calling it twice
"to check" a row's id returns a DIFFERENT id rather than the one you wrote down. Requirement 1 and
re-derivability are the same property with opposite signs, and the allocator cannot tell "re-derive
the row I already named" from "name a second row" because the two calls are byte-identical. So the
tie is broken by what the record has actually cost: three duplicated ids on this ledger, against
zero recorded need for re-derivation and no caller on the trunk that does it (the three other
mentions of `next_entry_id` are hint strings in `priority.py`, `push_guard.py` and
`prepush_ledger_guard.py`). ⭐ MINT ONCE PER ROW AND WRITE THE RESULT DOWN.
⚠ The ANTI-CLOCK guarantee that in-process idempotence used to carry is not lost, only moved to
where it belongs: `allocator_discriminator()` IS stable across calls, and
`test_the_discriminator_is_the_session_and_the_process_and_not_the_moment` pins it there.
⚠ Ordinals may now have GAPS — a mint that is discarded still burns its name. That is harmless: an
ordinal was never a count of anything, and two concurrent sessions have shared one since AUT-PD-171.

⚠ WHAT THIS DELIBERATELY DOES NOT DO: renumber history. Receipts already on the trunk keep their
bare `CYC-NNNN` ids — a receipt is immutable committed history, `receipt_schema.cycle_number()`
parses both shapes, and rewriting them to look collision-proof would be a fiction about what the
record actually was.
"""

from __future__ import annotations

import hashlib
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
#: ⭐ THE SECOND SEGMENT IS OPTIONAL AND THAT IS WHAT KEEPS COMMITTED HISTORY READABLE (AUT-085).
#: Five discriminated ids were on the ledger when the process half was added -- `AUT-PD-204-d7df5340`
#: and `AUT-08{2,3,4,5}-e71cf460` -- and all five still parse to exactly the tuple they parsed to
#: before. ⛔ A schema change that orphans a committed id is a worse bug than the collision it fixes.
ENTRY_ID = re.compile(
    r"^(?P<prefix>[A-Za-z][A-Za-z-]*?)-?(?P<ordinal>\d+)"
    r"(?:-(?P<discriminator>[0-9a-z]{4,16}(?:-[0-9a-z]{4,16})?))?$")


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


def process_identity() -> tuple[int, str, str]:
    """The OS's answer to *which process is this* — `(pid, start ticks, boot id)`.

    ⛔ ONLY THE PID IS LOAD-BEARING, AND THE OTHER TWO ARE ANTI-REUSE RATHER THAN ANTI-CONCURRENCY.
    The kernel guarantees exactly one thing, and it is exactly the thing this module needs: no two
    processes ALIVE AT ONCE in a pid namespace share a pid. Two seats of a fan-out minting against
    one committed ledger are two live processes, so the pid separates them by construction — the
    same standard the session half meets, an identity a process already holds and never has to
    negotiate for.

    ⚠ THE PID IS REUSED OVER TIME AND THE PRESSURE HERE IS MEASURED, NOT ASSUMED. `pid_max` in this
    container is **32 768**, not the 4 194 304 of a modern host, and this session went from pid 498
    at 23:25 to pid 11 020 at 08:19 — ~1 180 pids/hour, so a wraparound is ~28 h of one session's
    activity away. ⭐ The start time (`/proc/<pid>/stat` field 22, ticks since boot) makes a reused
    pid a different identity, and the boot id makes a reused (pid, start) pair a different identity
    across a restart — after a reboot the tick counter restarts too, so the pair alone CAN repeat.
    ⚠ Stated at its true weight: this is the marginal half of the fix. Two mints 28 h apart in one
    session would almost certainly hold different ORDINALS anyway, because the ledger moves. It is
    here because it costs nothing, not because it is what the item measured.

    ⛔ THE START TIME IS A TIE-BREAKER AND IS NEVER THE SOURCE OF UNIQUENESS — that distinction is
    the whole of why this does not re-introduce what `discriminator()` refuses. A clock as a SOURCE
    collides when two allocators start in the same tick, and it also makes two calls describing ONE
    row return two names; here the pid already separates every concurrent allocator, and the start
    time only distinguishes processes the kernel has already guaranteed are NOT concurrent. It is
    read once per process and never advances, which is what
    `test_the_process_half_is_the_process_and_not_the_moment` pins.

    ⚠ BOTH `/proc` READS ARE BEST-EFFORT AND THE EMPTY STRING IS NOT A DEGRADED DISCRIMINATOR. If
    `/proc` is unreadable the identity is `(pid, "", "")`, which still separates every concurrent
    allocator — the guarantee is not weakened, only the anti-reuse margin. There is no branch on
    which this returns an identity WITHOUT a pid, and `process_discriminator` refuses one anyway.
    """
    pid = os.getpid()
    try:
        with open(f"/proc/{pid}/stat", encoding="utf-8") as fh:
            stat = fh.read()
        # ⚠ SPLIT AFTER THE LAST `)`, NEVER ON WHITESPACE: field 2 is the executable name in
        # parentheses and may itself contain spaces and parens. After `) ` the fields resume at
        # field 3, so field 22 (starttime) is index 19.
        start = stat[stat.rindex(")") + 2:].split()[19]
    except (OSError, ValueError, IndexError):
        start = ""
    try:
        with open("/proc/sys/kernel/random/boot_id", encoding="utf-8") as fh:
            boot = fh.read().strip()
    except OSError:
        boot = ""
    return pid, start, boot


def process_discriminator(identity: tuple[int, str, str] | None = None) -> str:
    """The allocator's contribution to an id two seats of ONE session must not have to negotiate.

    ⛔ NOT A CLOCK AND NOT A COUNTER, for the reasons `discriminator()` gives, and ⛔ NOT
    `CLAUDE_CODE_CHILD_SESSION`: the value observed on 2026-09-02 is the literal `1`. It is a flag,
    so it separates a child from its parent and never a child from its sibling — building on it
    would look like a fix and leave a five-wide fan-out sharing one discriminator.

    ⛔ AN IDENTITY WITHOUT A PID IS REFUSED RATHER THAN HASHED. This guard is REACHABLE — a caller
    passing an override is the path — which is the bar the first draft of `write_receipt` failed:
    a guard nobody can trigger measures nothing, and its test fails with DID NOT RAISE.
    """
    ident = process_identity() if identity is None else tuple(identity)
    pid = ident[0] if ident else None
    if isinstance(pid, bool) or not isinstance(pid, int) or pid <= 0:
        raise ValueError(
            f"cannot discriminate an allocator: the process identity {ident!r} has no usable pid. "
            "⛔ Do NOT fall back to a clock, a counter or an empty string here: the pid is the only "
            "component the kernel guarantees is unique among concurrent allocators, and a "
            "discriminator that silently drops it re-introduces AUT-085 while looking fixed.")
    payload = "\x00".join(str(part) for part in ident)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:DISCRIMINATOR_LEN]


def allocator_discriminator(session_id: str | None = None,
                            identity: tuple[int, str, str] | None = None) -> str:
    """`<session>-<process>` — the two questions a ledger id has to answer, kept separate.

    ⭐ THE SESSION HALF IS KEPT, NOT REPLACED, AND THAT WAS THE CHOICE (AUT-085). Replacing it with
    the process half alone would have been shorter and would have satisfied uniqueness, and it would
    have thrown away the only provenance the id carries: `e71cf460` is greppable back to a session,
    a process hash is greppable back to nothing. A reader asking *which session filed this* must not
    have to consult a second artifact to find out.

    ⚠ AND THE ORDER IS NOT COSMETIC. Session first means every id this session mints still begins
    `AUT-085-e71cf460`, so the committed rows and their successors sort and grep together; process
    first would have scattered one session's rows across the id space for no gain.
    """
    return f"{session_discriminator(session_id)}-{process_discriminator(identity)}"


#: ⛔⛔ EVERY NAME THIS PROCESS HAS HANDED OUT. The whole of the fix for failure mode 1 above, and
#: it is deliberately keyed on the FULL id rather than on `(prefix, ordinal)`: the invariant is that
#: no NAME is issued twice, and two sessions minting in one process (which is what this module's own
#: tests do) legitimately share an ordinal — keying on the ordinal would push the second session off
#: 204 and break the "both survive saying so" property that is the point of the discriminator.
#: ⚠ Process-scoped by construction, which is the honest limit: it cannot see another process, which
#: is exactly why the discriminator exists and is not made redundant by this.
_ISSUED: set[str] = set()


def forget_issued_ids() -> None:
    """⛔ TESTS ONLY. Clearing this re-opens AUT-086 for anything that mints afterwards.

    It exists because pytest runs many independent scenarios in ONE process, so without a reset each
    test would inherit the previous test's ordinals — and a test that has to reason about what an
    earlier test minted is a test nobody can read. ⛔ There is no legitimate call site in a cycle:
    a cycle that "forgets" a name it already wrote into a row is the defect, not the workaround.
    """
    _ISSUED.clear()


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

    ⛔⛔ AND THE DISCRIMINATOR IS THE ALLOCATOR, NOT THE SESSION (AUT-085, 2026-09-02). The session
    half alone was a CONSTANT across every seat of a fan-out — a subagent inherits
    `CLAUDE_CODE_SESSION_ID` verbatim — so among the seats that actually file rows here this
    function was still `max(committed) + 1`. Reproduced before it was changed: two concurrent
    subprocesses, one committed ledger, one session id, both handed `AUT-PD-205-e71cf460`. See
    `allocator_discriminator`.

    ⛔ THE ORDINAL COUNTS DISCRIMINATED IDS TOO, and this is the one-of-a-pair defect this fix could
    trivially have shipped: widening the mint without widening the scan freezes the ordinal at the
    last bare id forever, so every later session — INCLUDING THIS ONE, on its second row — reuses
    it. `test_ids_cannot_collide` pins both halves.
    """
    disc = allocator_discriminator(session_id)
    used = []
    for e in entries or []:
        parsed = parse_entry_id(str(e.get("id", "")))
        if parsed and parsed[0] == prefix:
            used.append(parsed[1])
    width = 3
    n = max(used, default=0) + 1
    # ⛔⛔ FAILURE MODE 1 (AUT-086): `used` comes from a list the caller has not appended to yet, so
    # without this loop the second mint in one comprehension re-derives the first one's answer. The
    # loop advances past names THIS PROCESS has already issued — never past names it merely read,
    # which `used` already covers.
    # ⚠ It terminates: `n` only increases and `_ISSUED` is finite.
    candidate = f"{prefix}-{n:0{width}d}-{disc}"
    while candidate in _ISSUED:
        n += 1
        candidate = f"{prefix}-{n:0{width}d}-{disc}"
    _ISSUED.add(candidate)
    return candidate


def duplicate_ids(entries: list[dict]) -> dict[str, int]:
    """`{id: count}` for every id used more than once. Empty is the only acceptable answer.

    ⛔ THE ASSERTION THAT WOULD HAVE CAUGHT ALL THREE INSTANCES AT THE COMMIT THAT CREATED THEM, and
    it is four lines. `AUT-PD-012` sat duplicated on origin/main because a duplicate id is invisible
    until a human or a rebase trips over it: nothing reads a ledger looking for one.
    """
    counts = Counter(str(e.get("id")) for e in entries or [] if e.get("id"))
    return {k: v for k, v in counts.items() if v > 1}
