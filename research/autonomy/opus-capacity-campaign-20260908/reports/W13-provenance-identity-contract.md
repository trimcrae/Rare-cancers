> Collected by the campaign coordinator from this worker's in-response draft.
> Workers are read-only on the Git working tree; the coordinator is the sole collector.
> Per-child runtime model evidence, from the child transcript: `"model":"claude-opus-5"` (OBSERVED).

---

Sanity check: the schema passes `jsonschema.Draft202012Validator.check_schema` (exit 0), the validator runs against the frozen checkout and exits 1 with 41 violations plus 1 hand-adjudicated guard, and I re-read the lane brief to confirm I stayed off the source-index lane (W11) and wrote nothing into the repository.

---

## Worker

**W13** — Lane 13: observed input/provenance or specimen-identity ambiguity in committed data, with a machine-checkable repair.

**Model evidence — SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I report myself as Claude Opus 5 (`claude-opus-5`). No environment variable in this container names a model; the coordinator must extract the served model from the transcript. I do not assert it as observed fact.

`date -u` at start: `Tue Sep  8 01:55:02 UTC 2026`. `date -u` at end: `Tue Sep  8 02:00:23 UTC 2026`.

Literal output of `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` (start; long `no_proxy`/`JAVA_TOOL_OPTIONS` lines elided by me as `[…proxy host list…]`, nothing else changed):

```
CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1
CLAUDE_CODE_ACCOUNT_UUID=4c503081-e4c3-45a1-8002-1cb705f46605
CLAUDE_CODE_CHILD_SESSION=1
no_proxy=[…proxy host list…]
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
GLOBAL_AGENT_NO_PROXY=[…proxy host list…]
ANTHROPIC_BASE_URL=https://api.anthropic.com
CLAUDE_CODE_DIAGNOSTICS_FILE=/tmp/claude-code-303934770.diag.log
CLAUDE_ENABLE_STREAM_WATCHDOG=1
CLAUDE_CODE_REMOTE_HERMETIC_MODE=0
CLAUDE_CODE_ENVIRONMENT_RUNNER_VERSION=release-ba76006550-ext
CLAUDE_CODE_DISABLE_BUILTIN_ANTMCP=1
CLAUDE_ADDITIONAL_DIRECTORIES=/mnt/user-data
JAVA_TOOL_OPTIONS=[…truststore + proxy flags…]
NO_PROXY=[…proxy host list…]
CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=1
CLAUDE_CODE_USE_CCR_V2=true
CLAUDE_CODE_SYNC_SESSION_REFS=1
DOCUMENTS_MCP_SCRATCH_ROOT=/mnt/user-data/working/claude-docs
CLAUDE_CODE_TEE_SDK_STDOUT=true
CLAUDE_CODE_ENTRYPOINT=remote
CLAUDE_CODE_VERSION=2.1.42
CLAUDE_CODE_EXECPATH=/opt/claude-code/bin/claude
npm_config_noproxy=[…proxy host list…]
CLAUDE_CODE_REMOTE_SEND_KEEPALIVES=true
CLAUDE_CODE_REMOTE=true
CLAUDE_CODE_POST_FOR_SESSION_INGRESS_V2=true
CLAUDE_CODE_ORGANIZATION_UUID=9f10e945-e412-4b71-8a9d-5d6affcd7d4f
CLAUDE_SESSION_INGRESS_TOKEN=<redacted>
CLAUDE_CODE_SYNC_SKILLS=1
CLAUDE_CODE_HOLD_UNANSWERED_PARKED_PERMISSION=1
CLAUDE_CODE_MESSAGING_TOKEN=<redacted>
```

At end the same grep (filtered to the mutable fields) returned `AI_AGENT=claude-code_2-1-263_agent`, `CLAUDE_EFFORT=medium`, `CLAUDE_CODE_VERSION=2.1.42`, `CLAUDE_CODE_ENVIRONMENT_RUNNER_VERSION=release-ba76006550-ext` — unchanged.

`git rev-parse HEAD` → `92abbcb905cacf07f14b238db50d1b98f6590374` (the frozen read commit named in the brief).

---

## Question

**Where in this repository's committed data does a specimen, patient, or accession identifier admit more than one interpretation, and can a machine-checkable contract be written that would have caught it?**

It is open because `systems/POLICY-evidence.md` is a *citation* contract and `scripts/validate-registry.mjs` enforces the citation half of it. Neither names the **unit of a count**. The word `n` appears on all 14 committed cohorts and nothing anywhere states whether it counts patients, tumours, or specimens — while the standing campaign rule is that *arrays and specimens do not imply new patients*, and the program has already been burned once (Brenca case identities unresolved).

## Prior-work check

Commands actually run:

- `git ls-files '*.json' | rg -i "evidence|cohort|specimen|sample|provenance|registry|ledger" | head -40` — 40 committed JSON evidence files, inventoried; I inspected the structures of `research/data/emc-clinical-registry.json`, `research/modalities/emc-fourth-cohort-quant.json`, `research/modalities/emc-mtap-locus-persample.json`, `research/autonomy/evidence-fus-ddit3-2026-09-05/primary-junctions.json`, `research/modalities/emc-model-junction-evidence.json`.
- `rg -n "n_patients|n_specimens|n_samples|namespace" --glob '!.git' -i` — every hit is a **molecular-dynamics** `n_samples` (`results/nr4a3-abfe/…`, `results/nr4a3-denovo/…`, `results/nr4a3-metad-analysis-r2/…`), i.e. MD frames, not biological specimens. **No committed file anywhere carries `n_patients`, `n_specimens`, or a `namespace` declaration.** That is the gap, measured rather than assumed.
- `rg -n "PRJNA1357027|SRP640302" --glob '!.git' -l` and `rg -n -i "12 (patients|cases|tumou?rs|samples|runs|specimens)"` over the fourth-cohort files.
- `rg -n "primaryRef|provenance|populationKey|stratum|evidenceQuestions|orphan|unused|\.n\b|namespace" scripts/validate-registry.mjs` — to establish what is already guarded.

`CLOSED-WORK.md` read in full. I am **not** replaying: the Brenca case-identity gate (I make no claim about Brenca identities; my one accidental brush with it was a checker false positive I removed), the source-index lane (W11's, untouched), any unrecovered-source route (I fetched nothing external), or any pooled/clinical checkpoint. The Pazopanib finding below is about **how the repository points at** the Stacchiotti 2019 record — not an attempt to recover the unrecovered full paper, and I make no rate or exposure claim from it.

## Method / inputs

Read-only inspection of the frozen checkout at `92abbcb`. Scratch execution in `/tmp/claude-0/w13/`. Nothing written under `/home/user/Rare-cancers`; no git write of any kind. Python 3.11.15; `jsonschema` 4.26.0 (used **only** to self-check the schema — the validator itself is stdlib-only). No network, no paid API, no GPU.

Primary inputs:
- `systems/POLICY-evidence.md` (386 lines, read in full) — §1.2, §1.3, §2.1, §2.3, §2.6(d), §5.
- `scripts/validate-registry.mjs` (170 lines) — the incumbent gate.
- `research/data/emc-clinical-registry.json` — 4 patient rows, 14 cohorts, 25 citations.
- `research/modalities/emc-fourth-cohort-quant.json` — PRJNA1357027 / SRP640302, 12 runs.
- `research/manuscripts/fusion-output/emc-fourth-cohort-sra-2026-08-08.md`, `research/modalities/emc-fourth-cohort-route-readout.json`.
- `systems/schema/lane.schema.json` (style reference), `research/autonomy/ledger_schema.py` (convention reference — its "a name that LOOKS LIKE a name a reader uses" design and its prospective-gate framing are what I matched).

---

## Result

### The cited ambiguity inventory

Every row is a value I read in the committed file at `92abbcb`.

| # | File · key path | Committed value | The ambiguity | Class |
|---|---|---|---|---|
| A1 | `research/data/emc-clinical-registry.json` :: `registry.cohorts[*].n` (all 14) | `134, 29, 117, 60, 49, 41, 156, 31, 26, 270, 87, 44, 42, 40` | `registry.fields` defines **15 fields, all patient-row fields** (`age`, `sex`, … `note`) and **none of them is `n`**. No file states whether a cohort `n` counts patients, tumours or specimens. `validate-registry.mjs:84` requires only `typeof c.n === "number"`. | PRIMARY (unstated unit) |
| A2 | same :: `cohorts[2]` "Long-term outcome series (Meis-Kindblom)" | `n: 117`, `recurrence.denom: 83`, `metastasis.denom: 76`, `diseaseDeath.denom: 99` | Four different denominators in one row, none equal to `n`, and no field says whether the gaps are missing data, a different unit, or sub-strata. §2.2 pools on `Σdenom`, so the headline silently uses three different populations from this row. | PRIMARY (unstated denominator) |
| A3 | same :: `cohorts[8]` "Advanced disease on pazopanib" | `sourceId: "remiszewski2025"`, `provenance: "secondary"`, `primaryRef: "Stacchiotti et al., Lancet Oncol 2019 phase 2 (n=26)"` | The same study is **also** committed as `registry.citations.stacchiotti2019pazopanib` with `pmid 31331701` / `doi 10.1016/S1470-2045(19)30319-5`. **One study, two identities in one file** — one resolvable, one free text. §1.3 says: once the entry exists, repoint `sourceId`. Nothing enforces it; `validate-registry.mjs:86-87` only checks that a secondary row has *some* `primaryRef` string. | PRIMARY (identifier admits two readings) |
| A4 | same :: `registry.citations.stacchiotti2019pazopanib` | full resolvable entry | Referenced by **no** cohort and **no** patient row, while A3 names it in prose. A resolvable id orphaned beside its own free-text shadow. (9 further citations are unreferenced but are not named in any `primaryRef`, so they are inventory, not ambiguity.) | PRIMARY |
| A5 | same :: `cohorts[5,6,9,11]` `contextReason` | `"population-overlap (US single institution; likely within SEER / US Sarcoma Collaborative)"`, `"population-overlap; percentage-only"` ×2, `"population-overlap"` | Four rows **assert an overlap and name no counterpart**. §2.3 is the double-counting rule; these rows declare the very hazard it exists for, in prose a checker cannot resolve. | PRIMARY |
| A6 | same :: `cohorts[5..13]` `populationKey` | absent on 9 of 14 | `validate-registry.mjs:113` guards overlap only `if (c.pool !== false && c.populationKey)`. Omitting the key is therefore an **exemption** from the double-counting check, not a gap in it — the failure reads as green. | PRIMARY (unguarded invariant) |
| A7 | same :: `registry.patients[0]` | `age: 45`; note: `"Age reported only as 'in his 40s' (recorded as decade midpoint)"` | A **derived value carrying no machine-readable derivation**. Anything consuming `age` sees a measurement; only a human reading the free-text note learns it is an imputation. | PRIMARY (derived value unlinked) |
| A8 | same :: `registry.patients[1]` | `sizeCm: 11.5`; field definition `"Largest tumour dimension (cm)"`; note: `"Clinical size 13x17 cm, specimen 10x11.5x7.5 cm"` | **Specimen-versus-patient measurement ambiguity, with both readings committed.** Under the clinical (in-vivo) reading the largest dimension is **17**; under the gross-specimen reading it is **11.5**. The committed value takes the specimen reading; no field records that choice. | PRIMARY (specimen identity/basis) |
| A9 | same :: `registry.patients[0..3]` | no id field on any row | Four patient rows carry **no identifier in any namespace**, so they cannot be checked for overlap against a cohort or against each other. | PRIMARY |
| A10 | `research/modalities/emc-fourth-cohort-quant.json` :: `per_run.SRR35940646.sample_alias` (and 11 more) | `"Si19"`, `"Si17"`, `"Si16"`, `"Si15"`, `"Si14"`, `"Si10"`, `"Si09"`, `"Si05"`, `"Si22"`, `"Si20"`, `"Si02"`, `"Si01"` | A **submitter-private label with no declared namespace** and no `resolves_to`. `Si19` is unique inside PRJNA1357027 and means nothing outside it. Indices run to 22 with 10 gaps, so the parent series is larger than the deposit by an unstated amount. | PRIMARY |
| A11 | same :: top level | `n_runs_in_deposit: 12`, `n_runs_read: 12`; no `n_biosamples`, no `n_patients` | The file's own `_what_this_is_not` says *"Not a patient count: runs are not samples and samples are not people"* — but that distinction exists **only as prose**. There is no machine-readable place for the specimen count or for "patient count = UNKNOWN". | PRIMARY (contract gap) |
| A12 | `research/modalities/emc-fourth-cohort-route-readout.json:12` vs `research/manuscripts/fusion-output/emc-fourth-cohort-sra-2026-08-08.md:107,114` | readout: `"Not a patient count: 12 runs are 12 tumours, and a tumour is not an outcome."` — SRA reading: `"The 12 runs are 12 distinct biological specimens"` … `"12 BioSamples is NOT the same claim as 12 patients … one patient contributing a primary and a metastasis under two Si numbers would be indistinguishable from two patients"` | **The same 12 objects are counted in three unit words across committed files** — runs, BioSamples/specimens, tumours — and only the SRA reading declares which unit was measured. The readout's *"12 runs are 12 tumours"* asserts a run→tumour equation the deposit does not establish: the SRA reading rules out replicate **runs**, not two specimens of one tumour, and a primary plus its metastasis is two tumours in one patient. | **PRIMARY (the lane's exact failure mode, cross-file)** |

One further observation, recorded but **not** made a check because it is a policy/data mismatch rather than an identity ambiguity: `POLICY-evidence.md` §3 specifies `evidenceQuestions[]` and calls the ≥2-opposing-positions rule "validator-enforced", and `validate-registry.mjs:124` does enforce it — but the committed registry has keys `['intro','dataStatus','dataStatusBanner','fields','patients','cohorts','citations']` and **contains no `evidenceQuestions` at all**. The rule is live and its subject is absent. That is UNKNOWN as to intent and belongs to whoever owns the registry.

### The repair

Two files, returned inline below for the coordinator to write:

1. **`systems/schema/identity-provenance.schema.json`** — a JSON Schema (draft 2020-12, matching `systems/schema/lane.schema.json`'s style including its `_role`/`_prose` annotation convention). It gives a home to the four things that had none: a **unit** enum where `patient`, `tumour`, `specimen`, `biosample` and `sequencing_run` are distinct objects; a **count** that must carry `value` (nullable — *null means UNKNOWN, never zero*), `unit`, and `observed`, with a required `basis` whenever `observed` is false; an **identifier** that must declare its `namespace` (`SUBMITTER_ALIAS` is in the enum precisely so `Si19` cannot be recorded as though it were public); and a **derived_value** requiring `derivation`, `source_file`, `source_key`, with a `verbatim_source_value` slot that holds **both** candidate measurements in an A8-shaped case. `cohort_identity` requires `n_patients` **and** `n_specimens` as separate counts — both required so neither is read as the other, both nullable so the requirement cannot be met by invention.

2. **`scripts/validate_identity_contract.py`** — stdlib-only (196 lines), 12 checks, run against the real committed files. Exit 0 = clean, 1 = violations, 2 = a named file is missing (UNKNOWN, never a pass).

---

## Validation evidence

### RUN — schema self-check

```
$ python3 -c "import json,jsonschema; s=json.load(open('/tmp/claude-0/w13/identity-provenance.schema.json')); jsonschema.Draft202012Validator.check_schema(s); print('SCHEMA OK, draft 2020-12')"
SCHEMA OK, draft 2020-12
EXIT=0
```
Environment: Python 3.11.15, jsonschema 4.26.0, Linux 6.18.44-fc-v24, cwd `/tmp/claude-0/w13`.

### RUN — validator against the committed tree

```
$ python3 /tmp/claude-0/w13/validate_identity_contract.py /home/user/Rare-cancers
…
TOTAL FINDINGS: 42 across 3 files (41 violations, 1 annotated guards)
REAL_EXIT=1
```

Findings by check (verbatim from the run):

```
### C1-COUNT-UNIT-UNDECLARED  (14)
### C10-ALIAS-NAMESPACE-UNDECLARED  (1)
### C11-SPECIMEN-COUNT-TRIPLE-INCOMPLETE  (2)
### C12b-UNIT-WORD-NEGATED-MENTION  (1)
### C2-DENOM-UNEXPLAINED  (3)
### C3-SECONDARY-REF-UNLINKED  (1)
### C4-ORPHAN-RESOLVABLE-CITATION  (1)
### C5-OVERLAP-UNNAMED  (4)
### C6-POPULATION-KEY-MISSING  (9)
### C7-DERIVED-VALUE-UNFLAGGED  (1)
### C8-SPECIMEN-VS-CLINICAL-BASIS  (1)
### C9-PATIENT-ROW-UNIDENTIFIED  (4)
TOTAL FINDINGS: 42 across 3 files (41 violations, 1 annotated guards)
```

Three representative violation bodies, verbatim:

```
### C3-SECONDARY-REF-UNLINKED  (1)
  research/data/emc-clinical-registry.json :: registry.cohorts[8].primaryRef
      "Advanced disease on pazopanib" names its primary only as free text 'Stacchiotti et al.,
      Lancet Oncol 2019 phase 2 (n=26)', while registry.citations.stacchiotti2019pazopanib is a
      committed resolvable entry for the same study (pmid=31331701
      doi=10.1016/S1470-2045(19)30319-5). One study, two identities in one file;
      POLICY-evidence.md §1.3 requires the row be repointed or the reason it cannot be recorded

### C8-SPECIMEN-VS-CLINICAL-BASIS  (1)
  research/data/emc-clinical-registry.json :: registry.patients[1].sizeCm
      sizeCm=11.5 with registry.fields.sizeCm = "Largest tumour dimension (cm)", while the note
      commits 2 different measurements ['10x11.5x7.5 cm', '13x17 cm'] — a clinical (in-vivo)
      reading and a gross-specimen reading give different largest dimensions and no field says
      which was taken

### C10-ALIAS-NAMESPACE-UNDECLARED  (1)
  research/modalities/emc-fourth-cohort-quant.json :: per_run.SRR35940646.sample_alias
      sample_alias='Si19' is a submitter-private label carrying no declared namespace and no
      resolves_to; it is unique only inside this deposit
```

### RUN — two precision defects in my own checker, found and reported rather than tolerated

The **first** run produced 44 findings across 5 files. Two were checker defects, not repository defects, and I fixed the checker (never the contract, and never the verdict on a real row):

1. `C7` quoted the wrong 110 characters of the note (the match was real — `"recorded as decade midpoint"` — but the excerpt started at character 0). Now it quotes the matched window: `" yr. Age reported only as 'in his 40s' (recorded as decade midpoint)."`
2. `C12` was **file-scoped** and matched any `12 <unit>` in any file that mentioned the deposit anywhere. It fired on `research/autonomy/opus-capacity-campaign-20260908/reports/W01-expression-multiomics-resources.md:102`, whose *"all 12 cases"* is **Brenca's Table 1 — a different 12 entirely**, in an **untracked** file. C12 is now restricted to `git ls-files` output (committed evidence only) and paragraph-scoped. That false positive is, ironically, the lane's own thesis biting the lane's own tool.

**⛔ One remaining check output is wrong and I am reporting it as wrong rather than adjusting the verdict.** The negation heuristic reclassified `research/modalities/emc-fourth-cohort-route-readout.json:12` from `C12` to `C12b` (an "annotated guard"), because the string `"Not a patient count:"` sits in its 60-character window. **Hand adjudication says the machine is wrong here.** The negation governs *"patient count"*; the trailing clause *"12 runs are 12 tumours"* is an affirmative equation of runs to tumours, and it is a stronger claim than anything the deposit establishes. The check's own message instructs exactly this hand review, and the review's answer is: **this is a real A12 violation misclassified by a cheap heuristic.** The honest count is therefore **41 machine violations + 1 hand-confirmed violation the machine downgraded = 42**, and the C12b classifier is a known-imprecise component, documented as such in the source.

### PROPOSED (NOT RUN)

- Integration into `scripts/preflight.sh` as an additional gate. **Not run** — the brief forbids running preflight and forbids repository writes.
- Any repair edit to the 42 flagged values. **Not run, and not mine to make**: the clinical registry is protected state under `systems/POLICY-evidence.md` and the campaign write isolation.
- Migration of any record to the schema's shape. **Not run.**

---

## Limitations

- **I did not weaken any check to make a file pass.** The validator exits 1 against the committed tree and I am reporting that as the result.
- **A contract cannot see a unit that was never written.** C1 proves 14 counts have no declared unit; it cannot tell you what the unit *is*. Resolving A1/A2 requires reading Meis-Kindblom 1999 and the other sources, which I did not do (no external fetch this run). Each of the 14 is **UNKNOWN**, not "probably patients".
- **C12's unit-word check is scoped to one deposit** (PRJNA1357027 / SRP640302) and to the literal integer 12. It is a demonstration that the class is detectable, not a repository-wide sweep. Generalising it needs the deposit's counts declared per the schema first — which is the point of the schema.
- **The C12b negation classifier is imprecise in both directions**, as the hand-adjudicated miss above shows. It must never be read as an exoneration.
- **No clinical, efficacy, safety, selectivity or prognostic claim is made or implied here.** Every finding is about how a number is *recorded*, never about whether it is *right*. Fixing all 42 would change no scientific conclusion; it would make the existing conclusions checkable.
- **The 42 violations are a census of the two files I inspected in depth plus one cross-file scan.** The other 38 committed evidence JSONs were structurally inventoried but not run through checks tailored to them — absence of findings there is **UNKNOWN, not clean**.
- The schema is a **reviewed proposal**, not adopted state. It has never been run in anger and its enum will be wrong somewhere; `ledger_schema.py`'s lesson (a schema that rejects every unknown field gets switched off) applies.

## Stop condition

**Set:** a cited ambiguity inventory of actual committed values, plus a validator actually executed against committed data with its real output. **Met.** 12 cited ambiguities (A1–A12), a schema that self-checks, and a validator that ran against the frozen checkout at `92abbcb` and exited 1 with 41 machine violations plus 1 hand-confirmed miss, across 3 committed files.

## Tool-call and wall-clock count actually used

**23 tool calls; 5 minutes 21 seconds wall clock** (01:55:02Z → 02:00:23Z). Well inside the ~40/~40 target.

## Next concrete action

**One successor, finite:** resolve A1 for the five pooled cohorts only (`cohorts[0..4]`, the rows that actually feed the §2.2 headline) by reading each source's own words for what its `n` counts, and add `nUnit` to those five rows plus a `denomNote` to the three Meis-Kindblom denominators (A2). Five rows, three notes, one source-reading pass; it is the smallest change that makes the pooled headline's denominator unambiguous, and it is bounded by exactly five documents. It requires a repository writer, which W13 is not. The remaining 33 violations are lower-value in comparison (A9's patient ids and A6's population keys are bookkeeping; A3/A4 need a decision about whether the unrecovered pazopanib primary may be pointed at, which is a judgement for the registry owner, not a defect a worker should silently "fix").

---

### `systems/schema/identity-provenance.schema.json`

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://github.com/trimcrae/Rare-cancers/systems/schema/identity-provenance.schema.json",
  "title": "IDENTITY AND PROVENANCE — what a counted thing is, and where a number came from",
  "_role": "systems/POLICY-evidence.md is the evidence contract in prose; validate-registry.mjs enforces the citation half of it. Neither names the UNIT of a count. `n` appears 14 times in research/data/emc-clinical-registry.json and nothing anywhere says whether it counts patients, tumours or specimens — while CLOSED-WORK.md's standing rule is that arrays and specimens do not imply new patients. This schema gives the unit, the namespace and the derivation a home so a reader is not required to guess and a checker is able to refuse.",
  "_prose": "systems/POLICY-evidence.md §1.3, §2.1, §2.3, §2.6(d)",
  "_scope": "Any committed record that counts biological objects or carries a number read out of another document. It does NOT re-specify citation shape (POLICY-evidence.md §1.2 owns that) and does NOT govern free energies or ensembles.",
  "$defs": {
    "unit": {
      "enum": ["patient", "tumour", "specimen", "biosample", "sequencing_run", "array", "trial_arm", "probe"],
      "description": "⛔ THE ENUM IS THE POINT. `patient` and `specimen` are different objects and a deposit that measures one does not report the other. `tumour` sits between them: one patient may contribute a primary and a metastasis, and one tumour may yield two specimens. A count whose unit is not one of these has no unit."
    },
    "count": {
      "type": "object",
      "required": ["value", "unit", "observed"],
      "additionalProperties": false,
      "properties": {
        "value": { "type": ["integer", "null"], "minimum": 0, "description": "null means UNKNOWN. It never means zero." },
        "unit": { "$ref": "#/$defs/unit" },
        "observed": { "type": "boolean", "description": "true only when the source states this count in this unit. An inference from distinct ages/sexes is observed:false, however natural the reading." },
        "basis": { "type": "string", "minLength": 5, "description": "Required when observed is false: the inference, in words, so a reader can disagree with it." }
      },
      "allOf": [
        { "if": { "properties": { "observed": { "const": false } } },
          "then": { "required": ["basis"] } }
      ]
    },
    "identifier": {
      "type": "object",
      "required": ["namespace", "value"],
      "additionalProperties": false,
      "properties": {
        "namespace": {
          "enum": ["BIOPROJECT", "SRA_STUDY", "SRA_RUN", "SRA_SAMPLE", "BIOSAMPLE", "GEO_SERIES", "GEO_SAMPLE", "SUBMITTER_ALIAS", "PMID", "PMCID", "DOI", "RRID", "LOCAL_CITATION_ID", "LOCAL_POPULATION_KEY"],
          "description": "⛔ SUBMITTER_ALIAS IS NOT A PUBLIC NAMESPACE. `Si19` is unique inside one deposit and means nothing outside it; recording it without its namespace is how a private label is later read as a global id."
        },
        "value": { "type": "string", "minLength": 1 },
        "resolves_to": { "type": ["string", "null"], "description": "The identifier in a public namespace this one denotes, where the record actually establishes the link. null = the link is not established. Absent = never asked." }
      }
    },
    "derived_value": {
      "type": "object",
      "required": ["value", "derivation", "source_file", "source_key"],
      "additionalProperties": false,
      "description": "Any number this repository computed, imputed, digitised or re-expressed rather than read verbatim. A derivation recorded only in a free-text `note` is invisible to every consumer of the field.",
      "properties": {
        "value": { "type": ["number", "string", "null"] },
        "derivation": { "type": "string", "minLength": 5, "description": "e.g. 'decade midpoint of a reported age band', 'gross specimen greatest dimension'." },
        "source_file": { "type": "string", "minLength": 1, "description": "Repository-relative path, or a citation id in LOCAL_CITATION_ID." },
        "source_key": { "type": "string", "minLength": 1, "description": "The key path or the located sentence inside that source." },
        "verbatim_source_value": { "type": ["number", "string", "null"], "description": "What the source actually says, before derivation. Where the source gives two candidate values (a clinical measurement and a gross-specimen measurement), BOTH belong here." }
      }
    },
    "cohort_identity": {
      "type": "object",
      "required": ["population_key", "n_patients", "n_specimens"],
      "description": "⛔ n_patients AND n_specimens ARE BOTH REQUIRED AND EITHER MAY BE null. Requiring both is what stops one number being silently read as the other; allowing null is what stops the requirement being met by invention.",
      "properties": {
        "population_key": { "type": "string", "minLength": 1, "description": "Required on EVERY cohort, pooled or not. validate-registry.mjs only checks overlap `if (c.pool !== false && c.populationKey)`, so an omitted key is currently an exemption from the double-counting check rather than a gap in it." },
        "stratum": { "type": ["string", "null"] },
        "n_patients": { "$ref": "#/$defs/count" },
        "n_specimens": { "$ref": "#/$defs/count" },
        "overlaps_population_key": {
          "type": ["string", "null"],
          "description": "Required when the row declares a population overlap. A row that says `contextReason: \"population-overlap\"` and names no counterpart has asserted a relation to nothing."
        },
        "primary_ref_id": { "type": ["string", "null"], "description": "The LOCAL_CITATION_ID of the primary study, when this repository holds one. POLICY-evidence.md §1.3: leave it as text until you pull it, THEN add a citation entry and repoint. Where the entry already exists and the row still names the study only in prose, the study has two identities in one file." },
        "primary_ref_unlinked_reason": { "type": ["string", "null"], "description": "Required instead of primary_ref_id when a matching citation entry exists but must NOT be pointed at — e.g. the primary is unrecovered and only its abstract is held." }
      }
    },
    "deposit_identity": {
      "type": "object",
      "required": ["identifiers", "n_sequencing_runs", "n_biosamples", "n_patients", "runs_per_biosample"],
      "properties": {
        "identifiers": { "type": "array", "items": { "$ref": "#/$defs/identifier" }, "minItems": 1 },
        "n_sequencing_runs": { "$ref": "#/$defs/count" },
        "n_biosamples": { "$ref": "#/$defs/count" },
        "n_patients": { "$ref": "#/$defs/count" },
        "runs_per_biosample": { "type": ["number", "null"], "description": "Established by counting distinct sample identifiers, not assumed. null = not established." },
        "unit_words_permitted": { "type": "array", "items": { "$ref": "#/$defs/unit" }, "description": "The units any prose about this deposit may attach to its counts. A deposit that establishes runs and biosamples does not license the word 'tumour'." }
      }
    }
  }
}
```

### `scripts/validate_identity_contract.py`

```python
#!/usr/bin/env python3
"""IDENTITY AND PROVENANCE GATE — refuse a count whose unit is guessed and a number whose
derivation lives only in prose.

Companion checker for systems/schema/identity-provenance.schema.json. The schema names the shape a
record SHOULD have; this script asks whether the records this repository ALREADY COMMITTED satisfy
the invariants behind that shape, on their current shape, so the gap is measured before anything is
migrated.

⛔ WHAT IT DOES NOT DO. It does not re-check citation shape (scripts/validate-registry.mjs owns
that), does not judge whether a number is right, and cannot see a unit that was never written.
Stdlib only. Exit 0 = no violations; exit 1 = violations; exit 2 = a file it was told to read is
missing (UNKNOWN, never treated as a pass).
"""
from __future__ import annotations
import json, os, re, subprocess, sys

REPO = sys.argv[1] if len(sys.argv) > 1 else "."
REGISTRY = "research/data/emc-clinical-registry.json"
QUANT = "research/modalities/emc-fourth-cohort-quant.json"
DEPOSIT_IDS = ("PRJNA1357027", "SRP640302")
# Units the fourth-cohort deposit record actually establishes, from its own committed statements.
DEPOSIT_UNIT_WORDS_PERMITTED = {"run", "runs", "biosample", "biosamples", "sample", "samples",
                                "specimen", "specimens", "experiment", "experiments"}
DERIVATION_PROSE = re.compile(
    r"recorded as|midpoint|estimated|imputed|back-?calculat|converted|assumed|approximat|derived",
    re.I)
DIMENSION = re.compile(r"\b\d+(?:\.\d+)?\s*(?:x|×)\s*\d+(?:\.\d+)?(?:\s*(?:x|×)\s*\d+(?:\.\d+)?)?\s*cm\b", re.I)
SURNAME_YEAR = re.compile(r"([A-Z][a-zA-Z\-]{2,})\s+et al\.?.*?((?:19|20)\d{2})")
COUNT_UNIT_IN_PROSE = re.compile(r"\b12\s+(runs?|tumou?rs?|patients?|samples?|specimens?|biosamples?|cases?|people)\b", re.I)
ACCESSION = re.compile(r"^(SRR|SRS|SRX|GSM|GSE|SAMN|PRJNA)\d+$")

V = []          # violations
def bad(code, path, keypath, detail):
    V.append({"check": code, "file": path, "key": keypath, "detail": detail})

def load(rel):
    p = os.path.join(REPO, rel)
    if not os.path.exists(p):
        print(f"UNKNOWN: {rel} not found under {REPO}", file=sys.stderr)
        sys.exit(2)
    with open(p) as fh:
        return json.load(fh)

# ---------------------------------------------------------------- registry checks
reg = load(REGISTRY)["registry"]
cohorts, patients, cites = reg["cohorts"], reg["patients"], reg["citations"]
declared_popkeys = {c["populationKey"] for c in cohorts if c.get("populationKey")}
OUTCOME_KEYS = ("recurrence", "metastasis", "diseaseDeath", "otherCauseDeath")

for i, c in enumerate(cohorts):
    kp = f"registry.cohorts[{i}]"
    lbl = c.get("label", "?")
    # C1 — a count with no unit
    if "n" in c and "nUnit" not in c:
        bad("C1-COUNT-UNIT-UNDECLARED", REGISTRY, kp + ".n",
            f'n={c["n"]} on "{lbl}" declares no unit; registry.fields defines 15 patient-row '
            f"fields and none of them is `n`, so patient / tumour / specimen is a reader's guess")
    # C2 — an outcome denominator that is not n, with nothing saying why
    for ok in OUTCOME_KEYS:
        o = c.get(ok)
        if isinstance(o, dict) and "denom" in o and c.get("n") is not None:
            if o["denom"] != c["n"] and "denomNote" not in o and f"{ok}DenomNote" not in c:
                bad("C2-DENOM-UNEXPLAINED", REGISTRY, f"{kp}.{ok}.denom",
                    f'"{lbl}": denom={o["denom"]} != n={c["n"]} and no denomNote says whether the '
                    "difference is missing data, a different unit, or a sub-stratum")
    # C5 / C6 — population identity
    if c.get("populationKey") is None:
        bad("C6-POPULATION-KEY-MISSING", REGISTRY, kp + ".populationKey",
            f'"{lbl}" carries no populationKey; validate-registry.mjs:113 guards overlap only '
            "`if (c.pool !== false && c.populationKey)`, so omission is an exemption from the "
            "double-counting check, not a gap in it")
    cr = (c.get("contextReason") or "")
    if "overlap" in cr and not c.get("overlapsPopulationKey"):
        bad("C5-OVERLAP-UNNAMED", REGISTRY, kp + ".contextReason",
            f'"{lbl}" declares contextReason={cr!r} but names no counterpart population; the '
            "asserted overlap is with nothing a checker can resolve")
    # C3 — a secondary row naming in prose a study this repository already holds as a citation
    if c.get("provenance") == "secondary" and c.get("primaryRef"):
        m = SURNAME_YEAR.search(c["primaryRef"])
        if m:
            sur, yr = m.group(1).lower(), int(m.group(2))
            for cid, cit in cites.items():
                if sur in (cit.get("authors", "") + " " + cit.get("short", "")).lower() and cit.get("year") == yr:
                    if not c.get("primaryRefId") and not c.get("primaryRefUnlinkedReason"):
                        bad("C3-SECONDARY-REF-UNLINKED", REGISTRY, kp + ".primaryRef",
                            f'"{lbl}" names its primary only as free text {c["primaryRef"]!r}, while '
                            f"registry.citations.{cid} is a committed resolvable entry for the same "
                            f"study (pmid={cit.get('pmid')} doi={cit.get('doi')}). One study, two "
                            "identities in one file; POLICY-evidence.md §1.3 requires the row be "
                            "repointed or the reason it cannot be recorded")
                    break

# C4 — a resolvable citation no row uses, while a row names that same study in prose
used = {c.get("sourceId") for c in cohorts} | {p.get("sourceId") for p in patients}
prose_refs = " || ".join(c.get("primaryRef", "") for c in cohorts if c.get("primaryRef"))
for cid, cit in cites.items():
    if cid in used:
        continue
    short = (cit.get("short") or "").split()[0].lower()
    if short and re.search(re.escape(short) + r".{0,60}" + str(cit.get("year", "")), prose_refs, re.I):
        bad("C4-ORPHAN-RESOLVABLE-CITATION", REGISTRY, f"registry.citations.{cid}",
            f"citation {cid} carries a resolvable id (pmid={cit.get('pmid')}, doi={cit.get('doi')}) "
            "and is referenced by no cohort or patient row, yet a cohort's free-text primaryRef "
            "names the same study")

# C7 / C8 — patient rows
for i, p in enumerate(patients):
    kp = f"registry.patients[{i}]"
    note = p.get("note", "")
    dmatch = DERIVATION_PROSE.search(note)
    if dmatch:
        derived_fields = [k for k in ("age", "sizeCm", "followupMonths") if k in p]
        if not any(k + "Derived" in p or "derived" in p for k in derived_fields):
            bad("C7-DERIVED-VALUE-UNFLAGGED", REGISTRY, kp + ".note",
                f"the note records a derivation ({note[max(0,dmatch.start()-40):dmatch.end()+45]!r}) but no field carries a "
                "machine-readable derived block, so a consumer reading the numeric field cannot "
                "tell a measurement from an imputation")
    dims = DIMENSION.findall(note)
    if "sizeCm" in p and len(set(dims)) > 1 and "sizeCmBasis" not in p:
        bad("C8-SPECIMEN-VS-CLINICAL-BASIS", REGISTRY, kp + ".sizeCm",
            f'sizeCm={p["sizeCm"]} with registry.fields.sizeCm = "Largest tumour dimension (cm)", '
            f"while the note commits {len(set(dims))} different measurements {sorted(set(dims))} — "
            "a clinical (in-vivo) reading and a gross-specimen reading give different largest "
            "dimensions and no field says which was taken")
    if "sourceId" in p and "patientId" not in p:
        bad("C9-PATIENT-ROW-UNIDENTIFIED", REGISTRY, kp,
            "the row carries no identifier in any namespace, so it cannot be checked for overlap "
            "against any cohort or against another row")

# ---------------------------------------------------------------- deposit checks
q = load(QUANT)
if not any(k.startswith("identifier") for k in q):
    for run, rec in q.get("per_run", {}).items():
        if ACCESSION.match(run) and "sample_alias" in rec:
            bad("C10-ALIAS-NAMESPACE-UNDECLARED", QUANT, f"per_run.{run}.sample_alias",
                f'sample_alias={rec["sample_alias"]!r} is a submitter-private label carrying no '
                "declared namespace and no resolves_to; it is unique only inside this deposit")
            break
for k in ("n_patients", "n_biosamples"):
    if k not in q:
        bad("C11-SPECIMEN-COUNT-TRIPLE-INCOMPLETE", QUANT, k,
            f"the record states n_runs_in_deposit={q.get('n_runs_in_deposit')} and "
            f"n_runs_read={q.get('n_runs_read')} but has no `{k}` field, so the run/specimen/"
            "patient distinction its own `_what_this_is_not` insists on has no machine-readable form")

# C12 — the same 12 objects counted in a unit the deposit does not establish.
# ⛔ TRACKED FILES ONLY. The question is what the repository COMMITTED; an untracked scratch file
# is not committed evidence. And the scan is PARAGRAPH-scoped, not file-scoped: a file may discuss
# two unrelated 12-object sets (this checker's first run matched a "12 cases" belonging to Brenca's
# table in a file that also names this deposit), and a whole-file scope cannot tell them apart.
TRACKED = subprocess.run(["git", "-C", REPO, "ls-files", "*.md", "*.json"],
                         capture_output=True, text=True, check=True).stdout.split()
for rel in TRACKED:
        fp = os.path.join(REPO, rel)
        try:
            txt = open(fp, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        if not any(d in txt for d in DEPOSIT_IDS):
            continue
        for m in COUNT_UNIT_IN_PROSE.finditer(txt):
            para_start = txt.rfind("\n\n", 0, m.start())
            para_end = txt.find("\n\n", m.end())
            para = txt[para_start if para_start >= 0 else 0: para_end if para_end >= 0 else len(txt)]
            if not any(d in para for d in DEPOSIT_IDS) and "cohort" not in para.lower() \
               and "deposit" not in para.lower() and "run" not in para.lower():
                continue
            if m.group(1).lower() not in DEPOSIT_UNIT_WORDS_PERMITTED:
                line = txt[:m.start()].count("\n") + 1
                window = txt[max(0, m.start() - 60):m.end() + 20]
                # A sentence that DENIES the equation is the guard, not the defect. It is
                # annotated, never silently dropped, because the annotation is itself a claim.
                if re.search(r"\b(not|never|cannot|isn't|is NOT)\b", window, re.I):
                    bad("C12b-UNIT-WORD-NEGATED-MENTION", rel, f"line {line}",
                        f'"{m.group(0)}" appears inside an explicit denial ({window.strip()[:150]!r}); '
                        "recorded as a guard, not a violation — review by hand that the negation "
                        "really governs this occurrence")
                    continue
                bad("C12-UNIT-WORD-NOT-ESTABLISHED", rel, f"line {line}",
                    f'"{m.group(0)}" attaches a unit to this deposit\'s count that the deposit '
                    "record does not establish; its own SRA reading says only runs, experiments "
                    "and BioSamples were counted, and that the patient mapping is unavailable")

# ---------------------------------------------------------------- report
by = {}
for v in V:
    by.setdefault(v["check"], []).append(v)
for code in sorted(by):
    print(f"\n### {code}  ({len(by[code])})")
    for v in by[code]:
        print(f"  {v['file']} :: {v['key']}\n      {v['detail']}")
hard = [v for v in V if not v["check"].endswith("b-UNIT-WORD-NEGATED-MENTION")]
print(f"\nTOTAL FINDINGS: {len(V)} across {len({v['file'] for v in V})} files "
      f"({len(hard)} violations, {len(V) - len(hard)} annotated guards)")
sys.exit(1 if hard else 0)
```

result: W13 delivered a 12-item cited specimen-identity inventory from committed data — including one study (Stacchiotti 2019 pazopanib) carried under two identities in `emc-clinical-registry.json`, a `sizeCm` that resolves to 11.5 or 17 depending on specimen-vs-clinical reading, all 14 cohort `n` values with no declared unit, and the same 12 SRA objects counted as runs/BioSamples/tumours across three files — plus a JSON Schema and a stdlib validator actually executed against the frozen checkout `92abbcb` (exit 1, 41 machine violations + 1 hand-confirmed miss across 3 files); nothing was written to the repository.
