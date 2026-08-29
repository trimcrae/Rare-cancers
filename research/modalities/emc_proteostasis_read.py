#!/usr/bin/env python3
"""Is EMC a proteostatically loaded tumour — the axis behind the best ex-vivo result it has?

⭐ WHY THIS EXISTS, AND WHY IT WAS WRITTEN BEFORE THE DATA LANDED. `RT-CARFILZOMIB` is the only
route in this portfolio whose evidence was generated on cells that actually carry this disease:
carfilzomib, with venetoclax, active across two patient-derived EMC models. Every other route —
including the PRMT5 one — transfers from a different disease. Its target axis had never been read
in the only EMC expression data that exists; read 18 was added to `emc_expression_panels.PANELS` on
2026-08-09 to fix that, and THIS FILE WAS COMMITTED BEFORE THE FETCH RETURNED so that the grading
rule is pre-specified rather than chosen once the numbers were visible.

⭐ THE HYPOTHESIS IS SPECIFIC, AND IT IS NOT "IS THE PROTEASOME EXPRESSED". It is expressed
everywhere; that is what a housekeeping gene does. The question is whether this tumour carries the
LOAD that would make degradative capacity limiting. A myxoid sarcoma is a secretory,
matrix-producing tumour, and matrix synthesis is exactly the burden that makes a cell depend on
folding and disposal. So the read that carries the argument is:

    the SECRETORY/MATRIX-LOAD and UNFOLDED-PROTEIN-RESPONSE modules, contrasted against the
    PROTEASOME MACHINERY itself.

A tumour where the load modules move and the machinery does not is the shape the hypothesis
predicts. A tumour where everything moves together is a proliferation or cellularity story. A
tumour where nothing moves is a null.

⛔ THE PRE-STATED EXPECTED OUTCOME IS A NULL, AND IT IS RECORDED HERE SO IT CANNOT BE QUIETLY
REPLACED. Transcript abundance is a weak instrument for a dependency; the ex-vivo result this is
read against was measured by other people in models this programme does not have; and NFE2L1
bounce-back — the mechanism that actually limits proteasome inhibitors — is post-translational and
an array cannot see it at all. Nothing here can assert that any proteasome inhibitor acts, is
selective, or is safe in EMC.

⚠ AND THE DEPENDENCY SIDE WILL PROBABLY ARGUE AGAINST THE ROUTE, WHICH IS THE POINT OF READING IT.
The same panel already caught this once: PRMT5 and MAT2A are dependencies in 94.5% and 96.7% of the
91 SCREENED sarcoma lines, so the PRMT5 manuscript prints its dependency prior against its own route.
(Denominator corrected 2026-08-29: this docstring said 176, which is the number of sarcoma MODELS in
DepMap 24Q4; only 91 of them carry CRISPR gene-effect data. The percentages are unchanged.) A
proteasome subunit required in every line offers nothing to select on either, and if that is what
comes back it belongs in the repurposing paper in the same position and with the same prominence.

$0 — reads committed artifacts, stdlib only, no network.
"""
from __future__ import annotations

import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
PANEL = os.path.join(HERE, "emc-expression-panels.json")
DEPMAP = os.path.join(HERE, "depmap-sarcoma-dependency.json")
OUT = os.path.join(HERE, "emc-proteostasis-read.json")

P6244 = "GSE24369_series_matrix.txt.gz"
P3290 = "GSE4303-GPL3290_series_matrix.txt.gz"
PLATS = (P6244, P3290)

#: The two sides of the contrast, named before the data was seen.
MACHINERY = ("proteasome_20S_core", "proteasome_19S_regulatory")
LOAD = ("secretory_and_matrix_load_proxy", "unfolded_protein_response")
CONTEXT = ("bounceback_and_integrated_stress", "degradative_alternatives")

#: ⛔ THE GRADING RULE, PRE-SPECIFIED. |t| >= 2 is the panel's own "moved" threshold and is reused
#: rather than invented here; nothing below chooses a cutoff after seeing a number.
MOVED = 2.0


def _load(p):
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def _group(panel, gname, plat):
    g = ((panel.get("panels", {}).get("proteostasis") or {}).get("groups") or {}).get(gname) or {}
    per = (g.get("per_platform") or {}).get(plat) or {}
    sc = per.get("score")
    if not sc:
        return {"scored": False,
                "_reading": "⛔ NO SCORE EMITTED on this platform — an instrument statement "
                            "(coverage floor or no readable member), never a null result.",
                "n_genes_readable": per.get("n_genes_readable"),
                "n_genes_requested": per.get("n_genes_requested")}
    return {"scored": True, "t": sc.get("t"), "delta": sc.get("delta_a_minus_b"),
            "n_genes_readable": per.get("n_genes_readable"),
            "n_genes_requested": per.get("n_genes_requested")}


def _placed(panel, plat, gene):
    gw = ((panel.get("platforms") or {}).get(plat) or {}).get("genome_wide_null") or {}
    return ((gw.get("placed_wanted_genes") or {}).get(gene)) or None


def _verdict(load_ts, mach_ts, load_names=(), moved_names=()):
    """The pre-specified reading. Both arguments are lists of scored group t values.

    ⚠ THE LABEL MUST NOT BE QUOTABLE WITHOUT ITS SUBSTRUCTURE, and the first run showed why. On
    GPL6244 the rule fired 'the shape the hypothesis predicts' on ONE of two load modules — the
    unfolded-protein response at t = +2.11 — while `secretory_and_matrix_load_proxy`, the module
    that actually carries the mechanistic argument, was FLAT at −0.20. The rule is left exactly as
    it was pre-specified, because changing a threshold after seeing the numbers is fitting. What is
    added is that the verdict now names which modules moved and which did not, so the headline
    cannot travel without the qualification."""
    if not load_ts and not mach_ts:
        return ("⛔ NOT MEASURED on this platform — no group emitted a score. An absent reading, "
                "never a finding that the axis is flat.")
    load_moved = [t for t in load_ts if abs(t) >= MOVED and t > 0]
    mach_moved = [t for t in mach_ts if abs(t) >= MOVED and t > 0]
    if load_moved and not mach_moved:
        flat = [n for n in load_names if n not in moved_names]
        qual = ""
        if flat:
            qual = (f" ⚠ AND IT FIRED ON PART OF THE LOAD SIDE ONLY: {', '.join(moved_names)} "
                    f"moved while {', '.join(flat)} did not. "
                    f"{'secretory_and_matrix_load_proxy' in flat and 'The flat one is the module that carries the mechanistic argument — a myxoid tumour depending on degradative capacity BECAUSE it secretes matrix — so this verdict is markedly weaker than its label. ' or ''}"
                    f"The rule is the one pre-specified before the data; the qualification is here "
                    f"so the label cannot be quoted without it.")
        return ("⭐ THE SHAPE THE HYPOTHESIS PREDICTS — a load module moves up and the proteasome "
                "machinery does not. That is consistent with a tumour where degradative capacity is "
                "limiting rather than merely present. ⚠ Consistent with, not evidence for: it is a "
                "transcript contrast in archival tissue and it excludes no confound." + qual)
    if load_moved and mach_moved:
        return ("◐ EVERYTHING MOVES TOGETHER — load and machinery both up. That is the shape a "
                "proliferation, cellularity or general-biosynthesis difference produces, and it is "
                "NOT specific to the proteostatic argument. Read the proliferation control before "
                "reading this as support.")
    if mach_moved and not load_moved:
        return ("⚠ MACHINERY WITHOUT LOAD — the proteasome reads higher while the burden modules do "
                "not. The hypothesis predicted the opposite pairing, so this does not support it; "
                "it is a reading in search of a mechanism.")
    return ("⛔ NULL — neither the load modules nor the machinery move on this platform. This is the "
            "outcome the read was pre-stated to expect, and it lowers the prior that a proteasome "
            "inhibitor's ex-vivo activity in EMC runs through a transcript-visible load difference. "
            "It does NOT refute the ex-vivo result, which was measured on cells.")


def build():
    panel = _load(PANEL) if os.path.exists(PANEL) else {}
    if "proteostasis" not in (panel.get("panels") or {}):
        return {"_status": "⛔ NOT MEASURED — the committed panel predates read 18 (added "
                           "2026-08-09). Run `emc-expression-datasets.yml mode=panels`. THIS IS AN "
                           "ABSENT READING, NOT A NULL RESULT."}
    per_plat = {}
    for plat in PLATS:
        groups = {g: _group(panel, g, plat) for g in MACHINERY + LOAD + CONTEXT}
        load_ts = [groups[g]["t"] for g in LOAD if groups[g].get("scored")]
        mach_ts = [groups[g]["t"] for g in MACHINERY if groups[g].get("scored")]
        load_named = [g for g in LOAD if groups[g].get("scored")]
        moved_named = [g for g in load_named if abs(groups[g]["t"]) >= MOVED and groups[g]["t"] > 0]
        placed = {}
        for gname in MACHINERY + LOAD + CONTEXT:
            for gene in (((panel["panels"]["proteostasis"]["groups"].get(gname) or {})
                          .get("genes_requested")) or []):
                p = _placed(panel, plat, gene)
                if p:
                    placed[gene] = p
        hardest = sorted(placed.items(),
                         key=lambda kv: kv[1]["frac_of_array_at_least_as_extreme_two_sided"])[:8]
        per_plat[plat] = {
            "groups": groups,
            "verdict": _verdict(load_ts, mach_ts, load_named, moved_named),
            "the_eight_most_extreme_genes_of_this_read_on_this_array": dict(hardest),
            "⚠_how_to_read_the_placement": "`frac_of_array_at_least_as_extreme_two_sided` is the "
                "fraction of ALL symbols on this array whose EMC-vs-comparator |t| is at least this "
                "gene's. It controls no error rate; it says whether a t like this is remarkable "
                "here. A housekeeping gene sitting mid-distribution is the expected reading.",
        }
    dep = _load(DEPMAP) if os.path.exists(DEPMAP) else {}
    grp = (dep.get("genes_by_group") or {})
    prot = None
    for k, v in grp.items():
        if "roteasome" in k:
            # ⚠ THE ARTIFACT'S FIELD NAMES, READ FROM IT RATHER THAN ASSUMED. The first
            # version of this line guessed `mean_gene_effect`/`frac_dependent` and silently
            # produced None for every gene — a populated-looking block with no measurement in it,
            # which is the exact failure mode CLAUDE.md §4 names.
            prot = {r.get("gene"): {"sarcoma_mean": r.get("sarcoma_mean"),
                                    "sarcoma_frac_dependent": r.get("sarcoma_frac_dependent"),
                                    "rest_mean": r.get("rest_mean"),
                                    "selectivity": r.get("selectivity"),
                                    "n_sarcoma_lines_screened": r.get("n_sarcoma")} for r in v}
    return {
        "_title": "The proteostatic axis in EMC — the read behind the best ex-vivo evidence this "
                  "disease has.",
        "_generated_by": "research/modalities/emc_proteostasis_read.py",
        "_sources": {"expression": "research/modalities/emc-expression-panels.json → "
                                   "panels.proteostasis (read 18)",
                     "dependency": "research/modalities/depmap-sarcoma-dependency.json → "
                                   "the proteasome group"},
        "⭐_the_grading_rule_was_written_before_the_data": "This module was committed before the "
            "fetch that populates read 18 returned. The four readings it can emit — the predicted "
            "shape, everything-moves-together, machinery-without-load, and null — were all named "
            "in advance, and |t| >= 2 is the panel's own threshold rather than one chosen here.",
        "⛔_the_pre_stated_expectation_was_a_null": "Transcript abundance is a weak instrument for "
            "a dependency, and NFE2L1 bounce-back — the mechanism that limits proteasome "
            "inhibitors — is post-translational and invisible to an array. A null here lowers a "
            "prior; it does not refute an ex-vivo result measured on cells.",
        "_no_clinical_claim": "⛔ Nothing here asserts efficacy, safety, a therapeutic window or "
            "clinical readiness for any agent in any disease.",
        "per_platform": per_plat,
        "dependency_prior": prot or {
            "_status": "⛔ NOT MEASURED — the committed DepMap artifact predates the proteasome "
                       "group (added 2026-08-09). Run `depmap-dependency.yml`."},
        "⚠_read_the_dependency_prior_against_the_route": "A gene required in almost every line of "
            "a tissue class offers little to select on. If the proteasome subunits come back "
            "near-pan-essential, that QUALIFIES this route exactly as PRMT5's 94.5% qualified the "
            "methylosome route, and it belongs in the paper with the same prominence.",
    }


def main():
    res = build()
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(res, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    print(f"wrote {os.path.relpath(OUT, os.path.dirname(HERE))}")
    if res.get("_status"):
        print(" ", res["_status"][:150])
        return 0
    for plat, r in res["per_platform"].items():
        print(f"  {plat[:30]}")
        for g, v in r["groups"].items():
            if v.get("scored"):
                print(f"    {g:36} t={v['t']:+7.3f}  {v['n_genes_readable']}/"
                      f"{v['n_genes_requested']}")
            else:
                print(f"    {g:36} NO SCORE ({v.get('n_genes_readable')}/"
                      f"{v.get('n_genes_requested')})")
        print(f"    -> {r['verdict'][:120]}")
    dp = res["dependency_prior"]
    if "_status" in dp:
        print(" ", dp["_status"][:120])
    else:
        for g, v in sorted(dp.items()):
            print(f"    dep {g:8} mean={v['sarcoma_mean']} "
                  f"frac_dep={v['sarcoma_frac_dependent']} selectivity={v['selectivity']} "
                  f"n={v['n_sarcoma_lines_screened']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
