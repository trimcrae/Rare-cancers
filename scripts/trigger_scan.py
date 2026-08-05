#!/usr/bin/env python3
"""trigger_scan.py — search the literature for the NAMED reopening triggers, by name.

WHY THIS EXISTS
---------------
`scripts/method-watch.mjs` already runs a weekly keyword digest over a fixed list of broad
topics. That digest is useful and it is NOT what this is. The repo's parked rows each NAME
the specific capability that would reopen them -- `nr4a3-program-map.md` section 6b is a
table whose third column is literally "what has to land to reopen it" -- and nothing was
searching for those names. So a paper that satisfied a named trigger would have arrived in
the digest indistinguishable from background, and the person reading it would have had to
re-derive the mapping from paper to parked row by hand, every week.

This script closes that gap in one direction only: it turns each named trigger into queries,
runs them, and reports a hit ALONGSIDE THE ROUTES AND REQUIREMENTS THAT TRIGGER WOULD REOPEN.
The consequence travels with the paper. A reviewing session should not have to look anything
up to know why a line matters.

WHAT IT IS NOT
--------------
It is not a grader and it does not change any status. Every hit is an UNVALIDATED LEAD
produced by substring matching on a title. CLAUDE.md section 5's guardrail is the operative
one: a coming capability justifies waiting or re-running, never claiming a result before the
method supports it. Nothing here may be cited.

HONEST LIMITS, STATED BECAUSE THEY DETERMINE HOW TO READ THE OUTPUT
-------------------------------------------------------------------
  * Matching is on the TITLE only. A paper that fires a trigger in its abstract and not its
    title is missed. This is deliberate -- the alternative (abstract matching) floods.
  * Europe PMC indexes preprint servers unevenly and arXiv is queried separately for exactly
    that reason; a method paper posted to a venue neither indexes is missed.
  * A miss is silent. The run log records what was SEARCHED, so an empty result is
    distinguishable from a scan that did not run -- CLAUDE.md section 4: an absent reading is
    not a reading of absence.

SOURCES (both need unrestricted egress -- this cannot run in the dev sandbox; CLAUDE.md
section 6 routes it through GitHub Actions):
  * Europe PMC REST   https://www.ebi.ac.uk/europepmc
  * arXiv Atom API    https://export.arxiv.org

OUTPUTS
  research/method-watch-trigger-hits.json   ledger: every hit ever emitted + run history.
                                            Makes the scan idempotent -- a paper is reported
                                            once, not every week until someone acts.
  research/method-watch-trigger-scan.md     the board: every trigger, its state, its latest
                                            hits, regenerated each run.
  research/IDEAS.md                         appends new hits to the existing auto-capture
                                            section, in that section's own format.

USAGE
  python3 scripts/trigger_scan.py [--seed] [--report-days N] [--max-per-trigger N]
                                  [--only TRG-ID,...] [--dry-run]

  --seed   fill the ledger from the full window and append NOTHING. Use once, when the
           trigger list changes, so a newly-added trigger's back-catalogue does not land in
           IDEAS.md as if it were this week's news.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)

TRIGGERS = os.path.join(_ROOT, "research", "method-watch-triggers.json")
LEDGER = os.path.join(_ROOT, "research", "method-watch-trigger-hits.json")
BOARD = os.path.join(_ROOT, "research", "method-watch-trigger-scan.md")
IDEAS = os.path.join(_ROOT, "research", "IDEAS.md")
#: The systems model's technology register. The scan writes UNGRADED SIGNALS into it and nothing else.
TECHNOLOGIES = os.path.join(_ROOT, "systems", "graph", "technologies.json")

IDEAS_SECTION = "## 🔄 Auto-captured field-scan advances (review + integrate into the board above)"

EPMC = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
ARXIV = "https://export.arxiv.org/api/query"
UA = "rare-cancers-trigger-scan (https://github.com/trimcrae/Rare-cancers)"

# Politeness. Both APIs are public and free; neither is ours to hammer.
SLEEP_S = float(os.environ.get("TRIGGER_SCAN_SLEEP", "1.5"))
TIMEOUT_S = 60


# --------------------------------------------------------------------------- fetch helpers


def _get(url: str, tries: int = 3) -> bytes:
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
            with urllib.request.urlopen(req, timeout=TIMEOUT_S) as r:
                return r.read()
        except (urllib.error.URLError, urllib.error.HTTPError, OSError) as e:  # noqa: PERF203
            last = e
            time.sleep(2 * (i + 1))
    raise RuntimeError(f"GET failed after {tries} tries: {url} :: {last}")


def epmc_search(query: str, page_size: int = 25) -> list[dict]:
    qs = urllib.parse.urlencode(
        {
            "query": query,
            "format": "json",
            "resultType": "lite",
            "pageSize": str(page_size),
            "sort": "P_PDATE_D desc",
        }
    )
    data = json.loads(_get(f"{EPMC}?{qs}").decode("utf-8", "replace"))
    out = []
    for p in data.get("resultList", {}).get("result", []) or []:
        pmcid, pmid, src = p.get("pmcid"), p.get("pmid"), p.get("source") or "MED"
        if pmcid:
            ident, url = pmcid, f"https://europepmc.org/article/PMC/{pmcid}"
        elif pmid:
            ident, url = f"MED/{pmid}", f"https://europepmc.org/article/MED/{pmid}"
        else:
            ident = f"{src}/{p.get('id', '')}"
            url = f"https://europepmc.org/article/{src}/{p.get('id', '')}"
        out.append(
            {
                "id": ident,
                "title": re.sub(r"\s+", " ", (p.get("title") or "")).strip().rstrip("."),
                "date": p.get("firstPublicationDate") or str(p.get("pubYear") or ""),
                "venue": p.get("journalTitle") or src,
                "source": "europepmc",
                "url": url,
            }
        )
    return out


def arxiv_search(query: str, max_results: int = 15) -> list[dict]:
    qs = urllib.parse.urlencode(
        {
            "search_query": query,
            "sortBy": "submittedDate",
            "sortOrder": "descending",
            "max_results": str(max_results),
        }
    )
    raw = _get(f"{ARXIV}?{qs}")
    ns = {"a": "http://www.w3.org/2005/Atom"}
    root = ET.fromstring(raw)
    out = []
    for e in root.findall("a:entry", ns):
        eid = (e.findtext("a:id", "", ns) or "").strip()
        title = re.sub(r"\s+", " ", (e.findtext("a:title", "", ns) or "")).strip()
        pub = (e.findtext("a:published", "", ns) or "")[:10]
        short = eid.rsplit("/", 1)[-1] if eid else title[:40]
        out.append(
            {
                "id": f"arXiv/{short}",
                "title": title,
                "date": pub,
                "venue": "arXiv",
                "source": "arxiv",
                "url": eid or f"https://arxiv.org/abs/{short}",
            }
        )
    return out


# ------------------------------------------------------------------------------- filtering


def _days_old(datestr: str, today: _dt.date) -> int | None:
    """Age in days, tolerant of the three shapes these APIs emit.

    Europe PMC gives `firstPublicationDate` as YYYY-MM-DD, but falls back to a bare
    `pubYear` for some records; arXiv always gives a full timestamp. A year-only record is
    dated to mid-year rather than to 1 January, because 1 January would make every
    year-only record look ~12 months old and silently drop it from every window.
    """
    ds = (datestr or "").strip()
    m = re.match(r"^(\d{4})-(\d{2})-(\d{2})", ds)
    if m:
        try:
            return (today - _dt.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))).days
        except ValueError:
            return None
    m = re.match(r"^(\d{4})-(\d{2})$", ds)
    if m:
        try:
            return (today - _dt.date(int(m.group(1)), int(m.group(2)), 15)).days
        except ValueError:
            return None
    m = re.match(r"^(\d{4})$", ds)
    if m:
        return (today - _dt.date(int(m.group(1)), 7, 1)).days
    return None


def _matches(title: str, must: list[str], also: list[str], exclude: list[str]) -> bool:
    """`must` OR-list AND `also` OR-list, minus `exclude`.

    The second axis exists because the 2026-08-03 first run showed `must` doing no work on
    the broad-field triggers: their queries are already TITLE-anchored on the same terms, so
    every returned record matched and the filter was a no-op (in_window == results_seen).
    `also` is a DIFFERENT axis -- topic AND method, e.g. "oligonucleotide" AND "tumour" --
    which is what actually separates a delivery paper from an oligonucleotide chemistry one.
    Absent, it is skipped; a trigger with no natural second axis should not be given a fake one.
    """
    t = title.lower()
    if any(x.lower() in t for x in exclude):
        return False
    if must and not any(x.lower() in t for x in must):
        return False
    if also and not any(x.lower() in t for x in also):
        return False
    return True


# --------------------------------------------------------------------------------- ledger


def load_ledger() -> dict:
    if os.path.exists(LEDGER):
        with open(LEDGER, encoding="utf-8") as fh:
            return json.load(fh)
    return {
        "_schema": "method-watch-trigger-hits/1",
        "_role": (
            "Ledger for scripts/trigger_scan.py. Two jobs: (1) make the scan IDEMPOTENT, so a "
            "paper is reported once rather than every week until someone acts; (2) record that "
            "the scan RAN, so 'no new hits' is a reading of absence rather than an absent reading."
        ),
        "_integrity": "Machine-matched titles. Unvalidated leads. Nothing here may be cited.",
        "runs": [],
        "hits": {},
    }


# ---------------------------------------------------------------------------------- render


def _reopens_line(trg: dict) -> str:
    r = trg.get("reopens", {}) or {}
    parts = []
    if r.get("roadmap_rows"):
        parts.append("roadmap " + ", ".join(f"`{x}`" for x in r["roadmap_rows"]))
    if r.get("registry_routes"):
        parts.append("routes " + ", ".join(f"`{x}`" for x in r["registry_routes"]))
    if r.get("registry_blockers"):
        parts.append("blockers " + ", ".join(f"`{x}`" for x in r["registry_blockers"]))
    return " · ".join(parts) if parts else "_(no mapping recorded)_"


def ideas_bullet(trg: dict, hit: dict, today: str) -> str:
    return (
        f"- **{today} — trigger `{trg['id']}` matched: {trg['title']}.** "
        f"⚠ **Unvalidated lead — machine-matched on the trigger's own queries, not read and not graded.** "
        f"**Would reopen:** {_reopens_line(trg)}. "
        f"Hit: *{hit['title']}* ({hit['venue']}, {hit['date']}, {hit['id']}) {hit['url']} . "
        f"If it holds: {trg.get('on_fire', 'check the trigger row.')} "
        f"Trigger definition + queries: [`research/method-watch-triggers.json`](./method-watch-triggers.json)."
    )


def append_to_ideas(bullets: list[str]) -> bool:
    if not bullets:
        return False
    with open(IDEAS, encoding="utf-8") as fh:
        text = fh.read()
    if IDEAS_SECTION not in text:
        sys.stderr.write(
            "trigger_scan: IDEAS.md auto-capture section heading not found — refusing to guess "
            "where to append. Heading expected: " + IDEAS_SECTION + "\n"
        )
        return False
    if not text.endswith("\n"):
        text += "\n"
    text += "\n".join(bullets) + "\n"
    with open(IDEAS, "w", encoding="utf-8") as fh:
        fh.write(text)
    return True


def write_board(cfg: dict, ledger: dict, run: dict, per_trigger: dict) -> None:
    L = []
    L.append("# Reopening-trigger scan — the board")
    L.append("")
    L.append(f"**Last run: {run['date']}** (UTC date stamp from the runner).")
    L.append("")
    L.append(
        "Regenerated by [`scripts/trigger_scan.py`](../scripts/trigger_scan.py) from "
        "[`research/method-watch-triggers.json`](method-watch-triggers.json). It searches for the "
        "**specific capabilities the repo has already named** as the condition for reopening a parked "
        "route — the third column of "
        "[`nr4a3-program-map.md` §6b](manuscripts/nr4a3-program-map.md#6b--parked--failed-with-todays-tools-with-a-named-trigger-to-reopen) "
        "— rather than a generic topic list. It is a companion to, not a replacement for, the broad "
        "digest in [`method-watch.md`](method-watch.md)."
    )
    L.append("")
    L.append(
        "⚠ **Everything below is an unvalidated lead.** Hits are substring matches on paper TITLES. "
        "Nothing here has been read, graded or verified, and nothing here may be cited. A hit is a "
        "prompt to read the paper and check the trigger row — never a status change."
    )
    L.append("")
    L.append(
        "⚠ **Scheduling here is not a guarantee.** CLAUDE.md §6 records that this repo's `schedule:` "
        "crons are throttled and have in practice needed manual dispatch. If the run date above is "
        "stale, the scan did not fire — dispatch "
        "[`method-watch-triggers.yml`](../.github/workflows/method-watch-triggers.yml) by hand."
    )
    L.append("")
    L.append("## This run")
    L.append("")
    L.append("| trigger | queries | results seen | in window | NEW | appended to IDEAS.md |")
    L.append("|---|---:|---:|---:|---:|---:|")
    for t in cfg["triggers"]:
        s = per_trigger.get(t["id"])
        if s is None:
            L.append(f"| `{t['id']}` — _not scanned_ | — | — | — | — | — |")
            continue
        L.append(
            f"| `{t['id']}` | {s['queries']} | {s['seen']} | {s['in_window']} | "
            f"**{s['new']}** | {s['appended']} |"
        )
    if run.get("errors"):
        L.append("")
        L.append("**Query failures this run** (a failure is not a null result — the trigger was not scanned):")
        for e in run["errors"]:
            L.append(f"- `{e}`")
    L.append("")

    L.append("## Triggers")
    for t in cfg["triggers"]:
        L.append("")
        L.append(f"### `{t['id']}` — {t['title']}")
        L.append("")
        L.append(f"- **status:** {t['status']} · **kind:** {t['trigger_kind']} · "
                 f"**scanned:** {'yes' if t.get('scan_enabled') else 'no'}")
        if not t.get("scan_enabled") and t.get("not_searchable_because"):
            L.append(f"- **not scanned because:** {t['not_searchable_because']}")
        L.append(f"- **would reopen:** {_reopens_line(t)}")
        if (t.get("reopens") or {}).get("note"):
            L.append(f"- **scope note:** {t['reopens']['note']}")
        for pf in t.get("prior_fires", []) or []:
            L.append(f"- **prior partial fire ({pf['date']}):** {pf['what']}")
        hits = (ledger["hits"].get(t["id"]) or {})
        # The ledger is CUMULATIVE and a trigger's query can be REVISED, so a hit admitted
        # only by a superseded query would otherwise render as a current match forever.
        # Measured case (2026-08-03): TRG-E3-RECRUITER-STRUCTURE's first query admitted
        # TITLE:KEAP1 and TITLE:ligand, and three KEAP1 redox-pharmacology papers (acute lung
        # injury, coenzyme A, heart failure) entered the ledger under a row whose criterion is
        # a partner-free liganded structure for RNF114/DCAF16/DCAF15. Revising the query
        # stopped them being INGESTED; it did nothing about the ones already stored, and the
        # board is what a reader consults. So re-apply the CURRENT criterion at render time.
        # The ledger keeps every hit -- this filters the VIEW, it does not drop history, and
        # the count of withheld entries is printed rather than silently swallowed.
        _s = t.get("search") or {}
        _must = _s.get("must_match") or []
        _also = _s.get("also_match") or []
        _excl = _s.get("exclude_match") or []
        live, stale = [], []
        for h in hits.values():
            (live if _matches(h.get("title", ""), _must, _also, _excl) else stale).append(h)
        recent = sorted(live, key=lambda h: h.get("date", ""), reverse=True)[:5]
        if recent:
            L.append("- **most recent matches** (unvalidated, newest first):")
            for h in recent:
                flag = " 🆕" if h.get("first_seen") == run["date"] else ""
                L.append(f"  - {h.get('date', '?')} — {h.get('title', '')} ({h.get('venue', '')}, "
                         f"{h.get('id', '')}){flag} {h.get('url', '')}")
        else:
            L.append("- **no matches recorded**")
        if stale:
            L.append(
                f"- **{len(stale)} earlier ledger hit(s) withheld** — admitted by a SUPERSEDED "
                f"query and not matched by this trigger's current criterion. Retained in "
                f"[`method-watch-trigger-hits.json`](method-watch-trigger-hits.json), not shown "
                f"here, because a hit the current query would not return is not evidence for "
                f"this row."
            )
    L.append("")

    L.append("## Run history")
    L.append("")
    L.append("| run | triggers scanned | queries | new hits | appended | errors |")
    L.append("|---|---:|---:|---:|---:|---:|")
    for r in ledger["runs"][-20:][::-1]:
        L.append(
            f"| {r['date']} ({r.get('mode', 'scan')}) | {r.get('triggers', 0)} | {r.get('queries', 0)} | "
            f"{r.get('new_hits', 0)} | {r.get('appended', 0)} | {len(r.get('errors', []))} |"
        )
    L.append("")
    with open(BOARD, "w", encoding="utf-8") as fh:
        fh.write("\n".join(L) + "\n")


# ------------------------------------------------------------------- registry cross-check


REGISTRY = os.path.join(_ROOT, "research", "manuscripts", "emc-systems-map.json")



def write_pending_signals(fresh_by_trigger: dict, today: str, dry_run: bool = False) -> int:
    """Record each new hit against every TECH-* whose `scan_trigger` names the trigger that matched.

    ⛔ THIS WRITES ONLY `pending_signals`. It does not touch `current_state`, `evidence` or the
    forecast, and it must never be changed to. This module's whole contract is that a hit is an
    UNVALIDATED LEAD -- machine-matched on a title, not read and not graded -- and a register that
    updated itself from that would break the one rule keeping the watch list honest.

    What it closes is the gap on the other side: before this, a fired trigger told a human that
    something MIGHT have landed, and that human then re-derived by hand which routes, requirements
    and blockers it would reopen. The graph already carries those edges. This puts the hit next to
    them, so grading is a read rather than a re-derivation.

    Idempotent: a paper already recorded against a technology is not added twice.
    """
    if not os.path.exists(TECHNOLOGIES):
        return 0
    with open(TECHNOLOGIES, encoding="utf-8") as fh:
        techs = json.load(fh)

    added = 0
    for tech in techs:
        watched = set(tech.get("scan_trigger") or [])
        if not watched:
            continue
        existing = {(s.get("trg"), s.get("paper_id")) for s in tech.get("pending_signals", [])}
        for trg_id, hits in fresh_by_trigger.items():
            if trg_id not in watched:
                continue
            for h in hits:
                key = (trg_id, h.get("id"))
                if key in existing:
                    continue
                tech.setdefault("pending_signals", []).append({
                    "trg": trg_id,
                    "paper_id": h.get("id", ""),
                    "title": h.get("title", ""),
                    "date": h.get("date", ""),
                    "venue": h.get("venue", ""),
                    "url": h.get("url", ""),
                    "seen_on": today,
                    "graded": False,
                })
                existing.add(key)
                added += 1

    if added and not dry_run:
        with open(TECHNOLOGIES, "w", encoding="utf-8") as fh:
            json.dump(techs, fh, indent=2, ensure_ascii=False)
            fh.write("\n")
    return added


def check_registry(cfg: dict) -> int:
    """Every registry id a trigger points at must EXIST in the registry.

    WHY. This file is the one home for the SEARCH QUERIES; emc-systems-map.json is the one
    home for the route<->blocker mapping. Two files, one vocabulary — which is exactly the
    shape that rots silently: a route gets renamed there, the pointer here keeps rendering,
    and a scan hit names a route nobody can find. Cheap to check, so check it.

    ⭐ NO LONGER ONE-DIRECTIONAL — CLOSED 2026-08-05. ⚠ Superseded, retained: *"the reverse
    (every `revival_trigger` in the registry names a TRG-* that exists here) cannot be checked
    until the registry carries that field; as of 2026-08-03 it does not."* It does. All 22
    revival triggers carry `scan_trigger`, and `systems/graph/technologies.json` carries it too.
    The reverse direction is now checked by `systems_check.check_scan_interop`, which fails when
    a TECH-* names a TRG-* that does not exist here AND warns when a TRG-* here is watched by no
    TECH-* -- a trigger nobody has attached a consequence to fires into nothing.

    This docstring is corrected rather than deleted because it was accurate when written and
    stale for two days, which is the failure mode the whole register exists to make visible.
    """
    problems: list[str] = []
    if not os.path.exists(REGISTRY):
        print(f"trigger_scan --check: registry not found at {REGISTRY} — skipping cross-check")
        return 0
    with open(REGISTRY, encoding="utf-8") as fh:
        reg = json.load(fh)
    routes = {r["id"] for r in reg.get("routes", [])}
    blockers = {b["id"] for b in reg.get("blockers", [])}

    seen_ids: set[str] = set()
    for t in cfg["triggers"]:
        tid = t["id"]
        if tid in seen_ids:
            problems.append(f"{tid}: duplicate trigger id")
        seen_ids.add(tid)
        if not tid.startswith("TRG-"):
            problems.append(f"{tid}: trigger ids must start with TRG-")
        if t.get("status") not in ("watching", "landed", "superseded"):
            problems.append(f"{tid}: status {t.get('status')!r} is not one of watching/landed/superseded")
        if t.get("scan_enabled") and not (
            (t.get("search") or {}).get("europepmc") or (t.get("search") or {}).get("arxiv")
        ):
            problems.append(f"{tid}: scan_enabled with no queries")
        if not t.get("scan_enabled") and not t.get("not_searchable_because"):
            problems.append(f"{tid}: scan disabled without not_searchable_because")
        r = t.get("reopens") or {}
        for x in r.get("registry_routes", []) or []:
            if x not in routes:
                problems.append(f"{tid}: route id {x} not in emc-systems-map.json")
        for x in r.get("registry_blockers", []) or []:
            if x not in blockers:
                problems.append(f"{tid}: blocker id {x} not in emc-systems-map.json")

    reverse = [
        (r.get("id"), r["revival_trigger"])
        for r in reg.get("routes", [])
        if isinstance(r, dict) and r.get("revival_trigger")
    ]
    for rid, trg in reverse:
        names = trg if isinstance(trg, list) else [trg]
        for n in names:
            if isinstance(n, str) and n.startswith("TRG-") and n not in seen_ids:
                problems.append(f"registry route {rid}: revival_trigger {n} has no entry here")

    for p in problems:
        print(f"ERROR {p}")
    print(
        f"trigger_scan --check: {len(problems)} ERROR across {len(cfg['triggers'])} trigger(s); "
        f"{len(reverse)} registry revival_trigger field(s) seen"
        + ("" if reverse else " — reverse direction is UNCHECKED until the registry carries that field")
    )
    return 1 if problems else 0


# ------------------------------------------------------------------------------------ main


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true",
                    help="validate the trigger file against emc-systems-map.json and exit")
    ap.add_argument("--seed", action="store_true",
                    help="fill the ledger from the full window and append nothing to IDEAS.md")
    ap.add_argument("--report-days", type=int, default=int(os.environ.get("TRIGGER_REPORT_DAYS", "21")),
                    help="only hits published within this many days are appended to IDEAS.md")
    ap.add_argument("--max-per-trigger", type=int,
                    default=int(os.environ.get("TRIGGER_MAX_PER", "3")),
                    help="cap on IDEAS.md bullets per trigger per run")
    ap.add_argument("--only", default=os.environ.get("TRIGGER_ONLY", ""),
                    help="comma-separated trigger ids to scan (default: all enabled)")
    ap.add_argument("--dry-run", action="store_true", help="write nothing; print what would happen")
    args = ap.parse_args()

    with open(TRIGGERS, encoding="utf-8") as fh:
        cfg = json.load(fh)
    if args.check:
        return check_registry(cfg)
    ledger = load_ledger()
    today = _dt.date.today()
    today_s = today.isoformat()

    only = {x.strip() for x in args.only.split(",") if x.strip()}
    run = {"date": today_s, "mode": "seed" if args.seed else "scan",
           "triggers": 0, "queries": 0, "new_hits": 0, "appended": 0, "errors": []}
    per_trigger: dict[str, dict] = {}
    fresh_by_trigger: dict = {}
    bullets: list[str] = []

    for t in cfg["triggers"]:
        if not t.get("scan_enabled"):
            continue
        if t.get("status") != "watching":
            continue
        if only and t["id"] not in only:
            continue

        s = {"queries": 0, "seen": 0, "in_window": 0, "new": 0, "appended": 0}
        search = t.get("search", {}) or {}
        window = int(search.get("window_days") or 120)
        must = search.get("must_match") or []
        also = search.get("also_match") or []
        excl = search.get("exclude_match") or []
        results: list[dict] = []

        for q in search.get("europepmc", []) or []:
            s["queries"] += 1
            run["queries"] += 1
            try:
                results += epmc_search(q)
            except Exception as e:  # noqa: BLE001
                run["errors"].append(f"{t['id']} europepmc: {e}")
            time.sleep(SLEEP_S)
        for q in search.get("arxiv", []) or []:
            s["queries"] += 1
            run["queries"] += 1
            try:
                results += arxiv_search(q)
            except Exception as e:  # noqa: BLE001
                run["errors"].append(f"{t['id']} arxiv: {e}")
            time.sleep(SLEEP_S)

        s["seen"] = len(results)
        known = ledger["hits"].setdefault(t["id"], {})
        # Europe PMC returns the SAME paper under two ids when it is both in PMC and MED, and
        # two of a trigger's queries commonly overlap -- the 2026-08-03 run reported one Keap1
        # paper twice under one trigger. Id-level dedup cannot see that; title-level can.
        seen_titles = {
            re.sub(r"[^a-z0-9]+", " ", (v.get("title") or "").lower()).strip()
            for v in known.values()
        }
        fresh: list[dict] = []
        for h in results:
            if not h["title"] or not _matches(h["title"], must, also, excl):
                continue
            age = _days_old(h["date"], today)
            if age is None or age > window or age < -3:
                continue
            s["in_window"] += 1
            if h["id"] in known:
                continue
            norm = re.sub(r"[^a-z0-9]+", " ", h["title"].lower()).strip()
            if norm in seen_titles:
                known[h["id"]] = {**h, "first_seen": today_s, "duplicate_of_title": True}
                continue
            seen_titles.add(norm)
            s["new"] += 1
            rec = dict(h)
            rec["first_seen"] = today_s
            rec["age_days_at_first_seen"] = age
            known[h["id"]] = rec
            fresh.append(rec)
        fresh_by_trigger[t["id"]] = list(fresh)

        run["new_hits"] += s["new"]
        if not args.seed:
            fresh.sort(key=lambda h: h.get("date", ""), reverse=True)
            for h in fresh[: args.max_per_trigger]:
                if (h.get("age_days_at_first_seen") or 10**6) <= args.report_days:
                    bullets.append(ideas_bullet(t, h, today_s))
                    s["appended"] += 1
        run["appended"] += s["appended"]
        per_trigger[t["id"]] = s
        run["triggers"] += 1
        print(f"{t['id']}: queries={s['queries']} seen={s['seen']} in_window={s['in_window']} "
              f"new={s['new']} appended={s['appended']}", flush=True)

    ledger["runs"].append(run)

    # Record ungraded signals against the technology register. Runs BEFORE the dry-run return so a
    # dry run reports what it would write without writing it.
    signals = write_pending_signals(fresh_by_trigger, today_s, dry_run=args.dry_run)
    run["signals_recorded"] = signals
    if signals:
        print(f"pending_signals: recorded {signals} ungraded signal(s) against the technology register "
              f"-- ⚠ UNVALIDATED LEADS, not status changes", flush=True)

    if args.dry_run:
        print(json.dumps({"run": run, "bullets": bullets}, indent=2))
        return 0

    if bullets:
        append_to_ideas(bullets)
    with open(LEDGER, "w", encoding="utf-8") as fh:
        json.dump(ledger, fh, indent=1, sort_keys=False)
        fh.write("\n")
    write_board(cfg, ledger, run, per_trigger)

    summary = (
        f"trigger-scan {today_s} ({run['mode']}): {run['triggers']} triggers, {run['queries']} queries, "
        f"{run['new_hits']} new hits, {run['appended']} appended to IDEAS.md, "
        f"{len(run['errors'])} query failures"
    )
    print(summary)
    step = os.environ.get("GITHUB_STEP_SUMMARY")
    if step:
        with open(step, "a", encoding="utf-8") as fh:
            fh.write("### " + summary + "\n\n")
            for e in run["errors"]:
                fh.write(f"- query failure: `{e}`\n")
    # A query failure is NOT a null result -- but it is also not a reason to fail the job and
    # lose the hits that did land. It is recorded in the ledger, the board and the step summary.
    return 0


if __name__ == "__main__":
    sys.exit(main())
