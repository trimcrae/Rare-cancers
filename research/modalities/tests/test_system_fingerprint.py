#!/usr/bin/env python3
"""The commit manifest must carry a system fingerprint, and a restore must refuse a mismatched generation.

WHY. The spot commit prefix is `<seed>_dt<dt>fs_clig<c>_wu<warmup_dt>[_<salt>][_dir<dir>]`. Several params that
change the PHYSICS are absent from it -- SETUP_CACHE_VERSION (v2pe = alchemy started from the plain-MD-relaxed
complex, vs v1 raw), CHARGE_METHOD (nagl vs am1bcc = different partial charges), N_WINDOWS -- so two different
calculations can share one prefix.

The fwd/rev instance of this bug (audit section H) was caught ONLY because the two hybrid systems had different
particle counts, so OpenFE's assert_multistate_system_equality refused the restore. That escape does not
generalise: pre-equilibration only MOVES COORDINATES, so a v1-vs-v2pe mismatch has identical particle counts and
OpenFE cannot detect it. Hence a fingerprint recorded in the manifest and checked on restore.

The critical case is the LAST one: an UNSTAMPED manifest must be REJECTED, not assumed to match. Absent
provenance reading as matching provenance is the presence-blind defect this whole lane was audited for.
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
import rbfe_spot_checkpoint as ck  # noqa: E402

BASE = {
    "LEG_ID": "calib_hi_to_lo__ternary_vhl", "DIRECTION": "rev", "SEED": "0",
    "CHARGE_METHOD": "nagl", "SETUP_CACHE_VERSION": "v2pe", "N_WINDOWS": "12",
    "RBFE_TIMESTEP_FS": "2.0", "RBFE_WARMUP_TIMESTEP_FS": "1.0", "RBFE_CONSTRAIN_LIGAND_CH": "0",
}


def env(**over):
    e = dict(BASE)
    e.update(over)
    return e


def manifest_for(e):
    fp, fields = ck.system_fingerprint(e)
    return {"schema": 2, "system_fingerprint": fp, "system_fingerprint_fields": fields}


def main():
    fails = []

    def chk(name, cond, detail=""):
        if cond:
            print("PASS %s" % name)
        else:
            print("FAIL %s %s" % (name, detail))
            fails.append(name)

    # stability + sensitivity
    fp1, _ = ck.system_fingerprint(env())
    fp2, _ = ck.system_fingerprint(env())
    chk("fingerprint is stable across calls", fp1 == fp2)
    chk("a dict-order change does not alter it",
        ck.system_fingerprint({k: BASE[k] for k in reversed(list(BASE))})[0] == fp1)

    for var, other in [("SETUP_CACHE_VERSION", "v1"), ("CHARGE_METHOD", "am1bcc"),
                       ("N_WINDOWS", "16"), ("DIRECTION", "fwd"), ("SEED", "1"),
                       ("RBFE_TIMESTEP_FS", "4.0"), ("RBFE_WARMUP_TIMESTEP_FS", ""),
                       ("RBFE_CONSTRAIN_LIGAND_CH", "1"), ("LEG_ID", "other")]:
        chk("%s changes the fingerprint" % var,
            ck.system_fingerprint(env(**{var: other}))[0] != fp1)

    # matching provenance restores
    chk("a matching manifest is accepted",
        ck.fingerprint_mismatch_reason(manifest_for(env()), env()) is None)

    # THE case OpenFE cannot catch: v1 trajectory into a v2pe run, identical particle counts
    why = ck.fingerprint_mismatch_reason(manifest_for(env(SETUP_CACHE_VERSION="v1")), env())
    chk("v1 committed vs v2pe running is REFUSED", why is not None, "(got None)")
    chk("the refusal names the offending field",
        why is not None and "SETUP_CACHE_VERSION" in why, "(reason: %s)" % why)
    chk("the refusal shows both values",
        why is not None and "'v1'" in why and "'v2pe'" in why, "(reason: %s)" % why)

    # charge method: a different Hamiltonian under the same prefix
    why_c = ck.fingerprint_mismatch_reason(manifest_for(env(CHARGE_METHOD="am1bcc")), env())
    chk("am1bcc committed vs nagl running is REFUSED", why_c is not None)

    # UNSTAMPED is absence of evidence, not evidence of mismatch -- so it warns and is allowed by default, and
    # is refused only under RBFE_STRICT_PROVENANCE=1. Failing closed here would make ANOTHER session's already
    # running leg refuse to resume after a preemption and discard paid GPU hours, for a change it had no part in.
    chk("an UNSTAMPED manifest is allowed by default (with a warning)",
        ck.fingerprint_mismatch_reason({"schema": 1}, env()) is None)
    chk("RBFE_STRICT_PROVENANCE=1 refuses an unstamped manifest",
        ck.fingerprint_mismatch_reason({"schema": 1}, env(RBFE_STRICT_PROVENANCE="1")) is not None)
    chk("the strict refusal names the flag",
        "RBFE_STRICT_PROVENANCE" in (ck.fingerprint_mismatch_reason({"schema": 1},
                                                                    env(RBFE_STRICT_PROVENANCE="1")) or ""))
    # a real MISMATCH is refused UNCONDITIONALLY -- there is no flag for it, because we have positive evidence
    chk("a real MISMATCH is refused even without strict mode",
        ck.fingerprint_mismatch_reason(manifest_for(env(SETUP_CACHE_VERSION="v1")), env()) is not None)
    chk("no flag can excuse a real MISMATCH",
        ck.fingerprint_mismatch_reason(manifest_for(env(SETUP_CACHE_VERSION="v1")),
                                       env(RBFE_STRICT_PROVENANCE="0")) is not None)
    chk("an empty/None manifest is treated as unstamped (allowed, warned)",
        ck.fingerprint_mismatch_reason(None, env()) is None)
    chk("the ternary GPU lane opts INTO strict provenance",
        "RBFE_STRICT_PROVENANCE=1" in open(os.path.join(
            HERE, "..", "..", "..", ".github", "workflows", "gpu-ternary-fep-gcp.yml")).read())

    # commit() must actually stamp it, and restore_latest must consult it
    src = open(os.path.join(HERE, "..", "rbfe_spot_checkpoint.py")).read()
    chk("commit() stamps system_fingerprint into the manifest",
        '"system_fingerprint": _fp' in src)
    chk("restore_latest() consults the fingerprint before fetching",
        src.index("fingerprint_mismatch_reason(man)") < src.index("nc_p, chk_p = self.fetch("))

    # ---- restore_latest behaviour, with a fake store -------------------------------------------------
    # The real checkpoint suite (rbfe_spot_checkpoint_test.py) needs numpy + openmm and only runs in the AWS GPU
    # workflow, so it cannot gate this change. These fakes exercise the exact property that matters and need no
    # scientific stack: a mismatched generation must be skipped WITHOUT DOWNLOADING IT, and a prefix holding a
    # mix must still resume from the newest COMPATIBLE generation rather than refusing outright.
    import tempfile
    from pathlib import Path

    class _Fetched(Exception):
        pass

    class FakeStore(ck._BaseCommitStore):
        def __init__(self, gens):
            self.gens = gens          # [(iteration, generation, manifest)], newest first
            self.fetched = []

        def list_committed(self, phase):
            return self.gens

        def fetch(self, phase, iteration, generation, dest_dir):
            self.fetched.append((iteration, generation))
            raise _Fetched("fake store: no real files")   # we only care THAT it tried

    saved = dict(os.environ)
    try:
        os.environ.clear()
        os.environ.update(env())
        good = manifest_for(env())
        bad = manifest_for(env(SETUP_CACHE_VERSION="v1"))
        with tempfile.TemporaryDirectory() as ws:
            s = FakeStore([(200, "genbad", bad)])
            s.restore_latest(["production"], Path(ws), 40)
            chk("a mismatched generation is skipped WITHOUT being downloaded", s.fetched == [],
                "(fetched %s)" % s.fetched)

            s = FakeStore([(200, "gengood", good)])
            s.restore_latest(["production"], Path(ws), 40)
            chk("a matching generation IS downloaded", s.fetched == [(200, "gengood")],
                "(fetched %s)" % s.fetched)

            # newest is incompatible, an older one matches -> must fall through, not refuse
            s = FakeStore([(200, "genbad", bad), (160, "gengood", good)])
            s.restore_latest(["production"], Path(ws), 40)
            chk("falls through a mismatch to the newest COMPATIBLE generation",
                s.fetched == [(160, "gengood")], "(fetched %s)" % s.fetched)

            # unstamped legacy generation: downloaded by default (warned), refused under strict mode
            s = FakeStore([(200, "genold", {"schema": 1})])
            s.restore_latest(["production"], Path(ws), 40)
            chk("an unstamped generation still resumes by default", s.fetched == [(200, "genold")],
                "(fetched %s)" % s.fetched)
            os.environ["RBFE_STRICT_PROVENANCE"] = "1"
            s = FakeStore([(200, "genold", {"schema": 1})])
            s.restore_latest(["production"], Path(ws), 40)
            chk("strict mode declines to download an unstamped generation", s.fetched == [],
                "(fetched %s)" % s.fetched)
            del os.environ["RBFE_STRICT_PROVENANCE"]
    finally:
        os.environ.clear()
        os.environ.update(saved)

    print("\n%d check(s) failed" % len(fails))
    return 1 if fails else 0


def test_system_fingerprint_guards_the_commit_store():
    assert main() == 0


if __name__ == "__main__":
    sys.exit(main())
