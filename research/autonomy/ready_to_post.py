#!/usr/bin/env python3
"""WHICH PAPERS ARE WAITING ON trimcrae TO POST THEM — as a committed queue, not a thread message.

⛔⛔ WHY THIS EXISTS. trimcrae, 2026-08-27: "If you have a paper ready for me to post, you need a
better way of contacting me with it than putting it in a thread of an unmonitored session." Measured
that day: the ASO v2 was finished, gated and postable, and the only notice of it was prose in a
session he was not reading. CLAUDE.md §3 already required a PushNotification in the same turn and it
was not sent — so the rule existed and depended on an agent remembering it, which is the same as not
existing.

★ THE FIX IS TO MAKE "READY TO POST" A STATE OF THE REPOSITORY RATHER THAN A SENTENCE IN A REPLY.
This module derives that state from the bar every cycle already runs. A paper reaches the queue when
the clauses pass and the remaining act is one only he can perform; it leaves the queue when he
performs it. Nothing here posts anything, and nothing here decides that a paper is good — it reports
what `publish_bar.py` decided.

⚠ AND THE QUEUE IS NOT THE NOTIFICATION. A file nobody opens is exactly the failure it is fixing, one
layer down. The obligation is in `research-loop` §5: a cycle that finds a NEW paper in this queue
sends a PushNotification in the same turn. This file makes that condition checkable; the contract
makes it mandatory.

Usage:
  python3 research/autonomy/ready_to_post.py            # print the queue
  python3 research/autonomy/ready_to_post.py --write    # refresh the committed queue
  python3 research/autonomy/ready_to_post.py --new      # only papers not yet notified; exit 1 if any
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
QUEUE = os.path.join(HERE, "ready-to-post.json")
PUBLICATIONS = os.path.join(REPO, "systems", "graph", "publications.json")

#: Acts only trimcrae performs. ⛔ A paper whose next act is on this list is NEVER auto-shipped, and
#: the loop's job ends at "prepared". CLAUDE.md §3: prepare everything, post nothing.
HIS_ACTS = {
    "qeios_post": "post it to Qeios (his venue, his ORCID, his version history)",
    "qeios_new_version": "post the new version to Qeios",
    "journal_submission": "submit it to a journal — always his call (D4)",
    "zenodo_deposit": "publish the Zenodo deposit / mint the DOI",
}


def _head() -> str:
    r = subprocess.run(("git", "rev-parse", "HEAD"), cwd=REPO, capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else ""


def _publications() -> list[dict]:
    with open(PUBLICATIONS, encoding="utf-8") as fh:
        d = json.load(fh)
    return d if isinstance(d, list) else d.get("publications", [])


def _load_queue() -> dict:
    if not os.path.exists(QUEUE):
        return {"waiting": {}, "notified": {}}
    with open(QUEUE, encoding="utf-8") as fh:
        d = json.load(fh)
    return {"waiting": d.get("waiting", {}), "notified": d.get("notified", {})}


def evaluate(sha: str | None = None) -> dict:
    """Every publication whose next act belongs to trimcrae, with the bar's verdict beside it."""
    sys.path.insert(0, HERE)
    import publish_bar  # noqa: E402

    sha = sha or _head()
    waiting: dict[str, dict] = {}
    for pub in _publications():
        pid = pub.get("id")
        nxt = (pub.get("next_act") or "").strip()
        if not pid or nxt not in HIS_ACTS:
            continue
        try:
            verdict = publish_bar.evaluate(pid, sha, venue=pub.get("next_venue", "aixiv"),
                                           act="new_version")
        except Exception as exc:  # a bar that cannot run is UNKNOWN, never "ready"
            waiting[pid] = {"state": "UNVERIFIABLE", "why": f"{type(exc).__name__}: {exc}"}
            continue
        blocking = [c["clause"] for c in verdict["clauses"] if not c["ok"]]
        waiting[pid] = {
            "act": nxt,
            "what_he_does": HIS_ACTS[nxt],
            "document": (pub.get("document") or {}).get("file"),
            "commit": sha,
            "deliverable_digest": publish_bar._deliverable_digest_at(pid, sha),
            "clauses_passed": verdict["n_passed"],
            "clauses_total": verdict["n_clauses"],
            "blocking_clauses": blocking,
            # ⛔ READY MEANS EVERY CLAUSE PASSED. A paper with one clause open is IN PROGRESS, and
            # calling it ready would train him to ignore this queue — which is the whole failure.
            "state": "READY" if not blocking else "NOT-READY",
        }
    return waiting


def _already_notified(paper: str, ready: dict, queue: dict) -> bool:
    """Notification identity is the outgoing bytes and requested act, not repository HEAD."""
    import publish_bar
    previous = queue["notified"].get(paper, {})
    old_act = previous.get("act") or queue.get("waiting", {}).get(paper, {}).get("act")
    if old_act != ready.get("act"):
        return False
    old_digest = previous.get("deliverable_digest")
    if not old_digest and previous.get("commit"):
        old_digest = publish_bar._deliverable_digest_at(paper, previous["commit"])
    new_digest = ready.get("deliverable_digest")
    if old_digest and new_digest:
        return old_digest == new_digest
    # Missing digests cannot prove equivalence across revisions.
    return bool(previous.get("commit") and previous["commit"] == ready.get("commit"))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--write", action="store_true", help="refresh the committed queue")
    ap.add_argument("--new", action="store_true",
                    help="print only READY papers not yet notified; exit 1 if any exist")
    ap.add_argument("--mark-notified", metavar="PUB", help="record that he has been told about PUB")
    args = ap.parse_args(argv)

    q = _load_queue()

    if args.mark_notified:
        q["waiting"] = evaluate()
        ready = q["waiting"].get(args.mark_notified, {})
        if ready.get("state") != "READY":
            print(f"cannot mark {args.mark_notified}: no verified READY artifact")
            return 1
        q["notified"][args.mark_notified] = {
            key: ready.get(key) for key in ("commit", "deliverable_digest", "act")}
        _write(q)
        print(f"recorded that trimcrae was notified about {args.mark_notified}")
        return 0

    waiting = evaluate()
    ready = {k: v for k, v in waiting.items() if v.get("state") == "READY"}

    if args.new:
        fresh = {k: v for k, v in ready.items()
                 if not _already_notified(k, v, q)}
        for pid, v in fresh.items():
            print(f"READY (not yet notified): {pid} — {v['what_he_does']}  [{v['document']}]")
        if not fresh:
            print("nothing new to tell trimcrae about")
        return 1 if fresh else 0

    if args.write:
        q["waiting"] = waiting
        _write(q)
        print(f"wrote {QUEUE}: {len(ready)} READY, {len(waiting) - len(ready)} not ready")
        return 0

    if not waiting:
        print("no publication endpoint declares an act that belongs to trimcrae")
        return 0
    for pid, v in sorted(waiting.items()):
        mark = "✅ READY" if v.get("state") == "READY" else f"   {v.get('state')}"
        print(f"{mark}  {pid}  {v.get('what_he_does', v.get('why',''))}")
        if v.get("blocking_clauses"):
            print(f"           blocked on: {', '.join(v['blocking_clauses'])}")
    return 0


def _write(q: dict) -> None:
    q["_what"] = ("Papers whose next act belongs to trimcrae, and whether the bar clears them. "
                  "Derived — never hand-edited. Regenerate with ready_to_post.py --write.")
    q["_why"] = ("trimcrae, 2026-08-27: a finished, postable paper was announced only in a thread of "
                 "a session he was not reading. A queue in the repository is checkable by every "
                 "cycle; the PushNotification obligation that goes with it is in research-loop §5.")
    q["_not_a_notification"] = ("⛔ This FILE is not how he finds out. A file nobody opens is the same "
                                "failure one layer down. It exists so a cycle can DETECT the condition "
                                "and then push.")
    with open(QUEUE, "w", encoding="utf-8") as fh:
        json.dump(q, fh, indent=2, ensure_ascii=False)
        fh.write("\n")


if __name__ == "__main__":
    sys.exit(main())
