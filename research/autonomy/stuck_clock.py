#!/usr/bin/env python3
"""TWO CLOCKS ON EVERY OPEN LEDGER ROW — one says it was TOUCHED, one says it ADVANCED (AUT-PROP-029).

⛔⛔ THE FAILURE THIS EXISTS FOR IS A ROW THAT LOOKS MAXIMALLY ALIVE WHILE GOING NOWHERE. The loop
re-scores the ledger every cycle, a claim stamps `owner` and `claimed_utc`, a lease expiry bumps
`attempts` and flips `state` back to `queued`, and every one of those writes makes the row's last
modification time move. A row can be claimed, abandoned, re-queued, re-scored and re-claimed forever
and never once change what anybody knows about the work. Measured in this repository the same week:
a seat died on its first message and held AUT-PROP-012 for 2 h 36 m while `ListAgents` reported it
`running` (AUT-PD-034), and six finished seats left leases standing that read as "5 workers AT
CAPACITY" when one was running (2026-08-27). Both are the same shape — activity mistaken for progress.

★★ THE MECHANISM IS BORROWED FROM RUCIO, READ IN ITS OWN SOURCE ON 2026-08-28, NOT FROM MEMORY.
    `lib/rucio/db/sqla/models.py`  — `ModelBase` defines the touch clock for every table:
        mapped_column("updated_at", DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
      i.e. ANY write moves it. `ReplicationRule` then carries a SECOND, independent column,
        stuck_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
      which `onupdate` does not touch.
    `lib/rucio/core/rule.py` — `repair_rule` sets `rule.stuck_at = datetime.utcnow()` only `if
      rule.stuck_at is None`, and clears it (`rule.stuck_at = None`) only on SUCCESSFUL recovery. A
      mere retry leaves it alone. That single asymmetry is the whole idea: the retry loop cannot
      launder its own failure into freshness.
    Terminal state, same function: `if rule.stuck_at < (datetime.utcnow() - timedelta(days=14))` the
      rule is SUSPENDED — an explicit, dated state meaning automation has stopped trying.
  Fetched with WebFetch from raw.githubusercontent.com/rucio/rucio/master/... on 2026-08-28; the
  quoted lines are from that read. ⚠ UNVERIFIED, AND DELIBERATELY NOT USED AS EVIDENCE BELOW: the
  AUT-PROP-029 brief also reports PanDA declaring dead at 6x a beat interval and Rucio at 10x with a
  code comment saying the multiplier "was chosen without any particular reason". Neither number was
  found at the two Rucio locations read here, the survey that carries them
  (`research/method-watch-autonomy-prior-art-2.md`) is not present on any ref this worktree can see,
  and a remembered multiplier is exactly what CLAUDE.md §4 forbids carrying an argument. They are
  recorded as an anchor with a date on it, never as the reason for the constant.

⭐⭐ WHAT THIS PORT CHANGES, AND IT IS THE LOAD-BEARING CHANGE: RUCIO'S `stuck_at` IS A WRITABLE
COLUMN AND OURS IS NOT. Rucio can afford a field because one daemon owns every write to it. Here the
writer is a language model editing JSON, and the ledger already HAS a self-reported progress field —
`last_evidence_utc`, typed by whoever edits the row. CLAUDE.md §4: "a populated field is not a
measured one", "presence is never evidence of provenance". A second such field would be a stall
detector that a stalled session can clear by typing a date, which is not a detector. So both clocks
here are DERIVED FROM GIT — the commit history of `research-ledger.json` is the one record of this
row that no session can restate — and nothing in this module writes to the ledger at all.

★ WHY FULL VERSIONS AND NOT DIFF HUNKS. `git log -p` on this file yields hunks of an indented JSON
array; a changed line reads `"state": "queued",` with no way to say which of 145 entries it belongs
to without reconstructing the enclosing object anyway. So the history is walked as
`git log --follow` + `git show <sha>:<path>`, each version parsed, and rows compared by id. Same
source, exact attribution, no hunk arithmetic.

★★ THE SPLIT — WHICH FIELDS ARE PROGRESS AND WHICH ARE MERE TOUCHING. This is the decision the whole
module rests on, so it is argued rather than asserted.

  PROGRESS. `what` (the row's account of the work and its outcome), `blocked_by` and
  `blocked_evidence` (CLAUDE.md §0: "'Blocked' is a claim that needs evidence" — producing that
  evidence IS the advance, and `priority.py:apply_session_penalties` already treats the recorded
  observation as the block), `depends_on_evidence`, `outcome`, `observed`, `superseded_note`,
  `closes_clause`, `prerequisite_of` (a structural finding about what unblocks what),
  `requires_trimcrae`/`requires_trimcrae_why` (deciding an item is his, with a reason, is a finding
  and is nearly this module's own terminal state), and `serves.route` (re-pointing a row at a
  different route is a decision — and it is flagged as an identity change besides).

  TOUCHING. `score`, `score_inputs`, `_score_basis`, `score_clamped_from`, `clamp` — all re-derived
  from `systems/graph` on every `--write`, so they move on rows nobody looked at. `owner`,
  `claimed_utc` — a claim is a LEASE, not work; AUT-PD-034 is the measured case of a claim standing
  while nothing happened. `lease_released`/`_lease_released` — bookkeeping about a claim that
  expired. `kind`, `cost_class` — graph-derived. `last_evidence_utc` — the self-typed field this
  module exists to replace; letting it clear the clock would rebuild the thing being replaced.

  ⛔ AND `attempts` IS TOUCHING, WHICH CONTRADICTS THE BRIEF THAT COMMISSIONED THIS AND IS THE ONE
  PLACE IT SHOULD BE CONTRADICTED. AUT-PROP-029 lists `attempts` as a candidate for progress. It is
  the retry counter: `priority.py:release_stale_claims` increments it every time a lease expires,
  which is precisely the busy-retry-loop signal Rucio refuses to let reset `stuck_at` ("a mere retry
  leaves it alone", above). Counting a retry as an advance would make the detector report a row as
  healthy in exact proportion to how often the automation failed on it — the failure mode this module
  is built to catch, rebuilt inside the module. `attempts` is still read, but only to answer a
  different question: has anything ever TRIED this row (see `tried`)?

  ⛔ AND `state` IS PROGRESS ONLY ON ENTRY TO A RESOLUTION STATE (`PROGRESS_STATES`). `queued ->
  in_progress` is a claim under another name, and `in_progress -> queued` is a lease expiring; a row
  can oscillate between them all week. Entry to `done`, `abandoned`, `superseded` or `blocked` is a
  resolution, and `blocked` earns its place because the ranker's clamp turns an evidence-free
  `blocked` back into a queued fetch, so the state only survives with evidence attached.

  ⛔ AN UNRECOGNISED FIELD IS TOUCHING, NOT PROGRESS, AND IS REPORTED BY NAME. The two errors are not
  symmetric: an unknown field defaulting to PROGRESS silently clears the clock and hides a stall (the
  quiet direction), while defaulting to TOUCHING at worst names a row a human then looks at (the loud
  direction). `unclassified_fields` on every clock, and a line in `--check`, keep the drift visible —
  the schema here has already grown `_contested`, `_block_cleared` and `_lease_released` in one day.

★ THE THRESHOLD, AND WHAT IT IS RELATIVE TO. `STUCK_AFTER_CYCLES = 6` against the loop's own
`cycle_interval_hours` (4 h, read from `autonomy-state.json` via `priority.py`), so 24 h. Its
reasoning is beside the constant; in short, the two numbers this repository has already MEASURED
bracket it — the claim lease is 2 cycles, so anything at or below 8 h would call every expired lease
a stall, and `stall_alarm.REPEAT_EVERY_RUNS` is ~24 h, this loop's own settled period for "a genuine
outage nags but does not flood". The borrowed 6x-10x band is an anchor that agrees; it is not the
argument.

⛔⛔ THE HONEST LIMIT, AND IT BINDS TODAY: THIS CLONE IS SHALLOW. Measured 2026-08-28, `git rev-parse
--is-shallow-repository` returns true here, 206 commits, all of them dated 2026-08-27, and the oldest
one LOOKS like the commit that created the ledger only because it is the graft point. So for every
row already present in the oldest visible version, git can prove only `stuck_at <= horizon` — a
right-censored lower bound, not a measurement. Such a row is marked `censored` and it is NEVER
declared terminal while the horizon itself is younger than the threshold, because a bound below the
threshold decides nothing. Once the horizon is older than the threshold the bound becomes conclusive
and censored rows can be declared. An absent reading is not a reading of absence (CLAUDE.md §4);
this module says which rows it cannot yet measure instead of printing a young number for them.

⭐ THE REMEDY IS NOW RUN FOR YOU, AND IT IS NOT `git fetch --unshallow`. `scripts/dev-setup.sh` —
which the SessionStart hook already runs — deepens the clone before anything reads this module. ⚠ Its
window is NOT this module's threshold: three modules read the same history with different memories
(this one, `learning_rate.py`, `out_of_ideas.py`) and the deepen is sized off the LONGEST of them, so
do not infer the fetched depth from the number above. That script's comment block owns the window,
the guard and the measurement that chose `--shallow-since` over `--unshallow`, including the
three-way clone comparison behind it; none of it is restated here (CLAUDE.md §1). This module still
only REPORTS the limit and names that script — a measuring instrument does not write to the object
store it is measuring.

⚠ A DEEPENED CLONE IS STILL SHALLOW, AND THAT IS THE POINT RATHER THAN A GAP. `is_shallow()` stays
true and every row at the horizon stays flagged `censored`; what changes is that the horizon outruns
the threshold — exactly the condition named two paragraphs up as the one that makes a bound
conclusive. So do not read `shallow_clone: true` in the JSON as "this verdict is censored": read the
`censored` flag on the row and the horizon against the threshold, which is what `terminal()` does.

Usage:
    python3 research/autonomy/stuck_clock.py --check            # rows, longest-stuck first
    python3 research/autonomy/stuck_clock.py --check --json     # the same, machine-readable
    python3 research/autonomy/stuck_clock.py --check --fail-on-terminal   # exit 1 if any terminal
"""

from __future__ import annotations

import argparse
import datetime
import json
import os
import subprocess
import sys
from dataclasses import dataclass, field

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
LEDGER_PATH = os.path.join("research", "autonomy", "research-ledger.json")

# --------------------------------------------------------------------------------------------
# The split. One home for it: a reader and a writer must not be able to disagree about which
# fields mean progress, which is the AUT-PD-013 / AUT-PD-017 reader-writer mismatch family.
# --------------------------------------------------------------------------------------------

#: Fields whose change is a genuine advance in what is known about the work. Argued in the module
#: docstring; `state` is further restricted by PROGRESS_STATES below.
PROGRESS_FIELDS = frozenset({
    "what",
    "state",
    "blocked_by",
    "blocked_evidence",
    "depends_on_evidence",
    "outcome",
    "observed",
    "superseded_note",
    "closes_clause",
    "prerequisite_of",
    "requires_trimcrae",
    "requires_trimcrae_why",
    "_requires_trimcrae_why",
    "_block_cleared",
})

#: Fields that move without anybody learning anything: re-scores, claims, lease bookkeeping, and the
#: self-typed evidence date this module replaces.
TOUCH_FIELDS = frozenset({
    "score",
    "score_inputs",
    "_score_basis",
    "score_clamped_from",
    "clamp",
    "owner",
    "claimed_utc",
    "attempts",
    "retry_budget",
    # AUT-PD-014: the progress-aware retry-budget history. Bookkeeping about WHETHER a row was
    # dispatched, exactly like `attempts`/`retry_budget` beside it — never evidence of what was
    # learned. What WAS learned, if anything, shows up as a change to `last_evidence_utc` or
    # `blocked_evidence` instead, which are already PROGRESS_FIELDS above.
    "dispatch_log",
    "lease_released",
    "_lease_released",
    "last_evidence_utc",
    "kind",
    "cost_class",
    "cost_points_at",
    "filed_by",
    "id",
    "_derived",
    "serves",  # only `serves.route` is progress; handled as a special case in classify_change()
})

#: Entering one of these is a resolution. `queued` and `in_progress`/`running` are deliberately
#: absent: moving between them is a claim and a lease expiry, not an advance.
PROGRESS_STATES = frozenset({"done", "abandoned", "superseded", "blocked"})

#: A row in one of these is finished and has no stall clock. Anything else counts as open, including
#: a state nobody has seen before — an unreadable state must not be able to hide a row.
CLOSED_STATES = frozenset({"done", "abandoned", "superseded"})

# --------------------------------------------------------------------------------------------
# The threshold and the terminal state.
# --------------------------------------------------------------------------------------------

#: Cycles without a substantive change before a row is declared terminal. 6 x the 4 h cycle interval
#: = 24 h.
#:
#: ⛔ CHOSEN FROM WHAT THIS REPOSITORY HAS MEASURED, BECAUSE THE BORROWED NUMBER ADMITS IT WAS NOT.
#: The survey's Rucio multiplier comes with its own author's note that it "was chosen without any
#: particular reason", and Rucio's actual source uses a FLAT 14 days against a daemon that runs
#: continuously — a ratio of order 10^3 beats, not 10. Neither transfers. What does transfer is the
#: local bracket:
#:   LOWER BOUND, hard: `priority-weights.json:claim_lease.periods` is 2, so a lease expires at 2
#:     cycles (8 h) and bumps `attempts`. A threshold at or below that would declare a stall every
#:     time the lease machinery worked correctly.
#:   UPPER ANCHOR: `stall_alarm.REPEAT_EVERY_RUNS` is 12 runs of a 2 h tick, i.e. ~24 h, already
#:     settled in this repository as the period at which "a genuine outage nags but does not flood".
#:     A stall report that fires faster than the loop's own alarm cadence is noise by construction.
#: 6 cycles is 3x the lease and exactly that 24 h. It also lands at the low end of the borrowed
#: 6x-10x band, which is the direction to err: this loop's beat is 4 h, so 6 beats is already a full
#: day in which six chances to advance the row were available and none was taken.
#: ⚠ It is a number to be RE-MEASURED, not defended. The one observation that would settle it is the
#: distribution of real inter-advance gaps for rows that did eventually advance; with the history
#: censored at ~19 h (see the module docstring) that distribution is not yet computable here.
STUCK_AFTER_CYCLES = 6

#: Fallback if `autonomy-state.json` is unreadable — the same 4 h `priority.py` falls back to.
FALLBACK_CYCLE_INTERVAL_HOURS = 4.0

#: ⛔ THE TERMINAL STATE, AND IT IS DERIVED RATHER THAN DECLARABLE. Rucio's analogue is SUSPENDED.
#: It means exactly one thing: automation has stopped trying and a human is required. It is DATED —
#: every terminal verdict carries `since_utc`, the moment the threshold was crossed — so it can never
#: be a row quietly reading UNKNOWN. ⚠ No session can type this into the ledger; it exists only as
#: this module's output, computed from git, which is the point.
TERMINAL_STATE = "stalled_needs_human"

TERMINAL_WHY = (
    "no substantive change in {hours:.0f} h ({cycles:.1f} cycles) despite {attempts} recorded "
    "attempt(s). Automation has stopped trying: a human decides whether this row is re-scoped, "
    "handed over or closed."
)


def cycle_interval_hours(state_path: str | None = None) -> float:
    """The loop's beat. Read from the governor's own file, never restated (CLAUDE.md §1)."""
    path = state_path or os.path.join(HERE, "autonomy-state.json")
    try:
        with open(path, encoding="utf-8") as fh:
            value = json.load(fh).get("cycle_interval_hours")
        return float(value) if value else FALLBACK_CYCLE_INTERVAL_HOURS
    except Exception:
        return FALLBACK_CYCLE_INTERVAL_HOURS


def stuck_threshold_hours(state_path: str | None = None, cycles: int = STUCK_AFTER_CYCLES) -> float:
    """Hours of no substantive change after which a tried row is terminal."""
    return cycles * cycle_interval_hours(state_path)


# --------------------------------------------------------------------------------------------
# Reading the history out of git.
# --------------------------------------------------------------------------------------------


def _git(args: list[str], repo: str) -> str:
    return subprocess.run(["git", "-C", repo] + args, capture_output=True, text=True,
                          check=True).stdout


def _cat_file_batch(revs: list[str], repo: str) -> dict[str, str]:
    """`{rev: blob text}` for many revs in ONE git process, skipping anything git will not give.

    ⛔⛔ THE SECOND HALF OF THE 2026-09-01 HOT-SPOT FIX, AND IT IS THE HALF THE MEMO CANNOT DO.
    Memoising `ledger_versions` took gate 13 from 446 s to 54 s by cutting 130 walks to ~3, but a
    walk is still one `git show` PROCESS PER COMMIT — 372 forks, 372 object-store openings, 372
    ~1.25 MB blobs piped through a shell, ~7.5 s each. `git cat-file --batch` reads every rev on
    stdin and answers on one stream, so a walk costs one fork instead of 372.

    ⭐ THE PROTOCOL, READ FROM `git help cat-file` RATHER THAN REMEMBERED: for each input line git
    writes `<oid> SP <type> SP <size> LF`, then exactly `<size>` BYTES, then one LF. A rev git
    cannot resolve gets `<input> SP missing LF` and no body. Sizes are in bytes, so the stream is
    read as bytes and each blob decoded afterwards — decoding first would desynchronise the reader
    on the first non-ASCII character in the ledger, which is a silent corruption rather than an
    error.

    ⛔ IT FAILS TO AN EMPTY DICT, NEVER TO A GUESS. Any error — git too old, a truncated stream, a
    header that does not parse — returns `{}` and the caller falls back to the per-commit `git
    show` it has always used. A version this cannot read must look to `ledger_versions` exactly
    like a version that would not parse: skipped, never treated as an empty ledger, because
    "every row was deleted" resets every clock in one step.
    """
    if not revs:
        return {}
    try:
        proc = subprocess.run(["git", "-C", repo, "cat-file", "--batch"],
                              input=("\n".join(revs) + "\n").encode(),
                              stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, check=True)
    except Exception:
        return {}
    out: dict[str, str] = {}
    buf, pos = proc.stdout, 0
    for rev in revs:
        nl = buf.find(b"\n", pos)
        if nl < 0:
            break
        header = buf[pos:nl].decode("utf-8", "replace").split(" ")
        pos = nl + 1
        if len(header) != 3 or not header[2].isdigit():
            # `missing`, `ambiguous`, or anything this parser does not recognise: no body follows,
            # so the stream stays in sync and the rev is simply absent from the result.
            continue
        size = int(header[2])
        out[rev] = buf[pos:pos + size].decode("utf-8", "replace")
        pos += size + 1
    return out


def is_shallow(repo: str = REPO) -> bool:
    """⛔ A shallow clone cannot see when a row last advanced; it can only see the graft point."""
    try:
        return _git(["rev-parse", "--is-shallow-repository"], repo).strip() == "true"
    except Exception:
        return False


@dataclass
class Version:
    """One committed state of the ledger."""
    sha: str
    when: datetime.datetime
    rows: dict


#: ⛔⛔ THE COMMIT LOOP'S SINGLE BIGGEST COST LIVED IN THIS FUNCTION, AND IT SCALED WITH COMMIT
#: COUNT RATHER THAN WITH ANYTHING ANYONE WAS WATCHING. Measured 2026-09-01 by seat S6-COMMITLOOP,
#: counted with a `git` shim on PATH rather than estimated: **48,230 of gate 13's 50,270 git calls
#: — 96% — were `git show <sha>:research-ledger.json`**, over 371 commits. That is ~130 complete
#: walks of the ledger's entire history in one gate run: ~975 CPU-seconds and roughly 60 GB of blob
#: text, about 55% of a gate that is itself 85-94% of the commit loop.
#: ★ AND THE DENOMINATOR IS THE REPOSITORY'S OWN COMMIT COUNT, which is the part that made it
#: invisible: nothing regressed, no test got slower, no code changed. Every commit this repository
#: makes was making its own commit loop slower, by one more `git show` per walk per run. It went
#: 371 to 372 inside twenty minutes on the night it was found.
#: ⭐ THE CACHE IS KEYED ON (repo, path, HEAD), NOT ON (repo, path). History is append-only, so two
#: calls at the same HEAD MUST return the same answer — but two calls at different HEADs must not,
#: and a process that commits between them is the ordinary case here, not an exotic one. Keying on
#: HEAD makes the cache a memo of a pure function rather than a bet that nothing moved.
#: ⚠ WHAT THIS DOES NOT CHANGE: every assertion, every skip, every verdict. It is the same list,
#: computed once per HEAD instead of once per caller.
_VERSIONS_CACHE: dict[tuple[str, str, str], list["Version"]] = {}


def _head_sha(repo: str) -> str:
    """The commit the cache is keyed on, or `""` when it cannot be read.

    ⛔ AN UNREADABLE HEAD DISABLES THE CACHE RATHER THAN SHARING ONE BUCKET. Returning a constant
    on failure would make every call at every unreadable HEAD collide into a single entry — a
    correctness bug bought for a performance win, which is the trade this repository refuses. `""`
    is returned and the caller treats it as "do not cache".
    """
    try:
        return _git(["rev-parse", "HEAD"], repo).strip()
    except Exception:
        return ""


def ledger_versions(repo: str = REPO, path: str = LEDGER_PATH) -> list[Version]:
    """Every committed version of the ledger, oldest first, as `{id: row}` maps.

    ⚠ A version that will not parse is SKIPPED rather than treated as an empty ledger: a
    half-written file in history must not read as "every row was deleted and re-created", which would
    reset every clock in one step. Skipping is the direction that preserves the stall.

    ⭐ MEMOISED PER (repo, path, HEAD) — see `_VERSIONS_CACHE` above for the measurement that
    demanded it. The returned list is shared between callers, so it must be treated as read-only;
    every consumer in this module already reads it that way. ⛔ AND A ROW OBJECT IS SHARED BETWEEN
    VERSIONS TOO when it did not change between them — the interning below, which is what keeps the
    memo affordable. Read-only is therefore not a courtesy here; mutating one row would rewrite the
    row's own history.
    """
    head = _head_sha(repo)
    key = (repo, path, head)
    if head and key in _VERSIONS_CACHE:
        return _VERSIONS_CACHE[key]

    out: list[Version] = []
    try:
        log = _git(["log", "--follow", "--format=%H %ct", "--", path], repo)
    except subprocess.CalledProcessError:
        return out
    commits = []
    for line in reversed(log.strip().splitlines()):
        if not line.strip():
            continue
        sha, _, ts = line.partition(" ")
        commits.append((sha, ts))
    # ⭐ ONE `git cat-file --batch` FOR THE WHOLE WALK, falling back per commit to `git show` for
    # anything it could not answer — so an unreadable batch costs the old speed, never a wrong list.
    blobs = _cat_file_batch([f"{sha}:{path}" for sha, _ in commits], repo)
    # ⛔⛔ THE MEMO ABOVE TRADES CPU FOR MEMORY, AND WITHOUT THIS LINE IT TRADES IT AT 16x THE FAIR
    # PRICE — IN THE SAME CURRENCY THE WHOLE FIX WAS ABOUT: something that grows with COMMIT COUNT.
    # Measured 2026-09-02 against this repository's real history: the walk returns 380 versions
    # holding **84 792 row objects, of which only 2 319 are distinct states** — a 36.6x redundancy,
    # because the ordinary commit changes one row and copies 144.
    # ⭐ SO A ROW THAT DID NOT CHANGE IS THE SAME OBJECT AS THE VERSION BEFORE IT. Two fresh
    # processes, resident bytes read from `/proc/self/statm` after `gc.collect()`, each walking the
    # same 380 versions:
    #
    #                      walk    holding the memo    after dropping it    => RETAINED BY THE MEMO
    #   un-interned       7.33 s        466 MB               340 MB                  126 MB
    #   interned          2.79 s        245 MB               237 MB                    8 MB
    #
    # ⚠ THE RETAINED COLUMN IS THE ONE THAT MATTERS AND IT IS THE ONE A CASUAL MEASUREMENT MISSES.
    # `ru_maxrss` is a PEAK and barely moves here — transient parse arenas dominate it and CPython
    # does not return freed pages to the OS — so an earlier draft of this comment recorded 652 MB,
    # which was the delta INCLUDING that transient allocation, not what the cache holds. The number
    # that scales with commit count, four times over under `pytest -n 4`, is the retained one.
    # ⭐ And the walk gets FASTER as well, because dropping a duplicate costs less than keeping it.
    # ⛔ AND IT CHANGES NO VERDICT, WHICH IS ASSERTED RATHER THAN ARGUED: `compute_clocks` compares
    # rows with `!=`, so an interned row and an equal copy are already indistinguishable to it, and
    # `test_the_ledger_history_is_read_in_one_git_process.py` pins every clock field against the
    # un-interned walk over the real history.
    # ⚠ THE OBLIGATION THIS CREATES: a row object may now be SHARED between versions, so nothing
    # may mutate one. Every consumer in this module and in `learning_rate.py` / `out_of_ideas.py`
    # reads them, and `ledger_versions`' docstring already says the returned list is read-only.
    interned: dict = {}
    for sha, ts in commits:
        try:
            blob = blobs.get(f"{sha}:{path}")
            if blob is None:
                blob = _git(["show", f"{sha}:{path}"], repo)
            entries = json.loads(blob).get("entries", [])
        except Exception:
            continue
        rows = {e["id"]: e for e in entries if isinstance(e, dict) and e.get("id")}
        for entry_id, row in rows.items():
            previous = interned.get(entry_id)
            if previous is not None and previous == row:
                rows[entry_id] = previous          # unchanged: keep one copy, drop the duplicate
            else:
                interned[entry_id] = row
        when = datetime.datetime.fromtimestamp(int(ts), datetime.timezone.utc)
        out.append(Version(sha=sha, when=when, rows=rows))
    if head:
        _VERSIONS_CACHE[key] = out
    return out


# --------------------------------------------------------------------------------------------
# The two clocks.
# --------------------------------------------------------------------------------------------


def classify_change(field_name: str, before, after) -> str:
    """`"progress"`, `"touch"` or `"unclassified"` for one field that changed on one row.

    The three-way answer is the point: `"unclassified"` is not folded into `"touch"` at the call
    site, so a field the schema grew after this module was written is COUNTED as a non-advance and
    NAMED in the report, rather than silently deciding either way.
    """
    if field_name == "state":
        return "progress" if after in PROGRESS_STATES else "touch"
    if field_name == "serves":
        before_route = (before or {}).get("route") if isinstance(before, dict) else None
        after_route = (after or {}).get("route") if isinstance(after, dict) else None
        return "progress" if before_route != after_route else "touch"
    if field_name in PROGRESS_FIELDS:
        return "progress"
    if field_name in TOUCH_FIELDS:
        return "touch"
    return "unclassified"


@dataclass
class Clocks:
    """Both clocks for one ledger row, plus what the module could and could not see."""
    entry_id: str
    state: str | None
    created_at: datetime.datetime | None = None
    updated_at: datetime.datetime | None = None      # ANY change touched this row
    stuck_at: datetime.datetime | None = None        # the last change that ADVANCED it
    censored: bool = False                           # stuck_at is a lower bound (shallow horizon)
    tried: bool = False                              # automation ever claimed or retried this row
    attempts: int = 0
    identity_changed: bool = False                   # `serves.route` was re-pointed under this id
    unclassified_fields: set = field(default_factory=set)
    last_progress_fields: set = field(default_factory=set)

    def stuck_hours(self, now: datetime.datetime) -> float | None:
        if self.stuck_at is None:
            return None
        return (now - self.stuck_at).total_seconds() / 3600.0

    def is_open(self) -> bool:
        return self.state not in CLOSED_STATES

    def terminal(self, now: datetime.datetime, threshold_h: float,
                 horizon: datetime.datetime | None = None) -> dict | None:
        """The dated terminal verdict, or None.

        ⛔ FOUR CONDITIONS, AND THE LAST TWO ARE THE HONEST ONES. Open; past the threshold; TRIED,
        because a queued row nobody has reached yet is starved rather than stuck and calling 100 of
        those terminal is the cry-wolf failure this repository has already paid for; and — for a
        censored row — the bound must be one this function is entitled to reason about.

        ⛔ A CENSORED ROW IS DECIDED BY THE SAME COMPARISON AS ANY OTHER, AND THAT IS NOT AN
        OVERSIGHT. `compute_clocks` stamps a censored row's `stuck_at` FROM the horizon, so its age
        and the horizon's age are the same number: a bound above the threshold is conclusive (the
        true age is only larger), and a bound below it decides nothing. Adding a second, separate
        horizon-age comparison here would be dead code — measured, not assumed: the mutation that
        deleted it left all 38 tests green (M5, 2026-08-28), which is what dead code looks like.
        ⭐ WHAT THE HORIZON IS ACTUALLY FOR, THEN: checking that the invariant the paragraph above
        rests on still holds. A future censor that marks a row whose `stuck_at` predates the horizon
        would be handing this function a bound it has not reasoned about, and an unreadable horizon
        is the same case. Both refuse a verdict rather than issue one on unknown data.
        """
        if not self.is_open():
            return None
        hours = self.stuck_hours(now)
        if hours is None or hours < threshold_h:
            return None
        if not self.tried:
            return None
        if self.censored and (horizon is None or self.stuck_at < horizon):
            return None
        since = self.stuck_at + datetime.timedelta(hours=threshold_h)
        return {
            "state": TERMINAL_STATE,
            "since_utc": since.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "why": TERMINAL_WHY.format(hours=hours, cycles=hours / (threshold_h / STUCK_AFTER_CYCLES),
                                       attempts=self.attempts),
        }


def compute_clocks(versions: list[Version], shallow: bool = False) -> dict[str, Clocks]:
    """Walk the committed history once and stamp both clocks for every row it ever saw.

    ⚠ COMPARED AGAINST THE ROW'S LAST SEEN STATE, NOT THE PREVIOUS VERSION'S. A row can vanish from
    one committed version — a concurrent regeneration, a mid-rebase file — and return unchanged;
    treating the return as a creation would reset its clock, which is the silent direction.
    """
    clocks: dict[str, Clocks] = {}
    seen: dict[str, dict] = {}
    horizon_sha = versions[0].sha if versions else None
    for version in versions:
        for entry_id, row in version.rows.items():
            previous = seen.get(entry_id)
            if previous is None:
                clocks[entry_id] = Clocks(
                    entry_id=entry_id,
                    state=row.get("state"),
                    created_at=version.when,
                    updated_at=version.when,
                    stuck_at=version.when,
                    # ⛔ A row already present in the OLDEST visible version may be far older than
                    # this timestamp. In a shallow clone that is most of them.
                    censored=bool(shallow and version.sha == horizon_sha),
                    tried=bool(row.get("owner")) or bool(row.get("attempts")),
                    attempts=int(row.get("attempts") or 0),
                )
                seen[entry_id] = row
                continue

            clock = clocks[entry_id]
            changed = [k for k in set(previous) | set(row) if previous.get(k) != row.get(k)]
            if changed:
                clock.updated_at = version.when
            progressed = False
            for key in changed:
                verdict = classify_change(key, previous.get(key), row.get(key))
                if verdict == "unclassified":
                    clock.unclassified_fields.add(key)
                elif verdict == "progress":
                    progressed = True
                    clock.last_progress_fields.add(key)
                    if key == "serves":
                        clock.identity_changed = True
            if progressed:
                clock.stuck_at = version.when
                clock.censored = False       # an advance seen inside the window is exact
                clock.last_progress_fields = {
                    k for k in changed if classify_change(k, previous.get(k), row.get(k)) == "progress"
                }
            clock.state = row.get("state")
            clock.attempts = int(row.get("attempts") or 0)
            if row.get("owner") or int(row.get("attempts") or 0) > 0:
                clock.tried = True
            seen[entry_id] = row
    return clocks


# --------------------------------------------------------------------------------------------
# The public read.
# --------------------------------------------------------------------------------------------


def open_row_clocks(repo: str = REPO, path: str = LEDGER_PATH,
                    now: datetime.datetime | None = None) -> dict:
    """THE ONE CALL OTHER MODULES SHOULD USE.

    Returns `{"rows": [Clocks], "now", "horizon", "shallow", "threshold_hours", "interval_hours"}`,
    rows sorted longest-stuck first and restricted to rows that are still open.
    """
    now = now or datetime.datetime.now(datetime.timezone.utc)
    shallow = is_shallow(repo)
    versions = ledger_versions(repo, path)
    clocks = compute_clocks(versions, shallow=shallow)
    threshold = stuck_threshold_hours(os.path.join(repo, "research", "autonomy",
                                                   "autonomy-state.json"))
    rows = [c for c in clocks.values() if c.is_open()]
    rows.sort(key=lambda c: -(c.stuck_hours(now) or -1.0))
    return {
        "rows": rows,
        "now": now,
        "horizon": versions[0].when if versions else None,
        "n_versions": len(versions),
        "shallow": shallow,
        "threshold_hours": threshold,
        "interval_hours": cycle_interval_hours(os.path.join(repo, "research", "autonomy",
                                                            "autonomy-state.json")),
    }


def terminal_rows(report: dict | None = None, **kwargs) -> list[tuple]:
    """`[(Clocks, verdict)]` for every row automation should stop retrying."""
    report = report or open_row_clocks(**kwargs)
    out = []
    for clock in report["rows"]:
        verdict = clock.terminal(report["now"], report["threshold_hours"], report["horizon"])
        if verdict:
            out.append((clock, verdict))
    return out


def _fmt(stamp: datetime.datetime | None) -> str:
    return stamp.strftime("%Y-%m-%d %H:%M") if stamp else "—"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--check", action="store_true", help="print rows, longest-stuck first")
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    parser.add_argument("--repo", default=REPO)
    parser.add_argument("--path", default=LEDGER_PATH,
                        help="repo-relative path of the ledger (the CLI must be able to point at "
                             "another checkout, or nothing can test it against a known history)")
    parser.add_argument("--limit", type=int, default=25)
    parser.add_argument("--fail-on-terminal", action="store_true",
                        help="exit 1 if any open row is terminal")
    args = parser.parse_args(argv)

    report = open_row_clocks(repo=args.repo, path=args.path)
    now, threshold = report["now"], report["threshold_hours"]
    terminal = dict((c.entry_id, v) for c, v in terminal_rows(report))

    if args.json:
        print(json.dumps({
            "generated_utc": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "history_horizon_utc": _fmt(report["horizon"]),
            "shallow_clone": report["shallow"],
            "cycle_interval_hours": report["interval_hours"],
            "stuck_after_cycles": STUCK_AFTER_CYCLES,
            "threshold_hours": threshold,
            "terminal_state": TERMINAL_STATE,
            "rows": [{
                "id": c.entry_id, "state": c.state,
                "updated_at": _fmt(c.updated_at), "stuck_at": _fmt(c.stuck_at),
                "stuck_hours": round(c.stuck_hours(now) or 0.0, 2),
                "censored": c.censored, "tried": c.tried, "attempts": c.attempts,
                "identity_changed": c.identity_changed,
                "unclassified_fields": sorted(c.unclassified_fields),
                "terminal": terminal.get(c.entry_id),
            } for c in report["rows"]],
        }, indent=2))
        return 1 if (args.fail_on_terminal and terminal) else 0

    print(f"   ledger history: {report['n_versions']} committed versions, oldest "
          f"{_fmt(report['horizon'])} UTC")
    print(f"   threshold: {STUCK_AFTER_CYCLES} cycles x {report['interval_hours']:.0f} h = "
          f"{threshold:.0f} h without a SUBSTANTIVE change -> {TERMINAL_STATE}")
    if report["shallow"]:
        age = (now - report["horizon"]).total_seconds() / 3600.0 if report["horizon"] else 0.0
        print(f"   ⛔ SHALLOW CLONE: git can see back only {age:.1f} h. Rows marked >= carry a LOWER "
              "BOUND, not a measurement" + ("" if age >= threshold else
              " — and no censored row can be declared terminal until that bound passes the "
              "threshold") + ".")
        print("   ⭐ To measure them: ./scripts/dev-setup.sh — it deepens the clone past every "
              "window read off this history, not just this module's (it owns that window and "
              "the measurement behind it; the SessionStart hook runs it, so a sandbox still "
              "reading short is one the hook did not reach). A full `git fetch --unshallow` "
              "also works and costs ~90x more.")

    header = f"{'stuck':>9}  {'id':<16} {'state':<12} {'stuck_at':<17} {'updated_at':<17} flags"
    print()
    print(header)
    print("-" * len(header))
    for clock in report["rows"][:args.limit]:
        hours = clock.stuck_hours(now) or 0.0
        flags = []
        if clock.entry_id in terminal:
            flags.append(f"⛔ {TERMINAL_STATE} since {terminal[clock.entry_id]['since_utc']}")
        if clock.censored:
            flags.append("censored")
        if not clock.tried:
            flags.append("never tried")
        if clock.identity_changed:
            flags.append("identity changed")
        if clock.unclassified_fields:
            flags.append("unclassified: " + ",".join(sorted(clock.unclassified_fields)))
        print(f"{'>=' if clock.censored else '  '}{hours:7.1f}h  {clock.entry_id:<16} "
              f"{str(clock.state):<12} {_fmt(clock.stuck_at):<17} {_fmt(clock.updated_at):<17} "
              + " · ".join(flags))

    touched_not_advanced = [c for c in report["rows"]
                            if c.updated_at and c.stuck_at and c.updated_at > c.stuck_at]
    print()
    print(f"   {len(report['rows'])} open rows · {len(terminal)} {TERMINAL_STATE} · "
          f"{len(touched_not_advanced)} touched since they last advanced")
    if not terminal:
        print("   No row is terminal. That is a reading, not a green tick: a censored row is one "
              "git cannot see far enough back to judge.")
    return 1 if (args.fail_on_terminal and terminal) else 0


if __name__ == "__main__":
    sys.exit(main())
