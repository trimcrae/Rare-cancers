#!/usr/bin/env python3
"""CLOSED-ROUTES-2 — GENERATE (never hand-write) the unapplied diff that adds the
uncatalogued retrieval/data-access closures to the standing negative record.

HLA-COVERAGE-2 hit `git apply --check` exit 128 on a hand-written patch. This script
builds the new text in memory, runs difflib.unified_diff against the file exactly as it
is on disk at the moment of use, and writes the result. Nothing here is typed by hand.

Only rows with in_record == "no" are added, and a row with no evidence locator is refused.
Cataloguing a closure does NOT reopen it: no row below is a plan or an invitation to retry.
"""
import difflib, hashlib, json, os, sys

REPO = "/home/user/Rare-cancers"
LANE = ("research/autonomy/opus-capacity-campaign-20260908/paper-lane/"
        "PORTFOLIO-INVESTIGATIONS-2026-09-08/CLOSED-ROUTES-2")
RECORD = "research/manuscripts/methods-record/closed-routes-negative-record.md"
COVERAGE = os.path.join(REPO, LANE, "closed-route-coverage.json")
OUTDIFF = os.path.join(REPO, LANE, "UNAPPLIED-closed-routes-additions.diff")
ANCHOR = "## 10 · References\n"


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def md_escape(s):
    return s.replace("|", "\\|")


def main():
    cov = json.load(open(COVERAGE, encoding="utf-8"))
    add = [r for r in cov["routes"] if r["in_record"] == "no"]

    # Fence: a row without its lane's own evidence path may NOT be added.
    for r in add:
        if not r.get("evidence_locator"):
            print("REFUSED - row %s has no evidence locator" % r["route_id"], file=sys.stderr)
            return 3
        for p in r["evidence_locator"]:
            if not os.path.exists(os.path.join(REPO, p)):
                print("REFUSED - %s locator missing on disk: %s" % (r["route_id"], p),
                      file=sys.stderr)
                return 4
    if not add:
        print("nothing uncatalogued; no diff to generate", file=sys.stderr)
        return 5

    raw = open(os.path.join(REPO, RECORD), "rb").read()
    print("record sha256 at generation: %s" % sha256_bytes(raw))
    old = raw.decode("utf-8").splitlines(keepends=True)
    if ANCHOR not in old:
        print("REFUSED - anchor not found: %r" % ANCHOR, file=sys.stderr)
        return 6
    if old.count(ANCHOR) != 1:
        print("REFUSED - anchor matched %d times, must be exactly once" % old.count(ANCHOR),
              file=sys.stderr)
        return 7
    idx = old.index(ANCHOR)

    block = []
    block.append("## 9A · Retrieval closures evidenced by "
                 "OPUS-CAPACITY-CAMPAIGN-20260908\n")
    block.append("\n")
    block.append("**A different class from the seven, and filed separately for that reason.** "
                 "Sections 1–9\n")
    block.append("are about *therapeutic* routes closed on argument. The rows below are "
                 "**retrieval and data-access**\n")
    block.append("closures: a source that returns nothing, a body that arrives stripped, an "
                 "artifact that is built at\n")
    block.append("run time from a network source and is therefore not in this checkout. They "
                 "close no therapeutic\n")
    block.append("route and they carry no closure *kind* from §3; they record what could not be "
                 "read, and what that\n")
    block.append("costs the results that depend on it. Each is established by the retained "
                 "evidence its lane wrote at\n")
    block.append("the time — **listing one here is a catalogue entry, not a plan to retry it, "
                 "and re-probing a refused\n")
    block.append("host to \"confirm\" a refusal is exactly what this repository forbids.** "
                 "Where a row names a closed\n")
    block.append("route (B1/B2, B8), that route **stays closed**; the entry states the "
                 "consequence, and the affected\n")
    block.append("quantity is reported UNKNOWN rather than substituted.\n")
    block.append("\n")
    block.append("| # | route | what closed, and on what evidence | class | evidence locator |\n")
    block.append("|---|---|---|---|---|\n")
    for i, r in enumerate(add, 1):
        loc = "<br>".join("`%s`" % p for p in r["evidence_locator"])
        block.append("| %d | `%s` | %s | `%s` | %s |\n" % (
            i, r["route_id"], md_escape(r["closure_statement"]),
            r["closure_class"], loc))
    block.append("\n")
    block.append("**Coverage as measured, not asserted.** All %d rows were checked against this "
                 "document by a\n" % cov["n_routes"])
    block.append("literal token scan and **%d of %d were absent from it** — this section is the "
                 "first place any of\n" % (cov["n_uncatalogued"], cov["n_routes"]))
    block.append("them is catalogued. The scan, its tokens, its per-token hits and the "
                 "document hash it ran against\n")
    block.append("are in\n")
    block.append("[`%s/closed-route-coverage.json`](../../../%s/closed-route-coverage.json).\n"
                 % (LANE, LANE))
    block.append("\n")
    block.append("---\n")
    block.append("\n")

    new = old[:idx] + block + old[idx:]

    diff = list(difflib.unified_diff(old, new,
                                     fromfile="a/" + RECORD, tofile="b/" + RECORD, n=3))
    header = ["diff --git a/%s b/%s\n" % (RECORD, RECORD)]
    text = "".join(header + diff)
    with open(OUTDIFF, "w", encoding="utf-8") as f:
        f.write(text)
    print("wrote %s" % OUTDIFF)
    print("rows added: %d" % len(add))
    print("diff lines: %d" % len(text.splitlines()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
