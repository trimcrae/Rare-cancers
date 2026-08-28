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
    that reason; a method paper posted to a venue none of the sources indexes is missed.
  * PREPRINTS ARE UNREFEREED BY CONSTRUCTION. The preprint lane exists to see a capability
    COMING, not to credit it as arrived -- a preprint hit is the weakest lead on the board and
    is marked as one. It never moves a forecast on its own; it says where to look.
  * A miss is silent. The run log records what was SEARCHED, so an empty result is
    distinguishable from a scan that did not run -- CLAUDE.md section 4: an absent reading is
    not a reading of absence.

SOURCES (both need unrestricted egress -- this cannot run in the dev sandbox; CLAUDE.md
section 6 routes it through GitHub Actions):
  * Europe PMC REST   https://www.ebi.ac.uk/europepmc   (published + SRC:PPR preprints)
  * arXiv Atom API    https://export.arxiv.org           (preprints)
  * ChemRxiv API      https://chemrxiv.org/engage        (preprints -- the chemistry half that
                                                          neither of the other two reaches)

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
#: The preprint pipeline board -- what is coming, keyed by the BLOCKER it would reopen.
PREPRINT_BOARD = os.path.join(_ROOT, "research", "method-watch-preprint-pipeline.md")
IDEAS = os.path.join(_ROOT, "research", "IDEAS.md")
#: The systems model's technology register. The scan writes UNGRADED SIGNALS into it and nothing else.
TECHNOLOGIES = os.path.join(_ROOT, "systems", "graph", "technologies.json")

IDEAS_SECTION = "## 🔄 Auto-captured field-scan advances (review + integrate into the board above)"

EPMC = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
ARXIV = "https://export.arxiv.org/api/query"
CHEMRXIV = "https://chemrxiv.org/engage/chemrxiv/public-api/v1/items"
UA = "rare-cancers-trigger-scan (https://github.com/trimcrae/Rare-cancers)"

#: Preprint lane -- the SRC:PPR pass and ChemRxiv. On by default: a preprint is the earliest
#: observable signal that a forecast band is about to move, and the whole point of the register
#: is to see a capability coming rather than to learn it landed. Set TRIGGER_PREPRINTS=0 to run
#: the published-only corpus (e.g. to reproduce a pre-2026-08-08 board).
PREPRINT_LANE = os.environ.get("TRIGGER_PREPRINTS", "1") not in ("0", "false", "no")

# Politeness. These APIs are public and free; none is ours to hammer.
SLEEP_S = float(os.environ.get("TRIGGER_SCAN_SLEEP", "1.5"))
TIMEOUT_S = 60


# --------------------------------------------------------------------------- fetch helpers


def _get(url: str, tries: int = 3, timeout: int | None = None) -> bytes:
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
            with urllib.request.urlopen(req, timeout=timeout or TIMEOUT_S) as r:
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


def epmc_preprint_search(query: str, page_size: int = 25) -> list[dict]:
    """The SAME curated query, scoped to Europe PMC's preprint records (`SRC:PPR`).

    ⭐ WHY THIS REUSES THE QUERY RATHER THAN ADDING A NEW ONE (2026-08-08, trimcrae: "scan for
    open not yet published pre-prints ... that could help us plan what's coming"). Each trigger's
    europepmc queries are hand-curated against a named capability, and its `must_match` /
    `exclude_match` lists are what stop `ternary alloy` scoring as a ternary-complex paper. A
    second hand-written preprint query set would be a SECOND home for the same search intent and
    would drift from the first -- rule 1's exact failure mode. Appending the source filter keeps
    one home for the intent and changes only the corpus.

    ⚠ A preprint is a LEADING indicator and nothing more. It is unrefereed by construction, so it
    moves a forecast's `what_would_move_this` no further than a claim does; what it buys is
    warning. `on_fire` still says read the paper and check the criterion.
    """
    return [dict(h, is_preprint=True) for h in epmc_search(f"({query}) AND SRC:PPR", page_size)]


#: Consecutive failures after which a source is dropped for the REST OF THE RUN.
#: ⛔ ADDED AFTER A MEASURED HANG (2026-08-08). ChemRxiv was added as a new source with no
#: bounded failure, and `_get` retries 3 times against a 60 s timeout -- so ONE unreachable
#: source costs ~186 s per query, and the scan issues 2 ChemRxiv queries per trigger. The run
#: was cancelled at 25 minutes on a projected 3.4 HOURS, having produced nothing: the abstract
#: fetch runs after the query phase, so a slow source starves the step it was added to serve.
#: ⚠ The breaker must be LOUD. A source that silently stops being queried is the
#: credited-but-silent scanner this repository keeps rediscovering -- so tripping it writes an
#: error into the run log, which the board renders.
SOURCE_FAILURE_LIMIT = 3
#: Shorter than TIMEOUT_S: a search API that has not answered in this long is not going to.
SEARCH_TIMEOUT_S = 20
_source_failures: dict[str, int] = {}


def source_is_live(source: str) -> bool:
    return _source_failures.get(source, 0) < SOURCE_FAILURE_LIMIT


def note_source_failure(source: str) -> bool:
    """Record a failure; return True if this one TRIPPED the breaker."""
    _source_failures[source] = _source_failures.get(source, 0) + 1
    return _source_failures[source] == SOURCE_FAILURE_LIMIT


def chemrxiv_search(term: str, max_results: int = 15) -> list[dict]:
    """ChemRxiv, which NEITHER existing source reaches.

    ⛔ MEASURED GAP, and the reason this is worth a new source rather than a widened query: this
    scanner's own header records that "Europe PMC indexes preprint servers unevenly", and arXiv is
    queried separately for exactly that reason -- but arXiv is where the ML-methods half posts and
    ChemRxiv is where the CHEMISTRY half does. Free-energy methods, degrader chemistry and
    induced-proximity design papers routinely appear on ChemRxiv months before a journal, and
    every one of them would have been invisible here.
    """
    qs = urllib.parse.urlencode({"term": term, "limit": str(max_results), "sort": "PUBLISHED_DATE_DESC"})
    data = json.loads(_get(f"{CHEMRXIV}?{qs}", tries=1, timeout=SEARCH_TIMEOUT_S)
                      .decode("utf-8", "replace"))
    out = []
    for row in data.get("itemHits", []) or []:
        it = row.get("item") or {}
        doi = (it.get("doi") or "").strip()
        short = doi.rsplit("/", 1)[-1] if doi else (it.get("id") or "")[:40]
        out.append(
            {
                "id": f"chemRxiv/{short}",
                "title": re.sub(r"\s+", " ", (it.get("title") or "")).strip().rstrip("."),
                "date": (it.get("statusDate") or it.get("publishedDate") or "")[:10],
                "venue": "ChemRxiv",
                "source": "chemrxiv",
                "url": f"https://doi.org/{doi}" if doi else "https://chemrxiv.org",
                "is_preprint": True,
            }
        )
    return out


def fetch_abstracts(ids: list[str]) -> dict[str, str]:
    """Abstracts for specific hit ids. Europe PMC by query, arXiv by id_list.

    ⭐ WHY THE SCANNER FETCHES THESE AND NOT A HUMAN (2026-08-08, trimcrae: "You're not going to
    read the papers? You should at least read the abstracts right?"). The board's whole banner is
    that every row is UNREAD -- and it was, because the sandbox cannot reach EBI or arXiv, so
    reading one meant a CI round-trip nobody was going to make per paper. A title is not enough to
    grade a trigger: `TRG-COFOLD-TERNARY-ASSEMBLY`'s own `on_fire` says do NOT read a global
    accuracy number as an assembly claim, and a title cannot tell you which one a paper reports.
    Batch-fetching the abstract is the cheapest thing that makes the criterion checkable at all.

    ⚠ AN ABSTRACT IS STILL NOT THE PAPER. It is enough to REJECT a false positive with confidence
    and only enough to PROMOTE a lead to "worth the full read". No status changes from this.
    """
    out: dict[str, str] = {}
    epmc_ids = [i for i in ids if not i.startswith(("arXiv/", "chemRxiv/"))]
    arx_ids = [i.split("/", 1)[1] for i in ids if i.startswith("arXiv/")]

    # ⛔ BATCHED, NOT ONE REQUEST PER PAPER (2026-08-08, second cancelled run). The first version
    # issued one Europe PMC call per id with the default 3-try/60 s budget -- 60 papers meant 60
    # sequential calls and, on any rate-limit, up to 186 s EACH. A single-trigger run sat in this
    # loop for nine minutes and was cancelled. Europe PMC accepts an OR of ids in one query, so 60
    # papers is 3 requests. The bug was mine twice over: I bounded ChemRxiv for exactly this
    # failure and left the identical unbounded retry in the call site the fix existed to serve.
    for chunk in [epmc_ids[k:k + 20] for k in range(0, len(epmc_ids), 20)]:
        if not source_is_live("epmc_abstracts"):
            break
        terms = " OR ".join(f'EXT_ID:"{i.split("/", 1)[1] if "/" in i else i}"' for i in chunk)
        by_bare = {(i.split("/", 1)[1] if "/" in i else i): i for i in chunk}
        try:
            qs = urllib.parse.urlencode({"query": f"({terms})", "format": "json",
                                         "resultType": "core", "pageSize": str(len(chunk))})
            d = json.loads(_get(f"{EPMC}?{qs}", tries=1, timeout=SEARCH_TIMEOUT_S)
                           .decode("utf-8", "replace"))
            for r in d.get("resultList", {}).get("result", []) or []:
                key = by_bare.get(str(r.get("id") or "")) or by_bare.get(str(r.get("pmid") or "")) \
                    or by_bare.get(str(r.get("pmcid") or ""))
                if key and r.get("abstractText"):
                    out[key] = re.sub(r"<[^>]+>", " ", r["abstractText"]).strip()
        except Exception:  # noqa: BLE001, S110 -- a missing abstract is never a run failure
            note_source_failure("epmc_abstracts")
        time.sleep(SLEEP_S)

    for chunk in [arx_ids[k:k + 20] for k in range(0, len(arx_ids), 20)]:
        if not source_is_live("arxiv_abstracts"):
            break
        try:
            qs = urllib.parse.urlencode({"id_list": ",".join(chunk), "max_results": "40"})
            root = ET.fromstring(_get(f"{ARXIV}?{qs}", tries=1, timeout=SEARCH_TIMEOUT_S))
            ns = {"a": "http://www.w3.org/2005/Atom"}
            for e in root.findall("a:entry", ns):
                eid = (e.findtext("a:id", "", ns) or "").strip().rsplit("/", 1)[-1]
                summ = re.sub(r"\s+", " ", e.findtext("a:summary", "", ns) or "").strip()
                if summ:
                    out[f"arXiv/{eid}"] = summ
        except Exception:  # noqa: BLE001, S110
            note_source_failure("arxiv_abstracts")
        time.sleep(SLEEP_S)
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
                "is_preprint": True,
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


def _cite_into_line(trg: dict) -> str:
    """Name the artifacts a CONFIRMED hit is owed to, in the bullet a reader actually grades from.

    ⛔ THE BULLET USED TO STOP AT "would reopen", AND THAT IS ONE STEP SHORT OF THE ACTION. A
    reader learned which routes to re-grade and nothing about which committed document makes a
    claim the paper bears on — so the last hop, from "this matters" to "this file now says
    something it should not say alone", was re-derived by hand every time, or not at all. It was
    not at all for PMID 42570981: captured, triaged, cited in two manuscripts, and absent for
    four days from research/modalities/vaccine-construct.json, the artifact proposing exactly the
    design class it reports on.

    ⚠ IT IS A DESTINATION, NOT AN INSTRUCTION. The line says where the QUESTION goes once someone
    has read the paper; research/literature/citation-debt.json records the answer, including
    `declined`. Nothing in this module may write a citation — a hit here is a title match.
    """
    dests = trg.get("cite_into") or []
    if not dests:
        return ""
    return ("**Owed to (once read and graded, record the outcome in "
            "`research/literature/citation-debt.json`):** "
            + ", ".join(f"`{d}`" for d in dests) + ". ")


def ideas_bullet(trg: dict, hit: dict, today: str) -> str:
    return (
        f"- **{today} — trigger `{trg['id']}` matched: {trg['title']}.** "
        f"⚠ **Unvalidated lead — machine-matched on the trigger's own queries, not read and not graded.** "
        f"**Would reopen:** {_reopens_line(trg)}. "
        f"Hit: *{hit['title']}* ({hit['venue']}, {hit['date']}, {hit['id']}) {hit['url']} . "
        f"If it holds: {trg.get('on_fire', 'check the trigger row.')} "
        f"{_cite_into_line(trg)}"
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


def _permanent_blockers() -> set[str]:
    """Blocker ids that no advance retires, read from the systems graph -- the one home for `kind`.

    A missing or unreadable graph returns an EMPTY set, which is fail-OPEN, and that is deliberate
    here: this is a second wall behind systems_check [B8], and a scanner that refused to render a
    board because a sibling file moved would trade a visible wrong row for an invisible missing
    one. The banner already says every row is unrefereed and unread.
    """
    try:
        with open(os.path.join(_ROOT, "systems", "graph", "blockers.json"), encoding="utf-8") as fh:
            return {b["id"] for b in json.load(fh)
                    if b.get("kind") == "fundamental_biological_limit"}
    except (OSError, ValueError, KeyError, TypeError):
        return set()


def _tech_backed_blockers() -> dict[str, set[str]]:
    """trigger id -> the blockers its TECHNOLOGY actually claims to unblock.

    Lets the board distinguish a section the technology register corroborates from one asserted by
    the trigger registry alone. Both are printed -- suppressing the uncorroborated ones would hide
    the disagreement instead of showing it -- but they must not READ alike, which is the same rule
    as CLAUDE.md section 1's "a row we are paying and a row the gate refused must never render
    alike". systems_check [B9] holds the count; this makes it visible where a reader would
    otherwise over-read a tall stack of preprints.
    """
    try:
        with open(os.path.join(_ROOT, "systems", "graph", "technologies.json"), encoding="utf-8") as fh:
            techs = json.load(fh)
    except (OSError, ValueError):
        return {}
    out: dict[str, set[str]] = {}
    for t in techs:
        owned = set((t.get("unblocks") or {}).get("blockers") or [])
        for tid in t.get("scan_trigger") or []:
            out.setdefault(tid, set()).update(owned)
    return out


def _is_preprint(h: dict) -> bool:
    """DERIVED, never trusted from the record.

    ⛔ The flag was added 2026-08-08 and the ledger predates it, so every hit already banked --
    including a live arXiv lead on the ternary-generator trigger -- carries no flag at all. A
    renderer that filtered on the stored field would have shown an EMPTY board while the ledger
    held exactly the rows it was built to surface, and an empty preprint board reads as "nothing
    is coming". CLAUDE.md section 4: an absent reading is not a reading of absence. So the fact is
    recomputed from source and id, which every record has always had, and the stored flag is only
    a fast path.
    """
    if h.get("is_preprint"):
        return True
    if (h.get("source") or "") in ("arxiv", "chemrxiv"):
        return True
    return str(h.get("id") or "").startswith(("PPR/", "arXiv/", "chemRxiv/"))


def write_preprint_board(cfg: dict, ledger: dict, run: dict) -> None:
    """What is in the preprint pipeline, grouped by the BLOCKER it would reopen.

    ⭐ WHY BLOCKER-KEYED AND NOT TRIGGER-KEYED (2026-08-08). The existing board is keyed by
    trigger, which is the right shape for "did my watch fire". It is the wrong shape for the
    question actually asked -- *what is coming that could unblock us* -- because a reader then has
    to map trigger to blocker to forecast by hand, which is the same two-file join the blocker
    register just stopped requiring. Keyed by blocker, a row reads directly against
    `systems/views/registers/blockers.md`: here is the 2028 band, and here is what is on the
    preprint servers that might move it.

    ⛔ A PREPRINT IS THE WEAKEST THING ON THE BOARD. Unrefereed, title-matched, unread. It cannot
    move a forecast and must never be cited. Its whole value is warning -- months of it.
    """
    # ⛔ PERMANENT BLOCKERS ARE EXCLUDED FROM THIS BOARD BY CONSTRUCTION (2026-08-08). Filing a
    # preprint under a `fundamental_biological_limit` would say a paper might lift something no
    # paper can, which is the conflation taxonomy/blockers.md exists to prevent -- and it is not
    # hypothetical: TRG-JUNCTION-PHLA listed BLK-ANTIGEN-COLD until this board was built, so the
    # first render would have printed it. The trigger data is fixed and systems_check [B8] now
    # fails the build on a recurrence; this is the second wall, because the renderer must not
    # depend on a sibling registry staying correct.
    permanent = _permanent_blockers()
    corroborated = _tech_backed_blockers()
    trgs = [t for t in cfg["triggers"] if (t.get("search") or {}).get("europepmc")
            or (t.get("search") or {}).get("arxiv")]
    by_blocker: dict[str, list[tuple[dict, dict]]] = {}
    for t in trgs:
        pres = [h for h in (ledger["hits"].get(t["id"]) or {}).values() if _is_preprint(h)]
        if not pres:
            continue
        for b in (t.get("reopens", {}) or {}).get("registry_blockers") or ["(no blocker mapped)"]:
            if b in permanent:
                continue
            by_blocker.setdefault(b, []).extend((t, h) for h in pres)

    L = [
        "---",
        "id: DOC-METHOD-WATCH-PREPRINT-PIPELINE",
        "title: Preprint pipeline — what is coming, by blocker",
        "level: —",
        "kind: index",
        "status: live",
        "canonical_for: []",
        'purpose: "Unrefereed preprints matching a named reopening trigger, grouped by the blocker '
        'they would reopen — a leading indicator for the forecast bands in the blocker register."',
        'scope: "Preprints only (Europe PMC SRC:PPR, arXiv, ChemRxiv). The published corpus is on '
        'the trigger-scan board."',
        "audience: [maintainers, autonomous research agents]",
        f"date: {run['date']}",
        "last_verified: unverified",
        "---",
        "# Preprint pipeline — what is coming, by blocker\n",
        f"**Last run: {run['date']}** (UTC date stamp from the runner).\n",
        "⛔ **EVERYTHING HERE IS UNREFEREED, TITLE-MATCHED AND UNREAD.** A preprint is the weakest "
        "lead this repository records. It cannot move a forecast band, it is not evidence, and "
        "nothing here may be cited. Its value is WARNING — it is the earliest point at which a "
        "capability becomes visible, often months before the journal version.\n",
        "⚠ **An empty section is not a reading of absence** — it may mean the trigger's queries "
        "do not reach the venue where that work posts. The run log records what was searched.\n",
        "Forecast bands for each blocker: "
        "[`systems/views/registers/blockers.md`](../systems/views/registers/blockers.md).\n",
    ]
    if not by_blocker:
        L.append("_No preprint hits in the ledger yet._\n")
    for b in sorted(by_blocker):
        rows = sorted(by_blocker[b], key=lambda th: th[1].get("date", ""), reverse=True)
        backed = any(b in corroborated.get(t["id"], set()) for t, _ in rows)
        L.append(f"## {b}\n")
        if not backed:
            L.append("⚠ **The technology register does not corroborate this mapping.** Every trigger "
                     "below claims this blocker, and the technology it is registered under does NOT "
                     "list it in `unblocks.blockers` — so these preprints may be stacked against a "
                     "blocker the capability would not actually retire. Counted by systems_check "
                     "`[B9]`; resolve by adding the technology edge or narrowing the trigger.\n")
        L.append("| posted | preprint | venue | via trigger |")
        L.append("|---|---|---|---|")
        for t, h in rows:
            title = (h.get("title") or "")[:110].replace("|", "\\|")
            mark = "" if b in corroborated.get(t["id"], set()) else " ⚠"
            L.append(f"| {h.get('date','—')} | [{title}]({h.get('url','')}) "
                     f"| {h.get('venue','—')} | `{t['id']}`{mark} |")
        abs_rows = [(t, h) for t, h in rows if h.get("abstract")]
        if abs_rows:
            L.append("")
            L.append("<details><summary>Abstracts (fetched, still unrefereed and ungraded)</summary>\n")
            for t, h in abs_rows:
                L.append(f"**{h.get('title','')}** — {h.get('venue','—')}, {h.get('date','—')}\n")
                L.append(f"> {h['abstract'][:1400]}\n")
            L.append("</details>")
        L.append("")
    with open(PREPRINT_BOARD, "w", encoding="utf-8") as fh:
        fh.write("\n".join(L))


def write_board(cfg: dict, ledger: dict, run: dict, per_trigger: dict) -> None:
    # ⛔ FRONTMATTER IS EMITTED HERE BECAUSE THIS FILE IS GENERATED (2026-08-08). It was hand-
    # backfilled into the committed copy, and this writer did not know about it -- so the first
    # scan run in five days silently STRIPPED it and turned systems_check [D4] red ("purpose,
    # scope, audience and freshness are undeclared"). The bug was latent for as long as the scan
    # was not running, which is the same shape as the workflow's own four-day skipped-step
    # incident: a generator and a hand-edit sharing one file, where whichever ran last won.
    # A generated file must emit every part of itself.
    L = [
        "---",
        "id: DOC-METHOD-WATCH-TRIGGER-SCAN",
        "title: Reopening-trigger scan — the board",
        "level: —",
        "kind: index",
        "status: live",
        "canonical_for: []",
        'purpose: "Every named reopening trigger, its state, and the unvalidated literature hits '
        'matching its own queries — so a hit arrives with the routes and blockers it would reopen."',
        'scope: "All scan-enabled triggers. Preprints are additionally boarded by blocker in '
        'method-watch-preprint-pipeline.md."',
        "audience: [maintainers, autonomous research agents]",
        f"date: {run['date']}",
        "last_verified: unverified",
        "---",
    ]
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

    # ⛔ THE ID VOCABULARY IS `systems/graph/`, NOT THIS ONE FILE, AND CHECKING ONLY THE FILE
    # MANUFACTURED SIX ERRORS THAT WERE NOT ERRORS (fixed 2026-08-28). CLAUDE.md §7: "the
    # architecture is systems/ — systems/graph/*.json is the source of truth for every strategy
    # family, route, blocker and forecast". emc-systems-map.json is the MANUSCRIPT-SCOPED subset:
    # 40 routes against the graph's 77, and a strict subset of it (measured — every map route id
    # is a graph route id, and every map blocker id is a graph blocker id). So a trigger pointing
    # at a real route that the manuscript map does not carry — RT-IPD-SURVIVAL, RT-LIMB-PERFUSION,
    # RT-LUNG-DIRECTED, RT-RISK-MODEL, RT-SURVEILLANCE, BLK-NO-CURATED-CLINICAL-DATA, all six of
    # them present in the graph — was reported as a dangling pointer.
    # ⚠ AND THE COST WAS NOT THE FALSE POSITIVES. `--check` was red, and NOTHING RAN IT, so the
    # noise hid a REAL finding sitting in the same output: TRG-CONDENSATE-PARTNER-RESOLUTION was
    # `scan_enabled` with no queries — a row rendering as watched while searching for nothing.
    # That is the same "a --check mode existed and no gate ran it" defect the deposit-artifact
    # gate was built for; scripts/preflight.sh now runs this one too.
    for _graph, _key, _into in (("routes.json", "routes", routes),
                                ("blockers.json", "blockers", blockers)):
        _path = os.path.join(_ROOT, "systems", "graph", _graph)
        if os.path.exists(_path):
            with open(_path, encoding="utf-8") as fh:
                _into.update(x["id"] for x in json.load(fh) if isinstance(x, dict) and "id" in x)

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
        # ⭐ `cite_into` NAMES WHERE A CONFIRMED HIT IS OWED (added 2026-08-28). A path that has
        # been renamed or deleted turns the routing this field exists for back into nothing, and
        # does it silently, so the pointer is checked exactly like the registry ids are.
        # ⚠ THE FIELD IS OPTIONAL BY DESIGN: most triggers watch for a CAPABILITY this repository
        # would then go and use, with no document owing the paper a citation. A fake destination
        # would be worse than none.
        for c in t.get("cite_into") or []:
            if not os.path.exists(os.path.join(_ROOT, c)):
                problems.append(f"{tid}: cite_into path does not exist: {c}")
        r = t.get("reopens") or {}
        for x in r.get("registry_routes", []) or []:
            if x not in routes:
                problems.append(f"{tid}: route id {x} not in systems/graph/routes.json or emc-systems-map.json")
        for x in r.get("registry_blockers", []) or []:
            if x not in blockers:
                problems.append(f"{tid}: blocker id {x} not in systems/graph/blockers.json or emc-systems-map.json")

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
    if problems:
        # ⛔ THE CALLING GATE'S GENERIC REMEDY IS "rerun 'python3 scripts/trigger_scan.py' AND
        # COMMIT THE RESULT", AND THAT IS ACTIVELY WRONG HERE — a bare run is a NETWORK SCAN of
        # Europe PMC, arXiv and ChemRxiv that appends leads to IDEAS.md. Nothing about it fixes a
        # dangling pointer. The producer wins over the generic line (scripts/preflight.sh says so
        # in as many words), so it has to actually say what the fix is.
        print("trigger_scan --check: FIX THE POINTERS, DO NOT REGENERATE. Nothing here is a "
              "generated artifact — each ERROR above is a hand-written field in "
              "research/method-watch-triggers.json that names something that does not exist, or a "
              "trigger claiming to be watched with no queries behind it. A bare "
              "`python3 scripts/trigger_scan.py` runs a live literature scan and fixes none of it.")
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
    ap.add_argument("--no-abstracts", action="store_true",
                    help="skip abstract fetching for preprint hits")
    ap.add_argument("--max-abstracts", type=int,
                    default=int(os.environ.get("TRIGGER_MAX_ABSTRACTS", "60")),
                    help="cap on abstracts fetched per run (the rest fill in next run)")
    ap.add_argument("--no-preprints", action="store_true",
                    help="skip the preprint lane (SRC:PPR + ChemRxiv); published corpus only")
    ap.add_argument("--dry-run", action="store_true", help="write nothing; print what would happen")
    args = ap.parse_args()
    if args.no_preprints:
        globals()["PREPRINT_LANE"] = False

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
            if PREPRINT_LANE:
                # Same curated query, preprint corpus. See epmc_preprint_search.
                s["queries"] += 1
                run["queries"] += 1
                try:
                    results += epmc_preprint_search(q)
                except Exception as e:  # noqa: BLE001
                    run["errors"].append(f"{t['id']} europepmc/preprint: {e}")
                time.sleep(SLEEP_S)
        for q in search.get("arxiv", []) or []:
            s["queries"] += 1
            run["queries"] += 1
            try:
                results += arxiv_search(q)
            except Exception as e:  # noqa: BLE001
                run["errors"].append(f"{t['id']} arxiv: {e}")
            time.sleep(SLEEP_S)
        # ChemRxiv has no per-trigger query list: its API is a single free-text `term`, so the
        # trigger's own must_match vocabulary IS the query, and _matches() filters the return.
        for term in (search.get("chemrxiv") or must[:2]) if PREPRINT_LANE else []:
            if not source_is_live("chemrxiv"):
                break
            s["queries"] += 1
            run["queries"] += 1
            try:
                results += chemrxiv_search(term)
            except Exception as e:  # noqa: BLE001
                if note_source_failure("chemrxiv"):
                    run["errors"].append(
                        f"chemrxiv: DROPPED FOR THIS RUN after {SOURCE_FAILURE_LIMIT} consecutive "
                        f"failures (last: {e}). Every ChemRxiv query below was SKIPPED -- this run's "
                        f"preprint coverage is Europe PMC + arXiv only, and an empty ChemRxiv result "
                        f"is not a reading of absence.")
                else:
                    run["errors"].append(f"{t['id']} chemrxiv: {e}")
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
    # Abstracts for preprints that do not have one yet. Bounded per run so a first pass over a
    # cold ledger cannot turn into a several-hundred-request job; the rest fill in next run.
    if not args.no_abstracts:
        want = []
        for tid, hits in ledger["hits"].items():
            for hid, h in hits.items():
                if _is_preprint(h) and not h.get("abstract"):
                    want.append((tid, hid))
        want = want[: args.max_abstracts]
        if want:
            got = fetch_abstracts([hid for _, hid in want])
            for tid, hid in want:
                if hid in got:
                    ledger["hits"][tid][hid]["abstract"] = got[hid]
            run["abstracts_fetched"] = len(got)
            with open(LEDGER, "w", encoding="utf-8") as fh:
                json.dump(ledger, fh, indent=1, sort_keys=False)
                fh.write("\n")
    write_preprint_board(cfg, ledger, run)

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
