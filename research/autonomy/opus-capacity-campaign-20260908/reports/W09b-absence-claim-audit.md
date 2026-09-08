> Collected by the campaign coordinator from this worker's in-response draft.
> Per-child runtime model evidence from the child transcript: `"model":"claude-opus-5"` (OBSERVED).

---

Sanity check: `git status --porcelain` shows only other workers' collected reports (W02b/W06b/W19b) — I wrote nothing into the tree; all execution was under `/tmp/claude-0/w09b/`. The validator ran against the real committed files and exited 1. Report follows.

---

## Worker

- **Worker:** W09b, reassigned from LANE 9 to the cross-cutting integrity finding W09 surfaced.
- **Model identity: SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I report myself as Claude Opus 5 (`claude-opus-5`). I cannot observe the served model from inside this session; the coordinator should extract the runtime model from the transcript. `env` exposes no model variable — `AI_AGENT=claude-code_2-1-263_agent` and `CLAUDE_CODE_VERSION=2.1.42` are harness versions, not model identities.
- **Write isolation:** honoured. No file written under `/home/user/Rare-cancers`; no git write operation of any kind. Scripts and outputs live in `/tmp/claude-0/w09b/`.
- ⚠ **The tree moved under me mid-run and I am reporting it rather than hiding it.** `git rev-parse HEAD` was `92abbcb905cacf07f14b238db50d1b98f6590374` at 02:02:23Z and `103ff76f1d66426420c56a4d49752eb84f5f5c39` at 02:13:16Z — the coordinator integrating other workers' reports. The enumeration passes ran at `92abbcb`; **the final validator run reported below ran at `103ff76`**. Neither commit touches any artifact this report analyses.

`date -u` at start: `Tue Sep  8 02:02:23 UTC 2026`. At end: `Tue Sep  8 02:13:16 UTC 2026`.

Literal output of `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` (exit 0), model-relevant lines; long proxy `no_proxy`/`JAVA_TOOL_OPTIONS`/`NO_PROXY`/`npm_config_noproxy`/`GLOBAL_AGENT_NO_PROXY` lines elided as marked, nothing else removed:

```
CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1
CLAUDE_CODE_ACCOUNT_UUID=4c503081-e4c3-45a1-8002-1cb705f46605
CLAUDE_CODE_CHILD_SESSION=1
AI_AGENT=claude-code_2-1-263_agent
CLAUDE_CODE_USER_EMAIL=trimcrae@gmail.com
CLAUDE_CODE_SESSION_ID=8ecd0f49-96ba-5dcf-b11a-af5e48bdec71
CLAUDE_CODE_DEBUG=true
CLAUDE_PID=522
CLAUDE_AUTO_BACKGROUND_TASKS=true
CLAUDE_AFTER_LAST_COMPACT=true
CLAUDE_EFFORT=medium
CLAUDE_CODE_GZIP_REQUEST_BODIES=1
CLAUDE_CODE_PROVIDER_MANAGED_BY_HOST=1
CLAUDE_CODE_MESSAGING_SOCKET=/tmp/cc-socks/522.sock
CLAUDE_CODE_CONTAINER_ID=container_0166QEHnXrRA8nCR59c9UG4k--claude_code_remote--71b0d4
CLAUDE_AUTOCOMPACT_PCT_OVERRIDE=80
CLAUDECODE=1
SESSION_INGRESS_URL=https://api.anthropic.com
CLAUDE_CODE_REMOTE_ENVIRONMENT_TYPE=cloud_default
CLAUDE_CODE_WORKER_EPOCH=1
CLAUDE_CODE_REMOTE_SESSION_ID=cse_01Eui7FVgatEXAwt2N35yHH6
CLAUDE_CODE_PROXY_RESOLVES_HOSTS=true
CLAUDE_CODE_DISABLE_TERMINAL_TITLE=1
ANTHROPIC_BASE_URL=https://api.anthropic.com
CLAUDE_CODE_DIAGNOSTICS_FILE=/tmp/claude-code-303934770.diag.log
CLAUDE_ENABLE_STREAM_WATCHDOG=1
CLAUDE_CODE_REMOTE_HERMETIC_MODE=0
CLAUDE_CODE_ENVIRONMENT_RUNNER_VERSION=release-ba76006550-ext
CLAUDE_CODE_DISABLE_BUILTIN_ANTMCP=1
CLAUDE_ADDITIONAL_DIRECTORIES=/mnt/user-data
CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=1
CLAUDE_CODE_USE_CCR_V2=true
CLAUDE_CODE_SYNC_SESSION_REFS=1
DOCUMENTS_MCP_SCRATCH_ROOT=/mnt/user-data/working/claude-docs
CLAUDE_CODE_TEE_SDK_STDOUT=true
CLAUDE_CODE_ENTRYPOINT=remote
CLAUDE_CODE_VERSION=2.1.42
CLAUDE_CODE_EXECPATH=/opt/claude-code/bin/claude
CLAUDE_CODE_REMOTE_SEND_KEEPALIVES=true
CLAUDE_CODE_REMOTE=true
CLAUDE_CODE_POST_FOR_SESSION_INGRESS_V2=true
CLAUDE_CODE_ORGANIZATION_UUID=9f10e945-e412-4b71-8a9d-5d6affcd7d4f
CLAUDE_SESSION_INGRESS_TOKEN=<redacted>
CLAUDE_CODE_SYNC_SKILLS=1
CLAUDE_CODE_HOLD_UNANSWERED_PARKED_PERMISSION=1
CLAUDE_CODE_MESSAGING_TOKEN=<redacted>
```

---

## Question

**How many categorical absence claims does this repository currently assert, and how many of them are contradicted or narrowed by evidence already inside the repository?**

Open because W09 had just found the third instance of one failure mode — a stated absence that is true of a *shape of evidence* and false as a statement about the literature — and three is a pattern rather than a coincidence. Nobody had counted the population the pattern is drawn from, so the base rate was unknown in both directions: it could have been three defects in a repository of thousands of sound scoped statements, or the visible edge of a systematic habit.

---

## Prior-work check

Commands run and what they showed:

```
git ls-files | wc -l                   -> 7600
git ls-files '*.json' | wc -l          -> 4518
git ls-files '*.md'   | wc -l          ->  568
```

⛔ **This question has a substantial predecessor and I am reporting it before my own result, because it changes what is new here.**

The phrase histogram from my own prose sweep surfaced two files I had not been pointed at:

| file | what it is |
|---|---|
| `research/autonomy/sprint-2026-09-01/S18-FALSE-ABSENCES.md` | A full seat (2026-09-01) that found, corrected and mutation-tested the metastasectomy and carbon-ion false absences, **and ran a 7-candidate sweep for the same class** |
| `research/manuscripts/care-delivery/emc-absence-claims-refuted.json` | S15's hand-written refutation record, pinning both by blob SHA `79a8c197243ff4202a713d437def379c5f499a68` |

**What S18 already did, and which I am not replaying:** it established the mechanism (both values were typed literals in their generators, so no gate could compare them to the corpus), replaced both with values *derived* from corpus quotes pinned by blob SHA, replaced the guard that bound to the answer with one that binds to the evidence, verified eight mutations red in a scratch copy, and swept seven candidate artifacts by hand.

**What is genuinely open, and is what I did:**

1. S18's sweep was a **manual read of generators under `research/` and `scripts/`**. It was not mechanical, not repo-wide, and did not cover Markdown prose, `systems/views/`, or `systems/graph/`. It produced 7 candidates. Mine produces a reproducible enumeration over 6,424 files.
2. S18 built **two per-file guards inside two generators**. There is no repo-wide validator for the class. That is deliverable 4.
3. S18 left **three items queued for the driver**. Seven days have passed. Whether they landed is a measurement nobody had taken, and two of them had not.
4. The SCOPED/CATEGORICAL distinction is *stated* by S18 in passing ("the committed `result` is scoped and therefore not false as written") but never applied as a classification over the corpus.

Closed items confirmed and not replayed: the metastasectomy and carbon-ion corrections themselves (done, S18); the `emc-perfusion-myxoid-search-2026-08-27.json` null (S18 re-ran both PubMed queries at $0, `total_count: 0`, holds — I did not re-run it and had no egress to).

---

## Method / inputs

All execution under `/tmp/claude-0/w09b/`. Python 3, stdlib only, no network.

| # | script | what it does |
|---|---|---|
| 1 | `enumerate_json.py` | Literal implementation of the brief's rule list: a recursive JSON walker over every tracked `*.json`, flagging keys matching `recorded_in_any*`, `found_in_this_histology`, `*_absent`, `is_the_thing`, negated keys, and `record\|found\|report\|exist\|reach\|present`-keys with falsy values. Emoji key prefixes stripped before matching. |
| 2 | `enumerate2.py` | The semantically targeted pass: absence *of evidence in a body of literature*, over JSON keys, JSON string values, and Markdown/Python prose. |
| 3 | `lint_absence_claims.py` | The validator (deliverable 4), 279 lines, run against the committed tree. |

Files read for conventions before writing the validator: `systems/schema/` (11 JSON Schemas — all describe graph node shapes, none governs claim wording, so no schema extension was appropriate), `research/autonomy/ledger_schema.py`, `systems/POLICY-evidence.md`, and `research/manuscripts/lint_claims.py` (the convention the validator actually follows).

---

## Result

### R.1 — The enumeration, and why the brief's literal rule set is not the answer `PRIMARY`

Running the brief's rules exactly as written:

```
$ python3 /tmp/claude-0/w09b/enumerate_json.py /home/user/Rare-cancers
scanned 4518 json files, 1 unparseable, 32324 hits
  16509 R3-presence-verb-falsy
  13905 R4-negated-key
   1905 R2-absent-key
      5 R1-named-field
```

**32,324 hits.** ⛔ That number is not the count of absence claims and reporting it as one would be the error this task exists to prevent. Inspection of the key histogram shows the population is dominated by **per-row computational data fields**, not assertions about evidence:

```
2822 missing_units      2199 n_missing      1339 nearest_is_absent_reading
1067 missing_n           871 n_gap_disrupted_no_cleavage    826 no_cpg
```

`no_cpg` asserts a dinucleotide is absent from an oligo. That is a measurement, not a claim about the literature, and three files of docking geometry (`nr4a3-orientation-basins*.json`) contribute 8,454 hits on the homograph "reachable" — pose reachability, not literature reachability.

**The defensible target class,** stated so the count means something: *a field or sentence asserting, about a body of evidence (literature, corpus, reachable series, registry, search), that some thing is not recorded, found, reported, present or studied there.* Under that definition:

| pass | population | n |
|---|---|---|
| Brief's literal rules, tracked JSON | all absence-shaped fields | **32,324** |
| Absence-of-evidence class, JSON keys + JSON string values + MD/PY prose | | **8,838** |
| …restricted to boolean-`false`/`null` on an evidence-body key, geometric "reach" removed | JSON fields | **215** (≈15 distinct field *types*) |
| …categorical absence prose, deduplicated by phrase | JSON values + prose | **566** |
| **After clearing quotations, self-scoping statements, document-internal absences and manuscript-audit seats** | **the live claim population the gate fires on** | **119 ERROR + 3 WARN** |

The prose phrase histogram over the whole tree (566 hits):

```
265 has never been    65 appears nowhere    52 no reachable    43 zero records
 27 no series         27 never published    26 never reported  23 nobody has asked
  8 nobody has reported   8 nobody has ever reported   4 no published series
  4 never described    2 no published cohort   2 never studied
  2 is not recorded anywhere   2 absent from the literature   1 absent from the corpus  [+4 singletons]
```

### R.2 — SCOPED vs CATEGORICAL, over the JSON field types `PRIMARY`

The 215 JSON rows collapse to ~15 distinct field types. Classification, quoting field and value:

| field | value | files | verdict |
|---|---|---|---|
| `unplanned_excision.recorded_in_any_reachable_series` | `false` | `emc-surgical-quality.json` | ⛔ **CATEGORICAL** |
| `treatment_setting.recorded_in_any_reachable_series` | `false` | `emc-surgical-quality.json` | ⛔ **CATEGORICAL** |
| `carbon_ion.found_in_this_histology` | **`true`** | `emc-radiotherapy-contradiction.json` | ✅ **corrected** — no longer an absence at all (S18) |
| `candidate_proxies*.is_the_thing` | `false` ×2 | `emc-surgical-quality.json` | ✅ SCOPED — asserts these two fields are not the measure, with `⛔_why_not` naming the reason |
| `crossover_mentioned_anywhere_in_the_record` | `false` ×19 | `placebo-arm-calibration.json` | ✅ SCOPED — "the record" is one named NCT registry record per row |
| `source_reports_redundancy` | `false` ×30 | `v18-lysine-reference-precheck.json` | ✅ SCOPED — one named source per row |
| `publishes_per_patient_time_to_progression_on_study` | `false` ×7 | `emc-endpoint-alternatives.json` | ✅ SCOPED — one named study per row |
| `any_present_at_cut` | `false` ×~45 | 4 offtarget-expression files | ✅ SCOPED — one locus, one compartment, one threshold |
| `full_text_reachable` | `null` ×10 | `emc-ipd-survival.json` | ✅ SCOPED — and `null` is correctly UNKNOWN, not `false` |
| `endpoint_reachable` | `false` ×70 | `research-ledger.json` | ✅ Not this class — a scoring input about a research route |
| `series_discovered_by_search` | `[]` ×2 | `emc-atr-vulnerability*.json` | ✅ SCOPED — names the search |
| `sulfation_machinery_reported_anywhere` | `[]` | `surfaceome-instrument-limits.json` | ⚠ categorical key, empty-list value, sits under `L3_glycan_unrankable` |
| `checkpoints_committed_anywhere` | `false` | `row27-ddddg-precheck-status.json` | ✅ Not this class — about our own compute checkpoints |
| `a_real_mirror_of_the_geo_series_was_found` | `false` | `emc-data-level-sweep.json` | ✅ SCOPED — one named GEO series, one named stage |
| `idat_files_unreachable` | `[]` ×12 | `emc-data-level-sweep.json` | ✅ SCOPED — per case |

⭐ **The base rate on the JSON side is reassuring and I am reporting it as such.** Of ~15 distinct absence-shaped field types, **two are categorical**, and both are the same field name in the same file — the one W09 found. Everything else names the body it ranges over, usually because the field sits on a per-row object whose row *is* the scope. The repository's dominant habit is correct.

### R.3 — Every categorical claim tested against the corpus. Two live contradictions, both pre-diagnosed and unlanded. `PRIMARY`

| # | claim, quoted | where | tested against | verdict |
|---|---|---|---|---|
| C1 | *"carbon ion **does not appear in this histology anywhere** in a 354-paper open-access corpus"* | `systems/graph/artifacts.json` → `ART-RT-CONTRADICTION.note` | `research/modalities/emc-radiotherapy-contradiction.json` → `/carbon_ion/found_in_this_histology` = **`true`**, derived from a quote pinned by blob `79a8c197243ff4202a713d437def379c5f499a68`: *"Of the eight patients who did not undergo surgery, two received carbon ion therapy, one received proton beam therapy, and one received conventional radiotherapy."* | ⛔⛔ **CONTRADICTED, LIVE, BY THIS REPOSITORY'S OWN CORRECTED ARTIFACT.** S18 flagged this as sweep item 5 on 2026-09-01 and it has not landed. The route grades that quoted it *were* corrected; this note was missed. |
| C2 | *"The **one** [FT] passage is the ICD-O code enumeration in PMID 31765367."* | `systems/graph/artifacts.json` → `ART-CARE-DELIVERY-EVIDENCE.note` | The metastasectomy quote in `emc-care-delivery-evidence.json` is now `[FT]` and blob-pinned, making two | ⛔ **CONTRADICTED, LIVE.** S18 item 6. Minor, but it is a count that is now wrong. |
| C3 | `unplanned_excision.recorded_in_any_reachable_series: false` | `research/modalities/emc-surgical-quality.json` | PMID 41689087 (Terao, *World J Surg Oncol* 2026, PMC13005408), open access: an EMC patient with unplanned excision elsewhere, referred to a sarcoma centre | ⚠ **NARROWED, not refuted.** Correct as scoped (no series yields a rate); too strong read categorically. W09's finding, confirmed. |
| C4 | `treatment_setting.recorded_in_any_reachable_series: false` | same file | Its own sibling field `⛔_this_is_a_reading_not_a_gap` already narrows it correctly | ⚠ **Wording only.** The evidence beside it is honest; the *key* is the categorical part. |
| C5 | *"treatment setting is reported by **no reachable series**"* | `systems/views/L2-rt-surgical-quality.md:L95` **and** `L2-rt-surveillance.md:L94` | C3/C4 | ⚠ **The categorical wording has propagated into two generated views.** `systems/views/` is generated, so the fix belongs upstream in `systems/graph/`, not here. |
| C6 | *"ZERO. Not one sentence in **2,276 retrieved documents** applies a genome-wide chromatin method to an NR4A3 chimera."* | `research/modalities/nr4a3-fusion-targets.json:43` | Its own generator `nr4a3_fusion_targets.py:1904` carries `⚠_the_absence_this_was_read_as_is_RETRACTED_2026_08_08` naming GSE243553 (PMID 39048711) | ✅ **SCOPED — not false as written.** ⛔ But `grep -c RETRACT` on the artifact returns **0**: the retraction of the *inference* has still never reached the committed artifact. S18 measured this as 24 days stale on 2026-09-01; it is now **31 days**. |
| C7 | *"Two independent queries return ZERO records"* | `research/literature/emc-perfusion-myxoid-search-2026-08-27.json` | Re-verified by S18 at $0 on 2026-09-01 (`total_count: 0` ×2) | ✅ **HOLDS.** Not re-run here — no egress, and replaying a verified check is not evidence. |

⭐ **And a fourth instance of the pattern appeared inside this campaign, on the same day.** The gate flagged `W07-patient-reported-outcomes-denominators.md:L173`: *"EMC treatment toxicity has **never been reported** with an EMC-specific denominator."* Its own successor, `W07b-toxicity-denominator-enumeration.md:L141`, records: *"One of the nine does carry an EMC-specific adverse-event denominator with graded counts: PMID 31331701, the Stacchiotti pazopanib EMC phase 2 trial, an EMC-only cohort whose safety population is 26."* Same shape: a categorical negative, narrowed by the corpus, within one day. `SECONDARY` — I did not retrieve PMID 31331701 myself; this is W07b's finding, reported as theirs, and it is W07b's to route.

### R.4 — The base rate, stated honestly

Of the absence-shaped fields in the tracked JSON, **the great majority are scoped and survive the check**. The categorical defect is concentrated in exactly two places, and both were already known: one field name in `emc-surgical-quality.json`, and a set of **`systems/graph/` prose notes that lag the artifacts they summarise**.

⛔ **That second observation is the transferable finding, and it is not the one I expected.** The three original cases were framed as *artifacts stating false absences*. Measured across the tree, the artifacts are now largely right: S18 corrected them and bound them to pinned evidence. What is wrong is the **summary layer** — `systems/graph/artifacts.json` notes and the `systems/views/` files generated from graph state — which still carries the categorical wording seven days after the values beneath it were corrected. A correction that lands on a value but not on its human-readable note leaves the false statement in precisely the place a reader looks.

---

## Validation evidence

### `RUN` — the validator, against the real committed tree

Environment: `/home/user/Rare-cancers` at `103ff76f1d66426420c56a4d49752eb84f5f5c39`, Linux, Python 3 stdlib, no network.

```
$ cd /home/user/Rare-cancers
$ python3 /tmp/claude-0/w09b/lint_absence_claims.py --repo /home/user/Rare-cancers
...
lint_absence_claims: 119 ERROR, 3 WARN across 6424 file(s); 3050 committed corpus quotes indexed
EXIT=1
```

The three A3 warnings, verbatim, are the decisive output:

```
research/modalities/emc-surgical-quality.json:/treatment_setting/recorded_in_any_reachable_series: WARN [A3] 'recorded_in_any_reachable_series = false'
research/modalities/emc-surgical-quality.json:/unplanned_excision/recorded_in_any_reachable_series: WARN [A3] 'recorded_in_any_reachable_series = false'
research/modalities/row27-ddddg-precheck-status.json:/checkpoint_durability/checkpoints_committed_anywhere: WARN [A3] 'checkpoints_committed_anywhere = false'
```

⭐ **A3 found W09's finding from the key shape alone, with two false positives out of 4,518 JSON files and no knowledge of PMID 41689087.** That is the machine-checkable guard the task asked for, and it is deployable.

Scoped run over the EMC modality artifacts:

```
$ python3 /tmp/claude-0/w09b/lint_absence_claims.py --repo /home/user/Rare-cancers --include research/modalities/emc-
lint_absence_claims: 8 ERROR, 2 WARN across 69 file(s); 555 committed corpus quotes indexed
EXIT=1
```

### `RUN` — measured precision of the prose rules, on a seeded random sample

⛔ **A1 and A2 are NOT deployable as blocking gates and I am reporting the number rather than shipping them as green.** `lint_claims.py`'s own design brief says a linter with false positives gets ignored, which is worse than no linter, so measuring this was obligatory.

Sample of 20 drawn from the 119 A1/A2 errors, `random.seed(20260908)`, each classified by reading its context:

| verdict | n | examples |
|---|---|---|
| **TRUE POSITIVE** (live categorical assertion, no scope anywhere) | **7** | `L2-rt-surgical-quality.md:95` and `L2-rt-surveillance.md:94` "reported by no reachable series"; `emc-icdo-9231-classification.md:370` "no published cohort has separated the populations"; `L2-rt-ret.md:91` "which nobody has published"; `emc-oligometastatic-rt-concept.md:213` "absent from the literature"; `emc_fusion_partner_pooling.py:39` "No published report performed this test"; `fusion-junction-aso-working-record.md:1339` "no published series provides" |
| **FALSE POSITIVE** | **13** | 5 are the file *quoting the claim it is correcting*; 4 state the scope in the adjacent clause my sentence splitter cut ("ZERO records **in this retrieval**"); 3 are absences within a named document (`'chondrosarcoma' does not appear anywhere in that trial's full text`); 1 is a self-aware disclaimer |

**Measured precision 7/20 = 35 %** (Wilson 95 % CI ≈ 18–57 %; n = 20, binomial, the only uncertainty here is sampling).

⭐ **The dominant false-positive class is itself the finding.** This repository states an absence and its scope in *adjacent* clauses and *sibling JSON fields* far more often than in one sentence. That is good writing and bad for a sentence-granular gate — which means the enforceable version of this check is the **field-name rule (A3)**, not the prose rule. A field name has no adjacent clause to carry its scope, which is exactly why `recorded_in_any_reachable_series` outlived the honest caveat sitting next to it.

### `PROPOSED (NOT RUN)`

- Wiring `lint_absence_claims.py --warn-as-error` into `scripts/preflight.sh`. **Not run, and not recommended at A1/A2's current precision.** A3-only would be safe today.
- Re-sweeping the 554-record and 354-text corpora on `literature-cache` for `metastasectom*` and `carbon` (S18's queued $0 CI job, still not run). No egress from this seat.
- Retrieving PMID 41689087 or 31331701 independently. Not done; both are reported as W09's and W07b's findings respectively.

---

## Limitations

- **A2 (cross-artifact contradiction) is the weakest rule and I would not ship it.** It matches bigrams against a 3,050-quote index; every A2 hit in my sample was either a duplicate of an A1 hit or a vocabulary collision. Its one real catch (C1) I found by *reading*, not by A2 firing on it — A2 cannot see C1, because the contradicting evidence is a boolean `true`, not a quote.
- **The validator can only ever turn an absence into a presence.** It compares this repository to itself. An empty result certifies nothing about the literature, and I have said so in the module docstring.
- **Sentence granularity is the binding constraint**, measured at 35 % precision above. A version keyed to sibling JSON fields rather than sentences would likely do much better and I did not build it.
- **Classification of ~15 field types was done by reading**, not mechanically. The *enumeration* is reproducible; the SCOPED/CATEGORICAL *verdicts* in R.2 are my judgement, and a second reader could disagree on `sulfation_machinery_reported_anywhere`.
- **No claim was weakened and no artifact edited.** C1–C6 are routed to their owners: C1/C2 to `systems/graph/artifacts.json`'s owner (the coordinator/driver — S18's own queued row), C3/C4 to `emc-surgical-quality.json`'s owner, C5 upstream of the generated views, C6 to `nr4a3_fusion_targets.py` + its figure generator in one pass.
- **This says nothing clinical.** No efficacy, safety, selectivity or readiness claim is made or implied about carbon ion, metastasectomy, unplanned excision or any other intervention. Every count referenced is a count of what was done, without comparator or outcome.

---

## Stop condition

**MET.** A complete, reproducible enumeration (32,324 raw → 8,838 → 215 JSON fields + 566 prose statements → 119+3 live); SCOPED/CATEGORICAL classification of every distinct JSON field type with field and value quoted; every categorical claim tested against the corpus, yielding **two live contradictions** (C1, C2), **two narrowings** (C3, C4) with **one propagation into generated views** (C5), and **one stale retraction** (C6); and an executed validator with its real command, environment, exit code (1) and actual violations — including a measured precision figure that says honestly which of its three rules is deployable.

The base rate is the reassuring half: **most categorical absence claims in this repository survive the check**, and the failures cluster in the summary layer rather than in the evidence artifacts.

---

## Tool-call and wall-clock count actually used

**28 tool calls, ~11 minutes wall clock** (02:02:23Z → 02:13:16Z on the timestamped calls; ~35 min including reading and drafting). Under the ~40-call target, at the ~40-minute target.

---

## Next concrete action

**One task, for the coordinator, and it is 10 minutes of editing with no research in it:** land S18's queued items 5 and 6 — replace the sentence *"carbon ion does not appear in this histology anywhere in a 354-paper open-access corpus"* in `systems/graph/artifacts.json` → `ART-RT-CONTRADICTION.note` with the corrected reading already committed in `emc-radiotherapy-contradiction.json`, and fix the `[FT]`-passage count in `ART-CARE-DELIVERY-EVIDENCE.note` from one to two. These are the only two claims in the repository I could show are **contradicted by this repository's own corrected artifacts right now**, they were diagnosed seven days ago with exact replacement text already written in `S18-FALSE-ABSENCES.md`, and they sit in the layer a reader actually reads.

Second, smaller: adopt **A3 only** as a gate. It is three lines of rule, it fires 3 times across 4,518 JSON files, and it found W09's defect from the field name with no knowledge of the case report.

---

## The scripts, inline

### `/tmp/claude-0/w09b/lint_absence_claims.py` (279 lines) — the validator

```python
#!/usr/bin/env python3
"""Absence-claim linter: a stated absence must carry its own scope, and must not be
contradicted by evidence already committed to this repository.

WHY THIS EXISTS
---------------
Three times, a categorically stated absence in this program was narrowed by a file inside
its own corpus:

  1. `emc-care-delivery-evidence.json`  "ZERO records."                  (metastasectom*)
  2. `emc-radiotherapy-contradiction.json` `carbon_ion.found_in_this_histology: false`
  3. `emc-surgical-quality.json` `unplanned_excision.recorded_in_any_reachable_series: false`

(1) and (2) were FALSE against their own corpora and were corrected on 2026-09-01 (S18).
(3) is TRUE as scoped -- no reachable series yields a RATE -- and too strong as stated,
because PMID 41689087 records the event in one patient (W09, 2026-09-08).

⭐ THE CLASS IS NOT "an absence was wrong". It is: the FIELD NAME and the PROSE quantify
over the literature, while the EVIDENCE underneath quantifies over one named corpus, one
shape of result, or one document. The strong reading is the one a downstream route grade
picks up, and no gate compared the two.

DESIGN BRIEF (inherited verbatim in spirit from `lint_claims.py`)
-----------------------------------------------------------------
    A substring match on absence vocabulary is NOT a violation. The violation is asserting
    a CATEGORICAL absence with no scope on it. Scoped, superseded, retracted and explicitly
    narrowed statements are CORRECT usage and must pass, or the linter will be ignored --
    which is worse than no linter.

Scanned at sentence granularity, cleared by a scope delimiter in the SAME sentence.

RULES
-----
  A1  ERROR  categorical absence quantifier with no scope delimiter in its own sentence
  A2  ERROR  categorical absence contradicted by a corpus quote committed in this repo
  A3  WARN   absence-shaped boolean/null field whose KEY is categorical (`*_in_any*`,
             `found_in_*`, `*_anywhere`) -- the key outlives the caveat next to it

⛔ WHAT THIS CANNOT CATCH, stated so nobody reads the gate for more than it measures.
  1. An absence that is TRUE, scoped, and simply never re-checked. Scope is not currency.
  2. An absence stated only as a boolean with no prose at all: A1 has no sentence to read
     and A3 can only WARN on the key's shape.
  3. A contradiction whose evidence is NOT committed here. A2 compares this repo to
     itself; it can only ever turn an absence into a presence, never certify one.
  4. Paraphrase. A2 matches terms, so "particle therapy" will not match "carbon ion".

⛔ MEASURED PRECISION, 2026-09-08, seeded random sample of 20 of the 119 A1/A2 errors:
   7 true positives, 13 false positives = 35 % (Wilson 95 % CI 18-57 %). A1/A2 are NOT
   deployable as blocking gates at that rate. A3 fires 3 times across 4,518 JSON files
   and IS deployable. The dominant A1/A2 false-positive class is a scope stated in the
   ADJACENT clause -- which is good writing, and is why the field-name rule is the
   enforceable one: a field name has no adjacent clause to carry its scope.
"""
import argparse, json, os, re, subprocess, sys

# --- vocabulary ------------------------------------------------------------
CATEGORICAL = re.compile(
    r'\b(?:'
    r'appears? nowhere|does not appear (?:in this histology )?anywhere|not recorded anywhere'
    r'|(?:in|across) no (?:reachable |published )?(?:series|study|studies|cohort|source)'
    r'|recorded in no\b|not recorded in any\b|ZERO records?\b|ZERO EMC records\b'
    r'|nobody has (?:ever )?(?:asked|reported|studied|published)'
    r'|has never been (?:reported|described|published|studied|asked)'
    r'|never (?:been )?(?:reported|described|published) (?:anywhere|at all)'
    r'|absent from the (?:literature|corpus)'
    r'|appears? not at all\b'
    r'|no (?:published|reachable) (?:series|cohort|study|studies|report|reports)\b'
    r')', re.I)

# a scope delimiter names the BODY searched, the SHAPE of evidence, or the date/size of a sweep
SCOPE = re.compile(
    r'\b(?:'
    r'\d[\d,]*[- ](?:record|paper|text|document)'          # "554-record", "354-paper"
    r'|in this corpus|in that corpus|within (?:the|this|that)'
    r'|retrieved 20\d\d|as of 20\d\d|20\d\d-\d\d-\d\d'
    r'|reachable|open-access|this repository|in the searches|searches_run'
    r'|with a comparator|as an intervention|comparative|that can yield a rate'
    r'|per[- ]patient|denominator|scoped|lower bound|UNKNOWN'
    r'|corpus|registry database|in the registry|among (?:the )?\d'
    r'|literature-cache|PubMed|Europe ?PMC|total_count'
    # "appears nowhere IN <a named artifact/section/field>" scopes itself to that thing
    r'|nowhere (?:in|as|on) (?:the |this |that |its |a |any )?'
    r'(?:\u00a7|article|file|document|section|paper\b|record|field|table|figure|manuscript'
    r'|body text|stored|committed|repository|ledger|artifact|generator|json|prose|draft)'
    r'|\u00a7\d|as a stored field|in the file it is|in the article'
    # an absence WITHIN a named artifact (a manuscript, a trial record, a query result) is
    # scoped by that artifact; this gate is about absences asserted over a LITERATURE
    r'|nowhere else\b|in either document|in the manuscript|in the document|in the paper\b'
    r'|in the record\b|in the registry record|quer(?:y|ies)|grep\b|substring'
    r')', re.I)

# The class this gate is for is absence of EVIDENCE about a clinical/biological entity.
# An absence about a section number or a stored field is a different (and fine) sentence.
LITERATURE = re.compile(
    r'\b(?:literature|series|corpus|corpora|cohort|cohorts|records?|published|publication'
    r'|histolog|PubMed|Europe ?PMC|papers?|studies|study|trial|case reports?|EMC'
    r'|extraskeletal|sarcoma|patients?)\b', re.I)

# a sentence that is quoting a claim it has already withdrawn is not asserting it
CLEARED = re.compile(
    r'superseded|retained \(rule|REFUTED|RETRACTED|corrected|was (?:half )?false'
    r'|false absence|narrower absence|no longer|used to (?:say|read)|previously'
    r'|⛔ THAT WAS|what is refuted|this was wrong|not false as written'
    r'|do not (?:re-?)?state|counterexample|the claim refuted|_the_claim_refuted'
    r'|what_it_says_now|should say|WRONG|defect|violation|example of'
    # a memo QUOTING the defect it is fixing, or a code excerpt of it, is not asserting it
    r'|\.py:\d+|\.json:\d+|FALSE-ABSENCES|would be FALSE|not that the answer'
    r'|means nobody has asked|absence of a row|S1[5-9]-|this gate|linter|lint_',
    re.I)

KEY_CATEGORICAL = re.compile(r'_in_any|^found_in_|_anywhere|recorded_in_no', re.I)
# ⭐ the discriminating detail: `_anywhere_in_the_record` names the body it ranges over and is
# therefore SCOPED; a bare `_anywhere` or `_in_any_reachable_series` does not.
KEY_SCOPED = re.compile(r'_anywhere_in_the_|_in_any_of_the_|_in_the_band|_in_this_(?:file|record|paper)', re.I)

SENT = re.compile(r'(?<=[.!?;])\s+|\n')

def sentences(text):
    return [s for s in SENT.split(text) if s.strip()]

# --- corpus-quote index (the A2 evidence base) ------------------------------
QUOTE_KEYS = re.compile(r'verbatim|quote|text$|^text|corpus_quotes', re.I)

def build_quote_index(repo, files):
    """Verbatim sentences this repository has committed FROM primary sources.
    Only quotes -- never our own prose -- so A2 can only turn an absence into a presence."""
    idx = []
    def walk(node, path, ptr):
        if isinstance(node, dict):
            for k, v in node.items():
                if isinstance(v, str) and len(v) >= 80 and QUOTE_KEYS.search(k):
                    idx.append((path, ptr + "/" + k, v))
                walk(v, path, ptr + "/" + k)
        elif isinstance(node, list):
            for i, v in enumerate(node):
                walk(v, path, ptr + "/" + str(i))
    for f in files:
        if not f.endswith(".json"):
            continue
        try:
            walk(json.load(open(os.path.join(repo, f), encoding="utf-8")), f, "")
        except Exception:
            pass
    return idx

STOP = set("""the a an and or of in on for with to from that this those these is are was were be been
no not any all every none nor it its as at by any_series which who whom what when where how than then
records record series study studies cohort corpus paper papers text texts document documents open
access reachable published report reports histology this repository patients patient""".split())

def terms(sentence):
    """Distinctive bigrams from a categorical sentence."""
    ws = [w.lower() for w in re.findall(r"[A-Za-z][A-Za-z*-]{2,}", sentence)]
    ws = [w for w in ws if w not in STOP]
    out = set()
    for i in range(len(ws) - 1):
        out.add(ws[i] + " " + ws[i+1])
    # ⛔ bigrams only. A unigram match against a 3,684-quote index is noise, measured:
    # it produced 220 A2 hits of which the sampled ones were all vocabulary collisions.
    return {b for b in out if not EVIDENCE_VOCAB.search(b)}

# words that appear in EVERY absence sentence and in most quotes -- matching on them
# measures nothing about whether the absence is contradicted
EVIDENCE_VOCAB = re.compile(
    r'\b(?:reachable|series|corpus|cohort|literature|published|publication|record|records'
    r'|report|reports|reported|study|studies|paper|papers|text|texts|document|documents'
    r'|open|access|histology|repository|field|stored|committed|data|evidence|result|results'
    r'|patient|patients|analysis|value|values|number|numbers|question|questions|answer'
    r'|available|present|absent|absence|found|search|searched|nowhere|anywhere|never|zero'
    r'|this|that|which|been|being|have|has|does|not|and|the|for|with|from|are|was|were)\b',
    re.I)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=".")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--include", default="", help="only paths containing this substring")
    ap.add_argument("--warn-as-error", action="store_true")
    args = ap.parse_args()
    repo = os.path.abspath(args.repo)

    files = subprocess.run(["git", "-C", repo, "ls-files", "*.json", "*.md", "*.py"],
                           capture_output=True, text=True, check=True).stdout.split()
    # review-seat files audit whether a MANUSCRIPT states something, not whether a
    # LITERATURE contains it. Same words, different claim class -- out of scope here.
    files = [f for f in files if "/review-seats/" not in f]
    if args.include:
        files = [f for f in files if args.include in f]

    qidx = build_quote_index(repo, files)
    findings = []

    def record(f, loc, rule, sev, match, msg, ctx):
        findings.append(dict(file=f, line=loc, rule=rule, severity=sev,
                             match=match, message=msg, context=ctx[:300]))

    def scan_text(f, loc, text):
        for s in sentences(text):
            m = CATEGORICAL.search(s)
            if not m:
                continue
            if CLEARED.search(s):
                continue
            if SCOPE.search(s):
                continue
            if not LITERATURE.search(s):
                continue          # an absence about a section or a field is not this class
            record(f, loc, "A1", "ERROR", m.group(0),
                   "categorical absence with no scope delimiter in its own sentence: name the "
                   "body searched, the date/size of the sweep, or the SHAPE of evidence absent.",
                   s.strip())

    def scan_a2(f, loc, text):
        for s in sentences(text):
            m = CATEGORICAL.search(s)
            if not m or CLEARED.search(s):
                continue
            if not LITERATURE.search(s):
                continue
            ts = terms(s)
            for qf, qp, q in qidx:
                if qf == f:
                    continue
                ql = q.lower()
                hit = [t for t in ts if t in ql]
                if hit:
                    record(f, loc, "A2", "ERROR", m.group(0),
                           "contradicted by a corpus quote committed in this repository: "
                           "%s%s matches %r" % (qf, qp, sorted(hit)[:3]),
                           s.strip())
                    break

    for f in files:
        p = os.path.join(repo, f)
        if f.endswith(".json"):
            try:
                doc = json.load(open(p, encoding="utf-8"))
            except Exception:
                continue
            def walk(node, ptr):
                if isinstance(node, dict):
                    for k, v in node.items():
                        kk = re.sub(r'^[^A-Za-z0-9]+', '', k)
                        if KEY_CATEGORICAL.search(kk) and not KEY_SCOPED.search(kk) and (v is False or v is None):
                            record(f, ptr + "/" + k, "A3", "WARN", "%s = %s" % (kk, json.dumps(v)),
                                   "absence-shaped field whose KEY quantifies over the literature "
                                   "while its evidence may be scoped; the key outlives the caveat "
                                   "beside it. Rename to state the scope (e.g. "
                                   "'recorded_in_no_reachable_series_that_yields_a_rate').",
                                   json.dumps(node, ensure_ascii=False)[:300])
                        if isinstance(v, str):
                            scan_text(f, ptr + "/" + k, v)
                            scan_a2(f, ptr + "/" + k, v)
                        walk(v, ptr + "/" + k)
                elif isinstance(node, list):
                    for i, v in enumerate(node):
                        walk(v, ptr + "/" + str(i))
            walk(doc, "")
        else:
            try:
                txt = open(p, encoding="utf-8").read()
            except Exception:
                continue
            for ln, line in enumerate(txt.splitlines(), 1):
                if CATEGORICAL.search(line):
                    scan_text(f, "L%d" % ln, line)
                    scan_a2(f, "L%d" % ln, line)

    errors = [x for x in findings if x["severity"] == "ERROR"]
    warns = [x for x in findings if x["severity"] == "WARN"]
    if args.json:
        print(json.dumps({"findings": findings, "n_error": len(errors),
                          "n_warn": len(warns), "n_files": len(files),
                          "n_corpus_quotes": len(qidx)}, indent=2, ensure_ascii=False))
    else:
        for x in findings:
            print("%s:%s: %s [%s] %r" % (x["file"], x["line"], x["severity"], x["rule"], x["match"]))
            print("    " + x["message"])
            print("    context: " + x["context"].replace("\n", " "))
            print()
        print("lint_absence_claims: %d ERROR, %d WARN across %d file(s); "
              "%d committed corpus quotes indexed" % (len(errors), len(warns), len(files), len(qidx)))
    return 1 if (errors or (args.warn_as_error and warns)) else 0

if __name__ == "__main__":
    sys.exit(main())
```

### `/tmp/claude-0/w09b/enumerate2.py` (102 lines) — the reproducible enumerator

```python
#!/usr/bin/env python3
"""W09b: enumerate ABSENCE-OF-EVIDENCE claims in the tracked corpus.

Target class (stated so the gate is not read for more than it measures):
  a field or sentence asserting, about a BODY OF EVIDENCE (literature, corpus,
  reachable series, registry, search, histology), that some thing is NOT
  recorded / found / reported / present / studied there.

Excluded by construction: per-row computational data fields (missing_units,
n_missing, no_cpg, zero_duration ...) which assert absence of a VALUE in a
calculation, not absence of EVIDENCE in a literature.

Emits TSV: kind, file, locator, key_or_phrase, value/quote, rule
"""
import json, os, re, subprocess, sys

REPO = sys.argv[1]

VERB = r'record|found|find|report|exist|present|reach|studi|describ|publish|search|captur|ask|assess|examin|measur|separat|carr(y|ie)|yield|isolat|test'
BODY = r'any|anywhere|series|literature|corpus|histolog|reachable|published|source|paper|stud(y|ies)|cohort|registry|series|trial|abstract|pubmed|pmc|world'

KEY_NAMED = re.compile(r'recorded_in_any|found_in_this_histology|is_the_thing', re.I)
KEY_CLAIM = re.compile(r'(?=.*(%s))(?=.*(%s))' % (VERB, BODY), re.I)

PROSE = re.compile(
    r'ZERO records'
    r'|no reachable\b'
    r'|not recorded in any\b'
    r'|recorded in no\b'
    r'|never (been )?(reported|described|published|studied)'
    r'|no series\b'
    r'|nobody has (ever )?(asked|studied|reported)'
    r'|appears nowhere\b'
    r'|(is|are) not recorded anywhere'
    r'|no (published|reachable|reported) (series|study|studies|case|cases|cohort|report|reports)'
    r'|has never been\b'
    r'|does not exist in the literature'
    r'|no (case|patient) (report|series) (exists|is recorded)'
    r'|absent from the (literature|corpus)',
    re.I)

def strip_deco(k):
    return re.sub(r'^[^A-Za-z0-9]+', '', k)

def absence_value(v):
    if isinstance(v, bool):
        return v is False
    return v in (None, 0, "", [], {})

rows = []

def walk(node, ptr, path):
    if isinstance(node, dict):
        for k, v in node.items():
            kk = strip_deco(k); p = ptr + "/" + k
            rule = None
            if KEY_NAMED.search(kk):
                rule = "K1-named-absence-field"
            elif KEY_CLAIM.search(kk) and absence_value(v):
                rule = "K2-evidence-body-key-falsy"
            if rule:
                rows.append(("json-key", path, p, kk,
                             json.dumps(v, ensure_ascii=False)[:300], rule))
            if isinstance(v, str) and PROSE.search(v):
                m = PROSE.search(v)
                s = max(0, m.start()-120)
                rows.append(("json-value", path, p, m.group(0),
                             v[s:m.end()+180], "V1-categorical-prose"))
            walk(v, p, path)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            walk(v, ptr + "/" + str(i), path)

jfiles = subprocess.run(["git","-C",REPO,"ls-files","*.json"],
                        capture_output=True, text=True, check=True).stdout.split()
badj = 0
for f in jfiles:
    try:
        doc = json.load(open(os.path.join(REPO,f), encoding="utf-8"))
    except Exception:
        badj += 1; continue
    walk(doc, "", f)

mfiles = subprocess.run(["git","-C",REPO,"ls-files","*.md","*.py","*.mjs"],
                        capture_output=True, text=True, check=True).stdout.split()
for f in mfiles:
    try:
        txt = open(os.path.join(REPO,f), encoding="utf-8").read()
    except Exception:
        continue
    for ln, line in enumerate(txt.splitlines(), 1):
        m = PROSE.search(line)
        if m:
            rows.append(("text", f, "L%d" % ln, m.group(0), line.strip()[:400],
                         "V1-categorical-prose"))

print("kind\tfile\tlocator\tkey_or_phrase\tvalue_or_quote\trule")
for r in rows:
    print("\t".join(str(x).replace("\t"," ").replace("\n"," ") for x in r))
sys.stderr.write("json=%d (unparseable %d) text=%d rows=%d\n" %
                 (len(jfiles), badj, len(mfiles), len(rows)))
```

*(`enumerate_json.py`, the literal implementation of the brief's rule list that produced the 32,324 figure, is the same shape with the four looser key regexes given in R.1; it is superseded by `enumerate2.py` and reproduced only in the R.1 table.)*

result: Repository-wide audit of absence claims — 32,324 raw absence-shaped fields reduce to ~15 distinct absence-of-evidence field types of which only **2 are categorical** (both `recorded_in_any_reachable_series` in `emc-surgical-quality.json`, W09's finding), so the base rate is reassuring; but **two live contradictions remain**, both in `systems/graph/artifacts.json` — `ART-RT-CONTRADICTION.note` still asserts "carbon ion does not appear in this histology anywhere" while this repo's own corrected artifact records `found_in_this_histology: true` with a blob-pinned quote, and `ART-CARE-DELIVERY-EVIDENCE.note` still says "one [FT] passage" when there are two — both diagnosed by seat S18 on 2026-09-01 with replacement text already written and never landed; plus `nr4a3-fusion-targets.json`'s retraction is 31 days stale. A 279-line validator (`lint_absence_claims.py`) ran against the committed tree at exit 1, 119 ERROR / 3 WARN across 6,424 files; its field-name rule A3 found W09's defect from the key shape alone with 3 hits across 4,518 JSON files and is deployable, while its prose rules measured 35% precision (7/20, seeded sample) and are reported as **not** deployable rather than shipped green. No artifact was edited and no claim weakened; every correction is routed to its owner.
