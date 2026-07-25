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
        print("PASS %s (%s)" % (name, ",".join(str(t) for t in trig)))

    print("\n%d workflow(s) checked, %d failed" % (len(names), failed))
    return 1 if failed else 0


def test_all_workflows_parse_and_declare_triggers():
    """pytest entry point: the existing suite already collects this directory, so wiring it here means the
    gate runs on every push without anyone remembering to add a step."""
    assert main() == 0, "a workflow does not parse as YAML — see the FAIL lines above"


if __name__ == "__main__":
    sys.exit(main())
