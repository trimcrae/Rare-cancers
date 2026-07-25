#!/usr/bin/env python3
"""Unit tests for watchdog_validate: the guard that stops the watchdog relaunching a leg from incomplete config.

The guard must DISCRIMINATE, not merely run. It was born from a real defect -- ternary-watch.json omitted
`warmup_timestep_fs`, which keys the spot commit prefix, so a relaunch would have resumed a DIFFERENT
trajectory than the one being watched. A guard that passes whatever it is given reproduces exactly that.
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
import watchdog_validate as wv  # noqa: E402

REQ = ["leg_id", "seed", "direction", "commit_salt", "timestep_fs", "warmup_timestep_fs", "use_preequil"]


def doc(entries, required=REQ, key="_required_run_params"):
    return {key: required, "watch": entries}


def full(**over):
    e = {"enabled": True, "leg_id": "L", "seed": "0", "direction": "rev", "commit_salt": "v2pe",
         "timestep_fs": "2.0", "warmup_timestep_fs": "1.0", "use_preequil": "1"}
    e.update(over)
    return e


def main():
    fails = []

    def chk(name, got, want):
        if got == want:
            print("PASS %s" % name)
        else:
            print("FAIL %s: got %r want %r" % (name, got, want))
            fails.append(name)

    chk("a complete entry is valid", wv.validate(doc([full()])), [])

    e = full(); e.pop("warmup_timestep_fs")
    chk("the real defect is caught (warmup_timestep_fs missing)",
        wv.validate(doc([e])), [("L", "rev", ["warmup_timestep_fs"])])

    e = full(); e.pop("commit_salt"); e.pop("direction")
    got = wv.validate(doc([e]))
    chk("several missing keys are all reported", got, [("L", "?", ["direction", "commit_salt"])])

    e = full(enabled=False); e.pop("warmup_timestep_fs")
    chk("a DISABLED incomplete entry is ignored", wv.validate(doc([e])), [])

    chk("an empty watch list is valid", wv.validate(doc([])), [])

    # No declared requirements must not silently mean "everything passes" for the WRONG reason: it means the
    # config declares nothing to enforce. Assert the behaviour explicitly so nobody 'fixes' it by accident.
    e = full(); e.pop("warmup_timestep_fs")
    chk("no required list -> nothing enforced (explicitly)", wv.validate(doc([e], required=[])), [])

    # use_preequil is NOT part of the commit prefix, but it selects the relaxed (v2pe) vs raw (v1) starting
    # complex. Pre-equilibration only moves coordinates, so particle counts match and OpenFE's
    # assert_multistate_system_equality CANNOT catch a cross-restore the way it caught fwd/rev. Omitting it must
    # therefore fail exactly as loudly as omitting a prefix key.
    e = full(); e.pop("use_preequil")
    chk("missing use_preequil is caught (not prefix-keying, but system-changing)",
        wv.validate(doc([e])), [("L", "rev", ["use_preequil"])])

    # the legacy key name must keep working: another session may hold a copy of the older watch file
    e = full(); e.pop("warmup_timestep_fs")
    chk("legacy _prefix_keying_params key is still honoured",
        wv.validate(doc([e], key="_prefix_keying_params")), [("L", "rev", ["warmup_timestep_fs"])])

    # the real repo config must be valid, or the watchdog is inert
    real = os.path.join(HERE, "..", "ternary-watch.json")
    with open(real) as fh:
        problems = wv.validate(json.load(fh))
    chk("the checked-in ternary-watch.json is valid", problems, [])

    # exit code contract: main() must return non-zero on a bad file, since the workflow branches on it
    import tempfile
    bad = full(); bad.pop("timestep_fs")
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
        json.dump(doc([bad]), fh)
        badpath = fh.name
    rc = wv.main(["watchdog_validate.py", badpath])
    os.unlink(badpath)
    chk("main() exits non-zero on invalid config", rc, 1)
    rc_ok = wv.main(["watchdog_validate.py", real])
    chk("main() exits zero on the real config", rc_ok, 0)

    if check_watchdog_field_alignment() != 0:
        fails.append("field alignment")
    if check_setup_cache_key() != 0:
        fails.append("setup cache key")

    print("\n%d check(s) failed" % len(fails))
    return 1 if fails else 0


def check_watchdog_field_alignment():
    """The watchdog serialises each watch entry as a pipe-joined line and reads it back with `read -r A B C...`.
    If the format string, the value list and the variable list ever disagree, every field after the divergence
    is SILENTLY SHIFTED into the wrong variable -- charge_method landing in use_preequil, say -- and the relaunch
    runs a different configuration while reporting success. Same class as every other defect in the guard audit,
    so it gets a check rather than care."""
    import re
    wf = os.path.join(HERE, "..", "..", "..", ".github", "workflows", "ternary-leg-watchdog.yml")
    if not os.path.isfile(wf):
        print("SKIP field alignment (workflow not found)")
        return 0
    t = open(wf).read()
    m = re.search(r"\[print\('([^']+)'%\((.*?)\)\) for w in", t)
    r = re.search(r"read -r ([A-Z ]+); do", t)
    if not m or not r:
        print("FAIL field alignment: could not locate the serialise/read pair — markers changed")
        return 1
    n_fmt = m.group(1).count("%s")
    n_val = m.group(2).count("w[") + m.group(2).count("w.get(")
    names = r.group(1).split()
    if n_fmt == n_val == len(names):
        print("PASS field alignment: %d format slots == %d values == %d read vars (%s)"
              % (n_fmt, n_val, len(names), ",".join(names)))
        return 0
    print("FAIL field alignment: %d format slots, %d values, %d read vars — fields would shift silently"
          % (n_fmt, n_val, len(names)))
    return 1


def check_setup_cache_key():
    """The watchdog builds the primed-setup-cache path itself to check the precondition before buying a VM. That
    path must match the engine's key exactly, or the check silently passes/fails on a path nobody writes -- the
    same drift that made a rev leg resume the fwd trajectory. Observed engine path, from the 2026-07-25 prime:
    setupcache/calib_hi_to_lo__ternary_vhl_rev_r0__nagl__v2pe
    """
    wf = os.path.join(HERE, "..", "..", "..", ".github", "workflows", "ternary-leg-watchdog.yml")
    if not os.path.isfile(wf):
        print("SKIP setup-cache key (workflow not found)")
        return 0
    t = open(wf).read()
    bad = 0
    if "setupcache/${LEG}_${DIR}_r${SEED}__${CHG}__${SETUPVER}" not in t:
        print("FAIL setup-cache key: the watchdog's path no longer matches the engine's "
              "<leg>_<dir>_r<seed>__<charge>__<version> key")
        bad = 1
    else:
        print("PASS setup-cache key matches the engine's <leg>_<dir>_r<seed>__<charge>__<version>")
    if 'SETUPVER=v1; [ "$UPE" = "1" ] && SETUPVER=v2pe' not in t:
        print("FAIL setup-cache version: use_preequil=1 must select v2pe (it is what forces SETUP_VER=v2pe)")
        bad = 1
    else:
        print("PASS use_preequil=1 selects the v2pe setup cache")
    return bad


def test_setup_cache_key():
    assert check_setup_cache_key() == 0


def test_watchdog_field_alignment():
    assert check_watchdog_field_alignment() == 0


def test_watchdog_config_guard():
    assert main() == 0, "the watch-config guard failed a check — see the FAIL lines above"


if __name__ == "__main__":
    sys.exit(main())
