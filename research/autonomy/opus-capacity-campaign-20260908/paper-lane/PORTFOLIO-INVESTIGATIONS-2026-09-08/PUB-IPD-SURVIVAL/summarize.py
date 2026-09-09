"""Readout over decision-margin-real-figure.json. Pure reporting; computes nothing new."""
import json
d = json.load(open("decision-margin-real-figure.json"))
rows = sorted(d["E1_survival_offset_scan"], key=lambda r: r["survival_offset"])
bad = [r["survival_offset"] for r in rows if not r["anchored"]["admissible"]]
print("floor:", d["floor"])
for k in ("printed", "anchored"):
    b = d["baseline"][k]
    print(f"baseline {k}: n={b['n']} ev={b['events']} cen={b['censored']} dev={b['max_abs_km_deviation']} "
          f"adm={b['admissible']} median={b['median']} matches_printed_8mo={b['median_matches_printed_8mo']} "
          f"pfs6={b['pfs_rate_6mo']}")
print("E1 offsets scanned:", len(rows), "range", rows[0]["survival_offset"], rows[-1]["survival_offset"])
print("E1 anchored INADMISSIBLE offsets:", bad)
print("E1 printed branch ever admissible:", any(r["printed"]["admissible"] for r in rows),
      "| its minimum deviation over the scan:", min(r["printed"]["max_abs_km_deviation"] for r in rows))
print("E1 anchored median over ALL offsets:", sorted({r["anchored"]["median"] for r in rows}))
print("E1 anchored (events,censored) over ALL offsets:",
      sorted({(r["anchored"]["events"], r["anchored"]["censored"]) for r in rows}))
print("E1 non-monotone re-admission: offsets >= +0.019 pass the floor again with events =",
      sorted({r["anchored"]["events"] for r in rows if r["survival_offset"] >= 0.019}),
      "and offsets <= -0.025 with events =",
      sorted({r["anchored"]["events"] for r in rows if r["survival_offset"] <= -0.025}))
print("E1 summary:", json.dumps(d["E1_summary"]))
print("E2 held-out printed numbers-at-risk:")
for r in d["E2_heldout_risk_row"]:
    print(f"  t={r['held_out_time']}: printed={r['printed_n_at_risk']} predicted={r['predicted_n_at_risk']} "
          f"delta={r['delta']} adm={r['admissible']} dev={r['max_abs_km_deviation']} median={r['median']} "
          f"events={r['events']} censored={r['censored']}")
print("E2 max |delta|:", max(abs(r["delta"]) for r in d["E2_heldout_risk_row"]))
print("decision band:", json.dumps(d["decision_band"], ensure_ascii=False))
