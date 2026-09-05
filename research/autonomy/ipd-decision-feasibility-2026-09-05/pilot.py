"""Synthetic exact-curve compression experiment; no patient or efficacy data.

Run: python pilot.py. Standard library only. All times are arbitrary units.
The comparator is an oracle-count midpoint reconstruction, not IPDfromKM.
"""
import itertools
import json
import math
import random
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ALPHA = 0.05
SEED = 20260905
RISK_TIMES = [0.0, 5.0, 10.0, 15.0, 20.0]


def km(rows):
    s = Fraction(1)
    out = []
    for t in sorted({t for t, e in rows if e}):
        y = sum(x >= t for x, e in rows)
        d = sum(x == t and e for x, e in rows)
        s *= Fraction(y - d, y)
        out.append((t, str(s)))
    return out


def risks(rows, times=RISK_TIMES):
    return [sum(x >= t for x, e in rows) for t in times]


def logrank(a, b):
    u = v = 0.0
    for t in sorted({x for x, e in a + b if e}):
        ya = sum(x >= t for x, e in a)
        yb = sum(x >= t for x, e in b)
        da = sum(x == t and e for x, e in a)
        db = sum(x == t and e for x, e in b)
        y, d = ya + yb, da + db
        u += da - d * ya / y
        if y > 1:
            v += ya * yb * d * (y - d) / (y * y * (y - 1))
    z = u / math.sqrt(v) if v else 0.0
    return {"u": u, "variance": v, "z": z, "p": math.erfc(abs(z) / math.sqrt(2))}


def rmst(rows, tau=20.0):
    last, s, area = 0.0, 1.0, 0.0
    for t, sf in km(rows):
        if t > tau:
            break
        area += (t - last) * s
        last, s = t, float(Fraction(sf))
    return area + (tau - last) * s


def publish(rows):
    return {"n": len(rows), "total_events": sum(e for x,e in rows),
            "km": km(rows), "risk_times": RISK_TIMES, "risks": risks(rows), "tau":20.0}


def identified_intervals(summary):
    """Recover interval counts from published summaries alone, never hidden IPD."""
    assert summary["total_events"] == len(summary["km"]), "Pilot requires one event per drop"
    known = dict(zip(summary["risk_times"], summary["risks"]))
    previous = Fraction(1)
    events = []
    for t, survival in summary["km"]:
        current = Fraction(survival)
        y = 1 / (1 - current / previous)
        assert y.denominator == 1
        if t in known:
            assert known[t] == int(y)
        known[t] = int(y)
        events.append(t)
        previous = current
    cuts = sorted(known)
    intervals = []
    for left, right in zip(cuts,cuts[1:]):
        nc = known[left] - int(left in events) - known[right]
        assert nc >= 0
        intervals.append((left,right,nc))
    assert sum(c for lo,hi,c in intervals) + len(events) == summary["n"]
    return events, intervals


def schedules(summary_a, summary_b):
    """Enumerate censor-order equivalence classes, conditional on exact summaries.

    Total events equals number of distinct positive drops, hence one event/drop.
    Exact drop ratios identify each own-event risk set. Thus censors in each
    own-event/risk-table interval are fixed. Other-arm event times split these
    intervals into all classes relevant to an ordinary logrank statistic.
    Censors at event times have the same risk contribution as just after them.
    """
    events, intervals = identified_intervals(summary_a)
    assert summary_b["n"] == summary_b["total_events"] == len(summary_b["km"])
    options = []
    for left, right, nc in intervals:
        if not nc:
            continue
        inner = sorted(x for x, s in summary_b["km"] if left < x < right)
        bins = [left] + inner + [right]
        reps = [(lo + hi) / 2 for lo, hi in zip(bins, bins[1:])]
        options.append(list(itertools.combinations_with_replacement(reps, nc)))
    fixed = [(x, 1) for x in events]
    for pieces in itertools.product(*options):
        yield fixed + [(x, 0) for piece in pieces for x in piece]


def midpoint_reconstruction(summary):
    events, intervals = identified_intervals(summary)
    out = [(x, 1) for x in events]
    for lo, hi, nc in intervals:
        out.extend([((lo + hi) / 2, 0)] * nc)
    return out


def run():
    rng = random.Random(SEED)
    attempted = []
    selected = None
    # Deliberate counterexample search, not a representative Monte Carlo sample.
    for case in range(1000):
        a = [(rng.uniform(0.05, 19.95), 1) for _ in range(16)]
        a += [(rng.uniform(0.05, 19.95), 0) for _ in range(4)]
        b = [(rng.uniform(0.05, 15.0), 1) for _ in range(20)]
        summary_a, summary_b = publish(a), publish(b)
        candidates = list(schedules(summary_a, summary_b))
        scores = [logrank(rows, b) for rows in candidates]
        imin = min(range(len(scores)), key=lambda i: scores[i]["p"])
        imax = max(range(len(scores)), key=lambda i: scores[i]["p"])
        pmin, pmax = scores[imin]["p"], scores[imax]["p"]
        for rows in candidates:
            assert km(rows) == km(a)
            assert risks(rows) == risks(a)
            assert len(rows) == len(a)
            assert sum(e for x, e in rows) == 16
        attempted.append({"case": case, "classes": len(scores), "p_min": pmin, "p_max": pmax})
        if pmin < ALPHA <= pmax:
            mid = midpoint_reconstruction(summary_a)
            assert km(mid) == km(a) and risks(mid) == risks(a)
            selected = {"case": case, "n_per_arm": 20, "events_a": 16, "events_b": 20,
                        "true_a": sorted(a), "true_b": sorted(b), "km_a": km(a), "km_b": km(b),
                        "published_a":summary_a, "published_b":summary_b,
                        "risk_times": RISK_TIMES, "risk_a": risks(a), "risk_b": risks(b),
                        "classes": len(scores), "p_min": pmin, "p_max": pmax,
                        "minimum_p_witness_a": sorted(candidates[imin]),
                        "maximum_p_witness_a": sorted(candidates[imax]),
                        "true_logrank": logrank(a,b), "midpoint_logrank": logrank(mid,b),
                        "midpoint_a": sorted(mid),
                        "rmst_a": rmst(a), "rmst_b": rmst(b),
                        "max_rmst_discrepancy": max(abs(rmst(rows)-rmst(a)) for rows in candidates),
                        "all_scores": scores}
            # Which single added risk-table reading resolves the original decision?
            reveal = []
            query_options = []
            for t, e in sorted(b):
                observed = risks(a, [t])[0]
                keep = [s for rows,s in zip(candidates,scores) if risks(rows,[t])[0] == observed]
                lo, hi = min(s["p"] for s in keep), max(s["p"] for s in keep)
                reveal.append({"time":t,"observed_risk_a":observed,"remaining_classes":len(keep),
                               "p_min":lo,"p_max":hi,"stable":hi < ALPHA or lo >= ALPHA})
                outcomes = []
                for y in sorted({risks(rows,[t])[0] for rows in candidates}):
                    subset = [s for rows,s in zip(candidates,scores) if risks(rows,[t])[0] == y]
                    lower, upper = min(s["p"] for s in subset),max(s["p"] for s in subset)
                    outcomes.append({"risk":y,"classes":len(subset),"p_min":lower,"p_max":upper,
                                     "ambiguous":lower < ALPHA <= upper})
                query_options.append({"time":t,"outcomes":outcomes,
                    "worst_ambiguous_classes":max(o["classes"] if o["ambiguous"] else 0 for o in outcomes),
                    "worst_p_width":max(o["p_max"]-o["p_min"] for o in outcomes)})
            selected["single_risk_revelations"] = reveal
            # Deterministic minimax policy uses feasible summaries, no true answer.
            selected["query_options"] = query_options
            selected["selected_query"] = min(query_options,key=lambda q:(q["worst_ambiguous_classes"],q["worst_p_width"],q["time"]))
            break
    result = {"synthetic":True,"seed":SEED,"alpha":ALPHA,"time_unit":"arbitrary",
              "purpose":"counterexample and exact information-revelation feasibility, not prevalence or type-I error",
              "attempted":attempted,"selected":selected}
    (ROOT / "pilot-results.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"attempted":len(attempted),"selected_case":selected and selected["case"],
                      "classes":selected and selected["classes"],"p_min":selected and selected["p_min"],
                      "p_max":selected and selected["p_max"],
                      "single_reading_resolves":selected and sum(r["stable"] for r in selected["single_risk_revelations"])}))


if __name__ == "__main__":
    run()
