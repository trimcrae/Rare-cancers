#!/usr/bin/env python3
"""ORPHAN-CENSUS-1: junction/modality coverage benchmark over the 198-pair
fusion-junction orphan census. Reads one local JSON; makes NO network call."""
import json, hashlib, os, statistics, sys, datetime

SRC = "/home/user/Rare-cancers/research/modalities/fusion-junction-orphan-census.json"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "junction-modality-coverage-benchmark.json")
FOCUS = "EWSR1::NR4A3"
CONTROLS = ["BCR::ABL1", "EWSR1::FLI1", "PAX3::FOXO1"]

raw = open(SRC, "rb").read()
sha = hashlib.sha256(raw).hexdigest()
d = json.loads(raw)
rows = d["rows"]
assert d["n_universe_pairs"] == len(rows) == 198, "universe size changed"

def q(r, k):
    v = r["queries"].get(k)
    return v["hit_count"] if v else None

def qstat(r, k):
    v = r["queries"].get(k)
    return None if v is None else {"http_status": v["http_status"], "error": v["error"]}

def minlen(r):
    return min(len(r["donor_gene"]), len(r["acceptor_gene"]))

def stratum(r):
    return "short_symbol_le3" if minlen(r) <= 3 else "long_symbol_ge4"

def screened(r):
    # a row is fully screened only if every query returned HTTP 200 with a count
    return all(v["hit_count"] is not None and v["http_status"] == 200
               for v in r["queries"].values())

for r in rows:
    r["_stratum"] = stratum(r)
    r["_screened"] = screened(r)
    r["_den"] = q(r, "denominator")
    r["_mod"] = q(r, "modality")
    r["_jd"] = q(r, "junction_directed")
    r["_loose"] = q(r, "denominator_loose_fulltext")

# ---- controls: must be NON-orphan, else the instrument measures retrieval ----
controls = {}
for name in CONTROLS:
    r = next((x for x in rows if x["fusion"] == name), None)
    controls[name] = None if r is None else {
        "present_in_universe": True,
        "verdict": r["verdict"],
        "non_orphan": r["verdict"] != "orphan",
        "fully_screened": r["_screened"],
        "short_symbol_le3": r["_stratum"] == "short_symbol_le3",
        "denominator": r["_den"], "modality": r["_mod"], "junction_directed": r["_jd"],
    }
controls_pass = all(c is not None and c["non_orphan"] for c in controls.values())

# ---- verdict coverage overall and by stratum ----
def counts(sub):
    c = {}
    for r in sub:
        c[r["verdict"]] = c.get(r["verdict"], 0) + 1
    return c

strata = {}
for s in ("short_symbol_le3", "long_symbol_ge4"):
    sub = [r for r in rows if r["_stratum"] == s]
    scr = [r for r in sub if r["_screened"]]
    orph = [r for r in scr if r["verdict"] == "orphan"]
    strata[s] = {
        "n_pairs": len(sub),
        "n_fully_screened": len(scr),
        "verdict_counts": counts(sub),
        "orphan_rate_among_fully_screened": (round(len(orph)/len(scr), 4) if scr else None),
        "median_denominator_hits": (statistics.median([r["_den"] for r in scr]) if scr else None),
        "median_junction_directed_hits": (statistics.median([r["_jd"] for r in scr]) if scr else None),
        "examples_of_stratum": sorted(r["fusion"] for r in sub)[:10],
    }

# ---- ranks for the focus fusion ----
focus = next(x for x in rows if x["fusion"] == FOCUS)
comparator = [r for r in rows if r["_screened"] and r["_stratum"] == "long_symbol_ge4"]

def rank_block(pool, key, label):
    vals = [(r["fusion"], r[key]) for r in pool if r[key] is not None]
    vals.sort(key=lambda t: -t[1])
    pos = next((i + 1 for i, t in enumerate(vals) if t[0] == FOCUS), None)
    return {"metric": label, "n_ranked": len(vals), "focus_value": focus[key],
            "focus_rank_desc": pos,
            "focus_percentile_from_top": (round(100.0 * pos / len(vals), 1) if pos else None),
            "median": statistics.median([v for _, v in vals]) if vals else None,
            "top5": vals[:5]}

# junction-directed share of the pair's own literature (retrieval-normalised)
for r in rows:
    r["_jd_share"] = (r["_jd"] / r["_den"]) if (r["_jd"] is not None and r["_den"]) else None

ranks_all = [rank_block(rows, k, l) for k, l in
             (("_den", "denominator_hits"), ("_mod", "modality_hits"),
              ("_jd", "junction_directed_hits"), ("_jd_share", "junction_directed_share_of_denominator"))]
ranks_cmp = [rank_block(comparator, k, l) for k, l in
             (("_den", "denominator_hits"), ("_mod", "modality_hits"),
              ("_jd", "junction_directed_hits"), ("_jd_share", "junction_directed_share_of_denominator"))]

# ---- EWSR1-family and sarcoma-translocation peers, for like-with-like ----
peers = sorted([r["fusion"] for r in rows if r["donor_gene"] == "EWSR1" or r["acceptor_gene"] == "EWSR1"])
peer_rows = [{"fusion": r["fusion"], "verdict": r["verdict"], "stratum": r["_stratum"],
              "denominator": r["_den"], "modality": r["_mod"], "junction_directed": r["_jd"],
              "junction_share": (round(r["_jd_share"], 4) if r["_jd_share"] is not None else None)}
             for r in rows if r["fusion"] in peers]

failed = [{"fusion": r["fusion"], "stratum": r["_stratum"],
           "failed_queries": {k: qstat(r, k) for k, v in r["queries"].items()
                              if v["hit_count"] is None or v["http_status"] != 200}}
          for r in rows if not r["_screened"]]

out = {
  "_id": "ORPHAN-CENSUS-1-junction-modality-coverage-benchmark",
  "_what": ("Coverage benchmark over the 198 fusion pairs already fetched in "
            "fusion-junction-orphan-census.json: where EWSR1::NR4A3 sits in the retrieved "
            "literature, with orphan status stratified by gene-symbol length."),
  "_utc_built": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
  "_no_network": "This benchmark makes no HTTP call. It re-reads rows fetched by the census on "
                 + d["_utc"] + " and recomputes over them.",
  "⚠_not_a_field_absence_claim": ("Every count is a retrieval count from ONE index (Europe PMC) on "
      "ONE date under ONE query string. A rank or a zero here CANNOT establish that the field has "
      "not done something; an unclosed literature index cannot demonstrate absence. Read every "
      "'orphan' as 'these queries retrieved nothing on that date'."),
  "⚠_no_clinical_claim": "Nothing here bears on EMC efficacy, safety, selectivity, therapeutic "
      "window or clinical readiness, and no row is a recommendation.",
  "provenance": {
    "source_file": SRC,
    "source_sha256_recomputed_at_use": sha,
    "source_bytes": len(raw),
    "source_census_utc": d["_utc"],
    "source_status": d["status"],
    "source_epmc_endpoint": d["epmc_endpoint"],
    "source_modality_terms": d["modality_terms"],
    "source_junction_terms": d["junction_terms"],
    "source_carried_no_hashes": "DISCOVERY-2 computed no hashes; the sha256 above was computed here at use.",
    "n_universe_pairs": d["n_universe_pairs"],
    "census_summary_as_published": d["summary"],
  },
  "positive_controls": {
    "requirement": "BCR::ABL1, EWSR1::FLI1 and PAX3::FOXO1 must be NON-orphan. If any reads as "
                   "orphan, the instrument is measuring retrieval, not the literature.",
    "result": "PASS" if controls_pass else "FAIL",
    "detail": controls,
  },
  "verdict_coverage": {
    "overall": counts(rows),
    "n_fully_screened": sum(1 for r in rows if r["_screened"]),
    "n_not_fully_screened": len(failed),
    "by_symbol_length_stratum": strata,
    "stratum_definition": "min(len(donor_symbol), len(acceptor_symbol)) <= 3 -> short_symbol_le3; "
                          "the census's own caveat says such symbols are English words too "
                          "(ACT, FUS, MET), so their hit counts are inflated by unrelated text.",
  },
  "focus_fusion": {
    "fusion": FOCUS,
    "verdict": focus["verdict"],
    "is_orphan_by_this_census": focus["verdict"] == "orphan",
    "stratum": focus["_stratum"],
    "fully_screened": focus["_screened"],
    "diseases": focus["diseases"],
    "existing_therapies": focus["existing_therapies"],
    "hit_counts": {"denominator_loose_fulltext": focus["_loose"], "denominator": focus["_den"],
                   "modality": focus["_mod"], "junction_directed": focus["_jd"],
                   "junction_directed_share_of_denominator": round(focus["_jd_share"], 4)},
    "rank_within_all_198": ranks_all,
    "rank_within_long_symbol_fully_screened_comparator": {
        "n_comparator_pairs": len(comparator), "ranks": ranks_cmp},
  },
  "ewsr1_family_peers": peer_rows,
  "not_fully_screened_rows": failed,
  "stop_condition": "Stops at this benchmark table. No new retrieval, no re-query, no absence claim.",
}
json.dump(out, open(OUT, "w"), indent=1, ensure_ascii=False)
print("sha256", sha)
print("controls", out["positive_controls"]["result"], json.dumps(controls))
print("strata", json.dumps(strata, indent=1))
print("focus", json.dumps(out["focus_fusion"]["hit_counts"]), focus["verdict"], focus["_stratum"])
for b in ranks_all: print("ALL198", b["metric"], b["focus_value"], "rank", b["focus_rank_desc"], "/", b["n_ranked"], "median", b["median"])
for b in ranks_cmp: print("CMP", b["metric"], b["focus_value"], "rank", b["focus_rank_desc"], "/", b["n_ranked"], "median", b["median"])
print("peers", json.dumps(peer_rows))
print("wrote", OUT, os.path.getsize(OUT))

# ---- appendix pass: the concrete records behind the focus fusion's verdict, and the
# portfolio arguments that lean on the fusion being neglected -------------------------
out = json.load(open(OUT))
out["focus_fusion"]["retrieved_identifiers_for_hand_check"] = {
  "_why": ("The census verdict 'attempted' is keyword CO-OCCURRENCE in one retrieved record, not a "
           "read confirmation that an oligonucleotide was aimed at this junction. These are the "
           "identifiers the junction-directed query returned (the census stores at most 25 per "
           "query); reading them by hand is the only way to convert a co-occurrence into a claim."),
  "junction_directed_query": focus["queries"]["junction_directed"]["query"],
  "identifiers": focus["queries"]["junction_directed"]["identifiers"],
  "modality_identifiers": focus["queries"]["modality"]["identifiers"],
}
out["portfolio_arguments_leaning_on_neglect"] = [
 {"file": "research/manuscripts/aso/aso-citations-priorart-2026-08-08.md", "line": 371,
  "quote": "EMC / EWSR1::NR4A3 has never been attempted. No junction-directed oligonucleotide "
           "against any NR4A3 fusion appears in 5,385 records. Genuinely first — an "
           "indication-level first.",
  "status_against_this_benchmark": "QUALIFIED, not refuted. This census classifies EWSR1::NR4A3 as "
   "'attempted', not 'orphan', and its junction-directed retrieval (19 records) sits ABOVE the "
   "median of the 198-pair universe and of the long-symbol comparator. That does not show an ASO "
   "was aimed at this junction — the verdict is co-occurrence — but it does mean a second, "
   "independently-fetched index does NOT return zero, so a flat 'never been attempted' rests on one "
   "sweep's negative and should carry the sweep's bound. The 19 identifiers above are the check."},
 {"file": "research/manuscripts/mtap-prmt5/emc-mtap-prmt5-hypothesis.md", "line": 87,
  "quote": "usually EWSR1::NR4A3, for which no targeted agent exists.",
  "status_against_this_benchmark": "NOT REACHED. 'No approved targeted agent' is a therapeutics-"
   "availability statement, not a literature-coverage one; this benchmark measures retrieval only. "
   "Noted because the paper's own peer review (item 36, 2026-08-10) already asked for that phrase "
   "to be bounded."},
 {"file": "research/manuscripts/dependency/emc-biomarker-selected-classes.md", "line": 46,
  "quote": "It has no targeted agent, and its systemic options are few.",
  "status_against_this_benchmark": "NOT REACHED — same reason as above."},
]
out["portfolio_scan_bound"] = ("The scan was a grep over research/manuscripts for neglect-shaped "
  "phrasings tied to the fusion or the modality; it is not an exhaustive audit of the portfolio, and "
  "'orphan nuclear receptor' / 'orphan disease' uses were excluded as a different sense of the word.")
json.dump(out, open(OUT, "w"), indent=1, ensure_ascii=False)
print("appendix written", os.path.getsize(OUT))
