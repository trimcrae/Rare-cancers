#!/usr/bin/env python3
"""TD1 residual batch 2 — build UNAPPLIED unified diffs for the five PARENT-OWNED shared files.

Nothing in the repository is modified. Each file is copied to a pristine scratch tree, edited by
exact-literal replacement (each anchor must occur EXACTLY ONCE), and a unified diff is written.
No producer, no statistic, no source fetch, no network.
"""
import difflib
import hashlib
import json
import os
import shutil
import sys

SCRATCH = sys.argv[1]
OUTDIR = sys.argv[2]

C = "research/literature/fet-fusion-chaperone-clientship-2026-08-27.json"
G = "research/modalities/census-route-expression-grading.json"
GP = "research/modalities/census_route_expression_grading.py"
MC = "research/manuscripts/modality-census/cancer-modality-census.md"
PUB = "systems/graph/publications.json"

BS = chr(92)
D8 = "⚠ Corrected 2026-09-09 (TD1 focused verification, root adjudication)"
BOUND = ("⚠ Corrected 2026-09-09 (TD1 focused verification, root adjudication) R1: this is the "
         "outcome of ONE dated query string on 2026-08-27, bounded to the items actually inspected "
         "from it. It is not a statement about the whole literature and not evidence that no such "
         "record exists. The query string and hit count above are unchanged.")

EDITS = []


def edit(eid, path, group, field, old, new):
    EDITS.append({"id": eid, "path": path, "group": group, "field": field, "old": old, "new": new})


# ==================================================================== C — clientship search record
edit("C1", C, "R1", "searches_that_returned_nothing_relevant.queries[Q2].outcome",
     "\"outcome\": \"One relevant (PMID 26595521, category d), one Hsp104 yeast paper (PMID 31171724), one MeSH false positive. NO FUS-DDIT3 clientship record exists.\"",
     "\"outcome\": \"One relevant (PMID 26595521, category d), one Hsp104 yeast paper (PMID 31171724), one MeSH false positive. No FUS-DDIT3 clientship record was identified among the items inspected from this query. "
     + BOUND + "\"")

edit("C2", C, "R1", "searches_that_returned_nothing_relevant.queries[Q6].outcome",
     "NR4A3 has NO HSP90 clientship literature. The steroid-receptor chaperone cycle does not transfer to this orphan nuclear receptor on any evidence found here.",
     "No NR4A3 HSP90-clientship record was retrieved by this dated query. " + BOUND
     + " The steroid-receptor chaperone cycle does not transfer to this orphan nuclear receptor on any evidence found here.")

edit("C3", C, "R1", "searches_that_returned_nothing_relevant.queries[Q9].outcome",
     "\"outcome\": \"The whole HSP90-inhibitor literature in Ewing sarcoma is four papers, and all four are category (d) or (b-by-depletion).\"",
     "\"outcome\": \"This query returned four hits, and all four are category (d) or (b-by-depletion). "
     + D8 + " R1: 'the whole HSP90-inhibitor literature in Ewing sarcoma is four papers' is WITHDRAWN — "
     "one query string on one date does not define that literature. The query string and its hit count of 4 are unchanged.\"")

edit("C4", C, "R1", "what_this_changes.the_grade_should_not_move",
     "\"the_grade_should_not_move\": \"◐ PARTLY SUPPORTED is still right, and for the reason already written into it. This seat removes an over-read (the 'YES' of 2026-08-09) and adds one genuinely new positive (SGT1 knockdown destabilises EWS::FLI1, PMID 25985210) and one genuinely new negative (nothing exists for NR4A3 fusions at all). Those cancel: no clientship measurement has been added, and the expression-and-dependency reading the grade is built on is untouched.\"",
     "\"the_grade_should_not_move\": \"◐ PARTLY SUPPORTED is still right, and it rests on its own stated evidence and uncertainty. This seat removes an over-read (the 'YES' of 2026-08-09) and adds one genuinely new positive: SGT1 knockdown destabilises EWS::FLI1 (PMID 25985210). It adds NO measured negative. "
     + D8 + " R1: 'one genuinely new negative (nothing exists for NR4A3 fusions at all)' and the cancellation rationale are WITHDRAWN. Not retrieving a qualifying result is not a measured biological negative and cannot cancel a positive; the two do not offset. What remains true is narrower: no clientship MEASUREMENT has been added in either direction, and the expression-and-dependency reading the grade is built on is untouched.\"")

edit("C5", C, "R1", "what_this_changes.falsifier_F5_of_the_dependency_manuscript",
     "\"falsifier_F5_of_the_dependency_manuscript\": \"F5 reads 'the chimera's clientship is untested', killed by 'a published co-immunoprecipitation for any FET-family fusion protein'. F5 SURVIVES: no such co-immunoprecipitation exists. But the manuscript's §5 statement that the literature question was attempted and not answered is now stale and is corrected in this cycle.\"",
     "\"falsifier_F5_of_the_dependency_manuscript\": \"" + D8 + " R1: RETIRED. The old falsifier reading — 'F5 SURVIVES: no such co-immunoprecipitation exists' — is withdrawn and carries NO current authority. It asserted a global absence this search cannot support, and it does not describe the manuscript's corrected update condition. The authoritative current statement is U5 of research/manuscripts/dependency/emc-transcriptional-proteostatic-dependency.md, which distinguishes a binding assay published AFTER 2026-08-27 (updating the present evidence inventory) from an earlier qualifying item inside the searched set (which would expose an extraction or classification error here), and which keeps the separate warning that evidence in any FET fusion does not establish EWSR1/TAF15::NR4A3 clientship in EMC.\"")

edit("C6", C, "R1", "evidence[PMID=28383167].what_it_establishes",
     "\"what_it_establishes\": \"The only chaperone-family record that exists in the EMC literature at all: HSPA8 (HSC70) occurs as a 5' fusion partner of NR4A3 in one reported case.\"",
     "\"what_it_establishes\": \"The one chaperone-family record retrieved for EMC by this dated search: HSPA8 (HSC70) occurs as a 5' fusion partner of NR4A3 in one reported case. "
     + D8 + " R1: 'the only chaperone-family record that exists in the EMC literature at all' is WITHDRAWN — this search cannot establish exhaustive uniqueness.\"")

edit("C7", C, "R1", "evidence[PMID=31171724].what_it_establishes",
     "\"what_it_establishes\": \"The closest thing in the literature to a chaperone acting directly on FET FUSION proteins: two different FET fusions are handled as aggregation substrates by a disaggregase.\"",
     "\"what_it_establishes\": \"A relevant example found by this search of a chaperone acting directly on FET FUSION proteins: two different FET fusions are handled as aggregation substrates by a disaggregase. "
     + D8 + " R1: 'the closest thing in the literature' is WITHDRAWN — no comprehensive ranking of the literature was performed.\"")

edit("C8", C, "R1", "what_this_changes.the_rationale_needs_one_correction",
     "The only fusion oncoprotein whose chaperone clientship HAS been solved structurally is handled through its DNA-BINDING DOMAIN (PMID 26706127)",
     "The fusion oncoprotein identified by this search as having its chaperone clientship solved structurally — AML1-ETO, the non-FET comparator — is handled through its DNA-BINDING DOMAIN (PMID 26706127). "
     + D8 + " R1: 'the only fusion oncoprotein whose chaperone clientship HAS been solved structurally' is WITHDRAWN; this search establishes no exhaustive uniqueness. The comparator is")

edit("C9", C, "R1", "evidence[PMID=25036637].category",
     "\"category\": \"CLIENT SCREEN — read in full; it neither includes nor excludes the FET proteins in its body\"",
     "\"category\": \"CLIENT SCREEN — the retrieval record declares a full-text read on 2026-08-27; the original article was NOT inspectable in the 2026-09-09 focused review, so that declaration is retained as dated provenance and is not used here as verified full-text content. On the retained record it neither includes nor excludes the FET proteins.\"")

edit("C10", C, "R1", "evidence[PMID=25036637].what_it_does_NOT_establish",
     "\"what_it_does_NOT_establish\": \"⚠ The paper's body names no FET protein. Whether FUS, EWSR1 or TAF15 was in the 800-protein query panel at all is NOT answerable from the text;",
     "\"what_it_does_NOT_establish\": \"⚠ " + D8 + " R1: 'the paper's body names no FET protein' is retained ONLY as the dated 2026-08-27 retrieval declaration and is NOT asserted here as verified full-text absence — the original was not inspectable in the focused review. Whether FUS, EWSR1 or TAF15 was in the 800-protein query panel at all is NOT answerable from the retained material;")

edit("C11", C, "R1", "open_questions_stated_as_unknown[0]",
     "\"UNKNOWN — whether FUS, EWSR1 or TAF15 appear at all in the query panel of the one systematic human chaperone client screen (PMID 25036637). Its full text was read in this seat and names no FET protein; the panel membership and scores live in the deposited dataset",
     "\"UNKNOWN — whether FUS, EWSR1 or TAF15 appear at all in the query panel of the one systematic human chaperone client screen (PMID 25036637) retrieved by this search. " + D8
     + " R1: this seat's 2026-08-27 declaration that its full text was read and names no FET protein is preserved as dated provenance; the original was not inspectable in the focused review, so full-text absence is NOT asserted here, and SUPPLEMENT MEMBERSHIP REMAINS UNKNOWN. The panel membership and scores live in the deposited dataset")

edit("C12", C, "R1", "open_questions_stated_as_unknown[3]",
     "\"UNKNOWN — whether the EWS::FLI1 depletion seen under HSP90 inhibition is post-translational at all. None of the three papers reports a cycloheximide chase, a proteasome-block rescue or an mRNA measurement alongside the immunoblot, so a transcriptional route through the fusion's own autoregulated locus is not excluded.\"",
     "\"UNKNOWN — whether the EWS::FLI1 depletion seen under HSP90 inhibition is post-translational at all. " + D8
     + " R1: the earlier assertion that NONE of the three papers reports a cycloheximide chase, a proteasome-block rescue or an mRNA measurement is WITHDRAWN as a claim about those articles. Whether those assays were performed is UNVERIFIED from the originals available here: the retained curated extracts do not report them, and the originals were not inspectable. Either way the retained evidence does not establish a post-translational mechanism, and a transcriptional route through the fusion's own autoregulated locus is not excluded.\"")

edit("C13", C, "R1", "searches_that_returned_nothing_relevant.queries[Q1].outcome",
     "\"outcome\": \"PMID 36495678, PMID 31025088, PMID 27863422 — no binding assay in any of them.\"",
     "\"outcome\": \"PMID 36495678, PMID 31025088, PMID 27863422 — no binding assay was identified in the items inspected from this query. " + BOUND + "\"")

edit("C14", C, "R1", "searches_that_returned_nothing_relevant.queries[Q4].outcome",
     "one (PMID 24251390) is a RETRACTED review and is not cited here; none reports a FET protein bound to HSP90.\"",
     "one (PMID 24251390) is a RETRACTED review and is not cited here; none of the items inspected from this query reports a FET protein bound to HSP90. " + BOUND + "\"")

edit("C15", C, "R1", "searches_that_returned_nothing_relevant.queries[Q5].outcome",
     "\"outcome\": \"All six already reviewed above. Neither partner protein is independently documented as an HSP90 client.\"",
     "\"outcome\": \"All six already reviewed above. Neither partner protein was found independently documented as an HSP90 client among the items inspected from this query. " + BOUND + "\"")

edit("C16", C, "R1", "searches_that_returned_nothing_relevant.queries[Q12].outcome",
     "\"outcome\": \"Surfaced the AML1-ETO/TRiC comparator pair. NO HSP70-family or co-chaperone binding record for any FET fusion.\"",
     "\"outcome\": \"Surfaced the AML1-ETO/TRiC comparator pair. No HSP70-family or co-chaperone binding record for any FET fusion was identified among the items inspected from this query. " + BOUND + "\"")

edit("C17", C, "R1", "searches_that_returned_nothing_relevant.queries[Q14].outcome",
     "\"outcome\": \"The route by which the AML1-ETO comparator was found. No FET-fusion binding record appears in it.\"",
     "\"outcome\": \"The route by which the AML1-ETO comparator was found. No FET-fusion binding record was identified among the items inspected from this query's 43 hits, which were not all individually screened. " + BOUND + "\"")

edit("C18", C, "R1", "retrieval.full_text_read[0] — current-authority status",
     "\"PMC4450263 (PMID 25985210) — read in full\"",
     "\"PMC4450263 (PMID 25985210) — read in full on 2026-08-27. ⚠ HISTORICAL PROVENANCE, not current authority: " + D8
     + " R1. This entry records what this seat did on that date. It does not by itself verify any full-text content, and it does not reinstate any interpretation withdrawn elsewhere in this file.\"")

edit("C19", C, "R1", "_supersedes.what_changed — current-authority status",
     "The 2026-08-09 record is left exactly as written — it is a dated retrieval, and corrections belong in an appendix rather than inline.\"",
     "The 2026-08-09 record is left exactly as written — it is a dated retrieval, and corrections belong in an appendix rather than inline. ⚠ HISTORICAL PROVENANCE, not current authority: "
     + D8 + " R1. Where this block and the dated corrections below disagree, the dated corrections govern, and the authoritative bounded statement of what this search did and did not identify is `verdict.one_sentence` together with the per-query outcomes as corrected.\"")

# ==================================================================== G / GP — census route grading
G_ACTION_OLD = ("hold: elevated on abundance in archival EMC-labelled specimens; broad non-selective "
                "dependency in non-EMC cancer lines; unpaired, and unmeasured in EMC. ⚠ Corrected "
                "2026-09-08 (TD1 final review, root adjudication) F1/F3: " + BS + "\"closed on the axis that "
                "matters" + BS + "\" is withdrawn.")
G_ACTION_NEW = ("hold: elevated on abundance in archival EMC-labelled specimens; broad binary dependency "
                "in the screened non-EMC cancer lines, with selectivity UNRESOLVED; unpaired, and "
                "unmeasured in EMC. ⚠ Corrected 2026-09-08 (TD1 final review, root adjudication) F1/F3: "
                + BS + "\"closed on the axis that matters" + BS + "\" is withdrawn. " + D8 + " R2: " + BS + "\"non-selective" + BS + "\" is "
                "withdrawn — a cancer-versus-cancer screen measured no normal-tissue comparison and no "
                "graded response, so it does not show absence of selectivity.")

G_OBS_ADD = (" " + D8 + " R2: GPL3290 is WITHHELD from biological corroboration under the TD1 "
             "interpretation hold on its reference design (10 EMC CRH-mRNA, 3 DFSP CRH, 3 GIST UHR "
             "references), so the biological expression support for this route rests on GPL6244 alone. "
             "All displayed numbers, requested and readable gene counts and cohort memberships are "
             "retained unchanged; what is withdrawn is GPL3290's status as corroboration.")

G_VERDICT_ADD = (" " + D8 + " R2: this verdict rests on GPL6244 alone; the GPL3290 record is retained "
                 "and displayed but is withheld from biological corroboration (see `observed`).")

edit("G1", G, "R2a", "routes.RT-TXN-CDK.route_action", G_ACTION_OLD, G_ACTION_NEW)
edit("G2", G, "R2b", "routes.RT-CHAPERONE.observed",
     "not absence of elevation, not an equivalence result, and not contradictory biology.",
     "not absence of elevation, not an equivalence result, and not contradictory biology." + G_OBS_ADD)
edit("G3", G, "R2b", "routes.RT-CHAPERONE.verdict",
     "F4: \\\"the stress-response arm contradicts it\\\" is withdrawn.",
     "F4: \\\"the stress-response arm contradicts it\\\" is withdrawn." + G_VERDICT_ADD)

edit("GP1", GP, "R2a", "routes['RT-TXN-CDK']['route_action'] source literal",
     '        "route_action": ("hold: elevated on abundance in archival EMC-labelled specimens; broad non-selective "\n'
     '                         "dependency in non-EMC cancer lines; unpaired, and unmeasured in EMC. ⚠ Corrected "\n'
     '                         "2026-09-08 (TD1 final review, root adjudication) F1/F3: \\"closed on the axis that "\n'
     '                         "matters\\" is withdrawn."),\n',
     '        "route_action": ("hold: elevated on abundance in archival EMC-labelled specimens; broad binary dependency "\n'
     '                         "in the screened non-EMC cancer lines, with selectivity UNRESOLVED; unpaired, and "\n'
     '                         "unmeasured in EMC. ⚠ Corrected 2026-09-08 (TD1 final review, root adjudication) F1/F3: "\n'
     '                         "\\"closed on the axis that matters\\" is withdrawn. ⚠ Corrected 2026-09-09 (TD1 focused "\n'
     '                         "verification, root adjudication) R2: \\"non-selective\\" is withdrawn — a "\n'
     '                         "cancer-versus-cancer screen measured no normal-tissue comparison and no graded "\n'
     '                         "response, so it does not show absence of selectivity."),\n')

edit("GP2", GP, "R2b", "routes['RT-CHAPERONE']['observed'] source literal",
     '                     "for this curated list — not absence of elevation, not an equivalence result, and not "\n'
     '                     "contradictory biology."),\n',
     '                     "for this curated list — not absence of elevation, not an equivalence result, and not "\n'
     '                     "contradictory biology. ⚠ Corrected 2026-09-09 (TD1 focused verification, root "\n'
     '                     "adjudication) R2: GPL3290 is WITHHELD from biological corroboration under the TD1 "\n'
     '                     "interpretation hold on its reference design (10 EMC CRH-mRNA, 3 DFSP CRH, 3 GIST UHR "\n'
     '                     "references), so the biological expression support for this route rests on GPL6244 "\n'
     '                     "alone. All displayed numbers, requested and readable gene counts and cohort "\n'
     '                     "memberships are retained unchanged; what is withdrawn is GPL3290\'s status as "\n'
     '                     "corroboration."),\n')

edit("GP3", GP, "R2b", "routes['RT-CHAPERONE']['verdict'] source literal",
     '                    "adjudication) F4: \\"the stress-response arm contradicts it\\" is withdrawn."),\n',
     '                    "adjudication) F4: \\"the stress-response arm contradicts it\\" is withdrawn. ⚠ Corrected "\n'
     '                    "2026-09-09 (TD1 focused verification, root adjudication) R2: this verdict rests on "\n'
     '                    "GPL6244 alone; the GPL3290 record is retained and displayed but is withheld from "\n'
     '                    "biological corroboration (see `observed`)."),\n')

# ==================================================================== MC — census echo paragraph
edit("MC1", MC, "R2a", "§3.1 pan-essential phrasing (MC:184-185)",
     "against it: across 91 screened sarcoma lines, CDK7 and CDK9 are dependencies in 100% of them, which is\nthe definition of pan-essential.",
     "against it: across 91 screened sarcoma lines, CDK7 and CDK9 are dependencies in 100% of them — broad\nbinary dependency across the screened non-EMC cancer lines.")

edit("MC2", MC, "R2a", "§3.1 normal-tissue / cytotoxicity inference (MC:190-197)",
     " is real, but it buys\nno window against normal tissue, because every sarcoma line needs these genes regardless of fusion\n"
     "status. This closes the class on the evidence available here — transcript-level and small — as a\n"
     "de-prioritisation with a stated basis, not a proof of impossibility\n"
     "([`census-route-expression-grading.json`](../../modalities/census-route-expression-grading.json) →\n"
     "`routes.RT-TXN-CDK`). ⚠ **The cytotoxicity concern the first version of this row already raised turned\n"
     "out to be exactly the mechanism that closed it**, not a separate caveat sitting beside a surviving route.",
     " is real. ⛔ **Corrected 2026-09-09 (TD1\n"
     "focused verification, root adjudication) R2.** Two further readings of this row are **withdrawn**.\n"
     "*Withdrawn:* that the elevation *\"buys no window against normal tissue, because every sarcoma line\n"
     "needs these genes regardless of fusion status\"*. The 91-line summary is a **binary** dependency call\n"
     "in a **cancer-versus-cancer** comparison: it supplies no normal-tissue observation, no graded\n"
     "drug-response analysis and no fusion-status-stratified result, so it does **not** show absence of a\n"
     "therapeutic window and does **not** show fusion independence. *Withdrawn:* that *\"the cytotoxicity\n"
     "concern the first version of this row already raised turned out to be exactly the mechanism that\n"
     "closed it\"*. No mechanism was measured here; broad binary dependency is not a demonstrated cytotoxic\n"
     "mechanism, and the class's toxicity record remains a stated prior concern, not a finding of this\n"
     "screen. What the evidence available here supports is a **de-prioritisation with a stated basis** —\n"
     "transcript-level and small, with an EMC dependency that is **unmeasured and therefore unknown, not\n"
     "absent** — and not a proof of impossibility\n"
     "([`census-route-expression-grading.json`](../../modalities/census-route-expression-grading.json) →\n"
     "`routes.RT-TXN-CDK`).")

# ==================================================================== PUB — publication graph entry
edit("PUB1", PUB, "R2c", "PUB-TXN-DEPENDENCY.outcome_potential_why",
     "\"outcome_potential_why\": \"Two unpaired evidence streams, both unresolved for this disease and resolvable only by a perturbation observation in a fusion-positive EMC model. ⚠ Corrected 2026-09-08 (TD1 final review, root adjudication) F1: the 'disagree in opposite directions' framing is withdrawn.\"",
     "\"outcome_potential_why\": \"Two unpaired evidence streams, both unresolved for this disease. ⚠ Corrected 2026-09-08 (TD1 final review, root adjudication) F1: the 'disagree in opposite directions' framing is withdrawn. "
     + D8 + " R2: 'resolvable only by a perturbation observation in a fusion-positive EMC model' is WITHDRAWN — it compressed distinct questions into one purported resolution route. What is actually missing is EMC-SPECIFIC PERTURBATION EVIDENCE: no EMC-labelled model contributes CRISPR gene-effect data to the release read here. These remain SEPARATE questions that such an observation alone would not settle: whether the chimera is a chaperone CLIENT (a binding question); the MECHANISM of any observed depletion; tumour-versus-NORMAL-TISSUE selectivity, which no cancer-versus-cancer comparison can supply; the REFERENCE COMPARABILITY of the GPL3290 records, which are withheld from biological corroboration; and the SCOPE of the dated literature search. Each requires evidence of its own kind.\"")


def main():
    os.makedirs(SCRATCH, exist_ok=True)
    os.makedirs(OUTDIR, exist_ok=True)
    by_path, ledger, failed = {}, [], []
    for e in EDITS:
        by_path.setdefault(e["path"], []).append(e)
    for path, edits in by_path.items():
        with open(path, encoding="utf-8") as fh:
            original = fh.read()
        text = original
        rows = []
        for e in edits:
            n = text.count(e["old"])
            if n != 1:
                failed.append({"id": e["id"], "path": path, "occurrences": n})
                continue
            text = text.replace(e["old"], e["new"], 1)
            rows.append({"id": e["id"], "group": e["group"], "field": e["field"],
                         "old_bytes": len(e["old"].encode()), "new_bytes": len(e["new"].encode()),
                         "old_sha256": hashlib.sha256(e["old"].encode()).hexdigest(),
                         "new_sha256": hashlib.sha256(e["new"].encode()).hexdigest()})
        base = path.replace("/", "__")
        with open(os.path.join(SCRATCH, base), "w", encoding="utf-8", newline="") as fh:
            fh.write(text)
        diff = "".join(difflib.unified_diff(
            original.splitlines(keepends=True), text.splitlines(keepends=True),
            fromfile="a/" + path, tofile="b/" + path, n=3))
        with open(os.path.join(OUTDIR, base + ".patch"), "w", encoding="utf-8", newline="") as fh:
            fh.write(diff)
        ledger.append({"path": path, "patch": base + ".patch",
                       "original_bytes": len(original.encode()),
                       "original_sha256": hashlib.sha256(original.encode()).hexdigest(),
                       "patched_bytes": len(text.encode()),
                       "patched_sha256": hashlib.sha256(text.encode()).hexdigest(),
                       "n_edits": len(rows), "edits": rows})
    out = {"status": "FAILED" if failed else "BUILT", "anchors_not_unique": failed,
           "n_files": len(ledger), "n_edits": sum(f["n_edits"] for f in ledger), "files": ledger}
    json.dump(out, sys.stdout, indent=2, ensure_ascii=False)
    print()
    with open(os.path.join(OUTDIR, "EDIT-LEDGER.json"), "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
