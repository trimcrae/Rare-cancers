#!/usr/bin/env python3
"""How a test file in this directory declines to run when its dependency is absent.

WHY THIS EXISTS (2026-07-26, and it cost the whole suite). Every test here is written as a standalone
script — `python test_x.py`, module-level `check()` calls, `sys.exit(1)` at the bottom — AND is also
collected by `pytest research/modalities/tests`. Those two run modes disagree about what a module-level
`sys.exit(0)` means. Standalone it is "nothing to do, exit clean". Under pytest it is raised during
COLLECTION, where pytest has no handler for it: the run aborts with

    INTERNALERROR> SystemExit: 0
    no tests ran in 0.19s        (exit code 3)

Not "that file skipped" — NOTHING RAN. `test_5aks_pose.py` guards on gemmi, which `tests.yml` does not
pip-install, so its guard fired and took the entire modalities suite down with it. The suite is the gate in
front of the GPU launches, so a green-looking gate had stopped checking anything at all. Three other files
carried the identical guard and survived only because their dependency happened to still be installed.

The fix is to make the guard mode-aware: under pytest, skip the module the way pytest understands; run
standalone, exit clean the way the shell understands.
"""
import sys


def skip_module(reason):
    """Decline to run this module: a pytest module-level skip under pytest, a clean exit standalone.

    `"pytest" in sys.modules` is the discriminator rather than `import pytest` succeeding — pytest is
    installed inside `triskit23/ternary-fep` too, so importability says nothing about how this file is being
    run. Presence in `sys.modules` at the moment a test module is executing means pytest imported it.
    """
    print(f"SKIP: {reason}")
    if "pytest" in sys.modules:
        import pytest
        pytest.skip(reason, allow_module_level=True)
    sys.exit(0)
