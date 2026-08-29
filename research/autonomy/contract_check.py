#!/usr/bin/env python3
"""MEASURES THE AGREEMENT BETWEEN THE CYCLE CONTRACT AND THE GATE THAT ENFORCES IT.

⛔⛔ WHY THIS FILE EXISTS (AUT-PD-146, 2026-08-29). `receipt_schema.py` fails the commit of any
receipt from `FIRST_CCR_GOVERNED_CYCLE` onward that does not carry `ccr_session_id`. The cycle
contract -- `.claude/skills/research-loop/SKILL.md` §2 step 10, the text a cycle actually follows
when it hand-authors the receipt -- **never named that field**. A cycle that followed the contract
exactly wrote a receipt that failed the gate, and learned the requirement only from a red build.
CYC-0073-d4ccfde4 hit precisely this and wrote the field only because it had opened
`receipt_schema.py` for an unrelated reason. That is compliance by luck.

⭐ AND THE FIX COULD NOT BE THE SENTENCE ALONE. This repository has now lost the same
agreement-in-prose four separate times, each time between a writer and a reader of the same field:

    AUT-PD-013    `subagents.max_concurrent`  three spellings in seventeen receipts
    AUT-PROP-013  the receipt id itself       two sessions took CYC-0016 fifty seconds apart
    AUT-PD-037    the ledger serialization    two writers, two shapes
    AUT-PD-146    `ccr_session_id`            required by the gate, absent from the contract

The lesson recorded every time is the same, and `receipt_schema.py`'s own docstring states it:
**a field name agreed in prose between two files is a hope, not a mechanism.** So the remedy for
the fourth instance is not a fourth sentence. It is this module, which DERIVES what the enforcer
requires and checks the contract names all of it -- and fails the build when it does not.

★★ HOW THE REQUIRED SET IS DERIVED, AND WHY IT IS NOT A LIST. A hand-kept list of required fields
would be the same defect one file over: prose agreeing with prose. Instead:

  DIRECTION A -- BEHAVIOURAL, and it is the one that fails closed. `_fixtures()` holds receipts the
  enforcer currently ACCEPTS, spanning every condition `problems()` branches on. Each field is then
  deleted in turn and the enforcer re-run: a deletion that produces a complaint proves that field
  is REQUIRED. Nothing is asserted about the enforcer's internals.
  ⭐ THE FAIL-CLOSED PROPERTY IS THE FIXTURES THEMSELVES. If `receipt_schema.py` grows a NEW
  requirement, the fixtures stop being accepted and this check goes red immediately -- before the
  requirement can reach a cycle. Whoever adds the requirement must add it to a fixture, and the
  moment they do, direction A demands the contract name it. The gap this file closes cannot reopen
  without a red build.

  DIRECTION B -- THE CONSTANTS, as a backstop for a requirement conditioned on something no fixture
  happens to exercise. Every module-level `*_KEY` in `receipt_schema.py` names a receipt field, so
  every one must appear in step 10. ⚠ This assumes key names live in constants rather than in
  string literals -- which is `receipt_schema.py`'s own stated convention ("THE NAME, ONCE") and
  was, until this file landed, checked by nothing. `no_literal_key_lookups()` now checks it, so
  direction B is complete rather than merely likely.

⛔ WHAT THIS DOES **NOT** CHECK, SAID OUT LOUD RATHER THAN LEFT TO BE DISCOVERED.
 1. It covers the enforcer that FAILS THE COMMIT (`receipt_schema.py`) and no other reader.
    `health.py` reads `handoff.child_session_id` and `session_id`, `session_cap.py` reads
    `session_id`, `holder_liveness.py` reads `ccr_session_id` -- all named in the contract today,
    none checked here. A reader that merely grades a receipt cannot break a commit, so the same
    drift there is a wrong number rather than a red build; extending this module to them is a
    separate item, not something to absorb silently into this one.
 2. It checks that the contract NAMES each required field. It cannot check that what the contract
    says ABOUT the field is true or useful -- that "read it from `get_session`" still works, that
    the two id spaces are still distinct. Prose is not measurable; the name is.
 3. `cycle_id` is not in the derived required set, and that is correct rather than an oversight:
    `problems()` falls back to the receipt's FILENAME when the key is absent, so deleting it
    changes nothing. Direction B still demands it be documented, because the module reads it.

USAGE
    python3 research/autonomy/contract_check.py            # report
    python3 research/autonomy/contract_check.py --check    # exit 1 on any disagreement

EXIT CODES
    0  the contract names every field the gate requires
    1  a disagreement, or the contract could not be read at all (FAIL CLOSED -- see `step_text`)
"""

from __future__ import annotations

import argparse
import ast
import copy
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)

import receipt_schema as S  # noqa: E402

#: The cycle contract. ⛔ One path, here, because every other file that mentions it is prose.
CONTRACT = os.path.join(REPO, ".claude", "skills", "research-loop", "SKILL.md")

#: ⛔ THE ANCHOR IS THE STEP'S TITLE, NOT ITS NUMBER. Anchoring on `10.` would break silently the
#: first time a step is inserted above it -- the extractor would quietly return the WRONG step and
#: this whole check would pass against text that says nothing about receipts. The title is what the
#: step is; the number is where it currently sits.
STEP_ANCHOR = "Write the receipt"

#: A new top-level numbered item ends the step. Sub-bullets are indented and continuation lines are
#: indented, so an unindented `N.` is the only thing that closes it.
_ITEM = re.compile(r"^(\d+)\.\s")

#: Below this the extraction is not believable and something has moved. Step 10 is ~2 kB today; a
#: hundred characters would mean the anchor matched a mention rather than the step.
_MIN_STEP_CHARS = 400


class ContractUnreadable(Exception):
    """The contract could not be located or parsed.

    ⛔ RAISED, NEVER SWALLOWED. A checker that cannot read the thing it checks must go RED, not
    green: a vacuous pass is exactly how `subagent_width` governed nothing for a fortnight.
    """


def step_text(path: str = CONTRACT) -> str:
    """§2's receipt step, verbatim, or `ContractUnreadable`."""
    try:
        with open(path, encoding="utf-8") as fh:
            lines = fh.read().split("\n")
    except OSError as exc:
        raise ContractUnreadable(f"cannot open the cycle contract at {path}: {exc}") from exc

    start = None
    for i, line in enumerate(lines):
        if _ITEM.match(line) and STEP_ANCHOR in line:
            start = i
            break
    if start is None:
        raise ContractUnreadable(
            f"no numbered step in {os.path.relpath(path, REPO)} whose title contains "
            f"{STEP_ANCHOR!r}. The receipt step has been renamed or removed; this checker cannot "
            "tell which text a cycle is supposed to follow, so it refuses rather than passes.")

    end = len(lines)
    for j in range(start + 1, len(lines)):
        if _ITEM.match(lines[j]):
            end = j
            break
    body = "\n".join(lines[start:end])
    if len(body) < _MIN_STEP_CHARS:
        raise ContractUnreadable(
            f"the {STEP_ANCHOR!r} step extracted to only {len(body)} characters (< "
            f"{_MIN_STEP_CHARS}). The anchor probably matched a passing mention rather than the "
            "step itself; refusing rather than checking against near-empty text.")
    return body


def names(text: str) -> set[str]:
    """Every identifier-shaped token the step spells, so membership is a set lookup."""
    return set(re.findall(r"[A-Za-z_][A-Za-z0-9_]*", text))


# --------------------------------------------------------------------------------------------
# DIRECTION A — what the enforcer actually refuses, measured by deleting fields from receipts it
# accepts. No knowledge of `problems()`'s internals is used or needed.
# --------------------------------------------------------------------------------------------

def _fixtures() -> list[tuple[str, dict]]:
    """(receipt path, receipt) pairs the enforcer must accept, spanning its branches.

    ⛔ EVERY BRANCH `problems()` TAKES NEEDS A FIXTURE, or a requirement gated on that branch is
    invisible to direction A. Today it branches on the cycle number (the CCR cutoff) and on the
    recorded width; both sides of both are covered here. ⚠ A future branch on something else is
    caught by direction B if its key is a constant, and by nothing if it is not -- which is why
    `no_literal_key_lookups` exists.
    """
    def receipt(n: int, width: int) -> tuple[str, dict]:
        rid = f"CYC-{n:04d}-contract"
        return (f"{rid}.json", {
            S.CYCLE_ID_KEY: rid,
            S.ROUTE_ADVANCED_KEY: "none",
            S.CCR_ID_KEY: "session_01ContractCheckFixture",
            S.BLOCK_KEY: {S.WIDTH_KEY: width},
        })

    return [
        receipt(S.FIRST_GOVERNED_CYCLE, 0),            # governed, below the CCR cutoff
        receipt(S.FIRST_CCR_GOVERNED_CYCLE, 0),        # the first CCR-governed cycle, no fan-out
        receipt(S.FIRST_CCR_GOVERNED_CYCLE + 5, 3),    # CCR-governed, with a fan-out recorded
    ]


def fixtures_still_comply() -> list[str]:
    """Empty unless the enforcer has grown a requirement no fixture satisfies.

    ⭐ THIS IS THE FAIL-CLOSED HALF, and it is the reason the derived set cannot silently go stale:
    a new required field makes every fixture non-compliant, so the build goes red on the commit
    that adds the requirement rather than on the cycle that later trips over it.
    """
    out = []
    for path, r in _fixtures():
        for problem in S.problems(copy.deepcopy(r), path):
            out.append(
                f"the contract-check fixture {path} is no longer accepted by receipt_schema: "
                f"{problem} ⭐ Add the new field to `_fixtures()` -- then this checker will require "
                "the cycle contract to name it, which is the whole point.")
    return out


def _paths(obj: dict, prefix: tuple[str, ...] = ()) -> list[tuple[str, ...]]:
    out = []
    for k, v in obj.items():
        out.append(prefix + (k,))
        if isinstance(v, dict):
            out.extend(_paths(v, prefix + (k,)))
    return out


def _without(obj: dict, path: tuple[str, ...]) -> dict:
    out = copy.deepcopy(obj)
    cur = out
    for k in path[:-1]:
        cur = cur[k]
    cur.pop(path[-1], None)
    return out


def required_paths() -> list[tuple[str, ...]]:
    """Every field path whose REMOVAL makes the enforcer complain — i.e. what it truly requires."""
    found: list[tuple[str, ...]] = []
    for rpath, r in _fixtures():
        for fpath in _paths(r):
            if S.problems(_without(r, fpath), rpath):
                if fpath not in found:
                    found.append(fpath)
    return found


# --------------------------------------------------------------------------------------------
# DIRECTION B — the constants, plus the property that makes them exhaustive.
# --------------------------------------------------------------------------------------------

def key_constants() -> dict[str, str]:
    """`{constant name: field name}` for every module-level `*_KEY` string in the enforcer."""
    return {n: v for n, v in vars(S).items()
            if n.endswith("_KEY") and isinstance(v, str) and v}


def _reads_a_literal_key(node: ast.AST, params: set[str]) -> tuple[str, str] | None:
    """`(how, key)` when this node pulls a string-literal key out of one of `params`.

    ⛔ THE RECEIVER MUST BE A FUNCTION PARAMETER, AND THAT IS NOT AN EXEMPTION LIST — IT IS WHERE
    RECEIPTS COME FROM. A receipt enters this module only as an argument (`problems(receipt, path)`),
    while every internal dict is built locally. So a parameter receiver is the shape that reads a
    receipt field, and a local receiver is the shape that reads the module's own structures.
    ⚠ THE FIRST VERSION OF THIS RULE FLAGGED EVERY LOWER-CASE NAME AND PRODUCED NINE FALSE
    POSITIVES ON `audit`'s own result dict (`r["failures"]`, `r["unparsed"]`, …). A linter that
    flags true statements gets turned off, which is worse than no linter (`lint_claims.py`'s
    founding lesson), so it was tightened rather than shipped.
    ⛔ WHAT IT MISSES, SAID OUT LOUD: a receipt rebound to a local (`d = receipt`) and then read as
    `d["field"]` is invisible here. Direction A still catches such a field if omitting it changes a
    verdict; nothing catches it otherwise, and that is the honest edge of this check.
    """
    if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
            and node.func.attr == "get" and node.args
            and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str)):
        recv, key, how = node.func.value, node.args[0].value, ".get()"
    elif (isinstance(node, ast.Subscript) and isinstance(node.slice, ast.Constant)
            and isinstance(node.slice.value, str)):
        recv, key, how = node.value, node.slice.value, "[...]"
    else:
        return None
    if isinstance(recv, ast.Name) and recv.id in params:
        return how, key
    return None


def no_literal_key_lookups() -> list[str]:
    """Every field name the enforcer spells outside a `*_KEY` constant.

    ⛔ WHY THIS IS PART OF THE AGREEMENT CHECK AND NOT A STYLE RULE. Direction B enumerates the
    enforcer's field names from its `*_KEY` constants. That enumeration is complete only if no key
    name is spelled anywhere else, so a literal lookup is not untidy — it is a field this checker
    CANNOT SEE, which is precisely the class of defect the module exists to end.
    """
    src = open(S.__file__, encoding="utf-8").read()
    bad = []
    for fn in ast.walk(ast.parse(src)):
        if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        a = fn.args
        params = {p.arg for p in [*a.posonlyargs, *a.args, *a.kwonlyargs]}
        for node in ast.walk(fn):
            hit = _reads_a_literal_key(node, params)
            if hit:
                how, key = hit
                bad.append(
                    f"{os.path.basename(S.__file__)}:{node.lineno}: `{fn.name}` reads the field "
                    f"{key!r} off its own argument with `{how}` as a string literal, so "
                    "`contract_check` cannot enumerate it and the contract could drop the name "
                    "with nothing noticing. Bind it to a module-level `*_KEY` — the module's own "
                    "rule is THE NAME, ONCE.")
    return bad


# --------------------------------------------------------------------------------------------

def audit(contract: str = CONTRACT) -> dict:
    """Everything the two directions found, with the exact edit named for each failure."""
    failures: list[str] = list(fixtures_still_comply()) + list(no_literal_key_lookups())
    try:
        text = step_text(contract)
    except ContractUnreadable as exc:
        return {"failures": failures + [str(exc)], "required": [], "constants": {},
                "step_chars": 0}

    spelled = names(text)
    required = required_paths()
    for path in required:
        missing = [c for c in path if c not in spelled]
        if missing:
            failures.append(
                f"receipt_schema REQUIRES `{'.'.join(path)}` — a receipt without it fails the "
                f"preflight gate and the commit — but §2 step {STEP_ANCHOR!r} never spells "
                f"{', '.join('`' + m + '`' for m in missing)}. A cycle following the contract "
                "exactly writes a receipt the gate refuses, and finds out from a red build.")

    consts = key_constants()
    for cname, field in sorted(consts.items()):
        if field not in spelled:
            failures.append(
                f"receipt_schema.{cname} names the receipt field `{field}`, which §2 step "
                f"{STEP_ANCHOR!r} never spells. Every field the enforcer reads must be in the text "
                "the cycle follows, whether or not a fixture happens to make it mandatory.")

    return {"failures": failures, "required": required, "constants": consts,
            "step_chars": len(text)}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true", help="exit 1 on any disagreement")
    ap.add_argument("--contract", default=CONTRACT)
    args = ap.parse_args(argv)

    r = audit(args.contract)
    for line in r["failures"]:
        print(f"   FAILED {line}")
    if r["required"]:
        print("   required by the gate, and named by the contract: "
              + ", ".join("`" + ".".join(p) + "`" for p in r["required"]))
    print(f"   {len(r['required'])} required field path(s), {len(r['constants'])} key constant(s), "
          f"{r['step_chars']} chars of contract read, {len(r['failures'])} disagreement(s)")
    return 1 if (args.check and r["failures"]) else 0


if __name__ == "__main__":
    sys.exit(main())
