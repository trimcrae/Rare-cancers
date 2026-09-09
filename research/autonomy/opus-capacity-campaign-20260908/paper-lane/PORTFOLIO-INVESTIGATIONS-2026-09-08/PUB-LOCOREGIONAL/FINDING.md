---
id: DOC-PORTFOLIO-INVESTIGATION-PUB-LOCOREGIONAL-20260908
title: "PUB-LOCOREGIONAL — how many counted events carry the adjuvant-radiotherapy contrast in EMC"
level: L4
kind: investigation
status: complete
date: 2026-09-08
last_verified: 2026-09-08
lane: PUB-LOCOREGIONAL
campaign: OPUS-CAPACITY-CAMPAIGN-20260908
---

# PUB-LOCOREGIONAL — the counted-event floor under the local-control argument

⛔ **No clinical efficacy, safety, tolerability or therapeutic-window claim is made or supported
here.** The result runs the other way: it measures how little counted evidence exists.

## 1 · The question

> Restricted to **counted local-recurrence events with a stated treatment-arm assignment**, what is
> the entire admissible evidence base in this repository for the **surgery + radiotherapy vs surgery
> alone** contrast in extraskeletal myxoid chondrosarcoma — once population overlap, endpoint
> definition and arm-level event availability are each made explicit rather than assumed?

Cohort limit: patients **localised at diagnosis and surgically treated**, in series that record a
local-treatment exposure. Endpoint limit: **local recurrence as a counted event**, kept separate
from actuarial local control at a timepoint and from local recurrence-free survival. Overlap limit:
the US series are treated as one possibly-shared population and never summed.

## 2 · Paper-level merit

`PUB-LOCOREGIONAL`'s stated claim is that this disease is *"unusually well matched to locoregional
and radiation-based treatment."* The single strongest sentence available to that argument is
Bishop 2019's title — *"Combined Modality Therapy With Both Radiation and Surgery Improves Local
Control"* — and its 10-year local control of **100% vs 63%**, HR 12.7. A manuscript that leans on
that sentence without stating the event count under it would be repeating exactly the failure mode
this repository has already been burned by. Patient relevance is direct: adjuvant radiotherapy is a
real decision taken in this disease today. The contribution is non-trivial because the arithmetic
below is not printed in any of the source papers, and it is attainable because every input is
already committed.

**Scientific strength before convenience:** the honest deliverable is a floor on the evidence, not a
synthesis of it.

## 3 · The evidence gap, and how it differs from completed work

Already done and **not** re-opened:
- `research/modalities/emc-radiotherapy-contradiction.json` put Bishop and Masunaga *on one hazard
  scale* and showed the route's premise (a live contradiction) fails — both protective, intervals
  overlapping, the disagreement in significance not direction.
- `research/manuscripts/care-delivery/emc-care-delivery-endpoint-decision.md` rules
  **RT-RT-INTENSIFY REFUTED** and **RT-METASTASECTOMY DO-NOT-WRITE**. Honoured.
- P3 (`../../P3-PUB-LOCOREGIONAL-paper-step.md`) reproduced both headline pools and drafted §3.

**Unfinished, and different in kind:** every prior treatment of this contrast is *model-level* — HRs,
intervals, p-values. Nobody has assembled it at the level of **counted events per arm**, which is the
only level at which this repository's pooling contract (`systems/POLICY-evidence.md` §2.1(2), §2.3,
§2.4) can rule on whether a synthesis is permitted at all. Named inputs: the arm sizes and event
sentences in `emc-radiotherapy-contradiction.json#estimates`, the Table 2 rows in
`emc-prognostic-coefficients.json#models`, the arm counts in `emc-site-curation.json#series[2]`, and
the overlap flags in `research/data/emc-clinical-registry.json#registry.cohorts`.

## 4 · The bounded step taken

`rt_local_control_contrast_ledger.py` (stdlib only, read-only over committed inputs) →
`rt-local-control-contrast-ledger.json`.

### 4.1 The counted-event floor — **5 events, one series, k = 1**

| series | arms (n) | arm-level local events | endpoint as printed | poolable |
|---|---|---|---|---|
| `bishop2019` (MD Anderson, 1990–2016) | surgery+RT **33** (23 pre-op, 10 post-op) / surgery alone **8** | **1 / 4** — printed as integers | 10-yr actuarial local control | **No** — `pool:false`, population-overlap with USSC/SEER |
| `masunaga2025` (Japanese registry, 2002–2022) | RT **24** / no RT **110** | **NOT PRINTED** — HR 0.50 (0.11–2.25), p=0.365 only | local recurrence-free survival | contributes **0** countable events to the contrast |

Every other registry cohort records **no local-treatment exposure at all**. So the entire counted
evidence for the contrast is **5 local recurrences among 41 patients in one single-institution
retrospective series that the registry itself refuses to pool.**

### 4.2 The one countable 2×2 (reported to show its size, not to estimate an effect)

Surgery alone **4/8 = 50.0%** (Wilson 21.5–78.5) · Surgery + RT **1/33 = 3.0%** (Wilson 0.5–15.3) ·
Fisher exact two-sided **p = 0.0032** · **fragility = 2**: reassigning two of the four surgery-alone
events pushes p above 0.05. Treatment was assigned by indication; there is no adjustment and no
randomisation. ⛔ This is not an effect estimate.

### 4.3 A decidable internal-consistency finding

A 10-year actuarial local control of **100%** in the surgery+RT arm cannot coexist with a relapse
inside 10 years in that arm — yet the same paper counts **one** relapse among those 33. Printed
relapse times run 13–176 months, so the two are **consistent only if that relapse fell at or beyond
120 months.** Consistency is possible and is not contradicted. What follows is narrower and firmer:
**"100% local control" is a statement about a censored horizon, not a statement that the arm had no
local relapses.** Quoting it without the event count and the horizon overstates what was observed.

### 4.4 The endpoint mixture in the existing headline pool

The committed pooled local-recurrence figure — **27.0% (88/326), Wilson 22.5–32.1, k=4** — mixes
endpoint definitions. `ussc2022` contributes an explicitly **locoregional** count; the registry
records the other three only as *"recurrence"*, without saying local, distant or any.
`emc-radiotherapy-contradiction.json` resolves `masunaga2025`'s 16 events as **local** recurrence.
For **`meisKindblom1999` and `chiusole2020` the endpoint definition is not resolved by any committed
artifact read here** — 54 of the 88 pooled events sit in cohorts whose endpoint the repository has
not written down. That is a named, checkable gap, not a generic caveat.

## 5 · Artifact · validation · provenance · limitations · stop condition

**Artifact.** `rt_local_control_contrast_ledger.py` and `rt-local-control-contrast-ledger.json`
(this directory). No file outside this directory was created, edited or staged.

**Validation.** Four recorded executions in `checks/` (`command.txt`, `stdout.txt`, `stderr.txt`,
`exit_code.txt`), the first a preserved failure (`exit 1`, `KeyError: 'coefficients'` — the
prognostic-coefficients schema uses `rows`, not `coefficients`). `--check` re-derives the artifact
and compares it byte-equivalently to the committed one: **MATCH, exit 0**. Wilson intervals use the
same closed form and the same `z = 1.959963984540054` as
`research/modalities/emc_locoregional_eligibility.py:141-149`; the 27.0% headline is read from the
committed artifact rather than recomputed. Baseline: the arm sizes 33+8 and 24+110 each sum to their
cohort n (41, 134) — checked in the artifact.

**Provenance.** Every quantity is a transcription already committed to this repository. No network
request, no PDF, no paid API, no GPU, no new retrieval, no subagent. Nothing was read from any closed
or denied source.

**Limitations.**
- Transcription fidelity is inherited, not verified: whether `4 of 5`, `33/8`, `24/110`, `16/134` and
  the 176-month range faithfully reflect the printed papers is **UNKNOWN to me**. Every count is
  second-hand at one remove.
- The 2×2 is crude, unadjusted, confounded by indication, and drawn from 5 events. It is reported as
  a **size**, never as an effect.
- The Fisher p and the fragility count describe that one table only. Neither transfers to the disease.
- `meisKindblom1999` and `chiusole2020` endpoint definitions are recorded here as **unresolved**, not
  as absent from their papers.
- The overlap ledger records the registry's *declared* overlap classes; I did not independently
  establish that `bishop2019` is or is not inside USSC/SEER.

**Stop condition (set at dispatch, MET).** Stop once the arm-level event ledger is complete over
every registry cohort, the admissibility ruling under §2.1/§2.3/§2.4 is decided rather than asserted,
and the result is reproducible by a `--check` path. All three hold.

## 6 · Verdict — a bounded NO-GO, with what it licenses

⛔ **No pooled or synthesised estimate of the adjuvant-radiotherapy local-control contrast in EMC is
admissible** under this repository's evidence contract: k=1 on counted events, two non-identical
estimands, and the one series with arm-level counts is `pool:false` for population overlap.

⭐ **What a manuscript may still say**, and what makes this worth writing: the population size, the
arm sizes, the five events with their split, the two published hazard ratios each with its interval
and its confounding direction, and the explicit statement that **the entire counted evidence base for
this contrast is five local recurrences in one non-poolable series.** That sentence is defensible,
new, and more useful to a clinician than the headline it replaces.

**Next credible independent work** (not started, not a dependency of the above): obtain the per-arm
local-recurrence event split for `masunaga2025`, which would raise k from 1 to 2 on counted events.
It is not in Table 2 as transcribed; whether it appears elsewhere in PMC12398172 is **UNKNOWN** and
would need an ordinary permitted read of that open-access text. Failing that, the no-go stands.
