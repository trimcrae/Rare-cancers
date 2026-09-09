"""Re-derive PUB-IPD-SURVIVAL's headline reporting census from preserved band geometry alone.

⛔ Nothing here is medical advice, and nothing here asserts efficacy, safety, selectivity or
clinical readiness. This file measures whether a recorded MEASUREMENT follows from its own recorded
intermediates. It says nothing about any patient, any survival estimate or any therapy.

WHY. PUB-IPD-SURVIVAL's claim is a negative about reporting practice: of the reachable EMC series,
most Kaplan-Meier figures print no numbers-at-risk row, so most curves cannot be reconstructed at
all. Every one of those verdicts comes from one run of research/modalities/km_risk_row_detect.py on
PDFs that are NOT COMMITTED (licence), read from a cache branch, keyed by sha256. At this HEAD those
inputs do not resolve, so the run cannot be repeated. What CAN be checked -- and never has been --
is that each recorded verdict actually FOLLOWS from the band geometry the artifact preserved, under
the decision rule and constants the artifact also records. That converts an unrepeatable measurement
into a falsifiable one, at zero new inputs.

WHAT THIS IS NOT. This does not re-read any PDF, does not re-detect any band, and cannot detect a
figure that was mis-segmented, mis-thresholded or never seen. It bounds transcription and rule
application, not perception.
"""
import json, os, re, sys

REPO = "/home/user/Rare-cancers"
DET = os.path.join(REPO, "research", "modalities", "km-risk-row-detection.json")
SRC = os.path.join(REPO, "research", "modalities", "km_risk_row_detect.py")
IPD = os.path.join(REPO, "research", "modalities", "emc_ipd_survival.py")

art = json.load(open(DET))
src = open(SRC).read()

# --- constants taken from the SOURCE, not retyped -----------------------------------------
def const(name):
    m = re.search(rf"^{name}\s*=\s*([0-9.]+)", src, re.M)
    if not m:
        raise SystemExit(f"constant {name} not found in {SRC}")
    return float(m.group(1))

K = {n: const(n) for n in ("MIN_MARKS", "MIN_MATCHED_TICKS", "TICK_TOL", "MAX_MARK_WIDTH",
                           "MIN_GLYPH_WIDTH", "MAX_TICK_GAP", "MAX_RISK_GAP")}
MIN_MARKS = int(K["MIN_MARKS"]); MIN_MATCHED = int(K["MIN_MATCHED_TICKS"])
TICK_TOL, MAX_W, MIN_GLYPH = K["TICK_TOL"], K["MAX_MARK_WIDTH"], K["MIN_GLYPH_WIDTH"]

# the constants the artifact ADVERTISES, checked against the constants the code HOLDS
adv = art["method"]["constants"]
const_drift = {k: {"artifact": v, "source": const(k)} for k, v in adv.items() if float(v) != const(k)}

def width_of(fig):
    """The rule's width scale. pixel arm: the axis span in px (decide(..., max(1, ax1-ax0))).
    text arm: the tick-row span in pt. Both are recorded."""
    if fig["arm"] == "pixel":
        a = fig.get("axis_span_px")
        return (max(1, a[1] - a[0]), "axis_span_px")
    return (fig.get("tick_row_span_pt"), "tick_row_span_pt")

def med(xs):
    xs = sorted(xs)
    return xs[len(xs) // 2]

rows, mismatches, notes = [], [], []
for s in art["sources"]:
    for fig in s["figures"]:
        rec_verdict = fig["verdict"]
        bands = fig.get("bands", [])
        r = {"source_id": s["source_id"], "page": fig.get("page"), "arm": fig["arm"],
             "input": fig.get("source", "embedded_image"),
             "caption_head": (fig.get("caption_head") or "")[:90],
             "recorded_verdict": rec_verdict, "n_bands": len(bands)}
        if not bands:
            # decide() returns BEFORE appending any band on all three early-exit paths, so a row
            # with no bands carries no geometry to re-derive. Recorded as not-re-derivable.
            r.update({"re_derived_verdict": None, "agrees": None,
                      "why_not_re_derivable": "no band geometry preserved (early-exit path: "
                                              "undecodable encoding, too few tokens, no glyph band, "
                                              "or tick-gap refusal)"})
            rows.append(r); continue
        width, wsrc = width_of(fig)
        if not width:
            r.update({"re_derived_verdict": None, "agrees": None,
                      "why_not_re_derivable": "width scale not recorded for this arm"})
            rows.append(r); continue
        r["width_scale"] = width; r["width_scale_from"] = wsrc

        # 1. recompute each band's median mark width fraction from its marks
        wfrac = {b["index"]: med([m["w"] for m in b["marks"]]) / width for b in bands}
        for b in bands:
            if abs(round(wfrac[b["index"]], 4) - b["median_mark_width_frac"]) > 1e-4:
                mismatches.append({"figure": f"{s['source_id']} p{fig.get('page')}",
                                   "quantity": f"band[{b['index']}].median_mark_width_frac",
                                   "recorded": b["median_mark_width_frac"],
                                   "re_derived": round(wfrac[b["index"]], 4)})
        # 2. recompute the tick-label reference band
        ref = next((b["index"] for b in bands
                    if b["n_marks"] >= MIN_MARKS and wfrac[b["index"]] >= MIN_GLYPH), None)
        r["re_derived_tick_label_band_index"] = ref
        r["recorded_tick_label_band_index"] = fig.get("tick_label_band_index")
        if ref != fig.get("tick_label_band_index"):
            mismatches.append({"figure": f"{s['source_id']} p{fig.get('page')}",
                               "quantity": "tick_label_band_index",
                               "recorded": fig.get("tick_label_band_index"), "re_derived": ref})
        if ref is None:
            r.update({"re_derived_verdict": "undetermined",
                      "agrees": rec_verdict == "undetermined"}); rows.append(r); continue
        tick_x = [m["cx"] for m in next(b for b in bands if b["index"] == ref)["marks"]]

        # 3. recompute tick alignment for every band
        matched = {}
        for b in bands:
            matched[b["index"]] = sum(1 for m in b["marks"]
                                      if any(abs(m["cx"] - tx) <= TICK_TOL * width for tx in tick_x))
            if matched[b["index"]] != b["matched_ticks"]:
                mismatches.append({"figure": f"{s['source_id']} p{fig.get('page')}",
                                   "quantity": f"band[{b['index']}].matched_ticks",
                                   "recorded": b["matched_ticks"],
                                   "re_derived": matched[b["index"]]})
        # 4. apply the rule
        verdict, hit, hit_matched = "absent", None, 0
        cand = []
        for b in bands:
            i = b["index"]
            if i <= ref:
                continue
            near = b.get("near_enough_to_tick_labels", True)
            clauses = {"n_marks>=%d" % MIN_MARKS: b["n_marks"] >= MIN_MARKS,
                       "matched>=%d" % MIN_MATCHED: matched[i] >= MIN_MATCHED,
                       "med_width<=%.3f" % MAX_W: wfrac[i] <= MAX_W,
                       "near_enough(RECORDED, not re-derived)": bool(near)}
            ok = all(clauses.values())
            cand.append({"band": i, "n_marks": b["n_marks"], "matched_ticks": matched[i],
                         "median_mark_width_frac": round(wfrac[i], 4),
                         "near_enough_recorded": near, "qualifies": ok,
                         "failed_clauses": [k for k, v in clauses.items() if not v],
                         "marks_short_by": max(0, MIN_MARKS - b["n_marks"]),
                         "matched_short_by": max(0, MIN_MATCHED - matched[i]),
                         "width_over_by": round(max(0.0, wfrac[i] - MAX_W), 4)})
            if ok and hit is None:
                verdict, hit, hit_matched = "present", i, matched[i]
        if verdict == "absent" and fig.get("label_phrase_found"):
            verdict = "undetermined"
        r["candidate_bands"] = cand
        r["re_derived_verdict"] = verdict
        r["re_derived_risk_row_band_index"] = hit
        r["recorded_risk_row_band_index"] = fig.get("risk_row_band_index")
        r["re_derived_matched_ticks"] = hit_matched
        r["recorded_matched_ticks"] = fig.get("matched_ticks")
        r["agrees"] = (verdict == rec_verdict)
        if not r["agrees"]:
            mismatches.append({"figure": f"{s['source_id']} p{fig.get('page')}",
                               "quantity": "verdict", "recorded": rec_verdict,
                               "re_derived": verdict})
        if hit != fig.get("risk_row_band_index"):
            mismatches.append({"figure": f"{s['source_id']} p{fig.get('page')}",
                               "quantity": "risk_row_band_index",
                               "recorded": fig.get("risk_row_band_index"), "re_derived": hit})
        if hit_matched != fig.get("matched_ticks"):
            mismatches.append({"figure": f"{s['source_id']} p{fig.get('page')}",
                               "quantity": "matched_ticks (figure level)",
                               "recorded": fig.get("matched_ticks"), "re_derived": hit_matched})
        # 5. how close is this negative to flipping?
        if verdict == "absent":
            best = min(cand, key=lambda c: (c["marks_short_by"] + c["matched_short_by"]
                                            + (1 if c["width_over_by"] > 0 else 0)), default=None)
            r["closest_candidate_to_qualifying"] = best
        rows.append(r)

# --- totals ---------------------------------------------------------------------------------
def count(v):
    return sum(1 for r in rows if r["recorded_verdict"] == v)
tot = {"papers": len(art["sources"]), "figures": len(rows),
       "with_risk_row": count("present"), "without": count("absent"),
       "undetermined": count("undetermined")}
for k, v in art["_totals"].items():
    if tot.get(k) != v:
        mismatches.append({"figure": "_totals", "quantity": k, "recorded": v, "re_derived": tot.get(k)})
for s in art["sources"]:
    n = {"n_figures": len(s["figures"]),
         "n_with_risk_row": sum(1 for f in s["figures"] if f["verdict"] == "present"),
         "n_without": sum(1 for f in s["figures"] if f["verdict"] == "absent"),
         "n_undetermined": sum(1 for f in s["figures"] if f["verdict"] == "undetermined")}
    for k, v in n.items():
        if s.get(k) != v:
            mismatches.append({"figure": s["source_id"], "quantity": k, "recorded": s.get(k),
                               "re_derived": v})

# --- the one printed risk row whose VALUES were recovered, vs the eye reading ---------------
ipd_src = open(IPD).read()
m = re.search(r'"trabectedin"\s*:\s*(\[\[.*?\]\])', ipd_src, re.S)
eye = json.loads(m.group(1)) if m else None
txt = None
for s in art["sources"]:
    for f in s["figures"]:
        if f.get("risk_row_text"):
            txt = {"source_id": s["source_id"], "page": f["page"],
                   "risk_row_text": f["risk_row_text"], "tick_row_text": f["tick_row_text"]}
value_check = {"eye_reading_in_emc_ipd_survival_py": eye, "instrument_text_arm": txt}
if eye and txt:
    nums = [t for t in txt["risk_row_text"] if re.fullmatch(r"\d+", t)]
    ticks = [t for t in txt["tick_row_text"] if re.fullmatch(r"\d+", t)]
    pairs = [[int(a), int(b)] for a, b in zip(ticks, nums)]
    value_check["instrument_pairs"] = pairs
    value_check["identical_to_eye_reading"] = (pairs[:len(eye)] == eye)
    value_check["⚠"] = ("The instrument recovers one more timepoint than the eye reading "
                        "transcribed." if len(pairs) > len(eye) else "")
    if pairs[:len(eye)] != eye:
        mismatches.append({"figure": "morioka2016trabectedin p4", "quantity": "risk row VALUES",
                           "recorded": eye, "re_derived": pairs[:len(eye)]})

# --- provenance ceiling: do the recorded inputs resolve at this HEAD? ----------------------
import subprocess
def sh(cmd):
    p = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=REPO)
    return {"cmd": cmd, "exit": p.returncode, "out": p.stdout.strip()[:400],
            "err": p.stderr.strip()[:400]}
inp = art["inputs"]
prov = {"recorded_inputs": inp,
        "cache_commit_in_local_object_store": sh(f"git cat-file -t {inp['cache_commit']}"),
        "cache_branch_ref_present": sh(f"git rev-parse --verify {inp['cache_branch']}"),
        "any_pdf_committed": sh("git ls-files | grep -c -i '\\.pdf$' || true")}
prov["verdict"] = ("INPUTS_RESOLVE" if prov["cache_commit_in_local_object_store"]["exit"] == 0
                   else "INPUTS_DO_NOT_RESOLVE_AT_THIS_HEAD")
prov["consequence"] = ("The five recorded pdf_sha256 digests cannot be matched against any file "
                       "reachable from this checkout, so the ORIGINAL RUN is not repeatable here. "
                       "That is exactly why the band-geometry re-derivation above is the only "
                       "falsifiability this artifact currently has, and it is a re-derivation of "
                       "RULE APPLICATION, not of perception.")

OUT = {"_what": "Re-derivation of the PUB-IPD-SURVIVAL reporting census from the band geometry "
                "km-risk-row-detection.json preserved, under the constants km_risk_row_detect.py "
                "holds. No PDF was read; no figure was re-detected; no network call was made.",
       "_not_medical_advice": "Nothing here is medical advice and nothing asserts efficacy, "
                              "safety, selectivity or clinical readiness.",
       "_inputs": {"artifact": "research/modalities/km-risk-row-detection.json",
                   "rule_source": "research/modalities/km_risk_row_detect.py",
                   "value_cross_check": "research/modalities/emc_ipd_survival.py"},
       "constants_read_from_source": K,
       "constants_advertised_vs_source_drift": const_drift,
       "totals_re_derived": tot, "totals_recorded": art["_totals"],
       "figures": rows,
       "risk_row_value_cross_check": value_check,
       "input_provenance_at_this_HEAD": prov,
       "mismatches": mismatches}
n_red = sum(1 for r in rows if r["re_derived_verdict"] is not None)
n_agree = sum(1 for r in rows if r.get("agrees") is True)
OUT["summary"] = {
    "figures_total": len(rows),
    "figures_with_preserved_geometry": n_red,
    "figures_re_derived_verdict_agrees": n_agree,
    "figures_not_re_derivable": len(rows) - n_red,
    "mismatch_count": len(mismatches),
    "verdict": ("EVERY PRESERVED VERDICT FOLLOWS FROM ITS OWN PRESERVED GEOMETRY"
                if not mismatches and n_agree == n_red
                else f"{len(mismatches)} DISCREPANCY(IES) -- see 'mismatches'"),
}
json.dump(OUT, sys.stdout, indent=1, ensure_ascii=False)
print()
