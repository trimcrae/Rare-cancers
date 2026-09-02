#!/usr/bin/env python3
"""Is PUB-ATR's part-D negative a fact about the mechanism, or a fact about WHICH proliferation
control was chosen?

⛔ THE OBJECTION THIS ANSWERS. Part D's second specificity axis is
`beats_the_proliferation_control` = `abs(rho) > abs(prolif_rho) * 1.15`, and `prolif_rho` is
supplied by ONE score: `expr::proliferation_MYC` — Hallmark MYC Targets V1, 200 genes, mean
Spearman rho against ATR-inhibitor residual LN_IC50 of -0.1711 in the committed artifact. A
MYC-target set is not a mechanism-neutral nuisance variable for an ATR hypothesis: oncogene-induced
replication stress is itself a nominated axis of ATR-inhibitor sensitivity, and the source paper
treats it as a rival mechanism it had to exclude experimentally —

    "Previously described mechanisms of ATR sensitivity, most notably replication stress (RS),
     could also contribute to the elimusertib effects that we observed. To test this directly, we
     expressed RNAseH1, which degrades R-loops, the major source of oncogene-induced replication
     stress in ES."
     (research/modalities/atr-hrd-sarcoma-series-inputs.json -> mechanism_fulltext_xml)

So "cannot beat the proliferation control" may mean "cannot beat a SECOND REPLICATION-STRESS AXIS"
rather than "is only generic proliferation". Those are different findings and the manuscript
currently reports only the second.

⭐ THIS MODULE CHANGES NO BAR AND RE-GRADES NOTHING. The bar, the four mechanism tests, the
magnitude floor, the direction predictions and the `atri_specific` clause are all left exactly as
the committed module computes them. The ONLY substitution is which committed per-line score
supplies `prolif_rho`. The result is reported BESIDE the existing grade, never swapped into it —
re-grading on a new control would be a bar change, and a cycle may not change the bar that blocked
it (CLAUDE.md section 6, amendment_guard).

Cost: $0. Reads two committed files, fetches nothing, runs no GPU.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

INPUTS = os.path.join(HERE, "emc-atr-vulnerability-inputs.json")
ARTIFACT = os.path.join(HERE, "emc-atr-vulnerability.json")
OUT = os.path.join(HERE, "atr-part-d-proliferation-control.json")

# =============================================================================================
# THE PRE-REGISTRATION.
#
# ⛔⛔ EVERY WORD BELOW WAS WRITTEN AND COMMITTED BEFORE ANY VERDICT UNDER A NEW CONTROL WAS
# COMPUTED, AND THE GIT HISTORY OF THIS FILE IS THE RECORD OF THAT. The failure mode this guards
# against is the obvious one: run several comparators, keep the one whose answer you preferred.
# The comparators are named here, in full, with the reasoning for each, and the module reports all
# of them whatever they say.
# =============================================================================================
PREREGISTRATION = {
    "⭐ _what_exactly_preceded_what": (
        "EVERY WORD OF THIS PRE-REGISTRATION, AND THE `gene_set_composition` BLOCK THAT ARGUES FOR "
        "THE COMPARATOR, WAS WRITTEN BEFORE ANY COMPARATOR VERDICT WAS COMPUTED — before the "
        "compute module existed at all — and was generated into this artifact with `results: "
        "null`. That results-free artifact is committed on its own, ahead of the results commit, "
        "so `git log --follow` shows the two separately. "
        "⛔ WHAT WAS *NOT* UNSEEN, STATED PLAINLY RATHER THAN IMPLIED: the committed artifact's "
        "EXISTING numbers under the incumbent MYC control were read first — that is the state this "
        "analysis was asked to establish, and pretending otherwise would be the dishonest half of "
        "a pre-registration claim. What no one had seen when the comparator was fixed is any "
        "number produced UNDER the comparator. That is the guarantee this block makes, and it is "
        "the only one it makes."),

    "the_question": (
        "Do part D's four mechanism tests, its `tracks_mechanism` verdict, and the grading tier "
        "that reads them, depend on the CHOICE of `expr::proliferation_MYC` as the nuisance "
        "control — or do they hold under a proliferation control that is not built from the "
        "transcriptional output of the oncogene whose replication stress is the rival mechanism?"),

    "what_is_held_fixed": [
        "The bar itself: `beats_the_proliferation_control` = abs(rho) > abs(control_rho) * 1.15.",
        "The pass rule: direction_matches AND abs(rho) >= 0.15 AND atri_specific AND beats_control.",
        "`tracks_mechanism` = at least 2 of the mechanism tests pass.",
        "The grading tiers, verbatim, and the predicate wiring in `grade()`.",
        "Every rho: recomputed from the SAME committed per-line scores with the SAME `_spearman`, "
        "so the only thing that moves between columns is which score supplies `control_rho`.",
    ],

    "comparators_declared_in_advance": {
        "C0_incumbent": {
            "predictor": "expr::proliferation_MYC",
            "gene_set": "MSigDB Hallmark 2020 'Myc Targets V1', 200 genes",
            "role": "the control the committed artifact uses. Reported as the reference column.",
        },
        "C1_primary": {
            "predictor": "expr::proliferation_mitotic",
            "gene_set": "MSigDB Hallmark 2020 'Mitotic Spindle', 199 genes",
            "already_committed": (
                "scored for all 1673 DepMap lines in emc-atr-vulnerability-inputs.json -> "
                "part_d.expression_scores_by_line.proliferation_mitotic. No fetch is needed and "
                "no new gene set is introduced by this analysis."),
            "⭐ why_this_one_argued_from_CONTENT_not_from_its_NAME": [
                "IT SHARES ONE GENE WITH MYC TARGETS V1 — YWHAE — out of 200 and 199, Jaccard "
                "0.0025. The independence being claimed is quantified rather than asserted.",
                "⛔ IT SHARES ZERO OF THE 37 MEMBERS OF THE ATR-ACTIVATION SET THE PAPER TESTS "
                "(Reactome 'Activation of ATR in Response to Replication Stress'), WHERE MYC "
                "TARGETS V1 SHARES NINE — and those nine are the replication-origin machinery "
                "itself: CDC45, CDK2, MCM2, MCM4, MCM5, MCM6, MCM7, ORC2, RFC4. That is the CMG "
                "helicase plus origin licensing and firing. The incumbent control is therefore "
                "not merely correlated with the mechanism by biology; it CONTAINS the mechanism's "
                "genes, which is the strongest form the objection can take.",
                "Its own members are M-phase and cytoskeletal regulators — Rho GEFs and GAPs, "
                "kinesins, centrosomal and actin machinery, AURKA, BUB1, ANLN, BIRC5. That "
                "machinery acts AFTER replication is finished, so a line can score high on it "
                "without being under replication stress, which is exactly the separation a "
                "nuisance control for an ATR hypothesis has to have.",
                "What it shares with MYC Targets V1 is the property we WANT a proliferation "
                "control to have and only that: both are expressed in cycling cells. The reader "
                "can check the claim from the numbers reported under "
                "`gene_set_composition`.",
            ],
        },
        "C2_secondary_consistency_NOT_an_independent_control": {
            "predictor": "expr::proliferation_MYC_and_mitotic_mean",
            "definition": "per line, the mean of the two proliferation_* scores.",
            "⛔ why_it_cannot_answer_the_independence_question": (
                "it contains MYC Targets V1, so a verdict that holds under it is not evidence "
                "that the verdict is independent of MYC. It is declared and reported for a "
                "different reason."),
            "why_it_is_reported_anyway": (
                "PART B ALREADY USES EXACTLY THIS MEAN. `derive_part_b` collects every concept "
                "whose role is `proliferation_control` — both of them — and subtracts their "
                "per-sample mean. So part B and part D currently adjust for DIFFERENT "
                "proliferation controls, and this column is the aligned reading."),
        },
    },

    "comparators_ruled_out_and_why": {
        "expr::S_phase_E2F": (
            "Hallmark E2F Targets is the textbook proliferation axis and is the tempting choice. "
            "⛔ IT IS RULED OUT BECAUSE IT IS A TESTED PREDICTOR IN PART D, not a control — using "
            "one of the reported predictors as the nuisance variable for the others is circular. "
            "It is used below ONLY as the independent yardstick for the validity check."),
        "expr::control_oxphos / control_myogenesis / control_adipogenesis / "
        "control_generic_DNA_repair": (
            "these are UNRELATED controls, not proliferation proxies. Substituting one would not "
            "be choosing a different proliferation control, it would be removing the control."),
        "any gene set not already scored per line": (
            "the committed inputs cache holds per-line SCORES for twelve concepts, not the DepMap "
            "expression matrix, so scoring a new set would require a fetch. Ruled out to keep "
            "this $0 and to keep the comparator inside the committed record."),
    },

    "⭐ validity_check_on_the_comparator_declared_in_advance": {
        "why": (
            "A control is only informative if it MEASURES PROLIFERATION. A control that measures "
            "nothing is trivially easy to beat, and a verdict that flips under it would be an "
            "artefact of a weak control rather than evidence about the mechanism. So the "
            "comparator has to earn the role before its column is read."),
        "test": (
            "Spearman rho of `proliferation_mitotic` against `S_phase_E2F` across the DepMap "
            "lines, with the same statistic for `proliferation_MYC` reported beside it."),
        "declared_floor": 0.30,
        "⛔ what_happens_if_it_fails": (
            "if rho(mitotic, S_phase_E2F) is below +0.30 the comparison is declared VOID and this "
            "artifact reports that the comparator is not a usable proliferation proxy. It does "
            "NOT then report a flipped verdict. The floor is arbitrary but FIXED before the "
            "number; the measured value is reported either way so a reader can apply their own."),
    },

    "⭐ reproduction_check_declared_in_advance": (
        "The harness must reproduce the committed artifact's "
        "`specificity.<predictor>.mean_rho_across_ATR_inhibitors` EXACTLY, for every predictor the "
        "committed artifact carries. ⛔ If any value differs the run is VOID and this artifact "
        "reports the mismatch instead of any verdict — a re-analysis that cannot reproduce the "
        "number it is re-analysing is measuring its own harness."),

    "⛔ what_will_be_reported": (
        "Every mechanism test under EVERY declared comparator, side by side, with `passes` under "
        "each, plus n_passed, `tracks_mechanism` and the grading tier each implies. No comparator "
        "is selected as 'the right one' and no grade is changed. If the verdict does not move, "
        "that is a strengthening of the paper's negative and is reported as one. If it moves, the "
        "paper's central negative is weaker than stated and that is reported at full strength."),
}


# =============================================================================================
# GENE-SET COMPOSITION — the evidence for the comparator CHOICE, computed and committed WITH the
# pre-registration, because it is the argument for C1 rather than a result about C1.
# =============================================================================================
def gene_set_composition(inputs):
    """What each candidate control actually CONTAINS, and what it shares with the incumbent.

    ⛔ A READER MUST BE ABLE TO JUDGE THE INDEPENDENCE BEING CLAIMED, not take it on the word
    'mitotic'. So the overlap is a count against every set part D scores, not a sentence."""
    con = inputs["gene_sets"]["concepts"]
    myc = set(con["proliferation_MYC"]["genes"])
    mit = set(con["proliferation_mitotic"]["genes"])
    comp = {
        "_reading": (
            "n_shared_with_proliferation_MYC is the number of genes a set has in common with the "
            "INCUMBENT control. For a control meant to be mechanism-neutral, the number that "
            "matters is its overlap with the ATR-activation set the paper tests."),
        "proliferation_MYC": {
            "resolved_set": con["proliferation_MYC"]["resolved_set"],
            "library": con["proliferation_MYC"]["library"],
            "n_genes": len(myc)},
        "proliferation_mitotic": {
            "resolved_set": con["proliferation_mitotic"]["resolved_set"],
            "library": con["proliferation_mitotic"]["library"],
            "n_genes": len(mit)},
        "MYC_vs_mitotic": {
            "n_intersection": len(myc & mit),
            "intersection_genes": sorted(myc & mit),
            "n_union": len(myc | mit),
            "jaccard": round(len(myc & mit) / len(myc | mit), 4)},
        "overlap_of_each_control_with_every_scored_concept": {},
    }
    for c, rec in sorted(con.items()):
        g = set(rec.get("genes") or [])
        if not g:
            continue
        comp["overlap_of_each_control_with_every_scored_concept"][c] = {
            "role": rec.get("role"), "n_genes": len(g),
            "n_shared_with_proliferation_MYC": len(g & myc),
            "n_shared_with_proliferation_mitotic": len(g & mit)}
    atr = set(con["ATR_CHK1_activity"]["genes"])
    comp["⛔ the_finding_that_decides_the_choice"] = {
        "set": con["ATR_CHK1_activity"]["resolved_set"],
        "n_genes": len(atr),
        "shared_with_proliferation_MYC": sorted(atr & myc),
        "n_shared_with_proliferation_MYC": len(atr & myc),
        "shared_with_proliferation_mitotic": sorted(atr & mit),
        "n_shared_with_proliferation_mitotic": len(atr & mit),
        "reading": (
            "the incumbent proliferation control shares the replication-origin machinery with the "
            "ATR-activation set part D tests; the proposed comparator shares none of it. That is "
            "a membership fact about the gene lists, not an inference about biology."),
    }
    return comp


def build(prereg_only):
    with open(INPUTS) as fh:
        inputs = json.load(fh)
    out = {
        "_what": ("Whether PUB-ATR part D's four mechanism tests, its verdict and the grading tier "
                  "that reads them survive replacing the MYC-Targets-V1 proliferation control with "
                  "a proliferation control that is not built from MYC's transcriptional output."),
        "_generated_by": "research/modalities/atr_part_d_proliferation_control.py",
        "_cost": "$0 — reads two committed files; no fetch, no CI, no GPU.",
        "_serves": ["PUB-ATR", "RT-ATR-ASSESS", "AUT-PROP-059-11f2347b-8e081d15"],
        "_reads": {
            "inputs_cache": "research/modalities/emc-atr-vulnerability-inputs.json",
            "committed_artifact": "research/modalities/emc-atr-vulnerability.json",
            "statistics_reused_verbatim_from": "research/modalities/emc_atr_vulnerability.py",
        },
        "⛔ _this_changes_no_bar_and_re_grades_nothing": (
            "The committed grade stands. This artifact reports beside it. Re-grading on a new "
            "control is a bar change and is declared, never swapped in silently."),
        "preregistration": PREREGISTRATION,
        "gene_set_composition": gene_set_composition(inputs),
    }
    if prereg_only:
        out["_status"] = ("PRE-REGISTERED, NOT YET COMPUTED. `results` is null on purpose: this "
                          "commit exists so the criterion is on the record before the number.")
        out["results"] = None
    else:
        from _atr_part_d_control_compute import compute  # noqa: E402  (added in the results commit)
        out["_status"] = "COMPUTED"
        out["results"] = compute(inputs)
    return out


def main(argv):
    prereg_only = "--prereg-only" in argv
    out = build(prereg_only)
    if "--check" in argv:
        with open(OUT) as fh:
            on_disk = json.load(fh)
        if json.dumps(on_disk, sort_keys=True) != json.dumps(out, sort_keys=True):
            print("DRIFT: atr-part-d-proliferation-control.json does not reproduce from its "
                  "generator. Rerun: python3 research/modalities/"
                  "atr_part_d_proliferation_control.py")
            return 1
        print("OK: atr-part-d-proliferation-control.json reproduces from its generator")
        return 0
    with open(OUT, "w") as fh:
        json.dump(out, fh, indent=2)
        fh.write("\n")
    print(f"wrote {OUT} ({out['_status'].split(',')[0]})")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
