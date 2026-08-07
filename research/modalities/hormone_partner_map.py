#!/usr/bin/env python3
"""THE NR4A3 5' PARTNER DRUGGABILITY MAP — which partner imports a druggable regulatory input?

WHY THIS EXISTS
---------------
NR4A3 breaks near its own start, so in every documented rearrangement the **5' partner supplies the
promoter**. The pharmacologically reachable handle on *fusion expression* is therefore the PARTNER's
regulatory input, not NR4A3's. One patient makes that concrete: a PGR::NR4A3 EMC treated with
tamoxifen (PMID 36103645). `emc-unexplored-treatment-lanes.md` §3.12 asked for the general form of
that observation -- a partner-by-partner map of what input each imports and whether it is druggable --
and predicted that EWSR1, the dominant partner, would be the hard case with an honest answer of "no".

⛔ NOTHING HERE ASSERTS EFFICACY, SAFETY, A THERAPEUTIC WINDOW OR CLINICAL READINESS FOR EMC. The one
clinical observation in this file is n = 1. Everything else is sequence-level and regulatory-level
annotation of published fusion reports.

METHOD, AND WHAT IT CAN AND CANNOT CONCLUDE
-------------------------------------------
1. RETRIEVAL. A Europe PMC corpus was fetched on a GitHub Actions runner (the dev sandbox egress
   proxy 403s www.ebi.ac.uk on CONNECT -- measured 2026-08-07, HTTP 000 to both Europe PMC and RCSB).
   Query: `NR4A3 AND (fusion OR translocation) AND (chondrosarcoma OR myxoid OR sarcoma)`.
   530 records returned; 345 with open-access full text on disk, published to the `literature-cache`
   branch under
   `literature/nr4a3-fusion-partners/` (run 31175693393, 2026-08-07).
2. ENUMERATION. Every `<GENE>-NR4A3` / `NR4A3-<GENE>` token in the corpus was extracted with its
   sentence and PMCID. Deliberately dumb and exhaustive, so the partner list is READ rather than
   recalled. Old symbols and OCR variants of the same gene (RBP56 = TAF15; ESWR1/EWSRI/EWS1 = EWSR1)
   are folded; non-partner hits (GAL4/GST fusion-protein constructs, BLIMP1 in a T-cell knockout
   paper, NR4A2 in a paralogue sentence) are excluded and named below rather than silently dropped.
3. GRADING. Each partner gets an evidence TIER for the question "does this partner import a druggable
   regulatory input?". ⛔ A tier is assigned ONLY from a retrieved sentence. A partner for which the
   sweep retrieved no characterisation of its promoter's inducible inputs is graded
   NO_INDUCIBLE_INPUT_RETRIEVED -- which is a RETRIEVAL negative over a stated corpus, NOT a claim
   that no such input exists. That distinction is the whole honesty of this file.
4. REACH. The fraction of EMC patients any hormonal route could serve is computed from the two
   partner-genotyped EMC cohorts this repository already cites, with Wilson 95% intervals.

⚠ WHAT THIS FILE MAY NOT BE READ AS. It is an annotation of the published record, not a screen. It
runs no docking, predicts no binding and measures no transcription. "Druggable input" here means
"a drug exists that acts on the named regulatory axis" -- it does not mean the drug would lower this
fusion's expression in this tumour, which nobody has measured for any partner except by the single
tamoxifen observation below.

Output: hormone-partner-lane.json
"""
from __future__ import annotations

import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "hormone-partner-lane.json")

CORPUS = {
    "branch": "literature-cache",
    "path": "literature/nr4a3-fusion-partners/",
    "query": "NR4A3 AND (fusion OR translocation) AND (chondrosarcoma OR myxoid OR sarcoma)",
    "n_records_returned": 530,
    "n_fulltext_on_disk": 345,
    "⚠_which_number_the_enumeration_used": "345. The regex sweep reads FULL TEXT, so it saw the 345 "
        "open-access records with a .txt on disk, not all 530 Europe PMC returned. A partner named "
        "only in one of the 185 abstract-only or closed records is invisible to it. ⛔ This is stated "
        "because the first draft of this file wrote 346 — a directory FILE count, including "
        "_index.json — as if it were a record count. A count that was never measured is the bug rule "
        "1 exists for, and it was caught by re-reading the index rather than the directory listing.",
    "actions_run_id": 31175693393,
    "fetched": "2026-08-07",
    "why_ci": "the dev sandbox egress proxy 403s www.ebi.ac.uk and RCSB on CONNECT; measured HTTP 000 "
              "to both from this sandbox on 2026-08-07 before routing out (CLAUDE.md §6)",
}

# ── The retrieved record. Every row carries the PMCID and the verbatim sentence it rests on. ────────
# `tier` vocabulary, strongest first:
#   HORMONE_RESPONSIVE_TREATED  a retrieved source states the partner's expression is hormone-driven
#                               AND reports a drug acting on that axis given to a patient with this
#                               fusion, with an outcome.
#   HORMONE_RESPONSIVE_UNTREATED  the partner is a canonical target of a druggable hormone axis per a
#                               retrieved source, but no NR4A3-fusion case was treated on that axis.
#   CIS_INPUT_CHARACTERISED     a retrieved source characterises the imported cis-regulatory input,
#                               and no drug acts on it.
#   NO_INDUCIBLE_INPUT_RETRIEVED  the sweep retrieved no source characterising a druggable inducible
#                               input for this partner's promoter. NOT a claim that none exists.
#   PARTNER_NOT_RETRIEVED       §3.12 lists the partner; this sweep found no source for it at all.
PARTNERS = [
    {
        "partner": "EWSR1", "n_papers_in_corpus": 87, "context": "EMC — the dominant partner",
        "tier": "NO_INDUCIBLE_INPUT_RETRIEVED",
        "imported_input": "the EWSR1 locus's own promoter. No retrieved sentence in this corpus "
                          "characterises it as responsive to any druggable stimulus; the FET genes "
                          "are described throughout as ubiquitously expressed.",
        "druggable_input": False,
        "evidence": [{"pmcid": "PMC9489176", "quote":
                      "Seventy percent of EMC are characterized by a chromosomal rearrangement "
                      "involving the NR4A3 gene on chromosome 9 with EWSR1 on chromosome 22, t(9;22)."}],
        "note": "§3.12 predicted EWSR1 would be the hard case and that the honest answer might be "
                "'no'. Over 345 full-text records the answer is 'no source retrieved', which is "
                "the strongest form of no this instrument can return -- bounded by the 185 records "
                "whose full text was not open-access.",
    },
    {
        "partner": "TAF15", "n_papers_in_corpus": 36, "context": "EMC — second most common",
        "tier": "NO_INDUCIBLE_INPUT_RETRIEVED",
        "imported_input": "the TAF15 locus's promoter; same FET family as EWSR1 and FUS.",
        "druggable_input": False,
        "evidence": [{"pmcid": "PMC9489176", "quote":
                      "Rearrangements of NRA4A3 with TAF15, TCF12, TFG, and HSPA8 have also been "
                      "described and are associated with poorer outcomes."}],
        "note": "the corpus also carries the legacy symbol RBP56 for this gene (3 papers); folded here.",
    },
    {
        "partner": "TCF12", "n_papers_in_corpus": 11, "context": "EMC — rare",
        "tier": "NO_INDUCIBLE_INPUT_RETRIEVED",
        "imported_input": "the TCF12 (bHLH E-protein) locus's promoter.",
        "druggable_input": False,
        "evidence": [{"pmcid": "PMC7308468", "quote":
                      "Rare fusion transcripts have been described, which are TCF12-NR4A3, "
                      "TFG-NR4A3, and HSPA8-NR4A3"}],
    },
    {
        "partner": "TFG", "n_papers_in_corpus": 5, "context": "EMC — rare",
        "tier": "NO_INDUCIBLE_INPUT_RETRIEVED",
        "imported_input": "the TFG locus's promoter.",
        "druggable_input": False,
        "evidence": [{"pmcid": "PMC7308468", "quote":
                      "Rare fusion transcripts have been described, which are TCF12-NR4A3, "
                      "TFG-NR4A3, and HSPA8-NR4A3"}],
    },
    {
        "partner": "FUS", "n_papers_in_corpus": 1, "context": "EMC — rare",
        "tier": "NO_INDUCIBLE_INPUT_RETRIEVED",
        "imported_input": "the FUS locus's promoter; third FET-family member.",
        "druggable_input": False,
        "evidence": [{"pmcid": "PMC12504171", "quote":
                      "Common fusions include EWSR1::NR4A3, TAF15::NR4A3 and FUS::NR4A3."}],
        "note": "⚠ only ONE corpus paper names FUS::NR4A3, and PMC9489176's own partner list omits "
                "it. The repository's biology evidence file lists FUS among the rare partners; the "
                "retrieval here is thinner than that file implies and is recorded as such.",
    },
    {
        "partner": "HSPA8", "n_papers_in_corpus": 2, "context": "EMC — rare",
        "tier": "NO_INDUCIBLE_INPUT_RETRIEVED",
        "imported_input": "the HSPA8 (heat-shock cognate 70) locus's promoter.",
        "druggable_input": False,
        "evidence": [{"pmcid": "PMC7308468", "quote":
                      "Rare fusion transcripts have been described, which are TCF12-NR4A3, "
                      "TFG-NR4A3, and HSPA8-NR4A3"}],
        "note": "⚠ THE ONE ROW MOST WORTH A TARGETED FOLLOW-UP, AND DELIBERATELY NOT GRADED HIGHER. "
                "A heat-shock-family promoter is the only partner here whose gene family is known to "
                "carry an inducible element with a drug class aimed at it (HSF1). But NO retrieved "
                "sentence characterises the HSPA8 promoter's inducibility, and HSPA8 is the "
                "constitutively-expressed cognate rather than the stress-inducible HSPA1A. Grading "
                "this from gene-family intuition rather than from a retrieved measurement is exactly "
                "the move this file refuses.",
    },
    {
        "partner": "PGR", "n_papers_in_corpus": 4,
        "context": "EMC — ONE patient (PMID 36103645); also a recurrent event in uterine epithelioid "
                   "leiomyosarcoma, which is a DIFFERENT disease",
        "tier": "HORMONE_RESPONSIVE_TREATED",
        "imported_input": "the PGR promoter, which is oestrogen-driven.",
        "druggable_input": True,
        "drug_axis": "ER — SERM (tamoxifen), and by extension the rest of the endocrine armamentarium",
        "evidence": [
            {"pmcid": "PMC9489176", "quote":
             "The results of next-generation sequencing revealed gene fusion of progesterone "
             "receptor, PGR (exon2) to the 5′ untranslated region (UTR) of NR4A3 (exon2)"},
            {"pmcid": "PMC9489176", "quote":
             "Given the gene fusion involving PGR, driven by estrogen, and outlier expression of "
             "ESR1, PGR, and GREB1 further indicative of an activated estrogen-signaling pathway, a "
             "multidisciplinary precision medicine tumor board recommended anti-estrogen therapy."},
            {"pmcid": "PMC9489176", "quote":
             "Since initiation of tamoxifen was over 5 years ago, she has had ongoing decrease in "
             "size of her pulmonary nodules and no evidence of disease progression despite "
             "intraoperative rupture and previously rapid, aggressive recurrences"},
            {"pmcid": "PMC9489176", "quote":
             "Previously, Chiang et al reported four cases of uterine epithelioid leiomyosarcoma "
             "also with a PGR-NR4A3 fusion. However, the clinical implications of anti-estrogen "
             "treatment were not mentioned."},
            {"pmcid": "PMC12730577", "quote":
             "PGR gene fusions define a subset of uterine epithelioid leiomyosarcoma, with recurrent "
             "rearrangements such as PGR::NR4A3 representing the most commonly reported events"},
        ],
        "note": "⚠ THE INDEX PATIENT IS EWSR1-FISH-NEGATIVE CELLULAR-VARIANT EMC. That matters twice: "
                "it is the variant in which non-EWSR1 partners concentrate, and it means the case "
                "would not have been counted as fusion-positive by an EWSR1-break-apart assay.",
    },
    {
        "partner": "GREB1", "n_papers_in_corpus": 6,
        "context": "⛔ NOT EMC — uterine tumour resembling ovarian sex-cord tumour (UTROSCT) / "
                   "GREB1-rearranged uterine sarcoma",
        "tier": "HORMONE_RESPONSIVE_UNTREATED",
        "imported_input": "the GREB1 promoter. GREB1 (Growth Regulation by Estrogen in Breast cancer 1) "
                          "is a canonical direct oestrogen-receptor target gene, and PMC9489176 uses "
                          "GREB1 outlier expression as its READ-OUT of an activated oestrogen axis.",
        "druggable_input": True,
        "drug_axis": "ER — same axis as PGR",
        "evidence": [
            {"pmcid": "PMC7489201", "quote":
             "these included ESR1-NCOA3 (N = 15), ESR1-NCOA2 (N = 8), GREB1-NCOA1 (N = 5), "
             "GREB1-NCOA2 (N = 4), GREB1-CTNNB1 (N = 1), GREB1-NR4A3 (N = 1), GREB1-SS18 (N = 1)"},
            {"pmcid": "PMC7490989", "quote":
             "A subsequent report characterized the features of 4 GREB1-rearranged uterine sarcomas "
             "(GREB1-NCOA1, GREB1-NR4A3, GREB1-SS18, and GREB1-NCOA1)"},
        ],
        "note": "⭐ NEW AGAINST §3.12, WHICH DID NOT LIST GREB1 AT ALL. It is the SECOND "
                "oestrogen-axis 5' partner of NR4A3 and it strengthens the general principle — but "
                "⛔ it does NOT widen the EMC route by one patient, because every retrieved "
                "GREB1::NR4A3 case is a uterine tumour. Both hormone-responsive partners are "
                "gynaecologic-tract events; one of them turned up once in EMC.",
    },
    {
        "partner": "SMARCA2", "n_papers_in_corpus": 3, "context": "EMC — one case (foot)",
        "tier": "NO_INDUCIBLE_INPUT_RETRIEVED",
        "imported_input": "the SMARCA2 locus's promoter.",
        "druggable_input": False,
        "evidence": [{"pmcid": "PMC8555238", "quote":
                      "Only one case of extraskeletal myxoid chondrosarcoma of the foot was described "
                      "with a SMARCA2-NR4A3 fusion (with the same breakpoint at SMARCA2 gene)"}],
        "note": "⚠ SMARCA2 is separately a DEGRADER TARGET elsewhere in this repository (the "
                "SMARCA2/4 known-answer control). Different object entirely — here it is a 5' "
                "promoter donor in one EMC case, not a protein being degraded. Recorded because a "
                "text search for SMARCA2 in this repo returns mostly the other thing.",
    },
    {
        "partner": "LSM14A", "n_papers_in_corpus": 1, "context": "EMC — adolescent case",
        "tier": "NO_INDUCIBLE_INPUT_RETRIEVED",
        "imported_input": "the LSM14A locus's promoter.",
        "druggable_input": False,
        "evidence": [{"pmcid": "PMC12750061", "quote":
                      "Future work should prioritize establishing a dedicated registry for adolescent "
                      "EMCs and investigating age-specific mechanisms, including functional "
                      "interrogation of the LSM14A-NR4A3 fusion"}],
    },
    {
        "partner": "PRRC1", "n_papers_in_corpus": 1,
        "context": "EMC — novel, reported in a CONFERENCE ABSTRACT",
        "tier": "NO_INDUCIBLE_INPUT_RETRIEVED",
        "imported_input": "the PRRC1 locus's promoter.",
        "druggable_input": False,
        "evidence": [{"pmcid": "PMC9379246", "quote":
                      "Extraskeletal chondrosarcoma involving NR4A3-PRRC1 fusion has not been "
                      "reported before in the literature."}],
        "note": "⚠ abstract-only. Not peer-reviewed full text; graded but flagged.",
    },
    {
        "partner": "SCPP gene cluster (4q13)", "n_papers_in_corpus": 2,
        "context": "⛔ NOT EMC — acinic cell carcinoma of salivary gland",
        "tier": "CIS_INPUT_CHARACTERISED",
        "imported_input": "the salivary secretory-protein (SCPP) cluster ENHANCER, juxtaposed to the "
                          "NR4A3 transcription start site. ⭐ This is enhancer hijacking, not a "
                          "chimeric protein: the imported input up-regulates wild-type NR4A3.",
        "druggable_input": False,
        "evidence": [{"pmcid": "PMC8085676", "quote":
                      "SCPP) gene cluster at 4q13 to the transcription start site of transcription "
                      "factor nuclear receptor subfamily 4 group A member 3 (NR4A3) at 9q31, leading "
                      "to the up-regulation of NR4A3"}],
        "note": "⭐ THE STRONGEST INDEPENDENT SUPPORT FOR §3.12'S GENERAL PRINCIPLE, and it comes "
                "from outside EMC. A whole second disease exists in which NR4A3's expression is "
                "driven by an imported cis-regulatory element from the partner locus. It also shows "
                "the principle's limit: knowing the imported input tells you what drives the gene, "
                "and says nothing about whether a drug can turn that input down.",
    },
]

# §3.12 named twelve partners. These three produced ZERO hits over 346 records.
NOT_RETRIEVED = [
    {"partner": "ACTB", "listed_in": "emc-unexplored-treatment-lanes.md §3.12",
     "tier": "PARTNER_NOT_RETRIEVED"},
    {"partner": "CARMN", "listed_in": "emc-unexplored-treatment-lanes.md §3.12",
     "tier": "PARTNER_NOT_RETRIEVED"},
    {"partner": "SLCO5A1", "listed_in": "emc-unexplored-treatment-lanes.md §3.12",
     "tier": "PARTNER_NOT_RETRIEVED"},
]

# Excluded regex hits, named rather than silently dropped.
EXCLUDED = [
    {"token": "RBP56", "reason": "legacy symbol for TAF15; folded into that row"},
    {"token": "ESWR1 / EWSRI / EWS1", "reason": "OCR/typo variants of EWSR1; folded"},
    {"token": "GAL4, GST", "reason": "laboratory fusion-protein constructs (PMC7565926), not "
                                     "patient rearrangements"},
    {"token": "BLIMP1", "reason": "'BLIMP1/NR4A3 dual KO' in a T-cell exhaustion paper "
                                  "(PMC11466849) — a genotype, not a fusion"},
    {"token": "NR4A2", "reason": "a paralogue named beside NR4A3, not a partner"},
]

# ── Reach. Denominators are OWNED by nr4a3-emc-biology-evidence.md; this file does not re-derive them.
COHORTS = [
    {"cohort": "Modern Pathology 2023", "pmid": "36948401", "n": 58, "n_pgr": 0, "n_greb1": 0,
     "owner": "research/manuscripts/nr4a3-emc-biology-evidence.md — Hypothesis 2, pillar 1"},
    {"cohort": "Agaram, Hum Pathol 2014", "pmcid": "PMC4015728", "n": 26, "n_pgr": 0, "n_greb1": 0,
     "owner": "research/manuscripts/nr4a3-emc-biology-evidence.md — Hypothesis 2, pillar 1"},
]


def wilson(k: int, n: int, z: float = 1.959963984540054):
    """Wilson score interval — the repository's fixed method for a proportion (POLICY-evidence §)."""
    if n == 0:
        return (None, None, None)
    p = k / n
    d = 1.0 + z * z / n
    centre = (p + z * z / (2 * n)) / d
    half = (z / d) * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (p, max(0.0, centre - half), min(1.0, centre + half))


def build() -> dict:
    n_total = sum(c["n"] for c in COHORTS)
    k_total = sum(c["n_pgr"] for c in COHORTS)
    per_cohort = []
    for c in COHORTS:
        p, lo, hi = wilson(c["n_pgr"], c["n"])
        per_cohort.append({**c, "proportion": p, "wilson95_lo": lo, "wilson95_hi": hi})
    p, lo, hi = wilson(k_total, n_total)

    tiers = {}
    for row in PARTNERS + NOT_RETRIEVED:
        tiers.setdefault(row["tier"], []).append(row["partner"])

    emc_partners = [r["partner"] for r in PARTNERS if not r["context"].startswith("⛔")]
    druggable_in_emc = [r["partner"] for r in PARTNERS
                        if r.get("druggable_input") and not r["context"].startswith("⛔")]

    return {
        "_title": "The NR4A3 5' partner druggability map — what regulatory input does each partner "
                  "import, and is it druggable?",
        "_status": "live",
        "_generated_by": "research/modalities/hormone_partner_map.py",
        "_cost": "$0 — CPU/CI only. One Europe PMC retrieval on a GitHub-hosted runner; no GPU, "
                 "no rental, nothing dispatched to a paid provider.",
        "_lane": "emc-unexplored-treatment-lanes.md §3.12 (ranked #12)",
        "⛔_scope": "Annotation of the published record. No docking, no binding prediction, no "
                    "transcription measurement. Asserts no efficacy, safety, therapeutic window or "
                    "clinical readiness for EMC.",
        "corpus": CORPUS,

        "headline": (
            "⛔ A HORMONAL ROUTE IN EMC REACHES ESSENTIALLY NOBODY, AND THE ROUTE MUST SAY SO IN ITS "
            "OWN FIRST SENTENCE. PGR::NR4A3 is ONE reported EMC patient in the world literature "
            "(PMID 36103645) and ZERO of the %d partner-genotyped EMC cases in the two cohorts this "
            "repository cites. ⭐ The GENERAL principle §3.12 proposed nevertheless SURVIVES and is "
            "strengthened by two findings this sweep added: a SECOND oestrogen-axis partner "
            "(GREB1::NR4A3) and a whole second disease in which the partner locus imports a "
            "cis-regulatory input to NR4A3 (the SCPP enhancer in salivary acinic cell carcinoma). "
            "⛔ Neither adds an EMC patient — both hormone-responsive partners are gynaecologic-tract "
            "events. ⛔ And the dominant partner answers NO: across 345 full-text records, no "
            "retrieved source characterises the EWSR1 promoter as responsive to any druggable "
            "stimulus."
        ) % n_total,

        "reach": {
            "_asks": "What fraction of EMC patients could a hormonal route possibly serve?",
            "_method": "Wilson 95% score interval on the PGR-partnered fraction, per the "
                       "repository's fixed pooling method (systems/POLICY-evidence.md).",
            "per_cohort": per_cohort,
            "pooled": {
                "n": n_total, "k_pgr_partnered": k_total, "proportion": p,
                "wilson95_lo": lo, "wilson95_hi": hi,
                "⚠_assumption": "the two cohorts are treated as NON-OVERLAPPING. That is required by "
                                "POLICY-evidence and it is NOT VERIFIED here — neither report's "
                                "accrual institutions were checked. If they overlap the denominator "
                                "is smaller and the upper bound wider, so the pooled figure is the "
                                "OPTIMISTIC end of the honest range.",
            },
            "world_literature_emc_cases": 1,
            "reading": "Zero events in %d genotyped cases. The Wilson upper bound is the number that "
                       "should travel with this route: the hormone-responsive-partner fraction of EMC "
                       "is bounded above at roughly %.1f%%, and the only observed EMC case is n = 1."
                       % (n_total, 100.0 * hi),
            "⛔_what_this_does_not_say": [
                "It does not say the true fraction is zero. Zero events bound a rate; they do not "
                "measure one, and the bound is wide at n = %d." % n_total,
                "⚠ It may UNDERCOUNT, and the source paper says why in its own words: the fusion "
                "'would have not been captured by existing commercial vendors which use panel-based "
                "approaches that do not include PGR or N4A3' (PMC9489176). Both cited cohorts "
                "genotyped by targeted assays, so a PGR-partnered case could be invisible to them. "
                "⛔ This cuts BOTH ways and is not a reason to inflate the estimate — it is a reason "
                "the honest statement is a bound with a stated blind spot, not a point estimate.",
                "The index case was EWSR1-FISH-negative cellular-variant EMC, so an EWSR1 "
                "break-apart assay would not have called it fusion-positive at all.",
            ],
        },

        "partners": PARTNERS,
        "partners_not_retrieved": NOT_RETRIEVED,
        "excluded_regex_hits": EXCLUDED,
        "tier_summary": tiers,
        "counts": {
            "n_partners_with_at_least_one_retrieved_source": len(PARTNERS),
            "n_partners_listed_in_3_12_with_zero_sources": len(NOT_RETRIEVED),
            "n_partners_reported_in_EMC": len(emc_partners),
            "n_partners_importing_a_druggable_input_in_EMC": len(druggable_in_emc),
            "which_druggable_in_EMC": druggable_in_emc,
        },

        "corrections_to_3_12": [
            {"what": "§3.12's partner list names ACTB, CARMN and SLCO5A1.",
             "measured": "ZERO retrieved sources for any of the three over 345 full-text records.",
             "action": "they are carried as PARTNER_NOT_RETRIEVED, not as partners. A partner list "
                       "with unsourced entries inflates the apparent breadth of the route."},
            {"what": "§3.12's list omits GREB1.",
             "measured": "GREB1-NR4A3 appears in 6 corpus papers as a recurrent-fusion-series member "
                         "in UTROSCT / GREB1-rearranged uterine sarcoma.",
             "action": "ADDED. It is the second oestrogen-axis partner and the single best support "
                       "for the general principle — and it adds no EMC patient."},
            {"what": "§3.12's list omits the SCPP cluster.",
             "measured": "SCPP-NR4A3 in salivary acinic cell carcinoma, characterised as an "
                         "enhancer-to-TSS juxtaposition up-regulating NR4A3.",
             "action": "ADDED as the cross-disease proof of the imported-cis-input principle."},
            {"what": "§3.12 quotes the outcome sentence as 'Since initiation of tamoxifen IS over 5 "
                     "years ago'.",
             "measured": "the retrieved full text reads 'Since initiation of tamoxifen WAS over 5 "
                         "years ago'.",
             "action": "the verbatim retrieved wording is used here. Immaterial to the claim; "
                       "recorded because §3.12 presents it as a verbatim quote."},
        ],

        "⛔_the_clean_negative_that_travels_with_this_route": (
            "NR4A3 is a MAPK-induced immediate-early gene, so 'use a MEK inhibitor to lower fusion "
            "expression' is the obvious idea — and it is architecturally impossible, because the "
            "fusion allele does not use NR4A3's own IEG promoter. The same argument closes "
            "β-adrenergic, angiotensin-II and serum-response modulation of the fusion. ⭐ THIS SWEEP "
            "STRENGTHENS THAT ARGUMENT RATHER THAN MERELY REPEATING IT: across every partner "
            "retrieved here the imported input is the PARTNER's, never NR4A3's — including in a "
            "second disease (SCPP/AciCC) where the imported element is an enhancer rather than a "
            "promoter. The generalisation is now supported by 12 partners across 3 tumour types "
            "instead of by one case report."
        ),

        "what_would_change_this": [
            {"item": "A partner-stratified EMC series genotyped by unbiased RNA-seq rather than a "
                     "targeted panel.",
             "why": "the only cited denominators come from assays that PMC9489176 states would have "
                    "missed its own case. This is the single observation that could move the reach "
                    "figure in either direction.",
             "cost": "$0 to search for; the data are somebody else's to generate."},
            {"item": "Any report of anti-oestrogen therapy in a GREB1::NR4A3 or PGR::NR4A3 UTERINE "
                     "tumour with an outcome.",
             "why": "PMC9489176 notes the four uterine PGR-NR4A3 cases were reported without "
                    "mention of anti-oestrogen treatment. An outcome there would take the axis from "
                    "n = 1 to n > 1 — in a different disease, which is exactly how this route would "
                    "become publishable beyond a case note.",
             "cost": "$0 — literature only."},
            {"item": "A retrieved characterisation of the HSPA8 promoter's inducible elements.",
             "why": "the only partner whose gene family plausibly carries a druggable inducible "
                    "input. Currently ungraded because nothing was retrieved.",
             "cost": "$0 — one targeted Europe PMC query through CI."},
        ],

        "map_edits_required": [],
        "_why_map_edits_is_empty_here": (
            "Every edit this lane owes is routed through "
            "research/manuscripts/nr2f1-hormone-lane-map-edits.json, which is the single file the "
            "map's owner applies. This lane adds a ROUTE, not a requirement: it changes no gate, no "
            "price, no rung and no claim ceiling on nr4a3-program-map.md, so it owes that page "
            "nothing."
        ),
    }


def main() -> int:
    art = build()
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(art, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    r = art["reach"]["pooled"]
    print("wrote %s" % OUT)
    print("pooled PGR-partnered EMC: %d/%d  Wilson95 [%.4f, %.4f]"
          % (r["k_pgr_partnered"], r["n"], r["wilson95_lo"], r["wilson95_hi"]))
    print("partners with a retrieved source: %d; importing a druggable input IN EMC: %d (%s)"
          % (art["counts"]["n_partners_with_at_least_one_retrieved_source"],
             art["counts"]["n_partners_importing_a_druggable_input_in_EMC"],
             ", ".join(art["counts"]["which_druggable_in_EMC"]) or "none"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
