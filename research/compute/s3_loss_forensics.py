#!/usr/bin/env python3
"""S3 OBJECT-LOSS FORENSICS — re-derive WHEN a prefix was emptied, from committed artifacts alone.

WHY THIS EXISTS (2026-09-01, seat S11-DDG, ledger AUT-078). `s3://sagemaker-us-east-2-646605541856/
nr4a3-step1-fanout/results/` went from 8,510 objects to 10. The obvious explanation — the one this
repository has written down twice, in `archive_results.py`'s header and in `results/PROVENANCE.md` — is an
S3 lifecycle expiration. That is a "probably", and CLAUDE.md §4 wants the observation that discriminates.

THE OBSERVATION, and why it needs no credentials. `archive-results-aws.yml` commits a per-prefix
`results/<prefix>/MANIFEST.json` listing every key it found. Git therefore holds a series of dated S3
listings. Two properties of that series separate a one-shot deletion from a live expiry rule:

  * A live `Expiration: Days=N` rule keeps biting. Between two listings N days apart it must REMOVE keys.
    A one-shot event removes nothing after itself. -> `removed` between consecutive listings.
  * A lifecycle rule's cutoff is a whole-day, midnight-UTC boundary, and its deletions are asynchronous and
    smeared over hours. A bulk delete's cutoff is a sharp instant at an arbitrary minute. -> the
    `oldest_surviving` instant, read from the creation timestamp many lanes embed in the key name.

This module reads only `git show` output. No boto3, no credentials, no network, no AWS permissions — which
is the point: the sandbox that most needs this answer is the one that cannot reach the bucket
(`AWS_ACCESS_KEY_ID` there is the literal placeholder `proxy-injected`).

WHAT IT CANNOT DO. It sees only prefixes the archive workflow lists, only as often as that workflow runs,
and only keys that carry their own timestamp. A prefix whose keys are undated reports
`oldest_surviving: None` — that is an unreadable instrument, NOT a finding of "no loss", and it is printed
as UNKNOWN rather than omitted.

Run:  python3 research/compute/s3_loss_forensics.py [--json] [--repo PATH]
      python3 research/compute/s3_loss_forensics.py --selftest      # pure logic, no git
"""
import argparse
import json
import os
import re
import subprocess
import sys

# The creation instant many lanes embed in their key names, e.g.
# nrv04-retro-results/collect/nrv04-retro-collect-20260813T003138Z.json
KEY_TS = re.compile(r"(20\d{6}T\d{6}Z)")


def key_instant(key):
    """The creation instant embedded in a key name, or None when the key carries none."""
    m = KEY_TS.search(key)
    return m.group(1) if m else None


def compare(prev_keys, keys):
    """(added, removed) between two listings of one prefix. Sorted, so the output is diffable."""
    a, b = set(prev_keys), set(keys)
    return sorted(b - a), sorted(a - b)


def summarise(keys):
    """Oldest/newest embedded instant and how many keys carry one.

    ⛔ `dated` is reported beside `n` on purpose: a prefix where 5 of 2825 keys are undated is a sound
    reading, and one where 0 of 10 are is no reading at all. Collapsing those two into a bare timestamp is
    how an absent measurement gets read as a measurement of absence.
    """
    ts = sorted(t for t in (key_instant(k) for k in keys) if t)
    return {"n": len(keys), "dated": len(ts),
            "oldest_surviving": ts[0] if ts else None,
            "newest_surviving": ts[-1] if ts else None}


def _git(repo, *args):
    return subprocess.check_output(["git", "-C", repo, *args], text=True)


def manifest_paths(repo):
    out = _git(repo, "ls-files", "results/*/MANIFEST.json")
    return sorted(p for p in out.split("\n") if p.strip())


def history(repo, path):
    """[(commit, iso-date, [keys])] for one MANIFEST, oldest first. Unparseable revisions are skipped
    loudly rather than silently dropped."""
    log = _git(repo, "log", "--format=%H %ad", "--date=iso-strict", "--", path).strip()
    rows = []
    for line in reversed([l for l in log.split("\n") if l.strip()]):
        sha, date = line.split(" ", 1)
        try:
            doc = json.loads(_git(repo, "show", f"{sha}:{path}"))
            rows.append((sha[:9], date, [o["key"] for o in doc.get("objects", [])]))
        except Exception as e:  # noqa: BLE001
            print(f"  !! {path}@{sha[:9]} unreadable ({type(e).__name__}: {e}) — skipped", file=sys.stderr)
    return rows


def report(repo):
    out = []
    for path in manifest_paths(repo):
        prefix = path.split("/")[1]
        rows = history(repo, path)
        listings = []
        prev = None
        for sha, date, keys in rows:
            row = {"commit": sha, "listed_utc": date, **summarise(keys)}
            if prev is not None:
                added, removed = compare(prev, keys)
                row["added"] = len(added)
                row["removed"] = len(removed)
                row["removed_examples"] = removed[:5]
            listings.append(row)
            prev = keys
        out.append({"prefix": prefix, "manifest": path, "listings": listings})
    return out


def render(data):
    lines = ["S3 OBJECT-LOSS FORENSICS — from committed MANIFEST.json listings only ($0, no credentials)", ""]
    for p in data:
        lines.append(f"=== {p['prefix']} ({p['manifest']}) ===")
        if not p["listings"]:
            lines.append("  no readable listing in git history")
        for r in p["listings"]:
            old = r["oldest_surviving"] or "UNKNOWN (no key carries a timestamp)"
            delta = ("" if "removed" not in r
                     else f"   +{r['added']} / -{r['removed']}"
                          + (f"  e.g. {r['removed_examples'][0]}" if r["removed_examples"] else ""))
            lines.append(f"  {r['listed_utc']}  {r['commit']}  n={r['n']:6d} dated={r['dated']:6d}"
                         f"  oldest={old}{delta}")
        rem = [r.get("removed", 0) for r in p["listings"][1:]]
        if rem:
            lines.append(f"  -> keys removed between consecutive listings: {rem}. A live age-based "
                         f"expiration rule cannot show all-zero here.")
        lines.append("")
    return "\n".join(lines)


def _selftest():
    assert key_instant("a/b-20260813T003138Z.json") == "20260813T003138Z"
    assert key_instant("a/_map.json") is None
    assert compare(["a", "b"], ["b", "c"]) == (["c"], ["a"])
    s = summarise(["x-20260813T003138Z.json", "y-20260901T000000Z.json", "_map.json"])
    assert s == {"n": 3, "dated": 2, "oldest_surviving": "20260813T003138Z",
                 "newest_surviving": "20260901T000000Z"}, s
    assert summarise(["_map.json"])["oldest_surviving"] is None
    print("selftest OK")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--repo", default=os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__)))))
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    data = report(a.repo)
    print(json.dumps(data, indent=2) if a.json else render(data))
    return 0


if __name__ == "__main__":
    sys.exit(main())
