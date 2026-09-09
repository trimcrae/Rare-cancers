#!/usr/bin/env python3
"""Adversarial single-paper reclassification sensitivity on the collapsed case-report vs
all-other-genres contrast. For every one of the 162 papers in turn, flip that paper's genre
assignment (case <-> non-case), recompute the exact stratified test, and report the range.
This answers 'what would ONE misclassification do?' directly, rather than only in the
aggregate simulation. Uses the frozen classifier and the same two instruments; no re-tuning.
"""
import json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from genre_stratified_rates import (PROBE, EMC_TITLE, INSTRUMENTS, exact_stratified)  # noqa: E402
from genre_classifier import classify  # noqa: E402

OUT = pathlib.Path(__file__).with_name("reclassification-sensitivity.json")


def tables(rows, rx, flip=None):
    t = {True: [0, 0, 0, 0], False: [0, 0, 0, 0]}
    for r in rows:
        g = r["case"] if r["pmid"] != flip else not r["case"]
        for s in r["sentences"]:
            f = bool(rx.search(s))
            if r["emc"]:
                t[g][0 if f else 1] += 1
            else:
                t[g][2 if f else 3] += 1
    return [tuple(t[True]), tuple(t[False])]


def main():
    papers = json.loads(PROBE.read_text())["terminal_events"]
    rows = [{"pmid": p.get("pmid"), "title": p.get("title"),
             "emc": bool(EMC_TITLE.search(p.get("title") or "")),
             "case": classify(p.get("title"), p.get("journal"))[0] == "case_report_or_series",
             "sentences": [s["sentence"] for s in p["sentences"]]} for p in papers]
    out = {"_what_this_is": __doc__.strip(), "instruments": {}}
    for name, rx in INSTRUMENTS.items():
        base = exact_stratified(tables(rows, rx))
        per = []
        for r in rows:
            res = exact_stratified(tables(rows, rx, flip=r["pmid"]))
            per.append({"pmid": r["pmid"], "flipped_to": "non_case" if r["case"] else "case",
                        "p_two_sided": res["p_two_sided_point_prob"],
                        "mh_or": res["mantel_haenszel_odds_ratio"], "title": r["title"][:80]})
        ps = sorted(x["p_two_sided"] for x in per)
        movers = sorted(per, key=lambda x: x["p_two_sided"])[:5]
        out["instruments"][name] = {
            "baseline": base,
            "p_two_sided_min_over_single_flips": ps[0],
            "p_two_sided_max_over_single_flips": ps[-1],
            "n_flips_that_reach_p_below_0.05": sum(1 for p in ps if p < 0.05),
            "five_largest_movers_downward": movers,
            "all_flips": per,
        }
        print(f"== {name}")
        print("  baseline p_two_sided:", base["p_two_sided_point_prob"], " MH OR:", base["mantel_haenszel_odds_ratio"])
        print(f"  single-flip range of p: [{ps[0]}, {ps[-1]}]  flips reaching p<0.05: {sum(1 for p in ps if p < 0.05)}")
        for m in movers[:3]:
            print("   ", m["pmid"], m["flipped_to"], m["p_two_sided"], m["title"])
    OUT.write_text(json.dumps(out, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
