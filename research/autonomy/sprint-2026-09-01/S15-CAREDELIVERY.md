# S15-CAREDELIVERY — five care-delivery judgement calls answered, and two recorded absences refuted from one file

**Item(s):** AUT-042, AUT-057, AUT-058, AUT-064, AUT-065
**Owned paths:** `research/autonomy/sprint-2026-09-01/S15-CAREDELIVERY.md`, `research/manuscripts/care-delivery/emc-care-delivery-endpoint-decision.md`, `research/manuscripts/care-delivery/emc-absence-claims-refuted.json`
**Started/Finished (UTC):** ~2026-09-01T18:55Z / 2026-09-01T19:24:36Z

## Verdict

**PARTIAL + REFUTED** — three of five rows have a publishable statement and should be written as one
section of one paper (AUT-064 + AUT-057 + AUT-065); **AUT-042's proposed sentence has no computable
denominator and its premise is refuted; AUT-058 is already written elsewhere and its one new half is
wrong.** Two recorded absences load-bearing on two route grades are false against the very corpora
they name, proved by one blob SHA. `endpoint_declared` **cannot** close tonight for either paper, and
the reason is mechanical rather than evidentiary.

---

## What I measured

### 1 · The bar reading, re-taken, and what it actually says

```
$ python3 research/autonomy/publish_bar.py --paper PUB-CARE-DELIVERY --sha d5f8f3c675842b572f793b41f48024461729eada
PUB-CARE-DELIVERY @ d5f8f3c67584 -> BLOCKED (0/7 clauses)
  [FAIL] the endpoint is a declared falsifiable claim
         endpoint names no existing document (None)
  [????] claim strength within the endpoint's ceiling
         PUB-CARE-DELIVERY has no document.file in publications.json
  [????] every identifier traces to a fetch or the ledger
         PUB-CARE-DELIVERY has no readable document
  [????] the outgoing text is readable and keeps its caution
         PUB-CARE-DELIVERY names no document
```
Identical shape for `--paper PUB-LOCOREGIONAL`. ⭐ **The 0/7 is not "the manuscript does not
meaningfully exist" in the sense of a missing claim.** `clause_5_endpoint_declared` requires two
things — a `what_it_would_claim` ≥ 40 chars, and a `document.file` that exists on disk. **Both papers
pass the first.** Four of the seven clauses fail on the second, one missing field. Across all 32
entries of `systems/graph/publications.json` the correlation is exact: every `drafted`-or-better entry
has a `document.file`; every `unwritten`/`outlined` entry has none. So the bar is reporting that
nobody wrote the paper, not that the evidence is thin.

### 2 · ⛔⛔ TWO RECORDED ABSENCES ARE FALSE AGAINST THEIR OWN CORPORA — ONE FILE, ONE BLOB SHA

Read at $0 via the GitHub contents API on `refs/heads/literature-cache` (branch commit
`0eac3e3aaa5b3e`). **No git write command was run and the branch was not checked out.** The API
returns **the same blob SHA `79a8c197243f`** at both:

| path | corpus | the absence recorded against it |
|---|---|---|
| `literature/emc-care-delivery-and-classification/PMC12398172.txt` | the 554-record corpus, 2026-08-09 | `emc-care-delivery-evidence.json` → `absences[]` `no-emc-metastasectomy-literature`, `"result": "ZERO records."` |
| `literature/emc-radiotherapy-2026-08-26/PMC12398172.txt` | the 354-text corpus, 2026-08-26 | `emc-radiotherapy-contradiction.json` → `carbon_ion.found_in_this_histology: false` |

That file is Masunaga 2025 (`PMC12398172`, PMID 40885991), 171 pathologically diagnosed EMC patients,
and it contains **both** refuting sentences, verbatim:

> "Eight patients (27.6%) underwent metastasectomy, including six, one, and one who underwent lung,
> bone, and lymph node resections, respectively."

> "Of the eight patients who did not undergo surgery, two received carbon ion therapy, one received
> proton beam therapy, and one received conventional radiotherapy."

**The blob identity is the discriminating observation.** Two different corpora invites the reading
that each simply lacked the paper. It does not: one identical file sits inside both.

⛔⛔ **The carbon-ion case is worse, because the artifact considered that exact sentence and rejected
it.** Its own field records a web-search synthesis reporting *"two received carbon ion therapy, one
received proton beam therapy"* and dismisses it as belonging to *"EXTRACRANIAL CHONDROSARCOMA
generally, not to this histology … An AI search summary is a lead, never a citation."* That is
verbatim Masunaga. **The lead was right and the verification reached the wrong source** — CLAUDE.md
§4's prediction that a dismissed reading errs in the direction that kills a route, landing exactly
there.

**Mechanism, and no gate could have caught either.** Neither value is computed:
```
research/modalities/emc_care_delivery_evidence.py:216      "result": "ZERO records.",
research/modalities/emc_radiotherapy_contradiction.py:191  "found_in_this_histology": False,
research/modalities/emc_radiotherapy_contradiction.py:351  if CARBON_ION["found_in_this_histology"] is not False:
                                                    :352      errs.append("the carbon-ion finding has flipped without its search being redone")
```
Both are literals; the generators never read the corpus. **And the guard at :351 now locks the wrong
answer in** — written to stop an unexamined flip, it also stops a corrected one, so the value and its
guard must move in the same commit or the build goes red on the fix.

**What survives, narrowed rather than withdrawn:** no reachable series studies metastasectomy *with a
comparator* — Bishop's is the only comparison and it is uninformative at n = 13 (salvage surgery
p = 0.15, salvage chemotherapy p = 0.24) — and **no outcome is printed for any of the two carbon-ion
or one proton-beam patients**, because all eight non-operated patients are excluded from that paper's
prognostic analysis. Arms exist; comparisons do not.

### 3 · Row by row — the artifact against the row's own description

| row | artifact read | does the artifact match the row? |
|---|---|---|
| **AUT-064** | `emc-surgical-quality.json` | ⚠ **NO, and the artifact is right.** Row says *"a positive-margin rate with an honest denominator range"*. Artifact: *"THERE IS NO SINGLE POSITIVE-MARGIN RATE and the artifact refuses to elect one"*, with a test failing if the denominator stops moving the answer by more than any interval's width. One rate carrying a range is the reading the data refuses. |
| **AUT-057** | `emc-prognostic-coefficients.json` | ✅ matches, and is weaker than "cross-cohort consistency" sounds: 9 of 12 comparisons are between two intervals that **both** include 1, and **in none do both exclude 1**. |
| **AUT-065** | `emc-recurrence-timing.json`, `emc-ipd-survival.json` | ✅ matches. The IPD artifact holds **1** admitted curve (n = 11, 9 events, PFS, anthracycline-treated advanced) plus 2 printed trabectedin rows — genuinely the wrong shape for a surveillance model. |
| **AUT-042** | `emc-site-curation.json`, `emc-care-delivery-evidence.json` | ⛔ **NO.** Row's *"roughly a quarter"* is the lowest of three counts, taken from one stratum. Row's *"no comparator anywhere in the literature"* is refuted by Bishop. Its underlying absence is refuted by §2. |
| **AUT-058** | `emc-radiotherapy-contradiction.json`, `emc-radioresistance-reappraisal.md` | ⛔ **REFUTED.** The finding was written up **2026-08-07** in a live L3 memo, over *three* series with Cochran Q = 2.015 (p = 0.365, I² ≈ 0.007), pairwise z = 1.36, and an α/β identifiability closure. The row's note is a subset of an existing document. |

**The denominators, plainly (this is the answer to "is a positive-margin rate a result?"):**

*Margin — a result, because every denominator is named:* 25.0 % of **156** operated · 22.4 % of **134**
operated-and-localized · 40.9 % of **22** operated-and-metastatic · 35.0 % of **40** with the field
recorded. The denominator is explicit in every case and moves the answer by ~20 points inside one
paper. Nothing is computed over a population nobody defined.

*Metastasectomy — not a result, because no denominator exists:* 8/**29** presenting metastatic ·
8 metastasectomies + 2 ablations against a printed denominator of **47 that the paper never defines** ·
5/**13** who developed distant disease in a localized cohort. Presenting stratum, unstated
denominator, incidence cohort. POLICY-evidence §2.1/§2.3 forbid summing them, and there is no shared
population to name.

### 4 · Two stale records on PUB-CARE-DELIVERY, refuted

- `why_not_written`: *"The paper needs the reconstructed survival dataset (RT-IPD-SURVIVAL) to say
  anything quantitative."* **False now.** Four quantitative artifacts landed since, none of which
  consumes the reconstruction — 196 operated patients with a margin, 45 printed Cox coefficients, 271
  patients' site distribution, four printed time-to-event statistics with three IQRs. AUT-065 says the
  same thing in its own words.
- `blocked_by: BLK-NO-CURATED-CLINICAL-DATA`: *"…have never been extracted into the registry."*
  **Mis-stated.** They were extracted into `research/modalities/`, which is the correct home:
  `emc-site-curation.json` records that `research/data/emc-clinical-registry.json` sits inside a
  DOI-deposited archive manifest, so a byte change forces a re-stamp of a published deposit.

### 5 · Gates I ran (scoped to my change, per charter §6)

| gate | result |
|---|---|
| `lint_consistency.py` | **0 ERROR across 26 target file(s)** — unchanged from baseline. My files are not in `pinned-figures.json` targets. |
| `lint_claims.py` | **0 ERROR**, 168 WARN across 129 files (baseline 167). `grep` for both my paths in the output returns **nothing** — neither of my files raises a warning. |
| `lint_style.py` | exit 0 |
| `parser_guard.py` | exit 0 |
| JSON parse of my artifact | OK |
| `lint_citations.py` | ⛔ **exit 1 — 3 NEW unanchored PMIDs, all three in `research/autonomy/sprint-2026-09-01/S16-NEGATIVES.md`** (24555529, 28698435, 36568164). **Not mine, not my owned path.** My only prose identifiers (PMID 40885991, PMC12398172) are anchored by `emc-site-curation.json`. |

⚠ **Driver: `lint_citations` is red on `main`'s working tree right now and the cause is S16's file.**
Either S16 anchors those three in `citation-provenance-ledger.json` or they come out of the prose.
Preflight will stay red until then.

---

## What I changed

- **`research/manuscripts/care-delivery/emc-care-delivery-endpoint-decision.md`** *(new)* — L3 memo,
  `DOC-EMC-CARE-DELIVERY-ENDPOINT-DECISION`. Answers all five rows with a recommendation and its
  reasoning, states each publishable sentence and its honest denominator, and answers the
  `endpoint_declared` question for both papers. Quotes the six modality artifacts and computes
  nothing; every number's home is named in its header.
- **`research/manuscripts/care-delivery/emc-absence-claims-refuted.json`** *(new)* — the two
  refutations as a machine-readable record: blob SHA, both corpus paths, the verbatim sentences, what
  depends on each absence, and the guard that locks the carbon-ion value. A SHA makes the refutation a
  byte comparison rather than an argument.
- **`research/autonomy/sprint-2026-09-01/S15-CAREDELIVERY.md`** *(this file)*.

**Nothing else.** No manuscript, no ledger row, no registry file, no graph file, no artifact under
`research/modalities/`, no git command of any kind.

⚠ **Driver, so you stage by path and not by `-A`:** `git status` at 19:24Z also shows
`research/manuscripts/care-delivery/emc-icdo-9231-classification.md` modified and
`research/manuscripts/care-delivery/icdo-9231-restriction-audit.json` new. **Neither is mine** — another
seat shares this directory. My three paths are the only ones listed above.

⛔ **The memo is NOT the PUB-CARE-DELIVERY paper and must not be wired to its `document.file`.** It is
a decision memo about five ledger rows. Pointing an endpoint at it would close `endpoint_declared`
with a document that is not the paper its claim describes.

---

## What I could not do, and what it is actually waiting on

| item | what it is waiting on — checked, not assumed |
|---|---|
| Correct the two false absences | **`research/modalities/` is not my owned path.** Both fixes are $0 and each is one literal plus, for carbon ion, the guard at `emc_radiotherapy_contradiction.py:351` in the **same** commit. |
| Re-grade RT-METASTASECTOMY and RT-RT-INTENSIFY | `systems/graph/routes.json`, not mine. Both grades quote the refuted absences verbatim. |
| Amend PUB-CARE-DELIVERY's claim, `why_not_written` and blocker; amend PUB-LOCOREGIONAL's claim | `systems/graph/publications.json`, not mine. |
| Close `endpoint_declared` | **A manuscript that does not exist.** Not a data gap: §3.1–§3.3 of the memo are the three sections and every number is committed. Writing it is free and is a next-seat or next-cycle task. |
| Establish *how* each search failed | **Not establishable, and I did not guess.** Both values are literals, so no search execution is on record. What is established is that the recorded value disagrees with a file in the corpus it names. |

**Nothing here is blocked on trimcrae, on spend, or on the outside world.**

---

## Answer to the driver's question: can `endpoint_declared` close tonight?

**PUB-CARE-DELIVERY — NO tonight, and the claim needs one amendment first.** Its declared claim names
three determinants and **the second cannot be studied at all**: *"whether the diagnosis was known
before it"* is the unplanned-excision question, and `emc-surgical-quality.json` records
`unplanned_excision.recorded_in_any_reachable_series: false` with both proxies marked
`is_the_thing: false`, plus the same verdict for treatment setting. The sentence the evidence in hand
does support, offered for the driver to install:

> In extraskeletal myxoid chondrosarcoma the completeness of the first operation is the only
> determinant that holds its direction across four endpoints and two independent cohorts, and the
> published record cannot price it, cannot say whether the diagnosis was known before that operation,
> and stops watching patients before a quarter of the local recurrences it reports have happened.

Falsifiable in three separate places, each already carried by a committed artifact. **But clause 5
also needs an existing `document.file`, and that manuscript does not exist.** Two free steps stand
between here and a green clause: write it, then one line in the graph.

**PUB-LOCOREGIONAL — NO, and more is missing than a document.** Three of its four clauses survive;
the fourth (*"had never assessed any of it"*) is broken by §2, and *lung-metastasis-dominant* holds
only as **involvement** — the 27/29 and 12/13 readings are upper bounds on a lung-confined fraction
and the one series that separates confined from involved reports the confined figure markedly lower,
which cuts against the eligibility criterion a lung-directed strategy needs. **Its claim must be
rewritten before a document is written against it.** Its two existing route memos are not the
portfolio paper and must not be wired as a shortcut.

---

## Ledger rows the driver should write

| id | proposed `what` | `kind` | `state` |
|---|---|---|---|
| *(update)* **AUT-042** | ⛔ REFUTED 2026-09-01. The proposed note cannot be written: "roughly a quarter" has no denominator (8/29 presenting-metastatic, 8+2 against an undefined 47, 5/13 incidence — three strata POLICY-evidence forbids summing), and "no comparator anywhere in the literature" is false (Bishop: salvage surgery p = 0.15, salvage chemotherapy p = 0.24, n = 13, uninformative). The route's own absence is refuted — see `emc-absence-claims-refuted.json` REF-01. What is worth writing is §3.1–3.3 of DOC-EMC-CARE-DELIVERY-ENDPOINT-DECISION, not this note. | `experiment` | `done` |
| *(update)* **AUT-058** | ⛔ REFUTED 2026-09-01. The consistency finding was published 2026-08-07 in DOC-EMC-RT-REAPPRAISAL over three series with Cochran Q, a pairwise z and an α/β identifiability closure — strictly more than this row proposes. The one new half, the particle census, is WRONG: carbon ion has been delivered in this histology (2 patients) and proton beam (1), in a file inside the corpus the census searched. See REF-02. | `experiment` | `done` |
| *(keep open, merge)* **AUT-064 + AUT-057 + AUT-065** | ⭐ WRITE ONE PAPER, NOT THREE NOTES. All three converge on the completeness of the first operation, measured three ways: a denominator-dependent positive-margin rate (156/134/22/40), the one covariate of 45 that holds direction across four endpoints and two cohorts, and a cohort whose upper quartile of local recurrence (63.5 mo) exceeds its own median follow-up (38 mo). Sections and the falsifiable sentence are drafted in DOC-EMC-CARE-DELIVERY-ENDPOINT-DECISION §3.1–3.3 and §4. Writing it closes `endpoint_declared` for PUB-CARE-DELIVERY. | `experiment` | `queued` |
| *(new)* **AUT-PD-xxx** | ⛔ TWO RECORDED ABSENCES ARE HARD-CODED LITERALS THAT DISAGREE WITH THEIR OWN CORPORA. Fix `emc_care_delivery_evidence.py:216` and `emc_radiotherapy_contradiction.py:191`, and the guard at `:351` in the SAME commit or the build reds on the fix. Re-grade RT-METASTASECTOMY and RT-RT-INTENSIFY, which quote them verbatim. Evidence pinned by blob SHA in `emc-absence-claims-refuted.json`. ⚠ The class matters more than the two instances: an absence recorded as a constant is unfalsifiable by the build. | `process_defect` | `queued` |
| *(new)* **AUT-PD-xxx** | PUB-CARE-DELIVERY's `why_not_written` ("needs RT-IPD-SURVIVAL to say anything quantitative") and its blocker ("never extracted into the registry") are both false as of 2026-09-01; four quantitative artifacts landed since, extracted into `research/modalities/` because the registry is byte-frozen inside a DOI deposit. Amend both, and amend PUB-LOCOREGIONAL's claim clause "had never assessed any of it". | `process_defect` | `queued` |
| *(new)* **AUT-PD-xxx** | `lint_citations` is red on the sprint tree: 3 NEW unanchored PMIDs (24555529, 28698435, 36568164) in `research/autonomy/sprint-2026-09-01/S16-NEGATIVES.md`. Anchor in `citation-provenance-ledger.json` or remove from prose before the driver's preflight. | `process_defect` | `queued` |
