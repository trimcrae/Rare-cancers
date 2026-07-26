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


# --- every watch list a workflow guards on must EXIST and VALIDATE -------------------------------------
#
# WHY THIS SITS HERE, next to the parse gate, rather than in a watchdog-specific test file. The two failures
# are the same failure seen from opposite ends. A watchdog whose FILE does not parse never fires and reports
# nothing; a watchdog whose WATCH LIST does not validate fires, aborts on the config guard, and also protects
# nothing -- and in both cases the observable symptom is a repo that believes a leg is covered. The parse gate
# above catches the first. This catches the second, generically: any workflow that invokes
# `watchdog_validate.py <path>` is asserting that <path> is a real, valid watch list, so CI holds it to that
# on every push instead of discovering it at 3 AM on a billed leg.
#
# Note what is deliberately NOT asserted: that a list is non-empty. An empty or all-disabled list is a
# legitimate state -- nothing is running -- and a watchdog must be a no-op on it. Proving a specific unit is
# covered is a different question with a different tool (`--verify-armed`), because only something that knows
# which units were just launched can tell "nothing to watch" from "what I was watching went missing".
def test_every_watch_list_named_by_a_workflow_exists_and_validates():
    import glob
    import json as _json

    sys.path.insert(0, os.path.join(ROOT, "research", "modalities"))
    import watchdog_validate as wdv

    try:
        import vast_watchdog
        kinds = set(vast_watchdog.KINDS)
    except Exception:  # noqa: BLE001 — the registry is optional for this gate
        kinds = None

    referenced, problems = [], []
    for path in sorted(glob.glob(os.path.join(WF_DIR, "*.yml"))):
        text = open(path).read()
        for m in re.finditer(r"watchdog_validate\.py\s+(\S+\.json)", text):
            rel = m.group(1)
            referenced.append((os.path.basename(path), rel))
            full = os.path.join(ROOT, rel)
            if not os.path.exists(full):
                problems.append(f"{os.path.basename(path)} guards on {rel}, which DOES NOT EXIST -- the guard "
                                f"step fails every pass, so the watchdog never reaches its tick")
                continue
            try:
                doc = _json.load(open(full))
            except Exception as exc:  # noqa: BLE001
                problems.append(f"{rel} is not parseable JSON ({type(exc).__name__}) -- every pass aborts")
                continue
            bad = wdv.validate(doc, known_kinds=kinds)
            if bad:
                problems.append(f"{rel} does not validate: {bad}. The watchdog refuses to act on it, so "
                                f"anything it claims to cover is in fact uncovered.")

    assert referenced, ("no workflow references watchdog_validate.py at all -- either the watchdogs lost "
                       "their config guard or this check is looking in the wrong place")
    assert not problems, "\n".join(problems)


# --- `sort | head` under `set -e` + pipefail is a latent step-killer -------------------------------------
#
# WHY. `producer | head -N` makes `head` exit after N lines and close the pipe. The producer then dies on the
# write, `pipefail` propagates that non-zero status, and `set -e` kills the step. It is SIZE-DEPENDENT and so it
# does not show up in testing: while the producer's whole output fits in the 64 KB pipe buffer it finishes before
# `head` exits and nothing errors. Once the data grows past that, it does.
#
# It bit for real on 2026-07-26 (GH run 30202753766): mode=converge printed its lane path-shape listing, which
# looked complete, and then the step died with exit 2 because the lane had grown past 64 KB of sorted output. The
# exact status varies by coreutils build (2 on the runner, 141 reproducing locally) which makes it read like an
# unrelated failure. Reproduce: `set -eo pipefail; seq 1 200000 | sort -u | head -40 >/dev/null` -> 141.
#
# The fix is `| awk 'NR<=N'`, which reads to EOF and prints the first N, so there is no early close to fail on.
# NOT `|| true`, which would also swallow a genuine producer error.
#
# SCOPE, deliberately narrow, because a gate that cries wolf is worse than no gate — and the first draft of this
# one did exactly that. It matched the producer as a bare substring, so `--sort-by=~creationTimestamp` matched
# "sort" and it flagged four unrelated `gcloud ... list | head -1` lines in gcp-smoke.yml, gpu-bench-gcp.yml and
# gpu-rbfe-gcp.yml. Those are not the defect: the producer there emits a handful of image families, far under the
# 64 KB pipe buffer, and on multi-line pipelines the real producer is not even on the flagged line.
#
# So the match is on `sort` as a COMMAND TOKEN (start of line, after a pipe, or opening a substitution), which is
# the one producer measured to do this and the one that just cost a run. Only flagged when the step actually sets
# `pipefail`, and never when the pipeline already guards itself with `|| `.
_SIGPIPE_PRODUCER_RE = re.compile(r"(?:^|\||\$\(|&&|;)\s*sort(?:\s|$)")


def test_no_sort_into_head_under_pipefail():
    import glob

    offenders = []
    for path in sorted(glob.glob(os.path.join(WF_DIR, "*.yml"))):
        lines = open(path).read().split("\n")
        # crude but sufficient: pipefail anywhere in the file means at least one step sets it, and these
        # workflows set it per-step at the top of each `run:` block.
        if not any("pipefail" in l for l in lines):
            continue
        for i, l in enumerate(lines, 1):
            if "| head -" not in l and "|head -" not in l:
                continue
            if "|| " in l:                      # already guarded
                continue
            if l.lstrip().startswith("#"):      # a comment describing the hazard, not the hazard
                continue
            if not _SIGPIPE_PRODUCER_RE.search(l):
                continue
            offenders.append("%s:%d  %s" % (os.path.basename(path), i, l.strip()[:120]))

    assert not offenders, (
        "`<producer> | head -N` under `set -e` + pipefail is a size-dependent step-killer: head closes the pipe, "
        "the producer fails its write, pipefail+`set -e` kill the step, and it only starts happening once the "
        "output outgrows the 64 KB pipe buffer. Use `| awk 'NR<=N'` (reads to EOF, prints the first N) rather "
        "than `|| true`, which would also swallow a real producer error.\n  " + "\n  ".join(offenders))


# --- a task allowlist that drifts from its own input options is a SILENT downgrade -----------------------
#
# WHY. gpu-ternary-fep-vast.yml validates the dispatched task against a `case` allowlist and falls back to the
# free `test` task on no match — with a ::warning:: and a GREEN run. So a task present in the `workflow_dispatch`
# input's `options` but absent from the allowlist is dispatchable, looks like it ran, and does none of the work
# asked for. Caught while adding `converge` on 2026-07-26: the option was added and the allowlist was not, which
# would have produced a passing run that analysed nothing — the "reports success while measuring nothing" shape
# that research/modalities/ternary-lane-guard-audit-2026-07-25.md is entirely about.
#
# Checked generically: any workflow whose body contains a task/mode `case` allowlist AND declares matching
# dispatch options must cover every option.
def test_vast_task_allowlist_matches_the_input_options():
    path = os.path.join(WF_DIR, "gpu-ternary-fep-vast.yml")
    if not os.path.exists(path):
        print("SKIP: gpu-ternary-fep-vast.yml absent")
        return
    text = open(path).read()
    doc = yaml.safe_load(text)
    node = None
    for key in (True, "on", "On", "ON"):
        if key in doc and isinstance(doc[key], dict):
            node = doc[key]
            break
    options = ((node or {}).get("workflow_dispatch") or {}).get("inputs", {}).get("task", {}).get("options")
    assert options, "the task input lost its explicit options list — the allowlist can no longer be checked"

    m = re.search(r"case \"\$\{TASK:-test\}\" in\s*\n\s*([^)]+)\)", text)
    assert m, "could not find the task `case` allowlist — if it was restructured, update this gate"
    allowed = {t.strip() for t in m.group(1).split("|") if t.strip()}

    missing = [o for o in options if o not in allowed]
    assert not missing, (
        f"these dispatch options are NOT in the task allowlist and would SILENTLY fall back to `test` — a green "
        f"run that does none of the requested work: {missing}. Allowlist has {sorted(allowed)}.")
    # and the reverse, which is merely dead config but still a lie about what the workflow accepts
    extra = [a for a in sorted(allowed) if a not in options]
    assert not extra, (
        f"these tasks are in the allowlist but not dispatchable via the input options: {extra}. Either add them "
        f"to `options` or drop them from the `case`.")


def test_job_ids_are_valid_github_identifiers():
    """A workflow whose YAML parses can still be UNDISPATCHABLE, and the failure only shows at dispatch time.

    GitHub requires every job id to match `[A-Za-z_][A-Za-z0-9_-]*`. `yaml.safe_load` does not care, so a job
    named `5aks-prime` parsed cleanly here, passed every local check, and then the dispatch API answered
    HTTP 422 `The identifier '5aks-prime' is invalid` — for the WHOLE FILE, taking every other task in it
    down with it. Cost when this fired (2026-07-26): the RUNG 5a-KS legs could not be launched at all, on a
    workflow that looked green.
    """
    bad = []
    for fn in sorted(os.listdir(WF_DIR)):
        if not fn.endswith((".yml", ".yaml")):
            continue
        try:
            doc = yaml.safe_load(open(os.path.join(WF_DIR, fn)).read())
        except Exception:
            continue                      # malformed YAML is the other tests' problem, not this one's
        for jid in ((doc or {}).get("jobs") or {}):
            if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_-]*", str(jid)):
                bad.append(f"{fn}:{jid}")
    assert not bad, (
        f"these job ids are not valid GitHub identifiers, so their workflow is UNDISPATCHABLE (422) even "
        f"though the YAML parses: {bad}")
