#!/usr/bin/env python3
"""Match this week's news items against what each of this program's papers CLAIMS — with an LLM.

⛔ WHY THIS EXISTS, AND WHAT IT REPLACES (2026-08-28, trimcrae). The reopening-trigger scan decides
relevance with hand-written keyword lists, and that is fragile in a way this repository measured:
PMID 42570981 — an off-the-shelf peptide vaccine spanning the EWSR1-FLI1 breakpoint, the closest
human prior art the junction-vaccine route has — matched NONE of the 38 triggers' queries, because
the word "vaccine" appeared in none of them. Keeping a keyword list current against a field nobody
can enumerate in advance is the wrong shape of work. We already hold both halves of the answer: a
list of headlines, and a list of what each of our papers would claim. Matching them is a judgement,
and a judgement is what a model is for.

★★ WHERE IT SITS IS THE WHOLE DESIGN, AND IT IS DELIBERATELY NOT INSIDE THE TRIGGER SCAN.
That scan's bottleneck is its QUERY, not its filter: Europe PMC only returns what the query asked
for, so an LLM placed downstream of a narrow query still never sees the paper the query missed —
it would have made the miss more expensive and no less likely. The newsletter's feeds are BROAD
(a deliberately unscoped oncology catch-all, ClinicalTrials.gov, dated RSS) and are the layer that
actually caught this paper. So the model is placed there, where the candidate pool is wide and the
missing step is "which of our documents does this bear on".

⛔ IT PROPOSES; IT NEVER CITES. Output is a queue for a human or a session to read, exactly like a
trigger hit, and for the same reason: this model has seen a HEADLINE, not a paper. It cannot verify
an identifier, a sample size or an endpoint, and a pipeline that let it write into a manuscript
would put unread evidence into the published record. Rows that survive reading become `open` rows
in research/literature/citation-debt.json, which already refuses a row that names no `blocked_on`.

⛔ AND IT CANNOT NAME A DOCUMENT THAT DOES NOT EXIST. Every returned `publication_id` is checked
against the ids actually sent in the prompt, and anything else is dropped INTO A COUNTED
`rejected` list rather than silently discarded. That check is total and costs nothing, and it is
the one hallucination this design is structurally exposed to.

★ THE BIAS INSTRUMENT. A watch list maintained by people who want their routes to work
under-reports results that cut against them — CLAUDE.md §4, and the reason the vaccine trigger's
`on_fire` says a negative readout fires it too. So `bearing` distinguishes `supports` from
`complicates`, and the queue prints a census of the two. A run that returns only `supports` is not
proof of bias and is not failed for it; it is the number that makes the question askable at all.

Usage:
  python3 scripts/news_match.py --digest research/method-watch-digest.md      # call the API, write the queue
  python3 scripts/news_match.py --digest <path> --dry-run                     # print the prompt, call nothing
  python3 scripts/news_match.py --check                                       # offline: validate the committed queue
"""

import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "research", "modalities"))

PUBLICATIONS = os.path.join(ROOT, "systems", "graph", "publications.json")
TRIGGERS = os.path.join(ROOT, "research", "method-watch-triggers.json")
QUEUE = os.path.join(ROOT, "research", "literature", "news-match-queue.json")

BEARINGS = ["prior_art", "supports", "complicates", "supersedes", "unclear"]

SYSTEM = (
    "You match news items against the claims of a research program, and you produce LEADS for a "
    "human to read — never conclusions.\n\n"
    "The program is entirely in-silico, run by one unaffiliated researcher, against extraskeletal "
    "myxoid chondrosarcoma (EMC), a sarcoma driven by the EWSR1::NR4A3 fusion. It has no wet lab "
    "and no clinic, so a published paper is the only way any of it reaches a patient. You will be "
    "given (A) news items — headlines, with dates and sources — and (B) every paper the program "
    "has or plans, each with one sentence saying what it would CLAIM.\n\n"
    "For each item, decide which papers' claims it bears on.\n\n"
    "RULES.\n"
    "1. `none` is the correct answer for most items, and returning it is not a failure. A large "
    "cancer result that touches none of these claims bears on none of them. Say so.\n"
    "2. A result that CUTS AGAINST a claim bears on it exactly as much as one that supports it, "
    "and you must report it with the same readiness. Use `complicates` for a failed trial, a "
    "negative readout, a discontinued program or a contradicting finding. Under-reporting these "
    "is the specific failure mode this task exists to avoid.\n"
    "3. Judge from the headline. If it is too thin to tell whether it bears on a claim, say "
    "`unclear` rather than guessing in either direction — `unclear` is a request that a human "
    "read the source, which is exactly what this queue is for.\n"
    "4. Use ONLY publication ids from list (B), copied exactly. Never invent one, and never name "
    "a paper that is not in that list.\n"
    "5. `why` is one clause naming the CONNECTION — which part of the claim the item touches. Not "
    "a summary of the news, and never a restatement of a press claim as established fact.\n"
    "6. Relevance is about the CLAIM, not the disease. A result in a different cancer, in a "
    "different fusion, or in a different modality can bear directly on a claim about whether an "
    "approach works; and a paper about EMC can bear on nothing here. Judge the claim.\n"
)

SCHEMA = {
    "type": "object",
    "properties": {
        "matches": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "item_index": {"type": "integer"},
                    "publication_id": {"type": "string"},
                    "bearing": {"enum": BEARINGS},
                    "why": {"type": "string"},
                },
                "required": ["item_index", "publication_id", "bearing", "why"],
                "additionalProperties": False,
            },
        },
        "considered_and_not_matched": {
            "type": "array",
            "description": "Indexes of items looked at that bear on no paper. Every item must "
                           "appear either here or in matches.",
            "items": {"type": "integer"},
        },
    },
    "required": ["matches", "considered_and_not_matched"],
    "additionalProperties": False,
}


def load_publications():
    """The right-hand side of the match: one row per paper, with the sentence it would claim.

    ⛔ READ FROM systems/graph/publications.json AND NOWHERE ELSE. That register is the one home
    for `what_it_would_claim`, and a prompt that restated those sentences would be a second copy
    that drifts the day either is edited. A row with no claim sentence is SKIPPED and counted
    rather than sent with an empty claim — an empty claim matches everything.
    """
    with open(PUBLICATIONS, encoding="utf-8") as fh:
        pubs = json.load(fh)
    rows, skipped = [], []
    for p in pubs:
        claim = (p.get("what_it_would_claim") or "").strip()
        if not claim:
            skipped.append(p["id"])
            continue
        title = p.get("working_title") or (p.get("document") or {}).get("file", "")
        rows.append({"id": p["id"], "title": title, "claim": claim, "state": p.get("state", "")})
    return rows, skipped


def cite_into_map():
    """Where a confirmed hit is owed, per trigger — carried through so the queue names destinations.

    Optional and often empty: most triggers watch for a capability no document owes a citation to.
    """
    if not os.path.exists(TRIGGERS):
        return {}
    with open(TRIGGERS, encoding="utf-8") as fh:
        cfg = json.load(fh)
    return {t["id"]: t["cite_into"] for t in cfg.get("triggers", []) if t.get("cite_into")}


def build_prompt(items, pubs):
    L = ["(A) NEWS ITEMS", ""]
    for i, it in enumerate(items):
        # ⛔ THE LINK IS DELIBERATELY NOT SENT. These are Google News redirect URLs — 300-400
        # opaque base64 characters each — so 43 of them is several thousand tokens of string the
        # model cannot read, cannot follow, and must not be tempted to quote as a source. The link
        # is kept in the QUEUE, which is where the human who follows it is looking.
        L.append(f"[{i}] {it.get('date','')} — {it.get('title','')}")
    L += ["", "(B) THIS PROGRAM'S PAPERS AND WHAT EACH WOULD CLAIM", ""]
    for p in pubs:
        L.append(f"{p['id']} [{p['state']}] {p['title']}")
        L.append(f"    CLAIM: {p['claim']}")
    return "\n".join(L)


def validate(result, items, pubs):
    """Drop what the model could not have known, and COUNT what was dropped.

    Three checks, each cheap and total: an id that was not in the prompt, an item index that does
    not exist, and an empty `why`. None of them is a judgement about whether the match is good —
    that needs a reader — and all three are things a verdict cannot be right about.
    """
    known = {p["id"] for p in pubs}
    ok, rejected = [], []
    for m in result.get("matches", []):
        pid, idx = m.get("publication_id"), m.get("item_index")
        if pid not in known:
            rejected.append({**m, "_rejected": f"publication_id {pid!r} was not in the prompt"})
        elif not isinstance(idx, int) or not (0 <= idx < len(items)):
            rejected.append({**m, "_rejected": f"item_index {idx!r} is out of range"})
        elif not (m.get("why") or "").strip():
            rejected.append({**m, "_rejected": "empty `why`"})
        else:
            ok.append(m)
    return ok, rejected


def build_queue(items, pubs, matches, rejected, considered, model, source):
    by_item = {}
    for m in matches:
        by_item.setdefault(m["item_index"], []).append(
            {"publication_id": m["publication_id"], "bearing": m["bearing"], "why": m["why"]})

    cim = cite_into_map()
    census = {b: 0 for b in BEARINGS}
    for m in matches:
        census[m["bearing"]] += 1

    rows = []
    considered = set(considered or [])
    for i, it in enumerate(items):
        verdicts = by_item.get(i, [])
        rows.append({
            "item": {"date": it.get("date", ""), "title": it.get("title", ""),
                     "link": it.get("link", "")},
            "bears_on": verdicts,
            # ⛔ THE THREE-WAY DISTINCTION IS THE POINT. `matched` and `no_bearing` are both
            # ANSWERS; `not_reached` means the model returned neither a match nor an explicit
            # non-match for this item, which is a gap in the run and not a finding about the item.
            # Collapsing the last two would make an incomplete answer look like a quiet week.
            "status": ("matched" if verdicts else
                       "no_bearing" if i in considered else "not_reached"),
        })

    return {
        "_schema": "news-match-queue/1",
        "_what": "Proposed matches between this week's news items and what this program's papers "
                 "claim. UNVALIDATED LEADS from a model that saw HEADLINES, not papers.",
        "_may_not": "⛔ Nothing here may be cited, and nothing here changes a status. A row is a "
                    "prompt to read the source. Rows that survive reading become `open` rows in "
                    "research/literature/citation-debt.json.",
        "_model": model,
        "_source": source,
        "_produced_by": "scripts/news_match.py",
        "_bearing_census": census,
        "_bias_note": "⚠ `supports` vs `complicates` is here to be COUNTED. A watch list kept by "
                      "people who want these routes to work under-reports the results that cut "
                      "against them, and a run returning only `supports` is the shape that "
                      "failure takes. It is reported, never failed on — a genuinely good week is "
                      "possible and must not be forced to look otherwise.",
        "_cite_into": cim,
        "_rejected": rejected,
        "_rejected_note": "Verdicts dropped by scripts/news_match.py: an invented publication id, "
                          "an out-of-range item, or an empty reason. Kept rather than discarded "
                          "because a hallucination rate nobody records is a hallucination rate "
                          "nobody can notice rising.",
        "items": rows,
    }


def check():
    """Offline validation of the COMMITTED queue. No network, no model, runs in the commit loop."""
    if not os.path.exists(QUEUE):
        print("news_match --check: no queue committed yet — nothing to validate")
        return 0
    with open(QUEUE, encoding="utf-8") as fh:
        q = json.load(fh)
    pubs, _ = load_publications()
    known = {p["id"] for p in pubs}
    problems = []

    if not q.get("_model"):
        problems.append("queue records no `_model` — an LLM verdict nobody can attribute to a "
                        "model is not re-readable, and this file is not reproducible by rerunning")
    for n, row in enumerate(q.get("items", [])):
        status = row.get("status")
        if status not in ("matched", "no_bearing", "not_reached"):
            problems.append(f"item {n}: status {status!r} is not one of "
                            f"matched/no_bearing/not_reached")
        for v in row.get("bears_on", []):
            pid = v.get("publication_id")
            if pid not in known:
                problems.append(f"item {n}: publication_id {pid} is not in "
                                f"systems/graph/publications.json — it was renamed or invented")
            if v.get("bearing") not in BEARINGS:
                problems.append(f"item {n}: bearing {v.get('bearing')!r} is not one of {BEARINGS}")
            if not (v.get("why") or "").strip():
                problems.append(f"item {n}: a verdict with no reason")
        if row.get("bears_on") and status != "matched":
            problems.append(f"item {n}: has verdicts but status is {status!r}")

    for p in problems:
        print(f"ERROR {p}")
    n_items = len(q.get("items", []))
    stale = [p for p in (q.get("_rejected") or [])]
    print(f"news_match --check: {len(problems)} ERROR across {n_items} queued item(s); "
          f"{len(stale)} verdict(s) were rejected at write time; census {q.get('_bearing_census')}")
    if problems:
        print("news_match --check: FIX THE QUEUE OR RERUN THE MATCHER — this file is a committed "
              "product of a model run, not a hand-maintained list. A publication id that no longer "
              "resolves usually means the register was renamed under it.")
    return 1 if problems else 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--digest", help="path to a method-watch digest markdown file")
    ap.add_argument("--items", help="path to a JSON list of {date,title,link} instead of a digest")
    ap.add_argument("--max-items", type=int, default=60)
    ap.add_argument("--dry-run", action="store_true", help="print the prompt; call nothing")
    ap.add_argument("--check", action="store_true", help="validate the committed queue and exit")
    args = ap.parse_args()

    if args.check:
        return check()

    if args.items:
        with open(args.items, encoding="utf-8") as fh:
            items = json.load(fh)
    elif args.digest:
        # ⛔ REUSE THE DIGEST'S OWN PARSER. email_digest.treatment_headlines already knows the
        # digest's shape, its 🆕 marker and its cross-feed dedupe; a second parser of one format
        # is the drift this repository's first rule is about. Only the CAP differs, and for a
        # reason: the email shows the top few, this reads everything fresh.
        from email_digest import treatment_headlines
        with open(args.digest, encoding="utf-8") as fh:
            items = treatment_headlines(fh.read(), cap=args.max_items)
    else:
        print("news_match: give --digest or --items", file=sys.stderr)
        return 2

    if not items:
        # An empty digest section is NOT a quiet week; it is a digest with no news section, or a
        # generator that failed before writing one. Say which, and write nothing.
        print("news_match: no fresh news items found in the source — writing nothing. "
              "That is an absent reading, not a reading of absence.")
        return 0

    pubs, skipped = load_publications()
    if skipped:
        print(f"news_match: {len(skipped)} publication(s) carry no `what_it_would_claim` and were "
              f"not offered to the model: {', '.join(skipped)}")
    prompt = build_prompt(items, pubs)

    if args.dry_run:
        print(prompt)
        print(f"\n[dry run] {len(items)} item(s) x {len(pubs)} publication(s); "
              f"{len(prompt)} prompt chars; nothing was sent.")
        return 0

    from mailer import llm_json
    result = llm_json(prompt, SYSTEM, SCHEMA, max_tokens=8000)
    if result is None:
        # ⛔ FAIL, DO NOT WRITE AN EMPTY QUEUE. A queue of zero matches and a call that never
        # happened look identical once committed, and the second one would read as "the model
        # considered this week and found nothing".
        print("news_match: the model call did not return a usable answer; queue NOT written",
              file=sys.stderr)
        return 1

    matches, rejected = validate(result, items, pubs)
    queue = build_queue(items, pubs, matches, rejected,
                        result.get("considered_and_not_matched"), result.get("_model", "unknown"),
                        args.digest or args.items)
    with open(QUEUE, "w", encoding="utf-8") as fh:
        json.dump(queue, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    print(f"news_match: wrote {QUEUE} — {len(matches)} match(es) over {len(items)} item(s), "
          f"{len(rejected)} rejected; census {queue['_bearing_census']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
