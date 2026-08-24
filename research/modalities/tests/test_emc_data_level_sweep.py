"""The data-level sweep's offline guards, wired into the suite that runs on every push.

⛔ WHY THIS THIN FILE EXISTS. `emc_data_level_sweep.py` carries its guards in `--selftest`, and the
only thing that invoked them was the `data-level-sweep` mode of `emc-expression-datasets.yml` — a
workflow that runs when somebody dispatches it by hand. So the guards protecting this module's
zeros were exercised on the days we happened to run a sweep, and on no other day, while `tests.yml`
— the suite that runs on EVERY push and is the authority — never touched them.

That is the wrong way round for these particular guards. The defect they exist to catch is silent
by construction: `_bucket` deciding that the SKELETAL myxoid chondrosarcoma is the extraskeletal
one, or a partially-read census reporting itself as a complete negative, changes no output shape
and raises no error. It changes a number, in the direction of a cohort that is not there or a route
closed that is still open. A guard that only runs when someone remembers to dispatch a workflow is
not protecting the next session from that.

⚠ It deliberately adds no assertions of its own. `selftest()` owns them, next to the code and its
evidence; duplicating them here would create a second home for the same fact (CLAUDE.md §1).
"""

import importlib.util
import os

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MODULE = os.path.join(os.path.dirname(HERE), "emc_data_level_sweep.py")


def _load():
    spec = importlib.util.spec_from_file_location("emc_data_level_sweep", MODULE)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_the_module_is_present_to_be_tested():
    # ⛔ A missing module must FAIL, never skip. A guard that cannot run is not a guard that passed.
    assert os.path.exists(MODULE), f"{MODULE} is missing; its guards are therefore UNRUN"


def test_every_offline_guard_group_passes(capsys):
    """`selftest()` returns 0 only if all 15 guard groups hold. It fetches nothing."""
    mod = _load()
    rc = mod.selftest()
    out = capsys.readouterr().out
    assert rc == 0, f"emc_data_level_sweep --selftest failed:\n{out}"


def test_an_empty_cache_cannot_emit_a_biological_verdict():
    """The single property worth restating here, because it is the one CLAUDE.md §4 exists for.

    ⚠ This is not a duplicate of a `selftest()` assertion so much as a tripwire on the ENTRY POINT:
    if `derive` were ever refactored to tolerate a missing cache by filling in defaults, every other
    guard would still pass while the module began emitting verdicts about data it never read.
    """
    mod = _load()
    arms = mod.derive({})["arms"]
    for name, arm in arms.items():
        assert arm["verdict"] == "NOT_RUN", (
            f"an empty inputs cache produced verdict {arm['verdict']!r} for arm {name!r}")


@pytest.mark.parametrize(
    "label,expected",
    [
        ("Extraskeletal myxoid chondrosarcoma", "emc"),
        ("extraskeletal myxoid chondrosarcoma, grade 2", "emc"),
        ("EWSR1::NR4A3 fusion positive", "emc"),
        ("skeletal myxoid chondrosarcoma of the femur", "confusable"),
        ("Chondrosarcoma", "confusable"),
        ("Chondroblastoma", "confusable"),
        ("Osteosarcoma", None),
        ("osteochondrosarcoma", None),
    ],
)
def test_the_skeletal_and_extraskeletal_tumours_never_collapse_into_one_bucket(label, expected):
    """⛔ THE ONE-OF-A-PAIR DEFECT, PINNED WHERE `tests.yml` WILL SEE IT.

    These two tumours are different diseases with different drivers, and each of their names is a
    substring of a term on the other's list. Getting the split backwards does not error — it
    silently converts 112 skeletal chondrosarcomas into an EMC cohort that does not exist, or files
    real EMC cases under the skeletal tumour and reports a route closed that is open.
    """
    assert _load()._bucket(label) == expected
