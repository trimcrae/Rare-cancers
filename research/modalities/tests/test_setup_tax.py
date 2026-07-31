"""THE SETUP TAX PARSER — a cache whose effectiveness is unobservable is one we cannot tell from an absent one.

trimcrae, 2026-07-31: *"What do we have to do to get back to the good throughput we had in prior sessions?"*
The comparison rules out the obvious answer: the step 1 fan-out churned HARDER than 5a-KS (208 rentals for 19
units, median 7 each, max 37) and still landed 18 of 19. What differs is how much of each rental is
PRODUCTIVE — fan-out median 1.62 h per rental against <= 1.00 h here, against a ~28 min time-to-first-commit,
so 25 % of this lane's sessions bank nothing at all.

⚠ THE TRI-STATE IS THE WHOLE POINT. HIT / MISS / ABSENT are three different findings:
  * HIT    — the work was skipped.
  * MISS   — the cache is configured and cold; pre-bake it.
  * ABSENT — the line was never printed, so we cannot say. That is a REPORTING defect, not a cost, and
             folding it into MISS would invent a number while folding it into HIT would hide one.
CLAUDE.md §4: an absent reading is not a reading of absence.
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import setup_tax as tax  # noqa: E402

HIT_LOG = """[tvast] stage cache HIT -> s3://b/p/stage.tar
[tvast] pre-equil cache HIT -> s3://b/p/pe.tar (relaxed complex.pdb + ligands.sdf overlaid)
  [spot-safe] SETUP RESTORED from cache s3://b/p/setupcache/leg__nagl__v1pe — skipped the ~460s solvate
[spot-driver] restore: production took 12.4s
[restore] production: list_committed returned 7 generation(s) in 0.9s
[restore] production iter 1360 gen abcdef12 fetched 41231344 B in 11.2s
[timing] iter 5: 33.9 s/iter
"""

MISS_LOG = """[tvast] stage cache MISS -> staging leg from 1abc
[tvast] pre-equil cache MISS -> running ternary_preequil.py (1.0 ns)
  [spot-safe] SETUP begin (solvate + parameterize the hybrid system)…
  [spot-safe] SETUP done in 512s
"""

SILENT_LOG = "[tvast] recipe+engine sha256[:12]=c22be929a990 branch=main\n"


def test_a_hit_is_read_as_a_hit_on_every_cache():
    p = tax.parse_log(HIT_LOG)
    assert p["caches"] == {"stage": True, "preequil": True, "setup": True}
    assert p["setup_restored_from"].endswith("v1pe")
    assert p["setup_built"] is False and p["setup_seconds"] is None


def test_a_miss_is_read_as_a_miss_and_carries_what_it_cost():
    p = tax.parse_log(MISS_LOG)
    assert p["caches"] == {"stage": False, "preequil": False, "setup": False}
    assert p["setup_built"] is True and p["setup_seconds"] == 512.0
    assert "rebuilt the hybrid system ON THE RENTED GPU" in tax.verdict(p)


def test_a_log_that_says_NOTHING_is_ABSENT_and_never_a_hit_or_a_miss():
    p = tax.parse_log(SILENT_LOG)
    assert p["caches"] == {"stage": None, "preequil": None, "setup": None}
    v = tax.verdict(p)
    assert v.count("ABSENT(unobservable)") == 3
    assert "HIT" not in v and "MISS" not in v


def test_the_fail_fast_branch_is_distinguished_from_an_ordinary_miss():
    """`RBFE_REQUIRE_PRIMED_SETUP=1` makes a cold setup cache KILL the leg rather than rebuild on the GPU.
    That is a dead rented host, not a slow one, and it needs its own line in the readout."""
    p = tax.parse_log("  [spot-safe] SETUP CACHE MISSING at s3://b/p/setupcache/leg__nagl__v1pe — refusing\n")
    assert p["caches"]["setup"] is False
    assert p["setup_cache_missing"].endswith("v1pe")
    assert "FAILS FAST" in tax.verdict(p)
    assert p["setup_built"] is False, "a fail-fast leg did NOT pay for a rebuild — do not bill it for one"


def test_the_restore_timings_are_split_into_list_and_fetch():
    """The 5a-KS wedge was inside one of those two and the log could not say which — that is the whole reason
    both lines exist."""
    p = tax.parse_log(HIT_LOG)
    assert p["restore_seconds"] == {"production": 12.4}
    assert p["restore_list"] == [{"phase": "production", "n_gen": 7, "seconds": 0.9}]
    assert p["restore_fetch"][0]["bytes"] == 41231344


def test_the_iteration_rate_is_the_median_not_the_first():
    p = tax.parse_log("[timing] iter 1: 90.0 s/iter\n[timing] iter 2: 34.0 s/iter\n[timing] iter 3: 33.0 s/iter\n")
    assert p["s_per_iter"] == 34.0, "the first iteration includes warm-up cost and is not the rate"


@pytest.mark.parametrize("text", ["", "\n\n", "garbage without any anchor at all"])
def test_it_never_raises_on_a_log_it_does_not_understand(text):
    """This runs over archived logs from every past protocol version. A parser that throws on an old format
    would take the whole forensic down with it."""
    p = tax.parse_log(text)
    assert set(p["caches"].values()) == {None}
