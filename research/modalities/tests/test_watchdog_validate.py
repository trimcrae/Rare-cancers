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

REQ = ["leg_id", "seed", "direction", "commit_salt", "timestep_fs", "warmup_timestep_fs"]


def doc(entries, required=REQ):
    return {"_prefix_keying_params": required, "watch": entries}


def full(**over):
    e = {"enabled": True, "leg_id": "L", "seed": "0", "direction": "rev", "commit_salt": "v2pe",
         "timestep_fs": "2.0", "warmup_timestep_fs": "1.0"}
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
    chk("no _prefix_keying_params -> nothing enforced (explicitly)", wv.validate(doc([e], required=[])), [])

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

    print("\n%d check(s) failed" % len(fails))
    return 1 if fails else 0


def test_watchdog_config_guard():
    assert main() == 0, "the watch-config guard failed a check — see the FAIL lines above"


if __name__ == "__main__":
    sys.exit(main())
