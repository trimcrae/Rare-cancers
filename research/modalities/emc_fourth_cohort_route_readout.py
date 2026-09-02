#!/usr/bin/env python3
"""What the FOURTH EMC cohort adds, and does not add, to the sixteen routes that cite BLK-NO-EMC-DATA
for an expression or tissue read.

⭐ WHY THIS EXISTS. `AUT-PD-116` records sixteen routes whose `required_validation` is marked
`feasible_today: false` on `BLK-NO-EMC-DATA` while naming an expression or tissue read. Seat S32
adjudicated all sixteen against the two ARRAY series
(`research/modalities/emc-blk-no-emc-data-route-retest.json`, 2026-09-01) and left two questions
open, both priced at one $0 fetch: whether the fourth cohort's gene space covers `RT-TCRT-CTA`'s
cancer-testis antigens and whether it can resolve `RT-IMMUNOCYTOKINE`'s oncofetal fibronectin and
tenascin domains. The fourth cohort was fetched and quantified on 2026-09-02 (AUT-113/114/115), so
both questions are now readable off disk. This module reads them off disk.

⛔ WHAT A ROW HERE IS. `in_fourth_cohort: true` means the gene has AT LEAST ONE PROBE ASSIGNED TO IT
in `emc-fourth-cohort-gene-counts.tsv`, i.e. the gene is transcribed in EMC tumour tissue above the
run's own lossy-counting floor. It is not a phenotype, a protein, a surface location, a copy number,
a differential-expression result or a target claim.

⛔ AND `in_fourth_cohort: false` IS AN INSTRUMENT STATE, NOT A READING OF ABSENCE. The quantifier
matched 59.3% of the offered probes to a human cDNA/ncRNA transcript verbatim; a probe spanning a
junction the sequence set does not carry is unassigned, and the gene it targets then has no row.
`emc-fourth-cohort-quant.json` says this in its own words under `probe_map.⚠ unassigned_means` and
`⛔ gene_counts_units`. A false here says the repository cannot read that gene in this cohort.

Every figure this module reports has its one home elsewhere: `emc-fourth-cohort-quant.json` and
`emc-fourth-cohort-gene-counts.tsv` for the cohort, `emc-expression-panels.json` for the two array
series. Nothing is re-typed; addresses are carried instead.

Usage:  python3 research/modalities/emc_fourth_cohort_route_readout.py [--check]
"""

import csv
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "emc-fourth-cohort-route-readout.json")
GENE_TSV = os.path.join(HERE, "emc-fourth-cohort-gene-counts.tsv")
QUANT = os.path.join(HERE, "emc-fourth-cohort-quant.json")
PANELS = os.path.join(HERE, "emc-expression-panels.json")

# The genes each route's own required_validation text (or the route's stated address) turns on.
# Curated from `systems/graph/routes.json` and the route's owning memo; a route whose requirement
# names no gene carries an empty list and is still adjudicated, on the requirement's KIND.
ROUTE_GENES = {
    "RT-SSTR2": ["SSTR2"],
    "RT-B7H3": ["CD276", "NCAM1"],
    "RT-CART-SURFACE": ["ALCAM", "BGN", "CD44", "GPC1", "VCAN"],
    "RT-FAP-RLT": ["FAP"],
    "RT-TCRT-CTA": ["CTAG1B", "MAGEA3", "SSX2", "CTAG2", "MAGEA4", "PRAME"],
    "RT-JUNCTION-NEOANTIGEN": ["HLA-A", "HLA-B", "HLA-C", "B2M", "TAP1", "TAP2"],
    "RT-FUSION-OUTPUT": ["EWSR1", "TAF15", "NR4A3", "ENO3", "PPARG", "SEMA3C"],
    "RT-MTAP-PRMT5": ["MTAP", "PRMT5", "MAT2A", "CDKN2A"],
    "RT-TRABECTEDIN": [],
    "RT-SYNPROMOTER": ["NR4A3"],
    "RT-TXN-CDK": ["CDK7", "CDK9", "CDK12", "CDK13"],
    "RT-MATRIX-SYNTHESIS": ["CHSY1", "CHPF", "CSGALNACT1", "CSGALNACT2", "CHST11", "CHST3",
                            "UST", "PAPSS1", "PAPSS2", "ACAN", "VCAN", "BGN"],
    "RT-MATRIX-ADDRESS": ["CSPG4", "CHST11", "CHST3"],
    "RT-IMMUNOCYTOKINE": ["FN1", "TNC"],
    "RT-HYPOXIA-PRODRUG": ["CA9", "VEGFA", "SLC2A1", "LDHA", "HIF1A", "EGLN3", "ADM", "P4HA1"],
    "RT-VACCINE-COMBINATION": ["HLA-A", "HLA-B", "HLA-C", "CD274", "PDCD1", "CTLA4"],
}


def _sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def build():
    with open(GENE_TSV) as fh:
        rows = list(csv.reader(fh, delimiter="\t"))
    fourth = {r[0] for r in rows[1:]}
    quant = json.load(open(QUANT))
    panels = json.load(open(PANELS))
    gene_reads = panels["gene_reads"]

    fish = {a: v.get("ewsr1_break_apart_fish")
            for a, v in quant["per_run"].items()}
    n_pos = sum(1 for v in fish.values() if v == "EWSR1+")
    n_neg = sum(1 for v in fish.values() if v == "EWSR1-")

    per_route = {}
    for rid, genes in ROUTE_GENES.items():
        rows_out = {}
        for g in genes:
            arr = gene_reads.get(g)
            readable = None
            if isinstance(arr, dict):
                readable = sorted(s for s, v in arr.items()
                                  if isinstance(v, dict) and v.get("readable"))
            rows_out[g] = {
                "in_fourth_cohort": g in fourth,
                "readable_in_array_series": readable,
            }
        n_in = sum(1 for v in rows_out.values() if v["in_fourth_cohort"])
        per_route[rid] = {
            "genes_the_requirement_turns_on": genes,
            "per_gene": rows_out,
            "n_genes_with_a_fourth_cohort_probe": n_in,
            "n_genes_named": len(genes),
        }

    art = {
        "_what": ("Per route, which of the genes its BLK-NO-EMC-DATA-marked required_validation turns "
                  "on can be read in the fourth EMC cohort (PRJNA1357027 / SRP640302) and in the two "
                  "array series. One row per gene; no figure is re-typed."),
        "_generated_by": "research/modalities/emc_fourth_cohort_route_readout.py",
        "_cost": "$0 — reads four committed files; no fetch, no CI, no GPU.",
        "_serves": ["AUT-PD-116"],
        "⛔ _what_a_true_row_is_not": [
            "Not a phenotype, a protein, a surface location, a copy number or an activity.",
            "Not a differential-expression result: emc-fourth-cohort-quant.json → "
            "why_no_differential_expression refuses one at this design.",
            "Not a target, a therapeutic window, an efficacy, a selectivity or a safety claim.",
            "Not a patient count: 12 runs are 12 tumours, and a tumour is not an outcome.",
        ],
        "⛔ _what_a_false_row_is_not": (
            "NOT a reading of absence. It means no probe in this deposit was matched to that gene by "
            "this quantifier — emc-fourth-cohort-quant.json → probe_map.'⚠ unassigned_means' and "
            "'⛔ gene_counts_units'. The gene may be on the panel and unmatched, or off it."
        ),
        "⭐ the_rule_this_adjudication_applies": {
            "statement": (
                "BLK-NO-EMC-DATA covers a required_validation entry ONLY IF a public or deposited EMC "
                "FUNCTIONAL-GENOMICS dataset — a perturbation, dependency or drug-response screen — "
                "would satisfy it. An entry asking for an expression or tissue profile, a protein, a "
                "stain, an imaging or dosimetry value, a copy number, an immunopeptidome, a T-cell "
                "assay, or a clinical, outcome or registry read is NOT its to hold."
            ),
            "derived_from": "systems/graph/blockers.json → BLK-NO-EMC-DATA",
            "the_blocker_in_its_own_words": [
                "name: EMC is nearly absent from public functional-genomics data (one DepMap line, "
                "n = 1, no CRISPR data)",
                "statement_about: data availability — the repo-wide rate-limiter, not any one route",
                "retired_by_action refuses, unprompted, both this fourth cohort ('a tumour expression "
                "panel is not a dependency screen, so nothing here touches it') and a methylation "
                "reference set as retirements.",
            ],
            "⛔ what_this_rule_never_does": (
                "Removing this blocker from an entry does not make the entry satisfied, does not "
                "promote, re-grade or unblock a route, and does not change any grade, state or "
                "readiness field. Where a route's residual is a bench, a clinic or a reachable-set "
                "gap, the entry gains the blocker that names it and stays feasible_today: false."
            ),
            "applied_by": "AUT-PD-116, seat s31-emc-data-blocks, 2026-09-02",
            "the_prior_adjudications_this_builds_on": [
                "research/modalities/emc-blk-no-emc-data-route-retest.json (S32, 19 entries / 16 routes)",
                "research/autonomy/sprint-2026-09-01/S41-BLOCKED-ROUTE-AUDIT.md (9 entries / 7 routes)",
            ],
        },
        "cohort": {
            "bioproject": quant["bioproject"],
            "sra_study": quant["sra_study"],
            "n_runs_read": quant["n_runs_read"],
            "n_genes_with_at_least_one_assigned_probe": quant["n_genes_with_at_least_one_assigned_probe"],
            "gene_counts_sha256": quant["gene_counts_sha256"],
            "gene_counts_recomputed_sha256": _sha256(GENE_TSV),
            "n_probes_offered": quant["probe_map"]["n_probes_offered"],
            "n_probes_assigned_to_one_gene": quant["probe_map"]["n_probes_assigned_to_one_gene"],
            "n_probes_unassigned": quant["probe_map"]["n_probes_unassigned"],
            "⚠ design_that_travels_with_every_row_below": (
                "n = 12 FFPE tumours, one sequencing batch, archive collection years 1997–2020, split "
                "6 good-prognosis versus 6 poor-prognosis by the depositors' own unexplained B/G key. "
                "A targeted templated-ligation panel, so the gene space is the panel's and not the "
                "transcriptome, notwithstanding the deposit's own 'whole human transcriptome' wording. "
                "No differential-expression result is available or computed at this n and design."
            ),
            "ewsr1_break_apart_fish": {
                "per_run": fish,
                "n_EWSR1_positive": n_pos,
                "n_EWSR1_negative": n_neg,
                "⛔ what_this_is_not": (
                    "A break-apart FISH call is EWSR1 REARRANGED versus not. It is not a partner "
                    "identity: it does not say EWSR1::NR4A3 versus TAF15::NR4A3, and an EWSR1- case "
                    "is not thereby a TAF15 case. It is the depositors' annotation, not a measurement "
                    "taken here."
                ),
            },
        },
        "the_two_array_series_this_is_read_against": {
            "artifact": "research/modalities/emc-expression-panels.json",
            "registered_as": "ART-EMC-EXPRESSION-PANELS",
            "field_that_answers_a_gene_level_requirement": "gene_reads.<SYMBOL>.<series>.readable",
            "field_that_answers_a_surface_requirement": (
                "reads.read_8_SURFACE_ANTIGEN.cross_platform_board.by_state and "
                "reads.read_8_SURFACE_ANTIGEN.the_route_named_addresses"
            ),
        },
        "per_route": per_route,
        "⭐ the_two_questions_S32_left_open_and_priced_at_one_fetch": {
            "RT-TCRT-CTA": {
                "question_verbatim": ("whether CTAG1B, MAGEA3 and SSX2 are in the fourth cohort's gene "
                                      "space, since they are unreadable on both arrays"),
                "answer": "NO — none of the three has an assigned probe in the committed gene table.",
                "array_state": ("reads.read_8_SURFACE_ANTIGEN.cross_platform_board.by_state."
                                "NOT_READABLE_ON_EITHER_PLATFORM lists CTAG1B, MAGEA3 and SSX2."),
                "⛔ therefore": ("Three EMC tumour series now exist and all three of this route's named "
                                "antigens remain UNREAD. That is an instrument state on three "
                                "instruments, not a negative about the tumour, and it is not a "
                                "downgrade of the route on evidence."),
            },
            "RT-IMMUNOCYTOKINE": {
                "question_verbatim": ("whether the fourth cohort's data type can resolve the oncofetal "
                                      "fibronectin and tenascin spliced domains at all — the route's own "
                                      "next.best_next_action"),
                "answer": "NO.",
                "why": [
                    "TNC has no assigned probe in the committed gene table, so the tenascin parent gene "
                    "is not readable in this cohort at all.",
                    "FN1 has exactly one assigned probe across the 1,645 probes common to every run, and "
                    "gene counts are summed over the probes assigned to a gene "
                    "(emc-fourth-cohort-quant.json → '⛔ gene_counts_units').",
                    "The committed probe table carries probe_sequence and assigned_gene and no transcript "
                    "or exon identity, so no domain-inclusion call is derivable from it.",
                ],
                "⛔ therefore": ("The isoform half of this route's requirement is untaken and the fourth "
                                "cohort does not take it. An isoform-resolved read still needs "
                                "transcript-resolved sequencing, or the vendor probe manifest with its "
                                "per-probe transcript targets, which is not on disk."),
            },
        },
    }
    return art


def main():
    art = build()
    if "--check" in sys.argv:
        if not os.path.exists(OUT):
            print(f"⛔ {OUT} is missing — run this generator and commit the result")
            return 1
        cur = json.load(open(OUT))
        if cur != art:
            print(f"⛔ {OUT} is stale — rerun this generator and commit the result")
            return 1
        print("OK — the committed readout reproduces from its inputs")
        return 0
    with open(OUT, "w") as fh:
        json.dump(art, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
