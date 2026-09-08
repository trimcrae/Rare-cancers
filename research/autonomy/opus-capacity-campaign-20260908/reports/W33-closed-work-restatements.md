<!-- collected 2026-09-08T03:34:17Z by campaign coordinator; agent id aa705569f55cc31b7; transcript /root/.claude/projects/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/subagents/agent-aa705569f55cc31b7.jsonl;
     OBSERVED child model set: ['claude-opus-5']; single longest assistant turn;
     worker was read-only (no repository writes) -->

Stop condition met. Report follows.

---

## Worker

**W33** — standing-fact audit lane, OPUS-CAPACITY-CAMPAIGN-20260908. Object: `research/autonomy/opus-capacity-campaign-20260908/CLOSED-WORK.md` itself.

**Model identity: SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I report myself as Claude Opus 5 (`claude-opus-5`). No environment variable observed names a served model; the coordinator must extract the actual per-child runtime model from the transcript.

`date -u` at **start**: `Tue Sep  8 03:21:42 UTC 2026`
`date -u` at **end**: `Tue Sep  8 03:25:36 UTC 2026`

`git rev-parse HEAD` at **start**: `e2214d4f2145c138da44b11c3d59899a5349abfb`
`git rev-parse HEAD` mid-run (the read I pin CLOSED-WORK.md content to): `302c2b63f7cc3ff16e2690de46e90a644181635f`
`git rev-parse HEAD` at **end**: `ff6bb018936451d0c2d60fb4a2aa7ae8ba932d7f`
HEAD moved three times under me. **All CLOSED-WORK.md line numbers and quotes below are pinned to the file as it stood when I read it at `302c2b63`; its bytes did not change across my run (`mtime` Sep 8 01:49, 70 lines, 4893 B).**

`git status --porcelain` → **empty (0 lines) at start and at end.** I wrote nothing into `/home/user/Rare-cancers` and nothing under `/tmp/claude-0/frozen-corpus/`. My scratch dir `/tmp/claude-0/w33/` was created and is **empty** — I needed no scratch files. No git write operation. **No network of any kind; no MCP call; no WebFetch/WebSearch; no `curl`.** I did not probe, retry, rephrase or route around a single denied route, and I did not approach the blocked NR4A Perspective under any label. I did not run `scripts/preflight.sh`.

Literal output of `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` at **start** (verbatim):

```
CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1
CLAUDE_CODE_ACCOUNT_UUID=4c503081-e4c3-45a1-8002-1cb705f46605
CLAUDE_CODE_CHILD_SESSION=1
no_proxy=localhost,127.0.0.1,::1,127.0.0.0/8,0.0.0.0/8,::,169.254.0.0/16,api.anthropic.com,api-staging.anthropic.com,api-pr-preview.anthropic.com,mcp-proxy.anthropic.com,mcp-proxy-staging.anthropic.com,registry.npmjs.org,jsr.io,npm.jsr.io,pypi.org,files.pythonhosted.org,index.crates.io,proxy.golang.org,host.docker.internal,10.0.0.0/8,172.16.0.0/12,192.168.0.0/16,100.64.0.0/10,.svc.cluster.local,*.svc.cluster.local
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
GLOBAL_AGENT_NO_PROXY=<same list as no_proxy>
ANTHROPIC_BASE_URL=https://api.anthropic.com
CLAUDE_CODE_DIAGNOSTICS_FILE=/tmp/claude-code-303934770.diag.log
CLAUDE_ENABLE_STREAM_WATCHDOG=1
CLAUDE_CODE_REMOTE_HERMETIC_MODE=0
CLAUDE_CODE_ENVIRONMENT_RUNNER_VERSION=release-ba76006550-ext
CLAUDE_CODE_DISABLE_BUILTIN_ANTMCP=1
CLAUDE_ADDITIONAL_DIRECTORIES=/mnt/user-data
JAVA_TOOL_OPTIONS=<proxy/truststore flags, no model name>
NO_PROXY=<same list as no_proxy>
CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=1
CLAUDE_CODE_USE_CCR_V2=true
CLAUDE_CODE_SYNC_SESSION_REFS=1
DOCUMENTS_MCP_SCRATCH_ROOT=/mnt/user-data/working/claude-docs
CLAUDE_CODE_TEE_SDK_STDOUT=true
CLAUDE_CODE_ENTRYPOINT=remote
CLAUDE_CODE_VERSION=2.1.42
CLAUDE_CODE_EXECPATH=/opt/claude-code/bin/claude
npm_config_noproxy=<same list as no_proxy>
CLAUDE_CODE_REMOTE_SEND_KEEPALIVES=true
CLAUDE_CODE_REMOTE=true
CLAUDE_CODE_POST_FOR_SESSION_INGRESS_V2=true
CLAUDE_CODE_ORGANIZATION_UUID=9f10e945-e412-4b71-8a9d-5d6affcd7d4f
CLAUDE_SESSION_INGRESS_TOKEN=<redacted>
CLAUDE_CODE_SYNC_SKILLS=1
CLAUDE_CODE_HOLD_UNANSWERED_PARKED_PERMISSION=1
CLAUDE_CODE_MESSAGING_TOKEN=<redacted>
```

The same command at end returned the identical set (I elided the four long proxy-list variables above for readability and note the elision explicitly; nothing in them names a model). **No variable names a served model — the environment cannot corroborate my self-report.**

---

## Question

**Is every closure record in `CLOSED-WORK.md` — the campaign's densest standing-fact document, read by every worker and audited by none — accurate against the committed record, and where it is not, what is the smallest restatement that preserves the closure?**

Open because three reports (W21b, W21c, W23b) have now independently shown that a false standing fact in this campaign's own briefing text propagates into worker reports before anyone catches it, and because `CLOSED-WORK.md` is the one briefing document that has never been checked against its own sources.

---

## Prior-work check

Read in full at `302c2b63`: `COMMON-BRIEF.md`, `CLOSED-WORK.md`, `CORPUS-CONTEXT.md`, `SAFETY-EVENTS.md`, and `reports/W21b`, `W21c`, `W23b`. Read in part: `reports/W01b`, `W11b`, `W11c`, `W07g`, `W13b`, `W13c`, `W20`, `WAVE-LOG.md`.

Commands (all read-only, exit 0):

```
$ grep -rn -i 'CLOSED-WORK|false standing fact|premise|corrected root|propagat' W21b*.md W21c*.md W23b*.md
$ grep -rn -i 'pazopanib|24703573|32856598|35144048' reports/          → 40 hits, all compliance statements
$ git ls-files | grep -c 'clinical-methods-checkpoints-2026-09-07'      → 0
$ git ls-files | grep -c 'cycle-outcomes/20260905T133448Z-6bd43b913c'   → 0
$ git ls-files | grep -c 'peerj-validation-audit-2026-09-07'            → 0
$ find /tmp/claude-0/frozen-corpus/extracted/corpus -path '*<each>*'    → present (see Result)
```

**Not duplicating W21d.** My object is `CLOSED-WORK.md`; I graded no report for novelty and audited no report's absence claims. I read reports only as *evidence about closures*.

**Closed items I confirm I am not replaying, reopening, re-grading or relabelling:** the blocked NR4A Perspective (not approached under any label, framing or agent; I did not read `research/manuscripts/nr4a-reagents/` and made no attempt to characterise the refusal); the user-rejected registry ICD-O paper; Davis / Hofvander / Brenca / promoter-transfer / inverse-bounds gates; **every** unrecovered source (Pazopanib, anthracycline, Sunitinib 2014, Trabectedin/RT 2018, Wagner 2020, CTARC 2022) — I issued zero requests of any kind, so no denied route was tested, probed or rephrased; the lane-11 source-index bundle (Lane 11 is sole owner; I propose no source-index change); `GSE4303`/`GSE28866`; W25 and its held continuation (`SAFETY-EVENTS.md`) — I did not touch it. I invented no cohort, made no clinical claim, and draw no patient, independence or denominator conclusion from anything below.

**A note on my own method's limits, stated up front:** for six of the closures the accuracy check *is* the denied route, and testing it is forbidden. I therefore graded those on the committed record alone, and where the record cannot settle them I say `UNVERIFIABLE-FROM-THE-RECORD` rather than guessing. **That grade never means "reopen".**

---

## Method / inputs

- **Live checkout** `/home/user/Rare-cancers`, HEAD as pinned above. `git ls-files` and `grep` over the tracked tree.
- **Frozen corpus at the CORRECTED root** `/tmp/claude-0/frozen-corpus/extracted/corpus/` — read **in place**, not copied, not overlaid, not written. Also `…/extracted/metadata/closed-source-and-ownership-map.md` and `…/extracted/metadata/tracked-file-map.txt`.
- **The decisive input, which no prior worker used for this purpose:** `CLOSED-WORK.md:3` says it is *"Transcribed from the campaign admission"*, and `CORPUS-CONTEXT.md:47` says `metadata/closed-source-and-ownership-map.md` *"retains the original compact map **verbatim**"*. **The corpus therefore contains CLOSED-WORK.md's own source document.** My primary method is a line-by-line comparison of the transcription against that source, plus a check of every path and number either document names.
- Tools: `grep`, `find`, `git ls-files`, `ls`, `cat`, `python3` (stdlib `json` only, to read one JSON file). No network client of any kind.

---

## Result

### Summary

**The audit found real defects. `CLOSED-WORK.md` is not clean.** I graded **20 closure records**. **Every closure's verdict survives — I found no closure that should be reopened, and I reopened none.** But **9 of 20 records are non-CONFIRMED**, and the defects cluster in exactly the two shapes the campaign was warned about.

| Grade | Count |
|---|---|
| CONFIRMED | 11 |
| SUPERSEDED | 4 |
| OVER-SCOPED | 2 |
| UNVERIFIABLE-FROM-THE-RECORD | 3 |

**The single systemic finding, stated plainly:** the source map names a **canonical retained-evidence path for nine of its closures**. `CLOSED-WORK.md` **dropped every one of them.** Those paths are **absent from the live checkout** and **present and readable in the frozen corpus**. So the campaign's closure document tells 30-plus workers that a source is unrecovered while withholding the pointer to the retained evidence that says *what exactly* was retained — and two of the pointers it did keep, it mislabelled `(pending input)` when the input has been readable since the corpus went live at ~02:30Z. This is the same false-absence shape as W21c's M1 and W23b's W23-C, arriving from the opposite direction: not "absent when present", but **"pending when available"**.

---

### PRIMARY — path evidence underlying every grade below

`git ls-files | grep -c` in the live tree vs `find` at the corrected corpus root:

| Path named by the source map | live tree | corrected corpus root | tracked-map rows |
|---|---|---|---|
| `research/autonomy/clinical-methods-checkpoints-2026-09-07/` | **0** | **PRESENT** (10+ files incl. `inverse-bounds-assessment.txt`, `conditional-recurrence-gate.json`, `protocol-freeze.json`) | — |
| `research/autonomy/cycle-outcomes/20260905T133448Z-6bd43b913c/` | **0** | **PRESENT** (incl. `atlas-primary-matrix-availability.json`) | — |
| `research/autonomy/peerj-validation-audit-2026-09-07/` | **0** | **PRESENT** (incl. `final-handoff/integration.json`, `validation/linux-full-7baf2727/`) | — |
| `research/autonomy/pazopanib-exposure-gate-2026-09-07/` | **0** | **PRESENT** | 3 |
| `research/autonomy/anthracycline-exposure-gate-2026-09-07/` | **0** | **PRESENT** | 4 |
| `research/autonomy/sunitinib-primary-recovery-2026-09-07/` | **0** | **PRESENT** | 3 |
| `research/autonomy/trabectedin-case-deduplication-2026-09-08/` | **0** | **PRESENT** | 3 |
| `research/manuscripts/fusion-output/emc-fourth-cohort-sra-2026-08-08.md` | **PRESENT** | PRESENT | — |
| `research/manuscripts/fusion-output/gse28866-tumour-vs-normal-reading.md` | **PRESENT** | PRESENT | — |
| `parallel-followups-20260908/seer-source-followup/` (SEER/Noone) | **0** | **0** | **0** |
| `research/autonomy/source-reuse-program-2026-09-08` | **0** | **0** | **0** |

The last three rows are consistent with the map's own words — it calls the SEER material *"preserved **privately**"* and the source-reuse archives *"uncommitted"*. Their absence is **expected and correct**, and per `CORPUS-CONTEXT.md:41-45` remains **UNKNOWN**, never proof of repository-wide absence.

---

### Entry-by-entry audit

Quotes are verbatim from `CLOSED-WORK.md` at `302c2b63`, with line numbers. "Map" = `metadata/closed-source-and-ownership-map.md` at the corrected corpus root.

---

**C01 · L7 — ownership.** *"- ASO/NAT submission and the Qeios version history belong to the submission owner / user."*
**Kind:** ownership assignment (a route is owned elsewhere and remains so).
**Grade: CONFIRMED.** Map L9 states the same. No campaign report touches it; `W18:67` confirms non-touch.

---

**C02 · L8 — dissemination.** *"- The tissue-RNA paper is already disseminated."*
**Kind:** a question was answered (do not re-submit).
**Grade: CONFIRMED.** Map L9: *"Tissue-RNA paper already disseminated; no duplicate submission or manufactured rewrite."* Faithful.

---

**C03 · L9-11 — frozen external-validation comment.** *"- Frozen external-validation comment `7baf272705d7a629f6d21d4fc169a7188775a60b` has completed / writing, actual Linux FULL evidence and publication evidence. Qeios receipt `5848` is pending / public posting. **Do not edit or re-review these frozen deliverables.**"*
**Kind:** a deliverable is frozen and complete.
**Grade: OVER-SCOPED (verdict survives; a stated limitation was dropped).** This is the **W23b shape**.
The verdict is right and the evidence checks out. `…/final-handoff/integration.json` at the corrected corpus root gives `"full_exit": 0` and `"publication_bar_passed": 8`, so *"actual Linux FULL evidence and publication evidence"* is **supported** (and is an addition beyond the map, which says only *"writing complete"*). `status` = `"preprint_submission_ready_handed_to_submission_owner"`; `scope` = *"no posting is claimed here"*, so *"pending public posting"* is right.
**What was dropped is load-bearing.** The same file states `"remaining_source_limit": "Actual analyzed S6B cohort and original external normalization inputs remain unidentified. Reconcile substantive source clarification or venue feedback before changing the frozen paper."` Map L7 carries this as *"Actual S6 cohort/input uncertainty and author correspondence remain with submission owner."* **`CLOSED-WORK.md` carries neither.** A worker reading only `CLOSED-WORK.md` learns the deliverable is complete and would not learn that an unresolved cohort-identification limit stands on it. Also dropped: the map's *"exact nine-file family"* and the source path.
**Smallest correct restatement (verdict preserved):** *"Frozen external-validation comment `7baf2727…` — the exact nine-file family — has completed writing, Linux FULL evidence (`full_exit: 0`) and publication evidence (8 bar clauses passed); source `research/autonomy/peerj-validation-audit-2026-09-07/final-handoff/integration.json` (corpus-only, absent from the live checkout). **An unresolved source limit stands and belongs to the submission owner: the analysed S6B cohort and the original external normalization inputs remain unidentified.** Qeios receipt `5848` is pending public posting. Do not edit or re-review these frozen deliverables."*

---

**C04 · L14-17 — NR4A Perspective refusal.** *"- The restricted prior NR4A Perspective review hit an actual biology-access refusal and was / closed without probes, rephrasing or rerouting. **Do not recreate that review under another / label, agent or framing.**"*
**Kind:** a route was denied and remains denied (content-policy).
**Grade: CONFIRMED — and I did not test, approach or characterise it.** Map L8 matches. The closure stands exactly as written and I propose **no change to this entry**, including no wording change: any restatement of a refusal record risks reading as a re-grade.
One observation offered without acting on it: the map (L8) and `integration.json` (`bio_access_observation`) both add *"with no causal passage identified"* / *"without an identified passage or cause"*, which `CLOSED-WORK.md` omits. I note this **only** to record that the omission makes the closure look more diagnosed than it is; **I recommend no edit here**, because the safest handling of a refusal record is to leave it untouched. Flagged for the coordinator, not repaired by me.

---

**C05 · L20 — Davis.** *"- Paired Davis validation: negative."*
**Kind:** a scientific conclusion is settled (negative).
**Grade: UNVERIFIABLE-FROM-THE-RECORD.** Map L10: *"Paired Davis patient validation: completed negative coverage checkpoint."* The transcription drops *"patient"* and *"coverage checkpoint"*, which are what make the claim specific. Neither document names a retained record, and I could locate no artifact under the label "paired Davis" in the live tree or at the corrected corpus root. A worker cannot check what was negative, or of what.
This is **not** a challenge to the verdict — `W01b:R2` independently records that the Davis MI-ONCOSEQ 6 EMC cases exist and were obtainable only by formal request to journal editors, which is consistent with a completed paired checkpoint.
**Smallest correct restatement:** *"Paired Davis **patient** validation: completed **negative coverage checkpoint**. No canonical retained path is recorded for it; the basis is UNKNOWN to workers and must not be reconstructed."*

---

**C06 · L21 — Hofvander.** *"- Hofvander: one `TAF15` case, raw data controlled-access via EGA."*
**Kind:** a source is unrecovered (controlled-access), and a fact is settled (n=1).
**Grade: CONFIRMED.** Map L10 matches exactly. Corroborated in the campaign record by `W21c:201`, which states independently that *"Hofvander's TAF15 raw data remain controlled-access via EGA"* while correcting a different report's EGA claim. No worker retrieved it; no EGA route was opened.

---

**C07 · L22 — Brenca.** *"- Brenca: case identities unresolved."*
**Kind:** a question was answered in the negative (identities unresolved).
**Grade: CONFIRMED — with a scope note the coordinator should hold.** Map L10 matches. `W01b` exhausted 14 genuinely distinct routes and reports **UNRECOVERED**, explicitly recording *"The correct status is unrecovered-from-here, not nonexistent"* and that the deposit being controlled-access is **UNKNOWN** — *"not a Hofvander/EGA-style resolved controlled-access answer."*
The scope note: W21b/W21c/W23 record `PRJNA692081` / `SRP301712` as **ALREADY RECOVERED → DUPLICATE, never novelty**. Those are *accessions*, and the closure is about **case identities**. The two are not in conflict and the closure is correct as written — but the pair sits close enough that a reader could take accession recovery as identity resolution. Optional hardening, verdict unchanged: *"Brenca: **case identities** unresolved (accession-level material is separately recorded as already-recovered → DUPLICATE; that does not resolve identities)."*

---

**C08 · L23 — promoter transfer and inverse bounds.** *"- Promoter transfer: failed. Inverse bounds: 2/36 failed."*
**Kind:** two scientific gates are settled (failed).
**Grade: UNVERIFIABLE-FROM-THE-RECORD — and this is the entry most likely to mislead a reader who checks the premise.**
Map L10 says the same words, so **the transcription is faithful**; the defect, if it is one, is inherited.
- *"Promoter transfer: failed"* — `grep -rIn -i 'promoter transfer|promoter-transfer'` returns **zero** hits in the live tree outside the campaign directory **and zero** at the corrected corpus root. No retained record carries that label.
- *"Inverse bounds: 2/36 failed"* — I found the retained inverse-bounds record. It is `research/autonomy/clinical-methods-checkpoints-2026-09-07/inverse-bounds-assessment.txt`, **corpus-only** (absent from the live checkout), i.e. it sits inside the very directory `CLOSED-WORK.md:28` calls *"(pending input)"*. **Its arithmetic is not 2/36.** L12: *"Its 18 synthetic development releases completed (17 certificates); all four larger stress cases exceeded limits."* L14: *"17/18 development certificates but 0/4 stress certificates."* L22 separately records a **different** closed pilot with **120** dependent reporting variants from 30 pseudoarm assignments across ten TCGA groups, which *"failed its frozen continuation gate"* and *"neither supplies evidence for inverse bounds nor licenses"* reuse. **No `36` appears anywhere in that record.**
  **The concrete propagation risk:** the only committed *"2 of 36"* in this repository is an unrelated NR4A3 fusion-target occupancy statistic (`research/autonomy/review-seats/PUB-FUSION-OUTPUT-…-seat-arithmetic.json:63`; ENO3, 2 of 36 gene-by-experiment tests at p<0.05 against 1.8 expected, binomial p 0.54). A worker who checks *"2/36"* lands on that artifact and will conclude the inverse-bounds gate is a null occupancy result. **`W20:127` already cites the figure** — *"**Inverse bounds (2/36 failed)** — I compute no bound"* — correctly declining to use it, but repeating it.
  I do **not** assert the map is wrong: `2/36` may come from a private record I cannot see, and absence from the corpus is UNKNOWN. What I assert is that **no committed or corpus record supports it, and one committed record collides with it.**
**Smallest correct restatement (both verdicts preserved):** *"Promoter transfer: failed (no canonical retained path recorded; basis UNKNOWN to workers). Inverse bounds: **failed** — the retained assessment is `research/autonomy/clinical-methods-checkpoints-2026-09-07/inverse-bounds-assessment.txt` (corpus-only), which records **17/18 development certificates and 0/4 stress certificates**, plus a separately closed 120-variant empirical pilot that failed its frozen continuation gate. **The figure `2/36` is not reproducible from any committed or corpus record and should not be quoted; the only committed `2 of 36` is an unrelated NR4A3 occupancy statistic.** Do not replay either gate unchanged."*

---

**C09 · L24 — independent cohorts.** *"- **Do not invent independent cohorts.** Arrays or specimens do not imply new patients."*
**Kind:** a standing prohibition (not a factual claim).
**Grade: CONFIRMED.** Map L16: *"Different arrays/specimen labels are not proof of different patients."* Faithful and load-bearing; multiple reports cite it correctly (`W23b`, `W23:233`).

---

**C10 · L25 — registry paper.** *"- User **rejected** the registry ICD-O classification paper."*
**Kind:** a paper was rejected.
**Grade: CONFIRMED.** Map L11: *"Registry ICD-O classification paper: explicitly rejected by user. Not reopened."* Faithful. Reports refer to it as PUB-EMC-CLASSIFICATION and confirm non-touch (`W21:102`, `W23:95`).

---

**C11 · L26-27 — clinical checkpoints.** *"- Clinical conditional-recurrence, RT/IPD synthesis, and trial-discoverability/response / checkpoints did not admit their proposed papers. Methylation is deprioritized."*
**Kind:** proposals were not admitted.
**Grade: CONFIRMED.** Map L11 matches, including *"methylation deprioritized"*. The transcription's *"their proposed papers"* (plural) vs the map's *"the proposed paper"* (singular) is a harmless generalisation over three checkpoints.

---

**C12 · L28-30 — where to start.** *"- Read `research/autonomy/clinical-methods-checkpoints-2026-09-07` (pending input) and the / care-delivery records before proposing a new clinical question. These scoped failures do / **not** mean all research is exhausted."*
**Kind:** a pointer to required reading, annotated as unavailable.
**Grade: SUPERSEDED — a false-unavailability claim, this campaign's named failure mode.**
`git ls-files | grep -c` → **0**; the directory is **not in the live checkout**. But `find` at the corrected corpus root returns **10+ files**, including `conditional-recurrence-gate.json`, `masunaga-primary-record.json`, `rt-2026-primary-record.json`, `radiotherapy-primary-verification-addendum.json`, `protocol-freeze.json`, `source-extension-and-allocation.md`, and `inverse-bounds-assessment.txt`. **The input is not pending. It has been readable by every worker since the corpus went live at ~02:30Z**, and `(pending input)` is not in the source map — it is an annotation added in transcription, correct when written and false since.
The cost is concrete: C11's three non-admitted checkpoints and C08's inverse-bounds gate all have their primary records in this directory, and `CLOSED-WORK.md` tells workers they cannot be read.
**Smallest correct restatement:** *"Read `research/autonomy/clinical-methods-checkpoints-2026-09-07/` — **absent from the live checkout, present and readable at the frozen-corpus root `/tmp/claude-0/frozen-corpus/extracted/corpus/`** — and the care-delivery records before proposing a new clinical question. These scoped failures do **not** mean all research is exhausted."*

---

**C13 · L33-35 — Pazopanib.** *"- **Pazopanib**: primary full paper and observed exposure window unrecovered; abstract only. / EudraCT `2013-005456-15` exists. Planned 48 weeks is **not** observed exposure. Mortality / erratum unread. No rate claim, no full-method-omission claim."*
**Kind:** a source is unrecovered; a scope prohibition.
**Grade: SUPERSEDED (pointer only — the closure and every prohibition stand untouched).** Map L12 is faithfully transcribed but ends *"Canonical: pazopanib-exposure-gate-2026-09-07 under research/autonomy"* — **dropped in transcription.** That directory is **absent from the live tree, present in the corpus** (3 tracked-map rows). No route was tested by me or by any report; `W07d:96`, `W07g:93`, `W10b:53`, `W13b:85` all confirm non-touch.
Usability note: this is the only unrecovered source without a PMID in either document; workers supply `31331701` from elsewhere, consistently.
**Smallest correct restatement:** append *"Canonical retained gate: `research/autonomy/pazopanib-exposure-gate-2026-09-07/` (absent from the live checkout; present at the frozen-corpus root). Primary is `PMID 31331701`."*

---

**C14 · L36-38 — Anthracycline.** *"- **Anthracycline** (`PMC3879193` / `PMID 24345066`): retained only median 4 cycles / (range 1-8; a separate non-missing denominator is unknown) and one patient who stopped after / the first cycle for toxicity. No rate, no patient linkage, no time/dose or net-benefit inference."*
**Kind:** partial retention with prohibitions — **but filed under a heading that makes it a denial.**
**Grade: OVER-SCOPED, and it has already propagated. This is the W23b shape, caught in the act.**
The retained facts and all four prohibitions are transcribed **exactly** from map L13 and are **CONFIRMED**. The defect is placement plus one dropped word. Map L13 opens *"Anthracycline: **verified primary** PMC3879193/PMID 24345066."* `CLOSED-WORK.md` places it under the heading **"Unrecovered / partially retained sources"** (L32) and drops *"verified primary"*. Nothing in either document records a denial, a 403, or an `EGRESS_BLOCKED` for this paper — it is a **verified, read primary** whose *extraction* was deliberately limited.
**The propagation is already on the record.** `W07g:93` writes: *"**The denied list is** pazopanib `31331701` full text, sunitinib 2014 `24703573`, CTARC 2022 `35144048`, Wagner 2020 `32856598`, trabectedin/RT 2018 `10.4172/…`, **anthracycline `PMC3879193`/`24345066`**"*, and at `:143-144` renders such rows `**DENIED**` / `UNVERIFIABLE`. `W07d:96`, `W10b:53`, `W10d:87` and `W21:102` likewise list the anthracycline paper among unrecovered sources. **W07g's substantive verdict is unaffected** — it asserts nothing new about the paper and computes no rate, exactly as required — but its *stated reason* ("denied") is wrong, and a worker who inherits "denied" will treat a verified primary's limited retention as an access failure, which is the opposite conclusion about what more is knowable.
Also dropped: *"Canonical: anthracycline-exposure-gate-2026-09-07"* (corpus-only, 4 tracked-map rows).
**Smallest correct restatement (all prohibitions preserved):** move the entry out from under "Unrecovered" and state: *"**Anthracycline** (`PMC3879193` / `PMID 24345066`) — **verified primary; read, not denied.** Retention was deliberately limited to: median 4 cycles (range 1-8; a separate non-missing denominator is unknown) and one patient who stopped after the first cycle for toxicity. No rate, no patient linkage, no time/dose or net-benefit inference. Canonical gate: `research/autonomy/anthracycline-exposure-gate-2026-09-07/` (corpus-only). **This paper is not on the denied-route list.**"*

---

**C15 · L39-40 — Sunitinib 2014.** *"- **Sunitinib** original 2014 (`PMID 24703573`, `DOI 10.1016/j.ejca.2014.03.013`): unrecovered; / three ordinary institutional 403 routes exhausted. Metadata only. **No 2012 source substitution.**"*
**Kind:** a route was denied and remains denied.
**Grade: SUPERSEDED (pointer only).** Content faithful to map L14, including the substitution ban. **No route was tested by me.** Every report that names it confirms non-replay and no substitution (`W10:43`, `W10b:53`, `W10d:87`, `W07d:96`, `W10f:211`, `W24:201`). One transcription nuance: the map says *"full text unrecovered"*; `CLOSED-WORK.md` says *"unrecovered"* then *"Metadata only"*, which recovers the sense.
Dropped: *"Canonical: sunitinib-primary-recovery-2026-09-07"* (corpus-only, 3 rows).
**Smallest correct restatement:** *"…**full text** unrecovered; three ordinary institutional 403 routes exhausted unchanged. Metadata only. No 2012 source substitution. Canonical: `research/autonomy/sunitinib-primary-recovery-2026-09-07/` (corpus-only)."*

---

**C16 · L41-43 — Trabectedin/RT 2018.** *"- **Trabectedin/RT 2018** (`DOI 10.4172/clinical-practice.1000433`): a rediscovered / known-unverified PDF. The historical `EGRESS_BLOCKED` was an old proxy outcome — not a / biological refusal, not publisher authentication, not global absence. No unchanged route replay."*
**Kind:** a source is unverified; a **correction to a prior mis-attributed reason**.
**Grade: CONFIRMED, and this entry is the document's best-written one.** Map L15 matches. It is precisely the pattern the audit was told to look for — a verdict retained while a false reason is corrected — and here `CLOSED-WORK.md` **already does it right**, distinguishing an old proxy outcome from a biology refusal and from global absence. It should be the template for C14 and C12. Only the canonical pointer (`trabectedin-case-deduplication-2026-09-08`, corpus-only, 3 rows) is dropped.

---

**C17 · L44-45 — Wagner 2020.** *"- **Wagner 2020** (`PMID 32856598`, `DOI 10.1158/1055-9965.EPI-20-0447`): methods unresolved, / ordinary route historically `EGRESS_BLOCKED`."*
**Kind:** a route was denied; methods unresolved.
**Grade: CONFIRMED.** Map L17 matches, and the word *"historically"* correctly carries the C16 distinction. Not tested by me; non-replay confirmed at `W04b:95`, `W06:96`, `W10b:53`, `W10d:87`, `W10f:213`.
Note without action: `W15d:161` uses PMID 32856598 for a retained SEER n=439 design fact — an *abstract-level* use, consistent with "methods unresolved". No conflict.

---

**C18 · L46-47 — CTARC 2022.** *"- **CTARC 2022** (`PMID 35144048`, `DOI 10.1016/j.ctarc.2022.100530`): abstract retained; latest / publisher 403, methods unrecovered. No unchanged denied-route retries."*
**Kind:** a route was denied; abstract retained.
**Grade: CONFIRMED, and independently corroborated.** Map L17 matches. `W10f:214` records it as *"the only source of the 16 whose denial is correctly recorded in both places"* (`CLOSED-WORK.md` **and** `emc-km-admissibility-2026-08-27.json` `seer270_2022.retrieval.routes[0]`). `W13c:94-95,120` confirms `cohorts[9]` **is** this blocked paper, used at abstract level only, and — checking rather than assuming — that `W13b`'s `ussc2022` (`PMID 35962783`) is a **different** paper. The closure held under direct pressure.

---

**C19 · L48-51 — SEER / Noone.** *"- Official SEER treatment limitations and Noone `PMC4981219` concern specified **non-sarcoma** / cancers/modalities — **not** EMC calibration or surgery-capture validation. Exclude unsupported / plausible-EMC-value and age-gradient assertions. **No EMC-specific calibration from generic / SEER parameters. Source availability is not scientific admission.**"*
**Kind:** a scientific conclusion is settled (these sources do not transfer to EMC).
**Grade: OVER-SCOPED by omission — one clause was dropped, and it is the clause this campaign most needed.**
The scientific content is faithful to map L18 and **CONFIRMED**; the non-transfer verdict stands entirely. But map L18 reads *"Unsupported plausible-EMC-value/age-gradient assertions **and sparse-input repository-wide absence claims** are excluded."* **`CLOSED-WORK.md` dropped "and sparse-input repository-wide absence claims are excluded."**
That is a standing prohibition on exactly the error W21b, W21c and W23b each found propagating. Had it survived transcription, `CLOSED-WORK.md` would have carried an explicit ban on repository-wide absence claims in its own body rather than only the weaker generic note at L4 (*"A missing file or abstract is UNKNOWN, not proof of absence"*). It also explains why the ban reads as scoped to SEER when it was written as general.
Also dropped: the SEER/Noone material's location (*"preserved privately in parallel-followups-20260908/seer-source-followup/primary-evidence"*). I verified this path is absent from the live tree, the corpus **and** the tracked-file map — consistent with "private", and its absence therefore remains **UNKNOWN**, not evidence of anything.
**Smallest correct restatement:** restore the dropped clause and promote it out of the SEER bullet: *"…Exclude unsupported plausible-EMC-value and age-gradient assertions. No EMC-specific calibration from generic SEER parameters. Source availability is not scientific admission. The SEER HTML and Noone XML are preserved **privately** (`parallel-followups-20260908/seer-source-followup/primary-evidence`), outside this checkout, the frozen corpus and the tracked-file map; their absence here is UNKNOWN. **Standing and general, not specific to SEER: sparse-input repository-wide absence claims are excluded.**"*

---

**C20 · L54-59 — GSE4303 / GSE28866.** *"- `GSE4303` and `GSE28866` are heavily retained and analysed. Re-finding them or re-reading a / header is **not** new data."* with three paths, the third annotated *"(pending input)"*.
**Kind:** rediscovery is not novelty; plus three pointers.
**Grade: SUPERSEDED (the third pointer only; the closure is CONFIRMED).**
The closure is faithful to map L16 and correct. Paths 1 and 2 (`emc-fourth-cohort-sra-2026-08-08.md`, `gse28866-tumour-vs-normal-reading.md`) are **present in the live tree and in the corpus** — verified. Path 3, `research/autonomy/cycle-outcomes/20260905T133448Z-6bd43b913c/atlas-primary-matrix-availability.json`, is marked *"(pending input)"* — an annotation **not in the map** — and is **absent from the live checkout but present at the corrected corpus root**, alongside `outcome-1.json`, `plan.json`, `verification.json`, `runner-receipt.json` and more. Same defect as C12.
**Smallest correct restatement:** replace *"(pending input)"* with *"(absent from the live checkout; present and readable at the frozen-corpus root)"*.

---

**C21 · L61-69 — source-index state (lane 11).** *"Original helper/tests were actually executed: **discovery failed — the directory was not / importable**; running the 10 tests directly gave **9 pass / 1 fail**, the failure being a / case-sensitive disclaimer assertion; **4 CLI examples exited 0**. An independent read-only review / found **9 potential defects** and proposed diffs, but **both literal diffs failed / `git apply --check` (malformed hunks)**. **None of those 9 static findings is an empirically / passed review.** The exact bundle arrives with the supporting-input branch. …"*
**Kind:** a mixture — measured execution state, a review's status, and a forward-looking expectation.
**Grade: SUPERSEDED in two specific clauses; the rest CONFIRMED; the lane's ownership and its prohibitions stand entirely.**
Confirmed against map L25: *"Discovery failed, direct 10 tests 9 pass 1 fail on disclaimer capitalization, 4 bounded CLI examples exit 0"* — **faithful**, including the `git apply --check` failures and *"do not evade coverage or increase ceilings simply to land code"* (rendered as *"No arbitrary test-ceiling increase"*).
Two clauses are now stale, both overtaken by executed work:
1. *"The exact bundle arrives with the supporting-input branch"* — **it arrived.** `W11b:106` records reading the helper (779 lines), the 10-test file, `execution-result.json`, both stderr logs, the independent comparison §0-§2 and `input-manifest.json`, with manifest digests matching.
2. *"**None of those 9 static findings is an empirically passed review.**"* — **superseded, and by the very act it was written to require.** `W11b:145,161,1840`: *"Nine of nine reproduce as mechanisms"*, *"nine adjudicated by a probe I ran — eight reproduced-and-fixed, one (F4) reproduced as a mechanism with **the review's own cited example refuted** and recorded as such. **Zero accepted on reading.**"* `W11c` then executed the eight §2 divergence items and found **8/8 real**, overturning one of its own false verdicts by execution (`W11c` §2).
The clause's *intent* — never accept a static finding on its prose — was honoured exactly and should be preserved as a rule; only its factual half ("none has been") is out of date.
Two live constraints worth carrying forward, both measured: `W11c` §4 ran `python3 scripts/tier_budget.py` → `commit-loop 1466/1500`, **EXIT=0**, and confirmed `scripts/source_reuse_index.py` and its test file are **not in the tree** — so `W11b`'s `1484/1500` remains a **projection of a placement that has not occurred**. Note also that the map names the files at `research/tools/…` while W11b/W11c work at `scripts/…`; **that is lane 11's to adjudicate, not mine, and I propose nothing.**
**Smallest correct restatement (ownership and every prohibition preserved):** *"…An independent read-only review found **9 potential defects** and proposed diffs, but **both literal diffs failed `git apply --check` (malformed hunks)**. **No static finding is ever an empirically passed review — never accept one on its prose.** **Update: the bundle has arrived and all nine were adjudicated by execution (W11b: 8 reproduced-and-fixed, 1 reproduced with the review's own cited example refuted), and the review's eight §2 divergence items were separately executed and found 8/8 real (W11c).** Placement has **not** occurred: `scripts/source_reuse_index.py` is not in the tree and the measured commit-loop budget is **1466/1500** (`scripts/tier_budget.py`, EXIT=0), not the projected 1484. Prefer complete named final files and legitimate integration with existing test tiers. No arbitrary test-ceiling increase and no 30-test gate. Lane 11 is the only owner of source-index changes."*

---

### Two items present in the source map and **missing entirely** from `CLOSED-WORK.md`

Not defects in an existing entry, but omissions that remove a guard:

- **Map L23:** *"Independent source-index comparison 20260908T011747Z-371bbc743c is already running against recovered report/spec on base 2f6. **Keep blind to execution outputs until completed; do not duplicate it.**"* — a live blind-and-no-duplication instruction, absent from `CLOSED-WORK.md`. Whether it is still live is **UNKNOWN** to me (`CORPUS-CONTEXT.md:50` warns that historical worker-status wording in the map is not current live ownership), so this is **for the coordinator to resolve, not to paste forward.**
- **Map L26:** *"Six original scout/spec/recovery workers are terminal and preserved in terminal-integrity; **no actual worker should be counted from a stale receipt.**" ` — a counting rule with obvious campaign relevance, absent from `CLOSED-WORK.md`.

---

## Validation evidence

All **RUN**, all read-only, in the container, no network. Environment: Linux 6.18.44-fc-v24, `/home/user/Rare-cancers`, HEADs as pinned; corpus at `/tmp/claude-0/frozen-corpus/extracted/corpus/` (read-only, read in place, not copied).

**RUN 1 — start/end evidence.** `date -u`, `git rev-parse HEAD`, `git status --porcelain`, `env | grep …` at start and end. Exit 0. Output in **Worker** above. `git status --porcelain` **empty both times**; `/tmp/claude-0/w33/` empty at end (`ls -la` → `total 8`, `.` and `..` only).

**RUN 2 — the transcription's own source.** `cat -n /tmp/claude-0/frozen-corpus/extracted/metadata/closed-source-and-ownership-map.md` → 26 lines, exit 0. Quoted verbatim per entry above. This is the file `CORPUS-CONTEXT.md:47` designates as retaining the original compact map verbatim.

**RUN 3 — live-tree path existence.** Exit 0:
```
$ git ls-files | grep -c 'clinical-methods-checkpoints-2026-09-07'      → 0
$ git ls-files | grep -c 'cycle-outcomes/20260905T133448Z-6bd43b913c'   → 0
$ git ls-files | grep -c 'peerj-validation-audit-2026-09-07'            → 0
$ ls -d research/autonomy/clinical-methods-checkpoints-2026-09-07 \
        research/autonomy/cycle-outcomes/20260905T133448Z-6bd43b913c
ls: cannot access '…clinical-methods-checkpoints-2026-09-07': No such file or directory
ls: cannot access '…20260905T133448Z-6bd43b913c': No such file or directory
$ git ls-files | grep 'emc-fourth-cohort-sra-2026-08-08'
research/manuscripts/fusion-output/emc-fourth-cohort-sra-2026-08-08.md
$ git ls-files | grep 'gse28866-tumour-vs-normal-reading'
research/manuscripts/fusion-output/gse28866-tumour-vs-normal-reading.md
```
Per-gate counts in the live tree, all `0`: `pazopanib-exposure-gate-2026-09-07`, `anthracycline-exposure-gate-2026-09-07`, `sunitinib-primary-recovery-2026-09-07`, `trabectedin-case-deduplication-2026-09-08`, `source-reuse-program-2026-09-08`, `parallel-followups-20260908`.

**RUN 4 — corrected-corpus-root existence.** `find . -path "*<name>*"` at `/tmp/claude-0/frozen-corpus/extracted/corpus`, exit 0. `clinical-methods-checkpoints-2026-09-07` → directory + `conditional-recurrence-gate.json`, `masunaga-primary-record.json`, `radiotherapy-primary-verification-addendum.json`, `rt-2026-source-result.txt`, `rt-2026-primary-record.json`, `source-extension-and-allocation.md`, `protocol-freeze.json`, `conditional-distinct-source-assessment.txt`, `prefix-propagation-checkpoint.md` (+ more). `20260905T133448Z-6bd43b913c` → directory + `outcome-1.json`, `plan.json`, **`atlas-primary-matrix-availability.json`**, `verification.json`, `runner-receipt.json`, `normal-integration-verification.json` (+ more). The four exposure gates → all **PRESENT**, with `grep -c` on `metadata/tracked-file-map.txt` = 3/4/3/3 respectively. `source-reuse-program-2026-09-08`, `parallel-followups-20260908`, `seer-source-followup` → **empty in corpus and 0 rows in the tracked map**.

**RUN 5 — the frozen deliverable.** `ls …/peerj-validation-audit-2026-09-07/final-handoff/` → `archive-members.json`, `integration.json`, `package-ready.json`, `publication-bar.json`. `python3 -c "import json; …"` on `integration.json`, exit 0, verbatim:
```
status = "preprint_submission_ready_handed_to_submission_owner"
full_exit = 0
publication_bar_passed = 8
scope = "Writing and submission preparation completed. The separate submission thread handles venue authority, source clarification and posting; no posting is claimed here."
remaining_source_limit = "Actual analyzed S6B cohort and original external normalization inputs remain unidentified. Reconcile substantive source clarification or venue feedback before changing the frozen paper."
```
`grep -rIl '7baf272705d7a629f6d21d4fc169a7188775a60b'` at the corpus root → 10 files incl. `validation/linux-full-7baf2727/verification.json` and `preflight-receipts/7baf272705d7a629f6d21d4fc169a7188775a60b.json`. In the live tree the same string appears in only 2 files, both campaign documents (`CLOSED-WORK.md`, `reports/W17-heldout-validation.md`). `grep -rIn '5848'` filtered to qeios/receipt at the corpus root → **0**; in the live tree → only `CLOSED-WORK.md:10`.

**RUN 6 — inverse bounds and promoter transfer.** `grep -rIn -i 'inverse bound'`: live tree (excluding the campaign dir) → **0**; corpus → **1 file**, `research/autonomy/clinical-methods-checkpoints-2026-09-07/inverse-bounds-assessment.txt`, read in full (41 lines, `cat -n`, exit 0). Key lines quoted verbatim in C08. `grep -rIn -i 'promoter transfer|promoter-transfer'`: live tree (ex-campaign) → **0**; corpus → **0**. `grep -rIn '2/36|2 of 36'` in the live tree → `CLOSED-WORK.md:23`, `reports/W20:127`, and two `review-seats/PUB-FUSION-OUTPUT-…` JSONs describing the unrelated NR4A3 occupancy statistic (quoted in C08).

**RUN 7 — propagation check on denied-route lists.** `grep -rn -i 'pazopanib|24703573|32856598|35144048'` over `reports/` → 40 hits. Every hit is a non-replay compliance statement; **no report reports a retrieval of any closed source.** The over-scope evidence for C14 is `W07g:93` and `W07g:143-144`, quoted verbatim in C14.

**RUN 8 — lane-11 state.** `grep -n` over `W11b` → lines 106, 145, 151, 154, 155, 161, 1836, 1840, 1852, 1854 quoted in C21. `awk '/^## Result/,/^## Validation/'` over `W11c` → the 8-row §2 table, the §4 `tier_budget.py` block (`commit-loop 1466/1500`, `EXIT=0`) and the `ls: cannot access 'scripts/source_reuse_index.py'` block, quoted in C21.

**PROPOSED (NOT RUN).** Every restatement in **Result** is drafted text for the coordinator; I wrote none of it to disk, and `git status --porcelain` is empty. **No route, closure or refusal was tested, probed, retried, rephrased or rerouted at any point in this run** — the audit is entirely documentary, by design and by instruction.

---

## Limitations

- **The map may not be the whole source.** `CLOSED-WORK.md:3` says "the campaign admission"; `CORPUS-CONTEXT.md:47` designates the compact map as retaining it verbatim, and I treated the two as the same object. If the coordinator holds additional admission text I cannot see, some "dropped in transcription" findings would instead be "carried from elsewhere". The **path** and **arithmetic** findings do not depend on this: they are checks against the tree and the corpus directly.
- **Corpus absence is UNKNOWN.** 10,566 tracked-map rows vs 5,996 present files (`CORPUS-CONTEXT.md`, `W23b`). Where I report a path absent from **both** the live tree and the corrected root (SEER/Noone private evidence, `source-reuse-program-2026-09-08`, promoter-transfer and Davis records), that is **not** proof of repository-wide absence — and for the SEER material the map affirmatively says it is private.
- **Live-tree absence is a statement about a moving HEAD.** HEAD moved three times during my run (`e2214d4f` → `302c2b63` → `ff6bb018`). My `git ls-files` results are pinned to `302c2b63`; a later commit could add any of these paths. `CLOSED-WORK.md`'s own bytes were stable throughout.
- **I could not verify C08's `2/36` as false**, only as unsupported by any record I can read and colliding with one committed artifact. It may derive from a private record. I make no claim that the inverse-bounds gate did anything other than fail.
- **Three grades are UNVERIFIABLE-FROM-THE-RECORD** (C05 Davis, C08 promoter transfer, C08 inverse-bounds figure). That grade means *a worker cannot check the stated reason*, **never** that the closure is doubtful and **never** that it should be reopened. All three verdicts stand.
- **This audit establishes nothing scientific.** It contains no measurement, no cohort, no denominator, no patient data and no clinical claim. There is no wet lab. It does not admit, re-admit or advance any paper, and it does not change the status of any source.
- **I am read-only and proposed no repair to anything but text.** The lane-11 file-location divergence (`research/tools/` vs `scripts/`) is flagged for lane 11 and left alone.

---

## Stop condition

**Set at start:** return the moment every closure record in `CLOSED-WORK.md` has been (a) quoted verbatim with its line number, (b) typed by claim kind, (c) graded CONFIRMED / SUPERSEDED / OVER-SCOPED / UNVERIFIABLE-FROM-THE-RECORD against the committed record, with the two named failure modes — repository/corpus absence claims tested at the corrected root, and verdicts resting on contradicted reasons — checked explicitly, and (d) given a smallest correct restatement where non-CONFIRMED.

**MET.** 20 records graded: 11 CONFIRMED, 4 SUPERSEDED, 2 OVER-SCOPED, 3 UNVERIFIABLE-FROM-THE-RECORD, plus 2 map items missing from the document entirely. Every absence-shaped closure was tested at `/tmp/claude-0/frozen-corpus/extracted/corpus/`; two false-unavailability annotations (C12, C20) and one already-propagated wrong-reason closure (C14) were found. **No closure was reopened, re-graded or unblocked; no denied route was tested; the blocked NR4A Perspective was not approached.** Returning now without extending into adjacent lanes.

---

## Tool-call and wall-clock count actually used

**26 tool calls** (all Bash; zero network, zero MCP, zero WebFetch/WebSearch, zero writes). **Wall clock 03:21:42Z → 03:25:36Z ≈ 4 minutes** — well inside the ~40-call / ~40-minute target; the stop condition was met early because the corpus contained the transcription's own source document, which collapsed most of the audit into one comparison.

---

## Next concrete action

**One coordinator write to `research/autonomy/opus-capacity-campaign-20260908/CLOSED-WORK.md`, applying the nine restatements above verbatim, with C12, C14 and C19 first.** They are the three that are actively costing the campaign: C12 and C20 tell every worker that two input directories are "pending" when they have been readable at the corrected corpus root since ~02:30Z (C12's directory holds the primary records for C08's and C11's own closures); C14 has already propagated "denied" onto a verified primary in at least five reports; and C19 restores a dropped standing ban on *"sparse-input repository-wide absence claims"* — the exact error W21b, W21c and W23b each found spreading. The write needs **no retrieval, no network, no new analysis and no reopening** — every restatement preserves its closure and is sourced from files already in hand. It should ship in the same coordinator pass as W21b's and W21c's still-unapplied corrections, since this document is upstream of all of them.
