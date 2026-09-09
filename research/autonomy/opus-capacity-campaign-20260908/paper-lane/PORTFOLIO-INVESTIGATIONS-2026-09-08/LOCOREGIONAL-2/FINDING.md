---
id: DOC-PORTFOLIO-INVESTIGATION-LOCOREGIONAL-2-20260909
title: "LOCOREGIONAL-2 — the masunaga2025 per-arm local-recurrence split is reported; k moves 1 → 2"
level: L4
kind: investigation
status: complete
date: 2026-09-09
last_verified: 2026-09-09
lane: LOCOREGIONAL-2
continues: PUB-LOCOREGIONAL
campaign: OPUS-CAPACITY-CAMPAIGN-20260908
---

# LOCOREGIONAL-2 — settling the UNKNOWN the first lane named

⛔ **No clinical efficacy, safety, tolerability or therapeutic-window claim is made or supported
here.** Sizes are reported; effects are not. **RT-RT-INTENSIFY remains REFUTED** and
**RT-METASTASECTOMY remains DO-NOT-WRITE**; nothing below reopens either.

## 1 · The question

> `PUB-LOCOREGIONAL` closed with one named unknown: masunaga2025 prints arm sizes (24 / 110) and a
> local recurrence-free survival hazard ratio 0.50 (0.11–2.25), but no per-arm local-recurrence
> event count, and Table 2 does not carry one. **Does a per-arm event count appear anywhere else in
> PMC12398172, directly reported rather than reconstructed?**

## 2 · The answer — YES, verbatim

According to PubMed, from the open-access full text of Masunaga T, Tsukamoto S, Nagano A, et al.,
*"The role of radiotherapy and chemotherapy in extraskeletal myxoid chondrosarcoma"*,
J Orthop Surg Res 2025 — PMC12398172, PMID 40885991,
[DOI](https://doi.org/10.1186/s13018-025-06245-6) — retrieved 2026-09-09 through the PubMed/PMC MCP
route (`checks/01-pubmed-mcp-fulltext-PMC12398172/`):

> **"Of the 24 patients who received (neo)adjuvant radiotherapy, two (8.3%) experienced local
> recurrence, and of the 110 patients who did not receive (neo)adjuvant radiotherapy, 14 (12.7%)
> experienced local recurrence."**

It is **not in Table 2** — the first lane's transcription of Table 2 was correct and complete. The
split sits in the **Results body text**, in the paragraph immediately after the Table 2 call-out,
under *"Patients without metastases at diagnosis"*. The integers are **printed as words** with the
percentages in parentheses.

**Nothing was reconstructed.** No count here comes from the hazard ratio, the arm sizes, the
p-value, a confidence interval or Fig. 2. Fig. 2 (the LRFS Kaplan–Meier by radiotherapy status)
carries no numbers-at-risk table in the retrieved text and was not read for numbers.

Sections checked: Abstract; Background; Methods; Results (Table 1, *Patients without metastases at
diagnosis* incl. Tables 2–4, *Patients with metastases at diagnosis*); Discussion; Conclusions.
Supplementary Material 1 is referenced but not returned by this route — and is **not needed**,
because the split is in the body.

### 2.1 It checks out against everything else the paper prints

| check | result |
|---|---|
| 2 + 14 = 16 = printed total local recurrences among the 134 | ✅ |
| 24 + 110 = 134 = the analysed localised surgical cohort | ✅ |
| 2/24 → 8.3%, 14/110 → 12.7% — the printed percentages | ✅ both |
| 16/134 → 11.9% — the printed overall local-recurrence rate | ✅ |

Recomputing a **printed percentage from printed integers to confirm they agree** is verification.
It is not the forbidden reverse move.

## 3 · What changed — k = 1 → k = 2

| | before (PUB-LOCOREGIONAL, 2026-09-08) | after (this lane) |
|---|---|---|
| series with arm-level counted events | **1** (`bishop2019`) | **2** |
| counted local-recurrence events carrying the contrast | **5** | **21** |
| patients carrying the contrast | 41 | **175** |
| a pooled proportion admissible? | **No** — §2.1(2) failed | **Yes, for this contrast** |

`rt-local-control-contrast-ledger-k2.json` (this directory), built by
`rt_contrast_ledger_k2.py`, records it. The prior lane's ledger is **unchanged and not edited**.

### 3.1 The two 2×2s, reported as sizes

| series | surgery + RT | no perioperative RT | Fisher 2-sided | fragility | median f/u |
|---|---|---|---|---|---|
| `bishop2019` (MD Anderson) | **1/33** = 3.0% (Wilson 0.5–15.3) | **4/8** = 50.0% (21.5–78.5) | **p = 0.0032** | **2** | 94 mo |
| `masunaga2025` (Japan registry) | **2/24** = 8.3% (2.3–25.8) | **14/110** = 12.7% (7.7–20.3) | **p = 0.7361** | n/a | 38 mo |

⛔ Neither table is an effect estimate. Treatment was assigned by indication in both.

### 3.2 The pool, and the deliberate absence in it

Under `systems/POLICY-evidence.md` §2.1–§2.4 the pool is now **admissible for this contrast**, and
the ruling is decided rather than asserted in `pool_admissibility`:

* **§2.1(2) explicit integer counts** — the criterion that failed at k=1 — **now holds for both.**
* **§2.1(4)/§2.3 non-overlap** — `bishop2019` carries `pool:false` for overlap with SEER / the US
  Sarcoma Collaborative, but **neither `ussc2022` nor `remiszewski2025` nor `seer270_2022` nor
  `uMich2023` contributes any arm-level event to this contrast**, so no patient can be counted
  twice. §2.3 names this exact pair as permissible: *"Distinct populations (e.g. a Japanese registry
  and a US single institution) may be pooled."* **The ruling is scoped to this contrast only** —
  `bishop2019` still must never be summed into a total containing those US series, and this lane
  changed **no registry pool flag**.
* **§2.4** — only the **crude during-follow-up counts** are pooled. Bishop's 10-year actuarial local
  control and Masunaga's LRFS hazard ratio are **per row, never merged**.

**Crude pooled per-arm proportions, labelled crude / unadjusted / mixed follow-up / no censoring:**
surgery + RT **3/57 = 5.3%** (Wilson 1.8–14.4) · no perioperative RT **18/118 = 15.3%** (9.9–22.8).

**Deliberately not computed:** any pooled odds ratio, risk ratio, hazard ratio, risk difference,
cross-study p-value, I², or random-effects estimate. §2.2 sanctions a crude pooled proportion with a
Wilson interval and side-by-side per-cohort rates — nothing more — and the contrast between those
two numbers is confounded by indication and not interpretable as an effect.

### 3.3 The confounding is measured, printed, and runs against radiotherapy

Same paper, verbatim:

> *"Of the 24 patients who received (neo)adjuvant radiotherapy, 10 (41.7%) had R1 or R2 surgical
> margins, whereas only 20 (18.2%) of the 110 patients who did not receive (neo)adjuvant
> radiotherapy had R1 or R2 surgical margins."*

and *"Neoadjuvant or adjuvant radiotherapy is administered to prevent local recurrence in patients
with close surgical margins."* An R1/R2 margin is that paper's **only** significant multivariable
risk factor for local recurrence (HR 4.76, 1.72–13.15, p=0.003). **The irradiated arm was
systematically the higher-risk arm.** The authors state the bias themselves: *"there was an
indication bias for (neo)adjuvant radiotherapy and chemotherapy use."*

This is a reason the crude numbers cannot be read as an effect **in either direction**. It is not a
licence to reinterpret them as favourable.

The ledger also records, so as not to present only the favourable-looking row, masunaga2025's
**disease-specific survival** univariate row for radiotherapy: HR **5.05** (1.34–19.04), p=0.017 —
which did **not** survive that paper's own multivariate model. ⛔ **No safety claim is made or
supported by it**; it is an unadjusted univariate size in a cohort with a measured margin imbalance.

## 4 · A third split exists, and is NOT admitted

masunaga2025's Discussion quotes *"another multicenter retrospective study involving only localized
and molecularly confirmed cases"* with printed integers — **1/10 (10%) vs 7/17 (41%), p=0.08**.

**Not admitted, and k is not raised on it.** §1.3 forbids laundering a citation: a count read out of
another paper's discussion is not a primary read, and the retrieved full text has the reference
numbers stripped, so **the primary study is UNIDENTIFIED**. `chiusole2020` (European two-institution
series, n=49) is a plausible candidate for a 27-patient localised molecularly-confirmed subset —
**this is a guess, recorded as one, and has not been checked.** Resolving that reference and reading
the primary directly would take k to 3; that is the next credible step and it was not taken here.

Also recorded and excluded: `drilon2008`, 41% vs 35%, p=0.79 — **percentage-only**, §2.1(2).

## 5 · Artifact · validation · provenance · limitations · stop condition

**Artifact.** `rt-local-control-contrast-ledger-k2.json` and `rt_contrast_ledger_k2.py`, this
directory. No file outside this directory was created or edited. No `git add`/`commit`/`push`, no
`preflight.sh`, no subagent.

**Validation.** Four recorded executions in `checks/`, each with `command.txt`, `stdout.txt`,
`stderr.txt`, `exit_code.txt`, all exit 0 (`01` is the MCP retrieval, recorded as a tool call rather
than a shell command). Four internal arithmetic consistency checks against quantities printed
elsewhere in the same paper, all ✅ (§2.1). Wilson uses the same closed form and the same
z = 1.959963984540054 as the prior lane and as
`research/modalities/emc_locoregional_eligibility.py:141-149`, so the two ledgers are directly
comparable. `--check` re-derives the artifact and compares it byte-for-byte: **MATCH, exit 0**.

**Provenance.** One new primary read, by the ordinary permitted PubMed/PMC MCP route. **No direct
HTTP fetch was attempted** to any host; the closed routes stayed closed. Everything else is read
from committed repository artifacts. Only short verbatim excerpts necessary to evidence the finding
are reproduced (registry records the article as CC-BY-NC-ND-4.0).

**Limitations.**
- `bishop2019`'s counts remain **second-hand at one remove** — transcribed from
  `emc-radiotherapy-contradiction.json`, not re-verified against that paper. Only masunaga2025 was
  read at source in this lane. So k=2 rests on one verified and one inherited transcription.
- The pool is **crude, unadjusted, mixed follow-up (94 vs 38 months median), censoring ignored**,
  and `masunaga2025` supplies 77% of the patients and 76% of the events.
- The two series **disagree by roughly fourfold in their non-irradiated recurrence rate** (50.0% vs
  12.7%). The pooled point estimate hides that. No I² is computed, by policy.
- The within-series difference is significant **only** in `bishop2019`, **only** against an
  eight-patient comparator arm, with **fragility 2**.
- The third split (§4) is a real, printed, directly-reported per-arm count that this lane **could
  not admit** because its primary is unidentified — a bounded, checkable gap, not an absence.
- Supplementary Material 1 was not retrievable by this route and was not needed.

**Stop condition (set at dispatch, MET).** Stop once the presence or absence of a directly reported
per-arm split in PMC12398172 is settled by an ordinary permitted read, the ledger reflects the
result, and the artifact is reproducible by a `--check` path. All three hold.

## 6 · Verdict — the prior no-go was conditional, and the condition resolved in the affirmative

⭐ **k moved from 1 to 2.** The first lane's bounded no-go was explicitly conditional on this
unknown, and it does **not** stand permanently at k=1. What replaces it is narrower and firmer:

> The entire counted-event evidence base for the adjuvant-radiotherapy local-control contrast in EMC
> is **21 local recurrences among 175 localised, surgically treated patients in two series**. A
> crude pooled **proportion** is admissible; a pooled **effect estimate** is not, and is not
> computed. The within-series difference is significant only in the 41-patient series, only against
> an eight-patient comparator arm, with a fragility of 2 — while in the 134-patient registry, where
> the irradiated arm was measurably the higher-risk arm (41.7% vs 18.2% R1/R2 margins), the crude
> rates are 8.3% vs 12.7% with p = 0.74.

That sentence is defensible, new, and more useful to a clinician than *"100% vs 63%."*

**Next credible independent work** (not started, not a dependency of the above): resolve the
unidentified multicenter reference behind **1/10 vs 7/17** and read that primary directly, which
would take k to 3; and re-verify `bishop2019`'s 1/33 and 4/8 at source, which would make both
transcriptions first-hand.
