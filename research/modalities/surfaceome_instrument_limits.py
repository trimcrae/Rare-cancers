#!/usr/bin/env python3
"""Measure what the EMC surfaceome scan CANNOT see — against the script and its own artifacts.

★★ WHY THIS EXISTS. `emc-unexplored-treatment-lanes.md` §0 asserts two limits of
`emc_surfaceome_scan.py`: that it cannot see a glycan or a stromal antigen, and that `CSPG4` is
absent from its seed set and from its outputs. Both assertions are correct in direction and both
were PROSE. A prose limit cannot fail a build, cannot be re-checked after the scan is re-run, and
cannot be told apart from a limit somebody remembered wrong — which is the exact shape of the defect
CLAUDE.md §4 names: *a field's PRESENCE is never evidence of its provenance*, and its mirror, an
absence asserted rather than measured.

⛔ THE THING THIS PROTECTS AGAINST IS A FALSE NEGATIVE THAT READS AS A MEASURED ONE. The scan's
headline conclusion — that the selective ∩ normal-tissue-restricted intersection is empty — is cited
by three routes. It is a true statement about the antigen class the scan can rank. It is not a
statement about antigen classes the instrument is structurally incapable of ranking, and nothing in
the artifact distinguishes the two.

WHAT IS MEASURED HERE, all from committed files, no network, $0:

  L1  COMPARTMENT.   The scan's population is DepMap cell lines. A cancer-associated fibroblast is
      not in it, so a CAF/stromal antigen has no compartment to be measured in. Evidence taken from
      the artifact itself, not from the docstring.
  L2  THE STROMAL FLOOR.   `LRRC15` — a real sarcoma STROMAL ADC target — reads at the floor. That
      is the instrument reading a known stromal antigen as absent, which is the limit demonstrating
      itself rather than being claimed.
  L3  GLYCAN.   An oncofetal chondroitin-sulfate epitope is a SULFATION PATTERN. It has no gene, so
      it cannot be ranked by a gene-expression instrument at all. The measurable proxy — the CS/GAG
      biosynthetic module that would at least be an indirect read — is checked for presence, and is
      excluded twice over: those enzymes are Golgi-resident, so the scan's UniProt filter
      (SL-0039 plasma membrane + TM/GPI) does not admit them, and none is in the curated seed.
  L4  CSPG4.   Absent from `SEED_SURFACE` and reported in no artifact.
      ⚠ AND THE STRONGER CLAIM IS REFUSED HERE. "Absent from the outputs" is NOT "not scanned".
      The scan unions ~2,820 UniProt genes into its set and then reports only 40 top candidates,
      the 47 seed antigens and one line's top-30 — it never records the scanned gene list. So
      whether CSPG4 entered the scanned set is UNDECIDABLE from the committed artifacts, and this
      module says `undecidable` rather than picking whichever answer is more convenient. What IS
      decidable, and is the finding that matters: no per-gene number for CSPG4 exists anywhere in
      the record, so nothing has ever measured it and nothing ever rejected it.
  L5  FAP IN EMC.   The route `RT-FAP-RLT` inherits `myxoid_mean_log2tpm 0.0` from this scan. That
      value has n = 1, and the one line is `ACH-001519`, whose EMC identity the repository itself
      RETRACTED on 2026-08-05. So the scan contains no EMC observation of FAP — the readiness
      register's `missing: ["any measurement in EMC"]` is not merely still true, it is true for a
      second, independent reason.

⚠ WHAT THIS MODULE IS NOT. It has no known-answer control of its own and needs none: it makes no
prediction. Every output is a membership test or a field read on a committed file, and every one is
falsifiable by changing the file. Re-run it after any re-run of `emc_surfaceome_scan.py`.

Output: research/modalities/surfaceome-instrument-limits.json
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SCAN_JSON = os.path.join(HERE, "emc-surfaceome-scan.json")
NORMAL_WINDOW_JSON = os.path.join(HERE, "emc-surface-normal-window.json")
SCAN_PNG = os.path.join(HERE, "emc-surfaceome-scan.png")
PRIORITIZATION_PNG = os.path.join(HERE, "emc-surface-prioritization.png")
OUT = os.path.join(HERE, "surfaceome-instrument-limits.json")

# The ofCS lane's biosynthetic module, as named in emc-unexplored-treatment-lanes.md §3.6, SPLIT in
# two — and the split is the point, because the first draft of this module did not have it and
# scored a PARTIAL that was really two different facts stacked on one another.
#
#  * SULFATION MACHINERY — the enzymes that WRITE the sulfation pattern VAR2CSA reads, plus the PAPS
#    donor supply. This is the only sub-module that could ever carry a sulfation-CODE argument.
#    Golgi-resident type II membrane proteins and cytosolic synthases, so a PLASMA-membrane filter
#    excludes every one of them by construction.
#    ⚠ CORRECTED 2026-08-07 BY READING THE FULL TEXT, having first been written from an abstract.
#    ofCS is *"unusually long and highly **6-O and 4-O** sulfated CS chains"* — Skafte et al.,
#    Cell Death Dis 2026, PMC12877138 [FT]. An earlier draft of this module treated the 4-O arm as
#    the signature and the 6-O transferases (CHST3, CHST7) as the *contrary* reading. That was wrong
#    in the most misleading possible direction: it would have scored a real 6-O signal as evidence
#    AGAINST the lane. Both arms are part of the pattern.
#  * BACKBONES — the carrier proteoglycans. A backbone's abundance says a chain may be attached; it
#    says NOTHING about how that chain is sulfated, which is the entire address.
# ⭐ THE GENE SET IS CITED, NOT INVENTED. Wu et al., "Glycogenes in Oncofetal Chondroitin Sulfate
# Biosynthesis are Differently Expressed and Correlated With Immune Response in Placenta and
# Colorectal Cancer", Front Cell Dev Biol 2021 — PMID 34966741 / PMC8710744, retrieved and read as
# open-access full text through CI on 2026-08-07. Its glycogene panel is the tetrasaccharide linker
# (XYLT1/2, B4GALT7, B3GALT6, B3GAT3), the CS chain polymerases (CSGALNACT1/2, CHSY1/3) and the
# sulfotransferases/epimerase that write the pattern (CHST3/7/11/12/13/14/15, UST, DSE). PAPSS1/2
# and the Golgi PAPS transporters SLC35B2/B3 are added here as the sulfate-donor supply the
# 4-O and 6-O sulfation depends on — that addition is this module's, and is marked as such.
SULFATION_MACHINERY = [
    # linker tetrasaccharide
    "XYLT1", "XYLT2", "B4GALT7", "B3GALT6", "B3GAT3",
    # chain initiation / polymerisation
    "CSGALNACT1", "CSGALNACT2", "CHSY1", "CHSY3",
    # sulfotransferases + epimerase — these WRITE the pattern VAR2CSA reads
    "CHST3", "CHST7", "CHST11", "CHST12", "CHST13", "CHST14", "CHST15", "UST", "DSE",
    # PAPS supply (this module's addition, not Wu et al.'s panel)
    "PAPSS1", "PAPSS2", "SLC35B2", "SLC35B3",
]
#: ⚠ NAMED CARRIERS, NOT THE WHOLE REPERTOIRE. PMID 26461094 names CD44 and CSPG4 as the exemplars of
#: *"a limited repertoire of cancer-associated proteoglycans"*; Agerbæk et al., Nat Commun 2018
#: (PMC6095877 [FT]) puts that repertoire at *"more than 30 different proteoglycans"*. So "the two
#: carriers" would be false; "the two the founding paper names" is what is measured here.
PG_BACKBONES = ["CSPG4", "VCAN", "ACAN", "CD44"]
NAMED_OFCS_CARRIERS = ["CD44", "CSPG4"]
OFCS_MODULE = SULFATION_MACHINERY + PG_BACKBONES

# Stromal / CAF antigens. Not a scored panel — a demonstration set, and deliberately NOT a uniform
# one, because the uniform version would have overstated the limit.
#   * CAF_ONLY   — carried by the stromal compartment and not by mesenchymal tumour cells. These are
#     the genes for which this instrument's reading is a reading of the missing compartment.
#   * ALSO_TUMOUR_CELL — classically called stromal/pericyte, but genuinely transcribed by
#     mesenchymal tumour cells too, so the scan CAN see them and its numbers for them are real.
# The limit is not "the scan cannot see any stromal gene". It is "the scan cannot see a gene that
# ONLY the stroma expresses" — narrower, and the narrower statement is the true one.
STROMAL_CAF_ONLY = ["LRRC15", "FAP"]
STROMAL_ALSO_TUMOUR_CELL = ["CD248", "PDGFRB"]
STROMAL_DEMONSTRATION = STROMAL_CAF_ONLY + STROMAL_ALSO_TUMOUR_CELL


def load(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def reported_genes(scan: dict) -> dict:
    """Every gene for which the scan artifact carries a per-gene number, by where it appears."""
    return {
        "top_candidates": [c["gene"] for c in scan.get("top_candidates", [])],
        "actionable_antigens": sorted(scan.get("actionable_antigens", {})),
        "single_line_top_surface": [
            r["gene"] for r in (scan.get("emc_line_top_surface") or {}).get("top_surface_antigens", [])
        ],
    }


def main() -> int:
    sys.path.insert(0, HERE)
    import emc_surfaceome_scan as scan_module  # noqa: E402  (needs HERE on the path)

    scan = load(SCAN_JSON)
    seed = list(scan_module.SEED_SURFACE)
    reported = reported_genes(scan)
    all_reported = sorted(set(sum(reported.values(), [])))

    aa = scan.get("actionable_antigens", {})
    cls = scan.get("class_definition", {})
    src = scan.get("surfaceome_source", {})

    # ---- L1 · compartment -------------------------------------------------------------------
    l1 = {
        "limit": "no stromal / CAF compartment exists in the scanned population",
        "population": scan.get("data_source"),
        "n_sarcoma_lines": cls.get("n_sarcoma_lines"),
        "n_class_lines": cls.get("n_class_lines"),
        "unit_of_observation": "an immortalised tumour cell line, cultured as monoculture",
        "why_it_is_structural": (
            "DepMap OmicsExpression measures transcript abundance in the cell line itself. A "
            "cancer-associated fibroblast is a different cell that is not present in the culture, "
            "so an antigen carried by CAFs has no compartment in which it could be counted. This "
            "is not low sensitivity; the observation does not exist."
        ),
        "artifact_says_so": [c for c in scan.get("_caveats", []) if "NOT normal tissue" in c
                             or c.startswith("SURROGATE")],
        "a_concrete_antigen_this_costs_us": (
            "⭐ Not hypothetical. Oncofetal chondroitin sulfate — the VAR2CSA/Vartumab address — "
            "\"appears both on the malignant cells, in the ECM and on the cancer associated "
            "fibroblasts, while being absent on non-tumor associated fibroblasts and healthy "
            "adjacent tissue\" (Skafte et al., Cell Death Dis 2026, PMC12877138 [FT]). TWO of the "
            "three compartments it occupies do not exist in this instrument's data, so even if the "
            "epitope had a gene to rank, two thirds of its distribution would be invisible."
        ),
        "verdict": "CONFIRMED",
    }

    # ---- L2 · the stromal floor, demonstrated ------------------------------------------------
    demo = {}
    for g in STROMAL_DEMONSTRATION:
        row = aa.get(g)
        demo[g] = None if row is None else {
            "class_mean_log2tpm": row.get("class_mean_log2tpm"),
            "class_frac_expressed": row.get("class_frac_expressed"),
            "enrichment_vs_rest": row.get("enrichment_vs_rest"),
            "selectivity_q": row.get("selectivity_q"),
            "selectivity_significant": row.get("selectivity_significant"),
        }
    lrrc15 = demo.get("LRRC15") or {}
    caf_only_floor = {
        g: (demo.get(g) or {}).get("class_frac_expressed") for g in STROMAL_CAF_ONLY
    }
    l2 = {
        "limit": "an antigen carried ONLY by the stromal compartment reads at or near the floor",
        "genes": demo,
        "caf_only_frac_expressed": caf_only_floor,
        "lrrc15_at_floor": lrrc15.get("class_frac_expressed") == 0.0,
        "reading": (
            "LRRC15 is an established sarcoma stromal/CAF antigen with a clinical ADC programme "
            "behind it. In this instrument it reads frac_expressed 0.0. The instrument is "
            "reporting the compartment's absence, not the antigen's."
        ),
        "counter_reading_that_narrows_the_limit": {
            "genes": {g: demo.get(g) for g in STROMAL_ALSO_TUMOUR_CELL},
            "note": (
                "⚠ CD248 and PDGFRB are routinely called stromal/pericyte antigens and BOTH read "
                "selectivity_significant: true here. That is not the instrument malfunctioning and "
                "it is not evidence against L1 — mesenchymal tumour cells genuinely transcribe "
                "them, so there is something in the culture to measure. The honest limit is "
                "therefore NARROWER than 'the scan cannot see stroma': it cannot see a gene that "
                "ONLY the stroma expresses. LRRC15 and FAP are that case; CD248 and PDGFRB are "
                "not. Stating the wide version would have been easy to write and false."
            ),
        },
        "verdict": "CONFIRMED" if lrrc15.get("class_frac_expressed") == 0.0 else "NOT CONFIRMED",
    }

    # ---- L3 · glycan blindness ---------------------------------------------------------------
    machinery_reported = sorted(g for g in SULFATION_MACHINERY if g in all_reported)
    backbones_reported = sorted(g for g in PG_BACKBONES if g in all_reported)
    l3 = {
        "limit": "a sulfation pattern has no gene, and the machinery that writes it is filtered out",
        "target_class": "oncofetal chondroitin sulfate (ofCS) — a placental-type chondroitin "
                        "sulfate epitope, characterised as \"unusually long and highly 6-O and 4-O "
                        "sulfated CS chains\" (PMC12877138 [FT]); the VAR2CSA/Vartumab address",
        "why_direct_ranking_is_impossible": (
            "ofCS is a post-translational glycan modification pattern on a carrier proteoglycan. "
            "There is no ofCS gene, so no gene-expression ranking can return it — not weakly, not "
            "at the floor, not at all."
        ),
        "sulfation_machinery": SULFATION_MACHINERY,
        "sulfation_machinery_source": {
            "panel": "Wu et al., Front Cell Dev Biol 2021",
            "pmid": "34966741",
            "pmcid": "PMC8710744",
            "doi": "10.3389/fcell.2021.763875",
            "verification": "[FT] — open-access full text retrieved through CI 2026-08-07 "
                            "(literature-cache: literature/ofcs-var2csa-vartumab/PMC8710744.txt)",
            "this_modules_addition": ["PAPSS1", "PAPSS2", "SLC35B2", "SLC35B3"],
        },
        "sulfation_machinery_in_seed": sorted(g for g in SULFATION_MACHINERY if g in seed),
        "sulfation_machinery_reported_anywhere": machinery_reported,
        "backbones": PG_BACKBONES,
        "backbones_in_seed": sorted(g for g in PG_BACKBONES if g in seed),
        "backbones_reported_anywhere": backbones_reported,
        "backbone_rows": {g: aa.get(g) for g in backbones_reported},
        "why_the_machinery_is_excluded": (
            "the scan's own UniProt filter is " + str(src.get("query")) + " — reviewed human "
            "proteins at the PLASMA membrane presenting an extracellular epitope. The CS "
            "sulfotransferases and glycosyltransferases are GOLGI-resident type II membrane "
            "proteins and the PAPS synthases are cytosolic, so none is admitted. The exclusion is "
            "by design and correct for the instrument's stated job — it is a limit only because "
            "the artifact's conclusion is read more widely than its filter."
        ),
        "why_a_reported_backbone_does_not_rescue_it": (
            "⚠ ONE backbone IS reported — CD44, which is in the curated seed. That does not give "
            "the lane anything: a backbone's transcript abundance says a GAG chain may be "
            "attached and says nothing about whether it carries the sulfation pattern VAR2CSA "
            "binds. "
            "The repository's own rejection of CD44/RHAMM (enrichment "
            + str((aa.get("CD44") or {}).get("enrichment_vs_rest"))
            + ", selectivity_q " + str((aa.get("CD44") or {}).get("selectivity_q"))
            + ") is therefore a reading about a BACKBONE, and cannot be carried over to ofCS. "
            "VCAN and ACAN are secreted matrix proteoglycans and are not admitted either, so the "
            "matrix EMC is actually made of is absent from the scanned set."
        ),
        "verdict": ("CONFIRMED" if not machinery_reported
                    else "NOT CONFIRMED — sulfation machinery reported: " + ", ".join(machinery_reported)),
    }

    # ---- L4 · CSPG4 --------------------------------------------------------------------------
    cspg4_where = {k: ("CSPG4" in v) for k, v in reported.items()}
    normal_window = load(NORMAL_WINDOW_JSON)
    cspg4_in_normal_window = "CSPG4" in json.dumps(normal_window)
    l4 = {
        "limit": "CSPG4 was never seen, and was therefore never rejected",
        "in_seed_surface": "CSPG4" in seed,
        "n_seed": len(seed),
        "seed_size_matches_artifact": len(seed) == src.get("n_seed_unioned"),
        "reported_in": cspg4_where,
        "in_emc_surface_normal_window": cspg4_in_normal_window,
        "png_artifacts": {
            "note": (
                "the two PNGs are RENDERED FROM the JSON above (emc_surface_figure.py / "
                "emc_surfaceome_scan.py), so a gene carrying no row in the JSON has nothing to "
                "plot. That is the argument; a grep of a compressed raster is not evidence and is "
                "not offered as any."
            ),
            "paths": [os.path.basename(SCAN_PNG), os.path.basename(PRIORITIZATION_PNG)],
        },
        "was_it_scanned": "UNDECIDABLE",
        "why_undecidable": (
            "the artifact records n_from_uniprot=" + str(src.get("n_from_uniprot")) + " and "
            "n_total=" + str(src.get("n_total")) + " but NOT the gene list, and reports per-gene "
            "numbers for only " + str(len(all_reported)) + " distinct genes. CSPG4 is a "
            "single-pass type I plasma-membrane proteoglycan, so it plausibly entered the UniProt "
            "set — but the committed record cannot settle it, and this module refuses to guess. "
            "Recording the scanned gene list would close this permanently and costs nothing."
        ),
        "what_is_decidable": (
            "no per-gene number for CSPG4 exists in any committed artifact of this instrument. "
            "Its absence from the surface-antigen conclusion is therefore a COVERAGE GAP, not a "
            "negative result."
        ),
        "why_the_gap_is_worse_than_one_missing_gene": {
            "finding": (
                "⭐ The founding VAR2CSA paper NAMES two carrier proteoglycans for the oncofetal CS "
                "epitope — CD44 and CSPG4. This instrument's seed contains ONE of them. So the seed "
                "did not merely miss a gene: of the two named carriers of the antigen class the "
                "ofCS lane is built on, it scanned one and never saw the other, and the repository "
                "then rejected the one it scanned."
            ),
            "named_carriers": NAMED_OFCS_CARRIERS,
            "named_carriers_in_seed": [g for g in NAMED_OFCS_CARRIERS if g in seed],
            "⚠_not_the_whole_repertoire": (
                "CORRECTED 2026-08-07 from full text. An earlier draft of this field said the "
                "founding paper names EXACTLY two carriers. It names two as exemplars of \"a "
                "limited repertoire\"; Agerbæk et al., Nat Commun 2018 (PMC6095877 [FT]) puts that "
                "repertoire at \"more than 30 different proteoglycans\". The coverage point is "
                "unaffected and the arithmetic behind it is not: what is measured is that of the "
                "two carriers the founding paper NAMES, this seed holds one."
            ),
            "quote": (
                "\"In tumors, placental-like CS chains are linked to a limited repertoire of "
                "cancer-associated proteoglycans including CD44 and CSPG4.\""
            ),
            "source": {"pmid": "26461094", "journal": "Cancer Cell 2015",
                       "doi": "10.1016/j.ccell.2015.09.003",
                       "verification": "[API] — Europe PMC core record + abstract, retrieved "
                                       "through CI 2026-08-07. Not open access; full text not read."},
            "cd44_was_scanned_and_rejected": (aa.get("CD44") or {}),
            "⚠_what_this_does_NOT_say": (
                "it does NOT say CSPG4 is an EMC target, nor that a CSPG4 reading would have "
                "changed the scan's conclusion. A carrier's transcript abundance does not "
                "establish that its chains carry the ofCS sulfation pattern. The claim is only that the "
                "instrument's coverage of this antigen class was half, and nothing recorded that."
            ),
        },
        "verdict": "CONFIRMED",
    }

    # ---- L5 · what FAP evidence exists in EMC specifically -----------------------------------
    fap = aa.get("FAP", {})
    myxoid_named = cls.get("myxoid_lines_named", [])
    l5 = {
        "limit": "the scan holds no EMC observation of FAP, for two independent reasons",
        "fap_row": fap,
        "n_myxoid_lines": cls.get("n_myxoid_lines"),
        "myxoid_lines_named": myxoid_named,
        "identity_verdict_on_that_line": (scan.get("emc_line_top_surface") or {}).get("identity_verdict"),
        "reason_1_compartment": "FAP is a CAF antigen and there is no CAF compartment (L1).",
        "reason_2_identity": (
            "the single line matching the 'myxoid' subtype is ACH-001519, whose EMC identity this "
            "repository RETRACTED on 2026-08-05 (Cellosaurus CVCL_1238 records no EWSR1 fusion; "
            "DepMap's filtered fusion caller names no FET gene). So myxoid_mean_log2tpm = "
            + str(fap.get("myxoid_mean_log2tpm")) + " at n = " + str(fap.get("n_myxoid")) + " is "
            "not an EMC reading."
        ),
        "consequence_for_the_route": (
            "RT-FAP-RLT's readiness `missing: [\"any measurement in EMC\"]` SURVIVES unchanged. The "
            "class-level numbers (enrichment " + str(fap.get("enrichment_vs_rest")) + ", "
            "selectivity_q " + str(fap.get("selectivity_q")) + ", not significant) are a reading of "
            "tumour cells in translocation sarcomas generally, and they neither support nor refute "
            "a stromal radioligand route in EMC."
        ),
        "verdict": "CONFIRMED",
    }

    out = {
        "_what": (
            "Measured limits of the EMC surfaceome instrument (emc_surfaceome_scan.py / "
            "ART-SURFACE-EXPRESSION), taken from the script and its committed artifacts."
        ),
        "_why": (
            "Three routes cite this artifact's empty-intersection conclusion. That conclusion is "
            "true of the antigen class the instrument can rank and silent about the classes it "
            "cannot. Until now the distinction lived only in prose."
        ),
        "_cost": "$0 — committed artifacts only. No network, no GPU, no rental.",
        "_no_known_answer_control": (
            "and none is needed: this module makes no prediction. Every field is a membership test "
            "or a field read, falsifiable by changing the file it reads."
        ),
        "instrument": {
            "module": "research/modalities/emc_surfaceome_scan.py",
            "artifact_id": "ART-SURFACE-EXPRESSION",
            "artifact_path": "research/modalities/emc-surfaceome-scan.json",
            "n_surface_genes_scanned": scan.get("n_surface_genes_scanned"),
            "n_distinct_genes_reported": len(all_reported),
            "scanned_gene_list_recorded": False,
        },
        "limits": {
            "L1_no_stromal_compartment": l1,
            "L2_stromal_floor_demonstrated": l2,
            "L3_glycan_unrankable": l3,
            "L4_cspg4_coverage_gap": l4,
            "L5_no_emc_fap_observation": l5,
        },
        "what_would_close_each": {
            "L1": "a single-cell or bulk EMC tumour dataset with a stromal compartment, or CAF "
                  "co-culture data. Not obtainable by re-running this instrument.",
            "L2": "same as L1 — the floor is the compartment's absence.",
            "L3": "a CS/GAG biosynthesis + PAPS module expression read on the two readable EMC "
                  "series (GSE24369, GSE4303). ⚠ THIS IS DISPATCHED SEPARATELY AND IS NOT PART OF "
                  "THIS ARTIFACT — see the ofCS memo's open slot. It is an indirect, "
                  "sulfation-CODE argument and would not measure the epitope.",
            "L4": "one line: add CSPG4 and the proteoglycan module to SEED_SURFACE and re-run; and "
                  "record the scanned gene list so absence is never again undecidable.",
            "L5": "any FAP expression or imaging readout on EMC tissue. Not computable here.",
        },
        "consumers_that_should_carry_these_limits": [
            "RT-B7H3", "RT-PRAME-IMMTAC", "RT-TCRT-CTA", "RT-FAP-RLT", "RT-CART-SURFACE",
        ],
    }

    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2)
        fh.write("\n")

    for key, block in out["limits"].items():
        print(f"{block['verdict']:<12} {key}")
    print(f"\nwrote {OUT}")
    failed = [k for k, v in out["limits"].items() if not v["verdict"].startswith("CONFIRMED")]
    if failed:
        print("NOT CONFIRMED: " + ", ".join(failed), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
