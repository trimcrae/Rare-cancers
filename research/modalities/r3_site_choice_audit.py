#!/usr/bin/env python3
"""R3 site-choice audit — two questions that have been conflated, answered separately. $0 CPU.

★★ THE QUESTION trimcrae ASKED, WHICH NOBODY HAD (2026-08-03): *"Why are we using that frame when we have
tons of MD saying we can open a cryptic pocket in NR4A3?"*

`R3` closed against the program: the generation receptor `nr4a3-release-druggable.pdb` (unbiased release
replica 0, frame 95) scores **0.259** on its mapped orthosteric site against D* = 0.53. Meanwhile **44 of
75** unbiased release frames clear D* on the same mapped site under the same detector. So the frame the
whole design campaign was conditioned on is not merely a frame that failed — it is a frame that failed
while dozens of its own siblings passed.

Two questions live inside that, they call for different answers, and they have been run together:

  (A) SHOULD THE SITE BE POCKET 1 OR POCKET 2?  Two of the generation frame's 15 cavities clear the
      composite acceptance gate. `pocket_tracking.match_pocket` orders accepted candidates by
      frac_recovered → Jaccard → centroid → druggability, so pocket 1 (8/10 recovered, 0.259) wins over
      pocket 2 (6/10, 0.667) and the frame FAILS. This is a RULE CHOICE, not a measurement, and it decides
      the verdict. ⛔ The thresholds and the ordering were frozen 2026-07-11, before this datum; re-tuning
      them now is the outcome-selection defect the entire harmonized rerun exists to remove. So this
      module establishes WHAT each cavity is and what each choice would cost — it never re-tunes, and the
      answer it reports is the frozen rule's answer.

  (B) WHAT WOULD A QUALIFYING GENERATION FRAME LOOK LIKE?  Which release frames clear D* on the MAPPED
      site (not on any cavity), what the program's own selector picks from them today, and what
      re-anchoring would cost. ⛔ Nothing is re-generated here. `denovo_401`'s pose is defined against
      frame 95's coordinates, so a different receptor means RE-GENERATING, not swapping — and whether to
      do that is a program decision, not a computation.

EVERYTHING HERE IS $0 AND ALREADY ON DISK. Committed per-frame series, the committed harmonized artifacts,
and the repo's own selector (`release_frame_select`, called, never re-implemented).
"""
from __future__ import annotations

import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)

import pocket_tracking as pt          # noqa: E402  — D*, the frozen thresholds
import release_frame_select as rfs    # noqa: E402  — THE selector; called, never re-implemented

OUT = os.path.join(HERE, "r3-site-choice-audit.json")
REHARM = os.path.join(REPO, "results", "nr4a3-pocket-reharmonize")
HARMONIZED = os.path.join(HERE, "r3-generation-frame-harmonized.json")
REPFRAME = os.path.join(HERE, "r3-generation-frame-repframe.json")
ACCEPTED = os.path.join(HERE, "pocket-accepted-candidates.json")
CONTRAST = os.path.join(HERE, "paralogue-pocket-contrast.json")

# The manifest's own record of the generation frame. NOT re-derived here — it is the claim under test, and
# its one home is the S3 manifest, quoted through `r3-generation-frame-audit.json`.
AUDIT = os.path.join(HERE, "r3-generation-frame-audit.json")

TARGET_RG = 0.737          # release_frame_select's default and release-druggable-aws.yml's input default
GEN_REP, GEN_FRAME = 0, 95


# ==========================================================================================================
# pure
# ==========================================================================================================
def load_json(path):
    """Read or return None. An unreadable file is reported as `None` and the caller says so — an absent
    reading is not a reading of absence (CLAUDE.md §4)."""
    try:
        with open(path) as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return None


def series_records(summaries):
    """{rep: summary} -> the selector's record shape [{rep, frame, rg, druggability}]. PURE.

    `druggability` here is the MATCHED-SITE score, not the best cavity anywhere: the committed
    `druggability_timeseries` rows carry a `match` block, so a row's number is the cavity the harmonized
    gate accepted. That distinction is the whole of question (B) — "clears on the mapped site" is a
    different claim from "has a druggable cavity somewhere"."""
    recs = []
    for rep, summ in sorted(summaries.items()):
        ts = (summ or {}).get("druggability_timeseries") or {}
        for s in ts.get("series", []):
            if s.get("orthosteric_druggability") is None or s.get("cv_rg_nm") is None:
                continue
            recs.append({"rep": rep, "frame": int(s["frame"]), "rg": float(s["cv_rg_nm"]),
                         "druggability": float(s["orthosteric_druggability"]),
                         "match": s.get("match")})
    return recs


def qualifying(records, d_star=pt.D_STAR, target_rg=TARGET_RG):
    """Frames clearing D* ON THE MAPPED SITE, ranked by closeness to the selector's target Rg. PURE."""
    out = [dict(r, rg_offset=round(abs(r["rg"] - target_rg), 4))
           for r in records if r["druggability"] >= d_star]
    out.sort(key=lambda r: (r["rg_offset"], -r["druggability"], r["rep"], r["frame"]))
    return out


def per_replica(records, d_star=pt.D_STAR):
    """n_ge_dstar / n by replica. PURE. Counts are DERIVED from the rows, never typed."""
    out = {}
    for r in records:
        row = out.setdefault(r["rep"], {"rep": r["rep"], "n": 0, "n_ge_dstar": 0})
        row["n"] += 1
        if r["druggability"] >= d_star:
            row["n_ge_dstar"] += 1
    return [out[k] for k in sorted(out)]


def selector_choice(records, target_rg=TARGET_RG, d_star=pt.D_STAR, n_alt=3):
    """What `release_frame_select.select_receptor_ensemble` — the code that chose frame 95 — picks from a
    given pool TODAY. Called, never re-implemented, so this cannot drift from the real selector."""
    sel = rfs.select_receptor_ensemble(records, d_star=d_star, target_rg=target_rg, n_alt=n_alt)
    prim = sel.get("primary")
    return {
        "n_usable": sel.get("n_usable"), "n_druggable": sel.get("n_druggable"),
        "relaxed": sel.get("relaxed"), "d_star_used": sel.get("d_star_used"),
        "primary": None if prim is None else {k: prim[k] for k in ("rep", "frame", "rg", "druggability")},
        "alternates": [{k: a[k] for k in ("rep", "frame", "rg", "druggability")}
                       for a in sel.get("alternates", [])],
        "reason": sel.get("reason"),
    }


def identical_reading(a, b):
    """Do two harmonized scorings describe the same structure? PURE.

    ⚠ THIS IS THE OBSERVATION THAT DISCHARGES AN ARGUMENT. `r3-generation-frame-audit.json` states that a
    `release_rep*` trajectory row "is not a measurement of [the generation receptor] even at per-frame
    granularity", because the receptor is re-extracted and re-boxed and `nr4a3_release_druggable.
    confirm_filter` says the reused summary and the fresh confirmation "can disagree". That is an
    argument. Two fpocket runs — one on the S3 receptor, one on the committed rep0/frame-95 trajectory
    PDB — either agree or they do not, and the comparison is free."""
    if not a or not b:
        return {"comparable": False, "why": "one side is missing"}
    fields = ["n_candidate_pockets", "n_accepted_by_gate", "all_pocket_druggability", "matched_pocket",
              "mapped_lining_resseqs", "numbering"]
    diffs = {f: [a.get(f), b.get(f)] for f in fields if a.get(f) != b.get(f)}
    return {
        "comparable": True,
        "identical": not diffs,
        "fields_compared": fields,
        "differences": diffs,
        "verdict_a": (a.get("verdict") or {}).get("verdict"),
        "verdict_b": (b.get("verdict") or {}).get("verdict"),
        "druggability_a": (a.get("verdict") or {}).get("druggability"),
        "druggability_b": (b.get("verdict") or {}).get("druggability"),
    }


def verdict_under(druggability, d_star=pt.D_STAR):
    """GATE_A verdict for a given site druggability. PURE — the same threshold test
    `r3_score_generation_frame.classify_score` applies, restated only so both branches can be tabulated
    side by side without re-running fpocket."""
    return "GATE_A_PASS" if druggability >= d_star else "GATE_A_FAIL_BELOW_DSTAR"


def ensemble_consequence(accepted_dump, species="NR4A3"):
    """How far the ORDERING reaches beyond the generation frame. PURE.

    A rule is not a per-frame preference — the same ordering decides every frame in the committed
    ensembles. `pocket-accepted-candidates.json` records every gate-accepted cavity per frame, so the
    consequence is arithmetic. Returns None (and the caller says NOT MEASURED) when that dump is absent:
    an unmeasured consequence must never render as a small one."""
    if not accepted_dump:
        return None
    rows = [r for r in accepted_dump.get("summary", []) if r.get("species") == species]
    if not rows:
        return None
    tot = {"n_frames": 0, "n_matched": 0, "n_multi_accept": 0,
           "n_ge_dstar_frozen": 0, "n_ge_dstar_if_most_druggable": 0,
           "n_frames_where_the_two_rules_differ": 0}
    for r in rows:
        for k in tot:
            tot[k] += r.get(k, 0)
    return {"species": species, "per_ensemble": rows, "totals": tot,
            "d_star": accepted_dump.get("d_star"),
            "match_params": accepted_dump.get("match_params")}


UNBIASED = ("release_rep0", "release_rep1", "release_rep2")


def selectivity_under_each_rule(accepted_dump, subsets=UNBIASED):
    """⚠ THE CONSEQUENCE THAT REACHES BEYOND `R3`. PURE.

    Choosing which accepted cavity is "the site" is not a per-frame preference: the SAME ordering decides
    every frame of every species. The non-covalent route's premise is that the cryptic orthosteric pocket
    is itself a paralogue discriminator (`paralogue-pocket-contrast.json`), and that premise is a CONTRAST
    of these fractions. So a rule change that rescues the generation frame also moves the contrast — and
    it must be possible to see by how much BEFORE anybody chooses a rule, or the choice is made on one
    frame's verdict while silently repricing the selectivity statement.

    Pooled over the UNBIASED release replicas only (the biased metadynamics subset is excluded for the
    same reason `paralogue_pocket_contrast.contrast_summary` excludes it). Returns both rules side by
    side, never one alone."""
    if not accepted_dump:
        return None
    out = {}
    for r in accepted_dump.get("summary", []):
        if r.get("ensemble") not in subsets:
            continue
        row = out.setdefault(r["species"], {"species": r["species"], "n_frames": 0,
                                            "n_ge_dstar_frozen": 0,
                                            "n_ge_dstar_if_most_druggable": 0})
        row["n_frames"] += r.get("n_frames", 0)
        row["n_ge_dstar_frozen"] += r.get("n_ge_dstar_frozen", 0)
        row["n_ge_dstar_if_most_druggable"] += r.get("n_ge_dstar_if_most_druggable", 0)
    for row in out.values():
        n = row["n_frames"] or 1
        row["frac_frozen"] = round(row["n_ge_dstar_frozen"] / n, 4)
        row["frac_if_most_druggable"] = round(row["n_ge_dstar_if_most_druggable"] / n, 4)
    rows = [out[k] for k in sorted(out)]
    tgt = out.get("NR4A3")
    margins = None
    if tgt:
        margins = {}
        for sp, row in out.items():
            if sp == "NR4A3":
                continue
            margins[sp] = {
                "margin_frozen": round(tgt["frac_frozen"] - row["frac_frozen"], 4),
                "margin_if_most_druggable": round(
                    tgt["frac_if_most_druggable"] - row["frac_if_most_druggable"], 4),
            }
            margins[sp]["margin_change"] = round(
                margins[sp]["margin_if_most_druggable"] - margins[sp]["margin_frozen"], 4)
    return {
        "_what": ("the paralogue contrast — NR4A3's mapped-site >=D* fraction minus each paralogue's — "
                  "under the FROZEN rule and under an ordering that preferred the most druggable "
                  "accepted cavity. Pooled over the three UNBIASED release replicas."),
        "_does_not_license": ("a rule change. This is a sensitivity, computed so the cost of a choice is "
                              "visible; the frozen rule remains the rule."),
        "subsets": list(subsets),
        "rows": rows,
        "nr4a3_margin_vs_paralogue": margins,
    }


# ==========================================================================================================
# assembly
# ==========================================================================================================
def load_reharmonize_summaries(root=REHARM):
    out = {}
    for path in sorted(glob.glob(os.path.join(root, "release_rep*", "pocket_analysis_summary.json"))):
        m = re.search(r"release_rep(\d+)", path)
        if m:
            out[int(m.group(1))] = load_json(path)
    return out


def build():
    harm = load_json(HARMONIZED)
    repf = load_json(REPFRAME)
    audit = load_json(AUDIT)
    dump = load_json(ACCEPTED)
    contrast = load_json(CONTRAST)
    summaries = load_reharmonize_summaries()
    records = series_records(summaries)

    # ---- the identity chain, measured rather than argued -------------------------------------------
    ident = identical_reading(harm, repf)
    manifest_row = (audit or {}).get("primary_row") or {}
    measured_rg = (harm or {}).get("measured_cv_rg_nm")
    series_rg = next((r["rg"] for r in records if r["rep"] == GEN_REP and r["frame"] == GEN_FRAME), None)
    rg_check = {
        "manifest_selection_rg_nm": manifest_row.get("selection_rg"),
        "measured_on_the_generation_receptor_nm": measured_rg,
        "committed_rep0_frame95_series_nm": series_rg,
        "target_rg_nm": TARGET_RG,
        "selector_rule": ("release_frame_select.select_receptor_ensemble picks the druggable frame "
                          "MINIMISING |Rg - target_rg| — so Rg is the selection criterion, not a label"),
        "agrees": (measured_rg is not None and series_rg is not None
                   and abs(measured_rg - series_rg) < 1e-4),
        "manifest_matches_measurement": (
            measured_rg is not None and manifest_row.get("selection_rg") is not None
            and abs(measured_rg - float(manifest_row["selection_rg"])) < 1e-4),
        # ⚠ THE TWO READINGS THIS CANNOT YET SEPARATE, and the fields that would.
        "open_question": ("mislabelled frame vs mis-selected frame — the two call for different "
                          "responses and the rep0 legacy selection pool "
                          "(s3 nr4a3-release-pocket/pocket_analysis_summary.json) is NOT committed to "
                          "this repo, so it cannot be settled from what is on disk"),
        "manifest_candidate_source": (audit or {}).get("manifest_candidate_source"),
        "manifest_params": (audit or {}).get("manifest_params"),
        "manifest_selection": (audit or {}).get("manifest_selection"),
        "⚠_latent_hazard": ("nr4a3_release_druggable._load_summary_records labels EVERY record `rep: 0` "
                            "regardless of which trajectory's summary is mounted at POCKET_DIR, and "
                            "_extract_receptor then slices that frame index out of release_rep0.dcd. So "
                            "a summary from another replica would be selected on ITS numbers and "
                            "extracted from rep0's coordinates, silently. Reported as a code hazard; "
                            "there is no evidence here that it fired."),
    }

    # ---- (A) -----------------------------------------------------------------------------------------
    ident_by_pocket = (harm or {}).get("pocket_identity") or {}
    per_cand = {str(r["pocket"]): r for r in ((harm or {}).get("per_candidate_gate") or [])}
    accepted_nums = [n for n, r in per_cand.items() if r.get("accepted_by_gate")]
    branches = []
    for n in sorted(accepted_nums, key=lambda x: int(x)):
        pi, pc = ident_by_pocket.get(n, {}), per_cand[n]
        branches.append({
            "pocket": int(n),
            "druggability": pc.get("druggability"),
            "n_overlap": pc.get("n_overlap"), "jaccard": pc.get("jaccard"),
            "frac_recovered": pc.get("frac_recovered"),
            "centroid_dist_ang": pc.get("centroid_dist_ang"),
            "volume_a3": pi.get("volume_a3"), "alpha_spheres": pi.get("alpha_spheres"),
            "n_lining_residues": pi.get("n_lining_residues"),
            "reference_lining_shared_labels": pi.get("reference_lining_shared_labels"),
            "lining_uniprot_labels": pi.get("lining_uniprot_labels"),
            "gate_a_verdict_if_this_were_the_site": verdict_under(pc.get("druggability") or 0.0),
        })
    chosen = (harm or {}).get("matched_pocket") or {}

    question_a = {
        "_question": ("Should the mapped orthosteric site in the generation receptor be pocket 1 or "
                      "pocket 2? Both clear the frozen composite gate."),
        "_this_is_a_rule_choice_not_a_measurement": True,
        "frozen_rule": {
            "ordering": "frac_recovered -> jaccard -> nearer centroid -> druggability (deterministic tiebreak only)",
            "source": "pocket_tracking.match_pocket",
            "thresholds": (harm or {}).get("match_params"),
            "frozen_on": "2026-07-11",
            "⛔": ("re-tuning these after seeing the verdict is the outcome-selection defect the "
                   "harmonized rerun exists to remove; this module never does it"),
        },
        "reference_lining_labels": (harm or {}).get("reference_lining_labels"),
        "reference_centroid": (harm or {}).get("reference_centroid"),
        "accepted_cavities": branches,
        "chosen_by_the_frozen_rule": {"pocket": chosen.get("pocket"),
                                      "druggability": chosen.get("druggability")},
        "contrast": (harm or {}).get("site_choice_contrast"),
        "ensemble_consequence": ensemble_consequence(dump),
        "selectivity_consequence": selectivity_under_each_rule(dump),
        "ensemble_consequence_status": ("MEASURED" if dump else
                                        "NOT MEASURED — pocket-accepted-candidates.json absent; "
                                        "run r3-generation-frame-audit.yml with dump_accepted=true ($0)"),
    }

    # ---- (B) -----------------------------------------------------------------------------------------
    quals = qualifying(records)
    rep0_only = [r for r in records if r["rep"] == GEN_REP]
    question_b = {
        "_question": ("Which release frames clear D* ON THE MAPPED SITE, what does the program's own "
                      "selector pick from them today, and what would re-anchoring cost?"),
        "d_star": pt.D_STAR,
        "denominator_note": ("every count below is on the MATCHED site — the committed "
                             "druggability_timeseries rows carry their own `match` block, so a row's "
                             "number is the cavity the harmonized gate accepted, not the best cavity "
                             "anywhere in the structure"),
        "n_frames_scored": len(records),
        "n_qualifying": len(quals),
        "per_replica": per_replica(records),
        "qualifying_frames": quals,
        "selector_rerun": {
            "_what": ("release_frame_select.select_receptor_ensemble — the SAME function that chose "
                      "frame 95 — run over today's harmonized per-frame series"),
            "rep0_only_the_original_pool_shape": selector_choice(rep0_only),
            "all_three_release_replicas": selector_choice(records),
            "⚠": ("the original selection pool was rep0 ONLY (nr4a3_release_druggable._load_summary_"
                  "records hardcodes rep: 0 and reads ONE summary), so the rep0 row is the like-for-like "
                  "comparison and the pooled row is what a wider pool would offer"),
        },
        "generation_frame_row": next((r for r in records
                                      if r["rep"] == GEN_REP and r["frame"] == GEN_FRAME), None),
    }

    rec = {
        "_what": ("R3 site-choice audit — (A) which cavity is the site, and (B) what a qualifying "
                  "generation frame would be. Two questions that had been conflated."),
        "_prompted_by": ("trimcrae, 2026-08-03: \"Why are we using that frame when we have tons of MD "
                         "saying we can open a cryptic pocket in NR4A3?\""),
        "_cost": "$0 — committed artifacts + free CI. No GPU, no rental, nothing to tear down.",
        "_does_not_license": [
            "any change to pocket_tracking's thresholds or ordering (frozen 2026-07-11)",
            "re-generating denovo_401 against any other receptor — that is a program decision",
            "any claim about binding, affinity, reactivity, degradation, efficacy or safety",
            "reading a detection fraction as an opening free energy",
        ],
        "generation_frame": {"rep": GEN_REP, "frame": GEN_FRAME,
                             "pdb": manifest_row.get("pdb"),
                             "manifest_confirmed_druggability_LEGACY": manifest_row.get(
                                 "confirmed_druggability"),
                             "harmonized_site_druggability": (harm or {}).get("verdict", {}).get(
                                 "druggability")},
        "identity_cross_check": ident,
        "cv_rg_check": rg_check,
        "question_A_which_cavity_is_the_site": question_a,
        "question_B_what_a_qualifying_frame_would_be": question_b,
        "corroboration": {
            "paralogue_pocket_contrast_independent_rescore": _contrast_row(contrast),
            "_why": ("an INDEPENDENT harmonized re-score of the same committed frames, run in one "
                     "process under one fpocket build — so agreement is a reproduction, not a quote"),
        },
    }
    return rec


def _contrast_row(contrast, rep=GEN_REP, frame=GEN_FRAME):
    if not contrast:
        return None
    want = f"NR4A3/release_rep{rep}/fp_{frame}_"
    for r in contrast.get("per_frame", []):
        if r.get("frame", "").startswith(want):
            return r
    return None


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    out = OUT
    for i, a in enumerate(argv):
        if a == "--out" and i + 1 < len(argv):
            out = argv[i + 1]
    rec = build()
    with open(out, "w") as fh:
        json.dump(rec, fh, indent=2)

    a, b = rec["question_A_which_cavity_is_the_site"], rec["question_B_what_a_qualifying_frame_would_be"]
    print("=" * 100)
    print("IDENTITY  : re-extracted receptor vs committed rep0/frame-95 —",
          "IDENTICAL harmonized reading" if rec["identity_cross_check"].get("identical")
          else f"DIFFER: {rec['identity_cross_check'].get('differences')}")
    rg = rec["cv_rg_check"]
    print(f"CV Rg     : manifest {rg['manifest_selection_rg_nm']} nm vs MEASURED "
          f"{rg['measured_on_the_generation_receptor_nm']} nm "
          f"(series {rg['committed_rep0_frame95_series_nm']}); target {rg['target_rg_nm']} — "
          f"manifest matches measurement: {rg['manifest_matches_measurement']}")
    print("-" * 100)
    print("(A) ACCEPTED CAVITIES — the frozen rule chose pocket",
          a["chosen_by_the_frozen_rule"]["pocket"])
    for c in a["accepted_cavities"]:
        print(f"    pocket {c['pocket']}: drug={c['druggability']} recovered={c['frac_recovered']} "
              f"jaccard={c['jaccard']} centroid={c['centroid_dist_ang']} A vol={c['volume_a3']} A^3 "
              f"-> {c['gate_a_verdict_if_this_were_the_site']}")
        print(f"       shares with the reference site: {c['reference_lining_shared_labels']}")
    for p in ((a.get("contrast") or {}).get("pairs") or []):
        print(f"    PAIR {p['pockets']}: {p['n_shared']} shared residues, jaccard {p['pairwise_jaccard']}, "
              f"centroids {p['centroid_separation_ang']} A apart -> {p['relationship']}")
    print(f"    ensemble consequence: {a['ensemble_consequence_status']}")
    sc = a.get("selectivity_consequence")
    if sc:
        print("    ⚠ THE ORDERING DECIDES EVERY FRAME, NOT JUST THIS ONE — unbiased release, both rules:")
        for r in sc["rows"]:
            print(f"       {r['species']}: {r['n_ge_dstar_frozen']}/{r['n_frames']} "
                  f"({r['frac_frozen']}) frozen  vs  {r['n_ge_dstar_if_most_druggable']}/{r['n_frames']} "
                  f"({r['frac_if_most_druggable']}) if the most-druggable accepted cavity won")
        for sp, m in (sc.get("nr4a3_margin_vs_paralogue") or {}).items():
            print(f"       NR4A3 - {sp} margin: {m['margin_frozen']} frozen -> "
                  f"{m['margin_if_most_druggable']} ({m['margin_change']:+})")
    print("-" * 100)
    print(f"(B) {b['n_qualifying']} of {b['n_frames_scored']} release frames clear D* = {b['d_star']} "
          f"ON THE MAPPED SITE")
    for r in b["per_replica"]:
        print(f"    rep{r['rep']}: {r['n_ge_dstar']}/{r['n']}")
    sel0 = b["selector_rerun"]["rep0_only_the_original_pool_shape"]
    selA = b["selector_rerun"]["all_three_release_replicas"]
    print(f"    the SAME selector over rep0 today picks: {sel0['primary']}")
    print(f"    over all three replicas it picks       : {selA['primary']}")
    print(f"    the generation frame's own row         : {b['generation_frame_row']}")
    print("=" * 100)
    print(f"[r3-site-choice] wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
