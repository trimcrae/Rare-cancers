#!/usr/bin/env python3
"""ROADMAP ROW 27 — DID THE TWO $0 SEARCHES ACTUALLY RUN, AND WHAT DID THEY RETURN?

WHY THIS MODULE EXISTS AND WHY IT IS NOT `ddddg_known_answer_search.py`
----------------------------------------------------------------------
That module IS the two searches. This one asks a different and prior question, which row 27 raises in
its own text and which nothing in the repository could answer mechanically:

    ⛔ "NOT what the workflow's green badges say."

Row 27 records that `nr4a2-bound-ddddg-search.yml` went GREEN three times while both substantive jobs
were `skipped` with `completed_at == started_at`, because every dispatch passed `task=row26` and the
jobs' `if:` is `task == 'all' || task == 'c01a'`. **A green run is not evidence that a job ran**, and
a repository that reads conclusions off badges cannot tell the two apart. This module makes that
distinction MEASURABLE instead of narrated:

  * `badge_forensic()` reads the PUBLIC Actions API and reports, per run, the conclusion the badge
    shows AND the per-job state underneath it, flagging every zero-duration `skipped` job. No token
    is needed (public repo), so this is a $0 observation and there is no reason ever to defer it
    (CLAUDE.md §4).
  * `artifact_status()` reports whether each search's artifact actually EXISTS, because the only
    proof a search ran is the thing it was supposed to produce.
  * `timeout_verdict()` + `checkpoint_durability()` compare each job's MEASURED longest run against
    its own declared `timeout-minutes`, and ask whether a killed run's checkpoints survive.
  * `regime_test()` applies the question the row is FOR: even a found benchmark is worthless to this
    program if it cannot resolve the regime the selectivity claim needs.

⭐ AND THE FORENSIC FOUND SOMETHING ROW 27 DOES NOT SAY — THE BINDING BLOCKER IS NOT THE DISPATCH
-------------------------------------------------------------------------------------------------
Row 27's diagnosis is correct about the three GREEN runs and is not the whole story. Measured here:

  * `c01b` ran **7215 s — twice, to the second**, on two independent runs, against
    `timeout-minutes: 120`. Two runs landing on the identical duration is not an operator
    cancelling; it is a ceiling.
  * `c01a` ran **355.2 min** against `timeout-minutes: 350` — a 5.2 min overshoot, which is the
    runner tearing down a killed job.
  * the job writes per-stage checkpoints to `_ddddg_ckpt/` and **nothing ever restores them** — no
    `download-artifact`, no `actions/cache`, and the directory is committed on no ref.

⇒ **Row 27 cannot be closed by dispatching it correctly.** Every attempt buys the same first hours
and discards them. The next action is to make the search SURVIVE — restore the checkpoint at job
start, raise the timeout, or shard the scan — all of which are engineering, and engineering is free
(CLAUDE.md §5). Dispatching again without one of those is a measured no-op.

⭐ AND THE PREDICTION WAS THEN CONFIRMED PROSPECTIVELY, WHICH IS WHY THIS IS A DIAGNOSIS AND NOT A
STORY. The forensic above was written off the 2026-08-03 runs. `c01b` was RE-DISPATCHED on
2026-08-07 with `task=c01b` — correctly requested for the first time in the workflow's history, so
the dispatch defect row 27 names was fully removed — and it ran **120.6 min against its 120-minute
ceiling** and died with no artifact, exactly as predicted. Three independent c01b runs have now
terminated at their timeout. A correctly-dispatched run failing the same way is the observation that
separates the two blockers, and it settles which one binds.

⛔ THE THIRD IS THE ONE THAT MATTERS AND IT IS EASY TO SKIP
-----------------------------------------------------------
"A benchmark exists" and "a benchmark that could settle OUR question exists" are different findings,
and the first reads like the second. The resolution budget is already committed arithmetic and is
READ here, never typed (rule 1):

  * the margin the selectivity axis needs -- ~2.0 kcal/mol of TRUE margin
    (`nr4a3_basin_search` module docstring, `nr4a_paralogue_dynamics` module docstring);
  * the best case this program can RESOLVE -- 1.12 kcal/mol for the ternary kill-switch `S`
    (`valb_failure_propagation.S_BEST_CASE_RESOLVABLE_KCAL`) and 0.61 kcal/mol for the binary
    relative-FEP engine's own known-answer pass `V6` (`ddddg_known_answer_search.PREREG`);
  * what the one attempt on the relevant quantity CLASS returned -- 1.543 kcal/mol absolute error,
    AND WITH THE WRONG SIGN (`valb_failure_propagation.MEASURED["abs_error_kcal"]`).

⇒ **A known-answer set that cannot resolve the regime of interest is not a known answer for this
purpose.** `regime_test()` states that in the artifact rather than leaving a future reader to
re-derive it from three modules, which is what row 27's own existence proves does not happen.

WHAT THIS MODULE DOES NOT DO
----------------------------
It runs no search, fetches no ChEMBL record and computes no free energy. It raises no claim ceiling:
roadmap §2.3 is untouched and `C01` inherits NO validation from `V6` — the double-difference analysis
in `instrument-options.md` §2 is the one home of why, and this module points at it rather than
restating it.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

OUT = os.path.join(HERE, "row27-ddddg-precheck-status.json")

WORKFLOW = "nr4a2-bound-ddddg-search.yml"
REPO = "trimcrae/Rare-cancers"
API = "https://api.github.com/repos/%s/actions" % REPO

#: The two searches row 27 names, and the artifact each MUST produce to have run.
SEARCHES = [
    {"id": "C01a", "job": "c01a", "artifact": "ddddg-benchmark-scan.json",
     "what": ("the wide ligand-side wedge-band scan -- ChEMBL joined against the PDB for two "
              "homologous proteins x a matched congeneric ligand pair x four measured affinities x "
              "holo structures on both arms. The exact analogue of the SKEMPI scan that returned "
              "barnase_barstar_W35F from 7,085 rows.")},
    {"id": "C01b", "job": "c01b", "artifact": "ddddg-crebbp-brd4-precheck.json",
     "what": ("the CREBBP/BRD4 congeneric precheck -- the designated binary control already has both "
              "arms as real holo crystals with the SAME ligand; the only missing ingredient for a "
              "RELATIVE version is a congeneric analogue measured in BOTH proteins.")},
]


WORKFLOW_FILE = os.path.normpath(
    os.path.join(HERE, "..", "..", ".github", "workflows", WORKFLOW))


def declared_timeouts(path=WORKFLOW_FILE):
    """Each job's `timeout-minutes`, READ from the workflow rather than typed (rule 1). Pure.

    ⛔ THIS IS THE DENOMINATOR OF THE WHOLE ROW. A measured run duration means nothing until it is
    compared against the ceiling the job was given: 2.00 h is unremarkable in isolation and is
    decisive when the job's timeout is exactly 120 minutes.
    """
    out = {"_source": os.path.relpath(path, os.path.join(HERE, "..", "..")),
           "by_job": {}, "error": None}
    try:
        with open(path, encoding="utf-8") as fh:
            lines = fh.read().splitlines()
    except OSError as e:
        out["error"] = "%s: %s" % (type(e).__name__, e)
        return out
    current = None
    for ln in lines:
        m = re.match(r"^  ([A-Za-z0-9_-]+):\s*$", ln)
        if m:
            current = m.group(1)
            continue
        m = re.match(r"^\s+timeout-minutes:\s*(\d+)", ln)
        if m and current:
            out["by_job"][current] = int(m.group(1))
    return out


def checkpoint_durability(path=WORKFLOW_FILE):
    """Do a timed-out run's checkpoints survive to the next dispatch? Pure. Reads the workflow.

    ⛔ THIS IS WHY THE TIMEOUT IS TERMINAL RATHER THAN AN INCONVENIENCE. CLAUDE.md §6's checkpoint
    rule is explicit: checkpoints must be uploaded AS THEY ARE WRITTEN, because "a default
    end-of-job upload loses ALL partial work on a timeout or crash". `c01a` obeys the first half of
    the rule and not the second — it checkpoints per stage and per target into `_ddddg_ckpt/`, and
    the only thing that ever leaves the runner is an `actions/upload-artifact` step. There is no
    `actions/cache`, no `download-artifact`, and no restore of any kind at the start of the job.

    ⇒ Every re-dispatch begins at stage 1. Combined with a search that has never fit inside its
    `timeout-minutes`, that makes the row STRUCTURALLY unable to close by dispatching: each attempt
    buys the same first N hours of work and then throws them away. The fix is engineering, which is
    free (CLAUDE.md §5) — restore the checkpoint at job start from the previous run's artifact or a
    committed copy, and/or shard the scan — not more dispatches.
    """
    out = {"_source": os.path.relpath(path, os.path.join(HERE, "..", "..")),
           "writes_checkpoints": None, "has_restore_step": None,
           "checkpoints_committed_anywhere": False, "error": None}
    try:
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
    except OSError as e:
        out["error"] = "%s: %s" % (type(e).__name__, e)
        return out
    out["writes_checkpoints"] = "_ddddg_ckpt" in text
    # ⚠ THE RESTORE MUST WORK ACROSS DISPATCHES, NOT ONLY WITHIN ONE RUN. An `actions/cache` whose
    # key is unique per run and which declares no `restore-keys` hits only on a re-run of that same
    # run, which is indistinguishable from no restore at all for this defect. So the presence of a
    # cache step is necessary and not sufficient, and this reads the prefix key too.
    out["has_restore_step"] = bool(re.search(r"download-artifact|actions/cache", text))
    out["restore_survives_across_dispatches"] = bool(
        out["has_restore_step"] and re.search(r"restore-keys", text))
    # ⛔⛔ AND A RESTORE IS HALF A MECHANISM. THIS DETECTOR PRINTED A GREEN VERDICT OVER THE MISSING
    # HALF FOR 26 DAYS (measured 2026-09-02, and it is the second checker in this repository to put
    # a tick over the failure it existed to find). `actions/cache@v4` restores in its MAIN step and
    # saves in a POST step whose condition is `post-if: "success()"` — read from the action's own
    # `action.yml` at the v4 ref, not remembered. A job killed by `timeout-minutes` is CANCELLED,
    # which is not success, and the only runs that reach a checkpoint worth keeping are exactly the
    # runs that time out. So the composite action's save can never fire on this workflow's one
    # failure mode, and every re-dispatch restored an empty cache while this function said the
    # checkpoint was durable.
    # ★ The split API is what makes it real: `actions/cache/save@v4` is a MAIN step with no
    # `post-if`, so `if: always()` on it means what it says.
    out["uses_composite_cache_action"] = bool(re.search(r"uses:\s*actions/cache@", text))
    saves = re.findall(r"(?s)- name:[^\n]*\n(.{0,400}?uses:\s*actions/cache/save@)", text)
    out["has_save_step"] = bool(saves)
    out["save_is_unconditional"] = bool(saves) and all(
        re.search(r"^\s*if:\s*always\(\)\s*$", blk, re.M) for blk in saves)
    out["save_can_fire_after_a_timeout"] = bool(
        out["has_save_step"] and out["save_is_unconditional"]
        and not out["uses_composite_cache_action"])
    out["_why_the_save_half_is_checked"] = (
        "actions/cache@v4 declares `post-if: \"success()\"` in its own action.yml, so its save "
        "step cannot run on a job killed by timeout-minutes — and a timeout is the only way this "
        "workflow ever produces a checkpoint worth keeping. A restore without a reachable save is "
        "a mechanism that reads as fixed and banks nothing.")
    # ⚠ AND `always()` IS ITSELF UNREACHABLE AFTER A JOB-LEVEL TIMEOUT: a cancelled job runs no
    # further steps of any condition. So the save is only reachable if the WORK steps carry their
    # own `timeout-minutes` and expire before the job does.
    out["search_steps_have_their_own_timeout"] = bool(
        re.search(r"timeout-minutes:\s*\d+\s*\n\s*run:.*ddddg_known_answer_search", text)
        or re.search(r"(?s)timeout-minutes:\s*\d+.{0,200}?ddddg_known_answer_search", text))
    if out["writes_checkpoints"] and out["has_restore_step"] \
            and not out["save_can_fire_after_a_timeout"]:
        out["verdict"] = (
            "⛔ THE RESTORE IS PRESENT AND THE SAVE CANNOT FIRE, WHICH IS THE SAME OUTCOME WITH A "
            "GREEN LOOK. actions/cache@v4 saves in a post step gated on success(); a job killed by "
            "timeout-minutes is cancelled, and a timeout is how this workflow's checkpoints are "
            "produced. Use actions/cache/save@v4 with `if: always()`, placed AFTER the search "
            "steps, and give every search step its own timeout below the job's so the job is never "
            "cancelled and `always()` is reachable.")
        out["_consequence_for_the_row"] = (
            "row 27 still cannot accumulate across dispatches. Every attempt buys the same first "
            "hours and discards them.")
        return out
    if out["writes_checkpoints"] and not out["has_restore_step"]:
        out["verdict"] = (
            "⛔ CHECKPOINTS ARE WRITTEN AND NEVER RESTORED. The job writes per-stage checkpoints and "
            "uploads them only as a post-hoc run artifact; nothing reads them back at the start of the "
            "next run, and `_ddddg_ckpt/` is committed on no ref. So a timeout loses the whole scan and "
            "the next dispatch restarts at stage 1 — the exact loss CLAUDE.md §6's checkpoint rule "
            "exists to prevent.")
        out["_consequence_for_the_row"] = (
            "row 27 cannot be closed by dispatching. Its next action is to make the search survive: "
            "restore the checkpoint at job start, raise the timeout, or shard the scan. All three are "
            "engineering, which costs nothing.")
    elif out["writes_checkpoints"] and not out["restore_survives_across_dispatches"]:
        out["verdict"] = (
            "⚠ A RESTORE STEP EXISTS BUT MAY NOT SURVIVE A NEW DISPATCH. Without `restore-keys` a "
            "run-scoped cache key hits only on a re-run of the same run, which leaves the original "
            "defect intact for the case that matters. Read the key before relying on this.")
        out["_consequence_for_the_row"] = (
            "treat row 27 as still structurally blocked until the prefix key is confirmed.")
    else:
        # ✅ DISCHARGED 2026-08-07. Recorded rather than deleted, per the finding's own instruction:
        # the measurement that produced it (c01b at 7215 s TWICE to the second; c01a at 355.2 min
        # against a 350-minute ceiling) is what justified the fix, and a discharged finding whose
        # evidence is erased cannot be re-checked if the fix is ever reverted.
        out["verdict"] = (
            "✅ CHECKPOINTS ARE WRITTEN, RESTORED, AND SAVED ON A PATH A TIMEOUT CAN REACH. The "
            "restore carries `restore-keys` so it resumes across DISPATCHES rather than only "
            "across re-runs of one run; the save is `actions/cache/save@v4` — a MAIN step, so its "
            "`if: always()` is honoured — placed after the search; and every search step carries "
            "its own `timeout-minutes` below the job's, without which a job-level timeout cancels "
            "the job and no `always()` step runs at all. "
            "⚠ Superseded, retained: '⛔ CHECKPOINTS ARE WRITTEN AND NEVER RESTORED … the next "
            "dispatch restarts at stage 1.' True when measured — three c01b dispatches died at the "
            "120-minute ceiling with zero cumulative progress. "
            "⚠ Superseded, retained: '✅ CHECKPOINTS ARE WRITTEN AND RESTORED … the fix is the "
            "cache step.' That reading was GREEN OVER A HOLE for 26 days: the restore was there "
            "and `actions/cache@v4` saves in a post step gated on `success()`, which a timed-out "
            "job never is.")
        out["_consequence_for_the_row"] = (
            "row 27 can now accumulate across dispatches, so a dispatch is worth taking again. ⛔ It "
            "is NOT closed: an accumulating search still has to finish, and until one run reports "
            "coverage the gate reads UNDETERMINED, because a search-shaped null over an unfinished "
            "scan is an absent reading and not a reading of absence.")
    return out


def timeout_verdict(summary, timeouts):
    """Did each search hit its own ceiling? Pure. The finding row 27 does not have.

    A run cancelled at (or fractionally past) its declared `timeout-minutes` is a TIMEOUT that the
    Actions API reports as `cancelled`. The distinction matters enormously: "nobody asked for it" is
    fixed by dispatching correctly, and "it does not fit in its timeout" is not fixed by dispatching
    at all, however many times.
    """
    rows = {}
    longest = summary.get("longest_observed_run_h") or {}
    for job, limit_min in (timeouts.get("by_job") or {}).items():
        if job not in ("c01a", "c01b"):
            continue
        obs_h = longest.get(job)
        limit_h = limit_min / 60.0
        hit = obs_h is not None and obs_h >= limit_h * 0.98
        rows[job] = {
            "declared_timeout_minutes": limit_min,
            "declared_timeout_h": round(limit_h, 2),
            "longest_observed_run_h": obs_h,
            "longest_observed_run_min": (round(obs_h * 60, 1) if obs_h is not None else None),
            "overshoot_min": (round(obs_h * 60 - limit_min, 1) if obs_h is not None else None),
            "_overshoot_is_runner_teardown": (
                "a job killed by `timeout-minutes` records a few minutes MORE than its limit, "
                "because the runner still tears the job down after the kill. An overshoot of a few "
                "minutes is the signature of a timeout; a duration far BELOW the limit is not."),
            "reached_its_own_timeout": hit,
            "reading": (
                "⛔ HIT THE CEILING. The longest observed run reached this job's declared "
                "timeout-minutes, so the API's `cancelled` is a TIMEOUT, not an operator "
                "cancellation. Re-dispatching as committed cannot produce an artifact — the search "
                "does not fit in the time it is given."
                if hit else
                "did not reach its declared timeout; cancellation was not a timeout"),
        }
    any_hit = any(r["reached_its_own_timeout"] for r in rows.values())
    return {
        "per_job": rows,
        "timeouts_source": timeouts.get("_source"),
        "error": timeouts.get("error"),
        "⭐_the_finding": (
            "⛔ ROW 27 DIAGNOSES THE WRONG BLOCKER — or rather, only the first of two. Its diagnosis "
            "(every dispatch passed `task=row26`, so the substantive jobs were never requested) is "
            "TRUE of the three green runs and is a real defect. But it is not what is stopping the "
            "row now: both searches HAVE been requested on other runs, both burned real wall time, "
            "and both reached their own declared `timeout-minutes` — c01b landing on 7215 s TWICE, "
            "to the second, on two independent runs, which no operator cancellation produces. "
            "A search that exceeds its "
            "timeout cannot complete however correctly it is dispatched. ⇒ THE NEXT ACTION FOR ROW "
            "27 IS NOT 'DISPATCH IT PROPERLY' — that has now been done and is in flight — IT IS TO "
            "MAKE THE SEARCH FIT: raise the timeout, or shard it, or lean on the per-stage "
            "checkpointing the workflow already writes so a re-dispatch resumes instead of "
            "restarting. The checkpoints exist (`_ddddg_ckpt/`); what is missing is a run that "
            "survives long enough to use them."
            if any_hit else
            "no search has been observed reaching its declared timeout"),
    }


def _duration_s(started, completed):
    """Seconds between two ISO-8601 Z timestamps, or None. Pure. May be NEGATIVE — see `zero`."""
    if not started or not completed:
        return None
    import datetime as _dt
    try:
        a = _dt.datetime.strptime(started, "%Y-%m-%dT%H:%M:%SZ")
        b = _dt.datetime.strptime(completed, "%Y-%m-%dT%H:%M:%SZ")
    except (TypeError, ValueError):
        return None
    return (b - a).total_seconds()


def _nonpositive_duration(started, completed):
    """True when a job occupied no wall time at all — the tell that it never ran. Pure."""
    d = _duration_s(started, completed)
    return d is not None and d <= 0


def _get(url):
    """One public, unauthenticated Actions API read. Returns (payload, error)."""
    try:
        raw = subprocess.run(["curl", "-sS", "-m", "45", url],
                             capture_output=True, text=True, check=False)
        if raw.returncode != 0:
            return None, "curl rc=%d: %s" % (raw.returncode, (raw.stderr or "")[:200])
        return json.loads(raw.stdout), None
    except (ValueError, OSError) as e:                       # noqa: BLE001
        return None, "%s: %s" % (type(e).__name__, e)


def badge_forensic(per_page=40):
    """Per run: what the BADGE says, and what the jobs underneath it actually did.

    ⛔ THE DISCRIMINATOR IS `completed_at == started_at` ON A `skipped` JOB. A job that was never
    requested and a job that ran and found nothing both leave a green run; only the per-job record
    separates them, and that record is one free API call away.
    """
    out = {"_source": "%s/workflows/%s/runs" % (API, WORKFLOW),
           "_no_token_needed": "public repository -- this reading costs $0 and is re-checkable",
           "workflow": WORKFLOW, "runs": [], "error": None}
    runs, err = _get("%s/workflows/%s/runs?per_page=%d" % (API, WORKFLOW, per_page))
    if err or not isinstance(runs, dict):
        out["error"] = err or "unexpected payload"
        return out
    out["total_runs"] = runs.get("total_count")
    for r in runs.get("workflow_runs") or []:
        row = {"run_id": r.get("id"), "created_at": r.get("created_at"),
               "event": r.get("event"), "head_branch": r.get("head_branch"),
               "badge_conclusion": r.get("conclusion"), "status": r.get("status"),
               "jobs": [], "jobs_error": None}
        jobs, jerr = _get("%s/runs/%s/jobs" % (API, r.get("id")))
        if jerr or not isinstance(jobs, dict):
            row["jobs_error"] = jerr or "unexpected payload"
        else:
            for j in jobs.get("jobs") or []:
                # ⚠ `completed_at == started_at` IS TOO STRICT AND UNDER-DETECTS SKIPS. Measured on
                # run 30776566810: a skipped job reports started_at 01:20:53Z and completed_at
                # 01:20:52Z — completion one second BEFORE start. Exact equality scores that as a
                # real duration, i.e. the discriminator fails in the direction that makes a job that
                # never ran look like one that did, which is the only direction that matters here.
                zero = _nonpositive_duration(j.get("started_at"), j.get("completed_at"))
                dur = _duration_s(j.get("started_at"), j.get("completed_at"))
                row["jobs"].append({
                    "name": j.get("name"), "status": j.get("status"),
                    "conclusion": j.get("conclusion"),
                    "started_at": j.get("started_at"), "completed_at": j.get("completed_at"),
                    "zero_duration": zero,
                    "duration_s": dur,
                    "duration_h": (round(dur / 3600.0, 2) if dur else dur),
                    # RAN BUT NEVER FINISHED. ⛔ THE CATEGORY ROW 27 HAS NO WORD FOR, and the one
                    # that carries the most information: a job that burned real wall time and was
                    # then cancelled tells you the search's RUNTIME, which is what decides whether
                    # it can finish inside a job timeout at all.
                    "ran_but_did_not_complete": bool(
                        j.get("name") in ("c01a", "c01b")
                        and j.get("conclusion") in ("cancelled", "failure", "timed_out")
                        and dur is not None and dur > 60),
                    "did_substantive_work": bool(
                        j.get("conclusion") == "success" and not zero
                        and j.get("name") in ("c01a", "c01b")),
                    # ⛔ A JOB THAT IS RUNNING RIGHT NOW IS NOT A JOB THAT NEVER RAN, and the first
                    # version of this field could not tell them apart: `did_substantive_work`
                    # requires conclusion == "success", so an in-flight c01a scored False and the
                    # summary would have printed "STILL never executed" about a job actively
                    # executing. That is this module's own absent-reading trap, in the module written
                    # to catch absent readings.
                    "currently_running": bool(
                        j.get("status") in ("in_progress", "queued")
                        and j.get("name") in ("c01a", "c01b")),
                })
        out["runs"].append(row)

    # The summary row 27 asserts, RE-MEASURED rather than quoted.
    substantive = {s["job"]: [] for s in SEARCHES}
    running = {s["job"]: [] for s in SEARCHES}
    requested = {s["job"]: [] for s in SEARCHES}
    aborted = {s["job"]: [] for s in SEARCHES}
    for r in out["runs"]:
        for j in r["jobs"]:
            if j["name"] not in substantive:
                continue
            if j["did_substantive_work"]:
                substantive[j["name"]].append(r["run_id"])
            if j["currently_running"]:
                running[j["name"]].append(r["run_id"])
            if j.get("ran_but_did_not_complete"):
                aborted.setdefault(j["name"], []).append(
                    {"run_id": r["run_id"], "conclusion": j["conclusion"],
                     "duration_h": j["duration_h"]})
            # REQUESTED = the dispatch actually asked for this job, whatever became of it. A
            # zero-duration skip means it was never requested; anything else means it was.
            if not (j["conclusion"] == "skipped" and j["zero_duration"]):
                requested[j["name"]].append(r["run_id"])
    out["summary"] = {
        "runs_in_which_each_search_was_REQUESTED_at_all": requested,
        "runs_in_which_each_search_is_RUNNING_now": running,
        "runs_in_which_each_search_RAN_BUT_DID_NOT_COMPLETE": aborted,
        "longest_observed_run_h": {
            k: (max((a["duration_h"] or 0) for a in v) if v else None) for k, v in aborted.items()},
        "_four_categories_not_two": (
            "REQUESTED / RUNNING / RAN-BUT-DID-NOT-COMPLETE / did-substantive-work are four "
            "different states, and collapsing them loses the two facts that matter most: a live job "
            "reads as one that never ran, and a job that burned hours before being cancelled reads "
            "the same as one that was never requested."),
        "⛔_correction_to_row_27s_own_text": (
            "Row 27 says 'NEITHER SEARCH HAS EVER RUN'. The stronger claim it can support is that "
            "NEITHER HAS EVER COMPLETED — which is the load-bearing half and is still true, no "
            "artifact having ever been produced. But `runs_in_which_each_search_RAN_BUT_DID_NOT_"
            "COMPLETE` shows real wall time was burned on both before cancellation, and "
            "`longest_observed_run_h` is the number that actually bears on the plan: it is the "
            "measured lower bound on how long the search NEEDS, and it must be compared against the "
            "job's own timeout before dispatching again. A search whose runtime exceeds its timeout "
            "cannot complete however many times it is dispatched, and that is a different blocker "
            "from the one row 27 diagnosed."),
        "n_runs_seen": len(out["runs"]),
        "n_badge_success": sum(1 for r in out["runs"] if r["badge_conclusion"] == "success"),
        "n_badge_cancelled": sum(1 for r in out["runs"] if r["badge_conclusion"] == "cancelled"),
        "runs_in_which_each_search_did_substantive_work": substantive,
        "_the_row_27_claim": (
            "row 27 records that the workflow went green three times with both substantive jobs "
            "skipped at zero duration. The `runs_in_which_...` map above is that claim re-measured: "
            "an empty list for a job means NO run has ever executed it, however many badges are "
            "green."),
    }
    return out


def artifact_status(root=HERE):
    """Does each search's output actually exist? The only proof a search ran is its product."""
    rows = []
    for s in SEARCHES:
        path = os.path.join(root, s["artifact"])
        row = {"search": s["id"], "what_it_is": s["what"], "artifact": s["artifact"],
               "exists": os.path.exists(path), "verdict": None, "error": None}
        if row["exists"]:
            try:
                with open(path, encoding="utf-8") as fh:
                    doc = json.load(fh)
                v = doc.get("verdict") or {}
                row["verdict"] = v.get("decision") if isinstance(v, dict) else v
                row["n_gradeable"] = (doc.get("scored") or {}).get("n_gradeable") \
                    if isinstance(doc.get("scored"), dict) else doc.get("n_gradeable")
            except (OSError, ValueError) as e:
                row["error"] = "%s: %s" % (type(e).__name__, e)
        else:
            row["_absent_means"] = (
                "the search has not produced an artifact ON THIS REF. That is an ABSENT READING, not "
                "the finding that no benchmark exists -- and per CLAUDE.md §7 check WHICH ref the "
                "producing workflow writes to before reading absence as a fact.")
        rows.append(row)
    return rows


def resolution_budget():
    """The committed arithmetic, READ from its homes. Never typed here (rule 1)."""
    budget = {"_why": ("row 27 decides whether a known answer can be BOUGHT. This decides whether a "
                       "bought one would be USABLE, which is a separate question and the one that "
                       "actually binds."),
              "reads": [], "error": None}
    try:
        import valb_failure_propagation as vfp
        budget["reads"].append({
            "quantity": "the one attempt on the relevant quantity CLASS (ddG_coop, a "
                        "ternary-minus-binary double difference)",
            "value_kcal": vfp.MEASURED["abs_error_kcal"],
            "home": "valb_failure_propagation.MEASURED['abs_error_kcal']",
            "narrative_home": "paper §2.11",
            "⚠": ("AND IT CAME BACK WITH THE WRONG SIGN. An error larger than the effect is a "
                  "non-measurement; an error larger than the effect AND of the wrong sign is a "
                  "result that would have pointed a design in the opposite direction."),
        })
        budget["reads"].append({
            "quantity": "best case this program can RESOLVE on the ternary kill-switch S",
            "value_kcal": vfp.S_BEST_CASE_RESOLVABLE_KCAL,
            "home": "valb_failure_propagation.S_BEST_CASE_RESOLVABLE_KCAL",
        })
        budget["reads"].append({
            "quantity": "the designed effect S is trying to resolve",
            "value_kcal": list(vfp.S_DESIGNED_EFFECT_KCAL),
            "home": "valb_failure_propagation.S_DESIGNED_EFFECT_KCAL",
        })
    except Exception as e:                                   # noqa: BLE001
        budget["error"] = "valb_failure_propagation unreadable: %s: %s" % (type(e).__name__, e)
    try:
        import ddddg_known_answer_search as dd
        budget["reads"].append({
            "quantity": "the BINARY relative-FEP engine's own known-answer band (V6's pass)",
            "value_kcal": dd.PREREG["engine_band_kcal_fallback"],
            "home": "ddddg_known_answer_search.PREREG['engine_band_kcal_fallback'] (read from "
                    "instrument-options.json at run time; this is its fallback)",
            "scope": ("⚠ V6 passed WITHIN ONE POCKET. A ligand-side double difference across two "
                      "proteins inherits NONE of it -- instrument-options.md §2 is the one home of "
                      "the argument and it is not restated here."),
        })
        budget["reads"].append({
            "quantity": "the wedge band C01a searches in",
            "value_kcal": list(dd.PREREG["band_kcal"]),
            "home": "ddddg_known_answer_search.PREREG['band_kcal']",
        })
    except Exception as e:                                   # noqa: BLE001
        budget.setdefault("error", "")
        budget["error"] = (budget.get("error") or "") + \
            " | ddddg_known_answer_search unreadable: %s: %s" % (type(e).__name__, e)
    budget["margin_the_selectivity_axis_needs_kcal"] = 2.0
    budget["_margin_home"] = ("nr4a3_basin_search and nr4a_paralogue_dynamics module docstrings, "
                              "both of which state '~2.0 kcal/mol of true margin against a best-case "
                              "resolvable 1.12'. Quoted, not derived here.")
    return budget


def regime_test(artifacts, budget):
    """Does a found benchmark reach the regime that matters? Pure. The question row 27 is FOR."""
    ran = [a for a in artifacts if a["exists"]]
    found = [a for a in ran if a.get("verdict") and "STOP" not in str(a["verdict"])]
    if not ran:
        state = "UNDETERMINED"
        sentence = (
            "Neither search has produced an artifact on this ref, so nothing is known about whether "
            "a paralogue-scale known answer for the ligand-side ΔΔΔG exists. ⛔ This is NOT the "
            "finding that none exists — it is the finding that the question is still unasked, which "
            "is exactly the state row 27 was written to record.")
    elif not found:
        state = "STOP_NO_REFERENCE"
        sentence = (
            "Every search that ran returned a refusal on evidence. C01 — the register's best "
            "identifiable option — cannot be bought a known answer at paralogue scale from the "
            "sources searched. ⭐ A refusal on evidence is a better outcome than a budget hold: it "
            "closes the instrument rather than leaving it untested, and the pmx arm has already "
            "demonstrated the value of that state.")
    else:
        state = "FOUND_PENDING_REGIME_TEST"
        sentence = (
            "At least one search returned a candidate benchmark. ⛔ FINDING A BENCHMARK IS NOT "
            "PASSING ONE, and the prior question is whether the candidate reaches the regime: the "
            "selectivity axis needs ~2.0 kcal/mol of TRUE margin, and the one attempt on this "
            "quantity CLASS missed by more than the effect AND with the wrong sign. A candidate "
            "whose reference value sits inside the engine's own band cannot distinguish a right "
            "answer from a wrong one and is not a known answer FOR THIS PURPOSE, however real the "
            "measurement is.")
    return {
        "state": state,
        "sentence": sentence,
        "resolution_budget": budget,
        "the_binding_constraint": (
            "A known-answer set that cannot resolve the regime of interest is not a known answer for "
            "this purpose. Row 27's deliverable is therefore two-part: does a benchmark EXIST, and "
            "does it SIT IN THE BAND. The second is not automatic and has never been checked for any "
            "instrument in §3.1."),
        "inherits_nothing_from_V6": (
            "⚠ C01 inherits NO validation from V6. The double-difference analysis in "
            "instrument-options.md §2 is the one home of why: the cancellation removes exactly the "
            "error classes V6 also removes and leaves standing exactly the classes V6 never "
            "measured, so the two are different linear combinations of DISJOINT error terms."),
        "claim_ceiling": (
            "roadmap §2.3 unchanged. No requirement may be claimed above the validation status of "
            "the instrument producing it, and C01 is at `proposed` whatever these searches return."),
    }


def map_edits_required(badge, artifacts, regime, tmo=None, ckpt=None):
    """Routed roadmap edits — DESCRIBED, NOT APPLIED. Checked by verify_map_edits.py."""
    summary = badge.get("summary") or {}
    subst = summary.get("runs_in_which_each_search_did_substantive_work") or {}
    live = summary.get("runs_in_which_each_search_is_RUNNING_now") or {}
    ever = {k: ("completed at least once" if v else
                ("RUNNING NOW (first ever request)" if live.get(k) else "never been requested"))
            for k, v in subst.items()}
    return [
        {
            "section": "§10.1 row 27",
            "anchor": ("**The two $0 searches for a paralogue-scale known answer for the ligand-side "
                       "ΔΔΔG**"),
            "current_text": None,
            "proposed_text": (
                "Row 27 status re-measured %s: `c01a` has %s executed substantively, `c01b` has %s. "
                "Regime state `%s`. One home for the forensic and the regime arithmetic: "
                "[`row27-ddddg-precheck-status.json`](../modalities/row27-ddddg-precheck-status.json). "
                "⛔ The row's warning stands and is now MECHANICAL rather than narrated — "
                "`badge_forensic` prints the badge conclusion beside the per-job zero-duration flag, "
                "so a green run can no longer be read as a job having run."
                % ("from the public Actions API",
                   "NOW" if ever.get("c01a") else "STILL never",
                   "NOW" if ever.get("c01b") else "STILL never",
                   regime["state"])),
            "why": ("the row asserts a badge-versus-reality discrepancy in prose; this makes it a "
                    "reading that can be re-taken for $0 instead of a claim that ages"),
            "artifact": "research/modalities/row27-ddddg-precheck-status.json:badge_forensic.summary",
        },
        {
            "section": "§10.1 row 27",
            "anchor": None,
            "where": ("row 27's `state` and `next action` columns. The row's diagnosis — every "
                      "dispatch passed `task=row26` so the jobs never ran — is TRUE of the three "
                      "green runs and is NOT the binding blocker. This edit adds the second one."),
            "current_text": None,
            "proposed_text": (
                "⛔ **AND THE BINDING BLOCKER IS NOT THE DISPATCH — IT IS THE TIMEOUT.** Measured "
                "from the public Actions API: `c01b` has twice run to **2.00 h** against a declared "
                "`timeout-minutes: 120`, and `c01a` to **5.92 h** against `timeout-minutes: 350`. "
                "The API reports both as `cancelled`; they are TIMEOUTS. ⛔ And the job writes "
                "per-stage checkpoints to `_ddddg_ckpt/` that **nothing ever restores** — no "
                "`download-artifact`, no `actions/cache`, and the directory is committed on no ref — "
                "so every re-dispatch restarts at stage 1 and buys the same first hours again. "
                "⇒ **This row cannot be closed by dispatching it correctly.** Its next action is to "
                "make the search survive: restore the checkpoint at job start, raise the timeout, or "
                "shard the scan — all engineering, all $0. One home: "
                "[`row27-ddddg-precheck-status.json`](../modalities/row27-ddddg-precheck-status.json) "
                "→ `timeout_verdict` and `checkpoint_durability`."),
            "why": ("the row's stated next action ('dispatch it properly') has now been done and "
                    "cannot succeed; leaving that as the next action sends the next session to "
                    "re-run a job that has already been measured not to fit"),
            "artifact": "research/modalities/row27-ddddg-precheck-status.json:timeout_verdict",
        },
        {
            "section": "§10.1 row 27",
            "anchor": None,
            "where": ("beside row 27, as a second sentence of its `next action` column: the row asks "
                      "only whether a known answer can be BOUGHT, and never asks whether a bought "
                      "one would be USABLE. The regime arithmetic is committed in three other "
                      "modules and is re-derived every time it is needed."),
            "current_text": None,
            "proposed_text": (
                "⛔ AND THE ROW HAS A SECOND HALF: a known-answer set that cannot resolve the regime "
                "of interest is not a known answer for this purpose. The selectivity axis needs "
                "~2.0 kcal/mol of true margin; the one attempt on this quantity class returned "
                "1.543 kcal/mol absolute error WITH THE WRONG SIGN. One home for the arithmetic: "
                "[`row27-ddddg-precheck-status.json`](../modalities/row27-ddddg-precheck-status.json) "
                "→ `regime_test.resolution_budget`."),
            "why": ("'a benchmark exists' reads like 'a benchmark that could settle our question "
                    "exists' and they are different findings"),
            "artifact": "research/modalities/row27-ddddg-precheck-status.json:regime_test",
        },
    ]


def build(skip_network=False):
    badge = ({"_skipped": "network read not attempted", "runs": [], "summary": {}}
             if skip_network else badge_forensic())
    timeouts = declared_timeouts()
    tmo = timeout_verdict(badge.get("summary") or {}, timeouts)
    ckpt = checkpoint_durability()
    artifacts = artifact_status()
    budget = resolution_budget()
    regime = regime_test(artifacts, budget)
    return {
        "_what": ("ROADMAP ROW 27 — whether the two $0 ΔΔΔG known-answer searches have actually run, "
                  "what they returned, and whether anything they could return would reach the regime "
                  "the selectivity claim needs."),
        "_cost": "$0 — public Actions API reads and CPU. No GPU, no rental, no token.",
        "_scope": ("Runs no search and computes no free energy. Nothing here is a result about "
                   "binding, selectivity, degradation, efficacy or safety."),
        "badge_forensic": badge,
        "timeout_verdict": tmo,
        "checkpoint_durability": ckpt,
        "artifact_status": artifacts,
        "regime_test": regime,
        "map_edits_required": map_edits_required(badge, artifacts, regime, tmo, ckpt),
    }


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", default=OUT)
    ap.add_argument("--skip-network", action="store_true",
                    help="offline: emit the artifact without the Actions API forensic")
    args = ap.parse_args(argv)
    doc = build(skip_network=args.skip_network)
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, indent=1)
        fh.write("\n")
    print(json.dumps({"badge_summary": doc["badge_forensic"].get("summary"),
                      "artifact_status": [{k: a[k] for k in ("search", "exists", "verdict")}
                                          for a in doc["artifact_status"]],
                      "regime_state": doc["regime_test"]["state"]}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
