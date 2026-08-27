"""Offline tests for the successor-session generator.

⛔ WHY THIS FILE EXISTS. `handoff.py` had no tests at all, and the thing it kept getting wrong was
not its logic but its COMPLETENESS: the prompt it generated named no environment, no source
repository and no receipt field, so the outgoing session had to append them by hand from its own
context — the exact context a generated handoff exists to avoid trusting. A missing constant in a
generated prompt is invisible until a successor is already running on it, which is the worst moment
to find out. Every assertion below is about what the payload MUST CARRY, never about its prose.
"""
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.path.insert(0, str(REPO / "research" / "autonomy"))

import handoff as H  # noqa: E402


def _payload():
    import io
    import contextlib
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        assert H.main(["--json"]) == 0
    return json.loads(buf.getvalue())


def test_the_json_payload_carries_the_whole_create_session_call():
    """The docstring promises the untestable half is 'one tool call with no judgement left in it'."""
    cs = _payload()["create_session"]
    for k in ("title", "prompt", "environment_id", "source_url", "source_revision"):
        assert cs.get(k), f"create_session payload is missing {k}"
    assert cs["environment_id"].startswith("env_"), cs["environment_id"]
    assert cs["source_url"].startswith("https://"), cs["source_url"]


def test_the_prompt_names_the_environment_and_the_source_it_must_be_spawned_into():
    """CYC-0017 had to hand-copy all three out of its own prompt. That is the defect."""
    p = H.build("because")
    assert H.SPAWN["environment_id"] in p
    assert H.SPAWN["source_url"] in p
    assert H.SPAWN["source_revision"] in p


def test_the_prompt_names_the_exact_receipt_field_health_py_reads():
    """`cycles_are_sized` reads `handoff.child_session_id` and nothing else; a receipt recording the
    same fact under another name is invisible to it, so the successor must be told the NAME."""
    assert H.CHILD_ID_FIELD == "handoff.child_session_id"
    assert H.CHILD_ID_FIELD in H.build("")
    assert _payload()["record_child_id_under"] == H.CHILD_ID_FIELD


def test_the_prompt_carries_no_findings_from_the_session_that_built_it():
    """The module's own rule: tell the successor WHERE TO LOOK, never WHAT IT WILL FIND."""
    p = H.build("the previous session reached its cycle cap")
    assert "READ THEM RATHER THAN ASKING ME WHAT HAPPENED" in p
    assert "priority.py --write" in p, "the successor must be told to re-score, not to trust the list"


def test_the_reason_is_carried_verbatim_and_a_missing_one_still_builds():
    assert "because the trunk was red" in H.build("because the trunk was red")
    assert "cycle cap" in H.build("")


def test_the_sync_command_cannot_leave_the_successor_on_a_stale_branch():
    """⛔ THE ONE COMMAND EVERY FIRED SESSION RUNS BEFORE IT KNOWS ANYTHING.

    A successor begins on whatever ref the runner checked out, and that can be a DETACHED HEAD.
    `git pull --rebase origin main` there rebases HEAD and leaves the `main` BRANCH untouched, so a
    later `git checkout main` lands on a stale commit while every command reports success. Measured
    2026-08-27: a session ran six tool calls 33 commits behind, re-scored a ledger in which the
    queue's top item did not exist, and graded loop health off receipts that were not the last three.

    ⭐ THE ASSERTION IS ABOUT THE PROPERTY, NOT THE STRING. The sync must move the BRANCH to the
    remote unconditionally, which is what `checkout -B <branch> origin/<branch>` does and what any
    `pull`-shaped command cannot promise from a detached head. Binding the property rather than
    listing forbidden commands is what stops the next equivalent formulation slipping through
    (paper-hardening §8b.2: a fix scoped to a list regresses at a sibling).
    """
    prompt = _payload()["create_session"]["prompt"]
    sync = [ln for ln in prompt.splitlines()
            if ln.startswith("    git ") or ln.startswith("    git -C")]
    assert sync, "the prompt no longer carries an indented sync command block"
    block = "\n".join(sync)
    assert "checkout" in block and "-B main origin/main" in block, (
        "the sync command must force the LOCAL BRANCH onto origin/main; a pull cannot do that "
        f"from a detached head. Got:\n{block}")
    assert "fetch" in block, "the sync must fetch before it resets the branch"
    # ⛔ And the successor must be told to CHECK the sha rather than trust the command's exit code:
    # a stale start looks exactly like a healthy one, which is why this failed silently.
    # ⚠ SCOPED TO THE SYNC SECTION, AND THAT SCOPING IS NOT COSMETIC. The first version of this
    # assertion searched the WHOLE prompt for "git log origin/main" and a mutation deleting this
    # instruction SURVIVED it — the phrase is also supplied, for a different purpose, by the
    # concurrent-cycle note much further down. A guard crediting a sentence that another sentence
    # happens to contain is a false witness, and it reads as coverage (paper-hardening §8b.1d).
    head = prompt.split("Then load the cycle contract")[0]
    assert "git log origin/main" in head, (
        "the prompt must tell the successor, IN THE SYNC SECTION, to verify its head against "
        "origin/main — an instruction further down the prompt does not reach a session that has "
        "already decided its start was healthy")


def test_the_sync_command_is_a_single_runnable_shell_line_per_statement():
    """A generated command a successor pastes must not arrive with a broken continuation.

    The fix above spans two source lines. If the backslash-continuation ever survives into the
    payload as a bare trailing backslash on its own line, the successor pastes a command that hangs
    waiting for more input — a failure that reads as 'the session never started'.
    """
    prompt = _payload()["create_session"]["prompt"]
    for ln in prompt.splitlines():
        assert not ln.rstrip().endswith("\\"), f"dangling continuation in generated prompt: {ln!r}"
