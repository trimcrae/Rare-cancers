"""⛔ THE STALL GUARD, TESTED AGAINST THE STALLS IT WAS WRITTEN FOR — AND AGAINST THE SHAPES IT MUST
NOT PUNISH.

`promised-work-at-turn-end.sh` refuses a stop when three things hold together: the final message
promises work, HEAD did not move since the previous stop, and no live "In flight" board was printed.

⚠ WHY THE NEGATIVE CASES ARE HALF THIS FILE. A guard that reds on true input is one its reader
learns to loosen (`paper-hardening` §8b.1), and the most dangerous false positive here is a turn
that DISPATCHES work and reports it: CLAUDE.md §1 requires the foreground to stay free and
`inflight-reporting` requires the board, so a hook that fired on that shape would push every session
toward blocking waits — the exact opposite of the rule it serves.

⚠ AND THE POSITIVE CASES ARE VERBATIM, NOT INVENTED. All three are real closing lines from
2026-09-01, the session that prompted trimcrae's "Did you stall again?". The first version of the
hook was written from memory of them and caught ONE of the three, because it required `Fixing …:` to
end a line and `I'll` to begin one. A guard fitted to its author's recollection of a defect is
fitted to the recollection.
"""
import json
import os
import subprocess

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
HOOK = os.path.join(REPO, ".claude", "hooks", "promised-work-at-turn-end.sh")
STATE = os.path.join(REPO, ".git", "emc-hooks", "promised-work-last-head")

REFUSES = 2  # the harness convention: exit 2 + stderr blocks the stop


def _head():
    return subprocess.run(["git", "-C", REPO, "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()


def test_the_hook_finds_its_repository_without_being_told_where_it_is(tmp_path):
    """⛔⛔ THE GUARD THAT COULD NOT RUN, AND ITS OWN TESTS SAID SO BEFORE ANYONE ELSE DID.

    ⚠ MEASURED IN CI RUN 33513565956, hours after this file landed: the three cases above failed on
    a GitHub runner with `returncode=0, stdout='', stderr=''` — a silent exit, not a wrong verdict.
    The hook read `REPO="${CLAUDE_PROJECT_DIR:-/home/user/Rare-cancers}"` and `cd`'d into it, and a
    runner has neither, so it returned 0 before reading a single line of the transcript.
    ★ EVERY ASSERTION IN THIS FILE WAS CORRECT AND THE HOOK WAS NEVER REACHED — "a guard that cannot
    run is not a guard that passed", inside a hook written the same hour to stop a different rule
    that nothing measured.
    ⛔ SO THIS TEST DRIVES IT THE WAY THE RUNNER DOES: `CLAUDE_PROJECT_DIR` removed from the
    environment entirely. Without it the hook must still find the repository from its own path, and
    a stall must still be refused.
    """
    env = {k: v for k, v in os.environ.items() if k != "CLAUDE_PROJECT_DIR"}
    os.makedirs(os.path.dirname(STATE), exist_ok=True)
    with open(STATE, "w") as fh:
        fh.write(_head())
    transcript = tmp_path / "t.jsonl"
    transcript.write_text(json.dumps({
        "type": "assistant",
        "message": {"role": "assistant",
                    "content": [{"type": "text", "text": "Next: regenerate the chain and commit."}]},
    }) + "\n", encoding="utf-8")
    r = subprocess.run(["bash", HOOK], input=json.dumps({"transcript_path": str(transcript)}),
                       capture_output=True, text=True, env=env)
    assert r.returncode == REFUSES, (
        "with CLAUDE_PROJECT_DIR unset the hook did not reach its own repository, so it passed by "
        f"not looking (rc={r.returncode}, stderr={r.stderr[:200]!r})")


def _run(tmp_path, text, head_prev=None):
    """Drive the hook with one assistant message and a chosen 'HEAD at last stop'."""
    os.makedirs(os.path.dirname(STATE), exist_ok=True)
    prev = head_prev if head_prev is not None else _head()
    with open(STATE, "w") as fh:
        fh.write(prev)
    transcript = tmp_path / "t.jsonl"
    transcript.write_text(json.dumps({
        "type": "assistant",
        "message": {"role": "assistant", "content": [{"type": "text", "text": text}]},
    }) + "\n", encoding="utf-8")
    return subprocess.run(
        ["bash", HOOK], input=json.dumps({"transcript_path": str(transcript)}),
        capture_output=True, text=True)


@pytest.mark.parametrize("closing", [
    "Next: regenerate the chain, gate, commit, mint and publish a new archive version.",
    "Fixing both: the client gets a bounded retry with backoff, and the ledger row gets corrected.",
    "The lesson stands. I'll build the Stop hook that measures it.",
])
def test_a_real_stall_is_refused(tmp_path, closing):
    r = _run(tmp_path, closing)
    assert r.returncode == REFUSES, f"the hook let this stall through:\n{closing}"
    assert "PROMISED WORK" in r.stderr


@pytest.mark.parametrize("closing", [
    # ⛔ THE ONE THAT MUST NEVER FIRE: work dispatched, foreground free, board printed.
    "Round 28 is dispatched.\n\nIn flight: 5 blind seats, running, ~20 min, $0 — their completion "
    "wakes this session.",
    "Committed and pushed as f6cdb9360. Two documentation blockers fixed. Nothing in flight.",
    # Describing what a LATER cycle should do is required by the receipt contract, not a promise.
    "AUT-PROP-055 is queued. A resuming session should re-check the draft, then repoint the paper.",
    "The publish is yours: publication-authority.json excludes PUB-ASO from the aiXiv grant.",
])
def test_an_honest_ending_is_not_refused(tmp_path, closing):
    r = _run(tmp_path, closing)
    assert r.returncode == 0, f"the hook fired on a correct ending:\n{closing}\n{r.stderr[:400]}"


def test_work_that_landed_exempts_the_turn_whatever_the_prose_says(tmp_path):
    """A promise beside a real commit is a plan for the NEXT step, not a stall."""
    r = _run(tmp_path, "Next: regenerate the chain and commit.", head_prev="0" * 40)
    assert r.returncode == 0


def test_it_cannot_trap_a_session(tmp_path):
    """`stop_hook_active` is the harness saying it has already re-entered once."""
    os.makedirs(os.path.dirname(STATE), exist_ok=True)
    with open(STATE, "w") as fh:
        fh.write(_head())
    transcript = tmp_path / "t.jsonl"
    transcript.write_text(json.dumps({
        "type": "assistant",
        "message": {"role": "assistant", "content": [{"type": "text", "text": "Next: do the thing."}]},
    }) + "\n", encoding="utf-8")
    r = subprocess.run(["bash", HOOK], capture_output=True, text=True, input=json.dumps(
        {"transcript_path": str(transcript), "stop_hook_active": True}))
    assert r.returncode == 0, "a Stop hook that fires when already active can loop a session forever"


def test_a_first_run_with_no_baseline_says_nothing(tmp_path):
    """CLAUDE.md §4: an absent reading is not a reading of absence. A fresh container has no
    previous HEAD, so it cannot know whether anything landed."""
    if os.path.exists(STATE):
        os.remove(STATE)
    transcript = tmp_path / "t.jsonl"
    transcript.write_text(json.dumps({
        "type": "assistant",
        "message": {"role": "assistant", "content": [{"type": "text", "text": "Next: do the thing."}]},
    }) + "\n", encoding="utf-8")
    r = subprocess.run(["bash", HOOK], capture_output=True, text=True,
                       input=json.dumps({"transcript_path": str(transcript)}))
    assert r.returncode == 0
    with open(STATE, "w") as fh:  # leave the baseline as we found it for the rest of the suite
        fh.write(_head())
