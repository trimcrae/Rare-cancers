"""A never-started host must be excluded for EVERY lane; a slow one must not be.

2026-07-27: machine 1569 accepted TEN step-1 relaunches and started none of them — every one logged
`did not reach intended=running after 8 attempts`, and eight sat `cur_state=stopped` with an empty
`status_msg` for 26-33 min. The condemn site recorded that at the DEFAULT `scope="lane"`, so the shared
cross-lane set never learned it and every other lane was still free to rent the same dead box. A host that
never starts has infinite realised $/ns and is therefore invisible to $/ns ranking, so it keeps winning
selection — which is exactly how it won ten times.

The opposite error is just as real, which is why this is two tests and not one: `pricing.md` A.1 WITHDREW the
broad "low gpu_util means a bad host" rule after a metadynamics leg's low utilisation turned out to be
PLUMED's CPU-side bias and the same host ran at 74 % on the very next phase. Sharing a throughput verdict
would re-adopt the withdrawn rule by the back door and discard good hosts for everybody.
"""
from __future__ import annotations

import inspect
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest  # noqa: E402


# ⛔⛔ THESE TESTS PIN THE **RETIRED** DURABLE EXCLUSION LIST, DELIBERATELY (2026-07-31).
# trimcrae retired it that day — *"You've gotta just stop doing the blacklist. It seems like it only ever
# bites us in the ass and clearing it always makes things better."* — and `vast_machine_blacklist` now reads
# and writes NOTHING unless `VAST_DURABLE_EXCLUSIONS=1`. The machinery below (capacity-vs-host classification,
# wave scoping, the per-unit condemnation guard, clear/snapshot/retire) is kept and kept TESTED rather than
# deleted, because the retirement is a switch and a switch that flips back into untested code is a trap. The
# behaviour that is now live by default is pinned separately, in `test_blacklist_retired.py`.
@pytest.fixture(autouse=True)
def _durable_exclusions_on(monkeypatch):
    monkeypatch.setenv("VAST_DURABLE_EXCLUSIONS", "1")


def _monitor_src() -> str:
    import congeneric_fanout_vast as cfv
    return inspect.getsource(cfv.mode_monitor)


def test_the_default_scope_is_lane_so_sharing_is_always_a_deliberate_act():
    """`publish` must never guess. The value of the split is that somebody looked at the reason and decided."""
    import congeneric_fanout_vast as cfv
    assert inspect.signature(cfv._record_exclusion).parameters["scope"].default == "lane"


def test_a_host_that_NEVER_STARTED_is_published_cross_lane():
    """The empty-status_msg branch — a container that never executed — must set host scope."""
    src = _monitor_src()
    assert "if stuck_sig:" in src, "the scope branch was restructured — re-point this test"
    idx = src.index("if stuck_sig:")
    window = src[idx:idx + 700]
    assert "never started" in window and '_scope = "host"' in window, (
        "the never-started condemn must publish HOST-scoped so every lane sees it — machine 1569 took ten "
        "relaunches because it did not")
    # ⚠ ASSERT THE ARGUMENT, NOT THE LITERAL CALL TEXT (loosened 2026-07-29). This pinned the exact string
    # `_record_exclusion(s3, bucket, mid, why, scope=_scope)`, so adding a NEW keyword to the call — `unit=`,
    # which carries the per-unit blame guard's evidence — failed this test while the behaviour it guards was
    # untouched. What matters is that the condemn passes the computed scope through rather than defaulting.
    import ast
    call = next(n for n in ast.walk(ast.parse(src))
                if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
                and n.func.id == "_record_exclusion"
                and any(k.arg == "scope" for k in n.keywords))
    scope_kw = next(k for k in call.keywords if k.arg == "scope")
    assert isinstance(scope_kw.value, ast.Name) and scope_kw.value.id == "_scope"


def test_the_HARD_BACKSTOP_condemns_but_stays_LANE_scoped():
    """A box that reported activity and merely never finished is weaker evidence than a never-executed
    container. Wrongly publishing a healthy host permanently removes cheap supply for every lane, and the
    cheapest capacity on this board is exactly these cards — so the shared set stays reserved."""
    src = _monitor_src()
    # Anchor on the WHY STRING, not the explanatory comment above it, or the window lands in prose.
    idx = src.index("hard backstop {STUCK_START_HARD_MIN")
    window = src[idx:idx + 600]
    assert '_scope = "lane"' in window, "the hard backstop must NOT be shared cross-lane"


def test_the_backstop_bounds_the_OTHER_signature_so_no_stopped_box_is_nudged_forever():
    """The strike system fixed an unbounded nudge for EMPTY status_msg only. `s1f-00-cw_ev_5nh2` sat stopped
    carrying 'Successfully loaded <image>', which dodges that test and could never escalate. Both signatures
    must now have a ceiling."""
    import congeneric_fanout_vast as cfv
    assert cfv.STUCK_START_HARD_MIN > cfv.STUCK_START_MIN, "the backstop must be looser than the primary test"
    # Far beyond any real image pull (a ~6 GiB pull runs 20-40 min on a cheap host), so it cannot reap one.
    assert cfv.STUCK_START_HARD_MIN >= 120, cfv.STUCK_START_HARD_MIN
    src = _monitor_src()
    assert "or hard_stop" in src, "the condemn condition no longer admits the backstop"


def test_a_merely_SLOW_host_stays_lane_scoped():
    """The starved-host rule mixes the machine with THIS workload; pricing.md A.1 withdrew that reasoning
    once already, so it must not be exported."""
    src = _monitor_src()
    assert "healthy band 70-95%" in src, "the starved-host reason changed — re-point this test"
    idx = src.index("healthy band 70-95%")
    window = src[max(0, idx - 900):idx + 400]
    assert 'scope="host"' not in window, (
        "a gpu_util shortfall is a property of the machine PAIRED WITH THIS WORKLOAD and must stay lane-scoped")


def test_the_shared_set_is_only_ever_additive_and_never_blocks_a_launch():
    """An unreadable shared set must degrade to the lane's own list. An optimisation that can block a launch
    is a liability, and this one runs on the path that rents GPUs."""
    import vast_machine_blacklist as vmb
    assert vmb.load(None, None) == ([], {})
    assert vmb.union(["7"], None, None) == ["7"]
    assert vmb.publish(None, None, "1569", "why", "step1_fanout") is False
