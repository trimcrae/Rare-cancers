"""Independent numerical and global-enumeration checks for the synthetic pilot.

Requires scipy. Uses no production enumeration function for its global check.
"""
import hashlib
import itertools
import json
import math
import platform
import sys
from pathlib import Path

from scipy import __version__ as scipy_version
from scipy.stats import CensoredData, logrank
import pilot

ROOT = Path(__file__).resolve().parent


def cd(rows):
    return CensoredData(uncensored=[t for t,e in rows if e],right=[t for t,e in rows if not e])


def main():
    result = json.loads((ROOT / "pilot-results.json").read_text())
    s = result["selected"]
    a, b = s["true_a"], s["true_b"]
    candidates = list(pilot.schedules(s["published_a"],s["published_b"]))
    discrepancies = []
    for rows in candidates + [a,s["midpoint_a"]]:
        actual = logrank(cd(rows),cd(b))
        own = pilot.logrank(rows,b)
        discrepancies.append(abs(float(actual.pvalue)-own["p"]))
        assert math.isclose(actual.pvalue,own["p"],abs_tol=1e-12)
        assert math.isclose(actual.statistic,own["z"],abs_tol=1e-12)
    # Enumerate every 4-censor multiset on the global order grid, then filter by
    # published constraints. This deliberately does not use identified_intervals.
    event_a = [t for t,e in a if e]
    cuts = sorted(set([0.0,20.0] + event_a + [t for t,e in b if e] + s["risk_times"]))
    reps = [(lo+hi)/2 for lo,hi in zip(cuts,cuts[1:])]
    fixed = [(t,1) for t in event_a]
    expected_risks = dict(zip(s["risk_times"],s["risk_a"]))
    # Obtain own-event risk counts directly from Fraction step ratios, independently.
    prev = pilot.Fraction(1)
    for t, sf in s["km_a"]:
        now = pilot.Fraction(sf)
        expected_risks[t] = int(1/(1-now/prev))
        prev = now
    grid_visited = 0
    accepted = []
    for censors in itertools.combinations_with_replacement(reps,4):
        grid_visited += 1
        if any(sum(x >= t for x in event_a)+sum(x >= t for x in censors) != y
               for t,y in expected_risks.items()):
            continue
        rows = fixed+[(t,0) for t in censors]
        assert pilot.km(rows) == [tuple(x) for x in s["km_a"]]
        accepted.append(rows)
    # Global grid subdivides also intervals with no events relevant to logrank;
    # compare unique risk signatures at all pooled event times, rather than times.
    pooled_times = sorted(set(event_a+[t for t,e in b if e]))
    sig = lambda rows: tuple(pilot.risks(rows,pooled_times))
    assert {sig(rows) for rows in accepted} == {sig(rows) for rows in candidates}
    ps = [float(logrank(cd(rows),cd(b)).pvalue) for rows in accepted]
    assert math.isclose(min(ps),s["p_min"],abs_tol=1e-12)
    assert math.isclose(max(ps),s["p_max"],abs_tol=1e-12)
    assert min(ps) <= s["true_logrank"]["p"] <= max(ps)+1e-12
    query = s["selected_query"]
    for outcome in query["outcomes"]:
        subgroup = [p for rows,p in zip(accepted,ps)
                    if pilot.risks(rows,[query["time"]])[0] == outcome["risk"]]
        assert len(subgroup) == outcome["classes"]
        assert math.isclose(min(subgroup),outcome["p_min"],abs_tol=1e-12)
        assert math.isclose(max(subgroup),outcome["p_max"],abs_tol=1e-12)
        assert max(subgroup) < result["alpha"] or min(subgroup) >= result["alpha"]
    # Reproduction must be byte-identical.
    before = (ROOT / "pilot-results.json").read_bytes()
    pilot.run()
    assert before == (ROOT / "pilot-results.json").read_bytes()
    checks = {"passed":True,"python":platform.python_version(),"scipy":scipy_version,
              "max_scipy_p_discrepancy":max(discrepancies),"global_multisets_tested":grid_visited,
              "accepted_global_multisets":len(accepted),"distinct_logrank_risk_signatures":len({sig(r) for r in accepted}),
              "enumeration_agrees":True,"reproduction_byte_identical":True,
              "query_resolves_every_feasible_answer":True,
              "results_sha256":hashlib.sha256(before).hexdigest(),
              "scope":"independent SciPy score check and alternate brute force enumeration; not independent scientific review"}
    (ROOT/"validation.json").write_text(json.dumps(checks,indent=2)+"\n")
    print(json.dumps(checks))


if __name__ == "__main__":
    main()
