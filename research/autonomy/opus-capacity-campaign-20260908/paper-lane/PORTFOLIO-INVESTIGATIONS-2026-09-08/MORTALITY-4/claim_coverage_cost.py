#!/usr/bin/env python3
"""What regenerating research/manuscripts/claim-coverage.json would cost after BOTH diffs.

This does NOT regenerate the artifact, does not run `--write`, and does not touch the STALE_HEADER
guard or any test. It imports `claim_coverage` read-only and replays its own census logic
(`sentences`, `_pin_patterns`, `_test_patterns`, `is_selective`) against a patched copy of the
manuscript held OUTSIDE the repository, so the resulting numbers are the census's own, not a
re-implementation.

Control first: the same replay against the LIVE manuscript must reproduce the committed
182 / 54, or the method is not measuring what the census measures.
"""
import io, json, os, pathlib, re, subprocess, sys, tempfile

REPO = pathlib.Path("/home/user/Rare-cancers")
REL = "research/manuscripts/emc-mortality-mechanisms-paper.md"
BASE = os.path.basename(REL)
LANE = pathlib.Path(__file__).resolve().parent
D3 = LANE.parent / "MORTALITY-3/section-4.2-composition-effect.diff"
D6 = LANE / "section-6-conclusion-scope.diff"

sys.path.insert(0, str(REPO / "research/manuscripts"))
import claim_coverage as cc  # noqa: E402


def census_rows(path):
    """cc.census() with the document read from `path` instead of PAPERS[key]. Same functions."""
    sents = cc.sentences(path)
    pats = [(h, p, w) for h, p, w in cc._pin_patterns() if h == BASE] + cc._test_patterns(BASE)
    compiled = [(re.compile(p, re.I), w) for _h, p, w in pats if cc.is_selective(p, sents)]
    rows = []
    for s in sents:
        hits = sorted({w for rx, w in compiled if rx.search(s)})
        rows.append({"has_number": bool(re.search(r"\d", s)), "covered": bool(hits)})
    return rows


def summarise(rows):
    num = [r for r in rows if r["has_number"]]
    return {"sentences": len(rows), "covered": sum(r["covered"] for r in rows),
            "with_a_number": len(num), "with_a_number_covered": sum(r["covered"] for r in num),
            "uncovered": sum(not r["covered"] for r in rows),
            "uncovered_with_a_number": sum(not r["covered"] for r in num)}


def main():
    committed = json.loads((REPO / "research/manuscripts/claim-coverage.json").read_text())["papers"][REL]
    live = summarise(census_rows(str(REPO / REL)))
    print("committed in claim-coverage.json :", json.dumps(committed))
    print("replay against LIVE manuscript   :", json.dumps(live))
    if live != committed:
        print("CONTROL FAILED: the replay does not reproduce the committed row", file=sys.stderr)
        return 1
    print("CONTROL OK: the replay reproduces the committed row exactly\n")

    with tempfile.TemporaryDirectory() as td:
        work = pathlib.Path(td) / "research/manuscripts"
        work.mkdir(parents=True)
        (pathlib.Path(td) / ".git").mkdir()
        subprocess.run(["git", "init", "-q"], cwd=td, check=True)
        (work / BASE).write_text((REPO / REL).read_text())
        for d in (D3, D6):
            r = subprocess.run(["git", "apply", str(d)], cwd=td)
            print(f"apply {d.name}: exit {r.returncode}")
            if r.returncode != 0:
                return 1
        after = summarise(census_rows(str(work / BASE)))
    print("\nafter BOTH diffs                 :", json.dumps(after))
    print("\ndelta:")
    for k in committed:
        print(f"  {k}: {committed[k]} -> {after[k]}  ({after[k]-committed[k]:+d})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
