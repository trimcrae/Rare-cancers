#!/usr/bin/env python3
"""What would it cost to CONTRACT the wet-lab experiments this repository names? — a bottom-up model.

★★ WHY THIS EXISTS, AND WHAT IT CORRECTS. `what-a-civilian-can-buy.md` §4.4 examined biophysics and
screening CROs, found that **not one publishes a price**, and concluded that F1 (the ~$1,000 cost
filter) "cannot even be evaluated" — an unpriceable spend being an unbounded one. That finding is
CORRECT ABOUT CROs and is not disturbed here. But it was drawn over one supply channel, and there is
a second the memo never examined: **academic core facilities, which publish their rates, itemise them
per instrument-hour and per technician-hour, and frequently carry an explicit external-academic and
external-commercial tier.** Those published unit rates make a bottom-up estimate possible without
contacting any vendor, which is what this module builds.

⛔ WHAT THIS IS NOT.
  * NOT a quote. Nobody has been contacted, nothing has been purchased, no vendor has priced this work.
  * NOT a claim that any facility would accept this project, this client, or these cells. Eligibility
    is a SEPARATE gate and is the one `what-a-civilian-can-buy.md` §4.1 shows is decisive: the EMC
    cell lines are institution-gated by policy, and no rate card changes that.
  * NOT a route to running the experiments. A price for a thing you may not buy is still not a purchase.
  * NOT a substitute for the memo. Where the two differ on scope or verdict, the memo wins.

★ THE TWO CLASSES OF INPUT ARE KEPT APART ON PURPOSE, because mixing them is how an estimate acquires
the authority of a measurement.
  * `rate` entries are MEASURED — a figure quoted from a named facility's own published rate card,
    fetched read-only to `literature-cache` under `literature/wetlab-pricing/` and
    `literature/wetlab-pricing-b/`. Each carries its source and its tier.
  * `qty` entries are ESTIMATES — this module's assumption about how many hours, plates or oligos an
    experiment consumes. NOTHING in this repository measures them. They are the dominant uncertainty
    and they are labelled as such in every emitted row.

⚠ Rates are list prices as published on the fetch date and drift. They establish an ORDER OF
MAGNITUDE. Several are internal-academic tiers, which are the LOWEST any user pays; where a facility
publishes an external-commercial tier the ratio to its own internal tier is emitted as
`external_commercial_multiple` so a reader can see the markup rather than guess it.

No efficacy, safety, therapeutic-window or clinical-readiness claim is made or implied for any
molecule, route or experiment named here.
"""
from __future__ import annotations

import json
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "modalities" / "wetlab-contracting-costs.json"

# ─────────────────────────────────────────────────────────────────────────────────────────────
# MEASURED — published unit rates. Every figure is quoted from the cited page.
# `tier` records WHICH rate this is; an internal-academic rate is the floor, not what an outsider pays.
# ─────────────────────────────────────────────────────────────────────────────────────────────
RATES = {
    "tech_hour_external_academic": {
        "usd": 120.00, "unit": "hour", "tier": "external academic",
        "what": "Training and technical assistance — a technician's hands",
        "source": "McGill Imaging and Molecular Biology Platform, published fee table",
        "cache": "literature/wetlab-pricing-b/mcgill_impact_pricing.txt",
    },
    "tech_hour_internal": {
        "usd": 80.00, "unit": "hour", "tier": "internal (McGill)",
        "what": "Training and technical assistance — a technician's hands",
        "source": "McGill Imaging and Molecular Biology Platform, published fee table",
        "cache": "literature/wetlab-pricing-b/mcgill_impact_pricing.txt",
    },
    "high_content_imager_hour_external_academic": {
        "usd": 40.00, "unit": "hour", "tier": "external academic",
        "what": "PerkinElmer Operetta, high-content automated image acquisition (the gH2AX readout)",
        "source": "McGill Imaging and Molecular Biology Platform, published fee table",
        "cache": "literature/wetlab-pricing-b/mcgill_impact_pricing.txt",
    },
    "hcs_image_analysis_hour_external_academic": {
        "usd": 25.00, "unit": "hour", "tier": "external academic",
        "what": "Harmony / Columbus high-content image analysis",
        "source": "McGill Imaging and Molecular Biology Platform, published fee table",
        "cache": "literature/wetlab-pricing-b/mcgill_impact_pricing.txt",
    },
    "plate_reader_hour_external_academic": {
        "usd": 30.00, "unit": "hour", "tier": "external academic",
        "what": "Tecan Spark plate reader (viability / proliferation readout)",
        "source": "McGill Imaging and Molecular Biology Platform, published fee table",
        "cache": "literature/wetlab-pricing-b/mcgill_impact_pricing.txt",
    },
    "qpcr_hour_external_academic": {
        "usd": 20.00, "unit": "hour", "tier": "external academic",
        "what": "qPCR plate reading, ViiA7, 96-well (junction-spanning knockdown readout)",
        "source": "McGill Imaging and Molecular Biology Platform, published fee table",
        "cache": "literature/wetlab-pricing-b/mcgill_impact_pricing.txt",
    },
    "hts_personnel_instrument_day": {
        "usd": 577.23, "unit": "day", "tier": "internal academic (rates effective 2015-07-01)",
        "what": "Personnel and Instrument Daily Rate — a screening core's bundled hands-plus-robot day",
        "source": "University of Colorado Boulder High-Throughput Screening Core Facility, Rates",
        "cache": "literature/wetlab-pricing/core_cuboulder_hts_rates.txt",
    },
    "hts_pilot_screen_1000_compounds": {
        "usd": 1354.66, "unit": "screen", "tier": "internal academic (rates effective 2015-07-01)",
        "what": "Pilot Screen — 1,000 compounds, three 384-well plates, cherry-pick up to 10",
        "source": "University of Colorado Boulder High-Throughput Screening Core Facility, Rates",
        "cache": "literature/wetlab-pricing/core_cuboulder_hts_rates.txt",
    },
    "hts_full_screen_14400_compounds": {
        "usd": 10837.24, "unit": "screen", "tier": "internal academic (rates effective 2015-07-01)",
        "what": "High Throughput Screen — Maybridge Hitfinder 14,400 compounds in replicate, "
                "assay optimisation and automation included, cherry-pick up to 145",
        "source": "University of Colorado Boulder High-Throughput Screening Core Facility, Rates",
        "cache": "literature/wetlab-pricing/core_cuboulder_hts_rates.txt",
    },
    "spr_biacore8000_hour_external_commercial": {
        "usd": 20.55, "unit": "hour", "tier": "external commercial",
        "what": "Biacore 8000 surface plasmon resonance",
        "source": "University of Chicago BioPhysics Core Facility, Equipment & Fees",
        "cache": "literature/wetlab-pricing/core_uchicago_biophysics_fees.txt",
    },
    "spr_biacore8000_hour_internal": {
        "usd": 12.50, "unit": "hour", "tier": "internal",
        "what": "Biacore 8000 surface plasmon resonance",
        "source": "University of Chicago BioPhysics Core Facility, Equipment & Fees",
        "cache": "literature/wetlab-pricing/core_uchicago_biophysics_fees.txt",
    },
    "itc_peaq_hour_academic_selfuse": {
        "usd": 40.00, "unit": "hour", "tier": "academic self-use (2 hour minimum)",
        "what": "Malvern MicroCal PEAQ isothermal titration calorimeter",
        "source": "NC State Biomolecular Interactions Core Facility, published self-use rates",
        "cache": "literature/wetlab-pricing/core_ncsu_bicf.txt",
    },
    "cd_hour_academic_selfuse": {
        "usd": 25.00, "unit": "hour", "tier": "academic self-use (4 hour minimum)",
        "what": "Applied Photophysics circular dichroism — a fold/stability control on a purchased protein",
        "source": "NC State Biomolecular Interactions Core Facility, published self-use rates",
        "cache": "literature/wetlab-pricing/core_ncsu_bicf.txt",
    },
    "hts_cost_per_well_low": {
        "usd": 0.10, "unit": "well", "tier": "academic core, stated range low end",
        "what": "HTS assay cost per well, reagents and scientist time included",
        "source": "UW Carbone Cancer Center Small Molecule Screening Facility, Services/Equipment/Pricing",
        "cache": "literature/wetlab-pricing/core_uwisc_smsf_equipment_services.txt",
    },
    "hts_cost_per_well_high": {
        "usd": 1.00, "unit": "well", "tier": "academic core, stated range high end",
        "what": "HTS assay cost per well, reagents and scientist time included",
        "source": "UW Carbone Cancer Center Small Molecule Screening Facility, Services/Equipment/Pricing",
        "cache": "literature/wetlab-pricing/core_uwisc_smsf_equipment_services.txt",
    },
    "tool_compound_1_5mg_low": {
        "usd": 25.00, "unit": "compound", "tier": "commercial catalogue",
        "what": "1-5 mg of a catalogue tool compound from a chemical manufacturer",
        "source": "UW Carbone Cancer Center Small Molecule Screening Facility, Services/Equipment/Pricing",
        "cache": "literature/wetlab-pricing/core_uwisc_smsf_equipment_services.txt",
    },
    "tool_compound_1_5mg_high": {
        "usd": 100.00, "unit": "compound", "tier": "commercial catalogue",
        "what": "1-5 mg of a catalogue tool compound from a chemical manufacturer",
        "source": "UW Carbone Cancer Center Small Molecule Screening Facility, Services/Equipment/Pricing",
        "cache": "literature/wetlab-pricing/core_uwisc_smsf_equipment_services.txt",
    },
    "moe_base_modification_200nmol": {
        "usd": 15.00, "unit": "modified base", "tier": "commercial catalogue list price",
        "what": "2'-MOE-G oligonucleotide modification surcharge, 50 nmol and 200 nmol scales "
                "(1 umol: $18.00) — the gapmer wing chemistry, priced PER MODIFIED BASE and on top "
                "of the base oligo and phosphorothioate charges",
        "source": "Gene Link, 2'-MOE-G oligo modification product page",
        "cache": "literature/wetlab-pricing-b/genelink_moe_modification_price.txt",
    },
    "crispr_hdr_gene_tagging": {
        "usd": 10840.00, "unit": "cell line", "tier": "academic core service, FY2026",
        "what": "HDR-mediated gene tagging — the degron / dTAG knock-in shape",
        "source": "University of Minnesota Genome Engineering Shared Resource, FY26 service rates",
        "cache": "literature/wetlab-pricing/core_umn_gesr_fy26_rates.txt",
    },
    "crispr_single_aa_knockin": {
        "usd": 9680.00, "unit": "cell line", "tier": "academic core service, FY2026",
        "what": "Single amino-acid knock-in mutation incorporation",
        "source": "University of Minnesota Genome Engineering Shared Resource, FY26 service rates",
        "cache": "literature/wetlab-pricing/core_umn_gesr_fy26_rates.txt",
    },
    "crispr_simple_ko_line": {
        "usd": 5126.00, "unit": "cell line", "tier": "academic core service, FY2026",
        "what": "Simple, single-gene knockout cell line",
        "source": "University of Minnesota Genome Engineering Shared Resource, FY26 service rates",
        "cache": "literature/wetlab-pricing/core_umn_gesr_fy26_rates.txt",
    },
    "crispr_hdr_donor_vector": {
        "usd": 1469.00, "unit": "vector", "tier": "academic core service, FY2026",
        "what": "HDR donor vector construction",
        "source": "University of Minnesota Genome Engineering Shared Resource, FY26 service rates",
        "cache": "literature/wetlab-pricing/core_umn_gesr_fy26_rates.txt",
    },
    "crispr_grna_design_and_validation": {
        "usd": 1108.00, "unit": "target", "tier": "academic core service, FY2026",
        "what": "CRISPR Cas9 gRNA design ($369) plus gRNA validation ($739)",
        "source": "University of Minnesota Genome Engineering Shared Resource, FY26 service rates",
        "cache": "literature/wetlab-pricing/core_umn_gesr_fy26_rates.txt",
    },
    "crispr_commercial_custom_ko_from": {
        "usd": 1980.00, "unit": "cell line", "tier": "commercial list, promotional floor",
        "what": "Commercial custom knockout cell line, advertised starting price",
        "source": "Ubigene CRISPR gene-editing cell line services",
        "cache": "literature/wetlab-pricing-b/ubigene_all_cell_services.txt",
    },
}

# ─────────────────────────────────────────────────────────────────────────────────────────────
# ESTIMATES — how much of each rate an experiment consumes. NOTHING HERE IS MEASURED.
# Each experiment carries `repo_owner` (where the experiment is specified) so the scope is checkable.
# ─────────────────────────────────────────────────────────────────────────────────────────────
EXPERIMENTS = [
    {
        "id": "E1-ATRI-DOSE-RESPONSE",
        "name": "Route 1b — 7-point ATR-inhibitor dose-response in EMC lines, gH2AX readout, "
                "PARPi arm and proliferation index",
        "repo_owner": "research/manuscripts/program/emc-post-degrader-options.md (Axis W2, route 1b)",
        "why_it_is_first": "The repository grades this the SMALLEST wet-lab ask in the portfolio.",
        "lines": [
            ("tool_compound_1_5mg_high", 4, "3 ATR inhibitors (elimusertib / ceralasertib / berzosertib) + 1 PARPi arm"),
            ("tech_hour_external_academic", 120, "~3 technician-weeks: line expansion, plating, dosing, fix/stain, analysis"),
            ("high_content_imager_hour_external_academic", 16, "Operetta acquisition across the dose-response plates"),
            ("hcs_image_analysis_hour_external_academic", 16, "gH2AX foci quantification and proliferation index"),
            ("plate_reader_hour_external_academic", 8, "viability / proliferation readout"),
        ],
        "consumables_estimate_usd": 1500,
        "consumables_note": "plasticware, media, serum, antibodies, transfection-free; a plate-scale figure",
    },
    {
        "id": "E2-ASO-JUNCTION-KNOCKDOWN",
        "name": "ASO section 4 — junction-ASO vs scrambled knockdown in patient-derived EMC lines, "
                "with parental-sparing and phenotype arms",
        "repo_owner": "research/manuscripts/aso/fusion-junction-aso-working-record.md section 4",
        "why_it_is_first": "The repository calls this the single decisive wet-lab-doable experiment "
                           "for the ASO route.",
        "lines": [
            ("moe_base_modification_200nmol", 80, "8 oligos (5 candidate gapmers, 1 scrambled control, "
                                                  "2 single-parent positive controls) x ~10 MOE wing bases each; "
                                                  "EXCLUDES base oligo and phosphorothioate charges"),
            ("tech_hour_external_academic", 240, "~6 technician-weeks: transfection/gymnosis, RNA prep, "
                                                 "junction-spanning qPCR, immunoblot, viability across two lines"),
            ("qpcr_hour_external_academic", 24, "junction-spanning and wild-type-resolved qPCR"),
            ("plate_reader_hour_external_academic", 12, "viability / proliferation / apoptosis"),
        ],
        "consumables_estimate_usd": 4000,
        "consumables_note": "oligo base charges, transfection reagent, RNA kits, antibodies, RNA-seq excluded",
    },
    {
        "id": "E2b-ASO-ISOGENIC-CONTROL-LINE",
        "name": "ASO section 4 controls — the engineered fusion-positive/negative isogenic pair the "
                "red team required, without which wild-type sparing cannot be demonstrated",
        "repo_owner": "research/manuscripts/aso/fusion-junction-aso-working-record.md section 4",
        "why_it_is_first": "Costed SEPARATELY because it is the half of the decisive experiment that "
                           "is an engineering project rather than a plate.",
        "lines": [
            ("crispr_grna_design_and_validation", 1, "guide design and validation at the knock-in locus"),
            ("crispr_hdr_donor_vector", 1, "HDR donor carrying the fusion junction"),
            ("crispr_single_aa_knockin", 1, "HDR knock-in line generation, priced at the nearest published "
                                            "HDR service tier — a fusion knock-in is LARGER than a single "
                                            "amino-acid edit, so this is a FLOOR"),
        ],
        "consumables_estimate_usd": 0,
        "consumables_note": "bundled into the core's service price",
    },
    {
        "id": "E3-R4-BINDING-HALF",
        "name": "R4 (binding half) — does anything bind the NR4A3 ligand-binding domain at all? "
                "A fragment screen read by a binding assay",
        "repo_owner": "research/manuscripts/nr4a3-program-map.md section 5, row R4",
        "why_it_is_first": "The roadmap's cheapest decisive requirement.",
        "lines": [
            ("hts_pilot_screen_1000_compounds", 1, "a 1,000-compound pilot screen at a screening core's published rate"),
            ("spr_biacore8000_hour_external_commercial", 40, "SPR follow-up on pilot hits"),
            ("cd_hour_academic_selfuse", 4, "fold/stability control on the purchased truncated construct"),
        ],
        "consumables_estimate_usd": 0,
        "consumables_note": "PROTEIN IS EXCLUDED AND DOMINATES — see what-a-civilian-can-buy.md section 1.5, "
                            "which owns the protein price and the consumption estimate. Nothing here restates it.",
    },
    {
        "id": "E4-R16-DTAG-DEGRON",
        "name": "R16 — is NR4A3 the right target? A degron (dTAG) knock-in in an EMC line, "
                "the delegated dependency test",
        "repo_owner": "research/manuscripts/nr4a3-program-map.md section 5, row R16",
        "why_it_is_first": "It is the target-validation question every NR4A3-directed route inherits.",
        "lines": [
            ("crispr_grna_design_and_validation", 1, "guide design and validation at the NR4A3 locus"),
            ("crispr_hdr_donor_vector", 1, "HDR donor carrying the degron tag"),
            ("crispr_hdr_gene_tagging", 1, "HDR-mediated gene tagging service"),
            ("tech_hour_external_academic", 80, "~2 technician-weeks of degradation and phenotype characterisation"),
            ("plate_reader_hour_external_academic", 8, "viability after degron induction"),
        ],
        "consumables_estimate_usd": 2000,
        "consumables_note": "degrader ligand, antibodies, plasticware",
    },
    {
        "id": "E5-TRABECTEDIN-PPARG-MATRIX",
        "name": "Route 6 — trabectedin x PPARgamma agonist two-drug matrix on EMC lines",
        "repo_owner": "research/manuscripts/program/emc-post-degrader-options.md route 6",
        "why_it_is_first": "An all-approved-drug combination; the compounds are catalogue items.",
        "lines": [
            ("tool_compound_1_5mg_high", 3, "trabectedin plus two PPARgamma agonists"),
            ("tech_hour_external_academic", 100, "~2.5 technician-weeks for a dose x dose matrix across lines"),
            ("plate_reader_hour_external_academic", 12, "matrix viability readout"),
        ],
        "consumables_estimate_usd": 1500,
        "consumables_note": "plasticware, media, serum",
    },
]


# ─────────────────────────────────────────────────────────────────────────────────────────────
# WHAT YOU ARE ACTUALLY BUYING, per rate. Added 2026-08-23 to answer a question the artifact could
# not answer about itself: how much of each total is LABOUR?
#
# ⛔ THE ANSWER IS NOT ONE NUMBER, AND COLLAPSING IT TO ONE IS THE TRAP. "Labour" splits into two
# things that behave completely differently under automation, and a single "labour share" hides it:
#   * `hands`   — hourly technician time, billed by the hour on a published rate card. This is the
#                 part a liquid handler or an automated imager actually displaces.
#   * `service` — a bundled cell-engineering project price (a CRISPR knock-in line). Labour is
#                 inside it, but it is sold as an outcome, not as hours, and the price reflects
#                 CLONAL SELECTION AND VALIDATION — iterative, failure-prone biology on a timeline
#                 set by how fast cells grow. Automating the pipetting inside it does not make cells
#                 divide faster, and the vendor is not obliged to pass a saving through a fixed
#                 project price at all.
# Keeping them apart is the whole point of this classification; a reader who wants the aggregate can
# add them, and the emitted record says plainly that adding them answers a different question.
BUYING = {
    "hands": {
        "tech_hour_external_academic", "tech_hour_internal",
    },
    "instrument": {
        "high_content_imager_hour_external_academic", "hcs_image_analysis_hour_external_academic",
        "plate_reader_hour_external_academic", "qpcr_hour_external_academic",
        "spr_biacore8000_hour_external_commercial", "spr_biacore8000_hour_internal",
        "itc_peaq_hour_academic_selfuse", "cd_hour_academic_selfuse",
    },
    "bundled_screen": {
        "hts_personnel_instrument_day", "hts_pilot_screen_1000_compounds",
        "hts_full_screen_14400_compounds", "hts_cost_per_well_low", "hts_cost_per_well_high",
    },
    "cell_engineering_service": {
        "crispr_hdr_gene_tagging", "crispr_single_aa_knockin", "crispr_simple_ko_line",
        "crispr_hdr_donor_vector", "crispr_grna_design_and_validation",
        "crispr_commercial_custom_ko_from",
    },
    "materials": {
        "tool_compound_1_5mg_low", "tool_compound_1_5mg_high", "moe_base_modification_200nmol",
    },
}


def what_you_are_buying(rate_key: str) -> str:
    for category, keys in BUYING.items():
        if rate_key in keys:
            return category
    raise KeyError(f"rate {rate_key!r} is not classified in BUYING — classify it or the "
                   f"cost-structure breakdown silently undercounts")


def cost_structure(costed: list[dict]) -> dict:
    """How each total decomposes — the input to any 'what if labour got cheaper' question."""
    per_experiment, totals = {}, {}
    for exp in costed:
        agg = {}
        for line in exp["lines"]:
            cat = what_you_are_buying(line["rate_key"])
            agg[cat] = round(agg.get(cat, 0.0) + line["amount_usd"], 2)
        if exp["consumables_estimate_usd"]:
            agg["consumables"] = exp["consumables_estimate_usd"]
        for k, v in agg.items():
            totals[k] = round(totals.get(k, 0.0) + v, 2)
        t = exp["total_usd"]
        per_experiment[exp["id"]] = {
            "total_usd": t,
            "usd": agg,
            "share": {k: round(v / t, 4) for k, v in agg.items()},
            "hourly_hands_share": round(agg.get("hands", 0.0) / t, 4),
        }
    grand = sum(totals.values())
    return {
        "_what": "Each experiment's total split by WHAT IS BEING BOUGHT, so an automation or "
                 "labour-cost question can be answered against the model instead of by eye.",
        "_the_distinction_that_matters": (
            "`hands` is hourly technician time and is what lab automation displaces. "
            "`cell_engineering_service` is a bundled project price whose cost is clonal selection "
            "and validation — biology on a cell-division timeline, sold as an outcome rather than "
            "as hours. Both are labour in some sense; only the first is labour you can buy less of "
            "by adding a robot. Summing them answers a different question than the one automation asks."
        ),
        "_caution": "These shares inherit the module's ESTIMATED quantities. The SHAPE is robust — "
                    "hands dominate the plate experiments and service fees dominate the engineered "
                    "lines — but the exact percentages are only as good as the hour counts.",
        "per_experiment": per_experiment,
        "across_all_costed_usd": totals,
        "across_all_costed_share": {k: round(v / grand, 4) for k, v in totals.items()},
    }


def _rate(key: str) -> dict:
    if key not in RATES:
        raise KeyError(f"unknown rate {key!r} — every line item must cite a published rate")
    return RATES[key]


def cost_experiment(exp: dict) -> dict:
    lines, subtotal = [], 0.0
    for key, qty, note in exp["lines"]:
        r = _rate(key)
        amount = round(r["usd"] * qty, 2)
        subtotal += amount
        lines.append({
            "rate_key": key,
            "what": r["what"],
            "unit_rate_usd": r["usd"],
            "unit": r["unit"],
            "tier": r["tier"],
            "rate_provenance": "MEASURED — published rate card",
            "source": r["source"],
            "cache": r["cache"],
            "quantity": qty,
            "quantity_provenance": "ESTIMATE — this module's assumption, nothing measures it",
            "quantity_note": note,
            "amount_usd": amount,
        })
    consumables = float(exp.get("consumables_estimate_usd", 0))
    total = round(subtotal + consumables, 2)
    return {
        "id": exp["id"],
        "name": exp["name"],
        "repo_owner": exp["repo_owner"],
        "why_it_is_first": exp["why_it_is_first"],
        "lines": lines,
        "line_subtotal_usd": round(subtotal, 2),
        "consumables_estimate_usd": consumables,
        "consumables_note": exp["consumables_note"],
        "consumables_provenance": "ESTIMATE — this module's assumption, nothing measures it",
        "total_usd": total,
    }


def external_commercial_multiple() -> dict:
    """The one place this repository can MEASURE an external-commercial markup rather than guess it."""
    internal = RATES["spr_biacore8000_hour_internal"]["usd"]
    commercial = RATES["spr_biacore8000_hour_external_commercial"]["usd"]
    return {
        "instrument": "Biacore 8000 SPR, University of Chicago BioPhysics Core Facility",
        "internal_usd_per_hour": internal,
        "external_commercial_usd_per_hour": commercial,
        "multiple": round(commercial / internal, 3),
        "what_it_means": "A facility that publishes both tiers charges an outside commercial user this "
                         "multiple of its internal rate. It is ONE facility and ONE instrument; it is "
                         "cited to show the markup is bounded and small, not to be applied elsewhere.",
        "cache": RATES["spr_biacore8000_hour_external_commercial"]["cache"],
    }


def labour_sensitivity(costed: list[dict], factors=(1.0, 0.5, 0.1, 0.0)) -> dict:
    """What each experiment costs if HOURLY HANDS get cheaper — the automation question, bounded.

    ⛔ WHAT THIS DELIBERATELY DOES NOT DO. It scales `hands` ONLY. It does not scale the bundled
    cell-engineering service price, because that price is not sold by the hour and its cost driver
    is clonal selection on a cell-division timeline; assuming a robot discounts it would be assuming
    the answer. A reader who believes those fees fall too can read `cost_structure` and say so
    explicitly — which is the point of keeping the categories apart.

    ⚠ AND IT IS AN ARITHMETIC BOUND, NOT A FORECAST. `factor = 0` is the physical floor of this
    model — what remains when hands are free — and it exists to show that the floor is NOT zero and
    NOT below the cost filter. It is not a prediction that hands will be free, and nothing here
    claims a date.
    """
    rows = {}
    for exp in costed:
        hands = sum(l["amount_usd"] for l in exp["lines"]
                    if what_you_are_buying(l["rate_key"]) == "hands")
        rest = exp["total_usd"] - hands
        rows[exp["id"]] = {
            "total_usd": exp["total_usd"],
            "hourly_hands_usd": round(hands, 2),
            "everything_else_usd": round(rest, 2),
            "at_factor": {str(f): round(rest + hands * f, 2) for f in factors},
        }
    floor = sum(r["at_factor"]["0.0"] for r in rows.values())
    return {
        "_what": "Each total recomputed with hourly technician time scaled by a factor. "
                 "factor 1.0 is today; factor 0.0 is the floor with hands free.",
        "_scales_only": "hands (hourly technician time)",
        "_does_not_scale": ["cell_engineering_service", "instrument", "bundled_screen",
                            "materials", "consumables"],
        "per_experiment": rows,
        "portfolio_floor_with_free_hands_usd": round(floor, 2),
        "_the_finding": (
            "Even with hands FREE the five alternatives still total in the tens of thousands, and "
            "no single experiment falls anywhere near the $1,000 filter that "
            "what-a-civilian-can-buy.md applies. Cheaper labour moves this from 'expensive' to "
            "'less expensive'. It does not move it into the buyable tier, and it does not touch the "
            "gate that actually closes these routes, which is that the EMC cell lines are "
            "institution-gated by policy."
        ),
    }


# ─────────────────────────────────────────────────────────────────────────────────────────────
# THE AUTOMATION EVIDENCE — a VENDOR'S OWN CLAIM, recorded as advocacy rather than as measurement.
# ─────────────────────────────────────────────────────────────────────────────────────────────
AUTOMATION_EVIDENCE = {
    "_why_this_is_here": (
        "The labour_sensitivity factors above are arithmetic, not a forecast. This block records what "
        "the largest commercial cloud laboratory CLAIMS about the labour layer, so the sensitivity can "
        "be read against a real number instead of an invented one."
    ),
    "_provenance": "MARKETING — Emerald Cloud Lab's own startup-efficiency comparison. It is a vendor "
                   "selling a service, so it is evidence of what is CLAIMED, not of what is delivered. "
                   "Its own page says the industry study behind it is 'available upon request'.",
    "cache": "literature/wetlab-automation/ecl_efficiency_startup.txt",
    "traditional_lab": {
        "team": "2 co-founders, 2 scientists, 4 technicians",
        "headcount_usd_per_year": 802_000,
        "samples_per_year": 8_880,
        "initial_instrumentation_usd": 800_000,
    },
    "cloud_lab": {
        "team": "2 co-founders, 2 scientists",
        "headcount_usd_per_year": 480_000,
        "samples_per_year": 46_620,
        "initial_instrumentation_usd": 0,
    },
    "_the_load_bearing_detail": (
        "The layer the cloud lab removes is EXACTLY the four TECHNICIANS — the scientists stay. That "
        "maps precisely onto this model's `hands` category, which is hourly technician time, and NOT "
        "onto experimental design or interpretation. So the sensitivity's `hands -> 0` limb is the "
        "right shape for what automation is claimed to do."
    ),
    "_the_counter_evidence_from_the_same_vendor": (
        "ECL's own pricing function composes a protocol's cost from PriceInstrumentTime, "
        "PriceOperatorTime, PriceCleaning, PriceStocking, PriceWaste and PriceMaterials "
        "(literature/wetlab-automation/ecl_price_experiment.txt). OPERATOR TIME IS STILL A BILLED "
        "LINE ITEM ON A ROBOTIC LAB. The robot did not take the human out of the cost model; it "
        "moved them off the client's payroll and onto the invoice."
    ),
    "_and_the_price_is_still_not_published": (
        "The same documentation states the figures it displays 'are only for the sake of example and "
        "do not represent actual prices'. So the cloud-lab tier remains QUOTE-ONLY, which is the "
        "condition what-a-civilian-can-buy.md section 4.7 flagged as the thing to re-check. "
        "Re-checked 2026-08-23: still unresolved."
    ),
}


def automation_derived() -> dict:
    """What ECL's own figures imply, computed rather than quoted."""
    trad, cloud = AUTOMATION_EVIDENCE["traditional_lab"], AUTOMATION_EVIDENCE["cloud_lab"]
    t_per = trad["headcount_usd_per_year"] / trad["samples_per_year"]
    c_per = cloud["headcount_usd_per_year"] / cloud["samples_per_year"]
    return {
        "headcount_usd_per_sample_traditional": round(t_per, 2),
        "headcount_usd_per_sample_cloud": round(c_per, 2),
        "improvement_multiple": round(t_per / c_per, 2),
        "headcount_reduction_share": round(
            1 - cloud["headcount_usd_per_year"] / trad["headcount_usd_per_year"], 4),
        "throughput_multiple": round(cloud["samples_per_year"] / trad["samples_per_year"], 2),
        "_read_it_as": "A vendor's claimed order of magnitude for how far the technician layer can "
                       "fall, not a rate this repository can buy at.",
    }


def build() -> dict:
    costed = [cost_experiment(e) for e in EXPERIMENTS]
    return {
        "_what": "A bottom-up, published-rate estimate of what it would cost to contract the wet-lab "
                 "experiments this repository names. Unit rates are MEASURED from published academic "
                 "core-facility rate cards; quantities are ESTIMATES made here.",
        "_what_this_is_not": [
            "Not a quote. No vendor was contacted and nothing was purchased.",
            "Not a claim that any facility would accept this project, this client or these cells.",
            "Not an eligibility finding. The EMC cell lines are institution-gated by policy "
            "(what-a-civilian-can-buy.md section 4.1) and no rate card changes that.",
            "Not a measurement of consumption. Every quantity is this module's assumption.",
        ],
        "_cost": "$0 — arithmetic over published rate cards fetched read-only to literature-cache.",
        "_dominant_uncertainty": "The quantities, not the rates. A technician-hour count that is wrong "
                                 "by 2x moves every total by nearly 2x, because labour dominates each "
                                 "experiment costed here.",
        "external_commercial_markup": external_commercial_multiple(),
        "cost_structure": cost_structure(costed),
        "labour_sensitivity": labour_sensitivity(costed),
        "automation_evidence": {**AUTOMATION_EVIDENCE, "derived": automation_derived()},
        "experiments": costed,
        "portfolio_total_usd": round(sum(c["total_usd"] for c in costed), 2),
        "portfolio_total_note": "The sum of the five costed experiments. It is NOT a programme budget: "
                                "these are alternatives ranked elsewhere, not a sequence anyone plans to buy.",
        "rate_card": RATES,
    }


def main() -> int:
    doc = build()
    OUT.write_text(json.dumps(doc, indent=2) + "\n")
    print(f"wrote {OUT}")
    for e in doc["experiments"]:
        print(f"  {e['id']:32s} ${e['total_usd']:>10,.2f}")
    print(f"  {'PORTFOLIO (five alternatives)':32s} ${doc['portfolio_total_usd']:>10,.2f}")
    cs = doc["cost_structure"]["across_all_costed_share"]
    print("  cost structure across all five:")
    for k, v in sorted(cs.items(), key=lambda kv: -kv[1]):
        print(f"    {k:28s} {v*100:5.1f}%")
    ls = doc["labour_sensitivity"]
    print("  if hourly hands get cheaper (scales `hands` only):")
    print(f"    {'experiment':32s} {'today':>10s} {'x0.5':>10s} {'x0.1':>10s} {'free':>10s}")
    for k, r in ls["per_experiment"].items():
        a = r["at_factor"]
        print(f"    {k:32s} {a['1.0']:>10,.0f} {a['0.5']:>10,.0f} "
              f"{a['0.1']:>10,.0f} {a['0.0']:>10,.0f}")
    print(f"    {'FLOOR, five alternatives':32s} {'':>10s} {'':>10s} {'':>10s} "
          f"{ls['portfolio_floor_with_free_hands_usd']:>10,.0f}")
    m = doc["external_commercial_markup"]
    print(f"  external-commercial markup: {m['multiple']}x internal "
          f"(${m['internal_usd_per_hour']} -> ${m['external_commercial_usd_per_hour']}/hr)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
