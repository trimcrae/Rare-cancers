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


# ══════════════════════════════════════════════════════════════════════════════════════════════════════════
# THE BOARD, IN THE FORM IT IS ACTUALLY READ IN
#
# ★★ THE TOOL EMITS THE PRESENTATION FORMAT, BECAUSE THE HAND STEP IS WHERE THE ERRORS WERE (trimcrae,
# 2026-08-01: *"That board formatting is bad."*). Everything above this line returns STRUCTURE, and every
# consumer of it had to turn that structure into the markdown table trimcrae actually reads. That last hand
# step is not a formatting nicety — it is the same transcription gap that put a landed leg on the board as
# RUNNING at 98.9% with an ETA eleven minutes in the past, and a subagent's invented ETA in the ETA column
# for six consecutive reports. A row is only as trustworthy as the last hand that touched it, so the last
# hand is removed: `board_table()` returns the finished markdown.
#
# ⚠ IT READS THE FRAGMENTS, NOT `inflight-board-all.md`. The merged board is a CACHE, regenerated only by
# whichever lane happens to call `inflight_board --write`, so a lane can be perfectly healthy and still
# render STALE there because nobody re-merged. Measured 2026-08-01, 2:44 PM ET: the GCP lane's fragment was
# 1.8 min old and carried an ETA of 4:36 AM Aug 2 while the merged board showed that lane at "16 min ago,
# STALE (> 15 min)" with a blank ETA. Both were fixed at the source (`gcp_fanout_rep` now calls `ib.publish`,
# and the ternary and GCP workflows re-merge after their reset) — but a report must not be able to inherit
# that class of lag at all, so this reads each lane's own fragment and applies the staleness rule itself.
# The rule is still `inflight_board`'s: `stale_after_min()` and `stale_rows()` are imported, never restated.
# ══════════════════════════════════════════════════════════════════════════════════════════════════════════

#: How much of a `WHY` survives into a table cell. Long enough for the operative clause — every lane writes
#: the reason first and the justification after — and short enough that the row stays one line on a phone.
WHY_CLIP = 150


def _ifb():
    """`inflight_board`, imported lazily so this module stays usable where the lane code is absent."""
    import sys
    if str(REPO / "research" / "modalities") not in sys.path:
        sys.path.insert(0, str(REPO / "research" / "modalities"))
    import inflight_board  # noqa: PLC0415
    return inflight_board


#: ★★ COST IS PART OF THE FORMAT, NOT AN EXTRA (CLAUDE.md §1) — AND ITS ABSENCE IS WHY THE ETA KEPT
#: DISAPPEARING (trimcrae, 2026-08-01: *"We somehow lost the ETA from the supposedly procedurally generated
#: table."*). The generated table carried ETA, % done and `$/ns` but NOT cost, which §1 requires on every
#: in-flight row. So each time I reported I hand-built a table to add the cost column — and the hand-built
#: one dropped the ETA. The transcription this module exists to end came back through the one column it
#: did not emit. A generated artifact that is missing a required field will be rebuilt by hand, every time.
#:
#: ⚠ THE CELL IS A POINTER, NEVER A TYPED FIGURE. §1: a cost has one home and everywhere else links to it.
#: The ladder JSON owns priced rungs and pricing.md owns the evidence; quoting a dollar amount here would
#: be a second home free to drift, which is the defect the whole rule exists for.
_LANE_COST = {
    "gcp-s1f-rep": "$0 — free GCP trial credit (SEPARATE LEDGER, expires 2026-10-10)",
}


def _cost_cell(lane, row):
    """What this row costs — as a POINTER to the figure's one home, or the lane's own declaration."""
    if row and row.get("cost"):
        return str(row["cost"])                       # a lane that knows its own cost wins
    if lane in _LANE_COST:
        return _LANE_COST[lane]
    return "ladder — see vast-ladder-repricing.json"


def _cell(s: str, clip: int | None = None) -> str:
    """One markdown table cell. `|` is escaped and a clipped cell SAYS it was clipped.

    ⚠ ONLY `WHY` IS EVER CLIPPED. The `$/ns` cell carries the distinction between `⚠ PAYING OVER THE …×
    LINE` and `⛔ REFUSED at … — $0 spent`, which CLAUDE.md §1 requires never to render alike, and the STATE
    cell carries the verdict; truncating either could make a refusal read as a purchase. A clipped cell ends
    in `…` so a reader can never mistake a partial reason for a complete one.
    """
    s = " ".join(str(s if s is not None else "—").split()).replace("|", "\\|")
    if clip and len(s) > clip:
        cut = s[:clip].rsplit(" ", 1)[0]
        s = (cut or s[:clip]) + "…"
    return s or "—"


def _parse_rendered_block(block: str) -> list[dict] | None:
    """Cells recovered from a block `inflight_board.render()` produced, or None if it cannot be read.

    ⚠ A BRIDGE, NOT A SECOND HOME. The ternary lane published its board as fixed-width TEXT ONLY until
    2026-08-01; it now writes `inflight-board.d/ternary.json` from the same rows in the same call, and this
    parse exists only for the window before that fragment reaches `main`, and for any future lane that
    renders before it publishes. **The column offsets are DERIVED from the header line, never typed** —
    `render()` sizes its LEG and `$/ns` columns from the rows themselves, so any constant here would be
    wrong the first time a unit id got longer. Returns None rather than guessing if the header is not there,
    because a lane that cannot be parsed must say so and never render as empty.
    """
    lines = [ln for ln in (block or "").splitlines() if ln.strip()]
    head = next((ln for ln in lines if ln.startswith("LEG") and "ETA (ET)" in ln), None)
    if head is None:
        return None
    try:
        starts = [0] + [head.index(lbl) for lbl in ("ETA (ET)", "% DONE", "$/ns", "STATE", "WHY")]
    except ValueError:
        return None
    if starts != sorted(starts):
        return None
    edges = starts + [10**6]
    out = []
    for ln in lines[lines.index(head) + 1:]:
        if set(ln.strip()) <= {"-"} or ln.startswith("IN-FLIGHT BOARD:"):
            continue
        c = [ln[edges[i]:edges[i + 1]].strip() for i in range(6)]
        out.append({"name": c[0], "_eta_text": c[1], "_pct_text": c[2],
                    "usd_per_ns": c[3], "state": c[4], "why": c[5]})
    return out


def _lane_cells(now: float) -> list[dict]:
    """Every lane's rows as CELLS, with each lane's staleness already applied. One dict per row.

    Iterates `inflight_board.LANES`, never the fragments that happen to exist, so a lane that has published
    nothing renders a row saying so — an absent lane and an idle lane are opposite facts (`_absent_lane_
    section` exists for the same reason) and this table must not be the place they finally render alike.
    """
    ifb = _ifb()
    limit = ifb.stale_after_min()
    out: list[dict] = []
    for lane, _heading, writer in ifb.LANES:
        doc = _read(f"research/modalities/{ifb.FRAGMENT_DIR}/{lane}.json")
        rows, age, source = None, None, f"{ifb.FRAGMENT_DIR}/{lane}.json"
        if isinstance(doc, dict) and doc.get("rows") is not None:
            rows = doc.get("rows") or []
            age = max(0.0, (now - float(doc.get("generated_epoch") or 0.0)) / 60.0)
        elif lane == ifb.TERNARY:
            # The pre-fragment bridge described in `_parse_rendered_block`.
            md = _read(f"research/modalities/{ifb.TERNARY_BOARD_MD}")
            if isinstance(md, str):
                m = ifb._TERNARY_BLOCK_RE.search(md)
                stamp = ifb._TERNARY_STAMP_RE.search(md)
                rows = _parse_rendered_block(m.group(1)) if m else None
                source = f"{ifb.TERNARY_BOARD_MD} (text, pre-fragment)"
                if stamp:
                    try:
                        import calendar
                        t = time.strptime(f"{stamp.group(1)} {stamp.group(2)}", "%I:%M %p %b %d, %Y")
                        age = max(0.0, (now - (calendar.timegm(t) - ifb.ET_OFFSET_H * 3600.0)) / 60.0)
                    except ValueError:
                        age = None
        if rows is None:
            out.append({"lane": lane, "name": lane, "eta": "—", "pct": "—", "usd": "—",
                        "cost": _cost_cell(lane, None),
                        "state": ifb.UNKNOWN, "stale": True,
                        "why": f"no readable fragment on origin/main ({source}); published by `{writer}`"})
            continue
        stale = age is not None and age > limit
        if stale:
            rows = ifb.stale_rows(rows, age)
        if not rows:
            out.append({"lane": lane, "name": "—", "eta": "—", "pct": "—", "usd": "—",
                        "cost": _cost_cell(lane, None),
                        "state": "no GPU legs", "stale": False,
                        "why": f"lane is idle, not absent — fragment is {age:.0f} min old"
                               if age is not None else "lane is idle, not absent"})
            continue
        for r in rows:
            pct = r.get("_pct_text")
            if pct is None:
                # ⚠ NO `[:7]`. That truncation is `inflight_board.render`'s FIXED-WIDTH convention and has
                # no business in a markdown cell, which has no width to protect — it rendered the selcal
                # leg's real denominator `0/24 landed` as the meaningless `0/24 la`. Same defect class as
                # the fixed column widths: a constant applied where the layout does not need one.
                pct = (str(r["pct_of"]) if r.get("pct_of") else
                       ("—" if r.get("pct") is None else "%.1f%%" % r["pct"]))
            eta = r.get("_eta_text")
            if eta is None:
                eta = (ifb._fmt_eta(r["eta_s"], now_epoch=now) if r.get("eta_s") is not None
                       else ifb._fmt_eta_at(r.get("eta_epoch"), now_epoch=now))
            out.append({"lane": lane, "name": r.get("name") or "?", "eta": eta, "pct": pct,
                        "cost": _cost_cell(lane, r),
                        "usd": r.get("usd_per_ns") or "—", "state": r.get("state") or "?",
                        "stale": stale, "why": r.get("why") or ""})
    return out


def board_table(now_epoch: float | None = None) -> str:
    """The in-flight board as the markdown table it is read as. Nothing here is remembered or transcribed.

    Every cell traces to a lane's committed fragment on `origin/main` this call; a lane that cannot be read
    gets a row saying so. CLAUDE.md §1 requires a `$/ns` and its multiple of the ladder basis on every GPU
    row — those are the lane's own cells, carried through untouched, because the arithmetic's one home is
    `inflight_usd_per_ns.row()` and a board that re-derived it would be free to disagree with the gate that
    actually refuses a rental.
    """
    now = time.time() if now_epoch is None else now_epoch
    ifb = _ifb()
    cells = _lane_cells(now)
    lines = [f"**In flight** — every cell derived {ifb.et_stamp(now)} from each lane's committed fragment.",
             "",
             "| Lane | Leg | ETA (ET) | % done | Cost | $/ns vs basis | State | Why |",
             "|---|---|---|---:|---|---|---|---|"]
    for c in cells:
        lines.append("| %s | %s | %s | %s | %s | %s | %s | %s |" % (
            _cell(c["lane"]), _cell(c["name"]), _cell(c["eta"]), _cell(c["pct"]),
            _cell(c["cost"]), _cell(c["usd"]), _cell(c["state"]), _cell(c["why"], WHY_CLIP)))
    n_stale = sum(1 for c in cells if c.get("stale"))
    lines += ["", f"_Why cells are clipped at {WHY_CLIP} chars (`…`); the full text is in "
                  f"`research/modalities/inflight-board-all.md`._"]
    if n_stale:
        # ★★ A STALE ROW CANNOT BE GRADED WITHOUT KNOWING WHETHER ANYTHING IS BILLING (2026-08-01).
        # STALE means "nobody has re-measured this lane", and its whole reason for shouting is CLAUDE.md
        # §6: a lane that stops reporting WHILE IT IS BILLING is the condition that costs money. But a lane
        # that has FINISHED also stops reporting — the selcal panel completed 12/12, reaped its host, and
        # then drifted stale forever, printing the billing alarm on a lane that cannot bill.
        #
        # The lane's own last report is exactly the reading we have just declared untrustworthy, so it
        # cannot answer this. The ACCOUNT census can: it is the one source that sees every instance
        # regardless of which lane claims it (that is the orphan failure mode `billing_now` exists for),
        # and it is a committed artifact, so quoting it here stays $0 and needs no credentials.
        bill = billing_now()
        if bill.get("unreadable"):
            hosts = f"⚠ the account census is unreadable ({bill['unreadable']}), so whether anything is " \
                    f"billing is UNKNOWN — an absent reading is not a reading of absence"
        else:
            names = ", ".join(f"`{i['label']}`" for i in bill["instances"] if i.get("label")) or "none"
            age = "" if bill.get("age_min") is None else f", {bill['age_min']:.0f} min old"
            hosts = (f"the account holds **{bill['n']} live instance(s)**{age}: {names}"
                     + (" — **STALE census**, so this cross-check is itself a past reading"
                        if bill.get("stale") else ""))
        lines.append(f"_⚠ {n_stale} row(s) come from a lane that has not reported inside "
                     f"{ifb.stale_after_min():g} min — those are a PAST report, and their ETA is dropped "
                     f"rather than re-projected from a rate nobody has re-measured. To grade that: "
                     f"{hosts}._")
    return "\n".join(lines) + "\n"


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
    ap.add_argument("--table", action="store_true",
                    help="print the in-flight board as the markdown table it is reported as, and nothing "
                         "else — this is the form that goes in a message, so it is generated rather than "
                         "assembled by hand from the JSON below")
    a = ap.parse_args()
    if a.table:
        print(board_table(), end="")
        return
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
