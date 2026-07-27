#!/usr/bin/env python3
"""`mode=provenance` must never report ABSENT provenance as AGREEING provenance.

WHY THIS TEST EXISTS, and it is not hypothetical. `mode=provenance` was added to settle a question that had
been answered by INFERENCE FROM AN ABSENCE — "the only binary setup cache that exists is `__v1`, so the leg
must be v1". Its first run returned `setup=UNRECORDED` for all four landed legs, for two independent reasons:

  1. it read `cache_dir`, which is the key used only in the PRIME marker; the leg record's field is
     `setup_cache_dir`. So it reported "unrecorded" for a field it was looking up under the wrong name.
  2. its comparability check was `if len(set(versions)) > 1: warn`. With every leg UNRECORDED that set is the
     single value `{UNRECORDED}`, so the check PASSED — silently, on no evidence at all.

Defect 2 is the one that matters: the tool built to stop "absent rendered as a legal good value" contained
exactly that defect, and it presented as a clean run. A verdict of "no disagreement found" over a population
where nothing was measured is not a pass, and must not render as one.

METHOD: the verdict logic is EXTRACTED from the real workflow's provenance step and executed. Restating it
here would prove only that the copy agrees with itself — the same discipline as the commit-prefix tests.
"""

import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WF = os.path.join(HERE, "..", "..", "..", ".github", "workflows", "gpu-ternary-fep-gcp.yml")

UNREC = "UNRECORDED"


def verdict_source():
    """The tri-state verdict block, lifted verbatim out of the workflow and dedented."""
    text = open(WF).read()
    start = text.index("          known = {r[1] for r in rows if r[1] != UNREC}")
    end = text.index("[provenance] all legs agree on setup version", start)
    end = text.index("\n", text.index("\n", end) + 1) + 1
    block = "\n".join(l[10:] if len(l) > 10 else l for l in text[start:end].split("\n"))
    assert "LEG SETUP VERSION NOT VERIFIED" in block, "extraction missed the not-verified branch"
    return block


def run(rows, man_rows):
    """Execute the real block and return everything it printed."""
    out = []
    ns = {"rows": rows, "man_rows": man_rows, "UNREC": UNREC,
          "print": lambda *a: out.append(" ".join(str(x) for x in a))}
    exec(compile(verdict_source(), "<verdict>", "exec"), ns)  # noqa: S102 — the point is to run the real code
    return "\n".join(out)


def leg(name, ver):
    return (name, ver, None, "hash", 12, "")


def man(name, ver):
    return (name, ver, "", 2)


def test_all_unrecorded_is_NOT_VERIFIED_not_a_pass():
    """THE REGRESSION. Four legs, none recording a setup version, no manifests: the first implementation
    printed nothing at all here and the run read as clean."""
    got = run([leg("a.json", UNREC), leg("b.json", UNREC)], [])
    assert "NOT VERIFIED" in got, "absence must report NOT VERIFIED, got: %r" % got
    assert "not a measurement" in got.lower() or "NOT a pass" in got, (
        "the message must say plainly that this is not a pass: %r" % got)
    assert "agree on setup version" not in got, "absence must never render as agreement: %r" % got


def test_genuine_agreement_is_reported_as_verified():
    got = run([leg("a.json", "v1"), leg("b.json", "v1")], [])
    assert "VERIFIED" in got and "NOT VERIFIED" not in got, got
    assert "v1" in got, got


def test_a_real_disagreement_is_an_error_not_a_warning():
    """A v1 leg beside a v2pe leg is audit J.2-J.5's exact defect — different SYSTEMS, and for the ternary a
    ~4,052-particle difference. It must be an ::error, not a ::warning."""
    got = run([leg("a.json", "v1"), leg("b.json", "v2pe")], [])
    assert "::error" in got and "DIFFER" in got, got


def test_manifest_evidence_rescues_a_silent_leg_record_without_claiming_full_verification():
    """Legs older than the 2026-07-25 leg-record field carry no setup_cache_dir, but their commit manifests
    stamp SETUP_CACHE_VERSION. That is real evidence — and it still must not be reported as if the leg records
    themselves had been verified."""
    got = run([leg("a.json", UNREC)], [man("pfx", "v1")])
    assert "PARTIALLY VERIFIED" in got, got
    assert "not as agreement" in got, got


def test_manifest_disagreeing_with_a_leg_record_is_an_error():
    got = run([leg("a.json", "v1")], [man("pfx", "v2pe")])
    assert "::error" in got and "DIFFER" in got, got


def test_the_workflow_reads_the_real_leg_record_field_name():
    """Defect 1: the field is `setup_cache_dir` (nr4a3_ternary_fep writes it into every leg record);
    `cache_dir` is the PRIME marker's name. Reading only the latter reports UNRECORDED for every real leg
    while looking like it checked."""
    text = open(WF).read()
    i = text.index("=== [LEG-PROVENANCE] ===")
    j = text.index("COMMIT-MANIFEST PROVENANCE", i)
    assert "setup_cache_dir" in text[i:j], "the provenance step does not read `setup_cache_dir`"
    eng = open(os.path.join(HERE, "..", "nr4a3_ternary_fep.py")).read()
    assert re.search(r'"setup_cache_dir":\s*_setup_cache', eng), (
        "nr4a3_ternary_fep no longer writes setup_cache_dir under that name — the reader above is now blind")


# The runner stays LAST: tests defined below a `__main__` block are silently skipped, which has already happened
# twice in this directory. Add new test_* functions ABOVE this line.
if __name__ == "__main__":
    fails = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print("PASS", name)
            except AssertionError as e:
                print("FAIL", name, "\n      ", e)
                fails += 1
            except Exception as e:  # noqa: BLE001
                print("ERROR", name, "\n      ", type(e).__name__, e)
                fails += 1
    print("\n%d failure(s)" % fails)
    sys.exit(1 if fails else 0)
