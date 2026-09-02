#!/usr/bin/env python3
"""⛔⛔ THE RECORD OF WHAT THIS LOOP HAS ACTUALLY PUT ON aiXiv — because until now there was none.

★ WHY THIS FILE EXISTS. `publication-authority.json` has declared
`scope.max_versions_per_paper: 3` since 2026-08-26, with its reason written beside it: ELEVEN
versions of `aixiv.260822.000005` never moved its rating above 6 and it trended DOWN as the paper
improved, so an uncapped loop would rediscover that at trimcrae's expense and put ten near-identical
versions under his ORCID.

⚠ **MEASURED 2026-09-02: NO CODE READ THAT NUMBER.** `grep -rn max_versions_per_paper` over the
whole repository returned the JSON defining it, one architecture mention, and one test asserting it
is `>= 1`. `authority_permits('PUB-VACCINE-PATH', 'aixiv', 'new_version')` returned `ok=True` for a
paper carrying **eleven** posted versions against a cap of three. That is the `subagent_width` shape
exactly — a governed number, documented, asserted by one test, and governing nothing — and
`autonomy-state.json` names it in `_ENFORCEMENT_IS_NOT_THIS_FIELD` as the second time this
repository has paid for it.

⛔⛔ **AND THE HARD PART IS NOT THE COMPARISON, IT IS THE COUNT.** There was no machine record of any
aiXiv posting anywhere in `systems/graph/` — `PUB-VACCINE-PATH` is `state: drafted` with no `posted`
block while eleven of its versions are live. The only trace on disk is the filenames under
`research/literature/aixiv-reviews/`, and that is **A LOWER BOUND, NOT A COUNT**: a review file
exists only where a fetch RAN. A post whose review was never fetched leaves no file at all, so a cap
checked against those filenames silently permits posts past the cap — the failure mode is the same
one the cap exists to prevent, wearing a number.

★★ **SO THE DESIGN IS A REGISTER THE POSTING PATH WRITES, PLUS A CROSS-CHECK THAT FAILS CLOSED.**
Argued rather than assumed, because the cheaper option was available:

  * **Counting review files** would have been one function and no new file. It is refused because a
    lower bound used as a cap check is worse than no check: it reads as an enforced cap, and it
    silently permits. CLAUDE.md §4 — an absent reading is not a reading of absence.
  * **The register** is written by the act itself (`record()`, and `aixiv-submission` §"record the
    post" makes it a step of posting rather than a courtesy), so from here on a post that is not
    recorded is a bug in the posting path rather than a hole in the count.
  * **The cross-check is what makes the register honest about its own past.** The twelve backfilled
    rows were read off review filenames and are marked `backfilled_from_review_file`, which is an
    OBSERVATION of a posting, not a RECORD of one — `posted_utc` is null for every one of them,
    because a review file does not say when the version was posted. `reconcile()` then asserts the
    other direction forever: any review file whose `(aixiv_id, version)` has no register row means
    the register is provably incomplete, and `versions_posted` REFUSES rather than returning the
    smaller number. **A count that cannot be established is not permission.**

⛔ THE REGISTER IS APPEND-ONLY, like `amendments.jsonl`. Rewriting history here is the tell that the
cap was worked around, and `--check` is what a gate runs.

USAGE
    python3 research/autonomy/posting_register.py --check        # reconcile; exit 1 on a problem
    python3 research/autonomy/posting_register.py --count PUB-X  # what the cap check will see
    python3 research/autonomy/posting_register.py --record --pub-id PUB-X --aixiv-id aixiv.YYMMDD.NNNNNN \
            --version 1.0 --act submit --posted-utc 2026-09-02T15:13:00Z
"""

from __future__ import annotations

import argparse
import datetime as _dt
import glob
import json
import os
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent.parent

REGISTER = HERE / "aixiv-postings.jsonl"
REVIEWS_DIR = REPO / "research" / "literature" / "aixiv-reviews"

#: ⛔ THE TWO SOURCES ARE KEPT APART AND NEVER COLLAPSED. `recorded_at_post_time` is a record written
#: by the act; `backfilled_from_review_file` is an observation that the act must have happened,
#: inferred from an artifact a later fetch produced. They carry different weight and a reader must be
#: able to tell them apart — CLAUDE.md §4: a populated field is not a measured one.
RECORDED, BACKFILLED = "recorded_at_post_time", "backfilled_from_review_file"
SOURCES = (RECORDED, BACKFILLED)

REQUIRED_FIELDS = ("pub_id", "aixiv_id", "version_label", "act", "source", "recorded_utc")
ACTS = ("submit", "new_version")

#: `aixiv.260822.000005-1.7-reviews.json` -> ("aixiv.260822.000005", "1.7"). ⛔ The version group is
#: deliberately permissive about its shape: the SERVER assigns the label and it has surprised this
#: project before — aiXiv followed version 1.9 with 2.0 (`aixiv-submission` §"version numbering").
_REVIEW_FILE = re.compile(r"^(?P<aixiv_id>aixiv\.\d{6}\.\d{6})-(?P<version>[0-9][0-9.]*)-reviews\.json$")


def _is_utc_instant(value) -> bool:
    if not isinstance(value, str) or not value.strip():
        return False
    try:
        t = _dt.datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    except ValueError:
        return False
    return t.tzinfo is not None and t.utcoffset() == _dt.timedelta(0)


def load(path: pathlib.Path | None = None) -> tuple[list[dict], list[str]]:
    """`(rows, problems)`. ⛔ A malformed line is a PROBLEM, never a skipped line.

    A loader that swallows an unparseable row turns an incomplete register into a clean one, which
    is precisely the arithmetic this module exists to refuse.
    """
    path = path or REGISTER
    rows: list[dict] = []
    problems: list[str] = []
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return [], [f"{path.name} is absent — there is no posting record to count, and an absent "
                    "record is not a record of zero postings"]
    except Exception as exc:
        return [], [f"{path.name} is unreadable ({type(exc).__name__})"]

    seen: dict[tuple[str, str], str] = {}
    for i, line in enumerate(text.splitlines(), 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            problems.append(f"line {i} is not valid JSON — the register must stay machine-readable")
            continue
        if not isinstance(row, dict):
            problems.append(f"line {i} is not a JSON object")
            continue
        for field in REQUIRED_FIELDS:
            if not str(row.get(field) or "").strip():
                problems.append(f"line {i}: `{field}` is empty — a row that cannot say which paper, "
                                "which id, which version or where it came from is not a record")
        if row.get("source") not in SOURCES:
            problems.append(f"line {i}: source {row.get('source')!r} is not one of {list(SOURCES)}")
        if row.get("act") not in ACTS:
            problems.append(f"line {i}: act {row.get('act')!r} is not one of {list(ACTS)}")
        if not _is_utc_instant(row.get("recorded_utc")):
            problems.append(f"line {i}: `recorded_utc` is not an ISO-8601 UTC instant")
        # ⛔ A BACKFILLED ROW MAY NOT CARRY A POSTING TIME, AND THAT IS NOT PEDANTRY. A review file
        # records when the REVIEW was fetched; nothing on disk records when the VERSION was posted.
        # A plausible-looking date here would be a fabricated reading, which CLAUDE.md §4 calls more
        # dangerous than an empty one.
        if row.get("source") == BACKFILLED and row.get("posted_utc") is not None:
            problems.append(f"line {i}: a backfilled row carries `posted_utc` "
                            f"{row.get('posted_utc')!r}; nothing on disk records when a version was "
                            "posted, so this must be null")
        if row.get("source") == RECORDED and not _is_utc_instant(row.get("posted_utc")):
            problems.append(f"line {i}: a row recorded at post time must carry `posted_utc` as an "
                            "ISO-8601 UTC instant")
        key = (str(row.get("aixiv_id")), str(row.get("version_label")))
        owner = str(row.get("pub_id"))
        if key in seen and seen[key] != owner:
            problems.append(f"line {i}: {key[0]} v{key[1]} is attributed to both {seen[key]!r} and "
                            f"{owner!r} — an ambiguous attribution makes every count on this id "
                            "unreliable")
        seen.setdefault(key, owner)
        rows.append(row)
    return rows, problems


def observed_versions(reviews_dir: pathlib.Path | None = None) -> tuple[dict, list[str]]:
    """`({aixiv_id: {version, ...}}, unparsed_filenames)` — read from review FILENAMES.

    ⛔⛔ THIS IS A LOWER BOUND AND IT IS NEVER USED AS A COUNT. A review file exists only where a
    fetch ran, so the true number of posted versions is always at least this and may be more. It is
    used in exactly one direction: to prove the register INCOMPLETE. Reading it the other way — "the
    register says 3, the files say 11, take 11" — would be counting from an artifact that cannot see
    a post nobody fetched, which is the same silent under-count one layer down.
    """
    reviews_dir = reviews_dir or REVIEWS_DIR
    out: dict[str, set] = {}
    unparsed: list[str] = []
    for path in sorted(glob.glob(os.path.join(str(reviews_dir), "*.json"))):
        name = os.path.basename(path)
        m = _REVIEW_FILE.match(name)
        if not m:
            unparsed.append(name)
            continue
        out.setdefault(m.group("aixiv_id"), set()).add(m.group("version"))
    return out, unparsed


def reconcile(path: pathlib.Path | None = None,
              reviews_dir: pathlib.Path | None = None) -> dict:
    """Every problem that makes a count from this register untrustworthy.

    ⭐ THE FORWARD-LOOKING HALF, and the reason backfilling does not make this check vacuous: the
    backfilled rows were derived FROM the review files, so today every file has a row and the check
    is silent. From here on it is not. A version posted without `record()` produces a review file the
    next fetch cycle whose `(aixiv_id, version)` matches no row, and every aiXiv act is then refused
    until the register is reconciled — which is one appended line, and is meant to be.
    """
    rows, problems = load(path)
    known = {(str(r.get("aixiv_id")), str(r.get("version_label"))) for r in rows}
    observed, unparsed = observed_versions(reviews_dir)
    for aixiv_id in sorted(observed):
        for version in sorted(observed[aixiv_id]):
            if (aixiv_id, version) not in known:
                problems.append(
                    f"{aixiv_id} v{version} has a review file on disk and NO row in "
                    f"{REGISTER.name} — a version was posted and not recorded, so any count taken "
                    "from this register is a lower bound. Settle it: append the row "
                    "(`posting_register.py --record`, source backfilled_from_review_file).")
    for name in unparsed:
        problems.append(f"{name} does not parse as `<aixiv-id>-<version>-reviews.json`, so it cannot "
                        "be reconciled against the register — an unreadable filename is not an "
                        "absent posting")
    return {"ok": not problems, "rows": len(rows), "observed_ids": len(observed),
            "problems": problems}


def versions_posted(pub_id: str, path: pathlib.Path | None = None,
                    reviews_dir: pathlib.Path | None = None) -> dict:
    """`{"ok", "count", "why"}` — how many versions of `pub_id` are on aiXiv, or a refusal.

    ⛔ FAILS CLOSED, AND THAT IS THE WHOLE CONTRACT. `ok: False` means the number could not be
    established; it never means zero. A caller that treats a refusal as "no versions yet" has
    rebuilt the defect.
    """
    state = reconcile(path, reviews_dir)
    if not state["ok"]:
        return {"ok": False, "count": None,
                "why": ("the number of posted versions cannot be established: "
                        + "; ".join(state["problems"][:4])
                        + (f" (+{len(state['problems']) - 4} more)"
                           if len(state["problems"]) > 4 else ""))}
    rows, _ = load(path)
    versions = {(str(r.get("aixiv_id")), str(r.get("version_label")))
                for r in rows if r.get("pub_id") == pub_id}
    return {"ok": True, "count": len(versions),
            "why": f"{len(versions)} version(s) of {pub_id} recorded in {REGISTER.name}"}


def record(pub_id: str, aixiv_id: str, version_label: str, act: str,
           posted_utc: str | None = None, source: str = RECORDED,
           evidence: str | None = None, submission_id=None,
           note: str | None = None, path: pathlib.Path | None = None,
           now: str | None = None) -> dict:
    """Append one posting to the register. ⛔ Append-only: this never rewrites an existing line."""
    path = path or REGISTER
    row = {
        "pub_id": pub_id,
        "aixiv_id": aixiv_id,
        "version_label": str(version_label),
        "act": act,
        "source": source,
        "posted_utc": posted_utc,
        "recorded_utc": now or _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    if evidence:
        row["evidence"] = evidence
    if submission_id is not None:
        row["submission_id"] = submission_id
    if note:
        row["note"] = note
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    return row


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true", help="reconcile the register; exit 1 on any problem")
    ap.add_argument("--count", metavar="PUB_ID", help="what the cap check will see for this paper")
    ap.add_argument("--record", action="store_true", help="append one posting")
    ap.add_argument("--pub-id")
    ap.add_argument("--aixiv-id")
    ap.add_argument("--version")
    ap.add_argument("--act", choices=list(ACTS))
    ap.add_argument("--posted-utc")
    ap.add_argument("--source", choices=list(SOURCES), default=RECORDED)
    ap.add_argument("--evidence")
    ap.add_argument("--note")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    if args.record:
        missing = [f for f in ("pub_id", "aixiv_id", "version", "act") if not getattr(args, f)]
        if missing:
            ap.error("--record needs " + ", ".join("--" + m.replace("_", "-") for m in missing))
        row = record(args.pub_id, args.aixiv_id, args.version, args.act,
                     posted_utc=args.posted_utc, source=args.source,
                     evidence=args.evidence, note=args.note)
        print(json.dumps(row, ensure_ascii=False) if args.json else
              f"recorded {row['aixiv_id']} v{row['version_label']} for {row['pub_id']} ({row['source']})")
        return 0

    if args.count:
        result = versions_posted(args.count)
        print(json.dumps(result, indent=2) if args.json else
              f"{args.count}: {result['count'] if result['ok'] else 'UNCOUNTABLE'} — {result['why']}")
        return 0 if result["ok"] else 1

    result = reconcile()
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"{REGISTER.name}: {result['rows']} row(s) over {result['observed_ids']} aiXiv id(s), "
              f"{'OK' if result['ok'] else 'PROBLEMS'}")
        for p in result["problems"]:
            print(f"   ⛔ {p}")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
