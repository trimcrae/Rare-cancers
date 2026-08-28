#!/usr/bin/env python3
"""THREE-VALUED ENVIRONMENT READS — `sd_watchdog_enabled()`'s signature, ported.

⛔⛔ THE DEFECT THIS REPLACES, NAMED BY ITS CANONICAL ANSWER.
`research/method-watch-autonomy-prior-art-2.md` §2, sixth row: systemd's `sd_watchdog_enabled()`
returns **three** values — *"On failure… a negative errno-style error code. If the service manager
expects watchdog keep-alive notification messages to be sent, > 0 is returned, otherwise 0"* —
armed / not-armed / **error**. `os.environ.get(VAR, default)` returns **two**: a string, or the
default. It therefore collapses three different situations into one, and the one it collapses them
into is *"fine"*:

    UNSET                      -> the default. Correct, and the case the call was written for.
    SET, and readable          -> that value. Correct.
    SET TO SOMETHING UNUSABLE  -> ⛔ THAT UNUSABLE VALUE, NOT THE DEFAULT.

⛔ THE THIRD ROW IS THE WHOLE POINT AND IT SURPRISES EVERYONE: `os.environ.get("X", "d")` with
`X=""` exported returns `""`, **not** `"d"`. An empty export is not an absent variable to Python,
and it is not an absent variable to a shell either — `X= python3 …`, a `${MISSING}` that expanded to
nothing, a CI `env:` block whose secret was not available to a fork PR, all produce exactly this.
The caller then proceeds with an empty repo slug, an empty bucket or an `Authorization: Bearer `
header, and the failure surfaces far away as a 401, a 404 or an empty result set — which the callers
in this directory are specifically built to read as "no runs found", i.e. as a MEASUREMENT.

★★ THAT IS THIS REPOSITORY'S OWN NAMED FAILURE MODE, NOT A GENERIC ONE. CLAUDE.md §4: *an absent
reading is not a reading of absence, and a populated field is not a measured one — env-echoed
defaults once carried a fabricated verdict all the way out.* A two-valued env read is the mechanism
by which an env-echoed default becomes a verdict.

⭐ SO EVERY READ HERE RETURNS A STATUS, AND THE THIRD STATUS IS NEVER SILENTLY USABLE:

    "set"                  the variable was exported and passed its validator. Use `value`.
    "unset-using-default"  the variable was absent. `value` is the default. This is FINE and is
                           said out loud, because "we are running on the documented default" is a
                           reading, not an absence of one.
    "set-but-unreadable"   the variable was exported and its value cannot be used — empty,
                           whitespace, or rejected by the caller's validator. ⛔ `value` is None and
                           `usable` is False. THE CALLER MUST FAIL CLOSED. Falling back to the
                           default here is precisely the collapse: somebody deliberately set this
                           variable, we cannot honour what they set, and quietly doing something
                           else instead is how a job reads the wrong repository and reports a
                           verdict about it.

⛔ WHY NOT JUST RAISE. Because two of the three call sites are pollers and verdict-writers whose
whole contract is "exit 0, write nothing, leave the row `unmeasured`" (`gates_verdict.py`) or "exit
2 = UNKNOWN, which is not green" (`await_ci.py`). A traceback out of an argparse default is not that
contract; it is a red job in a workflow whose other steps must still run. The status is returned so
each caller can fail closed **in its own vocabulary**.

⛔ AND A SECRET IS NEVER ECHOED. `secret=True` keeps the value out of `detail` entirely — the detail
line reports only length and shape, because these details are printed into `$GITHUB_STEP_SUMMARY`.

USAGE
    r = envread.read("GITHUB_REPOSITORY", default="trimcrae/Rare-cancers", validate=envread.repo_slug)
    if not r.usable:
        print(r.detail); return 0          # fail closed, in this caller's vocabulary
    repo = r.value
"""

from __future__ import annotations

import os
import re
from typing import Callable, NamedTuple

#: The three statuses, spelled once. Callers compare against these names rather than string
#: literals, for the same reason `receipt_schema` owns `WIDTH_KEY`: a name agreed in prose between a
#: writer and a reader is not agreed at all (AUT-PD-013).
SET = "set"
DEFAULTED = "unset-using-default"
UNREADABLE = "set-but-unreadable"

STATUSES = (SET, DEFAULTED, UNREADABLE)


class EnvRead(NamedTuple):
    """One environment variable, read three ways.

    ⛔ `usable` is False for exactly one status. It is a property rather than a bare boolean field so
    that the two can never disagree — the `_row` assertion in `health.py` exists for the same reason.
    """

    name: str
    value: str | None
    status: str
    detail: str

    @property
    def usable(self) -> bool:
        return self.status != UNREADABLE

    @property
    def defaulted(self) -> bool:
        return self.status == DEFAULTED


# ══════════════════════════════════════════════════════════════════════════════════════ validators
# A validator answers "why is this unusable?" — None or "" means usable. Phrased that way round so a
# validator that forgets to return anything reads as PASS only when it genuinely fell through, and so
# the reason lands in `detail` for the human who has to fix the export.

def repo_slug(value: str) -> str | None:
    """`owner/name`, GitHub's own shape.

    ⚠ MEASURED IN THIS DIRECTORY, NOT HYPOTHETICAL. `await_ci.py`'s module docstring records that the
    Actions API matches `head_sha` exactly and *"a short sha silently returns zero runs"*, so the
    poller waited out its whole deadline and reported UNKNOWN — a fake stall manufactured by the
    poller itself. A malformed **repo** does the same thing one level up: the URL is well-formed, the
    request 404s or returns an empty list, and every downstream reader sees "no runs", which both
    callers here are built to treat as a reading.
    """
    if "/" not in value:
        return "it is not `owner/name` — a repo slug without a slash makes a URL that 404s"
    owner, _, name = value.partition("/")
    if not owner or not name or "/" in name:
        return "it is not `owner/name` — exactly one slash, with both halves non-empty"
    if not re.fullmatch(r"[A-Za-z0-9._-]+/[A-Za-z0-9._-]+", value):
        return "it carries characters GitHub does not allow in an owner or repository name"
    return None


def https_url(value: str) -> str | None:
    """An absolute `https://` origin. For anything that decides WHERE an outward request goes."""
    if not value.startswith("https://"):
        return "it is not an absolute https:// URL, and where a request goes is not a guess"
    if len(value) <= len("https://"):
        return "it is the scheme with no host"
    return None


def opaque_token(value: str) -> str | None:
    """A credential: any non-empty run of non-whitespace. Never inspected further, never echoed."""
    if any(ch.isspace() for ch in value):
        return "it contains whitespace, which no GitHub token does — this is a quoting accident"
    return None


# ═══════════════════════════════════════════════════════════════════════════════════════════ the read
def read(name: str,
         default: str | None = None,
         *,
         validate: Callable[[str], str | None] | None = None,
         secret: bool = False,
         what: str = "") -> EnvRead:
    """Read one variable three-valued. See the module docstring for the contract.

    ⛔ `os.environ.get(name)` is called WITHOUT a default on purpose — passing one here would rebuild
    the two-valued collapse inside the function meant to remove it. The default is applied only on
    the branch that proved the variable is absent.
    """
    raw = os.environ.get(name)
    subject = f" ({what})" if what else ""

    if raw is None:
        return EnvRead(name, default, DEFAULTED,
                       f"{name} is unset{subject}; using the documented default "
                       f"{'(none)' if default is None else default!r}. That is a reading, not an "
                       f"absence of one.")

    stripped = raw.strip()
    if not stripped:
        return EnvRead(name, None, UNREADABLE,
                       f"⛔ {name} is EXPORTED AND EMPTY{subject} ({len(raw)} character(s), all "
                       f"whitespace). `os.environ.get({name!r}, default)` would return that empty "
                       f"string rather than the default, so the default is NOT what a caller would "
                       f"get. Somebody set this variable; we cannot honour it. Unset it to use the "
                       f"default, or give it a value.")

    if validate is not None:
        why = validate(stripped)
        if why:
            shown = f"{len(stripped)} character(s)" if secret else repr(stripped)
            return EnvRead(name, None, UNREADABLE,
                           f"⛔ {name} is set{subject} to {shown} and it is unusable: {why}. Failing "
                           f"closed rather than substituting the default — an explicit setting we "
                           f"cannot honour is not the same as no setting at all.")

    shown = f"set ({len(stripped)} character(s))" if secret else repr(stripped)
    return EnvRead(name, stripped, SET, f"{name} is {shown}{subject} and passed its validator.")


def first_set(names, *, validate=None, secret: bool = False, what: str = "") -> EnvRead:
    """The first of several aliases that is exported — `GITHUB_TOKEN` or `GH_TOKEN`, the pattern both
    callers in this directory already use.

    ⛔ AND AN EXPORTED-BUT-UNREADABLE ALIAS STOPS THE SEARCH RATHER THAN BEING SKIPPED. `A or B` in
    Python skips an empty `A` and silently uses `B`; that is convenient and it is the wrong answer
    here, because "A is set to something broken" is a fact somebody needs to see. An alias that is
    merely UNSET is skipped, which is what an alias is for.
    """
    reads = [read(n, default=None, validate=validate, secret=secret, what=what) for n in names]
    for r in reads:
        if r.status == UNREADABLE:
            return r
        if r.status == SET:
            return r
    joined = " / ".join(names)
    return EnvRead(names[0], None, DEFAULTED,
                   f"none of {joined} is set{f' ({what})' if what else ''}; proceeding without one.")
