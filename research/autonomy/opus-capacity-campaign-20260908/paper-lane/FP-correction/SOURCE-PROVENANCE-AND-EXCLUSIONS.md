# FP correction — authentic source provenance and exclusions

2026-09-08. ⛔ **No source retrieval was performed.** Every check below is ordinary existing-byte intake from
this repository's own retained objects (`origin/literature-cache`) or from the verified review capsule. No
blocked publisher route was retried, and no reconstructed original was created.

## 1 · Held, and now source-verified — the one hold that CLOSED

**Lenz 2023, PMID 36563884** (F8). The authentic Europe PMC record carrying the **primary abstract** is
retained on the `literature-cache` branch in
`literature/emc-partner-events/epmc_search_taf15_fulltext.txt`
(blob `bfd551d768e80ae7c26863f71768c325d575f3c8`, 553,043 bytes, sha256
`158c5005e6493416d0620d4ab49975b67b0d9182e9fcc2d0c34a4aa9358d35ae`). The same record occurs in several other
retained sweep files; this one is in the FP's own `emc-partner-events` directory.

Verbatim, from that record: *"Molecular testing was successfully performed in 12/17 cases"*, and *"Molecular
assays revealed 8 EWSR1::NR4A3 positive tumors (67%), 2 TAF15::NR4A3 positive tumors (17%), 1 TCF12::NR4A3
positive tumor (8%) and 1 NR4A3 positive tumor (8%) in which no other gene alteration was identified."*

Those are exactly the integers the prevalence pool uses. **The final review's source hold on this input is
closed against that record**, and `28/154 = 18.2 % (12.9–25.0)` is retained rather than removed. The
bibliographic repair of this citation was already closed separately and is unaffected. The extracted record is
preserved at `source-intake/lenz-2023-primary-abstract.json` (sha256
`682f8d34904b967cbe2e458ec995b093e667e643c2140481b7e535b64e59f52d`).

⚠ The abstract also corrects that series' ascertainment flow: **17 in the series, 12 characterised, 11 with a
named partner, and five cases with no successful molecular result** — five cases an earlier version of §3.5
lost by describing the residue as one.

## 2 · Held, and NOT verifiable — the hold that stands, so the inputs were removed

**Huang 2023, PMID 36948401** (F12). Re-inspected on 2026-09-08:

| retained object | what it actually contains |
|---|---|
| `literature/emc-partner-events/huang2023_epmc_core.txt` | Europe PMC core record with the **abstract**. Verified to state the 58-case cohort, 46/9/2/1 partner counts, the 78 % size association with P = .025, the five named univariate factors, and that only size > 10 cm (P = .004) and metastasis at presentation (P = .032) remained prognostically independent |
| `literature/emc-partner-events-r2/huang2023_modpath_fulltext.txt` | 235 bytes. `HTTP: 403`, body *"Just a moment..."* — an anti-bot interstitial |
| `literature/emc-partner-events-r2/huang2023_modpath_pdf.txt` | 226 bytes. `HTTP: 403`, same interstitial |
| `literature/emc-partner-events-r2/huang2023_sciencedirect_pii.txt` | 874 bytes. `HTTP: 403`, ScienceDirect error page |

**No authentic Table 1 or full text exists in the inspected holdings.** A manifest of a denied route is not the
denied document, and the frozen manuscript's narrative of a human PDF read is not a retained original.

**Removed from the active synthesis** (quarantined verbatim in
`cohorts[huang-2023-outcome].withdrawn_2026_09_08`, not deleted): the per-partner outcome strata (NED/AWD/DOD,
local recurrence, and the three metastasis cells for both arms); the 53-followed and 42 EWSR1 / 8 TAF15
denominators; HR 30.60 and HR 8.14; the mean-size comparison 13.7 ± 6.2 vs 7.3 ± 4.7 cm and P = .024; the
12/46 EWSR1 size cell and its recorded printed-percentage inconsistency; the three published table p-values
(0.047, 0.728, 1.000); and the Discussion sentence quoted as the authors' own explanation.

**Retained at abstract scope**: the cohort prevalence counts (which stay in the four-series prevalence pool)
and the qualitative report of the model result, stated with what it does and does not establish.

⚠ **This is scoped absence, not a finding that the published counts are false**, and it reopens on an
authentic original or an authoritative source obtained through a separately authorised ordinary route,
verified cell by cell. ⛔ A contemporaneous extraction record must not be reconstructed from the quarantined
values and labelled an original.

## 3 · Sources re-read from the capsule and applied

| source | retained copy | what it settled here |
|---|---|---|
| Davis 2017 | `PMC5400622.txt`:14 | ⭐ All eight sunitinib clinical-benefit patients (6 PR + 2 SD) reported as *EWSR1-NR4A3*. Withdrew this paper's false "no held source states the SD patients' partner" (F4) |
| Sunitinib 2014 | `ft_sunitinib2014_ejc.txt` | An **abstract**, not a full text — corrected the §3.8 verification claim (F11) |
| Sunitinib 2012 | `PMC3534218.txt` | Retained **full text**; carries the 2012 hedge, which the attribution now rests on alone (F11) |
| Pazopanib primary | `emc_pazopanib_pubmed.txt`:661–669 | **26 treated → 23 mITT → 22 evaluable**, four responses, prior-six-month RECIST criterion (F4) |
| NCT02066285 | `nct02066285_ctgov_v2_full.txt`, `eligibilityModule` | Excludes previous antiangiogenic agents — applied to the overlap rationale as protocol evidence, not an audit (F5) |
| Agaram 2014 | `emc_fusion_freq_agaram2014_pmc.txt` | The one source-verified outcome cohort; case 3 is **dead of unknown cause**, kept distinct (F3) |
| Sjögren 2003 | capsule batch 2 record | **0/3 TAF15 vs 1/5 EWSR1** recorded tumour-related deaths, **nine patients**, cases 6-I/6-II one patient (F6) |
| Suemitsu 2025 | capsule batch 2 record | 18 patients, 14/2/1/1, no significant OS-by-subtype association (F6) |
| Brenca 2019, Bangerter 2022 | capsule batch 2 records | Model-context bounds; the 40-drug inventory is not in the retained text (F9) |
| GSE28866 | `research/modalities/geo-gse28866-brunner-series.json` line 5445 (`series_record.overall_design`, sha256 `c9440ea5…`) and `gse28866-tumour-vs-normal.json` lines 194–241 (sha256 `ac0a17bd…`) | Depth/sample-mean normalisation **then square root**; **10 fetal / 17 adult** normal libraries. SEMA3C ratios stated at deposited-score scale; no inverse transform (F9) |

## 4 · What was NOT done

⛔ No new literature search, no database query, no publisher route retried, no reconstructed original created,
no patient-level reconstruction beyond published retained records, no new model, no random-effects or CMH
selection, no hypothesis-search sweep, and no shared-graph edit.
