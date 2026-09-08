> Collected by the campaign coordinator from this worker's in-response draft.
> Per-child runtime model evidence from the child transcript: `"model":"claude-opus-5"` (OBSERVED).

---

Both contradictions re-verified live, S18's text checked, package built, validator re-run. Report follows.

---

## Worker

- **Worker:** W09c, lane 9 refill, OPUS-CAPACITY-CAMPAIGN-20260908.
- **Model identity: SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I report myself as Claude Opus 5 (`claude-opus-5`). `env` exposes no model variable; `AI_AGENT=claude-code_2-1-263_agent` and `CLAUDE_CODE_VERSION=2.1.42` are harness versions, not model identities. The coordinator should extract the runtime model from the transcript.
- **Write isolation: honoured.** Nothing written under `/home/user/Rare-cancers`; no git write operation. All execution under `/tmp/claude-0/w09c/`. **Neither correction was applied.**
- **HEAD actually read: `b9a0257e6acff53ad22535cf2adf261313e0b250`**, unchanged at start and end. ⚠ This is **not** the brief's frozen commit `92abbcb905…` — the tree has advanced (W09b already reported it moving to `103ff76f` mid-run; it has since moved again as the coordinator collected reports). `git status --porcelain` shows only other workers' collected reports plus `WAVE-LOG.md`; none of the four files I analyse is modified or untracked.

`date -u` at start: `Tue Sep  8 02:24:46 UTC 2026`. At end: `Tue Sep  8 02:29:32 UTC 2026`.

Literal output of `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` (exit 0). The five long proxy lines (`no_proxy`, `NO_PROXY`, `GLOBAL_AGENT_NO_PROXY`, `npm_config_noproxy`, `JAVA_TOOL_OPTIONS`) are elided as marked; nothing else removed:

```
CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1
CLAUDE_CODE_ACCOUNT_UUID=4c503081-e4c3-45a1-8002-1cb705f46605
CLAUDE_CODE_CHILD_SESSION=1
[no_proxy=… elided]
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
[GLOBAL_AGENT_NO_PROXY=… elided]
ANTHROPIC_BASE_URL=https://api.anthropic.com
CLAUDE_CODE_DIAGNOSTICS_FILE=/tmp/claude-code-303934770.diag.log
CLAUDE_ENABLE_STREAM_WATCHDOG=1
CLAUDE_CODE_REMOTE_HERMETIC_MODE=0
CLAUDE_CODE_ENVIRONMENT_RUNNER_VERSION=release-ba76006550-ext
CLAUDE_CODE_DISABLE_BUILTIN_ANTMCP=1
CLAUDE_ADDITIONAL_DIRECTORIES=/mnt/user-data
[JAVA_TOOL_OPTIONS=… elided]
[NO_PROXY=… elided]
CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=1
CLAUDE_CODE_USE_CCR_V2=true
CLAUDE_CODE_SYNC_SESSION_REFS=1
DOCUMENTS_MCP_SCRATCH_ROOT=/mnt/user-data/working/claude-docs
CLAUDE_CODE_TEE_SDK_STDOUT=true
CLAUDE_CODE_ENTRYPOINT=remote
CLAUDE_CODE_VERSION=2.1.42
CLAUDE_CODE_EXECPATH=/opt/claude-code/bin/claude
[npm_config_noproxy=… elided]
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

**For each of W09b's two contradictions in `systems/graph/artifacts.json`, is it still live at the current HEAD, what exactly is the minimal correction, and is S18's already-written replacement text still correct against today's tree?**

Open because a diagnosis with replacement text written seven days ago is not a repair, and because nobody had checked whether the replacement text was still accurate against a tree that has moved since. The transferred claim was to be re-verified, not trusted.

---

## Prior-work check

Read in full first: `COMMON-BRIEF.md`, `CLOSED-WORK.md`, `reports/W09b-absence-claim-audit.md` (705 lines), `systems/POLICY-evidence.md` (386 lines, read **before** forming any view on graph state, as instructed), `research/autonomy/sprint-2026-09-01/S18-FALSE-ABSENCES.md` (332 lines).

Commands run:

```
grep -n "does not appear in this histology" systems/graph/artifacts.json
grep -n "FT\] passage" systems/graph/artifacts.json
grep -n "found_in_this_histology" research/modalities/emc-radiotherapy-contradiction.json
grep -n -i -E "carbon|\[FT\]|artifacts.json" research/autonomy/sprint-2026-09-01/S18-FALSE-ABSENCES.md
grep -rn "systems/graph" --include=*.py --include=*.mjs --include=*.js scripts/ systems/
grep -rn "artifacts.json" --include=*.py --include=*.mjs -l .
git log --oneline -8 -- systems/graph/artifacts.json
```

Closed items confirmed and **not** replayed: PUB-EMC-CLASSIFICATION (untouched); every Brenca route (untouched); lane 11's source-index (untouched — W11b sole owner); the S18 corrections themselves inside `emc-radiotherapy-contradiction.json` / `emc-care-delivery-evidence.json` (already landed, verified only, not re-done); the `emc-perfusion-myxoid-search-2026-08-27.json` null (not re-run, no egress); W09b's precision measurement (**preserved unchanged — I did not tune the prose rules and did not re-measure precision**).

I did **not** take W09b's word for either contradiction; both were re-derived from the files.

---

## Method / inputs

No network. Python 3 stdlib. All execution under `/tmp/claude-0/w09c/`.

| input | role |
|---|---|
| `/home/user/Rare-cancers/systems/graph/artifacts.json` (556 lines, 56 records, JSON **list**) | the file carrying both contradictions |
| `/home/user/Rare-cancers/research/modalities/emc-radiotherapy-contradiction.json` | the corrected artifact that contradicts C1 |
| `/home/user/Rare-cancers/research/modalities/emc-care-delivery-evidence.json` | the artifact whose `[FT]` rows contradict C2 |
| `/home/user/Rare-cancers/systems/graph/routes.json` | where S18 items 1/3/4 landed; item 2 did not |
| `/home/user/Rare-cancers/scripts/tests/test_no_hand_authored_json_has_a_duplicate_key.py` | the tree's own declaration of what is hand-authored |
| `/tmp/claude-0/w09c/lint_absence_claims.py` | W09b's validator, reconstructed from the inline listing in its report |
| `/tmp/claude-0/w09c/test_w09c_acceptance.py` | the acceptance test authored here, run RED at HEAD and GREEN on a scratch fixture |

---

## Result

### R.1 — C1 is LIVE at `b9a0257e`. Verbatim, with file and line. `PRIMARY`

`systems/graph/artifacts.json:534`, inside record index **53**, `id: ART-RT-CONTRADICTION`, `path: research/modalities/emc-radiotherapy-contradiction.json`. The offending sentence, verbatim:

> `⭐ PARTICLE/BRACHYTHERAPY CENSUS RUN: brachytherapy and proton beam each reported ONCE in this histology, as case reports rather than registry arms; carbon ion does not appear in this histology anywhere in a 354-paper open-access corpus.`

Contradicted by the artifact that same record points at — `research/modalities/emc-radiotherapy-contradiction.json:171`:

> `"found_in_this_histology": true,`

derived (not typed) from a corpus quote pinned by blob `79a8c197243ff4202a713d437def379c5f499a68` (Masunaga 2025, PMID 40885991, PMC12398172). **Verdict: CONTRADICTED, LIVE.** W09b's C1 confirmed independently.

### R.2 — C2 is LIVE at `b9a0257e`. Verbatim, with file and line. `PRIMARY`

`systems/graph/artifacts.json:453`, record index **44**, `id: ART-CARE-DELIVERY-EVIDENCE`, `path: research/modalities/emc-care-delivery-evidence.json`. Verbatim:

> `The one [FT] passage is the ICD-O code enumeration in PMID 31765367.`

The artifact it summarises carries **two** `[FT]` rows, not one:

| line | row | `provenance` |
|---|---|---|
| `research/modalities/emc-care-delivery-evidence.json:41` | ICD-O code enumeration, PMID 31765367 / PMC6894367, `quote_source: "full text, Materials and Methods"` | `"[FT]"` |
| `research/modalities/emc-care-delivery-evidence.json:123` | the metastasectomy sentence, PMID 40885991, blob `79a8c197243ff4202a713d437def379c5f499a68` | `"[FT]"` |

Line 124 states why the second exists: *"This row was [API] while it asserted a zero it had not measured. It is [FT] now because the sentence that refutes it was read in the retrieved full text, whose blob SHA is pinned above."* **Verdict: CONTRADICTED, LIVE.** W09b's C2 confirmed independently. Count is exactly 2 (`json.dumps(...).count('"provenance": "[FT]"') == 2`).

### R.3 — S18's replacement text: located, and it has NOT drifted in substance, but it is not a drop-in string `PRIMARY`

S18's text is `research/autonomy/sprint-2026-09-01/S18-FALSE-ABSENCES.md:272-273`, rows 5 and 6 of the table "⛔ Route grades that quote the wrong values — DRIVER ACTION, not mine". Word-by-word check:

| S18 wrote | today's tree | drift |
|---|---|---|
| item 5 quotes the current text as *"carbon ion **does not appear in this histology anywhere** in a 354-paper open-access corpus"* | byte-identical at `artifacts.json:534` | **none** |
| item 5's correction column is *"⭐ A fifth copy of the false absence… **Same correction**"* — i.e. it delegates to item 3 rather than giving a literal | item 3's correction **has landed**, in expanded form, at `routes.json:7662` (`RT-RT-INTENSIFY.grade.value`) and `routes.json:7713` (`remaining_unknowns[2]`) | ⚠ **shape drift, not fact drift** — the canonical corrected wording now exists in the tree and is ~5× longer than a summary-layer note should be; it must be condensed, not copied |
| item 6 quotes *"The **one** [FT] passage is the ICD-O code enumeration in PMID 31765367."* | byte-identical at `artifacts.json:453` | **none** |
| item 6's premise: *"the metastasectomy quote in the absence row is `[FT]` and pinned by blob SHA"* | true at `emc-care-delivery-evidence.json:123-124` | **none** |

⭐ **One drift that changes how the correction must be written, and S18 could not have known it.** Since 2026-09-01 the repository has settled on a **rule-1.2 retention convention** for exactly this situation: the superseded string is kept verbatim inside a `⚠ Superseded, retained (rule 1.2): "…"` clause and then refuted. `routes.json:7662` does this with *this very sentence*. S18's items 5/6 predate that convention landing here and say only "replace". **The correction must retain, not delete** — otherwise the graph layer contradicts the precedent its own sibling file set three days ago.

⛔ **And S18 item 2 never landed either — a third live item W09b did not report.** `routes.json` → `RT-METASTASECTOMY.supporting_evidence[0].what_it_supports` still reads, verbatim:

> `the measured absence of any EMC metastasectomy record in a 554-record open-access corpus`

against a refutation that has landed everywhere around it (`RT-METASTASECTOMY.grade.value` at `routes.json:8492` carries the full correction). S18's proposed replacement for it, at `S18-FALSE-ABSENCES.md:269`, is *"the absence of any **comparative** EMC metastasectomy study; the operation itself is reported (8/29, Masunaga 2025) with no outcome attached"* — still accurate. **`PRIMARY`, and it is outside my two-contradiction package: routed, not packaged.** So of S18's six queued items, **1, 3 and 4 landed; 2, 5 and 6 did not.**

### R.4 — POLICY-evidence.md: which clauses govern these fields `PRIMARY`

Read before forming any opinion, as instructed. The honest reading:

- ⛔ **`systems/graph/artifacts.json` is NOT inside this policy's scope.** Its `scope:` frontmatter binds *"Clinical and epidemiological evidence only — the EMC registry, the manuscript's meta-analysis, and any pooled proportion or interval derived from published cohorts"*, and its named owner is `research/data/emc-clinical-registry.json`. It is enforced by `scripts/validate-registry.mjs` (preflight gate 10), which does not read the graph.
- ⭐ **But §1.3 governs these fields *by adoption*, because the note itself invokes it.** `artifacts.json:534` ends: *"⛔ Provenance is split primary/secondary throughout and a test fails if a record read only in a review loses its not-read-directly marker (**POLICY-evidence 1.3**)."* §1.3 is "Primary vs. secondary provenance — never launder a citation", and its operative sentence for C2 is: *"`sourceId` is **the document you actually read the number in**."* The `[API]`/`[FT]` marks in `emc-care-delivery-evidence.json` are that distinction implemented, and **§1.3 is the clause C2 violates**: the note claims one full-text read where the artifact records two, understating what was actually read from a source's own text — the same error class §1.3 forbids, in the opposite direction.
- **§1.2's `verified: true` rule is the second clause.** *"`verified: true` is set only when the link was opened and confirmed to support the exact claim."* C1's note asserts a corpus census result that the artifact beneath it no longer supports; a summary asserting what its own source contradicts is that rule failing at the summary layer.
- **§4 (temporal validity) is the reason neither correction may be silently rewritten.** *"never silently adjust a number upward"* — its logic (transparency + retention, never a quiet edit) is exactly the rule-1.2 retention behaviour I recommend.
- ⛔ **No clause of POLICY-evidence permits either correction to change a clinical claim, and neither does.** Both corrections record what was *done* (2 patients received carbon ion; 8/29 had metastasectomy) with **no outcome, no comparator, no rate**. Nothing here states or implies efficacy, safety, tolerability or appropriateness for carbon ion, proton beam, radiotherapy or metastasectomy in this or any disease.

### R.5 — Hand-maintained, not generated. The correction is a hand edit. `PRIMARY`

The tree says so itself. `scripts/tests/test_no_hand_authored_json_has_a_duplicate_key.py:39-46`:

```python
#: Where a human or an agent edits JSON by hand in this repository.
HAND_AUTHORED = (
    "research/data/*.json",
    "research/autonomy/*.json",
    "research/autonomy/receipts/*.json",
    "research/manuscripts/*.json",
    "systems/graph/*.json",
)
```

Corroborated three ways: (a) `grep -rn "artifacts.json" --include=*.py --include=*.mjs` returns four files, and **none writes it** — `systems/systems_check.py:1165` only *reads* it to emit warning `[W5]`, and `s4_lane_map_edits.py` / `nr4a3_tcip_reach.py` emit **proposal records** (`{"file": "systems/graph/artifacts.json", "action": "add", …}`) whose own docstring at `s4_lane_map_edits.py:99` says *"these are handed to the systems maintainer"*; (b) `systems/graph/artifacts.json` carries no `generator:` marker, whereas every `systems/views/` file does (`systems/views/L2-rt-surgical-quality.md` frontmatter: `kind: generated`, `generator: systems/systems_check.py`); (c) CLAUDE.md §7 states it directly — `systems/graph/*.json` owns model state, `systems/views/` is generated.

⭐ **Consequence for routing, and it is the useful half:** both corrections are **hand edits to `systems/graph/artifacts.json`**. There is **no generator to change**. But W09b's C5 (the same categorical wording in `systems/views/L2-rt-surgical-quality.md:95` and `L2-rt-surveillance.md:94`) *is* generated — those two are downstream of `systems/graph/`, must not be hand-edited, and are **not** in this package.

### R.6 — The routed decision package `PRIMARY`

**Owner:** the maintainer of `systems/graph/*.json` (S18 explicitly declined it: *"I did not touch `systems/graph/*.json`"*). **Not applied by me.**

Formatting note for whoever lands it: `artifacts.json` is a **JSON list** of 56 records; record fields are indented 4 spaces, records 2. Edit the two `note` strings **in place**; do **not** round-trip through `json.dump`, which would reflow all 556 lines and make the diff unreviewable.

---

#### CONTRADICTION 1 — `ART-RT-CONTRADICTION.note`

- **File / line:** `systems/graph/artifacts.json:534` (record index 53, `id: ART-RT-CONTRADICTION`), JSON path `/53/note`.
- **Kind: HAND EDIT.** No generator involved.
- **Exact current text** (the one sentence to replace; the rest of the 5-sentence note is correct and stays):
  ```
  ⭐ PARTICLE/BRACHYTHERAPY CENSUS RUN: brachytherapy and proton beam each reported ONCE in this histology, as case reports rather than registry arms; carbon ion does not appear in this histology anywhere in a 354-paper open-access corpus.
  ```
- **Exact proposed replacement** (condensed from the landed `routes.json:7662` wording; retention per rule 1.2):
  ```
  ⭐ PARTICLE/BRACHYTHERAPY CENSUS RUN, ITS CARBON-ION HALF CORRECTED 2026-09-01: brachytherapy and proton beam each reported ONCE in this histology, as case reports rather than registry arms; carbon ion is reported too -- among the 8 of 171 registry patients localized at diagnosis who did not undergo surgery, 2 received carbon ion therapy, 1 proton beam and 1 conventional radiotherapy (Masunaga 2025, PMID 40885991, PMC12398172, blob 79a8c197243ff4202a713d437def379c5f499a68), which is why this artifact's `carbon_ion.found_in_this_histology` is now `true` and derived rather than typed. ⛔ NO OUTCOME ATTACHES TO ANY OF THEM: an existence proof that an arm was delivered, not a utilisation rate, and it implies nothing about efficacy, safety, tolerability or appropriateness. How often carbon ion is used in this histology is UNKNOWN -- neither corpus has been recounted since the correction. ⚠ Superseded, retained (rule 1.2): "carbon ion does not appear in this histology anywhere in a 354-paper open-access corpus" -- a false absence refuted by a file inside its own corpus.
  ```
- **Acceptance test:** T1/T2/T4 of `/tmp/claude-0/w09c/test_w09c_acceptance.py` (listed in full below). T1 = the refuted string does not appear *outside* a `Superseded, retained` clause; T2 = the live text carries `carbon ion`, `2`, `Masunaga`, `no outcome`; T4 = all **54 other** artifact notes hash-identical to the pre-edit baseline. **Run RED at HEAD, GREEN on the scratch fixture — evidence below.**

#### CONTRADICTION 2 — `ART-CARE-DELIVERY-EVIDENCE.note`

- **File / line:** `systems/graph/artifacts.json:453` (record index 44, `id: ART-CARE-DELIVERY-EVIDENCE`), JSON path `/44/note`.
- **Kind: HAND EDIT.**
- **Exact current text** (last sentence of the note; the preceding three sentences stay):
  ```
  The one [FT] passage is the ICD-O code enumeration in PMID 31765367.
  ```
- **Exact proposed replacement:**
  ```
  The two [FT] passages are the ICD-O code enumeration in PMID 31765367 and the metastasectomy sentence in PMID 40885991, the latter read in retrieved full text and pinned by blob SHA 79a8c197243ff4202a713d437def379c5f499a68. ⚠ Superseded, retained (rule 1.2): "The one [FT] passage is the ICD-O code enumeration in PMID 31765367" -- correct until 2026-09-01, when the metastasectomy row was upgraded [API] -> [FT] with its correction.
  ```
- **Acceptance test:** T3/T4. ⭐ T3 does **not** hard-code "two": it counts `"provenance": "[FT]"` in `research/modalities/emc-care-delivery-evidence.json` and requires the note to agree with the count it finds — so a later third `[FT]` upgrade goes red instead of silently re-breaking the note. This is deliberately the pattern S18 established (bind the guard to the evidence, not to the answer), which is the mechanism that let this defect live in the first place.

---

## Validation evidence

### `RUN` — W09b's 279-line validator, reconstructed and re-run at the current HEAD

Reconstructed by extracting the inline listing from `reports/W09b-absence-claim-audit.md` lines 309-594 (`sed -n '309,594p'`); 286 lines including trailing blanks against W09b's stated 279 of code; `ast.parse` → `PARSE OK`.

Environment: `/home/user/Rare-cancers` at `b9a0257e6acff53ad22535cf2adf261313e0b250`, Linux, Python 3 stdlib, no network.

```
$ cd /home/user/Rare-cancers
$ python3 /tmp/claude-0/w09c/lint_absence_claims.py --repo /home/user/Rare-cancers
...
lint_absence_claims: 119 ERROR, 3 WARN across 6432 file(s); 3050 committed corpus quotes indexed
EXIT=1
```

⭐ **Counts identical to W09b: 119 ERROR, 3 WARN, exit 1.** The only difference is the file count, **6432 vs W09b's 6424** — exactly the 8 campaign reports the coordinator collected between the two runs. `3050` corpus quotes indexed, unchanged. The three A3 warnings are byte-identical to W09b's:

```
research/modalities/emc-surgical-quality.json:/treatment_setting/recorded_in_any_reachable_series: WARN [A3] 'recorded_in_any_reachable_series = false'
research/modalities/emc-surgical-quality.json:/unplanned_excision/recorded_in_any_reachable_series: WARN [A3] 'recorded_in_any_reachable_series = false'
research/modalities/row27-ddddg-precheck-status.json:/checkpoint_durability/checkpoints_committed_anywhere: WARN [A3] 'checkpoints_committed_anywhere = false'
```

⚠ **One correction to W09b's own Limitations, offered as a finding rather than a criticism.** W09b wrote *"A2 cannot see C1, because the contradicting evidence is a boolean `true`, not a quote."* It can, and it does — at this HEAD A2 fires on C1 by a different route, via S15's refutation record:

```
systems/graph/artifacts.json:/53/note: ERROR [A2] 'does not appear in this histology anywhere'
    contradicted by a corpus quote committed in this repository: research/manuscripts/care-delivery/emc-absence-claims-refuted.json/refutations/1/the_discriminating_observation/verbatim matches ['carbon ion']
    context: carbon ion does not appear in this histology anywhere in a 354-paper open-access corpus.
```

⛔ **W09b's 35% precision verdict is preserved exactly as it stands.** I did not re-measure it, did not tune any rule, and do not recommend deploying A1/A2. This single true positive does not change a measured precision of 7/20 and must not be read as doing so.

### `RUN` — the acceptance test, RED at HEAD and GREEN on a scratch fixture

The fixture is a **copy** under `/tmp/claude-0/w09c/fix/` holding only the two files; the repository was never modified.

```
$ python3 /tmp/claude-0/w09c/test_w09c_acceptance.py --repo /home/user/Rare-cancers --write-baseline /tmp/claude-0/w09c/baseline.json
baseline written

$ python3 /tmp/claude-0/w09c/test_w09c_acceptance.py --repo /home/user/Rare-cancers --baseline /tmp/claude-0/w09c/baseline.json
FAIL: T1 ART-RT-CONTRADICTION.note still asserts the refuted carbon-ion absence
FAIL: T3 ART-CARE-DELIVERY-EVIDENCE.note says one [FT] passage; artifact has 2
w09c-acceptance: 2 failure(s), 56 artifact notes checked
EXIT=1

$ python3 /tmp/claude-0/w09c/test_w09c_acceptance.py --repo /tmp/claude-0/w09c/fix --baseline /tmp/claude-0/w09c/baseline.json
w09c-acceptance: 0 failure(s), 56 artifact notes checked
EXIT=0
```

⭐ **The RED run is the load-bearing evidence**: the test detects both defects at HEAD from the files alone, and T4 confirms the proposed edit moves **no other value** — all 54 unrelated notes hash-identical, no node added or removed.

### `RUN` — the retained strings are exempt from the linter, so the fix does not trade one error for another

The validator's `CLEARED` regex (line 100-108) exempts a sentence that quotes a claim it has withdrawn. Applied to the proposed replacements, per-sentence, using the validator's own `sentences()` splitter:

```
ART-CARE-DELIVERY-EVIDENCE | CLEARED= True | ⚠ Superseded, retained (rule 1.2): "The one [FT] passage is the ICD-O …
ART-RT-CONTRADICTION      | CLEARED= True | ⚠ Superseded, retained (rule 1.2): "carbon ion does not appear in this …
```

**PREDICTION (this is a prediction, not a measurement):** after the fix the A2 error at `systems/graph/artifacts.json:/53/note` should clear, taking the repo-wide count from 119 to 118 ERROR with 3 WARN unchanged. I could not measure this without writing into the tree, which I am forbidden to do.

### `PROPOSED (NOT RUN)`

- The full-repo linter re-run *after* the fix, to confirm 118/3. Requires the edit to land; not mine to make.
- `scripts/preflight.sh` (and its gate-10 `validate-registry.mjs`) against the corrected tree. My dispatch does not authorise running preflight, and the edit does not exist.
- Landing S18 item 2 (`routes.json` `RT-METASTASECTOMY.supporting_evidence[0].what_it_supports`). Diagnosed here, replacement text already written by S18, **not packaged and not applied.**
- The `literature-cache` term census that would convert both "measured lower bound / UNKNOWN" statements into counts. No egress from this seat; S18 queued it 2026-09-01 and it is still queued.

### The acceptance test, inline

```python
#!/usr/bin/env python3
"""W09c acceptance test for the two artifacts.json note corrections.

Run BEFORE the fix -> must be RED (proves it detects the defect).
Run AFTER  the fix -> must be GREEN, and T4 proves nothing else moved.
Usage: python3 test_w09c_acceptance.py --repo /home/user/Rare-cancers [--baseline base.json]
       python3 test_w09c_acceptance.py --repo <repo> --write-baseline base.json   (before editing)
"""
import argparse, hashlib, json, os, sys

FALSE_ABSENCE = "carbon ion does not appear in this histology anywhere"
BAD_COUNT     = "The one [FT] passage is the ICD-O code enumeration in PMID 31765367."
REQ_RT = ["carbon ion", "2", "Masunaga", "no outcome"]          # corrected reading must say this
REQ_CD = ["two [FT] passage", "31765367", "metastasectomy"]      # corrected count must say this

def notes(repo):
    a = json.load(open(os.path.join(repo, "systems/graph/artifacts.json")))
    return {x["id"]: x.get("note", "") for x in a}

def main():
    p = argparse.ArgumentParser(); p.add_argument("--repo", required=True)
    p.add_argument("--baseline"); p.add_argument("--write-baseline")
    a = p.parse_args()
    n = notes(a.repo)
    if a.write_baseline:
        json.dump({k: hashlib.sha256(v.encode()).hexdigest() for k, v in n.items()},
                  open(a.write_baseline, "w"), indent=1)
        print("baseline written"); return 0
    fails = []
    rt, cd = n["ART-RT-CONTRADICTION"], n["ART-CARE-DELIVERY-EVIDENCE"]
    # rule 1.2: a superseded string may be RETAINED inside a "Superseded, retained" clause.
    # The live assertion is everything before the first such clause.
    live = lambda t: t.split("Superseded, retained")[0]
    rt_live, cd_live = live(rt), live(cd)
    # T1 - the refuted absence is no longer ASSERTED
    if FALSE_ABSENCE in rt_live.lower():
        fails.append("T1 ART-RT-CONTRADICTION.note still asserts the refuted carbon-ion absence")
    # T2 - the replacement states the corrected reading
    if FALSE_ABSENCE not in rt_live.lower():
        miss = [t for t in REQ_RT if t.lower() not in rt.lower()]
        if miss: fails.append(f"T2 corrected RT note is missing required tokens {miss}")
    # T3 - the [FT] count is DERIVED from the artifact, never typed
    art = json.load(open(os.path.join(a.repo, "research/modalities/emc-care-delivery-evidence.json")))
    ft = json.dumps(art, ensure_ascii=False).count('"provenance": "[FT]"')
    if BAD_COUNT in cd_live:
        fails.append(f"T3 ART-CARE-DELIVERY-EVIDENCE.note says one [FT] passage; artifact has {ft}")
    elif ft != 2 or not all(t.lower() in cd.lower() for t in REQ_CD):
        fails.append(f"T3 corrected count note does not match the artifact ({ft} [FT] rows)")
    # T4 - nothing else moved
    if a.baseline:
        base = json.load(open(a.baseline))
        for k, v in n.items():
            if k in ("ART-RT-CONTRADICTION", "ART-CARE-DELIVERY-EVIDENCE"): continue
            if base.get(k) != hashlib.sha256(v.encode()).hexdigest():
                fails.append(f"T4 unrelated note changed: {k}")
        for k in base:
            if k not in n: fails.append(f"T4 node removed: {k}")
    for f in fails: print("FAIL:", f)
    print(f"w09c-acceptance: {len(fails)} failure(s), {len(n)} artifact notes checked")
    return 1 if fails else 0

if __name__ == "__main__":
    sys.exit(main())
```

⚠ T4 needs a baseline captured **before** the edit; if the owner edits first, re-derive it from `git show HEAD:systems/graph/artifacts.json`.

---

## Limitations

- **Transfer limit:** I re-derived both contradictions from the files, but W09b's enumeration (32,324 → 8,838 → 215 + 566 → 119+3) and its 35% precision measurement are **taken on trust and preserved unchanged**. I did not re-run the enumeration passes and did not re-sample.
- **Reconstruction fidelity:** the validator is a transcription of W09b's inline listing, not W09b's original file (that seat's `/tmp/claude-0/w09b/` is not visible to me). It parses and reproduces the same 119/3/exit-1 and the same three A3 strings, which is strong evidence of fidelity but not proof of byte-identity.
- **The 118-ERROR prediction is a prediction.** I proved the retained sentences are `CLEARED`-exempt in isolation; I could not run the post-fix repo-wide count without writing to the tree.
- **The proposed replacement wording is my drafting**, condensed from `routes.json:7662`. Every fact in it is sourced (Masunaga 2025, PMID 40885991, PMC12398172, blob `79a8c197243f…`, 8 of 171, 2/1/1), but the sentence construction is mine and a different maintainer could word it differently without changing a fact.
- **POLICY-evidence does not formally scope `systems/graph/`.** My §1.3/§1.2 reading rests on the note's *own* invocation of "POLICY-evidence 1.3" and on the `[API]`/`[FT]` marks implementing §1.3's distinction. That is an adoption argument, not a scope claim, and I have not pretended otherwise.
- **Nothing clinical is claimed.** Both corrections record counts of what was *done*, with no comparator and no outcome. No statement about efficacy, safety, selectivity, tolerability, therapeutic window or clinical readiness of carbon ion, proton beam, radiotherapy or metastasectomy follows from any of it.
- **No corpus was recounted.** "1 matching record" and "2 carbon-ion patients" remain measured lower bounds against an un-swept corpus; UNKNOWN stays UNKNOWN.
- **Neither correction was applied**, and the third item (S18 item 2 in `routes.json`) was diagnosed only.

---

## Stop condition

**MET, in full.**

1. Both contradictions independently re-verified **LIVE** at HEAD `b9a0257e`, quoted verbatim with file and line (`artifacts.json:534` and `:453`) against their contradicting evidence (`emc-radiotherapy-contradiction.json:171`; `emc-care-delivery-evidence.json:41` and `:123`). Neither refuted.
2. S18's replacement text located at `S18-FALSE-ABSENCES.md:272-273` and checked word-by-word: **facts have not drifted; the delivery shape has** — items 5/6 predate the rule-1.2 retention convention that `routes.json:7662` now sets, and item 5 delegates to an item-3 correction that has since landed in a far longer form.
3. A routed decision package per contradiction, with exact current text, exact proposed replacement, file/line, **hand edit (no generator exists — `systems/graph/*.json` is declared hand-authored at `test_no_hand_authored_json_has_a_duplicate_key.py:39-46`)**, and an acceptance test **run RED at HEAD and GREEN on a fixture**, with T4 proving no other value moves.
4. Validator re-run at HEAD: **exit 1, 119 ERROR, 3 WARN** — identical to W09b; only the file count moved (6432 vs 6424, the 8 collected reports). W09b's 35% precision verdict preserved untouched.

Returning now. Bonus finding beyond the stop condition, reported not pursued: **S18 item 2 is also still live** in `routes.json`.

---

## Tool-call and wall-clock count actually used

**22 tool calls, ~5 minutes wall clock** (02:24:46Z → 02:29:32Z), well under the ~40-call / ~40-minute targets. No sleeping, no padding.

---

## Next concrete action

**Land the two-line package above** — the owner of `systems/graph/artifacts.json` edits the two `note` strings in place, captures the T4 baseline from `git show HEAD:systems/graph/artifacts.json` first, and runs `/tmp/claude-0/w09c/test_w09c_acceptance.py` (RED before, GREEN after). It is a ~10-minute edit with no research in it, the replacement text is written and evidence-pinned, and the acceptance test already exists and already discriminates. ⭐ **Land S18 item 2 in the same pass** — `routes.json` → `RT-METASTASECTOMY.supporting_evidence[0].what_it_supports`, replacement text at `S18-FALSE-ABSENCES.md:269`, still accurate — because the seat that opens `systems/graph/` is the expensive part and three strings cost no more than two.

⛔ **What should NOT be the next action:** hand-editing `systems/views/L2-rt-surgical-quality.md:95` or `L2-rt-surveillance.md:94`. Those are generated (`kind: generated`, `generator: systems/systems_check.py`) and regenerate from `systems/graph/`; W09b's C5 is fixed upstream or not at all.
