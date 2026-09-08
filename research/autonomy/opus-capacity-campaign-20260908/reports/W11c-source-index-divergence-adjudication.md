> Collected by the campaign coordinator from this worker's in-response draft.
> Per-child runtime model evidence from the child transcript: `"model":"claude-opus-5"` (OBSERVED).

---

Stop condition met. Report follows.

---

## Worker

**W11c**, lane 11 refill (source-index adjudication) — OPUS-CAPACITY-CAMPAIGN-20260908. Adjudicator only: I authored no replacement for `scripts/source_reuse_index.py` or its test file, and propose none. W11b remains sole owner of source-index code changes.

**Model identity — SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I report myself as Claude Opus 5 (`claude-opus-5`) from my own system context. No environment variable in this container names a model; the coordinator must extract the actual per-child runtime model from the transcript.

`date -u` start: `Tue Sep  8 02:25:18 UTC 2026` · `date -u` end: `Tue Sep  8 02:28:16 UTC 2026`

`env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` — literal output, long proxy host-lists retained in transcript and marked where elided:

```
CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1
CLAUDE_CODE_ACCOUNT_UUID=4c503081-e4c3-45a1-8002-1cb705f46605
CLAUDE_CODE_CHILD_SESSION=1
no_proxy=… (proxy host list, elided)
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
GLOBAL_AGENT_NO_PROXY=… (proxy host list, elided)
ANTHROPIC_BASE_URL=https://api.anthropic.com
CLAUDE_CODE_DIAGNOSTICS_FILE=/tmp/claude-code-303934770.diag.log
CLAUDE_ENABLE_STREAM_WATCHDOG=1
CLAUDE_CODE_REMOTE_HERMETIC_MODE=0
CLAUDE_CODE_ENVIRONMENT_RUNNER_VERSION=release-ba76006550-ext
CLAUDE_CODE_DISABLE_BUILTIN_ANTMCP=1
CLAUDE_ADDITIONAL_DIRECTORIES=/mnt/user-data
JAVA_TOOL_OPTIONS=… (proxy config, elided)
NO_PROXY=… (proxy host list, elided)
CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=1
CLAUDE_CODE_USE_CCR_V2=true
CLAUDE_CODE_SYNC_SESSION_REFS=1
DOCUMENTS_MCP_SCRATCH_ROOT=/mnt/user-data/working/claude-docs
CLAUDE_CODE_TEE_SDK_STDOUT=true
CLAUDE_CODE_ENTRYPOINT=remote
CLAUDE_CODE_VERSION=2.1.42
CLAUDE_CODE_EXECPATH=/opt/claude-code/bin/claude
npm_config_noproxy=… (proxy host list, elided)
CLAUDE_CODE_REMOTE_SEND_KEEPALIVES=true
CLAUDE_CODE_REMOTE=true
CLAUDE_CODE_POST_FOR_SESSION_INGRESS_V2=true
CLAUDE_CODE_ORGANIZATION_UUID=9f10e945-e412-4b71-8a9d-5d6affcd7d4f
CLAUDE_SESSION_INGRESS_TOKEN=<redacted>
CLAUDE_CODE_SYNC_SKILLS=1
CLAUDE_CODE_HOLD_UNANSWERED_PARKED_PERMISSION=1
CLAUDE_CODE_MESSAGING_TOKEN=<redacted>
```

**HEAD actually read: `b9a0257e6acff53ad22535cf2adf261313e0b250`.** This is NOT the `92abbcb905cacf07f14b238db50d1b98f6590374` named as frozen in COMMON-BRIEF.md, nor the `4878b9b9d1c082cea46e636dad47be419f1fe021` recorded as `writer_tier_source_commit` in the input manifest. The checkout has advanced under the campaign; I record what I read rather than what the brief asserts. `git status --porcelain` shows one modified file (`WAVE-LOG.md`) and 16 untracked sibling worker reports, none touched by me.

**Write isolation honoured.** Zero files created or modified under `/home/user/Rare-cancers`. All execution under `/tmp/claude-0/w11c/`. No git write operation of any kind. No network.

---

## Question

**The independent review's §2 divergence list names eight contract items as never implemented. For each: is the divergence real when executed against W11b's *delivered* helper (not the original draft), and what would satisfying it cost in commit-loop tier test-budget terms?**

Open because §2 has never been adjudicated by execution at all. W11b adjudicated §0's nine defect findings (F1–F9) and found the review materially wrong about its own F4 example; §2 was carried forward as reduced scope on the review's prose alone. Prose that was wrong once is not evidence.

---

## Prior-work check

```
$ git ls-files | rg -i "source_reuse|source-index"
research/autonomy/opus-capacity-campaign-20260908/reports/W11-source-index-integration-contract.md
```

Only W11's contract is tracked. W11b's report and the whole `inputs/source-index/` bundle are **untracked** — they are collector artifacts, not committed state.

```
$ for t in FIELD_NOT_ADMITTED admitted_fields referenced_origin_missing possible_same_deposit \
           base_revision PROVENANCE_UNVERIFIED KNOWN_ title_candidates; do
      rg -n -F "$t" --glob '!.git' -l ; done
```

- `FIELD_NOT_ADMITTED`, `admitted_fields`, `referenced_origin_missing` → **only** `reports/W11b-source-index-consolidated-repair.md` (which quotes the review verbatim; it does not adjudicate them).
- `possible_same_deposit`, `PROVENANCE_UNVERIFIED`, `title_candidates` → **no hits anywhere in the tree.**
- `base_revision` → 19 files, all unrelated (PUB-ASO verification, throughput measurements, follow-through replay). None is a source-index output contract.
- `KNOWN_` → ~60 files, all unrelated constants in other modules.

**Conclusion: no prior adjudication of any §2 item exists.** I confirmed I am not replaying the three lane-11 closed items (no ceiling increase, no 30-test gate, complete named final files into an existing tier), not touching PUB-EMC-CLASSIFICATION, and not re-entering any Brenca route. CLOSED-WORK.md read in full.

---

## Method / inputs

Input hashes re-verified against `inputs/source-index/input-manifest.json` **before** any execution:

```
$ sha256sum research/tools/source_reuse_index.py research/tools/tests/test_source_reuse_index.py \
            evidence/independent-comparison/report.md
bc348ce955534bf848b6a3d8b24944c3126abe6066ef1c5fbbe25f2b4bf91c4d  research/tools/source_reuse_index.py
2c07fae45942fdbf994ec5df4b67df4d957056f23d6a0cafbce6d736ff269bc4  research/tools/tests/test_source_reuse_index.py
368296fc818f6016febf9848120e37d4e69cba601543102ae7ce4fc55fb03f4a  evidence/independent-comparison/report.md
```

All three match the manifest exactly.

W11b's delivered pair was reproduced into `/tmp/claude-0/w11c/` by extracting the fenced blocks from `reports/W11b-source-index-consolidated-repair.md` (helper = report lines 208–1263; tests = lines 1271–1747), giving **1056** and **477** lines. Both parse clean under `ast.parse`. Nothing was placed in the repository tree.

The review's §2 was read verbatim at `evidence/independent-comparison/report.md:203–226` — I adjudicate the eight items as that paragraph words them, not as the dispatch paraphrases them.

Environment: container `container_0166QEHnXrRA8nCR59c9UG4k--claude_code_remote--71b0d4`, Linux 6.18.44-fc-v24, `python3` at `/usr/lib/python3.11` (stdlib path observed in traceback). Probe scripts: `/tmp/claude-0/w11c/probe/probe_d.py` (D1–D8), `/tmp/claude-0/w11c/probe/probe_d7.py` (D7 re-adjudication), `/tmp/claude-0/w11c/probe/corpus2_setup.py` (D5 refinement). Fixture corpora: `probe/corpus/` (3 records) and `probe/corpus2/` (2 Zenodo-shaped records carrying real `conceptdoi`/`conceptrecid` fields).

One harness defect I hit and fixed, recorded because it affects reproducibility: loading the helper via `importlib.util.spec_from_file_location` without registering it in `sys.modules` crashes at `@dataclass(frozen=True)` (`AttributeError: 'NoneType' object has no attribute '__dict__'`, exit 1). This is a probe-harness artifact, **not** a defect in W11b's helper — the helper imports correctly by ordinary path import. Fixed with `sys.modules["sri"] = sri` before `exec_module`.

---

## Result

### 1. Eight per-item verdicts, each backed by an executed probe

Every row is a probe I ran against W11b's **delivered** helper. "ABSENT" means the divergence the review asserts is **real**.

| # | §2 item | Verdict | Failing case actually run | Class |
|---|---|---|---|---|
| D1 | `KNOWN_*` vocabulary rename | **ABSENT — divergence REAL** | `dir(sri)` yields **zero** `KNOWN_*` names; `LOOKUP_STATES` is `('matched', 'matched_prose_mention_only', 'matched_with_divergent_states', 'unresolved_not_indexed', 'unresolved_url_without_identifier', 'ambiguous_multiple_identifiers', 'invalid_candidate')` — the `matched*`/`unresolved*` set, not the contract's | PRIMARY |
| D2 | `admitted_fields` / `FIELD_NOT_ADMITTED` | **ABSENT — divergence REAL, and W11b's F1 fix *widens* it** | Tokens `admitted_fields`, `FIELD_NOT_ADMITTED`, `field_not_admitted` appear nowhere in the 1056-line helper. A DOI planted in a deliberately junk key, `"unadmitted_field_carrying_id": "10.1016/j.ejca.2014.03.013"`, returns `state='matched'`, **1 match**, `context: structured_field`, no admissibility signal | PRIMARY |
| D3 | sha256 recomputation (`PROVENANCE_UNVERIFIED`) | **ABSENT — divergence REAL** | `hashlib` neither imported nor referenced anywhere; `PROVENANCE_UNVERIFIED` absent from source; a record carrying an all-zeros `sha256` next to a real archive member returns no `provenance_unverified` token. The docstring of `_bytes_signal` states this openly: "reports what the record states and does not verify any hash" | PRIMARY |
| D4 | `referenced_origin_missing` | **ABSENT — divergence REAL** | Token absent from source and from output. A record declaring `"referenced_origin": "evidence/does-not-exist.json"` — a path that does not exist — produces `state='matched'` with `indexed_scope.warnings` = `None`. The dangling reference is invisible | PRIMARY |
| D5 | Zenodo concept-vs-version advisory | **ABSENT — divergence REAL; the review's *stated reason* is right but its implicit premise needs correcting** | `possible_same_deposit` absent; the string `zenodo` appears nowhere in the helper (case-insensitive). Looking up `10.5281/zenodo.7654322` returns `state='matched'`, 1 match, with no mention of sibling `…7654321`. **Refinement (second corpus):** even when both records carry an explicit shared `conceptdoi: 10.5281/zenodo.7654320` and `conceptrecid: 7654320`, the lookup of `…7654321` surfaces neither the sibling version `…7654399` (`False`) nor the shared concept id (`False`) | PRIMARY |
| D6 | `base_revision` in output | **ABSENT — divergence REAL** | Token absent from source. Result top-level keys are exactly `['access_evidence', 'conflicts', 'disclaimer', 'indexed_scope', 'matches', 'normalized', 'notes', 'query', 'record_statuses', 'resolved_scheme', 'scope_warnings', 'state', 'synthetic_fixture_records', 'url_key_mentions']` — no `base_revision`, and a record that *carries* one does not surface it | PRIMARY |
| D7 | current-vs-superseded designation | **ABSENT — divergence REAL.** *My first probe returned a FALSE "PRESENT" and I overturned it* | Two dated statuses on one identifier return flat: keys are exactly `['date', 'field', 'locator', 'record_id', 'status']`; **zero** designation keys (`designation`, `is_current`, `current`, `superseded`, `superseded_by`, `rank`). Exit 0 from the corrected probe | PRIMARY |
| D8 | advisory title candidates | **ABSENT — divergence REAL** | `title_candidates` absent from source and output. Querying the exact title string of an indexed record returns `state='invalid_candidate'`, **0 matches**, plus `TITLE_NOTE`: "Titles are excluded from matching entirely." Refused outright, exactly as the review says | PRIMARY |

**Eight of eight divergences are real.** Unlike W11b's §0 adjudication, no §2 claim is refuted on the facts. That is itself worth stating plainly: the review was wrong about F4's example but is right about all eight §2 items.

### 2. What I got wrong, reported as prominently as the confirmations

**My own D7 probe produced a false "PRESENT (divergence REFUTED)" verdict and I overturned it by execution.** The first probe used a substring heuristic — `"superseded" in SRC` → `True` — and concluded designation was implemented. Grepping the two hits showed both are prose *disclaiming* the behaviour:

- line 124 (`DATED_NOTE`): "Nothing is merged, ranked or **superseded** by this tool; conflicting or dated entries are all retained."
- line 851: "order and all are retained; none is **superseded**, merged or …"

A token-presence check cannot distinguish implementing a behaviour from documenting its refusal. I replaced it with a functional probe on the returned status objects (`probe_d7.py`), which decided ABSENT with exit 0. **This is the same class of error the review made on F4** — reasoning from a string's presence rather than from what the code does with it — and I record it against myself.

### 3. Two items are real divergences that should probably NOT be closed

The question asks whether each divergence is real. Two are real *and* contraindicated, and the report would be dishonest to list them beside the other six as pending work:

- **D7 (designation).** The helper's flat status listing is a stated design decision (`DATED_NOTE`, line 122–125), and the review itself concedes it is "arguably safer". Implementing AC-25 means the tool decides which retained status supersedes which — ranking evidence. That is the opposite of the repository's posture that conflicting dated entries are all retained and nothing is merged.
- **D8 (title candidates).** §2 contains an **internal contradiction**. The same paragraph praises the helper for "**No fuzzy matching** — exact normalized equality only, so AC-05/AC-06-style near-miss accessions cannot cross-match" and then faults it for refusing titles instead of returning advisory candidates (N9). Advisory title candidates *are* fuzzy matching, over the least reliable key available. The review asks for a property in one clause and credits its absence in another. I flag this rather than costing it.

**D3 additionally cannot be satisfied in scope as worded.** sha256 recomputation requires reading the referenced bytes. The helper's only `open()` is read-mode over the corpus (a property the review verifies as AC-compliant); hashing a referenced *artifact* means opening files outside the indexed corpus, and where the referent is remote, network — explicitly out of scope. What is implementable offline is the narrower "digest recorded but referent not present in scope → `PROVENANCE_UNVERIFIED`", which is nearly D4 wearing a different name.

**D5 has a concrete offline basis that the review does not mention.** `conceptrecid`/`conceptdoi` are real retained fields in this repository (`scripts/zenodo_deposit.py:229,250,475`; `scripts/zenodo_verify.py:87`; `scripts/tests/test_a_new_version_run_adopts_the_draft_it_already_opened.py`). So AC-07 is implementable without network **for records that carry that field**, by grouping on the shared concept id — and must return UNKNOWN, not a guess, for records that do not. Version DOIs are not derivable from each other by string arithmetic; any prefix-only heuristic would manufacture a relationship. That is a real constraint on the item's shape, not a reason to skip it.

### 4. Measured tier budget — the projection was optimistic because placement never happened

```
$ cd /home/user/Rare-cancers && python3 scripts/tier_budget.py
   ok    commit-loop             1466/1500  test function(s) in 102 file(s)
   ok    modalities              7247/7500  test function(s) in 436 file(s)
   ok    paper-guards             966/1000  test function(s) in 111 file(s)
EXIT=0
```

```
$ ls scripts/source_reuse_index.py scripts/tests/test_source_reuse_index.py
ls: cannot access 'scripts/source_reuse_index.py': No such file or directory
ls: cannot access 'scripts/tests/test_source_reuse_index.py': No such file or directory
```

**Measured commit-loop total is 1466/1500 — 34 functions of headroom, shared not reserved.** The dispatch's prediction is confirmed: W11b's `1484/1500` was a *projection* of a placement that has not occurred, and the files are not in the tree. W11b's test file defines **18** test functions by the repository's own AST method, **0 duplicate names** (verified independently here). So placement would consume 18 of the 34, leaving **16**.

### 5. Cost of the eight items, and the feasibility answer

Test counts below are my estimate of the **minimum** needed to pin each behaviour under this repository's posture, where every advisory needs a companion negative control asserting it is *not* a match and not a claim. Marked `PREDICTION`, not measured — no such tests exist to count.

| # | Item | Min new test fns | Note | Class |
|---|---|---|---|---|
| D1 | `KNOWN_*` rename | **1** | cheap in *new* tests, but rewrites assertions in ~6 of W11b's 18 existing tests | PREDICTION |
| D2 | `admitted_fields` / `FIELD_NOT_ADMITTED` | **4** | admitted match; non-admitted → `FIELD_NOT_ADMITTED` not a match; carried limitation; CLI still exits 0. **Reverses W11b's F1 fix** — ≥2 existing tests change meaning | PREDICTION |
| D3 | sha256 / `PROVENANCE_UNVERIFIED` | **3** | digest matches; digest mismatches; referent absent → unverified, not false. Out-of-scope as fully worded | PREDICTION |
| D4 | `referenced_origin_missing` | **2** | origin present; origin dangling | PREDICTION |
| D5 | Zenodo concept/version advisory | **3** | shared `conceptdoi` → advisory; different concept → none; **no** `conceptdoi` → UNKNOWN, never a guess | PREDICTION |
| D6 | `base_revision` | **2** | present and surfaced; absent and stated absent | PREDICTION |
| D7 | current-vs-superseded | **3** | contradicts `DATED_NOTE`; contraindicated | PREDICTION |
| D8 | advisory title candidates | **3** | contradicts the review's own no-fuzzy-matching credit; contraindicated | PREDICTION |
| | **Total** | **21 minimum; 21–26 realistic** | | PREDICTION |

**Feasibility statement, explicit:**

- Headroom after placing W11b's pair: **16**. Minimum cost of the eight: **21**. **Short by at least 5, realistically by 10.** The commit-loop tier cannot carry the eight items.
- Sharper form: **18 + 21 = 39 > 34**. Even the *combined* delivery of W11b's pair and the eight items exceeds the tier's entire current headroom before any other worker in the repository adds a single test.
- What fits: the four cheapest items (D6 + D4 + D1 + D5 = 8) fit inside the 16 remaining after placement. D2 and D3 do not fit alongside them. D7 and D8 I recommend against implementing at all, on merits, independent of budget.

**I changed no budget file, raised no ceiling, and propose no 30-test gate** — all three are recorded closed. I note that `scripts/tier-budgets.json`'s own `_how_to_raise_a_ceiling` field pre-empts the question and names the sanctioned alternative: *"NOT BY EDITING THE NUMBER. Ask first whether the test belongs in a cheaper tier, and second whether something already in the tier has stopped earning its place."*

**So: yes, the commit-loop tier is the wrong home for these eight behaviours.** Not because the tier is too small, but because the arithmetic says a lookup helper's contract-completion suite would consume two-thirds of a shared budget that exists precisely to stop one concern from doing that. The honest routing is: place W11b's 18-function pair (which is defect repair, earns its tier seat, and fits), and treat the eight §2 items as a separate scope decision — six of them costing 15 functions that must find a cheaper home or a justified deletion elsewhere in the tier, and two of them (D7, D8) declined on merits.

---

## Validation evidence

All **RUN**. Environment: container `container_0166QEHnXrRA8nCR59c9UG4k--claude_code_remote--71b0d4`, Linux 6.18.44-fc-v24, `python3` 3.11 (`/usr/lib/python3.11`), cwd `/tmp/claude-0/w11c` unless stated.

**V1 — input hash re-verification (exit 0), `cwd=.../inputs/source-index`:** output quoted in Method above; all three digests match `input-manifest.json`.

**V2 — reproduce W11b's pair into /tmp (exit 0):**
```
1056 scripts/source_reuse_index.py
 477 scripts/tests/test_source_reuse_index.py
1533 total
PARSE OK
```

**V3 — probe harness defect, then fix (exit 1, then exit 0):**
```
  File "/tmp/claude-0/w11c/scripts/source_reuse_index.py", line 224, in <module>
    @dataclass(frozen=True)
AttributeError: 'NoneType' object has no attribute '__dict__'. Did you mean: '__dir__'?
EXIT=1
```
Harness artifact (module not registered in `sys.modules`), not a helper defect.

**V4 — `python3 probe/probe_d.py`, eight divergence probes, EXIT=0.** Verbatim summary:
```
D1	KNOWN_* vocabulary rename	ABSENT (divergence REAL)
D2	admitted_fields / FIELD_NOT_ADMITTED	ABSENT (divergence REAL)
D3	sha256 recomputation (PROVENANCE_UNVERIFIED)	ABSENT (divergence REAL)
D4	referenced_origin_missing	ABSENT (divergence REAL)
D5	Zenodo concept-vs-version advisory (possible_same_deposit)	ABSENT (divergence REAL)
D6	base_revision in output	ABSENT (divergence REAL)
D7	current-vs-superseded designation	PRESENT (divergence REFUTED)   <-- SUPERSEDED BY V6, FALSE POSITIVE
D8	advisory title candidates	ABSENT (divergence REAL)
```
Selected detail lines, verbatim:
```
== D2 admitted_fields / FIELD_NOT_ADMITTED -> ABSENT (divergence REAL)
   source tokens=[] ; lookup of id carried in 'unadmitted_field_carrying_id' -> state='matched' matches=1, 'not_admitted' in result=False
== D4 referenced_origin_missing -> ABSENT (divergence REAL)
   token in source=False ; rec_a declares referenced_origin='evidence/does-not-exist.json'; token in result=False ; warnings=None
== D8 advisory title candidates -> ABSENT (divergence REAL)
   state='invalid_candidate' ; matches=0 ; 'title_candidates' in source=False
```

**V5 — locate the D7 false positive (exit 0):**
```
$ grep -n -i "supersed\|current" scripts/source_reuse_index.py
124:    "ranked or superseded by this tool; conflicting or dated entries are all retained."
393:    ("no_access_attempt_in_this_packet", (...))
396:_NEGATION_MARKERS = (" not ", "is not", "are not", "never", "none", "no current", "no recovered")
851:                    "order and all are retained; none is superseded, merged or "
```

**V6 — `python3 probe/probe_d7.py`, D7 re-adjudicated functionally, EXIT=0:**
```
status object keys: ['date', 'field', 'locator', 'record_id', 'status']
designation keys present: []
note attached: ['Dated record statuses are reported verbatim in date order. Nothing is merged, ranked or superseded by this tool; conflicting or dated entries are all retained.']
VERDICT D7: ABSENT (divergence REAL)
```

**V7 — `python3 probe/corpus2_setup.py`, D5 refinement with real `conceptdoi` metadata, EXIT=0:**
```
lookup of version DOI v1 -> state='matched' matches=1
sibling version 7654399 surfaced in result: False
shared conceptdoi 7654320 surfaced in result: False
VERDICT D5 (with real conceptdoi metadata present): ABSENT (divergence REAL)
```

**V8 — `python3 scripts/tier_budget.py`, cwd `/home/user/Rare-cancers`, EXIT=0:** output quoted in Result §4. `commit-loop 1466/1500`.

**V9 — AST count of W11b's test file (exit 0):** `18` test functions, `dups: 0`; all 18 names listed in transcript.

**V10 — prior-work token search and `git ls-files` (exit 0):** output quoted in Prior-work check.

**PROPOSED (NOT RUN):** every test-count figure in Result §5 is an estimate of tests that do not exist. No test for any of the eight items was written or run by me, by design — I am an adjudicator and may not author source-index tests.

---

## Limitations

- **Fixture-based, not corpus-based.** The four real repository records the original review cites are absent at the commit I read (W11b established this). Each of my eight probes ran against synthetic records I constructed to the shape §2 describes. That limits the *citations*, not the mechanisms — but a divergence confirmed on a fixture is a confirmed property of the code, not of the repository's actual data.
- **Reconstruction risk.** W11b's helper was reproduced from fenced blocks inside a Markdown report, not from a hash-verified artifact. `ast.parse` succeeded and line counts are plausible, but there is **no digest** for W11b's final files to check against — the manifest hashes only the *original* draft. If the extraction clipped a line, my verdicts describe a near-copy. This is a transfer limit created by the report-as-delivery mechanism and it will recur for any successor.
- **HEAD drift.** I read `b9a0257`, not the brief's frozen `92abbcb` nor the manifest's `4878b9b`. The 1466 figure is a measurement of the tree as it stood at 02:27 UTC on 2026-09-08 and will move as the campaign lands reports.
- **Test-cost figures are predictions.** They are my judgement of minimum coverage, not measurements. A reviewer could argue several items down by one test or up by two; the feasibility conclusion survives that range (16 available vs. 21–26 needed) but is not a proof.
- **D3 and D5 scope judgements are mine.** That full sha256 recomputation exceeds the tool's no-network, corpus-only scope, and that Zenodo version relations are not derivable from DOI strings, are reasoned conclusions from the code and from Zenodo's documented concept-DOI model — not things I executed a test against.
- **No scientific claim.** This is an informational read-only lookup helper. Nothing here establishes anything about EMC, about any therapeutic, or about any patient. No efficacy, safety, selectivity or clinical-readiness claim is made or implied.

---

## Stop condition

**Set:** eight per-item verdicts each backed by an executed probe with a real exit code, plus a measured tier-budget figure and an explicit feasibility statement.

**MET.** Eight verdicts, all from probes I ran (V4 for D1–D6/D8, V6 for D7 after overturning my own false positive, V7 refining D5). Measured figure: `commit-loop 1466/1500`, exit 0, with the placement absence independently confirmed by `ls`. Feasibility stated explicitly and negatively: the eight items need ≥21 functions against 16 post-placement headroom, and the commit-loop tier is the wrong home. Returning immediately.

---

## Tool-call and wall-clock count actually used

**15 tool calls** (all Bash), **~3 minutes wall clock** (02:25:18 → 02:28:16 UTC). Well inside the ~40-call / ~40-minute target.

---

## Next concrete action

**One task, for W11b as sole code owner — not for a new writer.** Place W11b's existing 18-function pair into `scripts/` and `scripts/tests/` unchanged (1466 → 1484/1500, verified by re-running `scripts/tier_budget.py` after placement rather than projecting it), and implement **only D6 + D4** (`base_revision` surfaced in output; `referenced_origin_missing` when a declared origin path is absent from the indexed scope) at a cost of 4 test functions → 1488/1500. Both are pure additions that surface information the helper already walks past, neither contradicts an existing design note, and both stay inside headroom without touching a budget file.

D1, D2, D3, D5 should be routed as a **separate scope decision** with the tier question answered first — per `tier-budgets.json`'s own guidance, whether they belong in a cheaper tier, or whether something in commit-loop has stopped earning its place. D7 and D8 I recommend be **declined on merits** and the recommendation recorded, so the next reader of §2 does not re-open them: D7 asks the tool to rank retained evidence, and D8 asks for fuzzy title matching that the same paragraph credits the helper for refusing.
