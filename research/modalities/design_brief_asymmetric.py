#!/usr/bin/env python3
"""`Q16` — THE DESIGN BRIEF, RESTATED ASYMMETRICALLY IN ITS HARDER MEASURED FORM.

★ THE ONE-LINE CHANGE, AND WHY IT IS NOT A SOFTENING.

    was:  hard constraint — spare NR4A1;  SOFT constraint — spare NR4A2 as far as the handles allow,
          and carry the residual as a DISCLOSED, UNSIZED EXPOSURE question.

    now:  HARD vs NR4A1;  HARD-BUT-LOWER-PRIORITY vs NR4A2.  **BOTH MOLECULAR.**

⛔ THE EXPOSURE LEVER IS GONE, AND IT WAS REMOVED BY MEASUREMENT RATHER THAN BY JUDGEMENT.
`nr4a2-sparing-bound.json` bounded the NR4A2 half from two public sources and both readings point the same
way. **(a)** The repository's flagged-UNCONFIRMED *"Nurr1 single-KO is neonatal-lethal"* RESOLVED to a
citation — `MP:0011087`, *neonatal lethality, complete penetrance*, on three independent `Nr4a2`-only null
alleles, PMIDs 9092472 and 9608532 — so the constraint has a **floor with evidence under it** and is no
longer a precaution. **(b)** Across 51 tissues with all three paralogues quantified, NR4A2 and NR4A3 are
**co-expressed in 47**, NR4A2 is **dominant in 0** and **unbuffered in 0**. ⇒ **tissue distribution cannot
separate target from anti-target, so the selectivity has to be MOLECULAR** — and the previous brief's escape
hatch ("treat the residual as an exposure question") is not available, because there is no tissue in which
the anti-target is present and the target is not.

⚠ AND THE DIRECTION IS THE OPPOSITE OF WHAT THE BRIEF ASSUMED. The premise that NR4A2 marks the tissue
where paralogue compensation is least available is **not supported** by that table. ⛔ It is **not refuted
either**, and the reason is stated rather than buried: a bulk tissue average dilutes the substantia nigra
pars compacta — of order 10^5 neurons — to invisibility, so a low pooled nTPM is NOT evidence against a
dopaminergic requirement and this artifact must never be quoted that way. What the table supports is the
converse, which is the direction the brief needs: wherever NR4A2 is present above the cut, a non-sparing
degrader would act on it, and that count is a **floor on exposure breadth**.

────────────────────────────────────────────────────────────────────────────────────────────────────────
⭑ AND THE ASYMMETRY NOW HAS A SECOND, INDEPENDENT MEASUREMENT — WHICH THE BRIEF MUST CARRY WITH ITS OWN
  SENSITIVITY, NOT AS AN UNQUALIFIED WORD.

`paralogue-pocket-asymmetric-read.json` (2026-08-06) split a previously CONJOINED verdict along
`RT-ASYMMETRIC`'s own mandatory / best-effort axes, and the two halves got different answers:

    NR4A1 (MANDATORY axis)   — SEPARATED at replicate granularity
    NR4A2 (BEST-EFFORT axis) — RANKED, but replicate ranges OVERLAP

⛔ **AND ITS OWN `lead_status` IS *"LIVE BUT DEMOTED — the asymmetry is real, the word SEPARATED is not
carryable"*,** because the NR4A1 separation does **not** survive the contested `C2` cavity-selection rule.
So the brief carries the **asymmetry** and does **not** carry the word: three independent cautions travel
with it, all measured in that artifact — the contested-`C2` re-evaluation flips it, the design-effect
-corrected Wilson intervals overlap, and at 3 vs 3 replicates the exact test's FLOOR is p = 0.05 one-sided
(0.10 Holm-adjusted over two paralogues), so no outcome of this design can clear α = 0.05 family-wise.

────────────────────────────────────────────────────────────────────────────────────────────────────────
⛔ POSE MARGINALISATION. Neither half of this brief is pose-conditional and that is worth stating rather
than assuming: the NR4A2 bound is sequence/registry/expression data, and the pocket contrast is a
frame-fraction over unbiased ensembles, not a docked pose. `path-family-synthesis.md` §4's inheritance
table records both of the rows this brief descends from as inheriting **neither `R3` nor `R5`** — which is
exactly why the brief could be restated on a day when the second pose method returned
`R5_resolved: false`. ⇒ **No sentence in this brief may be re-specialised to a pose, a vector or a
construct**, and the pocket-contrast half is a RANKING on opening frequency, never a per-molecule claim.

⛔ WHAT THIS BRIEF DOES NOT SAY. It is a design TARGET assembled from committed readings. It contains no
free energy, no ΔG_open, no margin, no ratio and no window; it asserts nothing about binding, reactivity,
degradation, proteome-wide selectivity, efficacy, safety, a therapeutic window or clinical readiness. A
germline knockout bounds DEVELOPMENTAL, COMPLETE, LIFELONG loss; a degrader is ADULT, TRANSIENT and
INCOMPLETE loss, and no source read anywhere here measures that — so a knockout phenotype sets the
**ceiling of concern**, never the expected effect of a molecule.

Outputs: nr4a3-design-brief-asymmetric.json (+ .md)
"""
from __future__ import annotations

import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
if HERE not in sys.path:                       # so the shared frontmatter helper imports from any cwd
    sys.path.insert(0, HERE)

SPARING = os.path.join(HERE, "nr4a2-sparing-bound.json")
ASYM = os.path.join(HERE, "paralogue-pocket-asymmetric-read.json")
POSE_SECOND = os.path.join(HERE, "pose-second-method.json")
OUT = os.path.join(HERE, "nr4a3-design-brief-asymmetric.json")


def _walk(o):
    yield o
    if isinstance(o, dict):
        for v in o.values():
            yield from _walk(v)
    elif isinstance(o, list):
        for v in o:
            yield from _walk(v)


def nr4a2_bound(doc):
    """The measured half — every figure READ, none typed."""
    g = doc["verdict"]["gates"]
    b3 = g["B3_tissue_overlap_measured"]
    b2 = g["B2_lethality_claim_resolved_to_a_citation"]
    term = (b2["survival_or_viability_terms_found"] or [{}])[0]
    return {
        "_source": os.path.relpath(SPARING, REPO),
        "decision": doc["verdict"]["decision"],
        "the_floor": {
            "mp_term": term.get("term"),
            "mp_id": term.get("mp_id"),
            "pubmed_ids": term.get("pubmed_ids"),
            "genotypes": term.get("genotypes"),
            "n_single_gene_annotations": g["B1_nr4a2_single_ko_phenotyped"]["n_single_gene_annotations"],
        },
        "the_exposure_lever": {
            "n_tissues": b3["n_tissues"],
            "counts": b3["counts"],
            "source": b3["source"],
            "⛔_reading": "NR4A2 and NR4A3 co-express in %d of %d tissues; NR4A2 is DOMINANT in %d and "
                         "UNBUFFERED in %d. There is no tissue in which the anti-target is present and "
                         "the target is not, so tissue distribution cannot separate them and the "
                         "selectivity has to be MOLECULAR."
                         % (b3["counts"]["nr4a2_and_nr4a3_co_expressed"], b3["n_tissues"],
                            b3["counts"]["nr4a2_dominant"], b3["counts"]["nr4a2_unbuffered"]),
        },
        "⚠_the_limit_that_travels_with_it": doc["caveat_that_must_travel_with_any_result"],
        "⚠_what_the_table_may_NOT_be_quoted_for": (
            "⛔ THIS TABLE IS NOT EVIDENCE AGAINST A DOPAMINERGIC REQUIREMENT AND MAY NEVER BE QUOTED AS "
            "SUCH. A bulk tissue average dilutes the substantia nigra pars compacta — of order 10^5 "
            "neurons — to invisibility, so a low pooled nTPM in a brain region says nothing about it. "
            "What the table measures is exposure BREADTH: wherever NR4A2 is present above the cut, a "
            "non-sparing degrader would act on it."),
        "what_would_reopen_the_exposure_half": "single-cell or region-resolved expression, and a "
                                               "CNS-exposure measurement for a real candidate molecule. "
                                               "Neither exists here.",
    }


def asymmetry_read(doc):
    """The second, independent measurement — carried WITH its sensitivity, never as a bare word."""
    per = doc["per_paralogue"]
    v = doc["verdict"]
    out = {
        "_source": os.path.relpath(ASYM, REPO),
        "lead_status": v["lead_status"],
        "headline": v["headline"],
        "pooled_verdict_it_replaces": v["pooled_verdict_it_replaces"],
        "the_pooled_verdict_was_driven_by": v["the_pooled_verdict_is_driven_by"],
        "by_paralogue": {},
        "⛔_what_it_does_not_license": v["⛔_what_this_still_does_not_license"],
    }
    for par, r in per.items():
        c2 = r.get("sensitivity_to_the_contested_C2_rule", {})
        wil = r.get("design_corrected_wilson_overlap", {})
        perm = r.get("exact_ranksum_permutation", {})
        frag = r.get("fragility_one_more_replicate", {})
        out["by_paralogue"][par] = {
            "axis": r["rt_asymmetric_axis"],
            "verdict_under_the_frozen_rule": r["verdict_under_the_frozen_rule"]["verdict"],
            "separated_under_the_frozen_rule": r["verdict_under_the_frozen_rule"]["separated"],
            "cliffs_delta": r.get("effect_size_cliffs_delta", {}).get("delta"),
            "★_three_cautions": {
                "contested_C2_rule": {
                    "verdict_under_the_alternative_ordering": c2.get("verdict", {}).get("verdict"),
                    "survives_the_rule_change": c2.get("survives_the_rule_change"),
                },
                "design_effect_corrected_wilson": {
                    "intervals_overlap": wil.get("overlap"),
                    "uncorrected_would_have_said_overlap": (
                        wil.get("uncorrected_would_have_said", {}).get("overlap")),
                },
                "design_floor": {
                    "p_one_sided": perm.get("p_one_sided_a_greater"),
                    "p_one_sided_FLOOR": perm.get("p_one_sided_floor"),
                    "holm_adjusted_over_2_paralogues": perm.get("p_one_sided_holm_adjusted_over_2_paralogues"),
                    "⚠": "at 3 vs 3 NO outcome can return p < 0.05 one-sided, and no Holm-adjusted p "
                         "below 0.10 over a family of two. A p at the floor is the DESIGN's ceiling, "
                         "never 'just significant'.",
                },
            },
            "fragility_margin_in_replicate_SD": frag.get("margin_in_units_of_nr4a3_replicate_sd"),
        }
    return out


def build_brief(sparing, asym):
    """★ THE BRIEF ITSELF — assembled from the two readings, with every qualifier attached to the clause
    it qualifies rather than gathered into a footnote."""
    n1 = asym["by_paralogue"].get("NR4A1", {})
    n2 = asym["by_paralogue"].get("NR4A2", {})
    lever = sparing["the_exposure_lever"]
    floor = sparing["the_floor"]
    return {
        "one_line": "HARD vs NR4A1; HARD-BUT-LOWER-PRIORITY vs NR4A2. BOTH MOLECULAR.",
        "clauses": [
            {
                "id": "B1",
                "constraint": "NR4A1 — HARD",
                "text": "Spare NR4A1. The bound is a NAMED ANTI-TARGET GENOTYPE — the combined "
                        "Nr4a1-/-;Nr4a3-/- mouse (postnatal lethality, complete penetrance), which is "
                        "precisely the pair a non-selective NR4A3 degrader RECONSTITUTES. Single nulls "
                        "do not do it.",
                "why_it_outranks_B2": "it is a combination genotype a molecule can create, not a "
                                      "developmental loss no molecule delivers.",
                "instrument_reading": n1.get("verdict_under_the_frozen_rule"),
                "⚠_sensitivity": "this is the MANDATORY axis and its separation does NOT survive the "
                                 "contested C2 rule (%s under the alternative ordering), the "
                                 "design-effect-corrected Wilson intervals %s, and the exact test sits "
                                 "at its design FLOOR. Carry the asymmetry; do not carry the word "
                                 "SEPARATED."
                                 % (n1.get("★_three_cautions", {}).get("contested_C2_rule", {})
                                    .get("verdict_under_the_alternative_ordering"),
                                    "OVERLAP" if (n1.get("★_three_cautions", {})
                                                  .get("design_effect_corrected_wilson", {})
                                                  .get("intervals_overlap")) else "do not overlap"),
            },
            {
                "id": "B2",
                "constraint": "NR4A2 — HARD BUT LOWER PRIORITY",
                "text": "Spare NR4A2. ⛔ NOT a soft constraint: complete germline Nr4a2 loss produces %s "
                        "(%s), primary-cited to PMID %s across %d independent null alleles, so there is "
                        "a FLOOR under how much sparing is required and it is evidenced rather than "
                        "precautionary. It ranks BELOW NR4A1 only because NR4A1's bound is a "
                        "combination genotype a degrader reconstitutes, while this one is complete "
                        "developmental loss, which no degrader delivers."
                        % (floor.get("mp_term"), floor.get("mp_id"),
                           " / ".join(floor.get("pubmed_ids") or []),
                           len(floor.get("genotypes") or [])),
                "instrument_reading": n2.get("verdict_under_the_frozen_rule"),
                "⚠_sensitivity": "this is the BEST-EFFORT axis and its replicate ranges OVERLAP even "
                                 "under the frozen rule — it is a RANKING with a stated effect size "
                                 "(Cliff's delta %s), never a separation."
                                 % n2.get("cliffs_delta"),
            },
            {
                "id": "B3",
                "constraint": "BOTH MOLECULAR — the exposure lever is withdrawn",
                "text": "Neither half may be discharged by tissue distribution. Across %d tissues with "
                        "all three paralogues quantified, NR4A2 and NR4A3 are co-expressed in %d, "
                        "NR4A2 is dominant in %d and unbuffered in %d. There is no tissue in which the "
                        "anti-target is present and the target is not. ⇒ selectivity has to be "
                        "MOLECULAR, and the residual is DISCLOSED rather than discharged."
                        % (lever["n_tissues"], lever["counts"]["nr4a2_and_nr4a3_co_expressed"],
                           lever["counts"]["nr4a2_dominant"], lever["counts"]["nr4a2_unbuffered"]),
                "⚠_sensitivity": sparing["⚠_what_the_table_may_NOT_be_quoted_for"],
                "what_would_reopen_it": sparing["what_would_reopen_the_exposure_half"],
            },
            {
                "id": "B4",
                "constraint": "THE CEILING ON ALL THREE",
                "text": "A germline knockout bounds DEVELOPMENTAL, COMPLETE, LIFELONG loss. A degrader "
                        "is ADULT, TRANSIENT, INCOMPLETE loss of a protein, and no source read here "
                        "measures that. So every genotype above sets a CEILING OF CONCERN, never an "
                        "expected effect — and an absent knockout record is an absence of evidence, "
                        "not evidence of tolerability.",
                "⚠_sensitivity": sparing["⚠_the_limit_that_travels_with_it"],
            },
        ],
        "⛔_superseded_retained": [
            "'NR4A2 — a SOFT constraint … carry the residual as a DISCLOSED, UNSIZED EXPOSURE question' "
            "— the exposure half is withdrawn by measurement (47 of 51 tissues co-expressed, 0 dominant, "
            "0 unbuffered), and the constraint is bounded rather than soft.",
            "'NR4A2 — UNBOUNDED, in both directions' — bounded 2026-08-03 by MGI single-gene records.",
            "'treat the residual as an exposure question rather than a chemistry one' — the lever the "
            "phrase hands off to does not exist.",
            "reporting the paralogue pocket contrast as ONE conjoined verdict — it is two, on two axes, "
            "with two different answers.",
            "the word SEPARATED, unqualified, on the NR4A1 axis — it does not survive the contested C2 "
            "rule and the artifact's own lead_status says so.",
        ],
        "⛔_this_brief_contains_no": ["free energy", "ΔG_open or any opening penalty",
                                     "selectivity margin, ratio or window",
                                     "claim about binding, reactivity, degradation, proteome-wide "
                                     "selectivity, efficacy, safety, a therapeutic window or clinical "
                                     "readiness",
                                     "pose-, vector- or construct-specific statement"],
    }


def _pose_inheritance():
    if not os.path.exists(POSE_SECOND):
        return {"read": False}
    d = json.load(open(POSE_SECOND, encoding="utf-8"))

    def dig(key):
        for v in _walk(d):
            if isinstance(v, dict) and key in v:
                return v[key]
        return None
    return {"read": True, "R5_resolved": dig("R5_resolved"), "outcome": dig("outcome"),
            "_source": os.path.relpath(POSE_SECOND, REPO)}


def build():
    sp = nr4a2_bound(json.load(open(SPARING, encoding="utf-8")))
    az = asymmetry_read(json.load(open(ASYM, encoding="utf-8")))
    return {
        "_title": "Q16 — the design brief, restated ASYMMETRICALLY in its harder measured form",
        "_status": "A DESIGN TARGET assembled from committed readings. $0 CPU, pure stdlib, no new "
                   "compute. No free energy, no margin, no ratio, no window. Nothing here is a claim "
                   "about binding, reactivity, degradation, proteome-wide selectivity, efficacy, "
                   "safety, a therapeutic window or clinical readiness.",
        "_what_changes": "the brief's SHAPE, not any measurement. No result is withdrawn and no "
                         "instrument has to pass for it to be adopted — a narrowing of a requirement "
                         "inherits no instrument.",
        "★_the_brief": build_brief(sp, az),
        "the_NR4A2_bound": sp,
        "★_the_asymmetry_read": az,
        "_pose_marginalisation": {
            "rule": "no sentence in this brief may be re-specialised to a pose, a vector or a construct.",
            "why_it_is_nonetheless_statable_today": "neither half is pose-conditional — the NR4A2 bound "
                                                    "is registry and expression data, and the pocket "
                                                    "contrast is a frame-fraction over unbiased "
                                                    "ensembles rather than a docked pose. "
                                                    "path-family-synthesis.md §4 records both source "
                                                    "rows as inheriting NEITHER R3 NOR R5.",
            "evidence": _pose_inheritance(),
            "⛔": "the pocket-contrast half is a RANKING on opening frequency. It is not a per-molecule "
                 "claim and evidence of absence is not available at these ensemble sizes.",
        },
    }


def to_markdown(d):
    import antihandle_constraint as AC
    L = []
    A = L.append
    A(AC._frontmatter(
        "Q16 — the NR4A3 design brief, restated asymmetrically in its harder measured form",
        "State the selectivity brief as hard vs NR4A1 and hard-but-lower-priority vs NR4A2, both "
        "molecular, with each clause carrying its own measured sensitivity.",
        "A design TARGET assembled from committed readings. No free energy, no margin, no ratio, no "
        "window; no binding, degradation, selectivity, efficacy or safety statement.",
        "DOC-NR4A3-DESIGN-BRIEF-ASYMMETRIC",
        "research/modalities/design_brief_asymmetric.py"))
    b = d["★_the_brief"]
    A("# %s\n" % d["_title"])
    A("**Status.** %s\n" % d["_status"])
    A("## ★ The brief\n")
    A("> ### %s\n" % b["one_line"])
    for c in b["clauses"]:
        A("### `%s` · %s\n" % (c["id"], c["constraint"]))
        A("%s\n" % c["text"])
        if c.get("why_it_outranks_B2"):
            A("**Why it outranks `B2`.** %s\n" % c["why_it_outranks_B2"])
        if c.get("instrument_reading"):
            A("**Instrument reading.** `%s`\n" % c["instrument_reading"])
        A("⚠ **Sensitivity.** %s\n" % c["⚠_sensitivity"])
        if c.get("what_would_reopen_it"):
            A("**What would reopen it.** %s\n" % c["what_would_reopen_it"])
    A("## ★ The asymmetry read — carried with its sensitivity, not as a word\n")
    az = d["★_the_asymmetry_read"]
    A("**`lead_status`: %s**\n" % az["lead_status"])
    A("| paralogue | axis | verdict under the frozen rule | survives the contested `C2` rule? | "
      "design-corrected Wilson intervals overlap? | Holm-adjusted one-sided *p* (floor 0.10) |")
    A("|---|---|---|---|---|---|")
    for par, r in sorted(az["by_paralogue"].items()):
        t = r["★_three_cautions"]
        A("| %s | %s | %s | %s | %s | %s |"
          % (par, r["axis"], r["verdict_under_the_frozen_rule"],
             t["contested_C2_rule"]["survives_the_rule_change"],
             t["design_effect_corrected_wilson"]["intervals_overlap"],
             t["design_floor"]["holm_adjusted_over_2_paralogues"]))
    A("")
    A("⛔ The pooled verdict this replaces was `%s`, driven by **%s**.\n"
      % (az["pooled_verdict_it_replaces"], ", ".join(az["the_pooled_verdict_was_driven_by"])))
    A("## The NR4A2 bound\n")
    sp = d["the_NR4A2_bound"]
    f, lv = sp["the_floor"], sp["the_exposure_lever"]
    A("- **Decision:** `%s`" % sp["decision"])
    A("- **The floor:** %s (`%s`), PMID %s, on %d independent null alleles; %d single-gene annotations"
      % (f["mp_term"], f["mp_id"], " / ".join(f["pubmed_ids"] or []), len(f["genotypes"] or []),
         f["n_single_gene_annotations"]))
    A("- **The exposure lever:** %s\n" % lv["⛔_reading"])
    A("⚠ %s\n" % sp["⚠_what_the_table_may_NOT_be_quoted_for"])
    A("## ⛔ Superseded, retained\n")
    for s in b["⛔_superseded_retained"]:
        A("- %s" % s)
    A("")
    A("## ⛔ This brief contains no\n")
    for s in b["⛔_this_brief_contains_no"]:
        A("- %s" % s)
    A("")
    A("## ⛔ Pose marginalisation\n")
    pm = d["_pose_marginalisation"]
    A("**Rule.** %s\n" % pm["rule"])
    A("**Why it is statable today.** %s\n" % pm["why_it_is_nonetheless_statable_today"])
    A("%s\n" % pm["⛔"])
    return "\n".join(L)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", default=OUT)
    args = ap.parse_args(argv)
    for p in (SPARING, ASYM):
        if not os.path.exists(p):
            print("REFUSED — %s does not exist" % p, file=sys.stderr)
            return 2
    doc = build()
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    with open(os.path.splitext(args.out)[0] + ".md", "w", encoding="utf-8") as fh:
        fh.write(to_markdown(doc))
    print("wrote %s" % os.path.relpath(args.out, REPO))
    print(doc["★_the_brief"]["one_line"])
    print("asymmetry lead_status: %s" % doc["★_the_asymmetry_read"]["lead_status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
