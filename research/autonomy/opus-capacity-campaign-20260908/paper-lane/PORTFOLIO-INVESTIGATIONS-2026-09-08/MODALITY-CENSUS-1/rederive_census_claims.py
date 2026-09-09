#!/usr/bin/env python3
"""MODALITY-CENSUS-1 — claim re-derivation ledger for PUB-MODALITY-CENSUS.

One row per quantitative claim printed in
research/manuscripts/modality-census/cancer-modality-census.md, re-derived from the four
artifacts the manuscript's own section 7 names as its sources (plus one artifact section 3
cites transitively for the DepMap fractions).

Verdicts: REPRODUCES | MISMATCH | NOT-RE-DERIVABLE-LOCALLY.
A MISMATCH is REPORTED, never repaired. Nothing outside this lane directory is written.

Two known-answer controls bracket the harness: CTRL-POS must REPRODUCE and CTRL-NEG must
MISMATCH. If either control comes out the other way the harness is broken and the exit code
is 3 regardless of the real rows.
"""
import hashlib
import json
import os
import subprocess
import sys
from collections import Counter

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "..", ".."))
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "claim-rederivation-ledger.json")

SOURCES = {
    "manuscript": "research/manuscripts/modality-census/cancer-modality-census.md",
    "modalities": "systems/graph/modalities.json",
    "novelty_audit": "research/modalities/census-novelty-audit.json",
    "grading": "research/modalities/census-route-expression-grading.json",
    "panels": "research/modalities/emc-expression-panels.json",
    "depmap": "research/modalities/depmap-sarcoma-dependency.json",
}


def sha256(rel):
    with open(os.path.join(ROOT, rel), "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def load(rel):
    with open(os.path.join(ROOT, rel), encoding="utf-8") as fh:
        return json.load(fh)


ROWS = []


def row(cid, section, claim, quoted, artifact, key, rederived, level, note="",
        force=None, missing_input=None):
    if force is not None:
        verdict = force
    else:
        verdict = "REPRODUCES" if quoted == rederived else "MISMATCH"
    r = {
        "claim_id": cid,
        "manuscript_section": section,
        "claim": claim,
        "quoted_value": quoted,
        "source_artifact": artifact,
        "source_key": key,
        "rederived_value": rederived,
        "verdict": verdict,
        "derivation_level": level,
    }
    if note:
        r["note"] = note
    if missing_input:
        r["exact_missing_input"] = missing_input
    ROWS.append(r)
    return r


def pct(n, d):
    """Manuscript's stated rule: never-searched / classes, rounded to nearest whole percent."""
    return int(round(100.0 * n / d))


def main():
    mods = load(SOURCES["modalities"])
    audit = load(SOURCES["novelty_audit"])
    grading = load(SOURCES["grading"])
    panels = load(SOURCES["panels"])
    depmap = load(SOURCES["depmap"])

    A_MOD = "systems/graph/modalities.json"
    A_AUD = "research/modalities/census-novelty-audit.json"
    A_GRD = "research/modalities/census-route-expression-grading.json"
    A_PAN = "research/modalities/emc-expression-panels.json"
    A_DEP = "research/modalities/depmap-sarcoma-dependency.json"

    # ---------------- known-answer controls -------------------------------
    row("CTRL-POS", "harness control", "control: row count of the registry equals itself",
        217, A_MOD, "len(modalities.json)", len(mods),
        "READ-BACK (control)", "Known-answer positive control. Must be REPRODUCES.")
    row("CTRL-NEG", "harness control",
        "control: a deliberately wrong quoted value (218) against the same re-derivation",
        218, A_MOD, "len(modalities.json)", len(mods),
        "READ-BACK (control)",
        "Known-answer negative control. Must be MISMATCH, otherwise the comparator is broken.")

    # ---------------- section 2 headline ----------------------------------
    verdicts = Counter(r["verdict"] for r in mods)
    bands = Counter(r["band"] for r in mods)
    groups = {r["group"] for r in mods}
    ns = [r for r in mods if r.get("prior_coverage") == "never_searched"]
    ns_by_verdict = Counter(r["verdict"] for r in ns)
    ns_by_band = Counter(r["band"] for r in ns)

    row("S2-TOTAL", "2", "217 modality classes", 217, A_MOD, "len(rows)", len(mods),
        "READ-BACK (row count)")
    row("S2-GROUPS", "2", "19 groups", 19, A_MOD, "len(set(row.group))", len(groups),
        "RECOMPUTED (distinct group values)")
    row("S2-BANDS", "2", "4 bands", 4, A_MOD, "len(set(row.band))", len(bands),
        "RECOMPUTED (distinct band values)")

    verdict_table = [
        ("on_board", 42, 1), ("in_clinical_use", 8, 0), ("already_rejected", 33, 0),
        ("excluded", 95, 86), ("candidate", 20, 6), ("parked_capability", 9, 8),
        ("not_applicable", 10, 10),
    ]
    for v, q_classes, q_ns in verdict_table:
        row("S2-VT-%s" % v.upper().replace("_", "-"), "2 (verdict table)",
            "verdict %s: classes / of which never searched here" % v,
            {"classes": q_classes, "never_searched": q_ns},
            A_MOD, "count(row.verdict==%r) and its prior_coverage=='never_searched' subset" % v,
            {"classes": verdicts[v], "never_searched": ns_by_verdict[v]},
            "RECOMPUTED (grouped count over the registry)")

    row("S2-HEADLINE-111", "2",
        "111 of 217 classes had never been pointed at by any prior sweep here",
        {"never_searched": 111, "total": 217}, A_MOD,
        "count(prior_coverage=='never_searched') / len(rows)",
        {"never_searched": len(ns), "total": len(mods)},
        "RECOMPUTED (grouped count)")
    live_ns = sum(1 for r in ns if r["verdict"] in ("candidate", "parked_capability"))
    row("S2-HEADLINE-14-LIVE", "2", "and 14 of those are live",
        14, A_MOD,
        "count(prior_coverage=='never_searched' and verdict in {candidate, parked_capability})",
        live_ns, "RECOMPUTED (grouped count)",
        "'live' is not a stored field. Re-derived on the reading that the live verdicts are "
        "candidate + parked_capability, which is the only reading that reproduces the value and "
        "is consistent with the verdict table's own 6+8 split.")

    band_table = [("drug_mechanism", 162, 86, 53), ("delivery_and_conjugate", 26, 18, 69),
                  ("physical_locoregional", 15, 3, 20), ("strategy_and_architecture", 14, 4, 29)]
    for b, q_c, q_n, q_p in band_table:
        row("S2-BAND-%s" % b.upper().replace("_", "-"), "2 (band table)",
            "band %s: classes / never searched / share" % b,
            {"classes": q_c, "never_searched": q_n, "share_pct": q_p},
            A_MOD, "count(row.band==%r), its never_searched subset, and never/classes rounded" % b,
            {"classes": bands[b], "never_searched": ns_by_band[b],
             "share_pct": pct(ns_by_band[b], bands[b])},
            "RECOMPUTED (grouped count + the manuscript's stated rounding rule)")

    # ---------------- section 2.1 -----------------------------------------
    findings = audit["findings"]
    statuses = Counter()
    for fid, f in findings.items():
        st = f.get("adjudication") if isinstance(f, dict) else None
        statuses[st if st is not None else "<no adjudication key>"] += 1
    row("S21-FLAGGED-73", "2.1", "the audit flagged 73 rows", 73, A_AUD, "len(findings)",
        len(findings), "READ-BACK (row count)")
    row("S21-ALL-UNREVIEWED", "2.1",
        "every finding in the audit file is recorded UNREVIEWED",
        {"n": 73, "all_unreviewed": True}, A_AUD, "findings[*].adjudication",
        {"n": len(findings),
         "all_unreviewed": all(isinstance(k, str) and k.startswith("UNREVIEWED")
                               for k in statuses)},
        "RECOMPUTED (adjudication tally: %s)" % dict(statuses))
    row("S21-20-CANDIDATES-ADJUDICATED", "2.1",
        "Only the 20 candidate rows were adjudicated there [in modalities.json]",
        20, A_MOD, "count(row.verdict=='candidate')", verdicts["candidate"],
        "RECOMPUTED (grouped count)",
        "The count of candidate rows re-derives. Whether each candidate row carries an "
        "adjudication of its audit flag is a prose property with no schema field, so only "
        "the number is checked here.")
    row("S21-ARSENAL-8", "2.1", "the incumbent arsenal is 8 classes", 8, A_MOD,
        "count(row.verdict=='in_clinical_use')", verdicts["in_clinical_use"],
        "RECOMPUTED (grouped count)")
    row("S21-AUDIT-DENOM", "2.1",
        "context: the audit's own never-searched denominator versus the registry's current one",
        {"audit_n_never_searched_rows": 127}, A_AUD, "n_never_searched_rows",
        {"audit_n_never_searched_rows": audit["n_never_searched_rows"]},
        "READ-BACK",
        "NOT a manuscript claim; a context row. The audit artifact still carries the "
        "PRE-correction denominator 127 while the registry now holds %d, so the audit file "
        "was not regenerated after the 2026-08-09 novelty correction. The manuscript quotes "
        "only the 73 flag count from this file, and that count does reproduce; but a reader "
        "who opens the audit to check the 111 headline will find 127 there."
        % len([r for r in mods if r.get("prior_coverage") == "never_searched"]))

    # ---------------- section 3 / 4 ---------------------------------------
    row("S3-TWENTY-SURVIVE", "3", "Twenty classes survive", 20, A_MOD,
        "count(row.verdict=='candidate')", verdicts["candidate"],
        "RECOMPUTED (grouped count)")
    row("S3-ALL-CANDIDATES-ROUTED", "3",
        "every one of them is registered as a route",
        {"candidates": 20, "with_route": 20}, A_MOD,
        "count(verdict=='candidate') and its subset with a non-empty 'route' field",
        {"candidates": verdicts["candidate"],
         "with_route": sum(1 for r in mods if r["verdict"] == "candidate" and r.get("route"))},
        "RECOMPUTED (field presence)")
    row("S4-NINETY-FIVE", "4", "Ninety-five classes are closed here on first inspection",
        95, A_MOD, "count(row.verdict=='excluded')", verdicts["excluded"],
        "RECOMPUTED (grouped count)")

    # ---------------- section 5 -------------------------------------------
    ar = [r for r in mods if r["verdict"] == "already_rejected"]
    resolvable = sum(1 for r in ar
                     if (r.get("prior_ref") or {}).get("file")
                     and os.path.exists(os.path.join(ROOT, r["prior_ref"]["file"])))
    row("S5-33-POINTERS", "5",
        "Thirty-three rows carry already_rejected with a resolvable pointer",
        {"rows": 33, "resolvable": 33}, A_MOD,
        "count(verdict=='already_rejected'); prior_ref.file exists on disk",
        {"rows": len(ar), "resolvable": resolvable},
        "RECOMPUTED (grouped count + filesystem resolution at HEAD)")

    sweeps = ["research/manuscripts/program/emc-post-degrader-options.md",
              "research/manuscripts/program/emc-unexplored-treatment-lanes.md",
              "research/manuscripts/modality-census/emerging-modalities-scan-emc.md"]
    reach = {s: sum(1 for r in mods if (r.get("prior_ref") or {}).get("file") == s) for s in sweeps}
    row("S5-THREE-SWEEPS-REACHED", "5",
        "each of the three prior searches is reached by at least one row",
        {"all_reached": True}, A_MOD, "count of rows whose prior_ref.file is each sweep",
        {"all_reached": all(v >= 1 for v in reach.values())},
        "RECOMPUTED (pointer tally: %s)" % reach,
        "The three sweep documents are identified from section 1 of the manuscript plus the "
        "prior_ref file distribution; the manuscript names them in prose, not by path, so the "
        "identification is this lane's reading, not a stored mapping.")

    # ---------------- section 3.8 / panels --------------------------------
    row("S38-16-ROUTES", "3.8",
        "Sixteen of the routes ... the 16 graded routes", 16, A_GRD, "len(routes)",
        len(grading["routes"]), "READ-BACK (key count)")
    row("S38-479-GENES", "3.8 / 7",
        "the repository's targeted expression panel -- 479 of them as it now stands",
        479, A_PAN, "len(gene_reads)", len(panels["gene_reads"]),
        "READ-BACK (key count)")
    row("S38-TWO-PLATFORMS", "7",
        "the two expression platforms every 'both platforms' statement refers to",
        2, A_PAN, "len(platforms)", len(panels["platforms"]),
        "READ-BACK (key count)")

    ndrg1 = grading["routes"]["RT-SGK1"]["genes"]["NDRG1"]
    p6244 = ndrg1["GSE24369_series_matrix.txt.gz"]
    p3290 = ndrg1["GSE4303-GPL3290_series_matrix.txt.gz"]
    row("S38-NDRG1-98TH", "3.8 (SGK1 row)",
        "its canonical substrate NDRG1 is higher on both, at the 98th percentile on one",
        {"percentile_one_platform": 98, "higher_on_both": True}, A_GRD,
        "routes.RT-SGK1.genes.NDRG1.*.emc_array_percentile and .delta_emc_minus_comparator",
        {"percentile_one_platform": int(round(100 * p6244["emc_array_percentile"])),
         "higher_on_both": p6244["delta_emc_minus_comparator"] > 0
                           and p3290["delta_emc_minus_comparator"] > 0},
        "RECOMPUTED (percentile x100 rounded; sign of both deltas)",
        "GPL6244 percentile %.4f, GPL3290 %.4f." % (p6244["emc_array_percentile"],
                                                    p3290["emc_array_percentile"]))

    # ---------------- DepMap fractions ------------------------------------
    dep = {}
    for grp, rows_ in depmap["genes_by_group"].items():
        for r in rows_:
            dep[r["gene"]] = r

    row("S31-CDK-100PC", "3.1",
        "across 91 screened sarcoma lines, CDK7 and CDK9 are dependencies in 100% of them",
        {"n_sarcoma": 91, "CDK7": 1.0, "CDK9": 1.0}, A_DEP,
        "genes_by_group['BET / transcriptional'] -> CDK7/CDK9 .sarcoma_frac_dependent, .n_sarcoma",
        {"n_sarcoma": dep["CDK7"]["n_sarcoma"],
         "CDK7": dep["CDK7"]["sarcoma_frac_dependent"],
         "CDK9": dep["CDK9"]["sarcoma_frac_dependent"]},
        "READ-BACK from the committed DepMap summary",
        "The manuscript cites census-route-expression-grading.json -> routes.RT-TXN-CDK for this; "
        "that file states the same fractions in prose and names DepMap 24Q4 as their origin. "
        "Re-derived here against the numeric artifact rather than the prose restatement.")

    row("S32A-BH3-FRACTIONS", "3.2a (MCL-1 / BCL-xL row)",
        "across the 91 screened sarcoma lines MCL1 and BCL2L1 are dependencies in 83.5% and "
        "75.8% and BCL2 in 2.2%",
        {"n_sarcoma": 91, "MCL1": 0.835, "BCL2L1": 0.758, "BCL2": 0.022}, A_DEP,
        "genes_by_group['Apoptotic guardians (BH3)'] -> .sarcoma_frac_dependent, .n_sarcoma",
        {"n_sarcoma": dep["MCL1"]["n_sarcoma"],
         "MCL1": dep["MCL1"]["sarcoma_frac_dependent"],
         "BCL2L1": dep["BCL2L1"]["sarcoma_frac_dependent"],
         "BCL2": dep["BCL2"]["sarcoma_frac_dependent"]},
        "READ-BACK from the committed DepMap summary")

    # The manuscript's "five druggable guardians" is the panel group
    # anti_apoptotic_the_druggable_ones, whose stored genes_requested list is exactly five.
    grp = panels["panels"]["apoptotic_dependency"]["groups"]["anti_apoptotic_the_druggable_ones"]
    five = list(grp["genes_requested"])
    PL = ["GSE24369_series_matrix.txt.gz", "GSE4303-GPL3290_series_matrix.txt.gz"]
    per_gene = {}
    for g in five:
        rec = panels["gene_reads"][g]
        per_gene[g] = {}
        for pl in PL:
            v = rec.get(pl)
            if not v or not v.get("readable"):
                per_gene[g][pl] = None
            else:
                per_gene[g][pl] = round(v["EMC"]["mean_z"] - v["comparator"]["mean_z"], 4)
    lower_both = {g: all(d is not None and d < 0 for d in per_gene[g].values()) for g in five}
    n_lower = sum(1 for g in five if lower_both[g])

    row("S32A-GUARDIANS-LOWER", "3.2a (MCL-1 / BCL-xL row)",
        "all five druggable guardians are lower on both platforms",
        {"gene_set_size": 5, "n_lower_on_BOTH_platforms": 5}, A_PAN,
        "panels.apoptotic_dependency.groups.anti_apoptotic_the_druggable_ones.genes_requested; "
        "gene_reads[gene][platform].EMC.mean_z - .comparator.mean_z, sign on both platforms",
        {"gene_set_size": len(five), "n_lower_on_BOTH_platforms": n_lower},
        "RECOMPUTED (per-gene EMC-minus-comparator mean_z delta, sign on each platform)",
        "REPORTED, NOT REPAIRED. Gene set %s. Per-gene delta (EMC minus comparator) by platform: "
        "%s. BCL2, MCL1 and BCL2L1 are lower on both. BCL2L2 is HIGHER in EMC on GPL6244 "
        "(+0.1231) and lower on GPL3290 (-0.0457); BCL2A1 is HIGHER on GPL6244 (+0.0371) and "
        "lower on GPL3290 (-0.5299). Three of five, not five of five, are lower on both. "
        "What IS lower on both is the GROUP MEAN: the stored module score is LOWER in EMC on "
        "GPL6244 (delta -0.259, t -4.568, df 14.0, 5/5 readable) and on GPL3290 (delta -0.4097, "
        "t -2.538, df 9.8, 5/5 readable). The manuscript states a module-level result with a "
        "per-gene universal quantifier. The route verdict it supports ('against at the "
        "abundance level') is unaffected by this; the sentence is."
        % (five, {g: per_gene[g] for g in five}))

    row("S32A-GUARDIAN-MODULE-LOWER-BOTH", "3.2a (supporting re-derivation)",
        "the guardian MODULE is lower in EMC on both platforms",
        {"GPL6244_t": -4.568, "GPL3290_t": -2.538}, A_GRD,
        "routes.RT-APOPTOSIS-DEP.panel_groups.anti_apoptotic_the_druggable_ones.*.score.t",
        {"GPL6244_t": grading["routes"]["RT-APOPTOSIS-DEP"]["panel_groups"]
                     ["anti_apoptotic_the_druggable_ones"][PL[0]]["score"]["t"],
         "GPL3290_t": grading["routes"]["RT-APOPTOSIS-DEP"]["panel_groups"]
                     ["anti_apoptotic_the_druggable_ones"][PL[1]]["score"]["t"]},
        "READ-BACK from the committed grading artifact",
        "This is the statement the manuscript's evidence actually supports, and it reproduces. "
        "Recorded so the MISMATCH above is read as a quantifier defect, not as a reversal of "
        "the route verdict.")

    # ---------------- an explicitly non-local claim ------------------------
    row("S21-15-WRONG-ROWS", "2.1",
        "The first version of this document said 127, and 15 of those rows were wrong",
        {"prior_headline": 127, "rows_corrected": 15}, A_MOD + " (+ git history)",
        "no committed field records the pre-correction prior_coverage state of each row",
        None, "NOT-RE-DERIVABLE-LOCALLY",
        "The current registry holds only the post-correction state. 127 - 111 = 16, not 15, "
        "and the manuscript separately records a two-row change in total class count "
        "(215 -> 217), so the arithmetic is not closable from the present artifacts alone.",
        force="NOT-RE-DERIVABLE-LOCALLY",
        missing_input="The pre-2026-08-09 revision of systems/graph/modalities.json, or a "
                      "committed per-row before/after list of the 15 prior_coverage flips. "
                      "census-novelty-audit.json records n_never_searched_rows=%d and 73 "
                      "UNREVIEWED findings, and adjudicates none, so it cannot supply the 15."
                      % audit["n_never_searched_rows"])

    row("S1-FOUR-INVISIBLE", "1",
        "Four whole categories had been invisible to every previous search",
        4, "research/manuscripts/program/emc-unexplored-treatment-lanes.md (2026-08-07 sweep)",
        "prose claim of the cited sweep; no count field in any census artifact", None,
        "NOT-RE-DERIVABLE-LOCALLY",
        "Restated from a prior document rather than derived from the census artifacts.",
        force="NOT-RE-DERIVABLE-LOCALLY",
        missing_input="A machine-readable category list in the 2026-08-07 sweep artifact. The "
                      "sweep is a prose manuscript; the census registry stores no field "
                      "recording which categories that sweep could not see.")

    # ---------------- assemble --------------------------------------------
    counts = Counter(r["verdict"] for r in ROWS if not r["claim_id"].startswith("CTRL-"))
    ctrl = {r["claim_id"]: r["verdict"] for r in ROWS if r["claim_id"].startswith("CTRL-")}
    ctrl_ok = ctrl.get("CTRL-POS") == "REPRODUCES" and ctrl.get("CTRL-NEG") == "MISMATCH"

    head = subprocess.run(["git", "-C", ROOT, "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    porcelain = subprocess.run(
        ["git", "-C", ROOT, "status", "--porcelain", "--"] + list(SOURCES.values()),
        capture_output=True, text=True).stdout.strip()

    doc = {
        "id": "ART-MODALITY-CENSUS-CLAIM-REDERIVATION-LEDGER",
        "lane": "MODALITY-CENSUS-1",
        "campaign": "OPUS-CAPACITY-CAMPAIGN-20260908",
        "date": "2026-09-09",
        "endpoint": "PUB-MODALITY-CENSUS",
        "scope": "One pass over the quantitative claims printed in the manuscript. Verdicts are "
                 "REPRODUCES, MISMATCH or NOT-RE-DERIVABLE-LOCALLY. A MISMATCH is reported, "
                 "never repaired. This lane wrote nothing outside its own directory.",
        "repo_head": head,
        "git_status_porcelain_for_sources": porcelain,
        "sources_hashed_at_use_time": {k: {"path": v, "sha256": sha256(v)}
                                       for k, v in SOURCES.items()},
        "known_answer_control": {
            "CTRL-POS_expected": "REPRODUCES", "CTRL-POS_observed": ctrl.get("CTRL-POS"),
            "CTRL-NEG_expected": "MISMATCH", "CTRL-NEG_observed": ctrl.get("CTRL-NEG"),
            "harness_trustworthy": ctrl_ok,
        },
        "verdict_counts_excluding_controls": dict(counts),
        "claims": ROWS,
    }
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, indent=1, ensure_ascii=False)
        fh.write("\n")

    for r in ROWS:
        print("%-28s %-26s %s" % (r["claim_id"], r["verdict"], r["claim"][:70]))
    print()
    print("controls: CTRL-POS=%s CTRL-NEG=%s trustworthy=%s"
          % (ctrl.get("CTRL-POS"), ctrl.get("CTRL-NEG"), ctrl_ok))
    print("verdicts (excluding controls): %s" % dict(counts))
    print("ledger written: %s" % OUT)

    if not ctrl_ok:
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())
