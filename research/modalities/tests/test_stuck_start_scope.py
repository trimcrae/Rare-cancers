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


def _monitor_src() -> str:
    import congeneric_fanout_vast as cfv
    return inspect.getsource(cfv.mode_monitor)


def test_the_default_scope_is_lane_so_sharing_is_always_a_deliberate_act():
    """`publish` must never guess. The value of the split is that somebody looked at the reason and decided."""
    import congeneric_fanout_vast as cfv
    assert inspect.signature(cfv._record_exclusion).parameters["scope"].default == "lane"


def test_a_host_that_NEVER_STARTED_is_published_cross_lane():
    src = _monitor_src()
    marker = "never started"
    assert marker in src, "the condemn reason no longer says 'never started' — re-point this test"
    # The condemn site is the one whose `why` is built from the never-started signature.
    idx = src.index(marker)
    window = src[idx:idx + 2600]
    assert 'scope="host"' in window, (
        "the never-started condemn must publish HOST-scoped so every lane sees it — machine 1569 took ten "
        "relaunches because it did not")


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
