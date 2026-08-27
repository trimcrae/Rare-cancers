#!/usr/bin/env python3
"""Partner-stratified pooled synthesis of published EMC systemic-therapy and outcome data.

WHY THIS EXISTS
---------------
`research/manuscripts/program/emc-unexplored-treatment-lanes.md` s3.2 ranks "fusion-variant
stratification (EWSR1 vs TAF15)" #2 of twelve unexplored lanes and calls it "the cheapest
paper on the board": several lines bear on the NR4A3 5' partner as a treatment-relevant
biomarker, and **nobody has pooled them**. This file does the pooling, and it is the ONE
HOME of every number in that synthesis (CLAUDE.md rule 1).
  ⛔ *Superseded, retained: "four independent lines converge on the NR4A3 5' partner".*
  Appendix A14 of the manuscript retracted that phrasing -- two of the four are not
  independent of each other (the mechanism line and the TKI-response line share the
  Milan/Aviano consortium and a senior investigator with a trial site), and the prevalence
  line was never offered as converging evidence for clinical relevance. The retraction
  reached the manuscript on 2026-08-26 and NOT this docstring, where it stood undeclared
  until a blind seat found it. A retraction that reaches some of its copies is not a
  retraction -- the same finding this repository recorded as Appendix A5.

METHOD IS NOT A CHOICE HERE. `systems/POLICY-evidence.md` s2 is the repository's binding
evidence contract for clinical proportions:
  * s2.2 crude denominator-weighted proportions, **Wilson score** 95% intervals;
  * s2.1 a cohort is pooled only with **explicit integer {events, denom}**, a true outcome
    (not the inclusion criterion), and a **non-overlapping** population;
  * s2.3 where populations may overlap the **smaller** cohort is `pool: false` with
    `contextReason: "population-overlap"`;
  * s2.2 heterogeneity is reported as the **range of per-cohort rates**, not I^2;
  * s1.3 `sourceId` is the document the number was READ IN; a review is
    `provenance: "secondary"` and carries `primaryRef`.
The manuscript's random-effects (DerSimonian-Laird) pooler in `research/meta/meta-analysis.mjs`
is the OTHER method in this repo and is deliberately NOT used: the per-stratum denominators
and event counts are far too small for a between-study variance to be estimable. The range
is DERIVED into `method.not_used` rather than typed here -- see `_stratum_extent()`. The
typed pair "2-19 patients and 0-10 events" that used to stand in this sentence went stale
the day Huang 2023's counts were pooled and is retained as superseded in the manuscript's
s2.5 and in Appendix A.

Fisher's exact p-values are reported as a clearly-labelled **post-hoc descriptive**
statistic. No published report performed this test; it is not a prespecified analysis and
is not used to license any claim.

Stdlib only.
Run:     python3 research/manuscripts/emc_fusion_partner_pooling.py
Writes:  research/manuscripts/fusion-partner/emc-fusion-partner-pooling.json
Verify:  python3 research/manuscripts/emc_fusion_partner_pooling.py --check

⛔ `_do_not_hand_edit` WAS A PROMISE THIS FILE COULD NOT KEEP (found 2026-08-08, in the same
session that added the Huang 2023 clinical event counts to `COHORTS`). Until that day this module
parsed NO arguments: `--check` was accepted by the shell, ignored by the script, and the artifact
was REGENERATED and OVERWRITTEN whatever you passed -- exiting 0 unconditionally. So the banner the
artifact carries in its own body, telling every reader that a number here is computed and not
typed, was unenforced: **a hand edit to a pooled clinical proportion persisted and nothing could
say so.** That is a medical-integrity hole in a file whose entire content is clinical event counts.
⚠ The same defect was found and repaired the same day in `emc_systemic_therapy_pooling.py`; this is
the second instance, and the implementation below deliberately matches that one rather than
inventing a second idiom.

⭐ THE RE-DERIVATION GOES TO MEMORY, NEVER TO `OUT`. A verify mode that regenerates the artifact and
then finds it identical is comparing the generator against itself and cannot fail -- which is
precisely how a previous verify mode in this repository no-opped into the behaviour it replaced,
producing no symptom. `build()` is pure over this module's `COHORTS`/`CITATIONS` tables and touches
no file; `check()` reads the committed artifact and compares. `research/manuscripts/tests/
test_emc_fusion_partner_pooling_check.py` perturbs the REAL committed artifact on disk and asserts
the REAL `main(["--check"])` refuses it AND writes nothing -- because a guard exercised only against
a mock is a test of the mock.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
from datetime import datetime, timezone

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(REPO, "research", "manuscripts", "fusion-partner", "emc-fusion-partner-pooling.json")

Z95 = 1.959963984540054  # two-sided normal quantile at 95%


# ---------------------------------------------------------------------------
# statistics (POLICY-evidence.md s2.2)
# ---------------------------------------------------------------------------
def wilson(events: int, denom: int, z: float = Z95) -> dict:
    """Wilson score interval on a binomial proportion.

    Wilson rather than the normal approximation because every stratum here is small and
    several sit exactly at 0 %, where the normal interval collapses to a point and lies
    about the evidence. POLICY-evidence.md s2.2 names this interval by construction.
    """
    if denom <= 0:
        raise ValueError("denominator must be positive")
    p = events / denom
    d = 1.0 + z * z / denom
    centre = (p + z * z / (2 * denom)) / d
    half = (z / d) * math.sqrt(p * (1 - p) / denom + z * z / (4 * denom * denom))
    lo, hi = max(0.0, centre - half), min(1.0, centre + half)
    return {
        "events": events,
        "denom": denom,
        "proportion": round(p, 4),
        "percent": round(100 * p, 1),
        "ci95_lo_percent": round(100 * lo, 1),
        "ci95_hi_percent": round(100 * hi, 1),
        "interval": "Wilson score, 95%",
    }


def _logchoose(n: int, k: int) -> float:
    return math.lgamma(n + 1) - math.lgamma(k + 1) - math.lgamma(n - k + 1)


def fisher_exact_two_sided(a: int, b: int, c: int, d: int) -> float:
    """Two-sided Fisher exact p for the 2x2 table [[a, b], [c, d]].

    Summed over every table with the same margins whose probability does not exceed the
    observed table's (the conventional two-sided definition). Implemented here rather than
    imported because this file is stdlib-only so it runs in CI with no environment build
    (CLAUDE.md s6, "pull, don't solve").
    """
    row1, row2 = a + b, c + d
    col1 = a + c
    total = row1 + row2

    def prob(x: int) -> float:
        return math.exp(
            _logchoose(row1, x) + _logchoose(row2, col1 - x) - _logchoose(total, col1)
        )

    p_obs = prob(a)
    lo = max(0, col1 - row2)
    hi = min(col1, row1)
    p = 0.0
    for x in range(lo, hi + 1):
        px = prob(x)
        if px <= p_obs * (1 + 1e-9):
            p += px
    return min(1.0, p)


def zero_death_patients_to_reconcile(taf: dict, comparator: dict) -> dict:
    """How many further TAF15 patients with ZERO deaths would pull the pooled TAF15 point estimate
    down inside the comparator arm's Wilson interval.

    ⛔ THIS EXISTS BECAUSE THE PAPER STATED A FALSIFICATION THRESHOLD IT HAD NEVER COMPUTED. Round 7
    of the hardening series (2026-08-27) had falsifier #5 assert that "a third cohort of similar size
    disagreeing would put the pooled point estimate inside the comparator arm's interval". Two blind
    seats computed it independently and it is arithmetically false; re-derived here a third time from
    the artifact's own counts, a third cohort of 7 or 8 TAF15 patients with no deaths at all leaves
    the pooled point estimate at 31.8% or 30.4%, against a comparator upper bound of 20.8%.

    ⚠ A STATED FALSIFIER THAT THE STUDY DESCRIBING IT CANNOT REACH IS WORSE THAN NO FALSIFIER: it
    reads as a standing invitation to check while being unreachable by the evidence it names. So the
    threshold is DERIVED here from the counts rather than asserted in prose, and the paper prints
    whatever this returns.

    The comparator arm is held FIXED — it gains no patients from the hypothetical cohort. That is the
    conservative direction and the defensible one: letting the comparator grow too drives its own
    upper bound DOWN (its event count is fixed), which makes the threshold recede rather than
    approach, so modelling growth in both arms would overstate how reachable the falsifier is.
    """
    events = taf["events"]
    hi = comparator["ci95_hi_percent"]
    extra = 0
    # events stay fixed: the hypothetical patients contribute denominator only.
    while 100.0 * events / (taf["denom"] + extra) > hi:
        extra += 1
    return {
        "further_zero_death_taf15_patients_required": extra,
        "total_taf15_denominator_required": taf["denom"] + extra,
        "comparator_ci95_hi_percent": hi,
        "_method": (
            "Smallest k such that events/(denom+k) <= the comparator arm's Wilson 95% upper bound, "
            "with the TAF15 event count and the whole comparator arm held fixed. Derived, never typed."
        ),
    }


def contrast(name: str, taf: dict, other: dict, note: str) -> dict:
    """One TAF15-vs-comparator contrast with both arms' Wilson intervals."""
    a, b = taf["events"], taf["denom"] - taf["events"]
    c, d = other["events"], other["denom"] - other["events"]
    return {
        "id": name,
        "taf15_arm": taf,
        "comparator_arm": other,
        "comparator_minus_taf15_percentage_points": round(
            100 * (other["events"] / other["denom"] - taf["events"] / taf["denom"]), 1
        ),
        "fisher_exact_two_sided_p": round(fisher_exact_two_sided(a, b, c, d), 4),
        "fisher_note": (
            "POST-HOC DESCRIPTIVE ONLY. Not prespecified, not performed in any source "
            "report, not corrected for the multiple endpoints on this page, and not used "
            "to license any claim."
        ),
        "note": note,
    }


def heterogeneity(rates: list[dict]) -> dict:
    """POLICY-evidence.md s2.2: show how much the cohorts disagree, do not model it away."""
    vals = [r["percent"] for r in rates]
    return {
        "per_cohort_percent": {r["cohort"]: r["percent"] for r in rates},
        "range_percent": [min(vals), max(vals)],
        "spread_percent": round(max(vals) - min(vals), 1),
        "method_note": (
            "Range of per-cohort crude rates over {k} cohorts, per POLICY-evidence.md s2.2. "
            "I-squared is deliberately not computed: at these stratum sizes a between-study "
            "variance estimate would be uninterpretable."
        ).format(k=len(rates)),
    }


# ---------------------------------------------------------------------------
# citations (POLICY-evidence.md s1)
# ---------------------------------------------------------------------------
CITATIONS = {
    "stacchiotti2014": {
        "short": "Stacchiotti 2014 (sunitinib series)",
        "type": "journal-article",
        "title": "Activity of sunitinib in extraskeletal myxoid chondrosarcoma.",
        "authors": "Stacchiotti S, Pantaleo MA, Astolfi A, Dagrada GP, Negri T, Dei Tos AP, et al.",
        "journal": "Eur J Cancer",
        "year": 2014,
        "pmid": "24703573",
        "doi": "10.1016/j.ejca.2014.03.013",
        "url": "https://doi.org/10.1016/j.ejca.2014.03.013",
        "openAccess": False,
        "license": "publisher (abstract via Europe PMC)",
        "design": "retrospective named-use series",
        "n": 10,
        "population": "Progressive metastatic NR4A3-translocated EMC, Istituto Nazionale Tumori Milan, from July 2011",
        "accessed": "2026-08-07",
        "verified": True,
        "verification_note": (
            "Europe PMC core record read from the repository literature cache "
            "(literature-cache:literature/emc-clinical-sweep-c3-2026-08-07/ft_sunitinib2014_ejc.txt, "
            "HTTP 200). Abstract states 6 PR / 2 SD / 2 PD and 'all responsive cases turned out to "
            "express the typical EWSR1-NR4A3 fusion, while refractory cases carried the alternative "
            "TAF15-NR4A3 fusion'. Full text is paywalled; the per-arm DENOMINATORS come from the "
            "secondary sources below, which is why this cohort's strata carry provenance 'secondary'."
        ),
    },
    "stacchiotti2012": {
        "short": "Stacchiotti 2012 (two-case sunitinib report)",
        "type": "journal-article",
        "title": "Extraskeletal myxoid chondrosarcoma: tumor response to sunitinib.",
        "authors": "Stacchiotti S, Dagrada GP, Morosi C, Negri T, Romanini A, Pilotti S, Gronchi A, Casali PG.",
        "journal": "Clin Sarcoma Res",
        "year": 2012,
        "pmid": "23058004",
        "pmcid": "PMC3534218",
        "doi": "10.1186/2045-3329-2-22",
        "url": "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3534218/",
        "license": "BioMed Central open access",
        "openAccess": True,
        "design": "two-patient case report",
        "n": 2,
        "population": "Two consecutive pretreated progressive metastatic EMC, both EWSR1-CHN (EWSR1::NR4A3) positive, Istituto Nazionale Tumori Milan",
        "accessed": "2026-08-07",
        "verified": True,
        "verification_note": (
            "⭐ THIS, NOT THE 2014 SERIES, IS WHERE THE PRIMARY AUTHORS' HEDGE ACTUALLY APPEARS. Full "
            "text in the repository literature cache; the sentence 'Even in EMCS the fusion-protein "
            "is unlikely to be related to sunitinib sensitivity' is in its Discussion, following "
            "'As shown in ASPS, another STS bearing a translocation, the antitumor activity of "
            "sunitinib is unlikely to be directly linked to the fusion-protein.' The 2014 EJC "
            "abstract, which is the source usually cited for the hedge, does not contain it -- it "
            "says the opposite-facing 'Genotype/phenotype analyses support a correlation between "
            "response and EWSR1-NR4A3 fusion'."
        ),
    },
    "stacchiotti2019": {
        "short": "Stacchiotti 2019 (pazopanib phase 2)",
        "type": "journal-article",
        "title": "Pazopanib for treatment of advanced extraskeletal myxoid chondrosarcoma: a multicentre, single-arm, phase 2 trial",
        "authors": "Stacchiotti S, Ferrari S, Redondo A, Hindi N, Palmerini E, Vaz Salgado MA, et al.",
        "journal": "Lancet Oncol",
        "year": 2019,
        "pmid": "31331701",
        "doi": "10.1016/S1470-2045(19)30319-5",
        "url": "https://doi.org/10.1016/S1470-2045(19)30319-5",
        "nct": "NCT02066285",
        "openAccess": False,
        "license": "publisher (abstract via PubMed)",
        "design": "single-arm open-label phase 2 trial, 11 sites (Spanish/Italian/French sarcoma groups)",
        "n": 26,
        "population": "Adults, NR4A3-translocated metastatic or unresectable EMC with RECIST progression in the previous 6 months; enrolled 24 Jun 2014 - 17 Jan 2017",
        "erratum": "Lancet Oncol 2019;20(10):e559, PMID 31579002",
        "accessed": "2026-08-07",
        "verified": True,
        "verification_note": (
            "Abstract read from the repository literature cache "
            "(literature-cache:literature/emc-post-degrader-options/emc_pazopanib_pubmed.txt, HTTP 200): "
            "26 entered, 23 met modified-ITT eligibility, 22 evaluable for the primary endpoint "
            "(one patient died before the primary analysis), four (18% [95% CI 1-36]) with a RECIST "
            "objective response. THE ABSTRACT CARRIES NO FUSION-PARTNER BREAKDOWN and the full text is "
            "paywalled (Elsevier; isOpenAccess N, inEPMC N in the Europe PMC core record), so the "
            "partner strata are taken from the secondary sources below."
        ),
    },
    "stacchiotti2020review": {
        "short": "Stacchiotti 2020 (EMC state of the art)",
        "type": "review",
        "title": "Extraskeletal Myxoid Chondrosarcoma: State of the Art and Current Research on Biology and Clinical Management.",
        "authors": "Stacchiotti S, Baldi GG, Morosi C, Gronchi A, Maestro R.",
        "journal": "Cancers (Basel)",
        "year": 2020,
        "pmid": "32967265",
        "pmcid": "PMC7563993",
        "doi": "10.3390/cancers12092703",
        "url": "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7563993/",
        "license": "CC-BY-4.0",
        "openAccess": True,
        "design": "narrative review",
        "accessed": "2026-08-07",
        "verified": True,
        "verification_note": (
            "Full text in the repository literature cache. Written by the senior authors of BOTH "
            "primary reports, which is why it can state the per-arm denominators the primary "
            "abstracts omit -- and equally why it is not an independent reading of them. Verbatim: "
            "'no activity was observed in the two TAF15-NR4A3-positive patients included in the "
            "series' (sunitinib) and 'all three TAF15-NR4A3-positive tumors included in this "
            "pazopanib trial failed to respond to pazopanib'."
        ),
    },
    "jacobs2021": {
        "short": "Jacobs & Lapeire 2021 (review)",
        "type": "review",
        "title": "Translating Molecular Profiling of Soft Tissue Sarcomas into Daily Clinical Practice.",
        "authors": "Jacobs C, Lapeire L.",
        "journal": "Diagnostics (Basel)",
        "year": 2021,
        "pmid": "33799327",
        "pmcid": "PMC7999686",
        "doi": "10.3390/diagnostics11030512",
        "url": "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7999686/",
        "license": "CC-BY-4.0",
        "openAccess": True,
        "design": "narrative review",
        "accessed": "2026-08-07",
        "verified": True,
        "verification_note": (
            "Independent group (Ghent), so this is the corroborating secondary read. Verbatim: "
            "'Four out of 22 evaluable patients achieved a RECIST partial response, and all four "
            "were positive for the typical EWSR1-NR4A3 translocation. Of the three patients with "
            "TAF15 as translocation partner, none showed a response.'"
        ),
    },
    "davis2017": {
        "short": "Davis 2017 (EMC next-generation sequencing)",
        "type": "journal-article",
        "title": "Next generation sequencing of extraskeletal myxoid chondrosarcoma.",
        "authors": "Davis EJ, Wu YM, Robinson D, Schuetze SM, Baker LH, Athanikar J, Cao X, Kunju LP, Chinnaiyan AM, Chugh R.",
        "journal": "Oncotarget",
        "year": 2017,
        "pmid": "28423517",
        "pmcid": "PMC5400622",
        "doi": "10.18632/oncotarget.15568",
        "url": "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5400622/",
        "license": "CC-BY-4.0",
        "openAccess": True,
        "design": "molecular profiling series (6 EMC); cited here only for its reading of the sunitinib series",
        "accessed": "2026-08-07",
        "verified": True,
        "verification_note": (
            "Independent group (University of Michigan). Verbatim: 'The two patients with the "
            "variant fusion, TAF15-NR4A3, had progressive disease on sunitinib, while all patients "
            "with the classical translocation had stable or responsive disease.' This is the "
            "sentence that fixes the sunitinib denominators at 8 EWSR1 / 2 TAF15."
        ),
    },
    "agaram2014": {
        "short": "Agaram 2014",
        "type": "journal-article",
        "title": "Extraskeletal myxoid chondrosarcoma with non-EWSR1-NR4A3 variant fusions correlate with rhabdoid phenotype and high-grade morphology.",
        "authors": "Agaram NP, Zhang L, Sung YS, Singer S, Antonescu CR.",
        "journal": "Hum Pathol",
        "year": 2014,
        "pmid": "24746215",
        "pmcid": "PMC4015728",
        "doi": "10.1016/j.humpath.2014.01.007",
        "url": "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4015728/",
        "license": "NIH author manuscript (PMC)",
        "openAccess": True,
        "design": "consecutive single-institution molecular/pathology series with follow-up",
        "n": 26,
        "population": "26 consecutive EMC, Memorial Sloan-Kettering Cancer Center; follow-up available in all 26 (2-99 months)",
        "accessed": "2026-08-07",
        "verified": True,
        "verification_note": (
            "Author-manuscript full text in the repository literature cache. Per-partner outcome "
            "counts read from the Clinical Follow-up section verbatim and cross-checked case by "
            "case against Table 1."
        ),
    },
    "huang2023": {
        "short": "Huang 2023",
        "type": "journal-article",
        "title": "Extraskeletal Myxoid Chondrosarcomas: The Uncommon Clinicopathologic Manifestations and Significance of TAF15::NR4A3 Fusion.",
        "authors": "Huang SC, Lee JC, Hsu YC, Tsai JW, Kao YC, Hsieh TH, Chang YM, Chang KC, Wu PS, Chen PC, Chen CH, Chang CD, Lee PH, Tai HC, Liu TT, Wen MC, Li WS, Yu SC, Wang JC, Huang HY.",  # complete list, authorString of literature-cache:literature/emc-partner-events/huang2023_epmc_core.txt
        "journal": "Mod Pathol",
        "year": 2023,
        "pmid": "36948401",
        "doi": "10.1016/j.modpat.2023.100161",
        "pii": "S0893-3952(23)00066-2",
        "url": "https://doi.org/10.1016/j.modpat.2023.100161",
        "license": "publisher (bronze open access; published-version PDF designated free by the publisher, not carrying a reusable licence)",
        "openAccess": True,
        "open_access_status": "bronze",
        "design": "multi-institution molecular case series with survival analysis (Taiwan)",
        "n": 58,
        "population": (
            "58 FISH-confirmed EMC accrued across 15 Taiwanese institutions, led from Linkou and "
            "Kaohsiung Chang Gung Memorial Hospital; follow-up available in 53"
        ),
        "accessed": "2026-08-08",
        "verified": True,
        "registry_id": "huang2023",
        "registry_note": (
            "⚠ *Superseded, retained: 'research/data/emc-clinical-registry.json carries this same "
            "paper under the citation id `warmke2023` with short label \"Warmke 2023\", which does "
            "not match its author list; the identifier, title, DOI and PMID in that entry are "
            "correct.'* That defect was real and is FIXED as of 2026-08-08 -- the registry entry "
            "is now keyed `huang2023` with short label 'Huang 2023' (edit F3 of "
            "emc-fusion-partner-map-edits.json, applied). ⛔ DO NOT 'CORRECT' EVERY Warmke MENTION "
            "IN THIS REPOSITORY BY PATTERN: Warmke LM is a real author with a real and DIFFERENT "
            "TAF15::NR4A3 paper (PMID 37057757, Genes Chromosomes Cancer 2023, "
            "doi 10.1002/gcc.23144), cited correctly as reference 20 of "
            "research/manuscripts/degrader/nr4a3-degrader-paper.md. Check each hit against its identifier."
        ),
        "identity_confirmed": (
            "PMID 36948401 WAS CHECKED AGAINST THE PAPER RATHER THAN ASSUMED, because three "
            "citations in this repository have been found resolving cleanly to the wrong paper. "
            "The Europe PMC core record for EXT_ID:36948401 (HTTP 200, committed at "
            "literature-cache:literature/emc-partner-events/huang2023_epmc_core.txt) returns "
            "doi 10.1016/j.modpat.2023.100161, title 'Extraskeletal Myxoid Chondrosarcomas: The "
            "Uncommon Clinicopathologic Manifestations and Significance of TAF15::NR4A3 Fusion.', "
            "Mod Pathol 36(7):100161, and authorString 'Huang SC, Lee JC, Hsu YC, ... Huang HY.' "
            "with first author Shih-Chiang Huang, Department of Anatomic Pathology, Linkou Chang "
            "Gung Memorial Hospital, Taoyuan, Taiwan. DOI, PII (S0893-3952(23)00066-2 = "
            "S0893395223000662), journal, volume and first author all match the read PDF. It is a "
            "TAIWANESE multi-institutional cohort and is NOT an MSKCC series."
        ),
        "verification_note": (
            "⭐ THE PUBLISHED FULL TEXT WAS READ BY A HUMAN ON 2026-08-08 AND ITS TABLE 1 "
            "PER-PARTNER EVENT COUNTS ARE NOW IN THIS FILE. This cohort therefore contributes to "
            "the OUTCOME pool as well as the prevalence pool, and it is the second cohort ever to "
            "publish EMC outcome event counts stratified by NR4A3 partner. ⚠ *Superseded, "
            "retained: 'NO EVENT COUNTS by partner are in the abstract and the full text is "
            "paywalled, so this cohort contributes to the PREVALENCE pool and to nothing else.' "
            "The counts sentence was true of the ABSTRACT and remains so; the paywall clause was "
            "wrong on the mechanism.* MEASURED 2026-08-08: Unpaywall and OpenAlex independently "
            "report `is_oa: true`, `oa_status: bronze`, `journal_is_oa: false`, with a single "
            "publisher-hosted `publishedVersion` PDF at "
            "http://www.modernpathology.org/article/S0893395223000662/pdf and `oa_date` "
            "2023-03-21 -- i.e. a FREE published-version PDF is designated to exist. Every "
            "automated fetch of it returned HTTP 403 behind an anti-bot challenge "
            "(literature-cache:literature/emc-partner-events-r2/_manifest.json: "
            "huang2023_modpath_pdf 403, huang2023_modpath_fulltext 403, "
            "huang2023_sciencedirect_pii 403). A BOT BLOCK AND A PAYWALL HAVE DIFFERENT "
            "REMEDIES: a paywall needs a subscription or an author, a bot block needs a person "
            "with a browser -- which is exactly how these counts were obtained. Europe PMC's own "
            "flags (isOpenAccess N, inEPMC N, hasPDF N) describe Europe PMC's holdings, not the "
            "publisher's, and reading them as 'paywalled' is what produced the superseded "
            "sentence."
        ),
    },
    "lenz2023": {
        "short": "Lenz 2023",
        "type": "journal-article",
        "title": "Extraskeletal myxoid chondrosarcoma: A study of 17 cases focusing on the diagnostic utility of INSM1 expression and presenting rare morphological variants associated with non-EWSR1::NR4A3 fusions.",
        "authors": "Lenz J, Klubickova N, Ptakova N, Hajkova V, Grossmann P, Steiner P, Kinkor Z, Svajdler M, Michal M, Konecna P, Machacova D, Hurnik P, Tichy M, Tichy F, Kyllar M, Fiala L, Kavka M, Michal M.",  # complete list, research/literature/submission-reference-metadata-2026-08-09.json (diacritics folded)
        "journal": "Hum Pathol",
        "year": 2023,
        "pmid": "36563884",
        "doi": "10.1016/j.humpath.2022.12.005",
        "url": "https://doi.org/10.1016/j.humpath.2022.12.005",
        "license": "publisher (abstract via Europe PMC)",
        "openAccess": False,
        "design": "single-institution molecular/immunohistochemical series (Czech Republic)",
        "n": 17,
        "population": "17 EMC; molecular typing successful in 12",
        "accessed": "2026-08-07",
        "verified": True,
        "verification_note": (
            "Abstract states the fusion distribution as explicit integers over the 12 successfully "
            "typed cases: 8 EWSR1::NR4A3, 2 TAF15::NR4A3, 1 TCF12::NR4A3, 1 NR4A3-rearranged with "
            "no partner identified."
        ),
    },
    "paioli2021": {
        "short": "Paioli 2021 (Italian Sarcoma Group)",
        "type": "journal-article",
        "title": "Extraskeletal Myxoid Chondrosarcoma with Molecularly Confirmed Diagnosis: A Multicenter Retrospective Study Within the Italian Sarcoma Group.",
        "authors": "Paioli A, Stacchiotti S, Campanacci D, Palmerini E, Frezza AM, Longhi A, Radaelli S, Donati DM, Beltrami G, Bianchi G, Barisella M, Righi A, Benini S, Fiore M, Picci P, Gronchi A.",  # complete list, research/manuscripts/aso/lit-targets-aso-bibliography-completion.json
        "journal": "Ann Surg Oncol",
        "year": 2021,
        "pmid": "32572850",
        "doi": "10.1245/s10434-020-08737-7",
        "url": "https://doi.org/10.1245/s10434-020-08737-7",
        "license": "publisher (abstract via Europe PMC)",
        "openAccess": False,
        "design": "three-centre retrospective cohort, molecularly confirmed, localised disease",
        "n": 67,
        "population": "Localised NR4A3-rearranged EMC surgically treated 1989-2016 at three Italian Sarcoma Group referral centres; median follow-up 55 months",
        "accessed": "2026-08-07",
        "verified": True,
        "verification_note": (
            "Europe PMC core record in the repository literature cache (isOpenAccess N / inEPMC N; "
            "abstract only). Fusion distribution given as explicit integers -- 50 (80%) NR4A3-EWS, "
            "10 (16%) NR4A3-TAF15, 1 (2%) NR4A3-TCF12, 1 (2%) NR4A3-TFG -- which sum to 62, so the "
            "partner-assigned denominator is 62 of the 67 identified patients and the published "
            "percentages confirm it. Outcome by partner is reported ONLY as a trend with p-values "
            "and no event counts: 'Patients carrying the NR4A3-EWS translocation had a trend in "
            "favor of better DFS (p = 0.08) and DMFS (p = 0.09) compared with the patients with "
            "NR4A3-TAF15.'"
        ),
    },
    "sjogren2003": {
        "short": "Sjogren 2003 (Goteborg EMC series)",
        "type": "journal-article",
        "title": (
            "Studies on the molecular pathogenesis of extraskeletal myxoid "
            "chondrosarcoma-cytogenetic, molecular genetic, and cDNA microarray analyses."
        ),
        "authors": "Sjogren H, Meis-Kindblom JM, Orndal C, Bergh P, Ptaszynski K, Aman P, Kindblom LG, Stenman G.",
        "journal": "Am J Pathol",
        "year": 2003,
        "volume": "162",
        "issue": "3",
        "pages": "781-792",
        "pmid": "12598313",
        "pmcid": "PMC1868116",
        "doi": "10.1016/S0002-9440(10)63875-8",
        "url": "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC1868116/",
        "license": "Copyright (c) 2003, American Society for Investigative Pathology; free in PMC, no reusable licence stated",
        "openAccess": True,
        "design": "single-institution cytogenetic / SKY / FISH / RT-PCR and cDNA microarray series",
        "n": 9,
        "population": (
            "Ten EMCs from nine patients, Sahlgrenska University Hospital, Goteborg University, "
            "Sweden. Five patients new to this report; four previously reported by the same group "
            "for their fusion transcripts."
        ),
        "accessed": "2026-08-15",
        "verified": True,
        "verification_note": (
            "⭐ FULL TEXT READ, NOT THE ABSTRACT, AND THE DIFFERENCE DECIDES THE POOLING. Fetched "
            "as PMC HTML from https://pmc.ncbi.nlm.nih.gov/articles/PMC1868116/ at HTTP 200 "
            "(literature-cache:literature/ews-type-nom-fulltext/pmc_html_PMC1868116.txt, whose "
            "fetch header preserves the status). Europe PMC's fullTextXML endpoint 404s for this "
            "PMCID and an earlier pass read that 404 as 'the abstract is the record' -- the defect "
            "CLAUDE.md s4 names. The abstract's partner integers are TUMOUR-level; only the "
            "Discussion and Table 3 give patient-level ones. This citation is attached to a "
            "`pool: False` cohort and to nothing else."
        ),
    },
    "llombartBosch2022": {
        "short": "Llombart-Bosch 2022 (congress abstract)",
        "type": "conference-abstract",
        "title": "Extraskeletal myxoid chondrosarcoma: a morphological, immunohistochemical and molecular analysis of 31 cases (ECP 2022, OFP-04-002).",
        "authors": "Llombart-Bosch A, Giner F, Machado I, Navarro S, Ferrandez Izquierdo A.",
        "journal": "Virchows Arch (34th European Congress of Pathology abstracts)",
        "year": 2022,
        "pmcid": "PMC9379246",
        "doi": "10.1007/s00428-022-03379-4",
        "url": "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9379246/",
        "license": "PMC Open Access Subset",
        "openAccess": True,
        "design": "two-institution retrospective series, meeting abstract",
        "n": 31,
        "accessed": "2026-08-07",
        "verified": True,
    },
    "klubickova2022": {
        "short": "Klubickova 2022 (congress abstract)",
        "type": "conference-abstract",
        "title": "A single-institution experience with 11 cases of extraskeletal myxoid chondrosarcoma: rare fusions, unusual morphology and the utility of INSM1 immunohistochemistry (ECP 2022, OFP-04-003).",
        "authors": "Klubickova N, Lenz J, Michal M, Michal M.",
        "journal": "Virchows Arch (34th European Congress of Pathology abstracts)",
        "year": 2022,
        "pmcid": "PMC9379246",
        "doi": "10.1007/s00428-022-03379-4",
        "url": "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9379246/",
        "license": "PMC Open Access Subset",
        "openAccess": True,
        "design": "single-institution series, meeting abstract",
        "n": 11,
        "accessed": "2026-08-07",
        "verified": True,
    },
    "brenca2019": {
        "short": "Brenca 2019",
        "type": "journal-article",
        "title": "NR4A3 fusion proteins trigger an axon guidance switch that marks the difference between EWSR1 and TAF15 translocated extraskeletal myxoid chondrosarcomas.",
        "authors": "Brenca M, Stacchiotti S, Fassetta K, Sbaraglia M, Janjusevic M, Racanelli D, et al.",
        "journal": "J Pathol",
        "year": 2019,
        "pmid": "31020999",
        "pmcid": "PMC6766969",
        "doi": "10.1002/path.5284",
        "url": "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6766969/",
        "license": "CC-BY (Wiley open access)",
        "openAccess": True,
        "design": "transcriptional profiling of 7 EWSR1-NR4A3 and 5 TAF15-NR4A3 EMC, with engineered-cell recapitulation",
        "accessed": "2026-08-07",
        "verified": True,
    },
    "bangerter2022": {
        "short": "Bangerter 2022 (USZ ex vivo models)",
        "type": "journal-article",
        "title": "Establishment, characterization and functional testing of two novel ex vivo extraskeletal myxoid chondrosarcoma (EMC) cell models.",
        "authors": "Bangerter JL, Harnisch KJ, Chen Y, Hagedorn C, Planas-Paz L, Pauli C.",
        "journal": "Hum Cell",
        "year": 2022,
        "pmid": "36316541",
        "pmcid": "PMC9813045",
        "doi": "10.1007/s13577-022-00818-x",
        "url": "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9813045/",
        "license": "CC-BY-4.0",
        "openAccess": True,
        "design": "patient-derived ex vivo sarco-sphere models, n = 1 per fusion partner",
        "accessed": "2026-08-07",
        "verified": True,
    },
    "remiszewski2025": {
        "short": "Remiszewski 2025 (review)",
        "type": "review",
        "title": "From pathogenesis to the patient's bedside: a comprehensive review of extraskeletal myxoid chondrosarcoma",
        "authors": "Remiszewski P, Falkowski S, Szumera-Cieckiewicz A, et al.",
        "journal": "J Cancer Res Clin Oncol",
        "year": 2025,
        "pmcid": "PMC12504171",
        "doi": "10.1007/s00432-025-06316-5",
        "url": "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12504171/",
        "license": "CC-BY-NC-ND-4.0",
        "openAccess": True,
        "design": "narrative review",
        "accessed": "2026-08-07",
        "verified": True,
        "registry_id": "remiszewski2025",
        "verification_note": (
            "Already curated in research/data/emc-clinical-registry.json under the same id. Its EMC "
            "treatment section states the pazopanib partner split ONLY qualitatively ('better "
            "outcomes in patients with the EWSR1::NR4A3 fusion, while TAF15-NR4A3 cases showed a "
            "poor response'), which is why it is not the source of any count here."
        ),
    },
    "suemitsu2025": {
        "short": "Suemitsu 2025 (MSK)",
        "type": "journal-article",
        "title": "Secondary Genetic Alterations in Extraskeletal Myxoid Chondrosarcoma.",
        "authors": ("Suemitsu Y, Chang HY, Saoud C, Dermawan JK, Hameed M, Singer S, Tap WD, "
                    "Antonescu CR."),
        "journal": "Genes Chromosomes Cancer",
        "year": 2025,
        "pmid": "40828003",
        "doi": "10.1002/gcc.70076",
        "url": "https://doi.org/10.1002/gcc.70076",
        "openAccess": False,
        "design": "retrospective molecular series, MSK-IMPACT",
        "n": 18,
        "population": "18 EMC patients profiled by MSK-IMPACT",
        "accessed": "2026-08-08",
        "verified": True,
        "verification_note": (
            "Europe PMC abstract, HTTP 200, recorded verbatim in this paper's companion "
            "research/manuscripts/fusion-partner/partner-event-counts-2026-08-08.md s4 and targeted "
            "by lit-targets-partner-events.json. Two sentences bear on this synthesis: 'the most "
            "common NR4A3 fusion subtype involved EWSR1 (14/18, 78%), while two cases involved "
            "TAF15 gene partner, and one each TCF12 and FUS genes, respectively', and 'no "
            "statistically significant correlation was detected between OS and fusion subtypes'. "
            "\u26d4 IT WAS IN THE REPOSITORY AND IN NO VERSION OF THIS PAPER UNTIL 2026-08-26, when "
            "a blind adversarial seat found it missing from a table the manuscript calls 'the full "
            "inclusion table'. The companion had even logged the action item to bring it in."
        ),
    },
}


# ---------------------------------------------------------------------------
# cohorts (POLICY-evidence.md s2.1 / s2.3)
# ---------------------------------------------------------------------------
COHORTS = [
    # ---- endpoint: objective response to an antiangiogenic TKI -------------
    {
        "id": "sunitinib-2014",
        "endpoint": "objective_response_antiangiogenic_tki",
        "label": "Sunitinib 37.5 mg/day, named-use, progressive metastatic EMC",
        "n_treated": 10,
        "n_assessable": 10,
        "sourceId": "stacchiotti2020review",
        "provenance": "secondary",
        "primaryRef": "Stacchiotti S et al., Eur J Cancer 2014;50:1657-64 (PMID 24703573), n = 10; 6 PR, 2 SD, 2 PD",
        "corroboratingSourceIds": ["davis2017", "jacobs2021"],
        "populationKey": "int-milan-advanced-emc",
        "strata": {
            "EWSR1::NR4A3": {"events": 6, "denom": 8},
            "TAF15::NR4A3": {"events": 0, "denom": 2},
        },
        "stratum_definition": (
            "Objective response = RECIST partial response. The two TAF15 patients are the two "
            "progressors; the remaining eight are described as carrying 'the classical "
            "translocation', i.e. EWSR1::NR4A3, and comprise the 6 PR and the 2 SD."
        ),
        "pool": False,
        "contextReason": "population-overlap",
        "overlap_note": (
            "CANNOT BE SHOWN NON-OVERLAPPING WITH THE PAZOPANIB TRIAL, so POLICY-evidence.md s2.3 "
            "puts the smaller cohort out of the headline. Three facts make the risk material rather "
            "than theoretical: (1) Istituto Nazionale Tumori Milan ran this series and was a site of "
            "the trial, with the same senior investigator; (2) the trial's entry criterion -- "
            "NR4A3-translocated advanced EMC with RECIST progression in the previous 6 months -- is "
            "satisfied by definition by this series' two progressors, who are exactly its two TAF15 "
            "patients; (3) neither report states whether prior antiangiogenic therapy was permitted "
            "or whether any patient appears in both, and the trial's full text is paywalled. Worst "
            "case both TAF15 patients here are among the trial's three."
        ),
    },
    {
        "id": "pazopanib-NCT02066285",
        "endpoint": "objective_response_antiangiogenic_tki",
        "label": "Pazopanib 800 mg/day, phase 2 NCT02066285, advanced EMC",
        "n_enrolled": 26,
        "n_modified_itt": 23,
        "n_assessable": 22,
        "sourceId": "jacobs2021",
        "provenance": "secondary",
        "primaryRef": "Stacchiotti S et al., Lancet Oncol 2019;20:1252-62 (PMID 31331701), NCT02066285; 4/22 evaluable with a RECIST objective response",
        "corroboratingSourceIds": ["stacchiotti2020review"],
        "populationKey": "eu-sarcoma-groups-pazopanib-trial",
        "strata": {
            "TAF15::NR4A3": {"events": 0, "denom": 3},
            "non-TAF15": {"events": 4, "denom": 19},
        },
        "stratum_definition": (
            "Objective response = RECIST 1.1 response in the primary-endpoint population "
            "(22 evaluable). The comparator arm is labelled **non-TAF15, not EWSR1**: all four "
            "responders are reported as EWSR1::NR4A3, but no accessible source gives the trial's "
            "full partner distribution, so the 19 non-TAF15 patients may include FUS, TCF12 or "
            "untyped NR4A3-rearranged cases."
        ),
        "derivation": "19 = 22 evaluable - 3 TAF15. Both inputs are published integers; the strata are mutually exclusive (POLICY-evidence.md s2.3).",
        "assumptions": [
            "All three TAF15 patients are inside the 22-patient evaluable set. If the one patient "
            "who died before the primary analysis was a TAF15 case, the strata become 0/2 and "
            "4/20; that moves the TAF15 arm's Wilson upper bound UP, so it cannot rescue any claim "
            "made here. Computed in analyses.A_tki_objective_response.sensitivity_analyses.",
            "No accessible source reports whether any of the 19 non-TAF15 patients carried a "
            "partner other than EWSR1.",
        ],
        "pool": True,
    },
    {
        "id": "sunitinib-2012-two-cases",
        "endpoint": "objective_response_antiangiogenic_tki",
        "label": "Sunitinib, two consecutive EWSR1::NR4A3 patients (index report)",
        "n_assessable": 2,
        "sourceId": "stacchiotti2012",
        "provenance": "primary",
        "populationKey": "int-milan-advanced-emc",
        "pool": False,
        "contextReason": "population-overlap",
        "overlap_note": (
            "CONTAINED IN THE 2014 SERIES, not merely at risk of overlapping with it: the 2014 "
            "paper's own abstract says it reports 10 patients treated from July 2011 'strengthening "
            "what initially observed in two cases', these are those two cases, same institution and "
            "same investigator. Pooling it would count two responders twice. Both patients carried "
            "EWSR1-CHN (EWSR1::NR4A3), which is also the check on the 2014 series' 8-EWSR1 / 2-TAF15 "
            "split."
        ),
    },
    # ---- endpoint: disease-specific death by partner -----------------------
    {
        "id": "agaram-2014-outcome",
        "endpoint": "outcome_by_partner",
        "label": "Consecutive surgical EMC series with follow-up (MSKCC)",
        "n_assessable": 26,
        "sourceId": "agaram2014",
        "provenance": "primary",
        "populationKey": "mskcc-emc-consecutive",
        "strata": {
            "EWSR1::NR4A3": {
                "disease_specific_death": {"events": 1, "denom": 16},
                "local_recurrence": {"events": 1, "denom": 16},
                "distant_recurrence": {"events": 6, "denom": 16},
                "moderate_to_high_cellularity": {"events": 4, "denom": 16},
                "mean_followup_months": 43.3,
            },
            "TAF15::NR4A3": {
                "disease_specific_death": {"events": 3, "denom": 7},
                "local_recurrence": {"events": 2, "denom": 7},
                "distant_recurrence": {"events": 2, "denom": 7},
                "mean_followup_months": 21.7,
            },
            "variant non-EWSR1 (TAF15 + TCF12 + partner-unassigned)": {
                "moderate_to_high_cellularity_with_moderate_to_severe_atypia": {"events": 8, "denom": 10},
                "note": (
                    "The paper's own '80% high grade' figure is over this 10-case VARIANT group "
                    "(7 TAF15 + 1 TCF12 + 2 NR4A3-rearranged with no partner identified), not over "
                    "the 7 TAF15 cases. Quoting it as a TAF15 figure overstates a real signal."
                ),
            },
        },
        "pool": True,
        "pool_note": (
            "Pooled with huang-2023-outcome (POLICY-evidence.md s2.2). ⚠ *Superseded, retained: "
            "'The only published EMC cohort that reports outcome EVENT COUNTS by NR4A3 partner. "
            "Pooling it is therefore a single-cohort Wilson interval, stated as such rather than "
            "dressed as a meta-analysis.'* That was true until 2026-08-08, when Huang 2023's "
            "Table 1 was read from the published PDF and supplied a second, larger and "
            "geographically independent set of per-partner event counts. This cohort is now the "
            "SMALLER of two."
        ),
        "follow_up_warning": (
            "The two arms have very different mean follow-up (43.3 vs 21.7 months) and these are "
            "crude during-follow-up proportions with no censoring (POLICY-evidence.md s2.4). "
            "⛔ THE DIRECTION OF THAT BIAS IS NOT ESTABLISHED, AND THIS FIELD ASSERTED THAT IT WAS. "
            "The superseded reading -- 'the bias runs AGAINST the TAF15 arm accruing events, so "
            "the death excess is observed DESPITE shorter observation' -- is CIRCULAR in an "
            "uncensored during-follow-up analysis, because follow-up ENDS AT DEATH. The TAF15 "
            "arm's shorter mean follow-up (21.7 months against 43.3) is therefore partly PRODUCED "
            "BY its own 3/7 deaths rather than being an independent handicap it overcame; the "
            "same 3 deaths appear on both sides of that sentence, once as the effect and once as "
            "the reason the effect is impressive. What can honestly be said is narrower: the two "
            "arms' observation windows differ, the difference is not independent of the endpoint "
            "being compared, and no censored analysis exists in either source that would separate "
            "them. ⛔ THE RECURRENCE AND METASTASIS ROWS ARE CONFOUNDED TOO, BUT NOT BY THIS "
            "MECHANISM, AND THIS FIELD SAID THEY WERE. ⚠ *Superseded, retained: 'The recurrence "
            "comparison is confounded the same way, in a direction this record cannot sign.'* There "
            "the competing risk is death ITSELF -- a patient who has died is no longer at risk of a "
            "recorded recurrence or metastasis -- so informative censoring by the competing event "
            "biases the arm with more deaths and shorter observation DOWNWARD on those two rows if "
            "anything. THE SIGN MATTERS FOR HOW THE NULL ON THOSE ROWS IS READ: an understated "
            "TAF15 recurrence and metastasis rate means the two-cohort null is not evidence that "
            "those endpoints do NOT differ by partner, only that this record cannot establish that "
            "they do. ⛔ Nor is it a licence to read the rows as unbiased: the magnitude of the "
            "bias is unmeasured, and no censored analysis exists in either source. "
            "⚠ *Superseded, retained: 'the reversal reported below'* -- the "
            "reversal is this cohort's alone and the second cohort does not reproduce it; see "
            "analyses.B_outcome_by_partner.metastasis_reading."
        ),
    },
    {
        "id": "huang-2023-outcome",
        "endpoint": "outcome_by_partner",
        "label": "58 FISH-confirmed EMC, Taiwan (Table 1 outcome counts; follow-up available in 53)",
        "n_assessable": 58,
        "n_with_followup": 53,
        "sourceId": "huang2023",
        "provenance": "primary",
        "populationKey": "taiwan-emc-series",
        "counts_read_from": (
            "Table 1 of the published PDF, read by a human on 2026-08-08 after every automated "
            "fetch of the publisher's designated-free PDF returned HTTP 403 "
            "(citations.huang2023.verification_note). The outcome denominators are the "
            "partner-assigned cases WITH FOLLOW-UP: 42 EWSR1::NR4A3 and 8 TAF15::NR4A3 (50 of the "
            "53 with follow-up; the remaining 3 are the miscellaneous group -- 2 TCF12, 1 partner "
            "unidentified -- which the paper does not carry as an outcome arm and which is "
            "therefore in neither numerator nor denominator here)."
        ),
        "strata": {
            "EWSR1::NR4A3": {
                "disease_specific_death": {"events": 5, "denom": 42},
                "alive_with_disease": {"events": 12, "denom": 42},
                "no_evidence_of_disease": {"events": 25, "denom": 42},
                "local_recurrence": {"events": 12, "denom": 42},
                "distant_metastasis_any": {"events": 16, "denom": 42},
                "distant_metastasis_at_presentation": {"events": 8, "denom": 42},
                "distant_metastasis_after_presentation": {"events": 8, "denom": 42},
            },
            "TAF15::NR4A3": {
                "disease_specific_death": {"events": 4, "denom": 8},
                "alive_with_disease": {"events": 0, "denom": 8},
                "no_evidence_of_disease": {"events": 4, "denom": 8},
                "local_recurrence": {"events": 2, "denom": 8},
                "distant_metastasis_any": {"events": 4, "denom": 8},
                "distant_metastasis_at_presentation": {"events": 1, "denom": 8},
                "distant_metastasis_after_presentation": {"events": 3, "denom": 8},
            },
        },
        "stratum_definition": (
            "Final status is a three-way partition of each arm (NED / AWD / DOD) and the "
            "disease-specific-death row is its DOD cell. Distant metastasis is a three-way "
            "partition (present at presentation / developed subsequently / never) and the two "
            "metastasis rows above are derived from it by ADDITION of published integers, never "
            "from a percentage: `distant_metastasis_any` = at presentation + after presentation. "
            "Local recurrence is a two-way partition (positive / negative). Every cell is an "
            "explicit integer in Table 1, so POLICY-evidence.md s2.1(2) is satisfied."
        ),
        "size_covariate": {
            "EWSR1::NR4A3": {"mean_cm": 7.3, "sd_cm": 4.7, "over_10cm": {"events": 12, "denom": 46}},
            "TAF15::NR4A3": {"mean_cm": 13.7, "sd_cm": 6.2, "over_10cm": {"events": 7, "denom": 9}},
            "published_p_size_mean": 0.024,
            "published_p_size_over_10cm": 0.025,
            "why_the_denominator_differs": (
                "The size rows are over the WHOLE partner-assigned cohort (46 and 9), not over the "
                "subset with follow-up (42 and 8), because size is a presenting feature and needs "
                "no follow-up to be known. This is a covariate, not an outcome, and it is pooled "
                "into nothing."
            ),
            "internal_inconsistency_recorded_not_resolved": (
                "⚠ The paper prints the EWSR1 arm's >10 cm row as '12/46 (28%)' and 12/46 is "
                "26.1%, not 28%. One of those three printed numbers is wrong and NOTHING HERE "
                "GUESSES WHICH: a denominator of 43 would give 27.9% and a numerator of 13 would "
                "give 28.3%, and POLICY-evidence.md s2.1(2) forbids back-deriving a count from a "
                "percentage to close the gap. The integers as printed are recorded above and the "
                "discrepancy is recorded here. The TAF15 side has no such problem -- 7/9 = 77.8% "
                "and the paper prints 78%, which the independently-retrieved Europe PMC abstract "
                "corroborates verbatim ('TAF15::NR4A3 was significantly associated with size "
                ">10 cm (78%, P = .025)'). No figure in this file depends on the EWSR1 size cell."
            ),
        },
        "published_p_values": {
            "final_status_three_way": 0.047,
            "distant_metastasis_three_way": 0.728,
            "local_recurrence": 1.000,
            "note": (
                "The authors' own tests on their own tables, quoted as published. They are NOT "
                "the post-hoc Fisher values this file computes on the two-arm contrasts, and the "
                "two must not be conflated: the authors' status and metastasis p-values test "
                "THREE-way tables, this file's test two-way ones."
            ),
        },
        "multivariable_result": {
            "endpoint": "disease-specific survival",
            "independent_predictors": {
                "size >10 cm": 0.004,
                "metastasis at presentation": 0.032,
            },
            "hazard_ratios": {"size >10 cm": 30.60, "metastasis at presentation": 8.14},
            "taf15_status": "LOSES SIGNIFICANCE UNDER ADJUSTMENT",
            "authors_own_words": (
                "TAF15-positive EMCs had significantly shorter disease-free, metastasis-free and "
                "disease-specific survival, which 'might be partly attributable to the "
                "predominance of large tumors > 10 cm in TAF15-rearranged EMCs'."
            ),
            "why_this_travels_with_every_number_above": (
                "⛔ THE DEFEATER IS NOT A FOOTNOTE. Every pooled prognostic figure this file "
                "computes is a CRUDE, UNADJUSTED proportion, and this is the analysis that says "
                "the crude quantity is confounded -- by a covariate the same table shows is "
                "strongly partner-associated (78% of TAF15 tumours >10 cm against 26-28% of "
                "EWSR1 ones, P = .025). A pooled magnitude quoted without it is a number the "
                "source itself refuses."
            ),
        },
        "pool": True,
        "pool_note": (
            "Pooled with agaram-2014-outcome under POLICY-evidence.md s2.2. The two populations "
            "are distinct on every available axis -- MSKCC (New York) versus 15 Taiwanese "
            "institutions led from Chang Gung Memorial Hospital, no shared authors, no shared "
            "referral network -- which is the same non-overlap argument the prevalence pool "
            "already makes for these two series."
        ),
        "estimand_warning": (
            "⚠ THE METASTASIS ENDPOINTS OF THE TWO POOLED COHORTS ARE MATCHED ON THEIR LABELS, "
            "NOT ON A PUBLISHED DEFINITION. Agaram 2014 reports 'distant recurrence'; Huang 2023 "
            "partitions distant metastasis into present-at-presentation and developed-later. This "
            "file pools Agaram's distant recurrence with Huang's AFTER-PRESENTATION cell because "
            "that is the closer reading of 'recurrence', and reports Huang's ANY-metastasis figure "
            "separately and within-cohort only. Neither report states whether patients metastatic "
            "at presentation were in its recurrence denominator, so the match is an assumption and "
            "is labelled as one; both readings are printed so the conclusion can be checked at "
            "either. Death and local recurrence carry no such ambiguity."
        ),
        "follow_up_warning": (
            "Crude during-follow-up proportions with no censoring (POLICY-evidence.md s2.4). This "
            "cohort reports outcome only for the 53 of 58 with follow-up available and does not "
            "publish per-arm mean follow-up, so the follow-up asymmetry that confounds the Agaram "
            "cohort cannot be checked here in either direction."
        ),
    },
    {
        "id": "suemitsu-2025-outcome",
        "endpoint": "outcome_by_partner",
        "label": "MSK, 18 EMC profiled by MSK-IMPACT (secondary genetic alterations series)",
        "n_assessable": 18,
        "sourceId": "suemitsu2025",
        "provenance": "primary",
        "pool": False,
        "contextReason": "population-overlap-unresolved",
        "context_note": (
            "A FOURTH SERIES TESTING THE PARTNER AGAINST SURVIVAL, AND IT IS NULL: 'no statistically "
            "significant correlation was detected between OS and fusion subtypes'. It reports the "
            "partner distribution as explicit integers (EWSR1 14/18, TAF15 2, TCF12 1, FUS 1) but "
            "publishes no per-partner event counts, and its endpoint is OVERALL survival where this "
            "synthesis pools DISEASE-SPECIFIC death, so it could not enter the outcome pool on "
            "POLICY-evidence.md s2.1(2) even if overlap were resolved. "
            "\u26d4 THE BINDING GROUND IS OVERLAP, AND IT IS UNRESOLVED RATHER THAN EXCLUDED: this "
            "is an MSK series and agaram-2014-outcome is MSKCC, so the two may share patients, and "
            "agaram-2014 supplies 3 of the 7 pooled TAF15 disease-specific deaths. Nobody has "
            "checked. "
            "\u2b50 IT IS RECORDED HERE BECAUSE IT CUTS TOWARD THE NULL AND WAS NOT DISCLOSED. An "
            "undisclosed exclusion that weakens the paper's own headline is the worst kind, and "
            "this one sat in the paper's own companion (partner-event-counts-2026-08-08.md s4, "
            "which calls it 'a third independent series failing to establish the partner as a "
            "prognostic factor') and in its own fetch-target list, with an action item to bring it "
            "in, from 2026-08-08 until a blind seat found it missing on 2026-08-26. "
            "\u26a0 AND IT IS NOT EVIDENCE AGAINST THE PARTNER EITHER: 2 TAF15 patients of 18 "
            "cannot exclude an effect of the size the pooled contrast reports, so this is a series "
            "FAILING TO ESTABLISH the partner, not one refuting it."
        ),
        "counts": {"EWSR1::NR4A3": 14, "TAF15::NR4A3": 2, "TCF12::NR4A3": 1, "FUS::NR4A3": 1},
        "_counts_are_context_only": (
            "Recorded because they are the source's own integers and a reader will want them. NOT "
            "pooled into partner prevalence either: same unresolved MSKCC overlap, and s2.1(3) -- "
            "entry to this series is conditional on having been profiled by MSK-IMPACT."
        ),
    },
    {
        "id": "paioli-2021-outcome",
        "endpoint": "outcome_by_partner",
        "label": "Italian Sarcoma Group, 67 localised molecularly confirmed EMC",
        "n_assessable": 67,
        "sourceId": "paioli2021",
        "provenance": "primary",
        "pool": False,
        "contextReason": "counts-not-reported",
        # ⭐ PROMOTED OUT OF THE PROSE NOTE, 2026-08-27 (CYC-0013). These three p-values are stated
        # at six sites in the manuscript, and until this commit their only home in this file was
        # the `context_note` sentence below — a number typed inside a paragraph, which no guard can
        # read and no binding can derive from. They are the SOURCE'S OWN tests, quoted as published
        # (Paioli 2021's abstract is all this repository holds — see `full_text_closed`), so they
        # are kept apart from the Fisher values this file computes exactly as Huang's are.
        "published_p_values": {
            "disease_free_survival_by_partner": 0.08,
            "distant_metastasis_free_survival_by_partner": 0.09,
            "size_vs_dmfs": 0.004,
            "note": (
                "The authors' own tests, read from the abstract. The two partner contrasts reach "
                "no conventional threshold and the SIZE covariate does -- the same pattern "
                "huang-2023-outcome's multivariable model shows. Whether this analysis was "
                "adjusted is NOT recorded in anything held here, so it is not counted as a second "
                "multivariable result."
            ),
        },
        "full_text_closed": True,
        "context_note": (
            "THE THIRD INDEPENDENT TEST OF THE PARTNER AS A PROGNOSTIC FACTOR, AND IT IS NEGATIVE "
            "AT THE CONVENTIONAL THRESHOLD. NR4A3-EWS showed only a TREND toward better "
            "disease-free survival and distant-metastasis-free survival versus NR4A3-TAF15, while "
            "primary tumour SIZE was significantly related to DMFS -- the same pattern Huang 2023 "
            "found. The three p-values are in `published_p_values` above and are deliberately NOT "
            "restated here: one fact, one place. No per-partner event counts are published, so "
            "POLICY-evidence.md s2.1(2) bars it from the pool; its prevalence counts are pooled "
            "separately below."
        ),
    },
    # ---- endpoint: fusion-partner prevalence -------------------------------
    # Denominator convention: PARTNER-ASSIGNED cases only. Every series leaves some tumours
    # NR4A3-rearranged with no partner identified, and the series do not report that residue the
    # same way (Paioli's abstract does not report it at all). Pooling over "cases tested" would
    # therefore mean different things in different rows; pooling over "cases with a partner
    # assigned" means one thing everywhere. The unassigned residue is recorded per cohort rather
    # than dropped.
    {
        "id": "agaram-2014-prevalence",
        "endpoint": "partner_prevalence",
        "label": "MSKCC, 26 consecutive EMC, FISH",
        "sourceId": "agaram2014",
        "provenance": "primary",
        "populationKey": "mskcc-emc-consecutive",
        "counts": {"EWSR1::NR4A3": 16, "TAF15::NR4A3": 7, "TCF12::NR4A3": 1},
        "n_tested": 26,
        "not_partner_assigned": 2,
        "pool": True,
    },
    {
        "id": "huang-2023-prevalence",
        "endpoint": "partner_prevalence",
        "label": "Taiwan, 58 FISH-confirmed EMC",
        "sourceId": "huang2023",
        "provenance": "primary",
        "populationKey": "taiwan-emc-series",
        "counts": {"EWSR1::NR4A3": 46, "TAF15::NR4A3": 9, "TCF12::NR4A3": 2},
        "n_tested": 58,
        "not_partner_assigned": 1,
        "pool": True,
    },
    {
        "id": "lenz-2023-prevalence",
        "endpoint": "partner_prevalence",
        "label": "Czech Republic, 12 successfully typed EMC of 17",
        "sourceId": "lenz2023",
        "provenance": "primary",
        "populationKey": "czech-emc-series",
        "counts": {"EWSR1::NR4A3": 8, "TAF15::NR4A3": 2, "TCF12::NR4A3": 1},
        "n_tested": 12,
        "not_partner_assigned": 1,
        "pool": True,
    },
    {
        "id": "paioli-2021-prevalence",
        "endpoint": "partner_prevalence",
        "label": "Italian Sarcoma Group, 62 partner-assigned of 67 localised EMC",
        "sourceId": "paioli2021",
        "provenance": "primary",
        "populationKey": "isg-localised-emc",
        "counts": {"EWSR1::NR4A3": 50, "TAF15::NR4A3": 10, "TCF12::NR4A3": 1, "TFG::NR4A3": 1},
        "n_tested": 67,
        "not_partner_assigned": 5,
        "pool": True,
        "note": (
            "The abstract's percentages (80/16/2/2) are over 62, not 67, which is how the "
            "partner-assigned denominator is established. The 5-patient residue is not described."
        ),
    },
    {
        "id": "llombart-bosch-2022-prevalence",
        "endpoint": "partner_prevalence",
        "label": "Valencia, 31 EMC (congress abstract)",
        "sourceId": "llombartBosch2022",
        "provenance": "primary",
        "counts": {"EWSR1::NR4A3": 19, "TAF15::NR4A3": 7},
        "n_tested": 31,
        "not_partner_assigned": 5,
        "pool": False,
        "contextReason": "abstract-only",
        "context_note": (
            "Meeting abstract, not peer-reviewed as a full report, and it reports no third partner "
            "class at all, so its 5-case residue cannot be interpreted the way the other rows' can. "
            "Its TAF15 share over assigned cases (7 of 26) is the highest of any series here and is "
            "quoted only as a range endpoint."
        ),
    },
    {
        "id": "klubickova-2022-prevalence",
        "endpoint": "partner_prevalence",
        "label": "Pilsen/Znojmo, 11 EMC (congress abstract)",
        "sourceId": "klubickova2022",
        "provenance": "primary",
        "counts": {"EWSR1::NR4A3": 7, "TAF15::NR4A3": 1, "TCF12::NR4A3": 1},
        "n_tested": 11,
        "not_partner_assigned": 2,
        "pool": False,
        "contextReason": "population-overlap",
        "context_note": (
            "Same Czech group and same institutions as Lenz 2023 (Klubickova is a co-author of "
            "both), published months apart. Almost certainly the same patients; the larger, "
            "peer-reviewed report is the one pooled."
        ),
    },
    {
        "id": "sjogren-2003-prevalence",
        "endpoint": "partner_prevalence",
        "label": "Goteborg, 10 EMCs from nine patients (cytogenetic/SKY/FISH/RT-PCR series)",
        "sourceId": "sjogren2003",
        "provenance": "primary",
        "counts": {"EWSR1::NR4A3": 5, "TAF15::NR4A3": 3, "TCF12::NR4A3": 1},
        "n_tested": 9,
        "not_partner_assigned": 0,
        "pool": False,
        "contextReason": "outcome-is-the-inclusion-criterion",
        "counts_are_PATIENT_level_and_the_abstract_s_are_NOT": (
            "⛔ TWO DIFFERENT SETS OF INTEGERS EXIST IN THIS PAPER AND ONLY ONE OF THEM MAY BE "
            "POOLED. The abstract counts TUMOURS -- 'EWS-TEC (five cases, of which one was a novel "
            "fusion), TAF2N-TEC (four cases), and TCF12-TEC (one case)', which sums to the ten of "
            "its title. The Discussion counts PATIENTS: 'We detected a fusion transcript in all 10 "
            "EMCs; EWS-TEC, TAF2N-TEC, and TCF12-TEC fusions were found in tumors from five, "
            "three, and one patient, respectively.' Table 3's own title -- 'Summary of "
            "Cytogenetics, SKY, FISH, and RT-PCR Analyses in 10 EMCs from Nine Patients' -- and "
            "its footnotes reconcile them: '*Case 4 A, B, and C represent different parts of the "
            "same tumor. + Case 6 I and II represent two separate metastases from one patient.' "
            "The counts above are the PATIENT-level ones, per POLICY-evidence.md s2.3's "
            "within-study mutually-exclusive-strata rule; pooling the abstract's TAF2N integer "
            "would count case 6's patient twice."
        ),
        "entry_route_per_patient": {
            "_why_this_field_exists": (
                "s2.1(3) is decided by HOW EACH PATIENT GOT IN, so the entry route is recorded per "
                "patient rather than characterised in prose. Read from Materials and Methods: "
                "'Ten EMCs from nine patients were analyzed (Table 1). The tumors from five of the "
                "patients (cases 1 to 5) have not been previously reported. The remaining five "
                "tumors from four patients (cases 6-I and 6-II as well as cases 7 to 9) have been "
                "previously reported regarding the expression of EMC-specific fusion transcripts, "
                "and all but two of these (cases 5 and 6-I) have also been cytogenetically "
                "analyzed. 7,12,15' Partners per case are read from Table 3."
            ),
            "new_in_this_series": {
                "cases": [1, 2, 3, 4, 5],
                "partners": {"EWSR1::NR4A3": 4, "TAF15::NR4A3": 1, "TCF12::NR4A3": 0},
                "fusion_status_at_entry": "UNKNOWN -- the series went looking: 'To search for "
                                          "possible EWS-TEC, TAF2N-TEC, and TCF12-TEC fusion "
                                          "transcripts in cases 1 to 5, we performed RT-PCR "
                                          "experiments'. Their 5/5 partner assignment is MEASURED.",
            },
            "previously_reported_by_the_same_group": {
                "cases": [6, 7, 8, 9],
                "partners": {"EWSR1::NR4A3": 1, "TAF15::NR4A3": 2, "TCF12::NR4A3": 1},
                "fusion_status_at_entry": (
                    "ALREADY PUBLISHED -- these four are in because their fusion transcript had "
                    "been reported, so partner assignment is the entry ticket and a "
                    "partner-unassigned tumour could not have been among them."
                ),
                "the_three_prior_reports": [
                    "ref 7 -- Stenman G, Andersson H, Mandahl N, Meis-Kindblom JM, Kindblom L-G: "
                    "Translocation t(9;22)(q22;q12) is a primary cytogenetic abnormality in "
                    "extraskeletal myxoid chondrosarcoma. Int J Cancer 1995, 62:398-402",
                    "ref 12 -- Sjogren H, Meis-Kindblom J, Kindblom L-G, Aman P, Stenman G: Fusion "
                    "of the EWS-related gene TAF2N to TEC in extraskeletal myxoid chondrosarcoma. "
                    "Cancer Res 1999, 59:5064-5067 (PMID 10537274) -- the TAF2N index report",
                    "ref 15 -- Sjogren H, Wedell B, Meis-Kindblom JM, Kindblom L-G, Stenman G: "
                    "Fusion of the NH2-terminal domain of the basic helix-loop-helix protein TCF12 "
                    "to TEC ... Cancer Res 2000 (PMID 11156374) -- the TCF12 index report, whose "
                    "tumour is case 8, karyotype 48,X,-Y,t(9;15)(q22;q21),+12,"
                    "der(15)t(9;15)(q22;q21),+19[18]",
                ],
            },
        },
        "context_note": (
            "⛔ REFUSED AT POLICY-evidence.md s2.1(3), AND THE REFUSAL COSTS US THE HIGHER NUMBER. "
            "Four of the nine patients are in this series BECAUSE the same group had already "
            "published their fusion transcript (refs 7, 12, 15 above), so for those four the "
            "outcome -- which partner, and whether a partner can be named at all -- IS the "
            "inclusion criterion, which is the condition s2.1(3) exists to refuse. It is not an "
            "argument from provenance: the enrichment is visible in the counts. The four "
            "structurally-admitted patients are 3/4 variant-partner (2 TAF15 + 1 TCF12); the five "
            "freely-admitted ones are 1/5. And the consequence that matters for a coverage "
            "denominator is this series' partner-unassigned residue of ZERO, which is measured on "
            "five patients and structural on the other four. ⚠ THE DIRECTION IS THE CHECK A READER "
            "IS ENTITLED TO MAKE: a zero residue RAISES the arithmetic coverage ceiling, so "
            "applying the rule costs coverage rather than buying it. What it would have produced "
            "is computed -- never typed -- in research/manuscripts/aso_coverage_ladder.py, "
            "`fifth_partner_cohort_deliberately_not_pooled`."
        ),
        "⚠_it_also_reaches_the_outcome_pool_and_is_barred_there_too": (
            "Table 1 publishes a free-text follow-up string per case ('LR 13 years; AWD 15 years', "
            "'LR & pulmonary mets 8 years; TRD 10 years', ...) which joins to Table 3's partner "
            "column, so a TAF15-vs-EWSR1 outcome arm could be CONSTRUCTED from it. It is not, on "
            "two independent grounds: s2.1(3) as above, and s2.1(2) -- this paper publishes no "
            "per-partner outcome EVENT COUNTS, only per-patient narrative, so any arm would be "
            "this repository's extraction rather than the source's integers. ⛔ THE MOVE IT WOULD "
            "MAKE IS NAMED SO THAT NOT MAKING IT IS VISIBLE: its three TAF15 patients record no "
            "tumour-related death, which would pull the pooled TAF15 disease-specific-death arm "
            "DOWN -- i.e. toward the null the multivariable analysis in huang-2023-outcome already "
            "warns the crude proportions are confounded by."
        ),
    },
    # ---- mechanism / preclinical context, never pooled ---------------------
    {
        "id": "brenca-2019-mechanism",
        "endpoint": "mechanism",
        "label": "Transcriptional profiling, 7 EWSR1-NR4A3 vs 5 TAF15-NR4A3 EMC",
        "sourceId": "brenca2019",
        "provenance": "primary",
        "pool": False,
        "contextReason": "not-a-clinical-endpoint",
        "context_note": (
            "The axon-guidance switch: class 4-6 semaphorins and pro-tumorigenic guidance cues "
            "higher in TAF15-NR4A3, growth-inhibitory class 3 semaphorins higher in EWSR1-NR4A3, "
            "recapitulated in cells engineered to express either chimera, with greater "
            "anchorage-independent growth for TAF15-NR4A3. INDEPENDENCE CAVEAT: same consortium "
            "(Stacchiotti/Maestro, Milan/Aviano) as both clinical reports, so the mechanism is not "
            "an independent replication of the clinical correlation -- it is the same investigators "
            "explaining their own observation."
        ),
    },
    {
        "id": "bangerter-2022-exvivo",
        "endpoint": "preclinical_drug_response",
        "label": "Matched patient-derived ex vivo pair: USZ20-EMC1 (EWSR1::NR4A3) vs USZ22-EMC2 (TAF15::NR4A3)",
        "sourceId": "bangerter2022",
        "provenance": "primary",
        "pool": False,
        "contextReason": "n=1-per-arm-preclinical",
        "context_note": (
            "READ THIS AGAINST THE HYPOTHESIS, NOT WITH IT. ** CORRECTED 2026-08-07: superseded, "
            "retained -- 'The only matched EWSR1/TAF15 model pair in existence was screened over 40 "
            "agents'. The 40-drug screen ran on USZ20-EMC1 ALONE, verbatim: 'A medium throughput drug "
            "screen using 40 drugs was conducted with USZ20-EMC1 at passage 5.' Only carfilzomib, "
            "doxorubicin and venetoclax went on to the VALIDATION step that used both models, and it "
            "is that step -- not the 40-drug screen -- the partner-independence sentences describe. "
            "The correction does not weaken the reading: the comparison was always the validation. "
            "It is the same over-claim this repository retracted on 2026-08-06 for a different "
            "document, reappearing here.** The authors' finding is partner-"
            "INDEPENDENCE: 'Both models independent of the NR4A3 fusion partner showed high "
            "sensitivity to carfilzomib and good to moderate sensitivity to doxorubicin', and "
            "'Similar drug responses were seen in both models, independent of the fusion partner "
            "from NR4A3.' The only partner-differential reported is a scoring-threshold one: the "
            "carfilzomib + venetoclax and carfilzomib + doxorubicin combinations scored synergistic "
            "(ZIP/Loewe/Bliss/HSA) in the EWSR1 model and additive in the TAF15 model, with one "
            "model per arm and no statistical claim. NEITHER MODEL WAS TESTED AGAINST AN "
            "ANTIANGIOGENIC TKI, so this cannot confirm or refute the clinical correlation; what it "
            "does do is bound the biomarker's scope -- there is no evidence that the partner "
            "predicts response to drug classes in general."
        ),
    },
]


def _self_check(by_id: dict) -> None:
    """Arithmetic guards. A silently wrong count is the only failure mode that matters here.

    Each assertion re-derives a published TOTAL from the per-partner strata, so a typo in a
    stratum cannot survive: it has to disagree with a number printed in the source abstract.
    """
    suni = by_id["sunitinib-2014"]["strata"]
    assert suni["EWSR1::NR4A3"]["denom"] + suni["TAF15::NR4A3"]["denom"] == 10, (
        "sunitinib strata must partition the 10 patients in PMID 24703573"
    )
    assert suni["EWSR1::NR4A3"]["events"] == 6, "PMID 24703573 abstract: six RECIST partial responses"

    pazo = by_id["pazopanib-NCT02066285"]["strata"]
    assert pazo["TAF15::NR4A3"]["denom"] + pazo["non-TAF15"]["denom"] == 22, (
        "pazopanib strata must partition the 22 evaluable patients in PMID 31331701"
    )
    assert pazo["TAF15::NR4A3"]["events"] + pazo["non-TAF15"]["events"] == 4, (
        "PMID 31331701 abstract: four objective responses"
    )

    ag = by_id["agaram-2014-outcome"]["strata"]
    dod = (
        ag["EWSR1::NR4A3"]["disease_specific_death"]["events"]
        + ag["TAF15::NR4A3"]["disease_specific_death"]["events"]
    )
    assert dod == 4, "PMID 24746215: four patients died of disease in total (1 EWSR1 + 3 TAF15)"

    # ---- Huang 2023 Table 1: every published partition must close on its own denominator ----
    hg = by_id["huang-2023-outcome"]["strata"]
    for partner, denom in (("EWSR1::NR4A3", 42), ("TAF15::NR4A3", 8)):
        s = hg[partner]
        assert (
            s["no_evidence_of_disease"]["events"]
            + s["alive_with_disease"]["events"]
            + s["disease_specific_death"]["events"]
            == denom
        ), f"PMID 36948401 Table 1: NED + AWD + DOD must partition the {partner} arm ({denom})"
        assert (
            s["distant_metastasis_at_presentation"]["events"]
            + s["distant_metastasis_after_presentation"]["events"]
            == s["distant_metastasis_any"]["events"]
        ), f"PMID 36948401 Table 1: metastasis at presentation + subsequent must equal any ({partner})"
        assert s["distant_metastasis_any"]["events"] <= denom, "metastasis cannot exceed the arm"
        for key in (
            "disease_specific_death",
            "alive_with_disease",
            "no_evidence_of_disease",
            "local_recurrence",
            "distant_metastasis_any",
            "distant_metastasis_at_presentation",
            "distant_metastasis_after_presentation",
        ):
            assert s[key]["denom"] == denom, f"{partner}.{key} must sit on the arm's own denominator"

    hz = by_id["huang-2023-outcome"]
    assert hz["strata"]["EWSR1::NR4A3"]["disease_specific_death"]["denom"] + hz["strata"][
        "TAF15::NR4A3"
    ]["disease_specific_death"]["denom"] == 50, (
        "PMID 36948401: 50 partner-assigned patients with follow-up (42 EWSR1 + 8 TAF15); the "
        "remaining 3 of the 53 followed are the miscellaneous group"
    )
    hp = by_id["huang-2023-prevalence"]["counts"]
    assert hp["EWSR1::NR4A3"] == 46 and hp["TAF15::NR4A3"] == 9, (
        "the outcome arms must be follow-up subsets of the prevalence counts in the same paper"
    )
    assert hz["strata"]["EWSR1::NR4A3"]["disease_specific_death"]["denom"] <= hp["EWSR1::NR4A3"]
    assert hz["strata"]["TAF15::NR4A3"]["disease_specific_death"]["denom"] <= hp["TAF15::NR4A3"]
    sz = hz["size_covariate"]
    assert sz["EWSR1::NR4A3"]["over_10cm"]["denom"] == hp["EWSR1::NR4A3"], (
        "the size covariate is over the whole partner-assigned arm, not the followed subset"
    )
    assert sz["TAF15::NR4A3"]["over_10cm"]["denom"] == hp["TAF15::NR4A3"]


def _roster(endpoint: str) -> dict:
    """Who was identified, who was pooled and who was excluded — DERIVED from COHORTS, not typed.

    ⛔ ADDED 2026-08-26 BECAUSE THE TYPED VERSION SILENTLY UNDERCOUNTED THE MOMENT A COHORT WAS
    ADDED. `B_outcome_by_partner` carried `cohorts_identified: 3` and an excluded map naming one
    study; adding `suemitsu-2025-outcome` left both untouched, so the artifact would have asserted
    that three outcome cohorts exist while holding four — and the manuscript's inclusion table,
    which is the thing a reader checks selective reporting against, would have disagreed with it.
    That is the same failure the seat had just found in prose, reappearing one layer down.
    CLAUDE.md rule 1.1: a total is DERIVED, never typed.

    Excluded entries carry the cohort's own `contextReason` slug, so the reason a study is out is
    stated once, in the cohort record, and read from there everywhere else.
    """
    rows = [c for c in COHORTS if c["endpoint"] == endpoint]
    pooled = [c["id"] for c in rows if c.get("pool")]
    return {
        "cohorts_identified": len(rows),
        "cohorts_pooled": len(pooled),
        "pooled_cohorts": pooled,
        "cohorts_excluded": {
            c["id"]: "%s (POLICY-evidence.md s2.1/s2.3) -- see cohorts[%s].context_note"
                     % (c.get("contextReason") or "unstated", c["id"])
            for c in rows if not c.get("pool")
        },
    }


def _stratum_extent(*contrasts) -> dict:
    """The per-stratum denominator and event range, DERIVED from the pooled contrasts themselves.

    ⛔ THIS EXISTS BECAUSE THE TYPED VERSION WENT STALE AND NOBODY NOTICED FOR EIGHTEEN DAYS.
    `method.not_used` justified refusing a random-effects pooler with "2-19 patients and 0-10 events
    per stratum". That was true of the TKI-response strata alone; the day Huang 2023's counts were
    pooled the outcome denominators went past nineteen, and the sentence kept asserting the old pair
    in the artifact and twice in this file's docstring while the manuscript retracted it in s2.5.
    CLAUDE.md rule 1.1: a total is DERIVED, never typed — so it is derived, and the class of defect
    is closed rather than the instance.

    ⚠ TAKES AN EXPLICIT LIST OF CONTRASTS, NOT A RECURSIVE WALK, AND THAT CHOICE IS THE WHOLE
    CORRECTNESS ARGUMENT. A walk over the analysis blocks was written first and returned 2-58 /
    0-16, because it also swept the overlap-sensitivity arms, the per-cohort breakdowns and the
    Huang-only within-cohort readings — none of which is a stratum a random-effects pooler would
    have been run over. That number would have been derived, reproducible, and about the wrong set;
    a total that is computed is not thereby the total the sentence claims. The named contrasts below
    are exactly the strata s2.5 describes, and adding one is a visible edit here rather than a
    silent widening.
    """
    events, denoms = [], []
    for c in contrasts:
        for arm in ("taf15_arm", "comparator_arm"):
            a = c[arm]                    # KeyError on drift, deliberately: fail loud, not silent
            events.append(int(a["events"]))
            denoms.append(int(a["denom"]))
    if not denoms:
        raise RuntimeError("_stratum_extent was passed no contrasts — the caller moved")
    return {"denom_lo": min(denoms), "denom_hi": max(denoms),
            "events_lo": min(events), "events_hi": max(events), "n_strata": len(denoms)}


def build() -> dict:
    """Assemble the whole document IN MEMORY. Pure: reads no file and writes none."""
    by_id = {c["id"]: c for c in COHORTS}
    _self_check(by_id)

    # ---------------- analysis A: response to an antiangiogenic TKI ---------
    suni = by_id["sunitinib-2014"]["strata"]
    pazo = by_id["pazopanib-NCT02066285"]["strata"]

    primary_taf = wilson(pazo["TAF15::NR4A3"]["events"], pazo["TAF15::NR4A3"]["denom"])
    primary_oth = wilson(pazo["non-TAF15"]["events"], pazo["non-TAF15"]["denom"])

    union_taf = wilson(
        suni["TAF15::NR4A3"]["events"] + pazo["TAF15::NR4A3"]["events"],
        suni["TAF15::NR4A3"]["denom"] + pazo["TAF15::NR4A3"]["denom"],
    )
    union_oth = wilson(
        suni["EWSR1::NR4A3"]["events"] + pazo["non-TAF15"]["events"],
        suni["EWSR1::NR4A3"]["denom"] + pazo["non-TAF15"]["denom"],
    )

    analysis_tki = {
        "question": "Does the NR4A3 5' fusion partner predict objective response to an antiangiogenic TKI in advanced EMC?",
        "endpoint": "RECIST objective response (partial or complete) on sunitinib or pazopanib",
        "cohorts_identified": 3,
        "cohorts_pooled_primary": 1,
        "cohorts_excluded": {
            "sunitinib-2014": "population-overlap (POLICY-evidence.md s2.3) -- cannot be shown distinct from the pazopanib trial",
            "sunitinib-2012-two-cases": "population-overlap (POLICY-evidence.md s2.3) -- contained in the 2014 series",
        },
        "primary_non_overlapping": {
            "definition": (
                "POLICY-conformant headline: only cohorts that can be shown non-overlapping. "
                "Overlap with the sunitinib series cannot be excluded, so the smaller series is "
                "held out and the pazopanib trial stands alone."
            ),
            "contrast": contrast(
                "tki_response_pazopanib_only",
                primary_taf,
                primary_oth,
                "Single-cohort intervals; no between-study weighting is involved.",
            ),
        },
        "secondary_assume_independent": {
            "definition": (
                "Maximal-information analysis, valid ONLY if no patient appears in both reports. "
                "Crude denominator-weighted pool of both cohorts (POLICY-evidence.md s2.2)."
            ),
            "contrast": contrast(
                "tki_response_both_cohorts",
                union_taf,
                union_oth,
                "Denominator-weighted crude pool; the pazopanib trial supplies 19 of 27 comparator patients.",
            ),
            "heterogeneity": heterogeneity(
                [
                    {"cohort": "sunitinib-2014 (EWSR1 arm)", "percent": round(100 * 6 / 8, 1)},
                    {"cohort": "pazopanib-NCT02066285 (non-TAF15 arm)", "percent": round(100 * 4 / 19, 1)},
                ]
            ),
        },
        "overlap_sensitivity_bounds": {
            "explanation": (
                "The truth lies between the two analyses above. Because the sunitinib series' two "
                "TAF15 patients are at worst a subset of the trial's three, the union denominators "
                "are bounded, and the CONCLUSION IS THE SAME AT BOTH ENDS."
            ),
            "taf15_denominator_range": [3, 5],
            "taf15_events": 0,
            "taf15_upper_ci_range_percent": [
                wilson(0, 5)["ci95_hi_percent"],
                wilson(0, 3)["ci95_hi_percent"],
            ],
            "comparator_denominator_range": [19, 27],
        },
        "sensitivity_analyses": {
            "taf15_patient_not_evaluable": {
                "premise": (
                    "If the one pazopanib patient who died before the primary analysis carried "
                    "TAF15::NR4A3, the trial's strata are 0/2 and 4/20 rather than 0/3 and 4/19."
                ),
                "taf15_arm": wilson(0, 2),
                "comparator_arm": wilson(4, 20),
                "conclusion": "The TAF15 upper bound rises; the contrast weakens. No claim here depends on which way this resolves.",
            }
        },
        "verdict": (
            "Zero of the TAF15::NR4A3 patients treated with an antiangiogenic TKI in the reports "
            "THIS SYNTHESIS EXAMINED responded -- and that is {lo_n} to {hi_n} patients in total. "
            "\u26d4 NO SYSTEMATIC SEARCH WAS RUN (methods s2.3a): the candidate literature is this "
            "repository's existing EMC citation set, the reviews already in it, the reports they "
            "cite and the reports citing them. So this reads 'no such report was found in the "
            "sources examined', NEVER 'no such patient has ever been reported' -- which is why a "
            "single counter-report overturns it (falsifier #1). The 95% "
            "Wilson upper bound on the TAF15 response rate is {u5}% (both cohorts, assuming "
            "independence) to {u3}% (pazopanib alone), which sits ABOVE the comparator arm's point "
            "estimate in both analyses ({c5}% and {c3}% respectively). Post-hoc Fisher exact "
            "two-sided p = {p5} pooled and {p3} for the trial alone. The direction is consistent "
            "across two cohorts, two drugs and five years of accrual (July 2011 to January 2017); "
            "the magnitude is not established, and "
            "the data cannot exclude a TAF15 response rate equal to the EWSR1 one."
        ).format(
            lo_n=primary_taf["denom"],
            hi_n=union_taf["denom"],
            u5=union_taf["ci95_hi_percent"],
            u3=primary_taf["ci95_hi_percent"],
            c5=union_oth["percent"],
            c3=primary_oth["percent"],
            p5=round(fisher_exact_two_sided(0, union_taf["denom"], union_oth["events"], union_oth["denom"] - union_oth["events"]), 3),
            p3=round(fisher_exact_two_sided(0, primary_taf["denom"], primary_oth["events"], primary_oth["denom"] - primary_oth["events"]), 3),
        ),
    }

    # ---------------- analysis B: outcome by partner ------------------------
    # TWO cohorts publish EMC outcome event counts by NR4A3 partner as of 2026-08-08. Agaram 2014
    # was the only one until the Huang 2023 full text was read; the counts below are the first
    # time they have been put on one denominator, which is what makes a MAGNITUDE computable at
    # all. It is also the first place the size defeater has to travel with a number rather than
    # sitting in a limitations section -- see `defeater` on every pooled contrast.
    ag = by_id["agaram-2014-outcome"]["strata"]
    hu = by_id["huang-2023-outcome"]
    hus = hu["strata"]
    ews, taf = ag["EWSR1::NR4A3"], ag["TAF15::NR4A3"]
    hu_ews, hu_taf = hus["EWSR1::NR4A3"], hus["TAF15::NR4A3"]

    def arm(key: str, s: dict) -> dict:
        return wilson(s[key]["events"], s[key]["denom"])

    SIZE_DEFEATER = (
        "⛔ THIS MAGNITUDE IS CRUDE AND UNADJUSTED, AND THE LARGER OF ITS TWO COHORTS PUBLISHES "
        "THE ANALYSIS THAT DEFEATS IT. In Huang 2023's own multivariable model for "
        "disease-specific survival, only size >10 cm (P = .004, HR 30.60) and metastasis at "
        "presentation (P = .032, HR 8.14) remain independent; TAF15::NR4A3 LOSES SIGNIFICANCE "
        "UNDER ADJUSTMENT. The same table shows why: 78% of TAF15 tumours were >10 cm against "
        "the EWSR1 arm's 12/46 (P = .025). In the authors' own words the TAF15 survival "
        "difference 'might be partly attributable to the predominance of large tumors > 10 cm in "
        "TAF15-rearranged EMCs'. Paioli 2021 (n = 67) points the same way from a third cohort: a "
        "trend only for the partner (DFS p = 0.08, DMFS p = 0.09) in an analysis where size "
        "reaches p = 0.004. No figure in this block is adjusted for size, and none may be quoted "
        "without this sentence beside it."
    )

    def pooled_contrast(name: str, ag_key: str, hu_key: str, note: str) -> dict:
        t = wilson(
            taf[ag_key]["events"] + hu_taf[hu_key]["events"],
            taf[ag_key]["denom"] + hu_taf[hu_key]["denom"],
        )
        e = wilson(
            ews[ag_key]["events"] + hu_ews[hu_key]["events"],
            ews[ag_key]["denom"] + hu_ews[hu_key]["denom"],
        )
        c = contrast(name, t, e, note)
        c["per_cohort"] = {
            "agaram-2014-outcome": {
                "TAF15::NR4A3": arm(ag_key, taf),
                "EWSR1::NR4A3": arm(ag_key, ews),
                "stratum_key": ag_key,
            },
            "huang-2023-outcome": {
                "TAF15::NR4A3": arm(hu_key, hu_taf),
                "EWSR1::NR4A3": arm(hu_key, hu_ews),
                "stratum_key": hu_key,
            },
        }
        c["heterogeneity_taf15_arm"] = heterogeneity(
            [
                {"cohort": "agaram-2014-outcome", "percent": arm(ag_key, taf)["percent"]},
                {"cohort": "huang-2023-outcome", "percent": arm(hu_key, hu_taf)["percent"]},
            ]
        )
        c["heterogeneity_comparator_arm"] = heterogeneity(
            [
                {"cohort": "agaram-2014-outcome", "percent": arm(ag_key, ews)["percent"]},
                {"cohort": "huang-2023-outcome", "percent": arm(hu_key, hu_ews)["percent"]},
            ]
        )
        c["defeater"] = SIZE_DEFEATER
        return c

    pooled_dod = pooled_contrast(
        "dod_pooled_agaram2014_huang2023",
        "disease_specific_death",
        "disease_specific_death",
        "Crude during-follow-up proportions, mixed follow-up, no censoring "
        "(POLICY-evidence.md s2.4). Both cohorts report died-of-disease as a cell of a complete "
        "final-status partition, so the endpoints match on a published definition, not a label.",
    )
    pooled_lr = pooled_contrast(
        "lr_pooled_agaram2014_huang2023",
        "local_recurrence",
        "local_recurrence",
        "Crude during-follow-up proportions. Both cohorts report local recurrence as a two-way "
        "positive/negative partition.",
    )
    pooled_met = pooled_contrast(
        "distant_metastasis_after_presentation_pooled_agaram2014_huang2023",
        "distant_recurrence",
        "distant_metastasis_after_presentation",
        "⚠ MATCHED ON LABELS, NOT ON A PUBLISHED DEFINITION -- see "
        "cohorts[huang-2023-outcome].estimand_warning. Agaram's 'distant recurrence' is pooled "
        "with Huang's metastasis-developed-after-presentation cell; neither report states whether "
        "a patient metastatic at presentation was inside its recurrence denominator.",
    )

    huang_met_any = contrast(
        "distant_metastasis_any_huang2023_within_cohort",
        arm("distant_metastasis_any", hu_taf),
        arm("distant_metastasis_any", hu_ews),
        "WITHIN-COHORT ONLY, deliberately not pooled: 'any distant metastasis, at presentation or "
        "later' has no counterpart stratum in Agaram 2014. Printed because it is the reading on "
        "which the authors' own published p-value (P = .728 on the three-way table) was computed.",
    )
    huang_met_presentation = contrast(
        "metastasis_at_presentation_huang2023_within_cohort",
        arm("distant_metastasis_at_presentation", hu_taf),
        arm("distant_metastasis_at_presentation", hu_ews),
        "WITHIN-COHORT ONLY. This is the covariate that IS independent in Huang's multivariable "
        "model (P = .032, HR 8.14), and by partner it is 1/8 versus 8/42 -- i.e. the TAF15 arm "
        "does not carry the excess of the one metastasis variable that survives adjustment.",
    )

    analysis_outcome = {
        "question": "Does the NR4A3 5' fusion partner predict disease-specific death, recurrence or metastasis?",
        "what_changed_2026_08_08": (
            "⭐ A MAGNITUDE IS COMPUTABLE FOR THE FIRST TIME. Until 2026-08-08 exactly one cohort "
            "(Agaram 2014, 23 partner-assigned patients) published EMC outcome event counts by "
            "NR4A3 partner, so the 'pool' was a single-cohort Wilson interval and the file said so. "
            "A human read Huang 2023's published PDF and extracted its Table 1, adding 50 "
            "partner-assigned patients with follow-up from an independent country and institution "
            "set. The outcome pool is now 73 patients across two non-overlapping cohorts. ⚠ THIS "
            "IS THE PROGNOSIS QUESTION AND ONLY THE PROGNOSIS QUESTION -- see "
            "`does_not_touch_the_response_question` below."
        ),
        "does_not_touch_the_response_question": (
            "⛔ HUANG 2023 CONTAINS NO ANTIANGIOGENIC-TKI RESPONSE DATA AND MOVES ANALYSIS A BY "
            "ZERO. It is a pathology series with a survival analysis; the only systemic therapy it "
            "reports is chemotherapy, as a prognostic covariate, not as a response endpoint and "
            "not by partner. The TREATMENT-RESPONSE half of this page is still what it was: the "
            "entire published TAF15::NR4A3 antiangiogenic experience is 3 to 5 patients with ZERO "
            "responses, and a zero-event arm yields no magnitude at any denominator. "
            "A_tki_objective_response is unchanged, word for word, by this integration. Anyone "
            "reading the new prognostic magnitude as if it settled the response question has "
            "conflated two different endpoints in two different populations."
        ),
        **_roster("outcome_by_partner"),
        "non_overlap_argument": (
            "MSKCC (New York, 26 consecutive cases) versus 15 Taiwanese institutions led from "
            "Chang Gung Memorial Hospital (58 FISH-confirmed cases). No shared authors, no shared "
            "referral network, different continents. POLICY-evidence.md s2.3 is satisfied on the "
            "same grounds the prevalence pool already used for these two series."
        ),
        "disease_specific_death": pooled_dod,
        "local_recurrence": pooled_lr,
        "distant_metastasis_after_presentation": pooled_met,
        "huang_only_metastasis_readings": {
            "any_distant_metastasis": huang_met_any,
            "metastasis_at_presentation": huang_met_presentation,
            "published_three_way_p": hu["published_p_values"]["distant_metastasis_three_way"],
        },
        "single_cohort_contrasts_retained": {
            "_why": (
                "The per-cohort figures are kept because POLICY-evidence.md s2.2 requires the "
                "cohorts be shown side by side, and because the 2026-08-07 version of this page "
                "quoted the Agaram-only numbers -- a reader meeting those elsewhere must be able "
                "to find them here rather than conclude they were dropped."
            ),
            "agaram2014": {
                "disease_specific_death": contrast(
                    "dod_agaram2014",
                    arm("disease_specific_death", taf),
                    arm("disease_specific_death", ews),
                    "Single cohort (MSKCC). Crude during-follow-up proportions, mixed follow-up.",
                ),
                "local_recurrence": contrast(
                    "lr_agaram2014",
                    arm("local_recurrence", taf),
                    arm("local_recurrence", ews),
                    "Single cohort (MSKCC).",
                ),
                "distant_recurrence": contrast(
                    "dr_agaram2014",
                    arm("distant_recurrence", taf),
                    arm("distant_recurrence", ews),
                    "Single cohort (MSKCC).",
                ),
            },
            "huang2023": {
                "disease_specific_death": contrast(
                    "dod_huang2023",
                    arm("disease_specific_death", hu_taf),
                    arm("disease_specific_death", hu_ews),
                    "Single cohort (Taiwan). The authors' own three-way final-status test on this "
                    "table gives P = .047.",
                ),
                "local_recurrence": contrast(
                    "lr_huang2023",
                    arm("local_recurrence", hu_taf),
                    arm("local_recurrence", hu_ews),
                    "Single cohort (Taiwan). The authors' own test gives P = 1.000.",
                ),
                "distant_metastasis_after_presentation": contrast(
                    "dr_huang2023",
                    arm("distant_metastasis_after_presentation", hu_taf),
                    arm("distant_metastasis_after_presentation", hu_ews),
                    "Single cohort (Taiwan), subsequent metastasis only.",
                ),
            },
        },
        "metastasis_reading": (
            "⚠ THE REVERSAL DOES NOT SURVIVE THE SECOND COHORT, AND WHAT REPLACES IT IS A NULL. "
            "*Superseded, retained: 'THE DIRECTION REVERSES FOR METASTASIS ... the opposite of the "
            "narrative repeated across the review literature that TAF15 tumours are the "
            "metastasising ones.'* That statement was true of the ONE cohort then available and is "
            "not true of the two now available. Agaram 2014 alone has distant recurrence {ade}/"
            "{adn} ({adp}%) in EWSR1 against {atde}/{atdn} ({atdp}%) in TAF15 -- EWSR1 higher, the "
            "reversal. Huang 2023 runs the other way ({hde}/{hdn} = {hdp}% EWSR1 against {htde}/"
            "{htdn} = {htdp}% TAF15 for metastasis after presentation), i.e. in the reviews' own "
            "direction. Pooled over both, the contrast is {pte}/{ptn} ({ptp}%) TAF15 against "
            "{pee}/{pen} ({pep}%) EWSR1 -- a gap of {pgap} percentage points with overlapping "
            "intervals and post-hoc Fisher p = {pfp}. ⭐ WHAT SURVIVES IS THE NEGATIVE, AND IT IS "
            "NOW STRONGER THAN THE REVERSAL WAS: the largest series to test metastasis by partner "
            "DIRECTLY reports P = .728 on its own three-way table, so the review literature's "
            "metastasis claim (attributed here to PMC7563993 alone, Stacchiotti 2020, the only "
            "actual review among the four PMCIDs previously cited for it; the other three were "
            "MISATTRIBUTED rather than fabricated -- two are single-patient case reports and one "
            "is a national-registry cohort, and none of them is review literature -- and have been "
            "removed; Appendix A11 -- asserting lower metastasis or better "
            "metastasis-free survival with EWSR1) is not established by "
            "either cohort, in either direction. ⚠ AND THE ATTRIBUTION IS BY RECORD, NOT BY "
            "QUOTATION: that review's metastasis sentence is quoted nowhere in this artifact, so the "
            "provenance standard s8 asserts for every count is not met for this one claim, and it "
            "rests on n = 1 review rather than on a literature. A single-cohort reversal quoted as a finding was "
            "always one cohort from being overturned; a two-cohort null is a reading of the same "
            "evidence that does not depend on which cohort you happened to have."
        ).format(
            ade=ews["distant_recurrence"]["events"],
            adn=ews["distant_recurrence"]["denom"],
            adp=arm("distant_recurrence", ews)["percent"],
            atde=taf["distant_recurrence"]["events"],
            atdn=taf["distant_recurrence"]["denom"],
            atdp=arm("distant_recurrence", taf)["percent"],
            hde=hu_ews["distant_metastasis_after_presentation"]["events"],
            hdn=hu_ews["distant_metastasis_after_presentation"]["denom"],
            hdp=arm("distant_metastasis_after_presentation", hu_ews)["percent"],
            htde=hu_taf["distant_metastasis_after_presentation"]["events"],
            htdn=hu_taf["distant_metastasis_after_presentation"]["denom"],
            htdp=arm("distant_metastasis_after_presentation", hu_taf)["percent"],
            pte=pooled_met["taf15_arm"]["events"],
            ptn=pooled_met["taf15_arm"]["denom"],
            ptp=pooled_met["taf15_arm"]["percent"],
            pee=pooled_met["comparator_arm"]["events"],
            pen=pooled_met["comparator_arm"]["denom"],
            pep=pooled_met["comparator_arm"]["percent"],
            pgap=abs(pooled_met["comparator_minus_taf15_percentage_points"]),
            pfp=pooled_met["fisher_exact_two_sided_p"],
        ),
        "follow_up_caveat": (
            "Agaram 2014's two arms differ about two-fold in mean follow-up ({tf} vs {ef} months) "
            "and Huang 2023 publishes no per-arm follow-up at all, so the pooled proportions are "
            "crude during-follow-up rates over cohorts whose observation windows are unequal and, "
            "in one case, unstated (POLICY-evidence.md s2.4). Truncation biases AGAINST the TAF15 "
            "arm accruing events in the Agaram cohort, which makes the death excess harder to "
            "observe rather than easier; nothing equivalent can be said about the Huang cohort "
            "because the number is not published."
        ).format(tf=taf["mean_followup_months"], ef=ews["mean_followup_months"]),
        "verdict": (
            "TWO cohorts, {n} patients with an assigned EWSR1 or TAF15 partner and follow-up, "
            "from two continents with no shared authors. Pooled disease-specific death is "
            "{te}/{tn} ({tp}%, 95% CI {tlo}-{thi}) with TAF15::NR4A3 against {ee}/{en} ({ep}%, "
            "95% CI {elo}-{ehi}) with EWSR1::NR4A3 -- a gap of {gap} percentage points, post-hoc "
            "Fisher exact two-sided p = {p}, and the first time this contrast has had a magnitude "
            "at all. Both cohorts point the same way on death ({c1}% and {c2}% TAF15 mortality "
            "against {c3}% and {c4}% EWSR1). ⛔ AND THE MAGNITUDE ARRIVES WITH ITS OWN DEFEATER "
            "ATTACHED, FROM THE LARGER COHORT'S OWN AUTHORS: adjusted for tumour size and "
            "metastasis at presentation, TAF15::NR4A3 is NOT an independent predictor of "
            "disease-specific survival (only size >10 cm, P = .004, HR 30.60, and metastasis at "
            "presentation, P = .032, HR 8.14, remain), and 78% of TAF15 tumours were >10 cm "
            "(P = .025). Paioli 2021 (n = 67) cannot reach significance on the partner at all "
            "(DFS p = 0.08, DMFS p = 0.09) in an analysis where size reaches p = 0.004. So: THE "
            "CRUDE PARTNER EFFECT ON DEATH IS REAL AND NOW MEASURED; THE INDEPENDENT PARTNER "
            "EFFECT IS NOT ESTABLISHED AND THE ONE SERIES THAT TESTED IT SAYS THE PARTNER IS "
            "STANDING IN FOR SIZE. Local recurrence and distant metastasis show no material "
            "partner separation once both cohorts are in ({lrt}% vs {lre}% and {mt}% vs {me}%)."
        ).format(
            n=pooled_dod["taf15_arm"]["denom"] + pooled_dod["comparator_arm"]["denom"],
            te=pooled_dod["taf15_arm"]["events"],
            tn=pooled_dod["taf15_arm"]["denom"],
            tp=pooled_dod["taf15_arm"]["percent"],
            tlo=pooled_dod["taf15_arm"]["ci95_lo_percent"],
            thi=pooled_dod["taf15_arm"]["ci95_hi_percent"],
            ee=pooled_dod["comparator_arm"]["events"],
            en=pooled_dod["comparator_arm"]["denom"],
            ep=pooled_dod["comparator_arm"]["percent"],
            elo=pooled_dod["comparator_arm"]["ci95_lo_percent"],
            ehi=pooled_dod["comparator_arm"]["ci95_hi_percent"],
            gap=abs(pooled_dod["comparator_minus_taf15_percentage_points"]),
            p=pooled_dod["fisher_exact_two_sided_p"],
            c1=arm("disease_specific_death", taf)["percent"],
            c2=arm("disease_specific_death", hu_taf)["percent"],
            c3=arm("disease_specific_death", ews)["percent"],
            c4=arm("disease_specific_death", hu_ews)["percent"],
            lrt=pooled_lr["taf15_arm"]["percent"],
            lre=pooled_lr["comparator_arm"]["percent"],
            mt=pooled_met["taf15_arm"]["percent"],
            me=pooled_met["comparator_arm"]["percent"],
        ),
    }

    # ---------------- analysis C: partner prevalence ------------------------
    prev = [c for c in COHORTS if c["endpoint"] == "partner_prevalence" and c["pool"]]
    partners = ["EWSR1::NR4A3", "TAF15::NR4A3", "TCF12::NR4A3", "TFG::NR4A3"]
    per_cohort_assigned = {c["id"]: sum(c["counts"].values()) for c in prev}
    tot = sum(per_cohort_assigned.values())
    totals = {k: sum(c["counts"].get(k, 0) for c in prev) for k in partners}
    assert sum(totals.values()) == tot, "prevalence strata must partition the partner-assigned denominator"
    taf_n = totals["TAF15::NR4A3"]

    analysis_prev = {
        "question": "How many EMC patients would a TAF15-vs-EWSR1 stratification actually touch?",
        "denominator_convention": (
            "Partner-assigned cases only. Each cohort's NR4A3-rearranged-but-partner-unassigned "
            "residue is recorded in its `not_partner_assigned` field and excluded from both "
            "numerator and denominator, because the series do not report that residue comparably."
        ),
        "cohorts_pooled": [c["id"] for c in prev],
        "partner_assigned_per_cohort": per_cohort_assigned,
        "cohorts_excluded": {
            "llombart-bosch-2022-prevalence": "abstract-only",
            "klubickova-2022-prevalence": "population-overlap with lenz-2023-prevalence",
            "sjogren-2003-prevalence": (
                "outcome-is-the-inclusion-criterion (s2.1(3)): four of its nine patients are in "
                "the series because the same group had already published their fusion transcript, "
                "so their partner assignment is the entry ticket and its partner-unassigned "
                "residue of zero is structural on that half of the cohort"
            ),
        },
        "non_overlap_argument": (
            "Four geographically and institutionally distinct series -- MSKCC (USA), Taiwanese "
            "institutions, Czech Republic, Italian Sarcoma Group -- with no shared authors between "
            "them and no shared referral network."
        ),
        "⚠_a_fifth_series_EXISTS_and_is_refused_on_a_DIFFERENT_ground": (
            "sjogren-2003-prevalence is not held out for overlap or for being an abstract -- it "
            "is a peer-reviewed, fully-accounted, karyotyped series and it would have PASSED "
            "s2.1(1), (2) at patient level and (4). It fails s2.1(3) alone. That distinction is "
            "recorded because the three exclusions are otherwise easy to read as one kind of "
            "objection, and this one is the kind that a wider denominator makes tempting: it "
            "would have RAISED the coverage ceiling computed in "
            "research/manuscripts/aso_coverage_ladder.py, not lowered it."
        ),
        "pooled": {k: wilson(v, tot) for k, v in totals.items()},
        "heterogeneity_TAF15": heterogeneity(
            [
                {
                    "cohort": c["id"],
                    "percent": round(100 * c["counts"].get("TAF15::NR4A3", 0) / per_cohort_assigned[c["id"]], 1),
                }
                for c in prev
            ]
        ),
        # ⛔ ADDED 2026-08-27 (manuscript Appendix A30). THE COMPARATOR THIS REPLACES HAD NO SOURCE.
        # Until this round the prose compared the pooled share against "the ~27 % the field quotes"
        # -- a characterisation of the literature's practice that nothing in this repository, the
        # manuscript or its reference list ever attested, and which the guard therefore carried as
        # DELIBERATELY UNOWNED. The two sources in the manuscript's own reference list that state a
        # general TAF15 share both give about 20 %. They are recorded here WITH the sentence each
        # states it in, so the comparator is a quotation with a DOI behind it rather than a number
        # somebody remembered, and so an instrument reads it (paper-hardening s8a: close the class).
        # ⚠ `falls_inside_pooled_interval` is DERIVED below, never typed -- it is the whole finding.
        "external_reported_share": {
            "question": (
                "What share does the literature this manuscript cites actually state for "
                "TAF15::NR4A3, as against what this pooling computes?"
            ),
            "percent_approx": 20,
            "scope": (
                "The two sources in the manuscript's reference list that state a GENERAL TAF15 "
                "share. It is a figure this synthesis QUOTES; it is not pooled, re-derived or "
                "weighted here, and the two sources are not independent of each other in any way "
                "this record establishes."
            ),
            "sources": [
                {
                    "citation": "stacchiotti2020review",
                    "reference_number_in_manuscript": 4,
                    "pmcid": "PMC7563993",
                    "doi": "10.3390/cancers12092703",
                    "kind": "narrative review",
                    "quote": (
                        "less frequently (about 20% of cases) to the transactivation domain of "
                        "TAF15"
                    ),
                    "section": "Pathological and Molecular Characteristics",
                },
                {
                    "citation": "bangerter2022",
                    "reference_number_in_manuscript": 12,
                    "pmcid": "PMC9813045",
                    "doi": "10.1007/s13577-022-00818-x",
                    "kind": "journal article, introduction",
                    "quote": "less frequently (approximately 20%) to TAF15",
                    "section": "Introduction",
                },
            ],
            "_attribution": (
                "Both quotations are PubMed Central full-text reads and travel with their DOIs."
            ),
        },
        "context_range_note": (
            "The two excluded congress abstracts bracket the pooled estimate rather than "
            "contradicting it: 7 of 26 partner-assigned cases in Valencia, 1 of 9 in "
            "Pilsen/Znojmo. A THIRD prevalence series is excluded and does NOT bracket it: "
            "sjogren-2003-prevalence is 3/9 = 33.3 % TAF15 at patient level, above every pooled "
            "cohort, held out under POLICY-evidence.md "
            "s2.1(3). Pooling it would give 31/163 = 19.0 % with a per-cohort range of "
            "15.8-33.3 %, so this exclusion moves the estimate AWAY from the highest published "
            "shares rather than toward them."
        ),
        "outlier_note": (
            "Agaram 2014 is the high outlier of the four pooled series. Its cohort is 26 "
            "consecutive cases at a "
            "tertiary sarcoma referral centre, i.e. exactly the setting where morphologically "
            "unusual, high-grade, hard-to-classify tumours -- which is what TAF15::NR4A3 tends to "
            "be -- are over-represented. "
            "WHAT THIS NOTE NO LONGER SAYS, AND WHY (manuscript Appendix A30, 2026-08-27): it "
            "asserted that Agaram is 'the source most often quoted for TAF15 frequency (27%)' and "
            "that the pooled estimate is 'materially lower than the figure the field repeats'. NO "
            "SOURCE FOR THAT QUOTING PRACTICE WAS EVER HELD. The two sources in the manuscript's "
            "own reference list that state a general TAF15 share -- Stacchiotti 2020 (PMC7563993, "
            "doi 10.3390/cancers12092703) and Bangerter (PMC9813045, "
            "doi 10.1007/s13577-022-00818-x) -- both give about 20 %, which lies INSIDE this "
            "pooled interval. The pooling is consistent with the cited literature and its "
            "contribution is the interval, not a correction of a point figure."
        ),
        "verdict": (
            "TAF15::NR4A3 is carried by {t}/{n} partner-assigned EMC across four independent "
            "series -- {p}% (95% CI {lo}-{hi}). That is the size of the population any "
            "partner-stratified recommendation would move: large enough for the question to "
            "matter, small enough to explain why every series' TAF15 arm is 2-10 patients."
        ).format(
            t=taf_n,
            n=tot,
            p=wilson(taf_n, tot)["percent"],
            lo=wilson(taf_n, tot)["ci95_lo_percent"],
            hi=wilson(taf_n, tot)["ci95_hi_percent"],
        ),
    }

    # ⛔ DERIVED, NEVER TYPED (CLAUDE.md rule 1.1). Whether the literature's stated share falls
    # inside this pooling's own interval IS Appendix A30's finding, so it is computed from the
    # interval the generator just wrote rather than asserted beside it. If a count changes and the
    # interval moves off the cited figure, this flips here and the prose bound to it goes red --
    # which is the whole reason the comparator was moved into the artifact.
    _ext = analysis_prev["external_reported_share"]
    _w = wilson(taf_n, tot)
    _ext["pooled_percent_for_comparison"] = _w["percent"]
    _ext["pooled_ci95_for_comparison"] = [_w["ci95_lo_percent"], _w["ci95_hi_percent"]]
    _ext["falls_inside_pooled_interval"] = bool(
        _w["ci95_lo_percent"] <= _ext["percent_approx"] <= _w["ci95_hi_percent"]
    )
    _ext["reading"] = (
        "The share the cited literature states falls {inside} the interval this pooling computes, "
        "so the pooling {verb} it."
    ).format(
        inside="INSIDE" if _ext["falls_inside_pooled_interval"] else "OUTSIDE",
        verb="is consistent with" if _ext["falls_inside_pooled_interval"] else "disagrees with",
    )

    # The ten strata s2.5 names: both TKI-response contrasts and all three outcome contrasts.
    _extent = _stratum_extent(
        analysis_tki["primary_non_overlapping"]["contrast"],
        analysis_tki["secondary_assume_independent"]["contrast"],
        analysis_outcome["disease_specific_death"],
        analysis_outcome["local_recurrence"],
        analysis_outcome["distant_metastasis_after_presentation"],
    )

    # Falsifier #5's threshold, derived from the pooled death contrast rather than asserted in prose.
    _dod = analysis_outcome["disease_specific_death"]
    _dod_taf = _dod["taf15_arm"]
    dod_threshold = zero_death_patients_to_reconcile(_dod_taf, _dod["comparator_arm"])

    doc = {
        "_schema": "emc-fusion-partner-pooling/1",
        "_generated_by": "research/manuscripts/emc_fusion_partner_pooling.py",
        "_generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "_do_not_hand_edit": (
            "Every number in this file is computed by the generator from the counts in its COHORTS "
            "table. Change a count in the script and regenerate; never edit a number here "
            "(CLAUDE.md rule 1)."
        ),
        "title": "Partner-stratified pooled synthesis of published EMC systemic-therapy and outcome data (EWSR1::NR4A3 vs TAF15::NR4A3)",
        "lane": "research/manuscripts/program/emc-unexplored-treatment-lanes.md s3.2",
        "method": {
            "contract": "systems/POLICY-evidence.md s1-s2 (binding)",
            "estimator": "crude denominator-weighted proportions",
            "interval": "Wilson score, 95%",
            "heterogeneity": "range of per-cohort rates; I-squared deliberately not computed",
            "double_counting": "POLICY-evidence.md s2.3 - mutually exclusive strata within a study; smaller cohort held out where populations may overlap",
            "not_used": (
                "The DerSimonian-Laird random-effects pooler in research/meta/meta-analysis.mjs. "
                "Across the {n} response and outcome strata this synthesis pools, the per-stratum "
                "denominator runs from {dlo} to {dhi} and the event count from {elo} to {ehi}; a "
                "between-study variance is not estimable at that scale, a tau-squared from these "
                "counts would be an artefact, and quoting a random-effects interval would "
                "manufacture precision the data cannot support. \u26a0 Superseded, retained: "
                "'2-19 patients and 0-10 events per stratum' -- true of the TKI-response strata "
                "alone, before Huang 2023's counts were pooled on 2026-08-08 and widened the "
                "outcome denominators past nineteen. This range is now DERIVED from the analyses "
                "on every regeneration (CLAUDE.md rule 1.1) rather than typed, which is what let "
                "the old pair stand here after the manuscript retracted it."
            ).format(**{"n": _extent["n_strata"], "dlo": _extent["denom_lo"],
                        "dhi": _extent["denom_hi"], "elo": _extent["events_lo"],
                        "ehi": _extent["events_hi"]}),
            "significance_testing": "Fisher exact, two-sided, POST-HOC AND DESCRIPTIVE ONLY; no multiplicity correction; no claim rests on it.",
        },
        "citations": CITATIONS,
        "cohorts": COHORTS,
        "analyses": {
            "A_tki_objective_response": analysis_tki,
            "B_outcome_by_partner": analysis_outcome,
            "C_partner_prevalence": analysis_prev,
        },
        "primary_authors_hedge": {
            "quote": "Even in EMCS the fusion-protein is unlikely to be related to sunitinib sensitivity",
            "sourceId": "stacchiotti2012",
            "attribution_correction": (
                "⚠ THE QUOTE IS FROM THE 2012 TWO-CASE REPORT (PMID 23058004), NOT THE 2014 SERIES "
                "(PMID 24703573) IT IS USUALLY ATTRIBUTED TO -- including in this repository's own "
                "lane memo. Verified against the cached full text of both; the 2014 abstract does "
                "not contain it. This matters for what the hedge IS: it was written in 2012, when "
                "the authors had only two EWSR1-positive responders and no TAF15 patient at all, so "
                "it is their PRIOR that the fusion is not the mechanism -- not a retrospective "
                "caveat added once the partner correlation appeared. It is by analogy to alveolar "
                "soft part sarcoma, another translocation sarcoma where sunitinib activity is not "
                "linked to the fusion protein."
            ),
            "reading": (
                "The investigators who reported the correlation read it as a SURROGATE for something "
                "downstream, not as a mechanism. Three later observations are consistent with that "
                "reading and belong beside it: Huang 2023 found the partner's prognostic effect "
                "absorbed by tumour size on multivariable analysis, Paioli 2021 could not reach "
                "significance on it at all, and Bangerter 2022's matched ex vivo pair found drug "
                "response partner-INDEPENDENT for the one drug class it tested. Any paper on this "
                "lane must carry the hedge in its own abstract."
            ),
        },
        "what_could_kill_this": [
            "A single published TAF15::NR4A3 objective response on any antiangiogenic TKI. With a "
            "denominator of 3-5, one response moves the point estimate to 20-33% and the contrast "
            "disappears.",
            "The Lancet Oncol 2019 full text showing that the pazopanib trial's non-TAF15 arm "
            "contains non-EWSR1 partners, or that a TAF15 patient sat outside the evaluable 22.",
            "Confirmation that the sunitinib series' TAF15 patients re-enrolled on the pazopanib "
            "trial, which would collapse the world's TAF15 experience to three patients.",
            "A partner-stratified reanalysis of any registry (SEER, the Japanese national registry, "
            "the US Sarcoma Collaborative) showing no survival separation once size and stage are "
            "adjusted for -- which is the direction Huang 2023 already points.",
            (
                "A THIRD outcome cohort with per-partner event counts in which TAF15 mortality is "
                "not elevated. The pooled crude death contrast now rests on two cohorts whose "
                "TAF15 arms are 7 and 8 patients. ⚠ BUT ONE SUCH COHORT WOULD NOT OVERTURN THIS, "
                "AND SAYING SO IS PART OF THE FALSIFIER: it would take {k} FURTHER TAF15 patients "
                "with no disease-specific deaths at all -- a total TAF15 denominator of {n}, more "
                "than twice the world's pooled experience here -- to bring the pooled point "
                "estimate down to the comparator arm's Wilson upper bound of {hi}%. A third "
                "cohort of 7 or 8 with zero deaths leaves it at {p7}% and {p8}%. Derived by "
                "zero_death_patients_to_reconcile() from the counts in this artifact, not asserted."
            ).format(
                k=dod_threshold["further_zero_death_taf15_patients_required"],
                n=dod_threshold["total_taf15_denominator_required"],
                hi=dod_threshold["comparator_ci95_hi_percent"],
                p7=round(100.0 * _dod_taf["events"] / (_dod_taf["denom"] + 7), 1),
                p8=round(100.0 * _dod_taf["events"] / (_dod_taf["denom"] + 8), 1),
            ),
            "Any size-adjusted partner analysis in which the partner DOES remain independent. That "
            "would overturn the defeater rather than the effect, and it is the single result that "
            "would turn the crude magnitude on this page into a claim about biology instead of a "
            "claim about tumour size.",
        ],
        "resolved_2026_08_08": {
            "_what": (
                "Items that were filed as unreachable and are not any more. Kept as a block rather "
                "than deleted, because 'we could not get it' and 'we got it' are both facts about "
                "the same source and a reader meeting the old sentence elsewhere must be able to "
                "find what replaced it."
            ),
            "huang2023_full_text": {
                "was": "paywalled; carries the per-partner survival event counts that would let this cohort be pooled.",
                "now": (
                    "RETRIEVED, by a human reading the published PDF on 2026-08-08. The blocker "
                    "was never a paywall: Unpaywall and OpenAlex independently designate a free "
                    "publisher-hosted publishedVersion PDF (oa_status bronze, oa_date 2023-03-21), "
                    "and every automated fetch of it returned HTTP 403 behind an anti-bot "
                    "challenge. A BOT BLOCK, NOT A PAYWALL -- the two have different remedies, and "
                    "the remedy for this one was a person with a browser. Table 1's per-partner "
                    "event counts are now in cohorts[huang-2023-outcome].strata and the outcome "
                    "pool has gone from one cohort to two."
                ),
                "evidence": (
                    "literature-cache:literature/emc-partner-events/huang2023_unpaywall.txt and "
                    "huang2023_openalex.txt (both HTTP 200, both is_oa true / oa_status bronze); "
                    "literature-cache:literature/emc-partner-events-r2/_manifest.json "
                    "(huang2023_modpath_pdf 403, huang2023_modpath_fulltext 403, "
                    "huang2023_sciencedirect_pii 403)."
                ),
            },
            "nct02066285_eligibility_text": {
                "was": "not present in the cached ClinicalTrials.gov v2 records (the cached field set omits eligibilityModule); would answer whether prior antiangiogenic therapy was permitted.",
                "now": (
                    "RETRIEVED from two independent registries and it answers the question. "
                    "ClinicalTrials.gov v2 for NCT02066285, Exclusion Criteria, verbatim: "
                    "'Patients who have received previous antiangiogenic agents.' Corroborated on "
                    "the EU Clinical Trials Register under EudraCT 2013-005456-15 (GEIS-32) as "
                    "principal exclusion criterion 3, on a record first entered 2014-02-27 against "
                    "an actual trial start of 2014-06 -- i.e. on a public protocol record BEFORE "
                    "accrual opened. ⚠ NOT ACTED ON IN THIS FILE, deliberately: it bears on "
                    "cohorts[sunitinib-2014].contextReason and on the 3-to-5 denominator range in "
                    "analysis A, and changing a pooling decision is a separate edit from folding "
                    "in an event count. ⚠ AND IT IS THE PROTOCOL'S RULE, NOT A PATIENT-LEVEL "
                    "AUDIT: registries publish eligibility criteria, not enrolment decisions. The "
                    "honest form is 'the trial's own eligibility criterion excludes it', never 'no "
                    "patient appeared in both'."
                ),
                "evidence": (
                    "literature-cache:literature/emc-partner-events/nct02066285_ctgov_v2_full.txt "
                    "(HTTP 200) and literature-cache:literature/emc-partner-events-r3/"
                    "euctr_geis32_es.txt (HTTP 200); narrated in "
                    "research/manuscripts/fusion-partner/partner-event-counts-2026-08-08.md s3."
                ),
            },
        },
        "the_two_questions_this_page_answers_and_only_one_moved": {
            "a_prognosis_by_partner": (
                "MOVED on 2026-08-08. Huang 2023's Table 1 gives per-partner event counts, the "
                "outcome pool is now two non-overlapping cohorts and 73 patients, and a crude "
                "magnitude for disease-specific death exists for the first time -- carrying, "
                "inseparably, the same paper's multivariable result that the partner is NOT an "
                "independent predictor once tumour size is adjusted for. See "
                "analyses.B_outcome_by_partner."
            ),
            "b_treatment_response_by_partner": (
                "⛔ STILL BLOCKED, AND NOT BY ANYTHING HUANG 2023 COULD HAVE SUPPLIED. The "
                "antiangiogenic-TKI question rests on 3 to 5 TAF15::NR4A3 patients with ZERO "
                "reported responses, and a zero-event arm yields no magnitude at any denominator: "
                "the Wilson upper bound on the TAF15 response rate still sits ABOVE the comparator "
                "arm's own point estimate in both analyses. What would unblock it is one further "
                "cohort reporting objective response by partner with integer counts, or the "
                "Lancet Oncol 2019 full text's partner distribution -- neither of which Huang 2023 "
                "contains, because it reports no antiangiogenic therapy at all. "
                "analyses.A_tki_objective_response is unchanged by this integration."
            ),
            "why_this_block_exists": (
                "Because the two are easy to conflate and the conflation would be an over-claim in "
                "the direction the whole page is trying to avoid. A prognostic magnitude is not a "
                "predictive one: knowing that TAF15 patients die more often, crudely and probably "
                "because their tumours are bigger, says nothing about whether they respond to a "
                "drug class."
            ),
        },
        "retrieval_provenance": {
            "network": (
                "The dev sandbox proxy 403s Europe PMC, NCBI and ClinicalTrials.gov on CONNECT "
                "(verified this session: exit 56, HTTP 000). Every source below was read from the "
                "repository's own literature cache on the `literature-cache` branch, fetched by "
                "GitHub Actions runs of .github/workflows/fetch-literature.yml (CLAUDE.md s6)."
            ),
            "the_one_source_not_read_from_the_cache": (
                "⭐ Huang 2023's Table 1 counts were read by a HUMAN from the published PDF on "
                "2026-08-08, not by any fetcher, because the publisher's edge returns HTTP 403 to "
                "CI while designating the same PDF free (citations.huang2023.verification_note). "
                "That provenance is different from every other count on this page and is stated "
                "rather than blurred: it cannot be re-derived by re-running a workflow, and a "
                "future session that re-fetches will get the 403 again and must not read that as "
                "the counts being unavailable. The identity of the paper behind the counts WAS "
                "machine-verified -- citations.huang2023.identity_confirmed."
            ),
            "cache_slugs_used": [
                "literature/emc-partner-events",
                "literature/emc-partner-events-r2",
                "literature/emc-partner-events-r3",
                "literature/emc-clinical-sweep-c3-2026-08-07",
                "literature/emc-clinical-sweep-c4-2026-08-07",
                "literature/emc-clinical-sweep-fulltext-2026-08-07",
                "literature/emc-post-degrader-options",
                "literature/proximity-sweep-2026-08-07",
                "literature/nr4a-ligand-chemistry",
            ],
            "not_retrievable": {
                "Stacchiotti 2019 Lancet Oncol full text (PMID 31331701)": "GENUINELY CLOSED, and re-measured 2026-08-08 rather than assumed: Unpaywall oa_status closed with zero OA locations, OpenAlex any_repository_has_fulltext false, publisher full text (stacchiotti2019_lancet_fulltext) HTTP 403. Of the repository handles OpenAIRE and OpenAlex list for this paper and Stacchiotti 2014 TOGETHER -- the measurement does not split them per paper -- IRIS Bologna (11585/779084, 11585/393895), Ferrara (11392/2495557) and Padova (11577/3243739) fetch metadata-only, while DIGITAL.CSIC (10261/214284) is UNREAD rather than empty: an Anubis proof-of-work anti-scraper challenge no stdlib fetcher can clear, i.e. a bot block of the Appendix A8 kind and not evidence of closure. Measurement: partner-event-counts-2026-08-08.md s2.3. The Europe PMC isOpenAccess N / inEPMC N flags describe Europe PMC holdings only and are no longer the basis of this label (s8). Carries the trial's full fusion distribution and prior-therapy table, i.e. the two facts that would close the overlap question and the non-TAF15 composition question.",
                "Paioli 2021 Ann Surg Oncol full text (PMID 32572850)": "GENUINELY CLOSED, and re-measured 2026-08-08 rather than assumed: Unpaywall `is_oa: false` / `oa_status: closed` with zero OA locations, OpenAlex `any_repository_has_fulltext: false`, and both institutional-repository records it lists (IRIS Bologna 11585/778841, Florence Research 2158/1215233) fetch HTTP 200 and are metadata-only -- Florence states verbatim 'Non ci sono file associati a questo prodotto'. Carries the per-partner relapse and metastasis event counts behind its DFS/DMFS p-values, and would say what the 5 partner-unassigned patients of 67 were. ⚠ ITS ABSTRACT'S AGGREGATE RELAPSE SPLIT IS RETRIEVABLE AND STILL NOT POOLABLE (35/67 relapsed: 9 local recurrence, 26 distant metastasis, 5 with concomitant LR) -- POLICY-evidence.md s2.1 needs counts on BOTH SIDES of the stratification and that total is partner-blind; splitting 35 relapses across the published 50/10 partner ratio would be a back-derived count, which s2.1(2) forbids. Recorded so a future session does not re-fetch it believing it is the missing table.",
                "Stacchiotti 2014 Eur J Cancer full text (PMID 24703573)": "closed; no OA location in any index. The abstract states the qualitative split but not the per-arm denominators.",
            },
        },
    }

    return doc


#: Fields that differ between two correct runs and are therefore excluded from the comparison.
#: ⚠ DELIBERATELY MINIMAL — ONE KEY. Everything else, `_do_not_hand_edit` and `_schema` included,
#: IS compared, because editing those is exactly the drift this guard exists to catch. A volatile
#: list that grows is how a verify mode stops verifying.
_VOLATILE_TOP_LEVEL_KEYS = ("_generated_utc",)


def _comparable(doc: dict) -> dict:
    """`doc` minus the fields that differ between two correct runs. Everything else is compared."""
    return {k: v for k, v in doc.items() if k not in _VOLATILE_TOP_LEVEL_KEYS}


def check() -> int:
    """`0` if the committed artifact re-derives exactly, `1` otherwise. NEVER WRITES.

    ⛔ THE REFERENCE IS BUILT IN MEMORY, NOT WRITTEN TO `OUT`. The defect this replaces accepted
    `--check`, regenerated the file, and exited 0 -- a comparison of the generator against itself,
    which cannot fail and produces no symptom when it is wrong. `build()` is pure over this
    module's COHORTS/CITATIONS tables, so the reference never touches the file being judged.
    """
    if not os.path.exists(OUT):
        print("FAIL: %s does not exist -- run the generator" % OUT, file=sys.stderr)
        return 1
    try:
        with open(OUT, encoding="utf-8") as fh:
            committed = json.load(fh)
    except (OSError, ValueError) as exc:
        print("FAIL: %s is not readable JSON (%s)" % (OUT, exc), file=sys.stderr)
        return 1

    built = build()
    c, b = _comparable(committed), _comparable(built)
    if c == b:
        print("emc_fusion_partner_pooling --check: OK "
              "(committed artifact reproduces from the generator's counts)")
        return 0

    # ⛔ A REFUSAL THAT CANNOT SAY WHAT IT REFUSED SENDS THE READER TO A 2,000-LINE DIFF. Name the
    # top-level sections that disagree -- a pooled clinical proportion drifting deserves a pointer.
    differing = sorted(set(c) ^ set(b)) + sorted(k for k in set(c) & set(b) if c[k] != b[k])
    print("FAIL: %s differs from a fresh derivation. Regenerate it "
          "(python3 research/manuscripts/emc_fusion_partner_pooling.py)." % OUT, file=sys.stderr)
    print("  differing top-level keys: %s" % ", ".join(differing), file=sys.stderr)
    return 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="Partner-stratified pooled synthesis of published EMC systemic-therapy and "
                    "outcome data (EWSR1::NR4A3 vs TAF15::NR4A3)."
    )
    ap.add_argument("--check", action="store_true",
                    help="re-derive in memory and compare against the committed artifact; "
                         "exit 1 on any difference. Writes nothing.")
    args = ap.parse_args(argv)

    if args.check:
        return check()

    doc = build()
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, indent=2, ensure_ascii=True)
        fh.write("\n")
    a = doc["analyses"]
    print("wrote", OUT)
    for key in ("A_tki_objective_response", "B_outcome_by_partner", "C_partner_prevalence"):
        print("\n==", key)
        print(json.dumps(a[key], indent=1)[:2400])
    return 0


if __name__ == "__main__":
    # ⛔ `sys.exit(main())`, never a bare `main()`. A verify mode whose failure cannot reach the
    # shell's exit status is not wired into anything, however correct its comparison is.
    sys.exit(main())
