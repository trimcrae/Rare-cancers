#!/usr/bin/env python3
"""No test module may abort pytest COLLECTION by exiting from an import guard.

THE DEFECT THIS PINS (2026-07-26). `test_5aks_pose.py` ended its `except ImportError` handler with a
module-level `sys.exit(0)`. That is correct for a standalone `python test_x.py` run and catastrophic under
pytest: SystemExit raised while a module is being imported for collection is not caught as a skip, it is an
INTERNALERROR, and the run ends `no tests ran in 0.19s` with exit code 3. The whole modalities suite — the
guard gate in front of every GPU launch — reported nothing for six consecutive pushes while appearing to be
a normal red test.

What makes this worth a test rather than a fix: THREE other files carried the identical guard and were fine
only by luck, because numpy and PyYAML happen to be in `tests.yml`'s pip list while gemmi is not. Every one
of them is one dependency change away from the same total outage, and the failure gives no hint which file
caused it unless you read the traceback to the bottom.

So the rule is checked structurally: a handler that catches ImportError must not call `sys.exit` — it calls
`skip_module()` from `_skip_guard`, which does the right thing in both run modes. The `sys.exit(1)` at the
bottom of every file is untouched by this; that one runs after collection, in the module body proper, and is
how a standalone run reports failure.
"""
import ast
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

fails = []


def check(cond, msg):
    print(("  ok   " if cond else "  FAIL ") + msg)
    if not cond:
        fails.append(msg)


def _handler_catches_importerror(handler):
    """Does this `except ...:` clause catch ImportError (or a superclass of it)?"""
    names = []
    t = handler.type
    if t is None:                                    # bare `except:` catches everything
        return True
    for node in ast.walk(t):
        if isinstance(node, ast.Name):
            names.append(node.id)
        elif isinstance(node, ast.Attribute):
            names.append(node.attr)
    return any(n in ("ImportError", "ModuleNotFoundError", "Exception", "BaseException") for n in names)


def _calls(node, dotted):
    """Every call to `dotted` (e.g. 'sys.exit' or 'skip_module') anywhere under `node`."""
    hits = []
    for sub in ast.walk(node):
        if not isinstance(sub, ast.Call):
            continue
        f = sub.func
        if isinstance(f, ast.Attribute) and f.attr == dotted.split(".")[-1]:
            hits.append(sub)
        elif isinstance(f, ast.Name) and f.id == dotted.split(".")[-1]:
            hits.append(sub)
    return hits


# Every way a handler can end the process instead of the module. `sys.exit` is the one that actually
# happened; the rest are the same bug with different spelling, and a test that only knew the first would
# wave the next one through.
KILLERS = ("sys.exit", "exit", "quit", "_exit")


def _terminators(handler):
    hits = [c for name in KILLERS for c in _calls(handler, name)]
    hits += [n for n in ast.walk(handler)
             if isinstance(n, ast.Raise) and n.exc is not None
             and "SystemExit" in ast.dump(n.exc)]
    return hits


FILES = sorted(f for f in os.listdir(HERE) if f.startswith("test_") and f.endswith(".py"))
check(len(FILES) > 20, f"the scan actually found the test files ({len(FILES)} of them), not an empty dir")

print("== no import guard ends the PROCESS at module scope")
# A guard has exactly two legitimate shapes, and the test allows both:
#   * DECLINE the module     -> skip_module(), which is a pytest skip under pytest and a clean exit outside;
#   * SET A FLAG and go on   -> `HAVE_X = False` + `pytest.mark.skipif`, which never terminates anything.
# What is banned is the third shape: killing the interpreter while pytest is importing the file.
n_guards, n_declines = 0, 0
for name in FILES:
    tree = ast.parse(open(os.path.join(HERE, name)).read(), filename=name)
    for node in tree.body:                                   # MODULE SCOPE ONLY: collection-time code
        if not isinstance(node, ast.Try):
            continue
        for handler in node.handlers:
            if not _handler_catches_importerror(handler):
                continue
            n_guards += 1
            check(not _terminators(handler),
                  f"{name}:{handler.lineno} import guard does not end the process — a module-scope "
                  f"SystemExit aborts pytest COLLECTION and takes the ENTIRE suite down, not just this file")
            if _calls(handler, "skip_module"):
                n_declines += 1
check(n_guards >= 5, f"the scan found the real guards to check ({n_guards}), so it is not vacuously passing")
check(n_declines >= 4,
      f"{n_declines} guards decline via skip_module — the helper is actually in use, so this test is not "
      "just asserting the absence of a call nobody makes")

print("== skip_module itself picks its behaviour from the RUN MODE, not from importability")
import _skip_guard    # noqa: E402
src = open(os.path.join(HERE, "_skip_guard.py")).read()
check('"pytest" in sys.modules' in src,
      "the discriminator is pytest's presence in sys.modules — pytest is installed in the FEP image too, so "
      "'can I import pytest' would wrongly skip a standalone run inside the container")
check("allow_module_level=True" in src,
      "the pytest branch uses a module-level skip; pytest.skip() without it raises at import and is the same "
      "collection failure wearing a different exception")

# Behaviour, not just shape: standalone, it must still exit 0 the way a shell run expects.
import subprocess    # noqa: E402
r = subprocess.run([sys.executable, "-c",
                    f"import sys; sys.path.insert(0, {HERE!r}); "
                    "from _skip_guard import skip_module; skip_module('deliberate'); print('UNREACHABLE')"],
                   capture_output=True, text=True)
check(r.returncode == 0, "standalone: skip_module exits 0 (a missing optional dep is not a test failure)")
check("SKIP: deliberate" in r.stdout and "UNREACHABLE" not in r.stdout,
      "standalone: it prints the reason and stops the module — it does not fall through into the tests")

print()
if fails:
    print(f"FAILED {len(fails)}: {fails}")
    sys.exit(1)
print(f"all skip-guard tests passed ({n_guards} guards across {len(FILES)} files)")
