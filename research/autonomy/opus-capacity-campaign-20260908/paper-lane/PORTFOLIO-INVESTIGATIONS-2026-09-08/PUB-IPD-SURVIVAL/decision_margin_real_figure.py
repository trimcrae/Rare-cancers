"""Decision-level reconstruction uncertainty on the ONE REAL EMC figure, with held-out
external ground truth. No synthetic render is produced or read anywhere in this file.

Inputs (read-only, committed):
  research/modalities/km-figure-readings.json   -- the real reading of stacchiotti2013 Fig. 2
  research/modalities/emc_ipd_survival.py       -- reconstruct(), assess_quality(), kaplan_meier()

E1  MARGIN SENSITIVITY. The decision-relevant output (median PFS) is 5.0 or 8.0 months depending
    on ONE discrete reporting ambiguity (printed vs anchored first numbers-at-risk row). The only
    automatic discriminator is max_abs_km_deviation against MAX_KM_DEVIATION. Apply a systematic
    additive offset to the read survival values and find the offset at which the discrimination
    flips.
E2  HELD-OUT EXTERNAL VALIDATION. Withhold one printed numbers-at-risk row, reconstruct without
    it, then predict that row from the reconstructed cohort and compare with the number the paper
    printed. The comparison value is real published data the reconstruction never saw.
"""
import json, os, sys, importlib.util

REPO = "/home/user/Rare-cancers"
MOD = os.path.join(REPO, "research", "modalities")
spec = importlib.util.spec_from_file_location("emc_ipd_survival", os.path.join(MOD, "emc_ipd_survival.py"))
E = importlib.util.module_from_spec(spec); spec.loader.exec_module(E)

doc = json.load(open(os.path.join(MOD, "km-figure-readings.json")))
recipe = doc["recipes"][0]; reading = doc["readings"][0]
DIG = [[float(t), float(s)] for t, s in reading["digitized"]]
TABLES = {"printed": recipe["risk_table_printed"], "anchored": recipe["risk_table_anchored"]}
EXT = recipe["external_check"]          # printed median PFS 8.0 months, tolerance 0.5

def curve(dig, table, cid):
    return {"id": cid, "source_id": reading["source_id"], "endpoint": reading["endpoint"],
            "population": recipe["population"], "time_unit": recipe["time_unit"],
            "digitized": dig, "risk_table": table, "total_events": None,
            "digitized_by": recipe["digitized_by"]}

def km_at(km, t):
    return E.survival_at(km, t)

def grade(dig, table, cid):
    c = curve(dig, table, cid)
    try:
        rec = E.reconstruct(c); err = None
    except Exception as exc:                      # preserved, never swallowed
        rec, err = None, str(exc)
    q = E.assess_quality(c, rec, err)
    out = {"id": cid, "error": err, "admissible": q["admissible"], "failures": q["failures"],
           "max_abs_km_deviation": q["max_abs_km_deviation"]}
    if rec:
        km = E.kaplan_meier(rec["ipd"])
        med = E._median_survival(km)
        out.update({"n": rec["n_reconstructed"], "events": rec["n_events"],
                    "censored": rec["n_censored"], "median": med,
                    "median_matches_printed_8mo": (med is not None and abs(med - EXT["printed_value"]) <= EXT["tolerance"]),
                    "pfs_rate_6mo": km_at(km, 6.0), "pfs_rate_3mo": km_at(km, 3.0),
                    "risk_table_overridden": rec["risk_table_overridden"],
                    "ipd": rec["ipd"]})
    return out

def offset(dig, d):
    """Systematic additive offset on the READ survival values; clipped to [0,1], monotonicity
    restored the same way the digitizer's own contract requires (non-increasing S)."""
    out, prev = [], 1.0
    for t, s in dig:
        v = min(1.0, max(0.0, s + d))
        v = min(v, prev); prev = v
        out.append([t, v])
    return out

RES = {"_what": "Decision-level reconstruction uncertainty on the real stacchiotti2013 Fig. 2 "
                "reading, and held-out validation against printed numbers-at-risk.",
       "_not_medical_advice": "Nothing here is medical advice and nothing asserts efficacy, "
                              "safety or clinical readiness. Every number is a re-expression of "
                              "an already-published figure.",
       "_source": {"image": reading["image"], "figure": reading["figure"],
                   "source_id": reading["source_id"], "external_check": EXT},
       "floor": {"MAX_KM_DEVIATION": E.MAX_KM_DEVIATION}}

# --- baseline -------------------------------------------------------------------------
RES["baseline"] = {k: grade(DIG, TABLES[k], f"base::{k}") for k in TABLES}

# --- E1 margin sensitivity ------------------------------------------------------------
deltas = sorted(set([round(x * 0.0005, 4) for x in range(-60, 61)] + [0.0016, -0.0016, 0.0035, -0.0035]))
e1 = []
for d in deltas:
    row = {"survival_offset": d}
    for k in TABLES:
        g = grade(offset(DIG, d), TABLES[k], f"off{d}::{k}")
        row[k] = {kk: g[kk] for kk in ("admissible", "max_abs_km_deviation", "median",
                                       "median_matches_printed_8mo", "n", "events", "censored")
                  if kk in g}
        row[k]["error"] = g["error"]
    e1.append(row)
RES["E1_survival_offset_scan"] = e1

def first_flip(key, pred):
    for r in sorted(e1, key=lambda r: abs(r["survival_offset"])):
        if pred(r[key]):
            return r["survival_offset"]
    return None
RES["E1_summary"] = {
    "measured_reading_error_envelope": {
        "pixel_uncertainty_survival_shift": reading["diagnostics"]["axis"]["systematic_survival_shift_bound"],
        "worst_measured_off_step_error_synthetic_control": 0.0035},
    "smallest_offset_at_which_anchored_becomes_INADMISSIBLE": first_flip("anchored", lambda g: not g["admissible"]),
    "smallest_offset_at_which_printed_becomes_ADMISSIBLE": first_flip("printed", lambda g: g["admissible"]),
    "smallest_offset_at_which_anchored_median_leaves_8mo_window": first_flip(
        "anchored", lambda g: not g.get("median_matches_printed_8mo")),
}

# --- E2 held-out numbers-at-risk validation -------------------------------------------
anch = [list(r) for r in TABLES["anchored"]]
e2 = []
for i in range(1, len(anch)):                      # row 0 is the anchor the recursion starts from
    held_t, held_n = anch[i]
    reduced = [r for j, r in enumerate(anch) if j != i]
    g = grade(DIG, reduced, f"holdout_t{held_t}")
    pred = None
    if g.get("ipd") is not None:
        pred = sum(1 for p in g["ipd"] if p["time"] >= held_t - 1e-9)
    e2.append({"held_out_time": held_t, "printed_n_at_risk": held_n,
               "predicted_n_at_risk": pred,
               "delta": (None if pred is None else pred - held_n),
               "admissible": g["admissible"], "failures": g["failures"],
               "max_abs_km_deviation": g["max_abs_km_deviation"],
               "median": g.get("median"), "pfs_rate_6mo": g.get("pfs_rate_6mo"),
               "n": g.get("n"), "events": g.get("events"), "censored": g.get("censored"),
               "error": g["error"]})
RES["E2_heldout_risk_row"] = e2

meds = [r["median"] for r in e2 if r["median"] is not None] + [RES["baseline"]["anchored"]["median"]]
p6 = [r["pfs_rate_6mo"] for r in e2 if r.get("pfs_rate_6mo") is not None] + [RES["baseline"]["anchored"]["pfs_rate_6mo"]]
RES["decision_band"] = {
    "median_pfs_months_across_admissible_and_heldout_variants": [min(meds), max(meds)],
    "median_pfs_months_including_the_printed_table_branch": [
        min(meds + [RES["baseline"]["printed"]["median"]]), max(meds + [RES["baseline"]["printed"]["median"]])],
    "pfs_rate_6mo_range": [min(p6), max(p6)],
    "⚠": "A range over variants of one reading of one figure of one 11-patient series. It is not "
         "a confidence interval and it is not a cohort statistic.",
}
json.dump(RES, sys.stdout, indent=1, ensure_ascii=False)
