# D1 — HF-SMOKING source-evidence packet — conclusions kept beside raw evidence
Worker D1, campaign OPUS-CAPACITY-CAMPAIGN-20260908. Retrieval date 2026-09-08 (UTC).
Checkout /home/user/Rare-cancers @ b913719f548c4009711db0bada8f1d9a035567d9.
Route: PubMed MCP connector only (mcp__PubMed__get_article_metadata, mcp__PubMed__get_full_text_article).
No NCBI WebFetch attempted (S7 block respected). No repo write, no git op.

## PMID 41300991 — RESOLVES, SUPPORTS (abstract + full text), one internal CI discrepancy
Lee JM et al. "Impact of Quitting Smoking at Diagnosis on Overall Survival in Lung Cancer Patients:
A Comprehensive Meta-Analysis." Cancers 2025;17(22):3623. PMC12651382. doi 10.3390/cancers17223623.
- Abstract (original, via PubMed metadata): "Quitting smoking at diagnosis was associated with a 26%
  reduction in mortality risk (adjusted HR [aHR] 0.74, 95% CI 0.68-0.81)." -> EXACT match to the stored
  `verbatim` string and to stored HR 0.74 / CI [0.68,0.81].
- Design/population confirmed in full text: 25 cohort studies, 17,584 patients, no RCTs eligible,
  RoBANS 2 appraisal, searched September 2024. Endpoint overall survival. All as stored.
- DISCREPANCY INSIDE THE SOURCE: full-text Results states "(aHR 0.74, 95% CI 0.67-0.81)" — lower CI
  bound 0.67, not the abstract's 0.68. Stored row follows the abstract. Stored RRR band [0.19,0.32]
  = 1 - abstract CI; using the Results CI it would be [0.19,0.33].
- Qualifiers observed in full text, NOT carried by the stored row:
  benefit evident only in early-stage disease; self-reported cessation aHR 0.75 (0.68-0.82) but
  biochemically confirmed cessation aHR 0.42 (0.11-1.62), non-significant (3 studies);
  publication-bias trim-and-fill adjusted pooled aHR 0.80 (0.68-0.93);
  low-risk-of-bias sensitivity aHR 0.70 (0.59-0.84).

## PMID 42340948 — RESOLVES, SUPPORTS ITS OWN NUMBERS (abstract + full-text table)
Lee B, Im S, Won S. "Refined obesity, smoking exposure, and lipid metrics in mortality risk assessment:
a nationwide cohort analysis." PLoS One 2026;21(6):e0348128. PMC13293439. doi 10.1371/journal.pone.0348128.
- Abstract: "A pack-year to age ratio >=1 was significantly associated with an increased risk of
  mortality (AHR = 1.65, 95% CI: 1.51-1.81)." Full-text results table row: "Smoking packyear/Age ratio
  ... >=1  1.65 (1.51-1.81)***  1.31 (0.79-2.17)" (second column = KNHANES external validation,
  NOT significant). 659,494 NHIS-NSC participants confirmed in Methods; follow-up 2009-2019 baseline
  to 2021-12-31, ~9.5 y mean.
- Stored note's description is accurate for the figure cited but INCOMPLETE as article identity: the
  paper is a combined obesity + smoking + lipid metrics paper, not a smoking paper.
- It is an EXPOSURE-DOSE association (pack-year/age ratio vs non-smoker), retrospective, no cessation
  arm, no cessation timing. It cannot estimate a cessation effect. Stored status `association_only`
  and the note "not a cessation effect; recorded for direction only" are CORRECT.

## The drift
Both identifiers are real and both support their own stated numbers. The row conflates nothing at the
level of arithmetic: the committed model (emc-host-factor-model.json, HF-SMOKING compartment B) carries
ONLY pmid 41300991 and the [0.19,0.32] RRR; 42340948 is B_corroborating, RRR pinned to zero. But the two
are scientifically non-substitutable: 0.74 is a cessation-vs-continued-smoking effect in lung cancer;
1.65 is a smoking-dose-vs-never-smoker association in a general Korean cohort. 1/1.65 = 0.61 is NOT a
cessation effect and must never be read as one.

## Repository discrepancy found (reported, NOT edited)
research/autonomy/receipts/CYC-0105-e41d184e.json asserts PMIDs "... 41300991, 42340948 ... all present
in emc-host-factor-probe.json". Measured: `grep -c 42340948 research/literature/emc-host-factor-probe.json`
= 0; 41300991 IS present (with PMC12651382 / 10.3390/cancers17223623). The receipt's claim is false for
42340948. This is a provenance-claim error only: absence from the probe is NOT absence from the
literature, and the article was retrieved live today.

## Transfer limits
Neither source is EMC, sarcoma, or any rare-sarcoma population. 41300991 is lung cancer (a smoking-caused
cancer, so its OS mixes cancer and non-cancer death); 42340948 is a Korean general population. Neither
establishes any clinical benefit in EMC. They transfer at most as a direction and an order of magnitude
for compartment B (competing, non-EMC death). No wet lab; no EMC patient records smoking.
