#!/usr/bin/env python3
"""The half of the queue nothing prints — arbitration, not status.

⛔⛔ THE FINDING (2026-08-27 `/deep-research` pass, verified against AlabOS's source). Its task STATUS
is dashboard-visible; its pending RESOURCE-REQUEST queue lives in the `requests` collection and is
surfaced by NO route. So a reader can see what each task is DOING and cannot see what is WAITING ON
WHAT. ⭐ We have the identical split: `continuity.py` prints ready rows and the capacity line,
`stalled_holder.py` prints held rows — and nothing prints why a ready row is not moving, or what a
row is waiting behind. **That gap is where the 2026-08-27 dead seat hid for 2 h 36 m**: its claim was
open, `ListAgents` said "running", and no view joined those two facts.

★★ AND IT ANSWERS AUT-PD-051, WHICH IS THE SAME BLIND SPOT ONE STEP LATER. A lease records who HOLDS
a row; nothing records who FINISHED one. So a seat's branch can be merged to main while its ledger
row stays open, the stale-lease sweep releases it, and a second session claims it and rebuilds what
already shipped. Measured that day: `stuck_clock.py` (AUT-PROP-029) was on origin/main when
CYC-0044-schedule claimed the row and dispatched an agent to build it.

⛔⛔ AND THE FIRST VERSION OF THIS FIX ONLY ANSWERED HALF OF AUT-PD-051 (fixed 2026-08-28, CYC-0047).
`already_landed()` originally read `continuity.ready()` only — but AUT-PD-051's own SECOND instance
that same day (AUT-PROP-032's residue gate, merged locally and never pushed, row stayed open,
CYC-0046-schedule claimed and dispatched anyway) was a HELD row, not a ready one: `stuck_clock.py`
had already been released by the stale-lease sweep by the time it was rebuilt, but AUT-PROP-032 was
still actively `in_progress`, owned, and would never have been caught by the ready-only check. The
sharper diagnosis in AUT-PD-051's own text says so: "should be pointed at rows owned by a COMPLETED
seat, not only at ready rows." `main()` now also runs `already_landed()` against every currently-held
row, using the same filed-then-added-after discriminator, and reports it in its own section.

⛔⛔ IT REPORTS AND NEVER CLOSES ANYTHING, AND THAT LIMIT IS DELIBERATE. An artifact existing on the
trunk is NOT the same as the item being finished — a row whose deliverable partly landed must stay
open, and auto-closing on this signal would silently drop the unfinished half. The whole value is
making a human or the merging session look. ⚠ Same reason `stalled_holder.py` only ever reports:
"the driver cannot be the thing that notices the driver has stalled." This applies exactly as much
to a held row as a ready one: a seat mid-way through extending what already landed is not finished
just because its named path exists.

USAGE
    python3 research/autonomy/queue_view.py            # the arbitration view
    python3 research/autonomy/queue_view.py --check    # exit 1 if a ready OR held row's deliverable is already on the trunk
"""

from __future__ import annotations

import argparse
import datetime
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)

import continuity  # noqa: E402

#: A repo-relative path mentioned in a row's prose. Deliberately narrow: a token that looks like a
#: tracked source path, not any word with a dot in it.
PATH_RE = re.compile(r"\b((?:research|systems|scripts|\.claude)/[A-Za-z0-9_./-]+\.(?:py|json|md|sh))\b")

#: ⛔⛔ `depends_on_evidence` IS DELIBERATELY NOT HERE, AND THE FIRST VERSION INCLUDED IT AND WAS
#: USELESS. That field names what a row READS — so those paths exist BY DEFINITION, and scanning it
#: flagged 33 ready rows on the first run, nearly all of them citing this survey or a linter they
#: merely reference. A guard that flags 33 true statements is one that gets turned off within a week
#: (`lint_claims.py`'s founding lesson). A row's DELIVERABLE is what it would WRITE.
DELIVERABLE_FIELDS = ("what", "lease_released")


def named_paths(row: dict) -> list[str]:
    out: list[str] = []
    for f in DELIVERABLE_FIELDS:
        v = row.get(f)
        if isinstance(v, str):
            out.extend(PATH_RE.findall(v))
    seen, uniq = set(), []
    for p in out:
        if p not in seen:
            seen.add(p); uniq.append(p)
    return uniq


def on_trunk(path: str, ref: str = "origin/main", repo: str = REPO) -> bool:
    """Whether `ref` carries this path. ⚠ False on any git error — an unreadable trunk must never
    manufacture a 'already done' claim, which is the direction that would suppress real work."""
    try:
        return subprocess.run(["git", "-C", repo, "cat-file", "-e", f"{ref}:{path}"],
                              capture_output=True).returncode == 0
    except OSError:
        return False


def added_after(path: str, when: datetime.date, ref: str = "origin/main", repo: str = REPO) -> bool:
    """Whether `path` was ADDED to `ref` after `when`.

    ⛔⛔ THIS IS THE DISCRIMINATOR, AND WITHOUT IT THE VIEW IS NOISE. A path a row merely cites has
    existed since long before the row was filed; a path a row DELIVERED appeared after it. Measured
    2026-08-28: existence alone flagged 33 ready rows, nearly every one citing a survey or a linter
    it references. Creation-after-filing is what separates "this row's work landed" from "this row
    mentions a file".

    ⚠ False on any git error, and false when the creation date is unreadable — an unreadable history
    must never suppress ready work.
    """
    try:
        out = subprocess.run(
            ["git", "-C", repo, "log", ref, "--diff-filter=A", "--format=%ct", "-1", "--", path],
            capture_output=True, text=True)
    except OSError:
        return False
    stamp = out.stdout.strip().splitlines()
    if out.returncode != 0 or not stamp:
        return False
    try:
        added = datetime.datetime.fromtimestamp(int(stamp[0]), datetime.timezone.utc).date()
    except (ValueError, OverflowError):
        return False
    return added > when


def already_landed(rows: list[dict] | None = None, ref: str = "origin/main") -> list[tuple[str, list[str]]]:
    """`[(row id, [paths already on the trunk])]` for READY rows whose named deliverable exists.

    ⛔ READY rows only. A held row is somebody's live work and a closed row is finished; this asks
    only about rows the loop is about to OFFER to a session that would then rebuild them.
    """
    rows = rows if rows is not None else continuity.ready()
    out = []
    for r in rows:
        raw = r.get("last_evidence_utc")
        if not isinstance(raw, str) or not raw.strip():
            continue  # no filing date, no comparison, no claim
        try:
            filed = datetime.date.fromisoformat(raw.strip()[:10])
        except ValueError:
            continue
        landed = [p for p in named_paths(r)
                  if on_trunk(p, ref) and added_after(p, filed, ref)]
        if landed:
            out.append((r.get("id") or "?", landed))
    return out


def held_full_rows(rows: list[dict] | None = None) -> list[dict]:
    """Full ledger rows for every currently-held claim — `held()`'s summary carries no `what` or
    `lease_released`, and `already_landed()` needs those to find a named deliverable."""
    pool = rows if rows is not None else continuity._entries()
    by_id = {e.get("id"): e for e in pool if isinstance(e, dict)}
    return [by_id[eid] for eid, _owner in continuity.live_leases() if eid in by_id]


def held(rows: list[dict] | None = None) -> list[dict]:
    """Open rows a worker holds, with the age of the claim — the arbitration side of the queue."""
    out = []
    now = datetime.datetime.now(datetime.timezone.utc)
    for eid, owner in continuity.live_leases():
        row = next((e for e in (rows if rows is not None else continuity._entries())
                    if e.get("id") == eid), {})
        age_h = None
        raw = row.get("claimed_utc")
        if isinstance(raw, str) and raw.strip():
            try:
                t = datetime.datetime.fromisoformat(raw.replace("Z", "+00:00"))
                age_h = round((now - t).total_seconds() / 3600.0, 1)
            except ValueError:
                age_h = None
        out.append({"id": eid, "owner": owner, "claim_age_hours": age_h,
                    "workers": row.get("claim_workers")})
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true",
                    help="exit 1 if a ready row's named deliverable is already on the trunk")
    ap.add_argument("--ref", default="origin/main")
    args = ap.parse_args(argv)

    h = held()
    landed = already_landed(ref=args.ref)
    landed_held = already_landed(rows=held_full_rows(), ref=args.ref)

    print(f"HELD — {len(h)} row(s) a worker is holding right now:")
    for row in sorted(h, key=lambda r: -(r["claim_age_hours"] or 0)):
        age = f"{row['claim_age_hours']}h" if row["claim_age_hours"] is not None else "age unreadable"
        w = f", {row['workers']} agent(s)" if row.get("workers") else ""
        print(f"   {row['id']:<16} {row['owner']}  ({age}{w})")
    if not h:
        print("   (none)")

    print(f"\n⛔ ALREADY ON {args.ref} — {len(landed)} ready row(s) whose named deliverable exists:")
    for eid, paths in landed:
        print(f"   {eid:<16} {', '.join(paths)}")
    if not landed:
        print("   (none)")
    else:
        print("\n   ★ THIS IS A REPORT, NOT A CLOSURE. An artifact on the trunk is not the same as the")
        print("     item being finished — a row whose deliverable PARTLY landed must stay open. Read")
        print("     each one and close it deliberately, or say why it is still open (AUT-PD-051).")

    print(f"\n⛔⛔ HELD, BUT ALREADY ON {args.ref} — {len(landed_held)} owned row(s) whose named "
          f"deliverable exists:")
    for eid, paths in landed_held:
        owner = next((o for i, o in continuity.live_leases() if i == eid), "?")
        print(f"   {eid:<16} owner={owner}  {', '.join(paths)}")
    if not landed_held:
        print("   (none)")
    else:
        print("\n   ★ A ROW SOMEBODY HOLDS IS NOT AUTOMATICALLY UNFINISHED WORK — it may be a fresh")
        print("     dispatch rebuilding what a DIFFERENT session already merged (AUT-PD-051's exact")
        print("     shape, twice in one day). Check with the holder before releasing or re-dispatching.")
    return 1 if args.check and (landed or landed_held) else 0


if __name__ == "__main__":
    raise SystemExit(main())
