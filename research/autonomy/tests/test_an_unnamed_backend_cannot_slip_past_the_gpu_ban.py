#!/usr/bin/env python3
"""⛔ A `Backend` SUBCLASS THAT DECLARES NO `name` MUST REFUSE, NOT LAUNCH.

MEASURED 2026-09-02, in answer to "is the no-GPU ban actually codified?". `Backend.__init_subclass__`
wraps every subclass's `submit` with the ban check, and skipped it for any backend whose name is in
`_GPU_BAN_EXEMPT_BACKENDS`. That set held `{"mock", "abstract"}` and the read was
`getattr(self, "name", "abstract")` — so a subclass that never set `name` took the DEFAULT, landed on
the exempt list, and `.submit()` returned without the ban being consulted once.

⚠ NOTHING SHIPPED WAS EXPOSED. All eight concrete backends declare a name — checked at the time, not
assumed — so this was a hole in the prospective case, which is precisely the case the hook exists for:
its own comment promises "an EIGHTH backend is gated on the day it is written", and an eighth backend
that forgot one attribute was not.

★ THE DEFECT CLASS, not the line: a default that makes an UNCLASSIFIABLE case PASS. `mock` is exempt
because it creates nothing, contacts nothing and bills nothing; "I could not identify this backend"
is a different statement and must never share an answer with it.

⚠ MUTATION AUDIT, REPORTED HONESTLY BECAUSE ONE MUTANT SURVIVED. Three mutations were run against a
COPY: reverting the exempt set to `{"mock", "abstract"}` -> CAUGHT; reverting the default back to
`getattr(self, "name", "abstract")` -> SURVIVED; reverting BOTH, which is the original bypass exactly
-> CAUGHT.
★ THE SURVIVOR IS NOT A GAP IN THIS TEST AND WRITING A TEST TO KILL IT WOULD BE WRONG. The two edits
are defence in depth and only their CONJUNCTION is observable: with `abstract` off the exempt list, an
unnamed backend fails the membership check whatever the default resolves to. A test that failed on a
change with no behavioural consequence would be pinning the implementation rather than the behaviour,
which is how a suite starts costing more than it catches (CLAUDE.md §6 on the tier budget).

⛔ `mock` STAYING EXEMPT IS HALF THE TEST. A guard that reds on true input is the one people switch
off (`paper-hardening` §8b.1), and blanket-refusing here would break every dry run.
"""
import dataclasses
import os
import sys

import pytest

# ⛔ THIS FILE LIVES IN `research/autonomy/tests/` AND NOT BESIDE `gpu_backend.py`, DELIBERATELY.
# `research/modalities/tests/conftest.py` carries an autouse fixture that NEUTRALISES `gpu_ban.read_ban`
# so the mechanics tests can exercise launch paths — and its own comment says it is "SCOPED TO THE
# MECHANICS, NOT TO THE GATE", naming this directory as where the gate itself is tested. A test of the
# ban placed under that conftest passes for the wrong reason: the ban never runs.
HERE = os.path.dirname(os.path.abspath(__file__))
AUT = os.path.dirname(HERE)
for p in (os.path.join(os.path.dirname(AUT), "modalities"), AUT):
    if p not in sys.path:
        sys.path.insert(0, p)

import gpu_backend  # noqa: E402
from gpu_ban import GPUSpendProhibited  # noqa: E402


def _spec():
    return gpu_backend.JobSpec(**{f.name: "x" for f in dataclasses.fields(gpu_backend.JobSpec)})


def _backend(name):
    """A complete concrete Backend. `name` is omitted entirely when None."""
    body = {m: (lambda self, *a, **k: "LAUNCHED") for m in gpu_backend.Backend.__abstractmethods__}
    if name is not None:
        body["name"] = name
    return type("ProbeBackend", (gpu_backend.Backend,), body)


@pytest.mark.parametrize("name", [None, "abstract", "", "vast", "gcp", "a-backend-added-tomorrow"])
def test_a_backend_that_is_not_the_mock_refuses_to_submit(name):
    with pytest.raises(GPUSpendProhibited):
        _backend(name)().submit(_spec())


def test_the_mock_backend_still_runs_because_it_bills_nothing():
    assert _backend("mock")().submit(_spec()) == "LAUNCHED"


def test_the_exempt_set_names_only_the_mock():
    assert gpu_backend.Backend._GPU_BAN_EXEMPT_BACKENDS == frozenset({"mock"}), (
        "adding a name here exempts a backend from the no-GPU ban; `abstract` was on this list and "
        "was the bypass this file was written for"
    )
