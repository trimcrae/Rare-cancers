"""THE PIN THAT STOPS `null != '0'` FROM COMING BACK.

WHAT HAPPENED (2026-07-27). The money-spending step of `step1-fanout-autoscale.yml` was guarded by

    if: ${{ github.event.inputs.release_fanout != '0' }}     # "place unless explicitly disabled"

and was skipped on every `schedule:` tick for 1 h 47 m across seven green runs, while the fleet decayed
11 -> 5 with ten checkpointed units waiting for a host. A `schedule:` event carries no `inputs` context, so
the operand is `null`; Actions comparison is loose, both sides cast to number, `null -> 0` and `'0' -> 0`,
and the guard evaluated `0 != 0` = FALSE. The only trace was a grey `skipped` badge, which is why nothing
alarmed.

WHAT THIS FILE ASSERTS. Not that the incident is fixed — that is `step1-fanout-autoscale.yml`'s own
business. It asserts that the CHECKER still recognises the shape, still clears the shapes that are
deliberately fine, and above all still parses rather than greps: `step1-fanout-autoscale.yml` deliberately
CONTAINS the broken expression as evidence, in a comment and in an `env:` var that prints its real value on
every run, and a checker that flagged those would push someone to delete the evidence.

Each test names the property it pins, because a checker whose tests only assert "returns a list" is a
checker that can be quietly weakened.
"""

import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..")))

import lint_optional_input_guards as lint  # noqa: E402

REPO_ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
WORKFLOW_DIR = os.path.join(REPO_ROOT, ".github", "workflows")


def write_workflow(tmp_path, name, text):
    path = tmp_path / name
    path.write_text(text, encoding="utf-8")
    return str(path)


def bugs(path, allowlist=()):
    findings, _ = lint.scan_workflow(path, allowlist=allowlist)
    return [f for f in findings if f.severity == lint.SEVERITY_BUG and not f.allowlisted]


# ---------------------------------------------------------------------------------------
# The known-bad shape, verbatim
# ---------------------------------------------------------------------------------------

KNOWN_BAD = """
name: known bad
on:
  schedule:
    - cron: "*/10 * * * *"
  workflow_dispatch:
    inputs:
      release_fanout:
        description: "1 = place units, 0 = do not"
        default: "1"
jobs:
  tick:
    runs-on: ubuntu-latest
    steps:
      - name: Terminus-gated fan-out
        if: ${{ github.event.inputs.release_fanout != '0' }}
        run: echo spend money
"""


def test_the_incident_shape_is_flagged(tmp_path):
    """The exact expression that disabled the fan-out must be a BUG, defaults and all.

    Note the input DOES declare `default: "1"`. That default is exactly what made the bug
    invisible in review — it is applied on a dispatch and NOT on a schedule, where the whole
    `inputs` context is absent.
    """
    path = write_workflow(tmp_path, "known-bad.yml", KNOWN_BAD)
    found = bugs(path)
    assert len(found) == 1, [f.render() for f in found]
    assert found[0].expression == "github.event.inputs.release_fanout != '0'"
    assert found[0].job == "tick"
    assert "Terminus-gated fan-out" in found[0].step
    assert "schedule" in found[0].why
    assert "$GITHUB_OUTPUT" in found[0].should_be


def test_the_incident_shape_is_flagged_via_the_inputs_context_too(tmp_path):
    """`inputs.x` is null on a schedule for the same reason `github.event.inputs.x` is."""
    path = write_workflow(
        tmp_path,
        "known-bad-inputs-context.yml",
        KNOWN_BAD.replace("github.event.inputs.", "inputs."),
    )
    assert len(bugs(path)) == 1


def test_equality_against_zero_is_flagged_too(tmp_path):
    """`== '0'` is the same trap inverted: TRUE exactly when nobody typed anything."""
    path = write_workflow(tmp_path, "eq-zero.yml", KNOWN_BAD.replace("!= '0'", "== '0'"))
    found = bugs(path)
    assert len(found) == 1
    assert "fires on precisely the unattended trigger" in found[0].why


def test_numeric_and_boolean_comparands_are_the_same_trap(tmp_path):
    """`!= 0` and `!= false` coerce identically to `!= '0'` — same bug, different clothes."""
    for comparand in ("0", "false"):
        path = write_workflow(
            tmp_path,
            f"bare-{comparand}.yml",
            KNOWN_BAD.replace("!= '0'", f"!= {comparand}"),
        )
        assert len(bugs(path)) == 1, comparand


# ---------------------------------------------------------------------------------------
# The shapes that must NOT be flagged
# ---------------------------------------------------------------------------------------

REQUIRED_INPUT = """
name: required input
on:
  workflow_dispatch:
    inputs:
      release_fanout:
        description: "1 = place units, 0 = do not"
        required: true
jobs:
  tick:
    runs-on: ubuntu-latest
    steps:
      - name: Terminus-gated fan-out
        if: ${{ github.event.inputs.release_fanout != '0' }}
        run: echo spend money
"""


def test_required_input_on_a_dispatch_only_workflow_is_not_flagged(tmp_path):
    """A required input on a dispatch-only workflow cannot be null. Not a finding."""
    path = write_workflow(tmp_path, "required.yml", REQUIRED_INPUT)
    assert bugs(path) == []


def test_required_input_IS_flagged_once_an_inputless_trigger_appears(tmp_path):
    """`required: true` is a promise about the dispatch FORM, not about a cron.

    This is the half of the rule that review keeps getting wrong, so it is asserted directly:
    add a `schedule:` and the same required input is null on every scheduled run.
    """
    text = REQUIRED_INPUT.replace(
        "on:\n  workflow_dispatch:",
        'on:\n  schedule:\n    - cron: "*/10 * * * *"\n  workflow_dispatch:',
    )
    path = write_workflow(tmp_path, "required-plus-schedule.yml", text)
    assert len(bugs(path)) == 1


DEFAULTED_WITH_OR = """
name: or-defaulted
on:
  schedule:
    - cron: "*/10 * * * *"
  workflow_dispatch:
    inputs:
      release_fanout:
        default: "1"
      fleet_branch:
        default: "main"
jobs:
  tick:
    runs-on: ubuntu-latest
    env:
      GIT_BRANCH: ${{ github.event.inputs.fleet_branch || 'main' }}
    steps:
      - name: Terminus-gated fan-out
        if: ${{ (github.event.inputs.release_fanout || '1') != '0' }}
        run: echo spend money
"""


def test_or_defaulting_is_not_flagged(tmp_path):
    """`||` short-circuits on null, which is why `fleet_branch` worked while `release_fanout` did not.

    Both forms appear here: the fallback used as a value, and the fallback wrapped in the very
    comparison that failed without it.
    """
    path = write_workflow(tmp_path, "or-default.yml", DEFAULTED_WITH_OR)
    assert bugs(path) == []


def test_comparison_against_empty_string_is_the_null_test_not_a_victim_of_it(tmp_path):
    """`X != ''` MEANS "was a value supplied" — null and '' cast alike, so it reads true.

    Flagging this idiom would be the checker's own false-positive mode, and it is the most
    common shape in this repo's dispatch-only diagnostics.
    """
    text = KNOWN_BAD.replace("!= '0'", "!= ''")
    path = write_workflow(tmp_path, "empty-idiom.yml", text)
    assert bugs(path) == []


def test_explicit_empty_guard_alongside_the_zero_test_is_not_flagged(tmp_path):
    """The sanctioned inline fix: say what absent means, in the expression itself."""
    text = KNOWN_BAD.replace(
        "!= '0'",
        "!= '0' || github.event.inputs.release_fanout == ''",
    )
    path = write_workflow(tmp_path, "explicit.yml", text)
    assert bugs(path) == []


def test_non_numeric_comparand_is_reported_but_does_not_fail_the_build(tmp_path):
    """`== 'launch'` casts to NaN and is false for null — usually the intended default-off.

    Reported as a NOTE so the intent can be graded, never as a BUG, because a checker that
    fails the build on the ordinary mode-switch idiom would be turned off within a day.
    """
    text = KNOWN_BAD.replace("!= '0'", "== 'launch'")
    path = write_workflow(tmp_path, "mode-switch.yml", text)
    findings, _ = lint.scan_workflow(path)
    assert bugs(path) == []
    assert any(f.severity == lint.SEVERITY_NOTE for f in findings)


# ---------------------------------------------------------------------------------------
# Parse, don't grep
# ---------------------------------------------------------------------------------------

COMMENT_ONLY = """
name: incident writeup
on:
  schedule:
    - cron: "*/10 * * * *"
  workflow_dispatch:
    inputs:
      release_fanout:
        default: "1"
jobs:
  tick:
    runs-on: ubuntu-latest
    steps:
      # THE MECHANISM. The step was guarded by `if: ${{ github.event.inputs.release_fanout != '0' }}`,
      # which on a null inputs context is `0 != 0` = FALSE. Do not restore it.
      - name: Terminus-gated fan-out
        if: ${{ always() }}
        run: echo spend money
"""


def test_the_expression_inside_a_comment_is_invisible(tmp_path):
    """This is why the checker parses YAML instead of grepping.

    The repo's incident writeups quote the broken expression on purpose. A grep-based checker
    flags the documentation and pressures someone into deleting the evidence.
    """
    path = write_workflow(tmp_path, "comment-only.yml", COMMENT_ONLY)
    findings, _ = lint.scan_workflow(path)
    assert findings == []


def test_an_unwrapped_condition_is_still_analysed(tmp_path):
    """`if:` accepts a bare expression with no `${{ }}`; the trap does not care about braces."""
    text = KNOWN_BAD.replace(
        "if: ${{ github.event.inputs.release_fanout != '0' }}",
        "if: github.event.inputs.release_fanout != '0'",
    )
    path = write_workflow(tmp_path, "unwrapped.yml", text)
    assert len(bugs(path)) == 1


def test_env_value_is_a_note_unless_a_condition_reads_it(tmp_path):
    """An `env:` holding the comparison gates nothing by itself — but it does once an `if:` reads it."""
    inert = KNOWN_BAD.replace(
        "        if: ${{ github.event.inputs.release_fanout != '0' }}\n",
        "        env:\n          FLAG: ${{ github.event.inputs.release_fanout != '0' }}\n",
    )
    path = write_workflow(tmp_path, "env-inert.yml", inert)
    assert bugs(path) == []
    findings, _ = lint.scan_workflow(path)
    assert [f.severity for f in findings] == [lint.SEVERITY_NOTE]

    live = inert.replace(
        "      - name: Terminus-gated fan-out\n",
        "      - name: Terminus-gated fan-out\n        if: ${{ env.FLAG }}\n",
    )
    path = write_workflow(tmp_path, "env-live.yml", live)
    assert len(bugs(path)) == 1


# ---------------------------------------------------------------------------------------
# Coercion semantics — the arithmetic the whole checker rests on
# ---------------------------------------------------------------------------------------


@pytest.mark.parametrize(
    "op,literal,expected",
    [
        ("!=", "0", False),  # the incident
        ("==", "0", True),
        ("!=", "", False),
        ("==", "", True),
        ("!=", "1", True),
        ("==", "1", False),
        ("==", "launch", False),  # NaN comparand
        ("!=", "launch", True),
        ("==", "true", False),  # 'true' is a string, not a boolean: casts to NaN
    ],
)
def test_null_coercion_table(op, literal, expected):
    """`null` casts to 0; a string casts by numeric parse, else NaN; `!=` is `not (==)`."""
    node = lint.Literal("string", literal, literal)
    assert lint.compare_null_against_literal(op, node) is expected


def test_string_to_number_matches_the_actions_cast():
    assert lint.string_to_number("0") == 0.0
    assert lint.string_to_number("") == 0.0
    assert lint.string_to_number("  ") == 0.0
    assert lint.string_to_number("1") == 1.0
    assert lint.string_to_number("0.0") == 0.0
    assert lint.string_to_number("launch") != lint.string_to_number("launch")  # NaN


# ---------------------------------------------------------------------------------------
# The allowlist must cost a reason
# ---------------------------------------------------------------------------------------


def test_an_allowlist_entry_without_a_reason_cannot_be_constructed():
    """A bare suppression is not expressible. That is the point of the mechanism."""
    with pytest.raises(ValueError):
        lint.Allow(path="x.yml", expression="inputs.a != '0'", reason="")
    with pytest.raises(ValueError):
        lint.Allow(path="x.yml", expression="inputs.a != '0'", reason="ok")


def test_an_allowlisted_finding_is_reported_but_does_not_fail(tmp_path):
    path = write_workflow(tmp_path, "known-bad.yml", KNOWN_BAD)
    allow = (
        lint.Allow(
            path="known-bad.yml",
            expression="github.event.inputs.release_fanout != '0'",
            reason="Synthetic fixture used by the checker's own tests; it gates nothing real.",
        ),
    )
    assert bugs(path, allowlist=allow) == []
    findings, _ = lint.scan_workflow(path, allowlist=allow)
    assert findings[0].allowlisted
    assert "Synthetic fixture" in findings[0].allow_reason


def test_the_shipped_allowlist_covers_only_the_evidence_occurrence():
    """Every shipped entry must carry a reason, and the only one is step1's printed evidence."""
    assert len(lint.ALLOWLIST) == 1
    entry = lint.ALLOWLIST[0]
    assert entry.path == "step1-fanout-autoscale.yml"
    assert "EVIDENCE" in entry.reason


# ---------------------------------------------------------------------------------------
# The real tree
# ---------------------------------------------------------------------------------------


@pytest.mark.skipif(not os.path.isdir(WORKFLOW_DIR), reason="no workflows checked out")
def test_the_live_workflow_tree_is_clean():
    """The sweep itself, as CI runs it. A new guard of this shape turns this test red."""
    assert lint.main(["lint_optional_input_guards.py", WORKFLOW_DIR]) == 0


@pytest.mark.skipif(not os.path.isdir(WORKFLOW_DIR), reason="no workflows checked out")
def test_every_expression_in_the_live_tree_parses():
    """An unparsed expression is a blind spot, not a pass. Fail loudly if the grammar drifts."""
    unparsed = []
    for path in lint.iter_workflow_files([WORKFLOW_DIR]):
        _, doc = lint.read_workflow(path)
        if doc is None:
            continue
        for site in lint.collect_sites(doc):
            try:
                lint.parse_expression(site.expression)
            except lint.ExpressionSyntaxError as exc:
                unparsed.append(f"{os.path.basename(path)}: {site.expression!r} -- {exc}")
    assert unparsed == []
