#!/usr/bin/env python3
"""S5 summarizer: reads results.json (raw) and prints the compact per-cell tables. No computation
that presupposes sampling; every number is copied from a single fixed scenario."""
import json
d = json.load(open("results.json"))
ARMS = ["exact"] + [s for s in d["meta"]["read_scenarios"]]
for b in d["cohorts"]:
    t = b["truth"]
    print("\n### %s  sha256=%s" % (b["cohort"], b["cohort_sha256"][:16]))
    print("truth n=%d ev=%d cen=%d median=%s min=%s max=%s last_obs_is_event=%s n_at_tmax=%d"
          % (t["n_patients"], t["n_events"], t["n_censored"], t["median_survival"],
             t["min_time"], t["max_time"], t["last_observation_is_event"], t["n_at_t_max"]))
    for sname, info in b["renders"].items():
        ce = info.get("curve_error_vs_truth") or {}
        print("  render %-32s ok=%s refusal=%s maxerr=%s offstep=%s pts=%s"
              % (sname, info["ok"], info.get("refusal"), ce.get("max_abs_curve_error"),
                 ce.get("max_abs_curve_error_off_step"), info.get("n_digitized_points")))
    for axis in ("density@extent0.933", "extent@rows8"):
        print("  -- %s" % axis)
        print("     %-10s | %-6s | %s" % ("key", "arm", "evD cenD medD  maxdev adm"))
        for c in b["cells"]:
            if c["axis"] != axis:
                continue
            key = c.get("rows", c.get("extent"))
            for arm in ARMS:
                a = c["exact_arm"] if arm == "exact" else c["read_arms"][arm]
                if a.get("error"):
                    print("     %-10s | %-30s | ERROR %s" % (key, arm, a["error"]))
                    continue
                print("     %-10s | %-30s | %+4d %+5d %8s %7s %s"
                      % (key, arm, a["events_delta_vs_truth"], a["censored_delta_vs_truth"],
                         a["median_delta_vs_truth"], a["internal_max_abs_km_deviation"],
                         "OK" if a["admissible_under_the_floor"] else
                         "FAIL " + str(a["quality_failures"])))
