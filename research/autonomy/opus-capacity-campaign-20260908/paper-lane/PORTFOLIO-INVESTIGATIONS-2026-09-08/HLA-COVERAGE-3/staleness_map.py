#!/usr/bin/env python3
"""HLA-COVERAGE-3 step 2/3: the staleness map, built by READING the producer and the artifacts.

⛔ No producer is executed. ⛔ Route B8 (HLA-C) is closed: no HLA-C frequency is fetched,
substituted or invented. Where a value depends on one, the verdict is UNKNOWN, never zero.

Verdicts:
  REPRODUCES        — the current producer would write the committed value.
  CHANGES           — the current producer would write a different value, and the new value is
                      determinable offline from the source alone.
  CHANGES_DIRECTION — the value would change or stay, with the DIRECTION fixed by the code, but the
                      magnitude undeterminable offline.
  UNDETERMINABLE    — cannot be settled offline (needs MHCflurry's supported_alleles, HLA-C
                      frequencies, or a run).
"""
import ast, hashlib, json, os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), *[".."] * 6))
MOD = os.path.join(ROOT, "research", "modalities")
MS = os.path.join(ROOT, "research", "manuscripts", "neoantigen", "emc-vaccine-development-path.md")

def J(name): return json.load(open(os.path.join(MOD, name)))
def sha(p):
    b = open(p, "rb").read(); return {"bytes": len(b), "sha256": hashlib.sha256(b).hexdigest()}

src = open(os.path.join(MOD, "coverage_scan.py")).read()
consts = {}
for n in ast.parse(src).body:
    if isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Name) and n.targets[0].id in ("PANEL_AB", "PANEL_C"):
        consts[n.targets[0].id] = [ast.literal_eval(e) for e in n.value.elts]
AB, C = consts["PANEL_AB"], consts["PANEL_C"]
NEW = len(AB) + len(C)

strict, loose, curve, tcurve = J("epitope-allele-matrix.json"), J("epitope-allele-loose-matrix.json"), \
    J("coverage-curve.json"), J("coverage-threshold-curve.json")
conc, nug = J("predictor-concordance.json"), J("epitope-allele-matrix-mhcnuggets.json")
vtc, stage0 = J("vaccine-threshold-calibration.json"), J("stage0-vaccine-item-provenance.json")
OLD = len(strict["panel"])

def E(f, key, committed, verdict, new, why):
    return {"file": f, "key": key, "committed_value": committed, "verdict": verdict,
            "value_under_the_current_producer": new, "why": why}

rows = []
# ---- tier 1: written directly by coverage_scan.py ---------------------------------
rows += [
 E("research/modalities/epitope-allele-matrix.json", "panel (length)", OLD, "CHANGES", NEW,
   f"predict_matrix() writes `\"panel\": PANEL`, and PANEL = PANEL_AB + PANEL_C = {len(AB)} + {len(C)}."),
 E("research/modalities/epitope-allele-matrix.json", "panel (loci)", ["A", "B"], "CHANGES", ["A", "B", "C"],
   "PANEL_C adds 18 two-field HLA-C alleles under the AUT-079 comment."),
 E("research/modalities/epitope-allele-matrix.json", "panel (first 34 entries)", "PANEL_AB",
   "REPRODUCES", "PANEL_AB",
   "The committed panel is element-for-element equal to the producer's current PANEL_AB: "
   f"{consts['PANEL_AB'] == strict['panel']}. The drift is purely additive."),
 E("research/modalities/epitope-allele-matrix.json", "_note", strict["_note"], "CHANGES",
   "same sentence with 'broad HLA-A/-B/-C panel'",
   "The producer's _note literal now reads 'HLA-A/-B/-C panel'; the committed string reads "
   "'broad HLA-A/-B panel'. A pure string-literal difference, determinable by reading."),
 E("research/modalities/epitope-allele-matrix.json", "alleles_without_a_model",
   "ABSENT (key not in the committed file)", "CHANGES", "PRESENT (key always emitted)",
   "predict_matrix() unconditionally writes `alleles_without_a_model` and "
   "`⚠_missing_model_is_not_a_negative`. Its CONTENTS are UNDETERMINABLE offline: they depend on "
   "MHCflurry 2.1.4's own supported_alleles, which cannot be read without the package."),
 E("research/modalities/epitope-allele-matrix.json", "n_peptides", strict["n_peptides"], "REPRODUCES",
   strict["n_peptides"],
   "Peptides come from fusion-breakpoint-neoantigens.json junctions[].novel_peptides at lengths "
   "8-11; that input is untouched by the panel change."),
 E("research/modalities/epitope-allele-matrix.json", "rank_column", strict["rank_column"], "REPRODUCES",
   strict["rank_column"], "Column choice depends on the predictor build, not the panel."),
 E("research/modalities/epitope-allele-matrix.json", "strong_binders (count)", len(strict["strong_binders"]),
   "CHANGES_DIRECTION", f">= {len(strict['strong_binders'])}",
   "predict() is called with alleles={a: [a]}, i.e. one single-allele sample per allele, so each "
   "output row's best_allele IS that allele and its percentile does not depend on which other "
   "alleles are in the batch. Adding panel alleles can therefore only ADD rows, never alter or "
   "remove an existing one. How many HLA-C rows appear is UNKNOWN (B8)."),
 E("research/modalities/epitope-allele-matrix.json", "presenting_alleles",
   strict["presenting_alleles"], "CHANGES_DIRECTION", "a superset of the committed four",
   "presenting_alleles is derived from strong_binders, which is monotone non-decreasing in the "
   "panel. UNKNOWN whether any HLA-C allele enters."),
 E("research/modalities/coverage-curve.json", "panel_size", curve["panel_size"], "CHANGES", NEW,
   "panel_size = len(matrix['panel']) and the matrix would carry 52."),
 E("research/modalities/coverage-curve.json", "_note", "'Coverage vs number of HLA-A/-B alleles ...'",
   "CHANGES", "'Coverage vs number of HLA-A/-B/-C alleles ...'",
   "The producer's _note literal already says HLA-A/-B/-C; the committed artifact says HLA-A/-B."),
 E("research/modalities/coverage-curve.json", "n_presenting_alleles", curve["n_presenting_alleles"],
   "CHANGES_DIRECTION", f">= {curve['n_presenting_alleles']}", "As above, monotone non-decreasing."),
 E("research/modalities/coverage-curve.json", "global_max_coverage", curve["global_max_coverage"],
   "CHANGES_DIRECTION", f">= {curve['global_max_coverage']}",
   "greedy_curve keeps only alleles with a non-None AFND frequency and accumulates "
   "1 - prod(1-af)^2, which is non-decreasing as alleles are added. So coverage can only rise or "
   "stay equal. ⛔ The SIZE of any rise needs HLA-C allele frequencies; none exists in this "
   "checkout and route B8 forbids acquiring one. Magnitude UNKNOWN, not zero."),
 E("research/modalities/coverage-curve.json", "global_alleles_to_reach",
   curve["global_alleles_to_reach"], "CHANGES_DIRECTION",
   "each target reached at the same n or an earlier one, or still null",
   "alleles_to_reach reads the same non-decreasing cumulative curve. UNKNOWN whether any target "
   "(50/80/90/95%) becomes reachable."),
 E("research/modalities/coverage-curve.json", "regions (15 sub-regions)", len(curve["regions"]),
   "UNDETERMINABLE", "UNKNOWN",
   "Regional curves are rebuilt from a LIVE AFND fetch through hla_coverage.load_afnd. Offline "
   "this cannot be evaluated at all, and the HLA-C half is closed under B8."),
 E("research/modalities/coverage-curve.png", "(whole figure)", "committed image", "CHANGES_DIRECTION",
   "redrawn", "render_chart() is called with the new curve; it changes iff the curve changes."),
]
# ---- tier 2: producers that READ epitope-allele-matrix.json ------------------------
rows += [
 E("research/modalities/epitope-allele-loose-matrix.json", "panel (length)", len(loose["panel"]),
   "CHANGES", NEW,
   "coverage_threshold_curve.predict_loose() takes `panel = json.load(open(STRICT))['panel']` — it "
   "does NOT import coverage_scan.PANEL. So this file is stale only AFTER coverage_scan.py is "
   "re-run; on today's tree it still reproduces 34. It is a second-order dependency, and the "
   "committed loose panel equals the committed strict panel: "
   f"{loose['panel'] == strict['panel']}."),
 E("research/modalities/epitope-allele-loose-matrix.json", "calls (count)", len(loose["calls"]),
   "CHANGES_DIRECTION", f">= {len(loose['calls'])}", "Same single-allele-sample argument as above."),
 E("research/modalities/coverage-threshold-curve.json", "at_conventional_threshold.coverage",
   tcurve["at_conventional_threshold"]["coverage"], "CHANGES_DIRECTION",
   f">= {tcurve['at_conventional_threshold']['coverage']}",
   "Equals coverage-curve.json's global_max_coverage by construction (asserted by "
   "research/modalities/tests/test_coverage_threshold_curve.py), so it moves with it."),
 E("research/modalities/coverage-threshold-curve.json", "at_conventional_threshold.n_presenting_alleles",
   tcurve["at_conventional_threshold"]["n_presenting_alleles"], "CHANGES_DIRECTION",
   f">= {tcurve['at_conventional_threshold']['n_presenting_alleles']}", "Monotone in the panel."),
 E("research/modalities/coverage-threshold-curve.json", "allele_frequencies (count)",
   len(tcurve["allele_frequencies"]), "UNDETERMINABLE", "UNKNOWN",
   "⛔ This is the load-bearing B8 wall. The block is A/B only. Whether AFND carries the 18 "
   "PANEL_C alleles, and at what frequency, CANNOT be established from this checkout and may not "
   "be acquired. Reported UNKNOWN, never zero."),
 E("research/modalities/coverage-threshold-curve.json", "steps", len(tcurve["steps"]),
   "CHANGES_DIRECTION", f">= {len(tcurve['steps'])}", "One step per call that moves the curve."),
 E("research/modalities/predictor-concordance.json", "n_panel", conc["n_panel"], "CHANGES", NEW,
   "predictor_concordance.panel() returns json.load(open(MATRIX))['panel'], so n_panel tracks the "
   "strict matrix exactly."),
 E("research/modalities/epitope-allele-matrix-mhcnuggets.json", "panel (length)", len(nug["panel"]),
   "CHANGES", NEW, "Same panel() call; the MHCnuggets arm inherits the drift verbatim."),
 E("research/modalities/epitope-allele-matrix-mhcnuggets.json", "alleles_without_a_model",
   len(nug["alleles_without_a_model"]), "CHANGES_DIRECTION", f">= {len(nug['alleles_without_a_model'])}",
   "MHCnuggets class I HLA-C support is UNKNOWN here; the count cannot fall when alleles are added."),
 E("research/modalities/vaccine-threshold-calibration.json", "_panel (length)", len(vtc["_panel"]),
   "CHANGES", NEW,
   "vaccine_threshold_calibration.main() sets `panel = strict['panel']` from "
   "epitope-allele-matrix.json."),
 E("research/modalities/stage0-vaccine-item-provenance.json",
   "items[].headline_derived_from_the_artifact.n_alleles_in_the_panel", 34, "CHANGES", NEW,
   "stage0_vaccine_item_provenance.py reads epitope-allele-matrix.json → panel and records its "
   "length; the artifact names `panel_source: epitope-allele-matrix.json → panel`."),
 E("research/modalities/stage0-vaccine-item-provenance.json",
   "items[]....n_panel_alleles_presenting_anything_at_or_below_the_curve_ceiling", 28,
   "CHANGES_DIRECTION", ">= 28",
   "Counts panel alleles appearing in the loose curve; monotone in the panel, magnitude UNKNOWN."),
 E("research/modalities/run-manifest.json", "artifacts[] hashes / stale flags", "as committed",
   "CHANGES", "new hashes for every artifact above",
   "run_manifest.py tracks these six filenames explicitly; any regeneration moves their hashes."),
]
# ---- tier 3: the manuscript --------------------------------------------------------
ms = open(MS).read().splitlines()
def line_of(sub):
    for i, l in enumerate(ms, 1):
        if sub in l: return i, l.strip()
    return None, None
SENT = [
 ("34-allele panel for the coverage scan", "CHANGES", "52",
  "§Methods. The panel width is stated in prose; the producer now defines 52."),
 ("34-allele screen of the same peptides at the same threshold returns five strong", "CHANGES_DIRECTION",
  "52-allele screen returning >= five strong calls",
  "§2.2. Width CHANGES deterministically to 52; the call count can only rise, magnitude UNKNOWN. "
  "This sentence is enforced: test_vaccine_path_numbers.py binds "
  "r'a (\\d+)-allele screen of the same peptides' to len(matrix['panel'])."),
 ("Screened against the same 34-allele panel at the same cut, those 97 peptides return 10 strong",
  "CHANGES_DIRECTION", "52-allele panel; >= 10 strong calls across >= 6 alleles",
  "§2.2 out-of-frame screen. Produced by junction_frameshift_peptides.py over the same panel."),
 ("on 34 alleles the same lead peptide is also strong on HLA-A", "CHANGES_DIRECTION",
  "'on 52 alleles ...'; the ADDED-allele account may no longer be a single allele",
  "§2.3. test_the_broad_panel_adds_exactly_the_allele_the_paper_says_it_adds asserts "
  "len(curve.presenting_alleles - the three ten-allele ones) == 1. If any HLA-C allele presents, "
  "that assertion FAILS and the paper's whole account of why 8.5% becomes 12.3% needs rewriting. "
  "Whether it does is UNKNOWN (B8)."),
 ("gives 27.4% on ten alleles and 30.4% on 34", "CHANGES_DIRECTION",
  "27.4% unchanged; the second figure >= 30.4% on 52",
  "The 27.4% term comes from hla_coverage.py and the ten-allele junction screen and is NOT "
  "downstream of coverage_scan.py. Only the broad-panel figure moves."),
 ("The 34-allele screen finds 4 presenting alleles and 30.4%", "CHANGES_DIRECTION",
  "'The 52-allele screen finds >= 4 ... and >= 30.4%'", "§B1 evidence line."),
 ("On the 34-allele set the same product gives 2.0%", "CHANGES_DIRECTION", ">= 2.0%",
  "§ class I x class II product; the class I term is the broad-panel coverage."),
 ("The class I panels remain at 10 and 34 alleles", "CHANGES", "10 and 52", "§B4 status sentence."),
 ("The screen tested 174 peptides against 10 and then 34 alleles at two thresholds", "CHANGES",
  "10 and then 52", "§7."),
 ("0.644% of 59,160 peptide-allele tests", "CHANGES", "the denominator becomes 1,740 x 52 = 90,480",
  "§7 decoy null. 59,160 = 1,740 decoys x 34 panel alleles, exactly; the denominator is "
  "arithmetic in the panel size and is therefore determinable offline. The 0.644% RATE over a "
  "C-inclusive panel is UNKNOWN."),
 ("presents on a median of 23 of the 34 alleles", "CHANGES_DIRECTION",
  "'of the 52 alleles'; the median and the closed form rescale",
  "§7. The closed form is n_panel x (1-(1-p)^174): 34 x 0.675 = 22.95 as committed. With 52 the "
  "same p would give 35.1, but p over a C-inclusive panel is UNKNOWN, so only the denominator 52 "
  "is determinate."),
 ("over the 34-allele panel, each step one peptide-allele call", "CHANGES", "52", "Figure 2 caption (§2.3)."),
 ("Table 2. The 34-allele class I panel", "CHANGES", "52 in the header, WITH A LATENT DEFECT",
  "⚠ THE ONE PLACE THE DRIFT WOULD PRODUCE A WRONG PAGE RATHER THAN A STALE ONE. Table 2 is a "
  "GENERATED block (vaccine_path_tables.panel_block). It renders "
  "f'The {len(panel)}-allele class I panel' — so the header would read 52 — but the body emits "
  "only `HLA-A` and `HLA-B` rows (there is no HLA-C branch), so the 18 C alleles would be silently "
  "dropped and the table would list 34 alleles under a 52-allele heading; and the caption's "
  "hard-coded clause 'it carries no HLA-C and no class II allele' would become FALSE. Determinable "
  "offline by reading the generator."),
 ("`coverage_scan.py` (the coverage-versus-allele-count curve)", "AFFECTED_CLAIM",
  "the section's blanket reproducibility claim acquires a second exception",
  "§8 states every figure 'is generated by a script ... and is committed as a JSON artifact beside "
  "it, with one exception'. Under the current producer that claim has a second exception, and this "
  "is where the repository's own convention puts such a note (the adjacent 'These are not "
  "regenerated on every commit' paragraph is the comparable existing note)."),
]
sent_rows = []
for sub, verdict, new, why in SENT:
    ln, txt = line_of(sub)
    sent_rows.append({"file": "research/manuscripts/neoantigen/emc-vaccine-development-path.md",
                      "line": ln, "sentence_fragment": sub, "committed_line": txt,
                      "verdict": verdict, "value_under_the_current_producer": new, "why": why})

# ---- tier 4: enforcement -----------------------------------------------------------
guards = [
 E("research/manuscripts/tests/test_vaccine_path_numbers.py",
   "test_the_panel_the_paper_names_is_the_panel_that_ran", "passes on today's tree", "CHANGES",
   "FAILS unless every '34-allele screen' site in the prose is updated together",
   "It binds the prose number to len(matrix['panel']) at every site. This is the guard that turns "
   "the drift into a build failure rather than a silent error — it must NOT be weakened."),
 E("research/manuscripts/tests/test_vaccine_path_numbers.py",
   "test_the_broad_panel_adds_exactly_the_allele_the_paper_says_it_adds", "passes on today's tree",
   "UNDETERMINABLE", "UNKNOWN — passes iff no HLA-C allele presents a strong junction binder",
   "asserts len(added) == 1. Whether MHCflurry 2.1.4 even scores HLA-C is UNKNOWN and closed."),
 E("research/modalities/tests/test_coverage_threshold_curve.py",
   "the cross-artifact identity coverage-curve.json max == threshold curve at 0.5",
   "passes on today's tree", "CHANGES_DIRECTION",
   "still passes if BOTH are regenerated; FAILS if only one is",
   "The two artifacts must be regenerated together or the identity breaks."),
 E("research/manuscripts/vaccine_path_tables.py", "--check", "passes on today's tree", "CHANGES",
   "reports STALE for the class-i-panel block",
   "render() rebuilds Table 2 from the matrix; a 52-allele matrix makes the committed block stale."),
 E("systems/graph/artifact-refs.json", "the coverage-scan.json disposition entry",
   "already withdraws any byte-for-byte reproduction endorsement", "REPRODUCES",
   "unchanged, and corroborating",
   "Read 2026-09-08, it explicitly withdraws the earlier claim that re-running coverage_scan.py "
   "offline reproduces coverage-curve.json and epitope-allele-matrix.json. This lane's result is "
   "the concrete reason that withdrawal was right."),
]

out = {
 "_id": "HLA-COVERAGE-3-staleness-map", "_date": "2026-09-09",
 "_what": "Every committed artifact, manuscript sentence and guard downstream of "
          "research/modalities/coverage_scan.py, with a per-key verdict on whether the CURRENT "
          "producer would reproduce it.",
 "⛔_route_fence": "B8 (HLA-C) closed. The producer was NOT run. No HLA-C allele frequency exists "
                   "in this checkout and none was sought. Every quantity needing one is UNKNOWN.",
 "_method": "coverage_scan.py parsed with ast (never imported, never executed); every committed "
            "value read from the artifact on disk; every direction argued from the producer source.",
 "_verdict_key": {
   "REPRODUCES": "current producer writes the committed value",
   "CHANGES": "current producer writes a different value, determinable offline",
   "CHANGES_DIRECTION": "changes or stays; direction fixed by the code, magnitude not determinable offline",
   "UNDETERMINABLE": "cannot be settled offline",
   "AFFECTED_CLAIM": "prose claim whose truth value is affected without a number changing"},
 "_provenance": {p: sha(os.path.join(MOD, p)) for p in
                 ["coverage_scan.py", "epitope-allele-matrix.json", "epitope-allele-loose-matrix.json",
                  "coverage-curve.json", "coverage-threshold-curve.json", "predictor-concordance.json",
                  "epitope-allele-matrix-mhcnuggets.json", "vaccine-threshold-calibration.json",
                  "stage0-vaccine-item-provenance.json"]},
 "_panel": {"committed_panel_n": OLD, "producer_PANEL_AB_n": len(AB), "producer_PANEL_C_n": len(C),
            "producer_PANEL_n": NEW, "committed_panel_is_exactly_PANEL_AB": AB == strict["panel"],
            "PANEL_C": C},
 "artifacts": rows, "manuscript_sentences": sent_rows, "guards_and_graph": guards,
 "_totals": {"REPRODUCES": sum(1 for r in rows + guards if r["verdict"] == "REPRODUCES"),
             "CHANGES": sum(1 for r in rows + guards + sent_rows if r["verdict"] == "CHANGES"),
             "CHANGES_DIRECTION": sum(1 for r in rows + guards + sent_rows if r["verdict"] == "CHANGES_DIRECTION"),
             "UNDETERMINABLE": sum(1 for r in rows + guards + sent_rows if r["verdict"] == "UNDETERMINABLE"),
             "AFFECTED_CLAIM": sum(1 for r in sent_rows if r["verdict"] == "AFFECTED_CLAIM"),
             "n_rows": len(rows) + len(sent_rows) + len(guards)},
}
missing = [r for r in sent_rows if r["line"] is None]
if missing:
    raise SystemExit("⛔ manuscript fragment not found: " + json.dumps([m["sentence_fragment"] for m in missing]))
json.dump(out, open(os.path.join(os.path.dirname(__file__), "staleness-map.json"), "w"), indent=2, ensure_ascii=False)
print(json.dumps(out["_totals"], indent=2))
print(json.dumps(out["_panel"]["committed_panel_is_exactly_PANEL_AB"]))
for r in sent_rows: print(f"  line {r['line']:>5}  {r['verdict']:<18} {r['sentence_fragment'][:60]}")
