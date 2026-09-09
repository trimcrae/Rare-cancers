"""Independent re-derivation of the numbers PUB-IPD-SURVIVAL (first round) reported.

Nothing here is medical advice and nothing asserts efficacy, safety, selectivity or clinical
readiness. Every number is a re-expression of one already-published figure.

The Guyot inversion itself is the repository artifact under test, so it is imported. Everything
DOWNSTREAM of it -- the product-limit estimate, the median, S(6), and the predicted number at risk
-- is recomputed here from the returned patient-level rows with local code that does not call
emc_ipd_survival.kaplan_meier, survival_at or _median_survival. Where the two disagree the
disagreement is the finding.
"""
import json, os, importlib.util, sys

REPO = "/home/user/Rare-cancers"
MOD = os.path.join(REPO, "research", "modalities")
spec = importlib.util.spec_from_file_location("emc_ipd_survival", os.path.join(MOD, "emc_ipd_survival.py"))
E = importlib.util.module_from_spec(spec); spec.loader.exec_module(E)

doc = json.load(open(os.path.join(MOD, "km-figure-readings.json")))
recipe, reading = doc["recipes"][0], doc["readings"][0]
DIG = [[float(t), float(s)] for t, s in reading["digitized"]]

def mk(dig, table, cid):
    return {"id": cid, "source_id": reading["source_id"], "endpoint": reading["endpoint"],
            "population": recipe["population"], "time_unit": recipe["time_unit"],
            "digitized": dig, "risk_table": table, "total_events": None,
            "digitized_by": recipe["digitized_by"]}

# --- local, independent product-limit estimator -------------------------------------------
def km_local(ipd):
    """Return [(t, S)] steps. Standard KM: at each distinct event time, S *= 1 - d/n_at_risk."""
    rows = sorted((float(p["time"]), int(p["event"])) for p in ipd)
    n = len(rows); S = 1.0; steps = []
    i = 0
    while i < len(rows):
        t = rows[i][0]
        j = i
        d = c = 0
        while j < len(rows) and rows[j][0] == t:
            d += rows[j][1]; c += 1 - rows[j][1]; j += 1
        at_risk = n - i
        if d:
            S *= 1.0 - d / at_risk
            steps.append((t, S))
        i = j
    return steps

def S_at_local(steps, t):
    s = 1.0
    for tt, ss in steps:
        if tt <= t + 1e-12:
            s = ss
    return s

def median_local(steps):
    for tt, ss in steps:
        if ss <= 0.5 + 1e-12:
            return tt
    return None

def n_at_risk_local(ipd, t):
    return sum(1 for p in ipd if float(p["time"]) >= t - 1e-9)

def grade(dig, table, cid):
    c = mk(dig, table, cid)
    try:
        rec = E.reconstruct(c); err = None
    except Exception as exc:
        rec, err = None, str(exc)
    q = E.assess_quality(c, rec, err)
    out = {"id": cid, "error": err, "admissible": q["admissible"],
           "max_abs_km_deviation": q["max_abs_km_deviation"], "failures": q["failures"]}
    if rec:
        st = km_local(rec["ipd"])
        out.update({"n": rec["n_reconstructed"], "events": rec["n_events"],
                    "censored": rec["n_censored"],
                    "median_LOCAL": median_local(st), "S6_LOCAL": S_at_local(st, 6.0),
                    "median_MODULE": E._median_survival(E.kaplan_meier(rec["ipd"])),
                    "S6_MODULE": E.survival_at(E.kaplan_meier(rec["ipd"]), 6.0),
                    "ipd": rec["ipd"]})
    return out

REPORTED = {  # digit for digit, as written in PUB-IPD-SURVIVAL/FINDING.md and its summarize.py stdout
    "printed":  {"n": 10, "events": 9, "censored": 1, "dev": 0.0903, "adm": False,
                 "median": 4.987643, "S6": 0.5},
    "anchored": {"n": 11, "events": 9, "censored": 2, "dev": 0.0454, "adm": True,
                 "median": 7.984996, "S6": 0.511364},
    "E2": [{"t": 4, "printed": 7, "pred": 7, "delta": 0,  "dev": 0.0454, "median": 7.984996, "events": 9, "censored": 2},
           {"t": 6, "printed": 5, "pred": 4, "delta": -1, "dev": 0.0454, "median": 7.984996, "events": 9, "censored": 2},
           {"t": 8, "printed": 1, "pred": 2, "delta": 1,  "dev": 0.0324, "median": 7.984996, "events": 10, "censored": 1},
           {"t": 10, "printed": 0, "pred": 0, "delta": 0, "dev": 0.0454, "median": 7.984996, "events": 9, "censored": 2}],
    "E1": {"smallest_inadmissible_offset": 0.005, "printed_ever_admissible": False,
           "printed_min_dev_over_scan": 0.0604, "medians_over_all_offsets": [7.984996],
           "events_censored_over_all_offsets": [[8, 3], [9, 2], [10, 1]], "n_offsets": 123},
}

OUT = {"_what": "Independent re-derivation of every load-bearing number the first-round "
                "PUB-IPD-SURVIVAL lane reported, from the committed reading and the committed "
                "reconstruction module.",
       "_not_medical_advice": "Nothing here is medical advice and nothing asserts efficacy, "
                              "safety, selectivity or clinical readiness.",
       "_inputs": {"reading": "research/modalities/km-figure-readings.json",
                   "module": "research/modalities/emc_ipd_survival.py",
                   "MAX_KM_DEVIATION": E.MAX_KM_DEVIATION},
       "mismatches": []}

def cmp(label, got, want, tol=0.0):
    ok = (abs(got - want) <= tol) if isinstance(got, (int, float)) and isinstance(want, (int, float)) and not isinstance(got, bool) else (got == want)
    if not ok:
        OUT["mismatches"].append({"quantity": label, "reported": want, "re_derived": got})
    return ok

# --- baselines ---------------------------------------------------------------------------
base = {}
for k, tab in (("printed", recipe["risk_table_printed"]), ("anchored", recipe["risk_table_anchored"])):
    g = grade(DIG, tab, "rederive::" + k); r = REPORTED[k]
    base[k] = {"re_derived": {x: g.get(x) for x in ("n", "events", "censored", "admissible",
                                                    "max_abs_km_deviation", "median_LOCAL",
                                                    "median_MODULE", "S6_LOCAL", "S6_MODULE")},
               "reported": r}
    cmp(f"{k}.n", g["n"], r["n"]); cmp(f"{k}.events", g["events"], r["events"])
    cmp(f"{k}.censored", g["censored"], r["censored"])
    cmp(f"{k}.admissible", g["admissible"], r["adm"])
    cmp(f"{k}.max_abs_km_deviation", round(g["max_abs_km_deviation"], 4), r["dev"], 0)
    cmp(f"{k}.median(local estimator)", round(g["median_LOCAL"], 6), r["median"], 0)
    cmp(f"{k}.S6(local estimator)", round(g["S6_LOCAL"], 6), r["S6"], 1e-6)
    cmp(f"{k}.median(local vs module)", round(g["median_LOCAL"], 6), round(g["median_MODULE"], 6), 0)
OUT["baseline"] = base

# --- E2 hold-outs ------------------------------------------------------------------------
anch = [list(r) for r in recipe["risk_table_anchored"]]
e2 = []
for i in range(1, len(anch)):
    t, n_printed = anch[i]
    reduced = [r for j, r in enumerate(anch) if j != i]
    g = grade(DIG, reduced, f"rederive::holdout_t{t}")
    pred = n_at_risk_local(g["ipd"], t) if g.get("ipd") else None
    row = {"held_out_time": t, "printed_n_at_risk": n_printed, "predicted_n_at_risk": pred,
           "delta": None if pred is None else pred - n_printed,
           "max_abs_km_deviation": round(g["max_abs_km_deviation"], 4),
           "median_LOCAL": round(g["median_LOCAL"], 6) if g.get("median_LOCAL") else None,
           "events": g.get("events"), "censored": g.get("censored"),
           "admissible": g["admissible"]}
    e2.append(row)
    w = next(x for x in REPORTED["E2"] if x["t"] == t)
    cmp(f"E2[t={t}].predicted_n_at_risk", pred, w["pred"])
    cmp(f"E2[t={t}].delta", row["delta"], w["delta"])
    cmp(f"E2[t={t}].max_abs_km_deviation", row["max_abs_km_deviation"], w["dev"], 0)
    cmp(f"E2[t={t}].median", row["median_LOCAL"], w["median"], 0)
    cmp(f"E2[t={t}].events", row["events"], w["events"])
    cmp(f"E2[t={t}].censored", row["censored"], w["censored"])
OUT["E2_heldout"] = e2

# --- E1 scan (same grid, independently regenerated) ---------------------------------------
def offset(dig, d):
    out, prev = [], 1.0
    for t, s in dig:
        v = min(1.0, max(0.0, s + d)); v = min(v, prev); prev = v
        out.append([t, v])
    return out

deltas = sorted(set([round(x * 0.0005, 4) for x in range(-60, 61)] + [0.0016, -0.0016, 0.0035, -0.0035]))
anch_meds, anch_ec, inadm, printed_devs, printed_adm = set(), set(), [], [], []
for d in deltas:
    ga = grade(offset(DIG, d), recipe["risk_table_anchored"], f"off{d}::a")
    gp = grade(offset(DIG, d), recipe["risk_table_printed"], f"off{d}::p")
    if ga.get("median_LOCAL") is not None:
        anch_meds.add(round(ga["median_LOCAL"], 6)); anch_ec.add((ga["events"], ga["censored"]))
    if not ga["admissible"]:
        inadm.append(d)
    printed_devs.append(gp["max_abs_km_deviation"]); printed_adm.append(gp["admissible"])
e1 = {"n_offsets": len(deltas),
      "anchored_medians_over_all_offsets": sorted(anch_meds),
      "anchored_events_censored_over_all_offsets": sorted(anch_ec),
      "smallest_positive_offset_inadmissible": min([d for d in inadm if d > 0], default=None),
      "printed_ever_admissible": any(printed_adm),
      "printed_min_dev_over_scan": round(min(printed_devs), 4)}
OUT["E1_scan"] = e1
w = REPORTED["E1"]
cmp("E1.n_offsets", e1["n_offsets"], w["n_offsets"])
cmp("E1.smallest_inadmissible_offset", e1["smallest_positive_offset_inadmissible"], w["smallest_inadmissible_offset"], 0)
cmp("E1.printed_ever_admissible", e1["printed_ever_admissible"], w["printed_ever_admissible"])
cmp("E1.printed_min_dev_over_scan", e1["printed_min_dev_over_scan"], w["printed_min_dev_over_scan"], 0)
cmp("E1.anchored_medians_over_all_offsets", e1["anchored_medians_over_all_offsets"], w["medians_over_all_offsets"])
cmp("E1.anchored_events_censored", [list(x) for x in e1["anchored_events_censored_over_all_offsets"]], w["events_censored_over_all_offsets"])

OUT["verdict"] = ("ALL REPORTED NUMBERS REPRODUCE" if not OUT["mismatches"]
                  else f"{len(OUT['mismatches'])} MISMATCH(ES) -- see 'mismatches'")
json.dump(OUT, sys.stdout, indent=1, ensure_ascii=False)
print()
