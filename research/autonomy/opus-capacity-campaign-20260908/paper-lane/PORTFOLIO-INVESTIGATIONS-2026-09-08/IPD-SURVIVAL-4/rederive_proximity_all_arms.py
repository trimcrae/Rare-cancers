#!/usr/bin/env python3
"""Re-derive the PROXIMITY clause of km_risk_row_detect.decide() for BOTH arms.

IPD-SURVIVAL-3's additive y0/y1 made 10 of 15 figures proximity-re-derivable. The eleventh --
morioka2016 p4, caption "Fig. 1", the TEXT arm, and the one figure in the whole census whose
recorded verdict is `present` from that arm -- was still not re-derivable, because the text arm's
proximity denominator is `page.bbox[3]` and the artifact recorded it nowhere. This script consumes
an artifact regenerated with BOTH additive changes and re-derives the clause for every figure that
has band geometry at all.

The clause, structurally as decide() writes it:

    near_enough = min(t.y0 for t in band) - max(t.y1 for t in bands[ref]) <= max_risk_gap

with, at the call sites:
    pixel, embedded image : max_risk_gap = MAX_RISK_GAP * img.height   -> recorded as image_px[1]
    pixel, raster crop    : max_risk_gap = MAX_RISK_GAP * crop.height  -> recorded as image_px[1]
    text                  : max_risk_gap = MAX_RISK_GAP * page.bbox[3] -> recorded as page_height_pt

⛔ NOTHING IS LOOSENED. Every constant is parsed out of the source file and never retyped, and the
comparison is `<=` exactly as the source writes it. This is instrument provenance: no clinical,
prognostic, efficacy or survival claim follows from any number here, and no curve was digitised.
"""
import json, re, sys

SRC = "research/modalities/km_risk_row_detect.py"
_TXT = open(SRC, encoding="utf-8").read()


def const(name):
    m = re.search(rf"^{name}\s*=\s*([0-9.]+)", _TXT, re.M)
    if m is None:
        raise SystemExit(f"constant {name} not found in {SRC}")
    return float(m.group(1))


MAX_RISK_GAP = const("MAX_RISK_GAP")
MIN_MARKS = const("MIN_MARKS")
MIN_MATCHED_TICKS = const("MIN_MATCHED_TICKS")
MAX_MARK_WIDTH = const("MAX_MARK_WIDTH")

doc = json.load(open(sys.argv[1], encoding="utf-8"))
rows, agree, disagree, notderiv = [], 0, 0, 0
for src in doc["sources"]:
    for fi, f in enumerate(src["figures"]):
        arm = f.get("arm")
        row = {"source_id": src["source_id"], "figure_index": fi, "page": f.get("page"),
               "arm": arm, "caption_head": (f.get("caption_head") or "")[:70],
               "recorded_verdict": f["verdict"], "bands": []}
        ref = f.get("tick_label_band_index")
        if arm == "text":
            H = f.get("page_height_pt")
            row["proximity_denominator"] = "page.bbox[3] -> page_height_pt"
        else:
            H = (f.get("image_px") or [None, None])[1]
            row["proximity_denominator"] = "img/crop height -> image_px[1]"
        if ref is None or not f.get("bands"):
            row.update(proximity_rederivable=False,
                       why="no band geometry recorded (undetermined before any band was measured)")
            notderiv += 1; rows.append(row); continue
        if H is None:
            row.update(proximity_rederivable=False,
                       why="the proximity denominator is not recorded in this artifact")
            notderiv += 1; rows.append(row); continue
        refband = f["bands"][ref]
        if any("y1" not in m for m in refband["marks"]):
            row.update(proximity_rederivable=False,
                       why="per-mark y0/y1 absent -- artifact predates the additive change")
            notderiv += 1; rows.append(row); continue
        thr = MAX_RISK_GAP * H
        ref_bottom = max(m["y1"] for m in refband["marks"])
        row["figure_height"] = H
        row["max_risk_gap"] = round(thr, 2)
        row["tick_label_band_bottom_y1"] = ref_bottom
        ok = True
        for b in f["bands"]:
            if b["index"] <= ref:
                continue
            top = min(m["y0"] for m in b["marks"])
            gap = top - ref_bottom
            derived = gap <= thr
            rec_ = b.get("near_enough_to_tick_labels")
            match = (rec_ == derived)
            ok &= match
            conj = (b["n_marks"] >= MIN_MARKS and b["matched_ticks"] >= MIN_MATCHED_TICKS
                    and b["median_mark_width_frac"] <= MAX_MARK_WIDTH and derived)
            row["bands"].append({
                "index": b["index"], "n_marks": b["n_marks"],
                "matched_ticks": b["matched_ticks"],
                "median_mark_width_frac": b["median_mark_width_frac"],
                "band_top_y0": top, "gap": round(gap, 2),
                "gap_as_fraction_of_height": round(gap / H, 4),
                "derived_near_enough": derived, "recorded_near_enough": rec_, "agrees": match,
                "marks_truncated_by_16_cap": b["n_marks"] > len(b["marks"]),
                "derived_qualifies_as_risk_row": conj,
                "margin_to_proximity_boundary": round(thr - gap, 2)})
        derived_present = [b["index"] for b in row["bands"] if b["derived_qualifies_as_risk_row"]]
        row["proximity_rederivable"] = True
        row["all_proximity_flags_agree"] = ok
        row["derived_risk_row_band_index"] = derived_present[0] if derived_present else None
        row["recorded_risk_row_band_index"] = f.get("risk_row_band_index")
        row["derived_verdict_from_geometry"] = "present" if derived_present else "absent"
        row["verdict_agrees"] = (row["derived_verdict_from_geometry"] == f["verdict"]
                                 or f["verdict"] == "undetermined")
        row["risk_row_band_index_agrees"] = (
            row["derived_risk_row_band_index"] == row["recorded_risk_row_band_index"])
        agree += ok
        disagree += (not ok)
        rows.append(row)

out = {"_what": ("re-derivation of the proximity clause of km_risk_row_detect.decide() for both "
                 "arms, from per-mark y0/y1 and the recorded proximity denominator"),
       "_not_medical_advice": ("Instrument provenance only. No clinical, prognostic, efficacy, "
                              "safety or survival claim. No curve digitised, no IPD reconstructed."),
       "constants_parsed_from_source": {"MAX_RISK_GAP": MAX_RISK_GAP, "MIN_MARKS": MIN_MARKS,
                                        "MIN_MATCHED_TICKS": MIN_MATCHED_TICKS,
                                        "MAX_MARK_WIDTH": MAX_MARK_WIDTH},
       "n_figures": len(rows), "n_proximity_rederivable": agree + disagree,
       "n_all_flags_agree": agree, "n_disagree": disagree, "n_not_rederivable": notderiv,
       "n_verdict_disagreements": sum(1 for r in rows
                                      if r["proximity_rederivable"] and not r["verdict_agrees"]),
       "figures": rows}
json.dump(out, sys.stdout, indent=2, ensure_ascii=False)
sys.stdout.write("\n")
sys.exit(0 if disagree == 0 else 1)
