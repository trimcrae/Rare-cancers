"""The launcher must not buy a GPU it has no way to switch off.

A GCP VM cannot delete itself — the in-VM EXIT trap runs and GCE refuses the call (measured 2026-07-27,
`research/compute/gcp-gpu-facts.md` §6) — and the only reaper is the ternary watchdog's DONE branch, which
loops over the ENABLED entries of `ternary-watch.json`. So the watch entry is not bookkeeping: **it is the
teardown mechanism.** With none, a detached leg runs to its create-time `--max-run-duration` (72 h on the
on-demand branch) holding `GPUS_ALL_REGIONS = 1` — every GCP GPU job on the account — and burning expiring
trial credit, with a red workflow as the only signal.

These tests pin the refusal AND its two escape valves in the correct directions: a *near-miss* entry must be
refused (it would census the wrong commit prefix), and a *checked-out-ref* divergence must only warn (the
watchdog reads main, so the reap is unaffected).
"""

from __future__ import annotations

import json
import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import gcp_launch_guard as glg  # noqa: E402

REPO = pathlib.Path(__file__).resolve().parents[3]
REAL_WATCH = REPO / "research/modalities/ternary-watch.json"

DISPATCH = {
    "leg_id": "calib_hi_to_lo__ternary_vhl",
    "seed": "0",
    "direction": "rev",
    "commit_salt": "v2pe",
    "timestep_fs": "2.0",
    "warmup_timestep_fs": "1.0",
    "use_preequil": "1",
    "restrain": "0",
}
REQUIRED = ["leg_id", "seed", "direction", "commit_salt", "timestep_fs",
            "warmup_timestep_fs", "use_preequil", "restrain"]


def doc(entries):
    return {"_required_run_params": REQUIRED, "watch": entries}


def entry(**over):
    e = dict(DISPATCH)
    e["enabled"] = True
    e.update(over)
    return e


def test_a_matching_enabled_entry_authorises_the_launch():
    ok, msgs = glg.check(doc([entry()]), DISPATCH, "test")
    assert ok, msgs
    assert any("WATCHER PRESENT" in m for m in msgs)


def test_no_entry_at_all_is_refused():
    ok, msgs = glg.check(doc([]), DISPATCH, "test")
    assert not ok
    assert any("NOTHING WOULD REAP THIS VM" in m for m in msgs)


def test_a_DISABLED_entry_is_not_a_watcher():
    """The exact state that opened the gap: gcp_watch_reap auto-disables a landed unit, and the reaper
    leaves with it. A disabled entry must count for nothing."""
    ok, _ = glg.check(doc([entry(enabled=False)]), DISPATCH, "test")
    assert not ok


@pytest.mark.parametrize("field,value", [
    ("leg_id", "calib_hi_to_lo__binary_vhl"),
    ("direction", "fwd"),
    ("seed", "1"),
    ("restrain", "1"),
])
def test_an_entry_for_a_DIFFERENT_calculation_is_refused(field, value):
    """These four key the leg RESULT object, which is the only thing the DONE branch `ls`es. An entry
    differing on any of them watches a different calculation entirely and would never reap this VM."""
    ok, _ = glg.check(doc([entry(**{field: value})]), DISPATCH, "test")
    assert not ok


@pytest.mark.parametrize("field,value", [
    ("timestep_fs", "4.0"),
    ("warmup_timestep_fs", ""),
    ("commit_salt", ""),
    ("use_preequil", "0"),
])
def test_a_NEAR_MISS_is_refused_and_says_which_field(field, value):
    """Same result key, so the *reap* would work — but these are literal components of the GCS commit
    prefix (or select the setup cache), so the watchdog would census a trajectory this leg is not writing
    and relaunch the wrong prefix if it died. Refusing is right; naming the field is what stops the
    operator "fixing" it by adding a second entry."""
    ok, msgs = glg.check(doc([entry(**{field: value})]), DISPATCH, "test")
    assert not ok
    blob = " ".join(msgs)
    assert "AN ENTRY FOR THIS LEG EXISTS BUT DOES NOT REPRODUCE THE DISPATCH" in blob
    assert field in blob, blob


def test_string_equality_is_exact_not_numeric():
    """`2.0` and `2` are DIFFERENT commit prefixes. Coercing them to floats here would bless an entry
    that censuses a path the leg never writes — a convenience that silently becomes a bug."""
    ok, _ = glg.check(doc([entry(timestep_fs="2")]), DISPATCH, "test")
    assert not ok


def test_entry_defaults_match_the_watchdogs_own_get_defaults():
    """watchdog_run.sh reads each optional key with an explicit default. If this guard defaulted
    differently, a legitimate entry could be refused (or worse, a wrong one blessed) purely because the
    two files disagreed about what an omitted key means."""
    d = dict(DISPATCH, commit_salt="", warmup_timestep_fs="", use_preequil="0",
             restrain="0", timestep_fs="2.0")
    sparse = {"enabled": True, "leg_id": d["leg_id"], "seed": d["seed"], "direction": d["direction"]}
    ok, msgs = glg.check(doc([sparse]), d, "test")
    assert ok, msgs


def test_a_watch_list_with_no_required_param_list_is_refused():
    """Without `_required_run_params` this guard cannot tell whether an entry reproduces the dispatch,
    and 'cannot tell' must never render as 'yes'."""
    ok, msgs = glg.check({"watch": [entry()]}, DISPATCH, "test")
    assert not ok
    assert any("NO REQUIRED-PARAM LIST" in m for m in msgs)


def test_a_missing_dispatch_value_is_refused_not_defaulted():
    ok, msgs = glg.check(doc([entry()]), {k: v for k, v in DISPATCH.items() if k != "restrain"}, "t")
    assert not ok
    assert any("CALLED WITHOUT" in m for m in msgs)


def test_result_key_carries_the_restraint():
    assert glg.result_key(dict(DISPATCH, restrain="1")).endswith("_r0_rst.json")
    assert glg.result_key(dict(DISPATCH, restrain="0")).endswith("_r0.json")


def test_missing_or_unreadable_watch_file_is_a_refusal(tmp_path, capsys):
    assert glg.main(["--watch", str(tmp_path / "nope.json"), "--leg-id", "x"]) == 1
    bad = tmp_path / "bad.json"
    bad.write_text("{not json")
    assert glg.main(["--watch", str(bad), "--leg-id", "x"]) == 1
    assert "UNREADABLE" in capsys.readouterr().out


def test_divergence_from_main_only_WARNS(tmp_path, capsys):
    """main's copy is the authority because ternary-leg-watchdog.yml checks out with no `ref`. If main
    authorises the launch the reap is safe, so a stale branch copy must not block it — it is branch
    drift (CLAUDE.md §7) to reconcile, not a safety failure."""
    main_f, branch_f = tmp_path / "main.json", tmp_path / "branch.json"
    main_f.write_text(json.dumps(doc([entry()])))
    branch_f.write_text(json.dumps(doc([])))
    argv = ["--watch", str(main_f), "--also-watch", str(branch_f)]
    for k, v in DISPATCH.items():
        argv += [f"--{k.replace('_', '-')}", v]
    assert glg.main(argv) == 0
    assert "WATCH LIST DIVERGES FROM main" in capsys.readouterr().out


def test_the_real_watch_list_is_readable_and_declares_its_required_params():
    """Not a style check: the guard REFUSES a list it cannot read, so an unparseable committed watch file
    would block every future GCP launch."""
    d = json.loads(REAL_WATCH.read_text())
    assert glg.required_params(d) == REQUIRED, glg.required_params(d)


def test_every_real_entry_would_authorise_its_own_parameters():
    """Round-trip: each committed entry, treated as if it were enabled, must authorise a dispatch built
    from its own values. A committed entry that could not authorise itself means the guard and the watch
    file have drifted apart, and the symptom would be a launch refused for no visible reason."""
    d = json.loads(REAL_WATCH.read_text())
    for e in d["watch"]:
        params = {k: glg.entry_value(e, k) for k in REQUIRED}
        live = dict(e, enabled=True)
        ok, msgs = glg.check({"_required_run_params": REQUIRED, "watch": [live]}, params, "real")
        assert ok, f"{e.get('leg_id')}/{e.get('direction')} cannot authorise itself: {msgs}"


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(pytest.main([__file__, "-v"]))
