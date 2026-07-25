#!/usr/bin/env python3
"""Cross-leg SYSTEM identity must be checked, and 'unrecorded' must not read as 'consistent'.

WHY. ddG_coop is a DIFFERENCE of legs and |dG_fwd + dG_rev| is a SUM of them; both are meaningless if the legs
describe different systems. `protocol_hash` covers the OpenFE settings and NOT the system, so on 2026-07-25 four
reverse-leg attempts ran a 146,020-particle `v1` build while the forward leg they would be compared against was a
141,968-particle `v2pe` build -- and no check in the repo would have reported it. Establishing that required
excavating a five-day-old CI log from a different workflow.

The load-bearing case is the last one: legs written before these fields existed record None, and that must report
as UNKNOWN rather than being folded in as agreement. Absent provenance reading as matching provenance is the
presence-blind defect this lane was audited for (section B), and it has already recurred three times.
"""

import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))


def run_case(legs):
    """Write leg JSONs into a temp CKPT/IN and return the reduce's system-identity verdict."""
    with tempfile.TemporaryDirectory() as d:
        for name, rec in legs.items():
            json.dump(rec, open(os.path.join(d, name), "w"))
        os.environ["CKPT_DIR"] = d
        os.environ["INPUT_DIR"] = d
        for m in ("ternary_fep_reduce",):
            sys.modules.pop(m, None)
        import ternary_fep_reduce as r
        return r._system_identity_consistency()


def leg(n_particles=141968, charge="nagl", setup="v2pe"):
    return {"protocol_hash": "h", "n_particles": n_particles,
            "charge_method": charge, "setup_cache_version": setup}


def main():
    fails = []

    def chk(name, got, want):
        if got == want:
            print("PASS %s" % name)
        else:
            print("FAIL %s: got %r want %r" % (name, got, want))
            fails.append(name)

    chk("matched fwd/rev legs are CONSISTENT",
        run_case({"leg_a_fwd_r0.json": leg(), "leg_a_rev_r0.json": leg()})["verdict"], "CONSISTENT")

    # the actual 2026-07-25 situation: a v1 rev leg against a v2pe fwd leg
    v = run_case({"leg_a_fwd_r0.json": leg(141968, setup="v2pe"),
                  "leg_a_rev_r0.json": leg(146020, setup="v1")})
    chk("v1 rev vs v2pe fwd is INCONSISTENT", v["verdict"], "INCONSISTENT")
    chk("it names the particle count", "n_particles" in v["note"], True)
    chk("it names the setup version", "setup_cache_version" in v["note"], True)
    chk("it records both particle counts",
        sorted(v["fields"]["n_particles"]["values"]), ["141968", "146020"])

    # the atom-set-preserving case OpenFE structurally cannot see
    v = run_case({"leg_a_fwd_r0.json": leg(charge="nagl"), "leg_a_rev_r0.json": leg(charge="am1bcc")})
    chk("a charge-method mismatch is INCONSISTENT", v["verdict"], "INCONSISTENT")

    # THE load-bearing case: legacy legs with nothing recorded must be UNKNOWN, never CONSISTENT
    legacy = {"protocol_hash": "h"}
    v = run_case({"leg_a_fwd_r0.json": dict(legacy), "leg_a_rev_r0.json": dict(legacy)})
    chk("legs with NO recorded identity are UNKNOWN, not CONSISTENT", v["verdict"], "UNKNOWN")
    chk("the UNKNOWN note says NOT VERIFIED", "NOT VERIFIED" in v["note"], True)
    chk("it lists which legs are unrecorded",
        sorted(v["partially_unrecorded"]), ["leg_a_fwd_r0.json", "leg_a_rev_r0.json"])

    # a mix: one leg records, one does not -> the recorded ones agree but coverage is partial
    v = run_case({"leg_a_fwd_r0.json": leg(), "leg_a_rev_r0.json": dict(legacy)})
    chk("a partially-recorded set still reports the gap",
        v["partially_unrecorded"], ["leg_a_rev_r0.json"])

    # and a real disagreement must win over partial coverage
    v = run_case({"leg_a_fwd_r0.json": leg(141968), "leg_a_rev_r0.json": leg(146020),
                  "leg_a_sol_r0.json": dict(legacy)})
    chk("a real disagreement outranks partial coverage", v["verdict"], "INCONSISTENT")

    # the engine must actually WRITE the fields the check reads -- otherwise this passes against nothing
    src = open(os.path.join(HERE, "..", "nr4a3_ternary_fep.py")).read()
    for f in ("n_particles", "setup_cache_dir", "charge_method", "setup_cache_version"):
        chk("the leg record writes %s" % f, ('"%s"' % f) in src, True)
    red = open(os.path.join(HERE, "..", "ternary_fep_reduce.py")).read()
    chk("the reduction exposes system_identity_consistency",
        '"system_identity_consistency"' in red, True)

    print("\n%d check(s) failed" % len(fails))
    return 1 if fails else 0


def test_system_identity_consistency():
    assert main() == 0


if __name__ == "__main__":
    sys.exit(main())
