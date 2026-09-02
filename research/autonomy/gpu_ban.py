#!/usr/bin/env python3
"""⛔⛔ THE NO-GPU BAN, ENFORCED — one gate, read by every path in this repository that can start a
billable GPU.

trimcrae, 2026-09-02, verbatim: **"You shouldn't be doing any GPU runs as part of this automation."**

★★ WHY A MODULE AND NOT A FIELD. The instruction was recorded the same hour in
`autonomy-state.json → gpu_spend_prohibited`, and that file says of itself: *"RECORDED IS NOT ENFORCED,
AND THIS REPOSITORY HAS ALREADY PAID FOR THAT GAP TWICE — `subagent_width` was a governed number that
`grep` proved no code read, and `max_versions_per_paper` was measured on this same day to be enforced by
nothing while a paper carried 11 versions against a cap of 3."* This module is the enforcement half. The
field stays the ONE HOME of the decision (CLAUDE.md rule 1); nothing here restates its reasons, its date
or its scope — every message this module prints is quoted out of the record it just read.

★★ IT IS A CATEGORY BAN, NOT A BUDGET, AND THE ORDERING IS THE WHOLE POINT.
CLAUDE.md §2 makes spend ≲$50 self-doable and §3 sets the review trigger at >$50, so a $25.45 ABFE
replicate set reads as authorised **on dollars** and was about to be bought by a cycle reasoning from the
ceiling alone. The money gates — the `$/ns` buy line, a rung's dollar band, a free-credit lane — answer
*"is this rate acceptable?"*. He answered a prior question with *"no GPU at all"*. So:

    ⛔ THIS GATE IS ASKED FIRST, AND A `CLEARS` FROM ANY MONEY GATE IS NOT AN ANSWER TO IT.
       A cycle that reaches a CLEARS verdict on the market gate has learned nothing about whether it
       may buy. `relaunch_market_gate.gate` therefore calls `refusal(...)` BEFORE it consults its own
       EXEMPTIONS, before it reads the board, and before it prices anything — see the comment there.

★★ FAIL CLOSED, EVERY WAY THE READ CAN GO WRONG. CLAUDE.md §4: *"AN ABSENT READING IS NOT A READING OF
ABSENCE."* A missing state file, an unparseable one, a missing `gpu_spend_prohibited` block, a missing or
non-boolean `active` — every one of them REFUSES and says which. `active: false`, an actual boolean read
out of an actual file, is the ONLY thing that permits a GPU rental. Doubt never resolves to spend, which
is the same discipline `gpu_backend.vast_rental_hold` already applies to the Vast stand-down file.

=================================================================================================
★ WHAT IT COVERS — the census of GPU-billing paths taken 2026-09-02 before this module was written,
  because a gate that guards only the paths somebody remembered is not a gate. ⛔ A RELAUNCH IS A NEW
  PURCHASE (CLAUDE.md §6), so resume and watchdog-relaunch paths are inside every count below.
=================================================================================================
  A. VAST — 3 create-instance call sites (`PUT /asks/{id}/`: `gpu_backend.VastBackend.submit`, and
     `vast_bid_semantics_probe` twice), reached from 18 lane `.submit(...)` call sites across 12
     modules: nrv04 ×5, vast_watchdog ×2 (a relaunch path), selcal ×2, and one each in ternary,
     congeneric fan-out, protfep, bioemu, paralogue-MD launch, paralogue-MD ops, abfe-sel, bench
     sweep and vast_smoke. ⚠ Counted, not remembered — `ternary_vast_watchdog` reaches `submit`
     through the ternary lane rather than directly and is therefore NOT one of the 12.
     → GATED AT `gpu_backend._vast_request`, on a mutating method against `/asks/`. That is the
       single door: every Vast HTTP call in the repository goes through that function, and creation
       is the only thing that PUTs to `/asks/`. Board reads (`GET /search/asks/`), `destroy`, `stop`,
       `collect` and every reap path are untouched — see "WHAT IS NOT GATED" below.
  B. SAGEMAKER — 1 submit helper (`sagemaker_submit.submit_spot`) used by 21 lane modules.
     → GATED IN `submit_spot`, before the estimator is built.
  C. EVERY BACKEND ADAPTER — 7 real `Backend` subclasses in `gpu_backend` (SageMaker, Slurm, RunPod,
     Vast, Salad, GCP, Modal) plus any added later.
     → GATED IN `Backend.__init_subclass__`, which wraps each subclass's `submit` as it is defined.
       An eighth backend is covered on the day it is written, with no edit here — the failure mode
       `vast-RENTAL-HOLD.json` names ("wrong the moment a seventh lane is added"), removed.
  D. GCP GCE VMs — 6 workflows run `gcloud compute instances create` in YAML with no Python between
     the runner and the meter. E. MODAL — 5 workflows run `modal run`.
     → GATED BY THE CLI: `python3 research/autonomy/gpu_ban.py --context <lane>` exits non-zero,
       as a step before the create/run step.

⛔ WHAT IS NOT GATED, DELIBERATELY, AND WHY WEAKENING THIS WOULD BE THE EXPENSIVE MISTAKE.
   CREATION ONLY. Teardown, destroy, stop, reap, collect, board reads, price sampling, censuses and
   every $0 analysis path run untouched. `gpu_backend.vast_rental_hold` states the reason and it is
   this repository's most expensive recurring failure: *"a lane that is stood down must still tear
   down a host that somehow exists — otherwise 'stood down' quietly becomes 'billing unwatched'."*
   A ban that stopped the reapers would COST money rather than save it.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

#: The one home of the decision. Read, never restated.
STATE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "autonomy-state.json")

#: The block inside it that carries the instruction.
BAN_KEY = "gpu_spend_prohibited"


class GPUSpendProhibited(RuntimeError):
    """A GPU rental was attempted while `gpu_spend_prohibited` refuses it, or while it could not be read.

    ⚠ A DISTINCT TYPE, for the reason `gpu_backend.NoQualifyingOffer` is one: a refusal by standing
    instruction and a broken launcher must never produce the same signal. This one is neither a market
    verdict nor a fault — nothing is wrong, and nothing about the board, the price or the code would
    change the answer. It is deliberately NOT a subclass of `NoQualifyingOffer`: a lane that treats an
    unaffordable market as "quiet, try again next tick" must not quietly retry this forever.
    """


def _refusal(why: str, record=None, state_path=None) -> dict:
    return {"refuses": True, "why": why, "record": record, "state_path": state_path or STATE_PATH}


def read_ban(state_path: str | None = None) -> dict:
    """Read `gpu_spend_prohibited` and return `{refuses, why, record, state_path}`. FAILS CLOSED.

    Every failure to read is a refusal, and the `why` names which failure it was, so a future session
    debugging a refused launch is told whether the ban is active or the file is broken.
    """
    path = state_path or STATE_PATH
    if not os.path.exists(path):
        return _refusal(
            f"the autonomy state file is MISSING ({path}), so the standing no-GPU instruction could not be "
            f"read. An absent reading is not a reading of absence (CLAUDE.md §4) — REFUSING.", None, path)
    try:
        with open(path, encoding="utf-8") as fh:
            doc = json.load(fh)
    except Exception as e:  # noqa: BLE001
        return _refusal(
            f"the autonomy state file could not be parsed ({type(e).__name__}: {e}) — REFUSING, because an "
            f"unreadable instruction to stop is not permission to spend.", None, path)
    if not isinstance(doc, dict):
        return _refusal("the autonomy state file is not a JSON object — REFUSING.", None, path)
    if BAN_KEY not in doc:
        return _refusal(
            f"`{BAN_KEY}` is ABSENT from {os.path.basename(path)}. That block is how this automation records "
            f"whether it may spend on GPUs at all; with no block there is no permission to read, and a "
            f"deleted prohibition is indistinguishable from one that was never written — REFUSING.", None, path)
    rec = doc[BAN_KEY]
    if not isinstance(rec, dict):
        return _refusal(f"`{BAN_KEY}` is not an object — REFUSING.", None, path)
    if "active" not in rec:
        return _refusal(
            f"`{BAN_KEY}.active` is ABSENT — REFUSING. The field is the flag; a record with no flag says "
            f"nothing, and saying nothing is not saying yes.", rec, path)
    active = rec["active"]
    if not isinstance(active, bool):
        return _refusal(
            f"`{BAN_KEY}.active` is {type(active).__name__} ({active!r}), not a boolean — REFUSING rather "
            f"than coercing it. A truthiness rule would make `active: \"false\"` and `active: 0` mean "
            f"opposite things by accident.", rec, path)
    if active:
        # Quoted out of the record, never restated here (CLAUDE.md rule 1). The fallbacks exist only so a
        # truncated record still refuses with a usable message rather than a KeyError.
        said = rec.get("verbatim") or "(no verbatim recorded — read the record)"
        who = rec.get("set_by") or "trimcrae"
        scope = rec.get("scope") or "(see the record)"
        return {"refuses": True, "record": rec, "state_path": path,
                "why": f'\u26d4 NO GPU RUNS. {who}: "{said}" \u00b7 scope: {scope}'}
    return {"refuses": False, "record": rec, "state_path": path,
            "why": f"`{BAN_KEY}.active` is false — the standing no-GPU instruction has been lifted on record."}


def refusal(what: str, *, state_path: str | None = None) -> str | None:
    """The refusal message for `what`, or None if a GPU rental is permitted. NEVER RAISES.

    For callers that must return a verdict rather than throw — `relaunch_market_gate.gate` returns a
    `(hold, doc)` pair and a raise there would look like a launcher fault instead of a standing refusal.
    """
    r = read_ban(state_path)
    if not r["refuses"]:
        return None
    return (f"{r['why']}\n"
            f"   REFUSED: {what}\n"
            f"   This is a CATEGORY ban, not a budget: no price clears it, and a `CLEARS` verdict from the "
            f"$/ns buy line or a rung's dollar ceiling is not an answer to it.\n"
            f"   One home: {r['state_path']} → {BAN_KEY}. Only a person may lift it, by setting "
            f"`active: false` there.")


def assert_permitted(what: str, *, state_path: str | None = None) -> dict:
    """Raise `GPUSpendProhibited` unless a GPU rental is permitted. Returns the record when it is.

    `what` names the thing being bought — the lane, the backend, the endpoint — so the traceback says
    which path was refused rather than only that something was.
    """
    msg = refusal(what, state_path=state_path)
    if msg:
        raise GPUSpendProhibited(msg)
    return read_ban(state_path)["record"]


def main(argv=None) -> int:
    """CLI for the paths with no Python between the runner and the meter (GCP `gcloud`, Modal `modal run`).

    Exit 0 = permitted, 3 = refused. 3 rather than 1 so a refusal is never confused with an argparse
    error (2) or an interpreter crash (1) in a workflow log.
    """
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--context", required=True, help="what is about to be bought (lane / workflow / step)")
    p.add_argument("--state", default=None, help="path to autonomy-state.json (default: the committed one)")
    p.add_argument("--json", action="store_true")
    args = p.parse_args(argv)

    r = read_ban(args.state)
    if args.json:
        print(json.dumps({**r, "context": args.context}, indent=2))
    elif r["refuses"]:
        print(refusal(args.context, state_path=args.state), file=sys.stderr)
    else:
        print(f"✅ GPU spend permitted for {args.context}: {r['why']}")
    return 3 if r["refuses"] else 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
