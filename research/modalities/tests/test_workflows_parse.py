#!/usr/bin/env python3
"""Every file in .github/workflows must be parseable YAML, and must declare the triggers it thinks it has.

WHY THIS EXISTS. On 2026-07-25 the ternary watchdog was given an inline `python3 -c "..."` guard whose Python
lines sat at column 0. That dedents them out of the `run: |` block scalar and makes the whole workflow INVALID
YAML -- and GitHub's symptom is not a syntax error. It is:

    422 Workflow does not have 'workflow_dispatch' trigger

i.e. it reports a *missing trigger* on a file that plainly has one, and a `schedule:` cron on an unparseable
file simply NEVER FIRES, with no error anywhere. The guard intended to stop the watchdog acting on bad config
instead stopped the watchdog running at all, silently, for as long as it took to notice. `bash -n` on the
extracted step body cannot catch this, because the bash is fine -- it is the YAML around it that broke.

So: parse every workflow, and additionally assert that a workflow which sets a `schedule:` also keeps a
`workflow_dispatch:` (otherwise it cannot be exercised on demand, and a cron-only workflow that never fires is
indistinguishable from one that fires and finds nothing to do).

Pure stdlib apart from PyYAML, which is present on the runners and in the dev sandbox.
"""

import os
import re
import sys

try:
    import yaml
except ImportError:  # pragma: no cover
    print("SKIP: PyYAML unavailable")
    sys.exit(0)

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..")
WF_DIR = os.path.join(ROOT, ".github", "workflows")


def triggers_of(doc):
    """`on` is the YAML 1.1 boolean True, so it arrives as the key True, not the string 'on'."""
    if isinstance(doc, dict):
        for key in (True, "on", "On", "ON"):
            if key in doc:
                node = doc[key]
                if isinstance(node, dict):
                    return sorted(node.keys())
                if isinstance(node, list):
                    return sorted(node)
                return [node]
    return []


# THE 21,000-CHARACTER TEMPLATE CAP, and the condition that makes it bite.
# A `run:` block CONTAINING an expression (${{ ... }}) is compiled as a TEMPLATE, and the template is capped at
# 21,000 characters counting the raw indented block. Over the cap the whole workflow becomes unparseable: a
# dispatch fails with "Exceeded max expression length 21000" and a `schedule:` cron on that file simply NEVER
# FIRES. The ternary watchdog hit this at 23,453 chars and was silently disabled -- the SECOND time a parse
# failure disabled that one workflow (the first was column-0 Python inside the block scalar).
#
# A block with NO expression is a plain string and is NOT capped. This is measured, not assumed:
# gpu-ternary-fep-gcp.yml carries a 29,434-character run: block with zero ${{ }} and dispatches fine, all day.
# Flagging it would be a false alarm, and a gate that cries wolf is worse than no gate -- so the expression
# condition is part of the check.
#
# PyYAML parses an over-cap file happily, so the YAML check above cannot see this at all: it needs its own gate.
RUN_CAP = 21000
RUN_WARN = 18000


def run_block_sizes(path):
    """[(line_no, raw_chars, has_expression)] per `run:` block, sized as GitHub sees it (indentation included)."""
    lines = open(path).read().split("\n")
    out = []
    i = 0
    while i < len(lines):
        m = re.match(r"^(\s*)run:\s*[|>]", lines[i])
        if not m:
            i += 1
            continue
        key_indent = len(m.group(1))
        j = i + 1
        size = 0
        while j < len(lines):
            l = lines[j]
            if l.strip() and (len(l) - len(l.lstrip())) <= key_indent:
                break
            size += len(l) + 1
            j += 1
        out.append((i + 1, size, "${{" in "\n".join(lines[i + 1:j])))
        i = j
    return out


def main():
    if not os.path.isdir(WF_DIR):
        print("no .github/workflows directory — nothing to check")
        return 0
    names = sorted(n for n in os.listdir(WF_DIR) if n.endswith((".yml", ".yaml")))
    failed = 0
    for name in names:
        path = os.path.join(WF_DIR, name)
        try:
            doc = yaml.safe_load(open(path))
        except Exception as exc:  # noqa: BLE001
            print("FAIL %s: does NOT parse as YAML -> GitHub would report a MISSING TRIGGER, and any cron on "
                  "it would silently never fire.\n      %s: %s"
                  % (name, type(exc).__name__, str(exc).replace("\n", " ")[:300]))
            failed += 1
            continue
        trig = triggers_of(doc)
        if not trig:
            print("FAIL %s: parses, but declares no triggers at all" % name)
            failed += 1
            continue
        if "schedule" in trig and "workflow_dispatch" not in trig:
            print("FAIL %s: has a schedule but no workflow_dispatch — it cannot be exercised on demand, so a "
                  "cron that never fires looks identical to one with nothing to do" % name)
            failed += 1
            continue
        blocks = run_block_sizes(path)
        # only an EXPRESSION-bearing block is a template, and only a template is capped
        oversized = [(ln, sz) for ln, sz, expr in blocks if expr and sz >= RUN_CAP]
        if oversized:
            ln, sz = max(oversized, key=lambda x: x[1])
            print("FAIL %s: the `run:` block at line %d is %d raw chars, over GitHub's %d template cap — the "
                  "workflow will not parse, dispatch fails with 'Exceeded max expression length', and any cron "
                  "on it SILENTLY NEVER FIRES. Move the body into a script file (see "
                  "research/modalities/watchdog_run.sh), or remove the ${{ }} from it." % (name, ln, sz, RUN_CAP))
            failed += 1
            continue
        near = [(ln, sz) for ln, sz, expr in blocks if expr and sz >= RUN_WARN]
        warn = ""
        if near:
            ln, sz = max(near, key=lambda x: x[1])
            warn = "  [WARN run: block at line %d is %d chars, %d from the %d cap]" % (ln, sz, RUN_CAP - sz, RUN_CAP)
        print("PASS %s (%s)%s" % (name, ",".join(str(t) for t in trig), warn))

    print("\n%d workflow(s) checked, %d failed" % (len(names), failed))
    return 1 if failed else 0


def test_all_workflows_parse_and_declare_triggers():
    """pytest entry point: the existing suite already collects this directory, so wiring it here means the
    gate runs on every push without anyone remembering to add a step."""
    assert main() == 0, "a workflow does not parse as YAML — see the FAIL lines above"


if __name__ == "__main__":
    sys.exit(main())


# --- workflow_dispatch input cap -------------------------------------------------------------------
#
# WHY. GitHub caps `workflow_dispatch` at 25 inputs. Exceeding it does not fail the offending input --
# it makes the ENTIRE workflow file undispatchable: HTTP 422 on dispatch, plus a zero-job "failure" run
# that reads like a code failure and is not one. Lane 1 hit this on 2026-07-25; the repo had already
# had to retire a confirmed-no-op input (`constrain_ligand_ch`) once to make room for `direction`.
# fusion-cpu-extras.yml currently sits AT the cap, so the next input added there breaks it silently.
# Documented-but-unenforced is how this bites twice, so it is a test.
GITHUB_WORKFLOW_DISPATCH_INPUT_CAP = 25


def test_workflow_dispatch_inputs_within_github_cap():
    import glob

    offenders = []
    for path in sorted(glob.glob(os.path.join(WF_DIR, "*.yml"))):
        try:
            with open(path) as fh:
                doc = yaml.safe_load(fh)
        except Exception:
            continue  # parse failures are the other test's job, not this one's
        if not isinstance(doc, dict):
            continue
        # `on` is the YAML 1.1 boolean True, so it arrives as the key True (see triggers_of).
        node = None
        for key in (True, "on", "On", "ON"):
            if key in doc and isinstance(doc[key], dict):
                node = doc[key]
                break
        if node is None:
            continue
        dispatch = node.get("workflow_dispatch")
        if not isinstance(dispatch, dict):
            continue
        inputs = dispatch.get("inputs") or {}
        if len(inputs) > GITHUB_WORKFLOW_DISPATCH_INPUT_CAP:
            offenders.append((os.path.basename(path), len(inputs)))

    assert not offenders, (
        "workflow_dispatch input cap exceeded -- these files are UNDISPATCHABLE "
        f"(GitHub allows {GITHUB_WORKFLOW_DISPATCH_INPUT_CAP}): {offenders}. "
        "Remove an input before adding one; a 26th makes the whole file 422 with a zero-job run."
    )
