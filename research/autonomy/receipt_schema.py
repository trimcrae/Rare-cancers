#!/usr/bin/env python3
"""THE ONE PLACE THAT NAMES WHAT A CYCLE RECEIPT MUST RECORD ABOUT ITS FAN-OUT.

⛔⛔ WHY THIS FILE EXISTS, AND WHY THE OBVIOUS FIX WAS THE WRONG ONE (AUT-PD-013, 2026-08-27).
`health.py`'s `fanout_is_governed` reads `subagents.max_concurrent` from every receipt. CYC-0017
measured, against the live checker rather than the docs, that the receipts in the checker's window did
not write that key -- so the one row guarding the dial the architecture calls *the most important*
reported DISPATCH-NOT-RECORDED for cycles whose receipts plainly recorded a fan-out. The row was not
merely unmeasured: it printed a FALSE ABSENCE, which is the failure mode CLAUDE.md §4 exists for.

⭐ AND THE MEASUREMENT OVER ALL 22 RECEIPTS SAYS SOMETHING WORSE THAN THE TICKET DID. The ticket read
it as a key nobody writes. It is not: **the convention existed, was abandoned, was re-invented, and
was abandoned again** --

  CYC-0006, 0008, 0010   `max_concurrent` + `total`      the reader's key, recorded correctly
  CYC-0011 .. 0016, 0019 `concurrent_max` + `dispatched` the same numbers, both keys renamed
  CYC-0017, 0018         `max_concurrent` / `dispatched` re-invented by the cycle that filed this
  CYC-0020, 0021, 0022   `launched` + `cap`              the width dropped entirely

Three schemas in seventeen receipts, and the drop at CYC-0020 came four cycles after the correct
spelling was in use. There is no receipt writer anywhere in this repository: step 10 of `research-loop`
says "write the receipt" and every cycle hand-authors the JSON. A field name agreed in PROSE between a
writer and a reader is not agreed at all -- it is a hope, checked by nothing, and prose could not even
hold a convention this loop had already got right twice. That is the ledger's own phrasing of the
general form; this module is the answer to the instance: **the reader imports the name from here, and
a preflight gate checks the writer against it**, so the two cannot drift apart again without a red
build.

⛔ THE SYNONYMS ARE NOT ALL RENAMES, AND TREATING THEM AS RENAMES WOULD HAVE BROKEN THE MEASUREMENT.
The tempting cheap fix -- teach the checker to accept every spelling -- silently changes the QUANTITY:

  `concurrent_max`  the same number under a different name. A rename, and safe to compare.
  `launched` /      the SERIAL TOTAL over the cycle. Six agents run one at a time under a cap of 5
  `dispatched`      looks like a violation; five launched in one message looks identical to five run
                    in sequence. autonomy-state.json's `_subagent_width_means` settles it in writing:
                    "THE UNIT IS MAXIMUM CONCURRENT SUBAGENTS", and the 107-agent incident (40
                    completed, 67 errored, the synthesis lost) was ONE fan-out of width 107, not 107
                    sequential agents. A checker fed `launched` would measure the wrong thing in both
                    directions.

So a receipt may record the serial total as well -- it is real information -- but it must record
`max_concurrent`, because that is the only number the cap governs.

⛔ THE PRE-SCHEMA RECEIPTS ARE GRANDFATHERED, DELIBERATELY, AND THE REASON IS ALREADY PAID FOR.
A receipt is immutable committed history. Failing the gate on CYC-0014's spelling would make it red
forever with no action in any future session able to clear it -- exactly the LATCHING failure that
wedged the autonomy loop the same morning (`health.py`'s RECEIPT_WINDOW comment: fifty consecutive
well-behaved sessions left both rows red, and "a row that can never go green teaches every reader to
skip it"). The cutoff is a NUMBER, not a hand-maintained exemption list, so it cannot rot; and the
pre-cutoff drift is REPORTED rather than hidden, because the ledger item was filed against a checker
that hid what it could not read.

⭐ AND WHAT THIS MODULE REQUIRES IS NOW CHECKED AGAINST WHAT THE CONTRACT ASKS FOR (AUT-PD-146,
2026-08-29). Owning the name for the reader and the checker fixed half the problem and created the
other half: `ccr_session_id` became a commit-failing requirement that `.claude/skills/research-loop`
§2 step 10 -- the text a cycle follows when it hand-authors the receipt -- never mentioned, so a
cycle obeying the contract exactly would write a receipt this file rejects. (Measured: every receipt
since the cutoff does carry it, so nothing went red; what was absent is the guarantee.)
`contract_check.py` closes
that direction: it DERIVES the required set by deleting fields from receipts `problems()` accepts,
and reds the build when the contract does not name one. ⛔ TWO CONSEQUENCES FOR ANYONE EDITING HERE:
a new required field must be added to `contract_check._fixtures()` (its absence there is itself a
red build, by design), and every field name must live in a module-level `*_KEY` constant -- a name
spelled in a string literal is one that checker cannot enumerate, and `no_literal_key_lookups()`
refuses it.
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RECEIPT_DIR = os.path.join(HERE, "receipts")

#: ⛔ THE NAME, ONCE. `health.py` imports this rather than spelling it, which is the whole fix:
#: the reader and the checker cannot disagree about a constant they share.
WIDTH_KEY = "max_concurrent"

#: The block the width lives in.
BLOCK_KEY = "subagents"

#: A CCR session id as the session list writes it. Matched, never compared whole -- a receipt may
#: legitimately wrap the id in prose, which `session_reaper._SESSION_ID` already accounts for.
_CCR_ID = re.compile(r"\bsession_[A-Za-z0-9]{6,}\b")

#: ⭐ FIRST CYCLE THIS SCHEMA GOVERNS. CYC-0022 is the newest receipt on the trunk as this lands, so
#: CYC-0023 -- the next cycle written under a schema that exists -- is the first that can comply.
#: ⛔ Do NOT lower this to "catch" history: see the latching argument in the module docstring.
FIRST_GOVERNED_CYCLE = 23

#: The receipt's own id. ⚠ NOT in the derived required set and that is correct: `problems()`
#: falls back to the FILENAME when the key is absent, so removing it changes no verdict. It is
#: a constant anyway because `contract_check.py` enumerates this module's field names from the
#: `*_KEY` constants, and a name spelled in a string literal is a field that checker cannot see.
CYCLE_ID_KEY = "cycle_id"

#: The field that lets `session_reaper.py` join a receipt to a row in the session list.
CCR_ID_KEY = "ccr_session_id"

#: ⛔⛔ THE ESCAPE VALVE FOR A SESSION WHOSE TOOL SURFACE HAS NO `get_session` AT ALL (AUT-PD-157,
#: 2026-08-29). AUT-PD-146 measured how to OBTAIN `ccr_session_id` (`get_session` with no args ->
#: `.ccr.id`) and assumed the tool is always reachable. It is not: a scheduled-Routine session's tool
#: surface is narrower than an interactive one's and can omit `get_session`/`create_session`
#: entirely -- verified here by `ToolSearch` for "get_session", "create_session" and "session info
#: ccr claude-code-remote" all returning no match, not merely by the field being absent from one
#: receipt. Requiring the id unconditionally would make FIRST_CCR_GOVERNED_CYCLE a wall no scheduled
#: cycle could ever pass again, which is the exact LATCHING failure `research-loop` §1 already names
#: for a health condition keyed to immutable history -- except here it would latch every future
#: commit rather than one board row. Mirrors `handoff.UNAVAILABLE_FIELD`: a call that could not be
#: REACHED is recorded as absent-and-named, distinct from `session_id` (unreadable env var) and from
#: a refusal (a call was made and answered). A receipt carrying a non-empty string here is treated as
#: compliant for this field -- the same trust boundary this architecture already accepts for
#: `handoff.mechanism_unavailable`, `blocked_evidence` and every other self-reported "I could not"
#: in the loop: verified by audit over receipts, not by cryptographic proof.
CCR_UNAVAILABLE_FIELD = "ccr_session_id_unavailable"

#: ⭐ FIRST CYCLE REQUIRED TO CARRY `ccr_session_id` (AUT-PD-129, 2026-08-28).
#: ⛔ WHY A SECOND ID FIELD RATHER THAN REUSING `session_id`: they are different id spaces and each
#: has a reader that needs its own. `session_id` must stay the harness `CLAUDE_CODE_SESSION_ID` --
#: research-loop §2 step 10 requires it read from the environment, and `health.py:c_cycles_are_sized`
#: and `session_cap.py` both key on it. The session LIST speaks CCR ids (`session_01...`), so
#: `session_reaper.py` needs that one. Measured on the trunk the day this landed: 58 of 69 committed
#: receipts name no CCR id at all, so the reaper could not show a single modern session had
#: delivered -- it archived nothing and reported delivered cycles as having died holding work.
#: ⛔ SET TWO ORDINALS AHEAD, DELIBERATELY, AND THIS IS NOT SLACK. Three loop sessions ran
#: concurrently on 2026-08-28. A cutoff at the very next ordinal would fail the preflight of a cycle
#: ALREADY IN FLIGHT that cannot have known this field exists -- breaking another session's commit
#: to enforce a field invented while it was working. Two ordinals is the observed concurrent width.
FIRST_CCR_GOVERNED_CYCLE = 70

#: Spellings measured in real receipts, each with what it actually meant. `same_quantity` decides
#: whether a value found here may be compared against `max_concurrent` (a rename) or must not be
#: (a different measurement wearing a similar name).
DRIFTED_KEYS = {
    "concurrent_max": {
        "same_quantity": True,
        "seen_in": ["CYC-0011", "CYC-0012", "CYC-0013", "CYC-0014", "CYC-0016", "CYC-0019"],
        "remedy": f"rename it to `{WIDTH_KEY}` -- same number, the name the checker reads",
    },
    "launched": {
        "same_quantity": False,
        "seen_in": ["CYC-0020", "CYC-0021", "CYC-0022"],
        "remedy": (f"keep it if you like, but ADD `{WIDTH_KEY}`: `launched` is the serial total over "
                   "the cycle and the cap governs concurrency"),
    },
    "dispatched": {
        "same_quantity": False,
        "seen_in": ["CYC-0011", "CYC-0012", "CYC-0013", "CYC-0014", "CYC-0016",
                    "CYC-0017", "CYC-0018", "CYC-0019"],
        "remedy": (f"keep it if you like, but ADD `{WIDTH_KEY}`: `dispatched` is the serial total over "
                   "the cycle and the cap governs concurrency"),
    },
}

#: ⛔ THE SECOND KEY THIS SCHEMA OWNS (AUT-PD-017, generalising AUT-PD-013's fix rather than
#: re-deriving it). `research-loop` §2 step 10 says every receipt records "the id of the live route
#: you moved, or the literal 'none'" but has only ever named the FIELD in prose — agreed between the
#: skill's own text and `health.py`'s `c_advancing_live_work`, CLAUDE.md §0's own honesty instrument.
#: ⚠ MEASURED, NOT ASSUMED: all 29 receipts on the trunk as this lands already spell it
#: `route_advanced` — the convention has never drifted the way `subagents.max_concurrent` did. But
#: "has not drifted yet" is not "cannot drift", and the failure mode is identical in shape: before
#: this fix, a receipt that misspelled the field would have made `c_advancing_live_work` report
#: ROUTE-ADVANCED-ABSENT with no hint the value was sitting right there under another name — the same
#: false-absence risk `WIDTH_KEY` already paid for once. `health.py` now imports this name rather than
#: spelling it, and a governed receipt missing it fails the same `--check` gate `WIDTH_KEY` does.
ROUTE_ADVANCED_KEY = "route_advanced"

_CYCLE_NUM = re.compile(r"CYC-(\d+)")


def cycle_number(receipt_id: str) -> int | None:
    """`CYC-0017` -> 17, `CYC-0000-BOOTSTRAP` -> 0, anything else -> None."""
    m = _CYCLE_NUM.search(receipt_id or "")
    return int(m.group(1)) if m else None


def width_of(receipt: dict) -> int | None:
    """The governed quantity, or None when the receipt does not record it.

    ⚠ DELIBERATELY REFUSES THE SYNONYMS. This is the reader's contract and it exists so that a
    receipt that recorded the wrong quantity reads as UNMEASURED rather than as a green number.
    """
    block = receipt.get(BLOCK_KEY)
    if not isinstance(block, dict):
        return None
    w = block.get(WIDTH_KEY)
    return w if isinstance(w, int) and not isinstance(w, bool) and w >= 0 else None


def route_advanced_of(receipt: dict) -> str | None:
    """The route this receipt claims to have moved, or None when unreadable.

    ⚠ Deliberately does not distinguish 'the literal none' from 'a route id' — that judgement
    belongs to `health.py`'s `c_advancing_live_work`, which already makes it (§2 step 10: absent is
    neither). This is only the shared read both sides now use, so a spelling drift shows up as the
    same value on both sides of a diff rather than a silent divergence.
    """
    v = receipt.get(ROUTE_ADVANCED_KEY)
    return v.strip() if isinstance(v, str) and v.strip() else None


def drift_in(receipt: dict) -> dict:
    """Which drifted spellings this receipt used, for a diagnostic that names the cause.

    ⛔ CLAUDE.md §4: a checker that reports "not recorded" when the value is right there, under
    another name, has produced a probably-X. This is the observation that discriminates.
    """
    block = receipt.get(BLOCK_KEY)
    if not isinstance(block, dict):
        return {}
    return {k: block[k] for k in DRIFTED_KEYS if k in block}


def problems(receipt: dict, path: str) -> list[str]:
    """Every way this receipt fails the schema, as sentences naming the exact edit.

    Empty list means it complies. A receipt below FIRST_GOVERNED_CYCLE is never handed here by
    `audit`; calling it directly on one is legitimate (that is how the drift report is built).
    """
    out = []
    rid = receipt.get(CYCLE_ID_KEY) or os.path.basename(path).removesuffix(".json")

    # ⛔ CHECKED FIRST AND UNCONDITIONALLY (AUT-PD-017). This must not be short-circuited by the
    # `subagents`-block early return just below -- a missing route_advanced and a missing subagents
    # block are two independent failures, and a receipt missing both must be told about both, not
    # whichever the code happened to check first.
    if route_advanced_of(receipt) is None:
        out.append(
            f"{rid}: no `{ROUTE_ADVANCED_KEY}` (or it is empty/not a string). Every receipt records "
            "the route it moved, or the literal 'none' (research-loop §2 step 10) -- an absent value "
            "reads as ROUTE-ADVANCED-ABSENT to health.py's `advancing_live_work`, the loop's own "
            "honesty instrument, and is graded `unmeasured` rather than a pass.")

    n = cycle_number(rid)
    if n is not None and n >= FIRST_CCR_GOVERNED_CYCLE:
        ccr = receipt.get(CCR_ID_KEY)
        unavailable = receipt.get(CCR_UNAVAILABLE_FIELD)
        if not (isinstance(ccr, str) and _CCR_ID.search(ccr)):
            if isinstance(unavailable, str) and unavailable.strip():
                pass  # AUT-PD-157: a named, non-empty reason the tool could not be reached at all.
            else:
                out.append(
                    f"{rid}: no `{CCR_ID_KEY}` naming a CCR session id (`session_...`), and no "
                    f"`{CCR_UNAVAILABLE_FIELD}` naming why the tool could not be reached. It is what "
                    "joins this receipt to a row in the session list, and without it "
                    "`session_reaper.py` cannot show this session's work reached the trunk -- so the "
                    "session is never archived and is reported as one that may have died holding "
                    "uncommitted work. ⛔ This is NOT a duplicate of `session_id`, which is the "
                    "harness UUID and must stay that.")

    block = receipt.get(BLOCK_KEY)
    if not isinstance(block, dict):
        out.append(
            f"{rid}: no `{BLOCK_KEY}` block. Every cycle must record its fan-out -- INCLUDING a "
            f"cycle that spawned nobody, which records `{{\"{WIDTH_KEY}\": 0}}`. ⛔ An absent record "
            "is not a record of restraint: if omission were green, the cheapest clean board would "
            "be to stop recording dispatches.")
        return out

    w = block.get(WIDTH_KEY)
    if w is None:
        found = drift_in(receipt)
        if found:
            for k, v in found.items():
                out.append(f"{rid}: `{BLOCK_KEY}.{k}` = {v!r} but no `{WIDTH_KEY}` -- "
                           f"{DRIFTED_KEYS[k]['remedy']}.")
        else:
            keys = ", ".join(sorted(block)) or "(empty)"
            out.append(f"{rid}: `{BLOCK_KEY}` block records {keys} but not `{WIDTH_KEY}`, which is "
                       "the only key the governed cap is checked against.")
    elif isinstance(w, bool) or not isinstance(w, int):
        out.append(f"{rid}: `{BLOCK_KEY}.{WIDTH_KEY}` = {w!r} is not an integer.")
    elif w < 0:
        out.append(f"{rid}: `{BLOCK_KEY}.{WIDTH_KEY}` = {w} is negative.")

    # ⛔ ONE FACT, ONE PLACE (CLAUDE.md §1), applied inside a single file. A receipt carrying the same
    # number twice under two names is a receipt that can contradict itself, and one of the two copies
    # is the one a future reader believes.
    if isinstance(w, int) and not isinstance(w, bool):
        for k, v in drift_in(receipt).items():
            if DRIFTED_KEYS[k]["same_quantity"] and v != w:
                out.append(f"{rid}: `{BLOCK_KEY}.{k}` = {v!r} contradicts `{WIDTH_KEY}` = {w!r}. "
                           f"They are the same quantity; drop `{k}`.")
    return out


def audit(receipt_dir: str = RECEIPT_DIR) -> dict:
    """Every receipt on disk, split into governed / pre-schema, with the failures named."""
    failures, pre_schema, governed, unparsed = [], [], [], []
    for path in sorted(glob.glob(os.path.join(receipt_dir, "*.json"))):
        try:
            with open(path, encoding="utf-8") as fh:
                receipt = json.load(fh)
        except (OSError, ValueError) as exc:
            # ⚠ NOT SKIPPED SILENTLY. A receipt nobody can parse is a cycle nobody can grade, and a
            # loader that swallows it turns a broken record into a clean board.
            unparsed.append(f"{os.path.basename(path)}: unreadable -- {exc}")
            continue
        rid = receipt.get(CYCLE_ID_KEY) or os.path.basename(path).removesuffix(".json")
        n = cycle_number(rid) if isinstance(rid, str) else None
        if n is None or n < FIRST_GOVERNED_CYCLE:
            drift = drift_in(receipt)
            if width_of(receipt) is None:
                pre_schema.append((rid, sorted(drift) or ["(no width recorded)"]))
            continue
        governed.append(rid)
        failures.extend(problems(receipt, path))
    return {"failures": failures, "unparsed": unparsed,
            "pre_schema": pre_schema, "governed": governed}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true",
                    help="exit 1 if any governed receipt fails the schema")
    ap.add_argument("--dir", default=RECEIPT_DIR)
    args = ap.parse_args(argv)

    r = audit(args.dir)
    for line in r["unparsed"]:
        print(f"   UNREADABLE {line}")
    for line in r["failures"]:
        print(f"   FAILED {line}")

    if r["pre_schema"]:
        # ⭐ REPORTED, NEVER FAILED, AND NEVER SILENT. These fan-outs are permanently invisible to
        # `fanout_is_governed` and that is a fact about the record, not a fault to fix -- but the
        # ledger item was filed against a checker that hid what it could not read, so hiding it here
        # would rebuild the defect one file over.
        shown = ", ".join(f"{rid} ({'/'.join(keys)})" for rid, keys in r["pre_schema"])
        print(f"   pre-schema (< CYC-{FIRST_GOVERNED_CYCLE:04d}), width not readable by the cap "
              f"check, grandfathered: {shown}")
    print(f"   {len(r['governed'])} governed receipt(s), "
          f"{len(r['failures'])} failure(s), {len(r['unparsed'])} unreadable")
    return 1 if (args.check and (r["failures"] or r["unparsed"])) else 0


if __name__ == "__main__":
    sys.exit(main())
