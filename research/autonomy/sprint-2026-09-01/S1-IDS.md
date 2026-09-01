---
id: DOC-SPRINT-S1-IDS
title: "S1-IDS — the entry-id allocator now carries the discriminator its sibling always had"
level: L3
kind: memo
status: live
date: 2026-09-01
audience: [autonomous research agents, maintainers]
purpose: "The findings record of sprint seat S1-IDS — what it measured, what it changed, and what it could not do. Written before the seat returned, so a seat that dies costs its own work and nothing else."
scope: "One seat of the 2026-09-01 sprint, bounded by the owned-paths list in its own prompt. It reports; it does not decide what lands."
last_verified: 2026-09-01
---

# S1-IDS — `ids.next_entry_id` collided; it no longer can

**Item(s):** AUT-PD-171   **Owned paths:** `research/autonomy/ids.py`,
`research/autonomy/tests/` (`test_ids_cannot_collide.py`), this file
**Started/Finished (UTC):** 2026-09-01T18:37Z / 2026-09-01T19:00Z (the whole-suite bonus run was still going, §7)

## Verdict

**FIXED.** The defect was reproduced live before anything was touched — two concurrent processes
reading one committed ledger were both handed `AUT-PD-204` — and `next_entry_id` now mints
`AUT-PD-204-<session discriminator>` from the same `discriminator()` its sibling `next_receipt` has
used since 2026-08-27; 9 tests fail before the change and pass after, and 6 of 6 single-site
mutations of the fix are caught.

## What I measured

### 1 · The collision, reproduced first (charter §4)

Two real subprocesses, no shared memory, one committed ledger read with `git show HEAD:` — run
against the **unpatched** working tree:

```
$ python3 scratchpad/repro.py
committed ledger: HEAD:research/autonomy/research-ledger.json (344 entries)
  session 6b009680  ->  ids.next_entry_id('AUT-PD', entries) = AUT-PD-204
  session 4ce79c2a  ->  ids.next_entry_id('AUT-PD', entries) = AUT-PD-204

COLLISION: two concurrent sessions were both handed AUT-PD-204
exit=1
```

The two discriminators are those of the cycles the ledger row names in its second occurrence —
CYC-0085-6b009680 and CYC-0086-4ce79c2a; the full session UUIDs are not recorded anywhere, so the
rest of each is filler. **The row is not stale: the defect is live on the trunk as of this run.**

### 2 · What `next_receipt` does differently, cited

`research/autonomy/ids.py` before this change — `next_receipt` at line 82, `next_entry_id` at
line 114, one function between them:

```python
def next_receipt(receipt_dir: str, session_id: str) -> tuple[str, str]:
    n = max(receipt_ordinals(receipt_dir), default=-1) + 1
    cycle_id = f"CYC-{n:04d}-{discriminator(session_id)}"     # ← ordinal + SESSION

def next_entry_id(prefix: str, entries: list[dict]) -> str:
    ...
    return f"{prefix}-{max(used, default=0) + 1:0{width}d}"    # ← ordinal ONLY
```

Three differences, in the order they matter:

1. **`next_receipt` takes `session_id` at all.** `next_entry_id` had no parameter through which an
   identity could enter, so concurrency was outside its derivation *by construction* — the module's
   own docstring says exactly that about the derivation it replaced, and then left one caller on it.
2. **`discriminator()` refuses to invent one** (`ids.py:52-65`): an empty or unusable session id
   raises `ValueError` rather than falling back to a clock or a counter, *"because a fallback that
   silently produces a collidable id is worse than a loud failure."*
3. **The ordinal is deliberately shared** (`next_receipt`'s docstring): two concurrent cycles ARE
   both the Nth, and what the record needs is for both to survive saying so. Only the NAME must
   differ.

`next_entry_id`'s old docstring was honest about being max+1 and drew the wrong conclusion from it:
*"a concurrent filing surfaces as a rebase conflict or is caught by `duplicate_ids()` at the
commit."* Both halves of that are true and neither avoids the collision — they are how the loser
**learns**, and the loser is whoever pushes second, which nobody knows until the push.

### 3 · After the fix, same two processes, same committed ledger

```
  session 6b009680  ->  AUT-PD-204-6b009680
  session 4ce79c2a  ->  AUT-PD-204-4ce79c2a
no collision: the two sessions got different ids
exit=0
```

### 4 · Tests: red before, green after

`pytest research/autonomy/tests/test_ids_cannot_collide.py` — **19 passed** on the patched tree.
The same file run against the pre-fix module (`git show HEAD:research/autonomy/ids.py`, injected in
a scratch copy through a pytest plugin so the live tree was never mutated):

```
9 failed, 10 passed
FAILED ...::test_two_sessions_reading_the_same_ledger_get_different_entry_ids
FAILED ...::test_both_sessions_still_claim_the_same_entry_ordinal
FAILED ...::test_the_ordinal_advances_past_a_discriminated_id
FAILED ...::test_an_entry_id_is_refused_rather_than_minted_without_a_session
FAILED ...::test_the_session_is_read_from_the_environment_when_it_is_not_passed
FAILED ...::test_the_discriminator_is_the_session_and_not_the_moment
FAILED ...::test_entry_ids_are_allocated_over_the_whole_ledger_not_by_eye
FAILED ...::test_every_id_on_the_committed_ledger_still_parses
FAILED ...::test_two_concurrent_filings_merge_without_a_renumber
```

⚠ **Read that honestly: most of those nine fail on the SIGNATURE, not on the collision** — the old
function has no `session_id` parameter, so `TypeError` arrives before any assertion does. The
evidence that the tests detect the *defect* rather than the *signature* is the mutation run below,
where every mutation keeps the new signature and changes one thing.

### 4b · The consumers, run rather than reasoned about

```
$ pytest systems/tests/test_autonomy_priority.py systems/tests/test_autonomy_antistall.py -q
33 passed in 0.37s
$ python3 research/autonomy/prepush_ledger_guard.py --check
[prepush-ledger-guard] OK: no duplicate ledger ids
$ python3 research/autonomy/priority.py --limit 3        # 344 entries, ranks and prints
$ python3 -c "<spec_from_file_location load of ids.py>"  # the systems/tests loader pattern
spec_from_file_location load OK -> AUT-PD-204-e71cf460
$ python3 -c "import session_reaper, priority, proposal_dedup, claim"
consumers import OK
```

The `spec_from_file_location` check is not ceremony: `ids.py` gained a local import (`envread`), and
`systems/tests` loads modules from `research/autonomy/` by file path with that directory NOT on
`sys.path`. The module inserts its own directory first, the way `priority.py` and `session_cap.py`
already do, so both load paths work.

### 5 · Mutation testing — 6 of 6 caught, all single-site, all in scratch copies

Each mutation is one edit to a copy of the fixed `ids.py` under the scratchpad, injected the same
way; the live tree was never mutated (charter §7 / CLAUDE.md §6, the 2026-08-27 incident from the
other end).

| mutation | one site changed | caught by |
|---|---|---|
| M1 mint without the discriminator | drop `-{disc}` from the returned id | `two_sessions_..._different_entry_ids` (+3) |
| M2 discriminator from a clock | `disc = time.time()`-derived | `the_discriminator_is_the_session_and_not_the_moment` (+3) |
| M3 scan blind to a discriminated id | delete the optional group from `ENTRY_ID` | `the_ordinal_advances_past_a_discriminated_id` (+7) |
| M4 silent fallback when no session | `return "00000000"` instead of raising | `an_entry_id_is_refused_rather_than_minted_without_a_session` |
| M5 two-valued env read | `os.environ.get(X, "")` in place of `envread.read` | `an_entry_id_is_refused_rather_than_minted_without_a_session` |
| M6 prefix bleeds across families | drop `parsed[0] == prefix` | `entry_ids_are_allocated_over_the_whole_ledger_not_by_eye` |

**M3 is the one that justifies its own test.** Widening the mint without widening the scan is a
single plausible omission, and it is *worse* than the bug it replaces: the ordinal freezes at the
last bare id, so the very next call **in the same session** returns the id it just issued — one
session naming two rows the same thing, in one file, with no second pusher to notice.

### 6 · Nothing else on the trunk reads a ledger id by shape

- `ids.duplicate_ids` — opaque strings, unaffected.
- `push_guard.check_ledger`, `prepush_ledger_guard.check` — `Counter` over `e["id"]`, unaffected.
- `proposal_dedup.py:115` (`_ID_RE`) — `\b[A-Z]{2,}-[A-Z0-9]+-\d+\b` still
  extracts `AUT-PD-204` out of `AUT-PD-204-6b009680`; it normalises tokens for similarity, so
  matching on the ordinal is the behaviour it wants.
- `priority.merge` — **the one real interaction, measured:**

  ```
  'AUT-PD-204'           -> priority.merge used-ordinal = 204
  'AUT-PD-204-6b009680'  -> ValueError: invalid literal for int()  (swallowed by merge's
                            `except ValueError: pass`, so the ordinal stops being counted)
  ```

  `priority.py:629` derives its own `AUT-NNN` space with `int(str(id).rsplit("-", 1)[-1])`. This is
  **not** a duplicate-id risk — `AUT-204` and `AUT-PD-204-6b009680` are different strings and
  `duplicate_ids` stays empty — but a discriminated row stops de-conflicting the derived counter, so
  two rows could end up sharing an *ordinal* across families. `priority.py` is a governed path and
  not mine this sprint; `ids.parse_entry_id()` exists so the fix there is one line. Row proposed
  below.

## What I changed

Governance, asked of the guard rather than assumed:

```
$ python3 -c "import amendment_guard as A; ..."
False  research/autonomy/ids.py
 True  research/autonomy/tests/test_ids_cannot_collide.py     <- amendment record below
False  research/autonomy/sprint-2026-09-01/S1-IDS.md
 True  research/autonomy/priority.py                          <- NOT mine, row proposed below
```

**`research/autonomy/ids.py`**:

- `SESSION_ENV = "CLAUDE_CODE_SESSION_ID"` — spelled once, the same variable
  `session_cap.session_id()` reads.
- `ENTRY_ID` + `parse_entry_id()` — one regex for the allocator and every reader, parsing both the
  bare and the discriminated shape. The prefix is lazy because prefixes themselves contain hyphens
  (`AUT`, `AUT-PD`, `AUT-PROP`, `AUT-BIX`, `AUT-COV`, `AUT-RT`, `AUT-INC` are all live), and the
  separator stays optional so the new scan accepts everything the old one did.
- `session_discriminator(session_id=None)` — explicit session, else a **three-valued** `envread`
  read of `CLAUDE_CODE_SESSION_ID`; unset and exported-empty raise with different messages, and
  neither ever yields a bare id.
- `next_entry_id(prefix, entries, session_id=None)` — ordinal over the whole ledger (now counting
  discriminated ids), then `-{disc}`.
- Module docstring: records AUT-PD-171 and the five measured occurrences; the old
  *"honestly still max+1"* docstring is retained as superseded text inside the new one
  (CLAUDE.md rule 1.2), not deleted.

**⭐ WHY `session_id` IS OPTIONAL AND NOT REQUIRED — the one place I diverged from the sibling.**
`next_receipt` demands the session as a positional argument. Copying that exactly would have made
`.claude/skills/research-loop/SKILL.md` §2 step 10 — which tells every cycle to call
`ids.next_entry_id("AUT-PD", entries)` — a `TypeError`, so a cycle following the contract EXACTLY
would keep minting collidable ids until a file I do not own was edited. That is the writer/reader
gap this repository has now lost four times (AUT-PD-146). Making the parameter optional and reading
the session from the environment gives the *documented two-argument call site* the fix with no doc
edit, and `test_the_session_is_read_from_the_environment_when_it_is_not_passed` pins it. It is
strictly not weaker: there is no branch on which a missing session produces an id.

**`research/autonomy/tests/test_ids_cannot_collide.py`** — 9 entry-id tests where there was 1
(`test_entry_ids_are_allocated_over_the_whole_ledger_not_by_eye`, rewritten: its old docstring
asserted the max+1 behaviour as correct). Net 19 tests in the file, all passing.

## What I could not do, and what it is actually waiting on

- **Nothing was blocked.** No spend, no network, no trimcrae decision.
- **`priority.py:629` is not fixed** — it is a GOVERNED path and not in my OWNED PATHS. Waiting on
  the driver to sequence it (one line, named above), not on any external thing.
- **`.claude/skills/research-loop/SKILL.md` needs no edit for correctness** (the two-argument call
  now returns a discriminated id) but its §2 step 10 prose still describes ledger ids as plain
  `max+1`. Also governed, also the driver's.
- **⚠ AN HONEST LIMIT OF THE FIX, MEASURED, NOT ASSUMED: the discriminator separates SESSIONS, and
  I could not establish that it separates concurrent SUBAGENTS of one session.** In this seat's
  process `CLAUDE_CODE_SESSION_ID` is `e71cf460-…`, which equals this subagent's own scratchpad
  session directory rather than the driver's session id — evidence that the harness gives each agent
  its own value, but **one reading from inside one seat cannot settle it**, and I will not write
  down a guess about a harness (CLAUDE.md §4). **UNKNOWN.** It costs nothing to make it moot: a seat
  that files a row can pass its own identity, e.g.
  `ids.next_entry_id("AUT-PD", entries, session_id="S1-IDS")`. The driver can settle it in one
  command by comparing `CLAUDE_CODE_SESSION_ID` across two live seats.
- **Ambiguity the fix introduces, stated at full strength:** two rows may now share an ORDINAL
  (`AUT-PD-204-6b009680` and `AUT-PD-204-4ce79c2a`), so a bare cross-reference to "AUT-PD-204" in
  prose is ambiguous when that happens. This is the same trade `next_receipt` has made for receipts
  since 2026-08-27 and it is the cheaper half of the pair — an ambiguous reference is a reading
  problem, a duplicated id is a blocked push plus a five-file renumber. No guard reports it, because
  every place that could enforce one (`priority.py`, `health.py`) is governed and not mine.

## 7 · Every autonomy test that touches `ids` or `priority` — and a false red worth recording

The 17 files under `research/autonomy/tests` that import `ids`, `priority`, `claim`,
`proposal_dedup`, `push_guard` or `prepush_ledger_guard`:

```
263 passed in 81.95s     EXIT=0
```

⚠ **THE FIRST RUN OF THAT EXACT COMMAND WAS RED, AND IT WAS NOT THIS CHANGE.** It reported 6
failures and then died in `pytest_sessionfinish`:

```
AssertionError: the test run CHANGED tracked files that it did not find changed:
   M scripts/regenerate_aso_chain.sh
```

`scripts/regenerate_aso_chain.sh` is touched by no test in that list and by nothing I own — another
seat edited it while my run was in flight. **The re-run of the identical command over the identical
paths passed 263/263 with the guard silent**, so the six failures did not reproduce.
⛔ Recording it rather than deleting it, because it is a hazard the whole sprint shares: the
tracked-tree guard cannot distinguish "a test wrote to the tree" from "a sibling seat wrote to the
tree during the run", and every seat that runs pytest tonight can be handed a red build it did not
cause. It also **eats the failure list** — the guard raises inside `pytest_sessionfinish`, which
pre-empts pytest's own FAILURES section, so the first run never said WHICH six failed. A four-line
`pytest_runtest_logreport` plugin recovers that, and is how I established the re-run was clean.

⏱ `pytest research/autonomy/tests -q` (all 48 files, what preflight gate 15 runs) was started at
18:47Z, was still going 13m45s later — progressing, not hung: CPU time accumulating, load average
4.4 with several seats' suites and linters on the same box — and **I stopped it at 19:03Z rather
than leave a job running into a session that had ended.** It is a bonus check, not the scoped one,
and on a tree eleven seats are still mutating a whole-suite verdict is not a verdict about anything.
The driver runs preflight once, on a settled tree; that is where it means something. ⛔ Nothing here
claims that run passed — it was killed, not read.

## Ledger rows the driver should write

1. **AUT-PD-171 → `state: done`**, `last_evidence_utc: 2026-09-01`, owner released.
   `what` addendum: *"✅ DONE 2026-09-01 by sprint seat S1-IDS. Collision reproduced live on the
   unpatched trunk (two concurrent processes, one committed ledger, both handed AUT-PD-204) before
   anything was changed. `next_entry_id` now takes the same session discriminator `next_receipt`
   has carried since AUT-PROP-013; 9 tests red before / green after, 6/6 single-site mutations
   caught. ⚠ The discriminator separates SESSIONS; whether concurrent SUBAGENTS of one session get
   distinct `CLAUDE_CODE_SESSION_ID` values is UNKNOWN — pass `session_id=` explicitly from a seat."*
2. **NEW, `kind: process_defect`, `state: queued`, `cost_class: free`, serves `RT-AUTONOMY`** —
   *"`priority.merge` reads a ledger ordinal as `int(id.rsplit('-', 1)[-1])` (`priority.py:629`),
   which throws on a discriminated id and is swallowed by a bare `except ValueError: pass`, so the
   row silently stops de-conflicting the derived `AUT-NNN` counter. Measured 2026-09-01:
   `AUT-PD-204` yields 204, `AUT-PD-204-6b009680` yields nothing. Not a duplicate-id risk — the
   strings differ — but two families can now share an ordinal. One-line fix:
   `ids.parse_entry_id()`, which exists for this. GOVERNED path; needs an amendment record."*
3. **NEW, `kind: process_defect`, `state: queued`, `cost_class: free`, serves `RT-AUTONOMY`** —
   *"`.claude/skills/research-loop/SKILL.md` §2 step 10 still describes ledger entry ids as plain
   max+1 and shows `ids.next_entry_id('AUT-PD', entries)` without saying the id now carries a
   session discriminator. The call is correct as written (the session is read from the
   environment); the PROSE is the stale half, and the contract is what a cycle follows. GOVERNED."*

4. **NEW, `kind: process_defect`, `state: queued`, `cost_class: free`, serves `RT-AUTONOMY`** —
   *"`tracked_tree_guard.assert_tree_unchanged` raises in `pytest_sessionfinish`, which PRE-EMPTS
   pytest's own FAILURES section: a run it reds reports the count of failures and never says which
   ones. Measured 2026-09-01 (seat S1-IDS): a 17-file autonomy run showed 6 failures and died on
   `M scripts/regenerate_aso_chain.sh` — a file no test in the run touches, edited by a CONCURRENT
   SEAT mid-run — with no failure list; the identical re-run passed 263/263. Two defects in one:
   (a) the guard cannot distinguish a test writing to the tree from a sibling process writing to it,
   which makes every concurrent-seat run reddenable by something it did not do, and (b) it destroys
   the diagnostic that would settle which. A `pytest_runtest_logreport` reporter recovers (b) in
   four lines; (a) needs the guard to compare only paths the run could plausibly have touched, or to
   report rather than raise when the changed path is outside the tested tree. GOVERNED
   (`**/tests/**`); needs an amendment record."*

## Amendment record for the driver

⛔ I did not append this — `amendments.jsonl` is the driver's this sprint. Paste as one line;
replace `cycle_id` with the driver's real cycle id before appending.

```json
{"cycle_id": "<DRIVER-CYCLE-ID>", "utc": "2026-09-01T18:55:00Z", "path": "research/autonomy/tests/test_ids_cannot_collide.py", "what_changed": "The entry-id half of the file, 1 test -> 9 (file total 11 -> 19): two sessions reading one ledger get different ids; they still share the ordinal; the ordinal advances past a discriminated id (the mint-widened-but-scan-narrow defect); an absent session is REFUSED rather than minted bare, with unset and exported-empty distinguished; the session is read from the environment when the documented two-argument call site omits it; the discriminator is the session and not the moment; prefixes do not bleed across id families; every one of the 344 committed ledger ids still parses; and two concurrent filings merge into a ledger the real ranker accepts.", "old_value": "1 test, `test_entry_ids_are_allocated_over_the_whole_ledger_not_by_eye`, whose docstring asserted the collidable max+1 derivation as correct: 'THIS HALF IS HONESTLY STILL max+1 AND THE TEST SAYS SO.'", "new_value": "9 entry-id tests, 19 in the file, all passing; 9 red against the pre-fix module; 6/6 single-site mutations of the fix caught in scratch copies.", "why": "AUT-PD-171, sprint seat S1-IDS. `ids.next_receipt` has carried a session discriminator since AUT-PROP-013 and `ids.next_entry_id`, eleven lines below it, did not — one half of a pair, which collided five measured times on 2026-08-29 and cost one cycle two renumbers across five files.", "self_serving_check": "ANSWERED: NO, and the direction is one-way. Every added test CONSTRAINS the allocator further and none relaxes an existing bar: no test was deleted, no assertion weakened, no ratchet re-pinned, and the one rewritten test had asserted the DEFECT as intended behaviour. The change makes it harder, not easier, for a cycle to report success — a cycle with no readable session id can no longer mint a ledger id at all, where before it always got one. ⚠ The seat that wrote these tests was not blocked by them: it was blocked by nothing. ⚠ One assertion is load-bearing in a way worth naming: the refusal test asserts the TEXT of both env faults, not merely that a ValueError was raised, and that is the only reason M5 (a two-valued env read reporting an exported-empty session as unset) is caught rather than surviving — which fault it is decides who has to fix what."}
```
