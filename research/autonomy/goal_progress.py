#!/usr/bin/env python3
"""How far is each open goal from done, computed rather than reported.

⛔⛔ WHY THIS EXISTS. `research/autonomy/goals.json` explains the gap; this is the instrument. The
one real goal in play — "get ASO v2 submission ready" — lived as prose inside a budget field, so a
full session of warranted work could move `publish_bar` from 4/7 to 4/7 and nothing in the system
was able to say the distance had not closed.

★ IT RECOMPUTES, ALWAYS. The `readings` list in goals.json is a HISTORY for spotting a goal that is
not moving; it is never the answer. A checker that reads a stored verdict is the "populated field is
not a measured one" failure (CLAUDE.md §4), which this repository has paid for in `deposit-state`,
in the archive manifest and in `subagent_width`.

⛔ AND IT FAILS CLOSED, IN THE DIRECTION THAT COSTS SOMETHING. An unreadable goal, an unknown
done-condition kind, or a tool that will not run is reported UNKNOWN and exits non-zero. A goal
tracker that shrugs and prints green is worse than no tracker: it converts "nobody looked" into
"nothing is wrong".

Exit codes: 0 every open goal is MET · 1 at least one is not met · 2 at least one is UNKNOWN.
⭐ 1 IS NOT A FAILURE. A goal in progress is the normal state and the ordinary reading; it is
distinct from 2 because "three clauses open" and "I could not tell" are different facts and a
caller that conflates them is the defect this file is about.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
GOALS = os.path.join(HERE, "goals.json")

MET, OPEN, UNKNOWN = "MET", "OPEN", "UNKNOWN"


def _head() -> str | None:
    try:
        out = subprocess.run(["git", "-C", REPO, "rev-parse", "HEAD"],
                             capture_output=True, text=True, timeout=30)
        return out.stdout.strip() or None
    except Exception:
        return None


def _publish_bar(paper: str, sha: str):
    """Run the bar and return its parsed JSON, or (None, why)."""
    cmd = [sys.executable, os.path.join(HERE, "publish_bar.py"),
           "--paper", paper, "--sha", sha, "--json"]
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    except Exception as exc:
        return None, f"publish_bar could not be run ({type(exc).__name__})"
    text = (out.stdout or "").strip()
    if not text:
        return None, f"publish_bar wrote nothing (exit {out.returncode}); stderr: " \
                     f"{(out.stderr or '').strip()[:200]}"
    try:
        return json.loads(text), None
    except Exception:
        return None, f"publish_bar output is not JSON: {text[:200]}"


def measure(goal: dict) -> dict:
    """One goal's distance to done. Never reads `readings`."""
    cond = goal.get("done_condition") or {}
    kind = cond.get("kind")
    if kind != "publish_bar":
        # ⛔ An unknown kind is UNKNOWN, not MET. A tracker that treats "I do not understand this
        # goal" as "this goal is fine" is the exact inversion this file refuses.
        return {"status": UNKNOWN, "detail": f"done_condition.kind is {kind!r}, which this "
                                             "checker does not know how to compute"}
    sha = _head()
    if not sha:
        return {"status": UNKNOWN, "detail": "HEAD is unreadable, so there is no commit to measure "
                                             "the bar against"}
    data, why = _publish_bar(cond.get("paper", ""), sha)
    if data is None:
        return {"status": UNKNOWN, "detail": why}

    # ⭐ THE COUNT COMES FROM THE TOOL. Typing "7" here would be a second home for a number the bar
    # already owns, and a sibling record has already watched a hard-coded "six" go stale when a
    # seventh clause landed.
    passed, total = data.get("n_passed"), data.get("n_clauses")
    if not isinstance(passed, int) or not isinstance(total, int) or total <= 0:
        return {"status": UNKNOWN,
                "detail": f"publish_bar reported n_passed={passed!r} of n_clauses={total!r}"}
    openc = [c.get("clause") for c in (data.get("clauses") or []) if not c.get("ok")]
    return {
        "status": MET if passed == total else OPEN,
        "passed": passed, "of": total, "open": openc, "sha": sha,
        "detail": f"{passed}/{total} clauses on {sha[:12]}"
                  + (f" — open: {', '.join(str(c) for c in openc)}" if openc else ""),
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true", help="print each open goal's distance")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    try:
        doc = json.load(open(GOALS, encoding="utf-8"))
    except Exception as exc:
        print(f"[goal] goals.json is unreadable ({type(exc).__name__}) — that is UNKNOWN, not OK")
        return 2
    goals = [g for g in (doc.get("goals") or []) if g.get("state") == "open"]
    if not goals:
        print("[goal] no open goals recorded")
        return 0

    results, worst = [], 0
    for g in goals:
        m = measure(g)
        m["id"] = g.get("id")
        m["title"] = g.get("title")
        results.append(m)
        worst = max(worst, {MET: 0, OPEN: 1, UNKNOWN: 2}[m["status"]])

    if args.json:
        print(json.dumps({"goals": results}, indent=2))
        return worst

    for m in results:
        mark = {MET: "OK  ", OPEN: "OPEN", UNKNOWN: "????"}[m["status"]]
        print(f"[goal] {mark} {m['id']} — {m['title']}")
        print(f"[goal]      {m['detail']}")
        if m["status"] == OPEN:
            # ⭐ SAY WHAT WOULD MOVE IT. A distance with no next action is a status, and this
            # repository's own rule is that a status nobody can act on is an unanswered question
            # wearing a costume.
            print("[goal]      these clauses bind to the commit being posted, so any manuscript "
                  "edit after the round that closes them re-opens all three")
    return worst


if __name__ == "__main__":
    raise SystemExit(main())
