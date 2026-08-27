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
