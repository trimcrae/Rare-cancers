> Collected by the campaign coordinator from this worker's in-response draft.
> Per-child runtime model evidence from the child transcript: `"model":"claude-opus-5"` (OBSERVED).

---

Stop condition met. Report follows.

---

## Worker

- **Worker:** W09d, lane 9 refill, OPUS-CAPACITY-CAMPAIGN-20260908.
- **Model identity: SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I report myself as Claude Opus 5 (`claude-opus-5`). `env` exposes no model variable; `AI_AGENT=claude-code_2-1-263_agent` and `CLAUDE_CODE_VERSION=2.1.42` are harness versions, not model identities. The coordinator should extract the runtime model from the transcript.
- **Write isolation: honoured.** Nothing written under `/home/user/Rare-cancers`; no git write operation of any kind. All execution under `/tmp/claude-0/w09d/`. **No file under `systems/views/` was hand-edited.** Neither correction was applied to the repository.
- **HEAD actually read: `7d081218f107363573573e6d102e4334567adf77`**, unchanged at start and end. ⚠ This is **not** the brief's frozen commit `92abbcb905…`, nor W09c's `b9a0257e`. The tree has advanced again as the coordinator collects reports. `git status --porcelain` showed 1 entry at end (coordinator-collected report churn); none of the five files I analyse is modified or untracked.
- **Sources read:** the live cloud checkout at `/home/user/Rare-cancers` (primary), plus the frozen read-only corpus at `/tmp/claude-0/frozen-corpus/extracted/` (used once, for the S18 item-2 cross-check).

`date -u` at start: `Tue Sep  8 02:34:18 UTC 2026`. At end: `Tue Sep  8 02:37:5x UTC 2026` (last recorded stamp `Tue Sep  8 02:36:22 UTC 2026`).

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

Do the two generated views (`systems/views/L2-rt-surgical-quality.md:95`, `L2-rt-surveillance.md:94`) inherit W09b's C5 wording — *"treatment setting is reported by no reachable series"* — from `systems/graph/artifacts.json`, such that landing W09c's routed package would fix them? Or do they carry the false absence from an independent source, making W09c's package **necessary but not sufficient**?

It is open because W09b routed C5 as "fix belongs upstream in `systems/graph/`" without naming which file or field, and W09c flagged the ambiguity explicitly but did not resolve it — W09c's package touches only `artifacts.json`, and nobody had tested whether that propagates.

**Answer, established by construction: they carry it independently. W09c's package fixes zero view lines. And the string reaches FIVE views, not two.**

---

## Prior-work check

Commands run and what they showed:

- `grep -n "C5" research/autonomy/opus-capacity-campaign-20260908/reports/W09b-absence-claim-audit.md` → line 202 is W09b's C5 row, which names exactly the two files `L2-rt-surgical-quality.md:L95` and `L2-rt-surveillance.md:L94` and says only *"the fix belongs upstream in `systems/graph/`, not here."* No file or field named. **Open.**
- `sed -n '...' reports/W09c-artifacts-contradiction-package.md` (via the persisted full text) → W09c R.5 ends: *"But W09b's C5 … **is** generated — those two are downstream of `systems/graph/`, must not be hand-edited, and are **not** in this package."* W09c states the boundary and stops there. **Open, and explicitly handed on.**
- `grep -rn "treatment setting is reported by no reachable series" --include=*.json --include=*.py --include=*.md systems/ research/` → **6 hits: 1 source (`systems/graph/publications.json:119`) and 5 generated views.** Zero hits in `systems/graph/artifacts.json`. This alone falsifies the inheritance hypothesis; the regeneration test below proves it.
- `grep -rn "measured absence of any EMC metastasectomy record" --exclude-dir=.git .` → 3 live hits (S18 item 2's target at `routes.json:8536`, a generated view at `L2-rt-metastasectomy.md:50`, plus W09c's own report quoting it). Cross-checked in the frozen corpus: same two paths, **same line numbers** (`corpus/systems/graph/routes.json:8536`, `corpus/systems/views/L2-rt-metastasectomy.md:50`).
- `CLOSED-WORK.md` read in full. I am not replaying: PUB-EMC-CLASSIFICATION (user-rejected), any Brenca route, lane 11's source-index, the NR4A Perspective refusal, or any denied external route. **No network was used at all.**

---

## Method / inputs

| input | role |
|---|---|
| `/home/user/Rare-cancers` @ `7d081218` | the live tree under test (read-only) |
| `systems/systems_check.py` (4000+ lines) | the declared generator (`generator:` frontmatter of every view) |
| `systems/graph/artifacts.json` (56 records) | W09c's package target |
| `systems/graph/publications.json` (33 records) | the actual C5 source, found by grep |
| `systems/graph/routes.json` | S18 item 2's target |
| `systems/views/` (111 files) | the generated layer |
| `systems/POLICY-evidence.md` | read in full before any conclusion, as instructed |
| `research/autonomy/sprint-2026-09-01/S18-FALSE-ABSENCES.md:262-275` | S18's six queued items, verbatim |
| `research/modalities/emc-care-delivery-evidence.json` | the evidence that item 2's replacement rests on |
| `/tmp/claude-0/frozen-corpus/extracted/corpus/` | absence/identity cross-check only |
| `/tmp/claude-0/w09d/copy/` | scratch copy via `tar --exclude=./.git`, the only place anything was executed or modified |

Python 3 stdlib only. No network, no paid API, no GPU.

---

## Result

### R.1 — The generator lines that produce the C5 string. `PRIMARY`

The string is **not** rendered from `artifacts.json`. It is the `why_not_written` field of publication `PUB-CARE-DELIVERY`, emitted by two separate code paths.

**Path A — the L2 route view** (this is the one that produces W09b's two lines). `systems/systems_check.py:3034-3047`, verbatim:

```python
    pr = r.get("publication")
    if pr:
        p = by_id(g["publications"])[pr["endpoint"]]
        title, path = _pub_title(p)
        out += ["## Where this route ends — the paper\n",
                f"**[{pr['endpoint']}](L3-publications.md)** — "
                + (f"[{esc(title)}]({os.path.relpath(os.path.join(REPO, path), VIEWS).replace(os.sep, '/')})" if path
                   else f"*{esc(title)}* (unwritten)") + "\n",
                f"`{pr['role']}` · {PUB_GLYPH[p['state']]} `{p['state']}` · aimed at "
                f"`{p['target_venue']}`\n",
                f"**This route contributes:** {pr['contribution']}\n",
                f"**The paper would claim:** {p['what_it_would_claim']}\n"]
        if p.get("why_not_written"):
            out.append(f"**It is not written because:** {p['why_not_written']}\n")
```

Line 3047 is the emitter. Note `p = by_id(g["publications"])[pr["endpoint"]]` — the record is looked up in **`publications`**, keyed by the route's `publication.endpoint`. Every route whose endpoint is `PUB-CARE-DELIVERY` gets the identical paragraph. That is why the wording appears verbatim in four L2 views, not two.

**Path B — the L3 publications view.** `systems/systems_check.py:3239`:

```python
        if p.get("why_not_written"):
            out += [f"**Not written because:** {p['why_not_written']}\n"]
```

**The source field**, `systems/graph/publications.json:119`, record `PUB-CARE-DELIVERY` (record begins at line 112). The relevant clause, verbatim from the JSON value:

> `The third clause of what_it_would_claim, whether the diagnosis was known before the operation, is unstudiable in EMC from the reachable record: treatment setting is reported by no reachable series.`

### R.2 — `artifacts.json` `note` fields are never rendered into any view at all. `PRIMARY`

The generator touches `g["artifacts"]` only for **id/path cross-checks and one warning**, never to render note prose:

- `systems_check.py:468` — `by_basename = {os.path.basename(a.get("path", "")): a["id"] for a in g["artifacts"] if a.get("path")}` (path→id map)
- `systems_check.py:1159-1165` — builds `by_path` and emits warning `[W5]`
- `systems_check.py:1772` — `art = {a["id"] for a in g["artifacts"]}` (referential integrity)

The only two `note` renders in the file (`:2158`, `:4084`) belong to other collections. Confirmed empirically: `grep -rc "PARTICLE/BRACHYTHERAPY CENSUS RUN" systems/views/` returns **no non-zero file** — C1's sentence, 556 lines of hand-authored graph state, appears in **zero** generated views.

### R.3 — THE DELIVERABLE. Regeneration diff after applying W09c's package: **EMPTY.** `PRIMARY`

Both of W09c's proposed replacements were applied to the scratch copy's `artifacts.json` by exact in-place string substitution (each matched exactly once; no `json.dump` round-trip, per W09c's formatting warning), the views were regenerated with the repository's own generator, and the result diffed against the committed views:

```
$ diff -ru /tmp/claude-0/w09d/views-committed /tmp/claude-0/w09d/copy/systems/views
DIFF_EXIT=0
```

**Zero files differ. Zero lines differ. Across all 111 views.**

The control run (regenerate with **no** edit) also produced `DIFF_EXIT=0`, which establishes the generator is idempotent at this HEAD and that the empty post-fix diff is a real null, not a broken harness.

### R.4 — What the string *does* derive from, proved by a sentinel edit. `PRIMARY`

Replacing the 47-character clause in `publications.json` with `W09D-SENTINEL-TRACER` and regenerating changed exactly **five** files:

| view file | line | route / view |
|---|---|---|
| `systems/views/L2-rt-surgical-quality.md` | 95 | W09b's C5 hit #1 |
| `systems/views/L2-rt-surveillance.md` | 94 | W09b's C5 hit #2 |
| `systems/views/L2-rt-metastasectomy.md` | 94 | ⭐ **W09b did not report this one** |
| `systems/views/L2-rt-risk-model.md` | 95 | ⭐ **W09b did not report this one** |
| `systems/views/L3-publications.md` | 509 | ⭐ **W09b did not report this one** |

Sentinel present at exactly those five line numbers, nowhere else. **C5's blast radius is 5 view lines from 1 source field, not 2 from an unknown source.**

### R.5 — Verdict on W09c's package. `PRIMARY`

| question | answer |
|---|---|
| Do the views inherit C5 from `artifacts.json`? | **No.** Independent source. |
| Would landing W09c's package fix C5? | **No — it fixes zero view lines.** |
| Is W09c's package still correct? | **Yes, unchanged.** C1 and C2 are live defects in `artifacts.json` and W09c's routing, retention convention, acceptance test and no-generator finding all stand. |
| Is it sufficient for the C1/C2 defects it targets? | **Yes.** Precisely because notes are never rendered, C1/C2 have zero downstream propagation — the hand edit is complete in itself and needs no regeneration step. |
| Is it sufficient for C5? | **No.** C5 is a **separate defect in a separate file** — `systems/graph/publications.json`, `PUB-CARE-DELIVERY.why_not_written` — that W09b mis-routed as downstream of C3/C4 and that nobody has packaged. |

⭐ **The finding that is worth more than a confirmation, stated plainly:** W09b's C5 row implies the views inherited the wording from the surgical-quality artifact (it lists C5's "source" as C3/C4). They did not. C5 is a **sixth** live false-absence copy in `systems/graph/`, in a file neither W09b, W09c nor S18 examined — S18's table explicitly says *"I did not touch `systems/graph/*.json`"* and its six items name only `routes.json` and `artifacts.json`. `publications.json` has never been audited by this lane.

⚠ **I am not packaging a C5 correction.** Establishing whether *"treatment setting is reported by no reachable series"* is actually false requires reading the surgical-quality evidence and re-deciding a narrowing that W09b classified as C3/C4 — that is a distinct scientific judgement, and my dispatch is a propagation question. What I can state as measured: the C3/C4 narrowings W09b recorded have **not** been applied to `publications.json:119`, and its wording is categorical where W09b judged the underlying field warranted narrowing. The three A3 warnings W09c re-ran name the same two fields (`emc-surgical-quality.json` `treatment_setting` and `unplanned_excision`, both `recorded_in_any_reachable_series = false`).

### R.6 — S18 item 2, re-verified independently at `7d081218`. `PRIMARY`

**Current text, verbatim, read by `json.load` of `systems/graph/routes.json` at `RT-METASTASECTOMY.supporting_evidence[0].what_it_supports`** (file line **8536**; W09c did not record a line for this item, so this is a fresh locate):

```
the measured absence of any EMC metastasectomy record in a 554-record open-access corpus
```

**S18's replacement, verbatim from `research/autonomy/sprint-2026-09-01/S18-FALSE-ABSENCES.md:269`, right-hand column:**

```
the absence of any **comparative** EMC metastasectomy study; the operation itself is reported (8/29, Masunaga 2025) with no outcome attached
```

**Accuracy check against the evidence, not against S18's own prose:**

| assertion in the replacement | checked at | status |
|---|---|---|
| the operation is reported | `research/modalities/emc-care-delivery-evidence.json:115` — *"Eight patients (27.6%) underwent metastasectomy, including six, one, and one who underwent lung, bone, and lymph node resections, respectively."* | **supported** |
| 8/29, Masunaga 2025 | same row; 8 of the 29 who presented with distant metastases = 27.6% | **supported, arithmetic consistent** |
| no outcome attached | `emc-care-delivery-evidence.json:118` — *"The paper reports survival for this cohort split by whether advanced-stage CHEMOTHERAPY was given, never by whether a metastasectomy was performed. No comparator, no survival and no recurrence figure attaches to the eight."* | **supported** |
| what survives is the *comparative* absence | `routes.json` `RT-METASTASECTOMY.grade.value` — *"What is absent is a COMPARATIVE study: no reachable series studies metastasectomy as an intervention against a comparator, and the one comparison that exists is uninformative (Bishop 2019, salvage surgery p = 0.15 at n = 13)."* | **supported, and already landed in the sibling field** |

**Verdict: still accurate. No fact drift.**

⚠ **One shape drift S18 could not have known, and it matters for how the replacement should be written.** Since 2026-09-01 the sibling `RT-METASTASECTOMY.grade.value` has landed a *wider* correction than S18's item 2 anticipated: it now records local therapy of metastases in **all three** curated series — *"8 of 29 patients presenting with distant metastases in Masunaga; 8 lung metastasectomies and 2 radiofrequency ablations, counted as procedures rather than patients, among Chiusole's 59 patients of whom 26 were metastatic; 5 of the 13 who recurred distantly in Bishop"*. S18's `(8/29, Masunaga 2025)` is **true but now the narrowest of three**. Whoever lands item 2 should either keep the Masunaga figure as an exemplar (correct as written) or match the sibling's three-series scope — but must not present 8/29 as the total. This is the same drift class W09c found for items 5/6: the tree's canonical correction has grown past the summary S18 wrote for it.

⭐ **A propagation finding for item 2, and it is the mirror image of C5.** Unlike `artifacts.json` notes, `routes.json` `supporting_evidence[].what_it_supports` **is** rendered. Sentinel test: replacing that one string and regenerating changed exactly one file —

```
Files .../L2-rt-metastasectomy.md and .../L2-rt-metastasectomy.md differ
.../systems/views/L2-rt-metastasectomy.md:50:| `ART-CARE-DELIVERY-EVIDENCE` | W09D-ROUTES-SENTINEL | `direct` |
```

So landing S18 item 2 **does** clear a generated-view copy of the false absence (`L2-rt-metastasectomy.md:50`) for free, provided the lander runs `python3 systems/systems_check.py --write-views`. That regeneration step is not optional and is not in S18's item, which says only "replace".

### R.7 — POLICY-evidence.md, read before concluding `PRIMARY`

Read in full. Its `scope:` frontmatter binds *"Clinical and epidemiological evidence only — the EMC registry, the manuscript's meta-analysis, and any pooled proportion or interval derived from published cohorts"*, owned by `research/data/emc-clinical-registry.json` and enforced by `scripts/validate-registry.mjs`. **`systems/graph/publications.json` is outside that scope**, exactly as W09c found for `artifacts.json`. §2.6(h) is nonetheless the clause C5 engages by analogy — *"Selection bias is bounded by a census taken from the same denominator"* — and it is the reason a categorical "no reachable series" is the wrong shape: the honest form is the size of the non-reporting set, which for `treatment_setting` is currently the A3 warning, not a measurement.

⛔ **No clinical claim is made anywhere in this report.** Every count quoted (2 carbon ion, 1 proton beam, 1 conventional RT among 8 non-operated localized patients; 8/29 metastasectomy) is a count of **what was done**, with **no outcome, no comparator and no rate**. Nothing here states or implies efficacy, safety, tolerability, selectivity or appropriateness for carbon ion, proton beam, radiotherapy or metastasectomy in this or any disease. There is no wet lab and no clinical readiness claim.

---

## Validation evidence

Environment for every run below: scratch copy at `/tmp/claude-0/w09d/copy/`, produced by `tar --exclude=./.git` from `/home/user/Rare-cancers` @ `7d081218`. Linux, Python 3 stdlib, no network. `cmp` confirmed `artifacts.json` byte-identical between source and copy before any edit (`ARTIFACTS_IDENTICAL`).

### `RUN` — Control: regeneration with no edit is a no-op

```
$ cd /tmp/claude-0/w09d/copy && cp -r systems/views /tmp/claude-0/w09d/views-committed
$ python3 systems/systems_check.py --write-views
systems_check: wrote 111 view(s) to systems/views/
EXIT=0
$ diff -rq /tmp/claude-0/w09d/views-committed /tmp/claude-0/w09d/copy/systems/views
DIFF_EXIT=0
```

Idempotent. Any later diff is attributable to the edit alone.

### `RUN` — W09c's package applied, then regenerated

```
$ python3 /tmp/claude-0/w09d/apply_w09c.py
C1: occurrences of current text in file = 1
C2: occurrences of current text in file = 1
re-parse OK, records = 56
C1 applied: True
C2 applied: True
EXIT=0

$ cd /tmp/claude-0/w09d/copy && python3 systems/systems_check.py --write-views
systems_check: wrote 111 view(s) to systems/views/
EXIT=0

$ diff -ru /tmp/claude-0/w09d/views-committed /tmp/claude-0/w09d/copy/systems/views
DIFF_EXIT=0
```

⭐ **This empty diff is the deliverable.** Each replacement matched exactly once (guarded — the script `sys.exit`s on any count ≠ 1), the file re-parsed to 56 records, both notes verified changed in the parsed object, and the regenerated views are byte-identical to the committed ones. **W09c's package propagates to nothing.**

### `RUN` — Sentinel: `publications.json` is the real source of C5

```
$ # copy restored to pristine artifacts.json + publications.json first
occurrences in publications.json: 1
re-parse OK
GEN_EXIT=0
Files .../L2-rt-metastasectomy.md and ... differ
Files .../L2-rt-risk-model.md and ... differ
Files .../L2-rt-surgical-quality.md and ... differ
Files .../L2-rt-surveillance.md and ... differ
Files .../L3-publications.md and ... differ
.../L2-rt-risk-model.md:95:      ... W09D-SENTINEL-TRACER ...
.../L3-publications.md:509:      ... W09D-SENTINEL-TRACER ...
.../L2-rt-metastasectomy.md:94:  ... W09D-SENTINEL-TRACER ...
.../L2-rt-surveillance.md:94:    ... W09D-SENTINEL-TRACER ...
.../L2-rt-surgical-quality.md:95:... W09D-SENTINEL-TRACER ...
```

### `RUN` — Sentinel: S18 item 2 propagates to one view

```
occurrences: 1
re-parse OK
GEN_EXIT=0
Files .../L2-rt-metastasectomy.md and ... differ
.../systems/views/L2-rt-metastasectomy.md:50:| `ART-CARE-DELIVERY-EVIDENCE` | W09D-ROUTES-SENTINEL | `direct` |
```

### `RUN` — S18 item 2 live at HEAD

```
$ grep -n "the measured absence of any EMC metastasectomy record in a 554-record open-access corpus" systems/graph/routes.json
8536:        "what_it_supports": "the measured absence of any EMC metastasectomy record in a 554-record open-access corpus",
```
Read structurally via `json.load` → `RT-METASTASECTOMY.supporting_evidence[0].what_it_supports` returned the identical string. Cross-checked in the frozen corpus at the same path and line. **LIVE.**

### `PROPOSED (NOT RUN)`

- A packaged, acceptance-tested correction for `publications.json:119` `PUB-CARE-DELIVERY.why_not_written`. **Not written, not applied.** It needs the C3/C4 narrowing decision, which is not mine.
- Re-running W09b's `lint_absence_claims.py` after any of these edits. W09c already re-ran it at HEAD (119 ERROR / 3 WARN / exit 1) and predicted 118 after the C1 fix; I did not re-run it and did not re-measure anything.
- `scripts/preflight.sh`. My dispatch does not authorise it and no edit exists to gate.
- Landing S18 item 2, and the mandatory `python3 systems/systems_check.py --write-views` that must follow it.

---

## Limitations

- **Model identity is self-report.** Not independently verified from within this seat.
- **HEAD drift.** The tree moved from the brief's `92abbcb905…` → W09b's `103ff76f` → W09c's `b9a0257e` → my `7d081218`. All my line numbers are pinned to `7d081218` and will drift again.
- **The empty diff proves propagation, not correctness.** It shows W09c's package changes no view. It does not re-audit whether C1/C2 are defects — I took W09c's re-verification as given and did not independently re-derive the carbon-ion or `[FT]`-count evidence beyond confirming the `[FT]` row quotes.
- **I did not determine whether C5's claim is actually false.** I determined where it comes from and how far it reaches. Whether *"treatment setting is reported by no reachable series"* should be narrowed is W09b's C3/C4 judgement, and it remains unpackaged.
- **W09b's 35% precision measurement (7/20) and its non-deployable verdict on A1/A2 are preserved exactly.** I did not re-measure precision, did not run the linter, did not tune or read the prose rules, and nothing here bears on that verdict.
- **`tar --exclude=./.git` copies the working tree, not the Git object store.** The scratch copy carries the 1 uncommitted working-tree entry present at copy time; none of the five files under test was among them.
- **The frozen corpus is a selected snapshot** (`is_complete_repository: false`). Its agreement on `routes.json:8536` corroborates; its silence elsewhere would prove nothing.
- **No network.** No source was fetched, no external claim resolved.

---

## Stop condition

**MET, all four parts.**

1. **Generator path traced and quoted** — `systems_check.py:3034-3047` (L2 path, emitter at 3047) and `:3239` (L3 path), both reading `publications[…].why_not_written`; plus the proof that `artifacts.json` notes are read only at `:468`, `:1159-1165`, `:1772` and rendered nowhere.
2. **Propagation tested by regeneration in a scratch copy, diff shown** — `DIFF_EXIT=0`, zero files, against an idempotent control.
3. **The view string does NOT derive from `artifacts.json`** — the case the dispatch called "worth more than a confirmation". Real source identified as `systems/graph/publications.json:119` and confirmed by sentinel, with a blast radius of **5** views rather than the 2 W09b reported.
4. **S18 item 2 re-verified**, current text and replacement quoted verbatim, replacement checked against the underlying evidence: **still accurate**, one shape drift recorded, and its own one-view propagation measured.

---

## Tool-call and wall-clock count actually used

**25 tool calls** (all `Bash`; several issued as parallel pairs). **Wall clock ≈ 3.5 minutes** — `02:34:18Z` start, `02:36:22Z` last recorded stamp, report drafted immediately after. Well inside the ~40-call / ~40-minute target. Returned as soon as the stop condition was met; no padding.

---

## Next concrete action

**One task, for lane 9's next seat:** build the C5 package for `systems/graph/publications.json:119`, `PUB-CARE-DELIVERY.why_not_written` — the sixth false-absence copy, in the one `systems/graph/` file no seat has audited. Concretely: (a) settle whether *"treatment setting is reported by no reachable series"* is false or merely categorical, by reading `research/modalities/emc-surgical-quality.json` `treatment_setting` against W09b's C3/C4 narrowings and the A3 warning `recorded_in_any_reachable_series = false`; (b) if it must change, write the replacement under the rule-1.2 retention convention W09c established, matching the `routes.json:7662` precedent; (c) write an acceptance test that goes RED at HEAD on the source field **and** on all five view lines; (d) prove it GREEN on a scratch copy **with the regeneration step included** — which this report has now shown is mandatory for `publications.json` and `routes.json` edits and a no-op for `artifacts.json` edits. Apply nothing.

**Secondary, cheap, and independent:** whoever lands S18 item 2 must run `python3 systems/systems_check.py --write-views` in the same change, or `systems/views/L2-rt-metastasectomy.md:50` keeps the refuted wording. That regeneration requirement is measured here and is absent from S18's own instruction.
