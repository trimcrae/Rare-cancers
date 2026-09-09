---
id: DOC-PORTFOLIO-INVESTIGATION-LOCOREGIONAL-3-20260909
title: "LOCOREGIONAL-3 — bishop2019 holds at source; the multicenter 1/10 vs 7/17 primary is identified on descriptor but unreadable, so k stays 2"
level: L4
kind: investigation
status: complete
date: 2026-09-09
last_verified: 2026-09-09
lane: LOCOREGIONAL-3
continues: LOCOREGIONAL-2
proposal: FOLLOWTHROUGH-DISCOVERY P6 (rank 6)
campaign: OPUS-CAPACITY-CAMPAIGN-20260908
---

# LOCOREGIONAL-3 — the third series was attempted and is not admitted

⛔ **No claim is made or supported here that radiotherapy does, or does not, improve local
control in extraskeletal myxoid chondrosarcoma.** No efficacy, safety, selectivity,
therapeutic-window, prognosis or treatment-recommendation claim; no patient-specific advice.
This is a **curation ledger**, not a treatment comparison. **RT-RT-INTENSIFY stays REFUTED** and
**RT-METASTASECTOMY stays DO-NOT-WRITE**; nothing below reopens either.

⛔ **Direction of evidence, carried forward unsoftened.** LOCOREGIONAL-2 moved k from 1 to 2 and
that move **weakened** the radiotherapy case: the larger series reports **8.3% (2/24) vs 12.7%
(14/110), p = 0.74**, with the measured confounding running **against** radiotherapy (41.7% vs
18.2% R1/R2 margins in the irradiated arm). **This lane adds no series.** Nothing here is framed
as strengthening a case the second series weakened, and re-verifying bishop2019 does not do so —
bishop2019 was already in the ledger at k = 1.

## 1 · The question

> Which primary reports the **1/10 vs 7/17** multicenter local-recurrence split that
> masunaga2025 quotes in its Discussion, and do **bishop2019's 1/33 and 4/8** hold at source?

## 2 · The answer — split

| target | outcome |
|---|---|
| bishop2019 `1/33` and `4/8` | ✅ **HOLD AT SOURCE.** Transcription upgraded second-hand → **first-hand.** |
| the 1/10 vs 7/17 multicenter primary | ⚠️ **Identified on descriptor only, and unreadable.** **NOT admitted. k stays 2.** |

## 3 · The gate came first, and it is green

Per P6, `--check` had to re-derive the k = 2 rows **byte for byte** before any new row could be
added, and the four internal arithmetic consistency checks had to stay ✅.

* `checks/01-gate-k2-check/` — `python3 ../LOCOREGIONAL-2/rt_contrast_ledger_k2.py --check` →
  `CHECK MATCH: re-derived artifact is byte-identical to the committed one.` **exit 0.**
* `checks/14-k3-idempotence-check/` — this lane's builder re-derives the three carried k = 2
  blocks and compares canonical bytes against the committed k = 2 file:
  `arm_level_event_ledger` 2041 B ✅, `per_series_2x2_reported_as_sizes` 864 B ✅,
  `crude_pooled_per_arm_proportions` 1504 B ✅.
* Four arithmetic checks recomputed from **printed integers**: 2 + 14 = 16 ✅ · 24 + 110 = 134 ✅ ·
  8.3% / 12.7% / 11.9% reproduce ✅ · 1 + 4 = 5 and 33 + 8 = 41 ✅ · **all_green: true.**

The builder **exits non-zero and writes nothing** if either gate fails. No k = 2 number was
recomputed, restated or altered by this lane.

## 4 · bishop2019 at source — verbatim, and it holds

According to PubMed, from the open-access full text of Bishop AJ, Bird JE, Conley AP, et al.,
*"Extraskeletal Myxoid Chondrosarcomas: Combined Modality Therapy with both Radiation and Surgery
Improves Local Control"*, Am J Clin Oncol 2019;42(10):744–748 — PMCID **PMC7771031**, PMID
**31436747**, [DOI](https://doi.org/10.1097/COC.0000000000000590) — retrieved 2026-09-09 through
the PubMed/PMC MCP route (`checks/03-…`, `checks/05-…`):

> **"The majority of patients (n=33, 80%) received combined modality local therapy with both
> surgery and RT, whereas 8 patients received surgery alone (20%)."**

> **"There were 5 patients (12%) with local relapse at a median time of 75 months (range 13–176
> months). Four of those patients underwent surgery alone. The median time to local relapse
> occurred earlier in patients receiving surgery alone compared to the one patient who received
> CMT (61 months vs. 143 months)."**

**How each integer is known.** 33 and 8 are printed integers. 4 is printed as the word *"Four"*.
5 and 41 are printed integers. The surgery + RT event count **1** is printed **twice and
independently**: as 5 − 4 on printed integers, and as the words *"the one patient who received
CMT."* **No count is reconstructed** from a hazard ratio, a percentage, a p-value, a confidence
interval or a Kaplan–Meier curve.

**Corrections to the k = 2 ledger: none.** `1/33` and `4/8` reproduce exactly.

Two things newly confirmed at source rather than inherited:

* The **"100% 10-year LC"** headline coexists in the same paper with one counted CMT-arm relapse
  at 143 months. 100% is a **censored-horizon actuarial** statement, not zero relapses.
  LOCOREGIONAL-2 recorded that caveat second-hand; it is now first-hand.
* The cohort is **"41 consecutive patients with localized, non-metastatic histologically
  confirmed EMC."** **Histologically**, not molecularly. Recorded because the unresolved third
  series is described as *molecularly* confirmed — the two cohorts are not defined the same way.

## 5 · The multicenter reference — identified on descriptor, and not readable

**Best descriptor match:** Paioli A, Stacchiotti S, Campanacci D, et al., *"Extraskeletal Myxoid
Chondrosarcoma with Molecularly Confirmed Diagnosis: A Multicenter Retrospective Study Within the
Italian Sarcoma Group"*, Ann Surg Oncol 2020;28(2):1142–1150, PMID **32572850**,
[DOI](https://doi.org/10.1245/s10434-020-08737-7). Abstract, verbatim: *"a retrospective pooled
analysis of patients with EMC treated at three Italian Sarcoma Group (ISG) referral centers was
carried out"* · *"All patients with localized EMC surgically treated from 1989 to 2016 were
identified"* · *"Only patients with NR4A3 rearrangement were included."* That is masunaga2025's
descriptor — *"another multicenter retrospective study involving only localized and molecularly
confirmed cases"* — almost word for word, and it predates masunaga2025.

**It is still not admitted, for four separate reasons:**

1. **No full text through the admitted route.** `convert_article_ids(pmid 32572850)` returns
   **no pmcid**; `find_related_articles(link_type="pubmed_pmc")` returns an **empty linkset**.
   Paioli 2020 is not in PubMed Central (`checks/06-…`, `checks/11-…`).
2. **The split is not in the abstract.** No 1/10, no 7/17, no p = 0.08, and no
   radiotherapy-stratified counts at all. Stated precisely: **not in the abstract** — this lane
   does **not** claim they are absent from the paper; the body was never read.
3. **The arithmetic does not obviously reconcile.** The abstract prints **67** localized patients
   and, verbatim, *"Thirty-five (52%) patients relapsed: 9 had local recurrence (LR) and 26 had
   distant metastasis (5 with concomitant LR)"* — **14** local recurrences among 67. The quoted
   split is **8 among 27** (1/10 + 7/17). A 27-patient radiotherapy-status-known subgroup is
   conceivable but is **not evidenced by anything retrieved.** Recorded as caution, not refutation.
4. **`POLICY-evidence.md` §1.3 — secondary provenance.** A count read out of another paper's
   Discussion is not a primary read. Admitting it on masunaga2025's authority would launder a
   citation. The k = 2 refusal stands unchanged.

**Identification is descriptor-level, not confirmed.** What would confirm it: masunaga2025's
numbered reference list — which the PMC extraction **strips** (the same tool returned no reference
list for bishop2019 either) — or Paioli 2020's own text showing a 10 vs 17 split.

**LOCOREGIONAL-2's recorded guess is refuted.** `chiusole2020` (Front Oncol 2020;10:828, PMID
32612944, [DOI](https://doi.org/10.3389/fonc.2020.00828)) is **two institutions**, molecular
analysis in only **23 of 59** cases — so not *"only molecularly confirmed"* — and reports local
recurrence as a **percentage** on a denominator of 49 (`checks/09-…`, `checks/10-…`). Also
searched and excluded: PMID 31331701 (pazopanib phase 2, advanced disease), PMID 42465974 (12-case
biomarker study, published 2026 — **after** masunaga2025, so it cannot be its reference), PMID
33308312 (single case report).

**Overlap, if it were ever admitted:** **overlap-unknown, not pooled.** Paioli 2020 (three ISG
centres, 1989–2016), chiusole2020 (Istituto Oncologico Veneto + Gustave Roussy, 1980–2018) and
Stacchiotti 2019 cover overlapping European sarcoma referral networks over overlapping calendar
periods with several shared authors. No patient-level overlap has been established **or excluded**.

## 6 · What did **not** change

k stays **2**. The counted-event base is unchanged: **21 local recurrences among 175 localised,
surgically treated patients in two series**. No pooled proportion, Wilson interval, Fisher p-value
or fragility count was recomputed. No pooled odds ratio, risk ratio, hazard ratio, risk
difference, cross-study p-value, I² or random-effects estimate was computed. The only substantive
change to the evidence base is a **provenance upgrade**: both surviving transcriptions are now
first-hand.

## 7 · Artifact · validation · provenance · limitations · stop condition

**Artifact.** `rt-local-control-contrast-ledger-k3.json` (21 325 bytes) and
`rt_contrast_ledger_k3.py`, this directory — the k = 2 ledger **explicitly NOT extended**, with
the reason recorded **per candidate**. No file outside this lane was created or edited
(`checks/15-no-writes-outside-lane/`); `LOCOREGIONAL-2/` is untouched. No `git add`/`commit`/
`push`, no `scripts/preflight.sh`, no subagent, no shared-file diff needed.

**Validation.** Fifteen recorded attempts in `checks/`, each with `command.txt`, `stdout.txt`,
`stderr.txt`, `exit_code.txt`. **`12-build-k3-ledger` is a preserved FAILURE** (exit 1, `KeyError:
'surgery_plus_RT'` — masunaga2025 stores its arms under its own printed labels
`neoadjuvant_or_adjuvant_RT` / `no_perioperative_RT`); `13-…` is the fixed re-run, exit 0. The k=2
byte-identity gate and the four arithmetic checks are re-run inside the builder on every
invocation and are recorded in the artifact's `gate` block. `--check` re-derives this lane's own
artifact byte-for-byte: **MATCH, exit 0.** Exit codes are real (`echo $?`, no pipes).

**Provenance.** One new primary full-text read (PMC7771031) and five abstract-only metadata reads,
all through the **PubMed/PMC MCP server — the admitted route and the only one used**. Every tool
call and its response are recorded verbatim under `checks/`. **No direct HTTP fetch was attempted**
to any host. Closed routes B1/B2, B4, B8, B9 stayed closed; PMID 22592656 was not a target; R1/R4,
R2, R3 were not restarted; MF1 and P-ST were not touched. Information from PubMed is cited to
PubMed with its DOIs, as the tool requires.

**Limitations.**
- The third series is **not resolved**. Its primary is identified only on descriptor, and the
  identification is **unconfirmed** — the arithmetic mismatch in §5(3) is a live reason it could
  be wrong.
- Whether Paioli 2020's body contains the 1/10 vs 7/17 split is **unknown**, not negative. It is
  **not in the abstract**; that is all this route can say.
- bishop2019's RT-arm event count 1 rests on subtraction of printed integers, cross-confirmed by
  an independently printed statement of the same integer — strong, but not a single printed "1/33".
- Every k = 2 limitation stands unchanged: crude, unadjusted, mixed follow-up (94 vs 38 months),
  censoring ignored, masunaga2025 supplying 77% of patients; the two series' non-irradiated rates
  differ roughly fourfold; the within-series difference is significant only in bishop2019, only
  against an eight-patient comparator arm, with fragility 2.

**Stop condition (from P6, MET).** *Stop as soon as the multicenter reference is identified and
read, or shown unresolvable through the admitted route.* It is **shown unresolvable through the
admitted route** — no PMC record, split not in the abstract, reference list stripped by the
extraction tool. A not-found is the result, recorded, **not padded**. Stopped.

## 8 · Next credible independent work (not started, not a dependency)

Resolving the 1/10 vs 7/17 primary needs a route this campaign does not have: masunaga2025's
numbered reference list, or the body of Ann Surg Oncol 2020;28(2):1142–1150. Both are outside the
admitted route, and **relabelling does not open them.** If a legitimate ordinary-access route to
that reference list ever exists, the bounded step is unchanged and small: read the primary, check
whether 10 + 17 = 27 is a real radiotherapy-status subgroup, flag **overlap-unknown** against the
other European series, and only then consider k = 3.
