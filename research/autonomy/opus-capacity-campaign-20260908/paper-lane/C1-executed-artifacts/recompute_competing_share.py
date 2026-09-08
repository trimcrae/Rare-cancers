#!/usr/bin/env python3
"""C1 consequence check: change ONLY the competing-share input of
research/manuscripts/emc-host-factor-model.json and report every changed output.

The arithmetic is quoted verbatim from the committed generator
research/manuscripts/emc_host_factor_model.py (model_factor, lines ~198-217):

    "share_of_all_deaths": round(share, 4)
    "exposed_patient_share_of_deaths_averted_range": [round(share*rrr_lo*t_lo,4),
                                                      round(share*rrr_hi*t_hi,4)]
    "cohort_share_of_deaths_averted_range":          [round(prev*share*rrr_lo*t_lo,4),
                                                      round(prev*share*rrr_hi*t_hi,4)]
and, for compartment A, share_A = 1.0 - share.

Nothing else is altered: prevalence, relative-risk-reduction ranges, transfer
multipliers, statuses, PMIDs and the decomposition itself are held fixed.
"""
import json, pathlib, sys

MODEL = pathlib.Path(sys.argv[1])
DECOMP = pathlib.Path(sys.argv[2])

m = json.loads(MODEL.read_text())
d = json.loads(DECOMP.read_text())

cur = m["competing_share_of_deaths_used"]                      # 0.394 (within_series[0])

# NEW SHARE: taken from the STORED numerators and denominators of direct_cause_split,
# never from the paper's rounded "21.7 per cent" display.
oc = sum(r["other_cause_deaths"] for r in d["direct_cause_split"])
td = sum(r["total_deaths"] for r in d["direct_cause_split"])
n  = sum(r["n"] for r in d["direct_cause_split"])
dd = sum(r["disease_deaths"] for r in d["direct_cause_split"])
new = oc / td
print(f"stored direct_cause_split pooled: n={n} disease_deaths={dd} other_cause_deaths={oc} "
      f"total_deaths={td}  share={oc}/{td}={new!r} ({new*100:.4f} %)")
print(f"current share used by model      : {cur!r} ({cur*100:.4f} %)")
print(f"ratio new/current                : {new/cur:.6f}   current/new = {cur/new:.6f}\n")

rows = []
for f in m["factors"]:
    for comp in ("A", "B"):
        c = f["compartments"][comp]
        share_cur = 1.0 - cur if comp == "A" else cur
        share_new = 1.0 - new if comp == "A" else new
        assert abs(round(share_cur, 4) - c["share_of_all_deaths"]) < 1e-9, (f["id"], comp)
        rrr = c.get("relative_risk_reduction_range", [0.0, 0.0])
        t = c.get("transfer_multiplier_range", [1.0, 1.0])
        prev = f["prevalence_in_cohort"]
        def bands(s):
            ex = [round(s*rrr[0]*t[0], 4), round(s*rrr[1]*t[1], 4)]
            co = [round(prev*s*rrr[0]*t[0], 4), round(prev*s*rrr[1]*t[1], 4)]
            return ex, co
        ex_c, co_c = bands(share_cur)
        ex_n, co_n = bands(share_new)
        # self-consistency: the committed file must reproduce under its own formula
        if "exposed_patient_share_of_deaths_averted_range" in c:
            assert ex_c == c["exposed_patient_share_of_deaths_averted_range"], (f["id"], comp, ex_c, c)
            assert co_c == c["cohort_share_of_deaths_averted_range"], (f["id"], comp, co_c, c)
        rows.append({
            "factor": f["id"], "compartment": comp, "status": c["status"],
            "prevalence": prev, "rrr_range": rrr, "transfer_range": t,
            "share_current": round(share_cur, 4), "share_new": round(share_new, 4),
            "share_ratio": round(share_new/share_cur, 4) if share_cur else None,
            "exposed_current": ex_c, "exposed_new": ex_n,
            "cohort_current": co_c, "cohort_new": co_n,
        })

print(f"{'factor':<16}{'C':<2}{'status':<18}{'share cur':>10}{'share new':>10}"
      f"{'exposed cur':>22}{'exposed new':>22}{'cohort cur':>22}{'cohort new':>22}")
for r in rows:
    print(f"{r['factor']:<16}{r['compartment']:<2}{r['status']:<18}"
          f"{r['share_current']:>10}{r['share_new']:>10}"
          f"{str(r['exposed_current']):>22}{str(r['exposed_new']):>22}"
          f"{str(r['cohort_current']):>22}{str(r['cohort_new']):>22}")

out = {"competing_share_current": cur, "competing_share_new": new,
       "new_share_numerator_denominator": [oc, td],
       "new_share_source": "research/manuscripts/emc-mortality-decomposition.json direct_cause_split, "
                           "pooled STORED counts of both strata (masunaga2025_localized + masunaga2025_metastatic)",
       "ratio_new_over_current": new/cur, "rows": rows}
pathlib.Path(sys.argv[3]).write_text(json.dumps(out, indent=1) + "\n")
print("\nwrote", sys.argv[3])
