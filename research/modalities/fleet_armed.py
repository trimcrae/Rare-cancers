#!/usr/bin/env python3
"""Is there anything to supervise right now? — the one gate every idle supervision lane asks.

★★ WHY THIS EXISTS (trimcrae, 2026-08-06: *"Why would we need supervision for tests that aren't running?
That seems like a terrible system"*).

MEASURED THAT DAY: **1,476 commits to `main` in 24 hours, 1,438 of them CI ticks, 703 of which say in their
own subject line that they did nothing** — `NOTHING-TO-LAUNCH`, `NOTHING-TO-REAP (0 to reap)`,
`all supervised`. Eleven lanes, each committing every ~7 minutes. The account held **zero instances** and the
in-flight board read *"no GPU legs"* the entire time.

⚠ THE CHURN WAS DELIBERATE, WHICH IS WHY NOBODY HAD FIXED IT. `vast-account-reaper.yml` states the reasoning
outright: *"`--allow-empty`, AND NEVER GUARDED BY `git diff --cached --quiet`. THE TIMESTAMP IS THE
HEARTBEAT … a `git diff --quiet` guard would skip the commit, freeze the artifact's commit date, and make a
perfectly-running reaper look stopped. That landmine was found in three lanes."* That is a real lesson and
this module does not undo it.

⭐ WHAT IT ADDS IS THE STATE THE DESIGN NEVER HAD: **OFF**. Proof-of-life for a watchman guarding nothing is
worth nothing — a reaper that dies over an empty account costs $0, which is exactly when you do not need to
hear from it. So the heartbeat is conditional on there being something to guard, and the discriminator is an
account-level reading, never a lane-local belief.

⛔ WHAT THIS DOES **NOT** DO, AND THE DISTINCTION IS THE WHOLE SAFETY ARGUMENT:
  - It does NOT stop a lane running. Every cron fires exactly as before.
  - It does NOT stop a lane ACTING. A reap that needs to happen still happens; a teardown still tears down.
  - It gates ONLY whether a lane COMMITS A NON-EVENT.
So nothing that costs money is disabled here. The only thing lost when idle is a git-trail heartbeat that
was, by construction, reporting on an empty fleet.

★ AND ONE HEARTBEAT ALWAYS SURVIVES, so silence stays interpretable. The lane that OWNS this reading — the
account census — is exempt (`CENSUS_LANE`), because it is the thing that would notice a host appearing. Idle
therefore still produces a commit trail; it produces ONE lane's, hourly, instead of eleven lanes' every seven
minutes. "No commits at all" remains a real signal, which is what the 2026-08-01 incident bought.

⚠ FAIL-ARMED, NEVER FAIL-QUIET. Any doubt — census missing, unreadable, stale, or a field absent — returns
ARMED. A supervision lane that goes quiet because it could not read a file is the failure this repository
already paid for once, and it is strictly worse than the churn being fixed.
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))

#: The authoritative account-level reading: every instance the Vast account holds, from `GET /instances/`.
#: ⚠ ACCOUNT-LEVEL ON PURPOSE. A per-mode board filters to one mode's labels and so structurally cannot see
#: a host another lane holds — believing one of those would be a lane-local belief, which is what this
#: module exists to avoid.
CENSUS = os.path.join(HERE, "ternary-vast-account-census.json")

#: How old the census may be and still be trusted. Past this it is not evidence of an empty account, it is
#: an absent reading — and an absent reading is not a reading of absence (CLAUDE.md §4).
MAX_CENSUS_AGE_S = 3 * 3600

#: The lane that produces the census. It must NEVER gate itself on the census READING: it is the thing that
#: would discover a host appearing, and it is the heartbeat that keeps "no commits at all" meaningful.
CENSUS_LANE = "account-census"

#: ★★ HOW OFTEN THE CENSUS LANE MUST COMMIT — and why the answer is not "every tick" (trimcrae,
#: 2026-08-06: *"Why do we even need the census to be always on?"*).
#:
#: It does not, and the first fix over-corrected. Two things were being conflated:
#:
#:   THE READING must be unconditional. It is the ONLY detector of a host our own launch records do not
#:   know about — one left by a lane that died, or from an earlier session. That is exactly the 2026-08-01
#:   incident, and it is why the account-keyed alarm exists at all. You cannot gate it on "did we launch
#:   something", because the case it catches is precisely "a host exists that our launch records missed".
#:
#:   THE COMMIT does not. A commit saying "still zero" carries no information — trimcrae's original
#:   complaint, and correct. What it carries is PROOF THE DETECTOR IS ALIVE, and that proof is only needed
#:   often enough that the alarm can tell a live detector from a dead one.
#:
#: ⛔ AND YOU CANNOT DROP THE PROOF ENTIRELY. "Stale census whose last reading was zero" would have to be
#: read as fine — which makes a DEAD DETECTOR indistinguishable from a detector saying zero. That is the
#: fail-quiet direction, and it is the same failure in a new costume.
#:
#: So the census commits when it says something (n > 0), when it could not be read, or when the committed
#: copy is about to age past the alarm's own staleness window — and is otherwise silent. 30 min against the
#: alarm's 45: it can never be the reason the alarm fires, with room for a missed tick.
CENSUS_KEEPALIVE_S = 30 * 60


def _read_census(path=CENSUS):
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh), None
    except FileNotFoundError:
        return None, "census file is absent"
    except (json.JSONDecodeError, OSError) as e:
        return None, f"census unreadable: {e}"


def _age_seconds(doc, now=None):
    stamp = doc.get("utc")
    if not stamp:
        return None
    try:
        t = datetime.strptime(stamp, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    except ValueError:
        return None
    now = now or datetime.now(timezone.utc)
    return (now - t).total_seconds()


def _committed_census(path):
    """The census as it exists ON THE BRANCH, not in the working tree.

    ⚠ THE DISTINCTION IS THE WHOLE MECHANISM. By the time the publish gate runs, the working-tree copy has
    already been overwritten with THIS TICK's fresh reading, so its age is ~0 every time and asking it
    'are we about to go stale?' always answers no. The question is about the copy other lanes can SEE,
    which is the committed one.
    """
    import subprocess
    try:
        # ⚠ REPO-ROOT-RELATIVE, NOT CWD-RELATIVE. `git show HEAD:<path>` resolves from the repository
        # ROOT unless the path is written `./…`. The first version anchored on `research/` and every
        # lookup failed — silently harmless, because the failure is FAIL-ARMED, and therefore invisible:
        # the keep-alive simply never engaged and the lane published on every tick exactly as before.
        # A guard that no-ops into the old behaviour is the hardest kind to notice, which is why
        # `test_the_committed_census_lookup_works_against_the_real_repo` exercises the REAL function
        # rather than the mock the rest of these tests use.
        root = os.path.dirname(os.path.dirname(HERE))
        rel = os.path.relpath(path, root)
        out = subprocess.run(["git", "show", f"HEAD:{rel}"], cwd=root,
                             capture_output=True, timeout=30)
        if out.returncode != 0:
            return None, "the committed census could not be read from HEAD"
        return json.loads(out.stdout.decode("utf-8")), None
    except Exception as e:                                          # noqa: BLE001 — FAIL-ARMED on anything
        return None, f"the committed census could not be read: {e}"


def _census_lane_state(census_path, now=None):
    """The census lane: commit when it SAYS something, or when its published copy is about to go stale.

    ⛔ FAIL-ARMED IN EVERY DOUBT, and there are four of them: the fresh reading is unreadable, it has no
    integer count, the committed copy cannot be read, or the committed copy has no readable age. Being
    wrongly armed costs one small commit. Being wrongly silent means the account-level detector goes
    quiet while a host bills — the thing this whole module is downstream of.
    """
    fresh, err = _read_census(census_path)
    if err:
        return {"armed": True, "why": f"FAIL-ARMED — {err}. The account reading is the one thing that must "
                                      f"never be silently skipped", "evidence": {"error": err}}
    n = fresh.get("n_instances")
    if not isinstance(n, int):
        return {"armed": True, "why": "FAIL-ARMED — the fresh census carries no integer `n_instances`",
                "evidence": {"n_instances": n}}
    if n > 0:
        return {"armed": True, "why": f"the account holds {n} instance(s) — this reading is a RESULT, not a "
                                      f"heartbeat", "evidence": {"n_instances": n}}

    published, perr = _committed_census(census_path)
    if perr:
        return {"armed": True, "why": f"FAIL-ARMED — {perr}, so whether the published copy is about to go "
                                      f"stale is unknown", "evidence": {"error": perr, "n_instances": 0}}
    age = _age_seconds(published, now)
    if age is None:
        return {"armed": True, "why": "FAIL-ARMED — the published census has no readable `utc`, so its age "
                                      "is unknown", "evidence": {"utc": published.get("utc")}}
    if age >= CENSUS_KEEPALIVE_S:
        return {"armed": True, "why": f"the published census is {int(age // 60)} min old (keep-alive "
                                      f"{CENSUS_KEEPALIVE_S // 60} min) — committing so a DEAD detector "
                                      f"stays distinguishable from one that keeps reading zero",
                "evidence": {"published_age_s": int(age), "n_instances": 0}}
    return {"armed": False, "why": f"the account holds ZERO instances and the published census is only "
                                   f"{int(age // 60)} min old — this reading changes nothing and proves "
                                   f"nothing that the last one did not",
            "evidence": {"published_age_s": int(age), "n_instances": 0}}


def state(lane=None, census_path=None, now=None):
    """{'armed': bool, 'why': str, 'evidence': {...}} — ARMED means "commit as usual".

    ⛔ `census_path` RESOLVES AT CALL TIME, AND THE DEFAULT USED TO BIND AT IMPORT (fixed 2026-08-06).
    It read `census_path=CENSUS`, and a Python default argument is evaluated ONCE when the module is
    imported — so `monkeypatch.setattr(fa, "CENSUS", tmp)` rebound the module attribute and could not
    reach this signature. `main()` passes no `census_path`, so the test that asserts main's exit
    contract was silently reading the **real committed census** instead of its fixture, and therefore
    passed only while that file happened to be younger than MAX_CENSUS_AGE_S.

    ⚠ THAT IS WHAT IT DID. It turned `main` red at 511 minutes: a clock-dependent test wearing the
    costume of an exit-code assertion, and the thing it actually measured — live repo state — is
    already measured by the account-census alarms, which were reporting `CENSUS-STALE` at the time.
    A test whose pass depends on the wall clock is a test that will fail on an unrelated commit and
    send whoever gets it hunting in the wrong file.
    """
    census_path = CENSUS if census_path is None else census_path
    if lane == CENSUS_LANE:
        return _census_lane_state(census_path, now)

    doc, err = _read_census(census_path)
    if err:
        return {"armed": True, "why": f"FAIL-ARMED — {err}. Doubt about the fleet is not evidence of an "
                                      f"empty one", "evidence": {"error": err}}

    n = doc.get("n_instances")
    if not isinstance(n, int):
        return {"armed": True, "why": "FAIL-ARMED — the census carries no integer `n_instances`, so it "
                                      "cannot say the account is empty",
                "evidence": {"n_instances": n}}

    age = _age_seconds(doc, now)
    if age is None:
        return {"armed": True, "why": "FAIL-ARMED — the census carries no readable `utc`, so its age is "
                                      "unknown and its emptiness unusable",
                "evidence": {"utc": doc.get("utc")}}
    if age > MAX_CENSUS_AGE_S:
        return {"armed": True, "why": f"FAIL-ARMED — the census is {int(age // 60)} min old (limit "
                                      f"{MAX_CENSUS_AGE_S // 60} min). A stale census is an absent reading, "
                                      f"not a reading of absence",
                "evidence": {"age_s": int(age), "n_instances": n}}

    if n > 0:
        return {"armed": True, "why": f"the account holds {n} instance(s) — there is something to supervise",
                "evidence": {"n_instances": n, "age_s": int(age)}}

    return {"armed": False, "why": "the account holds ZERO instances and the census is fresh — there is "
                                   "nothing to supervise, so a heartbeat about it carries no information",
            "evidence": {"n_instances": 0, "age_s": int(age), "census_utc": doc.get("utc")}}


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    lane = argv[0] if argv else None
    st = state(lane=lane)
    print(json.dumps(st, indent=2))
    # 0 = ARMED (commit as usual) · 10 = IDLE (skip the non-event commit).
    # ⚠ NOT 1: a non-zero exit that collides with "the script crashed" would make a crash read as idle,
    # which is the fail-quiet direction this module refuses.
    return 0 if st["armed"] else 10


if __name__ == "__main__":
    sys.exit(main())
