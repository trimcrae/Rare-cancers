---
id: DOC-SPRINT-S18-FALSE-ABSENCES
title: "S18 — two false absences corrected, and the mechanism that made them unfalsifiable"
level: L3
kind: memo
status: live
date: 2026-09-01
audience: [autonomous research agents, maintainers]
purpose: "The findings record of sprint seat S18-FALSE-ABSENCES — what it measured, what it changed, and what it could not do. Written before the seat returned, so a seat that dies costs its own work and nothing else."
scope: "One seat of the 2026-09-01 sprint, bounded by the owned-paths list in its own prompt. It reports; it does not decide what lands."
last_verified: 2026-09-01
---

# S18-FALSE-ABSENCES — two recorded absences were false against their own corpora; both are corrected and neither can be re-typed

**Item(s):** the driver's S18 assignment; the `AUT-PD-xxx` row S15 proposed
**Owned paths:** `research/modalities/emc_radiotherapy_contradiction.py` + `emc-radiotherapy-contradiction.json`,
`research/modalities/emc_care_delivery_evidence.py` + `emc-care-delivery-evidence.json`,
`research/modalities/tests/test_emc_radiotherapy_contradiction.py`,
`research/modalities/tests/test_emc_care_delivery_evidence.py`, this file
**Started/Finished (UTC):** 2026-09-01T19:25Z / 2026-09-01T20:05Z

## Verdict

**FIXED.** S15's finding is confirmed in full, from the primary source read in this seat's own
hands rather than from S15's record. Both false values are corrected, both are now **derived from
committed corpus quotes pinned by blob SHA** instead of typed, the guard that locked the wrong
answer in is replaced by one that binds to the evidence, and all four mutations that would
reintroduce the defect go red. The sweep found **one further instance of the class** (not mine to
fix) and **one candidate that was checked at $0 and holds**.

---

## What I measured

### 1 · The primary source, read directly — S15 is right on every part

⛔ I did not take S15's word for any of it. I fetched the corpus file myself through the GitHub
contents API, `ref refs/heads/literature-cache`, at branch commit `0eac3e3aaa5b3e02c258611588e20162a7996515`.
**No git write command was run and the branch was not checked out.**

Both paths return the **same blob**, `79a8c197243ff4202a713d437def379c5f499a68`:

| path | corpus | absence recorded against it |
|---|---|---|
| `literature/emc-care-delivery-and-classification/PMC12398172.txt` | 554-record, 2026-08-09 | `"result": "ZERO records."` |
| `literature/emc-radiotherapy-2026-08-26/PMC12398172.txt` | 354-text, 2026-08-26 | `carbon_ion.found_in_this_histology: false` |

The file is Masunaga 2025 (`PMC12398172`, PMID 40885991, `10.1186/s13018-025-06245-6`,
*J Orthop Surg Res*), **171 patients pathologically diagnosed with EMC**, Japanese National Bone
and Soft Tissue Tumor Registry Database, 2002–2022. Read in the retrieved full text, verbatim:

> Results → *Patients with metastases at diagnosis* (denominator: the **29** of 171 with distant
> metastases at diagnosis): **"Eight patients (27.6%) underwent metastasectomy, including six,
> one, and one who underwent lung, bone, and lymph node resections, respectively."**

> Results → *Patients without metastases at diagnosis* (denominator: the **8** of 142 localized
> patients who did not undergo surgery): **"Of the eight patients who did not undergo surgery, two
> received carbon ion therapy, one received proton beam therapy, and one received conventional
> radiotherapy."**

⭐ **The blob identity is the discriminating observation.** Two different corpora invites the
reading that each simply lacked the paper. It does not — one identical file sits in both.

⛔ **And the same paper closes the outcome question in the same breath**, which is what keeps the
correction from becoming an overclaim: *"For the prognostic analysis, eight patients who did not
undergo surgery were excluded, and the remaining 134 patients were included."* No local control,
survival or toxicity figure attaches to any of the four non-surgical patients. For metastasectomy,
the 29-patient cohort's survival is reported split by advanced-stage **chemotherapy** and never by
whether a metastasectomy was performed.

### 2 · The mechanism, verified in the code rather than inferred

Both values were string/boolean literals in their generators, and neither generator ever read the
corpus it named:

```
research/modalities/emc_care_delivery_evidence.py:216      "result": "ZERO records.",
research/modalities/emc_radiotherapy_contradiction.py:191  "found_in_this_histology": False,
research/modalities/emc_radiotherapy_contradiction.py:351  if CARBON_ION["found_in_this_histology"] is not False:
                                                    :352      errs.append("the carbon-ion finding has flipped without its search being redone")
```

⛔⛔ **THE GUARD WORKED EXACTLY AS DESIGNED, ON A VALUE THAT WAS ALREADY WRONG.** It was written
to stop an unexamined flip; because it bound to the *answer* rather than to the *evidence*, it
also stopped the correction. `emc_care_delivery_evidence.py` had **no structural guard at all** —
its `check()` compared the artifact against `build()` and nothing else, which is structurally
incapable of catching a wrong input: a wrong literal reproduces perfectly.

⛔ **A third copy of the same wrong literal was in the test suite.**
`test_emc_radiotherapy_contradiction.py::test_the_carbon_ion_finding_records_how_it_was_searched`
asserted `ci["found_in_this_histology"] is False`. Value, guard and test all agreed with each
other while all three disagreed with the corpus — this is the one-of-a-pair defect class with a
third member.

⚠ **What is NOT established, and I did not guess it:** how the original search failed. Both values
are literals, so **no search execution is on record**. What is established is that the recorded
value disagrees with a file in the corpus it names.

### 3 · The carbon-ion case is worse, and I re-read the artifact to confirm why

The pre-correction artifact did not miss the sentence — it **considered and rejected it**:

> `⚠_a_search_summary_suggested_otherwise_and_was_not_used`: *"A web-search synthesis reported that
> 'two received carbon ion therapy, one received proton beam therapy' in a large clinical series.
> Read against the sources, that belongs to EXTRACRANIAL CHONDROSARCOMA generally, not to this
> histology… An AI search summary is a lead, never a citation."*

That is verbatim Masunaga, whose entire cohort is 171 pathologically diagnosed EMC patients.
**The lead was right and the verification reached the wrong source.** ⭐ The rule it was refused
under is correct and is retained unchanged in the corrected record; the error was recording a
refused lead as a *measured absence* rather than as an *unresolved lead*.

⛔ **And the census's own text shows the scope error.** It reads: *"354 open-access full texts…;
228 mention extraskeletal myxoid chondrosarcoma. The 2025 comprehensive EMC review in that corpus
(Remiszewski et al., PMC12504171) contains no occurrence of 'carbon' at all."* The second sentence
is a term count over **one document**; the verdict drawn from it was scoped to all 354.

### 4 · Gates I ran (scoped to my change, per charter §6)

| gate | result |
|---|---|
| `python3 research/modalities/emc_radiotherapy_contradiction.py --check` | **OK** (2 estimates, 3 case reports, 3 primary / 2 secondary) |
| `python3 research/modalities/emc_care_delivery_evidence.py --check` | **OK**, artifact matches the generator |
| `pytest` on both owned test files | **40 passed** (13 care-delivery, 27 radiotherapy) |
| `research/manuscripts/lint_consistency.py` | **0 ERROR across 26 target files** |
| `research/manuscripts/lint_claims.py` | **0 ERROR**, 170 WARN across 129 files — none on my paths |
| PubMed re-run of the third-candidate nulls (§7) | both reproduce, `total_count: 0` |
| `research/manuscripts/lint_citations.py` | ⛔ **exit 1 — and NOT mine.** All three errors are `research/autonomy/sprint-2026-09-01/S19-TRABECTEDIN.md:277,396`, a TYPE CLAIM WITH NO CACHED METADATA on PMID 27418251. ⚠ **This supersedes S15's diagnosis**, which named S16's three unanchored PMIDs — those no longer appear. Neither my findings file nor either artifact contributes an error; PMID 40885991 is already anchored in the provenance ledger. Driver: preflight stays red until S19's PMID gets a row in `citation-article-types.json` (fetchable at $0 via the PubMed MCP `get_article_metadata`). |

### 5 · ⭐ Mutation-tested, in a scratch copy, never the live tree

Charter §7 and CLAUDE.md §6. Each generator and its artifact were copied to
`scratchpad/mut-rt/` and `scratchpad/mut-cd/`; the live tree was never mutated.

| mutation | result |
|---|---|
| `emc_radiotherapy_contradiction`: retype `found_in_this_histology: False` | **RED** — *"is not the value its corpus quotes derive (stored False, quotes give True) — an absence in this file may not be typed"* |
| … empty `CORPUS_QUOTES` (the erasure route) | **RED** — *"records a correction but its corpus quotes no longer support it"* |
| … corrupt the pinned blob SHA | **RED** — *"blob_sha is not a 40-character git object id"* |
| … drop the no-outcome marker from the count | **RED** — *"that omission is how a count becomes an efficacy claim"* |
| `emc_care_delivery_evidence`: retype `"ZERO records."` | **RED** — *"`result` is a typed string, not the one its corpus quotes derive"* |
| … empty `CORPUS_QUOTES` | **RED** — *"carries a refutation notice but no quote supports it"* |
| … corrupt the blob SHA / gut the verbatim quote | **RED**, each with its own message |
| … flip `status` off `REFUTED` | **RED** — *"a committed quote matches its own search term but the row is not marked REFUTED"* |

⚠ **Two of these only went red after a second pass, and the first pass is the finding.** Emptying
`CORPUS_QUOTES` makes the derivation `False`, which *agrees* with a typed `False` — so deleting
the evidence silently restored the original state with every structural guard green. Both files
now carry a **ratchet**: a non-derived correction marker whose presence requires supporting
quotes. Going green now costs a visible deletion of a correction notice from a tracked file,
rather than a quiet one.

---

## What I changed

### `research/modalities/emc_radiotherapy_contradiction.py` (+ its artifact)

- **New `CORPUS_QUOTES` table**: one quote, pinned by blob SHA, with path, corpus, `read_via`,
  `read_utc`, source id, PMID, PMCID, series description, section, verbatim text, denominator and
  what the denominator means.
- **New `corpus_mentions(term)`**, documented with its asymmetry: *it can only ever turn an
  absence into a presence.* An empty return is "not in the quotes committed here", never a
  certified zero. That limit is stated in the function, the artifact and the tests.
- **`carbon_ion.found_in_this_histology` is now `bool(corpus_mentions("carbon ion"))`** — derived,
  not typed. It reads `true`.
- **New `carbon_ion.patients_reported`**: `carbon_ion: 2`, `proton_beam: 1`,
  `conventional_radiotherapy: 1`, `denominator: 8`, with `denominator_means`, an explicit
  `⛔_no_outcome_attaches_to_any_of_them`, and `⛔_do_not_compute_a_rate` (2 of 8 and 2 of 171
  answer different questions; **no rate is derived anywhere**).
- **`how_searched` retains the original census verbatim** and states why its verdict does not
  follow from it. The rejected-lead field is renamed to
  `⚠_the_lead_was_right_and_the_verification_reached_the_wrong_source` and keeps *"An AI search
  summary is a lead, never a citation"* on the record.
- **`⛔_what_is_still_UNKNOWN`** replaces the old `⛔_absence_of_evidence`: how often carbon ion is
  used in this histology is unknown; neither corpus has been recounted; the particle registries
  are not open.
- **Guard replaced.** `:351` becomes `_check_corpus_derivation()`, which fails if the stored
  verdict is not the derived one, if any quote lacks a 40-hex blob SHA / sits outside the corpus
  it names / carries a text under 40 characters / lacks `read_via`, `read_utc`, `source_id`,
  `pmid` or `section`, if a positive verdict carries no patient count, if a count carries no
  no-outcome marker, or if a recorded correction has lost its evidence.
- Module docstring rewritten for the particle question and the correction. `import re` added.

### `research/modalities/emc_care_delivery_evidence.py` (+ its artifact)

- **New `CORPUS_QUOTES`** (same shape) and **`corpus_hits(term)`** with the same documented
  asymmetry.
- **New `absence_result(term)`** — the `result` string is now *built* from the quotes.
- The `no-emc-metastasectomy-literature` row: `term_searched: "metastasectom"`,
  `status: "REFUTED"` (derived), `result` derived, `quotes` attached, `provenance` upgraded
  `[API]` → `[FT]` with a note saying why, and a non-derived
  `⭐_REFUTATION_IS_ON_THE_RECORD_2026_09_01` marker that the ratchet keys on.
- **New `_check_structure()`** — this module had none — wired into **both** `--check` and the
  write path, so a broken structure cannot be written out either.
- `corpus_quotes` added to the artifact; `pmids` now unions the quote PMIDs (PMID 40885991 is
  already anchored in `research/manuscripts/citation-provenance-ledger.json`, verified).
- Docstring gains the correction block.

### Both test files

Added 15 tests between them, covering: the verdict is derived and not typed; retyping the original
literal goes red; deleting the evidence goes red; every quote is pinned by a real blob SHA; the
quote actually contains the term the verdict turns on; a delivered-arm count may never be recorded
without its no-outcome marker; the correction states a lower bound and never a new count; and the
correction asserts no efficacy. Rewrote
`test_the_carbon_ion_finding_records_how_it_was_searched`, which had been the third copy of the
wrong literal.

⭐ **Two of my own sentences were caught by these tests and I reworded rather than loosened the
bar** (CLAUDE.md §3): *"the question of whether it should be offered has been asked of no EMC
cohort"* contained `should be offered`, a clinical-recommendation frame this repository should not
use at all — now *"no EMC cohort has been studied to find out whether the operation changes any
outcome in this disease."* And *"…that carbon ion, proton beam or radiotherapy is effective,
safe…"* contained `radiotherapy is effective`, tripping the module's pre-existing efficacy guard —
now *"…implies efficacy, safety, tolerability or appropriateness for carbon ion, proton beam or
radiotherapy…"*.

⚠ One test of my own had to be made **negation-aware**: a bare substring ban fires on the
disclaimer itself, which pressures an author to delete the disclaimer to go green. That is the
same orthogonality CLAUDE.md §6 records between claim strength and claim direction.

**Nothing else.** No git command of any kind, no ledger row, no graph file, no manuscript, no
registry file, no path outside the six listed above.

---

## ⭐ The corrected values, at exactly the weight the source supports

⛔ **Read the denominators. Neither of these is a rate, and neither says anything works.**

**Carbon ion / proton beam / conventional RT (Masunaga 2025):** among the **8** patients localized
at diagnosis who did **not** undergo surgery — out of 142 localized, out of 171 total — **2**
received carbon ion therapy, **1** proton beam, **1** conventional radiotherapy. **No outcome is
printed for any of them**: the series excludes all eight from its prognostic analysis. The honest
sentence is *"carbon-ion therapy has been delivered to patients of this histology and reported"* —
an existence proof of an arm. ⛔ Not *"carbon ion works in EMC"*, not a utilisation rate, not a
comparison, not a safety statement.

**Metastasectomy (Masunaga 2025):** **8 of the 29** patients (27.6 %) who presented with distant
metastases underwent metastasectomy — 6 lung, 1 bone, 1 lymph node. **No outcome is printed by
metastasectomy**; that cohort's survival is reported split by advanced-stage chemotherapy only.

**What survives of each original absence, narrowed rather than withdrawn:**

- *Metastasectomy:* no reachable series studies it **as an intervention against a comparator**.
  That is still RT-METASTASECTOMY's justification. What is refuted is "ZERO records", not "no
  comparative evidence".
- *Carbon ion:* **how often** it is used in this histology is UNKNOWN, and the particle registries
  are not open. What is refuted is "appears nowhere", not "is well characterised".

⛔ **I deliberately did NOT replace one unmeasured number with another.** The corpora were not
re-swept, so both corrected records state a **measured lower bound of 1** and an explicit
**UNKNOWN** total. Re-establishing a true count costs one term census over the `literature-cache`
branch and **no money** — a $0 CI job, not a purchase. A test asserts the correction says "lower
bound" and "UNKNOWN" so a later editor cannot quietly convert it into a count.

---

## ⛔ Route grades that quote the wrong values — DRIVER ACTION, not mine

I did not touch `systems/graph/*.json`. ⚠ **`systems/graph/routes.json` is already modified in
this working tree by another seat**, so these edits must be sequenced, not applied blind.

| # | file → JSON path | what it says now | what it should say |
|---|---|---|---|
| 1 | `routes.json` → `RT-METASTASECTOMY.grade.value` | *"A 554-record open-access corpus retrieved 2026-08-09 contains **ZERO EMC records matching metastasectom***… **nobody has asked the question in this histology**."* | The absence is refuted. Masunaga reports metastasectomy in 8 of 29 metastatic patients with no outcome by it. The route's justification survives as: **no reachable series studies metastasectomy against a comparator**. |
| 2 | `routes.json` → `RT-METASTASECTOMY.supporting_evidence[0].what_it_supports` | *"the **measured absence** of any EMC metastasectomy record in a 554-record open-access corpus"* | *"the absence of any **comparative** EMC metastasectomy study; the operation itself is reported (8/29, Masunaga 2025) with no outcome attached"* |
| 3 | `routes.json` → `RT-RT-INTENSIFY.grade.value` | *"…**carbon ion appears nowhere in it** across a 354-paper open-access corpus including a 2025 comprehensive EMC review."* | Carbon ion **is** reported in this histology: 2 patients, plus 1 proton beam and 1 conventional RT, among the 8 non-operated localized patients of a 171-patient registry series, **with no outcome printed for any of them**. "Arms exist; registries of them do not" still holds and is now the whole of it. |
| 4 | `routes.json` → `RT-RT-INTENSIFY.remaining_unknowns[2]` | *"carbon ion appears **not at all** in this histology across a 354-paper open-access corpus"* | Same correction. The genuine remaining unknown is **how often** and **with what result**, and the particle registries remain closed. |
| 5 | `systems/graph/artifacts.json` → `ART-RT-CONTRADICTION.note` | *"carbon ion **does not appear in this histology anywhere** in a 354-paper open-access corpus"* | ⭐ **A fifth copy of the false absence, which S15 did not find.** Same correction. |
| 6 | `systems/graph/artifacts.json` → `ART-CARE-DELIVERY-EVIDENCE.note` | *"The **one** [FT] passage is the ICD-O code enumeration in PMID 31765367."* | Now **two**: the metastasectomy quote in the absence row is `[FT]` and pinned by blob SHA. Minor, but it is a count that is now wrong. |

**Does either correction change what any manuscript currently claims?** ⛔ **No.** I grepped every
`.py`, `.mjs`, `.js` and `.json` in the repository for `found_in_this_histology`,
`absence_of_evidence` and `no-emc-metastasectomy-literature`: the only consumers outside the two
generators and their tests are the two route grades, the two `artifacts.json` notes, and S15's own
`emc-absence-claims-refuted.json`. **No manuscript, SI or deposit artifact reads either value**,
and neither PUB-CARE-DELIVERY nor PUB-LOCOREGIONAL has a `document.file` to have quoted them from.
The exposure was to the route board, not to the published record — which is the only reason this
was cheap to fix.

---

## The sweep: which other committed artifacts state a literature absence as a hard-coded literal

Method: (a) regex over every generator under `research/` and `scripts/` for absence vocabulary and
for zero/false-valued result fields; (b) a structural walk over every committed `.json` under
`research/` for strings pairing absence language with corpus/search language; (c) manual read of
each surviving candidate against its producer.

| # | artifact / generator | verdict |
|---|---|---|
| 1 | `emc-care-delivery-evidence.json` ← `:216` | ⛔ **FALSE — FIXED HERE.** |
| 2 | `emc-radiotherapy-contradiction.json` ← `:191`, guard `:351` | ⛔ **FALSE — FIXED HERE.** |
| 3 | `research/modalities/nr4a3-fusion-targets.json` ← `nr4a3_fusion_targets.py` | ⚠ **SAME CLASS, DIFFERENT FAILURE, AND STILL OPEN — NOT MY PATH.** `result` is the literal *"ZERO. Not one sentence in 2,276 retrieved documents applies a genome-wide chromatin method to an NR4A3 chimera."* The **generator** carries a retraction dated **2026-08-08** — a wider search found GSE243553 — and its own note says *"THIS FIELD IS NOT YET IN THE COMMITTED nr4a3-fusion-targets.json"* because the artifact is figure-stamped and that sandbox could not run the generator. **Measured 2026-09-01: the retraction is still not in the committed artifact** (`RETRACTED_2026_08_08` absent; the bare `ZERO.` string present) — **24 days stale.** ⭐ The committed `result` is *scoped* ("in 2,276 retrieved documents") so it is not false as written; what is missing is the retraction of the inference drawn from it. Fix needs `nr4a3_fusion_targets.py` re-run **together with** `nr4a3_fusion_targets_figures.py` to keep the figure stamp. |
| 4 | `research/literature/emc-perfusion-myxoid-search-2026-08-27.json` | ✅ **CHECKED AT $0 AND IT HOLDS.** Same shape (a null with no machine-checkable receipt, transcribed from executed queries), so I re-ran both queries through the PubMed MCP today rather than assume. `(isolated limb perfusion OR isolated limb infusion) AND (extraskeletal myxoid chondrosarcoma OR myxoid chondrosarcoma)` → `total_count: 0`; `extraskeletal myxoid chondrosarcoma AND perfusion` → `total_count: 0`. Both query translations confirm PubMed expanded to the `chondrosarcoma extraskeletal myxoid` Supplementary Concept, so the artifact's "not a term-spelling artefact" note is correct. **No defect.** |
| 5 | `research/modalities/hemcss-label-priorart.json` | ✅ No defect of this class. Self-labelled `INCOMPLETE`, scoped *"found IN THE SEARCHES"*, with `searches_run` carrying per-query outcomes. |
| 6 | `research/modalities/panagopoulos-elink-probe.json` | ✅ **Exemplary.** Carries a positive/negative control gate and states *"an unproven instrument cannot certify an absence."* |
| 7 | `research/modalities/v18_lysine_reference_precheck.py:338` | ✅ **The in-repo reference implementation.** `load_corpus` actually reads `literature/<slug>/_index.json` and reports a missing corpus as `loaded: False` with a reason **"and NEVER as zero records"** — verbatim. This is the pattern the two broken files should have followed. |

⭐ **The class, stated for the driver:** *an absence recorded as a constant is unfalsifiable by the
build*, and a `--check` that compares a generator to its own output is structurally incapable of
catching it. The general fix is the one applied here — bind the verdict to committed evidence
pinned by a content hash, and make the guard fail on missing evidence rather than on a changed
answer.

---

## What I could not do, and what it is actually waiting on

| item | what it is waiting on — checked, not assumed |
|---|---|
| Recount `metastasectom*` across the 554-record corpus and `carbon` across the 354-text corpus | **Not blocked, not free of latency.** The corpus lives on `literature-cache`, which this seat may not check out (charter §1). A term census is a $0 CI job or a `git fetch` the driver can run. Both artifacts state the count as UNKNOWN with a measured lower bound in the meantime, which is the honest interim state rather than a placeholder. |
| Correct the four route-grade strings and the two `artifacts.json` notes | `systems/graph/*.json`, not my path — and already modified by another seat this wave. Exact paths and replacement text are in the table above. |
| Land the `nr4a3-fusion-targets.json` retraction (sweep #3) | `nr4a3_fusion_targets.py` and its artifact, not my path. Needs the generator **and** `nr4a3_fusion_targets_figures.py` re-run in one pass or the figure stamp breaks. |
| Establish *how* the two original searches failed | **Not establishable, and I did not guess.** Both values are literals, so no search execution is on record. |

**Nothing here is blocked on trimcrae, on spend, or on the outside world.**

---

## Ledger rows the driver should write

| id | proposed `what` | `kind` | `state` |
|---|---|---|---|
| *(new)* **AUT-PD-xxx** | ✅ DONE 2026-09-01 (S18). Two recorded medical absences were FALSE against their own corpora and are corrected: `emc-care-delivery-evidence.json` `"ZERO records."` for `metastasectom*`, and `emc-radiotherapy-contradiction.json` `carbon_ion.found_in_this_histology: false`. Both refuted by one blob, `79a8c197243ff4202a713d437def379c5f499a68` (Masunaga 2025, PMID 40885991), which sits in BOTH corpora. Both values are now DERIVED from committed corpus quotes pinned by blob SHA; the guard at `emc_radiotherapy_contradiction.py:351` — which bound to the answer and so locked the wrong one in — is replaced by `_check_corpus_derivation`; `emc_care_delivery_evidence.py` gains the `_check_structure` it never had; a third copy of the wrong literal was removed from the test suite. Eight mutations verified red in a scratch copy, including the erasure route, which needed a ratchet. 40 tests pass. | `process_defect` | `done` |
| *(new)* **AUT-PD-xxx** | Correct the four route-grade strings and two `artifacts.json` notes that quote the two refuted absences. Exact JSON paths and replacement text: `research/autonomy/sprint-2026-09-01/S18-FALSE-ABSENCES.md` → "Route grades that quote the wrong values". ⚠ `routes.json` is concurrently modified this wave; sequence, do not apply blind. | `process_defect` | `queued` |
| *(new)* **AUT-PD-xxx** | ⚠ SWEEP RESULT, THIRD INSTANCE, 24 DAYS STALE. `nr4a3-fusion-targets.json` still carries the bare literal `"ZERO. Not one sentence in 2,276 retrieved documents…"`; the 2026-08-08 retraction of the inference (GSE243553) exists ONLY in `nr4a3_fusion_targets.py` and has never reached the committed artifact, because the artifact is figure-stamped and the sandbox that wrote the retraction could not run the generator. Measured 2026-09-01: `RETRACTED_2026_08_08` absent from the artifact. Re-run the generator AND `nr4a3_fusion_targets_figures.py` in one pass. ⛔ The committed `result` is scoped and therefore not false as written — what is missing is the retraction. | `process_defect` | `queued` |
| *(new)* **AUT-PROP-xxx** | Term census over `literature-cache` for `metastasectom*` (554-record corpus) and `carbon` (354-text corpus), so both corrected records can replace a measured LOWER BOUND with a measured count. $0 — a CI job or a `git fetch` plus grep. Until it runs, both artifacts correctly say UNKNOWN, and a test enforces that they do. | `experiment` | `queued` |
| *(refutes a worry, not a row)* | `research/literature/emc-perfusion-myxoid-search-2026-08-27.json` was checked as a same-class candidate and **HOLDS**: both PubMed queries re-run 2026-09-01 return `total_count: 0`, with query translations confirming Supplementary-Concept expansion. No action. | — | — |
