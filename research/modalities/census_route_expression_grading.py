#!/usr/bin/env python3
"""Grade the modality-census routes whose selecting feature is READABLE in data already on disk. ($0, stdlib)

⭐ WHY THIS EXISTS. The 2026-08-09 modality census registered 24 new routes, each carrying a "cheapest
next observation". For six of them that observation turned out not to need running at all: the genes
were already read and committed in `emc-expression-panels.json`, and nobody had ever graded them
AGAINST THESE ROUTES because the routes did not exist when the panel was built. This module closes
that gap and does nothing else -- it reads one committed artifact and emits a verdict per route.

⛔ IT COMPUTES NOTHING NEW. Every number it reports is lifted from the panel artifact, which owns it.
That is deliberate: re-deriving a z-score here would create a second home for a figure the panel
already owns (rule 1), and the whole finding of this pass is that the reading existed and the GRADE
did not.

⚠ WHAT A TRANSCRIPT READ CANNOT DO, stated once and inherited by every verdict below. These are two
small archival array series (6 EMC vs 29 comparator sarcomas on GPL6244; 10 vs 6 on GPL3290). A
transcript level is not a protein level, is not an activity, and is not a copy number. Every verdict
here is a reason to prioritise or de-prioritise a route, never a statement about what any agent does
in a patient. Nothing here asserts efficacy, safety, a therapeutic window or clinical readiness.
"""
from __future__ import annotations

import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
PANEL = os.path.join(HERE, "emc-expression-panels.json")
OUT = os.path.join(HERE, "census-route-expression-grading.json")

GPL6244 = "GSE24369_series_matrix.txt.gz"
GPL3290 = "GSE4303-GPL3290_series_matrix.txt.gz"
PLATFORMS = {GPL6244: "GPL6244 (6 EMC vs 29 comparator sarcomas)",
             GPL3290: "GPL3290 (10 EMC vs 6 comparator)"}


def load():
    with open(PANEL, encoding="utf-8") as fh:
        return json.load(fh)


def gene(panel, symbol):
    """EMC-minus-comparator mean z per platform, plus EMC's own array percentile.

    Returns `readable: False` where no probe maps -- and that is NOT a statement that the gene is
    unexpressed, which is the panel artifact's own governing rule and the one most easily lost when
    a second module summarises it.
    """
    out = {}
    src = panel["gene_reads"].get(symbol)
    if src is None:
        return {p: {"readable": False, "why": "symbol absent from the panel's gene_reads"}
                for p in PLATFORMS}
    for p in PLATFORMS:
        v = src.get(p)
        if not v or not v.get("readable"):
            out[p] = {"readable": False,
                      "why": "no probe on this platform maps to the symbol; NOT a reading of absence"}
            continue
        out[p] = {"readable": True,
                  "emc_mean_z": v["EMC"]["mean_z"],
                  "emc_array_percentile": v["EMC"]["mean_array_percentile"],
                  "comparator_mean_z": v["comparator"]["mean_z"],
                  "delta_emc_minus_comparator": round(
                      v["EMC"]["mean_z"] - v["comparator"]["mean_z"], 4)}
    return out


def group(panel, panel_name, group_name):
    """A scored group verdict as the panel emitted it, verbatim."""
    g = panel["panels"][panel_name]["groups"][group_name]["per_platform"]
    return {p: {"verdict": g[p]["verdict"], "score": g[p].get("score")} for p in PLATFORMS if p in g}


def concordance(per_platform, key="delta_emc_minus_comparator"):
    """Do the two platforms agree on SIGN? The only cross-platform claim this data supports.

    ⚠ Magnitudes are not comparable across these two series -- different platforms, different
    comparator arms, different n. Sign agreement is a real observation; a pooled effect size would be
    an invented one.
    """
    signs = [v[key] > 0 for v in per_platform.values() if v.get("readable") and key in v]
    if len(signs) < 2:
        return "not_assessable_one_platform_or_fewer"
    return "concordant" if len(set(signs)) == 1 else "discordant"


def build():
    p = load()
    routes = {}

    # ─────────────────────────── RT-ARGININE ───────────────────────────
    ass1 = gene(p, "ASS1")
    routes["RT-ARGININE"] = {
        "selecting_feature": "ASS1 silencing — the biomarker arginine-deprivation agents are given on",
        "direction_the_route_needed": "ASS1 LOW in EMC",
        "genes": {"ASS1": ass1, "ASL": gene(p, "ASL"), "ARG2": gene(p, "ARG2")},
        "concordance_of_the_primary_gene": concordance(ass1),
        "observed": "ASS1 is HIGHER in EMC than in comparator sarcomas on BOTH platforms, and on "
                    "GPL6244 it sits at the 92nd percentile of that array's own probe distribution.",
        "verdict": "AGAINST — the selecting feature is absent at transcript level on both platforms.",
        "what_this_does_not_settle": "ASS1 loss in the arginine-deprivation literature is an IHC "
                                     "call, and a transcript is not a protein. This de-prioritises "
                                     "the route; it does not prove the class could not act.",
        "route_action": "down-grade: the premise as stated is not supported",
    }

    # ───────────────────────────── RT-RET ─────────────────────────────
    ret = gene(p, "RET")
    routes["RT-RET"] = {
        "selecting_feature": "RET expressed AND activated — the historical claim the lane rests on",
        "direction_the_route_needed": "RET present, with an engageable activation route",
        "genes": {g: gene(p, g) for g in ("RET", "GDNF", "GFRA1", "ARTN", "NRTN")},
        "concordance_of_the_primary_gene": concordance(ret),
        "panel_groups": {"gdnf_family_ligands": group(p, "ret_axis", "gdnf_family_ligands"),
                         "gfra_co_receptors": group(p, "ret_axis", "gfra_co_receptors")},
        "observed": "RET itself is HIGHER in EMC on both platforms — the lane's own premise holds at "
                    "the receptor. ⛔ But the module that ACTIVATES it does not: the GFRα "
                    "co-receptors are LOWER in EMC on both platforms and strongly so, and the "
                    "GDNF-family ligands are LOWER on both. Canonical RET signalling needs a ligand "
                    "and a GFRα co-receptor; EMC has the receptor and, relative to comparator "
                    "sarcomas, less of both of the things that switch it on.",
        "verdict": "SPLIT — receptor supported, ligand-dependent activation route weakened.",
        "what_this_does_not_settle": "Ligand-independent activation exists in tumours carrying a RET "
                                     "rearrangement, and none is reported in this disease either "
                                     "way. Co-receptor transcript in bulk tumour also cannot exclude "
                                     "a paracrine supply from stroma or nerve. This narrows the "
                                     "mechanism the lane should claim; it does not close it.",
        "route_action": "keep, with the co-receptor reading carried as a stated caveat",
    }

    # ────────────────────── RT-HYPOXIA-PRODRUG ──────────────────────
    routes["RT-HYPOXIA-PRODRUG"] = {
        "selecting_feature": "a hypoxic fraction large enough to activate a prodrug",
        "direction_the_route_needed": "hypoxia signature HIGH in EMC",
        "genes": {g: gene(p, g) for g in ("CA9", "SLC2A1", "VEGFA", "LDHA", "ADM")},
        "panel_groups": {"hypoxia_canonical_hif_targets_curated":
                         group(p, "hypoxia", "hypoxia_canonical_hif_targets_curated")},
        "observed": "A curated canonical HIF-target metagene scores HIGHER in EMC than in comparator "
                    "sarcomas on BOTH platforms, with 15/15 and 14/15 genes readable.",
        "verdict": "SUPPORTED — and it is the only route in this pass supported concordantly on both "
                   "platforms.",
        "what_this_does_not_settle": "A hypoxia metagene is a transcriptional shadow of hypoxia, not "
                                     "an oxygen measurement, and 'higher than other sarcomas' is not "
                                     "'hypoxic enough to reduce a prodrug'. The class also carries a "
                                     "negative randomised soft-tissue-sarcoma record that any "
                                     "assessment must lead with.",
        "route_action": "keep; premise supported at the level this data can reach",
    }

    # ────────────────────── RT-MATRIX-SYNTHESIS ──────────────────────
    routes["RT-MATRIX-SYNTHESIS"] = {
        "selecting_feature": "the tumour actively manufacturing its sulfated chondroitin-sulfate matrix",
        "direction_the_route_needed": "CS biosynthetic and sulfation machinery HIGH in EMC",
        "genes": {g: gene(p, g) for g in ("CHST11", "CHST14", "PAPSS1", "PAPSS2", "XYLT1")},
        "panel_groups": {"paps_module": group(p, "cs_gag_paps", "paps_module"),
                         "cs_backbone_polymerisation":
                             group(p, "cs_gag_paps", "cs_backbone_polymerisation"),
                         "cs_sulfotransferases_4O":
                             group(p, "cs_gag_paps", "cs_sulfotransferases_4O")},
        "observed": "⛔ The sulfate-DONOR module is LOWER in EMC than in comparator sarcomas on BOTH "
                    "platforms, driven by PAPSS2. The backbone-polymerisation and 4-O-sulfotransferase "
                    "groups DISAGREE between platforms, so neither supports a call.",
        "verdict": "AGAINST AS STATED — the naive form of the premise, that a matrix-defining tumour "
                   "must be running its biosynthetic machinery hotter than its neighbours, is not "
                   "what the data shows.",
        "what_this_does_not_settle": "The comparator arm is itself matrix-rich sarcoma, so this is a "
                                     "relative statement and not an absolute one; and bulk transcript "
                                     "of a biosynthetic enzyme need not track accumulated matrix mass "
                                     "in a tumour whose product is long-lived. The route needs "
                                     "reformulating rather than deleting.",
        "route_action": "re-scope: the premise must be restated in a form this reading does not "
                        "already contradict",
    }

    # ─────────────────────── RT-IMMUNOCYTOKINE ───────────────────────
    fn1 = gene(p, "FN1")
    routes["RT-IMMUNOCYTOKINE"] = {
        "selecting_feature": "a matrix epitope present in EMC stroma and restricted enough to address",
        "direction_the_route_needed": "the epitope's parent genes present, ideally enriched",
        "genes": {"FN1": fn1, "TNC": gene(p, "TNC"), "FAP": gene(p, "FAP")},
        "observed": "The parent genes are abundantly expressed in ABSOLUTE terms — FN1 sits at the "
                    "94th percentile of its array on GPL6244 — but they are NOT enriched relative to "
                    "comparator sarcomas: FN1 is flat on one platform, and TNC and FAP are LOWER in "
                    "EMC on both.",
        "verdict": "PRESENT, NOT SELECTIVE — and the question that actually decides this route is "
                   "unreadable here.",
        "what_this_does_not_settle": "⛔ THE ADDRESS IS A SPLICE VARIANT, AND A GENE-LEVEL PROBE "
                                     "CANNOT SEE ONE. The clinical immunocytokines target an "
                                     "oncofetal fibronectin/tenascin isoform, not total FN1 or TNC, "
                                     "and its abundance is not deducible from the parent gene. So "
                                     "this reading bounds the parent genes and leaves the route's own "
                                     "premise untested.",
        "route_action": "keep; the isoform question is now the route's stated first requirement",
    }

    # ───────────────────────────── RT-NR2F1 ─────────────────────────────
    nr2f1 = gene(p, "NR2F1")
    routes["RT-NR2F1"] = {
        "selecting_feature": "expression of the dormancy receptor in EMC",
        "direction_the_route_needed": "the receptor readable and present",
        "genes": {"NR2F1": nr2f1},
        "panel_groups": {"dormancy_associated_context_curated":
                         group(p, "nr2f1_dormancy", "dormancy_associated_context_curated")},
        "observed": "NR2F1 is NOT READABLE on either platform — no probe maps to it. ⚠ That is an "
                    "instrument limit and not a reading of absence. Separately, a curated "
                    "dormancy-associated context set is HIGHER in EMC on BOTH platforms.",
        "verdict": "UNREAD — the route's precondition cannot be answered from these two series at all, "
                   "while the surrounding programme it belongs to is elevated on both.",
        "what_this_does_not_settle": "Everything about the receptor itself. An unreadable gene is the "
                                     "one case where this pass returns no information, and recording "
                                     "that as a negative would be the exact failure the source "
                                     "artifact's governing rule forbids.",
        "route_action": "keep; the next observation must come from a platform that carries the probe",
    }

    return {
        "_what": "Verdicts for the modality-census routes whose selecting feature was ALREADY readable "
                 "in emc-expression-panels.json. One reading per route, graded against the route's own "
                 "stated premise.",
        "_why": "The census registered these routes on 2026-08-09 with a 'cheapest next observation'. "
                "For six of them the observation was already committed and had never been graded "
                "against them, because the routes did not exist when the panel was built.",
        "_this_artifact_computes_nothing_new": "Every figure is lifted from emc-expression-panels.json, "
                                               "which owns it. Re-deriving one here would make a "
                                               "second home for it.",
        "_language_discipline": "Nothing here asserts efficacy, safety, a therapeutic window or "
                                "clinical readiness for any agent or class. A transcript level is not "
                                "a protein level, an activity or a copy number.",
        "_the_comparison_being_made": "EMC tumour tissue against comparator sarcomas on the same "
                                      "array, expressed as a mean z difference. Magnitudes are NOT "
                                      "comparable across the two platforms; only sign agreement is.",
        "source_artifact": "research/modalities/emc-expression-panels.json",
        "platforms": PLATFORMS,
        "routes": routes,
        "summary": {
            "supported": [k for k, v in routes.items() if v["verdict"].startswith("SUPPORTED")],
            "against": [k for k, v in routes.items() if v["verdict"].startswith("AGAINST")],
            "split_or_unread": [k for k, v in routes.items()
                                if not v["verdict"].startswith(("SUPPORTED", "AGAINST"))],
        },
    }


def main():
    doc = build()
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    print(f"wrote {os.path.relpath(OUT, os.path.dirname(HERE))}")
    for rid, r in doc["routes"].items():
        print(f"  {rid:<22} {r['verdict'][:78]}")


if __name__ == "__main__":
    main()
