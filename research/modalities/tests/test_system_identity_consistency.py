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
    """Write leg JSONs into a temp CKPT/IN and return the reduce's system-identity verdict.

    ⚠ This helper re-imports `ternary_fep_reduce` under patched env, which is a GLOBAL side effect, so it
    must leave no trace. It previously left two, and they made the suite order-dependent:

      1. It popped the module and re-imported, so `sys.modules["ternary_fep_reduce"]` ended up a DIFFERENT
         object from the one other test modules had already bound. `importlib.reload(x)` requires
         `sys.modules[x.__name__] is x`, so `test_ternary_leg_audit` failed with "module
         ternary_fep_reduce not in sys.modules" -- but only when it ran after this file. Passing alone and
         failing in the suite is the signature.
      2. It assigned CKPT_DIR/INPUT_DIR via os.environ and never restored them, leaving both pointing at a
         TemporaryDirectory that had since been deleted.

    Both are restored now, so the helper is order-independent.
    """
    prev_mod = sys.modules.get("ternary_fep_reduce")
    prev_env = {k: os.environ.get(k) for k in ("CKPT_DIR", "INPUT_DIR")}
    try:
        with tempfile.TemporaryDirectory() as d:
            for name, rec in legs.items():
                json.dump(rec, open(os.path.join(d, name), "w"))
            os.environ["CKPT_DIR"] = d
            os.environ["INPUT_DIR"] = d
            sys.modules.pop("ternary_fep_reduce", None)
            import ternary_fep_reduce as r
            return r._system_identity_consistency()
    finally:
        if prev_mod is not None:
            sys.modules["ternary_fep_reduce"] = prev_mod
        else:
            sys.modules.pop("ternary_fep_reduce", None)
        for k, v in prev_env.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


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
        sorted(v["fields"]["n_particles"]["by_leg"]["a"]), ["141968", "146020"])

    # ── the comparison that was meaningless BY CONSTRUCTION (2026-07-30, 3:07 AM ET) ──────────────
    # The check used to pool every leg into one bucket, so a ΔΔG_coop cycle's TERNARY arm (~144k
    # particles) was compared against its BINARY arm (~90k). Those differ because a ternary complex
    # carries the E3 — the guard could never return CONSISTENT for the cycle it guards, and fired on
    # every healthy run. Values below are the live valB_mini reduction.
    v = run_case({"leg_calib__ternary_vhl_fwd_r1.json": leg(144447),
                  "leg_calib__binary_vhl_fwd_r1.json": leg(90324)})
    chk("ternary vs binary arm is NOT an inconsistency", v["verdict"], "CONSISTENT")

    # ...but a leg disagreeing with ITSELF across seeds still is — this is the live cycle's real finding.
    v = run_case({"leg_calib__ternary_vhl_fwd_r1.json": leg(144447),
                  "leg_calib__ternary_vhl_fwd_r2.json": leg(141740)})
    chk("one arm disagreeing across seeds IS an inconsistency", v["verdict"], "INCONSISTENT")

    # ⚠ DIRECTION MUST STAY INSIDE THE GROUP. Grouping on the seed alone would split fwd from rev and
    # blind the check to its own founding case, which was a v1 REVERSE leg against a v2pe FORWARD leg.
    v = run_case({"leg_calib__ternary_vhl_fwd_r0.json": leg(141968, setup="v2pe"),
                  "leg_calib__ternary_vhl_rev_r0.json": leg(146020, setup="v1")})
    chk("fwd vs rev of one arm is still compared", v["verdict"], "INCONSISTENT")

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
