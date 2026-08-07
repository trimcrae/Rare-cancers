#!/usr/bin/env python3
"""Partner-stratified pooled synthesis of published EMC systemic-therapy and outcome data.

WHY THIS EXISTS
---------------
`research/manuscripts/emc-unexplored-treatment-lanes.md` s3.2 ranks "fusion-variant
stratification (EWSR1 vs TAF15)" #2 of twelve unexplored lanes and calls it "the cheapest
paper on the board": four independent lines converge on the NR4A3 5' partner as a
treatment-relevant biomarker, and **nobody has pooled them**. This file does the pooling,
and it is the ONE HOME of every number in that synthesis (CLAUDE.md rule 1).

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
is the OTHER method in this repo and is deliberately NOT used: every stratum here has 2-19
patients and 0-10 events, where a between-study variance estimate is not estimable.

Fisher's exact p-values are reported as a clearly-labelled **post-hoc descriptive**
statistic. No published report performed this test; it is not a prespecified analysis and
is not used to license any claim.

Stdlib only. Run:  python3 research/manuscripts/emc_fusion_partner_pooling.py
Writes:            research/manuscripts/emc-fusion-partner-pooling.json
"""

from __future__ import annotations

import json
import math
import os
from datetime import datetime, timezone

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(REPO, "research", "manuscripts", "emc-fusion-partner-pooling.json")

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
        "authors": "Huang SC, Lee JC, Hsu YC, Tsai JW, Kao YC, Hsieh TH, et al.",
        "journal": "Mod Pathol",
        "year": 2023,
        "pmid": "36948401",
        "doi": "10.1016/j.modpat.2023.100161",
        "url": "https://doi.org/10.1016/j.modpat.2023.100161",
        "license": "publisher (abstract via Europe PMC)",
        "openAccess": False,
        "design": "multi-institution molecular case series (Taiwan)",
        "n": 58,
        "population": "58 FISH-confirmed EMC, Taiwanese institutions",
        "accessed": "2026-08-07",
        "verified": True,
        "verification_note": (
            "Abstract gives the fusion distribution as explicit integers (46/9/2/1) and states that "
            "TAF15::NR4A3 'portended shorter univariate disease-specific survival, whereas only size "
            ">10 cm (P = .004) and metastasis at presentation (P = .032) remained prognostically "
            "independent'. NO EVENT COUNTS by partner are in the abstract and the full text is "
            "paywalled, so this cohort contributes to the PREVALENCE pool and to nothing else. "
            "NOTE: `research/data/emc-clinical-registry.json` carries this same paper under the "
            "citation id `warmke2023` with short label 'Warmke 2023', which does not match its "
            "author list; the identifier, title, DOI and PMID in that entry are correct."
        ),
    },
    "lenz2023": {
        "short": "Lenz 2023",
        "type": "journal-article",
        "title": "Extraskeletal myxoid chondrosarcoma: A study of 17 cases focusing on the diagnostic utility of INSM1 expression and presenting rare morphological variants associated with non-EWSR1::NR4A3 fusions.",
        "authors": "Lenz J, Klubickova N, Ptakova N, Hajkova V, Grossmann P, Steiner P, et al.",
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
        "authors": "Paioli A, Stacchiotti S, Campanacci D, Palmerini E, Frezza AM, Longhi A, Radaelli S, Donati DM, Beltrami G, Bianchi G, et al.",
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
            "The only published EMC cohort that reports outcome EVENT COUNTS by NR4A3 partner. "
            "'Pooling' it is therefore a single-cohort Wilson interval, stated as such rather than "
            "dressed as a meta-analysis."
        ),
        "follow_up_warning": (
            "The two arms have very different mean follow-up (43.3 vs 21.7 months) and these are "
            "crude during-follow-up proportions with no censoring (POLICY-evidence.md s2.4). The bias "
            "runs AGAINST the TAF15 arm accruing events, so the death excess is observed despite "
            "shorter observation, while the recurrence comparison is confounded in the direction "
            "that produces the reversal reported below."
        ),
    },
    {
        "id": "huang-2023-outcome",
        "endpoint": "outcome_by_partner",
        "label": "58 FISH-confirmed EMC, Taiwan (survival analysis)",
        "n_assessable": 58,
        "sourceId": "huang2023",
        "provenance": "primary",
        "pool": False,
        "contextReason": "counts-not-reported",
        "context_note": (
            "Reports that TAF15::NR4A3 portended shorter disease-specific survival on univariate "
            "analysis but did NOT remain independent on multivariable analysis -- only size >10 cm "
            "(P = .004) and metastasis at presentation (P = .032) did, and TAF15::NR4A3 was itself "
            "significantly associated with size >10 cm (78%, P = .025). No {events, denom} are given "
            "in any accessible source, so POLICY-evidence.md s2.1(2) bars it from the pool. This is "
            "the single most important context row on this page: the largest series to test the "
            "partner as a prognostic factor found its effect explained by tumour size."
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
        "context_note": (
            "THE THIRD INDEPENDENT TEST OF THE PARTNER AS A PROGNOSTIC FACTOR, AND IT IS NEGATIVE "
            "AT THE CONVENTIONAL THRESHOLD. NR4A3-EWS showed only a TREND toward better "
            "disease-free survival (p = 0.08) and distant-metastasis-free survival (p = 0.09) "
            "versus NR4A3-TAF15, while primary tumour SIZE was significantly related to DMFS "
            "(p = 0.004) -- the same pattern Huang 2023 found. No per-partner event counts are "
            "published, so POLICY-evidence.md s2.1(2) bars it from the pool; its prevalence counts "
            "are pooled separately below."
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


def main() -> dict:
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
            "Zero of every TAF15::NR4A3 patient ever treated with an antiangiogenic TKI in a "
            "published report responded -- and that is {lo_n} to {hi_n} patients in total. The 95% "
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
    ag = by_id["agaram-2014-outcome"]["strata"]
    ews, taf = ag["EWSR1::NR4A3"], ag["TAF15::NR4A3"]

    def arm(key: str, s: dict) -> dict:
        return wilson(s[key]["events"], s[key]["denom"])

    analysis_outcome = {
        "question": "Does the NR4A3 5' fusion partner predict disease-specific death, recurrence or metastasis?",
        "cohorts_identified": 3,
        "cohorts_pooled": 1,
        "cohorts_excluded": {
            "huang-2023-outcome": "counts-not-reported (POLICY-evidence.md s2.1)",
            "paioli-2021-outcome": "counts-not-reported (POLICY-evidence.md s2.1)",
        },
        "disease_specific_death": contrast(
            "dod_agaram2014",
            arm("disease_specific_death", taf),
            arm("disease_specific_death", ews),
            "Crude during-follow-up proportions, mixed follow-up, no censoring (POLICY-evidence.md s2.4).",
        ),
        "local_recurrence": contrast(
            "lr_agaram2014",
            arm("local_recurrence", taf),
            arm("local_recurrence", ews),
            "Same cohort, same caveats.",
        ),
        "distant_recurrence": contrast(
            "dr_agaram2014",
            arm("distant_recurrence", taf),
            arm("distant_recurrence", ews),
            "Same cohort, same caveats.",
        ),
        "counter_signal": (
            "THE DIRECTION REVERSES FOR METASTASIS. In the only cohort that reports events by "
            "partner, distant recurrence is {de}/{dn} ({dp}%) in EWSR1::NR4A3 and {te}/{tn} "
            "({tp}%) in TAF15::NR4A3 -- the opposite of the narrative repeated across the review "
            "literature that TAF15 tumours are the metastasising ones (e.g. PMC12398172, "
            "PMC12376927, PMC7563993, PMC9131214, all asserting lower metastasis or better "
            "metastasis-free survival with EWSR1). The TAF15 arm's mean follow-up is about half "
            "the EWSR1 arm's ({tf} vs "
            "{ef} months), which is enough to produce this on its own; but the same truncation "
            "makes the DEATH excess harder, not easier, to observe. No published source states "
            "this reversal. The one cohort that examined metastasis by partner as a "
            "TIME-TO-EVENT endpoint (Paioli 2021, n = 67) trends the other way and does not reach "
            "significance: DMFS p = 0.09 favouring NR4A3-EWS, in the same analysis where tumour "
            "size reaches p = 0.004. Crude proportions and DMFS are different estimands and the "
            "two readings are not in contradiction -- but neither of them establishes the "
            "metastasis claim the reviews make."
        ).format(
            de=ews["distant_recurrence"]["events"],
            dn=ews["distant_recurrence"]["denom"],
            dp=arm("distant_recurrence", ews)["percent"],
            te=taf["distant_recurrence"]["events"],
            tn=taf["distant_recurrence"]["denom"],
            tp=arm("distant_recurrence", taf)["percent"],
            tf=taf["mean_followup_months"],
            ef=ews["mean_followup_months"],
        ),
        "verdict": (
            "One cohort, {n} patients with an assigned EWSR1 or TAF15 partner and follow-up on all "
            "of them. Disease-specific death {te}/{tn} ({tp}%, 95% CI {tlo}-{thi}) with "
            "TAF15::NR4A3 versus {ee}/{en} ({ep}%, 95% CI {elo}-{ehi}) with EWSR1::NR4A3; post-hoc "
            "Fisher exact two-sided p = {p}. THE TWO LARGER SERIES THAT TESTED THE SAME QUESTION "
            "BOTH LAND SHORT OF SIGNIFICANCE ONCE SIZE IS IN THE MODEL, and neither can be pooled "
            "because neither publishes event counts: Huang 2023 (n = 58) found the partner "
            "significant on univariate but not independent of tumour size on multivariable "
            "analysis, and Paioli 2021 (n = 67) reports only a trend (DFS p = 0.08, DMFS p = 0.09) "
            "in an analysis where size reaches p = 0.004. Three cohorts, one direction, no "
            "cohort-level significance surviving adjustment."
        ).format(
            n=ews["disease_specific_death"]["denom"] + taf["disease_specific_death"]["denom"],
            te=taf["disease_specific_death"]["events"],
            tn=taf["disease_specific_death"]["denom"],
            tp=arm("disease_specific_death", taf)["percent"],
            tlo=arm("disease_specific_death", taf)["ci95_lo_percent"],
            thi=arm("disease_specific_death", taf)["ci95_hi_percent"],
            ee=ews["disease_specific_death"]["events"],
            en=ews["disease_specific_death"]["denom"],
            ep=arm("disease_specific_death", ews)["percent"],
            elo=arm("disease_specific_death", ews)["ci95_lo_percent"],
            ehi=arm("disease_specific_death", ews)["ci95_hi_percent"],
            p=round(
                fisher_exact_two_sided(
                    taf["disease_specific_death"]["events"],
                    taf["disease_specific_death"]["denom"] - taf["disease_specific_death"]["events"],
                    ews["disease_specific_death"]["events"],
                    ews["disease_specific_death"]["denom"] - ews["disease_specific_death"]["events"],
                ),
                3,
            ),
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
        },
        "non_overlap_argument": (
            "Four geographically and institutionally distinct series -- MSKCC (USA), Taiwanese "
            "institutions, Czech Republic, Italian Sarcoma Group -- with no shared authors between "
            "them and no shared referral network."
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
        "context_range_note": (
            "The two excluded congress abstracts bracket the pooled estimate rather than "
            "contradicting it: 7 of 26 partner-assigned cases in Valencia, 1 of 9 in "
            "Pilsen/Znojmo."
        ),
        "outlier_note": (
            "Agaram 2014 is the high outlier of the four pooled series and is also the source most "
            "often quoted for TAF15 frequency ('27%'). Its cohort is 26 consecutive cases at a "
            "tertiary sarcoma referral centre, i.e. exactly the setting where morphologically "
            "unusual, high-grade, hard-to-classify tumours -- which is what TAF15::NR4A3 tends to "
            "be -- are over-represented. The pooled estimate is materially lower than the figure "
            "the field repeats."
        ),
        "verdict": (
            "TAF15::NR4A3 is carried by {t}/{n} partner-assigned EMC across four independent "
            "series -- {p}% (95% CI {lo}-{hi}). That is the size of the population any "
            "partner-stratified recommendation would move: large enough for the question to "
            "matter, small enough to explain why every series' TAF15 arm is 2-9 patients."
        ).format(
            t=taf_n,
            n=tot,
            p=wilson(taf_n, tot)["percent"],
            lo=wilson(taf_n, tot)["ci95_lo_percent"],
            hi=wilson(taf_n, tot)["ci95_hi_percent"],
        ),
    }

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
        "lane": "research/manuscripts/emc-unexplored-treatment-lanes.md s3.2",
        "method": {
            "contract": "systems/POLICY-evidence.md s1-s2 (binding)",
            "estimator": "crude denominator-weighted proportions",
            "interval": "Wilson score, 95%",
            "heterogeneity": "range of per-cohort rates; I-squared deliberately not computed",
            "double_counting": "POLICY-evidence.md s2.3 - mutually exclusive strata within a study; smaller cohort held out where populations may overlap",
            "not_used": (
                "The DerSimonian-Laird random-effects pooler in research/meta/meta-analysis.mjs. "
                "With 2-19 patients and 0-10 events per stratum, a between-study variance is not "
                "estimable and quoting one would manufacture precision."
            ),
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
        ],
        "retrieval_provenance": {
            "network": (
                "The dev sandbox proxy 403s Europe PMC, NCBI and ClinicalTrials.gov on CONNECT "
                "(verified this session: exit 56, HTTP 000). Every source below was read from the "
                "repository's own literature cache on the `literature-cache` branch, fetched by "
                "GitHub Actions runs of .github/workflows/fetch-literature.yml (CLAUDE.md s6)."
            ),
            "cache_slugs_used": [
                "literature/emc-clinical-sweep-c3-2026-08-07",
                "literature/emc-clinical-sweep-c4-2026-08-07",
                "literature/emc-clinical-sweep-fulltext-2026-08-07",
                "literature/emc-post-degrader-options",
                "literature/proximity-sweep-2026-08-07",
                "literature/nr4a-ligand-chemistry",
            ],
            "not_retrievable": {
                "Stacchiotti 2019 Lancet Oncol full text (PMID 31331701)": "paywalled; isOpenAccess N / inEPMC N in the Europe PMC core record. Carries the trial's full fusion distribution and prior-therapy table, i.e. the two facts that would close the overlap question and the non-TAF15 composition question.",
                "Huang 2023 Mod Pathol full text (PMID 36948401)": "paywalled; carries the per-partner survival event counts that would let this cohort be pooled.",
                "Paioli 2021 Ann Surg Oncol full text (PMID 32572850)": "paywalled (isOpenAccess N / inEPMC N); carries the per-partner relapse and metastasis event counts behind its DFS/DMFS p-values, and would say what the 5 partner-unassigned patients of 67 were.",
                "Stacchiotti 2014 Eur J Cancer full text (PMID 24703573)": "paywalled; abstract states the qualitative split but not the per-arm denominators.",
                "NCT02066285 eligibility text": "not present in the cached ClinicalTrials.gov v2 records (the cached field set omits eligibilityModule); would answer whether prior antiangiogenic therapy was permitted.",
            },
        },
    }

    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, indent=2, ensure_ascii=True)
        fh.write("\n")
    return doc


if __name__ == "__main__":
    d = main()
    a = d["analyses"]
    print("wrote", OUT)
    for key in ("A_tki_objective_response", "B_outcome_by_partner", "C_partner_prevalence"):
        print("\n==", key)
        print(json.dumps(a[key], indent=1)[:2400])
