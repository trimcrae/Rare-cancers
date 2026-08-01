#!/usr/bin/env python3
"""The orchestrator's "In flight" board, DERIVED from artifacts — never carried forward from a prior report.

★★ WHY THIS EXISTS (trimcrae, 2026-08-01: *"Those are the kinds of things you should be evaluating and
solving without me having to prod you on it."*). On 2026-08-01 the agent's hand-written in-flight table
carried, across several consecutive reports:

  * a `.chk` prune smoke as "status unknown" for hours — the ACCOUNT census answered it in one call;
  * two subagents as "resume unverified" — `git log` answered it in one call, and the answer was that
    neither had run at all;
  * a 5a-KS leg as RUNNING after it had already landed.

None of those was a hard problem. Every one of them was **a row copied forward from the previous message
and updated only where the agent happened to look.** A row nobody re-checked renders identically to a row
that was re-checked and found unchanged — which is exactly the failure class the fleet's own board fixes
with `_As of … STALE (> 15 min)` and "this row is THAT report, not a current reading". The reporting layer
had the discipline; the reporter did not.

So: **the in-flight board is generated, like every other total in this repo (CLAUDE.md §1 — a total is
DERIVED, never typed).** Nothing here is remembered. Every row is read from a committed artifact or from
the account, this run, and a row whose evidence cannot be read says so rather than inheriting its last
known value.

THREE SOURCES, because no single one can see everything:

  1. `inflight-board-all.md`  — the per-lane GPU rows, with each lane's own staleness already computed.
     Cannot see: work with no lane, and lanes whose fragment writer is broken.
  2. `ternary-vast-account-census.json` — every instance the Vast account holds. This is the ONLY source
     that can see a host no lane claims, which is the whole orphan failure mode; a per-lane board filters
     to one mode's labels and structurally cannot.
  3. `git log` over non-CI commits — the only evidence that a SUBAGENT is alive. There is no artifact for
     "an agent is working", so liveness is inferred from work landing. `SendMessage` returning "resumed in
     the background" is NOT evidence and must never be treated as any: three separate resumes reported
     exactly that on 2026-08-01 and did nothing.

⚠ THE UNKNOWN BUDGET. A row may report UNKNOWN once. The second consecutive report of the same UNKNOWN is
not a status — it is an unanswered question, and `--since-report` marks it ESCALATE. That rule is here
because "status unknown" survived many reports untouched while the answer was one API call away.
"""
from __future__ import annotations

import json
import subprocess
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

#: A lane's fragment is its heartbeat; past this it is reporting the past. Imported rather than re-typed
#: so it cannot drift from the fleet's own rendering (`inflight_board` documents the same constant).
STALE_MIN = 15.0

#: Commit subjects that are machine chatter, not an agent working. Liveness must not be satisfied by the
#: very tick-artifacts that keep committing whether or not anyone is doing anything — that would make an
#: abandoned session look busy forever, which is this module's own failure mode one level up.
CI_NOISE = ("(CI)", "autoscale tick", "vast rate forensics", "market snapshot",
            "in-flight board", "lane staleness watch", "board fragment")


def _git(*args: str) -> str:
    return subprocess.run(("git", "-C", str(REPO)) + args,
                          capture_output=True, text=True, timeout=60).stdout.strip()


def _read(rel: str):
    """A committed artifact, or None. NEVER a remembered value — see the module docstring."""
    raw = _git("show", f"origin/main:{rel}")
    if not raw:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return raw


def billing_now() -> dict:
    """What the ACCOUNT says is billing — the only view that can see a host no lane claims.

    Returns `{"unreadable": why}` rather than an empty list when the census cannot be read. An absent
    reading is not a reading of absence (CLAUDE.md §4): "no census" and "no instances" are opposite
    findings and a caller that conflates them will report a quiet fleet while an orphan bills.
    """
    doc = _read("research/modalities/ternary-vast-account-census.json")
    if not isinstance(doc, dict):
        return {"unreadable": "ternary-vast-account-census.json absent or unparseable"}
    rows = doc.get("instances") or []
    age = (time.time() - _iso_epoch(doc.get("utc"))) / 60.0 if doc.get("utc") else None
    return {"utc": doc.get("utc"), "age_min": age, "n": len(rows),
            "stale": (age is not None and age > STALE_MIN),
            "instances": [{"id": r.get("id"), "label": r.get("label"),
                           "gpu": r.get("gpu_name"), "status": r.get("actual_status")} for r in rows]}


def _iso_epoch(s):
    try:
        return time.mktime(time.strptime(str(s).replace("Z", ""), "%Y-%m-%dT%H:%M:%S")) - time.timezone
    except (ValueError, TypeError):
        return 0.0


def lane_rows() -> list[dict]:
    """Each lane's section of the merged board, with the lane's OWN staleness verdict carried through.

    The staleness is not recomputed here: `inflight_board` already renders `STALE (> 15 min)` into the
    section header, and re-deriving it would be a second home for one fact.
    """
    md = _read("research/modalities/inflight-board-all.md")
    if not isinstance(md, str):
        return [{"lane": "(none)", "unreadable": "inflight-board-all.md absent"}]
    out, lane, cur = [], None, None
    in_fence = False
    for line in md.splitlines():
        if line.startswith("## "):
            lane, cur = line[3:].strip(), None
            in_fence = False
        elif line.startswith("_As of") and lane:
            cur = {"lane": lane, "as_of": line.strip("_ "), "stale": "STALE" in line, "legs": []}
            out.append(cur)
        elif line.startswith("```"):
            in_fence = not in_fence
        elif in_fence and cur is not None and line.strip() \
                and not line.startswith(("LEG", "---", "IN-FLIGHT BOARD:")):
            # ★★ THE LEG ROWS THEMSELVES, VERBATIM (2026-08-01). This function used to return only the
            # section HEADERS, so anyone reporting per-leg state had to transcribe the rows by hand — and a
            # hand-copied row is a row that survives on inertia. Measured that afternoon, in one session:
            # a leg reported RUNNING at 98.9% had already LANDED (its ETA was 11 min in the past and the row
            # was simply gone from the board); a prose ETA invented by a subagent sat in the ETA column for
            # six consecutive reports; and a `.chk` smoke was carried as "status unknown" for hours. Each
            # was a transcription artifact, not a fleet problem.
            # So the rows come out of the artifact verbatim. **A leg absent from the board is a leg that
            # LANDED or was never there — never one to carry forward from a previous report.**
            cur["legs"].append(line.rstrip())
    return out


def agents_alive(minutes: int = 45, expect: dict[str, list[str]] | None = None) -> dict:
    """Whether each named SUBAGENT is working, evidenced by ITS OWN work LANDING.

    ⚠ There is no artifact for "an agent is running", so a commit is the only honest signal, and this is
    deliberately conservative: an agent that has not pushed inside the window reads as SILENT. That error
    direction is correct — it prompts a check, whereas assuming alive is what let three dead threads be
    reported as "moving" on 2026-08-01, one of them for 17.5 hours.

    ★★ PER-AGENT, NOT AGGREGATE — the fix for this function's OWN first version (2026-08-01, same day).
    It answered one global question, "is any work landing", and the answer was yes while an agent sat dead.
    An aggregate cannot distinguish four healthy agents from one healthy agent and three corpses, so a
    report built on it said "launched" for rows that had produced nothing — the exact inertia this module
    exists to end, reappearing one level up in the module written to end it.

    `expect` maps a row label to substrings that identify that agent's commits. A label with no matching
    commit in the window is SILENT and is named. **A label nobody can match is itself the finding**: if a
    row cannot be tied to evidence, it may not be reported as working.
    """
    log = _git("log", "origin/main", f"--since={minutes} minutes ago", "--format=%ad|%s",
               "--date=format:%H:%M")
    real = [ln for ln in log.splitlines() if ln and not any(n in ln for n in CI_NOISE)]
    out = {"window_min": minutes, "n_agent_commits": len(real), "commits": real[:12],
           "verdict": "work landing" if real else "NO AGENT WORK LANDED — verify or re-launch"}
    if expect:
        per, silent = {}, []
        for label, keys in expect.items():
            hits = [c for c in real if any(k.lower() in c.lower() for k in keys)]
            per[label] = {"n": len(hits), "latest": hits[0] if hits else None,
                          "state": "WORKING" if hits else "SILENT — verify or re-launch"}
            if not hits:
                silent.append(label)
        out["per_agent"] = per
        out["silent"] = silent
        # Unattributed work is not noise: it means a row is missing, or a label is wrong. Either way the
        # report is incomplete, and saying so beats a table that looks accounted for.
        claimed = {c for label in expect for k in expect[label] for c in real if k.lower() in c.lower()}
        out["unattributed_commits"] = [c for c in real if c not in claimed][:6]
    return out


def report(prior_unknowns: set[str] | None = None) -> dict:
    """The whole readout. `prior_unknowns` are row keys that reported UNKNOWN in the LAST report.

    Anything in both this report's unknowns and the prior set is ESCALATE: an unknown that survives a
    report cycle is an unanswered question, not a state.
    """
    bill, lanes, agents = billing_now(), lane_rows(), agents_alive()
    unknown = {l["lane"] for l in lanes if l.get("stale") or l.get("unreadable")}
    if bill.get("unreadable") or bill.get("stale"):
        unknown.add("vast-account-census")
    return {"generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "billing": bill, "lanes": lanes, "agents": agents,
            "unknown_rows": sorted(unknown),
            "escalate": sorted(unknown & (prior_unknowns or set()))}


def main() -> None:
    import argparse
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--prior-unknowns", default="",
                    help="comma-separated row keys that were UNKNOWN in the previous report")
    a = ap.parse_args()
    r = report({s for s in a.prior_unknowns.split(",") if s})
    print(json.dumps(r, indent=1))
    if r["escalate"]:
        print(f"\n⛔ ESCALATE — unknown for a SECOND consecutive report, resolve now: "
              f"{', '.join(r['escalate'])}")
    if r["agents"]["verdict"].startswith("NO AGENT"):
        print(f"\n⚠ {r['agents']['verdict']} in the last {r['agents']['window_min']} min — a queued "
              f"SendMessage is not evidence of work.")


if __name__ == "__main__":
    main()
