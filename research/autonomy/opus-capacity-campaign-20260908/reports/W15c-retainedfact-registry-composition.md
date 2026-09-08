> Collected by the campaign coordinator from this worker's in-response draft.
> Per-child runtime model evidence from the child transcript: `"model":"claude-opus-5"` (OBSERVED).

---

Ran, mutated, and quantified. Writing the report now.

---

## Worker

**W15c** — cross-lane integration, lanes 13 × 15. Composition test of W15's `RetainedFact` invariants against the artifacts W13 audited.

**Model evidence — SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I report myself as Claude Opus 5 (`claude-opus-5`), from my own system context. No environment variable in this container names a served model; the coordinator must extract the runtime model from the transcript. I do not assert it as observed fact.

`date -u` at start: `Tue Sep  8 02:18:31 UTC 2026`. At end: `Tue Sep  8 02:24:—` (final call below).

`env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` (verbatim; I filtered out only the long `*proxy*` host lines, nothing else changed):

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

**Tree state.** `git rev-parse HEAD` → `b9a0257e6acff53ad22535cf2adf261313e0b250`, *not* the frozen `92abbcb…` named in the brief — the coordinator has since committed two batches of worker reports. I verified the file under test is byte-identical between the two commits:

```
$ git diff --stat 92abbcb905cacf07f14b238db50d1b98f6590374 HEAD -- research/data/emc-clinical-registry.json
REGISTRY_DIFF_EXIT=0        # empty diff — registry unchanged since the frozen commit
```

I wrote nothing under `/home/user/Rare-cancers` (`git status --porcelain` shows only two untracked coordinator-written reports, W01c and W13b, neither mine). All execution was in `/tmp/claude-0/w15c/`. No network, no paid API, no GPU, no git write. No content-policy refusal in this lane.

---

## Question

**If W15's `RetainedFact` invariants were applied to the clinical registry's cohort and outcome records — the artifacts W13 audited — how many could be represented without loss, and how many would be REFUSED at construction?**

Open because neither lane could answer it: W15 never touched the registry (its five adapters cover four other committed files), and W13 built a *new* contract rather than testing the one lane 15 had already written. The interesting sub-question is not the refusal count but its **overlap with W13's A1–A12 inventory**: a schema that admits the defects an audit found is a schema with a hole in it.

---

## Prior-work check

Commands actually run, with what they showed:

- `rg -n -i "RetainedFact|retained_facts" --glob '!.git' -l` → **one** hit, `research/autonomy/opus-capacity-campaign-20260908/reports/W15-ingestion-normalisation-retention.md`. The dataclass exists only inside W15's report; it is not committed as code, so nothing in the tree already applies it to anything.
- `git ls-files | rg -i "retained|retention"` → `research/modalities/retention-bid.json`, `retention_bid.py`, `tests/test_retention_bid.py`. Inspected by name/path: these are the *retention-bid* modality work, unrelated to evidence-retention typing. Not a prior version of this.
- `rg -n -i "denominator_means|RetentionError" --glob '!.git' -l` → `denominator_means` appears **only** in W15's report; `RetentionError` hits are unrelated same-named exceptions in care-delivery/site-curation modules. No prior cross-lane composition test exists.
- `git diff --stat 92abbcb HEAD -- research/data/emc-clinical-registry.json` → empty.
- `head -12 …/reports/W13b-pooled-cohort-unit-resolution.md` → W13b is resolving the *unit of `n`* from the primary sources. That is the complementary question (what the unit **is**); mine is whether the schema **notices it is missing**. Not a duplicate; I make no unit determination.

`CLOSED-WORK.md` read in full. I am not replaying: the registry ICD-O paper (user-rejected), any clinical checkpoint, any unrecovered-source route (I fetched nothing), lane 11's source-index, or the frozen external-validation comment. The anthracycline case is read as W15 read it — the *motivating* case for the UNKNOWN-denominator invariant — and I extend no fact from it.

---

## Method / inputs

Read-only. Python 3.11.15 (GCC 13.3.0), Linux 6.18.44-fc-v24 x86_64, stdlib only, cwd `/tmp/claude-0/w15c`.

Inputs:
- `research/autonomy/opus-capacity-campaign-20260908/reports/W15-ingestion-normalisation-retention.md` — source of truth for the dataclass, reproduced verbatim (vocabularies, `RetentionError`, `_norm_id`, `_kind_of`, `RetainedFact.__post_init__`, `rate`). **No invariant weakened, removed or reordered.**
- `research/autonomy/opus-capacity-campaign-20260908/reports/W13-provenance-identity-contract.md` — the A1–A12 inventory.
- `research/data/emc-clinical-registry.json` — read-only; 14 cohorts, 25 citations, 4 patient rows.

Files written (scratch, outside the repo):
`/tmp/claude-0/w15c/retained_fact_core.py`, `registry_to_retained_facts.py`, `mutate.py`, `strengthened.py`, `mutant_*.json`.

### The five mapping rules the adapter had to declare

`RetainedFact` demands fields the registry does not carry, so an adapter must supply a mapping. Every rule is stated so the refusal count can be audited, and none of them invents a value the registry commits:

| Rule | Mapping |
|---|---|
| **R1 source_id** | the cohort's own `sourceId` citation, preferring `pmid` > `pmcid` > `doi`; absent citation → the `sourceId` string at kind `OTHER`. |
| **R2 tier/access** | no citation → `UNCORROBORATED`/`UNRECOVERED_OTHER`; `provenance=="secondary"` → `ABSTRACT`/`ABSTRACT_ONLY` (the tree holds the *review's* text, not the primary it reports); citation `openAccess && verified` → `FT_QUOTE`/`FULL_TEXT`; otherwise `METADATA`/`METADATA_ONLY`. |
| **R3 quote** | the first verbatim double-quoted span (≥20 chars) in the block's **own** prose field (`<key>Note`; `note` for the cohort-size record). A quote attached to a different block is not evidence for this one. |
| **R4 denominator** | a `denom` **key present** = the registry states that denominator → `STATED` with whatever value it holds. No `denom` key → `UNKNOWN`, no number. Same for cohort `n`. No value is ever substituted for a missing one. |
| **R5 denominator_means** | taken only from a committed declaration of the counting unit. The registry contains none (W13/A1), so it is `None` everywhere. |

**R2 is the load-bearing choice and I flag it now:** it is *my* rule, not W15's and not the registry's. Every refusal in the base run traces to it. See Limitations.

### Unit of analysis

47 construction attempts: one `cohort_size` record per cohort (14) plus every outcome-bearing block (33) — the four `{events, denom}` blocks (12), every `*Pct` (5), every `*Text` (9), `fiveYearDSS` (2), `medianFollowupMonths` (5). Nothing filtered. A record is **lossless** when every committed quantity lands in a typed slot (`numerator`/`denominator`); a percentage or a survival string with neither a stated event count nor a stated population has nowhere to go but the free-text `claim`, and is counted **lossy**.

---

## Result

### Tally — PRIMARY (computation over committed data, run below)

| Outcome | n | |
|---|---|---|
| Attempts (cohorts + outcome blocks) | **47** | PRIMARY |
| **CONSTRUCTED** | **34** | PRIMARY |
| … lossless | 17 | PRIMARY |
| … lossy (value survives only as prose) | 17 | PRIMARY |
| **REFUSED** | **13** | PRIMARY |

### Refusals grouped by invariant — PRIMARY

| Invariant | Refusals | Records |
|---|---|---|
| **I3** `tier FT_QUOTE requires the quoted text it claims to rest on` | **13** | `cohorts[0]` ×6 (`n`, recurrence, metastasis, diseaseDeath, fiveYearDSS, medianFollowupMonths); `cohorts[1]` ×4 (`n`, diseaseDeath, fiveYearDSS, medianFollowupMonths); `cohorts[4]` ×3 (`n`, recurrence, metastasis) |
| **I1** `denominator_status STATED with no denominator` | **0** | — |
| **I2** `a number present under a non-STATED status` | **0** | — |
| **I4** `negative numerator` | **0** | — |
| **I5** controlled-vocabulary violation | **0** | — |

**Every refusal is I3. The denominator invariant — the one the whole module exists for — fires zero times on the registry.** It fires zero times because the registry has no missing-denominator defect: every count it commits comes with a number the registry *calls* its denominator. Its defect is that nobody says what those numbers count.

The two survivors at `FT_QUOTE` tier are `cohorts[0].otherCauseDeath` and `cohorts[1].otherCauseDeath` — the only two blocks in the registry that carry a verbatim quote from the paper (the 2026-08-09 mortality-probe extractions). That is a real, if narrow, positive: the schema correctly distinguishes the two blocks somebody actually read from the eleven asserted beside them under the same open-access source.

### The 17 admitted unit-less denominators — PRIMARY

Constructed records carrying `denominator_status="STATED"` with `denominator_means=None`:

```
cohorts[0].otherCauseDeath 134.0   cohorts[2].n            117.0
cohorts[1].otherCauseDeath  29.0   cohorts[2].recurrence    83.0
cohorts[3].n                60.0   cohorts[2].metastasis    76.0
cohorts[3].recurrence       60.0   cohorts[2].diseaseDeath  99.0
cohorts[5].n   41.0   cohorts[6].n  156.0   cohorts[7].n   31.0
cohorts[8].n   26.0   cohorts[9].n  270.0   cohorts[10].n  87.0
cohorts[11].n  44.0   cohorts[12].n 42.0    cohorts[13].n  40.0
```

All 17 admitted. **`denominator_means` is a free-text `Optional[str]` with no invariant attached to it** — I confirmed this by grepping every occurrence in W15's module: the field is declared once and populated by four adapters, and `__post_init__` never reads it. So the field that would have caught W13's headline finding exists, and is optional.

Worse for A2: `cohorts[2]` (Meis-Kindblom) constructs **all four** of its records — `n=117`, recurrence `40/83`, metastasis `35/76`, diseaseDeath `18/99` — and `RetainedFact.rate` returns a live number for each of the three, from three different populations, with nothing recording that they are different. The schema is per-record; it has no way to see two records at once.

### Cross-reference to W13's A1–A12 — the gap list

| W13 | Finding | Caught by `RetainedFact`? | Why |
|---|---|---|---|
| **A1** | 14 cohort `n` with no declared unit | **NO** | `denominator_means` is optional and unchecked. 11 of the 14 constructed; the other 3 were refused for an unrelated reason (I3), so **zero** refusals are attributable to A1. |
| **A2** | Meis-Kindblom: four denominators in one row | **NO** | All four records construct; `rate` divides on all three. No cross-record invariant exists. |
| **A3** | One study, two identities (`primaryRef` free text vs `stacchiotti2019pazopanib`) | **NO — and made worse** | R2 assigns `cohorts[8]` the *review's* PMCID `PMC12504171`. There is no slot for "the primary this rests on", so the free-text identity is dropped entirely and the record reads as a clean single-source fact. Silent loss, not a refusal. |
| **A4** | Orphan resolvable citation | **NO** | Out of frame: per-record schema, no referential integrity across a file. |
| **A5** | 4 rows assert population overlap, name no counterpart | **NO — and the warning is dropped** | `contextReason` has no field in `RetainedFact`. My adapter carries `note` into `notes`; `contextReason` goes nowhere. The double-counting hazard the registry explicitly declares does not survive ingestion. |
| **A6** | `populationKey` absent on 9 of 14 = silent exemption | **NO** | No population-key slot at all. |
| **A7** | `patients[0].age=45` is an imputation from "in his 40s" | **NO** | No derivation/basis slot. Also outside this run's records (patient rows). |
| **A8** | `patients[1].sizeCm` 11.5 vs 17 (specimen vs clinical) | **NO** | No basis slot; both readings would collapse into one number. Outside this run's records. |
| **A9** | 4 patient rows with no identifier | **NO** | `source_id` identifies the *paper*, never the subject. Structurally out of frame. |
| **A10** | `Si19` submitter alias, no namespace | **NO** | Different file; `ID_KINDS` has no `SUBMITTER_ALIAS`, so an alias would be recorded at kind `OTHER` beside real DOIs. |
| **A11** | `n_runs` present, `n_biosamples`/`n_patients` absent | **NO** | Different file; and one record cannot hold three parallel counts. |
| **A12** | 12 objects counted in three unit words across files | **NO** | Cross-file. Structurally impossible for a per-record constructor. |

**Score: 0 of 12.** W15's invariants refuse none of W13's findings.

Conversely, the 13 refusals correspond to **no W13 finding**. They are a genuinely new, W15-native observation about the same file: *the registry commits counts and outcome percentages attributed to sources whose full text the tree claims to hold, while retaining no quoted text for eleven of the thirteen.* W13's validator does not check this (its 12 checks are C1–C12, all identity/provenance); W15 never looked at the registry. This is the one thing the composition produced that neither lane had.

### The smallest repair, measured rather than proposed — PRIMARY

One added invariant, a **strengthening** (`I6`: `denominator_status=="STATED"` requires `denominator_means` ∈ `("patient","tumour","specimen","biosample","sequencing_run")`), re-running the identical adapter:

| | base | with I6 |
|---|---|---|
| CONSTRUCTED | 34 | **17** |
| … lossless | 17 | **0** |
| REFUSED | 13 | **30** |
| refusals under I3 | 13 | 13 |
| refusals under I6 | — | **17** |

Every one of the 17 unit-less denominators converts to a refusal, and the registry's *lossless* record count goes to zero — i.e. **under a schema that requires a unit, the clinical registry currently supports no fully-typed quantitative record at all.** That is the honest joint measurement of A1+A2's blast radius. It also shows the fix is one line in lane 15's module and needs no registry edit; the units themselves are W13b's question and mine to route, not to answer.

---

## Validation evidence

### RUN — adapter against the real committed registry

```
$ cd /tmp/claude-0/w15c && python3 registry_to_retained_facts.py
registry            : /home/user/Rare-cancers/research/data/emc-clinical-registry.json
cohorts             : 14
attempts            : 47  (1 cohort-size record + every outcome block)
CONSTRUCTED         : 34
  ... lossless      : 17  (every committed quantity lands in a typed slot)
  ... lossy         : 17  (value survives only as prose in `claim`)
REFUSED             : 13

REFUSALS BY INVARIANT
### I3 tier FT_QUOTE requires its quote  (13)
  registry.cohorts[0].n  [cohort_size]
      tier FT_QUOTE requires the quoted text it claims to rest on
  registry.cohorts[0].recurrence  [events_denom]
      tier FT_QUOTE requires the quoted text it claims to rest on
  registry.cohorts[0].metastasis  [events_denom]
      tier FT_QUOTE requires the quoted text it claims to rest on
  registry.cohorts[0].diseaseDeath  [events_denom]
      tier FT_QUOTE requires the quoted text it claims to rest on
  registry.cohorts[0].fiveYearDSS  [percentage_only]
      tier FT_QUOTE requires the quoted text it claims to rest on
  registry.cohorts[0].medianFollowupMonths  [non_proportion]
      tier FT_QUOTE requires the quoted text it claims to rest on
  registry.cohorts[1].n  [cohort_size]
  registry.cohorts[1].diseaseDeath  [events_denom]
  registry.cohorts[1].fiveYearDSS  [percentage_only]
  registry.cohorts[1].medianFollowupMonths  [non_proportion]
  registry.cohorts[4].n  [cohort_size]
  registry.cohorts[4].recurrence  [events_denom]
  registry.cohorts[4].metastasis  [events_denom]
      tier FT_QUOTE requires the quoted text it claims to rest on

CONSTRUCTED RECORDS THAT CARRY A STATED DENOMINATOR WITH NO DECLARED UNIT
  count = 17  (W13/A1: no committed file states patient vs tumour vs specimen)
    registry.cohorts[2].recurrence  denominator=83.0  denominator_means=None  -> ADMITTED, not refused
    registry.cohorts[2].metastasis  denominator=76.0  denominator_means=None  -> ADMITTED, not refused
    registry.cohorts[2].diseaseDeath  denominator=99.0  denominator_means=None  -> ADMITTED, not refused
    [... 14 more ...]

TIER / ACCESS DISTRIBUTION OF CONSTRUCTED RECORDS
  tier  : {'FT_QUOTE': 2, 'METADATA': 25, 'ABSTRACT': 7}
  access: {'FULL_TEXT': 2, 'METADATA_ONLY': 25, 'ABSTRACT_ONLY': 7}
  denom : {'STATED': 17, 'NOT_APPLICABLE': 3, 'UNKNOWN': 14}
REAL_EXIT=0
```

(Exit 0 by design: this is an inventory, not a gate. The refusal tally is the product, and the four `I*` counts are the assertions.)

The per-record ledger printed all 47 rows; the 13 `REF` rows are exactly those listed above, and the 34 `OK` rows include the 17 `(lossy)` markers.

### RUN — mutation check, four invariants, on scratch copies

The committed registry is never written; `mutate.py` deep-copies the parsed JSON and writes `/tmp/claude-0/w15c/mutant_*.json`.

```
$ cd /tmp/claude-0/w15c && python3 mutate.py
--- M1_quote_removed: FIRED
    CONSTRUCTED         : 33
    REFUSED             : 14
    REF registry.cohorts[0].otherCauseDeath  events_denom  << I3 tier FT_QUOTE requires its quote
--- M2_denom_nulled: FIRED
    CONSTRUCTED         : 33
    REFUSED             : 14
    REF registry.cohorts[0].otherCauseDeath  events_denom  << I1 denominator_status STATED with no denominator
--- M3_negative_events: FIRED
    CONSTRUCTED         : 33
    REFUSED             : 14
    REF registry.cohorts[2].recurrence  events_denom  << I4 negative numerator
--- I2 direct: FIRED -> denominator 117.0 carried under status UNKNOWN; a number that is present is STATED or it is not present
ALL MUTATIONS FIRED
REAL_EXIT=0
```

- **M1** deletes the verbatim mortality quote from `cohorts[0].otherCauseDeathNote`. A record that constructs in the base run becomes refused; constructed drops 34→33, refused 13→14.
- **M2** keeps the `denom` key on `cohorts[0].otherCauseDeath` but sets it to `null` — the registry would then *claim* a denominator and state none. **I1, the invariant this whole exercise was about, fires.** It is live; the committed registry simply never triggers it.
- **M3** sets `cohorts[2].recurrence.events = -1`. I4 fires.
- **I2** is unreachable by mutating this registry's *shape* (rule R4 makes a present number `STATED` by construction), so it is demonstrated directly at the constructor and labelled as such rather than dressed up as a data mutation.

The check is therefore non-vacuous on all four semantic invariants, and three of the four were driven from registry data.

### RUN — strengthened schema (I6)

```
$ cd /tmp/claude-0/w15c && python3 strengthened.py
attempts            : 47
CONSTRUCTED         : 17
  ... lossless      : 0
  ... lossy         : 17
REFUSED             : 30
### I3 tier FT_QUOTE requires its quote  (13)
### I6 STATED denominator with no declared unit  (17)
REAL_EXIT=0
```

`strengthened.py` wraps the original `__post_init__` and calls it first — it adds a check, it does not replace or relax one.

### PROPOSED (NOT RUN)

- Adding `I6` to lane 15's module as a permanent invariant, plus a `unit` enum on `denominator_means`.
- Fields `RetainedFact` would need to catch anything else on W13's list: `secondary_of` (A3), `population_key` (A5/A6), `value_basis`/`derivation` (A7/A8), `SUBMITTER_ALIAS` in `ID_KINDS` (A10). None written, none run.

---

## Limitations

- **The refusal count is a function of mapping rule R2, and the sensitivity is total.** `RetainedFact` requires a `provenance_tier`; the registry commits no tier. I derived it from `openAccess && verified`. Under a laxer mapping that never assigns `FT_QUOTE`, **all 13 refusals vanish and the registry constructs 47/47**. The defensible statement is therefore: *W15's invariants refuse zero registry values on the strength of registry data alone; every refusal comes from an evidence-tier rule the adapter had to supply.* I have not smuggled that caveat into a footnote because it is the result.
- **Scope.** Cohorts and outcome blocks only, per the dispatch. `registry.patients[*]` (A7, A8, A9) and the fourth-cohort files (A10–A12) were not run through the constructor; my "NOT caught" verdicts for those six rest on reading the dataclass's field list (there is no basis, subject-identity or namespace slot), not on execution. That is a structural argument, weaker than the executed ones.
- **A refusal count is bookkeeping, not science.** Nothing here measures anything about EMC. No clinical claim, no rate, no pooled estimate, no unit determination — in particular I do **not** assert what any cohort `n` counts; that is W13b's live question.
- I read-only the registry and propose **no edit to it**. `systems/POLICY-evidence.md` protects it and the correct route for A1/A2 is its owner plus W13b, not this worker.
- 17 "lossy" constructions are a softer failure than a refusal but arguably a worse one: a percentage like `recurrencePct: 12` enters the store as prose with `denominator_status="UNKNOWN"` and *looks* like a well-formed retained fact. The schema does not distinguish "we retained this number" from "we retained a sentence containing this number".
- One under-appreciated hazard the run surfaced: nothing stops a future adapter from recording a percentage as `numerator=12, denominator=100, STATED`. That would pass every invariant and manufacture a denominator of 100 patients. I declined to do it; the schema would not have stopped me.

---

## Do the two pieces compose?

**Plainly: no.** They are orthogonal, not complementary.

W15's `RetainedFact` catches **0 of W13's 12 findings**. It was built against a *missing-value* failure mode (the anthracycline case: a denominator that was never printed) and it is genuinely good at that — M2 proves the invariant is live and would have refused the anthracycline row. W13 found a *present-but-ambiguous-value* failure mode: every number is there, and no number says what it counts. A schema whose invariants are all of the form "is this field present and consistent with that field" cannot see it, because both fields are present and mutually consistent. `denominator_means` — the one field that could have caught it — is optional and unread.

That is the useful, uncomfortable answer. It is not a criticism of either lane's execution; both ran, both produced real evidence. It is a finding about what a per-record schema can do: **a constructor can enforce that you did not lose a number. It cannot enforce that you know what the number means, and it cannot see two records at once** — which is why Meis-Kindblom's four denominators and the four unnamed population overlaps sail straight through.

The composition did produce one thing neither lane had: 13 registry values attributed to sources the tree claims to hold in full, with no retained quote behind eleven of them. And it produced one measured, one-line repair: requiring `denominator_means` converts the registry from 17 lossless records to 0, which is the true size of A1.

---

## Stop condition

Set: an executed construction attempt over every registry cohort and outcome block; a refusal tally grouped by invariant and cross-referenced to A1–A12; a named list of the W13 findings the schema misses; a non-vacuous mutation check.

**Met.** 47/47 attempted (none skipped, none coerced), 34/13 split, refusals grouped (13 × I3, 0 × I1/I2/I4/I5), all twelve A-items cross-referenced with the miss list at 12/12, four invariants shown to fire under mutation with real commands and exit codes.

---

## Tool-call and wall-clock count actually used

14 tool calls; ~11 minutes wall clock (`date -u` 02:18:31Z → 02:29Z). Under the ~40/~40 target.

---

## Next concrete action

**Lane 15 (W15's successor, not this worker): add invariant I6 to `RetainedFact` — `denominator_status=="STATED"` requires `denominator_means` from a closed unit enum — and re-run W15's own five adapters to see how many of its 6 currently-`STATED` denominators survive it.** That is the single highest-value change either lane can make, it is one line plus an enum, it is measured (17 registry refusals) rather than argued, and it is a strengthening so it cannot be mistaken for weakening a guard. The risk it must report honestly: if W15's own 6 STATED rows also fail, the store loses its only computable rates, and that is information, not a reason to make the field optional again.

Separately, and **not** mine to do: the 13 quote-less counts attributed to open-access sources belong to the registry's owner, and the unit of `n` belongs to W13b.

---

result: W15's `RetainedFact` invariants applied to all 47 cohort/outcome records of `emc-clinical-registry.json` — 34 constructed (only 17 losslessly), 13 refused, every refusal under `FT_QUOTE`-requires-quote and **zero** under the denominator invariants; the schema catches **0 of W13's 12 findings** (`denominator_means` is optional and unread), so the two pieces do not compose, while one added invariant requiring a denominator's unit would refuse all 17 unit-less rows and take the registry's lossless count to 0. Code, four firing mutations and full output at `/tmp/claude-0/w15c/`.
