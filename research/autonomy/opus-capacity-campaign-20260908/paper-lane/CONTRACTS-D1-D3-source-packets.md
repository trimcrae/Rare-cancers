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
