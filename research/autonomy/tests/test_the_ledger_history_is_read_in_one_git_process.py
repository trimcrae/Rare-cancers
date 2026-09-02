#!/usr/bin/env python3
"""The ledger walk must cost ONE git process, and must be identical to the walk it replaced.

⛔⛔ WHAT THIS GUARDS, MEASURED RATHER THAN ARGUED. `ledger_versions()` is the commit loop's single
biggest cost and it scales with the repository's COMMIT COUNT, not with anything a test counts.
Seat S6-COMMITLOOP counted it with a shim in front of `git` on 2026-09-01: **48 230 of gate 13's
50 270 git calls — 96 % — were `git show <sha>:research-ledger.json`**, ~130 complete walks per gate
run, ~55 % of a 446 s gate. The fix has two halves and this file guards both:

  1. the memo (`_VERSIONS_CACHE`), which cut 130 walks to ~3 and took gate 13 to **54.0 s**;
  2. `git cat-file --batch`, which makes ONE walk cost one process instead of one per commit —
     **6.71 s -> 2.76 s over 380 versions, byte-identical output**, measured 2026-09-02.

⛔ NEITHER HALF CHANGES AN ASSERTION, AND THAT IS EXACTLY WHY THEY NEED A GUARD. A rewrite that goes
back to a `git show` per commit is green everywhere, prints the same verdicts, and silently returns
this gate to minutes. That is the `subagent_width` shape — a rule measured by nothing — which
CLAUDE.md §1 records this repository already paying for.

⚠ THE FIXTURES BUILD REAL GIT REPOSITORIES, for the reason the sibling file gives: the derivation
from git IS the part that could be wrong, so mocking git out would leave it untested.
"""

from __future__ import annotations

import datetime
import json
import os
import subprocess
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

import stuck_clock as S  # noqa: E402

T0 = datetime.datetime(2026, 8, 20, 12, 0, tzinfo=datetime.timezone.utc)
LEDGER = "ledger.json"


def _run(repo, *args, when=None):
    env = dict(os.environ)
    if when is not None:
        stamp = when.strftime("%Y-%m-%dT%H:%M:%S+0000")
        env["GIT_AUTHOR_DATE"] = env["GIT_COMMITTER_DATE"] = stamp
    env.setdefault("GIT_AUTHOR_NAME", "test")
    env.setdefault("GIT_AUTHOR_EMAIL", "test@example.invalid")
    env.setdefault("GIT_COMMITTER_NAME", "test")
    env.setdefault("GIT_COMMITTER_EMAIL", "test@example.invalid")
    subprocess.run(["git", "-C", str(repo)] + list(args), check=True, env=env,
                   capture_output=True, text=True)


@pytest.fixture
def history(tmp_path):
    """A repo with eight committed ledger versions, the fourth deliberately unparseable."""
    repo = tmp_path / "repo"
    repo.mkdir()
    _run(repo, "init", "-q")
    for i in range(8):
        when = T0 + datetime.timedelta(hours=i)
        if i == 3:
            body = '{"entries": [ THIS IS NOT JSON'
        else:
            # ⛔ `ensure_ascii=False` IS THE WHOLE FIXTURE, NOT A STYLE CHOICE. `json.dumps`
            # defaults to escaping non-ASCII as `\uXXXX`, which is pure ASCII — so the first
            # version of this fixture wrote a blob whose byte count and character count were
            # EQUAL, and the character-framing mutation it exists to catch passed. Measured
            # 2026-09-02: with the escapes, 0 of 8 tests noticed; without them, this one does.
            body = json.dumps({"entries": [
                {"id": "AUT-X", "state": "queued", "what": "step %d — naïve, résumé, ✅" % i}]},
                ensure_ascii=False)
        (repo / LEDGER).write_text(body, encoding="utf-8")
        _run(repo, "add", LEDGER, when=when)
        _run(repo, "commit", "-q", "-m", "v%d" % i, when=when)
    return repo


def _reference(repo):
    """The pre-2026-09-02 implementation: one `git show` per commit. The thing we must still equal."""
    log = S._git(["log", "--follow", "--format=%H %ct", "--", LEDGER], str(repo))
    out = []
    for line in reversed(log.strip().splitlines()):
        if not line.strip():
            continue
        sha, _, ts = line.partition(" ")
        try:
            entries = json.loads(S._git(["show", "%s:%s" % (sha, LEDGER)], str(repo))).get(
                "entries", [])
        except Exception:
            continue
        out.append((sha, {e["id"]: e for e in entries if isinstance(e, dict) and e.get("id")},
                    datetime.datetime.fromtimestamp(int(ts), datetime.timezone.utc)))
    return out


def _walk(repo):
    S._VERSIONS_CACHE.clear()
    return [(v.sha, v.rows, v.when) for v in S.ledger_versions(str(repo), LEDGER)]


# --------------------------------------------------------------------------------------------
# the walk is unchanged
# --------------------------------------------------------------------------------------------


def test_the_batched_walk_equals_the_per_commit_walk_it_replaced(history):
    """⛔ THE WHOLE SAFETY ARGUMENT FOR THE OPTIMISATION, AND IT INCLUDES THE UNPARSEABLE VERSION.

    A half-written ledger in history must still be SKIPPED rather than read as an empty ledger —
    "every row was deleted and re-created" resets every clock in one step, which is the silent
    direction. The fixture plants one on purpose so the equality is not asserted over clean input
    only.
    """
    got, ref = _walk(history), _reference(history)
    assert got == ref
    assert len(got) == 7, "the unparseable version must be skipped, not counted and not fatal"


def test_a_blob_with_non_ascii_survives_the_byte_framed_reader(history):
    """⛔ THE ONE BUG A BATCH READER GETS WRONG SILENTLY. `cat-file --batch` frames bodies by BYTE
    count; a reader that decodes before framing desynchronises at the first multi-byte character and
    every subsequent version is garbage — with no error, which is how a wrong list reaches a verdict.
    """
    rows = [v[1] for v in _walk(history)]
    assert any("naïve, résumé, ✅" in r["AUT-X"]["what"] for r in rows), (
        "the non-ASCII fixture text did not survive the walk — the batch reader is framing by "
        "characters instead of bytes")


def test_the_walk_does_not_spawn_one_git_show_per_commit(history, monkeypatch):
    """⭐ THE COST PROPERTY ITSELF. Counted, because it is invisible to every other assertion."""
    seen = []
    real = S._git
    monkeypatch.setattr(S, "_git", lambda args, repo: (seen.append(args[0]), real(args, repo))[1])
    _walk(history)
    shows = [a for a in seen if a == "show"]
    assert not shows, (
        "%d `git show` process(es) for 8 commits — the walk is back to one fork per commit. Over "
        "this repository's real history that is 372 forks and ~7.5 s per walk." % len(shows))


def test_an_unreadable_batch_falls_back_to_git_show_rather_than_to_a_shorter_history(history,
                                                                                    monkeypatch):
    """⛔ FAIL TO THE SLOW ANSWER, NEVER TO A WRONG ONE.

    A batch that cannot run — git too old, a truncated stream — must cost the old speed and nothing
    else. The dangerous alternative is a walk that silently returns fewer versions, because a
    SHORTER history moves the horizon forward and makes stuck rows look younger than they are: the
    detector talked out of its own finding, which is the failure `stuck_clock` exists for.
    """
    monkeypatch.setattr(S, "_cat_file_batch", lambda revs, repo: {})
    assert _walk(history) == _reference(history)


# --------------------------------------------------------------------------------------------
# the batch reader's protocol
# --------------------------------------------------------------------------------------------


def test_a_missing_rev_does_not_desynchronise_the_revs_after_it(history):
    """⛔ `missing` HAS NO BODY. A reader that skips a body anyway loses every following blob.

    This is the single most dangerous parse error available here: it does not raise, it returns
    plausible-looking text for the wrong commit.
    """
    log = S._git(["log", "--format=%H", "--", LEDGER], str(history)).split()
    revs = ["%s:%s" % (log[0], LEDGER),
            "0000000000000000000000000000000000000000:%s" % LEDGER,
            "%s:%s" % (log[1], LEDGER)]
    got = S._cat_file_batch(revs, str(history))
    assert revs[1] not in got, "a rev git cannot resolve must be absent, not empty-stringed"
    for rev in (revs[0], revs[2]):
        assert got[rev] == S._git(["show", rev.split(":")[0] + ":" + LEDGER], str(history)), (
            "the blob after the missing rev is wrong — the reader consumed a body that was never "
            "written")


def test_the_batch_reader_returns_empty_rather_than_raising_when_git_refuses(tmp_path):
    """Not a git repository at all: `{}`, so the caller's fallback runs."""
    assert S._cat_file_batch(["HEAD:x"], str(tmp_path)) == {}
    assert S._cat_file_batch([], str(tmp_path)) == {}


# --------------------------------------------------------------------------------------------
# interning: one object per distinct row state
# --------------------------------------------------------------------------------------------


def test_an_unchanged_row_is_the_same_object_across_versions(history):
    """⭐ THE MEMO'S PRICE, PINNED. Without this the cache holds one copy of every row for every
    commit — measured on the real history: 84 792 row objects for 2 319 distinct states, 126 MB
    retained per process against 8 MB, four times over under `pytest -n 4`, and growing with every
    commit this loop makes. That is the same accretion the memo was written to stop, in a different
    currency."""
    # ⭐ THE FIXTURE IS THE REAL-WORLD SHAPE: two commits in which ONE row moves and the other does
    # not. That is what makes the redundancy 36.6x on the live ledger — the ordinary commit changes
    # one row and re-serialises the other 144 unchanged.
    when = T0 + datetime.timedelta(hours=50)
    for i in range(2):
        (history / LEDGER).write_text(json.dumps({"entries": [
            {"id": "AUT-X", "state": "queued", "what": "frozen"},
            {"id": "AUT-Y", "state": "queued", "what": "moving %d" % i}]}, ensure_ascii=False),
            encoding="utf-8")
        _run(history, "add", LEDGER, when=when + datetime.timedelta(hours=i))
        _run(history, "commit", "-q", "-m", "frozen%d" % i, when=when + datetime.timedelta(hours=i))
    last_two = _walk(history)[-2:]
    assert last_two[0][1]["AUT-Y"] != last_two[1][1]["AUT-Y"], (
        "the fixture must produce two DIFFERENT committed versions, or nothing here is tested")
    assert last_two[0][1]["AUT-X"] is last_two[1][1]["AUT-X"], (
        "the unchanged row is a second copy in the memo. On the real ledger that is 84 792 row "
        "objects for 2 319 distinct states — 126 MB retained per process against 8 MB.")


def test_a_changed_row_is_not_shared_with_the_version_before_it(history):
    """⛔ THE DANGEROUS DIRECTION. Sharing an object across a version where the row DID change would
    make `compute_clocks` see no change at all — every clock frozen, every stall invisible, and the
    module reporting the deadest rows as the liveliest, which is the failure it exists for."""
    versions = _walk(history)
    for (_, before, _), (_, after, _) in zip(versions, versions[1:]):
        if "AUT-X" in before and "AUT-X" in after and before["AUT-X"] != after["AUT-X"]:
            assert before["AUT-X"] is not after["AUT-X"]
            return
    raise AssertionError("the fixture produced no changed row — this test asserted nothing")


def test_interning_moves_no_clock(history):
    """The verdicts, field by field, against a walk with interning switched off."""
    S._VERSIONS_CACHE.clear()
    interned = S.compute_clocks(S.ledger_versions(str(history), LEDGER))
    S._VERSIONS_CACHE.clear()
    plain = S.compute_clocks([S.Version(sha=sha, when=when,
                                        rows={k: dict(v) for k, v in rows.items()})
                              for sha, rows, when in _reference(history)])
    assert set(interned) == set(plain)
    for key in interned:
        a, b = interned[key], plain[key]
        assert (a.stuck_at, a.updated_at, a.created_at, a.censored, a.tried, a.attempts,
                a.identity_changed, a.state, a.unclassified_fields) == \
               (b.stuck_at, b.updated_at, b.created_at, b.censored, b.tried, b.attempts,
                b.identity_changed, b.state, b.unclassified_fields), key


# --------------------------------------------------------------------------------------------
# the memo
# --------------------------------------------------------------------------------------------


def test_the_walk_is_memoised_within_one_head(history, monkeypatch):
    """130 walks per gate run is what this cut to ~3. Asserted by counting the `log` calls."""
    S._VERSIONS_CACHE.clear()
    seen = []
    real = S._git
    monkeypatch.setattr(S, "_git", lambda args, repo: (seen.append(args[0]), real(args, repo))[1])
    first = S.ledger_versions(str(history), LEDGER)
    second = S.ledger_versions(str(history), LEDGER)
    assert first is second, "the second call must return the memo, not a fresh walk"
    assert seen.count("log") == 1, "the history was walked %d times" % seen.count("log")


def test_a_new_commit_invalidates_the_memo(history):
    """⛔ THE MEMO IS KEYED ON HEAD, and a process that commits between two reads is the ORDINARY
    case here. A cache keyed on (repo, path) alone would hand the second read a pre-commit answer.
    """
    S._VERSIONS_CACHE.clear()
    before = S.ledger_versions(str(history), LEDGER)
    when = T0 + datetime.timedelta(hours=99)
    (history / LEDGER).write_text(json.dumps({"entries": [{"id": "AUT-NEW", "state": "queued"}]}),
                                  encoding="utf-8")
    _run(history, "add", LEDGER, when=when)
    _run(history, "commit", "-q", "-m", "new", when=when)
    after = S.ledger_versions(str(history), LEDGER)
    assert len(after) == len(before) + 1
    assert "AUT-NEW" in after[-1].rows
