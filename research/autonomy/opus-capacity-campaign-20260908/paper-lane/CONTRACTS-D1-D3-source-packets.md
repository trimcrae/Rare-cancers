# D1–D3 — three source-evidence packets. Contracts recorded BEFORE launch.

Recorded `date -u` **Tue Sep 8 07:56 UTC 2026**. Same session `session_01Eui7FVgatEXAwt2N35yHH6`, sole parent /
sole launcher, `claude-opus-5` requested medium, saved subscription, no overage, deadline
2026-09-09T02:37:19Z. Disk 20 GiB free at contract time (floor 10 GiB).

**C1 stays CLOSED** — failed guarded regeneration plus conditional arithmetic only. No repeat, no second
variant, no guard bypass, no source-row withdrawal, no model/manuscript/graph edit, no paper admission. The
`3297be57` / `1f661450` / `04386cbe` originals and the **canonical-probe versus global-absence** distinction are
preserved untouched. **These packets are NOT an extension of C1's no-network contract**; they are a new
prospective source-evidence commission under the standing public-source / clinical-evidence admission.

## Non-overlap verified by the parent BEFORE dispatch — not assumed from identifiers

`grep` over `CLOSED-WORK.md` for each target: **42340948, 41300991, 42068528, 41055780 — none appears**. All
four are distinct from the held/denied targets: S7's `PMID 35251555 / PMC8891938`; W25's `GSE243553`; the denied
routes `24703573` (Sunitinib 2014), `32856598` (Wagner), `35144048` (CTARC), Pazopanib, Trabectedin/RT; and
`22592656`. No target belongs to the NR4A Perspective, P6, or any P1–P6 lane.

## What every packet must do before judging

Read the **exact current stored claim** from `research/manuscripts/emc-host-factor-inputs.json` — population,
design, endpoint, numerical effect, units, `status`, `compartment` — **and** its citation context in the cited
manuscript and the committed model. The five input files and the manuscript hash-match both checkouts per the
C1 intake. ⚠ **This is substantive evidence assessment of whether the row supports the model, NOT a
whitelist-population exercise: a real PMID, or a matching title, is not scientific support.**

⚠ Note for all three: `check_anchors` skips only `status == "unretrieved"`. A row marked `association_only` is
**still** anchor-checked, so `association_only` does not exempt a citation from needing to be real and anchored.

## The three packets, with their exact stored claims

**D1 — HF-SMOKING, the drift.** Two PMIDs, one row.
- `41300991`, `compartment: B`, `status: retrieved` — *"patients with lung cancer who quit smoking at
  diagnosis, meta-analysis of non-randomised studies appraised with RoBANS 2 (searched to September 2024)"*,
  endpoint **overall survival**, **HR 0.74 (0.68–0.81)**, RRR 0.19–0.32. **This is the anchored one** and it is
  the citation the committed model output carries.
- `42340948`, `compartment: B_corroborating`, `status: association_only` — *"Korean NHIS-NSC cohort, 659,494
  participants: a pack-year-to-age ratio ≥ 1 carried an adjusted HR of 1.65 (1.51–1.81) for all-cause
  mortality"*. **This is the unanchored one** the inputs drifted to.
- Question: does each identifier resolve to a real work matching that description, and does that work support
  the stored numbers? The drift is the point — a cessation-effect row and an exposure-association row are
  different claims and must not be conflated.

**D2 — HF-CV-RISK.** `42068528`, `compartment: B`, `status: retrieved` — *"randomised primary-prevention statin
trials pooled in a systematic review with meta-regression (searched to 20 January 2026); adults without
established cardiovascular disease"*, endpoint **cardiovascular death**, **RR 0.81 (0.71–0.95)**, RRR
0.05–0.29, with a stored `verbatim` quotation: *"statin treatment was associated with a reduced risk of MACE
(RR, 0.73[95% CI, 0.67 to 0.80]) ... and cardiovascular death (RR, 0.81[95% CI, 0.71 to 0.95], P = 0.008)"*.
The row's own `endpoint_caveat` already records that this is **cardiovascular** death applied to a compartment
containing **every** non-EMC death. Question: does the identifier resolve to that work, and is the verbatim
quotation actually in it?

**D3 — HF-SARCOPENIA.** `41055780`, `compartment: B`, `status: association_only` — *"prospective
general-population cohorts pooled in a systematic review (searched to February 2024); dynapenic obesity defined
by BMI versus normal BMI"*, endpoint **all-cause mortality**, **HR 1.33 (1.16–1.53); 1.73 for the
abdominal-obesity definition**. Recorded at zero in the model. Question: does the identifier resolve to that
work and support those figures?

## Acceptance, per packet

**Either** an evidence-supported verdict carrying: exact article identity; **original source material actually
observed** and the retrieval route used; population / design / endpoint and numerical-claim support; any exact
citation or effect-size mismatch or uncertainty; and transfer limits. **Or** a precise missing-source / route
condition with **original failure evidence**.

⚠ **Distinguish original abstract vs full text vs table/figure observation from third-party summaries.
Abstract-only support stays abstract-only.** ⛔ **Never infer clinical benefit in EMC from another population.**

## Bounds and prohibitions

**20 minutes or ~30 tool calls per packet**, stopping earlier at a supported verdict or a missing condition.
Permitted: the existing PubMed capability and normal open primary sources. ⛔ **Do not retry S7's blocked NCBI
`WebFetch` routes**; do not switch network, CI, model or tool to evade a block; no paid access, no credentials,
no contacting anyone; no held W25/NR4A/P6 work; **no broad literature census**. If a route refuses or the source
cannot be observed, **preserve that exact scoped result and stop that branch — do not reword a failed request or
repeat a blocked route to force acceptance.** ⛔ **Do not infer literature absence from missing canonical-probe
membership.** If a citation identifies a **different** exact work, resolving that specific citation is allowed
inside the same finite bound; **no invented replacement evidence**.

Task-scoped durable scratch **outside** the shared checkout (`/tmp/claude-0/d1-retained/`, `d2-`, `d3-`),
separate ownership, **sole parent collection**. Preserve original tool responses, exact URLs / query inputs /
tool IDs / retrieval dates, source excerpts and fields, hashes, errors and refusals, and actual child model
evidence **before any cleanup**; keep raw responses alongside conclusions; **no reconstructing source bytes
later**. ≥10 GiB free. No repository write, no git operation, no manuscript/model/schema/guard/graph edit.

**The parent adjudicates the collected scientific support. Any regeneration or correction is a SEPARATE owner
decision and is NOT authorized by these packets.**

---

# D2 VERDICT — HF-CV-RISK / PMID 42068528: **the source is real, matches, and supports the number.**

Child `ac190a6eda3284f20`, observed transcript model `claude-opus-5`, 08:00:35 → 08:02:19 UTC (11 tool calls of
~30, ~1 m 45 s of the 20-minute bound). No repository write, no git operation; `git status --porcelain` empty at
both ends. Artifacts `sha256sum -c` **3 of 3 OK** in `/tmp/claude-0/d2-retained/` (not deleted) and again after
copying to `paper-lane/D2-executed-artifacts/`.

## Identity and support — resolved

PMID 42068528 = Long Y *et al.*, *"Sources of Heterogeneity in the Efficacy of Statins for Primary Prevention of
Cardiovascular Diseases: A Systematic Review with Meta-Regression and Meta-Analysis of Within-Study Subgroup
Differences"*, **Cardiovascular Drugs and Therapy**, 2026-05-02, DOI 10.1007/s10557-026-07883-6, PROSPERO
CRD42024579932; 25 RCTs, 102,667 participants. Every element of the stored `measured_in` matches the abstract —
including **"searches … up to 20 January 2026"** verbatim. **RR 0.81 (95% CI 0.71–0.95), P = 0.008 for
cardiovascular death is supported exactly**, and the stored RRR band 0.05–0.29 is arithmetically consistent
with that CI (1−0.95, 1−0.71), verified by computation rather than asserted.

⭐ **This settles a distinction that matters for the whole C1 blocker:** a PMID's absence from the canonical
probe means it was **not in that retrieval set** — it does **not** mean the citation is unreal or unsupported.
Here the unanchored identifier resolves to a real, matching work that supports its stored effect. The guard
failure and the evidence question are **two different things**, and this is the first packet to demonstrate it
on a specific row.

## The one mismatch, characterised exactly — and parent-verified

The stored `verbatim` is **not** word-for-word. Segment test: the cardiovascular-death clause is **exact
(True)**; the MACE clause is **not (False)**. The source reads *"…MACE (RR, 0.73[95% CI, 0.67 to 0.80], P <
0.001), MI …, stroke …, and cardiovascular death (RR, 0.81[95% CI, 0.71 to 0.95], P = 0.008)"*. The stored
quotation **drops `, P < 0.001` from inside the MACE parenthesis and closes it early, with no ellipsis or
bracket marking that elision**; its `...` correctly marks only the omitted MI and stroke clauses. **I confirmed
independently** that the committed string's MACE parenthesis carries no P value.

**No number, bound or word is altered or invented, and the clause carrying the effect the model actually uses is
exact.** This is a **quotation-hygiene defect, not a misquoted result** — the distinction is preserved, and what
should be done about it is not decided here.

## The endpoint caveat — necessary, and not sufficient as written

The source's scope confirms the caveat's direction: the abstract pools MACE, MI, stroke and cardiovascular
death and **reports no all-cause mortality estimate at all**, so nothing observed licenses an all-cause reading.
Three further limits the source imposes that the caveat does **not** name: the trial population is people
**without prior CVD**, which an EMC cohort is not screened for; **the overstatement is unquantified**, since the
non-cardiovascular fraction of compartment-B deaths is unknown, so the caveat gives the error's direction but
not its magnitude; and the estimate is **trial-level efficacy under trial adherence**, from a review whose
stated subject is heterogeneity of effect — **nothing in the observed source supports any specific
`transfer_multiplier`, including the model's 1.0 upper edge**.

## Two scope observations, neither a defect claim

**Parent-verified:** `grep` for `42068528` and `HF-CV-RISK` over `emc-mortality-mechanisms-paper.md` returns
**0 matches** — this row is not cited in that manuscript's prose and lives only in the two host-factor JSONs.
And a **notation collision**: the source uses "RRR" for *ratio of risk ratios* in its meta-regression, while the
repository field means *relative risk reduction*; the stored values are correctly derived from the CI and are
not the source's RRRs, but a future reader could conflate them.

## Observation grade, and what was not seen

**Abstract-only throughout, and it stays abstract-only.** Identity from the original PubMed record; population,
design, search date and the effect size from the **original abstract**. **No full text, no table, no figure was
observed; no third-party summary contributed anything.** The outcome-specific trial count, I², effect model and
risk-of-bias grading behind RR 0.81 are **unknown, not zero**. The full-text branch stopped on a preserved
refusal — `WebFetch https://doi.org/…` returned
`{"error_type":"EGRESS_BLOCKED","domain":"doi.org",...}` — a **publisher DOI route, not an NCBI route**; one
attempt, not reworded, not repeated, no tool or network switch. PMC was **NOT RUN** because the metadata carried
no PMC identifier, so no valid input existed.

## Transfer limit, binding

A primary-prevention statin effect on **cardiovascular death in adults without prior CVD** transfers to an EMC
cohort **at most as a direction and an order of magnitude**. It is **not** evidence of clinical benefit in EMC,
not evidence about EMC-specific death, not about all-cause death, and not a survival gain in any sarcoma
population. **No clinical benefit in EMC may be inferred from it.** There is no wet lab.

**Adjudication is the parent's and is not made here. C1 stays closed; no correction, regeneration, row
withdrawal or model change is authorized by this packet.**
